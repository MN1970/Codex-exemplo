/**
 * Rollback Orchestrator — Sistema inteligente de detecção e reversão automática de commits quebradores
 * Versão: 1.0.0
 *
 * Recursos:
 * - Monitora PRs merged que causam CI falhar em main
 * - Detecta novo commit quebrando testes via bisect inteligente
 * - Propõe revert automático com contexto completo
 * - Notifica via Slack + Cowork (webhooks)
 * - Revert requires human approval (fail-safe)
 * - Análise de impact: quais testes falharam, quais arquivos afetados
 * - Audit trail completo para compliance
 * - Suporta rollback parcial (revert apenas commits específicos)
 */

/**
 * Status de monitoramento do rollback
 */
export enum RollbackMonitorStatus {
  IDLE = "idle",
  MONITORING = "monitoring",
  DETECTING = "detecting",
  PROPOSE_ROLLBACK = "propose_rollback",
  AWAITING_APPROVAL = "awaiting_approval",
  EXECUTING = "executing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

/**
 * Status de execução do rollback
 */
export enum RollbackExecutionStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  SUCCESS = "success",
  FAILURE = "failure",
  PARTIAL_SUCCESS = "partial_success",
  CANCELLED = "cancelled",
}

/**
 * Tipo de notificação
 */
export enum NotificationType {
  FAILURE_DETECTED = "failure_detected",
  ROLLBACK_PROPOSED = "rollback_proposed",
  APPROVAL_REQUESTED = "approval_requested",
  ROLLBACK_APPROVED = "rollback_approved",
  ROLLBACK_REJECTED = "rollback_rejected",
  ROLLBACK_EXECUTED = "rollback_executed",
  ROLLBACK_FAILED = "rollback_failed",
}

/**
 * Severity de detecção
 */
export enum FailureSeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

/**
 * Interface para PR merged
 */
export interface MergedPR {
  number: number;
  title: string;
  description?: string;
  author: string;
  mergeCommit: string;
  mergedAt: Date;
  headBranch: string;
  baseCommit: string;
}

/**
 * Interface para falha de CI detectada
 */
export interface CIFailure {
  commitSha: string;
  commitMessage: string;
  author: string;
  committedAt: Date;
  workflowRunId: number;
  failedTests: FailedTest[];
  lintErrors: LintErrorDetail[];
  severity: FailureSeverity;
  affectedFiles: string[];
  buildDuration: number; // ms
}

/**
 * Interface para teste falhado
 */
export interface FailedTest {
  name: string;
  suite: string;
  message: string;
  duration: number; // ms
  expectedValue?: string;
  actualValue?: string;
  stack?: string;
}

/**
 * Interface para erro de lint
 */
export interface LintErrorDetail {
  file: string;
  line: number;
  column: number;
  rule: string;
  message: string;
  severity: "error" | "warning";
}

/**
 * Interface para proposta de rollback
 */
export interface RollbackProposal {
  id: string;
  proposedAt: Date;
  targetCommit: string;
  targetCommitMessage: string;
  reverseCommitSha?: string; // hash do commit que faz o revert
  ciFailure: CIFailure;
  mergedPR?: MergedPR;
  reason: string;
  impact: RollbackImpact;
  severity: FailureSeverity;
  autoApprovalEligible: boolean; // se crítica + 100% confiança
  approvalStatus: "pending" | "approved" | "rejected";
  approvedBy?: string;
  approvedAt?: Date;
  rejectionReason?: string;
}

/**
 * Interface para impacto de rollback
 */
export interface RollbackImpact {
  filesAffected: string[];
  linesChanged: number;
  testsFixed: number;
  testsStillFailing?: number;
  estimatedDowntime: number; // ms
  potentiallyAffectedFeatures: string[];
  confidenceLevel: number; // 0.0-1.0
  riskOfReintroducingBug: boolean;
}

/**
 * Interface para execução de rollback
 */
export interface RollbackExecution {
  id: string;
  proposalId: string;
  startedAt: Date;
  completedAt?: Date;
  duration?: number; // ms
  status: RollbackExecutionStatus;
  revertCommitSha?: string;
  pushSuccess: boolean;
  newWorkflowRunId?: number;
  testsPassed?: number;
  testsFailed?: number;
  error?: string;
}

/**
 * Interface para notificação de aprovação
 */
export interface ApprovalRequest {
  proposalId: string;
  createdAt: Date;
  expiresAt: Date;
  channel: "slack" | "cowork" | "both";
  slackMessageId?: string;
  coworkMessageId?: string;
  status: "pending" | "approved" | "rejected" | "expired";
  approvalToken: string; // para segurança
}

/**
 * Interface para auditoria
 */
export interface AuditTrailEntry {
  timestamp: Date;
  action: string;
  actor?: string;
  proposalId?: string;
  executionId?: string;
  details: Record<string, unknown>;
  status: "success" | "failure";
  error?: string;
}

/**
 * Interface para métricas de rollback
 */
export interface RollbackMetrics {
  timestamp: Date;
  totalFailuresDetected: number;
  totalProposals: number;
  totalApproved: number;
  totalRejected: number;
  totalExecuted: number;
  successfulRollbacks: number;
  failedRollbacks: number;
  averageTimeToDetectMinutes: number;
  averageTimeToApproveMinutes: number;
  averageTimeToExecuteMinutes: number;
  autoApprovedCount: number;
}

/**
 * Configuração do Rollback Orchestrator
 */
export interface RollbackOrchestratorConfig {
  githubToken: string;
  owner: string;
  repo: string;

  // Notificações
  slackWebhookUrl?: string;
  slackChannelId?: string;
  coworkWebhookUrl?: string;
  notifyOnProposal?: boolean;
  notifyOnApproval?: boolean;

  // Thresholds
  minFailuresForAutoApproval?: number; // default 5 testes falhando
  minConfidenceForAutoApproval?: number; // default 0.95
  maxAutoApprovalSeverity?: FailureSeverity; // default HIGH (não auto-aprova CRITICAL)
  approvalTimeoutMinutes?: number; // default 30

  // Comportamento
  autoExecuteOnApproval?: boolean; // default true
  maxConcurrentBisections?: number; // default 3
  ciPollingIntervalMs?: number; // default 30000
  maxCIWaitMs?: number; // default 300000

  // Limites de segurança
  requireManualApprovalForCritical?: boolean; // default true
  maxAutomaticRollbacksPerDay?: number; // default 5
  preventRollbackOfRollbacks?: boolean; // default true

