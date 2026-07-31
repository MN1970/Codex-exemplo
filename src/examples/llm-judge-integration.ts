/**
 * Exemplo de Integração do LLM Judge
 * Demonstra como usar o judge em cenários reais de automação de PRs
 */

import {
  createLLMJudge,
  judgePR,
  translateAction,
  translateRiskLevel,
  JudgeAction,
  type PRData,
  type PRJudgment,
} from "../services/llm-judge";

/**
 * Classe que encapsula a integração do LLM Judge com GitHub
 */
class GitHubPRAutoMerger {
  private judge = createLLMJudge();
  private githubToken: string;

  constructor(githubToken: string) {
    this.githubToken = githubToken;
  }

  /**
   * Processa um PR e decide o melhor curso de ação
   */
  async processPR(prData: PRData): Promise<{
    judgment: PRJudgment;
    action: "merge" | "merge_conditional" | "comment" | "none";
    comment?: string;
  }> {
    console.log(`\n📋 Processando PR #${prData.prNumber}: ${prData.title}`);

    // Faz julgamento
    const judgment = await this.judge.judge(prData);

    console.log(`\n🎯 Resultado:`);
    console.log(`   Risk: ${translateRiskLevel(judgment.riskLevel)}`);
    console.log(`   Confidence: ${(judgment.confidence * 100).toFixed(1)}%`);
    console.log(`   Reason: ${judgment.reason}`);

    // Decide ação baseado no julgamento
    const decision = this.decideAction(judgment, prData);

    console.log(`\n✅ Ação recomendada: ${decision.action}`);
    if (decision.comment) {
      console.log(`💬 Comentário a postar:\n${decision.comment}`);
    }

    return {
      judgment,
      ...decision,
    };
  }

  /**
   * Decide qual ação tomar baseado no julgamento
   */
  private decideAction(
    judgment: PRJudgment,
    prData: PRData
  ): {
    action: "merge" | "merge_conditional" | "comment" | "none";
    comment?: string;
  } {
    switch (judgment.action) {
      case JudgeAction.AUTO_MERGE:
        return {
          action: "merge",
          comment: this.generateAutoMergeComment(judgment),
        };

      case JudgeAction.CONDITIONAL_MERGE:
        if (prData.ciPassed) {
          return {
            action: "merge_conditional",
            comment: this.generateConditionalMergeComment(judgment, prData),
          };
        } else {
          return {
            action: "comment",
            comment: this.generateWaitForCIComment(judgment),
          };
        }

      case JudgeAction.REQUIRES_REVIEW:
        return {
          action: "comment",
          comment: this.generateRequiresReviewComment(judgment),
        };

      case JudgeAction.BLOCKING:
        return {
          action: "none",
          comment: this.generateBlockingComment(judgment),
        };

      default:
        return {
          action: "none",
        };
    }
  }

  /**
   * Gera comentário para auto-merge
   */
  private generateAutoMergeComment(judgment: PRJudgment): string {
    return `✅ **LLM Judge: AUTO-MERGE**

🎯 Classificação: ${translateRiskLevel(judgment.riskLevel)}
📊 Confiança: ${(judgment.confidence * 100).toFixed(1)}%
📝 Motivo: ${judgment.reason}

Esta PR será merged automaticamente.`;
  }

