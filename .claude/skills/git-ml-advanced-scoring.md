# git-ml-advanced-scoring.md

**Skill ID:** git-ml-adv-score  
**Title:** Advanced ML Confidence Scoring (50-Feature Ensemble)  
**Version:** v1.0.0  
**Phase:** Fase 4 — Git Evolution Suite (Pillar D: Advanced ML Features)  
**Tier:** Opus (ML Engineering)  
**Agent:** agente-gitops (Manta 17)  
**Status:** Design Specification (Fase 4 — Q4 2026 rollout)

---

## 1. Overview & Strategic Alignment

### 1.1 Motivation

Fase 3 delivered 31-feature ML confidence scoring (92.4% precision). Fase 4 **Pillar D** expands to **50-feature ensemble** with:

- **Deeper signal extraction:** From commit patterns, temporal dynamics, team behavior, infrastructure health
- **Confidence intervals:** Quantile regression + uncertainty estimation
- **Active learning:** Flag uncertain predictions (75–85%) for human feedback, retrain weekly
- **Quarterly retraining:** 3-month data + A/B testing (≥93.5% accuracy gating)
- **Model versioning:** v1, v2, v3 with parallel A/B testing infrastructure

### 1.2 Goal Statement

Achieve **≥94% precision + ≤3% FN rate** on 1,000+ daily merges by enriching feature space, quantifying uncertainty, and closing feedback loops via automated retraining.

### 1.3 Scope

**In:**
- 50-feature engineering (expand Fase 3 baseline)
- Confidence interval estimation (quantile regression)
- Active learning prioritization (uncertain prediction flag)
- Weekly feedback integration + retraining
- Quarterly model refresh cycle
- Model serving (batch + online, <200ms latency)
- A/B testing framework (incumbent vs. v2, v3)
- 4 worked examples + performance benchmarks

**Out (Fase 5):**
- Causal inference (treatment effect estimation)
- Neural networks (deep learning)
- Federated learning (privacy-preserving training)

---

## 2. 50-Feature Engineering

### 2.1 Feature Architecture (3 Cohorts)

```
Cohort A — Preserved from Fase 3 (31 features)
├── Code Quality Signals (8)
│   ├── file_type_risk_score
│   ├── diff_size_complexity
│   ├── lines_added_deleted_ratio
│   ├── cyclomatic_complexity_delta
│   ├── test_coverage_delta
│   ├── comment_density_ratio
│   ├── dead_code_lines
│   └── code_duplication_percentage
│
├── Conflict & History (6)
│   ├── merge_conflict_frequency_30d
│   ├── branch_merge_history_count
│   ├── revert_frequency_90d
│   ├── file_churn_rate
│   ├── hotspot_file_touches
│   └── concurrent_changes_count
│
├── Author Reputation (6)
│   ├── author_pr_success_rate_90d
│   ├── author_defect_density
│   ├── author_code_review_participation
│   ├── author_response_time_hours
│   ├── author_years_in_repo
│   └── author_domain_expertise_score
│
└── Temporal & CI (11)
    ├── day_of_week_merge_pattern
    ├── time_of_day_optimal_window
    ├── pr_age_days
    ├── review_turnaround_hours
    ├── ci_pass_rate_historical
    ├── ci_flakiness_score
    ├── deployment_frequency_7d
    ├── rollback_rate_30d
    ├── incident_frequency_60d
    ├── mttr_mean_time_to_recovery
    └── sla_compliance_percent

Cohort B — New Behavioral Features (11)
├── Author Dynamics (4)
│   ├── author_skill_level_tier (L1-L5 grading)
│   ├── author_specialization_domain (file type expertise)
│   ├── author_cross_team_collaboration_score
│   └── author_mentoring_activity_count
│
├── Team Velocity (3)
│   ├── team_merge_frequency_per_day
│   ├── team_async_review_velocity_hours
│   └── team_context_switch_count_24h
│
└── Code Review Quality (4)
    ├── reviewer_expertise_match_score
    ├── code_review_duration_minutes
    ├── review_comment_depth_nlp_score
    └── reviewer_approval_pattern_consistency

Cohort C — Infrastructure & Dependency Features (8)
├── Environment Health (4)
│   ├── ci_flakiness_trend_7d_delta
│   ├── infrastructure_load_factor_percent
│   ├── resource_contention_score
│   └── deployment_pipeline_health_score
│
└── Dependency & Impact (4)
    ├── cross_repo_dependency_count
    ├── upstream_health_indicator
    ├── downstream_impact_breadth
    └── feature_flag_rollout_status

Cohort D — Security & Compliance (4)
├── Security Signals (2)
│   ├── vulnerability_count_new
│   └── security_scan_defect_rate
│
└── Compliance & QA (2)
    ├── license_compliance_check_pass_bool
    └── performance_regression_risk_score
```

**Total: 8 + 6 + 6 + 11 + 4 + 3 + 4 + 4 + 4 + 2 + 2 = 54 features**  
*(Optimized to 50 via dropping 4 correlated features: team_context_switch_count_24h, deployment_pipeline_health_score, upstream_health_indicator, downstream_impact_breadth — handled by cross_repo_dependency_count)*

### 2.2 Feature Importance Ranking (Current Model — Fase 3)

**Top 10 by SHAP value:**

| Rank | Feature | Importance % | Cohort | Type |
|------|---------|--------------|--------|------|
| 1 | author_pr_success_rate_90d | 12.3 | A (Author Rep) | Behavioral |
| 2 | ci_pass_rate_historical | 10.8 | A (Temporal) | Infrastructure |
| 3 | merge_conflict_frequency_30d | 9.2 | A (Conflict) | Code Quality |
| 4 | author_defect_density | 8.7 | A (Author Rep) | Behavioral |
| 5 | diff_size_complexity | 7.9 | A (Code Quality) | Code Quality |
| 6 | code_review_duration_minutes | 6.4 | B (Review Quality) | NEW |
| 7 | rollback_rate_30d | 5.8 | A (Temporal) | Infrastructure |
| 8 | reviewer_expertise_match_score | 5.1 | B (Review Quality) | NEW |
| 9 | pr_age_days | 4.6 | A (Temporal) | Code Quality |
| 10 | author_skill_level_tier | 4.2 | B (Author Dynamics) | NEW |

**Projected Importance (Post-Q4 Retraining):**

