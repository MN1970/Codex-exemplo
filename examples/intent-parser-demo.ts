#!/usr/bin/env ts-node

/**
 * Demo: Intent Parser em Ação
 * Mostra todos os recursos: parse, validação, routing, execução
 */

import {
  IntentParser,
  parseAndValidate,
  runIntentParserExamples,
} from "../src/services/intent-parser";
import { MaestroRouter } from "../src/services/maestro-router";

/**
 * Cenário 1: Parse Simples
 */
async function demo1_SimpleParse() {
  console.log("\n╔══════════════════════════════════════════════════════════╗");
  console.log("║ DEMO 1: Parse Simples                                   ║");
  console.log("╚══════════════════════════════════════════════════════════╝\n");

  const parser = new IntentParser();

  const messages = [
    "cria um novo agente para saneamento",
    "atualizar configuração do maestro",
    "executa o workflow de candidaturas",
  ];

  for (const msg of messages) {
    console.log(`📝 Input: "${msg}"`);

    const intent = await parser.parse(msg);

    console.log(`   ✓ Action: ${intent.action}`);
    console.log(`   ✓ Target: ${intent.target}`);
    console.log(`   ✓ Confidence: ${(intent.confidence * 100).toFixed(0)}%`);

    if (Object.keys(intent.params).length > 0) {
      console.log(`   ✓ Params: ${JSON.stringify(intent.params)}`);
    }

    console.log();
  }
}

/**
 * Cenário 2: Parse com Validação
 */
async function demo2_ParseAndValidate() {
  console.log("\n╔══════════════════════════════════════════════════════════╗");
  console.log("║ DEMO 2: Parse + Validação                               ║");
  console.log("╚══════════════════════════════════════════════════════════╝\n");

  const testCases = [
    {
      msg: "criar agente para saneamento",
      desc: "Válido: action + target claro",
    },
    {
      msg: "agende",
      desc: "Ambíguo: falta contexto",
    },
    {
      msg: "atualizar",
      desc: "Incompleto: ação sem target",
    },
  ];

  for (const { msg, desc } of testCases) {
    console.log(`📝 ${desc}`);
    console.log(`   Input: "${msg}"\n`);

    const { intent, validation } = await parseAndValidate(msg);

    console.log(`   Action: ${intent.action}`);
    console.log(`   Target: ${intent.target}`);
    console.log(`   Confidence: ${(intent.confidence * 100).toFixed(0)}%`);

    if (validation.isValid) {
      console.log(`   ✅ VÁLIDO`);
    } else {
      console.log(`   ❌ INVÁLIDO`);
      validation.errors.forEach((e) => console.log(`      • ${e}`));
    }

    if (validation.warnings.length > 0) {
      console.log(`   ⚠️  AVISOS`);
      validation.warnings.forEach((w) => console.log(`      • ${w}`));
    }

    if (intent.clarifyingQuestions?.length) {
      console.log(`   ❓ PERGUNTAS`);
      intent.clarifyingQuestions.forEach((q) => {
        console.log(`      • ${q}`);
      });
    }

    console.log();
  }
}

/**
 * Cenário 3: Extração de Parâmetros
 */
async function demo3_ParameterExtraction() {
  console.log("\n╔══════════════════════════════════════════════════════════╗");
  console.log("║ DEMO 3: Extração de Parâmetros                          ║");
  console.log("╚══════════════════════════════════════════════════════════╝\n");

  const parser = new IntentParser();

  const messages = [
    "criar usuário com email john@example.com",
    "atualizar documento em https://docs.example.com/file",
    "agendar para 2025-12-31 com lembrete",
    "executar s8 workflow com notificação para test@manta.com",
  ];

  for (const msg of messages) {
    console.log(`📝 Input: "${msg}"`);

    const intent = await parser.parse(msg);

    console.log(`   Action: ${intent.action}`);
    console.log(`   Target: ${intent.target}`);

    if (Object.keys(intent.params).length > 0) {
      console.log(`   📦 Parâmetros extraídos:`);
      Object.entries(intent.params).forEach(([key, value]) => {
        console.log(`      • ${key}: ${value}`);
      });
    }

    console.log();
  }
}

/**
 * Cenário 4: Integração com Maestro Router
 */
