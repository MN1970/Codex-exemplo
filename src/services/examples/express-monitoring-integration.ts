/**
 * Exemplo: Express Server com Monitoring & Observability
 *
 * Demonstra integração completa do monitoring service em um servidor Express:
 * - Middleware de observabilidade
 * - Endpoints de métricas
 * - Health checks
 * - Alertas automáticos
 */

import express, { Express, Request, Response, NextFunction } from "express";
import {
  ObservabilityManager,
  createObservabilityMiddleware,
} from "../monitoring";

/**
 * Tipo para requisição com contexto de rastreamento
 */
interface TracedRequest extends Request {
  traceId?: string;
  spanId?: string;
}

/**
 * Factory para criar servidor Express com observabilidade
 */
export function createObservableServer(
  serviceName: string = "api-server"
): {
  app: Express;
  observability: ObservabilityManager;
  start: (port: number) => Promise<void>;
  shutdown: () => Promise<void>;
} {
  const app = express();
  const observability = new ObservabilityManager(serviceName, "production");

  // Middleware de observabilidade global
  app.use(createObservabilityMiddleware(observability));

  // Middleware para parsear JSON
  app.use(express.json());

  // Middleware para logging de requisições
  app.use((req: TracedRequest, res: Response, next: NextFunction) => {
    const startTime = Date.now();

    observability.logger.info(
      {
        method: req.method,
        path: req.path,
        headers: req.headers,
      },
      "Incoming request"
    );

    // Interceptar response
    const originalJson = res.json;
    res.json = function (data) {
      const duration = Date.now() - startTime;
      observability.logger.info(
        {
          method: req.method,
          path: req.path,
          statusCode: res.statusCode,
          duration,
        },
        "Response sent"
      );
      return originalJson.call(this, data);
    };

    next();
  });

  /**
   * Health Check - usado para Kubernetes liveness probes
   */
  app.get("/health", (req: Request, res: Response) => {
    const status = observability.getSystemStatus();

    const activeAlerts = (status as any).health.alerts.active;
    const isHealthy = activeAlerts === 0;

    res.status(isHealthy ? 200 : 503).json({
      status: isHealthy ? "healthy" : "degraded",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      activeAlerts,
    });
  });

  /**
   * Readiness Check - usado para Kubernetes readiness probes
   */
  app.get("/ready", (req: Request, res: Response) => {
    // Verificar se o serviço está pronto para receber tráfego
    const metrics = observability.metrics.getKeyMetrics();
    const isReady = true; // Personalizar conforme necessário

    res.status(isReady ? 200 : 503).json({
      ready: isReady,
      timestamp: new Date().toISOString(),
    });
  });

  /**
   * Prometheus metrics endpoint
   */
  app.get("/metrics", (req: Request, res: Response) => {
    res.type("text/plain");
    const prometheusMetrics = observability.getPrometheusMetrics();
    res.send(prometheusMetrics);
  });

  /**
   * System status endpoint (JSON)
   */
  app.get("/system-status", (req: Request, res: Response) => {
    const status = observability.getSystemStatus();
    res.json(status);
  });

  /**
   * Alert history endpoint
   */
  app.get("/alerts/history", (req: Request, res: Response) => {
    const limit = parseInt(req.query.limit as string) || 100;
    const history = observability.alerts.getAlertHistory(limit);

    res.json({
      count: history.length,
      alerts: history,
      timestamp: new Date().toISOString(),
    });
  });

  /**
   * Alertas ativos
   */
  app.get("/alerts/active", (req: Request, res: Response) => {
    const activeAlerts = observability.alerts.getActiveAlerts();

    res.json({
      count: activeAlerts.length,
      alerts: activeAlerts,
      timestamp: new Date().toISOString(),
    });
  });

  /**
   * Exemplo: Endpoint de sincronização GitHub
   * Demonstra rastreamento distribuído completo
   */
  app.post("/api/sync/github", async (req: TracedRequest, res: Response) => {
    const trace = observability.tracing.startTrace();
    res.set("X-Trace-ID", trace.traceId);

    try {
      // Span 1: Fetch PRs from GitHub
      const span1 = observability.tracing.createSpan(trace, "fetch_prs", {
        repository: req.body.repository,
      });

      // Simular busca de PRs
      await new Promise((resolve) => setTimeout(resolve, 100));
      observability.tracing.endSpan(span1, {
        pr_count: 5,
        status: "success",
      });

      // Span 2: Process PRs
      const span2 = observability.tracing.createSpan(trace, "process_prs", {
        count: 5,
      });

      // Simular processamento
      await new Promise((resolve) => setTimeout(resolve, 200));
      observability.tracing.endSpan(span2, {
        processed: 5,
        errors: 0,
      });

      // Registrar sucesso
      observability.metrics.incrementCounter("sync_operations", 1, {
        type: "github",
        status: "success",
      });

      res.json({
        success: true,
        traceId: trace.traceId,
        message: "GitHub sync completed",
      });
    } catch (error) {
      observability.metrics.incrementCounter("sync_operations", 1, {
        type: "github",
        status: "error",
      });

      observability.logger.error(
        {
          error: error instanceof Error ? error.message : String(error),
          traceId: trace.traceId,
        },
        "GitHub sync failed"
      );

      res.status(500).json({
        success: false,
        traceId: trace.traceId,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  });

  /**
   * Exemplo: Endpoint de análise de código
   */
  app.post("/api/review/code", async (req: TracedRequest, res: Response) => {
    const startTime = Date.now();
    const trace = observability.tracing.startTrace();

    try {
      // Registrar início
      observability.metrics.incrementCounter("code_reviews_started");

      // Span: Análise
      const span = observability.tracing.createSpan(trace, "analyze_code", {
        files: req.body.files?.length || 0,
        model: req.body.model || "claude-opus",
      });

      // Simular análise
      await new Promise((resolve) => setTimeout(resolve, 150));

      observability.tracing.endSpan(span, {
        issues_found: 3,
        status: "complete",
      });

      const duration = Date.now() - startTime;

      // Registrar métrica
      observability.metrics.recordHistogram("code_review_duration_ms", duration, {
        model: req.body.model,
      });

      observability.metrics.incrementCounter("code_reviews_completed");

      res.json({
        traceId: trace.traceId,
        duration,
        issues_found: 3,
      });
    } catch (error) {
      observability.logger.error(
        { error, traceId: trace.traceId },
        "Code review failed"
      );

      res.status(500).json({
        error: "Code review failed",
        traceId: trace.traceId,
      });
    }
  });

  /**
   * Exemplo: Endpoint que simula queue
   */
  app.post("/api/queue/job", async (req: Request, res: Response) => {
    try {
      const queueSize = Math.floor(Math.random() * 200);

      // Registrar profundidade da fila
      observability.metrics.setGauge("queue_depth", queueSize, {
        queue_type: "sync",
      });

      // Se fila está profunda, pode disparar alerta
      observability.alerts.evaluateRules("queue_depth", queueSize);

      res.json({
        jobId: "job_" + Date.now(),
        queuePosition: queueSize,
        estimatedWaitMs: queueSize * 500,
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to queue job" });
    }
  });

  /**
   * Exemplo: Simular erros para testar alertas
   */
  app.post("/api/test/error-spike", (req: Request, res: Response) => {
    // Simular spike de erros
    const errorCount = req.body.count || 20;
    const totalCount = 100;

    for (let i = 0; i < errorCount; i++) {
      observability.metrics.incrementCounter("requests_error");
    }
    for (let i = 0; i < totalCount - errorCount; i++) {
      observability.metrics.incrementCounter("requests_success");
    }
    observability.metrics.incrementCounter("requests_total", totalCount);

    const errorRate = (errorCount / totalCount) * 100;
    observability.alerts.evaluateRules("error_rate_percent", errorRate);

    res.json({
      message: "Error spike simulated",
      errorRate: errorRate.toFixed(2) + "%",
      activeAlerts: observability.alerts.getActiveAlerts().length,
    });
  });

  /**
   * Exemplo: Simular latência alta
   */
  app.post("/api/test/high-latency", (req: Request, res: Response) => {
    const latency = req.body.latency || 40000; // 40 segundos

    observability.metrics.recordHistogram("sync_latency_ms", latency);
    observability.alerts.evaluateRules("sync_latency_ms", latency);

    res.json({
      message: "High latency recorded",
      latency,
      activeAlerts: observability.alerts.getActiveAlerts().length,
    });
  });

  /**
   * 404 handler
   */
  app.use((req: Request, res: Response) => {
    res.status(404).json({
      error: "Not Found",
      path: req.path,
      method: req.method,
    });
  });

  /**
   * Error handler
   */
  app.use(
    (
      error: Error,
      req: Request,
      res: Response,
      next: NextFunction
    ) => {
      observability.logger.error(
        { error: error.message, path: req.path },
        "Unhandled error"
      );

      res.status(500).json({
        error: "Internal Server Error",
        message:
          process.env.NODE_ENV === "development"
            ? error.message
            : "An error occurred",
      });
    }
  );

  /**
   * Função para iniciar servidor
   */
  async function start(port: number = 3000): Promise<void> {
    return new Promise((resolve) => {
      const server = app.listen(port, () => {
        observability.logger.info(
          { port },
          `Server listening on port ${port}`
        );
        resolve();
      });

      // Graceful shutdown
      process.on("SIGTERM", async () => {
        observability.logger.info("SIGTERM received, shutting down gracefully");
        server.close(() => {
          observability.shutdown();
          process.exit(0);
        });
      });
    });
  }

  /**
   * Função para shutdown
   */
  async function shutdown(): Promise<void> {
    observability.shutdown();
  }

  return {
    app,
    observability,
    start,
    shutdown,
  };
}

/**
 * Exemplo de uso
 */
async function main() {
  const { app, observability, start } = createObservableServer("example-api");

  try {
    await start(3000);
    console.log("✅ Server started with observability");

    // Simular alguns eventos
    setTimeout(() => {
      observability.metrics.recordHistogram("api_latency", 150);
      observability.metrics.incrementCounter("requests_total");
      observability.metrics.incrementCounter("requests_success");

      console.log("✅ Sample metrics recorded");
      console.log("📊 Check metrics at http://localhost:3000/metrics");
      console.log("❤️  Check health at http://localhost:3000/health");
      console.log("📈 Check status at http://localhost:3000/system-status");
    }, 1000);
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
}

// Executar se for o arquivo principal
if (require.main === module) {
  main().catch(console.error);
}

export {
  createObservableServer,
  main,
};
