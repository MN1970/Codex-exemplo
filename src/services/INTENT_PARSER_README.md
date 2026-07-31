# Intent Parser — NLU com Claude API

**Versão:** 1.0  
**Propósito:** Análise semântica de mensagens de usuário → estrutura tipada de intents  
**Dependências:** `@anthropic-ai/sdk`, TypeScript 5.0+

---

## 🎯 Visão Geral

O Intent Parser é um motor de **Natural Language Understanding (NLU)** que converte linguagem natural em instruções estruturadas e executáveis.

```
User Input
    ↓
Claude API (NLU + semantic analysis)
    ↓
ParsedIntent { action, target, confidence, params, ...}
    ↓
Validation + Enrichment
    ↓
Execution Plan
```

### Features

- ✅ **NLU via Claude API** — análise semântica completa
- ✅ **Typed Output** — `action`, `target`, `params` estruturados
- ✅ **Confidence Scoring** — 0.0–1.0, baseado em certeza semântica
- ✅ **Parameter Extraction** — email, URL, data, agent codes, etc.
- ✅ **Validation** — checks de negócio (ação + target válidos?)
- ✅ **Clarifying Questions** — fallback para intents ambíguos
- ✅ **Heuristics** — enriquecimento com regex patterns locais

---

## 📦 Tipos Principais

### `ParsedIntent`

```typescript
interface ParsedIntent {
  action: ActionType;           // "create" | "update" | "delete" | ...
  target: TargetType;           // "agent" | "workflow" | "config" | ...
  confidence: number;            // 0.0 – 1.0
  params: Record<string, any>;   // {segment: "saneamento", ...}
  reasoning: string;             // "Ação clara, target identificado"
  clarifyingQuestions?: string[]; // Perguntas se confidence < 0.5
  rawIntentTokens: string[];     // Tokens extraídos do Claude
  executionSuggestion?: string;  // "Use: manta-08 create-agent"
}
```

### `ActionType`

Ações que o sistema reconhece:

```typescript
type ActionType =
  | "create"    // Criar novo recurso
  | "update"    // Modificar existente
  | "delete"    // Remover
  | "read"      // Obter um item
  | "list"      // Listar vários
  | "execute"   // Rodar workflow/agente
  | "deploy"    // Deployar em ambiente
  | "schedule"  // Agendar para mais tarde
  | "cancel"    // Cancelar operação
  | "clarify";  // Pedir esclarecimento
```

### `TargetType`

O que as ações afetam:

```typescript
type TargetType =
  | "agent"       // Manta agentes
  | "workflow"    // Fluxos/pipelines
  | "document"    // Arquivos/reports
  | "schedule"    // Cronogramas
  | "config"      // Configurações
  | "deployment"  // Ambientes
  | "user"        // Usuários
  | "notification"// Notificações
  | "report"      // Relatórios
  | "unknown";    // Desconhecido
```

---

## 🚀 Como Usar

### 1. Instância do Parser

```typescript
import { IntentParser } from "./services/intent-parser";

const parser = new IntentParser({
  model: "claude-3-5-sonnet-20241022",
  minConfidenceThreshold: 0.4,
  enableClarifyingQuestions: true,
});
```

### 2. Parse Simples

```typescript
const intent = await parser.parse("cria um novo agente para saneamento");

console.log(intent.action);      // "create"
console.log(intent.target);      // "agent"
console.log(intent.confidence);  // 0.92
console.log(intent.params);      // { segment: "saneamento" }
```

### 3. Parse + Validação

```typescript
import { parseAndValidate } from "./services/intent-parser";

const { intent, validation } = await parseAndValidate(
  "atualizar o maestro router"
);

if (!validation.isValid) {
  console.error("Validation failed:", validation.errors);
}

console.log(intent.action); // "update"
```

### 4. Com Factory Function

```typescript
import { getIntentParser } from "./services/intent-parser";

// Singleton lazy-loaded
const parser = getIntentParser();
const intent = await parser.parse(userMessage);
```

---

## 🧠 Prompt Engineering

### System Prompt (Claude Context)

O parser usa um system prompt que define:

1. **Ações válidas** com sinônimos
2. **Targets válidos** com sinônimos
3. **Exemplos de intents** (few-shot)
4. **Formato de saída JSON** esperado
5. **Diretrizes de confiança**

```
AÇÕES VÁLIDAS:
- create: criar, gerar, novo, setup, initialize, ...
- update: atualizar, modificar, editar, change, ...
- execute: executar, rodar, run, trigger, start, ...
[...]

EXEMPLOS:
1. Entrada: "cria um agente novo para saneamento"
   → action: create, target: agent, confidence: 0.95

2. Entrada: "agende para amanhã"
   → action: clarify, target: unknown, confidence: 0.3
   → clarifyingQuestions: ["O que agendar?", "Para qual horário?"]

DIRETRIZES DE CONFIANÇA:
- 0.9+: Ação e target muito claros
- 0.7-0.9: Ação clara, detalhes incertos
- 0.5-0.7: Intenção parcialmente clara
- <0.5: Muito incerto, gere perguntas
```

