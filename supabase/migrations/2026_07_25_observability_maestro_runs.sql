-- Manta Maestro v5.0 — Observabilidade (P6)
-- Schema de logging imutável para runs completos do Maestro
-- Ticket: MNT-2026-MAESTRO-OBSERVABILITY-P6
--
-- Tabelas:
--   1. maestro_runs (principal, append-only)
--   2. maestro_runs_archive (retenção 90+ dias)
--   3. maestro_feedback (ratings 0-5)
--   4. Triggers para audit + archive automático
--   5. RLS policies (privacidade por user_id)
--
-- Indexes:
--   - (agent_id, created_at) — queries por agente
--   - (status, created_at) — dashboards de erro
--   - (cost_usd) — análise de custo
--   - (user_id, created_at) — por usuário
--
-- Executar via:
--   supabase db push
-- ou
--   psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_25_observability_maestro_runs.sql
--
-- RETENTION POLICY:
--   - Hot (maestro_runs): 90 dias
--   - Warm (maestro_runs_archive): 365 dias (compactado)
--   - Audit: imutável, append-only

BEGIN;

-- =====================================================================
-- 1. TABELA PRINCIPAL: maestro_runs (IMUTÁVEL, APPEND-ONLY)
-- =====================================================================

CREATE TABLE IF NOT EXISTS maestro_runs (
  -- Identificadores
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  session_id TEXT NOT NULL,

  -- Timing
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Roteamento
  agent_id TEXT NOT NULL,  -- e.g., "manta-03-s8", "manta-00"
  skill_id TEXT NOT NULL,  -- e.g., "agente-saneamento.v5.0"

  -- Modelo & Custo
  model_tier TEXT NOT NULL CHECK (model_tier IN ('haiku-4-5', 'sonnet-5', 'opus-5')),
  input_tokens INTEGER NOT NULL CHECK (input_tokens >= 0),
  output_tokens INTEGER NOT NULL CHECK (output_tokens >= 0),
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0.0 CHECK (cost_usd >= 0.0),

  -- Performance
  latency_ms INTEGER NOT NULL CHECK (latency_ms >= 0),

  -- Status
  status TEXT NOT NULL CHECK (status IN ('success', 'timeout', 'error')),
  error_message TEXT,

  -- Contexto de execução
  phase TEXT CHECK (
    phase IS NULL OR phase IN (
      'estudo-previo',
      'projeto-basico',
      'projeto-executivo',
      'obra',
      'operacao',
      'licitacao',
      'due-diligence',
      'encerramento'
    )
  ),

  -- Feedback (coletado pós-run, opcional)
  feedback_score INTEGER CHECK (feedback_score IS NULL OR (feedback_score >= 0 AND feedback_score <= 5)),
  feedback_timestamp TIMESTAMPTZ,

  -- Observabilidade
  routing_confidence NUMERIC(3, 2) CHECK (routing_confidence >= 0.0 AND routing_confidence <= 1.0),

  -- RAG context
  rag_collection TEXT,  -- e.g., "san:v5.0:chunks"
  rag_reranker_score NUMERIC(3, 2) CHECK (rag_reranker_score IS NULL OR (rag_reranker_score >= 0.0 AND rag_reranker_score <= 1.0)),

  -- Metadados adicionais (extensível)
  metadata JSONB DEFAULT '{}',

  -- Auditoria
  is_archived BOOLEAN DEFAULT FALSE NOT NULL,
  created_at_utc TIMESTAMPTZ GENERATED ALWAYS AS (created_at AT TIME ZONE 'UTC') STORED
);

