output "service_url" {
  description = "Public URL of the deployed Maestro router"
  value       = google_cloud_run_v2_service.maestro_router.uri
}

output "service_name" {
  value = google_cloud_run_v2_service.maestro_router.name
}

output "latest_ready_revision" {
  value = google_cloud_run_v2_service.maestro_router.latest_ready_revision
}
