# RAG Hierarchy v5.0 — Integration Examples

This document provides real-world examples of how to integrate the RAG hierarchy into Manta Maestro agents (S6–S10).

---

## Example 1: agente-saneamento (S8) — Answering User Questions

### Scenario
User asks: *"Estamos estruturando uma concessão de saneamento integrado com AySA. Qual é o framework da Lei 14.026 e quais são os prazos do BNDES 2024?"*

### Agent Flow

```typescript
import { RagQueryService, QueryContext } from '../src/rag-hierarchy';
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();
const ragService = new RagQueryService(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY,
  redisClient
);

async function agenteSaneamentoHandler(userQuery: string, userEmail?: string) {
  console.log(`[agente-saneamento] Query: ${userQuery}`);

  // Step 1: Determine project phase from context or user input
  // In real scenario, this comes from Q2 intake form or conversation history
  const lifecyclePhase = 6; // Phase 6 = Processo competitivo / Licitação

  // Step 2: Build RAG query context
  const ragQuery: QueryContext = {
    query_text: userQuery,
    segment_code: 'S8',
    lifecycle_phase: lifecyclePhase,
    user_email: userEmail,
    top_k: 6, // Get 6 for potential handoff
    include_reasoning: true,
  };

  // Step 3: Query RAG with handoff enabled (saneamento → editais for timing)
  const ragResult = await ragService.queryCollection(
    ragQuery,
    'saneamento',
    true // enableHandoff
  );

  console.log(`[RAG] Found ${ragResult.chunks.length} chunks`);
  if (ragResult.handoff_applied) {
    console.log(`[RAG] Handoff applied: ${ragResult.handoff_applied}`);
  }
  console.log(`[RAG] Cache hit: ${ragResult.cache_hit}`);

  // Step 4: Format chunks for Claude context
  const ragContext = ragResult.chunks
    .slice(0, 5) // Top 5 for context window efficiency
    .map(
      (chunk, idx) =>
        `**Document ${idx + 1}** (Score: ${(chunk.final_score * 100).toFixed(0)}%)
Title: ${chunk.chunk.source_document_title}
Source: ${chunk.chunk.source_organization}
Tags: ${chunk.chunk.domain_tags.join(', ')}

${chunk.chunk.text}

---`
    )
    .join('\n\n');

  // Step 5: Call Claude with RAG context
  const response = await client.messages.create({
    model: 'claude-opus-4',
    max_tokens: 2048,
    system: `You are agente-saneamento, an expert in sanitation infrastructure (S8).
    
Your expertise covers:
- Lei 14.026 (regulatory framework)
- NBR standards (12211-12218)
- BNDES financing programs
- AySA cooperation structures (Argentina)
- Water treatment plant (ETA) & sewage plant (ETE) design

You have access to the following reference documents. Use them to provide
accurate, cite-able answers. Always cite the source document name when
referencing specific rules, timelines, or technical requirements.

---

## REFERENCE DOCUMENTS

${ragContext}

---

