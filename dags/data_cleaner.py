import pandas as pd

class Cleaner:
    def data_cleaning(self,df):
        # df =pd.read_csv(file_path)
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.dropna(subset=['Channel Title', 'Channel Username', 'Message'])
        
        # Step 4: Standardize date formats
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 
        
        # Fill missing media paths with 'No Media'
        df['Media Path'] = df['Media Path'].fillna('No Media')
        
        # Reassigning ID
        df['ID'] = range(1, len(df) + 1)
        df.set_index('ID', inplace=True)
        
        return df
