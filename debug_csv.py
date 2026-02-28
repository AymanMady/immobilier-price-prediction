
import pandas as pd
try:
    df = pd.read_csv("data/raw/raw_data.csv")
    print("Columns:", df.columns.tolist())
    print("First 5 surfaces:", df['surface_m2'].head().tolist())
    print("Total Rows:", len(df))
except Exception as e:
    print(f"Error: {e}")
