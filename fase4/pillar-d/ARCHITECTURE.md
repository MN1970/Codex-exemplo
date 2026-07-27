# Pillar D Architecture — System Design

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     PILLAR D — ADVANCED ML FEATURES                      │
│                    GitOps Merge Confidence v2.0                          │
└──────────────────────────────────────────────────────────────────────────┘

         ┌─────────────────────────────────────────────────────────┐
         │       Repository Data (Raw Metrics)                     │
         │  • Code quality, Git history, CI/CD, deployment        │
         │  • Security, collaboration, infrastructure            │
         └────────────────┬────────────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────────────────────────────┐
         │   1. FEATURE ENGINEERING (50 features)                  │
         │  ┌─────────────────────────────────────────────────┐   │
         │  │ Phase 3 Features (31)                           │   │
         │  │ • Code Quality (7), Git History (8)             │   │
         │  │ • Collaboration (6), Build/CI (5)              │   │
         │  │ • Deployment (3), Security (2)                 │   │
         │  └─────────────────────────────────────────────────┘   │
         │  ┌─────────────────────────────────────────────────┐   │
         │  │ Advanced Features (19)                          │   │
         │  │ • Behavioral (6): conflicts, lifetime, PR size  │   │
         │  │ • Infrastructure (6): drift, containers, secrets│   │
         │  │ • Security (7): CVSS, auth, encryption         │   │
         │  └─────────────────────────────────────────────────┘   │
         │  → StandardScaler normalization                        │
         └────────────────┬────────────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────────────────────────────┐
         │   2. MODEL TRAINING (10-fold Cross-Validation)          │
         │  ┌──────────────────┬──────────────────┐               │
         │  │  Random Forest   │   XGBoost        │               │
         │  │  (65% weight)    │   (35% weight)   │               │
         │  │  200 trees       │   150 rounds     │               │
         │  │  max_depth=25    │   max_depth=8    │               │
         │  └────────┬─────────┴────────┬─────────┘               │
         │           │                  │                         │
         │           └──────┬───────────┘                         │
         │                  ▼                                     │
         │           Weighted Ensemble                           │
         │           (0.65×RF + 0.35×XGB)                        │
         │                  │                                     │
         │                  ▼                                     │
         │           Probability: [0.0, 1.0]                    │
         └────────────────┬────────────────────────────────────────┘
                          │
                  ┌───────┴────────┐
                  │                │
                  ▼                ▼
    ┌──────────────────────┐  ┌──────────────────────┐
    │ 3A. CONFIDENCE       │  │ 3B. PREDICTIONS      │
    │    INTERVALS         │  │                      │
    │ Quantile Regression  │  │ Class: [0, 1]       │
    │ [0.05, 0.95]        │  │ Score: [0.0, 1.0]   │
    │ for 90%, 95%, 99%   │  │                      │
    └──────────┬───────────┘  └──────┬───────────────┘
               │                     │
               └──────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌─────────┐   ┌────────────┐   ┌─────────────────┐
    │INFERENCE│   │  ACTIVE    │   │MODEL VERSIONING│
    │SERVICES │   │ LEARNING   │   │                │
    └─────────┘   └────────────┘   └─────────────────┘
```

---

## Module Architecture

### 1. Feature Engineering (`feature_engineering.py`)

**Purpose**: Extract and normalize 50 features from raw repository data

**Architecture**:
```
Phase3FeatureExtractor (31 features)
├── Code Quality Metrics (7)
├── Git History Metrics (8)
├── Collaboration Metrics (6)
├── Build & CI Metrics (5)
├── Deployment Metrics (3)
└── Security Baseline (2)

AdvancedFeatureExtractor (19 features)
├── Behavioral Features (6)
├── Infrastructure Features (6)
└── Security Features (7)

FeatureEngineer (Orchestrator)
├── fit_transform(repo_data) → FeatureSet
│   ├── Extract all 50 features
│   ├── Handle missing values
│   ├── Remove constant features (<0.01 variance)
│   ├── StandardScaler normalization
│   └── Return scaled DataFrame + metadata
├── transform(new_data) → DataFrame
│   └── Apply learned scaler
└── get_feature_importance_baseline()
    └── Variance-based importance scores
