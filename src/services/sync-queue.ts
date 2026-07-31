/**
 * Sync Queue Manager — Sistema de fila de sincronização com priorização
 * Versão: 1.0.0
 *
 * Recursos:
 * - FIFO queue com priorização (CRITICAL > HIGH > MEDIUM > LOW)
 * - Idempotency checks via hash SHA256 de conteúdo
 * - Batch processing (max 10 itens por vez)
 * - Dead letter queue com retry policy
 * - Observability: Prometheus metrics (queue size, processed, failed, latency)
 * - Pronto para Supabase (persistência opcional)
 */

import crypto from "crypto";

/**
 * Enum de prioridades de item na fila
 */
export enum QueuePriority {
  CRITICAL = 0,
  HIGH = 1,
  MEDIUM = 2,
  LOW = 3,
}

/**
 * Enum de status do item na fila
 */
export enum QueueItemStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  DEAD_LETTER = "dead_letter",
}

/**
 * Interface para um item da fila de sincronização
 */
export interface SyncQueueItem<T = Record<string, unknown>> {
  id: string;
  contentHash: string; // SHA256 hash do conteúdo para idempotency
  priority: QueuePriority;
  status: QueueItemStatus;
  data: T;
  retryCount: number;
  maxRetries: number;
  createdAt: Date;
  processedAt?: Date;
  failureReason?: string;
  metadata?: {
    source?: string; // origem do item (api, webhook, scheduler)
    tags?: string[];
    correlationId?: string; // para rastrear relacionados
    ttl?: number; // time to live em ms
  };
}

/**
 * Interface para configuração de retry
 */
export interface RetryPolicy {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number; // exponential backoff
}

/**
 * Interface para métricas de fila
 */
export interface QueueMetrics {
  timestamp: Date;
  queueSize: number;
  deadLetterSize: number;
  totalProcessed: number;
  totalFailed: number;
  averageLatencyMs: number;
  processingRate: number; // items/sec
  failureRate: number; // %
  byPriority: Record<QueuePriority, { queued: number; processed: number }>;
  byStatus: Record<QueueItemStatus, number>;
}

/**
 * Interface para Prometheus metrics
 */
export interface PrometheusMetrics {
  queue_size: number;
  dead_letter_queue_size: number;
  items_processed_total: number;
  items_failed_total: number;
  processing_duration_ms: number[];
  queue_wait_time_ms: number[];
}

/**
 * Calcula SHA256 hash do conteúdo
 */
function calculateContentHash(content: unknown): string {
  const jsonString = JSON.stringify(content);
  return crypto.createHash("sha256").update(jsonString).digest("hex");
}

/**
 * Monitor de Prometheus metrics
 */
class PrometheusMonitor {
  private metrics: PrometheusMetrics = {
    queue_size: 0,
    dead_letter_queue_size: 0,
    items_processed_total: 0,
    items_failed_total: 0,
    processing_duration_ms: [],
    queue_wait_time_ms: [],
  };

  private maxHistorySize = 1000; // Manter últimos 1000 eventos para calcular médias

  recordQueueSize(size: number): void {
    this.metrics.queue_size = size;
  }

  recordDeadLetterSize(size: number): void {
    this.metrics.dead_letter_queue_size = size;
  }

  recordItemProcessed(durationMs: number): void {
    this.metrics.items_processed_total++;
    this.metrics.processing_duration_ms.push(durationMs);

    // Manter apenas histórico limitado
    if (this.metrics.processing_duration_ms.length > this.maxHistorySize) {
      this.metrics.processing_duration_ms.shift();
    }
  }

  recordItemFailed(): void {
    this.metrics.items_failed_total++;
  }

  recordQueueWaitTime(waitMs: number): void {
    this.metrics.queue_wait_time_ms.push(waitMs);

    if (this.metrics.queue_wait_time_ms.length > this.maxHistorySize) {
      this.metrics.queue_wait_time_ms.shift();
    }
  }

  getMetrics(): PrometheusMetrics {
    return { ...this.metrics };
  }

