# Agent Auto-Registration Service

Implements Fase 3.1 ("Agent self-registration") of
[`docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`](../../docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md):
adding a new Manta agent should require **only** a new
`.claude/agents/meu-agente.md` file — everything else (registry entry,
self-test, gradual rollout, promotion) happens automatically.

**Status**: candidate implementation, not yet wired to production
infra. Same gate-human policy as the rest of this repo: review, apply
the Supabase migration, wire the webhook secret, get MN approval
before pointing a real GitHub webhook at it.

## Pipeline

```
.claude/agents/agente-x.md  (git push to main)
        │
        ▼
webhook-handler.js            verifies GitHub HMAC signature, diffs
                               commits for .claude/agents/*.md changes
        │
        ▼
auto-registration-service.js  parses frontmatter + body → upserts
                               `agents` row (lifecycle=alpha)
        │
        ▼
        runs 5 sample queries (curated prompts/starters.md if present,
        else synthesized from expertise keywords)
        │
        ├─ any query fails or exceeds 30s → promotion_status =
        │  'self_test_failed', agent stays at 0% traffic, NOT exposed
        │  to the Maestro in production
        │
        ▼ all 5 pass
ab-test-service.js            lifecycle=beta, traffic_percentage=5,
                               ab_test_started_at=now,
                               ab_test_ends_at=+7d
        │
        ▼  (runPromotionSweep(), run on a schedule — cron/Routine)
        after the window closes: checks agent_health +
        agent_self_test_results against promotion thresholds
        │
        ├─ pass → lifecycle=prod, traffic_percentage=100 (promoted)
        └─ fail → traffic_percentage=0, promotion_status=rolled_back
```

Every transition is logged to `agent_promotion_events` for audit.

## Files

| File | Responsibility |
|------|-----------------|
| `auto-registration-service.js` | Parse → upsert `agents` → run self-test → hand off to A/B test. Also a CLI: `node auto-registration-service.js .claude/agents/agente-x.md`. |
| `webhook-handler.js` | Express receiver for GitHub `push` events; verifies signature, filters `.claude/agents/*.md` changes, calls the registration service async, deregisters agents whose file was deleted. |
| `ab-test-service.js` | Starts the 5%/7-day rollout, deterministic traffic bucketing (`getTrafficAssignment`) for the Maestro to consult per-request, and `runPromotionSweep()` to promote/roll back once the window closes. |
| `lib/parse-agent-md.js` | Frontmatter + body parser. Understands today's minimal frontmatter (`name`, `description`, `tools`, `model`) and derives `expertise`/`rag_collections`/`handoffs_to` from the free-text body when a richer frontmatter isn't provided, so existing agents (e.g. `agente-saneamento.md`) register with zero edits. |
| `lib/sample-queries.js` | Produces the 5 self-test queries — prefers `sharepoint/01-agentes-fundamentais/<agent-id>/prompts/starters.md` when it exists, else synthesizes from expertise keywords. |
| `lib/supabase-client.js` | Shared Supabase client (service-role key, server-side only). |
| `lib/events.js` | Shared `agent_promotion_events` logger (kept out of the two service files to avoid a circular `require`). |

## Database

New migration:
[`supabase/migrations/2026_08_02_agent_auto_registration.sql`](../../supabase/migrations/2026_08_02_agent_auto_registration.sql)

Creates (if not already present from the v5.0 design doc):
- `agents` — master catalog (schema per §4.1 of the design doc) plus
  the rollout columns this service needs: `source_path`,
  `source_commit`, `registered_at`, `traffic_percentage`,
  `ab_test_started_at`, `ab_test_ends_at`, `promoted_at`,
  `promotion_status`.
- `agent_health` — heartbeat/telemetry (already specced in the design
  doc; the promotion sweep reads `success_count`/`error_count`/
  `avg_latency_ms` from here as the primary signal).
- `agent_self_test_results` — one row per sample query per run;
  fallback signal for promotion if `agent_health` has no data yet.
- `agent_promotion_events` — audit log of every registration/self-test/
  A-B/promotion transition.

Apply via `supabase db push` or `psql "$SUPABASE_DB_URL" -f supabase/migrations/2026_08_02_agent_auto_registration.sql` — same gate-human policy as `2026_07_05_v4_2_agents_s6_s10.sql`.

## Wiring it up

1. `cp .env.example .env` and fill in `SUPABASE_URL`,
   `SUPABASE_SERVICE_ROLE_KEY`, `GITHUB_WEBHOOK_SECRET`,
   `AGENTS_REPO_ROOT` (a local checkout of this repo, kept in sync with
   `main` by whatever CI/deploy already exists).
2. `npm install` (adds `@supabase/supabase-js`, `express`).
3. Run the webhook receiver: `npm run webhook` (listens on `$PORT`,
   default `8787`, at `POST /webhooks/github/agent-registry`).
4. On GitHub: repo → Settings → Webhooks → Add webhook →
   `https://<host>/webhooks/github/agent-registry`, content type
   `application/json`, secret = `GITHUB_WEBHOOK_SECRET`, events = "Just
   the push event".
5. Schedule the promotion sweep (`npm run sweep`, i.e.
   `node ab-test-service.js sweep`) — hourly is enough since the A/B
   window is measured in days. A Claude Code Remote Routine
   (`create_trigger` with a cron expression) or a Supabase Edge
   Function + `pg_cron` both work; nothing in this repo assumes one
   over the other.
6. **`agentInvoker` must be supplied for self-test to mean anything.**
   The default in `auto-registration-service.js` throws on purpose —
   without a real dispatcher (spin up the actual agent and send it the
   sample query), latency/correctness numbers would be fabricated.
   Inject it via `registerAgentFromFile(path, { agentInvoker })` /
   `createWebhookApp({ agentInvoker })` once the real dispatch call is
   available (e.g. a Claude Code Remote session per agent, or however
   the Maestro currently invokes verticals).

## Manual test (no webhook)

```bash
cd infra/agent-registry
npm install
node auto-registration-service.js ../../.claude/agents/agente-saneamento.md
```

This registers (or re-registers) `agente-saneamento`, derives its 5
self-test queries from
`sharepoint/01-agentes-fundamentais/agente-saneamento/prompts/starters.md`,
and — once a real `agentInvoker` is wired in — starts its A/B test on
a pass.

## What this does NOT do (by design)

- Does not decide routing at request time — that's the Maestro's job.
  This service only maintains `agents.traffic_percentage` /
  `lifecycle`; `getTrafficAssignment(agentId, trafficPercentage,
  requestKey)` is exported for the Maestro to call per-request.
- Does not invoke agents for real — `agentInvoker` is intentionally an
  injected dependency, not a built-in Claude API call, since how an
  agent is actually dispatched is specific to Manta's runtime.
- Does not touch RAG collection creation or SharePoint routing rules —
  those remain manual steps per the existing
  [`docs/DEPLOY-v4.2.md`](../../docs/DEPLOY-v4.2.md) checklist until a
  similar auto-provisioning pass is written for them.
