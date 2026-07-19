-- ============================================================================
-- Manta Maestro v4.9 — Judge Feedback Loop (ADAPTED to prod schema)
-- ----------------------------------------------------------------------------
-- Fecha o ciclo do juiz LLM sobre o esquema REAL de produção:
--
--   * A tabela canônica é `public.manta_rag_queries` (não agent_query_log)
--     — em prod ela já carrega inline: judge_score, judge_notes, judge_model,
--     judge_scored_at, tipo, filtros JSONB, query_text, hits_count,
--     timestamp, query_id, trace_id.
--   * NÃO existe `agent_response_flags` em prod (a v4.6 llm_judge original
--     não foi aplicada); portanto o trigger é montado DIRETAMENTE sobre
--     manta_rag_queries.
--   * NÃO existe `v_akp_gap_candidates` em prod; promote_gaps_to_backlog()
--     lê manta_rag_queries diretamente — este migration preserva esse
--     contrato e adiciona detecção de padrões crônicos (judge_pattern).
--
-- Pipeline:
--
--   manta_rag_queries.judge_score < 3
--     ── trigger trg_judge_flag_to_backlog ──▶
--       akp_curation_backlog (ticket_type='judge_flag', 1 por query_id)
--
--   promote_gaps_to_backlog() (cron diário 08:00 UTC)
--     ── detecta ≥N flags/30d por (agent_slug, segmento) ──▶
--       akp_curation_backlog (ticket_type='judge_pattern', agregado)
--
--   v_judge_feedback_health
--     ── alimenta prompt refinement, tier promotion (Haiku→Sonnet→Opus),
--        Reflexion Loop, SkillForge.
--
-- Idempotente. Aditivo. Nenhum DROP destrutivo além de recriação de funções
-- (CREATE OR REPLACE) e da view.
--
-- Requisitos (falha fast se não atendidos):
--   * public.manta_rag_queries com colunas: query_id, query_text, tipo,
--     filtros, hits_count, timestamp, judge_score, judge_notes, judge_model,
--     judge_scored_at, trace_id.
--   * public.akp_curation_backlog (v4.5) já criada com id, ticket_id, segmento,
--     query_text, n_occurrences, avg_top_similarity, status, first_detected_at,
--     last_detected_at.
-- ============================================================================

BEGIN;

-- ============================================================================
-- 0. Pre-flight schema guards — aborta cedo se prod não bate com o contrato
-- ============================================================================

DO $$
DECLARE
  missing TEXT;
BEGIN
  SELECT string_agg(col, ', ')
    INTO missing
    FROM (VALUES
      ('query_id'), ('query_text'), ('tipo'), ('filtros'), ('hits_count'),
      ('timestamp'), ('judge_score'), ('judge_notes'), ('judge_model'),
      ('judge_scored_at'), ('trace_id')
    ) AS req(col)
   WHERE NOT EXISTS (
     SELECT 1 FROM information_schema.columns
      WHERE table_schema = 'public'
        AND table_name   = 'manta_rag_queries'
        AND column_name  = req.col
   );

  IF missing IS NOT NULL THEN
    RAISE EXCEPTION
      'v4.9 judge feedback loop: coluna(s) ausente(s) em public.manta_rag_queries: %',
      missing
      USING HINT = 'Aplique primeiro a telemetria v4.3 e o v4.6 llm_judge adaptado.';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.tables
     WHERE table_schema = 'public' AND table_name = 'akp_curation_backlog'
  ) THEN
    RAISE EXCEPTION
      'v4.9 judge feedback loop: public.akp_curation_backlog não existe'
      USING HINT = 'Aplique primeiro supabase/migrations/2026_07_12_akp_governance_v4_5.sql.';
  END IF;
END $$;

-- ============================================================================
-- 1. Estender akp_curation_backlog com as 4 colunas aditivas v4.9
-- ============================================================================

ALTER TABLE public.akp_curation_backlog
  ADD COLUMN IF NOT EXISTS ticket_type TEXT NOT NULL DEFAULT 'gap_candidate';

ALTER TABLE public.akp_curation_backlog
  ADD COLUMN IF NOT EXISTS agent_slug TEXT;

ALTER TABLE public.akp_curation_backlog
  ADD COLUMN IF NOT EXISTS evidence JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE public.akp_curation_backlog
  ADD COLUMN IF NOT EXISTS priority SMALLINT NOT NULL DEFAULT 3;

COMMENT ON COLUMN public.akp_curation_backlog.ticket_type IS
  'v4.9 — gap_candidate (v4.5 clássico), judge_flag (1 ticket por query <3), judge_pattern (agregado por agente/segmento).';
