# SKILL.md — git-gitops-flow

**GitOps Phase 3: ML-powered auto-merge confidence scoring with intelligent routing, fallback safety gates, and explainable recommendations. Extends Phase 2 production-grade syncs with machine-learning-driven decision gates.**

Version: **3.0.0** | Tier: **Sonnet** | MCPs: **GitHub (create_branch, create_pull_request, list_commits, search_code, merge_pull_request, update_pull_request_branch), GitHub Actions (workflow dispatch), git-auto-merge-confidence (ML inference)** | Output: **Confidence-scored PR + ML Recommendation + Feature Importance + Fallback Safety Audit**

---

## Overview

Production-grade GitOps synchronization with **ML-driven confidence scoring** that maintains state consistency across **up to 5+ repositories** using:
- **Drift Detection** — Compares files, branches, or structured data across N repos with fan-out pattern
- **ML-Based Auto-Merge** (v3.0) — Machine-learning confidence scoring replaces 5-condition gate (confidence ≥0.95 → auto-merge, 0.75–0.95 → escalate, <0.75 → reject)
- **Intelligent Fallback** (v3.0) — If ML service unavailable, fall back to hardcoded 5-condition safety checks
- **Explainability** (v3.0) — Feature importance breakdown for marginal confidence scores (shows top factors affecting merge decision)
- **Sync Strategies** — Copy file, merge branch, rebase-onto-main, squash-fixups, three-way merge
- **Transactional Rollback** — Atomic revert on merge failure; reverts all downstream syncs
- **Conflict Resolution** — LCS-based three-way merge with smart escalation rules (package.json, Dockerfile, .tf files require human approval)
- **Scheduled Syncs** — GitHub Actions-based recurring syncs (cron + event-driven triggers)
- **Conflict Reporting** — JSON findings + human-readable issue if conflicts cannot auto-resolve
- **Commit Graph** — Visual timeline of sync operations with contributor attribution
- **Audit Logging** — Supabase-backed compliance log (who, what, when, risk level, rollback chain, ML confidence score)
- **MCP Integration** — GitHub create_branch/create_pull_request/merge_pull_request + git-auto-merge-confidence ML inference for fully automated workflows

**Phase 3 use cases**: ML-driven auto-merge across deployment pipeline (dev→staging→prod) with confidence-based escalation, multi-region rollout with explainable merge decisions, automated cost/schedule baselines with confidence scoring, infrastructure rollback with ML safety assurance, on-call escalation routing based on confidence tiers.

---

## Capability Matrix

| Feature | Phase 1 | Phase 2 | Phase 3 | Strategy | Output |
|---|---|---|---|---|---|
| **Drift Detection** | ✅ 1–2 repos | ✅ 5+ repos | ✅ + ML-scored | Byte-exact hash compare + fan-out | JSON delta report |
| **Branch Sync** | ✅ | ✅ | ✅ | `git merge --ff-only` simulation | Auto-created PR or issue if not FFable |
| **Rebase Sync** | ✅ Linear history | ✅ + squash-fixups | ✅ | Simulate `git rebase --onto-main` + commit squashing | Auto-PR with linear history |
| **Three-way Merge** | ✅ Basic | ✅ **Advanced LCS** | ✅ + ML input | Full longest-common-subsequence algorithm | Issue with merge diff blocks + acceptance rules |
| **File Copy** | ✅ | ✅ | ✅ | Byte-exact replace or append | Direct commit + PR |
| **Conflict Resolution** | ⚠ Semi-auto | ✅ **Smart escalation** | ✅ | LCS merge + high-risk file detection | Labeled issue + suggested patches |
| **Auto-Merge** | ❌ Draft only | ✅ **5-condition** | ✅ **ML Confidence** | ML scoring (≥0.95) replaces 5-condition gate | Auto-merged PR + confidence score + feature importance |
| **ML Confidence Scoring** | ❌ | ❌ | ✅ **NEW v3.0** | ML inference on 9 features (tests, security, files, etc.) | confidence_score + recommendation + feature_importance |
| **Fallback Safety Gate** | ❌ | ✅ Hardcoded | ✅ **Automatic** | If ML unavailable, use Phase 2 5-condition gate | Audit entry: fallback_gate_used=true |
| **Explainability** | ❌ | ❌ | ✅ **NEW v3.0** | Feature importance breakdown for marginal scores | Top 3 factors + contribution weights + actionable recommendations |
| **Commit Graph** | ✅ Visualization | ✅ | ✅ | DAG with timestamps + authors | SVG/Mermaid diagram embed |
| **Scheduled Syncs** | ❌ Manual | ✅ **GitHub Actions** | ✅ | Cron + event-driven workflows with retries | PR/merge on schedule |
| **Transactional Rollback** | ✅ Single PR revert | ✅ **Atomic cascade** | ✅ | On merge fail, revert all downstream syncs in reverse order | New PR + rollback chain audit log |
| **Status Reporting** | ✅ Real-time | ✅ | ✅ + ML confidence | GitHub check run + Slack notifications | PR comment + job summary + confidence % |
| **Escalation Rules** | ❌ All auto | ✅ **High-risk detection** | ✅ **ML-driven** | Detects package.json, Dockerfile, *.tf, secrets + ML factors | Requires human approval before merge |
| **Audit Logging** | ⚠ PR comments | ✅ **Supabase table** | ✅ **ML audit trail** | JSON audit trail + ML confidence + feature importance | Compliance-ready log + ML explainability audit |

---

## Phase 3 — ML-Based Auto-Merge Confidence Scoring

**NEW in v3.0**: Machine-learning-driven confidence scoring replaces the hardcoded 5-condition gate. Each PR receives a **confidence score (0.0–1.0)** and explicit recommendation.

### ML Confidence Scoring Model

The `git-auto-merge-confidence` service analyzes PR metadata and predicts merge safety:

```
Inputs to ML model:
  - Test results (pass/fail/pending status)
  - Security scan outcomes (CRITICAL/HIGH/MEDIUM/LOW)
  - File change patterns (risk classification per file)
  - Repo fan-out count (number of target repos)
  - LCS similarity scores (for three-way merges)
  - Commit message quality (conventional commits, linked issues)
  - Author history (trusted committer vs. new contributor)
  - Deployment history (success rate of past syncs)
  - Time of day (off-peak syncs have lower risk)

Output:
  - confidence_score: float [0.0–1.0]
  - recommendation: enum ["AUTO_MERGE", "ESCALATE", "REJECT"]
  - feature_importance: dict {feature_name: importance_weight}
  - explanation: string (human-readable reason)
```

### Decision Logic: Confidence-Based Routing

Based on ML confidence score:

```
┌─ Score ≥ 0.95
│   └─ Recommendation: AUTO_MERGE
│       └─ Action: Merge immediately (no human gate required)
│       └─ Post: Audit log entry with confidence score
│       └─ Notification: Silent merge to #deployments (optional)
│
├─ Score 0.75–0.95
│   └─ Recommendation: ESCALATE
│       └─ Action: Hold PR, request human approval
│       └─ Post: Comment with confidence breakdown + feature importance
│       └─ Assign: to escalation team (ops, infra, security per risk)
│       └─ Timeout: 24 hours (auto-reject if no approval)
│       └─ Notification: Alert #incident-response with confidence + reason
│
└─ Score < 0.75
    └─ Recommendation: REJECT
        └─ Action: Block PR, add label "confidence-too-low"
        └─ Post: Comment explaining why confidence is low
        └─ Require: Significant changes or risk reduction before re-evaluation
        └─ Notification: Alert author + dev team
```

### Fallback Mechanism: Safety Hardcoded Gate

If ML service is **unavailable** (timeout, error, degraded), fall back to hardcoded 5-condition gate:

```yaml
fallback:
  enabled: true
  trigger: ml_service_unavailable
  
  conditions:
    - tests_passing: true
    - zero_critical_severities: true
    - low_risk_file_patterns: true
    - repo_count_lte_5: true
    - audit_logged: true
  
  behavior:
    if_all_pass: "auto_merge"
    if_any_fail: "escalate"
    audit_entry: "fallback_gate_used: true"
  
  # Fallback is stricter than ML: requires ALL 5 conditions
  # This ensures safety during ML service degradation
```

### ML Confidence Configuration

```yaml
gitops:
  auto_merge:
    enabled: true
    
    # ===== NEW in v3.0: ML Scoring =====
    ml_confidence:
      enabled: true
      service: "git-auto-merge-confidence"
      endpoint: "https://ml.gitops.svc/confidence"
      timeout_ms: 5000
      
      # Confidence thresholds
      auto_merge_threshold: 0.95
      escalate_threshold: 0.75
      reject_threshold: 0.0  # anything below 0.75 is rejected
      
      # Feature weights (configurable)
      feature_weights:
        test_pass_rate: 0.25
        security_clean: 0.20
        file_risk_score: 0.20
        repo_count: 0.10
        lcs_similarity: 0.10
        author_trustworthiness: 0.08
        deployment_history: 0.04
        time_of_day: 0.03
      
      # Fallback to hardcoded gate if ML fails
      fallback:
        enabled: true
        use_hardcoded_5_conditions: true  # Fallback to Phase 2 5-condition gate
        
        # Fallback is STRICTER: all 5 conditions must pass to auto-merge
        fallback_auto_merge_only_if_all_pass: true
    
    # ===== PHASE 2 Hardcoded Conditions (fallback) =====
    condition_checks:
      tests_required: true
      allow_ignored_checks: ["optional-e2e", "performance-benchmark"]
      security_scan_required: true
      max_critical_issues: 0
      max_high_issues: 0
    
    risk_patterns:
      high_risk_files:
        - "package*.json"
        - "Dockerfile*"
        - "*.tf"
        - ".env*"
        - "*secret*"
        - "k8s/**/*.yaml"
      max_files_changed: 20
      max_lines_changed: 500
    
    max_target_repos: 5
    audit_table: "gitops_audit"
    audit_required: true
    
    # Notifications
    notify_on_auto_merge: true
    notify_channels:
      slack: "#deployments"
      github: "comment-on-pr"
```

### ML Scoring Decision Flowchart (v3.0)

