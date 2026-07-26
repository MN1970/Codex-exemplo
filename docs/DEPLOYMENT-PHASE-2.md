# Phase 2 Deployment Checklist

**Status**: 🟢 READY FOR DEPLOYMENT  
**Branch**: `claude/evaluar-manta-maestro-hzx1oo`  
**Target Date**: 2026-08-09 (Phase 2.1 feedback loop activation)

---

## 📋 Quick Summary

**Phase 2** implements intelligence and feedback systems across 5 workstreams:

| Component | Deliverable | Status | Owner |
|-----------|-------------|--------|-------|
| **2.1 Feedback Loop** | Database tables + functions | ✅ Complete | Cowork + MN |
| **2.2 Multi-Agent Orch** | Spec + tests + implementation guide | ✅ Complete | Maestro team |
| **2.3 Auto-Classification** | Design spec | ✅ Complete | Claude Code + Cowork |
| **2.4 RAG Ingestion** | Production script + CI/CD | ✅ Complete | Claude Code |
| **2.5 SharePoint Sync** | Production script + CI/CD | ✅ Complete | Claude Code |

**What's ready to deploy RIGHT NOW:**
- ✅ Phase 2.4: RAG ingestion script + monthly CI/CD workflow
- ✅ Phase 2.5: SharePoint sync script + auto-sync CI/CD workflow

**What needs integration:**
- 🔨 Phase 2.1: Cowork feedback button + weekly analysis job
- 🔨 Phase 2.2: Orchestrator implementation in manta-hub
- 🔨 Phase 2.3: MCP listener for document uploads

---

## PART 1: IMMEDIATE (This Week)

### 1.1 — Configure GitHub Secrets

```bash
# GitHub Settings → Secrets and variables → Actions
# Add these secrets:

ANTHROPIC_API_KEY=sk-ant-...               # Claude API key
SUPABASE_URL=https://xxx.supabase.co       # Your Supabase project
SUPABASE_ANON_KEY=eyJhbGc...               # Supabase anon key

SHAREPOINT_SITE_ID=xxx-xxx-xxx-xxx         # Manta SharePoint site ID
SHAREPOINT_DRIVE_ID=yyy-yyy-yyy-yyy        # 04_IA library drive ID
MICROSOFT_GRAPH_TOKEN=eyJ0eXAi...          # Azure app Graph API token

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... (optional)
```

**How to get these:**

**Anthropic API Key:**
```bash
# Get from https://console.anthropic.com/account/keys
# Or run: echo $ANTHROPIC_API_KEY
```

**Supabase:**
```bash
# From Supabase dashboard:
# Settings → API → URL and anon key
supabase status  # If you have supabase-cli installed
```

**SharePoint (Microsoft Graph):**
```
1. Go to Azure Portal → App registrations
2. Create app "Maestro-Sync" with Graph API scopes:
   - Sites.ReadWrite.All (for writing agents to SP)
3. Get:
   - Site ID: Graph API → GET /sites/mn1970.sharepoint.com/sites/manta → id
   - Drive ID: Graph API → GET /sites/{siteId}/drives → id (look for "04_IA")
   - App credentials: Client ID + Secret (generate in Certificates section)
4. Get token: POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
```

**Test configuration:**
```bash
# Verify secrets are set correctly
gh secret list  # View all secrets
```

### 1.2 — Deploy Phase 1 Supabase Migrations (If Not Done)

```bash
# Apply existing migrations in order:
supabase migration list

supabase db push supabase/migrations/2026_07_25_add_pgvector_to_rag.sql
supabase db push supabase/migrations/2026_07_25_add_maestro_monitoring.sql
supabase db push supabase/migrations/2026_07_26_add_feedback_tables.sql

# Verify tables exist:
supabase db columns rag_chunks
supabase db columns maestro_user_feedback
supabase db columns maestro_routing_keywords
```

---

## PART 2: PHASE 2.4 Deployment (RAG Ingestion)

### 2.1 — Test RAG Ingestion Locally

