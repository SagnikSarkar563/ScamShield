
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

ROOT = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    ROOT
    / "experiments"
    / "v5_evaluation_predictions.csv"
)

df = pd.read_csv(INPUT_PATH)

df = df[
    df["experiment"] == "B_UNSEEN_CAMPAIGNS_AND_CATEGORIES"
].copy()

y_true = df["actual"]
probabilities = df["scam_probability"]

print("=" * 88)
print("SCAMSHIELD V5 — THRESHOLD ANALYSIS")
print("=" * 88)

print(
    f"{'Threshold':<12}"
    f"{'Accuracy':<12}"
    f"{'Precision':<12}"
    f"{'Recall':<12}"
    f"{'F1':<12}"
    f"{'FPR':<12}"
    f"{'FNR':<12}"
)

for threshold in [0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:

    y_pred = probabilities.ge(threshold).map({
        True: "SCAM",
        False: "BENIGN",
    })

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=["BENIGN", "SCAM"],
    ).ravel()

    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true,
        y_pred,
        pos_label="SCAM",
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        pos_label="SCAM",
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        pos_label="SCAM",
        zero_division=0,
    )

    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0

    print(
        f"{threshold:<12.2f}"
        f"{accuracy:<12.4f}"
        f"{precision:<12.4f}"
        f"{recall:<12.4f}"
        f"{f1:<12.4f}"
        f"{fpr:<12.4f}"
        f"{fnr:<12.4f}"
    )

print("\nAnalysis complete. No model files were changed.")