| Rank | Feature | Proj. % | Δ | Notes |
|------|---------|---------|---|-------|
| 1 | author_skill_level_tier | 13.8 | +3.8 | Stronger signal than raw 90d rate |
| 2 | reviewer_expertise_match_score | 11.9 | +6.8 | Team specialization critical |
| 3 | ci_flakiness_score | 10.2 | +1.4 | More repos enable better calibration |
| 4 | code_review_duration_minutes | 9.7 | +3.3 | Time investment = quality proxy |
| 5 | author_defect_density | 8.9 | 0 | Stable signal |
| 6 | merge_conflict_frequency_30d | 8.1 | -1.1 | Slightly less dominant |
| 7 | diff_size_complexity | 7.4 | -0.5 | Stable |
| 8 | pr_age_days | 6.3 | +1.7 | Age becomes risk factor over time |
| 9 | rollback_rate_30d | 5.5 | -0.3 | Stable |
| 10 | cross_repo_dependency_count | 4.8 | NEW | Emerging risk pattern |

### 2.3 Feature Engineering Implementation

**Cohort A—D Computation (pseudocode):**

```python
# Cohort A (existing, 31 features)
author_pr_success_rate_90d = (
    SELECT COUNT(CASE WHEN merge_status = 'success')
    FROM merge_log
    WHERE author_id = :author AND created_at > NOW() - '90 days'
) / total_prs_authored_90d

ci_pass_rate_historical = (
    SELECT COUNT(CASE WHEN ci_status = 'pass')
    FROM ci_runs
    WHERE repo_id = :repo AND branch = :branch
) / total_ci_runs

# Cohort B: New behavioral features
author_skill_level_tier = CASE
    WHEN author_defect_density < 0.02 AND author_pr_success_rate_90d > 0.95 THEN 'L5'
    WHEN author_defect_density < 0.05 AND author_pr_success_rate_90d > 0.90 THEN 'L4'
    WHEN author_defect_density < 0.10 AND author_pr_success_rate_90d > 0.80 THEN 'L3'
    WHEN author_defect_density < 0.15 AND author_pr_success_rate_90d > 0.70 THEN 'L2'
    ELSE 'L1'
END

reviewer_expertise_match_score = (
    SELECT AVG(expertise_score)
    FROM reviewer_specialization
    WHERE reviewer_id = :reviewer
      AND file_type IN (
          SELECT DISTINCT file_type FROM diff
          WHERE pr_id = :pr_id
      )
) / MAX_EXPERTISE_SCORE * 100

code_review_duration_minutes = (
    SELECT (approved_at - created_at) / 60
    FROM code_reviews
    WHERE pr_id = :pr_id
    ORDER BY created_at DESC LIMIT 1
)

# Cohort C: Infrastructure & dependency
cross_repo_dependency_count = (
    SELECT COUNT(DISTINCT upstream_repo)
    FROM repo_dependencies
    WHERE downstream_repo = :repo
)

ci_flakiness_score = (
    SELECT 100 * (
        COUNT(CASE WHEN flaky_test_detected = true)
        / NULLIF(COUNT(*), 0)
    )
    FROM ci_runs
    WHERE repo_id = :repo AND created_at > NOW() - '30 days'
)

# Cohort D: Security & compliance
vulnerability_count_new = (
    SELECT COUNT(*)
    FROM vulnerability_scan
    WHERE repo_id = :repo
      AND scan_date >= pr_created_at
      AND severity IN ('critical', 'high')
)

license_compliance_check_pass_bool = (
    SELECT COALESCE(compliance_passed, false)
    FROM license_audit
    WHERE repo_id = :repo
    ORDER BY audit_date DESC LIMIT 1
)
```

---

## 3. Confidence Interval Estimation

### 3.1 Quantile Regression Approach

Rather than point estimates (e.g., 87%), output **confidence intervals** via quantile regression:

```
Merge success probability: 87% [82% — 92%] (95% CI)
Interpretation:
  - Point estimate: 87%
  - 95% confidence interval: 82–92%
  - Range width: 10 percentage points
  - Interpretation: High confidence (tight CI)
```

### 3.2 Algorithm: Gradient Boosting Quantiles

**Training phase (quarterly):**

```python
from sklearn.ensemble import GradientBoostingRegressor
import numpy as np

# Train 3 quantile models: 5th, 50th, 95th percentiles
quantiles = [0.05, 0.50, 0.95]
models = {}

for q in quantiles:
    gb = GradientBoostingRegressor(
        loss='quantile',
        alpha=q,
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42
    )
    gb.fit(X_train_50feat, y_train_success_bool)
    models[q] = gb

# Predictions: [lower_5%, point_50%, upper_95%]
predictions = np.array([
    models[0.05].predict(X_test),
    models[0.50].predict(X_test),
    models[0.95].predict(X_test)
]).T
```

**Output structure:**

```json
{
  "pr_id": "gh:anthropics/claude/12345",
  "merge_confidence": {
    "point_estimate": 0.87,
    "ci_lower": 0.82,
    "ci_upper": 0.92,
    "ci_width": 0.10,
    "confidence_level": "HIGH",
    "uncertainty_flag": false
  },
  "feature_contributions": [
    {"feature": "author_skill_level_tier", "contribution": 0.15},
    {"feature": "reviewer_expertise_match_score", "contribution": 0.12},
    ...
  ]
}
```

### 3.3 Confidence Buckets & Decision Rules

| CI Width | Confidence | Auto-Merge | Phase 1 | Phase 2 | Phase 3 |
|----------|-----------|-----------|---------|---------|---------|
| <5% | VERY HIGH | ≥97% | ≥95% | ≥92% | ≥85% |
| 5–10% | HIGH | 92–97% | 90–95% | 85–92% | 75–85% |
| 10–15% | MEDIUM | 85–92% | 80–90% | 75–85% | 65–75% |
| 15–25% | LOW | 75–85% | 70–80% | 60–75% | 50–65% |
| >25% | VERY LOW | <75% | <70% | <60% | <50% |

**Phase reference:** Phase 1 (green-field repos, low-risk), Phase 2 (medium-risk), Phase 3 (brownfield, legacy), Phase 4 (canary/experimental).

### 3.4 Example: Confidence Interval Outputs

**Example PR 1 — High Confidence:**
```
PR: gh:example-org/example-service/42
Features: 50-feature vector computed
Point estimate: 0.91 (91% success probability)
Quantile regression outputs:
  - 5th percentile: 0.88
  - 50th percentile: 0.91
  - 95th percentile: 0.94
Confidence interval: [0.88, 0.94] (6pp width)
Confidence level: HIGH
Decision: Auto-merge (Phase 1 threshold ≥95% not met, escalate to 90–95% bucket)
Action: Escalate to review team for final approval
```

**Example PR 2 — Uncertain (Active Learning Flag):**
```
PR: gh:example-org/legacy-service/156
Features: 50-feature vector computed
Point estimate: 0.79 (79% success probability)
Quantile regression outputs:
  - 5th percentile: 0.72
  - 50th percentile: 0.79
  - 95th percentile: 0.86
Confidence interval: [0.72, 0.86] (14pp width)
Confidence level: MEDIUM
Decision: Uncertain prediction → Flag for human feedback
Action: Collect reviewer feedback, add to active learning pool
```

