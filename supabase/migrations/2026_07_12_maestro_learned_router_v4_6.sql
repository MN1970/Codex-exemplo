-- Manta Maestro — Learned Routing (Vetor 1, scaffold)
-- Ticket: MAESTRO-V4.6-LEARNED-ROUTING
--
-- Motivação:
--   Hoje o Maestro roteia por keyword-matching (IF menção a X → agente Y).
--   Rígido, quebra com sinônimos, não aprende. A telemetria v4.3
--   (`agent_query_log`) registra `(query_text, agent_slug, top_similarity)` —
--   é um dataset supervisionado grátis. Esta migração cria a camada de dados
--   do classificador ML (Vetor 1). O pipeline de treino/inference vive em
--   `manta-hub/scripts/maestro_learned_router.py`.
--
-- Arquitetura runtime:
--   Maestro chama o classifier como PRÉ-ROUTER. Se confidence > 0.85, adota
--   `predicted_agent`; senão cai no keyword-router legado (com is_override=TRUE).
--   Todas as predições — adotadas ou não — vão para `maestro_routing_predictions`
--   para retreino direcionado.
--
-- Embedding: multilingual-e5-small (384d) — mesmo modelo do AskCAD KB e Orçamento.
-- Barato, rápido, roda offline. Trocar para 1536d exige rebuild do modelo.
--
-- MIGRAÇÃO CANDIDATA, aditiva sobre v4.5 (governance). Idempotente.

BEGIN;

-- =====================================================================
-- 1. Tabela de predições
-- =====================================================================
-- 1 linha / query classificada pelo modelo (independentemente da adoção).
-- Alta cardinalidade esperada — particionar por RANGE em predicted_at se
-- volume > 5M rows.
CREATE TABLE IF NOT EXISTS maestro_routing_predictions (
  id                 BIGSERIAL PRIMARY KEY,
  query_text         TEXT NOT NULL,
  query_embedding    vector(384),                     -- multilingual-e5-small
  predicted_agent    TEXT NOT NULL,                   -- ex.: agente-portos
  confidence         FLOAT NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  predicted_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  -- Preenchido depois: qual agente REALMENTE respondeu (feedback loop).
  -- NULL = ainda sem verdade absoluta.
  actual_agent       TEXT,
  -- TRUE quando o classifier foi rejeitado (confidence baixa) e o
  -- keyword-router legado assumiu a decisão.
  is_override        BOOLEAN NOT NULL DEFAULT FALSE,
  model_version      TEXT,                            -- ex.: v1-2026-07-12
  feedback_source    TEXT CHECK (feedback_source IN (
                       'production',   -- rodada real em produção
                       'smoke_test',   -- rodada de smoke
                       'manual',       -- operador logou manualmente
                       'training'      -- veio do próprio dataset de treino
                     )),
  session_id         TEXT                             -- correlaciona com Maestro session (opcional)
);

CREATE INDEX IF NOT EXISTS idx_mlr_pred_agent      ON maestro_routing_predictions(predicted_agent);
CREATE INDEX IF NOT EXISTS idx_mlr_pred_at         ON maestro_routing_predictions(predicted_at DESC);
CREATE INDEX IF NOT EXISTS idx_mlr_confidence      ON maestro_routing_predictions(confidence);
CREATE INDEX IF NOT EXISTS idx_mlr_actual_agent    ON maestro_routing_predictions(actual_agent) WHERE actual_agent IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_mlr_model_version   ON maestro_routing_predictions(model_version);
CREATE INDEX IF NOT EXISTS idx_mlr_source          ON maestro_routing_predictions(feedback_source);

-- HNSW p/ busca semântica de queries parecidas (retreino direcionado,
-- descoberta de clusters, análise offline). Requer pgvector 0.5+.
CREATE INDEX IF NOT EXISTS idx_mlr_embedding_hnsw
  ON maestro_routing_predictions
  USING hnsw (query_embedding vector_cosine_ops);

COMMENT ON TABLE maestro_routing_predictions IS
  'Log do pré-router ML do Maestro. 1 linha por query classificada. actual_agent preenchido no fim do turno para feedback.';

