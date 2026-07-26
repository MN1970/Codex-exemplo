# Git Multi-Repo Workflows

**Version:** 2.0.0  
**Tier:** Sonnet  
**Updated:** 2026-07-26

## Overview

Coordinate changes across 2–5 repositories with transactional guarantees: dependency tracking, critical path analysis (PERT), cascade merge automation, and atomic rollback on any failure. Fase 1 maps dependencies; Fase 2 orchestrates safe merges and rollbacks.

## When to Use

- "Update feature across multiple repos"
- "Coordinate multi-repo release with rollback on failure"
- "Map dependencies before migration"
- "Automated microservices rollout with transaction safety"

## Inputs

```json
{
  "repos": [
    {"name": "repo-A", "branch": "main", "owner": "org"},
    {"name": "repo-B", "branch": "develop", "owner": "org"},
    {"name": "repo-C", "branch": "develop", "owner": "org"}
  ],
  "changes": [
    {
      "repo": "repo-A",
      "title": "Update API contract",
      "files": ["src/api.ts"],
      "depends_on": []
    },
    {
      "repo": "repo-B",
      "title": "Consume new API",
      "files": ["src/client.ts"],
      "depends_on": ["repo-A"]
    }
  ],
  "fase": "fase-2-cascade",
  "auto_merge": true,
  "rollback_on_failure": true,
  "dry_run": false
}
```

**Schema Validation:**
- `repos.length <= 5` (hard limit)
- All `depends_on` entries must exist in repos list
- No circular dependencies
- `fase` ∈ ["fase-1-map", "fase-2-cascade"]
- `auto_merge` requires `rollback_on_failure=true`

## Outputs

### 1. Enhanced Gantt HTML Timeline (Fase 1 + 2)
Interactive SVG with:
- **PR bars:** merged/open/blocked/failing (color-coded)
- **Dependency arrows:** critical path highlighted (red)
- **Merge milestones:** timestamp + commit SHA
- **Rollback band:** (if triggered) show revert actions on reverse timeline
- **Blockers panel:** CI failures, pending reviews, merge conflicts
- **Transaction badge:** PENDING → MERGED → COMMITTED (or ROLLED_BACK)

**Gantt with Rollback Example:**
```
[Phase 1] Dependency Analysis
repo-A   ████████████ (12h) ✓ MERGED 2026-07-26 12:00 (abc1234)
repo-B        ████████ (8h) ✓ MERGED 2026-07-26 20:00 (def5678)
repo-C             ████ (4h) ✗ FAILED post-merge test 2026-07-26 23:30

[Phase 2] Rollback (triggered 2026-07-26 23:35)
repo-C            ████ (2h) REVERTED 2026-07-27 01:35 (rb-PR#99)
repo-B         ████ (2h) REVERTED 2026-07-27 03:35 (rb-PR#98)
repo-A      ████ (2h) REVERTED 2026-07-27 05:35 (rb-PR#97)

Recovery: Incident INC-2026-07-26-001
```