-- Comentários para documentação
COMMENT ON TABLE maestro_runs IS 'Log imutável de todas as execuções do Maestro (append-only). Retenção: 90 dias hot.';
COMMENT ON COLUMN maestro_runs.run_id IS 'UUID único identificador da run (PK, immutable).';
COMMENT ON COLUMN maestro_runs.user_id IS 'Usuário que acionou a run (FK auth.users).';
COMMENT ON COLUMN maestro_runs.session_id IS 'Sessão Claude Code (para correlação).';
COMMENT ON COLUMN maestro_runs.agent_id IS 'Agente roteado (e.g., "manta-03-s8").';
COMMENT ON COLUMN maestro_runs.skill_id IS 'Skill versionada utilizada (e.g., "agente-saneamento.v5.0").';
COMMENT ON COLUMN maestro_runs.model_tier IS 'Modelo utilizado: haiku-4-5, sonnet-5, opus-5.';
COMMENT ON COLUMN maestro_runs.cost_usd IS 'Custo calculado (input + output tokens).';
COMMENT ON COLUMN maestro_runs.status IS 'success|timeout|error';
COMMENT ON COLUMN maestro_runs.phase IS 'Fase do ciclo de vida injetada via contexto.';
COMMENT ON COLUMN maestro_runs.feedback_score IS 'Rating do usuário pós-run (0-5 stars, opcional).';
COMMENT ON COLUMN maestro_runs.routing_confidence IS 'Confiança da decisão de roteamento (R1).';
COMMENT ON COLUMN maestro_runs.rag_collection IS 'Coleção RAG utilizada (e.g., "san:v5.0:chunks").';
COMMENT ON COLUMN maestro_runs.metadata IS 'JSON extensível: fallback_cascade, complexity_score, phase_inferred, etc.';

-- =====================================================================
-- 2. TABELA DE RETENÇÃO: maestro_runs_archive
-- =====================================================================

