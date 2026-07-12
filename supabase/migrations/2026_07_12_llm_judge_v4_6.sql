-- Academic Knowledge Pipeline (WF-AKP-001) — Vetor 5 (LLM-as-a-judge) v4.6
-- Ticket: WF-AKP-001 backlog item #14 (auto-avaliação de respostas)
--
-- Motivação:
--   Sem feedback de qualidade, o agente responde e ninguém sabe se acertou.
--   Um juiz independente (Claude Sonnet 4.6) revisa amostragem de respostas
--   contra 5 critérios objetivos e grava score 0-5. Se score < 3, dispara
--   flag para revisão MN.
--
-- Baseado em Shinn et al. 2023 "Reflexion: Language Agents with Verbal
-- Reinforcement Learning" e no padrão Constitutional AI da Anthropic.
--
-- Estende a telemetria da v4.3 (`2026_07_12_akp_telemetry.sql`).
-- MIGRAÇÃO CANDIDATA, aditiva, idempotente.

BEGIN;

-- =====================================================================
-- 1. Colunas de julgamento em agent_query_log
-- =====================================================================
-- Hoje agent_query_log guarda a query + IDs retornados. Para o juiz avaliar,
-- precisamos também da resposta que o agente deu (texto natural), o score
-- do julgamento, o modelo que julgou e o breakdown por critério.
ALTER TABLE agent_query_log
  ADD COLUMN IF NOT EXISTS agent_response_text TEXT,
  ADD COLUMN IF NOT EXISTS judge_score         SMALLINT,
  ADD COLUMN IF NOT EXISTS judge_scored_at     TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS judge_model         TEXT,
  ADD COLUMN IF NOT EXISTS judge_notes         JSONB;

-- Constraint de range 0-5 (só cria uma vez).
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'agent_query_log_judge_score_range'
  ) THEN
    ALTER TABLE agent_query_log
      ADD CONSTRAINT agent_query_log_judge_score_range
      CHECK (judge_score IS NULL OR (judge_score BETWEEN 0 AND 5));
  END IF;
END$$;

-- Índices para o sampler e para os relatórios de saúde.
CREATE INDEX IF NOT EXISTS idx_agent_query_log_unjudged
  ON agent_query_log(query_ts DESC)
  WHERE judge_score IS NULL AND agent_response_text IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_query_log_judge_score
  ON agent_query_log(judge_score)
  WHERE judge_score IS NOT NULL;

COMMENT ON COLUMN agent_query_log.agent_response_text IS
  'Resposta natural que o agente devolveu ao usuário. Necessária para o juiz avaliar.';
COMMENT ON COLUMN agent_query_log.judge_score IS
  'Score 0-5 atribuído pelo juiz LLM (Vetor 5). NULL = ainda não avaliado.';
COMMENT ON COLUMN agent_query_log.judge_notes IS
  'Breakdown por critério: citations_real, norms_correct, answered_question, '
  'structure_v1v5, handoffs_emitted (+ notas textuais) + overall_reasoning.';