COMMENT ON COLUMN public.akp_curation_backlog.agent_slug IS
  'v4.9 — agente Manta responsável (derivado de manta_rag_queries.filtros->>filter_agente). NULL para gap_candidate.';
COMMENT ON COLUMN public.akp_curation_backlog.evidence IS
  'v4.9 — payload livre com query_id/trace_id/judge_score/judge_notes/judge_model + metadados de detecção.';
COMMENT ON COLUMN public.akp_curation_backlog.priority IS
  'v4.9 — 1 (crítico) a 5 (baixo). Escala com judge_score (0→1, 1→2, ≥2→3).';

-- ---------------------------------------------------------------------------
-- CHECK constraints (idempotent DO blocks — usam NOT VALID quando aplicável
-- para evitar full-table scan em backlog grande)
-- ---------------------------------------------------------------------------

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'akp_curation_backlog_ticket_type_chk'
      AND conrelid = 'public.akp_curation_backlog'::regclass
  ) THEN
    ALTER TABLE public.akp_curation_backlog
      ADD CONSTRAINT akp_curation_backlog_ticket_type_chk
      CHECK (ticket_type IN ('gap_candidate', 'judge_flag', 'judge_pattern'))
      NOT VALID;
    ALTER TABLE public.akp_curation_backlog
      VALIDATE CONSTRAINT akp_curation_backlog_ticket_type_chk;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'akp_curation_backlog_priority_range'
      AND conrelid = 'public.akp_curation_backlog'::regclass
  ) THEN
    ALTER TABLE public.akp_curation_backlog
      ADD CONSTRAINT akp_curation_backlog_priority_range
      CHECK (priority BETWEEN 1 AND 5)
      NOT VALID;
    ALTER TABLE public.akp_curation_backlog
      VALIDATE CONSTRAINT akp_curation_backlog_priority_range;
  END IF;
END $$;

-- Reconstrói o CHECK de status para incluir open|in_review (v4.9)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'akp_curation_backlog_status_check'
      AND conrelid = 'public.akp_curation_backlog'::regclass
  ) THEN
    ALTER TABLE public.akp_curation_backlog
      DROP CONSTRAINT akp_curation_backlog_status_check;
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'akp_curation_backlog_status_chk'
      AND conrelid = 'public.akp_curation_backlog'::regclass
  ) THEN
    ALTER TABLE public.akp_curation_backlog
      DROP CONSTRAINT akp_curation_backlog_status_chk;
  END IF;

  ALTER TABLE public.akp_curation_backlog
    ADD CONSTRAINT akp_curation_backlog_status_chk
    CHECK (status IN (
      'triage', 'open', 'in_review', 'accepted',
      'rejected', 'in_curation', 'ke_created', 'closed'
    ))
    NOT VALID;

  ALTER TABLE public.akp_curation_backlog
    VALIDATE CONSTRAINT akp_curation_backlog_status_chk;
END $$;

-- ---------------------------------------------------------------------------
-- Sequences para ticket_id (evita corrida em MAX(...)+1 sob concorrência)
-- ---------------------------------------------------------------------------

CREATE SEQUENCE IF NOT EXISTS public.akp_judge_flag_seq    START WITH 1;
CREATE SEQUENCE IF NOT EXISTS public.akp_judge_pattern_seq START WITH 1;
CREATE SEQUENCE IF NOT EXISTS public.akp_gap_candidate_seq START WITH 1;

-- Alinha as sequences com o maior sufixo já presente na tabela (idempotência
-- em reruns e compat com backlog gerado por MAX+1 na v4.5).
DO $$
DECLARE
  v_max_jf INTEGER;
  v_max_jp INTEGER;
  v_max_gc INTEGER;
BEGIN
  SELECT COALESCE(MAX(NULLIF(SUBSTRING(ticket_id FROM 8), '')::INTEGER), 0)
    INTO v_max_jf
    FROM public.akp_curation_backlog
   WHERE ticket_id LIKE 'AKP-JF-%';

  SELECT COALESCE(MAX(NULLIF(SUBSTRING(ticket_id FROM 8), '')::INTEGER), 0)
    INTO v_max_jp
    FROM public.akp_curation_backlog
   WHERE ticket_id LIKE 'AKP-JP-%';

  SELECT COALESCE(MAX(NULLIF(SUBSTRING(ticket_id FROM 9), '')::INTEGER), 0)
    INTO v_max_gc
    FROM public.akp_curation_backlog
   WHERE ticket_id LIKE 'AKP-002-%';

  PERFORM setval('public.akp_judge_flag_seq',    GREATEST(v_max_jf, 1), v_max_jf > 0);
  PERFORM setval('public.akp_judge_pattern_seq', GREATEST(v_max_jp, 1), v_max_jp > 0);
  PERFORM setval('public.akp_gap_candidate_seq', GREATEST(v_max_gc, 1), v_max_gc > 0);
