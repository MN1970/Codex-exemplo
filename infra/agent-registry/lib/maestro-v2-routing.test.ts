/**
 * maestro-v2-routing.test.ts
 * ---------------------------------------------------------------------
 * Test skeleton for maestro-v2-routing.ts.
 *
 * Uses Node's built-in test runner (`node:test` + `node:assert/strict`)
 * so it runs with zero new dependencies — no vitest/jest to add to the
 * repo just for this module. If Manta standardizes on vitest/jest
 * elsewhere, these `describe`/`it` calls translate 1:1; only the two
 * `node:*` imports would need to change.
 *
 * Run (after compiling, or via ts-node/tsx):
 *   npx tsc infra/agent-registry/lib/maestro-v2-routing.ts \
 *       infra/agent-registry/lib/maestro-v2-routing.test.ts \
 *       --module commonjs --target es2020 --outDir /tmp/mv2-build
 *   node --test /tmp/mv2-build/maestro-v2-routing.test.js
 *
 * or, with tsx installed:
 *   npx tsx --test infra/agent-registry/lib/maestro-v2-routing.test.ts
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

import {
  AGENT_REGISTRY_SEED,
  Bm25Index,
  DEFAULT_BM25_WEIGHT,
  DEFAULT_CONFIDENCE_THRESHOLD,
  DEFAULT_SEMANTIC_WEIGHT,
  EmbeddingProviderError,
  EmptyRegistryError,
  InvalidQueryError,
  InvalidTopKError,
  LocalHashingEmbeddingProvider,
  RankedAgent,
  StaticAgentRegistrySource,
  cosineSimilarity,
  evaluateCircuitBreaker,
  explainRanking,
  rankAgents,
  routeQuery,
  searchAgents,
  tokenize,
  type SearchCandidate,
} from './maestro-v2-routing';

// ---------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------

/** Builds a synthetic candidate pool without touching the real registry/embeddings. */
function fakeCandidates(): SearchCandidate[] {
  const [saneamento, energia, portos] = AGENT_REGISTRY_SEED.filter((a) =>
    ['manta-03-s8', 'manta-03-s9', 'manta-03-s6'].includes(a.id)
  );
  return [
    { agent: saneamento, bm25Raw: 8.2, semanticRaw: 0.81 },
    { agent: energia, bm25Raw: 1.1, semanticRaw: 0.35 },
    { agent: portos, bm25Raw: 0.2, semanticRaw: 0.1 },
  ];
}

// ---------------------------------------------------------------------
// tokenize()
// ---------------------------------------------------------------------

describe('tokenize', () => {
  it('lowercases, strips accents, and drops stopwords', () => {
    const tokens = tokenize('Preciso de uma ETE em São Paulo, com adutora de 800mm.');
    assert.ok(tokens.includes('ete'));
    assert.ok(tokens.includes('sao'));
    assert.ok(tokens.includes('adutora'));
    assert.ok(tokens.includes('800mm'));
    assert.ok(!tokens.includes('de')); // stopword
  });

  it('returns an empty array for whitespace-only input', () => {
    assert.deepEqual(tokenize('   '), []);
  });
});

// ---------------------------------------------------------------------
// Bm25Index
// ---------------------------------------------------------------------

describe('Bm25Index', () => {
  it('scores an agent higher when the query hits its keywords', () => {
    const bm25 = new Bm25Index(AGENT_REGISTRY_SEED);
    const queryTokens = tokenize('preciso projetar uma barragem CFRD de 80m');
    const barragensScore = bm25.score(queryTokens, 'manta-03-s10');
    const portosScore = bm25.score(queryTokens, 'manta-03-s6');
    assert.ok(barragensScore > portosScore);
  });

  it('returns 0 for an unknown agent id', () => {
    const bm25 = new Bm25Index(AGENT_REGISTRY_SEED);
    assert.equal(bm25.score(['barragem'], 'does-not-exist'), 0);
  });
});

// ---------------------------------------------------------------------
// cosineSimilarity()
// ---------------------------------------------------------------------

describe('cosineSimilarity', () => {
  it('is 1 for identical vectors', () => {
    assert.equal(cosineSimilarity([1, 2, 3], [1, 2, 3]), 1);
  });

  it('is 0 for orthogonal vectors', () => {
    assert.equal(cosineSimilarity([1, 0], [0, 1]), 0);
  });

  it('is 0 (not NaN) for a zero-length vector', () => {
    assert.equal(cosineSimilarity([0, 0, 0], [1, 2, 3]), 0);
  });
});

