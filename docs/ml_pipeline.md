# Machine Learning Pipeline

## Overview

The ML pipeline is responsible for training, evaluating, and serving the fraud detection model.

The pipeline transforms curated transaction data into predictions using a production-ready machine learning workflow.

---

## Pipeline Stages

### 1. Feature Engineering

Feature engineering transforms raw transaction attributes into predictive variables.

Examples include:

- behavioral features
- frequency-based features
- transaction statistics

The feature engineering module is implemented in:

---

### 2. Model Training

The training pipeline builds the fraud detection model using the engineered features.

Primary model:

- LightGBM

Training script:

---

### 3. Model Evaluation

Model performance is evaluated using validation datasets.

Typical metrics include:

- ROC-AUC
- Recall
- Precision

Evaluation logic is implemented in:

---

### 4. Batch Inference

Batch inference generates predictions for datasets using the trained model.

Implemented in:

---

## Model Artifacts

Trained models and outputs are stored in:

Examples:

- trained model files
- run metadata
- prediction outputs

---

## Pipeline Orchestration

The ML pipeline can be executed through automated workflows using orchestration tools such as:

- Apache Airflow

This enables scheduled model training and inference.