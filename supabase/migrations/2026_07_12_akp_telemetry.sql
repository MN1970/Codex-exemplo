-- Academic Knowledge Pipeline (WF-AKP-001) — Telemetria
-- Ticket: WF-AKP-001 backlog item #9 (Manta 17 Telemetry — camada de dados)
--
-- Motivação:
--   Sem observabilidade, é impossível provar ROI da coleção academic-knowledge.
--   Não sabemos: (a) frequência de routing por agente, (b) top KEs mais
--   consumidos, (c) taxa de fallback, (d) distribuição de similaridade, (e)
--   queries que retornaram top-1 fraco (candidato p/ próximo sprint de curadoria).
--
-- Este arquivo entrega a CAMADA DE DADOS. O agente Manta 17 Telemetry (SKILL.md,
-- roteador, artefato React) é backlog separado — este schema já suporta.
--
-- MIGRAÇÃO CANDIDATA, aditiva sobre stages 4-6. Idempotente.

BEGIN;

-- =====================================================================
-- 1. Tabela de log de queries
-- =====================================================================
-- 1 linha / chamada de match_academic_knowledge*. Alta cardinalidade
-- esperada — particionar por RANGE em query_ts se volume > 10M rows.
CREATE TABLE IF NOT EXISTS agent_query_log (
  id               BIGSERIAL PRIMARY KEY,
  agent_slug       TEXT NOT NULL,          -- agente-portos, agente-saneamento, ...
  collection_slug  TEXT NOT NULL DEFAULT 'academic-knowledge',
  query_text       TEXT,                    -- a query natural (pode ser NULL se só embedding)
  query_source     TEXT NOT NULL DEFAULT 'agent' CHECK (query_source IN (
                     'agent',        -- chamada normal do agente vertical
                     'smoke_test',   -- rodada do akp_smoke_test.py
                     'maestro',      -- Maestro perguntou direto
                     'manual',       -- operador SQL
                     'api'           -- consumo externo
                   )),
  filter_segmento  TEXT,                    -- filtro aplicado (se houver)
  filter_tipo      TEXT,
  matched_ke_ids   TEXT[] NOT NULL DEFAULT '{}',  -- IDs retornados no top-N
  top_similarity   FLOAT,                   -- similaridade do top-1
  match_count      INTEGER NOT NULL DEFAULT 5,
  hybrid_used      BOOLEAN NOT NULL DEFAULT FALSE,  -- FALSE=match_academic_knowledge, TRUE=hybrid
  latency_ms       INTEGER,                 -- opcional, best-effort
  session_id       TEXT,                    -- opcional, correlaciona com Maestro session
  query_ts         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_query_log_ts       ON agent_query_log(query_ts DESC);
CREATE INDEX IF NOT EXISTS idx_agent_query_log_agent    ON agent_query_log(agent_slug, query_ts DESC);
CREATE INDEX IF NOT EXISTS idx_agent_query_log_segmento ON agent_query_log(filter_segmento) WHERE filter_segmento IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_query_log_source   ON agent_query_log(query_source);

-- =====================================================================
-- 2. Tabela agregada de KE hits (contadores pré-computados)
-- =====================================================================
-- Alimentada por trigger — evita full scan em agent_query_log p/ ranking.
CREATE TABLE IF NOT EXISTS agent_ke_hits (
  ke_id          TEXT NOT NULL REFERENCES academic_knowledge_elements(id) ON DELETE CASCADE,
  agent_slug     TEXT NOT NULL,
  hit_count      BIGINT NOT NULL DEFAULT 0,
  last_hit_at    TIMESTAMPTZ,
  first_hit_at   TIMESTAMPTZ,
  PRIMARY KEY (ke_id, agent_slug)
);

CREATE INDEX IF NOT EXISTS idx_agent_ke_hits_agent    ON agent_ke_hits(agent_slug, hit_count DESC);
CREATE INDEX IF NOT EXISTS idx_agent_ke_hits_recent   ON agent_ke_hits(last_hit_at DESC);

-- Trigger: cada linha nova em agent_query_log incrementa hits de todos os KEs em matched_ke_ids
CREATE OR REPLACE FUNCTION agent_query_log_update_hits() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.matched_ke_ids IS NULL OR array_length(NEW.matched_ke_ids, 1) IS NULL THEN
    RETURN NEW;
  END IF;
  INSERT INTO agent_ke_hits (ke_id, agent_slug, hit_count, last_hit_at, first_hit_at)
  SELECT unnest(NEW.matched_ke_ids), NEW.agent_slug, 1, NEW.query_ts, NEW.query_ts
  ON CONFLICT (ke_id, agent_slug) DO UPDATE
    SET hit_count   = agent_ke_hits.hit_count + 1,
        last_hit_at = EXCLUDED.last_hit_at;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agent_query_log_hits ON agent_query_log;
CREATE TRIGGER trg_agent_query_log_hits
  AFTER INSERT ON agent_query_log
  FOR EACH ROW EXECUTE FUNCTION agent_query_log_update_hits();

-- =====================================================================
-- 3. Eventos de fallback (Maestro reencaminhou)
-- =====================================================================
CREATE TABLE IF NOT EXISTS agent_fallback_events (
  id                BIGSERIAL PRIMARY KEY,
  from_agent_slug   TEXT NOT NULL,          -- agente que declinou/falhou
  to_agent_slug     TEXT NOT NULL,          -- para onde o Maestro reencaminhou
  reason            TEXT NOT NULL CHECK (reason IN (
                     'low_confidence',    -- primário sem KE relevante
                     'explicit_handoff',  -- primário pediu explicitamente
                     'timeout',
                     'error',
                     'other'
                   )),
  session_id        TEXT,
  event_ts          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fallback_events_from ON agent_fallback_events(from_agent_slug, event_ts DESC);
CREATE INDEX IF NOT EXISTS idx_fallback_events_ts   ON agent_fallback_events(event_ts DESC);

-- =====================================================================
-- 4. Views para consumo pelo painel / CLI de report
-- =====================================================================

-- 4.1 Frequência de routing por agente (últimos 30 dias)
CREATE OR REPLACE VIEW v_akp_routing_frequency AS
SELECT
  agent_slug,
  COUNT(*)                                                                  AS queries_30d,
  COUNT(*) FILTER (WHERE query_ts > NOW() - INTERVAL '7 days')              AS queries_7d,
  COUNT(*) FILTER (WHERE query_ts > NOW() - INTERVAL '1 day')               AS queries_24h,
  COUNT(DISTINCT DATE(query_ts))                                             AS days_active,
  AVG(top_similarity)::NUMERIC(4,3)                                          AS avg_top_similarity,
  ROUND(100.0 * COUNT(*) FILTER (WHERE hybrid_used) / NULLIF(COUNT(*),0), 1) AS pct_hybrid
FROM agent_query_log
WHERE query_ts > NOW() - INTERVAL '30 days'
GROUP BY agent_slug
ORDER BY queries_30d DESC;

COMMENT ON VIEW v_akp_routing_frequency IS
  'Volume de queries por agente, últimos 30d/7d/24h + share de uso do modo hybrid.';

-- 4.2 Top KEs consumidos (por agente)
CREATE OR REPLACE VIEW v_akp_top_kes AS
SELECT
  h.agent_slug,
  h.ke_id,
  ake.titulo,
  ake.tipo,
  ake.segmento,
  ake.tese_id,
  h.hit_count,
  h.last_hit_at,
  RANK() OVER (PARTITION BY h.agent_slug ORDER BY h.hit_count DESC) AS rank_in_agent
FROM agent_ke_hits h
JOIN academic_knowledge_elements ake ON ake.id = h.ke_id
ORDER BY h.agent_slug, h.hit_count DESC;

COMMENT ON VIEW v_akp_top_kes IS
  'KEs mais consumidos por agente, com rank interno. Alimenta o painel Manta 17.';

-- 4.3 Health de similaridade (p50/p95 por segmento, últimos 7d)
CREATE OR REPLACE VIEW v_akp_similarity_health AS
SELECT
  COALESCE(filter_segmento, '(sem filtro)') AS segmento,
  COUNT(*)                                                          AS n_queries,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY top_similarity)::NUMERIC(4,3) AS p50_top_sim,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY top_similarity)::NUMERIC(4,3) AS p95_top_sim,
  MIN(top_similarity)::NUMERIC(4,3) AS min_top_sim,
  MAX(top_similarity)::NUMERIC(4,3) AS max_top_sim,
  COUNT(*) FILTER (WHERE top_similarity < 0.30) AS n_below_030,
  COUNT(*) FILTER (WHERE top_similarity < 0.20) AS n_below_020
