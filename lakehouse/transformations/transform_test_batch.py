# ------------------------------------------------------------
# Batch Feature Transformation Script
#
# Purpose:
# Convert processed test data into model-ready features using
# the previously trained feature transformer.
#
# Pipeline stage:
# Processed Data → Feature Transformer → Curated Data
#
# This ensures the test data is transformed exactly the same
# way as training data.
# ------------------------------------------------------------

from pathlib import Path
import pandas as pd
import joblib

# ------------------------------------------------------------
# Directory configuration
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "lakehouse" / "processed"
CURATED_DIR = PROJECT_ROOT / "lakehouse" / "curated"
ARTIFACTS_DIR = PROJECT_ROOT / "model_artifacts"

def main():
    # ------------------------------------------------------------
    # Load processed dataset
    # ------------------------------------------------------------
    print("Loading processed test batch...")
    df = pd.read_parquet(PROCESSED_DIR / "test_merged.parquet")

    # ------------------------------------------------------------
    # Load trained feature transformer
    # ------------------------------------------------------------
    print("Loading fitted feature transformer...")
    fe_engine = joblib.load(ARTIFACTS_DIR / "feature_transformer_v1.joblib")

    # ------------------------------------------------------------
    # Apply transformation (IMPORTANT: transform only)
    # ------------------------------------------------------------
    print("Applying transform (NO FIT)...")
    X_transformed = fe_engine.transform(df)

    # ------------------------------------------------------------
    # Ensure curated directory exists
    # ------------------------------------------------------------
    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Save transformed dataset
    # ------------------------------------------------------------
    output_path = CURATED_DIR / "test_batch_curated.parquet"
    X_transformed.to_parquet(output_path, index=False)

    print(f"Curated batch file saved to: {output_path}")

# ------------------------------------------------------------
# Script entry point
# Allows script to be executed from terminal or Airflow
# ------------------------------------------------------------
if __name__ == "__main__":
    main()