```
START: GitOps PR Created
  │
  ├─── Call: git-auto-merge-confidence API
  │    ├─ SUCCESS: Receive confidence_score [0.0–1.0]
  │    │   └─ Proceed to routing (below)
  │    │
  │    └─ FAILED (timeout/error):
  │        └─ Fallback: Use hardcoded 5-condition gate
  │           ├─ Check all 5 conditions
  │           ├─ If all pass → AUTO_MERGE
  │           └─ If any fail → ESCALATE
  │
  ├─── ROUTING by Confidence Score
  │
  ├─── Score ≥ 0.95 (HIGH confidence)
  │    ├─ Recommendation: AUTO_MERGE ✅
  │    ├─ Add label: "auto-merge-confident"
  │    ├─ Post comment: "ML Confidence: {score}% | {explanation}"
  │    ├─ Update audit: {ml_confidence: score, recommendation: AUTO_MERGE}
  │    ├─ Merge PR immediately
  │    └─ On success:
  │        ├─ Audit: {merged_at: timestamp, auto_merged: true, ml_scored: true}
  │        └─ Slack: "✅ Auto-merged (confidence: {score}%)"
  │
  ├─── Score 0.75–0.95 (MEDIUM confidence)
  │    ├─ Recommendation: ESCALATE ⚠️
  │    ├─ Add label: "requires-human-approval"
  │    ├─ Post comment: "ML Confidence: {score}% (below auto-merge threshold)"
  │    ├─ Feature importance breakdown:
  │    │   └─ Show top 3 factors affecting confidence (and their weights)
  │    ├─ Assign to: escalation team (based on risk category)
  │    ├─ Set timeout: 24 hours
  │    ├─ Update audit: {ml_confidence: score, recommendation: ESCALATE, escalation_reason: ...}
  │    │
  │    └─ ON APPROVAL (within 24h):
  │        ├─ Merge PR
  │        └─ Audit: {manual_approval: true, approved_by: user, approval_timestamp}
  │
  │    └─ ON TIMEOUT (no approval in 24h):
  │        ├─ Auto-reject PR
  │        ├─ Add label: "escalation-timeout"
  │        ├─ Comment: "Escalation expired. Requires manual re-submission."
  │        └─ Audit: {escalation_timeout: true, auto_rejected: true}
  │
  └─── Score < 0.75 (LOW confidence)
       ├─ Recommendation: REJECT ❌
       ├─ Add label: "confidence-too-low"
       ├─ Post comment: "ML Confidence: {score}% | Below rejection threshold"
       ├─ Show feature importance: "Factors preventing merge:"
       ├─ Update audit: {ml_confidence: score, recommendation: REJECT, reason: ...}
       │
       └─ Author Action Required:
           ├─ Fix identified risks (see feature importance)
           ├─ Request ML re-evaluation after changes
           └─ Or: Escalate manually (rare)
```

### Feature Importance Output (NEW v3.0)

When ML confidence is marginal (0.75–0.95), the system provides explainability:

```json
{
  "confidence_score": 0.82,
  "recommendation": "ESCALATE",
  "feature_importance": {
    "test_pass_rate": {
      "weight": 0.25,
      "contribution": -0.08,
      "reason": "2 out of 10 checks still pending"
    },
    "file_risk_score": {
      "weight": 0.20,
      "contribution": -0.12,
      "reason": "terraform/main.tf detected (high-risk file)"
    },
    "security_clean": {
      "weight": 0.20,
      "contribution": 0.20,
      "reason": "No CRITICAL or HIGH vulnerabilities"
    },
    "lcs_similarity": {
      "weight": 0.10,
      "contribution": 0.08,
      "reason": "LCS similarity 0.92 (high overlap with upstream)"
    },
    "author_trustworthiness": {
      "weight": 0.08,
      "contribution": 0.02,
      "reason": "Author has 12 prior successful merges"
    },
    "repo_count": {
      "weight": 0.10,
      "contribution": 0.10,
      "reason": "Syncing to 3 repos (below threshold of 5)"
    },
    "deployment_history": {
      "weight": 0.04,
      "contribution": 0.04,
      "reason": "Recent syncs: 100% success rate (5/5)"
    },
    "time_of_day": {
      "weight": 0.03,
      "contribution": 0.02,
      "reason": "Merge at 10:30 AM UTC (business hours, lower risk)"
    }
  },
  "explanation": "Confidence below auto-merge threshold due to pending test checks and high-risk infrastructure file. Recommend: wait for test completion, then escalate infrastructure team for terraform review.",
  "recommendations": [
    "Wait for remaining 2 checks to complete",
    "Request infrastructure team approval for terraform/main.tf changes",
    "After approval, re-evaluate for auto-merge"
  ]
}
```

---

## Architecture

### Input Phase

1. **Repo Declaration**
   ```
   Repo A: owner/name#branch (source)
   Repo B: owner/name#branch (target)
   ```

2. **Sync Type Selection**
   - `copy-file`: Single/multiple files from A → B
   - `merge-branch`: Merge A's branch into B's branch
   - `rebase`: Rebase B on top of A
   - `three-way-merge`: Resolve conflicts via LCS
   - `detect-drift`: Report differences without syncing

3. **Conflict Strategy**
   - `auto-merge`: Attempt automatic resolution
   - `manual-review`: Create issue for human review
   - `ours`: Prefer target repo changes
   - `theirs`: Prefer source repo changes

### Processing Phase

1. **Clone/Fetch** — Retrieve both repos (or branches) via GitHub API
2. **Diff Analysis** — Compute delta using:
   - File hash comparison
   - Line-by-line diff (unified format)
   - JSON/YAML merge diff for structured data
3. **Conflict Detection** — Flag overlapping changes using three-way merge algorithm
4. **Auto-Resolution** — Apply selected strategy
5. **PR/Branch Creation** — Use GitHub MCP to create branches and PRs
6. **ML Confidence Scoring** (NEW v3.0):
   - Extract PR metadata (tests, security, files, author, history, etc.)
   - Call `git-auto-merge-confidence` ML inference service
   - Receive confidence_score + recommendation + feature_importance
   - If ML unavailable: fall back to hardcoded 5-condition gate
   - Record ML audit entry
7. **Confidence-Based Routing** (NEW v3.0):
   - Score ≥ 0.95: proceed to auto-merge
   - Score 0.75–0.95: escalate with feature importance breakdown
   - Score < 0.75: reject with actionable recommendations
8. **Reporting** — Generate commit graph + findings JSON + ML confidence audit

### Output Phase

- **If successful**: Auto-created PR with:
  - Descriptive title: `GitOps: Sync {source}#{branch} → {target}#{branch}`
  - Commit-based changelog
  - Link to commit graph
  - Status: **ready to merge** (if auto-approved) or **review required**

- **If conflicts**: GitHub issue with:
  - Conflict blocks (file:line:before:after)
  - Suggested resolution (LCS merge or manual blocks)
  - Link to draft PR
  - Blocking status

- **Always**: Commit graph SVG/Mermaid showing:
  - Timeline of syncs
  - Branch divergence/convergence
  - Author attribution
  - SHA hashes for traceability

---

## Sync Strategies

### 1. Copy File (`copy-file`)

**Use case**: Keep a single config file identical across repos.

```yaml
strategy: copy-file
source:
  repo: org/infra-main
  path: config/production.yaml
  ref: main
target:
  repo: org/infra-staging
  path: config/production.yaml
  ref: main
conflict_strategy: auto-merge
```

**Flow**:
1. Fetch `source` file from GitHub
2. Compare with `target` file (hash check)
3. If identical: No change needed
4. If different:
   - Create branch `gitops/sync-production-config-{timestamp}`
   - Copy file contents
   - Commit: `chore: sync production.yaml from infra-main`
   - Create PR with auto-merge enabled

**Outputs**:
```json
{
  "sync_type": "copy-file",
  "source_file": "config/production.yaml",
  "source_sha": "a1b2c3d4",
  "target_sha": "x9y8z7w6",
  "status": "synced",
  "pr_number": 42,
  "pr_url": "https://github.com/org/infra-staging/pull/42",
  "commit_sha": "abc123def456",
  "timestamp": "2026-07-26T10:30:00Z"
}
```

---

### 2. Merge Branch (`merge-branch`)

**Use case**: Sync a feature branch or release branch across repos.

```yaml
strategy: merge-branch
source:
  repo: org/monorepo
  branch: release/v2.1.0
target:
  repo: org/deployed-config
  branch: main
conflict_strategy: manual-review
```

**Flow**:
1. Fetch source branch HEAD commit
2. Attempt `git merge --ff-only` simulation
3. If fast-forward possible:
   - Create branch `gitops/merge-release-v2.1.0`
   - Replay commits on top of target
   - Create PR with auto-merge
4. If conflicts:
   - Create draft PR with conflict markers
   - Open GitHub issue with conflict blocks
   - Await manual resolution

**Outputs**:
```json
{
  "sync_type": "merge-branch",
  "source_branch": "release/v2.1.0",
  "source_commits": 12,
  "source_commits_list": [
    { "sha": "abc123", "author": "alice@org.com", "message": "fix: deployment issue" }
  ],
  "target_branch": "main",
  "merge_type": "fast-forward",
  "status": "synced",
  "pr_number": 43,
  "conflict_count": 0,
  "timestamp": "2026-07-26T10:30:00Z"
}
```

---

### 3. Rebase Strategies (`rebase`, `rebase-onto-main`, `squash-fixups`)

**Use case**: Linearize history by rebasing target commits on top of source. Phase 2 adds two rebase variants for production workflows.

#### 3a. Standard Rebase (`rebase`)

```yaml
strategy: rebase
source:
  repo: org/canonical
  branch: main
target:
  repo: org/fork
  branch: feature/custom-overlay
conflict_strategy: auto-merge
```

**Flow**:
1. Fetch both branch HEADs
2. Find common ancestor (merge base)
3. Simulate `git rebase source/main` on target commits
4. If no conflicts:
   - Create branch `gitops/rebase-feature-custom-overlay-onto-main`
   - Replay target commits linearly
   - Create PR
5. If conflicts:
   - Report conflict hunk count
   - Create issue with suggested conflict resolution
   - Mark as **manual review required**

#### 3b. Rebase-onto-Main (`rebase-onto-main`) — NEW Phase 2

Clean up feature branches before merging to main: rebase all commits, then merge to main via fast-forward.

```yaml
strategy: rebase-onto-main
target:
  repo: org/project
  branch: feature/my-feature
main_branch: main
cleanup: true  # squash fixup commits
conflict_strategy: auto-merge
```