END $$;

-- ---------------------------------------------------------------------------
-- Indexes (idempotency + query paths)
-- ---------------------------------------------------------------------------

-- Idempotência: no máximo 1 ticket judge_flag por query_id
CREATE UNIQUE INDEX IF NOT EXISTS uq_akp_backlog_judge_flag_query
  ON public.akp_curation_backlog ((evidence->>'query_id'))
  WHERE ticket_type = 'judge_flag';

-- Dedup dos padrões: 1 aberto por (agent_slug, segmento)
CREATE UNIQUE INDEX IF NOT EXISTS uq_akp_backlog_judge_pattern_open
  ON public.akp_curation_backlog (COALESCE(agent_slug, 'unknown-agent'), segmento)
  WHERE ticket_type = 'judge_pattern'
    AND status NOT IN ('closed', 'rejected');

CREATE INDEX IF NOT EXISTS idx_akp_backlog_ticket_type
  ON public.akp_curation_backlog (ticket_type);

CREATE INDEX IF NOT EXISTS idx_akp_backlog_agent
  ON public.akp_curation_backlog (agent_slug)
  WHERE agent_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_akp_backlog_status_priority
  ON public.akp_curation_backlog (status, priority)
  WHERE status NOT IN ('closed', 'rejected');

-- ============================================================================
-- 2. Trigger function: judge_flag → akp_curation_backlog
-- ----------------------------------------------------------------------------
-- Cobre AFTER INSERT OR UPDATE OF judge_score em manta_rag_queries:
--   * INSERT: rows já criadas com judge_score < 3 (batch judge, replay)
--   * UPDATE: caminho normal (juiz roda depois da query e preenche o score)
-- Idempotência via UNIQUE INDEX parcial em evidence->>'query_id'.
-- ============================================================================

CREATE OR REPLACE FUNCTION public.judge_flag_to_backlog()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, extensions
AS $$
DECLARE
  v_agent_slug TEXT;
  v_segmento   TEXT;
  v_priority   SMALLINT;
  v_ticket_id  TEXT;
  v_scored_at  TIMESTAMPTZ;
BEGIN
  -- Precondição (redundante com o WHEN da trigger, mas defensivo)
  IF NEW.judge_score IS NULL OR NEW.judge_score >= 3 THEN
    RETURN NEW;
  END IF;

  v_agent_slug := NULLIF(NEW.filtros->>'filter_agente', '');
  v_segmento   := COALESCE(NEW.tipo, 'sem-segmento');
  v_scored_at  := COALESCE(NEW.judge_scored_at, NOW());

  -- Prioridade escala com severidade do score
  v_priority := CASE
    WHEN NEW.judge_score = 0 THEN 1
    WHEN NEW.judge_score = 1 THEN 2
    ELSE 3
  END;

  -- Short-circuit: se já existe ticket para este query_id, retorna cedo
  -- (o UNIQUE INDEX parcial ainda garante idempotência sob corrida)
  IF EXISTS (
    SELECT 1
      FROM public.akp_curation_backlog
     WHERE ticket_type = 'judge_flag'
       AND (evidence->>'query_id') = NEW.query_id::TEXT
     LIMIT 1
  ) THEN
    RETURN NEW;
  END IF;

  v_ticket_id := 'AKP-JF-' || LPAD(nextval('public.akp_judge_flag_seq')::TEXT, 5, '0');

  BEGIN
    INSERT INTO public.akp_curation_backlog (
      ticket_id, ticket_type, agent_slug, segmento, query_text,
      n_occurrences, avg_top_similarity, priority, evidence, status,
      first_detected_at, last_detected_at
    ) VALUES (
      v_ticket_id,
      'judge_flag',
      v_agent_slug,
      v_segmento,
      NEW.query_text,
      1,
      NULL,
      v_priority,
      jsonb_strip_nulls(jsonb_build_object(
        'query_id',        NEW.query_id,
        'judge_score',     NEW.judge_score,
        'judge_notes',     NEW.judge_notes,
        'judge_model',     NEW.judge_model,
        'judge_scored_at', NEW.judge_scored_at,
        'trace_id',        NEW.trace_id,
        'source',          'trg_judge_flag_to_backlog',
        'trigger_op',      TG_OP
      )),
      'triage',
      v_scored_at,
      v_scored_at
    );
  EXCEPTION
    WHEN unique_violation THEN
      -- Colisão apenas no dedup por query_id (UNIQUE INDEX parcial).
      -- ticket_id é seguro porque usa nextval — se cair aqui é o dedup
      -- perdendo uma corrida, e o outro backend já inseriu.
      IF SQLERRM NOT LIKE '%uq_akp_backlog_judge_flag_query%' THEN
        RAISE;
      END IF;
  END;

  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.judge_flag_to_backlog() IS
  'v4.9 Judge Feedback Loop — promove manta_rag_queries.judge_score < 3 '
  'para akp_curation_backlog como ticket_type=judge_flag. Idempotente via '
  'unique index parcial em evidence->>query_id. Coverage INSERT+UPDATE.';

