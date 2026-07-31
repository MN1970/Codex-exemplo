/**
 * Example Cowork Webhook Server
 *
 * Usage:
 *   WEBHOOK_SECRET="your-secret" npx ts-node src/webhooks/example-server.ts
 */

import express from 'express';
import { setupWebhookRoutes, rawJsonMiddleware } from './express-integration';
import { WebhookEventType } from './cowork-webhook';
import pino from 'pino';

const logger = pino({ level: 'info' });
const app = express();

const webhookSecret = process.env.WEBHOOK_SECRET;

if (!webhookSecret) {
  logger.error('WEBHOOK_SECRET environment variable is required');
  process.exit(1);
}

// Middleware
app.use(rawJsonMiddleware());

// Setup webhook handler and routes
const webhookHandler = setupWebhookRoutes(app, webhookSecret, logger);

// Event handlers
webhookHandler.on(WebhookEventType.PR_OPENED, async payload => {
  logger.info(
    {
      deliveryId: payload.deliveryId,
      pr_id: payload.data.pr_id,
      title: payload.data.title,
    },
    'PR opened event received'
  );

  // Example: Send notification
  // await notificationService.send({
  //   type: 'pr_opened',
  //   pr_id: payload.data.pr_id,
  //   title: payload.data.title,
  // });
});

webhookHandler.on(WebhookEventType.COMMIT, async payload => {
  logger.info(
    {
      deliveryId: payload.deliveryId,
      commit_sha: payload.data.commit_sha,
      message: payload.data.message,
    },
    'Commit event received'
  );

  // Example: Trigger CI/CD
  // await cicdService.trigger({
  //   commit_sha: payload.data.commit_sha,
  //   branch: payload.data.branch,
  // });
});

webhookHandler.on(WebhookEventType.TASK_UPDATED, async payload => {
  logger.info(
    {
      deliveryId: payload.deliveryId,
      task_id: payload.data.task_id,
      status: payload.data.status,
    },
    'Task updated event received'
  );

  // Example: Update project management system
  // await pmService.updateTask({
  //   task_id: payload.data.task_id,
  //   status: payload.data.status,
  //   assignee: payload.data.assignee,
  // });
});

// Listen for webhook events
(webhookHandler as any).on('processed', (payload: any) => {
  logger.debug({ deliveryId: payload.deliveryId }, 'Webhook processed successfully');
});

(webhookHandler as any).on('failed', (payload: any, error: any) => {
  logger.error(
    { deliveryId: payload.deliveryId, error },
    'Webhook processing failed after retries'
  );
});

// Root endpoint
app.get('/', (_req, res) => {
  res.json({
    name: 'Cowork Webhook Server',
    version: '1.0.0',
    endpoints: {
      webhook: 'POST /webhooks/cowork',
      status: 'GET /webhooks/status',
      auditLog: 'GET /webhooks/audit-log?limit=100',
      health: 'GET /health/webhooks',
    },
  });
});

// Start server
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  logger.info({ port: PORT }, 'Cowork webhook server started');
  logger.info('Endpoints:');
  logger.info('  Webhook:    POST http://localhost:3000/webhooks/cowork');
  logger.info('  Status:     GET  http://localhost:3000/webhooks/status');
  logger.info('  Audit Log:  GET  http://localhost:3000/webhooks/audit-log');
  logger.info('  Health:     GET  http://localhost:3000/health/webhooks');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  const status = webhookHandler.getStatus();
  logger.info({ status }, 'Final handler status');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  const status = webhookHandler.getStatus();
  logger.info({ status }, 'Final handler status');
  process.exit(0);
});

export default app;
