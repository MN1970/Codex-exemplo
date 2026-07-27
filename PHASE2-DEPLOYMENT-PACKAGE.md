# Phase 2 Complete Deployment Package

**Version:** 1.0  
**Created:** 2026-07-27  
**Status:** Ready for Implementation  
**Owner:** DevOps & Maestro Teams

---

## Overview

This deployment package contains all scripts, runbooks, and configurations needed for Phase 2 of the Manta Maestro evolution:

- **Phase 2.4:** RAG Batch Ingestion (1,300+ documents, 4,290+ chunks, vector embeddings)
- **Phase 2.5:** SharePoint Sync Automation (agent .md → SKILL.md synchronization)

**Scope:** All 5 new vertical agents (S6-S10: Portos, Aeroportos, Saneamento, Energia, Barragens)

**Timeline:** ~2 weeks execution (5 days Phase 2.4, 5 days Phase 2.5, 4 days validation)

**Success Criteria:**
- RAG: 4,290 chunks processed, <500ms query latency, ≥85% top-1 relevance
- SharePoint: 15 agents synced, <2 min latency, 0 critical conflicts
- System: ≥99.5% uptime, <$200 total cost

---

## Package Contents

### 1. Configuration Scripts

#### `.github/workflows/secrets-config.sh` (1,100 lines)
GitHub Actions secrets configuration wizard.

**Features:**
- Interactive setup wizard for all Phase 2 secrets
- Verification of existing secrets
- Template generation for manual entry
- Credential export (with warnings)
- Color-coded output and logging

**Secrets configured (20 total):**
- Anthropic API keys
- Supabase project credentials
- GCP service accounts
- Microsoft Graph authentication
- GitHub access tokens
- CloudWatch configuration
- Monitoring & alerting endpoints

**Usage:**
```bash
# Interactive setup
.github/workflows/secrets-config.sh --interactive

# Verify existing secrets
.github/workflows/secrets-config.sh --verify

# Generate template
.github/workflows/secrets-config.sh --template > secrets.env.template

# List all required secrets
.github/workflows/secrets-config.sh --list
```

**Execution Time:** ~5 minutes interactive, 30 seconds verification

---

### 2. Database Migration Scripts

#### `scripts/deploy_migrations.sh` (850 lines)
Supabase database schema migration runner.

**Features:**
- Pre-flight checks (tools, connections, permissions)
- Automatic migration generation for Phase 2 schema
- Dry-run validation before execution
- Full rollback capability
- Migration status monitoring
- Comprehensive logging

**Migrations included:**
1. `001_feedback_loop_schema.sql` - Feedback tracking tables (feedback_submissions, metrics view)
2. `002_rag_vector_schema.sql` - RAG vector storage (rag_documents, query cache, ingestion status)
3. `003_orchestrator_schema.sql` - Multi-agent orchestration (orchestration_tasks, agent_capabilities)
4. `004_document_classifier_schema.sql` - Document classification (classified_documents)
5. `005_sharepoint_sync_schema.sql` - SharePoint sync tracking (sharepoint_sync_log, skill_versions)

**Database Objects Created:**
- 8 production tables
- 2 views (feedback_metrics)
- 12+ indexes (for performance)
- Role-based access control

**Usage:**
```bash
# Dry-run validation
DRY_RUN=true scripts/deploy_migrations.sh

# Execute migrations
scripts/deploy_migrations.sh

# Check status
scripts/deploy_migrations.sh --status

# Rollback if needed
scripts/deploy_migrations.sh --rollback
```

**Execution Time:** ~5 minutes (migrations) + 2 minutes (validation)

---

### 3. Staging Validation Script

#### `scripts/validate_phase2_staging.sh` (650 lines)
Comprehensive staging validation suite for all Phase 2 components.

**Features:**
- Tests for all 5 Phase 2 components (feedback loop, orchestrator, classifier, RAG, SharePoint)
- Integration testing (end-to-end workflow)
- Performance testing (latency, throughput)
- SLA validation
- JSON report generation
- Color-coded test results

**Test Coverage:**
| Component | Tests | Coverage |
|-----------|-------|----------|
| Feedback Loop | 5 | Database, endpoints, metrics |
| Orchestrator | 3 | Multi-agent dispatch, capabilities |
| Classifier | 4 | Document classification, accuracy |
| RAG Ingestion | 6 | Collections, search, performance |
| SharePoint Sync | 5 | Auth, sync tables, version tracking |
| Integration | 4 | Full workflow, end-to-end |
| Performance | 7 | Latency, throughput, SLAs |

