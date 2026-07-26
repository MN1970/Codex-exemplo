# SKILL.md — git-repository-analytics

**Version:** 1.0.0  
**Tier:** Haiku  
**Status:** ✅ Operacional  
**Last updated:** 2026-07-26

---

## Overview

**git-repository-analytics** analyzes Git repository commit history to extract structural and temporal patterns. Produces three outputs: a JSON timeline of contributor activity, an interactive heatmap HTML visualization, and a contributor activity graph. Designed for code review, team retrospectives, codebase health assessment, and project planning.

### Purpose

- Quantify code churn (additions/deletions by file, author, date range)
- Identify contributor patterns and distribution
- Detect peak activity periods and velocity trends
- Surface high-impact commits and large refactors
- Generate reports for stakeholder communication

---

## When to Use

**Trigger 1: Code quality audit or retrospective**  
"Analyze commit patterns to understand team velocity and code stability in the past quarter."

**Trigger 2: Onboarding or knowledge transfer**  
"Show me a timeline of who touched which files most, to identify subject-matter experts."

**Trigger 3: Project health assessment or funding proposal**  
"Generate a contributor activity heatmap and timeline to demonstrate project momentum for our investor deck."

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repository` | string | Yes | GitHub owner/repo (e.g., `anthropics/claude-code`) or local path (absolute). |
| `date_start` | ISO 8601 | No | Earliest commit date to include (default: 90 days ago). |
| `date_end` | ISO 8601 | No | Latest commit date to include (default: today). |
| `branch` | string | No | Branch name (default: `main` or `master`). |
| `file_filter` | regex or glob | No | Limit analysis to files matching pattern (e.g., `**/*.py`, `src/**`). |
| `min_contributors` | integer | No | Exclude contributors with fewer commits (default: 1). |
| `include_merge_commits` | boolean | No | Include merge commits in analysis (default: `false`). |

---

## Outputs

### 1. JSON Timeline (`timeline.json`)

Structured commit log with metadata:

```json
{
  "repository": "owner/repo",
  "branch": "main",
  "period": { "start": "2026-04-26", "end": "2026-07-26" },
  "total_commits": 342,
  "total_contributors": 8,
  "summary": {
    "additions": 12547,
    "deletions": 3821,
    "churn": 16368,
    "avg_commit_size": 47.8
  },
  "commits": [
    {
      "sha": "abc123def456",
      "author": "alice@example.com",
      "date": "2026-07-26T14:32:00Z",
      "message": "Refactor auth module for clarity",
      "files_changed": 5,
      "additions": 142,
      "deletions": 89,
      "churn": 231
    }
  ],
  "contributors": {
    "alice@example.com": {
      "commits": 124,
      "additions": 5420,
      "deletions": 1200,
      "files_touched": 47,
      "last_commit": "2026-07-26T14:32:00Z"
    }
  }
}
```

### 2. Heatmap HTML (`heatmap.html`)

Interactive visualization showing:
- Commits per day of week × time of day (grid heatmap)
- Contributor activity over time (stacked area chart)
- File churn distribution (bar chart)
- Embedded CSV data for offline use

Displays in light/dark theme; responsive and self-contained.

### 3. Contributor Graph (`contributors.html`)

Network visualization showing:
- Nodes: contributors (sized by commit count)
- Edges: co-authored files (weight = number of shared files)
- Color: contribution percentage
- Interactive: click to filter, hover for stats

---

## Tools Used

| Tool | Usage |
|------|-------|
| `mcp__github__search_commits` | (GitHub repos) Fetch commit metadata via GitHub API. |
| `Bash git log` | (Local repos) Parse commit history with `git log --format`, `git diff-tree`. |
| `Bash git rev-parse` | Validate branch and resolve HEAD. |

---

## How It Works

1. **Input validation**: Parse repository URL/path and date range.
2. **Commit fetch**: 
   - If GitHub URL: use `search_commits` MCP.
   - If local path: run `git log --all-match` with date filters.
3. **Parse metadata**: Extract author, date, file changes, line additions/deletions per commit.
4. **Aggregate**: Sum churn by author, day-of-week, file, week.
5. **Generate outputs**:
   - JSON: raw timeline + summary stats.
   - Heatmap: render as HTML with embedded Plotly/Chart.js.
   - Graph: compute node/edge layout, render as interactive SVG/D3.
6. **Return**: File paths to three artifacts.

---

## Examples

### Example 1: Analyze public GitHub repo (90 days)

**Input:**
```
repository: anthropics/claude-code
date_start: 2026-04-26
date_end: 2026-07-26
```

**Output:**
- `timeline.json`: 342 commits, 8 contributors, 12.5k additions, 3.8k deletions
- `heatmap.html`: Peaks on Tuesday–Thursday 9–11am UTC; contributor Alice leads with 36% of commits
- `contributors.html`: Tight cluster (high co-authorship on auth module); Bob isolated (DevOps-only)

### Example 2: Filter by file type (Rust codebase)

**Input:**
```
repository: /home/user/my-project
file_filter: **/*.rs
branch: develop
date_start: 2026-01-01
include_merge_commits: false
```

**Output:**
- `timeline.json`: 156 commits touching .rs files
- `heatmap.html`: Steady Monday–Wednesday pattern; spike week-of 2026-03-15 (major refactor: 1.2k additions)
- `contributors.html`: 4 nodes; Alice + Bob frequently co-edit `engine.rs`

### Example 3: Identify subject-matter experts

**Input:**
```
repository: manta-repo/infrastructure
min_contributors: 5
date_start: 2025-07-26 (one year)
```

**Output:**
- `timeline.json`: Grouped by file → identify who touched `terraform/` most (Carol: 67 commits, 2.1k additions)
- `heatmap.html`: Carol's activity consistent; David recent spike (onboarding)
- `contributors.html`: Carol (cluster hub); David (new, learning path clear in edges)

---

## Limitations

1. **API rate limits**: GitHub `search_commits` caps at ~60 req/min; large repos (>5k commits in range) may require pagination loops and delay.

2. **Merge commit noise**: Unless filtered, merge commits inflate contributor count and obscure individual contributions.

3. **Email aliases**: Git history may contain multiple email addresses for same person; skill does not auto-deduplicate (user must normalize locally).

4. **Binary files**: Line-count stats (additions/deletions) are meaningless for `.png`, `.zip`, `.jar`; churn is counted but not actionable.

5. **Rebases and force-pushes**: Rewritten history shows as deletions + additions; does not detect "same logical commit, different SHA."

6. **Date range performance**: Queries spanning >2 years on large monorepos (>10k commits) may timeout or produce incomplete results; recommend sliding windows.

7. **Local-only commits**: If branch has unpushed commits, GitHub MCP cannot see them; use local repo path instead.

8. **Access restrictions**: Private repos require GitHub token in session; public repos work without auth.

---

## Related Skills

- **manta-maestro**: Route analysis to domain agent (e.g., agente-infraestrutura for codebase health in infra projects).
- **portal-gestao-manta**: Surface timeline + heatmap in project dashboards.
- **context-guardian**: Use contributor graph to assign code reviews to subject-matter experts.

---

## Invocation

From any Manta agent or Claude session:

```
/git-repository-analytics <repository> [--date-start YYYY-MM-DD] [--date-end YYYY-MM-DD] [--branch BRANCH] [--file-filter PATTERN]
```

Or programmatically via skill invoke:

```python
result = skill("git-repository-analytics", {
    "repository": "owner/repo",
    "date_start": "2026-04-26",
    "date_end": "2026-07-26"
})
# result.timeline, result.heatmap_html, result.contributors_html
```

---

## Support

**Questions / Issues:**  
- Tag `@git-analytics` in Slack channels or create ticket in Jira under `MNT-ANALYTICS`.
- See `SKILL-TROUBLESHOOTING.md` for common errors (rate limits, branch not found, empty date range).

**Maintenance:**  
- Next review: 2026-10-26 (quarterly)
- Owned by: Platform Engineering team
- Last patch: v1.0.0 (baseline)
