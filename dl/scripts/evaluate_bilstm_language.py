import json
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences


DATASET_PATH = r".\datasets\ScamShield_Expanded_Dataset_v1.csv"

MODEL_PATH = r".\dl\models\bilstm_scam_classifier.keras"

TOKENIZER_PATH = r".\dl\models\bilstm_tokenizer.json"

MAX_SEQUENCE_LENGTH = 100

LANGUAGES = [
    "English",
    "Hinglish"
]


print("=" * 70)
print("SCAMSHIELD - BiLSTM ENGLISH vs HINGLISH EVALUATION")
print("=" * 70)


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv(DATASET_PATH)

df["message"] = df["message"].fillna("")


print("\nDataset")
print("-" * 40)

print(
    df["language"]
    .value_counts()
    .to_string()
)


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading BiLSTM model...")

model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# LOAD TOKENIZER
# ============================================================

print("Loading tokenizer...")

with open(
    TOKENIZER_PATH,
    "r",
    encoding="utf-8"
) as f:
    tokenizer_json = f.read()


tokenizer = tokenizer_from_json(
    tokenizer_json
)

print("Model and tokenizer loaded successfully.")


# ============================================================
# LANGUAGE EVALUATION
# ============================================================

results = []


for language in LANGUAGES:

    print("\n" + "=" * 70)
    print(f"LANGUAGE: {language}")
    print("=" * 70)


    lang_df = df[
        df["language"] == language
    ].copy()


    print(
        f"Total samples: {len(lang_df)}"
    )

    print(
        f"SCAM: {(lang_df['label'] == 'SCAM').sum()}"
    )

    print(
        f"BENIGN: {(lang_df['label'] == 'BENIGN').sum()}"
    )


    # --------------------------------------------------------
    # Prepare data
    # --------------------------------------------------------

    X = lang_df["message"].astype(str)

    y = (
        lang_df["label"]
        .map({
            "BENIGN": 0,
            "SCAM": 1
        })
        .values
    )


    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    sequences = tokenizer.texts_to_sequences(
        X
    )


    padded = pad_sequences(
        sequences,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post"
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    probabilities = model.predict(
        padded,
        verbose=0
    ).ravel()


    y_pred = (
        probabilities >= 0.5
    ).astype(int)


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y,
        y_pred
    )

    precision = precision_score(
        y,
        y_pred,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        y,
        y_pred,
        average="macro",
        zero_division=0
    )

    f1 = f1_score(
        y,
        y_pred,
        average="macro",
        zero_division=0
    )


    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        y,
        y_pred,
        labels=[0, 1]
    )

    tn, fp, fn, tp = cm.ravel()


    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )


    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print("\nBiLSTM")
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
        f"False Positive Rate : {fpr:.4f}"
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


    results.append({
        "language": language,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr
    })


# ============================================================
# SUMMARY
# ============================================================

results_df = pd.DataFrame(
    results
)


print("\n" + "=" * 70)
print("BiLSTM LANGUAGE EVALUATION SUMMARY")
print("=" * 70)

print(
    results_df.to_string(index=False)
)


print("\nEvaluation complete.")