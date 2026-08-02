# 🚀 Manta Maestro v5.0.1 — Deployment Runbook

**Version**: v5.0.1 (Unified)  
**Date**: 2026-07-31  
**Scope**: S12 (Óleo & Gás) + S13 (Edificações) production activation  
**Estimated Duration**: 30–45 minutes  
**Status**: ✅ Ready for production deployment

---

## Quick Start

```bash
# Make all scripts executable
chmod +x deploy/*.sh

# Execute complete deployment (all 5 phases orchestrated)
bash deploy/00-deploy-all.sh

# Or execute phases individually
bash deploy/01-supabase-migration.sh
bash deploy/02-sharepoint-setup.sh
bash deploy/03-agent-indexing.sh
bash deploy/04-smoke-tests.sh
bash deploy/05-notification.sh
```

---

## Deployment Phases

### Phase 1: Supabase Schema Migration (~2 min)
**Script**: `deploy/01-supabase-migration.sh`

**What it does**:
- Creates 2 RAG collections: `oleo-gas` (S12) and `edificacoes` (S13)
- Registers SharePoint routing rules
- Adds 17 Maestro routing keywords
- All operations are idempotent (safe to re-run)

**Prerequisites**:
- Supabase CLI installed, OR
- `SUPABASE_DB_URL` environment variable set, OR
- Manual dashboard access

**How it works**:
1. Validates migration file exists
2. Shows dry-run preview (if using CLI)
3. Prompts for confirmation before execution
4. Provides manual dashboard instructions as fallback

**Execution**:
```bash
# Option A: Via Supabase CLI (recommended)
supabase db push --remote --dry-run  # preview
supabase db push --remote            # apply

# Option B: Via psql and SUPABASE_DB_URL
psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql

# Option C: Script (handles all options automatically)
bash deploy/01-supabase-migration.sh
```

**Rollback** (if needed):
```sql
BEGIN;
DELETE FROM maestro_routing_keywords WHERE agent_slug IN ('agente-oleo-gas','agente-edificacoes');
DELETE FROM sp_agent_routing WHERE agent_slug IN ('agente-oleo-gas','agente-edificacoes');
DELETE FROM rag_collections WHERE slug IN ('oleo-gas','edificacoes');
COMMIT;
```

---

### Phase 2: SharePoint Folder Setup (~10 min)
**Script**: `deploy/02-sharepoint-setup.sh`

**What it does**:
- Creates folder structure in SharePoint
- Applies folder-level permissions
- Signals MCP for indexing start (~5 min sync delay)

**Prerequisites**:
- Direct access to Manta SharePoint site
- Permission to create folders under `03_Projetos/`
- Permission to set folder-level permissions

**Manual steps**:
1. Open Manta SharePoint site
2. Navigate to `03_Projetos/`
3. Create `OleoGas/` folder with subfolders:
   - `Projetos Ativos/`
   - `Referências (ANP, API, NFPA)/`
   - `Documentação Técnica/`
4. Create `Edificacoes/` folder with subfolders:
   - `Projetos Ativos/`
   - `Referências (NBR, LEED, BIM)/`
   - `Documentação Técnica/`
5. Set folder permissions to match S6–S10 pattern (read for respective agents)
6. Wait ~5 minutes for MCP automatic indexing

**Script interaction**:
- Provides step-by-step instructions
- Interactive verification checklist
- Tracks MCP indexing readiness

---

### Phase 3: Agent Indexing & MCP Sync (~5 min)
**Script**: `deploy/03-agent-indexing.sh`

**What it does**:
- Monitors automatic MCP sync of agent files
- Verifies files in `.claude/agents/` are synced to SharePoint
- Confirms YAML headers and formatting

**Prerequisites**:
- Phase 2 SharePoint folders already created
- Files present in `.claude/agents/`:
  - `agente-oleo-gas.md`
  - `agente-edificacoes.md`

**Automatic behavior**:
- Waits 5 minutes for MCP automatic indexing
- Verifies agent files synced to SharePoint Skills
- Tests YAML frontmatter validity

**Manual verification**:
After script completes, check SharePoint to confirm:
- `/Skills/Óleo & Gás/agente-oleo-gas.md` present
- `/Skills/Edificações/agente-edificacoes.md` present

---

### Phase 4: Smoke Tests & Validation (~15 min)
**Script**: `deploy/04-smoke-tests.sh`

