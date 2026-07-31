/**
 * Exemplo de integração com FeedbackEngine
 *
 * Demonstra:
 * - Como processar output de CI
 * - Como gerar sugestões de correção
 * - Como postar comentários na PR
 * - Como rastrear tentativas e tempo
 */

import {
  createFeedbackEngine,
  ErrorType,
  ErrorSeverity,
  type CIOutput,
} from "../src/services/feedback-engine";

/**
 * Exemplo 1: Processar output de testes falhados
 */
async function example1_ProcessTestFailures() {
  console.log("\n=== Exemplo 1: Processar testes falhados ===\n");

  const engine = createFeedbackEngine({
    githubToken: process.env.GITHUB_TOKEN || "",
    owner: "manta-associados",
    repo: "codex-hub-mcp",
    anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  });

  const ciOutput: CIOutput = {
    workflowId: "workflow_run_123456",
    workflowName: "Jest Tests",
    prNumber: 123,
    branch: "feature/new-feedback-engine",
    commit: "abc123def456",
    timestamp: new Date(),
    duration: 45000, // 45 segundos
    status: "failure",
    errors: [
      {
        type: ErrorType.TEST_FAILURE,
        severity: ErrorSeverity.ERROR,
        message:
          "expect(result).toEqual({ success: true }) received false",
        file: "src/services/feedback-engine.test.ts",
        line: 142,
        context: `it("should generate suggestions", () => {
  const result = engine.generateSuggestions(mockOutput);
  expect(result).toEqual({ success: true });
});`,
      },
      {
        type: ErrorType.TEST_FAILURE,
        severity: ErrorSeverity.ERROR,
        message: "Timeout - async operation did not complete within 5000ms",
        file: "src/services/feedback-engine.test.ts",
        line: 200,
      },
    ],
    logs: [
      "FAIL src/services/feedback-engine.test.ts",
      "● should generate suggestions",
      "expect(result).toEqual({ success: true })",
      "Received: false",
    ],
    testResults: {
      total: 42,
      passed: 40,
      failed: 2,
      skipped: 0,
      duration: 45000,
      failedTests: [
        "should generate suggestions",
        "should handle timeout gracefully",
      ],
    },
  };

  try {
    const tracking = await engine.processCIOutput(ciOutput);

    console.log(`✅ Feedback processado com sucesso!`);
    console.log(`   ID: ${tracking.feedbackId}`);
    console.log(`   Status: ${tracking.status}`);
    console.log(`   Sugestões geradas: ${tracking.suggestionsGenerated}`);
    console.log(`   Comentários postados: ${tracking.commentsPosted}`);
    console.log(`   Tempo total: ${tracking.totalTimeSpent}ms`);
    console.log(`   Tentativas: ${tracking.totalAttempts}`);

    const stats = engine.getStatistics();
    console.log(`\n📊 Estatísticas gerais:`);
    console.log(`   Total de feedbacks: ${stats.totalFeedbacks}`);
    console.log(`   Taxa de sucesso: ${(stats.successRate * 100).toFixed(1)}%`);
    console.log(`   Tempo médio: ${stats.avgTimeSpentMs.toFixed(0)}ms`);
    console.log(
      `   Sugestões totais: ${stats.totalSuggestionsGenerated}`
    );
    console.log(
      `   Comentários totais: ${stats.totalCommentsPosted}`
    );
  } catch (error) {
    console.error("❌ Erro ao processar feedback:", error);
  }
}

/**
 * Exemplo 2: Processar erros de lint
 */
async function example2_ProcessLintErrors() {
  console.log("\n=== Exemplo 2: Processar erros de lint ===\n");

  const engine = createFeedbackEngine({
    githubToken: process.env.GITHUB_TOKEN || "",
    owner: "manta-associados",
    repo: "codex-hub-mcp",
    anthropicApiKey: process.env.ANTHROPIC_API_KEY,
    includeCodeExamples: true,
    autoReplyEnabled: true,
  });

  const ciOutput: CIOutput = {
    workflowId: "workflow_run_789012",
    workflowName: "ESLint",
    prNumber: 124,
    branch: "feature/lint-cleanup",
    commit: "def456ghi789",
    timestamp: new Date(),
    duration: 30000,
    status: "failure",
    errors: [
      {
        type: ErrorType.LINT_ERROR,
        severity: ErrorSeverity.WARNING,
        message: "'unusedVariable' is declared but never used",
        file: "src/utils/helpers.ts",
        line: 15,
        context: `export function formatDate(date: Date): string {
  const unusedVariable = 42;
  return date.toISOString();
}`,
      },
      {
        type: ErrorType.LINT_ERROR,
        severity: ErrorSeverity.ERROR,
        message: "Missing JSDoc comment",
        file: "src/services/new-service.ts",
        line: 1,
      },
    ],
    logs: ["ESLint found 2 issues"],
  };

  try {
    const tracking = await engine.processCIOutput(ciOutput);

    console.log(`✅ Lint feedback processado!`);
    console.log(`   Status: ${tracking.status}`);
    console.log(`   Sugestões: ${tracking.suggestionsGenerated}`);
  } catch (error) {
    console.error("❌ Erro:", error);
  }
}

