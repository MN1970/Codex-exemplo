/**
 * Teste Local do Maestro — Sem dependência de Claude AI
 */

import { getMaestroRouter } from "../src/services/maestro-router";
import {
  create_task,
  list_tasks,
  post_comment,
} from "../src/adapters/cowork-adapter";

async function testMaestroLocal() {
  console.log("\n🎯 TESTE LOCAL — MAESTRO + COWORK\n");
  console.log("=".repeat(70));

  const router = getMaestroRouter();

  const testPrompts = [
    {
      name: "Saneamento",
      prompt:
        "Projeto de ETA com análise de qualidade de água e adução completa",
      expected: "agente-saneamento",
    },
    {
      name: "Energia",
      prompt: "Linha de transmissão 500kV com subestação e RAP",
      expected: "agente-energia",
    },
    {
      name: "Portos",
      prompt: "Terminal portuário com berços de atracação e dragagem",
      expected: "agente-portos",
    },
    {
      name: "Aeroportos",
      prompt: "Pista de pouso com TPS (Terminal de Passageiros) e ANAC",
      expected: "agente-aeroportos",
    },
    {
      name: "Barragens",
      prompt: "Barragem de rejeitos com altura de 100m e PNSB",
      expected: "agente-barragens",
    },
  ];

  let passed = 0;
  const total = testPrompts.length;

  for (const test of testPrompts) {
    console.log(`\n📋 TESTE: ${test.name}`);
    console.log(`   Prompt: "${test.prompt}"`);
    console.log("-".repeat(70));

    try {
      // STEP 1: Maestro Router
      const routing = await router.route(test.prompt);

      console.log(`\n   ✅ STEP 1 - Maestro Routing`);
      console.log(`      Agent: ${routing.agent.name} (${routing.agent.code})`);
      console.log(`      Score: ${routing.score.toFixed(2)}`);
      console.log(`      Confidence: ${routing.confidence}`);
      console.log(`      Keywords: ${routing.matchedKeywords.join(", ")}`);

      if (routing.agent.name !== test.expected) {
        console.log(
          `      ❌ ERRO: Esperado ${test.expected}, recebeu ${routing.agent.name}`
        );
        continue;
      }

      // STEP 2: Criar Task no Cowork
      console.log(`\n   ✅ STEP 2 - Criar Task no Cowork`);
      const taskResponse = await create_task({
        title: `[${routing.agent.code}] ${test.name} - ${test.prompt.substring(0, 50)}...`,
        description: `
Agent: ${routing.agent.name}
Segment: ${routing.agent.segment}
Score: ${routing.score.toFixed(2)}
Confidence: ${routing.confidence}
Keywords: ${routing.matchedKeywords.join(", ")}

Prompt Original:
${test.prompt}
        `,
        priority:
          (routing.confidence === "high" ? "high" : "medium") as
            | "high"
            | "medium"
            | "low",
        agent_source: routing.agent.name,
        segment: routing.agent.segment || "Geral",
        tags: [routing.agent.name, "maestro-test", "local"],
      });

      if (taskResponse.success && taskResponse.data) {
        console.log(`      Task ID: ${taskResponse.data.id}`);
        console.log(`      Title: ${taskResponse.data.title}`);
        console.log(`      Status: ${taskResponse.data.status}`);

        // STEP 3: Postar Comentário
        console.log(`\n   ✅ STEP 3 - Postar Comentário no Cowork`);
        const commentResponse = await post_comment({
          taskId: taskResponse.data.id,
          content: `✅ **Maestro Routing Completo**

**Agent:** ${routing.agent.name} (${routing.agent.code})
**Confidence:** ${routing.confidence}
**Score:** ${routing.score.toFixed(2)}
**Keywords:** ${routing.matchedKeywords.join(", ")}

Processado por: Maestro Router v1.0
Timestamp: ${new Date().toISOString()}`,
        });

        if (commentResponse.success) {
          console.log(`      Comment ID: ${commentResponse.data?.id}`);
          console.log(`\n   ✅ TESTE PASSOU`);
          passed++;
        }
      }
    } catch (error) {
      console.log(
        `      ❌ ERRO: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  // SUMMARY
  console.log("\n" + "=".repeat(70));
  console.log("\n📊 RESUMO DOS TESTES\n");
  console.log(`   ✅ Passou: ${passed}/${total}`);
  console.log(`   ❌ Falhou: ${total - passed}/${total}`);
  console.log(
    `   Taxa de Sucesso: ${((passed / total) * 100).toFixed(1)}%\n`
  );

  // List all tasks
  console.log("📋 TASKS CRIADAS NO COWORK:\n");
  const tasksList = await list_tasks({ limit: 10 });

  if (tasksList.success) {
    const tasks = (tasksList.data as any)?.tasks || [];
    tasks.forEach((task: any, i: number) => {
      console.log(`   ${i + 1}. ${task.title}`);
      console.log(`      ID: ${task.id}`);
      console.log(`      Status: ${task.status}\n`);
    });
  }

  console.log("=".repeat(70));
  console.log("\n✨ MAESTRO LOCAL TEST COMPLETE\n");

  if (passed === total) {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

testMaestroLocal().catch(console.error);
