package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/codes"
	oteltrace "go.opentelemetry.io/otel/trace"
)

// Server represents the HTTP server with OpenTelemetry instrumentation.
type Server struct {
	router  *http.ServeMux
	metrics *MantaMetrics
	tracer  oteltrace.Tracer
}

// MergeRequest represents a PR merge request.
type MergeRequest struct {
	PRID                      string  `json:"pr_id"`
	Branch                    string  `json:"branch"`
	ConflictResolutionSeconds float64 `json:"conflict_resolution_time_seconds"`
}

// MergeResponse represents the response from a merge operation.
type MergeResponse struct {
	PRID        string `json:"pr_id"`
	Status      string `json:"status"`
	Traceparent string `json:"traceparent"`
	TraceState  string `json:"tracestate"`
}

// MLInferenceRequest represents an ML inference request.
type MLInferenceRequest struct {
	ModelID string    `json:"model_id"`
	Features []float64 `json:"features"`
	TraceID string    `json:"trace_id"`
}

// MLInferenceResponse represents an ML inference response.
type MLInferenceResponse struct {
	Prediction float64 `json:"prediction"`
	Confidence float64 `json:"confidence"`
	LatencyMS  float64 `json:"latency_ms"`
	TraceID    string  `json:"trace_id"`
}

// NewServer creates a new instrumented HTTP server.
func NewServer(metrics *MantaMetrics) *Server {
	s := &Server{
		router:  http.NewServeMux(),
		metrics: metrics,
		tracer:  otel.Tracer("manta-http-server"),
	}

	s.router.HandleFunc("/health", s.healthCheck)
	s.router.HandleFunc("/merge", s.mergePR)
	s.router.HandleFunc("/ml/infer", s.mlInference)
	s.router.HandleFunc("/metrics/summary", s.metricsSummary)

	return s
}

// healthCheck handles health check requests.
func (s *Server) healthCheck(w http.ResponseWriter, r *http.Request) {
	ctx, span := s.tracer.Start(r.Context(), "health-check")
	defer span.End()

	span.SetAttributes(
		attribute.String("http.method", r.Method),
		attribute.String("http.target", r.URL.Path),
	)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
}

// mergePR handles PR merge requests with tracing and metrics.
func (s *Server) mergePR(w http.ResponseWriter, r *http.Request) {
	ctx, span := s.tracer.Start(r.Context(), "merge-pr")
	defer span.End()

	// Extract W3C trace context from incoming request
	incomingTrace := ExtractTraceContext(r)
	if incomingTrace != nil {
		span.SetAttributes(
			attribute.String("trace.incoming.id", incomingTrace.TraceID),
			attribute.String("trace.incoming.span_id", incomingTrace.SpanID),
		)
	}

	// Parse request
	var req MergeRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		span.RecordError(err)
		span.SetStatus(codes.Error, "Invalid request body")
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	span.SetAttributes(
		attribute.String("pr.id", req.PRID),
		attribute.String("branch", req.Branch),
		attribute.Float64("conflict.resolution_seconds", req.ConflictResolutionSeconds),
	)

	// Record metrics
	ctx2, mergeSpan := s.tracer.Start(ctx, "record-merge-metrics")
	{
		s.metrics.GitMergeSuccessCount.Add(mergeSpan.SpanContext().Context(), 1,
			func(o *metric.AddOptions) {
				o.Attributes = attribute.NewSet(attribute.String("branch", req.Branch))
			}())
		s.metrics.GitMergeSuccessRate.Record(mergeSpan.SpanContext().Context(), 0.95)

		if req.ConflictResolutionSeconds > 0 {
			s.metrics.GitConflictResolutionTime.Record(
				mergeSpan.SpanContext().Context(),
				req.ConflictResolutionSeconds,
			)
		}
	}
	mergeSpan.End()

	// Inject trace context into response headers
	responseTrace := &W3CTraceContext{
		TraceID:    fmt.Sprintf("%032x", span.SpanContext().TraceID()),
		SpanID:     fmt.Sprintf("%016x", span.SpanContext().SpanID()),
		TraceFlags: "01",
		TraceState: "",
	}

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("traceparent", fmt.Sprintf("00-%s-%s-%s", responseTrace.TraceID, responseTrace.SpanID, responseTrace.TraceFlags))
	w.WriteHeader(http.StatusOK)

	json.NewEncoder(w).Encode(MergeResponse{
		PRID:        req.PRID,
		Status:      "merged",
		Traceparent: fmt.Sprintf("00-%s-%s-%s", responseTrace.TraceID, responseTrace.SpanID, responseTrace.TraceFlags),
		TraceState:  responseTrace.TraceState,
	})

	_ = ctx2
}

