-- Maestro APScheduler v5.0 — PostgreSQL Initialization
-- Database schema for tracking job runs, metrics, and state

-- Create maestro user and database
CREATE DATABASE maestro_v5 OWNER maestro;

-- Connect to maestro_v5 database
\c maestro_v5 maestro;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ===== Job Runs Table (for audit & metrics) =====
CREATE TABLE IF NOT EXISTS agent_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(50) NOT NULL,
    skill_id VARCHAR(100),
    model_tier VARCHAR(20),
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd DECIMAL(10, 6),
    latency_ms INTEGER,
    status VARCHAR(20) NOT NULL,  -- success, timeout, error
    error_message TEXT,
    feedback_score SMALLINT,  -- 0-5, nullable
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_agent_created (agent_id, created_at),
    INDEX idx_status_created (status, created_at)
);

-- ===== Job Execution History (for APScheduler) =====
CREATE TABLE IF NOT EXISTS maestro_job_runs (
    job_id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    job_type VARCHAR(50),  -- rag-reindex, memory-purge, feedback-loop, health-check
    trigger_type VARCHAR(20),  -- cron, manual, retry
    scheduled_time TIMESTAMP WITH TIME ZONE,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    status VARCHAR(20) NOT NULL,  -- pending, running, success, failure, timeout
    error_message TEXT,
    error_traceback TEXT,
    output_summary JSONB,  -- Job-specific output
    retry_count SMALLINT DEFAULT 0,
    max_retries SMALLINT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_name_time (job_name, start_time DESC),
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
);

-- ===== Job Metrics (for Prometheus export) =====
CREATE TABLE IF NOT EXISTS maestro_job_metrics (
    metric_id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms DECIMAL(10, 2),
    max_duration_ms INTEGER,
    min_duration_ms INTEGER,
    last_execution TIMESTAMP WITH TIME ZONE,
    health_status VARCHAR(20),  -- healthy, degraded, unhealthy
    INDEX idx_job_timestamp (job_name, timestamp DESC)
);

-- ===== Agent Memory State (for R10 purge tracking) =====
CREATE TABLE IF NOT EXISTS agent_memory_state (
    agent_id VARCHAR(50) PRIMARY KEY,
    memory_size_mb DECIMAL(10, 2),
    chunk_count INTEGER,
    last_purged TIMESTAMP WITH TIME ZONE,
    age_days INTEGER,
    retention_policy VARCHAR(50),  -- strict, normal, loose
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== RAG Collections Index (for R6 reindex tracking) =====
CREATE TABLE IF NOT EXISTS rag_collection_index (
    collection_id VARCHAR(100) PRIMARY KEY,
    version VARCHAR(10),  -- v5.0, v4.9, etc.
    chunk_count INTEGER,
    last_reindexed TIMESTAMP WITH TIME ZONE,
    embedding_model VARCHAR(100),
    embedding_dimension INTEGER,
    status VARCHAR(20),  -- active, deprecated, archived
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== Feedback Loop Data (for R9 retraining) =====
CREATE TABLE IF NOT EXISTS agent_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES agent_runs(run_id) ON DELETE CASCADE,
    user_id VARCHAR(100),
    rating SMALLINT,  -- 0-5 stars
    comment TEXT,
    intent_embedding FLOAT8[] DEFAULT NULL,  -- For clustering
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_run_rating (run_id, rating),
    INDEX idx_created (created_at DESC),
    INDEX idx_user (user_id)
);

-- ===== Scheduler State (for APScheduler coordination) =====
CREATE TABLE IF NOT EXISTS maestro_scheduler_state (
    scheduler_id VARCHAR(50) PRIMARY KEY,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_running BOOLEAN DEFAULT FALSE,
    job_count INTEGER,
    health_status VARCHAR(20),
    version VARCHAR(10),
    config_hash VARCHAR(64),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===== Alerting State (for AlertManager deduplication) =====
CREATE TABLE IF NOT EXISTS maestro_alerts (
    alert_id SERIAL PRIMARY KEY,
    alert_name VARCHAR(100) NOT NULL,
    alert_group VARCHAR(100),
    severity VARCHAR(20),  -- critical, warning, info
    message TEXT,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    INDEX idx_alert_time (alert_name, triggered_at DESC),
    INDEX idx_status (resolved_at NULLS FIRST)
);

-- ===== Audit Log (immutable, append-only) =====
CREATE TABLE IF NOT EXISTS maestro_audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50),  -- job_start, job_end, config_change, alert_fired
    entity_id VARCHAR(100),  -- job_name, run_id, alert_id
    entity_type VARCHAR(50),
    action VARCHAR(100),
    details JSONB,
    actor VARCHAR(100),  -- user, system, scheduler
    source_ip INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entity (entity_type, entity_id, created_at DESC),
    INDEX idx_event_time (event_type, created_at DESC)
);

-- ===== Permissions & Roles =====

-- Read-only role for monitoring (Prometheus, Grafana)
CREATE ROLE maestro_reader WITH LOGIN PASSWORD 'maestro_reader_pwd';
GRANT CONNECT ON DATABASE maestro_v5 TO maestro_reader;
GRANT USAGE ON SCHEMA public TO maestro_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO maestro_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO maestro_reader;

-- Read-write role for scheduler (APScheduler)
CREATE ROLE maestro_writer WITH LOGIN PASSWORD 'maestro_writer_pwd';
GRANT CONNECT ON DATABASE maestro_v5 TO maestro_writer;
GRANT USAGE ON SCHEMA public TO maestro_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO maestro_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO maestro_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO maestro_writer;

-- ===== Functions for Metrics Aggregation =====

