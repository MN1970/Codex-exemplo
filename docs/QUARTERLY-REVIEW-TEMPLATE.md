# Manta Maestro — Quarterly Review Template

**Processo**: Revisão trimestral do roteamento e do catálogo de agentes
**Cadência**: 1x/trimestre
**Duração**: 2 horas
**Participantes obrigatórios**: Maestro architect (Manta 16) + PM
**Participantes opcionais**: DevOps/RAG owner (se houver decisão de
schema/infra), owner do agente em discussão
**Ticket de origem do processo**: MNT-2026-ECOSYSTEM-UPGRADE-V5 (roadmap
Fase 4.2 — ver `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`)
**Queries companheiras**: `supabase/analytics/quarterly_review_kpis.sql`

Copie este arquivo para `docs/reviews/YYYY-QN-quarterly-review.md` no
início de cada ciclo e preencha os campos entre `[ ]`.

---

## 0. Metadados da review

| Campo | Valor |
|---|---|
| Trimestre analisado | `[ex.: 2026-Q3 (2026-05-01 a 2026-08-01)]` |
| Data da reunião | `[YYYY-MM-DD]` |
| Facilitador (Maestro architect) | `[nome]` |
| PM presente | `[nome]` |
| Versão do CLAUDE.md no início do período | `[ex.: v4.2]` |
| Versão do CLAUDE.md ao fim do período | `[ex.: v4.3]` |
| Nº de agentes ativos no período | `[ex.: 20]` |

### Pré-requisito de dados (bloqueante)

Status conhecido em 2026-08-02 (atualizar a cada ciclo):

- [ ] Migração `supabase/migrations/2026_08_02_routing_observability.sql`
      aplicada em produção (cria `routing_events`, `routing_feedback`,
      `agent_posteriors` — hoje só existem localmente via
      `feedback_loop.py` + SQLite; o adaptador Supabase é um stub não
      implementado). **Sem isso não há dado nenhum para as Seções 1-4.**
- [ ] Maestro instrumentado para logar `latency_ms` e `tokens_used` em
      cada `routing_events` (nenhum dos dois é gravado hoje — ver
      cabeçalho da migração acima). Sem isso, a métrica de cost/request
      (Seção 5) só roda em modo "estimativa estática", não custo real.
- [ ] Conflito de schema `agent_health` resolvido: há duas definições
      incompatíveis (`2026_08_02_agent_health_heartbeat.sql` — estado
      atual, 1 linha/agente, é a que o serviço real
      `services/heartbeat/heartbeat-service.js` escreve — vs.
      `2026_08_02_agent_auto_registration.sql` — série temporal). Como
      ambas usam `CREATE TABLE IF NOT EXISTS agent_health`, só a
      primeira a rodar existe de fato; a outra migração fica um no-op
      silencioso. Enquanto não resolvido, uptime é só snapshot atual,
      não trend do trimestre.
- [ ] `routing_events`/`routing_feedback` populados para **todo** o
      período analisado (não só a partir de quando a migração acima
      foi aplicada).

Se **qualquer item acima estiver em aberto**: esta review vira uma
reunião de "gate de instrumentação" — rodar só o que as queries de
`quarterly_review_kpis.sql` conseguem entregar hoje (marcado inline no
próprio arquivo SQL como disponível/indisponível), registrar o restante
como pendência na Seção 6 (Decisões), e escalar prazo do que falta.

---

## 1. Agenda (2 horas)

| Bloco | Duração | Conteúdo |
|---|---|---|
| 1 | 10 min | Abertura — recapitular decisões da review anterior, status das ações pendentes |
| 2 | 25 min | Routing Analysis — regra mais usada, agente mais requisitado |
| 3 | 25 min | Gap Detection — queries mal roteadas, feedback negativo >100 |
| 4 | 20 min | Trending — segmentos emergentes, composições multi-agente |
| 5 | 25 min | Key Metrics — accuracy, throughput, cost/request vs. metas |
| 6 | 25 min | Recommendations — novo agente? refinar keywords? upgrade de tier? |
| 7 | 10 min | Fechamento — decisões, owners, prazos, próxima review |

---

## 2. Routing Analysis

*Fonte: `quarterly_review_kpis.sql` §1 (queries 1.1–1.3)*

### 2.1 Agente mais requisitado

