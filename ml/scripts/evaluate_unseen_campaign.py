import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split


DATASET_PATH = r".\datasets\ScamShield_Expanded_Dataset_v1.csv"

SCAM_CAMPAIGNS = [
    "BK02",
    "DP02",
    "FS02",
    "GP02",
    "IV02",
    "JB02",
    "SM02",
    "UP02",
    "UT02"
]

BENIGN_CAMPAIGNS = [
    "BENIGN_CTRL",
    "BENIGN_EXPANDED"
]


print("=" * 70)
print("SCAMSHIELD - UNSEEN CAMPAIGN EVALUATION")
print("=" * 70)

df = pd.read_csv(DATASET_PATH)

df["message"] = df["message"].fillna("")


# ---------------------------------------------------------
# Separate scam and benign samples
# ---------------------------------------------------------

scam_df = df[df["label"] == "SCAM"].copy()

benign_df = df[
    df["campaign_id"].isin(BENIGN_CAMPAIGNS)
].copy()


results = []


for test_campaign in SCAM_CAMPAIGNS:

    print("\n" + "=" * 70)
    print(f"UNSEEN CAMPAIGN: {test_campaign}")
    print("=" * 70)

    # -----------------------------------------------------
    # Hold out one complete scam campaign
    # -----------------------------------------------------

    unseen_scam = scam_df[
        scam_df["campaign_id"] == test_campaign
    ].copy()

    remaining_scam = scam_df[
        scam_df["campaign_id"] != test_campaign
    ].copy()


    # -----------------------------------------------------
    # Split benign data into train/test
    # -----------------------------------------------------

    benign_train, benign_test = train_test_split(
        benign_df,
        test_size=0.20,
        random_state=42,
        stratify=benign_df["label"]
    )


    # -----------------------------------------------------
    # Create train and test datasets
    # -----------------------------------------------------

    train_df = pd.concat(
        [
            remaining_scam,
            benign_train
        ],
        ignore_index=True
    )

    test_df = pd.concat(
        [
            unseen_scam,
            benign_test
        ],
        ignore_index=True
    )


    X_train = train_df["message"]
    y_train = train_df["label"]

    X_test = test_df["message"]
    y_test = test_df["label"]


    print(f"Training samples : {len(train_df)}")
    print(f"Test samples     : {len(test_df)}")

    print(
        f"Training SCAM    : "
        f"{(y_train == 'SCAM').sum()}"
    )

    print(
        f"Training BENIGN  : "
        f"{(y_train == 'BENIGN').sum()}"
    )

    print(
        f"Test SCAM        : "
        f"{(y_test == 'SCAM').sum()}"
    )

    print(
        f"Test BENIGN      : "
        f"{(y_test == 'BENIGN').sum()}"
    )


    # -----------------------------------------------------
    # TF-IDF
    # -----------------------------------------------------

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )


    X_train_tfidf = vectorizer.fit_transform(X_train)

    X_test_tfidf = vectorizer.transform(X_test)


    # -----------------------------------------------------
    # Logistic Regression
    # -----------------------------------------------------

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )

    model.fit(
        X_train_tfidf,
        y_train
    )


    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    y_pred = model.predict(
        X_test_tfidf
    )


    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="macro",
        zero_division=0
    )


    # -----------------------------------------------------
    # Confusion Matrix
    # -----------------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=["BENIGN", "SCAM"]
    )

    tn, fp, fn, tp = cm.ravel()


    # -----------------------------------------------------
    # False Positive Rate
    # -----------------------------------------------------

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )


    # -----------------------------------------------------
    # Display results
    # -----------------------------------------------------

    print("\nResults")
    print("-" * 40)

    print(
        f"Accuracy           : {accuracy:.4f}"
    )

    print(
        f"Macro Precision    : {precision:.4f}"
    )

    print(
        f"Macro Recall       : {recall:.4f}"
    )

    print(
        f"Macro F1           : {f1:.4f}"
    )

    print(
        f"False Positive Rate : {false_positive_rate:.4f}"
    )


    print("\nConfusion Matrix")
    print("                 Predicted")
    print("                 BENIGN  SCAM")

    print(
        f"Actual BENIGN    {tn:6d} {fp:6d}"
    )

    print(
        f"Actual SCAM      {fn:6d} {tp:6d}"
    )


    results.append(
        {
            "campaign": test_campaign,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "false_positive_rate": false_positive_rate
        }
    )


# ---------------------------------------------------------
# Final results
# ---------------------------------------------------------

results_df = pd.DataFrame(results)


print("\n" + "=" * 70)
print("FINAL UNSEEN-CAMPAIGN RESULTS")
print("=" * 70)

print(
    results_df.to_string(index=False)
)


print("\n" + "=" * 70)
print("AVERAGE PERFORMANCE")
print("=" * 70)

print(
    f"Mean Accuracy            : "
    f"{results_df['accuracy'].mean():.4f}"
)

print(
    f"Mean Macro Precision     : "
    f"{results_df['precision'].mean():.4f}"
)

print(
    f"Mean Macro Recall        : "
    f"{results_df['recall'].mean():.4f}"
)

print(
    f"Mean Macro F1            : "
    f"{results_df['f1'].mean():.4f}"
)

print(
    f"Mean False Positive Rate : "
    f"{results_df['false_positive_rate'].mean():.4f}"
)


print("\nEvaluation complete.")