/**
 * Exemplo 3: Processar problemas de coverage
 */
async function example3_ProcessCoverageIssues() {
  console.log("\n=== Exemplo 3: Processar problemas de coverage ===\n");

  const engine = createFeedbackEngine({
    githubToken: process.env.GITHUB_TOKEN || "",
    owner: "manta-associados",
    repo: "codex-hub-mcp",
    model: "claude-3-5-haiku-20241022", // Haiku for faster processing
  });

  const ciOutput: CIOutput = {
    workflowId: "workflow_run_345678",
    workflowName: "Coverage Check",
    prNumber: 125,
    branch: "feature/new-api",
    commit: "ghi789jkl012",
    timestamp: new Date(),
    duration: 60000,
    status: "failure",
    errors: [
      {
        type: ErrorType.COVERAGE_BELOW_THRESHOLD,
        severity: ErrorSeverity.WARNING,
        message: "Coverage dropped from 85% to 72%",
      },
    ],
    logs: [
      "Coverage threshold check failed",
      "Current coverage: 72%",
      "Required: 80%",
    ],
    coverage: {
      lines: 72,
      statements: 74,
      functions: 68,
      branches: 65,
      linesCovered: 288,
      linesTotal: 400,
      threshold: 80,
    },
  };

  try {
    const tracking = await engine.processCIOutput(ciOutput);

    console.log(`✅ Coverage feedback processado!`);
    console.log(`   Sugestões: ${tracking.suggestionsGenerated}`);
    console.log(`   PR: #${tracking.prNumber}`);

    // Recupera histórico
    const history = engine.getFeedbackHistory(tracking.feedbackId);
    if (history.length > 0) {
      const item = history[0];
      console.log(`\n📋 Detalhes:`);
      console.log(`   Criado em: ${item.createdAt}`);
      console.log(`   Última tentativa: ${item.lastAttemptAt}`);
      console.log(`   Total de tempo: ${item.totalTimeSpent}ms`);
      console.log(`   Tentativas: ${item.attempts.length}`);

      item.attempts.forEach((attempt) => {
        console.log(
          `     - Tentativa ${attempt.attemptNumber}: ${attempt.status} (${attempt.duration}ms)`
        );
      });
    }
  } catch (error) {
    console.error("❌ Erro:", error);
  }
}

/**
 * Exemplo 4: Processar tipo de erro com sucesso (sem erros)
 */
async function example4_ProcessSuccessfulBuild() {
  console.log("\n=== Exemplo 4: Build bem-sucedido (skip) ===\n");

  const engine = createFeedbackEngine({
    githubToken: process.env.GITHUB_TOKEN || "",
    owner: "manta-associados",
    repo: "codex-hub-mcp",
  });

  const ciOutput: CIOutput = {
    workflowId: "workflow_run_901234",
    workflowName: "Full CI Suite",
    prNumber: 126,
    branch: "main",
    commit: "jkl012mno345",
    timestamp: new Date(),
    duration: 120000,
    status: "success",
    errors: [], // Sem erros!
    logs: ["All checks passed"],
    testResults: {
      total: 150,
      passed: 150,
      failed: 0,
      skipped: 0,
      duration: 45000,
    },
    coverage: {
      lines: 92,
      statements: 93,
      functions: 91,
      branches: 89,
      threshold: 80,
    },
  };

  try {
    const tracking = await engine.processCIOutput(ciOutput);

    console.log(`✅ Build bem-sucedido!`);
    console.log(`   Status: ${tracking.status}`);
    console.log(`   Sugestões geradas: ${tracking.suggestionsGenerated}`);
    console.log(`   (Nenhum feedback necessário)`);
  } catch (error) {
    console.error("❌ Erro:", error);
  }
}

/**
 * Exemplo 5: Demonstração de retry logic
 */
