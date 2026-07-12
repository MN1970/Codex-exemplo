-- v4.7 — Reflexion loop + Episodic memory + Cost tracking
-- Roadmap: MNT-IA-20260712-001 §2.3 (episodic) + §4.3 (retrieval) + §4.5 (decay) + §6.4 (cost)
-- Ver: docs/AUDIT-v4.6-vs-PROD.md (schema real bge-m3 1024d, agent_id TEXT como
-- em manta_agent_capabilities, manta_rag_queries.query_id BIGINT — NÃO UUID).
--
-- Depends on:
--   - public.manta_rag_queries (schema real de prod; query_id BIGINT PK)
--   - public.manta_agent_capabilities.agent_id (convenção 03-S6, M17, 00-maestro)
--   - Fase 1 hardening aplicada (search_path + security_invoker)
--
-- Idempotente. Coerente com Fase 1: search_path fixo, security_invoker=on nas
-- views, RLS habilitado em todas as tabelas + política aberta para service_role
-- (que já bypassa RLS mas a política existe para eliminar advisor INFO).
--
-- Rollback: bloco comentado no final do arquivo.

BEGIN;

-- ============================================================
-- 1. Tabela agent_episodes — memória episódica (Upgrade A + C)
-- ============================================================
-- Cada linha = um episódio de execução de task por um agente, com
-- autocrítica (Reflexion loop) + lições aprendidas. Consultada pelo
-- M18/RAG-manager antes de delegar tarefas para calibrar o agente.

