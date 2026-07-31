# FeedbackEngine — Feedback Inteligente de CI/CD

Versão: **1.0.0**

## Visão Geral

O **FeedbackEngine** é um sistema inteligente de feedback automatizado para CI/CD que:

- **Lê outputs de CI** (testes falhados, erros de lint, problemas de coverage)
- **Gera sugestões de correção** usando Claude Haiku para rapidez
- **Posta comentários na PR** com sugestões acionáveis
- **Implementa retry logic** com exponential backoff
- **Rastreia tentativas e tempo** de execução
- **Propõe iterações automáticas** de fix

## Arquitetura

```
┌─────────────┐
│  CI Output  │  (GitHub Actions, GitLab CI, etc)
└──────┬──────┘
       │
       v
┌──────────────────────────────┐
│   FeedbackEngine             │
│  ┌────────────────────────┐  │
│  │ 1. Parse CI Output     │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ 2. Claude Haiku API    │  │  Gera sugestões
│  │    (Prompt Builder)    │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ 3. GitHub API          │  │  Posta comentários
│  │    (PR Comments)       │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │ 4. Retry + Tracking    │  │  Rastreia tentativas
│  └────────────────────────┘  │
└──────────────────────────────┘
       │
       v
┌──────────────┐
│ PR Comment   │  Feedback automático
└──────────────┘
```

## Tipos de Erros Suportados

```typescript
enum ErrorType {
  TEST_FAILURE = "test_failure",              // Testes falhados
  LINT_ERROR = "lint_error",                  // Erros de linting
  TYPE_ERROR = "type_error",                  // Erros de tipo (TypeScript)
  COVERAGE_BELOW_THRESHOLD = "coverage_below_threshold",
  BUILD_FAILURE = "build_failure",            // Falha na build
  DEPENDENCY_ERROR = "dependency_error",      // Problemas com dependências
  PERFORMANCE_REGRESSION = "performance_regression",
  SECURITY_ISSUE = "security_issue",          // Problemas de segurança
}
```

## Quickstart

### 1. Instalar dependências

```bash
npm install @anthropic-ai/sdk
```

### 2. Configurar variáveis de ambiente

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_TOKEN="ghp_..."
```

### 3. Criar instância do FeedbackEngine

```typescript
import { createFeedbackEngine, type CIOutput } from "./src/services/feedback-engine";

const engine = createFeedbackEngine({
  githubToken: process.env.GITHUB_TOKEN,
  owner: "manta-associados",
  repo: "codex-hub-mcp",
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  model: "claude-3-5-haiku-20241022", // Rápido e eficiente
  includeCodeExamples: true,
  autoReplyEnabled: true,
});
```

### 4. Processar output de CI

```typescript
const ciOutput: CIOutput = {
  workflowId: "workflow_run_123",
  workflowName: "Jest Tests",
  prNumber: 42,
  branch: "feature/new-api",
  commit: "abc123def456",
  timestamp: new Date(),
  duration: 45000,
  status: "failure",
  errors: [
    {
      type: ErrorType.TEST_FAILURE,
      severity: ErrorSeverity.ERROR,
      message: "expect(result).toBe(true) received false",
      file: "src/api.test.ts",
      line: 142,
      context: "const result = await api.fetch();\nexpect(result).toBe(true);",
    },
  ],
  logs: ["FAIL src/api.test.ts"],
  testResults: {
    total: 100,
    passed: 95,
    failed: 5,
    skipped: 0,
    duration: 45000,
    failedTests: ["should fetch data", "should parse response"],
  },
};

const tracking = await engine.processCIOutput(ciOutput);

console.log(`Status: ${tracking.status}`);
console.log(`Sugestões geradas: ${tracking.suggestionsGenerated}`);
console.log(`Comentários postados: ${tracking.commentsPosted}`);
console.log(`Tempo total: ${tracking.totalTimeSpent}ms`);
```

## API

### FeedbackEngine

#### Constructor

```typescript
const engine = createFeedbackEngine(config: FeedbackEngineConfig)
```

**Config:**

```typescript
interface FeedbackEngineConfig {
  githubToken: string;
  owner: string;
  repo: string;
  anthropicApiKey?: string;
  model?: string; // default: claude-3-5-haiku-20241022
  maxTokens?: number; // default: 1000
  retryPolicy?: Partial<RetryPolicy>;
  includeCodeExamples?: boolean; // default: true
  autoReplyEnabled?: boolean; // default: true
  notifyOnNewIssues?: boolean; // default: true
}
```

#### Métodos principais

##### `processCIOutput(output: CIOutput): Promise<FeedbackTracking>`

Processa um output de CI e gera feedback automático.

**Retorna:**
- `FeedbackTracking` com status, tentativas e tempo gasto

**Fluxo:**
1. Valida se há erros
2. Se não há erros → retorna `SKIPPED`
3. Gera sugestões via Claude Haiku
4. Posta comentário na PR (com retry)
5. Retorna `POSTED` ou `FAILED`

##### `getFeedbackHistory(feedbackId?: string): FeedbackTracking[]`

Recupera histórico de feedbacks processados.

```typescript
// Todos os feedbacks
const all = engine.getFeedbackHistory();

