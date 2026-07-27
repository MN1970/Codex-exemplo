"""
Prometheus metrics definitions for Manta Maestro observability.
Covers git, ML, infrastructure, business, and anomaly detection domains.
"""

from opentelemetry import metrics
from opentelemetry.sdk.metrics.aggregation import (
    ExplicitBucketHistogramAggregation,
    LastValueAggregation,
    SumAggregation,
)
from typing import Optional


class MantaMetrics:
    """Centralized metrics management for Manta observability."""

    def __init__(self):
        self.meter = metrics.get_meter("manta-observability")
        self._setup_git_metrics()
        self._setup_ml_metrics()
        self._setup_infrastructure_metrics()
        self._setup_business_metrics()
        self._setup_anomaly_metrics()

    def _setup_git_metrics(self) -> None:
        """Setup Git/GitOps metrics."""
        # Git merge metrics
        self.git_merge_success_count = self.meter.create_counter(
            name="manta_git_merge_success_total",
            description="Total number of successful PR merges",
            unit="1",
        )

        self.git_merge_failure_count = self.meter.create_counter(
            name="manta_git_merge_failure_total",
            description="Total number of failed PR merges",
            unit="1",
        )

        self.git_merge_success_rate = self.meter.create_gauge(
            name="manta_git_merge_success_rate",
            description="PR merge success rate (0-1)",
            unit="1",
        )

        self.git_pr_review_time = self.meter.create_histogram(
            name="manta_git_pr_review_time_seconds",
            description="Time taken to review a PR from creation to merge",
            unit="s",
            aggregation=ExplicitBucketHistogramAggregation([60, 300, 900, 1800, 3600, 7200]),
        )

        self.git_conflict_resolution_time = self.meter.create_histogram(
            name="manta_git_conflict_resolution_time_seconds",
            description="Time to resolve merge conflicts",
            unit="s",
            aggregation=ExplicitBucketHistogramAggregation([60, 300, 900, 1800, 3600, 7200]),
        )

        self.git_commit_size = self.meter.create_histogram(
            name="manta_git_commit_size_lines",
            description="Number of lines changed per commit",
            unit="1",
            aggregation=ExplicitBucketHistogramAggregation([10, 50, 100, 500, 1000, 5000]),
        )

        self.git_ci_duration = self.meter.create_histogram(
            name="manta_git_ci_duration_seconds",
            description="CI/CD pipeline execution duration",
            unit="s",
            aggregation=ExplicitBucketHistogramAggregation([30, 60, 120, 300, 600, 1200]),
        )

    def _setup_ml_metrics(self) -> None:
        """Setup ML/AI metrics."""
        self.ml_model_accuracy = self.meter.create_gauge(
            name="manta_ml_model_accuracy",
            description="Current ML model accuracy (0-1)",
            unit="1",
        )

        self.ml_model_accuracy_baseline = self.meter.create_gauge(
            name="manta_ml_model_accuracy_baseline",
            description="Baseline ML model accuracy for drift detection",
            unit="1",
        )

        self.ml_model_precision = self.meter.create_gauge(
            name="manta_ml_model_precision",
            description="ML model precision metric",
            unit="1",
        )

        self.ml_model_recall = self.meter.create_gauge(
            name="manta_ml_model_recall",
            description="ML model recall metric",
            unit="1",
        )

        self.ml_inference_latency = self.meter.create_histogram(
            name="manta_ml_inference_latency_ms",
            description="ML model inference latency",
            unit="ms",
            aggregation=ExplicitBucketHistogramAggregation([10, 50, 100, 500, 1000, 2000]),
        )

        self.ml_training_duration = self.meter.create_histogram(
            name="manta_ml_training_duration_hours",
            description="ML model training duration",
            unit="h",
            aggregation=ExplicitBucketHistogramAggregation([0.5, 1, 2, 4, 8, 24]),
        )

        self.ml_feature_importance = self.meter.create_gauge(
            name="manta_ml_feature_importance",
            description="Importance score of individual features (top 10)",
            unit="1",
        )

        self.ml_prediction_count = self.meter.create_counter(
            name="manta_ml_predictions_total",
            description="Total number of ML model predictions",
            unit="1",
        )

    def _setup_infrastructure_metrics(self) -> None:
        """Setup infrastructure metrics."""
        self.cpu_usage_percent = self.meter.create_gauge(
            name="manta_infrastructure_cpu_usage_percent",
            description="CPU usage percentage (0-100)",
            unit="%",
        )

        self.memory_usage_mb = self.meter.create_gauge(
            name="manta_infrastructure_memory_usage_mb",
            description="Memory usage in megabytes",
            unit="MB",
        )

        self.disk_io_operations = self.meter.create_counter(
            name="manta_infrastructure_disk_io_operations_total",
            description="Total disk I/O operations",
            unit="1",
        )

        self.network_throughput_mbps = self.meter.create_gauge(
            name="manta_infrastructure_network_throughput_mbps",
            description="Network throughput in Mbps",
            unit="Mbps",
        )

        self.pod_restart_count = self.meter.create_counter(
            name="manta_infrastructure_pod_restarts_total",
            description="Total number of pod restarts",
            unit="1",
        )

    def _setup_business_metrics(self) -> None:
        """Setup business/cost metrics."""
        self.cost_per_merge_dollars = self.meter.create_gauge(
            name="manta_cost_per_merge_dollars",
            description="Infrastructure cost per successful merge",
            unit="$",
        )

        self.roi_per_feature = self.meter.create_gauge(
            name="manta_roi_per_feature",
            description="Return on investment per feature deployed",
            unit="1",
        )

        self.velocity_merges_per_day = self.meter.create_gauge(
            name="manta_velocity_merges_per_day",
            description="Average merges per day (deployment velocity)",
            unit="1",
        )

        self.cost_monthly = self.meter.create_gauge(
            name="manta_cost_monthly",
            description="Monthly infrastructure cost",
            unit="$",
        )

        self.feature_deployment_time = self.meter.create_histogram(
            name="manta_feature_deployment_time_days",
            description="Time from feature creation to production deployment",
            unit="d",
            aggregation=ExplicitBucketHistogramAggregation([0.5, 1, 3, 7, 14, 30]),
        )

    def _setup_anomaly_metrics(self) -> None:
        """Setup anomaly detection metrics."""
        self.anomaly_detection_latency = self.meter.create_histogram(
            name="manta_anomaly_detection_latency_ms",
            description="Latency of anomaly detection inference",
            unit="ms",
            aggregation=ExplicitBucketHistogramAggregation([10, 50, 100, 500, 1000]),
        )

        self.anomaly_score = self.meter.create_gauge(
            name="manta_anomaly_score",
            description="Raw anomaly score from Isolation Forest (0-1)",
            unit="1",
        )

        self.pattern_quality_score = self.meter.create_gauge(
            name="manta_pattern_quality_score",
            description="Quality score of detected patterns (0-100)",
            unit="1",
        )

        self.canary_rollout_progress = self.meter.create_gauge(
            name="manta_canary_rollout_progress_percent",
            description="Canary rollout progress percentage (0-100)",
            unit="%",
        )

        self.anomaly_detection_unresolved_count = self.meter.create_gauge(
            name="manta_anomaly_detection_unresolved_count",
            description="Number of unresolved anomalies",
            unit="1",
        )

        self.dbscan_cluster_size = self.meter.create_gauge(
            name="manta_anomaly_dbscan_cluster_size",
            description="Size of largest DBSCAN cluster (indicates drift magnitude)",
            unit="1",
        )

        self.canary_rollout_last_phase_change = self.meter.create_gauge(
            name="manta_canary_rollout_last_phase_change_timestamp",
            description="Unix timestamp of last canary phase change",
            unit="1",
        )

        self.jaeger_span_error_rate = self.meter.create_gauge(
            name="manta_jaeger_span_error_rate",
            description="Jaeger span error rate (0-1)",
            unit="1",
        )


# Singleton instance
_metrics_instance: Optional[MantaMetrics] = None


def get_metrics() -> MantaMetrics:
    """Get or create singleton metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MantaMetrics()
    return _metrics_instance
