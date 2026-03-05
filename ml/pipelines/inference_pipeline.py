"""
Enterprise Inference Pipeline
-----------------------------
Handles artifact loading, schema-safe transformation,
and prediction workflow.
"""

"""
Enterprise Inference Pipeline

Handles artifact loading, schema-safe transformation,
and prediction workflow.
"""

import os
import json
import logging
import joblib
import pandas as pd

ARTIFACT_DIR = "model_artifacts"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_artifacts():
    """
    Load trained model, feature transformer, and threshold.
    """

    model_path = os.path.join(ARTIFACT_DIR, "fraud_lgbm_v1.joblib")
    transformer_path = os.path.join(ARTIFACT_DIR, "feature_transformer_v1.joblib")
    threshold_path = os.path.join(ARTIFACT_DIR, "threshold_v1.json")

    for path in [model_path, transformer_path, threshold_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing artifact: {path}")

    logger.info("Loading model artifacts...")

    model = joblib.load(model_path)
    transformer = joblib.load(transformer_path)

    with open(threshold_path, "r") as f:
        threshold = json.load(f)["threshold"]

    logger.info("Artifacts loaded successfully.")

    return model, transformer, threshold        #  -------->  # inside the same file, inside predict().

def predict(data: pd.DataFrame) -> pd.DataFrame:
    """
    Full enterprise inference workflow.
    """

    try:
        if data.empty:
            raise ValueError("Input data is empty.")

        model, transformer, threshold = load_artifacts()

        logger.info("Applying feature transformation...")
        data_transformed = transformer.transform(data)

        logger.info("Generating probability predictions...")
        proba = model.predict_proba(data_transformed)[:, 1]

        if proba.ndim != 1:
            raise ValueError("Unexpected probability output shape.")

        logger.info("Applying optimal threshold...")
        prediction = (proba >= threshold).astype(int)

        result = pd.DataFrame(
            {
                "probability": proba,
                "prediction": prediction,
            },
            index=data.index,
        )

        logger.info("Inference completed successfully.")
        return result

    except Exception as e:
        logger.exception("Inference failed.")
        raise

        #It returns to:
        #  The code that calls predict()
        #  Usually an API endpoint or a testing script