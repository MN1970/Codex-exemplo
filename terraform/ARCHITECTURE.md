# Manta Platform - Infrastructure Architecture

Complete infrastructure-as-code solution for deploying a production-grade FastAPI + React application on AWS (with GCP alternative).

## Overview

This Terraform configuration provisions a **highly available, secure, and scalable** cloud infrastructure across:
- **Container Orchestration**: Amazon ECS on Fargate
- **Database**: Amazon RDS PostgreSQL with pgvector
- **API Gateway**: Application Load Balancer with path-based routing
- **Frontend CDN**: CloudFront with S3 static asset hosting
- **Encryption**: KMS encryption at rest for all data
- **Monitoring**: CloudWatch with SNS alerting
- **Security**: Multi-AZ deployment with private database access

## File Inventory (10 Core + 3 Support Files)

### Core Infrastructure Files (10 Terraform modules)

| File | Size | Purpose | Key Resources |
|------|------|---------|-----------------|
| **main.tf** | 3.5 KB | Provider config & foundation | AWS provider, KMS, Secrets Manager, SNS, CloudWatch logs |
| **variables.tf** | 9.2 KB | Input variable definitions | 40+ customizable parameters with validation |
| **vpc.tf** | 8.4 KB | Network infrastructure | VPC, subnets (2 AZ), NAT, security groups, flow logs |
| **rds.tf** | 9.0 KB | PostgreSQL database | RDS Multi-AZ, pgvector, backups, enhanced monitoring |
| **ecs.tf** | 11 KB | Container orchestration | ECS cluster, Fargate tasks, auto-scaling policies |
| **alb.tf** | 9.7 KB | Load balancer & routing | ALB, target groups, HTTPS, path-based routing, alarms |
| **s3.tf** | 8.4 KB | Storage & CDN | S3 bucket, CloudFront, SPA function, lifecycle rules |
| **iam.tf** | 8.6 KB | Identity & Access Management | Task roles, ECR repos, encryption permissions |
| **outputs.tf** | 9.0 KB | Output values | 20+ outputs for manual reference & automation |
| **gcp-equivalent.tf** | 14 KB | GCP alternative (commented) | Cloud Run, Cloud SQL, Cloud CDN, VPC equivalent |

### Support Files

| File | Purpose |
|------|---------|
| **terraform.tfvars.example** | Example configuration template |
| **cloudfront_spa_function.js** | CloudFront function for SPA routing |
| **README.md** (17 KB) | Comprehensive deployment guide |
| **Makefile** (8.6 KB) | 40+ helpful make targets for common operations |
| **ARCHITECTURE.md** | This file - design documentation |

## Infrastructure Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS Account                                │
│                     (Manta Associados - Prod)                       │
└──────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌────────▼─────────┐
            │  VPC: 10.0.0.0 │       │  KMS Encryption  │
            │     /16        │       │   (All-At-Rest)  │
            └───────┬────────┘       └──────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───┐   ┌───▼───┐   ┌──▼────┐
    │  IGW  │   │ NAT   │   │ Logs  │
    │ :80   │   │ :5632 │   │ Group │
    │ :443  │   │       │   │(KMS)  │
    └───┬───┘   └───┬───┘   └──────┘
        │           │
   ┌────┴───────────┴────┐
   │  Public Subnets(2)  │
   │  ┌─────────────┐    │
   │  │    ALB      │    │
   │  │  HTTPS/80   │    │
   │  │  Rules:/api │    │
   │  │      :/     │    │
   │  └──────┬──────┘    │
   └─────────┼────────────┘
             │
   ┌─────────┼──────────────────────┐
   │  Private Subnets (2 AZs)       │
   │                                 │
   │  ┌──────────────────────────┐  │
   │  │   ECS Cluster            │  │
   │  │   ┌────────────────────┐ │  │
   │  │   │  FastAPI Service   │ │  │
   │  │   │  (2 replicas)      │ │  │
   │  │   │  Auto-scale 1-10   │ │  │
   │  │   │  CPU: 512 / Mem:1GB│ │  │
   │  │   └────────┬───────────┘ │  │
   │  │   ┌────────▼───────────┐ │  │
   │  │   │  React Service     │ │  │
   │  │   │  (1 replica)       │ │  │
   │  │   │  CPU: 256 / Mem:512│ │  │
   │  │   └────────────────────┘ │  │
   │  └──────────┬───────────────┘  │
   │             │                   │
   │  ┌──────────▼──────────┐       │
   │  │  RDS PostgreSQL     │       │
   │  │  db.t3.medium       │       │
   │  │  Multi-AZ (HA)      │       │
   │  │  100GB + auto-scale │       │
   │  │  30-day backups     │       │
   │  │  pgvector ext       │       │
   │  │  KMS encrypted      │       │
   │  │  IAM auth enabled   │       │
   │  └─────────────────────┘       │
   └─────────────────────────────────┘
             │
    ┌────────┴──────────┐
    │                   │
