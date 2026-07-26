# FASE 4 ROADMAP — Advanced Optimization & Multi-Platform Expansion

**Git Evolution Suite Post-Production Strategy**

Version: **v1.0.0 (draft)**  
Status: **Ready for Fase 4 Kickoff Planning**  
Date: 2026-09-13  
Authors: Manta Maestro (Agente GitOps), Manta 16 (Arquiteto IA)

---

## FASE 4 OVERVIEW

### Strategic Vision

Fase 4 extends the Git Evolution Suite beyond single-platform (GitHub) automation into a **Multi-Platform, Observability-First, Advanced-Intelligence** ecosystem. Post-Fase 3 (full ML automation & chaos engineering on GitHub), Fase 4 targets:

- **Market expansion**: GitLab, Bitbucket, Gitea self-hosted support
- **Code intelligence**: AST-based refactoring engine with language coverage (Python, Java, TypeScript, Go)
- **Observability**: OpenTelemetry traces, custom dashboards, anomaly detection
- **Advanced ML**: 50-feature ensemble (from 31), confidence intervals, active learning

### Timeline

| Phase | Period | FTE-Weeks | Focus |
|-------|--------|-----------|-------|
| Planning | W17–W18 (Oct 1–14) | 4 | Architecture design, stakeholder alignment, API contracts |
| Implementation | W19–W24 (Oct 15–Dec 9) | 12 | Multi-platform routing, refactoring engine, observability, ML expansion |
| **Total** | **W17–W24** | **16 FTE-weeks** | **Advanced Optimization & Multi-Platform** |

### Budget & Resources

| Category | Amount | Notes |
|----------|--------|-------|
| **Dev effort** | 16 FTE-weeks | Senior backend (4), ML eng (3), DevOps (2), QA (2), PM (1), Arch (1), Intern (1), API expert (1), 1 floating |
| **ML training** | $8K–12K | 100+ additional repos, quarterly retraining infra |
| **Infrastructure** | +$2K/month | OTel collector, Jaeger, ClickHouse, custom dashboards |
| **Cloud compute** | +$5K–8K | Parallel CI runners for multi-platform testing |
| **External services** | $3K–5K | GitLab/Bitbucket API quotas, code intelligence APIs |
| **Contingency** | $15K | Risk buffer (14%) for scope creep |
| **TOTAL BUDGET** | **$120K–180K** | Blended cost (salary + infrastructure + external) |

### Success Criteria

- Multi-platform live: ≥3 platforms (GitLab, Bitbucket, Gitea)
- Auto-refactoring: ≥90% precision (human approval rate)
- Observability: 100% merge tracing coverage
- ML model: ≥93% quarterly accuracy (moving average)
- Adoption: 10+ organizations on Fase 4 by Q4 2026

---

## CAPABILITY PILLARS — 4x EXPANSION

### Pillar A: Multi-Platform Support

**Goal**: Extend merge automation & intelligence to GitLab, Bitbucket Cloud/Data Center, and Gitea.

#### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Unified Agent Interface                      │
│              (Platform-agnostic routing & intake)                │
└──────┬──────────────────┬──────────────────┬────────────────────┘
       │                  │                  │
   ┌───▼────┐        ┌───▼─────┐       ┌───▼──────┐
   │ GitHub │        │ GitLab  │       │ Bitbucket│
   │ Router │        │ Router  │       │  Router  │
   │(Exists)│        │(New)    │       │ (New)    │
   └───┬────┘        └───┬─────┘       └───┬──────┘
       │                 │                  │
   ┌───▼────────────────────────────────────▼─────────────────┐
   │  Platform Abstraction Layer (PAL)                         │
   │  - Webhook normalization (push, PR/MR, CI events)         │
   │  - VCS API adapter (create checks, merge, deploy)         │
   │  - CI/CD pipeline parser (GitHub Actions, GitLab CI, BB)  │
   └───┬────────────────────────────────────────────────────────┘
       │
   ┌───▼────────────────────────────────────────────────────────┐
   │  Unified ML Confidence Engine (Existing Fase 3 infra)      │
   │  - 50-feature ensemble (replaces 31)                       │
   │  - Platform-specific features (merge commit size, etc)     │
   └────────────────────────────────────────────────────────────┘
```

#### Key Features

**A1: GitLab CI/CD Integration**
- Native `.gitlab-ci.yml` parsing (YAML DSL)
- Issue→MR auto-linking (metadata extraction)
- Pipeline artifact preservation on merge
- Variable secret masking compliance (CI_JOB_TOKEN)
- Namespace-scoped permissions enforcement
- Status check mapping: GitHub Actions → GitLab CI (compatibility layer)

**A2: Bitbucket Cloud & Data Center**
- Repository sync (cloud to on-prem Data Center)
- PR review requirement automation (condition matchers)
- Jira integration passthrough (link sync, transition triggers)
- Server-side hooks for pre-merge validation
- Custom webhook delivery with signature verification
- Multi-workspace support (org hierarchy modeling)

**A3: Gitea & Self-Hosted Compatibility**
- Gitea API v1 support (PR, workflow hooks, deployments)
- SSH key + HTTPS auth fallback
- Minimal external dependency (single binary, SQLite/PostgreSQL)
- On-prem VCS discovery via API scan
- Firewall-friendly mode (webhook polling fallback)

**A4: Unified Platform Router**
- Smart dispatch based on repo URL pattern (github.com, gitlab.com, bitbucket.org, gitea.domain.com)
- Fallback routing (if GitLab down, use read-only mode)
- Platform feature capability matrix (merge via API vs. CLI)
- Graceful degradation per platform

#### Skill Specification

**`git-multi-platform-router.md` v1.0**
- 25-section comprehensive spec
- Platform detection heuristics
- API adapter interfaces (4x: GitHub, GitLab, Bitbucket, Gitea)
- Webhook normalization schema (push, MR/PR, deploy events)
- Routing decision tree (30+ decision points)
- Testing matrix: 5 platforms × 12 workflows = 60 test cases

---

### Pillar B: Advanced Code Intelligence

**Goal**: Introduce AST-based refactoring, code smell detection, and technical debt estimation.

#### Supported Languages

| Language | Refactoring Scope | Code Smell Rules | Status | ETA |
|----------|-------------------|-----------------|--------|-----|
| **Python** | PEP 8 compliance, type hints (via Pyright), docstrings | 15 rules (long methods, duplicate blocks, unused imports) | MVP | W22 |
| **Java** | Getter/setter extraction, name standardization, try-catch consolidation | 12 rules (God classes, long parameter lists, cyclomatic complexity) | MVP | W22–W23 |
| **TypeScript** | Unused import cleanup, interface generation, type narrowing | 18 rules (any-type usage, implicit returns, missing strict checks) | MVP | W22 |
| **Go** | Error handling patterns (defer vs. explicit), interface extraction | 10 rules (naked returns, error shadowing, goroutine leaks) | MVP | W23 |
| **Rust** | Ownership simplification, lifetime elision, idiomatic pattern matching | 8 rules (unsafe blocks, panics, unwrap chains) | Future (Q1 2027) | TBD |

#### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│            Code Refactoring Engine (CRE)                     │
│                                                               │
│  1. Language Detection (shebang, file ext, magic bytes)      │
│  2. Tokenization & AST Construction (via tree-sitter)       │
│  3. Static Analysis Passes (semantic, control flow)          │
│  4. Pattern Matching (code smell library)                    │
│  5. Refactoring Recommendation Generation                    │
│  6. Diff Generation & Validation (compile check)            │
│  7. Confidence Scoring (pattern match + test coverage)       │
│  8. Human Review Workflow (approval gate)                    │
└──────────────────────────────────────────────────────────────┘
       │                          │                     │
   ┌───▼────┐              ┌────▼─────┐          ┌────▼──────┐
   │ tree-   │              │ Semgrep  │          │ SonarQube │
   │ sitter  │              │ (OSS)    │          │ (optional)│
   │ parser  │              │ rules    │          │ enterprise│
   └─────────┘              └──────────┘          └───────────┘
```

#### Key Features

**B1: Python AST Refactoring**
- PEP 8 style compliance (line length, naming conventions, whitespace)
- Type hint injection (leveraging Pyright inference)
- Docstring standardization (Google/NumPy style auto-conversion)
- Import optimization (removal of unused, sorting per isort rules)
- Dead code elimination (variables, functions, classes)
- Complexity reduction (extract long methods, consolidate conditionals)

**B2: Java Refactoring**
- Getter/setter auto-extraction (with field reordering)
- Naming convention standardization (camelCase enforcement)
- Try-catch consolidation (consolidate identical catch blocks)
- Lambda expression introduction (where applicable)
- Null-safety patterns (Optional<T> substitution where safe)
- Access modifier tightening (public → private where possible)

