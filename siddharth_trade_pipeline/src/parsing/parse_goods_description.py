import pandas as pd
import re
import os

def parse_description_row(text):
    """
    Parses a single description string to extract model, material, qty, price.
    """
    if pd.isna(text):
        return pd.Series([None, None, None, None])

    text = str(text).upper()
    
    # 1. Extract USD Price (Look for 'USD' followed by digits)
    usd_match = re.search(r'USD\s*[:\-\s]?\s*([\d\.]+)', text)
    usd_price = float(usd_match.group(1)) if usd_match else None

    # 2. Extract Embedded Quantity (Look for 'QTY' followed by digits)
    qty_match = re.search(r'QTY\s*[:\-\s]?\s*([\d]+)', text)
    embedded_qty = float(qty_match.group(1)) if qty_match else None

    # 3. Extract Material (Keyword search)
    material = "UNKNOWN"
    if "STEEL" in text: material = "STEEL"
    elif "GLASS" in text: material = "GLASS"
    elif "PLASTIC" in text: material = "PLASTIC"
    elif "WOOD" in text: material = "WOODEN"

    # 4. Extract Model (First alphanumeric token heuristic)
    tokens = text.split()
    model = tokens[0] if tokens else "UNKNOWN"

    return pd.Series([model, material, embedded_qty, usd_price])

def run_parsing_logic(df, description_col='GOODS_DESCRIPTION'):
    """
    Applies parsing logic to the dataframe.
    """
    print("Parsing text descriptions (this may take a moment)...")
    extracted = df[description_col].apply(parse_description_row)
    extracted.columns = ['EXTRACTED_MODEL', 'EXTRACTED_MATERIAL', 'EMBEDDED_QTY', 'EXTRACTED_USD_PRICE']
    
    return pd.concat([df, extracted], axis=1)

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
        # 2. LOAD DATA
        print(f"Loading data from {FILE_PATH}...")
        try:
            df = pd.read_csv(FILE_PATH, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
            
        # Standardize headers (Required because the function looks for 'GOODS_DESCRIPTION')
        df.columns = [c.strip().replace(' ', '_').upper() for c in df.columns]

        # 3. RUN THE FUNCTION
        df_parsed = run_parsing_logic(df)
        
        # 4. SHOW THE OUTPUT
        print("\n--- Output Preview (Extracted Columns) ---")
        cols_to_show = ['GOODS_DESCRIPTION', 'EXTRACTED_USD_PRICE', 'EMBEDDED_QTY', 'EXTRACTED_MATERIAL']
        print(df_parsed[cols_to_show].head())
        print(f"\nTotal Rows Processed: {len(df_parsed)}")