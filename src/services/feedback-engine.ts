/**
 * Feedback Engine — Sistema inteligente de feedback de CI/CD
 * Versão: 2.0.0 (Phase 3 — Feedback Loop Completo)
 *
 * Recursos:
 * - Lê outputs de CI (testes, lint, coverage)
 * - Gera sugestões de correção via Claude Haiku
 * - Posta comentários automáticos na PR
 * - Retry logic com exponential backoff
 * - Rastreia tentativas e tempo gasto
 * - Propõe iterações automáticas de fix
 * - Análise de resultados de CI/CD (Phase 3)
 * - Geração de recomendações de melhoria
 * - Rastreamento de métricas de PR
 * - Sugestão automática de revisores
 * - Agregação de métricas e análise de tendências
 */

import Anthropic from "@anthropic-ai/sdk";

/**
 * Tipos de erros de CI detectados
 */
export enum ErrorType {
  TEST_FAILURE = "test_failure",
  LINT_ERROR = "lint_error",
  TYPE_ERROR = "type_error",
  COVERAGE_BELOW_THRESHOLD = "coverage_below_threshold",
  BUILD_FAILURE = "build_failure",
  DEPENDENCY_ERROR = "dependency_error",
  PERFORMANCE_REGRESSION = "performance_regression",
  SECURITY_ISSUE = "security_issue",
}

/**
 * Severidade do erro
 */
export enum ErrorSeverity {
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  CRITICAL = "critical",
}

/**
 * Status de feedback
 */
export enum FeedbackStatus {
  PENDING = "pending",
  GENERATING = "generating",
  GENERATED = "generated",
  POSTING = "posting",
  POSTED = "posted",
  FAILED = "failed",
  SKIPPED = "skipped",
}

/**
 * Interface para erro de CI
 */
export interface CIError {
  type: ErrorType;
  severity: ErrorSeverity;
  file?: string;
  line?: number;
  column?: number;
  message: string;
  context?: string; // código / output relevante
  suggestion?: string; // sugestão manual (opcional)
}

/**
 * Interface para output de CI
 */
export interface CIOutput {
  workflowId: string;
  workflowName: string;
  prNumber: number;
  branch: string;
  commit: string;
  timestamp: Date;
  duration: number; // ms
  status: "success" | "failure";
  errors: CIError[];
  logs: string[];
  testResults?: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
    duration: number; // ms
    failedTests?: string[];
  };
  coverage?: {
    lines: number;
    statements: number;
    functions: number;
    branches: number;
    threshold?: number;
  };
}

/**
 * Interface para sugestão gerada
 */
export interface CorrectionSuggestion {
  errorType: ErrorType;
  originalError: CIError;
  suggestion: string;
  codeExample?: string;
  confidence: number; // 0-1
  priority: "low" | "medium" | "high";
}

/**
 * Interface para comentário na PR
 */
export interface PRComment {
  id?: string;
  prNumber: number;
  owner: string;
  repo: string;
  body: string;
  inReplyTo?: string; // comment ID para thread
  suggestions?: CorrectionSuggestion[];
}

/**
 * Interface para retry policy
 */
export interface RetryPolicy {
  maxAttempts: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffFactor: number;
  retryableStatusCodes?: number[];
}

/**
 * Interface para tentativa de feedback
 */
export interface FeedbackAttempt {
  attemptNumber: number;
  timestamp: Date;
  status: FeedbackStatus;
  duration?: number; // ms
  error?: string;
}

/**
 * Interface para rastreamento de feedback
 */
export interface FeedbackTracking {
  feedbackId: string;
  ciOutputId: string;
  prNumber: number;
  createdAt: Date;
  attempts: FeedbackAttempt[];
  totalTimeSpent: number; // ms
  totalAttempts: number;
  suggestionsGenerated: number;
  commentsPosted: number;
  status: FeedbackStatus;
  lastAttemptAt?: Date;
}

/**
 * Interface para resultado de análise de CI (Phase 3)
 */
export interface BuildStatus {
  workflowId: string;
  workflowName: string;
  prNumber: number;
  status: "success" | "failure" | "unstable";
  timestamp: Date;
  duration: number;
  testResults?: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
    duration: number;
    failedTests?: string[];
  };
  coverage?: {
    lines: number;
    statements: number;
    functions: number;
    branches: number;
    threshold?: number;
    previousCoverage?: number; // para comparação
  };
  lint?: {
    errors: number;
    warnings: number;
    fixable: number;
  };
  performance?: {
    buildTimeMs: number;
    bundleSizeBytes?: number;
    memoryUsageMB?: number;
    previousBuildTimeMs?: number; // para detecção de regressão
  };
}

/**
 * Interface para feedback análise (Phase 3)
 */
export interface Feedback {
  feedbackId: string;
  prNumber: number;
  buildStatus: BuildStatus;
  summary: string;
  severity: "info" | "warning" | "error" | "critical";
  issues: {
    category: string;
    count: number;
    severity: string;
    details?: string[];
  }[];
  recommendations: Recommendation[];
  metricsChange?: {
    coverageChange: number; // percentual
    performanceChange: number; // percentual
    qualityScore: number; // 0-100
  };
  createdAt: Date;
}

/**
 * Interface para recomendações de melhoria (Phase 3)
 */
export interface Recommendation {
  id: string;
  type: "code" | "test" | "performance" | "coverage" | "quality";
  title: string;
  description: string;
  impact: "low" | "medium" | "high";
  effort: "low" | "medium" | "high";
  priority: number; // 1-10
  codeExample?: string;
  estimatedTimeMinutes?: number;
}

