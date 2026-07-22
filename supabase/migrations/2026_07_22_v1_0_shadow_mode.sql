-- Migration: CAG Shadow Mode Logging
-- Version: 1.0
-- Date: 2026-07-22
-- Description: Add tables for 30-day CAG vs RAG comparison (shadow mode)
-- Estimated Duration: 2 minutes
-- Downtime: None (CONCURRENT index creation)

BEGIN;

-- ========================================================================
-- SHADOW MODE LOGGING TABLE
-- ========================================================================
-- Stores detailed comparison results from each query
-- 30-day window: Jul 22 - Aug 21, 2026

CREATE TABLE IF NOT EXISTS cag_shadow_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- RAG (v4.2) Results
    rag_agent VARCHAR(255),
    rag_latency_ms NUMERIC(10,2),
    rag_confidence NUMERIC(5,3),
    rag_response_text TEXT,

    -- CAG (v5.0) Results
    cag_selected_agents VARCHAR(255)[] DEFAULT ARRAY[]::VARCHAR[],
    cag_latency_ms NUMERIC(10,2),
    cag_avg_confidence NUMERIC(5,3),
    cag_final_response TEXT,

    -- Comparison Metrics
    agent_match BOOLEAN,
    confidence_delta NUMERIC(5,3),
    latency_delta_ms NUMERIC(10,2),
    latency_delta_pct NUMERIC(6,2),

    -- CAG Metadata (JSON)
    cag_metadata JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT pk_shadow_logs PRIMARY KEY (id)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shadow_logs_session
    ON cag_shadow_logs(session_id, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shadow_logs_timestamp
    ON cag_shadow_logs(timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shadow_logs_rag_agent
    ON cag_shadow_logs(rag_agent, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shadow_logs_agent_match
    ON cag_shadow_logs(agent_match, timestamp DESC);

-- ========================================================================
-- SHADOW MODE DAILY AGGREGATES
-- ========================================================================
-- Stores daily summary metrics for dashboard visualization

CREATE TABLE IF NOT EXISTS cag_shadow_daily_stats (
    id BIGSERIAL PRIMARY KEY,
    date_bucket DATE NOT NULL,

    -- Volume
    total_queries INT DEFAULT 0,
    queries_with_errors INT DEFAULT 0,
    error_rate NUMERIC(5,3) DEFAULT 0.0,

    -- Agent Match
    queries_agent_match INT DEFAULT 0,
    agent_match_rate NUMERIC(5,3) DEFAULT 0.0,

    -- Latency (milliseconds)
    rag_p50_ms NUMERIC(10,2),
    rag_p95_ms NUMERIC(10,2),
    rag_p99_ms NUMERIC(10,2),
    rag_avg_ms NUMERIC(10,2),

    cag_p50_ms NUMERIC(10,2),
    cag_p95_ms NUMERIC(10,2),
    cag_p99_ms NUMERIC(10,2),
    cag_avg_ms NUMERIC(10,2),

    -- Deltas
    latency_delta_pct_avg NUMERIC(6,2),
    confidence_delta_avg NUMERIC(5,3),

    -- Status
    go_ready BOOLEAN DEFAULT FALSE,
    notes TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT pk_shadow_daily_stats PRIMARY KEY (id),
    CONSTRAINT uq_shadow_daily_stats UNIQUE (date_bucket)
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shadow_daily_stats_date
    ON cag_shadow_daily_stats(date_bucket DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_shadow_daily_stats_go_ready
    ON cag_shadow_daily_stats(go_ready, date_bucket DESC);

-- ========================================================================
-- SHADOW MODE CONFIGURATION
-- ========================================================================
-- Feature flags and settings for shadow mode operation

CREATE TABLE IF NOT EXISTS cag_shadow_config (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT pk_shadow_config PRIMARY KEY (id),
    CONSTRAINT uq_shadow_config_key UNIQUE (key)
);

INSERT INTO cag_shadow_config (key, value, description) VALUES
    ('enabled', 'true', 'Enable/disable shadow mode'),
    ('start_date', '2026-07-22', 'Shadow mode start date'),
    ('end_date', '2026-08-21', '30-day window end date'),
    ('buffer_size', '100', 'Number of results before flushing to Supabase'),
    ('agent_match_threshold', '0.85', 'Minimum agent match rate for GO decision'),
    ('latency_threshold_pct', '10.0', 'Maximum acceptable latency increase (%)'),
    ('error_threshold', '0.001', 'Maximum acceptable error rate'),
    ('comparison_mode', 'parallel', 'Run CAG and RAG in parallel (parallel|sequential)'),
    ('debug_logging', 'false', 'Enable verbose debug output');

-- ========================================================================
-- HELPER FUNCTION: Compute daily stats
-- ========================================================================

CREATE OR REPLACE FUNCTION fn_compute_shadow_daily_stats(p_date DATE)
RETURNS void AS $$
DECLARE
    v_total INT;
    v_with_errors INT;
    v_agent_matches INT;
    v_rag_p50 NUMERIC;
    v_rag_p95 NUMERIC;
    v_rag_p99 NUMERIC;
    v_cag_p50 NUMERIC;
    v_cag_p95 NUMERIC;
    v_cag_p99 NUMERIC;
BEGIN
    -- Collect daily metrics
    SELECT
        COUNT(*),
        SUM(CASE WHEN rag_response_text LIKE '%error%' OR cag_final_response LIKE '%error%' THEN 1 ELSE 0 END),
        SUM(CASE WHEN agent_match THEN 1 ELSE 0 END),
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rag_latency_ms),
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY rag_latency_ms),
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY rag_latency_ms),
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cag_latency_ms),
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY cag_latency_ms),
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY cag_latency_ms)
    INTO
        v_total, v_with_errors, v_agent_matches,
        v_rag_p50, v_rag_p95, v_rag_p99,
        v_cag_p50, v_cag_p95, v_cag_p99
    FROM cag_shadow_logs
    WHERE DATE(timestamp) = p_date;

    -- Insert or update daily record
    INSERT INTO cag_shadow_daily_stats (
        date_bucket, total_queries, queries_with_errors, error_rate,
        queries_agent_match, agent_match_rate,
        rag_p50_ms, rag_p95_ms, rag_p99_ms,
        cag_p50_ms, cag_p95_ms, cag_p99_ms,
        go_ready
    ) VALUES (
        p_date,
        v_total,
        v_with_errors,
        CASE WHEN v_total > 0 THEN v_with_errors::NUMERIC / v_total ELSE 0 END,
        v_agent_matches,
        CASE WHEN v_total > 0 THEN v_agent_matches::NUMERIC / v_total ELSE 0 END,
        v_rag_p50, v_rag_p95, v_rag_p99,
        v_cag_p50, v_cag_p95, v_cag_p99,
        CASE
            WHEN v_total = 0 THEN FALSE
            WHEN (v_agent_matches::NUMERIC / v_total) < 0.85 THEN FALSE
            WHEN v_cag_p95 > (v_rag_p95 * 1.10) THEN FALSE
            WHEN (v_with_errors::NUMERIC / v_total) > 0.001 THEN FALSE
            ELSE TRUE
        END
    )
    ON CONFLICT (date_bucket) DO UPDATE SET
        total_queries = EXCLUDED.total_queries,
        queries_with_errors = EXCLUDED.queries_with_errors,
        error_rate = EXCLUDED.error_rate,
        queries_agent_match = EXCLUDED.queries_agent_match,
        agent_match_rate = EXCLUDED.agent_match_rate,
        rag_p50_ms = EXCLUDED.rag_p50_ms,
        rag_p95_ms = EXCLUDED.rag_p95_ms,
        rag_p99_ms = EXCLUDED.rag_p99_ms,
        cag_p50_ms = EXCLUDED.cag_p50_ms,
        cag_p95_ms = EXCLUDED.cag_p95_ms,
        cag_p99_ms = EXCLUDED.cag_p99_ms,
        latency_delta_pct_avg = EXCLUDED.latency_delta_pct_avg,
        confidence_delta_avg = EXCLUDED.confidence_delta_avg,
        go_ready = EXCLUDED.go_ready,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ========================================================================
