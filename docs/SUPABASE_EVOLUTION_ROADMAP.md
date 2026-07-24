# Supabase Evolution Roadmap — CAG v5.0+

**Status:** Planning Phase (v1.0 → v5.0 over 18 months)  
**Ticket:** MNT-2026-CAG-SUPABASE-EVOLUTION  
**Author:** CAG Architecture Team  
**Last Updated:** 2026-07-22

---

## Executive Summary

Roadmap para evoluir o Supabase de **7 tabelas (v1.0 Shadow)** → **15+ tabelas (v5.0 Enterprise)** com otimizações para suportar:
- 100M+ queries/year (shadow testing)
- 1M+ active feedback logs/month (production)
- Real-time ML model retraining
- Multi-region failover
- Sub-100ms latency p95

---

## Phase Timeline

```
Jul-Set 2026  │ v1.0: Shadow (7 tables, single region)
              │
Out-Dez 2026  │ v1.1: Monitoring (add metrics aggregation)
              │ v1.2: Partitioning (table sharding for scale)
              │
Jan-Mar 2027  │ v2.0: Pilot (add real-time sync, webhooks)
              │
Abr-Jun 2027  │ v2.1: Multi-region (read replicas)
              │
Jul-Set 2027  │ v3.0: GA (full production hardening)
              │
              ▼
```

---

## Current State (v1.0 - Shadow)

### Tables
```
7 core tables:
├─ cag_intent_models       (classifier versions)
├─ cag_agent_scores        (hits/misses matrix)
├─ cag_feedback_logs       (user ratings)
├─ cag_routing_metrics     (daily aggregation)
├─ cag_agent_pool          (agent registry)
├─ cag_intent_classes      (intent definitions)
└─ cag_query_cache         (embedding cache)

Schema Size:  ~50 MB (initial data)
Growth Rate:  ~1-5 MB/month (shadow testing)
Queries/sec:  ~10 (test load)
```

### Indices
```
Current: 8 indices (basic)
├─ agent_slug (cag_agent_scores)
├─ query_intent (cag_agent_scores)
├─ session_id (cag_feedback_logs)
├─ created_at (cag_feedback_logs)
├─ date_bucket (cag_routing_metrics)
├─ query_hash (cag_query_cache)
├─ expires_at (cag_query_cache)
└─ intent_label (cag_intent_classes)
```

### Limitations
- ❌ No partitioning (single partition)
- ❌ No full-text search (keyword search slow)
- ❌ No materialized views (aggregations run live)
- ❌ No pub/sub (real-time sync manual)
- ❌ No backup replication (single region)
- ❌ No audit logging (compliance risk)

---

## Phase 1.1 — Monitoring (Oct 2026)

### Goals
- Real-time dashboard for accuracy metrics
- Alert system for classifier degradation
- Cost tracking per agent/intent

### New Tables
```sql
-- 1.1.1: Real-time metrics aggregation
CREATE TABLE cag_metrics_realtime (
    id BIGSERIAL PRIMARY KEY,
    minute_bucket TIMESTAMP NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    intent_label VARCHAR(255),
    total_queries INT,
    correct_selections INT,
    avg_latency_ms NUMERIC,
    p95_latency_ms NUMERIC,
    p99_latency_ms NUMERIC,
    error_count INT DEFAULT 0,
    UNIQUE(minute_bucket, agent_slug, intent_label)
);
CREATE INDEX idx_metrics_realtime_bucket ON cag_metrics_realtime(minute_bucket DESC);
CREATE INDEX idx_metrics_realtime_agent ON cag_metrics_realtime(agent_slug, minute_bucket DESC);

-- 1.1.2: Alerts & anomalies
CREATE TABLE cag_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(100), -- 'accuracy_drop', 'latency_spike', 'error_rate_high'
    agent_slug VARCHAR(255),
    severity VARCHAR(50), -- 'info', 'warning', 'critical'
    message TEXT,
    metric_value NUMERIC,
    threshold NUMERIC,
    triggered_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    UNIQUE(alert_type, agent_slug, triggered_at)
);
CREATE INDEX idx_alerts_severity ON cag_alerts(severity, triggered_at DESC);

-- 1.1.3: Cost tracking
CREATE TABLE cag_costs (
    id BIGSERIAL PRIMARY KEY,
    date_bucket DATE NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    intent_label VARCHAR(255),
    llm_calls INT, -- calls to Claude/ranking
    llm_cost_usd NUMERIC(10,4), -- ~$0.003 per call
    storage_gb NUMERIC(10,2),
    compute_hours NUMERIC(10,2),
    total_cost_usd NUMERIC(10,4),
    UNIQUE(date_bucket, agent_slug)
);
```

