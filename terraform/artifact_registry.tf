resource "google_artifact_registry_repository" "main" {
  project       = var.gcp_project_id
  location      = var.gcp_region
  repository_id = var.repo_name
  description   = "Docker repository for CALIF services"
  format        = "DOCKER"
} 