-- Recria trigger (permite re-run limpo do migration)
DROP TRIGGER IF EXISTS trg_judge_flag_to_backlog ON public.manta_rag_queries;

CREATE TRIGGER trg_judge_flag_to_backlog
  AFTER INSERT OR UPDATE OF judge_score ON public.manta_rag_queries
  FOR EACH ROW
  WHEN (
    NEW.judge_score IS NOT NULL
    AND NEW.judge_score < 3
    AND (
      TG_OP = 'INSERT'
      OR OLD.judge_score IS DISTINCT FROM NEW.judge_score
    )
  )
  EXECUTE FUNCTION public.judge_flag_to_backlog();

-- ============================================================================
-- 3. Extender promote_gaps_to_backlog()
-- ----------------------------------------------------------------------------
-- Preserva a semântica v4.5:
--   * gap_candidate: ≥ min_occurrences buscas/30d por (segmento, query_text)
--     com AVG(hits_count) < max_avg_hits (default 3.0).
-- Adiciona v4.9:
--   * judge_pattern: ≥ min_judge_flags respostas judge_score<3 por
--     (agent_slug, segmento) em 30d, agregando em UM ticket.
-- Retorna coluna extra ticket_type_out — assinatura MUDA e portanto os DROPs
-- explícitos abaixo são necessários.
-- ============================================================================

DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER);
DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER, FLOAT);
DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER, INTEGER);
DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER);

CREATE OR REPLACE FUNCTION public.promote_gaps_to_backlog(
  min_occurrences  INTEGER DEFAULT 3,
  max_avg_hits     FLOAT   DEFAULT 3.0,
  min_judge_flags  INTEGER DEFAULT 3
)
RETURNS TABLE (
  ticket_id_out    TEXT,
  action_out       TEXT,
  ticket_type_out  TEXT,
  segmento_out     TEXT,
  query_out        TEXT
)
LANGUAGE plpgsql
SET search_path = public, extensions
AS $$
DECLARE
  gap_rec        RECORD;
  pattern_rec    RECORD;
  existing_id    BIGINT;
  new_ticket     TEXT;
