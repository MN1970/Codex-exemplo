# ARQUITETURA-AGENTES-IA v5.2.0

**Manta Maestro** — Sistema de Agentes IA da Manta Associados

**Versao:** 5.2.0 (2026-07-29)
**Status:** Operacional (consolidacao trilhas paralelas)
**Substitui:** v5.1.0 (2026-07-28 KB rodovias) + v3.0.0 repo Codex-exemplo
(2026-07-19 Learning Loop v4.9)
**Mantido por:** mneves@mantaassociados.com

---

## Sumario Executivo

A v5.2.0 **reconcilia** as duas trilhas de arquitetura que evoluiram em
paralelo entre 2026-07-13 e 2026-07-28:

| Trilha            | Onde ficou              | Ultima versao        | Foco principal                          |
|-------------------|-------------------------|----------------------|-----------------------------------------|
| **SP-native**     | `04_IA/Manta-Maestro/`  | v5.1.0 (2026-07-28)  | KB dispositivos rodoviarios (S1)        |
| **Repo Codex**    | `MN1970/Codex-exemplo`  | v3.0.0 (2026-07-19)  | Learning Loop + Agentic Intelligence    |

Ambas continuam validas — sao camadas diferentes do mesmo Maestro:

- **KB rodovias** (v5.1.0) — camada de conhecimento estruturado especifica
  ao agente vertical S1 (rodovias). 5 tabelas Supabase no project
  `xgluoaaymbdzbbudnwrh` (us-east-2).
- **Learning Loop** (v4.9) — camada horizontal de feedback e autocorrecao
  do juiz LLM sobre todos os agentes. Trigger + view + funcoes em Supabase
  project `ogxxgvgtulrbbppshjie` (sa-east-1).

Este documento consolida ambas em uma tabela unica de features + esclarece
propriedade dos 2 projects Supabase + define politica de propriedade de
mudancas futuras (SP-native vs repo Codex).

---

## 1. ARQUITETURA CONSOLIDADA — 20 AGENTES + LEARNING LOOP + KB ESTRUTURADA

### 1.1 Tres eixos de organizacao (inalterado desde v5.0)

- **Eixo 1** — Agentes horizontais (11): maestro, claims, contratual,
  imobiliario, orcamento, modelagem, cronograma, BD, apresentacoes,
  advisory, arquiteto-IA
- **Eixo 2** — Agentes verticais (9): S1-S4 (rodovia, OAE, ferrovia,
  metro) + S6-S10 (portos, aeroportos, saneamento, energia, barragens)
- **Eixo 3** — Ciclo de vida (8 fases): estudo previo, projeto basico,
  projeto executivo, obra em execucao, O&M, licitacao, DD, encerramento

### 1.2 Camadas tecnicas (consolidadas v5.2)

| Camada                | Responsabilidade                        | Componentes                                                    |
|-----------------------|-----------------------------------------|----------------------------------------------------------------|
| **Intake**            | Recebimento de requisicoes              | Maestro router, parsing semantico                              |
| **Routing**           | Despacho para agente correto            | Regras pattern-matching + Learned Router (v4.6)                |
| **Agentes**           | Execucao de tarefas especializadas      | 20 agentes (11 horizontais + 9 verticais)                      |
| **RAG tematico**      | Contexto documental                     | 6 colecoes Supabase (san, ene, por, aer, bar, academic)        |
| **KB estruturada S1** | Parametros normativos consultaveis      | 12 modulos rodoviarios em Supabase `xgluoaaymbdzbbudnwrh`      |
| **Agentic Intel.**    | Auto-melhoria pre-entrega               | Reflexion Loop + agent_episodes + P2 Contract (v4.7)           |
| **Learning Loop**     | Feedback juiz LLM -> curadoria          | trg_judge_flag_to_backlog + akp_curation_backlog (v4.9)        |
| **Cost governance**   | Tier + custos por deliverable           | maestro_cost_log + model tiering explicito (v4.7)              |
| **Storage**           | Persistencia e versionamento            | SharePoint + GitHub + 2 projects Supabase                      |

### 1.3 Dois projects Supabase — propriedade clara

| Project ID                    | Regiao      | Escopo                                             | Owner de mudancas         |
|-------------------------------|-------------|----------------------------------------------------|---------------------------|
| `xgluoaaymbdzbbudnwrh`         | us-east-2   | KB estruturada S1 rodovias (v5.1 SP-native)        | trilha SP-native / MN     |
| `ogxxgvgtulrbbppshjie`         | sa-east-1   | Maestro core: episodios, judge, backlog, RAG hybrid | trilha repo Codex-exemplo |

