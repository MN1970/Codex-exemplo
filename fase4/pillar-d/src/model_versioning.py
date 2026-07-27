"""
Model Versioning & A/B Testing Framework for Pillar D
Implements semantic versioning, model registry, and A/B testing
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import hashlib
import shutil

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model lifecycle status"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ABTestStatus(Enum):
    """A/B test status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModelMetadata:
    """Model metadata and provenance"""
    model_id: str
    version: str
    status: str
    model_type: str
    created_at: str
    created_by: str
    description: str
    training_dataset_size: int
    training_dataset_hash: str
    feature_count: int
    feature_names: List[str]
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    training_time_seconds: float
    inference_latency_p95_ms: float
    inference_latency_p99_ms: float
    feature_importance: Dict[str, float]
    framework_versions: Dict[str, str]
    hyperparameters: Dict[str, Any]
    parent_model_version: Optional[str] = None
    retraining_schedule: Optional[str] = None
    tags: List[str] = None


@dataclass
class ABTestConfig:
    """A/B test configuration"""
    test_id: str
    model_a_version: str
    model_b_version: str
    split_ratio: float  # 0.5 = 50-50 split
    test_duration_hours: int
    success_metric: str  # e.g., "accuracy", "f1_score"
    success_threshold: float  # Model B must exceed this
    created_at: str
    created_by: str
    description: str


@dataclass
class ABTestResult:
    """A/B test result"""
    test_id: str
    status: str
    model_a_metric: float
    model_b_metric: float
    metric_name: str
    improvement: float  # (B - A) / A * 100
    p_value: Optional[float] = None
    confidence_level: float = 0.95
    winner: Optional[str] = None  # "model_a", "model_b", "tie"
    recommendation: str = ""
    completed_at: Optional[str] = None


class ModelRegistry:
    """Central registry for all models"""

    def __init__(self, registry_dir: Path = Path("./models/registry")):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.registry_dir / "models.json"

        # Load existing registry
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, ModelMetadata]:
        """Load model registry from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
                return {
                    model_id: ModelMetadata(**model_dict)
                    for model_id, model_dict in data.items()
                }
        return {}

    def _save_registry(self):
        """Save model registry to disk"""
        data = {
            model_id: asdict(metadata)
            for model_id, metadata in self.registry.items()
        }
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def register_model(self, metadata: ModelMetadata) -> bool:
        """Register a new model"""
        model_id = metadata.model_id
        if model_id in self.registry:
            logger.warning(f"Model {model_id} already registered. Updating...")

        self.registry[model_id] = metadata
        self._save_registry()

        logger.info(f"✓ Registered model: {model_id} (v{metadata.version})")
        return True

    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata"""
        return self.registry.get(model_id)

    def get_production_models(self) -> List[ModelMetadata]:
        """Get all production models"""
        return [
            m for m in self.registry.values()
            if m.status == ModelStatus.PRODUCTION.value
        ]

    def promote_to_production(self, model_id: str) -> bool:
        """Promote model to production"""
        if model_id not in self.registry:
            logger.error(f"Model {model_id} not found")
            return False

        # Demote other production models to staging
        for m_id, metadata in self.registry.items():
            if m_id != model_id and metadata.status == ModelStatus.PRODUCTION.value:
                metadata.status = ModelStatus.STAGING.value
                logger.info(f"Demoted {m_id} to {ModelStatus.STAGING.value}")

        # Promote new model
        self.registry[model_id].status = ModelStatus.PRODUCTION.value
        self._save_registry()

        logger.info(f"✓ Promoted {model_id} to {ModelStatus.PRODUCTION.value}")
        return True

    def deprecate_model(self, model_id: str) -> bool:
        """Deprecate a model"""
        if model_id not in self.registry:
            logger.error(f"Model {model_id} not found")
            return False

        self.registry[model_id].status = ModelStatus.DEPRECATED.value
        self._save_registry()

        logger.info(f"✓ Deprecated model: {model_id}")
        return True

    def list_models(self, status: Optional[str] = None) -> List[ModelMetadata]:
        """List all models, optionally filtered by status"""
        models = list(self.registry.values())
        if status:
            models = [m for m in models if m.status == status]
        return sorted(models, key=lambda m: m.created_at, reverse=True)

    def get_model_lineage(self, model_id: str) -> List[str]:
        """Get model lineage (parent chain)"""
        lineage = [model_id]
        current = self.registry.get(model_id)

        while current and current.parent_model_version:
            lineage.append(current.parent_model_version)
            current = self.registry.get(current.parent_model_version)

        return lineage


