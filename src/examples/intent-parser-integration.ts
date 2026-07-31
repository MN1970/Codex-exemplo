/**
 * Exemplo de integração do Intent Parser com Maestro Router
 * Fluxo completo: user input → intent parse → routing → execution
 */

import {
  IntentParser,
  parseAndValidate,
  type ParsedIntent,
} from "../services/intent-parser";
import { MaestroRouter, type RoutingResult } from "../services/maestro-router";

/**
 * Pipeline completo de processamento de comando de usuário
 */
export class CommandProcessingPipeline {
  private intentParser: IntentParser;
  private maestroRouter: MaestroRouter;

  constructor() {
    this.intentParser = new IntentParser();
    this.maestroRouter = new MaestroRouter();
  }

  /**
   * Processa uma mensagem de usuário do início ao fim
   * Retorna: intent → routing → execution plan
   */
  async processUserCommand(userMessage: string): Promise<{
    intent: ParsedIntent;
    routing: RoutingResult | null;
    executionPlan: ExecutionPlan;
    summary: string;
  }> {
    console.log(`\n📨 Processando: "${userMessage}"\n`);

    // ETAPA 1: Parse de intent com Claude
    console.log("⚙️  [1/3] Analisando intenção com Claude NLU...");
    const { intent, validation } = await parseAndValidate(userMessage);

    console.log(`  ✓ Action: ${intent.action}`);
    console.log(`  ✓ Target: ${intent.target}`);
    console.log(`  ✓ Confidence: ${(intent.confidence * 100).toFixed(0)}%`);

    if (!validation.isValid) {
      console.log(
        `  ⚠️  Validação falhou: ${validation.errors.join(", ")}`
      );
    }

    // ETAPA 2: Routing (se intent é sobre agente)
    let routing: RoutingResult | null = null;
    if (intent.target === "agent" && intent.params.segment) {
      console.log("\n🎯 [2/3] Roteando para agente apropriado...");

      try {
        routing = this.maestroRouter.route(userMessage);
        console.log(`  ✓ Agente: ${routing.agent.name}`);
        console.log(`  ✓ Score: ${routing.score.toFixed(2)}`);
      } catch (error) {
        console.warn("  ⚠️  Falha no routing:", error);
      }
    } else {
      console.log("\n⏭️  [2/3] Skipping routing (not an agent action)");
    }

    // ETAPA 3: Gerar plano de execução
    console.log("\n📋 [3/3] Gerando plano de execução...");
    const executionPlan = this.generateExecutionPlan(
      intent,
      routing,
      validation.isValid
    );

    const summary = this.generateSummary(intent, routing, executionPlan);

    return {
      intent,
      routing,
      executionPlan,
      summary,
    };
  }

  /**
   * Gera plano de execução baseado em intent + routing
   */
  private generateExecutionPlan(
    intent: ParsedIntent,
    routing: RoutingResult | null,
    isValid: boolean
  ): ExecutionPlan {
    const steps: ExecutionStep[] = [];
    let status: "ready" | "pending_approval" | "blocked" = "ready";

    if (!isValid) {
      status = "blocked";
      steps.push({
        order: 1,
        action: "HALT",
        description: "Intent validation failed",
        details: "User input could not be validated",
      });
      return { steps, status, estimatedTime: 0 };
    }

    if (intent.confidence < 0.5) {
      status = "pending_approval";
      steps.push({
        order: 1,
        action: "ASK_USER",
        description: "Request clarification",
        details: (intent.clarifyingQuestions || [])[0] || "Please clarify",
      });
    }

    // Passos baseados na ação
    switch (intent.action) {
      case "create":
        steps.push(
          {
            order: 1,
            action: "VALIDATE_PARAMS",
            description: "Validate creation parameters",
            details: `Creating ${intent.target} with params: ${JSON.stringify(intent.params)}`,
          },
          {
            order: 2,
            action: "CREATE_RESOURCE",
            description: `Create ${intent.target}`,
            details: routing
              ? `Via agent: ${routing.agent.name}`
              : `Via ${intent.target} service`,
          },
          {
            order: 3,
            action: "CONFIRM",
            description: "Confirm creation",
            details: "Wait for user/system confirmation",
          }
        );
        break;

      case "execute":
        steps.push(
          {
            order: 1,
            action: "LOAD_RESOURCE",
            description: `Load ${intent.target}`,
            details: intent.params.workflowName as string,
          },
          {
            order: 2,
            action: "EXECUTE",
            description: `Execute ${intent.target}`,
            details: routing
              ? `Via ${routing.agent.name}`
              : "Direct execution",
          },
          {
            order: 3,
            action: "MONITOR",
            description: "Monitor execution",
            details: "Stream progress and logs",
          }
        );
        break;

      case "update":
        steps.push(
          {
            order: 1,
            action: "LOAD_RESOURCE",
            description: `Load ${intent.target}`,
            details: "Fetch current state",
          },
          {
            order: 2,
            action: "APPLY_CHANGES",
            description: "Apply requested changes",
            details: JSON.stringify(intent.params),
          },
          {
            order: 3,
            action: "VALIDATE",
            description: "Validate changes",
            details: "Ensure consistency",
          }
        );
        break;

      case "list":
        steps.push({
          order: 1,
          action: "FETCH_RESOURCES",
          description: `List all ${intent.target}s`,
          details: "Query database/API",
        });
        break;

      case "delete":
        status = "pending_approval";
        steps.push(
          {
            order: 1,
            action: "CONFIRM_DELETE",
            description: `Confirm deletion of ${intent.target}`,
            details: "Destructive operation - requires approval",
          },
          {
            order: 2,
            action: "DELETE_RESOURCE",
            description: "Delete resource",
            details: "Remove from system",
          },
          {
            order: 3,
            action: "BACKUP",
            description: "Archive backup",
            details: "Store deleted state for recovery",
          }
        );
        break;

      case "deploy":
        status = "pending_approval";
        steps.push(
          {
            order: 1,
            action: "BUILD",
            description: "Build application",
            details: "Compile and package",
          },
          {
            order: 2,
            action: "TEST",
            description: "Run test suite",
            details: "Validate build integrity",
          },
          {
            order: 3,
            action: "DEPLOY",
            description: "Deploy to production",
            details: (intent.params.environment as string) || "staging",
          }
        );
        break;

      case "schedule":
        steps.push({
          order: 1,
          action: "SCHEDULE",
          description: "Schedule execution",
          details: `Date: ${intent.params.date}, Time: ${intent.params.time || "auto"}`,
        });
        break;

      case "clarify":
        steps.push({
          order: 1,
          action: "ASK_USER",
          description: "Clarify intent",
          details: intent.reasoning,
        });
        break;

      default:
        steps.push({
          order: 1,
          action: "UNKNOWN",
          description: "Unknown action",
          details: intent.action,
        });
    }

    const estimatedTime = steps.length * 2; // 2 segundos por step

    return { steps, status, estimatedTime };
  }

