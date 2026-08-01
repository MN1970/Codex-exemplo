/**
 * MCP Server — Model Context Protocol
 * Expõe ferramentas para Claude AI acessar Maestro, Cowork e Sync Manager
 */

import express from "express";
import { getMaestroRouter } from "./services/maestro-router";
import { syncManager } from "./services/sync-manager";
import {
  create_task,
  list_tasks,
  post_comment,
  TaskPriority,
  TaskStatus,
} from "./adapters/cowork-adapter";

const app = express();
app.use(express.json());

// Porta para MCP server
const MCP_PORT = process.env.MCP_PORT || 3001;

/**
 * MCP Tool 1: Route with Maestro
 * Use: Roteia um prompt para o agente correto
 */
app.post("/mcp/route", async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    const router = getMaestroRouter();
    const routing = await router.route(prompt);

    res.json({
      agent: {
        name: routing.agent.name,
        code: routing.agent.code,
        segment: routing.agent.segment,
      },
      score: routing.score,
      confidence: routing.confidence,
      keywords: routing.matchedKeywords,
    });
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * MCP Tool 2: Sync Prompt from Claude AI
 * Use: Registra um prompt do Claude AI para sincronizar com Maestro e Cowork
 */
app.post("/mcp/sync-prompt", async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "Prompt is required" });
    }

    const syncId = await syncManager.registerPromptFromClaudeAI(prompt);

    res.json({
      syncId,
      status: "pending",
      message: "Prompt registrado. Sincronizando com Maestro e Cowork...",
    });
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * MCP Tool 3: List Maestro Agents
 * Use: Lista todos os 20 agentes Manta disponíveis
 */
app.get("/mcp/agents", async (req, res) => {
  try {
    const agents = [
      {
        code: "Manta 00",
        name: "maestro",
        tier: "Haiku→Sonnet",
      },
      {
        code: "Manta 03-S1",
        name: "agente-infraestrutura",
        segment: "Rodovias",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S2",
        name: "agente-infraestrutura",
        segment: "OAE (Pontes)",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S3",
        name: "agente-infraestrutura",
        segment: "Ferrovia",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S4",
        name: "agente-infraestrutura",
        segment: "Metrô",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S6",
        name: "agente-portos",
        segment: "Portos",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S7",
        name: "agente-aeroportos",
        segment: "Aeroportos",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S8",
        name: "agente-saneamento",
        segment: "Saneamento",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S9",
        name: "agente-energia",
        segment: "Energia",
        tier: "Sonnet",
      },
      {
        code: "Manta 03-S10",
        name: "agente-barragens",
        segment: "Barragens",
        tier: "Sonnet",
      },
    ];

    res.json({
      agents,
      total: agents.length,
      status: "operational",
    });
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * MCP Tool 4: Create Cowork Task
 * Use: Cria uma task no Cowork com contexto Maestro
 */
app.post("/mcp/create-task", async (req, res) => {
  try {
    const { title, description, agent_source, segment, priority, tags } =
      req.body;

    const priorityEnum =
      priority === "high"
        ? TaskPriority.HIGH
        : priority === "low"
          ? TaskPriority.LOW
          : TaskPriority.MEDIUM;

    const response = await create_task({
      title,
      description,
      priority: priorityEnum,
      labels: tags || [],
      customFields: {
        agent_source,
        segment,
      },
    });

    res.json(response);
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * MCP Tool 5: List Cowork Tasks
 * Use: Lista tasks do Cowork com filtros
 */
app.get("/mcp/tasks", async (req, res) => {
  try {
    const { limit, agent_source, status } = req.query;

    const statusEnum = status
      ? (status === "open"
          ? TaskStatus.OPEN
          : status === "in_progress"
            ? TaskStatus.IN_PROGRESS
            : status === "done"
              ? TaskStatus.DONE
              : undefined)
      : undefined;

    const response = await list_tasks({
      limit: parseInt(limit as string) || 20,
      status: statusEnum,
    });

    res.json(response);
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * MCP Tool 6: Post Comment to Task
 * Use: Posta um comentário em uma task do Cowork
 */
app.post("/mcp/post-comment", async (req, res) => {
  try {
    const { taskId, content, authorId, authorName } = req.body;

    const response = await post_comment({
      taskId,
      content,
      authorId: authorId || "mcp-api",
      authorName: authorName || "MCP API",
    });

    res.json(response);
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * Webhook: Receber atualizações do Cowork
 * Use: Cowork envia atualizações de tasks via POST
 */
app.post("/webhooks/cowork-update", async (req, res) => {
  try {
    const { taskId, updateData } = req.body;

    console.log(`\n🔔 Webhook recebido do Cowork: ${taskId}`);

    await syncManager.registerUpdateFromCowork(taskId, updateData);

    res.json({
      status: "received",
      message: "Atualização do Cowork registrada",
    });
  } catch (error) {
    res.status(500).json({
      error: error instanceof Error ? error.message : String(error),
    });
  }
});

/**
 * Status: Visualizar status da sincronização
 */
app.get("/mcp/sync-status", (req, res) => {
  const status = syncManager.getStatus();
  const history = syncManager.getHistory(10);

  res.json({
    status,
    recentActivity: history,
  });
});

/**
 * Health check
 */
app.get("/health", (req, res) => {
  res.json({
    status: "operational",
    service: "MCP Maestro Sync Server",
    version: "1.0.0",
    features: [
      "maestro-routing",
      "claude-ai-sync",
      "cowork-integration",
      "bidirectional-sync",
    ],
  });
});

/**
 * Iniciar servidor
 */
app.listen(MCP_PORT, () => {
  console.log("\n🚀 MCP Server iniciado");
  console.log("=".repeat(70));
  console.log(`📡 Escutando em http://localhost:${MCP_PORT}`);
  console.log("\n📚 Endpoints disponíveis:\n");
  console.log(`   POST /mcp/route                  → Rotear prompt com Maestro`);
  console.log(`   POST /mcp/sync-prompt            → Sincronizar prompt Claude AI`);
  console.log(`   GET  /mcp/agents                 → Listar 20 agentes Manta`);
  console.log(`   POST /mcp/create-task            → Criar task no Cowork`);
  console.log(`   GET  /mcp/tasks                  → Listar tasks do Cowork`);
  console.log(`   POST /mcp/post-comment           → Postar comentário em task`);
  console.log(`   POST /webhooks/cowork-update     → Webhook de atualização Cowork`);
  console.log(`   GET  /mcp/sync-status            → Ver status de sincronização`);
  console.log(`   GET  /health                     → Health check\n`);
  console.log("=".repeat(70));
  console.log("\n✨ Sistema pronto para sincronizar Claude AI ↔ Maestro ↔ Cowork");
});

export default app;
