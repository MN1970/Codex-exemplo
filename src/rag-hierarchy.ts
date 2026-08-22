/**
 * Manta Maestro v5.0 — RAG Hierarchy & Relevance Ranking
 *
 * Implements a 5-collection RAG system with:
 * - Metadata schema (source_collection, domain_tags, confidence, recency, citation_count)
 * - Multi-factor relevance ranking (BM25 + semantic similarity + confidence boost)
 * - Collection registry with handoff hints
 * - Supabase pgvector integration
 * - Redis caching (1-hour TTL)
 * - Test queries for S6-S10 domains
 *
 * Ticket: MNT-2026-RAG-HIERARCHY-V5
 * Status: DRAFT (requires gate before prod deploy)
 */

import { createClient } from '@supabase/supabase-js';

// ============================================================================
// 1. TYPE DEFINITIONS & METADATA SCHEMA
// ============================================================================

/**
 * RAG Chunk Metadata Schema
 * Captures provenance, reliability, and recency signals for each chunk
 */
export interface ChunkMetadata {
  // Identifiers
  chunk_id: string;               // UUID
  document_id: string;            // Source document identifier
  source_collection: CollectionType;

  // Content & Embeddings
  text: string;                   // Raw chunk text
  embedding?: number[];           // vector(384): BAAI/bge-small-en-v1.5
  embedding_model?: string;       // e.g., 'BAAI/bge-small-en-v1.5'

  // Provenance & Trust
  source_document_title: string;
  source_document_type: 'regulation' | 'tender' | 'edital' | 'standard' | 'guide' | 'case_study';
  source_url?: string;            // PDF link, SharePoint path, etc.
  source_organization?: string;   // SNIS, ANEEL, ANTAQ, ICOLD, etc.

  // Domain Tagging
  domain_tags: string[];          // ['saneamento', 'ETA', 'NBR-12211'] or ['transmissao', 'LT', 'ANEEL']
  segment_codes: string[];        // S6, S7, S8, S9, S10 (cross-collection possible)
  lifecycle_phases: number[];     // 1-8: which phases this applies to

  // Recency & Freshness
  published_date?: Date;          // Original publication date
  ingested_at: Date;              // When added to RAG
  last_updated_at?: Date;         // When chunk refreshed (if tracking versions)
  currency_status: 'current' | 'draft' | 'superseded' | 'historical';

  // Reliability Signals
  confidence: number;             // 0.0-1.0: model confidence in chunk quality
  citation_count: number;         // How many internal docs reference this chunk
  relevance_feedback_score?: number;  // Bayesian score from user feedback (-1 to +1)

  // Operational
  chunk_order?: number;           // Position in original document (for coherence)
  window_size?: number;           // Sliding window context size used
}

/**
 * Ranked Retrieval Result
 */
export interface RankedChunk {
  chunk: ChunkMetadata;
  scores: {
    bm25: number;               // Lexical similarity [0..1]
    semantic: number;           // Cosine similarity [-1..1], normalized to [0..1]
    confidence_boost: number;   // Confidence + citation_count signal
    freshness: number;          // Recency score [0..1]
    feedback: number;           // Learned feedback signal
  };
  final_score: number;          // Weighted combination
  rank: number;                 // Position in result set
  reasoning?: string;           // Why this chunk was selected (debug)
}

/**
 * Five RAG Collections
 */
export type CollectionType = 'saneamento' | 'energia' | 'portos' | 'barragens' | 'editais';

export interface CollectionMetadata {
  code: CollectionType;
  display_name: string;
  prefix: string;               // Storage prefix in Supabase (e.g., 'san:')
  description: string;
  segment_codes: string[];
  agent_id: string;             // Primary agent that owns this collection
  agent_fallback?: string[];    // Secondary agents (handoff targets)

  // Handoff hints: "when this collection doesn't have a good match, also check..."
  handoff_hints: CollectionHandoff[];

  // Source specifications
  sources: SourceSpec[];
  indexing_frequency: string;   // e.g., 'daily', 'weekly', 'on-demand'
  last_indexed_at?: Date;

  // Search tuning
  default_top_k: number;
  bm25_k1: number;              // BM25 saturation parameter
  bm25_b: number;               // BM25 length norm parameter
  weight_bm25: number;          // Final weighting (0..1)
  weight_semantic: number;
  weight_confidence: number;
  weight_freshness: number;
}

/**
 * Collection handoff hint: if primary collection has low confidence,
 * also check secondary collection with this reasoning.
 */
export interface CollectionHandoff {
  target_collection: CollectionType;
  trigger_condition: string;    // e.g., 'score < 0.5', 'no_results', 'cross_segment'
  reasoning: string;            // e.g., "ANEEL edital might reference ANTAQ for cross-modal projects"
}

export interface SourceSpec {
  name: string;
  type: 'database' | 'document_set' | 'api_feed';
  location: string;             // SharePoint path, URL, query, etc.
  metadata_fields: Record<string, string>;  // e.g., { regulation_type: 'NBR', year: '2023' }
}

/**
 * Query context passed to ranking functions
 */
