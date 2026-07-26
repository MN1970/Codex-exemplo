# ====================
# Summary Outputs
# ====================

output "deployment_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    environment         = var.environment
    aws_region          = var.aws_region
    project_name        = var.project_name
    deployment_date     = timestamp()
  }
}

# ====================
# Network Outputs
# ====================

output "network_info" {
  description = "Network infrastructure information"
  value = {
    vpc_id                  = aws_vpc.main.id
    vpc_cidr                = aws_vpc.main.cidr_block
    public_subnets         = aws_subnet.public[*].id
    private_subnets        = aws_subnet.private[*].id
    internet_gateway_id    = aws_internet_gateway.main.id
    nat_gateway_ips        = var.enable_nat_gateway ? aws_eip.nat[*].public_ip : []
  }
}

# ====================
# Load Balancer Outputs
# ====================

output "load_balancer_info" {
  description = "Application Load Balancer information"
  value = {
    alb_dns_name        = aws_lb.main.dns_name
    alb_arn             = aws_lb.main.arn
    alb_zone_id         = aws_lb.main.zone_id
    https_enabled       = var.enable_https
    api_endpoint        = "https://${aws_lb.main.dns_name}/api"
    web_endpoint        = "https://${aws_lb.main.dns_name}"
  }
}

output "route53_setup_guide" {
  description = "Instructions for Route53 DNS configuration"
  value = {
    alb_dns_name    = aws_lb.main.dns_name
    alb_zone_id     = aws_lb.main.zone_id
    record_type     = "A"
    record_class    = "ALIAS"
    instructions    = "Create CNAME record pointing to ALB DNS name, or use Route53 ALIAS record pointing to ALB"
  }
}

# ====================
# Database Outputs
# ====================

output "database_info" {
  description = "RDS PostgreSQL database information"
  value = {
    endpoint            = aws_db_instance.main.endpoint
    hostname            = aws_db_instance.main.address
    port                = aws_db_instance.main.port
    database_name       = aws_db_instance.main.db_name
    master_username     = aws_db_instance.main.username
    multi_az_enabled    = aws_db_instance.main.multi_az
    backup_retention    = aws_db_instance.main.backup_retention_days
    storage_encrypted   = aws_db_instance.main.storage_encrypted
  }
}

output "database_connection_string" {
  description = "PostgreSQL connection string template"
  value       = "postgresql://${aws_db_instance.main.username}:PASSWORD@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "database_resource_id" {
  description = "RDS instance resource ID (for IAM auth)"
  value       = aws_db_instance.main.resource_id
}

# ====================
# Container Outputs
# ====================

output "container_info" {
  description = "ECS container service information"
  value = {
    ecs_cluster_name    = aws_ecs_cluster.main.name
    ecs_cluster_arn     = aws_ecs_cluster.main.arn
    fastapi_service     = aws_ecs_service.fastapi.name
    react_service       = aws_ecs_service.react.name
    fastapi_replicas    = aws_ecs_service.fastapi.desired_count
    react_replicas      = aws_ecs_service.react.desired_count
  }
}

output "ecr_repositories" {
  description = "ECR repository information for pushing container images"
  value = {
    fastapi_repository_url = aws_ecr_repository.fastapi.repository_url
    react_repository_url   = aws_ecr_repository.react.repository_url
    fastapi_push_command   = "docker tag YOUR_IMAGE:latest ${aws_ecr_repository.fastapi.repository_url}:latest && docker push ${aws_ecr_repository.fastapi.repository_url}:latest"
    react_push_command     = "docker tag YOUR_IMAGE:latest ${aws_ecr_repository.react.repository_url}:latest && docker push ${aws_ecr_repository.react.repository_url}:latest"
  }
}

# ====================
# Storage Outputs
# ====================

output "storage_info" {
  description = "S3 and CDN information"
  value = {
    react_assets_bucket    = aws_s3_bucket.react_assets.id
    cloudfront_enabled     = var.s3_cloudfront_enabled
    cloudfront_domain      = var.s3_cloudfront_enabled ? aws_cloudfront_distribution.react_assets[0].domain_name : null
    cloudfront_id          = var.s3_cloudfront_enabled ? aws_cloudfront_distribution.react_assets[0].id : null
  }
}

output "s3_deployment_guide" {
  description = "Instructions for deploying React assets to S3"
  value = {
    bucket_name = aws_s3_bucket.react_assets.id
    upload_command = "aws s3 sync ./build s3://${aws_s3_bucket.react_assets.id}/ --delete"
    cloudfront_invalidate = var.s3_cloudfront_enabled ? "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.react_assets[0].id} --paths '/*'" : null
  }
}