### Indices to Add
```sql
CREATE INDEX idx_agent_scores_agent_date ON cag_agent_scores(agent_slug, created_at DESC);
CREATE INDEX idx_feedback_logs_intent ON cag_feedback_logs(query_intent, created_at DESC);
CREATE INDEX idx_feedback_logs_rating ON cag_feedback_logs(user_rating, created_at DESC);
CREATE INDEX idx_routing_metrics_agent ON cag_routing_metrics(agent_slug, date_bucket DESC);
```

### Migration Script
```sql
-- Run after v1.0 deployment
-- Estimated time: ~5 minutes
-- Downtime: None (CREATE INDEX CONCURRENTLY)

BEGIN;

-- 1.1.1: Create realtime metrics table
CREATE TABLE cag_metrics_realtime (
    id BIGSERIAL PRIMARY KEY,
    minute_bucket TIMESTAMP NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    intent_label VARCHAR(255),
    total_queries INT,
    correct_selections INT,
    avg_latency_ms NUMERIC,
    p95_latency_ms NUMERIC,
    p99_latency_ms NUMERIC,
    error_count INT DEFAULT 0,
    UNIQUE(minute_bucket, agent_slug, intent_label)
);

CREATE INDEX CONCURRENTLY idx_metrics_realtime_bucket 
    ON cag_metrics_realtime(minute_bucket DESC);
CREATE INDEX CONCURRENTLY idx_metrics_realtime_agent 
    ON cag_metrics_realtime(agent_slug, minute_bucket DESC);

-- 1.1.2: Create alerts table
CREATE TABLE cag_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(100),
    agent_slug VARCHAR(255),
    severity VARCHAR(50),
    message TEXT,
    metric_value NUMERIC,
    threshold NUMERIC,
    triggered_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    UNIQUE(alert_type, agent_slug, triggered_at)
);

CREATE INDEX CONCURRENTLY idx_alerts_severity 
    ON cag_alerts(severity, triggered_at DESC);

-- 1.1.3: Create costs table
CREATE TABLE cag_costs (
    id BIGSERIAL PRIMARY KEY,
    date_bucket DATE NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    intent_label VARCHAR(255),
    llm_calls INT,
    llm_cost_usd NUMERIC(10,4),
    storage_gb NUMERIC(10,2),
    compute_hours NUMERIC(10,2),
    total_cost_usd NUMERIC(10,4),
    UNIQUE(date_bucket, agent_slug)
);

-- Add missing indices to existing tables
CREATE INDEX CONCURRENTLY idx_agent_scores_agent_date 
    ON cag_agent_scores(agent_slug, created_at DESC);
CREATE INDEX CONCURRENTLY idx_feedback_logs_intent 
    ON cag_feedback_logs(query_intent, created_at DESC);
CREATE INDEX CONCURRENTLY idx_feedback_logs_rating 
    ON cag_feedback_logs(user_rating, created_at DESC);
CREATE INDEX CONCURRENTLY idx_routing_metrics_agent 
    ON cag_routing_metrics(agent_slug, date_bucket DESC);

-- Trigger to auto-populate realtime metrics (example)
CREATE OR REPLACE FUNCTION populate_metrics_realtime()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO cag_metrics_realtime (minute_bucket, agent_slug, intent_label, total_queries)
  VALUES (DATE_TRUNC('minute', NEW.created_at), NEW.agent_slug, NEW.query_intent, 1)
  ON CONFLICT(minute_bucket, agent_slug, intent_label) 
  DO UPDATE SET total_queries = total_queries + 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_feedback_to_metrics
AFTER INSERT ON cag_feedback_logs
FOR EACH ROW
EXECUTE FUNCTION populate_metrics_realtime();

COMMIT;
```

---

## Phase 1.2 — Partitioning & Sharding (Dec 2026)

### Goals
- Support 100M+ queries/year (1k QPS peak)
- Reduce query latency for large tables
- Enable time-based data retention

### Strategy: Range Partitioning by Time

```sql
-- Partition cag_feedback_logs by month
ALTER TABLE cag_feedback_logs
PARTITION BY RANGE (DATE_TRUNC('month', created_at));

CREATE TABLE cag_feedback_logs_2026_07 PARTITION OF cag_feedback_logs
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

CREATE TABLE cag_feedback_logs_2026_08 PARTITION OF cag_feedback_logs
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
    
-- Continue monthly...
```

### New Tables for Partitioning
```sql
-- Hash partition for cag_agent_scores (by agent_slug)
ALTER TABLE cag_agent_scores
PARTITION BY HASH (agent_slug);

CREATE TABLE cag_agent_scores_0 PARTITION OF cag_agent_scores
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE cag_agent_scores_1 PARTITION OF cag_agent_scores
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE cag_agent_scores_2 PARTITION OF cag_agent_scores
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE cag_agent_scores_3 PARTITION OF cag_agent_scores
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### Expected Results
```
Before (v1.0):
├─ cag_feedback_logs: 500K rows, 150ms query
├─ Sequential scan when no index match
└─ Single partition = hotspot

