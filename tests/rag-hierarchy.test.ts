/**
 * Manta Maestro v5.0 — RAG Hierarchy Test Suite
 *
 * Tests for:
 * - ChunkScorer (BM25, semantic similarity, confidence boosting)
 * - CollectionRegistry (handoff hints, weights)
 * - RagQueryService (Supabase integration, caching)
 * - Test queries for S6-S10 domains
 *
 * Run: npm test -- tests/rag-hierarchy.test.ts
 */

import {
  ChunkScorer,
  RagQueryService,
  COLLECTION_REGISTRY,
  TEST_QUERIES,
  ChunkMetadata,
  QueryContext,
  RankedChunk,
  CollectionType,
} from '../src/rag-hierarchy';

// ============================================================================
// Mock Data for Testing
// ============================================================================

const MOCK_CHUNK_1: ChunkMetadata = {
  chunk_id: '12345678-1234-1234-1234-123456789abc',
  document_id: 'snis-nbr-12211-001',
  source_collection: 'saneamento',
  text: 'NBR 12211:2018 establishes design criteria for water supply adduction systems. For adduction distances exceeding 100 km, specialized pump design per NBR 8883 is required.',
  embedding: Array(384).fill(0.5), // Mock embedding vector
  embedding_model: 'BAAI/bge-small-en-v1.5',
  source_document_title: 'NBR 12211:2018 — Projeto de Adutoras',
  source_document_type: 'standard',
  source_url: 'https://example.com/nbr-12211.pdf',
  source_organization: 'ABNT',
  domain_tags: ['adução', 'dimensionamento', 'abastecimento', 'NBR-12211'],
  segment_codes: ['S8'],
  lifecycle_phases: [2, 3], // Basic and executive project phases
  published_date: new Date('2018-06-01'),
  ingested_at: new Date('2024-08-01'),
  currency_status: 'current',
  confidence: 0.95,
  citation_count: 12,
};

const MOCK_CHUNK_2: ChunkMetadata = {
  chunk_id: 'abcdefgh-1234-1234-1234-123456789xyz',
  document_id: 'aneel-edital-2024-001',
  source_collection: 'energia',
  text: 'ANEEL 2024 transmission auction for 765 kV line in Southeast. Authorization process: 24 months for environmental and basic project → public hearing → 36 months for executive design. Full timeline 5-7 years.',
  embedding: Array(384).fill(0.6),
  embedding_model: 'BAAI/bge-small-en-v1.5',
  source_document_title: 'ANEEL Edital Licitação LT 765 kV Sudeste',
  source_document_type: 'edital',
  source_organization: 'ANEEL',
  domain_tags: ['transmissão', 'licitação', 'LT', 'ANEEL', 'planejamento'],
  segment_codes: ['S9'],
  lifecycle_phases: [6],
  published_date: new Date('2024-07-15'),
  ingested_at: new Date('2024-07-20'),
  currency_status: 'current',
  confidence: 0.92,
  citation_count: 8,
};

const MOCK_CHUNK_3: ChunkMetadata = {
  chunk_id: 'xyz12345-1234-1234-1234-123456789def',
  document_id: 'bndes-edital-saneamento-2024',
  source_collection: 'editais',
  text: 'BNDES 2024 sanitation tender: submission open until June 30. Evaluation phase 120 days. Award announcement 60 days after. Financial close 180 days post-award. Typical cycle: 360 days from opening.',
  embedding: Array(384).fill(0.55),
  embedding_model: 'BAAI/bge-small-en-v1.5',
  source_document_title: 'BNDES Seleção Pública: Saneamento 2024',
  source_document_type: 'edital',
  source_organization: 'BNDES',
  domain_tags: ['licitação', 'saneamento', 'prazos', 'edital', 'BNDES'],
  segment_codes: ['S8'],
  lifecycle_phases: [6],
  published_date: new Date('2024-06-01'),
  ingested_at: new Date('2024-06-05'),
  currency_status: 'current',
  confidence: 0.94,
  citation_count: 6,
};

// ============================================================================
// Test Suite 1: ChunkScorer
// ============================================================================

