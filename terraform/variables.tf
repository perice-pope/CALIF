variable "gcp_project_id" {
  description = "The GCP project ID to deploy resources into."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to deploy resources into."
  type        = string
  default     = "us-central1"
}

variable "repo_name" {
  description = "The name of the Artifact Registry repository."
  type        = string
  default     = "calif-services"
}

variable "slack_bot_token" {
  description = "The Slack bot token for notifications."
  type        = string
  sensitive   = true
}

variable "slack_channel" {
  description = "The Slack channel to post notifications to (e.g., #deals)."
  type        = string
  default     = "#general"
}

variable "browse_ai_api_key" {
  description = "The API key for Browse AI."
  type        = string
  sensitive   = true
}

variable "postgres_db_url" {
  description = "The connection URL for the PostgreSQL database."
  type        = string
  sensitive   = true
} 