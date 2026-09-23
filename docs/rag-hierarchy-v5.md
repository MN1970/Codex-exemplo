# Manta Maestro v5.0 — RAG Hierarchy & Relevance Ranking

**Ticket:** MNT-2026-RAG-HIERARCHY-V5  
**Status:** DRAFT (requires gate before production deploy)  
**Version:** 5.0  
**Last Updated:** 2026-08-02

---

## Overview

The RAG (Retrieval-Augmented Generation) Hierarchy for Manta Maestro v5.0 implements a **5-collection knowledge base** supporting the new vertical agents (S6–S10: Portos, Aeroportos, Saneamento, Energia, Barragens) plus a cross-segmento Editais (tender templates & public bids).

**Key Features:**
- **Multi-factor relevance ranking:** BM25 (lexical) + semantic similarity (pgvector) + confidence boost + freshness
- **Collection registry** with handoff hints for cross-domain queries
- **Supabase pgvector** backend (BAAI/bge-small-en-v1.5, 384 dimensions)
- **Redis caching** (1-hour TTL) for frequently queried documents
- **Metadata schema** capturing provenance, domain tags, confidence, and recency
- **Test queries** covering all 5 collections & lifecycle phases 1-8

---

## Architecture

### 1. Five RAG Collections

| Collection | Segment | Primary Agent | Sources | Prefix |
|------------|---------|---------------|---------|--------|
| **saneamento** | S8 | agente-saneamento | SNIS, NBR 12211-12218, Lei 14.026, BNDES AySA | `san:` |
| **energia** | S9 | agente-energia | ANEEL editais, EPE (R1-R5), ONS, IEEE | `ene:` |
| **portos** | S6 | agente-portos | ANTAQ, PIANC, BNDES, dragagem | `por:` |
| **barragens** | S10 | agente-barragens | ICOLD, CBDB, Lei 12.334, PNSB, TSF | `bar:` |
| **editais** | S6–S10 | manta-05 (orcamento) | BNDES, Portal Transparência, ANTAQ, ANP | `edit:` |

Each collection is independently queryable but may reference others via **handoff hints** (see section 4).

### 2. Metadata Schema (ChunkMetadata)

Every chunk stored in `rag_chunks` table includes:

#### Identifiers
- `chunk_id` (UUID): Unique identifier
- `document_id` (TEXT): Source document reference
- `source_collection` (ENUM): One of 5 collections

#### Content & Embeddings
- `text` (TEXT): Raw chunk content (typically 200–500 tokens)
- `embedding` (vector(384)): BAAI/bge-small-en-v1.5 semantic embedding
- `embedding_model` (TEXT): Model used (default: BAAI/bge-small-en-v1.5)

#### Provenance
- `source_document_title` (TEXT): Document name
- `source_document_type` (ENUM): regulation | tender | edital | standard | guide | case_study
- `source_url` (TEXT): PDF link, SharePoint path, etc.
- `source_organization` (TEXT): SNIS, ANEEL, ANTAQ, ICOLD, BNDES, etc.

#### Domain Tagging
- `domain_tags` (TEXT[]): Keywords for topic filtering (e.g., `['adução', 'dimensionamento', 'NBR-12211']`)
- `segment_codes` (TEXT[]): Infrastructure segments (S6, S7, S8, S9, S10)
- `lifecycle_phases` (SMALLINT[]): Project phases 1–8 where chunk applies

#### Recency & Freshness
- `published_date` (DATE): Original publication date
- `ingested_at` (TIMESTAMPTZ): When added to RAG
- `last_updated_at` (TIMESTAMPTZ): When chunk last refreshed
- `currency_status` (ENUM): current | draft | superseded | historical

#### Reliability Signals
- `confidence` (NUMERIC 0–1): Model confidence in chunk quality (default 0.5)
- `citation_count` (INTEGER): How many internal docs reference this chunk
- `relevance_feedback_score` (NUMERIC –1–1): Bayesian feedback from user ratings

#### Operational
- `chunk_order` (INTEGER): Position in original document
- `window_size` (INTEGER): Context window size used during chunking

---

## Relevance Ranking Algorithm

### Overview: Four Scoring Factors

