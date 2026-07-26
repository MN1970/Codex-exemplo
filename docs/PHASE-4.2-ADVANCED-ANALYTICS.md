# PHASE 4.2 — Advanced Analytics & Intelligence

**Workstream**: 4.2 of PHASE 4 (Data & Intelligence Platform) | **Status**: 📋 Design specification
**Depends on**: 4.1 Data Platform Foundation (warehouse schema, nightly ETL, embeddings store)
**Feeds into**: 4.3 Autonomous Optimization (auto-tuning routing/tiering from 4.2 signals)
**Builds on**: Phase 1.4 monitoring (`maestro_runtime_metrics`, `maestro_routing_trace`), Phase 2.1 feedback loop (`maestro_user_feedback`, `maestro_routing_keywords`)
**Timeline (proposed)**: Oct 01, 2027 – Dec 15, 2027 (11 weeks)
**Owner**: Claude Code + DevOps, Gate humano: MN (final dashboard sign-off before exec rollout)

---

## 0. Purpose & Scope

Phase 1.4/2.1 gave Maestro raw observability (latency, tokens, approvals) and a keyword feedback loop.
Phase 4.2 turns that raw telemetry into **decision-grade intelligence**: trend lines instead of point-in-time
numbers, per-agent scorecards instead of scattered tables, forecasts and ROI instead of counts, and
alerts that fire *before* SLAs are breached instead of after.

Six analytical domains, in delivery order:

| # | Domain | Primary question it answers |
|---|--------|------------------------------|
| 1 | Routing Decision Analytics | Is routing getting better or worse, and where does it fail? |
| 2 | Agent Performance Analytics | Which of the 20 agents are healthy, and where is budget going? |
| 3 | User Behavior Analytics | What are people actually asking, and is the system learning? |
| 4 | Business Intelligence | Is Maestro worth what it costs, and how fast is it growing? |
| 5 | Predictive Analytics | Can we see a failure or cost spike coming, and what should we do? |
| 6 | Dashboards & Alerting | Where does all of this live, and who gets paged? |

Design constraints carried over from Phase 1–3:
- All new tables live in the existing Supabase Postgres project (no new data store).
- No plaintext prompts leave the audit boundary already established in `maestro_audit_log` (Phase 3.6) —
  analytics reads hashed/aggregated fields wherever a table is user-facing.
- Every new table follows the `maestro_*` naming convention and is additive; nothing in Phase 1/2/3 is altered.
- Every metric below states its **source table(s)**, its **refresh cadence**, and its **owner artifact**
  (view, materialized rollup, or BI dashboard) so this doc can be implemented as a single migration + one
  scheduled job + one dashboard bundle.

---

## 1. Routing Decision Analytics

### 1.1 Metrics definitions

| Metric | Definition | Source | Cadence |
|--------|-----------|--------|---------|
| **Routing accuracy (7d/30d rolling)** | `approved_cases / (approved_cases + rejected_cases)` from `maestro_user_feedback` joined to `maestro_routing_trace` | `maestro_routing_trace`, `maestro_user_feedback` | Hourly refresh, daily rollup |
| **Accuracy trend (WoW delta)** | Current 7d accuracy − prior 7d accuracy, per agent and system-wide | `maestro_routing_accuracy_trends` (new) | Daily |
| **Confidence distribution** | Histogram of `primary_score` in 10 buckets (0.0–0.1 … 0.9–1.0), split by outcome (approved/rejected/unreviewed) | `maestro_routing_trace` | Daily |
| **Score-gap distribution** | Histogram of `score_gap` (primary − runner-up); low gap = structurally ambiguous query | `maestro_routing_trace` | Daily |
| **Ambiguity rate** | `is_ambiguous=true` cases / total cases, per agent pair (e.g. S1↔S2, saneamento↔energia) | `maestro_routing_trace` | Daily |
| **Failure cluster** | Rejected/ambiguous cases grouped by (primary_agent, top rejected-alternate, dominant keyword) | `maestro_routing_failure_patterns` (new) | Weekly |
| **Tie-breaker effectiveness** | % of LLM tie-breaker (Phase 3.5) calls where `llm_correct=true` | `maestro_tiebreaker_events` | Daily |
| **Time-to-detect regression** | Days between an accuracy drop starting and an alert firing | Derived from `maestro_routing_accuracy_trends` + `maestro_alerts` | Per incident |

