# Service account for Cloud Run and Cloud Functions
resource "google_service_account" "calif_runtime" {
  project      = var.gcp_project_id
  account_id   = "calif-runtime-sa"
  display_name = "CALIF Service Runtime Account"
}

# Grant BigQuery User role to the service account for reading data
resource "google_project_iam_member" "bigquery_user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.calif_runtime.email}"
}

# Grant BigQuery Data Editor role for writing data (if any service needs it)
resource "google_project_iam_member" "bigquery_data_editor" {
  project = var.gcp_project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.calif_runtime.email}"
}

# Grant Secret Manager Secret Assessor role to access secrets
resource "google_project_iam_member" "secret_assessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.calif_runtime.email}"
}

# Service account for the Pub/Sub push subscription to authenticate
resource "google_service_account" "pubsub_invoker" {
  project      = var.gcp_project_id
  account_id   = "calif-pubsub-invoker-sa"
  display_name = "CALIF PubSub Invoker SA"
}

# Grant the invoker SA permission to invoke the Slack Bot Cloud Function
resource "google_cloud_run_service_iam_member" "slack_bot_invoker" {
  project  = google_cloudfunctions2_function.slack_bot.project
  location = google_cloudfunctions2_function.slack_bot.location
  service  = google_cloudfunctions2_function.slack_bot.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.pubsub_invoker.email}"
} 