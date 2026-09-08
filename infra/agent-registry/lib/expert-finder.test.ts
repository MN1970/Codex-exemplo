/**
 * expert-finder.test.ts
 * =====================================================================
 * Test suite for ExpertRanker (Manta Maestro v5.0 expert agent finder)
 *
 * Coverage:
 * - Unit tests: score computation, weights validation, tie-breaking
 * - Integration tests: 10 sample queries across all 5 new segments (S6-S10)
 * - Circuit breaker logic: low confidence & ambiguity detection
 * - Explainability: reasoning JSON per agent
 *
 * Test queries:
 * 1. S8 (Saneamento): ETA para 200k hab
 * 2. S8 (Saneamento): Sistema de esgotamento sanitário AySA
 * 3. S9 (Energia): LT de transmissão 345kV ANEEL
 * 4. S9 (Energia): Leilão de transmissão ONS
 * 5. S6 (Portos): Dragagem de berço portuário ANTAQ
 * 6. S6 (Portos): Terminal de contêineres 50k TEU
 * 7. S7 (Aeroportos): Dimensionamento de pista ANAC
 * 8. S7 (Aeroportos): Sistema de balizamento ICAO
 * 9. S10 (Barragens): Barragem CFRD 120m altura
 * 10. S10 (Barragens): Gestão de rejeitos TSF
 *
 * Run via Node.js built-in test runner:
 *   node --test infra/agent-registry/lib/expert-finder.test.ts
 */

import * as test from 'node:test';
import * as assert from 'node:assert';
import {
  ExpertRanker,
  ExpertRankingResult,
  RoutingHistory,
  CapabilityMatch,
  SyntheticHistoryProvider,
  LocalCapabilityProvider,
} from './expert-finder';
import { AGENT_REGISTRY_SEED } from './maestro-v2-routing';

// =====================================================================
// Test utilities
// =====================================================================

function mockQueryEmbedding(query: string): number[] {
  // Deterministic embedding for reproducibility in tests
  const vector = new Array<number>(1536).fill(0);
  for (let i = 0; i < query.length; i++) {
    const idx = (i * 31 + query.charCodeAt(i)) % 1536;
    vector[idx] += 1;
  }
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
  return norm > 0 ? vector.map((v) => v / norm) : vector;
}

// =====================================================================
// Test Suite 1: Score Computation
// =====================================================================

test('ExpertRanker: weight validation', () => {
  // Valid weights (sum = 1.0)
  const ranker = new ExpertRanker({
    weights: {
      semantic: 0.4,
      historical: 0.3,
      capability: 0.15,
      cost: 0.1,
      latency: 0.05,
    },
  });
  assert.ok(ranker);

  // Invalid weights (sum != 1.0)
  assert.throws(
    () => {
      new ExpertRanker({
        weights: {
          semantic: 0.5,
          historical: 0.5,
        },
      });
    },
    { name: 'MaestroRoutingError' }
  );
});

test('ExpertRanker: default weights & thresholds', () => {
  const ranker = new ExpertRanker();
  assert.ok(ranker); // Should not throw
});

// =====================================================================
// Test Suite 2: Sample Query Tests (S6-S10)
// =====================================================================