Answer the user's question based on these documents. If a document provides
a specific answer, cite it explicitly (e.g., "According to Lei 14.026, ...").
If the documents don't fully address the question, acknowledge the gap and
provide general industry guidance.`,
    messages: [
      {
        role: 'user',
        content: userQuery,
      },
    ],
  });

  const agentResponse = response.content[0].type === 'text' ? response.content[0].text : '';

  // Step 6: Log query metrics for observability
  await logRagMetrics({
    user_email: userEmail,
    query_text: userQuery,
    segment_code: 'S8',
    collection: 'saneamento',
    handoff_applied: ragResult.handoff_applied,
    top_score: ragResult.chunks[0]?.final_score || 0,
    chunks_returned: ragResult.chunks.length,
    cache_hit: ragResult.cache_hit,
    agent_response_length: agentResponse.length,
  });

  return agentResponse;
}

// Output Example:
/*
[agente-saneamento] Query: Estamos estruturando uma concessão de saneamento...
[RAG] Found 5 chunks
[RAG] Handoff applied: editais
[RAG] Cache hit: false

**Document 1** (Score: 94%)
Title: Lei 14.026 — Marco Regulatório do Saneamento
Source: Governo Federal
Tags: lei, regulacao, saneamento, concessao

Lei 14.026/2020 estabelece o novo marco regulatório do saneamento brasileiro...
[Lei 14.026 full text excerpt]

---

**Document 2** (Score: 88%)
Title: BNDES Seleção Pública: Saneamento Integrado 2024
Source: BNDES
Tags: licitacao, saneamento, prazos, edital

BNDES 2024 para saneamento integrado: período de submissão até 30-jun-2024...
[BNDES edital excerpt]

---

Response from Claude:

Para estruturar uma concessão de saneamento integrado com AySA, você deve 
seguir o marco da Lei 14.026, que estabelece os seguintes pontos-chave:

1. **Estrutura Regulatória (Lei 14.026)**
   - Define as competências de prestação de serviços de água e esgoto
   - Permite concessões integradas (água + esgoto em um único contrato)
   - Requer aprovação de entidades estaduais/municipais

2. **Processo de Licitação**
   Conforme o edital BNDES 2024:
   - Submissão: até 30 de junho de 2024
   - Avaliação: 120 dias
   - Anúncio de vencedor: 60 dias após avaliação
   - Ciclo total: ~360 dias até primeiro desembolso

3. **Estrutura AySA**
   [Additional context on AySA cooperation structure]

...
*/
```

---

## Example 2: Cross-Domain Query — Hydroelectric Integration (S10 + S9)

### Scenario
User asks: *"Estamos avaliando uma barragem de geração hidroelétrica. Como integrar os requisitos ICOLD para segurança com o plano EPE?"*

### Agent Flow (agente-barragens with energia handoff)

```typescript
async function agentesBarragensHandler(userQuery: string) {
  const ragQuery: QueryContext = {
    query_text: userQuery,
    segment_code: 'S10',
    lifecycle_phase: 2, // Projeto básico
    top_k: 6,
    include_reasoning: true,
  };

  // Query primary collection (barragens)
  const barragenResult = await ragService.queryCollection(
    ragQuery,
    'barragens',
    true // enableHandoff
  );

  // Since query mentions "geração hidroelétrica", handoff to energia should trigger
  // Trigger: barragens.handoff_hints includes:
  //   target='energia', condition='contains("hidrelétrica")'

  if (barragenResult.handoff_applied === 'energia') {
    console.log('[Handoff] Barragens → Energia (hydroelectric generation)');
  }

  // Combine top chunks from both collections for comprehensive answer
  const combinedChunks = [
    ...barragenResult.chunks.slice(0, 3), // Top 3 from barragens
    // Chunks from energia are already merged by handoff logic
  ];

  const ragContext = combinedChunks
    .map((chunk) => `
**${chunk.chunk.source_organization}** - ${chunk.chunk.source_document_title}
Rank: ${chunk.rank} | Score: ${(chunk.final_score * 100).toFixed(0)}%
Domain: ${chunk.chunk.domain_tags.join(', ')}

${chunk.chunk.text}`)
    .join('\n\n---\n\n');

  const response = await client.messages.create({
    model: 'claude-opus-4',
    max_tokens: 3000,
    system: `You are agente-barragens, expert in dam engineering and safety.
    
This query involves hydroelectric generation (a cross-domain topic).
You have been provided with documents from both:
- barragens collection: ICOLD standards, Lei 12.334, CBDB
- energia collection: EPE planning, ONS grid procedures

Synthesize both perspectives to provide an integrated answer addressing:
1. ICOLD safety requirements for the dam
2. EPE integration requirements for grid generation
3. How these two frameworks complement each other