The final score combines:
1. **BM25** (lexical matching, Okapi algorithm)
2. **Semantic similarity** (cosine distance on embeddings)
3. **Confidence boost** (source reliability signals)
4. **Freshness** (recency decay)

**Formula:**
```
final_score = (
  BM25 × w_bm25 +
  semantic × w_semantic +
  confidence_boost × w_confidence +
  freshness × w_freshness
) × (1 + feedback × 0.1)
```

where `w_bm25 + w_semantic + w_confidence + w_freshness = 1.0`

### 1. BM25 Score (Lexical)

**Algorithm:** Okapi BM25 (industry standard for keyword relevance)

**Parameters:**
- `k1 = 1.4–1.8` (term saturation; higher = more weight to term frequency)
- `b = 0.65–0.80` (length normalization; 0 = no normalization, 1 = full)

**Per Collection** (tuned for domain characteristics):
- `saneamento`: k1=1.5, b=0.75 (balanced)
- `energia`: k1=1.5, b=0.75 (balanced)
- `portos`: k1=1.6, b=0.70 (slightly favor rare terms)
- `barragens`: k1=1.4, b=0.80 (slightly favor longer docs)
- `editais`: k1=1.8, b=0.65 (aggressively favor keywords like "prazos", "licitação")

**Example:** Query "adução 100 km" on saneamento chunk:
- BM25 score = 0.72 (both "adução" and "100" are high-weight terms in NBR context)

### 2. Semantic Similarity (Vector)

**Algorithm:** Cosine similarity on 384-dimensional embeddings

**Pipeline:**
1. Query text embedded via BAAI/bge-small-en-v1.5
2. Cosine similarity computed: `cos(query_embedding, chunk_embedding)`
3. Normalized from [–1, 1] → [0, 1]: `(cosine + 1) / 2`

**Per Collection (default):**
- `saneamento`: 0.45 weight (semantic slightly favored)
- `energia`: 0.47 weight (semantic dominant)
- `portos`: 0.50 weight (semantic dominant for multi-modal content)
- `barragens`: 0.44 weight (balanced)
- `editais`: 0.40 weight (lexical more important for dates & tender names)

**Example:** Query "barragem hidroelétrica" on ICOLD chunk about concrete dams:
- Cosine = 0.82 → normalized = 0.91 (semantic match strong)

### 3. Confidence Boost

**Factors:**
- Chunk's own `confidence` (0–1): model-assigned quality (default 0.5)
- `citation_count`: how many docs cite this chunk (proxy for importance)
- `currency_status`: is it current, draft, superseded, or historical?

**Formula:**
```
confidence_boost = (
  confidence × 0.5 +
  min(citation_count / 10, 1.0) × 0.3 +
  currency_factor × 0.2
)
```

where `currency_factor = 1.0` (current) | 0.7 (draft) | 0.3 (superseded) | 0.5 (historical)

**Example:** ABNT NBR standard (confidence=0.95, citations=12, current):
```
boost = 0.95 × 0.5 + min(12/10, 1.0) × 0.3 + 1.0 × 0.2 = 0.475 + 0.30 + 0.20 = 0.975
```

### 4. Freshness Score

**Decay function:** Prefer recently ingested chunks, but plateau after ~90 days

| Age Range | Score |
|-----------|-------|
| ≤ 7 days | 1.0 |
| 8–30 days | 0.9 |
| 31–90 days | 0.7 |
| > 90 days | 0.4 |

**Example:** Chunk ingested 3 days ago:
```
freshness = 1.0 (recent)
```

Chunk ingested 150 days ago (still useful, but older):
```
freshness = 0.4
```

---

## Collection Registry & Handoff Hints

### Handoff Logic

When a query returns low-confidence results from primary collection, the system checks **handoff hints** to identify complementary collections.

**Trigger Conditions:**
- `score < 0.5`: Primary collection score below threshold
- `score < 0.6 AND contains("keyword")`: Conditional, keyword-based trigger
- `no_results`: No chunks found in primary collection

**Example:** Query "BNDES saneamento: prazos para licititar?"
1. Query `saneamento` collection → top result score = 0.48 (below 0.5)
2. Check handoff hints in saneamento registry
3. Find: `target=editais, trigger="score < 0.6 AND contains('licitação')"`
4. Condition met → also query `editais` collection
5. Top 3 editais chunks (score ≥ 0.6) merged with saneamento results
6. Return consolidated result with `handoff_applied='editais'`