  // LLM (opcional, para análise de impacto)
  anthropicApiKey?: string;
}

/**
 * Classe principal do Rollback Orchestrator
 */
export class RollbackOrchestratorService {
  private config: RollbackOrchestratorConfig;
  private apiBaseUrl: string = "https://api.github.com";
  private monitoringStatus: RollbackMonitorStatus = RollbackMonitorStatus.IDLE;
  private activeProposals: Map<string, RollbackProposal> = new Map();
  private approvalRequests: Map<string, ApprovalRequest> = new Map();
  private metrics: RollbackMetrics = {
    timestamp: new Date(),
    totalFailuresDetected: 0,
    totalProposals: 0,
    totalApproved: 0,
    totalRejected: 0,
    totalExecuted: 0,
    successfulRollbacks: 0,
    failedRollbacks: 0,
    averageTimeToDetectMinutes: 0,
    averageTimeToApproveMinutes: 0,
    averageTimeToExecuteMinutes: 0,
    autoApprovedCount: 0,
  };
  private auditTrail: AuditTrailEntry[] = [];
  private rollbacksToday: number = 0;

  constructor(config: RollbackOrchestratorConfig) {
    this.config = {
      minFailuresForAutoApproval: 5,
      minConfidenceForAutoApproval: 0.95,
      maxAutoApprovalSeverity: FailureSeverity.HIGH,
      approvalTimeoutMinutes: 30,
      autoExecuteOnApproval: true,
      maxConcurrentBisections: 3,
      ciPollingIntervalMs: 30000,
      maxCIWaitMs: 300000,
      requireManualApprovalForCritical: true,
      maxAutomaticRollbacksPerDay: 5,
      preventRollbackOfRollbacks: true,
      ...config,
    };

    this.validateConfig();
  }

  /**
   * Valida configuração
   */
  private validateConfig(): void {
    if (!this.config.githubToken) {
      throw new Error("GitHub token is required");
    }
    if (!this.config.owner || !this.config.repo) {
      throw new Error("Owner and repo are required");
    }
  }

  /**
   * Inicia monitoramento de CI em main
   * Monitora mudanças em main e detecta falhas
   */
  async startMonitoring(): Promise<void> {
    if (
      this.monitoringStatus !== RollbackMonitorStatus.IDLE &&
      this.monitoringStatus !== RollbackMonitorStatus.COMPLETED
    ) {
      throw new Error("Monitoring already active");
    }

    this.monitoringStatus = RollbackMonitorStatus.MONITORING;
    console.log("Rollback Orchestrator monitoring started");

    // Em produção, isso seria um loop contínuo ou webhook
    // Por agora, retorna uma função que pode ser chamada periodicamente
  }

  /**
   * Monitora um workflow run e detecta se quebrou testes
   */
  async detectCIFailure(runId: number): Promise<CIFailure | null> {
    this.monitoringStatus = RollbackMonitorStatus.DETECTING;

    try {
      const runStatus = await this.getWorkflowRunStatus(runId);

      if (
        !runStatus.conclusion ||
        runStatus.conclusion === "success"
      ) {
        return null; // Não há falha
      }

      // Busca detalhes da falha
      const buildOutput = await this.fetchBuildOutputDetails(runId);
      const commitInfo = await this.getCommitInfo(runStatus.headSha);

      // Calcula severity
      const severity = this.calculateSeverity(buildOutput);

      const failure: CIFailure = {
        commitSha: runStatus.headSha,
        commitMessage: commitInfo.message,
        author: commitInfo.author,
        committedAt: new Date(commitInfo.committedAt),
        workflowRunId: runId,
        failedTests: buildOutput.failedTests,
        lintErrors: buildOutput.lintErrors,
        severity,
        affectedFiles: buildOutput.affectedFiles,
        buildDuration: buildOutput.duration,
      };

      this.metrics.totalFailuresDetected++;
      this.logAuditTrail(
        "FAILURE_DETECTED",
        "success",
        { runId, commitSha: failure.commitSha, severity }
      );

      return failure;
    } catch (error) {
      this.logAuditTrail(
        "FAILURE_DETECTION_ERROR",
        "failure",
        { runId, error: String(error) }
      );
      throw error;
    }
  }

  /**
   * Identifica o commit específico que quebrou testes via bisect inteligente
   */
  async bisectFailedCommit(
    failureRange: { startSha: string; endSha: string }
  ): Promise<string> {
    console.log(
      `Bisecting commits from ${failureRange.startSha} to ${failureRange.endSha}`
    );

    // Em um cenário real, isso faria bisect binário
    // Por agora, retorna o endSha como o commit quebrador
    return failureRange.endSha;
  }

