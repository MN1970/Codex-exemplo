# Intent Parser — Quick Start Guide

## O que é?

Um motor de **NLU (Natural Language Understanding)** que converte linguagem natural em comandos estruturados usando a Claude API.

```
"cria um agente para saneamento"
         ↓ [Claude NLU]
{
  action: "create",
  target: "agent",
  confidence: 0.92,
  params: { segment: "saneamento" }
}
```

---

## Instalação (1 minuto)

### 1. Verificar dependências

```bash
npm ls @anthropic-ai/sdk
```

✅ Já está em `package.json`

### 2. Configurar API Key

```bash
export ANTHROPIC_API_KEY="sk-..."
```

Ou em `.env`:
```
ANTHROPIC_API_KEY=sk-...
```

### 3. Pronto!

```bash
npm run type-check   # Verificar tipos
npm test             # Rodar testes (opcional)
```

---

## Uso (3 Padrões)

### Padrão 1: Parse Simples

```typescript
import { parseIntent } from "./services/intent-parser";

const intent = await parseIntent("cria um agente para saneamento");

console.log(intent.action);       // "create"
console.log(intent.target);       // "agent"
console.log(intent.confidence);   // 0.92
console.log(intent.params);       // { segment: "saneamento" }
```

### Padrão 2: Parse + Validação

```typescript
import { parseAndValidate } from "./services/intent-parser";

const { intent, validation } = await parseAndValidate(
  "deletar o workflow antigo"
);

if (!validation.isValid) {
  console.error("❌ Erros:", validation.errors);
} else {
  console.log("✅ Pronto para executar");
}
```

### Padrão 3: Integração com Maestro

```typescript
import { IntentParser } from "./services/intent-parser";
import { MaestroRouter } from "./services/maestro-router";

const parser = new IntentParser();
const router = new MaestroRouter();

const intent = await parser.parse("executa saneamento");

if (intent.target === "agent") {
  const routing = router.route("saneamento");
  console.log(`→ ${routing.agent.name}`);
}
```

---

## Tipos Reconhecidos

### Actions (o que fazer)

```
create   → criar novo
update   → modificar existente
delete   → remover
read     → obter um
list     → listar vários
execute  → rodar/disparar
deploy   → publicar
schedule → agendar
cancel   → cancelar
clarify  → pedir esclarecimento
```

### Targets (onde fazer)

```
agent         → Manta agentes
workflow      → Fluxos/pipelines
document      → Arquivos/reports
config        → Configurações
deployment    → Ambientes (prod, staging)
schedule      → Cronogramas
user          → Usuários
notification  → Notificações
report        → Relatórios
```

---

## Exemplos Reais

```typescript
// ✅ Claro e estruturado
parseIntent("criar agente para saneamento com setor=água")
→ { action: "create", target: "agent", confidence: 0.95 }

// ⚠️ Confiança média (detalhes incertos)
parseIntent("atualizar a config")
→ { action: "update", target: "config", confidence: 0.7 }

// ❓ Ambíguo (pede esclarecimento)
parseIntent("agende algo")
→ { action: "clarify", target: "unknown", confidence: 0.2,
    clarifyingQuestions: ["O que agendar?", "Para quando?"] }
```

---

## Confidence Scores

| Faixa | Significado | Ação |
|-------|-----------|------|
| 0.9–1.0 | Muito claro | ✅ Executar |
| 0.7–0.9 | Claro | ⚠️ Confirmar |
| 0.5–0.7 | Parcial | ❓ Clarify |
| <0.5 | Ambíguo | ❌ Rejeitar |

---

## Features

### ✨ Extração Automática de Parâmetros

```typescript
const intent = await parseIntent(
  "criar usuário com email test@example.com em 2025-12-31"
);

console.log(intent.params);
// { email: "test@example.com", date: "2025-12-31" }
```

### ✨ Sugestões de Execução

```typescript
const intent = await parseIntent("cria agente");
const suggestion = parser.generateExecutionSuggestion(intent);

// "Criar novo agente. Use: manta-16 agente-novo"
```

### ✨ Validação Estrutural

```typescript
const { validation } = await parseAndValidate(intent);

validation.errors    // Bloqueadores
validation.warnings  // Avisos
```

---

## Configuração Avançada

```typescript
const parser = new IntentParser({
  model: "claude-3-opus-20240229",          // Modelo
  minConfidenceThreshold: 0.4,              // Limite mínimo
  maxConfidenceThreshold: 0.95,             // Limite máximo
  enableClarifyingQuestions: true,          // Perguntas de esclarecimento
  contextWindow: 8000,                      // Chars máximo
});
```

---

## Testes

### Rodar Suite Completa

```bash
npm test -- src/services/__tests__/intent-parser.test.ts
```

### Exemplos Integrados

```typescript
import { runIntentParserExamples } from "./services/intent-parser";

await runIntentParserExamples();
// Testa 6 casos diferentes
```

### Modo Interativo

```typescript
import { runInteractiveMode } from "./examples/intent-parser-integration";

await runInteractiveMode();
// Prompt interativo > type commands
```

---

## Troubleshooting

### Erro: "ANTHROPIC_API_KEY não configurada"

```bash
export ANTHROPIC_API_KEY="sk-..."
```

### Confiança muito baixa?

1. **Intent é ambíguo?** → Adicionar mais contexto
2. **Thresholds errados?** → Ajustar `minConfidenceThreshold`
3. **Modelo fraco?** → Usar `claude-3-opus` (mais potente)

### Parâmetros não extraídos?

Verificar:
- ✅ Email? → Deve ter `@` e domínio
- ✅ URL? → Deve ter `http://` ou `https://`
- ✅ Data? → Formato `YYYY-MM-DD` ou `DD/MM/YYYY`
- ✅ Agent code? → Padrão `s1`–`s10`, `manta-XX`

---

## Arquitetura

```
Intent Parser
├── System Prompt (Few-shot + Guidelines)
├── Claude API Call
├── JSON Extraction
├── Validation Layer
├── Heuristics (Regex patterns)
└── Output: ParsedIntent

Integração:
└── Maestro Router (para agent actions)
```

---

## Documentação Completa

Para detalhes completos, veja: [INTENT_PARSER_README.md](./src/services/INTENT_PARSER_README.md)

Tópicos:
- Prompt Engineering detalhado
- Algoritmo de Confidence Scoring
- Validação estrutural
- Exemplos avançados
- Troubleshooting aprofundado

---

## Próximos Passos

1. ✅ **Usar em sua app** → `parseIntent(userMessage)`
2. ✅ **Integrar com Maestro** → Routing automático
3. ✅ **Customizar prompts** → Seu domínio específico
4. ✅ **Monitorar metrics** → Confidence distribution

---

**Versão:** 1.0  
**Status:** Production-ready  
**Autor:** Manta Associados  
**License:** MIT
