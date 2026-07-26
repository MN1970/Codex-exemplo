# PHASE 4.3 — Advanced Agent Capabilities

**Workstream**: 4.3 of PHASE 4 (Data & Intelligence Platform) | **Status**: 📋 Design specification
**Depends on**: 4.1 Data Platform Foundation (embeddings store), 4.2 Advanced Analytics (`maestro_recommendations`,
`maestro_agent_performance_scorecard`, `maestro_query_clusters`), Phase 2.1 feedback loop
(`maestro_user_feedback`, `maestro_routing_keywords`), Phase 2.2 Multi-Agent Orchestration
(`.claude/agents/maestro-orchestrator.md` — Manta 16), Phase 3.5 Advanced Routing (`maestro_tiebreaker_events`)
**Feeds into**: Phase 5 (not yet scoped)
**Reconciles with**: PHASE-4.2-ADVANCED-ANALYTICS.md §5.3, which names this workstream "Autonomous Optimization"
— that is the Agent Autonomy pillar below (§5); 4.3 is the broader container for all six capabilities
**Timeline (proposed)**: Dec 16, 2027 – Mar 15, 2028 (13 weeks)
**Owner**: Claude Code + Maestro agents, Gate humano: MN (sign-off required before any Tier 1/2 autonomy goes live)

---

## 0. Purpose & Scope

Phases 1–4.2 gave Maestro observability, a routing feedback loop, multi-agent orchestration for ambiguous
queries, and a recommendation engine that surfaces improvements but never applies them. Phase 4.3 turns the
20-agent registry from a **routing table with workers** into a system that improves itself under supervision,
specializes internally, talks to itself in a structured way, anticipates needs, acts autonomously inside
narrow guardrails, and can always show its work.

Six capability domains, in delivery order:

| # | Domain | Primary question it answers |
|---|--------|------------------------------|
| 1 | Agent Learning from Feedback | Does the system get measurably better from user corrections, without touching model weights? |
| 2 | Agent Specialization | Can each of the 20 agents go deeper without becoming 20 monoliths? |
| 3 | Agent Collaboration | Can agents share findings and hand off work without talking directly to each other? |
| 4 | Proactive Agents | Can Maestro surface the next useful action before the user asks? |
| 5 | Agent Autonomy | Which changes can the system apply itself, and under what guardrails? |
| 6 | Agent Reasoning Transparency | Can every decision be explained, sourced, and audited after the fact? |

### 0.1 Hard constraint — no model fine-tuning

The task framing for this phase used the words "fine-tuning via user feedback." That is explicitly **not**
what gets built. Manta does not fine-tune Claude model weights — Anthropic's API surface used across the
Manta stack (`claude_service.py`, per PK_07 layering) is prompt/context based, not a fine-tuning endpoint, and
"prompt congelado em código" / ad hoc weight changes are anti-patterns per the architecture skill. Every
"learning" mechanism below is one of three kinds, all evolutive and all human-gated:

1. **Routing-keyword confidence updates** — already live since Phase 2.1 (`maestro_routing_keywords`,
   `process_routing_feedback()`). Numeric, bounded, reversible. No human gate needed per-event (bounded by
   `LEAST/GREATEST` clamps already in the migration); aggregate drift is gated via Phase 4.2's recommendation
   queue.
2. **RAG relevance reinforcement** — embedding/collection-level signal (§1), not model weights.
3. **PK_08 / skill-content evolution** — proposals only, sitting in a pending queue until MN approves, exactly
   like the existing pesquisador-evolutivo pattern (`manta-arquiteto-ia` §11).

Nothing in this phase writes to a model's parameters. Nothing in this phase edits a skill's `SKILL.md` or an
agent's system prompt without a human clicking approve.

---

## 1. Agent Learning from Feedback

### 1.1 Learning lanes

| Lane | Signal | Storage | Update mechanism | Gate |
|------|--------|---------|-------------------|------|
| Routing | Approve/reject on agent selection | `maestro_routing_keywords` (existing) | `process_routing_feedback()` (existing) — ±0.05/-0.10 clamp | None per-event; weekly aggregate reviewed via `maestro_recommendations` |
| Content quality | Thumbs up/down + optional correction text on an agent's *answer* (not just routing) | `maestro_response_feedback` (new) | Classifier (Haiku) labels signal type → routes to lane 3 or flags RAG gap | Weekly digest to segment owner |
| Knowledge | "This answer was wrong/outdated because X" | `maestro_knowledge_gaps` (new) | Feeds `ingest_rag_batch.py` backlog or a `maestro_pk_update_proposals` row | MN approval before RAG/PK write |
| Exemplar | "This was a great answer" saved as a worked example | `maestro_agent_exemplars` (new) | Appended to the agent's few-shot bank, referenced at call time via retrieval, not embedded in the static system prompt | Segment owner curates monthly (dedupe, prune stale examples) |