Reference Documents:
${ragContext}`,
    messages: [{ role: 'user', content: userQuery }],
  });

  return response.content[0].type === 'text' ? response.content[0].text : '';
}

// Output Example:
/*
[Handoff] Barragens → Energia (hydroelectric generation)

ICOLD Safety Framework:
- Dam height: up to 260m with adequate internal drainage
- Safety factor: 1.5 static, 1.2 seismic
- Spillway design flood: 500-year + safety margin

EPE Integration:
- Grid connection timeline: 3-5 years post-authorization
- Capacity planning: Must align with EPE 10-year plan
- ONS grid code compliance for generation units

Integration Checklist:
1. ICOLD → structural safety (your responsibility)
2. ONS Procedures → grid interconnection
3. EPE Plano Decenal → capacity planning alignment
*/
```

---

## Example 3: Maestro Router — Segment Inference & RAG Validation

### Scenario
Maestro (Manta 00) receives ambiguous query: *"How do we design the infrastructure for a sludge drying unit?"*

### Router Logic

```typescript
async function maestroRouteWithRagValidation(userQuery: string) {
  console.log('[Maestro] Routing ambiguous query:', userQuery);

  // Step 1: Semantic routing candidate (returns top-3 agents by embedding similarity)
  const semanticCandidates = await maestro.findCandidateAgents(userQuery, top_k: 3);
  // Result: [agente-saneamento (0.87), agente-infraestrutura (0.72), manta-06 (0.65)]

  // Step 2: RAG-based validation (check which collection has high-confidence matches)
  const ragValidation = await inferCollectionFromQuery(userQuery);
  
  async function inferCollectionFromQuery(query: string): Promise<{
    collection: CollectionType;
    agent_id: string;
    confidence: number;
  } | null> {
    // Query all relevant collections with low top_k
    const collections: CollectionType[] = ['saneamento', 'barragens'];
    const results = await ragService.queryMultiCollection(
      { query_text: query, top_k: 1, include_reasoning: false },
      collections
    );

    // Find highest-scoring collection
    const best = results.all_chunks[0];
    if (best && best.final_score > 0.65) {
      const collectionMeta = COLLECTION_REGISTRY[best.chunk.source_collection];
      return {
        collection: best.chunk.source_collection,
        agent_id: collectionMeta.agent_id,
        confidence: best.final_score,
      };
    }
    return null;
  }

  const ragMatch = await inferCollectionFromQuery(userQuery);

  // Step 3: Decision logic
  if (ragMatch && ragMatch.confidence > 0.70) {
    // RAG has high confidence → use RAG-inferred agent
    console.log(
      `[Maestro] RAG validation strong (${(ragMatch.confidence * 100).toFixed(0)}%) → ` +
        `route to ${ragMatch.agent_id} (saneamento)`
    );
    return { agent_id: ragMatch.agent_id, confidence: ragMatch.confidence };
  } else if (semanticCandidates[0].score > 0.85) {
    // Semantic routing confident → use top semantic candidate
    console.log(
      `[Maestro] Semantic routing confident (${(semanticCandidates[0].score * 100).toFixed(0)}%) → ` +
        `route to ${semanticCandidates[0].agent_id}`
    );
    return { agent_id: semanticCandidates[0].agent_id, confidence: semanticCandidates[0].score };
  } else {
    // Low confidence → escalate to agente-advisory or ask for clarification
    console.log('[Maestro] Low confidence (RAG < 0.7, semantic < 0.85) → escalate to advisory');
    return { agent_id: 'manta-15', confidence: 0.5 };
  }
}
```

---

## Example 4: Feedback Loop — Learning from User Ratings

### Scenario
After agent answers a question, user rates the answer. This feedback updates chunk relevance scores.