**Usage:**
```bash
# Quick validation (feedback, orchestrator, classifier)
scripts/validate_phase2_staging.sh --quick

# Full validation (all components + performance)
scripts/validate_phase2_staging.sh --full

# View JSON report
scripts/validate_phase2_staging.sh --report

# Generate HTML report
scripts/validate_phase2_staging.sh --full > report.html
```

**Execution Time:** 2 minutes (--quick), 10 minutes (--full)

**Output:**
```json
{
  "summary": {
    "total_tests": 34,
    "passed": 33,
    "failed": 1,
    "pass_rate_percent": 97
  },
  "components": {
    "feedback_loop": "operational",
    "orchestrator": "operational",
    "classifier": "operational",
    "rag_ingestion": "operational",
    "sharepoint_sync": "operational"
  }
}
```

---

### 4. Production Deployment Runbook

#### `docs/PHASE2-DEPLOYMENT-RUNBOOK.md` (1,200 lines)
Comprehensive step-by-step deployment guide.

**Contents:**

**Section 1: Pre-Deployment Checklist**
- Infrastructure readiness (Supabase, Anthropic, GCP, Microsoft Graph, CloudWatch)
- Data readiness (documents prepared, validated)
- Team readiness (training, schedules)
- Backup & disaster recovery plan

**Section 2: Phase 2.4 - RAG Batch Ingestion**
- Step 1: Database schema migration (5 min)
- Step 2: Embedding model configuration (10 min)
- Step 3: Document preparation & chunking (2 hours)
- Step 4: Batch ingestion & embedding (4 hours)
- Step 5: Quality validation (1 hour)

Detailed instructions for:
- Running migrations with validation
- Configuring embedding providers (Anthropic vs GCP)
- Document chunking pipeline with configuration
- Monitoring ingestion progress
- Quality assurance testing (relevance, latency, cost)

**Section 3: Phase 2.5 - SharePoint Sync Automation**
- Step 1: Microsoft Graph API configuration (20 min)
- Step 2: Sync engine implementation (2 hours)
- Step 3: Staging validation (1 hour)
- Step 4: Production deployment (30 min)
- Step 5: Sync monitoring & optimization (ongoing)

Detailed instructions for:
- Testing Graph API authentication
- Sync dry-run with diff preview
- Conflict resolution strategies
- Service deployment and monitoring
- Database sync logging

**Section 4: Rollback Procedures**
- Phase 2.4 rollback (RAG) - 15 minutes
- Phase 2.5 rollback (SharePoint) - 10 minutes
- Full Phase 2 rollback - 30 minutes

**Section 5: Monitoring & Post-Deployment**
- Real-time dashboard (CloudWatch)
- Alert thresholds
- Daily health checks (first 5 days)
- Success criteria & sign-off

**Usage:**
```
Main deployment guide: Start here
├── Pre-deployment checklist → Execute all items
├── Phase 2.4 steps → Execute in order with validation
├── Phase 2.5 steps → Execute in order with testing
├── Rollback procedures → Reference only, execute if needed
└── Post-deployment → Follow for 30 days
```

**Execution Stages:**
1. Pre-deployment (1 day): Infrastructure setup, team prep
2. Staging validation (2 days): Test migrations, pipelines in non-prod
3. Phase 2.4 deployment (5 days): RAG ingestion, vector setup
4. Phase 2.5 deployment (5 days): SharePoint sync, automation
5. Stabilization (4 days): Monitoring, tuning, signoff

---

### 5. Troubleshooting Guide

#### `docs/PHASE2-DEPLOYMENT-TROUBLESHOOTING.md` (900 lines)
Comprehensive troubleshooting and diagnosis guide.

**Structure:**

**Quick Diagnosis Matrix**
- 9 common symptoms → root causes → solutions
- Lookup table for rapid triage

**Phase 2.4 Issues (RAG Ingestion)**

1. Vector search returns irrelevant results
   - Symptoms, root causes, diagnosis steps
   - Solutions: re-embedding, index rebuilding, rechunking

2. Ingestion stops or fails
   - Network timeouts, database issues, chunk validation
   - Solutions: increase timeouts, test connections, resume ingestion

3. High embedding costs
   - Duplicate chunks, incorrect retry logic, wrong models
   - Solutions: deduplication, fix retry strategy, cost tracking