**Flow**:
1. Fetch feature branch and main
2. Find merge base between feature and main
3. Apply all feature commits on top of latest main
4. Optionally squash fixup commits (see 3c)
5. If no conflicts:
   - Create branch `gitops/rebase-feature-my-feature-onto-main-{timestamp}`
   - Merge back to main via fast-forward-only
   - Close feature branch
6. If conflicts: escalate to manual review

**Output**:
```json
{
  "sync_type": "rebase-onto-main",
  "feature_branch": "feature/my-feature",
  "main_branch": "main",
  "commits_rebased": 7,
  "commits_squashed": 2,
  "rebase_conflicts": 0,
  "merged_to_main": true,
  "status": "synced",
  "pr_number": 46,
  "merged_pr_number": 47,
  "timestamp": "2026-07-26T10:30:00Z"
}
```

#### 3c. Squash Fixups (`squash-fixups`) — NEW Phase 2

Combine "fixup" and "squash" commits before rebasing.

```yaml
strategy: squash-fixups
target:
  repo: org/project
  branch: feature/complex-work
main_branch: main
fixup_pattern: "fixup!|squash!|wip:"  # regex to match commit messages
result: "single-commit-per-feature"  # or "preserve-logical-commits"
conflict_strategy: auto-merge
```

**Algorithm**:
1. Fetch all commits on feature branch
2. Identify "fixup" commits: messages matching `fixup_pattern`
3. Combine fixup commits with their target commits:
   - `fixup! <target-msg>` → squash into the commit with message `<target-msg>`
   - `squash! <target-msg>` → squash with interaction prompts
   - Orphaned squashes → combine with previous commit
4. Resulting commits should be logically cohesive
5. Rebase onto main
6. Create PR with cleaned-up history

**Example**:
```
Before squash-fixups:
  abc1234 feat: add new endpoint
  def5678 wip: add error handling
  ghi9012 fixup! feat: add new endpoint
  jkl3456 tests: cover edge case

After squash-fixups:
  abc1234' feat: add new endpoint (with error handling + fixup)
  jkl3456' tests: cover edge case
```

**Output**:
```json
{
  "sync_type": "squash-fixups",
  "feature_branch": "feature/complex-work",
  "original_commits": 4,
  "fixup_commits_found": 1,
  "wip_commits_found": 1,
  "final_commit_count": 2,
  "rebase_conflicts": 0,
  "status": "synced",
  "pr_number": 48,
  "timestamp": "2026-07-26T10:30:00Z"
}
```

---

### 4. Three-way Merge with LCS Algorithm (`three-way-merge`)

**Use case**: Intelligently merge when source and target both have changes. Phase 2 adds full LCS (Longest Common Subsequence) algorithm for smarter conflict detection.

```yaml
strategy: three-way-merge
source:
  repo: org/upstream
  ref: main
target:
  repo: org/downstream
  ref: main
common_ancestor: auto-detect
conflict_strategy: auto-merge  # or manual-review
lcs_algorithm:
  enabled: true
  similarity_threshold: 0.75  # if LCS similarity > 75%, auto-merge even with minor changes
  context_lines: 3  # show ±3 lines around diffs
```

#### LCS Algorithm Details (Phase 2)

The three-way merge applies the **Longest Common Subsequence** algorithm to intelligently detect true conflicts:

1. **Fetch three versions**:
   - Ancestor (common base)
   - Source (upstream changes)
   - Target (downstream changes)

2. **Line-by-line diff computation** (for each file):
   ```
   diff_source = lines_of(ancestor) vs lines_of(source)
   diff_target = lines_of(ancestor) vs lines_of(target)
   ```

3. **Compute LCS** (on the full line sequence):
   ```
   lcs_source_target = LCS(lines_of(source), lines_of(target))
   lcs_similarity = len(lcs_source_target) / max(len(source), len(target))
   ```

4. **Classification** (for each differing region):
   - **Auto-merge** (no conflict):
     - Changes in different regions (source changes lines 10–15, target changes lines 30–35)
     - Both sides add the exact same line (idempotent add)
     - LCS similarity ≥ 75% (minor variations on same concept)
   
   - **Conflict** (requires human):
     - Overlapping changes (both modify lines 20–25 differently)
     - Incompatible semantic changes (e.g., `version: 1.0` vs `version: 2.0`)
     - File structure changes (one side adds blocks, other side removes them)
     - LCS similarity < 75% (diverged substantially)

5. **Resolution strategy**:
   - Return merged content for auto-merge regions
   - For conflicts: suggest LCS-based merge (preserves maximal common structure)
   - If LCS suggestion creates invalid syntax, escalate to manual review

6. **Output** (enriched in Phase 2):
   ```json
   {
     "sync_type": "three-way-merge",
     "common_ancestor": "ancestor123",
     "source_ref": "org/upstream:main",
     "target_ref": "org/downstream:main",
     "files_changed": 8,
     "files_auto_merged": 6,
     "files_with_conflicts": 2,
     "files_with_escalation": 1,
     "conflicts": [
       {
         "file": "src/config.yaml",
         "line_range": [10, 25],
         "conflict_type": "content-divergence",
         "source_content": "key: value-from-upstream",
         "target_content": "key: value-from-downstream",
         "lcs_similarity": 0.68,
         "lcs_suggestion": "key: value-from-upstream",
         "escalation_reason": "semantic conflict: different values for same key",
         "requires_human_approval": true
       },
       {
         "file": "terraform/main.tf",
         "line_range": [45, 60],
         "conflict_type": "location-divergence",
         "source_content": "resource \"aws_s3_bucket\" \"data\" { ... }",
         "target_content": "resource \"aws_s3_bucket\" \"data\" { acl = \"private\" ... }",
         "lcs_similarity": 0.82,
         "lcs_suggestion": "resource \"aws_s3_bucket\" \"data\" { acl = \"private\" ... }",
         "escalation_reason": "high-risk file (*.tf) requires approval",
         "requires_human_approval": true
       }
     ],
     "status": "partial-conflict",
     "auto_merged_count": 6,
     "manual_review_count": 2,
     "issue_number": 45,
     "issue_url": "https://github.com/org/downstream/issues/45",
     "timestamp": "2026-07-26T10:30:00Z"
   }
   ```

---

## Scheduled Syncs via GitHub Actions — NEW Phase 2

Automate recurring GitOps syncs using GitHub Actions workflows with cron scheduling and event-driven triggers.

### Cron-based Scheduling

Run syncs on a fixed schedule (e.g., daily, weekly):

```yaml
# .github/workflows/gitops-scheduled-sync.yml

name: GitOps Scheduled Sync

on:
  schedule:
    # Daily at 10 AM UTC: sync staging → prod
    - cron: '0 10 * * *'
    # Weekly Friday at 6 PM UTC: sync main → all deployment repos
    - cron: '0 18 * * 5'

jobs:
  sync-canonical-to-staging:
    runs-on: ubuntu-latest
    steps:
      - name: Run GitOps Sync
        uses: anthropics/claude-gitops@v2
        with:
          skill: git-gitops-flow
          source_repo: org/canonical-infra
          source_branch: main
          target_repos: |
            org/staging-infra#main
            org/staging-config#main
          sync_type: copy-file
          file_patterns: |
            terraform/**/*.tf
            config/*.yaml
          conflict_strategy: auto-merge
          auto_merge_enabled: true
          
      - name: Report to Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "GitOps Sync Complete",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "Scheduled sync: ${{ job.status }}\n*PRs created*: ${{ steps.sync.outputs.pr_count }}\n*Auto-merged*: ${{ steps.sync.outputs.auto_merged_count }}"
                  }
                }
              ]
            }
```

### Event-driven Scheduling

Trigger syncs on repository events:

```yaml
name: GitOps Event-Driven Sync

on:
  push:
    branches: [main, release/*]
    paths:
      - 'terraform/**'
      - 'config/**'
      
  pull_request:
    types: [closed]
    branches: [main]

jobs:
  sync-on-merge:
    if: github.event_name == 'pull_request' && github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Sync merged config to all repos
        uses: anthropics/claude-gitops@v2
        with:
          skill: git-gitops-flow
          source_repo: ${{ github.repository }}
          source_branch: main
          target_repos: |
            org/staging#main
            org/prod-us#main
            org/prod-eu#main
            org/prod-asia#main
            org/dr#main
          sync_type: merge-branch
          conflict_strategy: manual-review
          max_retries: 3
          retry_backoff: exponential
```

### Retry Logic & Error Handling

```yaml
sync-with-retries:
  runs-on: ubuntu-latest
  steps:
    - name: GitOps Sync with Retries
      uses: anthropics/claude-gitops@v2
      with:
        # ... sync config ...
        max_retries: 3
        retry_delay_seconds: 300  # wait 5 min before retry
        retry_backoff: exponential  # 5m, 10m, 20m
        on_retry_failure: escalate  # escalate to manual review
        
    - name: Create escalation issue on failure
      if: failure()
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: `[GitOps] Scheduled sync failed: ${context.run_id}`,
            labels: ['gitops', 'escalation']
          })
```

---

## Transactional Rollback — NEW Phase 2

**Atomic rollback**: If a merge fails or causes issues, revert all downstream syncs in reverse order.

### Rollback Trigger Conditions

Rollback is triggered when:
1. Merge to main fails (non-fast-forward, conflicts)
2. Post-merge check run fails (tests, linting, security)
3. Manual rollback request via `@gitops-bot rollback pr-{number}`
4. Automated rollback on high-severity issues detected in audit log

### Rollback Strategy

```yaml
gitops:
  transactional:
    enabled: true
    rollback_on_failure: true
    failure_conditions:
      - test_check_failed
      - merge_conflict
      - security_vulnerability
      - manual_request
    
    rollback_order: reverse  # revert in reverse order of sync chain
    revert_commit_message: |
      revert: GitOps rollback #{pr_number}
      
      Reason: {reason}
      Rollback chain: {chain_ids}
    
    notify_channels:
      - "#incident-response"
      - "#devops-team"
```

### Rollback Chain Tracking

Each sync is linked to its downstream syncs via `rollback_chain`:

```json
{
  "gitops_operation": {
    "op_id": "gitops-001",
    "sync_chain": [
      {
        "repo": "org/canonical#main",
        "pr_number": 100,
        "status": "merged",
        "merged_at": "2026-07-26T10:00:00Z"
      },
      {
        "repo": "org/staging#main",
        "pr_number": 101,
        "status": "merged",
        "merged_at": "2026-07-26T10:05:00Z"
      },
      {
        "repo": "org/prod-us#main",
        "pr_number": 102,
        "status": "merged",
        "merged_at": "2026-07-26T10:10:00Z"
      },
      {
        "repo": "org/prod-eu#main",
        "pr_number": 103,
        "status": "merged",
        "merged_at": "2026-07-26T10:15:00Z"
      }
    ]
  }
}
```

