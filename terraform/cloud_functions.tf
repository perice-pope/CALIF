# Cloud Function for the Analytics service
resource "google_cloudfunctions2_function" "analytics" {
  project  = var.gcp_project_id
  name     = "calif-analytics"
  location = var.gcp_region

  build_config {
    runtime     = "python311"
    entry_point = "process_signals" # The function name in calculate_signals.py
    source {
      storage_source {
        # This will be populated by Cloud Build
        # For local apply, you'd need to upload the source to a GCS bucket
        bucket = "" # To be configured in CI/CD
        object = "" # To be configured in CI/CD
      }
    }
  }

  service_config {
    max_instance_count = 3
    min_instance_count = 0
    available_memory   = "256Mi"
    timeout_seconds    = 300
    service_account_email = google_service_account.calif_runtime.email
    environment_variables = {
      GCP_PROJECT_ID   = var.gcp_project_id
      BIGQUERY_DATASET = "calif_raw"
      BIGQUERY_TABLE   = "listings"
    }
    secret_environment_variables {
      key          = "POSTGRES_DB_URL"
      project_id   = var.gcp_project_id
      secret       = google_secret_manager_secret.postgres_db_url.secret_id
      version      = "latest"
    }
  }
}

# Cloud Function for the Slack Bot service
resource "google_cloudfunctions2_function" "slack_bot" {
  project  = var.gcp_project_id
  name     = "calif-slack-bot"
  location = var.gcp_region

  build_config {
    runtime     = "python311"
    entry_point = "notify_slack" # The function name in notify.py
    source {
      storage_source {
        bucket = "" # To be configured in CI/CD
        object = "" # To be configured in CI/CD
      }
    }
  }

  service_config {
    max_instance_count    = 2
    min_instance_count    = 0
    available_memory      = "256Mi"
    timeout_seconds       = 60
    service_account_email = google_service_account.calif_runtime.email
    # The slack bot function needs the slack token and channel
    secret_environment_variables {
      key        = "SLACK_BOT_TOKEN"
      project_id = var.gcp_project_id
      secret     = google_secret_manager_secret.slack_bot_token.secret_id
      version    = "latest"
    }
    environment_variables = {
      SLACK_CHANNEL = var.slack_channel
    }
    # Allow unauthenticated access for Pub/Sub push, but we use OIDC for security
    ingress_settings = "ALLOW_ALL"
  }
} 