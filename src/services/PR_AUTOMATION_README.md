# PR Automation Engine (Phase 3)

## Visão Geral

O **PR Automation Engine** é um serviço inteligente que automatiza a análise, sugestão de melhorias e monitoramento de Pull Requests. Ele combina:

- **Detecção automática de mudanças** em arquivos do PR
- **Parse de intent** usando Claude para análise semântica de mensagens de commit
- **Geração de sugestões** baseadas em padrões de código
- **Trigger automático de CI/CD** com monitoramento de status
- **Persistência em Supabase** para histórico e análise

## Arquitetura

### Componentes Principais

```
PRAutomationEngine
├── IntentParser (analysis de commit messages)
├── CIOrchestratorService (trigger e monitoramento de CI)
├── GitHub API Client (fetch de PRs, files, commits)
├── Supabase Integration (persistência de dados)
└── Code Pattern Detector (análise de qualidade)
```

## Tipos de Dados

### PRAnalysis
Resultado completo da análise de um PR:

```typescript
interface PRAnalysis {
  prNumber: number;
  owner: string;
  repo: string;
  title: string;
  author: string;
  branch: string;
  baseBranch: string;
  status: PRAnalysisStatus;
  
  // Estatísticas
  filesChanged: number;
  additions: number;
  deletions: number;
  changedFiles: ChangedFile[];
  
  // Análise
  commitIntent?: ParsedIntent;
  commitMessages: string[];
  codePatterns: DetectedPattern[];
  suggestions: Suggestion[];
  
  // CI/CD
  ciTriggered: boolean;
  workflowRunId?: number;
  buildStatus?: BuildStatus;
  
  // Metadados
  analyzedAt: Date;
  completedAt?: Date;
  duration?: number;
  error?: string;
}
```

### Suggestion
Sugestão de melhoria gerada:

```typescript
interface Suggestion {
  id: string;
  type: CodePatternType;
  severity: "info" | "warning" | "critical";
  file?: string;
  title: string;
  description: string;
  recommendation: string;
  examples?: string[];
  confidence: number; // 0.0-1.0
}
```

### CodePatternType
Tipos de padrões detectados:

- `complexity` - Complexidade de código elevada
- `duplication` - Código duplicado
- `missing-types` - Tipos TypeScript faltando
- `missing-tests` - Testes não encontrados
- `performance` - Problemas de performance
- `security` - Preocupações de segurança
- `accessibility` - Acessibilidade
- `documentation` - Documentação faltando

## API

### PRAutomationEngine

#### Constructor
```typescript
const engine = new PRAutomationEngine({
  githubToken: string;
  owner: string;
  repo: string;
  workflowId?: string | number;
  supabaseUrl?: string;
  supabaseKey?: string;
  anthropicApiKey?: string;
  autoTriggerCI?: boolean;
  minConfidenceThreshold?: number;
});
```

#### analyzePR(prNumber, owner?, repo?)
Analisa um PR completo:

```typescript
const analysis = await engine.analyzePR(42, "owner", "repo");
```

**Fluxo:**
1. Busca dados do PR do GitHub
2. Busca arquivos alterados
3. Busca commits e parse de intent
4. Detecta padrões de código
5. Gera sugestões
6. (Opcional) Dispara CI/CD e monitora
7. (Opcional) Persiste em Supabase

**Retorna:** `Promise<PRAnalysis>`

#### generateSuggestions(files, patterns)
Gera sugestões baseadas em padrões:

```typescript
const suggestions = await engine.generateSuggestions(
  files,
  codePatterns
);
```

**Tipos de Sugestões:**
- Sugestões mapeadas de padrões detectados
- Aviso de PR grande (>500 adições)
- Aviso de falta de testes
- Avisos de complexidade
- Recomendações de segurança

#### triggerCI(prNumber, owner?, repo?)
Dispara o pipeline de CI/CD:

```typescript
const ciResult = await engine.triggerCI(42);
// {
//   success: boolean;
//   workflowRunId: number;
//   status: string;
//   buildOutput: BuildOutput;
//   duration: number;
// }
```

#### monitorBuild(workflowId)
Monitora o status do build:

```typescript
const buildStatus = await engine.monitorBuild(12345);
// {
//   workflowRunId: number;
//   status: string;
//   passed: boolean;
//   testsPassed?: number;
//   testsFailed?: number;
//   coverage?: number;
//   duration?: number;
// }
```

## Exemplos de Uso

### Exemplo 1: Análise Básica
```typescript
import { createPRAutomationEngine } from './services';

const engine = createPRAutomationEngine({
  githubToken: process.env.GITHUB_TOKEN,
  owner: 'manta-associados',
  repo: 'codex-example',
  autoTriggerCI: false,
});

const analysis = await engine.analyzePR(42);

console.log(`PR #${analysis.prNumber}: ${analysis.title}`);
console.log(`Sugestões: ${analysis.suggestions.length}`);
console.log(`Padrões: ${analysis.codePatterns.length}`);
```

### Exemplo 2: Com CI/CD Automático
```typescript
const engine = createPRAutomationEngine({
  githubToken: process.env.GITHUB_TOKEN,
  owner: 'manta-associados',
  repo: 'codex-example',
  workflowId: 'test.yml',
  autoTriggerCI: true,
  maxCIWait: 600000, // 10 minutos
});

const analysis = await engine.analyzePR(42);

if (analysis.buildStatus) {
  console.log(`Build: ${analysis.buildStatus.passed ? 'PASSOU' : 'FALHOU'}`);
  console.log(`Cobertura: ${analysis.buildStatus.coverage}%`);
}
```

### Exemplo 3: Análise em Batch
```typescript
const prNumbers = [40, 41, 42, 43, 44];
const results = [];

