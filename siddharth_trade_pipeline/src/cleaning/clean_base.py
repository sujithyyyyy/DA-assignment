import pandas as pd
import numpy as np
import os

def load_and_clean_raw_data(file_path):
    """
    Loads raw data, standardizes headers, and handles basic type conversions.
    """
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        
    # Standardize Column Headers: Strip spaces, Upper case, Replace space with underscore
    df.columns = [c.strip().replace(' ', '_').upper() for c in df.columns]
    
    # Date Conversion
    # Attempt to convert date. If errors, coercion will set them to NaT
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df['YEAR'] = df['DATE'].dt.year
        df['MONTH'] = df['DATE'].dt.month
    
    # Numeric Cleanup
    cols_to_numeric = ['TOTAL_VALUE_INR', 'DUTY_PAID_INR', 'QUANTITY']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

def standardize_units(df, unit_col='UNIT'):
    """
    Normalizes unit strings (e.g., 'NOS', 'PCS' -> 'PCS').
    """
    print("Standardizing units...")
    unit_map = {
        'PCS': 'PCS', 'PIECES': 'PCS', 'NOS': 'PCS', 'NO': 'PCS', 'NUMBERS': 'PCS',
        'KGS': 'KGS', 'KG': 'KGS', 'KILOGRAMS': 'KGS',
        'MTR': 'MTR', 'METER': 'MTR',
        'SETS': 'SETS', 'SET': 'SETS'
    }
    
    # Create normalized column
    df['STD_UNIT'] = df[unit_col].str.upper().str.strip().map(unit_map).fillna('OTHER')
    return df

# ==========================================
# EXECUTION BLOCK (Runs when you execute this file)
# ==========================================
if __name__ == "__main__":
    # 1. FIND THE FILE (Robust path checking)
    FILENAME = 'Siddharth_Associates_sample data 2 - Sheet1.csv'
    PATHS_TO_CHECK = [
        f'siddharth_trade_pipeline/data/raw/{FILENAME}',
        FILENAME,
        f'../data/raw/{FILENAME}'
    ]

    FILE_PATH = None
    for path in PATHS_TO_CHECK:
        if os.path.exists(path):
            FILE_PATH = path
            break
            
    if not FILE_PATH:
        print(f"CRITICAL ERROR: File '{FILENAME}' not found in paths: {PATHS_TO_CHECK}")
    else:
        # 2. CALL THE FUNCTIONS
        print("--- Executing Cleaning Logic ---")
        df_clean = load_and_clean_raw_data(FILE_PATH)
        df_clean = standardize_units(df_clean)
        
        # 3. SHOW THE OUTPUT
        print("\n--- Output Preview ---")
        print(df_clean[['GOODS_DESCRIPTION', 'STD_UNIT', 'TOTAL_VALUE_INR']].head())
        print(f"\nTotal Rows Processed: {len(df_clean)}")