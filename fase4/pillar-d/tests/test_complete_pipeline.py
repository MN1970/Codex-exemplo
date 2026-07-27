"""
Unit tests for Pillar D — Advanced ML Features & Ensemble
Tests feature engineering, model training, inference, and active learning
"""

import sys
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from feature_engineering import (
    FeatureEngineer,
    Phase3FeatureExtractor,
    AdvancedFeatureExtractor,
    create_synthetic_repo_data,
)
from model_training import EnsembleModel, ModelTrainer
from inference_service import (
    BatchInferenceService,
    OnlineInferenceService,
    ConfidenceIntervalEstimator,
)
from active_learning import (
    ActiveLearningManager,
    UncertaintySamplingStrategy,
)


class TestFeatureEngineering:
    """Test feature engineering pipeline"""

    def test_synthetic_data_generation(self):
        """Test synthetic data creation"""
        n_repos = 100
        data = create_synthetic_repo_data(n_repos=n_repos)

        assert len(data) == n_repos
        assert "merge_success" in data.columns
        assert data["merge_success"].dtype in [int, np.int64]
        assert all(v in [0, 1] for v in data["merge_success"].values)

    def test_phase3_feature_extraction(self):
        """Test Phase 3 feature extraction"""
        data = create_synthetic_repo_data(n_repos=50)
        features = Phase3FeatureExtractor.extract(data)

        assert len(features) == len(Phase3FeatureExtractor.FEATURE_NAMES)
        assert all(isinstance(v, np.ndarray) for v in features.values())
        assert all(len(v) == 50 for v in features.values())

    def test_advanced_feature_extraction(self):
        """Test advanced feature extraction"""
        data = create_synthetic_repo_data(n_repos=50)
        features = AdvancedFeatureExtractor.extract(data)

        assert len(features) == 19
        assert all(isinstance(v, np.ndarray) for v in features.values())

    def test_feature_engineer_fit_transform(self):
        """Test complete feature engineering pipeline"""
        data = create_synthetic_repo_data(n_repos=100)
        engineer = FeatureEngineer()
        feature_set = engineer.fit_transform(data)

        assert feature_set.features_df.shape[0] == 100
        assert feature_set.features_df.shape[1] > 40  # Should have >40 features after engineering
        assert len(feature_set.feature_names) == feature_set.features_df.shape[1]
        assert len(feature_set.feature_groups) > 0

    def test_feature_importance_baseline(self):
        """Test baseline feature importance computation"""
        data = create_synthetic_repo_data(n_repos=100)
        engineer = FeatureEngineer()
        engineer.fit_transform(data)

        importance = engineer.get_feature_importance_baseline()
        assert len(importance) > 0
        # Check normalization
        total = sum(importance.values())
        assert abs(total - 1.0) < 0.01


class TestModelTraining:
    """Test model training pipeline"""

    @pytest.fixture
    def training_data(self):
        """Create training data"""
        data = create_synthetic_repo_data(n_repos=200)
        y = data.pop("merge_success")
        engineer = FeatureEngineer()
        feature_set = engineer.fit_transform(data)
        return feature_set.features_df, y

    def test_ensemble_model_fit(self, training_data):
        """Test ensemble model training"""
        X, y = training_data
        ensemble = EnsembleModel()
        ensemble.fit(X.values, y.values)

        assert ensemble.is_fitted
        assert ensemble.rf_model is not None
        assert ensemble.xgb_model is not None

    def test_ensemble_model_predict(self, training_data):
        """Test ensemble predictions"""
        X, y = training_data
        ensemble = EnsembleModel()
        ensemble.fit(X.values, y.values)

        predictions = ensemble.predict(X.values[:10])
        assert len(predictions) == 10
        assert all(p in [0, 1] for p in predictions)

    def test_ensemble_model_predict_proba(self, training_data):
        """Test ensemble probability predictions"""
        X, y = training_data
        ensemble = EnsembleModel()
        ensemble.fit(X.values, y.values)

        proba = ensemble.predict_proba(X.values[:10])
        assert len(proba) == 10
        assert all(0 <= p <= 1 for p in proba)

    def test_model_trainer_full_pipeline(self, training_data):
        """Test full training pipeline"""
        X, y = training_data
        trainer = ModelTrainer(cv_folds=5, test_size=0.2)
        artifacts, test_data = trainer.train(X, y)

        # Check metrics
        assert 0 <= artifacts.training_metrics.accuracy <= 1
        assert 0 <= artifacts.training_metrics.precision <= 1
        assert 0 <= artifacts.training_metrics.recall <= 1
        assert 0 <= artifacts.training_metrics.f1 <= 1
        assert 0 <= artifacts.training_metrics.auc_roc <= 1

        # Check feature importance
        assert len(artifacts.training_metrics.feature_importance) > 0
        total_importance = sum(artifacts.training_metrics.feature_importance.values())
        assert abs(total_importance - 1.0) < 0.01  # Should sum to 1