**B3: TypeScript Refactoring**
- Unused import cleanup (with import ordering per eslint-plugin-import)
- Interface generation (extract from object literals with ≥3 usages)
- Type narrowing (explicit type guards vs. implicit)
- Explicit return types (for all exported functions)
- Any-type elimination (replace with unknown or more specific types)
- Strict mode compliance (strict null checks, strict function types)

**B4: Go Refactoring**
- Error handling patterns (explicit checks vs. defer chains)
- Interface extraction (when 3+ types implement same methods)
- Goroutine leak prevention (sync.WaitGroup + context patterns)
- Idiomatic naming (SingleLetter → FullName where appropriate)
- Defer order analysis (potential panic-on-panic edge cases)
- Resource cleanup verification (file/conn close calls)

**B5: Code Smell Detection & Scoring**

Technical Debt Score (0–100):
```
TDS = (Σ smell_weight × count) / total_lines × 100

Example thresholds:
- TDS > 70: "Refactor immediately" (blockers for merge)
- TDS 50–70: "Schedule refactoring" (merge allowed, tracked)
- TDS 30–50: "Low-priority" (informational)
- TDS < 30: "Negligible" (ignore)
```

**B6: Time-to-Refactor Estimation**

```
EstimatedTime = (Σ smell_complexity × language_velocity_factor) 
              × (1 + developer_skill_adjustment) 
              / team_parallelism_factor

Language velocity factors (task points per hour):
- Python:     8 points/hr
- Java:       6 points/hr
- TypeScript: 7 points/hr
- Go:         5 points/hr (lower due to goroutine/memory safety complexity)
```

#### Skill Specification

**`git-code-refactoring-engine.md` v1.0**
- 35-section comprehensive spec
- AST patterns for each language (Python, Java, TypeScript, Go)
- Code smell library (55 rules, weighted severity)
- Diff validation strategy (syntax checks, compile verification)
- Human approval workflow (comment-based gate with bot commands)
- Rollback procedures (revert via API if merge pre-approved)
- Testing matrix: 4 languages × 50 code patterns = 200 test cases

---

### Pillar C: Observability & Telemetry

**Goal**: Instrument all Git Evolution Suite operations with traces, metrics, and logs; enable anomaly detection.

#### Stack Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Application Layer (Git Evolution Suite)                      │
│  - Merge decisions, refactoring ops, platform APIs            │
│  - All instrumented with OpenTelemetry SDK (Python, JS)       │
└────────────┬─────────────────────────────────┬────────────────┘
             │                                 │
        ┌────▼──────────────────────────────────▼──────┐
        │      OpenTelemetry Collector Agent (OTLP)    │
        │  - Batching, sampling (10%), rate limiting    │
        │  - Protocol: gRPC (HTTP/2) + protobuf        │
        └────┬──────────────────────────────────┬───────┘
             │ Traces              │ Metrics  │ Logs
        ┌────▼────────┐      ┌────▼────┐  ┌───▼──┐
        │  Jaeger      │      │Prometheus│  │Loki  │
        │  (distributed│      │ (metrics)│  │(logs)│
        │   tracing)   │      │          │  │      │
        └────┬────────┘      └────┬────┘  └───┬──┘
             │                    │           │
        ┌────▼────────────────────▼───────────▼───┐
        │  ClickHouse (Time-Series OLAP DB)       │
        │  - 1yr retention, 5-min pre-aggregation │
        │  - Billions of events/day capacity       │
        └────┬────────────────────────────────────┘
             │
        ┌────▼──────────────────────────────────┐
        │  Grafana (Custom Dashboards + Alerts)  │
        │  - Git Merge Analytics                 │
        │  - ML Model Health                     │
        │  - Platform Availability               │
        │  - Anomaly Detection (ML-based)        │
        └───────────────────────────────────────┘
```

#### Key Features

**C1: Distributed Tracing**

Spans instrumented for every operation:

| Operation | Span ID Format | Duration Baseline | SLA |
|-----------|---|---|---|
| Merge decision (ML inference) | trace:merge:{repo}:{pr_id} | 5–45 sec | <100ms (p95) |
| Platform API call (create check) | trace:platform:{platform}:{op} | 1–5 sec | <1s (p95) |
| AST refactoring (parse+analysis) | trace:refactor:{lang}:{file} | 100–500 ms | <200ms (p95) |
| Chaos test scenario | trace:chaos:{scenario_id} | 30–180 sec | <5m (p95) |
| Webhook ingest & processing | trace:webhook:{platform}:{event_type} | 100–1000 ms | <500ms (p95) |

**C2: Custom Dashboards**

**Git Evolution Suite Control Plane**
- Real-time merge velocity (30-min rolling window)
- Platform availability heatmap (GitHub, GitLab, Bitbucket, Gitea)
- ML model confidence distribution (histogram, 5-point bins)
- Merge-day-of-week pattern (heatmap, identify slowdowns)
- Refactoring engine throughput (files/min, languages, success rate)
- Incident response timeline (chaos test durations, SLO attainment)

**ML Model Health Dashboard**
- Feature importance ranking (top 15 features, updated daily)
- Model accuracy trend (30-day rolling, ensemble vs. baselines)
- Prediction latency (p50, p95, p99 over 1-hour windows)
- Confidence interval width (narrowing = data abundance confidence)
- Retraining cadence & data freshness (days since last retrain)
- Active learning priority queue (top 20 borderline cases)

**Cost Attribution Dashboard**
- Cost per merge (compute + ML + platform API calls, $)
- Cost by platform (GitHub, GitLab, Bitbucket, Gitea breakdown)
- Cost by team/org (multi-tenant attribution)
- Compute resource utilization (vCPU-hours, memory-hours, GPU-hours)
- Model inference cost trend (cost/1000 inferences)

**C3: Anomaly Detection**

Unsupervised learning (isolation forests, DBSCAN) applied to:

| Signal | Baseline | Anomaly Threshold | Response |
|--------|----------|-------------------|----------|
| Merge success rate | 92–95% | <85% | Alert ops, disable ML confidence gate, manual review |
| Merge latency (p95) | 45–60 sec | >180 sec | Page on-call, investigate API degradation |
| Author commit frequency | μ ± 2σ (weekly) | 5σ outlier | Investigate potential account compromise (security) |
| PR merge-time distribution | 4–24 hours (modal) | >72h single PR | Escalate (merged after long delay, possible rework) |
| Refactoring rejection rate | 5–10% | >30% | Audit refactoring rules (false positives) |
| Test coverage drop | Δ < -2% per day | Δ < -5% per day | Halt auto-merges, require manual review |

**C4: Audit Trail (Compliance)**

Immutable log of all merge decisions, refactorings, and platform actions:

```
AuditEvent = {
  timestamp: ISO 8601,
  actor: (automated_agent | human_approver),
  action: (merge | refactor_applied | chaos_test | revert),
  resource: {repo, branch, pr_id},
  decision_details: {
    ml_confidence: float,
    rule_name: str,
    evidence: [str]
  },
  outcome: (success | failure),
  error_detail: (optional str)
}
```

Retained for 3 years, queryable via Grafana (audit trail plugin).

#### Skill Specification

**`git-observability-stack.md` v1.0**
- 40-section comprehensive spec
- OpenTelemetry instrumentation checklist (25+ spans)
- Trace sampling strategy (adaptive sampling based on error rate)
- Metrics schema (50+ KPIs, dimensional aggregation)
- Dashboard specs (4x dashboards, 15+ panels each)
- Alerting rules (30+ alert conditions, severity levels)
- Anomaly detection algorithms (isolation forest params, thresholds)
- On-call escalation playbooks (page duration, resolution time targets)
- Compliance & retention policies (GDPR, SOC 2 audit trail)
- Testing: synthetic load testing (10 concurrent workflows) with telemetry validation

---

### Pillar D: Advanced ML Features

**Goal**: Increase ML ensemble from 31 to 50 features, add confidence intervals, implement active learning.

#### ML Architecture (Fase 4 Enhancement)

```
Current (Fase 3):  31 features, single-point prediction
Fase 4 target:    50 features, confidence intervals, active learning

