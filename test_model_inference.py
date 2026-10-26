from pathlib import Path
import joblib

root = Path(__file__).resolve().parent
model_dir = root / "ml" / "models"

model = joblib.load(model_dir / "scam_classifier_v2.joblib")
vectorizer = joblib.load(model_dir / "tfidf_vectorizer_v2.joblib")

samples = [
    "Your bank account will be blocked today. Verify your KYC immediately and enter your OTP.",
    "Hey, are we still meeting for lunch at 1 PM?",
]

print("=== CLASSIFIER TEST ===")
for message in samples:
    features = vectorizer.transform([message])
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    classes = list(model.classes_)
    scam_probability = float(probabilities[classes.index("SCAM")])

    print("\nMessage:", message)
    print("Prediction:", prediction)
    print(f"SCAM probability: {scam_probability:.4f}")

print("\n=== URL ANALYZER TEST ===")
try:
    from ml.scripts.url_analyzer import analyze_text_urls

    result = analyze_text_urls(
        "Please verify your account at http://secure-bank-verify-kyc.xyz/login"
    )
    print("URL analyzer returned:", type(result).__name__)
    print("Result:", result)
except Exception as exc:
    print("URL ANALYZER ERROR:", type(exc).__name__, str(exc))

print("\n=== CATEGORY MODEL COMPATIBILITY ===")
category_model = joblib.load(model_dir / "scam_category_classifier.joblib")
print("Category model expects features:", category_model.n_features_in_)
print("Available V2 vectorizer features:", len(vectorizer.get_feature_names_out()))
