from airflow import DAG
from datetime import timedelta, datetime
import json
import pandas as pd
from airflow.operators.python import PythonOperator
# from scraper import run_scraper
# import subprocess
import scraper
from data_cleaner import Cleaner

def run_scrap():
    # scraper.scraper()
    print("hello")


def scrape_task(**kwargs):
    # Run the scraping logic and return the result
    df = scraper.scraper()  # Scrape the data
    # Push the DataFrame to XCom for downstream tasks
    kwargs['ti'].xcom_push(key='scraped_data', value=df.to_json())

def clean_task(**kwargs):
    # Retrieve the scraped data from XCom
    ti = kwargs['ti']
    scraped_data_json = ti.xcom_pull(task_ids='scrape_task', key='scraped_data')
    
    # Convert JSON back to DataFrame
    df = pd.read_json(scraped_data_json)
    
    # Perform the cleaning using the Cleaner class
    cleaner = Cleaner()
    cleaned_data = cleaner.data_cleaning(df)
    
    # You can return or save the cleaned data as needed
    print(cleaned_data.head())  # For demonstration




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
        python_callable=scrape_task,
        provide_context=True,
    )
        cleaning_task = PythonOperator(
        task_id='run_cleaner',
        python_callable=clean_task,
        provide_context=True,
    )

# Set task dependencies
scraper_task >> cleaning_task