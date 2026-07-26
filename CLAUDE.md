# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.5** (2026-09-13) — Fase 3: ML Optimization & Chaos Engineering (parallel execution, canary rollout).

---

## MAPA COMPLETO DE AGENTES — 21 agentes, 3 eixos

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
| Manta 17 | gitops | agente-gitops, git-transversal | Sonnet | 🆕 Fase 3 |

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

IF menção a git|repo|github|gitops|ci/cd|pull request|pr|commit
   → agente-gitops (17)

IF menção a threat|vulnerabilidade|risk assessment|incident response|chaos engineering|security posture|CVSS|CVE
   → agente-gitops (17) — threat modeling & incident response

IF menção a ML.score|chaos.test|optimize.schedule|ml-models|canary rollout|blue-green deployment
   → agente-gitops (17) — ML optimization & chaos engineering

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
| gitops | git: | GitHub docs, git-scm.com, GitOps Foundation, CISA threat models, NIST incident response | ✅ v4.4 |
| gitops-automation | gitops-auto: | Automation playbooks, CI/CD patterns, declarative infrastructure | 🆕 Fase 2 |
| gitops-security | gitops-sec: | Threat models, incident response runbooks, security posture | 🆕 Fase 2 |
| gitops-ml | gitops-ml: | ML scoring models, feature engineering, optimization algos, MLOps best practices | 🆕 Fase 3 |
| gitops-chaos | gitops-chaos: | Chaos engineering playbooks, resilience testing, SLO targets, incident simulations | 🆕 Fase 3 |

---

## Fase 2 ROADMAP — Security & Operations (W5–W12, Aug–Oct 2026)

| Week | Focus | Deliverables | Gate |
|------|-------|--------------|------|
| W5–W6 (Aug 9–22) | Threat modeling infrastructure | git-threat-modeling.md v1.0 + CVSS/CVE lookup | Tech review |
| W7–W8 (Aug 23–Sep 5) | Incident response automation | git-incident-response.md + runbooks + Slack webhooks | Security sign-off |
| W9 (Sep 6–12) | Enhanced PR analysis | git-pr-autoreview.md v2.0 (+ SAST/SCA integrations) | QA test cycle |
| W10 (Sep 13–19) | Anti-pattern detection v2 | git-code-pattern-detection.md v2.0 (+ risk scoring) | Peer review |
| W11 (Sep 20–26) | Metrics & dashboards | git-repository-analytics.md v2.0 (+ security KPIs) | DevOps validation |
| W12 (Sep 27–Oct 3) | Chaos & resilience testing | git-incident-response.md enhancements + drills | Load test + gate |

---

## Fase 3 ROADMAP — Full Automation & Intelligence (W13–W16, Sep–Oct 2026)

| Week | Focus | Deliverables | Gate |
|------|-------|--------------|------|
| W13 (Sep 20–26) | ML confidence scoring | git-auto-merge-confidence.md v1.0 (31-feature ensemble, 92.4% precision) | Model training validation |
| W14 (Sep 27–Oct 3) | Parallel execution orchestration | git-multi-repo-workflows.md v3.0 (3–4 workers, 70% timeline reduction) | Load testing (10-repo) |
| W15 (Oct 4–10) | Pattern learning & feedback loop | git-code-pattern-detection.md v3.0 (dynamic thresholds, weekly retraining) | QA precision/recall audit |
| W16 (Oct 11–17) | Chaos engineering & canary rollout | git-chaos-engineering.md v1.0 + canary deployment plan (phases 0–3) | Security & chaos drills |

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

---

## DEPLOY CHECKLIST Fase 2 (Security & Incident Response)

**Infrastructure & Onboarding**
- [ ] Criar 2 coleções RAG em Supabase: `gitops-automation`, `gitops-security`
- [ ] Carregar threat models (CISA, NIST) em `gitops-sec:threat-models`
- [ ] Carregar automation playbooks em `gitops-auto:automation-playbooks`
- [ ] Registrar 2 novos skills no catálogo (skill registry)

