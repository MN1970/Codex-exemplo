/**
 * Índice de exportações dos serviços
 */

// Sync Queue Manager
export {
  SyncQueueManager,
  QueuePriority,
  QueueItemStatus,
  type SyncQueueItem,
  type RetryPolicy,
  type QueueMetrics,
  type PrometheusMetrics,
  runSyncQueueExamples,
} from "./sync-queue";

// Notifications Service
export {
  InteligentNotifier,
  NotificationEventType,
  NotificationPriority,
  DeliveryStatus,
  type NotificationEvent,
  type Notification,
  type UserNotificationPreferences,
  type DeliveryAnalytics,
  getNotifier,
  runNotificationExamples,
} from "./notifications";

// Health Dashboard
export {
  HealthDashboard,
  type HealthStatus,
  type ComponentHealth,
  type HealthMetrics,
  type MetricsSnapshot,
  type AlertRule,
} from "./health-dashboard";

// Maestro Router
export {
  MaestroRouter,
  type RoutingResult,
  type AgentProfile,
  type KeywordMatchResult,
} from "./maestro-router";

// Code Generator
export {
  CodeGenerator,
  createCodeGenerator,
  validateYAMLFrontmatter,
  type CodeGeneratorIntent,
  type CodeGeneratorOutput,
  type GeneratedArtifact,
  type AgentFrontmatter,
  type ConversationMessage,
} from "./code-generator";

// Intent Parser
export {
  IntentParser,
  getIntentParser,
  parseIntent,
  parseAndValidate,
  runIntentParserExamples,
  type ParsedIntent,
  type ActionType,
  type TargetType,
  type IntentParserConfig,
  type ValidationResult,
} from "./intent-parser";
