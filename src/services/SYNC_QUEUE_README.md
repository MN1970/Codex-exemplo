# Sync Queue Manager

Um sistema robusto de fila de sincronização FIFO com priorização, idempotência, retry automático e observabilidade Prometheus.

## Características

- **FIFO com Priorização**: Suporta 4 níveis de prioridade (CRITICAL > HIGH > MEDIUM > LOW)
- **Idempotency**: Hash SHA256 de conteúdo previne duplicatas
- **Batch Processing**: Processa até 10 items por vez (configurável)
- **Dead Letter Queue**: Items que falham após retries são movidos para quarentena
- **Retry Policy**: Backoff exponencial com configuração customizável
- **Observability**: Métricas Prometheus completas (latência, throughput, taxa de falha)
- **TypeScript**: Type-safe com interfaces bem definidas
- **Supabase Ready**: Exemplo de integração com persistência em Supabase

## Instalação

```bash
npm install
# Ou yarn/pnpm
```

## Uso Básico

```typescript
import { SyncQueueManager, QueuePriority } from './src/services/sync-queue';

// Criar manager
const manager = new SyncQueueManager<{ id: string; data: string }>({
  maxBatchSize: 10,
  processingIntervalMs: 5000,
});

// Define callback de processamento
manager.onProcess(async (item) => {
  // Processar item
  console.log('Processing:', item.data);
  // Pode lançar erro para retry automático
});

// Adiciona items à fila
await manager.enqueue(
  { id: 'item1', data: 'content1' },
  QueuePriority.HIGH,
  { source: 'api', tags: ['important'] }
);

// Inicia processamento
manager.startProcessing();

// ... mais tarde
manager.stopProcessing();
manager.destroy();
```

## Prioridades

```typescript
export enum QueuePriority {
  CRITICAL = 0,  // Processa primeiro
  HIGH = 1,
  MEDIUM = 2,
  LOW = 3        // Processa por último
}
```

Items com mesma prioridade respeitam ordem FIFO.

## Idempotency

A fila usa hash SHA256 do conteúdo para evitar processamento duplicado:

```typescript
const item1 = { id: 'test', data: 'content' };
await manager.enqueue(item1, QueuePriority.MEDIUM);  // true

const item2 = { id: 'test', data: 'content' };
await manager.enqueue(item2, QueuePriority.MEDIUM);  // false - duplicado
```

## Status do Item

```typescript
export enum QueueItemStatus {
  PENDING = 'pending',           // Na fila, aguardando processamento
  PROCESSING = 'processing',     // Sendo processado
  COMPLETED = 'completed',       // Processado com sucesso
  FAILED = 'failed',             // Falhou (será retentado)
  DEAD_LETTER = 'dead_letter'   // Falhou após max retries
}
```

## Retry Policy

Configuração padrão:

```typescript
const manager = new SyncQueueManager({
  retryPolicy: {
    maxRetries: 3,                    // Máximo de tentativas
    initialDelayMs: 1000,             // Delay inicial
    maxDelayMs: 30000,                // Delay máximo
    backoffMultiplier: 2              // Multiplicador exponencial
  }
});
```

Com essas configurações:
- 1ª tentativa: imediata
- 2ª tentativa: 1000ms depois
- 3ª tentativa: 2000ms depois
- 4ª tentativa: 4000ms depois (até maxDelayMs)

Se falhar após `maxRetries`, o item vai para Dead Letter Queue.

## Batch Processing

A fila processa items em lotes de até 10 (configurável):

```typescript
const manager = new SyncQueueManager({
  maxBatchSize: 5,  // Processa 5 items por lote
  processingIntervalMs: 5000  // Processa a cada 5 segundos
});
```

Você pode também processar manualmente um batch:

```typescript
const processed = await manager.processBatch();
console.log(`Processados ${processed} items`);
```

## Dead Letter Queue

Items que falham após retries vão para quarentena:

