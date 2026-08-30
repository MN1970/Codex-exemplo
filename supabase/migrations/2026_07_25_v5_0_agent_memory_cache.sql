-- Manta Maestro v5.0 — Agent Memory Cache Schema (R10)
-- Ticket: MNT-2026-AGENT-MEMORY-CACHE
--
-- Este arquivo implementa o schema de agent_memory cache para S1 e demais agentes.
-- Objetivo: Cache ephemeral (TTL 480 min) + estado persistente com versionamento.
--
-- Componentes:
--   1. agent_memory — cache de curta duração (sessão)
--   2. agent_state — estado persistente (embeddings, ratings)
--   3. agent_memory_metrics — tracking de uso (size, chunks, purge)
--   4. RLS por agent_id (isolamento multi-tenant)
--   5. Índices para purga eficiente (expires_at, user_rating)
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_v5_0_agent_memory_cache.sql
--
-- ROLLBACK: ao final deste arquivo (bloco DOWN)

BEGIN;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================================
-- 1. AGENT_MEMORY — Cache ephemeral (TTL 480 min)
-- =====================================================================
-- Armazena conversas, context windows, embeddings de queries frequentes.
-- Política de limpeza: DELETE > expires_at
-- Isolamento: RLS por agent_id

CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,                    -- ex: "manta-03-s1" (rodovias)
    session_id TEXT NOT NULL,                  -- ex: "sess_abc123"
    memory_key TEXT NOT NULL,                  -- ex: "query:embedding", "context:window"
    memory_value JSONB NOT NULL,               -- Payload flexível (texto, números, arrays)
    memory_size_bytes BIGINT DEFAULT 0,        -- Tamanho em bytes (para tracking)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,           -- NOW() + 480 min
    user_rating SMALLINT DEFAULT NULL,         -- 0-5, coletado pós-run (R9)
    source_prompt TEXT,                        -- Query original que gerou este cache
    checksum VARCHAR(32),                      -- MD5 do memory_value (dedup)

    CONSTRAINT agent_id_not_empty CHECK (agent_id != ''),
    CONSTRAINT session_id_not_empty CHECK (session_id != ''),
    CONSTRAINT memory_key_not_empty CHECK (memory_key != ''),
    CONSTRAINT expires_after_created CHECK (expires_at > created_at),
    CONSTRAINT user_rating_valid CHECK (user_rating IS NULL OR (user_rating >= 0 AND user_rating <= 5))
);

-- Índices para purga eficiente (R10 policy)
CREATE INDEX idx_agent_memory_expires_at
    ON agent_memory (agent_id, expires_at DESC)
    WHERE expires_at > NOW();

CREATE INDEX idx_agent_memory_user_rating
    ON agent_memory (agent_id, user_rating)
    WHERE user_rating < 2 AND expires_at < (NOW() - INTERVAL '7 days');

CREATE INDEX idx_agent_memory_checksum
    ON agent_memory (agent_id, checksum);

CREATE INDEX idx_agent_memory_session
    ON agent_memory (session_id, created_at DESC);

-- RLS — isolamento por agent_id
ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_memory_isolation ON agent_memory
    USING (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true)
    WITH CHECK (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true);

-- =====================================================================
-- 2. AGENT_STATE — Estado persistente (embeddings, feedback)
-- =====================================================================
-- Armazena embeddings de queries frequentes, intent vectors, ratings agregados.
-- Persistência: 30+ dias (não auto-delete)
-- Feedback loop (R9): agrega ratings para fine-tuning embedding model

CREATE TABLE IF NOT EXISTS agent_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,                    -- ex: "manta-03-s1"
    embedding_vector vector(1536) DEFAULT NULL, -- Multilingual-E5-Large (1536 dim)
    user_intent_score FLOAT8 DEFAULT 0.0,      -- Score agregado de intent (0.0-1.0)
    feedback_count INT DEFAULT 0,              -- Número de ratings coletados
    avg_user_rating FLOAT8 DEFAULT NULL,       -- Média de user_rating (0.0-5.0)
    last_query_text TEXT,                      -- Última query processada
    total_memory_size_bytes BIGINT DEFAULT 0,  -- Tamanho total do cache
    chunk_count INT DEFAULT 0,                 -- Número de chunks em cache
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT agent_id_not_empty_state CHECK (agent_id != ''),
    CONSTRAINT user_intent_score_valid CHECK (user_intent_score >= 0.0 AND user_intent_score <= 1.0),
    CONSTRAINT feedback_count_non_negative CHECK (feedback_count >= 0),
    CONSTRAINT avg_user_rating_valid CHECK (avg_user_rating IS NULL OR (avg_user_rating >= 0.0 AND avg_user_rating <= 5.0)),
    CONSTRAINT chunk_count_non_negative CHECK (chunk_count >= 0)
);

