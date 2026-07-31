/**
 * Exemplos de uso do Auto-Merge Controller
 *
 * Este arquivo demonstra diferentes cenários de uso do auto-merge controller,
 * incluindo casos de sucesso, bloqueio e tratamento de erros.
 */

import {
  AutoMergeController,
  createAutoMergeController,
  MergeStatus,
  BlockReason,
  type AutoMergeConfig,
  type MergeResult,
} from "../auto-merge";

/**
 * Exemplo 1: Merge automático básico
 *
 * Executa merge simples de um PR com configuração mínima.
 */
export async function example1BasicAutoMerge() {
  console.log("\n=== Exemplo 1: Merge Automático Básico ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
  });

  // Simula resultado bem-sucedido
  const result: MergeResult = {
    success: true,
    prNumber: 42,
    owner: "my-org",
    repo: "my-repo",
    status: MergeStatus.MERGED,
    sha: "abc123def456",
    mergeCommitSha: "def456abc123",
    branchDeleted: true,
    auditEvents: [
      {
        timestamp: new Date(),
        action: "AUTO_MERGE_STARTED",
        status: MergeStatus.PENDING,
        prNumber: 42,
        owner: "my-org",
        repo: "my-repo",
      },
      {
        timestamp: new Date(),
        action: "MERGE_COMPLETED",
        status: MergeStatus.MERGED,
        prNumber: 42,
        owner: "my-org",
        repo: "my-repo",
      },
    ],
    timestamp: new Date(),
    duration: 2500,
  };

  console.log(`✅ PR #${result.prNumber} merged successfully!`);
  console.log(`   Status: ${result.status}`);
  console.log(`   Merge Commit: ${result.mergeCommitSha}`);
  console.log(`   Branch Deleted: ${result.branchDeleted}`);
  console.log(`   Duration: ${result.duration}ms`);
  console.log(`\n   Audit Events:`);
  result.auditEvents.forEach((event) => {
    console.log(`   - [${event.action}] ${event.status}`);
  });

  return result;
}

/**
 * Exemplo 2: Merge bloqueado por CI não passou
 *
 * Demonstra como o controller bloqueia merge quando CI falha.
 */
export async function example2BlockedByCI() {
  console.log("\n=== Exemplo 2: Merge Bloqueado (CI Falhou) ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
    requireCIPassed: true,
    requiredApprovals: 1,
  });

  // Simula resultado bloqueado por CI
  const result: MergeResult = {
    success: false,
    prNumber: 43,
    owner: "my-org",
    repo: "my-repo",
    status: MergeStatus.BLOCKED,
    blockedBy: [BlockReason.CI_FAILED],
    prerequisitesCheck: {
      passed: false,
      checks: {
        ciPassed: false,
        approvalsOk: true,
        noConflicts: true,
        notDraft: true,
        branchProtectionOk: true,
      },
      blockedBy: [BlockReason.CI_FAILED],
      details: "CI pipeline has not passed",
    },
    auditEvents: [
      {
        timestamp: new Date(),
        action: "AUTO_MERGE_STARTED",
        status: MergeStatus.PENDING,
        prNumber: 43,
        owner: "my-org",
        repo: "my-repo",
      },
      {
        timestamp: new Date(),
        action: "PREREQUISITES_CHECK_FAILED",
        status: MergeStatus.BLOCKED,
        prNumber: 43,
        owner: "my-org",
        repo: "my-repo",
        details: {
          blockedBy: [BlockReason.CI_FAILED],
          details: "CI pipeline has not passed",
        },
      },
    ],
    timestamp: new Date(),
    duration: 850,
  };

  console.log(`⚠️ PR #${result.prNumber} is BLOCKED\n`);
  console.log(`   Blocked by: ${result.blockedBy?.join(", ")}`);
  console.log(`   Details: ${result.prerequisitesCheck?.details}`);
  console.log(`\n   Checks:`);
  const checks = result.prerequisitesCheck?.checks;
  if (checks) {
    console.log(`   - CI Passed: ${checks.ciPassed ? "✅" : "❌"}`);
    console.log(`   - Approvals OK: ${checks.approvalsOk ? "✅" : "❌"}`);
    console.log(`   - No Conflicts: ${checks.noConflicts ? "✅" : "❌"}`);
    console.log(`   - Not Draft: ${checks.notDraft ? "✅" : "❌"}`);
  }

  return result;
}