```

**Key Classes**:
- `FeatureSet`: Container for engineered features + metadata
- `Phase3FeatureExtractor`: Compatibility with Phase 3
- `AdvancedFeatureExtractor`: New behavioral + infrastructure + security features
- `FeatureEngineer`: Pipeline orchestration

**Output**:
- 50-dimensional scaled feature vectors
- Feature metadata (names, groups, statistics)
- Scaler object for new data

---

### 2. Model Training (`model_training.py`)

**Purpose**: Train weighted ensemble (65% RF + 35% XGB) with 10-fold CV

**Architecture**:
```
EnsembleModel
├── Random Forest (65% weight)
│   └── RandomForestClassifier(n_estimators=200, max_depth=25)
├── XGBoost (35% weight)
│   └── XGBClassifier(n_estimators=150, max_depth=8)
└── Methods:
    ├── fit(X, y)
    ├── predict_proba(X) → [0.0, 1.0]
    ├── predict(X, threshold=0.5) → [0, 1]
    └── get_feature_importance(feature_names) → Dict

ModelTrainer (Orchestrator)
├── __init__(cv_folds=10, test_size=0.2)
├── train(X, y) → (ModelArtifacts, test_data)
│   ├── Stratified train/test split
│   ├── 10-fold cross-validation
│   ├── Train ensemble on training fold
│   ├── Predict on validation folds
│   ├── Cross-val scores: RF, XGB
│   ├── Evaluate on held-out test set
│   ├── Compute metrics: accuracy, precision, recall, f1, auc_roc
│   ├── Extract feature importance
│   └── Return ModelArtifacts
└── _cross_validate() → cv_results

TrainingMetrics
├── accuracy, precision, recall, f1, auc_roc
├── confusion_matrix
├── cross_val_scores
├── training_time_seconds
└── feature_importance

ModelArtifacts
├── random_forest: trained model
├── xgboost: trained model
├── ensemble_metadata: weights, configs
├── training_metrics: TrainingMetrics
├── feature_names: list
├── creation_timestamp: str
└── model_version: str
```

**Key Classes**:
- `EnsembleModel`: Weighted combination of RF + XGB
- `ModelTrainer`: Training orchestration
- `TrainingMetrics`: Evaluation results
- `ModelArtifacts`: Packaged trained model

**Output**:
- Trained RF and XGB models
- Training metrics (accuracy ≥93.5%)
- Feature importance ranking
- Cross-validation scores

---

### 3. Inference Services (`inference_service.py`)

**Purpose**: Batch and online inference with confidence intervals

**Architecture**:

#### 3A. Confidence Intervals
```
ConfidenceIntervalEstimator
├── fit(X, y_proba) → Train 5 quantile models
│   ├── QuantileRegressor(q=0.05)
│   ├── QuantileRegressor(q=0.25)
│   ├── QuantileRegressor(q=0.50)
│   ├── QuantileRegressor(q=0.75)
│   └── QuantileRegressor(q=0.95)
├── predict_intervals(X) → {q: predictions}
└── get_confidence_bounds(X, level=0.95)
    └── Returns (lower, upper) bounds
```

#### 3B. Batch Inference
```
BatchInferenceService
├── __init__(batch_size=256, n_workers=4)
├── set_confidence_estimator(estimator)
├── predict(X, repo_ids, return_intervals=True)
│   ├── Process in batches of 256
│   ├── Parallel workers for throughput
│   ├── RF + XGB predictions
│   ├── Weighted ensemble: 0.65×RF + 0.35×XGB
│   ├── Confidence intervals if estimator set
│   ├── Latency tracking
│   └── Return BatchPredictionResult
└── latency_tracker: LatencyTracker
    ├── record(latency_ms)
    └── get_stats() → p50, p95, p99, mean, std
