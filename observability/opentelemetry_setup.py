"""
opentelemetry_setup.py — Manta Maestro observability bootstrap (Python)
========================================================================

Instrumentação padrão OpenTelemetry para o ecossistema Manta Maestro
(Manta 00 + agentes horizontais/verticais). Fornece, em um único módulo:

  * TracerProvider + MeterProvider configurados via OTLP (gRPC), com
    fallback opcional para console em ambiente local.
  * Propagação de contexto W3C TraceContext + Baggage entre Maestro e
    agentes (Python <-> Python e Python <-> Node.js — ver
    instrumentation/nodejs/otel-setup.js para o par Node).
  * Spans padronizados: `maestro.route` (routing span), `agent.<phase>`
    (agent span) e `skill.<nome>` (skill span) — mapeando a pirâmide de
    camadas L4/L2/L1 descrita em
    docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md.
  * Métricas: manta.routing.latency_ms, manta.routing.success_rate,
    manta.agent.latency_ms, manta.agent.error_rate,
    manta.agent.queue_depth, manta.agent.errors_total.

Backend de exportação: Jaeger local (via docker-compose deste diretório)
ou Datadog (Agent com OTLP intake habilitado / otel-collector com o
exporter `datadog`). Ver observability/docker-compose.yml e
observability/otel-collector-config.yaml.

Uso mínimo (Maestro):

    from opentelemetry_setup import configure_telemetry

    telemetry = configure_telemetry("manta-maestro", agent_id="manta-00")

    with telemetry.routing_span("edital de saneamento AySA") as span:
        with telemetry.agent_span("manta-03-s8", segment="saneamento") as aspan:
            with telemetry.skill_span("ler-edital", "manta-03-s8"):
                ...  # trabalho da skill

Variáveis de ambiente relevantes:

    MANTA_ENV                  local | staging | prod        (default: local)
    MANTA_VERSION               versão do serviço/agente       (default: v5.0.1)
    OTEL_EXPORTER_TARGET        otlp_collector | jaeger_local | datadog | console
    OTEL_EXPORTER_OTLP_ENDPOINT override explícito do endpoint OTLP (host:port)

Ver instrumentation/python/maestro_routing_example.py para um exemplo
completo de ponta a ponta (routing -> agent -> skill -> métricas ->
propagação de contexto para um agente remoto).
"""

from __future__ import annotations

import contextlib
import functools
import logging
import os
import threading
import time
from collections import defaultdict, deque
from typing import Callable, Dict, Mapping, MutableMapping, Optional

from opentelemetry import baggage, context as otel_context, metrics, propagate, trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.metrics import Observation
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

    _OTLP_AVAILABLE = True
except ImportError:  # pragma: no cover - degrade gracefully in minimal envs
    _OTLP_AVAILABLE = False

log = logging.getLogger("manta.telemetry")

# ---------------------------------------------------------------------------
# Endpoints padrão por alvo de exportação
# ---------------------------------------------------------------------------
# Todos os alvos, por padrão, apontam para o mesmo host:porta local
# (localhost:4317) porque, no docker-compose deste diretório, é o
# `otel-collector` quem publica essa porta no host e faz o fan-out para
# Jaeger e (opcionalmente) Datadog — ver otel-collector-config.yaml.
# Para falar diretamente com um backend (sem collector), suba o profile
# correspondente no docker-compose e/ou sobrescreva via
# OTEL_EXPORTER_OTLP_ENDPOINT / otlp_endpoint=.
TARGET_DEFAULT_ENDPOINTS: Dict[str, str] = {
    "otlp_collector": "http://localhost:4317",
    "jaeger_local": "http://localhost:4317",
    "datadog": "http://localhost:4317",
}

_ROLLING_WINDOW_SECONDS = 300  # janela de 5 min para success_rate / error_rate


