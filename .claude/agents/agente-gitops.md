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
7. **[Fase 2]** Menção a "threat model this repo", "security threats in code", "analyze repository threats"
8. **[Fase 2]** Menção a "incident response", "git incident analysis", "emergency rollback", "revert deployment"

**Prompt classifier pattern:**
```
IF prompt =~ /git|github|repo|branch|pr|pull.request|commit|push|merge|rebase|gitops|ci\/cd|workflow|actions|conflict|threat.model|incident|rollback|emergency.revert/i
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

## CAPABILITIES MATRIX (11 Core: 6 Fase 1 + 5 Fase 2)

### Fase 1 — Foundation (v1.0.0)

| # | Capability | Scope | Scope Limit | Notes |
|----|-----------|-------|------------|-------|
| 1 | **Repository Analytics** | GitHub API: commits, PRs, branches, contributors, code frequency, network | Up to 5 repos per call; history last 90 days | Returns JSON summary + trend chart |
| 2 | **PR Auto-Review** | Syntax, style, test coverage, security patterns, performance smells | Max 500 LOC diffs per PR; 10 PRs/call | Human approval required for merge |
| 3 | **Code Pattern Detection** | Anti-patterns, security holes (hardcoded secrets, SQL injection, XSS), code duplication | Full repo scan; reports top 20 issues | Integrates with GitHub Security Advisories |
| 4 | **GitOps Flow Automation** | Branch strategy validation, semantic versioning enforcement, changelog gen, release prep | Single project scope per call | Supports trunk-based, git-flow, feature-branch models |
| 5 | **Commit Optimization** | Squash/rebase recommendations, author attribution, message standards, cherry-pick safety | Max 50-commit ranges | Suggests rewrites; never auto-executes |
| 6 | **Multi-Repo Dependency Mapping** | Cross-repo dependency graph, circular dep detection, upgrade impact analysis | Up to 10 repos; 3-level dependency depth | Uses GitHub API + manifest parsing |

### Fase 2 — Expanded Detection & Automation (v2.0.0)

| # | Capability | Scope | Scope Limit | Notes |
|----|-----------|-------|------------|-------|
| 7 | **Expanded Threat Detection** | AST-based code analysis, OWASP Top 10 patterns, supply chain risks, third-party code audit | Full repo scan with AST; 500+ LOC/sec | Flags: CVE dependencies, license violations, typosquatting |
| 8 | **Auto-Merge Decision Engine** | 5-condition safety matrix: tests green, zero CRITICAL findings, low-risk pattern match, protected branch rules, author verification | Requires passing CI + security gates | Blocks merge if any condition fails; escalates to human |
| 9 | **Threat Modeling** | STRIDE analysis, attack surface mapping, data flow diagram generation, threat register from code | Single repo per call | Output: threat JSON + markdown risk scorecard |
| 10 | **Incident Response Automation** | Root cause analysis from commit history, rollback candidate identification, blame chain, impact scope | Handles git log + GitHub issue linking | Suggested revert strategies with safety rankings |
| 11 | **Transactional Rollback** | Atomic multi-repo rollback orchestration, dependency-aware sequencing, verify pre/post-rollback state | Up to 10 repos; state verification mandatory | Requires explicit human approval; audit logged |

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

## AUTO-MERGE DECISION TREE (Fase 2)

**Flowchart: Automated PR Merge Gate**

```
╔══════════════════════════════════════════════════════════════╗
║  PR Submitted → Auto-Merge Safety Check Triggered            ║
╚══════════════════════════════════════════════════════════════╝
                              ↓
                ┌─────────────┴─────────────┐
                ↓                           ↓
        ┌──────────────┐          ┌──────────────┐
        │ Condition 1: │          │ Condition 2: │
        │ Tests Green? │          │ Zero CRITICAL│
        └──────────────┘          │ Findings?    │
                ↓                 └──────────────┘
            PASS/FAIL                  ↓
            (CI status)            PASS/FAIL
                                 (Security scan)
                ↓                      ↓
    ┌───────────────────────────────────────┐
    │ Condition 3: Low-Risk Pattern Match?  │  [Pattern classifier on PR metadata]
    │ - Docs-only changes                   │
    │ - Test-only changes                   │
    │ - Version bump (semver compatible)    │
    │ - Dependency update (green tests)     │
    └───────────────────────────────────────┘
                      ↓
                  PASS/FAIL
                      ↓
    ┌───────────────────────────────────────┐
    │ Condition 4: Protected Branch Rules?  │  [GitHub branch settings]
    │ - Requires PR reviews? (check: ≥1)    │
    │ - Dismisses stale approvals? (check)  │
    │ - Requires status checks? (check: ✓)  │
    └───────────────────────────────────────┘
                      ↓
                  PASS/FAIL
                      ↓
    ┌───────────────────────────────────────┐
    │ Condition 5: Author Verification?     │  [Git commit signing]
    │ - Commit verified GPG signature?      │
    │ - Author in approved list?            │
    │ - No suspicious author attributes?    │
    └───────────────────────────────────────┘
                      ↓
                  PASS/FAIL
                      ↓
        ┌─────────────┴──────────────┐
        ↓                            ↓
    ┌────────────┐          ┌──────────────┐
    │ ALL 5 ✓    │          │ ANY FAIL     │
    │ AUTO-MERGE │          │ DRAFT PR     │
    │ (logged)   │          │ (flag reason)│
    └────────────┘          └──────────────┘
        ↓                         ↓
    [Merged]              [Awaits human]
    Slack notify          Slack notify
    Audit log             Review request