FROM agent_query_log
WHERE query_ts > NOW() - INTERVAL '7 days'
  AND top_similarity IS NOT NULL
GROUP BY 1
ORDER BY 1;

COMMENT ON VIEW v_akp_similarity_health IS
  'Distribuição de similaridade top-1 por segmento (últimos 7d). p95 baixo = coleção pobre nesse segmento.';

-- 4.4 Gap candidates — queries com top-1 fraco (próximo sprint de curadoria)
CREATE OR REPLACE VIEW v_akp_gap_candidates AS
SELECT
  filter_segmento AS segmento,
  query_text,
  COUNT(*)                             AS n_occurrences,
  AVG(top_similarity)::NUMERIC(4,3)    AS avg_top_sim,
  MAX(query_ts)                        AS last_seen
FROM agent_query_log
WHERE query_ts > NOW() - INTERVAL '30 days'
  AND query_text IS NOT NULL
  AND top_similarity IS NOT NULL
  AND top_similarity < 0.30
  AND query_source IN ('agent', 'maestro')  -- exclui smoke_test
GROUP BY filter_segmento, query_text
HAVING COUNT(*) >= 2                          -- só queries que se repetem
ORDER BY n_occurrences DESC, avg_top_sim ASC
LIMIT 100;

COMMENT ON VIEW v_akp_gap_candidates IS
  'Queries repetidas com top-1 fraco (últimos 30d). Cada linha = candidato a novo KE curado.';