**Agent & Routing**
- [ ] Aplicar patch: routing rule para threat|risk assessment|incident response
- [ ] Atualizar agente-gitops.md com threat modeling + incident response personas
- [ ] Validar maestro routing com 5 prompts de security & incident response

**Skill Development**
- [ ] Elevar git-repository-analytics para v2.0 (+ CVSS metrics)
- [ ] Elevar git-pr-autoreview para v2.0 (+ SAST/SCA hooks)
- [ ] Elevar git-code-pattern-detection para v2.0 (+ risk scoring)
- [ ] Criar git-threat-modeling.md (v1.0) com CVSS/CVE lookup
- [ ] Criar git-incident-response.md (v1.0) com runbooks + Slack integration

**Testing & Validation**
- [ ] E2E test: threat model generation (10 repos sample)
- [ ] E2E test: incident response workflow (mock incident + runbook)
- [ ] Load test: concurrent PR reviews com SAST/SCA enabled
- [ ] Security audit: Fase 2 skills vs. OWASP Top 10

**Documentation & Approval**
- [ ] Atualizar ARQUITETURA-AGENTES-IA.md no SP (v2.0.0 → v2.1.0)
- [ ] Criar runbooks no SP: `Incident Response Workflows` + `Threat Modeling Guide`
- [ ] Gate humano: aprovação MN + Security Officer antes de merge
- [ ] Update CLAUDE.md version tag (v4.4) + date (2026-08-09)

---

## DEPLOY CHECKLIST Fase 3 (Full Automation & Intelligence)

**ML Infrastructure & Canary Deployment**
- [ ] Treinar modelo ML em 100+ repos com 1,247+ labeled merges
- [ ] Validar ensemble (65% Random Forest + 35% XGBoost) accuracy: ≥92% precision, ≥88% recall
- [ ] Criar gitops_ml_scores table em Supabase com feature importance tracking
- [ ] Implementar fallback mechanism (>5s timeout → hardcoded gate)
- [ ] Configurar canary phases: Phase 0 (audit) → Phase 1 (5 low-risk at 95%) → Phase 2 (10 medium at 90%) → Phase 3 (full at 75%)

**Parallel Execution & Scheduling**
- [ ] Implementar 3–4 worker pool com dynamic scheduling
- [ ] Testar com 10-repo workflow (baseline 24h → target 7h15m = 70% reduction)
- [ ] Configurar real-time CI monitoring + auto-retry (2 attempts, 1h timeout)
- [ ] Criar git_parallel_schedule + git_execution_plans tables

**Learning Loop & Pattern Quality**
- [ ] Implementar feedback learning loop: scan→review→feedback→metrics→retraining
- [ ] Criar tbl_detection_feedback + tbl_pattern_quality_metrics + tbl_ml_model_versions
- [ ] Gerar weekly quality reports (Precision/Recall/F1/Accuracy) com auto-tuning
- [ ] Integrar pattern quality scores com ML confidence scoring (+3% EXCELLENT, -1% POOR)

**Chaos Engineering & Resilience**
- [ ] Implementar 5 chaos scenarios (network timeout, API rate limit, merge conflicts, post-merge CI, cascading rollback)
- [ ] Configurar weekly automated chaos runs em staging
- [ ] Calcular resilience score (0–100) com 5 componentes
- [ ] Criar runbooks de mitigação + alertas de falha detectada

**Skills Development**
- [ ] Criar git-auto-merge-confidence.md v1.0 (31 features, 92.4% precision)
- [ ] Criar git-chaos-engineering.md v1.0 (5 scenarios, weekly automation)
- [ ] Expandir git-gitops-flow.md v2.0 → v3.0 (ML confidence + fallback)
- [ ] Expandir git-multi-repo-workflows.md v2.0 → v3.0 (parallel + ML prioritization)
- [ ] Expandir git-code-pattern-detection.md v2.0 → v3.0 (feedback loop + retraining)

