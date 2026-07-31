/**
 * Feedback Engine — Sistema inteligente de feedback de CI/CD
 * Versão: 1.0.0
 *
 * Recursos:
 * - Lê outputs de CI (testes, lint, coverage)
 * - Gera sugestões de correção via Claude Haiku
 * - Posta comentários automáticos na PR
 * - Retry logic com exponential backoff
 * - Rastreia tentativas e tempo gasto
 * - Propõe iterações automáticas de fix
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
  private config: Required<FeedbackEngineConfig>;
  private retryPolicy: RetryPolicy;
  private apiBaseUrl = "https://api.github.com";
  private feedbackHistory: Map<string, FeedbackTracking> = new Map();

  constructor(config: FeedbackEngineConfig) {
    this.client = new Anthropic({
      apiKey: config.anthropicApiKey || process.env.ANTHROPIC_API_KEY,
    });

    this.config = {
      anthropicApiKey: config.anthropicApiKey || process.env.ANTHROPIC_API_KEY || "",
      githubToken: config.githubToken,
      owner: config.owner,
      repo: config.repo,
      model: config.model || "claude-3-5-haiku-20241022",
      maxTokens: config.maxTokens || 1000,
      includeCodeExamples: config.includeCodeExamples ?? true,
      autoReplyEnabled: config.autoReplyEnabled ?? true,
      notifyOnNewIssues: config.notifyOnNewIssues ?? true,
    };

    this.retryPolicy = {
      ...DEFAULT_RETRY_POLICY,
      ...(config.retryPolicy || {}),
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

    const response = await this.client.messages.create({
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
        .map((s: any, idx: number) => ({
          errorType: errors[idx]?.type || ErrorType.BUILD_FAILURE,
          originalError: errors[idx],
          suggestion: s.suggestion || "",
          codeExample: this.config.includeCodeExamples ? s.codeExample : undefined,
          confidence: typeof s.confidence === "number" ? s.confidence : 0.5,
          priority: ["low", "medium", "high"].includes(s.priority) ? s.priority : "medium",
        }))
        .filter((s) => s.suggestion && s.suggestion.length > 0);
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
}

/**
 * Factory function para criar FeedbackEngine
 */
export function createFeedbackEngine(
  config: FeedbackEngineConfig
): FeedbackEngine {
  return new FeedbackEngine(config);
}