### Rollback Execution

```
Rollback triggered for pr-102 (prod-us merge failure)
  │
  ├─ Step 1: Revert pr-103 (prod-eu)
  │   └─ New revert PR: pr-103-revert, auto-merge
  │   └─ Audit: {op_id: gitops-001, rollback_step: 1, reverted_pr: 103}
  │
  ├─ Step 2: Revert pr-102 (prod-us)
  │   └─ New revert PR: pr-102-revert, auto-merge
  │   └─ Audit: {op_id: gitops-001, rollback_step: 2, reverted_pr: 102}
  │
  ├─ Step 3: Revert pr-101 (staging)
  │   └─ New revert PR: pr-101-revert, auto-merge
  │   └─ Audit: {op_id: gitops-001, rollback_step: 3, reverted_pr: 101}
  │
  └─ Rollback complete
      └─ Notify: "#incident-response: GitOps rollback complete. 3 PRs reverted."
      └─ Audit entry: {rollback_status: "success", reverted_prs: [103, 102, 101]}
```

---

## Escalation Rules — NEW Phase 2

**Smart escalation**: Detect high-risk files and require human approval before merge.

### High-Risk File Patterns (Require Approval)

```yaml
gitops:
  escalation:
    enabled: true
    auto_merge_requires_approval_for:
      dependency_files:
        - "package*.json"
        - "yarn.lock"
        - "Gemfile"
        - "Gemfile.lock"
        - "requirements*.txt"
        - "pyproject.toml"
        - "go.mod"
        - "Cargo.toml"
      
      infrastructure:
        - "Dockerfile*"
        - "docker-compose*.yml"
        - "*.tf"
        - "*.tfvars"
        - "k8s/**/*.yaml"
        - "helm/**/*.yaml"
        - ".github/workflows/*.yml"
      
      secrets:
        - ".env*"
        - "*secret*"
        - "*credential*"
        - "*key*"
        - "*.pem"
        - "*.key"
      
      critical_config:
        - "config/production.*"
        - "config/secrets.*"
        - "SECURITY.md"
        - "LICENSE*"
      
      custom_patterns: []  # user-defined patterns
```

### Escalation Flow

When high-risk files are detected:

```
PR created with high-risk files
  │
  ├─ Check 1: Is auto-merge enabled?
  │   ├─ No → Allow merge (respects user's choice)
  │   └─ Yes ↓
  │
  ├─ Check 2: High-risk files detected?
  │   ├─ No → Proceed to auto-merge
  │   └─ Yes → HOLD & ESCALATE ↓
  │
  ├─ Add label: "requires-human-approval"
  ├─ Add comment: "Escalation: {file_list} requires review"
  ├─ Request review from: @team-devops, @team-security
  ├─ Set auto-merge: false (block until approved)
  │
  └─ When approval given:
      ├─ Set auto-merge: true
      └─ Proceed to auto-merge (if other 4 conditions still pass)
```

### Escalation Configuration

```yaml
gitops:
  escalation:
    approvers:
      dependency_files:
        - "org/team-devops"
        - "org/team-security"
      infrastructure:
        - "org/team-infra"
      secrets:
        - "org/team-security"
    
    approval_required_count: 1  # require N approvals
    timeout_hours: 24  # escalation auto-closes if not approved
    block_on_escalation: true  # don't auto-merge until approved
```

---

## Conflict Resolution Strategies

### `auto-merge`

Automatically resolve if:
- No overlapping changes (changes in different files/lines)
- Both sides add the same line (idempotent)
- Source is strict ancestor of target (fast-forward)

If conflicts remain:
- Fall back to `manual-review`
- Create issue with conflict blocks

### `manual-review`

Always create issue for human review:
- List conflicted files
- Show conflict hunks with context
- Provide suggested resolutions (LCS merge)
- Link to draft PR

### `ours` / `theirs`

Deterministic resolution:
- `ours`: Keep all target changes, discard source
- `theirs`: Accept all source changes, discard target
- Use with caution — data loss possible

---

## Commit Graph

### Output Format

**SVG (Mermaid GitGraph)**:
```mermaid
gitGraph
  commit id: "Initial commit"
  branch gitops/sync-main-to-staging
  commit id: "copy: config.yaml"
  checkout main
  merge gitops/sync-main-to-staging
  commit id: "Merged GitOps sync #42"
  branch release/v2.1.0
  commit id: "chore: bump version"
  commit id: "fix: deployment script"
  checkout main
  merge release/v2.1.0
  commit id: "Merged release v2.1.0 #43"
```

### Metadata

```json
{
  "commit_graph": {
    "total_commits": 25,
    "sync_operations": [
      {
        "op_id": "gitops-001",
        "timestamp": "2026-07-26T10:30:00Z",
        "source_repo": "org/infra-main",
        "target_repo": "org/infra-staging",
        "strategy": "copy-file",
        "commit_sha": "abc123def456",
        "author": "gitops-bot@org.com",
        "message": "chore: sync production.yaml from infra-main",
        "pr_number": 42,
        "status": "merged"
      }
    ],
    "divergence_timeline": [
      { "date": "2026-07-20", "source_ahead": 2, "target_ahead": 0 },
      { "date": "2026-07-21", "source_ahead": 2, "target_ahead": 1 },
      { "date": "2026-07-26", "source_ahead": 0, "target_ahead": 0 }
    ]
  }
}
```

---

## Inputs & Configuration

### Minimal Configuration (Phase 1 Compatible)

```yaml
gitops:
  source:
    repo: owner/source-repo
    branch: main
    ref: null  # latest commit on branch
  target:
    repo: owner/target-repo
    branch: main
  sync_type: copy-file | merge-branch | rebase | three-way-merge | detect-drift
  file_patterns: ["config/*.yaml", "terraform/**/*.tf"]  # optional; if omitted, all files
  conflict_strategy: auto-merge | manual-review | ours | theirs
  auto_merge_pr: true | false
  labels: ["gitops", "auto-sync"]
```

### Phase 2 Full Configuration

```yaml
gitops:
  # Basic sync config
  name: "My GitOps Sync"
  source:
    repo: owner/source-repo
    branch: main
    ref: null
    path: "config/**"  # Optional: sync only this path
  
  # Target: single or multiple repos
  target:
    repo: owner/target-repo  # Single repo (Phase 1 style)
    branch: main
  
  # OR targets array (Phase 2 multi-repo)
  targets:
    - repo: owner/target-repo-1
      branch: main
    - repo: owner/target-repo-2
      branch: staging
    - repo: owner/target-repo-3
      branch: prod
    # ... up to N repos
  
  # Sync strategy
  sync_type: copy-file | merge-branch | rebase | rebase-onto-main | squash-fixups | three-way-merge | detect-drift
  
  # File filtering
  file_patterns: ["config/*.yaml", "terraform/**/*.tf"]
  ignore_patterns: [".git/**", "*.tmp", ".env"]
  preserve_history: false  # merge vs rebase
  
  # Conflict handling
  conflict_strategy: auto-merge | manual-review | ours | theirs
  lcs_algorithm:
    enabled: true
    similarity_threshold: 0.75
    context_lines: 3
  
  # ===== PHASE 2: Auto-Merge Gates =====
  auto_merge:
    enabled: true
    condition_checks:
      tests_required: true
      allow_ignored_checks: ["optional-e2e", "performance"]
      security_scan_required: true
      max_critical_issues: 0
      max_high_issues: 0
    risk_patterns:
      high_risk_files:
        - "package*.json"
        - "Dockerfile*"
        - "*.tf"
        - ".env*"
        - "*secret*"
      max_files_changed: 20
      max_lines_changed: 500
    max_target_repos: 5
    audit_table: "gitops_audit"
    audit_required: true
  
  # ===== PHASE 2: Escalation Rules =====
  escalation:
    enabled: true
    auto_merge_requires_approval_for:
      dependency_files:
        - "package*.json"
        - "yarn.lock"
        - "Gemfile"
        - "requirements*.txt"
      infrastructure:
        - "Dockerfile*"
        - "*.tf"
        - "k8s/**/*.yaml"
        - ".github/workflows/*.yml"
      secrets:
        - ".env*"
        - "*secret*"
    approvers:
      dependency_files: ["@team-devops"]
      infrastructure: ["@team-infra"]
      secrets: ["@team-security"]
    approval_required_count: 1
    timeout_hours: 24
    block_on_escalation: true
  
  # ===== PHASE 2: Scheduled Syncs =====
  scheduled:
    enabled: true
    cron: "0 10 * * *"  # Daily 10 AM UTC
    event_triggers:
      - event: push
        branches: [main, release/*]
      - event: pull_request
        types: [closed]  # trigger on PR merge
    retry_on_failure: true
    max_retries: 3
    retry_delay_seconds: 300
    retry_backoff: exponential  # or linear
  
  # ===== PHASE 2: Transactional Rollback =====
  transactional:
    enabled: true
    rollback_on_failure: true
    failure_conditions:
      - test_check_failed
      - merge_conflict
      - security_vulnerability
    rollback_order: reverse  # reverse order of sync chain
    revert_commit_message: "revert: GitOps rollback {pr_number}"
  
  # Commit customization
  commit_prefix: "gitops: "
  author_email: "gitops@org.com"
  author_name: "GitOps Bot"
  
  # PR customization
  pr_title: "GitOps: Sync {source}#{source_branch} → {target}#{target_branch}"
  pr_description: |
    Automated GitOps sync operation.
    Strategy: {sync_type}
    Conflicts: {conflict_count}
    Review: {review_url}
  
  # Notifications
  notify_on_conflict: true
  notify_on_auto_merge: true
  assignees: ["devops-team"]
  reviewers: ["devops-lead"]
  notify_channels:
    slack: "#deployments"
    teams: "@devops"
    github: "comment-on-pr"
  
  # Audit & logging
  audit_enabled: true
  audit_table: "gitops_audit"
  dry_run: false
```

---

## MCP Tools Used

