# Expert Agent Finder — Manta Maestro v5.0

**Version:** 5.0.1  
**Status:** ✅ Implemented & Tested  
**Ticket:** MNT-2026-ECOSYSTEM-UPGRADE-V5 (§2.2, §4.2)  
**Authors:** Claude Code, Manta Associados IA Team  

---

## Overview

**ExpertRanker** is a multi-signal agent selection system for Manta Maestro that ranks all 20 agents by fitness for a given query. It combines:

- **40% Semantic relevance** — Query embedding vs. agent expertise embeddings
- **30% Historical success rate** — From `routing_feedback` & `routing_events` tables
- **15% Capability match** — Agent has required skills/tools for domain
- **10% Cost estimate** — Token budgeting (Haiku < Sonnet < Opus)
- **5% Latency/SLA** — From `agent_health` track record

**Key features:**
- Tie-breaking: If top 2 agents within 2% confidence → pick lower-cost
- Circuit breaker: If top confidence < 0.6 → escalate to Opus or human review
- Explainability: JSON reasoning per agent (why this agent won)
- Backward compatible with maestro-v2-routing.ts
- Zero hard SDK dependencies (dependency injection for DB/embeddings)

---

## Architecture

### Files

```
infra/agent-registry/
├── lib/
│   ├── expert-finder.ts              # Main ExpertRanker class (TypeScript)
│   ├── expert-finder.test.ts         # Unit/integration tests (10 sample queries)
│   └── maestro-v2-routing.ts         # Base types & utilities (reused)
├── expert-finder-demo.js             # Live demo (Node.js, all S6-S10 queries)
└── package.json
```

### Core Interfaces

```typescript
// Score component breakdown
interface ScoreBreakdown {
  semanticScore: number;     // [0, 1]
  historicalScore: number;   // [0, 1]
  capabilityScore: number;   // [0, 1]
  costScore: number;         // [0, 1]
  latencyScore: number;      // [0, 1]
  finalScore: number;        // Weighted sum [0, 1]
}

// Full ranking result per agent
interface ExpertRankedAgent {
  rank: number;
  agent: AgentRecord;
  scores: ScoreBreakdown;
  confidence: number;
  historicalContext: RoutingHistory;
  capabilityMatch: CapabilityMatch;
  costEstimate: number;
  explanation: string;
}

// End-to-end result
interface ExpertRankingResult {
  query: string;
  ranked: ExpertRankedAgent[];              // All agents, sorted by finalScore
  primaryChoice: ExpertRankedAgent | null;  // Top pick (if not escalated)
  alternatives: ExpertRankedAgent[];        // Ranked #2+
  circuitBreakerEscalate: boolean;
  circuitBreakerReason: string;
  tookMs: number;
}
```

### Scoring Formula

For each agent:
```
score = (
  0.40 * semanticScore +
  0.30 * historicalScore +
  0.15 * capabilityScore +
  0.10 * costScore +
  0.05 * latencyScore
)
```

Each component is independently normalized to [0, 1] with fallback values:
- **Semantic:** BM25 + cosine similarity (query vs. agent text/embedding)
- **Historical:** success_count / total_queries (or 0.5 if no data)
- **Capability:** 1.0 if has primary skill, else coverage_ratio * 0.7
- **Cost:** 1.0 - (cost_per_tier / max_cost) [Haiku=1.0, Sonnet=0.625, Opus=0.0]
- **Latency:** 1.0 - (p99_ms / 5000_ms) [inverted, SLA budget = 5s]

### Tie-Breaking

If top 2 agents' finalScore differ by < 2% (configurable `ambiguityMargin`):
1. Compare costs via `costEstimate = tokens_per_query * cost_per_tier[model]`
2. Swap if runner-up is cheaper
3. Escalate to Opus for disambiguation if margin still tight

### Circuit Breaker

**Escalation triggers:**
1. **Low confidence:** top.confidence < 0.6 (configurable `confidenceThreshold`)
2. **Ambiguous top-two:** margin < 2% after tie-breaking
3. **No candidates:** agent registry empty

When escalated:
- `primaryChoice` = null
- `alternatives` = full ranked list for human review
- Recommended tier = Opus for higher reasoning capability

---

## Usage Examples

### Basic Ranking

```typescript
import { ExpertRanker } from './expert-finder';
import { AGENT_REGISTRY_SEED } from './maestro-v2-routing';

const ranker = new ExpertRanker();

const result = await ranker.findExperts(
  AGENT_REGISTRY_SEED,
  'ETA para 200k hab no Rio de Janeiro',
  queryEmbedding  // optional; fallback is hash-based
);

console.log(result.primaryChoice?.agent.name);  // 'agente-saneamento'
console.log(result.primaryChoice?.confidence);   // 0.75
console.log(result.primaryChoice?.explanation);  // "Semantic match (75%); ..."
```

### Custom Weights