class ABTestManager:
    """Manages A/B tests between models"""

    def __init__(self, tests_dir: Path = Path("./models/ab_tests")):
        self.tests_dir = Path(tests_dir)
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        self.tests = {}

    def create_test(
        self,
        model_a_version: str,
        model_b_version: str,
        split_ratio: float = 0.5,
        test_duration_hours: int = 24,
        success_metric: str = "accuracy",
        success_threshold: float = 0.02,
        created_by: str = "system",
        description: str = "",
    ) -> ABTestConfig:
        """Create a new A/B test"""
        test_id = f"ab_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        config = ABTestConfig(
            test_id=test_id,
            model_a_version=model_a_version,
            model_b_version=model_b_version,
            split_ratio=split_ratio,
            test_duration_hours=test_duration_hours,
            success_metric=success_metric,
            success_threshold=success_threshold,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            description=description,
        )

        self.tests[test_id] = config
        self._save_test(test_id, config)

        logger.info(f"✓ Created A/B test: {test_id}")
        logger.info(f"  Model A: {model_a_version}")
        logger.info(f"  Model B: {model_b_version}")
        logger.info(f"  Split: {split_ratio * 100:.0f}-{(1-split_ratio) * 100:.0f}")
        logger.info(f"  Duration: {test_duration_hours}h")

        return config

    def record_result(
        self,
        test_id: str,
        model_a_metric: float,
        model_b_metric: float,
        metric_name: str,
    ) -> ABTestResult:
        """Record A/B test results"""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")

        config = self.tests[test_id]
        improvement = ((model_b_metric - model_a_metric) / (model_a_metric + 1e-10)) * 100

        # Determine winner
        if model_b_metric > model_a_metric + config.success_threshold:
            winner = "model_b"
            recommendation = f"Promote {config.model_b_version} to production"
        elif model_a_metric > model_b_metric + config.success_threshold:
            winner = "model_a"
            recommendation = f"Keep {config.model_a_version} in production"
        else:
            winner = "tie"
            recommendation = "Continue testing or collect more data"

        result = ABTestResult(
            test_id=test_id,
            status=ABTestStatus.COMPLETED.value,
            model_a_metric=model_a_metric,
            model_b_metric=model_b_metric,
            metric_name=metric_name,
            improvement=improvement,
            winner=winner,
            recommendation=recommendation,
            completed_at=datetime.now().isoformat(),
        )

        self._save_result(test_id, result)

        logger.info(f"✓ A/B Test Results: {test_id}")
        logger.info(f"  {metric_name} (Model A): {model_a_metric:.4f}")
        logger.info(f"  {metric_name} (Model B): {model_b_metric:.4f}")
        logger.info(f"  Improvement: {improvement:+.2f}%")
        logger.info(f"  Winner: {winner}")
        logger.info(f"  Recommendation: {recommendation}")

        return result

    def _save_test(self, test_id: str, config: ABTestConfig):
        """Save test config to disk"""
        test_file = self.tests_dir / f"{test_id}.json"
        with open(test_file, "w") as f:
            json.dump(asdict(config), f, indent=2)

    def _save_result(self, test_id: str, result: ABTestResult):
        """Save test result to disk"""
        result_file = self.tests_dir / f"{test_id}_result.json"
        with open(result_file, "w") as f:
            json.dump(asdict(result), f, indent=2)


