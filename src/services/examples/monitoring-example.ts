/**
 * Exemplo de uso: Monitoring & Observability Service
 *
 * Demonstra:
 * - Coleta de métricas Prometheus
 * - Logging estruturado
 * - Rastreamento distribuído
 * - Gerenciamento de alertas com Slack
 * - Dashboard queries
 */

import {
  ObservabilityManager,
  AlertSeverity,
  MetricType,
  createObservabilityMiddleware,
} from "../monitoring";

/**
 * Exemplo 1: Inicializar o gerenciador de observabilidade
 */
function example1_initialization() {
  const observability = new ObservabilityManager("sync-service", "production");

  // Registrar alerta customizado com webhook Slack
  observability.alerts.registerRule({
    id: "custom-alert-1",
    name: "Database Connection Pool Exhausted",
    metricName: "db_pool_connections",
    operator: ">=",
    threshold: 95,
    severity: AlertSeverity.CRITICAL,
    enabled: true,
    slackWebhook: process.env.SLACK_WEBHOOK_URL,
    channels: ["#alerts", "#devops"],
  });

  console.log("✅ Observability manager initialized");
  return observability;
}

/**
 * Exemplo 2: Registrar métricas de performance
 */
function example2_recordMetrics(observability: ObservabilityManager) {
  // Simular requisições HTTP e registrar latência
  const latencies = [45, 52, 48, 61, 55, 49, 70, 44, 58, 51];

  latencies.forEach((latency) => {
    observability.metrics.recordHistogram("sync_latency_ms", latency, {
      endpoint: "/sync",
      service: "github",
    });
  });

  // Simular taxa de sucesso
  observability.metrics.incrementCounter("requests_total", latencies.length);
  observability.metrics.incrementCounter(
    "requests_success",
    latencies.length - 1
  ); // 1 erro
  observability.metrics.incrementCounter("requests_error", 1);

  // Registrar profundidade de fila
  observability.metrics.setGauge("queue_depth", 45, {
    service: "sync-queue",
  });

  // Registrar uso de CPU
  observability.metrics.setGauge("cpu_usage_percent", 62.5);

  // Registrar conexões de BD
  observability.metrics.setGauge("db_pool_connections", 92);

  console.log("✅ Metrics recorded");
}

/**
 * Exemplo 3: Avaliação de alertas
 */
function example3_evaluateAlerts(observability: ObservabilityManager) {
  // Simular aumento de latência que dispara alerta
  console.log("\n--- Triggering timeout alert ---");
  const alerts1 = observability.alerts.evaluateRules("sync_latency_ms", 35000); // > 30s threshold
  console.log(`Alerts triggered: ${alerts1.length}`);
  if (alerts1.length > 0) {
    console.log(alerts1[0].message);
  }

  // Simular queue depth alto
  console.log("\n--- Triggering stale sync alert ---");
  const alerts2 = observability.alerts.evaluateRules("queue_depth", 150); // > 100 threshold
  console.log(`Alerts triggered: ${alerts2.length}`);
  if (alerts2.length > 0) {
    console.log(alerts2[0].message);
  }

  // Simular error rate alto
  console.log("\n--- Triggering high error rate alert ---");
  observability.metrics.incrementCounter("requests_total", 100);
  observability.metrics.incrementCounter("requests_error", 10);
  const errorRate = (10 / 100) * 100; // 10%
  const alerts3 = observability.alerts.evaluateRules(
    "error_rate_percent",
    errorRate
  );
  console.log(`Alerts triggered: ${alerts3.length}`);
  if (alerts3.length > 0) {
    console.log(alerts3[0].message);
  }
}

/**
 * Exemplo 4: Rastreamento distribuído
 */
