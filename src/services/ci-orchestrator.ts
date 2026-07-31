/**
 * CI/CD Orchestrator — Sistema inteligente de orquestração de pipelines
 * Versão: 1.0.0
 *
 * Recursos:
 * - Dispara workflows GitHub Actions
 * - Polling automático de status (30s, máx 5min)
 * - Parsing de output (test results, coverage, lint errors)
 * - Detecção de timeouts e falhas
 * - Integração completa com GitHub API
 * - Métricas e observability
 */

/**
 * Status de execução do workflow
 */
export enum WorkflowRunStatus {
  QUEUED = "queued",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
  TIMED_OUT = "timed_out",
}

/**
 * Conclusão do workflow
 */
export enum WorkflowConclusion {
  SUCCESS = "success",
  FAILURE = "failure",
  NEUTRAL = "neutral",
  CANCELLED = "cancelled",
  TIMED_OUT = "timed_out",
  ACTION_REQUIRED = "action_required",
}

/**
 * Interface para resultado de teste
 */
export interface TestResult {
  name: string;
  passed: number;
  failed: number;
  skipped: number;
  duration: number; // ms
  suites?: Array<{
    name: string;
    passed: number;
    failed: number;
    skipped: number;
  }>;
}

/**
 * Interface para resultado de cobertura
 */
export interface CoverageResult {
  lines: number; // %
  statements: number; // %
  functions: number; // %
  branches: number; // %
  linesCovered?: number;
  linesTotal?: number;
}

/**
 * Interface para erro de linting
 */
export interface LintError {
  file: string;
  line: number;
  column: number;
  message: string;
  rule?: string;
  severity: "error" | "warning";
}

/**
 * Interface para saída de build
 */
export interface BuildOutput {
  logs: string[];
  testResults?: TestResult;
  coverage?: CoverageResult;
  lintErrors?: LintError[];
  duration: number; // ms
}

/**
 * Interface para execução de workflow
 */
export interface WorkflowRun {
  id: number;
  name: string;
  headBranch: string;
  status: WorkflowRunStatus;
  conclusion?: WorkflowConclusion;
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  duration?: number; // ms
}

/**
 * Interface para resultado de orquestração
 */
export interface OrchestrationResult {
  workflowRunId: number;
  status: "success" | "failure";
  workflowStatus: WorkflowRunStatus;
  conclusion: WorkflowConclusion | null;
  buildOutput: BuildOutput;
  duration: number; // ms total
  timestamp: Date;
  error?: string;
}

/**
 * Interface para configuração do orchestrador
 */
export interface CIOrchestratorConfig {
  githubToken: string;
  owner: string;
  repo: string;
  pollingIntervalMs?: number; // default 30000
  maxWaitMs?: number; // default 300000 (5 min)
  workflowId?: string | number; // workflow file name ou ID
}

/**
 * Interface para métricas de CI/CD
 */
export interface CIMetrics {
  timestamp: Date;
  totalWorkflowsTriggered: number;
  successCount: number;
  failureCount: number;
  timeoutCount: number;
  averageDurationMs: number;
  averageTestPassRate: number;
  averageCoverage: CoverageResult;
}

/**
 * Classe principal do CI/CD Orchestrator
 */
export class CIOrchestratorService {
  private config: CIOrchestratorConfig;
  private pollingIntervalMs: number;
  private maxWaitMs: number;
  private apiBaseUrl: string = "https://api.github.com";
  private metrics: CIMetrics = {
    timestamp: new Date(),
    totalWorkflowsTriggered: 0,
    successCount: 0,
    failureCount: 0,
    timeoutCount: 0,
    averageDurationMs: 0,
    averageTestPassRate: 0,
    averageCoverage: { lines: 0, statements: 0, functions: 0, branches: 0 },
  };

  constructor(config: CIOrchestratorConfig) {
    this.config = config;
    this.pollingIntervalMs = config.pollingIntervalMs || 30000;
    this.maxWaitMs = config.maxWaitMs || 300000;

    if (this.pollingIntervalMs < 5000) {
      console.warn(
        "Polling interval too short (< 5s), adjusting to 5000ms for GitHub API rate limits"
      );
      this.pollingIntervalMs = 5000;
    }

    if (this.maxWaitMs < this.pollingIntervalMs) {
      throw new Error(
        "maxWaitMs must be >= pollingIntervalMs"
      );
    }
  }