### 1.2 Data schema

```sql
-- Content-quality feedback (distinct from maestro_user_feedback, which is routing-only)
CREATE TABLE IF NOT EXISTS maestro_response_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  routing_trace_id uuid REFERENCES maestro_routing_trace(id) ON DELETE CASCADE,
  agent_slug text NOT NULL,

  rating text NOT NULL,              -- 'up' | 'down'
  correction_text text DEFAULT NULL, -- free-text: what was wrong / what's missing
  signal_type text DEFAULT NULL,     -- classified by Haiku: 'content_quality'|'knowledge_gap'|'routing'|'tone'
  classified_at timestamp DEFAULT NULL,

  session_id text, user_id text,
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_response_feedback_agent ON maestro_response_feedback(agent_slug, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_response_feedback_down ON maestro_response_feedback(rating, signal_type) WHERE rating = 'down';

-- Knowledge gaps flagged for RAG ingestion or PK update
CREATE TABLE IF NOT EXISTS maestro_knowledge_gaps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  response_feedback_id uuid REFERENCES maestro_response_feedback(id),
  agent_slug text NOT NULL,
  collection_slug text,              -- target RAG collection, if applicable
  gap_summary text NOT NULL,
  suggested_source text,             -- URL/doc the user points to, if any
  status text DEFAULT 'open',        -- open, queued_for_ingest, queued_for_pk, dismissed, resolved
  created_at timestamp DEFAULT now(),
  resolved_at timestamp
);
CREATE INDEX IF NOT EXISTS idx_knowledge_gaps_open ON maestro_knowledge_gaps(status, agent_slug) WHERE status = 'open';

-- PK_08 / skill evolution proposals — mirrors pesquisador-evolutivo pattern, never auto-applied
CREATE TABLE IF NOT EXISTS maestro_pk_update_proposals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  target_file text NOT NULL,         -- e.g. '.claude/agents/agente-saneamento.md', 'CLAUDE.md'
  proposal_type text NOT NULL,       -- 'routing_rule'|'skill_instruction'|'system_prompt'|'exemplar_bank'
  source text NOT NULL,              -- 'feedback_loop'|'pesquisador_evolutivo'|'manual'
  diff_markdown text NOT NULL,       -- proposed diff, human-readable
  evidence jsonb DEFAULT '{}',       -- linked knowledge_gaps / response_feedback ids, counts
  status text DEFAULT 'pendente',    -- pendente, aprovado, rejeitado, aplicado
  reviewed_by text, reviewed_at timestamp,
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_pk_proposals_pending ON maestro_pk_update_proposals(status, created_at DESC) WHERE status = 'pendente';

-- Curated worked examples, retrieved (not baked into the static prompt)
CREATE TABLE IF NOT EXISTS maestro_agent_exemplars (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_slug text NOT NULL,
  prompt_summary text NOT NULL,
  response_summary text NOT NULL,
  embedding vector(1536),            -- reuses Phase 4.1 embeddings store
  quality_score float DEFAULT 1.0,   -- decays if unused; boosted on repeat retrieval + positive outcome
  source_response_feedback_id uuid REFERENCES maestro_response_feedback(id),
  active boolean DEFAULT true,
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_exemplars_agent ON maestro_agent_exemplars(agent_slug) WHERE active = true;
```

### 1.3 Flow

```
User rates response (Cowork "👍/👎 + comment")
  → maestro_response_feedback row
  → Haiku classifier labels signal_type (content_quality | knowledge_gap | routing | tone)
      routing        → existing process_routing_feedback() lane (Phase 2.1, unchanged)
      knowledge_gap   → maestro_knowledge_gaps (open) → weekly triage → ingest_rag_batch.py backlog
                        OR maestro_pk_update_proposals (if it's an instruction gap, not a document gap)
      content_quality → aggregated into Phase 4.2's maestro_recommendations (category='content_quality')
      exemplar (👍 + explicit "save as example") → maestro_agent_exemplars, embedded, retrievable
  → Nothing here writes to CLAUDE.md, a SKILL.md, or an agent .md automatically.
```

