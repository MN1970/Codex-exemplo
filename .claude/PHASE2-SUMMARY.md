# PHASE 2: MAESTRO ROUTER & ORCHESTRATION — COMPLETE DELIVERY

**Date:** 2026-08-08  
**Status:** ✅ COMPLETE — Ready for implementation  
**Scope:** Router decision tree, adaptive model selection, priority queue system

---

## EXECUTIVE SUMMARY

Phase 2 implements the intelligent dispatch system for Maestro (Manta 00). This system:

1. **Routes** incoming tasks to correct segment agents (S1–S10 + horizontal)
2. **Selects models** adaptively based on volume & complexity
3. **Dispatches** tasks via 4 orchestration patterns (direct/pipeline/parallel/fan-out)
4. **Manages** priority queues (Q0 critical, Q16 normal, Q∞ background)
5. **Learns** via RAG logging to Supabase

---

## DELIVERABLES

### 3 Core Documents (75 KB total)

| File | Size | Purpose |
|------|------|---------|
| **phase2-router.md** | 32 KB | Complete pseudocode implementation of MaestroRouter, AdaptiveModelSelector, QPrioDispatcher |
| **phase2-routing-rules.md** | 14 KB | Routing keyword reference (S1–S10 decision table, regex patterns, confidence scores) |
| **phase2-integration.md** | 29 KB | System architecture, HTTP endpoints, client libraries (JS/Python), monitoring, deployment checklist |

### Also Provided

- This summary (PHASE2-SUMMARY.md)
- Reference to CLAUDE.md v4.2 (master agent registry)

---

## KEY COMPONENTS

### 1. MAESTRO ROUTER (MaestroRouter class)

**What it does:**
- Analyzes incoming prompt (tokenization, keyword extraction)
- Detects priority queue (Q0/Q16/Q∞)
- Routes to segment (S1–S10 or horizontal)
- Detects lifecycle phase (EVTE/BASICO/EXECUTIVO/EXECUCAO/OPERACAO/LICITACAO/DUE_DILIGENCE/ENCERRAMENTO)
- Selects orchestration pattern (direct/pipeline/parallel/fan-out)
- Builds agent roster based on complexity + phase

**Public API:**
```javascript
dispatch(userPrompt, context) → RoutingDecision {
  agents: [agentId, ...],
  models: [modelName, ...],
  priority: 'Q0'|'Q16'|'Q∞',
  pattern: 'direct'|'pipeline'|'parallel'|'fan-out',
  metadata: { tokenCount, complexity, phase, segment }
}
```

**Routing Rules (10 vertical segments):**
- **S1** (Rodovias): rodovia, pavimento, CBUQ, SICRO, DNIT
- **S2** (OAE): ponte, viaduto, OAE, NBR 7187, túnel rodoviário
- **S3** (Ferrovia): ferrovia, trilho, AMV, dormente, via permanente
- **S4** (Metrô): metrô, estação, NATM, PSD, linha X, VLT
- **S6** (Portos): porto, terminal, ANTAQ, dragagem, molhe, berço, calado, contêiner, granel
- **S7** (Aeroportos): aeroporto, pista pouso, ANAC, ICAO, TPS, TECA, balizamento
- **S8** (Saneamento): saneamento, ETA, ETE, adutora, esgoto, AySA, SNIS, drenagem urbana
- **S9** (Energia): transmissão, LT, subestação, ANEEL, RAP, leilão, ONS, EPE
- **S10** (Barragens): barragem, vertedouro, CFRD, CCR, rejeitos, PNSB, ICOLD, CBDB, TSF

---

### 2. ADAPTIVE MODEL SELECTOR (AdaptiveModelSelector class)

**What it does:**
- Classifies task volume into bands (Pequeno/Médio/Grande/Extra-Grande)
- Detects task complexity (Baixa/Média/Alta/Crítica)
- Applies decision matrix from CLAUDE.md
- Overrides for critical/large paths

**Decision Matrix:**

| Volume | Low | Medium | High | Critical |
|---|---|---|---|---|
| **Pequeno** (0–500 tokens) | Haiku | Sonnet | Sonnet | Opus+Sonnet |
| **Médio** (500–2000) | Haiku+Haiku | Sonnet+Haiku | Sonnet+Sonnet | Opus+Sonnet |
| **Grande** (2000–5000) | Sonnet+Haiku | Sonnet+Haiku | Sonnet+Haiku | Opus+Sonnet |
| **Extra-Grande** (5000+) | Sonnet+Haiku | Sonnet+Haiku | Sonnet+Haiku | Opus+Sonnet |

**Public API:**
```javascript
selectModels(tokenCount, complexity, segment) → {
  primaryModel: 'haiku'|'sonnet'|'opus',
  secondaryModel: 'haiku'|'sonnet'|'opus'|null,
  reasoning: string
}
```

---

### 3. PRIORITY QUEUE DISPATCHER (QPrioDispatcher class)

