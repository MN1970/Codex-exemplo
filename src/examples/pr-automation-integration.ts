/**
 * PR Automation Engine — Exemplos de integração
 *
 * Este arquivo demonstra como usar o PRAutomationEngine em diferentes cenários.
 *
 * Requisitos:
 * - GITHUB_TOKEN configurado
 * - ANTHROPIC_API_KEY configurado (opcional, para sugestões com Claude)
 * - SUPABASE_URL e SUPABASE_ANON_KEY (opcional, para persistência)
 */

import {
  PRAutomationEngine,
  createPRAutomationEngine,
  PRAnalysisStatus,
} from "../services/pr-automation";

/**
 * Exemplo 1: Análise básica de um PR
 * Analisa um PR específico e exibe os resultados
 */
export async function example1_BasicPRAnalysis(): Promise<void> {
  console.log("\n=== Exemplo 1: Análise básica de PR ===\n");

  const engine = createPRAutomationEngine({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-example",
    autoTriggerCI: false, // Não dispara CI neste exemplo
  });

  try {
    const analysis = await engine.analyzePR(42, "manta-associados", "codex-example");

    console.log(`📊 PR #${analysis.prNumber}: ${analysis.title}`);
    console.log(`👤 Autor: ${analysis.author}`);
    console.log(`🔄 Branch: ${analysis.branch} -> ${analysis.baseBranch}`);
    console.log(`📝 Status: ${analysis.status}`);
    console.log(`⏱️  Duração: ${analysis.duration}ms`);

    console.log("\n📈 Estatísticas:");
    console.log(`  - Arquivos alterados: ${analysis.filesChanged}`);
    console.log(`  - Linhas adicionadas: ${analysis.additions}`);
    console.log(`  - Linhas removidas: ${analysis.deletions}`);

    if (analysis.commitIntent) {
      console.log("\n💭 Intent do commit:");
      console.log(`  - Ação: ${analysis.commitIntent.action}`);
      console.log(`  - Target: ${analysis.commitIntent.target}`);
      console.log(`  - Confiança: ${(analysis.commitIntent.confidence * 100).toFixed(0)}%`);
    }

    if (analysis.codePatterns.length > 0) {
      console.log(`\n⚠️  Padrões detectados (${analysis.codePatterns.length}):`);
      analysis.codePatterns.forEach((pattern) => {
        console.log(`  - ${pattern.type}: ${pattern.description}`);
      });
    }

    if (analysis.suggestions.length > 0) {
      console.log(`\n💡 Sugestões (${analysis.suggestions.length}):`);
      analysis.suggestions.forEach((suggestion) => {
        console.log(`  - [${suggestion.severity}] ${suggestion.title}`);
        console.log(`    → ${suggestion.recommendation}`);
      });
    }
  } catch (error) {
    console.error("❌ Erro na análise:", error);
  }
}

/**
 * Exemplo 2: Análise com CI/CD automático
 * Analisa PR e dispara CI, monitora o build
 */