-- =====================================================================
-- 2. Tabela agent_response_flags — pendências de revisão MN
-- =====================================================================
CREATE TABLE IF NOT EXISTS agent_response_flags (
  id             BIGSERIAL PRIMARY KEY,
  query_log_id   BIGINT NOT NULL REFERENCES agent_query_log(id) ON DELETE CASCADE,
  flag_reason    TEXT NOT NULL,
  status         TEXT NOT NULL DEFAULT 'open' CHECK (status IN (
                   'open',           -- aguardando triagem MN
                   'reviewed_ok',    -- MN revisou e considerou aceitável (falso positivo do juiz)
                   'reviewed_bad',   -- MN confirma que a resposta foi ruim
                   'fixed'           -- respondida em nova versão / KE criado para cobrir
                 )),
  mn_notes       TEXT,
  flagged_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_response_flags_status
  ON agent_response_flags(status, flagged_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_response_flags_query_log
  ON agent_response_flags(query_log_id);

COMMENT ON TABLE agent_response_flags IS
  'Backlog de revisão MN alimentado automaticamente quando judge_score < 3.';

-- =====================================================================
-- 3. Trigger: score < 3 → cria flag automaticamente
-- =====================================================================
CREATE OR REPLACE FUNCTION agent_query_log_auto_flag() RETURNS TRIGGER AS $$
DECLARE
  reason_txt TEXT;
BEGIN
  -- Só age quando judge_score é setado (transição NULL→valor OU update para valor menor)
  -- e o valor final é < 3.
  IF NEW.judge_score IS NULL OR NEW.judge_score >= 3 THEN
    RETURN NEW;
  END IF;
  IF OLD.judge_score IS NOT NULL AND OLD.judge_score = NEW.judge_score THEN
    RETURN NEW;  -- idempotente: mesmo score já foi processado
  END IF;

  -- Deriva flag_reason das notas do juiz. Escolhe os 2 critérios mais fracos.
  reason_txt := 'Judge score ' || NEW.judge_score || '/5';
  IF NEW.judge_notes IS NOT NULL THEN
    reason_txt := reason_txt || COALESCE(
      ' — fracos: ' || (
        SELECT string_agg(k || '=' || v, ', ')
        FROM (
          SELECT key AS k, (value)::TEXT AS v
          FROM jsonb_each_text(NEW.judge_notes)
          WHERE key IN ('citations_real','norms_correct','answered_question',
                        'structure_v1v5','handoffs_emitted')
            AND (value)::TEXT ~ '^[0-2]$'
          ORDER BY (value)::INT ASC
          LIMIT 3
        ) x
      ),
      ''
    );
    IF NEW.judge_notes ? 'overall_reasoning' THEN
      reason_txt := reason_txt || ' | ' ||
        LEFT(NEW.judge_notes->>'overall_reasoning', 200);
    END IF;
  END IF;

  -- Evita duplicar flag em open para a mesma linha.
  IF NOT EXISTS (
    SELECT 1 FROM agent_response_flags
     WHERE query_log_id = NEW.id AND status = 'open'
  ) THEN
    INSERT INTO agent_response_flags (query_log_id, flag_reason, status)
    VALUES (NEW.id, reason_txt, 'open');
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agent_query_log_auto_flag ON agent_query_log;
CREATE TRIGGER trg_agent_query_log_auto_flag
  AFTER UPDATE OF judge_score ON agent_query_log
  FOR EACH ROW EXECUTE FUNCTION agent_query_log_auto_flag();

-- =====================================================================
-- 4. Função de sampling estratificada por segmento
-- =====================================================================
-- Retorna queries recentes ainda-não-julgadas para o juiz processar.
-- Estratificação: 10% por segmento, não 10% do total — evita que segmentos
-- majoritários (ex.: rodovias) engulam a amostra.
CREATE OR REPLACE FUNCTION select_queries_for_judging(
  sample_rate FLOAT       DEFAULT 0.10,
  since       TIMESTAMPTZ DEFAULT NOW() - INTERVAL '24 hours',
  max_batch   INTEGER     DEFAULT 100
)
RETURNS TABLE (
  id                    BIGINT,
  agent_slug            TEXT,
  filter_segmento       TEXT,
  query_text            TEXT,
  agent_response_text   TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
  IF sample_rate <= 0.0 OR sample_rate > 1.0 THEN
    RAISE EXCEPTION 'sample_rate must be in (0.0, 1.0], got %', sample_rate;
  END IF;

  RETURN QUERY
  WITH candidates AS (
    SELECT
      l.id,
      l.agent_slug,
      COALESCE(l.filter_segmento, '(sem_seg)') AS seg_key,
      l.filter_segmento,
      l.query_text,
      l.agent_response_text,
      -- ordem aleatória estável dentro do segmento
      ROW_NUMBER() OVER (
        PARTITION BY COALESCE(l.filter_segmento, '(sem_seg)')
        ORDER BY random()
      ) AS rn_seg,
      COUNT(*) OVER (
        PARTITION BY COALESCE(l.filter_segmento, '(sem_seg)')
      ) AS n_seg
    FROM agent_query_log l
    WHERE l.judge_score IS NULL
      AND l.agent_response_text IS NOT NULL
      AND l.query_text IS NOT NULL
      AND l.query_ts >= since
      AND l.query_source IN ('agent', 'maestro')  -- não julga smoke_test/manual
  ),
  picked AS (
    SELECT
      c.id, c.agent_slug, c.filter_segmento, c.query_text, c.agent_response_text
    FROM candidates c
    -- pelo menos 1 por segmento se houver algum; caso contrário ceil(n*rate)
    WHERE c.rn_seg <= GREATEST(1, CEIL(c.n_seg * sample_rate)::INT)
  )
  SELECT p.id, p.agent_slug, p.filter_segmento, p.query_text, p.agent_response_text
    FROM picked p
   ORDER BY p.filter_segmento NULLS LAST, p.id DESC
   LIMIT max_batch;
END;
$$;

COMMENT ON FUNCTION select_queries_for_judging IS
  'Amostragem estratificada por segmento (default 10% de cada) das queries '
  'recentes ainda não julgadas. Ignora smoke_test/manual/api.';

-- =====================================================================
-- 5. Views de health do juiz
-- =====================================================================

-- 5.1 — Cobertura e média por agente (últimos 7d)
CREATE OR REPLACE VIEW v_akp_judge_health AS
SELECT
  agent_slug,
  COUNT(*)                                                                       AS total_queries,
  COUNT(*) FILTER (WHERE judge_score IS NOT NULL)                                AS n_judged,
  ROUND(100.0 * COUNT(*) FILTER (WHERE judge_score IS NOT NULL)
        / NULLIF(COUNT(*), 0), 1)                                                AS pct_judged,
  ROUND(AVG(judge_score) FILTER (WHERE judge_score IS NOT NULL)::NUMERIC, 2)     AS avg_score,
  COUNT(*) FILTER (WHERE judge_score IS NOT NULL AND judge_score < 3)            AS n_flagged
FROM agent_query_log
WHERE query_ts > NOW() - INTERVAL '7 days'
GROUP BY agent_slug
ORDER BY total_queries DESC;

COMMENT ON VIEW v_akp_judge_health IS
  'Agregado por agente (últimos 7d): total, julgados, %julgados, média e nº de flags.';

-- 5.2 — Média por critério × segmento (últimos 7d)
CREATE OR REPLACE VIEW v_akp_judge_criteria_breakdown AS
SELECT
  COALESCE(filter_segmento, '(sem_segmento)') AS segmento,
  COUNT(*) FILTER (WHERE judge_score IS NOT NULL) AS n_judged,
  -- Cada critério é extraído do JSONB e convertido para int quando existe.
  ROUND(AVG((judge_notes->>'citations_real')::NUMERIC)
        FILTER (WHERE judge_notes ? 'citations_real'), 2)     AS avg_citations_real,
  ROUND(AVG((judge_notes->>'norms_correct')::NUMERIC)
        FILTER (WHERE judge_notes ? 'norms_correct'), 2)      AS avg_norms_correct,
  ROUND(AVG((judge_notes->>'answered_question')::NUMERIC)
        FILTER (WHERE judge_notes ? 'answered_question'), 2)  AS avg_answered_question,
  ROUND(AVG((judge_notes->>'structure_v1v5')::NUMERIC)
        FILTER (WHERE judge_notes ? 'structure_v1v5'), 2)     AS avg_structure_v1v5,
  ROUND(AVG((judge_notes->>'handoffs_emitted')::NUMERIC)
        FILTER (WHERE judge_notes ? 'handoffs_emitted'), 2)   AS avg_handoffs_emitted,
  ROUND(AVG(judge_score)
        FILTER (WHERE judge_score IS NOT NULL)::NUMERIC, 2)   AS avg_overall
FROM agent_query_log
WHERE query_ts > NOW() - INTERVAL '7 days'
  AND judge_score IS NOT NULL
GROUP BY 1
ORDER BY 1;

COMMENT ON VIEW v_akp_judge_criteria_breakdown IS
  'Média por critério (extraída do judge_notes JSONB) × segmento, últimos 7d. '
  'Coluna avg_<criterio> baixa = fraqueza sistemática nesse eixo.';

COMMIT;

-- =====================================================================
-- Uso esperado
-- =====================================================================
--
-- Sampling (chamado pelo akp_judge.py):
--   SELECT * FROM select_queries_for_judging(0.10, NOW() - INTERVAL '24 hours', 100);
--
-- Após o juiz avaliar, o script faz:
--   UPDATE agent_query_log
--     SET judge_score     = 4,
--         judge_scored_at = NOW(),
--         judge_model     = 'claude-sonnet-4-6',
--         judge_notes     = '{"citations_real":5,"norms_correct":4,
--                             "answered_question":5,"structure_v1v5":3,
--                             "handoffs_emitted":2,"overall_score":4,
--                             "overall_reasoning":"..."}'::JSONB
--   WHERE id = 12345;
--   -- trigger cria flag se score < 3.
--
-- Dashboards / painel Manta 17:
--   SELECT * FROM v_akp_judge_health;
--   SELECT * FROM v_akp_judge_criteria_breakdown;
--   SELECT * FROM agent_response_flags WHERE status = 'open' ORDER BY flagged_at DESC;
--
-- =====================================================================
-- ROLLBACK
-- =====================================================================
-- BEGIN;
-- DROP VIEW  IF EXISTS v_akp_judge_criteria_breakdown;
-- DROP VIEW  IF EXISTS v_akp_judge_health;
-- DROP FUNCTION IF EXISTS select_queries_for_judging(FLOAT, TIMESTAMPTZ, INTEGER);
-- DROP TRIGGER IF EXISTS trg_agent_query_log_auto_flag ON agent_query_log;
-- DROP FUNCTION IF EXISTS agent_query_log_auto_flag();
-- DROP TABLE IF EXISTS agent_response_flags;
-- ALTER TABLE agent_query_log
--   DROP CONSTRAINT IF EXISTS agent_query_log_judge_score_range,
--   DROP COLUMN IF EXISTS judge_notes,
--   DROP COLUMN IF EXISTS judge_model,
--   DROP COLUMN IF EXISTS judge_scored_at,
--   DROP COLUMN IF EXISTS judge_score,
--   DROP COLUMN IF EXISTS agent_response_text;
-- DROP INDEX IF EXISTS idx_agent_query_log_unjudged;
-- DROP INDEX IF EXISTS idx_agent_query_log_judge_score;
-- COMMIT;
