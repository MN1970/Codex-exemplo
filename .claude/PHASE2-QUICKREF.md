# Phase 2: Quick Reference Card

**TL;DR for developers** — How to use Maestro in 5 minutes

---

## ROUTING AT A GLANCE

| Keyword | Segment | Agent | Example |
|---|---|---|---|
| saneamento, ETA, esgoto, AySA | **S8** | agente-saneamento | "Edital de ETA para AySA" |
| transmissão, LT, ANEEL, RAP | **S9** | agente-energia | "Leilão de transmissão 2025" |
| porto, terminal, ANTAQ, dragagem | **S6** | agente-portos | "Terminal de contêineres" |
| aeroporto, pista, ANAC, TPS | **S7** | agente-aeroportos | "Novo TPS com 60 gates" |
| barragem, vertedouro, CFRD, rejeitos | **S10** | agente-barragens | "Barragem de 150 m" |
| rodovia, pavimento, SICRO | **S1** | agente-infraestrutura-S1 | "Concessão rodoviária" |
| ponte, viaduto, OAE, NBR 7187 | **S2** | agente-infraestrutura-S2 | "Ponte estaiada" |
| ferrovia, trilho, dormente | **S3** | agente-infraestrutura-S3 | "Ferrovia de carga" |
| metrô, estação, NATM, VLT | **S4** | agente-infraestrutura-S4 | "Linha 4 de metrô" |

---

## QUICK API CALL

### JavaScript
```javascript
const response = await fetch('/api/maestro', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Análise de edital de saneamento para AySA",
    context: { projectId: 'proj_123' }
  })
});

const { taskId, agents, models, pattern } = await response.json();
console.log(`Task ${taskId} → ${pattern} via ${agents.join(', ')}`);
```

### Python
```python
import requests

response = requests.post('/api/maestro', json={
  'prompt': 'Análise de edital de saneamento para AySA',
  'context': {'projectId': 'proj_123'}
})

task = response.json()
print(f"Task {task['taskId']} → {task['pattern']}")
```

### cURL
```bash
curl -X POST http://localhost:3000/api/maestro \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Análise de edital de saneamento para AySA",
    "context": {"projectId": "proj_123"}
  }' | jq .
```

---

## RESPONSE STRUCTURE

```json
{
  "taskId": "task_a1b2c3d4",
  "status": "QUEUED",
  "priority": "Q16",
  "queuePosition": 3,
  "estimatedWaitMs": 45000,
  "agents": ["agente-saneamento", "Manta 02", "Manta 15"],
  "models": ["sonnet", "sonnet"],
  "pattern": "pipeline",
  "metadata": {
    "tokenCount": 1200,
    "complexity": "alta",
    "segment": "S8",
    "keywords": ["análise", "edital", "saneamento", "AySA"]
  }
}
```

---

## PRIORITY QUEUES

```
Q0 (CRITICAL)    → Wait: 2–5 seconds
                   Use: claims, reequilíbrio, M&A, escalation
                   Pattern: parallel (8 agents)

Q16 (NORMAL)     → Wait: 30–60 seconds
                   Use: standard routing, analyses
                   Pattern: pipeline (3–4 agents)

Q∞ (BACKGROUND)  → Wait: unbounded
                   Use: RAG indexing, batch jobs
                   Pattern: fan-out (16+ agents async)
```

---

## EXECUTION PATTERNS

```
direct (1 agent)
├─ Agent 1 (30s)
└─ Result

pipeline (3–4 agents)
├─ Stage 1: Agent 1 (30s)
├─ Stage 2: Agents 2–3 parallel (120s)
└─ Stage 3: Agent 4 assembly (30s)

parallel (8 agents)
├─ Agents 1–8 all at once (parallel)
├─ [BARRIER: wait for all]
└─ Assembly agent

fan-out (16+ agents)
├─ Agents spawn async (no barrier)
└─ Results trickle in
```

---

## MODEL SELECTION QUICK TABLE

