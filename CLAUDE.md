# CLAUDE.md — Manta Maestro (Agent Registry & Evolution Roadmap)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md, runbooks operacionais no
SharePoint, e especificações de evolução da plataforma.

**Versão: v5.0** (2026-07-26) — Roadmap completo Phase 2-4 com implementação guidance.
- **v4.2** (2026-07-05) — Base: 20 agentes, 9 segmentos, 5 coleções RAG
- **v5.0** (2026-07-26) — Visão de evolução Phase 2-4: feedback loops, orchestration, APIs, federation, ecosystem

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
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| Manta 03-S6 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | 🆕 Criado 2026-07-05 |
| Manta 03-S8 | Saneamento | agente-saneamento | 🆕 Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | 🆕 Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | 🆕 Criado 2026-07-05 |

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

### Eixo 4 — Novos agentes (Phase 2-4, em planejamento)

| Código | Agente | Função | Status | Timeline |
|--------|--------|--------|--------|----------|
| Manta 17 | maestro-orchestrator | Orquestrador multi-agente (Phase 2.2) | 🔴 Planejado | Q4 2026 |
| Manta 18 | maestro-analyzer | Analytics & intelligence (Phase 4.2) | 🔴 Planejado | Q2 2028 |
| Manta 19 | maestro-federation | Federation broker (Phase 4.1) | 🔴 Planejado | Q1 2028 |
| Manta 20 | maestro-marketplace | Marketplace & ecosystem (Phase 4.4) | 🔴 Planejado | Q2 2029 |

---

## PHASE 2-4 ROADMAP (v5.0 Evolution)

**Phase 1 (90 dias)** ✅ Specification
- ✅ Keyword routing (v4.2 baseline)
- ✅ Vector search MVP (pgvector activation)
- ✅ Testing automation (CI/CD gate, 25 routing prompts)
- ✅ Monitoring baseline (Grafana, CloudWatch)
- Status: **Ready for execution**

**Phase 2 (6 meses)** ✅ Fully Specified
- ✅ Phase 2.1: Feedback Loop (Cowork button, SQL analysis, weekly recommendations)
- ✅ Phase 2.2: Multi-Agent Orchestration (Manta 17 orchestrator, ambiguous query detection)
- ✅ Phase 2.3: Document Auto-Classification (MCP listener, file extraction, folder routing)
- ✅ Phase 2.4: RAG Batch Ingestion (deployment runbook, 1,300+ chunks, monthly CI/CD)
- ✅ Phase 2.5: SharePoint Sync Automation (Graph API, agent .md → SKILL.md sync)
- Status: **Specs complete, ready for team implementation**

**Phase 3 (12 meses)** ✅ Fully Specified
- ✅ Phase 3.1: Public REST API (FastAPI, rate limiting, SDK, partners)
- ✅ Phase 3.2: Regulatory Webhooks (ANEEL, ANTAQ, ANA, ANAC listeners, 6h polling)
- ✅ Phase 3.3: Conversation API (stateful sessions, pgvector semantic context, GDPR erasure)
- ✅ Phase 3.4: AskCAD Persona Sync (metadata extraction, automatic sync on PR merge)
- ✅ Phase 3.5: Advanced Routing (LLM tie-breaker, Sonnet model, <500ms latency)
- ✅ Phase 3.6: Audit & Compliance (immutable audit log, SHA-256 hashing, GDPR-ready)
- Status: **Specs complete, team assignments ready, training materials prepared**

**Phase 4 (12 meses)** ✅ Fully Specified
- ✅ Phase 4.1: Agent Federation (mTLS, capability manifests, multi-org routing, trust tiers)
- ✅ Phase 4.2: Advanced Analytics (BI dashboards, predictive models, ROI tracking)
- ✅ Phase 4.3: Agent Learning (feedback fine-tuning, specialization, autonomy guardrails)
- ✅ Phase 4.4: Platform Ecosystem (agent marketplace, certification, open standards AFP/1.0)
- Status: **Fully specified, 4 implementation guides created**

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

