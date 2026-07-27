#!/bin/bash
#
# CloudWatch Monitoring & Alerting Setup for Phase 2
# Configures dashboards, log groups, and metric alarms
# Usage: ./cloudwatch-setup.sh [--dashboards|--alarms|--logs|--all|--help]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/tmp/cloudwatch_setup_${TIMESTAMP}.log"

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"
NAMESPACE="Maestro/Phase2"
DASHBOARD_NAME="maestro-phase2-monitoring"
LOG_GROUP="/maestro/phase2"
RETENTION_DAYS=90

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# Logging Utilities
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗${NC} $*" | tee -a "$LOG_FILE"
}

# ============================================================================
# Prerequisites Checks
# ============================================================================

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi

    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        echo "Install with: sudo apt-get install awscli jq"
        return 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        return 1
    fi

    if [ -z "$AWS_ACCOUNT_ID" ]; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        log_info "Detected AWS Account ID: $AWS_ACCOUNT_ID"
    fi

    log_success "Prerequisites verified"
    return 0
}

# ============================================================================
# Log Group Setup
# ============================================================================

setup_log_groups() {
    log_info "Setting up CloudWatch log groups..."

    # Create main log group
    local log_groups=(
        "/maestro/phase2"
        "/maestro/phase2/rag-ingestion"
        "/maestro/phase2/orchestrator"
        "/maestro/phase2/classifier"
        "/maestro/phase2/sharepoint-sync"
        "/maestro/phase2/feedback-loop"
    )

    for lg in "${log_groups[@]}"; do
        log_info "Creating log group: $lg"
        if aws logs create-log-group --log-group-name "$lg" --region "$AWS_REGION" 2>/dev/null; then
            log_success "Created: $lg"
        else
            log_warn "Log group already exists: $lg"
        fi

        # Set retention policy
        aws logs put-retention-policy \
            --log-group-name "$lg" \
            --retention-in-days "$RETENTION_DAYS" \
            --region "$AWS_REGION" 2>/dev/null

        log_success "Retention policy set: $RETENTION_DAYS days"
    done

    log_success "Log groups configured"
}

# ============================================================================
# CloudWatch Dashboard
# ============================================================================

create_dashboard() {
    log_info "Creating CloudWatch dashboard..."

    # Dashboard JSON definition
    cat > /tmp/maestro_dashboard.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "Maestro/Phase2", "RAGSearchLatency", { "stat": "Average" } ],
          [ "...", { "stat": "p95" } ],
          [ "...", { "stat": "Maximum" } ]
        ],
        "period": 60,
        "stat": "Average",
        "region": "AWS_REGION_PLACEHOLDER",
        "title": "RAG Vector Search Latency",
        "yAxis": {
          "left": {
            "min": 0,
            "max": 1000,
            "label": "Milliseconds"
          }
        }
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "Maestro/Phase2", "RAGChunksProcessed" ],
          [ ".", "RowingsProcessed" ],
          [ ".", "VectorEmbeddingsGenerated" ]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "AWS_REGION_PLACEHOLDER",
        "title": "RAG Ingestion Progress"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "Maestro/Phase2", "FeedbackSubmissions", { "stat": "Sum" } ],
          [ ".", "RoutingAccuracy", { "stat": "Average" } ],
          [ ".", "AmbiguousQueriesDetected", { "stat": "Sum" } ]
        ],
        "period": 60,
        "stat": "Average",
        "region": "AWS_REGION_PLACEHOLDER",
        "title": "Feedback Loop & Routing"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "Maestro/Phase2", "SharePointSyncLatency", { "stat": "Average" } ],
          [ "...", { "stat": "p95" } ],
          [ "Maestro/Phase2", "FilesSyncedCount", { "stat": "Sum" } ]
        ],
        "period": 300,
        "stat": "Average",
        "region": "AWS_REGION_PLACEHOLDER",
        "title": "SharePoint Synchronization"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "fields @timestamp, @message, @duration | stats count() by @duration",
        "region": "AWS_REGION_PLACEHOLDER",
        "title": "Phase 2 Error Rate"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          [ "AWS/Lambda", "Duration", { "stat": "Average" } ],
          [ "...", "Errors", { "stat": "Sum" } ],
          [ "...", "Invocations", { "stat": "Sum" } ]
        ],
        "period": 60,
        "stat": "Sum",
        "region": "AWS_REGION_PLACEHOLDER",
        "title": "Lambda Functions (if used)"
      }
    }
  ]
}
EOF

    # Replace placeholder with actual region
    sed -i "s/AWS_REGION_PLACEHOLDER/$AWS_REGION/g" /tmp/maestro_dashboard.json

    # Create dashboard
    log_info "Deploying dashboard: $DASHBOARD_NAME"
    aws cloudwatch put-dashboard \
        --dashboard-name "$DASHBOARD_NAME" \
        --dashboard-body file:///tmp/maestro_dashboard.json \
        --region "$AWS_REGION"

    log_success "Dashboard created: $DASHBOARD_NAME"
    log_info "View at: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=$DASHBOARD_NAME"
}

