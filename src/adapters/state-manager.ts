/**
 * State Manager — CRDT Light (Last-Write-Wins)
 * Gerencia estado distribuído com versionamento, sincronização Supabase e retry exponencial
 */

import { createClient, SupabaseClient } from "@supabase/supabase-js";

// ============================================================================
// TIPOS E INTERFACES
// ============================================================================

export type OriginPlatform = "web" | "mobile" | "agent" | "backend" | "sync";

export interface VersionedValue<T> {
  value: T;
  timestamp: number; // milliseconds
  origin_platform: OriginPlatform;
  revision: number;
}

export interface StateSnapshot {
  [key: string]: VersionedValue<any>;
}

export interface SyncConflict {
  key: string;
  local: VersionedValue<any>;
  remote: VersionedValue<any>;
  resolution: "local" | "remote";
}

export interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number; // 1000ms
  delays: number[]; // [1000, 5000, 30000]
}

export interface StateManagerConfig {
  supabaseUrl: string;
  supabaseKey: string;
  tableName: string;
  origin: OriginPlatform;
  retryConfig?: RetryConfig;
}

// ============================================================================
// STATE MANAGER CLASS
// ============================================================================

export class StateManager {
  private localState: StateSnapshot = {};
  private supabase: SupabaseClient | null = null;
  private config: StateManagerConfig;
  private retryConfig: RetryConfig;
  private syncInProgress = false;
  private lastSyncTimestamp = 0;

  constructor(config: StateManagerConfig) {
    this.config = config;
    this.retryConfig = config.retryConfig || {
      maxRetries: 3,
      initialDelayMs: 1000,
      delays: [1000, 5000, 30000],
    };

    // Inicializar cliente Supabase se credenciais disponíveis
    if (config.supabaseUrl && config.supabaseKey) {
      this.supabase = createClient(config.supabaseUrl, config.supabaseKey);
    }
  }

  /**
   * GET STATE — Retorna valor atual com versionamento
   */
  public get_state(key: string): VersionedValue<any> | undefined {
    return this.localState[key];
  }

  /**
   * GET STATE VALUE — Retorna apenas o valor (unwrap)
   */
  public get_state_value<T>(key: string): T | undefined {
    return this.localState[key]?.value;
  }

  /**
   * SET STATE — Atualiza estado local com Last-Write-Wins
   */
  public set_state<T>(key: string, value: T): VersionedValue<T> {
    const now = Date.now();
    const currentRevision = this.localState[key]?.revision || 0;

    const versioned: VersionedValue<T> = {
      value,
      timestamp: now,
      origin_platform: this.config.origin,
      revision: currentRevision + 1,
    };

    this.localState[key] = versioned;
    return versioned;
  }

  /**
   * GET SNAPSHOT — Retorna todo o estado local
   */
  public get_snapshot(): StateSnapshot {
    return { ...this.localState };
  }

  /**
   * MERGE STATE — Aplica Last-Write-Wins (retorna conflitos resolvidos)
   */
  public merge_state(remoteSnapshot: StateSnapshot): SyncConflict[] {
    const conflicts: SyncConflict[] = [];

    for (const [key, remoteVersioned] of Object.entries(remoteSnapshot)) {
      const localVersioned = this.localState[key];

      if (!localVersioned) {
        // Remoto vence se não existe localmente
        this.localState[key] = remoteVersioned;
      } else if (remoteVersioned.timestamp > localVersioned.timestamp) {
        // Last-Write-Wins: timestamp mais recente
        conflicts.push({
          key,
          local: localVersioned,
          remote: remoteVersioned,
          resolution: "remote",
        });
        this.localState[key] = remoteVersioned;
      } else if (remoteVersioned.timestamp === localVersioned.timestamp) {
        // Tie-break por revision, depois por origin_platform
        if (remoteVersioned.revision > localVersioned.revision) {
          conflicts.push({
            key,
            local: localVersioned,
            remote: remoteVersioned,
            resolution: "remote",
          });
          this.localState[key] = remoteVersioned;
        } else {
          // Local vence ou mantém igualdade
          conflicts.push({
            key,
            local: localVersioned,
            remote: remoteVersioned,
            resolution: "local",
          });
        }
      }
    }

    return conflicts;
  }

  /**
   * SYNC WITH SUPABASE — Sincroniza estado local com Supabase
   * - Implementa retry exponencial
   * - Resolve conflitos via Last-Write-Wins
   */
  public async sync_with_supabase(): Promise<{
    success: boolean;
    conflicts: SyncConflict[];
    error?: Error;
  }> {
    if (!this.supabase) {
      return {
        success: false,
        conflicts: [],
        error: new Error("Supabase client not initialized"),
      };
    }

    if (this.syncInProgress) {
      return {
        success: false,
        conflicts: [],
        error: new Error("Sync already in progress"),
      };
    }

    this.syncInProgress = true;

    try {
      const { success, conflicts, error } = await this._syncWithRetry();
      this.syncInProgress = false;
      return { success, conflicts, error };
    } catch (err) {
      this.syncInProgress = false;
      return {
        success: false,
        conflicts: [],
        error: err instanceof Error ? err : new Error(String(err)),
      };
    }
  }

