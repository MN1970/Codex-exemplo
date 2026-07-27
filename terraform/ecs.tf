# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-cluster"
  }
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }

  default_capacity_provider_strategy {
    weight            = 50
    capacity_provider = "FARGATE_SPOT"
  }
}

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.main.arn

  tags = {
    Name = "${var.project_name}-ecs-logs"
  }
}

# ====================
# FastAPI Task Definition
# ====================
resource "aws_ecs_task_definition" "fastapi" {
  family                   = "${var.project_name}-fastapi"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "fastapi"
      image     = var.fastapi_container_image
      essential = true

      portMappings = [
        {
          containerPort = var.fastapi_container_port
          hostPort      = var.fastapi_container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "fastapi"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "LOG_LEVEL"
          value = var.environment == "prod" ? "INFO" : "DEBUG"
        },
        {
          name  = "DATABASE_HOST"
          value = aws_db_instance.main.address
        },
        {
          name  = "DATABASE_PORT"
          value = tostring(aws_db_instance.main.port)
        },
        {
          name  = "DATABASE_NAME"
          value = aws_db_instance.main.db_name
        },
        {
          name  = "DATABASE_USER"
          value = aws_db_instance.main.username
        }
      ]

      secrets = [
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.api_keys.arn}:password::"
        },
        {
          name      = "API_KEY"
          valueFrom = "${aws_secretsmanager_secret.api_keys.arn}:api_key::"
        }
      ]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.fastapi_container_port}/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-fastapi-task"
  }
}

# ====================
# React Task Definition
# ====================
resource "aws_ecs_task_definition" "react" {
  family                   = "${var.project_name}-react"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "react"
      image     = var.react_container_image
      essential = true

      portMappings = [
        {
          containerPort = var.react_container_port
          hostPort      = var.react_container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "react"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "REACT_APP_API_BASE_URL"
          value = "https://${aws_lb.main.dns_name}/api"
        }
      ]

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.react_container_port}/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "${var.project_name}-react-task"
  }
}

# ====================
# FastAPI ECS Service
# ====================
resource "aws_ecs_service" "fastapi" {
  name            = "${var.project_name}-fastapi-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi.arn
  desired_count   = var.fastapi_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi.arn
    container_name   = "fastapi"
    container_port   = var.fastapi_container_port
  }

  depends_on = [
    aws_lb_listener.https,
    aws_iam_role_policy.ecs_task_execution_role
  ]

  tags = {
    Name = "${var.project_name}-fastapi-service"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# ====================
# React ECS Service
# ====================
resource "aws_ecs_service" "react" {
  name            = "${var.project_name}-react-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.react.arn
  desired_count   = var.react_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.react.arn
    container_name   = "react"
    container_port   = var.react_container_port
  }

  depends_on = [
    aws_lb_listener.https,
    aws_iam_role_policy.ecs_task_execution_role
  ]

  tags = {
    Name = "${var.project_name}-react-service"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}

# ====================
# Auto-Scaling: FastAPI
# ====================
resource "aws_appautoscaling_target" "fastapi" {
  max_capacity       = 10
  min_capacity       = var.fastapi_desired_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.fastapi.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "fastapi_cpu" {
  name               = "${var.project_name}-fastapi-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.fastapi.resource_id
  scalable_dimension = aws_appautoscaling_target.fastapi.scalable_dimension
  service_namespace  = aws_appautoscaling_target.fastapi.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = var.container_cpu_target_utilization / 100
  }
}

resource "aws_appautoscaling_policy" "fastapi_memory" {
  name               = "${var.project_name}-fastapi-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.fastapi.resource_id
  scalable_dimension = aws_appautoscaling_target.fastapi.scalable_dimension
  service_namespace  = aws_appautoscaling_target.fastapi.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = var.container_memory_target_utilization / 100
  }
}

# ====================
# Auto-Scaling: React
# ====================
resource "aws_appautoscaling_target" "react" {
  max_capacity       = 5
  min_capacity       = var.react_desired_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.react.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "react_cpu" {
  name               = "${var.project_name}-react-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.react.resource_id
  scalable_dimension = aws_appautoscaling_target.react.scalable_dimension
  service_namespace  = aws_appautoscaling_target.react.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = var.container_cpu_target_utilization / 100
  }
}

# ====================
# CloudWatch Alarms
# ====================
resource "aws_cloudwatch_metric_alarm" "ecs_service_cpu_utilization" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "ECS CPU utilization is high"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    ServiceName = aws_ecs_service.fastapi.name
    ClusterName = aws_ecs_cluster.main.name
  }

  tags = {
    Name = "${var.project_name}-ecs-cpu-alarm"
  }
}

# ====================
# Outputs
# ====================
output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

output "fastapi_service_name" {
  description = "FastAPI service name"
  value       = aws_ecs_service.fastapi.name
}

output "react_service_name" {
  description = "React service name"
  value       = aws_ecs_service.react.name
}

output "fastapi_task_definition_arn" {
  description = "FastAPI task definition ARN"
  value       = aws_ecs_task_definition.fastapi.arn
}

output "react_task_definition_arn" {
  description = "React task definition ARN"
  value       = aws_ecs_task_definition.react.arn
}
