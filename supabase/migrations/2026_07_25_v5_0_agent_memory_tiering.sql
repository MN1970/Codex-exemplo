-- Manta Maestro v5.0 — Agent Memory Tiering Schema (R10 refined)
-- Ticket: MNT-2026-AGENT-MEMORY-TIERING
--
-- Extensão da agent_memory schema para suportar 3 tiers:
--   1. HOT (in-process): últimas 100 completions, 30 min TTL
--   2. WARM (Supabase agent_memory): 480 min TTL, com rating feedback
--   3. COLD (Archive agent_memory_archive): 90 dias retenção, GDPR compliant
--
-- Novos componentes:
--   1. agent_memory_archive — tabela para cold tier (90 dias)
--   2. agent_memory_tier_log — auditoria de movimentações entre tiers
--   3. Colunas extras em agent_memory: tier, last_access_at, access_count
--   4. Índices para eviction LRU (least-recently-used)
--   5. Stored procedures para tiering automation
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_tiering.sql

BEGIN;

-- Enable required extensions (já devem estar habilitados de antes)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================================
-- 1. ALTERAÇÕES À TABELA EXISTENTE agent_memory (adicionar tiering cols)
-- =====================================================================

ALTER TABLE IF EXISTS agent_memory
    ADD COLUMN IF NOT EXISTS tier VARCHAR(10) DEFAULT 'WARM'
        CHECK (tier IN ('HOT', 'WARM', 'COLD')),
    ADD COLUMN IF NOT EXISTS last_access_at TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS access_count INT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS feedback_score FLOAT8 DEFAULT NULL
        CHECK (feedback_score IS NULL OR (feedback_score >= 0.0 AND feedback_score <= 1.0));

-- Índices para tiering automático (HOT → WARM transition)
CREATE INDEX IF NOT EXISTS idx_agent_memory_tier_hot
    ON agent_memory (agent_id, last_access_at DESC)
    WHERE tier = 'HOT' AND created_at < (NOW() - INTERVAL '30 minutes');

-- Índices para WARM → COLD transition (480 min + rating < 2)
CREATE INDEX IF NOT EXISTS idx_agent_memory_tier_warm_archive
    ON agent_memory (agent_id, last_access_at ASC)
    WHERE tier = 'WARM'
        AND last_access_at < (NOW() - INTERVAL '480 minutes')
        AND (user_rating IS NULL OR user_rating < 2);

-- Índice para LRU eviction (quota exceeded)
CREATE INDEX IF NOT EXISTS idx_agent_memory_lru
    ON agent_memory (agent_id, last_access_at ASC)
    WHERE tier = 'WARM'
    ORDER BY last_access_at ASC;

-- Índice para chunks com rating alto (embedding retraining - R9 integration)
CREATE INDEX IF NOT EXISTS idx_agent_memory_high_rating
    ON agent_memory (agent_id, feedback_score DESC)
    WHERE feedback_score >= 0.8 AND tier IN ('HOT', 'WARM');

-- =====================================================================
-- 2. AGENT_MEMORY_ARCHIVE — Cold tier (90 dias retenção)
-- =====================================================================
-- Armazena entradas antigas com audit trail completo para GDPR compliance.
-- Auto-delete após 90 dias (via scheduled job).
-- RLS isolamento por agent_id.

CREATE TABLE IF NOT EXISTS agent_memory_archive (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    memory_value JSONB NOT NULL,
    memory_size_bytes BIGINT DEFAULT 0,
    user_rating SMALLINT DEFAULT NULL,
    source_prompt TEXT,
    checksum VARCHAR(32),
    feedback_score FLOAT8 DEFAULT NULL,

    -- Tiering metadata
    tier VARCHAR(10) NOT NULL DEFAULT 'COLD',
    created_at TIMESTAMPTZ NOT NULL,
    last_access_at TIMESTAMPTZ NOT NULL,
    access_count INT DEFAULT 0,
    archived_at TIMESTAMPTZ DEFAULT NOW(),
    archive_reason VARCHAR(100),  -- 'TTL_EXPIRED', 'LOW_RATING', 'QUOTA_EVICT', 'USER_DELETE'

    -- Audit trail
    archived_by TEXT DEFAULT 'system',  -- 'system' ou user_id
    retention_until TIMESTAMPTZ NOT NULL,  -- Created + 90 days

    CONSTRAINT agent_id_not_empty CHECK (agent_id != ''),
    CONSTRAINT memory_key_not_empty CHECK (memory_key != ''),
    CONSTRAINT retention_after_archived CHECK (retention_until > archived_at)
);

