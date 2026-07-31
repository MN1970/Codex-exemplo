# CI/CD Orchestrator Service

Serviço inteligente de orquestração de pipelines GitHub Actions com polling automático, parsing de resultados e tratamento robusto de erros e timeouts.

## Visão Geral

O **CIOrchestratorService** automatiza o disparo e monitoramento de workflows GitHub Actions com:

- ✅ Disparo de workflows GitHub Actions via API REST
- ✅ Polling automático a cada 30 segundos (configurável)
- ✅ Timeout máximo de 5 minutos (configurável)
- ✅ Parsing inteligente de output (testes, cobertura, lint)
- ✅ Retorno estruturado de pass/fail + detalhes
- ✅ Tratamento robusto de erros e timeouts
- ✅ Métricas e observability agregadas
- ✅ Integração completa com GitHub REST API

## Instalação

O serviço está localizado em `src/services/ci-orchestrator.ts` e já está exportado via `src/services/index.ts`.

### Variáveis de Ambiente Necessárias

```bash
# .env
GITHUB_TOKEN=ghp_xxxxx              # Token de acesso pessoal do GitHub
GITHUB_OWNER=manta-associados       # Proprietário do repositório
GITHUB_REPO=codex-exemplo           # Nome do repositório
```

## Uso Básico

### 1. Criar uma instância

```typescript
import { createCIOrchestratorService } from "./services";

const orchestrator = createCIOrchestratorService({
  githubToken: process.env.GITHUB_TOKEN,
  owner: "manta-associados",
  repo: "codex-exemplo",
  workflowId: "ci.yml",              // opcional, pode ser passado depois
  pollingIntervalMs: 30000,           // padrão: 30s
  maxWaitMs: 300000,                  // padrão: 5min (300s)
});
```

### 2. Executar workflow completo (trigger + monitor)

```typescript
const result = await orchestrator.executeWorkflow(
  "ci.yml",                           // workflow ID ou filename
  "main",                             // branch (padrão: main)
  { debug: "true" }                   // inputs opcionais
);

console.log(result.status);           // "success" ou "failure"
console.log(result.buildOutput.testResults);
console.log(result.buildOutput.coverage);
```

### 3. Disparar workflow manualmente

```typescript
const runId = await orchestrator.triggerWorkflow(
  "ci.yml",
  "develop",
  { environment: "staging" }
);

console.log("Workflow disparado com ID:", runId);
```

### 4. Monitorar execução

```typescript
const result = await orchestrator.monitorWorkflowRun(
  runId,
  "ci.yml"
);

if (result.status === "success") {
  console.log("✅ Workflow passou!");
  console.log(`Cobertura: ${result.buildOutput.coverage?.lines}%`);
} else {
  console.error("❌ Workflow falhou");
  console.error("Erro:", result.error);
}
```

## Estrutura de Resposta

### OrchestrationResult

```typescript
{
  workflowRunId: 12345,
  status: "success" | "failure",
  workflowStatus: WorkflowRunStatus,
  conclusion: WorkflowConclusion,
  buildOutput: {
    logs: string[],
    testResults?: {
      name: string,
      passed: number,
      failed: number,
      skipped: number,
      duration: number
    },
    coverage?: {
      lines: number,          // %
      statements: number,     // %
      functions: number,      // %
      branches: number        // %
    },
    lintErrors?: [
      {
        file: string,
        line: number,
        column: number,
        message: string,
        rule?: string,
        severity: "error" | "warning"
      }
    ],
    duration: number          // ms
  },
  duration: number,           // tempo total em ms
  timestamp: Date,
  error?: string              // se houver erro
}
```

## Enums

### WorkflowRunStatus

- `QUEUED` - Na fila, aguardando execução
- `IN_PROGRESS` - Em execução
- `COMPLETED` - Completado (sucesso ou falha)
- `FAILED` - Falha direta
- `CANCELLED` - Cancelado
- `TIMED_OUT` - Excedeu timeout

