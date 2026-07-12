-- M-C — LLM-as-a-judge ADAPTADO ao schema real
-- Substitui: supabase/migrations/2026_07_12_llm_judge_v4_6.sql
-- Ver: docs/AUDIT-v4.6-vs-PROD.md § Fase 2 M-C
--
-- Reuso das tabelas de prod: manta_rag_queries (queries loggadas) +
-- manta_rag_errors (flags de baixa qualidade). Adiciona colunas de judge.

BEGIN;

-- ============================================================
-- 1. Colunas de julgamento em manta_rag_queries
-- ============================================================
ALTER TABLE public.manta_rag_queries
  ADD COLUMN IF NOT EXISTS agent_response_text TEXT;

ALTER TABLE public.manta_rag_queries
  ADD COLUMN IF NOT EXISTS judge_score SMALLINT
    CHECK (judge_score IS NULL OR judge_score BETWEEN 0 AND 5);

ALTER TABLE public.manta_rag_queries
  ADD COLUMN IF NOT EXISTS judge_scored_at TIMESTAMPTZ;

ALTER TABLE public.manta_rag_queries
  ADD COLUMN IF NOT EXISTS judge_model TEXT;

ALTER TABLE public.manta_rag_queries
  ADD COLUMN IF NOT EXISTS judge_notes JSONB;

CREATE INDEX IF NOT EXISTS idx_manta_rag_queries_judge_pending
  ON public.manta_rag_queries(timestamp DESC)
  WHERE judge_score IS NULL;

CREATE INDEX IF NOT EXISTS idx_manta_rag_queries_judge_low
  ON public.manta_rag_queries(judge_score)
  WHERE judge_score IS NOT NULL AND judge_score < 3;

-- ============================================================
-- 2. Trigger — score < 3 vira flag em manta_rag_errors
-- ============================================================
-- manta_rag_errors já tem estrutura ideal: tipo, guard_agent, descricao,
-- severidade, corrigido. Só precisamos linkar automaticamente.

CREATE OR REPLACE FUNCTION public.judge_flag_low_score()
RETURNS TRIGGER LANGUAGE plpgsql SET search_path = public, extensions AS $$
DECLARE
  reason_text TEXT;
BEGIN
  -- Só dispara se judge_score foi atualizado para < 3
  IF NEW.judge_score IS NULL OR NEW.judge_score >= 3 THEN RETURN NEW; END IF;
  IF OLD.judge_score = NEW.judge_score THEN RETURN NEW; END IF;

  -- Não duplica se já existe flag aberto para o mesmo query_id
  IF EXISTS (
    SELECT 1 FROM public.manta_rag_errors e
    WHERE e.trace_id = NEW.trace_id
      AND e.guard_agent = 'llm-judge'
      AND e.corrigido = false
  ) THEN
    RETURN NEW;
  END IF;

  reason_text := format(
    'judge_score=%s. Notes: %s',
    NEW.judge_score,
    COALESCE(NEW.judge_notes->>'overall_reasoning', '(sem overall_reasoning)')
  );

  INSERT INTO public.manta_rag_errors
    (trace_id, tipo, guard_agent, descricao, input_dump, output_dump, severidade)
  VALUES (
    NEW.trace_id,
    'inconsistencia',   -- CHECK constraint em manta_rag_errors.tipo
    'llm-judge',
    reason_text,
    jsonb_build_object('query_id', NEW.query_id, 'query_text', NEW.query_text),
    jsonb_build_object('response', NEW.agent_response_text,
                       'judge_notes', NEW.judge_notes),
    CASE WHEN NEW.judge_score = 0 THEN 'critical'
         WHEN NEW.judge_score = 1 THEN 'error'
         ELSE 'warn' END
  );
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_judge_flag_low ON public.manta_rag_queries;
CREATE TRIGGER trg_judge_flag_low
  AFTER UPDATE OF judge_score ON public.manta_rag_queries
  FOR EACH ROW EXECUTE FUNCTION public.judge_flag_low_score();

