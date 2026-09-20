# WEEK 4 EXECUTION PLAN — Tier 1 Crawler Deployment to Supabase Dev
## 2026-07-21 to 2026-07-27

---

## CRITICAL PATH & SCHEDULE

| Phase | Days | Owner | Objective |
|-------|------|-------|-----------|
| **Phase 1: Infra Setup** | Mon-Tue | DevOps | Supabase dev branch, schema deploy, pgvector config |
| **Phase 2: Crawler Deployment** | Wed-Thu | Engineering | Deploy all 5 crawlers, test in dev, validate chunking |
| **Phase 3: Validation & QA** | Fri-Sat | QA/Engineering | Run 45k+ chunks through pipeline, OCR quality, embedding tests |
| **Phase 4: Week 4 Go/No-Go** | Sat PM | Leadership | Decision gate for Week 5 Tier 2 planning |

---

## PHASE 1: INFRASTRUCTURE SETUP (Mon-Tue)

### 1.1 Supabase Development Branch
**Objective**: Create isolated dev environment for Tier 1 ingestion testing.

**Checklist:**
- [ ] Create Supabase dev branch `phase-1a-tier1-dev` from production
- [ ] Verify branch has 5 segment schemas (por:, aer:, san:, ene:, bar:)
- [ ] Confirm pgvector extension enabled + indices created
- [ ] Test connection from local machine + CI/CD pipeline
- [ ] Seed 100 test chunks per segment (5 sources × 20 chunks)
- [ ] Verify FTS indices working (`SELECT * FROM rag_chunks WHERE to_tsquery(...) @@...`)
- [ ] Confirm embedding dim = 384 for OpenAI text-embedding-3-small

**Owner**: Supabase team / DevOps

**Validation**:
```sql
SELECT 
  (SELECT count(*) FROM rag_chunks WHERE prefix = 'por:') AS portos,
  (SELECT count(*) FROM rag_chunks WHERE prefix = 'aer:') AS aeroportos,
  (SELECT count(*) FROM rag_chunks WHERE prefix = 'san:') AS saneamento,
  (SELECT count(*) FROM rag_chunks WHERE prefix = 'ene:') AS energia,
  (SELECT count(*) FROM rag_chunks WHERE prefix = 'bar:') AS barragens;
-- Expected: 100, 100, 100, 100, 100
```

### 1.2 CI/CD Pipeline Configuration
**Objective**: Automate crawler execution, chunking, and ingestion to dev.

**Checklist:**
- [ ] Create GitHub Actions workflow `.github/workflows/phase1a-tier1-ingest.yml`
  - Trigger: `workflow_dispatch` (manual) + schedule nightly
  - Matrix: 5 segments (portos, aeroportos, saneamento, aneel/energia, barragens)
  - Steps:
    1. Checkout repo + install crawlers
    2. Run crawler: `python backends/<segment>/crawlers/<segment>_rag_ingestion.py --env dev`
    3. Upload JSONL chunks to `tmp/phase1a/<segment>/chunks_week4.jsonl`
    4. Run chunker: `python scripts/chunk_and_embed.py --input tmp/phase1a/<segment>/chunks_week4.jsonl --output tmp/phase1a/<segment>/embedded_week4.jsonl`
    5. Ingest to Supabase dev: `python scripts/ingest_to_supabase.py --db-url $DEV_SUPABASE_URL --jsonl tmp/phase1a/<segment>/embedded_week4.jsonl`
    6. Post results to Slack: chunk count, embedding latency, any errors
- [ ] Set environment variables in GitHub Secrets:
  - `DEV_SUPABASE_URL` (read-write access to dev branch)
  - `OPENAI_API_KEY` (for embeddings)
  - `SLACK_WEBHOOK_URL` (for notifications)
- [ ] Test workflow with dry-run (no commit to dev yet)
- [ ] Verify each segment produces JSONL output without errors

**Owner**: DevOps / Engineering

**Validation**: Workflow runs successfully on all 5 segments, produces 5 JSONL files in artifacts.

