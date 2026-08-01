/**
 * SYNC MANAGER — Sincronização Bidirecional
 *
 * Mantém sincronizados:
 * 1. Claude AI → Prompts do usuário
 * 2. Maestro → Decisões de roteamento
 * 3. Cowork → Tasks e comentários
 *
 * Fluxo de sincronização:
 * Claude AI (prompt) → Maestro (route) → Cowork (task) → Claude AI (context)
 * Cowork (update) → Maestro (re-route) → Claude AI (notify)
 */

import { getMaestroRouter } from "./maestro-router";
import {
  create_task,
  list_tasks,
  post_comment,
  TaskPriority,
} from "../adapters/cowork-adapter";

interface SyncRecord {
  id: string;
  timestamp: string;
  source: "claude-ai" | "maestro" | "cowork";
  type: "prompt" | "routing" | "task" | "comment" | "update";
  data: Record<string, unknown>;
  status: "pending" | "syncing" | "synced" | "error";
  error?: string;
}

interface SyncState {
  lastSync: string;
  records: SyncRecord[];
  activePrompts: Map<string, unknown>;
  activeRoutes: Map<string, unknown>;
  activeTasks: Map<string, unknown>;
}

class SyncManager {
  private router = getMaestroRouter();
  private syncState: SyncState = {
    lastSync: new Date().toISOString(),
    records: [],
    activePrompts: new Map(),
    activeRoutes: new Map(),
    activeTasks: new Map(),
  };

  private syncQueue: SyncRecord[] = [];
  private isProcessing = false;

  constructor() {
    console.log("🔄 SyncManager initialized");
    this.startAutoSync();
  }

  /**
   * Registrar prompt vindo do Claude AI
   */
  async registerPromptFromClaudeAI(prompt: string): Promise<string> {
    const syncId = this.generateSyncId();

    const record: SyncRecord = {
      id: syncId,
      timestamp: new Date().toISOString(),
      source: "claude-ai",
      type: "prompt",
      data: { prompt },
      status: "pending",
    };

    this.syncQueue.push(record);
    this.syncState.records.push(record);
    this.syncState.activePrompts.set(syncId, prompt);

    console.log(`📥 Prompt registrado: ${syncId}`);
    console.log(`   "${prompt.substring(0, 60)}..."`);

    await this.processSyncQueue();

    return syncId;
  }

  /**
   * Sincronizar prompt com Maestro
   */
  private async syncPromptWithMaestro(syncId: string, prompt: string) {
    try {
      const record = this.syncState.records.find((r) => r.id === syncId);
      if (!record) return;

      record.status = "syncing";

      const routing = await this.router.route(prompt);

      const routingRecord: SyncRecord = {
        id: this.generateSyncId(),
        timestamp: new Date().toISOString(),
        source: "maestro",
        type: "routing",
        data: {
          promptId: syncId,
          agentName: routing.agent.name,
          agentCode: routing.agent.code,
          score: routing.score,
          confidence: routing.confidence,
          keywords: routing.matchedKeywords,
        },
        status: "synced",
      };

      this.syncState.records.push(routingRecord);
      this.syncState.activeRoutes.set(syncId, routingRecord.data);

      record.status = "synced";
      record.data.routingId = routingRecord.id;

      console.log(`✅ Maestro sincronizado: ${routingRecord.id}`);
      console.log(
        `   Agent: ${routing.agent.name} (Score: ${routing.score.toFixed(2)})`
      );

      // Próxima: sincronizar com Cowork
      await this.syncRoutingWithCowork(syncId, routingRecord.data);
    } catch (error) {
      const record = this.syncState.records.find((r) => r.id === syncId);
      if (record) {
        record.status = "error";
        record.error = error instanceof Error ? error.message : String(error);
      }
      console.error(`❌ Erro sincronizando com Maestro: ${error}`);
    }
  }

