
import json
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "ml" / "models"
OUT_DIR = ROOT / "experiments"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Synthetic examples for testing the multilingual training pipeline.
# These are not real-world scam messages or a representative dataset.
train_data = [
    # English scams
    ("Your bank account will be blocked today. Send your OTP now.", "SCAM"),
    ("Congratulations, you won a prize. Pay a fee to claim it.", "SCAM"),
    ("Your parcel is held. Pay this link immediately to release it.", "SCAM"),
    ("Your KYC expires today. Verify your account using this link.", "SCAM"),
    ("You are selected for a job. Pay a registration fee first.", "SCAM"),
    ("Your account is compromised. Share your PIN to secure it.", "SCAM"),
    ("Urgent: transfer money now or your account will be frozen.", "SCAM"),
    ("Click here to receive your government benefit payment.", "SCAM"),

    # English benign
    ("The library meeting starts at four in the afternoon.", "BENIGN"),
    ("I paid the electricity bill through the official app.", "BENIGN"),
    ("My job interview is scheduled for Monday morning.", "BENIGN"),
    ("Please send me the notes from today's lecture.", "BENIGN"),
    ("I checked my bank statement in the official application.", "BENIGN"),
    ("Dinner is ready. We can split the bill later.", "BENIGN"),
    ("The parcel arrived safely this afternoon.", "BENIGN"),
    ("I will submit the college assignment tonight.", "BENIGN"),

    # Hindi scams
    ("आपका बैंक खाता बंद हो जाएगा। अपना ओटीपी तुरंत भेजें।", "SCAM"),
    ("इनाम पाने के लिए पहले फीस जमा करें।", "SCAM"),
    ("आपका केवाईसी बंद हो रहा है। इस लिंक पर जानकारी भरें।", "SCAM"),
    ("नौकरी पक्की करने के लिए रजिस्ट्रेशन फीस भेजें।", "SCAM"),
    ("खाता सुरक्षित करने के लिए अपना पिन बताएं।", "SCAM"),
    ("बिजली कटने से बचाने के लिए अभी भुगतान करें।", "SCAM"),
    ("पैसे पाने के लिए इस लिंक पर बैंक विवरण डालें।", "SCAM"),
    ("आपका पार्सल रोक दिया गया है। तुरंत शुल्क भरें।", "SCAM"),

    # Hindi benign
    ("मैंने आधिकारिक ऐप से बिजली का बिल जमा किया।", "BENIGN"),
    ("मेरी नौकरी का इंटरव्यू सोमवार को है।", "BENIGN"),
    ("कक्षा की नोट्स कृपया मुझे भेज देना।", "BENIGN"),
    ("मैंने बैंक का स्टेटमेंट ऐप में देखा।", "BENIGN"),
    ("आज शाम को परिवार के साथ खाना खाएंगे।", "BENIGN"),
    ("कॉलेज का असाइनमेंट आज रात जमा करना है।", "BENIGN"),
    ("मेरा पार्सल आज सुरक्षित पहुंच गया।", "BENIGN"),
    ("कल पुस्तकालय में चार बजे मिलते हैं।", "BENIGN"),

    # Hinglish scams
    ("Aapka bank account block hoga, OTP abhi bhejo.", "SCAM"),
    ("Lottery jeet gaye ho, prize lene ke liye fee pay karo.", "SCAM"),
    ("KYC expire ho raha hai, link par details daalo.", "SCAM"),
    ("Job confirm karne ke liye registration fee bhejo.", "SCAM"),
    ("Bijli cut hogi, abhi is link se payment karo.", "SCAM"),
    ("Account safe karne ke liye apna PIN share karo.", "SCAM"),
    ("Parcel release karwana hai toh abhi fee pay karo.", "SCAM"),
    ("Government benefit ke liye bank details link par bharo.", "SCAM"),

    # Hinglish benign
    ("Maine official app se electricity bill pay kiya.", "BENIGN"),
    ("Mera job interview Monday morning ko hai.", "BENIGN"),
    ("Please class ke notes mujhe WhatsApp kar dena.", "BENIGN"),
    ("Maine bank statement official app mein check kiya.", "BENIGN"),
    ("Dinner ka bill baad mein split kar lenge.", "BENIGN"),
    ("College assignment aaj raat submit karunga.", "BENIGN"),
    ("Mera parcel safely aaj afternoon mein aa gaya.", "BENIGN"),
    ("Library mein four baje milte hain.", "BENIGN"),
]