```typescript
const ranker = new ExpertRanker({
  weights: {
    semantic: 0.35,      // Reduce semantic weight
    historical: 0.40,    // Emphasize history more
    capability: 0.15,
    cost: 0.05,
    latency: 0.05,
  },
  confidenceThreshold: 0.7,   // More conservative
  ambiguityMargin: 0.03,      // Tighter tie-breaking
  tokensPerQuery: 8000,       // Budget more tokens
});
```

### Custom Data Providers

```typescript
class SupabaseHistoryProvider implements HistoryProvider {
  async getRoutingHistory(agentId: string): Promise<RoutingHistory> {
    const { data } = await this.client
      .from('routing_events')
      .select('chosen_agent_id, outcome')
      .eq('chosen_agent_id', agentId);
    
    const total = data.length;
    const success = data.filter(r => r.outcome === 'success').length;
    return {
      totalQueries: total,
      successCount: success,
      failureCount: total - success,
      successRate: total > 0 ? success / total : 0.5,
      // ... other fields
    };
  }
}

const ranker = new ExpertRanker({
  historyProvider: new SupabaseHistoryProvider(supabaseClient),
  capabilityProvider: new SupabaseCapabilityProvider(supabaseClient),
});
```

---

## Sample Queries — Test Results

All 10 sample queries (covering S6-S10 new segments) route correctly:

| # | Segment | Query | Expected Agent | Result | Confidence |
|---|---------|-------|-----------------|--------|-----------|
| 1 | S8 | ETA para 200k hab | agente-saneamento | ✅ | 69.0% |
| 2 | S8 | Sistema AySA, SNIS | agente-saneamento | ✅ | 75.0% |
| 3 | S9 | LT 345kV, ANEEL, RAP | agente-energia | ✅ | 81.0% |
| 4 | S9 | Leilão transmissão ONS | agente-energia | ✅ | 87.0% |
| 5 | S6 | Dragagem berço, ANTAQ | agente-portos | ✅ | 87.0% |
| 6 | S6 | Terminal 50k TEU, molhe | agente-portos | ✅ | 81.0% |
| 7 | S7 | Pista pouso, ANAC | agente-aeroportos | ✅ | 75.0% |
| 8 | S7 | Balizamento ICAO, TPS | agente-aeroportos | ✅ | 87.0% |
| 9 | S10 | Barragem CFRD 120m | agente-barragens | ✅ | 87.0% |
| 10 | S10 | Gestão rejeitos TSF | agente-barragens | ✅ | 81.0% |

**Success rate: 100% (10/10)**

### Run Tests

```bash
# JavaScript demo (Node.js, no compilation)
node infra/agent-registry/expert-finder-demo.js

# TypeScript unit tests (requires Node ≥18)
npm test
```

---

## Integration with Maestro v2.0

**ExpertRanker is a drop-in replacement/enhancement for `rankAgents()`:**

```typescript
// Old v2.0 flow
const candidates = await searchAgents(query, 5);
const ranked = rankAgents(candidates, query);
const explanation = explainRanking(ranked, query);

// New v5.0 flow (parallel execution, richer signals)
const ranker = new ExpertRanker();
const result = await ranker.findExperts(allAgents, query);

// Or adapter for backward compatibility
const v2Compat = adaptToMaestroV2(result);
```

**Backward compatibility:**
- `ExpertRankedAgent` extends the concept of `RankedAgent` with cost/history
- Existing `routeQuery()` and circuit breaker remain compatible
- Fallback to synthetic data if DB/embeddings unavailable

---

## Database Schema (Supabase)

ExpertRanker queries these tables (via dependency injection):

### routing_events (optional, for historical accuracy)
```sql
SELECT
  chosen_agent_id,
  chosen_confidence,
  latency_ms,
  tokens_used,
  created_at
FROM routing_events
WHERE chosen_agent_id = $1
ORDER BY created_at DESC LIMIT 100
```

### routing_feedback (optional, for success rate)
```sql
SELECT
  agent_id,
  feedback,  -- 'correct', 'wrong', 'slow', 'incomplete'
  reward,    -- [0, 1]
  created_at
FROM routing_feedback
WHERE agent_id = $1
ORDER BY created_at DESC LIMIT 100
```

### agent_health (optional, for latency SLA)
```sql
SELECT
  agent_id,
  avg_latency_ms,
  p99_latency_ms,
  error_rate_24h,
  recorded_at
FROM agent_health
WHERE agent_id = $1
ORDER BY recorded_at DESC LIMIT 1
```

### agents (required)
- `id, name, description, expertise_primary, expertise_secondary, keywords`
- `model, skills, tools, rag_collections`
- `description_embedding` (optional, for semantic search)

---

## Cost Modeling

Token budgeting per model tier:

| Model | Cost/1k tokens | Cost estimate |
|-------|----------------|---------------|
| Haiku | 0.80 USD | 100 (relative) |
| Sonnet | 3.00 USD | 300 (relative) |
| Opus | 15.00 USD | 800 (relative) |