/**
 * Exemplo 3: Merge bloqueado por falta de approvals
 *
 * Demonstra como o controller bloqueia quando approvals são insuficientes.
 */
export async function example3BlockedByApprovals() {
  console.log("\n=== Exemplo 3: Merge Bloqueado (Approvals Insuficientes) ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
    requiredApprovals: 3, // Exige 3 approvals
  });

  // Simula resultado bloqueado por falta de approvals
  const result: MergeResult = {
    success: false,
    prNumber: 44,
    owner: "my-org",
    repo: "my-repo",
    status: MergeStatus.BLOCKED,
    blockedBy: [BlockReason.MISSING_APPROVALS],
    prerequisitesCheck: {
      passed: false,
      checks: {
        ciPassed: true,
        approvalsOk: false,
        noConflicts: true,
        notDraft: true,
        branchProtectionOk: true,
      },
      blockedBy: [BlockReason.MISSING_APPROVALS],
      details: "Missing approvals (current: 1/3)",
    },
    auditEvents: [
      {
        timestamp: new Date(),
        action: "PREREQUISITES_CHECK_FAILED",
        status: MergeStatus.BLOCKED,
        prNumber: 44,
        owner: "my-org",
        repo: "my-repo",
      },
    ],
    timestamp: new Date(),
    duration: 600,
  };

  console.log(`⚠️ PR #${result.prNumber} is BLOCKED\n`);
  console.log(`   Blocked by: ${result.blockedBy?.join(", ")}`);
  console.log(`   Details: ${result.prerequisitesCheck?.details}`);
  console.log(`\n   Status:`);
  console.log(`   - Current approvals: 1`);
  console.log(`   - Required approvals: 3`);
  console.log(`   - Missing: 2 more approvals`);

  return result;
}

/**
 * Exemplo 4: Merge com conflitos
 *
 * Demonstra como o controller detecta conflitos de merge.
 */
export async function example4MergeConflicts() {
  console.log("\n=== Exemplo 4: Merge com Conflitos ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
    allowMergingWithConflicts: false,
  });

  // Simula resultado bloqueado por conflitos
  const result: MergeResult = {
    success: false,
    prNumber: 45,
    owner: "my-org",
    repo: "my-repo",
    status: MergeStatus.BLOCKED,
    blockedBy: [BlockReason.MERGE_CONFLICTS],
    prerequisitesCheck: {
      passed: false,
      checks: {
        ciPassed: true,
        approvalsOk: true,
        noConflicts: false,
        notDraft: true,
        branchProtectionOk: true,
      },
      blockedBy: [BlockReason.MERGE_CONFLICTS],
      details: "PR has merge conflicts",
    },
    auditEvents: [],
    timestamp: new Date(),
    duration: 400,
  };

  console.log(`⚠️ PR #${result.prNumber} has MERGE CONFLICTS\n`);
  console.log(`   Blocked by: ${result.blockedBy?.join(", ")}`);
  console.log(`   Details: ${result.prerequisitesCheck?.details}`);
  console.log(`\n   Action Required:`);
  console.log(`   1. Resolve conflicts locally`);
  console.log(`   2. Push changes to feature branch`);
  console.log(`   3. Retry merge`);

  return result;
}

/**
 * Exemplo 5: Merge com squash strategy
 *
 * Demonstra merge usando squash strategy com mensagem customizada.
 */