  /**
   * Gera comentário para conditional merge
   */
  private generateConditionalMergeComment(
    judgment: PRJudgment,
    prData: PRData
  ): string {
    const concerns = judgment.detailedAnalysis.securityConcerns;
    const risks = judgment.detailedAnalysis.performanceRisks;

    let comment = `🔄 **LLM Judge: CONDITIONAL MERGE**

🎯 Classificação: ${translateRiskLevel(judgment.riskLevel)}
📊 Confiança: ${(judgment.confidence * 100).toFixed(1)}%
📝 Motivo: ${judgment.reason}

✅ **CI Pipeline passou** - PR será merged

`;

    if (concerns.length > 0) {
      comment += `⚠️ **Preocupações de Segurança:**\n`;
      concerns.forEach((c) => {
        comment += `  - ${c}\n`;
      });
      comment += "\n";
    }

    if (risks.length > 0) {
      comment += `⚡ **Riscos de Performance:**\n`;
      risks.forEach((r) => {
        comment += `  - ${r}\n`;
      });
      comment += "\n";
    }

    comment += `📊 **Estatísticas:**
- Arquivos: ${judgment.detailedAnalysis.changeSize.filesChanged}
- Adições: ${judgment.detailedAnalysis.changeSize.additionsCount}
- Deleções: ${judgment.detailedAnalysis.changeSize.deletionsCount}
- Tamanho: ${judgment.detailedAnalysis.changeSize.severity}`;

    return comment;
  }

  /**
   * Gera comentário para aguardar CI
   */
  private generateWaitForCIComment(judgment: PRJudgment): string {
    return `⏳ **LLM Judge: AGUARDANDO CI**

🎯 Classificação: ${translateRiskLevel(judgment.riskLevel)}
📊 Confiança: ${(judgment.confidence * 100).toFixed(1)}%

A PR foi classificada como ${judgment.riskLevel}-risk e o CI ainda não passou.
Merge será permitido assim que o CI passar.`;
  }

  /**
   * Gera comentário para review obrigatória
   */
  private generateRequiresReviewComment(judgment: PRJudgment): string {
    const concerns = judgment.detailedAnalysis.securityConcerns;
    const hasBreaking = judgment.detailedAnalysis.codePatterns.hasBreakingChanges;

    let comment = `🚨 **LLM Judge: REQUER REVISÃO HUMANA**

🎯 Classificação: ${translateRiskLevel(judgment.riskLevel)}
📊 Confiança: ${(judgment.confidence * 100).toFixed(1)}%
📝 Motivo: ${judgment.reason}

Esta PR foi classificada como **${judgment.riskLevel}-risk** e requer revisão humana antes do merge.

`;

    if (hasBreaking) {
      comment += `⚠️ **Mudança de Quebra Detectada**\n`;
      comment += `Esta PR pode conter mudanças que quebram compatibilidade.\n\n`;
    }

    if (concerns.length > 0) {
      comment += `🔒 **Preocupações de Segurança:**\n`;
      concerns.forEach((c) => {
        comment += `  - ${c}\n`;
      });
      comment += "\n";
    }

    const categories = judgment.riskCategories.join(", ");
    comment += `📋 **Categorias de Risco:** ${categories}

Por favor, revise este PR antes de fazer merge.`;

    return comment;
  }

  /**
   * Gera comentário para PR bloqueada
   */
  private generateBlockingComment(judgment: PRJudgment): string {
    return `🛑 **LLM Judge: BLOQUEADA**

🎯 Classificação: ${translateRiskLevel(judgment.riskLevel)}
📊 Confiança: ${(judgment.confidence * 100).toFixed(1)}%
📝 Motivo: ${judgment.reason}

Esta PR foi **BLOQUEADA** e não pode ser merged.

**Ações necessárias:**
1. Revise e resolva as questões apontadas
2. Resubmeta a PR após as correções

Categorias de Risco: ${judgment.riskCategories.join(", ")}`;
  }

  /**
   * Simula merge automático
   */
  async simulateMerge(prNumber: number, owner: string, repo: string): Promise<boolean> {
    console.log(
      `\n🔀 Simulando merge de PR #${prNumber} em ${owner}/${repo}`
    );
    console.log(
      `   Seria chamado: PUT /repos/${owner}/${repo}/pulls/${prNumber}/merge`
    );
    return true;
  }