### 1.3 Local Development Setup
**Objective**: Enable developers to run crawlers locally + test against dev Supabase.

**Checklist:**
- [ ] Update `.env.example` for each crawler with dev endpoints:
  ```
  SUPABASE_DEV_URL=https://<dev-branch>.supabase.co
  SUPABASE_DEV_KEY=<anon-key-dev>
  OPENAI_API_KEY=sk-...
  CRAWLER_ENV=dev
  ```
- [ ] Create `scripts/setup-dev-env.sh` to populate `.env` from Secrets Manager
- [ ] Test crawler locally:
  ```bash
  cd backends/portos
  source ../../.env
  python crawlers/portos_rag_ingestion_week3_v2.py --env dev --limit 50
  ```
  Expected: Pulls 50 documents, chunks them, produces JSONL locally
- [ ] Verify chunking output format matches schema:
  ```json
  {
    "id": "por:antaq-20260721-001",
    "prefix": "por:",
    "source": "ANTAQ Editais",
    "title": "...",
    "content": "...",
    "chunk_index": 0,
    "chunk_total": 5,
    "metadata": {
      "url": "https://...",
      "crawl_date": "2026-07-21T10:00:00Z",
      "document_type": "edital",
      "language": "pt-BR"
    }
  }
  ```

**Owner**: Engineering

**Validation**: Developers can clone repo, run setup script, and ingest test crawl locally to dev Supabase.

---

## PHASE 2: CRAWLER DEPLOYMENT (Wed-Thu)

### 2.1 Portos (S6) Deployment
**Objective**: Validate ANTAQ + DNIT crawl pipeline in dev.

**Checklist:**
- [ ] **Crawler Execution**:
  - [ ] Run `portos_rag_ingestion_week3_v2.py --env dev --full-crawl`
  - [ ] Target: 8,000–10,000 documents (ANTAQ editais + DNIT guidance)
  - [ ] Measure: Crawl time, HTTP errors, 403 fallback count
  - [ ] Output: `tmp/portos_tier1_week4.jsonl` (RAW)
  
- [ ] **Chunking**:
  - [ ] Run chunker: `scripts/chunk_and_embed.py --input tmp/portos_tier1_week4.jsonl --output tmp/portos_embedded_week4.jsonl`
  - [ ] Target: 9,000–11,000 chunks (avg 1.1 chunks per doc)
  - [ ] Measure: Chunking latency, avg chunk length (target 350–450 tokens)
  - [ ] Validate: No chunks > 512 tokens (hard limit for embeddings)
  
- [ ] **Embedding**:
  - [ ] Batch embed via OpenAI API: `tmp/portos_embedded_week4.jsonl`
  - [ ] Measure: Cost (est. $3–5 for 10k chunks at $0.02/1M), latency
  - [ ] Verify: All chunks have `embedding_384d` field (384 floats)
  
- [ ] **Ingestion to Supabase dev**:
  - [ ] Run: `scripts/ingest_to_supabase.py --db-url $DEV_SUPABASE_URL --jsonl tmp/portos_embedded_week4.jsonl --prefix por:`
  - [ ] Measure: Ingestion speed (target 500 chunks/sec), errors
  - [ ] Validate: `SELECT count(*) FROM rag_chunks WHERE prefix = 'por:'` → ~10k
  
- [ ] **FTS Index Test**:
  - [ ] Query: `SELECT * FROM rag_chunks WHERE prefix = 'por:' AND to_tsquery('porto & dragagem') @@ fts_content LIMIT 5`
  - [ ] Verify: Returns relevant results
  
- [ ] **Vector Search Test**:
  - [ ] Embed query: "Qual é o calado máximo do porto de Santos?"
  - [ ] `SELECT id, title, (embedding <-> query_embedding) AS distance FROM rag_chunks WHERE prefix = 'por:' ORDER BY distance LIMIT 5`
  - [ ] Verify: Top-5 results are relevant (distance < 0.3)

