# orchestration/dags/retrain_pipeline.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

import subprocess


# -------------------------------
# Tasks
# -------------------------------

def check_data():
    print("Checking new data availability...")


def run_drift_detection():
    print("Running data drift detection...")
    subprocess.run(["python", "ml/monitoring/data_drift.py"], check=True)


def retrain_model():
    print("Retraining model...")
    subprocess.run(
        ["python", "ml/pipelines/training_pipeline.py"],
        check=True
    )


def evaluate_model():
    print("Evaluating retrained model...")
    subprocess.run(
        ["python", "ml/monitoring/model_metrics.py"],
        check=True
    )


def register_model():
    print("Registering new model version...")
    subprocess.run(
        ["python", "ml/registry/register_model.py"],
        check=True
    )


# -------------------------------
# DAG configuration
# -------------------------------

default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    dag_id="fraud_model_retraining_pipeline",
    default_args=default_args,
    description="Automated ML model retraining pipeline",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
)


# -------------------------------
# Define tasks
# -------------------------------

task_check_data = PythonOperator(
    task_id="check_data",
    python_callable=check_data,
    dag=dag,
)

task_drift = PythonOperator(
    task_id="drift_detection",
    python_callable=run_drift_detection,
    dag=dag,
)

task_retrain = PythonOperator(
    task_id="retrain_model",
    python_callable=retrain_model,
    dag=dag,
)

task_evaluate = PythonOperator(
    task_id="evaluate_model",
    python_callable=evaluate_model,
    dag=dag,
)

task_register = PythonOperator(
    task_id="register_model",
    python_callable=register_model,
    dag=dag,
)


# -------------------------------
# Pipeline order
# -------------------------------

task_check_data >> task_drift >> task_retrain >> task_evaluate >> task_register