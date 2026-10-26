import json
import random

import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Embedding,
    Bidirectional,
    LSTM,
    Dense,
    Dropout
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = r".\datasets\ScamShield_Expanded_Dataset_v1.csv"

MODEL_PATH = r".\dl\models\bilstm_scam_classifier.keras"

TOKENIZER_PATH = r".\dl\models\bilstm_tokenizer.json"


# ============================================================
# SETTINGS
# ============================================================

MAX_SEQUENCE_LENGTH = 100

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
print("SCAMSHIELD - BiLSTM UNSEEN CAMPAIGN EVALUATION")
print("=" * 70)


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv(DATASET_PATH)

df["message"] = df["message"].fillna("")


print("\nDataset")
print("-" * 40)

print(f"Total samples : {len(df)}")
print(f"SCAM samples  : {(df['label'] == 'SCAM').sum()}")
print(f"BENIGN samples: {(df['label'] == 'BENIGN').sum()}")


# ============================================================
# LOAD TRAINED MODEL
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

    tokenizer_json = json.load(f)


tokenizer = tokenizer_from_json(
    json.dumps(tokenizer_json)
)


print("Model and tokenizer loaded successfully.")


# ============================================================
# SEPARATE DATA
# ============================================================

scam_df = df[
    df["label"] == "SCAM"
].copy()

benign_df = df[
    df["campaign_id"].isin(BENIGN_CAMPAIGNS)
].copy()


results = []


# ============================================================
# CAMPAIGN LOOP
# ============================================================

for test_campaign in SCAM_CAMPAIGNS:

    print("\n" + "=" * 70)
    print(f"UNSEEN CAMPAIGN: {test_campaign}")
    print("=" * 70)


    # --------------------------------------------------------
    # Hold out complete scam campaign
    # --------------------------------------------------------

    unseen_scam = scam_df[
        scam_df["campaign_id"] == test_campaign
    ].copy()


    remaining_scam = scam_df[
        scam_df["campaign_id"] != test_campaign
    ].copy()


    # --------------------------------------------------------
    # Split benign samples
    # --------------------------------------------------------

    benign_train, benign_test = train_test_split(
        benign_df,
        test_size=0.20,
        random_state=SEED,
        stratify=benign_df["label"]
    )


    # --------------------------------------------------------
    # Create train/test sets
    # --------------------------------------------------------

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


    X_train = train_df["message"].astype(str)
    y_train = (
        train_df["label"]
        .map({
            "BENIGN": 0,
            "SCAM": 1
        })
        .values
    )


    X_test = test_df["message"].astype(str)
    y_test = (
        test_df["label"]
        .map({
            "BENIGN": 0,
            "SCAM": 1
        })
        .values
    )


    print(f"Training samples : {len(train_df)}")
    print(f"Test samples     : {len(test_df)}")

    print(
        f"Training SCAM    : "
        f"{(y_train == 1).sum()}"
    )

    print(
        f"Training BENIGN  : "
        f"{(y_train == 0).sum()}"
    )

    print(
        f"Test SCAM        : "
        f"{(y_test == 1).sum()}"
    )

    print(
        f"Test BENIGN      : "
        f"{(y_test == 0).sum()}"
    )


    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    X_test_sequences = tokenizer.texts_to_sequences(
        X_test
    )


    X_test_padded = pad_sequences(
        X_test_sequences,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post",
        truncating="post"
    )


    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    probabilities = model.predict(
        X_test_padded,
        verbose=0
    ).ravel()


    y_pred = (
        probabilities >= 0.5
    ).astype(int)


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


    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    )

    tn, fp, fn, tp = cm.ravel()


    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )


    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

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
        f"False Positive Rate : "
        f"{false_positive_rate:.4f}"
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


# ============================================================
# FINAL RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)


print("\n" + "=" * 70)
print("FINAL BiLSTM UNSEEN-CAMPAIGN RESULTS")
print("=" * 70)

print(
    results_df.to_string(index=False)
)


# ============================================================
# AVERAGE
# ============================================================

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