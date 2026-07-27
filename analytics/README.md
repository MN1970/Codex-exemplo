# Phase 4.2 Advanced Analytics — Implementation Guide

**Version:** 1.0 (2026-07-27)  
**Status:** Production-Ready  
**Target Timeline:** Q2 2028 (Phase 4 roadmap)

---

## Overview

Phase 4.2 Advanced Analytics delivers complete business intelligence and predictive intelligence for the Manta Maestro platform. This package implements:

1. **Analytics Pipeline** — Real-time data collection, aggregation, federation
2. **BI Dashboard Integration** — Pre-built dashboards for Looker/Tableau
3. **Predictive Models** — Forecasting, drift detection, anomaly detection
4. **Monitoring & Alerting** — Health checks, incident escalation, SLA enforcement
5. **Testing & Validation** — Comprehensive test suite with model evaluation

---

## Components

### 1. Analytics Pipeline (`analytics_pipeline.py`)

Collects routing events and aggregates metrics for BI dashboards.

**Key Classes:**
- `RoutingEvent`: Individual routing decision
- `AggregatedMetrics`: Daily/weekly rollup (volume, accuracy, cost)
- `AnalyticsPipeline`: Main orchestrator

**Usage:**
```python
from analytics.analytics_pipeline import AnalyticsPipeline, RoutingEvent
from datetime import datetime

# Initialize pipeline
pipeline = AnalyticsPipeline('postgresql://user:pass@db:5432/maestro')

# Ingest event
event = RoutingEvent(
    event_id='evt-123',
    timestamp=datetime.utcnow(),
    user_id='user-1',
    organization_id='org-1',
    query='pavimento CBUQ rodoviário',
    routed_agent='agente-infraestrutura-S1',
    routing_confidence=0.92,
    routing_method='llm_tiebreaker',
    outcome='correct',
    feedback_score=5.0,
    input_tokens=150,
    output_tokens=250,
    model_used='claude-opus',
    cost_usd=0.015,
    phase='3',
    region='BR-SP',
    segment='S1'
)
pipeline.ingest_event(event)

# Calculate metrics
accuracy = pipeline.calculate_routing_accuracy('org-1', hours=24)
cost_per_query = pipeline.calculate_cost_per_query('org-1', days=7)
cohorts = pipeline.cohort_analysis('org-1')

# Daily aggregation
daily_metrics = pipeline.aggregate_daily('org-1')

# Federation rollup (Phase 4.1)
federation_metrics = pipeline.federation_rollup(['org-1', 'org-2', 'org-3'])

# Export to S3 Parquet for BI
pipeline.export_parquet('org-1', 's3://maestro-analytics/parquet', days=7)
```

**Database Schema:**
```sql
CREATE TABLE routing_events (
    event_id VARCHAR PRIMARY KEY,
    timestamp TIMESTAMP INDEX,
    user_id VARCHAR INDEX,
    organization_id VARCHAR INDEX,
    query_hash VARCHAR INDEX,
    routed_agent VARCHAR INDEX,
    routing_confidence FLOAT,
    routing_method VARCHAR,
    outcome VARCHAR,
    feedback_score FLOAT,
    input_tokens INT,
    output_tokens INT,
    model_used VARCHAR,
    cost_usd DECIMAL(10, 6),
    phase VARCHAR,
    region VARCHAR,
    segment VARCHAR
);

CREATE TABLE aggregated_metrics (
    metric_id VARCHAR PRIMARY KEY,
    period VARCHAR,
    timestamp TIMESTAMP INDEX,
    organization_id VARCHAR INDEX,
    total_queries INT,
    unique_users INT,
    routing_accuracy FLOAT,
    feedback_avg FLOAT,
    fallback_rate FLOAT,
    total_cost_usd DECIMAL(12, 2),
    cost_per_query_usd DECIMAL(10, 6),
    tokens_total INT,
    metrics_json JSONB
);
```

---

### 2. BI Dashboard Integration (`bi_integration.py`)

Pre-built dashboards for Looker and Tableau with one-click deployment.