**Owner**: S6 Portos team

**Expected Output**:
```json
{
  "segment": "portos",
  "tier": 1,
  "documents_crawled": 9000,
  "chunks_generated": 10500,
  "chunks_ingested": 10500,
  "embedding_cost_usd": 4.20,
  "crawl_time_minutes": 45,
  "chunking_time_minutes": 12,
  "embedding_time_minutes": 180,
  "http_403_count": 2,
  "fts_test": "PASS",
  "vector_search_test": "PASS",
  "status": "READY"
}
```

### 2.2 Aeroportos (S7) Deployment
**Objective**: Validate ANAC + ICAO crawl pipeline, handle 403 fallback.

**Checklist:**
- [ ] **Crawler Execution**:
  - [ ] Run `aeroportos_rag_week3_crawler.py --env dev --full-crawl`
  - [ ] Target: 5,000–7,000 documents (ANAC, ICAO Annex 14, FAA ACs)
  - [ ] Measure: HTTP 403 fallback activation count, alternative URL success rate
  - [ ] Troubleshoot: If 403 rate > 30%, escalate to ANAC team for API access
  - [ ] Output: `tmp/aeroportos_tier1_week4.jsonl`
  
- [ ] **Chunking & Embedding**:
  - [ ] Run chunker → `tmp/aeroportos_embedded_week4.jsonl` (target 6,500–8,000 chunks)
  - [ ] Batch embed (est. $2–3 cost)
  - [ ] Verify chunk quality (no truncation, >= 100 tokens)
  
- [ ] **Ingestion to Supabase dev**:
  - [ ] Ingest to `aer:` prefix (target 7,500 chunks)
  - [ ] Validate FTS and vector search as above
  - [ ] **Special test**: Query "ILS approach procedure" → verify FAA AC results appear

**Owner**: S7 Aeroportos team

**Expected Output**: Similar JSON as S6, but with note on HTTP 403 handling.

### 2.3 Saneamento (S8) Deployment
**Objective**: Validate SNIS 2024 + Lei 14.026 pipeline (highest volume).

**Checklist:**
- [ ] **Crawler Execution**:
  - [ ] Run `saneamento_rag_week3.py --env dev --full-crawl`
  - [ ] Target: 12,000–15,000 documents (SNIS largest contributor)
  - [ ] Measure: Crawl time (expect 60+ min for SNIS), API rate limits
  - [ ] Optimize: Implement exponential backoff if hitting SNIS rate limits
  - [ ] Output: `tmp/saneamento_tier1_week4.jsonl`
  
- [ ] **Chunking & Embedding**:
  - [ ] Run chunker → 14,000–17,000 chunks (expect high volume)
  - [ ] Batch embed in parallel batches (OpenAI API max 100 req/min) (est. $5–7 cost)
  - [ ] Monitor: Verify no timeout on large batches
  
- [ ] **Ingestion to Supabase dev**:
  - [ ] Ingest to `san:` prefix (target 16k chunks)
  - [ ] **Special test**: Query "ETA água tratada" → verify SNIS results
  - [ ] Validate: Confirm AySA Argentina documents (prioritized) appear in results

**Owner**: S8 Saneamento team

**Expected Output**: ~16k chunks ingested, cost $6, high volume confirmed.

### 2.4 Energia (S9) Deployment
**Objective**: Validate ANEEL crawler + LT transmission focus.

**Checklist:**
- [ ] **Crawler Execution**:
  - [ ] Run `aneel_harvester.py --env dev --full-crawl`
  - [ ] Target: 6,000–8,000 documents (ANEEL editals + EPE, ONS, IEEE)
  - [ ] Measure: CKAN API success rate, fallback to web scraper count
  - [ ] Verify: 48+ ANEEL editais discovered (from Week 3 validation)
  - [ ] Output: `tmp/energia_tier1_week4.jsonl`
  
