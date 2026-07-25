# RAG Query Test Suite
## rod:seism:* Collections — Validation & Acceptance Criteria

**Version:** 1.0  
**Date:** 2026-07-25  
**Purpose:** Validate RAG retrieval quality across all project phases (D6.1–D7.5)  

---

## 1. TEST FRAMEWORK

### 1.1 Evaluation Metrics

Each query test includes validation on:

| Metric | Definition | Target |
|---|---|---|
| **Result Count** | Number of relevant chunks returned | ≥ 3, ≤ 10 |
| **Avg Top-1 Score** | Cosine similarity + BM25 score of #1 result | ≥ 0.70 |
| **Latency (p95)** | Query execution time percentile | ≤ 500ms |
| **Phase Accuracy** | % of results matching expected phases | ≥ 80% |
| **Content Type Accuracy** | % of results matching expected content (formula/table/text) | ≥ 75% |
| **Expert Relevance** | Manual review score by domain expert | ≥ 4.0/5.0 |

### 1.2 Test Environment

```bash
Environment: Staging database (post-ingestion, pre-production)
Embedding Model: text-embedding-3-small (OpenAI)
Query Embedding Generation: See section 5.2
Collection Target: rod:seism:design, geotechnical, structure, analysis
Document Count: 78+ (full corpus)
Total Chunks: ~4,000
```

---

## 2. PHASE D6.1 QUERIES (Preliminary Study / Estudo Prévio)

### Query D6.1-001: Site Seismic Hazard Characterization

**Query Text:**
```
"What is the seismic zone classification and peak ground acceleration 
(PGA) for this region? Provide historical earthquake data."
```

**Query Embedding Generation:**
```python
import openai
text = "What is the seismic zone classification and peak ground acceleration (PGA) for this region? Provide historical earthquake data."
embedding = openai.Embedding.create(
    input=text,
    model="text-embedding-3-small"
)['data'][0]['embedding']
```

**Expected Results:**
- Collection: `rod:seism:design` (100%)
- Phase: D6.1 (primary), D6.2 (secondary)
- Content Types: Hazard assessment (70%), Normative standard (30%)
- Top-3 Documents: USGS Seismic Hazard, NBR 15421, EN 1998-1

**Acceptance Criteria:**
- [ ] Result count: 3–7
- [ ] Avg top-1 score: ≥ 0.75
- [ ] Phase accuracy: ≥ 90% results from D6.1 or D6.2
- [ ] Latency: ≤ 400ms
- [ ] Expert review: ≥ 4.5/5.0

**SQL Test:**
```sql
WITH query_embed AS (
  -- In practice, embed the query text via OpenAI API
  SELECT embedding FROM rag_chunks
  WHERE chunk_text ILIKE '%seismic zone%' LIMIT 1
)
SELECT
  rc.id,
  rc.chunk_text,
  rc.source_doc_id,
  rc.phase_code,
  rc.doc_type,
  (0.6 * (1 - (rc.embedding <=> qe.embedding))
   + 0.3 * 0.5
   + 0.1 * rc.chunk_relevance_weight) AS final_score
FROM rag_chunks rc, query_embed qe
WHERE rc.collection_key = 'rod:seism:design'
  AND rc.phase_code IN ('D6.1', 'D6.2')
ORDER BY final_score DESC
LIMIT 5;
```

### Query D6.1-002: Site Soil Classification

**Query Text:**
```
"Classify the soil type at the site using SPT (Standard Penetration Test) 
results. What is the shear wave velocity (Vs30)?"
```

**Expected Results:**
- Collection: `rod:seism:geotechnical`, `rod:seism:design`
- Phase: D6.1–D6.2
- Content Types: Technical procedure (60%), Normative (40%)
- Top Documents: ABNT NBR 6122, ABNT NBR 7250, EN 1998-1

**Acceptance Criteria:**
- [ ] Result count: 3–6
- [ ] Avg top-1 score: ≥ 0.70
- [ ] Phase accuracy: ≥ 85%
- [ ] Latency: ≤ 450ms
- [ ] Expert review: ≥ 4.0/5.0

---

## 3. PHASE D6.2 QUERIES (Basic Design / Projeto Básico)

### Query D6.2-001: Design Response Spectrum Calculation