  getPrometheusFormat(): string {
    const lines: string[] = [];

    // Gauge metrics
    lines.push(`# HELP queue_size Current size of the sync queue`);
    lines.push(`# TYPE queue_size gauge`);
    lines.push(`queue_size ${this.metrics.queue_size}`);

    lines.push(`# HELP dead_letter_queue_size Current size of the dead letter queue`);
    lines.push(`# TYPE dead_letter_queue_size gauge`);
    lines.push(`dead_letter_queue_size ${this.metrics.dead_letter_queue_size}`);

    // Counter metrics
    lines.push(`# HELP items_processed_total Total items processed successfully`);
    lines.push(`# TYPE items_processed_total counter`);
    lines.push(`items_processed_total ${this.metrics.items_processed_total}`);

    lines.push(`# HELP items_failed_total Total items that failed processing`);
    lines.push(`# TYPE items_failed_total counter`);
    lines.push(`items_failed_total ${this.metrics.items_failed_total}`);

    // Histogram metrics (simplificado)
    if (this.metrics.processing_duration_ms.length > 0) {
      const avgDuration =
        this.metrics.processing_duration_ms.reduce((a, b) => a + b, 0) /
        this.metrics.processing_duration_ms.length;
      const maxDuration = Math.max(...this.metrics.processing_duration_ms);

      lines.push(
        `# HELP processing_duration_ms Processing duration histogram`
      );
      lines.push(`# TYPE processing_duration_ms histogram`);
      lines.push(
        `processing_duration_ms_sum ${this.metrics.processing_duration_ms.reduce((a, b) => a + b, 0)}`
      );
      lines.push(
        `processing_duration_ms_count ${this.metrics.processing_duration_ms.length}`
      );
      lines.push(
        `processing_duration_ms{quantile="0.5"} ${this.getPercentile(this.metrics.processing_duration_ms, 50)}`
      );
      lines.push(
        `processing_duration_ms{quantile="0.95"} ${this.getPercentile(this.metrics.processing_duration_ms, 95)}`
      );
      lines.push(
        `processing_duration_ms{quantile="0.99"} ${this.getPercentile(this.metrics.processing_duration_ms, 99)}`
      );
      lines.push(`processing_duration_ms{quantile="+Inf"} ${maxDuration}`);
    }

    if (this.metrics.queue_wait_time_ms.length > 0) {
      const maxWaitTime = Math.max(...this.metrics.queue_wait_time_ms);
      lines.push(`# HELP queue_wait_time_ms Queue wait time histogram`);
      lines.push(`# TYPE queue_wait_time_ms histogram`);
      lines.push(
        `queue_wait_time_ms_sum ${this.metrics.queue_wait_time_ms.reduce((a, b) => a + b, 0)}`
      );
      lines.push(
        `queue_wait_time_ms_count ${this.metrics.queue_wait_time_ms.length}`
      );
      lines.push(
        `queue_wait_time_ms{quantile="0.5"} ${this.getPercentile(this.metrics.queue_wait_time_ms, 50)}`
      );
      lines.push(
        `queue_wait_time_ms{quantile="0.95"} ${this.getPercentile(this.metrics.queue_wait_time_ms, 95)}`
      );
      lines.push(
        `queue_wait_time_ms{quantile="0.99"} ${this.getPercentile(this.metrics.queue_wait_time_ms, 99)}`
      );
      lines.push(`queue_wait_time_ms{quantile="+Inf"} ${maxWaitTime}`);
    }

    return lines.join("\n");
  }

  private getPercentile(arr: number[], percentile: number): number {
    if (arr.length === 0) return 0;

    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  reset(): void {
    this.metrics = {
      queue_size: 0,
      dead_letter_queue_size: 0,
      items_processed_total: 0,
      items_failed_total: 0,
      processing_duration_ms: [],
      queue_wait_time_ms: [],
    };
  }
}

/**
 * Sync Queue Manager — Fila FIFO com priorização e resiliência
 */
export class SyncQueueManager<T = Record<string, unknown>> {
  private queue: SyncQueueItem<T>[] = [];
  private deadLetterQueue: SyncQueueItem<T>[] = [];
  private processedHashes: Set<string> = new Set(); // Rastreamento de idempotency
  private processingItems: Set<string> = new Set(); // Items sendo processados
  private retryPolicy: RetryPolicy = {
    maxRetries: 3,
    initialDelayMs: 1000,
    maxDelayMs: 30000,
    backoffMultiplier: 2,
  };
  private maxBatchSize = 10;
  private monitor = new PrometheusMonitor();
  private processingInterval: NodeJS.Timeout | null = null;
  private processingIntervalMs: number = 5000; // 5 segundos
  private isProcessing = false;

  // Callbacks para processamento customizado
  private processCallback: (item: SyncQueueItem<T>) => Promise<void> =
    async () => {
      /* default no-op */
    };