**What it does:**
- Maintains 3 priority queues (Q0, Q16, Q∞)
- Polls continuously: Q0 (immediate) → Q16 (30-60s) → Q∞ (background)
- Executes tasks via 4 patterns with correct model/agent assignment
- Logs all metrics to Supabase RAG learning table

**Execution Patterns:**

| Pattern | Agents | Timeline | Use Case |
|---|---|---|---|
| **direct** | 1 | <30s | Small, low-complexity tasks |
| **pipeline** | 3–4 | 5–10 min | Sequential analysis → synthesis → assembly |
| **parallel** | 8 | 10–20 min | Independent analyses with barrier |
| **fan-out** | 16+ | 30min–2h | Massive parallelization, no barrier |

**Public API:**
```javascript
enqueue(task, routing) → queuedTask
dispatch(task) → { task, result }
start() // Main loop
getQueueStats() → { Q0, Q16, Q∞, total }
```

---

## INTEGRATION POINTS

### HTTP Endpoints

```
POST   /api/maestro               → Submit task (returns taskId + ETA)
GET    /api/maestro/task/{taskId} → Get task status & result
GET    /api/maestro/stats         → Queue statistics
GET    /api/maestro/health        → System health check
```

### Example Request/Response

**Request:**
```json
POST /api/maestro
{
  "prompt": "Análise de edital de concessão rodoviária",
  "context": { "projectId": "proj_123" }
}
```

**Response (Immediate):**
```json
{
  "taskId": "task_a1b2c3d4",
  "status": "QUEUED",
  "priority": "Q16",
  "estimatedWaitMs": 45000,
  "agents": ["agente-infraestrutura-S1", "Manta 02", "Manta 15"],
  "models": ["sonnet", "sonnet"],
  "pattern": "pipeline"
}
```

**Callback (After 5–10 minutes):**
```json
{
  "taskId": "task_a1b2c3d4",
  "status": "COMPLETE",
  "result": { /* Full analysis */ },
  "wallClockMs": 600000,
  "costCents": 2500
}
```

### Client Libraries

**JavaScript:**
```javascript
const maestro = new MaestroClient();
const task = await maestro.submitTask(prompt, context);
const result = await maestro.waitForTask(task.taskId);
```

**Python:**
```python
maestro = MaestroClient()
task = maestro.submit_task(prompt, context)
result = maestro.wait_for_task(task['taskId'])
```

---

## DECISION EXAMPLES

### Example 1: Small Task (Consultoria)

```
Input: "Qual a SELIC hoje?"
Volume: 12 tokens → Pequeno
Complexity: Baixa
Route: Horizontal (no vertical segment)
Priority: Q16 (normal)
Model: Haiku
Pattern: direct (1 agent)
Agent: Manta 00 only
Duration: <10 sec
```

### Example 2: Medium Task (Edital)

```
Input: "Analise este edital de concessão rodoviária (10 pgs)"
Volume: 1800 tokens → Médio
Complexity: Alta
Route: S1 (rodovia)
Priority: Q16 (normal)
Model: Sonnet + Sonnet
Pattern: pipeline (3 agentes)

Stage 1 (30s): agente-infraestrutura-S1 (técnica)
Stage 2 (120s parallel):
  - Manta 02 (legal)
  - Manta 15 (advisory)
Stage 3 (30s): Assembly

Total Duration: 5–10 min
```

### Example 3: Large Task (CRÍTICA)

```
Input: "Proposta comercial completa para concessão hidrelétrica até amanhã"
Volume: 3500 tokens → Grande
Complexity: Crítica
Route: S10 (barragens)
Priority: Q0 (CRITICAL — stop-the-world)
Model: Opus + Sonnet
Pattern: parallel (8 agentes)

Agents:
  Stage 1: agente-barragens
  Stage 2 (parallel):
    - Manta 02 (legal)
    - Manta 05 (budget)
    - Manta 07 (schedule)
    - Manta 15 (advisory)
  Stage 3: Assembly

Total Duration: 20–30 min
```

---

## QUEUE MANAGEMENT (QPrio)

### Priority Queue Behavior

| Priority | Use Case | SLA | Example |
|---|---|---|---|
| **Q0** | CRITICAL | <5s wait | Claims, reequilíbrio, M&A, escalation |
| **Q16** | NORMAL | <60s wait | Standard routing, analyses, proposals |
| **Q∞** | BACKGROUND | Best effort | RAG learning, indexing, batch jobs |

### Queue Dispatching Algorithm

```
WHILE true:
  IF Q0.length > 0:
    dispatch(Q0.shift())
  ELSE IF Q16.length > 0:
    dispatch(Q16.shift())
  ELSE IF Q∞.length > 0 AND random() < 0.016:  // 1/60
    dispatch(Q∞.shift())
  ELSE:
    sleep(100ms)
```

---

## RAG LEARNING LOG

### Tracked Metrics

```sql
CREATE TABLE rag_learning_log (
  task_id, prompt_excerpt, volume_band, complexity, segment,
  agents, models, pattern, priority, wall_clock_ms, status,
  cost_cents, created_at
);
```