```typescript
async function recordUserFeedback(
  chunkId: string,
  feedback: 'correct' | 'wrong' | 'slow' | 'incomplete' | 'excellent',
  userEmail?: string
) {
  // Map feedback to numeric score (-1 to +1)
  const feedbackScore = {
    wrong: -1.0,
    incomplete: -0.5,
    slow: -0.3,
    correct: 0.5,
    excellent: 1.0,
  }[feedback];

  // Update chunk's relevance_feedback_score via exponential moving average
  // new_score = old_score × 0.7 + feedback × 0.3
  // This gradually biases the scoring toward user-preferred chunks

  const { error } = await supabase.rpc('update_chunk_feedback', {
    p_chunk_id: chunkId,
    p_feedback_score: feedbackScore,
  });

  if (!error) {
    console.log(
      `[Feedback] Chunk ${chunkId.slice(0, 8)}... ` +
        `updated with "${feedback}" (score: ${feedbackScore})`
    );

    // Invalidate cache to ensure new feedback is reflected
    await redis?.del(`rag:*`); // Clear all RAG cache entries
  }

  // Log for Bayesian learning (monthly retraining)
  await logFeedback({
    chunk_id: chunkId,
    feedback,
    feedback_score: feedbackScore,
    user_email: userEmail,
    timestamp: new Date(),
  });
}

// Usage in agent response:
async function agenteSaneamentoWithFeedback(userQuery: string, userEmail: string) {
  const ragResult = await ragService.queryCollection(
    { query_text: userQuery, top_k: 5, include_reasoning: true },
    'saneamento'
  );

  const agentResponse = await generateAgentResponse(userQuery, ragResult);

  // Return response with feedback collection UI
  return {
    response: agentResponse,
    feedback_chunk_ids: ragResult.chunks.map(c => c.chunk.chunk_id),
    feedback_enabled: true,
  };
}

// Client-side (UI):
/*
User sees agent response with 5-star rating widget:

[Agent Response]
"Lei 14.026 estabelece o marco regulatório para concessões integradas..."

[Feedback Widget]
Was this answer helpful?
☆ ☆ ☆ ☆ ☆  (1-5 stars)

Optional: Which chunk was most helpful?
[ ] Document 1: Lei 14.026...
[ ] Document 2: BNDES Edital...
[ ] Document 3: ...

When user clicks a chunk → recordUserFeedback(chunkId, rating)
*/
```

---

## Example 5: Bulk Document Ingestion

### Scenario
Quarterly ingestion of new regulations, editais, and standards into RAG.

```typescript
import { ChunkMetadata } from '../src/rag-hierarchy';

async function bulkIngestDocuments(
  collection: CollectionType,
  documents: {
    title: string;
    content: string;
    source_org: string;
    url?: string;
    published_date?: Date;
  }[]
) {
  console.log(`[Ingest] Starting bulk ingest for ${collection}: ${documents.length} docs`);

  const embeddings = await embeddingModel.embedBatch(
    documents.map(d => d.content),
    { model: 'BAAI/bge-small-en-v1.5' }
  );

  const chunks: ChunkMetadata[] = documents
    .flatMap((doc, docIdx) => {
      // Split document into chunks (using sliding window)
      const docChunks = splitIntoChunks(doc.content, windowSize: 300);

      return docChunks.map((chunk, chunkIdx) => ({
        chunk_id: crypto.randomUUID(),
        document_id: `${collection}:${doc.title.toLowerCase().replace(/\s/g, '-')}`,
        source_collection: collection,
        text: chunk,
        embedding: embeddings[docIdx],
        embedding_model: 'BAAI/bge-small-en-v1.5',
        source_document_title: doc.title,
        source_document_type: inferDocumentType(doc.title),
        source_url: doc.url,
        source_organization: doc.source_org,
        domain_tags: extractDomainTags(chunk, collection),
        segment_codes: inferSegmentCodes(collection),
        lifecycle_phases: inferLifecyclePhasess(collection),
        published_date: doc.published_date,
        ingested_at: new Date(),
        currency_status: 'current' as const,
        confidence: 0.75, // Default; can be overridden based on source
        citation_count: 0, // Will be updated as docs reference each other
        chunk_order: chunkIdx,
        window_size: 300,
      }));
    });

  // Bulk insert to Supabase
  const batchSize = 100;
  for (let i = 0; i < chunks.length; i += batchSize) {
    const batch = chunks.slice(i, i + batchSize);
    const { error } = await supabase.from('rag_chunks').insert(batch);

    if (error) {
      console.error(
        `[Ingest] Error inserting batch ${i / batchSize}: ${error.message}`
      );
    } else {
      console.log(
        `[Ingest] ✓ Inserted ${batch.length} chunks (${i + batch.length}/${chunks.length})`
      );
    }
  }

  console.log(`[Ingest] Complete: ${chunks.length} chunks ingested`);

  // Clear Redis cache to ensure new docs are discoverable
  await redis?.flushdb();
}

// Quarterly trigger (e.g., via Cron job)
async function quarterlyRagRefresh() {
  console.log('[Quarterly] RAG refresh starting...');

  // 1. Fetch new documents from source feeds
  const newDocs = {
    saneamento: await fetchNewSNISDocuments(),
    energia: await fetchNewANEELEditais(),
    portos: await fetchNewANTAQRegulations(),
    barragens: await fetchNewICOLDStandards(),
    editais: await fetchNewBNDESEditais(),
  };

  // 2. Ingest into respective collections
  for (const [collection, docs] of Object.entries(newDocs)) {
    if (docs.length > 0) {
      await bulkIngestDocuments(collection as CollectionType, docs);
    }
  }

  // 3. Monitor ingestion health
  const stats = await supabase.from('rag_chunks_stats').select('*');
  console.log('[Quarterly] RAG stats after refresh:', stats.data);

  console.log('[Quarterly] RAG refresh complete');
}
```

