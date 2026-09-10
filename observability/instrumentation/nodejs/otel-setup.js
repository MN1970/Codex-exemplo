'use strict';

/**
 * otel-setup.js — Manta Maestro observability bootstrap (Node.js)
 * =================================================================
 *
 * Espelha observability/opentelemetry_setup.py (Python) API-a-API, para
 * que agentes escritos em Node.js (ex.: integrações Slack/SharePoint,
 * serviços de skill em TypeScript) emitam traces/metrics compatíveis no
 * mesmo backend (Jaeger local / Datadog), propagados via W3C traceparent
 * a partir do Maestro (Python).
 *
 * API espelhada:
 *   configureTelemetry(serviceName, opts) -> MantaTelemetry
 *   telemetry.routingSpan(query, fn, opts)
 *   telemetry.agentSpan(agentId, fn, opts)
 *   telemetry.skillSpan(skillName, agentId, fn)
 *   telemetry.inject(carrier) / telemetry.extract(carrier)
 *   telemetry.runWithExtractedContext(carrier, fn)
 *   telemetry.registerQueueDepthProvider(agentId, fn)
 *
 * Dependências (ver observability/package.json):
 *   @opentelemetry/api ^1.9
 *   @opentelemetry/core ^1.25
 *   @opentelemetry/resources ^1.25
 *   @opentelemetry/semantic-conventions ^1.25
 *   @opentelemetry/sdk-trace-node ^1.25
 *   @opentelemetry/sdk-trace-base ^1.25
 *   @opentelemetry/sdk-metrics ^1.25
 *   @opentelemetry/exporter-trace-otlp-grpc ^0.52
 *   @opentelemetry/exporter-metrics-otlp-grpc ^0.52
 */

const {
  trace,
  metrics,
  context,
  propagation,
  SpanKind,
  SpanStatusCode,
} = require('@opentelemetry/api');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { BatchSpanProcessor, ConsoleSpanExporter } = require('@opentelemetry/sdk-trace-base');
const {
  MeterProvider,
  PeriodicExportingMetricReader,
  ConsoleMetricExporter,
} = require('@opentelemetry/sdk-metrics');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-grpc');
const {
  CompositePropagator,
  W3CTraceContextPropagator,
  W3CBaggagePropagator,
} = require('@opentelemetry/core');

// Ver comentário equivalente em opentelemetry_setup.py: todos os alvos
// apontam, por padrão, para o mesmo endpoint local — quem decide o
// fan-out real (Jaeger só / Jaeger+Datadog) é o otel-collector, não o SDK
// da aplicação. Ver docker-compose.yml + otel-collector-config*.yaml.
const TARGET_DEFAULT_ENDPOINTS = {
  otlp_collector: 'http://localhost:4317',
  jaeger_local: 'http://localhost:4317',
  datadog: 'http://localhost:4317',
};

const ROLLING_WINDOW_MS = 5 * 60 * 1000; // 5 min, igual ao lado Python

function nowMs() {
  const [s, ns] = process.hrtime();
  return s * 1000 + ns / 1e6;
}

/** Estatística de janela deslizante para success_rate / error_rate — espelha
 * _RollingStatsRegistry do opentelemetry_setup.py. */
class RollingStatsRegistry {
  constructor(windowMs = ROLLING_WINDOW_MS) {
    this.windowMs = windowMs;
    this.data = new Map();
  }

  record(key, success) {
    const now = Date.now();
    if (!this.data.has(key)) this.data.set(key, []);
    const arr = this.data.get(key);
    arr.push([now, success]);
    this._evict(arr, now);
  }

  rate(key) {
    const now = Date.now();
    const arr = this.data.get(key);
    if (!arr || arr.length === 0) return 1.0;
    this._evict(arr, now);
    if (arr.length === 0) return 1.0;
    const successes = arr.filter(([, ok]) => ok).length;
    return successes / arr.length;
  }

  keys() {
    return Array.from(this.data.keys());
  }

  _evict(arr, now) {
    while (arr.length && now - arr[0][0] > this.windowMs) arr.shift();
  }
}