# ---------------------------------------------------------------------------
# Estatística de janela deslizante (para as métricas *_rate, calculadas
# em processo — evita depender de PromQL/rate() no backend para casos
# simples de dashboard "ao vivo").
# ---------------------------------------------------------------------------
class _RollingStatsRegistry:
    def __init__(self, window_seconds: int = _ROLLING_WINDOW_SECONDS) -> None:
        self._window = window_seconds
        self._lock = threading.Lock()
        self._data: Dict[str, deque] = defaultdict(deque)

    def record(self, key: str, success: bool) -> None:
        now = time.time()
        with self._lock:
            dq = self._data[key]
            dq.append((now, success))
            self._evict(dq, now)

    def rate(self, key: str) -> float:
        now = time.time()
        with self._lock:
            dq = self._data.get(key)
            if not dq:
                return 1.0
            self._evict(dq, now)
            if not dq:
                return 1.0
            successes = sum(1 for _, ok in dq if ok)
            return successes / len(dq)

    def keys(self):
        with self._lock:
            return [k for k in self._data.keys()]

    @staticmethod
    def _evict(dq: deque, now: float) -> None:
        while dq and now - dq[0][0] > _ROLLING_WINDOW_SECONDS:
            dq.popleft()


# ---------------------------------------------------------------------------
# Handle único de telemetria: tracer + meter + instrumentos + helpers.
# ---------------------------------------------------------------------------
class MantaTelemetry:
    """Handle de telemetria para um serviço (Maestro ou um agente).

    Encapsula tracer, meter, instrumentos de métrica pré-criados e os
    context managers de span padronizados (routing/agent/skill), além
    dos helpers de propagação de contexto W3C usados nos handoffs entre
    Maestro e agentes (mesmo processo, HTTP, fila etc).
    """

    def __init__(
        self,
        tracer: trace.Tracer,
        meter: metrics.Meter,
        service_name: str,
        agent_id: str,
        environment: str,
    ) -> None:
        self.tracer = tracer
        self.meter = meter
        self.service_name = service_name
        self.agent_id = agent_id
        self.environment = environment

        self._stats = _RollingStatsRegistry()
        self._queue_depth_providers: Dict[str, Callable[[], int]] = {}

        # --- latência (histogramas) ---
        self.routing_latency = meter.create_histogram(
            name="manta.routing.latency_ms",
            unit="ms",
            description="Latência ponta a ponta da decisão de roteamento do Maestro",
        )
        self.agent_latency = meter.create_histogram(
            name="manta.agent.latency_ms",
            unit="ms",
            description="Latência de uma invocação de agente (dispatch -> resposta)",
        )
        self.skill_latency = meter.create_histogram(
            name="manta.skill.latency_ms",
            unit="ms",
            description="Latência de execução de uma skill individual",
        )

        # --- contadores ---
        self.routing_requests = meter.create_counter(
            name="manta.routing.requests_total",
            description="Total de requisições de roteamento, por outcome (success|error)",
        )
        self.agent_errors = meter.create_counter(
            name="manta.agent.errors_total",
            description="Total de erros por agente, por tipo de erro",
        )

        # --- gauges observáveis (calculados sob demanda no export) ---
        self.success_rate_gauge = meter.create_observable_gauge(
            name="manta.routing.success_rate",
            callbacks=[self._observe_success_rate],
            description="Taxa de sucesso de roteamento em janela deslizante de 5 min (0-1)",
        )
        self.error_rate_gauge = meter.create_observable_gauge(
            name="manta.agent.error_rate",
            callbacks=[self._observe_error_rate],
            description="Taxa de erro por agente em janela deslizante de 5 min (0-1)",
        )
        self.queue_depth_gauge = meter.create_observable_gauge(
            name="manta.agent.queue_depth",
            callbacks=[self._observe_queue_depth],
            description="Profundidade atual da fila de tarefas pendentes, por agente",
        )

    # ------------------------------------------------------------------
    # Registro de provedor de queue depth (o agente expõe uma função que
    # retorna o tamanho atual da sua fila; o gauge observável a lê a cada
    # ciclo de export, sem polling ativo do lado da telemetria).
    # ------------------------------------------------------------------
    def register_queue_depth_provider(self, agent_id: str, provider: Callable[[], int]) -> None:
        self._queue_depth_providers[agent_id] = provider

    def unregister_queue_depth_provider(self, agent_id: str) -> None:
        self._queue_depth_providers.pop(agent_id, None)

    def _observe_queue_depth(self, options):
        for agent_id, provider in list(self._queue_depth_providers.items()):
            try:
                yield Observation(provider(), {"agent_id": agent_id})
            except Exception:  # nunca deixar um provider quebrar o export
                log.exception("queue_depth provider falhou para agent_id=%s", agent_id)

    def _observe_success_rate(self, options):
        yield Observation(self._stats.rate("__routing__"), {})

    def _observe_error_rate(self, options):
        for agent_id in self._stats.keys():
            if agent_id == "__routing__":
                continue
            yield Observation(1.0 - self._stats.rate(agent_id), {"agent_id": agent_id})

    # ------------------------------------------------------------------
    # Registro manual de outcomes (usado pelos context managers abaixo,
    # mas também exposto para quem quiser instrumentar sem os spans).
    # ------------------------------------------------------------------
    def record_routing_outcome(self, outcome: str, duration_ms: float) -> None:
        self.routing_requests.add(1, {"outcome": outcome})
        self.routing_latency.record(duration_ms, {"outcome": outcome})
        self._stats.record("__routing__", outcome == "success")

    def record_agent_outcome(
        self, agent_id: str, outcome: str, duration_ms: float, error_type: Optional[str] = None
    ) -> None:
        self.agent_latency.record(duration_ms, {"agent_id": agent_id, "outcome": outcome})
        if outcome != "success":
            self.agent_errors.add(1, {"agent_id": agent_id, "error_type": error_type or "unknown"})
        self._stats.record(agent_id, outcome == "success")

    def record_skill_latency(self, skill_name: str, agent_id: str, duration_ms: float) -> None:
        self.skill_latency.record(duration_ms, {"skill": skill_name, "agent_id": agent_id})

    # ------------------------------------------------------------------
    # Spans padronizados — L4 (routing), L2 (agent), L1 (skill).
    # ------------------------------------------------------------------
    @contextlib.contextmanager
    def routing_span(self, query: str, *, request_id: Optional[str] = None):
        """Span raiz de uma decisão de roteamento do Maestro (`maestro.route`)."""
        attrs = {
            "manta.query": (query or "")[:200],
            "manta.layer": "L4-orchestration",
        }
        if request_id:
            attrs["manta.request_id"] = request_id
        with self.tracer.start_as_current_span(
            "maestro.route", kind=trace.SpanKind.SERVER, attributes=attrs
        ) as span:
            t0 = time.perf_counter()
            outcome = "success"
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as exc:
                outcome = "error"
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                duration_ms = (time.perf_counter() - t0) * 1000
                span.set_attribute("manta.duration_ms", duration_ms)
                self.record_routing_outcome(outcome, duration_ms)

    @contextlib.contextmanager
    def agent_span(self, agent_id: str, *, phase: str = "dispatch", segment: Optional[str] = None):
        """Span de invocação de um agente (`agent.<phase>`), filho do routing span
        se chamado dentro do bloco `with routing_span(...)`."""
        attrs = {
            "manta.agent.id": agent_id,
            "manta.agent.phase": phase,
            "manta.layer": "L2-agent",
        }
        if segment:
            attrs["manta.agent.segment"] = segment
        with self.tracer.start_as_current_span(
            f"agent.{phase}", kind=trace.SpanKind.INTERNAL, attributes=attrs
        ) as span:
            t0 = time.perf_counter()
            outcome = "success"
            error_type: Optional[str] = None
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as exc:
                outcome = "error"
                error_type = type(exc).__name__
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                duration_ms = (time.perf_counter() - t0) * 1000
                span.set_attribute("manta.duration_ms", duration_ms)
                self.record_agent_outcome(agent_id, outcome, duration_ms, error_type)

    @contextlib.contextmanager
    def skill_span(self, skill_name: str, agent_id: str):
        """Span de execução de uma skill (`skill.<nome>`), filho do agent span."""
        attrs = {
            "manta.skill.name": skill_name,
            "manta.agent.id": agent_id,
            "manta.layer": "L1-skill",
        }
        with self.tracer.start_as_current_span(
            f"skill.{skill_name}", kind=trace.SpanKind.INTERNAL, attributes=attrs
        ) as span:
            t0 = time.perf_counter()
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise
            finally:
                duration_ms = (time.perf_counter() - t0) * 1000
                span.set_attribute("manta.duration_ms", duration_ms)
                self.record_skill_latency(skill_name, agent_id, duration_ms)

    # ------------------------------------------------------------------
    # Propagação de contexto (W3C traceparent + baggage) entre agentes —
    # via headers HTTP, metadata de fila (SQS/RabbitMQ/Supabase Realtime)
    # ou qualquer carrier Mapping[str, str].
    # ------------------------------------------------------------------
    def inject(self, carrier: Optional[MutableMapping[str, str]] = None) -> MutableMapping[str, str]:
        """Injeta traceparent/tracestate/baggage no carrier (ex.: headers HTTP
        de uma chamada Maestro -> agente, incluindo agentes Node.js)."""
        carrier = {} if carrier is None else carrier
        propagate.inject(carrier)
        return carrier

    def extract(self, carrier: Mapping[str, str]) -> otel_context.Context:
        """Extrai um Context OTel a partir de um carrier recebido (ex.: headers
        HTTP de uma requisição recebida de outro agente/Maestro)."""
        return propagate.extract(carrier)

    @contextlib.contextmanager
    def continue_from_carrier(self, carrier: Mapping[str, str]):
        """Torna o Context extraído do carrier o contexto ativo dentro do bloco
        `with` — spans criados dentro dele viram filhos do trace remoto."""
        ctx = self.extract(carrier)
        token = otel_context.attach(ctx)
        try:
            yield ctx
        finally:
            otel_context.detach(token)

    def with_baggage(self, key: str, value: str, carrier: Optional[MutableMapping[str, str]] = None):
        """Anexa um item de baggage (ex.: manta.request_id, manta.tenant) ao
        contexto ativo e retorna o carrier injetado — útil para propagar
        metadados de negócio junto com o trace."""
        ctx = baggage.set_baggage(key, value)
        token = otel_context.attach(ctx)
        try:
            return self.inject(carrier)
        finally:
            otel_context.detach(token)

    def traced_skill(self, skill_name: str):
        """Decorator de conveniência: `@telemetry.traced_skill("ler-edital")`.
        A função decorada deve receber `agent_id` como kwarg."""

        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, agent_id: str = "unknown", **kwargs):
                with self.skill_span(skill_name, agent_id):
                    return func(*args, agent_id=agent_id, **kwargs)

            return wrapper

        return decorator