async function demo4_MaestroIntegration() {
  console.log("\n╔══════════════════════════════════════════════════════════╗");
  console.log("║ DEMO 4: Integração com Maestro Router                   ║");
  console.log("╚══════════════════════════════════════════════════════════╝\n");

  const parser = new IntentParser();
  const router = new MaestroRouter();

  const messages = [
    "cria agente para saneamento",
    "executa energia workflow",
    "rodar s2 ponte analysis",
  ];

  for (const msg of messages) {
    console.log(`📝 Input: "${msg}"`);

    const intent = await parser.parse(msg);
    console.log(`   Intent → action: ${intent.action}, target: ${intent.target}`);

    if (intent.target === "agent" || msg.includes("s")) {
      try {
        const routing = router.route(msg);
        console.log(`   🎯 Routing → agent: ${routing.agent.name}`);
        console.log(`      Segment: ${routing.agent.segment}`);
        console.log(`      Score: ${routing.score.toFixed(2)}`);
      } catch (error) {
        console.log(`   ⚠️  Routing failed`);
      }
    }

    console.log();
  }
}

/**
 * Cenário 5: Sugestões de Execução
 */
async function demo5_ExecutionSuggestions() {
  console.log("\n╔══════════════════════════════════════════════════════════╗");
  console.log("║ DEMO 5: Sugestões de Execução                           ║");
  console.log("╚══════════════════════════════════════════════════════════╝\n");

  const parser = new IntentParser();

  const testCases = [
    "cria um novo agente",
    "atualizar configuração",
    "executa workflow candidaturas",
    "deployar em produção",
  ];

  for (const msg of testCases) {
    console.log(`📝 Input: "${msg}"`);

    const intent = await parser.parse(msg);
    const suggestion = parser.generateExecutionSuggestion(intent);

    console.log(`   💡 Sugestão: ${suggestion}`);
    console.log();
  }
}

/**
 * Cenário 6: Confidence Scores em Detalhes
 */
async function demo6_ConfidenceScoring() {
  console.log("\n╔══════════════════════════════════════════════════════════╗");
  console.log("║ DEMO 6: Análise de Confidence Scores                    ║");
  console.log("╚══════════════════════════════════════════════════════════╝\n");

  const parser = new IntentParser();

  const messages = [
    {
      msg: "criar um novo agente para saneamento com os parâmetros x=1 y=2",
      expected: "Muito alto (action + target + params claros)",
    },
    {
      msg: "criar agente",
      expected: "Alto (action + target, mas genérico)",
    },
    {
      msg: "atualizar",
      expected: "Médio (ação clara, target incerto)",
    },
    {
      msg: "agende",
      expected: "Baixo (muito ambíguo)",
    },
  ];

  for (const { msg, expected } of messages) {
    console.log(`📝 Input: "${msg}"`);
    console.log(`   Esperado: ${expected}`);

    const intent = await parser.parse(msg);

    const confLevel =
      intent.confidence >= 0.8
        ? "🟢 Muito Alto"
        : intent.confidence >= 0.6
          ? "🟡 Médio"
          : intent.confidence >= 0.4
            ? "🟠 Baixo"
            : "🔴 Muito Baixo";

    console.log(`   Resultado: ${confLevel} (${(intent.confidence * 100).toFixed(0)}%)`);
    console.log(`   Reasoning: ${intent.reasoning}`);
    console.log();
  }
}

/**
 * Main: Rodar todos os demos
 */
async function main() {
  console.log("\n");
  console.log(
    "╔═══════════════════════════════════════════════════════════════╗"
  );
  console.log("║         Intent Parser — Demonstração Completa            ║");
  console.log("║     6 Cenários de Uso + Integração com Maestro           ║");
  console.log(
    "╚═══════════════════════════════════════════════════════════════╝"
  );

  try {
    await demo1_SimpleParse();
    await demo2_ParseAndValidate();
    await demo3_ParameterExtraction();
    await demo4_MaestroIntegration();
    await demo5_ExecutionSuggestions();
    await demo6_ConfidenceScoring();

    console.log("\n");
    console.log(
      "╔═══════════════════════════════════════════════════════════════╗"
    );
    console.log("║              ✅ DEMONSTRAÇÃO CONCLUÍDA                    ║");
    console.log(
      "╚═══════════════════════════════════════════════════════════════╝\n"
    );

    console.log("Próximos passos:");
    console.log("  1. Integrar parseIntent() em sua aplicação");
    console.log("  2. Ajustar confidence thresholds para seu domínio");
    console.log("  3. Monitorar distribuição de scores");
    console.log("  4. Customizar prompts para casos específicos\n");
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

// Executar
main();