  /**
   * SYNC WITH RETRY — implementa retry exponencial
   */
  private async _syncWithRetry(): Promise<{
    success: boolean;
    conflicts: SyncConflict[];
    error?: Error;
  }> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        if (attempt > 0) {
          const delayMs = this.retryConfig.delays[attempt - 1] || 30000;
          await this._delay(delayMs);
        }

        const result = await this._performSync();
        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));

        if (attempt === this.retryConfig.maxRetries) {
          return {
            success: false,
            conflicts: [],
            error: lastError,
          };
        }
      }
    }

    return {
      success: false,
      conflicts: [],
      error:
        lastError ||
        new Error("Sync failed after all retry attempts without error"),
    };
  }

  /**
   * PERFORM SYNC — executa a sincronização propriamente
   */
  private async _performSync(): Promise<{
    success: boolean;
    conflicts: SyncConflict[];
    error?: Error;
  }> {
    if (!this.supabase) {
      throw new Error("Supabase client not initialized");
    }

    // Buscar estado remoto
    const { data: remoteData, error: fetchError } = await this.supabase
      .from(this.config.tableName)
      .select("*")
      .order("timestamp", { ascending: false });

    if (fetchError) {
      throw new Error(`Failed to fetch remote state: ${fetchError.message}`);
    }

    // Construir snapshot remoto
    const remoteSnapshot: StateSnapshot = {};
    if (remoteData && Array.isArray(remoteData)) {
      for (const row of remoteData) {
        const key = row.key || row.id;
        remoteSnapshot[key] = {
          value: row.value,
          timestamp: new Date(row.timestamp).getTime(),
          origin_platform: row.origin_platform,
          revision: row.revision,
        };
      }
    }

    // Resolver conflitos via Last-Write-Wins
    const conflicts = this.merge_state(remoteSnapshot);

    // Fazer upload do estado local (sobrescrever remotamente)
    const uploadPromises = Object.entries(this.localState).map(
      ([key, versioned]) =>
        this.supabase!.from(this.config.tableName).upsert(
          {
            key,
            value: versioned.value,
            timestamp: new Date(versioned.timestamp).toISOString(),
            origin_platform: versioned.origin_platform,
            revision: versioned.revision,
          },
          { onConflict: "key" }
        )
    );

    const uploadResults = await Promise.all(uploadPromises);

    // Verificar se houve erros no upload
    for (const result of uploadResults) {
      if (result.error) {
        throw new Error(`Failed to upload state: ${result.error.message}`);
      }
    }

    this.lastSyncTimestamp = Date.now();

    return {
      success: true,
      conflicts,
    };
  }

  /**
   * DELETE STATE — Remove chave do estado local
   */
  public delete_state(key: string): void {
    delete this.localState[key];
  }

  /**
   * CLEAR STATE — Limpa todo o estado local
   */
  public clear_state(): void {
    this.localState = {};
  }

  /**
   * GET LAST SYNC TIMESTAMP — Retorna timestamp da última sincronização
   */
  public get_last_sync_timestamp(): number {
    return this.lastSyncTimestamp;
  }

  /**
   * HELPER: Delay para retry
   */
  private _delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * EXPORT STATE — Serializa estado para JSON
   */
  public export_state(): string {
    return JSON.stringify(this.localState, null, 2);
  }

  /**
   * IMPORT STATE — Deserializa estado de JSON
   */
  public import_state(json: string): void {
    try {
      const imported = JSON.parse(json);
      this.localState = imported;
    } catch (err) {
      throw new Error(`Failed to import state: ${String(err)}`);
    }
  }

  /**
   * GET STATISTICS — Retorna estatísticas do estado
   */
  public get_statistics(): {
    total_keys: number;
    total_size_bytes: number;
    last_sync_timestamp: number;
    sync_in_progress: boolean;
  } {
    return {
      total_keys: Object.keys(this.localState).length,
      total_size_bytes: JSON.stringify(this.localState).length,
      last_sync_timestamp: this.lastSyncTimestamp,
      sync_in_progress: this.syncInProgress,
    };
  }
}

// ============================================================================
// FACTORY FUNCTION
// ============================================================================

export function createStateManager(config: StateManagerConfig): StateManager {
  return new StateManager(config);
}

// ============================================================================
// TIPOS UTILITÁRIOS
// ============================================================================

export type StateManagerInstance = StateManager;