-- =====================================================================
-- 5. Função wrapper: match + log automático
-- =====================================================================
-- Simplifica a instrumentação: o agente chama uma função só, logging fica implícito.
CREATE OR REPLACE FUNCTION log_akp_query(
  p_agent_slug      TEXT,
  p_query_text      TEXT,
  p_query_embedding vector(1536),
  p_match_count     INTEGER DEFAULT 5,
  p_filter_segmento TEXT    DEFAULT NULL,
  p_filter_tipo     TEXT    DEFAULT NULL,
  p_use_hybrid      BOOLEAN DEFAULT TRUE,
  p_query_source    TEXT    DEFAULT 'agent',
  p_session_id      TEXT    DEFAULT NULL
)
RETURNS TABLE (
  id             TEXT,
  tese_id        TEXT,
  titulo         TEXT,
  chunk          TEXT,
  tipo           TEXT,
  segmento       TEXT,
  citacao_bibtex TEXT,
  similarity     FLOAT
)
LANGUAGE plpgsql AS $$
DECLARE
  matches_rec RECORD;
  matched_ids TEXT[]   := '{}';
  top_sim     FLOAT    := NULL;
BEGIN
  IF p_use_hybrid THEN
    FOR matches_rec IN
      SELECT id, tese_id, titulo, chunk, tipo, segmento, citacao_bibtex, similarity
        FROM match_academic_knowledge_hybrid(
          p_query_text, p_query_embedding, p_match_count,
          p_filter_segmento, p_filter_tipo, p_agent_slug
        )
    LOOP
      matched_ids := array_append(matched_ids, matches_rec.id);
      IF top_sim IS NULL THEN top_sim := matches_rec.similarity; END IF;
      id             := matches_rec.id;
      tese_id        := matches_rec.tese_id;
      titulo         := matches_rec.titulo;
      chunk          := matches_rec.chunk;
      tipo           := matches_rec.tipo;
      segmento       := matches_rec.segmento;
      citacao_bibtex := matches_rec.citacao_bibtex;
      similarity     := matches_rec.similarity;
      RETURN NEXT;
    END LOOP;
  ELSE
    FOR matches_rec IN
      SELECT id, tese_id, titulo, chunk, tipo, segmento, citacao_bibtex, similarity
        FROM match_academic_knowledge(
          p_query_embedding, p_match_count,
          p_filter_segmento, p_filter_tipo, p_agent_slug
        )
    LOOP
      matched_ids := array_append(matched_ids, matches_rec.id);
      IF top_sim IS NULL THEN top_sim := matches_rec.similarity; END IF;
      id             := matches_rec.id;
      tese_id        := matches_rec.tese_id;
      titulo         := matches_rec.titulo;
      chunk          := matches_rec.chunk;
      tipo           := matches_rec.tipo;
      segmento       := matches_rec.segmento;
      citacao_bibtex := matches_rec.citacao_bibtex;
      similarity     := matches_rec.similarity;
      RETURN NEXT;
    END LOOP;
  END IF;

  INSERT INTO agent_query_log (
    agent_slug, collection_slug, query_text, query_source,
    filter_segmento, filter_tipo, matched_ke_ids,
    top_similarity, match_count, hybrid_used, session_id
  ) VALUES (
    p_agent_slug, 'academic-knowledge', p_query_text, p_query_source,
    p_filter_segmento, p_filter_tipo, matched_ids,
    top_sim, p_match_count, p_use_hybrid, p_session_id
  );

  RETURN;