CREATE TABLE IF NOT EXISTS public.agent_episodes (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id              TEXT NOT NULL,
  -- FK para manta_rag_queries — em prod PK é query_id BIGINT (não UUID).
  -- Opcional: episódios de tasks fora do RAG loop (ex.: intake routing) não
  -- têm query_id associado.
  query_id              BIGINT REFERENCES public.manta_rag_queries(query_id)
                         ON DELETE CASCADE,
  task_type             TEXT NOT NULL,
  task_description      TEXT,
  -- ★/★★/★★★ (evita char especial no schema; UI renderiza)
  output_tier           TEXT CHECK (output_tier IN ('star', 'star2', 'star3')),
  aluci_guard_pass      BOOLEAN,
  consist_guard_pass    BOOLEAN,
  iterations_needed     INTEGER DEFAULT 1
                         CHECK (iterations_needed >= 1 AND iterations_needed <= 5),
  self_critique         TEXT,
  lessons_learned       TEXT[] DEFAULT '{}',
  quality_score         NUMERIC(3,1)
                         CHECK (quality_score IS NULL OR
                                (quality_score >= 0 AND quality_score <= 10)),
  tokens_consumed       INTEGER,
  duration_seconds      INTEGER,
  model_used            TEXT,
  escalated_to_human    BOOLEAN DEFAULT FALSE,
  created_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE  public.agent_episodes IS
  'Memória episódica dos agentes (v4.7 Upgrade A+C). Cada linha registra uma execução com autocrítica (Reflexion) e lições aprendidas. Consultada por M18/RAG-manager antes de delegar tarefas para calibrar tier/prompt.';
COMMENT ON COLUMN public.agent_episodes.agent_id IS
  'Mesma convenção de manta_agent_capabilities.agent_id (ex.: 03-S6, M17, 00-maestro).';
COMMENT ON COLUMN public.agent_episodes.query_id IS
  'FK opcional para manta_rag_queries.query_id (BIGINT). NULL quando o episódio não veio do RAG loop (ex.: intake routing).';
COMMENT ON COLUMN public.agent_episodes.output_tier IS
  'star / star2 / star3 — evita char especial ★ para compat MCP; UI renderiza estrelas.';
COMMENT ON COLUMN public.agent_episodes.iterations_needed IS
  'Quantas iterações do Reflexion loop foram necessárias para atingir tier alvo (1..5).';
COMMENT ON COLUMN public.agent_episodes.self_critique IS
  'Autocrítica verbal em PT-BR emitida pelo próprio agente ao final da execução.';
COMMENT ON COLUMN public.agent_episodes.lessons_learned IS
  'Lições operacionais extraídas (array TEXT[]). Ex.: {"Sempre citar NBR 12211 em ETA","Confirmar TR/TP antes de recomendar batelada"}.';

CREATE INDEX IF NOT EXISTS idx_episodes_agent
  ON public.agent_episodes(agent_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_episodes_task
  ON public.agent_episodes(task_type, quality_score DESC);

CREATE INDEX IF NOT EXISTS idx_episodes_lessons
  ON public.agent_episodes USING GIN (lessons_learned);

-- Sparse: só linhas com FK preenchida entram no índice
CREATE INDEX IF NOT EXISTS idx_episodes_query_id
  ON public.agent_episodes(query_id)
  WHERE query_id IS NOT NULL;

ALTER TABLE public.agent_episodes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_service_role_all ON public.agent_episodes;
CREATE POLICY p_service_role_all
  ON public.agent_episodes
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================
-- 2. Tabela maestro_cost_log — cost tracking (Upgrade E)
-- ============================================================
-- Todo turno LLM (Haiku/Sonnet/Opus, com/sem cache) grava aqui uma linha
-- com input_tokens, output_tokens, cache tokens e custo estimado em USD.
-- Alimenta view v_cost_by_agent para painel de custos por agente/tier.

CREATE TABLE IF NOT EXISTS public.maestro_cost_log (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id              TEXT NOT NULL,
  model_used            TEXT NOT NULL,
  tier                  TEXT CHECK (tier IN ('T1', 'T2', 'T3', 'T4')),
  input_tokens          INTEGER NOT NULL,
  output_tokens         INTEGER NOT NULL,
  cache_read_tokens     INTEGER DEFAULT 0,
  cache_write_tokens    INTEGER DEFAULT 0,
  estimated_cost_usd    NUMERIC(10,6),
  task_type             TEXT,
  query_id              BIGINT REFERENCES public.manta_rag_queries(query_id)
                         ON DELETE SET NULL,
  episode_id            UUID   REFERENCES public.agent_episodes(id)
                         ON DELETE SET NULL,
  created_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE  public.maestro_cost_log IS
  'Log de custo por turno LLM (v4.7 Upgrade E). Alimentado por manta-hub/scripts em tempo de execução; agregado em v_cost_by_agent (últimos 30d).';
COMMENT ON COLUMN public.maestro_cost_log.tier IS
  'T1=Haiku (roteamento), T2=Sonnet (execução padrão), T3=Opus (alta complexidade), T4=reservado para modelos extendidos/reasoning.';
COMMENT ON COLUMN public.maestro_cost_log.cache_read_tokens IS
  'Tokens lidos do prompt cache Anthropic (10% do preço base).';
COMMENT ON COLUMN public.maestro_cost_log.cache_write_tokens IS
  'Tokens escritos no prompt cache Anthropic (125% do preço base).';

CREATE INDEX IF NOT EXISTS idx_cost_log_agent
  ON public.maestro_cost_log(agent_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cost_log_tier
  ON public.maestro_cost_log(tier, created_at DESC);

ALTER TABLE public.maestro_cost_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_service_role_all ON public.maestro_cost_log;
CREATE POLICY p_service_role_all
  ON public.maestro_cost_log
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ============================================================
-- 3. View v_cost_by_agent — custos por agente/tier (últimos 30d)
-- ============================================================
CREATE OR REPLACE VIEW public.v_cost_by_agent
  WITH (security_invoker = on)
AS
SELECT
  agent_id,
  tier,
  COUNT(*)                                                AS total_tasks,
  SUM(estimated_cost_usd)                                 AS total_cost_usd,
  AVG(estimated_cost_usd)                                 AS avg_cost_per_task,
  SUM(input_tokens + output_tokens)                       AS total_tokens,
  SUM(cache_read_tokens)                                  AS cache_read_tokens,
  MAX(created_at)                                         AS last_execution
FROM public.maestro_cost_log
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY agent_id, tier
ORDER BY total_cost_usd DESC NULLS LAST;

COMMENT ON VIEW public.v_cost_by_agent IS
  'Custo agregado por (agent_id, tier) nos últimos 30 dias. security_invoker=on desde o início (audit v4.6). Alimenta painel de custos e alertas de budget.';

-- ============================================================
-- 4. View v_episodes_health — saúde de episódios (últimos 30d)
-- ============================================================
CREATE OR REPLACE VIEW public.v_episodes_health
  WITH (security_invoker = on)
AS
SELECT
  agent_id,
  COUNT(*)                                                              AS total_episodes,
  ROUND(AVG(iterations_needed)::NUMERIC, 2)                             AS avg_iterations,
  ROUND(AVG(quality_score)::NUMERIC, 2)                                 AS avg_quality_score,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE escalated_to_human) / NULLIF(COUNT(*), 0),
    2
  )                                                                     AS pct_escalated,
  COUNT(*) FILTER (WHERE aluci_guard_pass = false)                      AS n_aluci_fail,
  COUNT(*) FILTER (WHERE consist_guard_pass = false)                    AS n_consist_fail,
  COUNT(*) FILTER (WHERE output_tier = 'star3')                         AS n_star3,
  COUNT(*) FILTER (WHERE output_tier = 'star2')                         AS n_star2,
  COUNT(*) FILTER (WHERE output_tier = 'star')                          AS n_star1,
  MAX(created_at)                                                       AS last_episode_at
FROM public.agent_episodes
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY agent_id
ORDER BY avg_quality_score DESC NULLS LAST;

COMMENT ON VIEW public.v_episodes_health IS
  'Saúde da memória episódica por agente (30d): média de iterações Reflexion, taxa de escalação humana, distribuição de output_tier. security_invoker=on.';

-- ============================================================
-- 5. Função get_relevant_episodes — leitura para M18/RAG-manager
-- ============================================================
CREATE OR REPLACE FUNCTION public.get_relevant_episodes(
    p_agent_id TEXT,
    p_task_type TEXT,
    p_limit INTEGER DEFAULT 5
) RETURNS TABLE (
    episode_id        UUID,
    self_critique     TEXT,
    lessons_learned   TEXT[],
    quality_score     NUMERIC,
    task_description  TEXT,
    created_at        TIMESTAMPTZ
)
LANGUAGE sql STABLE
SET search_path = public, extensions
AS $$
  SELECT
    id, self_critique, lessons_learned, quality_score, task_description, created_at
  FROM public.agent_episodes
  WHERE agent_id = p_agent_id
    AND task_type = p_task_type
  ORDER BY quality_score DESC NULLS LAST, created_at DESC
  LIMIT p_limit;
$$;

COMMENT ON FUNCTION public.get_relevant_episodes(TEXT, TEXT, INTEGER) IS
  'Retorna os top-N episódios de (agent_id, task_type) por qualidade e recência. Consumido pelo M18/RAG-manager antes de delegar task para calibrar prompt/tier.';

-- ============================================================
-- 6. Função consolidate_old_episodes — decay policy (§4.5)
-- ============================================================
-- Política:
--   30–90d:  agrupa por (agent_id, task_type), extrai top-3 lessons_learned
--            mais frequentes, cria 1 episódio-resumo com task_type
--            'destilled_<orig>' e deleta os originais.
--   > 90d:   apaga (as destiladas já cobrem).
-- Retorna: número TOTAL de episódios consolidados/apagados.

CREATE OR REPLACE FUNCTION public.consolidate_old_episodes()
RETURNS INTEGER
LANGUAGE plpgsql
SET search_path = public, extensions
AS $$
DECLARE
  n_destilled INTEGER := 0;
  n_deleted   INTEGER := 0;
  grp         RECORD;
  top_lessons TEXT[];
BEGIN
  -- 1) Destilação da janela 30..90d, ignorando destilados prévios
  FOR grp IN
    SELECT
      agent_id,
      task_type,
      COUNT(*)                       AS n_orig,
      AVG(quality_score)             AS avg_q,
      AVG(iterations_needed)         AS avg_iter,
      SUM(tokens_consumed)           AS sum_tokens,
      SUM(duration_seconds)          AS sum_dur,
      MIN(created_at)                AS first_at,
      MAX(created_at)                AS last_at
    FROM public.agent_episodes
    WHERE created_at BETWEEN NOW() - INTERVAL '90 days'
                         AND NOW() - INTERVAL '30 days'
      AND task_type NOT LIKE 'destilled_%'
    GROUP BY agent_id, task_type
    HAVING COUNT(*) >= 3   -- só destila grupos com massa mínima
  LOOP
    -- Top-3 lessons_learned mais frequentes no grupo
    SELECT ARRAY(
      SELECT lesson
      FROM (
        SELECT UNNEST(lessons_learned) AS lesson, COUNT(*) AS freq
        FROM public.agent_episodes
        WHERE agent_id = grp.agent_id
          AND task_type = grp.task_type
          AND created_at BETWEEN NOW() - INTERVAL '90 days'
                             AND NOW() - INTERVAL '30 days'
          AND task_type NOT LIKE 'destilled_%'
        GROUP BY lesson
        ORDER BY freq DESC
        LIMIT 3
      ) t
    ) INTO top_lessons;

    INSERT INTO public.agent_episodes (
      agent_id, task_type, task_description,
      iterations_needed, self_critique, lessons_learned,
      quality_score, tokens_consumed, duration_seconds,
      model_used, escalated_to_human, created_at
    ) VALUES (
      grp.agent_id,
      'destilled_' || grp.task_type,
      format('Destilado de %s episódios entre %s e %s',
             grp.n_orig,
             to_char(grp.first_at, 'YYYY-MM-DD'),
             to_char(grp.last_at,  'YYYY-MM-DD')),
      GREATEST(1, LEAST(5, ROUND(grp.avg_iter)::INTEGER)),
      format('Destilação automática (%s episódios). avg_quality=%s.',
             grp.n_orig, ROUND(grp.avg_q, 2)),
      COALESCE(top_lessons, '{}'),
      grp.avg_q,
      grp.sum_tokens,
      grp.sum_dur,
      'consolidator',
      false,
      grp.last_at
    );
    n_destilled := n_destilled + 1;

    DELETE FROM public.agent_episodes
    WHERE agent_id = grp.agent_id
      AND task_type = grp.task_type
      AND created_at BETWEEN NOW() - INTERVAL '90 days'
                         AND NOW() - INTERVAL '30 days'
      AND task_type NOT LIKE 'destilled_%';
  END LOOP;

  -- 2) Purga > 90d (destilados cobrem o histórico)
  WITH del AS (
    DELETE FROM public.agent_episodes
    WHERE created_at < NOW() - INTERVAL '90 days'
      AND task_type NOT LIKE 'destilled_%'
    RETURNING 1
  )
  SELECT COUNT(*) INTO n_deleted FROM del;

  RETURN n_destilled + n_deleted;
END;
$$;

COMMENT ON FUNCTION public.consolidate_old_episodes() IS
  'Decay policy (§4.5 roadmap v4.7): destila episódios 30..90d em resumos (top-3 lessons por grupo) e apaga originais + apaga tudo > 90d. Rodar via cron diário. Retorna n de destilados + apagados.';

COMMIT;

-- ============================================================
-- ROLLBACK (aplicar manualmente se preciso)
-- ============================================================
-- BEGIN;
-- DROP FUNCTION IF EXISTS public.consolidate_old_episodes();
-- DROP FUNCTION IF EXISTS public.get_relevant_episodes(TEXT, TEXT, INTEGER);
-- DROP VIEW     IF EXISTS public.v_episodes_health;
-- DROP VIEW     IF EXISTS public.v_cost_by_agent;
-- DROP TABLE    IF EXISTS public.maestro_cost_log CASCADE;
-- DROP TABLE    IF EXISTS public.agent_episodes CASCADE;
-- COMMIT;
