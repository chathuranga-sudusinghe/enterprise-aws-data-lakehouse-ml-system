"""
Evaluation Module
-----------------
Handles validation metrics calculation.
"""
from typing import Dict, Union
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def evaluate_model(
    y_true: pd.Series,
    y_proba: pd.Series,
    threshold: float,
) -> Dict[str, Union[float, int]]:
    
    """
    Evaluate model performance using given threshold.
    """
      
    # --- DEBUG: Input validation ---
    # Ensure valid inputs before metric calculation
    if len(y_true) == 0 or len(y_proba) == 0:
        raise ValueError("y_true or y_proba is empty.")

    if len(y_true) != len(y_proba):
        raise ValueError("y_true and y_proba size mismatch.")

    # --- DEBUG: Validate threshold range --- 
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1.")

    # Compute core evaluation metrics aligned with notebook baseline
    # Convert probabilities to binary predictions
    y_pred = (y_proba >= threshold).astype(int)

    # --- Compute ROC-AUC safely ---
    if y_true.nunique() < 2:
        raise ValueError("ROC-AUC cannot be computed with only one class in y_true.")
    
    # Core metrics
    roc_auc = roc_auc_score(y_true, y_proba)
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    if cm.shape != (2, 2):
        raise ValueError("Confusion matrix is not binary 2x2.")
    
    # Extract confusion matrix components (tn, fp, fn, tp)
    tn, fp, fn, tp = cm.ravel()

    # --- Additional monitoring metrics ---
    if len(y_true) == 0:
        raise ValueError("Cannot compute alert_rate on empty dataset.")

    alert_rate = (tp + fp) / len(y_true)

    # Return metrics dictionary for pipeline orchestration layer
    # return to ml/pipelines/training_pipeline.py --> metrics = evaluate_model(..)
    return {
        "roc_auc": roc_auc,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "threshold": threshold,
        "alert_rate": alert_rate,
    }