**Politica de propriedade v5.2:**
- Mudancas em `xgluoaaymbdzbbudnwrh` (KB rodovias) → PR no SP com sync
  para repo em `sharepoint/00-arquitetura/`.
- Mudancas em `ogxxgvgtulrbbppshjie` (Maestro core) → PR no repo
  `MN1970/Codex-exemplo` + upload no SP como espelho.
- Cross-cutting (afeta os 2 projects) → coordenar via este documento.

---

## 2. CATALOGO DE AGENTES (20 OPERACIONAIS — inalterado)

Ver §2 de `ARQUITETURA-AGENTES-IA-v5.1.0.md` — sem mudancas de v5.1 para
v5.2.

## 3. ROUTING — MAESTRO (MANTA 00) — Inalterado v5.1

Ver §3 de `ARQUITETURA-AGENTES-IA-v5.1.0.md`.

## 4. CICLO DE VIDA (8 FASES) — Inalterado v5.1

Ver §4 de `ARQUITETURA-AGENTES-IA-v5.1.0.md`.

---

## 5. RAG + KB (consolidado v5.2)

### 5.1 Colecoes tematicas em `ogxxgvgtulrbbppshjie` (Maestro core)

| Colecao                       | Prefixo | Registros    | Tabela Supabase                     | Status |
|-------------------------------|---------|--------------|-------------------------------------|--------|
| Saneamento                    | `san:`  | 200+ docs    | `rag_chunks` (filtro segmento=S8)   | V5.0   |
| Energia                       | `ene:`  | 300+ docs    | `rag_chunks` (filtro segmento=S9)   | V5.0   |
| Portos                        | `por:`  | 150+ docs    | `rag_chunks` (filtro segmento=S6)   | V5.0   |
| Aeroportos                    | `aer:`  | 120+ docs    | `rag_chunks` (filtro segmento=S7)   | V5.0   |
| Barragens                     | `bar:`  | 180+ docs    | `rag_chunks` (filtro segmento=S10)  | V5.0   |
| Academic Knowledge            | `ake:`  | 36 teses + 52 KEs | `academic_knowledge_elements`   | V4.3   |
| Manta Cases                   | `mcs:`  | 3 projs + 23 KEs | `manta_cases_elements`          | V4.9   |

**Retrieval hybrid**: BM25 + vector via RRF k=60. RPCs:
`match_kes_hybrid`, `match_manta_cases_hybrid`, `manta_rag_agent_search`.

### 5.2 KB estruturada S1 rodovias em `xgluoaaymbdzbbudnwrh` (v5.1)

Ver §5.3 de `ARQUITETURA-AGENTES-IA-v5.1.0.md`. 5 tabelas: `modules` (12),
`parameters` (120), `technical_tables` (35), `common_errors` (48),
`case_studies` (18).

Queries prontas para agentes: ver §5.3 do v5.1.0.

---

## 6. AGENTIC INTELLIGENCE LAYER v4.7 (novo em v5.2 consolidado)

Aplicado ao Maestro core em `ogxxgvgtulrbbppshjie`. Roadmap
MNT-IA-20260712-001, 6 upgrades sequenciados:

- **Upgrade A — Reflexion Loop pre-entrega** (`maestro_reflexion.py`):
  output -> aluci-guard -> consist-guard -> se falha, autocritica + licao
  em `agent_episodes` -> refina (max 3 iter). Gating: apenas tarefas tier
  `star2`/`star3` (30-100% custo extra); `star1` fica single-shot.
- **Upgrade B — P2 Prompt Contract padronizado**: 4 elementos obrigatorios
  em delegacao a sub-agentes (`objective`, `output_format`,
  `tools_and_sources`, `boundaries`).
- **Upgrade C — Memoria episodica** (`agent_episodes` + HNSW 384d +
  `v_high_quality_episodes`): cada execucao registra `task_id`,
  `p2_contract`, `tools_used`, `outcome`, `custos`.
- **Upgrade D — Loop Primitives** (`manta_shared/loop_primitives.py`):
  sequential, parallel, race — Maestro emite DAG usando os 3 primitives.
- **Upgrade E — Model Tiering explicito** (`tier_policy` em cada SKILL.md
  + `maestro_cost_log`): enforcement no dispatcher; custos por execucao.
- **Upgrade F — SkillForge** (`sharepoint/03-skills-forjadas/`): pipeline
  cron 03:00 UTC gera skills automaticamente de padroes em
  `agent_episodes` (`skillforge_pending_review` gate humano MN).

