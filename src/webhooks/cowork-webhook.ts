import * as crypto from 'crypto';
import { EventEmitter } from 'events';
import pino from 'pino';

/**
 * Webhook event types
 */
export enum WebhookEventType {
  PR_OPENED = 'pr.opened',
  COMMIT = 'commit',
  TASK_UPDATED = 'task.updated',
}

/**
 * Webhook payload interface
 */
export interface WebhookPayload {
  event: WebhookEventType;
  timestamp: string;
  deliveryId: string;
  signature: string;
  data: Record<string, unknown>;
  retryCount?: number;
}

/**
 * Audit log entry
 */
export interface AuditLogEntry {
  timestamp: string;
  deliveryId: string;
  event: WebhookEventType;
  status: 'received' | 'validated' | 'queued' | 'processing' | 'success' | 'failed' | 'retrying';
  statusCode?: number;
  duration?: number;
  error?: string;
  retryCount?: number;
  userId?: string;
  ipAddress?: string;
}

/**
 * Webhook configuration
 */
export interface WebhookConfig {
  secret: string;
  maxRetries?: number;
  initialBackoffMs?: number;
  maxBackoffMs?: number;
  auditLogPath?: string;
  logger?: pino.Logger;
}

/**
 * Processing queue entry
 */
interface QueueEntry {
  payload: WebhookPayload;
  retryCount: number;
  timestamp: number;
}

/**
 * Handler function type
 */
export type WebhookHandler = (payload: WebhookPayload) => Promise<void>;

/**
 * Cowork Webhook Handler
 * Processes webhooks with signature validation, async queueing, retry logic, and audit logging
 */
export class CoworkWebhookHandler extends EventEmitter {
  private secret: string;
  private maxRetries: number;
  private initialBackoffMs: number;
  private maxBackoffMs: number;
  private logger: pino.Logger;
  private queue: QueueEntry[] = [];
  private processing: boolean = false;
  private handlers: Map<WebhookEventType, WebhookHandler[]> = new Map();
  private auditLog: AuditLogEntry[] = [];
  private auditLogPath: string | undefined;

  constructor(config: WebhookConfig) {
    super();

    this.secret = config.secret;
    this.maxRetries = config.maxRetries ?? 3;
    this.initialBackoffMs = config.initialBackoffMs ?? 1000;
    this.maxBackoffMs = config.maxBackoffMs ?? 30000;
    this.auditLogPath = config.auditLogPath;
    this.logger = config.logger ?? pino({ level: 'info' });

    // Initialize handlers map
    Object.values(WebhookEventType).forEach(event => {
      this.handlers.set(event, []);
    });

    // Start queue processor
    this.startQueueProcessor();
  }

  /**
   * Validates HMAC-SHA256 signature
   */
  validateSignature(payload: string, signature: string): boolean {
    try {
      const expectedSignature = crypto
        .createHmac('sha256', this.secret)
        .update(payload)
        .digest('hex');

      return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
    } catch (error) {
      this.logger.error({ error }, 'Signature validation error');
      return false;
    }
  }

