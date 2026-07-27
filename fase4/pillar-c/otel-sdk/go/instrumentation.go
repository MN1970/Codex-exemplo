package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/exporters/prometheus"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/sdk/trace"
	sdkmetric "go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/semconv/v1.21.0"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// InitializeOTel sets up OpenTelemetry tracing and metrics exporters.
func InitializeOTel(ctx context.Context, serviceName string) (func(context.Context) error, error) {
	// Create resource
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String(serviceName),
			semconv.ServiceVersionKey.String(os.Getenv("VERSION")),
			attribute.String("environment", os.Getenv("ENVIRONMENT")),
			attribute.String("deployment", os.Getenv("DEPLOYMENT")),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create resource: %w", err)
	}

	// Setup tracing with OTLP gRPC exporter
	jaegerHost := os.Getenv("JAEGER_HOST")
	if jaegerHost == "" {
		jaegerHost = "localhost"
	}
	jaegerPort := os.Getenv("JAEGER_PORT")
	if jaegerPort == "" {
		jaegerPort = "4317"
	}

	conn, err := grpc.NewClient(
		fmt.Sprintf("%s:%s", jaegerHost, jaegerPort),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create gRPC connection to Jaeger: %w", err)
	}

	traceExporter, err := otlptracegrpc.New(ctx, otlptracegrpc.WithGRPCConn(conn))
	if err != nil {
		return nil, fmt.Errorf("failed to create trace exporter: %w", err)
	}

	tp := trace.NewTracerProvider(
		trace.WithBatcher(traceExporter),
		trace.WithResource(res),
		trace.WithSampler(trace.TraceIDRatioBased(0.1)), // 10% sampling
	)
	otel.SetTracerProvider(tp)

	// Setup metrics with Prometheus exporter
	prometheusExporter, err := prometheus.New()
	if err != nil {
		return nil, fmt.Errorf("failed to create prometheus exporter: %w", err)
	}

	mp := sdkmetric.NewMeterProvider(
		sdkmetric.WithReader(prometheusExporter),
		sdkmetric.WithResource(res),
	)
	otel.SetMeterProvider(mp)

	// Start Prometheus HTTP server
	go func() {
		prometheusPort := os.Getenv("PROMETHEUS_PORT")
		if prometheusPort == "" {
			prometheusPort = "8000"
		}
		http.Handle("/metrics", promhttp.Handler())
		addr := fmt.Sprintf(":%s", prometheusPort)
		log.Printf("Prometheus metrics server started on %s\n", addr)
		if err := http.ListenAndServe(addr, nil); err != nil {
			log.Printf("Prometheus server error: %v\n", err)
		}
	}()

	log.Printf("OpenTelemetry initialized for service: %s\n", serviceName)

	return func(ctx context.Context) error {
		if err := tp.Shutdown(ctx); err != nil {
			return fmt.Errorf("failed to shutdown TracerProvider: %w", err)
		}
		if err := mp.Shutdown(ctx); err != nil {
			return fmt.Errorf("failed to shutdown MeterProvider: %w", err)
		}
		return conn.Close()
	}, nil
}

// GetTracer returns a tracer for the given name.
func GetTracer(name string) trace.Tracer {
	return otel.Tracer(name)
}

// GetMeter returns a meter for the given name.
func GetMeter(name string) sdkmetric.Meter {
	return otel.Meter(name)
}

// W3CTraceContext handles W3C TraceContext header propagation.
type W3CTraceContext struct {
	TraceID    string
	SpanID     string
	TraceFlags string
	TraceState string
}

// ExtractTraceContext extracts W3C trace context from HTTP headers.
func ExtractTraceContext(req *http.Request) *W3CTraceContext {
	traceparent := req.Header.Get("traceparent")
	if traceparent == "" {
		return nil
	}

	// Parse traceparent: version-trace_id-parent_id-trace_flags
	var version, traceID, spanID, traceFlags string
	if _, err := fmt.Sscanf(traceparent, "%s-%s-%s-%s", &version, &traceID, &spanID, &traceFlags); err != nil {
		log.Printf("Failed to parse traceparent header: %v\n", err)
		return nil
	}

	if version != "00" {
		return nil // Only support version 00
	}

	return &W3CTraceContext{
		TraceID:    traceID,
		SpanID:     spanID,
		TraceFlags: traceFlags,
		TraceState: req.Header.Get("tracestate"),
	}
}

// InjectTraceContext injects W3C trace context into HTTP headers.
func InjectTraceContext(req *http.Request, ctx *W3CTraceContext) {
	if ctx == nil {
		return
	}
	req.Header.Set("traceparent", fmt.Sprintf("00-%s-%s-%s", ctx.TraceID, ctx.SpanID, ctx.TraceFlags))
	if ctx.TraceState != "" {
		req.Header.Set("tracestate", ctx.TraceState)
	}
}