| Tool | Purpose | Phase | Called by |
|---|---|---|---|
| `create_branch` | Create sync branch in target repo | 1, 2, 3 | PR creation flow |
| `create_pull_request` | Create sync PR with description | 1, 2, 3 | Auto-merge flow |
| `merge_pull_request` | Merge PR (auto-merge) | 2, 3 | Phase 2/3 auto-merge decision |
| `update_pull_request_branch` | Sync PR branch to main (rebase) | 2, 3 | Rebase strategy |
| `list_commits` | Get commit details (author, message, SHA) | 1, 2, 3 | Commit graph generation + ML input |
| `search_code` | Find files matching patterns | 1, 2, 3 | File drift detection |
| `get_file_contents` | Fetch file for diff | 1, 2, 3 | Diff computation |
| `list_branches` | Enumerate available branches | 1, 2, 3 | Validation |
| `git-auto-merge-confidence` | **NEW v3.0**: ML inference for merge safety | 3 | Confidence scoring gate |
| Supabase (INSERT/SELECT) | Audit logging (gitops_audit, gitops_ml_scores) | 2, 3 | Pre-merge audit + ML audit trail |
| GitHub Actions (workflow_dispatch) | Trigger scheduled syncs | 2, 3 | Cron + event-driven scheduling |
| Slack API | Notifications (optional) | 2, 3 | Sync status + escalation alerts + ML recommendations |

---

## Error Handling

### Drift Detected (No Auto-Sync)

**Scenario**: `detect-drift` returns differences but no sync is requested.

```json
{
  "operation": "detect-drift",
  "status": "drift_detected",
  "drift_count": 3,
  "files_different": [
    "config/app.yaml",
    "terraform/main.tf",
    "scripts/deploy.sh"
  ],
  "message": "Run with sync_type='copy-file' or 'merge-branch' to synchronize."
}
```

### Merge Conflict (Unresolvable)

**Scenario**: Three-way merge detects conflicting changes.

```json
{
  "operation": "merge",
  "status": "conflict",
  "conflict_count": 2,
  "issue_url": "https://github.com/owner/target-repo/issues/45",
  "message": "Manual review required. See issue #45 for conflict details."
}
```

### Branch Not Found

**Scenario**: Source or target branch does not exist.

```json
{
  "operation": "merge-branch",
  "status": "error",
  "error_code": "BRANCH_NOT_FOUND",
  "missing_branch": "release/v2.1.0",
  "repo": "owner/target-repo"
}
```

### Permission Denied

**Scenario**: GitHub token lacks write permission to target repo.

```json
{
  "operation": "create-pr",
  "status": "error",
  "error_code": "PERMISSION_DENIED",
  "message": "Token does not have push access to owner/target-repo. Ensure GitHub App is installed and has 'contents:write' permission."
}
```

---

## Phase 2 Examples

### Example 1: Config Sync Across 5 Repos — NEW Phase 2

Sync Terraform configs from canonical infra repo to 5 deployment regions (US, EU, Asia, APAC, DR) daily, with auto-merge if all safety conditions pass.

**Configuration**:
```yaml
# .claude/gitops/config-sync-5-regions.yaml

gitops:
  name: "Daily Config Sync — 5 Regions"
  enabled: true
  
  source:
    repo: org/canonical-infra
    branch: main
    path: "terraform/modules/**/*.tf"
  
  targets:
    - repo: org/deployed-infra-us
      branch: main
      region: us-east
    - repo: org/deployed-infra-eu
      branch: main
      region: eu-west
    - repo: org/deployed-infra-asia
      branch: main
      region: ap-southeast
    - repo: org/deployed-infra-apac
      branch: main
      region: ap-northeast
    - repo: org/deployed-infra-dr
      branch: main
      region: us-west-dr
  
  sync_type: copy-file
  conflict_strategy: auto-merge
  
  auto_merge:
    enabled: true
    condition_checks:
      tests_required: true
      security_scan_required: true
      max_critical_issues: 0
    risk_patterns:
      high_risk_files:
        - "Dockerfile*"
        - "*.pem"
      max_files_changed: 15
    max_target_repos: 5
  
  scheduled:
    enabled: true
    cron: "0 10 * * *"  # Daily 10 AM UTC
    retry_on_failure: true
    max_retries: 3
    retry_delay: 300  # 5 minutes
  
  notifications:
    slack: "#deployments"
    teams: "@devops-team"
```

**Execution Flow**:
```
Day 1: 10:00 UTC
  ├─ Detect changes in canonical-infra/terraform
  ├─ Create PR for each of 5 repos
  ├─ Check 1: Tests Green? ✅
  ├─ Check 2: Zero CRITICAL? ✅
  ├─ Check 3: Low-Risk Pattern? ✅
  ├─ Check 4: ≤ 5 repos? ✅ (exactly 5)
  ├─ Check 5: Audit logged? ✅
  │
  └─ AUTO-MERGE all 5 PRs
      ├─ PR #500 merged: us-east
      ├─ PR #501 merged: eu-west
      ├─ PR #502 merged: ap-southeast
      ├─ PR #503 merged: ap-northeast
      └─ PR #504 merged: us-west-dr
      
      Audit log entry:
        {
          "op_id": "gitops-sync-daily-20260726",
          "source_repo": "org/canonical-infra",
          "target_repos": ["us", "eu", "asia", "apac", "dr"],
          "prs_created": 5,
          "prs_auto_merged": 5,
          "conditions_passed": [true, true, true, true, true],
          "risk_level": "low",
          "timestamp": "2026-07-26T10:00:00Z",
          "status": "success"
        }

Day 2: Conflict Scenario
  ├─ Canonical made changes to version.tf
  ├─ EU region manually updated version.tf (conflict!)
  ├─ Create PR for each of 5 repos
  ├─ LCS analysis:
  │   ├─ us-east: auto-merge ✅
  │   ├─ eu-west: CONFLICT detected
  │   │   └─ LCS similarity: 0.65 (< 75% threshold)
  │   │   └─ Escalate: requires human approval
  │   ├─ asia: auto-merge ✅
  │   ├─ apac: auto-merge ✅
  │   └─ dr: auto-merge ✅
  │
  ├─ Auto-merge 4 out of 5 PRs
  ├─ Hold PR #510 (eu-west) for manual review
  ├─ Create issue: "GitOps: Conflict in config sync #510"
  ├─ Request review: @team-eu-infrastructure
  │
  └─ When approved:
      ├─ Human resolves conflict
      ├─ PR #510 merged
      └─ Audit updated with manual intervention timestamp
```

**Output**:
```json
{
  "sync_batch_id": "gitops-sync-daily-20260727",
  "timestamp": "2026-07-27T10:00:00Z",
  "syncs": [
    {
      "target_repo": "org/deployed-infra-us",
      "pr_number": 505,
      "status": "auto-merged",
      "auto_merge_eligible": true
    },
    {
      "target_repo": "org/deployed-infra-eu",
      "pr_number": 506,
      "status": "conflicted",
      "auto_merge_eligible": false,
      "conflict_count": 1,
      "escalation_reason": "LCS similarity below threshold + high-risk file (*.tf)",
      "requires_human_approval": true
    },
    {
      "target_repo": "org/deployed-infra-asia",
      "pr_number": 507,
      "status": "auto-merged",
      "auto_merge_eligible": true
    },
    {
      "target_repo": "org/deployed-infra-apac",
      "pr_number": 508,
      "status": "auto-merged",
      "auto_merge_eligible": true
    },
    {
      "target_repo": "org/deployed-infra-dr",
      "pr_number": 509,
      "status": "auto-merged",
      "auto_merge_eligible": true
    }
  ],
  "summary": {
    "total_prs": 5,
    "auto_merged": 4,
    "manual_review": 1,
    "success_rate": 0.8,
    "risk_level": "low-with-escalation"
  }
}
```

---

### Example 2: Feature Rollout with Conflict Resolution — NEW Phase 2

Roll out a feature branch (v2.5.0) to 5 deployment repos with intelligent conflict handling.

**Configuration**:
```yaml
gitops:
  name: "Feature Rollout v2.5.0"
  sync_type: three-way-merge
  
  source:
    repo: org/monorepo
    branch: release/v2.5.0
    
  targets:
    - repo: org/staging-v2
    - repo: org/prod-us
    - repo: org/prod-eu
    - repo: org/prod-asia
    - repo: org/prod-canary
  
  conflict_strategy: auto-merge
  lcs_algorithm:
    enabled: true
    similarity_threshold: 0.75
  
  escalation:
    enabled: true
    approvers:
      infrastructure: ["@team-infra"]
      dependency_files: ["@team-devops"]
    
  transactional:
    enabled: true
    rollback_on_failure: true
```

**Execution Flow with Conflicts**:
```
Phase 1: Pre-flight Check
  ├─ Fetch release/v2.5.0 commits (15 commits)
  ├─ Check target repos for drift
  ├─ Compute LCS similarity for each target vs release branch
  └─ Result: staging-v2 (100%), prod-us (95%), prod-eu (72%), prod-asia (98%), prod-canary (100%)

Phase 2: Three-way Merge for Each Target
  
  Target 1: staging-v2 (LCS: 100%)
    ├─ No divergence from canonical → Fast-forward merge
    ├─ Create PR #600
    ├─ All auto-merge conditions pass ✅
    └─ Auto-merge: SUCCESS
  
  Target 2: prod-us (LCS: 95%)
    ├─ Minimal divergence (1 custom tweak to config.yaml)
    ├─ Three-way merge finds one overlapping change:
    │   - Release changes: line 30–35 in config.yaml
    │   - Prod-us changed: line 31–32 in config.yaml
    │   - LCS analysis: both adding logging config
    ├─ Merge strategy: Accept release version (prod-us change is subset)
    ├─ Create PR #601
    ├─ All conditions pass ✅
    └─ Auto-merge: SUCCESS
  
  Target 3: prod-eu (LCS: 72%) ⚠️
    ├─ Significant divergence detected (28% different)
    ├─ Terraform files modified by both sides:
    │   - Release: aws_security_group rules updated
    │   - Prod-eu: local security_group overrides
    ├─ Three-way merge:
    │   - Find common ancestor
    │   - Detect overlapping changes in terraform/security.tf (lines 45–70)
    │   - LCS similarity of conflict: 0.55 (< 75% threshold)
    │   - Escalation triggered: high-risk file + complex conflict
    ├─ Create PR #602
    ├─ Status: CONFLICT (requires human approval)
    ├─ Add labels: "high-risk-files", "requires-human-approval"
    ├─ Request review: @team-eu-infrastructure, @team-security
    └─ Hold PR until approved
  
  Target 4: prod-asia (LCS: 98%)
    ├─ Minimal changes by prod-asia (minor version bump in one file)
    ├─ Release changes compatible
    ├─ Create PR #603
    ├─ All conditions pass ✅
    └─ Auto-merge: SUCCESS
  
  Target 5: prod-canary (LCS: 100%)
    ├─ Canary repo synced to latest (as expected)
    ├─ Fast-forward merge
    ├─ Create PR #604
    ├─ All conditions pass ✅
    └─ Auto-merge: SUCCESS

Phase 3: Rollback Chain Setup
  ├─ Sync chain recorded:
  │   1. staging-v2 (merged)
  │   2. prod-us (merged)
  │   3. prod-eu (waiting)
  │   4. prod-asia (merged)
  │   5. prod-canary (merged)
  │
  └─ If prod-eu approval is rejected/times out:
      ├─ Revert prod-canary (PR #604)
      ├─ Revert prod-asia (PR #603)
      ├─ Keep prod-us (separately merged)
      ├─ Keep staging-v2 (separately merged)
      └─ Auto-rollback complete
```

