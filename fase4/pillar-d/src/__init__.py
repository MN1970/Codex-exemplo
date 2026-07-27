"""
Pillar D — Advanced ML Features & Ensemble
GitOps Merge Confidence v2.0 with 50-feature ensemble, confidence intervals,
active learning, and production serving
"""

from .feature_engineering import (
    FeatureEngineer,
    Phase3FeatureExtractor,
    AdvancedFeatureExtractor,
    create_synthetic_repo_data,
)

from .model_training import (
    EnsembleModel,
    ModelTrainer,
    TrainingMetrics,
    ModelArtifacts,
    save_model_artifacts,
)

from .inference_service import (
    BatchInferenceService,
    OnlineInferenceService,
    ConfidenceIntervalEstimator,
    PredictionResult,
    BatchPredictionResult,
    FallbackInferenceService,
)

from .active_learning import (
    ActiveLearningManager,
    FeedbackAccumulator,
    QueryInstance,
    FeedbackRecord,
    UncertaintySamplingStrategy,
)

from .model_versioning import (
    ModelRegistry,
    ABTestManager,
    ModelVersionManager,
    ModelCheckpoint,
    ModelMetadata,
    ABTestConfig,
    ModelStatus,
)

__version__ = "2.0.0"
__all__ = [
    # Feature Engineering
    "FeatureEngineer",
    "Phase3FeatureExtractor",
    "AdvancedFeatureExtractor",
    "create_synthetic_repo_data",
    # Model Training
    "EnsembleModel",
    "ModelTrainer",
    "TrainingMetrics",
    "ModelArtifacts",
    "save_model_artifacts",
    # Inference Services
    "BatchInferenceService",
    "OnlineInferenceService",
    "ConfidenceIntervalEstimator",
    "PredictionResult",
    "BatchPredictionResult",
    "FallbackInferenceService",
    # Active Learning
    "ActiveLearningManager",
    "FeedbackAccumulator",
    "QueryInstance",
    "FeedbackRecord",
    "UncertaintySamplingStrategy",
    # Model Versioning
    "ModelRegistry",
    "ABTestManager",
    "ModelVersionManager",
    "ModelCheckpoint",
    "ModelMetadata",
    "ABTestConfig",
    "ModelStatus",
]
