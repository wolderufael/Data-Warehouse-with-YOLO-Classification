import pandas as pd
import os
import pandas as pd
import glob
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from ultralytics import YOLO

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from .env file
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')



class Classification:
    def classify_products(self,image_folder):
        # Initialize an empty list to store all detection results for each image
        all_clasification = []

        # Loop through the images in the folder and process the detection results
        for img_name in os.listdir(image_folder):
            img_path = os.path.join(image_folder, img_name)

            # Run object detection
            model=YOLO("models/last_n_e_50.pt")

            results=model(img_path)
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


            # Append a single row of data for this image (lists of detections)
            all_clasification.append({
                'image_name': img_name,
                'product_category': category
            })

        # Convert the list of dictionaries to a DataFrame
        df_all_detections = pd.DataFrame(all_clasification)

        # Save the DataFrame to a single CSV file
        df_all_detections.to_csv('data/classification_result.csv', index=False)

        print("All dete saved to 'all_classification_results.csv'.")
        
        
    def add_dataframe_to_table(self, df, table_name, if_exists='replace'):
        try:
            # Create SQLAlchemy engine for database connection
            engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

            # Use pandas to_sql to add DataFrame to the database
            df.to_sql(table_name, engine, index=False, if_exists=if_exists)

            print(f"DataFrame successfully added to table '{table_name}' in the database.")

        except Exception as error:
            print("Error while inserting DataFrame to PostgreSQL", error)

        finally:
            if engine:
                engine.dispose()
                print("SQLAlchemy engine is disposed.")
