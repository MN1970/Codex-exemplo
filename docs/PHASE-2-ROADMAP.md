# PHASE 2: Intelligence & Feedback (6-month roadmap)

**Período**: Jul 26 - Jan 26 | **Status**: 🔨 In Progress  
**Objetivo**: Transformar Maestro de roteador determinístico em sistema de aprendizado contínuo

---

## 📋 Overview

PHASE 2 ativa feedback loops, multi-agent orquestração, e automação de RAG que permitem o Maestro aprender de usuários e melhorar continuamente.

| Workstream | Deliverables | Timeline | Owner |
|-----------|--------------|----------|-------|
| **2.1** Feedback Loop | feedback tables + keyword learning | Jul 26 - Aug 09 | Claude Code + MN |
| **2.2** Multi-Agent Orchestration | Orchestrator Agent + ambiguous case dispatch | Aug 10 - Aug 31 | Maestro agents |
| **2.3** Document Auto-Classification | MCP listener + SharePoint auto-routing | Sep 01 - Sep 15 | Cowork integration |
| **2.4** RAG Ingestion Automation | batch PDF processing + chunking | Sep 16 - Sep 30 | Python automation |
| **2.5** SharePoint Sync Automation | Graph API script + CI/CD trigger | Oct 01 - Oct 15 | DevOps + security review |

---

## 2.1 — Feedback Loop (Jul 26 - Aug 09)

### ✅ Completed
- `maestro_user_feedback` table — track approvals/rejections
- `maestro_routing_keywords` table — dynamic keywords with confidence
- `maestro_feedback_analysis` table — aggregate metrics
- `maestro_routing_ab_tests` table — A/B testing infra
- Functions: `process_routing_feedback()`, `analyze_feedback_and_recommend()`

### 🔨 In Progress
- [ ] Cowork feedback button integration (approve/reject + confidence)
- [ ] Weekly analysis job (recommend keyword adjustments)
- [ ] Dashboard for feedback trends

### 📋 Checklist
```
- [ ] Apply migration: 2026_07_26_add_feedback_tables.sql
- [ ] Seed maestro_routing_keywords from CLAUDE.md
- [ ] Add "Was this agent correct?" button to Cowork UI
- [ ] Integrate process_routing_feedback() in Cowork callback
- [ ] Setup weekly job: SELECT * FROM analyze_feedback_and_recommend()
- [ ] Create GitHub issues from recommendations (auto)
- [ ] Monitor: approval_rate ≥ 85% per agent
```

---

## 2.2 — Multi-Agent Orchestration (Aug 10 - Aug 31)

### Goals
- Detect ambiguous cases (routing confidence score gap < 10 points)
- Dispatch to 2+ agents in parallel
- Orchestrator Agent (Manta 16) merges responses

### Design

**Detection**:
```python
IF score_gap(primary, runner_up) < 10:
  is_ambiguous = True
  dispatch_both_agents()
```

Examples:
- `"UHE + CFRD + LT 500kV"` → agente-barragens + agente-energia
- `"ETE + subestação"` → agente-saneamento + agente-energia
- `"Porto + pátio aéreo"` → agente-portos + agente-aeroportos

**Orchestration**:
```
Manta 00 (Maestro)
  ├─> agente-barragens (response A)
  ├─> agente-energia (response B)
  └─> Manta 16 (Orchestrator)
       → merge(A, B)
       → identify cross-concerns
       → synthesized response
```

### Deliverables
- [x] `.claude/agents/maestro-orchestrator.md` — Orchestrator spec ✅
- [ ] `manta-hub/maestro/orchestrator.py` — merge logic (pending integration)
- [x] `tests/routing/test_multiagent_dispatch.md` — test cases ✅ (10+ scenarios)
- [ ] Integration in maestro router (detect ambiguity → dispatch) (pending)

---

## 2.3 — Document Auto-Classification (Sep 01 - Sep 15)

### Goal
When user uploads PDF/DWG to SharePoint `03_Projetos/`, automatically:
1. Extract metadata
2. Route through Maestro
3. Suggest correct agent + folder
4. User approves → move/copy file

### Flow
```
OneDrive/SharePoint Upload
  ↓ (MCP listener or webhook)
Extract metadata
  ↓
Call maestro route_prompt()
  ↓
Suggest agent (e.g., "agente-saneamento")
  ↓
User approves in Cowork
  ↓
Move file to 03_Projetos/Saneamento/
  ↓
Record feedback (approval)
```

### Deliverables
- [x] `docs/DOCUMENT-AUTO-CLASSIFICATION.md` — Complete design spec ✅
- [ ] MCP listener in Cowork (file upload trigger) (pending)
- [ ] Classification prompt (summarize doc → routing) (pending)
- [ ] SharePoint move automation (Graph API) (pending)
- [ ] Feedback integration (user approval → learning) (pending)

---

## 2.4 — RAG Ingestion Automation (Sep 16 - Sep 30)

### Goal
Automated batch processing of PDFs → RAG chunks → Supabase

### Pipeline
```
PDF source (docs/rag-sources/{segment}/*.pdf)
  ↓ (monthly trigger or on-demand)
Extract text
  ↓
Chunk (500 tokens, 100-token overlap)
  ↓
Generate embedding (via embeddings_sync.py)
  ↓
Bulk insert to rag_chunks
  ↓
Log metadata (source, tier, timestamp)
```

