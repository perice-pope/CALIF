import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from google.cloud import bigquery
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

# --- Configuration ---
BROWSE_AI_API_KEY = os.getenv("BROWSE_AI_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = "calif_raw"
BIGQUERY_TABLE = "listings"

# --- Pydantic Models for Data Validation ---

class Asset(BaseModel):
    asset_type: str
    source_api: str
    ingestion_timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Dict[str, Any]

class WatchAsset(Asset):
    asset_type: str = "watch"
    source_api: str = "watchcharts"

class WineAsset(Asset):
    asset_type: str = "wine"
    source_api: str = "liv-ex"

class JetAsset(Asset):
    asset_type: str = "private_jet"
    source_api: str = "charter_api"

# --- Browse AI API Interaction ---

def get_latest_browse_ai_runs(api_key: str, robot_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the latest successful run from a Browse AI robot.
    """
    url = f"https://api.browse.ai/v2/robots/{robot_id}/tasks/latest"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Browse AI for robot {robot_id}: {e}")
        return None

# --- Data Streaming to BigQuery ---

def stream_to_bigquery(project_id: str, dataset: str, table: str, rows: List[Dict[str, Any]]):
    """
    Streams data into a BigQuery table.
    """
    if not rows:
        print("No rows to stream. Skipping.")
        return

    client = bigquery.Client(project=project_id)
    table_ref = client.dataset(dataset).table(table)

    try:
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            print(f"Encountered errors while inserting rows: {errors}")
        else:
            print(f"Successfully streamed {len(rows)} rows to {dataset}.{table}")
    except Exception as e:
        print(f"An error occurred during BigQuery streaming: {e}")

# --- Main Ingestion Logic ---

def main():
    """
    Main function to orchestrate data ingestion.
    """
    print("Starting CALIF data ingestion...")

    if not BROWSE_AI_API_KEY or not GCP_PROJECT_ID:
        raise ValueError("API keys and GCP Project ID must be set in .env file.")

    # These would be the actual robot IDs for your Browse AI setup
    source_map = {
        "watchcharts_robot_id": ("watch", WatchAsset),
        "liv_ex_robot_id": ("wine", WineAsset),
        "charterapi_robot_id": ("jet", JetAsset),
    }

    all_assets_to_stream = []

    for robot_id_str, (asset_type, asset_model) in source_map.items():
        robot_id = os.getenv(robot_id_str.upper())
        if not robot_id:
            print(f"Skipping {asset_type}: {robot_id_str.upper()} not found in .env")
            continue

        print(f"Fetching data for asset type: {asset_type}...")
        run_data = get_latest_browse_ai_runs(BROWSE_AI_API_KEY, robot_id)

        if run_data and run_data.get("successful") and "capturedLists" in run_data.get("result", {}):
            items = run_data["result"]["capturedLists"].get("default", [])
            print(f"Found {len(items)} items for {asset_type}.")

            for item in items:
                try:
                    asset = asset_model(raw_data=item)
                    all_assets_to_stream.append(asset.model_dump(mode="json"))
                except ValidationError as e:
                    print(f"Validation error for an item of type {asset_type}: {e}")
        else:
            print(f"No successful run or no data found for {asset_type}.")

    if all_assets_to_stream:
        stream_to_bigquery(
            project_id=GCP_PROJECT_ID,
            dataset=BIGQUERY_DATASET,
            table=BIGQUERY_TABLE,
            rows=all_assets_to_stream
        )
    else:
        print("No new data to stream to BigQuery.")

    print("CALIF data ingestion finished.")

if __name__ == "__main__":
    main()
