# ARQUITETURA-AGENTES-IA.md

**Sistema Manta Maestro — Arquitetura de Agentes IA**

- **Versão**: 3.0.0 (trilha repo Codex-exemplo)
- **Data**: 2026-07-19
- **Autor**: Manta Associados
- **Substitui**: v2.0.0 (2026-07-05 expansão S6–S10), v1.0.0 (2026-06-24)
- **Ticket**: MNT-2026-UPGRADE-LEARNING-LOOP-v4.9
- **Sprint aplicado**: v4.9 — Fechar loop de aprendizado (2026-07-19)

> ⚠️ **Nota sobre trilhas paralelas de arquitetura (2026-07-29).** O
> SharePoint operacional (`04_IA/Manta-Maestro/00-arquitetura/`) mantém
> uma **trilha própria** com versões
> `ARQUITETURA-AGENTES-IA-v5.0.0.md` (2026-07-22) e
> `ARQUITETURA-AGENTES-IA-v5.1.0.md` (2026-07-28), focadas na
> **KB dispositivos rodoviários** (12 módulos, 221 registros, 5 tabelas
> em Supabase project `xgluoaaymbdzbbudnwrh`). Essa trilha NÃO passou
> pelo repo `MN1970/Codex-exemplo`. A trilha do repo (este documento,
> v3.0.0) foca em **Learning Loop Fechado + Agentic Intelligence Layer**
> em Supabase project `ogxxgvgtulrbbppshjie`. As duas trilhas rodam
> lado a lado em Supabase projects distintos e cobrem escopos
> diferentes. **Reconciliação em curso**: v5.2.0 no SP consolida ambas
> em uma tabela única de features + esclarecimento dos 2 projects
> Supabase e sua propriedade. Ver `ARQUITETURA-AGENTES-IA-v5.2.0.md`
> no SP quando publicada.

## Sumário

