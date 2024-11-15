from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def run_scraper():
    import subprocess
    subprocess.run(["python", "G:\Programming\10_Academy\Week_12\Medical Data Ware house with object detection\script\telegram_scraper.py"])

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='etl_scraper',
    default_args=default_args,
    description='Run scraper daily at 7 AM',
    schedule_interval='0 7 * * *',
    start_date=datetime(2024, 11, 16),
    catchup=False,
) as dag:
    scraper_task = PythonOperator(
        task_id='run_scraper',
        python_callable=run_scraper,
    )
