# Manta Maestro — Training Guide (DevOps & Data Teams)

**Audience:** DevOps/SRE engineers operating Maestro infrastructure, and the
Data Team maintaining the RAG pipeline and routing feedback loop.
**Scope:** v4.2 (20 agents, 3 eixos — see `CLAUDE.md`).
**Companion docs:** `docs/TRAINING-GUIDE-MAESTRO-TEAM.md` (routing engine
internals), `docs/MONITORING-MAESTRO.md` (SQL-level metrics/alerting).

---

## Table of Contents

**Part A — DevOps**
1. [Deployment Automation](#a1-deployment-automation)
   - 1.1 [GitHub Actions workflows](#a11-github-actions-workflows)
   - 1.2 [Supabase migrations](#a12-supabase-migrations)
   - 1.3 [Kubernetes / Cloud Run deployment](#a13-kubernetes--cloud-run-deployment)
   - 1.4 [Monitoring & alerting setup](#a14-monitoring--alerting-setup)
2. [Infrastructure Scaling](#a2-infrastructure-scaling)
   - 2.1 [Capacity planning](#a21-capacity-planning)
   - 2.2 [Auto-scaling rules](#a22-auto-scaling-rules)
   - 2.3 [Cost optimization](#a23-cost-optimization)
3. [Disaster Recovery](#a3-disaster-recovery)
   - 3.1 [Backup strategy](#a31-backup-strategy)
   - 3.2 [Failover procedures](#a32-failover-procedures)
   - 3.3 [RTO/RPO targets](#a33-rtorpo-targets)

**Part B — Data Team**
1. [RAG Pipeline](#b1-rag-pipeline)
   - 1.1 [Document ingestion](#b11-document-ingestion)
   - 1.2 [Embedding generation](#b12-embedding-generation)
   - 1.3 [Vector search](#b13-vector-search)
   - 1.4 [Quality monitoring](#b14-quality-monitoring)
2. [Feedback Loop](#b2-feedback-loop)
   - 2.1 [Collecting feedback](#b21-collecting-feedback)
   - 2.2 [Weekly analysis](#b22-weekly-analysis)
   - 2.3 [A/B testing](#b23-ab-testing)
   - 2.4 [Continuous improvement](#b24-continuous-improvement)

**Appendices**
- [File manifest](#appendix-file-manifest)
- [Quick-reference checklists](#appendix-quick-reference-checklists)
- [Troubleshooting](#appendix-troubleshooting)

---

# Part A — DevOps

## A1. Deployment Automation

### A1.1 GitHub Actions workflows

Maestro's CI/CD lives in `.github/workflows/`. Three workflows already handle
recurring jobs; a fourth (`deploy-maestro.yml`) covers the full
trigger → build → test → deploy lifecycle for the router service:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test-maestro-routing.yml` | push/PR touching `CLAUDE.md`, `.claude/agents/**` | Runs `scripts/test_routing.py` against `tests/comprehensive-test-suite.json` |
| `ingest-rag-monthly.yml` | cron `0 2 1 * *` + manual dispatch | Batch RAG ingestion per segment (matrix over saneamento/energia/portos/aeroportos/barragens) |
| `sync-agents-to-sharepoint.yml` | push to agent defs | Mirrors `.claude/agents/*.md` and SKILL.md to SharePoint |
| `deploy-maestro.yml` (**new**) | push to `main` (manta-hub/**, supabase/migrations/**, infra/**) + manual dispatch | Build → test → apply migrations → canary deploy → promote |

**`deploy-maestro.yml` stage breakdown** (`.github/workflows/deploy-maestro.yml`):

```
build              → docker build/push, tag = short SHA
  └─ test          → routing suite + `supabase db push --dry-run` + `supabase db lint`
       └─ deploy-migrations → supabase db push (real, transactional)
            └─ deploy-canary → Cloud Run --no-traffic, --tag canary, shift 10% traffic
                 └─ promote  → update-traffic --to-latest (100%)
```

Key operational rules:
- `concurrency.cancel-in-progress: false` — a deploy is never interrupted mid-flight; a second push queues behind it instead of corrupting the rollout.
- Canary stage watches 5 minutes before promotion; abort via
  `gcloud run services update-traffic maestro-router --to-revisions PREVIOUS_REVISION=100`
  if `maestro_runtime_metrics.fallback_rate` or 5xx rate spikes (see A1.4).
- `workflow_dispatch.inputs.skip_canary` exists for low-risk changes (docs-only,
  config-only) — use sparingly, never for changes touching routing logic.
- Secrets required: `GCP_SA_KEY`, `ANTHROPIC_API_KEY`, `SUPABASE_URL(_STAGING)`,
  `SUPABASE_ANON_KEY(_STAGING)`, `SUPABASE_ACCESS_TOKEN`,
  `SUPABASE_DB_PASSWORD(_STAGING)`, `SUPABASE_PROJECT_REF(_STAGING)`.

Onboarding exercise: trigger `deploy-maestro.yml` manually with
`environment=staging`, watch the four jobs complete, then read the
`$GITHUB_STEP_SUMMARY` for the rollback command.

### A1.2 Supabase migrations

All schema changes are versioned SQL files in `supabase/migrations/`, applied
in filename order (`YYYY_MM_DD_description.sql`). Current history:

```
2026_07_05_v4_2_agents_s6_s10.sql        # agent registry seed (S6-S10)
2026_07_25_add_pgvector_to_rag.sql       # pgvector + hybrid search functions
2026_07_25_add_maestro_monitoring.sql    # runtime_metrics, routing_trace
2026_07_26_add_feedback_tables.sql       # user_feedback, routing_keywords, ab_tests
```

**Safe apply procedure** (never apply directly to production without this):

1. `supabase link --project-ref <staging-ref>` and apply there first:
   `supabase db push`.
2. Run `supabase db lint` — must be clean before proceeding.
3. Smoke-test the new objects:
   ```sql
   SELECT to_regclass('public.maestro_user_feedback');
   SELECT * FROM maestro_routing_ab_tests LIMIT 1;
   ```
4. Every migration in this repo wraps DDL in `BEGIN; ... COMMIT;` — if
   `db push` fails mid-migration, Postgres rolls the whole file back
   automatically. Confirm no partial objects exist before retrying.
5. Only after staging verification: `supabase link --project-ref <prod-ref>`
   and repeat `db push`. This is what `deploy-migrations` in
   `deploy-maestro.yml` automates.
6. Run `mcp__Supabase__get_advisors` (security + performance) immediately
   after — new tables/indexes are a common source of missing RLS policies.

**Rollback**: Postgres migrations here are additive (no destructive `DROP`).
To roll back, write a new migration file that reverses the change — never
edit or delete an already-applied migration file, and never
hand-edit the database out of band from what's in `supabase/migrations/`.

### A1.3 Kubernetes / Cloud Run deployment

**Default target: Cloud Run** (`infra/terraform/main.tf`) — serverless,
scale-to-zero on staging, minimal ops overhead. Containerize with a slim
Dockerfile (Python 3.11-slim base, non-root user, multi-stage build to keep
image small since cold starts matter for `min_instances=0` environments).

**Use GKE (`infra/k8s/*.yaml`) instead when:**
- A sidecar is required (e.g., a local Prometheus exporter or a warm
  pgvector connection pool that must survive across requests).
- Long-lived in-memory caches (routing keyword tables, embedding cache)
  need to persist across many requests without Cloud Run's per-instance
  churn.

Manifests provided:

| File | Purpose |
|------|---------|
| `infra/k8s/deployment.yaml` | RollingUpdate (`maxUnavailable: 0`), zone `topologySpreadConstraints`, readiness/liveness/startup probes |
| `infra/k8s/service.yaml` | ClusterIP + `maestro-config` ConfigMap (secrets created out-of-band, never committed) |
| `infra/k8s/hpa.yaml` | HPA (CPU/mem + custom latency metric) + PodDisruptionBudget |
| `infra/k8s/prometheus-rules.yaml` | ServiceMonitor + PrometheusRule (cluster-level alerts) |

**Rollout strategy (both targets):**
1. Build & tag image with commit SHA (never deploy `:latest` in production —
   `deploy-maestro.yml` tags both, but promotion always references the SHA tag).
2. Canary: 10% traffic for 5 minutes minimum, watching latency/error-rate.
3. Promote to 100% only after canary is clean.
4. Keep `revisionHistoryLimit: 5` (K8s) / Cloud Run's automatic revision
   history so `--to-revisions PREVIOUS=100` rollback is always one command away.
5. Never scale `minReplicas`/`min_instances` down during a deploy — capacity
   must not dip below the pre-deploy floor (`maxUnavailable: 0`,
   `PodDisruptionBudget.minAvailable: 2`).

### A1.4 Monitoring & alerting setup

Two complementary layers:

- **Application/business metrics** (SQL-level, already documented in
  `docs/MONITORING-MAESTRO.md`): `maestro_runtime_metrics`,
  `maestro_routing_trace`, `maestro_metrics_daily`, dashboards via SQL views.
- **Infra/cluster metrics** (this guide, new): Prometheus + Grafana for pod
  health, HPA state, connection pool pressure — things SQL views can't see.

**Prometheus setup:**
1. Install `kube-prometheus-stack` (Helm) in the cluster if not already present.
2. Apply `infra/k8s/prometheus-rules.yaml` — registers a `ServiceMonitor`
   scraping `maestro-router:9090/metrics` every 15s, plus a `PrometheusRule`
   with six alerts (latency, fallback rate, crash loops, HPA maxed out,
   connection pool pressure, Opus usage spike).
3. Grafana: import a dashboard with panels for
   `maestro_routing_latency_seconds` (p50/p95/p99 by `agent_slug`),
   `maestro_fallback_total` rate, `kube_horizontalpodautoscaler_status_current_replicas`,
   and `pgbouncer_pools_client_active_connections`.
4. Alert routing: wire Prometheus Alertmanager to the same Slack channel
   used by `ingest-rag-monthly.yml`'s `SLACK_WEBHOOK_URL` so DevOps and
   Data Team see infra and pipeline alerts in one place.

**Cloud Run alternative**: `infra/terraform/main.tf` provisions
`google_monitoring_alert_policy` resources (`high_latency`, `error_rate`)
directly against Cloud Run's built-in metrics — use this path when running
on Cloud Run instead of GKE; both approaches converge on the same runbook
in the [Troubleshooting](#appendix-troubleshooting) appendix.

| Alert | Threshold | Where defined |
|-------|-----------|---------------|
| P95 latency | > 500ms for 5min | `prometheus-rules.yaml` / `main.tf` |
| 5xx / fallback rate | > 2-5% for 10min | `prometheus-rules.yaml` / `main.tf` |
| Pod crash loop | > 3 restarts / 15min | `prometheus-rules.yaml` |
| HPA maxed out | current == max replicas for 10min | `prometheus-rules.yaml` |
| DB connection pool | > 85% utilized | `prometheus-rules.yaml` |
| Opus tier usage | > 30% of traffic for 30min | `prometheus-rules.yaml`, cost signal |

---

## A2. Infrastructure Scaling

### A2.1 Capacity planning

Baseline sizing per Cloud Run/K8s instance (from `deployment.yaml` requests/limits):

| Resource | Request | Limit | Notes |
|----------|---------|-------|-------|
| CPU | 250m | 1000m | Router logic is I/O-bound (API calls); CPU rarely saturates outside JSON/keyword parsing bursts |
| Memory | 512Mi | 1Gi | Includes routing keyword table cache + response buffering |
| Concurrency/instance | 40 req | — | Set in `variables.tf`; tune down if p95 latency degrades under load, not up blindly |
| DB connections | 1 per active request (pooled) | — | Route through PgBouncer/Supavisor, not direct Postgres connections |

**Database connection budget:** Supabase's default connection limit is a
hard ceiling shared across all consumers (router, ingestion jobs, feedback
scripts, dashboards). Plan as:

```
max_pool_size = supabase_plan_connection_limit * 0.8   (headroom for migrations/CLI)
router_share  = max_pool_size * 0.6                     (steady-state traffic)
batch_share   = max_pool_size * 0.3                      (ingest-rag-monthly, weekly_feedback_report)
admin_share   = max_pool_size * 0.1                      (ad-hoc queries, dashboards)
```

Run `scripts/db_backup_verify.py`-adjacent checks against
`pgbouncer_pools_client_active_connections` weekly to confirm the split
still holds as agent count grows (currently 20 agents / 9 RAG-backed segments).

**Capacity planning triggers** — re-run this section's math whenever:
- A new vertical agent (S11+) is added to `CLAUDE.md`.
- `maestro_metrics_daily.total_requests` grows >50% month-over-month.
- A new RAG collection is added to Supabase (increases embedding sync + vector search load).

### A2.2 Auto-scaling rules

**When to scale up:**
- CPU > 65% average utilization sustained 30s (`hpa.yaml` `scaleUp.stabilizationWindowSeconds: 30`) — react fast, traffic spikes on Maestro are bursty (e.g., a client uploading a batch of EVTEAs).
- Memory > 75% average utilization.
- Custom metric `maestro_routing_latency_p95_ms` > 400ms average across pods.
- Scale-up policy allows doubling pod count per 60s step — aggressive by design, since under-provisioning directly costs latency SLA.

**When to scale down:**
- 5-minute stabilization window (`scaleDown.stabilizationWindowSeconds: 300`) before removing capacity — avoids flapping.
- Removes at most 1 pod per 120s — conservative, since Maestro traffic has been observed to have short lulls followed by resumption (client working sessions, not truly idle).
- Never scale below `minReplicas: 3` (K8s) / `min_instances` (Cloud Run, environment-dependent — 0 for staging, ≥2 for production to avoid cold-start latency on first request).

**Cloud Run specifics** (`infra/terraform/variables.tf`):
- `min_instances = 0` for staging (cost-optimized, cold start acceptable).
- `min_instances >= 2` for production (never cold-start the customer-facing path).
- `max_instances = 20` ceiling — if the HPA/Cloud Run autoscaler hits this repeatedly (`MaestroHPAMaxedOut` alert), that's a capacity-planning event, not something to silence by raising the ceiling reflexively — check A2.1 first.

**Database side:** Supabase connection pooling (PgBouncer/Supavisor) doesn't
autoscale the same way — it has a fixed pool size per plan tier. When
compute scales out faster than the DB pool, requests queue at the pooler.
Watch `pgbouncer_pools_client_active_connections` in the same dashboard as
compute HPA state (A1.4) — they must be read together.

### A2.3 Cost optimization

**Model tier is the primary cost lever** (see `CLAUDE.md` "Tier default"
column — most agents default to Sonnet; Manta 00/maestro escalates
Haiku→Sonnet; Manta 01/claims and Manta 16/arquiteto-ia default to Opus).

| Tier | Relative cost | When it's used | Cost control |
|------|---------------|-----------------|--------------|
| Haiku | 1x (baseline) | Maestro's first-pass routing, low-ambiguity classification | Default for anything not requiring deep reasoning |
| Sonnet | ~5-6x Haiku | Most vertical agents (S1-S10), routine drafting/analysis | Escalation target when Haiku confidence is low |
| Opus | ~15x Haiku | Manta 01 (claims), Manta 16 (arquiteto-ia), Manta 06/15 when explicitly needed | `MaestroOpusUsageSpike` alert fires at >30% of traffic — investigate before it becomes a recurring cost line |

**Resource utilization / reserved capacity:**
- Cloud Run `cpu_idle = true` — CPU is only billed while handling a request on non-min-instance replicas; keep `min_instances` low outside production peak windows.
- For predictable, high baseline traffic (production, business hours), evaluate committed-use discounts (CPU-seconds) once utilization data from `maestro_metrics_daily` shows a stable floor over 30 days — don't commit capacity before that baseline exists.
- Batch jobs (`ingest-rag-monthly.yml`, `weekly_feedback_report.py`) run on ephemeral GitHub Actions runners, not always-on infrastructure — keep it that way; don't move these to a standing VM/pod unless frequency increases beyond weekly/monthly.
- Track cost per agent by joining `maestro_runtime_metrics.model_tier` token counts against published API pricing; review monthly alongside the `MaestroOpusUsageSpike` alert history.

---

## A3. Disaster Recovery

### A3.1 Backup strategy

- **Database snapshots**: Supabase automated daily backups (retention per
  plan tier) plus **Point-in-Time Recovery (PITR/WAL)** for sub-daily
  granularity. Verify both are active with `scripts/db_backup_verify.py`:
  ```bash
  export SUPABASE_ACCESS_TOKEN=...
  python scripts/db_backup_verify.py --project-ref <prod-ref> --rpo-minutes 60 \
      --alert-webhook "$SLACK_WEBHOOK_URL"
  ```
  Schedule this as a daily cron (GitHub Actions `schedule` trigger, mirroring
  `ingest-rag-monthly.yml`'s pattern) — a non-zero exit means backups are
  stale or PITR is disabled, and should page on-call, not just log.
- **WAL recovery**: Supabase PITR lets you restore to any point within the
  retention window. Practice this quarterly against a **branch** (`mcp__Supabase__create_branch`),
  never against production, to confirm the restore procedure still works
  and RTO estimates (A3.3) are realistic.
- **Config/IaC backups**: Terraform state lives in the `manta-terraform-state`
  GCS bucket (`infra/terraform/versions.tf` backend block) — this bucket
  itself must have versioning enabled so a bad `terraform apply` can be
  reverted at the state level, independent of database recovery.
- **Migration files** (`supabase/migrations/`) are the source of truth for
  schema — a from-scratch environment is rebuilt by replaying them in order,
  which is itself a DR mechanism for schema (distinct from data recovery).

### A3.2 Failover procedures

- **Standby database**: Enable Supabase's read replica / standby (available
  on higher plan tiers) in the same or a different region. Application code
  should route read-heavy paths (RAG vector search, dashboard queries) to
  the replica and writes (feedback inserts, metric inserts) to primary —
  this also reduces load on primary during normal operation, not just during failover.
- **Multi-region**: Cloud Run service (`infra/terraform/main.tf`) is
  single-region (`southamerica-east1`) by default. For multi-region
  failover, deploy a second `google_cloud_run_v2_service` in a secondary
  region pointed at the same Supabase project (Supabase itself is
  single-primary-region; multi-region compute does not remove the database
  as a single point of failure unless a standby is also promoted).
- **DNS/traffic failover**: Front Cloud Run/GKE with a global HTTPS load
  balancer or Cloud DNS failover policy; health-check against `/health/ready`.
  On a regional outage, shift the load balancer's backend weight to the
  secondary region manually (documented, not yet automated — treat as a
  manual runbook step until failover volume justifies automation).
- **Runbook order during an incident:**
  1. Confirm scope: infra-only (pods/Cloud Run down, DB fine) vs. database
     incident (Supabase outage/corruption).
  2. Infra-only: redeploy from last known-good image tag
     (`gcloud run services update-traffic maestro-router --to-revisions <TAG>=100`),
     or `kubectl rollout undo deployment/maestro-router -n maestro`.
  3. Database incident: page Supabase support, evaluate PITR restore to a
     branch first to confirm data integrity before promoting, then follow
     Supabase's project-level restore/failover flow.
  4. Post-incident: run `scripts/db_backup_verify.py` and the routing test
     suite (`scripts/test_routing.py`) before declaring recovery complete.

### A3.3 RTO/RPO targets

| Component | RTO (time to recover) | RPO (max data loss) | Mechanism |
|-----------|------------------------|----------------------|-----------|
| Router compute (Cloud Run/K8s) | < 5 min | 0 (stateless) | Redeploy last-good revision / `kubectl rollout undo` |
| Routing keyword tables | < 15 min | < 1 hour | PITR restore to branch, re-seed from `maestro_routing_keywords` snapshot |
| RAG chunks + embeddings | < 4 hours | < 24 hours | Daily snapshot; re-run `scripts/ingest_rag_batch.py` + `supabase/embeddings_sync.py` for anything newer than the snapshot |
| Feedback / metrics tables | < 4 hours | < 1 hour (PITR) | PITR restore — these tables are append-heavy and low-value to lose more than an hour of |
| Full environment (worst case) | < 8 hours | < 24 hours | Terraform re-apply + migration replay + PITR restore + RAG re-ingestion |

These targets assume the quarterly restore drill (A3.1) has been performed
recently — an untested restore procedure has no real RTO, only an assumed one.

---

# Part B — Data Team

## B1. RAG Pipeline

### B1.1 Document ingestion

Pipeline entry point: `scripts/ingest_rag_batch.py` (PDF → chunks → Supabase
`rag_chunks`). Automated monthly via `.github/workflows/ingest-rag-monthly.yml`
(matrix over `saneamento, energia, portos, aeroportos, barragens`, per
`CLAUDE.md`'s RAG collections table), or manually:

```bash
python scripts/ingest_rag_batch.py \
  --segment saneamento --tier T1 \
  --source docs/rag-sources/saneamento/T1-normas/ \
  --batch-size 50
```

**Chunking strategy by tier** (already encoded in the script's docstring —
this is the operational reference for when to use which):

| Tier | Content type | Strategy |
|------|--------------|----------|
| T1 | Normas, leis, resoluções (SNIS, ANEEL, ANTAQ, ICOLD…) | Aggressive chunking, preserve article/section structure — precision over recall, these get cited verbatim |
| T2 | Projetos executivos, estudos básicos | Extract tables + code sections separately from prose |
| T3 | Relatórios, artigos, pesquisa | Full-text chunking, semantic-focused (larger overlap) |
| T4 | Templates, editais, manuais | Minimal processing, preserve original formatting |

PDF extraction uses `pypdf`; each `RAGChunk` carries `collection_slug`,
`tier`, `source_file`/`source_url` (SharePoint path), `page_num`, and
`chunk_index`/`chunk_count` for full traceability back to the source
document — never ingest a chunk that can't be traced to a page number.

### B1.2 Embedding generation

`supabase/embeddings_sync.py` reads pending `rag_chunks` and generates
embeddings via the Anthropic API in batches:

```bash
python supabase/embeddings_sync.py                    # all pending
python supabase/embeddings_sync.py --collection san    # one collection
python supabase/embeddings_sync.py --batch-size 50
python supabase/embeddings_sync.py --dry-run            # preview, no writes
```

Operational notes:
- Always `--dry-run` first after touching ingestion logic — confirms chunk
  counts and batch boundaries before spending API calls.
- Sync state is tracked in `rag_embedding_sync` (`pending/processing/completed/failed`,
  added by `2026_07_25_add_pgvector_to_rag.sql`) — re-running the sync is
  idempotent, it only processes rows not already `completed`.
- Schedule as a daily job (not just post-ingestion) so any chunk that failed
  embedding on first attempt gets retried automatically.
- Embeddings are 1536-dimensional (`rag_chunks.embedding vector(1536)`,
  model tag `embedding_model` defaults to `claude-embed-3` in the schema —
  confirm this matches whatever embedding model is actually configured in
  `embeddings_sync.py` before relying on it, and keep the two in sync on
  any model change).

### B1.3 Vector search

Two SQL functions ship in `2026_07_25_add_pgvector_to_rag.sql`:

- `search_rag_by_similarity(query_embedding, collection_filter, limit_results, similarity_threshold)`
  — pure cosine-similarity search (`1 - (embedding <=> query_embedding)`),
  `ivfflat` index (`lists = 100`, tuned for ~1M vectors; move to `hnsw` if a
  collection grows past that).
- `search_rag_hybrid(query_text, query_embedding, collection_filter, limit_results, keyword_weight, vector_weight)`
  — combines Portuguese full-text search (`ts_rank` over `search_vector`,
  a generated `tsvector` column) with vector similarity, default weights
  `0.3` keyword / `0.7` vector.

```sql
-- Example: hybrid search scoped to the saneamento collection
SELECT * FROM search_rag_hybrid(
  'adutora de água bruta',
  '<query_embedding>'::vector,
  'saneamento',
  10, 0.3, 0.7
);
```

Tuning guidance: raise `keyword_weight` for queries containing exact
regulatory citations (norm numbers, law articles — T1 content), raise
`vector_weight` for conceptual/paraphrased questions. Track which weighting
performs better per collection using the quality metrics in B1.4.

### B1.4 Quality monitoring

- **Relevance metrics**: sample query/result pairs weekly and score
  `similarity_score` distribution per collection — a collection whose
  median similarity for real user queries is trending down usually means
  ingestion has fallen behind (new source docs not yet ingested) or chunking
  is producing fragments too small/large for the query style.
- **Hallucination detection**: any Maestro output that cites a norm, law,
  SICRO code, URL, or DOI as grounding **must** pass through the
  `aluci-guard` skill before it reaches a client-facing document (laudo,
  claim, parecer, orçamento). This is a hard gate, not optional QA —
  `aluci-guard` regex/registry-checks citations against known-valid
  references and catches fabricated ABNT/law/SICRO codes and invented URLs/DOIs.
- **Query set for regression testing**: maintain a fixed set of
  representative queries per collection (mirroring `tests/comprehensive-test-suite.json`'s
  approach for routing) and re-run them after every ingestion batch or
  embedding model change — a drop in retrieved-chunk relevance is a release blocker.
- **Feedback signal as quality proxy**: low approval rates
  (`maestro_user_feedback.approved = false`) concentrated on a specific
  `collection_slug`/agent are a leading indicator of RAG quality problems,
  not just routing problems — cross-reference B2.2's weekly report with
  ingestion recency for that collection before assuming it's a keyword issue.

---

## B2. Feedback Loop

### B2.1 Collecting feedback

`maestro_user_feedback` (from `2026_07_26_add_feedback_tables.sql`) stores
one row per user approval/rejection of a routing decision, referencing
`maestro_routing_trace`:

```sql
CREATE TABLE maestro_user_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  routing_trace_id uuid UNIQUE REFERENCES maestro_routing_trace(id),
  approved boolean NOT NULL,
  confidence int DEFAULT NULL,       -- 1-5 scale
  notes text DEFAULT NULL,
  session_id text, user_id text,
  was_actioned boolean DEFAULT false,
  action_type text, action_description text,
  ...
);
```

Feedback is captured via the `process_routing_feedback(p_routing_trace_id,
p_approved, p_confidence)` SQL function, wired to the Cowork thumbs-up/down
UI on each routing decision. On approval, it boosts matching keyword
confidence in `maestro_routing_keywords` (+0.05, capped at 1.0); on
rejection, it decays confidence for that agent (-0.10, floored at 0.1) —
this is the mechanism, not just a log.

### B2.2 Weekly analysis

Two layers:

1. **SQL function** `analyze_feedback_and_recommend(p_analysis_date)` —
   flags agents with ≥3 rejections/day (HIGH priority) or ≥15
   approvals/day (MEDIUM, boost candidate) for a given date.
2. **`scripts/weekly_feedback_report.py`** — wraps the function into a
   weekly report and can open GitHub issues automatically for HIGH
   priority findings:

```bash
python scripts/weekly_feedback_report.py
python scripts/weekly_feedback_report.py --since 2026-07-19 --until 2026-07-26
python scripts/weekly_feedback_report.py --create-issues --repo manta/manta-hub --dry-run
```

Run this every Monday against the prior week. Recommendations feed directly
into `maestro_routing_keywords` updates — a HIGH priority finding should
become a reviewed PR to keyword weights (or a routing rule change in
`CLAUDE.md`) within the same week, not accumulate as backlog.

### B2.3 A/B testing

`maestro_routing_ab_tests` supports controlled experiments between the
current ("control", variant A) and a candidate ("treatment", variant B)
keyword set, with configurable traffic split (default 90/10):

```bash
# 1. Create a draft test from two keyword-set files
python scripts/ab_test_manager.py create \
  --slug saneamento-keyword-v2 --name "Saneamento keyword expansion v2" \
  --variant-a-file keywords/saneamento_v1.json \
  --variant-b-file keywords/saneamento_v2.json \
  --treatment-rate 0.10

# 2. Activate
python scripts/ab_test_manager.py start --slug saneamento-keyword-v2

# 3. Deterministic per-session assignment (called by the router)
python scripts/ab_test_manager.py assign --slug saneamento-keyword-v2 --session-id abc123

# 4. Report (once >=100 samples per variant)
python scripts/ab_test_manager.py report --slug saneamento-keyword-v2

# 5. Conclude and promote the winner
python scripts/ab_test_manager.py conclude --slug saneamento-keyword-v2 --promote b
```

Assignment is a deterministic hash of `slug:session_id`, so a given user
session always sees the same variant for the test's duration (no
mid-session flip-flopping). The report command requires ≥100 samples per
variant before making a recommendation, and calls a lift of ±3 percentage
points the threshold for a confident promote/keep decision — smaller
deltas are "inconclusive," extend the test rather than eyeballing it.

### B2.4 Continuous improvement

- **Cadence**: weekly feedback report (B2.2) → keyword PRs → monthly RAG
  re-ingestion (B1.1) → quarterly A/B tests on structural changes (new
  keyword sets, chunking strategy changes, embedding model upgrades).
- **Iteration speed**: keep changes small and measurable — one keyword set
  or one chunking parameter per A/B test, not a bundle of changes, or the
  lift can't be attributed.
- **Measurement discipline**: every change that touches routing or RAG
  quality should have a before/after comparison using the same query set
  (B1.4) and the same feedback-approval-rate baseline (B2.2) — "it feels
  better" is not a promotion criterion, the report command's lift
  calculation is.
- **Escalation path**: HIGH priority recommendations from B2.2 that recur
  for 2+ consecutive weeks without resolution should be escalated beyond a
  keyword tweak — consider whether the underlying agent/segment needs
  routing rule changes in `CLAUDE.md` itself (gate: MN approval, per the
  DEPLOY CHECKLIST in `CLAUDE.md`).

---

## Appendix: File Manifest

```
Codex-exemplo/
├── CLAUDE.md                                    # master agent registry + routing rules
├── docs/
│   ├── TRAINING-GUIDE-DEVOPS-DATA-TEAMS.md       # this document
│   ├── TRAINING-GUIDE-MAESTRO-TEAM.md            # routing engine internals
│   └── MONITORING-MAESTRO.md                     # SQL-level metrics/alerting
├── .github/workflows/
│   ├── deploy-maestro.yml                        # build -> test -> deploy (canary)
│   ├── test-maestro-routing.yml
│   ├── ingest-rag-monthly.yml
│   └── sync-agents-to-sharepoint.yml
├── infra/
│   ├── k8s/
│   │   ├── deployment.yaml
│   │   ├── service.yaml                          # + maestro-config ConfigMap
│   │   ├── hpa.yaml                               # + PodDisruptionBudget
│   │   └── prometheus-rules.yaml                  # ServiceMonitor + PrometheusRule
│   └── terraform/
│       ├── versions.tf
│       ├── variables.tf
│       ├── main.tf                                # Cloud Run + alert policies
│       └── outputs.tf
├── supabase/
│   ├── migrations/
│   │   ├── 2026_07_05_v4_2_agents_s6_s10.sql
│   │   ├── 2026_07_25_add_pgvector_to_rag.sql
│   │   ├── 2026_07_25_add_maestro_monitoring.sql
│   │   └── 2026_07_26_add_feedback_tables.sql
│   └── embeddings_sync.py
└── scripts/
    ├── ingest_rag_batch.py
    ├── test_routing.py
    ├── weekly_feedback_report.py                  # new — Data Team weekly job
    ├── ab_test_manager.py                          # new — routing A/B tests
    └── db_backup_verify.py                         # new — DR backup check
```

---

## Appendix: Quick-Reference Checklists

**DevOps — new deploy:**
- [ ] `deploy-maestro.yml` build + test jobs green
- [ ] Migrations applied to staging, `supabase db lint` clean
- [ ] Canary at 10% for ≥5 min, error/latency within bounds
- [ ] Promoted to 100%, `$GITHUB_STEP_SUMMARY` rollback command noted
- [ ] Post-deploy: `scripts/test_routing.py` re-run against production

**DevOps — weekly ops:**
- [ ] `scripts/db_backup_verify.py` passing (PITR enabled, backup age < RPO)
- [ ] Review Prometheus alerts fired this week (`prometheus-rules.yaml`)
- [ ] Check HPA scale events — any `MaestroHPAMaxedOut`? → capacity review (A2.1)
- [ ] Check Opus tier usage % (`MaestroOpusUsageSpike`) → cost review (A2.3)

**Data Team — weekly ops:**
- [ ] `python scripts/weekly_feedback_report.py` — review recommendations
- [ ] HIGH priority items → PR against `maestro_routing_keywords` this week
- [ ] Any active A/B test past 100 samples/variant? `ab_test_manager.py report`
- [ ] Confirm no `rag_embedding_sync` rows stuck in `failed` status

**Data Team — monthly ops:**
- [ ] `ingest-rag-monthly.yml` run succeeded for all 5 segments
- [ ] `embeddings_sync.py` backlog is zero (`--dry-run` shows 0 pending)
- [ ] Query-set regression test re-run per collection (B1.4)
- [ ] Any document requiring `aluci-guard` audit before client delivery — confirmed run

**Quarterly (both teams):**
- [ ] DR restore drill — PITR restore to a Supabase branch, verify data, discard branch
- [ ] Revisit RTO/RPO targets (A3.3) against actual drill timing
- [ ] Revisit capacity plan (A2.1) against latest `maestro_metrics_daily` trend

---

## Appendix: Troubleshooting

**<a name="troubleshooting-latency"></a>Latency (P95 > 500ms):**
1. Check `maestro_metrics_daily.latency_p95` by agent — isolate whether it's
   one agent (routing/tier issue) or global (infra issue).
2. Global: check HPA state — maxed out? (A2.2) Check DB connection pool
   pressure — queuing at PgBouncer? (A2.1)
3. Single agent: check `model_tier` distribution — has it drifted toward
   Opus/Sonnet unexpectedly? (A2.3) Check RAG vector search latency
   separately — `ivfflat` index may need `lists` retuning if the collection
   has grown past ~1M vectors (B1.3).

**<a name="troubleshooting-fallback"></a>Fallback rate spike (> 5%):**
1. Check `maestro_routing_trace.is_ambiguous` rate for the same window —
   correlated spike usually means a routing keyword gap (new terminology
   in user prompts not covered by `CLAUDE.md`'s routing rules or
   `maestro_routing_keywords`).
2. Not correlated with ambiguity: likely an upstream API issue (Anthropic
   API errors/timeouts) — check `fallback_reason` breakdown.
3. Cross-check `weekly_feedback_report.py` output for the affected agent —
   a fallback spike often shows up as a rejection spike too.

**RAG quality regression:**
1. Confirm `ingest-rag-monthly.yml` and `embeddings_sync.py` are current
   for the affected collection (B1.1/B1.2) — stale ingestion is the most
   common cause.
2. Re-run the collection's query set (B1.4) and compare similarity scores
   against the last known-good baseline.
3. If citations are involved, run `aluci-guard` regardless of the above —
   a hallucinated citation is a correctness issue independent of retrieval quality.