### 2. Summary JSON (Fase 1 + 2)
```json
{
  "transaction_id": "txn_20260726_abc123xyz",
  "fase": "fase-2-cascade",
  "status": "ROLLED_BACK",
  "incident_id": "INC-2026-07-26-001",
  "dependency_graph": {
    "repo-A": [],
    "repo-B": ["repo-A"],
    "repo-C": ["repo-A", "repo-B"]
  },
  "topological_order": ["repo-A", "repo-B", "repo-C"],
  "critical_path": ["repo-A", "repo-B", "repo-C"],
  "critical_path_duration_minutes": 1440,
  "timeline": {
    "phase_1_start": "2026-07-26T10:00:00Z",
    "phase_1_end": "2026-07-26T10:45:00Z",
    "phase_2_merge_start": "2026-07-26T11:00:00Z",
    "phase_2_merge_end": "2026-07-26T23:30:00Z",
    "phase_2_rollback_start": "2026-07-26T23:35:00Z",
    "phase_2_rollback_end": "2026-07-27T05:35:00Z"
  },
  "merge_results": {
    "repo-A": {
      "status": "MERGED",
      "merged_at": "2026-07-26T12:00:00Z",
      "merged_commit": "abc1234567890def",
      "merged_by": "automation-bot",
      "backup_ref": "refs/backup/txn_20260726_abc123xyz/repo-A"
    },
    "repo-B": {
      "status": "MERGED",
      "merged_at": "2026-07-26T20:00:00Z",
      "merged_commit": "def5678901234567",
      "merged_by": "automation-bot",
      "backup_ref": "refs/backup/txn_20260726_abc123xyz/repo-B"
    },
    "repo-C": {
      "status": "MERGE_FAILED_CI_POST_MERGE",
      "attempted_at": "2026-07-26T23:00:00Z",
      "failure_reason": "Integration test timeout",
      "check_runs": [
        {"name": "integration-tests", "status": "failure", "conclusion": "timed_out"}
      ]
    }
  },
  "rollback_results": {
    "repo-C": {
      "status": "ROLLED_BACK",
      "reverted_at": "2026-07-27T01:35:00Z",
      "revert_pr": 99,
      "revert_commit": "rb1111111111111111"
    },
    "repo-B": {
      "status": "ROLLED_BACK",
      "reverted_at": "2026-07-27T03:35:00Z",
      "revert_pr": 98,
      "revert_commit": "rb2222222222222222"
    },
    "repo-A": {
      "status": "ROLLED_BACK",
      "reverted_at": "2026-07-27T05:35:00Z",
      "revert_pr": 97,
      "revert_commit": "rb3333333333333333"
    }
  },
  "blockers": [
    {
      "repo": "repo-C",
      "phase": "post-merge-testing",
      "reason": "integration-tests timeout",
      "severity": "critical",
      "action": "triggered cascade rollback"
    }
  ]
}
```

## Architecture

### Fase 1 (Dependency Mapping)
```
Input Validation
    ↓
Fetch PRs (GitHub MCP, parallel)
    ↓
Kahn's Topological Sort (detect cycles)
    ↓
PERT Critical Path Analysis
    ↓
Render HTML Gantt + JSON
```

### Fase 2 (Transactional Merge + Rollback)
```
Topological Order from Fase 1
    ↓
Initialize Transaction (DB: state=PENDING)
    ↓
Merge in Safe Order (Kahn sequence)
    ├→ Each PR: create backup commit refs
    ├→ Each PR: update DB (state=MERGED)
    ↓
Monitor CI + Post-Merge Tests (parallel)
    ├→ If all green → state=COMMITTED, freeze refs
    ├→ If any red → state=ROLLBACK_REQUIRED
    ↓
Cascade Rollback (if needed)
    ├→ Reverse topological order
    ├→ git revert -n (non-interactive)
    ├→ Create rollback PR per repo
    ├→ Update DB (state=ROLLED_BACK, incident_id=UUID)
    ↓
Gantt Updated: show rollback actions + recovery time
```

## Key Features

### Topological Sort (Kahn's Algorithm) — Fase 1
- Detects circular dependencies → fails fast
- Produces safe merge sequence: `[repo-A] → [repo-B, repo-C] → [repo-D]`
- Time complexity: O(V+E)

**Pseudocode:**
```
function kahn_sort(repos, deps):
    in_degree = {}
    graph = {}
    
    for each repo:
        in_degree[repo] = 0
        graph[repo] = []
    
    for each (repo, dep_on) in deps:
        graph[dep_on].append(repo)
        in_degree[repo] += 1
    
    queue = [r for r in repos if in_degree[r] == 0]
    sorted_order = []
    
    while queue:
        current = queue.pop(0)
        sorted_order.append(current)
        
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(sorted_order) != len(repos):
        raise Error("Circular dependency detected")
    
    return sorted_order
```

