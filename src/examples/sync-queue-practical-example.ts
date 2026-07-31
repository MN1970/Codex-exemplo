/**
 * Sync Queue Manager — Exemplo Prático
 *
 * Cenário: Sistema de sincronização de Agents Manta
 * - Quando um agent é atualizado, precisa sincronizar em múltiplas fontes
 * - Prioridades diferentes para tipos diferentes
 * - Retry automático com backoff
 * - Observabilidade em tempo real
 */

import {
  SyncQueueManager,
  QueuePriority,
  runSyncQueueExamples,
} from "../services/sync-queue";

/**
 * Payload de sincronização de Agent
 */
export interface AgentSyncPayload {
  agentId: string;
  agentCode: string;
  agentName: string;
  action: "created" | "updated" | "deployed" | "deprecated";
  timestamp: string;
  changes?: {
    field: string;
    oldValue: unknown;
    newValue: unknown;
  }[];
}

/**
 * Serviço de sincronização de Agents
 */
export class AgentSyncService {
  private queue: SyncQueueManager<AgentSyncPayload>;
  private syncTargets = {
    registry: false,      // Agent registry em Supabase
    maestro: false,       // Maestro router
    documentation: false, // Documentação
    cache: false,         // Cache distribuído
  };

  constructor() {
    this.queue = new SyncQueueManager<AgentSyncPayload>({
      maxBatchSize: 10,
      processingIntervalMs: 5000,
      retryPolicy: {
        maxRetries: 3,
        initialDelayMs: 500,
        maxDelayMs: 10000,
        backoffMultiplier: 2,
      },
    });

    this.setupProcessing();
    console.log("✅ AgentSyncService initialized");
  }

  /**
   * Configura callback de processamento
   */
  private setupProcessing(): void {
    this.queue.onProcess(async (item) => {
      const payload = item.data;
      console.log(
        `🔄 Syncing agent ${payload.agentCode} (${payload.action})`
      );

      try {
        // Sincroniza em paralelo para múltiplos destinos
        await Promise.all([
          this.syncToRegistry(payload),
          this.syncToMaestro(payload),
          this.syncDocumentation(payload),
          this.updateCache(payload),
        ]);

        console.log(
          `✅ Agent ${payload.agentCode} synced successfully across all targets`
        );
      } catch (error) {
        console.error(`❌ Sync failed for ${payload.agentCode}:`, error);
        throw error; // Manager vai fazer retry
      }
    });
  }

  /**
   * Sincroniza com agent registry
   */
  private async syncToRegistry(payload: AgentSyncPayload): Promise<void> {
    console.log(`  📚 Updating agent registry for ${payload.agentCode}`);
    // Simula chamada a Supabase
    await new Promise((resolve) => setTimeout(resolve, 200));
    this.syncTargets.registry = true;
  }

  /**
   * Sincroniza com Maestro router
   */
  private async syncToMaestro(payload: AgentSyncPayload): Promise<void> {
    console.log(`  🔀 Updating Maestro router for ${payload.agentCode}`);
    // Simula chamada a API do Maestro
    await new Promise((resolve) => setTimeout(resolve, 300));
    this.syncTargets.maestro = true;
  }

  /**
   * Sincroniza documentação
   */
  private async syncDocumentation(payload: AgentSyncPayload): Promise<void> {
    console.log(`  📖 Updating documentation for ${payload.agentCode}`);
    // Simula atualização de docs
    await new Promise((resolve) => setTimeout(resolve, 150));
    this.syncTargets.documentation = true;
  }

  /**
   * Atualiza cache distribuído
   */
  private async updateCache(payload: AgentSyncPayload): Promise<void> {
    console.log(`  💾 Invalidating cache for ${payload.agentCode}`);
    // Simula atualização de cache
    await new Promise((resolve) => setTimeout(resolve, 100));
    this.syncTargets.cache = true;
  }

  /**
   * Registra atualização de agent
   */
  public async onAgentUpdated(
    agentId: string,
    agentCode: string,
    agentName: string,
    action: AgentSyncPayload["action"],
    changes?: AgentSyncPayload["changes"]
  ): Promise<boolean> {
    // Determina prioridade baseada no tipo de agent
    const priority = this.getPriorityForAgent(agentCode);

    const payload: AgentSyncPayload = {
      agentId,
      agentCode,
      agentName,
      action,
      timestamp: new Date().toISOString(),
      changes,
    };

    const success = await this.queue.enqueue(payload, priority, {
      source: "agent-update",
      tags: [agentCode, action],
      correlationId: agentId,
    });

    if (success) {
      console.log(`📥 Sync task queued for ${agentCode}`);
    } else {
      console.log(
        `⚠️ Duplicate sync task detected for ${agentCode} - skipping`
      );
    }

    return success;
  }