export interface QueryContext {
  query_text: string;
  query_embedding?: number[];
  user_email?: string;
  segment_code?: string;        // Optional segment hint (S6-S10)
  lifecycle_phase?: number;     // 1-8
  top_k: number;
  include_reasoning: boolean;
}

// ============================================================================
// 2. COLLECTION REGISTRY
// ============================================================================

/**
 * Manta Maestro RAG Collection Registry v5.0
 * Defines all 5 collections, their sources, agents, and handoff logic
 */
export const COLLECTION_REGISTRY: Record<CollectionType, CollectionMetadata> = {
  saneamento: {
    code: 'saneamento',
    display_name: 'SNIS & Saneamento',
    prefix: 'san:',
    description: 'Saneamento, ETA/ETE, adutoras, NBR 12211-12218, Lei 14.026, editais BNDES AySA',
    segment_codes: ['S8'],
    agent_id: 'agente-saneamento',
    agent_fallback: ['manta-02', 'manta-05'],  // contratual, orcamento
    handoff_hints: [
      {
        target_collection: 'editais',
        trigger_condition: 'score < 0.6 AND contains("licitação")',
        reasoning: 'SNIS may not cover tender timing; check editais for recent public bids',
      },
      {
        target_collection: 'energia',
        trigger_condition: 'contains("subestação") OR contains("energia")',
        reasoning: 'Cross-domain: saneamento projects may have power requirements',
      },
    ],
    sources: [
      {
        name: 'SNIS Database',
        type: 'database',
        location: 'SharePoint://03_Projetos/Saneamento/SNIS_2024',
        metadata_fields: { source: 'SNIS', year: '2024', language: 'pt-BR' },
      },
      {
        name: 'NBR 12211-12218 Series',
        type: 'document_set',
        location: 'SharePoint://Documentos_Tecnico/NBR_Saneamento',
        metadata_fields: { source: 'ABNT', standard_type: 'NBR', category: 'saneamento' },
      },
      {
        name: 'Lei 14.026 (Marco Regulatório)',
        type: 'document_set',
        location: 'SharePoint://Regulacao/Lei_14026',
        metadata_fields: { source: 'Governo Federal', doc_type: 'law' },
      },
      {
        name: 'BNDES Editais (Saneamento)',
        type: 'api_feed',
        location: 'https://www.bndes.gov.br/wps/portal/site/home/api',
        metadata_fields: { source: 'BNDES', segment: 'saneamento' },
      },
    ],
    indexing_frequency: 'daily',
    default_top_k: 5,
    bm25_k1: 1.5,
    bm25_b: 0.75,
    weight_bm25: 0.30,
    weight_semantic: 0.45,
    weight_confidence: 0.15,
    weight_freshness: 0.10,
  },

  energia: {
    code: 'energia',
    display_name: 'ANEEL & Energia',
    prefix: 'ene:',
    description: 'ANEEL editais, R1-R5 EPE, ONS, LT/subestações, RAP, IEEE, transmissão leilões',
    segment_codes: ['S9'],
    agent_id: 'agente-energia',
    agent_fallback: ['manta-02', 'manta-05'],  // contratual, orcamento
    handoff_hints: [
      {
        target_collection: 'editais',
        trigger_condition: 'score < 0.6 AND contains("leilão")',
        reasoning: 'ANEEL may reference recent transmission tenders; editais has timing data',
      },
      {
        target_collection: 'barragens',
        trigger_condition: 'contains("hidrelétrica") OR contains("usina")',
        reasoning: 'Energy generation may interact with hydroelectric facilities',
      },
    ],
    sources: [
      {
        name: 'ANEEL Edital Templates',
        type: 'document_set',
        location: 'SharePoint://03_Projetos/Energia/ANEEL_Editais_2024',
        metadata_fields: { source: 'ANEEL', doc_type: 'edital', regulatory: true },
      },
      {
        name: 'EPE Plano Decenal (R1-R5)',
        type: 'document_set',
        location: 'SharePoint://Regulacao/EPE_Plano_Decenal',
        metadata_fields: { source: 'EPE', plan_type: 'decenal', scope: 'brasil' },
      },
      {
        name: 'ONS Procedimentos de Rede',
        type: 'api_feed',
        location: 'https://www.ons.org.br/api/procedimentos',
        metadata_fields: { source: 'ONS', doc_type: 'procedure' },
      },
      {
        name: 'IEEE Power Standards',
        type: 'document_set',
        location: 'SharePoint://Padroes_Internacionais/IEEE_Power',
        metadata_fields: { source: 'IEEE', standard_type: 'IEEE', language: 'en' },
      },
    ],
    indexing_frequency: 'daily',
    default_top_k: 5,
    bm25_k1: 1.5,
    bm25_b: 0.75,
    weight_bm25: 0.28,
    weight_semantic: 0.47,
    weight_confidence: 0.15,
    weight_freshness: 0.10,
  },

  portos: {
    code: 'portos',
    display_name: 'ANTAQ & Portos',
    prefix: 'por:',
    description: 'ANTAQ regulações, PIANC, editais BNDES portos, dragagem, molhe, berço, contêiner',
    segment_codes: ['S6'],
    agent_id: 'agente-portos',
    agent_fallback: ['manta-02', 'manta-05'],  // contratual, orcamento
    handoff_hints: [
      {
        target_collection: 'editais',
        trigger_condition: 'score < 0.5 AND contains("concessão")',
        reasoning: 'Port concessions often tracked in editais; check for tender schedules',
      },
      {
        target_collection: 'energia',
        trigger_condition: 'contains("energia") OR contains("geração")',
        reasoning: 'Ports may have renewable energy generation (offshore wind, solar)',
      },
    ],
    sources: [
      {
        name: 'ANTAQ Database',
        type: 'database',
        location: 'SharePoint://03_Projetos/Portos/ANTAQ_2024',
        metadata_fields: { source: 'ANTAQ', regulatory: true },
      },
      {
        name: 'PIANC Guidelines',
        type: 'document_set',
        location: 'SharePoint://Padroes_Internacionais/PIANC',
        metadata_fields: { source: 'PIANC', standard_type: 'guideline', language: 'en' },
      },
      {
        name: 'BNDES Port Editais',
        type: 'api_feed',
        location: 'https://www.bndes.gov.br/wps/portal/site/home/api',
        metadata_fields: { source: 'BNDES', segment: 'portos' },
      },
    ],
    indexing_frequency: 'weekly',
    default_top_k: 4,
    bm25_k1: 1.6,
    bm25_b: 0.70,
    weight_bm25: 0.25,
    weight_semantic: 0.50,
    weight_confidence: 0.16,
    weight_freshness: 0.09,
  },

  barragens: {
    code: 'barragens',
    display_name: 'ICOLD & Barragens',
    prefix: 'bar:',
    description: 'ICOLD standards, breach analysis, PNSB, Lei 12.334, CBDB, TSF, rejeitos',
    segment_codes: ['S10'],
    agent_id: 'agente-barragens',
    agent_fallback: ['manta-06', 'manta-15'],  // modelagem, advisory
    handoff_hints: [
      {
        target_collection: 'saneamento',
        trigger_condition: 'contains("água") AND contains("captação")',
        reasoning: 'Dams may serve water supply; cross-check with saneamento for integration',
      },
      {
        target_collection: 'energia',
        trigger_condition: 'contains("hidrelétrica") OR contains("geração")',
        reasoning: 'Hydroelectric dams are energy infrastructure; check energia for grid data',
      },
    ],
    sources: [
      {
        name: 'ICOLD Standards',
        type: 'document_set',
        location: 'SharePoint://Padroes_Internacionais/ICOLD',
        metadata_fields: { source: 'ICOLD', standard_type: 'international', language: 'en' },
      },
      {
        name: 'CBDB (Comitê Brasileiro Barragens)',
        type: 'database',
        location: 'SharePoint://03_Projetos/Barragens/CBDB_2024',
        metadata_fields: { source: 'CBDB', regulatory: true },
      },
      {
        name: 'Lei 12.334 (Segurança Barragens)',
        type: 'document_set',
        location: 'SharePoint://Regulacao/Lei_12334',
        metadata_fields: { source: 'Governo Federal', doc_type: 'law' },
      },
      {
        name: 'PNSB Reportagem',
        type: 'api_feed',
        location: 'https://www.snisb.gov.br/api/barragens',
        metadata_fields: { source: 'PNSB', data_type: 'monitoring' },
      },
    ],
    indexing_frequency: 'weekly',
    default_top_k: 4,
    bm25_k1: 1.4,
    bm25_b: 0.80,
    weight_bm25: 0.28,
    weight_semantic: 0.44,
    weight_confidence: 0.18,
    weight_freshness: 0.10,
  },

  editais: {
    code: 'editais',
    display_name: 'Cross-Segmento: Editais & Licitações',
    prefix: 'edit:',
    description: 'Licitação templates, public bids (BNDES, ANP, ANEEL, ANTAQ), tender timing, process benchmarks',
    segment_codes: ['S6', 'S7', 'S8', 'S9', 'S10'],  // All segments
    agent_id: 'manta-05',  // orcamento is primary owner
    agent_fallback: ['manta-02', 'manta-13'],  // contratual, business-dev
    handoff_hints: [
      {
        target_collection: 'saneamento',
        trigger_condition: 'found_match AND contains("AySA")',
        reasoning: 'BNDES saneamento editais often co-reference; load additional context',
      },
      {
        target_collection: 'energia',
        trigger_condition: 'found_match AND contains("EPE")',
        reasoning: 'Energy tenders often multi-phase; check EPE docs for full scope',
      },
    ],
    sources: [
      {
        name: 'BNDES Edital Index',
        type: 'api_feed',
        location: 'https://www.bndes.gov.br/api/editais',
        metadata_fields: { source: 'BNDES', doc_type: 'edital' },
      },
      {
        name: 'Portal da Transparência',
        type: 'api_feed',
        location: 'https://www.portaltransparencia.gov.br/api/licitacoes',
        metadata_fields: { source: 'CGU', doc_type: 'tender' },
      },
      {
        name: 'Licitação Templates (Manta DB)',
        type: 'database',
        location: 'SharePoint://01-agentes-fundamentais/Manta-05_Orcamento/Templates_Licita',
        metadata_fields: { source: 'Manta Associados', doc_type: 'template' },
      },
      {
        name: 'ANP Concessões',
        type: 'api_feed',
        location: 'https://www.anp.gov.br/api/concessions',
        metadata_fields: { source: 'ANP', sector: 'oil_gas' },
      },
    ],
    indexing_frequency: 'daily',
    default_top_k: 6,
    bm25_k1: 1.8,
    bm25_b: 0.65,
    weight_bm25: 0.35,
    weight_semantic: 0.40,
    weight_confidence: 0.14,
    weight_freshness: 0.11,
  },
};