### 1.2 Data schema (additive)

```sql
-- 4.2.1 — Rolling accuracy trend (daily rollup, keeps 400 days)
CREATE TABLE IF NOT EXISTS maestro_routing_accuracy_trends (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  agent_slug text NOT NULL,             -- 'ALL' for system-wide row

  total_cases int DEFAULT 0,
  approved_cases int DEFAULT 0,
  rejected_cases int DEFAULT 0,
  unreviewed_cases int DEFAULT 0,

  accuracy_rate_7d float DEFAULT NULL,  -- rolling 7-day window ending `date`
  accuracy_rate_30d float DEFAULT NULL, -- rolling 30-day window ending `date`
  accuracy_delta_wow float DEFAULT NULL,-- 7d accuracy - previous 7d accuracy

  avg_confidence float DEFAULT NULL,
  avg_score_gap float DEFAULT NULL,
  ambiguity_rate float DEFAULT NULL,

  created_at timestamp DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_accuracy_trends_unique
  ON maestro_routing_accuracy_trends(date, agent_slug);

-- 4.2.2 — Confidence / score-gap histograms (10 buckets, per day)
CREATE TABLE IF NOT EXISTS maestro_confidence_distribution (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  bucket_low float NOT NULL,     -- e.g. 0.7
  bucket_high float NOT NULL,    -- e.g. 0.8
  outcome text NOT NULL,         -- 'approved' | 'rejected' | 'unreviewed'
  case_count int DEFAULT 0,
  UNIQUE(date, bucket_low, outcome)
);

-- 4.2.3 — Failure pattern clustering (weekly job output)
CREATE TABLE IF NOT EXISTS maestro_routing_failure_patterns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start date NOT NULL,
  primary_agent text NOT NULL,
  confused_with_agent text NOT NULL,   -- agent the query "should" have gone to
  dominant_keyword text,
  case_count int NOT NULL,
  sample_prompt_hashes text[] DEFAULT ARRAY[]::text[], -- pointer, not plaintext
  recommended_action text,             -- 'boost_keyword' | 'demote_keyword' | 'add_disambiguation_rule'
  status text DEFAULT 'open',          -- open, actioned, dismissed
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_failure_patterns_week
  ON maestro_routing_failure_patterns(week_start DESC, case_count DESC);
```

### 1.3 Rollup function (nightly)

```sql
CREATE OR REPLACE FUNCTION compute_routing_accuracy_trends(p_date date DEFAULT CURRENT_DATE)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  DELETE FROM maestro_routing_accuracy_trends WHERE date = p_date;

  INSERT INTO maestro_routing_accuracy_trends (
    date, agent_slug, total_cases, approved_cases, rejected_cases, unreviewed_cases,
    accuracy_rate_7d, accuracy_rate_30d, avg_confidence, avg_score_gap, ambiguity_rate
  )
  SELECT
    p_date,
    rt.primary_agent,
    COUNT(*),
    COUNT(*) FILTER (WHERE rt.user_approved = true),
    COUNT(*) FILTER (WHERE rt.user_approved = false),
    COUNT(*) FILTER (WHERE rt.user_approved IS NULL),
    NULLIF(COUNT(*) FILTER (WHERE rt.user_approved = true AND rt.timestamp > p_date - interval '7 days'), 0)::float
      / NULLIF(COUNT(*) FILTER (WHERE rt.user_approved IS NOT NULL AND rt.timestamp > p_date - interval '7 days'), 0),
    NULLIF(COUNT(*) FILTER (WHERE rt.user_approved = true AND rt.timestamp > p_date - interval '30 days'), 0)::float
      / NULLIF(COUNT(*) FILTER (WHERE rt.user_approved IS NOT NULL AND rt.timestamp > p_date - interval '30 days'), 0),
    AVG(rt.primary_score),
    AVG(rt.score_gap),
    AVG(CASE WHEN rt.is_ambiguous THEN 1.0 ELSE 0.0 END)
  FROM maestro_routing_trace rt
  WHERE DATE(rt.timestamp) = p_date
  GROUP BY rt.primary_agent;

  -- system-wide 'ALL' row
  INSERT INTO maestro_routing_accuracy_trends (date, agent_slug, total_cases, approved_cases, rejected_cases, unreviewed_cases)
  SELECT p_date, 'ALL', COUNT(*), COUNT(*) FILTER (WHERE user_approved = true),
         COUNT(*) FILTER (WHERE user_approved = false), COUNT(*) FILTER (WHERE user_approved IS NULL)
  FROM maestro_routing_trace WHERE DATE(timestamp) = p_date;

  -- week-over-week delta (self-join against 7 days prior)
  UPDATE maestro_routing_accuracy_trends t
  SET accuracy_delta_wow = t.accuracy_rate_7d - prev.accuracy_rate_7d
  FROM maestro_routing_accuracy_trends prev
  WHERE prev.date = t.date - interval '7 days' AND prev.agent_slug = t.agent_slug AND t.date = p_date;
END;
$$;
```

