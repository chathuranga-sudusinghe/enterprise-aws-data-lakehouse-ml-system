# ml/monitoring/model_metrics.py

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


def evaluate_model(y_true, y_pred, y_prob):

    metrics = {}

    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["precision"] = precision_score(y_true, y_pred)
    metrics["recall"] = recall_score(y_true, y_pred)
    metrics["f1_score"] = f1_score(y_true, y_pred)

    try:
        metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
    except:
        metrics["roc_auc"] = None

    return metrics