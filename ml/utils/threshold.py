import numpy as np
from sklearn.metrics import precision_recall_curve


def find_optimal_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_recall: float = 0.95,
) -> float:
    """
    Find optimal classification threshold under a recall constraint.

    Strategy:
        1. Compute precision-recall curve.
        2. Filter thresholds where recall >= target_recall.
        3. Among them, choose threshold with highest precision.

    Raises:
        ValueError: If no threshold satisfies recall constraint.
    """

    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)

    # Align arrays (thresholds is shorter by 1)
    precision = precision[:-1]
    recall = recall[:-1]

    valid_idx = np.where(recall >= target_recall)[0]

    if len(valid_idx) == 0:
        raise ValueError(
            f"No threshold satisfies target recall >= {target_recall}"
        )

    best_idx = valid_idx[np.argmax(precision[valid_idx])]

    return thresholds[best_idx]