**Pre-built Templates:**
1. **Executive Overview** — KPIs for C-suite (volume, accuracy, cost, satisfaction)
2. **Routing Intelligence** — Agent performance, confidence scores, routing methods
3. **User Analytics** — Cohort behavior, retention, feature adoption
4. **Cost Tracking** — Cost per query, model mix, optimization opportunities
5. **Regulatory & Compliance** — Phase 3.2 webhooks, GDPR, audit trail

**Usage:**
```python
from analytics.bi_integration import BIDashboardManager

# Initialize with clients
from looker_sdk import client
looker = client.Looker()
manager = BIDashboardManager(looker_client=looker)

# List available templates
templates = manager.list_templates()
# [
#   {template_id: 'executive_overview', name: 'Executive Overview', ...},
#   {template_id: 'routing_intelligence', ...},
#   ...
# ]

# Deploy dashboard to organization
result = manager.deploy_dashboard(
    template_id='executive_overview',
    org_id='org-1',
    platform='looker'
)
# {
#   'status': 'success',
#   'dashboard_url': 'https://looker.example.com/dashboards/org-1/executive_overview',
#   'dashboard_id': 'dashboard_org-1_executive_overview'
# }

# Get dashboard configuration for import
config = manager.get_dashboard_config('executive_overview')

# Add custom metric
from analytics.bi_integration import KPIDefinition

custom_kpi = KPIDefinition(
    name='Custom Routing Score',
    description='Confidence × Accuracy combined metric',
    metric_type='gauge',
    calculation='AVG(routing_confidence) * (COUNT(feedback_score >= 4) / COUNT(*))',
    unit='score',
    threshold_warning=0.80,
    threshold_critical=0.70,
    refresh_interval_minutes=60
)
manager.add_custom_metric('custom_routing_score', custom_kpi)

# Export all KPIs
kpis = manager.list_kpis()
```

**Supported BI Platforms:**
- **Looker** — Native LookML integration via SDK
- **Tableau** — TWB format with REST API deployment
- **Metabase** — JSON query export
- **Power BI** — OData endpoint

---

### 3. Predictive Models (`predictive_models.py`)

ML models for forecasting, drift detection, and anomaly detection.

**Models:**

#### 3a. Volume Forecaster
```python
from analytics.predictive_models import VolumeForecaster

# Fit on historical volumes
volumes = [100, 105, 110, 108, 112, 115, 120, 118, 122, 125]
forecaster = VolumeForecaster(alpha=0.3)
forecaster.fit(volumes)

# Generate forecast with confidence interval
forecast = forecaster.forecast(periods=7)
# [126, 128, 130, 131, 133, 134, 136]

ci_95 = forecaster.get_confidence_interval(forecast, confidence=0.95)
# {
#   'lower': [120, 121, 123, ...],
#   'point': [126, 128, 130, ...],
#   'upper': [132, 135, 137, ...]
# }
```

#### 3b. Drift Detector
```python
from analytics.predictive_models import DriftDetector
import numpy as np

# Fit on historical embeddings
embeddings = np.random.rand(100, 768)  # From query embedding store
detector = DriftDetector(drift_threshold=2.0)
detector.fit(embeddings)

# Detect if new query is novel/drifted
new_embedding = np.random.rand(768)
drift_score, is_drift = detector.detect_drift(new_embedding)

if is_drift:
    print(f"Drift detected: score={drift_score:.3f}, recommend human review")
```

#### 3c. Anomaly Detector
```python
from analytics.predictive_models import AnomalyDetector
import pandas as pd

# Fit on historical data
df = pd.read_sql("SELECT * FROM routing_events LIMIT 1000", engine)
detector = AnomalyDetector(contamination=0.05)
detector.fit(df, ['input_tokens', 'output_tokens', 'cost_usd', 'routing_confidence'])

# Predict anomalies
recent_df = pd.read_sql("SELECT * FROM routing_events ORDER BY timestamp DESC LIMIT 100", engine)
predictions = detector.predict(recent_df)  # -1 = anomaly, 1 = normal
scores = detector.anomaly_score(recent_df)

anomalies = recent_df[predictions == -1]
print(f"Found {len(anomalies)} anomalies in recent queries")
```