- [ ] **Chunking & Embedding**:
  - [ ] Run chunker → 7,500–9,500 chunks
  - [ ] Embed (est. $3–4 cost)
  - [ ] **Special attention**: Verify technical documents (ONS, EPE) chunked correctly (may have tables/diagrams)
  
- [ ] **Ingestion to Supabase dev**:
  - [ ] Ingest to `ene:` prefix (target 8.5k chunks)
  - [ ] **Special test**: Query "Leilão transmissão linha de transmissão" → verify ANEEL editals
  - [ ] Validate: Confirm State Grid documents (prioridade) in results

**Owner**: S9 Energia team

**Expected Output**: 8.5k chunks, ANEEL editorial coverage confirmed.

### 2.5 Barragens (S10) Deployment
**Objective**: Validate Lei 12.334 + ICOLD crawler, resolve 403 issues.

**Checklist:**
- [ ] **Crawler Execution**:
  - [ ] Run `barragens_s10_week3_ingestion.py + lei_parser.py --env dev --full-crawl`
  - [ ] Target: 4,000–6,000 documents (Lei 12.334, ICOLD, CBDB, SIGBM)
  - [ ] Measure: ICOLD database 403 rate, lei_parser success
  - [ ] Troubleshoot: If ICOLD 403 > 20%, escalate to data provider
  - [ ] Output: `tmp/barragens_tier1_week4.jsonl`
  
- [ ] **Chunking & Embedding**:
  - [ ] Run chunker → 5,000–7,000 chunks (legal documents may be dense)
  - [ ] Embed (est. $2–3 cost)
  - [ ] Validate: Lei 12.334 sections properly chunked by article
  
- [ ] **Ingestion to Supabase dev**:
  - [ ] Ingest to `bar:` prefix (target 6.5k chunks)
  - [ ] **Special test**: Query "Lei 12.334 rejeitos segurança" → verify legislation appears
  - [ ] Validate: CBDB (case studies) content searchable

**Owner**: S10 Barragens team

**Expected Output**: 6.5k chunks, Lei 12.334 coverage 100%.

---

## PHASE 3: VALIDATION & QA (Fri-Sat)

### 3.1 Aggregate Tier 1 Validation

**Checklist:**
- [ ] **Total Chunk Count**:
  ```sql
  SELECT 
    COUNT(*) AS total_chunks,
    SUM(CASE WHEN prefix = 'por:' THEN 1 ELSE 0 END) AS portos,
    SUM(CASE WHEN prefix = 'aer:' THEN 1 ELSE 0 END) AS aeroportos,
    SUM(CASE WHEN prefix = 'san:' THEN 1 ELSE 0 END) AS saneamento,
    SUM(CASE WHEN prefix = 'ene:' THEN 1 ELSE 0 END) AS energia,
    SUM(CASE WHEN prefix = 'bar:' THEN 1 ELSE 0 END) AS barragens
  FROM rag_chunks;
  ```
  **Expected**: 45,000–55,000 total chunks (~10k per segment)

- [ ] **Embedding Quality**:
  - [ ] Sample 100 random chunks per segment
  - [ ] Verify `embedding_384d` field populated (no NULLs)
  - [ ] Check embedding values in range [-1, 1] (normalized)
  - [ ] Measure: Avg embedding norm ≈ 1.0 (unit vectors)
  - [ ] **Expected**: 100% populated, valid ranges

- [ ] **FTS Coverage**:
  - [ ] Test each segment FTS index:
    ```sql
    SELECT COUNT(DISTINCT id) FROM rag_chunks WHERE prefix = 'por:' AND fts_content IS NOT NULL;
    -- Expected: 100% match with total chunks
    ```
  - [ ] Run 5 domain-specific queries per segment, verify results:
    - **Portos**: "dragagem", "contêiner", "berço", "molhe", "ANTAQ"
    - **Aeroportos**: "pista", "ILS", "balizamento", "ANAC", "taxiway"
    - **Saneamento**: "ETA", "ETE", "SNIS", "adutora", "Lei 14.026"
    - **Energia**: "transmissão", "ANEEL", "leilão", "ONS", "subestação"
    - **Barragens**: "Lei 12.334", "rejeitos", "CBDB", "barragem", "segurança"
  - [ ] **Expected**: Each query returns >= 5 relevant results (distance < 0.35)

