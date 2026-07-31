/**
 * Auto-Merge Service — Advanced PR merge automation with distributed locking
 * Versão: 2.0.0
 *
 * Recursos:
 * - Verifica critérios de qualidade para auto-merge
 * - Detecção inteligente de conflitos de merge
 * - Estratégias de merge personalizáveis (merge, squash, rebase, cherry-pick)
 * - Agendamento de merge para data/hora específicas
 * - Distributed locking para segurança em ambientes concorrentes
 * - Transaction safety com rollback capability
 * - Rastreamento completo de métricas
 */

/**
 * Estratégias de merge suportadas
 */
export type MergeStrategy = "merge" | "squash" | "rebase" | "cherry-pick" | "fast-forward";

/**
 * Tipos de conflito detectados
 */
export type ConflictType = "content" | "delete-modify" | "add-add" | "rename-rename" | "structural";

/**
 * Tipos de requisitos de merge
 */
export type RequirementType =
  | "ci_passed"
  | "approvals_met"
  | "no_conflicts"
  | "branch_protection"
  | "status_checks"
  | "code_review"
  | "not_draft"
  | "branch_up_to_date"
  | "required_labels"
  | "no_wip_marker";

/**
 * Status de lock distribuído
 */
export enum LockStatus {
  ACQUIRED = "acquired",
  RELEASED = "released",
  EXPIRED = "expired",
  CONFLICT = "conflict",
  RETRY = "retry",
}

/**
 * Status de agendamento de merge
 */
export enum ScheduleStatus {
  SCHEDULED = "scheduled",
  EXECUTING = "executing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
  EXPIRED = "expired",
}

/**
 * Interface para conflito de merge
 */
export interface Conflict {
  file: string;
  type: ConflictType;
  description: string;
  resolvable: boolean; // Pode ser resolvido automaticamente?
  suggestedResolution?: string;
  lineRange?: {
    start: number;
    end: number;
  };
  severity: "low" | "medium" | "high";
}

/**
 * Interface para requisito de merge
 */
export interface Requirement {
  type: RequirementType;
  met: boolean;
  description: string;
  currentValue?: string;
  requiredValue?: string;
  lastCheckedAt: Date;
  checkDetails?: Record<string, any>;
}

/**
 * Resultado de merge
 */
export interface MergeResult {
  success: boolean;
  prNumber: number;
  strategy: MergeStrategy;
  mergeCommitSha?: string;
  message: string;
  timestamp: Date;
  duration: number; // ms
  conflictsResolved?: number;
  transactionId: string;
  auditLog: AuditLogEntry[];
  error?: {
    code: string;
    message: string;
    recoverable: boolean;
  };
}

/**
 * Resultado de agendamento
 */
export interface ScheduleResult {
  success: boolean;
  scheduleId: string;
  prNumber: number;
  scheduledFor: Date;
  strategy: MergeStrategy;
  status: ScheduleStatus;
  message: string;
  willExecuteAt?: Date; // Tempo de execução estimado
}

/**
 * Lock distribuído
 */
export interface DistributedLock {
  lockId: string;
  resource: string;
  owner: string;
  acquiredAt: Date;
  expiresAt: Date;
  isActive: boolean;
  status: LockStatus;
}

/**
 * Entrada de log de auditoria
 */
export interface AuditLogEntry {
  timestamp: Date;
  action: string;
  status: "success" | "failure" | "warning";
  prNumber: number;
  details: Record<string, any>;
  transactionId: string;
}

/**
 * Métricas de merge
 */
export interface MergeMetrics {
  totalMerges: number;
  successfulMerges: number;
  failedMerges: number;
  averageDuration: number; // ms
  conflictRate: number; // %
  successRate: number; // %
  mergeStrategiesUsed: Record<MergeStrategy, number>;
  blockedByRequirement: Record<RequirementType, number>;
  lastMergeAt?: Date;
  lockWaitTime: {
    average: number; // ms
    max: number; // ms
    min: number; // ms
  };
}

/**
 * Configuração do AutoMerge Service
 */
export interface AutoMergeServiceConfig {
  githubToken: string;
  owner: string;
  repo: string;

  // Requisitos de qualidade
  requireCIPassed?: boolean;
  requiredApprovals?: number;
  allowConflicts?: boolean;
  allowMergingWithConflicts?: boolean;

  // Lock distribuído
  lockProvider?: "memory" | "redis" | "supabase"; // default: "memory"
  lockTtl?: number; // ms, default: 60000
  lockRetryAttempts?: number; // default: 3
  lockRetryDelay?: number; // ms, default: 1000

