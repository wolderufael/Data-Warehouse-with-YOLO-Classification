import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from dotenv import load_dotenv
import cv2
import numpy as np
from ultralytics import YOLO


# Load environment variables once
load_dotenv('.env')
telegram_bot_token = os.getenv('TOKEN4')

# Initialize the Application
app = Application.builder().token(telegram_bot_token).build()

# Introductory statement for the bot when the /start command is invoked
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello there. This is a fine-tuned YOLOv8 model for classifying Products in to four catagory i.e *Pharmaceutical*, *Cosmetic*, *Health Supplement* and *Nutritional*. Please Provide clear photo of product for better result!",parse_mode="Markdown"
    )
    
    
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Download the photo
    photo_file = await update.message.photo[-1].get_file()
    # photo_path = await photo_file.download_to_drive()

    # # Load image with OpenCV
    # Download the image as a byte array
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Convert the byte array to a NumPy array for OpenCV
    image_np = np.frombuffer(photo_bytes, np.uint8)
    
    # Decode the image using OpenCV
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    model=YOLO("../models/last.pt")

    results=model(img)
    def get_category_name(results):
        # Access the top1 index and names mapping
        custom_names = ['Cosmetics', 'Nutritional Product', 'Pharmaceutical Product', 'Health Supplement']
        results[0].names = {i: name for i, name in enumerate(custom_names)}
        top1_index = results[0].probs.top1
        names_mapping = results[0].names
        # Get the category name
        category_name = names_mapping[top1_index]
        return category_name

    category=get_category_name(results)
    
    await update.message.reply_text(f"Category: {category}")
    
# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Photo handler

# Run the webhook for the bot
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get('PORT', 5001)),
    url_path=telegram_bot_token,
    webhook_url=f'https://dictionary-bot-pbld.onrender.com/{telegram_bot_token}'
)

# # Start the bot
# app.run_polling()