# Arquitetura Manta Maestro v5.0 — Os 8 Pilares

**Especificação detalhada da arquitetura v5.0, com foco nos 8 pilares que sustentam
a plataforma de agentes IA.**

---

## Sumário Executivo

Manta Maestro v5.0 é uma plataforma escalável de agentes IA fundamentada em
**8 pilares arquiteturais**:

1. **Routing Determinístico** — Maestro (R1) roteia prompts com 90%+ confiança
2. **Qualidade Vertical** — 5 novos agentes (S6–S10) com ciclo de vida 8 fases
3. **Ciclo de Vida** — Intake declarativo: estudo prévio → encerramento
4. **RAG Híbrido** — BM25 + embedding + reranker (R6) em <50ms
5. **Tiering Automático** — R7 escolhe Haiku/Sonnet/Opus via complexity score
6. **Observabilidade** — Run tracking imutável, custos, latência, feedback
7. **Orquestração Async** — APScheduler: reindex, feedback, purge diárias
8. **Versionamento de Skills** — Checksums MD5, rollback automático, grace period 30d

**Target:** Suportar 50+ agentes com custo 30% menor e latência p95 < 5s.

---

## P1 — Routing Determinístico (Maestro / R1)

### Objetivo

Todo prompt deve ser roteado ao agente correto com **routing_confidence ≥ 0.85**.

Fallback: se confiança < 0.85, retorna ambiguidade e solicita clarificação.

### Mecanismo (3 estágios)

**Estágio 1: Keyword extraction + BM25 + embedding**
- Parse prompt → keywords
- BM25 lookup em todas as coleções RAG
- Embedding similarity vs. 20 agent profiles
- Score: `0.4 × kw_relevance + 0.4 × emb_sim + 0.15 × rag + 0.05 × history`

**Estágio 2: Context injection**
- Infer phase (estudo → projeto-executivo → obra → etc.)
- Detectar file processing (DWG, PDF)
- Allocate context window (4k–16k tokens)
- Pin RAG collection (san:v5.0 vs ene:v4.9, etc.)

**Estágio 3: Tiering + fallback**
- Compute complexity score (R7)
- Decide tier: Haiku vs Sonnet vs Opus
- Setup fallback cascade (R8)

### Garantias

- **Latência:** < 500ms (keyword + embedding + context)
- **Confiança:** ≥ 85% routing accuracy (audit via tiering-audit.py)
- **Reproducibilidade:** Mesmo prompt → mesmo agente (hash-based)

### Monitoramento

```sql
SELECT 
  agent_id, 
  COUNT(*) as runs,
  AVG(routing_confidence) as avg_confidence,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency
FROM agent_runs
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY agent_id
ORDER BY runs DESC;
```

---

## P2 — Qualidade Vertical (5 novos agentes S6–S10)

### S6 — Portos (ANTAQ, PIANC)

**Escopo:** Estudos prévios, projetos, licitação de terminais portuários.

**Skills v5.0:**
- Análise de calado e capacidade
- Cálculo de dragagem
- PIANC wave climate analysis
- Retroárea & pátio design

**RAG:** por:v5.0:chunks (2000+)

---

### S7 — Aeroportos (ANAC/RBAC)

**Escopo:** Pistas, TPS, TECA, balizamento, concessões.

**Skills v5.0:**
- Cálculo de PCN (Pavement Classification Number)
- Design de taxiways (ICAO Annex 14)
- SIL (Safety Integrity Level) para sistemas de guia

**RAG:** aer:v5.0:chunks (1800+)

---

### S8 — Saneamento (AySA, Lei 14.026)

**Escopo:** ETAs, ETEs, adução, esgotamento, drenagem urbana. PRIORIDADE AySA.

**Skills v5.0:**
- Dimensionamento de estações (ABNT NBR 12211-12218)
- Cálculo de OPEX (subsídio cruzado)
- Tratamento avançado (UASB, MBR, DAF)

**RAG:** san:v5.0:chunks (2500+) — maior coleção

---

### S9 — Energia (ANEEL, State Grid)

**Escopo:** Transmissão (LT), subestações, geração, licitações ANEEL.

**Skills v5.0:**
- Cálculo de capacidade termal (ACSR, CAA)
- Fluxo de potência (power flow)
- Econômico: RAP (Receita Anual Permitida), MRE (Mecanismo de Realocação)

