-- Manta Maestro v4.9 — Judge Feedback Loop (fecha o ciclo LLM-as-a-judge → curadoria)
-- Ticket: MNT-2026-JUDGE-FEEDBACK-LOOP
--
-- Contexto:
--   v4.6 (`2026_07_12_llm_judge_v4_6.sql`) instalou o juiz Sonnet 4.6 + trigger
--   que popula `agent_response_flags` sempre que `agent_query_log.judge_score < 3`.
--   v4.5 (`2026_07_12_akp_governance_v4_5.sql`) formalizou `akp_curation_backlog`
--   + `promote_gaps_to_backlog()` — hoje ele só consome `v_akp_gap_candidates`.
--   Faltava o pino: um flag warn/error do juiz nao vira ticket automaticamente,
--   ficando parado na lista de flags até alguem inspecionar. Este loop fecha isso.
--
-- Nesta migracao:
--   1. Estender `akp_curation_backlog` com colunas `ticket_type`, `agent_slug`,
--      `evidence` (JSONB) e `priority` — necessarias para representar tickets
--      alem do gap classico.
--   2. Trigger `trg_judge_flag_to_backlog` (AFTER INSERT em `agent_response_flags`):
--      severity warn/error => insere linha `ticket_type='judge_flag'` no backlog.
--   3. Estender `promote_gaps_to_backlog()`: alem de consumir gaps academicos,
--      detecta padroes de flags recorrentes (>=3 warn+ em 30d por agente) e abre
--      ticket agregado `ticket_type='judge_pattern'`.
--   4. View `v_judge_feedback_health` — dashboard operacional MN.
--
-- Aditiva sobre v4.6 + v4.5. Idempotente. Sem impacto nas colunas/tables existentes
-- (novas colunas nullable ou com default). Fase 1 hardening: SET search_path.
--
-- NAO EXECUTAR EM PRODUCAO SEM GATE MN — este arquivo e candidato de review.

BEGIN;

-- =====================================================================
-- 1. Extensao do schema de akp_curation_backlog
-- =====================================================================
-- Antes: tabela pensada apenas para gaps academicos (segmento + query_text).
-- Agora: passa a suportar tres tipos de ticket via coluna `ticket_type`.
-- Todas as adicoes sao aditivas: linhas antigas herdam o default 'gap_candidate'.

ALTER TABLE akp_curation_backlog
  ADD COLUMN IF NOT EXISTS ticket_type TEXT NOT NULL DEFAULT 'gap_candidate',
  ADD COLUMN IF NOT EXISTS agent_slug  TEXT,
  ADD COLUMN IF NOT EXISTS evidence    JSONB NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS priority    SMALLINT NOT NULL DEFAULT 3;

-- Constraint de dominio para ticket_type (idempotente).
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'akp_curation_backlog_ticket_type_chk'
  ) THEN
    ALTER TABLE akp_curation_backlog
      ADD CONSTRAINT akp_curation_backlog_ticket_type_chk
      CHECK (ticket_type IN ('gap_candidate', 'judge_flag', 'judge_pattern'));
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'akp_curation_backlog_priority_range'
  ) THEN
    ALTER TABLE akp_curation_backlog
      ADD CONSTRAINT akp_curation_backlog_priority_range
      CHECK (priority BETWEEN 1 AND 5);
  END IF;
END$$;

-- Idempotencia dos tickets judge_flag: nao criar duplicata para o mesmo flag_id.
-- Indice parcial sobre `evidence->>'flag_id'` so quando ticket_type='judge_flag'.
CREATE UNIQUE INDEX IF NOT EXISTS uq_akp_backlog_judge_flag
  ON akp_curation_backlog ((evidence->>'flag_id'))
  WHERE ticket_type = 'judge_flag';

CREATE INDEX IF NOT EXISTS idx_akp_backlog_ticket_type
  ON akp_curation_backlog(ticket_type, status);
CREATE INDEX IF NOT EXISTS idx_akp_backlog_agent
  ON akp_curation_backlog(agent_slug)
  WHERE agent_slug IS NOT NULL;