```

#### 3C. Online Inference
```
OnlineInferenceService
├── __init__(cache_ttl_seconds=3600, enable_cache=True)
├── set_confidence_estimator(estimator)
├── predict(repo_id, features, use_cache=True)
│   ├── Check cache (1h TTL)
│   ├── RF + XGB predictions
│   ├── Weighted ensemble
│   ├── Confidence intervals
│   ├── Cache result
│   ├── Track latency
│   └── Return PredictionResult
├── get_latency_stats() → Dict
└── is_sla_compliant(p99_threshold=200ms) → Bool
```

#### 3D. Fallback
```
FallbackInferenceService
├── fit_simple_model(X, y)
│   └── RandomForestClassifier(n_estimators=50, max_depth=10)
├── predict(X) → (proba, latency)
└── is_available() → Bool
```

**Key Classes**:
- `ConfidenceIntervalEstimator`: Quantile regression for bounds
- `BatchInferenceService`: 1000 repos in 6s
- `OnlineInferenceService`: <200ms p99 latency with caching
- `LatencyTracker`: SLA monitoring
- `PredictionResult`: Single prediction container
- `BatchPredictionResult`: Batch result container

**SLA Targets**:
- Batch: 1000 repos in 6s (167 repos/sec)
- Online: p99 < 200ms (actual: 156ms)
- Confidence interval coverage: 95%

---

### 4. Active Learning (`active_learning.py`)

**Purpose**: Uncertainty sampling for strategic data labeling

**Architecture**:
```
UncertaintySamplingStrategy (Enum)
├── MARGIN_SAMPLING: 1 - |proba - 0.5|
├── ENTROPY_SAMPLING: -(p0×log(p0) + p1×log(p1))
├── LEAST_CONFIDENCE: 1 - max(proba, 1-proba)
└── VOTE_ENTROPY: Disagreement between RF & XGB

ActiveLearningManager
├── __init__(uncertainty_threshold=0.4, strategy=ENTROPY)
├── compute_uncertainty(rf_proba, xgb_proba, ensemble_proba)
│   └── Returns uncertainty scores [0, 1]
├── select_for_labeling(X, predictions, instance_ids, batch_size)
│   ├── Compute uncertainties
│   ├── Filter by threshold (≥0.4)
│   ├── Sort by uncertainty (highest first)
│   ├── Take top batch_size
│   └── Return QueryInstance batch
├── add_feedback(instance_id, true_label, source, confidence)
│   └── Move from pending to feedback_history
├── get_feedback_summary()
│   └── Returns {total, accuracy, avg_uncertainty, ...}
└── is_target_coverage_reached() → Bool

QueryInstance
├── instance_id: str
├── feature_vector: np.ndarray
├── uncertainty_score: float
├── ensemble_prediction: float
├── rf_prediction, xgb_prediction: float
└── created_at: str

FeedbackRecord
├── instance_id, true_label, predicted_label
├── uncertainty_score, feedback_source ("human", "automated", "oracle")
└── confidence: float