```

**Decision Matrix (5 Conditions):**

| Condition | Check | Pass Criteria | Fail Action |
|-----------|-------|---------------|-------------|
| **1: Tests Green** | CI/CD status | All required status checks PASS | Await re-run |
| **2: Zero CRITICAL** | Security scan (OWASP + CVE) | Zero CRITICAL severity findings | Manual review required |
| **3: Low-Risk Pattern** | Commit diff classification | Matches safe pattern (docs/test/semver/green-dep) | Flag risk level; await approval |
| **4: Branch Protection** | GitHub branch settings | All rules enabled (review, status, dismiss) | Cannot auto-merge; escalate |
| **5: Author Verified** | GPG signature + allowlist | Commit signed + author trusted | Cannot auto-merge; security hold |

**Pseudocode:**

```python
def auto_merge_decision(pr: PullRequest) -> Decision:
    """
    Evaluate PR against 5-condition matrix.
    Returns: MERGE | DRAFT | HOLD
    """
    
    # Condition 1: Test status
    if not all_checks_pass(pr.status_checks):
        return DRAFT("Tests not green")
    
    # Condition 2: Security scan
    security_scan = scan_pr_for_threats(pr)
    if security_scan.has_critical:
        return HOLD("CRITICAL security finding")
    
    # Condition 3: Pattern classification
    pattern = classify_change_pattern(pr)
    if pattern not in [DOCS, TEST, SEMVER_COMPAT, SAFE_DEP_UPDATE]:
        return DRAFT(f"Non-standard pattern: {pattern}")
    
    # Condition 4: Branch protection rules
    branch = get_branch(pr.target)
    if not branch.has_all_protections():
        return HOLD("Branch protection rules not enforced")
    
    # Condition 5: Author verification
    for commit in pr.commits:
        if not commit.is_signed() or commit.author not in TRUSTED_AUTHORS:
            return HOLD(f"Commit {commit.sha} not verified")
    
    # All conditions pass
    log_audit("Auto-merge approved", pr=pr, timestamp=now())
    notify_slack(f"✅ {pr.title} auto-merged")
    return MERGE()
