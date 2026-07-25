# Sprint 2 RAG Integration — Quick Reference & Index
## rod:seism:* Collections Ingest Plan

**Prepared:** 2026-07-25  
**Corpus:** 78+ documents (seismic & structural design, roadway projects)  
**Target:** Supabase PostgreSQL with pgvector extension  
**Phases:** D6.1 through D7.5 (project lifecycle)  

---

## DELIVERABLES CHECKLIST

All files located in `/tmp/claude-0/.../scratchpad/`:

### 1. Core Planning Document
- **File:** `SPRINT2-RAG-INTEGRATION-PLAN.md` (25 KB)
  - SQL schema design (3 tables, 7+ indexes)
  - Chunking strategy (1.2k–2.0k tokens, 15–20% overlap)
  - Retrieval weights & scoring formula (hybrid: 60% semantic + 30% BM25 + 10% metadata)
  - Python & TypeScript ingestion templates (ready to deploy)
  - Query patterns for D6.1–D7.5 phases
  - Deployment checklist (pre-deploy, staging, production, post-deploy)
  - Monitoring KPIs and weekly review procedures

### 2. Database Schema & Deployment
- **File:** `rag-schema-deployment.sql` (12 KB)
  - CREATE TABLE: rag_chunks, rag_documents, rag_query_logs
  - 7+ optimized indexes (IVFFlat for embeddings, GIN for text search)
  - Helper functions: query_rag_chunks(), phase_proximity_weight(), content_type_boost()
  - RLS policies (read for all, insert for service role)
  - Reporting views: v_rag_ingestion_status, v_rag_query_performance
  - Verification queries (post-deployment validation)

### 3. Ingestion Scripts
- **Python Template:** `SPRINT2-RAG-INTEGRATION-PLAN.md` (section 5.1)
  - PDFExtractor class (text + structure extraction)
  - ChunkingEngine class (semantic chunking with header hierarchy)
  - EmbeddingService class (OpenAI text-embedding-3-small)
  - SupabaseUploader class (batch insert, error handling)
  - CLI args: --pdf, --collection, --phase, --type
  
- **TypeScript/Edge Function:** `SPRINT2-RAG-INTEGRATION-PLAN.md` (section 5.2)
  - HTTP POST endpoint for batch ingest
  - Request validation (chunk count == embedding count)
  - Batch processing logic (10 chunks/batch)
  - RLS-aware inserts with error handling

### 4. Deployment & Testing
- **File:** `DEPLOYMENT-CHECKLIST.md` (18 KB)
  - Phase 0: Pre-deployment validation (schema, documents, embedding service)
  - Phase 1: Staging deployment (schema, 10% ingestion, query validation)
  - Phase 2: Production deployment (full ingestion, live queries)
  - Phase 3: Post-deployment monitoring (Day-1, weekly, monthly)
  - Rollback procedure for critical issues
  
- **File:** `RAG-QUERY-TEST-SUITE.md` (22 KB)
  - 8+ test queries covering D6.1–D7.5 phases
  - Evaluation metrics: relevance score, latency, phase accuracy, content type accuracy
  - Cross-phase validation (proximity weighting, content boost, feedback loop)
  - Performance benchmarks (latency p95, relevance distribution)
  - Failure investigation guide with remediation steps
  - Test execution checklist

