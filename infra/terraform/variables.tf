variable "project_id" {
  description = "GCP project ID hosting Maestro"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run / GKE"
  type        = string
  default     = "southamerica-east1"
}

variable "environment" {
  description = "staging or production"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be 'staging' or 'production'."
  }
}

variable "image" {
  description = "Fully qualified container image (registry/repo:tag)"
  type        = string
}

variable "min_instances" {
  description = "Minimum warm Cloud Run instances (0 for staging, >=2 for production to avoid cold starts)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
  default     = 20
}

variable "cpu" {
  description = "vCPU allocated per instance"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory per instance"
  type        = string
  default     = "1Gi"
}

variable "concurrency" {
  description = "Max concurrent requests per instance before scaling out"
  type        = number
  default     = 40
}

variable "anthropic_api_key_secret_id" {
  description = "Secret Manager secret ID holding the Anthropic API key"
  type        = string
  default     = "maestro-anthropic-api-key"
}

variable "supabase_service_role_key_secret_id" {
  description = "Secret Manager secret ID holding the Supabase service role key"
  type        = string
  default     = "maestro-supabase-service-role-key"
}

variable "supabase_project_ref" {
  description = "Supabase project ref (for the supabase provider, PITR config, etc.)"
  type        = string
}

variable "alert_notification_channels" {
  description = "Cloud Monitoring notification channel IDs (Slack, PagerDuty, email)"
  type        = list(string)
  default     = []
}
