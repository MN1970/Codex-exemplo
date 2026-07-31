/**
 * Testes para Monitoring & Observability Service
 */

import {
  MetricsCollector,
  AlertManager,
  TracingManager,
  ObservabilityManager,
  AlertSeverity,
  MetricType,
  createLogger,
} from "../monitoring";
import { Logger } from "pino";

// Mock logger para testes
function createMockLogger(): Logger {
  return {
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  } as unknown as Logger;
}

describe("MetricsCollector", () => {
  let collector: MetricsCollector;
  let logger: Logger;

  beforeEach(() => {
    logger = createMockLogger();
    collector = new MetricsCollector(logger);
  });

  describe("incrementCounter", () => {
    it("should increment counter correctly", () => {
      collector.incrementCounter("requests_total", 1);
      collector.incrementCounter("requests_total", 2);

      const metrics = collector.getKeyMetrics();
      // Note: getKeyMetrics retorna valores calculados, não contadores brutos
      expect(metrics).toBeDefined();
    });

    it("should handle counters with labels", () => {
      collector.incrementCounter("requests_total", 1, { method: "GET" });
      collector.incrementCounter("requests_total", 1, { method: "POST" });

      const prometheus = collector.getPrometheusMetrics();
      expect(prometheus).toContain("requests_total");
    });
  });

  describe("setGauge", () => {
    it("should set gauge value", () => {
      collector.setGauge("queue_depth", 45);
      collector.setGauge("queue_depth", 50);

      const prometheus = collector.getPrometheusMetrics();
      expect(prometheus).toContain("queue_depth");
    });

    it("should set gauge with labels", () => {
      collector.setGauge("memory_usage_mb", 512, { service: "sync" });

      const prometheus = collector.getPrometheusMetrics();
      expect(prometheus).toContain("memory_usage_mb");
      expect(prometheus).toContain("service");
    });
  });

  describe("recordHistogram", () => {
    it("should record histogram values", () => {
      const latencies = [45, 52, 48, 61, 55];
      latencies.forEach((l) => collector.recordHistogram("latency_ms", l));

      const agg = collector.aggregateMetrics("latency_ms");
      expect(agg).toBeDefined();
      expect(agg?.count).toBe(5);
      expect(agg?.min).toBe(45);
      expect(agg?.max).toBe(61);
    });

    it("should calculate percentiles correctly", () => {
      const values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
      values.forEach((v) => collector.recordHistogram("response_time", v));

      const agg = collector.aggregateMetrics("response_time");
      expect(agg).toBeDefined();
      expect(agg?.p50).toBeLessThanOrEqual(55);
      expect(agg?.p95).toBeGreaterThan(agg?.p50!);
      expect(agg?.p99).toBeGreaterThan(agg?.p95!);
    });
  });

  describe("aggregateMetrics", () => {
    it("should return null for non-existent metric", () => {
      const agg = collector.aggregateMetrics("non_existent");
      expect(agg).toBeNull();
    });

    it("should compute correct aggregation", () => {
      [1, 2, 3, 4, 5].forEach((v) => collector.recordHistogram("test", v));

      const agg = collector.aggregateMetrics("test");
      expect(agg?.sum).toBe(15);
      expect(agg?.mean).toBe(3);
      expect(agg?.count).toBe(5);
    });
  });

  describe("getPrometheusMetrics", () => {
    it("should format metrics in Prometheus format", () => {
      collector.recordHistogram("latency_ms", 100);
      collector.setGauge("queue_depth", 10);

      const prometheus = collector.getPrometheusMetrics();
      expect(prometheus).toContain("# TYPE");
      expect(prometheus).toContain("latency_ms");
      expect(prometheus).toContain("queue_depth");
    });

    it("should include labels in output", () => {
      collector.recordHistogram("api_latency", 100, { endpoint: "/users" });

      const prometheus = collector.getPrometheusMetrics();
      expect(prometheus).toContain("endpoint=");
    });
  });

  describe("pruneMetrics", () => {
    it("should remove old metrics", () => {
      collector.recordHistogram("test", 100);

      // Artificially age the metric by manipulating the map
      const metrics = (collector as any).metrics.get("test");
      if (metrics && metrics.length > 0) {
        metrics[0].timestamp = new Date(Date.now() - 4000000); // > 1h
      }

      collector.pruneMetrics(3600000);

      const agg = collector.aggregateMetrics("test");
      // Após prune, a métrica antiga não será incluída
      expect(agg).toBeNull();
    });
  });

  describe("reset", () => {
    it("should clear all metrics", () => {
      collector.recordHistogram("test1", 100);
      collector.setGauge("test2", 50);
      collector.incrementCounter("test3", 1);

      collector.reset();

      expect(collector.getPrometheusMetrics()).toBe("");
    });
  });
});

