## Summary

v4.9 closes the AKP feedback loop: judge_score < 3 in `manta_rag_queries` now automatically triggers ticket creation in `akp_curation_backlog`. Adaptation D1' to prod schema (direct `manta_rag_queries` table, no intermediate `agent_response_flags`).

## Changes

- **Migration** – 4 additive columns on `akp_curation_backlog`: `ticket_type VARCHAR(50)` (category), `agent_slug VARCHAR(100)` (originating agent), `evidence TEXT` (judge notes excerpt), `priority SMALLINT` (1–5).
- **Trigger** – Real-time `on_judge_feedback_v4_9` (AFTER INSERT OR UPDATE OF judge_score ON manta_rag_queries WHEN score < 3). Fires stored proc `judge_feedback_handler()`.
- **Handler function** – `judge_feedback_handler()` with race-safe sequence (`akp_curation_backlog_seq`), idempotency check via UNIQUE INDEX (session_id, rag_query_id, ticket_type).
- **View** – `v_judge_feedback_health` (read-only, security_invoker=true) aggregates by agent/day + open/resolved counts. No backend changes required.
- **Signature extension** – `promote_gaps_to_backlog(user_id INTEGER, min_confidence FLOAT, batch_limit INTEGER)` now routes to judge-pattern branch (INNER JOIN manta_rag_queries).
- **5 verdict patches** – Pre-flight guard + DROP old signatures + partial UNIQUE INDEX + COMMENT on v4.6 view + race-safe sequences.
- **Cron YAML** – Updated `promote_gaps_to_backlog()` call signature in `.github/workflows/akp-daily-cron.yml`.
- **Verify script** – `backends/shared/manta_shared/verify_judge_feedback_v4_9.py` validates schema post-apply: 11/11 columns present, trigger active, handler callable.

## Migration Applied

Executed in prod 2026-07-19 via Supabase after MN gate. Pre-flight check: **PASS** (11/11 columns, sequence, trigger, handler, view, UNIQUE INDEX). Post-apply hardening: REVOKE excessive grants, cron renamed (`promote_gaps_v4_9`), verify script refactored for real schema.

## Smoke Test

1. INSERT into `manta_rag_queries(session_id, rag_query_id, judge_score, judge_notes)` with `judge_score=1`.
   → Ticket `AKP-JF-00001` created (priority=2, agent_slug from context).
2. UPDATE same row, judge_score=2 (still <3).
   → No new ticket (idempotent via UNIQUE INDEX partial on judge pattern).
3. UPDATE judge_score=5.
   → No row inserted (score ≥ 3).
4. Cleanup: TRUNCATE akp_curation_backlog → all gone.

## Rollback

Single bounded script at end of migration SQL:
```sql
DROP TRIGGER IF EXISTS on_judge_feedback_v4_9 ON manta_rag_queries;
DROP FUNCTION IF EXISTS judge_feedback_handler();
DROP VIEW IF EXISTS v_judge_feedback_health;
DROP INDEX IF EXISTS ix_akp_backlog_judge_idempotent;
DROP SEQUENCE IF EXISTS akp_curation_backlog_seq;
ALTER TABLE akp_curation_backlog DROP COLUMN IF EXISTS ticket_type, 
                                  DROP COLUMN IF EXISTS agent_slug,
                                  DROP COLUMN IF EXISTS evidence,
                                  DROP COLUMN IF EXISTS priority;
-- Restore v4.5 promote_gaps_to_backlog(INTEGER)
```

Restores `promote_gaps_to_backlog(INTEGER)` signature.

## Refs

- Migration: `supabase/migrations/2026_07_19_akp_judge_feedback_loop_v4_9.sql`
- Runbook: `docs/JUDGE-FEEDBACK-LOOP-v4.9-ADAPTED-RUNBOOK.md`
- Release notes: `docs/RELEASE-NOTES-v4.9.md`
- Commits: 55274b8, c8b86f0, cc9baf3

Closes #MNT-2026-AKP-JUDGE-LOOP.