### Deliverables
- [x] `scripts/ingest_rag_batch.py` — main ingestion script ✅
  - [x] TIER 1 (normas): aggressive chunking, preserve structure ✅
  - [x] TIER 2 (projetos): table/code-aware chunking ✅
  - [x] TIER 3 (estudos): semantic paragraph-based chunking ✅
  - [x] TIER 4 (templates): minimal processing ✅
  - [x] Supabase batch insert com error handling ✅
  - [x] Dry-run mode + CLI args (--segment, --tier, --max-chunks) ✅
- [ ] Audit table: `rag_ingestion_log` (what, when, how many) (pending)
- [ ] CI/CD trigger: `.github/workflows/ingest-rag-monthly.yml` (pending)
- [ ] Execute ingestion for 5 segments (saneamento, energia, portos, aeroportos, barragens) (pending)

### Coverage Targets
```
Collection      | Current | Target | Status
saneamento      | 0       | 150+   | 🔨
energia         | 0       | 180+   | 🔨
portos          | 0       | 120+   | 🔨
barragens       | 0       | 140+   | 🔨
aeroportos      | 0       | 110+   | 🔨
```

---

## 2.5 — SharePoint Sync Automation (Oct 01 - Oct 15)

### Goal
Continuous sync of `.claude/agents/*.md` → SharePoint SKILL.md

### Flow
```
PR merged to main
  ↓ (GitHub Actions trigger)
Update .claude/agents/*.md
  ↓
Build trigger: .github/workflows/sync-agents-to-sp.yml
  ↓
Graph API: agents .md → SP 04_IA/Manta-Maestro/01-agentes-fundamentais/
  ↓
Verify + version history
```

### Implementation
```python
# scripts/sync_agents_to_sharepoint.py
for agent_file in glob.glob('.claude/agents/*.md'):
    agent_slug = extract_slug(agent_file)
    sp_path = f"04_IA/Manta-Maestro/01-agentes-fundamentais/{agent_slug}/SKILL.md"

    content = agent_file.read_text()
    upload_to_sharepoint(sp_path, content, version_comment="Auto-sync from PR")
```

### Deliverables
- [x] `scripts/sync_agents_to_sharepoint.py` — upload logic ✅
  - [x] Graph API client for file upload ✅
  - [x] Dry-run preview mode ✅
  - [x] CLI support (--all, --changed, --agent) ✅
  - [x] Version history comments ✅
  - [x] Error handling + retry logic ✅
- [ ] `.github/workflows/sync-agents-to-sp.yml` — GitHub Actions (pending)
- [ ] Graph API scope approval (MICROSOFT_GRAPH_TOKEN credential setup) (pending)
- [ ] CI/CD integration: trigger on PR merge to main (pending)
- [ ] Version tracking + rollback capability (pending)

---

## Success Metrics — Phase 2

| Metric | Target | Validation |
|--------|--------|------------|
| **Feedback Loop** | ≥20 feedback entries/week | maestro_user_feedback row count |
| **Approval Rate** | ≥85% per agent | maestro_feedback_analysis.approval_rate |
| **Multi-Agent Dispatch** | 10+ ambiguous cases resolved | maestro_orchestrator logs |
| **Auto-Classification** | >80% accuracy | user approval rate on suggested agents |
| **RAG Coverage** | 150+ chunks/collection | rag_chunks row count by collection |
| **SharePoint Sync** | 100% agents in sync | diff between .claude/agents/ and SP |

---

## Timeline Gantt

```
Jul  Aug  Sep  Oct  Nov  Dec  Jan
├──┤  ├──┤  ├──┤  ├──┤  ├──┤  ├──┤
[2.1]  [2.2]  [2.3]  [2.4]  [2.5]
└───────────────────────────────┘
      PHASE 2 (6 months)
```

---

## Blocked/Risks

| Risk | Mitigation | Owner |
|------|-----------|-------|
| MN gate on Graph API scope | Start with read-only fallback | Security review |
| Low feedback signal initially | Promote button in Cowork; educate users | Product |
| Ambiguous case detection complexity | Start with simple score gap; iterate | Maestro team |
| RAG quality (relevance < 80%) | Increase chunk size; tune embedding model | Claude Code |

---

## Appendix: Implementation Checklist

### 2.1 Feedback Loop
```bash
# Setup
supabase db push supabase/migrations/2026_07_26_add_feedback_tables.sql

# Seed keywords
psql -d $DB << "SQL"
INSERT INTO maestro_routing_keywords (agent_slug, keyword, confidence, source)
SELECT agent, keyword, 0.8, 'manual'
FROM parse_claudemd_routing_rules();
SQL

# Monitor
SELECT approved, COUNT(*) FROM maestro_user_feedback
GROUP BY approved;
```

### 2.2 Multi-Agent Orchestration
```python
# Test ambiguous case
prompt = "UHE + CFRD + LT 500kV"
routes = maestro.route_multi(prompt)
# routes = [
#   {agent: 'agente-barragens', score: 0.95, primary: true},
#   {agent: 'agente-energia', score: 0.88, primary: false}
# ]

response = maestro_orchestrator.merge(
  agente_barragens_response,
  agente_energia_response
)
```

### 2.3 Document Auto-Classification
```
SharePoint upload → MCP listener → classification → user approval → move
```

### 2.4 RAG Ingestion
```bash
python scripts/ingest_rag_batch.py \
  --segment saneamento \
  --tier T1 \
  --source docs/rag-sources/saneamento/
```

### 2.5 SharePoint Sync
```bash
# CI/CD integration
git commit
git push
→ GitHub Actions runs
→ Calls scripts/sync_agents_to_sp.py
→ Updates SP automatically
```

---

**Last Updated**: 2026-07-26  
**Status**: 🔨 Phase 2.1 in progress — awaiting Cowork integration  
**Next Checkpoint**: 2026-08-09 (Feedback loop feedback signals)
