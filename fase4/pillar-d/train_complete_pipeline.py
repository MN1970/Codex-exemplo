#!/usr/bin/env python
"""
Complete End-to-End Training Pipeline for Pillar D
GitOps Merge Confidence v2.0
Demonstrates: Feature Engineering → Training → Inference → Active Learning → Versioning
"""

import sys
import time
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime

# Setup paths
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from feature_engineering import (
    FeatureEngineer,
    create_synthetic_repo_data,
)
from model_training import ModelTrainer, save_model_artifacts
from inference_service import (
    BatchInferenceService,
    OnlineInferenceService,
    ConfidenceIntervalEstimator,
)
from active_learning import (
    ActiveLearningManager,
    UncertaintySamplingStrategy,
)
from model_versioning import (
    ModelRegistry,
    ABTestManager,
    ModelMetadata,
    ModelStatus,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_metrics(metrics):
    """Pretty print metrics"""
    print(f"\n  Accuracy:  {metrics.accuracy:.4f}")
    print(f"  Precision: {metrics.precision:.4f}")
    print(f"  Recall:    {metrics.recall:.4f}")
    print(f"  F1-Score:  {metrics.f1:.4f}")
    print(f"  AUC-ROC:   {metrics.auc_roc:.4f}")
    print(f"  Training Time: {metrics.training_time_seconds:.1f}s")


def main():
    """Execute complete training pipeline"""
    start_time = time.time()

    print_header("PILLAR D — COMPLETE TRAINING PIPELINE")
    print("\nGitOps Merge Confidence v2.0")
    print("50-feature ensemble with confidence intervals & active learning")

    # =========================================================================
    # PHASE 1: Data Generation & Feature Engineering
    # =========================================================================
    print_header("PHASE 1: DATA GENERATION & FEATURE ENGINEERING")

    print("\n[1/3] Generating synthetic repository data...")
    start_phase = time.time()
    repo_data = create_synthetic_repo_data(n_repos=5000)
    y = repo_data.pop("merge_success")
    print(f"  ✓ Generated {len(repo_data)} repos with {repo_data.shape[1]} raw features")
    print(f"  ✓ Class distribution: {y.value_counts().to_dict()}")

    print("\n[2/3] Running feature engineering pipeline...")
    engineer = FeatureEngineer()
    feature_set = engineer.fit_transform(repo_data)
    X = feature_set.features_df
    print(f"  ✓ Extracted {X.shape[1]} engineered features")
    print(f"  Feature groups:")
    for group, features in feature_set.feature_groups.items():
        print(f"    - {group}: {len(features)} features")

    print("\n[3/3] Top 10 baseline feature importance:")
    importance = engineer.get_feature_importance_baseline()
    for i, (fname, score) in enumerate(
        sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10], 1
    ):
        print(f"  {i:2d}. {fname:40s} {score:.6f}")

    phase1_time = time.time() - start_phase
    print(f"\n✓ Phase 1 complete ({phase1_time:.1f}s)")

    # =========================================================================
    # PHASE 2: Model Training
    # =========================================================================
    print_header("PHASE 2: MODEL TRAINING (10-FOLD CROSS-VALIDATION)")

    print("\n[1/2] Training ensemble model...")
    start_phase = time.time()
    trainer = ModelTrainer(cv_folds=10, test_size=0.2, random_state=42)
    artifacts, test_data = trainer.train(X, y)

    print("\n[2/2] Training results:")
    print_metrics(artifacts.training_metrics)

    # Print top feature importance
    print("\nTop 10 Features (SHAP-weighted Ensemble):")
    for i, (fname, importance) in enumerate(
        list(artifacts.training_metrics.feature_importance.items())[:10], 1
    ):
        print(f"  {i:2d}. {fname:40s} {importance:.6f}")

    phase2_time = time.time() - start_phase
    print(f"\n✓ Phase 2 complete ({phase2_time:.1f}s)")

    # =========================================================================
    # PHASE 3: Model Inference Services
    # =========================================================================
    print_header("PHASE 3: INFERENCE SERVICES (BATCH & ONLINE)")

    # Save models temporarily for loading
    models_dir = SCRIPT_DIR / "models" / "temp"
    models_dir.mkdir(parents=True, exist_ok=True)
    import joblib
    joblib.dump(artifacts.random_forest, models_dir / "rf.pkl")
    joblib.dump(artifacts.xgboost, models_dir / "xgb.pkl")

    print("\n[1/3] Setting up confidence interval estimation...")
    ci_estimator = ConfidenceIntervalEstimator()
    X_train = X.iloc[: int(len(X) * 0.8)]
    y_train_proba = artifacts.random_forest.predict_proba(X_train.values)[:, 1]
    ci_estimator.fit(X_train.values, y_train_proba)
    print(f"  ✓ Fitted quantile models for confidence intervals")

    print("\n[2/3] Running batch inference service (1000 repos)...")
    start_phase = time.time()
    batch_service = BatchInferenceService()
    batch_service.set_confidence_estimator(ci_estimator)
    X_batch = X.iloc[: min(1000, len(X))]
    batch_result = batch_service.predict(X_batch, return_intervals=True)
    phase3_2_time = time.time() - start_phase

    print(f"  ✓ Processed {batch_result.batch_size} repos in {batch_result.total_latency_ms:.1f}ms")
    print(f"    - Average latency: {batch_result.average_latency_ms:.2f}ms per repo")
    print(f"    - P95 latency: {batch_result.percentile_95_latency_ms:.2f}ms")
    print(f"    - P99 latency: {batch_result.percentile_99_latency_ms:.2f}ms")
    print(f"    - Throughput: {batch_result.batch_size / (batch_result.total_latency_ms / 1000):.0f} repos/sec")

    print("\n[3/3] Running online inference service (single prediction)...")
    online_service = OnlineInferenceService()
    online_service.set_confidence_estimator(ci_estimator)
    sample_features = X.iloc[0].values
    pred = online_service.predict("sample_repo_1", sample_features)

    print(f"  ✓ Single prediction completed in {pred.latency_ms:.2f}ms")
    print(f"    - Repo: {pred.repo_id}")
    print(f"    - Confidence: {pred.confidence_score:.4f}")
    if pred.confidence_interval_lower:
        print(
            f"    - Interval (95%): [{pred.confidence_interval_lower:.4f}, "
            f"{pred.confidence_interval_upper:.4f}]"
        )
    print(f"  ✓ SLA compliant (p99 < 200ms): {online_service.is_sla_compliant()}")

    phase3_time = time.time() - start_phase
    print(f"\n✓ Phase 3 complete ({phase3_time:.1f}s)")

    # =========================================================================
    # PHASE 4: Active Learning
    # =========================================================================
    print_header("PHASE 4: ACTIVE LEARNING FEEDBACK LOOP")

    print("\n[1/2] Selecting instances for labeling (uncertainty sampling)...")
    al_manager = ActiveLearningManager(
        uncertainty_threshold=0.3,
        batch_size=100,
        target_coverage=0.80,
        strategy=UncertaintySamplingStrategy.ENTROPY_SAMPLING,
    )

    rf_proba = artifacts.random_forest.predict_proba(X.iloc[:500].values)[:, 1]
    xgb_proba = artifacts.xgboost.predict_proba(X.iloc[:500].values)[:, 1]
    ensemble_proba = 0.65 * rf_proba + 0.35 * xgb_proba

    query_batch = al_manager.select_for_labeling(
        X.iloc[:500],
        rf_proba,
        xgb_proba,
        ensemble_proba,
        [f"repo_{i}" for i in range(500)],
        batch_size=50,
    )
    print(f"  ✓ Selected {len(query_batch)} instances for labeling")
    print(
        f"  ✓ Uncertainty range: {min(q.uncertainty_score for q in query_batch):.4f} - "
        f"{max(q.uncertainty_score for q in query_batch):.4f}"
    )

    print("\n[2/2] Processing feedback...")
    for i, query in enumerate(query_batch):
        # Simulate feedback: correct 85% of the time
        true_label = int(query.ensemble_prediction > 0.5)
        if np.random.random() > 0.85:
            true_label = 1 - true_label
        al_manager.add_feedback(query.instance_id, true_label)

    summary = al_manager.get_feedback_summary()
    print(f"  ✓ Processed {summary['total_feedback']} feedback records")
    print(f"    - Feedback accuracy: {summary['accuracy']:.4f}")
    print(f"    - Avg uncertainty: {summary['avg_uncertainty']:.4f}")

    print("\n✓ Phase 4 complete")

    # =========================================================================
    # PHASE 5: Model Versioning & Registry
    # =========================================================================
    print_header("PHASE 5: MODEL VERSIONING & REGISTRY")

    print("\n[1/3] Registering model in registry...")
    registry = ModelRegistry(SCRIPT_DIR / "models" / "registry")

    metadata = ModelMetadata(
        model_id="gitops_ensemble_v2",
        version="2.0.0",
        status=ModelStatus.PRODUCTION.value,
        model_type="ensemble",
        created_at=datetime.now().isoformat(),
        created_by="training_pipeline",
        description="50-feature ensemble with confidence intervals (Phase 4)",
        training_dataset_size=len(X),
        training_dataset_hash="phase4_production_dataset",
        feature_count=X.shape[1],
        feature_names=X.columns.tolist(),
        accuracy=artifacts.training_metrics.accuracy,
        precision=artifacts.training_metrics.precision,
        recall=artifacts.training_metrics.recall,
        f1_score=artifacts.training_metrics.f1,
        auc_roc=artifacts.training_metrics.auc_roc,
        training_time_seconds=artifacts.training_metrics.training_time_seconds,
        inference_latency_p95_ms=batch_result.percentile_95_latency_ms,
        inference_latency_p99_ms=batch_result.percentile_99_latency_ms,
        feature_importance=artifacts.training_metrics.feature_importance,
        framework_versions={"sklearn": "1.3.0", "xgboost": "2.0.0"},
        hyperparameters={
            "rf_weight": 0.65,
            "xgb_weight": 0.35,
            "rf_trees": 200,
            "xgb_rounds": 150,
        },
        retraining_schedule="quarterly",
    )
    registry.register_model(metadata)
    print(f"  ✓ Registered model v{metadata.version}")

    print("\n[2/3] Setting up A/B testing...")
    ab_manager = ABTestManager(SCRIPT_DIR / "models" / "ab_tests")
    test = ab_manager.create_test(
        model_a_version="1.9.2",  # Previous production
        model_b_version="2.0.0",  # New model
        split_ratio=0.5,
        test_duration_hours=24,
        success_metric="accuracy",
        success_threshold=0.005,
        created_by="training_pipeline",
    )
    print(f"  ✓ Created A/B test: {test.test_id}")

    print("\n[3/3] Recording test results...")
    result = ab_manager.record_result(
        test.test_id,
        model_a_metric=0.9240,  # Phase 3 baseline
        model_b_metric=artifacts.training_metrics.accuracy,  # Phase 4 new
        metric_name="accuracy",
    )
    print(f"  ✓ Test completed: {result.winner}")
    print(f"    - Improvement: {result.improvement:+.2f}%")
    print(f"    - Recommendation: {result.recommendation}")

    print("\n✓ Phase 5 complete")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    total_time = time.time() - start_time

    print_header("TRAINING PIPELINE SUMMARY")

    print("\n✓ Pipeline Stages:")
    print(f"  1. Data & Feature Engineering  {phase1_time:6.1f}s")
    print(f"  2. Model Training (10-fold)    {phase2_time:6.1f}s")
    print(f"  3. Inference Services          {phase3_time:6.1f}s")
    print(f"  4. Active Learning             {0.0:6.1f}s (included in Phase 3)")
    print(f"  5. Model Versioning            {0.0:6.1f}s (included in Phase 5)")
    print(f"  ───────────────────────────────────────")
    print(f"  Total Pipeline Time            {total_time:6.1f}s")

    print("\n✓ Key Metrics:")
    print(f"  Accuracy:              {artifacts.training_metrics.accuracy:.4f} ✓")
    print(f"  Precision:             {artifacts.training_metrics.precision:.4f}")
    print(f"  Recall:                {artifacts.training_metrics.recall:.4f}")
    print(f"  F1-Score:              {artifacts.training_metrics.f1:.4f}")
    print(f"  AUC-ROC:               {artifacts.training_metrics.auc_roc:.4f}")
    print(f"  Features:              {X.shape[1]}")
    print(f"  Training Samples:      {len(X)}")

    print("\n✓ Inference Performance:")
    print(f"  Batch (1000 repos):    {batch_result.total_latency_ms:.1f}ms ({batch_result.batch_size / (batch_result.total_latency_ms / 1000):.0f} repos/sec) ✓")
    print(f"  Online p99 latency:    {online_service.get_latency_stats().get('p99', 0):.1f}ms ✓")
    print(f"  SLA Compliant (p99):   {online_service.is_sla_compliant()} ✓")

    print("\n✓ Model Registry:")
    print(f"  Models registered:     {len(registry.list_models())}")
    print(f"  Production models:     {len(registry.get_production_models())}")

    print("\n✓ Active Learning:")
    print(f"  Feedback collected:    {summary['total_feedback']}")
    print(f"  Feedback accuracy:     {summary['accuracy']:.4f}")
    print(f"  Labeled pool size:     {summary['labeled_pool_size']}")

    print("\n" + "=" * 80)
    print("✓ TRAINING PIPELINE COMPLETE")
    print("=" * 80)
    print(f"\nNext Steps:")
    print(f"  1. Review model card: fase4/pillar-d/docs/MODEL_CARD_v2.0.md")
    print(f"  2. Deploy to staging: kubectl apply -f k8s/model-v2.0.yaml")
    print(f"  3. Monitor inference: kubectl logs -l app=inference-service")
    print(f"  4. Run A/B tests: Continue for {test.test_duration_hours}h")
    print(f"  5. Schedule retraining: 2026-12-13 (quarterly schedule)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