- [1. Visão geral](#1-visão-geral)
- [2. 3 eixos do sistema](#2-3-eixos-do-sistema)
- [3. 5 camadas da arquitetura](#3-5-camadas-da-arquitetura)
- [4. Hub-and-spoke](#4-hub-and-spoke)
- [5. Model tiering](#5-model-tiering)
- [6. Routing do Maestro](#6-routing-do-maestro-manta-00)
- [7. Knowledge Engine (RAG)](#7-knowledge-engine-rag)
- [8. SharePoint routing](#8-sharepoint-routing)
- [9. Diagrama de fluxo](#9-diagrama-de-fluxo-agente-vertical)
- [10. Changelog v1→v2→v3](#10-changelog-v10--v20--v30)
- [11. Referências](#11-referências)

---

## 1. Visão geral

O **Manta Maestro** é o sistema de agentes IA da Manta Associados —
20 agentes especializados em engenharia de infraestrutura, cobrindo do
estudo prévio ao descomissionamento, organizados em um **hub-and-spoke**
com um router central (Manta 00, o Maestro).

A v2.0.0 (2026-07-05) promoveu os 5 agentes verticais **S6–S10** (Portos,
Aeroportos, Saneamento, Energia, Barragens) de "novos" para **operacional**,
completando a cobertura de 10 segmentos de infraestrutura.

A **v3.0.0 (2026-07-19)** adiciona as camadas **Agentic Intelligence
Layer** (v4.7) e **Learning Loop Fechado** (v4.9) sobre a arquitetura
hub-and-spoke. As entregas principais:

- **v4.7 Agentic Intelligence Layer** (2026-07-13) — Reflexion Loop pré-
  entrega, Memória Episódica (`agent_episodes` + HNSW 384d), P2 Prompt
  Contract padronizado, Loop Primitives (sequential/parallel/race DAG),
  Model Tiering explícito com `maestro_cost_log`, SkillForge auto-geração.
- **v4.9 Learning Loop Fechado** (2026-07-19, APLICADO EM PROD) —
  Trigger `trg_judge_flag_to_backlog` promove automaticamente respostas
  com `judge_score < 3` para tickets `AKP-JF` em `akp_curation_backlog`.
  `promote_gaps_to_backlog(INT, FLOAT, INT)` estendida com branch
  `judge_pattern` (agrega padrões crônicos por agente/segmento em 30d).
  View `v_judge_feedback_health` com `security_invoker` alimenta tier
  promotion, prompt refinement, Reflexion Loop e SkillForge.

**Estado prod (Supabase project ogxxgvgtulrbbppshjie):** infraestrutura
completa aplicada, sequences race-safe, UNIQUE INDEXes parciais para
dedup, RLS + grants mínimos (só `service_role` executa a trigger fn),
smoke test passou (AKP-JF-00001 criado com priority=1 para score=0,
idempotência OK).

## 2. 3 eixos do sistema

O sistema é ortogonal em 3 dimensões — cada consulta se posiciona na
interseção das três:

### Eixo 1 — Horizontais (11 agentes transversais)

Aplicam-se a qualquer segmento. Cada horizontal responde por uma
disciplina não-técnica ou meta-função.

| Código | Agente | Aliases | Tier |
|---|---|---|---|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet |
| Manta 01 | claims | 02-C, manta-claims | Opus |
| Manta 02 | contratual | manta-02, contratual | Sonnet |
| Manta 04 | imobiliario | manta-04 | Sonnet |
| Manta 05 | orcamento | manta-05 | Sonnet |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus |
| Manta 07 | cronograma | manta-07 | Sonnet |
| Manta 13 | bd (business dev) | manta-13, business-dev | Sonnet |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus |

### Eixo 2 — Verticais por segmento (9 agentes operacionais)

Cada vertical concentra vocabulário, normas, cálculos e handoffs de
um segmento específico. **v2.0.0**: S6–S10 promovidos a operacional.

| Código | Segmento | Agente | Status v2.0.0 |
|---|---|---|---|
| 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial |
| **03-S6** | **Portos** | agente-portos | 🆕 **v2.0.0 Operacional** |
| **03-S7** | **Aeroportos** | agente-aeroportos | 🆕 **v2.0.0 Operacional** |
| **03-S8** | **Saneamento** | agente-saneamento | 🆕 **v2.0.0 Operacional — prioridade AySA** |
| **03-S9** | **Energia** | agente-energia | 🆕 **v2.0.0 Operacional — ANEEL/State Grid** |
| **03-S10** | **Barragens** | agente-barragens | 🆕 **v2.0.0 Operacional** |

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais suportam as 8 fases via Q2 do intake:

1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

## 3. 5 camadas da arquitetura

```
┌────────────────────────────────────────────────────────────┐
│ C5 — Apresentação                                          │
│      artefatos React, memoriais DOCX, dashboards, PPTX     │
├────────────────────────────────────────────────────────────┤
│ C4 — Orquestração                                          │
│      Maestro (Manta 00) — router; sessões; handoffs        │
├────────────────────────────────────────────────────────────┤
│ C3 — Agentes verticais (por segmento)                      │
│      Manta 03-S1..S10 (Rodovias..Barragens)                │
├────────────────────────────────────────────────────────────┤
│ C2 — Agentes horizontais (transversais)                    │
│      Manta 01/02/04-07/13-16 (claims, contratual, orçamento│
│      modelagem, cronograma, BD, PPT, advisory, arquiteto)  │
├────────────────────────────────────────────────────────────┤
│ C1 — Skills reutilizáveis                                  │
│      SKILL.md registrados no catálogo, invocáveis por      │
│      qualquer agente. Ex.: aluci-guard, consist-guard,     │
│      padrao-manta, mk-manta, cad-quantifier.               │
├────────────────────────────────────────────────────────────┤
│ C0 — Dados                                                 │
│      Supabase (RAG chunks + routing tables), SharePoint    │
│      (projetos, SKILL.md, ARQUITETURA), storage por agente │
└────────────────────────────────────────────────────────────┘
```

## 4. Hub-and-spoke

Princípio de operação:

- **Maestro (C4) decide QUEM.** Recebe a consulta, aplica routing
  rules (palavras-chave + escala Q1-Q4 do intake) e despacha para 1
  ou mais agentes de C2/C3.
- **Agente (C2/C3) decide CONTEÚDO.** Aplica conhecimento de domínio,
  interpreta o problema, define artefato, escolhe skills.
- **Skill (C1) EXECUTA.** Função pura: recebe entrada, produz saída.
  Sem estado próprio.

Handoffs entre agentes são declarativos: cada SKILL.md declara "quando
X aparecer, encaminhe para Y" — o Maestro é notificado e faz o
handoff sem passar pelo cliente.

## 5. Model tiering

| Tier | Modelo | Uso típico | % de chamadas |
|---|---|---|---|
| Triagem | Claude Haiku 4.5 | Routing, intake, extração de metadados | ~20% |
| Execução | Claude Sonnet 4.6 | Análise técnica, redação, orçamento, cronograma | ~70% |
| Complexo | Claude Opus 4.7/4.8 | Claims complexos, arquitetura, second opinion crítico | ~10% |

O Maestro faz **routing dinâmico de tier** dentro de uma sessão:
começa em Haiku para triagem, escala para Sonnet ao entrar no agente
vertical, e escala novamente para Opus se detectar complexidade
(claim + jurídico + técnico + financeiro no mesmo pleito).

## 6. Routing do Maestro (Manta 00)

Regra de dispatch Q1 (segmento):

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S8)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S9)

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S6)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S7)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → agente-barragens (S10)

# Regras existentes S1-S4 mantidas sem alteração
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4
```

**Casos ambíguos** (múltiplas regras aplicáveis):
- UHE (barragem + LT + SE) → dispatch primário `agente-barragens`
  + handoff a `agente-energia`.
- ETE + subestação → dispatch primário `agente-saneamento` + handoff
  a `agente-energia`.
- Porto + pista de carga → dispatch primário `agente-portos` +
  handoff a `agente-aeroportos`.
- Ver `tests/routing/prompts.md` no repo `Codex-exemplo` para lista
  atualizada de casos ambíguos e política.

## 7. Knowledge Engine (RAG)

Cada vertical carrega uma coleção RAG dedicada em Supabase, com
prefixo de storage único:

| Coleção | Prefixo | Fontes iniciais | Status |
|---|---|---|---|
| rodovias | rod: | DNIT, SICRO, NBR-DNIT | ✅ Operacional |
| oae | oae: | NBR 7187, 6118, 6122, PRL/RioSP | ✅ Operacional |
| ferrovia | fer: | AREMA, DNIT ferroviário, concessionárias | ✅ Operacional |
| metro | mtr: | ABNT NBR-NM, ARTESP, manual STM | ✅ Operacional |
| **portos** | **por:** | ANTAQ, PIANC, ROM, editais BNDES | 🆕 **v2.0.0** |
| **aeroportos** | **aer:** | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 **v2.0.0** |
| **saneamento** | **san:** | SNIS, IWA, NBR 12211-12218, Lei 14.026, ERAS/AySA | 🆕 **v2.0.0** |
| **energia** | **ene:** | ANEEL editais, R1-R5 EPE, ONS, IEEE, IEC | 🆕 **v2.0.0** |
| **barragens** | **bar:** | ICOLD, CBDB, SIGBM, Lei 12.334, PNSB | 🆕 **v2.0.0** |

Sub-prefixos de contexto:
- `san:br:` / `san:ar:` — saneamento por país (Brasil × Argentina AySA).
- `ene:t:` / `ene:d:` / `ene:g:` — energia por segmento (transmissão × distribuição × geração).
- `bar:c:` / `bar:t:` / `bar:e:` / `bar:r:` — barragens por tipologia
  (concreto × terra × enrocamento × rejeitos).

Migração canônica: `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`
no repo `Codex-exemplo`.

## 8. SharePoint routing

Tabela `sp_agent_routing` mapeia cada agente para uma pasta canônica:

| Agente | Pasta SP | Padrões |
|---|---|---|
| agente-infraestrutura S1 | `03_Projetos/Rodovias/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-infraestrutura S2 | `03_Projetos/OAE/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-infraestrutura S3 | `03_Projetos/Ferrovia/*` | `*.pdf, *.dwg, *.xlsx` |
| agente-infraestrutura S4 | `03_Projetos/Metro/*` | `*.pdf, *.dwg, *.xlsx` |
| **agente-portos** | **`03_Projetos/Portos/*`** | `*.pdf, *.dwg, *.xlsx` |
| **agente-aeroportos** | **`03_Projetos/Aeroportos/*`** | `*.pdf, *.dwg, *.xlsx` |
| **agente-saneamento** | **`03_Projetos/Saneamento/*`** | `*.pdf, *.dwg, *.xlsx` |
| **agente-energia** | **`03_Projetos/Energia/*`** | `*.pdf, *.dwg, *.xlsx` |
| **agente-barragens** | **`03_Projetos/Barragens/*`** | `*.pdf, *.dwg, *.xlsx` |

Cada agente vertical também tem sua pasta SKILL em
`01-agentes-fundamentais/agente-<slug>/` contendo:
- `SKILL.md` — definição canônica (frontmatter + intake + arquitetura).
- `README.md` — visão geral e onboarding.
- `refs/` — documentos técnicos de referência.
- `prompts/` — prompts amostrais e conversation starters.

## 9. Diagrama de fluxo — agente vertical

```
Usuário ─────► Maestro (Manta 00)
                   │
                   │ 1. Triagem (Haiku): identifica segmento (Q1),
                   │    fase (Q2), objetivo (Q3), formato dados (Q4)
                   ▼
              Agente vertical (ex.: agente-saneamento)
                   │
                   │ 2. Ativa vertentes V1-V5 do SKILL.md
                   │    (Análise, Inteligência, Obra, DocIntel, Disciplinas)
                   │
                   │ 3. Consulta RAG por prefixo (ex.: san:*, san:ar:*)
                   │
                   │ 4. Invoca skills (C1): aluci-guard, consist-guard,
                   │    cad-quantifier, padrao-manta, etc.
                   │
                   │ 5. Decide handoffs (agente-05 para orçamento,
                   │    agente-07 para cronograma, agente-contratual
                   │    para claim, etc.)
                   ▼
              Artefato (C5): React app + memorial DOCX
                   │
                   ▼
              Usuário ← resposta com fontes, quantitativos, risco
```

## 10. Changelog v1.0 → v2.0 → v3.0

### v3.0.0 (2026-07-19) — Learning Loop Fechado + Agentic Intelligence

#### Adicionado (v4.7 Agentic Intelligence, sobreposto em v4.6.1)

- **Reflexion Loop pré-entrega** (`maestro_reflexion.py`): output → aluci-guard
  → consist-guard → autocrítica + lição em `agent_episodes` → refina (max 3
  iterações). Só em tier `star2`/`star3` (30-100% custo extra); `star1`
  permanece single-shot.
- **Memória episódica** — tabela `agent_episodes` + `v_high_quality_episodes`
  + índice HNSW 384d. Cada execução de sub-agente registra `task_id`,
  `p2_contract`, `tools_used`, `outcome`, `custos`.
- **P2 Prompt Contract** — 4 elementos obrigatórios em delegação a
  sub-agentes: `objective`, `output_format`, `tools_and_sources`,
  `boundaries`. System prompt dedicado + brief estruturado.
- **Loop Primitives** (`manta_shared/loop_primitives.py`): sequential,
  parallel, race. Maestro emite DAG de execução usando os 3 primitives.
- **Model Tiering explícito** — campo `tier_policy` em cada SKILL.md
  (`haiku_for/sonnet_for/opus_for`) + enforcement no dispatcher.
  `maestro_cost_log` registra custos por execução.
- **SkillForge** — pipeline em `sharepoint/03-skills-forjadas/` gera
  skills automaticamente de padrões em `agent_episodes` (cron 03:00 UTC
  + gate humano MN via `skillforge_pending_review`).

#### Adicionado (v4.9 Learning Loop Fechado, aplicado 2026-07-19)

- **Trigger real-time `trg_judge_flag_to_backlog`** em `manta_rag_queries`
  (`AFTER INSERT OR UPDATE OF judge_score` `WHEN judge_score < 3`). Cria
  ticket `AKP-JF-NNNNN` em `akp_curation_backlog` com `priority` escalando
  com severidade (score 0 → priority 1, score 1 → priority 2).
- **`akp_curation_backlog` estendido** com 4 colunas aditivas:
  `ticket_type` ∈ {gap_candidate, judge_flag, judge_pattern}, `agent_slug`,
  `evidence` (JSONB com query_id/trace_id/judge_notes), `priority` (1-5).
- **`promote_gaps_to_backlog(INT, FLOAT, INT)`** — assinatura estendida,
  branch `judge_pattern` agrega ≥N flags/30d por `(agent_slug, segmento)`
  em UM ticket agregado.
- **View `v_judge_feedback_health`** com `security_invoker=true` — saúde
  do juiz LLM por agente/segmento em 30d (8 métricas + `health_status`
  critical/warn/ok/healthy). Alimenta tier promotion, prompt refinement,
  Reflexion Loop, SkillForge.
- **3 sequences race-safe** (`akp_judge_flag_seq`, `akp_judge_pattern_seq`,
  `akp_gap_candidate_seq`) — nunca usa MAX+1.
- **2 UNIQUE INDEXes parciais** — dedup por `query_id` em `judge_flag` +
  dedup por `(agent_slug, segmento)` em `judge_pattern` aberto.
- **RLS + hardening** — REVOKE de grants excessivos em view e função,
  só `service_role` (+ `postgres` owner) executa a trigger function.
  `authenticated` mantém SELECT na view; `anon` sem acesso.

#### Mudado (v4.9)

- **v_akp_judge_health** (v4.6) marcado com `COMMENT ON VIEW`: "superseded
  by v_judge_feedback_health em v4.9. Mantida por compat com dashboards
  legados. Deprecar em v5.0 se 90d sem consumer."
- **Cron `akp-daily-cron.yml`** — body do RPC atualizado da assinatura
  antiga `max_top_sim` para a nova `max_avg_hits` + `min_judge_flags`.

#### Mantido (sem alteração)

- Estrutura de 5 camadas (C0-C5).
- Hub-and-spoke com Manta 00 (Maestro) no centro.
- Model tiering (Haiku → Sonnet → Opus).
- Todos os agentes horizontais + verticais S1-S13.
- Coleções RAG existentes (`saneamento`, `energia`, `portos`, `aeroportos`,
  `barragens`, `academic-knowledge`, `tuneis`, `mineracao`, `oleo-gas`,
  `edificacoes`, `mcs:` Manta Cases).

---

## 10. Changelog v1.0 → v2.0

### Adicionado
- 5 agentes verticais operacionais: **agente-portos** (S6),
  **agente-aeroportos** (S7), **agente-saneamento** (S8),
  **agente-energia** (S9), **agente-barragens** (S10).
- 5 coleções RAG (`por:`/`aer:`/`san:`/`ene:`/`bar:`) com sub-prefixos.
- 5 regras de routing do Maestro para os novos segmentos.
- 5 pastas SP em `03_Projetos/{Saneamento,Energia,Portos,Aeroportos,Barragens}/`.
- 5 pastas SP em `01-agentes-fundamentais/agente-{portos,aeroportos,
  saneamento,energia,barragens}/` com SKILL.md canônico.
- Migração Supabase idempotente + prompts de teste do routing +
  runbook manual de deploy — todos versionados no repo `MN1970/Codex-exemplo`.

### Mudado
- Total de agentes: 15 → **20**.
- Cobertura de segmentos verticais: 4 completos (+1 parcial) → **9 completos** (+1 parcial).
- S6-S10 promovidos de "novos" (v1.0.0) para "operacional" (v2.0.0).

### Mantido (sem alteração)
- Estrutura de 5 camadas (C0-C5).
- Model tiering (Haiku → Sonnet → Opus).
- Padrão hub-and-spoke.
- Todos os agentes horizontais (Manta 00/01/02/04-07/13-16).
- Todos os agentes verticais S1-S5.

## 11. Referências

- **Repositório mestre**: `MN1970/Codex-exemplo` (branch/PR:
  `claude/manta-agents-s6-s10-7qklcw`).
- **Mirror operacional**: `viniciusmagnos/manta-hub` (mesma branch,
  PR #3).
- **Registro completo dos 20 agentes**: `CLAUDE.md` no repo mestre.
- **Definições canônicas dos verticais**: `.claude/agents/*.md` no repo mestre.
- **SKILL.md em SP**: `Documentos Compartilhados/04_IA/Manta-Maestro/
  01-agentes-fundamentais/agente-*/SKILL.md`.
- **Coleções RAG**: Supabase (aguardando aplicação da migração v4.2).
- **Rotas SP**: tabela `sp_agent_routing` (aguardando insert v4.2).
- **Runbook de deploy**: `docs/DEPLOY-v4.2.md` no repo mestre.
- **Prompts de teste do routing**: `tests/routing/prompts.md` no repo mestre.

---

_Documento vivo. Alterações via pull request no repo `MN1970/Codex-exemplo`,
aprovação MN, e re-upload aqui no SharePoint como nova versão._
