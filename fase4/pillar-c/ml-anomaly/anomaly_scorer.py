"""
Anomaly scorer service that runs inference and exports metrics to Prometheus.
Combines Isolation Forest and DBSCAN for comprehensive anomaly detection.
"""

import os
import time
import logging
from typing import Dict, List, Tuple
import requests
from datetime import datetime, timedelta

from isolation_forest_model import IsolationForestAnomalyDetector
from dbscan_model import DBSCANDriftDetector
from feature_engineering import AnomalyFeatureExtractor

from prometheus_client import Counter, Gauge, Histogram, start_http_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyScorer:
    """Main anomaly detection and scoring service."""

    def __init__(
        self,
        prometheus_port: int = 8001,
        prometheus_url: str = "http://prometheus:9090",
        scrape_interval_seconds: int = 60,
    ):
        """
        Initialize anomaly scorer.

        Args:
            prometheus_port: Port for exporting Prometheus metrics
            prometheus_url: URL to Prometheus for fetching data
            scrape_interval_seconds: How often to run anomaly detection
        """
        self.prometheus_port = prometheus_port
        self.prometheus_url = prometheus_url
        self.scrape_interval = scrape_interval_seconds

        # Initialize models
        self.iso_forest = IsolationForestAnomalyDetector(model_path="models/isolation_forest.pkl")
        self.dbscan = DBSCANDriftDetector(model_path="models/dbscan_drift.pkl")

        # Load pre-trained models
        self._load_models()

        # Setup Prometheus metrics
        self._setup_prometheus_metrics()

    def _load_models(self) -> None:
        """Load pre-trained models."""
        iso_loaded = self.iso_forest.load_model()
        dbscan_loaded = self.dbscan.load_model()

        if not iso_loaded:
            logger.warning("Isolation Forest model not found. Training new model...")
            from isolation_forest_model import train_and_save_model
            train_and_save_model()
            self.iso_forest.load_model()

        if not dbscan_loaded:
            logger.warning("DBSCAN model not found. Training new model...")
            from dbscan_model import train_and_save_dbscan_model
            train_and_save_dbscan_model()
            self.dbscan.load_model()

    def _setup_prometheus_metrics(self) -> None:
        """Setup Prometheus metrics for export."""
        # Anomaly detection metrics
        self.anomaly_score = Gauge(
            "manta_anomaly_detection_score",
            "Anomaly score from Isolation Forest (0-1)",
            ["metric_name"],
        )

        self.anomaly_detected = Gauge(
            "manta_anomaly_detected",
            "Binary flag indicating anomaly detection (1=anomaly, 0=normal)",
            ["metric_name", "detection_method"],
        )

        self.anomaly_detection_latency = Histogram(
            "manta_anomaly_detection_latency_ms",
            "Latency of anomaly detection inference",
        )

        self.drift_score = Gauge(
            "manta_drift_wasserstein_distance",
            "Wasserstein distance indicating drift magnitude",
        )

        self.largest_dbscan_cluster = Gauge(
            "manta_anomaly_dbscan_cluster_size",
            "Size of largest DBSCAN cluster (drift indicator)",
        )

        self.unresolved_anomalies = Gauge(
            "manta_anomaly_detection_unresolved_count",
            "Number of unresolved anomalies in last hour",
        )

        self.anomaly_resolution_time = Histogram(
            "manta_anomaly_resolution_time_minutes",
            "Time taken to resolve anomalies",
        )

    def fetch_prometheus_metrics(self, query: str, minutes_back: int = 60) -> Dict[str, List[float]]:
        """
        Fetch metrics from Prometheus.

        Args:
            query: Prometheus query (e.g., "manta_ml_inference_latency_ms")
            minutes_back: How far back to fetch data (default: 60 minutes)

        Returns:
            Dict of {metric_name: [values]}
        """
        try:
            # Query range data
            end_time = int(time.time())
            start_time = end_time - (minutes_back * 60)

            response = requests.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": start_time,
                    "end": end_time,
                    "step": "60s",
                },
                timeout=5,
            )

            if response.status_code != 200:
                logger.error(f"Prometheus query failed: {response.status_code}")
                return {}

            data = response.json()
            if data.get("status") != "success":
                logger.error(f"Prometheus error: {data.get('error')}")
                return {}

            # Extract metric values
            metrics_data = {}
            for result in data.get("data", {}).get("result", []):
                metric_name = result["metric"].get("__name__", "unknown")
                values = [float(v[1]) for v in result.get("values", [])]

                if metric_name not in metrics_data:
                    metrics_data[metric_name] = values
                else:
                    metrics_data[metric_name].extend(values)

            return metrics_data

        except Exception as e:
            logger.error(f"Failed to fetch metrics from Prometheus: {e}")
            return {}

    def score_metrics(self, metrics: Dict[str, List[float]]) -> Tuple[bool, float, Dict]:
        """
        Score metrics for anomalies using both models.

        Args:
            metrics: Dict of {metric_name: [values]}

        Returns:
            Tuple of (has_anomaly, mean_score, detailed_results)
        """
        start_time = time.perf_counter()

        # Feature extraction
        features, metric_names = AnomalyFeatureExtractor.extract_multi_metric_features(metrics)

        if features.size == 0:
            return False, 0.0, {}

        # Normalize features
        features = AnomalyFeatureExtractor.normalize_features(features)

        results = {}

        # Isolation Forest detection
        iso_predictions, iso_scores = self.iso_forest.predict(features)
        iso_anomalies = np.sum(iso_predictions == -1)

        # DBSCAN drift detection
        drift_detected, wasserstein_dist, cluster_size = self.dbscan.detect_drift(features)

        # Aggregate results
        has_anomaly = iso_anomalies > 0 or drift_detected
        mean_score = np.mean(iso_scores)

        results = {
            "iso_anomalies": int(iso_anomalies),
            "iso_mean_score": float(mean_score),
            "drift_detected": drift_detected,
            "wasserstein_distance": float(wasserstein_dist),
            "largest_cluster_size": int(cluster_size),
            "latency_ms": (time.perf_counter() - start_time) * 1000,
        }

        return has_anomaly, mean_score, results

    def run_continuous_detection(self) -> None:
        """Run continuous anomaly detection loop."""
        logger.info(f"Starting anomaly detection service on port {self.prometheus_port}")
        start_http_server(self.prometheus_port)

        while True:
            try:
                # Fetch recent metrics
                metrics = self.fetch_prometheus_metrics(
                    "manta_ml_inference_latency_ms", minutes_back=60
                )

                if not metrics:
                    logger.warning("No metrics found. Skipping...")
                    time.sleep(self.scrape_interval)
                    continue

                # Score metrics
                has_anomaly, mean_score, results = self.score_metrics(metrics)

                # Export metrics
                self.anomaly_detection_latency.observe(results.get("latency_ms", 0))

                for metric_name in metrics.keys():
                    self.anomaly_score.labels(metric_name=metric_name).set(mean_score)
                    self.anomaly_detected.labels(
                        metric_name=metric_name, detection_method="isolation_forest"
                    ).set(1 if has_anomaly else 0)

                self.drift_score.set(results.get("wasserstein_distance", 0))
                self.largest_dbscan_cluster.set(results.get("largest_cluster_size", 0))

                logger.info(
                    f"Detection complete: anomaly={has_anomaly}, "
                    f"score={mean_score:.3f}, latency={results.get('latency_ms', 0):.1f}ms"
                )

                time.sleep(self.scrape_interval)

            except Exception as e:
                logger.error(f"Error in detection loop: {e}", exc_info=True)
                time.sleep(self.scrape_interval)


if __name__ == "__main__":
    # Check for required models
    import numpy as np

    if not os.path.exists("models"):
        os.makedirs("models")

    # Initialize scorer
    scorer = AnomalyScorer(
        prometheus_port=int(os.getenv("PROMETHEUS_PORT", "8001")),
        prometheus_url=os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
        scrape_interval_seconds=int(os.getenv("SCRAPE_INTERVAL", "60")),
    )

    # Run continuous detection
    try:
        scorer.run_continuous_detection()
    except KeyboardInterrupt:
        logger.info("Shutting down anomaly scorer...")
