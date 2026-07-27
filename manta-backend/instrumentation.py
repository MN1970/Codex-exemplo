"""
OpenTelemetry instrumentation for Manta Maestro backend.

Provides:
- Distributed tracing via OTLP exporter (DataDog/Jaeger)
- FastAPI middleware with request/span context
- Prometheus metrics (latency, routing accuracy, model inference)
- Structured JSON logging with trace context propagation
- Auto-instrumentation for PostgreSQL, requests library
"""

import json
import logging
import logging.handlers
import os
import time
from datetime import datetime
from typing import Callable, Optional

from fastapi import FastAPI, Request
from opentelemetry import metrics, trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPTraceExporter,
)
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.postgresql import PostgreSQLInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.aggregation import (
    ExplicitBucketHistogramAggregation,
)
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from prometheus_client import Counter, Histogram, Gauge, generate_latest


class StructuredJSONFormatter(logging.Formatter):
    """JSON formatter for structured logging with trace context."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with trace context."""
        trace_context = trace.get_current_span().get_span_context()

        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": format(trace_context.trace_id, "032x")
            if trace_context.trace_id
            else None,
            "span_id": format(trace_context.span_id, "016x")
            if trace_context.span_id
            else None,
            "trace_flags": trace_context.trace_flags.trace_id
            if trace_context.trace_flags
            else None,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add custom fields from LogRecord
        if hasattr(record, "extra_fields"):
            log_obj.update(record.extra_fields)

        return json.dumps(log_obj, default=str)


class TracedLogger(logging.Logger):
    """Logger that automatically adds trace context to all logs."""

    def _log(
        self,
        level: int,
        msg: str,
        args,
        exc_info=None,
        extra=None,
        stack_info=None,
        **kwargs,
    ):
        """Override _log to add trace context."""
        if extra is None:
            extra = {}

        # Extract trace context
        span = trace.get_current_span()
        span_context = span.get_span_context()

        extra["extra_fields"] = {
            "trace_id": format(span_context.trace_id, "032x")
            if span_context.trace_id
            else None,
            "span_id": format(span_context.span_id, "016x")
            if span_context.span_id
            else None,
        }

        super()._log(level, msg, args, exc_info, extra, stack_info, **kwargs)


logging.setLoggerClass(TracedLogger)


def setup_tracing(app_name: str = "manta-maestro"):
    """Initialize OpenTelemetry tracing with OTLP exporter."""

    environment = os.getenv("ENVIRONMENT", "development")
    version = os.getenv("APP_VERSION", "unknown")

    # Resource attributes
    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: app_name,
            ResourceAttributes.SERVICE_VERSION: version,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
            "service.namespace": "manta",
            "team": "platform",
        }
    )

    # Tracer provider with OTLP exporter
    otlp_exporter = OTLPTraceExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317"),
        insecure=environment != "production",
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(tracer_provider)

    return trace.get_tracer(__name__)


def setup_metrics(app_name: str = "manta-maestro"):
    """Initialize OpenTelemetry metrics with Prometheus exporter."""

    environment = os.getenv("ENVIRONMENT", "development")

    resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: app_name,
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: environment,
        }
    )

    # Prometheus exporter
    prometheus_reader = PrometheusMetricReader()

    # Metric provider with custom views
    metric_provider = MeterProvider(
        resource=resource,
        metric_readers=[prometheus_reader],
        views=[
            # HTTP request duration histogram with custom buckets
            View(
                instrument_name="http.server.request.duration",
                aggregation=ExplicitBucketHistogramAggregation(
                    boundaries=[
                        0.005,
                        0.01,
                        0.05,
                        0.1,
                        0.5,
                        1.0,
                        5.0,
                        10.0,
                    ]
                ),
            ),
        ],
    )

    metrics.set_meter_provider(metric_provider)

    return metrics.get_meter(__name__)


def setup_logging(log_level: str = "INFO"):
    """Configure structured JSON logging with trace context."""

    # Remove default handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # JSON formatter
    formatter = StructuredJSONFormatter()

    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        filename="logs/manta-maestro.log",
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("opentelemetry").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root_logger


def setup_auto_instrumentation():
    """Auto-instrument FastAPI, PostgreSQL, requests library."""

    # FastAPI instrumentation
    FastAPIInstrumentor.instrument_app(app=None)  # Will be called with app instance

    # PostgreSQL instrumentation
    PostgreSQLInstrumentor().instrument()

    # Requests library instrumentation
    RequestsInstrumentor().instrument()