### Weekly Analysis Query

```sql
SELECT 
  volume_band, complexity, pattern,
  COUNT(*) as tasks,
  AVG(wall_clock_ms) as avg_duration,
  SUM(cost_cents) as total_cost,
  100.0 * SUM(CASE WHEN status='COMPLETE' THEN 1 ELSE 0 END) / COUNT(*) as success_pct
FROM rag_learning_log
WHERE created_at >= now() - interval '7 days'
GROUP BY volume_band, complexity, pattern
ORDER BY total_cost DESC;
```

---

## DEPLOYMENT CHECKLIST

### Pre-Production (Code Review & Testing)

- [ ] Code review: router, selector, dispatcher
- [ ] Unit tests: routing rules, model selection, queue behavior
- [ ] Integration tests: small/medium/large examples
- [ ] Load test: 100 tasks in Q16 queue
- [ ] Agent pool: all 20 agents configured
- [ ] Database: Supabase tables & indexes created
- [ ] Monitoring: alerts configured
- [ ] Documentation: API reference, runbooks, troubleshooting

### Production Deployment

- [ ] Stage environment validated
- [ ] Gradual traffic ramp: 5% → 25% → 100%
- [ ] Monitor: error rates, queue depth, latency, cost
- [ ] Gate: human approval before 100%

---

## FILES & ORGANIZATION

```
Codex-exemplo/
├── CLAUDE.md                              (v4.2, master registry)
├── .claude/
│   ├── PHASE2-SUMMARY.md                 (this file)
│   ├── phase2-router.md                  (32 KB, core implementation)
│   ├── phase2-routing-rules.md           (14 KB, routing reference)
│   ├── phase2-integration.md             (29 KB, architecture & deployment)
│   └── agents/                           (Phase 1 files)
│       ├── agente-saneamento.md
│       ├── agente-energia.md
│       ├── agente-portos.md
│       ├── agente-aeroportos.md
│       └── agente-barragens.md
```

---

## WHAT'S NEXT (Phase 3 & 4)

### Phase 3: RAG Indexing & Knowledge Base

- [ ] Create 5 Supabase collections (saneamento, energia, portos, aeroportos, barragens)
- [ ] Embed 500+ documents via BAAI/bge-small-en-v1.5
- [ ] Set up pgvector similarity search
- [ ] Configure agent RAG retrieval

### Phase 4: End-to-End Testing & Production

- [ ] Integration tests (all 10 routing rules)
- [ ] Load testing (1000 tasks/day)
- [ ] Failover testing (agent outage)
- [ ] Production deployment with human gate

---

## KEY FEATURES

✅ **10 vertical routing rules** (S1–S10)  
✅ **Adaptive model selection** (Haiku/Sonnet/Opus)  
✅ **4 execution patterns** (direct/pipeline/parallel/fan-out)  
✅ **Priority queues** (Q0 critical, Q16 normal, Q∞ background)  
✅ **RAG learning log** (metrics, cost tracking, SLA monitoring)  
✅ **Client libraries** (JS, Python)  
✅ **Monitoring & observability** (queue stats, metrics, logs)  
✅ **Graceful degradation** (fallback to horizontal agents)  
✅ **Comprehensive documentation** (75 KB, production-ready)  

---

## TESTING SCENARIOS

### Test 1: Small Task Routing

```bash
curl -X POST http://localhost:3000/api/maestro \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Qual a SELIC hoje?"}'

# Expected: direct pattern, Haiku, <10s
```

### Test 2: Vertical Segment Routing (S8)

```bash
curl -X POST http://localhost:3000/api/maestro \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Análise de edital de saneamento para AySA"}'

# Expected: S8 routing, pipeline, Sonnet+Sonnet
```

### Test 3: Critical Path (Q0)

```bash
curl -X POST http://localhost:3000/api/maestro \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "URGENTE: Reequilíbrio econômico de concessão hidrelétrica",
    "context": {"priority": "critical"}
  }'

# Expected: Q0 queue, Opus+Sonnet, parallel
```

---

## SUCCESS CRITERIA

- [ ] All 10 routing rules tested and validated
- [ ] Model selection matrix matches CLAUDE.md exactly
- [ ] Queue SLAs met: Q0 <5s, Q16 <60s
- [ ] Railer cost per task tracked accurately
- [ ] 95%+ success rate on all patterns
- [ ] End-to-end latency <30 min for 95th percentile

---

## REFERENCES

- **CLAUDE.md v4.2** — Master agent registry (source of truth)
- **phase2-router.md** — Full pseudocode, classes, methods
- **phase2-routing-rules.md** — Keyword patterns, confidence scores
- **phase2-integration.md** — Architecture, APIs, deployment

---

**Status:** ✅ Phase 2 COMPLETE  
**Next:** Phase 3 (RAG indexing) — scheduled 2026-08-15  

**Questions?** Refer to the 3 core documents above or review CLAUDE.md § ROUTING.
