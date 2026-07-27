# ====================
# GCP Provider Configuration
# ====================
# This file provides a GCP equivalent deployment for organizations
# preferring Google Cloud Platform over AWS. Uncomment and configure
# the provider block below to use GCP. Variables remain mostly the same.

/*

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# ====================
# GCP Variables (add to variables.tf)
# ====================

variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region (e.g., us-central1, europe-west1)"
  type        = string
  default     = "us-central1"
}

# ====================
# VPC Network (GCP equivalent)
# ====================

resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

# Public Subnet
resource "google_compute_subnetwork" "public" {
  name          = "${var.project_name}-public-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Private Subnet
resource "google_compute_subnetwork" "private" {
  name          = "${var.project_name}-private-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  private_ip_google_access = true
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Cloud NAT for private subnet outbound access
resource "google_compute_router" "main" {
  name    = "${var.project_name}-router"
  region  = var.gcp_region
  network = google_compute_network.main.id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "main" {
  name                               = "${var.project_name}-nat"
  router                             = google_compute_router.main.name
  region                             = var.gcp_region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ====================
# Firewall Rules
# ====================

resource "google_compute_firewall" "allow_http_https" {
  name    = "${var.project_name}-allow-http-https"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server", "https-server"]
}

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.project_name}-allow-internal"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = ["10.0.0.0/16"]
}

# ====================
# Cloud SQL (PostgreSQL)
# ====================

resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-postgres"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier              = var.gcp_db_tier # e.g., db-custom-2-8192 (2 vCPU, 8GB RAM)
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    backup_configuration {
      enabled                        = var.enable_backups
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_days          = var.db_backup_retention_days
      transaction_log_retention_days = 7
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "200"
    }

    database_flags {
      name  = "shared_buffers"
      value = "262144"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }

    active_directory_config {
      domain = ""
    }
  }

  deletion_protection = var.environment == "prod" ? true : false

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Private VPC Connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.project_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Cloud SQL Database
resource "google_sql_database" "main" {
  name     = var.environment == "prod" ? "mantadb" : "devdb"
  instance = google_sql_database_instance.main.name
}

# Cloud SQL User
resource "google_sql_user" "main" {
  name     = var.db_username
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# ====================
# Cloud Run (FastAPI)
# ====================

resource "google_cloud_run_service" "fastapi" {
  name     = "${var.project_name}-fastapi"
  location = var.gcp_region

  template {
    spec {
      containers {
        image = var.fastapi_container_image # gcr.io/PROJECT_ID/fastapi:latest

        ports {
          container_port = var.fastapi_container_port
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DATABASE_HOST"
          value = google_sql_database_instance.main.private_ip_address
        }

        env {
          name  = "DATABASE_PORT"
          value = "5432"
        }

        env {
          name  = "DATABASE_NAME"
          value = google_sql_database.main.name
        }

        env {
          name  = "DATABASE_USER"
          value = google_sql_user.main.name
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run.email

      vpc_access_connector {
        name = google_vpc_access_connector.main.name
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/max-scale" = "100"
        "autoscaling.knative.dev/min-scale" = var.fastapi_desired_count
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_vpc_access_connector.main,
    google_service_account.cloud_run
  ]
}

# VPC Access Connector for Cloud Run
resource "google_vpc_access_connector" "main" {
  name          = "${var.project_name}-vpc-connector"
  region        = var.gcp_region
  subnet {
    name = google_compute_subnetwork.private.name
  }
}

# Cloud Run IAM: Public Access
resource "google_cloud_run_service_iam_binding" "fastapi_public" {
  service = google_cloud_run_service.fastapi.name
  role    = "roles/run.invoker"

  members = [
    "allUsers"
  ]

  location = var.gcp_region
}

# ====================
# Cloud Storage (React)
# ====================

resource "google_storage_bucket" "react_assets" {
  name          = "${var.project_name}-react-assets-${data.google_client_config.default.project}"
  location      = "US"
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = var.s3_bucket_versioning_enabled
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage.id
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = var.s3_lifecycle_transition_days
    }
    action {
      type          = "SetStorageClass"
      storage_class = ["NEARLINE"]
    }
  }
}

# Cloud CDN (CloudFront equivalent)
resource "google_compute_backend_bucket" "react_cdn" {
  name            = "${var.project_name}-react-cdn"
  bucket_name     = google_storage_bucket.react_assets.name
  enable_cdn      = true
  cdn_policy {
    client_ttl    = var.cloudfront_default_ttl
    default_ttl   = var.cloudfront_default_ttl
    max_ttl       = var.cloudfront_max_ttl
    negative_caching = true
  }
}

# ====================
# KMS Encryption
# ====================

resource "google_kms_key_ring" "main" {
  name     = "${var.project_name}-key-ring"
  location = var.gcp_region
}

resource "google_kms_crypto_key" "storage" {
  name            = "${var.project_name}-storage-key"
  key_ring        = google_kms_key_ring.main.id
  rotation_period = "7776000s" # 90 days
}

resource "google_kms_crypto_key" "database" {
  name            = "${var.project_name}-database-key"
  key_ring        = google_kms_key_ring.main.id
  rotation_period = "7776000s"
}

# ====================
# Service Accounts & IAM
# ====================

resource "google_service_account" "cloud_run" {
  account_id   = "${var.project_name}-cloud-run"
  display_name = "Cloud Run Service Account for ${var.project_name}"
}

resource "google_project_iam_member" "cloud_run_cloud_sql" {
  project = var.gcp_project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_storage" {
  project = var.gcp_project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_secrets" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# ====================
# Cloud Load Balancer
# ====================

resource "google_compute_url_map" "main" {
  name            = "${var.project_name}-load-balancer"
  default_service = google_compute_backend_service.fastapi.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "main"
  }

  path_matcher {
    name            = "main"
    default_service = google_compute_backend_service.fastapi.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.fastapi.id
    }

    path_rule {
      paths   = ["/*"]
      service = google_compute_backend_bucket.react_cdn.id
    }
  }
}

resource "google_compute_backend_service" "fastapi" {
  name        = "${var.project_name}-fastapi-backend"
  protocol    = "HTTP2"
  port_name   = "http"
  timeout_sec = 30

  backend {
    group = google_cloud_run_service.fastapi.id
  }

  health_checks = [google_compute_health_check.fastapi.id]
}

resource "google_compute_health_check" "fastapi" {
  name = "${var.project_name}-health-check"

  http_health_check {
    port         = var.fastapi_container_port
    request_path = var.alb_health_check_path
  }
}

resource "google_compute_ssl_certificate" "main" {
  name        = "${var.project_name}-ssl-cert"
  description = "SSL certificate for ${var.project_name}"
}

resource "google_compute_target_https_proxy" "main" {
  name      = "${var.project_name}-https-proxy"
  url_map   = google_compute_url_map.main.id
  ssl_certificates = [
    google_compute_ssl_certificate.main.id
  ]
}

resource "google_compute_global_forwarding_rule" "main" {
  name       = "${var.project_name}-forwarding-rule"
  ip_version = "IPV4"
  load_balancing_scheme = "EXTERNAL"
  port_range = "443"
  target     = google_compute_target_https_proxy.main.id
}

# ====================
# Monitoring (GCP equivalent)
# ====================

resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification"
  type         = "email"
  labels = {
    email_address = var.alarm_email
  }
}

resource "google_monitoring_alert_policy" "cpu_utilization" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.project_name} - High CPU Utilization"
  combiner        = "OR"
  notification_channels = [
    google_monitoring_notification_channel.email.id
  ]

  conditions {
    display_name = "CPU > 80%"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND metric.type = \"run.googleapis.com/request_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 80
    }
  }
}

# ====================
# Outputs
# ====================

output "gcp_deployment_info" {
  description = "GCP deployment information"
  value = {
    project_id           = var.gcp_project_id
    region               = var.gcp_region
    fastapi_service_url  = google_cloud_run_service.fastapi.status[0].url
    cloud_sql_instance   = google_sql_database_instance.main.connection_name
    storage_bucket       = google_storage_bucket.react_assets.name
  }
}

data "google_client_config" "default" {}

*/