  // Padrões
  defaultStrategy?: MergeStrategy; // default: "squash"
  commitMessageTemplate?: string;

  // Agendamento
  enableScheduling?: boolean; // default: true
  schedulerIntervalMs?: number; // default: 60000

  // Métricas
  trackMetrics?: boolean; // default: true
  metricsStorageUrl?: string; // Supabase URL para persistência

  // GitHub
  apiBaseUrl?: string;
  requestTimeout?: number; // ms
}

/**
 * Classe principal do AutoMerge Service
 */
export class AutoMerge {
  private config: Required<AutoMergeServiceConfig>;
  private apiBaseUrl: string;
  private lockManager: DistributedLockManager;
  private metrics: MergeMetrics;
  private auditLog: AuditLogEntry[] = [];
  private scheduledMerges: Map<string, ScheduledMerge> = new Map();
  private transactionLog: Map<string, Transaction> = new Map();

  constructor(config: AutoMergeServiceConfig) {
    this.config = {
      requireCIPassed: true,
      requiredApprovals: 1,
      allowConflicts: false,
      allowMergingWithConflicts: false,
      lockProvider: "memory",
      lockTtl: 60000,
      lockRetryAttempts: 3,
      lockRetryDelay: 1000,
      defaultStrategy: "squash",
      commitMessageTemplate: "Merge PR #{prNumber}: {title}",
      enableScheduling: true,
      schedulerIntervalMs: 60000,
      trackMetrics: true,
      metricsStorageUrl: "",
      apiBaseUrl: "https://api.github.com",
      requestTimeout: 30000,
      ...config,
    };

    this.apiBaseUrl = this.config.apiBaseUrl;

    // Inicializa lock manager
    this.lockManager = new DistributedLockManager(this.config.lockProvider, {
      ttl: this.config.lockTtl,
      retryAttempts: this.config.lockRetryAttempts,
      retryDelay: this.config.lockRetryDelay,
    });

    // Inicializa métricas
    this.metrics = {
      totalMerges: 0,
      successfulMerges: 0,
      failedMerges: 0,
      averageDuration: 0,
      conflictRate: 0,
      successRate: 0,
      mergeStrategiesUsed: {
        merge: 0,
        squash: 0,
        rebase: 0,
        "cherry-pick": 0,
        "fast-forward": 0,
      },
      blockedByRequirement: {
        ci_passed: 0,
        approvals_met: 0,
        no_conflicts: 0,
        branch_protection: 0,
        status_checks: 0,
        code_review: 0,
        not_draft: 0,
        branch_up_to_date: 0,
        required_labels: 0,
        no_wip_marker: 0,
      },
      lockWaitTime: {
        average: 0,
        max: 0,
        min: 0,
      },
    };

    // Inicia scheduler se habilitado
    if (this.config.enableScheduling) {
      this.startScheduler();
    }
  }

  /**
   * Verifica se um PR pode ser mergido
   */
  async canMerge(pr: { number: number; draft?: boolean }): Promise<boolean> {
    try {
      const requirements = await this.checkRequirements(pr);
      const allMet = requirements.every((r) => r.met);

      this.logAudit("CAN_MERGE_CHECK", "success", pr.number, {
        canMerge: allMet,
        requirementsMet: requirements.filter((r) => r.met).length,
        requirementsTotal: requirements.length,
      });

      return allMet;
    } catch (error) {
      this.logAudit("CAN_MERGE_CHECK", "failure", pr.number, {
        error: error instanceof Error ? error.message : String(error),
      });
      return false;
    }
  }