// ============================================================================
// 3. CHUNK SCORER: BM25 + SEMANTIC + CONFIDENCE + FRESHNESS
// ============================================================================

/**
 * ChunkScorer: Multi-factor relevance ranking
 *
 * Combines:
 * - BM25 for lexical/keyword matching
 * - Cosine similarity for semantic embedding match
 * - Confidence boost from metadata signals
 * - Freshness score from recency
 * - Learned feedback from past ratings
 */
export class ChunkScorer {
  private collection: CollectionMetadata;

  constructor(collectionCode: CollectionType) {
    this.collection = COLLECTION_REGISTRY[collectionCode];
    if (!this.collection) {
      throw new Error(`Unknown collection: ${collectionCode}`);
    }
  }

  /**
   * Score a single chunk against a query
   */
  scoreChunk(chunk: ChunkMetadata, query: QueryContext): Omit<RankedChunk, 'rank'> {
    const scores = {
      bm25: this.bm25Score(chunk.text, query.query_text),
      semantic: query.query_embedding
        ? this.normalizeCosineSimilarity(this.cosineSimilarity(
            chunk.embedding || [],
            query.query_embedding
          ))
        : 0.5, // Neutral if no embedding available
      confidence_boost: this.confidenceBoostScore(chunk),
      freshness: this.freshnessScore(chunk),
      feedback: chunk.relevance_feedback_score ?? 0,
    };

    const final_score = this.weightedCombination(scores);

    return {
      chunk,
      scores,
      final_score,
      reasoning: this.generateReasoning(scores, chunk, query),
    };
  }

