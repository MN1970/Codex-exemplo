# DATADOG DASHBOARD SPEC — Manta Maestro v5.0

**Dashboard name**: `Manta Maestro v5.0 — Ecosystem Health`
**Ticket**: MNT-2026-ECOSYSTEM-UPGRADE-V5 (segue `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`)
**Layout**: `ordered` (free-form groups per seção, screenboard-style dentro de um dashboard `ordered`)
**Owner**: Maestro architect + DevOps/Infra
**Reload cadence**: 10s (live) para Seção 1-2, 1min para Seção 3-5
**Status**: 📝 Spec — aguarda implementação da instrumentação OTel→Datadog (Fase 1, §2.4 e §4.3 do upgrade doc)

---

## 0. Pré-requisitos de instrumentação

O dashboard consome métricas emitidas pelo exporter OTel→Datadog descrito em
`docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` §4.3 (`DatadogMetricExporter` +
`DatadogSpanExporter`, meter `manta.maestro`). Este spec **estende** o catálogo de
métricas já definido lá (`manta.routing.total`, `manta.routing.latency`) com as
métricas adicionais necessárias para as 5 seções pedidas.

### 0.1 Catálogo de métricas (namespace `manta.*`)

| Métrica | Tipo | Unidade | Tags obrigatórias | Descrição |
|---|---|---|---|---|
| `manta.routing.total` | count | requests | `outcome` (success\|fallback\|error), `agent_id`, `segment`, `model` | Total de decisões de roteamento do Maestro |
| `manta.routing.latency` | distribution | ms | `agent_id`, `segment` | Latência fim-a-fim do `maestro.route()` — Datadog deriva `.avg`, `.count`, `.max`, `.min`, `.sum` e percentis via `p50:`/`p90:`/`p95:`/`p99:` |
| `manta.routing.composed` | count | requests | `strategy` (serial\|parallel) | Roteamentos que dispararam composição multi-agente |
| `manta.routing.fallback` | count | requests | `from_agent_id`, `to_agent_id` | Fallbacks acionados (Markov chain, §4.2) |
| `manta.agent.health.status` | gauge | enum (0=down,1=degraded,2=healthy) | `agent_id`, `segment` | Último heartbeat reportado (`agent_health.status`) |
| `manta.agent.queue_depth` | gauge | jobs | `agent_id`, `segment` | Fila corrente do agente (`agent_health.queue_depth`) |
| `manta.agent.errors` | count | errors | `agent_id`, `segment`, `error_type` | Erros do agente na janela (`agent_health.error_count`) |
| `manta.agent.calls` | count | requests | `agent_id`, `segment` | Chamadas totais ao agente (`success_count + error_count`) |
| `manta.agent.uptime_check` | gauge | bool (1=up, 0=down) | `agent_id` | Resultado do heartbeat/ping periódico — base para monitor de uptime e SLO |
| `manta.feedback.received` | count | events | `outcome` (correct\|wrong\|slow\|incomplete), `agent_id` | Evento `routing_feedback` (thumbs up/down) |
| `manta.feedback.reranking` | count | events | `agent_id` | Correções aplicadas ao bandit/ranking (`acceptFeedback` → `updatePosterior`) |
| `manta.routing.tokens` | distribution | tokens | `agent_id`, `model` | `tokens_used` por evento de roteamento (`routing_events.tokens_used`) |
| `manta.routing.cost_usd` | distribution | USD | `agent_id`, `model` | Custo estimado por chamada (`tokens_used` × preço do tier, calculado no pipeline antes do submit) |

> **Nota de nomenclatura:** tag `segment` usa a taxonomia canônica v5.0.1 (`S1`…`S11`
> verticais, `A1`…`A10` horizontais — ver skill `manta-maestro` v5.0.1). Tag `model`
> usa `haiku`\|`sonnet`\|`opus`. Enquanto a reconciliação `03-S*`/`M*` → `A*/S*`
> (pendência bloqueante registrada no §9.3.21-E da skill) não fechar, mapear os
> IDs legados para os canônicos na camada de submit — não duplicar séries.