**RAG:** ene:v5.0:chunks (3000+)

---

### S10 — Barragens (ICOLD, Lei 12.334)

**Escopo:** Barragens de terra/concreto, rejeitos, PAE, desativação.

**Skills v5.0:**
- CFRD (Concrete Face Rockfill Dam) design
- TSF (Tailings Storage Facility) estabilidade
- Instrumentação & monitoramento

**RAG:** bar:v5.0:chunks (2200+)

---

### Skill Versioning (P8)

Cada skill pinned a v5.0:
```json
{
  "skill_version_pin": {
    "agente-saneamento": "v5.0",  // checksum: f1a3d2b4...
    "agente-energia": "v5.0"       // checksum: e2b5c3a1...
  }
}
```

Checksums validados em `.claude/agents/VERSIONS.json` (immutable).

---

## P3 — Ciclo de Vida (8 fases)

### Phases Supported

```
1. ESTUDO PRÉVIO
   Input: Brief, benchmarks
   Output: Diagnóstico, viabilidade order-of-magnitude
   Duration: 2–4 weeks
   Agents: Primarily S1–S10 + advisory (15)

2. PROJETO BÁSICO
   Input: Budget, preliminary specs
   Output: Layouts, order-of-magnitude CAPEX, schedule rough
   Duration: 4–8 weeks
   Agents: S1–S10 + modeling (06)

3. PROJETO EXECUTIVO
   Input: Approved concepts
   Output: CAD 100%, specs, detailed CAPEX/schedule
   Duration: 8–16 weeks
   Agents: S1–S10 + autodesk-toolkit

4. OBRA EM EXECUÇÃO
   Input: Daily reports, desvios
   Output: Variance analysis, schedule recovery
   Duration: Variable (1–5 years)
   Agents: S1–S10 + cronograma (07)

5. OPERAÇÃO & MANUTENÇÃO
   Input: KPIs, maintenance logs
   Output: OPEX optimization, predictive maintenance
   Duration: 20+ years
   Agents: S1–S10 + bd (13)

6. LICITAÇÃO / PROCESSO COMPETITIVO
   Input: Especificações
   Output: Edital, termo de referência, avaliação
   Duration: 3–6 months
   Agents: S1–S10 + contratual (02) + bd (13)

7. DUE DILIGENCE / M&A
   Input: Projeto existente
   Output: Auditoria financeira, legal, ambiental, riscos
   Duration: 2–4 months
   Agents: S1–S10 + advisory (15) + claims (01)

8. ENCERRAMENTO / DESCOMISSIONAMENTO
   Input: EOL decision
   Output: Plano de desativação, remediação, passivos
   Duration: 6–12 months
   Agents: S1–S10 + ambiental (skill TBD)
```

### Intake Declarativo

Usuário informa fase:
```json
{
  "phase": "projeto-executivo",
  "segment": "s8",
  "deliverables": [
    "memorial-descritivo.pdf",
    "projeto-estrutural.dwg"
  ]
}
```

Maestro infere via embedding se ausente.

---

## P4 — RAG Híbrido (BM25 + Embedding + Reranker)

### Arquitetura

```
Query: "Qual o custo de uma ETA em São Paulo?"
  ↓
[1] BM25 Lookup (Elasticsearch)
    san:v5.0 → relevance 0.95
    [SNIS doc, Lei 14.026, AySA case]
  ↓
[2] Embedding Search (Qdrant/Pinecone)
    embed(query) → similarity 0.92
    [Tratamento água, custo capex]
  ↓
[3] Union + Dedup
    20 unique chunks (top-10 BM25 + top-10 embedding)
  ↓
[4] Reranker (R6 Cross-encoder)
    Infinity (intfloat/multilingual-e5-large)
    Top-5 reranked: score > 0.5
  ↓
Agent receives: Top-5 results (relevance 0.65–0.95)
```

### Latência SLA

- BM25: 1–2ms
- Embedding: 5–10ms
- Reranker: 10–20ms
- Cache hit: 1ms
- **Total:** < 50ms p95

### Cache Policy (R6)

```
cache_key = hash(query, agent_id)
cache_ttl = 7 days

IF cache_hit AND (NOW - cache_time) < ttl:
  return cached_reranked_results  # 1ms
ELSE:
  compute full pipeline
  store in rag_cache (Supabase)
```