### Critical Path Analysis (PERT) — Fase 1
- Calculates earliest merge window for each PR
- Identifies bottleneck repos (longest serial chain)
- Estimates full completion date

**PERT Calculation:**
```
For each repo in topological order:
  earliest_start = max(earliest_finish of all dependencies, now)
  estimated_duration = (optimistic + 4*likely + pessimistic) / 6
  earliest_finish = earliest_start + estimated_duration
  
critical_path = chain with max(earliest_finish)
slack_time[repo] = earliest_finish[repo] - min(earliest_finish among peers)
```

### Cascade Merge — Fase 2
- Automatically merge PRs in safe topological order
- Skip if any CI check fails (all-or-nothing)
- Create backup commit references before each merge
- Atomic: either all merge or all rollback

**Algorithm:**
```
function cascade_merge(sorted_repos, transaction_id):
    merged_commits = {}
    backup_refs = {}
    
    for repo in sorted_repos:
        if not all_checks_green(repo):
            log_and_abort(f"CI failing in {repo}", transaction_id)
            break
        
        backup_ref = f"refs/backup/{transaction_id}/{repo}"
        exec(f"git update-ref {backup_ref} HEAD")
        backup_refs[repo] = backup_ref
        
        merge_result = exec(f"gh pr merge {pr_num} --merge")
        if merge_result.error:
            log_error(f"Merge failed: {repo}", transaction_id)
            break
        
        merged_commits[repo] = merge_result.merged_commit_sha
        db_update(transaction_id, repo, "MERGED", merged_commits[repo])
    
    return {merged_commits, backup_refs, transaction_id}
```

### Transactional Rollback — Fase 2
- Reverse merges in opposite topological order
- Non-interactive git revert (avoid merge conflicts in rollback)
- Create public rollback PRs for audit trail
- Idempotent: safe to re-run

**Rollback Steps:**
```
function cascade_rollback(merged_commits, backup_refs, transaction_id):
    incident_id = generate_uuid()
    
    for repo in reverse(topological_order):
        if repo not in merged_commits:
            continue  # Skip repos that weren't merged
        
        original_head = backup_refs[repo]
        merged_commit = merged_commits[repo]
        
        # Revert merge commit (non-interactive)
        exec(f"git revert -n {merged_commit}")
        
        # Create rollback PR
        rb_branch = f"rollback/{transaction_id}/{repo}"
        exec(f"git checkout -b {rb_branch}")
        exec(f"git commit -m 'Rollback {transaction_id}: {incident_id}'")
        
        pr_result = exec(f"gh pr create \
            --title 'ROLLBACK: {transaction_id}' \
            --body 'Automatic rollback due to post-merge test failure. Incident: {incident_id}' \
            --draft")
        
        db_update(transaction_id, repo, "ROLLED_BACK", {
            incident_id, 
            rollback_pr: pr_result.pr_number,
            rollback_time: now()
        })
    
    return {transaction_id, incident_id}
```

### Blocker Detection — Fase 1
- Pending CI checks
- Pending code reviews
- Merge conflicts
- Dependency not merged

## MCP Tools

- `github__list_pull_requests` — fetch branch PRs
- `github__get_commit` — extract created/merged dates
- `github__create_pull_request` — create rollback PRs (Fase 2)
- `github__merge_pull_request` — auto-merge in cascade order (Fase 2)

## SQL Schema — Transaction State Tracking (Fase 2)

Store transactional state in a PostgreSQL/Supabase database to enable idempotent rollbacks and audit trails.