# ====================
# Security Outputs
# ====================

output "security_info" {
  description = "Security-related resources"
  value = {
    kms_key_id                      = aws_kms_key.main.id
    kms_key_arn                     = aws_kms_key.main.arn
    secrets_manager_secret_arn      = aws_secretsmanager_secret.api_keys.arn
    iam_task_execution_role_arn     = aws_iam_role.ecs_task_execution_role.arn
    iam_task_role_arn               = aws_iam_role.ecs_task_role.arn
  }
}

output "security_groups" {
  description = "Security group IDs for reference"
  value = {
    alb_sg                  = aws_security_group.alb.id
    ecs_tasks_sg            = aws_security_group.ecs_tasks.id
    rds_sg                  = aws_security_group.rds.id
  }
}

# ====================
# Monitoring Outputs
# ====================

output "monitoring_info" {
  description = "CloudWatch monitoring resources"
  value = {
    log_group_name        = aws_cloudwatch_log_group.ecs.name
    sns_alarm_topic_arn   = aws_sns_topic.alarms.arn
    monitoring_enabled    = var.enable_monitoring
  }
}

# ====================
# Quick Reference
# ====================

output "quick_reference" {
  description = "Quick reference for common tasks"
  value = {
    ssh_jump_host_required = true
    ec2_directly_reachable = false
    access_method = "via ALB at ${aws_lb.main.dns_name}"

    database_access = {
      from_ec2 = "psql -h ${aws_db_instance.main.address} -U ${aws_db_instance.main.username} -d ${aws_db_instance.main.db_name}"
      from_lambda = "Use VPC endpoint or NAT gateway with security group rules"
      iam_auth_enabled = true
    }

    container_logs = "aws logs tail /ecs/${var.project_name} --follow"

    scale_fastapi = "aws application-autoscaling update-scalable-target --service-namespace ecs --resource-id service/${aws_ecs_cluster.main.name}/${aws_ecs_service.fastapi.name} --scalable-dimension ecs:service:DesiredCount --min-capacity 2 --max-capacity 20"

    view_alarms = "aws cloudwatch describe-alarms --alarm-names ${var.project_name}-* --region ${var.aws_region}"
  }
}

# ====================
# Compliance & Cost
# ====================

output "compliance_checklist" {
  description = "Compliance features enabled"
  value = {
    encryption_at_rest        = true
    encryption_in_transit     = true
    backup_retention_days     = aws_db_instance.main.backup_retention_days
    multi_az_deployment       = aws_db_instance.main.multi_az
    public_access_blocked     = true
    vpc_flow_logs_enabled     = var.enable_flow_logs
    enhanced_monitoring       = var.enable_enhanced_monitoring
    deletion_protection       = var.environment == "prod"
    automated_backups         = var.enable_backups
  }
}

output "cost_optimization_tips" {
  description = "Cost optimization recommendations"
  value = {
    use_fargate_spot = "Consider using Fargate Spot for non-critical services (up to 70% savings)"
    scale_down_non_prod = "Set min capacity to 1 for dev/staging environments"
    s3_lifecycle = "Old objects transition to Glacier after ${var.s3_lifecycle_transition_days} days"
    cloudfront_caching = "Static assets cached for ${var.cloudfront_default_ttl} seconds"
    rds_multi_az = var.environment == "prod" ? "Multi-AZ enabled (cost: ~100% additional)" : "Multi-AZ disabled for cost savings in dev"
  }
}

# ====================
# Next Steps
# ====================

output "next_steps" {
  description = "Recommended next steps after deployment"
  value = {
    step_1 = "Configure DNS: Create CNAME or ALIAS record pointing to ALB (${aws_lb.main.dns_name})"
    step_2 = "Upload SSL Certificate: If using custom domain, import ACM certificate and update ALB listener"
    step_3 = "Push Docker Images: Build and push FastAPI and React images to ECR repositories"
    step_4 = "Update ECS Tasks: Update task definitions with correct ECR image URIs"
    step_5 = "Deploy React Assets: Upload compiled React build to S3 bucket"
    step_6 = "Verify Alarms: Check SNS topic subscriptions and test alarm emails"
    step_7 = "Configure Secrets: Store database password and API keys in Secrets Manager"
    step_8 = "Enable Backup: Verify RDS backup window and retention policy"
    step_9 = "Monitor Logs: Check CloudWatch logs for application startup issues"
    step_10 = "Performance Test: Load test the application and monitor CloudWatch metrics"
  }
}