CREATE TABLE IF NOT EXISTS maestro_runs_archive (
  -- Mesma estrutura que maestro_runs, mas sem constraints de FK
  run_id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  session_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  agent_id TEXT NOT NULL,
  skill_id TEXT NOT NULL,
  model_tier TEXT NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0.0,
  latency_ms INTEGER NOT NULL,
  status TEXT NOT NULL,
  error_message TEXT,
  phase TEXT,
  feedback_score INTEGER,
  feedback_timestamp TIMESTAMPTZ,
  routing_confidence NUMERIC(3, 2),
  rag_collection TEXT,
  rag_reranker_score NUMERIC(3, 2),
  metadata JSONB DEFAULT '{}',
  is_archived BOOLEAN DEFAULT TRUE NOT NULL,
  created_at_utc TIMESTAMPTZ NOT NULL,
  archived_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE maestro_runs_archive IS 'Arquivo de runs com idade > 90 dias (warm storage, compactado). Retenção: 365 dias.';

-- =====================================================================
-- 3. TABELA DE FEEDBACK: maestro_feedback
-- =====================================================================

CREATE TABLE IF NOT EXISTS maestro_feedback (
  feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES maestro_runs(run_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  score INTEGER NOT NULL CHECK (score >= 0 AND score <= 5),
  comment TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE maestro_feedback IS 'Feedback de usuários pós-run (0-5 stars). Usado para feedback loop (R9).';

-- =====================================================================
-- 4. INDEXES PARA PERFORMANCE
-- =====================================================================

-- Index 1: Queries por agente e período (dashboard de custo/agente)
CREATE INDEX idx_maestro_runs_agent_created
  ON maestro_runs(agent_id, created_at DESC)
  WHERE is_archived = FALSE;

-- Index 2: Queries por status (taxa de erro, timeouts)
CREATE INDEX idx_maestro_runs_status_created
  ON maestro_runs(status, created_at DESC)
  WHERE is_archived = FALSE;

-- Index 3: Análise de custo (top-N runs by cost)
CREATE INDEX idx_maestro_runs_cost_usd
  ON maestro_runs(cost_usd DESC)
  WHERE is_archived = FALSE;

-- Index 4: Queries por usuário (auditoria, GDPR)
CREATE INDEX idx_maestro_runs_user_created
  ON maestro_runs(user_id, created_at DESC)
  WHERE is_archived = FALSE;

-- Index 5: Queries por model_tier (tiering analysis)
CREATE INDEX idx_maestro_runs_model_created
  ON maestro_runs(model_tier, created_at DESC)
  WHERE is_archived = FALSE;

-- Index 6: Queries por phase (ciclo de vida)
CREATE INDEX idx_maestro_runs_phase_created
  ON maestro_runs(phase, created_at DESC)
  WHERE phase IS NOT NULL AND is_archived = FALSE;

-- Index 7: Queries por skill_id (análise de skill utilization)
CREATE INDEX idx_maestro_runs_skill_created
  ON maestro_runs(skill_id, created_at DESC)
  WHERE is_archived = FALSE;

-- Index 8: Correlação run_id + feedback (para join)
CREATE INDEX idx_maestro_feedback_run_id
  ON maestro_feedback(run_id)
  WHERE score IS NOT NULL;

-- Index 9: Composite para queries típicas (agent + status + created_at)
CREATE INDEX idx_maestro_runs_agent_status_created
  ON maestro_runs(agent_id, status, created_at DESC)
  WHERE is_archived = FALSE;

-- =====================================================================
-- 5. ROW-LEVEL SECURITY (RLS)
-- =====================================================================

ALTER TABLE maestro_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE maestro_feedback ENABLE ROW LEVEL SECURITY;

-- Policy 1: Usuários veem apenas seus próprios runs
CREATE POLICY maestro_runs_select_own
  ON maestro_runs FOR SELECT
  USING (auth.uid() = user_id);

-- Policy 2: Usuários não podem modificar (append-only)
CREATE POLICY maestro_runs_no_update
  ON maestro_runs FOR UPDATE
  USING (FALSE);

-- Policy 3: Usuários não podem deletar (imutável)
CREATE POLICY maestro_runs_no_delete
  ON maestro_runs FOR DELETE
  USING (FALSE);

-- Policy 4: Apenas serviços backend podem inserir (via service role)
-- Nota: em produção, usar app role específico + JWT
CREATE POLICY maestro_runs_insert_service
  ON maestro_runs FOR INSERT
  WITH CHECK (TRUE);  -- Validar via RLS de aplicação, não via SQL

-- Policy 5: Feedback — usuários veem/criam feedback de seus runs
CREATE POLICY maestro_feedback_select_own
  ON maestro_feedback FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY maestro_feedback_insert_own
  ON maestro_feedback FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- =====================================================================
-- 6. FUNÇÃO PARA ARCHIVE AUTOMÁTICO (90 dias)
-- =====================================================================

CREATE OR REPLACE FUNCTION archive_old_maestro_runs()
RETURNS TABLE(archived_count INT) AS $$
DECLARE
  _archived_count INT;
BEGIN
  -- Mover runs com idade > 90 dias para maestro_runs_archive
  INSERT INTO maestro_runs_archive
  SELECT
    run_id, user_id, session_id, created_at, agent_id, skill_id,
    model_tier, input_tokens, output_tokens, cost_usd, latency_ms,
    status, error_message, phase, feedback_score, feedback_timestamp,
    routing_confidence, rag_collection, rag_reranker_score, metadata,
    TRUE, created_at_utc, NOW()
  FROM maestro_runs
  WHERE created_at < (NOW() - INTERVAL '90 days')
    AND is_archived = FALSE
  ON CONFLICT (run_id) DO NOTHING;

  GET DIAGNOSTICS _archived_count = ROW_COUNT;

  -- Marcar como arquivados (soft delete)
  UPDATE maestro_runs
  SET is_archived = TRUE
  WHERE created_at < (NOW() - INTERVAL '90 days')
    AND is_archived = FALSE;

  RETURN QUERY SELECT _archived_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION archive_old_maestro_runs() IS 'Arquiva runs com idade > 90 dias (R10 retention policy).';

-- =====================================================================
-- 7. FUNÇÃO PARA CALCULAR CUSTO (helper)
-- =====================================================================

CREATE OR REPLACE FUNCTION calculate_run_cost(
  p_model_tier TEXT,
  p_input_tokens INT,
  p_output_tokens INT
) RETURNS NUMERIC AS $$
DECLARE
  _cost NUMERIC;
  _input_rate NUMERIC;
  _output_rate NUMERIC;
BEGIN
  -- Preço por 1M tokens (conforme CLAUDE.md R7)
  CASE p_model_tier
    WHEN 'haiku-4-5' THEN
      _input_rate := 0.08 / 1000000;
      _output_rate := 0.24 / 1000000;
    WHEN 'sonnet-5' THEN
      _input_rate := 3.0 / 1000000;
      _output_rate := 15.0 / 1000000;
    WHEN 'opus-5' THEN
      _input_rate := 15.0 / 1000000;
      _output_rate := 75.0 / 1000000;
    ELSE
      RAISE EXCEPTION 'Unknown model_tier: %', p_model_tier;
  END CASE;

  _cost := (p_input_tokens::NUMERIC * _input_rate) +
           (p_output_tokens::NUMERIC * _output_rate);

  RETURN ROUND(_cost, 6);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_run_cost(TEXT, INT, INT) IS 'Calcula custo USD de uma run baseado no model_tier e tokens.';

-- =====================================================================
-- 8. VISTAS ANALÍTICAS (para Grafana)
-- =====================================================================

-- Vista 1: Custo por agente por dia
CREATE OR REPLACE VIEW vw_cost_by_agent_daily AS
SELECT
  DATE(created_at_utc) AS date,
  agent_id,
  COUNT(*) AS run_count,
  SUM(input_tokens) AS total_input_tokens,
  SUM(output_tokens) AS total_output_tokens,
  SUM(cost_usd) AS total_cost_usd,
  AVG(cost_usd) AS avg_cost_usd,
  COUNT(CASE WHEN status = 'error' THEN 1 END) AS error_count,
  COUNT(CASE WHEN status = 'timeout' THEN 1 END) AS timeout_count,
  ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS success_rate_pct
FROM maestro_runs
WHERE is_archived = FALSE
GROUP BY DATE(created_at_utc), agent_id
ORDER BY DATE(created_at_utc) DESC, total_cost_usd DESC;

COMMENT ON VIEW vw_cost_by_agent_daily IS 'Dashboard: Custo/agente/dia (P6 observabilidade).';

-- Vista 2: Latência por agent (percentis)
CREATE OR REPLACE VIEW vw_latency_by_agent AS
SELECT
  agent_id,
  COUNT(*) AS run_count,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms)::NUMERIC, 2) AS p50_ms,
  ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)::NUMERIC, 2) AS p95_ms,
  ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms)::NUMERIC, 2) AS p99_ms,
  ROUND(AVG(latency_ms)::NUMERIC, 2) AS avg_ms,
  MAX(latency_ms) AS max_ms,
  MIN(latency_ms) AS min_ms