COMMENT ON COLUMN akp_curation_backlog.ticket_type IS
  'Tipo do ticket: gap_candidate (padrao v4.5, gap academico da view v_akp_gap_candidates), '
  'judge_flag (v4.9, criado 1:1 por flag warn/error do juiz), '
  'judge_pattern (v4.9, ticket agregado por padrao de baixa qualidade recorrente).';
COMMENT ON COLUMN akp_curation_backlog.agent_slug IS
  'Agente responsavel pelo ticket (opcional para gap_candidate legado).';
COMMENT ON COLUMN akp_curation_backlog.evidence IS
  'JSONB com evidencia bruta. judge_flag: {flag_id, query_log_id, judge_score, judge_notes}. '
  'judge_pattern: {n_flags_warn, n_flags_error, top_flags, window_days}.';
COMMENT ON COLUMN akp_curation_backlog.priority IS
  '1 (critico, erro do juiz) .. 5 (baixo). Default 3.';

-- RLS: enable + policy permissiva para service_role (idempotente).
ALTER TABLE akp_curation_backlog ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename  = 'akp_curation_backlog'
      AND policyname = 'akp_curation_backlog_service_all'
  ) THEN
    CREATE POLICY akp_curation_backlog_service_all
      ON akp_curation_backlog
      FOR ALL
      TO service_role
      USING (true)
      WITH CHECK (true);
  END IF;
END$$;

-- =====================================================================
-- 2. Trigger judge_flag -> backlog
-- =====================================================================
-- AFTER INSERT em agent_response_flags: se severidade (derivada do judge_score
-- da agent_query_log referenciada) for warn/error, cria ticket judge_flag.
-- Idempotencia garantida pelo indice unico parcial acima.

CREATE OR REPLACE FUNCTION judge_flag_to_backlog() RETURNS TRIGGER AS $$
DECLARE
  v_score     SMALLINT;
  v_notes     JSONB;
  v_agent     TEXT;
  v_segmento  TEXT;
  v_query     TEXT;
  v_severity  TEXT;
  v_priority  SMALLINT;
  v_next_seq  INTEGER;
  v_ticket_id TEXT;
BEGIN
  -- Puxa contexto do log referenciado.
  SELECT
    l.judge_score,
    l.judge_notes,
    l.agent_slug,
    COALESCE(l.filter_segmento, '(sem_seg)'),
    l.query_text
  INTO
    v_score, v_notes, v_agent, v_segmento, v_query
  FROM agent_query_log l
  WHERE l.id = NEW.query_log_id;

  -- Deriva severidade a partir do judge_score.
  -- Regras: 0..1 => error, 2 => warn, 3+ => info (nao gera ticket).
  v_severity := CASE
                  WHEN v_score IS NULL          THEN 'warn'   -- flag manual sem score, tratar como warn
                  WHEN v_score BETWEEN 0 AND 1  THEN 'error'
                  WHEN v_score = 2              THEN 'warn'
                  ELSE                               'info'
                END;

  IF v_severity NOT IN ('warn', 'error') THEN
    RETURN NEW;  -- info: nao promove
  END IF;

  v_priority := CASE v_severity
                  WHEN 'error' THEN 1
                  WHEN 'warn'  THEN 3
                  ELSE              5
                END;

  -- Gera ticket_id sequencial no namespace JF (Judge Flag).
  SELECT COALESCE(MAX(SUBSTRING(t.ticket_id FROM 9)::INTEGER), 0) + 1
    INTO v_next_seq
    FROM akp_curation_backlog t
   WHERE t.ticket_id LIKE 'AKP-JF-%';
  v_ticket_id := 'AKP-JF-' || LPAD(v_next_seq::TEXT, 5, '0');

  -- Insert idempotente. Se o flag_id ja tem ticket, ON CONFLICT no indice
  -- parcial rejeita e ignoramos silenciosamente.
  INSERT INTO akp_curation_backlog (
    ticket_id,
    ticket_type,
    segmento,
    agent_slug,
    query_text,
    n_occurrences,
    priority,
    status,
    evidence,
    first_detected_at,
    last_detected_at
  ) VALUES (
    v_ticket_id,
    'judge_flag',
    v_segmento,
    v_agent,
    COALESCE(v_query, '(sem query_text no log)'),
    1,
    v_priority,
    'open',
    jsonb_build_object(
      'flag_id',      NEW.id,
      'query_log_id', NEW.query_log_id,
      'judge_score',  v_score,
      'judge_notes',  COALESCE(v_notes, '{}'::jsonb),
      'severity',     v_severity,
      'flag_reason',  NEW.flag_reason
    ),
    NEW.flagged_at,
    NEW.flagged_at
  )
  ON CONFLICT ((evidence->>'flag_id')) WHERE ticket_type = 'judge_flag'
  DO NOTHING;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql
   SET search_path = public, extensions;

