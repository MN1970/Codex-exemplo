terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration for state management
  # Uncomment and configure based on your setup
  backend "s3" {
    # bucket         = "manta-terraform-state-prod"
    # key            = "infrastructure/terraform.tfstate"
    # region         = "us-east-1"
    # encrypt        = true
    # dynamodb_table = "terraform-locks"
  }
}

# Primary AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
      Organization = "Manta Associados"
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Data source for available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# KMS Key for encryption at rest
resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.project_name} infrastructure encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-kms-key"
  }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-main"
  target_key_id = aws_kms_key.main.key_id
}

# CloudWatch Log Group for centralized logging
resource "aws_cloudwatch_log_group" "main" {
  name              = "/manta/${var.project_name}/${var.environment}"
  retention_in_days = var.log_retention_days

  kms_key_id = aws_kms_key.main.arn

  tags = {
    Name = "${var.project_name}-logs"
  }
}

# SNS Topic for alarms
resource "aws_sns_topic" "alarms" {
  name              = "${var.project_name}-${var.environment}-alarms"
  kms_master_key_id = aws_kms_key.main.id

  tags = {
    Name = "${var.project_name}-alarms"
  }
}

resource "aws_sns_topic_subscription" "alarms_email" {
  count             = var.alarm_email != "" ? 1 : 0
  topic_arn         = aws_sns_topic.alarms.arn
  protocol          = "email"
  endpoint          = var.alarm_email
  filter_policy     = jsonencode({ environment = [var.environment] })
}

# Secrets Manager for API keys and sensitive data
resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "${var.project_name}/${var.environment}/api-keys"
  description             = "API keys for ${var.project_name}"
  recovery_window_in_days = 7
  kms_key_id              = aws_kms_key.main.id

  tags = {
    Name = "${var.project_name}-api-keys"
  }
}

# Enable automatic rotation (handler Lambda must be created separately)
resource "aws_secretsmanager_secret_rotation" "api_keys" {
  secret_id           = aws_secretsmanager_secret.api_keys.id
  rotation_rules {
    automatically_after_days = 30
  }
}

# Output for reference in other modules/scripts
output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "kms_key_id" {
  description = "KMS Key ID for encryption"
  value       = aws_kms_key.main.id
  sensitive   = false
}

output "kms_key_arn" {
  description = "KMS Key ARN"
  value       = aws_kms_key.main.arn
}

output "log_group_name" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.main.name
}

output "sns_alarm_topic_arn" {
  description = "SNS Topic ARN for alarms"
  value       = aws_sns_topic.alarms.arn
}

output "secrets_manager_secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.api_keys.arn
}