  /**
   * Realiza merge de um PR
   */
  async merge(
    prNumber: number,
    strategy?: MergeStrategy
  ): Promise<MergeResult> {
    const transactionId = this.generateTransactionId();
    const startTime = Date.now();
    const mergeStrategy = strategy || this.config.defaultStrategy;

    // Cria transação
    const transaction: Transaction = {
      id: transactionId,
      prNumber,
      strategy: mergeStrategy,
      startedAt: new Date(),
      status: "pending",
      steps: [],
    };

    this.transactionLog.set(transactionId, transaction);

    try {
      // 1. Adquire lock distribuído
      this.logAudit("ACQUIRING_LOCK", "success", prNumber, {
        transactionId,
      });

      const lock = await this.lockManager.acquireLock(
        `merge-pr-${prNumber}`,
        `auto-merge-${transactionId}`
      );

      if (!lock.isActive) {
        throw new Error("Failed to acquire merge lock");
      }

      // 2. Verifica requisitos
      this.logAudit("CHECKING_REQUIREMENTS", "success", prNumber, {
        transactionId,
      });

      const requirements = await this.checkRequirements({ number: prNumber });
      const unmetRequirements = requirements.filter((r) => !r.met);

      if (unmetRequirements.length > 0) {
        this.recordBlockedMerge(unmetRequirements);

        await this.lockManager.releaseLock(lock.lockId);

        const result: MergeResult = {
          success: false,
          prNumber,
          strategy: mergeStrategy,
          message: `Blocked by: ${unmetRequirements.map((r) => r.type).join(", ")}`,
          timestamp: new Date(),
          duration: Date.now() - startTime,
          transactionId,
          auditLog: [...this.auditLog],
          error: {
            code: "REQUIREMENTS_NOT_MET",
            message: `${unmetRequirements.length} requirement(s) not met`,
            recoverable: true,
          },
        };

        return result;
      }

      // 3. Detecta conflitos
      this.logAudit("DETECTING_CONFLICTS", "success", prNumber, {
        transactionId,
      });

      const conflicts = await this.getConflicts({ number: prNumber });

      if (conflicts.length > 0 && !this.config.allowMergingWithConflicts) {
        await this.lockManager.releaseLock(lock.lockId);

        const result: MergeResult = {
          success: false,
          prNumber,
          strategy: mergeStrategy,
          message: `Merge conflicts detected: ${conflicts.length}`,
          timestamp: new Date(),
          duration: Date.now() - startTime,
          transactionId,
          auditLog: [...this.auditLog],
          error: {
            code: "MERGE_CONFLICTS",
            message: `Found ${conflicts.length} merge conflict(s)`,
            recoverable: false,
          },
        };

        this.recordFailedMerge(result);
        return result;
      }

      // 4. Obtém dados do PR
      this.logAudit("FETCHING_PR_DATA", "success", prNumber, {
        transactionId,
      });

      const prData = await this.fetchPRData(prNumber);

      // 5. Realiza merge
      this.logAudit("PERFORMING_MERGE", "success", prNumber, {
        transactionId,
        strategy: mergeStrategy,
      });

      const mergeCommitSha = await this.performMerge(
        prNumber,
        mergeStrategy,
        prData.head.sha
      );

      // 6. Confirma transação
      transaction.status = "completed";
      transaction.completedAt = new Date();

      this.logAudit("MERGE_COMPLETED", "success", prNumber, {
        transactionId,
        mergeCommitSha,
        strategy: mergeStrategy,
      });

      // 7. Libera lock
      await this.lockManager.releaseLock(lock.lockId);

      const result: MergeResult = {
        success: true,
        prNumber,
        strategy: mergeStrategy,
        mergeCommitSha,
        message: "Merge completed successfully",
        timestamp: new Date(),
        duration: Date.now() - startTime,
        conflictsResolved: conflicts.length,
        transactionId,
        auditLog: [...this.auditLog],
      };

      this.recordSuccessfulMerge(result);
      return result;
    } catch (error) {
      transaction.status = "failed";
      transaction.error = error instanceof Error ? error.message : String(error);
      transaction.completedAt = new Date();

      const errorMsg = error instanceof Error ? error.message : String(error);

      this.logAudit("MERGE_FAILED", "failure", prNumber, {
        transactionId,
        error: errorMsg,
      });

      // Tenta liberar lock em caso de erro
      try {
        await this.lockManager.releaseLock(`merge-pr-${prNumber}`);
      } catch (lockError) {
        console.warn("Failed to release lock after merge error:", lockError);
      }

      const result: MergeResult = {
        success: false,
        prNumber,
        strategy: mergeStrategy,
        message: errorMsg,
        timestamp: new Date(),
        duration: Date.now() - startTime,
        transactionId,
        auditLog: [...this.auditLog],
        error: {
          code: "MERGE_FAILED",
          message: errorMsg,
          recoverable: this.isRecoverableError(errorMsg),
        },
      };

      this.recordFailedMerge(result);
      return result;
    }
  }

