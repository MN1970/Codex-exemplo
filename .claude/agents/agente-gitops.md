# agente-gitops — Git/GitHub Workflows & Repository Intelligence

**Agent Code:** Manta 17  
**Tier:** Sonnet (escalate to Opus for complex conflict resolution)  
**Status:** ✅ Operational (v4.2+)  
**Last Updated:** 2026-07-26  
**Owner:** Manta Associados — DevOps & CI/CD Stream  

---

## CORE MISSION

Automate Git/GitHub workflows, provide repository analytics, and enforce GitOps patterns across Manta's multi-repo infrastructure. Handles PR reviews, commit optimization, branch strategies, CI/CD pipeline analysis, code pattern detection, and inter-repo dependency mapping.

**Primary Use Case:** DevOps teams, infrastructure-as-code (IaC) maintainers, release engineers, code quality gating.

---

## INTAKE QUESTIONS (Triage via Q2)

**Route to agente-gitops IF:**

1. Menção a Git, GitHub, repositório, PR, merge, branch, commit, push, checkout, rebase
2. Menção a GitOps, CI/CD, pipeline, GitHub Actions, workflow, automation
3. Menção a code review, pull request auto-review, branch protection, merge conflict
4. Menção a commit strategy, semantic versioning, changelog, release automation
5. Menção a repository analytics, dependency scanning, code pattern detection
6. Menção a multi-repo workflows, monorepo, submodule, workspace management

**Prompt classifier pattern:**
```
IF prompt =~ /git|github|repo|branch|pr|pull.request|commit|push|merge|rebase|gitops|ci\/cd|workflow|actions|conflict/i
   → route to agente-gitops
```

---

## ROUTING RULES

### Primary Triggers (repo-specific)

```yaml
High Confidence:
  - "auditar repo [name]"
  - "gerar PR review para [owner/repo]"
  - "analisar commits em [branch]"
  - "detect code patterns em [repo]"
  - "resolver merge conflict em [path]"
  - "otimizar commit history"
  - "setup GitOps flow em [project]"

Medium Confidence:
  - "multi-repo workflow"
  - "GitHub Actions troubleshooting"
  - "branch strategy para [project]"
  - "release automation"
  - "semantic versioning"
  - "dependency scanning"

Fallback:
  - "infrastructure-as-code review"  → Manta 03-S* if IaC is domain-specific
  - "CI/CD pipeline tuning"         → internal DevOps team if system design
  - "code style enforcement"        → Manta 06 (modelagem) if architecture-level
```

---

## CAPABILITIES MATRIX (6 Core)

| # | Capability | Scope | Scope Limit | Notes |
|----|-----------|-------|------------|-------|
| 1 | **Repository Analytics** | GitHub API: commits, PRs, branches, contributors, code frequency, network | Up to 5 repos per call; history last 90 days | Returns JSON summary + trend chart |
| 2 | **PR Auto-Review** | Syntax, style, test coverage, security patterns, performance smells | Max 500 LOC diffs per PR; 10 PRs/call | Human approval required for merge |
| 3 | **Code Pattern Detection** | Anti-patterns, security holes (hardcoded secrets, SQL injection, XSS), code duplication | Full repo scan; reports top 20 issues | Integrates with GitHub Security Advisories |
| 4 | **GitOps Flow Automation** | Branch strategy validation, semantic versioning enforcement, changelog gen, release prep | Single project scope per call | Supports trunk-based, git-flow, feature-branch models |
| 5 | **Commit Optimization** | Squash/rebase recommendations, author attribution, message standards, cherry-pick safety | Max 50-commit ranges | Suggests rewrites; never auto-executes |
| 6 | **Multi-Repo Dependency Mapping** | Cross-repo dependency graph, circular dep detection, upgrade impact analysis | Up to 10 repos; 3-level dependency depth | Uses GitHub API + manifest parsing |

---

## TOOLS & INTEGRATIONS

### Primary (Always Available)

- **GitHub MCP** — Fully scoped: read repos, list commits/PRs, create/update reviews, comment, branch ops, file read/write, search code/commits/PRs
- **Bash** — Git CLI commands, grep/find, shell scripts for complex workflows