-- ============================================================
-- 3. Função de sampling estratificado por tipo (segmento inferido)
-- ============================================================
CREATE OR REPLACE FUNCTION public.select_queries_for_judging(
  sample_rate FLOAT DEFAULT 0.10,
  since_hours INTEGER DEFAULT 24,
  max_batch INTEGER DEFAULT 100
)
RETURNS TABLE (
  query_id      BIGINT,
  query_text    TEXT,
  agent_response TEXT,
  tipo          TEXT
)
LANGUAGE sql STABLE SET search_path = public, extensions AS $$
  WITH ranked AS (
    SELECT
      q.query_id, q.query_text, q.agent_response_text, q.tipo,
      ROW_NUMBER() OVER (
        PARTITION BY COALESCE(q.tipo, '_none') ORDER BY random()
      ) AS rnk,
      COUNT(*) OVER (PARTITION BY COALESCE(q.tipo, '_none')) AS n_seg
    FROM public.manta_rag_queries q
    WHERE q.timestamp > NOW() - (since_hours || ' hours')::INTERVAL
      AND q.judge_score IS NULL
      AND q.agent_response_text IS NOT NULL
  )
  SELECT r.query_id, r.query_text, r.agent_response_text, r.tipo
    FROM ranked r
   WHERE r.rnk <= GREATEST(1, CEIL(r.n_seg * sample_rate))
   ORDER BY r.tipo, r.rnk
   LIMIT max_batch;
$$;

-- ============================================================
-- 4. Views de saúde do juiz (últimos 7 dias)
-- ============================================================
CREATE OR REPLACE VIEW public.v_akp_judge_health AS
SELECT
  COALESCE(q.tipo, '(sem tipo)') AS segmento,
  COUNT(*)                                                       AS total_queries,
  COUNT(*) FILTER (WHERE q.judge_score IS NOT NULL)              AS n_judged,
  ROUND(100.0 * COUNT(*) FILTER (WHERE q.judge_score IS NOT NULL)
        / NULLIF(COUNT(*), 0), 1)                                AS pct_judged,
  ROUND(AVG(q.judge_score::NUMERIC), 2)                          AS avg_score,
  COUNT(*) FILTER (WHERE q.judge_score < 3)                      AS n_flagged
FROM public.manta_rag_queries q
WHERE q.timestamp > NOW() - INTERVAL '7 days'
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE VIEW public.v_akp_judge_criteria_breakdown AS
SELECT
  COALESCE(q.tipo, '(sem tipo)') AS segmento,
  ROUND(AVG((q.judge_notes->>'citations_real')::NUMERIC), 2)     AS avg_citations_real,
  ROUND(AVG((q.judge_notes->>'norms_correct')::NUMERIC), 2)      AS avg_norms_correct,
  ROUND(AVG((q.judge_notes->>'answered_question')::NUMERIC), 2)  AS avg_answered_question,
  ROUND(AVG((q.judge_notes->>'structure_v1v5')::NUMERIC), 2)     AS avg_structure_v1v5,
  ROUND(AVG((q.judge_notes->>'handoffs_emitted')::NUMERIC), 2)   AS avg_handoffs_emitted,
  COUNT(*)                                                        AS n
FROM public.manta_rag_queries q
WHERE q.judge_notes IS NOT NULL
  AND q.timestamp > NOW() - INTERVAL '7 days'
GROUP BY 1
ORDER BY 1;

COMMIT;

-- ============================================================
-- ROLLBACK
-- ============================================================
-- BEGIN;
-- DROP VIEW    IF EXISTS public.v_akp_judge_criteria_breakdown;
-- DROP VIEW    IF EXISTS public.v_akp_judge_health;
-- DROP FUNCTION IF EXISTS public.select_queries_for_judging(FLOAT, INTEGER, INTEGER);
-- DROP TRIGGER IF EXISTS trg_judge_flag_low ON public.manta_rag_queries;
-- DROP FUNCTION IF EXISTS public.judge_flag_low_score();
-- ALTER TABLE public.manta_rag_queries
--   DROP COLUMN IF EXISTS agent_response_text,
--   DROP COLUMN IF EXISTS judge_score,
--   DROP COLUMN IF EXISTS judge_scored_at,
--   DROP COLUMN IF EXISTS judge_model,
--   DROP COLUMN IF EXISTS judge_notes;
-- COMMIT;
