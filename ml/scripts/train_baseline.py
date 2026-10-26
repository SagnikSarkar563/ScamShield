import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


print("=" * 70)
print("SCAMSHIELD BASELINE MODEL V4")
print("Diverse Benign Dataset + Word TF-IDF")
print("=" * 70)


# =========================================================
# 1. Paths
# =========================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "datasets",
    "ScamShield_Expanded_Dataset_v2.csv",
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "ml",
    "models",
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
      "scam_classifier_v2.joblib",
)

VECTORIZER_PATH = os.path.join(
    MODEL_DIR,
    "tfidf_vectorizer_v2.joblib",
)

os.makedirs(MODEL_DIR, exist_ok=True)


# =========================================================
# 2. Load dataset
# =========================================================

print("\nLoading dataset...")
print(DATA_PATH)

df = pd.read_csv(DATA_PATH)

df["message"] = df["message"].fillna("").astype(str)
df["label"] = df["label"].astype(str).str.upper().str.strip()

print(f"\nTotal samples: {len(df)}")
print(f"SCAM samples: {(df['label'] == 'SCAM').sum()}")
print(f"BENIGN samples: {(df['label'] == 'BENIGN').sum()}")

print("\nLanguage distribution:")
print(df["language"].value_counts())


# =========================================================
# 3. Remove exact duplicate messages
# =========================================================

before = len(df)

df = df.drop_duplicates(
    subset=["message", "label"],
    keep="first",
).reset_index(drop=True)

after = len(df)

print("\nDuplicate handling:")
print(f"Removed duplicates: {before - after}")
print(f"Unique samples: {after}")

print("\nFinal class distribution:")
print(df["label"].value_counts())


# =========================================================
# 4. Features and target
# =========================================================

X = df["message"]
y = df["label"]


# =========================================================
# 5. Train/test split
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nTrain/Test split:")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")


# =========================================================
# 6. Word TF-IDF
# =========================================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
    sublinear_tf=True,
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("\nTF-IDF:")
print(f"Training shape: {X_train_tfidf.shape}")
print(f"Testing shape : {X_test_tfidf.shape}")


# =========================================================
# 7. Logistic Regression
# =========================================================
# We intentionally do NOT use class_weight='balanced'.
#
# The dataset already contains more SCAM than BENIGN examples.
# We want to avoid unnecessarily pushing borderline messages
# toward the SCAM class.

model = LogisticRegression(
    max_iter=3000,
    class_weight=None,
    C=1.0,
    solver="liblinear",
    random_state=42,
)

print("\nTraining Logistic Regression...")

model.fit(
    X_train_tfidf,
    y_train,
)


# =========================================================
# 8. Predictions
# =========================================================

y_pred = model.predict(X_test_tfidf)


# =========================================================
# 9. Evaluation
# =========================================================

accuracy = accuracy_score(
    y_test,
    y_pred,
)

precision = precision_score(
    y_test,
    y_pred,
    pos_label="SCAM",
    zero_division=0,
)

recall = recall_score(
    y_test,
    y_pred,
    pos_label="SCAM",
    zero_division=0,
)

f1 = f1_score(
    y_test,
    y_pred,
    pos_label="SCAM",
    zero_division=0,
)


# =========================================================
# 10. Confusion Matrix
# =========================================================

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=["BENIGN", "SCAM"],
)

tn, fp, fn, tp = cm.ravel()

false_positive_rate = (
    fp / (tn + fp)
    if (tn + fp) > 0
    else 0.0
)

false_negative_rate = (
    fn / (tp + fn)
    if (tp + fn) > 0
    else 0.0
)


# =========================================================
# 11. Results
# =========================================================

print("\n" + "=" * 70)
print("V4 TEST SET RESULTS")
print("=" * 70)

print(f"Accuracy           : {accuracy:.4f}")
print(f"Precision          : {precision:.4f}")
print(f"Recall             : {recall:.4f}")
print(f"F1 Score           : {f1:.4f}")
print(f"False Positive Rate: {false_positive_rate:.4f}")
print(f"False Negative Rate: {false_negative_rate:.4f}")

print("\nConfusion Matrix")
print("----------------")
print("                Predicted")
print("              BENIGN   SCAM")
print(f"Actual BENIGN   {tn:4d}   {fp:4d}")
print(f"Actual SCAM     {fn:4d}   {tp:4d}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        labels=["BENIGN", "SCAM"],
        zero_division=0,
    )
)


# =========================================================
# 12. 5-Fold Cross Validation
# =========================================================

print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION")
print("=" * 70)

cv_vectorizer = TfidfVectorizer(
    lowercase=True,
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
    sublinear_tf=True,
)

X_cv = cv_vectorizer.fit_transform(X)

cv_model = LogisticRegression(
    max_iter=3000,
    class_weight=None,
    C=1.0,
    solver="liblinear",
    random_state=42,
)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

cv_results = cross_validate(
    cv_model,
    X_cv,
    y,
    cv=cv,
    scoring=[
        "accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
    ],
)

print(
    f"5-Fold Accuracy : "
    f"{cv_results['test_accuracy'].mean():.4f}"
)

print(
    f"5-Fold Precision: "
    f"{cv_results['test_precision_macro'].mean():.4f}"
)

print(
    f"5-Fold Recall   : "
    f"{cv_results['test_recall_macro'].mean():.4f}"
)

print(
    f"5-Fold F1       : "
    f"{cv_results['test_f1_macro'].mean():.4f}"
)


# =========================================================
# 13. Save model
# =========================================================

print("\n" + "=" * 70)
print("SAVING V4 MODEL")
print("=" * 70)

joblib.dump(
    model,
    MODEL_PATH,
)

joblib.dump(
    vectorizer,
    VECTORIZER_PATH,
)

print(f"Model      : {MODEL_PATH}")
print(f"Vectorizer : {VECTORIZER_PATH}")

print("\n" + "=" * 70)
print("SCAMSHIELD V4 TRAINING COMPLETE")
print("=" * 70)