# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.4** (2026-08-09) — Fase 2: GitOps (security, threat modeling, incident response).

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
| Manta 17 | Git/GitHub (transversal) | agente-gitops | 🆕 Criado 2026-07-26 |

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
        ├── git-code-pattern-detection.md   # v2.0 — Fase 2 AST + CWE patterns (50+)
        ├── git-threat-modeling.md          # 🆕 Fase 2 — architectural threat analysis
        ├── git-incident-response.md        # 🆕 Fase 2 — incident & chaos workflows
        ├── git-gitops-flow.md              # ✅ Fase 1 — declarative operations (v2.0)
        ├── git-multi-repo-workflows.md     # ✅ Fase 1 — polyrepo automation (v2.0)
        └── git-commit-optimizer.md         # ✅ Fase 1 — commit message & history
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## Histórico de versões

- **v4.4** (2026-08-09) — Fase 2: Segurança & Resposta a Incidentes.
  5 skills (3 expandidos v2.0 + 2 novos) + 2 coleções RAG + threat modeling +
  incident response automation. Ticket MNT-2026-FASE2-GITOPS-SECURITY.
- **v4.3** (2026-07-26) — Agente Manta 17 (GitOps) com 6 skills iniciais.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