  /**
   * BM25 (Okapi) scoring for lexical relevance
   * Standard information retrieval metric
   */
  private bm25Score(documentText: string, queryText: string): number {
    const { k1, b } = {
      k1: this.collection.bm25_k1,
      b: this.collection.bm25_b,
    };

    const docTerms = this.tokenize(documentText);
    const queryTerms = this.tokenize(queryText);

    const docLength = docTerms.length;
    const avgDocLength = 250; // Approximate average chunk length
    const corpusSize = 100000; // Estimated corpus size

    let score = 0;
    const termFreqDoc = this.countTerms(docTerms);

    for (const term of queryTerms) {
      const tf = termFreqDoc[term] || 0;
      const df = Math.max(1, Math.round(corpusSize * 0.01)); // Estimate
      const idf = Math.log((corpusSize - df + 0.5) / (df + 0.5) + 1);

      const numerator = tf * (k1 + 1);
      const denominator = tf + k1 * (1 - b + b * (docLength / avgDocLength));

      score += idf * (numerator / denominator);
    }

    return Math.min(1, score / (queryTerms.length * 5)); // Normalize to [0,1]
  }

  /**
   * Cosine similarity between two embedding vectors
   */
  private cosineSimilarity(vecA: number[], vecB: number[]): number {
    if (vecA.length === 0 || vecB.length === 0) return 0;
    if (vecA.length !== vecB.length) return 0;

    let dotProduct = 0;
    let magA = 0;
    let magB = 0;

    for (let i = 0; i < vecA.length; i++) {
      dotProduct += vecA[i] * vecB[i];
      magA += vecA[i] * vecA[i];
      magB += vecB[i] * vecB[i];
    }

    magA = Math.sqrt(magA);
    magB = Math.sqrt(magB);

    if (magA === 0 || magB === 0) return 0;
    return dotProduct / (magA * magB);
  }

  /**
   * Normalize cosine similarity from [-1, 1] to [0, 1]
   */
  private normalizeCosineSimilarity(cosine: number): number {
    return (cosine + 1) / 2;
  }

  /**
   * Confidence boost: combination of metadata confidence + citation count
   * Higher citation_count suggests document is "canonical" or "well-vetted"
   */
  private confidenceBoostScore(chunk: ChunkMetadata): number {
    const confidenceFactor = chunk.confidence || 0.5;
    const citationFactor = Math.min(1, chunk.citation_count / 10); // Cap at 10 citations
    const currentFactor =
      chunk.currency_status === 'current' ? 1.0 :
      chunk.currency_status === 'draft' ? 0.7 :
      chunk.currency_status === 'superseded' ? 0.3 :
      0.5;

    return (confidenceFactor * 0.5 + citationFactor * 0.3 + currentFactor * 0.2);
  }