### 0.2 Template variables do dashboard

| Variável | Fonte da tag | Default |
|---|---|---|
| `$env` | `env` | `prod` |
| `$segment` | `segment` | `*` |
| `$agent` | `agent_id` | `*` |
| `$model` | `model` | `*` |

Todas as queries abaixo devem ser lidas com esses template vars aplicados
(omitidos no texto por brevidade, mas equivalem a `{env:$env,segment:$segment,agent_id:$agent,model:$model}`).

---

## 1. Seção — Routing Performance

Grupo de 4 widgets, topo do dashboard (visão executiva de 24h).

### 1.1 Timeseries — Routing Latency p50/p99

- **Tipo**: `timeseries`, linha, dois eixos sobrepostos
- **Query A (p50)**: `p50:manta.routing.latency{$env,$segment,$agent,$model}`
- **Query B (p99)**: `p99:manta.routing.latency{$env,$segment,$agent,$model}`
- **Markers**: linha horizontal fixa em `y=2000` (2s) rotulada "SLA P99" — mesma
  cor do monitor de alerta (§6.1) para leitura visual imediata de violação
- **Display**: `line`, p50 em azul (`#3b82f6`), p99 em laranja (`#f59e0b`)

### 1.2 Query Value — Routing Success Rate

- **Tipo**: `query_value`
- **Query**: `sum:manta.routing.total{outcome:success,$env,$segment,$agent,$model}.as_count() / sum:manta.routing.total{$env,$segment,$agent,$model}.as_count() * 100`
- **Formato**: percentual, 1 casa decimal
- **Conditional formatting**: verde ≥95%, amarelo 90-95%, vermelho <90%
- **Timeframe**: last 24h (comparação com "last 24h vs. previous 24h" habilitada)

### 1.3 Top List — Top Agents por volume

- **Tipo**: `toplist`
- **Query**: `top(sum:manta.routing.total{$env,$segment,$model} by {agent_id}.as_count(), 10, 'sum', 'desc')`
- **Ordenação**: desc por volume
- **Uso**: identifica quais agentes (S1-S11/A1-A10) concentram tráfego — alimenta
  revisão trimestral (§4.2 do upgrade doc)

### 1.4 Table — Top Agents: volume × success rate

- **Tipo**: `table`, uma linha por `agent_id`
- **Colunas**:
  - Volume: `sum:manta.routing.total{$env,$segment,$model} by {agent_id}.as_count()`
  - Success %: `sum:manta.routing.total{outcome:success,$env,$segment,$model} by {agent_id}.as_count() / sum:manta.routing.total{$env,$segment,$model} by {agent_id}.as_count() * 100`
  - p99 latency: `p99:manta.routing.latency{$env,$segment,$model} by {agent_id}`
- **Conditional formatting** na coluna Success %: mesmas faixas do widget 1.2

### 1.5 Timeseries — Fallback rate

- **Tipo**: `timeseries`, área
- **Query**: `sum:manta.routing.fallback{$env,$segment}.as_count() / sum:manta.routing.total{$env,$segment}.as_count() * 100`
- **Marker**: linha em `y=5` (5%, target do §4.1 do upgrade doc: "Fallback triggered % <5%")

---

## 2. Seção — Agent Health

Grupo de 4 widgets. Granularidade por `agent_id`, refresh 10s.

### 2.1 Status Table — Health por agente

- **Tipo**: `table` (ou `hostmap`-style se preferir densidade visual)
- **Query**: `avg:manta.agent.health.status{$env,$segment,$agent} by {agent_id}`
- **Value mapping**: `2 = ✅ healthy` (verde), `1 = ⚠️ degraded` (amarelo), `0 = 🔴 down` (vermelho)
- **Colunas adicionais na mesma tabela**:
  - Queue depth: `avg:manta.agent.queue_depth{$env,$segment,$agent} by {agent_id}`
  - p50 latency: `p50:manta.routing.latency{$env,$segment,$agent} by {agent_id}`