```sql
-- Transactions (one per multi-repo workflow run)
CREATE TABLE git_transactions (
    transaction_id UUID PRIMARY KEY,
    initiated_at TIMESTAMP NOT NULL DEFAULT now(),
    initiated_by TEXT NOT NULL,  -- GitHub username
    repos_json JSONB NOT NULL,   -- array of {name, owner, branch}
    dependencies_json JSONB NOT NULL,  -- {repo: [deps...]}
    topological_order TEXT[] NOT NULL,
    critical_path_minutes INT,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'MERGING', 'COMMITTED', 'ROLLBACK_REQUIRED', 'ROLLED_BACK', 'FAILED')),
    incident_id UUID,  -- null until rollback triggered
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
CREATE INDEX idx_git_transactions_status ON git_transactions(status);
CREATE INDEX idx_git_transactions_incident ON git_transactions(incident_id) WHERE incident_id IS NOT NULL;

-- Per-repo merge history (one row per repo per transaction)
CREATE TABLE git_transaction_repos (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL REFERENCES git_transactions(transaction_id) ON DELETE CASCADE,
    repo_name TEXT NOT NULL,
    repo_owner TEXT NOT NULL,
    target_branch TEXT NOT NULL,
    pr_number INT,
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'MERGED', 'FAILED', 'ROLLED_BACK')),
    merged_commit_sha TEXT,
    merged_at TIMESTAMP,
    merged_by TEXT,  -- GitHub username
    backup_ref TEXT,  -- refs/backup/{txn_id}/{repo}
    revert_pr_number INT,  -- for rollback
    reverted_at TIMESTAMP,
    revert_commit_sha TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    UNIQUE(transaction_id, repo_name, repo_owner)
);
CREATE INDEX idx_transaction_repos_txn ON git_transaction_repos(transaction_id);
CREATE INDEX idx_transaction_repos_status ON git_transaction_repos(status);

-- Incidents (rollback events)
CREATE TABLE git_incidents (
    incident_id UUID PRIMARY KEY,
    transaction_id UUID NOT NULL REFERENCES git_transactions(transaction_id) ON DELETE CASCADE,
    triggered_at TIMESTAMP NOT NULL DEFAULT now(),
    trigger_reason TEXT NOT NULL,  -- e.g., "integration-tests timeout"
    trigger_repo TEXT NOT NULL,  -- which repo failed post-merge tests
    rollback_started_at TIMESTAMP,
    rollback_completed_at TIMESTAMP,
    rollback_status TEXT CHECK (rollback_status IN ('IN_PROGRESS', 'COMPLETED', 'FAILED')),
    root_cause_analysis TEXT,  -- filled post-incident
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX idx_incidents_txn ON git_incidents(transaction_id);
CREATE INDEX idx_incidents_trigger_repo ON git_incidents(trigger_repo);

-- Audit log (immutable, one row per state change)
CREATE TABLE git_audit_log (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL REFERENCES git_transactions(transaction_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,  -- MERGE, ROLLBACK, CI_CHECK, BLOCKER, etc.
    repo_name TEXT,
    old_state TEXT,
    new_state TEXT,
    actor TEXT NOT NULL,  -- 'automation-bot' or GitHub username
    actor_type TEXT CHECK (actor_type IN ('automation', 'human')),
    details_json JSONB,  -- commit SHA, PR URL, etc.
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_log_txn ON git_audit_log(transaction_id);
CREATE INDEX idx_audit_log_event ON git_audit_log(event_type);
CREATE INDEX idx_audit_log_actor ON git_audit_log(actor);

-- Views for common queries
CREATE VIEW git_transaction_summary AS
SELECT
    gt.transaction_id,
    gt.status,
    gt.incident_id,
    COUNT(CASE WHEN gtr.status = 'MERGED' THEN 1 END) as repos_merged,
    COUNT(CASE WHEN gtr.status = 'ROLLED_BACK' THEN 1 END) as repos_rolled_back,
    COUNT(CASE WHEN gtr.status = 'FAILED' THEN 1 END) as repos_failed,
    EXTRACT(EPOCH FROM (gt.updated_at - gt.created_at)) / 60.0 as duration_minutes,
    gt.initiated_by,
    gt.created_at
FROM git_transactions gt
LEFT JOIN git_transaction_repos gtr ON gt.transaction_id = gtr.transaction_id
GROUP BY gt.transaction_id;

CREATE VIEW git_active_incidents AS
SELECT
    gi.incident_id,
    gi.transaction_id,
    gi.trigger_reason,
    gi.trigger_repo,
    gi.triggered_at,
    EXTRACT(EPOCH FROM (NOW() - gi.triggered_at)) / 60.0 as minutes_since_trigger,
    COUNT(gtr.id) as repos_involved
FROM git_incidents gi
LEFT JOIN git_transaction_repos gtr ON gi.transaction_id = gtr.transaction_id
WHERE gi.rollback_status IN ('IN_PROGRESS', NULL)
GROUP BY gi.incident_id;
```

