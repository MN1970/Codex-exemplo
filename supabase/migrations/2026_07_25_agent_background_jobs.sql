-- Manta Maestro v5.0 — Background Job Queue Schema (S5 + horizontais)
-- Ticket: MNT-2026-BACKGROUND-AGENTS
--
-- Implementa schema para agent_jobs (background tasks).
-- Objetivo: Suportar long-running tasks (> 30s) sem bloquear agent.
--
-- Componentes:
--   1. agent_jobs — Job queue (pending → running → completed/failed/timeout)
--   2. agent_job_logs — Audit trail (append-only)
--   3. Indexes para polling eficiente (status, created_at)
--   4. RLS por agent_id (isolamento multi-tenant)
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_agent_background_jobs.sql

BEGIN;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================================
-- 1. AGENT_JOBS — Background job queue
-- =====================================================================
-- Armazena background jobs com state machine: pending → running → completed/failed/timeout
-- TTL: Manter por 30 dias após conclusão (depois purgar)
-- Isolamento: RLS por agent_id

CREATE TABLE IF NOT EXISTS agent_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,                    -- ex: "manta-03-s5" (túneis)
    status TEXT NOT NULL DEFAULT 'pending',    -- pending|running|completed|failed|timeout|cancelled
    prompt TEXT NOT NULL,                      -- Task prompt for agent
    result TEXT,                               -- Result (populated when completed)
    error TEXT,                                -- Error message (if failed)
    timeout_seconds INTEGER DEFAULT 300,       -- Job timeout (default: 5 min)
    retry_count INTEGER DEFAULT 0,             -- Current retry attempt
    max_retries INTEGER DEFAULT 2,             -- Max retries allowed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,                    -- When job started processing
    completed_at TIMESTAMPTZ,                  -- When job finished
    metadata JSONB DEFAULT '{}'::jsonb,        -- Custom metadata (agent-specific)
    callback_url TEXT,                         -- Optional webhook for completion
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT agent_id_not_empty CHECK (agent_id != ''),
    CONSTRAINT prompt_not_empty CHECK (prompt != ''),
    CONSTRAINT status_valid CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout', 'cancelled')),
    CONSTRAINT retry_count_valid CHECK (retry_count >= 0 AND retry_count <= max_retries),
    CONSTRAINT timeout_seconds_valid CHECK (timeout_seconds > 0 AND timeout_seconds <= 600),
    CONSTRAINT timestamps_valid CHECK (started_at IS NULL OR started_at >= created_at),
    CONSTRAINT completed_after_started CHECK (completed_at IS NULL OR started_at IS NULL OR completed_at >= started_at)
);

-- Indexes para polling eficiente (R7 — job queue processor)
CREATE INDEX idx_agent_jobs_status
    ON agent_jobs (status, created_at DESC)
    WHERE status = 'pending';

CREATE INDEX idx_agent_jobs_agent_id
    ON agent_jobs (agent_id, status);

CREATE INDEX idx_agent_jobs_created_at
    ON agent_jobs (created_at DESC);

CREATE INDEX idx_agent_jobs_cleanup
    ON agent_jobs (completed_at)
    WHERE status IN ('completed', 'failed', 'timeout');

-- RLS — isolamento por agent_id
ALTER TABLE agent_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_jobs_isolation ON agent_jobs
    USING (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true)
    WITH CHECK (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true);

-- =====================================================================
-- 2. AGENT_JOB_LOGS — Audit trail (append-only)
-- =====================================================================
-- Armazena histórico de transições de estado para cada job.
-- Objetivo: Auditoria + debugging
-- Política: Append-only (INSERT only, no UPDATE/DELETE)

CREATE TABLE IF NOT EXISTS agent_job_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES agent_jobs(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    old_status TEXT,                           -- Previous status
    new_status TEXT NOT NULL,                  -- New status
    reason TEXT,                               -- Why status changed
    error_detail TEXT,                         -- Error details if applicable
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT agent_id_not_empty_logs CHECK (agent_id != ''),
    CONSTRAINT new_status_not_empty CHECK (new_status != ''),
    CONSTRAINT old_status_different CHECK (old_status IS NULL OR old_status != new_status)
);

