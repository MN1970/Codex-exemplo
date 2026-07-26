# Terraform Infrastructure as Code - Manta Platform

Production-ready Terraform configuration for deploying a scalable FastAPI + React application on AWS (with GCP alternative).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Internet / Users                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   ALB (HTTPS)   │
                    │  with WAF-ready │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐         ┌───▼────┐
    │ FastAPI │         │  React  │         │ S3/CDN │
    │  (ECS)  │         │  (ECS)  │         │Assets  │
    └────┬────┘         └────┬────┘         └───┬────┘
         │                   │                   │
    ┌────▼───────────────────▼─────────────────┐
    │         Private Subnets (2 AZs)          │
    │  - ECS Cluster (Fargate)                 │
    │  - VPC Endpoints                         │
    └────┬────────────────────────────────────┘
         │
    ┌────▼──────────────┐
    │  RDS PostgreSQL   │
    │  Multi-AZ with    │
    │  - pgvector ext.  │
    │  - IAM Auth       │
    │  - Encrypted      │
    └───────────────────┘
```

## Prerequisites

- AWS Account with appropriate IAM permissions
- Terraform >= 1.5.0
- AWS CLI configured with credentials
- Docker (for building container images)
- Node.js & npm (for React app)
- Python 3.9+ (for FastAPI app)

## File Structure

```
terraform/
├── main.tf                          # AWS provider, KMS, Secrets Manager, SNS
├── variables.tf                     # Input variable definitions
├── vpc.tf                           # VPC, subnets, security groups, NAT
├── rds.tf                           # PostgreSQL database with pgvector
├── ecs.tf                           # ECS cluster, Fargate services, auto-scaling
├── alb.tf                           # Application Load Balancer, target groups
├── s3.tf                            # S3 bucket, CloudFront CDN
├── iam.tf                           # IAM roles, ECR repositories
├── outputs.tf                       # Output values for reference
├── gcp-equivalent.tf                # Alternative GCP deployment (commented)
├── cloudfront_spa_function.js       # CloudFront function for SPA routing
├── terraform.tfvars.example         # Example variables file
└── README.md                        # This file
```

## Quick Start

### 1. Prepare Variables

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 2. Initialize Terraform

```bash
terraform init
# For remote state on S3 (recommended for production):
# Configure backend in main.tf first, then:
# terraform init -backend-config="bucket=your-bucket" -backend-config="key=prod/terraform.tfstate"
```

### 3. Validate Configuration

```bash
terraform validate
terraform plan -out=tfplan
```

### 4. Apply Configuration

```bash
terraform apply tfplan
```

### 5. Verify Deployment

```bash
# Get outputs
terraform output

# Check ECS services
aws ecs list-services --cluster manta-platform-cluster --region us-east-1

