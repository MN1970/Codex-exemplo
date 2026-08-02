-- Manta Maestro — Analytics de Quarterly Review
-- Ticket: MNT-2026-ECOSYSTEM-UPGRADE-V5 (Fase 4.2 — Quarterly reviews)
-- Companion de: docs/QUARTERLY-REVIEW-TEMPLATE.md
--
-- IMPORTANTE — PRÉ-REQUISITO DE SCHEMA
-- ---------------------------------------------------------------------
-- Estas queries assumem o schema de registry/observabilidade proposto
-- em docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1 (tabelas `agents`,
-- `agent_health`, `routing_events`, `routing_feedback`). Em 2026-08-02
-- (v4.2 em produção) esse schema AINDA NÃO EXISTE — o Maestro v4.2 é
-- estático (CLAUDE.md + keywords) e não persiste routing logs.
--
-- Portanto, antes da PRIMEIRA quarterly review com dados reais:
--   1. Aplicar o schema de `routing_events` / `routing_feedback` /
--      `agent_health` (ver migração candidata a criar em
--      supabase/migrations/, espelhando §4.1 do doc de ecossistema).
--   2. Instrumentar o Maestro para logar cada decisão de roteamento
--      (Fase 1.4 do roadmap v5.0 — tracing/logging).
--   3. Rodar por >= 1 trimestre completo antes da 1ª review, para ter
--      volume estatisticamente útil.
--
-- Até lá, a seção "Pré-requisitos" do QUARTERLY-REVIEW-TEMPLATE.md
-- deve ser marcada como bloqueada e a review vira um gate de "dados
-- disponíveis? sim/não" em vez de análise de KPIs.
--
-- Todas as queries abaixo aceitam dois parâmetros de janela via psql
-- variables (:'period_start' / :'period_end'), formato 'YYYY-MM-DD'.
-- Exemplo de chamada:
--   psql "$SUPABASE_DB_URL" \
--     -v period_start="'2026-05-01'" -v period_end="'2026-08-01'" \
--     -f supabase/analytics/quarterly_review_kpis.sql
--
-- Se preferir rodar manualmente uma query por vez (recomendado na
-- reunião), copie o bloco desejado e substitua :'period_start' /
-- :'period_end' por literais.

-- =====================================================================
-- 1. ROUTING ANALYSIS — qual regra/agente é mais usado
-- =====================================================================

-- 1.1 Agente mais requisitado no trimestre (volume + share do total)
SELECT
  chosen_agent_id                                   AS agent_id,
  a.name                                             AS agent_name,
  COUNT(*)                                           AS routes,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
  ROUND(AVG(chosen_confidence)::numeric, 3)          AS avg_confidence,
  ROUND(AVG(latency_ms)::numeric, 0)                 AS avg_latency_ms
FROM routing_events re
LEFT JOIN agents a ON a.id = re.chosen_agent_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY chosen_agent_id, a.name
ORDER BY routes DESC;

-- 1.2 Regra de routing mais acionada (por keyword, se instrumentado)
-- Assumes `routing_events.matched_keyword TEXT` (extensão sugerida ao
-- schema §4.1 para rastrear qual regra do CLAUDE.md disparou o match;
-- se ausente, comentar este bloco e usar 1.1 como proxy por agente).
SELECT
  matched_keyword,
  chosen_agent_id,
  COUNT(*) AS times_matched
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND matched_keyword IS NOT NULL
GROUP BY matched_keyword, chosen_agent_id
ORDER BY times_matched DESC
LIMIT 30;

-- 1.3 Distribuição por eixo (horizontal x vertical x lifecycle-phase)
-- Assumes `agents.axis TEXT CHECK (axis IN ('horizontal','vertical'))`.
SELECT
  a.axis,
  COUNT(*)                                            AS routes,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct_of_total
FROM routing_events re
JOIN agents a ON a.id = re.chosen_agent_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY a.axis
ORDER BY routes DESC;

-- =====================================================================
-- 2. GAP DETECTION — queries mal roteadas (regra: >100 bad feedback)
-- =====================================================================

-- 2.1 Agentes com feedback negativo acima do threshold (100) no trimestre
-- feedback negativo = 'wrong' | 'slow' | 'incomplete' (ver §4.1)
WITH bad_feedback AS (
  SELECT
    rf.agent_id,
    rf.feedback,
    COUNT(*) AS n
  FROM routing_feedback rf
  WHERE rf.created_at >= :'period_start'::timestamptz
    AND rf.created_at <  :'period_end'::timestamptz
    AND rf.feedback IN ('wrong', 'slow', 'incomplete')
  GROUP BY rf.agent_id, rf.feedback
)
SELECT
  agent_id,
  SUM(n) AS total_bad_feedback,
  jsonb_object_agg(feedback, n) AS breakdown
FROM bad_feedback
GROUP BY agent_id
HAVING SUM(n) > 100          -- <-- threshold do processo (ver template)
ORDER BY total_bad_feedback DESC;

