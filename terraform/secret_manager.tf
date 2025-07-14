# Slack Bot Token Secret
resource "google_secret_manager_secret" "slack_bot_token" {
  project   = var.gcp_project_id
  secret_id = "slack-bot-token"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "slack_bot_token_version" {
  secret      = google_secret_manager_secret.slack_bot_token.id
  secret_data = var.slack_bot_token
}

# Browse AI API Key Secret
resource "google_secret_manager_secret" "browse_ai_api_key" {
  project   = var.gcp_project_id
  secret_id = "browse-ai-api-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "browse_ai_api_key_version" {
  secret      = google_secret_manager_secret.browse_ai_api_key.id
  secret_data = var.browse_ai_api_key
}

# Postgres DB URL Secret
resource "google_secret_manager_secret" "postgres_db_url" {
  project   = var.gcp_project_id
  secret_id = "postgres-db-url"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "postgres_db_url_version" {
  secret      = google_secret_manager_secret.postgres_db_url.id
  secret_data = var.postgres_db_url
} 