- Replica o mockup §6.2 do upgrade doc (`manta-03-s1 | ✅ healthy | queue: 2 | p50: 820ms`)

### 2.2 Timeseries — Queue depth por agente

- **Tipo**: `timeseries`, linha, `by {agent_id}` (top 10 agentes com maior fila)
- **Query**: `avg:manta.agent.queue_depth{$env,$segment,$agent} by {agent_id}`
- **Marker**: linha em `y=5` — acima disso, considerar scaling/tier upgrade (Haiku→Sonnet)

### 2.3 Timeseries — Error rate %

- **Tipo**: `timeseries`, linha
- **Query**: `sum:manta.agent.errors{$env,$segment,$agent}.as_rate() / sum:manta.agent.calls{$env,$segment,$agent}.as_rate() * 100`
- **Group by**: `agent_id` (top 5 por erro)
- **Marker**: `y=5` (5% — limiar de degradação, alinhado ao `error_rate_24h` do schema `agent_health`)

### 2.4 Heatmap — Distribuição de latência por agente

- **Tipo**: `heatmap`
- **Query**: `avg:manta.routing.latency{$env,$segment,$agent} by {agent_id}`
- **Uso**: detectar outliers de latência (cauda longa) que não aparecem em médias/p99 agregados

### 2.5 Query Value — Agentes down agora

- **Tipo**: `query_value`, cor de fundo condicional
- **Query**: `count_nonzero(avg:manta.agent.health.status{$env,$segment} by {agent_id} < 1)`
- **Conditional**: 0 = verde, 1-2 = amarelo, ≥3 = vermelho (dispara revisão imediata)

---

## 3. Seção — Feedback Loop

Grupo de 3 widgets, foco no ciclo de aprendizado do Maestro v2.0 (§2.2, "Learning from feedback").

### 3.1 Query Value — % Feedback positivo

- **Tipo**: `query_value`
- **Query**: `sum:manta.feedback.received{outcome:correct,$env,$segment,$agent}.as_count() / sum:manta.feedback.received{$env,$segment,$agent}.as_count() * 100`
- **Target**: ≥80% (linha de referência, conforme §4.1 do upgrade doc)
- **Conditional formatting**: verde ≥80%, amarelo 70-80%, vermelho <70%

### 3.2 Query Value — % Feedback negativo

- **Tipo**: `query_value`
- **Query**: `sum:manta.feedback.received{outcome:wrong,$env,$segment,$agent}.as_count() / sum:manta.feedback.received{$env,$segment,$agent}.as_count() * 100`
- **Nota**: `outcome:wrong` é o "negativo puro"; `outcome:slow` e `outcome:incomplete`
  aparecem à parte no widget 3.3 para não confundir "errado" com "lento"
- **Target**: <15%

### 3.3 Timeseries — Volume de feedback por outcome

- **Tipo**: `timeseries`, área empilhada (`stacked`)
- **Query**: `sum:manta.feedback.received{$env,$segment,$agent} by {outcome}.as_count()`
- **Cores por outcome**: correct=verde, wrong=vermelho, slow=laranja, incomplete=cinza

### 3.4 Query Value / Timeseries — Frequência de reranking

- **Tipo**: `query_value` (contador) + `timeseries` (tendência) lado a lado
- **Query valor absoluto**: `sum:manta.feedback.reranking{$env,$segment,$agent}.as_count()`
- **Query como % do total de rotas**: `sum:manta.feedback.reranking{$env,$segment,$agent}.as_count() / sum:manta.routing.total{$env,$segment,$agent}.as_count() * 100`
- **Uso**: acompanha quantas vezes o bandit (Thompson Sampling / `updatePosterior`,
  §4.2 do upgrade doc) corrigiu o ranking — volume muito baixo pode indicar
  feedback insuficiente; volume muito alto pode indicar roteamento instável