### WorkflowConclusion

- `SUCCESS` - Sucesso (todos os jobs passaram)
- `FAILURE` - Falha (pelo menos um job falhou)
- `NEUTRAL` - Conclusão neutra
- `CANCELLED` - Cancelado
- `TIMED_OUT` - Timeout
- `ACTION_REQUIRED` - Requer ação

## Exemplos de Uso

### Exemplo 1: Verificar se pode fazer deploy

```typescript
async function canDeploy(): Promise<boolean> {
  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN,
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  const result = await orchestrator.executeWorkflow("ci.yml");

  return (
    result.status === "success" &&
    (result.buildOutput.testResults?.failed ?? 0) === 0 &&
    (result.buildOutput.coverage?.lines ?? 0) >= 80
  );
}
```

### Exemplo 2: Deploy automático com notificações

```typescript
async function deployIfPassed() {
  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN,
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  // Executa testes
  const testResult = await orchestrator.executeWorkflow("ci.yml");

  if (testResult.status === "success") {
    console.log("✅ Testes passaram! Iniciando deploy...");
    
    // Dispara deploy
    const deployResult = await orchestrator.executeWorkflow(
      "deploy.yml",
      "main",
      { environment: "production" }
    );

    if (deployResult.status === "success") {
      console.log("✅ Deploy concluído com sucesso!");
      // await notificationService.sendSuccess("Deploy realizado");
    } else {
      console.error("❌ Deploy falhou!");
      // await notificationService.sendError("Deploy falhou", deployResult);
    }
  } else {
    console.error("❌ Testes falharam! Deploy cancelado.");
    
    if (testResult.buildOutput.testResults) {
      console.log(
        `Testes: ${testResult.buildOutput.testResults.failed} falhas`
      );
    }

    if (testResult.buildOutput.lintErrors?.length) {
      console.log(
        `Lint: ${testResult.buildOutput.lintErrors.length} erros`
      );
    }
  }
}
```

### Exemplo 3: Monitoramento com timeouts personalizados

```typescript
async function deployWithCustomTimeout() {
  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN,
    owner: "manta-associados",
    repo: "codex-exemplo",
    pollingIntervalMs: 10000,   // Poll a cada 10s
    maxWaitMs: 600000,          // Timeout de 10 minutos
  });

  try {
    const result = await orchestrator.executeWorkflow("long-deploy.yml");

    if (result.workflowStatus === "timed_out") {
      console.log("Workflow excedeu timeout configurado");
      console.log("Verifique o status manualmente em: https://github.com/...");
    }
  } catch (error) {
    console.error("Erro ao executar workflow:", error);
  }
}
```

### Exemplo 4: Análise de cobertura

```typescript
async function checkCoverageThreshold() {
  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN,
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  const result = await orchestrator.executeWorkflow("ci.yml");
  const coverage = result.buildOutput.coverage;

  if (!coverage) {
    console.log("Nenhuma métrica de cobertura disponível");
    return false;
  }

  const MINIMUM_COVERAGE = 80;
  const metrics = {
    lines: coverage.lines >= MINIMUM_COVERAGE,
    statements: coverage.statements >= MINIMUM_COVERAGE,
    functions: coverage.functions >= MINIMUM_COVERAGE,
    branches: coverage.branches >= MINIMUM_COVERAGE,
  };

  console.log("Verificação de Cobertura:");
  console.log(`  Linhas:      ${coverage.lines}% ${metrics.lines ? "✅" : "❌"}`);
  console.log(`  Statements:  ${coverage.statements}% ${metrics.statements ? "✅" : "❌"}`);
  console.log(`  Functions:   ${coverage.functions}% ${metrics.functions ? "✅" : "❌"}`);
  console.log(`  Branches:    ${coverage.branches}% ${metrics.branches ? "✅" : "❌"}`);

  return Object.values(metrics).every((m) => m);
}
```