| Rank | Agente | Rotas no período | % do total | Confiança média | Latência média |
|---|---|---|---|---|---|
| 1 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| 2 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| 3 | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### 2.2 Regra/keyword mais acionada

| Rank | Keyword/regra | Agente-alvo | Vezes acionada |
|---|---|---|---|
| 1 | `[ ]` | `[ ]` | `[ ]` |
| 2 | `[ ]` | `[ ]` | `[ ]` |
| 3 | `[ ]` | `[ ]` | `[ ]` |

### 2.3 Distribuição por eixo (horizontal x vertical)

- Horizontais: `[ ]`% das rotas
- Verticais: `[ ]`% das rotas
- Leitura: `[comentário — ex.: concentração excessiva em 1 eixo indica
  sub ou super-cobertura de segmentos]`

---

## 3. Gap Detection

*Fonte: `quarterly_review_kpis.sql` §2 (queries 2.1–2.3)*
*Critério de gap: **>100 feedback negativo** (`wrong`/`slow`/`incomplete`)
no trimestre para um mesmo agente, OU volume relevante de fallback/baixa
confiança.*

### 3.1 Agentes acima do threshold de feedback negativo

| Agente | Total feedback negativo | Breakdown (wrong/slow/incomplete) | Ação sugerida |
|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |

Se **nenhum agente** cruzou o threshold: registrar explicitamente
"nenhum gap crítico este trimestre" — não deixar em branco.

### 3.2 Fallbacks acionados (troca de agente em runtime)

| Agente original | Agente de fallback | Ocorrências | Causa provável |
|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### 3.3 Rotas de baixa confiança (< 0.60) sem feedback ainda

| Agente | Rotas de baixa confiança | Confiança média | Observação |
|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |

---

## 4. Trending — segmentos emergentes

*Fonte: `quarterly_review_kpis.sql` §3 (queries 3.1–3.3)*

### 4.1 Composição multi-agente (proxy de caso de uso cruzado)

| Mês | Rotas compostas | Total rotas | % composição | Tendência |
|---|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[↑/↓/estável]` |

### 4.2 Combinações de agentes mais frequentes

| Combinação | Estratégia (serial/paralelo) | Ocorrências | Deveria virar handoff formal no CLAUDE.md? |
|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[Sim/Não]` |

### 4.3 Termos frequentes em rotas sem agente claro (candidatos a novo segmento)

| Termo/tema | Ocorrências | Segmento existente cobre? | Candidato a novo agente? |
|---|---|---|---|
| `[ ]` | `[ ]` | `[Sim/Não/Parcial]` | `[Sim/Não]` |

**Pergunta de trigger**: algum termo/tema acima aparece **>100 vezes**
e não é coberto por nenhum dos 20 agentes atuais (S1-S10 + horizontais)?
Se sim → levar para Seção 5 como candidato formal a novo agente.

---

## 5. Key Metrics — vs. metas do roadmap v5.0

*Fonte: `quarterly_review_kpis.sql` §4 (queries 4.1–4.5). Metas de
referência: `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` §8.*

| Métrica | Trimestre anterior | Este trimestre | Meta | Status |
|---|---|---|---|---|
| Routing accuracy (success rate) | `[ ]`% | `[ ]`% | >95% | `[✅/⚠️/❌]` |
| Feedback positivo | `[ ]`% | `[ ]`% | >80% | `[✅/⚠️/❌]` |
| Throughput (rotas/mês, média do trimestre) | `[ ]` | `[ ]` | crescimento vs. trimestre anterior | `[✅/⚠️/❌]` |
| Crescimento de throughput (MoM médio) | — | `[ ]`% | — | `[comentário]` |
| Cost/request médio (USD, ponderado por agente) | `[ ]` | `[ ]` | tendência de queda ou estável | `[✅/⚠️/❌]` |
| P50 / P99 latência | `[ ]` / `[ ]` ms | `[ ]` / `[ ]` ms | <1s / <2-3s | `[✅/⚠️/❌]` |
| Fallback triggered % | `[ ]`% | `[ ]`% | <5% | `[✅/⚠️/❌]` |
| % composição multi-agente | `[ ]`% | `[ ]`% | 5-10% (v5.0) | `[✅/⚠️/❌]` |
| Uptime médio dos agentes | `[ ]`% | `[ ]`% | >99% | `[✅/⚠️/❌]` |

