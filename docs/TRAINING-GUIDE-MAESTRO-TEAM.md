# Manta Maestro — Training Guide (manta-hub team)

**Audience**: Engineers on the Maestro team (manta-hub) — onboarding, debugging, and deployment reference.
**Source of truth**: This guide is a synthesis of the design/implementation docs already in this repo
(`docs/*.md`, `supabase/migrations/*.sql`, `scripts/*.py`, `.claude/agents/*.md`, `tests/routing/*`).
It does **not** describe a separately-deployed codebase — `manta-hub/maestro/*.py` is the target module
path referenced by these guides; treat every code block flagged **Status: design / pending implementation**
as a spec to build against, not as something already running in production. Where a component **is**
live today (the Supabase schema, the CI/CD workflows, the routing keyword seed data), it is marked
**Status: deployed**.

Read `CLAUDE.md` (repo root) first — it is the canonical agent registry and routing-rule source that
everything in this guide derives from.

---

## Status legend

| Marker | Meaning |
|--------|---------|
| ✅ Deployed | Exists and runs today (Supabase tables/functions, CI/CD workflows, scripts in `scripts/`) |
| 🔨 Pending | Designed and spec'd, not yet implemented in `manta-hub/maestro/` |
| 📐 Design phase | Architecture agreed, implementation guide exists, no code written yet |

---

## Table of Contents