// ---------------------------------------------------------------------
// LocalHashingEmbeddingProvider
// ---------------------------------------------------------------------

describe('LocalHashingEmbeddingProvider', () => {
  it('is deterministic for the same input', async () => {
    const provider = new LocalHashingEmbeddingProvider(128);
    const a = await provider.embed('barragem CFRD rejeitos');
    const b = await provider.embed('barragem CFRD rejeitos');
    assert.deepEqual(a, b);
  });

  it('produces more similar vectors for overlapping text than unrelated text', async () => {
    const provider = new LocalHashingEmbeddingProvider(256);
    const query = await provider.embed('preciso de uma adutora e ETE para saneamento');
    const close = await provider.embed('projeto de ETE e adutora de saneamento urbano');
    const far = await provider.embed('dimensionamento de pista de pouso ICAO');
    assert.ok(cosineSimilarity(query, close) > cosineSimilarity(query, far));
  });
});

// ---------------------------------------------------------------------
// rankAgents
// ---------------------------------------------------------------------

describe('rankAgents', () => {
  it('sorts candidates by weighted score, best first', () => {
    const ranked = rankAgents(fakeCandidates(), 'preciso de uma ETE e adutora');
    assert.equal(ranked[0].agent.id, 'manta-03-s8');
    assert.equal(ranked[0].rank, 1);
    assert.ok(ranked[0].finalScore >= ranked[1].finalScore);
    assert.ok(ranked[1].finalScore >= ranked[2].finalScore);
  });

  it('applies the default 0.6/0.4 blend', () => {
    assert.equal(DEFAULT_BM25_WEIGHT, 0.6);
    assert.equal(DEFAULT_SEMANTIC_WEIGHT, 0.4);
    const ranked = rankAgents(fakeCandidates(), 'ETE adutora saneamento');
    for (const r of ranked) {
      const expected =
        (DEFAULT_BM25_WEIGHT * r.bm25Score + DEFAULT_SEMANTIC_WEIGHT * r.semanticScore) /
        (DEFAULT_BM25_WEIGHT + DEFAULT_SEMANTIC_WEIGHT);
      assert.ok(Math.abs(r.finalScore - expected) < 1e-9);
    }
  });

  it('returns an empty array for an empty candidate pool', () => {
    assert.deepEqual(rankAgents([], 'qualquer coisa'), []);
  });

  it('rejects an empty query', () => {
    assert.throws(() => rankAgents(fakeCandidates(), ''), InvalidQueryError);
  });
});

// ---------------------------------------------------------------------
// evaluateCircuitBreaker
// ---------------------------------------------------------------------

describe('evaluateCircuitBreaker', () => {
  it('escalates to opus when top confidence is below the threshold', () => {
    const ranked = rankAgents(fakeCandidates(), 'algo bem genérico e ambíguo');
    // Force a low-confidence scenario regardless of the fixture's real scores.
    const lowConfidence: RankedAgent[] = ranked.map((r) => ({ ...r, confidence: 0.4 }));
    const result = evaluateCircuitBreaker(lowConfidence);
    assert.equal(result.escalate, true);
    assert.equal(result.reason, 'low_confidence');
    assert.equal(result.recommendedTier, 'opus');
  });

  it('does not escalate when confidence clears the threshold with a clear margin', () => {
    const ranked = rankAgents(fakeCandidates(), 'ETE adutora saneamento AySA SNIS');
    const confident: RankedAgent[] = [
      { ...ranked[0], confidence: 0.9, finalScore: 0.9 },
      { ...ranked[1], confidence: 0.3, finalScore: 0.3 },
      { ...ranked[2], confidence: 0.1, finalScore: 0.1 },
    ];
    const result = evaluateCircuitBreaker(confident);
    assert.equal(result.escalate, false);
    assert.equal(result.reason, 'ok');
  });

  it('flags ambiguous top-two even above the confidence threshold', () => {
    const ranked = rankAgents(fakeCandidates(), 'ETE adutora saneamento');
    const ambiguous: RankedAgent[] = [
      { ...ranked[0], confidence: 0.7, finalScore: 0.7 },
      { ...ranked[1], confidence: 0.68, finalScore: 0.68 },
      { ...ranked[2], confidence: 0.1, finalScore: 0.1 },
    ];
    const result = evaluateCircuitBreaker(ambiguous);
    assert.equal(result.escalate, true);
    assert.equal(result.reason, 'ambiguous_top_two');
  });

  it('escalates when there are no candidates at all', () => {
    const result = evaluateCircuitBreaker([]);
    assert.equal(result.escalate, true);
    assert.equal(result.reason, 'no_candidates');
  });

  it('honors a threshold override', () => {
    const ranked = rankAgents(fakeCandidates(), 'ETE adutora saneamento');
    const mid: RankedAgent[] = [{ ...ranked[0], confidence: 0.5, finalScore: 0.5 }];
    assert.equal(evaluateCircuitBreaker(mid, { confidenceThreshold: 0.4 }).escalate, false);
    assert.equal(evaluateCircuitBreaker(mid, { confidenceThreshold: 0.6 }).escalate, true);
    assert.equal(DEFAULT_CONFIDENCE_THRESHOLD, 0.6);
  });
});

