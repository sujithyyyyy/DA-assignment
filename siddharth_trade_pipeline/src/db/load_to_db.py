from sqlalchemy import create_engine, text
import pandas as pd
import os

def load_to_sqlite(df, db_name='trade_analysis.db', table_name='shipments'):
    """
    Loads the processed dataframe into a SQLite database.
    """
    print(f"Connecting to SQLite database: {db_name}...")
    
    # Create SQLite engine
    # echo=False prevents SQL query logging to console
    engine = create_engine(f'sqlite:///{db_name}', echo=False)
    
    print(f"Writing {len(df)} rows to table '{table_name}'...")
    
    # Write to SQL (Replace if exists)
    # index=False prevents writing the Pandas index as a column
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    
    print("Database load complete.")

# ==========================================
# EXECUTION BLOCK (Runs when you execute this file)
# ==========================================
if __name__ == "__main__":
    # 1. FIND THE INPUT FILE (to create dummy data for the DB)
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
        print(f"CRITICAL ERROR: File '{FILENAME}' not found. Cannot test DB load.")
    else:
        # 2. LOAD DATA
        print("--- Loading CSV for DB Test ---")
        try:
            df = pd.read_csv(FILE_PATH, encoding='utf-8')
        except:
            df = pd.read_csv(FILE_PATH, encoding='ISO-8859-1')
            
        # Standardize headers so they look nice in SQL
        df.columns = [c.strip().replace(' ', '_').upper() for c in df.columns]

        # 3. RUN THE FUNCTION
        DB_NAME = 'test_trade_analysis.db'
        load_to_sqlite(df, db_name=DB_NAME)
        
        # 4. VERIFY THE LOAD (Query the DB back)
        print("\n--- Verifying Data in Database ---")
        engine = create_engine(f'sqlite:///{DB_NAME}')
        with engine.connect() as conn:
            # Check row count
            result = conn.execute(text("SELECT COUNT(*) FROM shipments"))
            count = result.scalar()
            print(f"Verification: Found {count} rows in table 'shipments'.")
            
            # Show top 3 rows
            print("Top 3 rows from DB:")
            preview = pd.read_sql("SELECT * FROM shipments LIMIT 3", conn)
            print(preview)