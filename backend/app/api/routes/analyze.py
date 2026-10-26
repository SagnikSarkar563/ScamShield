
import sys
from pathlib import Path
from typing import Optional

import joblib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Locate the ScamShield project root.
PROJECT_ROOT = Path(__file__).resolve().parents[4]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODEL_DIR = PROJECT_ROOT / "ml" / "models"

CLASSIFIER_PATH = MODEL_DIR / "scam_classifier_v2.joblib"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer_v2.joblib"

# Load only the compatible V2 model and vectorizer.
classifier = joblib.load(CLASSIFIER_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

from ml.scripts.url_analyzer import analyze_text_urls

router = APIRouter(prefix="/api/v1", tags=["Scam Analysis"])


class AnalyzeRequest(BaseModel):
    message: Optional[str] = Field(default=None, max_length=20000)
    url: Optional[str] = Field(default=None, max_length=4096)


def get_risk_level(score: float) -> str:
    if score < 25:
        return "LOW"
    if score < 50:
        return "MEDIUM"
    if score < 75:
        return "HIGH"
    return "CRITICAL"


@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    message = (request.message or "").strip()
    supplied_url = (request.url or "").strip()

    if not message and not supplied_url:
        raise HTTPException(
            status_code=400,
            detail="Provide a message or URL to analyze.",
        )

    # Include a separately supplied URL in URL analysis.
    text_for_url_analysis = " ".join(
        part for part in (message, supplied_url) if part
    )

    # The text classifier is used only for message text when available.
    classifier_input = message if message else supplied_url

    try:
        features = vectorizer.transform([classifier_input])
        prediction = str(classifier.predict(features)[0])

        probabilities = classifier.predict_proba(features)[0]
        classes = list(classifier.classes_)
        scam_probability = float(probabilities[classes.index("SCAM")])

        url_results = analyze_text_urls(text_for_url_analysis)
        if not isinstance(url_results, list):
            url_results = []

    except Exception as exc:
        # Do not expose internal paths or exception details to API clients.
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Check the backend logs.",
        ) from exc

    highest_url_score = max(
        (float(item.get("risk_score", 0)) for item in url_results),
        default=0.0,
    )

    # Transparent recovery scoring: combine model probability and URL
    # heuristic score by taking the maximum. This is not calibrated.
    risk_score = round(max(scam_probability * 100, highest_url_score), 2)
    risk_level = get_risk_level(risk_score)

    findings = []
    for item in url_results:
        findings.extend(item.get("findings", []))

    findings = list(dict.fromkeys(findings))

    if prediction == "SCAM":
        explanation = (
            "The text classifier identified scam-like language. "
            "Review the message and supporting URL findings."
        )
        action = (
            "Do not share OTPs, passwords, UPI PINs, or banking details. "
            "Verify the request through the organisation's official channel."
        )
    elif highest_url_score >= 50:
        explanation = (
            "The text classifier predicted BENIGN, but the URL analyzer "
            "found suspicious characteristics. Treat this result cautiously."
        )
        action = (
            "Avoid opening the link or entering personal information until "
            "you verify the destination independently."
        )
    else:
        explanation = (
            "The text classifier predicted BENIGN. This does not guarantee "
            "that the message or any link is safe."
        )
        action = (
            "Verify unexpected requests independently and never share "
            "confidential authentication details."
        )

    return {
        "prediction": prediction,
        "label": prediction,
        "scam_score": round(scam_probability, 4),
        "scam_probability": round(scam_probability, 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "category": None,
        "tactics": [],
        "url_analysis": url_results,
        "url_risk_score": highest_url_score,
        "explanation": explanation,
        "findings": findings,
        "recommended_action": action,
        "limitations": [
            "Category prediction is unavailable in recovery mode.",
            "Tactic detection is unavailable in recovery mode.",
            "URL risk is heuristic and is not a reputation lookup.",
            "Risk scores are not calibrated probabilities of harm.",
            "A BENIGN prediction does not guarantee safety.",
        ],
    }
