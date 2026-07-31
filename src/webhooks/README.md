# Cowork Webhook Handler

Production-ready webhook handler for Cowork events with HMAC-SHA256 signature validation, async queueing, exponential backoff retry logic, and comprehensive audit logging.

## Features

- **HMAC-SHA256 Signature Validation**: Ensures webhook authenticity
- **Async Event Processing**: Non-blocking queue-based processing
- **Exponential Backoff Retries**: Configurable retry logic with jitter
- **Audit Logging**: Complete event lifecycle tracking
- **Event Types**: PR_OPENED, COMMIT, TASK_UPDATED
- **Type-Safe**: Full TypeScript support
- **Express Integration**: Ready-to-use middleware

## Installation

```bash
npm install
```

## Quick Start

### Basic Setup

```typescript
import { CoworkWebhookHandler, WebhookEventType } from './webhooks';
import pino from 'pino';

const handler = new CoworkWebhookHandler({
  secret: process.env.WEBHOOK_SECRET!,
  logger: pino(),
  maxRetries: 3,
  initialBackoffMs: 1000,
  maxBackoffMs: 30000,
});

handler.on(WebhookEventType.PR_OPENED, async (payload) => {
  console.log('PR opened:', payload.data);
});

handler.on(WebhookEventType.COMMIT, async (payload) => {
  console.log('Commit received:', payload.data);
});

handler.on(WebhookEventType.TASK_UPDATED, async (payload) => {
  console.log('Task updated:', payload.data);
});
```

### Express Integration

```typescript
import express from 'express';
import { setupWebhookRoutes, rawJsonMiddleware } from './webhooks/express-integration';

const app = express();

app.use(rawJsonMiddleware());

const webhookHandler = setupWebhookRoutes(
  app,
  process.env.WEBHOOK_SECRET!,
  logger
);

app.listen(3000, () => {
  console.log('Webhook server listening on port 3000');
});
```

### Sending Webhooks

```bash
#!/bin/bash

SECRET="your-webhook-secret"
EVENT_TYPE="pr.opened"
PAYLOAD='{"event":"pr.opened","data":{"pr_id":"123","title":"Fix bug"}}'

SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" -hex | cut -d' ' -f2)

curl -X POST http://localhost:3000/webhooks/cowork \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

## API Reference

### CoworkWebhookHandler

#### Constructor

```typescript
new CoworkWebhookHandler({
  secret: string;              // HMAC secret key
  maxRetries?: number;         // Default: 3
  initialBackoffMs?: number;   // Default: 1000
  maxBackoffMs?: number;       // Default: 30000
  auditLogPath?: string;       // Optional file path
  logger?: pino.Logger;        // Optional logger
})
```

#### Methods

```typescript
// Register event handler
handler.on(WebhookEventType.PR_OPENED, async (payload) => {
  // Handle event
});

// Unregister event handler
handler.off(WebhookEventType.PR_OPENED, handler);

// Process incoming webhook
const result = await handler.handleWebhook(payload, signature, ipAddress);
// Returns: { success: boolean; deliveryId: string; error?: string }

// Validate signature
const isValid = handler.validateSignature(payload, signature);

// Get queue status
const queueSize = handler.getQueueSize();

// Get audit log
const auditLog = handler.getAuditLog(limit?: number);

// Clear audit log
handler.clearAuditLog();

// Get full status
const status = handler.getStatus();
// Returns: {
//   processing: boolean;
//   queueSize: number;
//   auditLogSize: number;
//   handlerCount: Record<WebhookEventType, number>;
// }
```

#### Events

```typescript
// Emitted when payload is enqueued
handler.on('enqueued', (payload) => {});

// Emitted when payload is processed successfully
handler.on('processed', (payload) => {});