### 3.5 Top List — Agentes mais corrigidos (reranking)

- **Tipo**: `toplist`
- **Query**: `top(sum:manta.feedback.reranking{$env,$segment} by {agent_id}.as_count(), 10, 'sum', 'desc')`
- **Uso**: aponta candidatos a revisão de keywords/expertise no registry (§1.2 do upgrade doc)

---

## 4. Seção — SLA Status

Grupo compacto tipo "scoreboard", 3 SLOs formais (Datadog SLO objects) + 1 resumo visual.

### 4.1 SLO — P99 latência <2s

- **Tipo de widget**: `slo` (Datadog Service Level Objective, tipo `metric`)
- **SLO query (good events / total events)**:
  - Numerador (good): `sum:manta.routing.total{$env,$segment}.as_count()` filtrado onde `manta.routing.latency < 2000ms` — implementar via **monitor-based SLO** alimentado pelo monitor M1 (§6.1), pois SLO tipo `metric` não filtra por percentil diretamente; alternativa: SLO `monitor`-based usando o monitor de latência como fonte
  - Denominador (total): `sum:manta.routing.total{$env,$segment}.as_count()`
- **Target**: 99.5% das janelas de 5 min com p99 <2s, em 30 dias corridos
- **Widget companion**: `query_value` mostrando `p99:manta.routing.latency{$env,$segment}` com threshold visual em 2000ms

### 4.2 SLO — Uptime >99%

- **Tipo**: `slo` (monitor-based, alimentado pelo monitor M3 §6.3)
- **Base**: `avg:manta.agent.uptime_check{$env,$segment} by {agent_id}` — proporção de checks com valor 1
- **Target**: 99% em janela rolante de 30 dias
- **Widget companion**: `query_value` — `avg:manta.agent.uptime_check{$env,$segment} * 100`

### 4.3 SLO — Success rate >95%

- **Tipo**: `slo` (metric-based)
- **Good events**: `sum:manta.routing.total{outcome:success,$env,$segment}.as_count()`
- **Total events**: `sum:manta.routing.total{$env,$segment}.as_count()`
- **Target**: 95% em janela de 7 dias (mais curta que uptime/latência pois é o
  indicador mais sensível a regressões de roteamento)

### 4.4 Free Text + Check Status — Resumo consolidado

- **Tipo**: `group` contendo 3 `check_status` widgets lado a lado, replicando o
  mockup §6.2 do upgrade doc:

```
P99 latency:    [valor ao vivo]  (target: <2s)   [✅/❌]
Uptime:         [valor ao vivo]  (target: >99%)  [✅/❌]
Success rate:   [valor ao vivo]  (target: >95%)  [✅/❌]
```

  - Cada `check_status` referencia o monitor correspondente (M1/M3/M2 — §6)
    via `check` = nome do monitor, de forma que o ícone reflita o estado real
    do monitor (OK/Alert/Warn/No Data), não apenas o valor pontual da métrica

### 4.5 Timeseries — Fallback % (SLA auxiliar)

- **Tipo**: `timeseries`
- **Query**: mesma do widget 1.5, replicada aqui para leitura conjunta com os
  3 SLOs formais (target <5%, conforme §4.1 do upgrade doc)

---

## 5. Seção — Cost & Efficiency

Grupo de 4 widgets. Baseline e metas vindas de `docs/EXECUTIVE-SUMMARY-v5-UPGRADE.md`
("Cost/request v4.2: $0.08 → target v5.0: <$0.05").

### 5.1 Query Value — Tokens médios por request

- **Tipo**: `query_value`
- **Query**: `avg:manta.routing.tokens{$env,$segment,$agent,$model}`
- **Group by**: opcional por `$model` para comparar Haiku vs Sonnet vs Opus

### 5.2 Timeseries — Custo por request (tendência)

