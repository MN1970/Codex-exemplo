# PHASE 4.4 — Platform & Ecosystem

**Workstream**: 4.4 of PHASE 4 (Data & Intelligence Platform) | **Status**: 📋 Design specification
**Depends on**: 4.1 Data Platform Foundation (warehouse, embeddings store), 4.2 Advanced Analytics
(`maestro_agent_performance_scorecard`, health scores), 4.3 Autonomous Optimization (recommendation
auto-apply, tier tuning), Phase 3.1 Public API (`/api/v1/maestro/*`), Phase 3.6 Audit & Compliance
(`maestro_audit_log`, data-minimization boundary)
**Feeds into**: Future Phase 5 — External Partner Ecosystem (subsidiaries/consultants publishing agents
against the standards this phase defines); contingent on MN approval of the governance model in §4
**Timeline (proposed)**: Apr 01, 2028 – Jul 15, 2028 (15 weeks)
**Owner**: Claude Code + DevOps + Segment Owners (S1–S10 leads act as first reviewers), Gate humano: MN
(final sign-off on governance model, certification criteria, and marketplace launch)

---

## 0. Purpose & Scope

Phases 1–3 built Maestro as a closed system: 20 agents maintained directly by Manta, routed by keyword +
LLM tie-breaker, exposed via a public API to trusted partners. Phase 4.1–4.3 turned that system's own
telemetry into intelligence and self-tuning. Phase 4.4 answers a different question: **how does anything
that isn't one of the original 20 agents — a new vertical built by a subsidiary, a skill shared by a
segment lead, a custom integration written by a consultant — get in, get trusted, and get maintained
without every submission becoming a manual MN review?**

Six deliverables, in dependency order:

| # | Deliverable | Primary question it answers |
|---|-------------|------------------------------|
| 1 | Agent Marketplace | Where do third-party agents live, and how do users find/install/rate them? |
| 2 | Skills & Plugins Marketplace | How are skills and MCP integrations packaged and shared safely? |
| 3 | Agent Certification Program | What does "safe to route production traffic to" actually mean, and who checks it? |
| 4 | Community Governance | Who can propose, review, and merge a change to the ecosystem — and how are disputes resolved? |
| 5 | Extensibility Framework | What is the supported way to build a custom agent/skill/integration from scratch? |
| 6 | Open Standards | What is frozen (protocol, API, data formats) so external builders don't need Manta's source? |

Design constraints carried over from Phase 1–4.3:
- All new tables live in the existing Supabase Postgres project (`maestro_*` naming convention, additive only).
- Distribution artifacts (agent manifests, skill packages) are stored as **Git repositories**, not blobs in
  Supabase — GitHub is already the system of record for `.claude/agents/*.md` (this repo) and CI (Phase 3.2
  pattern); the marketplace indexes Git, it does not replace it.
- Nothing here weakens the Phase 3.6 audit boundary: certification scans and marketplace listings never
  require submitting production prompt data, only the agent/skill source and a synthetic test suite.
- Every third-party artifact runs inside the same sandboxing model Cowork/Claude Code already enforce
  (tool permissions, no unreviewed shell/network access) — Phase 4.4 adds a certification layer on top,
  it does not invent a new execution sandbox.
- Every new table states its **source of truth**, its **refresh trigger**, and its **owner artifact**, so
  this doc can be implemented as one migration + one CI workflow + one Cowork/portal surface.

---

## 1. Agent Marketplace

### 1.1 Concept & scope

The marketplace is the discovery and lifecycle layer over the 20 core agents (Manta 00–16, S1–S10) **plus**
any third-party agent submitted by a subsidiary, consultant, or integrator under the Phase 3.1 public API
program. A "third-party agent" is a Git repository containing an agent manifest (§6.3) that the maestro
router can load exactly like `.claude/agents/agente-saneamento.md` — same shape, same routing contract,
different maintainer.

Marketplace states, in order:

```
submitted → scanning → under_review → certified (tier: bronze|silver|gold) → listed → [deprecated|revoked]
```

### 1.2 Data model