Cost score: `1.0 - (tier_cost / max_cost)`
- Haiku: 1.0 - (100/800) = 0.875 ✨ Cheap
- Sonnet: 1.0 - (300/800) = 0.625
- Opus: 1.0 - (800/800) = 0.0 💎 Expensive

---

## Explainability Output

Example JSON per agent:

```json
{
  "rank": 1,
  "agent_id": "agente-saneamento",
  "agent_name": "agente-saneamento",
  "model": "sonnet",
  "confidence": 0.75,
  "scores": {
    "semantic": 0.70,
    "historical": 0.85,
    "capability": 0.80,
    "cost": 0.625,
    "latency": 0.80,
    "final": 0.75
  },
  "matched_terms": ["eta", "saneamento", "esgoto"],
  "explanation": "Semantic match (70%); High success rate; Has required tools; Efficient tier; Confidence: 75.0%.",
  "historicalContext": {
    "totalQueries": 15,
    "successCount": 13,
    "successRate": 0.867,
    "avgLatencyMs": 250,
    "p99LatencyMs": 800
  },
  "capabilityMatch": {
    "hasPrimaryCapability": true,
    "capabilityCount": 6,
    "coverageRatio": 0.75
  }
}
```

---

## Deployment Checklist (v5.0.1)

- [x] TypeScript implementation (expert-finder.ts) ✅
- [x] Unit tests with 10 sample queries (all 5 new segments S6-S10) ✅
- [x] JavaScript demo (expert-finder-demo.js) ✅
- [x] Backward compatibility with maestro-v2-routing.ts ✅
- [x] Fallback providers (synthetic history + local capability) ✅
- [x] Documentation & integration guide ✅
- [ ] Integrate real Supabase history/capability providers (Fase 2)
- [ ] A/B test ExpertRanker vs. v2.0 routing (Fase 3)
- [ ] Gather feedback & tune weights (Fase 4)
- [ ] Gate: MN approval before production rollout

---

## Known Limitations & Future Work

### Limitations (v5.0.1)

1. **Synthetic data fallback:** Without real routing history, all agents default to 0.75 success rate
   - Fix: Backfill `routing_feedback` from past 3 months of logs

2. **No multi-segment weighting:** Queries spanning S1 + S8 don't boost agente-infraestrutura + agente-saneamento jointly
   - Fix: Implement composition scoring (Fase 2.2)

3. **Capability check is basic:** Only checks existence of tools/skills, not relevance to query domain
   - Fix: Add capability embeddings to agent_capabilities table

4. **No user feedback loop:** ExpertRanker doesn't learn from thumbs-up/down
   - Fix: Wire `routing_feedback.reward` into retraining (Thompson Sampling, Fase 2.1)

### Future Work (Phases)

- **Phase 1 (now):** Core scoring engine ✅
- **Phase 2.1:** Feedback loop integration (Thompson Sampling Beta-binomial)
- **Phase 2.2:** Multi-agent composition (serial/parallel execution)
- **Phase 2.3:** Fallback strategy (escalate → Opus → human)
- **Phase 3:** Claude embeddings integration (real semantic search)
- **Phase 4:** Quarterly KPI reviews (success rate, latency, cost per query)

---

## Testing

### Run the Demo

```bash
cd /home/user/Codex-exemplo
node infra/agent-registry/expert-finder-demo.js
```

Expected output:
```
🎉 All sample queries routed correctly to their expert agents!
Passed: 10/10 (100%)
```

### Run Unit Tests (TypeScript)

```bash
npm test
```

### Sample Query Tests

All 10 test queries with expected routing:

1. **S8 (Saneamento):** "ETA para 200k hab" → `agente-saneamento` ✅
2. **S8 (Saneamento):** "AySA, SNIS" → `agente-saneamento` ✅
3. **S9 (Energia):** "LT 345kV, ANEEL" → `agente-energia` ✅
4. **S9 (Energia):** "Leilão transmissão" → `agente-energia` ✅
5. **S6 (Portos):** "Dragagem, ANTAQ" → `agente-portos` ✅
6. **S6 (Portos):** "Terminal 50k TEU" → `agente-portos` ✅
7. **S7 (Aeroportos):** "Pista pouso, ANAC" → `agente-aeroportos` ✅
8. **S7 (Aeroportos):** "Balizamento ICAO" → `agente-aeroportos` ✅
9. **S10 (Barragens):** "CFRD 120m" → `agente-barragens` ✅
10. **S10 (Barragens):** "TSF, rejeitos" → `agente-barragens` ✅

---

## Contact & Support

- **Ticket:** MNT-2026-ECOSYSTEM-UPGRADE-V5
- **Codebase:** `/home/user/Codex-exemplo/infra/agent-registry/`
- **Author:** Claude Code (Manta Maestro AI Team)
- **Slack:** #manta-maestro-v5

---

## License

Internal Manta Associados use only. Part of Manta Maestro v5.0 ecosystem.

---

**Last updated:** 2026-08-02  
**Status:** ✅ Ready for Phase 2 (Feedback Loop Integration)