  /**
   * Gera um resumo legível da execução planejada
   */
  private generateSummary(
    intent: ParsedIntent,
    routing: RoutingResult | null,
    plan: ExecutionPlan
  ): string {
    const lines: string[] = [];

    lines.push(`Action: ${intent.action.toUpperCase()}`);
    lines.push(`Target: ${intent.target}`);
    lines.push(`Status: ${plan.status.toUpperCase()}`);
    lines.push(
      `Confidence: ${(intent.confidence * 100).toFixed(0)}% - ${intent.action === "clarify" ? "needs clarification" : "proceed"}`
    );

    if (routing) {
      lines.push(`Agent: ${routing.agent.name}`);
      lines.push(`Tier: ${routing.agent.tier}`);
    }

    lines.push(`Steps: ${plan.steps.length}`);
    lines.push(`Est. Time: ${plan.estimatedTime}s`);

    return lines.join(" | ");
  }
}

/**
 * Tipos para plano de execução
 */
export interface ExecutionStep {
  order: number;
  action: string;
  description: string;
  details: string;
}

export interface ExecutionPlan {
  steps: ExecutionStep[];
  status: "ready" | "pending_approval" | "blocked";
  estimatedTime: number;
}

/**
 * Exemplo de uso
 */
export async function runIntegrationExample(): Promise<void> {
  const pipeline = new CommandProcessingPipeline();

  const userCommands = [
    "criar um novo agente para saneamento",
    "atualizar a configuração do maestro",
    "executar o workflow de candidaturas",
    "listar todos os agentes disponíveis",
    "deployar para produção",
  ];

  console.log("╔════════════════════════════════════════════════════════╗");
  console.log("║   Intent Parser + Maestro Router Integration Example   ║");
  console.log("╚════════════════════════════════════════════════════════╝");

  for (const command of userCommands) {
    try {
      const result = await pipeline.processUserCommand(command);

      console.log("\n📋 EXECUTION PLAN:");
      console.log("━".repeat(60));

      for (const step of result.executionPlan.steps) {
        console.log(
          `\n  ${step.order}. [${step.action}] ${step.description}`
        );
        console.log(`     └─ ${step.details}`);
      }

      console.log("\n📊 SUMMARY:");
      console.log("━".repeat(60));
      console.log(`  ${result.summary}`);

      if (result.intent.clarifyingQuestions?.length) {
        console.log("\n❓ CLARIFYING QUESTIONS:");
        result.intent.clarifyingQuestions.forEach((q) => {
          console.log(`  • ${q}`);
        });
      }

      console.log("\n" + "═".repeat(60));
    } catch (error) {
      console.error(`Error processing command: ${error}`);
    }
  }
}

/**
 * Exemplo de uso em interativo (requires Node.js readline)
 */
export async function runInteractiveMode(): Promise<void> {
  const pipeline = new CommandProcessingPipeline();

  console.log("\n🤖 Intent Parser Interactive Mode");
  console.log("Type your commands. Type 'exit' to quit.\n");

  // Importar readline dinamicamente para evitar tipo implícito
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const readline = require("readline") as typeof import("readline");
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const askQuestion = (prompt: string): Promise<string> => {
    return new Promise((resolve) => {
      rl.question(prompt, (answer: string) => {
        resolve(answer);
      });
    });
  };

  while (true) {
    const command = await askQuestion("\n> ");

    if (command.toLowerCase() === "exit") {
      rl.close();
      break;
    }

    if (!command.trim()) {
      continue;
    }

    try {
      const result = await pipeline.processUserCommand(command);

      console.log("\n🎯 Processed Intent:");
      console.log(`   Action: ${result.intent.action}`);
      console.log(`   Target: ${result.intent.target}`);
      console.log(`   Confidence: ${(result.intent.confidence * 100).toFixed(0)}%`);

      if (result.routing) {
        console.log(`   Route: ${result.routing.agent.name}`);
      }

      console.log(
        `\n📋 Execution Plan (${result.executionPlan.steps.length} steps):`
      );
      result.executionPlan.steps.forEach((step) => {
        console.log(`   ${step.order}. ${step.action}: ${step.description}`);
      });

      console.log(`\n✨ Summary: ${result.summary}`);
    } catch (error) {
      console.error(`Error: ${error}`);
    }
  }
}