  /**
   * Freshness score: prefer recently ingested chunks
   * Decay exponentially with age, but plateau after 90 days
   */
  private freshnessScore(chunk: ChunkMetadata): number {
    const now = new Date();
    const ageMs = now.getTime() - chunk.ingested_at.getTime();
    const ageDays = ageMs / (1000 * 60 * 60 * 24);

    if (ageDays <= 7) return 1.0;
    if (ageDays <= 30) return 0.9;
    if (ageDays <= 90) return 0.7;
    return 0.4; // Older than 3 months, still some value
  }

  /**
   * Weighted combination of all signals
   */
  private weightedCombination(scores: {
    bm25: number;
    semantic: number;
    confidence_boost: number;
    freshness: number;
    feedback: number;
  }): number {
    const w = this.collection;
    const sum =
      scores.bm25 * w.weight_bm25 +
      scores.semantic * w.weight_semantic +
      scores.confidence_boost * w.weight_confidence +
      scores.freshness * w.weight_freshness;

    // Feedback adjustment: ±10% effect
    const feedbackAdjustment = 1 + (scores.feedback * 0.1);

    return Math.min(1, Math.max(0, sum * feedbackAdjustment));
  }

  /**
   * Tokenize text for BM25: lowercase, split, remove stopwords
   */
  private tokenize(text: string): string[] {
    const stopwords = new Set([
      'a', 'o', 'de', 'em', 'para', 'por', 'que', 'e', 'é', 'ou', 'não',
      'do', 'da', 'os', 'as', 'um', 'uma', 'the', 'and', 'or', 'is', 'in', 'to',
    ]);

    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(term => term.length > 2 && !stopwords.has(term));
  }

  /**
   * Count term frequencies in a token list
   */
  private countTerms(tokens: string[]): Record<string, number> {
    const counts: Record<string, number> = {};
    for (const token of tokens) {
      counts[token] = (counts[token] || 0) + 1;
    }
    return counts;
  }

  /**
   * Generate explanation for ranking decision (debug/transparency)
   */
  private generateReasoning(
    scores: RankedChunk['scores'],
    chunk: ChunkMetadata,
    query: QueryContext
  ): string {
    const topFactor = Math.max(...Object.values(scores));
    let reason = '';

    if (topFactor === scores.semantic) {
      reason = `Semantic match (similarity: ${(scores.semantic * 100).toFixed(1)}%)`;
    } else if (topFactor === scores.bm25) {
      reason = `Lexical match (BM25: ${(scores.bm25 * 100).toFixed(1)}%)`;
    } else if (topFactor === scores.confidence_boost) {
      reason = `High confidence source (${chunk.citation_count} citations)`;
    } else {
      reason = `Recency weighted`;
    }

    if (chunk.currency_status === 'superseded') {
      reason += ' [superseded]';
    }
    if (scores.feedback < -0.3) {
      reason += ' [historically low feedback]';
    }

    return reason;
  }
}

// ============================================================================
// 4. SUPABASE RAG QUERY INTEGRATION
// ============================================================================

/**
 * RagQueryService: Execute ranked queries against Supabase pgvector
 *
 * Responsibilities:
 * - Query Supabase rag_chunks table by collection
 * - Apply ranking via ChunkScorer
 * - Handle handoff hints (fallback collections)
 * - Cache results in Redis
 */
export class RagQueryService {
  private supabase: ReturnType<typeof createClient>;
  private redis?: any; // Redis client (optional)
  private redisEnabled: boolean;
  private cacheTTLSeconds: number = 3600; // 1 hour

  constructor(
    supabaseUrl: string,
    supabaseKey: string,
    redisClient?: any
  ) {
    this.supabase = createClient(supabaseUrl, supabaseKey);
    this.redis = redisClient;
    this.redisEnabled = !!redisClient;
  }

  /**
   * Execute a ranked RAG query across collections
   *
   * Flow:
   * 1. Check Redis cache (key = hash of query + collection + top_k)
   * 2. Query Supabase rag_chunks for this collection
   * 3. Score and rank via ChunkScorer
   * 4. Apply handoff hints if score is low
   * 5. Cache result
   * 6. Return top-K ranked chunks with lineage
   */
  async queryCollection(
    query: QueryContext,
    collection: CollectionType,
    applyHandoff: boolean = true
  ): Promise<{
    chunks: RankedChunk[];
    collection: CollectionType;
    handoff_applied?: CollectionType;
    cache_hit: boolean;
  }> {
    // Generate cache key
    const cacheKey = this.cacheKey(query, collection);

    // Check cache
    if (this.redisEnabled && this.redis) {
      const cached = await this.getCachedResult(cacheKey);
      if (cached) {
        return { ...cached, cache_hit: true };
      }
    }

    // Query Supabase
    let chunks = await this.fetchChunksFromSupabase(query, collection);

    // Score and rank
    const scorer = new ChunkScorer(collection);
    let ranked = chunks
      .map((chunk, idx) => {
        const scored = scorer.scoreChunk(chunk, query);
        return { ...scored, rank: idx + 1 };
      })
      .sort((a, b) => b.final_score - a.final_score)
      .slice(0, query.top_k);

    // Apply handoff if score is low
    let handoff_applied: CollectionType | undefined;
    const collectionMeta = COLLECTION_REGISTRY[collection];
    const minScore = Math.max(...ranked.map(r => r.final_score), 0);

    if (applyHandoff && minScore < 0.5 && collectionMeta.handoff_hints.length > 0) {
      for (const hint of collectionMeta.handoff_hints) {
        if (hint.trigger_condition === 'score < 0.5' || hint.trigger_condition === 'no_results') {
          const handoffResult = await this.queryCollection(
            query,
            hint.target_collection,
            false // Don't recursively handoff
          );

          if (handoffResult.chunks.length > 0) {
            ranked.push(
              ...handoffResult.chunks
                .slice(0, Math.floor(query.top_k * 0.3)) // Add up to 30% from handoff
            );
            ranked.sort((a, b) => b.final_score - a.final_score);
            ranked = ranked.slice(0, query.top_k);
            handoff_applied = hint.target_collection;
            break;
          }
        }
      }
    }

    const result = {
      chunks: ranked,
      collection,
      handoff_applied,
      cache_hit: false,
    };

    // Cache result
    if (this.redisEnabled && this.redis) {
      await this.cacheResult(cacheKey, result);
    }

    return result;
  }

