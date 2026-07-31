import { Request, Response, Express } from 'express';
import { CoworkWebhookHandler, WebhookEventType } from './cowork-webhook';
import pino from 'pino';

/**
 * Sets up webhook routes on Express app
 */
export function setupWebhookRoutes(
  app: Express,
  webhookSecret: string,
  logger?: pino.Logger
): CoworkWebhookHandler {
  const log = logger || pino({ level: 'info' });

  const handler = new CoworkWebhookHandler({
    secret: webhookSecret,
    logger: log,
    maxRetries: 3,
    initialBackoffMs: 1000,
    maxBackoffMs: 30000,
  });

  // Register event handlers
  handler.on(WebhookEventType.PR_OPENED, async payload => {
    log.info({ deliveryId: payload.deliveryId }, 'Processing PR_OPENED event');
    // Handle PR opened
  });

  handler.on(WebhookEventType.COMMIT, async payload => {
    log.info({ deliveryId: payload.deliveryId }, 'Processing COMMIT event');
    // Handle commit
  });

  handler.on(WebhookEventType.TASK_UPDATED, async payload => {
    log.info({ deliveryId: payload.deliveryId }, 'Processing TASK_UPDATED event');
    // Handle task update
  });

  // Webhook endpoint
  app.post('/webhooks/cowork', async (req: Request, res: Response) => {
    const signature = req.headers['x-webhook-signature'] as string;

    if (!signature) {
      res.status(400).json({ error: 'Missing webhook signature' });
      return;
    }

    const payload = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    const ipAddress = req.ip || 'unknown';

    const result = await handler.handleWebhook(payload, signature, ipAddress);

    if (result.success) {
      res.status(202).json({
        success: true,
        deliveryId: result.deliveryId,
        message: 'Webhook queued for processing',
      });
    } else {
      res.status(400).json({
        success: false,
        deliveryId: result.deliveryId,
        error: result.error,
      });
    }
  });

  // Status endpoint
  app.get('/webhooks/status', (_req: Request, res: Response) => {
    const status = handler.getStatus();
    res.json(status);
  });

  // Audit log endpoint
  app.get('/webhooks/audit-log', (req: Request, res: Response) => {
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 100;
    const auditLog = handler.getAuditLog(limit);
    res.json({ entries: auditLog, total: auditLog.length });
  });

  // Health check endpoint
  app.get('/health/webhooks', (_req: Request, res: Response) => {
    const status = handler.getStatus();
    const isHealthy = status.queueSize < 1000 && !status.processing;

    res.status(isHealthy ? 200 : 503).json({
      healthy: isHealthy,
      processing: status.processing,
      queueSize: status.queueSize,
    });
  });

  log.info('Webhook routes configured');

  return handler;
}

/**
 * Raw request middleware for parsing JSON bodies as strings
 */
export function rawJsonMiddleware() {
  return (req: Request, res: Response, next: () => void) => {
    let rawBody = '';

    req.on('data', chunk => {
      rawBody += chunk.toString();
    });

    req.on('end', () => {
      req.body = rawBody;
      next();
    });
  };
}

export default setupWebhookRoutes;