- **Tipo**: `timeseries`, linha
- **Query**: `sum:manta.routing.cost_usd{$env,$segment,$agent,$model}.as_count() / sum:manta.routing.total{$env,$segment,$agent,$model}.as_count()`
- **Marker**: linha em `y=0.05` (meta v5.0) e `y=0.08` (baseline v4.2, tracejada,
  cor neutra) para visualizar o progresso da redução de custo

### 5.3 Top List — Custo acumulado por agente

- **Tipo**: `toplist`
- **Query**: `top(sum:manta.routing.cost_usd{$env,$segment,$model} by {agent_id}.as_count(), 10, 'sum', 'desc')`
- **Uso**: identifica quais agentes/segmentos concentram gasto — insumo para
  decisões de tiering dinâmico (Haiku→Sonnet→Opus, §Fase 3 do upgrade doc)

### 5.4 Timeseries — Distribuição de chamadas por tier de modelo

- **Tipo**: `timeseries`, área empilhada 100%
- **Query**: `sum:manta.routing.total{$env,$segment} by {model}.as_count()`
- **Uso**: acompanha se o dynamic tier routing está de fato empurrando volume
  para Haiku (mais barato) quando a confiança permite, sem sacrificar success rate

### 5.5 Query Value — Custo total do dia vs. budget

- **Tipo**: `query_value`
- **Query**: `sum:manta.routing.cost_usd{$env,$segment}.as_count()` (rollup diário)
- **Conditional formatting**: comparar contra budget diário configurado (ex.:
  budget = `throughput_esperado × $0.05`) — se não houver widget de budget
  nativo, usar `query_value` com "comparação" habilitada contra o mesmo período
  do dia anterior

---

## 6. Alertas (Monitors)

Três monitors obrigatórios pedidos, mais 1 monitor composto de suporte (não
obrigatório, mas recomendado para reduzir ruído de notificação).

### 6.1 Monitor M1 — P99 routing latency > 2s

```yaml
name: "[Manta Maestro v5.0] P99 routing latency > 2s"
type: metric alert
query: "p99(last_5m):p99:manta.routing.latency{env:prod} > 2000"
message: |
  {{#is_alert}}
  🔴 P99 de latência de roteamento do Maestro acima do SLA (2s).
  Valor atual: {{value}}ms. Segmento afetado: {{segment.name}}.
  Runbook: verificar queue_depth dos agentes top (widget 2.2) e status
  de heartbeat (widget 2.1) antes de escalar tier de modelo.
  {{/is_alert}}
  {{#is_recovery}}
  ✅ P99 de latência voltou a ficar abaixo de 2s.
  {{/is_recovery}}
  @slack-manta-maestro-alerts @pagerduty-manta-oncall
options:
  thresholds:
    critical: 2000
    warning: 1600
  evaluation_delay: 60
  notify_no_data: true
  no_data_timeframe: 10
  renotify_interval: 30
tags:
  - "service:manta-maestro"
  - "team:maestro-arch"
  - "version:v5.0"
```

### 6.2 Monitor M2 — Routing success rate < 95%

```yaml
name: "[Manta Maestro v5.0] Routing success rate < 95%"
type: metric alert
query: >
  sum(last_15m):sum:manta.routing.total{outcome:success,env:prod}.as_count() /
  sum(last_15m):sum:manta.routing.total{env:prod}.as_count() * 100 < 95
message: |
  {{#is_alert}}
  🔴 Taxa de sucesso de roteamento abaixo de 95% nos últimos 15min
  ({{value}}%). Verificar top agents por erro (widget 2.3) e volume de
  fallback (widget 1.5) — possível regressão de keywords/ranking.
  {{/is_alert}}
  @slack-manta-maestro-alerts @pagerduty-manta-oncall
options:
  thresholds:
    critical: 95
    warning: 97
  evaluation_delay: 60
  notify_no_data: true
  no_data_timeframe: 15
  renotify_interval: 30
tags:
  - "service:manta-maestro"
  - "team:maestro-arch"
  - "version:v5.0"
```

