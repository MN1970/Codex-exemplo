/**
 * Intent Parser — Motor de análise semântica (NLU) usando Claude API
 * Versão: 1.0
 * Propósito: Parse de intenções de usuário → ações estruturadas
 * Algoritmo: Claude API + confidence scoring + fallback heurístico
 */

import Anthropic from "@anthropic-ai/sdk";

/**
 * Ações válidas que o sistema pode executar
 */
export type ActionType =
  | "create"
  | "update"
  | "delete"
  | "read"
  | "list"
  | "execute"
  | "deploy"
  | "schedule"
  | "cancel"
  | "clarify";

/**
 * Alvos (targets) que as ações podem afetar
 */
export type TargetType =
  | "agent"
  | "workflow"
  | "document"
  | "schedule"
  | "config"
  | "deployment"
  | "user"
  | "notification"
  | "report"
  | "unknown";

/**
 * Resultado do parse de intent com estrutura tipada
 */
export interface ParsedIntent {
  action: ActionType;
  target: TargetType;
  confidence: number; // 0.0 - 1.0
  params: Record<string, unknown>;
  reasoning: string;
  clarifyingQuestions?: string[];
  rawIntentTokens: string[];
  executionSuggestion?: string;
}

/**
 * Configuração para o intent parser
 */
export interface IntentParserConfig {
  apiKey?: string;
  model?: string;
  maxConfidenceThreshold?: number;
  minConfidenceThreshold?: number;
  enableClarifyingQuestions?: boolean;
  contextWindow?: number;
}

/**
 * Interface para validação de intent
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Dicionário de ações conhecidas e seus sinônimos
 */
const ACTION_SYNONYMS: Record<ActionType, string[]> = {
  create: [
    "criar",
    "criar novo",
    "gerar",
    "fazer",
    "setup",
    "initialize",
    "instantiate",
    "new",
    "open",
    "abrir",
  ],
  update: [
    "atualizar",
    "modificar",
    "editar",
    "change",
    "alter",
    "patch",
    "adjust",
    "mudar",
  ],
  delete: [
    "deletar",
    "remover",
    "remove",
    "excluir",
    "drop",
    "uninstall",
    "destroy",
  ],
  read: [
    "ler",
    "obter",
    "get",
    "fetch",
    "retrieve",
    "show",
    "visualize",
    "mostra",
  ],
  list: [
    "listar",
    "enumerate",
    "todas",
    "list all",
    "mostrar lista",
    "ver todos",
  ],
  execute: [
    "executar",
    "rodar",
    "run",
    "trigger",
    "start",
    "launch",
    "begin",
    "disparar",
  ],
  deploy: [
    "deploy",
    "deployar",
    "publicar",
    "publish",
    "release",
    "go live",
    "promote",
  ],
  schedule: [
    "agendar",
    "schedule",
    "tempo",
    "quando",
    "time",
    "later",
    "em breve",
  ],
  cancel: [
    "cancelar",
    "cancel",
    "abort",
    "stop",
    "parar",
    "interrupt",
    "abandon",
  ],
  clarify: [
    "esclarecer",
    "clarify",
    "explicar",
    "dúvida",
    "não entendi",
    "help",
  ],
};

/**
 * Dicionário de targets conhecidos
 */
const TARGET_SYNONYMS: Record<TargetType, string[]> = {
  agent: [
    "agent",
    "agente",
    "agentes",
    "ia",
    "manta",
    "bot",
    "maestro",
    "s1",
    "s2",
    "s3",
    "s4",
    "s5",
    "s6",
    "s7",
    "s8",
    "s9",
    "s10",
  ],
  workflow: [
    "workflow",
    "fluxo",
    "processo",
    "pipeline",
    "rotina",
    "routine",
    "automation",
  ],
  document: [
    "documento",
    "documento",
    "arquivo",
    "file",
    "pdf",
    "doc",
    "report",
    "relatório",
  ],
  schedule: [
    "cronograma",
    "schedule",
    "agenda",
    "timing",
    "deadline",
    "prazo",
  ],
  config: [
    "config",
    "configuração",
    "settings",
    "parâmetros",
    "parameters",
    "preferences",
  ],
  deployment: [
    "deployment",
    "deploy",
    "release",
    "staging",
    "production",
    "prod",
    "ambiente",
  ],
  user: ["user", "usuário", "account", "conta", "profile", "perfil"],
  notification: [
    "notificação",
    "notification",
    "alerta",
    "alert",
    "mensagem",
    "message",
  ],
  report: ["report", "relatório", "resultado", "resultado"],
  unknown: [],
};

/**
 * Sistema de extração de parâmetros heurísticos
 */
const PARAM_PATTERNS = {
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
  url: /https?:\/\/[^\s]+/,
  date: /\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4}/,
  number: /\d+/,
  agent_code: /s[1-9]\d{0}|manta-\d{2}/i,
};