4. Vector search slow (>500ms)
   - Poor index parameters, fragmentation, network issues
   - Solutions: increase nprobes, rebuild index, optimize queries

**Phase 2.5 Issues (SharePoint Sync)**

1. Sync hangs or times out
   - Expired tokens, rate limits, connectivity issues
   - Solutions: refresh tokens, check rate limits, increase timeouts

2. Sync conflicts
   - Simultaneous edits, race conditions, version mismatches
   - Solutions: conflict resolution strategies (GitHub/SharePoint priority), manual merge

3. Files not syncing
   - Service not running, permissions issues, path problems
   - Solutions: restart service, check permissions, verify paths, force re-sync

**System-Wide Issues**

1. Database connection pooling exhausted
   - Too many connections, stale connections, pool misconfigured
   - Solution: kill idle connections, increase pool size

2. Out of memory
   - Batch size too large, file loading, cache issues
   - Solution: reduce batch size, streaming mode, clear cache

**Escalation Path**
- Level 1: System admin (restarts, logs, endpoints)
- Level 2: DevOps lead (migrations, APIs, infrastructure)
- Level 3: Architect (schema design, performance, rollbacks)
- Level 4: Executive (SLA violations, costs, continuity)

**Appendix: Useful Commands**
- 15+ database queries for diagnosis
- CloudWatch monitoring commands
- Log analysis techniques
- Cleanup & maintenance procedures

---

### 6. CloudWatch Monitoring Setup

#### `infra/monitoring/cloudwatch-setup.sh` (900 lines)
AWS CloudWatch monitoring and alerting configuration.

**Features:**
- Automatic log group creation (6 groups)
- CloudWatch dashboard with 6 widget panels
- 6 metric alarms with intelligent thresholds
- 30+ CloudWatch Insights query templates
- Python metrics publisher library
- SNS notifications for critical alerts

**Log Groups Created:**
```
/maestro/phase2                    (main)
/maestro/phase2/rag-ingestion      (RAG pipeline)
/maestro/phase2/orchestrator       (multi-agent dispatch)
/maestro/phase2/classifier         (document classification)
/maestro/phase2/sharepoint-sync    (SharePoint automation)
/maestro/phase2/feedback-loop      (feedback tracking)
```

**Dashboard Panels:**
1. RAG Search Latency (avg, p95, max)
2. RAG Ingestion Progress (chunks, embeddings, vectors)
3. Feedback Loop & Routing (submissions, accuracy, ambiguous queries)
4. SharePoint Synchronization (latency, files synced, conflicts)
5. Error Rate & Logs (application errors, system logs)
6. Lambda Functions (if using serverless components)

**Alarms (6 total):**
| Alarm | Metric | Threshold | Action |
|-------|--------|-----------|--------|
| maestro-rag-latency-high | RAGSearchLatency | >500ms | Page engineer |
| maestro-rag-ingestion-failures | FailureRate | >5% | Page engineer |
| maestro-sharepoint-sync-failures | FailureCount | ≥3 consecutive | Investigate |
| maestro-api-error-rate-high | ErrorRate | >5% | Investigate |
| maestro-vector-chunks-low | ChunkCount | <4000 | Verify status |
| maestro-feedback-loop-inactive | Submissions | 0 in 1h | Check service |

**CloudWatch Insights Queries (30+):**
- RAG ingestion performance
- Vector search latency distribution
- SharePoint sync success rates
- Feedback accuracy by agent
- API error breakdown
- System health overview
- Cost tracking by service

**Usage:**
```bash
# Full setup (all components)
infra/monitoring/cloudwatch-setup.sh --all

# Just create log groups
infra/monitoring/cloudwatch-setup.sh --logs

# Create dashboard only
infra/monitoring/cloudwatch-setup.sh --dashboards

# Setup alarms and notifications
ALERT_EMAIL=ops@mantaassociados.com \
  infra/monitoring/cloudwatch-setup.sh --alarms

# Validate configuration
infra/monitoring/cloudwatch-setup.sh --validate
```

**Execution Time:** 3 minutes (full setup)

**Python Metrics Publisher:**
```python
from publish_cloudwatch_metrics import CloudWatchMetricsPublisher

publisher = CloudWatchMetricsPublisher(
    namespace="Maestro/Phase2",
    region="us-east-1"
)

# Publish metrics
publisher.put_rag_metrics(
    chunks_processed=100,
    latency_ms=145.3,
    success=True,
    collection="saneamento"
)

publisher.put_sync_metrics(
    latency_ms=45000,
    files_synced=15,
    conflicts=0
)

publisher.put_feedback_metrics(
    submissions=12,
    accuracy=0.92,
    agent="agente-saneamento"
)
```