### 5. Document Manifest & Configuration
- **File:** `DOCUMENT_MANIFEST_TEMPLATE.json` (15 KB)
  - Collection metadata (78+ documents across 4 collections)
  - Per-collection document inventory (sourceDocId, title, phase_code, doc_type, etc.)
  - Phase mapping (D6.1–D7.5 with expected collections and query examples)
  - Ingestion checklist (pre, during, post)
  - Configuration notes (chunking, embedding, vector DB, weighting)

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────┐
│      Documents (78+)                    │
│  ├─ rod:seism:design (20 docs)          │
│  ├─ rod:seism:geotechnical (18 docs)    │
│  ├─ rod:seism:structure (22 docs)       │
│  └─ rod:seism:analysis (18 docs)        │
└─────────────────┬───────────────────────┘
                  │ (PDF extraction + chunking)
                  ↓
        ┌────────────────────┐
        │ Chunking Engine    │
        │ • 1.2k–2.0k tokens │
        │ • 15–20% overlap   │
        │ • Header hierarchy │
        │ • Content classify │
        └─────────┬──────────┘
                  │ (Batch 10–50 chunks)
                  ↓
        ┌────────────────────┐
        │ Embedding Service  │
        │ text-embedding-3-  │
        │ small (1536 dim)   │
        └─────────┬──────────┘
                  │
                  ↓
    ┌──────────────────────────────┐
    │   Supabase PostgreSQL        │
    │   ┌──────────────────────┐   │
    │   │ rag_chunks (4,000)   │   │
    │   │ • embedding VECTOR   │   │
    │   │ • metadata indices   │   │
    │   │ • IVFFlat search     │   │
    │   └──────────────────────┘   │
    │   ┌──────────────────────┐   │
    │   │ rag_documents (78+)  │   │
    │   │ • ingestion tracking │   │
    │   │ • versioning         │   │
    │   └──────────────────────┘   │
    │   ┌──────────────────────┐   │
    │   │ rag_query_logs       │   │
    │   │ • performance metrics│   │
    │   │ • relevance feedback │   │
    │   └──────────────────────┘   │
    └──────────────┬───────────────┘
                   │
        ┌──────────────────────────────┐
        │  Query Interface             │
        │  • Hybrid scoring (BM25+cos) │
        │  • Phase proximity weighting │
        │  • Content type boost        │
        │  • Result ranking: 60/30/10  │
        └──────────────────────────────┘
```

---

## KEY PARAMETERS

### Chunk Configuration
| Parameter | Value | Rationale |
|---|---|---|
| Target size | 1,500 tokens | Balances context preservation with embedding quality |
| Min size | 1,200 tokens | Ensure sufficient context |
| Max size | 2,000 tokens | Avoid token count overages |
| Overlap | 200–300 tokens (15–20%) | Prevent formula/table splits |

### Retrieval Scoring
```
FINAL_SCORE = 0.6 × SEMANTIC_SIM + 0.3 × BM25_SCORE + 0.1 × METADATA_BOOST
```

**Phase Proximity (METADATA_BOOST component):**
- Same phase (D6.2 → D6.2): 1.0
- Adjacent phase (D6.2 → D6.1 or D6.3): 0.9–0.95
- Non-adjacent (D6.1 → D6.4): 0.3–0.7

**Content Type Boost:**
- Formula: 1.5x
- Table: 1.2x
- Figure caption: 0.8x
- Default text: 1.0x

### Performance Targets

| Metric | Target | Acceptable Range |
|---|---|---|
| Query latency (p95) | 350ms | 250–500ms |
| Top-1 relevance score | 0.75 | 0.70–0.90 |
| Avg user rating | 4.0/5.0 | 3.5–5.0 |
| Phase accuracy | 85% | 80–100% |
| Ingestion success rate | 99% | 97–100% |

---

## CRITICAL PATHS & DEPENDENCIES

### Data Dependencies
```
Document Manifest (sourceDocId, phaseCode, collection_key)
    ↓
PDF Extraction (text + structure)
    ↓
Semantic Chunking (1.2k–2.0k tokens)
    ↓
Embedding Generation (OpenAI API)
    ↓
Supabase Upload (batch insert)
    ↓
Query Validation (relevance testing)
```

### Timeline Estimates
- **Pre-deployment validation:** 2–3 days (document prep, script testing)
- **Staging ingestion (10%):** 30 min (8 documents)
- **Staging query validation:** 4 hours (test suite execution + expert review)
- **Production full ingestion (100%):** 4–8 hours (78 documents, parallel)
- **Production query validation:** 2–4 hours (full test suite + sign-off)
- **Post-deployment monitoring (Day-1):** 8 hours (real-time dashboards + incident response)

**Total Sprint Duration:** 5–7 days

---

## ROLES & RESPONSIBILITIES

| Role | Responsibilities |
|---|---|
| **Engineering Lead** | Schema design, ingestion pipeline, deployment orchestration |
| **Database Admin** | Schema deployment, backups, index tuning, performance monitoring |
| **QA Lead** | Test suite execution, relevance validation, acceptance criteria verification |
| **Product Manager** | Query requirements, phase mapping, expert review coordination |
| **CTO/Approver** | Go/No-Go decision, production sign-off, escalation authority |

---

## QUICK START: LOCAL TESTING

### 1. Clone & Setup
```bash
cd /home/user/Codex-exemplo
cp -r /tmp/claude-0/.../scratchpad ./sprint2-rag
cd sprint2-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # See below
```

### 2. Install Dependencies
```bash
# Python script dependencies
pip install pypdf tiktoken anthropic supabase python-dotenv openai