Refs canonicos: `sharepoint/01-agentes-fundamentais/manta-maestro/refs/`
(`p2-contract-template.md`, `reflexion-loop-guide.md`,
`skillforge-pipeline.md`, `episodic-memory-schema.md`).

---

## 7. LEARNING LOOP FECHADO v4.9 (novo em v5.2 consolidado)

Aplicado ao Maestro core em `ogxxgvgtulrbbppshjie` em 2026-07-19. Fecha
o ciclo de aprendizado ligando o juiz LLM (v4.6) ao backlog de curadoria
(v4.5) automaticamente.

### 7.1 Pipeline em uma tela

```
manta_rag_queries.judge_score < 3
  ── trigger trg_judge_flag_to_backlog ──▶
    akp_curation_backlog (ticket_type='judge_flag', 1 por query_id)

promote_gaps_to_backlog(3, 3.0, 3)  [cron diario 08:00 UTC]
  ── ≥3 flags/30d por (agent_slug, segmento) ──▶
    akp_curation_backlog (ticket_type='judge_pattern', agregado)

v_judge_feedback_health
  ── alimenta prompt refinement, tier promotion (Haiku→Sonnet→Opus),
     Reflexion Loop, SkillForge, dashboard M19.
```

### 7.2 Objetos criados em prod

- **4 colunas aditivas** em `akp_curation_backlog`: `ticket_type`,
  `agent_slug`, `evidence` (JSONB), `priority` (SMALLINT 1-5).
- **3 CHECK constraints** (todas `NOT VALID` + `VALIDATE`).
- **3 sequences race-safe** — nunca MAX+1: `akp_judge_flag_seq`,
  `akp_judge_pattern_seq`, `akp_gap_candidate_seq`.
- **5 indexes** (2 UNIQUE parciais para dedup + 3 regulares).
- **Trigger** `trg_judge_flag_to_backlog` `AFTER INSERT OR UPDATE OF
  judge_score` `WHEN judge_score < 3` em `manta_rag_queries`.
- **Function** `judge_flag_to_backlog()` (SECURITY DEFINER, search_path
  fixo).
- **Function** `promote_gaps_to_backlog(INT, FLOAT, INT)` — estende v4.5
  com branch `judge_pattern`.
- **View** `v_judge_feedback_health` (`security_invoker=true`) — 30d,
  8 metricas + `health_status` ∈ {critical, warn, ok, healthy}.
- **RLS + hardening** — REVOKE grants excessivos; so `service_role`
  (+ `postgres` owner) executa a funcao. `authenticated` mantem SELECT
  na view; `anon` sem acesso.
