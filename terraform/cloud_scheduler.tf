resource "google_cloud_scheduler_job" "ingest_trigger" {
  project   = var.gcp_project_id
  name      = "calif-nightly-ingest-trigger"
  schedule  = "0 2 * * *" # Run at 2:00 AM UTC every day
  time_zone = "Etc/UTC"
  
  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions2_function.analytics.uri
    
    oidc_token {
      service_account_email = google_service_account.calif_runtime.email
    }
  }
} 