-- Adiciona 'open' e 'in_review' ao dominio de status caso ainda nao existam,
-- reconstruindo a check constraint (Postgres nao permite ALTER de CHECK).
DO $$
DECLARE
  chk_name TEXT;
BEGIN
  SELECT c.conname
    INTO chk_name
    FROM pg_constraint c
    JOIN pg_class r ON r.oid = c.conrelid
   WHERE r.relname = 'akp_curation_backlog'
     AND c.contype = 'c'
     AND pg_get_constraintdef(c.oid) LIKE '%status%';
  IF chk_name IS NOT NULL THEN
    EXECUTE format('ALTER TABLE akp_curation_backlog DROP CONSTRAINT %I', chk_name);
  END IF;
  ALTER TABLE akp_curation_backlog
    ADD CONSTRAINT akp_curation_backlog_status_chk
    CHECK (status IN (
      'triage','accepted','rejected','in_curation','ke_created','closed',
      'open','in_review'
    ));
END$$;

DROP TRIGGER IF EXISTS trg_judge_flag_to_backlog ON agent_response_flags;
CREATE TRIGGER trg_judge_flag_to_backlog
  AFTER INSERT ON agent_response_flags
  FOR EACH ROW
  EXECUTE FUNCTION judge_flag_to_backlog();

COMMENT ON FUNCTION judge_flag_to_backlog() IS
  'v4.9 — Ao inserir um agent_response_flags, se severidade derivada do judge_score '
  'for warn ou error, abre ticket AKP-JF-* em akp_curation_backlog. Idempotente por flag_id.';

-- =====================================================================
-- 3. promote_gaps_to_backlog() estendido — judge_pattern
-- =====================================================================
-- Alem do comportamento v4.5 (gaps academicos da view v_akp_gap_candidates),
-- agora tambem: para cada agente com >=3 flags warn+ nos ultimos 30d SEM ticket
-- pattern aberto, cria ticket_type='judge_pattern' com evidencia agregada.

CREATE OR REPLACE FUNCTION promote_gaps_to_backlog(
  min_occurrences INTEGER DEFAULT 3,
  max_top_sim     FLOAT   DEFAULT 0.30
)
RETURNS TABLE (
  ticket_id       TEXT,
  action          TEXT,   -- 'created' | 'updated' | 'skipped'
  segmento        TEXT,
  query_text      TEXT
)
LANGUAGE plpgsql
SET search_path = public, extensions
AS $$
DECLARE
  gap_rec       RECORD;
  pat_rec       RECORD;
  existing_id   BIGINT;
  new_ticket_id TEXT;
  next_seq      INTEGER;
