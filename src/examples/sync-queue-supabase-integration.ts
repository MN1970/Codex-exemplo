/**
 * Sync Queue Manager — Integração com Supabase
 * Exemplo completo de integração para persistência e sincronização
 *
 * Requisitos:
 * - Supabase project configurado
 * - Tabelas criadas via migration
 * - @supabase/supabase-js instalado
 */

import {
  SyncQueueManager,
  QueuePriority,
  QueueItemStatus,
  SyncQueueItem,
} from "../services/sync-queue";

/**
 * Tipo de dado sincronizado
 */
export interface SyncPayload {
  id: string;
  entityType: "agent" | "skill" | "project";
  entityId: string;
  action: "create" | "update" | "delete";
  data: Record<string, unknown>;
  timestamp: string;
}

/**
 * Configuração para Supabase persistence
 */
export interface SupabaseQueueConfig {
  supabaseUrl: string;
  supabaseKey: string;
  tableName?: string; // default: 'sync_queue'
  deadLetterTableName?: string; // default: 'sync_queue_dead_letter'
}

/**
 * Supabase Sync Queue — Estende SyncQueueManager com persistência
 */
export class SupabaseSyncQueue {
  private manager: SyncQueueManager<SyncPayload>;
  private supabaseUrl: string;
  private supabaseKey: string;
  private tableName: string;
  private deadLetterTableName: string;
  private persistenceEnabled: boolean = false;

  constructor(config: SupabaseQueueConfig) {
    this.supabaseUrl = config.supabaseUrl;
    this.supabaseKey = config.supabaseKey;
    this.tableName = config.tableName || "sync_queue";
    this.deadLetterTableName = config.deadLetterTableName || "sync_queue_dead_letter";

    this.manager = new SyncQueueManager<SyncPayload>({
      maxBatchSize: 10,
      processingIntervalMs: 5000,
      retryPolicy: {
        maxRetries: 3,
        initialDelayMs: 1000,
        maxDelayMs: 30000,
        backoffMultiplier: 2,
      },
    });

    console.log(
      `✅ SupabaseSyncQueue initialized (table: ${this.tableName})`
    );
  }

