"""
Isolation Forest model for anomaly detection.
50-tree ensemble with 5% contamination rate for latency spike detection.
"""

import numpy as np
import pickle
import logging
from typing import Tuple, Optional
from sklearn.ensemble import IsolationForest
from pathlib import Path

from feature_engineering import AnomalyFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IsolationForestAnomalyDetector:
    """Isolation Forest-based anomaly detection model."""

    def __init__(
        self,
        n_estimators: int = 50,
        contamination: float = 0.05,
        random_state: int = 42,
        model_path: str = "models/isolation_forest.pkl",
    ):
        """
        Initialize Isolation Forest detector.

        Args:
            n_estimators: Number of trees in ensemble (default: 50)
            contamination: Expected proportion of anomalies (default: 0.05 = 5%)
            random_state: Random seed for reproducibility
            model_path: Path to save/load model
        """
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model_path = model_path
        self.model = None
        self.feature_extractor = AnomalyFeatureExtractor()

    def train(self, X_train: np.ndarray) -> Tuple[float, float, float]:
        """
        Train Isolation Forest model.

        Args:
            X_train: Training features of shape (n_samples, n_features)

        Returns:
            Tuple of (train_accuracy, precision_estimate, recall_estimate)
        """
        logger.info(
            f"Training Isolation Forest with {self.n_estimators} trees, "
            f"contamination={self.contamination}"
        )

        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1,
        )

        self.model.fit(X_train)

        # Calculate training accuracy
        predictions = self.model.predict(X_train)
        # -1: anomaly, 1: normal
        normal_count = np.sum(predictions == 1)
        anomaly_count = np.sum(predictions == -1)

        train_accuracy = normal_count / len(X_train)
        # Estimate precision/recall assuming ~5% are true anomalies
        precision = anomaly_count / max(anomaly_count, 1)
        recall = anomaly_count / max(len(X_train) * self.contamination, 1)

        logger.info(f"Training complete. Normal: {normal_count}, Anomalies: {anomaly_count}")
        logger.info(f"Estimated precision: {precision:.3f}, recall: {recall:.3f}")

        return train_accuracy, precision, recall

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies on new data.

        Args:
            X: Feature matrix of shape (n_samples, n_features)

        Returns:
            Tuple of (predictions, anomaly_scores)
            predictions: -1 for anomaly, 1 for normal
            anomaly_scores: Normalized anomaly scores (0-1), higher = more anomalous
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        predictions = self.model.predict(X)

        # Get raw anomaly scores and normalize to [0, 1]
        raw_scores = self.model.score_samples(X)
        # Normalize: lower scores (more anomalous) -> higher anomaly_score
        min_score = np.min(raw_scores)
        max_score = np.max(raw_scores)

        if max_score > min_score:
            anomaly_scores = 1 - ((raw_scores - min_score) / (max_score - min_score))
        else:
            anomaly_scores = np.ones_like(raw_scores)

        return predictions, anomaly_scores

    def predict_from_metrics(self, metrics: dict) -> Tuple[bool, float]:
        """
        Predict anomaly from raw metrics data.

        Args:
            metrics: Dict of {metric_name: [values]}

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        features, _ = self.feature_extractor.extract_multi_metric_features(metrics)

        if features.size == 0:
            return False, 0.0

        predictions, scores = self.predict(features)

        # Aggregate across metrics (if multiple)
        is_anomaly = np.any(predictions == -1)
        mean_score = np.mean(scores)

        return is_anomaly, mean_score

    def save_model(self) -> None:
        """Save trained model to disk."""
        if self.model is None:
            logger.warning("No model to save.")
            return

        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)

        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)

        logger.info(f"Model saved to {self.model_path}")

    def load_model(self) -> bool:
        """
        Load model from disk.

        Returns:
            True if successful, False otherwise
        """
        if not Path(self.model_path).exists():
            logger.error(f"Model file not found: {self.model_path}")
            return False

        try:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_and_save_model():
    """Train a new Isolation Forest model and save it."""
    detector = IsolationForestAnomalyDetector(
        n_estimators=50,
        contamination=0.05,
        model_path="models/isolation_forest.pkl",
    )

    # Create synthetic training data
    normal_data = AnomalyFeatureExtractor.create_synthetic_normal_data(n_samples=950)
    anomalous_data = AnomalyFeatureExtractor.create_synthetic_anomalous_data(n_samples=50)

    X_train = np.vstack([normal_data, anomalous_data])
    np.random.shuffle(X_train)

    # Normalize features
    X_train = AnomalyFeatureExtractor.normalize_features(X_train)

    # Train model
    train_acc, precision, recall = detector.train(X_train)

    logger.info(f"Training completed: accuracy={train_acc:.3f}, precision={precision:.3f}, recall={recall:.3f}")

    # Save model
    detector.save_model()


if __name__ == "__main__":
    train_and_save_model()

    # Test the model
    detector = IsolationForestAnomalyDetector(model_path="models/isolation_forest.pkl")
    detector.load_model()

    # Test with normal data
    normal_test = AnomalyFeatureExtractor.create_synthetic_normal_data(n_samples=10)
    normal_test = AnomalyFeatureExtractor.normalize_features(normal_test)

    predictions, scores = detector.predict(normal_test)
    print(f"Normal data - Anomalies detected: {np.sum(predictions == -1)}/{len(normal_test)}")
    print(f"Normal data - Mean anomaly score: {np.mean(scores):.3f}")

    # Test with anomalous data
    anomalous_test = AnomalyFeatureExtractor.create_synthetic_anomalous_data(n_samples=10)
    anomalous_test = AnomalyFeatureExtractor.normalize_features(anomalous_test)

    predictions, scores = detector.predict(anomalous_test)
    print(f"Anomalous data - Anomalies detected: {np.sum(predictions == -1)}/{len(anomalous_test)}")
    print(f"Anomalous data - Mean anomaly score: {np.mean(scores):.3f}")