1. [Routing Engine Architecture](#1-routing-engine-architecture)
2. [Advanced Features (by phase)](#2-advanced-features-by-phase)
3. [Debugging & Optimization](#3-debugging--optimization)
4. [Deployment & Rollback](#4-deployment--rollback)
5. [Deployment Runbook (condensed)](#5-deployment-runbook-condensed)
6. [Troubleshooting Tree](#6-troubleshooting-tree)
7. [Reference Index](#7-reference-index)

---

## 1. Routing Engine Architecture

### 1.1 Maestro Router class

**Status: 📐 Design phase** — target file `manta-hub/maestro/router.py`.

The router's job in every implementation guide follows the same five-step shape. This is the
canonical skeleton (assembled from `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md` and
`docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md`, which both extend the same class):

```python
# manta-hub/maestro/router.py

class MaestroRouter:
    def __init__(self):
        self.orchestrator = MaestroOrchestrator()      # Phase 2.2
        self.advanced_router = AdvancedRouter()          # Phase 3.5
        # ... agent registry, keyword cache, Supabase client

    def route_and_respond(self, user_prompt: str) -> Dict:
        # 1. Score all agents (keyword-based)
        scores = self._score_agents(user_prompt)
        primary_agent = max(scores, key=scores.get)
        primary_score = scores[primary_agent]

        remaining = {a: s for a, s in scores.items() if a != primary_agent}
        secondary_agent = max(remaining, key=remaining.get) if remaining else None
        secondary_score = remaining[secondary_agent] if secondary_agent else 0
        score_gap = primary_score - secondary_score

        # 2. Two DIFFERENT ambiguity checks live at two DIFFERENT layers — see 1.4
        #    - Orchestrator (Phase 2.2):     score_gap < 0.10           → dispatch BOTH agents
        #    - Advanced tie-breaker (3.5):   score_gap < 0.15 OR
        #                                    primary_score < 0.70      → LLM disambiguation
        ...

    def _score_agents(self, user_prompt: str) -> Dict[str, float]:
        """Keyword-based scoring. Returns {"agente-saneamento": 0.92, ...}."""
        ...

    def _dispatch(self, agent_slug: str, prompt: str) -> str:
        """Invoke the specialized agent (.claude/agents/{slug}.md system prompt)."""
        ...

    def _log_routing_event(self, **kwargs):
        """Insert into maestro_routing_trace (see §1.3 / §3)."""
        ...
```

Two things to internalize immediately, because they trip people up in code review:

- **`_score_agents` is keyword scoring only.** It never calls an LLM. It is fast (no API round-trip)
  and deterministic, which is why it runs on every request before anything else.
- **There are two independent "ambiguous" checks**, owned by two different Phase 2/3 features, with
  **different thresholds and different responses**:
  - Phase 2.2 Orchestrator: `score_gap < 0.10` → dispatch to **both** agents in parallel, then merge.
  - Phase 3.5 Advanced Router: `score_gap < 0.15 OR primary_score < 0.70` → ask an LLM to **pick one**.
  Do not confuse these two thresholds when reading `maestro_routing_trace` — a row can be ambiguous
  for one system and not the other. See §2.1 and §2.2.

### 1.2 Agent definitions (`.claude/agents/*.md` metadata)

Every specialized agent is defined as a markdown file in `.claude/agents/`. The router treats each
file as a system-prompt + metadata source. Fields used consistently across the agent files in this
repo (see `.claude/agents/maestro-orchestrator.md` for the fullest example):

| Field | Purpose | Example |
|-------|---------|---------|
| Title / Manta code | Agent identity (`Manta 16`) | `Manta 16 — Maestro Orchestrator Agent` |
| **Role** | One-line description used in tie-breaker prompts | `Synthesis and coordination agent for multi-agent responses` |
| **Tier** | Default model (`haiku`/`sonnet`/`opus`) | `Opus (complex reasoning required)` |
| **Activation** | The trigger condition from the router | `score gap < 10 points` |
| Input/Output spec | Python `@dataclass` blocks documenting the contract | `OrchestratorInput` / `OrchestratorOutput` |
| System Prompt | The literal prompt text used when dispatching | fenced code block |
| Deployment Checklist | Tracks what's built vs pending for that agent | checkbox list |

The 5 vertical (segment) agents added in v4.2 — `agente-portos`, `agente-aeroportos`,
`agente-saneamento`, `agente-energia`, `agente-barragens` — follow the same pattern but are simpler
(no orchestration role). `CLAUDE.md`'s "MAPA COMPLETO DE AGENTES" table is the master index of all 20
agents, their aliases, default tier, and status; **that table, not the individual `.md` files, is what
you update first when adding/retiring an agent**, then mirror the change into the corresponding
`.claude/agents/*.md`.

`_get_agent_descriptions()` (used by the Phase 3.5 tie-breaker, §2.2) pulls a one-line description per
agent — today those are hardcoded in the implementation guide as a stopgap; the intended source is
"Load from CLAUDE.md or agent .md files" (see `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md` line
~302-311). If you're implementing this for real, parse the CLAUDE.md table rather than hand-copying
strings — that's the drift risk the TODO is flagging.

### 1.3 Keyword tables (`maestro_routing_keywords` schema)

**Status: ✅ Deployed** (`supabase/migrations/2026_07_26_add_feedback_tables.sql`).

```sql
CREATE TABLE IF NOT EXISTS maestro_routing_keywords (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_slug text NOT NULL,
  keyword text NOT NULL,

  confidence float DEFAULT 0.5,   -- 0-1: how confident this keyword → agent
  frequency int DEFAULT 0,        -- times user has approved this route
  last_approved timestamp DEFAULT NULL,

  source text DEFAULT 'manual',   -- 'manual' or 'feedback_learning'
  feedback_count int DEFAULT 0,

  active boolean DEFAULT true,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

CREATE UNIQUE INDEX idx_maestro_routing_keywords_unique
  ON maestro_routing_keywords(agent_slug, keyword);
```

There is also an older, simpler seed of the same table shipped in
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` (a `(agent_slug, keyword, priority)` insert
for the 5 v4.2 verticals — `priority` there is an integer weight, not the 0-1 `confidence` used later).
**Reconcile these before running both migrations against a fresh project**: the v4.2 migration's
comment explicitly says "Comentar o bloco inteiro caso o Maestro carregue as keywords direto do
CLAUDE.md via parsing" — i.e. that insert is optional and may conflict with the feedback-tables
version. If you already track keywords in Supabase, don't insert both; align on `confidence` (0-1)
as the canonical scoring unit and either drop or convert the `priority` integers.

The keyword table is **self-tuning** via `process_routing_feedback()` (see §2.3/§4.1): every user
approval nudges `confidence += 0.05` (capped at 1.0) for the keywords of the approved agent; every
rejection nudges `confidence -= 0.10` (floored at 0.1).

### 1.4 Confidence scoring (how keyword matches translate to scores)

**Status: 📐 Design phase for the exact aggregation function** — but the *shape* of a score is
demonstrated extensively in `tests/routing/test_multiagent_dispatch.md`. A score is the sum of
per-keyword-match contributions, each contribution itself a function of `keyword.confidence` weighted
by specificity/length. Example from Case 1.1 (`docs/../tests/routing/test_multiagent_dispatch.md`):

```
Primary: agente-barragens (score: 0.95)
  Keywords matched: CFRD (0.30), barragem (0.28), altura 100m (0.18), UHE (0.15), viabilidade (0.04)

Secondary: agente-energia (score: 0.88)
  Keywords matched: LT 500kV (0.32), transmissão (0.28), SE/subestação (0.18), cronograma (0.10)
```

Reading this pattern across all test cases in that file gives you the practical rules of thumb the
team has been designing against:
- More specific / rarer terms score higher per match (`AySA` seeded at priority 120 vs generic
  `saneamento` at 100 in the v4.2 keyword insert — see §1.3).
- A prompt's total score for an agent is a **sum, not an average**, of matched-keyword contributions
  — so longer, more detailed prompts naturally produce higher absolute scores across the board, which
  is why ambiguity is measured as a **gap** between agents, not an absolute score alone.
- `score_gap = primary_score - secondary_score` is the single number both Phase 2.2 and Phase 3.5
  read, but they react to it differently (§1.1, §2.1, §2.2).
- False-ambiguity guard: Case 5.1 in the same test file shows a `score_gap = 0.18` (> 0.10) case that
  must **not** trigger the orchestrator even though a low-scoring secondary agent (`agente-barragens`
  at 0.78) technically "matched" — this is the negative test to keep in your suite.

---

## 2. Advanced Features (by phase)

### 2.1 Phase 2.2: Orchestrator agent (Manta 16)

**Status: 📐 Design phase.** Spec: `.claude/agents/maestro-orchestrator.md`. Implementation guide:
`docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md`. Roadmap entry: `docs/PHASE-2-ROADMAP.md` §2.2
(Aug 10 – Aug 31 window).

**When it triggers**: `score_gap(primary, secondary) < 0.10` (10 percentage points). Below that gap,
the router treats the query as genuinely multi-domain rather than "keyword noise near the boundary."

**How it works**:

```
Manta 00 (Maestro)
  ├─> primary_agent.invoke(prompt)     → response A
  ├─> secondary_agent.invoke(prompt)   → response B
  └─> Manta 16 (Orchestrator, Sonnet)
       → merge(A, B)
       → identify ≥2 cross-concerns with impact direction (A→B or B→A)
       → recommend execution sequence + handoff points
       → synthesized response
```

The `MaestroOrchestrator.orchestrate()` method (full listing in
`docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md`) calls Sonnet with a system prompt that **mandates** a
fixed markdown structure (`## Visão Integrada` → `### Responsabilidade Primária` →
`### Responsabilidade Secundária` → `### Cross-Concerns` → `### Sequência Recomendada` →
`### Pontos de Handoff`), then parses that structure back out with `extract_section()`. This
prompt-then-parse pattern is fragile by construction — if you touch the system prompt's header
wording, you must also update `extract_section()`'s literal string matches or parsing silently
breaks and every field falls back to `""`.

**Quality gate**: `score_merge_quality()` grades the merged response 0–1 across five weighted
dimensions (perspective coverage 20%, cross-concern ID 25%, coordination clarity 20%, actionability
20%, coherence 15%). Target ≥ 0.75. This rubric is also the one used by
`tests/routing/test_multiagent_dispatch.md`'s "Merge Quality Target" per test case — **use that file
as your test fixture set** when you implement `orchestrator.py`; it already has 10+ worked examples
across saneamento/energia/portos/aeroportos/barragens pairs plus 2 negative (non-ambiguous /
conflicting-recommendation) cases.

**Deliverable status** (from `docs/PHASE-2-ROADMAP.md`):
- [x] `.claude/agents/maestro-orchestrator.md` — spec ✅
- [x] `tests/routing/test_multiagent_dispatch.md` — 10+ scenarios ✅
- [ ] `manta-hub/maestro/orchestrator.py` — merge logic — **pending**
- [ ] Router integration (ambiguity detection → dispatch) — **pending**

### 2.2 Phase 3.5: LLM tie-breaker (Sonnet, prompt engineering)

**Status: 📐 Design phase.** Implementation guide: `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md`.
Roadmap entry: `docs/PHASE-3-ROADMAP.md` §3.5 (Feb 01 – Feb 28, 2027 window). **Do not confuse this
with the Orchestrator (§2.1)** — the tie-breaker picks **one** winner; the Orchestrator merges **two**
full responses. They also disagree on model: the tie-breaker's guide pins
`claude-sonnet-4-20250514`; the Phase 3 roadmap's earlier sketch (`route_with_fallback`) uses
`tier='haiku'` for a cheaper/faster disambiguation call. **Reconcile which tier ships** before
building this — Sonnet gives better reasoning on genuinely hard cases, Haiku is cheaper and matches
the "fast fallback" framing in the roadmap doc. The Advanced Routing guide is the more complete /
later spec, so default to Sonnet unless cost data says otherwise (see §3.3 for how to pull that data
once this is live).

**Trigger**: `score_gap < 0.15 OR primary_score < 0.70` (`AdvancedRouter.should_use_tie_breaker`).

**Prompt engineering** — the system prompt is intentionally terse and decisive:

```
You are the Maestro Router's tie-breaker. Your job is to resolve ambiguous
routing decisions by choosing the single best agent for a user query.
...
Output format:
{
    "primary_agent": "agent-slug",
    "confidence": 0.85,
    "reasoning": "Short explanation of why this agent is best"
}

Be concise and decisive. No hedging. The user will dispatch to this agent.
```

Key implementation details worth internalizing before you build this:
- **Parsing is defensive by necessity.** `_parse_decision()` finds the first `{` and last `}` in the
  response text, attempts `json.loads`, and falls back to the keyword-based `primary_agent` on *any*
  failure (missing JSON, malformed JSON, unexpected exception). This fallback path also flips
  `tie_breaker_used=False` in the logged decision — that flag is how you'll distinguish "tie-breaker
  ran and won" from "tie-breaker was invoked but silently failed" in `maestro_tiebreaker_events`.
- **The LLM's choice is validated against the candidate set**: if the model hallucinates a third
  agent slug not in `{primary_agent, secondary_agent}`, the code forces it back to `primary_agent`.
  Never trust free-text agent-slug output without this guard.
- Logging table: `maestro_tiebreaker_events` (full DDL in the implementation guide) — records
  `primary_from_keywords` vs `primary_from_llm` side by side, which is exactly the field pair
  `TiebreakerAnalytics.get_effectiveness_metrics()` diffs to compute a "decision change rate."

**Success metrics to watch once deployed** (targets from the implementation guide):

| Metric | Target |
|--------|--------|
| Tie-Breaker Usage Rate | 5–10% of queries |
| Approval Rate | > 85% |
| Decision Change Rate (LLM overrides keywords) | 30–50% |
| Latency Addition | < 500 ms |

**Rollout plan specified in the guide**: canary 10% → 50% → 100% (see §4.1).

### 2.3 RAG integration (vector search, context injection)

**Status: ✅ Deployed (schema + scripts)**, ingestion content is 🔨 in progress.
Migration: `supabase/migrations/2026_07_25_add_pgvector_to_rag.sql`. Runbook:
`docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md`. Ingestion script: `scripts/ingest_rag_batch.py`.
Embedding sync: `supabase/embeddings_sync.py`.

**Schema**: `rag_chunks` gained a `vector(1536)` `embedding` column (pgvector, `ivfflat` index,
cosine ops) plus a generated `tsvector` `search_vector` column for full-text search — the table
supports both semantic and keyword search from day one.

**Two search functions ship in the migration**:

```sql
-- Pure vector similarity
SELECT * FROM search_rag_by_similarity(
  query_embedding := $1,
  collection_filter := 'san:br:',
  limit_results := 10,
  similarity_threshold := 0.5
);

-- Hybrid: 30% keyword (ts_rank) + 70% vector (cosine) by default
SELECT * FROM search_rag_hybrid(
  query_text := 'Como dimensionar uma ETA para 100 mil habitantes?',
  query_embedding := $1,
  collection_filter := 'san:br:',
  keyword_weight := 0.3,
  vector_weight := 0.7
);
```

**5 collections**, one per v4.2 vertical, each with a storage prefix used as the `collection_slug`
filter above (`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`):

| Slug | Prefix | Seed sources |
|------|--------|--------------|
| saneamento | `san:` | SNIS, Lei 14.026, NBR 12211-12218, editais BNDES, AySA |
| energia | `ene:` | ANEEL editais, EPE R1-R5, ONS, IEEE 738/80/60826 |
| portos | `por:` | ANTAQ, PIANC, ROM 0.2/2.0, NBR 9782/6122 |
| aeroportos | `aer:` | ANAC RBAC 154, ICAO Annex 14, FAA ACs |
| barragens | `bar:` | ICOLD, CBDB, SIGBM, SNISB, Lei 12.334/14.066 |

**Context injection pattern**: the agent dispatch layer is expected to call `search_rag_hybrid()` (or
`search_rag_by_similarity()` for a cheaper pure-vector path) scoped to the dispatched agent's
collection, and prepend the top-K chunks to the agent's system prompt before the actual LLM call —
this is the "RAG integration" referred to across the segment agent `.claude/agents/*.md` files, but
the injection call site itself lives in the not-yet-written `manta-hub/maestro/router.py` dispatch
path, not in this repo.

**Ingestion pipeline** (already scripted, see `docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md` for the full
walkthrough):

```bash
# Dry run first — always
python scripts/ingest_rag_batch.py \
  --segment saneamento --tier T1 \
  --source docs/rag-sources/saneamento/T1-normas/ \
  --dry-run --max-chunks 5

# Real ingestion
python scripts/ingest_rag_batch.py \
  --segment saneamento --tier T1 \
  --source docs/rag-sources/saneamento/T1-normas/ \
  --max-chunks 3
```

CI/CD: `.github/workflows/ingest-rag-monthly.yml`, scheduled `0 2 1 * *` (1st of month, 2 AM UTC),
also `workflow_dispatch`-able for on-demand runs per segment/tier.

---

## 3. Debugging & Optimization

### 3.1 Query an agent — trace a routing decision

**Local/manual smoke test** (`scripts/test_routing.py`): parses test cases out of
`tests/routing/prompts.md` (format: `` - [ ] `prompt text` → **agent-name** ``), calls the model
directly with a routing-only system prompt, and scores exact/partial/miss:

```bash
python scripts/test_routing.py tests/routing/prompts.md -v
python scripts/test_routing.py tests/routing/prompts.md --format json --output results.json
```

Exit code is non-zero if `accuracy_percent < 90` — wire this into CI as a routing regression gate.

**Live trace lookup** (once the router is instrumented per §3.2): every dispatch writes one row to
`maestro_routing_trace`. To trace a single query after the fact:

```sql
SELECT
  timestamp, prompt, primary_agent, primary_score,
  alternate_agents, score_gap, is_ambiguous,
  executed_agent, user_approved
FROM maestro_routing_trace
WHERE prompt_hash = encode(sha256('exact prompt text'::bytea), 'hex')
ORDER BY timestamp DESC
LIMIT 1;
```

`prompt_hash` is a `UNIQUE` sha256 of the raw prompt — use it for dedup and for building a
click-through link from a Cowork feedback button back to the originating trace row (see
`insert_routing_trace()` in `docs/MONITORING-MAESTRO.md` §2 for the Python helper that computes it).

### 3.2 Analyze the routing trace table

**Status: ✅ Deployed schema.** Tables/views: `maestro_routing_trace`, `maestro_routing_quality`
(view), `maestro_metrics_daily`. Full DDL in
`supabase/migrations/2026_07_25_add_maestro_monitoring.sql`.

Routing quality over the last 7 days:

```sql
SELECT
  date, primary_agent, total_cases, ambiguous_cases,
  ROUND(100.0 * ambiguous_cases / total_cases, 2) AS ambiguity_rate,
  ROUND(100.0 * approved_cases / total_cases, 2) AS approval_rate,
  median_gap
FROM maestro_routing_quality
WHERE date >= CURRENT_DATE - interval '7 days'
ORDER BY date DESC, total_cases DESC;
```

Orchestration rate + confidence (Phase 2.2 specific):

```sql
SELECT
  COUNT(*) AS total_queries,
  SUM(CASE WHEN is_ambiguous THEN 1 ELSE 0 END) AS ambiguous_queries,
  ROUND(100.0 * SUM(CASE WHEN is_ambiguous THEN 1 ELSE 0 END) / COUNT(*), 1) AS orchestration_rate,
  AVG(CASE WHEN is_ambiguous THEN orchestrator_confidence ELSE NULL END) AS avg_orchestration_confidence
FROM maestro_routing_trace
WHERE created_at > now() - interval '7 days';
```

Alert query — ambiguity spike per agent (feed into Slack/GitHub-issue automation):

```sql
SELECT date, primary_agent, ambiguous_cases,
       ROUND(100.0 * ambiguous_cases / total_cases, 2) AS ambiguity_pct
FROM maestro_routing_quality
WHERE date = CURRENT_DATE - interval '1 day'
  AND ambiguous_cases > 10;
```

### 3.3 Performance profiling (latency, token usage)

**Status: ✅ Deployed schema.** Table: `maestro_runtime_metrics` (per-dispatch row: `latency_ms`,
`prompt_tokens`, `response_tokens`, `model_tier`, `fallback_count`, `routing_confidence`).
Nightly rollup function: `compute_daily_metrics(p_date)` → `maestro_metrics_daily`
(`latency_p50/p95/p99`, `haiku_count/sonnet_count/opus_count`, `fallback_rate`).

Current-hour dashboard (uses the `maestro_metrics_current_hour` view):

```sql
SELECT * FROM maestro_metrics_current_hour ORDER BY request_count DESC;
```

Latency SLO tracking, with a traffic-light status column:

```sql
SELECT
  date, agent_slug, total_requests,
  ROUND(latency_p50::numeric) AS p50_ms,
  ROUND(latency_p95::numeric) AS p95_ms,
  ROUND(latency_p99::numeric) AS p99_ms,
  CASE
    WHEN latency_p95 < 300 THEN '✅ OK'
    WHEN latency_p95 < 500 THEN '⚠️  WARNING'
    ELSE '❌ SLA_BREACH'
  END AS slo_status
FROM maestro_metrics_daily
WHERE date = CURRENT_DATE - interval '1 day'
ORDER BY latency_p99 DESC;
```

Token efficiency / model-tier cost audit:

```sql
SELECT
  date, agent_slug, total_requests,
  ROUND(total_tokens::numeric / total_requests, 0) AS avg_tokens_per_request,
  haiku_count AS cheap_tier, sonnet_count AS mid_tier, opus_count AS expensive_tier
FROM maestro_metrics_daily
WHERE date >= CURRENT_DATE - interval '30 days'
ORDER BY date DESC, total_tokens DESC;
```

**Recommended alert thresholds** (from `docs/MONITORING-MAESTRO.md` §4):

| Alert | Threshold | Action |
|-------|-----------|--------|
| Latency P95 | > 500 ms | Slack notify, investigate tier strategy |
| Fallback Rate | > 5% | Page on-call, check routing issues |
| Ambiguous Cases | > 10/day/agent | File GitHub issue for routing improvement |
| Opus Usage | > 30%/day | Cost review, evaluate Sonnet capability |

Nightly aggregation runs via Supabase Edge Function calling `compute_daily_metrics()` — see the Deno
snippet in `docs/MONITORING-MAESTRO.md` §5 if you need to redeploy that function.

### 3.4 A/B testing results (comparing routing strategies)

**Status: ✅ Deployed schema, not yet run.** Table: `maestro_routing_ab_tests`
(`supabase/migrations/2026_07_26_add_feedback_tables.sql`).

```sql
CREATE TABLE maestro_routing_ab_tests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  test_name text NOT NULL,
  test_slug text UNIQUE NOT NULL,
  variant_a_prompt text NOT NULL,   -- original keywords
  variant_b_prompt text NOT NULL,   -- new/optimized keywords
  control_rate float DEFAULT 0.9,   -- 90% on variant A
  treatment_rate float DEFAULT 0.1, -- 10% on variant B
  status text DEFAULT 'draft',      -- draft, active, paused, completed
  variant_a_samples int DEFAULT 0,
  variant_a_approval_rate float DEFAULT 0.0,
  variant_b_samples int DEFAULT 0,
  variant_b_approval_rate float DEFAULT 0.0,
  ...
);
```

To read results on an active/completed test:

```sql
SELECT test_name, status,
       variant_a_samples, variant_a_approval_rate,
       variant_b_samples, variant_b_approval_rate,
       variant_b_approval_rate - variant_a_approval_rate AS lift
FROM maestro_routing_ab_tests
WHERE test_slug = 'saneamento-keyword-v2'
ORDER BY started_at DESC;
```

This is the same infrastructure that powers the **canary rollout** described in §4.1 — a canary is
just an A/B test where you monitor `variant_b_approval_rate` climb through 10% → 50% → 100% traffic
before retiring variant A.

---

## 4. Deployment & Rollback

### 4.1 Promoting new keyword tables (safe rollout, canary)

The canary pattern used across every implementation guide in this repo (Orchestrator, Advanced
Router) is the same three-stage ramp:

```
Stage 1:  10% of matching traffic → new keyword set / new feature
             ↓  monitor approval_rate + latency for ≥ 48h
Stage 2:  50% of matching traffic
             ↓  monitor again
Stage 3: 100% — old keyword set retired
```

Practical steps for promoting a **new/adjusted keyword set** in `maestro_routing_keywords`:

1. Insert or update rows with `source = 'manual'` (or leave `source = 'feedback_learning'` if the
   change came out of `analyze_feedback_and_recommend()`, §3.2/§4.3) and `active = true`.
2. If you want a true A/B split rather than an in-place edit, register the change as a row in
   `maestro_routing_ab_tests` with `variant_a_prompt`/`variant_b_prompt` holding the two keyword
   configurations, `status='active'`, `treatment_rate=0.10` to start.
3. Watch `maestro_routing_quality` (approval_rate, ambiguity_rate) and
   `maestro_routing_ab_tests.variant_b_approval_rate` for the canary window before bumping
   `treatment_rate`.
4. Only flip `status='completed'` and fold variant B into the single active keyword set once
   `variant_b_approval_rate >= variant_a_approval_rate` holds for the full 48h+ window.

This exact ramp (10% → 50% → 100%) is explicitly called out as the last checklist item in
`docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md`'s Deployment Checklist for the Phase 3.5 tie-breaker
— reuse it for any routing-affecting change, not just that feature.

### 4.2 Rollback procedure (reverting to previous keywords)

**Status: ✅ Deployed pattern**, demonstrated concretely in
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`. Every routing-keyword migration in this repo
follows the same convention: the forward migration is idempotent (`ON CONFLICT DO NOTHING`), and a
matching `DELETE` block is kept commented at the bottom of the same file for manual rollback:

```sql
-- =====================================================================
-- ROLLBACK (executar manualmente se necessário)
-- =====================================================================
-- BEGIN;
--
-- DELETE FROM maestro_routing_keywords WHERE agent_slug IN
--   ('agente-saneamento','agente-energia','agente-portos',
--    'agente-aeroportos','agente-barragens');
--
-- DELETE FROM sp_agent_routing WHERE agent_slug IN (...);
-- DELETE FROM rag_collections WHERE slug IN (...);
--
-- COMMIT;
```

For a feedback-driven keyword drift (confidence decayed too aggressively after a burst of rejections,
§1.3), the rollback is a targeted `UPDATE`, not a `DELETE`:

```sql
-- Reset confidence for an over-penalized agent back to baseline
UPDATE maestro_routing_keywords
SET confidence = 0.8, updated_at = now()
WHERE agent_slug = 'agente-energia' AND source = 'manual';
```

**Full rollback checklist** (from `docs/DEPLOY-v4.2.md` §6, generalize beyond v4.2):
1. **Git**: `git revert -m 1 <merge-sha>` on the affected repos — never force-push a revert.
2. **Supabase**: run the commented `ROLLBACK` block at the bottom of the migration that introduced
   the change.
3. **SharePoint**: rename any newly-created folders to `*_DEPRECATED` rather than deleting — content
   may already have been placed there by users.
4. **CI/CD**: `gh workflow disable <workflow>.yml` if the rollback is in response to a bad automated
   job (RAG ingestion, SharePoint sync) — see `docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md` and
   `docs/RUNBOOK-PHASE-2.5-SHAREPOINT-SYNC.md` for the per-workflow rollback commands.

### 4.3 Data migration (updating agent definitions)

Two distinct migration concerns show up under this heading — don't conflate them:

**(a) Supabase schema/data migrations** — plain numbered `.sql` files under `supabase/migrations/`,
applied with:

```bash
supabase migration list                 # see what's already applied
supabase db push --dry-run              # preview
supabase db push                        # apply
# or, directly:
psql "$SUPABASE_DB_URL" -f supabase/migrations/<file>.sql
```

Every migration in this repo wraps its body in `BEGIN … COMMIT`, so a failure mid-migration rolls
back cleanly with no partial state (see the migration files themselves for the pattern).

**(b) Agent-definition sync to SharePoint** — `.claude/agents/*.md` is the source of truth; changes
are synced out to SharePoint's `01-agentes-fundamentais/{agent}/SKILL.md` by
`scripts/sync_agents_to_sharepoint.py`, triggered by `.github/workflows/sync-agents-to-sharepoint.yml`
on push to `main` touching `.claude/agents/*.md` or `CLAUDE.md`. Always dry-run first:

```bash
python scripts/sync_agents_to_sharepoint.py --all --dry-run
python scripts/sync_agents_to_sharepoint.py --agent agente-saneamento   # test one
python scripts/sync_agents_to_sharepoint.py --all                       # full sync
```

If you're changing an agent's routing keywords **and** its `.md` metadata in the same PR, sequence
it as: (1) apply the Supabase keyword migration, (2) merge the `.claude/agents/*.md` change to `main`
(which auto-fires the SharePoint sync), (3) verify both independently — a keyword-only change with no
`.md` diff will not trigger the SharePoint workflow at all (path filter is `.claude/agents/*.md` /
`CLAUDE.md` only).

---

## 5. Deployment Runbook (condensed)

This is a quick-reference version of the full runbooks in `docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md`,
`docs/RUNBOOK-PHASE-2.5-SHAREPOINT-SYNC.md`, and `docs/DEPLOYMENT-PHASE-2.md`. Follow those docs for
the complete step-by-step; use this as the checklist during an actual deploy window.

### Pre-flight (once per environment)

- [ ] GitHub secrets set: `ANTHROPIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
      `SHAREPOINT_SITE_ID`, `SHAREPOINT_DRIVE_ID`, `MICROSOFT_GRAPH_TOKEN`, `SLACK_WEBHOOK_URL` (opt).
      Verify: `gh secret list`.
- [ ] Supabase migrations applied in order:
      `2026_07_25_add_pgvector_to_rag.sql` → `2026_07_25_add_maestro_monitoring.sql` →
      `2026_07_26_add_feedback_tables.sql` → (segment-specific migrations, e.g. `..._s6_s10.sql`).
      Verify: `supabase migration list`, then spot-check with the queries in §4.3(a).
- [ ] `supabase/embeddings_sync.py` scheduled (daily) for any newly-ingested RAG chunks missing
      embeddings.

### Feature-specific rollout

| Feature | Reference | Key gate before 100% |
|---------|-----------|----------------------|
| RAG ingestion (new segment/tier) | `docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md` | Dry-run passes, ≥1 hour spot-check of `rag_chunks` counts |
| SharePoint sync | `docs/RUNBOOK-PHASE-2.5-SHAREPOINT-SYNC.md` | One agent synced manually + verified before `--all` |
| Orchestrator (2.2) | `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md` | 5+ real ambiguous prompts scored ≥ 0.75 merge quality |
| Tie-breaker (3.5) | `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md` | 2-week staging monitor, then canary 10%→50%→100% |
| Keyword table change | §4.1 above | 48h canary window, approval_rate stable or improved |

### Go-live verification (all features)

```sql
-- Confirm rows are flowing after go-live
SELECT COUNT(*) FROM maestro_routing_trace WHERE timestamp > now() - interval '1 hour';
SELECT COUNT(*) FROM maestro_runtime_metrics WHERE timestamp > now() - interval '1 hour';
```

If either returns 0 after real traffic should have occurred, the router isn't calling
`_log_routing_event` / `insert_maestro_metric` — check the dispatch integration, not the database.

### Post-deploy monitoring window

- First 48h: watch `maestro_routing_quality` and `maestro_metrics_daily` (latency SLO) hourly.
- First 7 days: run the weekly feedback job manually once
  (`SELECT * FROM analyze_feedback_and_recommend(CURRENT_DATE - interval '1 day')`) even if it's not
  on cron yet, to catch early keyword-drift signals.

---

## 6. Troubleshooting Tree

Start at the top; follow the branch that matches your symptom.

```
Query routed to the WRONG agent
├─ Was the score_gap small (<0.10 or <0.15 depending on feature)?
│   ├─ YES → Check if Orchestrator/tie-breaker even fired
│   │         (maestro_routing_trace.is_ambiguous, maestro_tiebreaker_events row exists?)
│   │        ├─ Neither fired → router integration is missing/broken (§1.1) — this is
│   │        │                  the "pending implementation" gap; not a data problem.
│   │        ├─ Tie-breaker fired but chose wrong agent →
│   │        │     read `reasoning` in maestro_tiebreaker_events; if reasoning is generic/
│   │        │     empty, _parse_decision() likely hit the fallback path (JSON parse failed) —
│   │        │     check tie_breaker_used flag: false means the fallback silently used
│   │        │     keyword primary_agent, not an LLM choice at all (§2.2).
│   │        └─ Orchestrator fired, merge picked wrong "recommended_lead" →
│   │              check score_merge_quality() output; low cross-concern count usually
│   │              means the system prompt's markdown headers drifted from what
│   │              extract_section() is matching (§2.1).
│   └─ NO (score_gap was large, high-confidence miss) →
│         this is a KEYWORD problem, not an ambiguity-logic problem.
│         → Pull the keyword contributions for both agents (§1.4 pattern) for this
│           exact prompt; is the "wrong" agent's keyword simply mis-weighted?
│         → File as a `maestro_user_feedback(approved=false)` if a user reported it,
│           then check `analyze_feedback_and_recommend()` output next cycle (§4.3).
│         → If confidence has drifted from repeated rejections (§1.3 decay), consider
│           the manual UPDATE reset in §4.2 rather than waiting for it to self-correct.

Latency is high / SLA breach
├─ Check maestro_metrics_daily.latency_p95 per agent_slug (§3.3)
│   ├─ One agent only → likely model_tier mismatch (check haiku/sonnet/opus distribution
│   │   for that agent — is it running Opus when Sonnet would do? See Opus Usage alert §3.3)
│   ├─ All agents, correlated with tie-breaker/orchestrator usage →
│   │   check orchestration_rate / tiebreaker usage rate (§2.1, §2.2 success metrics) —
│   │   an LLM-in-the-loop feature running more than its 5-10% target adds real latency;
│   │   this often means score_gap thresholds are mis-tuned and firing too often.
│   └─ All agents, no correlation → check RAG search latency (search_rag_hybrid is doing
│       both a keyword AND vector query — confirm the ivfflat index exists and lists=100
│       is still appropriate for current row count; §2.3).

Ambiguous-case rate is climbing (maestro_routing_quality.ambiguity_rate trending up)
├─ Is it concentrated in one agent pair (e.g., saneamento/energia)? →
│   this is expected for genuinely overlapping domains (see Test Suite 2/3 patterns in
│   tests/routing/test_multiagent_dispatch.md) — verify Orchestrator merge quality is
│   still ≥0.75 for that pair rather than trying to eliminate the ambiguity itself.
├─ Is it new (a segment just launched, e.g., v4.2 S6-S10)? →
│   expected during the settling period; monitor for ~2 weeks (per the tie-breaker
│   deployment checklist §2.2) before tuning keywords.
└─ Is it broad (many unrelated agent pairs)? →
    check if a keyword migration was recently applied with `priority`/`confidence` units
    accidentally mixed (§1.3 — the v4.2 migration's `priority` int vs the feedback-tables
    migration's `confidence` float are NOT the same scale).

SharePoint sync failing
├─ "Unauthorized" → client secret expired, regenerate in Azure Portal
│   (docs/RUNBOOK-PHASE-2.5-SHAREPOINT-SYNC.md Troubleshooting Reference)
├─ "Not found" → SHAREPOINT_DRIVE_ID or AGENTS_FOLDER_ID wrong, re-verify via Graph API
├─ Workflow never triggers → check path filter in
│   .github/workflows/sync-agents-to-sharepoint.yml matches the files you changed
└─ Rate limited → wait 60s, script has backoff built in; retry via
    `gh workflow run sync-agents-to-sharepoint.yml -f mode=all`

RAG ingestion failing
├─ "ANTHROPIC_API_KEY not found" → gh secret set ANTHROPIC_API_KEY --body "sk-ant-xxx"
├─ "Connection to Supabase failed" → verify SUPABASE_URL/SUPABASE_ANON_KEY, test with the
│   inline Python snippet in docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md Troubleshooting
├─ "Rate limit exceeded" → reduce --batch-size or add delay between segments
└─ Workflow never triggers → `gh workflow enable ingest-rag-monthly.yml`
```

---

## 7. Reference Index

**Docs**
- `CLAUDE.md` — master agent registry + routing rules (read this first)
- `docs/ORCHESTRATOR-IMPLEMENTATION-GUIDE.md` — Phase 2.2 full implementation
- `docs/ADVANCED-ROUTING-IMPLEMENTATION-GUIDE.md` — Phase 3.5 full implementation
- `docs/MONITORING-MAESTRO.md` — metrics schema, dashboard queries, alerts
- `docs/RUNBOOK-PHASE-2.4-RAG-DEPLOYMENT.md` / `docs/RUNBOOK-PHASE-2.5-SHAREPOINT-SYNC.md` — deploy runbooks
- `docs/DEPLOYMENT-PHASE-2.md` — cross-workstream deployment checklist + timeline
- `docs/DEPLOY-v4.2.md` — worked example of a full deploy + rollback for a segment expansion
- `docs/PHASE-2-ROADMAP.md` / `docs/PHASE-3-ROADMAP.md` — feature timelines and design sketches
- `.claude/agents/maestro-orchestrator.md` — Manta 16 agent spec

**Code / scripts**
- `scripts/test_routing.py` — routing accuracy/latency test runner
- `scripts/ingest_rag_batch.py` — RAG ingestion CLI
- `scripts/sync_agents_to_sharepoint.py` — agent `.md` → SharePoint sync CLI
- `supabase/embeddings_sync.py` — embedding backfill for `rag_chunks`

**Test fixtures**
- `tests/routing/prompts.md` — routing smoke tests (expected agent per prompt)
- `tests/routing/test_multiagent_dispatch.md` — orchestrator merge-quality worked examples + negative cases

**Supabase migrations (apply in this order on a fresh project)**
1. `2026_07_25_add_pgvector_to_rag.sql`
2. `2026_07_25_add_maestro_monitoring.sql`
3. `2026_07_26_add_feedback_tables.sql`
4. `2026_07_05_v4_2_agents_s6_s10.sql` (segment-specific; reconcile keyword units per §1.3)

**Key tables at a glance**

| Table | Written by | Read by |
|-------|-----------|---------|
| `maestro_routing_keywords` | manual seed, `process_routing_feedback()` | `_score_agents` |
| `maestro_routing_trace` | router per dispatch | `maestro_routing_quality`, tie-breaker analytics |
| `maestro_runtime_metrics` | router per dispatch | `compute_daily_metrics()`, dashboards |
| `maestro_user_feedback` | Cowork feedback button | `process_routing_feedback()`, `analyze_feedback_and_recommend()` |
| `maestro_tiebreaker_events` | `AdvancedRouter` | `TiebreakerAnalytics` |
| `maestro_routing_ab_tests` | canary/A-B setup | rollout decision (§4.1) |
| `rag_chunks` | `ingest_rag_batch.py`, `embeddings_sync.py` | `search_rag_by_similarity`, `search_rag_hybrid` |

---

**Owner**: Maestro team (manta-hub)
**Last synchronized against repo state**: 2026-07-26
