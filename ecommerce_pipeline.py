"""
E-commerce ELT Pipeline DAG
Orchestrates: ingestion → Snowflake load → dbt run → dbt test
Schedule: Daily at 02:00 UTC
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.dates import days_ago

from ingestion.extract_olist import ingest_olist_data

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="ecommerce_elt_pipeline",
    default_args=default_args,
    description="End-to-end ELT pipeline for Olist e-commerce data",
    schedule_interval="0 2 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["ecommerce", "elt", "dbt"],
) as dag:

    # ── 1. Ingest raw data ──────────────────────────────────────────────────
    ingest_raw = PythonOperator(
        task_id="ingest_raw_data",
        python_callable=ingest_olist_data,
        op_kwargs={"execution_date": "{{ ds }}"},
    )

    # ── 2. Load raw CSVs into Snowflake RAW schema ─────────────────────────
    load_to_snowflake = SnowflakeOperator(
        task_id="load_raw_to_snowflake",
        snowflake_conn_id="snowflake_default",
        sql="sql/load_raw_tables.sql",
    )

    # ── 3. dbt run — staging + marts ───────────────────────────────────────
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt run --profiles-dir /opt/airflow/dbt --target prod"
        ),
    )

    # ── 4. dbt test ────────────────────────────────────────────────────────
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt test --profiles-dir /opt/airflow/dbt --target prod"
        ),
    )

    # ── 5. Generate dbt docs ───────────────────────────────────────────────
    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            "cd /opt/airflow/dbt && "
            "dbt docs generate --profiles-dir /opt/airflow/dbt --target prod"
        ),
    )

    # ── DAG Dependencies ───────────────────────────────────────────────────
    ingest_raw >> load_to_snowflake >> dbt_run >> dbt_test >> dbt_docs
