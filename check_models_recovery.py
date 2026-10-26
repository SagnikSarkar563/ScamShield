from pathlib import Path
import joblib
import sklearn

model_dir = Path.cwd() / "ml" / "models"

print("scikit-learn:", sklearn.__version__)

files = [
    "scam_classifier_v2.joblib",
    "tfidf_vectorizer_v2.joblib",
    "scam_category_classifier.joblib",
    "tactic_label_encoder.joblib",
]

for name in files:
    path = model_dir / name
    print(f"\n{name}: exists={path.exists()}")
    if path.exists():
        try:
            obj = joblib.load(path)
            print("  Loaded:", type(obj).__name__)
            if hasattr(obj, "classes_"):
                print("  Classes:", obj.classes_)
            if hasattr(obj, "n_features_in_"):
                print("  Input features:", obj.n_features_in_)
        except Exception as exc:
            print("  LOAD ERROR:", type(exc).__name__, str(exc))
