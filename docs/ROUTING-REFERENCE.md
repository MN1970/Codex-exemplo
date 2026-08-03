# Routing Reference — R1 Maestro (v5.0)

**Complete specification of the Maestro (Manta 00) routing engine.**

---

## Overview

The Maestro is the canonical router that receives every user prompt, applies routing
rules (R1), and delegates to the appropriate agent with configuration injection.

**Three-stage pipeline:**
1. Keyword matching + embedding similarity
2. Context injection (phase, files, window allocation)
3. Tiering decision (R7) + fallback setup (R8)

---

## Stage 1 — Keyword Matching + Embedding

### Input

```json
{
  "prompt": "Preciso de ajuda com uma ETA em São Paulo",
  "user_id": "mneves@mantaassociados.com",
  "session_id": "sess_abc123",
  "context_hints": [],
  "file_context": [
    {"name": "projeto.dwg", "size_mb": 2.1}
  ]
}
```

### Keyword Extraction

Extract key terms from prompt:
- Exact matches: "ETA", "São Paulo"
- Fuzzy matches: "saneamento" (topic area)
- Acronyms: expand "ETA" → "Estação de Tratamento de Água"

### BM25 Lookup

For each RAG collection, compute BM25 relevance:

```
collections = {
  "san:v5.0": 0.95,   ← Highest relevance (keywords match)
  "ene:v5.0": 0.05,
  "por:v5.0": 0.08,
  "aer:v5.0": 0.02,
  "bar:v5.0": 0.03,
  "rod:v5.0": 0.01,
  ...
}
```

### Embedding Similarity

Embed prompt using e5-large-instruct, compare to agent profile embeddings:

```
agent_similarity = {
  "agente-saneamento": 0.92,
  "agente-energia": 0.15,
  "agente-portos": 0.08,
  ...
}
```

### Candidate Ranking

Score = `0.4 × keyword_relevance + 0.4 × embedding_sim + 0.15 × rag_score + 0.05 × history`

If top candidate score - runner-up score > 0.15, proceed to Stage 2.
If gap < 0.15, return ambiguity (request clarification).

---

## Stage 2 — Context Injection

### Phase Inference

Check if prompt contains phase hints:
- "básico" / "conceitual" → **projeto-basico**
- "executivo" / "detalhado" → **projeto-executivo**
- "obra" / "construção" / "execução" → **obra-em-execucao**
- "operação" / "O&M" → **operacao**
- "licitação" / "edital" → **licitacao**
- "due diligence" / "auditoria" → **due-diligence**
- "encerramento" / "desativação" → **encerramento**
- (default) → **estudo-previo**

### File Processing

If files detected:
- Set `file_processing=true`
- Allocate additional tokens: `window_tokens += files.count * 1000`
- Pass file metadata to agent skill

### RAG Collection Pin

Based on routing decision, pin RAG collection:
- agente-saneamento → san:v5.0:chunks
- agente-energia → ene:v5.0:chunks
- agente-portos → por:v5.0:chunks
- agente-aeroportos → aer:v5.0:chunks
- agente-barragens → bar:v5.0:chunks

### Context Window Allocation

```
base_window = 4000 tokens

IF file_processing:
  window_tokens = base_window + (files.count * 1000)
  # Max: 16000 (Opus limit - safety margin)

IF phase in ["projeto-executivo", "due-diligence", "licitacao"]:
  window_tokens = min(window_tokens * 1.2, 16000)

IF cross_agent_references:
  window_tokens = min(window_tokens * 1.15, 16000)
```

---

## Stage 3 — Tiering & Fallback Setup

### Complexity Score (R7)

```
complexity = compute_complexity_score(
  input_tokens=prompt.token_count(),
  keywords_matched=len(keywords),
  rag_reranker_score_max=rag_scores.max(),
  files_to_process=len(files),
  cross_agent_references=cross_refs,
  phase=inferred_phase
)
```

