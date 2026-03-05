import numpy as np
from sklearn.metrics import precision_recall_curve


def find_optimal_threshold(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    target_recall: float = 0.95,
) -> float:
    """
    Find optimal classification threshold under a recall constraint.

    Strategy:
        1. Compute precision-recall curve.
        2. Filter thresholds where recall >= target_recall.
        3. Among them, choose threshold with highest precision.

    Raises:
        ValueError: If inputs are invalid or no threshold satisfies constraint.
    """

    # --- DEBUG: Input validation ---
    # Ensure non-empty arrays
    if y_true.size == 0 or y_proba.size == 0:
        raise ValueError("y_true or y_prob is empty.")

    # Ensure matching lengths
    if y_true.shape[0] != y_proba.shape[0]:
        raise ValueError("y_true and y_prob size mismatch.")

    # Ensure binary classification problem
    if np.unique(y_true).size < 2:
        raise ValueError("Cannot compute precision-recall curve with only one class.")

    # Ensure valid recall range
    if not 0 <= target_recall <= 1:
        raise ValueError("target_recall must be between 0 and 1.")

    # --- Compute precision-recall curve ---
    # Note: thresholds array length = len(precision) - 1
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)

    # Ensure thresholds exist
    if thresholds.size == 0:
        raise ValueError("No thresholds returned from precision_recall_curve.")

    # Align arrays (thresholds shorter by 1 compared to precision/recall)
    precision = precision[:-1]
    recall = recall[:-1]     # thresholds already length n-1, matching trimmed precision/recall

    # --- Filter thresholds satisfying recall constraint ---
    valid_idx = np.flatnonzero(recall >= target_recall)

    if valid_idx.size == 0:
        raise ValueError(
            f"No threshold satisfies target_recall >= {target_recall}"
        )

    # --- Select threshold with highest precision among valid candidates ---
    valid_precisions = precision[valid_idx]

    # Replace NaN precision values with 0 (worst case precision)
    valid_precisions = np.nan_to_num(valid_precisions, nan=0.0)

    best_relative_idx = np.argmax(valid_precisions)
    best_idx = valid_idx[best_relative_idx]

    # Return optimal threshold
    # return to ml/pipelines/training_pipeline.py ---> optimal_threshold = find_optimal_threshold(...)
    return thresholds[best_idx]
