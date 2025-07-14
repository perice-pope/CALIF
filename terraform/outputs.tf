output "api_service_url" {
  description = "The URL of the deployed API service on Cloud Run."
  value       = google_cloud_run_v2_service.api.uri
}

output "analytics_function_uri" {
  description = "The URI of the analytics Cloud Function."
  value       = google_cloudfunctions2_function.analytics.uri
}

output "slack_bot_function_uri" {
  description = "The URI of the slack_bot Cloud Function."
  value       = google_cloudfunctions2_function.slack_bot.uri
}

output "pubsub_topic_name" {
  description = "The name of the Pub/Sub topic for new signals."
  value       = google_pubsub_topic.signals_new.name
}

output "artifact_registry_repo" {
  description = "The URI of the Artifact Registry Docker repository."
  value       = google_artifact_registry_repository.main.id
} 