**What it does**:
- 8 automated tests verify deployment artifacts
- Manual test prompts for hands-on validation
- Regression checks on existing agents (S1–S10)

**Automated tests**:
1. ✓ Verify routing keywords in CLAUDE.md
2. ✓ Verify agent files exist and are properly formatted
3. ✓ Verify RAG collections in migration
4. ✓ Verify SharePoint routing in migration
5. ✓ Verify no regressions in S1–S10
6. ✓ Verify Maestro keywords present (S12/S13)
7. ✓ Verify segment numbering consistency
8. ✓ Verify deployment documents complete

**Manual tests** (requires deployed infrastructure):
- Test 9: Maestro dispatch to S12 — query agente-oleo-gas with "gasoduto" keyword
- Test 10: Maestro dispatch to S13 — query agente-edificacoes with "data center" keyword
- Test 11: RAG query S12 — SELECT COUNT from manta_rag_chunks for collection='oleo-gas'
- Test 12: RAG query S13 — SELECT COUNT from manta_rag_chunks for collection='edificacoes'

**Pass criteria**:
- All 8 automated tests pass
- At least 2/4 manual tests pass
- No regressions detected in S1–S10

---

### Phase 5: Operational Hub Communication (~2 min)
**Script**: `deploy/05-notification.sh`

**What it does**:
- Posts announcement to #manta-maestro Slack channel
- Includes new segment details, keywords, and documentation links
- Notifies team of new capabilities

**Prerequisites**:
- Slack CLI installed, OR
- `SLACK_WEBHOOK_URL` environment variable set, OR
- Manual access to #manta-maestro channel

**Automatic posting**:
1. Detects Slack CLI availability
2. Attempts webhook if environment variable set
3. Falls back to manual instructions if needed

**Manual posting** (if script fallback):
1. Open Slack → #manta-maestro channel
2. Copy announcement text from script output
3. Paste and post to channel

---

## Complete Deployment Script

**File**: `deploy/00-deploy-all.sh`

Orchestrates all 5 phases with:
- Sequential execution
- Phase timing and duration tracking
- Summary report of pass/fail status
- Clear next steps if any phase fails

**Usage**:
```bash
bash deploy/00-deploy-all.sh
```

**Output**:
- Real-time progress for each phase
- Phase durations
- Pass/fail count
- Actionable summary
- Rollback guidance if needed

---

## Troubleshooting

### Phase 1: Supabase Migration Failed

**Symptoms**:
- Script says migration file not found
- Supabase CLI not available
- psql connection fails

**Resolution**:
1. Verify file exists: `ls supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql`
2. Install Supabase CLI: `brew install supabase/tap/supabase` (macOS)
3. Or set `SUPABASE_DB_URL`: `export SUPABASE_DB_URL="postgresql://..."`
4. Or use manual dashboard: copy SQL file content → Supabase dashboard → SQL Editor → Execute

---

### Phase 2: SharePoint Folders Not Created

**Symptoms**:
- Script reports manual execution required
- Folders don't appear in SharePoint

**Resolution**:
1. Verify you have write permission to `03_Projetos/`
2. Create folders using SharePoint UI if script cannot execute
3. Ensure folder names exactly match: `OleoGas` and `Edificacoes` (case-sensitive)
4. Set folder permissions to match S6–S10 pattern

---

### Phase 3: MCP Sync Not Completing

**Symptoms**:
- Script times out after 5 minutes
- Agent files don't appear in SharePoint Skills

**Resolution**:
1. Manual check: navigate to SharePoint `/Skills/` folder
2. Wait additional 5–10 minutes (MCP sync can be delayed)
3. Verify `.claude/agents/` files exist locally with correct names
4. Manually upload files if MCP sync fails

---

### Phase 4: Smoke Tests Failing

**Symptoms**:
- Automated tests report failures
- Manual tests cannot reach agents

**Resolution**:
1. Review test output for specific failures
2. Verify Phase 1–3 completed successfully
3. Check Maestro logs for S12/S13 dispatch errors
4. Confirm RAG collections created (check `manta_rag_chunks` table)

---

### Phase 5: Slack Notification Not Posting

**Symptoms**:
- Script says post failed
- Announcement not visible in #manta-maestro

**Resolution**:
1. If script fallback: manually copy announcement text
2. Post to #manta-maestro manually
3. Or set `SLACK_WEBHOOK_URL` environment variable for automated posting
4. Install Slack CLI: `brew install slack-cli` (macOS)

