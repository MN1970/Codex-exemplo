# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# RDS Parameter Group with optimized PostgreSQL settings
resource "aws_db_parameter_group" "main" {
  family      = "postgres15"
  name        = "${var.project_name}-postgres15-params"
  description = "Optimized PostgreSQL 15 parameters for ${var.project_name}"

  # PostgreSQL optimization parameters
  parameter {
    name  = "max_connections"
    value = "200"
  }

  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/32768}"
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory/4096}"
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "{DBInstanceClassMemory/16}"
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "wal_buffers"
    value = "16384"
  }

  parameter {
    name  = "work_mem"
    value = "4194"
  }

  parameter {
    name  = "min_wal_size"
    value = "2048"
  }

  parameter {
    name  = "max_wal_size"
    value = "8192"
  }

  # Enable pgvector extension
  parameter {
    name  = "shared_preload_libraries"
    value = "pgvector"
  }

  # Performance Insights
  parameter {
    name  = "track_activity_query_size"
    value = "2048"
  }

  # Logging
  parameter {
    name  = "log_statement"
    value = "ddl"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  tags = {
    Name = "${var.project_name}-db-params"
  }
}

# Enhanced Monitoring IAM Role
resource "aws_iam_role" "rds_monitoring" {
  count = var.enable_enhanced_monitoring ? 1 : 0
  name  = "${var.project_name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-rds-monitoring-role"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.enable_enhanced_monitoring ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# RDS Database Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-postgres-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.db_instance_class

  # Storage
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  iops                  = 3000
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.main.arn

  # Database Configuration
  db_name  = "mantadb"
  username = var.db_username
  password = var.db_password

  # Network
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # High Availability
  multi_az               = var.db_multi_az
  backup_retention_days  = var.db_backup_retention_days
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  copy_tags_to_snapshot  = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "${var.project_name}-postgres-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Performance & Monitoring
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  performance_insights_kms_key_id       = aws_kms_key.main.arn
  enabled_cloudwatch_logs_exports       = ["postgresql"]

  # Enhanced Monitoring
  monitoring_interval             = var.enable_enhanced_monitoring ? 60 : 0
  monitoring_role_arn             = var.enable_enhanced_monitoring ? aws_iam_role.rds_monitoring[0].arn : null
  enable_iam_database_authentication = true

  # Parameter Group
  parameter_group_name = aws_db_parameter_group.main.name

  # Backups & Binary Logs
  enable_cloudwatch_logs_exports = ["postgresql"]
  enable_automatic_minor_version_upgrade = true
  auto_minor_version_upgrade     = true

  # Deletion protection
  deletion_protection = var.environment == "prod" ? true : false

  depends_on = [aws_security_group.rds]

  tags = {
    Name = "${var.project_name}-postgres-db"
  }
}

# RDS Enhanced Monitoring Alarms
resource "aws_cloudwatch_metric_alarm" "rds_cpu_utilization" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "RDS CPU utilization is high"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "${var.project_name}-rds-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_database_connections" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-rds-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "150"
  alarm_description   = "RDS database connections are high"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "${var.project_name}-rds-connections-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_free_storage_space" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-rds-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10737418240" # 10 GB in bytes
  alarm_description   = "RDS free storage space is low"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "${var.project_name}-rds-storage-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_read_latency" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-rds-read-latency-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ReadLatency"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "5" # 5 ms
  alarm_description   = "RDS read latency is high"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  tags = {
    Name = "${var.project_name}-rds-latency-alarm"
  }
}

# RDS Backup Alarm
resource "aws_cloudwatch_metric_alarm" "rds_backup_window" {
  count               = var.enable_monitoring && var.enable_backups ? 1 : 0
  alarm_name          = "${var.project_name}-rds-backup-window"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "FailedSQLServerAgentJobsCount"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "RDS backup failed"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  tags = {
    Name = "${var.project_name}-rds-backup-alarm"
  }
}

# Outputs
output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.main.id
}

output "db_instance_endpoint" {
  description = "RDS instance endpoint (hostname:port)"
  value       = aws_db_instance.main.endpoint
  sensitive   = false
}

output "db_instance_address" {
  description = "RDS instance address (hostname only)"
  value       = aws_db_instance.main.address
  sensitive   = false
}

output "db_instance_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
  sensitive   = false
}

output "db_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "db_resource_id" {
  description = "RDS instance resource ID"
  value       = aws_db_instance.main.resource_id
}

output "db_backup_window" {
  description = "RDS backup window"
  value       = aws_db_instance.main.backup_window
}

output "db_parameter_group_name" {
  description = "RDS parameter group name"
  value       = aws_db_parameter_group.main.name
}