### Handoff Matrix

```
saneamento
├─ → editais (score < 0.6 AND contains("licitação"))
│   └─ "SNIS may not cover tender timing; check editais for recent public bids"
└─ → energia (contains("subestação") OR contains("energia"))
    └─ "Cross-domain: saneamento projects may have power requirements"

energia
├─ → editais (score < 0.6 AND contains("leilão"))
│   └─ "ANEEL may reference recent transmission tenders; editais has timing data"
└─ → barragens (contains("hidrelétrica") OR contains("usina"))
    └─ "Energy generation may interact with hydroelectric facilities"

portos
├─ → editais (score < 0.5 AND contains("concessão"))
│   └─ "Port concessions often tracked in editais; check for tender schedules"
└─ → energia (contains("energia") OR contains("geração"))
    └─ "Ports may have renewable energy generation (offshore wind, solar)"

barragens
├─ → saneamento (contains("água") AND contains("captação"))
│   └─ "Dams may serve water supply; cross-check with saneamento for integration"
└─ → energia (contains("hidrelétrica") OR contains("geração"))
    └─ "Hydroelectric dams are energy infrastructure; check energia for grid data"

editais
├─ → saneamento (found_match AND contains("AySA"))
│   └─ "BNDES saneamento editais often co-reference; load additional context"
└─ → energia (found_match AND contains("EPE"))
    └─ "Energy tenders often multi-phase; check EPE docs for full scope"
```

---

## Supabase Integration

### Schema: rag_chunks Table

```sql
CREATE TABLE rag_chunks (
  chunk_id              UUID PRIMARY KEY,
  document_id           TEXT NOT NULL,
  source_collection     TEXT NOT NULL,  -- enum: saneamento|energia|portos|barragens|editais
  
  text                  TEXT NOT NULL,
  embedding             vector(384),
  embedding_model       TEXT,
  
  source_document_title TEXT NOT NULL,
  source_document_type  TEXT,           -- enum: regulation|tender|edital|...
  source_url            TEXT,
  source_organization   TEXT,
  
  domain_tags           TEXT[],
  segment_codes         TEXT[],
  lifecycle_phases      SMALLINT[],
  
  published_date        DATE,
  ingested_at           TIMESTAMPTZ,
  currency_status       TEXT,           -- enum: current|draft|superseded|historical
  
  confidence            NUMERIC(3,2),
  citation_count        INTEGER,
  relevance_feedback_score NUMERIC(3,2),
  
  chunk_order           INTEGER,
  window_size           INTEGER,
  
  created_at            TIMESTAMPTZ,
  updated_at            TIMESTAMPTZ
);
```

### Indexes (HNSW + BRIN + GIN)

| Index | Type | Purpose |
|-------|------|---------|
| `idx_rag_chunks_collection` | BTree | Filter by collection |
| `idx_rag_chunks_currency` | BTree | Filter current vs. superseded |
| `idx_rag_chunks_embedding` | HNSW | k-NN vector search (cosine) |
| `idx_rag_chunks_domain_tags` | GIN | Multi-valued tag search |
| `idx_rag_chunks_segment_codes` | GIN | Multi-valued segment search |
| `idx_rag_chunks_ingested_brin` | BRIN | Recency filtering (append-only) |
| `idx_rag_chunks_text_fts` | GIN | Full-text search (Portuguese) |

---

## Redis Caching Layer

### TTL & Key Strategy

**TTL:** 1 hour (3600 seconds)

**Cache Key Format:**
```
rag:{sha256(query_text + collection + top_k)}
```

**Cached Data:**
```json
{
  "chunks": [
    {
      "chunk": { ... },
      "scores": { "bm25": 0.72, "semantic": 0.85, ... },
      "final_score": 0.78,
      "rank": 1
    },
    ...
  ],
  "collection": "saneamento",
  "handoff_applied": "editais",
  "cache_hit": false
}
```

**Cache Invalidation:**
- Automatic: 1-hour TTL
- Manual: When chunks updated (trigger on `rag_chunks` UPDATE)
- Explicit: API endpoint to clear cache by query/collection