**Query Text:**
```
"Calculate the design response spectrum (Sa, Sv, Sd) for periods T = 0.1s, 
0.3s, 1.0s, 2.0s using USGS hazard data for a site with soil class C 
and damping ratio 5%. Include seismic factor and response modification."
```

**Expected Results:**
- Collection: `rod:seism:design` (100%)
- Phase: D6.2 (primary), D6.1 (secondary)
- Content Types: Formula-heavy (70%), Table reference (20%), Text (10%)
- Top Documents: EN 1998-1, NBR 15421, USGS Hazard Maps

**Acceptance Criteria:**
- [ ] Result count: 4–8
- [ ] Avg top-1 score: ≥ 0.80 (spectrum calculation is critical)
- [ ] Content type accuracy: ≥ 90% formula/table chunks
- [ ] Phase accuracy: ≥ 95% D6.2 chunks
- [ ] Latency: ≤ 350ms (formula chunks should be found fast)
- [ ] Expert review: ≥ 4.5/5.0 (correctness is critical)
- [ ] Contains spectral ordinates or calculation procedure

**Query-Specific Validation:**
```sql
-- Verify formula chunks ranked highest
WITH results AS (
  SELECT * FROM query_rag_chunks(
    query_embedding => (embeddings of query text),
    query_phase => 'D6.2',
    collection_keys => ARRAY['rod:seism:design'],
    limit_count => 5
  )
)
SELECT
  COUNT(*) FILTER (WHERE is_formula) AS formula_chunks,
  COUNT(*) FILTER (WHERE is_table) AS table_chunks,
  COUNT(*) AS total_chunks,
  ROUND(100.0 * COUNT(*) FILTER (WHERE is_formula) / COUNT(*), 1) AS pct_formula
FROM results;
-- Expected: pct_formula >= 70%
```

### Query D6.2-002: Ground Motion Selection

**Query Text:**
```
"Select and scale earthquake ground motion records for nonlinear time 
history analysis. What are the criteria for record selection based on 
magnitude, distance, and site classification?"
```

**Expected Results:**
- Collection: `rod:seism:design`, `rod:seism:analysis`
- Phase: D6.2–D6.4
- Content Types: Technical guide (60%), Normative (40%)
- Top Documents: FEMA P440B, ASCE 7, EN 1998-1

**Acceptance Criteria:**
- [ ] Result count: 4–7
- [ ] Avg top-1 score: ≥ 0.75
- [ ] Phase accuracy: ≥ 85% (D6.2, D6.3, D6.4)
- [ ] Latency: ≤ 400ms
- [ ] Expert review: ≥ 4.0/5.0

---

## 4. PHASE D6.3 QUERIES (Structural Design / Projeto Executivo)

### Query D6.3-001: Reinforcement Detailing for Seismic Design

**Query Text:**
```
"Design column reinforcement for seismic loads. What are the ductility 
requirements, spacing of transverse reinforcement (stirrups), and 
confinement criteria? Include lap splice length calculations."
```

**Expected Results:**
- Collection: `rod:seism:structure` (90%), `rod:seism:design` (10%)
- Phase: D6.3 (primary), D6.4 (secondary)
- Content Types: Detailing guide (50%), Formula (30%), Table (20%)
- Top Documents: ACI 318-19 (Ch. 18), EN 1998-2, ASCE 7

**Acceptance Criteria:**
- [ ] Result count: 5–10
- [ ] Avg top-1 score: ≥ 0.75
- [ ] Content type accuracy: ≥ 80% (formula + detailing chunks)
- [ ] Phase accuracy: ≥ 85%
- [ ] Latency: ≤ 400ms
- [ ] Expert review: ≥ 4.5/5.0
- [ ] Includes lap splice length method and confinement details

**Detailed Validation:**
```sql
-- Verify detailing guidance in top results
WITH results AS (
  SELECT * FROM query_rag_chunks(...)
)
SELECT
  source_doc_id,
  phase_code,
  final_score,
  CASE
    WHEN chunk_text ILIKE '%lap splice%' THEN 'Contains lap splice guidance'
    WHEN chunk_text ILIKE '%stirrup%' THEN 'Contains stirrup spacing'
    WHEN chunk_text ILIKE '%confinement%' THEN 'Contains confinement rules'
    ELSE 'General detailing'
  END AS guidance_type
FROM results
ORDER BY final_score DESC;
```