  /**
   * Handles incoming webhook request
   */
  async handleWebhook(
    payload: string,
    signature: string,
    ipAddress?: string
  ): Promise<{ success: boolean; deliveryId: string; error?: string }> {
    const deliveryId = this.generateDeliveryId();
    const receiveTime = Date.now();

    try {
      // Log receipt
      this.logAudit({
        timestamp: new Date().toISOString(),
        deliveryId,
        event: 'commit' as WebhookEventType,
        status: 'received',
        ipAddress,
      });

      // Validate signature
      if (!this.validateSignature(payload, signature)) {
        this.logAudit({
          timestamp: new Date().toISOString(),
          deliveryId,
          event: 'commit' as WebhookEventType,
          status: 'failed',
          error: 'Invalid signature',
          ipAddress,
          duration: Date.now() - receiveTime,
        });

        this.logger.warn({ deliveryId, ipAddress }, 'Webhook signature validation failed');
        return {
          success: false,
          deliveryId,
          error: 'Invalid signature',
        };
      }

      // Parse payload
      let parsedPayload: WebhookPayload;
      try {
        const data = JSON.parse(payload);
        parsedPayload = {
          ...data,
          deliveryId,
          signature,
          timestamp: new Date().toISOString(),
        };
      } catch (error) {
        this.logAudit({
          timestamp: new Date().toISOString(),
          deliveryId,
          event: 'commit' as WebhookEventType,
          status: 'failed',
          error: 'Invalid JSON payload',
          ipAddress,
          duration: Date.now() - receiveTime,
        });

        this.logger.error({ error, deliveryId }, 'Failed to parse webhook payload');
        return {
          success: false,
          deliveryId,
          error: 'Invalid JSON payload',
        };
      }

      // Validate event type
      if (!Object.values(WebhookEventType).includes(parsedPayload.event)) {
        this.logAudit({
          timestamp: new Date().toISOString(),
          deliveryId,
          event: parsedPayload.event as WebhookEventType,
          status: 'failed',
          error: 'Unknown event type',
          ipAddress,
          duration: Date.now() - receiveTime,
        });

        this.logger.warn({ event: parsedPayload.event, deliveryId }, 'Unknown webhook event type');
        return {
          success: false,
          deliveryId,
          error: 'Unknown event type',
        };
      }

      // Log validation success
      this.logAudit({
        timestamp: new Date().toISOString(),
        deliveryId,
        event: parsedPayload.event,
        status: 'validated',
        ipAddress,
      });

      // Enqueue for processing
      this.enqueuePayload(parsedPayload);

      // Log enqueued
      this.logAudit({
        timestamp: new Date().toISOString(),
        deliveryId,
        event: parsedPayload.event,
        status: 'queued',
        ipAddress,
        duration: Date.now() - receiveTime,
      });

      this.logger.info(
        { deliveryId, event: parsedPayload.event, queueSize: this.queue.length },
        'Webhook enqueued for processing'
      );

      return {
        success: true,
        deliveryId,
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error({ error, deliveryId }, 'Webhook handling error');

      this.logAudit({
        timestamp: new Date().toISOString(),
        deliveryId,
        event: 'commit' as WebhookEventType,
        status: 'failed',
        error: errorMessage,
        ipAddress,
        duration: Date.now() - receiveTime,
      });

      return {
        success: false,
        deliveryId,
        error: errorMessage,
      };
    }
  }

  /**
   * Registers a handler for a specific event type
   */
  on(event: WebhookEventType, handler: WebhookHandler): this {
    const handlers = this.handlers.get(event) || [];
    handlers.push(handler);
    this.handlers.set(event, handlers);
    return this;
  }

  /**
   * Removes a handler for a specific event type
   */
  off(event: WebhookEventType, handler: WebhookHandler): this {
    const handlers = this.handlers.get(event) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
    return this;
  }

  /**
   * Gets current queue size
   */
  getQueueSize(): number {
    return this.queue.length;
  }

  /**
   * Gets audit log
   */
  getAuditLog(limit?: number): AuditLogEntry[] {
    if (limit) {
      return this.auditLog.slice(-limit);
    }
    return [...this.auditLog];
  }

  /**
   * Clears audit log
   */
  clearAuditLog(): void {
    this.auditLog = [];
  }

  /**
   * Gets processing status
   */
  getStatus(): {
    processing: boolean;
    queueSize: number;
    auditLogSize: number;
    handlerCount: Record<WebhookEventType, number>;
  } {
    const handlerCount: Record<WebhookEventType, number> = {} as Record<WebhookEventType, number>;
    Object.values(WebhookEventType).forEach(event => {
      handlerCount[event] = this.handlers.get(event)?.length || 0;
    });

    return {
      processing: this.processing,
      queueSize: this.queue.length,
      auditLogSize: this.auditLog.length,
      handlerCount,
    };
  }

  /**
   * Private: Enqueues payload for processing
   */
  private enqueuePayload(payload: WebhookPayload): void {
    this.queue.push({
      payload,
      retryCount: 0,
      timestamp: Date.now(),
    });

    this.emit('enqueued', payload);
  }

  /**
   * Private: Starts the queue processor
   */
  private startQueueProcessor(): void {
    setInterval(() => {
      if (!this.processing && this.queue.length > 0) {
        this.processQueue();
      }
    }, 100);
  }

  /**
   * Private: Processes queue entries
   */
  private async processQueue(): Promise<void> {
    if (this.processing || this.queue.length === 0) {
      return;
    }

    this.processing = true;

    try {
      while (this.queue.length > 0) {
        const entry = this.queue.shift();
        if (!entry) {
          break;
        }

        await this.processEntry(entry);
      }
    } finally {
      this.processing = false;
    }
  }

  /**
   * Private: Processes a single queue entry
   */
  private async processEntry(entry: QueueEntry): Promise<void> {
    const { payload, retryCount } = entry;
    const startTime = Date.now();

    try {
      this.logAudit({
        timestamp: new Date().toISOString(),
        deliveryId: payload.deliveryId,
        event: payload.event,
        status: 'processing',
        retryCount,
      });

      const handlers = this.handlers.get(payload.event) || [];

      if (handlers.length === 0) {
        this.logger.warn(
          { event: payload.event, deliveryId: payload.deliveryId },
          'No handlers registered for webhook event'
        );

        this.logAudit({
          timestamp: new Date().toISOString(),
          deliveryId: payload.deliveryId,
          event: payload.event,
          status: 'success',
          duration: Date.now() - startTime,
          retryCount,
        });

        this.emit('processed', payload);
        return;
      }

      // Execute all handlers
      const results = await Promise.allSettled(handlers.map(handler => handler(payload)));

      const failed = results.some(result => result.status === 'rejected');

      if (failed) {
        throw new Error('One or more handlers failed');
      }

      this.logAudit({
        timestamp: new Date().toISOString(),
        deliveryId: payload.deliveryId,
        event: payload.event,
        status: 'success',
        duration: Date.now() - startTime,
        retryCount,
      });

      this.logger.info(
        { deliveryId: payload.deliveryId, event: payload.event, duration: Date.now() - startTime },
        'Webhook processed successfully'
      );

      this.emit('processed', payload);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const shouldRetry = retryCount < this.maxRetries;

      this.logger.error(
        {
          deliveryId: payload.deliveryId,
          event: payload.event,
          error,
          retryCount,
          shouldRetry,
        },
        'Error processing webhook'
      );

      if (shouldRetry) {
        const backoffMs = this.calculateBackoff(retryCount);

        this.logAudit({
          timestamp: new Date().toISOString(),
          deliveryId: payload.deliveryId,
          event: payload.event,
          status: 'retrying',
          error: errorMessage,
          retryCount,
          duration: Date.now() - startTime,
        });

        this.logger.info(
          {
            deliveryId: payload.deliveryId,
            event: payload.event,
            retryCount: retryCount + 1,
            backoffMs,
          },
          'Webhook processing failed, retrying'
        );

        // Re-enqueue with delay
        setTimeout(() => {
          this.queue.unshift({
            payload: {
              ...payload,
              retryCount: retryCount + 1,
            },
            retryCount: retryCount + 1,
            timestamp: Date.now(),
          });
        }, backoffMs);
      } else {
        this.logAudit({
          timestamp: new Date().toISOString(),
          deliveryId: payload.deliveryId,
          event: payload.event,
          status: 'failed',
          error: errorMessage,
          retryCount,
          duration: Date.now() - startTime,
        });

        this.logger.error(
          {
            deliveryId: payload.deliveryId,
            event: payload.event,
            retryCount,
          },
          'Webhook processing failed after max retries'
        );

        this.emit('failed', payload, errorMessage);
      }
    }
  }

  /**
   * Private: Calculates exponential backoff
   */
  private calculateBackoff(retryCount: number): number {
    const backoff = Math.min(
      this.initialBackoffMs * Math.pow(2, retryCount),
      this.maxBackoffMs
    );

    // Add jitter (±10%)
    const jitter = backoff * 0.1 * (Math.random() - 0.5) * 2;
    return Math.max(backoff + jitter, this.initialBackoffMs);
  }

  /**
   * Private: Generates a unique delivery ID
   */
  private generateDeliveryId(): string {
    return `dlv_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
  }

  /**
   * Private: Logs audit entry
   */
  private logAudit(entry: AuditLogEntry): void {
    this.auditLog.push(entry);

    // Keep last 10000 entries
    if (this.auditLog.length > 10000) {
      this.auditLog = this.auditLog.slice(-10000);
    }

    // Write to file if configured
    if (this.auditLogPath) {
      this.writeAuditLogFile(entry);
    }

    this.logger.debug(entry, 'Audit log entry');
  }

  /**
   * Private: Writes audit log entry to file (async, non-blocking)
   */
  private writeAuditLogFile(entry: AuditLogEntry): void {
    // Async write to avoid blocking the main thread
    setImmediate(() => {
      try {
        // In production, use proper file system operations
        // This is a placeholder for the actual implementation
        if (this.auditLogPath) {
          // fs.appendFileSync(this.auditLogPath, JSON.stringify(entry) + '\n');
        }
      } catch (error) {
        this.logger.error({ error }, 'Failed to write audit log file');
      }
    });
  }
}

/**
 * Express middleware factory for webhook handling
 */
export function createWebhookMiddleware(handler: CoworkWebhookHandler) {
  return async (
    req: {
      body?: string | object;
      headers?: Record<string, string | string[] | undefined>;
      ip?: string;
    },
    res: {
      status(code: number): { json(data: unknown): void };
      json(data: unknown): void;
      sendStatus(code: number): void;
    }
  ) => {
    const signature = (req.headers?.['x-webhook-signature'] as string) || '';
    const payload = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    const ipAddress = req.ip || '';

    const result = await handler.handleWebhook(payload, signature, ipAddress);

    if (result.success) {
      res.status(200).json({ success: true, deliveryId: result.deliveryId });
    } else {
      res.status(400).json({ success: false, error: result.error, deliveryId: result.deliveryId });
    }
  };
}

export default CoworkWebhookHandler;