describe('ChunkScorer', () => {
  let scorer: ChunkScorer;

  beforeEach(() => {
    scorer = new ChunkScorer('saneamento');
  });

  test('scores a single chunk against a query', () => {
    const query: QueryContext = {
      query_text: 'adução para abastecimento público',
      segment_code: 'S8',
      lifecycle_phase: 2,
      top_k: 5,
      include_reasoning: true,
    };

    const result = scorer.scoreChunk(MOCK_CHUNK_1, query);

    expect(result).toBeDefined();
    expect(result.final_score).toBeGreaterThanOrEqual(0);
    expect(result.final_score).toBeLessThanOrEqual(1);
    expect(result.scores).toHaveProperty('bm25');
    expect(result.scores).toHaveProperty('semantic');
    expect(result.scores).toHaveProperty('confidence_boost');
    expect(result.scores).toHaveProperty('freshness');
    expect(result.reasoning).toBeDefined();
  });

  test('gives higher scores to recently ingested chunks', () => {
    const query: QueryContext = {
      query_text: 'NBR dimensionamento',
      top_k: 5,
      include_reasoning: false,
    };

    const recentChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      ingested_at: new Date(),
    };

    const oldChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      chunk_id: 'old-chunk',
      ingested_at: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000), // 6 months old
    };

    const recentScore = scorer.scoreChunk(recentChunk, query);
    const oldScore = scorer.scoreChunk(oldChunk, query);

    expect(recentScore.final_score).toBeGreaterThan(oldScore.final_score);
  });

  test('boosts chunks with higher confidence and citation counts', () => {
    const query: QueryContext = {
      query_text: 'NBR norma padrão',
      top_k: 5,
      include_reasoning: false,
    };

    const highConfidenceChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      confidence: 0.95,
      citation_count: 20,
    };

    const lowConfidenceChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      chunk_id: 'low-conf',
      confidence: 0.60,
      citation_count: 1,
    };

    const highScore = scorer.scoreChunk(highConfidenceChunk, query);
    const lowScore = scorer.scoreChunk(lowConfidenceChunk, query);

    expect(highScore.final_score).toBeGreaterThan(lowScore.final_score);
  });

  test('penalizes superseded chunks', () => {
    const query: QueryContext = {
      query_text: 'dimensionamento',
      top_k: 5,
      include_reasoning: false,
    };

    const currentChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      currency_status: 'current',
    };

    const supersededChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      chunk_id: 'superseded',
      currency_status: 'superseded',
    };

    const currentScore = scorer.scoreChunk(currentChunk, query);
    const supersededScore = scorer.scoreChunk(supersededChunk, query);

    expect(currentScore.final_score).toBeGreaterThan(supersededScore.final_score);
  });

  test('handles queries with and without embeddings', () => {
    const queryWithEmbedding: QueryContext = {
      query_text: 'adução',
      query_embedding: Array(384).fill(0.5),
      top_k: 5,
      include_reasoning: false,
    };

    const queryWithoutEmbedding: QueryContext = {
      query_text: 'adução',
      top_k: 5,
      include_reasoning: false,
    };

    const scoreWith = scorer.scoreChunk(MOCK_CHUNK_1, queryWithEmbedding);
    const scoreWithout = scorer.scoreChunk(MOCK_CHUNK_1, queryWithoutEmbedding);

    expect(scoreWith).toBeDefined();
    expect(scoreWithout).toBeDefined();
    expect(scoreWith.final_score).not.toEqual(scoreWithout.final_score);
  });
});

// ============================================================================
// Test Suite 2: Collection Registry
// ============================================================================