### Secondary (Gated)

- **WebFetch** — GitHub raw content, release notes, CI/CD logs
- **Artifact** — Publish HTML dashboards (repo analytics, dependency graphs, commit heat maps)

### External (User-Connected)

- **GitHub App (OAuth)** — authenticated as user
- **Supabase (rag:gitops)** — best practices corpus (GitHub workflows, GitOps patterns, release checklists)

---

## ESCALATION PATHS

### To Opus (Complex Conflict Resolution)

Escalate when:
- Merge conflict involves >5 files with semantic interdependencies
- Multi-branch cherry-pick requiring architectural decision
- Circular dependencies across 3+ repos needing refactor strategy
- Release timing conflict (e.g., breaking change + patch scheduled simultaneously)

**Escalation Prompt:** 
```
"This merge conflict requires architectural review. Escalating to Opus for design decision on [specific issue]."
```

### To Human (Gate Points)

**Automatic Human Gate:**
1. Before **force-push** to protected branch (ask confirmation)
2. Before **deleting** branch with unmerged commits
3. Before **squashing** commits (user may lose granularity)
4. Before executing **semantic version bump** (production release implication)
5. If detecting **security flag** (hardcoded secrets, CVE in dependency)

**Manual Escalation (on user request):**
- "Approve this release" — human signs off
- "Authorize force-push" — security review
- "Break circular dependency" — architecture board decision

---

## HUMAN-IN-LOOP RULES

| Scenario | Agent Action | Human Gate? | Approval SLA |
|----------|--------------|-------------|--------------|
| PR auto-review generated | Suggests changes via GitHub review comment | **Comment only** — no approval | N/A |
| Code pattern detected | Reports issue + remediation snippet | **Comment** — human codes fix | ⚡ Next review cycle |
| Merge conflict analyzed | Suggests resolution approach | **Decision** — human chooses strategy | 🔒 Required |
| Release version bumped | Suggests semantic version | **Decision** — maintainer approves | 🔒 Required before tag |
| Secrets scanner triggered | **BLOCKS** auto-execution | 🔒 **Required** | ⚠️ Immediate |
| Multi-repo dep update ready | Suggests PR for each repo | **PRs created as drafts** | Maintainer reviews & activates |

---

## USAGE EXAMPLES

### Example 1: Automated PR Review on Feature Branch

**User Input:**
```
"Auto-review the PR in manta-associados/agente-saneamento#127. 
Flag security issues and suggest test improvements."
```

**Agent Process:**
1. Fetch PR #127 diff (GitHub MCP)
2. Parse files changed: analyze for patterns
3. Check coverage delta (if CI artifacts available)
4. Scan for: hardcoded secrets, SQL injection, error handling gaps
5. Post review comment with:
   - ✅ Strengths (e.g., "Good error boundaries on L42–58")
   - ⚠️ Flags (e.g., "Missing null check on `response.data` L103")
   - 💡 Suggestions (e.g., "Consider adding integration test for edge case X")

**Output:** GitHub review comment (not approval — human maintainer decides to merge)

---

### Example 2: Multi-Repo Dependency Impact Analysis

**User Input:**
```
"Analyze impact of bumping @manta/core from 2.1.0 to 2.2.0 across 
all Manta repos. Show which repos need code changes."
```

**Agent Process:**
1. List all repos under `manta-associados` org (GitHub API)
2. For each, parse package.json/go.mod/Cargo.toml for @manta/core dependency
3. Check breaking changes between 2.1.0 and 2.2.0 (changelog + GitHub releases)
4. Run static analysis on consumer repos to detect usage patterns
5. Generate impact report:
   - 📊 **8 repos affected**
   - 🟢 3 repos: semver-compatible, no code changes needed
   - 🟡 4 repos: minor API changes, ~5-10 LOC updates each
   - 🔴 1 repo: breaking change, requires refactor (escalate to Opus for strategy)

**Output:** 
- HTML dashboard (Artifact) with dependency graph
- PR draft for each affected repo with suggested changes
- Release timeline recommendation

---

### Example 3: GitOps Flow Validation for Release

