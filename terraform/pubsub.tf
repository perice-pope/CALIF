# Pub/Sub topic for new signals
resource "google_pubsub_topic" "signals_new" {
  project = var.gcp_project_id
  name    = "signals.new"
}

# Push subscription to the Slack Bot Cloud Function
resource "google_pubsub_subscription" "slack_notifier" {
  project = var.gcp_project_id
  name    = "slack-notifier-push"
  topic   = google_pubsub_topic.signals_new.name

  ack_deadline_seconds = 60

  push_config {
    push_endpoint = google_cloudfunctions2_function.slack_bot.uri

    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
    }
  }

  depends_on = [
    google_cloudfunctions2_function.slack_bot
  ]
} 