export async function example2_PRAnalysisWithCI(): Promise<void> {
  console.log("\n=== Exemplo 2: Análise com CI/CD automático ===\n");

  const engine = createPRAutomationEngine({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-example",
    workflowId: "test.yml",
    autoTriggerCI: true,
    ciPollingInterval: 30000, // 30 segundos
    maxCIWait: 600000, // 10 minutos
  });

  try {
    const analysis = await engine.analyzePR(42);

    console.log(`📊 PR #${analysis.prNumber}: ${analysis.title}`);
    console.log(`📊 Status: ${analysis.status}`);

    if (analysis.ciTriggered && analysis.buildStatus) {
      console.log("\n✅ CI/CD disparado:");
      console.log(`  - Workflow ID: ${analysis.buildStatus.workflowRunId}`);
      console.log(`  - Status: ${analysis.buildStatus.status}`);
      console.log(`  - Resultado: ${analysis.buildStatus.passed ? "✅ PASSOU" : "❌ FALHOU"}`);

      if (analysis.buildStatus.testsPassed !== undefined) {
        console.log(`  - Testes: ${analysis.buildStatus.testsPassed} passou, ${analysis.buildStatus.testsFailed} falhou`);
      }

      if (analysis.buildStatus.coverage !== undefined) {
        console.log(`  - Cobertura: ${analysis.buildStatus.coverage}%`);
      }

      console.log(`  - Duração: ${analysis.buildStatus.duration}ms`);
    }

    // Exibe métricas de CI
    const ciMetrics = engine.getCIMetrics();
    console.log("\n📊 Métricas de CI/CD:");
    console.log(`  - Total de workflows: ${ciMetrics.totalWorkflowsTriggered}`);
    console.log(`  - Sucesso: ${ciMetrics.successCount}`);
    console.log(`  - Falhas: ${ciMetrics.failureCount}`);
    console.log(`  - Duração média: ${ciMetrics.averageDurationMs}ms`);
    console.log(`  - Taxa de sucesso em testes: ${(ciMetrics.averageTestPassRate * 100).toFixed(1)}%`);
  } catch (error) {
    console.error("❌ Erro na análise com CI:", error);
  }
}

/**
 * Exemplo 3: Análise em batch de múltiplos PRs
 * Analisa vários PRs em sequência
 */
export async function example3_BatchPRAnalysis(): Promise<void> {
  console.log("\n=== Exemplo 3: Análise em batch de múltiplos PRs ===\n");

  const engine = createPRAutomationEngine({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-example",
    autoTriggerCI: false,
  });

  const prNumbers = [40, 41, 42, 43, 44];
  const results = [];

  for (const prNumber of prNumbers) {
    try {
      console.log(`\nAnalisando PR #${prNumber}...`);
      const analysis = await engine.analyzePR(prNumber);

      results.push({
        prNumber: analysis.prNumber,
        title: analysis.title,
        status: analysis.status,
        suggestions: analysis.suggestions.length,
        patterns: analysis.codePatterns.length,
        duration: analysis.duration,
      });

      console.log(`✅ PR #${prNumber} analisado em ${analysis.duration}ms`);
    } catch (error) {
      console.log(`❌ Erro ao analisar PR #${prNumber}`);
    }
  }

  console.log("\n📊 Resumo da análise em batch:");
  console.log("PR #  | Título                    | Status      | Sugestões | Padrões");
  console.log("------|---------------------------|-------------|-----------|--------");
  results.forEach((result) => {
    const title = result.title.substring(0, 25).padEnd(25);
    const status = result.status.padEnd(11);
    const suggestions = String(result.suggestions).padStart(9);
    const patterns = String(result.patterns).padStart(7);
    console.log(`${result.prNumber}   | ${title} | ${status} | ${suggestions} | ${patterns}`);
  });
}

/**
 * Exemplo 4: Monitoramento contínuo de PRs
 * Monitora PRs em um intervalo
 */
export async function example4_ContinuousPRMonitoring(): Promise<void> {
  console.log("\n=== Exemplo 4: Monitoramento contínuo ===\n");

  const engine = createPRAutomationEngine({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-example",
    autoTriggerCI: true,
  });

  const analyzeInterval = 60000; // 1 minuto
  let iterationCount = 0;
  const maxIterations = 3; // Limita a 3 iterações para o exemplo

  const monitor = setInterval(async () => {
    iterationCount++;
    console.log(`\n⏰ Iteração ${iterationCount} (${new Date().toLocaleTimeString()})`);

    try {
      // Analisa PRs abertos recentemente
      const prNumbers = [42]; // Pode ser expandido para buscar dinamicamente

      for (const prNumber of prNumbers) {
        const analysis = await engine.analyzePR(prNumber);

        if (analysis.suggestions.length > 0) {
          console.log(
            `⚠️  PR #${prNumber} tem ${analysis.suggestions.length} sugestões`
          );
        }

        if (analysis.buildStatus && !analysis.buildStatus.passed) {
          console.log(`❌ PR #${prNumber}: Build falhou`);
        }
      }
    } catch (error) {
      console.error("❌ Erro no monitoramento:", error);
    }

    if (iterationCount >= maxIterations) {
      clearInterval(monitor);
      console.log("\n✅ Monitoramento finalizado");
    }
  }, analyzeInterval);
}

/**
 * Exemplo 5: Análise com sugestões detalhadas
 * Foca em gerar e exibir sugestões detalhadas
 */
export async function example5_DetailedSuggestions(): Promise<void> {
  console.log("\n=== Exemplo 5: Sugestões detalhadas ===\n");

  const engine = createPRAutomationEngine({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-example",
    autoTriggerCI: false,
    minConfidenceThreshold: 0.5,
  });

  try {
    const analysis = await engine.analyzePR(42);

    console.log(`📊 PR #${analysis.prNumber}: ${analysis.title}`);
    console.log(`\n📋 Total de sugestões: ${analysis.suggestions.length}\n`);

    analysis.suggestions.forEach((suggestion, index) => {
      console.log(
        `${index + 1}. [${suggestion.severity.toUpperCase()}] ${suggestion.title}`
      );
      console.log(`   Confiança: ${(suggestion.confidence * 100).toFixed(0)}%`);
      if (suggestion.file) {
        console.log(`   Arquivo: ${suggestion.file}`);
      }
      console.log(`   \n   Descrição: ${suggestion.description}`);
      console.log(`   \n   Recomendação: ${suggestion.recommendation}`);

      if (suggestion.examples && suggestion.examples.length > 0) {
        console.log(`   \n   Exemplos:`);
        suggestion.examples.forEach((example) => {
          console.log(`     • ${example}`);
        });
      }
      console.log("\n");
    });
  } catch (error) {
    console.error("❌ Erro ao gerar sugestões:", error);
  }
}

/**
 * Exemplo 6: Integração com Supabase
 * Persiste análises no Supabase
 */
export async function example6_SupabaseIntegration(): Promise<void> {
  console.log("\n=== Exemplo 6: Integração com Supabase ===\n");

  const engine = createPRAutomationEngine({
    githubToken: process.env.GITHUB_TOKEN || "test-token",
    owner: "manta-associados",
    repo: "codex-example",
    supabaseUrl: process.env.SUPABASE_URL,
    supabaseKey: process.env.SUPABASE_ANON_KEY,
    autoTriggerCI: false,
  });

  try {
    const analysis = await engine.analyzePR(42);

    if (analysis.status === PRAnalysisStatus.COMPLETED) {
      console.log("✅ Análise completada e persistida no Supabase");
      console.log(`  - PR: #${analysis.prNumber}`);
      console.log(`  - Arquivos: ${analysis.filesChanged}`);
      console.log(`  - Sugestões: ${analysis.suggestions.length}`);
      console.log(`  - Padrões: ${analysis.codePatterns.length}`);
      console.log(`  - CI Disparado: ${analysis.ciTriggered}`);
    }
  } catch (error) {
    console.error("❌ Erro na integração com Supabase:", error);
  }
}

/**
 * Função auxiliar para rodar todos os exemplos
 */
export async function runAllPRAutomationExamples(): Promise<void> {
  console.log("🚀 PR Automation Engine - Exemplos\n");
  console.log("=" + "=".repeat(50));

  try {
    // Nota: Os exemplos requerem PRs reais e GitHub token válido
    // Para demo, estão comentados
    /*
    await example1_BasicPRAnalysis();
    await example2_PRAnalysisWithCI();
    await example3_BatchPRAnalysis();
    await example5_DetailedSuggestions();
    */

    console.log("\n✅ Exemplos carregados (comentados por padrão)");
    console.log("\nPara executar, descomente os exemplos em:");
    console.log("  src/examples/pr-automation-integration.ts");
    console.log("\nRequisitos:");
    console.log("  - GITHUB_TOKEN configurado");
    console.log("  - PRs reais no repositório");
    console.log("  - Permissões de leitura no repositório");
  } catch (error) {
    console.error("❌ Erro ao executar exemplos:", error);
  }
}