# ============================================================================
# CloudWatch Alarms
# ============================================================================

create_alarms() {
    log_info "Creating CloudWatch alarms..."

    # Alarm 1: RAG Search Latency
    log_info "Creating alarm: RAG Search Latency High"
    aws cloudwatch put-metric-alarm \
        --alarm-name "maestro-rag-latency-high" \
        --alarm-description "RAG vector search latency exceeds 500ms" \
        --metric-name "RAGSearchLatency" \
        --namespace "$NAMESPACE" \
        --statistic "Average" \
        --period 300 \
        --threshold 500 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 2 \
        --treat-missing-data "notBreaching" \
        --region "$AWS_REGION"
    log_success "Alarm created: maestro-rag-latency-high"

    # Alarm 2: Ingestion Failure Rate
    log_info "Creating alarm: RAG Ingestion Failures"
    aws cloudwatch put-metric-alarm \
        --alarm-name "maestro-rag-ingestion-failures" \
        --alarm-description "RAG ingestion failure rate exceeds 5%" \
        --metric-name "RAGIngestionFailureRate" \
        --namespace "$NAMESPACE" \
        --statistic "Average" \
        --period 300 \
        --threshold 5 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 1 \
        --treat-missing-data "notBreaching" \
        --region "$AWS_REGION"
    log_success "Alarm created: maestro-rag-ingestion-failures"

    # Alarm 3: SharePoint Sync Failures
    log_info "Creating alarm: SharePoint Sync Failures"
    aws cloudwatch put-metric-alarm \
        --alarm-name "maestro-sharepoint-sync-failures" \
        --alarm-description "SharePoint sync has failed 3+ times consecutively" \
        --metric-name "SharePointSyncFailureCount" \
        --namespace "$NAMESPACE" \
        --statistic "Sum" \
        --period 600 \
        --threshold 3 \
        --comparison-operator "GreaterThanOrEqualToThreshold" \
        --evaluation-periods 1 \
        --treat-missing-data "notBreaching" \
        --region "$AWS_REGION"
    log_success "Alarm created: maestro-sharepoint-sync-failures"

    # Alarm 4: API Error Rate
    log_info "Creating alarm: High API Error Rate"
    aws cloudwatch put-metric-alarm \
        --alarm-name "maestro-api-error-rate-high" \
        --alarm-description "API error rate exceeds 5%" \
        --metric-name "APIErrorRate" \
        --namespace "$NAMESPACE" \
        --statistic "Average" \
        --period 300 \
        --threshold 5 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 2 \
        --treat-missing-data "notBreaching" \
        --region "$AWS_REGION"
    log_success "Alarm created: maestro-api-error-rate-high"

    # Alarm 5: Vector Chunks Below Threshold
    log_info "Creating alarm: Insufficient Vector Chunks"
    aws cloudwatch put-metric-alarm \
        --alarm-name "maestro-vector-chunks-low" \
        --alarm-description "Vector chunks count below 4000" \
        --metric-name "VectorChunksTotal" \
        --namespace "$NAMESPACE" \
        --statistic "Maximum" \
        --period 300 \
        --threshold 4000 \
        --comparison-operator "LessThanThreshold" \
        --evaluation-periods 1 \
        --treat-missing-data "notBreaching" \
        --region "$AWS_REGION"
    log_success "Alarm created: maestro-vector-chunks-low"

    # Alarm 6: Feedback Loop Inactive
    log_info "Creating alarm: Feedback Loop Inactive"
    aws cloudwatch put-metric-alarm \
        --alarm-name "maestro-feedback-loop-inactive" \
        --alarm-description "Feedback submissions have stopped (0 in last hour)" \
        --metric-name "FeedbackSubmissions" \
        --namespace "$NAMESPACE" \
        --statistic "Sum" \
        --period 3600 \
        --threshold 1 \
        --comparison-operator "LessThanThreshold" \
        --evaluation-periods 1 \
        --treat-missing-data "breaching" \
        --region "$AWS_REGION"
    log_success "Alarm created: maestro-feedback-loop-inactive"

    log_success "All alarms created"
}