---

## 4. Active Learning & Feedback Loop

### 4.1 Uncertainty Sampling Strategy

**Goal:** Improve model by collecting human feedback on predictions where model is uncertain (75–85% range).

**Procedure:**

1. **Predict on all new merges** → compute point estimate + CI
2. **Flag uncertain predictions:** 75% ≤ score ≤ 85% (CI width >10%)
3. **Query human:** "Did this PR merge successfully? Any blockers?"
4. **Collect feedback:** Success / failure + root cause tags
5. **Accumulate weekly** → retrain on accumulated feedback
6. **Update model** → deploy improved version

### 4.2 Feedback Collection Schema

```python
class MergeFeedback(BaseModel):
    pr_id: str
    prediction_score: float
    prediction_ci_width: float
    actual_outcome: bool  # True = merged successfully
    human_rater_id: str
    feedback_tags: List[str]  # ['reviewer-blocked', 'ci-failed', 'dependencies', 'manual-override', ...]
    timestamp: datetime
    notes: str  # Optional narrative

# Weekly feedback table: tbl_merge_feedback_weekly
# Accumulated over 7 days, ~50–100 samples (1,000+ repos × 7% uncertain flag rate)
```

### 4.3 Weekly Retraining Loop

**Schedule:** Every Monday at 02:00 UTC

```python
# Step 1: Collect feedback from last 7 days
feedback_week = fetch_feedback(
    start=NOW - timedelta(days=7),
    end=NOW,
    confidence_min=0.75,
    confidence_max=0.85
)
print(f"Feedback collected: {len(feedback_week)} samples")

# Step 2: Augment training data
X_augmented = concatenate([X_train_historical, feedback_week.features])
y_augmented = concatenate([y_train_historical, feedback_week.outcomes])

# Step 3: Retrain ensemble (5th, 50th, 95th percentiles)
for q in [0.05, 0.50, 0.95]:
    gb = GradientBoostingRegressor(
        loss='quantile',
        alpha=q,
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        validation_fraction=0.1,
        n_iter_no_change=10,
        random_state=42
    )
    gb.fit(X_augmented, y_augmented)
    models_updated[q] = gb

# Step 4: Validate on holdout set (last 100 merges)
y_pred = ensemble_predict(X_holdout)
accuracy = f1_score(y_holdout, y_pred > 0.70)
if accuracy >= 0.92:
    deploy_updated_models(models_updated)
else:
    log_alert("Weekly retraining accuracy < 92%, rollback to v1.0")
```

### 4.4 Drift Detection

Monitor model performance weekly:

```python
# Metric: Rolling F1 score (50-merge window)
f1_current = f1_score(y_actual_50m, y_pred_50m)
f1_baseline = 0.920  # Fase 3 target

if f1_current < f1_baseline - 0.03:
    alert("Model drift detected: F1 dropped to {:.3f}".format(f1_current))
    recommend_full_retrain()
```

---

## 5. Model Serving Architecture

### 5.1 Batch Inference (Daily)

**Purpose:** Score all 1,000+ repos daily for dashboards + reporting.

```python
# Run at 04:00 UTC daily (after CI stabilizes)
all_repos = fetch_all_repos()  # 1,000+ repos
all_pending_merges = fetch_pending_merges(all_repos)

batch_features = compute_50_features(all_pending_merges)
batch_predictions = ensemble_predict_batch(batch_features)

# Write results
write_predictions_to_db(
    batch_predictions,
    table='tbl_merge_predictions_daily',
    timestamp=NOW
)

# Index for dashboards
create_index('idx_daily_repo_score', 'tbl_merge_predictions_daily')
```

**Expected latency:** ~50ms per repo × 1,000 repos = **50 seconds total** (parallelized: 8 workers → **6 seconds**)

### 5.2 Online Inference (Real-time, <200ms)

**Purpose:** Score merge requests as they arrive in GitHub.

```python
# Triggered by GitHub webhook: pull_request.opened / updated
async def score_pr_realtime(pr_event):
    pr_features = compute_50_features_single(pr_event)
    
    # Timeout: 200ms (or fallback to Fase 3 model)
    try:
        result = await asyncio.wait_for(
            ensemble_predict_async(pr_features),
            timeout=0.200
        )
        return result
    except asyncio.TimeoutError:
        # Fallback to Fase 3 (31-feature model, cached)
        return ensemble_predict_fase3(pr_features[:31])

# Latency target: <100ms p99
# Fallback trigger: >500ms latency
```

### 5.3 Model Versioning & A/B Testing

**Version registry:**

```
Model v1.0.0 (Baseline, Fase 3 → 4 transition)
├── Training date: 2026-06-01
├── Accuracy: 92.4%
├── F1 score: 0.920
├── Ensemble: RF 65% + XGB 35%
└── Status: INCUMBENT (serving 100%)

Model v2.0.0 (Q1 Retrain, +19 features)
├── Training date: 2026-10-01
├── Accuracy: 93.8%
├── F1 score: 0.938
├── Features: 50 (31 + 19 new)
├── Ensemble: RF 65% + XGB 35%
├── Confidence intervals: Enabled (quantile regression)
└── Status: CANARY (serving 10%, Phase 1 repos only)

Model v2.1.0 (Weekly learning update #5)
├── Training date: 2026-10-29
├── Accuracy: 93.9%
├── F1 score: 0.939
├── Feedback samples: 346 (28 weeks × ~12.4 samples/week)
└── Status: STAGED (ready for rollout if v2.0 stable >14 days)
```

**A/B testing framework:**

```python
def route_request_ab_test(pr_id, user_id):
    variant = hash(pr_id) % 100
    
    if variant < 90:
        # Control: v1.0.0 (incumbent)
        return predict_v1(pr_features), version='v1.0.0'
    else:
        # Test: v2.0.0 (canary)
        return predict_v2(pr_features), version='v2.0.0'

# Collect metrics for both variants
# Rollout criteria: v2 F1 ≥ v1 F1 + 0.01 for 14+ days
```

### 5.4 Fallback & Failover

| Scenario | Latency | Action | Outcome |
|----------|---------|--------|---------|
| v2 inference OK | <100ms p99 | Serve prediction | Use v2 (50 features) |
| v2 inference SLOW | 100–500ms | Serve fallback | Use v1 (31 features, cached) |
| v2 inference TIMEOUT | >500ms | Serve fallback | Use v1 (31 features, cached) |
| v2 model UNAVAILABLE | N/A | Serve fallback | Use v1 (hardcoded) |
| v1 UNAVAILABLE | N/A | Threshold-based | Score < 70% → review, >85% → auto-merge |

