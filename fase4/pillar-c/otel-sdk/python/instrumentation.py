"""
OpenTelemetry instrumentation helper for FastAPI applications.
Provides distributed tracing with OTLP gRPC exporter and Prometheus metrics.
"""

import os
import logging
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME
from prometheus_client import start_http_server

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_otel_instrumentation(
    service_name: str,
    jaeger_host: str = "jaeger",
    jaeger_port: int = 4317,
    prometheus_port: int = 8000,
) -> tuple[TracerProvider, MeterProvider]:
    """
    Setup OpenTelemetry instrumentation for distributed tracing and metrics.

    Args:
        service_name: Name of the service (e.g., "manta-gitops")
        jaeger_host: Jaeger collector hostname (default: jaeger)
        jaeger_port: Jaeger OTLP gRPC port (default: 4317)
        prometheus_port: Prometheus metrics scrape port (default: 8000)

    Returns:
        Tuple of (TracerProvider, MeterProvider) for custom instrumentation
    """

    # Create resource
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": os.getenv("VERSION", "unknown"),
            "deployment": os.getenv("DEPLOYMENT", "kubernetes"),
        }
    )

    # Setup tracing
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{jaeger_host}:{jaeger_port}",
        insecure=True,  # Set to False in production with proper TLS
        headers=(("Authorization", f"Bearer {os.getenv('OTEL_AUTH_TOKEN', '')}"),)
        if os.getenv("OTEL_AUTH_TOKEN")
        else (),
    )

    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(trace_provider)

    # Setup metrics with Prometheus
    prometheus_reader = PrometheusMetricReader()
    metrics_provider = MeterProvider(resource=resource, metric_readers=[prometheus_reader])
    metrics.set_meter_provider(metrics_provider)

    # Start Prometheus HTTP server for metrics scraping
    try:
        start_http_server(port=prometheus_port)
        logger.info(f"Prometheus metrics server started on port {prometheus_port}")
    except OSError as e:
        logger.warning(f"Failed to start Prometheus server: {e}")

    logger.info(f"OpenTelemetry instrumentation initialized for {service_name}")
    return trace_provider, metrics_provider


def instrument_fastapi_app(app) -> None:
    """Instrument a FastAPI application with automatic tracing and metrics."""
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace.get_tracer_provider(),
        meter_provider=metrics.get_meter_provider(),
    )
    logger.info("FastAPI application instrumented")


def instrument_requests() -> None:
    """Instrument requests library for HTTP client tracing."""
    RequestsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
    logger.info("Requests library instrumented")


def instrument_sqlalchemy(engine) -> None:
    """Instrument SQLAlchemy for database tracing."""
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        service=os.getenv("SERVICE_NAME", "unknown"),
        tracer_provider=trace.get_tracer_provider(),
    )
    logger.info("SQLAlchemy instrumented")


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for manual span creation."""
    return trace.get_tracer(__name__)


def get_meter(name: str) -> metrics.Meter:
    """Get a meter instance for manual metric recording."""
    return metrics.get_meter(__name__)


class W3CTraceContextPropagator:
    """
    W3C Trace Context propagator for cross-service span correlation.
    Implements W3C TraceContext specification (https://www.w3.org/TR/trace-context/).
    """

    @staticmethod
    def extract_trace_context(headers: dict) -> Optional[dict]:
        """
        Extract trace context from W3C traceparent header.

        Args:
            headers: HTTP headers dict

        Returns:
            Dict with trace_id, span_id, trace_flags, or None if not present
        """
        traceparent = headers.get("traceparent")
        if not traceparent:
            return None

        try:
            # Format: version-trace_id-parent_id-trace_flags
            parts = traceparent.split("-")
            if len(parts) != 4:
                return None

            version, trace_id, span_id, trace_flags = parts
            if version != "00":  # Only support version 00
                return None

            return {
                "trace_id": trace_id,
                "span_id": span_id,
                "trace_flags": trace_flags,
                "tracestate": headers.get("tracestate", ""),
            }
        except Exception as e:
            logger.warning(f"Failed to extract trace context: {e}")
            return None

    @staticmethod
    def inject_trace_context(span_context: dict) -> dict:
        """
        Inject trace context into W3C traceparent header.

        Args:
            span_context: Dict with trace_id, span_id, trace_flags

        Returns:
            Dict with traceparent and tracestate headers
        """
        trace_id = span_context.get("trace_id", "0" * 32)
        span_id = span_context.get("span_id", "0" * 16)
        trace_flags = span_context.get("trace_flags", "01")
        tracestate = span_context.get("tracestate", "")

        return {
            "traceparent": f"00-{trace_id}-{span_id}-{trace_flags}",
            "tracestate": tracestate,
        }