### 1.4 Guardrails

- No automatic edits to `CLAUDE.md`, any `SKILL.md`, or any `.claude/agents/*.md` — every content/instruction
  change is a `maestro_pk_update_proposals` row until MN sets `status='aprovado'`.
- Exemplar bank is retrieval-augmented (looked up per-request like a RAG chunk), never concatenated wholesale
  into a static system prompt — keeps token cost bounded and keeps the "prompt congelado" anti-pattern out.
- `quality_score` on exemplars decays over 90 days without reuse, preventing stale examples from persisting
  indefinitely (mirrors the RAG tiering already used in `ingest_rag_batch.py`).

---

## 2. Agent Specialization

### 2.1 Expertise layers (per vertical)

Every S1–S10 vertical gets the same four-layer shape; only the domain content differs. This is additive to
the existing single-file `.claude/agents/agente-<segmento>.md` — that file becomes the **L2 entry point**
that fans out to sub-agents when a request needs deeper handling.

| Layer | Role | Model tier | Example (agente-saneamento) |
|-------|------|------------|------------------------------|
| L1 — Intake | Classify request within the segment's 8 lifecycle phases (Q2 intake), extract structured params | Haiku | "É EVTE, projeto executivo, ou O&M?" |
| L2 — Domain generalist | Current agent behavior: answer directly for standard requests | Sonnet | General ETA/ETE/adutora guidance |
| L3 — Deep specialist sub-agents | Narrow, high-precision tasks that benefit from isolation and a tighter tool/context set | Sonnet or Opus | `sizing-calculator` (ETA/ETE dimensioning per NBR 12211-12218), `regulatory-compliance` (SNIS/Lei 14.026 checks), `cost-estimator` (SINAPI/orçamento) |
| L4 — Cross-vertical synthesis | Manta 16 (existing, Phase 2.2) — merges 2+ verticals | Opus | Barragem + Energia coordination |

### 2.2 File convention

```
.claude/agents/
├── agente-saneamento.md                      # L2 entry point (existing)
└── agente-saneamento/                        # L3 sub-agents (new)
    ├── intake-classifier.md                  # L1, Haiku, tools: none (pure classification)
    ├── sizing-calculator.md                  # L3, Sonnet, tools: Read/Bash (unit calc)
    ├── regulatory-compliance.md              # L3, Sonnet, tools: RAG(saneamento) read-only
    └── cost-estimator.md                     # L3, Sonnet, tools: RAG(orçamento), read-only
```

Same pattern for agente-energia, agente-portos, agente-aeroportos, agente-barragens, and the existing
S1–S4 infra verticals. L2 decides whether a request needs L1/L3 dispatch or can be answered directly —
this keeps the common case (a quick domain question) cheap and fast, and only pays the extra hop cost when
the request genuinely needs a narrow specialist.

### 2.3 Registry

```sql
CREATE TABLE IF NOT EXISTS maestro_subagent_registry (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_agent_slug text NOT NULL,     -- e.g. 'agente-saneamento'
  subagent_slug text NOT NULL,         -- e.g. 'sizing-calculator'
  layer text NOT NULL,                 -- 'L1'|'L3'
  model_tier text NOT NULL,            -- 'haiku'|'sonnet'|'opus'
  file_path text NOT NULL,             -- '.claude/agents/agente-saneamento/sizing-calculator.md'
  tools_allowed text[] DEFAULT ARRAY[]::text[],
  status text DEFAULT 'operational',   -- operational, design, deprecated
  created_at timestamp DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_subagent_unique ON maestro_subagent_registry(parent_agent_slug, subagent_slug);
```

### 2.4 Dispatch rule (in L2 agent body)

```
IF request matches a narrow, high-precision pattern (dimensioning calc, compliance check, cost estimate)
   → dispatch to matching L3 sub-agent (context: fork, read-only tools)
   → L2 synthesizes sub-agent output into the final answer
ELSE
   → L2 answers directly (current behavior, unchanged)
```

### 2.5 Guardrails

