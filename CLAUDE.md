# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.7** (2026-07-13 planejada) — Agentic Intelligence Layer
sobre v4.6.1: Reflexion Loop pré-entrega + Memória episódica + P2
Prompt Contract + Loop primitives + Model tiering explícito + SkillForge
(ver roadmap MNT-IA-20260712-001 e SKILL.md §14 do Maestro).

Versão anterior: **v4.6** (2026-07-12, com reconciliação Codex ↔ SP) —
evolução Maestro em 5 vetores paralelos: V1 learned routing (scaffold
ML), V2 bibliografia arq. de agentes (6 KEs seed), V3 WF-MCP-001 casos
Manta (coleção `mcs:` priority 120 > academic), V4 cron diário
promote_gaps_to_backlog, V5 LLM-as-a-judge (Sonnet 4.6), V7 multi-channel
distribution (Claude Code/AI/Cowork). Adicionalmente formaliza a
reconciliação entre a taxonomia sub-segmento `Manta 03-S{n}` deste repo
Codex-exemplo e a taxonomia top-level `S{n}` do Maestro operacional SP
v3.0+ (ver seção "RECONCILIAÇÃO COM MAESTRO OPERACIONAL").

Versão v4.5 (2026-07-12) — camada de governança: cross-refs
entre KEs (contradicts/supports), versionamento de tese com history,
WF-AKP-002 (backlog de curadoria alimentado pela telemetria), human
approval workflow, CI parity check, playbook de handoffs cross-agent.

Versão v4.4 (2026-07-12) — expansão de verticais: S5 Túneis promovido
a agente próprio + S11 Mineração + S12 Óleo & Gás + S13 Edificações.

Versão v4.3 (2026-07-12) — ativação do Academic Knowledge Pipeline
(WF-AKP-001): coleção `academic-knowledge` transversal, schema pgvector,
36 teses + 52 KEs, hooks nos SKILL.md de S6–S10.

Versão base: **v4.2** (2026-07-05) — expansão S6–S10 (Portos,
Aeroportos, Saneamento, Energia, Barragens).

---

## MAPA COMPLETO DE AGENTES — 20 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional |

### Eixo 2 — Verticais por segmento (C3)

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S5 | Túneis | agente-tuneis | 🆕 Criado 2026-07-12 (v4.4) |
| Manta 03-S6 | Portos | agente-portos | ✅ Criado 2026-07-05 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | ✅ Criado 2026-07-05 |
| Manta 03-S8 | Saneamento | agente-saneamento | ✅ Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | ✅ Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | ✅ Criado 2026-07-05 |
| Manta 03-S11 | Mineração | agente-mineracao | 🆕 Criado 2026-07-12 (v4.4) — adjacente S10 |
| Manta 03-S12 | Óleo & Gás | agente-oleo-gas | 🆕 Criado 2026-07-12 (v4.4) — downstream + midstream |
| Manta 03-S13 | Edificações | agente-edificacoes | 🆕 Criado 2026-07-12 (v4.4) — vertical + galpão |

### RECONCILIAÇÃO COM MAESTRO OPERACIONAL (SP v3.0+)

**Contexto do conflito:** o repositório Codex-exemplo (este) modela os
segmentos de C3 como sub-códigos `Manta 03-S{n}` (S1–S13); o Maestro
operacional SP v3.0 (rodando em produção) usa códigos top-level `S{n}`
que colidem em S5 e S6 (SP: S5 Imobiliário, S6 Edificações — sem os
outros verticais deste repo). A tabela abaixo é a **reconciliação
canônica** aplicada aos SKILL.md via campo `sp_operational_segment` no
frontmatter YAML:

| Codex-exemplo (este repo) | Segmento    | Maestro SP operacional |
|---------------------------|-------------|------------------------|
| Manta 03-S1               | Rodovias    | S1                     |
| Manta 03-S2               | OAE         | S2                     |
| Manta 03-S3               | Ferrovia    | S3                     |
| Manta 03-S4               | Metrô       | S4                     |
| Manta 03-S5               | Túneis      | **S12**                |
| Manta 03-S6               | Portos      | **S7**                 |
| Manta 03-S7               | Aeroportos  | **S8**                 |
| Manta 03-S8               | Saneamento  | **S9**                 |
| Manta 03-S9               | Energia     | **S10**                |
| Manta 03-S10              | Barragens   | **S11**                |
| Manta 03-S11              | Mineração   | **S13**                |
| Manta 03-S12              | Óleo & Gás  | **S14**                |
| Manta 03-S13              | Edificações | S6 (reusa)             |

