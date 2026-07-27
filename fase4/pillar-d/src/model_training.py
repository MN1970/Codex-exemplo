"""
Model Training Pipeline for Pillar D — Advanced ML Features & Ensemble
Implements 65% Random Forest + 35% XGBoost ensemble with cross-validation
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, train_test_split, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
import joblib
import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class TrainingMetrics:
    """Container for training and validation metrics"""
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc_roc: float
    confusion_matrix: np.ndarray
    cross_val_scores: Dict[str, np.ndarray]
    training_time_seconds: float
    feature_importance: Dict[str, float]
    threshold_metrics: Optional[Dict[str, float]] = None


@dataclass
class ModelArtifacts:
    """Container for trained models and metadata"""
    random_forest: RandomForestClassifier
    xgboost: XGBClassifier
    ensemble_metadata: Dict[str, Any]
    training_metrics: TrainingMetrics
    feature_names: list
    creation_timestamp: str
    model_version: str


class EnsembleModel:
    """Weighted ensemble combining Random Forest and XGBoost"""

    def __init__(
        self,
        rf_weight: float = 0.65,
        xgb_weight: float = 0.35,
        rf_config: Optional[Dict] = None,
        xgb_config: Optional[Dict] = None,
    ):
        self.rf_weight = rf_weight
        self.xgb_weight = xgb_weight

        # Random Forest configuration
        rf_cfg = rf_config or {}
        self.rf_model = RandomForestClassifier(
            n_estimators=rf_cfg.get("n_estimators", 200),
            max_depth=rf_cfg.get("max_depth", 25),
            min_samples_split=rf_cfg.get("min_samples_split", 5),
            min_samples_leaf=rf_cfg.get("min_samples_leaf", 2),
            max_features=rf_cfg.get("max_features", "sqrt"),
            n_jobs=rf_cfg.get("n_jobs", -1),
            random_state=rf_cfg.get("random_state", 42),
            class_weight=rf_cfg.get("class_weight", "balanced"),
            bootstrap=rf_cfg.get("bootstrap", True),
            oob_score=rf_cfg.get("oob_score", True),
        )

        # XGBoost configuration
        xgb_cfg = xgb_config or {}
        self.xgb_model = XGBClassifier(
            n_estimators=xgb_cfg.get("n_estimators", 150),
            max_depth=xgb_cfg.get("max_depth", 8),
            learning_rate=xgb_cfg.get("learning_rate", 0.1),
            subsample=xgb_cfg.get("subsample", 0.8),
            colsample_bytree=xgb_cfg.get("colsample_bytree", 0.8),
            min_child_weight=xgb_cfg.get("min_child_weight", 1),
            gamma=xgb_cfg.get("gamma", 1.0),
            reg_alpha=xgb_cfg.get("reg_alpha", 0.1),
            reg_lambda=xgb_cfg.get("reg_lambda", 1.0),
            objective=xgb_cfg.get("objective", "binary:logistic"),
            eval_metric=xgb_cfg.get("eval_metric", "logloss"),
            tree_method=xgb_cfg.get("tree_method", "hist"),
            random_state=xgb_cfg.get("random_state", 42),
            verbosity=0,
        )

        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Train both models"""
        logger.info("Training Random Forest model...")
        self.rf_model.fit(X, y)

        logger.info("Training XGBoost model...")
        self.xgb_model.fit(X, y)

        self.is_fitted = True
        logger.info("Ensemble training complete")

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probability with weighted ensemble"""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        rf_proba = self.rf_model.predict_proba(X)[:, 1]
        xgb_proba = self.xgb_model.predict_proba(X)[:, 1]

        # Weighted average
        ensemble_proba = (self.rf_weight * rf_proba + self.xgb_weight * xgb_proba)
        return ensemble_proba

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Predict class with optional threshold"""
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)

    def get_feature_importance(self, feature_names: list, top_k: int = 50) -> Dict[str, float]:
        """Aggregate feature importance from both models"""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # Get feature importances
        rf_importance = self.rf_model.feature_importances_
        xgb_importance = self.xgb_model.feature_importances_

        # Weighted average
        ensemble_importance = (
            self.rf_weight * rf_importance + self.xgb_weight * xgb_importance
        )

        # Create dictionary
        importance_dict = {
            feature_names[i]: float(ensemble_importance[i])
            for i in range(len(feature_names))
        }

        # Sort and get top k
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_importance[:top_k])