-- Índices para retrieval rápido
CREATE INDEX idx_agent_state_agent_id
    ON agent_state (agent_id);

CREATE INDEX idx_agent_state_embedding
    ON agent_state USING ivfflat (embedding_vector vector_cosine_ops)
    WHERE embedding_vector IS NOT NULL;

CREATE INDEX idx_agent_state_last_updated
    ON agent_state (agent_id, last_updated DESC);

-- RLS — isolamento por agent_id
ALTER TABLE agent_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_state_isolation ON agent_state
    USING (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true)
    WITH CHECK (agent_id = CURRENT_SETTING('app.current_agent_id', true)::TEXT
        OR CURRENT_SETTING('app.is_admin', true)::BOOLEAN = true);

-- =====================================================================
-- 3. AGENT_MEMORY_METRICS — Tracking de purga e health
-- =====================================================================
-- Registra histórico de purgas (R10), tamanhos, chunk counts.
-- Usado para observabilidade (Grafana dashboard)

CREATE TABLE IF NOT EXISTS agent_memory_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,                 -- "purge", "size", "chunk_count"
    metric_value FLOAT8 NOT NULL,
    memory_size_mb FLOAT8,                     -- Tamanho do cache em MB
    chunk_count INT,                           -- Número de chunks ativos
    deleted_count INT,                         -- Número deletado na purga
    last_purge_at TIMESTAMPTZ,                 -- Timestamp da última purga
    purge_reason TEXT,                         -- "ttl_expired", "rating_low", "manual"
    recorded_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT agent_id_not_empty_metric CHECK (agent_id != ''),
    CONSTRAINT metric_type_valid CHECK (metric_type IN ('purge', 'size', 'chunk_count', 'health')),
    CONSTRAINT metric_value_non_negative CHECK (metric_value >= 0)
);

-- Índices para análise histórica
CREATE INDEX idx_agent_memory_metrics_agent_id
    ON agent_memory_metrics (agent_id, recorded_at DESC);

CREATE INDEX idx_agent_memory_metrics_type
    ON agent_memory_metrics (metric_type, recorded_at DESC);

-- =====================================================================
-- 4. AGENT_MEMORY_PURGE_LOG — Log de purgas (append-only)
-- =====================================================================
-- Auditoria de todas as purgas (R10 policy enforcement)

CREATE TABLE IF NOT EXISTS agent_memory_purge_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id TEXT NOT NULL,
    purge_timestamp TIMESTAMPTZ DEFAULT NOW(),
    policy_applied TEXT NOT NULL,              -- "ttl_expired", "rating_low", "manual"
    total_rows_deleted INT DEFAULT 0,
    total_bytes_freed BIGINT DEFAULT 0,
    memory_size_before_mb FLOAT8,
    memory_size_after_mb FLOAT8,
    chunk_count_before INT,
    chunk_count_after INT,
    purge_duration_ms INT,                     -- Duração da operação em ms
    executed_by TEXT DEFAULT 'system',         -- "system" ou user_id
    notes JSONB DEFAULT NULL,                  -- Metadados adicionais

    CONSTRAINT agent_id_not_empty_log CHECK (agent_id != '')
);

-- Índices para auditoria
CREATE INDEX idx_agent_memory_purge_log_agent_id
    ON agent_memory_purge_log (agent_id, purge_timestamp DESC);

CREATE INDEX idx_agent_memory_purge_log_policy
    ON agent_memory_purge_log (policy_applied, purge_timestamp DESC);

-- =====================================================================
-- 5. STORED PROCEDURES — Purga automática (R10)
-- =====================================================================

