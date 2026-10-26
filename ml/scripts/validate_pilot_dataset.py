
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "datasets"

SCAM_FILE = DATASET_DIR / "ScamShield_Independent_Validation_Pilot_5_Scams.csv"
BENIGN_FILE = DATASET_DIR / "ScamShield_Benign_Control_Examples_5.csv"
OUTPUT_FILE = DATASET_DIR / "independent_validation_pilot.csv"

REQUIRED_COLUMNS = [
    "sample_id",
    "message",
    "label",
    "language",
    "scam_category",
    "source_type",
    "source_title",
    "source_url",
    "collection_date",
    "campaign_group",
    "consent_status",
    "pii_removed",
    "independent_review",
    "reviewer_notes",
]

def main():
    for path in [SCAM_FILE, BENIGN_FILE]:
        if not path.exists():
            raise FileNotFoundError(
                f"Missing file: {path}\n"
                "Save both downloaded CSV files in the datasets folder."
            )

    scam_df = pd.read_csv(SCAM_FILE, dtype=str).fillna("")
    benign_df = pd.read_csv(BENIGN_FILE, dtype=str).fillna("")

    print("=" * 72)
    print("SCAMSHIELD — PILOT DATA QUALITY CHECK")
    print("=" * 72)

    for name, df in [("Scam file", scam_df), ("Benign file", benign_df)]:
        missing_columns = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
        if missing_columns:
            raise ValueError(
                f"{name} is missing columns: {missing_columns}"
            )

    combined = pd.concat([scam_df, benign_df], ignore_index=True)
    combined = combined[REQUIRED_COLUMNS]

    # Normalize whitespace without changing the underlying wording.
    for column in combined.columns:
        combined[column] = combined[column].astype(str).str.strip()

    print(f"\nRows loaded: {len(combined)}")
    print("\nLabel counts:")
    print(combined["label"].value_counts(dropna=False).to_string())

    valid_labels = {"SCAM", "BENIGN", "UNCERTAIN"}
    invalid_labels = sorted(set(combined["label"]) - valid_labels)
    print(f"\nInvalid labels: {invalid_labels or 'None'}")

    missing_message = combined["message"].eq("")
    missing_id = combined["sample_id"].eq("")
    duplicate_ids = combined["sample_id"].duplicated(keep=False)
    duplicate_messages = combined["message"].str.casefold().duplicated(
        keep=False
    )

    print(f"Empty messages: {int(missing_message.sum())}")
    print(f"Empty sample IDs: {int(missing_id.sum())}")
    print(f"Rows with duplicate IDs: {int(duplicate_ids.sum())}")
    print(f"Rows with duplicate messages: {int(duplicate_messages.sum())}")

    # Source URLs are required for non-synthetic examples.
    non_synthetic = ~combined["source_type"].str.lower().eq("synthetic")
    missing_source_url = non_synthetic & combined["source_url"].eq("")
    print(
        "Non-synthetic rows missing source URLs: "
        f"{int(missing_source_url.sum())}"
    )

    print("\nSource-type counts:")
    print(combined["source_type"].value_counts(dropna=False).to_string())

    print("\nLanguage counts:")
    print(combined["language"].value_counts(dropna=False).to_string())

    print("\nReview status:")
    print(
        combined["independent_review"]
        .value_counts(dropna=False)
        .to_string()
    )

    combined.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\nCombined file saved to:\n{OUTPUT_FILE}")
    print("\nIMPORTANT:")
    print("- Review every label and source before scoring the model.")
    print("- These 10 rows are a pipeline pilot, not real-world validation.")
    print("- Do not train on this file or use it to tune the threshold.")
    print("- No model files were modified.")

if __name__ == "__main__":
    main()