async function example5_RetryLogic() {
  console.log("\n=== Exemplo 5: Demonstração de Retry Logic ===\n");

  const engine = createFeedbackEngine({
    githubToken: process.env.GITHUB_TOKEN || "",
    owner: "manta-associados",
    repo: "codex-hub-mcp",
    retryPolicy: {
      maxAttempts: 3,
      initialDelayMs: 500,
      maxDelayMs: 5000,
      backoffFactor: 2,
    },
  });

  console.log(`🔄 Configuração de retry:`);
  console.log(`   Max tentativas: 3`);
  console.log(`   Delay inicial: 500ms`);
  console.log(`   Delay máximo: 5000ms`);
  console.log(`   Backoff factor: 2x`);
  console.log(`\n   Sequência de delays:`);
  console.log(`   - Tentativa 1: 0ms`);
  console.log(`   - Tentativa 2: 500ms (1x)`);
  console.log(`   - Tentativa 3: 1000ms (2x)`);
  console.log(`   - Tentativa 4: 2000ms (2x) [máx 3]`);

  const ciOutput: CIOutput = {
    workflowId: "workflow_retry_test",
    workflowName: "Retry Test",
    prNumber: 127,
    branch: "feature/retry-test",
    commit: "mno345pqr678",
    timestamp: new Date(),
    duration: 15000,
    status: "failure",
    errors: [
      {
        type: ErrorType.BUILD_FAILURE,
        severity: ErrorSeverity.CRITICAL,
        message: "Network timeout during build",
      },
    ],
    logs: ["Build failed due to network issue"],
  };

  console.log(`\n⏱️  Processando com retry automático...`);
  console.log(`   (Com mock, demonstra a estrutura de retry)`);
}

/**
 * Exemplo 6: Rastreamento completo
 */
async function example6_CompletTracking() {
  console.log("\n=== Exemplo 6: Rastreamento Completo ===\n");

  const engine = createFeedbackEngine({
    githubToken: process.env.GITHUB_TOKEN || "",
    owner: "manta-associados",
    repo: "codex-hub-mcp",
  });

  // Simula múltiplos feedbacks
  const outputs: CIOutput[] = [
    {
      workflowId: "w1",
      workflowName: "Tests",
      prNumber: 101,
      branch: "feature/a",
      commit: "a1",
      timestamp: new Date(),
      duration: 5000,
      status: "failure",
      errors: [
        {
          type: ErrorType.TEST_FAILURE,
          severity: ErrorSeverity.ERROR,
          message: "Test 1 failed",
        },
      ],
      logs: [],
    },
    {
      workflowId: "w2",
      workflowName: "Lint",
      prNumber: 102,
      branch: "feature/b",
      commit: "b1",
      timestamp: new Date(),
      duration: 3000,
      status: "failure",
      errors: [
        {
          type: ErrorType.LINT_ERROR,
          severity: ErrorSeverity.WARNING,
          message: "Lint error detected",
        },
      ],
      logs: [],
    },
    {
      workflowId: "w3",
      workflowName: "Build",
      prNumber: 103,
      branch: "feature/c",
      commit: "c1",
      timestamp: new Date(),
      duration: 8000,
      status: "success",
      errors: [],
      logs: [],
    },
  ];

  console.log(`📊 Rastreando ${outputs.length} feedbacks...`);

  for (const output of outputs) {
    try {
      const tracking = await engine.processCIOutput(output);
      console.log(
        `   - PR #${tracking.prNumber}: ${tracking.status} (${tracking.totalTimeSpent}ms)`
      );
    } catch (error) {
      console.log(
        `   - PR #${output.prNumber}: Erro durante processamento`
      );
    }
  }

  // Exibe estatísticas finais
  const stats = engine.getStatistics();
  console.log(`\n📈 Estatísticas Finais:`);
  console.log(`   Total processados: ${stats.totalFeedbacks}`);
  console.log(`   Taxa de sucesso: ${(stats.successRate * 100).toFixed(1)}%`);
  console.log(`   Tempo médio: ${stats.avgTimeSpentMs.toFixed(0)}ms`);
  console.log(`   Sugestões geradas: ${stats.totalSuggestionsGenerated}`);
  console.log(`   Comentários postados: ${stats.totalCommentsPosted}`);
}

/**
 * Executa todos os exemplos
 */
async function runAllExamples() {
  try {
    await example1_ProcessTestFailures();
    await example2_ProcessLintErrors();
    await example3_ProcessCoverageIssues();
    await example4_ProcessSuccessfulBuild();
    await example5_RetryLogic();
    await example6_CompletTracking();

    console.log("\n✅ Todos os exemplos completados!");
  } catch (error) {
    console.error("❌ Erro ao executar exemplos:", error);
  }
}

// Executa se for chamado diretamente
if (require.main === module) {
  runAllExamples();
}

export {
  example1_ProcessTestFailures,
  example2_ProcessLintErrors,
  example3_ProcessCoverageIssues,
  example4_ProcessSuccessfulBuild,
  example5_RetryLogic,
  example6_CompletTracking,
};