-- Função: purgar cache expirado
CREATE OR REPLACE FUNCTION purge_expired_agent_memory(
    p_agent_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    agent_id TEXT,
    rows_deleted BIGINT,
    bytes_freed BIGINT,
    memory_before_mb FLOAT8,
    memory_after_mb FLOAT8
) AS $$
DECLARE
    v_agent_id TEXT;
    v_memory_before BIGINT;
    v_memory_after BIGINT;
    v_rows_deleted BIGINT;
    v_bytes_freed BIGINT;
    v_start_time TIMESTAMPTZ;
BEGIN
    v_start_time := NOW();

    -- Se agent_id não foi fornecido, purgar para todos
    FOR v_agent_id IN
        SELECT DISTINCT agent_id FROM agent_memory
        WHERE expires_at <= NOW()
        UNION
        SELECT DISTINCT agent_id FROM agent_memory
        WHERE user_rating < 2 AND created_at < (NOW() - INTERVAL '7 days')
    LOOP
        -- Calcular tamanho antes
        SELECT COALESCE(SUM(memory_size_bytes), 0) INTO v_memory_before
        FROM agent_memory
        WHERE agent_id = v_agent_id;

        -- Deletar rows expiradas
        DELETE FROM agent_memory
        WHERE agent_id = v_agent_id
        AND (expires_at <= NOW()
             OR (user_rating < 2 AND created_at < (NOW() - INTERVAL '7 days')));

        v_rows_deleted := FOUND::INTEGER;
        v_bytes_freed := v_memory_before - COALESCE((
            SELECT SUM(memory_size_bytes) FROM agent_memory WHERE agent_id = v_agent_id
        ), 0);

        -- Calcular tamanho depois
        SELECT COALESCE(SUM(memory_size_bytes), 0) INTO v_memory_after
        FROM agent_memory
        WHERE agent_id = v_agent_id;

        -- Log purga
        INSERT INTO agent_memory_purge_log (
            agent_id, total_rows_deleted, total_bytes_freed,
            memory_size_before_mb, memory_size_after_mb,
            purge_duration_ms, executed_by, policy_applied
        ) VALUES (
            v_agent_id, v_rows_deleted, v_bytes_freed,
            v_memory_before / 1024.0 / 1024.0,
            v_memory_after / 1024.0 / 1024.0,
            EXTRACT(EPOCH FROM (NOW() - v_start_time))::INTEGER * 1000,
            'system',
            CASE
                WHEN v_rows_deleted > 0 THEN 'ttl_expired|rating_low'
                ELSE 'no_action'
            END
        );

        -- Update metrics
        INSERT INTO agent_memory_metrics (
            agent_id, metric_type, metric_value, memory_size_mb,
            chunk_count, deleted_count, last_purge_at, purge_reason
        ) VALUES (
            v_agent_id, 'purge', v_rows_deleted::FLOAT8,
            v_memory_after / 1024.0 / 1024.0,
            (SELECT COUNT(*) FROM agent_memory WHERE agent_id = v_agent_id),
            v_rows_deleted,
            NOW(),
            'ttl_expired|rating_low'
        );

        -- Return resultado
        RETURN QUERY SELECT
            v_agent_id,
            v_rows_deleted,
            v_bytes_freed,
            v_memory_before / 1024.0 / 1024.0,
            v_memory_after / 1024.0 / 1024.0;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função: calcular metrics do agente