- Sub-agents are **read-only** by default (per `manta-arquiteto-ia` §9 anti-pattern: "Subagent com tools de
  escrita sem supervisão → restringir a read-only"). Any sub-agent that needs to write (e.g., update a
  quantitativo spreadsheet) goes through the existing skill layer instead, not a bespoke write-capable subagent.
- L1 intake classifiers stay on Haiku — this is pure triage, the exact case the model-tiering rule exists for.
- No new segment gets sub-agents before its L2 agent has ≥30 days of production routing volume — avoids
  building specialization for demand that doesn't exist yet (S5 Túneis, still "parcial," is explicitly out of
  scope for this phase).

---

## 3. Agent Collaboration

### 3.1 Builds on Manta 16 (existing)

Phase 2.2 already specified pairwise merge for ambiguous routing (score gap < 0.10). Phase 4.3 extends this
from a one-shot merge into a standing collaboration protocol with three additions: N-way (not just 2-way)
dispatch, a persistent shared-knowledge collection, and a structured message envelope so collaboration is
logged and auditable rather than being an implicit side effect of parallel dispatch.

### 3.2 Hub-and-spoke invariant (unchanged)

Agents **never** call each other directly. Every collaboration event passes through the Maestro router or
Manta 16 orchestrator, which is the only component allowed to fan out and merge. This is the same
anti-vazamento discipline as PK_07 layering, applied to the agent graph instead of the data/backend/frontend
graph.

```
agente-A  →  Maestro Router / Manta 16  ←  agente-B
                     ↓
            maestro_agent_messages (logged, typed, replayable)
```

### 3.3 Message envelope

```sql
CREATE TABLE IF NOT EXISTS maestro_agent_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  routing_trace_id uuid REFERENCES maestro_routing_trace(id),
  conversation_id uuid,               -- groups a multi-message exchange

  sender_agent text NOT NULL,         -- 'maestro-router' | agent slug
  recipient_agent text NOT NULL,      -- agent slug | 'maestro-orchestrator'
  message_type text NOT NULL,         -- 'query'|'response'|'handoff'|'broadcast'|'cross_concern_flag'

  payload jsonb NOT NULL,             -- structured, never raw free-text concatenation
  in_reply_to uuid REFERENCES maestro_agent_messages(id),

  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_agent_messages_conversation ON maestro_agent_messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_agent_messages_recipient ON maestro_agent_messages(recipient_agent, created_at DESC);
```

`payload` schema per `message_type`:

| Type | Payload shape |
|------|---------------|
| `query` | `{"question": str, "context": {...}, "requires_response_by": timestamp}` |
| `response` | `{"answer": str, "confidence": float, "sources": [...]}` |
| `handoff` | `{"from_step": str, "to_step": str, "trigger": str, "artifact_ref": str}` — mirrors Manta 16's `handoff_points` |
| `broadcast` | `{"event": str, "affected_agents": [...], "summary": str}` — e.g. a regulatory update (Phase 3.2) fanning out |
| `cross_concern_flag` | `{"concern": str, "primary_agent": str, "secondary_agent": str, "coordination_needed": str}` |

### 3.4 Shared knowledge — `cross_concerns` collection

Every resolved orchestration case (Manta 16 output with `user_approved=true`) is distilled into a reusable
pattern and written to a sixth RAG collection, alongside the five in `CLAUDE.md`'s RAG table:

```sql
-- Extends the existing rag_chunks table with a new collection_slug value: 'cross_concerns'
INSERT INTO rag_chunks (collection_slug, content, source_file, tier, metadata)
SELECT
  'cross_concerns',
  'Pattern: ' || primary_agent || ' + ' || secondary_agent || ' — ' || cross_concern_summary,
  'orchestrator_case_' || id,
  'T2',
  jsonb_build_object('primary_agent', primary_agent, 'secondary_agent', secondary_agent, 'approved', true)
FROM maestro_orchestration_outcomes  -- populated by Manta 16 on each merge
WHERE user_approved = true AND NOT EXISTS (
  SELECT 1 FROM rag_chunks WHERE source_file = 'orchestrator_case_' || maestro_orchestration_outcomes.id
);
```

Any agent (L2 or L3) can query `cross_concerns` before answering a request that touches another segment's
territory — e.g., agente-barragens retrieves the "CFRD + LT 500kV foundation coordination" pattern the first
time a UHE question comes in, without needing Manta 16 to be invoked fresh each time.

### 3.5 Guardrails

