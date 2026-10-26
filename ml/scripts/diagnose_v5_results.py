
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

path = ROOT / "experiments" / "v5_evaluation_predictions.csv"

df = pd.read_csv(path)

df = df[
    df["experiment"] == "B_UNSEEN_CAMPAIGNS_AND_CATEGORIES"
].copy()

df["correct"] = df["actual"] == df["predicted"]

print("=" * 70)
print("V5 CAMPAIGN-HOLDOUT DIAGNOSTICS")
print("=" * 70)

print("\n1. LANGUAGE AND LABEL SUMMARY")

summary = (
    df.groupby(["language", "actual"])
    .agg(
        samples=("actual", "size"),
        accuracy=("correct", "mean"),
        mean_scam_probability=("scam_probability", "mean"),
    )
    .round(4)
)

print(summary.to_string())


print("\n2. LOWEST SCAM PROBABILITIES")

scams = df[df["actual"] == "SCAM"]

print(
    scams.nsmallest(10, "scam_probability")[
        [
            "campaign_id",
            "language",
            "scam_probability",
            "predicted",
            "message",
        ]
    ].to_string(index=False)
)


print("\n3. FALSE POSITIVES")

false_positives = df[
    (df["actual"] == "BENIGN")
    & (df["predicted"] == "SCAM")
]

if false_positives.empty:
    print("No false positives.")

else:
    print(
        false_positives[
            ["language", "scam_probability", "message"]
        ].to_string(index=False)
    )


print("\n4. HIGHEST SCAM PROBABILITIES AMONG BENIGN MESSAGES")

benign = df[df["actual"] == "BENIGN"]

print(
    benign.nlargest(10, "scam_probability")[
        [
            "campaign_id",
            "language",
            "scam_probability",
            "predicted",
            "message",
        ]
    ].to_string(index=False)
)


print("\nDiagnostic complete.")
