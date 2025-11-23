import pandas as pd
import numpy as np
import os

def calculate_landed_cost(df):
    """
    Calculates Grand Total and Unit Costs.
    """
    print("Calculating Landed Costs...")
    
    # Ensure columns are numeric before calculation (Safety check)
    for col in ['TOTAL_VALUE_INR', 'DUTY_PAID_INR', 'QUANTITY']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Grand Total = Value + Duty
    df['GRAND_TOTAL_INR'] = df['TOTAL_VALUE_INR'] + df['DUTY_PAID_INR']
    
    # Landed Cost Per Unit (Avoid division by zero)
    df['LANDED_COST_PER_UNIT'] = np.where(
        df['QUANTITY'] > 0,
        df['GRAND_TOTAL_INR'] / df['QUANTITY'],
        0
    )
    return df

def assign_categories(df, desc_col='GOODS_DESCRIPTION'):
    """
    Assigns Categories and Sub-Categories based on keywords.
    """
    print("Assigning Categories...")
    
    def get_category_logic(row):
        text = str(row[desc_col]).upper()
        # Category Logic
        category = "GENERAL"
        if "CUTLERY" in text or "SPOON" in text or "FORK" in text:
            category = "KITCHENWARE"
        elif "SCRUBBER" in text or "CLEANING" in text:
            category = "CLEANING"
        elif "GLASS" in text:
            category = "GLASSWARE"
            
        # Sub-Category Logic
        sub_category = "STANDARD"
        if category == "GLASSWARE":
            if "BOROSILICATE" in text: sub_category = "BOROSILICATE"
            elif "OPAL" in text: sub_category = "OPALWARE"
            
        return pd.Series([category, sub_category])

    cats = df.apply(get_category_logic, axis=1)
    cats.columns = ['CATEGORY', 'SUB_CATEGORY']
    
    return pd.concat([df, cats], axis=1)

def enrich_supplier_info(df):
    """
    Ensures SUPPLIER_NAME column exists. 
    If missing (common in sample data), creates synthetic supplier names.
    """
    print("Enriching Supplier Info...")
    
    # Check if column exists (it might be named differently in raw data)
    if 'SUPPLIER_NAME' not in df.columns:
        print("WARNING: 'SUPPLIER_NAME' missing in raw data. Generating synthetic suppliers for demo.")
        
        # IMPROVED LOGIC: 
        # Instead of using HS_CODE (which often ends in 0), we use the Description length/content
        # to distribute suppliers into 5 distinct groups (Group-1 to Group-5).
        def generate_supplier(row):
            # Combine Description and HS Code to make a seed
            text_seed = str(row.get('GOODS_DESCRIPTION', '')) + str(row.get('HS_CODE', ''))
            
            # Simple hash logic: Sum of character codes modulo 5
            # This is deterministic (same product always gets same supplier)
            seed_val = sum(ord(c) for c in text_seed if c.isalnum())
            group_id = (seed_val % 5) + 1 
            
            return f"Global Supplier Group-{group_id}"

        df['SUPPLIER_NAME'] = df.apply(generate_supplier, axis=1)
        
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
        # 2. LOAD DATA
        print(f"Loading data from {FILE_PATH}...")
        try:
            df = pd.read_csv(FILE_PATH, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
            
        # Standardize headers 
        df.columns = [c.strip().replace(' ', '_').upper() for c in df.columns]

        # 3. RUN THE FUNCTIONS
        df_engineered = calculate_landed_cost(df)
        df_engineered = assign_categories(df_engineered)
        df_engineered = enrich_supplier_info(df_engineered) # <--- NEW STEP
        
        # 4. SHOW THE OUTPUT
        print("\n--- Output Preview (Calculated Features) ---")
        cols_to_show = ['GOODS_DESCRIPTION', 'SUPPLIER_NAME', 'CATEGORY']
        print(df_engineered[cols_to_show].head())
        print(f"\nTotal Rows Processed: {len(df_engineered)}")