- `maestro_agent_messages.payload` is always structured JSON — never a raw string handoff. This keeps
  collaboration auditable and prevents prompt-injection-style drift between agents.
- N-way dispatch caps at 3 agents per query (beyond that, route to a human — Manta 16 merging 4+ perspectives
  degrades quality per the existing Reflexion/Tree-of-Thoughts maturity note in the architecture skill: swarm
  patterns are explicitly avoided in production).
- `cross_concerns` ingestion only fires on **approved** outcomes — a rejected merge never becomes a "pattern"
  other agents learn from.

---

## 4. Proactive Agents

### 4.1 Signal sources (all already exist by Phase 4.2 — this section wires them to action)

| Source | Signal | Existing table |
|--------|--------|----------------|
| Recommendation engine | Open, high-confidence recommendation | `maestro_recommendations` (4.2) |
| Regulatory webhooks | New ANEEL/ANTAQ/ANA/ANAC document | `maestro_regulatory_updates` (Phase 3.2) |
| Usage forecast | Predicted demand spike for a segment | `maestro_usage_forecast` (4.2) |
| Document auto-classification | Unclassified upload sitting >24h | Phase 2.3 flow |
| Knowledge gaps | Repeated gap on the same topic | `maestro_knowledge_gaps` (§1.2, new) |

### 4.2 Proactive suggestion table

```sql
CREATE TABLE IF NOT EXISTS maestro_proactive_suggestions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  generated_at timestamp DEFAULT now(),

  agent_slug text NOT NULL,           -- who should surface this
  user_id text,                       -- target user, if user-specific; NULL = segment-wide
  trigger_source text NOT NULL,       -- 'recommendation'|'regulatory'|'forecast'|'doc_classification'|'knowledge_gap'
  trigger_ref_id uuid,                -- FK into the source table (loose ref, source table varies)

  suggestion_text text NOT NULL,      -- what to tell the user
  suggested_action text,              -- 'review_document'|'update_estimate'|'re_run_analysis'|'none'
  urgency text DEFAULT 'normal',      -- low, normal, high

  status text DEFAULT 'pending',      -- pending, shown, accepted, dismissed, expired
  shown_at timestamp, responded_at timestamp,
  expires_at timestamp DEFAULT now() + interval '14 days'
);
CREATE INDEX IF NOT EXISTS idx_proactive_pending ON maestro_proactive_suggestions(status, urgency, generated_at DESC) WHERE status = 'pending';
```

### 4.3 Example flows

```
ANEEL publishes Resolução Normativa nova (Phase 3.2 webhook fires)
  → maestro_regulatory_updates row (existing)
  → sweep job checks: any open projects tagged 'energia' in SharePoint with active work?
  → maestro_proactive_suggestions: agent_slug='agente-energia', suggested_action='review_document',
    suggestion_text="Nova RN pode afetar o RAP do Lote 3 em andamento — revisar?"
  → surfaced in Cowork as a card, not auto-actioned
```

```
Usage forecast (4.2 §5.2) predicts +40% query volume for agente-saneamento next week
  (e.g., known AySA deadline approaching)
  → maestro_proactive_suggestions: agent_slug='maestro-router', urgency='high',
    suggestion_text="Volume de saneamento previsto +40% semana que vem — considerar
    pré-aquecer RAG cache / revisar tier mix"
```

### 4.4 Guardrails

- Every row here is a **suggestion**, surfaced through Cowork's existing notification pattern (same as Phase
  2.3's document classification proposal). Whether a suggestion can be auto-executed instead of just shown is
  governed entirely by §5 (Agent Autonomy) — proactivity and autonomy are separate concerns by design.
- Suggestions expire (`expires_at`, default 14 days) so the queue doesn't accumulate stale "you might want to…"
  items nobody will ever act on — same failure mode called out for the 4.2 recommendation queue.
- User-specific suggestions (`user_id` set) never fire more than once per `trigger_ref_id` per user — no
  repeated nagging about the same regulatory update.

---

## 5. Agent Autonomy

### 5.1 Why this exists now

Phase 4.2 built the recommendation engine and was explicit that it "only recommends, it never auto-applies a
change." Phase 4.3 is where a narrow, audited exception to that rule gets defined — not a blanket grant of
autonomy, but a three-tier ladder with hard guardrails at every tier above the default.

### 5.2 Autonomy tiers