---

## P5 — Tiering Automático (Complexity Score + R7)

### Formula

```python
complexity = (
  keywords_matched * 1.0 +
  (rag_reranker_score_max > 0.7 ? 2.0 : (score > 0.5 ? 1.0 : 0)) +
  files_to_process * 1.5 +
  cross_agent_references * 1.0
) × phase_multiplier[phase]

# Phase multipliers
estudo-previo: 0.5
projeto-basico: 0.8
projeto-executivo: 1.2
obra: 1.0
operacao: 0.7
licitacao: 1.1
due-diligence: 1.3
encerramento: 0.9
```

### Decision Tree

```
IF input_tokens < 2000 AND complexity < 3.0:
  model_tier = "haiku-4-5"       # cost: $0.08/1M
ELIF input_tokens < 10000 AND complexity < 6.0:
  model_tier = "sonnet-5"        # cost: $3/1M
ELSE:
  model_tier = "opus-5"          # cost: $15/1M
```

### Fallback Cascade (R8)

```
1. Submit to model_tier
2. IF timeout after 60s:
   - Log: {run_id, model_tier, latency_ms, timeout=true}
   - Resubmit with fallback_tier (next level up)
   - Inject previous context (RAG results, partial output)
   - Set max_tokens = 1500 (reduced scope)
3. IF fallback also timeout:
   - Alert #agent-ops
   - Return best-effort partial output
```

### Cost Savings

Expected savings vs. always-Opus: **45–65%**

```
Baseline (v4.2): 100% Sonnet → avg $0.08/run
v5.0 with tiering:
  - 60% Haiku: 0.60 × $0.008 = $0.0048
  - 30% Sonnet: 0.30 × $0.08 = $0.024
  - 10% Opus: 0.10 × $0.40 = $0.040
  Total: $0.0688/run → 14% savings

Plus Haiku improvements (better for structured tasks):
  Realistic: 30–45% savings over mixed Sonnet/Opus
```

---

## P6 — Observabilidade (Run Tracking + Custos)

### Agent Runs (Immutable Log)

```sql
CREATE TABLE agent_runs (
  run_id UUID PRIMARY KEY,
  agent_id TEXT,
  skill_id TEXT,
  model_tier TEXT,
  input_tokens INT,
  output_tokens INT,
  cost_usd DECIMAL(8,4),
  latency_ms INT,
  status TEXT,  -- success|timeout|error
  feedback_score INT,  -- 0–5 (post-run)
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Write once, never deleted** (audit compliance).

### Metrics & Dashboards

**Real-time (Grafana):**
- Cost per agent per day (bar chart)
- Latency p50/p95/p99 (line chart)
- Error rate by segment (gauge)
- Model tier distribution (pie)
- Feedback score trend (3-month rolling avg)

**Alerts (Slack #agent-ops):**
- Error spike: > 3 timeouts/hour
- Cost spike: > 20% daily budget
- Feedback drop: avg < 3.0/5
- Deprecation: v4.9 skills near end-of-life

---

## P7 — Orquestração Async (APScheduler)

### Background Triggers

**Trigger 1: RAG Reindex (R6)**
```
Cron: 0 2 * * *  (daily 02:00 UTC)
Job: rag-reindex.py
Task:
  - Reindex all collections (san:v5.0, ene:v5.0, ...)
  - Validate embeddings (dimension, format)
  - Update metadata.json
  - Prune cache (> 7 days)
SLA: Complete in < 30 minutes
```

**Trigger 2: Embedding Retraining (R9)**
```
Cron: 0 3 * * 0  (Sunday 03:00 UTC)
Job: embedding-retrain.py
Task:
  - Fetch user ratings > 4 from last 7 days
  - Extract "user_intent_vector" from high-rating queries
  - Fine-tune cross-encoder model
  - Update checksum in VERSIONS.json
  - Stage new model in `.claude/embedding/`
  - (Manual approval before promotion to prod)
SLA: Complete in < 2 hours
```

**Trigger 3: Memory Purge (R10)**
```
Cron: 30 3 * * *  (daily 03:30 UTC)
Job: memory-purge.py
Task:
  - FOR each agent_memory:
    IF size > 100MB OR last_purge > 30 days:
      - Keep latest 1000 completions
      - Delete chunks (age > 7 days AND rating < 2)
      - Keep embedding cache of frequent queries
  - Log: {agent_id, size_before, size_after, deleted_count}