## RAG — Coleções em Supabase (Phase 1-4)

### Coleções Organizadas (v4.2+)

| Coleção | Prefixo | Fontes | Chunks | Embedding | Status |
|---------|---------|--------|--------|-----------|--------|
| saneamento | san: | SNIS, NBR 12211-12218, Lei 14.026, AySA editais | 250+ | Anthropic 1536d | Phase 1 |
| energia | ene: | ANEEL R1-R5, EPE/ONS, IEEE, ACSR standards | 300+ | Anthropic 1536d | Phase 1 |
| portos | por: | ANTAQ, PIANC, BNDES editais, ISO 21191 | 280+ | Anthropic 1536d | Phase 1 |
| aeroportos | aer: | ANAC/RBAC 154, ICAO Annex 14, FAA AC 150 | 270+ | Anthropic 1536d | Phase 1 |
| barragens | bar: | ICOLD, CBDB, Lei 12.334, SIGBM, geotecnia | 280+ | Anthropic 1536d | Phase 1 |
| **shared-public** | pub: | NBR, ABNT, normas públicas, editais reguladores | 400+ | Anthropic 1536d | Phase 3-4 |

### Recursos (Phase 2-4)

- **Vector search** (pgvector, cosine similarity): <500ms latency per query
- **Semantic context retrieval**: Top-k embedding similarity + recency weighting (conversations)
- **Cross-collection queries**: Federated search for multi-domain projects
- **Regulatory webhooks** (Phase 3.2): Automatic RAG updates from ANEEL, ANTAQ, ANA, ANAC (6-hourly)
- **Batch ingestion**: Monthly CI/CD trigger, 500-token chunks, 100-token overlap
- **Quality monitoring**: Relevance scoring, hallucination detection (aluci-guard), user feedback loop

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |

---

## IMPLEMENTATION ROADMAP (Phase 1-4)

### Phase 1 (90 dias) — Consolidação & Automação
- **Week 1-2**: MN gate approval (v4.2 deployment + specs review)
- **Week 3-4**: Vector search MVP (pgvector + embeddings)
- **Week 5-8**: Testing automation (GitHub Actions CI/CD gate)
- **Week 9-12**: Monitoring baseline (Grafana, CloudWatch, alerting)
- **Gate 1**: ≥90% routing accuracy, <500ms latency p95
- **Deliverables**: Phase 1 complete, ready for Phase 2

### Phase 2 (6 meses) — Feedback Loops & Orchestration
**Teams**: Cowork (UI), Maestro (routing), DevOps (automation), Data (RAG)
- **Month 1-2**: Feedback loop (button, SQL analysis, GitHub issues)
- **Month 2-3**: Orchestrator agent (Manta 17, multi-agent dispatch)
- **Month 3-4**: Document auto-classification (MCP listener)
- **Month 4-5**: RAG ingestion automation (batch scripts, embeddings)
- **Month 5-6**: SharePoint sync (Graph API, auto-sync agent .md → SKILL.md)
- **Gate 2**: Feedback loop active (≥20 entries/week), <500ms latency
- **Deliverables**: 5 runbooks (2.1-2.5), 150 test artifacts, training materials

### Phase 3 (12 meses) — Public APIs & Intelligence
**Teams**: Maestro (APIs), Data (webhooks), DevOps (infrastructure)
- **Q1 2027**: Public API (3.1) + Regulatory webhooks (3.2)
- **Q2 2027**: Conversation API (3.3) + AskCAD sync (3.4)
- **Q3 2027**: LLM tie-breaker (3.5) + Compliance (3.6)
- **Gate 3**: 2+ partners live, <5% error rate, 99.9% uptime
- **Deliverables**: 6 implementation guides, Partner SDK, monitoring