export async function example5SquashMerge() {
  console.log("\n=== Exemplo 5: Squash Merge com Mensagem Customizada ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
    mergeMethod: "squash",
    commitMessage: "feat: Add new authentication system",
    commitDescription: "- Implement OAuth2 integration\n- Add JWT token support\n- Update login flow",
    deleteBranchAfterMerge: true,
  });

  const result: MergeResult = {
    success: true,
    prNumber: 46,
    owner: "my-org",
    repo: "my-repo",
    status: MergeStatus.MERGED,
    sha: "feature/oauth2",
    mergeCommitSha: "abc789def012",
    branchDeleted: true,
    auditEvents: [
      {
        timestamp: new Date(),
        action: "MERGE_COMPLETED",
        status: MergeStatus.MERGED,
        prNumber: 46,
        owner: "my-org",
        repo: "my-repo",
        details: {
          mergeCommitSha: "abc789def012",
          mergeMethod: "squash",
        },
      },
    ],
    timestamp: new Date(),
    duration: 2100,
  };

  console.log(`✅ PR #${result.prNumber} merged with SQUASH strategy\n`);
  console.log(`   Strategy: ${controller.getAuditLog().length === 0 ? "squash" : "merge"}`);
  console.log(`   Commit Message: feat: Add new authentication system`);
  console.log(`   Merge Commit: ${result.mergeCommitSha}`);
  console.log(`   Branch Deleted: ${result.branchDeleted}`);

  return result;
}

/**
 * Exemplo 6: Processamento em batch com audit trail
 *
 * Demonstra como processar múltiplas PRs com audit trail completo.
 */
export async function example6BatchProcessing() {
  console.log("\n=== Exemplo 6: Processamento em Batch ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
    auditTableUrl: "https://xxx.supabase.co/rest/v1/auto_merge_audit",
    auditApiKey: "sbp_example",
  });

  const prNumbers = [50, 51, 52];
  const results: MergeResult[] = [];

  for (const prNumber of prNumbers) {
    console.log(`\nProcessing PR #${prNumber}...`);

    // Simula diferentes resultados
    const mockResult: MergeResult = {
      success: prNumber % 2 === 0, // Alterna entre sucesso e bloqueio
      prNumber,
      owner: "my-org",
      repo: "my-repo",
      status: prNumber % 2 === 0 ? MergeStatus.MERGED : MergeStatus.BLOCKED,
      blockedBy: prNumber % 2 === 0 ? undefined : [BlockReason.CI_FAILED],
      auditEvents: [
        {
          timestamp: new Date(),
          action: prNumber % 2 === 0 ? "MERGE_COMPLETED" : "PREREQUISITES_CHECK_FAILED",
          status: prNumber % 2 === 0 ? MergeStatus.MERGED : MergeStatus.BLOCKED,
          prNumber,
          owner: "my-org",
          repo: "my-repo",
        },
      ],
      timestamp: new Date(),
      duration: Math.random() * 3000,
    };

    results.push(mockResult);

    const status = mockResult.success ? "✅ MERGED" : "⚠️ BLOCKED";
    console.log(`   ${status} - Duration: ${mockResult.duration?.toFixed(0)}ms`);
  }

  // Resumo
  console.log("\n=== Resumo do Processamento em Batch ===\n");
  const successful = results.filter((r) => r.success).length;
  const blocked = results.filter((r) => !r.success).length;

  console.log(`Total PRs: ${results.length}`);
  console.log(`✅ Merged: ${successful}`);
  console.log(`⚠️ Blocked: ${blocked}`);
  console.log(`Success Rate: ${((successful / results.length) * 100).toFixed(1)}%`);

  return results;
}

/**
 * Exemplo 7: Configuração com notificações Slack
 *
 * Demonstra como configurar notificações de bloqueio via Slack.
 */