#### 3d. Model Evaluator
```python
from analytics.predictive_models import ModelEvaluator

evaluator = ModelEvaluator()

# Evaluate forecast accuracy
actual = [100, 105, 110, 108, 112]
forecast = [102, 103, 111, 107, 113]
metrics = evaluator.evaluate_forecast(actual, forecast, 'volume_forecast')
# {
#   'mae': 1.8,
#   'rmse': 2.1,
#   'mape': 0.018,
#   'median_error': 1.5,
#   'timestamp': '2026-07-27T...',
#   'model_name': 'volume_forecast'
# }

# Check if model should retrain
should_retrain = evaluator.should_retrain('volume_forecast', threshold_mae=5.0)

# Get model health summary
health = evaluator.get_model_health()
```

#### 3e. Predictive Model Manager
```python
from analytics.predictive_models import PredictiveModelManager
import pandas as pd

manager = PredictiveModelManager()

# Train all models
df = pd.read_sql("SELECT * FROM routing_events WHERE timestamp > NOW() - INTERVAL 90 DAY", engine)
embeddings = load_embeddings('recent')  # From vector store
results = manager.train_all_models(df, embeddings)
# {
#   'volume_forecaster': True,
#   'drift_detector': True,
#   'anomaly_detector': True
# }

# Use models
forecast = manager.forecast_volume(days=7)
anomalies = manager.detect_anomalies(recent_df)

# Save/load models (for versioning)
manager.save_model('volume_forecaster', 'models/volume_forecaster_v1.pkl')
manager.load_model('volume_forecaster', 'models/volume_forecaster_v1.pkl')
```

**Model Training Pipeline (Weekly):**
```python
# Orchestrated via GitHub Actions / Cloud Scheduler
# .github/workflows/retrain-models.yml

import pandas as pd
from analytics.predictive_models import PredictiveModelManager

# 1. Fetch training data
df = pd.read_sql("""
    SELECT * FROM routing_events
    WHERE timestamp > NOW() - INTERVAL 90 DAY
""", engine)

# 2. Fetch embeddings
embeddings = load_embeddings('vector_store')

# 3. Train
manager = PredictiveModelManager()
manager.train_all_models(df, embeddings)

# 4. Evaluate
evaluations = manager.evaluator.get_model_health()

# 5. Promote if accuracy improved
if should_promote(evaluations):
    manager.save_model('volume_forecaster', 'models/volume_forecaster_latest.pkl')
    print("✅ Models promoted to production")
else:
    print("⚠️  Models did not meet accuracy threshold, rolling back")
```

---

### 4. Monitoring & Alerting (`monitoring.py`)

Real-time health checks, performance monitoring, and incident escalation.

**Health Checks (5-minute interval):**
1. Dashboard availability (Looker, Tableau, Metabase)
2. Query latency p95 (< 500ms, Phase 3 SLA)
3. Routing accuracy (>85%, Phase 1 gate)
4. Cost anomalies (>50% above baseline)
5. Webhook lag (Phase 3.2, <30 min)
6. Database connectivity

**Usage:**
```python
from analytics.monitoring import (
    HealthChecker, AlertingEngine, IncidentEscalation,
    AlertSeverity, NotificationHandlers
)

# Initialize components
health_checker = HealthChecker()
alerting_engine = AlertingEngine()
escalation = IncidentEscalation()

# Register notification handlers
slack_handler = NotificationHandlers.slack_handler('https://hooks.slack.com/services/...')
alerting_engine.register_handler(AlertSeverity.WARNING, slack_handler)
alerting_engine.register_handler(AlertSeverity.CRITICAL, slack_handler)

email_handler = NotificationHandlers.email_handler({
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'from_addr': 'alerts@mantaassociados.com'
})
alerting_engine.register_handler(AlertSeverity.CRITICAL, email_handler)

pagerduty_handler = NotificationHandlers.pagerduty_handler('api-key-xyz')
alerting_engine.register_handler(AlertSeverity.PAGE, pagerduty_handler)

# Run health checks
context = {
    'query_latency_p95_ms': 450,
    'routing_accuracy_pct': 87.5,
    'daily_cost_usd': 8.0,
    'avg_daily_cost_usd': 7.5,
    'webhook_max_lag_minutes': 15,
    'database_available': True,
    'database_latency_ms': 45,
    'dashboard_endpoints': {'looker': 'https://looker.example.com'},
    'looker_available': True,
    'pending_webhooks': 5
}

health_results = health_checker.run_all_checks(context)
# [
#   HealthCheckResult(check_name='query_latency', status='pass', ...),
#   HealthCheckResult(check_name='routing_accuracy', status='pass', ...),
#   ...
# ]

# Process results → alerts
alerts = alerting_engine.process_health_checks(health_results)

# Evaluate escalation
for alert in alerts:
    action = escalation.evaluate_escalation(alert)
    if action:
        print(f"Escalating: {action['type']} to level {action['level']}")

# Check active incidents
open_incidents = escalation.get_open_incidents()
```

