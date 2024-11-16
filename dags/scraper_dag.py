from airflow import DAG
from datetime import timedelta, datetime
import json
from airflow.operators.python import PythonOperator
# from scraper import run_scraper
import subprocess


# Function to run the scraper script and push the file path to XCom
def run_scraper(**kwargs):
    result = subprocess.run(
        ["python", "G:\\Programming\\10_Academy\\Week_12\\Medical Data Ware house with object detection\\script\\telegram_scraper.py"],
        capture_output=True,
        text=True,
        check=True
    )
    file_path = result.stdout.strip()  # Extract the file path from the script output
    print(f"Scraper output file path: {file_path}")
    kwargs['ti'].xcom_push(key='scraper_output', value=file_path)  # Push to XCom


# Function to run the cleaner script with the file path from XCom
def run_cleaner(**kwargs):
    ti = kwargs['ti']
    file_path = ti.xcom_pull(key='scraper_output', task_ids='run_scraper')  # Pull file path from XCom

    if not file_path:
        raise ValueError("File path not found in XCom.")

    subprocess.run(
        ["python", "G:\\Programming\\10_Academy\\Week_12\\Medical Data Ware house with object detection\\script\\data_cleaner.py", file_path],
        check=True
    )
    print(f"Cleaner processed file: {file_path}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 16),
    'email': [],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

with DAG('etl_scraper',
        default_args=default_args,
        schedule_interval = '@daily',
        catchup=False) as dag:
    
        scraper_task = PythonOperator(
        task_id='run_scraper',
        python_callable=run_scraper,
        provide_context=True,
    )
        cleaning_task = PythonOperator(
        task_id='run_cleaner',
        python_callable=run_scraper,
        provide_context=True,
    )

# Set task dependencies
scraper_task >> cleaning_task