  /**
   * Multi-collection query: distribute query across multiple collections
   */
  async queryMultiCollection(
    query: QueryContext,
    collections: CollectionType[]
  ): Promise<{
    all_chunks: RankedChunk[];
    by_collection: Record<CollectionType, RankedChunk[]>;
  }> {
    const byCollection: Record<CollectionType, RankedChunk[]> = {} as any;
    const allChunks: RankedChunk[] = [];

    const promises = collections.map(col =>
      this.queryCollection(query, col).then(result => {
        byCollection[col] = result.chunks;
      })
    );

    await Promise.all(promises);

    // Merge and re-rank (ensemble scoring)
    for (const col of collections) {
      allChunks.push(...byCollection[col]);
    }
    allChunks.sort((a, b) => b.final_score - a.final_score);

    return {
      all_chunks: allChunks.slice(0, query.top_k),
      by_collection: byCollection,
    };
  }

  /**
   * Fetch raw chunks from Supabase for a collection
   */
  private async fetchChunksFromSupabase(
    query: QueryContext,
    collection: CollectionType
  ): Promise<ChunkMetadata[]> {
    // If we have query embedding, use vector search; otherwise use full-text
    if (query.query_embedding) {
      return this.fetchVectorSearch(query, collection);
    } else {
      return this.fetchFullTextSearch(query, collection);
    }
  }

  /**
   * Vector search via pgvector (semantic)
   */
  private async fetchVectorSearch(
    query: QueryContext,
    collection: CollectionType
  ): Promise<ChunkMetadata[]> {
    const { data, error } = await this.supabase
      .from('rag_chunks')
      .select('*')
      .eq('source_collection', collection)
      .eq('currency_status', 'current') // Only current docs
      .order('embedding', { ascending: false, foreignTable: 'euclidean' })
      .limit(100); // Get more candidates for ranking

    if (error) {
      console.error('Vector search error:', error);
      return [];
    }

    return (data || []) as ChunkMetadata[];
  }

  /**
   * Full-text search (fallback if no embedding)
   */
  private async fetchFullTextSearch(
    query: QueryContext,
    collection: CollectionType
  ): Promise<ChunkMetadata[]> {
    const { data, error } = await this.supabase
      .from('rag_chunks')
      .select('*')
      .eq('source_collection', collection)
      .eq('currency_status', 'current')
      .textSearch('text', query.query_text) // Full-text search
      .limit(100);

    if (error) {
      console.error('Full-text search error:', error);
      return [];
    }

    return (data || []) as ChunkMetadata[];
  }

  /**
   * Generate cache key from query parameters
   */
  private cacheKey(query: QueryContext, collection: CollectionType): string {
    const hash = require('crypto')
      .createHash('sha256')
      .update(`${query.query_text}:${collection}:${query.top_k}`)
      .digest('hex');
    return `rag:${hash}`;
  }

  /**
   * Get cached result from Redis
   */
  private async getCachedResult(
    key: string
  ): Promise<{ chunks: RankedChunk[]; collection: CollectionType; handoff_applied?: CollectionType } | null> {
    if (!this.redis) return null;
    try {
      const cached = await this.redis.get(key);
      return cached ? JSON.parse(cached) : null;
    } catch (e) {
      console.error('Redis get error:', e);
      return null;
    }
  }

  /**
   * Cache result in Redis (1-hour TTL)
   */
  private async cacheResult(
    key: string,
    result: { chunks: RankedChunk[]; collection: CollectionType; handoff_applied?: CollectionType }
  ): Promise<void> {
    if (!this.redis) return;
    try {
      await this.redis.setex(key, this.cacheTTLSeconds, JSON.stringify(result));
    } catch (e) {
      console.error('Redis set error:', e);
    }
  }
}

// ============================================================================
// 5. DATABASE SCHEMA (SQL MIGRATION)
// ============================================================================

/**
 * SQL migration to create rag_chunks table in Supabase
 * Run via: supabase db push
 */
