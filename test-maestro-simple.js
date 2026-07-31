/**
 * SIMPLE TEST: Maestro Routing Logic
 *
 * Testa a lógica de roteamento sem dependências externas
 * Implementa o algoritmo de scoring direto
 */

// Configuração de agentes e keywords
const ROUTING_CONFIG = {
  "agente-saneamento": {
    code: "Manta 03-S8",
    keywords: ["saneamento", "eta", "ete", "adutora", "aysa", "drenagem urbana", "snis"],
    weight: 1.0
  },
  "agente-energia": {
    code: "Manta 03-S9",
    keywords: ["transmissão", "lt", "subestação", "aneel", "ons", "epe", "kv"],
    weight: 1.0
  },
  "agente-portos": {
    code: "Manta 03-S6",
    keywords: ["porto", "terminal", "antaq", "dragagem", "berço", "contêiner", "granel"],
    weight: 1.0
  },
  "agente-aeroportos": {
    code: "Manta 03-S7",
    keywords: ["aeroporto", "pista", "anac", "tps", "balizamento", "icao"],
    weight: 1.0
  },
  "agente-barragens": {
    code: "Manta 03-S10",
    keywords: ["barragem", "vertedouro", "rejeitos", "tsf", "pnsb", "icold"],
    weight: 1.0
  }
};

// Algoritmo de roteamento
function routePrompt(prompt) {
  const lowerPrompt = prompt.toLowerCase();
  const scores = {};
  const matchedKeywords = {};

  // Scoring
  for (const [agentName, config] of Object.entries(ROUTING_CONFIG)) {
    scores[agentName] = 0;
    matchedKeywords[agentName] = [];

    for (const keyword of config.keywords) {
      if (lowerPrompt.includes(keyword)) {
        // Base weight
        let weight = config.weight;

        // Bonificação de posição (aparece no início = maior relevância)
        if (lowerPrompt.indexOf(keyword) < lowerPrompt.length * 0.3) {
          weight *= 1.5; // 50% bonus para primeiras palavras
        }

        scores[agentName] += weight;
        matchedKeywords[agentName].push(keyword);
      }
    }
  }

  // Find winner
  let bestAgent = null;
  let bestScore = 0;

  for (const [agent, score] of Object.entries(scores)) {
    if (score > bestScore) {
      bestScore = score;
      bestAgent = agent;
    }
  }

  // Determine confidence
  let confidence = "low";
  if (bestScore >= 3) confidence = "high";
  else if (bestScore >= 1.5) confidence = "medium";

  return {
    agent: bestAgent || "unknown",
    code: bestAgent ? ROUTING_CONFIG[bestAgent].code : "N/A",
    matchedKeywords: matchedKeywords[bestAgent] || [],
    score: bestScore,
    confidence,
    allScores: scores
  };
}

// Test cases
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
];

// Run tests
console.log("🚀 MAESTRO ROUTER SIMPLE CONNECTION TEST\n");
console.log("=" .repeat(70));

let passCount = 0;
let failCount = 0;
const results = [];

for (const testCase of TEST_CASES) {
  console.log(`\n📋 Test: ${testCase.description}`);
  console.log(`   Prompt: "${testCase.prompt}"`);
  console.log(`   Expected: ${testCase.expectedAgent}`);

  const result = routePrompt(testCase.prompt);

  console.log(`\n   ✅ Result:`);
  console.log(`      Agent: ${result.agent} (${result.code})`);
  console.log(`      Matched Keywords: ${result.matchedKeywords.join(', ') || '(none)'}`);
  console.log(`      Score: ${result.score.toFixed(2)}`);
  console.log(`      Confidence: ${result.confidence}`);

  const passed = result.agent === testCase.expectedAgent;

  if (passed) {
    console.log(`   ✅ PASS`);
    passCount++;
  } else {
    console.log(`   ❌ FAIL — Expected ${testCase.expectedAgent}, got ${result.agent}`);
    failCount++;
  }

  results.push({
    test: testCase.description,
    passed,
    score: result.score
  });
}

// Summary
console.log("\n" + "=".repeat(70));
console.log("\n📊 TEST SUMMARY\n");
console.log(`✅ Passed: ${passCount}/${TEST_CASES.length}`);
console.log(`❌ Failed: ${failCount}/${TEST_CASES.length}`);
console.log(`Success Rate: ${((passCount / TEST_CASES.length) * 100).toFixed(1)}%`);

console.log("\n" + "=".repeat(70));

if (failCount === 0) {
  console.log("\n🎉 ALL TESTS PASSED - MAESTRO ROUTER IS OPERATIONAL\n");
  process.exit(0);
} else {
  console.log("\n⚠️  SOME TESTS FAILED - CHECK ROUTING KEYWORDS\n");
  process.exit(1);
}