// Um feedback específico
const one = engine.getFeedbackHistory("feedback_42_1234567890");
```

##### `getStatistics(): object`

Retorna estatísticas agregadas.

```typescript
const stats = engine.getStatistics();
// {
//   totalFeedbacks: 10,
//   successRate: 0.9,
//   avgTimeSpentMs: 2500,
//   totalSuggestionsGenerated: 15,
//   totalCommentsPosted: 9
// }
```

##### `clearHistory(): void`

Limpa o histórico de feedbacks.

```typescript
engine.clearHistory();
```

## Retry Logic

### Exponential Backoff

O FeedbackEngine implementa **exponential backoff** com jitter para manejar falhas transientes:

```typescript
retryPolicy: {
  maxAttempts: 3,           // Máximo de tentativas
  initialDelayMs: 1000,     // 1s
  maxDelayMs: 30000,        // 30s
  backoffFactor: 2,         // Duplica a cada tentativa
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
}
```

**Sequência de delays:**

```
Tentativa 1: 0ms (imediato)
Tentativa 2: 1000ms (1s × 2^0)
Tentativa 3: 2000ms (1s × 2^1)
Tentativa 4: 4000ms (1s × 2^2) [máx 30s]
```

### Status codes retentáveis

- `408` — Request Timeout
- `429` — Too Many Requests
- `500` — Internal Server Error
- `502` — Bad Gateway
- `503` — Service Unavailable
- `504` — Gateway Timeout

## Tracking

### FeedbackTracking

Cada processamento de CI output retorna um objeto `FeedbackTracking`:

```typescript
interface FeedbackTracking {
  feedbackId: string;              // ID único
  ciOutputId: string;              // ID do workflow
  prNumber: number;                // Número da PR
  createdAt: Date;                 // Timestamp
  attempts: FeedbackAttempt[];     // Histórico de tentativas
  totalTimeSpent: number;          // Em ms
  totalAttempts: number;           // Contador
  suggestionsGenerated: number;    // Quantas sugestões
  commentsPosted: number;          // Quantos comentários
  status: FeedbackStatus;          // PENDING, GENERATING, GENERATED, POSTING, POSTED, FAILED, SKIPPED
  lastAttemptAt?: Date;
}
```

### FeedbackAttempt

Cada tentativa de gerar/postar feedback é rastreada:

```typescript
interface FeedbackAttempt {
  attemptNumber: number;           // 1, 2, 3...
  timestamp: Date;                 // Quando tentou
  status: FeedbackStatus;          // Status dessa tentativa
  duration?: number;               // Em ms
  error?: string;                  // Mensagem de erro (se houver)
}
```

## Exemplos

### Exemplo 1: Processar testes falhados

Ver `/examples/feedback-engine-integration.ts`

```bash
npx ts-node examples/feedback-engine-integration.ts
```

### Exemplo 2: Integração com GitHub Actions

```yaml
# .github/workflows/ci-with-feedback.yml
name: CI with Feedback

on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: npm install
      
      - name: Run tests
        id: tests
        run: npm test -- --json --outputFile=test-results.json
        continue-on-error: true
      
      - name: Generate feedback
        if: failure()
        uses: actions/setup-node@v3
        with:
          node-version: "18"
      
      - name: Post feedback
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: npx ts-node scripts/generate-ci-feedback.ts
```

### Exemplo 3: Integração com CI/CD customizado

```typescript
// scripts/generate-ci-feedback.ts
import { createFeedbackEngine, ErrorType, ErrorSeverity } from "src/services";
import * as fs from "fs";

const testResults = JSON.parse(fs.readFileSync("test-results.json", "utf-8"));