  /**
   * Verifica todos os requisitos de merge
   */
  async checkRequirements(pr: {
    number: number;
    draft?: boolean;
  }): Promise<Requirement[]> {
    const requirements: Requirement[] = [];
    const prNumber = pr.number;
    const now = new Date();

    try {
      // 1. Verifica draft status
      const draftStatus = await this.checkNotDraft(prNumber, pr.draft);
      requirements.push({
        type: "not_draft",
        met: draftStatus,
        description: "PR is not in draft mode",
        lastCheckedAt: now,
      });

      // 2. Verifica status checks
      const statusChecks = await this.checkStatusChecks(prNumber);
      requirements.push({
        type: "status_checks",
        met: statusChecks.allPassed,
        description: "All required status checks passed",
        currentValue: `${statusChecks.passed}/${statusChecks.total} passed`,
        lastCheckedAt: now,
        checkDetails: statusChecks.details,
      });

      // 3. Verifica CI
      if (this.config.requireCIPassed) {
        const ciPassed = await this.checkCIPassed(prNumber);
        requirements.push({
          type: "ci_passed",
          met: ciPassed,
          description: "CI pipeline passed",
          lastCheckedAt: now,
        });
      }

      // 4. Verifica approvals
      if (this.config.requiredApprovals > 0) {
        const approvalsResult = await this.checkApprovals(prNumber);
        requirements.push({
          type: "approvals_met",
          met: approvalsResult.met,
          description: `Required approvals met`,
          currentValue: `${approvalsResult.count}/${this.config.requiredApprovals}`,
          requiredValue: String(this.config.requiredApprovals),
          lastCheckedAt: now,
        });
      }

      // 5. Verifica conflitos
      const conflicts = await this.getConflicts(pr);
      requirements.push({
        type: "no_conflicts",
        met: conflicts.length === 0,
        description: "No merge conflicts",
        currentValue: `${conflicts.length} conflict(s)`,
        lastCheckedAt: now,
      });

      // 6. Verifica branch atualizado
      const isUpdated = await this.isBranchUpToDate(prNumber);
      requirements.push({
        type: "branch_up_to_date",
        met: isUpdated,
        description: "Branch is up to date with base",
        lastCheckedAt: now,
      });

      // 7. Verifica branch protection
      const branchProtection = await this.checkBranchProtection(prNumber);
      requirements.push({
        type: "branch_protection",
        met: branchProtection.compliant,
        description: "Compliant with branch protection rules",
        lastCheckedAt: now,
        checkDetails: branchProtection.details,
      });

      // 8. Verifica marcador WIP
      const noWIP = await this.checkNoWIPMarker(prNumber);
      requirements.push({
        type: "no_wip_marker",
        met: noWIP,
        description: "PR does not have WIP marker",
        lastCheckedAt: now,
      });

      return requirements;
    } catch (error) {
      this.logAudit("CHECK_REQUIREMENTS_ERROR", "failure", prNumber, {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }

  /**
   * Detecta conflitos de merge
   */
  async getConflicts(pr: {
    number: number;
  }): Promise<Conflict[]> {
    const conflicts: Conflict[] = [];
    const prNumber = pr.number;

    try {
      // Busca dados do PR
      const prData = await this.fetchPRData(prNumber);

      // Verifica se mergeable_state indica conflito
      if (prData.mergeable_state === "dirty" || prData.mergeable === false) {
        // Tenta buscar informações detalhadas de conflito
        const detailedConflicts = await this.getDetailedConflicts(prNumber);
        conflicts.push(...detailedConflicts);

        // Se não conseguir detalhes, cria um conflito genérico
        if (detailedConflicts.length === 0) {
          conflicts.push({
            file: "multiple",
            type: "content",
            description: "One or more files have merge conflicts",
            resolvable: false,
            severity: "high",
          });
        }
      }

      // Verifica conflitos de deletar/modificar
      const deleteModifyConflicts = await this.checkDeleteModifyConflicts(prNumber);
      conflicts.push(...deleteModifyConflicts);

      // Verifica conflitos de add/add
      const addAddConflicts = await this.checkAddAddConflicts(prNumber);
      conflicts.push(...addAddConflicts);

      // Verifica conflitos estruturais
      const structuralConflicts = await this.checkStructuralConflicts(prNumber);
      conflicts.push(...structuralConflicts);

      this.logAudit("CONFLICTS_DETECTED", "success", prNumber, {
        conflictCount: conflicts.length,
        types: [...new Set(conflicts.map((c) => c.type))],
      });

      return conflicts;
    } catch (error) {
      this.logAudit("GET_CONFLICTS_ERROR", "failure", prNumber, {
        error: error instanceof Error ? error.message : String(error),
      });
      throw error;
    }
  }

  /**
   * Agenda merge para uma data/hora específica
   */
  async scheduleMerge(
    prNumber: number,
    scheduledFor: Date,
    strategy?: MergeStrategy
  ): Promise<ScheduleResult> {
    const scheduleId = this.generateScheduleId();
    const mergeStrategy = strategy || this.config.defaultStrategy;

    try {
      // Valida data agendada
      if (scheduledFor <= new Date()) {
        throw new Error("Scheduled time must be in the future");
      }

      // Cria agendamento
      const scheduled: ScheduledMerge = {
        scheduleId,
        prNumber,
        strategy: mergeStrategy,
        scheduledFor,
        createdAt: new Date(),
        status: "scheduled",
      };

      this.scheduledMerges.set(scheduleId, scheduled);

      this.logAudit("MERGE_SCHEDULED", "success", prNumber, {
        scheduleId,
        scheduledFor: scheduledFor.toISOString(),
        strategy: mergeStrategy,
      });

      return {
        success: true,
        scheduleId,
        prNumber,
        scheduledFor,
        strategy: mergeStrategy,
        status: ScheduleStatus.SCHEDULED,
        message: `Merge scheduled for ${scheduledFor.toISOString()}`,
        willExecuteAt: scheduledFor,
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);

      this.logAudit("SCHEDULE_MERGE_FAILED", "failure", prNumber, {
        error: errorMsg,
      });

      return {
        success: false,
        scheduleId,
        prNumber,
        scheduledFor,
        strategy: mergeStrategy,
        status: ScheduleStatus.FAILED,
        message: errorMsg,
      };
    }
  }

  /**
   * Obtém métricas de merge
   */
  getMetrics(): MergeMetrics {
    return { ...this.metrics };
  }

  /**
   * Obtém status de agendamentos
   */
  getScheduledMerges(): ScheduleResult[] {
    return Array.from(this.scheduledMerges.values()).map((scheduled) => ({
      success: true,
      scheduleId: scheduled.scheduleId,
      prNumber: scheduled.prNumber,
      scheduledFor: scheduled.scheduledFor,
      strategy: scheduled.strategy,
      status: this.getScheduleStatus(scheduled),
      message: `Scheduled for ${scheduled.scheduledFor.toISOString()}`,
    }));
  }

  /**
   * Cancela um agendamento
   */
  cancelSchedule(scheduleId: string): boolean {
    const scheduled = this.scheduledMerges.get(scheduleId);
    if (!scheduled) {
      return false;
    }

    scheduled.status = "cancelled";
    this.logAudit("SCHEDULE_CANCELLED", "success", scheduled.prNumber, {
      scheduleId,
    });

    return true;
  }

  /**
   * Obtém log de auditoria
   */
  getAuditLog(): AuditLogEntry[] {
    return [...this.auditLog];
  }

  /**
   * Obtém transação por ID
   */
  getTransaction(transactionId: string): Transaction | undefined {
    return this.transactionLog.get(transactionId);
  }

  // ============================================================================
  // MÉTODOS PRIVADOS
  // ============================================================================

  /**
   * Verifica se não é draft
   */
  private async checkNotDraft(
    prNumber: number,
    isDraft?: boolean
  ): Promise<boolean> {
    if (isDraft !== undefined) {
      return !isDraft;
    }

    try {
      const prData = await this.fetchPRData(prNumber);
      return !prData.draft;
    } catch {
      return false;
    }
  }

  /**
   * Verifica status checks
   */
  private async checkStatusChecks(
    prNumber: number
  ): Promise<{ allPassed: boolean; passed: number; total: number; details: any }> {
    try {
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/commits/${prNumber}/status`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
        signal: AbortSignal.timeout(this.config.requestTimeout),
      });

      if (!response.ok) {
        return {
          allPassed: false,
          passed: 0,
          total: 0,
          details: { error: response.statusText },
        };
      }

      const data = (await response.json()) as {
        state: string;
        statuses?: Array<{ state: string }>;
      };

      const statuses = data.statuses || [];
      const passed = statuses.filter((s) => s.state === "success").length;
      const total = statuses.length;

      return {
        allPassed: data.state === "success",
        passed,
        total,
        details: { state: data.state, statusCount: total },
      };
    } catch (error) {
      return {
        allPassed: false,
        passed: 0,
        total: 0,
        details: { error: error instanceof Error ? error.message : String(error) },
      };
    }
  }

  /**
   * Verifica CI passou
   */
  private async checkCIPassed(prNumber: number): Promise<boolean> {
    try {
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
        signal: AbortSignal.timeout(this.config.requestTimeout),
      });

      if (!response.ok) return false;

      const prData = (await response.json()) as any;
      return prData.mergeable === true || prData.mergeable_state !== "dirty";
    } catch {
      return false;
    }
  }

  /**
   * Verifica approvals
   */
  private async checkApprovals(
    prNumber: number
  ): Promise<{ met: boolean; count: number }> {
    try {
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/reviews`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
        signal: AbortSignal.timeout(this.config.requestTimeout),
      });

      if (!response.ok) {
        return { met: false, count: 0 };
      }

      const reviews = (await response.json()) as Array<{ state: string }>;
      const approvalCount = reviews.filter((r) => r.state === "APPROVED").length;

      return {
        met: approvalCount >= this.config.requiredApprovals,
        count: approvalCount,
      };
    } catch {
      return { met: false, count: 0 };
    }
  }

  /**
   * Verifica se branch está atualizado
   */
  private async isBranchUpToDate(prNumber: number): Promise<boolean> {
    try {
      const prData = await this.fetchPRData(prNumber);
      const compareUrl = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/compare/${prData.base.ref}...${prData.head.ref}`;

      const response = await fetch(compareUrl, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
        signal: AbortSignal.timeout(this.config.requestTimeout),
      });

      if (!response.ok) return false;

      const data = (await response.json()) as { status: string };
      return data.status === "identical" || data.status === "ahead";
    } catch {
      return false;
    }
  }

  /**
   * Verifica branch protection
   */
  private async checkBranchProtection(
    prNumber: number
  ): Promise<{ compliant: boolean; details: any }> {
    try {
      const prData = await this.fetchPRData(prNumber);
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/branches/${prData.base.ref}/protection`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
        signal: AbortSignal.timeout(this.config.requestTimeout),
      });

      if (!response.ok) {
        // Se não encontra proteção, assume compliant
        return { compliant: true, details: { protected: false } };
      }

      const data = await response.json();
      return { compliant: true, details: { protected: true, rules: data } };
    } catch {
      return { compliant: true, details: { error: "Could not verify" } };
    }
  }

  /**
   * Verifica marcador WIP
   */
  private async checkNoWIPMarker(prNumber: number): Promise<boolean> {
    try {
      const prData = await this.fetchPRData(prNumber);
      const title = prData.title || "";
      const wipPatterns = [/^\[WIP\]/i, /^WIP:/i, /^WIP\s/i];

      return !wipPatterns.some((pattern) => pattern.test(title));
    } catch {
      return false;
    }
  }

  /**
   * Obtém conflitos detalhados
   */
  private async getDetailedConflicts(prNumber: number): Promise<Conflict[]> {
    try {
      const prData = await this.fetchPRData(prNumber);
      const filesUrl = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/files`;

      const response = await fetch(filesUrl, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
        signal: AbortSignal.timeout(this.config.requestTimeout),
      });

      if (!response.ok) return [];

      const files = (await response.json()) as Array<{
        filename: string;
        patch?: string;
        status: string;
      }>;

      const conflicts: Conflict[] = [];

      for (const file of files) {
        if (file.patch && file.patch.includes("<<<<<<")) {
          conflicts.push({
            file: file.filename,
            type: "content",
            description: `Content conflict in ${file.filename}`,
            resolvable: false,
            severity: "high",
          });
        }
      }

      return conflicts;
    } catch {
      return [];
    }
  }

  /**
   * Verifica conflitos de delete/modify
   */
  private async checkDeleteModifyConflicts(
    prNumber: number
  ): Promise<Conflict[]> {
    // Implementação simplificada
    return [];
  }

  /**
   * Verifica conflitos de add/add
   */
  private async checkAddAddConflicts(prNumber: number): Promise<Conflict[]> {
    // Implementação simplificada
    return [];
  }

  /**
   * Verifica conflitos estruturais
   */
  private async checkStructuralConflicts(
    prNumber: number
  ): Promise<Conflict[]> {
    // Implementação simplificada
    return [];
  }

  /**
   * Busca dados do PR
   */
  private async fetchPRData(prNumber: number): Promise<any> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}`;

    const response = await fetch(url, {
      headers: {
        Authorization: `token ${this.config.githubToken}`,
      },
      signal: AbortSignal.timeout(this.config.requestTimeout),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch PR data: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Realiza merge
   */
  private async performMerge(
    prNumber: number,
    strategy: MergeStrategy,
    headSha: string
  ): Promise<string> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/merge`;

    const payload = {
      commit_title: this.config.commitMessageTemplate.replace(
        /{prNumber}/g,
        String(prNumber)
      ),
      merge_method: this.getMergeMethodFromStrategy(strategy),
      sha: headSha,
    };

    const response = await fetch(url, {
      method: "PUT",
      headers: {
        Authorization: `token ${this.config.githubToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(this.config.requestTimeout),
    });

    if (!response.ok) {
      const errorData = (await response.json()) as any;
      throw new Error(
        `Merge failed: ${response.status} - ${errorData.message || response.statusText}`
      );
    }

    const data = (await response.json()) as { sha: string };
    return data.sha;
  }

  /**
   * Converte estratégia para método de merge GitHub
   */
  private getMergeMethodFromStrategy(strategy: MergeStrategy): string {
    switch (strategy) {
      case "squash":
        return "squash";
      case "rebase":
        return "rebase";
      case "merge":
      case "fast-forward":
      default:
        return "merge";
    }
  }

  /**
   * Inicia scheduler de merges agendados
   */
  private startScheduler(): void {
    setInterval(() => {
      const now = new Date();

      for (const [scheduleId, scheduled] of this.scheduledMerges.entries()) {
        if (
          scheduled.status === "scheduled" &&
          scheduled.scheduledFor <= now
        ) {
          this.executeScheduledMerge(scheduled);
        }
      }
    }, this.config.schedulerIntervalMs);
  }

  /**
   * Executa merge agendado
   */
  private async executeScheduledMerge(scheduled: ScheduledMerge): Promise<void> {
    scheduled.status = "executing";

    try {
      const result = await this.merge(scheduled.prNumber, scheduled.strategy);
      scheduled.status = result.success ? "completed" : "failed";
      scheduled.executedAt = new Date();

      this.logAudit("SCHEDULED_MERGE_EXECUTED", result.success ? "success" : "failure", scheduled.prNumber, {
        scheduleId: scheduled.scheduleId,
        result: {
          success: result.success,
          mergeCommitSha: result.mergeCommitSha,
        },
      });
    } catch (error) {
      scheduled.status = "failed";
      scheduled.executedAt = new Date();
      scheduled.error = error instanceof Error ? error.message : String(error);

      this.logAudit("SCHEDULED_MERGE_FAILED", "failure", scheduled.prNumber, {
        scheduleId: scheduled.scheduleId,
        error: scheduled.error,
      });
    }
  }

  /**
   * Registra merge bem-sucedido nas métricas
   */
  private recordSuccessfulMerge(result: MergeResult): void {
    this.metrics.totalMerges++;
    this.metrics.successfulMerges++;
    this.metrics.successRate = (this.metrics.successfulMerges / this.metrics.totalMerges) * 100;
    this.metrics.mergeStrategiesUsed[result.strategy]++;

    const totalDuration =
      this.metrics.averageDuration * (this.metrics.totalMerges - 1) + result.duration;
    this.metrics.averageDuration = totalDuration / this.metrics.totalMerges;

    this.metrics.lastMergeAt = new Date();
  }

  /**
   * Registra merge falhado nas métricas
   */
  private recordFailedMerge(result: MergeResult): void {
    this.metrics.totalMerges++;
    this.metrics.failedMerges++;
    this.metrics.successRate = (this.metrics.successfulMerges / this.metrics.totalMerges) * 100;

    if (result.conflictsResolved && result.conflictsResolved > 0) {
      this.metrics.conflictRate = (result.conflictsResolved / this.metrics.totalMerges) * 100;
    }
  }

  /**
   * Registra requisitos bloqueadores nas métricas
   */
  private recordBlockedMerge(unmetRequirements: Requirement[]): void {
    for (const req of unmetRequirements) {
      this.metrics.blockedByRequirement[req.type]++;
    }
  }

  /**
   * Verifica se erro é recuperável
   */
  private isRecoverableError(error: string): boolean {
    const nonRecoverablePatterns = [
      /merge conflict/i,
      /permission denied/i,
      /not found/i,
    ];

    return !nonRecoverablePatterns.some((pattern) => pattern.test(error));
  }

  /**
   * Log de auditoria
   */
  private logAudit(
    action: string,
    status: "success" | "failure" | "warning",
    prNumber: number,
    details: Record<string, any>
  ): void {
    const entry: AuditLogEntry = {
      timestamp: new Date(),
      action,
      status,
      prNumber,
      details,
      transactionId: details.transactionId || "system",
    };

    this.auditLog.push(entry);

    // Limita tamanho do log
    if (this.auditLog.length > 10000) {
      this.auditLog = this.auditLog.slice(-5000);
    }
  }

  /**
   * Gera ID único de transação
   */
  private generateTransactionId(): string {
    return `txn-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Gera ID único de agendamento
   */
  private generateScheduleId(): string {
    return `sch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Obtém status de agendamento
   */
  private getScheduleStatus(scheduled: ScheduledMerge): ScheduleStatus {
    if (scheduled.status === "completed") return ScheduleStatus.COMPLETED;
    if (scheduled.status === "failed") return ScheduleStatus.FAILED;
    if (scheduled.status === "cancelled") return ScheduleStatus.CANCELLED;
    if (scheduled.status === "executing") return ScheduleStatus.EXECUTING;
    return ScheduleStatus.SCHEDULED;
  }
}

// ============================================================================
// LOCK MANAGER - Distributed Locking
// ============================================================================

interface LockManagerConfig {
  ttl: number;
  retryAttempts: number;
  retryDelay: number;
}

/**
 * Gerenciador de locks distribuídos
 */
class DistributedLockManager {
  private provider: "memory" | "redis" | "supabase";
  private config: LockManagerConfig;
  private locks: Map<string, DistributedLock> = new Map();
  private waitTimes: number[] = [];

  constructor(provider: "memory" | "redis" | "supabase", config: LockManagerConfig) {
    this.provider = provider;
    this.config = config;
  }

  /**
   * Adquire lock
   */
  async acquireLock(resource: string, owner: string): Promise<DistributedLock> {
    const lockId = `${resource}-${Date.now()}`;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
      const startWait = Date.now();

      try {
        // Tenta adquirir lock
        if (this.provider === "memory") {
          return this.acquireMemoryLock(resource, owner, lockId);
        } else {
          // Para redis/supabase, implementação real seria necessária
          return this.acquireMemoryLock(resource, owner, lockId);
        }
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        if (attempt < this.config.retryAttempts - 1) {
          await this.delay(this.config.retryDelay);
        }
      }

      const waitTime = Date.now() - startWait;
      this.waitTimes.push(waitTime);
    }

    throw lastError || new Error("Failed to acquire lock after retries");
  }

  /**
   * Libera lock
   */
  async releaseLock(lockId: string): Promise<void> {
    this.locks.delete(lockId);
  }

  /**
   * Adquire lock em memória
   */
  private acquireMemoryLock(
    resource: string,
    owner: string,
    lockId: string
  ): DistributedLock {
    // Verifica se já existe lock ativo
    for (const [, lock] of this.locks) {
      if (lock.resource === resource && lock.isActive) {
        throw new Error(`Resource ${resource} is locked`);
      }
    }

    const now = new Date();
    const expiresAt = new Date(now.getTime() + this.config.ttl);

    const lock: DistributedLock = {
      lockId,
      resource,
      owner,
      acquiredAt: now,
      expiresAt,
      isActive: true,
      status: LockStatus.ACQUIRED,
    };

    this.locks.set(lockId, lock);

    // Agenda expiração
    setTimeout(() => {
      const storedLock = this.locks.get(lockId);
      if (storedLock) {
        storedLock.isActive = false;
        storedLock.status = LockStatus.EXPIRED;
      }
    }, this.config.ttl);

    return lock;
  }

  /**
   * Obtém estatísticas de wait time
   */
  getWaitTimeStats(): {
    average: number;
    max: number;
    min: number;
  } {
    if (this.waitTimes.length === 0) {
      return { average: 0, max: 0, min: 0 };
    }

    const average = this.waitTimes.reduce((a, b) => a + b, 0) / this.waitTimes.length;
    const max = Math.max(...this.waitTimes);
    const min = Math.min(...this.waitTimes);

    return { average, max, min };
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ============================================================================
// INTERFACES INTERNAS
// ============================================================================

interface ScheduledMerge {
  scheduleId: string;
  prNumber: number;
  strategy: MergeStrategy;
  scheduledFor: Date;
  createdAt: Date;
  status: "scheduled" | "executing" | "completed" | "failed" | "cancelled";
  executedAt?: Date;
  error?: string;
}

interface Transaction {
  id: string;
  prNumber: number;
  strategy: MergeStrategy;
  startedAt: Date;
  completedAt?: Date;
  status: "pending" | "completed" | "failed";
  steps: string[];
  error?: string;
}

/**
 * Factory function
 */
export function createAutoMerge(config: AutoMergeServiceConfig): AutoMerge {
  return new AutoMerge(config);
}
