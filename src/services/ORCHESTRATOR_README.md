# Master Orchestrator — Documentação Completa

## Visão Geral

O **Master Orchestrator** é um componente crítico que coordena o pipeline completo de desenvolvimento de código, desde a intenção inicial até o merge automático. Implementa uma state machine robusta com tratamento de timeouts, retry logic avançado, e rollback automático em caso de falhas críticas.

```
Intent → Code Gen → CI Execution → Code Review → Auto-Merge
   ↓        ↓            ↓              ↓             ↓
Parse    Generate      Test          Review       Merge
```

## Arquitetura

### State Machine (9 Estados)

```
IDLE
  ↓
INTENT_PARSING
  ↓
CODE_GENERATION
  ↓
CI_EXECUTION
  ↓
CODE_REVIEW
  ↓
MERGE_EXECUTION
  ↓
COMPLETED (sucesso)
  ↓
FAILED (erro)
  ↓
ROLLED_BACK (recuperação)
```

### Componentes Principais

1. **Intent Parser**: Interpreta intenção do usuário
2. **Code Generator**: Gera código com Claude
3. **CI Orchestrator**: Executa testes e build
4. **Feedback Engine**: Fornece feedback automático
5. **Code Reviewer**: Revisa código gerado
6. **Auto-Merge**: Realiza merge automático

## Timeout Handling

- **Global Timeout**: 60 minutos máximo (configurável)
- **Fase Timeout**: Rastreia tempo por fase
- **Timeout Warning**: Emite evento de aviso antes do timeout
- **Auto-Rollback**: Faz rollback automático em timeout crítico

```typescript
const orch = createMasterOrchestrator({
  timeoutMinutes: 45,  // 45 minutos (máx 60)
});

// Timeout também pode ser customizado por execução
await orch.orchestrate({
  intent: "...",
  timeoutMinutes: 30,  // Sobrescreve config global
});
```

## Retry Logic

Implementa **exponential backoff** automático:

```typescript
const orch = createMasterOrchestrator({
  retryPolicy: {
    maxAttempts: 3,           // Máximo 3 tentativas
    initialDelayMs: 1000,     // 1 segundo
    maxDelayMs: 30000,        // 30 segundos máximo
    backoffFactor: 2,         // Duplica a cada tentativa
    retryableStates: [
      OrchestratorState.CODE_GENERATION,
      OrchestratorState.CI_EXECUTION,
      OrchestratorState.CODE_REVIEW,
    ],
  },
});
```

**Exemplo de delays**:
- Tentativa 1: 1s delay
- Tentativa 2: 2s delay (1s × 2)
- Tentativa 3: 4s delay (2s × 2)

## Rollback Automático

Ativa rollback em caso de erro crítico:

```typescript
const orch = createMasterOrchestrator({
  autoRollback: true,  // Ativa rollback automático
});
```

Quando ativado, em erro crítico:
1. Identifica commit anterior
2. Emite `ROLLED_BACK` event
3. Executa `git reset --hard [previousCommit]`
4. Retorna resultado com detalhes de rollback

## Telemetria Completa

Rastreia eventos em tempo real:

```typescript
const orch = createMasterOrchestrator({
  telemetryEnabled: true,
});

orch.on("telemetry", (event) => {
  console.log("Evento de telemetria:", {
    type: event.type,
    state: event.state,
    phaseDuration: event.phaseDuration,
    timestamp: event.timestamp,
  });
});
```

### Tipos de Eventos

- `STATE_TRANSITION`: Mudança de estado
- `PHASE_STARTED`: Fase iniciada
- `PHASE_COMPLETED`: Fase completada
- `PHASE_FAILED`: Fase falhou
- `ERROR_OCCURRED`: Erro ocorreu
- `TIMEOUT_WARNING`: Timeout advertência
- `ROLLBACK_INITIATED`: Rollback iniciado
- `RETRY_ATTEMPTED`: Retry tentado
- `METRIC_SNAPSHOT`: Snapshot de métricas

## Exemplos de Uso

### 1. Pipeline Básico

```typescript
import { createMasterOrchestrator } from "./services";

const orch = createMasterOrchestrator();

const result = await orch.orchestrate({
  intent: "Criar novo agente para análise de saneamento",
  segment: "Saneamento",
  userEmail: "user@manta.com",
  timeoutMinutes: 30,
});

console.log("Sucesso:", result.success);
console.log("Estado Final:", result.finalState);
console.log("Duração Total:", result.metrics.totalDurationMs, "ms");
```

### 2. Com Callbacks

```typescript
const orch = createMasterOrchestrator({
  callbacks: {
    onStateChange: async (state) => {
      console.log(`→ Transição para: ${state}`);
    },

    onError: async (error) => {
      console.error(`✗ Erro em ${error.state}: ${error.message}`);
      // Enviar notificação
      await notifySlack(`Pipeline falhou: ${error.message}`);
    },

    onSuccess: async (result) => {
      console.log(`✓ Pipeline completado`);
      // Enviar notificação
      await notifySlack(
        `Pipeline concluído! PR: ${result.artifacts?.pullRequest?.url}`
      );
    },
  },
});

await orch.orchestrate({ intent: "..." });
```

