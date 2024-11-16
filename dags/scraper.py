# /opt/airflow/dags/scraper.py
# import logging
import csv
import os
import json
from telethon import TelegramClient
from dotenv import load_dotenv
import asyncio
import pandas as pd

# # Set up logging
# logging.basicConfig(
#     filename='/opt/airflow/logs/scraping.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# Load environment variables
load_dotenv('/opt/airflow/dags/.env')
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('phone')

# Function to read channels from a JSON file
def load_channels_from_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('channels', []), data.get('comments', [])
    except Exception as e:
        # logging.error(f"Error reading channels from JSON: {e}")
        return [], []

# Function to scrape data from a single channel
async def scrape_channel(client, channel_username, writer, media_dir, num_messages):
    try:
        entity = await client.get_entity(channel_username)
        channel_title = entity.title

        message_count = 0
        async for message in client.iter_messages(entity):
            if message_count >= num_messages:
                break  # Stop after scraping the specified number of messages

            media_path = None
            if message.media:
                filename = f"{channel_username}_{message.id}.{message.media.document.mime_type.split('/')[-1]}" if hasattr(message.media, 'document') else f"{channel_username}_{message.id}.jpg"
                media_path = os.path.join(media_dir, filename)
                await client.download_media(message.media, media_path)
                # logging.info(f"Downloaded media for message ID {message.id}.")

            writer.writerow([channel_title, channel_username, message.id, message.message, message.date, media_path])
            # logging.info(f"Processed message ID {message.id} from {channel_username}.")

            message_count += 1

        # if message_count == 0:
        #     logging.info(f"No messages found for {channel_username}.")

    except Exception as e:
        # logging.error(f"Error while scraping {channel_username}: {e}")
        print(f"Error while scraping {channel_username}: {e}")

# Function to run the scraper, which will be executed by the PythonOperator
def scraper():
    client = TelegramClient('scraping_session', api_id, api_hash)
    
    try:
        asyncio.run(client.start(phone))
        # logging.info("Client started successfully.")
        
        media_dir = '/opt/airflow/dags/data/photos'
        os.makedirs(media_dir, exist_ok=True)

        channels, comments = load_channels_from_json('/opt/airflow/dags/data/channels.json')
        
        num_messages_to_scrape = 10
        
        for channel in channels:
            csv_filename = f"/opt/airflow/dags/data/{channel[1:]}_data.csv"
            with open(csv_filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Channel Title', 'Channel Username', 'ID', 'Message', 'Date', 'Media Path'])
                
                asyncio.run(scrape_channel(client, channel, writer, media_dir, num_messages_to_scrape))
                # logging.info(f"Scraped data from {channel}.")
                
                df = pd.read_csv(csv_filename)
                return df 

    except Exception as e:
        # logging.error(f"Error in main function: {e}")
        print(f"Error in main function: {e}")


# if __name__ == "__main__":
#     run_scraper()