-- Índices para Cold tier
CREATE INDEX idx_agent_memory_archive_expires
    ON agent_memory_archive (agent_id, retention_until ASC)
    WHERE archived_at < (NOW() - INTERVAL '90 days');

CREATE INDEX idx_agent_memory_archive_reason
    ON agent_memory_archive (agent_id, archive_reason)
    WHERE archived_at > (NOW() - INTERVAL '7 days');

-- RLS — isolamento por agent_id
ALTER TABLE agent_memory_archive ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_memory_archive_isolation ON agent_memory_archive
    USING (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true)
    WITH CHECK (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true);

-- =====================================================================
-- 3. AGENT_MEMORY_TIER_LOG — Auditoria de movimentações
-- =====================================================================
-- Registro imutável (append-only) de transições entre tiers.
-- Serve para análise de eficiência de tiering e debugging.

CREATE TABLE IF NOT EXISTS agent_memory_tier_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,
    memory_id UUID NOT NULL,
    from_tier VARCHAR(10) NOT NULL,
    to_tier VARCHAR(10) NOT NULL,
    reason VARCHAR(100) NOT NULL,  -- 'INACTIVITY', 'LOW_RATING', 'QUOTA', 'FEEDBACK_HIGH', 'COLD_PURGE'
    memory_size_bytes BIGINT,
    user_rating SMALLINT,
    feedback_score FLOAT8,
    transitioned_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT from_tier_valid CHECK (from_tier IN ('HOT', 'WARM', 'COLD')),
    CONSTRAINT to_tier_valid CHECK (to_tier IN ('HOT', 'WARM', 'COLD', 'DELETED'))
);

-- Índice para auditoria rápida
CREATE INDEX idx_agent_memory_tier_log_agent
    ON agent_memory_tier_log (agent_id, transitioned_at DESC);

CREATE INDEX idx_agent_memory_tier_log_reason
    ON agent_memory_tier_log (agent_id, reason)
    WHERE transitioned_at > (NOW() - INTERVAL '7 days');

-- =====================================================================
-- 4. AGENT_MEMORY_QUOTA — Tracking de quota por agent
-- =====================================================================
-- Mantém métricas atualizadas de quota (max 100 MB / agent por padrão).

CREATE TABLE IF NOT EXISTS agent_memory_quota (
    agent_id TEXT PRIMARY KEY,
    max_memory_mb NUMERIC(10,2) DEFAULT 100.00,
    current_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    hot_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    warm_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    cold_memory_mb NUMERIC(10,2) DEFAULT 0.00,
    chunk_count INT DEFAULT 0,
    last_checked_at TIMESTAMPTZ DEFAULT NOW(),
    quota_exceeded_at TIMESTAMPTZ DEFAULT NULL,  -- Timestamp de quando > 80%

    CONSTRAINT agent_id_not_empty CHECK (agent_id != ''),
    CONSTRAINT max_memory_positive CHECK (max_memory_mb > 0),
    CONSTRAINT current_memory_non_negative CHECK (current_memory_mb >= 0)
);

CREATE INDEX idx_agent_memory_quota_exceeded
    ON agent_memory_quota (agent_id)
    WHERE (current_memory_mb / max_memory_mb) > 0.8;

-- =====================================================================
-- 5. STORED PROCEDURE: promote_hot_to_warm()
-- =====================================================================
-- Transição HOT → WARM após 30 min inatividade.
-- Chamado a cada 5 min pelo scheduler.

CREATE OR REPLACE FUNCTION promote_hot_to_warm()
RETURNS TABLE (
    agent_id TEXT,
    moved_count INT,
    freed_mb NUMERIC
) AS $$
DECLARE
    v_threshold TIMESTAMPTZ;
    v_moved_count INT := 0;
    v_freed_mb NUMERIC := 0;
    rec RECORD;