BEGIN
  -- ========================================================================
  -- PARTE 1 — gap_candidate (v4.5 preservada, threshold configurável)
  -- ========================================================================
  FOR gap_rec IN
    SELECT
      COALESCE(q.tipo, 'sem-segmento')            AS segmento,
      q.query_text                                AS query_text,
      COUNT(*)::INTEGER                           AS n_occ,
      NULLIF(AVG(q.hits_count::FLOAT), 0)         AS avg_hits,
      MAX(q.timestamp)                            AS last_seen
    FROM public.manta_rag_queries q
    WHERE q.timestamp > NOW() - INTERVAL '30 days'
      AND q.query_text IS NOT NULL
    GROUP BY 1, 2
    HAVING COUNT(*) >= min_occurrences
       AND COALESCE(AVG(q.hits_count::FLOAT), 0) < max_avg_hits
  LOOP
    SELECT b.id INTO existing_id
      FROM public.akp_curation_backlog b
     WHERE b.ticket_type = 'gap_candidate'
       AND b.segmento    = gap_rec.segmento
       AND b.query_text  = gap_rec.query_text
       AND b.status NOT IN ('closed', 'rejected')
     LIMIT 1;

    IF existing_id IS NOT NULL THEN
      UPDATE public.akp_curation_backlog b
         SET n_occurrences      = gap_rec.n_occ,
             avg_top_similarity = gap_rec.avg_hits,
             last_detected_at   = gap_rec.last_seen
       WHERE b.id = existing_id
       RETURNING b.ticket_id INTO new_ticket;

      ticket_id_out   := new_ticket;
      action_out      := 'updated';
      ticket_type_out := 'gap_candidate';
      segmento_out    := gap_rec.segmento;
      query_out       := gap_rec.query_text;
      RETURN NEXT;
    ELSE
      new_ticket := 'AKP-002-'
        || LPAD(nextval('public.akp_gap_candidate_seq')::TEXT, 5, '0');

      INSERT INTO public.akp_curation_backlog (
        ticket_id, ticket_type, segmento, query_text, n_occurrences,
        avg_top_similarity, priority, evidence, status,
        first_detected_at, last_detected_at
      ) VALUES (
        new_ticket,
        'gap_candidate',
        gap_rec.segmento,
        gap_rec.query_text,
        gap_rec.n_occ,
        gap_rec.avg_hits,
        3,
        jsonb_build_object(
          'source',   'gap_candidate',
          'avg_hits', gap_rec.avg_hits,
          'threshold_max_avg_hits', max_avg_hits,
          'window',   '30d'
        ),
        'triage',
        gap_rec.last_seen,
        gap_rec.last_seen
      );

      ticket_id_out   := new_ticket;
      action_out      := 'created';
      ticket_type_out := 'gap_candidate';
      segmento_out    := gap_rec.segmento;
      query_out       := gap_rec.query_text;
      RETURN NEXT;
    END IF;
  END LOOP;

  -- ========================================================================
  -- PARTE 2 — judge_pattern (novo v4.9)
  -- Aggregate ≥ min_judge_flags respostas ruins (score<3) em 30d por
  -- (agent_slug, segmento) em 1 ticket. Preserva o insight de padrão
  -- crônico separado dos judge_flag individuais.
  -- ========================================================================
  FOR pattern_rec IN
    SELECT
      COALESCE(NULLIF(q.filtros->>'filter_agente', ''), 'unknown-agent') AS agent_slug,
      COALESCE(q.tipo, 'sem-segmento')                                    AS segmento,
      COUNT(*)::INTEGER                                                   AS n_flags,
      AVG(q.judge_score::FLOAT)                                           AS avg_score,
      MIN(q.judge_score)                                                  AS min_score,
      MIN(q.judge_scored_at)                                              AS first_seen,
      MAX(q.judge_scored_at)                                              AS last_seen,
      jsonb_agg(DISTINCT q.judge_model)
        FILTER (WHERE q.judge_model IS NOT NULL)                          AS judge_models,
      (jsonb_agg(q.query_id::TEXT ORDER BY q.judge_scored_at DESC)
         FILTER (WHERE q.query_id IS NOT NULL))                           AS query_ids
    FROM public.manta_rag_queries q
    WHERE q.judge_scored_at > NOW() - INTERVAL '30 days'
      AND q.judge_score IS NOT NULL
      AND q.judge_score < 3
    GROUP BY 1, 2
    HAVING COUNT(*) >= min_judge_flags
  LOOP
    SELECT b.id INTO existing_id
      FROM public.akp_curation_backlog b
     WHERE b.ticket_type = 'judge_pattern'
       AND COALESCE(b.agent_slug, 'unknown-agent') = pattern_rec.agent_slug
       AND b.segmento    = pattern_rec.segmento
       AND b.status NOT IN ('closed', 'rejected')
     LIMIT 1;

    IF existing_id IS NOT NULL THEN
      UPDATE public.akp_curation_backlog b
         SET n_occurrences     = pattern_rec.n_flags,
             last_detected_at  = pattern_rec.last_seen,
             priority          = CASE
               WHEN pattern_rec.avg_score < 1 THEN 1
               WHEN pattern_rec.avg_score < 2 THEN 2
               ELSE 3
             END,
             evidence          = jsonb_strip_nulls(jsonb_build_object(
               'source',           'judge_pattern',
               'agent_slug',       pattern_rec.agent_slug,
               'segmento',         pattern_rec.segmento,
               'n_flags',          pattern_rec.n_flags,
               'avg_judge_score',  ROUND(pattern_rec.avg_score::NUMERIC, 2),
               'min_judge_score',  pattern_rec.min_score,
               'first_seen',       pattern_rec.first_seen,
               'last_seen',        pattern_rec.last_seen,
               'judge_models',     pattern_rec.judge_models,
               'sample_query_ids', COALESCE(pattern_rec.query_ids -> 0, 'null'::jsonb),
               'threshold_min_judge_flags', min_judge_flags,
               'window',           '30d'
             ))
       WHERE b.id = existing_id
       RETURNING b.ticket_id INTO new_ticket;

      ticket_id_out   := new_ticket;
      action_out      := 'updated';
      ticket_type_out := 'judge_pattern';
      segmento_out    := pattern_rec.segmento;
      query_out       := '[judge_pattern] ' || pattern_rec.agent_slug
                        || ' / ' || pattern_rec.segmento;
      RETURN NEXT;
    ELSE
      new_ticket := 'AKP-JP-'
        || LPAD(nextval('public.akp_judge_pattern_seq')::TEXT, 5, '0');

      BEGIN
        INSERT INTO public.akp_curation_backlog (
          ticket_id, ticket_type, agent_slug, segmento, query_text,
          n_occurrences, priority, evidence, status,
          first_detected_at, last_detected_at
        ) VALUES (
          new_ticket,
          'judge_pattern',
          pattern_rec.agent_slug,
          pattern_rec.segmento,
          '[judge_pattern] ' || pattern_rec.agent_slug
            || ' / ' || pattern_rec.segmento
            || ' (' || pattern_rec.n_flags || ' flags/30d)',
          pattern_rec.n_flags,
          CASE
            WHEN pattern_rec.avg_score < 1 THEN 1
            WHEN pattern_rec.avg_score < 2 THEN 2
            ELSE 3
          END,
          jsonb_strip_nulls(jsonb_build_object(
            'source',           'judge_pattern',
            'agent_slug',       pattern_rec.agent_slug,
            'segmento',         pattern_rec.segmento,
            'n_flags',          pattern_rec.n_flags,
            'avg_judge_score',  ROUND(pattern_rec.avg_score::NUMERIC, 2),
            'min_judge_score',  pattern_rec.min_score,
            'first_seen',       pattern_rec.first_seen,
            'last_seen',        pattern_rec.last_seen,
            'judge_models',     pattern_rec.judge_models,
            'sample_query_ids', COALESCE(pattern_rec.query_ids -> 0, 'null'::jsonb),
            'threshold_min_judge_flags', min_judge_flags,
            'window',           '30d'
          )),
          'triage',
          pattern_rec.first_seen,
          pattern_rec.last_seen
        );

        ticket_id_out   := new_ticket;
        action_out      := 'created';
        ticket_type_out := 'judge_pattern';
        segmento_out    := pattern_rec.segmento;
        query_out       := '[judge_pattern] ' || pattern_rec.agent_slug
                          || ' / ' || pattern_rec.segmento;
        RETURN NEXT;
      EXCEPTION
        WHEN unique_violation THEN
          -- Corrida no dedup do padrão (uq_akp_backlog_judge_pattern_open).
          -- Silencia: outra execução concorrente já criou o mesmo agregado.
          IF SQLERRM NOT LIKE '%uq_akp_backlog_judge_pattern_open%' THEN
            RAISE;
          END IF;
      END;
    END IF;
  END LOOP;

  RETURN;