for (const prNumber of prNumbers) {
  const analysis = await engine.analyzePR(prNumber);
  results.push({
    prNumber: analysis.prNumber,
    suggestions: analysis.suggestions.length,
    patterns: analysis.codePatterns.length,
  });
}

console.table(results);
```

### Exemplo 4: Sugestões Detalhadas
```typescript
const analysis = await engine.analyzePR(42);

for (const suggestion of analysis.suggestions) {
  console.log(`[${suggestion.severity}] ${suggestion.title}`);
  console.log(`  → ${suggestion.recommendation}`);
  
  if (suggestion.examples) {
    console.log('  Exemplos:');
    suggestion.examples.forEach(ex => console.log(`    • ${ex}`));
  }
}
```

## Integração com Supabase

### Schema SQL
Execute o script em `src/services/migrations/pr-analyses-schema.sql` no Supabase SQL Editor para criar as tabelas necessárias.

### Tabelas Criadas:
- `pr_analyses` - Análises principais
- `code_patterns` - Padrões detectados
- `suggestions` - Sugestões geradas
- `changed_files` - Arquivos alterados
- `commit_intents` - Intents de commits
- `pr_metrics_daily` - Métricas agregadas diárias

### Configuração
```typescript
const engine = createPRAutomationEngine({
  githubToken: process.env.GITHUB_TOKEN,
  owner: 'manta-associados',
  repo: 'codex-example',
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseKey: process.env.SUPABASE_ANON_KEY,
});
```

## Padrões de Código Detectados

### Complexity
- **Detecção:** Múltiplas adições em um arquivo
- **Recomendação:** Refatorar para reduzir complexidade ciclomática

### Missing Tests
- **Detecção:** Nenhum arquivo `.test.*` ou `.spec.*` foi alterado
- **Recomendação:** Adicionar testes para a nova funcionalidade

### Missing Types (TypeScript)
- **Detecção:** Uso de `any` type ou falta de anotações de tipo
- **Recomendação:** Adicionar tipos explícitos para melhor type safety

### Performance
- **Detecção:** Operações potencialmente síncronas
- **Recomendação:** Usar async/await e lazy loading

### Security
- **Detecção:** Uso de `eval()` ou outras operações perigosas
- **Recomendação:** Revisar para potenciais vulnerabilidades

### Large PR
- **Detecção:** >500 linhas adicionadas
- **Recomendação:** Dividir em PRs menores

## Configuração de Ambiente

### Variáveis Obrigatórias
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### Variáveis Opcionais
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
SUPABASE_URL=https://xxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
```

## Métricas e Observability

### Métricas de CI/CD
```typescript
const metrics = engine.getCIMetrics();
// {
//   totalWorkflowsTriggered: number;
//   successCount: number;
//   failureCount: number;
//   timeoutCount: number;
//   averageDurationMs: number;
//   averageTestPassRate: number;
//   averageCoverage: CoverageResult;
// }
```

### Logs e Observability
- Todos os passos principais são logados
- Erros incluem stack traces completos
- Timing é rastreado para otimização

## Tratamento de Erros

### Estados de Erro
```typescript
if (analysis.status === PRAnalysisStatus.FAILED) {
  console.error(`Erro: ${analysis.error}`);
}
```

### Falhas Esperadas
- PR não encontrado → `PRAnalysisStatus.FAILED`
- CI timeout → Retorna status de timeout sem falhar a análise
- Supabase indisponível → Log de warning, análise continua
- GitHub API rate limit → Erro lançado

## Testes

Execute os testes com:
```bash
npm test -- pr-automation.test.ts
```

### Cobertura de Testes
- ✅ Análise de PR completa
- ✅ Detecção de padrões de código
- ✅ Geração de sugestões
- ✅ Trigger de CI/CD
- ✅ Monitoramento de build
- ✅ Tratamento de erros

## Roadmap

### v1.1
- [ ] Integração com GitHub Comments (post de sugestões direto no PR)
- [ ] Análise de histórico de código (git blame)
- [ ] Métricas de complexidade avançadas (cyclomatic, cognitive)

### v2.0
- [ ] Análise de dependências
- [ ] Detecção de duplicação de código
- [ ] Integração com SonarQube
- [ ] Custom rule engine

### v3.0
- [ ] Auto-fix para issues comuns
- [ ] Integração com JIRA
- [ ] Dashboard web de análises

## Performance

### Benchmarks
- Análise de PR pequeno (1-5 arquivos): ~5-10 segundos
- Análise de PR médio (5-20 arquivos): ~15-30 segundos
- Análise de PR grande (20+ arquivos): ~30-60 segundos
- CI/CD monitoramento: depende do workflow (typically 5-10 minutos)

### Otimizações
- Processamento paralelo de arquivos
- Cache de intents já analisados
- Polling inteligente com backoff exponencial

## Suporte e Troubleshooting

### PR não encontrado
```typescript
// Verifique: owner, repo, e prNumber estão corretos
// GitHub API retorna 404 se PR não existe
```

### CI não dispara
```typescript
// Verifique: workflowId existe e está correto
// Verifique: GitHub token tem permissão de workflow dispatch
```

### Sugestões vazias
```typescript
// Normal para PRs pequenos ou com poucas mudanças
// Sugestões aparecem principalmente para arquivos alterados
```

## Contribuindo

Para adicionar novos tipos de padrões:

1. Adicione o tipo em `CodePatternType`
2. Implemente detecção em `detectCodePatterns()`
3. Adicione título em `getTitleForPattern()`
4. Adicione recomendação em `getRecommendationForPattern()`
5. Adicione exemplos em `getExamplesForPattern()`
6. Adicione testes em `pr-automation.test.ts`

## Licença

MIT
