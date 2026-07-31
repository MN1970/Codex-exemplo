# Code Generator Service

**Versão:** 1.0.0  
**Status:** ✅ Operacional  
**Modelo:** Claude Opus 4.1 (multi-turn)  
**Linguagem:** TypeScript  
**Localização:** `src/services/code-generator.ts`

---

## Visão Geral

O **Code Generator** é um serviço que automatiza a criação de novos agentes Manta baseado em intents em linguagem natural. Ele:

1. **Recebe um intent** (descrição do agente a criar)
2. **Conversa com Claude Opus** em múltiplas turnos para refinar especificações
3. **Gera 4 artefatos**:
   - `agente-name.md` (definição do agente com YAML frontmatter)
   - `agente-name.test.ts` (test cases Jest)
   - `agente-name-documentation.md` (documentação)
   - `agente-name-keywords.json` (keywords para roteamento)
4. **Valida YAML frontmatter** obrigatório em todos os outputs
5. **Cria branch feature/*** e faz commits dos arquivos
6. **Retorna metadados** completos incluindo conversationLog para auditoria

---

## Arquitetura

### Fluxo de Execução

```
┌─────────────────────────────────┐
│  intent: CodeGeneratorIntent    │
│  (descrição em linguagem natural)│
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Fase 1: Planejamento           │
│  (Claude Opus determina         │
│   estrutura, dependências)      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Fase 2: Geração Iterativa      │
│  (Multi-turn se necessário)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Fase 3: Validação Schema       │
│  (YAML frontmatter obrigatório) │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Fase 4: Criação de Branch      │
│  (git checkout, add, commit)    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  CodeGeneratorOutput:           │
│  - artifacts[]                  │
│  - branchName                   │
│  - commitHash                   │
│  - conversationLog[]            │
│  - errors[], warnings[]         │
└─────────────────────────────────┘
```

### Tipos Principais

#### `CodeGeneratorIntent`

Input para geração de código:

```typescript
interface CodeGeneratorIntent {
  intent: string;           // "Criar agente para saneamento básico..."
  segment: string;          // "Saneamento", "Energia", "Portos", etc
  mantaCode?: string;       // "Manta 03-S8"
  tier?: "Haiku" | "Sonnet" | "Opus";
  keywords?: string[];      // ["eta", "ete", "adutora"]
  userEmail?: string;       // "mneves@mantaassociados.com"
  projectRoot?: string;     // "/home/user/Codex-exemplo"
}
```

#### `GeneratedArtifact`

Artefato individual gerado:

```typescript
interface GeneratedArtifact {
  filename: string;              // "agente-saneamento.md"
  filepath: string;              // ".claude/agents/agente-saneamento.md"
  content: string;               // Conteúdo completo
  type: "agent-md" | "test-cases" | "documentation" | "keywords-json";
  validated: boolean;            // true se passou validação schema
  validationErrors?: string[];   // Erros de validação, se houver
}
```

#### `CodeGeneratorOutput`

Output com todos os resultados:

```typescript
interface CodeGeneratorOutput {
  status: "success" | "partial" | "failed";
  artifacts: GeneratedArtifact[];
  createdFiles: string[];
  branchName: string;            // "feature/agente-saneamento-abc123"
  commitHash: string;            // Commit SHA
  errors: string[];
  warnings: string[];
  executionTimeMs: number;
  conversationLog?: ConversationMessage[];  // Para auditoria
}
```

---

## Uso

### Instalação e Importação

```typescript
import {
  CodeGenerator,
  CodeGeneratorIntent,
  validateYAMLFrontmatter,
} from "./services/code-generator";
```

### Exemplo 1: Geração Básica

```typescript
const generator = new CodeGenerator(
  undefined, // usa ANTHROPIC_API_KEY do env
  process.cwd()
);

const result = await generator.generateCode({
  intent: "Criar agente para ETA e ETE com cálculos de demanda",
  segment: "Saneamento",
  mantaCode: "Manta 03-S8",
  tier: "Sonnet",
  keywords: ["eta", "ete", "adutora"],
  userEmail: "mneves@mantaassociados.com",
});

console.log(result.status);        // "success"
console.log(result.branchName);    // "feature/agente-criar-agente-abc123"
console.log(result.artifacts);     // [agent-md, test-cases, documentation, keywords-json]
```

### Exemplo 2: Validação Standalone

```typescript
const { valid, errors } = validateYAMLFrontmatter(`---
name: agente-saneamento
description: Agente de saneamento
tools: [Read, Bash, Grep]
model: sonnet
---

# Agente Saneamento
...`);

if (!valid) {
  console.error("Erros de validação:", errors);
}
```

### Exemplo 3: Tratamento de Erros

```typescript
const result = await generator.generateCode(intent);

if (result.status === "failed") {
  console.error("Erros:", result.errors);
} else if (result.status === "partial") {
  console.warn("Avisos:", result.warnings);
  // Alguns artefatos foram gerados mesmo com erro
}

// Auditoria: ver conversas com Claude Opus
if (result.conversationLog) {
  result.conversationLog.forEach(msg => {
    console.log(`[${msg.role}] ${msg.content}`);
  });
}
```

---

## YAML Frontmatter — Schema Obrigatório

Todo arquivo agent `.md` gerado **deve** conter frontmatter YAML válido:

```yaml
---
name: agente-nome              # required: string
description: Descrição...      # required: string
tools: [Read, Bash, Grep]      # required: string[]
model: sonnet                  # required: "haiku" | "sonnet" | "opus"
---

# Agent Body (markdown)
```

### Validação de Campos

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| `name` | string | ✅ | Lowercase, sem espaços |
| `description` | string | ✅ | 1-500 caracteres |
| `tools` | string[] | ✅ | Read, Bash, Grep, WebFetch, etc |
| `model` | string | ✅ | haiku \| sonnet \| opus |

### Exemplo Válido

```markdown
---
name: agente-saneamento
description: Especialista em ETA, ETE, adução e drenagem urbana
tools: [Read, Bash, Grep, WebFetch, WebSearch]
model: sonnet
---

# Agente Saneamento (Manta 03-S8)

Especialista em saneamento básico brasileiro...
```

---

## Artefatos Gerados

### 1. Agent `.md` (`.claude/agents/agente-name.md`)

**Formato:**
```markdown
---
name: agente-name
description: ...
tools: [...]
model: sonnet
---

# Agent Name
Seções:
- Contexto de domínio
- Ordem canônica de raciocínio
- Ferramentas e integrações
- Handoff com outros agentes
- O que este agente NÃO faz
```

**Validação:** YAML frontmatter obrigatório ✅

---

### 2. Test Cases (`.test.ts`)

**Localização:** `src/services/__tests__/agente-name.test.ts`

**Formato:**
```typescript
import { describe, test, expect } from '@jest/globals';

describe('Agente Name', () => {
  describe('Routing', () => {
    test('deve rotear para agente correto', () => {
      // ...
    });
  });

  describe('Validação', () => {
    test('deve validar schema', () => {
      // ...
    });
  });
});
```

**Validação:** Sintaxe TypeScript + presença de `describe` e `test` ✅

---

### 3. Documentation (`.md`)

**Localização:** `docs/agente-name-documentation.md`

**Formato:**
```markdown
# Documentação do Agente Name

## Overview
- Responsabilidades
- Limites

## API Reference
- Inputs
- Outputs
- Erro handling

## Examples
- Caso de uso 1
- Caso de uso 2
```

---

### 4. Keywords JSON (`.json`)

**Localização:** `.claude/agents/agente-name-keywords.json`

**Formato:**
```json
{
  "keywords": [
    {
      "keyword": "eta",
      "weight": 3.0,
      "category": "primary"
    },
    {
      "keyword": "tratamento",
      "weight": 2.5,
      "category": "secondary"
    }
  ]
}
```

**Validação:** JSON válido + estrutura obrigatória ✅

---

## Integração com Git

### Branch Naming

```
feature/agente-{agent-name}-{random-hex}
feature/agente-saneamento-abc123
feature/agente-energia-def456
```

### Commit Message

```
feat: add agente-name agent

Generated by CodeGenerator service
Agent segment: Saneamento
Intent: Criar agente para ETA e ETE...
```

### Estrutura Criada

```
Codex-exemplo/
├── .claude/agents/
│   ├── agente-saneamento.md
│   └── agente-saneamento-keywords.json
├── src/services/__tests__/
│   └── agente-saneamento.test.ts
└── docs/
    └── agente-saneamento-documentation.md
```

---

## Error Handling

### Status Codes

| Status | Significado | Ação Recomendada |
|--------|-------------|------------------|
| `success` | Todos os artefatos válidos, branch criado | Mesclar PR |
| `partial` | Alguns artefatos gerados, mas erros em validação | Revisar `artifacts` e `errors` |
| `failed` | Falha crítica, branch não criado | Ver `errors` detalhados |

### Erros Comuns

#### API Error
```typescript
// Error: API rate limit exceeded
result.status = "failed"
result.errors = ["Erro crítico: API rate limit exceeded"]
```

**Solução:** Aguarde 60s e tente novamente

#### YAML Validation Error
```typescript
// frontmatter inválido
result.artifacts[0].validationErrors = [
  "Campo obrigatório ausente: tools",
  "Campo 'model' deve ser: haiku, sonnet ou opus"
]
```

**Solução:** Claude Opus regenerará com frontmatter válido

#### Git Commit Error
```typescript
// Falha ao criar branch
result.status = "failed"
result.errors = ["Erro ao criar branch/commit: fatal: Not a git repository"]
```

**Solução:** Verifique que `projectRoot` é um repositório git válido

---

## Auditoria (Conversation Log)

O campo `conversationLog` registra toda a conversa com Claude Opus:

```typescript
const result = await generator.generateCode(intent);

result.conversationLog?.forEach((msg) => {
  console.log(`[${msg.role}] ${msg.timestamp}`);
  console.log(msg.content);
  console.log('---');
});
```

**Uso:**
- Auditoria de quem criou o agente e quando
- Debug de falhas na geração
- Reproduzir geração se necessário
- Compliance + rastreabilidade

---

## Performance

### Tempos Típicos

| Fase | Tempo Esperado |
|------|---|
| Planejamento (Opus) | 3-5s |
| Geração iterativa | 2-4s |
| Validação | <100ms |
| Git operations | 500ms-1s |
| **Total** | **6-10s** |

### Otimizações

- **Parallelização:** Múltiplos intents podem ser processados em paralelo
- **Cache:** Respostas de Opus não são cacheadas (cada geração é fresca)
- **Streaming:** Não usa streaming; aguarda resposta completa

---

## Limitações

1. **Modelo:** Apenas Claude Opus 4.1 (não suporta Sonnet/Haiku para geração)
2. **Tamanho:** Max 4000 tokens por geração (Fase 1), 3000 (Fase 2)
3. **Artefatos:** Sempre 4 tipos (agent.md, test.ts, docs.md, keywords.json)
4. **Frontmatter:** YAML simplificado (sem parsing de tipos complexos)
5. **Branching:** Requer repositório git local com permissões de escrita

---

## Roadmap

- [ ] Suporte a custom templates para artefatos
- [ ] Persistência de conversation logs em database
- [ ] Integração com SharePoint para upload automático
- [ ] Validação contra CLAUDE.md existente
- [ ] Geração de skills.md automático
- [ ] Benchmark comparativo de gerações

---

## Referências

- **Arquivo de exemplo:** `src/examples/code-generator-integration.ts`
- **Testes:** `src/services/__tests__/code-generator.test.ts`
- **Tipos:** `src/services/code-generator.ts` (linhas 1-120)
- **Agent template:** `.claude/agents/agente-saneamento.md`

---

## Suporte

- **Issues:** Abra issue com label `code-generator`
- **Contribuições:** PRs bem-vindas; siga CONTRIBUTING.md
- **Email:** mneves@mantaassociados.com