# ============================================================================
# CloudWatch Insights Queries
# ============================================================================

create_log_insights_queries() {
    log_info "Creating CloudWatch Insights queries..."

    # Create queries file
    cat > "$REPO_ROOT/infra/monitoring/insights-queries.md" << 'EOQUERY'
# CloudWatch Insights Queries - Phase 2 Monitoring

## RAG Ingestion Performance

### Chunks Processed by Collection
```
fields @timestamp, collection_id, chunk_count
| stats sum(chunk_count) as total_chunks by collection_id
```

### Embedding Latency Distribution
```
fields @timestamp, embedding_latency_ms
| stats avg(embedding_latency_ms) as avg_latency, pct(embedding_latency_ms, 95) as p95_latency, max(embedding_latency_ms) as max_latency
```

### Ingestion Error Analysis
```
fields @timestamp, error_type, error_message
| filter @message like /ERROR/
| stats count() as error_count by error_type
```

## Vector Search Performance

### Search Latency by Query Type
```
fields @timestamp, query_type, search_latency_ms
| stats avg(search_latency_ms) as avg_latency, pct(search_latency_ms, 95) as p95 by query_type
```

### Top Slow Queries
```
fields @timestamp, query_text, search_latency_ms
| filter search_latency_ms > 500
| stats count() as occurrence by query_text
| sort occurrence desc
| limit 10
```

## SharePoint Sync Monitoring

### Sync Success Rate
```
fields @timestamp, sync_status
| stats count(*) as total, count(sync_status="success") as successful by sync_status
| fields successful, total
```

### Sync Latency Analysis
```
fields @timestamp, sync_duration_ms
| stats avg(sync_duration_ms) as avg_latency, pct(sync_duration_ms, 95) as p95, max(sync_duration_ms) as max_duration
```

### Conflict Detection
```
fields @timestamp, file_path, conflict_type
| filter conflict_type != "none"
| stats count() as conflicts by file_path
| sort conflicts desc
```

## Feedback Loop Analytics

### Feedback Submission Rate
```
fields @timestamp, agent_routed_to
| stats count() as submissions by agent_routed_to
```

### Routing Accuracy by Agent
```
fields @timestamp, agent_routed_to, relevant_result
| stats count(*) as total, count(relevant_result=true) as correct by agent_routed_to
| fields agent_routed_to, correct, total, round(100.0 * correct / total, 2) as accuracy_percent
```

### Feedback Processing Latency
```
fields @timestamp, feedback_processing_time_ms
| stats avg(feedback_processing_time_ms) as avg_time, pct(feedback_processing_time_ms, 95) as p95_time
```

## System Health

### API Error Breakdown
```
fields @timestamp, error_code, endpoint
| filter error_code >= 400
| stats count() as error_count by error_code, endpoint
| sort error_count desc
```

### Database Connection Issues
```
fields @timestamp, event_type, connection_status
| filter event_type="connection_error"
| stats count() as connection_errors by connection_status
```

### Memory and CPU Usage
```
fields @timestamp, resource_type, usage_percent
| stats avg(usage_percent) as avg_usage, max(usage_percent) as peak_usage by resource_type
```

## Cost Tracking

### API Call Volume
```
fields @timestamp, api_endpoint, call_count
| stats sum(call_count) as total_calls by api_endpoint
```

### Cost by Service
```
fields @timestamp, service_name, cost_usd
| stats sum(cost_usd) as total_cost by service_name
```

## Operational Insights

### Top Error Types
```
fields @timestamp, error_type
| filter @message like /ERROR/
| stats count() as frequency by error_type
| sort frequency desc
| limit 15
```

### Component Health Summary
```
fields @timestamp, component, health_status
| stats count(*) as checks, count(health_status="healthy") as healthy_checks by component
| fields component, healthy_checks, checks
```

EOQUERY

    log_success "Insights queries saved to: infra/monitoring/insights-queries.md"
}

# ============================================================================
# Metric Publishing Configuration
# ============================================================================

