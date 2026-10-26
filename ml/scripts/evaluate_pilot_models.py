import csv
import json
from pathlib import Path
from datetime import datetime, timezone

import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "datasets" / "independent_validation_pilot.csv"
CLASSIFIER_PATH = ROOT / "ml/models/scam_classifier_v2.joblib"
VECTORIZER_PATH = ROOT / "ml/models/tfidf_vectorizer_v2.joblib"
CANDIDATE_PATH = ROOT / "ml/models/scam_multilingual_candidate.joblib"
OUTPUT_DIR = ROOT / "experiments"

PREDICTIONS_PATH = OUTPUT_DIR / "pilot_model_comparison_predictions.csv"
SUMMARY_PATH = OUTPUT_DIR / "pilot_model_comparison_summary.json"

required = [
    DATASET, CLASSIFIER_PATH, VECTORIZER_PATH, CANDIDATE_PATH
]
for path in required:
    if not path.is_file():
        raise FileNotFoundError(f"Required file missing: {path}")

if PREDICTIONS_PATH.exists() or SUMMARY_PATH.exists():
    raise FileExistsError(
        "Evaluation output already exists. Move or rename the existing "
        "output files before running again; nothing was overwritten."
    )

with DATASET.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames or not {
        "sample_id", "message", "label", "language", "independent_review"
    }.issubset(reader.fieldnames):
        raise ValueError("Pilot CSV is missing required columns.")
    rows = list(reader)

if not rows:
    raise ValueError("Pilot dataset is empty.")

for row in rows:
    if not row["sample_id"].strip() or not row["message"].strip():
        raise ValueError("A row has a missing sample ID or message.")
    row["label"] = row["label"].strip().upper()
    if row["label"] not in {"SCAM", "BENIGN"}:
        raise ValueError(
            f"Invalid label for {row['sample_id']}: {row['label']}"
        )

ids = [row["sample_id"] for row in rows]
if len(ids) != len(set(ids)):
    raise ValueError("Duplicate sample IDs detected.")

classifier = joblib.load(CLASSIFIER_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
candidate = joblib.load(CANDIDATE_PATH)

messages = [row["message"].strip() for row in rows]
actual = [row["label"] for row in rows]

# Production model uses its original saved vectorizer.
production_predictions = [
    str(value).strip().upper()
    for value in classifier.predict(vectorizer.transform(messages))
]

# Candidate is a complete pipeline and accepts raw text.
candidate_predictions = [
    str(value).strip().upper()
    for value in candidate.predict(messages)
]

valid_labels = {"SCAM", "BENIGN"}
for name, predictions in (
    ("Production V2", production_predictions),
    ("Candidate", candidate_predictions),
):
    if any(value not in valid_labels for value in predictions):
        raise ValueError(f"{name} produced an unexpected label.")

def calculate_metrics(predictions):
    return {
        "accuracy": accuracy_score(actual, predictions),
        "scam_precision": precision_score(
            actual, predictions, pos_label="SCAM", zero_division=0
        ),
        "scam_recall": recall_score(
            actual, predictions, pos_label="SCAM", zero_division=0
        ),
        "scam_f1": f1_score(
            actual, predictions, pos_label="SCAM", zero_division=0
        ),
        "macro_f1": f1_score(
            actual, predictions, average="macro", zero_division=0
        ),
        "confusion_matrix_labels": ["BENIGN", "SCAM"],
        "confusion_matrix": confusion_matrix(
            actual, predictions, labels=["BENIGN", "SCAM"]
        ).tolist(),
    }

prediction_rows = []
for row, truth, prod, cand in zip(
    rows, actual, production_predictions, candidate_predictions
):
    prediction_rows.append({
        "sample_id": row["sample_id"],
        "language": row["language"],
        "actual_label": truth,
        "production_v2_prediction": prod,
        "production_v2_correct": prod == truth,
        "candidate_prediction": cand,
        "candidate_correct": cand == truth,
        "models_disagree": prod != cand,
        "independent_review": row["independent_review"],
    })

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with PREDICTIONS_PATH.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=prediction_rows[0].keys())
    writer.writeheader()
    writer.writerows(prediction_rows)

review_statuses = {}
for row in rows:
    status = (row.get("independent_review") or "").strip() or "(blank)"
    review_statuses[status] = review_statuses.get(status, 0) + 1

summary = {
    "evaluation_type": "Preliminary pilot comparison",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "dataset": str(DATASET.relative_to(ROOT)),
    "sample_count": len(rows),
    "label_counts": {
        label: actual.count(label) for label in ("SCAM", "BENIGN")
    },
    "independent_review_status_counts": review_statuses,
    "models_retrained": False,
    "production_model_modified": False,
    "production_v2": calculate_metrics(production_predictions),
    "multilingual_candidate": calculate_metrics(candidate_predictions),
    "limitations": [
        "Small pilot dataset; results are not a real-world accuracy estimate.",
        "Labels have not necessarily been independently verified.",
        "Scam scenarios and synthetic benign controls have different provenance.",
        "Do not use this report alone to promote the candidate to production."
    ],
}

with SUMMARY_PATH.open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("Pilot comparison completed.")
print(f"Samples evaluated: {len(rows)}")
print(f"Review statuses: {review_statuses}")

for name in ("production_v2", "multilingual_candidate"):
    result = summary[name]
    print(f"\n{name}:")
    print(f"  Accuracy:       {result['accuracy']:.3f}")
    print(f"  Scam precision: {result['scam_precision']:.3f}")
    print(f"  Scam recall:    {result['scam_recall']:.3f}")
    print(f"  Scam F1:        {result['scam_f1']:.3f}")
    print(f"  Macro F1:       {result['macro_f1']:.3f}")
    print(f"  Confusion matrix: {result['confusion_matrix']}")

print("\nPredictions:", PREDICTIONS_PATH.relative_to(ROOT))
print("Summary:", SUMMARY_PATH.relative_to(ROOT))
print("\nPreliminary results only. Do not treat them as real-world performance.")
