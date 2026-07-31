/**
 * Exemplo: Integração do LLM Judge com PRAutomationEngine
 * Demonstra como combinar análise de PR com julgamento de risco
 */

import {
  PRAutomationEngine,
  type PRAnalysis,
} from "../services/pr-automation";
import {
  createLLMJudge,
  translateRiskLevel,
  translateAction,
  type PRJudgment,
  type PRData,
} from "../services/llm-judge";

/**
 * Sistema completo de automação de PR com julgamento de risco
 */
export class EnhancedPRAutomationEngine {
  private automationEngine: PRAutomationEngine;
  private judge = createLLMJudge();

  constructor(automationConfig: any) {
    this.automationEngine = new PRAutomationEngine(automationConfig);
  }

  /**
   * Pipeline completo: análise + julgamento de risco
   */
  async analyzeAndJudgePR(
    prNumber: number,
    owner: string,
    repo: string
  ): Promise<{
    analysis: PRAnalysis;
    judgment: PRJudgment;
    decision: {
      canAutoMerge: boolean;
      requiresHumanReview: boolean;
      recommendation: string;
    };
  }> {
    console.log(`\n📋 Analisando PR #${prNumber}...`);

    // Etapa 1: Análise com PRAutomationEngine
    console.log("   → Fase 1: Análise de PR (padrões, sugestões, CI)");
    const analysis = await this.automationEngine.analyzePR(
      prNumber,
      owner,
      repo
    );

    // Etapa 2: Converte análise para formato do LLM Judge
    console.log("   → Fase 2: Conversão para PRData");
    const prData = this.convertAnalysisToPRData(analysis);

    // Etapa 3: Julgamento de risco
    console.log("   → Fase 3: Julgamento de risco (Claude Haiku)");
    const judgment = await this.judge.judge(prData);

    // Etapa 4: Combina resultados
    console.log("   → Fase 4: Combinação de resultados");
    const decision = this.makeDecision(analysis, judgment);

    return {
      analysis,
      judgment,
      decision,
    };
  }

  /**
   * Converte PRAnalysis em PRData para o judge
   */
  private convertAnalysisToPRData(analysis: PRAnalysis): PRData {
    return {
      prNumber: analysis.prNumber,
      owner: analysis.owner,
      repo: analysis.repo,
      title: analysis.title,
      description: analysis.description,
      author: analysis.author,
      branch: analysis.branch,
      baseBranch: analysis.baseBranch,
      filesChanged: analysis.filesChanged,
      additions: analysis.additions,
      deletions: analysis.deletions,
      changedFiles: analysis.changedFiles,
      commits: analysis.commitMessages.map((msg) => ({
        message: msg,
        author: analysis.author,
      })),
      ciPassed: analysis.buildStatus?.passed,
      ciWorkflowId: analysis.workflowRunId,
      testsPassed: analysis.buildStatus?.testsPassed,
      testsFailed: analysis.buildStatus?.testsFailed,
      coverage: analysis.buildStatus?.coverage,
    };
  }

  /**
   * Toma decisão baseada em análise + julgamento
   */
  private makeDecision(
    analysis: PRAnalysis,
    judgment: PRJudgment
  ): {
    canAutoMerge: boolean;
    requiresHumanReview: boolean;
    recommendation: string;
  } {
    const decision = {
      canAutoMerge: false,
      requiresHumanReview: false,
      recommendation: "",
    };

    // Lógica de decisão
    if (judgment.riskLevel === "high") {
      decision.requiresHumanReview = true;
      decision.recommendation =
        `⚠️ ALTO RISCO - Requer revisão humana\n` +
        `Motivo: ${judgment.reason}\n` +
        `Categorias: ${judgment.riskCategories.join(", ")}\n` +
        `Confiança: ${(judgment.confidence * 100).toFixed(1)}%`;
    } else if (judgment.riskLevel === "medium") {
      if (analysis.buildStatus?.passed && judgment.confidence > 0.75) {
        decision.canAutoMerge = true;
        decision.recommendation =
          `✅ MERGE AUTOMÁTICO (CI passou, confiança alta)\n` +
          `Motivo: ${judgment.reason}\n` +
          `Confiança: ${(judgment.confidence * 100).toFixed(1)}%`;
      } else {
        decision.requiresHumanReview = true;
        decision.recommendation =
          `⚠️ RISCO MÉDIO - Aguardando confirmação\n` +
          `CI Status: ${analysis.buildStatus?.passed ? "✅ Passou" : "❌ Falhou"}\n` +
          `Confiança: ${(judgment.confidence * 100).toFixed(1)}%`;
      }
    } else {
      // low-risk
      decision.canAutoMerge = true;
      decision.recommendation =
        `✅ AUTO-MERGE (baixo risco)\n` +
        `Motivo: ${judgment.reason}\n` +
        `Confiança: ${(judgment.confidence * 100).toFixed(1)}%`;
    }

    return decision;
  }

