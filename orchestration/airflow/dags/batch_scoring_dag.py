# orchestration/airflow/dags/batch_scoring_dag.py

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

# -------------------------------------------------------------------
# PROJECT ROOT (IMPORTANT)
# We assume Airflow runs inside repo root as mounted volume.
# If you run in Docker, you will mount repo to /opt/airflow/repo
# -------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3] # Docker mount path (recommended)
PYTHON_BIN = "python"  # optional venv inside container
# If you don't use venv inside airflow container, change to: PYTHON_BIN = "python"

# Your scripts (already created)
SCRIPT_PROCESS = REPO_ROOT / "lakehouse" / "transformations" / "process_test_batch.py"
SCRIPT_TRANSFORM = REPO_ROOT / "lakehouse" / "transformations" / "transform_test_batch.py"
SCRIPT_PREDICT = REPO_ROOT / "lakehouse" / "transformations" / "run_batch_prediction.py"

default_args = {
    "owner": "enterprise-ml",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="batch_scoring_dag",
    description="Enterprise batch scoring: process -> transform -> predict",
    default_args=default_args,
    start_date=datetime(2026, 3, 4),
    schedule="0 2 * * *",  # Daily at 02:00 AM
    catchup=False,
    max_active_runs=1,
    tags=["lakehouse", "batch", "scoring", "production"],
) as dag:

    start = EmptyOperator(task_id="start")

    # 1) external parquet -> processed/test_merged.parquet
    process_test_batch = BashOperator(
        task_id="process_test_batch",
        bash_command=f"{PYTHON_BIN} {SCRIPT_PROCESS}",
    )

    # 2) processed/test_merged.parquet -> curated/test_batch_curated.parquet
    transform_test_batch = BashOperator(
        task_id="transform_test_batch",
        bash_command=f"{PYTHON_BIN} {SCRIPT_TRANSFORM}",
    )

    # 3) curated/test_batch_curated.parquet -> curated/test_batch_predictions.parquet
    run_batch_prediction = BashOperator(
        task_id="run_batch_prediction",
        bash_command=f"{PYTHON_BIN} {SCRIPT_PREDICT}",
    )

    end = EmptyOperator(task_id="end")

    # Order (THIS is the orchestration)
    start >> process_test_batch >> transform_test_batch >> run_batch_prediction >> end