# Custom metrics
class MantaMetrics:
    """Custom metrics for Manta Maestro."""

    def __init__(self, meter):
        """Initialize custom metrics."""
        self.meter = meter

        # Request metrics
        self.request_duration = Histogram(
            name="http_request_duration_seconds",
            documentation="HTTP request duration in seconds",
            labelnames=["method", "endpoint", "status"],
            buckets=(0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, float("inf")),
        )

        self.request_count = Counter(
            name="http_requests_total",
            documentation="Total HTTP requests",
            labelnames=["method", "endpoint", "status"],
        )

        # Routing metrics
        self.routing_accuracy = Gauge(
            name="routing_accuracy",
            documentation="Routing accuracy (0-1)",
            labelnames=["agent", "environment"],
        )

        self.routing_decisions = Counter(
            name="routing_decisions_total",
            documentation="Total routing decisions",
            labelnames=["agent", "decision", "environment"],
        )

        # Model metrics
        self.model_latency = Histogram(
            name="model_inference_duration_seconds",
            documentation="Model inference latency in seconds",
            labelnames=["model_type", "agent"],
            buckets=(
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
                float("inf"),
            ),
        )

        self.model_tokens = Counter(
            name="model_tokens_total",
            documentation="Total tokens used by models",
            labelnames=["model_type", "agent", "token_type"],  # token_type: input/output
        )

        # Database metrics
        self.db_connection_pool = Gauge(
            name="database_connection_pool_size",
            documentation="Database connection pool size",
            labelnames=["pool", "status"],  # status: active, idle, waiting
        )

        self.db_query_duration = Histogram(
            name="database_query_duration_seconds",
            documentation="Database query duration in seconds",
            labelnames=["operation", "table"],
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf")),
        )

        # Cache metrics
        self.cache_hits = Counter(
            name="cache_hits_total",
            documentation="Total cache hits",
            labelnames=["cache_type"],
        )

        self.cache_misses = Counter(
            name="cache_misses_total",
            documentation="Total cache misses",
            labelnames=["cache_type"],
        )


def instrument_fastapi(app: FastAPI, tracer, meter, metrics: MantaMetrics):
    """Add FastAPI middleware for tracing and metrics."""

    # Instrument the app for auto-tracing
    FastAPIInstrumentor.instrument_app(app)

    @app.middleware("http")
    async def trace_and_metrics_middleware(request: Request, call_next: Callable):
        """FastAPI middleware for request tracing and metrics."""
        start_time = time.perf_counter()
        path = request.url.path
        method = request.method

        # Extract or create trace context
        span_ctx = trace.set_span_in_context(trace.get_current_span())

        # Add custom attributes to span
        span = trace.get_current_span()
        span.set_attribute("http.method", method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.target", path)

        # Extract user context if present
        if hasattr(request.state, "user_id"):
            span.set_attribute("user.id", request.state.user_id)

        # Extract agent context if present
        if hasattr(request.state, "agent_slug"):
            span.set_attribute("manta.agent", request.state.agent_slug)

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            span.record_exception(exc)
            raise
        finally:
            # Record metrics
            duration = time.perf_counter() - start_time
            metrics.request_duration.labels(
                method=method, endpoint=path, status=status_code
            ).observe(duration)
            metrics.request_count.labels(
                method=method, endpoint=path, status=status_code
            ).inc()

            # Add duration to span
            span.set_attribute("http.status_code", status_code)
            span.set_attribute("http.duration_ms", int(duration * 1000))

        return response

    # Prometheus /metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus metrics endpoint."""
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

        return generate_latest()

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


def initialize_observability(app: FastAPI, app_name: str = "manta-maestro"):
    """Initialize complete observability stack."""

    # Setup logging
    logger = setup_logging(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    logger.info(f"Initializing observability for {app_name}")

    # Setup tracing
    tracer = setup_tracing(app_name)

    # Setup metrics
    meter = setup_metrics(app_name)

    # Initialize custom metrics
    manta_metrics = MantaMetrics(meter)

    # Auto-instrument libraries
    setup_auto_instrumentation()

    # Instrument FastAPI
    instrument_fastapi(app, tracer, meter, manta_metrics)

    logger.info("Observability stack initialized successfully")

    return {
        "logger": logger,
        "tracer": tracer,
        "meter": meter,
        "metrics": manta_metrics,
    }
