variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-\\d{1}$", var.aws_region))
    error_message = "AWS region must be valid (e.g., us-east-1, eu-west-1)."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "manta-platform"

  validation {
    condition     = can(regex("^[a-z0-9\\-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway (cost saving, less HA)"
  type        = bool
  default     = false
}

variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway"
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class (e.g., db.t3.medium, db.m6i.large)"
  type        = string
  default     = "db.t3.medium"

  validation {
    condition     = can(regex("^db\\.", var.db_instance_class))
    error_message = "Instance class must start with 'db.' (e.g., db.t3.medium)."
  }
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 100

  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "Database storage must be between 20 and 65536 GB."
  }
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS autoscaling in GB"
  type        = number
  default     = 500

  validation {
    condition     = var.db_max_allocated_storage >= var.db_allocated_storage
    error_message = "Max allocated storage must be >= allocated storage."
  }
}

variable "db_backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30

  validation {
    condition     = var.db_backup_retention_days >= 7 && var.db_backup_retention_days <= 35
    error_message = "Backup retention must be between 7 and 35 days."
  }
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = true
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "manta_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Master database password (minimum 8 characters)"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 8
    error_message = "Database password must be at least 8 characters."
  }
}

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for RDS"
  type        = bool
  default     = true
}

# ECS Configuration
variable "fastapi_container_image" {
  description = "Docker image URI for FastAPI service"
  type        = string
  default     = "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/fastapi:latest"
}

variable "fastapi_container_port" {
  description = "Container port for FastAPI"
  type        = number
  default     = 8000

  validation {
    condition     = var.fastapi_container_port > 0 && var.fastapi_container_port < 65536
    error_message = "Container port must be between 1 and 65535."
  }
}

variable "fastapi_desired_count" {
  description = "Desired number of FastAPI task replicas"
  type        = number
  default     = 2

  validation {
    condition     = var.fastapi_desired_count >= 1 && var.fastapi_desired_count <= 10
    error_message = "Desired count must be between 1 and 10."
  }
}

variable "react_container_image" {
  description = "Docker image URI for React service"
  type        = string
  default     = "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/react:latest"
}

variable "react_container_port" {
  description = "Container port for React"
  type        = number
  default     = 3000
}

variable "react_desired_count" {
  description = "Desired number of React task replicas"
  type        = number
  default     = 1

  validation {
    condition     = var.react_desired_count >= 1 && var.react_desired_count <= 5
    error_message = "Desired count must be between 1 and 5."
  }
}

variable "ecs_task_cpu" {
  description = "Task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512

  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.ecs_task_cpu)
    error_message = "Task CPU must be 256, 512, 1024, 2048, or 4096."
  }
}

variable "ecs_task_memory" {
  description = "Task memory in MB"
  type        = number
  default     = 1024

  validation {
    condition     = contains([512, 1024, 2048, 3072, 4096, 5120, 6144, 7168, 8192], var.ecs_task_memory)
    error_message = "Task memory must be a valid value (512, 1024, 2048, etc.)."
  }
}

variable "container_cpu_target_utilization" {
  description = "Target CPU utilization for auto-scaling (%)"
  type        = number
  default     = 70

  validation {
    condition     = var.container_cpu_target_utilization > 0 && var.container_cpu_target_utilization < 100
    error_message = "CPU utilization must be between 1 and 99 percent."
  }
}

variable "container_memory_target_utilization" {
  description = "Target memory utilization for auto-scaling (%)"
  type        = number
  default     = 80

  validation {
    condition     = var.container_memory_target_utilization > 0 && var.container_memory_target_utilization < 100
    error_message = "Memory utilization must be between 1 and 99 percent."
  }
}

# ALB Configuration
variable "enable_https" {
  description = "Enable HTTPS on ALB (requires ACM certificate)"
  type        = bool
  default     = true
}

variable "acm_certificate_arn" {
  description = "ARN of ACM certificate for HTTPS (required if enable_https=true)"
  type        = string
  default     = ""
}

variable "alb_health_check_path" {
  description = "Health check path for ALB target group"
  type        = string
  default     = "/health"
}

variable "alb_health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "alb_health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "alb_health_check_healthy_threshold" {
  description = "Healthy threshold count"
  type        = number
  default     = 2
}

variable "alb_health_check_unhealthy_threshold" {
  description = "Unhealthy threshold count"
  type        = number
  default     = 3
}

# S3 Configuration
variable "s3_bucket_versioning_enabled" {
  description = "Enable versioning on S3 bucket"
  type        = bool
  default     = true
}

variable "s3_cloudfront_enabled" {
  description = "Enable CloudFront distribution for S3 bucket"
  type        = bool
  default     = true
}

variable "cloudfront_default_ttl" {
  description = "CloudFront default TTL in seconds"
  type        = number
  default     = 3600

  validation {
    condition     = var.cloudfront_default_ttl >= 0
    error_message = "TTL must be non-negative."
  }
}

variable "cloudfront_max_ttl" {
  description = "CloudFront max TTL in seconds"
  type        = number
  default     = 86400
}

variable "s3_lifecycle_transition_days" {
  description = "Days before transitioning objects to Glacier"
  type        = number
  default     = 90

  validation {
    condition     = var.s3_lifecycle_transition_days > 0
    error_message = "Transition days must be positive."
  }
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring and alarms"
  type        = bool
  default     = true
}

variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch value."
  }
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default = {
    MaintainedBy = "Manta-Associados"
    CostCenter   = "Infrastructure"
  }
}
