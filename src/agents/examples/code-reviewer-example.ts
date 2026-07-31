/**
 * Code Reviewer Agent — Exemplo de uso
 *
 * Demonstra como usar o CodeReviewerAgent para analisar:
 * 1. PR diffs
 * 2. Novo código de agentes
 * 3. Pull requests completas
 */

import { CodeReviewerAgent, type CodeReviewInput } from "../code-reviewer";

/**
 * Exemplo 1: Análise básica de PR
 */
async function exampleBasicPRReview() {
  const agent = new CodeReviewerAgent(process.env.ANTHROPIC_API_KEY);

  const prInput: CodeReviewInput = {
    prDiff: `
--- a/src/agents/maestro.ts
+++ b/src/agents/maestro.ts
@@ -1,10 +1,15 @@
 export async function routeAgent(intent: string) {
-  const agents = ['01', '02', '03', '04', '05'];
-  for (let i = 0; i < agents.length; i++) {
-    if (intent.includes(agents[i])) {
-      return agents[i];
+  if (!intent) throw new Error('intent required');
+
+  const routes = {
+    '01': /claims|claim/i,
+    '02': /contrato|legal/i,
+    '03': /infra|rodovia/i,
+    '04': /imóvel|real estate/i,
+    '05': /orçamento|budget/i,
+  };
+
+  for (const [agent, pattern] of Object.entries(routes)) {
+    if (pattern.test(intent)) {
+      return agent;
     }
   }
-  return 'maestro';
+  return 'maestro-default';
 }`,
    newAgentCode: `
export async function routeAgent(intent: string) {
  if (!intent) throw new Error('intent required');

  const routes = {
    '01': /claims|claim/i,
    '02': /contrato|legal/i,
    '03': /infra|rodovia/i,
    '04': /imóvel|real estate/i,
    '05': /orçamento|budget/i,
  };

  for (const [agent, pattern] of Object.entries(routes)) {
    if (pattern.test(intent)) {
      return agent;
    }
  }
  return 'maestro-default';
}`,
    agentPath: "src/agents/maestro.ts",
    prContext: {
      title: "refactor: improve agent routing with regex patterns",
      description:
        "Replace loop-based routing with regex patterns for better performance and maintainability",
      author: "dev@mantaassociados.com",
    },
  };

  const result = await agent.reviewCode(prInput);

  console.log("=== ANÁLISE DE PR - MAESTRO ===\n");
  console.log(`Status: ${result.status}`);
  console.log(`Score: ${result.overallScore}/100`);
  console.log(`Findings: ${result.findings.length}\n`);
  console.log("Estatísticas:");
  console.log(`  Correctness: ${result.dimensionStats.correctness}`);
  console.log(`  Security: ${result.dimensionStats.security}`);
  console.log(`  Performance: ${result.dimensionStats.performance}`);
  console.log(`  Style: ${result.dimensionStats.style}\n`);
  console.log("Severidade:");
  console.log(`  Critical: ${result.severityStats.critical}`);
  console.log(`  Error: ${result.severityStats.error}`);
  console.log(`  Warning: ${result.severityStats.warning}`);
  console.log(`  Info: ${result.severityStats.info}\n`);
  console.log("RESUMO:");
  console.log(result.summary);

  if (result.findings.length > 0) {
    console.log("\nFINDINGS DETALHADOS:");
    for (const finding of result.findings) {
      console.log(`\n[${finding.severity.toUpperCase()}] ${finding.title}`);
      console.log(`  Arquivo: ${finding.file}:${finding.line}`);
      console.log(`  Dimensão: ${finding.dimension}`);
      console.log(`  ${finding.description}`);
      if (finding.suggestion) {
        console.log(`  Sugestão: ${finding.suggestion}`);
      }
    }
  }
}

/**
 * Exemplo 2: Análise focada em segurança
 */