```bash
# 1. Prepare source files
mkdir -p docs/rag-sources/{saneamento,energia,portos,aeroportos,barragens}/{T1-normas,T2-projetos,T3-estudos,T4-templates}

# 2. Add sample PDFs (get from SharePoint 02_Conhecimento/)
# E.g.: docs/rag-sources/saneamento/T1-normas/NBR_12211.pdf

# 3. Install dependencies
pip install pypdf anthropic supabase python-dotenv

# 4. Run dry-run test
python scripts/ingest_rag_batch.py \
  --segment saneamento \
  --tier T1 \
  --source docs/rag-sources/saneamento/T1-normas/ \
  --dry-run \
  --max-chunks 10

# Expected output:
# ✅ 10 chunks would be ingested
# Total tokens: ~5000
```

### 2.2 — Activate Monthly CI/CD

```bash
# 1. Push to main or feature branch
git push origin claude/evaluar-manta-maestro-hzx1oo

# 2. Verify workflow is available
gh workflow list | grep ingest-rag-monthly

# 3. Manually trigger for testing
gh workflow run ingest-rag-monthly.yml \
  -f segment=saneamento \
  -f tier=T1

# 4. Monitor execution
gh run list --workflow=ingest-rag-monthly.yml
gh run view <run-id> --log

# Expected on next scheduled run:
# - Fires on 1st of month at 2 AM UTC
# - Processes all 5 segments in parallel (max 2 concurrent)
# - Logs metrics to Supabase + Slack
```

### 2.3 — Create RAG Source Directories

```bash
# SharePoint → 02_Conhecimento/
# Download PDFs for each segment/tier combination

# Directory structure:
docs/rag-sources/
├── saneamento/
│   ├── T1-normas/       # SNIS, Lei 14.026, NBR 12211-12218
│   ├── T2-projetos/     # ETA/ETE design projects
│   ├── T3-estudos/      # PMSB, feasibility studies
│   └── T4-templates/    # RFP templates, editais
├── energia/
│   ├── T1-normas/       # ANEEL R1-R5, ONS procedure
│   ├── T2-projetos/     # LT designs, subestação projects
│   ├── T3-estudos/      # EPE studies, PDE
│   └── T4-templates/    # Leilão editais
# ... (portos, aeroportos, barragens)
```

---

## PART 3: PHASE 2.5 Deployment (SharePoint Sync)

### 3.1 — Test SharePoint Sync Locally

```bash
# 1. Test dry-run mode (no authentication needed)
python scripts/sync_agents_to_sharepoint.py --all --dry-run

# Expected output:
# [DRY RUN] Would sync agente-portos → 04_IA/.../agente-portos/SKILL.md
# [DRY RUN] Would sync agente-aeroportos → 04_IA/.../agente-aeroportos/SKILL.md
# ... etc

# 2. After secrets configured, test actual sync
export SHAREPOINT_SITE_ID="<from-secrets>"
export SHAREPOINT_DRIVE_ID="<from-secrets>"
export MICROSOFT_GRAPH_TOKEN="<from-secrets>"

python scripts/sync_agents_to_sharepoint.py --changed

# Expected:
# ✅ Uploaded agente-saneamento/SKILL.md
# Version: auto-sync from PR — 2026-07-26T...
```

### 3.2 — Activate Auto-Sync CI/CD

```bash
# 1. Push to main
git push origin claude/evaluar-manta-maestro-hzx1oo

# 2. Verify workflow
gh workflow list | grep sync-agents-to-sharepoint

# 3. Test manual trigger
gh workflow run sync-agents-to-sharepoint.yml \
  -f mode=all

# 4. On PR to main, workflow auto-runs on changed agents
# Check "Checks" tab in PR for sync status
```

---

## PART 4: PHASE 2.1 Deployment (Feedback Loop)

### 4.1 — Cowork Integration (Pending)

**Owner**: Cowork team + MN  
**Tasks**:
- [ ] Create "Was this agent correct?" button in Cowork UI
- [ ] Connect button to `process_routing_feedback()` function
- [ ] Add confidence scale (1-5) option
- [ ] Integrate with maestro_user_feedback table

**Implementation reference**:
```python
# When user clicks approval/rejection in Cowork:

from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# User approved:
supabase.table('maestro_user_feedback').insert({
    'prompt': original_query,
    'routed_agent': 'agente-saneamento',
    'correct_agent': 'agente-saneamento',  # user approved
    'confidence': 5,  # slider value (1-5)
    'approved': True,
    'timestamp': datetime.utcnow(),
    'session_id': session_id,
}).execute()
```