```sql
-- 4.4.1 — Marketplace agent listings (one row per agent, first-party or third-party)
CREATE TABLE IF NOT EXISTS maestro_marketplace_agents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_slug text NOT NULL UNIQUE,          -- e.g. 'agente-saneamento', 'acme-agente-ferrovia-leve'
  display_name text NOT NULL,
  publisher text NOT NULL,                  -- 'manta' for first-party, org/handle for third-party
  publisher_type text NOT NULL DEFAULT 'third_party', -- 'manta' | 'subsidiary' | 'consultant' | 'integrator'
  segment_hint text,                        -- S1-S10 mapping if it competes/complements an existing vertical
  repo_url text NOT NULL,                   -- source of truth (GitHub)
  manifest_path text NOT NULL DEFAULT 'AGENT.md',
  description text,
  category text[] DEFAULT ARRAY[]::text[],  -- free tags for search/filter

  certification_tier text DEFAULT 'uncertified', -- 'uncertified' | 'bronze' | 'silver' | 'gold'
  certification_expires_at date,            -- certifications are time-boxed, see §3.5
  status text NOT NULL DEFAULT 'submitted', -- see state machine above
  visibility text NOT NULL DEFAULT 'private',-- 'private' (submitter org only) | 'internal' (all Manta) | 'public'

  install_count int DEFAULT 0,
  avg_rating numeric(2,1),                  -- denormalized from maestro_marketplace_ratings
  rating_count int DEFAULT 0,

  submitted_by text NOT NULL,
  submitted_at timestamp DEFAULT now(),
  last_scanned_at timestamp,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_marketplace_agents_status ON maestro_marketplace_agents(status, visibility);
CREATE INDEX IF NOT EXISTS idx_marketplace_agents_segment ON maestro_marketplace_agents(segment_hint);

-- 4.4.2 — Semver-tracked versions per agent (immutable once published)
CREATE TABLE IF NOT EXISTS maestro_marketplace_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  marketplace_agent_id uuid NOT NULL REFERENCES maestro_marketplace_agents(id) ON DELETE CASCADE,
  version text NOT NULL,                    -- strict semver: MAJOR.MINOR.PATCH
  git_commit_sha text NOT NULL,
  changelog text,
  breaking_changes boolean DEFAULT false,
  certification_tier_at_publish text,       -- tier held at the moment this version was published
  scan_report_id uuid,                      -- FK to maestro_certification_scans (§3.3)
  is_yanked boolean DEFAULT false,           -- publisher/moderator can pull a bad version without deleting history
  yanked_reason text,
  published_at timestamp DEFAULT now(),
  UNIQUE(marketplace_agent_id, version)
);
CREATE INDEX IF NOT EXISTS idx_marketplace_versions_agent ON maestro_marketplace_versions(marketplace_agent_id, published_at DESC);

-- 4.4.3 — Ratings & reviews (one per user per agent, editable)
CREATE TABLE IF NOT EXISTS maestro_marketplace_ratings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  marketplace_agent_id uuid NOT NULL REFERENCES maestro_marketplace_agents(id) ON DELETE CASCADE,
  user_id text NOT NULL,
  stars int NOT NULL CHECK (stars BETWEEN 1 AND 5),
  review_text text,
  used_version text,                        -- which version the reviewer actually ran
  verified_install boolean DEFAULT false,   -- true if backed by a maestro_marketplace_installs row
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now(),
  UNIQUE(marketplace_agent_id, user_id)
);

-- 4.4.4 — Install/uninstall events (audit trail + install_count source)
CREATE TABLE IF NOT EXISTS maestro_marketplace_installs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  marketplace_agent_id uuid NOT NULL REFERENCES maestro_marketplace_agents(id),
  installed_version text NOT NULL,
  installed_by text NOT NULL,
  installed_scope text NOT NULL,            -- 'personal_cowork' | 'team' | 'org_wide'
  installed_at timestamp DEFAULT now(),
  uninstalled_at timestamp
);
CREATE INDEX IF NOT EXISTS idx_marketplace_installs_agent ON maestro_marketplace_installs(marketplace_agent_id, installed_at DESC);
```

### 1.3 Versioning policy

