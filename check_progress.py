
import pandas as pd
import time

file_path = "data/raw/raw_data.csv"

def check_progress():
    try:
        df = pd.read_csv(file_path)
        total = len(df)
        with_surface = df['surface_m2'].notna().sum()
        with_desc = df['description'].notna().sum()
        # Count descriptions that look like garbage (start with "UTC" or contain "messages":{)
        garbage_desc = df['description'].apply(lambda x: 1 if isinstance(x, str) and ('"messages":{' in x or x.startswith('"UTC"')) else 0).sum()
        
        print(f"Total rows: {total}")
        print(f"Rows with surface_m2: {with_surface}")
        print(f"Rows with description: {with_desc}")
        print(f"Rows with garbage description: {garbage_desc}")
        
    except Exception as e:
        print(f"Error reading CSV: {e}")

if __name__ == "__main__":
    check_progress()