**Conflict Resolution (Manual)**:
```
PR #602 Conflict Details:
  File: terraform/security.tf
  Lines: 45–70
  
  Conflict block:
    <<<<<<< release/v2.5.0
    resource "aws_security_group" "api" {
      ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      }
    }
    =======
    resource "aws_security_group" "api" {
      ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["10.0.0.0/8"]  # Prod-EU custom restriction
      }
    }
    >>>>>>> prod-eu
  
  LCS-suggested merge:
    resource "aws_security_group" "api" {
      ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["10.0.0.0/8"]  # Keep prod-eu's more restrictive rule
      }
      # TODO: Ensure release/v2.5.0 requirements are met with this CIDR
    }
  
  Approval comment from @team-eu-infrastructure:
    "Approved with prod-eu's CIDR block. We'll coordinate with central team to update release notes."

After approval:
  ├─ Manual conflict resolution applied
  ├─ PR #602 merged
  ├─ Audit updated: {manual_intervention: true, resolved_by: "alice@org.com"}
  └─ Rollback chain committed (all 5 targets now merged)
```

**Final Audit Log**:
```json
{
  "rollout_id": "feature-rollout-v2.5.0-20260728",
  "source_branch": "release/v2.5.0",
  "start_time": "2026-07-28T14:00:00Z",
  "end_time": "2026-07-28T14:30:00Z",
  "targets": [
    {
      "repo": "staging-v2",
      "pr": 600,
      "status": "auto-merged",
      "merge_time": "2026-07-28T14:05:00Z",
      "risk_level": "low"
    },
    {
      "repo": "prod-us",
      "pr": 601,
      "status": "auto-merged",
      "merge_time": "2026-07-28T14:10:00Z",
      "risk_level": "low"
    },
    {
      "repo": "prod-eu",
      "pr": 602,
      "status": "merged-with-manual-resolution",
      "merge_time": "2026-07-28T14:28:00Z",
      "conflict_resolution_time_minutes": 23,
      "resolved_by": "alice@org.com",
      "risk_level": "high"
    },
    {
      "repo": "prod-asia",
      "pr": 603,
      "status": "auto-merged",
      "merge_time": "2026-07-28T14:12:00Z",
      "risk_level": "low"
    },
    {
      "repo": "prod-canary",
      "pr": 604,
      "status": "auto-merged",
      "merge_time": "2026-07-28T14:08:00Z",
      "risk_level": "low"
    }
  ],
  "summary": {
    "total_prs": 5,
    "auto_merged": 4,
    "manual_merged": 1,
    "rollbacks": 0,
    "total_duration_minutes": 30,
    "escalations": 1
  }
}
```

---

## Phase 3 Examples — ML Confidence Scoring

### Example 3: ML-Scored Config Sync with Escalation — NEW Phase 3

Same 5-region sync as Example 1, but with ML confidence scoring determining merge behavior.

**Scenario**: Daily config sync to 5 regions. ML confidence varies due to test delays and infrastructure file changes.

**Execution Flow with ML Scoring**:

```
Day 1: Standard Case (All Regions Confident)
  10:00 UTC: Sync triggered
  ├─ Create PR for each of 5 regions
  │
  ├─ Region: us-east
  │   ├─ Call: git-auto-merge-confidence
  │   ├─ Input:
  │   │   - Tests: 10/10 passing ✅
  │   │   - Security: 0 CRITICAL ✅
  │   │   - Files: 5 config files (low-risk) ✅
  │   │   - Repos: 1 target ✅
  │   │   - Deployment history: 100% (12/12 past syncs) ✅
  │   │   - Time: 10:00 AM UTC (business hours) ✅
  │   │
  │   ├─ Output: confidence_score = 0.98
  │   ├─ Recommendation: AUTO_MERGE ✅
  │   ├─ Audit: {region: us-east, pr: 500, ml_confidence: 0.98, recommendation: AUTO_MERGE}
  │   └─ Action: Merge immediately
  │       └─ Comment: "ML Confidence: 98% | Auto-merged"
  │       └─ Slack: "✅ PR #500 (us-east) auto-merged (confidence: 98%)"
  │
  ├─ Region: eu-west
  │   ├─ Call: git-auto-merge-confidence
  │   ├─ Input:
  │   │   - Tests: 8/10 passing (2 pending) ⚠️
  │   │   - Security: 0 CRITICAL ✅
  │   │   - Files: 3 config + 1 terraform file ⚠️
  │   │   - Repos: 1 target ✅
  │   │   - Author: trusted (20 prior merges) ✅
  │   │
  │   ├─ Output: confidence_score = 0.81
  │   ├─ Recommendation: ESCALATE ⚠️
  │   ├─ Feature importance:
  │   │   - test_pass_rate: -0.10 (tests still pending)
  │   │   - file_risk_score: -0.09 (terraform file)
  │   │   - security_clean: +0.20
  │   │   - author_trustworthiness: +0.08
  │   │   - [others]: +0.22
  │   │
  │   ├─ Audit: {region: eu-west, pr: 501, ml_confidence: 0.81, recommendation: ESCALATE}
  │   └─ Action: Hold for approval
  │       ├─ Label: "requires-human-approval"
  │       ├─ Assign: @team-eu-infrastructure
  │       ├─ Comment:
  │       │  ```
  │       │  ML Confidence: 81% (below auto-merge threshold of 95%)
  │       │  
  │       │  Feature Importance:
  │       │  - test_pass_rate: 2 checks still pending (weight: 0.25)
  │       │  - file_risk_score: terraform/main.tf detected (weight: 0.20)
  │       │  - security_clean: No CRITICAL/HIGH (weight: 0.20)
  │       │  - author_trustworthiness: 20 prior successful merges (weight: 0.08)
  │       │  
  │       │  Recommendation: Wait for tests to complete, then approve for terraform review.
  │       │  Escalation timeout: 24 hours
  │       │  ```
  │       └─ Slack: "⚠️ PR #501 (eu-west) escalated (confidence: 81%) — needs @team-eu-infrastructure approval"
  │
  ├─ Region: ap-southeast
  │   ├─ Call: git-auto-merge-confidence
  │   ├─ Output: confidence_score = 0.96
  │   ├─ Recommendation: AUTO_MERGE ✅
  │   └─ Action: Merge immediately
  │
  ├─ Region: ap-northeast
  │   ├─ Call: git-auto-merge-confidence
  │   ├─ Output: confidence_score = 0.72 ❌
  │   ├─ Recommendation: REJECT
  │   ├─ Reason: "LCS similarity too low (0.68) due to conflicting config changes in previous sync"
  │   └─ Action: Hold (requires manual conflict resolution)
  │       ├─ Label: "confidence-too-low"
  │       ├─ Comment: "ML Confidence: 72% (below rejection threshold of 75%)"
  │       └─ Audit: {region: ap-northeast, pr: 503, ml_confidence: 0.72, recommendation: REJECT}
  │
  └─ Region: us-west-dr
      ├─ Call: git-auto-merge-confidence
      ├─ ML service TIMEOUT (degraded) ⚠️
      ├─ Fallback: Use hardcoded 5-condition gate
      ├─ Check all 5 conditions:
      │   ├─ Tests green? YES ✅
      │   ├─ Zero CRITICAL? YES ✅
      │   ├─ Low-risk pattern? YES ✅
      │   ├─ ≤5 repos? YES ✅ (only 1)
      │   └─ Audit logged? YES ✅
      ├─ Fallback result: All 5 pass → AUTO_MERGE
      └─ Action: Merge with fallback flag
          ├─ Audit: {region: us-west-dr, pr: 504, fallback_gate_used: true, auto_merged: true}
          └─ Slack: "✅ PR #504 (us-west-dr) auto-merged (ML unavailable, fallback gate used)"

Summary:
  ├─ Total PRs: 5
  ├─ Auto-merged (ML ≥ 0.95): 3
  ├─ Escalated (0.75–0.95): 1
  ├─ Rejected (< 0.75): 1
  ├─ Fallback used: 1
  └─ Confidence distribution: [0.98, 0.81, 0.96, 0.72, fallback]
```

**Escalation Resolution (eu-west)**:

```
Day 1, 14:30 UTC (4.5 hours after sync):
  ├─ Remaining 2 tests complete ✅
  ├─ Team approves terraform changes
  ├─ Comment from @alice:
  │   "Approved. Terraform changes align with EU regional requirements."
  │
  ├─ Manual merge triggered
  ├─ Audit updated:
  │   {
  │     "region": "eu-west",
  │     "pr": 501,
  │     "ml_confidence_initial": 0.81,
  │     "recommendation_initial": "ESCALATE",
  │     "manual_approval": true,
  │     "approved_by": "alice@org.com",
  │     "approval_timestamp": "2026-07-26T14:30:00Z",
  │     "merged_at": "2026-07-26T14:31:00Z",
  │     "resolution_time_minutes": 270
  │   }
  └─ Slack: "✅ PR #501 (eu-west) merged after manual approval (ML escalation resolved)"
```

**Output JSON** (shows ML confidence across sync batch):