┌───▼────┐         ┌────▼────┐
│   S3   │         │CloudFront│
│Bucket  │         │ + CDN    │
│(Assets)│         │(1-year   │
│Version │         │ cache)   │
│Control │         │SPA func  │
│KMS enc │         │Logs:S3   │
└────────┘         └──────────┘

┌────────────────────────────────────────────┐
│      Monitoring & Alarms (CloudWatch)      │
│  - CPU/Memory metrics                      │
│  - Database connections & latency          │
│  - ALB response time & errors              │
│  - RDS storage & backup status             │
│  - SNS notifications to ops team           │
└────────────────────────────────────────────┘
```

## Security Model

### Data at Rest
- **S3 & RDS**: KMS encryption with master key rotation (90 days)
- **CloudWatch Logs**: KMS encryption for sensitive application logs
- **Secrets Manager**: Encrypted API keys, database passwords

### Data in Transit
- **ALB ↔ Clients**: HTTPS only (redirects HTTP)
- **ALB ↔ ECS Tasks**: HTTP within VPC (internal)
- **ECS ↔ RDS**: Private subnet, security group isolation
- **ECS ↔ S3**: VPC Gateway endpoint (no NAT needed)

### Access Control (IAM)
- **Task Execution Role**: ECR pull, CloudWatch write, Secrets fetch
- **Task Role**: S3 read/write, RDS connect, metrics publish
- **No SSH Access**: Bastion host pattern not needed (use Systems Manager)
- **Least Privilege**: Each service has minimal required permissions

### Network Isolation
- **Public Subnets**: ALB only (for incoming traffic)
- **Private Subnets**: ECS tasks, RDS database
- **NAT Gateway**: For outbound internet access from private subnets
- **Security Groups**: Explicit allow rules, deny by default
- **VPC Flow Logs**: All network traffic monitored

## High Availability & Disaster Recovery

### Multi-AZ Architecture
- **Compute**: 2+ Fargate tasks spread across AZs
- **Database**: RDS Multi-AZ with automatic failover
- **Load Balancer**: ALB spans 2+ AZs (no single point of failure)
- **NAT**: Dual NAT Gateways (one per AZ) for redundancy

### Backup & Recovery
- **RDS Backups**: Daily automated + transaction logs (7 days)
- **Backup Retention**: 30 days (customizable)
- **S3 Versioning**: Enabled for asset recovery
- **RTO**: < 15 minutes (RDS multi-AZ automatic failover)
- **RPO**: < 5 minutes (automated backups every 30 seconds)

### Auto-Scaling
- **FastAPI**: 1-10 replicas based on CPU (70%) & memory (80%)
- **React**: 1-5 replicas (lighter workload)
- **RDS Storage**: Auto-scales from 100 GB to 500 GB
- **Fargate Spot**: Optional cost optimization (70% savings)

## Database Design

### PostgreSQL 15.3 Configuration
```
Max Connections: 200
Shared Buffers: Auto-tuned to 25% RAM
Effective Cache: Auto-tuned to 75% RAM
Work Memory: 4 MB per connection
Extensions: pgvector (for embeddings)
```

### Performance Features
- **Query Insights**: Real-time query monitoring
- **Enhanced Monitoring**: CloudWatch metrics every 60s
- **Slow Query Log**: Automatic capture of queries > 1000ms
- **Automated Backups**: Daily snapshots with 30-day retention
- **Parameter Group**: Optimized for 2-4 vCPU instances

### High Availability
- **Multi-AZ Deployment**: Synchronous standby in different AZ
- **Automatic Failover**: < 2 minutes to standby promotion
- **Storage**: 100 GB SSD gp3 with auto-scaling to 500 GB
- **Backup Window**: 03:00-04:00 UTC daily

## Container Strategy

### FastAPI Service
- **Image**: Custom Docker image from ECR
- **Port**: 8000 (configurable)
- **Replicas**: 2 minimum, auto-scales to 10
- **CPU/Memory**: 512 CPU units, 1024 MB RAM
- **Health Check**: HTTP GET /health (30s interval)
- **Logging**: CloudWatch with KMS encryption

### React Service
- **Image**: Custom Docker image from ECR
- **Port**: 3000 (configurable)
- **Replicas**: 1 minimum, auto-scales to 5
- **CPU/Memory**: 256 CPU units, 512 MB RAM
- **Health Check**: HTTP GET / (30s interval)
- **Env Variables**: API_BASE_URL injected at runtime

### ECR Repositories
- **FastAPI Repo**: `ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/manta-platform/fastapi`
- **React Repo**: `ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/manta-platform/react`
- **Image Scanning**: Automatically scan on push
- **Lifecycle**: Keep last 10 images only
- **Encryption**: KMS key encryption

## Load Balancer Strategy

### Application Load Balancer
- **Type**: Layer 7 (Application) - HTTP/HTTPS aware
- **Listeners**: 
  - HTTP (80) → HTTPS redirect (production)
  - HTTPS (443) → ACM certificate required
- **Target Groups**:
  - FastAPI: `/api/*` path pattern
  - React: `/*` catch-all pattern
- **Stickiness**: Enabled (86400s cookie)
- **Access Logs**: S3 bucket with encryption

### Health Checks
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Healthy Threshold**: 2 consecutive checks
- **Unhealthy Threshold**: 3 consecutive failures
- **Success Codes**: 200-299 range

## CloudFront CDN Strategy

### Distribution Configuration
- **Origin**: S3 bucket with Origin Access Identity (OAI)
- **Caching**:
  - Static assets (1 year): `/static/*`
  - HTML/index (1 hour): `index.html`
  - Default (1 hour): everything else
- **SPA Function**: Rewrites 404s to index.html for React routing
- **Compression**: Enabled for text, HTML, CSS, JS
- **HTTP/2 & HTTP/3**: Enabled for performance

### Security
- **Origin Access Identity**: S3 bucket not publicly accessible
- **HTTPS Only**: Redirects HTTP to HTTPS
- **Custom Headers**: Can inject additional security headers
- **Signed Cookies/URLs**: Optional token-based access

## Monitoring & Alarms

### CloudWatch Metrics
| Service | Metric | Threshold | Action |
|---------|--------|-----------|--------|
| **RDS** | CPU > 80% | 2×300s | SNS alert |
| **RDS** | Connections > 150 | 1×300s | SNS alert |
| **RDS** | Free Storage < 10GB | 1×300s | SNS alert |
| **ECS** | CPU > 90% | 2×300s | SNS alert + scale |
| **ALB** | Target 5XX > 10 | 1×60s | SNS alert |
| **ALB** | Unhealthy Hosts > 0 | 1×300s | SNS alert |
| **CloudFront** | 5XX Rate > 1% | 2×300s | SNS alert |

### Log Aggregation
- **ECS Logs**: `/ecs/manta-platform` (CloudWatch)
- **RDS Logs**: PostgreSQL error/audit logs
- **ALB Logs**: S3 bucket with 90-day retention
- **CloudFront Logs**: S3 bucket with 90-day retention
- **VPC Flow Logs**: Network traffic analysis

## Cost Optimization

### Infrastructure Costs (Monthly Estimates)

| Component | Instance | Price | Notes |
|-----------|----------|-------|-------|
| **ALB** | 1 × ALB | $20 | ~0.006/hour |
| **ECS** | 2 FastAPI (Fargate) | $40-50 | CPU on-demand |
| **ECS** | 1 React (Fargate) | $10-15 | Lightweight |
| **RDS** | db.t3.medium Multi-AZ | $400-500 | ~$1.2/hour |
| **NAT** | 2 × NAT Gateways | $45 | ~$0.045/hour each |
| **S3** | Storage + Lifecycle | $5-10 | Glacier archival |
| **CloudFront** | CDN + Caching | $5-10 | 1 year cache |
| **Logging** | CloudWatch + S3 | $10-15 | Retention policies |
| **KMS** | Key operations | $1 | ~$0.03 per 10K ops |
| **Secrets Manager** | API keys storage | $0.40 | Per secret/month |
| **Total** | ~Production Setup | **$550-700/month** | Excludes data transfer |

### Cost Saving Strategies
1. **Fargate Spot**: Use for up to 50% capacity (70% cheaper)
2. **Reserved Instances**: 1-year commitment on RDS (40-60% savings)
3. **Dev/Staging**: Single NAT, db.t3.small, 1 replica
4. **S3 Lifecycle**: Auto-archive old versions to Glacier
5. **CloudFront Cache**: 1-year TTL for static assets (1 request vs 365)

## Deployment Workflow

```
┌─────────────────┐
│ 1. Setup        │
│ - Init Terraform│
│ - Config vars   │
└────────┬────────┘
         │
┌────────▼─────────────────┐
│ 2. Plan Infrastructure   │
│ - terraform plan         │
│ - Review changes         │
└────────┬────────────────┘
         │
┌────────▼─────────────────┐
│ 3. Deploy AWS Resources  │
│ - terraform apply        │
│ - Wait 10-15 minutes     │
└────────┬────────────────┘
         │
┌────────▼──────────────────────┐
│ 4. Push Container Images      │
│ - docker build & push to ECR  │
│ - FastAPI + React             │
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 5. Update ECS Services        │
│ - ecs update-service          │
│ - Force new deployment        │
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 6. Deploy Frontend Assets     │
│ - npm run build               │
│ - aws s3 sync to bucket       │
│ - CloudFront invalidation     │
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 7. Configure DNS              │
│ - Route53 or DNS provider     │
│ - ALB CNAME/ALIAS             │
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 8. Setup SSL Certificate      │
│ - ACM certificate request     │
│ - ALB HTTPS listener          │
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 9. Verify & Test              │
│ - Health checks passing       │
│ - Load tests                  │
│ - SSL validation              │
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 10. Enable Monitoring         │
│ - SNS email subscriptions     │
│ - CloudWatch dashboards       │
│ - Alarms active               │
└──────────────────────────────┘
```

## Multi-Environment Setup

### Development Environment
```
aws_region                      = "us-east-1"
environment                     = "dev"
fastapi_desired_count           = 1
db_instance_class               = "db.t3.small"
db_multi_az                     = false
enable_nat_gateway              = true
single_nat_gateway              = true    # Cost saving
acm_certificate_arn             = ""      # Self-signed OK
Cost/month: ~$150
```

### Staging Environment
```
aws_region                      = "us-east-1"
environment                     = "staging"
fastapi_desired_count           = 2
db_instance_class               = "db.t3.medium"
db_multi_az                     = true    # HA testing
enable_nat_gateway              = true
single_nat_gateway              = false
acm_certificate_arn             = "arn:aws:acm:..."
Cost/month: ~$350
```

### Production Environment
```
aws_region                      = "us-east-1"
environment                     = "prod"
fastapi_desired_count           = 3
db_instance_class               = "db.m6i.large"
db_multi_az                     = true    # Required
enable_nat_gateway              = true
single_nat_gateway              = false   # Dual for HA
acm_certificate_arn             = "arn:aws:acm:..."
Cost/month: ~$700
```

## Support & Maintenance

### Regular Tasks
- **Weekly**: Check CloudWatch alarms, review logs
- **Monthly**: Capacity planning, cost analysis
- **Quarterly**: Security audit, patch updates
- **Semi-annually**: DR testing, plan scaling needs

### Emergency Response
- **Pod Crash**: Auto-restart within 60 seconds
- **RDS Failover**: < 2 minutes to standby
- **ALB Failure**: DNS fails over to backup (not applicable - managed service)
- **Disk Full**: Auto-scaling to 500 GB max (add monitoring for >400 GB)

## Appendix

### AWS Service Limits
- RDS: 100 GB per instance (can increase)
- ECS: 1000 tasks per cluster
- ALB: 1000 target groups per account
- S3: Unlimited storage
- KMS: 1000 keys per account

### Tags Applied to All Resources
```
Environment: dev/staging/prod
Project: manta-platform
ManagedBy: Terraform
CreatedAt: timestamp
Organization: Manta Associados
```

### Referenced Outputs
- **ALB DNS**: manta-platform-alb-1234567890.us-east-1.elb.amazonaws.com
- **RDS Endpoint**: manta-platform-postgres-db.c12345abcde.us-east-1.rds.amazonaws.com
- **CloudFront Domain**: d1234abcde.cloudfront.net
- **S3 Bucket**: manta-platform-react-assets-123456789