END;
$$;

COMMENT ON FUNCTION public.promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER) IS
  'v4.9 — Promove: (1) gap_candidate (≥min_occurrences buscas/30d com '
  'AVG(hits_count) < max_avg_hits) e (2) judge_pattern (≥min_judge_flags '
  'respostas judge_score<3/30d por agente/segmento). Ambos leem '
  'manta_rag_queries diretamente. Executado pelo cron akp-daily-cron 08:00 UTC.';

-- ============================================================================
-- 4. View v_judge_feedback_health — saúde por agente/segmento (30d)
-- ----------------------------------------------------------------------------
-- Lê manta_rag_queries.judge_score DIRETAMENTE (não depende de
-- agent_response_flags nem de agent_query_log). Alimenta prompt refinement,
-- tier promotion (Haiku→Sonnet→Opus), Reflexion Loop, SkillForge.
-- ============================================================================

DROP VIEW IF EXISTS public.v_judge_feedback_health;

CREATE VIEW public.v_judge_feedback_health
WITH (security_invoker = true) AS
WITH scored_30d AS (
  SELECT
    COALESCE(NULLIF(q.filtros->>'filter_agente', ''), 'unknown-agent') AS agent_slug,
    COALESCE(q.tipo, 'sem-segmento')                                    AS segmento,
    q.query_id,
    q.judge_score,
    q.judge_scored_at,
    q.judge_model,
    q.hits_count
  FROM public.manta_rag_queries q
  WHERE q.judge_scored_at > NOW() - INTERVAL '30 days'
    AND q.judge_score IS NOT NULL
),
totals_30d AS (
  SELECT
    COALESCE(NULLIF(q.filtros->>'filter_agente', ''), 'unknown-agent') AS agent_slug,
    COALESCE(q.tipo, 'sem-segmento')                                    AS segmento,
    COUNT(*)::INTEGER                                                   AS n_queries_30d
  FROM public.manta_rag_queries q
  WHERE q.timestamp > NOW() - INTERVAL '30 days'
  GROUP BY 1, 2
),
per_agent AS (
  SELECT
    s.agent_slug,
    s.segmento,
    COUNT(*)::INTEGER                                              AS n_judged_30d,
    ROUND(AVG(s.judge_score)::NUMERIC, 2)                          AS avg_judge_score,
    COUNT(*) FILTER (WHERE s.judge_score >= 4)::INTEGER            AS n_good,
    COUNT(*) FILTER (WHERE s.judge_score = 3)::INTEGER             AS n_ok,
    COUNT(*) FILTER (WHERE s.judge_score < 3)::INTEGER             AS n_low,
    COUNT(*) FILTER (WHERE s.judge_score = 0)::INTEGER             AS n_zero,
    MIN(s.judge_scored_at)                                         AS first_scored_at,
    MAX(s.judge_scored_at)                                         AS last_scored_at,
    jsonb_agg(DISTINCT s.judge_model)
      FILTER (WHERE s.judge_model IS NOT NULL)                     AS judge_models
  FROM scored_30d s
  GROUP BY 1, 2
),
tickets AS (
  SELECT
    COALESCE(b.agent_slug, 'unknown-agent')                                AS agent_slug,
    b.segmento,
    COUNT(*) FILTER (WHERE b.ticket_type = 'judge_flag')::INTEGER          AS n_open_judge_flags,
    COUNT(*) FILTER (WHERE b.ticket_type = 'judge_pattern')::INTEGER       AS n_open_judge_patterns
  FROM public.akp_curation_backlog b
  WHERE b.status NOT IN ('closed', 'rejected')
    AND b.ticket_type IN ('judge_flag', 'judge_pattern')
  GROUP BY 1, 2
)
SELECT
  p.agent_slug,
  p.segmento,
  t30.n_queries_30d,
  p.n_judged_30d,
  ROUND(
    100.0 * p.n_judged_30d::NUMERIC
      / NULLIF(t30.n_queries_30d, 0),
    1
  )                                                                AS judge_coverage_pct,
  p.avg_judge_score,
  p.n_good,
  p.n_ok,
  p.n_low,
  p.n_zero,
  ROUND(
    100.0 * p.n_low::NUMERIC / NULLIF(p.n_judged_30d, 0),
    1
  )                                                                AS pct_low,
  ROUND(
    100.0 * p.n_good::NUMERIC / NULLIF(p.n_judged_30d, 0),
    1
  )                                                                AS pct_good,
  COALESCE(tk.n_open_judge_flags, 0)                               AS n_open_judge_flags,
  COALESCE(tk.n_open_judge_patterns, 0)                            AS n_open_judge_patterns,
  p.judge_models,
  p.first_scored_at,
  p.last_scored_at,
  -- Sinal composto para tier promotion / prompt refinement
  CASE
    WHEN p.avg_judge_score < 2.0 THEN 'critical'
    WHEN p.avg_judge_score < 3.0 THEN 'warn'
    WHEN p.avg_judge_score < 4.0 THEN 'ok'
    ELSE 'healthy'
  END                                                              AS health_status