# ---------------------------------------------------------------------------
# Bootstrap / singleton de processo
# ---------------------------------------------------------------------------
_telemetry: Optional[MantaTelemetry] = None
_telemetry_lock = threading.Lock()


def _resolve_endpoint(exporter_target: str, otlp_endpoint: Optional[str]) -> str:
    if otlp_endpoint:
        return otlp_endpoint
    env_override = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if env_override:
        return env_override
    return TARGET_DEFAULT_ENDPOINTS.get(exporter_target, TARGET_DEFAULT_ENDPOINTS["otlp_collector"])


def configure_telemetry(
    service_name: str,
    *,
    agent_id: Optional[str] = None,
    environment: Optional[str] = None,
    exporter_target: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    service_version: Optional[str] = None,
    console_fallback: Optional[bool] = None,
    force_reconfigure: bool = False,
) -> MantaTelemetry:
    """Configura TracerProvider + MeterProvider globais e retorna o handle
    `MantaTelemetry` (singleton por processo, salvo `force_reconfigure=True`).

    Args:
        service_name: nome do serviço OTel (ex.: "manta-maestro",
            "agente-saneamento"). Vira `service.name` no Resource.
        agent_id: ID canônico do agente no registry Manta (ex.: "manta-00",
            "manta-03-s8"). Default: igual a `service_name`.
        environment: "local" | "staging" | "prod". Default: env
            MANTA_ENV ou "local".
        exporter_target: "otlp_collector" | "jaeger_local" | "datadog" |
            "console". Default: env OTEL_EXPORTER_TARGET ou "otlp_collector".
        otlp_endpoint: override explícito do endpoint OTLP gRPC
            (ex.: "http://otel-collector:4317"). Tem prioridade sobre
            OTEL_EXPORTER_OTLP_ENDPOINT e sobre o default do target.
        service_version: default env MANTA_VERSION ou "v5.0.1".
        console_fallback: também exporta para stdout (útil em dev sem
            docker-compose rodando). Default: True quando environment=="local".
    """
    global _telemetry
    with _telemetry_lock:
        if _telemetry is not None and not force_reconfigure:
            return _telemetry

        environment = environment or os.getenv("MANTA_ENV", "local")
        exporter_target = (exporter_target or os.getenv("OTEL_EXPORTER_TARGET", "otlp_collector")).lower()
        service_version = service_version or os.getenv("MANTA_VERSION", "v5.0.1")
        if console_fallback is None:
            console_fallback = environment == "local"
        resolved_agent_id = agent_id or service_name

        resource = Resource.create(
            {
                SERVICE_NAME: service_name,
                SERVICE_VERSION: service_version,
                "deployment.environment": environment,
                "manta.agent.id": resolved_agent_id,
                "manta.exporter_target": exporter_target,
            }
        )

        tracer_provider = TracerProvider(resource=resource)
        metric_readers = []

        if exporter_target != "console" and _OTLP_AVAILABLE:
            endpoint = _resolve_endpoint(exporter_target, otlp_endpoint)
            tracer_provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
            )
            metric_readers.append(
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=endpoint, insecure=True),
                    export_interval_millis=15_000,
                )
            )
            log.info("Telemetria OTLP configurada: target=%s endpoint=%s", exporter_target, endpoint)
        elif exporter_target != "console" and not _OTLP_AVAILABLE:
            log.warning(
                "opentelemetry-exporter-otlp-proto-grpc não instalado; "
                "caindo para console-only. `pip install -r requirements.txt`."
            )

        if console_fallback or exporter_target == "console":
            tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
            metric_readers.append(
                PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=30_000)
            )

        trace.set_tracer_provider(tracer_provider)
        meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
        metrics.set_meter_provider(meter_provider)

        # W3C TraceContext + Baggage — compatível nativamente com o par
        # Node.js (@opentelemetry/core W3CTraceContextPropagator), permitindo
        # handoffs Maestro (Python) <-> agente (Node.js) sem tradução manual.
        propagate.set_global_textmap(
            CompositePropagator([TraceContextTextMapPropagator(), W3CBaggagePropagator()])
        )

        tracer = trace.get_tracer("manta.telemetry", service_version)
        meter = metrics.get_meter("manta.telemetry", service_version)

        _telemetry = MantaTelemetry(tracer, meter, service_name, resolved_agent_id, environment)
        return _telemetry