### 3. Com Listeners de Evento

```typescript
const orch = createMasterOrchestrator({
  verbose: true,
});

// Rastrear transições de estado
orch.on("stateChange", (data) => {
  console.log(`${data.previousState} → ${data.newState}`);
});

// Rastrear telemetria
orch.on("telemetry", (event) => {
  if (event.type === "PHASE_COMPLETED") {
    console.log(
      `Fase ${event.state} completada em ${event.phaseDuration}ms`
    );
  }
});

await orch.orchestrate({ intent: "..." });
```

### 4. Retry Policy Customizado

```typescript
const orch = createMasterOrchestrator({
  retryPolicy: {
    maxAttempts: 5,
    initialDelayMs: 500,
    maxDelayMs: 60000,
    backoffFactor: 1.5,
    retryableStates: [
      OrchestratorState.CI_EXECUTION,  // Retry apenas em CI
    ],
  },
});

const result = await orch.orchestrate({
  intent: "Teste com retry customizado",
});

console.log("Retries executados:", result.metrics.retryCount);
```

### 5. Sem Auto-Merge (Requer Aprovação)

```typescript
const orch = createMasterOrchestrator({
  autoMerge: false,  // Aguarda aprovação humana
});

const result = await orch.orchestrate({
  intent: "Criar novo recurso",
  requireApproval: true,
});

// Em resultado de sucesso, aguarda aprovação antes do merge
if (result.success && result.artifacts?.pullRequest) {
  console.log(
    `PR criada: ${result.artifacts.pullRequest.url}`
  );
  console.log("Aguardando aprovação...");
}
```

### 6. Audit Trail Completo

```typescript
const orch = createMasterOrchestrator();
const result = await orch.orchestrate({
  intent: "Teste audit trail",
});

const auditTrail = orch.exportAuditTrail();

console.log("Audit Trail:", {
  startedAt: auditTrail.startedAt,
  endedAt: auditTrail.endedAt,
  totalDurationMs: auditTrail.totalDurationMs,
  finalState: auditTrail.finalState,
  stateTransitions: auditTrail.stateTransitions,
  errors: auditTrail.errors,
  retries: auditTrail.retries,
  telemetryEventCount: auditTrail.telemetryEvents.length,
});

// Exportar para arquivo de auditoria
writeFileSync(
  "audit-trail.json",
  JSON.stringify(auditTrail, null, 2)
);
```

### 7. Métricas em Tempo Real

```typescript
const orch = createMasterOrchestrator();

// Monitorar métricas enquanto executa
let metricsInterval = setInterval(() => {
  const metrics = orch.getMetrics();
  console.log(`Duração até agora: ${metrics.totalDurationMs}ms`);
  console.log(`Estado: ${orch.getCurrentState()}`);
}, 1000);

const result = await orch.orchestrate({
  intent: "Teste métricas",
});

clearInterval(metricsInterval);

console.log("Métricas Finais:", {
  totalDurationMs: result.metrics.totalDurationMs,
  errorCount: result.metrics.errorCount,
  retryCount: result.metrics.retryCount,
  timeoutCount: result.metrics.timeoutCount,
  successRate: result.metrics.successRate,
});
```

## Estrutura de Result

```typescript
interface OrchestratorResult {
  success: boolean;
  finalState: OrchestratorState;
  message: string;

  artifacts?: {
    branch: string;
    pullRequest?: {
      number: number;
      url: string;
    };
    files?: string[];
  };

  metrics: {
    totalDurationMs: number;
    phaseDurations: Record<OrchestratorState, number>;
    errorCount: number;
    retryCount: number;
    timeoutCount: number;
    successRate: number; // 0-1
    startedAt: Date;
    endedAt?: Date;
    finalState: OrchestratorState;
    errors: TrackedError[];
    retries: RetryAttempt[];
  };

  errors: TrackedError[];
  rolledBack: boolean;

  rollbackDetails?: {
    reason: string;
    timestamp: Date;
    restoredCommit: string;
  };
}
```

## Estrutura de Input

```typescript
interface OrchestratorInput {
  intent: string;              // Obrigatório: descrição da tarefa
  segment?: string;            // Segmento vertical (Saneamento, Energia, etc)
  baseBranch?: string;         // Branch base (padrão: main)
  projectRoot?: string;        // Diretório raiz do projeto
  userEmail?: string;          // Email do usuário
  tags?: string[];             // Tags para categorização
  timeoutMinutes?: number;     // Timeout customizado (máx 60)
  requireApproval?: boolean;   // Requer aprovação humana antes do merge
}
```

## Error Handling

### Severidade de Erros

```typescript
enum ErrorSeverity {
  INFO = "info",              // Informativo
  WARNING = "warning",        // Aviso
  ERROR = "error",            // Erro
  CRITICAL = "critical",      // Crítico (dispara rollback)
}
```

### TrackedError

```typescript
interface TrackedError {
  timestamp: Date;
  state: OrchestratorState;
  severity: ErrorSeverity;
  message: string;
  stack?: string;
  context?: Record<string, any>;
  id: string;  // ID único para rastreamento
}
```