FROM per_agent p
LEFT JOIN totals_30d t30
  ON t30.agent_slug = p.agent_slug
 AND t30.segmento   = p.segmento
LEFT JOIN tickets tk
  ON tk.agent_slug  = p.agent_slug
 AND tk.segmento    = p.segmento
ORDER BY
  CASE
    WHEN p.avg_judge_score < 2.0 THEN 1
    WHEN p.avg_judge_score < 3.0 THEN 2
    WHEN p.avg_judge_score < 4.0 THEN 3
    ELSE 4
  END,
  p.n_low DESC,
  p.n_judged_30d DESC;

COMMENT ON VIEW public.v_judge_feedback_health IS
  'v4.9 — Saúde do juiz LLM por agente/segmento em 30d, lendo '
  'manta_rag_queries.judge_score diretamente. security_invoker=true para '
  'preservar RLS eventual da tabela base. Alimenta prompt refinement, '
  'tier promotion (Haiku→Sonnet→Opus), Reflexion Loop e SkillForge.';

-- ============================================================================
-- 5. RLS (idempotente, service_role ALL)
-- ============================================================================

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_class
     WHERE oid = 'public.akp_curation_backlog'::regclass
       AND relrowsecurity = TRUE
  ) THEN
    EXECUTE 'ALTER TABLE public.akp_curation_backlog ENABLE ROW LEVEL SECURITY';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename  = 'akp_curation_backlog'
       AND policyname = 'akp_curation_backlog_service_all'
  ) THEN
    CREATE POLICY akp_curation_backlog_service_all
      ON public.akp_curation_backlog
      AS PERMISSIVE
      FOR ALL
      TO service_role
      USING (TRUE)
      WITH CHECK (TRUE);
  END IF;