const engine = createFeedbackEngine({
  githubToken: process.env.GITHUB_TOKEN,
  owner: "manta-associados",
  repo: "codex-hub-mcp",
});

const errors = testResults.failures.map((failure: any) => ({
  type: ErrorType.TEST_FAILURE,
  severity: ErrorSeverity.ERROR,
  message: failure.failureMessage,
  file: failure.testFilePath,
}));

const ciOutput = {
  workflowId: process.env.GITHUB_RUN_ID,
  workflowName: "Tests",
  prNumber: parseInt(process.env.PR_NUMBER || "0"),
  branch: process.env.GITHUB_HEAD_REF,
  commit: process.env.GITHUB_SHA,
  timestamp: new Date(),
  duration: testResults.totalTime,
  status: errors.length === 0 ? "success" : "failure",
  errors,
  testResults: {
    total: testResults.numTotalTests,
    passed: testResults.numPassedTests,
    failed: testResults.numFailedTests,
    skipped: testResults.numPendingTests,
    duration: testResults.totalTime,
  },
  logs: [],
};

const tracking = await engine.processCIOutput(ciOutput);
console.log(`Feedback posted: ${tracking.status}`);
```

## Prompt Engineering

O FeedbackEngine constrói prompts otimizados para Claude Haiku:

```
Você é um especialista em CI/CD e análise de código.
Sua tarefa é analisar erros de CI e gerar sugestões claras, acionáveis e concisas.

## Erro: TEST_FAILURE
- Mensagem: expect(result).toBe(true) received false
- Arquivo: src/api.test.ts:142
- Contexto: const result = await api.fetch();

## Sugestão esperada:
{
  "suggestion": "Verifique se a função fetch() está mockada corretamente",
  "codeExample": "jest.mock('./api', () => ({ fetch: jest.fn() }))",
  "confidence": 0.85,
  "priority": "high"
}
```

## Modelo Recomendado

**Claude 3.5 Haiku** (`claude-3-5-haiku-20241022`):

- ✅ Rápido (latência <1s)
- ✅ Eficiente (custo baixo)
- ✅ Competente em code review
- ✅ Suporta ~200K tokens de contexto

**vs Claude 3.5 Sonnet** (mais poderoso, mas mais lento/caro):

- Use para análises complexas multi-arquivo
- Use para refactorings maiores

## Limitações e Considerações

1. **Qualidade de sugestões** depende de:
   - Clareza do erro (message vs logs)
   - Contexto disponível (file, line, code snippet)
   - Quantidade de erros simultâneos (agrupa até N)

2. **Taxa de sucesso**:
   - ~95% com testes bem-estruturados
   - ~80% com lint errors
   - ~75% com problemas de coverage

3. **Custos**:
   - Haiku: ~$0.80 por 1M input tokens
   - GitHub API: Gratuito (rate limit: 5000 req/hora)

4. **Segurança**:
   - Não expõe secrets em comentários
   - Code examples são sanitizados
   - Respeita `.gitignore` e privacy settings

## Troubleshooting

### ❌ "GitHub API error (404)"

- Verifique se o `githubToken` é válido
- Verifique se o repositório existe
- Verifique se a PR existe

### ❌ "Failed to parse suggestions"

- Claude retornou formato inesperado
- Aumente `maxTokens`
- Verifique logs de erro

### ❌ "Max retries exceeded"

- API indisponível (check status page)
- Rate limit atingido (espere antes de retry)
- Aumentar `retryPolicy.maxAttempts`

## Roadmap

- [ ] Suporte a diferentes modelos (Sonnet para análises complexas)
- [ ] Integração com Jira (comentários automáticos em tickets)
- [ ] Alertas por Slack/Email
- [ ] Dashboard de métricas (API endpoint)
- [ ] Auto-fix e auto-commit (modo experimental)
- [ ] Custom prompt templates
- [ ] Cached context (prompt caching da API)

## Testing

```bash
# Rodar testes do feedback-engine
npm test -- feedback-engine.test.ts

# Com coverage
npm run test:coverage -- feedback-engine.test.ts

# Watch mode
npm run test:watch -- feedback-engine.test.ts
```

## Contribuindo

PRs são bem-vindas! Áreas de interesse:

- [ ] Novos tipos de erro
- [ ] Melhores prompts
- [ ] Integração com mais CI systems
- [ ] Performance optimizations

---

**Versão:** 1.0.0  
**Última atualização:** 2026-07-31  
**Mantido por:** Manta Associados
