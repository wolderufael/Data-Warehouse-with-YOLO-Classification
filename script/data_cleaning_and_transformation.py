import pandas as pd
import glob
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from .env file
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

class Transformer:
    def clean_and_load_to_db(self,file_path,table_name):
        # Load all the CSV file and concatenate them
        file_path = f"{file_path}/*.csv"
        all_files = glob.glob(file_path)
        dfs = []
        # Loop through the file list and read each file
        for file in all_files:
            df = pd.read_csv(file)
            dfs.append(df)
            
        # Concatenate all DataFrames
        df_combined = pd.concat(dfs, ignore_index=True)

            
        # try:
        #     df = pd.read_csv(csv_file_path)
        # except FileNotFoundError:
        #     print(f"File {csv_file_path} not found!")
        #     return None
        
        # Remove duplicate rows
        df_combined = df_combined.drop_duplicates()
        
        # Handle missing values
        df_combined = df_combined.dropna(subset=['Channel Title', 'Channel Username', 'Message'])
        
        # Step 4: Standardize date formats
        df_combined['Date'] = pd.to_datetime(df_combined['Date'], errors='coerce') 
        
        # Fill missing media paths with 'No Media'
        df_combined['Media Path'] = df_combined['Media Path'].fillna('No Media')
        
        # Reassigning ID
        df_combined['ID'] = range(1, len(df_combined) + 1)
        df_combined.set_index('ID', inplace=True)
   
        # Load data frame to database
        engine = None 
        
        try:
            # Create SQLAlchemy engine for database connection
            engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

            # Use pandas to_sql to add DataFrame to the database
            df_combined.to_sql(table_name, engine, index=False, if_exists='replace')

            print(f"DataFrame successfully added to table '{table_name}' in the database.")

        except Exception as error:
            print("Error while inserting DataFrame to PostgreSQL", error)

        finally:
            if engine is not None:
                engine.dispose()
                print("SQLAlchemy engine is disposed.")

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