**Example Flow:**
```
1. User query: "NBR adução 100 km"
2. Cache miss → query Supabase + rank → 280ms
3. Result cached for 1 hour
4. Same query within 1 hour → Redis hit → 5ms
5. After 1 hour, re-fetch from Supabase (cache expired)
```

---

## API Usage Guide

### Basic Query (Single Collection)

```typescript
import { RagQueryService, QueryContext } from './src/rag-hierarchy';

const service = new RagQueryService(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY,
  redisClient // optional
);

const query: QueryContext = {
  query_text: "NBR dimensionamento adução 100 km",
  segment_code: 'S8',
  lifecycle_phase: 2,
  top_k: 5,
  include_reasoning: true
};

const result = await service.queryCollection(query, 'saneamento');

// result.chunks: [RankedChunk[], ...]
// result.handoff_applied: 'editais' | undefined
// result.cache_hit: boolean
```

### Multi-Collection Query

```typescript
const result = await service.queryMultiCollection(
  query,
  ['saneamento', 'editais'] // search multiple collections
);

// result.all_chunks: merged & re-ranked across collections
// result.by_collection: results per collection
```

### Query with Embedding

For best results, provide a pre-computed query embedding:

```typescript
const query: QueryContext = {
  query_text: "ETA com adução",
  query_embedding: embeddingModel.embed("ETA com adução"), // 384-dim vector
  segment_code: 'S8',
  top_k: 5,
  include_reasoning: true
};

const result = await service.queryCollection(query, 'saneamento');
```

### Handling Results

```typescript
for (const chunk of result.chunks) {
  console.log(`[Rank ${chunk.rank}] Score: ${(chunk.final_score * 100).toFixed(1)}%`);
  console.log(`  Title: ${chunk.chunk.source_document_title}`);
  console.log(`  Source: ${chunk.chunk.source_organization}`);
  console.log(`  Reasoning: ${chunk.reasoning}`);
  console.log(`  Tags: ${chunk.chunk.domain_tags.join(', ')}`);
}
```

---

## Integration with Agents

### Example: agente-saneamento S8

```typescript
// In agente-saneamento/index.ts

import { RagQueryService } from '../src/rag-hierarchy';

const ragService = new RagQueryService(supabaseUrl, supabaseKey, redis);

async function answerUser(userQuery: string) {
  // 1. Parse user intent (via LLM or keyword matching)
  const intent = parseIntent(userQuery);
  
  // 2. Determine lifecycle phase if available
  const lifecyclePhase = intent.lifecycle_phase || 2;
  
  // 3. Query RAG with handoff enabled
  const ragResult = await ragService.queryCollection(
    {
      query_text: userQuery,
      segment_code: 'S8',
      lifecycle_phase: lifecyclePhase,
      top_k: 5,
      include_reasoning: true
    },
    'saneamento',
    true // enable handoff
  );
  
  // 4. Format results for LLM context
  const context = ragResult.chunks
    .map(c => `[${c.chunk.source_organization}] ${c.chunk.text}`)
    .join('\n\n');
  
  // 5. If handoff applied, note in response
  if (ragResult.handoff_applied) {
    console.log(`Note: Also checked ${ragResult.handoff_applied} collection`);
  }
  
  // 6. Pass context to agent's Claude model
  return await claude.messages.create({
    model: 'claude-opus-4',
    system: `You are agente-saneamento. Use the following reference documents:\n${context}`,
    messages: [{ role: 'user', content: userQuery }]
  });
}
```

### Example: Routing from Maestro (Manta 00)

```typescript
// In manta-maestro-router (Maestro)

async function routeQuery(userQuery: string) {
  // 1. Semantic routing via agent embeddings
  const topCandidates = await maestro.findCandidateAgents(userQuery, top_k=3);
  
  // 2. For infrastructure segments (S6–S10), also check RAG collection match
  const ragMatch = await inferCollectionFromQuery(userQuery);
  if (ragMatch) {
    // Query RAG to validate routing
    const ragResult = await ragService.queryMultiCollection(
      { query_text: userQuery, top_k: 1, include_reasoning: false },
      [ragMatch.collection] // test this collection
    );
    
    if (ragResult.all_chunks[0]?.final_score > 0.6) {
      // High confidence in this collection → route to corresponding agent
      return routeToAgent(ragMatch.agent_id);
    }
  }
  
  // 3. Fall back to standard semantic routing
  return routeToAgent(topCandidates[0].agent_id);
}
```