  /**
   * Sincronizar roteamento com Cowork
   */
  private async syncRoutingWithCowork(syncId: string, routingData: any) {
    try {
      const prompt = this.syncState.activePrompts.get(syncId);
      if (!prompt) return;

      const taskResponse = await create_task({
        title: `[${routingData.agentCode}] ${(prompt as string).substring(0, 60)}...`,
        description: `
**Prompt Original:**
${prompt}

**Roteamento Maestro:**
- Agent: ${routingData.agentName} (${routingData.agentCode})
- Score: ${routingData.score.toFixed(2)}
- Confidence: ${routingData.confidence}
- Keywords: ${routingData.keywords.join(", ")}

**Status:** Criado automaticamente via SyncManager
**Timestamp:** ${new Date().toISOString()}
**SyncID:** ${syncId}
        `,
        priority:
          routingData.confidence === "high"
            ? TaskPriority.HIGH
            : TaskPriority.MEDIUM,
        labels: [routingData.agentName, "sync-manager", syncId],
        customFields: {
          agent_source: routingData.agentName,
          segment: routingData.segment || "Geral",
        },
      });

      if (taskResponse.success && taskResponse.data) {
        const taskRecord: SyncRecord = {
          id: this.generateSyncId(),
          timestamp: new Date().toISOString(),
          source: "cowork",
          type: "task",
          data: {
            promptId: syncId,
            taskId: taskResponse.data.id,
            taskTitle: taskResponse.data.title,
            taskUrl: `https://cowork.example.com/tasks/${taskResponse.data.id}`,
          },
          status: "synced",
        };

        this.syncState.records.push(taskRecord);
        this.syncState.activeTasks.set(syncId, taskRecord.data);

        console.log(`✅ Cowork sincronizado: ${taskResponse.data.id}`);
        console.log(`   Task: ${taskResponse.data.title}`);

        // Postar comentário com contexto completo
        await post_comment({
          taskId: taskResponse.data.id,
          content: `✅ **Sincronização Maestro Completa**

**Origem:** Claude AI
**Roteamento:** Maestro Router
**Agent:** ${routingData.agentName} (${routingData.agentCode})
**Confidence:** ${routingData.confidence}
**Score:** ${routingData.score.toFixed(2)}
**Keywords Detectadas:** ${routingData.keywords.join(", ")}

**SyncID:** \`${syncId}\`
**Timestamp:** ${new Date().toISOString()}

Este task foi criado automaticamente através da integração:
Claude AI → Maestro Router → Cowork Sync Manager`,
          authorId: "sync-manager-system",
          authorName: "SyncManager",
        });

        console.log(`💬 Comentário postado com contexto de sincronização`);
      }
    } catch (error) {
      console.error(`❌ Erro sincronizando com Cowork: ${error}`);
    }
  }

  /**
   * Registrar atualização vindo do Cowork
   */
  async registerUpdateFromCowork(taskId: string, updateData: any): Promise<void> {
    const syncId = this.generateSyncId();

    const record: SyncRecord = {
      id: syncId,
      timestamp: new Date().toISOString(),
      source: "cowork",
      type: "update",
      data: {
        taskId,
        updateData,
      },
      status: "pending",
    };

    this.syncQueue.push(record);
    this.syncState.records.push(record);

    console.log(`📥 Atualização do Cowork registrada: ${syncId}`);
    console.log(`   Task: ${taskId}`);

    await this.processSyncQueue();
  }

  /**
   * Processar fila de sincronização
   */
  private async processSyncQueue() {
    if (this.isProcessing || this.syncQueue.length === 0) return;

    this.isProcessing = true;

    try {
      while (this.syncQueue.length > 0) {
        const record = this.syncQueue.shift();
        if (!record) break;

        if (record.type === "prompt") {
          const prompt = record.data.prompt as string;
          await this.syncPromptWithMaestro(record.id, prompt);
        } else if (record.type === "update") {
          // Handle Cowork updates
          console.log(`Processing Cowork update: ${record.id}`);
        }

        // Pequeno delay entre sincronizações
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } finally {
      this.isProcessing = false;
      this.syncState.lastSync = new Date().toISOString();
    }
  }

  /**
   * Auto-sincronização periódica
   */
  private startAutoSync() {
    setInterval(async () => {
      try {
        // Verificar se há tasks pendentes no Cowork
        const tasksList = await list_tasks({ limit: 20 });

        if (tasksList.success) {
          const tasks = (tasksList.data as any)?.tasks || [];

          // Sincronizar status de tasks
          for (const task of tasks) {
            const isSynced = this.syncState.records.some(
              (r) => (r.data as any).taskId === task.id
            );

            if (!isSynced) {
              console.log(`🔄 Auto-sync detectou task não sincronizado: ${task.id}`);
            }
          }
        }
      } catch (error) {
        console.error(`❌ Erro em auto-sync: ${error}`);
      }
    }, 30000); // A cada 30 segundos
  }

  /**
   * Obter status da sincronização
   */
  getStatus() {
    const synced = this.syncState.records.filter(
      (r) => r.status === "synced"
    ).length;
    const pending = this.syncQueue.length;
    const errors = this.syncState.records.filter(
      (r) => r.status === "error"
    ).length;

    return {
      lastSync: this.syncState.lastSync,
      totalRecords: this.syncState.records.length,
      synced,
      pending,
      errors,
      activePrompts: this.syncState.activePrompts.size,
      activeRoutes: this.syncState.activeRoutes.size,
      activeTasks: this.syncState.activeTasks.size,
    };
  }

  /**
   * Obter histórico de sincronização
   */
  getHistory(limit: number = 20) {
    return this.syncState.records
      .slice(-limit)
      .reverse()
      .map((r) => ({
        id: r.id,
        timestamp: r.timestamp,
        source: r.source,
        type: r.type,
        status: r.status,
        error: r.error,
      }));
  }

  /**
   * Gerar ID único para sincronização
   */
  private generateSyncId(): string {
    return `sync-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}

// Export singleton
export const syncManager = new SyncManager();
export { SyncManager, SyncRecord, SyncState };