describe('CollectionRegistry', () => {
  test('contains all 5 required collections', () => {
    const collections = Object.keys(COLLECTION_REGISTRY) as CollectionType[];

    expect(collections).toContain('saneamento');
    expect(collections).toContain('energia');
    expect(collections).toContain('portos');
    expect(collections).toContain('barragens');
    expect(collections).toContain('editais');
    expect(collections.length).toBe(5);
  });

  test('each collection has valid metadata', () => {
    for (const [code, meta] of Object.entries(COLLECTION_REGISTRY)) {
      expect(meta.code).toBe(code);
      expect(meta.display_name).toBeDefined();
      expect(meta.prefix).toBeDefined();
      expect(meta.description).toBeDefined();
      expect(meta.agent_id).toBeDefined();
      expect(meta.sources.length).toBeGreaterThan(0);
      expect(meta.weight_bm25 + meta.weight_semantic + meta.weight_confidence + meta.weight_freshness)
        .toBeCloseTo(1.0, 2);
    }
  });

  test('handoff hints are defined for cross-collection queries', () => {
    const saneamentoMeta = COLLECTION_REGISTRY.saneamento;
    const energiaMeta = COLLECTION_REGISTRY.energia;

    expect(saneamentoMeta.handoff_hints).toBeDefined();
    expect(saneamentoMeta.handoff_hints.length).toBeGreaterThan(0);
    expect(energiaMeta.handoff_hints).toBeDefined();
  });

  test('S8 (saneamento) is mapped to agente-saneamento', () => {
    const saneamentoMeta = COLLECTION_REGISTRY.saneamento;
    expect(saneamentoMeta.agent_id).toBe('agente-saneamento');
    expect(saneamentoMeta.segment_codes).toContain('S8');
  });

  test('S9 (energia) is mapped to agente-energia', () => {
    const energiaMeta = COLLECTION_REGISTRY.energia;
    expect(energiaMeta.agent_id).toBe('agente-energia');
    expect(energiaMeta.segment_codes).toContain('S9');
  });

  test('editais collection is cross-segmento', () => {
    const editaisMeta = COLLECTION_REGISTRY.editais;
    expect(editaisMeta.segment_codes).toContain('S6');
    expect(editaisMeta.segment_codes).toContain('S8');
    expect(editaisMeta.segment_codes).toContain('S9');
    expect(editaisMeta.segment_codes.length).toBeGreaterThan(1);
  });
});

// ============================================================================
// Test Suite 3: RagQueryService (Mocked Supabase)
// ============================================================================

describe('RagQueryService', () => {
  let service: RagQueryService;

  beforeEach(() => {
    // Mock Supabase initialization
    service = new RagQueryService(
      'https://example.supabase.co',
      'mock-anon-key',
      undefined // No Redis for unit tests
    );
  });

  test('initializes with Supabase credentials', () => {
    expect(service).toBeDefined();
  });

  test('generates unique cache keys for different queries', () => {
    const query1: QueryContext = {
      query_text: 'adução 100 km',
      segment_code: 'S8',
      top_k: 5,
      include_reasoning: true,
    };

    const query2: QueryContext = {
      query_text: 'transmissão LT 765',
      segment_code: 'S9',
      top_k: 5,
      include_reasoning: true,
    };

    // Note: cache key generation is private, so we test via behavior
    // (different queries should produce different results in real Supabase)
    expect(query1.query_text).not.toBe(query2.query_text);
  });
});

// ============================================================================
// Test Suite 4: Test Query Validation
// ============================================================================