**Schema Notes:**
- All timestamps in UTC
- `transaction_id` is immutable key for entire workflow
- `backup_ref` enables instant rollback to pre-merge state
- `git_audit_log` is append-only (no deletes) for compliance
- Views provide dashboards for monitoring + incident response

## Examples

### Example 1: Feature Rollout (3 repos) — Fase 1

**Input:**
```json
{
  "repos": [
    {"name": "graphql-server", "branch": "main", "owner": "myorg"},
    {"name": "react-client", "branch": "main", "owner": "myorg"},
    {"name": "mobile-app", "branch": "main", "owner": "myorg"}
  ],
  "changes": [
    {
      "repo": "graphql-server",
      "title": "Add new Query",
      "depends_on": []
    },
    {
      "repo": "react-client",
      "title": "Consume Query",
      "depends_on": ["graphql-server"]
    },
    {
      "repo": "mobile-app",
      "title": "Consume Query",
      "depends_on": ["graphql-server"]
    }
  ],
  "fase": "fase-1-map"
}
```

**Output (Gantt):**
```
[graphql-server] ████████████ (12h) → MERGED
                          ├→ [react-client]   ████████ (8h) → MERGED
                          ├→ [mobile-app]     ████████ (8h) → OPEN (waiting review)
```

**Critical Path:** graphql-server → mobile-app (20h total)

---

### Example 2: 5-Repo Microservices Rollout with Rollback (Fase 2) ⭐

**Real-world scenario:** Coordinating a payment system upgrade across 5 microservices with automatic rollback on failure.

**Input:**
```json
{
  "repos": [
    {"name": "payment-contracts", "branch": "main", "owner": "acmecorp"},
    {"name": "payment-service", "branch": "main", "owner": "acmecorp"},
    {"name": "billing-service", "branch": "main", "owner": "acmecorp"},
    {"name": "api-gateway", "branch": "main", "owner": "acmecorp"},
    {"name": "fraud-detector", "branch": "main", "owner": "acmecorp"}
  ],
  "changes": [
    {
      "repo": "payment-contracts",
      "title": "Add v3 PaymentProcessor interface",
      "files": ["src/contracts/payment.proto"],
      "depends_on": []
    },
    {
      "repo": "payment-service",
      "title": "Implement PaymentProcessor v3",
      "files": ["src/service/processor.go"],
      "depends_on": ["payment-contracts"]
    },
    {
      "repo": "billing-service",
      "title": "Consume PaymentProcessor v3",
      "files": ["src/client/payment.go"],
      "depends_on": ["payment-contracts"]
    },
    {
      "repo": "api-gateway",
      "title": "Update payment endpoint routing",
      "files": ["src/routes/payment.ts"],
      "depends_on": ["payment-service", "billing-service"]
    },
    {
      "repo": "fraud-detector",
      "title": "Add v3 payload inspection",
      "files": ["src/rules/payment.json"],
      "depends_on": ["payment-contracts"]
    }
  ],
  "fase": "fase-2-cascade",
  "auto_merge": true,
  "rollback_on_failure": true,
  "dry_run": false
}
```

**Execution Timeline:**