- [ ] **Metadata Completeness**:
  - [ ] Sample 50 chunks per segment, verify metadata:
    - `url` field populated and valid
    - `crawl_date` in ISO 8601 format
    - `document_type` in allowed enum (edital, norma, lei, artigo, publicação, etc.)
    - `language` = "pt-BR" (or "en" for ICAO/FAA/ICOLD)
  - [ ] **Expected**: 100% fields populated, no NULLs

### 3.2 OCR Quality Assessment

**Objective**: Validate that PDF text extraction produced usable chunks (for segments with PDF source docs).

**Checklist:**
- [ ] **PDF Source Identification**:
  - [ ] Query: `SELECT COUNT(*) FROM rag_chunks WHERE prefix IN ('por:', 'san:', 'ene:', 'bar:') AND metadata->>'document_type' = 'pdf';`
  - [ ] **Expected**: 60%+ chunks from PDFs (ANEEL, Lei 12.334, ICOLD documents are PDF-heavy)

- [ ] **OCR Artifacts Detection**:
  - [ ] Sample 50 PDF-sourced chunks, manually inspect for:
    - Garbled characters (mojibake, encoding errors)
    - Excessive whitespace / line breaks
    - Missing sections (e.g., tables that became blank lines)
    - Rotated text fragments
  - [ ] **Acceptance criteria**: <= 5% chunks with severe OCR issues, medium issues (formatting) acceptable
  
- [ ] **Table Extraction**:
  - [ ] For S8 Saneamento (SNIS has tables): sample 20 SNIS chunks
    - Verify tabular data readable (e.g., "ETA | Capac. | Consórcio")
    - **Acceptance**: >= 80% table chunks preserve column structure
  - [ ] For S9 Energia (EPE has tables): sample EPE chunks
    - Verify cost/capacity tables readable
    - **Acceptance**: >= 80% preserve structure

### 3.3 Embedding Quality Test

**Objective**: Verify semantic relevance of embeddings via similarity search.

**Checklist:**
- [ ] **Query Relevance Test** (per segment):
  
  **Portos**: 
  - Query: "Qual é o calado máximo do porto de Santos?" → encode + search
  - Expected top-5: ANTAQ docs about Santos port, calado specs
  - **Pass if**: top-3 results relevant (distance < 0.25)
  
  **Aeroportos**:
  - Query: "Qual é a altitude do aeroporto de Brasília?" → encode + search
  - Expected: ANAC documents, airport procedures
  - **Pass if**: top-3 relevant (distance < 0.25)
  
  **Saneamento**:
  - Query: "Qual é a ETA maior do Brasil em capacidade?" → encode + search
  - Expected: SNIS 2024 data, large ETAs
  - **Pass if**: top-3 relevant (distance < 0.25)
  
  **Energia**:
  - Query: "Qual é o custo de uma subestação de transmissão?" → encode + search
  - Expected: EPE cost data, ANEEL editais
  - **Pass if**: top-3 relevant (distance < 0.25)
  
  **Barragens**:
  - Query: "Qual foi o acidente na barragem de Brumadinho?" → encode + search
  - Expected: CBDB case studies, Lei 12.334 discussions
  - **Pass if**: top-3 relevant (distance < 0.25)

- [ ] **Semantic Drift Test**:
  - Query: "pizza" (off-topic) → should NOT return engineering results (distance > 0.6)
  - **Expected**: All segments reject off-topic queries

### 3.4 Ingestion Performance Metrics

**Checklist:**
- [ ] **Speed**:
  ```
  Crawling: portos 45 min, aeroportos 30 min, saneamento 60 min, energia 25 min, barragens 20 min
  Chunking: ~1 min per segment
  Embedding: 180–200 min total (parallel batching)
  Ingestion: 200–300 min total (depends on Supabase throughput)
  TOTAL WEEK 4: ~9–10 hours wall-clock (acceptable for automated pipeline)
  ```