export const RAG_SCHEMA_MIGRATION = `
-- =====================================================================
-- Manta Maestro v5.0 — RAG Hierarchy: rag_chunks table
-- Ticket: MNT-2026-RAG-HIERARCHY-V5
-- =====================================================================

CREATE TABLE IF NOT EXISTS rag_chunks (
  -- Identifiers
  chunk_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id       TEXT NOT NULL,
  source_collection TEXT NOT NULL CHECK (
    source_collection IN ('saneamento', 'energia', 'portos', 'barragens', 'editais')
  ),

  -- Content & Embeddings
  text              TEXT NOT NULL,
  embedding         vector(384),
  embedding_model   TEXT DEFAULT 'BAAI/bge-small-en-v1.5',

  -- Provenance
  source_document_title  TEXT NOT NULL,
  source_document_type   TEXT NOT NULL CHECK (
    source_document_type IN ('regulation', 'tender', 'edital', 'standard', 'guide', 'case_study')
  ),
  source_url        TEXT,
  source_organization TEXT,

  -- Domain Tags
  domain_tags       TEXT[] NOT NULL DEFAULT '{}',
  segment_codes     TEXT[] NOT NULL DEFAULT '{}',
  lifecycle_phases  SMALLINT[] NOT NULL DEFAULT ARRAY[1,2,3,4,5,6,7,8]::SMALLINT[],

  -- Recency & Freshness
  published_date    DATE,
  ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_updated_at   TIMESTAMPTZ,
  currency_status   TEXT NOT NULL DEFAULT 'current' CHECK (
    currency_status IN ('current', 'draft', 'superseded', 'historical')
  ),

  -- Reliability Signals
  confidence        NUMERIC(3,2) NOT NULL DEFAULT 0.5 CHECK (confidence BETWEEN 0 AND 1),
  citation_count    INTEGER NOT NULL DEFAULT 0 CHECK (citation_count >= 0),
  relevance_feedback_score NUMERIC(3,2) CHECK (
    relevance_feedback_score BETWEEN -1 AND 1
  ),

  -- Operational
  chunk_order       INTEGER,
  window_size       INTEGER,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_rag_chunks_collection ON rag_chunks (source_collection);
CREATE INDEX idx_rag_chunks_currency ON rag_chunks (currency_status);
CREATE INDEX idx_rag_chunks_domain_tags ON rag_chunks USING GIN (domain_tags);
CREATE INDEX idx_rag_chunks_segment_codes ON rag_chunks USING GIN (segment_codes);
CREATE INDEX idx_rag_chunks_source_org ON rag_chunks (source_organization);
CREATE INDEX idx_rag_chunks_embedding ON rag_chunks USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE embedding IS NOT NULL;
CREATE INDEX idx_rag_chunks_ingested_brin ON rag_chunks USING BRIN (ingested_at);

-- Full-text search
ALTER TABLE rag_chunks ADD COLUMN IF NOT EXISTS text_fts tsvector GENERATED ALWAYS AS (
  to_tsvector('portuguese', text)
) STORED;
CREATE INDEX idx_rag_chunks_text_fts ON rag_chunks USING GIN (text_fts);
`;

// ============================================================================
// 6. TEST QUERIES FOR S6-S10 DOMAINS
// ============================================================================

/**
 * Test suite: 15 realistic queries covering all 5 collections and S6-S10 domains
 */