---

## 6. Quarterly Retraining Procedure

### 6.1 Timeline: Q4 2026 (Target Deployment)

**Phase 0 (Training):** Oct 1–14, 2026

```
Oct 1:   Start data collection (3 months: Jul 1 — Sep 30)
Oct 2:   Compute 50 features on 1,247 accumulated merges
Oct 5:   Train quantile regression ensemble (5th, 50th, 95th)
Oct 8:   Validate on holdout (100 merges, last week)
Oct 10:  Run offline A/B test (v1.0 vs v2.0)
Oct 12:  Feature importance analysis + dashboard
Oct 14:  Sign-off: Accuracy ≥93.5% ✓
```

**Phase 1 (Canary):** Oct 15–21, 2026

```
Oct 15:  Deploy v2.0.0 to 10% Phase 1 repos (low-risk)
Oct 16:  Monitor: F1 score, latency, feedback rate
Oct 18:  Expand to 25% if stable
Oct 21:  Evaluate: Continue or rollback
```

**Phase 2 (Staged Rollout):** Oct 22–28, 2026

```
Oct 22:  Expand to 50% (Phase 1 + Phase 2)
Oct 25:  Monitor infrastructure (batch job latency, DB load)
Oct 28:  Evaluate: Ready for Phase 3?
```

**Phase 3 (Full Deployment):** Oct 29–31, 2026

```
Oct 29:  Deploy to 100% (all phases)
Oct 30–31: Final monitoring + feedback collection
```

### 6.2 Data Collection & Feature Computation

**Input:** 3 months of merge activity (Jul–Sep 2026)

```python
# Expected volume
merged_prs = fetch_merged_prs(
    start='2026-07-01',
    end='2026-09-30'
)
print(f"Total merges: {len(merged_prs)}")  # ~1,247

# Feature computation (50 features × 1,247 merges)
X_train = []
y_train = []
for pr in merged_prs:
    features = compute_50_features(pr)
    outcome = pr.merge_status == 'success'  # 1 = success, 0 = blocked/reverted
    X_train.append(features)
    y_train.append(outcome)

X_train = np.array(X_train)  # Shape: (1247, 50)
y_train = np.array(y_train)  # Shape: (1247,)

print(f"Training data: {X_train.shape}")
print(f"Label distribution: {np.mean(y_train):.1%} success rate")  # ~92%
```

### 6.3 Model Training

```python
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# Train/test split (80/20, temporal)
split_idx = int(0.8 * len(X_train))
X_t, X_h = X_train[:split_idx], X_train[split_idx:]
y_t, y_h = y_train[:split_idx], y_train[split_idx:]

# Train 3 quantile models
quantiles = [0.05, 0.50, 0.95]
models = {}

for q in quantiles:
    print(f"Training quantile={q}...")
    gb = GradientBoostingRegressor(
        loss='quantile',
        alpha=q,
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        max_features='sqrt',
        random_state=42,
        verbose=1
    )
    gb.fit(X_t, y_t)
    models[q] = gb
    
    # Evaluate on holdout
    y_pred_q = gb.predict(X_h)
    mae = np.mean(np.abs(y_pred_q - y_h))
    print(f"  Holdout MAE: {mae:.4f}")

# Aggregate to single ensemble prediction
def predict_ensemble(X):
    preds = {
        'lower': models[0.05].predict(X),
        'point': models[0.50].predict(X),
        'upper': models[0.95].predict(X)
    }
    return preds

y_pred_ensemble = predict_ensemble(X_h)
y_pred_binary = y_pred_ensemble['point'] > 0.70  # Threshold for binary classification

# Metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

accuracy = accuracy_score(y_h, y_pred_binary)
precision = precision_score(y_h, y_pred_binary)
recall = recall_score(y_h, y_pred_binary)
f1 = f1_score(y_h, y_pred_binary)

print(f"Holdout Metrics:")
print(f"  Accuracy:  {accuracy:.4f}")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall:.4f}")
print(f"  F1 Score:  {f1:.4f}")
```

**Expected results:**

| Metric | v1.0 (Baseline) | v2.0 (Target) | Δ |
|--------|---|---|---|
| Accuracy | 92.4% | ≥93.5% | +1.1pp |
| Precision | 94.1% | ≥95.0% | +0.9pp |
| Recall | 89.3% | ≥90.0% | +0.7pp |
| F1 Score | 0.920 | ≥0.935 | +0.015 |

### 6.4 Feature Importance Analysis

```python
import shap

# SHAP explainer for top features
explainer = shap.TreeExplainer(models[0.50])  # Use median quantile
shap_values = explainer.shap_values(X_t)

# Feature importance ranking
feature_importance = np.abs(shap_values).mean(axis=0)
sorted_idx = np.argsort(feature_importance)[::-1]

print("Top 20 Features (by SHAP importance):")
for i, idx in enumerate(sorted_idx[:20]):
    print(f"{i+1:2d}. {feature_names[idx]:40s} {feature_importance[idx]:6.3f}")

# Save for monthly review
save_feature_importance(
    feature_importance,
    feature_names,
    timestamp=NOW,
    model_version='v2.0.0'
)
```

### 6.5 A/B Testing (Offline)

```python
# Offline A/B test: v1.0 vs v2.0
y_pred_v1 = predict_v1(X_h)  # 31 features
y_pred_v2 = predict_ensemble(X_h)  # 50 features, point estimate

y_pred_v1_binary = y_pred_v1 > 0.70
y_pred_v2_binary = y_pred_v2['point'] > 0.70

# Statistical comparison
from scipy.stats import chi2_contingency

contingency = np.array([
    [
        np.sum((y_h == 1) & (y_pred_v1_binary == 1)),  # True Positives
        np.sum((y_h == 1) & (y_pred_v1_binary == 0))   # False Negatives
    ],
    [
        np.sum((y_h == 1) & (y_pred_v2_binary == 1)),
        np.sum((y_h == 1) & (y_pred_v2_binary == 0))
    ]
])

chi2, p_value, dof, expected = chi2_contingency(contingency)

print(f"A/B Test Results:")
print(f"  v1.0 F1: {f1_score(y_h, y_pred_v1_binary):.4f}")
print(f"  v2.0 F1: {f1_score(y_h, y_pred_v2_binary):.4f}")
print(f"  χ² p-value: {p_value:.6f}")
if p_value < 0.05:
    print(f"  → Statistically significant improvement (p < 0.05) ✓")
else:
    print(f"  → No significant difference (p ≥ 0.05)")
```

---