- [ ] **Cost**:
  ```
  Embeddings (OpenAI): $18–22 for 45k chunks
  Supabase storage: +500 MB ~ +$5/month
  TOTAL INCREMENTAL COST: ~$25 (one-time Week 4 run)
  ```

- [ ] **Error Rate**:
  - [ ] HTTP errors during crawl: <= 5% (retries handle most)
  - [ ] Chunking failures: 0% (all documents should chunk)
  - [ ] Embedding failures: < 1% (OpenAI API reliability)
  - [ ] Ingestion failures: < 0.5% (Supabase transaction handling)
  - [ ] **Expected**: Pipeline completes with > 99% success rate

### 3.5 Documentation & Reporting

**Checklist:**
- [ ] **Week 4 Validation Report** (to be created):
  - Segment-by-segment metrics (chunks, cost, time)
  - Total Tier 1 coverage: 45k–55k chunks ✓
  - FTS validation: 5 queries per segment ✓
  - Vector search: semantic relevance confirmed ✓
  - OCR quality: < 5% severe issues ✓
  - Embedding performance: latency + cost tracked ✓
  - Go/No-Go recommendation for Week 5
  
- [ ] **Known Issues Log**:
  - S7 Aeroportos: 403 rate X%, mitigation Y
  - S10 Barragens: ICOLD access limited, fallback to CBDB
  - Any segment-specific blockers documented
  
- [ ] **Archive Week 4 Outputs**:
  - Store all JSONL files: `docs/phase-1a-week4/{portos,aeroportos,saneamento,energia,barragens}_tier1_chunks.jsonl`
  - Store embedding costs + timing: `docs/phase-1a-week4/METRICS.json`
  - Store validation report: `docs/phase-1a-week4/VALIDATION-REPORT.md`

---

## PHASE 4: GO/NO-GO DECISION (Sat PM)

### 4.1 Decision Criteria

**GO Decision** (Week 5 Tier 2 planning proceeds):
- [ ] Total chunks ingested: 45,000–55,000 ✓
- [ ] All 5 segments have > 8,000 chunks ✓
- [ ] FTS test: 5 queries per segment, 80%+ relevant results ✓
- [ ] Vector search: semantic relevance confirmed (distance < 0.25) ✓
- [ ] OCR quality: < 5% severe issues ✓
- [ ] Embedding errors: < 1% ✓
- [ ] Ingestion errors: < 0.5% ✓

**NO-GO Decision** (Week 5 paused, root-cause analysis):
- If any segment < 8,000 chunks: re-crawl + chunk
- If FTS/vector search fail: investigate embedding quality or schema issues
- If OCR > 5% severe: escalate PDF processing pipeline
- If 403 blockers unresolved: escalate to data providers (ANAC, ICOLD, ANTAQ)

### 4.2 Escalation & Contingency

**If blocked on Tier 1 completion**:
- Week 5 (Jul 28–Aug 3): Focus on **HTTP 403 resolution** + **Tier 2 crawl planning** (Tier 2 discovery agents completing in parallel)
- Delay Week 6–7 Tier 2 ingestion by 1 week if needed
- Resume critical path: Week 4 completion → Week 5 planning → Week 6 Tier 2 ingest

**If Tier 2 discovery completes early**:
- Begin Week 5 Tier 2 crawler development in Week 4 (overlap)
- Accelerate timeline by 3–5 days

---

## DELIVERABLES CHECKLIST

By EOD Saturday (2026-07-27):

**Code & Infrastructure**:
- [ ] Supabase dev branch `phase-1a-tier1-dev` populated + validated
- [ ] GitHub Actions workflow `.github/workflows/phase1a-tier1-ingest.yml` deployed
- [ ] Local dev setup (`scripts/setup-dev-env.sh`) working
- [ ] All 5 crawlers tested + producing JSONL in dev environment

