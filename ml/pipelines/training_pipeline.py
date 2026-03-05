"""
Training Pipeline
-----------------
Orchestrates full model training workflow.
"""
"""  
# def format 

def run_training_pipeline(...):
    Feature engineering
    Model training
    Threshold optimization
    Evaluation
    Save artifacts
    return metrics

def call  

"""

import joblib
import json
import os

import pandas as pd

from ml.training.feature_engineering import FraudFeatureEngineeringEngine
from ml.training.train_lgbm import train_lightgbm
from ml.training.evaluate import evaluate_model
from ml.utils.threshold import find_optimal_threshold
from pathlib import Path
from ml.utils.run_manifest import new_run_id, build_training_manifest, write_manifest

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

ARTIFACT_DIR = "model_artifacts"

def run_training_pipeline(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
) -> dict:
    """
    Full training workflow.
    """

    # --------------------------
    # 1️⃣ Feature Engineering
    # --------------------------
    transformer = FraudFeatureEngineeringEngine()
    X_train, X_val = transformer.fit_transform(X_train, X_val)

    # --------------------------
    # 2️⃣ Model Training
    # --------------------------

    model, y_prob = train_lightgbm(    # "return model, y_prob" From ml\training\train_lgbm.py 
        X_train,
        y_train,
        X_val,
        y_val,
        categorical_cols=transformer.categorical_cols,
    )

    # --------------------------
    # 3️⃣ Threshold Optimization
    # --------------------------
    optimal_threshold = find_optimal_threshold(   # "return thresholds[best_idx]" from ml\utils\threshold.py
        y_true=y_val.to_numpy(),
        y_proba=y_prob,
        target_recall=0.95,
    )

    # --------------------------
    # 4️⃣ Evaluation (Evaluate model using optimal threshold)
    # --------------------------
    metrics = evaluate_model(     # "return {"roc_auc": roc_auc, "accuracy": accuracy, ......}" from ml/training/evaluate.py
        y_true=y_val,
        y_proba=pd.Series(y_prob, index=y_val.index),
        threshold=optimal_threshold,
)
    # --------------------------
    # 5️⃣ Save Artifacts
    # --------------------------
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    joblib.dump(model, os.path.join(ARTIFACT_DIR, "fraud_lgbm_v1.joblib"))
    joblib.dump(transformer, os.path.join(ARTIFACT_DIR, "feature_transformer_v1.joblib"))
    
    metadata = {
        "best_iteration": model.best_iteration_,
        "optimal_threshold": optimal_threshold,
        "n_features": X_train.shape[1],
    }

    with open(os.path.join(ARTIFACT_DIR, "metadata_v1.json"), "w") as f:
        json.dump(metadata, f)

    feature_columns = list(X_train.columns)

    with open(os.path.join(ARTIFACT_DIR, "feature_columns_v1.json"), "w") as f:
        json.dump(feature_columns, f)

    with open(os.path.join(ARTIFACT_DIR, "threshold_v1.json"), "w") as f:
        json.dump({"threshold": optimal_threshold}, f)

    return metrics #-------------------------------------------------------->#
                                                                             #
# =====================                                                      
# ENTRY POINT                                                                #
# =====================                                                      
                                                                             #
if __name__ == "__main__":                                                   
                                                                             #
    import pandas as pd                                      

    logger.info("Starting training pipeline execution...")                   #

    # Load pre-split datasets                                                
    X_train = pd.read_parquet("lakehouse/splits/X_train.parquet")            #
    X_val = pd.read_parquet("lakehouse/splits/X_val.parquet")                     
    y_train = pd.read_parquet("lakehouse/splits/y_train.parquet").squeeze()  #
    y_val = pd.read_parquet("lakehouse/splits/y_val.parquet").squeeze()
                                                                             #
    metrics = run_training_pipeline(       #<------------------------------- #
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
    )

    logger.info("Training completed successfully.")
    logger.info(f"Final metrics: {metrics}")


     # --- RUN MANIFEST (training) ---
    
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    RUN_ID = new_run_id("training")

    # Inputs/outputs you actually have in THIS script
    train_parquet_path = PROJECT_ROOT / "lakehouse" / "splits" / "X_train.parquet" 

    # outputs produced by this script
    model_path = Path(ARTIFACT_DIR) / "fraud_lgbm_v1.joblib"

    manifest = build_training_manifest(
        project_root=PROJECT_ROOT,
        run_id=RUN_ID,
        stage="training",
        train_parquet=train_parquet_path,
        model_path=model_path,
        metrics=metrics,    # output from evaluate_model(...)
        extra_outputs={
            "transformer_path": str(Path(ARTIFACT_DIR) / "feature_transformer_v1.joblib"),
            "metadata_path": str(Path(ARTIFACT_DIR) / "metadata_v1.json"),
            "threshold_path": str(Path(ARTIFACT_DIR) / "threshold_v1.json"),
            "feature_columns_path": str(Path(ARTIFACT_DIR) / "feature_columns_v1.json"),

            # record split inputs too (repro)
            "x_train_parquet": str(PROJECT_ROOT / "lakehouse" / "splits" / "X_train.parquet"),
            "x_val_parquet": str(PROJECT_ROOT / "lakehouse" / "splits" / "X_val.parquet"),
            "y_train_parquet": str(PROJECT_ROOT / "lakehouse" / "splits" / "y_train.parquet"),
            "y_val_parquet": str(PROJECT_ROOT / "lakehouse" / "splits" / "y_val.parquet"),
        },
    )

    write_manifest(manifest, PROJECT_ROOT / "artifacts" / "runs" / RUN_ID)
    print(f"[RUN_ID] {RUN_ID}")