class MantaTelemetry {
  constructor(tracer, meter, serviceName, agentId, environment) {
    this.tracer = tracer;
    this.meter = meter;
    this.serviceName = serviceName;
    this.agentId = agentId;
    this.environment = environment;

    this._stats = new RollingStatsRegistry();
    this._queueDepthProviders = new Map();

    this.routingLatency = meter.createHistogram('manta.routing.latency_ms', {
      unit: 'ms',
      description: 'Latência ponta a ponta da decisão de roteamento do Maestro',
    });
    this.agentLatency = meter.createHistogram('manta.agent.latency_ms', {
      unit: 'ms',
      description: 'Latência de uma invocação de agente (dispatch -> resposta)',
    });
    this.skillLatency = meter.createHistogram('manta.skill.latency_ms', {
      unit: 'ms',
      description: 'Latência de execução de uma skill individual',
    });

    this.routingRequests = meter.createCounter('manta.routing.requests_total', {
      description: 'Total de requisições de roteamento, por outcome',
    });
    this.agentErrors = meter.createCounter('manta.agent.errors_total', {
      description: 'Total de erros por agente, por tipo de erro',
    });

    this.successRateGauge = meter.createObservableGauge('manta.routing.success_rate', {
      description: 'Taxa de sucesso de roteamento em janela deslizante de 5 min (0-1)',
    });
    this.successRateGauge.addCallback((result) => {
      result.observe(this._stats.rate('__routing__'));
    });

    this.errorRateGauge = meter.createObservableGauge('manta.agent.error_rate', {
      description: 'Taxa de erro por agente em janela deslizante de 5 min (0-1)',
    });
    this.errorRateGauge.addCallback((result) => {
      for (const key of this._stats.keys()) {
        if (key === '__routing__') continue;
        result.observe(1 - this._stats.rate(key), { agent_id: key });
      }
    });

    this.queueDepthGauge = meter.createObservableGauge('manta.agent.queue_depth', {
      description: 'Profundidade atual da fila de tarefas pendentes, por agente',
    });
    this.queueDepthGauge.addCallback((result) => {
      for (const [agentId, provider] of this._queueDepthProviders.entries()) {
        try {
          result.observe(provider(), { agent_id: agentId });
        } catch (err) {
          // nunca deixar um provider quebrar o ciclo de export
        }
      }
    });
  }

  registerQueueDepthProvider(agentId, provider) {
    this._queueDepthProviders.set(agentId, provider);
  }

  unregisterQueueDepthProvider(agentId) {
    this._queueDepthProviders.delete(agentId);
  }

  recordRoutingOutcome(outcome, durationMs) {
    this.routingRequests.add(1, { outcome });
    this.routingLatency.record(durationMs, { outcome });
    this._stats.record('__routing__', outcome === 'success');
  }

  recordAgentOutcome(agentId, outcome, durationMs, errorType) {
    this.agentLatency.record(durationMs, { agent_id: agentId, outcome });
    if (outcome !== 'success') {
      this.agentErrors.add(1, { agent_id: agentId, error_type: errorType || 'unknown' });
    }
    this._stats.record(agentId, outcome === 'success');
  }

  recordSkillLatency(skillName, agentId, durationMs) {
    this.skillLatency.record(durationMs, { skill: skillName, agent_id: agentId });
  }