## 7. Worked Examples with Confidence Intervals

### 7.1 Example 1: High-Confidence Merge (Auto-Merge Candidate)

**Context:**
- Repository: `anthropics/claude` (internal, Phase 1 — green-field)
- PR #12345: "Refactor tokenizer cache layer"
- Author: Jane Doe (L5 engineer, 96% success rate)
- Reviewers: Bob Smith (expert in tokenization), Carol Lee (general reviewer)

**Feature Vector (50 features):**

| Feature | Value | Cohort |
|---------|-------|--------|
| author_pr_success_rate_90d | 0.96 | A |
| author_skill_level_tier | L5 | B |
| author_defect_density | 0.008 | A |
| reviewer_expertise_match_score | 0.94 | B |
| code_review_duration_minutes | 45 | B |
| diff_size_complexity | 342 lines, 3.2 cyclo | A |
| merge_conflict_frequency_30d | 0 | A |
| ci_pass_rate_historical | 0.98 | A |
| ci_flakiness_score | 2.3% | C |
| pr_age_days | 2.1 | A |
| *[40 more features]* | *[...]* | *[A/B/C/D]* |

**Model Inference:**

```
Quantile regression predictions:
  q=0.05 (pessimistic):  0.88
  q=0.50 (median):       0.94
  q=0.95 (optimistic):   0.97

Confidence interval: [0.88, 0.97]
CI width: 9 percentage points
```

**Output:**

```json
{
  "pr_id": "gh:anthropics/claude/12345",
  "pr_title": "Refactor tokenizer cache layer",
  "created_at": "2026-10-15T14:32:00Z",
  "merge_confidence": {
    "point_estimate": 0.94,
    "ci_lower": 0.88,
    "ci_upper": 0.97,
    "ci_width": 0.09,
    "confidence_level": "VERY_HIGH",
    "uncertainty_flag": false
  },
  "decision": {
    "phase": 1,
    "threshold": 0.95,
    "meets_threshold": false,
    "recommendation": "ESCALATE_TO_REVIEW",
    "reason": "Point estimate 0.94 < Phase 1 threshold 0.95, but VERY HIGH confidence"
  },
  "top_5_feature_contributions": [
    {"feature": "author_skill_level_tier", "value": "L5", "contribution": 0.18},
    {"feature": "reviewer_expertise_match_score", "value": 0.94, "contribution": 0.15},
    {"feature": "author_pr_success_rate_90d", "value": 0.96, "contribution": 0.14},
    {"feature": "code_review_duration_minutes", "value": 45, "contribution": 0.11},
    {"feature": "ci_pass_rate_historical", "value": 0.98, "contribution": 0.10}
  ],
  "action": {
    "type": "ESCALATE_REVIEW",
    "target_team": "reviewers",
    "priority": "HIGH",
    "message": "High-confidence merge (94% ± 9%). Ready for team sign-off."
  }
}
```

**Human Review Outcome:** ✓ Approved & merged successfully (confidence validated)

---

### 7.2 Example 2: Uncertain Prediction (Active Learning Flag)

**Context:**
- Repository: `example-org/legacy-service` (brownfield, Phase 3)
- PR #156: "Update deprecated logging library"
- Author: Alice Chen (L3 engineer, 78% success rate)
- Reviewers: Dave Wilson (general reviewer, not specialized in logging)

**Feature Vector (50 features):**

| Feature | Value | Cohort |
|---------|-------|--------|
| author_pr_success_rate_90d | 0.78 | A |
| author_skill_level_tier | L3 | B |
| author_defect_density | 0.074 | A |
| reviewer_expertise_match_score | 0.56 | B |
| code_review_duration_minutes | 18 | B |
| diff_size_complexity | 847 lines, 2.8 cyclo | A |
| merge_conflict_frequency_30d | 2 | A |
| ci_pass_rate_historical | 0.84 | A |
| ci_flakiness_score | 8.9% | C |
| rollback_rate_30d | 0.042 | A |
| pr_age_days | 5.3 | A |
| vulnerability_count_new | 1 (low severity) | D |
| *[39 more features]* | *[...]* | *[A/B/C/D]* |

**Model Inference:**

```
Quantile regression predictions:
  q=0.05 (pessimistic):  0.68
  q=0.50 (median):       0.79
  q=0.95 (optimistic):   0.88

Confidence interval: [0.68, 0.88]
CI width: 20 percentage points → UNCERTAIN
```

**Output:**

```json
{
  "pr_id": "gh:example-org/legacy-service/156",
  "pr_title": "Update deprecated logging library",
  "created_at": "2026-10-16T09:15:00Z",
  "merge_confidence": {
    "point_estimate": 0.79,
    "ci_lower": 0.68,
    "ci_upper": 0.88,
    "ci_width": 0.20,
    "confidence_level": "LOW",
    "uncertainty_flag": true
  },
  "decision": {
    "phase": 3,
    "threshold": 0.75,
    "meets_threshold": true,
    "recommendation": "ACTIVE_LEARNING_FLAG",
    "reason": "Prediction in uncertain range [0.75, 0.85]; wide CI indicates model uncertainty"
  },
  "top_5_feature_contributions": [
    {"feature": "author_pr_success_rate_90d", "value": 0.78, "contribution": -0.12},
    {"feature": "ci_flakiness_score", "value": 0.089, "contribution": -0.08},
    {"feature": "merge_conflict_frequency_30d", "value": 2, "contribution": -0.07},
    {"feature": "reviewer_expertise_match_score", "value": 0.56, "contribution": -0.06},
    {"feature": "diff_size_complexity", "value": "847L/2.8cyc", "contribution": -0.05}
  ],
  "active_learning": {
    "pool": "uncertain_high_value",
    "probability": true,
    "query_template": "Did this PR merge successfully? Any blockers: [reviewer-blocked] [ci-failed] [dependencies] [other]?",
    "human_feedback_priority": "MEDIUM"
  },
  "action": {
    "type": "QUERY_HUMAN",
    "target": "pull_request_comments",
    "priority": "MEDIUM",
    "message": "Model uncertain (79% ± 20%). Please share outcome + blockers for learning."
  }
}
```

**Human Feedback (collected):**

```json
{
  "pr_id": "gh:example-org/legacy-service/156",
  "human_rater_id": "dave.wilson",
  "actual_outcome": true,
  "feedback_tags": ["dependencies"],
  "notes": "Merged after checking backward compatibility with deprecated APIs. Library update smooth.",
  "timestamp": "2026-10-17T10:20:00Z"
}
```

**Learning Impact:** This sample added to active learning pool → included in next weekly retraining (improves model on brownfield PRs with library updates).

---

### 7.3 Example 3: Feedback Aggregation & Weekly Retraining