  /**
   * Determina prioridade baseada no agent
   */
  private getPriorityForAgent(agentCode: string): QueuePriority {
    // Agents críticos (Maestro, horizontais)
    if (
      agentCode.startsWith("Manta 00") ||
      agentCode.startsWith("Manta 01") ||
      agentCode.startsWith("Manta 02")
    ) {
      return QueuePriority.CRITICAL;
    }

    // Agents de alta prioridade (S8 - Saneamento, S9 - Energia)
    if (
      agentCode.includes("S8") ||
      agentCode.includes("S9") ||
      agentCode.includes("saneamento") ||
      agentCode.includes("energia")
    ) {
      return QueuePriority.HIGH;
    }

    // Agents de prioridade média
    if (
      agentCode.includes("S1") ||
      agentCode.includes("S2") ||
      agentCode.includes("S3") ||
      agentCode.includes("S4")
    ) {
      return QueuePriority.MEDIUM;
    }

    // Padrão: low priority
    return QueuePriority.LOW;
  }

  /**
   * Inicia sincronização contínua
   */
  public start(): void {
    this.queue.startProcessing();
    console.log("▶️ Agent sync service started");
  }

  /**
   * Para sincronização
   */
  public stop(): void {
    this.queue.stopProcessing();
    console.log("⏹️ Agent sync service stopped");
  }

  /**
   * Retorna status da sincronização
   */
  public getStatus() {
    const metrics = this.queue.getMetrics();
    return {
      queueSize: metrics.queueSize,
      deadLetterSize: metrics.deadLetterSize,
      totalProcessed: metrics.totalProcessed,
      failureRate: metrics.failureRate,
      avgLatencyMs: metrics.averageLatencyMs,
      syncTargets: this.syncTargets,
    };
  }

  /**
   * Retorna métricas para dashboard
   */
  public getMetrics() {
    return this.queue.getMetrics();
  }

  /**
   * Retorna Prometheus metrics
   */
  public getPrometheusMetrics(): string {
    return this.queue.getPrometheusMetrics();
  }

  /**
   * Cleanup
   */
  public destroy(): void {
    this.queue.destroy();
    console.log("🧹 AgentSyncService destroyed");
  }
}

/**
 * Exemplo de uso prático
 */
export async function runPracticalExample(): Promise<void> {
  console.log("\n=== AGENT SYNC SERVICE PRACTICAL EXAMPLE ===\n");

  const service = new AgentSyncService();
  service.start();

  // Simula atualizações de agents em tempos diferentes
  console.log("📝 Simulating agent updates...\n");

  // Atualização crítica: Maestro router
  await service.onAgentUpdated(
    "agent_manta_00",
    "Manta 00",
    "maestro",
    "updated",
    [
      {
        field: "routingRules",
        oldValue: "v3.1",
        newValue: "v4.2",
      },
    ]
  );

  // Aguarda um pouco
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Atualização alta prioridade: Agent Saneamento
  await service.onAgentUpdated(
    "agent_s8_001",
    "Manta 03-S8",
    "agente-saneamento",
    "created",
    [
      {
        field: "keywords",
        oldValue: "[]",
        newValue: "[ETA, ETE, adutora, SNIS]",
      },
    ]
  );

  // Aguarda um pouco
  await new Promise((resolve) => setTimeout(resolve, 500));

  // Atualização média prioridade: Agent Rodovia
  await service.onAgentUpdated(
    "agent_s1_005",
    "Manta 03-S1",
    "agente-infraestrutura",
    "updated"
  );

  // Tenta duplicate
  console.log("\n🔄 Testing idempotency...");
  const duplicate = await service.onAgentUpdated(
    "agent_s8_001",
    "Manta 03-S8",
    "agente-saneamento",
    "created",
    [
      {
        field: "keywords",
        oldValue: "[]",
        newValue: "[ETA, ETE, adutora, SNIS]",
      },
    ]
  );
  console.log(`Duplicate result: ${duplicate}\n`);

  // Aguarda processamento
  console.log("⏳ Waiting for sync tasks to complete...\n");
  await new Promise((resolve) => setTimeout(resolve, 8000));

  // Mostra status
  console.log("\n📊 Sync Service Status:");
  const status = service.getStatus();
  console.log(`   Queue size: ${status.queueSize}`);
  console.log(`   Dead letter: ${status.deadLetterSize}`);
  console.log(`   Total processed: ${status.totalProcessed}`);
  console.log(`   Failure rate: ${status.failureRate.toFixed(1)}%`);
  console.log(`   Avg latency: ${status.avgLatencyMs.toFixed(0)}ms`);

  console.log("\n🎯 Sync Targets Status:");
  console.log(`   Registry: ${status.syncTargets.registry ? "✅" : "❌"}`);
  console.log(`   Maestro: ${status.syncTargets.maestro ? "✅" : "❌"}`);
  console.log(
    `   Documentation: ${status.syncTargets.documentation ? "✅" : "❌"}`
  );
  console.log(`   Cache: ${status.syncTargets.cache ? "✅" : "❌"}`);

  // Mostra métricas completas
  console.log("\n📈 Detailed Metrics:");
  const metrics = service.getMetrics();
  console.log(`   By Priority:`);
  console.log(
    `     CRITICAL: ${metrics.byPriority[0].queued} queued, ${metrics.byPriority[0].processed} processed`
  );
  console.log(
    `     HIGH: ${metrics.byPriority[1].queued} queued, ${metrics.byPriority[1].processed} processed`
  );
  console.log(
    `     MEDIUM: ${metrics.byPriority[2].queued} queued, ${metrics.byPriority[2].processed} processed`
  );
  console.log(
    `     LOW: ${metrics.byPriority[3].queued} queued, ${metrics.byPriority[3].processed} processed`
  );

  // Mostra Prometheus metrics (sample)
  console.log("\n📡 Prometheus Metrics (sample):");
  const prometheusMetrics = service.getPrometheusMetrics();
  const lines = prometheusMetrics.split("\n");
  for (const line of lines.slice(0, 15)) {
    console.log(`   ${line}`);
  }
  console.log("   ...");

  // Cleanup
  service.stop();
  service.destroy();

  console.log("\n✅ Practical example completed!");
}