---

## Post-Deployment Monitoring

**First 24 hours** — watch these metrics:

| Metric | Target | Check Location |
|--------|--------|-----------------|
| Maestro S12 dispatch success rate | 100% | Maestro logs |
| Maestro S13 dispatch success rate | 100% | Maestro logs |
| RAG latency (new collections) | <500ms | APM/observability dashboard |
| SharePoint indexing confirmation | ✓ MCP sync | MCP logs |
| S1–S10 regression | 0 failures | Maestro logs, smoke tests |

**Log locations**:
- Maestro routing logs: CloudWatch/structured logs for dispatcher
- RAG performance: APM dashboard for query latencies
- SharePoint MCP: sync logs in Azure or MCP agent system
- Regressions: automated monitoring or nightly test suite

---

## Rollback Plan

If any phase fails unrecoverably:

**Step 1**: Stop current phase and revert Supabase (if Phase 1 completed)
```sql
BEGIN;
DELETE FROM maestro_routing_keywords WHERE agent_slug IN ('agente-oleo-gas','agente-edificacoes');
DELETE FROM sp_agent_routing WHERE agent_slug IN ('agente-oleo-gas','agente-edificacoes');
DELETE FROM rag_collections WHERE slug IN ('oleo-gas','edificacoes');
COMMIT;
```

**Step 2**: Delete SharePoint folders (if Phase 2 completed)
- Navigate to `03_Projetos/OleoGas/` → Delete
- Navigate to `03_Projetos/Edificacoes/` → Delete
- Wait for MCP sync (~5 min)

**Step 3**: Notify #manta-maestro of rollback
```
⚠️  Deployment rollback: S12/S13 production activation has been reverted.
Reason: [specific phase failure]
Next attempt: [date/time]
Questions: @architect
```

**Estimated rollback time**: 5–10 minutes

---

## Success Criteria

Deployment is **GO** when:
- ✅ Phase 1 (Supabase): migration applied successfully
- ✅ Phase 2 (SharePoint): folders created and permissions verified
- ✅ Phase 3 (MCP Sync): agent files synced to SharePoint
- ✅ Phase 4 (Tests): all automated tests pass
- ✅ Phase 5 (Notify): announcement posted to #manta-maestro

**Additional verification** (post-deployment):
- ✅ Maestro successfully routes S12 queries to agente-oleo-gas
- ✅ Maestro successfully routes S13 queries to agente-edificacoes
- ✅ RAG retrieval works for both new collections
- ✅ No regressions in existing S1–S10 agents

---

## Support & Escalation

| Issue | Contact | Docs |
|-------|---------|------|
| Architecture questions | @architect | CLAUDE.md v5.0.1 |
| Supabase migration errors | @db-admin | docs/SEGMENTOS-S12-S13-DECISION.md |
| SharePoint permission issues | @sharepoint-admin | docs/DEPLOY-CHECKLIST-v5.0.md |
| Maestro routing failures | @architect-ia | docs/ROUTING-TROUBLESHOOTING.md |
| RAG performance issues | @ml-team | docs/EMBEDDER-DECISION.md |

---

## Deployment Checklist

**Before deployment**:
- [ ] PR #47 merged to main
- [ ] All phases scripts in `deploy/` directory
- [ ] Migration file present: `supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql`
- [ ] Agent files present: `.claude/agents/agente-oleo-gas.md`, `.claude/agents/agente-edificacoes.md`
- [ ] SharePoint access verified
- [ ] Supabase access verified (CLI or DB URL)
- [ ] Slack posting capability (CLI or webhook)

**During deployment**:
- [ ] Execute Phase 1 (Supabase) — monitor for errors
- [ ] Execute Phase 2 (SharePoint) — verify folder creation
- [ ] Wait Phase 3 (MCP Sync) — monitor sync completion
- [ ] Execute Phase 4 (Tests) — verify all tests pass
- [ ] Execute Phase 5 (Notify) — confirm announcement posted

**After deployment**:
- [ ] Monitor Maestro dispatch logs (24 hours)
- [ ] Verify S12/S13 routing success rates
- [ ] Confirm RAG latency <500ms
- [ ] Check SharePoint indexing status
- [ ] Validate no regressions in S1–S10

---

**Version**: v5.0.1  
**Last Updated**: 2026-07-31  
**Status**: ✅ Ready for production
