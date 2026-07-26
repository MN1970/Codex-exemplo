# Git Multi-Repo Workflows

**Version:** 1.0.0  
**Tier:** Sonnet  
**Updated:** 2026-07-26

## Overview

Coordinate changes across 2–5 repositories in parallel, with dependency tracking, critical path analysis (PERT), and Gantt timeline visualization.

## When to Use

- "Update feature across multiple repos"
- "Coordinate multi-repo release"
- "Map dependencies before migration"

## Inputs

```json
{
  "repos": [
    {"name": "repo-A", "branch": "main"},
    {"name": "repo-B", "branch": "develop"},
    {"name": "repo-C", "branch": "develop"}
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
  "dry_run": true
}
```

## Outputs

### 1. Gantt HTML Timeline
Interactive SVG with:
- PR bars (merged/open/blocked/failing)
- Dependency arrows (critical path highlighted)
- Milestone markers
- Blockers panel (CI failures, pending reviews, merge conflicts)

### 2. Summary JSON
```json
{
  "dependency_graph": { "repo-A": [], "repo-B": ["repo-A"], ... },
  "topological_order": ["repo-A", "repo-B", "repo-C"],
  "critical_path": ["repo-A → repo-B → repo-C"],
  "duration_days": 12,
  "blockers": [
    {
      "repo": "repo-B",
      "reason": "CI failing",
      "pr_number": 42
    }
  ],
  "prs": [
    {
      "repo": "repo-A",
      "number": 40,
      "status": "merged",
      "merged_at": "2026-07-26T12:00:00Z"
    }
  ]
}
```

## Architecture

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

## Key Features

### Topological Sort (Kahn's Algorithm)
- Detects circular dependencies → fails fast
- Produces safe merge sequence: `[repo-A] → [repo-B, repo-C] → [repo-D]`
- Time complexity: O(V+E)

### Critical Path Analysis (PERT)
- Calculates earliest merge window for each PR
- Identifies bottleneck repos (longest serial chain)
- Estimates full completion date

### Blocker Detection
- Pending CI checks
- Pending code reviews
- Merge conflicts
- Dependency not merged

## MCP Tools

- `github__list_pull_requests` — fetch branch PRs
- `github__get_commit` — extract created/merged dates

## Examples

### Example 1: Feature Rollout (3 repos)

**Input:**
```json
{
  "repos": [
    {"name": "graphql-server", "branch": "main"},
    {"name": "react-client", "branch": "main"},
    {"name": "mobile-app", "branch": "main"}
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
  ]
}
```

**Output (Gantt):**
```
[graphql-server] ████████████ (12h) → MERGED
                          ├→ [react-client]   ████████ (8h) → MERGED
                          ├→ [mobile-app]     ████████ (8h) → OPEN (waiting review)
```

**Critical Path:** graphql-server → mobile-app (20h total)

### Example 2: Migration with Dependencies

**Topological Order:** [shared-lib] → [service-A, service-B] → [api-gateway]

## Limitations

- **5 repos max** per run (use sequential batches for larger migrations)
- **No auto-merge** (human approval required)
- **Assumes linear timeline** (no rebases or force-pushes during workflow)
- **GitHub API rate limits** (60-100 requests/hour)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Circular dependency detected" | Check `depends_on` fields; reorder repos |
| "Timeout fetching PR data" | Split into smaller batches (≤3 repos) |
| "Merge conflict not resolved" | Re-run with manual conflict resolution steps |

## Related Skills

- `git-gitops-flow` — single repo sync
- `git-commit-optimizer` — rebase prep