┌─────────────────────────────────────────────────────────────┐
│           Feature Engineering (50 features)                  │
│                                                               │
│  Existing (31):                                              │
│  - Code (SLOC, complexity, churn, tech debt score)    [8]   │
│  - Author (commits, merge count, test-writing ratio) [6]    │
│  - Repository (age, language diversity, test cov)    [5]    │
│  - Temporal (day-of-week, time-of-day, sprint phase) [4]    │
│  - CI/CD (test pass rate, build time, flakiness)     [5]    │
│  - Platform (API health, queue depth, current load)  [3]    │
│                                                               │
│  New (19) in Fase 4:                                         │
│  - Author Skill (code review defect correlation)     [4]    │
│  - Deployment (post-merge failures, rollback freq)   [3]    │
│  - Peer Review (comment sentiment, approval speed)   [4]    │
│  - Cross-repo (dependency depth, merge sequencing)   [3]    │
│  - Platform-specific (GitLab MR size, BB reviewer set) [5]  │
└─────────────────────────────────────────────────────────────┘
         │                                  │
         │                    ┌─────────────▼─────────────┐
         │                    │  Feature Selection (RFE)  │
         │                    │  Drop low-variance (<1%)   │
         │                    │  Keep ≥45 high-signal      │
         │                    └──────────────┬─────────────┘
         │                                   │
    ┌────▼───────────────────────────────────▼───────────────┐
    │      Ensemble (50-feature input)                        │
    │  65% Gradient Boosted Tree (XGBoost v2.1)             │
    │  25% Neural Net (2-hidden-layer, 128→64→output)       │
    │  10% Calibrated Linear (logistic regression, Platt)    │
    └────┬───────────────────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────────────────┐
    │  Confidence Interval Estimation                       │
    │  Method: Quantile regression (0.05, 0.50, 0.95)     │
    │  Output: P_merge, CI_lower, CI_upper (95% nominal)   │
    │  Confidence is width(CI), not model agreement        │
    └──────────────────────────────────────────────────────┘
```

#### Key Features

**D1: 50-Feature Ensemble**

New feature categories (19 features):

**Author Skill Level**
```
skill_score = Σ (successful_merges / total_merges) × defect_weight
              × (code_review_approvals / total_reviews)
            × (test_coverage_added / total_files)

Classes: Novice (<40%), Proficient (40–75%), Expert (>75%)
Impact on model: Author defect correlation (if expert, +3% merge success)
```

**Deployment & Stability**
```
post_merge_error_rate = failures_in_first_hour / total_deploys
rollback_frequency = rollbacks_past_30_days / deploys_past_30_days
stability_score = 1 - (post_merge_error_rate + rollback_frequency)
```

**Peer Review Dynamics**
```
review_sentiment = avg(comment_polarity[-1, 1]) over past 20 reviews
approval_latency = avg(time_to_approval_minutes) for author
peer_trust = (approvals_by_author / total_peer_code_reviews) in org
```

**Cross-Repo Dependency Graph**
```
dependency_depth = max(hop_count(PR_repo → downstream_repos))
parallel_merge_safety = (concurrent_merges_same_chain / avg_concurrent) risk score
merge_sequence_conflict = (conflict_likelihood if merged_before_peer_branch)
```

**Platform-Specific Features**

GitLab (new features for platform expansion):
- MR description length (→ planning quality signal)
- Draft MR auto-convert duration (→ readiness)
- Approver diversity (number of unique reviewers)

Bitbucket:
- Server-side hook validation latency
- Jira issue type (correlates with merge success)
- Reviewer conflict-of-interest flags

Gitea:
- Self-hosted CI runner availability
- Network latency (API response times)
- Repo size (small repos = faster, less risky)

**D2: Confidence Intervals (95% Nominal)**

Rather than point prediction, Fase 4 returns a distribution:

```
merge_decision = {
  prediction: 0.87,                  # P(success)
  confidence_interval: {
    lower: 0.79,                     # 2.5th percentile
    upper: 0.93                      # 97.5th percentile
  },
  interval_width: 0.14,              # Indicator of uncertainty
  confidence_category: "HIGH"        # if width < 0.10
}

Interpretation:
- If width < 0.08: "Very confident" → auto-merge at threshold 0.75
- If width 0.08–0.12: "Confident" → auto-merge at threshold 0.85
- If width > 0.12: "Uncertain" → require human review, lower threshold 0.92
```

**D3: Active Learning & Human Feedback Loop**

Prioritize human feedback on borderline cases:

```
Active learning priority queue:
1. Rank all recent merges by |P(success) - 0.5|
   (cases closest to 50% confidence first)
2. For top 50 borderline cases:
   - Request human feedback: "Was this merge good? Why?"
   - Capture feedback in tbl_active_learning_feedback
3. Weekly retraining incorporates:
   - New labeled data from human feedback
   - Error analysis (merges where prediction was wrong)
   - Emerging patterns (new code change styles, platform changes)
4. Quality metrics:
   - Human feedback acceptance rate (% useful feedback)
   - Model improvement per feedback (RMSE delta)
   - Diversity of feedback (org-wide, not just top reviewers)
```

**D4: Quarterly Retraining Cadence**

```
Timeline:
Q1 2027:
  - Retraining frequency: Monthly (from quarterly)
  - Feature count expansion: 50 → 60 (add emerging patterns)
  - Model diversity: Add LSTM for sequential patterns
  - Accuracy target: ≥94%

Quarterly Retraining Process:
Week 1: Data collection (100+ repos, 500+ recent merges)
Week 2: Feature computation (500+ features, 50 selected)
Week 3: Model training (3 ensemble members, hyperparameter tuning)
Week 4: Validation (test set 20%, A/B test vs. previous model, shadow mode)
Week 5: Deployment (canary 5%, then full rollout; fallback if AUROC <0.92)
```

#### Skill Specification

**`git-ml-advanced-scoring.md` v1.0**
- 45-section comprehensive spec
- Feature engineering (50 features, with derivation formulas)
- Ensemble architecture (50-feature input, 3-member ensemble)
- Confidence interval methodology (quantile regression, calibration)
- Active learning algorithm (priority queue, human feedback workflow)
- Quarterly retraining playbook (data collection, validation, canary deployment)
- Model monitoring (accuracy tracking, feature importance drift detection)
- Fallback mechanisms (timeout >5s, revert to 0.75 threshold)
- Testing: 100+ repos for quarterly retraining validation

---

## DETAILED FEATURE LIST — 12 CAPABILITIES

### Fase 4 Feature Backlog (MVP Scope)

| # | Capability | Pillar | MVP | Priority | Effort | Target Week |
|---|------------|--------|-----|----------|--------|------------|
| 1 | GitLab issue↔MR auto-linking | A | Yes | P0 | 2 days | W19 |
| 2 | Bitbucket server-side pre-merge hooks | A | Yes | P0 | 3 days | W21 |
| 3 | Python AST refactoring (PEP 8 + types) | B | Yes | P0 | 5 days | W22 |
| 4 | Java getter/setter extraction | B | Yes | P1 | 4 days | W22–W23 |
| 5 | TypeScript unused import cleanup + types | B | Yes | P0 | 3 days | W22 |
| 6 | Go error handling patterns | B | Yes | P1 | 4 days | W23 |
| 7 | Cost per merge tracking | C | Yes | P1 | 2 days | W23 |
| 8 | Author skill level estimation | D | Yes | P1 | 3 days | W23 |
| 9 | Merge time-of-day optimization | D | Yes | P2 | 2 days | W24 |
| 10 | Cross-repo dependency graph | A/D | Yes | P2 | 6 days | W23–W24 |
| 11 | Weekly ML model retraining | D | Yes | P0 | 5 days | W24 |
| 12 | A/B testing framework (for heuristics) | C/D | Yes | P2 | 4 days | W24 |

---

### Feature 1: GitLab Issue↔MR Auto-Linking

**Goal**: Automatically link GitLab issues to merge requests, enabling metadata flow and cross-reference management.

**Implementation**:
```
GitLab MR Webhook (on merge):
  {
    "object_kind": "merge_request",
    "object_attributes": {
      "iid": 42,
      "title": "Fix: address validation module",
      "description": "Closes #123\nImplements feature #456"
    }
  }

Parser:
  - Regex: `(closes|fixes|resolves|closes|implements) #(\d+)`
  - Extract: [123, 456]
  - Call: GitLab API POST /projects/{id}/issues/{issue_id}/notes

Result:
  - Issue #123 gains link: "closed by !42"
  - Issue #456 gains link: "implemented by !42"
  - Enables burn-down tracking, impact analysis
```

**Acceptance Criteria**:
- Parse MR description + commit messages for issue refs
- Handle multiple issue links (≤10 per MR)
- Bidirectional linking (issue→MR and MR→issue)
- Latency <500ms (async webhook processing)

---

### Feature 2: Bitbucket Server-Side Pre-Merge Hooks

**Goal**: Run validation logic on Bitbucket Data Center via server-side hooks before merge commits.

**Implementation**:
```
Server-side hook script (bash, executed by Bitbucket):
  1. Clone PR branch + main branch (local)
  2. Run ML confidence model (Python):
     - Extract merge features from local repo
     - Call endpoint: POST /ml/predict (local service)
     - Get confidence score + decision
  3. If confidence < 0.80: ABORT merge with reason
  4. If confidence ≥ 0.80 & tests pass: ALLOW merge
  5. Log decision to audit trail (Supabase)

Configuration (bitbucket-server-hook.properties):
  trigger.on=pr:merged
  script.location=/opt/bitbucket/hooks/git-evolution-pre-merge.sh
  timeout=30000ms
  max_retries=2
