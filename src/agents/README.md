# Agents — Módulo de Agentes IA Manta

Implementação de agentes IA verticais e serviços de código relacionados.

## Estrutura

```
src/agents/
├── code-reviewer.ts           # ✨ Code Review Agent (novo)
├── examples/
│   └── code-reviewer-example.ts
├── __tests__/
│   └── code-reviewer.test.ts
└── README.md                  # Este arquivo
```

## Code Reviewer Agent

### O que faz

Análise profunda de PRs e novo código de agentes usando Claude Opus. Avalia:

- **Correctness**: Lógica, validações, edge cases
- **Security**: Injeção, exposição de secrets, acessos inseguros
- **Performance**: Complexidade, loops desnecessários, alocações
- **Style**: Padrões, type safety, documentação

### Como usar

```typescript
import { CodeReviewerAgent, type CodeReviewInput } from "./code-reviewer";

const agent = new CodeReviewerAgent(process.env.ANTHROPIC_API_KEY);

const input: CodeReviewInput = {
  prDiff: "... unified diff ...",
  newAgentCode: "... typescript code ...",
  agentPath: "src/agents/maestro.ts",
  prContext: {
    title: "refactor: improve routing",
    description: "Better patterns for agent selection",
    author: "dev@example.com",
  },
  // Opcional: analisar apenas algumas dimensões
  dimensions: ["correctness", "security"],
};

const result = await agent.reviewCode(input);

// result.findings: CodeFinding[]
// result.summary: string (max 50 linhas)
// result.overallScore: 0-100
// result.dimensionStats: contagem por dimensão
// result.severityStats: contagem por severidade
```

### Output Structure

```typescript
interface CodeReviewOutput {
  status: "success" | "failed";
  findings: CodeFinding[];       // Estruturado com file/line/severity
  summary: string;               // ~50 linhas max
  dimensionStats: {
    correctness: number;
    security: number;
    performance: number;
    style: number;
  };
  severityStats: {
    info: number;
    warning: number;
    error: number;
    critical: number;
  };
  overallScore: number;          // 0-100
  analysisTimeMs: number;
  errors?: string[];
}
```

### Finding Structure

```typescript
interface CodeFinding {
  file: string;                  // Caminho relativo
  line: number;                  // 1-indexed
  endLine?: number;              // Para spans multi-line
  dimension: AnalysisDimension;  // correctness|security|performance|style
  severity: FindingSeverity;     // info|warning|error|critical
  title: string;                 // Título curto
  description: string;           // Descrição detalhada
  suggestion?: string;           // Como corrigir
  code?: string;                 // Snippet problemático
}
```

## Score Calculation

Penalidades por severidade:

| Severidade | Penalidade |
|-----------|-----------|
| Critical  | -30       |
| Error     | -15       |
| Warning   | -5        |
| Info      | -1        |

Score = max(0, min(100, 100 - penalidades))

## Exemplos

### Exemplo 1: Análise de PR

```typescript
const input: CodeReviewInput = {
  prDiff: `
--- a/src/agents/maestro.ts
+++ b/src/agents/maestro.ts
@@ -1,5 +1,8 @@
 export async function routeAgent(intent: string) {
+  if (!intent) throw new Error('intent required');
   const agents = ['01', '02', '03', '04', '05'];
-  for (let i = 0; i < agents.length; i++) {
+  for (const agent of agents) {
-    if (intent.includes(agents[i])) return agents[i];
+    if (intent.includes(agent)) return agent;
   }
   return 'maestro';
 }`,
  newAgentCode: "...",
  agentPath: "src/agents/maestro.ts",
};
```

### Exemplo 2: Análise com dimensão específica

```typescript
const input: CodeReviewInput = {
  prDiff: "",
  newAgentCode: "export function query(sql: string) { return db.execute(sql); }",
  agentPath: "src/agents/query.ts",
  dimensions: ["security"], // Foca em segurança
};

const result = await agent.reviewCode(input);
// Retorna apenas findings de segurança
```

### Exemplo 3: Análise de novo agente vertical

```typescript
const input: CodeReviewInput = {
  prDiff: `--- /dev/null
+++ b/src/agents/agente-saneamento.ts
@@ -0,0 +1,50 @@
+export class SanitationAgent { ... }`,
  newAgentCode: newSanitationAgentCode,
  agentPath: "src/agents/agente-saneamento.ts",
  prContext: {
    title: "feat: implement sanitation vertical agent S8",
    description: "New vertical agent for sanitation projects",
    author: "mauricio.neves@mantaassociados.com",
  },
};

const result = await agent.reviewCode(input);
// Análise completa do novo agente S8
```

## Testes

Executar testes:

```bash
npm test -- src/agents/__tests__/code-reviewer.test.ts
```

Testes cobrem:

- Análise básica com múltiplas dimensões
- Detecção de issues de segurança
- Detecção de issues de style
- Cálculo de estatísticas
- Cálculo de score
- Geração de summary
- Tratamento de erros

## Integração com CI/CD

Sugestão de uso em pipeline GitHub Actions:

```yaml
- name: Code Review
  run: |
    npm run build
    npx ts-node src/agents/examples/code-reviewer-example.ts
```

## Modelo e Costs

- **Modelo**: Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- **Max tokens**: 4,096 por análise
- **Latência típica**: 5-15s por PR
- **Custo estimado**: ~$0.15 por análise (25K input tokens @ 0.003, 1K output @ 0.015)

## Notas de Design

### Por que Claude Opus?

- Análise estruturada e precisa
- Suporta instruções complexas
- Melhor detecção de edge cases
- Refere-se a linhas específicas no código

### JSON Parsing

O agent retorna findings em JSON estruturado. Se o JSON for inválido, retorna array vazio (graceful degradation).

### Scoring

Score de 0-100 com penalidades progressivas:

- **90+**: Excelente código
- **80-89**: Bom, poucos ajustes
- **70-79**: Aceitável, revisar antes de merge
- **<70**: Crítico, requer mudanças

## Roadmap

- [ ] Cache de análises anteriores
- [ ] Suporte a múltiplas linguagens (Python, Go, Java)
- [ ] Integração com GitHub API para comentários automáticos em PR
- [ ] Histórico de scores por arquivo
- [ ] Métricas de trend (melhora/piora ao longo do tempo)

---

**Versão**: 1.0.0  
**Status**: ✅ Produção  
**Última atualização**: 2026-07-31