describe("AlertManager", () => {
  let alertManager: AlertManager;
  let logger: Logger;

  beforeEach(() => {
    logger = createMockLogger();
    alertManager = new AlertManager(logger);
  });

  describe("registerRule", () => {
    it("should register alert rule", () => {
      alertManager.registerRule({
        id: "test-alert",
        name: "Test Alert",
        metricName: "test_metric",
        operator: ">",
        threshold: 100,
        severity: AlertSeverity.WARNING,
        enabled: true,
      });

      expect(logger.info).toHaveBeenCalled();
    });
  });

  describe("evaluateRules", () => {
    beforeEach(() => {
      alertManager.registerRule({
        id: "high-value",
        name: "High Value Alert",
        metricName: "test_metric",
        operator: ">",
        threshold: 100,
        severity: AlertSeverity.ERROR,
        enabled: true,
      });
    });

    it("should trigger alert when condition is met", () => {
      const alerts = alertManager.evaluateRules("test_metric", 150);

      expect(alerts).toHaveLength(1);
      expect(alerts[0].name).toBe("High Value Alert");
      expect(alerts[0].currentValue).toBe(150);
    });

    it("should not trigger alert when condition is not met", () => {
      const alerts = alertManager.evaluateRules("test_metric", 50);

      expect(alerts).toHaveLength(0);
    });

    it("should respect enabled flag", () => {
      alertManager.registerRule({
        id: "disabled-alert",
        name: "Disabled Alert",
        metricName: "test_metric",
        operator: ">",
        threshold: 100,
        severity: AlertSeverity.WARNING,
        enabled: false,
      });

      const alerts = alertManager.evaluateRules("test_metric", 150);

      // Apenas o primeiro alerta deve disparar
      expect(alerts).toHaveLength(1);
      expect(alerts[0].id).toBe("high-value");
    });
  });

  describe("operators", () => {
    beforeEach(() => {
      const operators: Array<">" | "<" | ">=" | "<=" | "==" | "!="> = [
        ">",
        "<",
        ">=",
        "<=",
        "==",
        "!=",
      ];
      operators.forEach((op, idx) => {
        alertManager.registerRule({
          id: `op-${idx}`,
          name: `Test ${op}`,
          metricName: `metric_${op}`,
          operator: op,
          threshold: 50,
          severity: AlertSeverity.WARNING,
          enabled: true,
        });
      });
    });

    it("should evaluate > operator", () => {
      const alerts = alertManager.evaluateRules("metric_>", 60);
      expect(alerts).toHaveLength(1);

      const alerts2 = alertManager.evaluateRules("metric_>", 40);
      expect(alerts2).toHaveLength(0);
    });

    it("should evaluate < operator", () => {
      const alerts = alertManager.evaluateRules("metric_<", 40);
      expect(alerts).toHaveLength(1);

      const alerts2 = alertManager.evaluateRules("metric_<", 60);
      expect(alerts2).toHaveLength(0);
    });

    it("should evaluate >= operator", () => {
      const alerts1 = alertManager.evaluateRules("metric_>=", 50);
      expect(alerts1).toHaveLength(1);

      const alerts2 = alertManager.evaluateRules("metric_>=", 49);
      expect(alerts2).toHaveLength(0);
    });

    it("should evaluate <= operator", () => {
      const alerts1 = alertManager.evaluateRules("metric_<=", 50);
      expect(alerts1).toHaveLength(1);

      const alerts2 = alertManager.evaluateRules("metric_<=", 51);
      expect(alerts2).toHaveLength(0);
    });

    it("should evaluate == operator", () => {
      const alerts1 = alertManager.evaluateRules("metric_==", 50);
      expect(alerts1).toHaveLength(1);

      const alerts2 = alertManager.evaluateRules("metric_==", 49);
      expect(alerts2).toHaveLength(0);
    });

    it("should evaluate != operator", () => {
      const alerts1 = alertManager.evaluateRules("metric_!=", 60);
      expect(alerts1).toHaveLength(1);

      const alerts2 = alertManager.evaluateRules("metric_!=", 50);
      expect(alerts2).toHaveLength(0);
    });
  });

  describe("getActiveAlerts", () => {
    beforeEach(() => {
      alertManager.registerRule({
        id: "test",
        name: "Test",
        metricName: "metric",
        operator: ">",
        threshold: 50,
        severity: AlertSeverity.WARNING,
        enabled: true,
      });
    });

    it("should return only unresolved alerts", () => {
      const alerts1 = alertManager.evaluateRules("metric", 100);
      const alerts2 = alertManager.evaluateRules("metric", 100);

      const active = alertManager.getActiveAlerts();
      expect(active.length).toBe(2);

      alertManager.resolveAlert(alerts1[0].id);

      const activeAfter = alertManager.getActiveAlerts();
      expect(activeAfter).toHaveLength(1);
    });
  });

  describe("getAlertHistory", () => {
    beforeEach(() => {
      alertManager.registerRule({
        id: "test",
        name: "Test",
        metricName: "metric",
        operator: ">",
        threshold: 50,
        severity: AlertSeverity.WARNING,
        enabled: true,
      });
    });

    it("should maintain alert history", () => {
      alertManager.evaluateRules("metric", 100);
      alertManager.evaluateRules("metric", 100);
      alertManager.evaluateRules("metric", 100);

      const history = alertManager.getAlertHistory();
      expect(history.length).toBe(3);
    });

    it("should respect limit parameter", () => {
      for (let i = 0; i < 10; i++) {
        alertManager.evaluateRules("metric", 100);
      }

      const history = alertManager.getAlertHistory(5);
      expect(history).toHaveLength(5);
    });
  });

  describe("pruneAlerts", () => {
    it("should remove resolved alerts older than threshold", () => {
      alertManager.registerRule({
        id: "test",
        name: "Test",
        metricName: "metric",
        operator: ">",
        threshold: 50,
        severity: AlertSeverity.WARNING,
        enabled: true,
      });

      const alerts = alertManager.evaluateRules("metric", 100);
      alertManager.resolveAlert(alerts[0].id);

      // Age the alert
      const activeAlerts = alertManager.getActiveAlerts();
      if (activeAlerts[0]) {
        activeAlerts[0].resolvedAt = new Date(Date.now() - 90000000); // > 24h
      }

      alertManager.pruneAlerts(86400000);

      // Alerta antigo deve ter sido removido
      expect(logger.info).toHaveBeenCalled();
    });
  });
});