  /**
   * Simula comentário em PR
   */
  async simulateComment(
    prNumber: number,
    owner: string,
    repo: string,
    comment: string
  ): Promise<boolean> {
    console.log(`\n💬 Simulando comentário em PR #${prNumber}`);
    console.log(`   Seria chamado: POST /repos/${owner}/${repo}/issues/${prNumber}/comments`);
    console.log(`   Corpo: ${comment.substring(0, 100)}...`);
    return true;
  }
}

/**
 * Exemplo de uso 1: Processar uma PR de documentação (baixo risco)
 */
async function example1_DocumentationPR() {
  console.log("\n" + "=".repeat(60));
  console.log("Exemplo 1: PR de Documentação (Baixo Risco)");
  console.log("=".repeat(60));

  const prData: PRData = {
    prNumber: 101,
    owner: "mycompany",
    repo: "myapp",
    title: "docs: add API documentation",
    description:
      "Adds comprehensive API documentation for v2.0 endpoints\n\nFixes #456",
    author: "jane.smith",
    branch: "docs/api-v2",
    baseBranch: "main",
    filesChanged: 3,
    additions: 250,
    deletions: 10,
    changedFiles: [
      {
        filename: "docs/api.md",
        additions: 200,
        deletions: 10,
      },
      {
        filename: "docs/examples.md",
        additions: 50,
        deletions: 0,
      },
      {
        filename: "CONTRIBUTING.md",
        additions: 0,
        deletions: 0,
      },
    ],
    commits: [
      {
        message: "docs: add API documentation",
        author: "jane.smith",
      },
    ],
    ciPassed: true,
    testsPassed: 42,
    testsFailed: 0,
    coverage: 95,
  };

  const merger = new GitHubPRAutoMerger("fake-token");
  const result = await merger.processPR(prData);

  console.log(`\n📌 Resultado Final:`);
  console.log(`   Ação: ${result.action.toUpperCase()}`);
  console.log(`   Risk: ${translateRiskLevel(result.judgment.riskLevel)}`);
}

/**
 * Exemplo de uso 2: Processar uma PR com nova feature (risco médio)
 */
async function example2_FeaturePR() {
  console.log("\n" + "=".repeat(60));
  console.log("Exemplo 2: PR com Feature (Risco Médio)");
  console.log("=".repeat(60));

  const prData: PRData = {
    prNumber: 102,
    owner: "mycompany",
    repo: "myapp",
    title: "feat: add dark mode support",
    description:
      "Implements dark mode for the entire application\n\nIncludes theme switcher component and CSS variables",
    author: "john.doe",
    branch: "feat/dark-mode",
    baseBranch: "main",
    filesChanged: 12,
    additions: 450,
    deletions: 150,
    changedFiles: [
      {
        filename: "src/theme/darkMode.ts",
        additions: 150,
        deletions: 0,
      },
      {
        filename: "src/components/ThemeSwitcher.tsx",
        additions: 100,
        deletions: 0,
      },
      {
        filename: "src/styles/dark.css",
        additions: 200,
        deletions: 0,
      },
      {
        filename: "src/theme/darkMode.test.ts",
        additions: 80,
        deletions: 0,
      },
    ],
    commits: [
      {
        message: "feat: add dark mode support",
        author: "john.doe",
      },
      {
        message: "test: add dark mode tests",
        author: "john.doe",
      },
    ],
    ciPassed: true,
    testsPassed: 75,
    testsFailed: 0,
    coverage: 88,
  };

  const merger = new GitHubPRAutoMerger("fake-token");
  const result = await merger.processPR(prData);

  console.log(`\n📌 Resultado Final:`);
  console.log(`   Ação: ${result.action.toUpperCase()}`);
  console.log(`   Risk: ${translateRiskLevel(result.judgment.riskLevel)}`);
}

/**
 * Exemplo de uso 3: Processar uma PR com breaking change (alto risco)
 */
