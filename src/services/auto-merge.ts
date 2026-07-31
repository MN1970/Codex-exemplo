/**
 * Auto-Merge Controller — Automação inteligente de merge de PRs
 * Versão: 1.0.0
 *
 * Recursos:
 * - Verifica pré-requisitos antes de merge (CI, approvals, conflicts)
 * - Merge automático com mensagem padrão
 * - Deleção de feature branch pós-merge
 * - Audit trail completo
 * - Fallback com notificação para humano
 * - Integração com GitHub API
 */

/**
 * Status de merge
 */
export enum MergeStatus {
  PENDING = "pending",
  CHECKING_PREREQUISITES = "checking_prerequisites",
  READY_TO_MERGE = "ready_to_merge",
  MERGING = "merging",
  MERGED = "merged",
  FAILED = "failed",
  BLOCKED = "blocked",
  REQUIRES_HUMAN_REVIEW = "requires_human_review",
}

/**
 * Razão de bloqueio
 */
export enum BlockReason {
  CI_FAILED = "ci_failed",
  MISSING_APPROVALS = "missing_approvals",
  MERGE_CONFLICTS = "merge_conflicts",
  BRANCH_OUTDATED = "branch_outdated",
  REQUIRED_STATUS_CHECK_FAILED = "required_status_check_failed",
  DRAFT_PR = "draft_pr",
  NETWORK_ERROR = "network_error",
  PERMISSION_DENIED = "permission_denied",
  UNKNOWN = "unknown",
}

/**
 * Resultado de verificação de pré-requisito
 */
export interface PrerequisiteCheckResult {
  passed: boolean;
  checks: {
    ciPassed: boolean;
    approvalsOk: boolean;
    noConflicts: boolean;
    notDraft: boolean;
    branchProtectionOk: boolean;
  };
  blockedBy?: BlockReason[];
  details: string;
}

/**
 * Evento de audit trail
 */
export interface AuditEvent {
  timestamp: Date;
  action: string;
  status: string;
  prNumber: number;
  owner: string;
  repo: string;
  details?: Record<string, any>;
  error?: string;
  userId?: string;
}

/**
 * Resultado de merge
 */
export interface MergeResult {
  success: boolean;
  prNumber: number;
  owner: string;
  repo: string;
  status: MergeStatus;
  sha?: string;
  mergeCommitSha?: string;
  blockedBy?: BlockReason[];
  prerequisitesCheck?: PrerequisiteCheckResult;
  branchDeleted?: boolean;
  auditEvents: AuditEvent[];
  timestamp: Date;
  duration?: number; // ms
  error?: string;
}

/**
 * Configuração do auto-merge controller
 */
export interface AutoMergeConfig {
  githubToken: string;
  owner: string;
  repo: string;

  // Pré-requisitos
  requireCIPassed?: boolean; // default: true
  requiredApprovals?: number; // default: 1
  allowMergingWithConflicts?: boolean; // default: false

  // Merge strategy
  mergeMethod?: "merge" | "squash" | "rebase"; // default: "merge"
  commitMessage?: string;
  commitDescription?: string;
  deleteBranchAfterMerge?: boolean; // default: true

  // Audit
  auditTableUrl?: string; // Supabase table URL para audit trail
  auditApiKey?: string;

  // Notificações
  notifyOnBlock?: boolean; // default: true
  slackWebhook?: string; // Para notificações em caso de bloqueio

  // Thresholds
  maxWaitForCI?: number; // ms
  checkInterval?: number; // ms
}

/**
 * Resposta da API de PR do GitHub
 */
interface GitHubPR {
  number: number;
  state: string;
  draft: boolean;
  mergeable: boolean | null;
  mergeable_state: string;
  title: string;
  head: {
    ref: string;
    sha: string;
  };
  base: {
    ref: string;
  };
  merged: boolean;
  merge_commit_sha: string | null;
}

/**
 * Classe principal do Auto-Merge Controller
 */
export class AutoMergeController {
  private config: Required<AutoMergeConfig>;
  private apiBaseUrl = "https://api.github.com";
  private auditLog: AuditEvent[] = [];

  constructor(config: AutoMergeConfig) {
    this.config = {
      requireCIPassed: true,
      requiredApprovals: 1,
      allowMergingWithConflicts: false,
      mergeMethod: "merge",
      deleteBranchAfterMerge: true,
      notifyOnBlock: true,
      maxWaitForCI: 300000, // 5 min
      checkInterval: 10000, // 10s
      ...config,
      commitMessage: config.commitMessage || "Merge pull request",
      commitDescription: config.commitDescription || "",
      auditTableUrl: config.auditTableUrl || "",
      auditApiKey: config.auditApiKey || "",
      slackWebhook: config.slackWebhook || "",
    };
  }