- **View v4.6 antiga** `v_akp_judge_health` mantida com COMMENT
  ("superseded by v_judge_feedback_health. Deprecar em v5.0 se 90d sem
  consumer.").

Ref canonico: `05-sub-skills/manta-maestro/refs/learning-loop-v4.9.md`.

### 7.3 Como o Maestro consome esta camada

- **F6 Guardrails** — juiz LLM (Sonnet 4.6) roda ao final de cada resposta
  `star2`/`star3`. Se `judge_score < 3`, trigger cria ticket. Reflexion
  Loop le `agent_episodes.last_flags` na proxima execucao do mesmo agente
  e ativa autocritica.
- **F1.c Learned Router** — se `v_judge_feedback_health.health_status =
  'critical'` para um segmento, dispatcher promove tier de Haiku → Sonnet
  automaticamente.
- **SkillForge** — se >5 tickets `judge_pattern` abertos por 30d para
  o mesmo agente, aciona `skillforge_pipeline.py` para gerar sub-skill
  especifica do padrao (gate humano MN).

### 7.4 Migration + runbooks

- Migration: `supabase/migrations/2026_07_13_judge_feedback_loop_v4_9_adapted.sql`
- Runbook apply/rollback: `docs/JUDGE-FEEDBACK-LOOP-v4.9-ADAPTED-RUNBOOK.md`
- Backfill historico: `docs/V4.9-BACKFILL-RUNBOOK.md`
- Smoke test: `docs/SMOKE-TEST-v4.9-RUNBOOK.md`
- Sprint retrospectiva: `docs/SPRINT-RETROSPECTIVE-v4.9.md`
- Roadmap v5.x: `docs/ROADMAP-v5.0.md` (8 vetores priorizados)

---

## 8. INTEGRACAO COM SHAREPOINT (atualizado v5.2)

### 8.1 Estrutura de pastas (fusao dos dois trails)

```
04_IA/Manta-Maestro/
|-- 00-arquitetura/
|   |-- ARQUITETURA-AGENTES-IA-v5.2.0.md  <-- Este arquivo (consolidacao)
|   |-- ARQUITETURA-AGENTES-IA-v5.1.0.md  (KB rodovias, mantido)
|   |-- ARQUITETURA-AGENTES-IA-v5.0.0.md  (linha base v5)
|   |-- CLAUDE.md-v5.1.0-CONSOLIDATED.md
|   |-- SKILL-MANTA-MAESTRO-v1.1.0.md
|   |-- MAESTRO-OS-v6-API.md
|   |-- MAESTRO-OS-v6-DEVELOPER.md
|   +-- SYNC-SP-2026-07-28.md
|-- 01-segmentos/               (SP-native)
|-- 02-atividades/              (SP-native)
|-- 05-sub-skills/              (espelho repo Codex-exemplo)
|   +-- manta-maestro/
|       |-- SKILL.md (v4.9)
|       +-- refs/
|           |-- learning-loop-v4.9.md  (NOVO 2026-07-29)
|           |-- reflexion-loop-guide.md
|           |-- episodic-memory-schema.md
|           |-- p2-contract-template.md
|           +-- skillforge-pipeline.md
|-- 09-base-conhecimento/       (SP-native)
|   +-- KB-SUPABASE-RODOVIAS.md
+-- 99-backup/
```

### 8.2 Routing para SharePoint (inalterado v5.1)

Ver §6.2 de v5.1.0.md.

---

## 9. DEPLOYMENT CHECKLIST v5.2.0

- [x] v5.1.0 KB rodovias completo (12 modulos, 221 registros, 5 tabelas)
- [x] v4.7 Agentic Intelligence Layer aplicado em prod (roadmap MNT-IA-20260712-001)
- [x] v4.9 Learning Loop Fechado aplicado em prod 2026-07-19
- [x] SP: `refs/learning-loop-v4.9.md` uploaded (2026-07-29)
- [ ] SP: `SKILL.md v4.9` uploaded (grande arquivo — upload manual pendente)
- [x] SP: este documento `ARQUITETURA-AGENTES-IA-v5.2.0.md` publicado
- [x] Repo: nota de trilhas paralelas em `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`
- [x] Politica de propriedade dos 2 projects Supabase definida (§1.3)
- [ ] Reconciliar CLAUDE.md master (repo v4.9) com CLAUDE.md-v5.1.0-CONSOLIDATED.md (SP)
- [ ] Reconciliar SKILL-MANTA-MAESTRO-v1.1.0.md (SP) com SKILL.md v4.9 (repo)

---

## 10. HISTORICO

- **v5.2.0** (2026-07-29) — Reconciliacao das trilhas SP-native (v5.1
  KB rodovias) e repo Codex-exemplo (v3.0 Learning Loop v4.9). Politica
  de propriedade dos 2 projects Supabase definida. Este documento
  substitui v5.1.0 como referencia consolidada.
- **v5.1.0** (2026-07-28) — KB dispositivos rodoviarios integrada ao
  Supabase project `xgluoaaymbdzbbudnwrh` (12 modulos, 221 registros,
  5 tabelas). SKILL.md Maestro v1.1.0, S1 v3.2.0. Nova colecao RAG `rod:`.
  (trilha SP-native, nao passou pelo repo).
- **v5.0.0** (2026-07-22) — Consolidacao operacional completa SP-native.
  20 agentes, MAESTRO-OS v6.0, 5 colecoes RAG. (trilha SP-native).
- **v4.9** (2026-07-19, repo trail) — Fechar loop de aprendizado. 5 pipes
  aplicadas em prod: consolidate_old_episodes cron, /field-measurement
  endpoint, learned router SKIP formal, seed Manta Cases, judge feedback
  loop D1'. Hardening pos-apply.
- **v4.7** (2026-07-13, repo trail) — Agentic Intelligence Layer sobre
  v4.6.1: Reflexion + Episodic + P2 Contract + Loop primitives + Model
  tiering + SkillForge.
- **v4.6** (2026-07-12, repo trail) — Evolucao Maestro em 5 vetores
  paralelos (learned routing, biblio, Manta Cases pipeline, cron
  promote_gaps, LLM-judge).
- **v4.2** (2026-07-05) — Expansao S6-S10 (Portos, Aeroportos, Saneamento,
  Energia, Barragens).
- **v4.1** (anterior) — 15 agentes: horizontais + S1-S4.

**Documento — ARQUITETURA-AGENTES-IA v5.2.0**
Gerado: 2026-07-29 | Consolidacao de duas trilhas paralelas
Autor: Manta Associados
