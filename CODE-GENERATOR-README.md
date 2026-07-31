# Code Generator Service — Guia Completo

**Versão:** 1.0.0 | **Status:** ✅ Pronto para Uso | **Modelo:** Claude Opus 4.1

---

## O que é?

O **Code Generator** é um serviço TypeScript que automatiza a criação completa de novos agentes Manta a partir de uma descrição em linguagem natural (intent). Ele:

- **Recebe:** Uma descrição do agente (intent)
- **Processa:** Multi-turn conversation com Claude Opus
- **Gera:** 4 artefatos prontos para produção (agent.md, test.ts, docs.md, keywords.json)
- **Valida:** YAML frontmatter obrigatório em todos os outputs
- **Integra:** Cria branch feature/*, commits arquivos, retorna metadados

---

## Localização

```
src/services/code-generator.ts          ← Implementação (600+ linhas)
src/services/__tests__/code-generator.test.ts  ← Testes (700+ linhas)
src/examples/code-generator-integration.ts     ← Exemplos práticos
docs/CODE-GENERATOR.md                  ← Documentação completa
```

---

## Quick Start

### 1. Importar

```typescript
import { CodeGenerator, CodeGeneratorIntent } from "./services";
```

### 2. Criar instância

```typescript
const generator = new CodeGenerator(
  process.env.ANTHROPIC_API_KEY, // ou undefined (usa env)
  process.cwd()                   // project root
);
```

### 3. Definir intent

```typescript
const intent: CodeGeneratorIntent = {
  intent: "Criar agente especializado em ETA, ETE e adução de água",
  segment: "Saneamento",
  mantaCode: "Manta 03-S8",
  tier: "Sonnet",
  keywords: ["eta", "ete", "adutora", "tratamento"],
  userEmail: "mneves@mantaassociados.com",
  projectRoot: process.cwd(),
};
```

### 4. Gerar

```typescript
const result = await generator.generateCode(intent);

if (result.status === "success") {
  console.log(`✓ Agente criado: ${result.branchName}`);
  console.log(`✓ Commit: ${result.commitHash}`);
  console.log(`✓ Artefatos:`);
  result.artifacts.forEach(a => {
    console.log(`  - ${a.filename} (${a.type})`);
  });
} else {
  console.error("Erros:", result.errors);
}
```

---

## Tipos de Dados

### Input: `CodeGeneratorIntent`

```typescript
interface CodeGeneratorIntent {
  // Obrigatório
  intent: string;              // "Criar agente para saneamento básico..."
  segment: string;             // "Saneamento", "Energia", "Portos", etc

  // Opcional
  mantaCode?: string;          // "Manta 03-S8"
  tier?: "Haiku" | "Sonnet" | "Opus";  // default: Sonnet
  keywords?: string[];         // ["eta", "ete", "adutora"]
  userEmail?: string;          // "mneves@mantaassociados.com"
  projectRoot?: string;        // default: process.cwd()
}
```

### Output: `CodeGeneratorOutput`

```typescript
interface CodeGeneratorOutput {
  status: "success" | "partial" | "failed";
  artifacts: GeneratedArtifact[];      // 4 arquivos gerados
  createdFiles: string[];               // ["./claude/agents/..."]
  branchName: string;                   // "feature/agente-..."
  commitHash: string;                   // SHA do commit
  errors: string[];                     // Erros encontrados
  warnings: string[];                   // Avisos
  executionTimeMs: number;              // Tempo total em ms
  conversationLog?: ConversationMessage[]; // Para auditoria
}
```

### Artefato: `GeneratedArtifact`

```typescript
interface GeneratedArtifact {
  filename: string;                    // "agente-saneamento.md"
  filepath: string;                    // ".claude/agents/agente-saneamento.md"
  content: string;                     // Conteúdo completo
  type: "agent-md" | "test-cases" | "documentation" | "keywords-json";
  validated: boolean;                  // true se passou validação
  validationErrors?: string[];         // Erros de validação, se houver
}
```

---

## Validação de YAML Frontmatter

Toda agent `.md` **deve** ter frontmatter YAML válido:

```yaml
---
name: agente-saneamento              # obrigatório
description: Especialista em ETA...  # obrigatório
tools: [Read, Bash, Grep, WebFetch]  # obrigatório
model: sonnet                         # obrigatório
---

# Corpo do Agente (markdown)
```

### Validar manualmente

```typescript
import { validateYAMLFrontmatter } from "./services";

const { valid, errors } = validateYAMLFrontmatter(content);

if (!valid) {
  errors.forEach(err => console.error(`✗ ${err}`));
}
```

---

## Fluxo Interno (4 Fases)

### Fase 1: Planejamento

- Claude Opus recebe o intent
- Determina estrutura do agente
- Identifica dependências, keywords, tools

### Fase 2: Geração Iterativa

- Se artefatos faltam, faz follow-up
- Regenera conteúdo se necessário
- Continua até 4 artefatos prontos

### Fase 3: Validação

- Verifica YAML frontmatter (agent.md)
- Valida sintaxe TypeScript (test.ts)
- Parse JSON (keywords.json)
- Retorna erros/avisos

### Fase 4: Criação de Branch

```bash
git checkout -b feature/agente-{name}-{hash}
git add .claude/agents/agente-{name}.md
git add .claude/agents/agente-{name}-keywords.json
git add src/services/__tests__/agente-{name}.test.ts
git add docs/agente-{name}-documentation.md
git commit -m "feat: add agente-{name}..."
```

---

## Exemplos Práticos

### Exemplo 1: Gerar Agente Saneamento

```typescript
const generator = new CodeGenerator();

const result = await generator.generateCode({
  intent: "Agente para ETA, ETE e sistemas de adução de água",
  segment: "Saneamento",
  mantaCode: "Manta 03-S8",
  tier: "Sonnet",
  keywords: ["eta", "ete", "adutora", "saneamento"],
});

console.log(result.status);
// → "success"

console.log(result.artifacts.map(a => a.filename));
// → [
//   "agente-saneamento.md",
//   "agente-saneamento.test.ts",
//   "agente-saneamento-documentation.md",
//   "agente-saneamento-keywords.json"
// ]
```

### Exemplo 2: Geração em Paralelo

```typescript
const intents = [
  { intent: "...", segment: "Saneamento" },
  { intent: "...", segment: "Energia" },
  { intent: "...", segment: "Portos" },
];

const results = await Promise.all(
  intents.map(intent => generator.generateCode(intent))
);

console.log(`✓ ${results.length} agentes criados`);
```

### Exemplo 3: Tratamento de Erros

```typescript
try {
  const result = await generator.generateCode(intent);

  if (result.status === "failed") {
    console.error("Falha crítica:");
    result.errors.forEach(err => console.error(`  - ${err}`));
  } else if (result.status === "partial") {
    console.warn("Geração parcial com avisos:");
    result.warnings.forEach(warn => console.warn(`  - ${warn}`));
  }
} catch (error) {
  console.error("Erro não capturado:", error);
}
```

### Exemplo 4: Auditoria

```typescript
const result = await generator.generateCode(intent);

if (result.conversationLog) {
  console.log("=== Conversa com Claude Opus ===");
  result.conversationLog.forEach(msg => {
    console.log(`\n[${msg.role.toUpperCase()}] ${msg.timestamp}`);
    console.log(msg.content);
  });
}
```

---

## Estrutura de Artefatos

### 1. Agent `.md` — `.claude/agents/agente-name.md`

```markdown
---
name: agente-saneamento
description: Especialista em ETA, ETE, adução e drenagem urbana
tools: [Read, Bash, Grep, WebFetch, WebSearch]
model: sonnet
---

# Agente Saneamento (Manta 03-S8)

Especialista em saneamento básico brasileiro...

## Contexto de domínio
- Água: captação, adução, ETA, distribuição
- Esgoto: coleta, ETE, disposição
- Drenagem urbana: micro e macrodrenagem
- Resíduos sólidos: coleta, tratamento, aterro

## Ordem canônica de raciocínio
1. Enquadramento
2. Diagnóstico
3. Concepção
4. ...

## Ferramentas e integrações
- Consulta SNIS
- Repositórios ANA
- ...

## Handoff com outros agentes
- manta-05 (orçamento)
- manta-06 (modelagem)
- ...

## O que este agente NÃO faz
- Não substitui projeto assinado por engenheiro
- ...
```

### 2. Test Cases — `src/services/__tests__/agente-name.test.ts`

```typescript
import { describe, test, expect } from '@jest/globals';

describe('Agente Saneamento', () => {
  describe('Routing', () => {
    test('deve rotear ETA/ETE para agente-saneamento', () => {
      // ...
    });
  });

  describe('Cálculos', () => {
    test('deve calcular demanda de água', () => {
      // ...
    });
  });

  describe('Validação', () => {
    test('deve validar tubulação', () => {
      // ...
    });
  });
});
```

### 3. Documentation — `docs/agente-name-documentation.md`

```markdown
# Documentação do Agente Saneamento

## Overview
- Responsabilidades
- Escopo de conhecimento
- Limitações

## API Reference
- Input esperado
- Output esperado
- Tratamento de erros

## Exemplos
### Caso 1: Dimensionar ETA
### Caso 2: Calcular demanda
### Caso 3: Drenagem urbana

## Referências
- Lei 14.026/2020
- NBR 12211-12218
- SNIS
```

### 4. Keywords JSON — `.claude/agents/agente-name-keywords.json`

```json
{
  "keywords": [
    {
      "keyword": "eta",
      "weight": 3.0,
      "category": "primary"
    },
    {
      "keyword": "ete",
      "weight": 3.0,
      "category": "primary"
    },
    {
      "keyword": "adutora",
      "weight": 2.8,
      "category": "secondary"
    },
    {
      "keyword": "saneamento",
      "weight": 2.5,
      "category": "context"
    }
  ]
}
```

---

## Testing

### Rodar testes

```bash
npm test -- code-generator.test.ts
npm test -- code-generator.test.ts --watch
npm test -- code-generator.test.ts --coverage
```

### Cobertura esperada

- ✅ Inicialização
- ✅ Validação YAML frontmatter
- ✅ Geração de código (Intent → Artifacts)
- ✅ Criação de branch e commits
- ✅ Error handling
- ✅ Intents específicas (Saneamento, Energia, etc)

---

## Performance

| Operação | Tempo |
|----------|-------|
| Planejamento (Opus) | 3-5s |
| Geração iterativa | 2-4s |
| Validação | <100ms |
| Git operations | 500ms-1s |
| **Total** | **6-10s** |

---

## Integração com Sistema

### Usando dentro do projeto

```typescript
// Em src/index.ts ou seu entry point
import { CodeGenerator } from "./services";

export async function createNewAgent(intent: string) {
  const generator = new CodeGenerator();
  return await generator.generateCode({
    intent,
    segment: "Saneamento",
    projectRoot: process.cwd(),
  });
}
```

### Expor como MCP tool

```typescript
// Em seu MCP server
import { CodeGenerator } from "./services";

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "code_generator") {
    const generator = new CodeGenerator();
    const result = await generator.generateCode(JSON.parse(request.params.arguments.intent));
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  }
});
```

---

## Checklist de Implementação

- [x] Implementado `CodeGenerator` class
- [x] Implementados 4 tipos de geração (agent.md, test.ts, docs.md, keywords.json)
- [x] Validação YAML frontmatter obrigatória
- [x] Multi-turn conversation com Opus
- [x] Criação de branch feature/*
- [x] Git commit automático
- [x] Error handling robusto
- [x] Conversation log para auditoria
- [x] Testes completos (60+ testes)
- [x] Exemplos práticos (6 exemplos)
- [x] Documentação (CODE-GENERATOR.md)
- [x] Type safety (TypeScript)

---

## Próximos Passos

1. **Usar em produção:** `npm run test` para validar
2. **Integrar em CLI:** Adicionar comando `manta generate-agent`
3. **Expor em MCP:** Tornar disponível como tool no Maestro
4. **Persistência:** Guardar conversation logs em Supabase
5. **Validação cruzada:** Comparar contra CLAUDE.md existente

---

## Suporte

- **Dúvidas:** Abra issue com label `code-generator`
- **Bugs:** Report em GitHub com stacktrace
- **Melhorias:** PRs bem-vindas
- **Email:** mneves@mantaassociados.com

---

## License

MIT — Manta Associados 2026

---

**Última atualização:** 2026-07-31  
**Versão:** 1.0.0  
**Status:** ✅ Operacional