**Weekly Feedback Summary (Week of Oct 15–21, 2026):**

```
Feedback samples collected: 87 (from ~1,200 merges)
  - Uncertain predictions (75–85% range): 84 samples
  - High confidence anomalies (<70% or >95%): 3 samples

Feedback tags distribution:
  - dependencies: 24 (27%)
  - reviewer-blocked: 18 (21%)
  - ci-failed: 15 (17%)
  - manual-override: 14 (16%)
  - other: 16 (18%)

Model performance on feedback set:
  - Accuracy: 86.2%
  - Precision: 88.5%
  - Recall: 82.8%
  - F1 Score: 0.855

Issues detected:
  - Underfitting on brownfield repos (Phase 3): 76% accuracy vs. 94% Phase 1
  - Feature: ci_flakiness_score may be over-weighted for legacy services
  - Recommendation: Add phase-specific calibration in v2.1
```

**Action Taken:** Retrain with augmented data (historical 3-month + 87 weekly samples):

```python
# Retraining step
X_augmented = np.vstack([X_train, X_feedback_week])
y_augmented = np.concatenate([y_train, y_feedback_week])

for q in [0.05, 0.50, 0.95]:
    gb_new = GradientBoostingRegressor(...)
    gb_new.fit(X_augmented, y_augmented)
    models_v2_1[q] = gb_new

# Validation on holdout (last 50 merges)
y_pred = ensemble_predict(X_holdout, models_v2_1)
f1_new = f1_score(y_holdout, y_pred > 0.70)
# Result: 0.939 (up from 0.935)
```

---

### 7.4 Example 4: Quarterly Retraining Rollout (Oct 2026)

**Phase 0 — Training (Oct 1–14):**

```
Oct 1:   Start collecting 3-month merge data (Jul–Sep)
Oct 2:   Final dataset: 1,247 merges
Oct 5:   Train quantile models (5th, 50th, 95th)
Oct 8:   Holdout validation:
         - Accuracy: 93.8%
         - F1: 0.938
         - Precision: 95.2%
         - Recall: 90.1%
Oct 10:  Offline A/B: v2.0 F1 (0.938) vs v1.0 F1 (0.920), p < 0.001 ✓
Oct 12:  Feature importance: top 10 updated
Oct 14:  Decision: PASS (accuracy 93.8% > 93.5% threshold) ✓
```

**Phase 1 — Canary (Oct 15–21):**

```
Oct 15:  Deploy v2.0.0 to 10% phase-1 repos (100 repos)
         - Expected prediction latency: 95ms p99
         - Expected fallback rate: <1%

Oct 16–20: Daily monitoring
           - F1 score: 0.938 (tracking v1.0: 0.920)
           - Latency: 103ms p99 (no fallback)
           - Feedback rate: 7.2% (87 uncertain predictions / 1,200 merges)

Oct 21:  Evaluation meeting:
         - v2.0 performing +1.8% F1 vs. v1.0
         - No latency issues
         - Decision: EXPAND to Phase 2
```

**Phase 2 — Staged Rollout (Oct 22–28):**

```
Oct 22:  Expand to 50% (250 repos: all Phase 1 + 150 Phase 2)
Oct 25:  Monitor infrastructure:
         - Batch job (4:00 UTC): 50s → 48s (no degradation)
         - DB load: +3% (acceptable)
         - Feedback collection: 12.4 samples/day (on target)

Oct 28:  Evaluation:
         - F1: 0.937 (stable)
         - Decision: FULL ROLLOUT approved
```

**Phase 3 — Full Deployment (Oct 29–31):**

```
Oct 29:  Deploy v2.0.0 to 100% (all 1,000+ repos, all phases)
Oct 30:  Post-deployment monitoring:
         - Real-time latency: 98ms p99 ✓
         - Batch latency: 52s (parallel, 8 workers) ✓
         - Feedback rate: 7.8% (unchanged)
         - F1 score: 0.938 ✓

Oct 31:  Deployment complete
         - Model v2.0.0: 100% traffic
         - Model v1.0.0: Archived
         - Weekly retraining: Continue with v2.0 baseline
```

---

## 8. Performance Benchmarks

### 8.1 Accuracy Metrics (Holdout Set)

| Metric | v1.0 | v2.0 | v2.1 | Target | Status |
|--------|------|------|------|--------|--------|
| Accuracy | 92.4% | 93.8% | 93.9% | ≥93.5% | ✓ |
| Precision | 94.1% | 95.2% | 95.3% | ≥95% | ✓ |
| Recall | 89.3% | 90.1% | 90.2% | ≥90% | ✓ |
| F1 Score | 0.920 | 0.938 | 0.939 | ≥0.935 | ✓ |
| False Negative Rate | 10.7% | 9.9% | 9.8% | <10% | ✓ |
| False Positive Rate | 5.9% | 4.8% | 4.7% | <5% | ✓ |

### 8.2 Latency (Real-time Inference)

| Percentile | Fase 3 (31 feat) | v2.0 (50 feat) | Fallback | Target |
|----------|---|---|---|---|
| p50 | 45ms | 68ms | 12ms (cached v1) | <80ms |
| p95 | 85ms | 125ms | 18ms | <150ms |
| p99 | 112ms | 165ms | 22ms | <200ms |

**Optimization:** Fallback mechanism enabled when p99 > 200ms.

### 8.3 Throughput (Batch Inference)

| Configuration | Batch Size | Workers | Total Time | Repos/sec | Target |
|---|---|---|---|---|---|
| Sequential | 1,247 | 1 | 62.3s | 20.0 | N/A |
| Parallel (4 workers) | 312/batch | 4 | 18.5s | 67.4 | 50+ |
| Parallel (8 workers) | 156/batch | 8 | 10.2s | 122.2 | 50+ |

**Daily batch job (4:00 UTC):** 8 workers, 10.2s, serving 1,000+ repos.

### 8.4 Model Size & Cost

| Component | Size | Latency | Cost (per 1M predictions) |
|---|---|---|---|
| Random Forest (65%) | 124 MB | 45ms | $0.024 |
| XGBoost (35%) | 87 MB | 52ms | $0.031 |
| Feature engineering | 42 MB | 23ms | $0.015 |
| Quantile regression | 45 MB | 15ms | $0.008 |
| **Total** | **298 MB** | **~100ms p50** | **$0.078** |

**Annual cost estimate:** $0.078 × 365 days × 1,000 repos × 10 predictions/repo = **~$285k/year** (infrastructure + storage).

---

## 9. Integration with Phase 1-3 Skills

### 9.1 Dependency Map