  /**
   * Retorna relatório completo
   */
  printReport(
    analysis: PRAnalysis,
    judgment: PRJudgment,
    decision: {
      canAutoMerge: boolean;
      requiresHumanReview: boolean;
      recommendation: string;
    }
  ): void {
    console.log("\n" + "=".repeat(70));
    console.log("📊 RELATÓRIO COMPLETO DE ANÁLISE");
    console.log("=".repeat(70));

    // Header
    console.log(`\n🔹 PR #${analysis.prNumber}: ${analysis.title}`);
    console.log(`   Autor: ${analysis.author} | Branch: ${analysis.branch}`);

    // Análise de Padrões
    console.log(`\n📋 Análise de Padrões (PRAutomationEngine):`);
    console.log(`   • Arquivos: ${analysis.filesChanged}`);
    console.log(`   • Adições: ${analysis.additions} linhas`);
    console.log(`   • Deleções: ${analysis.deletions} linhas`);
    console.log(`   • Padrões detectados: ${analysis.codePatterns.length}`);
    console.log(`   • Sugestões geradas: ${analysis.suggestions.length}`);

    if (analysis.suggestions.length > 0) {
      console.log(`\n   Sugestões principais:`);
      analysis.suggestions.slice(0, 3).forEach((s) => {
        console.log(
          `   - [${s.severity.toUpperCase()}] ${s.title} (${(s.confidence * 100).toFixed(0)}%)`
        );
      });
    }

    // Julgamento de Risco
    console.log(`\n🎯 Julgamento de Risco (LLM Judge):`);
    console.log(`   • Risk Level: ${translateRiskLevel(judgment.riskLevel)}`);
    console.log(
      `   • Confiança: ${(judgment.confidence * 100).toFixed(1)}%`
    );
    console.log(`   • Ação: ${translateAction(judgment.action)}`);
    console.log(`   • Motivo: ${judgment.reason}`);

    if (judgment.riskCategories.length > 0) {
      console.log(`   • Categorias: ${judgment.riskCategories.join(", ")}`);
    }

    // Análise Detalhada
    console.log(`\n🔍 Análise Detalhada:`);
    const details = judgment.detailedAnalysis;

    if (details.securityConcerns.length > 0) {
      console.log(`   Preocupações de Segurança:`);
      details.securityConcerns.forEach((c) => console.log(`   - ${c}`));
    }

    if (details.performanceRisks.length > 0) {
      console.log(`   Riscos de Performance:`);
      details.performanceRisks.forEach((r) => console.log(`   - ${r}`));
    }

    console.log(`   Testes: ${details.testCoverage.hasTests ? "✅ Presentes" : "❌ Ausentes"}`);
    console.log(
      `   Tamanho: ${details.changeSize.severity.toUpperCase()} (${details.changeSize.filesChanged} arquivos)`
    );

    // Decisão Final
    console.log(`\n✨ DECISÃO FINAL:`);
    console.log(`   ${decision.recommendation}`);

    // Status de CI
    if (analysis.buildStatus) {
      console.log(`\n🔧 Status de CI/CD:`);
      console.log(
        `   • Build: ${analysis.buildStatus.passed ? "✅ Passou" : "❌ Falhou"}`
      );
      if (analysis.buildStatus.testsPassed !== undefined) {
        console.log(
          `   • Testes: ${analysis.buildStatus.testsPassed}/${(analysis.buildStatus.testsPassed || 0) + (analysis.buildStatus.testsFailed || 0)}`
        );
      }
      if (analysis.buildStatus.coverage !== undefined) {
        console.log(`   • Cobertura: ${analysis.buildStatus.coverage}%`);
      }
    }

    console.log("\n" + "=".repeat(70));
  }
}

/**
 * Middleware para GitHub Actions
 */
export async function githubActionsMiddleware(
  prNumber: number,
  owner: string,
  repo: string,
  githubToken: string
) {
  const engine = new EnhancedPRAutomationEngine({
    githubToken,
    owner,
    repo,
  });

  try {
    const { analysis, judgment, decision } =
      await engine.analyzeAndJudgePR(prNumber, owner, repo);

    return {
      status: "success",
      canAutoMerge: decision.canAutoMerge,
      requiresReview: decision.requiresHumanReview,
      riskLevel: judgment.riskLevel,
      confidence: judgment.confidence,
      recommendation: decision.recommendation,
      judgment,
      analysis,
    };
  } catch (error) {
    return {
      status: "error",
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

// Exportar
export { EnhancedPRAutomationEngine, githubActionsMiddleware };