  /**
   * Executa auto-merge de um PR
   */
  async mergePR(prNumber: number): Promise<MergeResult> {
    const startTime = Date.now();
    const result: MergeResult = {
      success: false,
      prNumber,
      owner: this.config.owner,
      repo: this.config.repo,
      status: MergeStatus.PENDING,
      auditEvents: [],
      timestamp: new Date(),
    };

    try {
      this.logAuditEvent("AUTO_MERGE_STARTED", MergeStatus.PENDING, prNumber, {
        config: {
          mergeMethod: this.config.mergeMethod,
          deleteBranchAfterMerge: this.config.deleteBranchAfterMerge,
        },
      });

      // 1. Busca dados do PR
      result.status = MergeStatus.CHECKING_PREREQUISITES;
      const prData = await this.fetchPRData(prNumber);

      // 2. Verifica pré-requisitos
      const prerequisitesCheck = await this.checkPrerequisites(prNumber, prData);
      result.prerequisitesCheck = prerequisitesCheck;

      if (!prerequisitesCheck.passed) {
        result.status = MergeStatus.BLOCKED;
        result.blockedBy = prerequisitesCheck.blockedBy || [BlockReason.UNKNOWN];

        this.logAuditEvent("PREREQUISITES_CHECK_FAILED", MergeStatus.BLOCKED, prNumber, {
          blockedBy: prerequisitesCheck.blockedBy,
          details: prerequisitesCheck.details,
        });

        // Notifica humano
        if (this.config.notifyOnBlock) {
          await this.notifyHumanReview(prNumber, prerequisitesCheck.blockedBy || []);
        }

        result.auditEvents = this.auditLog;
        result.duration = Date.now() - startTime;
        return result;
      }

      this.logAuditEvent("PREREQUISITES_CHECK_PASSED", MergeStatus.READY_TO_MERGE, prNumber);

      // 3. Merge
      result.status = MergeStatus.MERGING;
      const mergeResult = await this.performMerge(prNumber, prData.head.sha);
      result.mergeCommitSha = mergeResult.sha;
      result.sha = prData.head.sha;

      this.logAuditEvent("MERGE_COMPLETED", MergeStatus.MERGED, prNumber, {
        mergeCommitSha: mergeResult.sha,
        mergeMethod: this.config.mergeMethod,
      });

      // 4. Deleta branch se configurado
      if (this.config.deleteBranchAfterMerge) {
        try {
          await this.deleteBranch(prData.head.ref);
          result.branchDeleted = true;

          this.logAuditEvent("BRANCH_DELETED", MergeStatus.MERGED, prNumber, {
            branch: prData.head.ref,
          });
        } catch (error) {
          console.warn("Failed to delete branch:", error);
          // Não falha o merge se a deleção falhar
          this.logAuditEvent("BRANCH_DELETE_FAILED", MergeStatus.MERGED, prNumber, {
            branch: prData.head.ref,
            error: error instanceof Error ? error.message : String(error),
          });
        }
      }

      // 5. Persiste audit trail
      if (this.config.auditTableUrl) {
        await this.persistAuditLog();
      }

      result.success = true;
      result.status = MergeStatus.MERGED;
      result.auditEvents = this.auditLog;
      result.duration = Date.now() - startTime;

      this.logAuditEvent("AUTO_MERGE_COMPLETED_SUCCESS", MergeStatus.MERGED, prNumber, {
        duration: result.duration,
      });

      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);

      result.status = MergeStatus.FAILED;
      result.error = errorMsg;
      result.auditEvents = this.auditLog;
      result.duration = Date.now() - startTime;

      this.logAuditEvent("AUTO_MERGE_FAILED", MergeStatus.FAILED, prNumber, {
        error: errorMsg,
        duration: result.duration,
      });

      // Notifica humano em caso de erro desconhecido
      if (this.config.notifyOnBlock) {
        await this.notifyHumanReview(prNumber, [BlockReason.NETWORK_ERROR]);
      }

      // Persiste audit trail mesmo em caso de erro
      if (this.config.auditTableUrl) {
        await this.persistAuditLog().catch(console.error);
      }

      return result;
    }
  }

  /**
   * Verifica pré-requisitos para merge
   */
  private async checkPrerequisites(
    prNumber: number,
    prData: GitHubPR
  ): Promise<PrerequisiteCheckResult> {
    const result: PrerequisiteCheckResult = {
      passed: true,
      checks: {
        ciPassed: true,
        approvalsOk: true,
        noConflicts: true,
        notDraft: true,
        branchProtectionOk: true,
      },
      blockedBy: [],
      details: "",
    };

    // 1. Verifica se é draft
    if (prData.draft) {
      result.checks.notDraft = false;
      result.blockedBy?.push(BlockReason.DRAFT_PR);
      result.details += "PR is in draft mode. ";
    }

    // 2. Verifica conflitos de merge
    if (prData.mergeable === false || prData.mergeable_state === "dirty") {
      result.checks.noConflicts = false;
      result.blockedBy?.push(BlockReason.MERGE_CONFLICTS);
      result.details += "PR has merge conflicts. ";
    }

    if (!this.config.allowMergingWithConflicts && prData.mergeable_state === "dirty") {
      result.passed = false;
    }

    // 3. Verifica CI passed
    if (this.config.requireCIPassed) {
      const ciPassed = await this.checkCIPassed(prNumber);
      result.checks.ciPassed = ciPassed;

      if (!ciPassed) {
        result.blockedBy?.push(BlockReason.CI_FAILED);
        result.details += "CI pipeline has not passed. ";
        result.passed = false;
      }
    }

    // 4. Verifica approvals
    const approvalsResult = await this.checkApprovals(prNumber);
    result.checks.approvalsOk = approvalsResult.approved;

    if (!approvalsResult.approved) {
      result.blockedBy?.push(BlockReason.MISSING_APPROVALS);
      result.details += `Missing approvals (current: ${approvalsResult.approvalCount}/${this.config.requiredApprovals}). `;
      result.passed = false;
    }

    // 5. Verifica branch outdated
    const isOutdated = await this.isBranchOutdated(prNumber, prData);
    if (isOutdated) {
      result.blockedBy?.push(BlockReason.BRANCH_OUTDATED);
      result.details += "Branch is outdated. ";
      // Não bloqueia, mas avisa
    }

    // 6. Verifica status checks
    const statusChecks = await this.checkStatusChecks(prNumber);
    result.checks.branchProtectionOk = statusChecks.allPassed;

    if (!statusChecks.allPassed) {
      result.blockedBy?.push(BlockReason.REQUIRED_STATUS_CHECK_FAILED);
      result.details += `Failed status checks: ${statusChecks.failed.join(", ")}. `;
      result.passed = false;
    }

    return result;
  }

  /**
   * Verifica se CI passou
   */
  private async checkCIPassed(prNumber: number): Promise<boolean> {
    try {
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/status`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!response.ok) {
        console.warn("Failed to check CI status:", response.statusText);
        return false;
      }

      const data = (await response.json()) as {
        state: string;
        statuses?: Array<{ state: string; context: string }>;
      };

      // State pode ser: pending, success, failure, error
      return data.state === "success";
    } catch (error) {
      console.error("Error checking CI status:", error);
      return false;
    }
  }

  /**
   * Verifica status checks
   */
  private async checkStatusChecks(
    prNumber: number
  ): Promise<{ allPassed: boolean; failed: string[] }> {
    try {
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/status`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!response.ok) {
        return { allPassed: false, failed: ["Unable to check status"] };
      }

      const data = (await response.json()) as {
        state: string;
        statuses?: Array<{ state: string; context: string }>;
      };

      const failedChecks = (data.statuses || [])
        .filter((s) => s.state !== "success")
        .map((s) => s.context);

      return {
        allPassed: failedChecks.length === 0,
        failed: failedChecks,
      };
    } catch (error) {
      console.error("Error checking status checks:", error);
      return { allPassed: false, failed: ["Error fetching status"] };
    }
  }

  /**
   * Verifica approvals
   */
  private async checkApprovals(
    prNumber: number
  ): Promise<{ approved: boolean; approvalCount: number }> {
    try {
      const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/reviews`;

      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!response.ok) {
        console.warn("Failed to check approvals:", response.statusText);
        return { approved: false, approvalCount: 0 };
      }

      const reviews = (await response.json()) as Array<{
        state: string;
        user: { login: string };
      }>;

      // Conta aprovações únicas (por usuário)
      const approvedUsers = new Set(
        reviews.filter((r) => r.state === "APPROVED").map((r) => r.user.login)
      );

      const approvalCount = approvedUsers.size;
      const approved = approvalCount >= this.config.requiredApprovals;

      return { approved, approvalCount };
    } catch (error) {
      console.error("Error checking approvals:", error);
      return { approved: false, approvalCount: 0 };
    }
  }

  /**
   * Verifica se branch está outdated
   */
  private async isBranchOutdated(prNumber: number, prData: GitHubPR): Promise<boolean> {
    try {
      // Busca commit do head
      const headUrl = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/commits/${prData.head.sha}`;
      const headResponse = await fetch(headUrl, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
      });

      if (!headResponse.ok) return false;

      // Busca commit do base
      const baseUrl = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/commits/${prData.base.ref}`;
      const baseResponse = await fetch(baseUrl, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
        },
      });

      if (!baseResponse.ok) return false;

      const headData = (await headResponse.json()) as { commit: { committer: { date: string } } };
      const baseData = (await baseResponse.json()) as { commit: { committer: { date: string } } };

      const headDate = new Date(headData.commit.committer.date);
      const baseDate = new Date(baseData.commit.committer.date);

      return headDate < baseDate;
    } catch (error) {
      console.warn("Error checking if branch is outdated:", error);
      return false;
    }
  }

  /**
   * Executa merge
   */
  private async performMerge(prNumber: number, headSha: string): Promise<{ sha: string }> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}/merge`;

    const payload = {
      commit_title: this.config.commitMessage,
      commit_message: this.config.commitDescription,
      sha: headSha,
      merge_method: this.config.mergeMethod,
    };

    try {
      const response = await fetch(url, {
        method: "PUT",
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = (await response.json()) as { message?: string };
        throw new Error(
          `Merge failed: ${response.status} ${response.statusText} - ${errorData.message || ""}`
        );
      }

      const data = (await response.json()) as { sha: string };
      return { sha: data.sha };
    } catch (error) {
      throw new Error(`Failed to merge PR: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Deleta feature branch
   */
  private async deleteBranch(branchRef: string): Promise<void> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/git/refs/heads/${branchRef}`;

    try {
      const response = await fetch(url, {
        method: "DELETE",
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!response.ok && response.status !== 422) {
        // 422 = branch not found, que é ok
        throw new Error(`Delete branch failed: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      throw new Error(
        `Failed to delete branch: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  /**
   * Busca dados do PR
   */
  private async fetchPRData(prNumber: number): Promise<GitHubPR> {
    const url = `${this.apiBaseUrl}/repos/${this.config.owner}/${this.config.repo}/pulls/${prNumber}`;

    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `token ${this.config.githubToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch PR data: ${response.status} ${response.statusText}`);
      }

      return (await response.json()) as GitHubPR;
    } catch (error) {
      throw new Error(`Failed to fetch PR data: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Log de evento de audit
   */
  private logAuditEvent(
    action: string,
    status: string,
    prNumber: number,
    details?: Record<string, any>
  ): void {
    const event: AuditEvent = {
      timestamp: new Date(),
      action,
      status,
      prNumber,
      owner: this.config.owner,
      repo: this.config.repo,
      details,
    };

    this.auditLog.push(event);
    console.log(`[AUDIT] ${action} - ${status}`, details);
  }

  /**
   * Persiste audit log no Supabase
   */
  private async persistAuditLog(): Promise<void> {
    if (!this.config.auditTableUrl || !this.config.auditApiKey) {
      return;
    }

    try {
      for (const event of this.auditLog) {
        const payload = {
          timestamp: event.timestamp.toISOString(),
          action: event.action,
          status: event.status,
          pr_number: event.prNumber,
          owner: event.owner,
          repo: event.repo,
          details: JSON.stringify(event.details || {}),
          error: event.error,
        };

        const response = await fetch(this.config.auditTableUrl, {
          method: "POST",
          headers: {
            apikey: this.config.auditApiKey,
            Authorization: `Bearer ${this.config.auditApiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok && response.status !== 409) {
          console.warn(`Failed to persist audit event: ${response.statusText}`);
        }
      }
    } catch (error) {
      console.warn("Error persisting audit log:", error);
      // Não falha se a persistência falhar
    }
  }

  /**
   * Notifica humano para revisar
   */
  private async notifyHumanReview(prNumber: number, blockedBy: BlockReason[]): Promise<void> {
    const message = `
⚠️ **Auto-Merge Blocked** — PR #${prNumber} requires human review

**Blocked by:** ${blockedBy.join(", ")}

**Repository:** ${this.config.owner}/${this.config.repo}
**Action:** https://github.com/${this.config.owner}/${this.config.repo}/pull/${prNumber}

Please review and address the blocking issues.
    `.trim();

    // Tenta notificar via Slack se configurado
    if (this.config.slackWebhook) {
      await this.notifySlack(message);
    }

    // Log como fallback
    console.warn(`[HUMAN_REVIEW_REQUIRED] PR #${prNumber}: ${blockedBy.join(", ")}`);
  }

  /**
   * Notifica via Slack
   */
  private async notifySlack(message: string): Promise<void> {
    try {
      const response = await fetch(this.config.slackWebhook, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: message,
          mrkdwn: true,
        }),
      });

      if (!response.ok) {
        console.warn("Failed to send Slack notification:", response.statusText);
      }
    } catch (error) {
      console.warn("Error sending Slack notification:", error);
    }
  }

  /**
   * Retorna log de audit
   */
  getAuditLog(): AuditEvent[] {
    return [...this.auditLog];
  }

  /**
   * Limpa audit log
   */
  clearAuditLog(): void {
    this.auditLog = [];
  }
}

/**
 * Factory function para criar instância
 */
export function createAutoMergeController(config: AutoMergeConfig): AutoMergeController {
  return new AutoMergeController(config);
}
