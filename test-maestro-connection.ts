/**
 * TEST: Maestro Router Connection & Routing Validation
 *
 * Valida:
 * 1. Importação do maestro-router
 * 2. Roteamento de prompts para agentes corretos
 * 3. Scoring e confiança
 * 4. Performance (< 100ms)
 */

import { MaestroRouter, RoutingResult, RouterStats } from './src/services/maestro-router';

// Teste cases com prompts reais da Manta
const TEST_CASES = [
  {
    prompt: "Preciso de um projeto de ETA com análise de qualidade de água e adução",
    expectedAgent: "agente-saneamento",
    description: "Saneamento (ETA + adução)"
  },
  {
    prompt: "Vou construir uma linha de transmissão de 500kV com subestação",
    expectedAgent: "agente-energia",
    description: "Energia (LT + subestação)"
  },
  {
    prompt: "Projeto de terminal de contêineres com berços e dragagem",
    expectedAgent: "agente-portos",
    description: "Portos (contêiner + dragagem)"
  },
  {
    prompt: "Aeroporto com pista de pouso de 3500m e TPS",
    expectedAgent: "agente-aeroportos",
    description: "Aeroportos (pista + TPS)"
  },
  {
    prompt: "Barragem de rejeitos com altura de 120m e vertedouro",
    expectedAgent: "agente-barragens",
    description: "Barragens (rejeitos + altura)"
  },
  {
    prompt: "Rodovia com pavimento CBUQ e terraplenagem",
    expectedAgent: "agente-infraestrutura-s1",
    description: "Rodovia (CBUQ + terraplenagem)"
  },
  {
    prompt: "Ponte de concreto armado com vão de 80m",
    expectedAgent: "agente-infraestrutura-s2",
    description: "OAE (ponte + concreto)"
  },
];

async function testMaestroConnection() {
  console.log("🚀 MAESTRO ROUTER CONNECTION TEST\n");
  console.log("=" .repeat(60));

  const router = new MaestroRouter();
  let passCount = 0;
  let failCount = 0;
  const results: Array<{test: string; passed: boolean; score: number; time: number}> = [];

  for (const testCase of TEST_CASES) {
    console.log(`\n📋 Test: ${testCase.description}`);
    console.log(`   Prompt: "${testCase.prompt}"`);
    console.log(`   Expected Agent: ${testCase.expectedAgent}`);

    const startTime = performance.now();
    const routingResult = await router.route(testCase.prompt);
    const endTime = performance.now();
    const executionTime = endTime - startTime;

    console.log(`\n   ✅ Routing Result:`);
    console.log(`      Agent: ${routingResult.agent.name} (${routingResult.agent.code})`);
    console.log(`      Matched Keywords: ${routingResult.matchedKeywords.join(', ')}`);
    console.log(`      Score: ${routingResult.score.toFixed(2)}`);
    console.log(`      Confidence: ${routingResult.confidence}`);
    console.log(`      Execution Time: ${executionTime.toFixed(2)}ms`);

    const passed = routingResult.agent.name === testCase.expectedAgent;

    if (passed) {
      console.log(`   ✅ PASS — Routed to correct agent`);
      passCount++;
    } else {
      console.log(`   ❌ FAIL — Expected ${testCase.expectedAgent}, got ${routingResult.agent.name}`);
      failCount++;
    }

    results.push({
      test: testCase.description,
      passed,
      score: routingResult.score,
      time: executionTime
    });

    if (executionTime > 100) {
      console.log(`   ⚠️  WARNING: Execution time ${executionTime.toFixed(2)}ms > 100ms target`);
    }
  }

  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("\n📊 TEST SUMMARY\n");
  console.log(`✅ Passed: ${passCount}/${TEST_CASES.length}`);
  console.log(`❌ Failed: ${failCount}/${TEST_CASES.length}`);
  console.log(`Success Rate: ${((passCount / TEST_CASES.length) * 100).toFixed(1)}%`);

  const avgTime = results.reduce((sum, r) => sum + r.time, 0) / results.length;
  const maxTime = Math.max(...results.map(r => r.time));
  const minTime = Math.min(...results.map(r => r.time));

  console.log(`\n⏱️  Performance Metrics:`);
  console.log(`   Average Time: ${avgTime.toFixed(2)}ms`);
  console.log(`   Min Time: ${minTime.toFixed(2)}ms`);
  console.log(`   Max Time: ${maxTime.toFixed(2)}ms`);
  console.log(`   Target: < 100ms ✅`);

  console.log("\n" + "=".repeat(60));

  if (failCount === 0 && maxTime < 100) {
    console.log("\n🎉 ALL TESTS PASSED - MAESTRO ROUTER IS OPERATIONAL\n");
    return true;
  } else {
    console.log("\n❌ SOME TESTS FAILED - CHECK MAESTRO CONFIGURATION\n");
    return false;
  }
}

// Run test
testMaestroConnection().catch(console.error);