  /**
   * Dispara um workflow GitHub Actions
   */
  async triggerWorkflow(
    workflowId: string | number,
    branch: string = "main",
    inputs?: Record<string, string>
  ): Promise<number> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/workflows/${workflowId}/dispatches`;

    const payload = {
      ref: branch,
      inputs: inputs || {},
    };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 204) {
        // GitHub retorna 204 No Content quando sucesso
        console.log(
          `Workflow ${workflowId} triggered successfully on branch ${branch}`
        );

        // Aguarda um pouco e depois busca o ID do run mais recente
        await this.delay(2000);
        const runId = await this.getLatestWorkflowRunId(workflowId, branch);

        this.metrics.totalWorkflowsTriggered++;
        return runId;
      } else if (response.status === 422) {
        throw new Error("Workflow not found or invalid branch");
      } else {
        const errorData = await response.json();
        throw new Error(
          `Failed to trigger workflow: ${response.statusText} - ${JSON.stringify(errorData)}`
        );
      }
    } catch (error) {
      throw new Error(
        `Error triggering workflow: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Obtém o ID do run mais recente de um workflow
   */
  private async getLatestWorkflowRunId(
    workflowId: string | number,
    branch: string
  ): Promise<number> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/workflows/${workflowId}/runs?branch=${branch}&per_page=1`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get workflow runs: ${response.statusText}`);
    }

    const data = (await response.json()) as { workflow_runs: Array<{ id: number }> };

    if (!data.workflow_runs || data.workflow_runs.length === 0) {
      throw new Error("No workflow runs found");
    }

    return data.workflow_runs[0].id;
  }

  /**
   * Monitora um workflow run até conclusão ou timeout
   */
  async monitorWorkflowRun(
    runId: number,
    workflowId?: string | number
  ): Promise<OrchestrationResult> {
    const startTime = Date.now();
    const effectiveWorkflowId = workflowId || this.config.workflowId;

    if (!effectiveWorkflowId) {
      throw new Error(
        "workflowId must be provided in config or as parameter"
      );
    }

    try {
      while (true) {
        const elapsedMs = Date.now() - startTime;

        // Verifica timeout
        if (elapsedMs > this.maxWaitMs) {
          this.metrics.timeoutCount++;
          return {
            workflowRunId: runId,
            status: "failure",
            workflowStatus: WorkflowRunStatus.TIMED_OUT,
            conclusion: WorkflowConclusion.TIMED_OUT,
            buildOutput: {
              logs: ["Workflow execution timed out after max wait time"],
              duration: this.maxWaitMs,
            },
            duration: elapsedMs,
            timestamp: new Date(),
            error: `Workflow monitoring timed out after ${this.maxWaitMs}ms`,
          };
        }

        // Busca status do run
        const run = await this.getWorkflowRunStatus(runId);

        // Se completado, processa resultado
        if (run.status === WorkflowRunStatus.COMPLETED) {
          const buildOutput = await this.fetchBuildOutput(runId);
          const result: OrchestrationResult = {
            workflowRunId: runId,
            status:
              run.conclusion === WorkflowConclusion.SUCCESS
                ? "success"
                : "failure",
            workflowStatus: run.status,
            conclusion: run.conclusion || null,
            buildOutput,
            duration: elapsedMs,
            timestamp: new Date(),
          };

          // Atualiza métricas
          if (result.status === "success") {
            this.metrics.successCount++;
          } else {
            this.metrics.failureCount++;
          }

          this.updateAverageMetrics(result);

          return result;
        }

        // Ainda não completou, aguarda e tenta novamente
        console.log(
          `Workflow ${runId} still ${run.status}... (${elapsedMs}ms elapsed)`
        );
        await this.delay(this.pollingIntervalMs);
      }
    } catch (error) {
      const elapsedMs = Date.now() - startTime;
      this.metrics.failureCount++;

      return {
        workflowRunId: runId,
        status: "failure",
        workflowStatus: WorkflowRunStatus.FAILED,
        conclusion: WorkflowConclusion.FAILURE,
        buildOutput: {
          logs: [
            `Error monitoring workflow: ${error instanceof Error ? error.message : String(error)}`,
          ],
          duration: elapsedMs,
        },
        duration: elapsedMs,
        timestamp: new Date(),
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  /**
   * Obtém status de um workflow run
   */
  private async getWorkflowRunStatus(runId: number): Promise<WorkflowRun> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/runs/${runId}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get workflow run status: ${response.statusText}`);
    }

    const data = await response.json() as {
      id: number;
      name: string;
      head_branch: string;
      status: string;
      conclusion: string | null;
      created_at: string;
      updated_at: string;
      run_started_at?: string;
    };

    return {
      id: data.id,
      name: data.name,
      headBranch: data.head_branch,
      status: this.normalizeStatus(data.status),
      conclusion: data.conclusion as WorkflowConclusion | null,
      createdAt: new Date(data.created_at),
      updatedAt: new Date(data.updated_at),
    };
  }

  /**
   * Busca output do build (logs, test results, coverage, lint errors)
   */
  private async fetchBuildOutput(runId: number): Promise<BuildOutput> {
    const startTime = Date.now();
    const logs: string[] = [];
    let testResults: TestResult | undefined;
    let coverage: CoverageResult | undefined;
    const lintErrors: LintError[] = [];

    try {
      // Busca logs de jobs
      const jobs = await this.getWorkflowJobs(runId);

      for (const job of jobs) {
        const jobLogs = await this.getJobLogs(runId, job.id);
        logs.push(`=== Job: ${job.name} ===`);
        logs.push(jobLogs);

        // Tenta parsear test results dos logs
        const parsed = this.parseTestResults(jobLogs);
        if (parsed && !testResults) {
          testResults = parsed;
        }

        // Tenta parsear coverage dos logs
        const cov = this.parseCoverage(jobLogs);
        if (cov && !coverage) {
          coverage = cov;
        }

        // Tenta parsear lint errors dos logs
        const lints = this.parseLintErrors(jobLogs);
        lintErrors.push(...lints);
      }
    } catch (error) {
      logs.push(
        `Error fetching build output: ${error instanceof Error ? error.message : String(error)}`
      );
    }

    return {
      logs,
      testResults,
      coverage,
      lintErrors: lintErrors.length > 0 ? lintErrors : undefined,
      duration: Date.now() - startTime,
    };
  }

  /**
   * Obtém jobs de um workflow run
   */
  private async getWorkflowJobs(
    runId: number
  ): Promise<Array<{ id: number; name: string }>> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/runs/${runId}/jobs`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get workflow jobs: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      jobs: Array<{ id: number; name: string }>;
    };

    return data.jobs;
  }

  /**
   * Obtém logs de um job
   */
  private async getJobLogs(runId: number, jobId: number): Promise<string> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/jobs/${jobId}/logs`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      if (response.status === 410) {
        // Logs expirados
        return "[Logs expired]";
      }
      throw new Error(`Failed to get job logs: ${response.statusText}`);
    }

    return await response.text();
  }

  /**
   * Parseia resultado de testes dos logs
   */
  private parseTestResults(logs: string): TestResult | null {
    // Exemplo de padrões que podem aparecer nos logs
    const testPatterns = [
      /Tests:\s*(\d+)\s*passed,?\s*(\d+)?\s*failed,?\s*(\d+)?\s*skipped/i,
      /(\d+)\s*passed.*?(\d+)?\s*failed.*?(\d+)?\s*skipped/i,
    ];

    for (const pattern of testPatterns) {
      const match = logs.match(pattern);
      if (match) {
        return {
          name: "Jest/Test Suite",
          passed: parseInt(match[1] || "0", 10),
          failed: parseInt(match[2] || "0", 10),
          skipped: parseInt(match[3] || "0", 10),
          duration: this.extractDuration(logs),
        };
      }
    }

    // Padrão alternativo: resultado JSON nos logs
    const jsonMatch = logs.match(/"numPassedTests":\s*(\d+)[\s\S]*?"numFailedTests":\s*(\d+)/);
    if (jsonMatch) {
      return {
        name: "Jest/Test Suite",
        passed: parseInt(jsonMatch[1], 10),
        failed: parseInt(jsonMatch[2], 10),
        skipped: 0,
        duration: this.extractDuration(logs),
      };
    }

    return null;
  }

  /**
   * Parseia cobertura dos logs
   */
  private parseCoverage(logs: string): CoverageResult | null {
    // Padrões de cobertura
    const coveragePatterns = [
      /Lines\s*:\s*([\d.]+)%[\s\S]*?Statements\s*:\s*([\d.]+)%[\s\S]*?Functions\s*:\s*([\d.]+)%[\s\S]*?Branches\s*:\s*([\d.]+)%/i,
      /coverage[\s\S]*?lines:\s*([\d.]+)%[\s\S]*?statements:\s*([\d.]+)%[\s\S]*?functions:\s*([\d.]+)%[\s\S]*?branches:\s*([\d.]+)%/i,
    ];

    for (const pattern of coveragePatterns) {
      const match = logs.match(pattern);
      if (match) {
        return {
          lines: parseFloat(match[1] || "0"),
          statements: parseFloat(match[2] || "0"),
          functions: parseFloat(match[3] || "0"),
          branches: parseFloat(match[4] || "0"),
        };
      }
    }

    return null;
  }

  /**
   * Parseia erros de lint dos logs
   */
  private parseLintErrors(logs: string): LintError[] {
    const errors: LintError[] = [];

    // Padrão para ESLint
    const eslintPattern =
      /^([^:\s]+):(\d+):(\d+):\s*(\w+)\s*-\s*(.+?)\s*\(([^)]+)\)/gm;

    let match;
    while ((match = eslintPattern.exec(logs)) !== null) {
      errors.push({
        file: match[1],
        line: parseInt(match[2], 10),
        column: parseInt(match[3], 10),
        severity: match[4].toLowerCase() as "error" | "warning",
        message: match[5],
        rule: match[6],
      });
    }

    return errors;
  }

  /**
   * Extrai duração dos logs
   */
  private extractDuration(logs: string): number {
    const durationPattern = /took\s+(\d+\.?\d*)\s*(?:s|ms)/i;
    const match = logs.match(durationPattern);

    if (match) {
      const value = parseFloat(match[1]);
      // Se termina em 's', converte para ms
      return match[0].includes("s") && !match[0].includes("ms")
        ? value * 1000
        : value;
    }

    return 0;
  }

  /**
   * Normaliza status do workflow
   */
  private normalizeStatus(status: string): WorkflowRunStatus {
    const statusMap: Record<string, WorkflowRunStatus> = {
      queued: WorkflowRunStatus.QUEUED,
      in_progress: WorkflowRunStatus.IN_PROGRESS,
      completed: WorkflowRunStatus.COMPLETED,
      failed: WorkflowRunStatus.FAILED,
      cancelled: WorkflowRunStatus.CANCELLED,
      timed_out: WorkflowRunStatus.TIMED_OUT,
    };

    return statusMap[status.toLowerCase()] || WorkflowRunStatus.QUEUED;
  }

  /**
   * Atualiza métricas de average
   */
  private updateAverageMetrics(result: OrchestrationResult): void {
    const { buildOutput } = result;

    // Atualiza duração média
    const totalDuration =
      this.metrics.averageDurationMs *
        (this.metrics.successCount + this.metrics.failureCount - 1) +
      buildOutput.duration;
    this.metrics.averageDurationMs = Math.round(
      totalDuration / (this.metrics.successCount + this.metrics.failureCount)
    );

    // Atualiza test pass rate média
    if (buildOutput.testResults) {
      const total =
        buildOutput.testResults.passed + buildOutput.testResults.failed;
      const passRate = total > 0 ? buildOutput.testResults.passed / total : 0;
      const count = this.metrics.successCount + this.metrics.failureCount;
      this.metrics.averageTestPassRate =
        (this.metrics.averageTestPassRate * (count - 1) + passRate) / count;
    }

    // Atualiza cobertura média
    if (buildOutput.coverage) {
      const count = this.metrics.successCount + this.metrics.failureCount;
      this.metrics.averageCoverage.lines =
        (this.metrics.averageCoverage.lines * (count - 1) +
          buildOutput.coverage.lines) /
        count;
      this.metrics.averageCoverage.statements =
        (this.metrics.averageCoverage.statements * (count - 1) +
          buildOutput.coverage.statements) /
        count;
      this.metrics.averageCoverage.functions =
        (this.metrics.averageCoverage.functions * (count - 1) +
          buildOutput.coverage.functions) /
        count;
      this.metrics.averageCoverage.branches =
        (this.metrics.averageCoverage.branches * (count - 1) +
          buildOutput.coverage.branches) /
        count;
    }
  }

  /**
   * Fluxo completo: dispara e monitora
   */
  async executeWorkflow(
    workflowId: string | number,
    branch?: string,
    inputs?: Record<string, string>
  ): Promise<OrchestrationResult> {
    const runId = await this.triggerWorkflow(workflowId, branch, inputs);
    return await this.monitorWorkflowRun(runId, workflowId);
  }

  /**
   * Obtém métricas atuais
   */
  getMetrics(): CIMetrics {
    return {
      ...this.metrics,
      timestamp: new Date(),
    };
  }

  /**
   * Reseta métricas
   */
  resetMetrics(): void {
    this.metrics = {
      timestamp: new Date(),
      totalWorkflowsTriggered: 0,
      successCount: 0,
      failureCount: 0,
      timeoutCount: 0,
      averageDurationMs: 0,
      averageTestPassRate: 0,
      averageCoverage: { lines: 0, statements: 0, functions: 0, branches: 0 },
    };
  }

  /**
   * Helper para delay
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * Factory function para criar instância
 */
export function createCIOrchestratorService(
  config: CIOrchestratorConfig
): CIOrchestratorService {
  return new CIOrchestratorService(config);
}
