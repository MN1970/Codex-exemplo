"""
Example FastAPI application with full OpenTelemetry instrumentation.
Demonstrates tracing, metrics, and W3C TraceContext propagation.
"""

import os
import time
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, BackgroundTasks
from pydantic import BaseModel

from instrumentation import (
    setup_otel_instrumentation,
    instrument_fastapi_app,
    instrument_requests,
    get_tracer,
    get_meter,
    W3CTraceContextPropagator,
)
from metrics import get_metrics


# Request/Response models
class MergeRequest(BaseModel):
    """PR merge request model."""

    pr_id: str
    branch: str
    conflict_resolution_time_seconds: Optional[float] = None


class MLInferenceRequest(BaseModel):
    """ML inference request model."""

    model_id: str
    features: list[float]
    trace_id: Optional[str] = None


class MLInferenceResponse(BaseModel):
    """ML inference response model."""

    prediction: float
    confidence: float
    latency_ms: float
    trace_id: str


# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Setup and teardown for the application."""
    # Setup OpenTelemetry
    service_name = os.getenv("SERVICE_NAME", "manta-gitops")
    jaeger_host = os.getenv("JAEGER_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_PORT", "4317"))
    prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8000"))

    setup_otel_instrumentation(
        service_name=service_name,
        jaeger_host=jaeger_host,
        jaeger_port=jaeger_port,
        prometheus_port=prometheus_port,
    )
    instrument_fastapi_app(app)
    instrument_requests()

    yield

    # Cleanup on shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Manta GitOps Service",
    description="GitOps service with full OpenTelemetry observability",
    lifespan=lifespan,
)


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/merge")
async def merge_pr(
    request: MergeRequest,
    traceparent: Optional[str] = Header(None),
    tracestate: Optional[str] = Header(None),
    background_tasks: BackgroundTasks = None,
):
    """
    Merge a PR with tracing and metrics.

    Demonstrates:
    - W3C TraceContext header propagation
    - Custom span creation
    - Metrics recording
    """
    tracer = get_tracer("merge-handler")
    metrics = get_metrics()

    # Extract trace context from incoming request
    trace_context = W3CTraceContextPropagator.extract_trace_context(
        {"traceparent": traceparent, "tracestate": tracestate}
    )

    with tracer.start_as_current_span("merge_pr") as span:
        span.set_attribute("pr_id", request.pr_id)
        span.set_attribute("branch", request.branch)

        # Record metrics
        merge_success = True
        try:
            # Simulate merge operation
            merge_time = request.conflict_resolution_time_seconds or 0
            if merge_time > 0:
                metrics.git_conflict_resolution_time.record(
                    merge_time,
                    attributes={"pr_id": request.pr_id},
                )

            # Update success rate (example: 95% success)
            metrics.git_merge_success_count.add(1, attributes={"branch": request.branch})
            metrics.git_merge_success_rate.set(0.95)

        except Exception as e:
            merge_success = False
            metrics.git_merge_failure_count.add(1, attributes={"branch": request.branch})
            span.record_exception(e)
            raise

        # Return response with trace context for propagation
        response_trace = W3CTraceContextPropagator.inject_trace_context(
            trace_context or {"trace_id": span.get_span_context().trace_id}
        )

        return {
            "pr_id": request.pr_id,
            "status": "merged" if merge_success else "failed",
            "traceparent": response_trace.get("traceparent"),
            "tracestate": response_trace.get("tracestate"),
        }


@app.post("/ml/infer")
async def ml_inference(request: MLInferenceRequest):
    """
    Run ML inference with tracing and metrics.

    Demonstrates:
    - Inference latency measurement
    - Model accuracy tracking
    - Cross-service trace correlation
    """
    tracer = get_tracer("ml-inference")
    metrics = get_metrics()

    start_time = time.perf_counter()

    with tracer.start_as_current_span("inference") as span:
        span.set_attribute("model_id", request.model_id)
        span.set_attribute("feature_count", len(request.features))

        try:
            # Simulate inference (replace with actual model)
            import random

            inference_time = (time.perf_counter() - start_time) * 1000
            prediction = random.random()
            confidence = random.uniform(0.7, 0.99)

            # Record metrics
            metrics.ml_inference_latency.record(
                inference_time,
                attributes={"model_id": request.model_id},
            )
            metrics.ml_prediction_count.add(1, attributes={"model_id": request.model_id})
            metrics.ml_model_accuracy.set(0.924)  # 92.4% accuracy

            span.set_attribute("prediction", float(prediction))
            span.set_attribute("confidence", float(confidence))
            span.set_attribute("latency_ms", inference_time)

            return MLInferenceResponse(
                prediction=prediction,
                confidence=confidence,
                latency_ms=inference_time,
                trace_id=span.get_span_context().trace_id.to_bytes().hex(),
            )

        except Exception as e:
            span.record_exception(e)
            raise


@app.get("/metrics/summary")
async def metrics_summary():
    """Get current metrics summary."""
    metrics = get_metrics()

    return {
        "git": {
            "merge_success_rate": 0.95,
            "average_review_time_hours": 2.5,
        },
        "ml": {
            "model_accuracy": 0.924,
            "average_inference_latency_ms": 145,
        },
        "infrastructure": {
            "cpu_usage_percent": 45,
            "memory_usage_mb": 512,
        },
    }


@app.get("/metrics/anomalies")
async def anomalies():
    """Get current anomaly scores."""
    metrics = get_metrics()

    return {
        "anomaly_score": 0.15,  # Low anomaly score
        "pattern_quality": 85,
        "unresolved_count": 0,
        "dbscan_cluster_size": 5,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )
