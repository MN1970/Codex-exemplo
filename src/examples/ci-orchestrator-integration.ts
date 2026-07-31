/**
 * CI/CD Orchestrator Integration Examples
 * Demonstrates how to use the CIOrchestratorService
 */

import {
  CIOrchestratorService,
  createCIOrchestratorService,
  WorkflowRunStatus,
  WorkflowConclusion,
} from "../services/ci-orchestrator";

/**
 * Exemplo 1: Dispara um workflow e aguarda conclusão
 */
async function example1_BasicWorkflowExecution() {
  console.log("\n=== Example 1: Basic Workflow Execution ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
    workflowId: "ci.yml",
    pollingIntervalMs: 30000, // 30 segundos
    maxWaitMs: 300000, // 5 minutos
  });

  try {
    console.log("Disparando workflow ci.yml na branch main...");

    const result = await orchestrator.executeWorkflow("ci.yml", "main");

    console.log("\nResultado da execução:");
    console.log(`  Status: ${result.status}`);
    console.log(`  Workflow Status: ${result.workflowStatus}`);
    console.log(`  Conclusão: ${result.conclusion}`);
    console.log(`  Duração total: ${result.duration}ms`);

    if (result.buildOutput.testResults) {
      const { passed, failed, skipped } = result.buildOutput.testResults;
      console.log(`\nTestes:`);
      console.log(`  Passou: ${passed}`);
      console.log(`  Falhou: ${failed}`);
      console.log(`  Pulados: ${skipped}`);
    }

    if (result.buildOutput.coverage) {
      const { lines, statements, functions, branches } =
        result.buildOutput.coverage;
      console.log(`\nCobertura:`);
      console.log(`  Linhas: ${lines}%`);
      console.log(`  Statements: ${statements}%`);
      console.log(`  Functions: ${functions}%`);
      console.log(`  Branches: ${branches}%`);
    }

    if (result.buildOutput.lintErrors && result.buildOutput.lintErrors.length > 0) {
      console.log(`\nErros de Lint (${result.buildOutput.lintErrors.length}):`);
      result.buildOutput.lintErrors.slice(0, 5).forEach((error) => {
        console.log(`  ${error.file}:${error.line}:${error.column} - ${error.message}`);
      });
    }
  } catch (error) {
    console.error("Erro ao executar workflow:", error);
  }
}

/**
 * Exemplo 2: Dispara workflow com inputs customizados
 */
async function example2_WorkflowWithInputs() {
  console.log("\n=== Example 2: Workflow with Custom Inputs ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
    workflowId: "deploy.yml",
  });

  try {
    console.log("Disparando workflow de deploy com inputs customizados...");

    const result = await orchestrator.executeWorkflow("deploy.yml", "main", {
      environment: "staging",
      debug: "true",
      skipTests: "false",
    });

    if (result.status === "success") {
      console.log("Deploy executado com sucesso!");
    } else {
      console.log("Deploy falhou!");
      console.log("Logs:", result.buildOutput.logs.slice(0, 10).join("\n"));
    }
  } catch (error) {
    console.error("Erro ao executar deploy:", error);
  }
}

/**
 * Exemplo 3: Dispara e monitora manualmente com polling personalizado
 */
async function example3_ManualMonitoring() {
  console.log("\n=== Example 3: Manual Workflow Triggering and Monitoring ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
    pollingIntervalMs: 10000, // 10 segundos para polls mais frequentes
    maxWaitMs: 600000, // 10 minutos
  });

  try {
    // Passo 1: Dispara o workflow
    console.log("Disparando workflow test.yml...");
    const runId = await orchestrator.triggerWorkflow("test.yml", "develop");
    console.log(`Workflow disparado com ID: ${runId}\n`);

    // Passo 2: Monitora a execução
    console.log("Monitorando execução...");
    const result = await orchestrator.monitorWorkflowRun(runId, "test.yml");

    console.log("\nExecução concluída!");
    console.log(`Status: ${result.status}`);

    // Analisa resultados
    if (result.buildOutput.testResults) {
      const passRate =
        result.buildOutput.testResults.passed /
        (result.buildOutput.testResults.passed +
          result.buildOutput.testResults.failed);

      console.log(
        `Taxa de aprovação de testes: ${(passRate * 100).toFixed(2)}%`
      );

      if (passRate < 0.8) {
        console.warn("Aviso: Taxa de aprovação abaixo de 80%!");
      }
    }
  } catch (error) {
    console.error("Erro durante monitoramento:", error);
  }
}

/**
 * Exemplo 4: Monitoramento com tratamento de timeout
 */
async function example4_TimeoutHandling() {
  console.log("\n=== Example 4: Timeout Handling ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
    pollingIntervalMs: 5000,
    maxWaitMs: 30000, // Timeout curto para demonstração (30s)
  });

  try {
    const result = await orchestrator.executeWorkflow("long-running.yml");

    if (result.workflowStatus === "timed_out") {
      console.log("Workflow excedeu o tempo máximo de espera!");
      console.log(`Configurado para aguardar máximo de ${orchestrator} ms`);

      // Pode reconfigurar e tentar novamente
      console.log(
        "Nota: Você pode verificar o workflow manualmente no GitHub Actions"
      );
    }
  } catch (error) {
    console.error("Erro:", error);
  }
}

/**
 * Exemplo 5: Monitoramento de métricas e estatísticas
 */
async function example5_MetricsTracking() {
  console.log("\n=== Example 5: Metrics and Statistics ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  // Simula múltiplas execuções (em um cenário real)
  try {
    for (let i = 0; i < 3; i++) {
      console.log(`\nExecutando workflow ${i + 1}/3...`);
      // await orchestrator.executeWorkflow("ci.yml");
      // (comentado para evitar chamadas reais)
    }

    // Obtém métricas
    const metrics = orchestrator.getMetrics();

    console.log("\nMétricas agregadas:");
    console.log(`  Total de workflows disparados: ${metrics.totalWorkflowsTriggered}`);
    console.log(`  Sucessos: ${metrics.successCount}`);
    console.log(`  Falhas: ${metrics.failureCount}`);
    console.log(`  Timeouts: ${metrics.timeoutCount}`);
    console.log(`  Duração média: ${metrics.averageDurationMs}ms`);
    console.log(
      `  Taxa média de aprovação de testes: ${(metrics.averageTestPassRate * 100).toFixed(2)}%`
    );
    console.log(`  Cobertura média:`);
    console.log(
      `    - Linhas: ${metrics.averageCoverage.lines.toFixed(2)}%`
    );
    console.log(
      `    - Statements: ${metrics.averageCoverage.statements.toFixed(2)}%`
    );
    console.log(
      `    - Functions: ${metrics.averageCoverage.functions.toFixed(2)}%`
    );
    console.log(
      `    - Branches: ${metrics.averageCoverage.branches.toFixed(2)}%`
    );

    // Reset métricas
    // orchestrator.resetMetrics();
  } catch (error) {
    console.error("Erro ao coletar métricas:", error);
  }
}

/**
 * Exemplo 6: Análise de resultados e decisões automatizadas
 */
async function example6_AutomatedDecisions() {
  console.log("\n=== Example 6: Automated Decision Making ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  try {
    const result = await orchestrator.executeWorkflow("ci.yml");

    // Análise 1: Qualidade geral
    const qualityMetrics = {
      testsPassed: result.buildOutput.testResults?.passed ?? 0,
      testsFailed: result.buildOutput.testResults?.failed ?? 0,
      lineCoverage: result.buildOutput.coverage?.lines ?? 0,
      lintErrorCount: result.buildOutput.lintErrors?.length ?? 0,
    };

    console.log("Análise de Qualidade:");
    console.log(`  ✓ Testes aprovados: ${qualityMetrics.testsPassed}`);
    console.log(`  ✗ Testes falhados: ${qualityMetrics.testsFailed}`);
    console.log(`  ≈ Cobertura de linhas: ${qualityMetrics.lineCoverage}%`);
    console.log(`  ⚠ Erros de lint: ${qualityMetrics.lintErrorCount}`);

    // Decisão 1: Pode fazer deploy?
    const canDeploy =
      qualityMetrics.testsFailed === 0 &&
      qualityMetrics.lineCoverage >= 80 &&
      qualityMetrics.lintErrorCount === 0;

    if (canDeploy) {
      console.log("\n✅ Pode fazer deploy em produção!");
      // Próximo passo: disparar workflow de deploy
      // await orchestrator.executeWorkflow("deploy-prod.yml");
    } else {
      console.log("\n❌ Não pode fazer deploy - critérios não atendidos");

      const issues: string[] = [];
      if (qualityMetrics.testsFailed > 0) {
        issues.push(`${qualityMetrics.testsFailed} testes falhados`);
      }
      if (qualityMetrics.lineCoverage < 80) {
        issues.push(
          `Cobertura insuficiente: ${qualityMetrics.lineCoverage}% (mínimo 80%)`
        );
      }
      if (qualityMetrics.lintErrorCount > 0) {
        issues.push(`${qualityMetrics.lintErrorCount} erros de lint`);
      }

      console.log("Problemas encontrados:");
      issues.forEach((issue) => console.log(`  • ${issue}`));
    }
  } catch (error) {
    console.error("Erro ao analisar resultados:", error);
  }
}

/**
 * Exemplo 7: Integração com notificações
 */
async function example7_WithNotifications() {
  console.log("\n=== Example 7: Integration with Notifications ===\n");

  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN || "ghp_xxx",
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  try {
    const result = await orchestrator.executeWorkflow("ci.yml");

    // Simula envio de notificações baseado no resultado
    const notification = {
      title:
        result.status === "success"
          ? "✅ CI Pipeline Passed"
          : "❌ CI Pipeline Failed",
      message: `Workflow ${result.workflowRunId} - ${result.workflowStatus}`,
      timestamp: result.timestamp,
      details: {
        testResults: result.buildOutput.testResults,
        coverage: result.buildOutput.coverage,
        lintErrors: result.buildOutput.lintErrors,
      },
    };

    console.log("Notificação que seria enviada:");
    console.log(JSON.stringify(notification, null, 2));

    // Em integração real, enviaria para Slack, email, etc
    // await notificationService.send(notification);
  } catch (error) {
    console.error("Erro ao processar notificações:", error);
  }
}

/**
 * Executor de exemplos
 */
export async function runCIOrchestratorExamples() {
  console.log("╔════════════════════════════════════════════════════════════╗");
  console.log("║   CI/CD Orchestrator Service - Integration Examples        ║");
  console.log("╚════════════════════════════════════════════════════════════╝");

  try {
    // Descomente para executar exemplos reais (requer GITHUB_TOKEN válido)
    // await example1_BasicWorkflowExecution();
    // await example2_WorkflowWithInputs();
    // await example3_ManualMonitoring();
    // await example4_TimeoutHandling();
    await example5_MetricsTracking();
    // await example6_AutomatedDecisions();
    // await example7_WithNotifications();

    console.log("\n╔════════════════════════════════════════════════════════════╗");
    console.log("║   Exemplos executados com sucesso!                        ║");
    console.log("╚════════════════════════════════════════════════════════════╝\n");
  } catch (error) {
    console.error("Erro ao executar exemplos:", error);
  }
}

// Executa se rodado diretamente
if (require.main === module) {
  runCIOrchestratorExamples().catch(console.error);
}