---

## Test Queries (15 Examples)

### S8 — Saneamento (3 queries)

1. **Basic design question (Projeto Básico, Phase 2)**
   ```
   "ETA com adução de 500 km: qual é a norma NBR para dimensionamento de adutoras?"
   ```
   Expected: NBR 12211-12218 chunks with sizing formulas

2. **Regulatory structure (Licitação, Phase 6)**
   ```
   "Lei 14.026: como estruturar concessão para prestador de saneamento integrado (água + esgoto)?"
   ```
   Expected: Lei 14.026 text + concession structure templates

3. **Tender timing (Licitação, Phase 6)**
   ```
   "BNDES edital saneamento 2024: quais são os prazos para submissão de projetos?"
   ```
   Expected: BNDES edital + handoff to editais for timeline

### S9 — Energia (3 queries)

4. **Transmission authorization (Licitação, Phase 6)**
   ```
   "Licitação transmissão ANEEL: qual é o processo para autorização de linha de transmissão (LT) em 765 kV?"
   ```
   Expected: ANEEL regulatory process + EPE reference

5. **Planning (Estudo Prévio, Phase 1)**
   ```
   "EPE Plano Decenal 2024: expansão prevista de geração renovável nos próximos 5 anos?"
   ```
   Expected: EPE 10-year plan + renewable targets

6. **Grid procedures (Projeto Executivo, Phase 3)**
   ```
   "ONS Procedimentos de Rede: qual é a distância mínima de afastamento de subestação em zona urbana?"
   ```
   Expected: ONS grid codes + urban setback distances

### S6 — Portos (3 queries)

7. **Capacity design (Projeto Básico, Phase 2)**
   ```
   "ANTAQ regulação: quais são os critérios de capacidade de berço para terminal de contêineres?"
   ```
   Expected: ANTAQ capacity formulas + berth sizing

8. **Dredging tender (Licitação, Phase 6)**
   ```
   "BNDES porto: edital de concessão para dragagem de bacia portuária; prazos 2024?"
   ```
   Expected: BNDES edital + dredging specs + handoff to editais

9. **International standards (Projeto Básico, Phase 2)**
   ```
   "PIANC Guidelines: qual é a profundidade mínima de calado para porta-contêineres Panamax?"
   ```
   Expected: PIANC guidelines + Panamax drafts

### S10 — Barragens (3 queries)

10. **Tailings dam (Projeto Executivo, Phase 3)**
    ```
    "Lei 12.334 segurança barragens: quais são as exigências para barragem de rejeitos em zona urbana?"
    ```
    Expected: Lei 12.334 + tailings dam safety requirements

11. **Concrete height (Projeto Básico, Phase 2)**
    ```
    "ICOLD guidelines: qual é a altura máxima de barragem de concreto com drenagem interna?"
    ```
    Expected: ICOLD design tables + height limits

12. **Inspection data (Operação, Phase 5)**
    ```
    "CBDB/PNSB: dados de inspeção de barragens existentes para reavaliação de segurança?"
    ```
    Expected: PNSB inspection database + risk assessment

### Cross-Collection (3 queries)

13. **Tender templates (Licitação, Phase 6)**
    ```
    "Licitação pública: template de cronograma para concessão de saneamento ou geração de energia?"
    ```
    Expected: editais templates + segment-specific timelines

14. **Portfolio view (Licitação, Phase 6)**
    ```
    "Portal Transparência / BNDES: qual é o status de editais abertos em portos/energia para 2024?"
    ```
    Expected: editais cross-collection summary

15. **Hydroelectric integration (Projeto Básico, Phase 2)**
    ```
    "Barragem de geração hidroelétrica: como integrar requisitos ICOLD (barragens) + EPE (energia)?"
    ```
    Expected: barragens + energia handoff + integration checklist

---

## Deployment Checklist