### Por que funciona?

1. **Few-shot examples** — Claude aprende do padrão
2. **Explicitness** — Listar ações/targets deixa claro o escopo
3. **JSON structure** — Output tipado facilita parsing
4. **Confidence anchoring** — Diretrizes numéricas guiam o modelo

---

## 📊 Confidence Scoring

### Algoritmo

```
confidence = Claude_confidence_rating
           + heuristic_boost (se parâmetros extraídos)
           + target_match_bonus (se target identificado)
           clamped to [0.0, 1.0]
```

### Thresholds

| Faixa | Interpretação | Ação |
|-------|---------------|------|
| 0.9–1.0 | Muito claro | ✅ Executar |
| 0.7–0.9 | Claro | ✅ Executar com confirmação |
| 0.5–0.7 | Parcial | ⚠️ Clarifying questions |
| <0.5 | Ambíguo | ❌ Pedir reescrita |

### Exemplo

```typescript
const intent = await parser.parse("cria um agente");

// confidence = 0.75
// Razão: ação clara ("create"), mas target genérico ("agent")
// Ação: solicitar confirmação do segment/tipo

if (intent.confidence < 0.85) {
  console.log("Confirme:", intent.clarifyingQuestions);
  // ["Qual segmento? (saneamento, energia, rodovias, ...)"]
}
```

---

## 🔍 Extração de Parâmetros

### Heurísticas Locais

O parser enriquece a saída do Claude com padrões regex:

```typescript
const PARAM_PATTERNS = {
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
  url: /https?:\/\/[^\s]+/,
  date: /\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4}/,
  number: /\d+/,
  agent_code: /s[1-9]\d{0}|manta-\d{2}/i,
};
```

### Exemplo

```typescript
const intent = await parser.parse(
  "criar usuário com email test@example.com em 2025-12-31"
);

intent.params = {
  email: "test@example.com",
  date: "2025-12-31",
};
```

---

## ✅ Validação

### método `validateIntent(intent)`

Checks estruturais:

```typescript
const validation = parser.validateIntent(intent);

validation = {
  isValid: boolean,
  errors: string[],      // Bloqueadores
  warnings: string[]     // Avisos
}
```

### Regras

| Situação | Erro/Aviso |
|----------|-----------|
| confidence < minThreshold | ❌ Erro |
| action não reconhecida | ❌ Erro |
| create/update/deploy sem target | ❌ Erro |
| schedule sem date | ⚠️ Aviso |
| action != clarify mas sem params | ⚠️ Aviso |

### Exemplo

```typescript
const { intent, validation } = await parseAndValidate(
  "atualizar o maestro"
);

if (validation.isValid) {
  // Prosseguir com execução
} else {
  console.error(validation.errors);
  // ["Alvo não identificado para ação de modificação"]
}
```

---

## 🔄 Clarifying Questions

### Quando Ativadas

Se `confidence < 0.5` e `enableClarifyingQuestions=true`:

```typescript
{
  action: "clarify",
  target: "unknown",
  confidence: 0.3,
  clarifyingQuestions: [
    "O que você quer agendar?",
    "Para qual data/hora?",
    "Em qual contexto (agente, workflow, etc)?"
  ]
}
```

### Exemplo

```typescript
const intent = await parser.parse("agende");

if (intent.action === "clarify") {
  // Apresentar UI com perguntas
  for (const q of intent.clarifyingQuestions || []) {
    console.log(`❓ ${q}`);
  }
}
```

---

## 💡 Sugestões de Execução

### método `generateExecutionSuggestion(intent)`

Retorna uma sugestão de como executar o intent:

```typescript
const intent = await parser.parse("cria um agente para saneamento");
const suggestion = parser.generateExecutionSuggestion(intent);

// "Criar novo agente saneamento. Use: manta-16 agente-novo"
```

### Mapeamento

| Action | Target | Sugestão |
|--------|--------|----------|
| create | agent | `manta-16 agente-novo` |
| create | workflow | `manta-07 workflow-create` |
| update | config | `update-config --merge` |
| execute | workflow | Disparar workflow |
| deploy | agent | `npm run deploy` |

---

## 🔗 Integração com Maestro Router

O Intent Parser trabalha em conjunto com o Maestro Router:

```
User Input
    ↓
[Intent Parser] → ParsedIntent
    ↓
[Maestro Router] → RoutingResult (se target="agent")
    ↓
[Execution] → Deploy para agente específico
```

### Exemplo Integrado