### 6.3 Monitor M3 — Uptime < 99%

```yaml
name: "[Manta Maestro v5.0] Agent uptime < 99%"
type: metric alert
query: >
  avg(last_1h):avg:manta.agent.uptime_check{env:prod} by {agent_id} < 0.99
message: |
  {{#is_alert}}
  🔴 Uptime do agente {{agent_id.name}} caiu abaixo de 99% na última hora.
  Verificar heartbeat e queue_depth (widget 2.1). Se persistir, acionar
  fallback manual e abrir incidente.
  {{/is_alert}}
  {{#is_recovery}}
  ✅ Agente {{agent_id.name}} voltou a reportar uptime ≥99%.
  {{/is_recovery}}
  @slack-manta-maestro-alerts @pagerduty-manta-oncall
options:
  thresholds:
    critical: 0.99
    warning: 0.995
  evaluation_delay: 60
  notify_no_data: true
  no_data_timeframe: 20
  renotify_interval: 60
  new_group_delay: 300
tags:
  - "service:manta-maestro"
  - "team:maestro-arch"
  - "version:v5.0"
```

### 6.4 Monitor composto (recomendado) — Violação múltipla de SLA

```yaml
name: "[Manta Maestro v5.0] SLA em risco — múltiplos indicadores"
type: composite
query: "{M1} || ({M2} && {M3})"
message: |
  ⚠️ Mais de um indicador de SLA violado simultaneamente. Provável
  incidente sistêmico (não pontual de um agente). Escalar para
  Maestro architect + DevOps on-call imediatamente.
  @slack-manta-maestro-incidents @pagerduty-manta-oncall-p1
tags:
  - "service:manta-maestro"
  - "severity:p1"
```

> Substituir `{M1}`, `{M2}`, `{M3}` pelos IDs reais dos monitors 6.1-6.3 após
> criação no Datadog.

### 6.5 Canais de notificação

| Canal | Uso |
|---|---|
| `@slack-manta-maestro-alerts` | Warnings e alerts individuais (M1, M2, M3) |
| `@pagerduty-manta-oncall` | Alerts críticos com impacto de SLA |
| `@slack-manta-maestro-incidents` + `@pagerduty-manta-oncall-p1` | Monitor composto (6.4), tratado como incidente P1 |
| Email semanal (digest) | Resumo dos 6 widgets de SLA (§4) para revisão trimestral (§4.2 do upgrade doc) |

---

## 7. Notas de implementação

1. **Dependência bloqueante**: os widgets deste dashboard só populam dados reais
   após a Fase 1 do upgrade (`agents`, `agent_health`, `routing_events`,
   `routing_feedback` em Supabase + exporter OTel→Datadog ativo — ver
   `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` §3 Fase 1 e §4.3).
2. **Custo (Seção 5)** depende de uma etapa de precificação por tier de modelo
   que converta `tokens_used` em `cost_usd` antes do submit à métrica
   `manta.routing.cost_usd` — não fazer essa conta em query-time no Datadog
   (percentis de custo não são lineares em tokens quando há mistura de tiers).
3. **Taxonomia de tags**: usar exclusivamente os IDs canônicos v5.0.1
   (`A1`-`A10`, `S1`-`S11`) nas tags `agent_id`/`segment`. Enquanto a
   reconciliação com a produção (`03-S*`/`M*`) não fechar, mapear na camada de
   submit — nunca no dashboard.
4. **KE-068 (barragens)**: erro factual documentado e não corrigido no RAG de
   S11-barragens (skill `manta-maestro` v5.0.1, §9.3.21). Não afeta métricas de
   observabilidade, mas se `manta.feedback.received{outcome:wrong}` mostrar pico
   concentrado em `agent_id:S11`, este é o suspeito primário antes de abrir
   investigação nova.
5. **Revisão trimestral**: os dados deste dashboard alimentam a cadência de
   revisão descrita em §4.2 do upgrade doc (Maestro architect + PM, 1x/trimestre).
