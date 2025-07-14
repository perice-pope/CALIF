# This file is intentionally left blank as a placeholder.
#
# For production environments, it is highly recommended to configure a VPC
# and use VPC connectors for Cloud Run and Cloud Functions to ensure
# secure and private communication with other GCP services like a
# private Cloud SQL instance.
#
# Example of a VPC Connector:
#
# resource "google_vpc_access_connector" "main" {
#   project        = var.gcp_project_id
#   name           = "calif-connector"
#   region         = var.gcp_region
#   ip_cidr_range  = "10.8.0.0/28"
#   network        = "default" # Or your custom VPC
# }
#
# You would then reference this connector in your Cloud Run and Cloud Function
# resources within the `service_config` block:
#
# service_config {
#   ...
#   vpc_connector = google_vpc_access_connector.main.id
#   vpc_connector_egress_settings = "ALL_TRAFFIC"
#   ...
# } 