END;
$$;

COMMENT ON FUNCTION log_akp_query IS
  'Wrapper que roda match_academic_knowledge_hybrid (ou legacy) e loga em agent_query_log. Preferir sobre chamadas diretas para observabilidade automática.';

COMMIT;

-- =====================================================================
-- Uso esperado
-- =====================================================================
--
-- Agente vertical (canal instrumentado default):
--   SELECT * FROM log_akp_query(
--     p_agent_slug      := 'agente-portos',
--     p_query_text      := 'dragagem em terminal graneleiro',
--     p_query_embedding := '[...]'::vector(1536),
--     p_filter_segmento := 'portos',
--     p_use_hybrid      := TRUE
--   );
--
-- Dashboard Manta 17:
--   SELECT * FROM v_akp_routing_frequency;
--   SELECT * FROM v_akp_top_kes WHERE agent_slug = 'agente-barragens' LIMIT 10;
--   SELECT * FROM v_akp_similarity_health;
--   SELECT * FROM v_akp_gap_candidates;
--
-- Fallback logging (Maestro reencaminhando manualmente):
--   INSERT INTO agent_fallback_events (from_agent_slug, to_agent_slug, reason, session_id)
--   VALUES ('agente-portos', 'agente-infraestrutura-s1', 'low_confidence', 'sess_XYZ');
--
-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- BEGIN;
-- DROP FUNCTION IF EXISTS log_akp_query(TEXT, TEXT, vector, INTEGER, TEXT, TEXT, BOOLEAN, TEXT, TEXT);
-- DROP VIEW IF EXISTS v_akp_gap_candidates;
-- DROP VIEW IF EXISTS v_akp_similarity_health;
-- DROP VIEW IF EXISTS v_akp_top_kes;
-- DROP VIEW IF EXISTS v_akp_routing_frequency;
-- DROP TRIGGER IF EXISTS trg_agent_query_log_hits ON agent_query_log;
-- DROP FUNCTION IF EXISTS agent_query_log_update_hits();
-- DROP TABLE IF EXISTS agent_ke_hits;
-- DROP TABLE IF EXISTS agent_fallback_events;
-- DROP TABLE IF EXISTS agent_query_log;
-- COMMIT;