  constructor(config?: {
    maxBatchSize?: number;
    retryPolicy?: Partial<RetryPolicy>;
    processingIntervalMs?: number;
  }) {
    if (config?.maxBatchSize) {
      this.maxBatchSize = config.maxBatchSize;
    }
    if (config?.retryPolicy) {
      this.retryPolicy = { ...this.retryPolicy, ...config.retryPolicy };
    }
    if (config?.processingIntervalMs) {
      this.processingIntervalMs = config.processingIntervalMs;
    }

    console.log(
      `✅ SyncQueueManager initialized (batch size: ${this.maxBatchSize}, interval: ${this.processingIntervalMs}ms)`
    );
  }

  /**
   * Define callback para processamento de items
   */
  public onProcess(
    callback: (item: SyncQueueItem<T>) => Promise<void>
  ): void {
    this.processCallback = callback;
  }

  /**
   * Adiciona item à fila
   * Retorna false se item é duplicado (mesmo contentHash)
   */
  public async enqueue(
    data: T,
    priority: QueuePriority = QueuePriority.MEDIUM,
    metadata?: SyncQueueItem<T>["metadata"]
  ): Promise<boolean> {
    const contentHash = calculateContentHash(data);

    // Idempotency check
    if (this.processedHashes.has(contentHash)) {
      console.warn(
        `⚠️ Item with hash ${contentHash.substring(0, 8)}... already processed. Skipping.`
      );
      return false;
    }

    const item: SyncQueueItem<T> = {
      id: `item_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      contentHash,
      priority,
      status: QueueItemStatus.PENDING,
      data,
      retryCount: 0,
      maxRetries: this.retryPolicy.maxRetries,
      createdAt: new Date(),
      metadata,
    };

    this.queue.push(item);
    this.sortQueue();

    this.monitor.recordQueueSize(this.queue.length);

    console.log(
      `📥 Item ${item.id} (priority: ${priority}) added to queue. Queue size: ${this.queue.length}`
    );

    return true;
  }

  /**
   * Inicia processamento contínuo da fila
   */
  public startProcessing(): void {
    if (this.processingInterval) {
      console.warn("⚠️ Processing already started");
      return;
    }

    console.log("▶️ Starting queue processing...");

    this.processingInterval = setInterval(async () => {
      await this.processBatch();
    }, this.processingIntervalMs);
  }

  /**
   * Para o processamento contínuo
   */
  public stopProcessing(): void {
    if (this.processingInterval) {
      clearInterval(this.processingInterval);
      this.processingInterval = null;
      console.log("⏹️ Queue processing stopped");
    }
  }

  /**
   * Processa um batch de items
   */
  public async processBatch(): Promise<number> {
    if (this.isProcessing || this.queue.length === 0) {
      return 0;
    }

    this.isProcessing = true;

    try {
      const batch = this.queue.splice(0, this.maxBatchSize);
      this.monitor.recordQueueSize(this.queue.length);

      if (batch.length === 0) {
        return 0;
      }

      console.log(
        `⚙️ Processing batch of ${batch.length} items (queue remaining: ${this.queue.length})`
      );

      let successCount = 0;
      let failureCount = 0;

      for (const item of batch) {
        // Marca como processando
        item.status = QueueItemStatus.PROCESSING;
        this.processingItems.add(item.id);

        const startTime = Date.now();
        const waitTime = startTime - item.createdAt.getTime();
        this.monitor.recordQueueWaitTime(waitTime);

        try {
          await this.processCallback(item);

          item.status = QueueItemStatus.COMPLETED;
          item.processedAt = new Date();
          this.processedHashes.add(item.contentHash);

          const processingTime = Date.now() - startTime;
          this.monitor.recordItemProcessed(processingTime);

          console.log(
            `✅ Item ${item.id} processed successfully (${processingTime}ms)`
          );
          successCount++;
        } catch (error) {
          console.error(
            `❌ Error processing item ${item.id}:`,
            error instanceof Error ? error.message : String(error)
          );

          await this.handleFailedItem(item, error);
          failureCount++;
        } finally {
          this.processingItems.delete(item.id);
        }
      }

      console.log(
        `📊 Batch complete: ${successCount} succeeded, ${failureCount} failed`
      );

      return successCount;
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Manipula item que falhou
   */
  private async handleFailedItem(
    item: SyncQueueItem<T>,
    error: unknown
  ): Promise<void> {
    item.retryCount++;
    item.failureReason = error instanceof Error ? error.message : String(error);

    if (item.retryCount < item.maxRetries) {
      // Retry com backoff exponencial
      const delayMs = Math.min(
        this.retryPolicy.initialDelayMs *
          Math.pow(this.retryPolicy.backoffMultiplier, item.retryCount - 1),
        this.retryPolicy.maxDelayMs
      );

      console.log(
        `🔄 Retrying item ${item.id} in ${delayMs}ms (attempt ${item.retryCount}/${item.maxRetries})`
      );

      // Re-adiciona à fila após delay
      item.status = QueueItemStatus.PENDING;
      setTimeout(() => {
        this.queue.push(item);
        this.sortQueue();
        this.monitor.recordQueueSize(this.queue.length);
      }, delayMs);
    } else {
      // Movido para dead letter queue
      item.status = QueueItemStatus.DEAD_LETTER;
      this.deadLetterQueue.push(item);

      this.monitor.recordItemFailed();
      this.monitor.recordDeadLetterSize(this.deadLetterQueue.length);

      console.error(
        `💀 Item ${item.id} moved to dead letter queue after ${item.maxRetries} retries`
      );
    }
  }

  /**
   * Ordena fila por prioridade (CRITICAL primeiro)
   */
  private sortQueue(): void {
    this.queue.sort((a, b) => {
      if (a.priority !== b.priority) {
        return a.priority - b.priority; // Menor número = maior prioridade
      }
      return a.createdAt.getTime() - b.createdAt.getTime(); // FIFO secundário
    });
  }

  /**
   * Retorna size atual da fila
   */
  public getQueueSize(): number {
    return this.queue.length;
  }

  /**
   * Retorna size da dead letter queue
   */
  public getDeadLetterQueueSize(): number {
    return this.deadLetterQueue.length;
  }

  /**
   * Retorna items da dead letter queue
   */
  public getDeadLetterItems(limit: number = 50): SyncQueueItem<T>[] {
    return this.deadLetterQueue.slice(-limit);
  }

  /**
   * Remove item da dead letter queue (manual cleanup)
   */
  public removeFromDeadLetterQueue(itemId: string): boolean {
    const index = this.deadLetterQueue.findIndex((item) => item.id === itemId);
    if (index >= 0) {
      this.deadLetterQueue.splice(index, 1);
      this.monitor.recordDeadLetterSize(this.deadLetterQueue.length);
      console.log(`🗑️ Item ${itemId} removed from dead letter queue`);
      return true;
    }
    return false;
  }

  /**
   * Retorna item específico da fila ou dead letter
   */
  public getItem(itemId: string): SyncQueueItem<T> | null {
    const inQueue = this.queue.find((item) => item.id === itemId);
    if (inQueue) return inQueue;

    return this.deadLetterQueue.find((item) => item.id === itemId) || null;
  }

  /**
   * Calcula métricas agregadas
   */
  public getMetrics(): QueueMetrics {
    const prometheusMetrics = this.monitor.getMetrics();

    // Calcula por prioridade
    const byPriority: Record<QueuePriority, { queued: number; processed: number }> =
      {
        [QueuePriority.CRITICAL]: { queued: 0, processed: 0 },
        [QueuePriority.HIGH]: { queued: 0, processed: 0 },
        [QueuePriority.MEDIUM]: { queued: 0, processed: 0 },
        [QueuePriority.LOW]: { queued: 0, processed: 0 },
      };

    for (const item of this.queue) {
      byPriority[item.priority].queued++;
    }

    // Calcula por status
    const byStatus: Record<QueueItemStatus, number> = {
      [QueueItemStatus.PENDING]: this.queue.length,
      [QueueItemStatus.PROCESSING]: this.processingItems.size,
      [QueueItemStatus.COMPLETED]: prometheusMetrics.items_processed_total,
      [QueueItemStatus.FAILED]: 0, // Retried items volta à PENDING
      [QueueItemStatus.DEAD_LETTER]: this.deadLetterQueue.length,
    };

    // Calcula latência média
    let averageLatencyMs = 0;
    if (prometheusMetrics.processing_duration_ms.length > 0) {
      averageLatencyMs =
        prometheusMetrics.processing_duration_ms.reduce((a, b) => a + b, 0) /
        prometheusMetrics.processing_duration_ms.length;
    }

    // Taxa de processamento (items/sec)
    const totalProcessed = prometheusMetrics.items_processed_total;
    const processingRate = totalProcessed > 0 ? totalProcessed / 60 : 0; // Aproximado

    // Taxa de falha
    const totalAttempts =
      prometheusMetrics.items_processed_total +
      prometheusMetrics.items_failed_total;
    const failureRate =
      totalAttempts > 0
        ? (prometheusMetrics.items_failed_total / totalAttempts) * 100
        : 0;

    return {
      timestamp: new Date(),
      queueSize: prometheusMetrics.queue_size,
      deadLetterSize: prometheusMetrics.dead_letter_queue_size,
      totalProcessed: prometheusMetrics.items_processed_total,
      totalFailed: prometheusMetrics.items_failed_total,
      averageLatencyMs,
      processingRate,
      failureRate,
      byPriority,
      byStatus,
    };
  }

  /**
   * Retorna métricas Prometheus em formato text
   */
  public getPrometheusMetrics(): string {
    return this.monitor.getPrometheusFormat();
  }

  /**
   * Limpa queue e dead letter (para testes)
   */
  public clear(): void {
    this.queue = [];
    this.deadLetterQueue = [];
    this.processedHashes.clear();
    this.processingItems.clear();
    this.monitor.reset();
    console.log("🧹 Queue cleared");
  }

  /**
   * Cleanup resources
   */
  public destroy(): void {
    this.stopProcessing();
    this.clear();
    console.log("🧹 SyncQueueManager destroyed");
  }
}

/**
 * Exemplo de uso
 */
export async function runSyncQueueExamples(): Promise<void> {
  console.log("\n=== SYNC QUEUE MANAGER EXAMPLES ===\n");

  const manager = new SyncQueueManager<{ id: string; timestamp: string }>({
    maxBatchSize: 5,
    processingIntervalMs: 2000,
  });

  // Define callback de processamento
  manager.onProcess(async (item) => {
    // Simula processamento
    await new Promise((resolve) =>
      setTimeout(resolve, Math.random() * 500 + 100)
    );

    // 10% de chance de falha para testar retry
    if (Math.random() < 0.1) {
      throw new Error("Simulated processing error");
    }
  });

  // Exemplo 1: Adiciona items com diferentes prioridades
  console.log("📝 Adding items to queue...\n");

  // Items com prioridade LOW
  for (let i = 0; i < 3; i++) {
    await manager.enqueue(
      { id: `low_${i}`, timestamp: new Date().toISOString() },
      QueuePriority.LOW,
      { source: "example", tags: ["low-priority"] }
    );
  }

  // Items com prioridade HIGH
  for (let i = 0; i < 2; i++) {
    await manager.enqueue(
      { id: `high_${i}`, timestamp: new Date().toISOString() },
      QueuePriority.HIGH,
      { source: "example", tags: ["high-priority"] }
    );
  }

  // Items com prioridade CRITICAL
  await manager.enqueue(
    { id: "critical_0", timestamp: new Date().toISOString() },
    QueuePriority.CRITICAL,
    { source: "example", tags: ["critical"] }
  );

  // Testa idempotency
  console.log("\n🔄 Testing idempotency...");
  const duplicateResult = await manager.enqueue(
    { id: "low_0", timestamp: new Date().toISOString() },
    QueuePriority.LOW
  );
  console.log(`Duplicate item result: ${duplicateResult}\n`);

  // Inicia processamento
  manager.startProcessing();

  // Aguarda processamento
  console.log("⏳ Waiting for processing...\n");
  await new Promise((resolve) => setTimeout(resolve, 10000));

  // Mostra métricas
  const metrics = manager.getMetrics();
  console.log("\n📊 Queue Metrics:");
  console.log(`   Queue size: ${metrics.queueSize}`);
  console.log(`   Dead letter size: ${metrics.deadLetterSize}`);
  console.log(`   Total processed: ${metrics.totalProcessed}`);
  console.log(`   Total failed: ${metrics.totalFailed}`);
  console.log(`   Average latency: ${metrics.averageLatencyMs.toFixed(0)}ms`);
  console.log(`   Processing rate: ${metrics.processingRate.toFixed(2)} items/sec`);
  console.log(`   Failure rate: ${metrics.failureRate.toFixed(1)}%`);

  console.log("\n📈 By Priority:");
  for (const [priority, data] of Object.entries(metrics.byPriority)) {
    console.log(`   ${priority}: ${data.queued} queued, ${data.processed} processed`);
  }

  // Mostra Prometheus format
  console.log("\n📡 Prometheus Metrics:");
  console.log(manager.getPrometheusMetrics());

  // Mostra dead letter items
  if (metrics.deadLetterSize > 0) {
    console.log("\n💀 Dead Letter Queue Items:");
    const dlItems = manager.getDeadLetterItems();
    for (const item of dlItems) {
      console.log(
        `   ${item.id}: ${item.failureReason} (retries: ${item.retryCount}/${item.maxRetries})`
      );
    }
  }

  // Cleanup
  manager.stopProcessing();
  manager.destroy();
}