**Phase 1 (Dependency Analysis) — 0min–5min**
```
Kahn sort: [payment-contracts] → [payment-service, billing-service, fraud-detector] → [api-gateway]
PERT: critical path = payment-contracts → payment-service → api-gateway (estimated 240 min)
Status: All CI green, no blockers
```

**Phase 2 (Merge Execution) — 5min–120min**
```
10:05 — [payment-contracts] MERGED ✓ (commit abc1234, backup ref set)
10:25 — [payment-service] MERGED ✓ (commit def5678, backup ref set)
10:40 — [billing-service] MERGED ✓ (commit ghi9012, backup ref set)
10:55 — [fraud-detector] MERGED ✓ (commit jkl3456, backup ref set)
11:15 — [api-gateway] MERGED ✓ (commit mno7890, backup ref set)

Transaction state: MERGING → post-merge CI checks
```

**Phase 2 (Post-Merge Testing) — 120min–130min — ⚠️ FAILURE**
```
11:20 — api-gateway: integration-tests FAILED
        └─ Error: "PaymentProcessor v3 timeout in downstream call to fraud-detector"
        └─ Reason: fraud-detector not yet deployed; mismatched v3 payload format

Transaction state: ROLLBACK_REQUIRED
Incident ID: INC-2026-07-26-001
```

**Phase 3 (Cascade Rollback) — 130min–200min**
```
11:25 — Initiating rollback (reverse topological order)
        Incident INC-2026-07-26-001 triggered by fraud-detector payload mismatch

11:26 — [api-gateway] REVERTED ✓
        └─ git revert -n mno7890
        └─ Rollback PR #203 created
        └─ Revert commit rb0001111

11:40 — [fraud-detector] REVERTED ✓
        └─ Rollback PR #202 created
        └─ Revert commit rb0002222

11:54 — [billing-service] REVERTED ✓
        └─ Rollback PR #201 created
        └─ Revert commit rb0003333

12:08 — [payment-service] REVERTED ✓
        └─ Rollback PR #200 created
        └─ Revert commit rb0004444

12:22 — [payment-contracts] REVERTED ✓
        └─ Rollback PR #199 created
        └─ Revert commit rb0005555

Transaction state: ROLLED_BACK
All repos back to main@abc0000 (pre-transaction)
Recovery time: 75 minutes
```

**Output (Gantt with Rollback):**
```
[MERGE PHASE]
payment-contracts     ██████░░░░░░░░░░░ 0m–20m MERGED
payment-service          ██████░░░░░░░░ 20m–40m MERGED
billing-service           ██████░░░░░░░ 20m–35m MERGED
fraud-detector            ██████░░░░░░░ 20m–35m MERGED
api-gateway                   ██████░░░░ 40m–60m MERGED

[POST-MERGE TESTING — FAILURE]
api-gateway              ci check ✗ 120m timeout

[ROLLBACK PHASE]
api-gateway                      ██████░░░ 130m–145m REVERTED
fraud-detector                   ██████░░░ 130m–160m REVERTED (depends)
billing-service                  ██████░░░ 130m–175m REVERTED (depends)
payment-service                  ██████░░░ 130m–190m REVERTED (depends)
payment-contracts                ██████░░░ 130m–205m REVERTED (depends)

Total time: 205 minutes (including rollback)
Status: ROLLED_BACK | Incident: INC-2026-07-26-001
```

**Root Cause (Post-Incident):**
- fraud-detector v3 schema not registered in discovery service
- api-gateway routed to fraud-detector before it was deployed
- **Fix:** Add pre-deployment validation in CI (check all dependencies deployed before merging api-gateway)

**Lessons Learned:**
1. Payment contracts must have min 2-hour soak time before consumer merges
2. Add mutual health-check before cascade merge: each service can reach all dependencies at v3
3. Add canary stage: run integration tests against pre-merge state first

---

### Example 3: Migration with Dependencies — Fase 1

