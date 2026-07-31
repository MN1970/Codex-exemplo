import crypto from 'crypto';
import { CoworkWebhookHandler, WebhookEventType, WebhookPayload } from '../cowork-webhook';
import pino from 'pino';

describe('CoworkWebhookHandler', () => {
  let handler: CoworkWebhookHandler;
  const secret = 'test-secret-key-12345';
  const logger = pino({ level: 'silent' });

  beforeEach(() => {
    handler = new CoworkWebhookHandler({
      secret,
      logger,
      maxRetries: 2,
      initialBackoffMs: 100,
      maxBackoffMs: 500,
    });
  });

  describe('Signature Validation', () => {
    test('validates correct HMAC-SHA256 signature', () => {
      const payload = JSON.stringify({ event: WebhookEventType.PR_OPENED, data: {} });
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      const isValid = handler.validateSignature(payload, signature);
      expect(isValid).toBe(true);
    });

    test('rejects invalid signature', () => {
      const payload = JSON.stringify({ event: WebhookEventType.PR_OPENED, data: {} });
      const invalidSignature = 'invalid-signature-12345';

      const isValid = handler.validateSignature(payload, invalidSignature);
      expect(isValid).toBe(false);
    });

    test('rejects tampered payload', () => {
      const payload = JSON.stringify({ event: WebhookEventType.PR_OPENED, data: {} });
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      const tamperedPayload = JSON.stringify({ event: WebhookEventType.COMMIT, data: { extra: 'field' } });

      const isValid = handler.validateSignature(tamperedPayload, signature);
      expect(isValid).toBe(false);
    });
  });

  describe('Webhook Handling', () => {
    test('successfully handles valid webhook', async () => {
      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      const result = await handler.handleWebhook(payload, signature);

      expect(result.success).toBe(true);
      expect(result.deliveryId).toBeDefined();
    });

    test('rejects webhook with invalid signature', async () => {
      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const invalidSignature = 'invalid-sig';

      const result = await handler.handleWebhook(payload, invalidSignature);

      expect(result.success).toBe(false);
      expect(result.error).toContain('signature');
    });

    test('rejects webhook with invalid JSON', async () => {
      const payload = '{invalid json}';
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      const result = await handler.handleWebhook(payload, signature);

      expect(result.success).toBe(false);
      expect(result.error).toContain('JSON');
    });

    test('rejects webhook with unknown event type', async () => {
      const data = { event: 'unknown.event', data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      const result = await handler.handleWebhook(payload, signature);

      expect(result.success).toBe(false);
      expect(result.error).toContain('event type');
    });
  });

  describe('Event Handling', () => {
    test('registers and calls handler for PR_OPENED event', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.PR_OPENED, mockHandler);

      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      // Wait for queue processing
      await new Promise(resolve => setTimeout(resolve, 200));

      expect(mockHandler).toHaveBeenCalled();
      const callArg = mockHandler.mock.calls[0][0] as WebhookPayload;
      expect(callArg.event).toBe(WebhookEventType.PR_OPENED);
    });

    test('registers and calls handler for COMMIT event', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.COMMIT, mockHandler);

      const data = { event: WebhookEventType.COMMIT, data: { commit_sha: 'abc123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      await new Promise(resolve => setTimeout(resolve, 200));

      expect(mockHandler).toHaveBeenCalled();
    });

    test('registers and calls handler for TASK_UPDATED event', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.TASK_UPDATED, mockHandler);

      const data = { event: WebhookEventType.TASK_UPDATED, data: { task_id: 'task-123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      await new Promise(resolve => setTimeout(resolve, 200));

      expect(mockHandler).toHaveBeenCalled();
    });

    test('calls multiple handlers for same event', async () => {
      const handler1 = jest.fn().mockResolvedValue(undefined);
      const handler2 = jest.fn().mockResolvedValue(undefined);

      handler.on(WebhookEventType.PR_OPENED, handler1);
      handler.on(WebhookEventType.PR_OPENED, handler2);

      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      await new Promise(resolve => setTimeout(resolve, 200));

      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
    });

    test('removes handler with off()', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.PR_OPENED, mockHandler);
      handler.off(WebhookEventType.PR_OPENED, mockHandler);

      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      await new Promise(resolve => setTimeout(resolve, 200));

      expect(mockHandler).not.toHaveBeenCalled();
    });
  });

  describe('Retry Logic', () => {
    test('retries failed handler with exponential backoff', async () => {
      const mockHandler = jest
        .fn()
        .mockRejectedValueOnce(new Error('First failure'))
        .mockResolvedValueOnce(undefined);

      handler.on(WebhookEventType.PR_OPENED, mockHandler);

      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      // Wait for initial processing
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(mockHandler).toHaveBeenCalledTimes(1);

      // Wait for retry
      await new Promise(resolve => setTimeout(resolve, 300));

      expect(mockHandler).toHaveBeenCalledTimes(2);
    });

    test('fails after max retries exceeded', async () => {
      const mockHandler = jest.fn().mockRejectedValue(new Error('Always fails'));

      handler.on(WebhookEventType.PR_OPENED, mockHandler);

      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      const failedPromise = new Promise<void>(resolve => {
        handler.on('failed', () => {
          resolve();
        });
      });

      await handler.handleWebhook(payload, signature);

      await failedPromise;

      // Should be called: initial + 2 retries = 3 times
      expect(mockHandler).toHaveBeenCalledTimes(3);
    });
  });

  describe('Queue Management', () => {
    test('enqueues payloads for processing', async () => {
      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      expect(handler.getQueueSize()).toBeGreaterThan(0);

      await new Promise(resolve => setTimeout(resolve, 200));

      expect(handler.getQueueSize()).toBe(0);
    });

    test('processes multiple queued items', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.PR_OPENED, mockHandler);

      const data1 = { event: WebhookEventType.PR_OPENED, data: { pr_id: '1' } };
      const data2 = { event: WebhookEventType.PR_OPENED, data: { pr_id: '2' } };

      const payload1 = JSON.stringify(data1);
      const payload2 = JSON.stringify(data2);

      const signature1 = crypto
        .createHmac('sha256', secret)
        .update(payload1)
        .digest('hex');

      const signature2 = crypto
        .createHmac('sha256', secret)
        .update(payload2)
        .digest('hex');

      await handler.handleWebhook(payload1, signature1);
      await handler.handleWebhook(payload2, signature2);

      expect(handler.getQueueSize()).toBe(2);

      await new Promise(resolve => setTimeout(resolve, 300));

      expect(handler.getQueueSize()).toBe(0);
      expect(mockHandler).toHaveBeenCalledTimes(2);
    });
  });

  describe('Audit Logging', () => {
    test('logs audit entries for webhook processing', async () => {
      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      await new Promise(resolve => setTimeout(resolve, 200));

      const auditLog = handler.getAuditLog();

      expect(auditLog.length).toBeGreaterThan(0);
      expect(auditLog[0].event).toBe(WebhookEventType.PR_OPENED);
      expect(auditLog[0].status).toBe('received');
    });

    test('includes all status transitions in audit log', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.PR_OPENED, mockHandler);

      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      await handler.handleWebhook(payload, signature);

      await new Promise(resolve => setTimeout(resolve, 200));

      const auditLog = handler.getAuditLog();
      const statuses = auditLog.map(entry => entry.status);

      expect(statuses).toContain('received');
      expect(statuses).toContain('validated');
      expect(statuses).toContain('queued');
      expect(statuses).toContain('processing');
      expect(statuses).toContain('success');
    });

    test('clears audit log', () => {
      const data = { event: WebhookEventType.PR_OPENED, data: { pr_id: '123' } };
      const payload = JSON.stringify(data);
      const signature = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');

      handler.handleWebhook(payload, signature);

      let auditLog = handler.getAuditLog();
      expect(auditLog.length).toBeGreaterThan(0);

      handler.clearAuditLog();
      auditLog = handler.getAuditLog();
      expect(auditLog.length).toBe(0);
    });
  });

  describe('Status', () => {
    test('reports correct status', async () => {
      const mockHandler = jest.fn().mockResolvedValue(undefined);
      handler.on(WebhookEventType.PR_OPENED, mockHandler);
      handler.on(WebhookEventType.COMMIT, mockHandler);

      const status = handler.getStatus();

      expect(status.processing).toBe(false);
      expect(status.queueSize).toBe(0);
      expect(status.auditLogSize).toBeGreaterThan(0);
      expect(status.handlerCount[WebhookEventType.PR_OPENED]).toBe(1);
      expect(status.handlerCount[WebhookEventType.COMMIT]).toBe(1);
      expect(status.handlerCount[WebhookEventType.TASK_UPDATED]).toBe(0);
    });
  });
});