---

## 2. Agent Performance Analytics

### 2.1 Metrics definitions

| Metric | Definition | Source | Cadence |
|--------|-----------|--------|---------|
| **Throughput** | Requests/day, requests/hour peak, per agent | `maestro_runtime_metrics` | Real-time + daily |
| **Latency P50/P95/P99** | Already tracked (Phase 1.4) | `maestro_metrics_daily` | Daily |
| **Token efficiency** | `total_tokens / successful_resolutions` (a resolution is "successful" if `user_approved != false`) | `maestro_runtime_metrics` + `maestro_user_feedback` | Daily |
| **Cost per query** | `total_tokens × blended $/token by tier` (haiku/sonnet/opus rate card) | `maestro_agent_performance_scorecard` (new) | Daily |
| **Tier mix drift** | Change in haiku/sonnet/opus % share vs prior 30d | `maestro_metrics_daily` | Weekly |
| **User satisfaction (CSAT proxy)** | `avg(confidence 1-5)` from `maestro_user_feedback` where `approved=true` | `maestro_user_feedback` | Daily |
| **Composite health score** | Weighted score (0–100): 40% accuracy, 30% latency SLO adherence, 20% CSAT, 10% fallback rate | `maestro_agent_performance_scorecard` (new) | Daily |

### 2.2 Data schema

```sql
CREATE TABLE IF NOT EXISTS maestro_agent_performance_scorecard (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  agent_slug text NOT NULL,

  requests_total int DEFAULT 0,
  requests_peak_hour int DEFAULT 0,

  latency_p50 float, latency_p95 float, latency_p99 float,
  latency_slo_met_pct float,              -- % of requests under target (default 500ms p95)

  total_tokens bigint DEFAULT 0,
  tokens_per_resolution float,
  estimated_cost_usd numeric(10,4) DEFAULT 0,

  haiku_pct float, sonnet_pct float, opus_pct float,
  tier_mix_delta_30d float,                -- signed % point shift in opus share

  csat_avg float,                          -- 1-5 scale
  fallback_rate float,

  health_score float,                      -- 0-100 composite, see weights above
  health_band text,                        -- 'green' >=80, 'yellow' 60-79, 'red' <60

  created_at timestamp DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_scorecard_unique ON maestro_agent_performance_scorecard(date, agent_slug);
CREATE INDEX IF NOT EXISTS idx_scorecard_health ON maestro_agent_performance_scorecard(date DESC, health_score);

-- Rate card, editable without a migration
CREATE TABLE IF NOT EXISTS maestro_model_rate_card (
  model_tier text PRIMARY KEY,             -- haiku, sonnet, opus
  usd_per_1k_input_tokens numeric(10,6) NOT NULL,
  usd_per_1k_output_tokens numeric(10,6) NOT NULL,
  effective_from date NOT NULL DEFAULT CURRENT_DATE
);
```

### 2.3 Composite health score (reference formula)

```
health_score =
    40 * accuracy_rate_7d
  + 30 * latency_slo_met_pct
  + 20 * (csat_avg / 5.0)
  + 10 * (1 - fallback_rate)
```
`health_band`: green ≥ 80, yellow 60–79, red < 60. Any agent in `red` for 2 consecutive days auto-opens
a GitHub issue (reuses the Phase 3.2 notification pattern) tagged `agent-health`.

---

## 3. User Behavior Analytics

### 3.1 Metrics definitions

