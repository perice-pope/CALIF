import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
from google.cloud import bigquery
from dotenv import load_dotenv
import functions_framework
from flask import Request, jsonify

load_dotenv()

# --- Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = "calif_raw"
BIGQUERY_TABLE = "listings"
POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL") # e.g. postgresql+psycopg2://user:pass@host/dbname

# --- Database Connection ---
def get_db_engine():
    """Initializes and returns a SQLAlchemy engine."""
    if not POSTGRES_DB_URL:
        raise ValueError("POSTGRES_DB_URL must be set in the environment.")
    return create_engine(POSTGRES_DB_URL)

# --- Data Loading ---
def load_data_from_bigquery(project_id: str, dataset: str, table: str) -> pd.DataFrame:
    """Loads the last 35 days of data from BigQuery for signal calculation."""
    client = bigquery.Client(project=project_id)
    query = f"""
    SELECT
        asset_type,
        ingestion_timestamp,
        -- Note: This assumes a 'price' field exists within the nested raw_data JSON.
        -- This will need to be adjusted based on the actual schema of your data.
        JSON_EXTRACT_SCALAR(raw_data, '$.price') AS price
    FROM
        `{project_id}.{dataset}.{table}`
    WHERE
        ingestion_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 35 DAY)
        AND JSON_EXTRACT_SCALAR(raw_data, '$.price') IS NOT NULL
    """
    print("Loading data from BigQuery...")
    df = client.query(query).to_dataframe()
    print(f"Loaded {len(df)} rows.")

    # Data cleaning and type conversion
    df['ingestion_timestamp'] = pd.to_datetime(df['ingestion_timestamp'])
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)
    df.sort_values(by=['asset_type', 'ingestion_timestamp'], inplace=True)
    return df

# --- Signal Calculation ---
def calculate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates rolling metrics and generates signals."""
    if df.empty:
        return pd.DataFrame()

    print("Calculating signals...")
    df['rolling_mean_30d'] = df.groupby('asset_type')['price'].transform(
        lambda x: x.rolling(window=30, min_periods=5).mean()
    )
    df['rolling_std_30d'] = df.groupby('asset_type')['price'].transform(
        lambda x: x.rolling(window=30, min_periods=5).std()
    )
    df['z_score'] = (df['price'] - df['rolling_mean_30d']) / df['rolling_std_30d']

    # Generate signals
    df['discount_signal'] = df['price'] <= (df['rolling_mean_30d'] * 0.9)
    df['z_score_signal'] = df['z_score'] <= -2.0
    df['is_deal'] = df['discount_signal'] | df['z_score_signal']

    # Get the latest record for each asset type to represent the current signal
    latest_signals = df.loc[df.groupby('asset_type')['ingestion_timestamp'].idxmax()]
    print(f"Generated signals for {len(latest_signals)} asset types.")
    return latest_signals

# --- Data Upsert to Postgres ---
def upsert_signals_to_postgres(signals_df: pd.DataFrame, engine):
    """Upserts the calculated signals into the Postgres 'signals' table."""
    if signals_df.empty:
        print("No signals to upsert.")
        return

    table_name = "signals"
    print(f"Upserting {len(signals_df)} signals to Postgres table '{table_name}'...")

    # For simplicity, we'll do a row-by-row upsert.
    # For performance, a bulk upsert method would be better.
    with engine.connect() as connection:
        for _, row in signals_df.iterrows():
            stmt = text(f"""
                INSERT INTO {table_name} (asset_type, last_price, rolling_mean_30d, z_score, is_deal, updated_at)
                VALUES (:asset_type, :price, :rolling_mean_30d, :z_score, :is_deal, NOW())
                ON CONFLICT (asset_type) DO UPDATE SET
                    last_price = EXCLUDED.last_price,
                    rolling_mean_30d = EXCLUDED.rolling_mean_30d,
                    z_score = EXCLUDED.z_score,
                    is_deal = EXCLUDED.is_deal,
                    updated_at = NOW();
            """)
            connection.execute(stmt, parameters=row.to_dict())
        connection.commit()
    print("Upsert complete.")


# --- Cloud Function Entrypoint ---
@functions_framework.http
def process_signals(request: Request):
    """
    HTTP-triggered Cloud Function to run the signal calculation pipeline.
    """
    try:
        if not GCP_PROJECT_ID:
            raise ValueError("GCP_PROJECT_ID must be set.")

        # 1. Load Data
        raw_data_df = load_data_from_bigquery(GCP_PROJECT_ID, BIGQUERY_DATASET, BIGQUERY_TABLE)

        # 2. Calculate Signals
        signals_df = calculate_signals(raw_data_df)

        # 3. Upsert to Postgres
        if not signals_df.empty:
            db_engine = get_db_engine()
            upsert_signals_to_postgres(signals_df, db_engine)
            return jsonify({"status": "success", "signals_processed": len(signals_df)}), 200
        else:
            return jsonify({"status": "success", "message": "No new signals processed"}), 200

    except ValueError as ve:
        print(f"Configuration error: {ve}")
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500

# To run locally for testing:
if __name__ == '__main__':
    # This block will not run in the Cloud Function environment
    print("Running locally for testing purposes...")
    # You would need to have BigQuery and Postgres credentials set up locally.
    # e.g., using `gcloud auth application-default login`
    # and having a .env file with POSTGRES_DB_URL
    process_signals(Request(environ={"REQUEST_METHOD": "POST"})) 