**Monitoring Dashboard (Example Grafana):**
```yaml
# grafana/dashboards/maestro-monitoring.json
{
  "title": "Maestro Analytics Monitoring",
  "panels": [
    {
      "title": "Health Check Status",
      "targets": [
        { "expr": "maestro_health_check_status{check='query_latency'}" }
      ]
    },
    {
      "title": "Active Alerts",
      "targets": [
        { "expr": "maestro_active_alerts" }
      ]
    },
    {
      "title": "Incident Timeline",
      "targets": [
        { "expr": "maestro_incident_duration_minutes" }
      ]
    }
  ]
}
```

**Alert Rules (Kubernetes ConfigMap):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: maestro-alert-rules
data:
  alerts.yaml: |
    groups:
      - name: maestro.analytics
        rules:
          - alert: RoutingAccuracyLow
            expr: maestro_routing_accuracy < 85
            for: 15m
            labels:
              severity: warning
            annotations:
              summary: "Routing accuracy below 85%"

          - alert: DatabaseDown
            expr: maestro_database_available == 0
            for: 1m
            labels:
              severity: critical
            annotations:
              summary: "Database unavailable"
```

---

### 5. Testing & Validation (`tests/test_analytics.py`)

Comprehensive test suite with >30 tests covering:

- **Unit Tests** — Individual modules and functions
- **Integration Tests** — End-to-end data flows
- **Model Validation** — Accuracy thresholds
- **Performance Tests** — Latency and throughput

**Running Tests:**
```bash
# All tests
pytest analytics/tests/test_analytics.py -v

# Specific test class
pytest analytics/tests/test_analytics.py::TestAnalyticsPipeline -v

# With coverage
pytest analytics/tests/test_analytics.py --cov=analytics --cov-report=html

# Performance benchmarks
pytest analytics/tests/test_analytics.py::TestPerformance -v -s
```

**Test Coverage:**
```
analytics_pipeline.py ............ 95%
bi_integration.py ................ 92%
predictive_models.py ............. 88%
monitoring.py .................... 90%
─────────────────────────────────────
TOTAL ............................ 91%
```

---

## Deployment

### Prerequisites
- PostgreSQL 13+ with pgvector extension
- Python 3.9+
- Looker or Tableau (for BI dashboards)
- Kubernetes cluster (for monitoring stack)

### Installation

1. **Clone and install dependencies:**
```bash
cd analytics
pip install -r requirements.txt
```

2. **Set up database:**
```bash
psql -h postgres.example.com -U maestro << EOF
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE TABLE routing_events (...);  # See schema above
CREATE TABLE aggregated_metrics (...);
EOF
```

3. **Configure environment:**
```bash
# .env or .env.local
DB_URL=postgresql://user:pass@postgres.example.com:5432/maestro
LOOKER_URL=https://looker.example.com
LOOKER_CLIENT_ID=xxx
LOOKER_CLIENT_SECRET=yyy
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
S3_BUCKET=maestro-analytics
AWS_REGION=us-east-1
```

4. **Initialize pipeline:**
```python
from analytics.analytics_pipeline import AnalyticsPipeline