| Volume | Complexity | Model |
|---|---|---|
| <500 tokens | Low | **Haiku** |
| <500 tokens | Medium+ | **Sonnet** |
| 500–2000 | Low | Haiku + Haiku |
| 500–2000 | Medium | **Sonnet** + Haiku |
| 500–2000 | High+ | Sonnet + **Sonnet** |
| 2000+ | Any | **Sonnet** + Haiku |
| Critical | Any | **Opus** + Sonnet |

---

## COMMON PATTERNS

### Pattern 1: "I need quick info"
```
Input:    "Qual a SELIC hoje?"
Volume:   12 tokens (Pequeno)
Pattern:  direct
Agent:    Manta 00
Model:    Haiku
Time:     <10 sec
Cost:     <100¢
```

### Pattern 2: "Analyze this document"
```
Input:    "Análise de edital..." (1800 tokens)
Volume:   Médio
Pattern:  pipeline
Agents:   Vertical (S1–S10) + Manta 02 + Manta 15
Model:    Sonnet + Sonnet
Time:     5–10 min
Cost:     1500–2500¢
```

### Pattern 3: "I need this NOW (critical)"
```
Input:    "URGENTE: Reequilíbrio..." + context
Volume:   Grande
Pattern:  parallel
Priority: Q0 (no wait)
Agents:   8 (vertical + horizontal mix)
Model:    Opus + Sonnet
Time:     20–30 min
Cost:     4000–6000¢
```

---

## STATUS POLLING

### Check Queue Position
```bash
curl http://localhost:3000/api/maestro/stats | jq .
```

**Response:**
```json
{
  "queues": {
    "critical": { "count": 0, "label": "Q0" },
    "normal": { "count": 3, "label": "Q16" },
    "background": { "count": 12, "label": "Q∞" }
  },
  "total": 15
}
```

### Get Task Result
```bash
curl http://localhost:3000/api/maestro/task/{taskId} | jq .
```

---

## ENVIRONMENT VARIABLES

```bash
# Required
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ0eXAi...

# Optional
PORT=3000
LOG_LEVEL=info
QUEUE_POLL_MS=100
```

---

## DEBUGGING

### "Wrong segment routed"
```
→ Check routing-rules.md for keyword patterns
→ Add debug logging to router.dispatch()
→ Verify regex case-insensitive (/i flag)
```

### "Queue growing indefinitely"
```
→ Check agent logs for errors
→ Verify agent pool is healthy
→ Increase timeouts if legitimate slowness
→ Consider scaling agent instances
```

### "Model tokens exhausted"
```
→ Check API dashboard for remaining quota
→ Implement token budgeting per priority
→ Queue background tasks until next billing cycle
```

---

## MONITORING COMMANDS

```bash
# Health check
curl http://localhost:3000/api/maestro/health

# Queue stats (real-time)
curl http://localhost:3000/api/maestro/stats

# Task status
curl http://localhost:3000/api/maestro/task/{taskId}

# See logs
docker logs maestro-container | grep maestro
```

---

## PERFORMANCE TARGETS

| Metric | Target |
|---|---|
| Request-to-queue latency | <100ms |
| Q0 queue wait | <5s |
| Q16 queue wait | <60s |
| Small task duration | <30s |
| Medium task duration | 5–10 min |
| Large task duration | 20–30 min |
| Token cost / task | 100–6000¢ |
| Success rate | 95%+ |

---

## KEY FILES

- **phase2-router.md** (32 KB) — Full implementation
- **phase2-routing-rules.md** (14 KB) — Routing reference
- **phase2-integration.md** (29 KB) — Deployment guide
- **CLAUDE.md v4.2** — Source of truth for agents

---

## CHEAT SHEET: ROUTING KEYWORDS BY PRIORITY

### High-Priority Keywords (Match immediately)
```
S8: saneamento, AySA, SNIS
S9: ANEEL, leilão transmissão
S6: ANTAQ, dragagem
S7: ANAC, aeroporto
S10: barragem, rejeitos
```

### Context Keywords (Help confirm segment)
```
S8: ETA, ETE, adutora, esgoto
S9: transmissão, LT, RAP, ONS
S6: porto, terminal, molhe
S7: pista, TPS, TECA
S10: vertedouro, CFRD, ICOLD
```

---

**Ready to build?** Start with phase2-router.md →  implementation→ integration → testing → production.