BEGIN
    v_threshold := NOW() - INTERVAL '30 minutes';

    -- Identificar HOT chunks inativos
    FOR rec IN
        SELECT agent_id, COUNT(*) as cnt, SUM(memory_size_bytes) as total_bytes
        FROM agent_memory
        WHERE tier = 'HOT'
            AND last_access_at < v_threshold
        GROUP BY agent_id
    LOOP
        -- Transição para WARM
        UPDATE agent_memory
        SET tier = 'WARM'
        WHERE agent_id = rec.agent_id
            AND tier = 'HOT'
            AND last_access_at < v_threshold;

        -- Log da transição
        INSERT INTO agent_memory_tier_log (
            agent_id, memory_id, from_tier, to_tier, reason, memory_size_bytes
        )
        SELECT
            agent_id, id, 'HOT', 'WARM', 'INACTIVITY', memory_size_bytes
        FROM agent_memory
        WHERE agent_id = rec.agent_id
            AND tier = 'WARM'
            AND created_at < v_threshold
            AND id NOT IN (
                SELECT memory_id FROM agent_memory_tier_log
                WHERE agent_id = rec.agent_id AND to_tier = 'WARM'
            );

        v_moved_count := v_moved_count + rec.cnt;
        v_freed_mb := v_freed_mb + (rec.total_bytes::NUMERIC / 1048576.0);
    END LOOP;

    RETURN QUERY SELECT rec.agent_id::TEXT, v_moved_count, v_freed_mb;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 6. STORED PROCEDURE: archive_warm_to_cold()
-- =====================================================================
-- Transição WARM → COLD após 480 min + (user_rating < 2 OR aged).
-- Chamado diariamente (03:00 UTC).

CREATE OR REPLACE FUNCTION archive_warm_to_cold(p_agent_id TEXT DEFAULT NULL)
RETURNS TABLE (
    agent_id TEXT,
    archived_count INT,
    freed_mb NUMERIC
) AS $$
DECLARE
    v_threshold TIMESTAMPTZ;
    v_archived_count INT := 0;
    v_freed_mb NUMERIC := 0;
    rec RECORD;
    v_agents TEXT[] := ARRAY[]::TEXT[];
BEGIN
    v_threshold := NOW() - INTERVAL '480 minutes';

    -- Se p_agent_id NULL, processar todos; senão apenas esse agent
    IF p_agent_id IS NOT NULL THEN
        v_agents := ARRAY[p_agent_id];
    ELSE
        SELECT ARRAY_AGG(DISTINCT agent_id)
        INTO v_agents
        FROM agent_memory
        WHERE tier = 'WARM';
    END IF;

    FOREACH p_agent_id IN ARRAY v_agents
    LOOP
        -- Mover para archive
        INSERT INTO agent_memory_archive (
            agent_id, session_id, memory_key, memory_value, memory_size_bytes,
            user_rating, source_prompt, checksum, feedback_score,
            tier, created_at, last_access_at, access_count, archive_reason,
            archived_by, retention_until
        )
        SELECT
            agent_id, session_id, memory_key, memory_value, memory_size_bytes,
            user_rating, source_prompt, checksum, feedback_score,
            'COLD', created_at, last_access_at, access_count,
            CASE
                WHEN user_rating < 2 THEN 'LOW_RATING'
                ELSE 'TTL_EXPIRED'
            END,
            'system', NOW() + INTERVAL '90 days'
        FROM agent_memory
        WHERE agent_id = p_agent_id
            AND tier = 'WARM'
            AND last_access_at < v_threshold
            AND (user_rating IS NULL OR user_rating < 2);

        v_archived_count := v_archived_count + ROW_COUNT();

        -- Deletar do warm tier
        DELETE FROM agent_memory
        WHERE agent_id = p_agent_id
            AND tier = 'WARM'
            AND last_access_at < v_threshold
            AND (user_rating IS NULL OR user_rating < 2);

        -- Log das transições
        INSERT INTO agent_memory_tier_log (
            agent_id, memory_id, from_tier, to_tier, reason, memory_size_bytes, user_rating
        )
        SELECT
            agent_id, id, 'WARM', 'COLD', 'TTL_EXPIRED', memory_size_bytes, user_rating
        FROM agent_memory_archive
        WHERE agent_id = p_agent_id
            AND tier = 'COLD'
            AND archived_at > NOW() - INTERVAL '1 minute';

        -- Calcular bytes libertados
        SELECT SUM(memory_size_bytes)::NUMERIC / 1048576.0
        INTO v_freed_mb
        FROM agent_memory_archive
        WHERE agent_id = p_agent_id
            AND tier = 'COLD'
            AND archived_at > NOW() - INTERVAL '1 minute';
    END LOOP;

    RETURN QUERY
        SELECT p_agent_id::TEXT, v_archived_count, COALESCE(v_freed_mb, 0::NUMERIC);
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 7. STORED PROCEDURE: purge_cold_tier()
-- =====================================================================
-- Deletar entradas de cold tier após 90 dias (GDPR compliance).
-- Chamado diariamente (03:30 UTC), após archive_warm_to_cold().