function example4_distributedTracing(observability: ObservabilityManager) {
  console.log("\n--- Distributed Tracing Example ---");

  // Inicia novo rastreamento
  const traceContext = observability.tracing.startTrace();
  console.log(`Trace ID: ${traceContext.traceId}`);

  // Cria spans dentro do rastreamento
  const span1 = observability.tracing.createSpan(traceContext, "fetch_pr_metadata", {
    repository: "anthropic/claude-code",
    pr_number: 1234,
  });

  // Simula work
  setTimeout(() => {
    observability.tracing.endSpan(span1, {
      status: "success",
      data_fetched: true,
    });
  }, 100);

  // Cria outro span
  const span2 = observability.tracing.createSpan(traceContext, "run_code_review", {
    model: "claude-opus",
    file_count: 15,
  });

  setTimeout(() => {
    observability.tracing.endSpan(span2, {
      status: "success",
      issues_found: 3,
    });

    // Exporta rastreamento completo
    const trace = observability.tracing.exportTrace(traceContext.traceId);
    console.log("Trace exported (OpenTelemetry compatible):");
    console.log(JSON.stringify(trace, null, 2));
  }, 200);
}

/**
 * Exemplo 5: Prometheus metrics export
 */
function example5_prometheusExport(observability: ObservabilityManager) {
  console.log("\n--- Prometheus Metrics Export ---");
  const prometheusMetrics = observability.getPrometheusMetrics();
  console.log("Sample Prometheus output:");
  console.log(prometheusMetrics.split("\n").slice(0, 15).join("\n"));
  console.log("... (truncated)");
}

/**
 * Exemplo 6: Dashboard data
 */
function example6_dashboardData(observability: ObservabilityManager) {
  console.log("\n--- Dashboard Data ---");
  const keyMetrics = observability.metrics.getKeyMetrics();
  console.log("Key Metrics:");
  console.log(JSON.stringify(keyMetrics, null, 2));

  const systemStatus = observability.getSystemStatus();
  console.log("\nFull System Status:");
  console.log(JSON.stringify(systemStatus, null, 2));
}

/**
 * Exemplo 7: Logging estruturado
 */
function example7_structuredLogging(observability: ObservabilityManager) {
  console.log("\n--- Structured Logging ---");

  observability.logger.info(
    {
      action: "sync_started",
      service: "github",
      repository: "anthropic/claude-code",
    },
    "GitHub sync initiated"
  );

  observability.logger.warn(
    {
      action: "rate_limit_warning",
      remaining: 45,
      resetAt: new Date(Date.now() + 3600000),
    },
    "GitHub API rate limit warning"
  );

  observability.logger.error(
    {
      action: "sync_failed",
      error: "Connection timeout",
      retryCount: 3,
    },
    "GitHub sync failed after retries"
  );
}

/**
 * Exemplo 8: Limpeza e shutdown
 */
function example8_cleanup(observability: ObservabilityManager) {
  console.log("\n--- Cleanup & Shutdown ---");

  // Prune métricas antigas
  observability.metrics.pruneMetrics(3600000); // Remover métricas > 1h
  console.log("✅ Old metrics pruned");

  // Prune alertas resolvidos antigos
  observability.alerts.pruneAlerts(86400000); // Remover alertas resolvidos > 24h
  console.log("✅ Old resolved alerts pruned");

  // Shutdown limpo
  observability.shutdown();
  console.log("✅ Observability manager shut down");
}

/**
 * Exemplo 9: Express middleware integration
 */
function example9_expressMiddleware(observability: ObservabilityManager) {
  console.log("\n--- Express Middleware Example ---");

  // Aplicar middleware em Express app
  // app.use(createObservabilityMiddleware(observability));

  // Este middleware irá:
  // - Criar trace para cada requisição
  // - Registrar latência HTTP
  // - Rastrear sucesso/erro
  // - Adicionar headers de trace

  const middleware = createObservabilityMiddleware(observability);
  console.log("✅ Middleware criado e pronto para Express");
}

/**
 * Exemplo 10: Métricas customizadas para negócio
 */
