"""
Feature engineering for anomaly detection.
Extracts 10 statistical features from 1-hour windows of Prometheus metrics.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
from scipy import stats


class AnomalyFeatureExtractor:
    """Extract statistical features from time series metrics for anomaly detection."""

    @staticmethod
    def extract_window_features(values: List[float], window_size: int = 60) -> np.ndarray:
        """
        Extract 10 statistical features from a sliding window of metric values.

        Features:
        1. Mean of values
        2. Standard deviation
        3. Skewness
        4. Kurtosis
        5. Min value
        6. Max value
        7. Range (max - min)
        8. 95th percentile
        9. Coefficient of variation (std / mean)
        10. Autocorrelation at lag 1

        Args:
            values: List of metric values
            window_size: Size of sliding window (default: 60 for 1 minute at 1Hz)

        Returns:
            Feature vector of shape (10,)
        """
        if len(values) < window_size:
            # Pad with zeros if not enough data
            values = values + [values[-1] if values else 0] * (window_size - len(values))

        values_array = np.array(values[-window_size:], dtype=np.float64)

        # Feature 1: Mean
        mean = np.mean(values_array)

        # Feature 2: Standard deviation
        std = np.std(values_array)

        # Feature 3: Skewness
        skewness = float(stats.skew(values_array))

        # Feature 4: Kurtosis
        kurtosis = float(stats.kurtosis(values_array))

        # Feature 5: Min value
        min_val = np.min(values_array)

        # Feature 6: Max value
        max_val = np.max(values_array)

        # Feature 7: Range
        range_val = max_val - min_val

        # Feature 8: 95th percentile
        percentile_95 = np.percentile(values_array, 95)

        # Feature 9: Coefficient of variation
        if mean != 0:
            coef_var = std / mean
        else:
            coef_var = 0.0

        # Feature 10: Autocorrelation at lag 1
        if len(values_array) > 1 and std > 0:
            diffs = values_array[:-1] - mean
            diffs_lag = values_array[1:] - mean
            autocorr = np.corrcoef(diffs, diffs_lag)[0, 1]
            if np.isnan(autocorr):
                autocorr = 0.0
        else:
            autocorr = 0.0

        features = np.array(
            [mean, std, skewness, kurtosis, min_val, max_val, range_val, percentile_95, coef_var, autocorr],
            dtype=np.float64,
        )

        return features

    @staticmethod
    def extract_multi_metric_features(
        metrics: dict, window_size: int = 60
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Extract features from multiple metrics.

        Args:
            metrics: Dict of {metric_name: [values]}
            window_size: Sliding window size

        Returns:
            Tuple of (feature_matrix, metric_names)
        """
        all_features = []
        metric_names = []

        for metric_name, values in metrics.items():
            features = AnomalyFeatureExtractor.extract_window_features(values, window_size)
            all_features.append(features)
            metric_names.append(metric_name)

        if all_features:
            feature_matrix = np.vstack(all_features)
        else:
            feature_matrix = np.array([]).reshape(0, 10)

        return feature_matrix, metric_names

    @staticmethod
    def normalize_features(features: np.ndarray) -> np.ndarray:
        """
        Normalize features to zero mean and unit variance.

        Args:
            features: Feature matrix of shape (n_samples, n_features)

        Returns:
            Normalized feature matrix
        """
        mean = np.mean(features, axis=0)
        std = np.std(features, axis=0)

        # Avoid division by zero
        std = np.where(std == 0, 1, std)

        return (features - mean) / std

    @staticmethod
    def create_synthetic_normal_data(n_samples: int = 1000, seed: int = 42) -> np.ndarray:
        """
        Create synthetic normal (non-anomalous) data for model training.

        Args:
            n_samples: Number of samples
            seed: Random seed for reproducibility

        Returns:
            Feature matrix of shape (n_samples, 10)
        """
        np.random.seed(seed)

        features = []
        for _ in range(n_samples):
            # Generate normal metric values (latency in ms)
            values = np.random.normal(loc=150, scale=30, size=60).tolist()
            features.append(AnomalyFeatureExtractor.extract_window_features(values))

        return np.array(features)

    @staticmethod
    def create_synthetic_anomalous_data(n_samples: int = 100, seed: int = 42) -> np.ndarray:
        """
        Create synthetic anomalous data for model testing.

        Args:
            n_samples: Number of anomalous samples
            seed: Random seed

        Returns:
            Feature matrix of shape (n_samples, 10)
        """
        np.random.seed(seed)

        features = []
        anomaly_types = [
            ("spike", 500),  # Latency spike
            ("gradual_increase", 200),  # Gradual increase
            ("high_variance", 300),  # High variance
        ]

        for i in range(n_samples):
            anomaly_type, param = anomaly_types[i % len(anomaly_types)]

            if anomaly_type == "spike":
                # Sudden latency spike
                values = np.random.normal(loc=150, scale=30, size=50).tolist()
                values.extend(np.random.normal(loc=param, scale=50, size=10).tolist())
            elif anomaly_type == "gradual_increase":
                # Gradual increase in latency
                values = np.linspace(150, param, 60).tolist()
                values = [v + np.random.normal(0, 10) for v in values]
            else:
                # High variance
                values = np.random.normal(loc=150, scale=param, size=60).tolist()

            features.append(AnomalyFeatureExtractor.extract_window_features(values))

        return np.array(features)


if __name__ == "__main__":
    # Example usage
    print("Testing feature extraction...")

    # Test with synthetic data
    normal_data = AnomalyFeatureExtractor.create_synthetic_normal_data(n_samples=100)
    anomalous_data = AnomalyFeatureExtractor.create_synthetic_anomalous_data(n_samples=20)

    print(f"Normal data shape: {normal_data.shape}")
    print(f"Anomalous data shape: {anomalous_data.shape}")

    print(f"\nNormal data sample (first row):\n{normal_data[0]}")
    print(f"\nAnomalous data sample (first row):\n{anomalous_data[0]}")

    # Test normalization
    combined = np.vstack([normal_data, anomalous_data])
    normalized = AnomalyFeatureExtractor.normalize_features(combined)
    print(f"\nNormalized data shape: {normalized.shape}")
    print(f"Normalized mean: {np.mean(normalized, axis=0)}")
    print(f"Normalized std: {np.std(normalized, axis=0)}")