After (v1.2):
├─ cag_feedback_logs_2026_07: 50K rows, 5ms query
├─ cag_feedback_logs_2026_08: 60K rows, 6ms query
├─ Partition pruning = 10× faster
└─ Old partitions can be archived
```

---

## Phase 2.0 — Real-Time Sync & Webhooks (Jan 2027)

### Goals
- Live dashboard updates (Supabase Realtime)
- Webhook triggers for alerts
- Event streaming to ML pipeline

### New Tables
```sql
-- Event log for audit trail + webhooks
CREATE TABLE cag_events (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100), -- 'feedback_received', 'model_trained', 'accuracy_alert'
    resource_type VARCHAR(100), -- 'agent', 'intent', 'query'
    resource_id VARCHAR(255),
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_events_created ON cag_events(created_at DESC);
CREATE INDEX idx_events_type ON cag_events(event_type, created_at DESC);

-- Webhook subscriptions
CREATE TABLE cag_webhooks (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    endpoint_url VARCHAR(2048) NOT NULL,
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    retry_count INT DEFAULT 0,
    last_triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_webhooks_event_type ON cag_webhooks(event_type);
```

### Realtime Subscriptions (Client-Side)
```javascript
// Example: Live dashboard update
const subscription = client
  .from('cag_metrics_realtime')
  .on('*', (payload) => {
    // Update dashboard in real-time
    updateMetricsDisplay(payload.new);
  })
  .subscribe();
```

---

## Phase 2.1 — Multi-Region (Apr 2027)

### Goals
- Reduced latency for users in different regions
- High availability (99.99% SLA)
- Disaster recovery

### Architecture
```
Primary (US-East):
├─ Write master
├─ Full schema
└─ Primary backups

Replica (EU-West):
├─ Read-only
├─ Async replication lag ~100ms
└─ Failover ready

Replica (SA-South):
├─ Read-only
├─ Async replication lag ~200ms
└─ Failover ready
```

### Configuration
```sql
-- Enable logical replication on primary
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_wal_senders = 10;

-- Create publication for subscribers
CREATE PUBLICATION cag_pub FOR ALL TABLES;

-- On replica
CREATE SUBSCRIPTION cag_sub CONNECTION 'primary_connection_string'
PUBLICATION cag_pub;
```

---

## Phase 3.0 — Enterprise Hardening (Jul 2027)

### Goals
- HIPAA/LGPD compliance
- Advanced audit logging
- Data retention policies
- Encryption at rest + transit

### New Tables
```sql
-- Audit trail (immutable log)
CREATE TABLE cag_audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(255),
    operation VARCHAR(50), -- INSERT, UPDATE, DELETE
    user_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMP DEFAULT NOW()
) WITH (fillfactor = 100);

-- Data retention policies
CREATE TABLE cag_retention_policies (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(255),
    retention_days INT, -- 90, 365, 730, NULL (forever)
    archive_destination VARCHAR(255), -- S3 bucket
    is_active BOOLEAN DEFAULT TRUE
);

-- Encryption keys (managed via Supabase Vault)
CREATE TABLE cag_encryption_keys (
    id BIGSERIAL PRIMARY KEY,
    key_name VARCHAR(255),
    algorithm VARCHAR(50), -- 'AES-256-GCM'
    rotation_enabled BOOLEAN DEFAULT TRUE,
    rotated_at TIMESTAMP,
    next_rotation TIMESTAMP
);
```

### Compliance Features
```sql
-- GDPR: Right to be forgotten
CREATE FUNCTION gdpr_delete_user_data(user_id VARCHAR)
RETURNS void AS $$
BEGIN
  DELETE FROM cag_feedback_logs WHERE session_id LIKE user_id || '_%';
  DELETE FROM cag_audit_log WHERE user_id = $1;
  -- Keep cag_agent_scores (anonymized)
END;
$$ LANGUAGE plpgsql;

-- LGPD: Data minimization (delete old feedback after 1 year)
CREATE FUNCTION archive_old_feedback()
RETURNS void AS $$
BEGIN
  INSERT INTO cag_feedback_logs_archive 
  SELECT * FROM cag_feedback_logs 
  WHERE created_at < NOW() - INTERVAL '1 year';
  
  DELETE FROM cag_feedback_logs 
  WHERE created_at < NOW() - INTERVAL '1 year';
END;
$$ LANGUAGE plpgsql;
```

---

## Data Growth Projections

### Shadow Phase (v1.0-1.2)
```
Month 1-3 (Jul-Sep 2026):
├─ Queries: 100K
├─ Feedback logs: 10K
├─ Storage: 50 MB
└─ Cost: ~$100/month