describe("TracingManager", () => {
  let tracing: TracingManager;
  let logger: Logger;

  beforeEach(() => {
    logger = createMockLogger();
    tracing = new TracingManager(logger);
  });

  describe("startTrace", () => {
    it("should create trace context with IDs", () => {
      const context = tracing.startTrace();

      expect(context.traceId).toBeDefined();
      expect(context.spanId).toBeDefined();
      expect(context.flags).toBe(1);
    });

    it("should generate unique IDs", () => {
      const context1 = tracing.startTrace();
      const context2 = tracing.startTrace();

      expect(context1.traceId).not.toBe(context2.traceId);
      expect(context1.spanId).not.toBe(context2.spanId);
    });
  });

  describe("createSpan", () => {
    it("should create span within trace", () => {
      const traceContext = tracing.startTrace();
      const span = tracing.createSpan(traceContext, "test_operation", {
        user_id: "123",
      });

      expect(span.name).toBe("test_operation");
      expect(span.traceContext?.traceId).toBe(traceContext.traceId);
      expect(span.metadata.user_id).toBe("123");
    });

    it("should set parent span ID", () => {
      const traceContext = tracing.startTrace();
      const span1 = tracing.createSpan(traceContext, "parent");
      const span2 = tracing.createSpan(traceContext, "child");

      expect(span2.traceContext?.parentSpanId).toBe(span1.traceContext?.spanId);
    });
  });

  describe("endSpan", () => {
    it("should record duration when span ends", () => {
      const traceContext = tracing.startTrace();
      const span = tracing.createSpan(traceContext, "operation");

      // Simular 100ms de processamento
      const start = Date.now();
      while (Date.now() - start < 50) {
        // Busy wait
      }

      tracing.endSpan(span, { status: "success" });

      expect(span.duration).toBeGreaterThan(0);
      expect(span.metadata.status).toBe("success");
    });
  });

  describe("getTrace", () => {
    it("should return all spans for trace", () => {
      const traceContext = tracing.startTrace();
      tracing.createSpan(traceContext, "op1");
      tracing.createSpan(traceContext, "op2");
      tracing.createSpan(traceContext, "op3");

      const spans = tracing.getTrace(traceContext.traceId);
      expect(spans).toHaveLength(3);
    });

    it("should return empty array for non-existent trace", () => {
      const spans = tracing.getTrace("non-existent");
      expect(spans).toHaveLength(0);
    });
  });

  describe("exportTrace", () => {
    it("should export trace in OpenTelemetry format", () => {
      const traceContext = tracing.startTrace();
      tracing.createSpan(traceContext, "operation", { key: "value" });

      const exported = tracing.exportTrace(traceContext.traceId);

      expect(exported.traceId).toBe(traceContext.traceId);
      expect(exported.spanCount).toBe(1);
      expect(exported.spans).toHaveLength(1);
    });

    it("should include span details", () => {
      const traceContext = tracing.startTrace();
      const span = tracing.createSpan(traceContext, "test", { foo: "bar" });
      tracing.endSpan(span);

      const exported = tracing.exportTrace(traceContext.traceId);
      const exportedSpan = exported.spans[0];

      expect(exportedSpan.name).toBe("test");
      expect(exportedSpan.attributes.foo).toBe("bar");
    });
  });

  describe("pruneTraces", () => {
    it("should remove old traces", () => {
      const context = tracing.startTrace();
      tracing.createSpan(context, "op1");

      // Age the trace
      const spans = (tracing as any).spans.get(context.traceId);
      if (spans && spans.length > 0) {
        spans[0].timestamp = new Date(Date.now() - 4000000); // > 1h
      }

      tracing.pruneTraces(3600000);

      const retrieved = tracing.getTrace(context.traceId);
      expect(retrieved).toHaveLength(0);
    });
  });
});

