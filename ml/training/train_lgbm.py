"""
LightGBM Training Module

Handles model initialization, validation checks, 
training with early stopping, and probability output.
"""

from typing import List, Tuple
import pandas as pd
from lightgbm import LGBMClassifier
from lightgbm import early_stopping, log_evaluation
import logging


def train_lightgbm(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    categorical_cols: List[str],
) -> Tuple[LGBMClassifier, pd.Series]:
    """
    Train LightGBM model and return trained model + validation probabilities.
    """

    # --- DEBUG: Input validation ---
    # Ensure no empty datasets and matching shapes
    if X_train.empty or X_val.empty:
        raise ValueError("Training or validation feature set is empty.")

    if len(X_train) != len(y_train):
        raise ValueError("X_train and y_train size mismatch.")

    if len(X_val) != len(y_val):
        raise ValueError("X_val and y_val size mismatch.")   

    # model initialization starts here
    model = LGBMClassifier(
        objective="binary",
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=64,
        random_state=42,
        n_jobs=-1,
    )

    # --- DEBUG: Validate categorical feature integrity ---
    # Ensures categorical columns exist and are correct dtype
    if categorical_cols:
         missing_cols = [col for col in categorical_cols if col not in X_train.columns]
    if missing_cols:
        raise ValueError(f"Categorical columns missing in training data: {missing_cols}")

    # Ensure correct dtype
    if categorical_cols:
       for col in categorical_cols:
         if X_train[col].dtype.name != "category":
            X_train[col] = X_train[col].astype("category")
            X_val[col] = X_val[col].astype("category")
    
    # --- Train model with validation monitoring ---
    # Uses early stopping (50 rounds) and silent logging
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="auc",
        categorical_feature=categorical_cols,
        callbacks=[
            early_stopping(50),
            log_evaluation(0)
        ],
    )

    # --- DEBUG: Training summary ---
    # --- Training summary ---
    best_auc = model.best_score_["valid_0"]["auc"]
   
    logger = logging.getLogger(__name__)

    logger.info(f"Best iteration: {model.best_iteration_}")
    logger.info(f"Best validation AUC: {best_auc}")

    # --- Predict validation probabilities ---
    # Ensures binary classification output shape
    proba = model.predict_proba(X_val)

    if proba.shape[1] != 2:
        raise ValueError("Model did not return binary class probabilities.")

    y_prob = proba[:, 1]

    # Return trained model and validation probabilities
    # return to ml/pipelines/training_pipeline.py --> model, y_prob = train_lightgbm(...)
    return model, y_prob