-- Index para audit queries
CREATE INDEX idx_agent_job_logs_job_id
    ON agent_job_logs (job_id, created_at DESC);

CREATE INDEX idx_agent_job_logs_agent_id
    ON agent_job_logs (agent_id, created_at DESC);

-- RLS — Audit trail read-only
ALTER TABLE agent_job_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_job_logs_insert ON agent_job_logs
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY agent_job_logs_read ON agent_job_logs
    FOR SELECT
    USING (true);

-- =====================================================================
-- 3. AGENT_JOB_METRICS — Job performance metrics
-- =====================================================================
-- Agregações de performance por agente.
-- Atualizado automaticamente por trigger (trg_job_completion_metrics)

CREATE TABLE IF NOT EXISTS agent_job_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL UNIQUE,             -- ex: "manta-03-s5"
    total_jobs INTEGER DEFAULT 0,
    completed_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    timeout_jobs INTEGER DEFAULT 0,
    avg_duration_seconds FLOAT8 DEFAULT 0.0,
    avg_retry_count FLOAT8 DEFAULT 0.0,
    success_rate FLOAT8 DEFAULT 0.0,           -- completed / total (%)
    last_job_timestamp TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT agent_id_not_empty_metrics CHECK (agent_id != ''),
    CONSTRAINT success_rate_valid CHECK (success_rate >= 0.0 AND success_rate <= 100.0)
);

-- Index
CREATE INDEX idx_agent_job_metrics_agent_id
    ON agent_job_metrics (agent_id);

-- RLS
ALTER TABLE agent_job_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_job_metrics_read ON agent_job_metrics
    FOR SELECT
    USING (true);

-- =====================================================================
-- 4. FUNCTIONS — Job state transitions & logging
-- =====================================================================

