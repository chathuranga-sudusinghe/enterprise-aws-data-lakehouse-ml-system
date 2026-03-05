# ------------------------------------------------------------
# Batch Prediction Pipeline
#
# Purpose:
# Run fraud predictions on curated test batch data using
# the trained LightGBM model.
#
# Flow:
# Curated Data → Load Model → Predict Probabilities → Save Results
# ------------------------------------------------------------

from pathlib import Path
import pandas as pd
import joblib
from ml.utils.run_manifest import new_run_id, build_batch_manifest, write_manifest


# ------------------------------------------------------------
# Define important project directories
# ------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURATED_DIR = PROJECT_ROOT / "lakehouse" / "curated"
ARTIFACTS_DIR = PROJECT_ROOT / "model_artifacts"


def main():
    # ------------------------------------------------------------
    # Load curated batch dataset
    # ------------------------------------------------------------
    print("Loading curated batch data...")
    X = pd.read_parquet(CURATED_DIR / "test_batch_curated.parquet")

    # ------------------------------------------------------------
    # Load trained model
    # ------------------------------------------------------------
    print("Loading trained model...")
    model = joblib.load(ARTIFACTS_DIR / "fraud_lgbm_v1.joblib")

    # ------------------------------------------------------------
    # Generate fraud probability predictions
    # ------------------------------------------------------------
    print("Generating fraud probabilities...")
    probabilities = model.predict_proba(X)[:, 1]

    # ------------------------------------------------------------
    # Attach predictions to dataset
    # ------------------------------------------------------------
    results = X.copy()
    results["fraud_probability"] = probabilities

    # ------------------------------------------------------------
    # Save prediction results
    # ------------------------------------------------------------
    output_path = CURATED_DIR / "test_batch_predictions.parquet"
    results.to_parquet(output_path, index=False)

    print(f"Batch predictions saved to: {output_path}")


# ------------------------------------------------------------
# Script entry point
# Allows the script to run from terminal
# ------------------------------------------------------------
if __name__ == "__main__":

    # Run main batch prediction pipeline
    main()

    # ------------------------------------------------------------
    # RUN MANIFEST
    # Track this batch scoring run for reproducibility
    # ------------------------------------------------------------
    RUN_ID = new_run_id("batch")

    # Paths used in this batch run
    curated_path = CURATED_DIR / "test_batch_curated.parquet"
    predictions_path = CURATED_DIR / "test_batch_predictions.parquet"
    model_path = ARTIFACTS_DIR / "fraud_lgbm_v1.joblib"

    # Build batch run manifest
    manifest = build_batch_manifest(
        project_root=PROJECT_ROOT,
        run_id=RUN_ID,
        stage="batch_scoring",
        curated_parquet=curated_path,
        predictions_parquet=predictions_path,
        model_path=model_path,
    )

    # Save manifest file
    write_manifest(manifest, PROJECT_ROOT / "artifacts" / "runs" / RUN_ID)

    # Print run id for tracking
    print(f"[RUN_ID] {RUN_ID}")