  /**
   * Carrega items pendentes do Supabase
   */
  public async loadPendingItems(): Promise<void> {
    try {
      const response = await fetch(
        `${this.supabaseUrl}/rest/v1/${this.tableName}?status=eq.pending&order=priority.asc,created_at.asc`,
        {
          method: "GET",
          headers: {
            apikey: this.supabaseKey,
            Authorization: `Bearer ${this.supabaseKey}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to load items: ${response.status} ${response.statusText}`
        );
      }

      const items = (await response.json()) as Array<{
        id: string;
        content_hash: string;
        priority: number;
        data: SyncPayload;
        retry_count: number;
        max_retries: number;
        created_at: string;
      }>;

      console.log(`📥 Loaded ${items.length} pending items from Supabase`);

      for (const item of items) {
        await this.manager.enqueue(item.data, item.priority as QueuePriority, {
          source: "supabase",
          tags: ["persisted"],
        });
      }
    } catch (error) {
      console.error("Failed to load pending items from Supabase:", error);
      throw error;
    }
  }

  /**
   * Salva item no Supabase
   */
  private async persistItem(
    item: SyncQueueItem<SyncPayload>
  ): Promise<void> {
    if (!this.persistenceEnabled) return;

    try {
      const response = await fetch(
        `${this.supabaseUrl}/rest/v1/${this.tableName}`,
        {
          method: "POST",
          headers: {
            apikey: this.supabaseKey,
            Authorization: `Bearer ${this.supabaseKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            id: item.id,
            content_hash: item.contentHash,
            priority: item.priority,
            status: item.status,
            data: item.data,
            retry_count: item.retryCount,
            max_retries: item.maxRetries,
            created_at: item.createdAt.toISOString(),
            processed_at: item.processedAt?.toISOString() || null,
            failure_reason: item.failureReason || null,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to persist item: ${response.status} ${response.statusText}`
        );
      }

      console.log(`💾 Item ${item.id} persisted to Supabase`);
    } catch (error) {
      console.error(`Failed to persist item ${item.id}:`, error);
      // Não lance erro para não travar o processamento
    }
  }

  /**
   * Atualiza status do item no Supabase
   */
  private async updateItemStatus(
    itemId: string,
    status: QueueItemStatus
  ): Promise<void> {
    if (!this.persistenceEnabled) return;

    try {
      const response = await fetch(
        `${this.supabaseUrl}/rest/v1/${this.tableName}?id=eq.${itemId}`,
        {
          method: "PATCH",
          headers: {
            apikey: this.supabaseKey,
            Authorization: `Bearer ${this.supabaseKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status,
            processed_at: new Date().toISOString(),
          }),
        }
      );

      if (!response.ok) {
        console.warn(
          `Failed to update item status in Supabase: ${response.status}`
        );
      }
    } catch (error) {
      console.error(`Failed to update item status:`, error);
    }
  }

  /**
   * Move item para dead letter queue no Supabase
   */
  private async moveToDeadLetterQueue(
    item: SyncQueueItem<SyncPayload>
  ): Promise<void> {
    if (!this.persistenceEnabled) return;

    try {
      // Remove da fila principal
      await fetch(
        `${this.supabaseUrl}/rest/v1/${this.tableName}?id=eq.${item.id}`,
        {
          method: "DELETE",
          headers: {
            apikey: this.supabaseKey,
            Authorization: `Bearer ${this.supabaseKey}`,
          },
        }
      );

      // Insere na dead letter queue
      const response = await fetch(
        `${this.supabaseUrl}/rest/v1/${this.deadLetterTableName}`,
        {
          method: "POST",
          headers: {
            apikey: this.supabaseKey,
            Authorization: `Bearer ${this.supabaseKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            id: item.id,
            content_hash: item.contentHash,
            priority: item.priority,
            data: item.data,
            retry_count: item.retryCount,
            max_retries: item.maxRetries,
            created_at: item.createdAt.toISOString(),
            moved_at: new Date().toISOString(),
            failure_reason: item.failureReason,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to move to DLQ: ${response.status} ${response.statusText}`
        );
      }

      console.log(`💀 Item ${item.id} moved to dead letter queue`);
    } catch (error) {
      console.error(`Failed to move item to DLQ:`, error);
    }
  }

  /**
   * Configura e inicia processamento com callback customizado
   */
  public setProcessingCallback(
    callback: (payload: SyncPayload) => Promise<void>
  ): void {
    this.manager.onProcess(async (item) => {
      try {
        console.log(
          `🔄 Processing sync for ${item.data.entityType}/${item.data.entityId}`
        );
        await callback(item.data);
        await this.updateItemStatus(item.id, QueueItemStatus.COMPLETED);
      } catch (error) {
        console.error(
          `Error processing item ${item.id}:`,
          error instanceof Error ? error.message : String(error)
        );
        throw error; // Deixa o manager lidar com retry
      }
    });
  }

  /**
   * Inicia processamento da fila
   */
  public startProcessing(): void {
    this.manager.startProcessing();
    console.log("▶️ Sync queue processing started");
  }

  /**
   * Para processamento
   */
  public stopProcessing(): void {
    this.manager.stopProcessing();
    console.log("⏹️ Sync queue processing stopped");
  }

  /**
   * Adiciona item à fila
   */
  public async enqueue(
    payload: SyncPayload,
    priority: QueuePriority = QueuePriority.MEDIUM
  ): Promise<boolean> {
    const success = await this.manager.enqueue(payload, priority, {
      source: "api",
      tags: [payload.entityType, payload.action],
      correlationId: payload.id,
    });

    if (success) {
      await this.persistItem(
        this.manager.getItem(payload.id) as SyncQueueItem<SyncPayload>
      );
    }

    return success;
  }

  /**
   * Retorna métricas
   */
  public getMetrics() {
    return this.manager.getMetrics();
  }

  /**
   * Retorna Prometheus metrics
   */
  public getPrometheusMetrics(): string {
    return this.manager.getPrometheusMetrics();
  }

  /**
   * Cleanup
   */
  public destroy(): void {
    this.manager.destroy();
    console.log("🧹 SupabaseSyncQueue destroyed");
  }
}

/**
 * Exemplo de uso com diferentes tipos de entidades
 */
export async function runSupabaseIntegrationExample(): Promise<void> {
  console.log("\n=== SUPABASE SYNC QUEUE INTEGRATION EXAMPLE ===\n");

  const queue = new SupabaseSyncQueue({
    supabaseUrl: process.env.SUPABASE_URL || "https://your-project.supabase.co",
    supabaseKey: process.env.SUPABASE_ANON_KEY || "your-anon-key",
  });

  // Define callback de sincronização
  queue.setProcessingCallback(async (payload) => {
    console.log(`✅ Syncing ${payload.entityType}: ${payload.entityId}`);

    // Simula chamada a API externa
    await new Promise((resolve) => setTimeout(resolve, 500));

    console.log(`📤 Synced ${payload.entityType}/${payload.entityId} successfully`);
  });

  // Exemplo: Sincronizar agents
  const agentPayload: SyncPayload = {
    id: "sync_agent_123",
    entityType: "agent",
    entityId: "manta_03_s8",
    action: "update",
    data: {
      agentCode: "Manta 03-S8",
      agentName: "agente-saneamento",
      status: "updated",
      version: "1.2.0",
    },
    timestamp: new Date().toISOString(),
  };

  // Exemplo: Sincronizar skills
  const skillPayload: SyncPayload = {
    id: "sync_skill_456",
    entityType: "skill",
    entityId: "sicro_completo",
    action: "create",
    data: {
      skillName: "sicro-completo",
      description: "Sincroniza base SICRO completa",
      version: "2.1.0",
    },
    timestamp: new Date().toISOString(),
  };

  // Exemplo: Sincronizar projeto
  const projectPayload: SyncPayload = {
    id: "sync_project_789",
    entityType: "project",
    entityId: "project_aysasp_01",
    action: "update",
    data: {
      projectName: "AySA São Paulo",
      status: "in-progress",
      lastUpdate: new Date().toISOString(),
    },
    timestamp: new Date().toISOString(),
  };

  console.log("📝 Enqueueing sync tasks...\n");

  // Enqueue com diferentes prioridades
  await queue.enqueue(agentPayload, QueuePriority.HIGH);
  await queue.enqueue(skillPayload, QueuePriority.MEDIUM);
  await queue.enqueue(projectPayload, QueuePriority.LOW);

  // Inicia processamento
  queue.startProcessing();

  // Aguarda processamento
  console.log("⏳ Processing queue...\n");
  await new Promise((resolve) => setTimeout(resolve, 5000));

  // Mostra métricas
  const metrics = queue.getMetrics();
  console.log("\n📊 Sync Queue Metrics:");
  console.log(`   Queue size: ${metrics.queueSize}`);
  console.log(`   Processed: ${metrics.totalProcessed}`);
  console.log(`   Failed: ${metrics.totalFailed}`);
  console.log(`   Average latency: ${metrics.averageLatencyMs.toFixed(0)}ms`);
  console.log(`   Failure rate: ${metrics.failureRate.toFixed(1)}%`);

  queue.stopProcessing();
  queue.destroy();
}

/**
 * Schema Supabase (migrations/001_create_sync_queue.sql)
 *
 * -- Fila principal de sincronização
 * CREATE TABLE sync_queue (
 *   id TEXT PRIMARY KEY,
 *   content_hash TEXT UNIQUE NOT NULL,
 *   priority INTEGER NOT NULL,
 *   status TEXT NOT NULL DEFAULT 'pending',
 *   data JSONB NOT NULL,
 *   retry_count INTEGER DEFAULT 0,
 *   max_retries INTEGER DEFAULT 3,
 *   created_at TIMESTAMP DEFAULT NOW(),
 *   processed_at TIMESTAMP,
 *   failure_reason TEXT,
 *   INDEX idx_status (status),
 *   INDEX idx_priority (priority),
 *   INDEX idx_content_hash (content_hash),
 *   INDEX idx_created_at (created_at)
 * );
 *
 * -- Dead letter queue
 * CREATE TABLE sync_queue_dead_letter (
 *   id TEXT PRIMARY KEY,
 *   content_hash TEXT NOT NULL,
 *   priority INTEGER NOT NULL,
 *   data JSONB NOT NULL,
 *   retry_count INTEGER,
 *   max_retries INTEGER,
 *   created_at TIMESTAMP,
 *   moved_at TIMESTAMP DEFAULT NOW(),
 *   failure_reason TEXT,
 *   INDEX idx_moved_at (moved_at)
 * );
 *
 * -- Métricas agregadas (para dashboards)
 * CREATE TABLE sync_queue_metrics (
 *   id SERIAL PRIMARY KEY,
 *   timestamp TIMESTAMP DEFAULT NOW(),
 *   queue_size INTEGER,
 *   dead_letter_size INTEGER,
 *   items_processed_total BIGINT,
 *   items_failed_total BIGINT,
 *   average_latency_ms FLOAT,
 *   failure_rate FLOAT,
 *   INDEX idx_timestamp (timestamp)
 * );
 *
 * -- Row-level security policies
 * ALTER TABLE sync_queue ENABLE ROW LEVEL SECURITY;
 * CREATE POLICY "Authenticated users can view sync queue"
 *   ON sync_queue FOR SELECT
 *   USING (auth.role() = 'authenticated');
 *
 * ALTER TABLE sync_queue_dead_letter ENABLE ROW LEVEL SECURITY;
 * CREATE POLICY "Authenticated users can view dead letter queue"
 *   ON sync_queue_dead_letter FOR SELECT
 *   USING (auth.role() = 'authenticated');
 */
