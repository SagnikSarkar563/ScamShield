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

DATASET_PATH = r".\datasets\ScamShield_Expanded_Dataset_v1.csv"

LANGUAGES = ["English", "Hinglish"]


print("=" * 70)
print("SCAMSHIELD - ENGLISH vs HINGLISH EVALUATION")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATASET_PATH)

df["message"] = df["message"].fillna("")


print("\nDataset")
print("-" * 40)

print(df["language"].value_counts().to_string())


# ============================================================
# EVALUATE EACH LANGUAGE
# ============================================================

results = []


for language in LANGUAGES:

    print("\n" + "=" * 70)
    print(f"LANGUAGE: {language}")
    print("=" * 70)

    lang_df = df[
        df["language"] == language
    ].copy()

    print(f"Total samples: {len(lang_df)}")
    print(
        f"SCAM: {(lang_df['label'] == 'SCAM').sum()}"
    )
    print(
        f"BENIGN: {(lang_df['label'] == 'BENIGN').sum()}"
    )


    # --------------------------------------------------------
    # Train/Test Split
    # --------------------------------------------------------

    X = lang_df["message"]

    y = lang_df["label"]

    X_train, X_test, y_train, y_test = __import__(
        "sklearn.model_selection",
        fromlist=["train_test_split"]
    ).train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )


    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )

    X_train_tfidf = vectorizer.fit_transform(
        X_train
    )

    X_test_tfidf = vectorizer.transform(
        X_test
    )


    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    )

    model.fit(
        X_train_tfidf,
        y_train
    )

    y_pred = model.predict(
        X_test_tfidf
    )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

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


    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=["BENIGN", "SCAM"]
    )

    tn, fp, fn, tp = cm.ravel()

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )


    print("\nTF-IDF + Logistic Regression")
    print("-" * 40)

    print(f"Accuracy           : {accuracy:.4f}")
    print(f"Macro Precision    : {precision:.4f}")
    print(f"Macro Recall       : {recall:.4f}")
    print(f"Macro F1           : {f1:.4f}")
    print(f"False Positive Rate : {fpr:.4f}")


    print("\nConfusion Matrix")
    print("                 Predicted")
    print("                 BENIGN  SCAM")

    print(
        f"Actual BENIGN    {tn:6d} {fp:6d}"
    )

    print(
        f"Actual SCAM      {fn:6d} {tp:6d}"
    )


    results.append({
        "language": language,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr
    })


# ============================================================
# FINAL RESULTS
# ============================================================

results_df = pd.DataFrame(results)


print("\n" + "=" * 70)
print("LANGUAGE EVALUATION SUMMARY")
print("=" * 70)

print(
    results_df.to_string(index=False)
)


print("\nEvaluation complete.")