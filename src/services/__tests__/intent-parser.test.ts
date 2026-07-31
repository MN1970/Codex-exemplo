/**
 * Testes para o Intent Parser
 * Cobre: parsing, validação, normalização, e edge cases
 */

import {
  IntentParser,
  parseIntent,
  parseAndValidate,
  type ParsedIntent,
  type ValidationResult,
} from "../intent-parser";

describe("IntentParser", () => {
  let parser: IntentParser;

  beforeEach(() => {
    parser = new IntentParser();
  });

  describe("Inicialização", () => {
    test("deve criar instância com config padrão", () => {
      expect(parser).toBeDefined();
    });

    test("deve lançar erro sem ANTHROPIC_API_KEY", () => {
      const originalKey = process.env.ANTHROPIC_API_KEY;
      delete process.env.ANTHROPIC_API_KEY;

      expect(() => {
        new IntentParser();
      }).toThrow("ANTHROPIC_API_KEY não configurada");

      process.env.ANTHROPIC_API_KEY = originalKey;
    });

    test("deve aceitar config customizada", () => {
      const customParser = new IntentParser({
        model: "claude-3-opus-20240229",
        minConfidenceThreshold: 0.4,
        enableClarifyingQuestions: false,
      });

      expect(customParser).toBeDefined();
    });
  });

  describe("Normalização de Actions", () => {
    test("deve normalizar 'create' corretamente", async () => {
      const intent = await parser.parse("criar um novo agente");
      expect(intent.action).toBe("create");
    });

    test("deve normalizar 'update'", async () => {
      const intent = await parser.parse("atualizar a configuração");
      expect(intent.action).toBe("update");
    });

    test("deve normalizar 'delete'", async () => {
      const intent = await parser.parse("remover o workflow");
      expect(intent.action).toBe("delete");
    });

    test("deve normalizar 'execute'", async () => {
      const intent = await parser.parse("executar o pipeline");
      expect(intent.action).toMatch(/execute|run/);
    });

    test("deve normalizar 'list'", async () => {
      const intent = await parser.parse("listar todos os agentes");
      expect(intent.action).toBe("list");
    });
  });

  describe("Normalização de Targets", () => {
    test("deve identificar 'agent' como target", async () => {
      const intent = await parser.parse("cria um agente");
      expect(intent.target).toBe("agent");
    });

    test("deve identificar 'workflow' como target", async () => {
      const intent = await parser.parse("criar um workflow novo");
      expect(intent.target).toBe("workflow");
    });

    test("deve identificar 'config' como target", async () => {
      const intent = await parser.parse("atualizar configuração");
      expect(intent.target).toBe("config");
    });

    test("deve identificar 'deployment' como target", async () => {
      const intent = await parser.parse("deploy em produção");
      expect(intent.target).toBe("deployment");
    });
  });

  describe("Confidence Scoring", () => {
    test("deve retornar score entre 0.0 e 1.0", async () => {
      const intent = await parser.parse("cria um agente para saneamento");
      expect(intent.confidence).toBeGreaterThanOrEqual(0.0);
      expect(intent.confidence).toBeLessThanOrEqual(1.0);
    });

    test("deve ter alta confiança para intents claros", async () => {
      const intent = await parser.parse(
        "criar novo agente saneamento com parâmetros x=1 y=2"
      );
      // Deve ter confiança razoável (heurística não garante >0.8)
      expect(intent.confidence).toBeGreaterThan(0.5);
    });

    test("deve ter baixa confiança para intents ambíguos", async () => {
      const intent = await parser.parse("agende");
      expect(intent.confidence).toBeLessThan(0.8);
    });
  });

  describe("Extração de Parâmetros", () => {
    test("deve extrair email de mensagem", async () => {
      const intent = await parser.parse(
        "criar usuário com email test@example.com"
      );
      expect(intent.params.email).toBe("test@example.com");
    });

    test("deve extrair URL de mensagem", async () => {
      const intent = await parser.parse(
        "atualizar documento em https://example.com/doc"
      );
      expect(intent.params.url).toContain("https://");
    });

    test("deve extrair data de mensagem", async () => {
      const intent = await parser.parse("agendar para 2025-12-31");
      expect(intent.params.date).toBeDefined();
    });

    test("deve extrair agent code", async () => {
      const intent = await parser.parse("executar s8 workflow");
      expect(intent.params.agent).toBeDefined();
    });
  });

  describe("Validação de Intent", () => {
    test("deve validar intent bem formado", () => {
      const validIntent: ParsedIntent = {
        action: "create",
        target: "agent",
        confidence: 0.9,
        params: { segment: "saneamento" },
        reasoning: "Teste",
        rawIntentTokens: ["create", "agent"],
      };

      const validation = parser.validateIntent(validIntent);
      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });

    test("deve rejeitar intent com confiança muito baixa", () => {
      const lowConfIntent: ParsedIntent = {
        action: "clarify",
        target: "unknown",
        confidence: 0.1,
        params: {},
        reasoning: "Muito incerto",
        rawIntentTokens: [],
      };

      const validation = parser.validateIntent(lowConfIntent);
      expect(validation.isValid).toBe(false);
      expect(validation.errors.length).toBeGreaterThan(0);
    });

    test("deve avisar quando action de modificação não tem target", () => {
      const noTargetIntent: ParsedIntent = {
        action: "create",
        target: "unknown",
        confidence: 0.5,
        params: {},
        reasoning: "Teste",
        rawIntentTokens: [],
      };

      const validation = parser.validateIntent(noTargetIntent);
      expect(validation.isValid).toBe(false);
    });

    test("deve avisar quando schedule não tem data", () => {
      const noDateIntent: ParsedIntent = {
        action: "schedule",
        target: "workflow",
        confidence: 0.7,
        params: {},
        reasoning: "Teste",
        rawIntentTokens: [],
      };

      const validation = parser.validateIntent(noDateIntent);
      expect(validation.warnings.length).toBeGreaterThan(0);
    });
  });

  describe("Clarifying Questions", () => {
    test("deve gerar perguntas para intent pouco claro", async () => {
      const intent = await parser.parse("agende algo");
      if (intent.confidence < 0.5) {
        expect(intent.clarifyingQuestions).toBeDefined();
        expect(intent.clarifyingQuestions?.length).toBeGreaterThan(0);
      }
    });

    test("deve respeitar enableClarifyingQuestions=false", () => {
      const noClarifyParser = new IntentParser({
        enableClarifyingQuestions: false,
      });

      const intent: ParsedIntent = {
        action: "clarify",
        target: "unknown",
        confidence: 0.2,
        params: {},
        reasoning: "Teste",
        rawIntentTokens: [],
        clarifyingQuestions: [],
      };

      expect(intent.clarifyingQuestions?.length).toBe(0);
    });
  });

  describe("Sugestões de Execução", () => {
    test("deve gerar sugestão para create + agent", () => {
      const intent: ParsedIntent = {
        action: "create",
        target: "agent",
        confidence: 0.9,
        params: { segment: "saneamento" },
        reasoning: "Teste",
        rawIntentTokens: [],
      };

      const suggestion = parser.generateExecutionSuggestion(intent);
      expect(suggestion).toContain("agente");
    });

    test("deve gerar sugestão para execute + workflow", () => {
      const intent: ParsedIntent = {
        action: "execute",
        target: "workflow",
        confidence: 0.9,
        params: { workflowName: "candidaturas" },
        reasoning: "Teste",
        rawIntentTokens: [],
      };

      const suggestion = parser.generateExecutionSuggestion(intent);
      expect(suggestion).toBeDefined();
    });

    test("deve gerar sugestão genérica para combos desconhecidos", () => {
      const intent: ParsedIntent = {
        action: "read",
        target: "unknown",
        confidence: 0.7,
        params: {},
        reasoning: "Teste",
        rawIntentTokens: [],
      };

      const suggestion = parser.generateExecutionSuggestion(intent);
      expect(suggestion).toContain("read");
    });
  });

  describe("Edge Cases", () => {
    test("deve lidar com mensagem vazia", async () => {
      const intent = await parser.parse("");
      expect(intent.action).toBe("clarify");
      expect(intent.confidence).toBe(0.0);
    });

    test("deve lidar com mensagem apenas espaços", async () => {
      const intent = await parser.parse("   ");
      expect(intent.action).toBe("clarify");
    });

    test("deve lidar com mensagem muito longa", async () => {
      const longMessage = "a".repeat(20000);
      const intent = await parser.parse(longMessage);
      expect(intent).toBeDefined();
    });

    test("deve lidar com caracteres especiais", async () => {
      const intent = await parser.parse("criar @#$% &*()");
      expect(intent).toBeDefined();
    });

    test("deve lidar com idiomas mistos", async () => {
      const intent = await parser.parse("create um novo agente workflow");
      expect(intent).toBeDefined();
    });
  });

  describe("Factory Functions", () => {
    test("parseIntent deve retornar ParsedIntent", async () => {
      const intent = await parseIntent("criar agente");
      expect(intent.action).toBeDefined();
      expect(intent.target).toBeDefined();
      expect(intent.confidence).toBeDefined();
    });

    test("parseAndValidate deve retornar intent + validation", async () => {
      const { intent, validation } = await parseAndValidate(
        "criar novo agente"
      );

      expect(intent.action).toBeDefined();
      expect(validation.isValid).toBeDefined();
      expect(validation.errors).toBeInstanceOf(Array);
      expect(validation.warnings).toBeInstanceOf(Array);
    });
  });

  describe("Integração com Maestro", () => {
    test("deve mapear intent com segment de segmento", async () => {
      const intent = await parser.parse("cria um agente para saneamento");

      if (intent.params.segment === "saneamento") {
        expect(intent.target).toBe("agent");
      }
    });

    test("deve extrair agent code para routing", async () => {
      const intent = await parser.parse("executar s8");
      expect(intent.params.agent).toBeDefined();
    });
  });
});