-- 2.2 Fallbacks acionados (Maestro trocou de agente no meio da rota)
SELECT
  chosen_agent_id      AS original_agent,
  outcome_agent_id     AS fallback_agent,
  COUNT(*)             AS fallback_count
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND outcome = 'fallback'
GROUP BY chosen_agent_id, outcome_agent_id
ORDER BY fallback_count DESC;

-- 2.3 Queries com baixa confiança de roteamento (candidatas a gap de
-- keyword/segmento) — não necessariamente com feedback negativo ainda,
-- mas sinal antecedente de má cobertura.
SELECT
  chosen_agent_id,
  COUNT(*)                                    AS low_confidence_routes,
  ROUND(AVG(chosen_confidence)::numeric, 3)   AS avg_confidence
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND chosen_confidence < 0.60                -- limiar sugerido; ajustar
GROUP BY chosen_agent_id
ORDER BY low_confidence_routes DESC;

-- =====================================================================
-- 3. TRENDING — segmentos emergentes (queries recorrentes fora do mapa)
-- =====================================================================

-- 3.1 Crescimento mês a mês de composições multi-agente (proxy de novo
-- caso de uso / segmento cruzado que hoje exige handoff manual)
SELECT
  DATE_TRUNC('month', created_at)::date AS month,
  COUNT(*) FILTER (WHERE is_composed)   AS composed_routes,
  COUNT(*)                              AS total_routes,
  ROUND(100.0 * COUNT(*) FILTER (WHERE is_composed) / NULLIF(COUNT(*), 0), 1)
                                          AS pct_composed
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
GROUP BY 1
ORDER BY 1;

-- 3.2 Combinações de agentes mais compostas (candidatos a virar 1 agente
-- só, ou a virar handoff formalizado no CLAUDE.md)
SELECT
  composed_agents,
  composition_strategy,
  COUNT(*) AS occurrences
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND is_composed
GROUP BY composed_agents, composition_strategy
ORDER BY occurrences DESC
LIMIT 20;

-- 3.3 "Sem agente claro" — outcome = 'error' ou confidence muito baixa,
-- agrupado por termos extraídos da query (heurística simples via
-- ts_vector; refinar com embeddings quando disponível)
SELECT
  word,
  COUNT(*) AS occurrences
FROM routing_events,
     LATERAL unnest(
       string_to_array(lower(regexp_replace(query, '[^a-zà-ú0-9 ]', '', 'g')), ' ')
     ) AS word
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND (outcome = 'error' OR chosen_confidence < 0.50)
  AND length(word) > 4          -- corta stopwords curtas
GROUP BY word
ORDER BY occurrences DESC
LIMIT 40;

-- =====================================================================
-- 4. KEY METRICS — accuracy trend, throughput growth, cost/request
-- =====================================================================

-- 4.1 Routing accuracy trend (mensal) — success rate + feedback positivo
SELECT
  DATE_TRUNC('month', re.created_at)::date AS month,
  COUNT(*)                                                          AS total_routes,
  ROUND(100.0 * COUNT(*) FILTER (WHERE re.outcome = 'success')
        / NULLIF(COUNT(*), 0), 1)                                    AS success_rate_pct,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rf.feedback = 'correct')
        / NULLIF(COUNT(rf.id), 0), 1)                                 AS positive_feedback_pct
FROM routing_events re
LEFT JOIN routing_feedback rf ON rf.routing_id = re.routing_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY 1
ORDER BY 1;

-- 4.2 Throughput growth (mensal, trimestre atual vs trimestre anterior)
WITH monthly AS (
  SELECT
    DATE_TRUNC('month', created_at)::date AS month,
    COUNT(*)                              AS routes
  FROM routing_events
  WHERE created_at >= (:'period_start'::timestamptz - INTERVAL '3 months')
    AND created_at <  :'period_end'::timestamptz
  GROUP BY 1
)
SELECT
  month,
  routes,
  LAG(routes) OVER (ORDER BY month)                                   AS routes_prev_month,
  ROUND(100.0 * (routes - LAG(routes) OVER (ORDER BY month))
        / NULLIF(LAG(routes) OVER (ORDER BY month), 0), 1)            AS mom_growth_pct
FROM monthly
ORDER BY month;

-- 4.3 Cost per request (por agente, tokens_used médio x custo estimado)
-- Assumes `routing_events.tokens_used` e `agents.cost_per_call`
-- (estimativa de custo unitário por token/1k, ajustar constante de preço
-- conforme tabela de pricing vigente do modelo usado por cada agente).
SELECT
  re.chosen_agent_id                                       AS agent_id,
  a.model,
  COUNT(*)                                                 AS routes,
  ROUND(AVG(re.tokens_used)::numeric, 0)                   AS avg_tokens_per_request,
  ROUND(SUM(re.tokens_used)::numeric, 0)                   AS total_tokens,
  -- custo estimado: ajustar price_per_1k_tokens por modelo antes de usar
  ROUND(SUM(re.tokens_used) / 1000.0 *
        (CASE a.model
           WHEN 'haiku'  THEN 0.0008  -- placeholder — atualizar com pricing real
           WHEN 'sonnet' THEN 0.003
           WHEN 'opus'   THEN 0.015
           ELSE 0.003
         END)::numeric, 2)                                 AS estimated_cost_usd,
  ROUND((SUM(re.tokens_used) / 1000.0 *
        (CASE a.model
           WHEN 'haiku'  THEN 0.0008
           WHEN 'sonnet' THEN 0.003
           WHEN 'opus'   THEN 0.015
           ELSE 0.003
         END)) / NULLIF(COUNT(*), 0), 4)                    AS estimated_cost_per_request_usd
