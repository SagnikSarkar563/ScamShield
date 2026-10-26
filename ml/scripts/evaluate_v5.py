
import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# =========================================================
# ScamShield V5: Evaluation Only
# V4 model artifacts will NOT be overwritten.
# =========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "datasets",
    "ScamShield_Expanded_Dataset_v2.csv",
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "experiments",
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 72)
print("SCAMSHIELD V5 - EVALUATION EXPERIMENT")
print("Random Split vs Unseen Campaigns")
print("=" * 72)


# =========================================================
# 1. Load and validate dataset
# =========================================================

df = pd.read_csv(DATA_PATH)

required_columns = {
    "message",
    "label",
    "campaign_id",
    "language",
    "scam_category",
}

missing = required_columns - set(df.columns)

if missing:
    raise ValueError(
        f"Dataset is missing required columns: {sorted(missing)}"
    )

df["message"] = df["message"].fillna("").astype(str).str.strip()
df["label"] = df["label"].astype(str).str.upper().str.strip()
df["campaign_id"] = df["campaign_id"].fillna("").astype(str).str.strip()

df = df[df["label"].isin(["SCAM", "BENIGN"])].copy()
df = df[df["message"] != ""].copy()

# Match V4's exact message/label duplicate handling.
df = df.drop_duplicates(
    subset=["message", "label"],
    keep="first",
).reset_index(drop=True)

print(f"\nDataset: {DATA_PATH}")
print(f"Total samples: {len(df)}")
print(f"SCAM samples: {(df['label'] == 'SCAM').sum()}")
print(f"BENIGN samples: {(df['label'] == 'BENIGN').sum()}")


# =========================================================
# 2. Define model
# =========================================================

def create_model():
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                analyzer="word",
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=3000,
                class_weight=None,
                C=1.0,
                solver="liblinear",
                random_state=42,
            ),
        ),
    ])


# =========================================================
# 3. Evaluation helper
# =========================================================

all_predictions = []
all_metrics = []


def evaluate_experiment(
    experiment_name,
    train_df,
    test_df,
):
    print("\n" + "=" * 72)
    print(experiment_name)
    print("=" * 72)

    if train_df.empty or test_df.empty:
        raise ValueError("Training or test set is empty.")

    if set(train_df["label"]) != {"SCAM", "BENIGN"}:
        raise ValueError(
            "Training set must contain both SCAM and BENIGN samples."
        )

    X_train = train_df["message"]
    y_train = train_df["label"]

    X_test = test_df["message"]
    y_test = test_df["label"]

    model = create_model()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    scam_index = list(model.classes_).index("SCAM")
    scam_probabilities = probabilities[:, scam_index]

    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test,
        predictions,
        pos_label="SCAM",
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        pos_label="SCAM",
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        pos_label="SCAM",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=["BENIGN", "SCAM"],
    )

    tn, fp, fn, tp = cm.ravel()

    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0

    print(f"Training samples: {len(train_df)}")
    print(f"Testing samples : {len(test_df)}")
    print(f"Test SCAM       : {(y_test == 'SCAM').sum()}")
    print(f"Test BENIGN     : {(y_test == 'BENIGN').sum()}")

    print("\nMetrics")
    print("-" * 40)
    print(f"Accuracy           : {accuracy:.4f}")
    print(f"SCAM Precision     : {precision:.4f}")
    print(f"SCAM Recall        : {recall:.4f}")
    print(f"SCAM F1            : {f1:.4f}")
    print(f"Macro F1           : {macro_f1:.4f}")
    print(f"False Positive Rate: {fpr:.4f}")
    print(f"False Negative Rate: {fnr:.4f}")

    print("\nConfusion Matrix")
    print("                Predicted")
    print("              BENIGN   SCAM")
    print(f"Actual BENIGN   {tn:4d}   {fp:4d}")
    print(f"Actual SCAM     {fn:4d}   {tp:4d}")

    print("\nClassification Report")
    print(
        classification_report(
            y_test,
            predictions,
            labels=["BENIGN", "SCAM"],
            zero_division=0,
        )
    )

    metrics = {
        "experiment": experiment_name,
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "test_scam": int((y_test == "SCAM").sum()),
        "test_benign": int((y_test == "BENIGN").sum()),
        "accuracy": accuracy,
        "scam_precision": precision,
        "scam_recall": recall,
        "scam_f1": f1,
        "macro_f1": macro_f1,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }

    all_metrics.append(metrics)

    predictions_df = pd.DataFrame({
        "experiment": experiment_name,
        "sample_id": test_df["sample_id"].values
        if "sample_id" in test_df.columns
        else test_df.index.astype(str),
        "campaign_id": test_df["campaign_id"].values,
        "scam_category": test_df["scam_category"].values,
        "language": test_df["language"].values,
        "message": X_test.values,
        "actual": y_test.values,
        "predicted": predictions,
        "scam_probability": scam_probabilities,
    })

    all_predictions.append(predictions_df)

    return metrics


