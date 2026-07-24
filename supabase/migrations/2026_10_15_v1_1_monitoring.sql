-- Migration: Supabase Evolution Phase 1.1 - Monitoring
-- Version: 1.1.0
-- Date: 2026-10-15
-- Description: Add real-time metrics, alerts, and cost tracking
-- Estimated Duration: 5 minutes
-- Downtime: None (CONCURRENT index creation)

BEGIN;

-- ========================================================================
-- 1.1.1: REAL-TIME METRICS TABLE
-- ========================================================================
-- Stores minute-granularity metrics for dashboards
-- Populated by triggers from feedback_logs and agent_scores

CREATE TABLE IF NOT EXISTS cag_metrics_realtime (
    id BIGSERIAL PRIMARY KEY,
    minute_bucket TIMESTAMP NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    intent_label VARCHAR(255),
    total_queries INT DEFAULT 0,
    correct_selections INT DEFAULT 0,
    incorrect_selections INT DEFAULT 0,
    avg_latency_ms NUMERIC(10,2) DEFAULT 0.0,
    p95_latency_ms NUMERIC(10,2) DEFAULT 0.0,
    p99_latency_ms NUMERIC(10,2) DEFAULT 0.0,
    error_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT pk_metrics_realtime PRIMARY KEY (id),
    CONSTRAINT uq_metrics_realtime UNIQUE (minute_bucket, agent_slug, intent_label)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_realtime_bucket
    ON cag_metrics_realtime(minute_bucket DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_realtime_agent
    ON cag_metrics_realtime(agent_slug, minute_bucket DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_realtime_intent
    ON cag_metrics_realtime(intent_label, minute_bucket DESC);

-- ========================================================================
-- 1.1.2: ALERTS & ANOMALIES TABLE
-- ========================================================================
-- Triggered when accuracy drops, latency spikes, error rates high

CREATE TABLE IF NOT EXISTS cag_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(100) NOT NULL, -- 'accuracy_drop', 'latency_spike', 'error_rate_high'
    agent_slug VARCHAR(255),
    intent_label VARCHAR(255),
    severity VARCHAR(50) NOT NULL, -- 'info', 'warning', 'critical'
    message TEXT NOT NULL,
    metric_name VARCHAR(255),
    metric_value NUMERIC(10,3),
    threshold NUMERIC(10,3),
    triggered_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP,
    CONSTRAINT pk_alerts PRIMARY KEY (id),
    CONSTRAINT uq_alert_trigger UNIQUE(alert_type, agent_slug, intent_label, triggered_at)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_severity
    ON cag_alerts(severity, triggered_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_agent
    ON cag_alerts(agent_slug, triggered_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_alerts_resolved
    ON cag_alerts(resolved_at) WHERE resolved_at IS NULL;

-- ========================================================================
-- 1.1.3: COST TRACKING TABLE
-- ========================================================================
-- Daily cost breakdown by agent, including LLM, storage, compute

CREATE TABLE IF NOT EXISTS cag_costs (
    id BIGSERIAL PRIMARY KEY,
    date_bucket DATE NOT NULL,
    agent_slug VARCHAR(255) NOT NULL,
    intent_label VARCHAR(255),
    llm_calls INT DEFAULT 0, -- calls to Claude ranking/synthesis
    llm_cost_usd NUMERIC(12,4) DEFAULT 0.0000, -- ~$0.003 per call
    storage_gb NUMERIC(10,3) DEFAULT 0.000,
    storage_cost_usd NUMERIC(12,4) DEFAULT 0.0000, -- $0.25/GB/month
    compute_hours NUMERIC(10,2) DEFAULT 0.0,
    compute_cost_usd NUMERIC(12,4) DEFAULT 0.0000, -- per hour
    inference_calls INT DEFAULT 0,
    inference_cost_usd NUMERIC(12,4) DEFAULT 0.0000,
    total_cost_usd NUMERIC(12,4) DEFAULT 0.0000,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT pk_costs PRIMARY KEY (id),
    CONSTRAINT uq_costs UNIQUE (date_bucket, agent_slug, intent_label)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_costs_date
    ON cag_costs(date_bucket DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_costs_agent
    ON cag_costs(agent_slug, date_bucket DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_costs_total
    ON cag_costs(total_cost_usd DESC);

-- ========================================================================
-- ADD MISSING INDICES TO EXISTING TABLES
-- ========================================================================
-- These improve query performance for common access patterns

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_scores_agent_date
    ON cag_agent_scores(agent_slug, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agent_scores_hit
    ON cag_agent_scores(hit, agent_slug) WHERE hit IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feedback_logs_intent
    ON cag_feedback_logs(query_intent, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feedback_logs_rating
    ON cag_feedback_logs(user_rating, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feedback_logs_session_date
    ON cag_feedback_logs(session_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_routing_metrics_agent
    ON cag_routing_metrics(agent_slug, date_bucket DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_routing_metrics_accuracy
    ON cag_routing_metrics(
        (correct_selections::FLOAT / NULLIF(correct_selections + incorrect_selections, 0))
    ) WHERE correct_selections + incorrect_selections > 0;

-- ========================================================================
-- HELPER FUNCTIONS
-- ========================================================================

-- Function: Calculate accuracy for an agent on a given date
CREATE OR REPLACE FUNCTION fn_agent_accuracy_on_date(
    p_agent_slug VARCHAR,
    p_date DATE
) RETURNS NUMERIC AS $$
DECLARE
    v_accuracy NUMERIC;
BEGIN
    SELECT ROUND(
        100.0 * correct_selections / NULLIF(correct_selections + incorrect_selections, 0),
        2
    ) INTO v_accuracy
    FROM cag_routing_metrics
    WHERE agent_slug = p_agent_slug
      AND date_bucket = p_date;

    RETURN COALESCE(v_accuracy, 0.0);
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: Get top N agents by feedback rating
CREATE OR REPLACE FUNCTION fn_top_agents_by_rating(
    p_limit INT DEFAULT 10,
    p_days INT DEFAULT 7
) RETURNS TABLE (
    agent_slug VARCHAR,
    avg_rating NUMERIC,
    feedback_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        fl.selected_agents[1] as agent_slug,
        ROUND(AVG(fl.user_rating), 2) as avg_rating,
        COUNT(*) as feedback_count
    FROM cag_feedback_logs fl
    WHERE fl.created_at > NOW() - (p_days || ' days')::INTERVAL
      AND fl.selected_agents IS NOT NULL
      AND array_length(fl.selected_agents, 1) > 0
    GROUP BY fl.selected_agents[1]
    ORDER BY avg_rating DESC, feedback_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: Calculate daily cost summary
CREATE OR REPLACE FUNCTION fn_cost_summary(
    p_start_date DATE,
    p_end_date DATE
) RETURNS TABLE (
    date_bucket DATE,
    total_cost_usd NUMERIC,
    llm_cost_usd NUMERIC,
    storage_cost_usd NUMERIC,
    compute_cost_usd NUMERIC,
    agent_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.date_bucket,
        SUM(c.total_cost_usd)::NUMERIC as total_cost_usd,
        SUM(c.llm_cost_usd)::NUMERIC as llm_cost_usd,
        SUM(c.storage_cost_usd)::NUMERIC as storage_cost_usd,
        SUM(c.compute_cost_usd)::NUMERIC as compute_cost_usd,
        COUNT(DISTINCT c.agent_slug)::INT as agent_count
    FROM cag_costs c
    WHERE c.date_bucket >= p_start_date
      AND c.date_bucket <= p_end_date
    GROUP BY c.date_bucket
    ORDER BY c.date_bucket DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ========================================================================
-- TRIGGER: Auto-populate metrics from feedback_logs
-- ========================================================================
-- Every time feedback is logged, update the realtime metrics

CREATE OR REPLACE FUNCTION fn_update_realtime_metrics()
RETURNS TRIGGER AS $$
DECLARE
    v_minute_bucket TIMESTAMP;
    v_first_agent VARCHAR;
BEGIN
    v_minute_bucket := DATE_TRUNC('minute', NEW.created_at);
    v_first_agent := NEW.selected_agents[1];

    INSERT INTO cag_metrics_realtime (
        minute_bucket,
        agent_slug,
        intent_label,
        total_queries
    ) VALUES (
        v_minute_bucket,
        v_first_agent,
        NEW.query_intent,
        1
    )
    ON CONFLICT (minute_bucket, agent_slug, intent_label)
    DO UPDATE SET
        total_queries = total_queries + 1,
        updated_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_feedback_to_metrics
AFTER INSERT ON cag_feedback_logs
FOR EACH ROW
EXECUTE FUNCTION fn_update_realtime_metrics();

-- ========================================================================
-- TRIGGER: Check for alert conditions
-- ========================================================================
-- When metrics show degradation, create alerts

CREATE OR REPLACE FUNCTION fn_check_accuracy_alert()
RETURNS TRIGGER AS $$
DECLARE
    v_accuracy NUMERIC;
    v_threshold NUMERIC := 0.80; -- Alert if accuracy drops below 80%
BEGIN
    v_accuracy :=
        CASE
            WHEN (NEW.correct_selections + NEW.incorrect_selections) > 0
            THEN NEW.correct_selections::FLOAT / (NEW.correct_selections + NEW.incorrect_selections)
            ELSE 1.0
        END;

    IF v_accuracy < v_threshold THEN
        INSERT INTO cag_alerts (
            alert_type,
            agent_slug,
            severity,
            message,
            metric_name,
            metric_value,
            threshold
        ) VALUES (
            'accuracy_drop',
            NEW.agent_slug,
            CASE WHEN v_accuracy < 0.70 THEN 'critical' ELSE 'warning' END,
            'Accuracy dropped to ' || ROUND(v_accuracy * 100, 1) || '%',
            'accuracy',
            v_accuracy,
            v_threshold
        )
        ON CONFLICT DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_accuracy_alert
AFTER INSERT OR UPDATE ON cag_routing_metrics
FOR EACH ROW
EXECUTE FUNCTION fn_check_accuracy_alert();

-- ========================================================================
-- INITIAL DATA
-- ========================================================================
-- Populate historical metrics from existing feedback logs (last 7 days)

INSERT INTO cag_metrics_realtime (
    minute_bucket,
    agent_slug,
    intent_label,
    total_queries
)
SELECT
    DATE_TRUNC('minute', created_at) as minute_bucket,
    selected_agents[1] as agent_slug,
    query_intent,
    COUNT(*) as total_queries
FROM cag_feedback_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY minute_bucket, agent_slug, query_intent
ON CONFLICT (minute_bucket, agent_slug, intent_label) DO NOTHING;

-- ========================================================================
-- VERIFICATION QUERIES
-- ========================================================================
-- Run these to verify migration success

/*
-- Check table creation
SELECT tablename FROM pg_tables
WHERE tablename LIKE 'cag_metrics_%'
   OR tablename LIKE 'cag_alerts'
   OR tablename LIKE 'cag_costs';

-- Check indices
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE tablename LIKE 'cag_%'
ORDER BY tablename, indexname;

-- Check function creation
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE 'fn_%';

-- Check triggers
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
  AND event_object_table LIKE 'cag_%';

-- Sample data from new tables
SELECT * FROM cag_metrics_realtime LIMIT 5;
SELECT * FROM cag_alerts LIMIT 5;
SELECT * FROM cag_costs LIMIT 5;
*/

COMMIT;

-- ========================================================================
-- ROLLBACK SCRIPT (if needed)
-- ========================================================================
/*
BEGIN;

DROP TRIGGER IF EXISTS trg_feedback_to_metrics ON cag_feedback_logs;
DROP TRIGGER IF EXISTS trg_accuracy_alert ON cag_routing_metrics;

DROP FUNCTION IF EXISTS fn_update_realtime_metrics();
DROP FUNCTION IF EXISTS fn_check_accuracy_alert();
DROP FUNCTION IF EXISTS fn_agent_accuracy_on_date(VARCHAR, DATE);
DROP FUNCTION IF EXISTS fn_top_agents_by_rating(INT, INT);
DROP FUNCTION IF EXISTS fn_cost_summary(DATE, DATE);

DROP INDEX IF EXISTS idx_metrics_realtime_bucket;
DROP INDEX IF EXISTS idx_metrics_realtime_agent;
DROP INDEX IF EXISTS idx_metrics_realtime_intent;
DROP INDEX IF EXISTS idx_alerts_severity;
DROP INDEX IF EXISTS idx_alerts_agent;
DROP INDEX IF EXISTS idx_alerts_resolved;
DROP INDEX IF EXISTS idx_costs_date;
DROP INDEX IF EXISTS idx_costs_agent;
DROP INDEX IF EXISTS idx_costs_total;
DROP INDEX IF EXISTS idx_agent_scores_agent_date;
DROP INDEX IF EXISTS idx_agent_scores_hit;
DROP INDEX IF EXISTS idx_feedback_logs_intent;
DROP INDEX IF EXISTS idx_feedback_logs_rating;
DROP INDEX IF EXISTS idx_feedback_logs_session_date;
DROP INDEX IF EXISTS idx_routing_metrics_agent;
DROP INDEX IF EXISTS idx_routing_metrics_accuracy;

DROP TABLE IF EXISTS cag_metrics_realtime;
DROP TABLE IF EXISTS cag_alerts;
DROP TABLE IF EXISTS cag_costs;

COMMIT;
*/