### 4.2 — Weekly Analysis Job

**Setup**:
```sql
-- Schedule weekly job in Supabase
-- Runs every Monday at 9 AM UTC

-- Call function:
SELECT * FROM analyze_feedback_and_recommend();

-- This generates:
-- 1. Approval rates per agent
-- 2. Keywords with low confidence
-- 3. Recommended adjustments
-- 4. GitHub issue creation (optional)
```

**Create GitHub issue from recommendations**:
```bash
# After weekly job runs, query results:
psql $DB_URL << "SQL"
SELECT
  agent_slug,
  approval_rate,
  recommended_action
FROM maestro_feedback_analysis
WHERE week = date_trunc('week', now())
ORDER BY approval_rate ASC;
SQL

# For agents with approval_rate < 85%, create GitHub issue:
gh issue create \
  --title "Routing improvement: ${agent} approval ${rate}%" \
  --body "Recommend boosting keywords: [list from feedback_analysis]"
```

---

## PART 5: PHASE 2.2 Deployment (Orchestrator)

### 5.1 — Implementation in manta-hub

**Owner**: Maestro team  
**Reference**: `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md`

**Steps**:
1. [ ] Create `manta-hub/maestro/orchestrator.py` using guide
2. [ ] Create test cases in `manta-hub/tests/test_orchestrator.py`
3. [ ] Integrate with maestro router:
   ```python
   # In maestro/router.py:
   from orchestrator import MaestroOrchestrator
   
   def route_and_respond(self, user_prompt):
       scores = self._score_agents(user_prompt)
       primary = max(scores, key=scores.get)
       secondary = max((s for a,s in scores.items() if a!=primary), default=0)
       
       if primary - secondary < 0.10:
           # AMBIGUOUS: orchestrate
           ...
   ```
4. [ ] Test with 5+ real ambiguous queries
5. [ ] Monitor orchestration rate (target: 5-10%)

---

## PART 6: PHASE 2.3 Deployment (Doc Auto-Classification)

### 6.1 — MCP Listener Setup (Pending)

**Owner**: Cowork team  
**Reference**: `docs/DOCUMENT-AUTO-CLASSIFICATION.md`

**Implementation**:
```python
# In Cowork listener:

@app.webhook('/sharepoint/on_document_uploaded')
async def handle_upload(event):
    # 1. Extract metadata from uploaded file
    metadata = DocumentClassifier.extract_metadata(file_path)
    
    # 2. Route through Maestro
    classification = DocumentClassifier.classify(metadata)
    
    # 3. Notify user in Cowork
    notification = {
        "title": f"📄 {filename}",
        "message": f"Classified as {classification.suggested_agent}",
        "actions": [
            {"label": "Concordar e mover", "action": "approve"},
            {"label": "Discordar", "action": "reject"},
            {"label": "Revisar manualmente", "action": "escalate"},
        ]
    }
    
    # 4. Wait for response
    response = await cowork.wait_for_response(notification)
    
    # 5. Move file + record feedback
    if response.action == "approve":
        sharepoint_move(file_path, response.suggested_folder)
        record_feedback(approved=True, agent=response.agent)
```

---

## Deployment Timeline

```
Week 1 (Jul 28 - Aug 02):
  ✅ Configure GitHub Secrets
  ✅ Deploy Phase 1 migrations (if needed)
  🔨 Test Phase 2.4 (RAG ingestion)
  🔨 Test Phase 2.5 (SharePoint sync)

Week 2 (Aug 05 - Aug 09):
  ✅ Activate Phase 2.4 monthly CI/CD
  ✅ Activate Phase 2.5 auto-sync CI/CD
  🔨 Cowork feedback button integration (2.1)
  🔨 Orchestrator implementation starts (2.2)

Weeks 3-4 (Aug 12 - Aug 26):
  🔨 Orchestrator testing + integration (2.2)
  🔨 Document auto-classification MCP listener (2.3)
  ✅ Weekly feedback analysis job (2.1)

By Aug 31:
  ✅ PHASE 2 Complete: All 5 workstreams operational
```

---

## Success Metrics & Monitoring

### Metrics Dashboard