# =========================================================
# 4. Experiment A: Random stratified split
# =========================================================

train_random, test_random = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["label"],
)

random_metrics = evaluate_experiment(
    "A_RANDOM_SPLIT",
    train_random,
    test_random,
)


# =========================================================
# 5. Experiment B: Hold out entire scam campaigns
# =========================================================
# These four campaigns are held out completely:
# DP02, FS02, GP02, UP02.
#
# IMPORTANT:
# Each campaign maps to its own specific category in this
# dataset. This therefore tests a mixture of unseen-campaign
# and unseen-category generalization, not campaign effects alone.

HELD_OUT_CAMPAIGNS = [
    "DP02",
    "FS02",
    "GP02",
    "UP02",
]

scam_df = df[df["label"] == "SCAM"].copy()
benign_df = df[df["label"] == "BENIGN"].copy()

available_campaigns = set(scam_df["campaign_id"])

missing_campaigns = (
    set(HELD_OUT_CAMPAIGNS) - available_campaigns
)

if missing_campaigns:
    raise ValueError(
        f"Campaigns not found: {sorted(missing_campaigns)}"
    )

held_out_scam = scam_df[
    scam_df["campaign_id"].isin(HELD_OUT_CAMPAIGNS)
].copy()

remaining_scam = scam_df[
    ~scam_df["campaign_id"].isin(HELD_OUT_CAMPAIGNS)
].copy()

# Use the same random state to create a reproducible benign split.
benign_train, benign_test = train_test_split(
    benign_df,
    test_size=0.20,
    random_state=42,
)

train_campaign = pd.concat(
    [remaining_scam, benign_train],
    ignore_index=True,
)

test_campaign = pd.concat(
    [held_out_scam, benign_test],
    ignore_index=True,
)

# Check that none of the held-out scam campaigns leaked into training.
training_scam_campaigns = set(
    train_campaign.loc[
        train_campaign["label"] == "SCAM",
        "campaign_id",
    ]
)

assert not (
    training_scam_campaigns & set(HELD_OUT_CAMPAIGNS)
), "Campaign leakage detected!"

print("\nHeld-out scam campaigns:", HELD_OUT_CAMPAIGNS)
print("Held-out scam samples:", len(held_out_scam))
print("Scam training samples:", len(remaining_scam))

campaign_metrics = evaluate_experiment(
    "B_UNSEEN_CAMPAIGNS_AND_CATEGORIES",
    train_campaign,
    test_campaign,
)


# =========================================================
# 6. Save results
# =========================================================

metrics_path = os.path.join(
    OUTPUT_DIR,
    "v5_evaluation_metrics.csv",
)

predictions_path = os.path.join(
    OUTPUT_DIR,
    "v5_evaluation_predictions.csv",
)

pd.DataFrame(all_metrics).to_csv(
    metrics_path,
    index=False,
)

pd.concat(
    all_predictions,
    ignore_index=True,
).to_csv(
    predictions_path,
    index=False,
)


# =========================================================
# 7. Comparison
# =========================================================

print("\n" + "=" * 72)
print("V5 EXPERIMENT COMPARISON")
print("=" * 72)

comparison = pd.DataFrame(all_metrics)

columns = [
    "experiment",
    "accuracy",
    "scam_precision",
    "scam_recall",
    "scam_f1",
    "macro_f1",
    "false_positive_rate",
    "false_negative_rate",
]

print(
    comparison[columns].to_string(
        index=False,
        formatters={
            column: "{:.4f}".format
            for column in columns
            if column != "experiment"
        },
    )
)

print("\nSaved metrics:")
print(metrics_path)

print("\nSaved individual predictions:")
print(predictions_path)

print("\nV5 evaluation complete.")
print("No V4 model files were modified.")