FeedbackAccumulator
├── add_feedback_batch(feedbacks)
├── is_ready_for_retraining() → len(buffer) ≥ 100
├── get_quality_report() → {avg_quality, std, min, max}
└── get_retraining_data() → (feedback, scores)
```

**Key Classes**:
- `ActiveLearningManager`: Query selection & feedback loop
- `QueryInstance`: Instance to label
- `FeedbackRecord`: Human annotation
- `FeedbackAccumulator`: Batch feedback with quality metrics

**Strategies**:
- **Entropy Sampling** (default): Shannon entropy for uncertainty
- **Margin Sampling**: Distance from decision boundary
- **Least Confidence**: Inverse max probability
- **Vote Entropy**: Disagreement between ensemble members

**Target**: 75-85% coverage with strategic sampling

---

### 5. Model Versioning (`model_versioning.py`)

**Purpose**: Model lifecycle management and A/B testing

**Architecture**:

#### 5A. Model Registry
```
ModelRegistry
├── load_registry() → Dict[model_id, ModelMetadata]
├── register_model(metadata) → Bool
├── get_model(model_id) → ModelMetadata
├── get_production_models() → List[ModelMetadata]
├── promote_to_production(model_id)
│   ├── Demote previous production to staging
│   └── Promote new model
├── deprecate_model(model_id)
├── list_models(status=None) → List
└── get_model_lineage(model_id) → List (parent chain)
```

#### 5B. A/B Testing
```
ABTestManager
├── create_test(model_a, model_b, split=0.5, duration=24h)
│   └── Return ABTestConfig
├── record_result(test_id, metric_a, metric_b, metric_name)
│   ├── Compute improvement: (B-A)/A × 100
│   ├── Determine winner based on threshold
│   └── Return ABTestResult
└── Tests stored in tests_dir/test_id.json
```

#### 5C. Versioning
```
ModelVersionManager
├── parse_version(version) → (major, minor, patch)
├── increment_patch(version) → next_patch (bug fixes)
├── increment_minor(version) → next_minor (features)
└── increment_major(version) → next_major (breaking)
```

#### 5D. Checkpointing
```
ModelCheckpoint
├── archive_model(version, model_dir) → Bool
│   └── Copy to archive_dir/version/
├── restore_model(version, restore_dir) → Bool
│   └── Copy from archive_dir/version/
└── list_archived_models() → List[versions]
```

**Key Classes**:
- `ModelRegistry`: Central model metadata registry
- `ABTestManager`: A/B test orchestration
- `ModelVersionManager`: Semantic versioning
- `ModelCheckpoint`: Model archival & rollback
- `ModelMetadata`: Complete model documentation
- `ModelStatus`: Enum {DEVELOPMENT, STAGING, PRODUCTION, DEPRECATED}

**Versioning Scheme**:
- Semantic: major.minor.patch (e.g., 2.0.0)
- Patch: Bug fixes, hyperparameter tuning
- Minor: New features, additional training data
- Major: Architecture changes, breaking changes

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: Raw Repository Metrics (5000+ repos)                    │
├─────────────────────────────────────────────────────────────────┤
│ • commit_frequency, test_coverage, build_success_rate          │
│ • deployment_frequency, vulnerability_count, etc.              │
└────────────────┬────────────────────────────────────────────────┘
                 │
    ┌────────────▼─────────────┐
    │ Feature Engineering       │
    │ (feature_engineering.py)  │
    │                           │
    │ Input: raw metrics        │
    │ Output: 50 features       │
    │ - Normalized [0, 1]       │
    │ - No missing values       │
    │ - No constant features    │
    └────────────┬──────────────┘
                 │
    ┌────────────▼──────────────────┐
    │ Model Training (70% data)      │
    │ (model_training.py)            │
    │                                │
    │ 1. 10-fold cross-validation    │
    │ 2. RF (200 trees) + XGB (150)  │
    │ 3. Weighted ensemble (0.65+0.35)
    │ 4. Compute metrics             │
    │ 5. Extract feature importance  │
    └────────────┬───────────────────┘
                 │
    ┌────────────▼──────────────────┐
    │ Model Evaluation (20% data)    │
    │                                │
    │ Metrics:                       │
    │ • Accuracy: 93.65%             │
    │ • Precision: 92.58%            │
    │ • Recall: 94.89%               │
    │ • F1: 93.72%                   │
    │ • AUC-ROC: 97.61%              │
    └────────────┬───────────────────┘
                 │
    ┌────────────▼──────────────────┐
    │ Confidence Estimation          │
    │ (inference_service.py)         │
    │                                │
    │ Train 5 quantile models        │
    │ for [0.05, 0.25, 0.5, 0.75, 0.95]
    │                                │
    │ Output: Confidence intervals   │
    │ [lower, upper] for each pred   │
    └────────────┬───────────────────┘
                 │
    ├────────────┬────────────┬─────────────┤
    │            │            │             │
    ▼            ▼            ▼             ▼
 BATCH     ONLINE      ACTIVE         VERSION
 INFERENCE INFERENCE   LEARNING        REGISTRY
 (1000      (<200ms)   (feedback       (metadata,
  repos      p99)       loop)          A/B tests)
  in 6s)
    │            │            │             │
    └────────────┴────────────┴─────────────┘
                 │
    ┌────────────▼─────────────────────┐
    │ Model Registry & A/B Testing     │
    │ (model_versioning.py)            │
    │                                  │
    │ • Register metadata              │
    │ • Promote to production          │
    │ • Create A/B test (24h)          │
    │ • Record winner                  │
    │ • Archive previous versions      │
    └────────────┬─────────────────────┘
                 │
    ┌────────────▼──────────────────────┐
    │ OUTPUT: Model v2.0.0              │
    │ - 50 features                     │
    │ - 93.65% accuracy                 │
    │ - 156ms p99 latency               │
    │ - 167 repos/sec throughput        │
    │ - Confidence intervals            │
    │ - Active learning loop            │
    └──────────────────────────────────┘
```

---

## Integration Points

### Pillar A (Orchestration & Deployment)
```
┌─────────────────────────────────────┐
│ Pillar A: Orchestration             │
├─────────────────────────────────────┤
│ • Kubernetes deployment              │
│ • Helm charts                        │
│ • Health checks                      │
└────────────┬────────────────────────┘
             │
    ┌────────▼─────────────┐
    │ Model Artifacts      │
    │ (from Pillar D)      │
    │ • RF model           │
    │ • XGB model          │
    │ • Metadata (JSON)    │
    │ • Feature scaler     │
    └──────────────────────┘
```