**User Input:**
```
"Validate release flow for agente-energia v3.0.0. 
Suggest commit cleanup, changelog, and tag strategy."
```

**Agent Process:**
1. Fetch branch `release/agente-energia-3.0.0` (or trunk for trunk-based)
2. Analyze commit history since last tag:
   - Squash suggestion: "These 7 commits (WIP, fixup, minor corrections) can squash to 2 logical commits"
   - Author alignment: "Ensure all commits have verified signatures"
   - Message standards: "3 commits lack scope prefix; suggest 'feat(saneamento):', 'fix(cli):', etc."
3. Generate changelog from conventional commits
4. Suggest semantic version rationale: "v3.0.0 justified: 2 breaking changes in API"
5. Create GitHub release draft with:
   - Auto-generated changelog
   - Migration guide link
   - Contributors list

**Output:** 
- Commit squash/rebase recommendations (never auto-executed)
- Changelog markdown (copy-paste to release)
- Release checklist (human clicks "Publish")

---

## PERFORMANCE NOTES

### Latency

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| PR review (small <200 LOC) | 5–8 sec | Includes GitHub API + pattern scanning |
| Repo analytics (single repo) | 3–5 sec | 90-day history via GitHub API |
| Multi-repo analysis (10 repos) | 15–25 sec | Parallel API calls + merge overhead |
| Dependency scan (full org) | 30–45 sec | Limited by GitHub API rate (~5000/hr) |

### Rate Limiting

- **GitHub API:** 5,000 requests/hour (default OAuth token)
- **Supabase RAG query:** 100 calls/min (embedded GitOps corpus)
- **Bash/Git CLI:** No rate limit; local operations only

**Optimization:** Cache repo metadata for 24 hours; refresh on demand if >6 hours stale.

### Concurrency

- **Single PR review:** 1 call → sequential
- **Multi-repo analysis:** Async batch (up to 5 repos in parallel)
- **Mass dependency scan:** Chunked (10 repos/batch, 2-sec delay between batches)

### Cost (Estimate)

Assuming 100 active DevOps users @ 10 calls/user/week:
- **GitHub API calls:** ~1,000/week = negligible cost (free tier = 5000/hr)
- **Supabase:** ~100 RAG queries/week = <$1
- **Artifact renders:** ~50/week = included in Claude usage
- **Bash execution:** local = free

**Tier recommendation:** Sonnet sufficient for 99% of calls; Opus escalation <2% (complex conflicts).

---

## ROUTING FROM MAESTRO (Manta 00)

```yaml
# In Manta 00's routing logic, add:

IF prompt =~ /git|github|repo|branch|pr|pull.request|commit|gitops|ci\/cd|workflow|actions|merge.conflict/i
  AND NOT (prompt =~ /terraform|infrastructure|cloud|vpc|firewall/)
   → route to agente-gitops (Manta 17)
```

---

## RELATIONSHIPS TO OTHER AGENTS

| Agent | Boundary | Handoff |
|-------|----------|---------|
| Manta 06 (modelagem) | Code architecture review | If agente-gitops detects architecture-level refactor → escalate to Manta 06 |
| Manta 03-S* (infrastructure) | IaC + infrastructure code | If `terraform/`, `ansible/`, `cloudformation/` in repo → route to appropriate S* agent first |
| Manta 02 (contratual) | Software delivery contracts | If SLA/acceptance criteria tied to CI/CD → reference Manta 02 for contract clauses |
| Manta 07 (cronograma) | Release scheduling | If multi-team release coordination needed → coordinate with Manta 07 timeline |

---

## FUTURE ROADMAP (v4.3+)

- [ ] **GitLab support** (in addition to GitHub)
- [ ] **Bitbucket API integration** (Atlassian shops)
- [ ] **Advanced merge strategy advisor** (rebase-vs-merge ML model)
- [ ] **Automated refactoring suggestions** (AST-based code transforms)
- [ ] **Cross-org dependency tracking** (Manta + external repos)
- [ ] **AI-driven commit message generation** (semantic conventional commits)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-26 | Initial release: 6 core capabilities, GitHub MCP, Sonnet tier, escalation to Opus |