```

**Acceptance Criteria**:
- Hook execution latency <30s (within Bitbucket timeout)
- Graceful degradation if ML service unavailable (allow merge)
- Hook logs visible in Bitbucket PR UI
- Audit trail captures hook decision + evidence

---

### Feature 3: Python AST Refactoring (PEP 8 + Type Hints)

**Goal**: Automatically refactor Python code for style compliance and type hint addition.

**Implementation**:
```
Refactoring Pipeline:
  1. Parse: Use ast module (built-in) or tree-sitter (C ext)
     - Build full AST of *.py files in PR
  2. Analysis Passes (4x):
     a. Style Check (PEP 8): line length, naming conventions
     b. Type Inference: Use Pyright LSP → infer types
     c. Import Optimization: Remove unused, sort per isort
     d. Complexity: Identify long functions (>20 lines), extract
  3. Refactoring Rules (20+ rules):
     - Expand 1-char vars (x → counter)
     - Add type hints (def foo(x): → def foo(x: int) -> str:)
     - Standardize docstrings (convert Sphinx → Google style)
     - Consolidate imports (from x import y, z vs. from x import *)
  4. Diff Generation:
     - Preserve formatting (use black for consistency)
     - Per-file diffs shown in PR comment
  5. Human Review:
     - Bot comment with diffs + severity
     - Human approves via "@bot approve refactoring"
     - Apply if approved, merge PR

Example Refactoring:
  Before:
    def f(x,y):
      z=x+y
      return z

  After:
    def f(x: int, y: int) -> int:
      """Add two numbers.
      
      Args:
        x: First number.
        y: Second number.
      
      Returns:
        Sum of x and y.
      """
      result = x + y
      return result
```

**Acceptance Criteria**:
- PEP 8 compliance (linting score 100/100 post-refactor)
- Type hint coverage ≥95% (all public functions + methods)
- No breaking changes to logic (syntax-only)
- Human approval required before apply
- Rollback available (revert commit)

---

### Feature 4: Java Getter/Setter Extraction

**Goal**: Automatically extract and generate getter/setter methods, reducing boilerplate.

**Implementation**:
```
AST Analysis (ANTLR Java parser):
  1. Identify fields (private int age, String name)
  2. Count field usages in methods
  3. If field is read/written >3 times: candidate for getter/setter
  4. Generate methods (JavaBeans convention):
     - Getter: public int getAge() { return age; }
     - Setter: public void setAge(int age) { this.age = age; }
  5. Refactor: Replace direct field access with getter/setter calls
  6. Apply in order: fields defined → getters → setters → callers updated

Example:
  Before:
    class Person {
      private String name;
      private int age;
      
      public Person(String name, int age) {
        this.name = name;
        this.age = age;
      }
      
      public void printInfo() {
        System.out.println(name + " is " + age);
      }
    }
  
  After:
    class Person {
      private String name;
      private int age;
      
      public Person(String name, int age) {
        this.name = name;
        this.age = age;
      }
      
      public String getName() { return name; }
      public void setName(String name) { this.name = name; }
      public int getAge() { return age; }
      public void setAge(int age) { this.age = age; }
      
      public void printInfo() {
        System.out.println(getName() + " is " + getAge());
      }
    }
```

**Acceptance Criteria**:
- Getter/setter naming follows JavaBeans convention
- Compile checks pass post-refactor
- No logic changes (direct access → method calls only)
- IDE quick-fix compatible (can undo easily)

---

### Feature 5: TypeScript Unused Import Cleanup + Type Narrowing

**Goal**: Remove unused imports and enforce strict type checking in TypeScript.

**Implementation**:
```
Tree-sitter AST (TypeScript grammar):
  1. Parse: All import statements, usages (variable refs)
  2. Analyze:
     - For each import, check if symbol appears in code
     - If zero usages: mark for removal
     - If used but untyped: flag for type annotation
  3. Type Narrowing:
     - Identify any-type usages
     - Replace with unknown or specific type
     - Add type guards where needed
  4. Strict Mode Compliance:
     - Ensure all function returns are typed
     - Ensure all parameters are typed (no implicit any)
     - Enforce null checks (--strictNullChecks)

Example Refactoring:
  Before:
    import { foo, bar, unused } from './utils';
    import * as types from './types';
    
    function process(data: any): any {
      return foo(data);
    }
  
  After:
    import { foo } from './utils';
    import type { DataType } from './types';
    
    function process(data: DataType): DataType {
      return foo(data);
    }
```

**Acceptance Criteria**:
- All unused imports removed
- No breaking changes to exports/imports
- Strict type checks pass (tsconfig: strict=true)
- Tree-sitter parse succeeds (syntax valid)

---

### Feature 6: Go Error Handling Patterns

**Goal**: Standardize Go error handling (explicit checks vs. defer chains) and detect potential leaks.

**Implementation**:
```
Go AST Analysis (tree-sitter or go/parser):
  1. Identify defer statements + error checks
  2. Pattern matching:
     a. Naked returns in error-handling code → add variable names
     b. Missing error checks (func returns error, but not checked)
     c. Goroutine leaks (launched but no sync.WaitGroup)
     d. Resource leaks (file/conn open, no close in defer)
  3. Refactoring suggestions:
     - Consolidate error-handling defer chains
     - Add explicit error variable names
     - Insert sync.WaitGroup for goroutines
     - Add defer file.Close() after file open

Example:
  Before:
    func readFile(path string) ([]byte, error) {
      file, err := os.Open(path)
      // Missing error check!
      defer file.Close()
      return ioutil.ReadAll(file)
    }
    
    func startWorker() {
      go func() {
        // Long-running task
        for {
          work()
        }
      }()
      // Goroutine never cleaned up (leak)
    }
  
  After:
    func readFile(path string) ([]byte, error) {
      file, err := os.Open(path)
      if err != nil {
        return nil, err
      }
      defer func() {
        if err := file.Close(); err != nil {
          log.Printf("close error: %v", err)
        }
      }()
      return ioutil.ReadAll(file)
    }
    
    func startWorker(ctx context.Context) {
      var wg sync.WaitGroup
      wg.Add(1)
      go func() {
        defer wg.Done()
        for {
          select {
          case <-ctx.Done():
            return
          default:
            work()
          }
        }
      }()
      wg.Wait()
    }
```

**Acceptance Criteria**:
- Error checks exist for all error-returning calls
- Defer statements ordered correctly (reverse LIFO)
- Goroutines cleaned up via context or WaitGroup
- Compile checks pass post-refactor

---

### Feature 7: Cost Per Merge Tracking

**Goal**: Calculate and track the cost of each merge operation (compute, ML, platform APIs).

**Implementation**:
```
Cost Attribution Model:
  Total Cost = Compute Cost + ML Cost + Platform API Cost + Storage Cost

  1. Compute Cost (AWS pricing):
     - ML inference: t3.medium (2 vCPU, 4 GB RAM) × duration (ms) → $0.0416/hour
     - Refactoring: c5.large (2 vCPU, 4 GB RAM) × duration (ms) → $0.085/hour
     - Observability: (trace ingestion + processing) → $0.30 per 1M spans
  
  2. ML Cost:
     - Model inference: 50 features × 3 ensemble members
       - XGBoost: ~5ms @ $0.0001/inference
       - Neural Net: ~10ms @ $0.0002/inference
       - Linear: ~1ms @ $0.00005/inference
       - Total: ~$0.0003/inference
  
  3. Platform API Cost:
     - GitHub: Free (no per-call cost)
     - GitLab: Free (self-hosted API)
     - Bitbucket Cloud: Free (self-hosted hooks)
     - Bitbucket Data Center: Free (on-prem)
     - But: webhook event ingestion (our infrastructure): $0.0001/event
  
  4. Storage Cost:
     - Audit trail log entry: 500 bytes @ $0.023 per GB/month
     - Daily merges: 1000 × $0.00003 = ~$0.03/day = $10/month
  
  Example Calculation:
    Merge decision:
      - Compute (inference): 25ms @ t3.medium = $0.000289
      - ML cost: 3 inferences × $0.0003 = $0.0009
      - Platform API: 3 calls (create check, update PR, merge) = free
      - Storage (audit): 1 entry × $0.00003 = $0.00003
      - Observability: 10 spans × $0.0000003 = $0.000003
    
    Total cost per merge: ~$0.00122 (~$1.22 per 1000 merges)

Tracking:
  - Per-merge cost logged to tbl_merge_costs (date, repo, cost_usd)
  - Dashboards show: Cost by org, by platform, by refactoring engine, trends
  - Cost chargeback (if multi-tenant): allocate to team/project
