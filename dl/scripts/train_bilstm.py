import os
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

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Embedding,
    Bidirectional,
    LSTM,
    Dense,
    Dropout
)
from tensorflow.keras.callbacks import EarlyStopping


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
# HYPERPARAMETERS
# ============================================================

MAX_WORDS = 10000
MAX_SEQUENCE_LENGTH = 100

EMBEDDING_DIM = 128

LSTM_UNITS = 64

DROPOUT_RATE = 0.3

BATCH_SIZE = 32

EPOCHS = 15


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("SCAMSHIELD - BiLSTM DEEP LEARNING MODEL")
print("=" * 70)

df = pd.read_csv(DATASET_PATH)

df["message"] = df["message"].fillna("")

print("\nDataset")
print("-" * 40)

print(f"Total samples : {len(df)}")
print(f"SCAM samples  : {(df['label'] == 'SCAM').sum()}")
print(f"BENIGN samples: {(df['label'] == 'BENIGN').sum()}")


# ============================================================
# PREPARE LABELS
# ============================================================

X = df["message"].astype(str)

y = (
    df["label"]
    .map({
        "BENIGN": 0,
        "SCAM": 1
    })
    .values
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=SEED,
    stratify=y
)

print("\nData Split")
print("-" * 40)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")


# ============================================================
# TOKENIZATION
# ============================================================

print("\nTokenizing text...")

tokenizer = Tokenizer(
    num_words=MAX_WORDS,
    oov_token="<OOV>"
)

tokenizer.fit_on_texts(X_train)


X_train_sequences = tokenizer.texts_to_sequences(X_train)

X_test_sequences = tokenizer.texts_to_sequences(X_test)


# ============================================================
# PADDING
# ============================================================

X_train_padded = pad_sequences(
    X_train_sequences,
    maxlen=MAX_SEQUENCE_LENGTH,
    padding="post",
    truncating="post"
)

X_test_padded = pad_sequences(
    X_test_sequences,
    maxlen=MAX_SEQUENCE_LENGTH,
    padding="post",
    truncating="post"
)


print(f"Vocabulary size : {len(tokenizer.word_index)}")
print(f"Input shape     : {X_train_padded.shape}")


# ============================================================
# BUILD BiLSTM MODEL
# ============================================================

print("\nBuilding BiLSTM model...")

model = Sequential([
    Embedding(
        input_dim=MAX_WORDS,
        output_dim=EMBEDDING_DIM,
        input_length=MAX_SEQUENCE_LENGTH
    ),

    Bidirectional(
        LSTM(
            LSTM_UNITS,
            return_sequences=False
        )
    ),

    Dropout(DROPOUT_RATE),

    Dense(
        32,
        activation="relu"
    ),

    Dropout(DROPOUT_RATE),

    Dense(
        1,
        activation="sigmoid"
    )
])


# ============================================================
# COMPILE
# ============================================================

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)


print("\nModel Architecture")
print("-" * 40)

model.summary()


# ============================================================
# EARLY STOPPING
# ============================================================

early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining BiLSTM...")
print("=" * 70)

history = model.fit(
    X_train_padded,
    y_train,
    validation_split=0.20,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[early_stopping],
    verbose=1
)


# ============================================================
# PREDICTION
# ============================================================

print("\nEvaluating model...")

probabilities = model.predict(
    X_test_padded,
    verbose=0
).ravel()


y_pred = (
    probabilities >= 0.5
).astype(int)


# ============================================================
# METRICS
# ============================================================

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


# ============================================================
# CONFUSION MATRIX
# ============================================================

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


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("BiLSTM RESULTS")
print("=" * 70)

print(f"Accuracy           : {accuracy:.4f}")
print(f"Macro Precision    : {precision:.4f}")
print(f"Macro Recall       : {recall:.4f}")
print(f"Macro F1           : {f1:.4f}")
print(f"False Positive Rate: {false_positive_rate:.4f}")


print("\nConfusion Matrix")
print("                 Predicted")
print("                 BENIGN  SCAM")

print(
    f"Actual BENIGN    {tn:6d} {fp:6d}"
)

print(
    f"Actual SCAM      {fn:6d} {tp:6d}"
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    os.path.dirname(MODEL_PATH),
    exist_ok=True
)

model.save(MODEL_PATH)


# ============================================================
# SAVE TOKENIZER
# ============================================================

tokenizer_json = tokenizer.to_json()

with open(
    TOKENIZER_PATH,
    "w",
    encoding="utf-8"
) as f:
    f.write(tokenizer_json)


print("\n" + "=" * 70)
print("MODEL SAVED")
print("=" * 70)

print(f"Model     : {MODEL_PATH}")
print(f"Tokenizer : {TOKENIZER_PATH}")

print("\nTraining complete.")