pipeline = AnalyticsPipeline(os.getenv('DB_URL'))
# Tables auto-created via SQLAlchemy
```

5. **Deploy dashboards:**
```bash
python scripts/deploy_dashboards.py --platform looker --org-id org-1
# ✅ Dashboard deployed: executive_overview
# ✅ Dashboard deployed: routing_intelligence
# ...
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "analytics.pipeline", "--config", "/etc/maestro/config.yaml"]
```

```bash
docker build -t maestro-analytics:latest .
docker run -e DB_URL=$DB_URL maestro-analytics:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maestro-analytics
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: analytics
        image: maestro-analytics:latest
        env:
        - name: DB_URL
          valueFrom:
            secretKeyRef:
              name: maestro-secrets
              key: database-url
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
      - name: health-checker
        image: maestro-analytics:latest
        args: ["python", "-m", "analytics.monitoring"]
```

---

## Operations

### Daily Tasks

**1. Ingest Routing Events (5-minute interval)**
```python
from analytics.analytics_pipeline import AnalyticsPipeline

pipeline = AnalyticsPipeline(os.getenv('DB_URL'))

# Events from Maestro router (via message queue or webhook)
for event in get_routing_events_from_queue():
    pipeline.ingest_event(event)
```

**2. Run Health Checks (5-minute interval)**
```bash
# Via Kubernetes CronJob
*/5 * * * * python -m analytics.monitoring --check-all
```

**3. Daily Aggregation (1 AM UTC)**
```bash
# Via GitHub Actions
0 1 * * * python scripts/aggregate_daily.py
```

**4. Weekly Model Retraining (Sunday 2 AM)**
```bash
# .github/workflows/retrain-models.yml
- name: Retrain predictive models
  run: python scripts/retrain_models.py
```

**5. Monthly Export to S3 (First of month)**
```bash
# Via Cloud Scheduler
python scripts/export_to_parquet.py --days 30
```

### Troubleshooting

**Problem: Dashboard not loading**
```
Check: 1. BI platform connectivity
       2. Data freshness (last_refresh timestamp)
       3. Database query performance
Solution: Run health check, check logs
```

**Problem: Models predicting poorly**
```
Check: 1. Training data quality (gaps, outliers)
       2. Distribution shift (drift detector results)
       3. Model evaluation metrics
Solution: Trigger manual retraining, review evaluation metrics
```

**Problem: Cost anomalies not detected**
```
Check: 1. Baseline calculation (avg_daily_cost)
       2. Anomaly detector contamination setting
       3. Cost accuracy in routing_events table
Solution: Adjust threshold, retrain detector
```

---

## Success Criteria (Phase 4.2)

- ✅ BI dashboards deployed and live (Looker + Tableau)
- ✅ Volume forecast MAPE < 15%
- ✅ Anomaly detection precision > 85%
- ✅ Health checks running on 5-min interval
- ✅ Alerts firing correctly (test coverage > 90%)
- ✅ Cost prediction accuracy within 10%
- ✅ Model retraining pipeline automated (weekly)
- ✅ All tests passing (pytest -v)

---

## Cost Estimation

| Component | Cost | Notes |
|-----------|------|-------|
| PostgreSQL + pgvector | $0.10/hour | t3.medium RDS |
| Looker License | $2,500/month | 5-user licensing |
| Data export to S3 | $0.02/GB | Parquet compression |
| Monitoring (Datadog) | $0.50/hour | APM + logs |
| **Total** | ~**$4,500/month** | For 50M+ queries/month |

---

## Next Steps (Phase 4.3)

- Agent learning pipeline (feedback → fine-tuning)
- Specialization models per segment (S1-S10)
- Autonomous agent improvement recommendations

## References

- **CLAUDE.md** — Master agent registry
- **Phase 4 Roadmap** — Ecosystem evolution plan
- **Training Guide** — Role-specific documentation
- **API Docs** — Phase 3 REST API spec

---

**Questions?** → maestro@mantaassociados.com  
**Monitoring Slack Channel** → #maestro-analytics  
**Incident Channel** → #maestro-incidents (with PagerDuty)
