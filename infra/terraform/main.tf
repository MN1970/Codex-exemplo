provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# Cloud Run service — default deployment target (simpler ops than GKE).
# Use infra/k8s/*.yaml on GKE only if sidecars or persistent connections
# are required (see docs/TRAINING-GUIDE-DEVOPS-DATA-TEAMS.md §1.3).
# ---------------------------------------------------------------------------
resource "google_cloud_run_v2_service" "maestro_router" {
  name     = "maestro-router-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    max_instance_request_concurrency = var.concurrency

    containers {
      image = var.image

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        cpu_idle = true   # scale CPU to zero between requests on non-min instances
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "MODEL_TIER_DEFAULT"
        value = "haiku"
      }
      env {
        name = "ANTHROPIC_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.anthropic_api_key_secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "SUPABASE_SERVICE_ROLE_KEY"
        value_source {
          secret_key_ref {
            secret  = var.supabase_service_role_key_secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health/ready"
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 30
      }

      liveness_probe {
        http_get {
          path = "/health/live"
        }
        period_seconds = 20
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,   # image is promoted via CI (canary tags), not Terraform
      traffic,                            # traffic splits managed by deploy-maestro.yml during canary
    ]
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.environment == "staging" ? 0 : 1 # production sits behind API gateway/auth; staging can be open to team VPN
  name     = google_cloud_run_v2_service.maestro_router.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ---------------------------------------------------------------------------
# Monitoring — alert policies mirroring infra/k8s/prometheus-rules.yaml,
# for the Cloud Run deployment path.
# ---------------------------------------------------------------------------
resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "Maestro (${var.environment}) — P95 latency > 500ms"
  combiner     = "OR"
  conditions {
    display_name = "Cloud Run request latency p95"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${google_cloud_run_v2_service.maestro_router.name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
      comparison      = "COMPARISON_GT"
      threshold_value = 500
      duration        = "300s"
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }
  notification_channels = var.alert_notification_channels
}

resource "google_monitoring_alert_policy" "error_rate" {
  display_name = "Maestro (${var.environment}) — 5xx error rate > 2%"
  combiner     = "OR"
  conditions {
    display_name = "Cloud Run 5xx ratio"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${google_cloud_run_v2_service.maestro_router.name}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.02
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  notification_channels = var.alert_notification_channels
}