### Exemplo 5: Relatório de qualidade

```typescript
async function generateQualityReport() {
  const orchestrator = createCIOrchestratorService({
    githubToken: process.env.GITHUB_TOKEN,
    owner: "manta-associados",
    repo: "codex-exemplo",
  });

  const result = await orchestrator.executeWorkflow("ci.yml");

  const report = {
    timestamp: result.timestamp,
    workflow: {
      id: result.workflowRunId,
      status: result.status,
      conclusion: result.conclusion,
      duration: `${(result.duration / 1000).toFixed(2)}s`,
    },
    tests: {
      passed: result.buildOutput.testResults?.passed ?? 0,
      failed: result.buildOutput.testResults?.failed ?? 0,
      skipped: result.buildOutput.testResults?.skipped ?? 0,
      passRate: `${(
        ((result.buildOutput.testResults?.passed ?? 0) /
          ((result.buildOutput.testResults?.passed ?? 0) +
            (result.buildOutput.testResults?.failed ?? 0))) *
        100
      ).toFixed(2)}%`,
    },
    coverage: {
      lines: `${result.buildOutput.coverage?.lines ?? 0}%`,
      statements: `${result.buildOutput.coverage?.statements ?? 0}%`,
      functions: `${result.buildOutput.coverage?.functions ?? 0}%`,
      branches: `${result.buildOutput.coverage?.branches ?? 0}%`,
    },
    quality: {
      lintErrors: result.buildOutput.lintErrors?.length ?? 0,
      canDeploy:
        result.status === "success" &&
        (result.buildOutput.coverage?.lines ?? 0) >= 80 &&
        (result.buildOutput.testResults?.failed ?? 0) === 0,
    },
  };

  console.log(JSON.stringify(report, null, 2));
  return report;
}
```

## Parsing de Output

O serviço tenta fazer parsing automático dos seguintes formatos:

### Test Results

Detecta padrões como:
- `Tests: 42 passed, 0 failed, 2 skipped`
- JSON com `numPassedTests`, `numFailedTests`
- Saída do Jest

### Coverage

Detecta:
- `Lines: 85.5% | Statements: 85.0% | Functions: 90.2% | Branches: 80.1%`
- Formatos alternativos de cobertura (Nyc, Istanbul, etc)

### Lint Errors

Detecta:
- ESLint: `file.ts:42:10: error - Message (rule-name)`
- Outros padrões de linter

## Polling e Timeout

- **Intervalo de polling padrão**: 30 segundos
- **Timeout máximo padrão**: 5 minutos
- **Mínimo de intervalo**: 5 segundos (limite do GitHub API rate)
- **Máximo de tentativas**: calculado com base em `maxWaitMs / pollingIntervalMs`

## Métricas

O serviço rastreia:

```typescript
{
  timestamp: Date,
  totalWorkflowsTriggered: number,
  successCount: number,
  failureCount: number,
  timeoutCount: number,
  averageDurationMs: number,
  averageTestPassRate: number,  // 0-1
  averageCoverage: {
    lines: number,              // %
    statements: number,         // %
    functions: number,          // %
    branches: number            // %
  }
}
```

### Acessar métricas

```typescript
const metrics = orchestrator.getMetrics();
console.log("Taxa de sucesso:", 
  (metrics.successCount / metrics.totalWorkflowsTriggered * 100).toFixed(2) + "%"
);

// Reset de métricas
orchestrator.resetMetrics();
```

## Tratamento de Erros

### Erros Possíveis

1. **Workflow não encontrado** (422)
   - Verificar se `workflowId` está correto
   - Verificar se o arquivo existe no repositório

2. **Token inválido** (401)
   - Verificar `GITHUB_TOKEN`
   - Verificar se token tem permissão no repositório

3. **Timeout**
   - Aumentar `maxWaitMs` se necessário
   - Verificar status manual no GitHub Actions