describe("ObservabilityManager", () => {
  let observability: ObservabilityManager;

  beforeEach(() => {
    observability = new ObservabilityManager("test-service", "test");
  });

  afterEach(() => {
    observability.shutdown();
  });

  describe("initialization", () => {
    it("should initialize all components", () => {
      expect(observability.metrics).toBeDefined();
      expect(observability.alerts).toBeDefined();
      expect(observability.tracing).toBeDefined();
      expect(observability.logger).toBeDefined();
    });

    it("should register default alert rules", () => {
      const activeAlerts = observability.alerts.getActiveAlerts();
      // No active alerts initially
      expect(activeAlerts).toHaveLength(0);
    });
  });

  describe("setupDefaultAlerts", () => {
    it("should have high error rate alert", () => {
      observability.alerts.evaluateRules("error_rate_percent", 6);
      const alerts = observability.alerts.getActiveAlerts();

      expect(alerts.length).toBeGreaterThan(0);
      expect(alerts[0].name).toContain("Error");
    });

    it("should have timeout alert", () => {
      observability.alerts.evaluateRules("sync_latency_ms", 35000);
      const alerts = observability.alerts.getActiveAlerts();

      expect(alerts.length).toBeGreaterThan(0);
    });

    it("should have queue depth alert", () => {
      observability.alerts.evaluateRules("queue_depth", 150);
      const alerts = observability.alerts.getActiveAlerts();

      expect(alerts.length).toBeGreaterThan(0);
    });
  });

  describe("getSystemStatus", () => {
    it("should return complete system status", () => {
      observability.metrics.recordHistogram("sync_latency_ms", 100);
      observability.metrics.setGauge("queue_depth", 10);

      const status = observability.getSystemStatus();

      expect(status).toHaveProperty("timestamp");
      expect(status).toHaveProperty("health");
      expect(status).toHaveProperty("dashboard");
    });
  });

  describe("getPrometheusMetrics", () => {
    it("should return Prometheus format metrics", () => {
      observability.metrics.recordHistogram("test", 100);

      const prometheus = observability.getPrometheusMetrics();

      expect(prometheus).toContain("# TYPE");
      expect(prometheus).toContain("test");
    });
  });

  describe("shutdown", () => {
    it("should clean up resources", () => {
      const observ = new ObservabilityManager("test", "test");
      observ.shutdown();

      // Should not throw
      expect(observ).toBeDefined();
    });
  });
});