See `CLAUDE.md apêndice` for formula.

### Tier Decision

```
IF input_tokens < 2000 AND complexity < 3.0:
  model_tier = "haiku-4-5"
  fallback_tier = "sonnet-5"

ELIF input_tokens < 10000 AND complexity < 6.0:
  model_tier = "sonnet-5"
  fallback_tier = "opus-5"

ELSE:
  model_tier = "opus-5"
  fallback_tier = "opus-5"  # No fallback (already max)
```

### Fallback Configuration (R8)

```json
{
  "model_tier": "sonnet-5",
  "fallback_tier": "opus-5",
  "timeout_sec": 60,
  "max_retries": 1,
  "preserve_context": true
}
```

---

## Output Routing

### Maestro Output

```json
{
  "agent_id": "manta-03-s8",
  "agent_name": "agente-saneamento",
  "skill_ids": ["agente-saneamento.v5.0", "autodesk-toolkit"],
  "config": {
    "model_tier": "haiku-4-5",
    "fallback_tier": "sonnet-5",
    "max_tokens": 2048,
    "temperature": 0.7,
    "context_window_tokens": 8000
  },
  "context_injection": {
    "phase": "projeto-executivo",
    "file_processing": true,
    "rag_collection": "san:v5.0:chunks",
    "skill_version_pin": "v5.0"
  },
  "routing_confidence": 0.90,
  "routing_logs": {
    "bm25_score": 0.95,
    "embedding_similarity": 0.92,
    "complexity_score": 2.8,
    "candidate_runner_up": "agente-energia",
    "runner_up_score": 0.15
  }
}
```

This output is injected into the skill execution context.

---

## Keyword Rules — Complete Specification

### S8 — SANEAMENTO

**Keywords (partial list):**
```
saneamento, ETA, ETE, adutora, esgoto, água tratada, AySA, drenagem,
macrodrenagem, SNIS, PMSB, Lei 14.026, subsídio cruzado, elevatória,
reservatório, RAP, EEE, EEAB, reúso, lodo, digestor, UASB, MBR,
bombeamento, tratamento, captação, recalque, condomínio, unifamiliar,
tarifa, acesso à água, coleta de esgoto, emissário, interceptor,
ETAR, flotação, decantação, lagoa, biofiltro
```

**Multi-keyword boost:**
```
IF keywords.count >= 2 AND "ETA|ETE|AySA" in keywords:
  relevance += 0.2  # High confidence
```

---

### S9 — ENERGIA

**Keywords (partial list):**
```
transmissão, LT, subestação, ANEEL, RAP, leilão, ONS, EPE, PDE, R1-R5,
torre, cabo, ACSR, CAA, ATSR, MRE, ACR, ACL, WEG, State Grid,
ISA CTEEP, Alupar, Taesa, geração, eólica, PV, hidráulica, PCH, UHE,
usina, térmica, nuclear, CCGT, despachador, contratos bilaterais,
ambiente livre, carga, perfil de consumo, fator de carga, demanda
```

**Regulatory boosters:**
```
IF "ANEEL" in keywords:
  relevance += 0.3
IF "leilão" AND "transmissão" in keywords:
  agent_priority = "HIGH"
```

---

### S6 — PORTOS

**Keywords (partial list):**
```
porto, terminal, ANTAQ, dragagem, molhe, quebra-mar, berço, calado,
contêiner, granel, cais, píer, retroárea, pátio, TUP, TPS, PIANC,
arrendamento, hidrovia, navios, cabotagem, longo-curso, fluvial,
marítimo, acostagem, bóia, farol, batimetria, zona portuária,
operador portuário, bunkering, cabotagem, cabos submarinos
```

---

### S7 — AEROPORTOS