# Check RDS instance
aws rds describe-db-instances --db-instance-identifier manta-platform-postgres-db --region us-east-1
```

## Configuration Details

### Network (vpc.tf)

- **VPC CIDR**: 10.0.0.0/16 (customizable)
- **Public Subnets**: 2 AZs for ALB, NAT Gateway, bastion hosts
- **Private Subnets**: 2 AZs for ECS, RDS
- **NAT Gateway**: Single or dual (configurable)
- **VPC Flow Logs**: For traffic monitoring and troubleshooting
- **Security Groups**:
  - ALB: Ingress HTTP(80), HTTPS(443)
  - ECS Tasks: From ALB on container ports
  - RDS: From ECS tasks on port 5432

### Database (rds.tf)

- **Engine**: PostgreSQL 15.3
- **Instance Class**: db.t3.medium (configurable)
- **Storage**: 100 GB with auto-scaling to 500 GB
- **High Availability**: Multi-AZ deployment (production only)
- **Backups**: 30-day retention with automated daily backups
- **Encryption**: KMS encryption at rest
- **Extensions**: pgvector for vector similarity search
- **Performance Insights**: Enabled for query analysis
- **Enhanced Monitoring**: CloudWatch metrics every 60 seconds
- **IAM Authentication**: Supported for connections
- **Optimized Parameters**: For 2-4 vCPU instances

### Container Orchestration (ecs.tf)

- **Cluster**: Fargate cluster with Container Insights
- **FastAPI Service**:
  - 2 replicas (configurable, min=1, max=10)
  - Auto-scaling based on CPU (70%) and memory (80%)
  - Health checks every 30 seconds
  - Graceful shutdown (60s timeout)
  - CloudWatch logging with KMS encryption

- **React Service**:
  - 1 replica (configurable, min=1, max=5)
  - Lightweight container (256 CPU, 512 MB memory)
  - Auto-scaling capability
  - Health checks on root path

- **Task Definition Features**:
  - CPU: 512 units, Memory: 1024 MB (FastAPI)
  - Environment variables for database connection
  - Secrets from Secrets Manager for sensitive data
  - Execution role for container image pulls & logs
  - Task role for S3, RDS, CloudWatch access

### Load Balancer (alb.tf)

- **Type**: Application Load Balancer (ALB)
- **Listeners**:
  - HTTP (80): Auto-redirect to HTTPS in production
  - HTTPS (443): With ACM certificate or self-signed
- **Path-based Routing**:
  - `/api/*` → FastAPI target group
  - `/*` → React target group
- **Target Groups**:
  - Stickiness enabled (86400s cookie duration)
  - Health checks customizable per target
- **Access Logs**: Stored in encrypted S3 bucket
- **Monitoring**: Response time, 4xx/5xx errors, unhealthy hosts

### Storage & CDN (s3.tf)

- **S3 Bucket**: For React static assets
- **Versioning**: Enabled for asset recovery
- **Encryption**: KMS encryption at rest
- **Public Access**: Blocked (CloudFront OAI only)
- **Lifecycle Policy**: Transition to Glacier after 90 days
- **CloudFront Distribution**:
  - Custom domain support with ACM certificate
  - SPA routing function for client-side routes
  - Static asset caching (1 year TTL)
  - HTML caching (1 hour TTL)
  - HTTP/2 and HTTP/3 support
  - Custom error pages (404/403 → index.html for SPA)
- **CloudFront Function**: Handles SPA routing automatically

### Security & IAM (iam.tf)

- **Task Execution Role**:
  - ECR image pull permissions
  - CloudWatch logs write
  - Secrets Manager access
  - KMS decrypt

- **Task Role**:
  - S3 read/write for assets
  - RDS database connect
  - CloudWatch metrics publish
  - KMS encrypt/decrypt

- **ECR Repositories**:
  - Separate repos for FastAPI and React
  - KMS encryption
  - Image scanning on push
  - Lifecycle policy (keep last 10 images)

- **Encryption**:
  - KMS master key with 90-day rotation
  - S3 bucket encryption
  - RDS encryption at rest
  - EBS encryption
  - Secrets Manager encryption

## Deployment Guide

### Step 1: Build and Push Container Images

```bash
# Build FastAPI Docker image
cd ../fastapi
docker build -t fastapi:latest .

# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag fastapi:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/manta-platform/fastapi:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/manta-platform/fastapi:latest

# Build React Docker image
cd ../react
docker build -t react:latest .

docker tag react:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/manta-platform/react:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/manta-platform/react:latest
```

### Step 2: Deploy Infrastructure

```bash
cd terraform
terraform apply
```

### Step 3: Update ECS Task Definitions

```bash
# Trigger ECS service update to pull latest images
aws ecs update-service --cluster manta-platform-cluster \
  --service manta-platform-fastapi-service \
  --force-new-deployment --region us-east-1
```

### Step 4: Deploy React Assets

```bash
# Build React application
cd ../react
npm run build

# Upload to S3
aws s3 sync build/ s3://manta-platform-react-assets-ACCOUNT_ID/ --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "Distributions[?Origins[0].DomainName=='manta-platform-react-assets-ACCOUNT_ID.s3.us-east-1.amazonaws.com'].Id" --output text)
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

### Step 5: Configure DNS

```bash
# Get ALB DNS name
terraform output alb_dns_name

# Option A: Route53 ALIAS record (recommended)
aws route53 change-resource-record-sets --hosted-zone-id ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z18D5FSRJIJILD",
          "DNSName": "manta-platform-alb-1234567890.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# Option B: CNAME record
# app.example.com -> manta-platform-alb-1234567890.us-east-1.elb.amazonaws.com
```

### Step 6: Install SSL Certificate

If using a custom domain with HTTPS:

```bash
# Request or import ACM certificate
aws acm request-certificate \
  --domain-name app.example.com \
  --subject-alternative-names "*.app.example.com" \
  --region us-east-1

# Update ALB listener with certificate ARN
# (Modify terraform.tfvars: acm_certificate_arn)
terraform apply
```

## Monitoring & Alarms

### CloudWatch Dashboards

```bash
# View RDS metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=manta-platform-postgres-db \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

### Check Alarms

```bash
# List all alarms for this project
aws cloudwatch describe-alarms \
  --alarm-names manta-platform-* \
  --region us-east-1
```

### View ECS Logs

```bash
# Real-time FastAPI logs
aws logs tail /ecs/manta-platform --follow

# Filter by service
aws logs filter-log-events \
  --log-group-name /ecs/manta-platform \
  --filter-pattern "fastapi"
```

## Scaling

### Scale FastAPI Horizontally

```bash
# Update desired count manually
aws ecs update-service --cluster manta-platform-cluster \
  --service manta-platform-fastapi-service \
  --desired-count 5 --region us-east-1

# Or modify terraform.tfvars and apply
# fastapi_desired_count = 5
```

### Database Scaling

```bash
# Modify instance class (requires downtime)
# In terraform.tfvars: db_instance_class = "db.m6i.large"
terraform apply

# View storage auto-scaling
aws rds describe-db-instances \
  --db-instance-identifier manta-platform-postgres-db \
  --query 'DBInstances[0].[MaxAllocatedStorage,AllocatedStorage]'
```

## Disaster Recovery

### Backup & Recovery

```bash
# List available backups
aws rds describe-db-snapshots \
  --db-instance-identifier manta-platform-postgres-db

# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier manta-platform-postgres-db \
  --db-snapshot-identifier manual-backup-2024-01-15

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier manta-platform-postgres-db-restored \
  --db-snapshot-identifier manual-backup-2024-01-15
```

### RTO/RPO Metrics

- **RTO** (Recovery Time Objective): < 15 minutes (RDS Multi-AZ failover)
- **RPO** (Recovery Point Objective): < 5 minutes (automated backups + transaction logs)

## Cost Optimization

### Recommendations

1. **Use Fargate Spot**: Replace up to 50% of capacity with FARGATE_SPOT for 70% savings
2. **Dev/Staging**: Use single NAT Gateway, db.t3.small, 1 replica
3. **Reserved Instances**: For production RDS (up to 72% savings)
4. **S3 Lifecycle**: Transition old assets to Glacier after 90 days (included)
5. **CloudFront Caching**: Cache static assets for 1 year (included)

### Estimated Monthly Cost (Production)

- ALB: ~$20
- ECS Fargate: ~$80-100 (2 FastAPI, 1 React)
- RDS db.t3.medium Multi-AZ: ~$400-500
- NAT Gateway: ~$45 + data transfer
- S3/CloudFront: ~$10-30 (depending on traffic)
- **Total**: ~$550-700/month

## Troubleshooting

### ECS Tasks Not Starting

```bash
# Check task definition
aws ecs describe-task-definition \
  --task-definition manta-platform-fastapi

# View task logs
aws logs get-log-events \
  --log-group-name /ecs/manta-platform \
  --log-stream-name fastapi/...

# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT_ID:role/manta-platform-ecs-task-role \
  --action-names ecr:GetDownloadUrlForLayer s3:GetObject
```

### Database Connection Issues

```bash
# Test RDS security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp --port 5432 \
  --source-security-group-id sg-yyyyy

# Check RDS parameter group
aws rds describe-db-parameters \
  --db-parameter-group-name manta-platform-postgres15-params \
  --query 'Parameters[?ParameterName==`max_connections`]'
```

### CloudFront Not Serving Content

```bash
# Check distribution status
aws cloudfront get-distribution-config \
  --id DISTRIBUTION_ID

# List objects in S3
aws s3 ls s3://manta-platform-react-assets-ACCOUNT_ID/ --recursive

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id DISTRIBUTION_ID \
  --paths "/*"
```

## Security Best Practices Implemented

✅ Encryption at rest (KMS)  
✅ Encryption in transit (TLS/HTTPS)  
✅ VPC isolation for databases  
✅ Security groups with least privilege  
✅ IAM roles with minimal permissions  
✅ Secrets Manager for sensitive data  
✅ Multi-AZ high availability  
✅ Automated backups with retention  
✅ Access logging (ALB, S3, CloudFront)  
✅ CloudWatch monitoring & alarms  
✅ RDS deletion protection in production  
✅ VPC Flow Logs for network monitoring  

## Multi-Region Deployment

To deploy to multiple regions, create separate terraform workspaces:

```bash
terraform workspace new us-west-2
terraform workspace select us-west-2

# Update terraform.tfvars for new region
aws_region = "us-west-2"

terraform init
terraform apply
```

## GCP Alternative

Uncomment the `gcp-equivalent.tf` file and provide GCP variables:

```bash
gcp_project_id = "manta-platform-prod"
gcp_region     = "us-central1"
```

This will deploy:
- Cloud Run (FastAPI)
- Cloud SQL (PostgreSQL)
- Cloud Storage (React assets)
- Cloud CDN (equivalent to CloudFront)

## Support & Maintenance

- **Terraform State**: Stored in S3 with encryption and versioning
- **Locking**: DynamoDB table prevents concurrent modifications
- **Validation**: `terraform validate` before every apply
- **Cost Analysis**: Use AWS Cost Explorer for monitoring
- **Updates**: Review AWS provider changelog for deprecated resources

## References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [PostgreSQL on RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [CloudFront with S3](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/DownloadDistS3AndCustomOrigins.html)

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0  
**Organization**: Manta Associados