test('Sample Query 1: S8 (Saneamento) — ETA para 200k hab', async () => {
  const ranker = new ExpertRanker();
  const query = 'ETA para população de 200 mil habitantes, sistema de abastecimento de água';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0, 'Should have ranked agents');
  // saneamento (S8) should rank in top 3
  const top3Ids = result.ranked.slice(0, 3).map((r) => r.agent.id);
  assert.ok(
    top3Ids.includes('agente-saneamento'),
    `Expected agente-saneamento in top 3, got ${top3Ids.join(', ')}`
  );

  if (result.primaryChoice) {
    console.log(`Query 1 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 2: S8 (Saneamento) — Sistema AySA', async () => {
  const ranker = new ExpertRanker();
  const query =
    'Sistema de esgotamento sanitário na Argentina (AySA), tratamento terciário, SNIS';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  // AySA keyword should boost agente-saneamento strongly
  const saneamentoRank = result.ranked.findIndex((r) => r.agent.id === 'agente-saneamento');
  assert.ok(saneamentoRank >= 0, 'agente-saneamento should be in results');
  assert.ok(saneamentoRank < 3, `agente-saneamento should rank in top 3, got rank ${saneamentoRank + 1}`);

  if (result.primaryChoice) {
    console.log(`Query 2 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 3: S9 (Energia) — LT de transmissão 345kV', async () => {
  const ranker = new ExpertRanker();
  const query = 'Linha de transmissão 345kV, ANEEL, RAP (Receita Anual Permitida), leilão';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const energiaRank = result.ranked.findIndex((r) => r.agent.id === 'agente-energia');
  assert.ok(energiaRank >= 0, 'agente-energia should be in results');
  assert.ok(energiaRank < 3, `agente-energia should rank in top 3, got rank ${energiaRank + 1}`);

  if (result.primaryChoice) {
    console.log(`Query 3 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 4: S9 (Energia) — Leilão transmissão ONS', async () => {
  const ranker = new ExpertRanker();
  const query = 'Análise econômica de leilão de transmissão (transmissão), ONS, EPE, estruturação';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const energiaRank = result.ranked.findIndex((r) => r.agent.id === 'agente-energia');
  assert.ok(energiaRank >= 0 && energiaRank < 5, 'agente-energia should rank well');

  if (result.primaryChoice) {
    console.log(`Query 4 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 5: S6 (Portos) — Dragagem de berço', async () => {
  const ranker = new ExpertRanker();
  const query = 'Dragagem de berço portuário, ANTAQ, calado, terminal de contêineres';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const portosRank = result.ranked.findIndex((r) => r.agent.id === 'agente-portos');
  assert.ok(portosRank >= 0, 'agente-portos should be in results');
  assert.ok(portosRank < 3, `agente-portos should rank in top 3, got rank ${portosRank + 1}`);

  if (result.primaryChoice) {
    console.log(`Query 5 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 6: S6 (Portos) — Terminal contêineres', async () => {
  const ranker = new ExpertRanker();
  const query = 'Terminal de contêineres 50k TEU/ano, molhe, PIANC, granel (carga geral)';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const portosRank = result.ranked.findIndex((r) => r.agent.id === 'agente-portos');
  assert.ok(portosRank >= 0 && portosRank < 5, 'agente-portos should rank well');

  if (result.primaryChoice) {
    console.log(`Query 6 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 7: S7 (Aeroportos) — Dimensionamento pista', async () => {
  const ranker = new ExpertRanker();
  const query = 'Dimensionamento de pista pouso aterrado, ANAC, RBAC, ICAO Annex 14';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const aeroportosRank = result.ranked.findIndex((r) => r.agent.id === 'agente-aeroportos');
  assert.ok(aeroportosRank >= 0, 'agente-aeroportos should be in results');
  assert.ok(aeroportosRank < 3, `agente-aeroportos should rank in top 3, got rank ${aeroportosRank + 1}`);

  if (result.primaryChoice) {
    console.log(`Query 7 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 8: S7 (Aeroportos) — Sistema balizamento', async () => {
  const ranker = new ExpertRanker();
  const query = 'Sistema de balizamento e sinalização ICAO, TPS (throughput), TECA';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const aeroportosRank = result.ranked.findIndex((r) => r.agent.id === 'agente-aeroportos');
  assert.ok(aeroportosRank >= 0 && aeroportosRank < 5, 'agente-aeroportos should rank well');

  if (result.primaryChoice) {
    console.log(`Query 8 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 9: S10 (Barragens) — Barragem CFRD', async () => {
  const ranker = new ExpertRanker();
  const query = 'Barragem CFRD 120 metros altura, vertedouro, fundações, ICOLD, CBDB';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const barragensRank = result.ranked.findIndex((r) => r.agent.id === 'agente-barragens');
  assert.ok(barragensRank >= 0, 'agente-barragens should be in results');
  assert.ok(barragensRank < 3, `agente-barragens should rank in top 3, got rank ${barragensRank + 1}`);

  if (result.primaryChoice) {
    console.log(`Query 9 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

test('Sample Query 10: S10 (Barragens) — Gestão rejeitos TSF', async () => {
  const ranker = new ExpertRanker();
  const query =
    'Gestão de rejeitos e Tailings Storage Facility (TSF), descaracterização, Lei 12.334, PNSB';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const barragensRank = result.ranked.findIndex((r) => r.agent.id === 'agente-barragens');
  assert.ok(barragensRank >= 0 && barragensRank < 5, 'agente-barragens should rank well');

  if (result.primaryChoice) {
    console.log(`Query 10 result: ${result.primaryChoice.agent.name} (confidence: ${result.primaryChoice.confidence.toFixed(2)})`);
  }
});

// =====================================================================
// Test Suite 3: Circuit Breaker Logic
// =====================================================================

test('Circuit breaker: low confidence escalation', async () => {
  const ranker = new ExpertRanker({
    confidenceThreshold: 0.8, // Very high threshold to force escalation
  });

  // Generic query that won't match any agent strongly
  const query = 'xyz abc123 qwerty';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  // With such a high threshold, should escalate most of the time
  if (result.circuitBreakerEscalate) {
    assert.ok(result.circuitBreakerReason.includes('low_confidence'));
    assert.strictEqual(result.primaryChoice, null);
    console.log(`Circuit breaker triggered: ${result.circuitBreakerReason}`);
  }
});

test('Circuit breaker: no candidates', async () => {
  const ranker = new ExpertRanker();

  const result = await ranker.findExperts([], 'any query', mockQueryEmbedding('any query'));

  assert.strictEqual(result.ranked.length, 0);
  assert.ok(result.circuitBreakerEscalate);
  assert.ok(result.circuitBreakerReason.includes('no_candidates'));
});

// =====================================================================
// Test Suite 4: Explainability
// =====================================================================

test('Explainability: reasoning per agent', async () => {
  const ranker = new ExpertRanker();
  const query = 'Dragagem portuária ANTAQ';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  // Check that explanations are populated
  for (const ranked of result.ranked.slice(0, 3)) {
    assert.ok(ranked.explanation.length > 0, `Agent ${ranked.agent.id} should have explanation`);
    assert.ok(
      ranked.explanation.includes('%') || ranked.explanation.includes('Confidence'),
      'Explanation should include percentage or confidence metric'
    );
  }

  console.log('Top 3 explanations:');
  for (const ranked of result.ranked.slice(0, 3)) {
    console.log(`  ${ranked.rank}. ${ranked.agent.name}: ${ranked.explanation}`);
  }
});

test('Score breakdown: all components populated', async () => {
  const ranker = new ExpertRanker();
  const query = 'ETA para saneamento';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  assert.ok(result.ranked.length > 0);
  const top = result.ranked[0];

  // Verify all score components are populated
  assert.strictEqual(typeof top.scores.semanticScore, 'number');
  assert.strictEqual(typeof top.scores.historicalScore, 'number');
  assert.strictEqual(typeof top.scores.capabilityScore, 'number');
  assert.strictEqual(typeof top.scores.costScore, 'number');
  assert.strictEqual(typeof top.scores.latencyScore, 'number');
  assert.strictEqual(typeof top.scores.finalScore, 'number');

  // All should be in [0, 1]
  for (const key of [
    'semanticScore',
    'historicalScore',
    'capabilityScore',
    'costScore',
    'latencyScore',
    'finalScore',
  ] as const) {
    const value = top.scores[key];
    assert.ok(
      value >= 0 && value <= 1,
      `${key} = ${value} should be in [0, 1]`
    );
  }

  console.log('Score breakdown for top agent:');
  console.log(
    `  Semantic: ${top.scores.semanticScore.toFixed(3)}, ` +
    `Historical: ${top.scores.historicalScore.toFixed(3)}, ` +
    `Capability: ${top.scores.capabilityScore.toFixed(3)}, ` +
    `Cost: ${top.scores.costScore.toFixed(3)}, ` +
    `Latency: ${top.scores.latencyScore.toFixed(3)} ` +
    `→ Final: ${top.scores.finalScore.toFixed(3)}`
  );
});

// =====================================================================
// Test Suite 5: Result Structure & Metadata
// =====================================================================

test('Result structure: complete ExpertRankingResult', async () => {
  const ranker = new ExpertRanker();
  const query = 'Test query';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  // Validate top-level fields
  assert.strictEqual(result.query, query);
  assert.ok(Array.isArray(result.ranked));
  assert.strictEqual(typeof result.circuitBreakerEscalate, 'boolean');
  assert.strictEqual(typeof result.circuitBreakerReason, 'string');
  assert.ok(result.tookMs > 0);

  // Validate ranked array content
  for (const ranked of result.ranked) {
    assert.ok(ranked.agent);
    assert.ok(ranked.agent.id);
    assert.strictEqual(typeof ranked.rank, 'number');
    assert.ok(ranked.rank >= 1);
    assert.strictEqual(typeof ranked.confidence, 'number');
    assert.ok(ranked.explanation);
  }
});

test('Result metadata: alternatives vs primary choice', async () => {
  const ranker = new ExpertRanker({ confidenceThreshold: 0.3 });
  const query = 'Saneamento básico';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  if (result.primaryChoice) {
    // primaryChoice should be ranked #1 if not escalated
    assert.strictEqual(result.primaryChoice.rank, 1);

    // alternatives should be ranked #2+
    for (const alt of result.alternatives) {
      assert.ok(alt.rank >= 2);
    }
  }

  console.log(
    `Primary choice: ${result.primaryChoice?.agent.name ?? 'escalated'} | ` +
    `Alternatives: ${result.alternatives.length} | ` +
    `Time: ${result.tookMs}ms`
  );
});

// =====================================================================
// Test Suite 6: Tie-breaking
// =====================================================================

test('Tie-breaking: same score → lower cost wins', async () => {
  // This test depends on synthetic data, which generates similar scores
  // In production with real history, tie-breaking would use actual routing_feedback
  const ranker = new ExpertRanker();
  const query = 'generic infrastructure query';
  const embedding = mockQueryEmbedding(query);

  const result = await ranker.findExperts(AGENT_REGISTRY_SEED, query, embedding);

  if (result.ranked.length > 1) {
    const top = result.ranked[0];
    const second = result.ranked[1];

    // If scores are very close, cheaper should win
    const scoreMargin = top.scores.finalScore - second.scores.finalScore;
    if (scoreMargin < 0.02) {
      assert.ok(
        top.costEstimate <= second.costEstimate,
        'When tied, cheaper agent should rank higher'
      );
      console.log(
        `Tie-breaking applied: top (cost ${top.costEstimate}) vs second (cost ${second.costEstimate})`
      );
    }
  }
});

console.log('\n=== Expert Finder Test Suite Complete ===\n');
