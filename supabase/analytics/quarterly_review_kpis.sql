-- Manta Maestro — Analytics de Quarterly Review
-- Ticket: MNT-2026-ECOSYSTEM-UPGRADE-V5 (Fase 4.2 — Quarterly reviews)
-- Companion de: docs/QUARTERLY-REVIEW-TEMPLATE.md
--
-- SCHEMA-BASE DESTAS QUERIES (o que existe de fato hoje, 2026-08-02)
-- ---------------------------------------------------------------------
-- `agents`                     — supabase/migrations/2026_08_02_agent_auto_registration.sql
-- `routing_events`             — supabase/migrations/2026_08_02_routing_observability.sql
-- `routing_feedback`           — idem (espelha feedback_loop.py)
-- `agent_health` (estado atual, 1 linha/agente, SEM histórico) —
--                                 supabase/migrations/2026_08_02_agent_health_heartbeat.sql
--                                 (é a versão que services/heartbeat/heartbeat-service.js
--                                 realmente grava — ver ATENÇÃO abaixo)
--
-- Estas 3 primeiras já existem em código funcional (feedback_loop.py +
-- migração companheira). O que NÃO existe ainda e por isso NÃO está
-- nestas queries: `outcome`/fallback (Fase 2.3), composição multi-agente
-- `is_composed` (Fase 2.2), `matched_keyword` explícito por regra do
-- CLAUDE.md. Onde o KPI pedido depende disso, a query abaixo entrega o
-- melhor proxy possível hoje e comenta o que falta instrumentar.
--
-- ATENÇÃO — CONFLITO agent_health: há uma 2ª definição incompatível de
-- `agent_health` (série temporal) em
-- supabase/migrations/2026_08_02_agent_auto_registration.sql. Como
-- ambas usam `CREATE TABLE IF NOT EXISTS`, só a que rodar primeiro
-- realmente existe; a query 5.x (agent health) deste arquivo assume a
-- versão "estado atual" (heartbeat), que é a que o serviço em produção
-- de fato escreve. Resolver esse conflito é pré-requisito da Seção 5
-- do QUARTERLY-REVIEW-TEMPLATE.md — ver nota lá.
--
-- Todas as queries de janela temporal aceitam dois parâmetros via
-- psql variables (:'period_start' / :'period_end'), formato
-- 'YYYY-MM-DD'. Exemplo:
--   psql "$SUPABASE_DB_URL" \
--     -v period_start="'2026-05-01'" -v period_end="'2026-08-01'" \
--     -f supabase/analytics/quarterly_review_kpis.sql
-- Ou copie um bloco por vez e substitua os literais manualmente
-- (recomendado ao rodar ao vivo na reunião).

-- =====================================================================
-- 1. ROUTING ANALYSIS — qual regra/agente é mais usado
-- =====================================================================

-- 1.1 Agente mais requisitado no trimestre (volume + share + confiança)
SELECT
  re.chosen_agent_id                                   AS agent_id,
  a.name                                                AS agent_name,
  a.model,
  COUNT(*)                                              AS routes,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)    AS pct_of_total,
  ROUND(AVG(re.chosen_confidence)::numeric, 3)          AS avg_confidence,
  ROUND(AVG(re.latency_ms)::numeric, 0)                 AS avg_latency_ms  -- NULL até instrumentar (ver migração)
FROM routing_events re
LEFT JOIN agents a ON a.id = re.chosen_agent_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY re.chosen_agent_id, a.name, a.model
ORDER BY routes DESC;

-- 1.2 Distribuição por eixo (horizontal x vertical), inferida pela
-- convenção de nomenclatura do slug (não existe coluna `axis` em
-- `agents` hoje). Convenção observada no repo: agentes verticais por
-- segmento usam prefixo "agente-*" (ex.: agente-saneamento);
-- horizontais usam prefixo "manta-*" (ex.: manta-05). Ajustar o CASE
-- abaixo se a convenção mudar, ou promover isso a coluna real
-- (`agents.axis`) em migração futura para parar de depender de regex.
SELECT
  CASE
    WHEN re.chosen_agent_id LIKE 'agente-%' THEN 'vertical (segmento)'
    WHEN re.chosen_agent_id LIKE 'manta-%'  THEN 'horizontal'
    ELSE 'desconhecido/outro'
  END                                                    AS axis,
  COUNT(*)                                                AS routes,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)      AS pct_of_total