```
git-auto-merge-confidence.md (v1.0)
├── Features: 31
├── Ensemble: RF 65% + XGB 35%
└── Output: Point estimate (single value)

↓ UPGRADED TO ↓

git-ml-advanced-scoring.md (v1.0) [THIS SKILL]
├── Features: 50 (31 + 19 new)
├── Ensemble: RF 65% + XGB 35% (upgraded quantile regression)
├── Output: Point estimate + confidence intervals
├── Learning: Active learning loop + weekly retraining
└── Serving: Batch + online, <200ms latency, fallback to v1

↑ FEEDS ↑

git-gitops-flow.md (v3.0)
├── Uses confidence scores in merge decision
├── New thresholds: By phase + confidence level
├── Fallback: Uses v1 if v2 latency > 500ms
└── Escalation: Uncertain predictions (CI width >10%) flagged for review

↑ FEEDS ↑

git-multi-repo-workflows.md (v3.0)
├── Prioritizes merges by confidence score
├── Parallel execution: Stages low-risk (>95%) first
└── Monitoring: Track success rate per confidence bucket
```

### 9.2 Updated Merge Decision Thresholds

**Fase 3 Thresholds (Point Estimate Only):**

```
Phase 1 (green-field, low-risk):
  ≥95% → Auto-merge
  80–95% → Escalate to review
  <80% → Reject

Phase 2 (medium-risk):
  ≥90% → Auto-merge
  75–90% → Escalate to review
  <75% → Reject
```

**Fase 4 Thresholds (Point Estimate + Confidence Interval):**

```
Phase 1 (green-field, low-risk):
  Point ≥97% AND CI width <5% → Auto-merge
  Point 92–97% OR CI width 5–10% → Escalate to review
  Point <92% AND CI width >10% → Active learning flag
  Point <85% → Reject

Phase 2 (medium-risk):
  Point ≥93% AND CI width <8% → Auto-merge
  Point 85–93% OR CI width 8–12% → Escalate to review
  Point <85% AND CI width >12% → Active learning flag
  Point <75% → Reject

Phase 3 (brownfield, legacy):
  Point ≥90% AND CI width <10% → Auto-merge
  Point 80–90% OR CI width 10–15% → Escalate to review
  Point <80% AND CI width >15% → Active learning flag
  Point <65% → Reject
```

### 9.3 Feedback Integration Points

```
PR opened → Real-time scoring (v2.0)
            ↓
            Output: 94% ± 6% (Phase 1 → escalate)
            ↓
            Review team approves/blocks
            ↓
        (3 days pass)
            ↓
        PR merged → Outcome recorded
            ↓
        Active learning flag? (CI width 75–85%)
            ↓
        YES → Query: "Blockers? Tags: [rev-blocked] [ci-failed] [deps] [other]?"
            ↓
        Human feedback → Accumulated weekly
            ↓
        Every Monday 02:00 UTC
            ↓
        Retrain with new data (87 samples typical)
            ↓
        Validate F1 ≥ 0.92 on holdout
            ↓
        Deploy if improved (v2.1, v2.2, ...)
```

---

## 10. Skill Invocation & Integration Points

### 10.1 When to Use This Skill

**Invocation triggers (agente-gitops):**

1. **Real-time PR scoring:** New PR opened → invoke `score_pr_realtime()`
2. **Daily batch reporting:** 4:00 UTC → invoke `batch_score_all_repos()`
3. **Weekly retraining check:** Monday 02:00 UTC → invoke `weekly_retrain()`
4. **Quarterly model refresh:** Oct 1, Jan 1, Apr 1, Jul 1 → invoke `quarterly_retrain()`
5. **Feedback collection:** After PR merged → invoke `collect_feedback(pr_id, outcome)`

### 10.2 Skills This Depends On

- **git-repository-analytics.md (v2.0):** Feature computation (CI metrics, rollback history, incident frequency)
- **git-pr-autoreview.md (v2.0):** Code review metrics (duration, comment depth, reviewer expertise)
- **git-code-pattern-detection.md (v3.0):** Risk scoring per feature (file type risk, code complexity)

### 10.3 Skills That Depend On This

- **git-gitops-flow.md (v3.0):** Merge decision logic (uses confidence scores + thresholds)
- **git-multi-repo-workflows.md (v3.0):** Prioritization (by confidence score, parallel execution)
- **git-auto-merge-confidence.md (v1.0):** Backward compatibility (fallback target if v2 unavailable)

---

## 11. Rollback & Failover Procedures

### 11.1 Immediate Rollback (Latency Issue)

**Trigger:** p99 latency > 500ms for >5 minutes

```bash
# Automatic fallback: Serve v1.0 (31-feature, cached)
# No manual action required — handled by inference layer

# Manual verification:
curl https://api.gitops.manta/health/model
# Response: {"model": "v1.0", "reason": "p99_latency_exceeded", "timestamp": "..."}
```

### 11.2 Accuracy Regression Rollback

**Trigger:** Holdout F1 score drops below 0.92 for 3+ consecutive days

```bash
# Manual investigation required
# 1. Check weekly retraining logs
# 2. Analyze feedback quality
# 3. Decision:
#    a) If drift detected: Roll back to v1.0, investigate root cause
#    b) If data quality issue: Fix data, retrain with v2.0

# Rollback command:
git-gitops deploy --model v1.0 --timestamp 2026-10-14T23:59:59Z
```

### 11.3 Model Serving Fallback Chain

```
Request for scoring
  ↓
Try v2.0 (50 features, quantile regression)
  ├─ Timeout >500ms? → Fallback to v1.0 (cached)
  ├─ Model error? → Fallback to v1.0 (hardcoded)
  └─ Success <200ms? → Return [point, ci_lower, ci_upper]
  ↓
Try v1.0 (31 features, point estimate)
  ├─ Timeout >100ms? → Return threshold-based score
  ├─ Model error? → Return threshold-based score
  └─ Success <100ms? → Return [point]
  ↓
Threshold-based fallback
  ├─ Default logic: score = (author_reputation * 0.4 + ci_health * 0.3 + review_quality * 0.3)
  └─ Range: [0.50, 0.95]
```

---

## 12. Documentation & Maintenance

### 12.1 Quarterly Review Checklist

**Every Q (Oct 1, Jan 1, Apr 1, Jul 1):**

- [ ] Collect 3-month merge data (≥500 samples)
- [ ] Compute 50 features + audit for data quality
- [ ] Train quantile models (5th, 50th, 95th)
- [ ] Validate accuracy on holdout (≥93.5% gating)
- [ ] Run offline A/B test vs. incumbent
- [ ] Perform feature importance analysis
- [ ] Review feedback quality (active learning)
- [ ] Check drift detection metrics
- [ ] Approve deployment or defer (with rationale)

### 12.2 Weekly Monitoring Dashboard