```

---

## ESCALATION PATHS (Updated Fase 2)

### Fase 1 — Opus (Complex Conflict Resolution)

Escalate when:
- Merge conflict involves >5 files with semantic interdependencies
- Multi-branch cherry-pick requiring architectural decision
- Circular dependencies across 3+ repos needing refactor strategy
- Release timing conflict (e.g., breaking change + patch scheduled simultaneously)

**Escalation Prompt:** 
```
"This merge conflict requires architectural review. Escalating to Opus for design decision on [specific issue]."
```

### Fase 1 — Human (Gate Points)

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

### Fase 2 — Security & Incident Escalation (New)

**Security Findings → Slack (Automated Notification)**

When threat detection (Capability 7) or auto-merge check (Capability 8) identifies issues:

| Severity | Channel | Message Format | Action |
|----------|---------|-----------------|--------|
| **INFO** | #gitops-security-log | "ℹ️ Low-risk: [repo] [finding] (Details: [link])" | Logged only; no block |
| **WARN** | #gitops-security-log | "⚠️ Medium: [repo] [finding] (Remediation: [snippet])" | PR comment; no auto-merge |
| **HIGH** | #security-team | "🔴 HIGH: [repo] [finding] (Assign to: [owner])" | Auto-comment on PR; block auto-merge |
| **CRITICAL** | #security-team + @ciso-on-call | "🚨 CRITICAL: [repo] [finding] (Quarantine: [branch]) (Decision SLA: 1h)" | Blocks all automation; human approval required |

**CRITICAL Findings → Human Approval Required**

Blocking scenarios (auto-merge blocked; manual intervention required):

1. **Hardcoded secrets detected** (AWS key, GitHub token, DB password)
   - Action: Quarantine branch, notify security@manta, run `git-secrets` remediation
   - Approval: Security engineer (CISO)
   - Timeline: <1 hour

2. **Known CVE in dependency** (CVSS ≥ 7.0)
   - Action: Suggest patch version; block merge if unpatched
   - Approval: DevOps lead + affected team
   - Timeline: <4 hours (patch) or <24 hours (explanation)

3. **Supply chain risk detected** (typosquatting, unusual source)
   - Action: Quarantine; scan for infection
   - Approval: Security engineer
   - Timeline: <2 hours

4. **Compromised maintainer account suspected** (unusual commit pattern, new email)
   - Action: Require 2-factor auth re-verification; lock commits
   - Approval: GitHub org admin + DevOps
   - Timeline: Immediate

**Threats → Security Engineering Escalation**

Threat modeling (Capability 9) produces risk scorecard; escalate to security engineering:

- **STRIDE findings** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
  - Route to: Security team + architecture board
  - Response SLA: 24 hours (assessment), 72 hours (remediation plan)

- **Attack surface mapping** identifies new exposures
  - Route to: Security + DevOps
  - Action: Create GitHub issues, tag `security-review-required`

- **Data flow violations** (unauthenticated data access, unencrypted transmission)
  - Route to: Security + product owner
  - Action: Block deployment until fixed

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

### Latency (Fase 1 + Fase 2)

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| PR review (small <200 LOC) | 5–8 sec | Includes GitHub API + pattern scanning |
| Repo analytics (single repo) | 3–5 sec | 90-day history via GitHub API |
| Multi-repo analysis (10 repos) | 15–25 sec | Parallel API calls + merge overhead |
| Dependency scan (full org) | 30–45 sec | Limited by GitHub API rate (~5000/hr) |
| **[Fase 2] Threat detection (AST analysis)** | **45–120 sec** | Full AST parse + OWASP pattern matching (500+ LOC/sec) |
| **[Fase 2] Auto-merge decision (5-condition)** | **8–15 sec** | Security scan + CI status + pattern classification |
| **[Fase 2] Threat modeling (STRIDE)** | **60–90 sec** | Attack surface mapping + data flow analysis |
| **[Fase 2] Incident response (root cause)** | **20–45 sec** | Commit history + blame chain analysis |
| **[Fase 2] Rollback orchestration (10 repos)** | **30–60 sec** | Dependency sequencing + state verification |

### Rate Limiting

- **GitHub API:** 5,000 requests/hour (default OAuth token)
- **Supabase RAG query:** 100 calls/min (embedded GitOps corpus)
- **Bash/Git CLI:** No rate limit; local operations only
- **[Fase 2] AST analysis:** ~500 LOC/sec (internally managed; no external rate limit)

**Optimization:** Cache repo metadata for 24 hours; refresh on demand if >6 hours stale. Cache AST parse results for 6 hours per commit.

### Concurrency

- **Single PR review:** 1 call → sequential
- **Multi-repo analysis:** Async batch (up to 5 repos in parallel)
- **Mass dependency scan:** Chunked (10 repos/batch, 2-sec delay between batches)
- **[Fase 2] Threat scanning:** Single repo per call (AST is CPU-intensive)
- **[Fase 2] Rollback orchestration:** Sequential (atomic multi-repo safety)

### Cost (Estimate)

**Fase 1 (per call average): ~$0.08**
- GitHub API calls: ~0.5 calls average = negligible
- Supabase RAG: ~$0.02
- Artifact render: ~$0.05
- Bash execution: local (free)

**[Fase 2] Expanded cost (per call average): ~$0.50**
- AST analysis (threat detection, incident response): +$0.35 (CPU-intensive)
- Security scanning (OWASP, CVE, typosquatting): +$0.10
- GitHub API (verification calls): +$0.03
- Rollback orchestration (state verification): +$0.02

**Scaling assumptions (100 active DevOps users @ 10 calls/user/week):**
- Fase 1: ~$80/week baseline
- Fase 2 add-on: ~$350/week (if ~70% of calls use new capabilities)
- **Monthly estimate: ~$1,720 (Fase 1 + Fase 2 blended)**

**Tier recommendation:** 
- **Fase 1:** Sonnet sufficient for 99% of calls; Opus <2% (complex conflicts)
- **[Fase 2]:** Sonnet for detection/review; **Opus for threat modeling + incident response** (AST complexity, risk assessment)

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

## ROADMAP — Fase 2 (v2.0.0 Implementation Timeline)

### W5–W6 (Week 5–6 from Fase 2 start): Core Threat Detection

**Goals:** Deploy Capabilities 7 (Expanded Threat Detection) + escalation to Slack

- [x] Implement AST parser (Python + JavaScript support)
- [x] Deploy OWASP Top 10 pattern matchers
- [x] Integrate with GitHub Security Advisories (CVE sync)
- [x] Configure Slack webhook for security findings (#gitops-security-log)
- [ ] Load test AST analysis (target: 500 LOC/sec)
- [ ] Beta test on 3 internal repos (Manta-platform, agente-maestro, cli-tools)

**Rollout:** Internal teams only; feedback cycle 3 days

---

### W7–W8 (Week 7–8): Auto-Merge Decision Engine

**Goals:** Deploy Capability 8 (Auto-Merge with 5-condition matrix) + human gates

- [ ] Build 5-condition evaluator (tests, security, pattern, branch rules, author verification)
- [ ] Implement pattern classifier (docs-only, test-only, semver, safe-deps)
- [ ] Add GPG signature validation + trusted author list
- [ ] Create Slack approval workflow (human-in-loop for DRAFT PRs)
- [ ] Test false-positive rate (<5% target)
- [ ] Audit logging (all merge decisions logged with timestamp + reason)

**Rollout:** Opt-in per repo; default = disabled

---

### W9–W10 (Week 9–10): Threat Modeling + Incident Response

**Goals:** Deploy Capability 9 (Threat Modeling) + Capability 10 (Incident Response)

- [ ] Build STRIDE analyzer (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation)
- [ ] Generate attack surface maps (data flow diagrams)
- [ ] Implement root cause analysis (commit blame chain + GitHub issue linking)
- [ ] Build rollback candidate ranker (safety scores + dependency ordering)
- [ ] Create threat JSON schema + risk scorecard markdown
- [ ] Incident response runbook template (auto-generated per repo)

**Rollout:** Security team pilot (2–3 repos); feedback 1 week

---

### W11–W12 (Week 11–12): Transactional Rollback Orchestration

**Goals:** Deploy Capability 11 (Transactional Rollback) + full Fase 2 integration

- [ ] Build multi-repo rollback orchestrator (dependency-aware sequencing)
- [ ] Implement pre-rollback state verification (snapshot commits, branch states)
- [ ] Add post-rollback verification (CI re-run, health checks)
- [ ] Require explicit human approval (2-factor + approval chain)
- [ ] Audit logging (full rollback transcript)
- [ ] Test disaster recovery scenario (simulate 5-repo cascade failure)

**Rollout:** Staged (low-risk repos first); production readiness review

---

### Fase 2 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Threat detection accuracy** | >95% precision, <10% false positives | Test against OWASP benchmark corpus |
| **Auto-merge adoption** | >60% of eligible PRs auto-merged | GitHub webhook telemetry |
| **Security escalation time** | <5 min from detection to Slack | Slack message timestamp vs. scan trigger |
| **Incident RCA turnaround** | <10 min from request to root cause | Internal benchmark (manual vs. agent) |
| **Rollback success rate** | 100% (no failed rollbacks) | Post-execution state verification |
| **User confidence (NPS)** | >7/10 in security/DevOps teams | Quarterly survey |

---

## FUTURE ROADMAP (v4.3+ Beyond Fase 2)

- [ ] **GitLab support** (in addition to GitHub)
- [ ] **Bitbucket API integration** (Atlassian shops)
- [ ] **Advanced merge strategy advisor** (rebase-vs-merge ML model)
- [ ] **Automated refactoring suggestions** (AST-based code transforms)
- [ ] **Cross-org dependency tracking** (Manta + external repos)
- [ ] **AI-driven commit message generation** (semantic conventional commits)
- [ ] **Custom STRIDE templates** (industry-specific threat modeling: fintech, healthcare, infra)
- [ ] **Chaos engineering integration** (rollback safety testing)

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-26 | **Fase 1:** 6 core capabilities, GitHub MCP, Sonnet tier, escalation to Opus |
| 2.0.0 | 2026-07-26 | **Fase 2:** 5 new capabilities (threat detection, auto-merge, threat modeling, incident response, rollback); expanded escalation (security→Slack, CRITICAL→approval, threats→security-eng); AST analysis (45–120s latency); cost $0.50/call; roadmap W5–W12 |