---

## Example 6: Observability Dashboard (Query Metrics)

### Schema

```sql
CREATE TABLE rag_query_metrics (
  id              UUID PRIMARY KEY,
  user_email      TEXT,
  query_text      TEXT NOT NULL,
  segment_code    TEXT,
  collection      TEXT NOT NULL,
  top_score       NUMERIC,
  chunks_returned INT,
  handoff_applied TEXT,
  cache_hit       BOOLEAN,
  latency_ms      INT,
  agent_response_length INT,
  feedback        TEXT, -- user's rating (optional, set later)
  created_at      TIMESTAMPTZ DEFAULT now()
);
```

### Dashboard Queries

```typescript
// 1. Cache effectiveness (last 24 hours)
SELECT
  COUNT(*) FILTER (WHERE cache_hit) as cached_queries,
  COUNT(*) FILTER (WHERE NOT cache_hit) as uncached_queries,
  ROUND(100.0 * COUNT(*) FILTER (WHERE cache_hit) / COUNT(*), 1) as cache_hit_rate,
  ROUND(AVG(latency_ms) FILTER (WHERE cache_hit), 1) as avg_cached_latency_ms,
  ROUND(AVG(latency_ms) FILTER (WHERE NOT cache_hit), 1) as avg_uncached_latency_ms
FROM rag_query_metrics
WHERE created_at > now() - INTERVAL '1 day';

// 2. Collection popularity (last 7 days)
SELECT
  collection,
  COUNT(*) as query_count,
  ROUND(AVG(top_score), 3) as avg_top_score,
  ROUND(100.0 * COUNT(*) FILTER (WHERE handoff_applied IS NOT NULL) / COUNT(*), 1) as handoff_rate_pct
FROM rag_query_metrics
WHERE created_at > now() - INTERVAL '7 days'
GROUP BY collection
ORDER BY query_count DESC;

// 3. Agent usage (which agents are hitting RAG most?)
SELECT
  agent_id,
  COUNT(*) as queries,
  AVG(latency_ms) as avg_latency
FROM rag_query_metrics
WHERE created_at > now() - INTERVAL '30 days'
GROUP BY agent_id
ORDER BY queries DESC;
```

---

## Summary

These examples demonstrate:
1. **Single-agent query:** agente-saneamento answering user questions with RAG
2. **Cross-domain:** Handling queries that span multiple collections (S10 + S9)
3. **Maestro routing:** Using RAG to validate semantic routing decisions
4. **Feedback loop:** Learning from user ratings to improve chunk ranking
5. **Bulk ingest:** Quarterly document ingestion & refresh
6. **Observability:** Monitoring cache hit rates, latency, and agent usage

For more details, refer to `docs/rag-hierarchy-v5.md`.