FROM routing_events re
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY 1
ORDER BY routes DESC;

-- 1.3 "Regra mais usada" — proxy via keywords do agente vs. texto da
-- query. Requer `query_preview` (só os 200 primeiros caracteres — ver
-- routing_events) e a lista `agents.keywords`. É uma aproximação: só
-- enxerga keywords presentes no preview truncado, e não sabe qual
-- keyword *especificamente* disparou o match no Maestro (o Maestro não
-- loga isso hoje). Para precisão real, adicionar
-- `routing_events.matched_keyword TEXT` e popular no momento do
-- roteamento (mudança de 1 linha no Maestro, migração de 1 coluna).
SELECT
  kw                                        AS keyword,
  re.chosen_agent_id,
  COUNT(*)                                  AS query_previews_matching
FROM routing_events re
JOIN agents a ON a.id = re.chosen_agent_id
CROSS JOIN LATERAL unnest(a.keywords) AS kw
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
  AND re.query_preview ILIKE '%' || kw || '%'
GROUP BY kw, re.chosen_agent_id
ORDER BY query_previews_matching DESC
LIMIT 30;

-- =====================================================================
-- 2. GAP DETECTION — queries mal roteadas (regra: >100 bad feedback)
-- =====================================================================

-- 2.1 Agentes acima do threshold de feedback negativo no trimestre
-- (feedback negativo = 'wrong' | 'slow' | 'incomplete', igual ao
-- reward_map de feedback_loop.py). Este é o KPI central de gap
-- detection pedido no processo.
WITH bad_feedback AS (
  SELECT rf.agent_id, rf.feedback, COUNT(*) AS n
  FROM routing_feedback rf
  WHERE rf.created_at >= :'period_start'::timestamptz
    AND rf.created_at <  :'period_end'::timestamptz
    AND rf.feedback IN ('wrong', 'slow', 'incomplete')
  GROUP BY rf.agent_id, rf.feedback
)
SELECT
  agent_id,
  SUM(n)                        AS total_bad_feedback,
  jsonb_object_agg(feedback, n) AS breakdown
FROM bad_feedback
GROUP BY agent_id
HAVING SUM(n) > 100             -- <-- threshold do processo (ver template §3.1)
ORDER BY total_bad_feedback DESC;

-- 2.2 Rotas de baixa confiança (Thompson Sampling amostrou theta_hat
-- baixo) — sinal antecedente de má cobertura, mesmo antes do feedback
-- humano chegar.
SELECT
  chosen_agent_id,
  COUNT(*)                                  AS low_confidence_routes,
  ROUND(AVG(chosen_confidence)::numeric, 3) AS avg_confidence
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND chosen_confidence < 0.60               -- limiar sugerido; ajustar por experiência
GROUP BY chosen_agent_id
ORDER BY low_confidence_routes DESC;

-- 2.3 Beta posterior atual por agente (crença acumulada de qualidade,
-- não só do trimestre — mostra o estado "vitalício" do bandit; útil
-- para contextualizar 2.1/2.2 com histórico de mais longo prazo).
-- Requer `agent_posteriors` populada (só acontece se SupabaseFeedbackStore
-- estiver de fato implementado e em uso — hoje é um stub, ver
-- feedback_loop.py). Se a tabela estiver vazia, pular esta query.
SELECT
  agent_id,
  alpha,
  beta,
  ROUND((alpha / (alpha + beta))::numeric, 3)                          AS posterior_mean,
  ROUND(((alpha * beta) / (POWER(alpha + beta, 2) * (alpha + beta + 1)))::numeric, 5)
                                                                         AS posterior_variance,
  n_updates,
  updated_at
FROM agent_posteriors
ORDER BY posterior_mean ASC;