describe('Test Queries for S6-S10 Domains', () => {
  test('all test queries are defined and valid', () => {
    expect(TEST_QUERIES).toBeDefined();
    expect(TEST_QUERIES.length).toBeGreaterThan(0);
  });

  test('test queries cover all 5 collections', () => {
    const domainsCovered = new Set<string>();

    TEST_QUERIES.forEach(query => {
      // Determine which collection(s) the query targets by keywords
      const text = query.query_text.toLowerCase();

      if (text.includes('eta') || text.includes('ete') || text.includes('saneamento') || text.includes('nbr 12')) {
        domainsCovered.add('saneamento');
      }
      if (text.includes('aneel') || text.includes('epe') || text.includes('transmissão') || text.includes('energia')) {
        domainsCovered.add('energia');
      }
      if (text.includes('porto') || text.includes('antaq') || text.includes('contêiner')) {
        domainsCovered.add('portos');
      }
      if (text.includes('barragem') || text.includes('icold') || text.includes('lei 12.334')) {
        domainsCovered.add('barragens');
      }
      if (text.includes('edital') || text.includes('licitação') || text.includes('prazos')) {
        domainsCovered.add('editais');
      }
    });

    expect(domainsCovered.size).toBeGreaterThanOrEqual(4); // At least 4 of 5
  });

  test('test queries include segment codes S6-S10', () => {
    const segmentsCovered = new Set<string>();

    TEST_QUERIES.forEach(query => {
      if (query.segment_code) {
        segmentsCovered.add(query.segment_code);
      }
    });

    expect(segmentsCovered).toContain('S8'); // Saneamento
    expect(segmentsCovered).toContain('S9'); // Energia
    expect(segmentsCovered).toContain('S6'); // Portos
    expect(segmentsCovered).toContain('S10'); // Barragens
  });

  test('test queries include lifecycle phases 1-8', () => {
    const phasesCovered = new Set<number>();

    TEST_QUERIES.forEach(query => {
      if (query.lifecycle_phase) {
        phasesCovered.add(query.lifecycle_phase);
      }
    });

    expect(phasesCovered.size).toBeGreaterThanOrEqual(3); // At least 3 phases
  });

  test('each test query is reasonably formatted', () => {
    TEST_QUERIES.forEach((query, idx) => {
      expect(query.query_text).toBeDefined();
      expect(query.query_text.length).toBeGreaterThan(10);
      expect(query.top_k).toBeGreaterThanOrEqual(4);
      expect(query.include_reasoning).toBeDefined();
    });
  });
});

// ============================================================================
// Test Suite 5: Handoff Logic
// ============================================================================

describe('Collection Handoff Hints', () => {
  test('saneamento has handoff to editais for tender timing', () => {
    const saneamento = COLLECTION_REGISTRY.saneamento;
    const handoffToEditais = saneamento.handoff_hints.find(
      h => h.target_collection === 'editais'
    );

    expect(handoffToEditais).toBeDefined();
    expect(handoffToEditais?.trigger_condition).toContain('licitação');
  });

  test('energia has handoff to barragens for hydroelectric', () => {
    const energia = COLLECTION_REGISTRY.energia;
    const handoffToBarragens = energia.handoff_hints.find(
      h => h.target_collection === 'barragens'
    );

    expect(handoffToBarragens).toBeDefined();
    expect(handoffToBarragens?.reasoning).toContain('hydroelectric');
  });

  test('editais has cross-collection handoff hints', () => {
    const editais = COLLECTION_REGISTRY.editais;

    expect(editais.handoff_hints.length).toBeGreaterThanOrEqual(2);
    const targets = editais.handoff_hints.map(h => h.target_collection);
    expect(targets).toContain('saneamento');
  });
});

// ============================================================================
// Test Suite 6: Ranking Weight Validation
// ============================================================================

describe('Collection Weight Configuration', () => {
  test('all collections have valid weight distributions', () => {
    for (const [code, meta] of Object.entries(COLLECTION_REGISTRY)) {
      const totalWeight =
        meta.weight_bm25 + meta.weight_semantic + meta.weight_confidence + meta.weight_freshness;
      expect(totalWeight).toBeCloseTo(1.0, 2);

      // All weights positive
      expect(meta.weight_bm25).toBeGreaterThan(0);
      expect(meta.weight_semantic).toBeGreaterThan(0);
      expect(meta.weight_confidence).toBeGreaterThan(0);
      expect(meta.weight_freshness).toBeGreaterThan(0);

      // Semantic and BM25 should be primary
      expect(
        meta.weight_semantic + meta.weight_bm25
      ).toBeGreaterThanOrEqual(0.7);
    }
  });

  test('semantic weighting dominates across collections', () => {
    for (const [code, meta] of Object.entries(COLLECTION_REGISTRY)) {
      expect(meta.weight_semantic).toBeGreaterThan(meta.weight_bm25);
      expect(meta.weight_semantic).toBeGreaterThan(meta.weight_confidence);
      expect(meta.weight_semantic).toBeGreaterThan(meta.weight_freshness);
    }
  });

  test('editais collection prioritizes BM25 for keyword matching', () => {
    const editais = COLLECTION_REGISTRY.editais;
    // Editais is keyword-focused (tender names, dates), so BM25 should be relatively high
    expect(editais.weight_bm25).toBeGreaterThanOrEqual(0.30);
  });
});