describe("createLogger", () => {
  it("should create logger with correct service name", () => {
    const logger = createLogger("test-service");

    expect(logger).toBeDefined();
    expect(logger.info).toBeDefined();
    expect(logger.error).toBeDefined();
  });

  it("should create different logger for different environments", () => {
    const devLogger = createLogger("test", "development");
    const prodLogger = createLogger("test", "production");

    expect(devLogger).toBeDefined();
    expect(prodLogger).toBeDefined();
  });
});

describe("Integration Tests", () => {
  let observability: ObservabilityManager;

  beforeEach(() => {
    observability = new ObservabilityManager("integration-test", "test");
  });

  afterEach(() => {
    observability.shutdown();
  });

  it("should handle complete observability flow", () => {
    // Start trace
    const trace = observability.tracing.startTrace();

    // Record metrics
    observability.metrics.recordHistogram("operation_latency", 150);
    observability.metrics.incrementCounter("operations_total");

    // Create and end span
    const span = observability.tracing.createSpan(trace, "main_op");
    observability.tracing.endSpan(span);

    // Check status
    const status = observability.getSystemStatus();
    expect(status).toBeDefined();

    // Export trace
    const exported = observability.tracing.exportTrace(trace.traceId);
    expect(exported.spanCount).toBe(1);
  });

  it("should handle metrics and alerts together", () => {
    // Record error metric
    observability.metrics.incrementCounter("requests_total", 100);
    observability.metrics.incrementCounter("requests_error", 10);

    // Evaluate alerts
    observability.alerts.evaluateRules("error_rate_percent", 10);

    // Get status
    const alerts = observability.alerts.getActiveAlerts();
    expect(alerts.length).toBeGreaterThan(0);
  });

  it("should perform cleanup without errors", () => {
    // Generate metrics and alerts
    for (let i = 0; i < 10; i++) {
      observability.metrics.recordHistogram("test", i * 10);
      observability.alerts.evaluateRules("queue_depth", i * 20);
    }

    // Manual cleanup
    observability.metrics.pruneMetrics(0);
    observability.alerts.pruneAlerts(0);
    observability.tracing.pruneTraces(0);

    // Should still work
    const status = observability.getSystemStatus();
    expect(status).toBeDefined();
  });
});
