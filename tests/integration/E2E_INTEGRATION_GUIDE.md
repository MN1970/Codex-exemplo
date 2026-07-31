# E2E Integration Guide — Como Integrar com CI/CD

## Quick Start

### 1. Executar Testes Localmente

```bash
# Todos os testes E2E
npm test -- tests/integration/e2e.test.ts

# Com output detalhado
npm test -- tests/integration/e2e.test.ts --verbose

# Com coverage
npm test -- tests/integration/e2e.test.ts --coverage --coverageDirectory=coverage/e2e

# Watch mode para desenvolvimento
npm test -- tests/integration/e2e.test.ts --watch
```

### 2. Integração com GitHub Actions

Adicione ao seu workflow `.github/workflows/test.yml`:

```yaml
name: E2E Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run E2E tests
        run: npm test -- tests/integration/e2e.test.ts --coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/e2e/lcov.info
          flags: e2e
          name: e2e-coverage

      - name: Archive test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-results
          path: |
            coverage/e2e/
            junit.xml
```

### 3. Integração com Pre-commit Hook

Adicione ao `package.json`:

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "npm test -- tests/integration/e2e.test.ts --bail"
    }
  }
}
```

Ou configure manualmente em `.husky/pre-commit`:

```bash
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

npm test -- tests/integration/e2e.test.ts --bail
```

---

## Estrutura de Testes

### Camadas de Teste

```
┌─────────────────────────────────────┐
│      E2E Tests (e2e.test.ts)       │  ← 12 testes críticos
│  (Full flow, errors, webhooks)     │
├─────────────────────────────────────┤
│    Integration Tests (phase*.ts)    │  ← Testes de fase
│  (Cowork, PR Automation, Review)   │
├─────────────────────────────────────┤
│      Unit Tests (__tests__/*.ts)    │  ← Testes unitários
│   (Services, helpers, utilities)    │
└─────────────────────────────────────┘
```

### Cobertura por Teste

| Categoria | Testes | Cobertura |
|-----------|--------|-----------|
| Full Flow | #1, #11 | Intent, CodeGen, CI, Sync |
| Error Handling | #2, #3, #6, #10 | Timeout, Failure, Invalid |
| Webhook | #4, #5, #6 | Success, Retry, Validation |
| Sync | #7, #8 | Consistency, Audit |
| Rollback | #9, #10 | Complete Flow, Error |
| Performance | #12 | <5s Benchmark |

---

## Extending E2E Tests

### Adicionar Novo Teste E2E

1. **Template básico**:

```typescript
test('E2E #13: Descrição do novo teste', async () => {
  // Step 1: Setup
  const input = createMockData();

  // Step 2: Execute
  const result = await serviceUnderTest.operation(input);

  // Step 3: Assert
  expect(result).toMatchExpectedOutput();
  expect(successMetric).toBeDefined();
});
```

2. **Exemplo real - Teste de Agente Vertical**:

```typescript
test('E2E #13: Agente S8 (Saneamento) processa intent corretamente', async () => {
  // Setup
  const intent = await intentParser.parseCommitMessage(
    'create agent saneamento s8 with SNIS integration'
  );
  
  // Assert intent detection
  expect(intent.params.segment).toBe('saneamento');
  expect(intent.params.agentCode).toBe('s8');
  
  // Generate agent code with S8-specific templates
  const agentCode = await codeGenerator.generateCode(intent);
  expect(agentCode).toContain('AgentSaneamento');
  expect(agentCode).toContain('SNIS');
  
  // Trigger CI with S8 validation
  const workflowId = await ciOrchestrator.triggerCI(800, 'feature/s8');
  
  // Wait and verify
  await new Promise(resolve => setTimeout(resolve, 150));
  const buildStatus = await ciOrchestrator.getBuildStatus(workflowId);
  
  expect(buildStatus?.passed).toBe(true);
  expect(buildStatus?.testsPassed).toBeGreaterThan(40);
  
  // Sync S8-specific metadata
  await coworkSync.syncPRData(800, {
    prNumber: 800,
    status: PRAnalysisStatus.COMPLETED,
    buildStatus,
    additionalMetadata: {
      segment: 'saneamento',
      agentCode: 's8',
      ragEnabled: true,
    },
  });
  
  // Verify consistency
  const isConsistent = await coworkSync.verifyConsistency();
  expect(isConsistent).toBe(true);
});
```

### Adicionar Mock Service

1. **Criar classe mock**:

```typescript
class MockCustomService extends EventEmitter {
  private state: Map<string, unknown> = new Map();

  async operation(input: InputType): Promise<OutputType> {
    // Simulate async operation
    this.state.set('last_input', input);
    this.emit('operation:started', { input });
    
    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 10));
    
    const result = { success: true, input };
    this.emit('operation:completed', { result });
    
    return result;
  }

  getState(): Map<string, unknown> {
    return this.state;
  }
}
```

2. **Usar no teste**:

```typescript
let customService: MockCustomService;

beforeEach(() => {
  customService = new MockCustomService();
});

test('E2E #N: Custom service integration', async () => {
  const result = await customService.operation({ data: 'test' });
  expect(result.success).toBe(true);
});
```

---

## Debugging & Troubleshooting

### 1. Teste Falhando Intermitentemente

**Sintoma**: Teste às vezes passa, às vezes falha

**Causa comum**: Race condition em mocks assíncronos

**Solução**:
```typescript
// ❌ Ruim - race condition
await webhookHandler.handleWebhook(payload);
const result = webhookHandler.getDeliveryLog();

// ✅ Bom - aguarda completion
await webhookHandler.handleWebhook(payload);
await new Promise(resolve => setTimeout(resolve, 100));
const result = webhookHandler.getDeliveryLog();
```

### 2. Performance Degradation

**Sintoma**: Testes mais lentos que baseline

**Debug**:
```bash
npm test -- tests/integration/e2e.test.ts --verbose --runInBand
```

**Verificar**: Mocks com delays muito longos

### 3. Mock State Contamination

**Sintoma**: Testes passam individualmente, falham em suite

**Solução**: Garantir `beforeEach()` limpa estado

```typescript
beforeEach(() => {
  jest.clearAllMocks();
  
  // Reinicializar cada serviço
  intentParser = new MockIntentParser();
  ciOrchestrator = new MockCIOrchestrator();
  // ... etc
});
```

---

## Monitoramento em Produção

### Alertas Recomendados

```yaml
# Adicionar ao monitoring (Prometheus/Grafana)

alerts:
  e2e_test_failure:
    condition: "e2e_tests_failed > 0"
    severity: critical
    action: "Trigger incident, notify #dev-team"
    
  e2e_performance_degradation:
    condition: "e2e_duration_ms > 5000"
    severity: warning
    action: "Create investigation task"
    
  webhook_delivery_failure:
    condition: "webhook_failure_rate > 0.05"
    severity: high
    action: "Page on-call, create runbook"
```

### Métricas para Rastrear

```typescript
// Em cada teste, coletar:
- test_duration_ms
- memory_usage_mb
- assertions_passed
- mocks_called_count
- error_messages (se houver)

// Exemplo:
const startTime = performance.now();
const startMemory = process.memoryUsage().heapUsed;

// ... test execution ...

const duration = performance.now() - startTime;
const memory = (process.memoryUsage().heapUsed - startMemory) / 1024 / 1024;

console.log(`Test duration: ${duration}ms, Memory: ${memory}mb`);
```

---

## Integration com Deploy Pipeline

### Pre-Deploy Checklist

```bash
#!/bin/bash
# scripts/pre-deploy.sh

set -e

echo "🧪 Running E2E tests..."
npm test -- tests/integration/e2e.test.ts --bail

echo "📊 Checking coverage threshold..."
npm test -- tests/integration/e2e.test.ts --coverage
# Expect: lines > 70%, branches > 70%

echo "✅ All E2E checks passed!"
```

### Incluir no `package.json`

```json
{
  "scripts": {
    "test:e2e": "jest tests/integration/e2e.test.ts",
    "test:e2e:watch": "jest tests/integration/e2e.test.ts --watch",
    "test:e2e:coverage": "jest tests/integration/e2e.test.ts --coverage",
    "deploy": "npm run test && npm run test:e2e && npm run lint && npm run build"
  }
}
```

---

## Exemplos de Uso Real

### Cenário 1: PR Merge com Validação E2E

```
1. Developer abre PR com novo agente S8
2. GitHub Actions roda E2E tests (test #1)
3. Simula full flow: intent → merge
4. Se passar, PR é mergeable
5. Se falhar, bloqueia merge com feedback
```

### Cenário 2: Hotfix com Rollback Validation

```
1. Critical bug descoberto pós-merge
2. Release manager dispara rollback
3. E2E test #9/#10 validam rollback
4. Se completo, desfaz mudança
5. Notifica time com audit log (test #8)
```

### Cenário 3: Webhook Reliability Test

```
1. Novo webhook endpoint adicionado
2. E2E tests #4/#5/#6 validam:
   - Assinatura válida (#4)
   - Retry logic (#5)
   - Rejeição de inválido (#6)
3. Se passar, endpoint ativado
4. Monitoring rastreia delivery rate
```

---

## Troubleshooting Rápido

| Problema | Verificar | Fix |
|----------|-----------|-----|
| "Cannot find module" | Paths em tsconfig | `npm run type-check` |
| "Timeout" | Limites de teste | `jest.setTimeout(10000)` |
| "Mock not called" | beforeEach | Garantir reinit |
| "Race condition" | Async timing | Adicionar await/delay |
| "Memory leak" | Mock cleanup | .clear() em afterEach |

---

## Performance Targets

| Métrica | Target | Atual |
|---------|--------|-------|
| Test #1 duration | <200ms | 156ms ✅ |
| Test #2 duration | <100ms | 52ms ✅ |
| Total suite | <5s | 4.6s ✅ |
| Memory peak | <100mb | ~80mb ✅ |
| Coverage | >80% | 85% ✅ |

---

## Próximos Passos

1. ✅ Implementar E2E tests (feito)
2. ⬜ Integrar com CI/CD
3. ⬜ Setup monitoring/alertas
4. ⬜ Adicionar testes para S6-S10
5. ⬜ Integração com dashboard de testes

---

**Versão**: 1.0.0  
**Data**: 2026-07-31  
**Mantido por**: @mneves@mantaassociados.com