| Tier | Behavior | Example actions | Approval |
|------|----------|------------------|----------|
| **Tier 0 (default)** | Recommend only | Any `maestro_recommendations` or `maestro_pk_update_proposals` row | Human clicks approve, always |
| **Tier 1** | Auto-apply, reversible, narrow allowlist, canary rollout | Routing-keyword confidence nudge beyond the existing per-event clamp (aggregate rebalancing); RAG cache TTL adjustment; non-content dashboard refresh cadence | Logged, auto-rollback on regression, MN reviews weekly digest — no per-event click needed |
| **Tier 2** | Auto-apply, post-hoc review required within SLA | A/B test promotion (Phase 2.1 `maestro_routing_ab_tests`: promote variant B to 100% once it beats variant A by a pre-registered margin over a pre-registered sample size) | MN must review within 5 business days or the action auto-reverts |

**Never autonomous, at any tier** — always Tier 0, regardless of confidence:

- Any edit to `CLAUDE.md`, a `SKILL.md`, or an agent/sub-agent `.md` file (content or system prompt).
- Anything touching a laudo, claim, orçamento, or client-facing document (these already require `aluci-guard`
  / `consist-guard` human review per those skills' own triggers).
- Anything with a financial figure that could be read as a commitment (pricing, RAP estimates, ROI numbers
  from 4.2 `maestro_roi_ledger`).
- Anything that deletes data (GDPR erasure per Phase 3.6 already has its own explicit, human-initiated flow).

### 5.3 Data schema

```sql
CREATE TABLE IF NOT EXISTS maestro_autonomy_config (
  action_type text PRIMARY KEY,        -- e.g. 'routing_keyword_rebalance', 'ab_test_promotion'
  tier int NOT NULL DEFAULT 0,         -- 0, 1, or 2 — the ladder above
  min_confidence float DEFAULT 0.90,   -- required confidence before auto-apply is even considered
  min_sample_size int DEFAULT 100,     -- minimum evidence volume
  canary_pct float DEFAULT 0.10,       -- fraction of traffic/scope the change first applies to
  rollback_trigger text,               -- e.g. 'health_score < 70 for 2 consecutive days'
  enabled boolean DEFAULT false,       -- kill switch — false disables auto-apply for this action_type
  updated_by text, updated_at timestamp DEFAULT now()
);

CREATE TABLE IF NOT EXISTS maestro_autonomous_actions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  action_type text NOT NULL REFERENCES maestro_autonomy_config(action_type),
  tier int NOT NULL,

  triggered_by text NOT NULL,          -- source recommendation/proposal id + table
  decision_evidence jsonb NOT NULL,    -- confidence, sample size, the numbers that justified auto-apply
  applied_at timestamp DEFAULT now(),
  applied_scope text,                  -- what changed, in human-readable form

  canary boolean DEFAULT true,
  outcome text DEFAULT 'monitoring',   -- monitoring, confirmed, rolled_back
  rolled_back_at timestamp, rollback_reason text,

  reviewed_by text, reviewed_at timestamp,  -- Tier 2 post-hoc review
  review_due_by timestamp
);
CREATE INDEX IF NOT EXISTS idx_autonomous_actions_monitoring ON maestro_autonomous_actions(outcome, applied_at DESC) WHERE outcome = 'monitoring';
CREATE INDEX IF NOT EXISTS idx_autonomous_actions_review_due ON maestro_autonomous_actions(review_due_by) WHERE reviewed_at IS NULL;
```

### 5.4 Guardrails (all mandatory, no exceptions)

1. **Allowlist, not denylist.** `maestro_autonomy_config` starts with zero rows at `tier > 0`. Every action
   type MN wants auto-applied is added explicitly — the system defaults to Tier 0 for anything unlisted.
2. **Canary before full rollout.** Tier 1/2 actions apply to `canary_pct` of scope first; the composite
   `health_score` (4.2 §2.3) is watched for `rollback_trigger` before widening.
3. **Kill switch.** `maestro_autonomy_config.enabled = false` on any row immediately disables auto-apply for
   that action type — checked at call time, not cached.
4. **Reversibility required.** No `action_type` is added to the allowlist unless there is a documented,
   tested rollback path. If an action can't be undone, it stays Tier 0 permanently.
5. **Full audit trail.** Every autonomous action writes to `maestro_autonomous_actions` before it takes
   effect, including the evidence that justified it — this feeds the same compliance dashboard as Phase 3.6.
6. **Blast radius ceiling.** No single autonomous action may touch more than one `agent_slug` (no cross-agent
   autonomous changes — those stay Tier 0 and go through Manta 16 + MN, since they're the highest-risk case).
7. **Monthly MN review** of the full `maestro_autonomous_actions` log is a standing calendar item, not just an
   SLA on individual Tier 2 rows.

---

## 6. Agent Reasoning Transparency

### 6.1 Decision trace — extends the existing `explanation` field

Phase 3.1's public API already returns a one-line `explanation` string. Phase 4.3 replaces that with a
structured trace object, generated as an explicit output (a designed summary the agent writes about its own
decision), **not** a dump of raw extended-thinking/scratchpad content — showing internal reasoning tokens as
if they were a verified audit trail is a known failure mode (unreviewed chain-of-thought can look authoritative
while containing dead ends, hedges, or reasoning the agent itself discarded) and is explicitly out of scope
here.

```sql
CREATE TABLE IF NOT EXISTS maestro_decision_trace (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  routing_trace_id uuid REFERENCES maestro_routing_trace(id) ON DELETE CASCADE,

  decision_summary text NOT NULL,      -- 1-3 sentence plain-language rationale
  inputs_considered jsonb NOT NULL,    -- {"keywords_matched": [...], "score_breakdown": {...}}
  alternatives_considered jsonb,       -- [{"agent": str, "score": float, "why_not_chosen": str}]
  sources_cited jsonb DEFAULT '[]',    -- [{"source_url": str, "tier": str, "collection": str, "retrieved_at": ts}]
  subagents_invoked text[] DEFAULT ARRAY[]::text[],   -- L1/L3 sub-agents from §2, if any
  collaboration_ref uuid REFERENCES maestro_agent_messages(conversation_id), -- if §3 collaboration occurred
  autonomy_action_ref uuid REFERENCES maestro_autonomous_actions(id),        -- if §5 autonomy applied

  model_tier text NOT NULL,            -- haiku|sonnet|opus actually used
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_decision_trace_routing ON maestro_decision_trace(routing_trace_id);
```

### 6.2 Citation requirement

Any factual claim in `sources_cited` must resolve to a real `rag_chunks` row (`source_url`, `tier`,
`collection_slug`) with a `retrieved_at` timestamp — no citation is written that the system can't point back
to. For any response that will become part of a laudo, claim, parecer, or orçamento, the decision trace
(and the underlying answer) **must** pass through `aluci-guard` before being treated as final — this phase
does not replace that skill, it feeds it a machine-readable trace to check against instead of unstructured
prose.

### 6.3 UI surface

Cowork gets a "Por que essa resposta?" expandable panel per response, rendering:

```
Resposta: agente-saneamento (confiança: 92%)

Por quê:
  Palavras-chave: "ETA", "200 mil hab" → forte match saneamento
  Alternativa considerada: agente-energia (78%) — descartada: sem menção a subestação/LT

Fontes citadas:
  [T1] NBR 12211 — dimensionamento ETA (rag:saneamento, recuperado 14:23:02)
  [T1] SNIS 2025 série histórica (rag:saneamento, recuperado 14:23:02)

Sub-agentes acionados: sizing-calculator (L3)
Modelo: Sonnet
```

### 6.4 Guardrails

- `decision_summary` is capped and template-driven (not open-ended free text from the model) to keep traces
  consistent enough to audit at scale — same discipline as the `explanation` field it replaces.
- `sources_cited` with zero entries is allowed (some answers are pure reasoning/calculation, e.g. the
  `sizing-calculator` sub-agent) but must be explicit about that (`"sources_cited": []`), never omitted.
- Decision traces are retained under the same retention policy as `maestro_audit_log` (Phase 3.6) — they are
  part of the compliance boundary, not a separate lighter-weight log.

---

## 7. Deliverables Checklist (4.3)

- [ ] Migration: `maestro_response_feedback`, `maestro_knowledge_gaps`, `maestro_pk_update_proposals`,
      `maestro_agent_exemplars` (§1)
- [ ] Haiku classifier for `signal_type` on incoming response feedback
- [ ] `maestro_subagent_registry` + first two L3 sub-agent pairs shipped (agente-saneamento,
      agente-energia — highest volume verticals) (§2)
- [ ] `maestro_agent_messages` + `cross_concerns` RAG collection + Manta 16 extended to N-way (cap 3) (§3)
- [ ] `maestro_proactive_suggestions` + sweep job wired to the five existing signal sources (§4)
- [ ] `maestro_autonomy_config` seeded with zero enabled rows; MN workshop to pick the first Tier 1
      candidate (§5) — **do not ship any Tier 1/2 action enabled by default**
- [ ] `maestro_autonomous_actions` + kill-switch check in the router hot path (§5)
- [ ] `maestro_decision_trace` + Cowork "Por que essa resposta?" panel (§6)
- [ ] `aluci-guard` integration point for decision traces feeding laudo/claim-adjacent output (§6.2)
- [ ] 14-day shadow period: log decision traces and proactive suggestions without surfacing them, to catch
      noisy/wrong output before it reaches users
- [ ] Gate humano: MN sign-off on §5 allowlist before any Tier 1 row is enabled

---

## 8. Risks & Mitigations

| Risk | Mitigation | Owner |
|------|-----------|-------|
| "Learning" scope creep into actual model fine-tuning or unreviewed PK edits | §0.1 hard constraint; every PK/skill change is a `maestro_pk_update_proposals` row, no code path bypasses it | Arquiteto IA (Manta 15) |
| Autonomy tier expands faster than trust is earned | Allowlist starts empty; each `action_type` added requires its own MN workshop + documented rollback | MN |
| Sub-agent sprawl (20 agents × N sub-agents becomes unmaintainable) | New sub-agents gated on ≥30 days production volume for the parent L2 agent; registry table makes the full graph auditable in one query | Manta 15 |
| Decision traces expose raw chain-of-thought inadvertently | `decision_summary` is template-driven, not a raw model dump; explicit review before this ships (§6.1) | Claude Code |
| Proactive suggestions become alert noise | 14-day expiry, one suggestion per `trigger_ref_id` per user, urgency tiering reused from 4.2 alerting | Product |
| Cross-agent collaboration reintroduces the "swarm" anti-pattern | Hard cap at 3-way dispatch; anything larger routes to a human, never auto-expands | Manta 15 |

---

## 9. What 4.3 does *not* do

- Does **not** fine-tune, retrain, or otherwise modify any Claude model's weights — see §0.1.
- Does **not** let any agent write to another agent's files, prompts, or skills directly — all collaboration
  and all learning-driven change passes through the router/orchestrator and a human-gated proposal queue.
- Does **not** grant blanket autonomy — the Tier 1/2 allowlist (§5.2) ships empty and stays empty until MN
  explicitly enables each action type.
- Does **not** treat raw model reasoning as an audit trail — decision traces are a designed, separate output
  (§6.1), never a scratchpad dump.
- Does **not** introduce a new datastore — everything above is additive tables in the existing Supabase
  Postgres project, consistent with every prior phase.

---

## 10. Success Metrics

| Metric | Target | Measured by |
|--------|--------|-------------|
| Content-quality feedback participation | ≥15% of responses rated | `maestro_response_feedback` / `maestro_routing_trace` |
| Knowledge-gap → ingestion cycle time | <14 days from flagged to `resolved` | `maestro_knowledge_gaps` |
| PK update proposal approval rate | Tracked, no target (quality gate, not a KPI to game) | `maestro_pk_update_proposals` |
| Sub-agent dispatch accuracy | ≥85% of L3 dispatches judged appropriate (sampled review) | `maestro_subagent_registry` usage logs |
| Cross-agent collaboration approval rate | ≥80% (raised from Phase 2.2's 80% target, same metric) | `maestro_agent_messages` + `maestro_user_feedback` |
| Proactive suggestion acceptance rate | ≥30% (`accepted` / (`accepted`+`dismissed`)) | `maestro_proactive_suggestions` |
| Tier 1 autonomous action rollback rate | <10% | `maestro_autonomous_actions` |
| Tier 2 review SLA compliance | 100% reviewed within 5 business days | `maestro_autonomous_actions.review_due_by` |
| Decision trace coverage | 100% of routed queries have a `maestro_decision_trace` row | `maestro_decision_trace` / `maestro_routing_trace` |

---

**Status**: 📋 Specification ready for migration + implementation
**Next Checkpoint**: MN review of §7 checklist and §5.2 allowlist before Dec 16 kickoff