4. **Logs expirados** (410)
   - GitHub remove logs após 90 dias
   - Serviço retorna "[Logs expired]"

### Tratamento Recomendado

```typescript
try {
  const result = await orchestrator.executeWorkflow("ci.yml");
  
  if (result.status === "failure") {
    if (result.error?.includes("timed out")) {
      console.error("Workflow excedeu timeout");
      // Reconfigurar com maxWaitMs maior
    } else if (result.error?.includes("not found")) {
      console.error("Workflow ou branch não encontrado");
    } else {
      console.error("Workflow falhou:", result.error);
      // Analisar buildOutput.lintErrors, testResults, etc
    }
  }
} catch (error) {
  if (error instanceof Error) {
    if (error.message.includes("Network")) {
      console.error("Erro de conexão com GitHub API");
    } else {
      console.error("Erro inesperado:", error);
    }
  }
}
```

## Integração com Serviços Manta

### Com o Sync Queue

```typescript
import { SyncQueueManager } from "./sync-queue";
import { createCIOrchestratorService } from "./ci-orchestrator";

const queue = new SyncQueueManager();
const orchestrator = createCIOrchestratorService({ /* config */ });

queue.onProcess(async (item) => {
  const result = await orchestrator.executeWorkflow(item.data.workflowId);
  if (result.status === "success") {
    // Próximo passo no pipeline
  }
});
```

### Com Notifications

```typescript
import { getNotifier } from "./notifications";
import { createCIOrchestratorService } from "./ci-orchestrator";

const notifier = getNotifier();
const orchestrator = createCIOrchestratorService({ /* config */ });

const result = await orchestrator.executeWorkflow("ci.yml");

await notifier.notify({
  type: result.status === "success" ? "BUILD_SUCCESS" : "BUILD_FAILED",
  priority: result.status === "success" ? "medium" : "high",
  userId: "system",
  data: result,
});
```

## Testes

Executar testes:

```bash
npm test -- src/services/__tests__/ci-orchestrator.test.ts
npm test -- ci-orchestrator.test.ts --coverage
```

Testes cobrem:
- ✅ Disparo de workflows
- ✅ Monitoramento de execução
- ✅ Parsing de resultados
- ✅ Timeout handling
- ✅ Tratamento de erros
- ✅ Métricas

## Performance

- **Overhead de polling**: ~100ms por tentativa
- **Overhead de parsing**: ~50ms por job
- **Latência média**: 30-60 segundos (incluindo polling initial)
- **Limite de rate**: GitHub API permite 5000 requisições/hora

## Roadmap

- [ ] Support para GitLab CI
- [ ] Webhook-based monitoring (vs polling)
- [ ] Caching de resultados
- [ ] Integração com Supabase para persistência
- [ ] Dashboard web de workflows
- [ ] Retry policy para workflows falhados
- [ ] Artifact download/management

## Troubleshooting

### Workflow não dispara

```
Error: Workflow not found or invalid branch
```

**Solução**: Verificar:
- Nome do workflow (`.github/workflows/ci.yml`)
- Existência da branch
- Sintaxe do workflow file

### Timeout frequente

```
Workflow execution timed out after max wait time
```

**Solução**:
```typescript
const orchestrator = createCIOrchestratorService({
  ...config,
  maxWaitMs: 600000,  // Aumentar para 10 minutos
  pollingIntervalMs: 60000  // Aumentar para 1 minuto
});
```

### Token inválido

```
Error: Authorization header must be in the format "Authorization: token <token>"
```

**Solução**: Verificar `GITHUB_TOKEN` e permissões no repositório

## Suporte

Para problemas ou dúvidas:
1. Verificar [GitHub API Docs](https://docs.github.com/en/rest/actions)
2. Consultar testes em `__tests__/ci-orchestrator.test.ts`
3. Verificar exemplos em `src/examples/ci-orchestrator-integration.ts`