function example10_businessMetrics(observability: ObservabilityManager) {
  console.log("\n--- Business Metrics ---");

  // Registrar métricas de negócio
  observability.metrics.incrementCounter("sync_operations_completed", 1, {
    type: "github",
    status: "success",
  });

  observability.metrics.incrementCounter("pr_reviews_created", 1, {
    reviewer: "claude-opus",
    files_reviewed: "15",
  });

  observability.metrics.recordHistogram("review_time_seconds", 45, {
    complexity: "high",
  });

  // Registrar conversão/goals
  observability.metrics.incrementCounter("agent_deployments", 1, {
    agent: "code-reviewer",
    version: "2.1.0",
  });

  const customMetrics = observability.metrics.getKeyMetrics();
  console.log("Custom business metrics captured:");
  console.log(customMetrics);
}

/**
 * Exemplo 11: Alert history and replay
 */
function example11_alertHistory(observability: ObservabilityManager) {
  console.log("\n--- Alert History ---");

  // Simular múltiplos alertas
  observability.alerts.evaluateRules("sync_latency_ms", 35000);
  observability.alerts.evaluateRules("queue_depth", 150);

  // Buscar histórico
  const history = observability.alerts.getAlertHistory(10);
  console.log(`Alert history (last 10):`);
  history.forEach((alert) => {
    console.log(`- [${alert.severity}] ${alert.name}: ${alert.message}`);
  });

  // Resolver o primeiro alerta
  if (history.length > 0) {
    observability.alerts.resolveAlert(history[0].id);
    console.log(`Alert ${history[0].id} resolved`);
  }
}

/**
 * Exemplo 12: Aggregations e percentis
 */
function example12_aggregations(observability: ObservabilityManager) {
  console.log("\n--- Metric Aggregations ---");

  // Simular múltiplas observações de latência
  const latencies = [
    45, 52, 48, 61, 55, 49, 70, 44, 58, 51, 53, 47, 62, 54, 50, 59, 46, 63,
    55, 57,
  ];

  latencies.forEach((latency) => {
    observability.metrics.recordHistogram("api_latency_ms", latency);
  });

  // Computar agregações
  const agg = observability.metrics.aggregateMetrics("api_latency_ms");
  if (agg) {
    console.log(`Latency aggregations:`);
    console.log(`  Count: ${agg.count}`);
    console.log(`  Min: ${agg.min.toFixed(2)}ms`);
    console.log(`  Max: ${agg.max.toFixed(2)}ms`);
    console.log(`  Mean: ${agg.mean.toFixed(2)}ms`);
    console.log(`  P50: ${agg.p50.toFixed(2)}ms`);
    console.log(`  P95: ${agg.p95.toFixed(2)}ms`);
    console.log(`  P99: ${agg.p99.toFixed(2)}ms`);
  }
}

/**
 * Main: Execute todos os exemplos
 */
async function main() {
  console.log("=".repeat(60));
  console.log("Monitoring & Observability Service - Examples");
  console.log("=".repeat(60));

  const observability = example1_initialization();

  example2_recordMetrics(observability);
  example3_evaluateAlerts(observability);
  example4_distributedTracing(observability);

  // Aguardar spans terminarem
  await new Promise((resolve) => setTimeout(resolve, 300));

  example5_prometheusExport(observability);
  example6_dashboardData(observability);
  example7_structuredLogging(observability);
  example9_expressMiddleware(observability);
  example10_businessMetrics(observability);
  example11_alertHistory(observability);
  example12_aggregations(observability);
  example8_cleanup(observability);

  console.log("\n" + "=".repeat(60));
  console.log("Examples completed!");
  console.log("=".repeat(60));
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export {
  example1_initialization,
  example2_recordMetrics,
  example3_evaluateAlerts,
  example4_distributedTracing,
  example5_prometheusExport,
  example6_dashboardData,
  example7_structuredLogging,
  example8_cleanup,
  example9_expressMiddleware,
  example10_businessMetrics,
  example11_alertHistory,
  example12_aggregations,
};