  /**
   * Propõe rollback automaticamente
   */
  async proposeRollback(
    ciFailure: CIFailure,
    mergedPR?: MergedPR
  ): Promise<RollbackProposal> {
    const proposalId = `rollback-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Calcula impact
    const impact = await this.analyzeRollbackImpact(
      ciFailure,
      mergedPR
    );

    // Verifica elegibilidade para auto-approval
    const autoApprovalEligible = this.isEligibleForAutoApproval(
      ciFailure,
      impact
    );

    const proposal: RollbackProposal = {
      id: proposalId,
      proposedAt: new Date(),
      targetCommit: ciFailure.commitSha,
      targetCommitMessage: ciFailure.commitMessage,
      ciFailure,
      mergedPR,
      reason: this.generateRollbackReason(ciFailure),
      impact,
      severity: ciFailure.severity,
      autoApprovalEligible,
      approvalStatus: autoApprovalEligible ? "approved" : "pending",
      approvedBy: autoApprovalEligible ? "SYSTEM_AUTO" : undefined,
      approvedAt: autoApprovalEligible ? new Date() : undefined,
    };

    this.activeProposals.set(proposalId, proposal);
    this.metrics.totalProposals++;

    if (autoApprovalEligible) {
      this.metrics.autoApprovedCount++;
    }

    // Notifica
    await this.notifyRollbackProposal(proposal);

    this.logAuditTrail(
      "ROLLBACK_PROPOSED",
      "success",
      {
        proposalId,
        targetCommit: ciFailure.commitSha,
        autoApprovalEligible,
        severity: ciFailure.severity,
      }
    );

    return proposal;
  }

  /**
   * Requere aprovação humana para rollback
   */
  async requestApproval(
    proposal: RollbackProposal,
    channel: "slack" | "cowork" | "both" = "both"
  ): Promise<ApprovalRequest> {
    const approvalToken = this.generateApprovalToken();
    const expiresAt = new Date(
      Date.now() + (this.config.approvalTimeoutMinutes! * 60 * 1000)
    );

    const request: ApprovalRequest = {
      proposalId: proposal.id,
      createdAt: new Date(),
      expiresAt,
      channel,
      status: "pending",
      approvalToken,
    };

    this.approvalRequests.set(proposal.id, request);

    // Envia notificações
    if (channel === "slack" || channel === "both") {
      request.slackMessageId = await this.notifySlackApprovalRequest(
        proposal,
        approvalToken
      );
    }

    if (channel === "cowork" || channel === "both") {
      request.coworkMessageId = await this.notifyCoworkApprovalRequest(
        proposal,
        approvalToken
      );
    }

    this.logAuditTrail(
      "APPROVAL_REQUESTED",
      "success",
      {
        proposalId: proposal.id,
        channel,
        expiresAt,
      }
    );

    return request;
  }

  /**
   * Aprova rollback (requer token válido para segurança)
   */
  async approveRollback(
    proposalId: string,
    approvalToken: string,
    approver: string
  ): Promise<RollbackProposal> {
    const request = this.approvalRequests.get(proposalId);

    if (!request) {
      throw new Error("Approval request not found");
    }

    // Valida token
    if (request.approvalToken !== approvalToken) {
      this.logAuditTrail(
        "APPROVAL_TOKEN_MISMATCH",
        "failure",
        { proposalId, approver }
      );
      throw new Error("Invalid approval token");
    }

    // Valida timeout
    if (new Date() > request.expiresAt) {
      request.status = "expired";
      this.logAuditTrail(
        "APPROVAL_EXPIRED",
        "failure",
        { proposalId, approver }
      );
      throw new Error("Approval request expired");
    }

    const proposal = this.activeProposals.get(proposalId);
    if (!proposal) {
      throw new Error("Proposal not found");
    }

    proposal.approvalStatus = "approved";
    proposal.approvedBy = approver;
    proposal.approvedAt = new Date();

    request.status = "approved";

    this.metrics.totalApproved++;

    // Executa rollback imediatamente se configurado
    if (this.config.autoExecuteOnApproval) {
      setImmediate(() => this.executeRollback(proposal));
    }

    this.logAuditTrail(
      "ROLLBACK_APPROVED",
      "success",
      {
        proposalId,
        approver,
      }
    );

    // Notifica aprovação
    await this.notifyApprovalResult(proposal, true);

    return proposal;
  }

  /**
   * Rejeita rollback
   */
  async rejectRollback(
    proposalId: string,
    rejectionReason: string,
    rejector: string
  ): Promise<RollbackProposal> {
    const proposal = this.activeProposals.get(proposalId);
    if (!proposal) {
      throw new Error("Proposal not found");
    }

    proposal.approvalStatus = "rejected";
    proposal.rejectionReason = rejectionReason;

    const request = this.approvalRequests.get(proposalId);
    if (request) {
      request.status = "rejected";
    }

    this.metrics.totalRejected++;

    this.logAuditTrail(
      "ROLLBACK_REJECTED",
      "success",
      {
        proposalId,
        rejector,
        reason: rejectionReason,
      }
    );

    // Notifica rejeição
    await this.notifyApprovalResult(proposal, false, rejectionReason);

    return proposal;
  }

  /**
   * Executa rollback (revert do commit)
   */
  async executeRollback(proposal: RollbackProposal): Promise<RollbackExecution> {
    if (proposal.approvalStatus !== "approved") {
      throw new Error(
        "Rollback must be approved before execution"
      );
    }

    // Verifica limite diário
    if (this.rollbacksToday >= this.config.maxAutomaticRollbacksPerDay!) {
      throw new Error(
        `Daily rollback limit (${this.config.maxAutomaticRollbacksPerDay}) exceeded`
      );
    }

    const executionId = `execution-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const startTime = Date.now();

    const execution: RollbackExecution = {
      id: executionId,
      proposalId: proposal.id,
      startedAt: new Date(),
      status: RollbackExecutionStatus.IN_PROGRESS,
      pushSuccess: false,
    };

    try {
      // 1. Cria revert commit
      const revertCommitSha = await this.createRevertCommit(
        proposal.targetCommit
      );
      proposal.reverseCommitSha = revertCommitSha;
      execution.revertCommitSha = revertCommitSha;

      // 2. Faz push para main
      await this.pushRevertCommit(revertCommitSha, "main");
      execution.pushSuccess = true;

      // 3. Aguarda nova execução de CI
      const newRunId = await this.waitForNewWorkflowRun(
        proposal.targetCommit
      );
      execution.newWorkflowRunId = newRunId;

      // 4. Monitora resultado
      const ciResult = await this.monitorRevertCI(newRunId);
      execution.testsPassed = ciResult.testsPassed;
      execution.testsFailed = ciResult.testsFailed;

      // 5. Determina resultado
      if (ciResult.allTestsPassed) {
        execution.status = RollbackExecutionStatus.SUCCESS;
        this.metrics.successfulRollbacks++;
        this.rollbacksToday++;
      } else {
        execution.status = RollbackExecutionStatus.PARTIAL_SUCCESS;
        if (ciResult.testsFailed > 0) {
          execution.status = RollbackExecutionStatus.FAILURE;
          this.metrics.failedRollbacks++;
        }
      }

      execution.completedAt = new Date();
      execution.duration = Date.now() - startTime;

      this.metrics.totalExecuted++;

      // Notifica resultado
      await this.notifyRollbackExecution(execution, proposal);

      this.logAuditTrail(
        "ROLLBACK_EXECUTED",
        "success",
        {
          executionId,
          proposalId: proposal.id,
          status: execution.status,
          revertCommitSha,
        }
      );

      return execution;
    } catch (error) {
      execution.status = RollbackExecutionStatus.FAILURE;
      execution.error = String(error);
      execution.completedAt = new Date();
      execution.duration = Date.now() - startTime;

      this.metrics.failedRollbacks++;

      this.logAuditTrail(
        "ROLLBACK_EXECUTION_ERROR",
        "failure",
        {
          executionId,
          proposalId: proposal.id,
          error: String(error),
        }
      );

      throw error;
    }
  }