CREATE OR REPLACE FUNCTION refresh_agent_memory_metrics(p_agent_id TEXT)
RETURNS TABLE (
    agent_id TEXT,
    memory_size_mb FLOAT8,
    chunk_count INT,
    oldest_entry_age_days INT,
    avg_rating FLOAT8
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        am.agent_id,
        COALESCE(SUM(am.memory_size_bytes), 0) / 1024.0 / 1024.0 AS memory_size_mb,
        COUNT(am.id)::INT AS chunk_count,
        EXTRACT(EPOCH FROM (NOW() - MIN(am.created_at)))::INT / 86400 AS oldest_entry_age_days,
        ROUND(AVG(CASE WHEN am.user_rating IS NOT NULL THEN am.user_rating ELSE NULL END)::NUMERIC, 2)::FLOAT8 AS avg_rating
    FROM agent_memory am
    WHERE am.agent_id = p_agent_id
    GROUP BY am.agent_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função: inserir memory com dedup por checksum
CREATE OR REPLACE FUNCTION insert_agent_memory_dedup(
    p_agent_id TEXT,
    p_session_id TEXT,
    p_memory_key TEXT,
    p_memory_value JSONB,
    p_ttl_minutes INT DEFAULT 480
)
RETURNS UUID AS $$
DECLARE
    v_checksum VARCHAR(32);
    v_id UUID;
    v_expires_at TIMESTAMPTZ;
BEGIN
    -- Calcular checksum
    v_checksum := md5(p_memory_value::TEXT);
    v_expires_at := NOW() + (p_ttl_minutes || ' minutes')::INTERVAL;

    -- Verificar se já existe com mesmo checksum (dedup)
    SELECT id INTO v_id
    FROM agent_memory
    WHERE agent_id = p_agent_id
    AND checksum = v_checksum
    AND memory_key = p_memory_key
    LIMIT 1;

    IF FOUND THEN
        -- Update expires_at se já existe
        UPDATE agent_memory
        SET expires_at = v_expires_at
        WHERE id = v_id;
        RETURN v_id;
    END IF;

    -- Inserir novo record
    INSERT INTO agent_memory (
        agent_id, session_id, memory_key, memory_value,
        memory_size_bytes, expires_at, checksum
    ) VALUES (
        p_agent_id, p_session_id, p_memory_key, p_memory_value,
        OCTET_LENGTH(p_memory_value::TEXT),
        v_expires_at,
        v_checksum
    )
    RETURNING agent_memory.id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================================
-- 6. TRIGGERS — Atualizar agent_state com feedback
-- =====================================================================

CREATE OR REPLACE FUNCTION update_agent_state_on_rating()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_rating IS NOT NULL AND NEW.user_rating != OLD.user_rating THEN
        -- Atualizar agent_state com novo rating agregado
        UPDATE agent_state
        SET
            feedback_count = feedback_count + 1,
            avg_user_rating = (
                SELECT AVG(user_rating)
                FROM agent_memory
                WHERE agent_id = NEW.agent_id
                AND user_rating IS NOT NULL
            ),
            last_updated = NOW()
        WHERE agent_id = NEW.agent_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_agent_memory_rating_update
    AFTER UPDATE ON agent_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_state_on_rating();

-- =====================================================================
-- 7. GRANTS — Permissões para aplicação
-- =====================================================================

-- Tables
GRANT SELECT, INSERT, UPDATE, DELETE ON agent_memory TO "authenticated";
GRANT SELECT, INSERT, UPDATE ON agent_state TO "authenticated";
GRANT INSERT ON agent_memory_metrics TO "authenticated";
GRANT SELECT ON agent_memory_purge_log TO "authenticated";

-- Functions
GRANT EXECUTE ON FUNCTION purge_expired_agent_memory TO "authenticated";
GRANT EXECUTE ON FUNCTION refresh_agent_memory_metrics TO "authenticated";
GRANT EXECUTE ON FUNCTION insert_agent_memory_dedup TO "authenticated";

-- Procedure admin-only
GRANT EXECUTE ON FUNCTION purge_expired_agent_memory TO "service_role";

COMMIT;

-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DROP TRIGGER IF EXISTS trg_agent_memory_rating_update ON agent_memory;
-- DROP FUNCTION IF EXISTS update_agent_state_on_rating();
-- DROP FUNCTION IF EXISTS insert_agent_memory_dedup(TEXT, TEXT, TEXT, JSONB, INT);
-- DROP FUNCTION IF EXISTS refresh_agent_memory_metrics(TEXT);
-- DROP FUNCTION IF EXISTS purge_expired_agent_memory(TEXT);
-- DROP TABLE IF EXISTS agent_memory_purge_log CASCADE;
-- DROP TABLE IF EXISTS agent_memory_metrics CASCADE;
-- DROP TABLE IF EXISTS agent_state CASCADE;
-- DROP TABLE IF EXISTS agent_memory CASCADE;
--
-- COMMIT;