---

## Deployment Workflow

### Phase 1: Pre-Deployment (Day 1)

**Morning:**
1. Execute pre-deployment checklist (docs/PHASE2-DEPLOYMENT-RUNBOOK.md → Section 1)
2. Run secrets configuration: `.github/workflows/secrets-config.sh --interactive`
3. Verify all environment variables set
4. Ensure team is trained and prepared

**Afternoon:**
1. Create CloudWatch monitoring: `infra/monitoring/cloudwatch-setup.sh --all`
2. Create SNS notifications with alert email
3. Test backup & disaster recovery procedures
4. Conduct team standby meeting

### Phase 2: Staging Validation (Days 2-3)

**Day 2:**
1. Run staging validation: `scripts/validate_phase2_staging.sh --full`
2. All tests pass (≥90% pass rate)
3. Review and fix any failing tests
4. Generate report and review with team

**Day 3:**
1. Conduct load testing (optional, for high-volume scenarios)
2. Verify all alerts are functional
3. Final sign-off from all teams
4. Schedule production deployment window

### Phase 3: Phase 2.4 Deployment (Days 4-8)

**Day 4: Database & Preparation**
```bash
# Step 1: Run migrations (5 min)
scripts/deploy_migrations.sh --dry-run   # Validate
scripts/deploy_migrations.sh             # Execute

# Step 2: Configure embeddings (10 min)
# Follow docs/PHASE2-DEPLOYMENT-RUNBOOK.md → Section 2 → Step 2

# Step 3: Prepare documents (2 hours)
python3 scripts/chunk_documents.py \
  --input-dir docs/rag \
  --output-dir chunks \
  --chunk-size 500 \
  --overlap 100
```

**Day 5-7: Ingestion & Quality Assurance**
```bash
# Step 4: Batch ingestion (4 hours)
python3 scripts/ingest_rag_documents.py \
  --input-dir chunks/ \
  --batch-size 50 \
  --max-workers 10

# Step 5: Quality validation (1 hour)
python3 scripts/test_rag_quality.py \
  --test-queries tests/rag_test_queries.jsonl \
  --top-k 5
```

**Day 8: Validation & Stabilization**
```bash
# Re-run validation
scripts/validate_phase2_staging.sh --full

# Monitor metrics in CloudWatch
# Review logs for any issues
# Sign-off: Phase 2.4 complete
```

### Phase 4: Phase 2.5 Deployment (Days 9-13)

**Day 9-10: Microsoft Graph Setup & Testing**
```bash
# Step 1: Configure Graph API (20 min)
python3 scripts/test_graph_auth.py \
  --tenant-id "$MICROSOFT_TENANT_ID" \
  --client-id "$MICROSOFT_CLIENT_ID" \
  --client-secret "$MICROSOFT_CLIENT_SECRET"

# Step 2: Test sync in dry-run (1 hour)
python3 scripts/sharepoint_sync_engine.py \
  --config configs/sharepoint_sync_config.json \
  --dry-run \
  --show-diffs
```

**Day 11-12: Staging & Production Deployment**
```bash
# Step 3: Staging validation (1 hour)
# (if staging available)

# Step 4: Deploy to production (30 min)
python3 scripts/sharepoint_sync_engine.py \
  --config configs/sharepoint_sync_config.json \
  --run-daemon \
  --polling-interval 30
```

**Day 13: Monitoring & Stabilization**
```bash
# Step 5: Monitor sync logs
tail -f /var/log/maestro/sharepoint_sync.log

# Verify files in SharePoint
# Check database sync_log table
# Address any conflicts
# Sign-off: Phase 2.5 complete
```

### Phase 5: Stabilization & Sign-Off (Days 14-18)

**Ongoing (24/7 monitoring):**
- CloudWatch dashboard → Real-time metrics
- Alarms → Immediate notification of issues
- Daily health checks → First 5 days
- Weekly checks → Next 4 weeks