// mlInference handles ML inference requests with tracing and metrics.
func (s *Server) mlInference(w http.ResponseWriter, r *http.Request) {
	ctx, span := s.tracer.Start(r.Context(), "ml-inference")
	defer span.End()

	startTime := time.Now()

	// Parse request
	var req MLInferenceRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		span.RecordError(err)
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	span.SetAttributes(
		attribute.String("model.id", req.ModelID),
		attribute.Int("feature.count", len(req.Features)),
	)

	// Record inference metrics
	ctx2, inferenceSpan := s.tracer.Start(ctx, "run-inference")
	{
		// Simulate inference
		inferenceTime := time.Since(startTime).Milliseconds()
		prediction := 0.75
		confidence := 0.92

		s.metrics.MLInferenceLatency.Record(
			inferenceSpan.SpanContext().Context(),
			float64(inferenceTime),
		)
		s.metrics.MLPredictionCount.Add(inferenceSpan.SpanContext().Context(), 1)
		s.metrics.MLModelAccuracy.Record(inferenceSpan.SpanContext().Context(), 0.924)

		inferenceSpan.SetAttributes(
			attribute.Float64("prediction", prediction),
			attribute.Float64("confidence", confidence),
			attribute.Int64("latency_ms", inferenceTime),
		)

		// Return response
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)

		response := MLInferenceResponse{
			Prediction: prediction,
			Confidence: confidence,
			LatencyMS:  float64(inferenceTime),
			TraceID:    inferenceSpan.SpanContext().TraceID().String(),
		}

		json.NewEncoder(w).Encode(response)
	}
	inferenceSpan.End()
	_ = ctx2
}

// metricsSummary returns a summary of current metrics.
func (s *Server) metricsSummary(w http.ResponseWriter, r *http.Request) {
	ctx, span := s.tracer.Start(r.Context(), "metrics-summary")
	defer span.End()

	summary := map[string]interface{}{
		"git": map[string]interface{}{
			"merge_success_rate":        0.95,
			"average_review_time_hours": 2.5,
		},
		"ml": map[string]interface{}{
			"model_accuracy":               0.924,
			"average_inference_latency_ms": 145,
		},
		"infrastructure": map[string]interface{}{
			"cpu_usage_percent":   45,
			"memory_usage_mb":     512,
			"network_throughput":  100.5,
		},
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(summary)
}

// Start starts the HTTP server.
func (s *Server) Start(port int) error {
	addr := fmt.Sprintf(":%d", port)
	log.Printf("Starting HTTP server on %s\n", addr)
	return http.ListenAndServe(addr, s.router)
}

// main demonstrates a complete example of an instrumented HTTP server.
func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Initialize OpenTelemetry
	serviceName := os.Getenv("SERVICE_NAME")
	if serviceName == "" {
		serviceName = "manta-ml-inference"
	}

	shutdown, err := InitializeOTel(ctx, serviceName)
	if err != nil {
		log.Fatalf("Failed to initialize OpenTelemetry: %v\n", err)
	}
	defer func() {
		if err := shutdown(ctx); err != nil {
			log.Printf("Error shutting down OpenTelemetry: %v\n", err)
		}
	}()

	// Initialize metrics
	metrics, err := InitializeMetrics(ctx)
	if err != nil {
		log.Fatalf("Failed to initialize metrics: %v\n", err)
	}

	// Create and start server
	server := NewServer(metrics)

	port := 8080
	if portStr := os.Getenv("PORT"); portStr != "" {
		if p, err := strconv.Atoi(portStr); err == nil {
			port = p
		}
	}

	// Handle graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		if err := server.Start(port); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v\n", err)
		}
	}()

	<-sigChan
	log.Println("Server shutting down...")
}

// Placeholder for metric package
package metric

type AddOptions struct {
	Attributes Attributes
}

type Attributes interface{}