CREATE OR REPLACE FUNCTION purge_cold_tier(p_agent_id TEXT DEFAULT NULL)
RETURNS TABLE (
    agent_id TEXT,
    purged_count INT,
    freed_mb NUMERIC
) AS $$
DECLARE
    v_purged_count INT := 0;
    v_freed_mb NUMERIC := 0;
    v_agents TEXT[] := ARRAY[]::TEXT[];
    v_agent_id_iter TEXT;
BEGIN
    -- Se p_agent_id NULL, processar todos; senão apenas esse agent
    IF p_agent_id IS NOT NULL THEN
        v_agents := ARRAY[p_agent_id];
    ELSE
        SELECT ARRAY_AGG(DISTINCT agent_id)
        INTO v_agents
        FROM agent_memory_archive
        WHERE retention_until < NOW();
    END IF;

    FOREACH v_agent_id_iter IN ARRAY v_agents
    LOOP
        -- Calcular bytes a liberar antes de deletar
        SELECT SUM(memory_size_bytes)::NUMERIC / 1048576.0
        INTO v_freed_mb
        FROM agent_memory_archive
        WHERE agent_id = v_agent_id_iter
            AND retention_until < NOW();

        -- Deletar registros expirados
        DELETE FROM agent_memory_archive
        WHERE agent_id = v_agent_id_iter
            AND retention_until < NOW();

        v_purged_count := v_purged_count + ROW_COUNT();

        -- Log da purga
        INSERT INTO agent_memory_tier_log (
            agent_id, memory_id, from_tier, to_tier, reason, transitioned_at
        )
        VALUES (
            v_agent_id_iter,
            uuid_generate_v4(),
            'COLD',
            'DELETED',
            'COLD_PURGE',
            NOW()
        );
    END LOOP;

    RETURN QUERY
        SELECT v_agent_id_iter::TEXT, v_purged_count, COALESCE(v_freed_mb, 0::NUMERIC);
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 8. STORED PROCEDURE: lru_evict_quota_exceeded()
-- =====================================================================
-- LRU eviction quando quota > 80% (graceful eviction).
-- Move oldest WARM/HOT entries para COLD ou DELETE dependendo de rating.

CREATE OR REPLACE FUNCTION lru_evict_quota_exceeded(p_agent_id TEXT)
RETURNS TABLE (
    agent_id TEXT,
    evicted_count INT,
    freed_mb NUMERIC
) AS $$
DECLARE
    v_current_mb NUMERIC;
    v_max_mb NUMERIC;
    v_quota_pct NUMERIC;
    v_eviction_needed_mb NUMERIC;
    v_evicted_count INT := 0;
    v_freed_mb NUMERIC := 0;
BEGIN
    -- Obter quota atual
    SELECT current_memory_mb, max_memory_mb
    INTO v_current_mb, v_max_mb
    FROM agent_memory_quota
    WHERE agent_id = p_agent_id;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    v_quota_pct := (v_current_mb / v_max_mb) * 100.0;

    IF v_quota_pct < 80.0 THEN
        RETURN;
    END IF;

    -- Calcular quanto precisa liberar (target 60% quota)
    v_eviction_needed_mb := (v_current_mb - (v_max_mb * 0.6));

    -- LRU: mover chunks mais antigos com acesso baixo
    -- Prioridade: WARM/HOT com user_rating < 2 ou access_count < 2
    WITH to_evict AS (
        SELECT id, memory_size_bytes, user_rating
        FROM agent_memory
        WHERE agent_id = p_agent_id
            AND tier IN ('HOT', 'WARM')
            AND (user_rating < 2 OR access_count < 2)
        ORDER BY last_access_at ASC
        LIMIT LEAST(
            1000,
            (v_eviction_needed_mb * 1048576.0 /
                NULLIF(AVG(memory_size_bytes), 0))::INT
        )
    )
    DELETE FROM agent_memory
    WHERE id IN (SELECT id FROM to_evict);

    v_evicted_count := ROW_COUNT();
    v_freed_mb := (v_eviction_needed_mb * 0.6)::NUMERIC;

    -- Update quota
    UPDATE agent_memory_quota
    SET current_memory_mb = current_memory_mb - v_freed_mb
    WHERE agent_id = p_agent_id;

    RETURN QUERY SELECT p_agent_id, v_evicted_count, v_freed_mb;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 9. TRIGGER: update_memory_metrics_on_tier_change()
-- =====================================================================
-- Atualizar agent_memory_quota quando tier muda.

CREATE OR REPLACE FUNCTION update_memory_metrics_on_tier_change()
RETURNS TRIGGER AS $$
DECLARE
    v_hot_mb NUMERIC;
    v_warm_mb NUMERIC;
    v_cold_mb NUMERIC;
    v_total_mb NUMERIC;