```typescript
const dlItems = manager.getDeadLetterItems(limit);

for (const item of dlItems) {
  console.log(`Item ${item.id}: ${item.failureReason}`);
  console.log(`Retries: ${item.retryCount}/${item.maxRetries}`);
}

// Remover item da DLQ manualmente
manager.removeFromDeadLetterQueue(itemId);
```

## Métricas

### Métricas Estruturadas

```typescript
const metrics = manager.getMetrics();

console.log(metrics);
// {
//   timestamp: Date,
//   queueSize: 5,
//   deadLetterSize: 2,
//   totalProcessed: 150,
//   totalFailed: 3,
//   averageLatencyMs: 245.3,
//   processingRate: 2.5,        // items/sec
//   failureRate: 1.98,          // %
//   byPriority: {
//     0: { queued: 1, processed: 50 },  // CRITICAL
//     1: { queued: 2, processed: 60 },  // HIGH
//     2: { queued: 1, processed: 30 },  // MEDIUM
//     3: { queued: 1, processed: 10 }   // LOW
//   },
//   byStatus: {
//     pending: 5,
//     processing: 0,
//     completed: 150,
//     failed: 0,
//     dead_letter: 2
//   }
// }
```

### Prometheus Format

```typescript
const prometheusMetrics = manager.getPrometheusMetrics();
console.log(prometheusMetrics);

// Retorna string em formato Prometheus:
// # HELP queue_size Current size of the sync queue
// # TYPE queue_size gauge
// queue_size 5
// 
// # HELP dead_letter_queue_size Current size of the dead letter queue
// # TYPE dead_letter_queue_size gauge
// dead_letter_queue_size 2
// 
// # HELP items_processed_total Total items processed successfully
// # TYPE items_processed_total counter
// items_processed_total 150
// 
// ... etc
```

Para integração com Prometheus:

```typescript
// Express example
app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain; charset=utf-8');
  res.send(manager.getPrometheusMetrics());
});
```

## Integração com Supabase

Veja `src/examples/sync-queue-supabase-integration.ts` para um exemplo completo.

### Schema SQL

```sql
-- Fila principal
CREATE TABLE sync_queue (
  id TEXT PRIMARY KEY,
  content_hash TEXT UNIQUE NOT NULL,
  priority INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  data JSONB NOT NULL,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP,
  failure_reason TEXT,
  INDEX idx_status (status),
  INDEX idx_priority (priority),
  INDEX idx_created_at (created_at)
);

-- Dead letter queue
CREATE TABLE sync_queue_dead_letter (
  id TEXT PRIMARY KEY,
  content_hash TEXT NOT NULL,
  priority INTEGER NOT NULL,
  data JSONB NOT NULL,
  retry_count INTEGER,
  max_retries INTEGER,
  created_at TIMESTAMP,
  moved_at TIMESTAMP DEFAULT NOW(),
  failure_reason TEXT,
  INDEX idx_moved_at (moved_at)
);
```

### Uso com Supabase

```typescript
import { SupabaseSyncQueue } from './src/examples/sync-queue-supabase-integration';

const queue = new SupabaseSyncQueue({
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseKey: process.env.SUPABASE_ANON_KEY,
});

// Carrega items pendentes do BD
await queue.loadPendingItems();

// Define callback de processamento
queue.setProcessingCallback(async (payload) => {
  // Seu código de sincronização aqui
  await sync(payload);
});

// Inicia processamento contínuo
queue.startProcessing();
```

## Metadata

Você pode adicionar metadata aos items para rastreamento:

```typescript
await manager.enqueue(
  { id: 'test', data: 'content' },
  QueuePriority.HIGH,
  {
    source: 'webhook',  // origem
    tags: ['important', 'urgent'],
    correlationId: 'corr-123',  // para rastrear relacionados
    ttl: 3600000  // time to live em ms
  }
);
```

## Eventos e Logs

A fila emite logs no console. Para capturar eventos, você pode estender a classe:

```typescript
class CustomSyncQueue extends SyncQueueManager {
  protected async handleFailedItem(item, error) {
    super.handleFailedItem(item, error);
    // Seu código aqui: alertar, registrar em BD, etc
  }
}
```