FROM routing_events re
JOIN agents a ON a.id = re.chosen_agent_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY re.chosen_agent_id, a.model
ORDER BY total_tokens DESC;

-- 4.4 SLA snapshot do trimestre (comparar contra alvos do roadmap v5.0,
-- doc MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1 tabela de métricas)
SELECT
  COUNT(*)                                                              AS total_routes,
  ROUND(100.0 * COUNT(*) FILTER (WHERE outcome = 'success')
        / NULLIF(COUNT(*), 0), 1)                                        AS success_rate_pct,
  ROUND(100.0 * COUNT(*) FILTER (WHERE outcome = 'fallback')
        / NULLIF(COUNT(*), 0), 1)                                        AS fallback_pct,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms)                AS p50_latency_ms,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms)               AS p99_latency_ms,
  ROUND(100.0 * COUNT(*) FILTER (WHERE is_composed)
        / NULLIF(COUNT(*), 0), 1)                                        AS composition_pct
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz;

-- 4.5 Agent health snapshot (uptime aproximado via amostras de heartbeat)
SELECT
  agent_id,
  COUNT(*)                                                          AS heartbeats,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'healthy')
        / NULLIF(COUNT(*), 0), 1)                                    AS uptime_pct_approx,
  ROUND(AVG(error_rate_24h)::numeric, 4)                            AS avg_error_rate_24h,
  ROUND(AVG(avg_latency_ms)::numeric, 0)                            AS avg_latency_ms
FROM agent_health
WHERE recorded_at >= :'period_start'::timestamptz
  AND recorded_at <  :'period_end'::timestamptz
GROUP BY agent_id
ORDER BY uptime_pct_approx ASC;

-- =====================================================================
-- 5. RECOMMENDATION HELPERS — sinais para decisão humana na reunião
-- =====================================================================

-- 5.1 Candidatos a "novo agente vertical": clusters de baixa confiança
-- e alto volume (>= 100 ocorrências) que não colam bem em nenhum
-- agente existente — combinar com 3.3 (palavras mais frequentes) e
-- revisão manual/qualitativa dos textos de query originais.
SELECT
  chosen_agent_id,
  COUNT(*)                                  AS routes,
  ROUND(AVG(chosen_confidence)::numeric, 3) AS avg_confidence
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND chosen_confidence < 0.60
GROUP BY chosen_agent_id
HAVING COUNT(*) >= 100
ORDER BY routes DESC;

-- 5.2 Candidatos a "upgrade de tier" (haiku/sonnet → sonnet/opus):
-- agentes com volume alto + confiança/success baixos, sugerindo que
-- o modelo atual está subdimensionado para a complexidade real.
SELECT
  a.id            AS agent_id,
  a.model         AS current_model,
  COUNT(*)                                            AS routes,
  ROUND(100.0 * COUNT(*) FILTER (WHERE re.outcome = 'success')
        / NULLIF(COUNT(*), 0), 1)                      AS success_rate_pct,
  ROUND(AVG(re.chosen_confidence)::numeric, 3)         AS avg_confidence
FROM routing_events re
JOIN agents a ON a.id = re.chosen_agent_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY a.id, a.model
HAVING COUNT(*) >= 50
   AND (100.0 * COUNT(*) FILTER (WHERE re.outcome = 'success') / NULLIF(COUNT(*), 0)) < 90
ORDER BY routes DESC;

-- 5.3 Candidatos a "refinar keywords": agente com volume ok e confiança
-- ok, mas feedback negativo concentrado (indica que chegou no agente
-- certo, mas a keyword trouxe caso fora do escopo real do agente).
SELECT
  rf.agent_id,
  COUNT(*)                                    AS bad_feedback,
  ROUND(AVG(re.chosen_confidence)::numeric, 3) AS avg_confidence_when_bad
FROM routing_feedback rf
JOIN routing_events re ON re.routing_id = rf.routing_id
WHERE rf.created_at >= :'period_start'::timestamptz
  AND rf.created_at <  :'period_end'::timestamptz
  AND rf.feedback IN ('wrong', 'incomplete')
  AND re.chosen_confidence >= 0.75   -- roteou "confiante", mas errou
GROUP BY rf.agent_id
HAVING COUNT(*) > 20
ORDER BY bad_feedback DESC;