BEGIN
    -- Recalcular totais para o agent
    SELECT
        SUM(CASE WHEN tier = 'HOT' THEN memory_size_bytes ELSE 0 END)::NUMERIC / 1048576.0,
        SUM(CASE WHEN tier = 'WARM' THEN memory_size_bytes ELSE 0 END)::NUMERIC / 1048576.0,
        COUNT(*) FILTER (WHERE tier = 'COLD')::INT
    INTO v_hot_mb, v_warm_mb, v_cold_mb
    FROM agent_memory
    WHERE agent_id = NEW.agent_id;

    v_total_mb := COALESCE(v_hot_mb, 0) + COALESCE(v_warm_mb, 0);

    -- Update quota table
    INSERT INTO agent_memory_quota (agent_id, hot_memory_mb, warm_memory_mb, cold_memory_mb, current_memory_mb, last_checked_at)
    VALUES (NEW.agent_id, v_hot_mb, v_warm_mb, v_cold_mb, v_total_mb, NOW())
    ON CONFLICT (agent_id) DO UPDATE SET
        hot_memory_mb = EXCLUDED.hot_memory_mb,
        warm_memory_mb = EXCLUDED.warm_memory_mb,
        cold_memory_mb = EXCLUDED.cold_memory_mb,
        current_memory_mb = EXCLUDED.current_memory_mb,
        last_checked_at = EXCLUDED.last_checked_at;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_memory_metrics
    AFTER INSERT OR UPDATE ON agent_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_memory_metrics_on_tier_change();

-- =====================================================================
-- 10. TRIGGER: access_count_increment()
-- =====================================================================
-- Incrementar access_count e atualizar last_access_at ao consultar.

CREATE OR REPLACE FUNCTION increment_access_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.access_count := NEW.access_count + 1;
    NEW.last_access_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_access
    BEFORE UPDATE ON agent_memory
    FOR EACH ROW
    WHEN (OLD.tier = NEW.tier)  -- Só incrementar se não houver tier change
    EXECUTE FUNCTION increment_access_count();

-- =====================================================================
-- 11. GRANTS — Permissões para AUTHENTICATED + SERVICE_ROLE
-- =====================================================================

GRANT SELECT, INSERT, UPDATE ON agent_memory TO authenticated;
GRANT SELECT, INSERT ON agent_memory_archive TO authenticated;
GRANT SELECT ON agent_memory_tier_log TO authenticated;
GRANT SELECT, INSERT, UPDATE ON agent_memory_quota TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON agent_memory TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON agent_memory_archive TO service_role;
GRANT SELECT, INSERT ON agent_memory_tier_log TO service_role;
GRANT SELECT, INSERT, UPDATE ON agent_memory_quota TO service_role;

GRANT EXECUTE ON FUNCTION promote_hot_to_warm() TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION archive_warm_to_cold(TEXT) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION purge_cold_tier(TEXT) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION lru_evict_quota_exceeded(TEXT) TO authenticated, service_role;

COMMIT;

-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- Se necessário fazer rollback desta migration:
--
-- BEGIN;
-- DROP TRIGGER IF EXISTS trg_increment_access ON agent_memory;
-- DROP TRIGGER IF EXISTS trg_update_memory_metrics ON agent_memory;
-- DROP FUNCTION IF EXISTS increment_access_count();
-- DROP FUNCTION IF EXISTS update_memory_metrics_on_tier_change();
-- DROP FUNCTION IF EXISTS lru_evict_quota_exceeded(TEXT);
-- DROP FUNCTION IF EXISTS purge_cold_tier(TEXT);
-- DROP FUNCTION IF EXISTS archive_warm_to_cold(TEXT);
-- DROP FUNCTION IF EXISTS promote_hot_to_warm();
-- DROP TABLE IF EXISTS agent_memory_quota CASCADE;
-- DROP TABLE IF EXISTS agent_memory_tier_log CASCADE;
-- DROP TABLE IF EXISTS agent_memory_archive CASCADE;
-- ALTER TABLE agent_memory DROP COLUMN IF EXISTS tier, DROP COLUMN IF EXISTS last_access_at, DROP COLUMN IF EXISTS access_count, DROP COLUMN IF EXISTS feedback_score;
-- DROP INDEX IF EXISTS idx_agent_memory_high_rating;
-- DROP INDEX IF EXISTS idx_agent_memory_lru;
-- DROP INDEX IF EXISTS idx_agent_memory_tier_warm_archive;
-- DROP INDEX IF EXISTS idx_agent_memory_tier_hot;
-- COMMIT;