```sql
-- Query to check Phase 2 health:

-- 2.1 Feedback: Approval rates
SELECT
  routed_agent,
  COUNT(*) as total_feedback,
  SUM(CASE WHEN approved THEN 1 ELSE 0 END) as approved,
  ROUND(100.0 * SUM(CASE WHEN approved THEN 1 ELSE 0 END) / COUNT(*), 1) as approval_rate
FROM maestro_user_feedback
WHERE created_at > now() - interval '7 days'
GROUP BY routed_agent
ORDER BY approval_rate DESC;

-- 2.2 Orchestration: Rate + quality
SELECT
  COUNT(*) as total_queries,
  SUM(CASE WHEN is_ambiguous THEN 1 ELSE 0 END) as ambiguous_queries,
  ROUND(100.0 * SUM(CASE WHEN is_ambiguous THEN 1 ELSE 0 END) / COUNT(*), 1) as orchestration_rate,
  AVG(CASE WHEN is_ambiguous THEN orchestrator_confidence ELSE NULL END) as avg_orchestration_confidence
FROM maestro_routing_trace
WHERE created_at > now() - interval '7 days';

-- 2.4 RAG: Ingestion metrics
SELECT
  collection_slug,
  COUNT(*) as chunk_count,
  SUM(CASE WHEN created_at > now() - interval '7 days' THEN 1 ELSE 0 END) as chunks_this_week
FROM rag_chunks
GROUP BY collection_slug
ORDER BY chunk_count DESC;

-- 2.5 SharePoint: Sync success
SELECT
  COUNT(*) as total_syncs,
  SUM(CASE WHEN status = 'synced' THEN 1 ELSE 0 END) as successful,
  ROUND(100.0 * SUM(CASE WHEN status = 'synced' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
FROM maestro_sharepoint_sync_log
WHERE synced_at > now() - interval '7 days';
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Feedback approval rate | < 80% | < 70% |
| Orchestration rate | > 15% | > 25% |
| Orchestrator confidence | < 0.70 | < 0.60 |
| RAG chunks per segment | < 100 | < 50 |
| SharePoint sync success | < 95% | < 80% |

---

## Rollback Plan

If issues arise:

**RAG Ingestion Issue**:
```bash
# Stop monthly workflow
gh workflow disable ingest-rag-monthly.yml

# Delete problematic chunks (if ingested incorrectly)
psql $DB_URL << "SQL"
DELETE FROM rag_chunks
WHERE created_at > '2026-08-01' AND collection_slug = 'saneamento';
SQL

# Re-run with dry-run to verify
python scripts/ingest_rag_batch.py --segment saneamento --dry-run
```

**SharePoint Sync Issue**:
```bash
# Stop auto-sync workflow
gh workflow disable sync-agents-to-sharepoint.yml

# Manually revert on SharePoint (version history)
# Or roll back agent .md files in git

# Re-enable with credentials fixed
gh workflow enable sync-agents-to-sharepoint.yml
```

**Feedback Loop Issue**:
```bash
# Disable feedback button in Cowork temporarily
# Keep metrics collection running
# Fix process_routing_feedback() function

# Re-enable with corrected logic
```

---

## Questions & Support

**RAG Ingestion Issues:**
- Contact: Claude Code team
- Docs: `docs/PHASE-2-ROADMAP.md` § 2.4
- Script: `scripts/ingest_rag_batch.py --help`

**SharePoint Sync Issues:**
- Contact: Claude Code team
- Docs: `docs/PHASE-2-ROADMAP.md` § 2.5
- Script: `scripts/sync_agents_to_sharepoint.py --help`
- Graph API: https://learn.microsoft.com/en-us/graph/api/driveitem-put-content

**Feedback Loop Issues:**
- Contact: Cowork team + MN
- Docs: `.claude/agents/maestro-orchestrator.md` (schema)
- Function: `maestro_user_feedback`, `process_routing_feedback()`

**Orchestrator Issues:**
- Contact: Maestro team (manta-hub)
- Docs: `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md`
- Reference: `tests/routing/test_multiagent_dispatch.md`

---

**Deployment Owner**: MN (DevOps)  
**Last Updated**: 2026-07-26  
**Status**: 🟢 READY FOR DEPLOYMENT