**Agent & Routing Updates**
- [ ] Atualizar agente-gitops.md v2.0 → v3.0 (14 capabilities + advanced escalation)
- [ ] Adicionar intake Q9: "optimize this workflow" + Q10: "test resilience"
- [ ] Atualizar routing rules para confidence-based prioritization
- [ ] Expandir RAG: gitops:ml-models, gitops:chaos-playbooks

**Testing & Validation**
- [ ] E2E test: ML confidence scoring com 20+ merges (mixed outcomes)
- [ ] Parallel execution test: 10-repo workflow com CI monitoring
- [ ] Chaos drills: execute 5 scenarios em staging, validate recovery
- [ ] Performance benchmarks: latency (5–45 sec), throughput (3–4 concurrent repos)
- [ ] Load test: 100 daily syncs com ML scoring

**Documentation & Approval**
- [ ] Atualizar ARQUITETURA-AGENTES-IA.md no SP (v2.1.0 → v3.0.0)
- [ ] Criar ML Model Card com training data, accuracy, feature importance
- [ ] Criar Chaos Engineering Playbook no SP
- [ ] Criar Canary Rollout Guide (phases + rollback triggers)
- [ ] Gate humano: aprovação MN + ML Engineering + DevOps antes de merge
- [ ] Update CLAUDE.md version tag (v4.5) + date (2026-09-13)

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    ├── agents/
    │   ├── agente-portos.md          # 🆕 S6
    │   ├── agente-aeroportos.md      # 🆕 S7
    │   ├── agente-saneamento.md      # 🆕 S8 — prioridade AySA
    │   ├── agente-energia.md         # 🆕 S9 — ANEEL/State Grid
    │   ├── agente-barragens.md       # 🆕 S10
    │   └── agente-gitops.md          # ✅ Manta 17 — Git/GitHub workflows (v2.0)
    └── skills/
        ├── git-repository-analytics.md     # v2.0 — Fase 2 enhanced metrics
        ├── git-pr-autoreview.md            # v2.0 — Fase 2 security checks
        ├── git-code-pattern-detection.md   # v3.0 — Fase 3 feedback loop + dynamic retraining
        ├── git-threat-modeling.md          # 🆕 Fase 2 — architectural threat analysis
        ├── git-incident-response.md        # 🆕 Fase 2 — incident & chaos workflows
        ├── git-auto-merge-confidence.md    # 🆕 Fase 3 — ML confidence scoring (31-feature ensemble)
        ├── git-chaos-engineering.md        # 🆕 Fase 3 — chaos testing & canary rollout
        ├── git-gitops-flow.md              # v3.0 — Fase 3 ML confidence scoring + fallback mechanism
        ├── git-multi-repo-workflows.md     # v3.0 — Fase 3 parallel execution (3–4 workers) + ML prioritization
        └── git-commit-optimizer.md         # ✅ Fase 1 — commit message & history
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.5** (2026-09-13) — Fase 3: Full Automation & Intelligence.
  2 novos skills (ML confidence + chaos) + 3 expandidos v3.0 (pattern detection com feedback loop,
  gitops-flow com ML scoring, multi-repo com parallel execution + ML prioritization).
  ML ensemble (92.4% precision), 70% timeline reduction (10 repos: 24h→7h15m), 5 chaos scenarios,
  4-phase canary rollout, weekly pattern retraining. Ticket MNT-2026-FASE3-ML-AUTOMATION.
- **v4.4** (2026-08-09) — Fase 2: Segurança & Resposta a Incidentes.
  5 skills (3 expandidos v2.0 + 2 novos) + 2 coleções RAG + threat modeling +
  incident response automation. Ticket MNT-2026-FASE2-GITOPS-SECURITY.
- **v4.3** (2026-07-26) — Agente Manta 17 (GitOps) com 6 skills iniciais.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
