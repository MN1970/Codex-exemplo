# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.5** (2026-07-12) — camada de governança: cross-refs entre
KEs (contradicts/supports), versionamento de tese com history, WF-AKP-002
(backlog de curadoria alimentado pela telemetria), human approval workflow,
CI parity check, playbook de handoffs cross-agent.

Versão anterior: **v4.4** (2026-07-12) — expansão de verticais: S5
Túneis promovido a agente próprio + S11 Mineração + S12 Óleo & Gás +
S13 Edificações.

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