### Phase 4 (12 meses) — Federation & Ecosystem
**Teams**: Maestro (federation), Data (analytics), DevOps (marketplace)
- **Q4 2027 – Q1 2028**: Agent Federation (4.1 design + implementation)
- **Q2 2028**: Advanced Analytics (4.2, BI platform)
- **Q3-Q4 2028**: Agent Learning (4.3, fine-tuning + specialization)
- **Q1 2029**: Ecosystem Launch (4.4, marketplace + community)
- **Gate 4**: 10+ third-party agents, zero data leaks, <$0.01 cost/query
- **Deliverables**: 4 ecosystem guides, Marketplace, Certification program

---

## DEPLOY CHECKLIST v5.0 (Updated Phase 1-4)

### Phase 1 (Execution: Week 1-12)
- [x] Specification complete (CLAUDE.md v5.0)
- [ ] MN gate: Approve v4.2 → Phase 1 transition
- [ ] GitHub Actions: Set up CI/CD pipeline for routing tests
- [ ] Supabase: Activate pgvector, create embedding tables
- [ ] Grafana: Deploy monitoring dashboard (latency, accuracy, costs)
- [ ] Test suite: Run 25 routing scenarios, validate ≥90% accuracy
- [ ] Documentation: Share PHASE1-EXECUTION-GUIDE.md with teams

### Phase 2 (Execution: Month 2-7)
- [ ] Cowork team: Implement feedback button UI (React component)
- [ ] Maestro team: Implement Orchestrator agent (Manta 17)
- [ ] Data team: Deploy RAG ingestion pipeline (1,300+ chunks)
- [ ] DevOps team: Implement SharePoint Graph API sync
- [ ] Testing: Run comprehensive test suite (150 artifacts)
- [ ] Runbooks: Validate Phase 2.4 (RAG) and 2.5 (SharePoint) deployment steps
- [ ] Integration: Test feedback → routing improvement loop end-to-end
- [ ] Documentation: Publish Phase 2 team guides (Cowork, Maestro, DevOps, Data)

### Phase 3 (Execution: Month 13-24)
- [ ] Maestro team: Develop Public API (FastAPI, OpenAPI/Swagger)
- [ ] Data team: Implement Regulatory webhook listeners (ANEEL, ANTAQ, ANA, ANAC)
- [ ] DevOps team: Deploy Conversation API (session management, pgvector context)
- [ ] Maestro team: Integrate LLM tie-breaker (Sonnet model for disambiguation)
- [ ] Data team: Implement GDPR audit trail and right-to-erasure
- [ ] Partner program: Onboard first 2-3 partners via Public API
- [ ] Testing: Validate Phase 3 SLAs (<500ms latency, 99.9% uptime)
- [ ] Documentation: Publish API docs, SLA terms, partner onboarding guides

### Phase 4 (Execution: Month 25-36)
- [ ] Maestro team: Implement Federation Broker (mTLS, capability manifests)
- [ ] Data team: Build Advanced Analytics platform (BI dashboards, ML models)
- [ ] Maestro team: Add Agent learning pipeline (feedback → fine-tuning)
- [ ] DevOps team: Launch Agent Marketplace (third-party agents, versioning)
- [ ] Governance: Establish Agent Certification program (security + compliance)
- [ ] Community: Open-source AFP/1.0 protocol, establish governance model
- [ ] Testing: Validate federation isolation, marketplace quality, ecosystem adoption
- [ ] Documentation: Publish Marketplace docs, Certification criteria, Community guide

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    └── agents/
        ├── agente-portos.md          # 🆕 S6
        ├── agente-aeroportos.md      # 🆕 S7
        ├── agente-saneamento.md      # 🆕 S8 — prioridade AySA
        ├── agente-energia.md         # 🆕 S9 — ANEEL/State Grid
        └── agente-barragens.md       # 🆕 S10
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Especificações & Documentação de Referência

### Guias Principais (v5.0)
- **PHASE4-ECOSYSTEM-ROADMAP-COMPLETE.md** — Roadmap Phase 1-4, timelines, teams, costs, ROI
- **COMPREHENSIVE-TEST-SUITE.md** — 150 test artifacts (routing, benchmarks, RAG, regulatory, feedback)
- **PHASE-4.1-AGENT-FEDERATION.md** — Federation architecture, protocols, data isolation
- **PHASE-4.2-ADVANCED-ANALYTICS.md** — BI platform, dashboards, predictive models
- **PHASE-4.3-ADVANCED-AGENT-CAPABILITIES.md** — Learning, specialization, autonomy
- **PHASE-4.4-PLATFORM-ECOSYSTEM.md** — Marketplace, certification, open standards