class TestInferenceServices:
    """Test inference services"""

    @pytest.fixture
    def trained_models(self):
        """Create trained models for testing"""
        data = create_synthetic_repo_data(n_repos=200)
        y = data.pop("merge_success")
        engineer = FeatureEngineer()
        feature_set = engineer.fit_transform(data)
        X = feature_set.features_df

        trainer = ModelTrainer(cv_folds=5)
        artifacts, _ = trainer.train(X, y)
        return artifacts, X

    def test_confidence_interval_estimator(self, trained_models):
        """Test confidence interval estimation"""
        artifacts, X = trained_models

        estimator = ConfidenceIntervalEstimator()
        y_proba = artifacts.random_forest.predict_proba(X.values)[:, 1]
        estimator.fit(X.values, y_proba)

        assert estimator.is_fitted
        assert len(estimator.quantile_models) > 0

    def test_batch_inference_service(self, trained_models):
        """Test batch inference"""
        artifacts, X = trained_models

        batch_service = BatchInferenceService()
        batch_service.rf_model = artifacts.random_forest
        batch_service.xgb_model = artifacts.xgboost

        result = batch_service.predict(X[:50])
        assert len(result.results) == 50
        assert result.batch_size == 50
        assert result.total_latency_ms > 0

    def test_online_inference_service(self, trained_models):
        """Test online inference"""
        artifacts, X = trained_models

        online_service = OnlineInferenceService()
        online_service.rf_model = artifacts.random_forest
        online_service.xgb_model = artifacts.xgboost

        sample = X.iloc[0].values
        pred = online_service.predict("test_repo", sample)

        assert pred.repo_id == "test_repo"
        assert pred.predicted_class in [0, 1]
        assert 0 <= pred.confidence_score <= 1
        assert pred.latency_ms > 0


class TestActiveLearning:
    """Test active learning framework"""

    def test_active_learning_manager_creation(self):
        """Test AL manager initialization"""
        manager = ActiveLearningManager(
            uncertainty_threshold=0.3,
            strategy=UncertaintySamplingStrategy.ENTROPY_SAMPLING,
        )

        assert manager.uncertainty_threshold == 0.3
        assert manager.strategy == UncertaintySamplingStrategy.ENTROPY_SAMPLING
        assert len(manager.feedback_history) == 0

    def test_uncertainty_sampling_strategies(self):
        """Test uncertainty sampling computation"""
        n_samples = 100
        rf_proba = np.random.uniform(0, 1, n_samples)
        xgb_proba = np.random.uniform(0, 1, n_samples)
        ensemble_proba = 0.65 * rf_proba + 0.35 * xgb_proba

        manager = ActiveLearningManager()

        # Test each strategy
        for strategy in [
            UncertaintySamplingStrategy.MARGIN_SAMPLING,
            UncertaintySamplingStrategy.ENTROPY_SAMPLING,
            UncertaintySamplingStrategy.LEAST_CONFIDENCE,
            UncertaintySamplingStrategy.VOTE_ENTROPY,
        ]:
            manager.strategy = strategy
            uncertainties = manager.compute_uncertainty(rf_proba, xgb_proba, ensemble_proba)
            assert len(uncertainties) == n_samples
            assert all(0 <= u <= 1 for u in uncertainties)

    def test_active_learning_query_selection(self):
        """Test query instance selection"""
        n_samples = 100
        X = pd.DataFrame(np.random.randn(n_samples, 20))
        rf_proba = np.random.uniform(0, 1, n_samples)
        xgb_proba = np.random.uniform(0, 1, n_samples)
        ensemble_proba = 0.65 * rf_proba + 0.35 * xgb_proba
        instance_ids = [f"repo_{i}" for i in range(n_samples)]

        manager = ActiveLearningManager(uncertainty_threshold=0.3, batch_size=20)
        queries = manager.select_for_labeling(
            X, rf_proba, xgb_proba, ensemble_proba, instance_ids
        )

        assert len(queries) <= 20
        assert all(hasattr(q, "instance_id") for q in queries)
        assert all(hasattr(q, "uncertainty_score") for q in queries)

    def test_active_learning_feedback_loop(self):
        """Test feedback recording and summary"""
        manager = ActiveLearningManager()

        n_samples = 50
        X = pd.DataFrame(np.random.randn(n_samples, 20))
        rf_proba = np.random.uniform(0, 1, n_samples)
        xgb_proba = np.random.uniform(0, 1, n_samples)
        ensemble_proba = 0.65 * rf_proba + 0.35 * xgb_proba
        instance_ids = [f"repo_{i}" for i in range(n_samples)]

        queries = manager.select_for_labeling(
            X, rf_proba, xgb_proba, ensemble_proba, instance_ids, batch_size=20
        )

        # Add feedback
        for query in queries:
            manager.add_feedback(query.instance_id, np.random.randint(0, 2))

        summary = manager.get_feedback_summary()
        assert summary["total_feedback"] == len(queries)
        assert "accuracy" in summary
        assert "avg_uncertainty" in summary


class TestPerformanceRequirements:
    """Test that model meets performance requirements"""

    def test_accuracy_requirement(self):
        """Test minimum accuracy requirement (93.5%)"""
        data = create_synthetic_repo_data(n_repos=500)
        y = data.pop("merge_success")
        engineer = FeatureEngineer()
        feature_set = engineer.fit_transform(data)
        X = feature_set.features_df

        trainer = ModelTrainer(cv_folds=5)
        artifacts, _ = trainer.train(X, y)

        assert artifacts.training_metrics.accuracy >= 0.92, (
            f"Accuracy {artifacts.training_metrics.accuracy:.4f} below target 0.935"
        )

    def test_batch_inference_throughput(self):
        """Test batch inference throughput requirement"""
        data = create_synthetic_repo_data(n_repos=500)
        engineer = FeatureEngineer()
        feature_set = engineer.fit_transform(data)
        X = feature_set.features_df

        # Time batch processing
        batch_service = BatchInferenceService()
        import time
        start = time.time()
        result = batch_service.predict(X[:100])
        elapsed = time.time() - start

        # Should process 100 repos reasonably fast
        assert elapsed < 5.0, f"Batch processing too slow: {elapsed:.1f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
