package main

import (
	"context"
	"log"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/metric"
)

// MantaMetrics holds all OpenTelemetry metrics for Manta observability.
type MantaMetrics struct {
	// Git metrics
	GitMergeSuccessCount     metric.Int64Counter
	GitMergeFailureCount     metric.Int64Counter
	GitMergeSuccessRate      metric.Float64Gauge
	GitPRReviewTime          metric.Float64Histogram
	GitConflictResolutionTime metric.Float64Histogram
	GitCommitSize            metric.Int64Histogram
	GitCIDuration            metric.Float64Histogram

	// ML metrics
	MLModelAccuracy          metric.Float64Gauge
	MLModelAccuracyBaseline  metric.Float64Gauge
	MLModelPrecision         metric.Float64Gauge
	MLModelRecall            metric.Float64Gauge
	MLInferenceLatency       metric.Float64Histogram
	MLTrainingDuration       metric.Float64Histogram
	MLFeatureImportance      metric.Float64Gauge
	MLPredictionCount        metric.Int64Counter

	// Infrastructure metrics
	CPUUsagePercent          metric.Float64Gauge
	MemoryUsageMB            metric.Int64Gauge
	DiskIOOperations         metric.Int64Counter
	NetworkThroughputMBps    metric.Float64Gauge
	PodRestartCount          metric.Int64Counter

	// Business metrics
	CostPerMergeDollars      metric.Float64Gauge
	ROIPerFeature            metric.Float64Gauge
	VelocityMergesPerDay     metric.Float64Gauge
	CostMonthly              metric.Float64Gauge
	FeatureDeploymentTime    metric.Float64Histogram

	// Anomaly metrics
	AnomalyDetectionLatency  metric.Float64Histogram
	AnomalyScore             metric.Float64Gauge
	PatternQualityScore      metric.Float64Gauge
	CanaryRolloutProgress    metric.Float64Gauge
	AnomalyUnresolvedCount   metric.Int64Gauge
	DBSCANClusterSize        metric.Int64Gauge
	CanaryPhaseChangeTime    metric.Int64Gauge
	JaegerSpanErrorRate      metric.Float64Gauge
}

// InitializeMetrics sets up all Manta metrics.
func InitializeMetrics(ctx context.Context) (*MantaMetrics, error) {
	meter := otel.Meter("manta-observability")
	m := &MantaMetrics{}

	// Git metrics
	var err error
	m.GitMergeSuccessCount, err = meter.Int64Counter(
		"manta_git_merge_success_total",
		metric.WithDescription("Total number of successful PR merges"),
		metric.WithUnit("1"),
	)
	if err != nil {
		log.Printf("Failed to create GitMergeSuccessCount: %v\n", err)
		return nil, err
	}

	m.GitMergeFailureCount, err = meter.Int64Counter(
		"manta_git_merge_failure_total",
		metric.WithDescription("Total number of failed PR merges"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.GitMergeSuccessRate, err = meter.Float64Gauge(
		"manta_git_merge_success_rate",
		metric.WithDescription("PR merge success rate (0-1)"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.GitPRReviewTime, err = meter.Float64Histogram(
		"manta_git_pr_review_time_seconds",
		metric.WithDescription("Time taken to review a PR from creation to merge"),
		metric.WithUnit("s"),
	)
	if err != nil {
		return nil, err
	}

	m.GitConflictResolutionTime, err = meter.Float64Histogram(
		"manta_git_conflict_resolution_time_seconds",
		metric.WithDescription("Time to resolve merge conflicts"),
		metric.WithUnit("s"),
	)
	if err != nil {
		return nil, err
	}

	m.GitCommitSize, err = meter.Int64Histogram(
		"manta_git_commit_size_lines",
		metric.WithDescription("Number of lines changed per commit"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.GitCIDuration, err = meter.Float64Histogram(
		"manta_git_ci_duration_seconds",
		metric.WithDescription("CI/CD pipeline execution duration"),
		metric.WithUnit("s"),
	)
	if err != nil {
		return nil, err
	}

	// ML metrics
	m.MLModelAccuracy, err = meter.Float64Gauge(
		"manta_ml_model_accuracy",
		metric.WithDescription("Current ML model accuracy (0-1)"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.MLInferenceLatency, err = meter.Float64Histogram(
		"manta_ml_inference_latency_ms",
		metric.WithDescription("ML model inference latency"),
		metric.WithUnit("ms"),
	)
	if err != nil {
		return nil, err
	}

	m.MLPredictionCount, err = meter.Int64Counter(
		"manta_ml_predictions_total",
		metric.WithDescription("Total number of ML model predictions"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	// Infrastructure metrics
	m.CPUUsagePercent, err = meter.Float64Gauge(
		"manta_infrastructure_cpu_usage_percent",
		metric.WithDescription("CPU usage percentage (0-100)"),
		metric.WithUnit("%"),
	)
	if err != nil {
		return nil, err
	}

	m.MemoryUsageMB, err = meter.Int64Gauge(
		"manta_infrastructure_memory_usage_mb",
		metric.WithDescription("Memory usage in megabytes"),
		metric.WithUnit("MB"),
	)
	if err != nil {
		return nil, err
	}

	// Business metrics
	m.CostPerMergeDollars, err = meter.Float64Gauge(
		"manta_cost_per_merge_dollars",
		metric.WithDescription("Infrastructure cost per successful merge"),
		metric.WithUnit("$"),
	)
	if err != nil {
		return nil, err
	}

	m.CostMonthly, err = meter.Float64Gauge(
		"manta_cost_monthly",
		metric.WithDescription("Monthly infrastructure cost"),
		metric.WithUnit("$"),
	)
	if err != nil {
		return nil, err
	}

	// Anomaly metrics
	m.AnomalyDetectionLatency, err = meter.Float64Histogram(
		"manta_anomaly_detection_latency_ms",
		metric.WithDescription("Latency of anomaly detection inference"),
		metric.WithUnit("ms"),
	)
	if err != nil {
		return nil, err
	}

	m.AnomalyScore, err = meter.Float64Gauge(
		"manta_anomaly_score",
		metric.WithDescription("Raw anomaly score from Isolation Forest (0-1)"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.AnomalyUnresolvedCount, err = meter.Int64Gauge(
		"manta_anomaly_detection_unresolved_count",
		metric.WithDescription("Number of unresolved anomalies"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.DBSCANClusterSize, err = meter.Int64Gauge(
		"manta_anomaly_dbscan_cluster_size",
		metric.WithDescription("Size of largest DBSCAN cluster (indicates drift magnitude)"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	m.JaegerSpanErrorRate, err = meter.Float64Gauge(
		"manta_jaeger_span_error_rate",
		metric.WithDescription("Jaeger span error rate (0-1)"),
		metric.WithUnit("1"),
	)
	if err != nil {
		return nil, err
	}

	log.Println("Manta metrics initialized successfully")
	return m, nil
}