export async function example7SlackNotifications() {
  console.log("\n=== Exemplo 7: Notificações via Slack ===\n");

  const controller = createAutoMergeController({
    githubToken: process.env.GITHUB_TOKEN || "ghp_example",
    owner: "my-org",
    repo: "my-repo",
    notifyOnBlock: true,
    slackWebhook: process.env.SLACK_WEBHOOK_URL || "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  });

  // Simula PR bloqueado
  const result: MergeResult = {
    success: false,
    prNumber: 53,
    owner: "my-org",
    repo: "my-repo",
    status: MergeStatus.BLOCKED,
    blockedBy: [BlockReason.CI_FAILED, BlockReason.MISSING_APPROVALS],
    prerequisitesCheck: {
      passed: false,
      checks: {
        ciPassed: false,
        approvalsOk: false,
        noConflicts: true,
        notDraft: true,
        branchProtectionOk: true,
      },
      blockedBy: [BlockReason.CI_FAILED, BlockReason.MISSING_APPROVALS],
      details: "CI failed, missing approvals (1/2)",
    },
    auditEvents: [],
    timestamp: new Date(),
    duration: 600,
  };

  console.log(`📢 Slack Notification Sent\n`);
  console.log(`   Channel: #dev-alerts`);
  console.log(`   Message:`);
  console.log(`   ⚠️ Auto-Merge Blocked — PR #${result.prNumber}`);
  console.log(`   Blocked by: ${result.blockedBy?.join(", ")}`);
  console.log(`   Details: ${result.prerequisitesCheck?.details}`);
  console.log(`   Link: https://github.com/${result.owner}/${result.repo}/pull/${result.prNumber}`);

  return result;
}

/**
 * Exemplo 8: Comparação de estratégias de merge
 *
 * Demonstra diferentes configurações e estratégias de merge.
 */
export async function example8MergeStrategies() {
  console.log("\n=== Exemplo 8: Comparação de Estratégias de Merge ===\n");

  const strategies: Array<{
    name: string;
    method: "merge" | "squash" | "rebase";
    description: string;
  }> = [
    {
      name: "Merge Commit",
      method: "merge",
      description: "Preserva histórico completo de commits",
    },
    {
      name: "Squash & Merge",
      method: "squash",
      description: "Combina todos os commits em um",
    },
    {
      name: "Rebase & Merge",
      method: "rebase",
      description: "Reaplica commits na base (linha reta)",
    },
  ];

  console.log("Comparação de Estratégias:\n");
  strategies.forEach((strategy, index) => {
    console.log(`${index + 1}. ${strategy.name}`);
    console.log(`   Método: ${strategy.method}`);
    console.log(`   Descrição: ${strategy.description}`);

    if (strategy.method === "merge") {
      console.log(`   Histórico: Mantém todos os commits`);
      console.log(`   Bom para: Features complexas com múltiplos commits`);
    } else if (strategy.method === "squash") {
      console.log(`   Histórico: Compacto (1 commit)`);
      console.log(`   Bom para: Features simples, PRs pequenas`);
    } else {
      console.log(`   Histórico: Linear, sem merge commits`);
      console.log(`   Bom para: Repos com histórico limpo`);
    }
    console.log();
  });

  return strategies;
}

/**
 * Executa todos os exemplos
 */
export async function runAllExamples() {
  console.log("\n╔═══════════════════════════════════════════════════════════╗");
  console.log("║    Auto-Merge Controller — Exemplos de Uso               ║");
  console.log("╚═══════════════════════════════════════════════════════════╝");

  try {
    await example1BasicAutoMerge();
    await example2BlockedByCI();
    await example3BlockedByApprovals();
    await example4MergeConflicts();
    await example5SquashMerge();
    await example6BatchProcessing();
    await example7SlackNotifications();
    await example8MergeStrategies();

    console.log("\n╔═══════════════════════════════════════════════════════════╗");
    console.log("║    ✅ Todos os exemplos completados com sucesso!       ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");
  } catch (error) {
    console.error("❌ Erro ao executar exemplos:", error);
  }
}

// Execute se for rodado diretamente
if (require.main === module) {
  runAllExamples();
}