```json
{
  "sync_batch_id": "gitops-sync-daily-20260726-ml-v3",
  "timestamp": "2026-07-26T10:00:00Z",
  "ml_scoring_enabled": true,
  "syncs": [
    {
      "target_repo": "org/deployed-infra-us",
      "pr_number": 500,
      "ml_confidence": 0.98,
      "ml_recommendation": "AUTO_MERGE",
      "status": "auto-merged",
      "feature_importance_top3": [
        {"feature": "deployment_history", "contribution": 0.12},
        {"feature": "security_clean", "contribution": 0.20},
        {"feature": "test_pass_rate", "contribution": 0.25}
      ],
      "merged_at": "2026-07-26T10:02:00Z"
    },
    {
      "target_repo": "org/deployed-infra-eu",
      "pr_number": 501,
      "ml_confidence": 0.81,
      "ml_recommendation": "ESCALATE",
      "status": "escalated",
      "escalation_reason": "ML confidence below auto-merge threshold (81% < 95%)",
      "feature_importance_top3": [
        {"feature": "test_pass_rate", "contribution": -0.10, "reason": "2/10 pending"},
        {"feature": "file_risk_score", "contribution": -0.09, "reason": "terraform file"},
        {"feature": "security_clean", "contribution": 0.20}
      ],
      "escalation_timeout_hours": 24,
      "manual_approval_required": true,
      "approved_by": "alice@org.com",
      "merged_at": "2026-07-26T14:31:00Z"
    },
    {
      "target_repo": "org/deployed-infra-asia",
      "pr_number": 502,
      "ml_confidence": 0.96,
      "ml_recommendation": "AUTO_MERGE",
      "status": "auto-merged",
      "merged_at": "2026-07-26T10:05:00Z"
    },
    {
      "target_repo": "org/deployed-infra-apac",
      "pr_number": 503,
      "ml_confidence": 0.72,
      "ml_recommendation": "REJECT",
      "status": "rejected",
      "rejection_reason": "ML confidence below rejection threshold (72% < 75%)",
      "feature_importance_top3": [
        {"feature": "lcs_similarity", "contribution": -0.15, "reason": "LCS 0.68 due to prior conflict"},
        {"feature": "file_risk_score", "contribution": -0.08},
        {"feature": "test_pass_rate", "contribution": 0.20}
      ]
    },
    {
      "target_repo": "org/deployed-infra-dr",
      "pr_number": 504,
      "ml_confidence": null,
      "ml_service_status": "timeout",
      "fallback_gate_used": true,
      "fallback_conditions_passed": [true, true, true, true, true],
      "ml_recommendation": "FALLBACK_AUTO_MERGE",
      "status": "auto-merged",
      "merged_at": "2026-07-26T10:03:00Z",
      "audit_note": "ML service unavailable; 5-condition hardcoded gate used (all conditions passed)"
    }
  ],
  "summary": {
    "total_prs": 5,
    "auto_merged_via_ml": 2,
    "escalated_via_ml": 1,
    "rejected_via_ml": 1,
    "auto_merged_via_fallback": 1,
    "ml_service_availability": 0.8,
    "average_confidence": 0.862,
    "success_rate": 0.6,
    "escalation_resolution_rate": 1.0
  }
}
```

---

## Usage Patterns — PHASE 1 (Still Supported)

### Pattern 1: Canonical Sync

Keep a staged config repo in sync with the canonical upstream.

```
Input:
  source: org/canonical-infra#main
  target: org/staging-infra#main
  sync_type: copy-file
  file_patterns: ["terraform/**/*.tf"]
  schedule: "0 10 * * *"  # Daily 10am

Output:
  - Auto-PR created if drift detected
  - PR auto-merged if no conflicts
  - Commit graph shows sync timeline
```

### Pattern 2: Release Coordination

Sync a release branch across multiple deployment repos.

```
Input:
  source: org/monorepo#release/v3.0.0
  target: org/deployment-prod#main
  sync_type: merge-branch
  conflict_strategy: manual-review
  auto_merge_pr: false

Output:
  - PR created with all commits from release branch
  - Awaits manual approval before merge
  - Commit graph shows release propagation
```

### Pattern 3: Conflict Detection Only

Monitor for drift without auto-syncing.

```
Input:
  source: org/upstream-app
  target: org/fork-app
  sync_type: detect-drift
  notify_on_conflict: true

Output:
  - JSON report of drift (no PR created)
  - Issue opened if drift exceeds threshold
  - Manual sync can be triggered later
```

---

## Integration Points

### With `manta-05` (Orçamento)

Sync cost/budget configs across project repos:
```
gitops → manta-05: Pass synced SICRO/composição files
manta-05 → gitops: Request sync of updated cost baselines
```

### With `manta-07` (Cronograma)

Sync schedule baselines across projects:
```
gitops: Detect drift in project schedules
manta-07: Generate recommendations for sync strategy
```

### With CI/CD Pipelines

Trigger GitOps sync on merge to main:
```
GitHub Actions:
  on:
    push:
      branches: [main]
  jobs:
    sync:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/invoke-skill@gitops-flow
          with:
            source: org/main#main
            target: org/staging#main
```

---

## Rules & Best Practices

### Phase 1 & 2 (Foundation)

1. **Always test in staging first**
   - Use `dry_run: true` to validate sync plan
   - Review conflict report before enabling `auto_merge_pr`

2. **Preserve audit trail**
   - All syncs create commits with GitOps attribution
   - Revert any sync via GitHub PR revert (creates new commit)
   - Phase 2: All syncs logged to `gitops_audit` table with risk_level, actor, timestamp

3. **Conflict resolution priority**
   - `auto-merge` for non-overlapping changes
   - `manual-review` for overlapping changes
   - Never use `ours/theirs` without human review
   - Phase 2: Use LCS algorithm (similarity threshold) before escalating to manual

4. **Naming conventions**
   - Branches: `gitops/{operation}-{timestamp}` or `gitops/{target}-on-{source}`
   - Commits: `gitops: {strategy} {source} → {target}`
   - Issues: `[GitOps] Conflict in {sync operation} #{number}`
   - Phase 2: Rollback branches: `gitops/rollback-{parent-op-id}-{timestamp}`

5. **Performance**
   - Limit to <1000 files per sync
   - Use `file_patterns` to narrow scope
   - Cache commit graph for repeated queries
   - Phase 2: Limit fan-out to ≤5 repos per sync (auto-merge safety gate)

6. **Security**
   - Use GitHub App with minimal scopes (contents:read, pull_requests:write)
   - Audit `ours/theirs` strategy usage (potential data loss)
   - Log all sync operations to Supabase `gitops_audit` table
   - Phase 2: Escalation rules protect high-risk files (package.json, Dockerfile, *.tf)

### Phase 2 Only (Production-Grade)

7. **Auto-Merge Safety Gates**
   - Enable auto-merge only after validating all 5 conditions
   - Always require audit logging before merge
   - Use escalation rules for high-risk files (not auto-merge eligible)
   - Monitor auto-merge success rate; if < 90%, increase escalation thresholds

8. **Scheduled Syncs**
   - Set max_retries conservatively (3–5 retries with exponential backoff)
   - Schedule syncs during low-traffic windows (off-peak hours)
   - Monitor scheduled sync audit log for failure patterns
   - Use event triggers for critical syncs (e.g., on release tag push)

9. **Transactional Rollback**
   - Always enable `transactional.rollback_on_failure` for production syncs
   - Test rollback procedures in staging before deploying to prod
   - Keep rollback audit entries for 90 days minimum (compliance)
   - Alert on-call team when rollback triggered (incident signal)

10. **Escalation Rules & Approvals**
    - Review escalation rules quarterly; update high_risk_files patterns as needed
    - Require at least 2 reviewers for infrastructure files (Dockerfile, *.tf)
    - Set timeout_hours conservatively (e.g., 24 hours) to avoid stale approvals
    - Block auto-merge until all escalation approvals received

11. **Multi-Repo Syncs**
    - Fan-out to ≤5 repos max (Phase 2 safety gate)
    - If syncing to >5 repos, break into multiple sync operations
    - Document dependencies between syncs (which repos depend on which)
    - Use rollback chain tracking to manage cascades

12. **Conflict Detection & LCS**
    - Set LCS similarity_threshold = 0.75 as baseline
    - Increase threshold to 0.85 for high-risk files (*.tf, Dockerfile)
    - Decrease to 0.65 for config-only files (*.yaml, *.json)
    - Always review LCS-suggested merges before applying

13. **Audit & Compliance**
    - Export audit log weekly to compliance system
    - Flag manual interventions (resolved conflicts) for review
    - Track auto_merge_eligible → auto_merged success rate
    - Monitor escalation frequency; high escalations = process issue

### Phase 3 Only (ML-Driven)

14. **ML Confidence Scoring**
    - Monitor ML confidence distribution: should be skewed toward ≥0.95 (>80% high confidence)
    - If many PRs fall in 0.75–0.95 range: feature weights may need tuning
    - If many PRs fall < 0.75: escalate to ML team for model debugging
    - Track ML vs. fallback gate performance: confidence should outperform 5-condition gate by >10%

15. **Fallback Gate Activation**
    - If ML service unavailable: fallback gate is stricter (all 5 conditions must pass)
    - Monitor fallback activation rate: >5% indicates ML service degradation (investigate)
    - Set ML timeout conservatively (5–10 seconds); longer timeouts hurt user experience
    - Keep Phase 2 5-condition gate well-maintained as fallback safety net

16. **Feature Importance Interpretation**
    - Share feature importance breakdowns with PRs in escalation tier (0.75–0.95)
    - Use feature importance to guide author actions: "Add missing tests" vs. "Request security approval"
    - Track feature importance trends: which factors most often block auto-merge? (signals process issue)
    - Quarterly review: are the 9 ML features still relevant to your org's risk profile?

17. **Confidence Tier Management**
    - HIGH (≥0.95): Silent auto-merge is safe; monitor for false positives (rare merge failures)
    - MEDIUM (0.75–0.95): Escalation timeout 24 hours; if frequently expired, increase auto-merge threshold
    - LOW (<0.75): Author should fix issues; if many re-submissions, lower rejection threshold (make less strict)

18. **Model Versioning & A/B Testing**
    - Use audit log to track ML model version for each PR (enables A/B comparisons)
    - When ML model updates: run A/B test window (e.g., 1 week) comparing old vs. new confidence scores
    - Only deploy new model if: (1) false positive rate ≤ 0.5%, (2) confidence distribution improves
    - Keep model changelog in audit table for compliance

---

## Outputs Summary

