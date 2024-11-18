# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime
# import os

# default_args = {
#     "owner": "airflow",
#     "depends_on_past": False,
#     "retries": 1,
# }

# def connect_to_telegram(**kwargs):
#     from telethon.sync import TelegramClient

#     api_id = os.environ.get("TELEGRAM_API_ID")
#     api_hash = os.environ.get("TELEGRAM_API_HASH")

#     with TelegramClient("session_name", api_id, api_hash) as client:
#         me = client.get_me()
#         if me:
#             print("Connection successful!")
#             return True
#         else:
#             print("Connection failed.")
#             return False

# with DAG(
#     dag_id="telegram_api_connect",
#     default_args=default_args,
#     start_date=datetime(2024, 1, 1),
#     schedule_interval="@daily",
#     catchup=False,
# ) as dag:
#     connect_task = PythonOperator(
#         task_id="connect_to_telegram",
#         python_callable=connect_to_telegram,
#     )

#     connect_task