async function example3_BreakingChangePR() {
  console.log("\n" + "=".repeat(60));
  console.log("Exemplo 3: PR com Breaking Change (Alto Risco)");
  console.log("=".repeat(60));

  const prData: PRData = {
    prNumber: 103,
    owner: "mycompany",
    repo: "myapp",
    title: "refactor: change API response format (BREAKING CHANGE)",
    description:
      "Major API restructuring for improved consistency\n\nWARNING: This is a breaking change for API v1 consumers",
    author: "alice.johnson",
    branch: "refactor/api-v2",
    baseBranch: "main",
    filesChanged: 34,
    additions: 1200,
    deletions: 800,
    changedFiles: [
      {
        filename: "src/api/handlers/user.ts",
        additions: 300,
        deletions: 250,
        patch:
          "- export interface UserResponse { id: number; name: string; }\n+ export interface APIUser { userId: string; fullName: string; }",
      },
      {
        filename: "src/api/handlers/products.ts",
        additions: 400,
        deletions: 350,
      },
      {
        filename: "src/types/api.ts",
        additions: 200,
        deletions: 150,
      },
    ],
    commits: [
      {
        message: "refactor: change API response format",
        author: "alice.johnson",
      },
    ],
    ciPassed: false,
    testsPassed: 45,
    testsFailed: 12,
    coverage: 72,
  };

  const merger = new GitHubPRAutoMerger("fake-token");
  const result = await merger.processPR(prData);

  console.log(`\n📌 Resultado Final:`);
  console.log(`   Ação: ${result.action.toUpperCase()}`);
  console.log(`   Risk: ${translateRiskLevel(result.judgment.riskLevel)}`);
}

/**
 * Exemplo de uso 4: Processar uma PR com vulnerabilidade de segurança
 */
async function example4_SecurityRiskPR() {
  console.log("\n" + "=".repeat(60));
  console.log("Exemplo 4: PR com Risco de Segurança");
  console.log("=".repeat(60));

  const prData: PRData = {
    prNumber: 104,
    owner: "mycompany",
    repo: "myapp",
    title: "fix: improve user authentication",
    description: "Add user input validation and authentication improvements",
    author: "bob.wilson",
    branch: "fix/auth-security",
    baseBranch: "main",
    filesChanged: 5,
    additions: 200,
    deletions: 50,
    changedFiles: [
      {
        filename: "src/auth/login.ts",
        additions: 120,
        deletions: 30,
        patch: `
+ const user = JSON.parse(userInput);
+ response.html = '<div>' + userInput + '</div>';
+ const query = 'SELECT * FROM users WHERE email = ' + email;
`,
      },
    ],
    commits: [
      {
        message: "fix: improve authentication",
        author: "bob.wilson",
      },
    ],
    ciPassed: true,
  };

  const merger = new GitHubPRAutoMerger("fake-token");
  const result = await merger.processPR(prData);

  console.log(`\n📌 Resultado Final:`);
  console.log(`   Ação: ${result.action.toUpperCase()}`);
  console.log(`   Risk: ${translateRiskLevel(result.judgment.riskLevel)}`);
}

/**
 * Função principal que executa todos os exemplos
 */
async function runAllExamples() {
  console.log("\n╔════════════════════════════════════════════════════╗");
  console.log("║         LLM Judge Integration Examples              ║");
  console.log("╚════════════════════════════════════════════════════╝");

  try {
    await example1_DocumentationPR();
    await example2_FeaturePR();
    await example3_BreakingChangePR();
    await example4_SecurityRiskPR();

    console.log("\n" + "=".repeat(60));
    console.log("✅ Todos os exemplos executados com sucesso!");
    console.log("=".repeat(60));
  } catch (error) {
    console.error("\n❌ Erro ao executar exemplos:", error);
  }
}

// Exporta funções
export {
  GitHubPRAutoMerger,
  example1_DocumentationPR,
  example2_FeaturePR,
  example3_BreakingChangePR,
  example4_SecurityRiskPR,
  runAllExamples,
};

// Se executado diretamente
if (require.main === module) {
  runAllExamples().catch(console.error);
}
