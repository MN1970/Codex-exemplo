/**
 * Extended type definitions for Cowork webhooks
 */

import { WebhookPayload, WebhookEventType } from './cowork-webhook';

/**
 * PR Opened Event Data
 */
export interface PROpenedData {
  pr_id: string;
  title: string;
  author: string;
  description?: string;
  target_branch: string;
  source_branch?: string;
  repository?: string;
  created_at?: string;
}

/**
 * PR Opened Webhook Payload
 */
export interface PROpenedPayload extends Omit<WebhookPayload, 'data'> {
  event: WebhookEventType.PR_OPENED;
  data: PROpenedData;
}

/**
 * Commit Event Data
 */
export interface CommitData {
  commit_sha: string;
  message: string;
  author: string;
  author_email?: string;
  branch: string;
  repository?: string;
  timestamp?: string;
  files_changed?: number;
  additions?: number;
  deletions?: number;
}

/**
 * Commit Webhook Payload
 */
export interface CommitPayload extends Omit<WebhookPayload, 'data'> {
  event: WebhookEventType.COMMIT;
  data: CommitData;
}

/**
 * Task Updated Event Data
 */
export interface TaskUpdatedData {
  task_id: string;
  title?: string;
  status: 'open' | 'in_progress' | 'review' | 'done' | 'cancelled' | 'blocked';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  assignee?: string;
  assignee_email?: string;
  due_date?: string;
  changes?: Record<string, { from: unknown; to: unknown }>;
  updated_at?: string;
}

/**
 * Task Updated Webhook Payload
 */
export interface TaskUpdatedPayload extends Omit<WebhookPayload, 'data'> {
  event: WebhookEventType.TASK_UPDATED;
  data: TaskUpdatedData;
}

/**
 * Union type for all webhook payloads
 */
export type AnyWebhookPayload = PROpenedPayload | CommitPayload | TaskUpdatedPayload;

/**
 * Webhook event handlers by type
 */
export interface WebhookHandlers {
  [WebhookEventType.PR_OPENED]?: (payload: PROpenedPayload) => Promise<void>;
  [WebhookEventType.COMMIT]?: (payload: CommitPayload) => Promise<void>;
  [WebhookEventType.TASK_UPDATED]?: (payload: TaskUpdatedPayload) => Promise<void>;
}

/**
 * Webhook error response
 */
export interface WebhookErrorResponse {
  success: false;
  error: string;
  deliveryId: string;
  details?: Record<string, unknown>;
}

/**
 * Webhook success response
 */
export interface WebhookSuccessResponse {
  success: true;
  deliveryId: string;
  message?: string;
}

/**
 * Webhook response (union type)
 */
export type WebhookResponse = WebhookSuccessResponse | WebhookErrorResponse;

/**
 * Type guard for PR opened payload
 */
export function isPROpenedPayload(payload: AnyWebhookPayload): payload is PROpenedPayload {
  return payload.event === WebhookEventType.PR_OPENED;
}

/**
 * Type guard for commit payload
 */
export function isCommitPayload(payload: AnyWebhookPayload): payload is CommitPayload {
  return payload.event === WebhookEventType.COMMIT;
}

/**
 * Type guard for task updated payload
 */
export function isTaskUpdatedPayload(payload: AnyWebhookPayload): payload is TaskUpdatedPayload {
  return payload.event === WebhookEventType.TASK_UPDATED;
}