**Scenario:** Multi-service library migration

**Topological Order:** [shared-lib] → [service-A, service-B] → [api-gateway]

**Key insight:** Shared-lib must be merged first; then services A and B can merge in parallel; finally api-gateway waits for both.

**PERT Estimate:**
- shared-lib: 2h
- service-A, service-B: 3h (parallel)
- api-gateway: 1h
- **Total: 6h** (not 9h, because A and B are parallel)

## Constraints & Limits

### Hard Limits
| Constraint | Limit | Rationale |
|------------|-------|-----------|
| Repos per run | 5 max | Reduces cognitive load, avoids parallelism explosion |
| Cascading depth | 3 levels max | Mitigates cascading rollback complexity |
| Transaction age | 24h | Prevents stale backup refs from expiring |
| Concurrent transactions | 1 per org | Serializes to prevent merge conflicts |
| Rollback parallelism | Sequential | Ensures consistent git history |

### Rate Limits
- GitHub API: 100 requests/hour (per token)
- POST /repos/{owner}/{repo}/git/refs: 10/min per repo
- git push: 1/sec per repo

### Failure Scenarios (Graceful Degradation)

| Scenario | Behavior |
|----------|----------|
| PR merge conflict detected | Abort before merge, return conflict delta |
| Post-merge CI timeout (>1h) | Abort, trigger rollback automatically |
| Rollback PR creation fails | Retry 3x; if 3x fail, escalate to on-call |
| GitHub API rate limit hit | Back off exponentially; pause until reset |
| Incomplete rollback | Idempotent re-run: detect prior state, continue |

## Limitations

- **No rebases during workflow** — assumes linear main/develop branches
- **No force-pushes** — would invalidate backup refs
- **Post-merge tests only** — pre-merge checks are standard GitHub checks
- **GitHub-centric** — currently only supports GitHub (GitLab roadmap TBD)
- **Synchronous transaction model** — async notifications TBD

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Circular dependency detected" | Check `depends_on` fields; use `kahn_sort()` to validate |
| "Timeout fetching PR data" | Split into smaller batches (≤3 repos); check GitHub API status |
| "Merge conflict not resolved" | PR already has conflicts; resolve manually, re-push to branch, retry |
| "Rollback failed for repo-X" | Check git refs; run `mcp__github__list_branches` to verify backup ref exists |
| "Transaction stuck in MERGING" | Manual recovery: query `git_transactions` table, set status=FAILED, create incident |
| "Cannot merge: insufficient permissions" | Verify GitHub token has `repo:write` + `admin:repo_hook` scopes |

## Safety & Guardrails — Fase 2

### Pre-Merge Validation (required)
```
✓ All repos exist + accessible
✓ All branches trackable (no detached HEAD)
✓ No circular dependencies
✓ All PRs pass GitHub checks (CI, reviews)
✓ No pending conflicts
✓ Repos count ≤ 5
✓ Backup refs unique per transaction
```

### Merge Safeguards (automatic)
- **Atomic:** All-or-nothing (no partial merges)
- **Idempotent:** Re-run safe after any failure
- **Auditable:** Every action logged to `git_audit_log`
- **Reversible:** Rollback PRs created (public, reviewable)
- **Non-destructive:** Original commits preserved in backup refs