```

**Acceptance Criteria**:
- Cost calculation within ±5% of actual AWS billing
- Logged for all merges (100% coverage)
- Visible in cost attribution dashboard
- Monthly cost report generated automatically

---

### Feature 8: Author Skill Level Estimation

**Goal**: Estimate developer skill level based on code review data, defect correlation, and merge patterns.

**Implementation**:
```
Skill Score Calculation:
  skill_score = (successful_merge_rate × 0.4) 
              + (code_review_quality × 0.3)
              + (test_coverage_added × 0.2)
              + (defect_detection_speed × 0.1)

  Where:
  - successful_merge_rate = (merged / total_prs) × 100 [target: >90%]
  - code_review_quality = (approved_prs / reviewed_prs) × (low_defect_rate)
    = approval rate weighted by downstream defect count
  - test_coverage_added = (avg lines of test per line of code) [target: >1:1]
  - defect_detection_speed = (days to detect defect post-merge) [lower = better]

Classification:
  - Novice: skill_score < 40% → 1st/2nd PRs, needs review
  - Proficient: 40% ≤ skill_score < 75% → Regular PRs, trusted
  - Expert: skill_score ≥ 75% → Can approve own code, mentors others

Use Cases:
  1. ML Model Feature: Expert-authored PRs have +3% merge success bias
  2. Code Review Assignment: Route PRs from Novices to Experts
  3. On-Call Rotation: Bias toward Expert developers
  4. Merge Confidence Threshold: Expert (75%), Proficient (85%), Novice (95%)

Example Metrics (for org of 50 developers):
  - Alice (Expert, 87%): 200 merges, 98% success, 5 defects in 1yr, tests 1.2:1
  - Bob (Proficient, 62%): 45 merges, 91% success, 3 defects, tests 0.8:1
  - Charlie (Novice, 38%): 8 merges, 87% success, 2 defects (high rate for volume), tests 0.3:1
```

**Acceptance Criteria**:
- Skill score computed from ≥20 data points (merges, reviews, etc.)
- Classification accuracy ≥85% (validated against self-assessment survey)
- Updates weekly (sliding window of past 6 months)
- Used in ML model + merge decision logic

---

### Feature 9: Merge Time-of-Day Optimization

**Goal**: Analyze merge patterns by time-of-day and recommend optimal merge windows.

**Implementation**:
```
Time-of-Day Analysis:
  For each hour (0–23), compute:
    1. Success Rate: (successful_merges / total_merges_in_hour) × 100
    2. Latency (p95): percentile(merge_duration) for merges in hour
    3. Rollback Rate: (rollbacks_post_merge_in_hour / merges)
    4. Load (concurrent_merges): avg concurrent merges in hour
  
  Example results (UTC):
    08:00–09:00 UTC: 94% success, 42s latency, 1% rollback, 12 concurrent
    12:00–13:00 UTC: 89% success, 68s latency, 3% rollback, 24 concurrent (lunch dip)
    18:00–19:00 UTC: 87% success, 95s latency, 4% rollback, 8 concurrent (Europe EOD)
    02:00–03:00 UTC: 96% success, 28s latency, 0% rollback, 1 concurrent (quiet)

Recommendation:
  - Best windows: 02:00–06:00 UTC (low load, high success)
  - Avoid windows: 12:00–14:00 UTC (lunch effect), 18:00–20:00 UTC (Europe EOD)
  - For critical PRs: schedule merge during 08:00–10:00 UTC (normal hours, staffed)

Implementation:
  - Schedule merge job for recommended hour (async job queue)
  - If PR urgent: immediate merge, but alert on-call if outside good window
  - Reduce ML confidence threshold for off-hour merges (e.g., 95% instead of 85%)
```

**Acceptance Criteria**:
- Time-of-day heatmap generated weekly (success rate by hour)
- Recommendations provided via bot comment ("Best merge window: 08:00–10:00 UTC")
- Scheduled merges executed ±15 minutes of target time
- Impact measured: compare suggested vs. non-suggested merges (success rate delta)

---

### Feature 10: Cross-Repo Dependency Graph

**Goal**: Build and maintain a dependency graph across repositories, enabling sequenced merges and conflict detection.

**Implementation**:
```
Dependency Discovery:
  1. Scan all PR code changes for imports/requires:
     - Python: import foo, from foo import bar
     - Java: import com.foo.Bar
     - TypeScript: import { X } from '@org/lib'
     - Go: import "github.com/org/lib"
  
  2. Build directed graph:
     - Nodes: {repo, branch, pr_id}
     - Edges: {pr_a → pr_b} if pr_a's code is imported by pr_b
  
  3. Detect merge sequencing:
     - If pr_a → pr_b (dependency), require merge order: pr_a THEN pr_b
     - Compute safe merge sequence (topological sort)
     - Warn if merges are out of order (conflict risk)