## Performance

### Benchmark

Com 1000 items em fila:
- Throughput: ~100-200 items/sec (depende do callback)
- Latência P95: ~500ms
- Latência P99: ~1000ms

### Otimizações

1. **Aumentar batch size** para melhor throughput:
   ```typescript
   const manager = new SyncQueueManager({ maxBatchSize: 20 });
   ```

2. **Reduzir interval** para menor latência:
   ```typescript
   const manager = new SyncQueueManager({ processingIntervalMs: 1000 });
   ```

3. **Callbacks rápidos** - mantenha processing callbacks curtos

4. **Persistência** - use Supabase para salvar estado entre restarts

## Testes

```bash
npm test -- src/services/__tests__/sync-queue.test.ts
```

Coverage:
- Enqueuing e duplicação
- Priorização e FIFO
- Batch processing
- Retry policy
- Dead letter queue
- Métricas
- Lifecycle

## Troubleshooting

### Items não estão sendo processados

1. Verifique se `startProcessing()` foi chamado
2. Verifique se callback está configurado com `onProcess()`
3. Verifique logs para erros no callback

### Dead letter queue crescendo

1. Verifique logs de erro para entender falhas
2. Aumente `maxRetries` se apropriado
3. Revise callback de processamento

### Memória crescendo

1. Limite histórico de métricas (padrão: 1000 eventos)
2. Limpe periodicamente com `manager.clear()`
3. Use persistência com Supabase e `clear()` frequente

## API Reference

### SyncQueueManager

#### Constructor

```typescript
new SyncQueueManager<T>(config?: {
  maxBatchSize?: number;
  retryPolicy?: Partial<RetryPolicy>;
  processingIntervalMs?: number;
})
```

#### Métodos

- `enqueue(data: T, priority?: QueuePriority, metadata?: object): Promise<boolean>`
  - Adiciona item à fila
  - Retorna false se duplicado
  
- `startProcessing(): void`
  - Inicia processamento contínuo
  
- `stopProcessing(): void`
  - Para processamento contínuo
  
- `processBatch(): Promise<number>`
  - Processa um batch manualmente
  
- `onProcess(callback: (item) => Promise<void>): void`
  - Define callback de processamento
  
- `getQueueSize(): number`
  - Tamanho atual da fila
  
- `getDeadLetterQueueSize(): number`
  - Tamanho da dead letter queue
  
- `getDeadLetterItems(limit?: number): SyncQueueItem[]`
  - Retorna items da DLQ
  
- `removeFromDeadLetterQueue(itemId: string): boolean`
  - Remove item da DLQ
  
- `getItem(itemId: string): SyncQueueItem | null`
  - Busca item por ID
  
- `getMetrics(): QueueMetrics`
  - Métricas estruturadas
  
- `getPrometheusMetrics(): string`
  - Métricas em formato Prometheus
  
- `clear(): void`
  - Limpa fila e DLQ
  
- `destroy(): void`
  - Cleanup e encerramento

## Exemplos

### Sincronização de Agents

```typescript
const agentQueue = new SyncQueueManager<AgentPayload>();

agentQueue.onProcess(async (item) => {
  await updateAgentRegistry(item.data);
});

// Quando agent é atualizado
await agentQueue.enqueue(agentData, QueuePriority.HIGH);
```

### Sincronização de Dados

```typescript
const syncQueue = new SupabaseSyncQueue({
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseKey: process.env.SUPABASE_ANON_KEY,
});

syncQueue.setProcessingCallback(async (payload) => {
  await api.sync(payload);
});

syncQueue.startProcessing();
```

### Webhook Processing

```typescript
app.post('/webhooks/github', async (req, res) => {
  await syncQueue.enqueue(
    req.body,
    QueuePriority.MEDIUM,
    { source: 'github', correlationId: req.headers['x-github-delivery'] }
  );
  res.json({ ok: true });
});
```

## License

MIT

## Versão

1.0.0