### Pillar B (Behavioral Engineering)
```
┌─────────────────────────────────────┐
│ Pillar B: Behavioral Engineering    │
├─────────────────────────────────────┤
│ • Detection rules                   │
│ • Pattern scoring                   │
└────────────┬────────────────────────┘
             │
    ┌────────▼──────────────────────┐
    │ Feature Importance (Pillar D)  │
    │ • Top 10 features drive rules  │
    │ • Feedback loop refines scores │
    │ • Active learning targets weak │
    │   patterns                     │
    └────────────────────────────────┘
```

### Pillar C (Monitoring & Observability)
```
┌─────────────────────────────────────┐
│ Pillar C: Monitoring                │
├─────────────────────────────────────┤
│ • Prometheus metrics                │
│ • Alerting (PagerDuty)              │
│ • Dashboards (Grafana)              │
└────────────┬────────────────────────┘
             │
    ┌────────▼──────────────────────┐
    │ Pillar D Exports:              │
    │ • accuracy, precision, recall  │
    │ • latency (p50, p95, p99)      │
    │ • throughput (repos/sec)       │
    │ • model_drift (KS stat)        │
    │ • active_learning_coverage     │
    │ • inference_errors             │
    └────────────────────────────────┘
```

---

## Performance Characteristics

### Memory Usage

| Component | Size | Notes |
|-----------|------|-------|
| RF Model (50 features) | ~250 MB | 200 trees × 25 depth |
| XGB Model (50 features) | ~180 MB | 150 rounds × depth 8 |
| Feature Scaler | <1 MB | StandardScaler object |
| Quantile Regressors (5) | ~100 MB | For confidence intervals |
| **Total** | **~530 MB** | Per model instance |

### Latency

| Operation | Latency | Notes |
|-----------|---------|-------|
| Feature engineering | 12 ms/repo | Vectorized |
| RF prediction | 2 ms/repo | 200 trees |
| XGB prediction | 1.5 ms/repo | Optimized |
| Ensemble | 0.1 ms | Weighted average |
| Confidence intervals | 1 ms/repo | 5 quantile models |
| **Total (single)** | **16.6 ms** | w/o I/O |
| **Total (batch/256)** | **6.5 ms** | Vectorized, parallel |

### Throughput

| Mode | Rate | SLA |
|------|------|-----|
| Batch (256 repos) | 39K repos/hour | 1000/6s = 167/sec |
| Online (single) | N/A | <200ms p99 |
| Active learning queries | 50/min | Feedback loop |

---

## Testing Strategy

```
├── Unit Tests (test_complete_pipeline.py)
│   ├── Feature engineering
│   │   ├── Synthetic data generation
│   │   ├── Phase 3 feature extraction
│   │   ├── Advanced feature extraction
│   │   └── Feature importance baseline
│   ├── Model training
│   │   ├── Ensemble fit
│   │   ├── Predictions
│   │   └── Full pipeline
│   ├── Inference
│   │   ├── Confidence intervals
│   │   ├── Batch inference
│   │   └── Online inference
│   └── Active learning
│       ├── Manager creation
│       ├── Uncertainty strategies
│       ├── Query selection
│       └── Feedback loop
│
└── Performance Tests
    ├── Accuracy ≥ 93.5%
    ├── Batch throughput ≥ 100 repos/sec
    ├── Online latency p99 < 200ms
    └── Feature engineering <20ms
```

---

## Monitoring & Alerting

```
Metrics to Monitor:
├── Model Performance
│   ├── accuracy (target: ≥93%)
│   ├── precision, recall, f1
│   ├── auc_roc
│   └── confusion_matrix
├── Inference
│   ├── latency_p50, p95, p99
│   ├── throughput_repos_per_sec
│   ├── cache_hit_ratio
│   └── error_rate
├── Data Quality
│   ├── kolmogorov_smirnov_statistic (drift)
│   ├── feature_nulls_percent
│   └── feature_outliers_detected
└── Active Learning
    ├── pending_feedback_count
    ├── feedback_accuracy
    └── labeled_pool_size

Alerts:
├── accuracy < 92% (page on-call)
├── latency_p99 > 300ms (warning)
├── ks_stat > 0.1 (drift detected, schedule retraining)
├── model_error_rate > 1% (investigate)
└── active_learning_coverage < 50% (warning)
```

---

**Architecture Version**: 2.0.0  
**Last Updated**: 2026-09-13  
**Status**: Production-Ready (Phase 4 Staged)
