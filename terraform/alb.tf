# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "prod" ? true : false
  enable_http2              = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "${var.project_name}-alb"
  }

  depends_on = [aws_internet_gateway.main]
}

# ALB Access Logs S3 Bucket
resource "aws_s3_bucket" "alb_logs" {
  bucket = "${var.project_name}-alb-logs-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${var.project_name}-alb-logs"
  }
}

resource "aws_s3_bucket_versioning" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bucket policy for ALB access logs
data "aws_elb_service_account" "main" {}

resource "aws_s3_bucket_policy" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = data.aws_elb_service_account.main.arn
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.alb_logs.arn}/*"
      }
    ]
  })
}

# Enable ALB access logs
resource "aws_lb" "main" {
  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    enabled = true
    prefix  = "alb"
  }
}

# ====================
# Target Groups
# ====================

# FastAPI Target Group
resource "aws_lb_target_group" "fastapi" {
  name        = "${var.project_name}-fastapi-tg"
  port        = var.fastapi_container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = var.alb_health_check_healthy_threshold
    unhealthy_threshold = var.alb_health_check_unhealthy_threshold
    timeout             = var.alb_health_check_timeout
    interval            = var.alb_health_check_interval
    path                = var.alb_health_check_path
    matcher             = "200-299"
  }

  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = true
  }

  tags = {
    Name = "${var.project_name}-fastapi-tg"
  }
}

# React Target Group
resource "aws_lb_target_group" "react" {
  name        = "${var.project_name}-react-tg"
  port        = var.react_container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = var.alb_health_check_healthy_threshold
    unhealthy_threshold = var.alb_health_check_unhealthy_threshold
    timeout             = var.alb_health_check_timeout
    interval            = var.alb_health_check_interval
    path                = "/"
    matcher             = "200-299"
  }

  tags = {
    Name = "${var.project_name}-react-tg"
  }
}

# ====================
# ALB Listeners
# ====================

# HTTP Listener (redirect to HTTPS in production)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = var.enable_https ? "redirect" : "forward"

    dynamic "redirect" {
      for_each = var.enable_https ? [1] : []
      content {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }

    dynamic "forward" {
      for_each = !var.enable_https ? [1] : []
      content {
        target_group {
          arn    = aws_lb_target_group.react.arn
          weight = 100
        }
      }
    }
  }
}

# HTTPS Listener (conditional)
resource "aws_lb_listener" "https" {
  count             = var.enable_https ? 1 : 0
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.acm_certificate_arn != "" ? var.acm_certificate_arn : aws_acm_certificate.self_signed[0].arn
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.react.arn
  }
}

# Self-signed certificate for testing (only if ACM cert not provided)
resource "tls_private_key" "self_signed" {
  count     = var.enable_https && var.acm_certificate_arn == "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "self_signed" {
  count           = var.enable_https && var.acm_certificate_arn == "" ? 1 : 0
  private_key_pem = tls_private_key.self_signed[0].private_key_pem

  subject {
    common_name  = aws_lb.main.dns_name
    organization = "Manta Associados"
  }

  validity_period_hours = 8760 # 1 year

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "aws_acm_certificate" "self_signed" {
  count             = var.enable_https && var.acm_certificate_arn == "" ? 1 : 0
  private_key      = tls_private_key.self_signed[0].private_key_pem
  certificate_body = tls_self_signed_cert.self_signed[0].cert_pem

  tags = {
    Name = "${var.project_name}-self-signed-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ====================
# ALB Rules for Path-based Routing
# ====================

# Rule: /api/* → FastAPI
resource "aws_lb_listener_rule" "fastapi" {
  count            = var.enable_https ? 1 : 0
  listener_arn     = aws_lb_listener.https[0].arn
  priority         = 1
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fastapi.arn
  }

  condition {
    path_pattern {
      values = ["/api", "/api/*"]
    }
  }
}

# Rule: / → React (catch-all)
resource "aws_lb_listener_rule" "react" {
  count            = var.enable_https ? 1 : 0
  listener_arn     = aws_lb_listener.https[0].arn
  priority         = 100
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.react.arn
  }

  condition {
    path_pattern {
      values = ["/*"]
    }
  }
}

# ====================
# ALB Monitoring
# ====================

resource "aws_cloudwatch_metric_alarm" "alb_target_response_time" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-alb-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Average"
  threshold           = "1" # 1 second
  alarm_description   = "ALB target response time is high"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name = "${var.project_name}-alb-response-time"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_hosts" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-alb-unhealthy-hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "ALB has unhealthy hosts"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.fastapi.arn_suffix
  }

  tags = {
    Name = "${var.project_name}-alb-unhealthy-hosts"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_http_4xx" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-alb-http-4xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "HTTPCode_Target_4XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50"
  alarm_description   = "High number of HTTP 4XX errors"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  tags = {
    Name = "${var.project_name}-alb-4xx"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_http_5xx" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-alb-http-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "High number of HTTP 5XX errors"
  alarm_actions       = [aws_sns_topic.alarms.arn]

  tags = {
    Name = "${var.project_name}-alb-5xx"
  }
}

# ====================
# Outputs
# ====================

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ALB ARN"
  value       = aws_lb.main.arn
}

output "alb_zone_id" {
  description = "ALB zone ID (for Route53 ALIAS records)"
  value       = aws_lb.main.zone_id
}

output "fastapi_target_group_arn" {
  description = "FastAPI target group ARN"
  value       = aws_lb_target_group.fastapi.arn
}

output "react_target_group_arn" {
  description = "React target group ARN"
  value       = aws_lb_target_group.react.arn
}