END $$;

-- ============================================================================
-- 6. GRANTS mínimos
-- ============================================================================

GRANT EXECUTE ON FUNCTION public.judge_flag_to_backlog()                      TO service_role;
GRANT EXECUTE ON FUNCTION public.promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER) TO service_role;
GRANT USAGE   ON SEQUENCE public.akp_judge_flag_seq                           TO service_role;
GRANT USAGE   ON SEQUENCE public.akp_judge_pattern_seq                        TO service_role;
GRANT USAGE   ON SEQUENCE public.akp_gap_candidate_seq                        TO service_role;
GRANT SELECT  ON public.v_judge_feedback_health                               TO service_role, authenticated;

COMMIT;

-- ============================================================================
-- ROLLBACK (comentado — executar em bloco separado se necessário)
-- ----------------------------------------------------------------------------
-- BEGIN;
--
-- -- 1. Trigger + função
-- DROP TRIGGER IF EXISTS trg_judge_flag_to_backlog ON public.manta_rag_queries;
-- DROP FUNCTION IF EXISTS public.judge_flag_to_backlog();
--
-- -- 2. View
-- DROP VIEW IF EXISTS public.v_judge_feedback_health;
--
-- -- 3. Função promote_gaps_to_backlog (v4.9) → restaurar assinatura v4.5
-- DROP FUNCTION IF EXISTS public.promote_gaps_to_backlog(INTEGER, FLOAT, INTEGER);
-- -- (Reaplicar o corpo v4.5 a partir de
-- --  supabase/migrations/2026_07_12_akp_governance_v4_5.sql
-- --  para recriar a versão single-param.)
--
-- -- 4. Apagar tickets criados na janela v4.9 (opcional — remove evidências)
-- -- DELETE FROM public.akp_curation_backlog
-- --   WHERE ticket_type IN ('judge_flag', 'judge_pattern');
--
-- -- 5. Indexes v4.9
-- DROP INDEX IF EXISTS public.uq_akp_backlog_judge_flag_query;
-- DROP INDEX IF EXISTS public.uq_akp_backlog_judge_pattern_open;
-- DROP INDEX IF EXISTS public.idx_akp_backlog_ticket_type;
-- DROP INDEX IF EXISTS public.idx_akp_backlog_agent;
-- DROP INDEX IF EXISTS public.idx_akp_backlog_status_priority;
--
-- -- 6. Sequences v4.9
-- DROP SEQUENCE IF EXISTS public.akp_judge_flag_seq;
-- DROP SEQUENCE IF EXISTS public.akp_judge_pattern_seq;
-- DROP SEQUENCE IF EXISTS public.akp_gap_candidate_seq;
--
-- -- 7. CHECK constraints v4.9
-- ALTER TABLE public.akp_curation_backlog
--   DROP CONSTRAINT IF EXISTS akp_curation_backlog_ticket_type_chk,
--   DROP CONSTRAINT IF EXISTS akp_curation_backlog_priority_range,
--   DROP CONSTRAINT IF EXISTS akp_curation_backlog_status_chk;
--
-- -- Restaura o CHECK de status original (v4.5)
-- ALTER TABLE public.akp_curation_backlog
--   ADD CONSTRAINT akp_curation_backlog_status_check
--   CHECK (status IN (
--     'triage', 'accepted', 'rejected', 'in_curation', 'ke_created', 'closed'
--   ));
--
-- -- 8. Colunas v4.9 (destrutivo — dropa dados; execute APENAS se realmente
-- --    quiser reverter esquema. Descomente com cuidado.)
-- -- ALTER TABLE public.akp_curation_backlog
-- --   DROP COLUMN IF EXISTS priority,
-- --   DROP COLUMN IF EXISTS evidence,
-- --   DROP COLUMN IF EXISTS agent_slug,
-- --   DROP COLUMN IF EXISTS ticket_type;
--
-- COMMIT;
-- ============================================================================