# Environment variables
echo 'SUPABASE_URL=https://[PROJECT_ID].supabase.co' > .env
echo 'SUPABASE_ANON_KEY=[ANON_KEY]' >> .env
echo 'ANTHROPIC_API_KEY=[API_KEY]' >> .env
echo 'OPENAI_API_KEY=[OPENAI_KEY]' >> .env
```

### 3. Test on Sample Document
```bash
python scripts/ingest_rag_documents.py \
  --pdf docs/sample_doc.pdf \
  --collection rod:seism:design \
  --phase D6.2 \
  --type technical_specification \
  --dry-run

# Review output, then run live:
python scripts/ingest_rag_documents.py \
  --pdf docs/sample_doc.pdf \
  --collection rod:seism:design \
  --phase D6.2 \
  --type technical_specification
```

### 4. Validate in Supabase
```sql
-- Check document metadata
SELECT * FROM rag_documents ORDER BY created_at DESC LIMIT 1;

-- Check chunks
SELECT COUNT(*), collection_key, phase_code
FROM rag_chunks
WHERE source_doc_id = 'sample_doc'
GROUP BY collection_key, phase_code;

-- Test query
SELECT * FROM query_rag_chunks(
  query_embedding => (SELECT embedding FROM rag_chunks LIMIT 1),
  query_phase => 'D6.2',
  collection_keys => ARRAY['rod:seism:design'],
  limit_count => 5
);
```

---

## MONITORING & OBSERVABILITY

### Dashboards to Create

**1. Ingestion Progress**
```sql
SELECT
  collection_key,
  phase_code,
  COUNT(*) AS doc_count,
  SUM(chunk_count) AS total_chunks,
  COUNT(*) FILTER (WHERE ingestion_status='completed') AS completed,
  COUNT(*) FILTER (WHERE ingestion_status='error') AS errors
FROM rag_documents
GROUP BY collection_key, phase_code;
```

**2. Query Performance**
```sql
SELECT
  DATE(created_at) AS date,
  AVG(query_latency_ms) AS avg_latency_ms,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY query_latency_ms) AS p95_latency,
  AVG(top_score) AS avg_relevance,
  AVG(user_rating) AS avg_rating
FROM rag_query_logs
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

**3. Data Quality**
```sql
SELECT
  collection_key,
  COUNT(*) AS total_chunks,
  COUNT(*) FILTER (WHERE has_extraction_issues) AS issue_count,
  ROUND(100.0 * COUNT(*) FILTER (WHERE has_extraction_issues) / COUNT(*), 2) AS issue_pct,
  COUNT(*) FILTER (WHERE is_manually_reviewed) AS reviewed_count
FROM rag_chunks
GROUP BY collection_key;
```

### Alerts to Configure

| Alert | Condition | Action |
|---|---|---|
| **Ingestion Failure** | ingestion_status = 'error' count > 2 | Page on-call engineer |
| **Query Latency** | p95 > 600ms for 5 min | Check Supabase CPU; consider read replicas |
| **Low Relevance** | avg_top_score < 0.60 | Review embedding quality; check phase weights |
| **API Cost** | Embedding costs > $100/day | Review query volume; optimize batch sizes |

---

## REFERENCES

- **Supabase Vector Docs:** https://supabase.com/docs/guides/ai/vector-columns
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Tiktoken:** https://github.com/openai/tiktoken
- **PostgreSQL Full-Text Search:** https://www.postgresql.org/docs/current/textsearch.html
- **RAG Architecture:** https://docs.anthropic.com/claude/reference/models-overview (check for latest RAG patterns)

---

## SUPPORT & ESCALATION

**Questions during implementation?**
- Check: SPRINT2-RAG-INTEGRATION-PLAN.md (main reference)
- Schema issues: rag-schema-deployment.sql (SQL comments)
- Query problems: RAG-QUERY-TEST-SUITE.md (failure investigation)
- Deployment issues: DEPLOYMENT-CHECKLIST.md (troubleshooting)

**Escalation path:**
1. **Level 1 (Engineering):** Check test suite, review logs
2. **Level 2 (DBA):** Investigate index health, query plans
3. **Level 3 (CTO):** Go/No-Go decisions, rollback authorization

---

**Document Generated:** 2026-07-25  
**Status:** Ready for Sprint 2 Execution  
**Next Step:** Schedule Phase 0 Pre-Deployment Validation meeting