```typescript
import { IntentParser } from "./intent-parser";
import { MaestroRouter } from "./maestro-router";

const parser = new IntentParser();
const router = new MaestroRouter();

const intent = await parser.parse("executa saneamento");

if (intent.target === "agent" && intent.params.segment) {
  const routing = router.route(`${intent.params.segment} workflow`);
  console.log(`Route to: ${routing.agent.name}`);
}
```

---

## 🧪 Testes

### Executar Test Suite

```bash
npm test -- src/services/__tests__/intent-parser.test.ts
```

### Exemplos Integrados

```typescript
import { runIntentParserExamples } from "./services/intent-parser";

await runIntentParserExamples();
// Testa 6 mensagens diferentes e exibe resultados
```

### Modo Interativo

```typescript
import { runInteractiveMode } from "./examples/intent-parser-integration";

await runInteractiveMode();
// Prompt > type commands
```

---

## 📈 Performance & Cotas

### Claude API Calls

- **1 call por parse** (não batched)
- ~400–600 tokens input (system + user message)
- ~200–400 tokens output (JSON intent)
- **Custo típico:** ~$0.0005/parse (Sonnet 3.5)

### Otimizações

1. **Cache System Prompt** — reutilizar entre calls
2. **Confidence threshold** — skip parsing em high-confidence heuristics
3. **Batch processing** — agrupar múltiplos parses (future)

### Exemplo com Caching

```typescript
// Memoize parser instance
const parser = getIntentParser(); // Singleton

const intent = await parser.parse(userMessage);
// Reutiliza Claude config entre calls
```

---

## 🔧 Configuração

### Opções

```typescript
interface IntentParserConfig {
  apiKey?: string;                        // Default: ANTHROPIC_API_KEY env
  model?: string;                         // Default: claude-3-5-sonnet-20241022
  maxConfidenceThreshold?: number;        // Default: 0.95
  minConfidenceThreshold?: number;        // Default: 0.3
  enableClarifyingQuestions?: boolean;    // Default: true
  contextWindow?: number;                 // Default: 8000 chars
}
```

### Exemplo

```typescript
const parser = new IntentParser({
  model: "claude-3-opus-20240229",
  minConfidenceThreshold: 0.6,
  enableClarifyingQuestions: false,
});
```

---

## 🎓 Exemplos Completos

### 1. Parse Simples

```typescript
const intent = await parseIntent("cria um agente");
console.log(intent.action);   // "create"
console.log(intent.target);   // "agent"
```

### 2. Parse + Validação

```typescript
const { intent, validation } = await parseAndValidate(
  "deletar o workflow antigo"
);

if (!validation.isValid) {
  console.error(validation.errors);
} else {
  console.log("Ready to execute:", intent.action);
}
```

### 3. Com Routing (Maestro)

```typescript
const intent = await parseIntent("executa o agente de saneamento");

const router = new MaestroRouter();
const routing = router.route("saneamento");

console.log(`Execute via: ${routing.agent.name}`);
```

### 4. Fluxo Completo

```typescript
import { CommandProcessingPipeline } from "./examples/intent-parser-integration";

const pipeline = new CommandProcessingPipeline();
const result = await pipeline.processUserCommand(
  "criar agente para energia"
);

console.log(result.executionPlan.steps);
// Plano com 3–5 steps estruturados
```

---

## 📋 Checklist de Deploy

- [ ] `ANTHROPIC_API_KEY` configurada em `.env`
- [ ] Testes passam: `npm test -- intent-parser.test.ts`
- [ ] Exemplos rodados: `runIntentParserExamples()`
- [ ] Integração com Maestro testada
- [ ] Confidence thresholds ajustados para seu domínio
- [ ] Logs e monitoring em place

---

## 🚨 Troubleshooting

### Erro: "ANTHROPIC_API_KEY não configurada"

```bash
export ANTHROPIC_API_KEY="sk-..."
# ou em .env
ANTHROPIC_API_KEY=sk-...
```

### Confidence muito baixa?

1. Verificar se intent é ambíguo (ex: "agende")
2. Adicionar mais contexto à mensagem
3. Ajustar `minConfidenceThreshold` para seu case

### Parâmetros não extraídos?

Verificar:
- Padrão regex cobre seu formato? (ex: email)
- Claude identificou o parâmetro na análise?
- Mensagem é clara o suficiente?

### Claude retorna invalid JSON?

1. Verificar logs de response text
2. Aumentar `max_tokens` em client.messages.create()
3. Usar modelo mais robusto (Opus se crítico)

---

## 📚 Referências

- [Claude API Docs](https://docs.anthropic.com)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Maestro Router](./maestro-router.ts)
- [Integration Example](../examples/intent-parser-integration.ts)

---

## 📝 Licença

MIT — Manta Associados 2025