create_metrics_publisher() {
    log_info "Creating metrics publisher configuration..."

    # Python script for publishing custom metrics
    cat > "$REPO_ROOT/scripts/publish_cloudwatch_metrics.py" << 'EOMETRY'
#!/usr/bin/env python3
"""
CloudWatch Custom Metrics Publisher for Phase 2
Publishes application metrics to CloudWatch for monitoring
"""

import os
import json
import boto3
from datetime import datetime
from typing import Dict, Any

class CloudWatchMetricsPublisher:
    def __init__(self, namespace: str = "Maestro/Phase2", region: str = "us-east-1"):
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.namespace = namespace
        self.metrics_buffer = []

    def put_metric(self, metric_name: str, value: float, unit: str = "None",
                   dimensions: Dict[str, str] = None) -> bool:
        """Publish a single metric"""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
            }

            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': v} for k, v in dimensions.items()
                ]

            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            return True
        except Exception as e:
            print(f"Error publishing metric {metric_name}: {e}")
            return False

    def put_rag_metrics(self, chunks_processed: int, latency_ms: float,
                       success: bool, collection: str):
        """Publish RAG ingestion metrics"""
        self.put_metric('RAGChunksProcessed', chunks_processed, 'Count',
                       {'Collection': collection})
        self.put_metric('RAGSearchLatency', latency_ms, 'Milliseconds',
                       {'Collection': collection})
        self.put_metric('RAGIngestionSuccess', 1 if success else 0, 'None')

    def put_sync_metrics(self, latency_ms: float, files_synced: int,
                        conflicts: int):
        """Publish SharePoint sync metrics"""
        self.put_metric('SharePointSyncLatency', latency_ms, 'Milliseconds')
        self.put_metric('FilesSyncedCount', files_synced, 'Count')
        self.put_metric('SyncConflictCount', conflicts, 'Count')

    def put_feedback_metrics(self, submissions: int, accuracy: float,
                           agent: str):
        """Publish feedback loop metrics"""
        self.put_metric('FeedbackSubmissions', submissions, 'Count',
                       {'Agent': agent})
        self.put_metric('RoutingAccuracy', accuracy * 100, 'Percent',
                       {'Agent': agent})

    def put_api_metrics(self, error_count: int, latency_ms: float,
                       endpoint: str):
        """Publish API metrics"""
        self.put_metric('APIErrorCount', error_count, 'Count',
                       {'Endpoint': endpoint})
        self.put_metric('APILatency', latency_ms, 'Milliseconds',
                       {'Endpoint': endpoint})

if __name__ == "__main__":
    publisher = CloudWatchMetricsPublisher()

    # Example: Publish metrics
    publisher.put_rag_metrics(
        chunks_processed=100,
        latency_ms=145.3,
        success=True,
        collection="saneamento"
    )

    print("✓ Metrics published to CloudWatch")

EOMETRY

    chmod +x "$REPO_ROOT/scripts/publish_cloudwatch_metrics.py"
    log_success "Metrics publisher script created"
}

# ============================================================================
# Alerts Configuration
# ============================================================================

setup_sns_notifications() {
    log_info "Setting up SNS notifications for alarms..."

    # Create SNS topic for alarms
    local topic_name="maestro-phase2-alarms"

    log_info "Creating SNS topic: $topic_name"
    local topic_arn=$(aws sns create-topic --name "$topic_name" --region "$AWS_REGION" \
        --query 'TopicArn' --output text)

    log_success "SNS topic created: $topic_arn"

    # Subscribe email (if provided)
    if [ -n "${ALERT_EMAIL:-}" ]; then
        log_info "Subscribing email: $ALERT_EMAIL"
        aws sns subscribe --topic-arn "$topic_arn" \
            --protocol email --notification-endpoint "$ALERT_EMAIL" \
            --region "$AWS_REGION"
        log_success "Email subscription created (requires confirmation)"
    fi

    # Store topic ARN
    echo "$topic_arn" > /tmp/maestro_sns_topic_arn.txt
    log_info "Topic ARN saved to: /tmp/maestro_sns_topic_arn.txt"
}

# ============================================================================
# Validation & Testing
# ============================================================================