class ModelTrainer:
    """Orchestrates complete training pipeline"""

    def __init__(
        self,
        rf_config: Optional[Dict] = None,
        xgb_config: Optional[Dict] = None,
        cv_folds: int = 10,
        test_size: float = 0.2,
        random_state: int = 42,
    ):
        self.ensemble = EnsembleModel(rf_config=rf_config, xgb_config=xgb_config)
        self.cv_folds = cv_folds
        self.test_size = test_size
        self.random_state = random_state
        self.feature_names = None

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Tuple[ModelArtifacts, Dict]:
        """
        Complete training pipeline with cross-validation and metrics
        """
        import time

        start_time = time.time()

        logger.info("=" * 80)
        logger.info("Starting complete training pipeline")
        logger.info("=" * 80)

        # Store feature names
        self.feature_names = X.columns.tolist()

        # Split data
        logger.info(f"Splitting data (test_size={self.test_size})...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, stratify=y
        )
        logger.info(f"  Train: {len(X_train)}, Test: {len(X_test)}")
        logger.info(f"  Train class distribution: {y_train.value_counts().to_dict()}")

        # Train models
        logger.info(f"Training {self.cv_folds}-fold cross-validation...")
        self.ensemble.fit(X_train.values, y_train.values)

        # Cross-validation scores
        cv_results = self._cross_validate(X_train.values, y_train.values)

        # Test metrics
        y_pred_proba = self.ensemble.predict_proba(X_test.values)
        y_pred = (y_pred_proba >= 0.5).astype(int)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc_roc = roc_auc_score(y_test, y_pred_proba)
        conf_matrix = confusion_matrix(y_test, y_pred)

        training_time = time.time() - start_time

        # Feature importance
        feature_importance = self.ensemble.get_feature_importance(self.feature_names)

        # Create training metrics
        metrics = TrainingMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            auc_roc=auc_roc,
            confusion_matrix=conf_matrix,
            cross_val_scores=cv_results,
            training_time_seconds=training_time,
            feature_importance=feature_importance,
        )

        # Create model artifacts
        artifacts = ModelArtifacts(
            random_forest=self.ensemble.rf_model,
            xgboost=self.ensemble.xgb_model,
            ensemble_metadata={
                "rf_weight": self.ensemble.rf_weight,
                "xgb_weight": self.ensemble.xgb_weight,
                "rf_config": self.ensemble.rf_model.get_params(),
                "xgb_config": self.ensemble.xgb_model.get_params(),
            },
            training_metrics=metrics,
            feature_names=self.feature_names,
            creation_timestamp=datetime.now().isoformat(),
            model_version="2.0.0",
        )

        # Log results
        self._log_training_results(metrics)

        training_time = time.time() - start_time
        artifacts.training_metrics.training_time_seconds = training_time

        return artifacts, {"X_test": X_test, "y_test": y_test}

    def _cross_validate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, np.ndarray]:
        """Perform cross-validation on training data"""
        cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)

        rf_scores = []
        xgb_scores = []

        for fold, (train_idx, val_idx) in enumerate(cv.split(X, y), 1):
            X_fold_train, X_fold_val = X[train_idx], X[val_idx]
            y_fold_train, y_fold_val = y[train_idx], y[val_idx]

            # Train RF
            rf_fold = RandomForestClassifier(
                n_estimators=200,
                max_depth=25,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features="sqrt",
                n_jobs=-1,
                random_state=42,
                class_weight="balanced",
            )
            rf_fold.fit(X_fold_train, y_fold_train)
            rf_pred = rf_fold.predict(X_fold_val)
            rf_scores.append(accuracy_score(y_fold_val, rf_pred))

            # Train XGB
            xgb_fold = XGBClassifier(
                n_estimators=150,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=0,
            )
            xgb_fold.fit(X_fold_train, y_fold_train)
            xgb_pred = xgb_fold.predict(X_fold_val)
            xgb_scores.append(accuracy_score(y_fold_val, xgb_pred))

            logger.info(f"  Fold {fold}: RF={rf_scores[-1]:.4f}, XGB={xgb_scores[-1]:.4f}")

        return {
            "random_forest": np.array(rf_scores),
            "xgboost": np.array(xgb_scores),
        }

    def _log_training_results(self, metrics: TrainingMetrics):
        """Log training results"""
        logger.info("=" * 80)
        logger.info("TRAINING RESULTS")
        logger.info("=" * 80)
        logger.info(f"Accuracy:  {metrics.accuracy:.4f}")
        logger.info(f"Precision: {metrics.precision:.4f}")
        logger.info(f"Recall:    {metrics.recall:.4f}")
        logger.info(f"F1-Score:  {metrics.f1:.4f}")
        logger.info(f"AUC-ROC:   {metrics.auc_roc:.4f}")
        logger.info("")
        logger.info("Cross-validation scores (10-fold):")
        logger.info(
            f"  Random Forest:  {metrics.cross_val_scores['random_forest'].mean():.4f} "
            f"(+/- {metrics.cross_val_scores['random_forest'].std():.4f})"
        )
        logger.info(
            f"  XGBoost:        {metrics.cross_val_scores['xgboost'].mean():.4f} "
            f"(+/- {metrics.cross_val_scores['xgboost'].std():.4f})"
        )
        logger.info("")
        logger.info("Top 10 Features:")
        for i, (fname, importance) in enumerate(
            list(metrics.feature_importance.items())[:10], 1
        ):
            logger.info(f"  {i:2d}. {fname:40s} {importance:.6f}")
        logger.info("")
        logger.info(f"Training time: {metrics.training_time_seconds:.1f}s")
        logger.info("=" * 80)