Example (microservices):
  auth-service (PR#50: add OAuth token validation)
    ↓ (dependency)
  api-gateway (PR#120: use new token validation)
    ↓
  mobile-app (PR#310: use new gateway endpoints)

Correct merge order: #50 → #120 → #310
If #120 merges before #50: rollback risk, revert #120 or fast-follow #50

Implementation:
  - Build graph nightly (scan all open PRs)
  - On merge request: check sequence, warn via PR comment
  - Optional: auto-delay merge of pr_b if pr_a hasn't merged yet
  - Track cross-repo conflicts (post-merge integration tests)

Metrics:
  - Dependency graph size: (repos, edges) → identify heavily coupled services
  - Merge conflict rate by dependency: if high, refactor interface or add integration tests
```

**Acceptance Criteria**:
- Dependency graph accurate for ≥95% of PRs (validated by manual sampling)
- Merge sequence recommendations prevent conflicts (post-merge test pass rate ≥95%)
- No false positives for indirect dependencies (only direct imports counted)
- Performance: graph computation <5 minutes for 10-repo org

---

### Feature 11: Weekly ML Model Retraining

**Goal**: Establish automated, repeatable process for retraining the ML ensemble weekly (vs. quarterly in Fase 3).

**Implementation**:
```
Weekly Retraining Schedule (every Monday, 02:00 UTC):

Step 1 — Data Collection (10 min):
  - Query Supabase: select merges from past 7 days
  - Filter: ≥500 merges, ≥50 repos (statistical significance)
  - Outcome labels: success (no post-merge failures in 24h) vs. failure
  
Step 2 — Feature Computation (15 min):
  - For each merge, compute 50 features (code, author, repo, temporal, CI, platform)
  - Cache features to avoid recompute (feature store)
  - Remove outliers (>3σ deviation, likely data errors)
  
Step 3 — Model Training (20 min):
  - Split: 80% train, 20% test
  - Train ensemble:
    a. XGBoost (65% weight): 500 trees, max_depth=8, learning_rate=0.1
    b. Neural Net (25%): 2 hidden layers (128→64 neurons), dropout 0.2
    c. Logistic (10%): L2 regularization, Platt scaling for calibration
  - Hyperparameter tuning: Bayesian search (20 trials) on validation set
  
Step 4 — Validation (10 min):
  - Compute metrics on test set:
    * AUROC (area under ROC curve) → target ≥0.93
    * Precision @ 85% threshold → target ≥90%
    * Recall @ 85% threshold → target ≥85%
    * Calibration error → target <0.03
  - Compare to previous model: accept if AUROC delta > -0.01
  - A/B test: run old + new model on same test set
  
Step 5 — Deployment (5 min):
  - If validation passes:
    * Canary: Route 5% of merge requests to new model (shadow mode)
    * Monitor for 24 hours: accuracy, latency, false positive rate
    * If metrics OK: full rollout (100% of merges use new model)
  - If validation fails: alert on-call, revert to previous model, investigate
  
Step 6 — Monitoring & Feedback (ongoing):
  - Track model drift: weekly AUROC on holdout set (data freshness)
  - Log false positives/negatives: enable next week's retraining to improve
  - Weekly report: accuracy trend, feature importance changes, anomalies detected

Automation:
  - GitHub Actions workflow (scheduled, runs on infrastructure)
  - Logs: stored in Supabase (tbl_model_training_runs)
  - Alerts: Slack notification if training fails or accuracy drops >2%
```

**Acceptance Criteria**:
- Weekly retraining executes on schedule (99.5% success rate)
- Model performance tracked (AUROC, precision, recall logged)
- Canary deployment validated before full rollout
- Rollback to previous model if new model underperforms
- Operator runbook for manual retraining (if automated fails)

---

### Feature 12: A/B Testing Framework (for Heuristics)

**Goal**: Enable safe experimentation of new merge heuristics without impacting all users.

**Implementation**:
```
A/B Testing Harness:
  A = Control: Current merge heuristics (Fase 3 rules)
  B = Treatment: New experimental heuristic (Fase 4 candidate)

  For N% of PRs (configurable, start 5%):
    1. Compute decision via both A + B
    2. Store both decisions in tbl_ab_test_decisions
    3. Merge via A (control), log B decision (would-be outcome) for analysis
    4. Track post-merge outcome (success/failure)
    5. Compare: did B predict better than A?

Experiment Design:
  Sample size: 1000 merges per treatment (1 week of data, assumed)
  Significance: α=0.05 (95% confidence), β=0.20 (80% power)
  Metric: Lift in success rate
  
  Example:
    A (control): 93% success rate, 930 successes / 1000 merges
    B (treatment): 94.5% success rate, 945 successes / 1000 merges
    Lift: +1.5% (statistically significant, p < 0.05)
    Conclusion: Accept B, deploy to 100%

Heuristics to Experiment:
  1. "Increase ML confidence threshold to 0.90 for >50-file PRs"
  2. "Auto-merge only if author is Expert + peer reviewed"
  3. "Reduce merge window to business hours (08:00–18:00 UTC)"
  4. "New feature: cross-repo dependency checks"
  5. "Weighting: 55% XGBoost instead of 65%"

Workflow:
  1. Engineer proposes heuristic: PR to `.claude/experiments/{name}.yaml`
  2. Config:
     ```
     experiment_id: heuristic-confidence-threshold-v2
     description: "Test 0.90 confidence for large PRs"
     treatment:
       rule: "if file_count > 50: require confidence >= 0.90"
     sample_rate: 0.05  # 5% of PRs
     duration_days: 7
     success_metric: "merge_success_rate"
     target_lift: 0.01  # expect +1% improvement
     ```
  3. Run A/B test for 7 days (collect 1000 merges)
  4. Analyze results: generate report (success rate, confidence intervals, p-value)
  5. If lift significant: promote to default heuristic
     If not: archive experiment, try different approach

Analysis Dashboard:
  - Real-time A/B test results
  - Success rate chart (A vs. B over time)
  - Lift histogram (estimated lift + 95% CI)
  - Segment analysis (by repo, by author skill, by platform)
  - Early stopping (if clear winner before N=1000)
```

**Acceptance Criteria**:
- A/B testing framework deployed and tested (on toy data)
- Experiment configuration via YAML (simple, versionable)
- Results analysis automated (p-value, confidence interval computed)
- Early stopping rules implemented (sequential analysis, save resources)
- Rollout decision documented (why feature accepted/rejected)

---

## ROADMAP TIMELINE — W17–W24 (16 Weeks)

### Gantt Chart (ASCII)

```
FASE 4 TIMELINE — October 1 to December 9, 2026

┌─────────────────────────────────────────────────────────────────────┐
│                         Planning Phase (W17–W18)                    │
│ Oct 1 ·───────────────────────────────────────────────────────────··│
│        └─ Architecture design (4 days)                               │
│        └─ Stakeholder alignment (2 days)                             │
│        └─ API contract finalization (2 days)                         │
│        └─ Risk mitigation planning (1 day)                           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Implementation Phase (W19–W24)                    │
│                                                                       │
│  W19: Multi-Platform Routing (Oct 15–21)                            │
│  Oct 15 ·─────────────────────────────────────────────────────────· │
│         └─ Pillar A (PAL design) ████████                           │
│         └─ Feature 1: GitLab issue↔MR linking █████                │
│         └─ Platform router implementation ██████                    │
│                                                                       │
│  W20: GitLab Integration MVP (Oct 22–28)                            │
│  Oct 22 ·──────────────────────────────────────────────────────────·│
│         └─ GitLab CI/CD parser ████████                             │
│         └─ Webhook normalization ██████████                         │
│         └─ GitLab testing suite (E2E) █████                         │
│                                                                       │
│  W21: Bitbucket Integration (Oct 29–Nov 4)                          │
│  Oct 29 ·──────────────────────────────────────────────────────────·│
│         └─ Bitbucket API adapter ██████████                         │
│         └─ Feature 2: Server-side hooks ████████                    │
│         └─ Cloud + Data Center support █████                        │
│                                                                       │
│  W22: AST Refactoring Engine (Nov 5–11)                             │
│  Nov  5 ·──────────────────────────────────────────────────────────·│
│         └─ Pillar B (Python) ████████████                           │
│         └─ Feature 3: Python AST refactoring █████████              │
│         └─ Feature 5: TypeScript imports ███████                    │
│         └─ Code smell library (15 rules) ████                       │
│                                                                       │
│  W23: Java + Go + Observability (Nov 12–18)                         │
│  Nov 12 ·──────────────────────────────────────────────────────────·│
│         └─ Feature 4: Java refactoring ███████                      │
│         └─ Feature 6: Go error handling █████                       │
│         └─ Pillar C (OTel stack) █████████████                      │
│         └─ Feature 7: Cost tracking ██████                          │
│         └─ Dashboards MVP (4x) ████                                 │
│                                                                       │
│  W24: Advanced ML + Testing (Nov 19–25, + Dec 1–5 for slack)        │
│  Nov 19 ·──────────────────────────────────────────────────────────·│
│         └─ Pillar D (50-feature ensemble) █████████                 │
│         └─ Feature 8: Author skill estimation ██████                │
│         └─ Feature 9: Merge time-of-day opt. ███                    │
│         └─ Feature 10: Cross-repo deps ████████                     │
│         └─ Feature 11: Weekly retraining ██████████                 │
│         └─ Feature 12: A/B testing framework ███████                │
│         └─ Integration testing (all pillars) ██████                 │
│         └─ Security audit + hardening ████                          │
│                                                                       │
│  W25–W26: Cutover & Stabilization (Dec 6–19) — OPTIONAL buffer      │
└─────────────────────────────────────────────────────────────────────┘

Legend:
  ████ 1 FTE-day
  ██████████ 2.5 FTE-days
  ███████████████ 4 FTE-days

Critical Path (bottleneck items):
  1. Platform router (enables parallel: GitLab, Bitbucket, Gitea)
  2. ML feature engineering + retraining (blocks: confidence intervals, active learning)
  3. OTel integration (affects monitoring, decision transparency)

Parallel Work Streams (4 teams, 4 weeks simultaneous):
  Team 1: Multi-Platform (A1, A2, A3, A4)
  Team 2: Code Intelligence (B1, B2, B3, B4)
  Team 3: Observability (C1, C2, C3, C4)
  Team 4: Advanced ML (D1, D2, D3, D4)
```

### Weekly Milestones

| Week | Milestone | Completion % | Go/No-Go Gate |
|------|-----------|--------------|---------------|
| W17–W18 | Architecture design complete | 100% | Design review, stakeholder sign-off |
| W19 | Platform router implemented, GitLab linked | 40% | Router latency <100ms, E2E test pass |
| W20 | GitLab integration MVP tested | 65% | 5-repo pilot success rate >90% |
| W21 | Bitbucket integration MVP tested | 80% | Bitbucket hook latency <30s, no merge failures |
| W22 | Python + TypeScript refactoring working | 90% | Refactoring precision >90%, compile checks pass |
| W23 | Java, Go, cost tracking, observability MVP | 95% | Dashboards live, cost tracking within ±5% of actual |
| W24 | All features integrated, A/B testing live | 100% | Full regression testing pass, canary deployment ready |
| W25 (buffer) | Cutover to production | 100% | Rollout to 10+ organizations, SLA met |

---

## SUCCESS METRICS & ACCEPTANCE CRITERIA

### Pillar A: Multi-Platform Support

| Metric | Target | Acceptance Criteria |
|--------|--------|----------------------|
| GitLab adoption | ≥5 orgs live | 5+ organizations on platform, merge velocity >5/day |
| Bitbucket adoption | ≥3 orgs live | 3+ organizations live, data center + cloud supported |
| Gitea compatibility | 1 self-hosted tested | 1 on-prem instance functional, no API gaps |
| Platform router latency | <100ms | p95 routing decision time <100ms, no timeout errors |
| Webhook processing latency | <500ms | MR/PR events ingested and processed in <500ms |
| API adapter stability | 99.5% uptime | <4 hours downtime per month across all platforms |

### Pillar B: Advanced Code Intelligence

| Metric | Target | Acceptance Criteria |
|--------|--------|----------------------|
| Auto-refactoring precision | ≥90% | ≥90% of refactoring diffs are correct (no logic changes) |
| Language coverage | 4 languages | Python, Java, TypeScript, Go all working MVP |
| Compile check pass rate | 100% | All refactored code compiles/passes syntax checks |
| Code smell detection accuracy | ≥85% | 85% precision on known code smells (f1-score) |
| Human approval rate | ≥70% | 70%+ of refactoring recommendations approved by developers |
| Time-to-refactor accuracy | ±30% | Estimated refactoring time within ±30% of actual |

### Pillar C: Observability & Telemetry

| Metric | Target | Acceptance Criteria |
|--------|--------|----------------------|
| Merge trace coverage | 100% | All merges traced, full span hierarchy captured |
| OTel collector uptime | 99.9% | <8 hours downtime per month, no lost spans |
| Dashboard availability | 100% | All 4 dashboards available, <5s load time |
| Metric accuracy | ±2% | Cost tracking within ±2% of actual; latency p95 within ±5% |
| Anomaly detection false positive rate | <5% | <5% of anomalies are spurious; must be manually validated |
| Audit trail completeness | 100% | All merges, refactorings, chaos tests logged immutably |

### Pillar D: Advanced ML Features

| Metric | Target | Acceptance Criteria |
|--------|--------|----------------------|
| Feature count | 50 features | 50 features engineered and validated |
| ML model accuracy | ≥93% AUROC | Rolling 30-day average ≥0.93 (cross-validated) |
| Confidence interval width | <0.12 | 95% of intervals have width <0.12 (not too uncertain) |
| Calibration error | <0.03 | Predicted confidence matches actual success rate (within ±3%) |
| Weekly retraining success rate | ≥95% | 95% of weekly retraining cycles complete successfully |
| Active learning feedback rate | ≥60% | ≥60% of humans respond to active learning prompts |
| Model explainability (SHAP) | Top-10 features explain ≥70% variance | SHAP values computed; top 10 features contribute ≥70% to prediction |

### Overall Adoption & Business Metrics

| Metric | Target | Acceptance Criteria |
|--------|--------|----------------------|
| Organization adoption | ≥10 orgs on Fase 4 | 10+ organizations live on Fase 4 by Q4 2026 |
| Merge velocity increase | +15% vs. Fase 3 | Average merges/day increase by 15% (less waiting for reviews) |
| Developer satisfaction | NPS ≥40 | Net Promoter Score ≥40 (survey of 50+ users) |
| Defect rate post-merge | ≤3% | Post-merge failures within 24h ≤3% (down from 4% in Fase 3) |
| Cost per merge | ≤$0.002 | Total cost <$2 per 1000 merges (cloud + ML + platform) |
| Time-to-market reduction | 20% | Time from commit to production down 20% vs. Fase 3 |

---

## EFFORT & COST BREAKDOWN

### Team Composition (16 FTE-weeks total)

| Role | Count | FTE-weeks | Responsibilities |
|------|-------|-----------|------------------|
| Senior Backend Engineer | 4 | 16 | Platform routers (A), core ML infra (D), integration |
| ML Engineer | 3 | 12 | Feature engineering, model training (Pillar D), SHAP analysis |
| DevOps Engineer | 2 | 8 | OTel stack, dashboards, CI/CD automation, scaling |
| QA Engineer | 2 | 8 | E2E testing (all pillars), regression suites, chaos drills |
| Product Manager | 1 | 4 | Roadmap prioritization, stakeholder management, decisions |
| Architect | 1 | 4 | Design reviews, technical debt mitigation, risk assessment |
| Junior Developer | 1 | 4 | Code refactoring logic (Pillar B), test automation |
| **Floating** | **1** | **4** | Risk mitigation, scope creep, ad hoc support |
| **TOTAL** | **15** | **60 FTE-weeks** | **(16 weeks wall-clock = 4/15 ratio)** |

### Cost Breakdown

| Category | Amount | Notes |
|----------|--------|-------|
| **Personnel** | $75K–95K | 15 FTE-weeks avg $5K/FTE-week (salary + benefits + overhead) |
| **ML Infrastructure** | $8K–12K | 100+ additional repos for training, GPU time (weekly retraining) |
| **Cloud Infrastructure** | $5K–8K | Parallel CI runners, storage for audit trail, OTel collector |
| **External Services** | $3K–5K | GitLab/Bitbucket API quotas, code-intelligence APIs (Semgrep), analytics |
| **Tools & Licenses** | $2K–3K | Jaeger hosted (optional), Grafana Cloud (dashboards), ClickHouse |
| **Documentation & Training** | $1K–2K | SKILL.md specs, runbooks, engineer onboarding |
| **Contingency (14%)** | $15K–18K | Risk buffer for scope creep, unforeseen delays |
| **TOTAL BUDGET** | **$120K–180K** | **Blended cost (design + build + test + deploy)** |

### Monthly Operational Cost (Post-Fase 4)

| Item | Cost/Month | Notes |
|------|------------|-------|
| OTel Collector + Jaeger | $800–1200 | Trace ingestion, storage, UI |
| ClickHouse (time-series DB) | $400–600 | 1yr retention, 5-min pre-aggregation |
| Grafana Cloud (dashboards) | $200–300 | 4x custom dashboards, alert evaluation |
| AWS Compute (inference, refactor) | $300–500 | t3.medium + c5.large instances, autoscaling |
| Storage (audit trail, models) | $100–150 | 100 repos × 1yr audit = 10GB; ML model versions |
| External APIs | $200–300 | GitLab, Bitbucket, code intelligence queries |
| **TOTAL/MONTH** | **$2K–3K** | **(+$2K from Fase 3 baseline)** |

---

## RISK MITIGATION STRATEGY

### Risk 1: Multi-Platform API Changes

**Risk**: GitLab, Bitbucket release breaking API changes, invalidating adapter code.

**Mitigation**:
- Version pin all APIs (GitHub v3/graphql, GitLab v4, Bitbucket v2.0)
- Implement API versioning in PAL: "Adapter v2 for GitLab API 4.5+"
- Fallback to git CLI for core operations (push, merge, fetch)
- Monitor release calendars; add deprecation warnings (6 months before breaking change)
- Quarterly compatibility audit (W25, W29, W33, W37)
- Maintain 2 API versions in parallel during sunset period

**Responsible**: Senior Backend Engineer (API expertise)

---

### Risk 2: AST Refactoring Bugs (Code Breaking)

**Risk**: Refactoring logic produces incorrect code (broken imports, logic errors), breaking production.

**Mitigation**:
- **100% diff review**: Every refactoring diffs reviewed by human before apply
- **Staged rollout per language**:
  - W22 (Python): Internal/beta repos only, 5 repos tested
  - W23 (TypeScript, Java): Expand to 20 repos if no issues
  - W23 (Go): Expand if previous languages stable
- **Compile/syntax checks mandatory**: All refactored code must parse + compile
- **Test coverage requirement**: Refactoring only applied if test coverage ≥80%
- **Rollback procedure**: Single-click revert via API, automatic rollback if post-merge CI fails
- **Canary deployment**: 5% of eligible PRs get refactoring; monitor success rate

**Responsible**: QA Engineer, Senior Backend Engineer

---

### Risk 3: ML Model Performance Cliff

**Risk**: Model accuracy drops >5% suddenly (distribution shift, data poisoning, overfitting).

**Mitigation**:
- **Monitoring interval**: Reduced from weekly to **hourly** during Fase 4 (W24 onward)
- **Holdout test set**: Fixed 20% of merges never used in training; weekly accuracy check
- **Feature importance drift detection**: Alert if top-10 features drop >10% importance
- **Anomaly detection on predictions**: Flag unusual prediction distributions (e.g., all 0.95 confidence)
- **Graceful fallback**: If AUROC drops <0.90, automatically revert to hardcoded 0.75 threshold
- **Human-in-the-loop**: Require manual approval if ML confidence used for auto-merge (not just decision support)

**Responsible**: ML Engineer, DevOps Engineer

---

### Risk 4: Observability Data Explosion

**Risk**: OTel traces + metrics grow to > 10TB/month, unsustainable cost and query latency.

**Mitigation**:
- **Sampling strategy**: 10% sampling of successful merges (reduce noise), 100% of failures
- **Retention policy**: 3 months hot storage (Jaeger), 1yr cold storage (ClickHouse)
- **Pre-aggregation**: 5-min buckets for metrics; hourly for cost tracking
- **Cardinality control**: Limit high-cardinality dimensions (no PR content, only PR id)
- **Cost monitoring dashboard**: Alert if monthly cost >$3.5K (risk threshold)
- **Early-out queries**: Set max query duration 30 sec; deny <1-minute intervals for time-series

**Responsible**: DevOps Engineer, ML Engineer (cost monitoring)

---

### Risk 5: Multi-Platform Adoption Lag

**Risk**: GitLab/Bitbucket integrations built but orgs don't adopt (network effects, inertia).

**Mitigation**:
- **Early user recruitment**: Identify 2–3 pilot orgs per platform before W19
- **Sales enablement**: Create 1-pager demo + case study
- **Integration workshops**: Run 2x per platform (Oct, Nov) to remove friction
- **Success metrics tracking**: Monitor adoption velocity weekly; escalate if <1 org/week
- **Incentive program**: First 5 GitLab orgs get free 6-month license + 1-on-1 training
- **Fallback**: If adoption <3 orgs by W25, recommend scaling GitHub-only through Fase 5

**Responsible**: Product Manager, Sales/DevRel

---

### Risk 6: Refactoring Over-Aggressiveness

**Risk**: Refactoring engine suggests too many changes (>10 per PR), overwhelming developers, high rejection rate.

**Mitigation**:
- **Severity tiers**: Only apply High/Critical rules by default; Medium/Low must be opted-in
- **Change budget per PR**: Max 5 refactoring suggestions per PR
- **Prioritization**: Rank by impact (code smell weight × estimated time-to-fix)
- **Opt-out workflow**: "Skip refactoring" label disables suggestions for that PR
- **Feedback loop**: Track rejection rate; if >40%, reduce aggressiveness (disable low-value rules)
- **Developer education**: Explain why each refactoring (rationale comment)

**Responsible**: QA Engineer, Product Manager

---

### Risk 7: Cross-Repo Dependency Deadlock

**Risk**: Dependency sequencing creates circular dependencies or merge queuing, blocking releases.

**Mitigation**:
- **Circular dependency detection**: Daily graph scan; alert if cycles found
- **Manual override**: Allow force-merge if merge is blocked >24h (human decision)
- **Async validation**: Don't block merge on dependency checks; warn asynchronously
- **Fallback**: If dependency graph unavailable, proceed with merge (graceful degradation)
- **Rollback automation**: If post-merge integration test fails, auto-revert related PRs (within 10 min)

**Responsible**: Senior Backend Engineer, DevOps Engineer

---

## DEPLOYMENT & CUTOVER PLAN

### Canary Deployment Phases (W24–W25)

```
Phase 0 — Audit Mode (W24, days 1–3):
  - All Fase 4 features enabled, but NO automatic actions taken
  - Log would-be decisions (merge, refactor, etc.)
  - Collect baseline metrics for 3 days
  - Human review all decisions (100% audit)
  - Decision: proceed to Phase 1 if no critical issues found

Phase 1 — Low-Risk Rollout (W24, days 4–7):
  - 5% of merges use Fase 4 heuristics (ML confidence 95%+)
  - Auto-merge only for repos with <5 developers, <100 files
  - Monitor: success rate, latency, false positives
  - Alert threshold: success rate <90%, latency >120s
  - Decision: proceed to Phase 2 if metrics OK for 3 days

Phase 2 — Expanded Rollout (W25, days 1–5):
  - 10% of merges use Fase 4 heuristics (ML confidence 90%+)
  - Medium-risk repos now included (5–20 developers, 100–500 files)
  - Refactoring engine enabled for Python + TypeScript (high precision)
  - Monitor: same metrics as Phase 1
  - Decision: proceed to Phase 3 if metrics stable for 3 days

Phase 3 — Full Deployment (W25, days 6–10):
  - 100% of merges use Fase 4 heuristics
  - All repos, all languages eligible for refactoring
  - All platforms (GitHub, GitLab, Bitbucket, Gitea) live
  - All features operational (cost tracking, author skill, cross-repo deps)
  - Monitor: extend to 14-day observation period

Rollback Trigger: If success rate <88% OR latency >180s OR AUROC <0.91, rollback to Fase 3
```

### Runbook: Fase 4 Rollback (Emergency)

1. **Immediately**:
   - Disable all Fase 4 merge decision heuristics; revert to Fase 3 ML model (hardcoded 0.75 threshold)
   - Disable refactoring suggestions (no apply, just informational)
   - Alert: page on-call, notify stakeholders via Slack

2. **Within 5 minutes**:
   - Analyze logs: identify root cause (API failure, model degradation, data corruption)
   - Create incident ticket (Jira, SIRT protocol)

3. **Within 1 hour**:
   - Implement hotfix OR revert specific feature (commit rollback)
   - Re-enable Fase 4 gradually (canary restart, Phase 0)
   - Post-incident review scheduled (within 24h)

---

## CONFIGURATION & DEPLOYMENT FILES

### `.claude/planning/FASE-4-ROADMAP.md` (THIS DOCUMENT)
Stored in `/home/user/Codex-exemplo/.claude/planning/FASE-4-ROADMAP.md`

### Derived Skill Specifications (To Be Created)

1. **`git-multi-platform-router.md` v1.0** — 25 sections, platform detection, API adapters, routing logic
2. **`git-code-refactoring-engine.md` v1.0** — 35 sections, AST patterns (4 languages), code smell library, diff validation
3. **`git-observability-stack.md` v1.0** — 40 sections, OTel instrumentation, dashboard specs, alerting rules
4. **`git-ml-advanced-scoring.md` v1.0** — 45 sections, 50-feature engineering, ensemble architecture, confidence intervals

### Configuration Files (To Be Created)

```
.claude/config/
├── fase4-platforms.yaml
│   ├── github: { api_version: "2022-11-28", status: "operational" }
│   ├── gitlab: { api_version: "4.0", status: "pilot_w19" }
│   ├── bitbucket: { api_version: "2.0", status: "pilot_w21" }
│   └── gitea: { api_version: "1.0", status: "pilot_w24" }
├── fase4-features.yaml
│   ├── refactoring-rules: { python, java, typescript, go }
│   ├── code-smell-library: { 55_rules, severity_weighted }
│   └── ml-features: { 50_features, quarterly_retraining }
└── fase4-observability.yaml
    ├── otel-collector: { sampling_rate: 0.10, retention: "1yr" }
    ├── dashboards: { cost, ml_health, platform_status, anomalies }
    └── alerts: { 30+ alert_rules, severity_levels }
```

---

## SUCCESS DEFINITION

### Definition of Done for Fase 4

**Technical**:
- [ ] All 4 pillars implemented (A, B, C, D)
- [ ] All 12 features deployed to production
- [ ] 4 new SKILL.md specifications published
- [ ] All acceptance criteria met (per feature)
- [ ] Multi-platform support: ≥3 platforms live (GitHub, GitLab, Bitbucket)
- [ ] ML model: ≥93% AUROC, weekly retraining automated
- [ ] Observability: 100% merge tracing, 4 dashboards operational
- [ ] Security: Audit trail complete, compliance validated

**Business**:
- [ ] ≥10 organizations on Fase 4 platform
- [ ] NPS ≥40 (customer satisfaction survey)
- [ ] Merge velocity +15% vs. Fase 3
- [ ] Cost per merge ≤$0.002 ($2/1000 merges)
- [ ] Time-to-market reduced 20% vs. Fase 3

**Operational**:
- [ ] Runbooks for all common scenarios (deployment, rollback, incident response)
- [ ] Engineer onboarding documentation (SKILL.md + runbooks)
- [ ] SLA: 99.5% uptime, <30min MTTR for critical issues
- [ ] Monitoring & alerting 24/7 operational

---

## NEXT STEPS (Week of Oct 1, 2026)

1. **Architecture Review** (Oct 2–4):
   - Present Fase 4 roadmap to Manta leadership
   - Stakeholder alignment: sales, devops, ml-engineering
   - Risk assessment & mitigation approval

2. **Team Allocation** (Oct 5–7):
   - Recruit 15 FTE-weeks (4 backend, 3 ML, 2 DevOps, 2 QA, 1 PM, 1 arch, 1 junior, 1 floating)
   - Kick-off meeting: roadmap walkthrough, technical deep-dives

3. **Infrastructure Setup** (Oct 8–14):
   - Provision staging environment (multi-platform test harness)
   - Deploy OTel collector + Jaeger (observability infrastructure)
   - Set up CI/CD for Fase 4 automation (weekly retraining job, A/B test runner)

4. **Work Begin** (Oct 15, W19):
   - Implementation starts: Pillar A (platform routing), Pillar B (refactoring), Pillar C (observability), Pillar D (ML expansion)
   - Daily standups, weekly milestone reviews

---

## APPENDIX: GLOSSARY & REFERENCES

**Terminology**:
- **FTE-week**: Full-time equivalent person-week (40 hours)
- **AUROC**: Area Under Receiver Operating Characteristic curve; ML model classification accuracy (0–1, higher is better)
- **Canary Deployment**: Gradual rollout to small % of traffic, monitor, then expand
- **OTel**: OpenTelemetry (open-source observability framework)
- **PAL**: Platform Abstraction Layer (unified interface across Git platforms)
- **SHAP**: SHapley Additive exPlanations (ML model explainability)
- **Topological Sort**: Ordering of nodes in directed acyclic graph (dependency sequencing)

**External References**:
- OpenTelemetry: https://opentelemetry.io/docs/
- Jaeger Distributed Tracing: https://www.jaegertracing.io/
- ClickHouse OLAP: https://clickhouse.com/
- GitLab API: https://docs.gitlab.com/ee/api/
- Bitbucket API: https://developer.atlassian.com/bitbucket/api/2/
- Gitea API: https://docs.gitea.io/en-us/api-usage/

**Related Fase Documents**:
- CLAUDE.md (Manta Maestro master registry, v4.5)
- Fase 3 Roadmap (Full Automation & Intelligence, W13–W16, Sept–Oct 2026)
- Fase 2 Roadmap (Security & Incident Response, W5–W12, Aug–Oct 2026)

---

**End of Document**

Version: **v1.0.0 (draft)**  
Status: **Ready for Fase 4 Kickoff Planning**  
Date: 2026-09-13  
Distribution: Manta Leadership, Engineering Team, Stakeholders