export const TEST_QUERIES: QueryContext[] = [
  // S8 - Saneamento (SNIS)
  {
    query_text: 'ETA com adução de 500 km: qual é a norma NBR para dimensionamento de adutoras?',
    segment_code: 'S8',
    lifecycle_phase: 2, // Projeto básico
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'Lei 14.026: como estruturar concessão para prestador de saneamento integrado (água + esgoto)?',
    segment_code: 'S8',
    lifecycle_phase: 6, // Processo competitivo
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'BNDES edital saneamento 2024: quais são os prazos para submissão de projetos?',
    segment_code: 'S8',
    lifecycle_phase: 6, // Licitação
    top_k: 5,
    include_reasoning: true,
  },

  // S9 - Energia (ANEEL)
  {
    query_text: 'Licitação transmissão ANEEL: qual é o processo para autorização de linha de transmissão (LT) em 765 kV?',
    segment_code: 'S9',
    lifecycle_phase: 6, // Licitação
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'EPE Plano Decenal 2024: expansão prevista de geração renovável nos próximos 5 anos?',
    segment_code: 'S9',
    lifecycle_phase: 1, // Estudo prévio
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'ONS Procedimentos de Rede: qual é a distância mínima de afastamento de subestação em zona urbana?',
    segment_code: 'S9',
    lifecycle_phase: 3, // Projeto executivo
    top_k: 5,
    include_reasoning: true,
  },

  // S6 - Portos (ANTAQ)
  {
    query_text: 'ANTAQ regulação: quais são os critérios de capacidade de berço para terminal de contêineres?',
    segment_code: 'S6',
    lifecycle_phase: 2, // Projeto básico
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'BNDES porto: edital de concessão para dragagem de bacia portuária; prazos 2024?',
    segment_code: 'S6',
    lifecycle_phase: 6, // Licitação
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'PIANC Guidelines: qual é a profundidade mínima de calado para porta-contêineres Panamax?',
    segment_code: 'S6',
    lifecycle_phase: 2, // Projeto básico
    top_k: 5,
    include_reasoning: true,
  },

  // S10 - Barragens (ICOLD)
  {
    query_text: 'Lei 12.334 segurança barragens: quais são as exigências para barragem de rejeitos em zona urbana?',
    segment_code: 'S10',
    lifecycle_phase: 3, // Projeto executivo
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'ICOLD guidelines: qual é a altura máxima de barragem de concreto com drenagem interna?',
    segment_code: 'S10',
    lifecycle_phase: 2, // Projeto básico
    top_k: 5,
    include_reasoning: true,
  },
  {
    query_text: 'CBDB/PNSB: dados de inspeção de barragens existentes para reavaliação de segurança?',
    segment_code: 'S10',
    lifecycle_phase: 5, // Operação & manutenção
    top_k: 5,
    include_reasoning: true,
  },

  // Cross-collection: Editais
  {
    query_text: 'Licitação pública: template de cronograma para concessão de saneamento ou geração de energia?',
    segment_code: 'S8',
    lifecycle_phase: 6, // Licitação
    top_k: 6,
    include_reasoning: true,
  },
  {
    query_text: 'Portal Transparência / BNDES: qual é o status de editais abertos em portos/energia para 2024?',
    lifecycle_phase: 6,
    top_k: 6,
    include_reasoning: true,
  },

  // Cross-domain (S9 + S10): barragem hidrelétrica
  {
    query_text: 'Barragem de geração hidroelétrica: como integrar requisitos ICOLD (barragens) + EPE (energia)?',
    segment_code: 'S10',
    lifecycle_phase: 2, // Projeto básico
    top_k: 5,
    include_reasoning: true,
  },

  // Cross-domain (S8 + S6): porto com saneamento
  {
    query_text: 'Porto com terminais e sistema de tratamento de água: normas de saneamento + ANTAQ?',
    segment_code: 'S6',
    lifecycle_phase: 2,
    top_k: 5,
    include_reasoning: true,
  },
];

// ============================================================================
// 7. INTEGRATION EXAMPLE: AGENT S8 (Saneamento) HANDOFF FLOW
// ============================================================================

/**
 * Example: agente-saneamento querying RAG for edital timing
 *
 * Flow:
 * 1. User asks: "BNDES saneamento: quais são os prazos para licitar?"
 * 2. Agent calls RagQueryService.queryCollection('saneamento')
 * 3. ChunkScorer rates saneamento results; score = 0.62
 * 4. Collection has handoff_hint: "score < 0.6 AND contains('licitação')"
 * 5. Since score = 0.62, no handoff triggered
 * 6. Return top 5 chunks from saneamento
 *
 * Alternative: if score had been 0.45:
 * 5. Trigger handoff → also query 'editais' collection
 * 6. Merge top 3 editais chunks with saneamento results
 * 7. Return merged result with handoff_applied='editais'
 */
export async function exampleAgenteSaneamentoQuery() {
  // Initialize service
  const supabaseUrl = process.env.SUPABASE_URL || 'https://ogxxgvgtulrbbppshjie.supabase.co';
  const supabaseKey = process.env.SUPABASE_ANON_KEY || '';

  const ragService = new RagQueryService(supabaseUrl, supabaseKey);

  // User query
  const userQuery: QueryContext = {
    query_text: 'BNDES saneamento 2024: qual é o prazo para submissão? E se for AySA?',
    segment_code: 'S8',
    lifecycle_phase: 6,
    top_k: 5,
    include_reasoning: true,
  };

  console.log('>> agente-saneamento query:');
  console.log('   User question:', userQuery.query_text);
  console.log('   Segment:', userQuery.segment_code);

  // Query saneamento collection with handoff
  const result = await ragService.queryCollection(userQuery, 'saneamento', true);

  console.log('\n>> RAG Results:');
  console.log(`   Collection: ${result.collection}`);
  console.log(`   Chunks found: ${result.chunks.length}`);
  if (result.handoff_applied) {
    console.log(`   Handoff applied: YES → ${result.handoff_applied}`);
  }
  console.log(`   Cache hit: ${result.cache_hit}`);

  for (const chunk of result.chunks.slice(0, 3)) {
    console.log(`\n   [Rank ${chunk.rank}] Score: ${(chunk.final_score * 100).toFixed(1)}%`);
    console.log(`   Title: ${chunk.chunk.source_document_title}`);
    console.log(`   Source: ${chunk.chunk.source_organization}`);
    console.log(`   Reasoning: ${chunk.reasoning}`);
    console.log(`   Tags: ${chunk.chunk.domain_tags.join(', ')}`);
  }
}

// ============================================================================
// 8. TYPE EXPORTS FOR CLIENT USAGE
// ============================================================================

export default {
  ChunkScorer,
  RagQueryService,
  COLLECTION_REGISTRY,
  TEST_QUERIES,
  RAG_SCHEMA_MIGRATION,
};