### Query D6.3-002: Concrete Member Shear Design

**Query Text:**
```
"Calculate shear reinforcement for a seismic moment frame beam. 
Include capacity design procedures and brittleness checks."
```

**Expected Results:**
- Collection: `rod:seism:structure`, `rod:seism:design`
- Phase: D6.3
- Content Types: Formula (40%), Technical guide (40%), Example (20%)
- Top Documents: ACI 318, EN 1998-2

**Acceptance Criteria:**
- [ ] Result count: 3–6
- [ ] Avg top-1 score: ≥ 0.70
- [ ] Phase accuracy: ≥ 90%
- [ ] Latency: ≤ 400ms
- [ ] Expert review: ≥ 4.0/5.0
- [ ] Includes capacity design methodology

---

## 5. PHASE D6.4 QUERIES (Seismic Analysis)

### Query D6.4-001: Nonlinear Time History Analysis in SAP2000

**Query Text:**
```
"Set up a nonlinear time history analysis in SAP2000 for a moment-resisting 
frame structure. Define plastic hinge properties, damping model, and 
ground motion record application. Include acceptance criteria for 
structural performance (chord rotation limits)."
```

**Expected Results:**
- Collection: `rod:seism:analysis` (90%), `rod:seism:structure` (10%)
- Phase: D6.4 (primary), D6.3 (secondary)
- Content Types: Software guide (50%), Technical procedure (40%), Formula (10%)
- Top Documents: SAP2000 User Manual, FEMA P440B, ACI 318

**Acceptance Criteria:**
- [ ] Result count: 5–10
- [ ] Avg top-1 score: ≥ 0.80 (analysis procedure is critical)
- [ ] Phase accuracy: ≥ 95%
- [ ] Latency: ≤ 450ms (larger chunks for detailed procedures)
- [ ] Expert review: ≥ 4.5/5.0
- [ ] Includes hinge properties, damping definition, acceptance criteria
- [ ] SAP2000-specific guidance present

**Step-by-Step Validation:**
```python
# Pseudo-code for validation
results = query_rag("Set up nonlinear time history...", phase="D6.4")

validations = {
    "result_count": 5 <= len(results) <= 10,
    "avg_top_score": avg([r.final_score for r in results[:3]]) >= 0.80,
    "phase_d64_pct": sum(1 for r in results if r.phase_code == "D6.4") / len(results) >= 0.95,
    "contains_hinge_guidance": any("hinge" in r.text.lower() for r in results),
    "contains_damping_guidance": any("damping" in r.text.lower() for r in results),
    "contains_sap2000_guidance": any("sap2000" in r.text.lower() for r in results),
    "latency_ms": < 450
}

# All validations must pass
assert all(validations.values()), f"Failed: {validations}"
```

### Query D6.4-002: Pushover Analysis and Capacity Curve

**Query Text:**
```
"Perform a pushover analysis to generate the capacity curve (base shear 
vs. roof displacement) and identify the performance point. What are the 
acceptance criteria for interstorey drift and member ductility?"
```

**Expected Results:**
- Collection: `rod:seism:analysis`, `rod:seism:structure`
- Phase: D6.4
- Content Types: Technical procedure (60%), Formula (30%), Example (10%)
- Top Documents: FEMA P440B, ATC-40, SAP2000 Manual

**Acceptance Criteria:**
- [ ] Result count: 4–8
- [ ] Avg top-1 score: ≥ 0.75
- [ ] Phase accuracy: ≥ 90%
- [ ] Latency: ≤ 450ms
- [ ] Expert review: ≥ 4.0/5.0

---

## 6. PHASE D6.5–D7.5 QUERIES (Execution & Monitoring)

### Query D6.5-001: Construction Quality Control

**Query Text:**
```
"Quality control specifications for reinforcement placement and concrete 
compaction. What are the acceptance criteria for compressive strength, 
rebar placement tolerance, and cover verification?"
```

**Expected Results:**
- Collection: `rod:seism:structure` (80%), `rod:seism:design` (20%)
- Phase: D6.5–D7.2
- Content Types: Standard procedure (70%), Specification (30%)
- Top Documents: ABNT NBR 12655, ACI 318, EN 1998-1

