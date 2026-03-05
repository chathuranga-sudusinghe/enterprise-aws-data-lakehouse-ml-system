import pandas as pd
from ml.training.train_lgbm import train_lightgbm


def test_training_pipeline():

    # Minimal dataset that satisfies FeatureEngineeringEngine
    X_train = pd.DataFrame({
        "TransactionDT": [1, 2, 3, 4],
        "TransactionAmt": [100, 200, 150, 180],
        "card1": [1111, 2222, 3333, 4444],
        "card2": [100, 100, 200, 200],
        "card3": [150, 150, 150, 150],
        "card4": ["visa", "visa", "mastercard", "visa"],
        "addr1": [10, 20, 10, 30]
    })

    y_train = pd.Series([0, 1, 0, 1])

    # simple validation dataset
    X_val = X_train.copy()
    y_val = y_train.copy()

    model, preds = train_lightgbm(
        X_train,
        y_train,
        X_val,
        y_val,
        categorical_cols=["card4"]
    )

    assert model is not None
    assert len(preds) == len(X_val)