-- Function to aggregate job metrics hourly
CREATE OR REPLACE FUNCTION aggregate_job_metrics()
RETURNS TABLE (
    job_name VARCHAR,
    period_hour TIMESTAMP WITH TIME ZONE,
    success_count INTEGER,
    failure_count INTEGER,
    avg_duration DECIMAL
) LANGUAGE SQL STABLE AS $$
SELECT
    job_name,
    date_trunc('hour', start_time) as period_hour,
    COUNT(*) FILTER (WHERE status = 'success') as success_count,
    COUNT(*) FILTER (WHERE status = 'failure') as failure_count,
    AVG(duration_ms) FILTER (WHERE status = 'success')::DECIMAL as avg_duration
FROM maestro_job_runs
WHERE start_time > NOW() - INTERVAL '7 days'
GROUP BY job_name, period_hour
ORDER BY period_hour DESC;
$$;

-- Function to clean old audit logs (retention: 90 days)
CREATE OR REPLACE FUNCTION cleanup_audit_logs()
RETURNS INTEGER LANGUAGE SQL AS $$
DELETE FROM maestro_audit_log
WHERE created_at < NOW() - INTERVAL '90 days';
$$;

-- Function to clean old job runs (retention: 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_job_runs()
RETURNS INTEGER LANGUAGE SQL AS $$
DELETE FROM maestro_job_runs
WHERE status = 'success'
  AND end_time < NOW() - INTERVAL '30 days';
$$;

-- ===== Views for Monitoring =====

-- View: Recent job health
CREATE OR REPLACE VIEW v_job_health AS
SELECT
    job_name,
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE status = 'success') as successful_runs,
    COUNT(*) FILTER (WHERE status = 'failure') as failed_runs,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') / COUNT(*), 2) as success_rate,
    AVG(duration_ms) as avg_duration_ms,
    MAX(start_time) as last_run
FROM maestro_job_runs
WHERE start_time > NOW() - INTERVAL '7 days'
GROUP BY job_name
ORDER BY success_rate ASC;

-- View: Current scheduler state
CREATE OR REPLACE VIEW v_scheduler_status AS
SELECT
    scheduler_id,
    last_heartbeat,
    is_running,
    job_count,
    health_status,
    version,
    ROUND(EXTRACT(EPOCH FROM (NOW() - last_heartbeat))) as seconds_since_heartbeat
FROM maestro_scheduler_state
ORDER BY last_heartbeat DESC
LIMIT 1;

-- ===== Triggers =====

-- Trigger: Auto-update maestro_scheduler_state.updated_at
CREATE OR REPLACE FUNCTION update_scheduler_timestamp()
RETURNS TRIGGER LANGUAGE PLPGSQL AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER maestro_scheduler_state_update_ts
BEFORE UPDATE ON maestro_scheduler_state
FOR EACH ROW
EXECUTE FUNCTION update_scheduler_timestamp();

-- Trigger: Insert audit log on job completion
CREATE OR REPLACE FUNCTION log_job_completion()
RETURNS TRIGGER LANGUAGE PLPGSQL AS $$
BEGIN
    IF NEW.status IN ('success', 'failure') THEN
        INSERT INTO maestro_audit_log (event_type, entity_id, entity_type, action, details, actor)
        VALUES (
            'job_' || NEW.status,
            NEW.job_name,
            'job',
            'Job ' || NEW.status,
            jsonb_build_object(
                'job_id', NEW.job_id,
                'duration_ms', NEW.duration_ms,
                'error_message', NEW.error_message
            ),
            'scheduler'
        );
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER maestro_job_runs_audit
AFTER UPDATE ON maestro_job_runs
FOR EACH ROW
EXECUTE FUNCTION log_job_completion();

-- ===== Constraints & Indexes =====

-- Primary key constraints are already set above
-- Add check constraints
ALTER TABLE maestro_job_runs ADD CONSTRAINT check_duration_positive
    CHECK (duration_ms >= 0);

ALTER TABLE agent_feedback ADD CONSTRAINT check_rating_range
    CHECK (rating >= 0 AND rating <= 5);

-- Add unique constraints
ALTER TABLE maestro_scheduler_state ADD CONSTRAINT unique_scheduler_id
    UNIQUE (scheduler_id);

-- ===== Initial Data =====

-- Insert initial scheduler state
INSERT INTO maestro_scheduler_state (scheduler_id, is_running, job_count, health_status, version)
VALUES ('maestro-apscheduler-1', FALSE, 0, 'initializing', '5.0')
ON CONFLICT (scheduler_id) DO NOTHING;

-- Insert initial RAG collections (from VERSIONS.json)
INSERT INTO rag_collection_index (collection_id, version, chunk_count, status)
VALUES
    ('san:v5.0', 'v5.0', 2500, 'active'),
    ('ene:v5.0', 'v5.0', 3000, 'active'),
    ('por:v5.0', 'v5.0', 2000, 'active'),
    ('aer:v5.0', 'v5.0', 1800, 'active'),
    ('bar:v5.0', 'v5.0', 2200, 'active'),
    ('rod:v5.0', 'v5.0', 4000, 'active'),
    ('oae:v5.0', 'v5.0', 2000, 'active'),
    ('fer:v5.0', 'v5.0', 1500, 'active'),
    ('met:v5.0', 'v5.0', 2000, 'active')
ON CONFLICT (collection_id) DO NOTHING;

-- ===== Grant Permissions =====

-- maestro user (main scheduler) - full access
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO maestro;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO maestro;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO maestro;

-- Set default privileges for new objects
ALTER DEFAULT PRIVILEGES FOR USER maestro IN SCHEMA public GRANT ALL ON TABLES TO maestro;
ALTER DEFAULT PRIVILEGES FOR USER maestro IN SCHEMA public GRANT ALL ON SEQUENCES TO maestro;

-- ===== End of Initialization =====