-- Function: Log job status transition
CREATE OR REPLACE FUNCTION log_job_status_change(
    p_job_id UUID,
    p_agent_id TEXT,
    p_old_status TEXT,
    p_new_status TEXT,
    p_reason TEXT DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    INSERT INTO agent_job_logs (
        job_id,
        agent_id,
        old_status,
        new_status,
        reason
    ) VALUES (p_job_id, p_agent_id, p_old_status, p_new_status, p_reason);
END;
$$ LANGUAGE plpgsql;

-- Function: Refresh job metrics (called after job completion)
CREATE OR REPLACE FUNCTION refresh_agent_job_metrics(p_agent_id TEXT)
RETURNS void AS $$
DECLARE
    v_total INTEGER;
    v_completed INTEGER;
    v_failed INTEGER;
    v_timeout INTEGER;
    v_avg_duration FLOAT8;
    v_success_rate FLOAT8;
BEGIN
    -- Compute aggregates
    SELECT COUNT(*) INTO v_total
        FROM agent_jobs WHERE agent_id = p_agent_id;

    SELECT COUNT(*) INTO v_completed
        FROM agent_jobs WHERE agent_id = p_agent_id AND status = 'completed';

    SELECT COUNT(*) INTO v_failed
        FROM agent_jobs WHERE agent_id = p_agent_id AND status = 'failed';

    SELECT COUNT(*) INTO v_timeout
        FROM agent_jobs WHERE agent_id = p_agent_id AND status = 'timeout';

    SELECT COALESCE(AVG(EXTRACT(EPOCH FROM (completed_at - started_at))), 0)
        INTO v_avg_duration
        FROM agent_jobs
        WHERE agent_id = p_agent_id AND started_at IS NOT NULL AND completed_at IS NOT NULL;

    v_success_rate := CASE WHEN v_total > 0 THEN (v_completed * 100.0 / v_total) ELSE 0 END;

    -- Upsert metrics
    INSERT INTO agent_job_metrics (
        agent_id,
        total_jobs,
        completed_jobs,
        failed_jobs,
        timeout_jobs,
        avg_duration_seconds,
        success_rate,
        last_job_timestamp,
        updated_at
    ) VALUES (
        p_agent_id,
        v_total,
        v_completed,
        v_failed,
        v_timeout,
        v_avg_duration,
        v_success_rate,
        NOW(),
        NOW()
    )
    ON CONFLICT (agent_id) DO UPDATE SET
        total_jobs = EXCLUDED.total_jobs,
        completed_jobs = EXCLUDED.completed_jobs,
        failed_jobs = EXCLUDED.failed_jobs,
        timeout_jobs = EXCLUDED.timeout_jobs,
        avg_duration_seconds = EXCLUDED.avg_duration_seconds,
        success_rate = EXCLUDED.success_rate,
        last_job_timestamp = EXCLUDED.last_job_timestamp,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function: Cleanup old jobs (called by trigger or APScheduler)
CREATE OR REPLACE FUNCTION cleanup_old_agent_jobs(p_days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM agent_jobs
        WHERE completed_at < (NOW() - (p_days_old || ' days')::interval)
        AND status IN ('completed', 'failed', 'timeout');

    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 5. TRIGGERS — Automatic state tracking & metrics refresh
-- =====================================================================

-- Trigger: Log status changes
CREATE OR REPLACE FUNCTION trg_agent_jobs_log_status()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        PERFORM log_job_status_change(
            NEW.id,
            NEW.agent_id,
            OLD.status,
            NEW.status,
            NULL
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agent_jobs_log_status ON agent_jobs;
CREATE TRIGGER trg_agent_jobs_log_status
    AFTER UPDATE ON agent_jobs
    FOR EACH ROW
    EXECUTE FUNCTION trg_agent_jobs_log_status();

-- Trigger: Refresh metrics on job completion
CREATE OR REPLACE FUNCTION trg_agent_jobs_refresh_metrics()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('completed', 'failed', 'timeout') AND OLD.status != NEW.status THEN
        PERFORM refresh_agent_job_metrics(NEW.agent_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agent_jobs_refresh_metrics ON agent_jobs;
CREATE TRIGGER trg_agent_jobs_refresh_metrics
    AFTER UPDATE ON agent_jobs
    FOR EACH ROW
    EXECUTE FUNCTION trg_agent_jobs_refresh_metrics();

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION trg_agent_jobs_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agent_jobs_update_timestamp ON agent_jobs;
CREATE TRIGGER trg_agent_jobs_update_timestamp
    BEFORE UPDATE ON agent_jobs
    FOR EACH ROW
    EXECUTE FUNCTION trg_agent_jobs_update_timestamp();

-- =====================================================================
-- 6. GRANTS — Role-based access
-- =====================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON agent_jobs TO "authenticated";
GRANT SELECT, INSERT ON agent_job_logs TO "authenticated";
GRANT SELECT ON agent_job_metrics TO "authenticated";

GRANT EXECUTE ON FUNCTION log_job_status_change TO "service_role";
GRANT EXECUTE ON FUNCTION refresh_agent_job_metrics TO "service_role";
GRANT EXECUTE ON FUNCTION cleanup_old_agent_jobs TO "service_role";

-- =====================================================================
-- ROLLBACK (DOWN)
-- =====================================================================
-- Uncomment below to rollback all changes

-- DROP TRIGGER IF EXISTS trg_agent_jobs_update_timestamp ON agent_jobs;
-- DROP TRIGGER IF EXISTS trg_agent_jobs_refresh_metrics ON agent_jobs;
-- DROP TRIGGER IF EXISTS trg_agent_jobs_log_status ON agent_jobs;
-- DROP FUNCTION IF EXISTS trg_agent_jobs_update_timestamp();
-- DROP FUNCTION IF EXISTS trg_agent_jobs_refresh_metrics();
-- DROP FUNCTION IF EXISTS trg_agent_jobs_log_status();
-- DROP FUNCTION IF EXISTS cleanup_old_agent_jobs(INTEGER);
-- DROP FUNCTION IF EXISTS refresh_agent_job_metrics(TEXT);
-- DROP FUNCTION IF EXISTS log_job_status_change(UUID, TEXT, TEXT, TEXT, TEXT);
-- DROP TABLE IF EXISTS agent_job_metrics CASCADE;
-- DROP TABLE IF EXISTS agent_job_logs CASCADE;
-- DROP TABLE IF EXISTS agent_jobs CASCADE;

COMMIT;