BEGIN
  -- ---------------------------------------------------------------
  -- 3.1 comportamento historico v4.5: gaps academicos
  -- ---------------------------------------------------------------
  FOR gap_rec IN
    SELECT
      g.segmento,
      g.query_text,
      g.n_occurrences,
      g.avg_top_sim,
      g.last_seen
    FROM v_akp_gap_candidates g
    WHERE g.n_occurrences >= min_occurrences
      AND (g.avg_top_sim IS NULL OR g.avg_top_sim <= max_top_sim)
  LOOP
    SELECT id INTO existing_id
      FROM akp_curation_backlog
     WHERE segmento    = gap_rec.segmento
       AND query_text  = gap_rec.query_text
       AND ticket_type = 'gap_candidate'
       AND status NOT IN ('closed', 'rejected')
     LIMIT 1;

    IF existing_id IS NOT NULL THEN
      UPDATE akp_curation_backlog
         SET n_occurrences      = gap_rec.n_occurrences,
             avg_top_similarity = gap_rec.avg_top_sim,
             last_detected_at   = gap_rec.last_seen
       WHERE id = existing_id;
      action := 'updated';
      SELECT b.ticket_id INTO new_ticket_id
        FROM akp_curation_backlog b WHERE b.id = existing_id;
    ELSE
      SELECT COALESCE(MAX(SUBSTRING(t.ticket_id FROM 9)::INTEGER), 0) + 1
        INTO next_seq
        FROM akp_curation_backlog t
       WHERE t.ticket_id LIKE 'AKP-002-%';
      new_ticket_id := 'AKP-002-' || LPAD(next_seq::TEXT, 5, '0');
      INSERT INTO akp_curation_backlog (
        ticket_id, ticket_type, segmento, query_text,
        n_occurrences, avg_top_similarity,
        first_detected_at, last_detected_at
      ) VALUES (
        new_ticket_id, 'gap_candidate', gap_rec.segmento, gap_rec.query_text,
        gap_rec.n_occurrences, gap_rec.avg_top_sim,
        gap_rec.last_seen, gap_rec.last_seen
      );
      action := 'created';
    END IF;

    ticket_id  := new_ticket_id;
    segmento   := gap_rec.segmento;
    query_text := gap_rec.query_text;
    RETURN NEXT;
  END LOOP;

  -- ---------------------------------------------------------------
  -- 3.2 NOVO v4.9: padroes de flags warn+ recorrentes
  -- ---------------------------------------------------------------
  FOR pat_rec IN
    WITH flags30 AS (
      SELECT
        b.agent_slug,
        COALESCE(l.filter_segmento, '(sem_seg)') AS segmento,
        b.id            AS backlog_id,
        b.evidence      AS ev,
        b.first_detected_at,
        b.last_detected_at
      FROM akp_curation_backlog b
      JOIN agent_query_log      l
        ON l.id = (b.evidence->>'query_log_id')::BIGINT
      WHERE b.ticket_type = 'judge_flag'
        AND b.first_detected_at > NOW() - INTERVAL '30 days'
        AND (b.evidence->>'severity') IN ('warn','error')
    ),
    agg AS (
      SELECT
        agent_slug,
        segmento,
        COUNT(*)                                         AS n_flags,
        COUNT(*) FILTER (WHERE (ev->>'severity')='warn') AS n_warn,
        COUNT(*) FILTER (WHERE (ev->>'severity')='error')AS n_error,
        MIN(first_detected_at)                           AS first_seen,
        MAX(last_detected_at)                            AS last_seen,
        jsonb_agg(jsonb_build_object(
          'backlog_id', backlog_id,
          'severity',   ev->>'severity',
          'score',      ev->>'judge_score',
          'reason',     LEFT(COALESCE(ev->>'flag_reason',''), 160)
        ) ORDER BY last_detected_at DESC) FILTER (WHERE TRUE) AS all_flags
      FROM flags30
      WHERE agent_slug IS NOT NULL
      GROUP BY agent_slug, segmento
      HAVING COUNT(*) >= min_occurrences
    )
    SELECT
      a.agent_slug,
      a.segmento,
      a.n_flags,
      a.n_warn,
      a.n_error,
      a.first_seen,
      a.last_seen,
      (SELECT jsonb_agg(x) FROM (
         SELECT * FROM jsonb_array_elements(a.all_flags) LIMIT 3
       ) x)                                                    AS top_flags
    FROM agg a
  LOOP
    -- Ja existe pattern aberto para o mesmo agente no ultimo ciclo? Atualiza.
    SELECT id INTO existing_id
      FROM akp_curation_backlog
     WHERE ticket_type = 'judge_pattern'
       AND agent_slug  = pat_rec.agent_slug
       AND status NOT IN ('closed','rejected')
     LIMIT 1;

    IF existing_id IS NOT NULL THEN
      UPDATE akp_curation_backlog
         SET n_occurrences    = pat_rec.n_flags,
             last_detected_at = pat_rec.last_seen,
             evidence         = jsonb_build_object(
                                  'n_flags_warn',   pat_rec.n_warn,
                                  'n_flags_error',  pat_rec.n_error,
                                  'top_flags',      COALESCE(pat_rec.top_flags, '[]'::jsonb),
                                  'window_days',    30
                                ),
             priority         = CASE WHEN pat_rec.n_error > 0 THEN 1 ELSE 2 END
       WHERE id = existing_id;
      action := 'updated';
      SELECT b.ticket_id INTO new_ticket_id
        FROM akp_curation_backlog b WHERE b.id = existing_id;
    ELSE
      SELECT COALESCE(MAX(SUBSTRING(t.ticket_id FROM 9)::INTEGER), 0) + 1
        INTO next_seq
        FROM akp_curation_backlog t
       WHERE t.ticket_id LIKE 'AKP-JP-%';
      new_ticket_id := 'AKP-JP-' || LPAD(next_seq::TEXT, 5, '0');

      INSERT INTO akp_curation_backlog (
        ticket_id, ticket_type, segmento, agent_slug, query_text,
        n_occurrences, priority, status, evidence,
        first_detected_at, last_detected_at
      ) VALUES (
        new_ticket_id,
        'judge_pattern',
        pat_rec.segmento,
        pat_rec.agent_slug,
        format('Padrao de %s flags warn+ em 30d para %s', pat_rec.n_flags, pat_rec.agent_slug),
        pat_rec.n_flags,
        CASE WHEN pat_rec.n_error > 0 THEN 1 ELSE 2 END,
        'open',
        jsonb_build_object(
          'n_flags_warn',  pat_rec.n_warn,
          'n_flags_error', pat_rec.n_error,
          'top_flags',     COALESCE(pat_rec.top_flags, '[]'::jsonb),
          'window_days',   30
        ),
        pat_rec.first_seen,
        pat_rec.last_seen
      );
      action := 'created';
    END IF;

    ticket_id  := new_ticket_id;
    segmento   := pat_rec.segmento;
    query_text := format('[judge_pattern] agente=%s', pat_rec.agent_slug);
    RETURN NEXT;
  END LOOP;

  RETURN;
