from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def say_hello() -> None:
    print("Hello World!")


with DAG(
    dag_id="hello_world",
    description="Simple hello world example",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    PythonOperator(
        task_id="print_hello",
        python_callable=say_hello,
    )
