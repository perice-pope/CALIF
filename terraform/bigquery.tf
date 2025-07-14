resource "google_bigquery_dataset" "raw_data" {
  project    = var.gcp_project_id
  dataset_id = "calif_raw"
  location   = var.gcp_region
  description = "Raw data ingested from various sources for the CALIF project."

  delete_contents_on_destroy = false # Be cautious with production data
}

resource "google_bigquery_table" "listings" {
  project    = var.gcp_project_id
  dataset_id = google_bigquery_dataset.raw_data.dataset_id
  table_id   = "listings"

  # Define partitioning and clustering for query performance and cost optimization
  time_partitioning {
    type  = "DAY"
    field = "ingestion_timestamp"
  }

  clustering = ["asset_type"]

  schema = <<EOF
[
  {
    "name": "asset_type",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "The type of asset (e.g., 'watch', 'wine', 'private_jet')."
  },
  {
    "name": "source_api",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "The source API the data was pulled from."
  },
  {
    "name": "ingestion_timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "The timestamp when the data was ingested."
  },
  {
    "name": "raw_data",
    "type": "JSON",
    "mode": "NULLABLE",
    "description": "The raw JSON payload from the source API."
  }
]
EOF
} 