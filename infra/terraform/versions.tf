terraform {
  required_version = ">= 1.7.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.3"
    }
  }

  backend "gcs" {
    bucket = "manta-terraform-state"
    prefix = "maestro"
  }
}