**Data & Validation**:
- [ ] 45k–55k chunks ingested to dev Supabase (all 5 segments)
- [ ] FTS index: 5 queries per segment tested, 80%+ relevant
- [ ] Vector search: semantic test queries passed (distance < 0.25)
- [ ] OCR quality report: < 5% severe issues identified
- [ ] Embedding quality: 100% chunks have valid 384d vectors
- [ ] Cost tracking: OpenAI embeddings + Supabase storage documented

**Documentation**:
- [ ] Week 4 Validation Report (`docs/phase-1a-week4/VALIDATION-REPORT.md`)
- [ ] Metrics JSON (`docs/phase-1a-week4/METRICS.json`)
- [ ] Known Issues Log (blockers + mitigations documented)
- [ ] Go/No-Go decision memo to leadership

**Status Communications**:
- [ ] Daily standup messages (Mon–Sat) to Slack #phase1a-engineering
- [ ] Weekly summary: "Week 4 Tier 1 validation: PASS / blockers: [X]"
- [ ] Week 5 readiness: Tier 2 discovery results + decision on Tier 2 crawler deployment

---

## RISK REGISTER & CONTINGENCIES

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| HTTP 403 blockers (ANAC, ICOLD, ANTAQ) | High (40%) | Medium | Documented fallback URLs; escalate early Mon if > 20% failure |
| SNIS crawl timeout (12k+ docs) | Medium (25%) | Medium | Implement exponential backoff; split crawl if needed |
| OCR quality too low (>10% severe) | Low (10%) | High | Switch to alternative PDF library (pdfplumber → PyPDF2); manual intervention for critical docs |
| Embedding API rate limit | Low (5%) | Medium | Implement exponential backoff; batch smaller if needed |
| Supabase ingestion bottleneck | Low (5%) | Medium | Increase batch size; use `--parallel 10` flag |
| Tier 2 discovery agents incomplete by Fri | Medium (35%) | Medium | Continue into Week 5; do not block Tier 1 validation |

---

## SUCCESS CRITERIA

**Week 4 is successful if**:
1. ✅ 45k–55k Tier 1 chunks ingested to dev Supabase
2. ✅ All 5 segments pass FTS + vector search validation
3. ✅ OCR quality acceptable (< 5% severe issues)
4. ✅ Total cost < $30 (embeddings + storage)
5. ✅ Pipeline documented and repeatable
6. ✅ Go/No-Go decision made for Week 5 Tier 2

---

## TIMELINE SUMMARY

```
Mon 2026-07-21: Infra setup (Supabase, CI/CD, local dev)
Tue 2026-07-22: CI/CD validation, dry-run
Wed 2026-07-23: S6 Portos + S7 Aeroportos deployment
Thu 2026-07-24: S8 Saneamento + S9 Energia + S10 Barragens deployment
Fri 2026-07-25: Full validation (FTS, vector, embedding, OCR)
Sat 2026-07-26: Final QA + reporting
Sat 2026-07-27: Go/No-Go decision (PM) + Week 5 planning kickoff
```

---

## OWNER ASSIGNMENTS

| Component | Owner | Slack Handle |
|-----------|-------|--------------|
| Supabase dev branch | DevOps | @devops |
| CI/CD pipeline | Engineering | @backend-lead |
| Local dev setup | Engineering | @backend-lead |
| S6 Portos deployment | S6 Team | @portos-tech |
| S7 Aeroportos deployment | S7 Team | @aeroportos-tech |
| S8 Saneamento deployment | S8 Team | @saneamento-tech |
| S9 Energia deployment | S9 Team | @energia-tech |
| S10 Barragens deployment | S10 Team | @barragens-tech |
| Validation & QA | QA Lead | @qa-lead |
| Week 4 reporting | PM | @pm-phase1a |

---

**Last Updated**: 2026-07-16
**Status**: Ready for Week 4 execution
**Next Review**: 2026-07-27 (Go/No-Go decision)