// ---------------------------------------------------------------------
// explainRanking
// ---------------------------------------------------------------------

describe('explainRanking', () => {
  it('produces one explanation entry per top-N candidate with the expected shape', () => {
    const ranked = rankAgents(fakeCandidates(), 'ETE adutora saneamento AySA');
    const explained = explainRanking(ranked, 'ETE adutora saneamento AySA', { topN: 2 });

    assert.equal(explained.top_candidates.length, 2);
    assert.equal(explained.weights.bm25, DEFAULT_BM25_WEIGHT);
    assert.equal(explained.weights.semantic, DEFAULT_SEMANTIC_WEIGHT);
    const [first] = explained.top_candidates;
    assert.equal(first.agent_id, 'manta-03-s8');
    assert.ok(first.explanation.length > 0);
    assert.ok(typeof explained.reasoning_summary === 'string');
  });

  it('sets chosen=null and reasons about escalation when the circuit breaker trips', () => {
    const ranked = rankAgents(fakeCandidates(), 'ETE adutora saneamento');
    const lowConfidence: RankedAgent[] = ranked.map((r) => ({ ...r, confidence: 0.2 }));
    const explained = explainRanking(lowConfidence, 'ETE adutora saneamento');
    assert.equal(explained.chosen, null);
    assert.equal(explained.circuit_breaker.escalate, true);
    assert.match(explained.reasoning_summary, /Escalated to Opus/);
  });
});

// ---------------------------------------------------------------------
// searchAgents (integration-ish, uses the static registry + local embeddings)
// ---------------------------------------------------------------------

describe('searchAgents', () => {
  it('returns a non-empty candidate pool for a clear domain query', async () => {
    const result = await searchAgents('barragem CFRD rejeitos ICOLD', 5);
    assert.ok(result.candidates.length > 0);
    assert.equal(result.registrySource, 'claude-md-static');
  });

  it('rejects an empty query', async () => {
    await assert.rejects(() => searchAgents('', 5), InvalidQueryError);
  });

  it('rejects a non-positive top_k', async () => {
    await assert.rejects(() => searchAgents('barragem', 0), InvalidTopKError);
  });

  it('rejects a top_k above the max', async () => {
    await assert.rejects(() => searchAgents('barragem', 999), InvalidTopKError);
  });

  it('surfaces EmbeddingProviderError instead of throwing raw errors', async () => {
    const failingProvider = {
      name: 'always-fails',
      dimensions: 8,
      embed: async () => {
        throw new Error('network down');
      },
    };
    await assert.rejects(
      () => searchAgents('barragem', 3, { embeddingProvider: failingProvider }),
      EmbeddingProviderError
    );
  });

  it('throws EmptyRegistryError when every agent is marked down', async () => {
    const allDown = new StaticAgentRegistrySource(
      AGENT_REGISTRY_SEED.map((a) => ({ ...a, status: 'down' as const }))
    );
    await assert.rejects(
      () => searchAgents('barragem', 3, { registrySource: allDown }),
      EmptyRegistryError
    );
  });
});

// ---------------------------------------------------------------------
// routeQuery (end-to-end orchestrator)
// ---------------------------------------------------------------------

describe('routeQuery', () => {
  it('routes a clear, unambiguous query to a primary agent with high confidence', async () => {
    const decision = await routeQuery('Preciso projetar uma barragem CFRD de 80m de altura', 5);
    assert.ok(decision.primary !== null || decision.circuitBreaker.escalate);
    assert.ok(Array.isArray(decision.alternatives));
    assert.ok(decision.explanation.top_candidates.length > 0);
  });

  it('never throws for a vague query — it escalates via the circuit breaker instead', async () => {
    const decision = await routeQuery('me ajuda com uma coisa', 5);
    assert.ok(typeof decision.circuitBreaker.escalate === 'boolean');
  });
});
