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

// CI/CD Orchestrator (Phase 3 - CI Integration)
export {
  CIOrchestratorService,
  createCIOrchestratorService,
  WorkflowRunStatus,
  WorkflowConclusion,
  BuildPriority,
  LockStatus,
  type CIOrchestratorConfig,
  type OrchestrationResult,
  type WorkflowRun,
  type BuildOutput,
  type TestResult,
  type CoverageResult,
  type LintError,
  type CIMetrics,
  type BuildStatus,
  type JobResult,
  type BuildQueueItem,
  type BuildEvent,
  type BuildWebhook,
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

// Feedback Engine (Phase 3 - Complete Feedback Loop)
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
  type FeedbackAttempt,
  type FeedbackTracking,
  type FeedbackEngineConfig,
  // Phase 3 additions
  type BuildStatus,
  type Feedback,
  type Recommendation,
  type PRAnalysis,
  type Metrics,
  type Reviewer,
  type MetricsAggregate,
} from "./feedback-engine";

// LLM Judge (Phase 4 - Decision Engine)
export {
  LLMJudge,
  createLLMJudge,
  judgePR,
  translateAction,
  translateRiskLevel,
  translateConfidenceLevel,
  translateMergeDecision,
  translateIssueSeverity,
  JudgeAction,
  type PRJudgment,
  type PRData,
  type LLMJudgeConfig,
  type RiskLevel,
  type RiskCategory,
  type MergeDecisionType,
  type ConfidenceLevel,
  type IssueSeverity,
  type Evaluation,
  type CodeReview,
  type CodeIssue,
  type SecurityRisk,
  type PerformanceRisk,
  type TestabilityScore,
  type MaintainabilityScore,
  type DocumentationScore,
  type MergeDecision,
  type QualityScore,
  type AuditTrailEntry,
} from "./llm-judge";

// Code Reviewer Service (Phase 4 - Main Service)
export {
  CodeReviewer,
  createCodeReviewer,
  reviewCodeFast,
  reviewCodeDeep,
  analyzeSecurity,
  analyzePerformance,
  suggestRefactors,
  type SecurityIssue,
  type PerformanceIssue,
  type Refactoring,
  type ReviewComment,
  type Review,
  type ReviewContext,
  type ReviewStats,
  type CodeReviewerConfig,
  type IssueSeverity,
  type IssueCategory,
} from "./code-reviewer";

// Rollback Orchestrator (Phase 5 - Failure Recovery)
export {
  RollbackOrchestratorService,
  createRollbackOrchestratorService,
  RollbackMonitorStatus,
  RollbackExecutionStatus,
  NotificationType,
  FailureSeverity,
  type MergedPR,
  type CIFailure,
  type FailedTest,
  type LintErrorDetail,
  type RollbackProposal,
  type RollbackImpact,
  type RollbackExecution,
  type ApprovalRequest,
  type AuditTrailEntry,
  type RollbackMetrics,
  type RollbackOrchestratorConfig,
} from "./rollback";

// Rollback Service (Phase 4 - Safety Mechanism)
export {
  Rollback,
  createRollback,
  type RollbackConfig,
  type Issue,
  type RevertResult,
  type RollbackEvent,
} from "./rollback";

// Auto-Merge Controller (Phase 5 - Auto-Merge Automation)
export {
  AutoMergeController,
  createAutoMergeController,
  MergeStatus,
  BlockReason,
  type AutoMergeConfig,
  type MergeResult,
  type PrerequisiteCheckResult,
  type AuditEvent,
} from "./auto-merge";

// Auto-Merge Service (Phase 4 - Advanced Merge Automation)
export {
  AutoMerge,
  createAutoMerge,
  LockStatus,
  ScheduleStatus,
  type MergeStrategy,
  type ConflictType,
  type RequirementType,
  type Conflict,
  type Requirement,
  type ScheduleResult,
  type DistributedLock,
  type AuditLogEntry,
  type MergeMetrics,
  type AutoMergeServiceConfig,
} from "./auto-merge-service";

// Master Orchestrator (Pipeline Orchestrator - Coordena todo o fluxo)
export {
  MasterOrchestrator,
  createMasterOrchestrator,
  OrchestratorState,
  ErrorSeverity,
  TelemetryEventType,
  type OrchestratorInput,
  type OrchestratorResult,
  type OrchestratorConfig,
  type OrchestratorMetrics,
  type TelemetryEvent,
  type TrackedError,
  type RetryAttempt,
  type RetryPolicy,
} from "./orchestrator";