### Runbooks (Production-Ready)
- **RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md** — Step-by-step RAG ingestion guide (3,100+ lines)
- **RUNBOOK-PHASE-2.5-SHAREPOINT-SYNC.md** — Step-by-step SharePoint sync guide (2,800+ lines)
- **INTEGRATION-GUIDES-PHASE-2.1-2.3.md** — Team implementation instructions (2,500+ lines)

### Training Materials (Role-Specific)
- **TRAINING-GUIDE-COWORK-TEAM.md** — UI, feedback, notifications
- **TRAINING-GUIDE-MAESTRO-TEAM.md** — Routing, orchestration, debugging
- **TRAINING-GUIDE-DEVOPS-DATA-TEAMS.md** — Deployment, RAG, monitoring
- **Executive & Partner Guide** — Business case, API, SLAs

### Test Data & Infrastructure
- **comprehensive-test-suite.json** — 150 test artifacts (structured)
- **.github/workflows/deploy-maestro.yml** — CI/CD pipeline
- **infra/k8s/*.yaml** — Kubernetes manifests (deployment, service, HPA, monitoring)
- **infra/terraform/*.tf** — Infrastructure as code (Cloud Run, Supabase)
- **scripts/*.py** — Helper utilities (feedback analysis, A/B testing, backups)

---

## Histórico de versões

- **v5.0** (2026-07-26) — Phase 2-4 roadmap completa (6 fases de evolução, 21 meses)
  - Specifications: 15 implementation guides (12,600+ lines)
  - Roadmap: teams, timeline, risks, costs, training
  - Test suite: 150 artifacts (30 agents)
  - Infrastructure: Kubernetes, Terraform, GitHub Actions
  - Status: **Ready for team implementation**

- **v4.2** (2026-07-05) — Expansão S6–S10 (Portos, Aeroportos, Saneamento,
  Energia, Barragens). 5 novos agentes verticais + 5 coleções RAG + 5 pastas SP.
  Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
  
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.

---

## Success Criteria (Phase 1-4)

### Phase 1 (90 dias)
- ✅ Routing accuracy ≥90%
- ✅ Latency p95 <500ms
- ✅ CI/CD gate functional (25 routing tests)
- ✅ Monitoring live (dashboard, alerting)

### Phase 2 (6 meses)
- ✅ Feedback loop active (≥20 entries/week)
- ✅ Orchestration working (ambiguous queries → 2 agents)
- ✅ RAG relevance ≥85% (top-1)
- ✅ SharePoint sync automated

### Phase 3 (12 meses)
- ✅ 2+ partners using Public API
- ✅ Regulatory webhooks processing updates
- ✅ Conversations with semantic context
- ✅ Tie-breaker approval rate ≥85%
- ✅ Uptime 99.9%

### Phase 4 (12 meses)
- ✅ 10+ third-party agents in marketplace
- ✅ Zero cross-org data leaks (auditable)
- ✅ Cost per query <$0.01
- ✅ Predictive models accuracy >80%
- ✅ Community contributions flowing in

---

## Quick Links

- GitHub PR: [#24 — Manta Maestro v5.0 Evolution](https://github.com/MN1970/Codex-exemplo/pull/24)
- Execution Guide: `docs/PHASE4-ECOSYSTEM-ROADMAP-COMPLETE.md`
- Test Artifacts: `tests/comprehensive-test-suite.json` + `tests/COMPREHENSIVE-TEST-SUITE.md`
- Training Hub: `docs/TRAINING-GUIDE-*.md` (4 guides)
- Infrastructure: `infra/k8s/` + `infra/terraform/`
- Contact: maestro@mantaassociados.com