def get_telemetry() -> MantaTelemetry:
    """Retorna o handle configurado por `configure_telemetry()`. Lança
    RuntimeError se chamado antes do bootstrap (falha cedo, de propósito —
    evita spans "órfãos" indo para um provider no-op silenciosamente)."""
    if _telemetry is None:
        raise RuntimeError(
            "Telemetria não configurada. Chame configure_telemetry(...) no "
            "startup do processo (Maestro ou agente) antes de instrumentar."
        )
    return _telemetry


def shutdown_telemetry() -> None:
    """Força flush + shutdown dos exporters (chamar em atexit / SIGTERM
    handler dos serviços de longa duração, para não perder o último batch)."""
    global _telemetry
    provider = trace.get_tracer_provider()
    if hasattr(provider, "shutdown"):
        provider.shutdown()
    meter_provider = metrics.get_meter_provider()
    if hasattr(meter_provider, "shutdown"):
        meter_provider.shutdown()
    _telemetry = None


# ---------------------------------------------------------------------------
# Smoke test manual: `python opentelemetry_setup.py`
# Gera um trace completo routing -> agent -> skill contra o backend
# configurado em OTEL_EXPORTER_TARGET (default otlp_collector), e imprime
# o trace_id para conferência na UI do Jaeger (http://localhost:16686).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    telemetry = configure_telemetry("manta-maestro", agent_id="manta-00", environment="local")

    with telemetry.routing_span("edital de saneamento AySA — ETE Riachuelo", request_id="smoke-test-001") as rspan:
        trace_id = format(rspan.get_span_context().trace_id, "032x")
        print(f"trace_id={trace_id}  (procure em http://localhost:16686/trace/{trace_id})")

        with telemetry.agent_span("manta-03-s8", segment="saneamento") as _aspan:
            time.sleep(0.05)
            with telemetry.skill_span("ler-edital", "manta-03-s8"):
                time.sleep(0.08)
            with telemetry.skill_span("aluci-guard", "manta-03-s8"):
                time.sleep(0.02)

    shutdown_telemetry()