/**
 * Exemplo avançado: REST API com Express
 */
export function setupAgentSyncAPI(app: any): void {
  const service = new AgentSyncService();
  service.start();

  /**
   * POST /api/agents/:agentId/sync
   * Registra uma atualização de agent
   */
  app.post("/api/agents/:agentId/sync", async (req: any, res: any) => {
    try {
      const { agentId } = req.params;
      const { agentCode, agentName, action, changes } = req.body;

      const success = await service.onAgentUpdated(
        agentId,
        agentCode,
        agentName,
        action,
        changes
      );

      res.json({
        success,
        message: success
          ? "Sync task queued"
          : "Duplicate sync task skipped",
      });
    } catch (error) {
      res.status(500).json({
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  });

  /**
   * GET /api/agents/sync/status
   * Retorna status da sincronização
   */
  app.get("/api/agents/sync/status", (req: any, res: any) => {
    res.json(service.getStatus());
  });

  /**
   * GET /api/agents/sync/metrics
   * Retorna métricas detalhadas
   */
  app.get("/api/agents/sync/metrics", (req: any, res: any) => {
    res.json(service.getMetrics());
  });

  /**
   * GET /metrics (Prometheus)
   * Retorna métricas em formato Prometheus
   */
  app.get("/metrics", (req: any, res: any) => {
    res.set("Content-Type", "text/plain; charset=utf-8");
    res.send(service.getPrometheusMetrics());
  });

  /**
   * Health check
   */
  app.get("/health", (req: any, res: any) => {
    const status = service.getStatus();
    const isHealthy =
      status.failureRate < 10 && status.deadLetterSize < 50;

    res.status(isHealthy ? 200 : 503).json({
      healthy: isHealthy,
      status,
    });
  });
}

/**
 * Exemplo de uso com webhook GitHub
 */
export async function handleGitHubWebhook(
  payload: any,
  service: AgentSyncService
): Promise<void> {
  // Se push contém alterações em agent files
  if (
    payload.action === "opened" ||
    payload.action === "synchronize"
  ) {
    const prTitle = payload.pull_request?.title || "";

    // Detecta se é update de agent
    if (prTitle.includes("[AGENT]")) {
      const match = prTitle.match(/\[(AGENT)\]\s+(\w+)\s+(\S+)/);
      if (match) {
        const [, , agentCode, action] = match;

        await service.onAgentUpdated(
          `pr_${payload.pull_request.id}`,
          agentCode,
          agentCode.toLowerCase(),
          action as any,
          [{ field: "source", oldValue: "manual", newValue: "github-pr" }]
        );
      }
    }
  }
}
