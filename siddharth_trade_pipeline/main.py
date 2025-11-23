import os
import pandas as pd
from src.cleaning import clean_base
from src.parsing import parse_goods_description
from src.feature_engineering import features
from src.db import load_to_db

# ==========================================
# CONFIGURATION
# ==========================================
# 1. INPUT: Correct filename with the .xlsx part
FILENAME = 'Siddharth_Associates_sample data 2 - Sheet1.csv'

# 2. OUTPUT: Where the clean file will be saved
OUTPUT_CSV = 'processed_trade_data.csv'

def main():
    print("=== STARTING PIPELINE ===")
    
    # ---------------------------------------------------------
    # STEP 0: FIND THE RAW FILE (Robust Path Checking)
    # ---------------------------------------------------------
    path_options = [
        f'siddharth_trade_pipeline/data/raw/{FILENAME}',
        f'data/raw/{FILENAME}',
        FILENAME,
        f'../data/raw/{FILENAME}'
    ]
    
    raw_file_path = None
    for path in path_options:
        if os.path.exists(path):
            raw_file_path = path
            break
            
    if not raw_file_path:
        print(f"CRITICAL ERROR: Could not find input file '{FILENAME}'")
        return

    print(f"Input Data Found: {raw_file_path}")

    # ---------------------------------------------------------
    # STEP 1: CLEANING
    # ---------------------------------------------------------
    print("\n--- Phase 1: Cleaning ---")
    df = clean_base.load_and_clean_raw_data(raw_file_path)
    df = clean_base.standardize_units(df)
    
    # ---------------------------------------------------------
    # STEP 2: PARSING TEXT (REGEX)
    # ---------------------------------------------------------
    print("\n--- Phase 2: Parsing ---")
    df = parse_goods_description.run_parsing_logic(df)
    
    # ---------------------------------------------------------
    # STEP 3: FEATURE ENGINEERING
    # ---------------------------------------------------------
    print("\n--- Phase 3: Engineering ---")
    df = features.calculate_landed_cost(df)
    df = features.assign_categories(df)
    
    # FIX: Add missing Supplier Info (Synthetic generation if missing)
    df = features.enrich_supplier_info(df)
    
    # ---------------------------------------------------------
    # STEP 4: SAVE INTERMEDIATE CSV
    # ---------------------------------------------------------
    print(f"\n--- Phase 4: Saving CSV to {OUTPUT_CSV} ---")
    df.to_csv(OUTPUT_CSV, index=False)
    
    # ---------------------------------------------------------
    # STEP 5: LOAD TO DATABASE
    # ---------------------------------------------------------
    print("\n--- Phase 5: Loading to SQLite ---")
    load_to_db.load_to_sqlite(df)
    
    print("\n=== PIPELINE FINISHED SUCCESSFULLY ===")
    print(f"You can now refresh Power BI with '{OUTPUT_CSV}'")

if __name__ == "__main__":
    main()