Cada arquivo `sharepoint/01-agentes-fundamentais/agente-*/SKILL.md`
declara agora `sp_operational_segment: S<N>` conforme a coluna direita.
O código `Manta 03-S{n}` continua sendo a identidade canônica deste
repo; o `sp_operational_segment` é o pino de ligação com o kernel
Manta 12 do SP.

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais suportam as 8 fases via intake Q2:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento atualizada para Q1 do intake:

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

IF menção a túnel|tunel|NATM|TBM|EPB|shotcrete|dovela|cut and cover|imerso
   → agente-tuneis (S5)

IF menção a mineração|mina|minério|ANM|DNPM|cava|open pit|NI 43-101|JORC|LOM|heap leach|Vale|Anglo|Carajás
   → agente-mineracao (S11)

IF menção a petróleo|óleo e gás|ANP|gasoduto|oleoduto|refinaria|Comperj|Rnest|API 650|API 5L|GASBOL|LNG|HAZOP
   → agente-oleo-gas (S12)

IF menção a edificação|torre|galpão|warehouse|data center|hospital|MCMV|NBR 15575|MRV|Cyrela|BIM|LEED|AQUA
   → agente-edificacoes (S13)

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

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES | 🆕 v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE | 🆕 v4.2 |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |
| academic-knowledge | ake: | 36 teses + 52 KEs curados (WF-AKP-001) | 🆕 v4.3 — transversal |
| tuneis | tun: | ITA/AITES, PIARC C4, NFPA 502, NBR 15220, DNIT IPR-742 | 🆕 v4.4 |
| mineracao | min: | ANM/NRM, SME, CIM/JORC, NI 43-101, PERC | 🆕 v4.4 |
| oleo-gas | ogs: | ANP, API (650, 5L, 653), ANSI B31, NFPA 30/59A, IEC 61511 | 🆕 v4.4 |
| edificacoes | edi: | NBR 15575, NBR 6118, IT-CBMESP, LEED, ISO 19650 | 🆕 v4.4 |

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |
| rag-academic-knowledge | 07_Conhecimento_Academico/* | *.pdf, *.md, *.json |
| agente-tuneis | 03_Projetos/Tuneis/* | *.pdf, *.dwg, *.xlsx |
| agente-mineracao | 03_Projetos/Mineracao/* | *.pdf, *.dwg, *.xlsx |
| agente-oleo-gas | 03_Projetos/OleoGas/* | *.pdf, *.dwg, *.xlsx |
| agente-edificacoes | 03_Projetos/Edificacoes/* | *.pdf, *.dwg, *.xlsx |

---

## DEPLOY CHECKLIST v4.2

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing`
- [ ] Criar pastas SP para novos segmentos
- [ ] Registrar skills no catálogo (skill registry)
- [ ] Testar routing do Maestro com prompts de cada segmento
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge

## DEPLOY CHECKLIST v4.3 — Academic Knowledge Pipeline (WF-AKP-001)

Stages 1-3 concluídas fora deste repo (36 teses, 52 KEs). Stages 4-6:

- [x] Migração pgvector candidata em `supabase/migrations/2026_07_12_akp_stages_4_6.sql`
- [x] Folder SharePoint scaffolded em `sharepoint/02-academic-knowledge/`
- [x] Hooks `academic-knowledge` adicionados nos 5 SKILL.md (S6-S10)
- [x] Script ingestor em `manta-hub/scripts/akp_ingest.py`
- [x] Runbook em `manta-hub/docs/AKP-INGESTION.md`
- [ ] Aplicar migração no Supabase (`supabase db push`)
- [ ] Upload dos 36 PDFs em `07_Conhecimento_Academico/01_teses/`
- [ ] Rodar `akp_ingest.py` com `akp-ke-payload.json` real
- [ ] Validar 52 embeddings em `academic_knowledge_elements`
- [ ] Smoke test — 5 prompts (um por segmento S6-S10) retornando ≥3 KEs
- [ ] Gate humano MN antes de habilitar produção

## DEPLOY CHECKLIST v4.4 — Expansão S5, S11, S12, S13

- [x] Copiar 4 novos agent .md para `.claude/agents/`
      (agente-tuneis, agente-mineracao, agente-oleo-gas, agente-edificacoes)
- [x] Criar 4 novas pastas SP em `01-agentes-fundamentais/`
      (SKILL.md + README.md + refs/ + prompts/)
- [x] Bump versão CLAUDE.md master v4.3 → v4.4
- [x] Migração candidata `supabase/migrations/2026_07_12_verticals_v4_4.sql`
      (4 rag_collections + 4 sp_agent_routing + keywords + agent_rag_bindings
      para consumo da coleção academic-knowledge)
- [ ] Aplicar migração no Supabase
- [ ] Criar as 4 pastas no SharePoint (`03_Projetos/{Tuneis,Mineracao,OleoGas,Edificacoes}/`)
- [ ] Testar routing do Maestro com prompts de cada novo segmento
- [ ] Smoke test AKP também para os 4 novos (extender `akp_smoke_test.py`)
- [ ] Gate humano MN antes de merge

## DEPLOY CHECKLIST v4.6 — Evolução Maestro (5 vetores paralelos)

- [x] **V1 Learned Routing** — migração `2026_07_12_maestro_learned_router_v4_6.sql`
      (`maestro_routing_predictions` + views `v_router_accuracy` + `v_router_disagreements`)
      + `manta-hub/scripts/maestro_learned_router.py` com 4 modos (train/infer/evaluate/retrain-incremental).
- [x] **V2 Bibliografia arq. agentes** — 6 seed KEs em
      `sharepoint/02-academic-knowledge/seed/akp-seed-arquitetura-agentes.json`
      (Chen AgentBench, Wu AutoGen, Park Generative Agents, Shen HuggingGPT,
      Anthropic Building Effective Agents, Cormack RRF).
- [x] **V3 WF-MCP-001 casos Manta** — migração `2026_07_12_manta_cases_v4_6.sql`
      (coleção `mcs:` priority 120, tabelas `manta_projects` + `manta_cases_elements`
      + função `match_manta_cases_hybrid` com filtro NDA) + folder SP
      `03-manta-cases/` + doc `docs/WF-MCP-001.md` + script `manta-hub/scripts/manta_cases_extract.py`.
- [x] **V4 Cron diário** — GH Action `.github/workflows/akp-daily-cron.yml`
      (promote-gaps 08:00 UTC + daily-report como job auxiliar).
- [x] **V5 LLM-as-a-judge** — migração `2026_07_12_llm_judge_v4_6.sql`
      (colunas `judge_score/judge_notes` em `agent_query_log` + tabela
      `agent_response_flags` + trigger auto-flag < 3 + view `v_akp_judge_health`)
      + `manta-hub/scripts/akp_judge.py`.
- [x] **V7 Multi-channel distribution** — `manta-hub/scripts/publish_agents.py`
      (emite Claude Code + claude.ai Project.zip + Skill v2.zip + Cowork.json)
      + GH Action `.github/workflows/publish-agents.yml`.
- [x] Fix YAML frontmatter dos 4 agentes v4.4 (colons no `description:` →
      block scalar `>-`).
- [ ] Aplicar as 4 migrações v4.6 no Supabase (ordem: learned_router →
      llm_judge → manta_cases; independentes entre si)
- [ ] Gate humano MN antes de mergear v4.6

## DEPLOY CHECKLIST v4.5 — Governance Layer

- [x] Migração candidata `supabase/migrations/2026_07_12_akp_governance_v4_5.sql`
      - Coluna `related_kes` JSONB + view `v_akp_contradictions` (#7)
      - Coluna `revision` + tabela `academic_theses_history` + trigger (#8)
      - Tabela `akp_curation_backlog` + função `promote_gaps_to_backlog()` (#10 — WF-AKP-002)
      - Tabelas `agent_change_requests` + `agent_change_reviews` + trigger de auto-status (#13)
- [x] Playbook em `docs/HANDOFFS-CROSS-AGENT.md` (8 cenários canônicos)
- [x] CI parity em `.github/workflows/skill-sync-check.yml`
- [ ] Aplicar migração no Supabase (aditiva sobre v4.4)
- [ ] Rodar os 8 cenários do playbook manualmente com MN e registrar resultado
- [ ] Agendar `SELECT promote_gaps_to_backlog();` diário via pg_cron ou GH Action
- [ ] Gate humano MN antes de merge

## DEPLOY CHECKLIST v4.7 — Agentic Intelligence Upgrade

Roadmap MNT-IA-20260712-001. Seis fases sequenciadas (A pode ir em
paralelo com B; C bloqueia F). Cada fase tem gate humano MN antes de
mergear.

### Fase 1 — Fundação (docs + refs SharePoint)

- [x] Criar 4 refs canônicos em `sharepoint/01-agentes-fundamentais/manta-maestro/refs/`
      (`p2-contract-template.md`, `reflexion-loop-guide.md`,
      `skillforge-pipeline.md`, `episodic-memory-schema.md`)
- [x] Bump versão CLAUDE.md master v4.6 → v4.7 (esta entrada)
- [ ] Bump `SKILL.md` do Maestro para v4.7 incluindo §14 (A-F)
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v2.0.0 → v3.0.0)

### Fase 2 — P2 Contract (Upgrade B) + Episodic Memory (Upgrade C)

- [ ] Migração candidata `supabase/migrations/2026_07_13_episodic_memory_v4_7.sql`
      (tabela `agent_episodes` + view `v_high_quality_episodes` +
      view `v_episodic_health` + índice HNSW)
- [ ] Implementar emissão obrigatória de P2 no dispatcher do Maestro
      (falha soft se ausente; log warning por 14d, hard fail depois)
- [ ] Instrumentar gravação em `agent_episodes` ao fim de cada
      execução de subagente (task_id, p2_contract, tools_used, custos)

### Fase 3 — Reflexion Loop (Upgrade A)

- [ ] Implementar `maestro_reflexion.py` em `manta-hub/scripts/`
      (prompt de autocrítica §2.4 do roadmap + retry policy max=3)
- [ ] Gating: aplicar SOMENTE em tarefas star2/star3 (intake Q3)
- [ ] Métrica: `v_reflexion_stats` (taxa 1-iter, escalation rate por agente)
- [ ] Alerta Slack: escalation rate > 10% em 7d ⇒ ping MN

### Fase 4 — Loop primitives (Upgrade D)

- [ ] Definir 3 loop primitives canônicos (sequential, parallel, race)
      em `manta_shared/loop_primitives.py`
- [ ] Refactor do Maestro para emitir DAG de execução usando os 3
      primitives (substitui orquestração ad-hoc atual)
- [ ] Testes E2E dos 8 cenários de `handoffs-cross-agent.md` com DAG novo

### Fase 5 — Model Tiering explícito (Upgrade E) + Cost governance

- [ ] Atualizar todos SKILL.md com campo `tier_policy` explícito:
      `haiku_for: [...]`, `sonnet_for: [...]`, `opus_for: [...]`
- [ ] Enforcement no dispatcher (rejeita tier abaixo do mínimo)
- [ ] Dashboard `/admin/cost-per-agent` em manta-hub com timeseries

### Fase 6 — SkillForge (Upgrade F)

- [ ] Criar `sharepoint/03-skills-forjadas/` (vazio inicial) +
      `sharepoint/03-skills-forjadas/deprecated/`
- [ ] Migração `supabase/migrations/2026_07_13_skillforge_v4_7.sql`
      (tabela `skillforge_rejects` + view `v_skillforge_gate`)
- [ ] Script `manta-hub/scripts/skillforge_pipeline.py` (6 passos do
      §1 do ref)
- [ ] GH Action `.github/workflows/skillforge-daily.yml` — cron 03:00 UTC

### Gate humano MN final (aplicável a TODAS as fases)

- [ ] MN roda `tests/maestro/test_wipe_recovery.py` (episódios wipe test)
- [ ] MN valida os 8 cenários de `handoffs-cross-agent.md` com v4.7 ligado
- [ ] MN aprova merge para main (branch `feat/v4.7-agentic-intelligence`)

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    └── agents/
        ├── agente-portos.md          # S6 (v4.2)
        ├── agente-aeroportos.md      # S7 (v4.2)
        ├── agente-saneamento.md      # S8 — prioridade AySA (v4.2)
        ├── agente-energia.md         # S9 — ANEEL/State Grid (v4.2)
        ├── agente-barragens.md       # S10 (v4.2)
        ├── agente-tuneis.md          # 🆕 S5 (v4.4)
        ├── agente-mineracao.md       # 🆕 S11 (v4.4) — adjacente S10
        ├── agente-oleo-gas.md        # 🆕 S12 (v4.4) — downstream/midstream
        └── agente-edificacoes.md     # 🆕 S13 (v4.4) — vertical + galpão
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.6** (2026-07-12) — Evolução Maestro em 5 vetores paralelos
  (V1+V2+V3+V4+V5+V7), disparados como 5 subagentes simultâneos e
  costurados em commit único. **V1 Learned Routing** (scaffold ML: MLP
  384→128 sobre embeddings multilingual-e5-small; mock data quando log
  vazio; integra como pré-router com threshold de confidence 0.85).
  **V2 Bibliografia arq. agentes** (6 papers seed cobrindo AgentBench,
  AutoGen, Generative Agents, HuggingGPT, Anthropic "Building Effective
  Agents", Cormack RRF — Maestro consulta a si mesmo). **V3 WF-MCP-001
  Manta Cases Pipeline** (coleção `mcs:` transversal priority 120 > 100
  da academic; tabela `manta_projects` + `manta_cases_elements` com
  8 tipos de caso; função hybrid com filtro NDA 4 níveis; extrator PDF
  /DOCX via Sonnet 4.6). **V4 cron diário** de `promote_gaps_to_backlog`
  (GH Action 08:00 UTC + issue automática ≥5 tickets). **V5
  LLM-as-a-judge** (Sonnet 4.6 avalia 5 critérios 0-5 sobre amostragem
  10% estratificada; trigger auto-flag < 3; ~US$0.02/query). **V7
  multi-channel distribution** (script publish_agents emite Claude Code
  + claude.ai Project.zip + Skill v2.zip + Cowork.json a partir da mesma
  fonte SKILL.md; GH Action publica em push). Fix bonus: os 4 YAML
  frontmatter dos agentes v4.4 (colons no `description:`) foram
  convertidos para block scalar `>-`. V6 (fusão Codex↔manta-hub) fica
  para sprint separada com Vinícius.
- **v4.5** (2026-07-12) — Camada de governança. Cross-references entre
  KEs (contradicts/supports/extends/supersedes/cites via JSONB + view
  `v_akp_contradictions`). Versionamento de tese: coluna `revision` +
  tabela `academic_theses_history` + trigger auto-snapshot antes de
  UPDATE. WF-AKP-002 formalizado como `akp_curation_backlog` +
  função `promote_gaps_to_backlog()` que alimenta tickets a partir da
  view v4.3 `v_akp_gap_candidates`. Human approval workflow com
  `agent_change_requests` + `agent_change_reviews` (regra ≥2 approvals
  sem rejeitos → aprovado). Playbook `docs/HANDOFFS-CROSS-AGENT.md`
  com 8 cenários cross-agent. CI parity check
  `.github/workflows/skill-sync-check.yml` valida drift entre
  `.claude/agents/`, `sharepoint/` e o CLAUDE.md master.
- **v4.4** (2026-07-12) — Expansão de verticais: S5 Túneis promovido
  a agente próprio (NATM/TBM/imerso), S11 Mineração (adjacente a S10
  barragens, escopo fora de TSF), S12 Óleo & Gás (downstream + midstream,
  fora reservatório/poço), S13 Edificações (vertical residencial +
  comercial + galpão industrial leve). 4 novos agentes + 4 coleções RAG
  + 4 pastas SP + migração candidata `2026_07_12_verticals_v4_4.sql`.
- **v4.3** (2026-07-12) — Academic Knowledge Pipeline (WF-AKP-001)
  stages 4-6. Nova coleção RAG transversal `academic-knowledge` com
  36 teses + 52 Knowledge Elements. Schema pgvector, folder SP
  `07_Conhecimento_Academico/`, hooks nos SKILL.md de S6-S10 e nos
  horizontais advisory + arquiteto-ia.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
