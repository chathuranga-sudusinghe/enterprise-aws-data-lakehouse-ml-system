import os
import json
import joblib
import logging
from datetime import datetime

import lightgbm as lgb
from sklearn.metrics import roc_auc_score

from ml.utils.threshold import find_optimal_threshold


ARTIFACT_DIR = "model_artifacts"


def train_lgbm(
    X_train,
    y_train,
    X_val,
    y_val,
    target_recall=0.95,
    model_params=None,
):
    """
    Train LightGBM model and save artifacts.
    """

    try:
        if model_params is None:
            model_params = {
                "n_estimators": 300,
                "max_depth": 8,
                "min_samples_leaf": 50,
                "class_weight": "balanced",
                "random_state": 42,
            }

        model = lgb.LGBMClassifier(**model_params)
        model.fit(X_train, y_train)

        y_val_prob = model.predict_proba(X_val)[:, 1]

        roc_auc = roc_auc_score(y_val, y_val_prob)

        threshold = find_optimal_threshold(
            y_true=y_val,
            y_prob=y_val_prob,
            target_recall=target_recall,
        )

        save_artifacts(model, threshold, X_train.columns.tolist())

        return {
            "roc_auc": roc_auc,
            "threshold": threshold,
            "model_params": model_params,
        }

    except Exception as e:
        logging.exception("Training failed.")
        raise e


def save_artifacts(model, threshold, feature_columns):
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    model_path = os.path.join(ARTIFACT_DIR, f"fraud_lgbm_{timestamp}.pkl")
    threshold_path = os.path.join(ARTIFACT_DIR, f"threshold_{timestamp}.json")
    feature_path = os.path.join(ARTIFACT_DIR, f"feature_columns_{timestamp}.json")

    joblib.dump(model, model_path)

    with open(threshold_path, "w") as f:
        json.dump({"threshold": threshold}, f)

    with open(feature_path, "w") as f:
        json.dump({"features": feature_columns}, f)