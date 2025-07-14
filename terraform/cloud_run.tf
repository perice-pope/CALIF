resource "google_cloud_run_v2_service" "api" {
  project  = var.gcp_project_id
  name     = "calif-api"
  location = var.gcp_region

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "us-central1-docker.pkg.dev/${var.gcp_project_id}/${var.repo_name}/api:latest"
      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.gcp_project_id
      }
      
      env {
        name = "POSTGRES_DB_URL"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.postgres_db_url.secret_id
            version = "latest"
          }
        }
      }
    }

    service_account = google_service_account.calif_runtime.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # Allow public access to the API
  iam_bindings {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
} 