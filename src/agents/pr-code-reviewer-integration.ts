/**
 * PR Code Reviewer Integration
 *
 * Integra o CodeReviewerAgent com o sistema de PR Automation existente.
 * Permite análise automática de PRs durante o fluxo de CI/CD.
 */

import { CodeReviewerAgent, type CodeReviewInput, type CodeReviewOutput } from "./code-reviewer";

/**
 * Interface de PR do GitHub
 */
export interface GitHubPRPayload {
  pull_request: {
    number: number;
    title: string;
    body: string;
    user: { login: string };
    head: { ref: string };
    base: { ref: string };
  };
  repository: {
    name: string;
    owner: { login: string };
  };
}

/**
 * Interface de diff
 */
export interface PullRequestDiff {
  files: Array<{
    filename: string;
    patch?: string;
    additions: number;
    deletions: number;
    status: string;
  }>;
  merged_diff?: string;
}

/**
 * Resultado integrado de análise
 */
export interface PRCodeReviewResult extends CodeReviewOutput {
  prNumber: number;
  owner: string;
  repo: string;
  actionRequired: boolean;
  blockingIssues: number;
  suggestedAction: "approve" | "request-changes" | "comment";
}

/**
 * Integração do Code Reviewer com fluxo de PR
 */
export class PRCodeReviewerIntegration {
  private reviewerAgent: CodeReviewerAgent;

  constructor(apiKey?: string) {
    this.reviewerAgent = new CodeReviewerAgent(apiKey);
  }

  /**
   * Analisa PR a partir do webhook do GitHub
   */
  async reviewPullRequest(
    prPayload: GitHubPRPayload,
    diffData: PullRequestDiff,
    newAgentCode?: string
  ): Promise<PRCodeReviewResult> {
    const { pull_request, repository } = prPayload;

    // Agrupa diff
    const mergedDiff = this.mergeDiffs(diffData.files);

    // Detecta se é novo agente
    const isNewAgent = this.detectNewAgentFile(diffData.files);
    const agentPath = isNewAgent ? this.findAgentPath(diffData.files) : "";

    // Prepara input de review
    const reviewInput: CodeReviewInput = {
      prDiff: mergedDiff,
      newAgentCode: newAgentCode || "",
      agentPath,
      prContext: {
        title: pull_request.title,
        description: pull_request.body,
        author: pull_request.user.login,
      },
      // Foca em dimensões críticas para PRs
      dimensions: ["correctness", "security"],
    };

    // Executa review
    const reviewResult = await this.reviewerAgent.reviewCode(reviewInput);

    // Enriquece resultado com metadados de PR
    const enriched: PRCodeReviewResult = {
      ...reviewResult,
      prNumber: pull_request.number,
      owner: repository.owner.login,
      repo: repository.name,
      actionRequired: this.requiresAction(reviewResult),
      blockingIssues: this.countBlockingIssues(reviewResult.findings),
      suggestedAction: this.suggestAction(reviewResult),
    };

    return enriched;
  }

  /**
   * Filtra arquivos de agentes para análise aprofundada
   */
  filterAgentFiles(files: PullRequestDiff["files"]): PullRequestDiff["files"] {
    return files.filter(
      (f) =>
        f.filename.startsWith("src/agents/") &&
        (f.filename.endsWith(".ts") || f.filename.endsWith(".md"))
    );
  }

  /**
   * Detecta se PR contém novo agente
   */
  private detectNewAgentFile(files: PullRequestDiff["files"]): boolean {
    return files.some((f) => {
      const isAgent = f.filename.startsWith("src/agents/agente-");
      const isNew = f.status === "added";
      return isAgent && isNew;
    });
  }

  /**
   * Encontra caminho do novo agente
   */
  private findAgentPath(files: PullRequestDiff["files"]): string {
    const agentFile = files.find(
      (f) =>
        f.filename.startsWith("src/agents/agente-") &&
        f.status === "added" &&
        f.filename.endsWith(".ts")
    );
    return agentFile?.filename || "src/agents/new-agent.ts";
  }

  /**
   * Mescla diffs de múltiplos arquivos
   */
  private mergeDiffs(files: PullRequestDiff["files"]): string {
    return files
      .filter((f) => f.patch)
      .map((f) => f.patch)
      .join("\n\n");
  }

  /**
   * Conta issues bloqueantes
   */
  private countBlockingIssues(findings: CodeReviewOutput["findings"]): number {
    return findings.filter((f) => f.severity === "critical").length;
  }