### Rollback Safeguards
- **No interactive conflicts:** Use `git revert -n` (stage only, don't commit)
- **Sequential order:** Reverse topological order prevents dangling dependencies
- **Human approval:** Rollback PRs created as drafts (requires review before merge)
- **Incident tracking:** INC-YYYY-MM-DD-NNN created for each rollback

### Operator Responsibilities
1. **Before cascade merge:** Verify all 5 repos + dependencies with `--dry-run`
2. **Monitor during merge:** Watch for CI failures (don't let auto-merge proceed if blocked)
3. **Post-merge (if failed):** Review rollback PRs before auto-merging them
4. **After rollback:** File incident ticket, root-cause analysis (RCA) in `git_incidents.root_cause_analysis`

---

## How to Use This Skill

### Invocation (Fase 1 — Dependency Analysis)
```
User: "Map dependencies for payment-contracts update across 5 repos"

Claude:
1. Validate input (≤5 repos, no cycles)
2. Fetch PRs from all repos
3. Run Kahn sort
4. Calculate PERT (critical path)
5. Render Gantt + JSON summary
6. Return: HTML Gantt + JSON transaction_id (for Fase 2)
```

### Invocation (Fase 2 — Cascade Merge with Rollback)
```
User: "Run phase 2 on transaction txn_20260726_abc123xyz with auto-merge=true"

Claude:
1. Fetch transaction from DB (validate state=PENDING)
2. Run cascade_merge() in topological order
3. Monitor post-merge CI checks (poll every 30s for 2h)
4. If all green:
   - Set transaction state=COMMITTED
   - Freeze backup refs (move to refs/frozen/)
5. If any fail:
   - Set state=ROLLBACK_REQUIRED
   - Create incident (INC-YYYY-MM-DD-NNN)
   - Run cascade_rollback() (reverse order)
   - Create rollback PRs (as drafts)
   - Return rollback summary
```

### Invocation (Manual Rollback Recovery)
```
User: "Recover transaction txn_20260726_abc123xyz — it's stuck in MERGING"

Claude:
1. Query git_transactions WHERE transaction_id = txn_...
2. Query git_transaction_repos (check which repos have backup_ref set)
3. Restart cascade_rollback from last successful repo
4. Update incident with recovery notes
5. Return recovery timeline
```

---

## Related Skills

- `git-gitops-flow` — single repo sync
- `git-commit-optimizer` — rebase prep
- `github-actions-monitor` — CI/CD health checks
- `incident-commander` — post-rollback RCA orchestration

---

## Implementation Checklist

### Fase 1 (Complete ✅)
- [x] Kahn topological sort algorithm
- [x] PERT critical path calculation
- [x] Gantt timeline renderer (SVG)
- [x] Blocker detection (CI, reviews, conflicts)
- [x] JSON summary output

### Fase 2 (This Update 🎯)
- [x] Cascade merge algorithm (topological order)
- [x] Backup ref creation + tracking
- [x] Post-merge CI check polling
- [x] Transactional rollback algorithm
- [x] Rollback PR creation (draft mode)
- [x] SQL schema (`git_transactions`, `git_transaction_repos`, `git_incidents`, `git_audit_log`)
- [x] Enhanced Gantt with rollback timeline
- [x] 5-repo microservices example
- [x] Safety guardrails + limits
- [x] Incident tracking (INC-YYYY-MM-DD-NNN)
- [x] Idempotency guarantees
- [x] Usage documentation + recovery procedures

### Fase 3 (Future 🗓️)
- [ ] Async notifications (Slack, PagerDuty)
- [ ] Canary stages (deploy to staging before main)
- [ ] GitLab + Gitea support
- [ ] Manual approval gates (per repo)
- [ ] Automated RCA (parse CI logs, suggest fixes)
- [ ] Undo limit: allow 7-day rollforward from frozen refs
- [ ] Multi-org federation (cross-org PRs)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-07-26 | **Fase 2 Release:** Transactional merge + rollback, SQL schema, cascade automation, 5-repo limit enforced |
| 1.0.0 | 2026-07-15 | **Initial:** Fase 1 dependency mapping, Kahn sort, PERT analysis, Gantt renderer |

---

## Contact & Support

- **Issue tracker:** github.com/acmecorp/git-multi-repo-workflows/issues
- **Slack:** #platform-devops
- **On-call:** PagerDuty "Multi-Repo Orchestration"

For questions on transactional rollback or incident recovery, file an issue with:
- transaction_id (from output JSON)
- Current git log --oneline (per repo)
- Screenshots of rollback PRs