-- 2.4 Fallback / composição multi-agente — NÃO DISPONÍVEL HOJE.
-- Fase 2.2 (composição) e Fase 2.3 (fallback com Markov chain) do
-- roadmap v5.0 ainda não estão implementadas no Maestro, então
-- `routing_events` não tem `outcome`, `is_composed`, `composed_agents`.
-- Quando essas fases forem implementadas, replicar aqui as queries
-- 2.2/3.1/3.2 descritas em versões anteriores deste arquivo (ver
-- histórico do git) — a estrutura de query já está desenhada, só
-- falta o schema/dado de origem existir.

-- =====================================================================
-- 3. TRENDING — segmentos emergentes (queries recorrentes fora do mapa)
-- =====================================================================

-- 3.1 Termos frequentes em rotas de baixa confiança (candidatos a
-- segmento não coberto). Usa `query_preview` (200 chars truncados —
-- suficiente para tema geral, não para leitura integral da query).
SELECT
  word,
  COUNT(*) AS occurrences
FROM routing_events,
     LATERAL unnest(
       string_to_array(
         lower(regexp_replace(coalesce(query_preview, ''), '[^a-zà-ú0-9 ]', '', 'g')),
         ' '
       )
     ) AS word
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
  AND chosen_confidence < 0.50
  AND length(word) > 4              -- corta stopwords curtas
GROUP BY word
ORDER BY occurrences DESC
LIMIT 40;

-- 3.2 Crescimento mês a mês do volume de rotas de baixa confiança —
-- se um tema emergente está crescendo (e não é ruído pontual), este
-- número deve subir mês a mês dentro do próprio trimestre.
SELECT
  DATE_TRUNC('month', created_at)::date AS month,
  COUNT(*) FILTER (WHERE chosen_confidence < 0.60) AS low_confidence_routes,
  COUNT(*)                                          AS total_routes,
  ROUND(100.0 * COUNT(*) FILTER (WHERE chosen_confidence < 0.60)
        / NULLIF(COUNT(*), 0), 1)                    AS pct_low_confidence
FROM routing_events
WHERE created_at >= :'period_start'::timestamptz
  AND created_at <  :'period_end'::timestamptz
GROUP BY 1
ORDER BY 1;

-- 3.3 Composição multi-agente — NÃO DISPONÍVEL HOJE (ver nota em 2.4).

-- =====================================================================
-- 4. KEY METRICS — accuracy trend, throughput growth, cost/request
-- =====================================================================

-- 4.1 Routing accuracy trend (mensal) — % de feedback 'correct' entre
-- todo o feedback recebido, e reward médio (0..1, ponderando parcial
-- credit de 'slow'/'incomplete' — ver DEFAULT_REWARD_MAP em
-- feedback_loop.py).
SELECT
  DATE_TRUNC('month', rf.created_at)::date AS month,
  COUNT(*)                                                    AS feedback_events,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rf.feedback = 'correct')
        / NULLIF(COUNT(*), 0), 1)                              AS pct_correct,
  ROUND(AVG(rf.reward)::numeric, 3)                           AS avg_reward
FROM routing_feedback rf
WHERE rf.created_at >= :'period_start'::timestamptz
  AND rf.created_at <  :'period_end'::timestamptz
GROUP BY 1
ORDER BY 1;

-- 4.2 Throughput growth (mensal, trimestre atual + mês anterior para MoM)
WITH monthly AS (
  SELECT DATE_TRUNC('month', created_at)::date AS month, COUNT(*) AS routes
  FROM routing_events
  WHERE created_at >= (:'period_start'::timestamptz - INTERVAL '1 month')
    AND created_at <  :'period_end'::timestamptz
  GROUP BY 1
)
SELECT
  month,
  routes,
  LAG(routes) OVER (ORDER BY month)                                AS routes_prev_month,
  ROUND(100.0 * (routes - LAG(routes) OVER (ORDER BY month))
        / NULLIF(LAG(routes) OVER (ORDER BY month), 0), 1)          AS mom_growth_pct
FROM monthly
ORDER BY month;