**Acceptance Criteria:**
- [ ] Result count: 3–7
- [ ] Avg top-1 score: ≥ 0.70
- [ ] Phase accuracy: ≥ 80%
- [ ] Latency: ≤ 400ms
- [ ] Expert review: ≥ 4.0/5.0

### Query D7.2-001: Structural Health Monitoring Installation

**Query Text:**
```
"Install accelerometers and displacement transducers for structural health 
monitoring (SHM). Specify sensor placement, data acquisition frequency, 
and real-time monitoring thresholds for seismic events."
```

**Expected Results:**
- Collection: `rod:seism:analysis`, `rod:seism:structure`
- Phase: D7.2–D7.5
- Content Types: Technical procedure (60%), Design procedure (40%)
- Top Documents: FEMA guidelines, IEEE standards, SAP2000 monitoring tools

**Acceptance Criteria:**
- [ ] Result count: 3–6
- [ ] Avg top-1 score: ≥ 0.65 (less standardized phase)
- [ ] Phase accuracy: ≥ 75%
- [ ] Latency: ≤ 450ms
- [ ] Expert review: ≥ 3.5/5.0 (less critical phase)

---

## 7. CROSS-PHASE VALIDATION

### Test CX-001: Phase Proximity Weighting Correctness

**Purpose:** Verify that phase proximity matrix is working correctly

**Test Procedure:**
```sql
-- Query with D6.2, expect D6.2 results first, then D6.1, D6.3
SELECT
  row_number() OVER (ORDER BY final_score DESC) AS rank,
  phase_code,
  final_score,
  CASE
    WHEN phase_code = 'D6.2' THEN 'Target phase'
    WHEN phase_code IN ('D6.1', 'D6.3') THEN 'Adjacent phase'
    ELSE 'Distant phase'
  END AS phase_type
FROM query_rag_chunks(
  query_embedding => ...,
  query_phase => 'D6.2',
  collection_keys => ARRAY['rod:seism:design', 'rod:seism:structure'],
  limit_count => 20
);
```

**Expected Pattern:**
```
Rank 1–5: Mostly D6.2 (ideal: 100%, acceptable: ≥80%)
Rank 6–10: Mix of D6.1, D6.2, D6.3 (acceptable)
Rank 11–20: Wider range (D6.4, D7.x allowed but low-ranked)
```

**Acceptance Criteria:**
- [ ] Top-5 results: ≥ 80% from target phase
- [ ] Ranks 6–10: ≥ 50% from adjacent phases (±1)
- [ ] No distant phases (D6.1 for D6.4 query) in top-10

### Test CX-002: Content Type Boost Verification

**Purpose:** Verify that formula and table chunks are boosted appropriately

**Test Procedure:**
```sql
-- Query for design formula, expect is_formula=TRUE chunks ranked high
WITH formula_query AS (
  SELECT * FROM query_rag_chunks(
    query_embedding => (embed query about spectral ordinate formula),
    query_phase => 'D6.2',
    collection_keys => ARRAY['rod:seism:design'],
    limit_count => 10
  )
)
SELECT
  is_formula,
  is_table,
  COUNT(*) AS count,
  AVG(final_score) AS avg_score,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM formula_query
GROUP BY is_formula, is_table
ORDER BY avg_score DESC;
```

**Expected Results:**
```
is_formula=TRUE: ~70% of results, avg_score ≥ 0.75
is_table=TRUE:   ~15% of results, avg_score ≥ 0.70
is_formula=FALSE: ~15% of results, avg_score ≤ 0.65
```

**Acceptance Criteria:**
- [ ] is_formula chunks: ≥ 60% of results
- [ ] is_formula avg_score: ≥ 0.70
- [ ] is_formula avg_score > is_table avg_score

### Test CX-003: Relevance Feedback Loop

**Purpose:** Ensure user ratings are captured and tracked

**Test Procedure:**
```sql
-- Log a query with user rating
INSERT INTO rag_query_logs (
  collection_key, query_text, returned_chunk_count, 
  query_latency_ms, top_score, user_rating, feedback_notes
) VALUES (
  'rod:seism:design',
  'Design response spectrum calculation',
  5,
  245,
  0.82,
  5,
  'Excellent results, found spectral formula immediately'
);

-- Retrieve feedback for continuous improvement
SELECT
  collection_key,
  AVG(user_rating) AS avg_rating,
  COUNT(*) AS feedback_count,
  MAX(created_at) AS latest_feedback
FROM rag_query_logs
WHERE user_rating IS NOT NULL
GROUP BY collection_key;
```

