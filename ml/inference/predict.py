import json
import joblib
import pandas as pd
from pathlib import Path


ARTIFACT_DIR = Path("model_artifacts")


class FraudPredictor:
    def __init__(self):
        self.model = joblib.load(ARTIFACT_DIR / "fraud_lgbm_v1.joblib")
        self.feature_engine = joblib.load(ARTIFACT_DIR / "feature_transformer_v1.joblib")

        with open(ARTIFACT_DIR / "threshold_v1.json") as f:
            self.threshold = json.load(f)["threshold"]

        with open(ARTIFACT_DIR / "feature_columns_v1.json") as f:
            self.feature_columns = json.load(f)

    def predict(self, input_df: pd.DataFrame) -> pd.DataFrame:
        # Apply feature engineering
        X = self.feature_engine.transform(input_df)

        # Align columns (safety)
        X = X[self.feature_columns]

        # Predict probability
        y_proba = self.model.predict_proba(X)[:, 1]

        # Apply threshold
        y_pred = (y_proba >= self.threshold).astype(int)

        # Return results
        result = input_df.copy()
        result["fraud_probability"] = y_proba
        result["fraud_prediction"] = y_pred

        return result