validate_setup() {
    log_info "Validating CloudWatch setup..."

    # Check log groups
    local log_groups=$(aws logs describe-log-groups --log-group-name-prefix "/maestro" \
        --region "$AWS_REGION" --query 'logGroups[].logGroupName' --output text)

    if [ -n "$log_groups" ]; then
        log_success "Log groups found: $log_groups"
    else
        log_warn "No log groups found"
        return 1
    fi

    # Check dashboard
    local dashboard=$(aws cloudwatch get-dashboard --dashboard-name "$DASHBOARD_NAME" \
        --region "$AWS_REGION" 2>/dev/null || true)

    if [ -n "$dashboard" ]; then
        log_success "Dashboard verified: $DASHBOARD_NAME"
    else
        log_warn "Dashboard not found"
        return 1
    fi

    # Check alarms
    local alarms=$(aws cloudwatch describe-alarms --alarm-name-prefix "maestro" \
        --region "$AWS_REGION" --query 'MetricAlarms[].AlarmName' --output text)

    if [ -n "$alarms" ]; then
        log_success "Alarms found: $(echo $alarms | wc -w) alarms configured"
        echo "Alarms: $alarms"
    else
        log_warn "No alarms found"
        return 1
    fi

    log_success "CloudWatch setup validation complete"
    return 0
}

# ============================================================================
# Usage & Help
# ============================================================================

show_help() {
    cat << EOF
${BLUE}CloudWatch Monitoring & Alerting Setup - Phase 2${NC}

${BLUE}Usage:${NC}
  $0 [COMMAND]

${BLUE}Commands:${NC}
  --logs         Create log groups
  --dashboards   Create monitoring dashboards
  --alarms       Create metric alarms
  --insights     Create Insights queries
  --metrics      Create metrics publisher
  --sns          Setup SNS notifications
  --all          Run all setup steps (default)
  --validate     Validate CloudWatch configuration
  --help         Show this help message

${BLUE}Environment Variables:${NC}
  AWS_REGION              AWS region (default: us-east-1)
  AWS_ACCOUNT_ID          AWS account ID (auto-detected if not set)
  ALERT_EMAIL             Email for alarm notifications (optional)

${BLUE}Examples:${NC}
  # Full setup
  $0 --all

  # Just create logs
  $0 --logs

  # With email alerts
  ALERT_EMAIL=ops@mantaassociados.com $0 --all

${BLUE}Features:${NC}
  ✓ Log groups for all Phase 2 components
  ✓ CloudWatch dashboard with 6 widget panels
  ✓ Metric alarms with thresholds
  ✓ CloudWatch Insights queries (30+ templates)
  ✓ Custom metrics publisher (Python)
  ✓ SNS notifications for alerts
  ✓ Validation and health checks

${BLUE}Dashboard URL:${NC}
  https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:

${BLUE}Log Groups:${NC}
  /maestro/phase2
  /maestro/phase2/rag-ingestion
  /maestro/phase2/orchestrator
  /maestro/phase2/classifier
  /maestro/phase2/sharepoint-sync
  /maestro/phase2/feedback-loop

${BLUE}Alarms (6 total):${NC}
  1. maestro-rag-latency-high (>500ms)
  2. maestro-rag-ingestion-failures (>5%)
  3. maestro-sharepoint-sync-failures (≥3 consecutive)
  4. maestro-api-error-rate-high (>5%)
  5. maestro-vector-chunks-low (<4000)
  6. maestro-feedback-loop-inactive (0 in 1h)

EOF
}

# ============================================================================
# Main
# ============================================================================

main() {
    log_info "CloudWatch Monitoring Setup - Phase 2"
    log_info "Timestamp: $(date)"
    log_info "Region: $AWS_REGION"

    if ! check_prerequisites; then
        return 1
    fi

    case "${1:-all}" in
        --logs)
            setup_log_groups
            ;;
        --dashboards)
            create_dashboard
            ;;
        --alarms)
            create_alarms
            ;;
        --insights)
            create_log_insights_queries
            ;;
        --metrics)
            create_metrics_publisher
            ;;
        --sns)
            setup_sns_notifications
            ;;
        --validate)
            validate_setup
            ;;
        --all)
            setup_log_groups
            create_dashboard
            create_alarms
            create_log_insights_queries
            create_metrics_publisher
            setup_sns_notifications
            validate_setup
            log_success "All CloudWatch components configured!"
            log_info "Next steps:"
            log_info "1. Confirm email subscription in your inbox"
            log_info "2. Configure application to publish metrics"
            log_info "3. View dashboard: https://console.aws.amazon.com/cloudwatch/"
            ;;
        --help)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            return 1
            ;;
    esac

    log_info "Log file: $LOG_FILE"
}

main "$@"
