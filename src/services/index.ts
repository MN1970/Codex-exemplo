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

// Code Generator Enhanced (Phase 3 - PR-Specific)
export {
  CodeGeneratorPR,
  createCodeGeneratorPR,
  analyzeQuickPR,
  suggestTestsQuick,
  type PRContext,
  type CodeFix,
  type Refactoring,
  type TestSuite,
  type TestCase,
  type TestScenario,
  type Improvement,
  type PRAnalysisResult,
} from "./code-generator-enhanced";

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

// CI/CD Orchestrator
export {
  CIOrchestratorService,
  createCIOrchestratorService,
  WorkflowRunStatus,
  WorkflowConclusion,
  type CIOrchestratorConfig,
  type OrchestrationResult,
  type WorkflowRun,
  type BuildOutput,
  type TestResult,
  type CoverageResult,
  type LintError,
  type CIMetrics,
} from "./ci-orchestrator";

// PR Automation Engine
export {
  PRAutomationEngine,
  createPRAutomationEngine,
  PRAnalysisStatus,
  type PRAnalysis,
  type Suggestion,
  type SuggestionSeverity,
  type CodePatternType,
  type DetectedPattern,
  type BuildStatus,
  type CIResult,
  type CodeContext,
  type PRAutomationConfig,
} from "./pr-automation";

// Feedback Engine
export {
  FeedbackEngine,
  createFeedbackEngine,
  ErrorType,
  ErrorSeverity,
  FeedbackStatus,
  type CIError,
  type CIOutput,
  type CorrectionSuggestion,
  type PRComment,
  type RetryPolicy,
  type FeedbackAttempt,
  type FeedbackTracking,
  type FeedbackEngineConfig,
} from "./feedback-engine";