SLA: Complete in < 15 minutes per agent
```

### Persistence

Triggers stored in Supabase `agent_triggers` table:
```json
{
  "trigger_id": "trig_rag-reindex-daily",
  "name": "RAG Reindex",
  "cron_expression": "0 2 * * *",
  "enabled": true,
  "next_run_at": "2026-07-26T02:00:00Z",
  "created_at": "2026-07-25T14:32:00Z"
}
```

Survives container restarts.

---

## P8 — Versionamento de Skills (Checksums + Rollback)

### Structure

```
.claude/agents/
├── agente-saneamento.md         # live (unversioned symlink)
├── agente-saneamento.v5.0.md    # production
├── agente-saneamento.v4.9.md    # archived
└── VERSIONS.json                # metadata
```

### VERSIONS.json

```json
{
  "agent_skills": {
    "agente-saneamento": {
      "v5.0": {
        "checksum": "f1a3d2b4c5e7a8b9c1d2e3f4a5b6c7d8",
        "pinned_by": ["prod"],
        "rag_collection": "san:v5.0:chunks",
        "created_at": "2026-07-25T14:32:00Z",
        "deprecated_at": null
      },
      "v4.9": {
        "checksum": "e4c3b2a1f5d6e7c8b9a1d2e3f4a5b6c7",
        "pinned_by": [],
        "deprecated_at": "2026-07-25T14:32:00Z",
        "grace_period_ends": "2026-08-24T14:32:00Z"
      }
    }
  }
}
```

### Guarantees

**Immutability:**
- Checksum validates file content (MD5)
- If file modified, healthcheck fails
- Automatic revert via rollback.py

**Rollback:**
- Load skill v4.9 via checksum
- Revert RAG to san:v4.9:chunks
- Update skill_version_pin in settings.json
- Restart agent
- **RTO:** < 2 minutes

**Deprecation:**
- Mark v4.9 as deprecated (30-day grace)
- Daily reminder in Slack (15d, 7d, 1d before end)
- Auto-disable at grace period end
- Audit log: who deprecates, when, reason

---

## Integration & Deployment

### Pre-deploy Validation

```bash
# 1. Validate architecture
python3 scripts/healthcheck.py

# 2. Validate tiering formula
python3 scripts/tiering-audit.py

# 3. Validate RAG collections
python3 scripts/rag-reindex.py --validate

# 4. Validate VERSIONS.json
python3 -c "import json; json.load(open('VERSIONS.json'))"
```

### Deployment Checklist

See `DEPLOYMENT-GUIDE.md` (Phase 1–8).

---

## Performance Targets

| Metric | Target | Current (v4.2) | v5.0 improvement |
|--------|--------|-----------------|-----------------|
| Routing latency | < 500ms | ~800ms | 37% faster |
| RAG query (BM25+embed) | < 50ms | ~200ms | 75% faster |
| Cost per run | $0.05–$0.08 | $0.12 (Sonnet) | 40% cheaper |
| Latency p95 | < 5s | ~8s | 37% faster |
| Feedback score | ≥ 4.0/5 | ~3.8 | +5% improvement |
| RAG cache hit | > 50% | ~25% | 2x improvement |
| Routing accuracy | ≥ 90% | ~85% | +6% accuracy |

---

## Migration Path (v4.2 → v5.0)

**Backward compatible?** Yes (R1–R5 unchanged, R6–R10 opt-in).

**Recommended migration:**
1. Staging deployment (Phase 1–7 in DEPLOYMENT-GUIDE.md)
2. Run tests (Phase 6)
3. Monitor 24h (Phase 8)
4. Gate approval (MN)
5. Rollback window: 24h after go-live (Phase 8)

**Rollback:** < 2 hours RTO (Phase 8 alternative).

---

## Future Roadmap (Post v5.0)

- **v5.1:** LLM-as-judge (self-ranking of agent outputs)
- **v5.2:** Multi-agent orchestration (complex queries span 3+ agents)
- **v5.3:** Knowledge distillation (smaller models trained on Opus outputs)
- **v5.4:** Streaming (real-time token output instead of wait-for-complete)
- **v6.0:** Agentic loops (agent calls another agent in a controlled loop)

---

**End of Arquitetura v5.0**