**Success Criteria Validation:**
- [ ] RAG: 4,290 chunks processed
- [ ] RAG: <500ms p95 latency
- [ ] RAG: ≥85% top-1 relevance
- [ ] SharePoint: 15 agents synced
- [ ] SharePoint: <2 min sync latency
- [ ] SharePoint: 0 critical conflicts
- [ ] System: ≥99.5% uptime
- [ ] Cost: <$200 total

**Final Sign-Off:**
- [ ] DevOps Lead - Infrastructure OK
- [ ] Maestro Lead - Routing/Orchestration OK
- [ ] Data Lead - RAG/Embeddings OK
- [ ] CTO/Architect - Architecture OK

---

## File Locations & Access

### Scripts (Executable)

```
.github/workflows/
├── secrets-config.sh                    [Secrets setup wizard]

scripts/
├── deploy_migrations.sh                 [Database migrations]
├── validate_phase2_staging.sh           [Staging validation]
└── publish_cloudwatch_metrics.py        [Metrics publisher]

infra/monitoring/
├── cloudwatch-setup.sh                  [CloudWatch setup]
├── insights-queries.md                  [30+ query templates]
└── dashboards/                          [Dashboard definitions]
```

### Documentation (Reference)

```
docs/
├── PHASE2-DEPLOYMENT-RUNBOOK.md         [Main deployment guide]
├── PHASE2-DEPLOYMENT-TROUBLESHOOTING.md [Troubleshooting guide]
└── PHASE4-ECOSYSTEM-ROADMAP-COMPLETE.md [Future phases]

./
├── PHASE2-DEPLOYMENT-PACKAGE.md         [This document]
├── CLAUDE.md                            [Master registry]
└── PHASE-2-BRANCH-README.md            [Branch overview]
```

### Configurations

```
configs/
├── embedding_config.json                [Embedding model settings]
├── sharepoint_sync_config.json          [SharePoint settings]
└── monitoring_config.json               [CloudWatch settings]

supabase/
└── migrations/                          [SQL migration files]
    ├── 001_feedback_loop_schema.sql
    ├── 002_rag_vector_schema.sql
    ├── 003_orchestrator_schema.sql
    ├── 004_document_classifier_schema.sql
    └── 005_sharepoint_sync_schema.sql
```

---

## Key Metrics & Success Criteria

### Phase 2.4 (RAG Ingestion)

| Metric | Target | Status | Notes |
|--------|--------|--------|-------|
| Documents ingested | 1,300 | - | 5 new vertical agents |
| Chunks processed | 4,290 | - | Across all collections |
| Vector embeddings | 100% | - | pgvector storage |
| Search latency (p95) | <500ms | - | Cosine similarity |
| Top-1 relevance | ≥85% | - | Quality validation |
| Embedding cost | <$100 | - | ~1.3M tokens |
| Uptime | ≥99.5% | - | During deployment |

### Phase 2.5 (SharePoint Sync)

| Metric | Target | Status | Notes |
|--------|--------|--------|-------|
| Agents synced | 15 | - | All .md → SKILL.md |
| Sync latency | <2 min | - | File modification to SharePoint |
| Sync accuracy | 100% | - | No data corruption |
| Conflict count | 0 critical | - | Auto-resolved minor conflicts |
| Service uptime | ≥99.5% | - | During deployment |
| Folder structure | 5 segments | - | S6-S10 in SharePoint |

### Overall System

| Metric | Target | Status | Notes |
|--------|--------|--------|-------|
| Feedback submissions | ≥20/week | - | Routing improvement input |
| API availability | ≥99.5% | - | During deployment window |
| Total cost | <$200 | - | RAG + SharePoint |
| Database size | ~2GB | - | 4,290 chunks + metadata |
| Team satisfaction | ≥4/5 | - | Post-deployment survey |

---

## Support & Escalation

### Primary Contacts

| Role | Name | Email | Slack |
|------|------|-------|-------|
| DevOps Lead | [TBD] | [TBD] | @devops-lead |
| Maestro Lead | [TBD] | [TBD] | @maestro-lead |
| Data Lead | [TBD] | [TBD] | @data-lead |
| On-Call | [TBD] | maestro-on-call@mantaassociados.com | #maestro-deployment |

### Escalation Matrix

**Issue Type → Escalation Path**

- **Latency issues** → Level 1 (check config) → Level 2 (tune) → Level 3 (architect review)
- **Data issues** → Level 1 (diagnose) → Level 2 (fix) → Level 3 (design review)
- **Cost overruns** → Level 2 (optimize) → Level 3 (review) → Level 4 (decision)
- **Downtime** → Level 1 (restart) → Level 2 (investigate) → Level 3 (incident response)