class ModelVersionManager:
    """Manages semantic versioning for models"""

    @staticmethod
    def parse_version(version: str) -> Tuple[int, int, int]:
        """Parse semantic version (major.minor.patch)"""
        parts = version.split(".")
        return int(parts[0]), int(parts[1]), int(parts[2])

    @staticmethod
    def increment_patch(version: str) -> str:
        """Increment patch version (bug fixes)"""
        major, minor, patch = ModelVersionManager.parse_version(version)
        return f"{major}.{minor}.{patch + 1}"

    @staticmethod
    def increment_minor(version: str) -> str:
        """Increment minor version (new features, no breaking changes)"""
        major, minor, patch = ModelVersionManager.parse_version(version)
        return f"{major}.{minor + 1}.0"

    @staticmethod
    def increment_major(version: str) -> str:
        """Increment major version (breaking changes)"""
        major, minor, patch = ModelVersionManager.parse_version(version)
        return f"{major + 1}.0.0"


class ModelCheckpoint:
    """Manages model checkpoints for archival and rollback"""

    def __init__(self, archive_dir: Path = Path("./models/archive")):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_model(self, model_version: str, model_dir: Path) -> bool:
        """Archive a model version"""
        archive_subdir = self.archive_dir / model_version
        if archive_subdir.exists():
            logger.warning(f"Model version {model_version} already archived. Skipping...")
            return False

        try:
            shutil.copytree(model_dir, archive_subdir)
            logger.info(f"✓ Archived model: {model_version} -> {archive_subdir}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive model: {e}")
            return False

    def restore_model(self, model_version: str, restore_dir: Path) -> bool:
        """Restore a model from archive"""
        archive_subdir = self.archive_dir / model_version
        if not archive_subdir.exists():
            logger.error(f"Archive for model {model_version} not found")
            return False

        try:
            shutil.copytree(archive_subdir, restore_dir, dirs_exist_ok=True)
            logger.info(f"✓ Restored model: {model_version} from archive")
            return True
        except Exception as e:
            logger.error(f"Failed to restore model: {e}")
            return False

    def list_archived_models(self) -> List[str]:
        """List all archived model versions"""
        return [d.name for d in self.archive_dir.iterdir() if d.is_dir()]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Pillar D — Model Versioning & A/B Testing")
    print("=" * 80)

    # Create registry
    print("\n[1/4] Initializing Model Registry...")
    registry = ModelRegistry()

    # Register models
    print("\n[2/4] Registering models...")
    for i in range(3):
        metadata = ModelMetadata(
            model_id=f"gitops_ensemble_v2",
            version=f"2.0.{i}",
            status="staging" if i < 2 else "production",
            model_type="ensemble",
            created_at=datetime.now().isoformat(),
            created_by="training_pipeline",
            description=f"Ensemble model iteration {i}",
            training_dataset_size=5000,
            training_dataset_hash="abc123",
            feature_count=50,
            feature_names=[f"feat_{j}" for j in range(50)],
            accuracy=0.93 + i * 0.005,
            precision=0.92 + i * 0.005,
            recall=0.94 + i * 0.005,
            f1_score=0.93 + i * 0.005,
            auc_roc=0.95 + i * 0.003,
            training_time_seconds=120,
            inference_latency_p95_ms=150,
            inference_latency_p99_ms=200,
            feature_importance={f"feat_{j}": 0.01 for j in range(50)},
            framework_versions={"sklearn": "1.3.0", "xgboost": "2.0.0"},
            hyperparameters={"rf_weight": 0.65, "xgb_weight": 0.35},
            parent_model_version="2.0.0" if i > 0 else None,
        )
        registry.register_model(metadata)

    print("✓ Registered 3 models")

    # List models
    print("\n[3/4] Model Registry Content:")
    for model in registry.list_models():
        print(f"  {model.model_id} v{model.version}: {model.status} (acc={model.accuracy:.4f})")

    # A/B Testing
    print("\n[4/4] Setting up A/B Test...")
    ab_manager = ABTestManager()
    test = ab_manager.create_test(
        model_a_version="2.0.1",
        model_b_version="2.0.2",
        split_ratio=0.5,
        test_duration_hours=24,
        success_metric="accuracy",
        success_threshold=0.01,
    )

    # Record results
    result = ab_manager.record_result(
        test.test_id,
        model_a_metric=0.935,
        model_b_metric=0.940,
        metric_name="accuracy",
    )

    print("\n✓ Model Versioning & A/B Testing Framework operational!")