async function exampleSecurityFocusedReview() {
  const agent = new CodeReviewerAgent(process.env.ANTHROPIC_API_KEY);

  const securityInput: CodeReviewInput = {
    prDiff: "",
    newAgentCode: `
import { Anthropic } from "@anthropic-ai/sdk";

export class UnsafeService {
  private apiKey: string;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
    // BUG: Logging sensitive data
    console.log("API Key: " + apiKey);
  }

  async queryDatabase(userInput: string) {
    // BUG: SQL injection
    const query = "SELECT * FROM agents WHERE name = '" + userInput + "'";
    return database.execute(query);
  }

  getSecretConfig() {
    // BUG: Exposing secrets in code
    return {
      apiKey: "sk-ant-v123456789",
      dbPassword: "admin123",
    };
  }
}`,
    agentPath: "src/agents/unsafe-service.ts",
    dimensions: ["security"],
  };

  const result = await agent.reviewCode(securityInput);

  console.log("\n=== ANÁLISE DE SEGURANÇA ===\n");
  console.log(`Score: ${result.overallScore}/100`);
  console.log(`Security Findings: ${result.dimensionStats.security}\n`);

  const criticalFindings = result.findings.filter((f) => f.severity === "critical");
  if (criticalFindings.length > 0) {
    console.log("🔴 ISSUES CRÍTICOS:");
    for (const finding of criticalFindings) {
      console.log(`  - [L${finding.line}] ${finding.title}`);
    }
  }
}

/**
 * Exemplo 3: Análise de novo agente vertical (S8 - Saneamento)
 */
async function exampleNewVerticalAgentReview() {
  const agent = new CodeReviewerAgent(process.env.ANTHROPIC_API_KEY);

  const newAgentInput: CodeReviewInput = {
    prDiff: `
--- /dev/null
+++ b/src/agents/agente-saneamento.ts
@@ -0,0 +1,100 @@
+export interface SanitationProject {
+  id: string;
+  type: 'ETA' | 'ETE' | 'Adutora';
+  location: string;
+  budget: number;
+}
+
+export class SanitationAgent {
+  async analyzeProject(project: SanitationProject) {
+    if (!project.id) return null;
+
+    const analysis = {
+      regulatory: this.checkSNIS(project),
+      technical: this.assessTechnical(project),
+      financial: this.reviewBudget(project),
+    };
+
+    return analysis;
+  }
+}`,
    newAgentCode: `
export interface SanitationProject {
  id: string;
  type: 'ETA' | 'ETE' | 'Adutora' | 'Drenagem';
  location: string;
  budget: number;
  stage: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;
}

export class SanitationAgent {
  private rag: RAGService;

  constructor(ragService: RAGService) {
    this.rag = ragService;
  }

  async analyzeProject(project: SanitationProject): Promise<ProjectAnalysis> {
    this.validateProject(project);

    const analysis = {
      regulatory: await this.checkSNIS(project),
      technical: await this.assessTechnical(project),
      financial: await this.reviewBudget(project),
      references: await this.rag.search('saneamento', project.type),
    };

    return analysis;
  }

  private validateProject(project: SanitationProject): void {
    if (!project.id) throw new Error('Project ID required');
    if (!project.budget || project.budget < 0) {
      throw new Error('Valid budget required');
    }
    if (project.stage < 1 || project.stage > 8) {
      throw new Error('Invalid stage');
    }
  }

  private async checkSNIS(project: SanitationProject) {
    // Check against SNIS database
    return { status: 'pending' };
  }

  private async assessTechnical(project: SanitationProject) {
    // Technical assessment
    return { status: 'pending' };
  }

  private async reviewBudget(project: SanitationProject) {
    // Financial review
    return { status: 'pending' };
  }
}`,
    agentPath: "src/agents/agente-saneamento.ts",
    prContext: {
      title: "feat: implement sanitation vertical agent S8",
      description:
        "New vertical agent for sanitation projects (ETA/ETE/Adutora). Supports all 8 lifecycle phases. Integrates with SNIS RAG collection.",
      author: "mauricio.neves@mantaassociados.com",
    },
  };

  const result = await agent.reviewCode(newAgentInput);

  console.log("\n=== NOVO AGENTE VERTICAL - SANEAMENTO (S8) ===\n");
  console.log(`Score: ${result.overallScore}/100`);
  console.log(`Tempo de análise: ${result.analysisTimeMs}ms\n`);
  console.log("Resumo da análise:");
  console.log(result.summary);
}

/**
 * Main: executa exemplos
 */
async function main() {
  console.log("Code Reviewer Agent - Exemplos de Uso\n");
  console.log("=====================================\n");

  try {
    await exampleBasicPRReview();
    await exampleSecurityFocusedReview();
    await exampleNewVerticalAgentReview();

    console.log("\n✅ Todos os exemplos executados com sucesso!");
  } catch (error) {
    console.error("❌ Erro ao executar exemplos:", error);
    process.exit(1);
  }
}

// Se executado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export {
  exampleBasicPRReview,
  exampleSecurityFocusedReview,
  exampleNewVerticalAgentReview,
};