END;
$$;

COMMENT ON FUNCTION promote_gaps_to_backlog(INTEGER, FLOAT) IS
  'v4.9 — 1) gap_candidate a partir de v_akp_gap_candidates (v4.5); '
  '2) judge_pattern a partir de >=N flags warn/error em 30d por agente. '
  'Roda diariamente via cron ou GH Action.';

-- =====================================================================
-- 4. View de health do loop
-- =====================================================================
-- Por agente, ultimos 30 dias: contagens de flags por severidade, tickets
-- abertos, media do judge_score, ultima insercao no backlog.

CREATE OR REPLACE VIEW v_judge_feedback_health AS
WITH flags AS (
  SELECT
    l.agent_slug,
    l.judge_score,
    CASE
      WHEN l.judge_score BETWEEN 0 AND 1 THEN 'error'
      WHEN l.judge_score = 2             THEN 'warn'
      ELSE                                    'info'
    END                                       AS severity,
    f.flagged_at
  FROM agent_response_flags f
  JOIN agent_query_log      l ON l.id = f.query_log_id
  WHERE f.flagged_at > NOW() - INTERVAL '30 days'
),
tix AS (
  SELECT
    agent_slug,
    COUNT(*) FILTER (WHERE status IN ('open','triage','in_review','in_curation'))
      AS n_tickets_open,
    MAX(first_detected_at) AS last_ticket_at
  FROM akp_curation_backlog
  WHERE ticket_type IN ('judge_flag','judge_pattern')
    AND agent_slug IS NOT NULL
    AND first_detected_at > NOW() - INTERVAL '30 days'
  GROUP BY agent_slug
)
SELECT
  COALESCE(f.agent_slug, t.agent_slug)                          AS agent_slug,
  COALESCE(COUNT(*) FILTER (WHERE f.severity = 'warn'),  0)     AS n_flags_warn,
  COALESCE(COUNT(*) FILTER (WHERE f.severity = 'error'), 0)     AS n_flags_error,
  COALESCE(MAX(t.n_tickets_open), 0)                            AS n_tickets_open,
  ROUND(AVG(f.judge_score)::NUMERIC, 2)                         AS mean_judge_score,
  MAX(t.last_ticket_at)                                         AS last_ticket_at