  /**
   * Determina se análise requer ação
   */
  private requiresAction(result: CodeReviewOutput): boolean {
    // Requer ação se há critical ou error em security/correctness
    const criticalSecurityIssues = result.findings.filter(
      (f) =>
        f.severity === "critical" &&
        (f.dimension === "security" || f.dimension === "correctness")
    );

    return criticalSecurityIssues.length > 0 || result.overallScore < 70;
  }

  /**
   * Sugere ação recomendada para o PR
   */
  private suggestAction(result: CodeReviewOutput): "approve" | "request-changes" | "comment" {
    const blockingCount = result.findings.filter((f) => f.severity === "critical").length;
    const warningCount = result.findings.filter((f) => f.severity === "warning").length;

    if (blockingCount > 0 || result.overallScore < 60) {
      return "request-changes";
    } else if (warningCount > 2 || result.overallScore < 80) {
      return "comment";
    } else {
      return "approve";
    }
  }

  /**
   * Gera comentário para PR no GitHub
   */
  generatePRComment(result: PRCodeReviewResult): string {
    const emoji = {
      approve: "✅",
      "request-changes": "⚠️",
      comment: "💬",
    };

    const lines: string[] = [];

    lines.push(`${emoji[result.suggestedAction]} Code Review by Opus`);
    lines.push(`**Score: ${result.overallScore}/100**\n`);

    if (result.findings.length === 0) {
      lines.push("✨ No issues found! Ready to merge.");
      return lines.join("\n");
    }

    lines.push(`## Findings (${result.findings.length} total)\n`);

    // Agrupa por dimensão
    const dimensions = ["correctness", "security", "performance", "style"] as const;
    for (const dim of dimensions) {
      const dimFindings = result.findings.filter((f) => f.dimension === dim);
      if (dimFindings.length === 0) continue;

      lines.push(`### ${dim.charAt(0).toUpperCase() + dim.slice(1)}`);

      for (const finding of dimFindings.slice(0, 3)) {
        const severityEmoji = {
          critical: "🔴",
          error: "🟠",
          warning: "🟡",
          info: "ℹ️",
        };

        lines.push(`${severityEmoji[finding.severity]} **${finding.title}** (L${finding.line})`);
        lines.push(`> ${finding.description}`);
        if (finding.suggestion) {
          lines.push(`> **Suggestion:** ${finding.suggestion}`);
        }
        lines.push("");
      }

      if (dimFindings.length > 3) {
        lines.push(
          `... +${dimFindings.length - 3} more ${dim} issue(s) in full report\n`
        );
      }
    }

    lines.push("\n---");
    lines.push(
      `🤖 *Powered by Claude Opus Code Reviewer (${result.analysisTimeMs}ms)*`
    );

    if (result.suggestedAction === "request-changes") {
      lines.push(
        "\n**Action Required**: Please address critical findings before merging."
      );
    }

    return lines.join("\n");
  }

  /**
   * Gera relatório resumido (para logs/histórico)
   */
  generateReport(result: PRCodeReviewResult): string {
    return `
PR #${result.prNumber} - ${result.owner}/${result.repo}
Score: ${result.overallScore}/100
Suggested Action: ${result.suggestedAction}
Blocking Issues: ${result.blockingIssues}

Stats:
  Correctness: ${result.dimensionStats.correctness}
  Security: ${result.dimensionStats.security}
  Performance: ${result.dimensionStats.performance}
  Style: ${result.dimensionStats.style}

  Critical: ${result.severityStats.critical}
  Error: ${result.severityStats.error}
  Warning: ${result.severityStats.warning}
  Info: ${result.severityStats.info}

Analysis Time: ${result.analysisTimeMs}ms
`;
  }
}

// ============================================================================
// EXEMPLO: Integration com GitHub Actions
// ============================================================================

/**
 * Exemplo de uso em GitHub Actions workflow
 */
export async function handleGitHubPRWebhook(
  prPayload: GitHubPRPayload,
  diffData: PullRequestDiff,
  newAgentCode?: string
): Promise<void> {
  const integration = new PRCodeReviewerIntegration(process.env.ANTHROPIC_API_KEY);

  // Analisa PR
  const result = await integration.reviewPullRequest(
    prPayload,
    diffData,
    newAgentCode
  );

  // Log do relatório
  console.log(integration.generateReport(result));

  // Comentário em PR (exemplo - implementar com GitHub API)
  const comment = integration.generatePRComment(result);
  console.log("\nGitHub PR Comment:\n");
  console.log(comment);

  // Validações de saída
  if (result.blockingIssues > 0) {
    console.error(`\n❌ PR #${result.prNumber} has ${result.blockingIssues} blocking issues`);
    process.exit(1);
  }

  console.log(`\n✅ PR #${result.prNumber} passed code review`);
}

export default PRCodeReviewerIntegration;