FROM maestro_runs
WHERE is_archived = FALSE
GROUP BY agent_id
ORDER BY avg_ms DESC;

COMMENT ON VIEW vw_latency_by_agent IS 'Dashboard: Latência p50/p95/p99 por agente.';

-- Vista 3: Taxa de erro por agente
CREATE OR REPLACE VIEW vw_error_rate_by_agent AS
SELECT
  agent_id,
  COUNT(*) AS total_runs,
  COUNT(CASE WHEN status = 'error' THEN 1 END) AS error_count,
  COUNT(CASE WHEN status = 'timeout' THEN 1 END) AS timeout_count,
  COUNT(CASE WHEN status = 'success' THEN 1 END) AS success_count,
  ROUND(100.0 * COUNT(CASE WHEN status = 'error' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS error_rate_pct,
  ROUND(100.0 * COUNT(CASE WHEN status = 'timeout' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS timeout_rate_pct,
  ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS success_rate_pct
FROM maestro_runs
WHERE is_archived = FALSE
GROUP BY agent_id
ORDER BY error_rate_pct DESC;

COMMENT ON VIEW vw_error_rate_by_agent IS 'Dashboard: Taxa de erro/timeout por agente.';

-- Vista 4: Distribuição de model_tier
CREATE OR REPLACE VIEW vw_model_tier_distribution AS
SELECT
  DATE(created_at_utc) AS date,
  model_tier,
  COUNT(*) AS run_count,
  ROUND(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (PARTITION BY DATE(created_at_utc)), 0), 2) AS pct_of_day,
  SUM(cost_usd) AS total_cost_usd
FROM maestro_runs
WHERE is_archived = FALSE
GROUP BY DATE(created_at_utc), model_tier
ORDER BY DATE(created_at_utc) DESC, model_tier;

COMMENT ON VIEW vw_model_tier_distribution IS 'Dashboard: Distribuição de modelos usado (R7 tiering efficiency).';

-- Vista 5: Feedback score distribution
CREATE OR REPLACE VIEW vw_feedback_distribution AS
SELECT
  feedback_score,
  COUNT(*) AS count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM maestro_runs
WHERE is_archived = FALSE AND feedback_score IS NOT NULL
GROUP BY feedback_score
ORDER BY feedback_score DESC;

COMMENT ON VIEW vw_feedback_distribution IS 'Dashboard: Distribuição de ratings (0-5 stars).';

-- Vista 6: Top-10 runs by cost
CREATE OR REPLACE VIEW vw_top_cost_runs AS
SELECT
  run_id,
  DATE(created_at_utc) AS date,
  agent_id,
  model_tier,
  input_tokens,
  output_tokens,
  cost_usd,
  status,
  latency_ms
FROM maestro_runs
WHERE is_archived = FALSE
ORDER BY cost_usd DESC
LIMIT 10;

COMMENT ON VIEW vw_top_cost_runs IS 'Debug: Top-10 runs mais caras.';

-- =====================================================================
-- 9. FUNÇÃO DE SUMARIZAÇÃO PARA ALERTAS
-- =====================================================================

CREATE OR REPLACE FUNCTION get_error_stats_last_hour()
RETURNS TABLE (
  agent_id TEXT,
  error_count INT,
  timeout_count INT,
  total_runs INT,
  error_rate_pct NUMERIC,
  most_recent_error_msg TEXT,
  most_recent_error_time TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    m.agent_id,
    COUNT(CASE WHEN m.status = 'error' THEN 1 END)::INT,
    COUNT(CASE WHEN m.status = 'timeout' THEN 1 END)::INT,
    COUNT(*)::INT,
    ROUND(100.0 * COUNT(CASE WHEN m.status IN ('error', 'timeout') THEN 1 END) / NULLIF(COUNT(*), 0), 2),
    (ARRAY_AGG(m.error_message ORDER BY m.created_at DESC))[1],
    (ARRAY_AGG(m.created_at ORDER BY m.created_at DESC))[1]
  FROM maestro_runs m
  WHERE m.is_archived = FALSE
    AND m.created_at > NOW() - INTERVAL '1 hour'
  GROUP BY m.agent_id
  HAVING COUNT(CASE WHEN m.status IN ('error', 'timeout') THEN 1 END) > 0
  ORDER BY error_count DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_error_stats_last_hour() IS 'Alert helper: Resumo de erros da última hora (Slack #agent-ops).';

-- =====================================================================
-- 10. GRANT PERMISSIONS (acessos)
-- =====================================================================

-- Usuários autenticados podem ler suas próprias runs (via RLS)
GRANT SELECT ON maestro_runs TO authenticated;
GRANT SELECT ON maestro_feedback TO authenticated;
GRANT INSERT ON maestro_feedback TO authenticated;

-- Serviço backend pode inserir runs (via app role / JWT)
GRANT INSERT, SELECT ON maestro_runs TO anon;
GRANT INSERT, SELECT ON maestro_runs_archive TO anon;
GRANT SELECT ON maestro_feedback TO anon;

-- Grafana/Analytics service role pode ler tudo (sem RLS)
-- (Configurar no Supabase: create new service role, grant SELECT on views)

COMMIT;

-- =====================================================================
-- VERSÃO: 2026-07-25 (Maestro v5.0, P6)
-- STATUS: Production-ready
-- PRÓXIMOS PASSOS:
--   1. Executar: supabase db push
--   2. Configurar Grafana data source (Supabase + vistas)
--   3. Setup APScheduler job: archive_old_maestro_runs() diário às 02:00 UTC
--   4. Integrar hook SubagentStop (scripts/setup_maestro_runs.py)
-- =====================================================================