-- 4.3 Cost per request — PARCIALMENTE DISPONÍVEL. `routing_events.tokens_used`
-- é NULL até o Maestro passar a logar consumo real de tokens (ver
-- comentário na migração 2026_08_02_routing_observability.sql). Até lá,
-- este é o melhor proxy possível: `agents.cost_per_call`, uma
-- ESTIMATIVA ESTÁTICA de tokens por chamada (não medida), multiplicada
-- por um preço/1k tokens placeholder — NÃO reportar como custo real à
-- liderança sem atualizar os dois: (a) tokens_used real, (b) pricing
-- vigente do modelo.
SELECT
  re.chosen_agent_id                                       AS agent_id,
  a.model,
  a.cost_per_call                                          AS estimated_tokens_per_call_static,
  COUNT(*)                                                 AS routes,
  ROUND(AVG(re.tokens_used)::numeric, 0)                   AS avg_tokens_used_real,  -- NULL se não instrumentado
  COUNT(re.tokens_used)                                    AS routes_with_real_token_data,
  ROUND(
    (a.cost_per_call * COUNT(*) / 1000.0) *
    (CASE a.model
       WHEN 'haiku'  THEN 0.0008   -- placeholder — atualizar com pricing real vigente
       WHEN 'sonnet' THEN 0.003
       WHEN 'opus'   THEN 0.015
       ELSE 0.003
     END)
  ::numeric, 2)                                             AS estimated_cost_usd_static_proxy
FROM routing_events re
JOIN agents a ON a.id = re.chosen_agent_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY re.chosen_agent_id, a.model, a.cost_per_call
ORDER BY routes DESC;

-- 4.4 Agent health — snapshot ATUAL (não é trend histórico; a tabela
-- `agent_health` em uso real (heartbeat) guarda 1 linha por agente,
-- sobrescrita a cada heartbeat — ver ATENÇÃO no topo do arquivo). Para
-- um trend real de uptime ao longo do trimestre seria necessário um
-- `agent_health_history` (append-only) que não existe hoje.
SELECT
  agent_id,
  status,
  routable,
  queue_depth,
  error_rate_5m,
  last_heartbeat_at,
  unhealthy_since,
  updated_at
FROM agent_health
ORDER BY
  CASE status WHEN 'unhealthy' THEN 0 WHEN 'degraded' THEN 1 ELSE 2 END,
  agent_id;

-- =====================================================================
-- 5. RECOMMENDATION HELPERS — sinais para decisão humana na reunião
-- =====================================================================

-- 5.1 Candidatos a "novo agente vertical": volume alto + confiança
-- baixa persistente (combinar com 3.1 para ver os termos concretos).
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

-- 5.2 Candidatos a "upgrade de tier": volume alto + accuracy real
-- (feedback 'correct') baixa no tier atual.
SELECT
  a.id                                                 AS agent_id,
  a.model                                              AS current_model,
  COUNT(DISTINCT re.routing_id)                        AS routes,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rf.feedback = 'correct')
        / NULLIF(COUNT(rf.id), 0), 1)                   AS pct_correct
FROM routing_events re
JOIN agents a ON a.id = re.chosen_agent_id
LEFT JOIN routing_feedback rf ON rf.routing_id = re.routing_id
WHERE re.created_at >= :'period_start'::timestamptz
  AND re.created_at <  :'period_end'::timestamptz
GROUP BY a.id, a.model
HAVING COUNT(DISTINCT re.routing_id) >= 50
   AND (100.0 * COUNT(*) FILTER (WHERE rf.feedback = 'correct') / NULLIF(COUNT(rf.id), 0)) < 90
ORDER BY routes DESC;

-- 5.3 Candidatos a "refinar keywords": Maestro roteou CONFIANTE
-- (theta_hat alto) mas o feedback veio negativo mesmo assim — sinal de
-- que a keyword/regra trouxe um caso fora do escopo real do agente,
-- não um problema de confiança/ranking.
SELECT
  rf.agent_id,
  COUNT(*)                                     AS bad_feedback,
  ROUND(AVG(re.chosen_confidence)::numeric, 3) AS avg_confidence_when_bad
FROM routing_feedback rf
JOIN routing_events re ON re.routing_id = rf.routing_id
WHERE rf.created_at >= :'period_start'::timestamptz
  AND rf.created_at <  :'period_end'::timestamptz
  AND rf.feedback IN ('wrong', 'incomplete')
  AND re.chosen_confidence >= 0.75             -- roteou "confiante", mas errou
GROUP BY rf.agent_id
HAVING COUNT(*) > 20
ORDER BY bad_feedback DESC;