**Keywords (partial list):**
```
aeroporto, pista, RWY, taxiway, TWY, pátio, TPS, TECA, ANAC, RBAC,
ICAO, Annex 14, FAA, balizamento, PAPI, ILS, PCN, gate, jetway,
ponte, embarque, desembarque, aviação, regional, geral, concessão,
corredor, aproximação, decolagem, sinalização, radar, beacon, DME
```

---

### S10 — BARRAGENS

**Keywords (partial list):**
```
barragem, vertedouro, CFRD, CCR, RCC, rejeitos, TSF, PNSB, ICOLD,
CBDB, dique, SIGBM, ANM, ANA, Lei 12.334, Fundão, Brumadinho,
descomissionamento, alteamento, montante, jusante, linha-centro,
filtragem, dry-stack, PAE, PAEBM, ZAS, ZSS, HHP, piping, galgamento,
liquefação, seepage, piezômetro, instrumentação, hydrologic routing
```

---

### S1–S4 (Existing — unchanged)

See CLAUDE.md section "ROUTING — REGRAS ATUALIZADAS (R1)".

---

## Ambiguity Resolution

If top-2 candidates within 0.15 confidence gap:

```json
{
  "status": "ambiguous",
  "candidates": [
    {
      "agent_id": "manta-03-s8",
      "agent_name": "agente-saneamento",
      "confidence": 0.62
    },
    {
      "agent_id": "manta-03-s9",
      "agent_name": "agente-energia",
      "confidence": 0.58
    }
  ],
  "clarification_request": "Seu projeto envolve saneamento ou energia? Ou ambos?"
}
```

User selects agent, routing re-executes with explicit hint.

---

## Caching & Optimization

### Query Cache (R6)

Recent queries (< 7 days) cached with top-5 reranked RAG results:

```
cache_key = hash(prompt, agent_id)
IF cache_key in rag_cache AND ttl_valid:
  return cached_results  # ~1ms vs 20ms
```

### Agent Profile Embeddings

Stored offline in Qdrant:
```
collection: "agent-profiles"
documents: 20 agent descriptions
updated: weekly (after feedback loop R9)
```

---

## Monitoring & Alerts

### Metrics

- **Routing accuracy:** % of runs with routing_confidence > 0.85
- **Ambiguity rate:** % of prompts requiring clarification
- **Fallback rate:** % of runs using fallback tier (R8)
- **RAG cache hit rate:** % of queries served from cache

### Alerts

- Routing accuracy < 90% → Review keyword rules
- Fallback rate > 5% → Adjust tiering thresholds (R7)
- RAG cache hit < 30% → Increase TTL or reindex

---

## Testing

### Unit Tests

```python
def test_keyword_extraction():
    prompt = "ETA em São Paulo"
    keywords = extract_keywords(prompt)
    assert "ETA" in keywords
    assert "saneamento" in keywords

def test_rag_lookup():
    keywords = ["ETA", "AySA"]
    scores = bm25_lookup(keywords)
    assert scores["san:v5.0"] > 0.9

def test_tier_decision():
    complexity = 2.5
    tokens = 1200
    tier = decide_tier(tokens, complexity)
    assert tier == "haiku-4-5"
```

### Integration Tests

```bash
# Test prompt → agent mapping
pytest tests/routing/test_end_to_end.py -v

# Test all S6–S10 agents route correctly
pytest tests/routing/test_vertical_agents.py -v

# Performance benchmark
pytest tests/routing/test_latency.py --benchmark
# Expected: < 500ms total (keyword + embedding + context)
```

---

## Troubleshooting

| Issue | Root cause | Fix |
|-------|-----------|-----|
| Wrong agent routed | Keyword mismatch | Add keywords to CLAUDE.md R1 section |
| High routing latency | Embedding model slow | Use cached embeddings or reduce dimensionality |
| Ambiguity too frequent | Keywords too generic | Split into sub-keywords, add negation rules |
| Fallback triggered often | Tiering too aggressive | Increase complexity threshold (3.0 → 3.5) |

---

**End of R1 Routing Reference**