/**
 * Classe IntentParser — motor principal de análise de intents
 */
export class IntentParser {
  private client: Anthropic;
  private config: Required<IntentParserConfig>;
  private systemPrompt: string;

  constructor(config: IntentParserConfig = {}) {
    const apiKey = config.apiKey || process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      throw new Error(
        "ANTHROPIC_API_KEY não configurada. Configure via config ou env var."
      );
    }

    this.client = new Anthropic({ apiKey });
    this.config = {
      apiKey,
      model: config.model || "claude-3-5-sonnet-20241022",
      maxConfidenceThreshold: config.maxConfidenceThreshold ?? 0.95,
      minConfidenceThreshold: config.minConfidenceThreshold ?? 0.3,
      enableClarifyingQuestions: config.enableClarifyingQuestions ?? true,
      contextWindow: config.contextWindow || 8000,
    };

    this.systemPrompt = this.buildSystemPrompt();
  }

  /**
   * Constrói o prompt de sistema para o Claude
   * Inclui:
   * - Definição de ações e targets
   * - Exemplos de intents
   * - Instruções de JSON estruturado
   * - Guidelines de confiança
   */
  private buildSystemPrompt(): string {
    return `Você é um analisador de intenção (NLU) para um sistema de automação de infraestrutura.

Sua tarefa é extrair a intenção do usuário e retornar um JSON estruturado.

AÇÕES VÁLIDAS:
${Object.entries(ACTION_SYNONYMS)
  .map(([action, synonyms]) => `- ${action}: ${synonyms.join(", ")}`)
  .join("\n")}

TARGETS VÁLIDOS:
${Object.entries(TARGET_SYNONYMS)
  .map(([target, synonyms]) => `- ${target}: ${synonyms.join(", ")}`)
  .join("\n")}

INSTRUÇÕES:
1. Parse a mensagem do usuário em componentes estruturados
2. Identifique a ação principal (create, update, read, list, execute, deploy, schedule, cancel, clarify)
3. Identifique o alvo (agent, workflow, document, schedule, config, deployment, user, notification, report, unknown)
4. Extraia parâmetros relevantes (nome, email, data, URL, etc.)
5. Retorne confidence score entre 0.0 (muito incerto) e 1.0 (certo)
6. Se confidence < 0.5, gere clarifying questions
7. Retorne JSON bem-formado com a estrutura exata

ESTRUTURA DE SAÍDA (JSON):
{
  "action": "create|update|delete|read|list|execute|deploy|schedule|cancel|clarify",
  "target": "agent|workflow|document|schedule|config|deployment|user|notification|report|unknown",
  "confidence": 0.0-1.0,
  "params": { ... },
  "reasoning": "uma linha explicando a análise",
  "clarifyingQuestions": ["pergunta 1", "pergunta 2"],
  "rawIntentTokens": ["token1", "token2"],
  "executionSuggestion": "sugestão de como executar, se aplicável"
}

EXEMPLOS:
1. Entrada: "cria um agente novo para saneamento"
   - action: create
   - target: agent
   - confidence: 0.95
   - params: { segment: "saneamento" }

2. Entrada: "quero atualizar a config do maestro"
   - action: update
   - target: config
   - confidence: 0.85
   - params: { resource: "maestro" }

3. Entrada: "executa o workflow de candidaturas"
   - action: execute
   - target: workflow
   - confidence: 0.92
   - params: { workflowName: "candidaturas" }

4. Entrada: "agende para amanhã"
   - action: clarify
   - target: unknown
   - confidence: 0.3
   - clarifyingQuestions: ["O que você quer agendar?", "Para qual horário especificamente?"]

DIRETRIZES DE CONFIANÇA:
- 0.9+: Ação e target muito claros
- 0.7-0.9: Ação clara, alguns detalhes incertos
- 0.5-0.7: Intenção parcialmente clara, precisa contexto
- <0.5: Muito incerto, gere perguntas
`;
  }

  /**
   * Parse principal de intent com Claude API
   * @param userMessage Mensagem do usuário
   * @returns ParsedIntent com análise completa
   */
  async parse(userMessage: string): Promise<ParsedIntent> {
    try {
      // Validação de entrada
      if (!userMessage || userMessage.trim().length === 0) {
        return this.createFallbackIntent(
          "Mensagem vazia",
          [],
          0.0,
          ["clarify"]
        );
      }

      const trimmedMessage = userMessage.trim().slice(0, this.config.contextWindow);

      // Chamar Claude API para análise semântica
      const response = await this.client.messages.create({
        model: this.config.model,
        max_tokens: 1024,
        system: this.systemPrompt,
        messages: [
          {
            role: "user",
            content: `Analise a seguinte mensagem de usuário:\n\n"${trimmedMessage}"`,
          },
        ],
      });

      // Extrair texto da resposta
      const responseText =
        response.content[0].type === "text" ? response.content[0].text : "";

      // Parse JSON da resposta
      const parsedResponse = this.extractJsonFromResponse(responseText);

      // Validação e normalização
      const validated = this.validateAndNormalize(parsedResponse);

      // Enriquecimento com heurísticas locais
      const enriched = this.enrichWithHeuristics(validated, trimmedMessage);

      return enriched;
    } catch (error) {
      console.error("Erro no intent parser:", error);
      return this.createFallbackIntent(
        "Erro ao processar intent",
        [],
        0.0,
        ["clarify"]
      );
    }
  }

  /**
   * Extrai JSON de uma resposta do Claude
   */
  private extractJsonFromResponse(text: string): Partial<ParsedIntent> {
    try {
      // Tenta encontrar JSON entre chaves
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return {};
    } catch (error) {
      console.warn("Falha ao extrair JSON:", error);
      return {};
    }
  }

  /**
   * Valida e normaliza a resposta do Claude
   */
  private validateAndNormalize(
    response: Partial<ParsedIntent>
  ): ParsedIntent {
    const action = this.normalizeAction(response.action as string);
    const target = this.normalizeTarget(response.target as string);
    const confidence = this.normalizeConfidence(response.confidence as number);

    return {
      action: action || "clarify",
      target: target || "unknown",
      confidence,
      params: response.params || {},
      reasoning:
        response.reasoning ||
        "Intent análise via Claude API (fallback validation)",
      clarifyingQuestions: response.clarifyingQuestions || [],
      rawIntentTokens: response.rawIntentTokens || [],
      executionSuggestion: response.executionSuggestion,
    };
  }

  /**
   * Enriquece o intent com heurísticas locais
   */
  private enrichWithHeuristics(
    intent: ParsedIntent,
    userMessage: string
  ): ParsedIntent {
    // Detecta padrões adicionais
    const params = { ...intent.params };

    // Email
    const emailMatch = userMessage.match(PARAM_PATTERNS.email);
    if (emailMatch) params.email = emailMatch[0];

    // URL
    const urlMatch = userMessage.match(PARAM_PATTERNS.url);
    if (urlMatch) params.url = urlMatch[0];

    // Data
    const dateMatch = userMessage.match(PARAM_PATTERNS.date);
    if (dateMatch) params.date = dateMatch[0];

    // Agent Code
    const agentMatch = userMessage.match(PARAM_PATTERNS.agent_code);
    if (agentMatch) params.agent = agentMatch[0].toLowerCase();

    // Boost confidence se houver ação + target + parâmetros claros
    if (intent.action !== "clarify" && Object.keys(params).length > 0) {
      intent.confidence = Math.min(1.0, intent.confidence + 0.1);
    }

    intent.params = params;
    return intent;
  }

  /**
   * Normaliza ação para um dos tipos válidos
   */
  private normalizeAction(action?: string): ActionType | undefined {
    if (!action) return undefined;

    const lower = action.toLowerCase().trim();

    for (const [validAction, synonyms] of Object.entries(ACTION_SYNONYMS)) {
      if (lower === validAction || synonyms.includes(lower)) {
        return validAction as ActionType;
      }
    }

    // Busca parcial
    for (const [validAction, synonyms] of Object.entries(ACTION_SYNONYMS)) {
      if (
        synonyms.some((syn) => lower.includes(syn) || syn.includes(lower))
      ) {
        return validAction as ActionType;
      }
    }

    return undefined;
  }

  /**
   * Normaliza target para um dos tipos válidos
   */
  private normalizeTarget(target?: string): TargetType | undefined {
    if (!target) return undefined;

    const lower = target.toLowerCase().trim();

    for (const [validTarget, synonyms] of Object.entries(TARGET_SYNONYMS)) {
      if (lower === validTarget || synonyms.includes(lower)) {
        return validTarget as TargetType;
      }
    }

    // Busca parcial
    for (const [validTarget, synonyms] of Object.entries(TARGET_SYNONYMS)) {
      if (
        synonyms.some((syn) => lower.includes(syn) || syn.includes(lower))
      ) {
        return validTarget as TargetType;
      }
    }

    return undefined;
  }

  /**
   * Normaliza confidence para [0, 1]
   */
  private normalizeConfidence(confidence?: number): number {
    if (confidence === undefined || confidence === null) return 0.5;
    const num = Number(confidence);
    if (isNaN(num)) return 0.5;
    return Math.max(0, Math.min(1, num));
  }

  /**
   * Cria um intent fallback em caso de erro
   */
  private createFallbackIntent(
    reasoning: string,
    tokens: string[],
    confidence: number,
    questions?: string[]
  ): ParsedIntent {
    return {
      action: "clarify",
      target: "unknown",
      confidence,
      params: {},
      reasoning,
      clarifyingQuestions:
        questions || [
          "Você pode ser mais específico sobre o que deseja fazer?",
        ],
      rawIntentTokens: tokens,
    };
  }

  /**
   * Valida se um intent é executável
   */
  validateIntent(intent: ParsedIntent): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Validações críticas
    if (!intent.action) {
      errors.push("Ação não identificada");
    }

    if (intent.confidence < this.config.minConfidenceThreshold) {
      errors.push(
        `Confiança muito baixa (${intent.confidence.toFixed(2)} < ${this.config.minConfidenceThreshold})`
      );
    }

    // Validações por tipo de ação
    if (["create", "update", "deploy"].includes(intent.action)) {
      if (!intent.target || intent.target === "unknown") {
        errors.push("Alvo não identificado para ação de modificação");
      }
    }

    if (intent.action === "schedule" && !intent.params.date) {
      warnings.push("Ação schedule sem data especificada");
    }

    // Validações de parâmetros esperados
    if (intent.confidence > this.config.maxConfidenceThreshold) {
      if (Object.keys(intent.params).length === 0) {
        warnings.push("High confidence mas sem parâmetros extraídos");
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Gera sugestões de ação baseadas no intent
   */
  generateExecutionSuggestion(intent: ParsedIntent): string {
    const { action, target, params } = intent;

    const suggestions: Record<string, Record<string, string>> = {
      create: {
        agent: `Criar novo agente ${(params.segment as string) || ""}. Use: manta-16 agente-novo`,
        workflow: `Criar workflow. Use: manta-07 workflow-create`,
        config: `Atualizar configuração. Use: update-config`,
      },
      update: {
        agent: `Atualizar agente. Use: manta-16 agente-update`,
        config: `Aplicar mudanças de config. Use: update-config --merge`,
      },
      execute: {
        workflow: `Executar workflow ${(params.workflowName as string) || ""}`,
        agent: `Disparar agente ${(params.agent as string) || ""}`,
      },
      deploy: {
        agent: `Deploy de agente. Use: npm run deploy`,
        deployment: `Deploy em ${(params.environment as string) || "staging"}`,
      },
    };

    return (
      suggestions[action]?.[target] ||
      `Executar ação '${action}' sobre '${target}'`
    );
  }
}

/**
 * Factory function para obter instância singleton
 */
let parserInstance: IntentParser | null = null;

export function getIntentParser(
  config?: IntentParserConfig
): IntentParser {
  if (!parserInstance || config) {
    parserInstance = new IntentParser(config);
  }
  return parserInstance;
}

/**
 * Função auxiliar de parse rápido
 */
export async function parseIntent(
  userMessage: string,
  config?: IntentParserConfig
): Promise<ParsedIntent> {
  const parser = getIntentParser(config);
  return parser.parse(userMessage);
}

/**
 * Função auxiliar para validação
 */
export async function parseAndValidate(
  userMessage: string,
  config?: IntentParserConfig
): Promise<{
  intent: ParsedIntent;
  validation: ValidationResult;
}> {
  const parser = getIntentParser(config);
  const intent = await parser.parse(userMessage);
  const validation = parser.validateIntent(intent);

  return { intent, validation };
}

/**
 * Exemplos de uso para testes
 */
export async function runIntentParserExamples(): Promise<void> {
  const parser = new IntentParser();

  const testMessages = [
    "cria um novo agente para saneamento",
    "quero atualizar a configuração do maestro",
    "executa o workflow de candidaturas",
    "agende o deploy para amanhã",
    "lista todos os agentes disponíveis",
    "não entendi, como funciona?",
  ];

  console.log("\n=== Intent Parser Examples ===\n");

  for (const message of testMessages) {
    console.log(`📝 Entrada: "${message}"`);

    const { intent, validation } = await parseAndValidate(message);

    console.log(`✨ Action: ${intent.action}`);
    console.log(`🎯 Target: ${intent.target}`);
    console.log(`📊 Confidence: ${intent.confidence.toFixed(2)}`);
    console.log(`💭 Reasoning: ${intent.reasoning}`);

    if (Object.keys(intent.params).length > 0) {
      console.log(`📦 Params:`, intent.params);
    }

    if (intent.clarifyingQuestions?.length) {
      console.log(`❓ Clarifying questions:`);
      intent.clarifyingQuestions.forEach((q, i) => {
        console.log(`   ${i + 1}. ${q}`);
      });
    }

    if (!validation.isValid) {
      console.log(`❌ Validation errors:`, validation.errors);
    }

    if (validation.warnings.length > 0) {
      console.log(`⚠️  Warnings:`, validation.warnings);
    }

    const suggestion = parser.generateExecutionSuggestion(intent);
    console.log(`💡 Suggestion: ${suggestion}`);

    console.log("\n---\n");
  }
}
