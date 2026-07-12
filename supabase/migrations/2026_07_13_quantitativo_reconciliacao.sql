-- Migration: manta_quantitativos_reconciliacao
-- Sprint: Meta-Quantitativo (Agente A) — orquestrador /api/quantitativo/projeto
-- Data: 2026-07-13
--
-- Tabela que armazena cada quantity reconciliada de um projeto Manta:
-- uma row por (project, session, sap_code). ``sources`` é JSONB com o array
-- de leituras {backend, value, confidence, unit, provenance}. Status é
-- 'auto_approved' quando confidence_agregado >= sla_confidence_min E as
-- fontes convergiram; caso contrário 'human_review'. Reviewer humano (MN)
-- fecha o loop escrevendo em ``reviewed_by`` + ``reviewed_at``.
--
-- Depende de:
--   - public.agent_episodes (v4.7, migration 2026_07_13)
--
-- Idempotente. Coerente com Fase 1 hardening: search_path fixo, RLS ligado
-- com política aberta p/ service_role.
--
-- Rollback: bloco comentado no final.

BEGIN;

-- ============================================================
-- 1. Tabela principal
-- ============================================================

CREATE TABLE IF NOT EXISTS public.manta_quantitativos_reconciliacao (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id              TEXT NOT NULL,
  session_id              UUID NOT NULL,
  sap_code                TEXT NOT NULL,
  qty                     NUMERIC NOT NULL,
  unit                    TEXT,
  confidence_agregado     NUMERIC(3, 2)
                          CHECK (confidence_agregado BETWEEN 0 AND 1),
  sources                 JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- Ex.: [{"backend": "oae", "value": 21.84, "confidence": 1.0,
  --        "unit": "m3", "provenance": "MTEXT literal"}, ...]
  delta_max_pct           NUMERIC(6, 2) DEFAULT 0.00,
  episode_id              UUID
                          REFERENCES public.agent_episodes(id)
                          ON DELETE SET NULL,
  status                  TEXT NOT NULL DEFAULT 'human_review'
                          CHECK (status IN ('auto_approved', 'human_review', 'rejected')),
  reviewed_by             TEXT,      -- login do humano (MN, VS, etc.)
  reviewed_at             TIMESTAMPTZ,
  created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.manta_quantitativos_reconciliacao IS
  'Uma row por (projeto, sessão, sap_code) reconciliado pelo orquestrador '
  '/api/quantitativo/projeto (backend quantitativo :8016). ``sources`` é o '
  'array de leituras dos peer backends; ``delta_max_pct`` é a maior '
  'divergência entre fontes; ``status`` é gate de human-in-the-loop.';

COMMENT ON COLUMN public.manta_quantitativos_reconciliacao.sources IS
  'JSONB array [{backend, value, confidence, unit, provenance}] com todas as '
  'leituras que o orquestrador consolidou nesta quantity.';

COMMENT ON COLUMN public.manta_quantitativos_reconciliacao.status IS
  'auto_approved (dentro da tolerância + confidence >= SLA) | '
  'human_review (default; divergiu ou confidence baixa) | rejected (MN vetou).';

-- ============================================================
-- 2. Índices
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_quantitativos_project
  ON public.manta_quantitativos_reconciliacao (project_id);

CREATE INDEX IF NOT EXISTS idx_quantitativos_sap_code
  ON public.manta_quantitativos_reconciliacao (sap_code);

CREATE INDEX IF NOT EXISTS idx_quantitativos_status
  ON public.manta_quantitativos_reconciliacao (status);

CREATE INDEX IF NOT EXISTS idx_quantitativos_session
  ON public.manta_quantitativos_reconciliacao (session_id);

CREATE INDEX IF NOT EXISTS idx_quantitativos_episode
  ON public.manta_quantitativos_reconciliacao (episode_id);

-- Índice parcial: fila de revisão humana (o caso mais consultado)
CREATE INDEX IF NOT EXISTS idx_quantitativos_review_queue
  ON public.manta_quantitativos_reconciliacao (project_id, created_at DESC)
  WHERE status = 'human_review';

-- GIN em ``sources`` para queries do tipo "quantities onde OAE contribuiu":
CREATE INDEX IF NOT EXISTS idx_quantitativos_sources_gin
  ON public.manta_quantitativos_reconciliacao USING GIN (sources jsonb_path_ops);

-- ============================================================
-- 3. Row-Level Security
-- ============================================================
-- Convenção Manta: RLS ligado em toda tabela pública + política aberta pro
-- service_role. Fase 1 hardening prevê que apps de leitura tenham suas
-- próprias policies granulares depois.

ALTER TABLE public.manta_quantitativos_reconciliacao ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role can do everything"
  ON public.manta_quantitativos_reconciliacao;

CREATE POLICY "service_role can do everything"
  ON public.manta_quantitativos_reconciliacao
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================
-- 4. View auxiliar para o Maestro (fila de revisão + KPIs)
-- ============================================================

CREATE OR REPLACE VIEW public.v_quantitativos_pending_review
WITH (security_invoker = on)
AS
  SELECT
    project_id,
    COUNT(*)                                   AS n_pending,
    AVG(confidence_agregado)                   AS avg_confidence,
    MAX(delta_max_pct)                         AS max_delta_pct,
    MIN(created_at)                            AS oldest_pending,
    MAX(created_at)                            AS newest_pending
  FROM public.manta_quantitativos_reconciliacao
  WHERE status = 'human_review'
  GROUP BY project_id
  ORDER BY oldest_pending ASC;

COMMENT ON VIEW public.v_quantitativos_pending_review IS
  'Fila agregada por projeto de reconciliações aguardando revisão humana '
  '(status = human_review). Consumida pelo dashboard do Maestro.';

COMMIT;

-- ============================================================
-- Rollback (comentado, executar manualmente se preciso)
-- ============================================================
-- BEGIN;
-- DROP VIEW IF EXISTS public.v_quantitativos_pending_review;
-- DROP TABLE IF EXISTS public.manta_quantitativos_reconciliacao;
-- COMMIT;