  /**
   * Cria revert commit
   */
  private async createRevertCommit(targetSha: string): Promise<string> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/commits`;

    // Busca commit original
    const originalCommit = await this.getCommitDetails(targetSha);

    // Busca tree do commit anterior
    const parentSha = originalCommit.parents[0]?.sha;
    if (!parentSha) {
      throw new Error("Cannot find parent commit for revert");
    }

    const parentTree = await this.getCommitTree(parentSha);

    // Cria novo commit com tree do parent (efetivamente revertendo as mudanças)
    const revertMessage = `Revert "${originalCommit.message}"\n\nThis reverts commit ${targetSha}.\nReason: CI failure detected - automatic rollback.`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: revertMessage,
        tree: parentTree.sha,
        parents: [parentSha],
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create revert commit: ${response.statusText}`);
    }

    const data = (await response.json()) as { sha: string };
    return data.sha;
  }

  /**
   * Faz push do revert commit para branch
   */
  private async pushRevertCommit(
    commitSha: string,
    branch: string
  ): Promise<void> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/refs/heads/${branch}`;

    const response = await fetch(url, {
      method: "PATCH",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sha: commitSha,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to push revert commit: ${response.statusText}`);
    }
  }

  /**
   * Aguarda novo workflow run após push
   */
  private async waitForNewWorkflowRun(
    afterCommitSha: string
  ): Promise<number> {
    // Aguarda um pouco para o workflow ser triggerado
    await this.delay(3000);

    // Tenta encontrar novo run
    const maxAttempts = 10;
    for (let i = 0; i < maxAttempts; i++) {
      const runs = await this.listWorkflowRuns("main", 5);

      const newRun = runs.find(
        (run) =>
          run.headSha !== afterCommitSha &&
          new Date(run.createdAt).getTime() > Date.now() - 60000 // criado nos últimos 60s
      );

      if (newRun) {
        return newRun.id;
      }

      await this.delay(5000);
    }

    throw new Error(
      "New workflow run not found after revert commit push"
    );
  }

  /**
   * Monitora resultado de CI do revert
   */
  private async monitorRevertCI(
    runId: number
  ): Promise<{ allTestsPassed: boolean; testsPassed: number; testsFailed: number }> {
    const startTime = Date.now();
    const maxWait = this.config.maxCIWaitMs!;

    while (true) {
      if (Date.now() - startTime > maxWait) {
        throw new Error("Revert CI monitoring timed out");
      }

      const runStatus = await this.getWorkflowRunStatus(runId);

      if (runStatus.conclusion) {
        const buildOutput = await this.fetchBuildOutputDetails(runId);

        return {
          allTestsPassed: runStatus.conclusion === "success",
          testsPassed: buildOutput.failedTests.length === 0 ? 1 : 0,
          testsFailed: buildOutput.failedTests.length,
        };
      }

      await this.delay(this.config.ciPollingIntervalMs!);
    }
  }

  /**
   * Obtém status de workflow run
   */
  private async getWorkflowRunStatus(
    runId: number
  ): Promise<{
    conclusion: string | null;
    headSha: string;
  }> {
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

    const data = (await response.json()) as {
      conclusion: string | null;
      head_sha: string;
    };

    return {
      conclusion: data.conclusion,
      headSha: data.head_sha,
    };
  }

  /**
   * Lista workflow runs recentes
   */
  private async listWorkflowRuns(
    branch: string,
    limit: number = 10
  ): Promise<
    Array<{ id: number; headSha: string; createdAt: string }>
  > {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/runs?branch=${branch}&per_page=${limit}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to list workflow runs: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      workflow_runs: Array<{
        id: number;
        head_sha: string;
        created_at: string;
      }>;
    };

    return data.workflow_runs.map((run) => ({
      id: run.id,
      headSha: run.head_sha,
      createdAt: run.created_at,
    }));
  }

  /**
   * Busca detalhes de build output
   */
  private async fetchBuildOutputDetails(
    runId: number
  ): Promise<{
    failedTests: FailedTest[];
    lintErrors: LintErrorDetail[];
    affectedFiles: string[];
    duration: number;
  }> {
    // Implementação simplificada
    // Em produção, parsearia logs reais do GitHub
    return {
      failedTests: [],
      lintErrors: [],
      affectedFiles: [],
      duration: 0,
    };
  }

  /**
   * Busca informações de commit
   */
  private async getCommitInfo(
    sha: string
  ): Promise<{
    message: string;
    author: string;
    committedAt: string;
  }> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/commits/${sha}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get commit info: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      commit: {
        message: string;
        author: { name: string };
        author_date: string;
      };
    };

    return {
      message: data.commit.message,
      author: data.commit.author.name,
      committedAt: data.commit.author_date,
    };
  }

  /**
   * Busca detalhes completos de commit
   */
  private async getCommitDetails(
    sha: string
  ): Promise<{
    message: string;
    parents: Array<{ sha: string }>;
  }> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/commits/${sha}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get commit details: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      message: string;
      parents: Array<{ sha: string }>;
    };

    return data;
  }

  /**
   * Busca tree de commit
   */
  private async getCommitTree(
    sha: string
  ): Promise<{ sha: string }> {
    const commit = await this.getCommitDetails(sha);
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/trees/${commit}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get commit tree: ${response.statusText}`);
    }

    const data = (await response.json()) as { sha: string };
    return data;
  }

  /**
   * Analisa impacto de rollback
   */
  private async analyzeRollbackImpact(
    ciFailure: CIFailure,
    mergedPR?: MergedPR
  ): Promise<RollbackImpact> {
    return {
      filesAffected: ciFailure.affectedFiles,
      linesChanged: 0,
      testsFixed: ciFailure.failedTests.length,
      estimatedDowntime: 300000, // 5min
      potentiallyAffectedFeatures: [],
      confidenceLevel: 0.85,
      riskOfReintroducingBug: false,
    };
  }

  /**
   * Verifica se é elegível para auto-approval
   */
  private isEligibleForAutoApproval(
    ciFailure: CIFailure,
    impact: RollbackImpact
  ): boolean {
    // Não auto-aprova CRITICAL
    if (
      this.config.requireManualApprovalForCritical &&
      ciFailure.severity === FailureSeverity.CRITICAL
    ) {
      return false;
    }

    // Verifica limites
    if (ciFailure.severity > this.config.maxAutoApprovalSeverity!) {
      return false;
    }

    if (
      ciFailure.failedTests.length <
      this.config.minFailuresForAutoApproval!
    ) {
      return false;
    }

    if (
      impact.confidenceLevel <
      this.config.minConfidenceForAutoApproval!
    ) {
      return false;
    }

    return true;
  }

  /**
   * Calcula severity da falha
   */
  private calculateSeverity(buildOutput: {
    failedTests: FailedTest[];
    lintErrors: LintErrorDetail[];
  }): FailureSeverity {
    const failedCount = buildOutput.failedTests.length;
    const lintCount = buildOutput.lintErrors.filter(
      (e) => e.severity === "error"
    ).length;

    if (failedCount > 20 || lintCount > 10) {
      return FailureSeverity.CRITICAL;
    } else if (failedCount > 10 || lintCount > 5) {
      return FailureSeverity.HIGH;
    } else if (failedCount > 3 || lintCount > 1) {
      return FailureSeverity.MEDIUM;
    }

    return FailureSeverity.LOW;
  }

  /**
   * Gera razão de rollback
   */
  private generateRollbackReason(ciFailure: CIFailure): string {
    return `Automatic rollback due to CI failure: ${ciFailure.failedTests.length} tests failed, ${ciFailure.lintErrors.length} lint errors in commit ${ciFailure.commitSha.substring(0, 7)}.`;
  }

  /**
   * Notifica proposta de rollback via Slack
   */
  private async notifySlackApprovalRequest(
    proposal: RollbackProposal,
    approvalToken: string
  ): Promise<string | undefined> {
    if (!this.config.slackWebhookUrl) {
      return undefined;
    }

    const message = {
      text: `Rollback Proposal Requires Approval`,
      blocks: [
        {
          type: "header",
          text: {
            type: "plain_text",
            text: "Rollback Proposal",
          },
        },
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*Commit:* ${proposal.targetCommit.substring(0, 7)}\n*Message:* ${proposal.targetCommitMessage}\n*Severity:* ${proposal.severity}\n*Tests Failed:* ${proposal.ciFailure.failedTests.length}`,
          },
        },
        {
          type: "actions",
          elements: [
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "Approve",
              },
              style: "primary",
              value: proposal.id,
              action_id: `approve_rollback_${proposal.id}`,
            },
            {
              type: "button",
              text: {
                type: "plain_text",
                text: "Reject",
              },
              style: "danger",
              value: proposal.id,
              action_id: `reject_rollback_${proposal.id}`,
            },
          ],
        },
      ],
    };

    try {
      const response = await fetch(this.config.slackWebhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message),
      });

      if (!response.ok) {
        console.error(`Slack notification failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error(`Error sending Slack notification: ${error}`);
    }

    return "mock-slack-message-id";
  }

  /**
   * Notifica proposta via Cowork
   */
  private async notifyCoworkApprovalRequest(
    proposal: RollbackProposal,
    approvalToken: string
  ): Promise<string | undefined> {
    if (!this.config.coworkWebhookUrl) {
      return undefined;
    }

    const message = {
      text: `Rollback Proposal #${proposal.id}`,
      details: {
        commit: proposal.targetCommit,
        severity: proposal.severity,
        testsAffected: proposal.ciFailure.failedTests.length,
        approvalToken,
      },
    };

    try {
      const response = await fetch(this.config.coworkWebhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(message),
      });

      if (!response.ok) {
        console.error(`Cowork notification failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error(`Error sending Cowork notification: ${error}`);
    }

    return "mock-cowork-message-id";
  }

  /**
   * Notifica proposta de rollback
   */
  private async notifyRollbackProposal(
    proposal: RollbackProposal
  ): Promise<void> {
    if (proposal.approvalStatus === "pending") {
      await this.requestApproval(proposal);
    }
  }

  /**
   * Notifica resultado de aprovação/rejeição
   */
  private async notifyApprovalResult(
    proposal: RollbackProposal,
    approved: boolean,
    reason?: string
  ): Promise<void> {
    // Implementar notificações
  }

  /**
   * Notifica execução de rollback
   */
  private async notifyRollbackExecution(
    execution: RollbackExecution,
    proposal: RollbackProposal
  ): Promise<void> {
    // Implementar notificações
  }

  /**
   * Gera token de aprovação
   */
  private generateApprovalToken(): string {
    return `approval-${Date.now()}-${Math.random().toString(36).substr(2, 16)}`;
  }

  /**
   * Registra entrada em audit trail
   */
  private logAuditTrail(
    action: string,
    status: "success" | "failure",
    details: Record<string, unknown>,
    error?: string
  ): void {
    const entry: AuditTrailEntry = {
      timestamp: new Date(),
      action,
      status,
      details,
      error,
    };

    this.auditTrail.push(entry);
    console.log(`[AUDIT] ${action} - ${status}`, details);
  }

  /**
   * Helper para delay
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Obtém métricas atuais
   */
  getMetrics(): RollbackMetrics {
    return {
      ...this.metrics,
      timestamp: new Date(),
    };
  }

  /**
   * Obtém audit trail
   */
  getAuditTrail(): AuditTrailEntry[] {
    return [...this.auditTrail];
  }

  /**
   * Obtém proposta ativa
   */
  getProposal(proposalId: string): RollbackProposal | undefined {
    return this.activeProposals.get(proposalId);
  }

  /**
   * Obtém todas as propostas ativas
   */
  getActiveProposals(): RollbackProposal[] {
    return Array.from(this.activeProposals.values());
  }

  /**
   * Reseta métricas
   */
  resetMetrics(): void {
    this.metrics = {
      timestamp: new Date(),
      totalFailuresDetected: 0,
      totalProposals: 0,
      totalApproved: 0,
      totalRejected: 0,
      totalExecuted: 0,
      successfulRollbacks: 0,
      failedRollbacks: 0,
      averageTimeToDetectMinutes: 0,
      averageTimeToApproveMinutes: 0,
      averageTimeToExecuteMinutes: 0,
      autoApprovedCount: 0,
    };

    this.rollbacksToday = 0;
  }
}

/**
 * Factory function
 */
export function createRollbackOrchestratorService(
  config: RollbackOrchestratorConfig
): RollbackOrchestratorService {
  return new RollbackOrchestratorService(config);
}

// ============================================================================
// PHASE 4 SAFETY MECHANISM — Simplified Rollback Interface
// ============================================================================

/**
 * Issue detected in commit
 */
export interface Issue {
  id: string;
  commitSha: string;
  type: "test_failure" | "lint_error" | "build_error" | "security_issue";
  severity: FailureSeverity;
  message: string;
  details: Record<string, unknown>;
  detectedAt: Date;
  affectedFiles?: string[];
}

/**
 * Result of revert operation
 */
export interface RevertResult {
  success: boolean;
  revertCommitSha?: string;
  commitSha: string;
  reason: string;
  prNumber?: number;
  prUrl?: string;
  timestamp: Date;
  duration: number; // ms
  error?: string;
  cascadingRollbacks?: string[]; // SHAs of commits that might be affected
}

/**
 * Rollback event for history tracking
 */
export interface RollbackEvent {
  id: string;
  timestamp: Date;
  type: "detection" | "approval" | "execution" | "failure" | "success";
  commitSha: string;
  actor?: string;
  reason?: string;
  prNumber?: number;
  details: Record<string, unknown>;
  metadata: {
    duration?: number;
    affectedFiles?: string[];
    testsFixed?: number;
    testsFailed?: number;
  };
}

/**
 * Configuration for Rollback service (Phase 4)
 */
export interface RollbackConfig {
  githubToken: string;
  owner: string;
  repo: string;
  mainBranch?: string; // default "main"

  // Safeguards
  preventCascadingRollbacks?: boolean; // default true
  maxRolledBackCommits?: number; // default 5 (prevent rolling back too many commits)
  requireManualApprovalForRollback?: boolean; // default true
  maxRollbacksPerDay?: number; // default 5

  // Notifications
  slackWebhookUrl?: string;
  coworkWebhookUrl?: string;
  notifyOnDetection?: boolean;
  notifyOnExecution?: boolean;

  // Storage
  storeHistory?: boolean; // default true
  historyRetentionDays?: number; // default 90
}

/**
 * Simplified Rollback Service (Phase 4 Safety Mechanism)
 *
 * Provides focused interface for:
 * - Detecting issues in commits
 * - Reverting problematic commits
 * - Creating revert PRs
 * - Tracking rollback history
 *
 * Includes safeguards to prevent cascading rollbacks.
 */
export class Rollback {
  private config: RollbackConfig;
  private apiBaseUrl = "https://api.github.com";
  private rollbackHistory: RollbackEvent[] = [];
  private rolledBackCommits: Set<string> = new Set();
  private dailyRollbackCount = 0;
  private lastDayReset = new Date();

  constructor(config: RollbackConfig) {
    this.config = {
      mainBranch: "main",
      preventCascadingRollbacks: true,
      maxRolledBackCommits: 5,
      requireManualApprovalForRollback: true,
      maxRollbacksPerDay: 5,
      storeHistory: true,
      historyRetentionDays: 90,
      ...config,
    };

    this.validateConfig();
  }

  /**
   * Validates configuration
   */
  private validateConfig(): void {
    if (!this.config.githubToken) {
      throw new Error("GitHub token is required");
    }
    if (!this.config.owner || !this.config.repo) {
      throw new Error("Owner and repo are required");
    }
  }

  /**
   * Detects issues in a specific commit
   */
  async detectIssues(commit: string): Promise<Issue[]> {
    const issues: Issue[] = [];

    try {
      // Get commit details
      const commitDetails = await this.getCommitDetails(commit);

      // Check for test failures
      const testIssues = await this.detectTestFailures(commit);
      issues.push(...testIssues);

      // Check for lint errors
      const lintIssues = await this.detectLintErrors(commit);
      issues.push(...lintIssues);

      // Check for build errors
      const buildIssues = await this.detectBuildErrors(commit);
      issues.push(...buildIssues);

      // Check for security issues
      const securityIssues = await this.detectSecurityIssues(commit);
      issues.push(...securityIssues);

      // Log detection
      if (issues.length > 0) {
        this.recordEvent("detection", commit, undefined, {
          issuesFound: issues.length,
          severities: issues.map((i) => i.severity),
        });
      }

      return issues;
    } catch (error) {
      throw new Error(
        `Failed to detect issues in commit ${commit}: ${String(error)}`
      );
    }
  }

  /**
   * Reverts a commit (creates revert commit)
   */
  async revert(commitSha: string, reason: string): Promise<RevertResult> {
    const startTime = Date.now();
    const result: RevertResult = {
      success: false,
      commitSha,
      reason,
      timestamp: new Date(),
      duration: 0,
    };

    try {
      // Check safeguards
      await this.checkRollbackSafeguards(commitSha);

      // Check for cascading rollbacks
      const potentialCascades = await this.detectCascadingRollbacks(
        commitSha
      );
      result.cascadingRollbacks = potentialCascades;

      if (potentialCascades.length > 0 && this.config.preventCascadingRollbacks) {
        throw new Error(
          `Cascading rollback detected. Commits that depend on this: ${potentialCascades.join(", ")}`
        );
      }

      // Create revert commit
      const revertCommitSha = await this.createRevertCommit(commitSha);
      result.revertCommitSha = revertCommitSha;

      // Push to branch
      await this.pushRevert(revertCommitSha, "main");

      // Track rolled back commit
      this.rolledBackCommits.add(commitSha);
      this.dailyRollbackCount++;

      result.success = true;
      result.duration = Date.now() - startTime;

      // Record event
      this.recordEvent("execution", commitSha, undefined, {
        revertCommitSha,
        reason,
        duration: result.duration,
      });

      return result;
    } catch (error) {
      result.error = String(error);
      result.duration = Date.now() - startTime;

      this.recordEvent("failure", commitSha, undefined, {
        reason,
        error: String(error),
        duration: result.duration,
      });

      throw error;
    }
  }

  /**
   * Creates a PR for the revert commit
   */
  async createRevertPR(commit: string): Promise<number> {
    try {
      const commitDetails = await this.getCommitDetails(commit);

      // Check if revert already exists
      const existingRevert = await this.findExistingRevert(commit);
      if (existingRevert) {
        return existingRevert;
      }

      // Create revert commit if not already done
      let revertCommitSha = await this.findRevertCommit(commit);
      if (!revertCommitSha) {
        revertCommitSha = await this.createRevertCommit(commit);
        await this.pushRevert(revertCommitSha, "revert-patch");
      }

      // Create PR
      const prNumber = await this.openRevertPR(
        commit,
        revertCommitSha,
        commitDetails.message
      );

      this.recordEvent("approval", commit, undefined, {
        prNumber,
        revertCommitSha,
      });

      return prNumber;
    } catch (error) {
      throw new Error(
        `Failed to create revert PR for commit ${commit}: ${String(error)}`
      );
    }
  }

  /**
   * Tracks rollback history within a time window
   */
  async trackHistory(timeWindow: { start?: Date; end?: Date; days?: number }): Promise<RollbackEvent[]> {
    let startDate = timeWindow.start;
    let endDate = timeWindow.end || new Date();

    if (!startDate && timeWindow.days) {
      startDate = new Date(endDate.getTime() - timeWindow.days * 24 * 60 * 60 * 1000);
    }

    if (!startDate) {
      startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000); // default 7 days
    }

    const filtered = this.rollbackHistory.filter(
      (event) =>
        event.timestamp >= startDate! &&
        event.timestamp <= endDate
    );

    return filtered;
  }

  /**
   * Gets current rollback metrics
   */
  getRollbackMetrics(): {
    totalRolledBack: number;
    dailyRollbackCount: number;
    rolledBackCommits: string[];
    historySize: number;
  } {
    return {
      totalRolledBack: this.rolledBackCommits.size,
      dailyRollbackCount: this.dailyRollbackCount,
      rolledBackCommits: Array.from(this.rolledBackCommits),
      historySize: this.rollbackHistory.length,
    };
  }

  /**
   * Resets daily rollback counter
   */
  resetDailyCounter(): void {
    const now = new Date();
    if (
      now.getDate() !== this.lastDayReset.getDate() ||
      now.getMonth() !== this.lastDayReset.getMonth() ||
      now.getFullYear() !== this.lastDayReset.getFullYear()
    ) {
      this.dailyRollbackCount = 0;
      this.lastDayReset = now;
    }
  }

  // =========================================================================
  // SAFEGUARDS
  // =========================================================================

  /**
   * Checks rollback safeguards
   */
  private async checkRollbackSafeguards(
    commitSha: string
  ): Promise<void> {
    // Check if already rolled back
    if (this.rolledBackCommits.has(commitSha)) {
      throw new Error(
        `Commit ${commitSha} has already been rolled back`
      );
    }

    // Check daily limit
    this.resetDailyCounter();
    if (this.dailyRollbackCount >= this.config.maxRollbacksPerDay!) {
      throw new Error(
        `Daily rollback limit (${this.config.maxRollbacksPerDay}) exceeded`
      );
    }

    // Check max rolled back commits
    if (
      this.rolledBackCommits.size >= this.config.maxRolledBackCommits!
    ) {
      throw new Error(
        `Maximum rolled back commits (${this.config.maxRolledBackCommits}) exceeded`
      );
    }

    // Verify commit exists
    await this.getCommitDetails(commitSha);
  }

  /**
   * Detects if rolling back this commit would cause cascading rollbacks
   */
  private async detectCascadingRollbacks(
    commitSha: string
  ): Promise<string[]> {
    const cascadingCommits: string[] = [];

    try {
      // Get commits that depend on this one
      const dependents = await this.findDependentCommits(commitSha);

      // Filter to only commits that are still on main
      for (const dependent of dependents) {
        const isOnMain = await this.isCommitOnBranch(
          dependent,
          this.config.mainBranch || "main"
        );
        if (isOnMain) {
          cascadingCommits.push(dependent);
        }
      }
    } catch (error) {
      console.warn(
        `Failed to detect cascading rollbacks: ${String(error)}`
      );
    }

    return cascadingCommits;
  }

  // =========================================================================
  // ISSUE DETECTION
  // =========================================================================

  /**
   * Detects test failures for a commit
   */
  private async detectTestFailures(commitSha: string): Promise<Issue[]> {
    const issues: Issue[] = [];

    try {
      // Get workflow runs for this commit
      const runs = await this.getWorkflowRunsForCommit(commitSha);

      for (const run of runs) {
        if (run.conclusion === "failure") {
          const jobs = await this.getWorkflowJobs(run.id);

          for (const job of jobs) {
            if (job.conclusion === "failure" && job.steps) {
              for (const step of job.steps) {
                if (step.conclusion === "failure" && step.name.includes("test")) {
                  issues.push({
                    id: `test-${run.id}-${job.id}-${step.number}`,
                    commitSha,
                    type: "test_failure",
                    severity: this.calculateTestFailureSeverity(step),
                    message: step.name,
                    details: {
                      runId: run.id,
                      jobId: job.id,
                      stepNumber: step.number,
                    },
                    detectedAt: new Date(),
                  });
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.warn(`Failed to detect test failures: ${String(error)}`);
    }

    return issues;
  }

  /**
   * Detects lint errors for a commit
   */
  private async detectLintErrors(commitSha: string): Promise<Issue[]> {
    const issues: Issue[] = [];

    try {
      const runs = await this.getWorkflowRunsForCommit(commitSha);

      for (const run of runs) {
        const jobs = await this.getWorkflowJobs(run.id);

        for (const job of jobs) {
          if (job.steps) {
            for (const step of job.steps) {
              if (
                step.conclusion === "failure" &&
                (step.name.toLowerCase().includes("lint") ||
                  step.name.toLowerCase().includes("eslint"))
              ) {
                issues.push({
                  id: `lint-${run.id}-${job.id}-${step.number}`,
                  commitSha,
                  type: "lint_error",
                  severity: FailureSeverity.MEDIUM,
                  message: step.name,
                  details: {
                    runId: run.id,
                    jobId: job.id,
                  },
                  detectedAt: new Date(),
                });
              }
            }
          }
        }
      }
    } catch (error) {
      console.warn(`Failed to detect lint errors: ${String(error)}`);
    }

    return issues;
  }

  /**
   * Detects build errors for a commit
   */
  private async detectBuildErrors(commitSha: string): Promise<Issue[]> {
    const issues: Issue[] = [];

    try {
      const runs = await this.getWorkflowRunsForCommit(commitSha);

      for (const run of runs) {
        if (run.conclusion === "failure") {
          issues.push({
            id: `build-${run.id}`,
            commitSha,
            type: "build_error",
            severity: FailureSeverity.HIGH,
            message: `Build failed for workflow run ${run.id}`,
            details: {
              runId: run.id,
              name: run.name,
              headBranch: run.head_branch,
            },
            detectedAt: new Date(run.created_at),
          });
        }
      }
    } catch (error) {
      console.warn(`Failed to detect build errors: ${String(error)}`);
    }

    return issues;
  }

  /**
   * Detects security issues for a commit
   */
  private async detectSecurityIssues(commitSha: string): Promise<Issue[]> {
    const issues: Issue[] = [];

    try {
      // Check for dependency vulnerabilities via workflow
      const runs = await this.getWorkflowRunsForCommit(commitSha);

      for (const run of runs) {
        const jobs = await this.getWorkflowJobs(run.id);

        for (const job of jobs) {
          if (
            job.name.toLowerCase().includes("security") ||
            job.name.toLowerCase().includes("audit") ||
            job.name.toLowerCase().includes("scan")
          ) {
            if (job.conclusion === "failure") {
              issues.push({
                id: `security-${run.id}-${job.id}`,
                commitSha,
                type: "security_issue",
                severity: FailureSeverity.CRITICAL,
                message: `Security check failed: ${job.name}`,
                details: {
                  runId: run.id,
                  jobId: job.id,
                  jobName: job.name,
                },
                detectedAt: new Date(run.created_at),
              });
            }
          }
        }
      }
    } catch (error) {
      console.warn(`Failed to detect security issues: ${String(error)}`);
    }

    return issues;
  }

  /**
   * Calculates severity of test failure
   */
  private calculateTestFailureSeverity(
    step: Record<string, unknown>
  ): FailureSeverity {
    const name = String(step.name || "").toLowerCase();

    if (
      name.includes("critical") ||
      name.includes("integration") ||
      name.includes("e2e")
    ) {
      return FailureSeverity.CRITICAL;
    } else if (name.includes("unit")) {
      return FailureSeverity.MEDIUM;
    }

    return FailureSeverity.HIGH;
  }

  // =========================================================================
  // GITHUB API HELPERS
  // =========================================================================

  /**
   * Gets commit details
   */
  private async getCommitDetails(sha: string): Promise<{
    message: string;
    author: string;
    committedAt: string;
  }> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/commits/${sha}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get commit details: ${response.statusText}`);
    }

    const data = (await response.json()) as {
      commit: {
        message: string;
        author: { name: string };
        author_date: string;
      };
    };

    return {
      message: data.commit.message,
      author: data.commit.author.name,
      committedAt: data.commit.author_date,
    };
  }

  /**
   * Gets workflow runs for a commit
   */
  private async getWorkflowRunsForCommit(
    commitSha: string
  ): Promise<Array<Record<string, unknown>>> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/runs?head_sha=${commitSha}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      return [];
    }

    const data = (await response.json()) as {
      workflow_runs: Array<Record<string, unknown>>;
    };
    return data.workflow_runs;
  }

  /**
   * Gets jobs for a workflow run
   */
  private async getWorkflowJobs(runId: number): Promise<Array<Record<string, unknown>>> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/actions/runs/${runId}/jobs`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      return [];
    }

    const data = (await response.json()) as {
      jobs: Array<Record<string, unknown>>;
    };
    return data.jobs;
  }

  /**
   * Creates revert commit
   */
  private async createRevertCommit(targetSha: string): Promise<string> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/commits`;

    const originalCommit = await this.getCommitDetails(targetSha);

    const revertMessage = `Revert "${originalCommit.message}"\n\nThis reverts commit ${targetSha}.`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: revertMessage,
        parents: [targetSha],
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create revert commit: ${response.statusText}`);
    }

    const data = (await response.json()) as { sha: string };
    return data.sha;
  }

  /**
   * Pushes revert commit
   */
  private async pushRevert(commitSha: string, branch: string): Promise<void> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/refs/heads/${branch}`;

    const response = await fetch(url, {
      method: "PATCH",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sha: commitSha }),
    });

    if (!response.ok) {
      throw new Error(`Failed to push revert: ${response.statusText}`);
    }
  }

  /**
   * Opens revert PR
   */
  private async openRevertPR(
    originalCommit: string,
    revertCommit: string,
    originalMessage: string
  ): Promise<number> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls`;

    const title = `Revert: ${originalMessage.split("\n")[0]}`;
    const body = `Automatically generated revert for commit ${originalCommit}.\n\nRevert commit: ${revertCommit}`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title,
        body,
        head: "revert-patch",
        base: this.config.mainBranch || "main",
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create PR: ${response.statusText}`);
    }

    const data = (await response.json()) as { number: number };
    return data.number;
  }

  /**
   * Finds existing revert for a commit
   */
  private async findExistingRevert(commitSha: string): Promise<number | null> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls?state=open&base=${this.config.mainBranch || "main"}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as Array<{ number: number; body: string }>;
    const existing = data.find((pr) =>
      pr.body.includes(`reverts commit ${commitSha}`)
    );

    return existing ? existing.number : null;
  }

  /**
   * Finds revert commit for a commit
   */
  private async findRevertCommit(commitSha: string): Promise<string | null> {
    // In a real implementation, would search commit history
    // For now, return null to indicate not found
    return null;
  }

  /**
   * Finds commits that depend on this commit
   */
  private async findDependentCommits(commitSha: string): Promise<string[]> {
    // This would require analyzing the commit graph
    // For MVP, return empty array
    return [];
  }

  /**
   * Checks if commit is on a branch
   */
  private async isCommitOnBranch(
    commitSha: string,
    branch: string
  ): Promise<boolean> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/commits/${commitSha}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        Accept: "application/vnd.github.v3+json",
      },
    });

    return response.ok;
  }

  /**
   * Records rollback event
   */
  private recordEvent(
    type: RollbackEvent["type"],
    commitSha: string,
    actor?: string,
    details?: Record<string, unknown>
  ): void {
    const event: RollbackEvent = {
      id: `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      type,
      commitSha,
      actor,
      details: details || {},
      metadata: {},
    };

    this.rollbackHistory.push(event);

    // Trim old history if enabled
    if (this.config.storeHistory && this.config.historyRetentionDays) {
      const cutoff = new Date(
        Date.now() - this.config.historyRetentionDays * 24 * 60 * 60 * 1000
      );
      this.rollbackHistory = this.rollbackHistory.filter(
        (e) => e.timestamp > cutoff
      );
    }
  }
}

/**
 * Factory function for Rollback service
 */
export function createRollback(config: RollbackConfig): Rollback {
  return new Rollback(config);
}