def save_model_artifacts(
    artifacts: ModelArtifacts,
    output_dir: Path = Path("./models"),
):
    """Save trained model and metadata to disk"""
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version = artifacts.model_version.replace(".", "_")
    model_name = f"gitops_ensemble_v{version}_{timestamp}"

    model_dir = output_dir / model_name
    model_dir.mkdir(parents=True, exist_ok=True)

    # Save models
    logger.info(f"Saving models to {model_dir}...")
    joblib.dump(artifacts.random_forest, model_dir / "random_forest.pkl")
    joblib.dump(artifacts.xgboost, model_dir / "xgboost.pkl")

    # Save metadata
    metadata = {
        "model_version": artifacts.model_version,
        "creation_timestamp": artifacts.creation_timestamp,
        "feature_names": artifacts.feature_names,
        "ensemble_metadata": artifacts.ensemble_metadata,
        "training_metrics": {
            "accuracy": float(artifacts.training_metrics.accuracy),
            "precision": float(artifacts.training_metrics.precision),
            "recall": float(artifacts.training_metrics.recall),
            "f1": float(artifacts.training_metrics.f1),
            "auc_roc": float(artifacts.training_metrics.auc_roc),
            "training_time_seconds": artifacts.training_metrics.training_time_seconds,
            "confusion_matrix": artifacts.training_metrics.confusion_matrix.tolist(),
            "cross_val_scores": {
                k: v.tolist() for k, v in artifacts.training_metrics.cross_val_scores.items()
            },
            "feature_importance": artifacts.training_metrics.feature_importance,
        },
    }

    with open(model_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"✓ Models saved to {model_dir}")
    return model_dir


if __name__ == "__main__":
    from feature_engineering import create_synthetic_repo_data, FeatureEngineer

    logging.basicConfig(level=logging.INFO)

    print("=" * 80)
    print("Pillar D — Model Training Pipeline")
    print("=" * 80)

    # Create synthetic data
    print("\n[1/5] Generating synthetic repository data...")
    repo_data = create_synthetic_repo_data(n_repos=1000)
    y = repo_data.pop("merge_success")
    print(f"  ✓ Generated {len(repo_data)} repos")

    # Feature engineering
    print("\n[2/5] Running feature engineering...")
    engineer = FeatureEngineer()
    feature_set = engineer.fit_transform(repo_data)
    X = feature_set.features_df
    print(f"  ✓ Extracted {X.shape[1]} features")

    # Training
    print("\n[3/5] Training ensemble model...")
    trainer = ModelTrainer(cv_folds=10)
    artifacts, test_data = trainer.train(X, y)

    # Evaluate
    print("\n[4/5] Final metrics:")
    print(f"  Accuracy:  {artifacts.training_metrics.accuracy:.4f}")
    print(f"  Precision: {artifacts.training_metrics.precision:.4f}")
    print(f"  Recall:    {artifacts.training_metrics.recall:.4f}")
    print(f"  F1-Score:  {artifacts.training_metrics.f1:.4f}")
    print(f"  AUC-ROC:   {artifacts.training_metrics.auc_roc:.4f}")

    # Save
    print("\n[5/5] Saving model artifacts...")
    model_dir = save_model_artifacts(artifacts, Path("./models"))
    print(f"  ✓ Saved to {model_dir}")

    print("\n✓ Training complete!")