-- =====================================================================
-- 2. View — acurácia dos últimos 7 dias (por model_version)
-- =====================================================================
CREATE OR REPLACE VIEW v_router_accuracy AS
SELECT
  model_version,
  COUNT(*)                                                                    AS n_predictions,
  COUNT(*) FILTER (WHERE actual_agent IS NOT NULL)                            AS n_with_ground_truth,
  COUNT(*) FILTER (WHERE actual_agent IS NOT NULL AND predicted_agent = actual_agent)  AS n_correct,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE actual_agent IS NOT NULL AND predicted_agent = actual_agent)
    / NULLIF(COUNT(*) FILTER (WHERE actual_agent IS NOT NULL), 0),
    2
  )                                                                           AS accuracy_pct,
  AVG(confidence)::NUMERIC(4,3)                                               AS avg_confidence,
  AVG(confidence) FILTER (WHERE predicted_agent = actual_agent)::NUMERIC(4,3) AS avg_confidence_when_correct,
  AVG(confidence) FILTER (WHERE actual_agent IS NOT NULL AND predicted_agent != actual_agent)::NUMERIC(4,3) AS avg_confidence_when_wrong,
  COUNT(*) FILTER (WHERE is_override)                                         AS n_overrides,
  MIN(predicted_at)                                                           AS window_start,
  MAX(predicted_at)                                                           AS window_end
FROM maestro_routing_predictions
WHERE predicted_at > NOW() - INTERVAL '7 days'
GROUP BY model_version
ORDER BY n_predictions DESC;

COMMENT ON VIEW v_router_accuracy IS
  'Acurácia dos últimos 7 dias por model_version. Dashboard Manta 17 + gate de release do modelo.';

-- =====================================================================
-- 3. View — desacordos (candidatos a retreino direcionado)
-- =====================================================================
CREATE OR REPLACE VIEW v_router_disagreements AS
SELECT
  id,
  query_text,
  predicted_agent,
  actual_agent,
  confidence,
  model_version,
  feedback_source,
  predicted_at
FROM maestro_routing_predictions
WHERE predicted_at > NOW() - INTERVAL '30 days'
  AND actual_agent IS NOT NULL
  AND predicted_agent != actual_agent
  AND is_override = FALSE          -- excluir casos em que o classifier foi rejeitado (não é culpa dele)
ORDER BY predicted_at DESC;

COMMENT ON VIEW v_router_disagreements IS
  'Queries dos últimos 30d onde o classifier ERROU (não foi override). Alimenta o próximo sprint de retreino: hard negatives.';

COMMIT;

-- =====================================================================
-- Uso esperado
-- =====================================================================
--
-- Insert de predição (feito pelo maestro_learned_router.py --mode infer --log):
--   INSERT INTO maestro_routing_predictions (
--     query_text, query_embedding, predicted_agent, confidence,
--     model_version, feedback_source
--   ) VALUES (
--     'Como dimensionar dragagem em terminal graneleiro?',
--     '[...384 dims...]'::vector(384),
--     'agente-portos', 0.91,
--     'v1-2026-07-12', 'production'
--   );
--
-- Feedback loop (fim do turno, Maestro sabe qual agente respondeu):
--   UPDATE maestro_routing_predictions
--      SET actual_agent = 'agente-portos'
--    WHERE id = <id>;
--
-- Dashboard:
--   SELECT * FROM v_router_accuracy;
--   SELECT * FROM v_router_disagreements LIMIT 20;
--
-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- BEGIN;
-- DROP VIEW IF EXISTS v_router_disagreements;
-- DROP VIEW IF EXISTS v_router_accuracy;
-- DROP INDEX IF EXISTS idx_mlr_embedding_hnsw;
-- DROP INDEX IF EXISTS idx_mlr_source;
-- DROP INDEX IF EXISTS idx_mlr_model_version;
-- DROP INDEX IF EXISTS idx_mlr_actual_agent;
-- DROP INDEX IF EXISTS idx_mlr_confidence;
-- DROP INDEX IF EXISTS idx_mlr_pred_at;
-- DROP INDEX IF EXISTS idx_mlr_pred_agent;
-- DROP TABLE IF EXISTS maestro_routing_predictions;
-- COMMIT;