| Metric | Definition | Source | Cadence |
|--------|-----------|--------|---------|
| **Query volume by segment** | Count of routed prompts per segment (S1–S10 + horizontais) | `maestro_routing_trace` | Daily |
| **Query topic clusters** | K-means / cosine clustering of prompt embeddings into named topics (e.g. "quantitativo pavimento", "reequilíbrio contratual") | `maestro_query_clusters` (new), embeddings from Phase 4.1 store | Weekly |
| **Session depth** | Avg turns per `maestro_conversations` session (Phase 3.3) | `maestro_conversation_turns` | Daily |
| **Follow-up rate** | % of sessions with ≥2 turns (proxy for whether first answer was sufficient) | `maestro_conversation_turns` | Daily |
| **Feedback participation rate** | `feedback_count / routing_trace_count` — are users actually clicking approve/reject? | `maestro_user_feedback`, `maestro_routing_trace` | Daily |
| **Feedback trend by agent** | 7d rolling approval rate per agent (same series as 1.1, surfaced here from the user's-eye view) | `maestro_routing_accuracy_trends` | Daily |
| **Learning signal strength** | Count of `maestro_routing_keywords` rows whose `confidence` changed ≥ 0.05 in the last 7 days (evidence the feedback loop is actively reshaping routing) | `maestro_routing_keywords` | Weekly |

### 3.2 Data schema

```sql
CREATE TABLE IF NOT EXISTS maestro_query_clusters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start date NOT NULL,
  cluster_label text NOT NULL,          -- human-assigned or auto-named via top TF-IDF terms
  segment_hint text,                    -- dominant segment for this cluster
  case_count int NOT NULL,
  avg_confidence float,
  representative_prompt_hash text,      -- pointer only, not plaintext
  centroid vector(1536),                -- reuses pgvector extension from Phase 2.4 RAG store
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_query_clusters_week ON maestro_query_clusters(week_start DESC, case_count DESC);

CREATE TABLE IF NOT EXISTS maestro_user_behavior_daily (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL,
  segment text NOT NULL,                -- 'ALL' for system-wide row

  query_count int DEFAULT 0,
  unique_sessions int DEFAULT 0,
  avg_session_turns float,
  followup_rate float,
  feedback_participation_rate float,

  created_at timestamp DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_behavior_daily_unique ON maestro_user_behavior_daily(date, segment);
```

---

## 4. Business Intelligence

### 4.1 Metrics definitions

| Metric | Definition | Source | Cadence |
|--------|-----------|--------|---------|
| **Adoption — active users** | Distinct `user_id` per week/month | `maestro_runtime_metrics` | Weekly |
| **Adoption — agent coverage** | # of the 20 agents with ≥1 request in the trailing 7 days | `maestro_runtime_metrics` | Daily |
| **ROI — cost side** | `Σ estimated_cost_usd` (from 2.2 rate card) | `maestro_agent_performance_scorecard` | Monthly |
| **ROI — value side** | `approved_cases × avg_manual_hours_saved × loaded_hourly_rate` (manual hours/rate configured per agent, editable table) | `maestro_roi_assumptions` (new) | Monthly |
| **ROI ratio** | value side / cost side | `maestro_roi_ledger` (new) | Monthly |
| **Usage forecast** | Next-30-day request volume, per agent and system-wide, from time-series model (see §5.2) | `maestro_usage_forecast` (new) | Weekly |
| **Segment growth rate** | MoM % change in query_count per segment | `maestro_user_behavior_daily` | Monthly |

### 4.2 Data schema

```sql
CREATE TABLE IF NOT EXISTS maestro_roi_assumptions (
  agent_slug text PRIMARY KEY,
  avg_manual_hours_saved float NOT NULL DEFAULT 0.5,  -- hours a consultant would spend on an equivalent query
  loaded_hourly_rate_usd numeric(10,2) NOT NULL DEFAULT 85.00,
  updated_by text,
  updated_at timestamp DEFAULT now()
);

CREATE TABLE IF NOT EXISTS maestro_roi_ledger (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  month date NOT NULL,                  -- first day of month
  agent_slug text NOT NULL,             -- 'ALL' for consolidated row

  total_cost_usd numeric(12,2) DEFAULT 0,
  approved_resolutions int DEFAULT 0,
  estimated_value_usd numeric(12,2) DEFAULT 0,
  roi_ratio float,                      -- value / cost

  created_at timestamp DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_roi_ledger_unique ON maestro_roi_ledger(month, agent_slug);

CREATE TABLE IF NOT EXISTS maestro_usage_forecast (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  generated_at timestamp DEFAULT now(),
  forecast_date date NOT NULL,          -- date being predicted
  agent_slug text NOT NULL,             -- 'ALL' for system-wide

  predicted_requests int NOT NULL,
  ci_low int, ci_high int,              -- 80% confidence interval
  model_used text DEFAULT 'holt_winters', -- documented in §5.2
  actual_requests int,                  -- backfilled once the date passes, for accuracy tracking
  mape float,                           -- mean abs. % error, computed once actual is known

  UNIQUE(generated_at, forecast_date, agent_slug)
);
```

### 4.3 Executive BI view

```sql
CREATE OR REPLACE VIEW maestro_executive_summary AS
SELECT
  date_trunc('month', r.month) AS month,
  SUM(r.total_cost_usd) AS total_cost_usd,
  SUM(r.estimated_value_usd) AS total_value_usd,
  ROUND((SUM(r.estimated_value_usd) / NULLIF(SUM(r.total_cost_usd), 0))::numeric, 2) AS roi_ratio,
  (SELECT COUNT(DISTINCT agent_slug) FROM maestro_agent_performance_scorecard
     WHERE date > now() - interval '7 days') AS active_agents_7d,
  (SELECT AVG(accuracy_rate_7d) FROM maestro_routing_accuracy_trends
     WHERE agent_slug = 'ALL' AND date = CURRENT_DATE - interval '1 day') AS system_accuracy_7d
FROM maestro_roi_ledger r
WHERE r.agent_slug = 'ALL'
GROUP BY 1
ORDER BY 1 DESC;
```

---

## 5. Predictive Analytics

### 5.1 Anticipating failures

Approach is deliberately lightweight (statistical, not a hosted ML service) so it runs inside existing
Supabase/Python jobs with no new infrastructure:

| Signal | Method | Trigger |
|--------|--------|---------|
| **Accuracy regression** | 3-sigma control chart on `accuracy_rate_7d` (rolling mean/stddev over trailing 90 days) | Flag if today's value < mean − 3σ |
| **Latency creep** | Linear regression slope on `latency_p95` over trailing 14 days | Flag if slope projects SLO breach within 7 days |
| **Ambiguity build-up** | Rate-of-change on `ambiguity_rate` per agent pair | Flag if 2× the 30-day baseline |
| **Cost runaway** | Compare current-week `estimated_cost_usd` run-rate to `maestro_roi_assumptions`-implied budget | Flag if projected month-end cost > 120% of prior month |
| **Failure probability per query (online)** | Logistic regression over `(primary_score, score_gap, agent_slug, keyword_match_count)` trained weekly on `maestro_user_feedback` outcomes, scored at request time | Surface `p_reject` back to the router; if `p_reject > 0.7`, auto-route to LLM tie-breaker (Phase 3.5) instead of accepting the keyword match |

### 5.2 Usage forecasting model

Holt-Winters (triple exponential smoothing) over `maestro_user_behavior_daily.query_count`, one model
per agent + one system-wide, retrained weekly. Chosen over a heavier ML stack because traffic is small,
seasonal (weekday-driven), and interpretable output (with confidence bands) is more useful to MN than a
black-box model. `mape` is back-filled once the forecast date passes and tracked on `maestro_usage_forecast`
so the model can be swapped if MAPE > 20% for 3 consecutive weeks.

### 5.3 Recommendation engine

```sql
CREATE TABLE IF NOT EXISTS maestro_recommendations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  generated_at timestamp DEFAULT now(),
  category text NOT NULL,          -- 'routing_keyword' | 'tier_downgrade' | 'tier_upgrade' | 'capacity' | 'cost'
  agent_slug text,
  summary text NOT NULL,
  evidence jsonb DEFAULT '{}',     -- supporting numbers (e.g. {"rejected_count": 12, "keyword": "dragagem"})
  confidence text DEFAULT 'medium',-- low | medium | high
  status text DEFAULT 'open',      -- open, actioned, dismissed
  actioned_by text,
  actioned_at timestamp
);
CREATE INDEX IF NOT EXISTS idx_recommendations_open ON maestro_recommendations(status, generated_at DESC) WHERE status = 'open';
```

Recommendation sources feeding this table: §1.2 failure patterns, §2 tier-mix drift, §4 ROI ratio decline,
§5.1 cost-runaway signal. All four write into the same table so MN reviews one queue, not four dashboards.
This queue is the direct input to Phase 4.3 (Autonomous Optimization) — 4.2 only recommends, it never
auto-applies a change.

---

## 6. Dashboards & Alerting

### 6.1 BI tool integration

| Layer | Tool | Rationale | Access |
|-------|------|-----------|--------|
| **Operational (real-time)** | Existing Cowork custom dashboards (Phase 1.4 pattern) reading `maestro_metrics_current_hour` and the new `maestro_agent_performance_scorecard` | Zero new infra, already how Maestro on-call works | Manta ops team |
| **Analytical (self-serve, drill-down)** | **Metabase** (self-hosted, connects directly to the Supabase Postgres connection string; open-source, no per-seat license cost) | Lets any Manta lead build ad-hoc charts over the views in §1–5 without writing SQL | Manta leads + segment owners |
| **Executive (monthly)** | **Power BI**, via the native Postgres connector, reading only `maestro_executive_summary` and `maestro_roi_ledger` | Org already standardized on Microsoft 365 (SharePoint, Outlook); MN and clients already work in Power BI/Excel | MN + client-facing partners |
| **Alerting** | Slack webhook (existing Phase 1.4 channel) + GitHub issue auto-creation (existing Phase 3.2 pattern) | No new alerting channel to maintain | On-call + segment owners |

Data path for every tool above is **read-only views**, never raw tables — `maestro_executive_summary`,
`maestro_routing_quality` (existing), and three new views below are the only objects granted to the BI
service-role credentials.

```sql
CREATE OR REPLACE VIEW maestro_dashboard_agent_health AS
SELECT date, agent_slug, health_score, health_band, requests_total, latency_p95, csat_avg
FROM maestro_agent_performance_scorecard
WHERE date >= CURRENT_DATE - interval '90 days';

CREATE OR REPLACE VIEW maestro_dashboard_recommendations_open AS
SELECT generated_at, category, agent_slug, summary, confidence
FROM maestro_recommendations
WHERE status = 'open'
ORDER BY generated_at DESC;

CREATE OR REPLACE VIEW maestro_dashboard_forecast_vs_actual AS
SELECT forecast_date, agent_slug, predicted_requests, ci_low, ci_high, actual_requests, mape
FROM maestro_usage_forecast
WHERE forecast_date >= CURRENT_DATE - interval '60 days';
```

### 6.2 SLA tracking

Extends the Phase 1.4 SLO table with the analytics-layer SLAs this phase introduces:

| SLA | Target | Measured by |
|-----|--------|-------------|
| Latency P95 | < 500 ms per agent | `maestro_agent_performance_scorecard.latency_slo_met_pct` |
| Routing accuracy (system) | ≥ 85% 7-day rolling | `maestro_routing_accuracy_trends` (agent_slug='ALL') |
| Forecast accuracy | MAPE < 20% | `maestro_usage_forecast.mape` |
| Dashboard freshness | Nightly rollups complete by 02:00 UTC | Job run log (see §6.4) |
| Recommendation triage | Every `open` item reviewed within 5 business days | `maestro_recommendations.status` age |

### 6.3 Alerting thresholds

| Alert | Threshold | Severity | Channel | Action |
|-------|-----------|----------|---------|--------|
| Routing accuracy drop | `accuracy_delta_wow < -0.05` (5pp) for any agent | High | Slack + GitHub issue | Routing team reviews `maestro_routing_failure_patterns` for that agent |
| System accuracy floor breach | `accuracy_rate_7d < 0.85` (ALL row) | Critical | Slack page | On-call review within 4h |
| Confidence distribution shift | ≥15% of daily cases fall below 0.70 bucket (vs 30d baseline) | Medium | Slack | Weekly review, no page |
| Health score red | `health_band = 'red'` for 2 consecutive days | High | GitHub issue (`agent-health` tag) | Segment owner triage |
| Latency creep | Regression slope projects P95 breach within 7 days | Medium | Slack | Proactive tier-mix review |
| Cost runaway | Projected month-end cost > 120% of prior month | High | Slack + email to MN | ROI review, consider tier downgrade |
| ROI ratio decline | `roi_ratio` < 1.0 for 2 consecutive months, any agent | High | Email to MN | Business case review — sunset or re-scope agent |
| Forecast miss | `mape > 0.20` for 3 consecutive weeks | Low | GitHub issue | Swap/retrain forecasting model |
| Anomaly (generic) | Any tracked metric > 3σ from its trailing 90-day mean | Medium–Critical (scaled by σ) | Slack | Investigate before next scheduled rollup |
| Feedback participation collapse | `feedback_participation_rate < 0.10` system-wide | Medium | Slack | UX review of the approve/reject affordance in Cowork |

### 6.4 Scheduled jobs

```
02:00 UTC daily  → compute_routing_accuracy_trends(), compute_daily_metrics() [existing],
                   agent scorecard rollup, anomaly scan (3σ check across all daily tables)
02:30 UTC daily  → refresh confidence/score-gap histograms
03:00 UTC weekly (Mon) → failure-pattern clustering, query-topic clustering, Holt-Winters forecast retrain
03:30 UTC weekly (Mon) → recommendation engine sweep (writes to maestro_recommendations)
1st of month, 04:00 UTC → ROI ledger close-out (maestro_roi_ledger), executive summary refresh
```
Every job writes a row to `maestro_job_runs (job_name, started_at, finished_at, status, rows_affected)`
(new, trivial table) so §6.2's "dashboard freshness" SLA has something concrete to check.

```sql
CREATE TABLE IF NOT EXISTS maestro_job_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_name text NOT NULL,
  started_at timestamp NOT NULL,
  finished_at timestamp,
  status text DEFAULT 'running',  -- running, success, failed
  rows_affected int,
  error_message text
);
CREATE INDEX IF NOT EXISTS idx_job_runs_name ON maestro_job_runs(job_name, started_at DESC);
```

---

## 7. Deliverables Checklist (4.2)

- [ ] Migration: tables in §1.2, §2.2, §3.2, §4.2, §5.3, §6.1, §6.4 (one file, additive only)
- [ ] `compute_routing_accuracy_trends()` + nightly schedule
- [ ] Agent scorecard rollup job (§2) + `maestro_model_rate_card` seeded with current tier pricing
- [ ] Query clustering job (embeddings reused from Phase 4.1 store; pgvector already enabled)
- [ ] ROI assumptions seeded per agent (`maestro_roi_assumptions`) — needs MN sign-off on hourly rate
- [ ] Holt-Winters forecast job + backfill of `actual_requests`/`mape` for accuracy tracking
- [ ] Recommendation engine sweep job writing to `maestro_recommendations`
- [ ] Metabase instance stood up, connected read-only to the four dashboard views
- [ ] Power BI workbook for MN/exec (`maestro_executive_summary`, `maestro_roi_ledger`)
- [ ] Slack + GitHub alert wiring for all rows in §6.3
- [ ] `maestro_job_runs` table + freshness check wired into the alerting channel
- [ ] 14-day baseline capture before any alert threshold goes live (avoid false pages on cold data)
- [ ] Gate humano: MN review of dashboards + ROI assumptions before executive rollout

---

## 8. Risks & Mitigations

| Risk | Mitigation | Owner |
|------|-----------|-------|
| ROI assumptions (hours saved, hourly rate) are subjective and could overstate value | MN reviews and signs off `maestro_roi_assumptions` before any ROI number leaves the dashboard | MN |
| Query clustering surfaces near-verbatim prompt text in cluster labels, risking data minimization | Cluster labels generated from TF-IDF top-terms only; `representative_prompt_hash` stored, never plaintext | Security |
| Forecast model (Holt-Winters) underperforms once traffic pattern changes (e.g. new segment launch) | `mape` tracked per forecast; 3-week breach auto-opens a model-swap issue | DevOps |
| Alert fatigue from 10 new thresholds on top of Phase 1.4's existing ones | 14-day baseline before enabling; severities tiered so only High/Critical page, Medium/Low go to async Slack | On-call |
| Recommendation queue becomes a dumping ground nobody triages | SLA in §6.2 (5 business days) + weekly digest to segment owners | Product |

---

## 9. What 4.2 does *not* do

- Does **not** auto-apply any routing/tier change — every output here is read-only or a `maestro_recommendations`
  row for a human to action. Auto-apply is explicitly scoped to Phase 4.3.
- Does **not** introduce a new database, warehouse, or hosted ML service — everything runs on the existing
  Supabase Postgres + pgvector + scheduled jobs already used since Phase 1.4/2.4.
- Does **not** expose raw prompt text to any BI tool — all dashboard-facing views are pre-aggregated or
  hash-referenced, consistent with the Phase 3.6 audit/compliance boundary.

---

**Status**: 📋 Specification ready for migration + implementation
**Next Checkpoint**: MN review of §7 checklist before `Oct 01` kickoff