- Strict [semver](https://semver.org): `MAJOR` = breaking manifest/routing-contract change, `MINOR` =
  new capability/skill reference, `PATCH` = prompt/documentation fix with no behavior change.
- A published version is **immutable** — fixing a bug always means publishing a new version, never
  editing history. `is_yanked` hides a version from new installs without breaking existing pins.
- The router (Manta 00) always resolves `agent_slug@version-range` the same way a package manager does:
  default install pins `^MAJOR.MINOR.0`; auto-updates are opt-in per install scope.
- A `MAJOR` bump automatically drops the agent back to `certification_tier = 'uncertified'` until re-scanned
  (§3) — certification is a property of a specific version, not the agent slug in general.

### 1.4 Rating & discovery

- `avg_rating` / `rating_count` are recomputed by a trigger on insert/update of `maestro_marketplace_ratings`,
  not read live, to keep listing pages cheap.
- Search/discovery surface (in the existing Cowork/Portal shell, no new frontend framework) supports filter
  by: certification tier, segment, publisher type, rating, "compatible with my current agents" (keyword
  overlap check against `maestro_routing_keywords` to warn about collisions before install).
- **Collision warning**: before install, the marketplace UI runs the candidate agent's declared keywords
  (§6.3 manifest field `routing.keywords`) against the live `maestro_routing_keywords` table and flags any
  overlap with an existing installed agent (e.g., a third-party "ferrovia leve" agent overlapping S3) —
  installer must acknowledge the collision or request a disambiguation rule (feeds Phase 3.5 tie-breaker).

---

## 2. Skills & Plugins Marketplace

### 2.1 Concept & scope

Distinct from agents: a **skill** is a packaged capability (`SKILL.md` + supporting scripts/templates) an
agent or user invokes directly — the same shape as `.claude/skills/*` used throughout this repo's
ecosystem (30+ skills per `manta-maestro-guide`). A **plugin** bundles one or more skills, agent
definitions, and MCP server configs for one-shot install. This phase makes both shareable beyond the
Manta org boundary, with the same certification gate as agents (lighter-weight, since skills carry less
routing risk but more execution risk — they run scripts).

### 2.2 Data model

```sql
-- 4.4.5 — Skill/plugin listings
CREATE TABLE IF NOT EXISTS maestro_marketplace_skills (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_slug text NOT NULL UNIQUE,
  package_type text NOT NULL DEFAULT 'skill', -- 'skill' | 'plugin' (bundle of skills+agents+MCP config)
  display_name text NOT NULL,
  publisher text NOT NULL,
  publisher_type text NOT NULL DEFAULT 'third_party',
  repo_url text NOT NULL,
  manifest_path text NOT NULL DEFAULT 'SKILL.md',
  integration_pattern text,                 -- 'standalone' | 'agent_dependency' | 'mcp_wrapper' | 'hook'
  requires_mcp_servers text[] DEFAULT ARRAY[]::text[], -- declared MCP dependencies, e.g. {'Supabase','SharePoint_Manta'}
  requires_permissions jsonb DEFAULT '{}',  -- declared tool/permission footprint, checked at scan time (§3.3)
  description text,
  category text[] DEFAULT ARRAY[]::text[],

  certification_tier text DEFAULT 'uncertified',
  status text NOT NULL DEFAULT 'submitted',
  visibility text NOT NULL DEFAULT 'private',

  install_count int DEFAULT 0,
  avg_rating numeric(2,1),
  rating_count int DEFAULT 0,

  submitted_by text NOT NULL,
  submitted_at timestamp DEFAULT now(),
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_marketplace_skills_status ON maestro_marketplace_skills(status, visibility);

-- Versions and ratings reuse the same shape as §1.2 (separate tables to keep FKs clean)
CREATE TABLE IF NOT EXISTS maestro_marketplace_skill_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  marketplace_skill_id uuid NOT NULL REFERENCES maestro_marketplace_skills(id) ON DELETE CASCADE,
  version text NOT NULL,
  git_commit_sha text NOT NULL,
  changelog text,
  breaking_changes boolean DEFAULT false,
  scan_report_id uuid,
  is_yanked boolean DEFAULT false,
  published_at timestamp DEFAULT now(),
  UNIQUE(marketplace_skill_id, version)
);

CREATE TABLE IF NOT EXISTS maestro_marketplace_skill_ratings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  marketplace_skill_id uuid NOT NULL REFERENCES maestro_marketplace_skills(id) ON DELETE CASCADE,
  user_id text NOT NULL,
  stars int NOT NULL CHECK (stars BETWEEN 1 AND 5),
  review_text text,
  created_at timestamp DEFAULT now(),
  UNIQUE(marketplace_skill_id, user_id)
);
```

### 2.3 Integration patterns (supported, documented, scanned-for)

| Pattern | Shape | Example in this repo | Certification implication |
|---------|-------|----------------------|---------------------------|
| **Standalone skill** | Pure prompt/template logic, no external calls | `docx`, `xlsx`, `pptx` | Lightest scan: manifest lint + prompt-injection check only |
| **Agent dependency** | Skill assumes a specific agent's output shape as input | `cad-quantifier` (consumes `cad-reader` JSON) | Scan verifies declared upstream skill exists and version-compatible |
| **MCP wrapper** | Skill is a thin prompt layer over one or more MCP servers | `autodesk-toolkit` (wraps Autodesk Product Help MCP) | Scan checks `requires_mcp_servers` matches actual tool calls in scripts; no undeclared MCP usage allowed |
| **Hook-based** | Skill installs a Claude Code hook (PreToolUse/SessionStart) | `session-start-hook` pattern | Highest scrutiny — hooks run automatically without explicit invocation; requires Silver tier minimum (§3.1) |

Publishing requires declaring the pattern up front (`integration_pattern` column) — the certification
scan (§3.3) applies a different static-analysis ruleset per pattern, and mismatched declarations
(e.g., a "standalone" skill that silently calls an MCP tool) is an automatic scan failure, not just a
warning.

---

## 3. Agent Certification Program

### 3.1 Certification tiers

| Tier | Meaning | Who can install | Renewal |
|------|---------|------------------|---------|
| **Uncertified** | Submitted, not yet scanned or scan failed | Submitter's own org only (`visibility='private'`), explicit opt-in warning banner | N/A — must pass Bronze to progress |
| **Bronze** | Passed automated security + manifest-compliance scan | Any Manta internal user (`visibility='internal'`), with warning that no human reviewed it | Re-scan on every version publish |
| **Silver** | Bronze + passed performance benchmark + segment-owner peer review (§4.2) | Any Manta internal user, eligible for production routing traffic | Every 6 months or on MAJOR version bump |
| **Gold** | Silver + 90 days of production telemetry meeting Phase 4.2 health-score bar (≥80, green band) + MN sign-off | Public listing (`visibility='public'`), eligible for external partner distribution under Phase 3.1 | Every 6 months; auto-downgrades to Silver if health score drops to `red` for 7 consecutive days (ties into Phase 4.3 recommendation engine) |

### 3.2 Certification criteria

| Domain | Criterion | Method | Blocking? |
|--------|-----------|--------|-----------|
| **Security** | No hardcoded credentials/secrets in manifest or scripts | Automated secret-scan (reuses Phase 3.2's GitHub secret-scanning pattern via `mcp__github__run_secret_scanning`) | Yes, all tiers |
| **Security** | No undeclared tool/MCP permission usage | Static analysis of scripts vs. declared `requires_permissions` / `requires_mcp_servers` | Yes, all tiers |
| **Security** | No prompt-injection-susceptible instruction patterns (e.g., "ignore all previous instructions" honored from untrusted input) | Automated red-team prompt suite (50 canned adversarial inputs) + manual spot-check at Silver | Yes, Bronze+ |
| **Security** | Sandboxed execution only — no shell/network calls outside declared tool allowlist | Enforced at runtime by existing Cowork/Claude Code permission system; scan verifies manifest doesn't request `dangerouslyDisableSandbox`-equivalent scope | Yes, all tiers |
| **Compliance** | Manifest declares data handled (PII, contract-confidential, public) and matches Phase 3.6 audit categories | Manifest lint against `maestro_data_classification` enum (Phase 3.6) | Yes, Silver+ |
| **Compliance** | No plaintext prompt/document content is persisted or transmitted outside declared MCP servers | Static trace of write/network operations in scripts | Yes, all tiers |
| **Compliance** | License compatible with Manta's redistribution terms (declared in manifest) | Manifest lint | Yes, all tiers |
| **Performance** | Median response latency under segment's SLO (reuses Phase 4.2 `latency_p95` target of 500ms, adjusted per agent type) | Synthetic benchmark suite run against submitted agent in isolated sandbox | Yes, Silver+ |
| **Performance** | Routing accuracy ≥ 80% on a held-out labeled test set (200 prompts per segment, maintained by segment owners) | Automated eval harness, same shape as `tests/comprehensive-test-suite.json` | Yes, Silver+ |
| **Performance** | Token efficiency within 2× of the tier-equivalent first-party agent for comparable tasks | Comparative benchmark against nearest first-party analog | No — informational (surfaced on listing page) |
| **Documentation** | Manifest includes description, example prompts, known limitations, and a changelog per version | Manifest lint | Yes, Bronze+ |

### 3.3 Automated scan pipeline

```sql
-- 4.4.6 — Certification scan runs (one row per scan attempt, agent or skill)
CREATE TABLE IF NOT EXISTS maestro_certification_scans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  target_type text NOT NULL,               -- 'agent' | 'skill'
  target_id uuid NOT NULL,                 -- FK to maestro_marketplace_agents.id or maestro_marketplace_skills.id
  version text NOT NULL,
  git_commit_sha text NOT NULL,

  requested_tier text NOT NULL,            -- tier the submitter is attempting to reach
  security_pass boolean,
  compliance_pass boolean,
  performance_pass boolean,
  documentation_pass boolean,

  security_findings jsonb DEFAULT '[]',
  compliance_findings jsonb DEFAULT '[]',
  performance_metrics jsonb DEFAULT '{}',  -- {"latency_p95_ms":420,"accuracy_pct":86.5,"token_ratio":1.4}

  overall_result text NOT NULL DEFAULT 'running', -- 'running' | 'pass' | 'fail'
  started_at timestamp DEFAULT now(),
  completed_at timestamp,

  CHECK (target_type IN ('agent','skill'))
);
CREATE INDEX IF NOT EXISTS idx_cert_scans_target ON maestro_certification_scans(target_type, target_id, started_at DESC);

-- 4.4.7 — Human (peer/segment-owner) review, required for Silver+
CREATE TABLE IF NOT EXISTS maestro_certification_reviews (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id uuid NOT NULL REFERENCES maestro_certification_scans(id),
  reviewer text NOT NULL,                  -- segment owner or MN
  reviewer_role text NOT NULL,             -- 'segment_owner' | 'security' | 'mn'
  decision text NOT NULL,                  -- 'approve' | 'request_changes' | 'reject'
  comments text,
  reviewed_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cert_reviews_scan ON maestro_certification_reviews(scan_id);
```

**Pipeline** (mirrors the existing GitHub Actions pattern already used for routing tests in this repo):

```
1. Submission webhook (GitHub PR opened against manta-maestro-marketplace index repo)
2. CI job: manifest lint → secret scan → permission-declaration cross-check
3. If target_type='agent': eval harness runs held-out test set, records accuracy + latency
   If target_type='skill': red-team prompt suite + declared-MCP-usage cross-check
4. Write result to maestro_certification_scans; overall_result computed from all *_pass columns
5. Bronze: auto-granted if overall_result='pass' and requested_tier='bronze' — no human step
6. Silver/Gold: scan pass is necessary but not sufficient — routes to maestro_certification_reviews;
   segment owner (Silver) or MN (Gold) reviews before certification_tier updates
7. On any result, submitter notified via existing Slack/GitHub-issue pattern (Phase 3.2)
```

### 3.4 Human review gate

- **Silver**: the relevant segment owner (S1–S10 lead, or horizontal-agent owner for Eixo 1 agents) reviews
  scan findings + runs a manual 30-minute smoke test against 10 representative prompts from their domain.
  Decision recorded in `maestro_certification_reviews`.
- **Gold**: requires (a) 90 consecutive days at Silver with `health_band='green'` in
  `maestro_agent_performance_scorecard` (Phase 4.2), and (b) MN sign-off — the same gate already used for
  every phase's executive rollout in this repository's convention.
- **Revocation**: any tier can be revoked immediately (no notice period) if a security finding surfaces
  post-certification (e.g., a Phase 4.3 anomaly signal flags data exfiltration behavior). Revocation is a
  status change on `maestro_marketplace_agents.status = 'revoked'`, cascades to hide all listed versions,
  and force-notifies every org with an active install row in `maestro_marketplace_installs`.

### 3.5 Certification badge & display

Marketplace listing pages show: tier badge (bronze/silver/gold icon), scan date, expiry date, and a link to
the redacted scan report (findings only, never the raw prompt/test corpus). Expired certifications
(§3.1 renewal column) auto-downgrade one tier and re-open the pipeline — they never silently keep serving
production traffic on a stale certification.

---

## 4. Community Governance

### 4.1 Contribution model

Governance mirrors what already works for the internal 20-agent catalog (this repo's own PR-based
workflow) rather than inventing a new process:

| Contribution type | Process | Approval needed |
|--------------------|---------|------------------|
| **New third-party agent/skill submission** | PR against `manta-maestro-marketplace` index repo with manifest + repo link | Automated scan (§3.3); Bronze auto-grants, Silver+ needs reviewer |
| **Change to an existing certified agent/skill** | New version published in the agent's own repo, re-indexed via webhook | Re-scan; tier is retained only if scan still passes at that tier |
| **Change to certification criteria (§3.2)** | RFC (see §4.2) | MN + Security lead |
| **Change to open standards (§6)** | RFC, minimum 2-week comment period | MN + at least 2 segment owners |
| **Governance model change (this section)** | RFC + full segment-owner vote | MN (tie-break) |

### 4.2 RFC / peer review workflow

1. **Draft**: proposer opens a GitHub issue tagged `rfc` in the marketplace index repo using the RFC
   template (problem statement, proposed change, alternatives considered, backward-compatibility impact).
2. **Comment period**: minimum 5 business days for tier/criteria changes, 10 for protocol/standards changes
   (§6). Any segment owner or MN can extend once.
3. **Review**: at least 2 of the following must approve — the relevant segment owner(s), the Security lead
   (for anything touching §3.2 security criteria), MN (required for standards/governance changes, optional
   otherwise).
4. **Decision recorded**: approved/rejected/deferred, with rationale, appended to the RFC issue and mirrored
   to `maestro_governance_decisions` (below) so the decision history is queryable, not just buried in
   GitHub issue threads.
5. **Implementation**: only after recorded approval — no RFC merges its own implementation PR without a
   separate approving review on the code, same as this repo's existing PR discipline.

```sql
-- 4.4.8 — Governance decision log (append-only)
CREATE TABLE IF NOT EXISTS maestro_governance_decisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  rfc_ref text NOT NULL,                   -- GitHub issue URL
  decision_type text NOT NULL,             -- 'certification_criteria' | 'open_standard' | 'governance' | 'other'
  title text NOT NULL,
  summary text NOT NULL,
  decision text NOT NULL,                  -- 'approved' | 'rejected' | 'deferred'
  approvers text[] NOT NULL,
  effective_date date,
  supersedes_decision_id uuid REFERENCES maestro_governance_decisions(id),
  created_at timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_governance_decisions_type ON maestro_governance_decisions(decision_type, created_at DESC);
```

### 4.3 Roles

| Role | Who | Responsibilities |
|------|-----|-------------------|
| **Segment owner** | S1–S10 leads (existing, per CLAUDE.md routing table) + horizontal-agent owners | Silver-tier reviews for their domain; maintain the held-out test set (§3.2) for their segment |
| **Security lead** | Designated by MN | Approves security-criteria RFCs; spot-audits Gold-tier agents quarterly |
| **Maintainers council** | Segment owners + Security lead, convened monthly | Triages open RFCs, resolves disputes escalated from peer review deadlock |
| **MN (executive gate)** | Named individual | Final sign-off on Gold certifications, standards changes, governance changes — same gate used at every phase's rollout in this repository |
| **Contributor** | Anyone (internal Manta staff, subsidiary, consultant, integrator) submitting an agent/skill | Follows contribution model in §4.1; no special access required to submit, only to approve |

### 4.4 Code of conduct & dispute resolution

- All contributors (internal and external) agree to a published code of conduct (technical-disagreement
  norms, no disparagement of competing submissions, disclosure of conflicts of interest e.g. a consultant
  submitting an agent that competes with a Manta first-party one).
- **Disputes** (e.g., two segment owners disagree on a Silver review, or a revoked publisher contests the
  revocation): escalate to the Maintainers Council; unresolved after one council cycle escalates to MN.
- All dispute outcomes are logged in `maestro_governance_decisions` with `decision_type='other'` for
  auditability — this is the same append-only pattern already used for the audit log in Phase 3.6, applied
  to governance instead of data access.

---

## 5. Extensibility Framework

### 5.1 Custom agent SDK

A scaffolding CLI (`maestro-agent-init`, a thin wrapper script, not a new runtime) generates:
- `AGENT.md` manifest skeleton matching the §6.3 schema (routing keywords, tier default, lifecycle-phase
  support declaration per Eixo 3's 8 phases, data-classification declaration for Phase 3.6 compliance).
- A stub held-out test set (10 example prompts) the segment owner must expand to 200 before Silver review.
- A GitHub Actions workflow file pre-wired to call the certification scan webhook (§3.3) on every push.
- README template documenting the agent's scope, explicitly modeled on the existing `.claude/agents/*.md`
  files in this repository so first-party and third-party agents are indistinguishable in shape.

### 5.2 Custom skill SDK

Same pattern (`maestro-skill-init`), generating a `SKILL.md` skeleton plus:
- A manifest section declaring `integration_pattern` (§2.3) up front — the scaffold refuses to generate
  a hook-based skeleton without an explicit flag, since that pattern requires Silver-tier minimum.
- A permissions declaration file (`PERMISSIONS.md`) listing every tool/MCP server the skill's scripts touch,
  which the scan (§3.3) diffs against actual usage.
- Example integration test showing the skill invoked standalone and (if applicable) as an agent dependency.

### 5.3 Custom integration (MCP) template

For contributors building a new MCP server rather than a skill/agent: this phase does not re-specify MCP
itself (that is Anthropic's open protocol, referenced not reinvented — see §6.1) but adds a **Manta-specific
registration template** so a new MCP server can be:
- Declared in a submission manifest (`mcp_server.yaml`: name, transport, required auth, tool list, data
  classification of what it can read/write).
- Scanned for the same permission-declaration cross-check as skills (§3.2) before any first-party agent is
  allowed to declare it in `requires_mcp_servers`.
- Listed in the marketplace under a fourth listing type (`maestro_marketplace_mcp_servers`, same shape as
  §1.2/§2.2, omitted above for brevity — schema is a structural copy with `transport_type` and
  `auth_method` columns replacing agent-specific fields).

### 5.4 Sandboxing & permission model

Extensibility never means "arbitrary code with arbitrary access." Every custom agent/skill/integration:
- Runs under the same Cowork/Claude Code tool-permission system already governing first-party agents —
  the marketplace layer adds provenance and certification, not a new execution boundary.
- Declares its full permission footprint in the manifest before submission; the scan pipeline (§3.3) is the
  enforcement point that catches undeclared-usage drift, not a runtime sandbox escape (there isn't one to
  escape — permissions are enforced by the harness itself, independent of this phase).
- Cannot request `dangerouslyDisableSandbox`-equivalent scope, elevated GitHub-push access, or raw database
  credentials as part of a marketplace submission; those remain first-party-only capabilities, full stop.

---

## 6. Open Standards

### 6.1 Manta Agent Protocol (MAP) — versioned spec

Freezing the contract between "anything the router can dispatch to" and "the router itself" is what lets
third parties build without reading Maestro's source. **MAP v1.0** (this phase) formalizes what the 20
first-party agents already do implicitly:

| Contract element | Spec |
|-------------------|------|
| **Manifest format** | `AGENT.md` — YAML frontmatter (machine-readable) + Markdown body (human-readable), see §6.3 |
| **Routing input** | `{prompt: string, context: {segment_hint?, session_id?, conversation_history?, metadata?}}` — identical shape to the existing Phase 3.1 `/api/v1/maestro/route` request body |
| **Routing output** | `{primary_agent, primary_score, alternatives[], orchestrated, explanation, confidence, processing_time_ms, version, timestamp}` — identical shape to the existing Phase 3.1 response, now a **frozen** contract any agent must be dispatchable through |
| **Lifecycle phase declaration** | Agent manifest must declare which of the 8 Eixo 3 phases it supports (a subset is valid; router treats unsupported-phase requests as a routing miss, not an error) |
| **Versioning** | Semver (§1.3); MAP itself is versioned independently (`map_version` field in manifest) so the router can support multiple MAP versions during a deprecation window |

### 6.2 API contracts

- The public API surface is the one already shipped in Phase 3.1 (`/api/v1/maestro/route`,
  `/api/v1/maestro/ask`) — Phase 4.4 does not add new endpoints, it publishes the **OpenAPI 3.1 spec** for
  that surface as a standalone, versioned artifact (`maestro-api-spec` repo) so external integrators can
  generate clients without scraping documentation.
- Every marketplace-listed agent that reaches **Gold** tier is required to be reachable through this exact
  contract with no agent-specific request/response deviation — that uniformity is what "Gold = eligible for
  external distribution" actually buys.
- Breaking changes to the OpenAPI spec follow the same MAJOR-version discipline as §1.3, with a minimum
  90-day dual-support window (old + new contract both served) before the old one is retired.

### 6.3 Data formats (JSON Schema, canonical)

```jsonc
// AGENT.md frontmatter schema (informal JSON Schema notation)
{
  "agent_slug": "string, required, kebab-case, unique",
  "display_name": "string, required",
  "map_version": "string, required, e.g. '1.0'",
  "publisher": "string, required",
  "routing": {
    "keywords": ["string, ..."],
    "segment_hint": "string, optional, one of S1-S10 or 'horizontal'",
    "tier_default": "string, one of haiku|sonnet|opus|haiku->sonnet"
  },
  "lifecycle_phases_supported": ["int, 1-8, at least one required"],
  "data_classification": "string, one of public|internal|confidential|pii — per Phase 3.6 enum",
  "requires_mcp_servers": ["string, ...", "optional"],
  "requires_permissions": { "tools": ["string, ..."], "note": "cross-checked at scan time, §3.2" },
  "certification": { "tier": "string", "expires_at": "date, optional" },
  "version": "string, required, semver"
}
```

```jsonc
// SKILL.md frontmatter schema
{
  "skill_slug": "string, required",
  "package_type": "string, one of skill|plugin",
  "integration_pattern": "string, one of standalone|agent_dependency|mcp_wrapper|hook",
  "requires_mcp_servers": ["string, ...", "optional"],
  "requires_permissions": { "tools": ["string, ..."] },
  "depends_on_skills": ["string, ...", "optional, for agent_dependency pattern"],
  "version": "string, required, semver"
}
```

Both schemas are published as standalone `.schema.json` files in the `manta-maestro-marketplace` repo and
validated in CI (§3.3 step 2) — this is the same manifest-lint step already run against
`.claude/agents/*.md` in this repository's existing test suite, generalized to third-party submissions.

### 6.4 Backward compatibility policy

- MAP, the OpenAPI spec, and both JSON Schemas each carry independent version numbers and independent
  deprecation windows (minimum 90 days, matching §6.2), so a MAP bump doesn't force an API bump.
- Deprecation is announced via the same RFC process as §4.2 (`decision_type='open_standard'`), logged in
  `maestro_governance_decisions`, and mirrored to every certified publisher's registered contact via the
  existing Slack/email notification pattern (Phase 3.2/4.2).
- No standard is ever broken silently — a version bump without a corresponding RFC and dual-support window
  is itself a governance violation escalated to the Maintainers Council (§4.3).

---

## 7. Deliverables Checklist (4.4)

- [ ] Migration: tables in §1.2, §2.2, §3.3, §4.2 (one file, additive only)
- [ ] `manta-maestro-marketplace` index repo created (manifests, scan CI, RFC template, schemas)
- [ ] Scaffolding CLIs: `maestro-agent-init`, `maestro-skill-init` (§5.1, §5.2)
- [ ] Certification scan pipeline wired to GitHub Actions (manifest lint, secret scan, permission
      cross-check, eval harness, red-team prompt suite)
- [ ] Held-out test sets (200 prompts) authored per segment by segment owners — blocking for Silver tier
- [ ] Marketplace discovery/listing surface added to existing Cowork/Portal shell (no new frontend stack)
- [ ] Collision-warning check wired against live `maestro_routing_keywords` (§1.4)
- [ ] OpenAPI 3.1 spec published as standalone versioned artifact (§6.2)
- [ ] Both JSON Schemas (§6.3) published and enforced in CI
- [ ] Code of conduct + RFC template + Maintainers Council roster published
- [ ] Security lead designated; quarterly Gold-tier audit cadence scheduled
- [ ] Pilot: 2-3 subsidiary/consultant agents run through the full pipeline end-to-end before public listing opens
- [ ] Gate humano: MN review of governance model (§4), certification criteria (§3.2), and open standards
      (§6) before marketplace visibility is set to `public` for any listing

---

## 8. Risks & Mitigations

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Third-party agent silently collides with a first-party routing keyword, degrading accuracy for an existing segment | Collision-warning check (§1.4) blocks install without explicit acknowledgment; feeds Phase 3.5 disambiguation backlog | Routing team |
| Certification scan gives false confidence (passes automated checks but still misbehaves in production) | Gold tier requires 90 days of live health-score evidence (§3.1), not just a point-in-time scan; Phase 4.3 anomaly signals can trigger immediate revocation | Security lead |
| Governance process becomes a bottleneck, discouraging contribution | Bronze tier is fully automated with zero human review; only Silver+ requires a person, and RFC comment periods are capped (§4.2) | Maintainers Council |
| A revoked publisher disputes the revocation publicly, reputational risk | Revocation criteria (§3.4) and dispute path (§4.4) are published in advance, not improvised after the fact | MN |
| Marketplace scan pipeline itself becomes an attack surface (malicious submission targets the CI runner) | Scans run in the same isolated sandbox pattern as any untrusted-code execution already used in this org's CI; no scan step gets credentials beyond what a `read`-only add_repo grants | DevOps |
| Segment owners lack bandwidth to maintain 200-prompt held-out test sets | Seed sets generated from existing `maestro_routing_trace` approved cases (Phase 1.4/2.1 data), owners only curate/expand, not build from zero | Segment owners |
| Open standards (§6) fork in practice because enforcement is CI-only, not runtime | Manifest schema validation is a hard CI gate (submission cannot merge without passing), and MAP-version mismatches are treated as routing misses, not silently ignored | Claude Code |

---

## 9. What 4.4 does *not* do

- Does **not** create a new execution sandbox or permission system — every third-party artifact runs under
  the same Cowork/Claude Code tool-permission model already governing first-party agents; this phase adds
  provenance, scanning, and certification on top, not a new runtime boundary.
- Does **not** auto-certify Silver or Gold tier — Bronze is the only fully automated tier; every Silver+
  certification requires a named human reviewer's recorded decision (§3.4).
- Does **not** replace GitHub as the source of truth for agent/skill code — Supabase tables in this phase
  are an **index and audit trail** over Git repositories, never a copy of the code itself.
- Does **not** open public marketplace visibility by default — every listing starts `visibility='private'`
  and requires an explicit, logged decision to widen scope, with `public` gated on Gold certification and
  MN sign-off (§3.1, §7).
- Does **not** change the Phase 3.6 data-minimization boundary — certification scans and held-out test sets
  use synthetic/redacted prompts, never raw production conversation content.

---

**Status**: 📋 Specification ready for migration + implementation
**Next Checkpoint**: MN review of §4 governance model and §3.2 certification criteria before `Apr 01` kickoff