  /** Span raiz de roteamento (`maestro.route`). `fn(span)` pode ser async. */
  async routingSpan(query, fn, { requestId } = {}) {
    const attributes = {
      'manta.query': String(query).slice(0, 200),
      'manta.layer': 'L4-orchestration',
    };
    if (requestId) attributes['manta.request_id'] = requestId;

    return this.tracer.startActiveSpan(
      'maestro.route',
      { kind: SpanKind.SERVER, attributes },
      async (span) => {
        const t0 = nowMs();
        let outcome = 'success';
        try {
          const result = await fn(span);
          span.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (err) {
          outcome = 'error';
          span.recordException(err);
          span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
          throw err;
        } finally {
          const durationMs = nowMs() - t0;
          span.setAttribute('manta.duration_ms', durationMs);
          this.recordRoutingOutcome(outcome, durationMs);
          span.end();
        }
      },
    );
  }

  /** Span de invocação de agente (`agent.<phase>`). */
  async agentSpan(agentId, fn, { phase = 'dispatch', segment } = {}) {
    const attributes = {
      'manta.agent.id': agentId,
      'manta.agent.phase': phase,
      'manta.layer': 'L2-agent',
    };
    if (segment) attributes['manta.agent.segment'] = segment;

    return this.tracer.startActiveSpan(
      `agent.${phase}`,
      { kind: SpanKind.INTERNAL, attributes },
      async (span) => {
        const t0 = nowMs();
        let outcome = 'success';
        let errorType;
        try {
          const result = await fn(span);
          span.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (err) {
          outcome = 'error';
          errorType = err.name || 'Error';
          span.recordException(err);
          span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
          throw err;
        } finally {
          const durationMs = nowMs() - t0;
          span.setAttribute('manta.duration_ms', durationMs);
          this.recordAgentOutcome(agentId, outcome, durationMs, errorType);
          span.end();
        }
      },
    );
  }

  /** Span de execução de skill (`skill.<nome>`). */
  async skillSpan(skillName, agentId, fn) {
    const attributes = {
      'manta.skill.name': skillName,
      'manta.agent.id': agentId,
      'manta.layer': 'L1-skill',
    };
    return this.tracer.startActiveSpan(`skill.${skillName}`, { kind: SpanKind.INTERNAL, attributes }, async (span) => {
      const t0 = nowMs();
      try {
        const result = await fn(span);
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (err) {
        span.recordException(err);
        span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
        throw err;
      } finally {
        const durationMs = nowMs() - t0;
        span.setAttribute('manta.duration_ms', durationMs);
        this.recordSkillLatency(skillName, agentId, durationMs);
        span.end();
      }
    });
  }

  /** Injeta traceparent/tracestate/baggage no carrier (ex.: headers de
   * resposta HTTP, ou de uma nova chamada saindo deste agente). */
  inject(carrier = {}) {
    propagation.inject(context.active(), carrier);
    return carrier;
  }

  /** Extrai um Context a partir de um carrier recebido (ex.: req.headers
   * de uma chamada HTTP feita pelo Maestro). */
  extract(carrier) {
    return propagation.extract(context.active(), carrier);
  }

  /** Executa `fn` com o Context extraído do carrier como contexto ativo —
   * spans criados dentro de `fn` viram filhos do trace remoto (Maestro). */
  runWithExtractedContext(carrier, fn) {
    const ctx = this.extract(carrier);
    return context.with(ctx, fn);
  }
}

let _telemetry = null;
let _tracerProviderRef = null;
let _meterProviderRef = null;

function configureTelemetry(
  serviceName,
  {
    agentId,
    environment = process.env.MANTA_ENV || 'local',
    exporterTarget = process.env.OTEL_EXPORTER_TARGET || 'otlp_collector',
    otlpEndpoint,
    serviceVersion = process.env.MANTA_VERSION || 'v5.0.1',
    consoleFallback,
  } = {},
) {
  if (_telemetry) return _telemetry;

  const resolvedAgentId = agentId || serviceName;
  const resolvedConsoleFallback = consoleFallback ?? environment === 'local';
  const endpoint =
    otlpEndpoint ||
    process.env.OTEL_EXPORTER_OTLP_ENDPOINT ||
    TARGET_DEFAULT_ENDPOINTS[exporterTarget] ||
    TARGET_DEFAULT_ENDPOINTS.otlp_collector;

  const resource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
    [SemanticResourceAttributes.SERVICE_VERSION]: serviceVersion,
    'deployment.environment': environment,
    'manta.agent.id': resolvedAgentId,
    'manta.exporter_target': exporterTarget,
  });

  const tracerProvider = new NodeTracerProvider({ resource });
  tracerProvider.addSpanProcessor(new BatchSpanProcessor(new OTLPTraceExporter({ url: endpoint })));
  if (resolvedConsoleFallback) {
    tracerProvider.addSpanProcessor(new BatchSpanProcessor(new ConsoleSpanExporter()));
  }

  // W3C TraceContext + Baggage — mesmo par usado em opentelemetry_setup.py,
  // garantindo handoffs Maestro (Python) <-> agente (Node.js) sem tradução.
  tracerProvider.register({
    propagator: new CompositePropagator({
      propagators: [new W3CTraceContextPropagator(), new W3CBaggagePropagator()],
    }),
  });

  const metricReaders = [
    new PeriodicExportingMetricReader({
      exporter: new OTLPMetricExporter({ url: endpoint }),
      exportIntervalMillis: 15000,
    }),
  ];
  if (resolvedConsoleFallback) {
    metricReaders.push(
      new PeriodicExportingMetricReader({
        exporter: new ConsoleMetricExporter(),
        exportIntervalMillis: 30000,
      }),
    );
  }
  const meterProvider = new MeterProvider({ resource, readers: metricReaders });
  metrics.setGlobalMeterProvider(meterProvider);

  // Guardamos as instâncias reais (não os proxies retornados por
  // trace.getTracerProvider()/metrics.getMeterProvider()) para garantir que
  // shutdownTelemetry() consiga chamar .shutdown() de fato e flushar o
  // último batch de spans/métricas antes do processo terminar.
  _tracerProviderRef = tracerProvider;
  _meterProviderRef = meterProvider;

  const tracer = trace.getTracer('manta.telemetry', serviceVersion);
  const meter = metrics.getMeter('manta.telemetry', serviceVersion);

  _telemetry = new MantaTelemetry(tracer, meter, serviceName, resolvedAgentId, environment);
  return _telemetry;
}

function getTelemetry() {
  if (!_telemetry) {
    throw new Error(
      'Telemetria não configurada. Chame configureTelemetry(...) no startup ' +
        'do processo antes de instrumentar.',
    );
  }
  return _telemetry;
}

async function shutdownTelemetry() {
  if (_tracerProviderRef) {
    await _tracerProviderRef.shutdown();
    _tracerProviderRef = null;
  }
  if (_meterProviderRef) {
    await _meterProviderRef.shutdown();
    _meterProviderRef = null;
  }
  _telemetry = null;
}

module.exports = {
  configureTelemetry,
  getTelemetry,
  shutdownTelemetry,
  MantaTelemetry,
};