FROM flags f
FULL OUTER JOIN tix t ON t.agent_slug = f.agent_slug
GROUP BY COALESCE(f.agent_slug, t.agent_slug)
ORDER BY n_flags_error DESC, n_flags_warn DESC;

COMMENT ON VIEW v_judge_feedback_health IS
  'v4.9 — Health do loop juiz->backlog por agente, janela 30d. Uso: painel MN + alertas.';

COMMIT;

-- =====================================================================
-- USO ESPERADO
-- =====================================================================
--
-- Loop end-to-end (ver docs/JUDGE-FEEDBACK-LOOP-v4.9.md):
--   1. Agente responde  -> row em agent_query_log
--   2. akp_judge.py     -> UPDATE judge_score < 3
--   3. Trigger v4.6     -> INSERT em agent_response_flags
--   4. Trigger v4.9     -> INSERT em akp_curation_backlog (ticket_type='judge_flag')
--   5. Cron diario      -> promote_gaps_to_backlog() cria judge_pattern se >=3 flags/agente/30d
--   6. MN revisa        -> altera status para in_review/accepted/rejected/closed
--   7. Prompt refino    -> mudanca no SKILL.md via agent_change_request
--   8. Merge            -> tier promotion/demotion no Maestro
--
-- Consultas uteis:
--   SELECT * FROM v_judge_feedback_health;
--   SELECT * FROM akp_curation_backlog WHERE ticket_type='judge_flag' AND status='open' ORDER BY priority, first_detected_at DESC;
--   SELECT * FROM akp_curation_backlog WHERE ticket_type='judge_pattern' ORDER BY first_detected_at DESC;
--   SELECT promote_gaps_to_backlog();  -- dry-run manual, ver rows retornadas
--
-- =====================================================================
-- ROLLBACK (comentado — nao executar sem gate MN)
-- =====================================================================
-- BEGIN;
-- DROP VIEW     IF EXISTS v_judge_feedback_health;
-- DROP TRIGGER  IF EXISTS trg_judge_flag_to_backlog ON agent_response_flags;
-- DROP FUNCTION IF EXISTS judge_flag_to_backlog();
-- -- Restaura promote_gaps_to_backlog() na versao v4.5 (ver 2026_07_12_akp_governance_v4_5.sql).
-- -- ATENCAO: NAO derrubar as colunas ticket_type/agent_slug/evidence/priority se ha rows
-- -- judge_flag/judge_pattern ativos. Preferir marcar 'closed' e manter.
-- DROP INDEX IF EXISTS uq_akp_backlog_judge_flag;
-- DROP INDEX IF EXISTS idx_akp_backlog_ticket_type;
-- DROP INDEX IF EXISTS idx_akp_backlog_agent;
-- ALTER TABLE akp_curation_backlog
--   DROP CONSTRAINT IF EXISTS akp_curation_backlog_status_chk,
--   DROP CONSTRAINT IF EXISTS akp_curation_backlog_priority_range,
--   DROP CONSTRAINT IF EXISTS akp_curation_backlog_ticket_type_chk,
--   DROP COLUMN IF EXISTS priority,
--   DROP COLUMN IF EXISTS evidence,
--   DROP COLUMN IF EXISTS agent_slug,
--   DROP COLUMN IF EXISTS ticket_type;
-- DROP POLICY IF EXISTS akp_curation_backlog_service_all ON akp_curation_backlog;
-- COMMIT;