Month 4-6 (Oct-Dec 2026):
├─ Queries: 500K
├─ Feedback logs: 50K
├─ Storage: 200 MB
└─ Cost: ~$200/month
```

### Pilot Phase (v2.0)
```
Month 7-12 (Jan-Jun 2027):
├─ Queries: 5M (50K QPS peak)
├─ Feedback logs: 500K
├─ Storage: 2 GB
├─ Replication: 3 regions
└─ Cost: ~$500/month
```

### GA Phase (v3.0)
```
Year 2 (Jul 2027+):
├─ Queries: 50M (100K QPS peak)
├─ Feedback logs: 5M
├─ Storage: 20 GB
├─ Active archive: 100 GB (S3)
└─ Cost: ~$2,000/month
```

---

## Performance Targets

| Metric | v1.0 | v1.2 | v2.0 | v3.0 |
|--------|------|------|------|------|
| **Query latency (p95)** | 200ms | 50ms | 20ms | <10ms |
| **Write throughput** | 10 QPS | 100 QPS | 1K QPS | 10K QPS |
| **Availability** | 99.0% | 99.5% | 99.9% | 99.99% |
| **RTO** | 4 hours | 2 hours | 15 min | <5 min |
| **RPO** | 1 hour | 15 min | 1 min | <30s |
| **Storage** | 50 MB | 500 MB | 2 GB | 20 GB |

---

## Backup Strategy

### v1.0 (Shadow)
```
Daily backups → AWS S3
├─ Retention: 30 days
├─ RPO: 24 hours
└─ RTO: 4 hours (restore)
```

### v2.0 (Pilot)
```
Continuous replication (3 regions)
├─ Primary → Replica 1: ~100ms lag
├─ Primary → Replica 2: ~200ms lag
├─ RTO: <5 minutes (failover)
└─ RPO: ~1 minute
```

### v3.0 (GA)
```
PITR (Point-in-Time Recovery)
├─ 30-day retention
├─ Incremental backups every 6 hours
├─ Full backups daily
└─ RTO: <1 minute (restore to any point)
```

---

## Cost Optimization

### Storage
```
Compression:
├─ Enable JSONB compression (15% reduction)
├─ Archive feedback logs > 1 year to S3
└─ Estimated savings: 30-40%

Indexing:
├─ Partial indexes (WHERE is_active = true)
├─ Drop unused indices
└─ Estimated savings: 10-15%
```

### Compute
```
Query optimization:
├─ Materialized views for daily metrics
├─ Cache frequently-accessed data (Redis)
├─ Batch inserts instead of individual rows
└─ Estimated savings: 20-25%

Caching:
├─ cag_intent_classes (static)
├─ cag_agent_pool (semi-static)
├─ cag_routing_metrics (aggregate once/day)
└─ Estimated savings: 15-20%
```

---

## Monitoring & Observability

### Key Metrics
```sql
-- Query to monitor health
SELECT 
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as feedback_count,
  AVG(user_rating) as avg_rating,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY confidence_score) as p95_confidence
FROM cag_feedback_logs
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;

-- Cost tracking
SELECT 
  DATE_TRUNC('day', created_at) as day,
  SUM(llm_cost_usd) as llm_cost,
  SUM(storage_gb * 0.25) as storage_cost,  -- $0.25/GB/month
  SUM(llm_cost_usd) + SUM(storage_gb * 0.25) as total_daily_cost
FROM cag_costs
GROUP BY day
ORDER BY day DESC;
```

### Dashboards
1. **Real-time Metrics** (1-min granularity)
2. **Daily Summary** (24-hour view)
3. **Cost Dashboard** (per-agent tracking)
4. **Health Dashboard** (latency, errors, uptime)

---

## Rollback Plan

If migration fails:

```
v1.1 Rollback (add monitoring):
├─ DROP TABLE cag_metrics_realtime;
├─ DROP TABLE cag_alerts;
├─ DROP TABLE cag_costs;
└─ Restore from backup (< 5 min)

v1.2 Rollback (partitioning):
├─ ALTER TABLE cag_feedback_logs DETACH PARTITION ...;
├─ Merge partitions back
└─ Estimated time: 30 min
```

---

## Success Criteria

✅ v1.0: Deploy successfully, no data loss  
✅ v1.1: Dashboard live, <100ms latency for metrics  
✅ v1.2: Support 1K QPS, p95 latency <50ms  
✅ v2.0: 99.9% availability, webhooks working  
✅ v2.1: Multi-region failover tested (<5min)  
✅ v3.0: HIPAA/LGPD compliant, <10ms latency  

---

## Owner & Contact

- **Data Architect:** CAG Team
- **DBA:** Manta Infrastructure
- **Approver:** MN (VP Eng)
- **Review Cadence:** Quarterly

---

**Next Step:** Approve Phase 1.1 migration script for Oct deployment