### 5.1 Cost/request por agente (top 5 por volume)

| Agente | Modelo | Rotas | Tokens médios/rota | Custo estimado/rota (USD) |
|---|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

> Nota: preços por 1k tokens na query são placeholders — atualizar
> conforme tabela de pricing vigente do modelo antes de reportar valor
> absoluto de custo à liderança.

---

## 6. Recommendations

*Fonte: `quarterly_review_kpis.sql` §5 (queries 5.1–5.3), cruzado com
julgamento qualitativo dos participantes.*

### 6.1 Novo agente necessário?

| Candidato a segmento | Evidência (volume/termos) | Decisão | Owner | Prazo |
|---|---|---|---|---|
| `[ ]` | `[ ]` | `[Criar / Aguardar mais dados / Rejeitar]` | `[ ]` | `[ ]` |

### 6.2 Refinar keywords de routing?

| Agente | Keyword a ajustar | Ajuste (adicionar/remover/reponderar) | Owner | Prazo |
|---|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### 6.3 Upgrade/downgrade de tier (Haiku/Sonnet/Opus)?

| Agente | Tier atual | Tier proposto | Justificativa | Owner | Prazo |
|---|---|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### 6.4 Outras ações (infra, RAG, SharePoint, handoffs)

| Ação | Motivo | Owner | Prazo |
|---|---|---|---|
| `[ ]` | `[ ]` | `[ ]` | `[ ]` |

---

## 7. Decisões e itens de ação (fechamento)

| # | Decisão/Ação | Owner | Prazo | Status |
|---|---|---|---|---|
| 1 | `[ ]` | `[ ]` | `[ ]` | `[Aberto/Em andamento/Concluído]` |
| 2 | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

### Gate humano

- [ ] Aprovação MN registrada para mudanças em CLAUDE.md (nova versão)
- [ ] Aprovação MN registrada para novo agente (se aplicável)
- [ ] Ticket(s) aberto(s) para cada ação da Seção 7

### Próxima review

- Data prevista: `[YYYY-MM-DD, +1 trimestre]`
- Pendências herdadas para a próxima pauta: `[ ]`

---

## Apêndice A — Índice de queries SQL

Todas em `supabase/analytics/quarterly_review_kpis.sql`, parametrizadas
por `:'period_start'` / `:'period_end'`:

| Seção do template | Query(ies) | O que responde |
|---|---|---|
| 2.1 | §1, query 1.1 | Agente mais requisitado, share, confiança, latência |
| 2.2 | §1, query 1.2 | Keyword/regra mais acionada (requer `matched_keyword`) |
| 2.3 | §1, query 1.3 | Distribuição horizontal x vertical |
| 3.1 | §2, query 2.1 | Agentes acima do threshold de feedback negativo (>100) |
| 3.2 | §2, query 2.2 | Fallbacks acionados |
| 3.3 | §2, query 2.3 | Rotas de baixa confiança |
| 4.1 | §3, query 3.1 | % composição multi-agente por mês |
| 4.2 | §3, query 3.2 | Combinações de agentes mais frequentes |
| 4.3 | §3, query 3.3 | Termos frequentes em rotas sem agente claro |
| 5 (tabela geral) | §4, queries 4.1–4.4 | Accuracy trend, throughput, latência, SLA |
| 5.1 | §4, query 4.3 | Cost/request por agente |
| — | §4, query 4.5 | Uptime aproximado por agente (agent_health) |
| 6.1 | §5, query 5.1 | Candidatos a novo agente (alto volume + baixa confiança) |
| 6.2 | §5, query 5.3 | Candidatos a refinar keywords (confiante mas errado) |
| 6.3 | §5, query 5.2 | Candidatos a upgrade de tier (volume alto + success baixo) |

## Apêndice B — Critérios de decisão (referência rápida)

- **Novo agente**: `>= 100` rotas/trimestre com confiança `< 0.60` e
  concentradas em um tema/termo não coberto por segmento existente.
- **Refinar keywords**: `> 20` feedbacks negativos com confiança
  `>= 0.75` no momento do roteamento (Maestro "roteou confiante, errou").
- **Upgrade de tier**: `>= 50` rotas/trimestre com success rate `< 90%`
  no tier atual.
- **Gap crítico (ação obrigatória antes da próxima review)**: qualquer
  agente com `> 100` feedback negativo no trimestre.