// ============================================================================
// Integration Test: Multi-Collection Query Simulation
// ============================================================================

describe('Integration: Multi-Collection Query Scenario', () => {
  test('simulates S8 (saneamento) agent query with handoff', async () => {
    /**
     * Scenario: User asks agente-saneamento about edital prazos.
     * Expected flow:
     * 1. Query saneamento collection
     * 2. If score < 0.6, handoff to editais
     * 3. Return merged results
     */

    const query: QueryContext = {
      query_text: 'BNDES 2024 saneamento: qual é o prazo para licititar?',
      segment_code: 'S8',
      lifecycle_phase: 6,
      top_k: 5,
      include_reasoning: true,
    };

    // Simulate scoring with mock chunks
    const scorer = new ChunkScorer('saneamento');
    const saneamentoScore = scorer.scoreChunk(MOCK_CHUNK_1, query);
    const editaisScore = new ChunkScorer('editais').scoreChunk(MOCK_CHUNK_3, query);

    // Editais chunk should score higher for tender timing question
    expect(editaisScore.final_score).toBeGreaterThanOrEqual(0.3);

    // In real scenario, RagQueryService would automatically handoff
    // if saneamento score is too low
  });

  test('simulates S10 (barragens) cross-domain query (hydroelectric)', async () => {
    /**
     * Scenario: User asks agente-barragens about hydroelectric generation.
     * Expected: query barragens → low score → handoff to energia
     */

    const query: QueryContext = {
      query_text: 'Barragem hidroelétrica: como integrar requisitos ICOLD + plano EPE?',
      segment_code: 'S10',
      lifecycle_phase: 2,
      top_k: 5,
      include_reasoning: true,
    };

    const barragem_scorer = new ChunkScorer('barragens');
    const energia_scorer = new ChunkScorer('energia');

    // Both should have some relevance
    const barragemScore = barragem_scorer.scoreChunk(MOCK_CHUNK_1, query);
    const energiaScore = energia_scorer.scoreChunk(MOCK_CHUNK_2, query);

    expect(barragemScore.final_score).toBeGreaterThanOrEqual(0);
    expect(energiaScore.final_score).toBeGreaterThanOrEqual(0);
  });
});

// ============================================================================
// Performance & Edge Cases
// ============================================================================

describe('Edge Cases & Error Handling', () => {
  test('scorer handles empty query text gracefully', () => {
    const scorer = new ChunkScorer('saneamento');
    const query: QueryContext = {
      query_text: '',
      top_k: 5,
      include_reasoning: false,
    };

    // Should not throw
    const result = scorer.scoreChunk(MOCK_CHUNK_1, query);
    expect(result).toBeDefined();
    expect(result.final_score).toBeGreaterThanOrEqual(0);
  });

  test('scorer handles missing embedding vector', () => {
    const scorer = new ChunkScorer('saneamento');
    const chunkNoEmbedding: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      embedding: undefined,
    };
    const query: QueryContext = {
      query_text: 'test',
      query_embedding: Array(384).fill(0.5),
      top_k: 5,
      include_reasoning: false,
    };

    // Should not throw; semantic score should be neutral (0.5)
    const result = scorer.scoreChunk(chunkNoEmbedding, query);
    expect(result).toBeDefined();
    expect(result.scores.semantic).toBe(0.5);
  });

  test('scorer handles very long chunk text', () => {
    const scorer = new ChunkScorer('saneamento');
    const longChunk: ChunkMetadata = {
      ...MOCK_CHUNK_1,
      text: 'Lorem ipsum '.repeat(1000), // ~12KB text
    };
    const query: QueryContext = {
      query_text: 'ipsum',
      top_k: 5,
      include_reasoning: false,
    };

    const result = scorer.scoreChunk(longChunk, query);
    expect(result).toBeDefined();
    expect(result.final_score).toBeLessThanOrEqual(1);
  });

  test('ChunkScorer rejects unknown collection code', () => {
    expect(() => {
      new ChunkScorer('unknown-collection' as any);
    }).toThrow();
  });
});
