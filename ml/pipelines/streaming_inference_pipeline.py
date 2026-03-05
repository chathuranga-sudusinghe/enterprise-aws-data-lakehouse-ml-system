# ml/pipelines/streaming_inference_pipeline.py

from pathlib import Path
import pandas as pd
import joblib


ARTIFACTS_DIR = Path("model_artifacts")


class StreamingFraudScorer:

    def __init__(self):
        print("Loading feature transformer...")
        self.fe_engine = joblib.load(
            ARTIFACTS_DIR / "feature_transformer_v1.joblib"
        )

        print("Loading trained model...")
        self.model = joblib.load(
            ARTIFACTS_DIR / "fraud_lgbm_v1.joblib"
        )

    def score_transaction(self, transaction_dict: dict) -> float:
        # Convert single record to DataFrame
        df = pd.DataFrame([transaction_dict])

        # Transform (NO FIT)
        X_transformed = self.fe_engine.transform(df)

        # Predict probability
        probability = self.model.predict_proba(X_transformed)[:, 1][0]

        return float(probability)


def main():
    # Example simulated streaming event
    sample_transaction = {
        "TransactionID": 999999,
        "TransactionDT": 86400,
        "TransactionAmt": 120.5,
        "card1": 1000,
        "card2": 111,
        "card3": 150,
        "card4": "visa",
        "addr1": 325
    }

    scorer = StreamingFraudScorer()

    probability = scorer.score_transaction(sample_transaction)

    print(f"Fraud probability: {probability}")


if __name__ == "__main__":
    main()