// Emitted when payload processing fails after all retries
handler.on('failed', (payload, error) => {});
```

## Webhook Events

### PR_OPENED

```typescript
handler.on(WebhookEventType.PR_OPENED, async (payload) => {
  const { pr_id, title, author, target_branch } = payload.data;
});
```

### COMMIT

```typescript
handler.on(WebhookEventType.COMMIT, async (payload) => {
  const { commit_sha, message, author, timestamp } = payload.data;
});
```

### TASK_UPDATED

```typescript
handler.on(WebhookEventType.TASK_UPDATED, async (payload) => {
  const { task_id, status, assignee, changes } = payload.data;
});
```

## Audit Log Format

```typescript
{
  timestamp: string;           // ISO 8601
  deliveryId: string;          // Unique delivery ID
  event: WebhookEventType;     // Event type
  status: 'received' | 'validated' | 'queued' | 'processing' | 'success' | 'failed' | 'retrying';
  statusCode?: number;         // HTTP status if applicable
  duration?: number;           // Processing time in ms
  error?: string;              // Error message if failed
  retryCount?: number;         // Current retry count
  userId?: string;             // User ID if available
  ipAddress?: string;          // Source IP address
}
```

## Express Routes

### POST /webhooks/cowork

Receives webhook payload. Requires `X-Webhook-Signature` header.

**Response (202 Accepted):**
```json
{
  "success": true,
  "deliveryId": "dlv_1234567890_abcdef",
  "message": "Webhook queued for processing"
}
```

### GET /webhooks/status

Returns webhook handler status.

**Response:**
```json
{
  "processing": false,
  "queueSize": 0,
  "auditLogSize": 42,
  "handlerCount": {
    "pr.opened": 1,
    "commit": 1,
    "task.updated": 1
  }
}
```

### GET /webhooks/audit-log?limit=100

Returns audit log entries (default limit: 100).

**Response:**
```json
{
  "entries": [...],
  "total": 42
}
```

### GET /health/webhooks

Health check endpoint.

**Response (200 OK):**
```json
{
  "healthy": true,
  "processing": false,
  "queueSize": 0
}
```

## Configuration

### Environment Variables

```bash
WEBHOOK_SECRET="your-hmac-secret-key"
WEBHOOK_MAX_RETRIES=3
WEBHOOK_INITIAL_BACKOFF_MS=1000
WEBHOOK_MAX_BACKOFF_MS=30000
```

### Retry Strategy

Default exponential backoff with jitter:
- Retry 1: ~1000ms (±10%)
- Retry 2: ~2000ms (±10%)
- Retry 3: ~4000ms (±10%)

Jitter prevents thundering herd problem.

## Testing

```bash
npm test
npm run test:watch
npm run test:coverage
```

## Production Checklist

- [ ] Set strong `WEBHOOK_SECRET` (32+ characters)
- [ ] Configure appropriate `maxRetries` for your use case
- [ ] Set up audit log file path for persistence
- [ ] Monitor `/health/webhooks` endpoint
- [ ] Configure log aggregation for Pino logger
- [ ] Set up alerting for failed webhooks
- [ ] Test signature validation with production secret
- [ ] Load test with expected webhook volume
- [ ] Implement graceful shutdown in your app
- [ ] Set up database backups if using persistent storage

## Performance Considerations

- Queue processes in a non-blocking loop (100ms intervals)
- Default settings handle 100+ webhooks/second
- Audit log kept in memory (last 10,000 entries)
- Optional file-based persistence for long-term audit trail
- Each handler execution is isolated via Promise.allSettled()

## Error Handling

The handler gracefully handles:
- Invalid signatures (rejected, logged)
- Malformed JSON (rejected, logged)
- Unknown event types (rejected, logged)
- Handler failures (retried with backoff)
- Signature timing attacks (constant-time comparison)

## Security

- HMAC-SHA256 validation on all webhooks
- Timing-safe signature comparison
- No sensitive data in logs by default
- IP address logging for audit trail
- Separate audit log with full event lifecycle
