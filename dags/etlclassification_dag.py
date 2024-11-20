from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
# from airflow.operators.python import PythonOperator
from airflow.decorators import task
from airflow.utils.dates import days_ago
import requests
import json
import os
import pandas as pd
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
# from ultralytics import YOLO

# Load credentials from environment variables or .env file
load_dotenv()

channel_username = "@lobelia4cosmetics" 
POSTGRES_CONN_ID='postgres_default'

    
def scrape_telegram_channel(channel_username: str):
    # Define the time range: last 24 hours (making it timezone-aware)
    time_threshold = datetime.now(pytz.utc) - timedelta(days=1)
    
    # Load credentials from environment variables
    api_id = os.getenv('TG_API_ID')  # Your API ID from Telegram
    api_hash = os.getenv('TG_API_HASH')  # Your API hash from Telegram
    session_name = os.getenv('SESSION_NAME')

    # Initialize Telegram client
    client = TelegramClient('session_name', api_id, api_hash)
    # client = TelegramClient(session_name, api_id, api_hash)

    async def fetch_posts():
        # Start the client session and handle authentication
        await client.start()  # No phone number needed if the session is saved
        
        # Fetch messages from the channel within the last 24 hours
        messages = await client.get_messages(channel_username, limit=100)

        # Prepare a list to store scraped data
        scraped_data = []
        
        for message in messages:
            # Check if the message was sent within the last 24 hours
            if message.date > time_threshold:
                message_data = {
                    'channelname': channel_username,
                    'message': message.text or "",  # Get message text, if available
                    'photo_path': None,  # Initialize with None, in case no photo
                    'date': message.date.strftime('%d-%m-%Y')
                }

                # If the message contains a photo, download it
                if isinstance(message.media, MessageMediaPhoto):
                    # Ensure the directory exists for saving images
                    os.makedirs("downloaded_photos", exist_ok=True)
                    photo = await message.download_media(file="downloaded_photos/") 
                    message_data['photo_path'] = os.path.abspath(photo)  # Store the absolute path
                
                scraped_data.append(message_data)

        # Create a DataFrame from the scraped data
        df = pd.DataFrame(scraped_data)
        
        # Optionally, save the DataFrame to a JSON file
        df.to_json(f'{channel_username}_scraped_data.json', index=False)
        
        return df

    # Run the client and fetch posts from the specified channel
    with client:
        df = client.loop.run_until_complete(fetch_posts())
    
    return df[:5]


# def classify_products(img_path):
#     model=YOLO("../models/last_n_e_50.pt")

#     results=model(img_path)
#     def get_category_name(results):
#         # Access the top1 index and names mapping
#         custom_names = ['Cosmetics', 'Nutritional Product', 'Pharmaceutical Product', 'Health Supplement']
#         results[0].names = {i: name for i, name in enumerate(custom_names)}
#         top1_index = results[0].probs.top1
#         names_mapping = results[0].names
#         # Get the category name
#         category_name = names_mapping[top1_index]
#         return category_name

#     category=get_category_name(results)
    
#     return category

# Define the DAG
# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }
default_args={
    'owner':'airflow',
    'start_date':days_ago(1)
}

with DAG(dag_id='product_etl_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dags:
    
    @task()
    def scrape_telegram_data(channel_username: str):
        """Scrape messages from a Telegram channel."""
        return scrape_telegram_channel(channel_username)
    
    @task()
    def transform_scrapped_data(scraped_data):
        """Transform the extracted weather data."""
        # Add a 'product_name' column to the DataFrame
        scraped_data['product_name'] = scraped_data['message'].str.split('\n').str[0]
        # Apply the classify function to the 'image_path' column
        # scraped_data['category'] = scraped_data['photo_path'].apply(classify_products)

        # Create the transformed data dictionary
        transformed_data = {
            'date': scraped_data['date'].tolist(),
            'channelname': scraped_data['channelname'].tolist(),
            'product_name': scraped_data['product_name'].tolist(),
            'image_path': scraped_data['photo_path'].tolist(),
            # 'category': scraped_data['category'].tolist()
        }
        return transformed_data
    
    @task()
    def load_transformed_data(transformed_data):
        """Load transformed data into PostgreSQL."""
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_data (
            date VARCHAR(255),
            channelname VARCHAR(255),
            product_name VARCHAR(255),
            image_path VARCHAR(255),
            category VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Insert transformed data into the table
        cursor.execute("""
        INSERT INTO product_data (date, channelname, product_name, image_path, category)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            transformed_data['date'],
            transformed_data['channelname'],
            transformed_data['product_name'],
            transformed_data['image_path'],
            transformed_data['category']
        ))

        conn.commit()
        cursor.close()
        
    scraped_data=scrape_telegram_data(channel_username)
    transformed_data=transform_scrapped_data(scraped_data)
    load_transformed_data(transformed_data)
    