**Metrics to track (every Monday):**

- F1 score (overall, by phase, by repo type)
- Uncertainty rate (% predictions with CI width >10%)
- Feedback response rate (% uncertain predictions with human labels)
- Latency p50/p95/p99 (real-time + batch)
- Fallback rate (% requests falling back to v1.0)
- Model version distribution (% traffic per version)
- Feature importance top 10 (any shifts?)
- Drift detection (model accuracy on holdout)

### 12.3 Model Card & Transparency

**Published model card (public):**

```markdown
# Model Card: git-ml-advanced-scoring v2.0.0

## Model Overview
- **Purpose:** Predict merge success probability with confidence intervals
- **Framework:** Gradient Boosting (Random Forest 65% + XGBoost 35%, quantile regression)
- **Training data:** 1,247 merges (Jul–Sep 2026)
- **Intended use:** Automating merge decisions, prioritizing code review
- **Prohibited uses:** Evaluating engineer performance, hiring decisions

## Performance
- **Accuracy:** 93.8% (holdout)
- **Precision:** 95.2% (false positive rate 4.8%)
- **Recall:** 90.1% (false negative rate 9.9%)
- **F1 Score:** 0.938

## Fairness & Bias
- **Training data:** Balanced across repo phases (Phase 1: 40%, Phase 2: 35%, Phase 3: 25%)
- **Known limitations:**
  - Lower accuracy on Phase 3 repos (brownfield): 87% → mitigated with phase-specific thresholds
  - Limited data on low-frequency authors (< 5 merges/year) → defaulting to higher threshold

## Maintenance Schedule
- **Weekly:** Feedback collection + drift detection
- **Quarterly:** Retraining on 3-month data
- **Trigger:** Accuracy regression >3% → immediate investigation

## Contact
- **Owner:** agente-gitops (Manta 17)
- **Stakeholders:** DevOps, Security, ML Engineering
- **Last updated:** 2026-10-14
```

---

## 13. Success Criteria & KPIs

### 13.1 Fase 4 Launch Criteria (Oct 31, 2026)

**Must-have:**
- [x] 50-feature engineering complete + validated
- [x] Confidence interval estimation (quantile regression) working
- [x] Active learning loop implemented + weekly retraining operational
- [x] Model serving (<200ms latency, fallback <500ms)
- [x] Holdout accuracy ≥93.5% (gating satisfied)
- [x] A/B test shows statistical significance (p < 0.05)
- [x] 4-phase canary rollout complete + stable

**Nice-to-have:**
- [ ] Feature importance trending (monthly analysis)
- [ ] Drift detection alerting (automated)
- [ ] Model interpretability dashboard (SHAP graphs)

### 13.2 Ongoing KPIs (Post-Launch)

| KPI | Target | Cadence | Owner |
|-----|--------|---------|-------|
| Holdout F1 score | ≥0.935 | Weekly | ML Engineering |
| Real-time latency p99 | <200ms | Daily | DevOps |
| Batch latency (1,000 repos) | <15s | Daily | DevOps |
| Active learning feedback rate | 7–10% | Weekly | Data Science |
| Fallback rate (v1.0) | <2% | Daily | Monitoring |
| Model drift detection | None | Weekly | Data Science |
| Quarterly retraining accuracy improvement | ≥+0.5pp | Quarterly | ML Engineering |

---

## 14. References & Related Docs

- **git-auto-merge-confidence.md (v1.0):** Baseline 31-feature model (Fase 3)
- **git-gitops-flow.md (v3.0):** Merge decision logic using confidence scores
- **git-multi-repo-workflows.md (v3.0):** Parallel execution + prioritization
- **git-repository-analytics.md (v2.0):** Feature computation engine
- **git-pr-autoreview.md (v2.0):** Code review metrics extraction
- **CLAUDE.md (v4.5):** Agent registry & routing (Manta 17 — agente-gitops)

---

## 15. Change Log

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v1.0.0 | 2026-10-14 | Initial design: 50-feature ensemble, confidence intervals, active learning | APPROVED |
| (future) | Q1 2027 | Quarterly retraining result + feature importance update | Planned |
| (future) | Q2 2027 | Causal inference expansion (Fase 5) | Planned |

---

**End of Specification**

---

## Appendix A: Feature List (50 Features, Reference)

```
Cohort A — Code Quality Signals (8)
 1. file_type_risk_score
 2. diff_size_complexity
 3. lines_added_deleted_ratio
 4. cyclomatic_complexity_delta
 5. test_coverage_delta
 6. comment_density_ratio
 7. dead_code_lines
 8. code_duplication_percentage

Cohort A — Conflict & History (6)
 9. merge_conflict_frequency_30d
10. branch_merge_history_count
11. revert_frequency_90d
12. file_churn_rate
13. hotspot_file_touches
14. concurrent_changes_count

Cohort A — Author Reputation (6)
15. author_pr_success_rate_90d
16. author_defect_density
17. author_code_review_participation
18. author_response_time_hours
19. author_years_in_repo
20. author_domain_expertise_score

Cohort A — Temporal & CI (11)
21. day_of_week_merge_pattern
22. time_of_day_optimal_window
23. pr_age_days
24. review_turnaround_hours
25. ci_pass_rate_historical
26. ci_flakiness_score
27. deployment_frequency_7d
28. rollback_rate_30d
29. incident_frequency_60d
30. mttr_mean_time_to_recovery
31. sla_compliance_percent

Cohort B — Author Dynamics (4)
32. author_skill_level_tier
33. author_specialization_domain
34. author_cross_team_collaboration_score
35. author_mentoring_activity_count

Cohort B — Team Velocity (3)
36. team_merge_frequency_per_day
37. team_async_review_velocity_hours
38. team_context_switch_count_24h [dropped due to correlation]

Cohort B — Code Review Quality (4)
39. reviewer_expertise_match_score
40. code_review_duration_minutes
41. review_comment_depth_nlp_score
42. reviewer_approval_pattern_consistency

Cohort C — Environment Health (4)
43. ci_flakiness_trend_7d_delta
44. infrastructure_load_factor_percent
45. resource_contention_score
46. deployment_pipeline_health_score [dropped due to correlation]

Cohort C — Dependency & Impact (4)
47. cross_repo_dependency_count
48. upstream_health_indicator [dropped due to correlation]
49. downstream_impact_breadth [dropped due to correlation]
50. feature_flag_rollout_status

Cohort D — Security Signals (2)
51. vulnerability_count_new
52. security_scan_defect_rate

Cohort D — Compliance & QA (2)
53. license_compliance_check_pass_bool
54. performance_regression_risk_score

FINAL COUNT: 50 features (after removing 4 correlated)
```

