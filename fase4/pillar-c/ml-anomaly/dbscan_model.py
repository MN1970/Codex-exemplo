"""
DBSCAN model for massive drift detection.
Detects clusters of anomalies indicating distribution shift via Wasserstein distance.
"""

import numpy as np
import pickle
import logging
from typing import Tuple, Optional, List
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist, wasserstein_distance
from pathlib import Path

from feature_engineering import AnomalyFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBSCANDriftDetector:
    """DBSCAN-based model drift and massive anomaly detection."""

    def __init__(
        self,
        eps: float = 0.3,
        min_samples: int = 5,
        model_path: str = "models/dbscan_drift.pkl",
    ):
        """
        Initialize DBSCAN drift detector.

        Args:
            eps: Maximum distance between samples in same cluster (default: 0.3)
            min_samples: Minimum samples in neighborhood to form core point (default: 5)
            model_path: Path to save/load model
        """
        self.eps = eps
        self.min_samples = min_samples
        self.model_path = model_path
        self.model = None
        self.baseline_centroid = None
        self.baseline_cluster = None
        self.feature_extractor = AnomalyFeatureExtractor()

    def fit_baseline(self, X_baseline: np.ndarray) -> Tuple[float, int]:
        """
        Fit DBSCAN on baseline (normal) data and store centroid.

        Args:
            X_baseline: Baseline features of shape (n_samples, n_features)

        Returns:
            Tuple of (baseline_density, n_clusters)
        """
        logger.info(f"Fitting baseline DBSCAN with eps={self.eps}, min_samples={self.min_samples}")

        self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        labels = self.model.fit_predict(X_baseline)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)

        logger.info(f"Baseline: {n_clusters} clusters, {n_noise} noise points")

        # Store baseline centroid (mean of all baseline points)
        self.baseline_centroid = np.mean(X_baseline, axis=0)
        self.baseline_cluster = X_baseline

        baseline_density = len(X_baseline) / (n_clusters if n_clusters > 0 else 1)

        return baseline_density, n_clusters

    def detect_drift(self, X_test: np.ndarray) -> Tuple[bool, float, int]:
        """
        Detect massive drift using DBSCAN clustering and Wasserstein distance.

        Args:
            X_test: Test features of shape (n_samples, n_features)

        Returns:
            Tuple of (is_drift_detected, wasserstein_distance_to_baseline, largest_cluster_size)
        """
        if self.model is None or self.baseline_centroid is None:
            raise ValueError("Baseline not fitted. Call fit_baseline() first.")

        # Apply DBSCAN clustering on test data
        labels = self.model.fit_predict(X_test)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

        # Find largest cluster
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = counts[unique != -1]  # Exclude noise points
        largest_cluster_size = np.max(cluster_sizes) if len(cluster_sizes) > 0 else 0

        # Calculate Wasserstein distance to baseline
        test_centroid = np.mean(X_test, axis=0)

        # For each dimension, calculate Wasserstein distance
        wasserstein_dists = []
        for dim in range(X_test.shape[1]):
            try:
                w_dist = wasserstein_distance(self.baseline_cluster[:, dim], X_test[:, dim])
                wasserstein_dists.append(w_dist)
            except Exception as e:
                logger.warning(f"Failed to compute Wasserstein for dimension {dim}: {e}")
                wasserstein_dists.append(0.0)

        mean_wasserstein = np.mean(wasserstein_dists)

        # Detect drift if:
        # 1. Largest cluster significantly larger than baseline (>100 samples)
        # 2. OR Wasserstein distance exceeds threshold (>0.5)
        is_drift = largest_cluster_size > 100 or mean_wasserstein > 0.5

        logger.info(
            f"Drift detection: largest_cluster={largest_cluster_size}, "
            f"wasserstein={mean_wasserstein:.3f}, drift_detected={is_drift}"
        )

        return is_drift, mean_wasserstein, largest_cluster_size

    def cluster_analysis(self, X: np.ndarray) -> dict:
        """
        Perform detailed cluster analysis.

        Args:
            X: Feature matrix of shape (n_samples, n_features)

        Returns:
            Dict with cluster statistics
        """
        labels = self.model.fit_predict(X)

        unique, counts = np.unique(labels, return_counts=True)

        clusters_info = {
            "n_clusters": len(set(labels)) - (1 if -1 in labels else 0),
            "n_noise_points": list(labels).count(-1),
            "cluster_sizes": {int(label): int(count) for label, count in zip(unique, counts) if label != -1},
            "largest_cluster_size": int(np.max(counts[unique != -1])) if len(counts[unique != -1]) > 0 else 0,
            "mean_cluster_size": float(
                np.mean(counts[unique != -1]) if len(counts[unique != -1]) > 0 else 0
            ),
        }

        return clusters_info

    def save_model(self) -> None:
        """Save trained model to disk."""
        if self.model is None:
            logger.warning("No model to save.")
            return

        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "model": self.model,
            "baseline_centroid": self.baseline_centroid,
            "baseline_cluster": self.baseline_cluster,
            "eps": self.eps,
            "min_samples": self.min_samples,
        }

        with open(self.model_path, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {self.model_path}")

    def load_model(self) -> bool:
        """Load model from disk."""
        if not Path(self.model_path).exists():
            logger.error(f"Model file not found: {self.model_path}")
            return False

        try:
            with open(self.model_path, "rb") as f:
                model_data = pickle.load(f)

            self.model = model_data["model"]
            self.baseline_centroid = model_data["baseline_centroid"]
            self.baseline_cluster = model_data["baseline_cluster"]
            self.eps = model_data["eps"]
            self.min_samples = model_data["min_samples"]

            logger.info(f"Model loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


def train_and_save_dbscan_model():
    """Train and save DBSCAN drift detector."""
    detector = DBSCANDriftDetector(eps=0.3, min_samples=5, model_path="models/dbscan_drift.pkl")

    # Create baseline data (normal distribution)
    baseline_data = AnomalyFeatureExtractor.create_synthetic_normal_data(n_samples=500)
    baseline_data = AnomalyFeatureExtractor.normalize_features(baseline_data)

    baseline_density, n_clusters = detector.fit_baseline(baseline_data)
    logger.info(f"Baseline fitted: density={baseline_density:.1f}, clusters={n_clusters}")

    detector.save_model()


if __name__ == "__main__":
    # Train model
    train_and_save_dbscan_model()

    # Load and test
    detector = DBSCANDriftDetector(model_path="models/dbscan_drift.pkl")
    detector.load_model()

    # Test with normal data (similar to baseline)
    normal_test = AnomalyFeatureExtractor.create_synthetic_normal_data(n_samples=100)
    normal_test = AnomalyFeatureExtractor.normalize_features(normal_test)

    is_drift, wasserstein, cluster_size = detector.detect_drift(normal_test)
    print(f"Normal test: drift={is_drift}, wasserstein={wasserstein:.3f}, largest_cluster={cluster_size}")

    # Test with anomalous data (significant drift)
    anomalous_test = AnomalyFeatureExtractor.create_synthetic_anomalous_data(n_samples=200)
    anomalous_test = AnomalyFeatureExtractor.normalize_features(anomalous_test)

    is_drift, wasserstein, cluster_size = detector.detect_drift(anomalous_test)
    print(f"Anomalous test: drift={is_drift}, wasserstein={wasserstein:.3f}, largest_cluster={cluster_size}")

    # Detailed cluster analysis
    cluster_info = detector.cluster_analysis(anomalous_test)
    print(f"Cluster analysis: {cluster_info}")
