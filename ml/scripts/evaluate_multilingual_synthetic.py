import csv
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datasets" / "multilingual_heldout_synthetic.csv"
CLASSIFIER = ROOT / "ml/models/scam_classifier_v2.joblib"
VECTORIZER = ROOT / "ml/models/tfidf_vectorizer_v2.joblib"
CANDIDATE = ROOT / "ml/models/scam_multilingual_candidate.joblib"
OUT = ROOT / "experiments"
PRED = OUT / "multilingual_heldout_synthetic_predictions.csv"
REPORT = OUT / "multilingual_heldout_synthetic_summary.json"

for path in (DATA, CLASSIFIER, VECTORIZER, CANDIDATE):
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {path}")

if PRED.exists() or REPORT.exists():
    raise FileExistsError("Output exists; rename it before rerunning. Nothing overwritten.")

with DATA.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

required = {"sample_id", "message", "label", "language", "source_type", "independent_review"}
if not rows or not required.issubset(rows[0]):
    raise ValueError("Dataset is empty or missing required columns.")

ids = [r["sample_id"].strip() for r in rows]
if len(ids) != len(set(ids)):
    raise ValueError("Duplicate sample IDs.")

for r in rows:
    r["label"] = r["label"].strip().upper()
    if r["label"] not in {"SCAM", "BENIGN"}:
        raise ValueError(f"Invalid label: {r['sample_id']}")
    if not r["message"].strip():
        raise ValueError(f"Empty message: {r['sample_id']}")
    if r["source_type"].strip().lower() != "synthetic":
        raise ValueError("This evaluator only accepts synthetic samples.")

messages = [r["message"].strip() for r in rows]
actual = [r["label"] for r in rows]

classifier = joblib.load(CLASSIFIER)
vectorizer = joblib.load(VECTORIZER)
candidate = joblib.load(CANDIDATE)

predictions = {
    "production_v2": [
        str(x).strip().upper()
        for x in classifier.predict(vectorizer.transform(messages))
    ],
    "multilingual_candidate": [
        str(x).strip().upper() for x in candidate.predict(messages)
    ],
}

def metrics(y, p):
    return {
        "sample_count": len(y),
        "accuracy": round(accuracy_score(y, p), 4),
        "scam_precision": round(precision_score(y, p, pos_label="SCAM", zero_division=0), 4),
        "scam_recall": round(recall_score(y, p, pos_label="SCAM", zero_division=0), 4),
        "scam_f1": round(f1_score(y, p, pos_label="SCAM", zero_division=0), 4),
        "macro_f1": round(f1_score(y, p, average="macro", zero_division=0), 4),
        "confusion_matrix_labels": ["BENIGN", "SCAM"],
        "confusion_matrix": confusion_matrix(y, p, labels=["BENIGN", "SCAM"]).tolist(),
    }

details = []
for i, r in enumerate(rows):
    item = {
        "sample_id": r["sample_id"],
        "language": r["language"],
        "actual_label": actual[i],
        "source_type": r["source_type"],
        "independent_review": r["independent_review"],
    }
    for name, preds in predictions.items():
        item[name + "_prediction"] = preds[i]
        item[name + "_correct"] = preds[i] == actual[i]
    item["message"] = r["message"]
    details.append(item)

by_language = {}
for language in sorted({r["language"] for r in rows}):
    idx = [i for i, r in enumerate(rows) if r["language"] == language]
    by_language[language] = {
        name: metrics([actual[i] for i in idx], [preds[i] for i in idx])
        for name, preds in predictions.items()
    }

OUT.mkdir(parents=True, exist_ok=True)
with PRED.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=details[0].keys())
    writer.writeheader()
    writer.writerows(details)

summary = {
    "evaluation_type": "Synthetic multilingual smoke evaluation",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "dataset": str(DATA.relative_to(ROOT)),
    "sample_count": len(rows),
    "language_counts": {
        lang: sum(r["language"] == lang for r in rows)
        for lang in sorted({r["language"] for r in rows})
    },
    "labels_are_independently_reviewed": False,
    "models_retrained": False,
    "production_model_modified": False,
    "overall": {
        name: metrics(actual, preds) for name, preds in predictions.items()
    },
    "by_language": by_language,
    "limitations": [
        "All messages are synthetic and labels are pending review.",
        "This is a constructed smoke test, not real-world validation.",
        "Small sample count; metrics are highly uncertain.",
        "Do not use these results alone to promote a model to production."
    ],
}

with REPORT.open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("Synthetic multilingual evaluation complete.")
print(f"Samples: {len(rows)}")
print("\nOVERALL")
for name, result in summary["overall"].items():
    print(f"\n{name}")
    for key in ("accuracy", "scam_precision", "scam_recall", "scam_f1", "macro_f1"):
        print(f"  {key}: {result[key]:.3f}")
    print(f"  confusion_matrix [BENIGN, SCAM]: {result['confusion_matrix']}")

print("\nBY LANGUAGE")
for lang, results in by_language.items():
    print(f"\n{lang}")
    for name, result in results.items():
        print(f"  {name}: accuracy={result['accuracy']:.3f}, scam_recall={result['scam_recall']:.3f}, scam_f1={result['scam_f1']:.3f}")

print("\nMISCLASSIFICATIONS")
errors = [d for d in details if not d["production_v2_correct"] or not d["multilingual_candidate_correct"]]
if not errors:
    print("No errors on this synthetic test set.")
for e in errors:
    print(f"{e['sample_id']} [{e['language']}] actual={e['actual_label']} | V2={e['production_v2_prediction']} | candidate={e['multilingual_candidate_prediction']}")

print(f"\nPredictions: {PRED.relative_to(ROOT)}")
print(f"Report: {REPORT.relative_to(ROOT)}")
print("PRELIMINARY ONLY: synthetic data; not independent or real-world validation.")