/**
 * Interface para análise de PR (Phase 3)
 */
export interface PRAnalysis {
  prNumber: number;
  title: string;
  description: string;
  author: string;
  filesChanged: number;
  additions: number;
  deletions: number;
  commits: number;
  diff?: string;
  labels?: string[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Interface para métricas de PR (Phase 3)
 */
export interface Metrics {
  prNumber: number;
  timestamp: Date;
  qualityScore: number; // 0-100
  testCoverage: number; // percentual
  buildTimeMs: number;
  testsPassed: number;
  testsFailed: number;
  lintIssues: number;
  securityIssues: number;
  reviewComments: number;
  iterationCount: number; // quantas vezes foi atualizado
  timeToMergeMinutes?: number;
  complexity?: {
    cyclomaticComplexity: number;
    cognitiveComplexity: number;
    maintainabilityIndex: number;
  };
}

/**
 * Interface para sugestão de revisor (Phase 3)
 */
export interface Reviewer {
  username: string;
  expertise: string[];
  matchScore: number; // 0-1
  recentReviews?: number;
  avgReviewTimeHours?: number;
  filesExpertise?: {
    [file: string]: number; // score de expertise em arquivo
  };
}

/**
 * Interface para agregação de métricas (Phase 3)
 */
export interface MetricsAggregate {
  period: {
    startDate: Date;
    endDate: Date;
  };
  totalPRs: number;
  avgQualityScore: number;
  avgTestCoverage: number;
  avgBuildTimeMs: number;
  totalTestsPassed: number;
  totalTestsFailed: number;
  successRate: number; // percentual
  trends: {
    qualityTrend: number; // mudança em pontos percentuais
    coverageTrend: number;
    performanceTrend: number; // positivo = mais rápido
  };
  topIssues: {
    category: string;
    count: number;
    percentage: number;
  }[];
}

/**
 * Interface para configuração do FeedbackEngine
 */
export interface FeedbackEngineConfig {
  anthropicApiKey?: string;
  githubToken: string;
  owner: string;
  repo: string;
  model?: string; // default: claude-3-5-haiku-20241022
  maxTokens?: number; // default: 1000
  retryPolicy?: Partial<RetryPolicy>;
  includeCodeExamples?: boolean;
  autoReplyEnabled?: boolean; // propõe iteração automática
  notifyOnNewIssues?: boolean;
  metricsHistoryLimit?: number; // default: 100
}

/**
 * Interface interna para armazenar config resolvida
 */
interface ResolvedFeedbackEngineConfig extends Omit<FeedbackEngineConfig, "retryPolicy"> {
  retryPolicy: RetryPolicy;
  metricsHistoryLimit: number;
}

/**
 * Default retry policy
 */
const DEFAULT_RETRY_POLICY: RetryPolicy = {
  maxAttempts: 3,
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  backoffFactor: 2,
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
};

/**
 * FeedbackEngine — Classe principal
 */
export class FeedbackEngine {
  private client: Anthropic;
  private config: ResolvedFeedbackEngineConfig;
  private retryPolicy: RetryPolicy;
  private apiBaseUrl = "https://api.github.com";
  private feedbackHistory: Map<string, FeedbackTracking> = new Map();
  private metricsHistory: Map<number, Metrics[]> = new Map(); // prNumber -> Metrics[]
  private feedbackCache: Map<number, Feedback> = new Map(); // prNumber -> Feedback
  private reviewerCache: Map<string, Reviewer> = new Map(); // username -> Reviewer

  constructor(config: FeedbackEngineConfig) {
    this.client = new Anthropic({
      apiKey: config.anthropicApiKey || process.env.ANTHROPIC_API_KEY,
    });

    const apiKey = config.anthropicApiKey || process.env.ANTHROPIC_API_KEY || "";
    this.config = {
      anthropicApiKey: apiKey,
      githubToken: config.githubToken,
      owner: config.owner,
      repo: config.repo,
      model: config.model || "claude-3-haiku-20240307",
      maxTokens: config.maxTokens || 1000,
      retryPolicy: {
        ...DEFAULT_RETRY_POLICY,
        ...(config.retryPolicy || {}),
      },
      includeCodeExamples: config.includeCodeExamples ?? true,
      autoReplyEnabled: config.autoReplyEnabled ?? true,
      notifyOnNewIssues: config.notifyOnNewIssues ?? true,
      metricsHistoryLimit: config.metricsHistoryLimit ?? 100,
    };

    this.retryPolicy = this.config.retryPolicy;
  }

  /**
   * Phase 3 — Analisa resultados de CI/CD e retorna Feedback consolidado
   */
  public async analyzeCIResults(buildStatus: BuildStatus): Promise<Feedback> {
    const feedbackId = `feedback_${buildStatus.prNumber}_${Date.now()}`;

    try {
      // Determina severidade baseado no status
      const severity: "info" | "warning" | "error" | "critical" = this.determineSeverity(
        buildStatus
      );

      // Coleta problemas identificados
      const issues = this.extractIssuesFromBuildStatus(buildStatus);

      // Gera recomendações específicas
      const recommendations = await this.generateRecommendationsFromIssues(
        buildStatus,
        issues
      );

      // Calcula mudanças de métricas
      const metricsChange = this.calculateMetricsChange(buildStatus);

      // Cria summary
      const summary = this.generateFeedbackSummary(buildStatus, issues, severity);

      const feedback: Feedback = {
        feedbackId,
        prNumber: buildStatus.prNumber,
        buildStatus,
        summary,
        severity,
        issues,
        recommendations,
        metricsChange,
        createdAt: new Date(),
      };

      // Cacheia feedback
      this.feedbackCache.set(buildStatus.prNumber, feedback);

      return feedback;
    } catch (error) {
      console.error("Error analyzing CI results:", error);
      throw error;
    }
  }

  /**
   * Phase 3 — Gera recomendações de melhoria baseado em análise de PR
   */
  public async generateRecommendations(prAnalysis: PRAnalysis): Promise<Recommendation[]> {
    const systemPrompt = `Você é um especialista em qualidade de código e engenharia de software.
Analise informações de uma Pull Request e gere recomendações de melhoria prioritizadas.
Retorne um JSON com array de recomendações.`;

    const userPrompt = `
Análise de PR:
- Número: ${prAnalysis.prNumber}
- Título: ${prAnalysis.title}
- Descrição: ${prAnalysis.description}
- Autor: ${prAnalysis.author}
- Arquivos alterados: ${prAnalysis.filesChanged}
- Adições: ${prAnalysis.additions}
- Deleções: ${prAnalysis.deletions}
- Commits: ${prAnalysis.commits}
- Labels: ${(prAnalysis.labels || []).join(", ")}

${prAnalysis.diff ? `Diff (primeiras linhas):\n${prAnalysis.diff.split("\n").slice(0, 50).join("\n")}` : ""}

Gere recomendações estruturadas em JSON com formato:
{
  "recommendations": [
    {
      "type": "code|test|performance|coverage|quality",
      "title": "string",
      "description": "string",
      "impact": "low|medium|high",
      "effort": "low|medium|high",
      "priority": 1-10,
      "codeExample": "string (opcional)",
      "estimatedTimeMinutes": número (opcional)
    }
  ]
}`;

    try {
      const response = await (this.client.messages.create as any)({
        model: this.config.model,
        max_tokens: this.config.maxTokens,
        system: systemPrompt,
        messages: [
          {
            role: "user",
            content: userPrompt,
          },
        ],
      });

      const content = response.content[0];
      if (content.type !== "text") {
        throw new Error("Unexpected response format from Claude");
      }

      return this.parseRecommendations(content.text);
    } catch (error) {
      console.error("Error generating recommendations:", error);
      return [];
    }
  }

  /**
   * Phase 3 — Rastreia e agrega métricas de PR
   */
  public async trackMetrics(prNumber: number): Promise<Metrics> {
    const timestamp = new Date();

    // Recupera métricas do feedback cache se disponível
    const feedback = this.feedbackCache.get(prNumber);
    const buildStatus = feedback?.buildStatus;

    const metrics: Metrics = {
      prNumber,
      timestamp,
      qualityScore: this.calculateQualityScore(buildStatus),
      testCoverage: buildStatus?.coverage?.lines ?? 0,
      buildTimeMs: buildStatus?.duration ?? 0,
      testsPassed: buildStatus?.testResults?.passed ?? 0,
      testsFailed: buildStatus?.testResults?.failed ?? 0,
      lintIssues: buildStatus?.lint?.errors ?? 0,
      securityIssues: 0, // TODO: integrar com ferramenta de segurança
      reviewComments: 0, // TODO: recuperar do GitHub
      iterationCount: 1, // TODO: contar updates da PR
      complexity: this.calculateCodeComplexity(buildStatus),
    };

    // Armazena métricas no histórico
    if (!this.metricsHistory.has(prNumber)) {
      this.metricsHistory.set(prNumber, []);
    }

    const prMetrics = this.metricsHistory.get(prNumber)!;
    prMetrics.push(metrics);

    // Mantém limite de histórico
    if (prMetrics.length > this.config.metricsHistoryLimit) {
      prMetrics.shift();
    }

    return metrics;
  }

  /**
   * Phase 3 — Sugere revisores baseado no diff da PR
   */
  public async suggestReviewers(prDiff: string): Promise<Reviewer[]> {
    const systemPrompt = `Você é um especialista em arquitetura de software e conhece profundamente este repositório.
Analise um diff de PR e sugira revisores ideais com base em expertise em areas afetadas.
Retorne JSON com sugestões de revisores.`;

    const userPrompt = `
Diff da PR (primeiras 100 linhas):
${prDiff.split("\n").slice(0, 100).join("\n")}

Baseado nas alterações, sugira revisores ideais em formato JSON:
{
  "reviewers": [
    {
      "username": "string",
      "expertise": ["area1", "area2"],
      "matchScore": 0.0-1.0,
      "filesExpertise": {
        "path/to/file.ts": 0.0-1.0
      }
    }
  ]
}`;

    try {
      const response = await (this.client.messages.create as any)({
        model: this.config.model,
        max_tokens: this.config.maxTokens,
        system: systemPrompt,
        messages: [
          {
            role: "user",
            content: userPrompt,
          },
        ],
      });

      const content = response.content[0];
      if (content.type !== "text") {
        throw new Error("Unexpected response format from Claude");
      }

      return this.parseReviewers(content.text);
    } catch (error) {
      console.error("Error suggesting reviewers:", error);
      return [];
    }
  }

  /**
   * Retorna agregação de métricas por período (Phase 3)
   */
  public getMetricsAggregate(startDate: Date, endDate: Date): MetricsAggregate {
    const allMetrics: Metrics[] = [];

    // Coleta todas as métricas no período
    for (const metrics of this.metricsHistory.values()) {
      allMetrics.push(
        ...metrics.filter((m) => m.timestamp >= startDate && m.timestamp <= endDate)
      );
    }

    if (allMetrics.length === 0) {
      return {
        period: { startDate, endDate },
        totalPRs: 0,
        avgQualityScore: 0,
        avgTestCoverage: 0,
        avgBuildTimeMs: 0,
        totalTestsPassed: 0,
        totalTestsFailed: 0,
        successRate: 0,
        trends: {
          qualityTrend: 0,
          coverageTrend: 0,
          performanceTrend: 0,
        },
        topIssues: [],
      };
    }

    // Calcula agregações
    const totalPRs = new Set(allMetrics.map((m) => m.prNumber)).size;
    const avgQualityScore = allMetrics.reduce((sum, m) => sum + m.qualityScore, 0) / allMetrics.length;
    const avgTestCoverage = allMetrics.reduce((sum, m) => sum + m.testCoverage, 0) / allMetrics.length;
    const avgBuildTimeMs = allMetrics.reduce((sum, m) => sum + m.buildTimeMs, 0) / allMetrics.length;
    const totalTestsPassed = allMetrics.reduce((sum, m) => sum + m.testsPassed, 0);
    const totalTestsFailed = allMetrics.reduce((sum, m) => sum + m.testsFailed, 0);
    const successRate = totalTestsPassed / (totalTestsPassed + totalTestsFailed || 1);

    // Calcula tendências
    const sortedMetrics = allMetrics.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    const trends = this.calculateTrends(sortedMetrics);

    return {
      period: { startDate, endDate },
      totalPRs,
      avgQualityScore,
      avgTestCoverage,
      avgBuildTimeMs,
      totalTestsPassed,
      totalTestsFailed,
      successRate: successRate * 100,
      trends,
      topIssues: [], // TODO: agregar issues mais comuns
    };
  }

  /**
   * Processa output de CI e gera feedback
   */
  public async processCIOutput(output: CIOutput): Promise<FeedbackTracking> {
    const feedbackId = `feedback_${output.prNumber}_${Date.now()}`;
    const tracking: FeedbackTracking = {
      feedbackId,
      ciOutputId: output.workflowId,
      prNumber: output.prNumber,
      createdAt: new Date(),
      attempts: [],
      totalTimeSpent: 0,
      totalAttempts: 0,
      suggestionsGenerated: 0,
      commentsPosted: 0,
      status: FeedbackStatus.PENDING,
    };

    const startTime = Date.now();

    try {
      // Se não há erros, pula o processamento
      if (output.errors.length === 0) {
        tracking.status = FeedbackStatus.SKIPPED;
        tracking.totalTimeSpent = Date.now() - startTime;
        this.feedbackHistory.set(feedbackId, tracking);
        return tracking;
      }

      // Gera sugestões com retry
      const suggestions = await this.generateSuggestionsWithRetry(output);
      tracking.suggestionsGenerated = suggestions.length;

      // Posta comentário na PR com retry
      if (suggestions.length > 0) {
        await this.postCommentWithRetry({
          prNumber: output.prNumber,
          owner: this.config.owner,
          repo: this.config.repo,
          body: this.formatSuggestionsComment(output, suggestions),
          suggestions,
        });
        tracking.commentsPosted = 1;
      }

      tracking.status = FeedbackStatus.POSTED;
      tracking.totalTimeSpent = Date.now() - startTime;
    } catch (error) {
      tracking.status = FeedbackStatus.FAILED;
      tracking.totalTimeSpent = Date.now() - startTime;
      const attempt = tracking.attempts[tracking.attempts.length - 1];
      if (attempt) {
        attempt.error = error instanceof Error ? error.message : String(error);
      }
    }

    this.feedbackHistory.set(feedbackId, tracking);
    return tracking;
  }

  /**
   * Determina severidade de build status
   */
  private determineSeverity(
    buildStatus: BuildStatus
  ): "info" | "warning" | "error" | "critical" {
    if (buildStatus.status === "success") {
      return "info";
    }

    if (buildStatus.status === "failure") {
      // Escalona para critical se há múltiplas falhas
      const failedTests = buildStatus.testResults?.failed ?? 0;
      const lintErrors = buildStatus.lint?.errors ?? 0;

      if (failedTests > 5 || lintErrors > 10) {
        return "critical";
      }

      return "error";
    }

    return "warning"; // unstable
  }

  /**
   * Extrai problemas de BuildStatus
   */
  private extractIssuesFromBuildStatus(
    buildStatus: BuildStatus
  ): { category: string; count: number; severity: string; details?: string[] }[] {
    const issues: { category: string; count: number; severity: string; details?: string[] }[] =
      [];

    if (buildStatus.testResults && buildStatus.testResults.failed > 0) {
      issues.push({
        category: "Test Failures",
        count: buildStatus.testResults.failed,
        severity: "error",
        details: buildStatus.testResults.failedTests?.slice(0, 5),
      });
    }

    if (buildStatus.coverage && buildStatus.coverage.threshold) {
      if (buildStatus.coverage.lines < buildStatus.coverage.threshold) {
        const diff = buildStatus.coverage.threshold - buildStatus.coverage.lines;
        issues.push({
          category: "Coverage Below Threshold",
          count: 1,
          severity: "warning",
          details: [`Missing ${diff.toFixed(2)}% coverage`],
        });
      }
    }

    if (buildStatus.lint && buildStatus.lint.errors > 0) {
      issues.push({
        category: "Lint Errors",
        count: buildStatus.lint.errors,
        severity: "error",
        details: [`${buildStatus.lint.fixable} fixable errors`],
      });
    }

    if (
      buildStatus.performance &&
      buildStatus.performance.previousBuildTimeMs &&
      buildStatus.performance.buildTimeMs > buildStatus.performance.previousBuildTimeMs * 1.2
    ) {
      const increase = (
        ((buildStatus.performance.buildTimeMs - buildStatus.performance.previousBuildTimeMs) /
          buildStatus.performance.previousBuildTimeMs) *
        100
      ).toFixed(1);
      issues.push({
        category: "Performance Regression",
        count: 1,
        severity: "warning",
        details: [`Build time increased by ${increase}%`],
      });
    }

    return issues;
  }

  /**
   * Gera recomendações a partir de issues identificadas
   */
  private async generateRecommendationsFromIssues(
    buildStatus: BuildStatus,
    issues: { category: string; count: number; severity: string; details?: string[] }[]
  ): Promise<Recommendation[]> {
    const recommendations: Recommendation[] = [];

    for (const issue of issues) {
      if (issue.category === "Test Failures") {
        recommendations.push({
          id: `rec_${Date.now()}_test`,
          type: "test",
          title: "Fix failing tests",
          description: `${issue.count} test(s) are failing. Review error logs and fix the underlying issues.`,
          impact: "high",
          effort: "medium",
          priority: 9,
          estimatedTimeMinutes: 30,
        });
      } else if (issue.category === "Coverage Below Threshold") {
        recommendations.push({
          id: `rec_${Date.now()}_coverage`,
          type: "coverage",
          title: "Increase test coverage",
          description: "Add tests for uncovered code paths to meet coverage threshold.",
          impact: "medium",
          effort: "medium",
          priority: 7,
          estimatedTimeMinutes: 45,
        });
      } else if (issue.category === "Lint Errors") {
        recommendations.push({
          id: `rec_${Date.now()}_lint`,
          type: "code",
          title: "Fix linting errors",
          description: `${issue.details?.[0] || "Fix all linting violations."}`,
          impact: "medium",
          effort: "low",
          priority: 6,
          estimatedTimeMinutes: 15,
        });
      } else if (issue.category === "Performance Regression") {
        recommendations.push({
          id: `rec_${Date.now()}_perf`,
          type: "performance",
          title: "Investigate performance regression",
          description: issue.details?.[0] || "Build performance has degraded.",
          impact: "medium",
          effort: "high",
          priority: 8,
          estimatedTimeMinutes: 60,
        });
      }
    }

    return recommendations;
  }

  /**
   * Calcula mudança em métricas
   */
  private calculateMetricsChange(buildStatus: BuildStatus): {
    coverageChange: number;
    performanceChange: number;
    qualityScore: number;
  } {
    const coverageChange = buildStatus.coverage?.previousCoverage
      ? buildStatus.coverage.lines - buildStatus.coverage.previousCoverage
      : 0;

    const performanceChange = buildStatus.performance?.previousBuildTimeMs
      ? (
          ((buildStatus.performance.buildTimeMs - buildStatus.performance.previousBuildTimeMs) /
            buildStatus.performance.previousBuildTimeMs) *
          100
        ).toFixed(1)
      : 0;

    const qualityScore = this.calculateQualityScore(buildStatus);

    return {
      coverageChange,
      performanceChange: typeof performanceChange === "string" ? parseFloat(performanceChange) : 0,
      qualityScore,
    };
  }

  /**
   * Calcula score de qualidade (0-100)
   */
  private calculateQualityScore(buildStatus?: BuildStatus): number {
    if (!buildStatus) return 0;

    let score = 100;

    // Penaliza por testes falhados
    if (buildStatus.testResults) {
      const failureRate =
        buildStatus.testResults.failed /
        (buildStatus.testResults.total || 1);
      score -= failureRate * 40;
    }

    // Penaliza por coverage baixa
    if (buildStatus.coverage) {
      const coverageDeficit = Math.max(0, (buildStatus.coverage.threshold ?? 80) - buildStatus.coverage.lines);
      score -= (coverageDeficit / 20) * 30;
    }

    // Penaliza por erros de lint
    if (buildStatus.lint) {
      const lintPenalty = Math.min(20, buildStatus.lint.errors * 2);
      score -= lintPenalty;
    }

    // Penaliza por regressão de performance
    if (
      buildStatus.performance?.previousBuildTimeMs &&
      buildStatus.performance.buildTimeMs > buildStatus.performance.previousBuildTimeMs * 1.2
    ) {
      score -= 10;
    }

    return Math.max(0, score);
  }

  /**
   * Calcula complexidade de código
   */
  private calculateCodeComplexity(buildStatus?: BuildStatus) {
    // TODO: integrar com ferramentas de análise de complexidade
    return {
      cyclomaticComplexity: 5,
      cognitiveComplexity: 3,
      maintainabilityIndex: 85,
    };
  }

  /**
   * Gera summary de feedback
   */
  private generateFeedbackSummary(
    buildStatus: BuildStatus,
    issues: { category: string; count: number; severity: string; details?: string[] }[],
    severity: "info" | "warning" | "error" | "critical"
  ): string {
    if (buildStatus.status === "success") {
      return "All checks passed successfully!";
    }

    const issueCount = issues.length;
    const issueList = issues.map((i) => `${i.category} (${i.count})`).join(", ");

    return `Build ${buildStatus.status} with ${issueCount} issue(s): ${issueList}`;
  }

  /**
   * Parse recomendações do Claude
   */
  private parseRecommendations(responseText: string): Recommendation[] {
    try {
      let jsonText = responseText.trim();
      if (jsonText.startsWith("```json")) {
        jsonText = jsonText.slice(7);
      } else if (jsonText.startsWith("```")) {
        jsonText = jsonText.slice(3);
      }
      if (jsonText.endsWith("```")) {
        jsonText = jsonText.slice(0, -3);
      }

      const parsed = JSON.parse(jsonText.trim());

      if (!Array.isArray(parsed.recommendations)) {
        return [];
      }

      return parsed.recommendations.map(
        (r: Record<string, unknown>, idx: number): Recommendation => ({
          id: `rec_${Date.now()}_${idx}`,
          type: (String(r.type) as any) || "quality",
          title: String(r.title || ""),
          description: String(r.description || ""),
          impact: (String(r.impact) as any) || "medium",
          effort: (String(r.effort) as any) || "medium",
          priority: typeof r.priority === "number" ? r.priority : 5,
          codeExample: r.codeExample ? String(r.codeExample) : undefined,
          estimatedTimeMinutes: typeof r.estimatedTimeMinutes === "number"
            ? r.estimatedTimeMinutes
            : undefined,
        })
      );
    } catch (error) {
      console.error("Failed to parse recommendations:", error);
      return [];
    }
  }

  /**
   * Parse revisores do Claude
   */
  private parseReviewers(responseText: string): Reviewer[] {
    try {
      let jsonText = responseText.trim();
      if (jsonText.startsWith("```json")) {
        jsonText = jsonText.slice(7);
      } else if (jsonText.startsWith("```")) {
        jsonText = jsonText.slice(3);
      }
      if (jsonText.endsWith("```")) {
        jsonText = jsonText.slice(0, -3);
      }

      const parsed = JSON.parse(jsonText.trim());

      if (!Array.isArray(parsed.reviewers)) {
        return [];
      }

      return parsed.reviewers.map((r: Record<string, unknown>): Reviewer => {
        const reviewer: Reviewer = {
          username: String(r.username || ""),
          expertise: Array.isArray(r.expertise) ? r.expertise.map(String) : [],
          matchScore: typeof r.matchScore === "number" ? r.matchScore : 0.5,
        };

        if (r.filesExpertise && typeof r.filesExpertise === "object") {
          reviewer.filesExpertise = Object.entries(r.filesExpertise).reduce(
            (acc: Record<string, number>, [file, score]) => {
              acc[file] = typeof score === "number" ? score : 0.5;
              return acc;
            },
            {}
          );
        }

        return reviewer;
      });
    } catch (error) {
      console.error("Failed to parse reviewers:", error);
      return [];
    }
  }

  /**
   * Calcula tendências de métricas
   */
  private calculateTrends(sortedMetrics: Metrics[]): {
    qualityTrend: number;
    coverageTrend: number;
    performanceTrend: number;
  } {
    if (sortedMetrics.length < 2) {
      return { qualityTrend: 0, coverageTrend: 0, performanceTrend: 0 };
    }

    const mid = Math.floor(sortedMetrics.length / 2);
    const firstHalf = sortedMetrics.slice(0, mid);
    const secondHalf = sortedMetrics.slice(mid);

    const avgQualityFirst = firstHalf.reduce((sum, m) => sum + m.qualityScore, 0) / firstHalf.length;
    const avgQualitySecond = secondHalf.reduce((sum, m) => sum + m.qualityScore, 0) / secondHalf.length;

    const avgCoverageFirst = firstHalf.reduce((sum, m) => sum + m.testCoverage, 0) / firstHalf.length;
    const avgCoverageSecond = secondHalf.reduce((sum, m) => sum + m.testCoverage, 0) / secondHalf.length;

    const avgBuildTimeFirst = firstHalf.reduce((sum, m) => sum + m.buildTimeMs, 0) / firstHalf.length;
    const avgBuildTimeSecond = secondHalf.reduce((sum, m) => sum + m.buildTimeMs, 0) / secondHalf.length;

    return {
      qualityTrend: avgQualitySecond - avgQualityFirst,
      coverageTrend: avgCoverageSecond - avgCoverageFirst,
      performanceTrend: avgBuildTimeFirst - avgBuildTimeSecond, // positivo = mais rápido
    };
  }

  /**
   * Gera sugestões com retry logic
   */
  private async generateSuggestionsWithRetry(
    output: CIOutput
  ): Promise<CorrectionSuggestion[]> {
    let lastError: Error | null = null;
    const trackingId = `gen_${output.prNumber}_${Date.now()}`;

    for (let attempt = 1; attempt <= this.retryPolicy.maxAttempts; attempt++) {
      try {
        const attempt_obj: FeedbackAttempt = {
          attemptNumber: attempt,
          timestamp: new Date(),
          status: FeedbackStatus.GENERATING,
        };

        const startTime = Date.now();
        const suggestions = await this.generateSuggestions(output);
        attempt_obj.duration = Date.now() - startTime;
        attempt_obj.status = FeedbackStatus.GENERATED;

        return suggestions;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        if (attempt < this.retryPolicy.maxAttempts) {
          const delay = this.calculateBackoffDelay(attempt);
          await this.delay(delay);
        }
      }
    }

    throw lastError || new Error("Failed to generate suggestions after all retries");
  }

  /**
   * Gera sugestões usando Claude Haiku
   */
  private async generateSuggestions(output: CIOutput): Promise<CorrectionSuggestion[]> {
    const systemPrompt = `Você é um especialista em CI/CD e análise de código.
Sua tarefa é analisar erros de CI e gerar sugestões claras, acionáveis e concisas de como corrigi-los.
Retorne um JSON com um array de sugestões, cada uma com:
- suggestion: texto da sugestão (uma frase clara)
- codeExample: exemplo de código (opcional, máx 5 linhas)
- confidence: número entre 0 e 1
- priority: "low", "medium" ou "high"`;

    const userPrompt = this.buildPromptFromCI(output);

    const response = await (this.client.messages.create as any)({
      model: this.config.model,
      max_tokens: this.config.maxTokens,
      system: systemPrompt,
      messages: [
        {
          role: "user",
          content: userPrompt,
        },
      ],
    });

    const content = response.content[0];
    if (content.type !== "text") {
      throw new Error("Unexpected response format from Claude");
    }

    return this.parseAndValidateSuggestions(output.errors, content.text);
  }

  /**
   * Constrói prompt a partir do CI output
   */
  private buildPromptFromCI(output: CIOutput): string {
    let prompt = `Analize os seguintes erros de CI/CD e gere sugestões de correção:\n\n`;

    prompt += `## Workflow\n- Nome: ${output.workflowName}\n- PR: #${output.prNumber}\n\n`;

    if (output.testResults) {
      prompt += `## Testes\n- Total: ${output.testResults.total}\n- Passou: ${output.testResults.passed}\n- Falhou: ${output.testResults.failed}\n`;
      if (output.testResults.failedTests && output.testResults.failedTests.length > 0) {
        prompt += `- Testes falhados:\n${output.testResults.failedTests
          .slice(0, 5)
          .map((t) => `  - ${t}`)
          .join("\n")}\n`;
      }
      prompt += "\n";
    }

    if (output.coverage) {
      prompt += `## Coverage\n- Linhas: ${output.coverage.lines}%\n- Statements: ${output.coverage.statements}%\n`;
      if (output.coverage.threshold && output.coverage.lines < output.coverage.threshold) {
        prompt += `- ⚠️  Abaixo do threshold de ${output.coverage.threshold}%\n`;
      }
      prompt += "\n";
    }

    prompt += `## Erros Detectados\n`;
    output.errors.forEach((error, idx) => {
      prompt += `\n${idx + 1}. **${error.type}** (${error.severity})\n`;
      prompt += `   Mensagem: ${error.message}\n`;
      if (error.file) {
        prompt += `   Arquivo: ${error.file}`;
        if (error.line) prompt += `:${error.line}`;
        if (error.column) prompt += `:${error.column}`;
        prompt += "\n";
      }
      if (error.context) {
        prompt += `   Contexto:\n   \`\`\`\n${error.context}\n   \`\`\`\n`;
      }
    });

    prompt += `\n## Instruções
Retorne APENAS um JSON válido (sem markdown, sem explicações adicionais) com este schema:
{
  "suggestions": [
    {
      "errorType": "tipo_do_erro",
      "suggestion": "Descrição clara e concisa da solução",
      "codeExample": "código opcional (máx 5 linhas)",
      "confidence": 0.85,
      "priority": "high"
    }
  ]
}`;

    return prompt;
  }

  /**
   * Parse e valida sugestões do Claude
   */
  private parseAndValidateSuggestions(
    errors: CIError[],
    responseText: string
  ): CorrectionSuggestion[] {
    try {
      // Remove markdown code fences se presentes
      let jsonText = responseText.trim();
      if (jsonText.startsWith("```json")) {
        jsonText = jsonText.slice(7);
      } else if (jsonText.startsWith("```")) {
        jsonText = jsonText.slice(3);
      }
      if (jsonText.endsWith("```")) {
        jsonText = jsonText.slice(0, -3);
      }

      const parsed = JSON.parse(jsonText.trim());

      if (!Array.isArray(parsed.suggestions)) {
        throw new Error("Invalid suggestions format");
      }

      return parsed.suggestions
        .map((s: Record<string, unknown>, idx: number) => ({
          errorType: errors[idx]?.type || ErrorType.BUILD_FAILURE,
          originalError: errors[idx],
          suggestion: String(s.suggestion || ""),
          codeExample: this.config.includeCodeExamples ? String(s.codeExample || "") : undefined,
          confidence: typeof s.confidence === "number" ? s.confidence : 0.5,
          priority: ["low", "medium", "high"].includes(String(s.priority))
            ? (String(s.priority) as "low" | "medium" | "high")
            : ("medium" as const),
        }))
        .filter((s: CorrectionSuggestion) => s.suggestion && s.suggestion.length > 0);
    } catch (error) {
      console.error("Failed to parse suggestions:", error);
      return [];
    }
  }

  /**
   * Posta comentário na PR com retry
   */
  private async postCommentWithRetry(comment: PRComment): Promise<string> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.retryPolicy.maxAttempts; attempt++) {
      try {
        const startTime = Date.now();
        const commentId = await this.postCommentToGitHub(comment);
        const duration = Date.now() - startTime;

        console.log(`Comment posted in attempt ${attempt}, duration: ${duration}ms`);
        return commentId;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        const statusCode = this.extractStatusCode(lastError.message);
        if (
          statusCode &&
          !this.retryPolicy.retryableStatusCodes?.includes(statusCode)
        ) {
          throw lastError;
        }

        if (attempt < this.retryPolicy.maxAttempts) {
          const delay = this.calculateBackoffDelay(attempt);
          await this.delay(delay);
        }
      }
    }

    throw lastError || new Error("Failed to post comment after all retries");
  }