| Output | Format | Use Case |
|---|---|---|
| **Sync Report (JSON)** | Structured JSON | Machine-readable drift/sync status |
| **PR** | GitHub PR object | Review + merge sync changes |
| **Conflict Issue** | GitHub issue with diff blocks | Human-guided conflict resolution |
| **Commit Graph (Mermaid SVG)** | SVG diagram | Timeline of syncs + branch divergence |
| **ML Confidence Score** | float [0.0–1.0] | Auto-merge decision gate (v3.0 NEW) |
| **Feature Importance** | JSON dict | Explains ML decision for marginal scores (v3.0 NEW) |
| **ML Recommendation** | enum [AUTO_MERGE, ESCALATE, REJECT] | Actionable merge guideline (v3.0 NEW) |
| **Audit Log** | JSON (Supabase) | Compliance + trend analysis + ML audit trail (v3.0 enhanced) |

---

## Decision Flowchart: Is It Safe to Merge? — Phase 3 (ML-Based)

**Updated for v3.0**: Use this flowchart to determine whether a GitOps PR should auto-merge based on **ML confidence scoring**.

For the Phase 2 hardcoded 5-condition gate (used as fallback when ML unavailable), see the flowchart in § Phase 3 — ML-Based Auto-Merge Confidence Scoring → Fallback Mechanism.

```
PRIMARY FLOW (v3.0): ML Confidence Scoring
================================================

START: GitOps Sync PR Created
  │
  ├─── Call: git-auto-merge-confidence API
  │    ├─ SUCCESS: Receive confidence_score + recommendation
  │    │   └─ Proceed to CONFIDENCE-BASED ROUTING (below)
  │    │
  │    └─ FAILED (timeout/degraded):
  │        └─ FALLBACK: Use Phase 2 hardcoded 5-condition gate
  │           ├─ Check: tests_passing AND zero_critical AND low_risk_files AND repo_count_le_5 AND audit_logged
  │           ├─ If ALL pass → AUTO_MERGE
  │           └─ If ANY fail → ESCALATE or REJECT
  │           └─ Audit: {fallback_gate_used: true}
  │
  │
  ├─── CONFIDENCE-BASED ROUTING
  │
  ├─── TIER 1: Score ≥ 0.95 (HIGH CONFIDENCE)
  │    │    Recommendation: AUTO_MERGE ✅
  │    ├─ Label: "auto-merge-confident"
  │    ├─ Comment: "ML Confidence: {score}% ✅ Auto-merging..."
  │    ├─ Audit: {ml_confidence: score, recommendation: AUTO_MERGE, merged_at: timestamp}
  │    ├─ Merge immediately
  │    └─ Slack: "✅ Auto-merged (confidence: {score}%)"
  │
  ├─── TIER 2: Score 0.75–0.95 (MEDIUM CONFIDENCE)
  │    │    Recommendation: ESCALATE ⚠️
  │    ├─ Label: "requires-human-approval"
  │    ├─ Comment:
  │    │   ```
  │    │   ML Confidence: {score}% (below auto-merge threshold)
  │    │   Feature Importance:
  │    │   - {top_factor}: {contribution} ({reason})
  │    │   - {second_factor}: {contribution} ({reason})
  │    │   - {third_factor}: {contribution} ({reason})
  │    │   Recommendation: {actionable_recommendation}
  │    │   ```
  │    ├─ Assign: escalation_team (based on risk)
  │    ├─ Timeout: 24 hours
  │    ├─ Audit: {ml_confidence: score, recommendation: ESCALATE, escalation_reason: ...}
  │    │
  │    ├─ ON APPROVAL (within 24h):
  │    │  ├─ Merge PR
  │    │  └─ Audit: {manual_approval: true, approved_by: user}
  │    │
  │    └─ ON TIMEOUT (no approval):
  │       ├─ Auto-reject
  │       ├─ Label: "escalation-timeout"
  │       └─ Comment: "Escalation expired. Requires re-submission."
  │
  └─── TIER 3: Score < 0.75 (LOW CONFIDENCE)
       │    Recommendation: REJECT ❌
       ├─ Label: "confidence-too-low"
       ├─ Comment:
       │   ```
       │   ML Confidence: {score}% (below rejection threshold of 75%)
       │   Factors preventing merge:
       │   - {top_blocker}: {contribution} ({reason})
       │   - {second_blocker}: {contribution} ({reason})
       │   Action required: Fix {specific_issues} and re-submit.
       │   ```
       ├─ Audit: {ml_confidence: score, recommendation: REJECT, reason: ...}
       │
       └─ Author Action:
           ├─ Address identified issues
           ├─ Re-request ML evaluation
           └─ Or escalate manually (requires override)


DECISION TABLE (v3.0 ML-Based)
==============================

| Confidence | Decision | Action | Timeout | Audit |
|---|---|---|---|---|
| **≥ 0.95** | AUTO_MERGE | Merge immediately | None | auto_merged=true |
| **0.75–0.95** | ESCALATE | Hold for approval | 24h | escalated + approval_required |
| **< 0.75** | REJECT | Block merge | None | rejected + reason |
| **ML unavailable** | FALLBACK | Use Phase 2 gate | None | fallback_gate_used=true |

PHASE 2 FALLBACK: Hardcoded 5-Condition Gate (if ML unavailable)
================================================================

| Condition | Pass | Fail | Action |
|-----------|------|------|--------|
| Tests passing | ✅ | ❌ | HOLD + comment |
| Zero CRITICAL | ✅ | ❌ | HOLD + security review |
| Low-risk files | ✅ | ❌ | HOLD + ops review |
| ≤20 files, ≤500 lines | ✅ | ❌ | HOLD + review |
| ≤5 target repos | ✅ | ❌ | HOLD + comment |
| **All 5 pass** | **✅** | | **AUTO_MERGE (fallback)** |
| **Any fail** | | **❌** | **ESCALATE or HOLD** |
```

---

## Metadata

```
Skill: git-gitops-flow
Version: 3.0.0  # Phase 3: ML-powered confidence scoring
Created: 2026-07-26
Updated: 2026-07-26 (Phase 3 expansion: ML confidence scoring)
Tier: Sonnet
MCP Servers: 
  - GitHub (create_branch, create_pull_request, merge_pull_request, list_commits, search_code, update_pull_request_branch)
  - GitHub Actions (workflow dispatch for scheduled syncs)
  - git-auto-merge-confidence (ML inference service for confidence scoring) — NEW v3.0
  - Supabase (audit logging: gitops_audit, gitops_operations, gitops_conflicts, gitops_ml_scores) — NEW v3.0

PHASE 3 ADDITIONS (v3.0) — ML-Based Confidence Scoring:
  Auto-Merge Decision: ML confidence scoring replaces 5-condition hardcoded gate
  Confidence Thresholds:
    - ≥ 0.95: AUTO_MERGE (silent, immediate)
    - 0.75–0.95: ESCALATE (hold for human approval, 24h timeout)
    - < 0.75: REJECT (author must fix + re-submit)
  
  ML Model Inputs:
    - Test results (pass/fail/pending)
    - Security scan outcomes (CRITICAL/HIGH/MEDIUM/LOW)
    - File change patterns (risk classification)
    - Repo fan-out count (≤5 safety check)
    - LCS similarity scores (three-way merge analysis)
    - Commit message quality (conventional commits)
    - Author history (trustworthiness score)
    - Deployment history (success rate)
    - Time of day (off-peak = lower risk)
  
  ML Model Outputs:
    - confidence_score: [0.0–1.0] float
    - recommendation: enum [AUTO_MERGE, ESCALATE, REJECT]
    - feature_importance: dict {feature: weight, contribution, reason}
    - explanation: human-readable interpretation
  
  Fallback Mechanism:
    - If ML service unavailable (timeout > 5s): Use hardcoded 5-condition gate
    - Fallback is STRICTER: all 5 conditions must pass (Phase 2)
    - Audit: {fallback_gate_used: true}
  
  Explainability:
    - Feature importance breakdown for marginal cases (0.75–0.95)
    - Top 3 factors affecting confidence score
    - Actionable recommendations for author
  
  Audit Trail (NEW):
    - gitops_ml_scores: {pr_id, ml_confidence, recommendation, feature_importance, timestamp}
    - Tracks ML model versions & inference latency
    - Compliance-ready: explains every auto-merge decision

PHASE 2 FEATURES (v2.0) — Still Supported:
  Sync Strategies: 6 (copy-file, merge-branch, rebase, rebase-onto-main, squash-fixups, three-way-merge)
  Conflict Detection: Advanced LCS-based three-way merge with similarity thresholds
  Scheduled Syncs: GitHub Actions (cron + event-driven)
  Transactional Rollback: Atomic cascade revert on merge failure
  Escalation Rules: High-risk file detection (package.json, Dockerfile, *.tf, secrets, etc.)

Output Formats: 
  - JSON (sync report, audit log, ML scores + feature importance)
  - GitHub PR/Issue (with auto-merge status + ML recommendation)
  - Mermaid SVG (commit graph + decision flowchart)
  - Slack notifications (sync status, escalations, rollbacks, ML confidence)
  - Audit trail (Supabase: compliance-ready + ML explainability)

Use Cases: 
  - Phase 1: GitOps multi-repo sync, draft PR creation
  - Phase 2: Auto-merge production syncs, multi-region rollout, transactional rollback
  - Phase 3: ML-driven auto-merge (confidence-based routing), explainable decisions, fallback safety

GitHub Scopes Required: 
  - contents:read, contents:write
  - pull_requests:read, pull_requests:write
  - issues:read, issues:write
  - workflows:write (for scheduled syncs)

Logging: Supabase tables
  - `gitops_operations`: all sync operations (status, target_repos, strategy)
  - `gitops_conflicts`: conflict details + resolution (LCS analysis)
  - `gitops_audit`: compliance log (actor, timestamp, risk_level, auto_merged)
  - `gitops_ml_scores`: ML inference audit (pr_id, confidence, recommendation, feature_importance) — NEW v3.0
  - `gitops_rollbacks`: rollback chains (parent_op_id, reverted_prs, reason)

Classification: Horizontal Skill — Manta Associados (Multi-Agent GitOps Infrastructure)
Integration: Compatible with manta-05 (Orçamento), manta-07 (Cronograma), CI/CD workflows
Depends On: git-auto-merge-confidence (ML inference service)
Fallback: Hardcoded 5-condition gate (Phase 2)
```