- [ ] Create `rag_chunks` table via migration: `supabase db push`
- [ ] Verify pgvector + BRIN indexes created successfully
- [ ] Run test queries to validate scoring algorithm
- [ ] Seed initial chunks from source documents (SNIS, ANEEL, etc.)
- [ ] Configure Redis connection (TTL = 3600s)
- [ ] Add rag-hierarchy.ts to agent runtimes (skills, Claude SDK)
- [ ] Test handoff logic with low-score scenarios
- [ ] Validate S6–S10 agent integration (agente-saneamento, agente-energia, etc.)
- [ ] Performance testing: query latency p99 < 500ms (cached) / < 1s (uncached)
- [ ] Gate human review: MN approval before merge to main
- [ ] Post-deploy monitoring: cache hit rate, query distribution, feedback scores

---

## Monitoring & Observability

### Key Metrics

| Metric | Target | Query |
|--------|--------|-------|
| Query latency (cached) | < 100ms | SELECT p99_latency_ms FROM rag_query_metrics WHERE cache_hit=true |
| Query latency (uncached) | < 1000ms | SELECT p99_latency_ms FROM rag_query_metrics WHERE cache_hit=false |
| Cache hit rate | > 60% | SELECT COUNT(*) FILTER (WHERE cache_hit) / COUNT(*) FROM rag_query_metrics |
| Handoff rate | 10–20% | SELECT COUNT(*) FILTER (WHERE handoff_applied IS NOT NULL) / COUNT(*) FROM rag_query_metrics |
| Avg final score | 0.65–0.75 | SELECT AVG(final_score) FROM rag_query_metrics |
| Feedback score movement | ±0.05/day | SELECT AVG(relevance_feedback_score) FROM rag_chunks GROUP BY DATE(updated_at) |

### Dashboard Queries

```sql
-- Cache effectiveness
SELECT
  COUNT(*) FILTER (WHERE cache_hit) as cached,
  COUNT(*) FILTER (WHERE NOT cache_hit) as uncached,
  ROUND(100.0 * COUNT(*) FILTER (WHERE cache_hit) / COUNT(*), 1) as hit_rate_pct
FROM rag_query_metrics
WHERE created_at > now() - INTERVAL '1 day';

-- Top queried collections
SELECT
  collection,
  COUNT(*) as query_count,
  ROUND(AVG(final_score), 3) as avg_score,
  ROUND(100.0 * COUNT(*) FILTER (WHERE handoff_applied IS NOT NULL) / COUNT(*), 1) as handoff_pct
FROM rag_query_metrics
WHERE created_at > now() - INTERVAL '7 days'
GROUP BY collection
ORDER BY query_count DESC;

-- Top documents by citation
SELECT
  chunk.source_organization,
  chunk.source_document_title,
  SUM(chunk.citation_count) as total_citations,
  COUNT(DISTINCT chunk.chunk_id) as num_chunks,
  ROUND(AVG(chunk.confidence), 3) as avg_confidence
FROM rag_chunks chunk
WHERE chunk.currency_status = 'current'
GROUP BY 1, 2
ORDER BY total_citations DESC
LIMIT 20;
```

---

## Future Enhancements

1. **Multi-language support:** Extend embeddings & BM25 to Portuguese + Spanish + English
2. **Document hierarchy:** Track chunk-to-document-to-collection lineage for citation tracking
3. **Feedback loop integration:** Bayesian updates to scoring weights based on agent feedback
4. **Reranking with cross-encoder:** Second-stage reranking for top-K (more expensive but higher precision)
5. **Knowledge graph:** Link chunks via entity recognition (e.g., "Lei 14.026" → shared across S8 chunks)
6. **A/B testing:** Test different weight configurations (BM25 vs. semantic emphasis)
7. **Semantic clustering:** Group chunks by topic for related-document recommendations
8. **Citation network:** Visualize how documents reference each other

---

## References

- **Manta Maestro CLAUDE.md:** Agent registry & routing rules
- **Supabase pgvector:** https://supabase.com/docs/guides/ai/vector
- **BM25 Algorithm:** Okapi BM25 (Robertson et al., 2009)
- **BAAI/bge-small-en-v1.5:** BGE embedding model, 384 dimensions
- **HNSW Index:** Approximate nearest neighbor search (Malkov & Yashunin, 2018)
- **Redis Caching:** Distributed in-memory data store, 1-hour TTL

---

## Support & Questions

**Issues / Enhancements:** Ticket MNT-2026-RAG-HIERARCHY-V5 on Jira  
**Code Review Gate:** Approval required from MN before merge  
**Integration Help:** Contact agente-infraestrutura team or architect (manta-15-arq)