**Acceptance Criteria:**
- [ ] Feedback logging works without errors
- [ ] Average user rating: ≥ 4.0/5.0
- [ ] ≥ 50% of queries logged with rating by end of week 1

---

## 8. PERFORMANCE BENCHMARKS

### Query Latency (p95)

| Phase | Expected Latency | Acceptable Range |
|---|---|---|
| D6.1 | 300ms | 200–450ms |
| D6.2 | 350ms | 250–500ms |
| D6.3 | 350ms | 250–500ms |
| D6.4 | 400ms | 300–550ms |
| D6.5–D7.5 | 350ms | 250–500ms |

### Relevance Score Distribution

| Phase | Avg Top-1 Score | Acceptable Range |
|---|---|---|
| D6.1 | 0.75 | 0.70–0.85 |
| D6.2 | 0.80 | 0.75–0.90 |
| D6.3 | 0.75 | 0.70–0.85 |
| D6.4 | 0.80 | 0.75–0.90 |
| D6.5–D7.5 | 0.70 | 0.65–0.80 |

---

## 9. FAILURE INVESTIGATION GUIDE

### Symptom: Low Top-1 Score (< 0.70)

**Diagnostic Steps:**
1. Check if query text is clear and specific (not ambiguous)
2. Verify embedding generation used correct model (text-embedding-3-small)
3. Check phase_code matches expected collection phase range
4. Review query logs: is user rating low? (suggests genuine relevance issue)

**Remediation:**
- Adjust chunk_relevance_weight for low-scoring document type
- Increase phase_proximity_weight for frequently queried phases
- Re-review manual chunking for documents producing low scores

### Symptom: High Latency (> 500ms)

**Diagnostic Steps:**
1. Check Supabase CPU usage during query
2. Verify IVFFlat index exists and is healthy: `REINDEX idx_rag_chunks_embedding;`
3. Check query log volume: if > 100 concurrent, scale read replicas
4. Review query plan: `EXPLAIN ANALYZE` the query

**Remediation:**
- Increase lists parameter in IVFFlat: `lists = 200`
- Add connection pooling (pgBouncer) if connection overhead is high
- Consider materialized view for high-traffic queries

### Symptom: Phase Proximity Not Working

**Diagnostic Steps:**
1. Verify phase_proximity_weight() function returns correct values
2. Check that query_phase parameter is passed correctly
3. Confirm phase_code column populated for all chunks

**Remediation:**
```sql
-- Test phase function directly
SELECT phase_proximity_weight('D6.2', 'D6.2') AS same_phase,
       phase_proximity_weight('D6.3', 'D6.2') AS adj_phase,
       phase_proximity_weight('D7.1', 'D6.2') AS dist_phase;
-- Expected: 1.0, 0.9, 0.3
```

---

## 10. TEST EXECUTION CHECKLIST

### Pre-Test

- [ ] Staging database populated with 78+ documents and ~4,000 chunks
- [ ] All 6 test users have embedding API access
- [ ] Test suite scripts have environment variables set (SUPABASE_URL, etc.)
- [ ] Query logs table is empty (fresh baseline)

### During Test

- [ ] Execute each phase's queries (D6.1, D6.2, D6.3, D6.4, D6.5–D7.5)
- [ ] Record latency, score, result count, phase accuracy
- [ ] Capture expert review scores (1–5 scale)
- [ ] Monitor database performance (CPU, disk, connections)

### Post-Test

- [ ] Aggregate results in test report
- [ ] Compare against acceptance criteria
- [ ] Flag any failures for investigation
- [ ] Generate recommendations for tuning

### Final Sign-Off

- [ ] All critical queries (D6.1–D6.4) pass with ≥ 80% criteria met
- [ ] No latency violations (> 500ms p95)
- [ ] Expert review avg ≥ 4.0/5.0
- [ ] Production ready: ✓ or ✗

---

**Test Report Template Location:** `/reports/rag_test_report_[DATE].md`  
**Queries Executed:** [Count]  
**Pass Rate:** [%]  
**Date Completed:** [AUTO-POPULATED]  
**Signed Off By:** [CTO/Tech Lead]