## Configuração Avançada

```typescript
const orch = createMasterOrchestrator({
  // Timeout global
  timeoutMinutes: 45,

  // Política de retry
  retryPolicy: {
    maxAttempts: 3,
    initialDelayMs: 1000,
    maxDelayMs: 30000,
    backoffFactor: 2,
    retryableStates: [
      OrchestratorState.CODE_GENERATION,
      OrchestratorState.CI_EXECUTION,
    ],
  },

  // Auto-rollback em erro crítico
  autoRollback: true,

  // Auto-merge (sem aprovação)
  autoMerge: true,

  // Habilitar telemetria
  telemetryEnabled: true,

  // Log verboso
  verbose: false,

  // Callbacks
  callbacks: {
    onStateChange: async (state) => {
      // Handler
    },
    onError: async (error) => {
      // Handler
    },
    onSuccess: async (result) => {
      // Handler
    },
  },
});
```

## Casos de Uso

### 1. CI/CD Pipeline Automático

```typescript
// Webhook do GitHub dispara orchestrador
app.post("/webhook/github", async (req, res) => {
  const { pull_request, action } = req.body;

  if (action === "opened") {
    const orch = createMasterOrchestrator({
      autoMerge: false,  // Aguarda aprovação
      autoRollback: true,
    });

    const result = await orch.orchestrate({
      intent: `Revisar PR #${pull_request.number}: ${pull_request.title}`,
      tags: ["pr-review", pull_request.head.ref],
    });

    // Postar comentário na PR
    await postComment(pull_request.number, {
      status: result.success ? "✓ Aprovada" : "✗ Requer alterações",
      metrics: result.metrics,
    });
  }

  res.json({ ok: true });
});
```

### 2. Code Generation com Timeout Rígido

```typescript
const orch = createMasterOrchestrator({
  timeoutMinutes: 10,  // Gerar código em até 10 minutos
  autoRollback: true,
});

const result = await orch.orchestrate({
  intent: "Gerar agente de análise de saneamento",
  segment: "Saneamento",
  requireApproval: true,  // Revisar antes de merge
});

if (result.success) {
  console.log("✓ Código gerado e testado");
  console.log("PR:", result.artifacts?.pullRequest?.url);
} else if (result.rolledBack) {
  console.log("✗ Falha crítica, rollback executado");
}
```

### 3. Monitoramento com Métricas

```typescript
const orch = createMasterOrchestrator({
  verbose: true,
});

orch.on("telemetry", async (event) => {
  // Enviar para sistema de métricas (Prometheus, DataDog, etc)
  await metrics.record({
    name: "orchestrator.phase",
    value: event.phaseDuration,
    tags: {
      state: event.state,
      type: event.type,
    },
  });
});

const result = await orch.orchestrate({
  intent: "...",
});

// Exportar audit trail
const auditTrail = orch.exportAuditTrail();
await storage.saveAuditTrail(auditTrail);
```

## Performance e Limites

- **Timeout máximo**: 60 minutos
- **Retry máximo**: Configurável (padrão 3)
- **Estados rastreados**: 9
- **Telemetria eventos**: Completa
- **Overhead de timeout**: ~10ms por fase
- **Tamanho de audit trail**: ~50KB por execução

## Testing

```typescript
import { describe, it, expect } from "@jest/globals";
import { createMasterOrchestrator } from "../services";

describe("Master Orchestrator", () => {
  it("deve completar pipeline com sucesso", async () => {
    const orch = createMasterOrchestrator();
    const result = await orch.orchestrate({
      intent: "Teste",
    });

    expect(result.success).toBe(true);
    expect(result.finalState).toBe(OrchestratorState.COMPLETED);
    expect(result.metrics.totalDurationMs).toBeGreaterThan(0);
  });

  it("deve fazer retry em falha transiente", async () => {
    const orch = createMasterOrchestrator({
      retryPolicy: {
        maxAttempts: 2,
        initialDelayMs: 10,
        maxDelayMs: 100,
        backoffFactor: 2,
        retryableStates: [OrchestratorState.CI_EXECUTION],
      },
    });

    const result = await orch.orchestrate({
      intent: "Teste retry",
    });

    expect(result.metrics.retryCount).toBeGreaterThanOrEqual(0);
  });
});
```

## Troubleshooting

### Pipeline Timeout

```typescript
// Aumentar timeout global
const orch = createMasterOrchestrator({
  timeoutMinutes: 60,  // Máximo permitido
});

// Ou customizar por execução
await orch.orchestrate({
  intent: "...",
  timeoutMinutes: 45,
});
```

### Muitos Retries

```typescript
// Reduzir retry
const orch = createMasterOrchestrator({
  retryPolicy: {
    maxAttempts: 1,  // Sem retry
    // ... outros campos
  },
});
```

### Sem Rollback

```typescript
// Desabilitar rollback automático
const orch = createMasterOrchestrator({
  autoRollback: false,
});
```

## Referências

- [State Machine Pattern](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Audit Trail](https://en.wikipedia.org/wiki/Audit_trail)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

## License

MIT — Manta Associados