---

## Next Steps

### Immediate (Before Phase 2 Start)

1. **Assign team members** to each deployment phase
2. **Schedule training sessions** using docs/PHASE2-DEPLOYMENT-RUNBOOK.md
3. **Set up infrastructure** (Supabase, GCP, Microsoft Graph, CloudWatch)
4. **Prepare documents** (organize RAG source files by collection)
5. **Conduct pre-deployment meeting** with all teams

### During Phase 2

1. **Follow deployment workflow** (execute scripts in order)
2. **Run validation checks** after each major step
3. **Monitor metrics** via CloudWatch dashboard
4. **Address issues** using troubleshooting guide
5. **Update team** with daily progress

### After Phase 2

1. **Conduct post-deployment review** with all teams
2. **Optimize performance** based on metrics (first 5 days)
3. **Train operations team** on monitoring and maintenance
4. **Plan Phase 3** (Public APIs, Regulatory Webhooks)

---

## References

### Internal Documents
- `CLAUDE.md` - Master agent registry and Phase roadmap
- `PHASE-2-BRANCH-README.md` - Branch overview and structure
- `docs/PHASE2-DEPLOYMENT-RUNBOOK.md` - Detailed deployment guide
- `docs/PHASE2-DEPLOYMENT-TROUBLESHOOTING.md` - Issue resolution
- `docs/COMPREHENSIVE-TEST-SUITE.md` - Test artifacts and scenarios

### External Resources
- Anthropic Docs: https://docs.anthropic.com/
- Supabase Docs: https://supabase.com/docs/
- Microsoft Graph: https://learn.microsoft.com/en-us/graph/
- AWS CloudWatch: https://docs.aws.amazon.com/cloudwatch/

---

## Document Info

**Package Version:** 1.0  
**Created:** 2026-07-27  
**Updated:** 2026-07-27  
**Owner:** DevOps & Maestro Teams  
**Status:** Ready for Implementation  
**Last Review:** 2026-07-27

**Checklist for Deployment Lead:**
- [ ] Read this entire document
- [ ] Review PHASE2-DEPLOYMENT-RUNBOOK.md
- [ ] Review PHASE2-DEPLOYMENT-TROUBLESHOOTING.md
- [ ] Test all scripts in staging environment
- [ ] Confirm all team members have access
- [ ] Verify all infrastructure prerequisites
- [ ] Schedule deployment window with stakeholders
- [ ] Conduct team briefing 1 day before start
- [ ] Begin Phase 1 (Pre-Deployment)

---

**Questions?** Contact maestro@mantaassociados.com or post in #maestro-deployment Slack channel.

---

## Appendix: Quick Reference Cards

### Quick Commands

```bash
# Secrets setup
.github/workflows/secrets-config.sh --interactive

# Database migration
scripts/deploy_migrations.sh --dry-run && scripts/deploy_migrations.sh

# Validation
scripts/validate_phase2_staging.sh --full

# CloudWatch setup
infra/monitoring/cloudwatch-setup.sh --all

# Monitor logs
tail -f /var/log/maestro/phase2.log

# Troubleshoot
# See: docs/PHASE2-DEPLOYMENT-TROUBLESHOOTING.md
```

### Environment Variables Required

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export SUPABASE_PROJECT_URL="https://xxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="sbp_..."
export MICROSOFT_TENANT_ID="..."
export MICROSOFT_CLIENT_ID="..."
export MICROSOFT_CLIENT_SECRET="..."
export SHAREPOINT_SITE_URL="..."
export AWS_REGION="us-east-1"
export GITHUB_PAT="ghp_..."
```

### Deployment Phases Summary

| Phase | Duration | Key Steps | Success Criteria |
|-------|----------|-----------|------------------|
| Pre-Deployment | 1 day | Checklist, secrets, infrastructure | All items checked |
| Staging Validation | 2 days | Run tests, fix issues, sign-off | ≥90% pass rate |
| Phase 2.4 (RAG) | 5 days | Migrations, chunking, ingestion | 4,290 chunks, <500ms |
| Phase 2.5 (SharePoint) | 5 days | Graph setup, sync, automation | 15 files, <2 min |
| Stabilization | 4 days | Monitoring, tuning, sign-off | All SLAs met |

---

**END OF DEPLOYMENT PACKAGE**

For updates, contact: maestro@mantaassociados.com