  /**
   * Posta comentário no GitHub
   */
  private async postCommentToGitHub(comment: PRComment): Promise<string> {
    const url = `${this.apiBaseUrl}/repos/${comment.owner}/${comment.repo}/issues/${comment.prNumber}/comments`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        "Content-Type": "application/json",
        Accept: "application/vnd.github.v3+json",
      },
      body: JSON.stringify({
        body: comment.body,
        in_reply_to: comment.inReplyTo,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`GitHub API error (${response.status}): ${error}`);
    }

    const data = (await response.json()) as { id: number };
    return String(data.id);
  }

  /**
   * Formata comentário com sugestões
   */
  private formatSuggestionsComment(
    output: CIOutput,
    suggestions: CorrectionSuggestion[]
  ): string {
    let comment = `## 🤖 CI Feedback\n\n`;
    comment += `Detected **${output.errors.length}** issue(s) in workflow **${output.workflowName}**\n\n`;

    comment += `### Issues & Suggestions\n\n`;

    suggestions.forEach((s, idx) => {
      const priorityEmoji = {
        low: "🟢",
        medium: "🟡",
        high: "🔴",
      }[s.priority];

      comment += `${idx + 1}. ${priorityEmoji} **${s.errorType}**\n`;
      comment += `   - Error: ${s.originalError.message}\n`;
      comment += `   - Suggestion: ${s.suggestion}\n`;

      if (s.codeExample) {
        comment += `   - Example:\n`;
        comment += `   \`\`\`\n${s.codeExample}\n   \`\`\`\n`;
      }

      comment += `   - Confidence: ${(s.confidence * 100).toFixed(0)}%\n\n`;
    });

    if (this.config.autoReplyEnabled) {
      comment += `---\n\n`;
      comment += `**Auto-fix suggested.** Would you like me to:\n`;
      comment += `- [ ] Commit these fixes\n`;
      comment += `- [ ] Re-run CI after fixes\n`;
      comment += `- [ ] Create auto-fix PR\n`;
    }

    return comment;
  }

  /**
   * Calcula delay com exponential backoff
   */
  private calculateBackoffDelay(attempt: number): number {
    const delay =
      this.retryPolicy.initialDelayMs *
      Math.pow(this.retryPolicy.backoffFactor, attempt - 1);
    return Math.min(delay, this.retryPolicy.maxDelayMs);
  }

  /**
   * Sleep helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Extrai status code da mensagem de erro
   */
  private extractStatusCode(message: string): number | null {
    const match = message.match(/\((\d{3})\)/);
    return match ? parseInt(match[1], 10) : null;
  }

  /**
   * Retorna histórico de feedback
   */
  public getFeedbackHistory(feedbackId?: string): FeedbackTracking[] {
    if (feedbackId) {
      const tracking = this.feedbackHistory.get(feedbackId);
      return tracking ? [tracking] : [];
    }
    return Array.from(this.feedbackHistory.values());
  }

  /**
   * Retorna estatísticas de feedback
   */
  public getStatistics(): {
    totalFeedbacks: number;
    successRate: number;
    avgTimeSpentMs: number;
    totalSuggestionsGenerated: number;
    totalCommentsPosted: number;
  } {
    const feedbacks = Array.from(this.feedbackHistory.values());
    const successful = feedbacks.filter((f) => f.status === FeedbackStatus.POSTED);

    return {
      totalFeedbacks: feedbacks.length,
      successRate: feedbacks.length > 0 ? successful.length / feedbacks.length : 0,
      avgTimeSpentMs:
        feedbacks.length > 0
          ? feedbacks.reduce((sum, f) => sum + f.totalTimeSpent, 0) / feedbacks.length
          : 0,
      totalSuggestionsGenerated: feedbacks.reduce((sum, f) => sum + f.suggestionsGenerated, 0),
      totalCommentsPosted: feedbacks.reduce((sum, f) => sum + f.commentsPosted, 0),
    };
  }

  /**
   * Limpa histórico de feedback
   */
  public clearHistory(): void {
    this.feedbackHistory.clear();
  }

  /**
   * Retorna feedback em cache para uma PR (Phase 3)
   */
  public getFeedback(prNumber: number): Feedback | undefined {
    return this.feedbackCache.get(prNumber);
  }

  /**
   * Retorna histórico de métricas para uma PR (Phase 3)
   */
  public getMetricsHistory(prNumber: number): Metrics[] {
    return this.metricsHistory.get(prNumber) || [];
  }

  /**
   * Limpa cache de revisores
   */
  public clearReviewerCache(): void {
    this.reviewerCache.clear();
  }

  /**
   * Limpa todo o histórico de métricas
   */
  public clearMetricsHistory(): void {
    this.metricsHistory.clear();
  }

  /**
   * Limpa todos os caches
   */
  public clearAllCaches(): void {
    this.feedbackHistory.clear();
    this.metricsHistory.clear();
    this.feedbackCache.clear();
    this.reviewerCache.clear();
  }
}

/**
 * Factory function para criar FeedbackEngine
 */
export function createFeedbackEngine(
  config: FeedbackEngineConfig
): FeedbackEngine {
  return new FeedbackEngine(config);
}
