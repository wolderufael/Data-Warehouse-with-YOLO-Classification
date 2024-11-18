from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

# Define a simple Python function for the task
def print_hello():
    print("Hello, Airflow!")

# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 18),  # You can set this to your preferred start date
    'retries': 1,
}

# Instantiate the DAG
with DAG(
    dag_id='test_hello_world_dag',
    default_args=default_args,
    schedule_interval=None,  # Set to None for manual trigger
    catchup=False,           # Don't run past DAG runs on schedule
) as dag:

    # Define the task
    hello_task = PythonOperator(
        task_id='print_hello_task',
        python_callable=print_hello,  # This points to the print_hello function
    )

# To run the task, trigger the DAG manually
