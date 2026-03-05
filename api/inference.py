import json
import joblib
import pandas as pd
from pathlib import Path

# ----------------------------------
# Load Artifacts
# ----------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = PROJECT_ROOT / "model_artifacts"

MODEL_VERSION = "v1"

model = joblib.load(ARTIFACT_DIR / f"fraud_lgbm_{MODEL_VERSION}.pkl")

with open(ARTIFACT_DIR / f"threshold_{MODEL_VERSION}.json") as f:
    threshold = json.load(f)["threshold"]

with open(ARTIFACT_DIR / f"feature_columns_{MODEL_VERSION}.json") as f:
    feature_columns = json.load(f)

# ----------------------------------
# Preprocessing
# ----------------------------------
def apply_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype("category")
    return df

# ----------------------------------
# Prediction Function
# ----------------------------------
def predict(input_dict: dict) -> dict:
    df = pd.DataFrame([input_dict])

    # Ensure feature order
    df = df[feature_columns]

    # Apply preprocessing
    df = apply_preprocessing(df)

    # Predict
    prob = model.predict_proba(df)[:, 1][0]
    prediction = int(prob >= threshold)

    return {
        "fraud_probability": float(prob),
        "prediction": prediction
    }