# Small, separate smoke-test set.
# These examples are not a scientific benchmark.
test_data = [
    ("Send your OTP immediately or your account will close.",
     "SCAM", "English"),
    ("Pay a processing fee to receive your prize.",
     "SCAM", "English"),
    ("I reviewed my bank statement in the official app.",
     "BENIGN", "English"),
    ("My class begins at ten tomorrow.",
     "BENIGN", "English"),

    ("आपका खाता बंद होगा, अभी ओटीपी भेजें।",
     "SCAM", "Hindi"),
    ("इनाम के लिए पहले पैसे जमा करें।",
     "SCAM", "Hindi"),
    ("मैंने आधिकारिक ऐप में अपना बिल देखा।",
     "BENIGN", "Hindi"),
    ("कल कॉलेज में परीक्षा है।",
     "BENIGN", "Hindi"),

    ("OTP bhejo warna bank account block ho jayega.",
     "SCAM", "Hinglish"),
    ("Prize claim karne ke liye pehle fee pay karo.",
     "SCAM", "Hinglish"),
    ("Maine official app mein bill check kiya.",
     "BENIGN", "Hinglish"),
    ("Aaj college mein friends ke saath lunch hai.",
     "BENIGN", "Hinglish"),
]


train_df = pd.DataFrame(train_data, columns=["message", "label"])
test_df = pd.DataFrame(
    test_data, columns=["message", "expected", "language"]
)


# Word features capture words and phrases.
# Character features can capture script and spelling variations.
model = Pipeline([
    ("features", FeatureUnion([
        ("word", TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=12000,
        )),
        ("char", TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 5),
            sublinear_tf=True,
            max_features=20000,
        )),
    ])),
    ("classifier", LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )),
])


print("Training experimental multilingual candidate...")
start = time.time()

model.fit(train_df["message"], train_df["label"])

test_df["predicted"] = model.predict(test_df["message"])
test_df["correct"] = test_df["expected"] == test_df["predicted"]

candidate_path = MODEL_DIR / "scam_multilingual_candidate.joblib"
results_path = OUT_DIR / "multilingual_candidate_smoke_tests.csv"
summary_path = OUT_DIR / "multilingual_candidate_summary.json"

# Save only to new filenames. Do not replace the production model.
joblib.dump(model, candidate_path)

test_df.to_csv(
    results_path,
    index=False,
    encoding="utf-8-sig",
)

summary = {
    "purpose": "Synthetic multilingual pipeline smoke test",
    "training_examples": int(len(train_df)),
    "training_scam": int((train_df["label"] == "SCAM").sum()),
    "training_benign": int((train_df["label"] == "BENIGN").sum()),
    "test_examples": int(len(test_df)),
    "correct": int(test_df["correct"].sum()),
    "accuracy": float(
        accuracy_score(test_df["expected"], test_df["predicted"])
    ),
    "seconds": round(time.time() - start, 2),
    "warning": (
        "Synthetic examples only. This score is not a real-world "
        "accuracy estimate and does not justify production deployment."
    ),
}

summary_path.write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("\n=== CANDIDATE SUMMARY ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))

print("\n=== RESULTS BY LANGUAGE ===")
print(
    test_df.groupby("language")["correct"]
    .agg(["sum", "count"])
    .to_string()
)

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(
    test_df["expected"],
    test_df["predicted"],
    zero_division=0,
))

print("\n=== INDIVIDUAL TEST RESULTS ===")
print(test_df[
    ["language", "message", "expected", "predicted", "correct"]
].to_string(index=False))

print(f"\nCandidate model: {candidate_path}")
print(f"Test results:    {results_path}")
print(f"Summary:         {summary_path}")
print("\nProduction model was NOT changed.")