-- VERIFICATION QUERIES
-- ========================================================================

/*
-- Check table creation
SELECT tablename FROM pg_tables
WHERE tablename LIKE 'cag_shadow_%'
ORDER BY tablename;

-- Check indices
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE tablename LIKE 'cag_shadow_%'
ORDER BY tablename, indexname;

-- Check function
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE 'fn_compute_shadow%';

-- Compute stats for today (manual)
SELECT fn_compute_shadow_daily_stats(CURRENT_DATE);

-- View daily summary
SELECT * FROM cag_shadow_daily_stats ORDER BY date_bucket DESC LIMIT 7;

-- View shadow logs sample
SELECT session_id, timestamp, rag_agent, cag_selected_agents, agent_match, latency_delta_pct
FROM cag_shadow_logs
ORDER BY timestamp DESC
LIMIT 10;
*/

COMMIT;

-- ========================================================================
-- ROLLBACK SCRIPT (if needed)
-- ========================================================================
/*
BEGIN;

DROP FUNCTION IF EXISTS fn_compute_shadow_daily_stats(DATE);

DROP INDEX IF EXISTS idx_shadow_daily_stats_go_ready;
DROP INDEX IF EXISTS idx_shadow_daily_stats_date;
DROP INDEX IF EXISTS idx_shadow_logs_agent_match;
DROP INDEX IF EXISTS idx_shadow_logs_rag_agent;
DROP INDEX IF EXISTS idx_shadow_logs_timestamp;
DROP INDEX IF EXISTS idx_shadow_logs_session;

DROP TABLE IF EXISTS cag_shadow_config;
DROP TABLE IF EXISTS cag_shadow_daily_stats;
DROP TABLE IF EXISTS cag_shadow_logs;

COMMIT;
*/
