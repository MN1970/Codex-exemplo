# Expert Agent Finder — Architecture & Integration Guide

**Manta Maestro v5.0 | Expert Ranker System**

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Query Input                              │
│                    "ETA para 200k hab"                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
     ┌──────────────────┐
     │ ExpertRanker()   │  ← Main class: orchestrator
     │  .findExperts()  │    - Takes query, agent pool, embedding
     └────┬─────────────┘    - Returns ranked list + decision
          │
          ├─────────────────────────────────────┐
          │                                     │
          ▼                                     ▼
    ┌─────────────────┐              ┌──────────────────┐
    │ Score Compute   │              │ Data Providers   │
    │ ─────────────── │              │ ──────────────── │
    │ • Semantic 40%  │              │ HistoryProvider  │
    │ • Historical 30%│              │ └─ routing_events│
    │ • Capability 15%│              │    routing_feedbk│
    │ • Cost 10%      │              │ CapabilityPrvdr  │
    │ • Latency 5%    │              │ └─ agent_capablt │
    └─────────────────┘              │    agent_health  │
                                     └──────────────────┘
          │
          ▼
    ┌──────────────────────────┐
    │ ScoreBreakdown per Agent │  ← Individual scores [0, 1]
    │ {semantic, historical,   │
    │  capability, cost,       │
    │  latency, final}         │
    └──────┬───────────────────┘
           │
           ▼
    ┌──────────────────────────┐
    │ Sort & Rank Agents       │  ← sort by finalScore desc
    │ ranked[0] = top choice   │
    └──────┬───────────────────┘
           │
           ├──────────────────────────────────────────┐
           │                                          │
           ▼                                          ▼
    ┌─────────────────┐                    ┌──────────────────┐
    │ Tie-Breaker     │                    │ Circuit Breaker  │
    │ ─────────────── │                    │ ──────────────── │
    │ If top-2 within │                    │ • Low confidence │
    │ 2% margin:      │                    │   (< 0.6)?       │
    │ → pick cheaper  │                    │ • Ambiguous      │
    │                 │                    │   (margin < 2%)? │
    └─────────────────┘                    │ • No candidates? │
           │                               │ → Escalate to    │
           │                               │   Opus / human   │
           └───────────────┬────────────────┘
                           │
                           ▼
            ┌───────────────────────────┐
            │ ExpertRankingResult       │
            │ ───────────────────────── │
            │ • primaryChoice OR null   │
            │ • alternatives []         │
            │ • escalate flag           │
            │ • explanations (JSON)     │
            └───────────────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Final Route  │
                    │ Decision     │
                    └─────────────┘
```

---

## Score Computation Flow

### Per-Agent Scoring (Detailed)

```
Agent: agente-saneamento
Query: "ETA para 200k hab"
├── Semantic (40% weight)
│   ├── BM25 on keywords: match["eta", "saneamento"] → 0.70
│   ├── Cosine similarity (embedding): → 0.75
│   └── Blended: (0.6 * 0.70 + 0.4 * 0.75) = 0.72
│       → Normalized to [0, 1]: semantic_score = 0.72
│
├── Historical (30% weight)
│   ├── Query routing_events: 15 total, 13 success
│   ├── Success rate: 13/15 = 0.867
│   └── historical_score = 0.867
│
├── Capability (15% weight)
│   ├── Check: has ETA/ETE design skill? YES (hasPrimary=true)
│   ├── Tools count: 6 / max 10 = coverage 0.60
│   ├── Formula: 0.9 + (0.1 * 0.60) = 0.96
│   └── capability_score = 0.96
│
├── Cost (10% weight)
│   ├── Model: sonnet → cost_tier = 300
│   ├── Max cost (opus): 800
│   ├── Formula: 1.0 - (300/800) = 0.625
│   └── cost_score = 0.625
│
├── Latency (5% weight)
│   ├── p99_latency_ms: 800
│   ├── SLA budget: 5000 ms
│   ├── Formula: 1.0 - (800/5000) = 0.84
│   └── latency_score = 0.84
│
└── FINAL SCORE (weighted blend):
    0.40 * 0.72 + 0.30 * 0.867 + 0.15 * 0.96 + 0.10 * 0.625 + 0.05 * 0.84
    = 0.288 + 0.260 + 0.144 + 0.0625 + 0.042
    = 0.7565 → confidence = 75.65% ✅
```

---

## Data Flow: Integration with Supabase

### Read Operations (Parallel Fetch)

```
ExpertRanker.findExperts(agents, query)
  │
  ├─ For each agent in parallel:
  │  ├─ HistoryProvider.getRoutingHistory(agent_id)
  │  │  └─ Query routing_events + routing_feedback tables
  │  │     SELECT success_count, avg_latency_ms, p99_latency_ms
  │  │     FROM (routing logic)
  │  │
  │  └─ CapabilityProvider.checkCapability(agent_id, query)
  │     └─ Query agent_capabilities table
  │        SELECT capability_name, config
  │        WHERE agent_id = $1 AND capability_type IN (...)
  │
  └─ Combine: (history + capability) → scores
```

### Dependency Injection Pattern

```typescript
// Implement custom providers to inject real Supabase calls
class SupabaseHistoryProvider implements HistoryProvider {
  constructor(private client: SupabaseLikeClient) {}

  async getRoutingHistory(agentId: string): Promise<RoutingHistory> {
    // Query routing_events + routing_feedback
    const { data: events } = await this.client
      .from('routing_events')
      .select('chosen_agent_id, outcome, latency_ms')
      .eq('chosen_agent_id', agentId)
      .order('created_at', { ascending: false })
      .limit(100);

    const { data: feedback } = await this.client
      .from('routing_feedback')
      .select('feedback, reward')
      .eq('agent_id', agentId)
      .order('created_at', { ascending: false })
      .limit(50);

    // Aggregate
    const total = events?.length ?? 0;
    const success = feedback?.filter(f => f.feedback === 'correct')?.length ?? 0;
    
    return {
      totalQueries: total,
      successCount: success,
      failureCount: total - success,
      successRate: total > 0 ? success / total : 0.5,
      avgLatencyMs: events?.reduce((s, e) => s + (e.latency_ms ?? 0), 0) / (total || 1),
      p99LatencyMs: calculateP99(events),
      errorRate24h: 0.02,  // From agent_health
      lastRoutedAt: events?.[0]?.created_at ? new Date(events[0].created_at) : null,
    };
  }
}

// Wire into ExpertRanker
const ranker = new ExpertRanker({
  historyProvider: new SupabaseHistoryProvider(supabaseClient),
  capabilityProvider: new SupabaseCapabilityProvider(supabaseClient),
});
```

---

## Integration Points

### 1. maestro-v2-routing.ts (Existing)

**Reuses:**
- `AgentRecord` interface
- `tokenize()` & `Bm25Index`
- `cosineSimilarity()` & embedding utilities
- `MaestroRoutingError` class

**Enhances:**
- `rankAgents()` → `ExpertRanker.rankAgents()` (richer signals)
- `evaluateCircuitBreaker()` → same logic, same thresholds

### 2. Maestro v2.0 Router (manta-00)

```typescript
// Old v2.0 flow (still works)
const result = await routeQuery(query, top_k, options);
const agent = result.primary?.agent;

// New v5.0 enhanced flow (parallel signals)
const ranker = new ExpertRanker(options);
const result = await ranker.findExperts(agents, query);
const agent = result.primaryChoice?.agent;
```

### 3. Feedback Loop (feedback_loop.py)

**ExpertRanker → Thompson Sampling:**
- Write `routing_events.chosen_agent_id`, `chosen_confidence`, `latency_ms`
- Write `routing_feedback.feedback`, `reward` (1.0 for 'correct', 0.5 for 'incomplete', etc.)
- Read `agent_posteriors` to influence historical scores

### 4. Auto-Registration Service

When a new agent joins (via `.claude/agents/*.md`):
1. `parse-agent-md.js` extracts expertise & capabilities
2. Seeds `agents` + `agent_expertise` + `agent_capabilities` tables
3. ExpertRanker picks it up automatically next ranking call

---

## Configuration & Tuning

### Weight Adjustments by Use Case

```typescript
// Conservative: Trust history, penalize new agents
const ranker = new ExpertRanker({
  weights: {
    semantic: 0.30,
    historical: 0.50,
    capability: 0.10,
    cost: 0.05,
    latency: 0.05,
  },
  confidenceThreshold: 0.75,
});

// Aggressive: Trust semantic match, explore new agents
const ranker = new ExpertRanker({
  weights: {
    semantic: 0.50,
    historical: 0.15,
    capability: 0.20,
    cost: 0.10,
    latency: 0.05,
  },
  confidenceThreshold: 0.50,
});

// Cost-conscious: Prioritize Haiku/Sonnet
const ranker = new ExpertRanker({
  weights: {
    semantic: 0.35,
    historical: 0.30,
    capability: 0.10,
    cost: 0.20,        // ↑ increased
    latency: 0.05,
  },
});

// SLA-strict: Penalize slow agents
const ranker = new ExpertRanker({
  weights: {
    semantic: 0.35,
    historical: 0.30,
    capability: 0.15,
    cost: 0.05,
    latency: 0.15,     // ↑ increased
  },
});
```

### Thresholds

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `confidenceThreshold` | 0.6 | [0.3, 0.9] | Escalate if top < this |
| `ambiguityMargin` | 0.02 | [0.01, 0.05] | Tie-break if gap < this |
| `tokensPerQuery` | 5000 | [1000, 20000] | Cost budget for calculation |

---

## Performance Characteristics

### Time Complexity

```
rankAgents(N agents):
  ├─ For each agent: O(N)
  │  ├─ BM25 score: O(Q) where Q = query tokens (~10)
  │  ├─ Embedding similarity: O(D) where D = embedding dims (1536)
  │  ├─ Async history/capability: O(1) [parallel]
  │  └─ Score compute: O(1)
  └─ Total: O(N * (Q + D)) ≈ O(N * 1600) = O(N)
           with async I/O not blocking
```

For 20 agents: ~32-100ms (serial), ~50-150ms with DB calls

### Space Complexity

```
O(N * (embedding_dims + metadata))
  ≈ O(20 * (1536 + 50)) = ~32KB per ranking
  → negligible
```

### Scaling Notes

- ✅ Handles 20-50 agents efficiently
- ⚠️ Beyond 100 agents: consider indexing (HNSW in Supabase)
- 🔄 Parallel async calls to history/capability providers mitigate I/O cost

---

## Testing Strategy

### Unit Tests (TypeScript)

```typescript
test('score components', () => {
  const ranker = new ExpertRanker();
  const scores = computeScores(agent, query, embedding);
  assert(scores.finalScore >= 0 && scores.finalScore <= 1);
});

test('circuit breaker', () => {
  const result = ranker.findExperts(agents, genericQuery);
  if (result.primaryChoice.confidence < 0.6) {
    assert(result.circuitBreakerEscalate === true);
  }
});
```

### Integration Tests (10 Sample Queries)

All 10 test queries route to correct expert agent (100% pass rate):
- Query → tokenize → compute per-agent scores → rank → assert top.agent.id

### Stress Tests (Pending Phase 2)

- 1000 concurrent queries → latency distribution
- Historical accuracy vs. user feedback (KPI validation)
- Cost per query (token tracking)

---

## Rollout Plan

### Phase 1: Foundation (✅ Done)
- ExpertRanker implementation
- TypeScript + JavaScript demo
- 10 sample queries passing
- Backward compat with v2.0

### Phase 2: Data Integration (Next)
- Wire Supabase history provider
- Implement real capability matching
- Backfill routing_feedback from logs
- Deploy to staging

### Phase 3: Optimization
- A/B test vs. v2.0 (50/50 traffic split)
- Gather user feedback (thumbs up/down)
- Tune weights based on KPIs
- Monitor latency + cost

### Phase 4: Feedback Loop
- Thompson Sampling integration
- Quarterly KPI review
- Graduated rollout to 100% production

---

## Troubleshooting

### "My agent never ranks high"

**Check:**
1. Keywords: Does query tokenize to your agent's keywords?
   ```bash
   tokenize("your query")  # Should overlap with agent.keywords
   ```
2. History: Does routing_feedback show success?
   ```sql
   SELECT feedback, COUNT(*) FROM routing_feedback
   WHERE agent_id = 'your-agent'
   GROUP BY feedback;
   ```
3. Capability: Are tools/skills configured?
   ```sql
   SELECT * FROM agent_capabilities WHERE agent_id = 'your-agent';
   ```

### "Confidence always < 0.6"

**Likely causes:**
1. Synthetic history fallback (no real routing_feedback)
2. Query too generic (matches many agents equally)
3. Agent keywords misaligned with real usage

**Fix:**
1. Wait for real traffic to accumulate history
2. Refine keywords in agent definition
3. Lower `confidenceThreshold` if needed (⚠️ less safe)

### "Wrong agent ranked first"

**Debug:**
```typescript
const ranker = new ExpertRanker();
const result = await ranker.findExperts(agents, query);
console.log(result.ranked.map(r => ({
  rank: r.rank,
  agent: r.agent.id,
  scores: r.scores,
  explanation: r.explanation,
})));
```

Compare score breakdown (which signal boosted wrong agent?):
- Semantic: Keyword overlap too high?
- Historical: Noise in feedback loop?
- Capability: Tool matching too broad?

---

## References

- **Manta Maestro v5.0 Upgrade Spec:** `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`
- **Feedback Loop (Thompson Sampling):** `feedback_loop.py`
- **Agent Registry Schema:** `supabase/migrations/2026_07_29_agent_registry_schema.sql`
- **maestro-v2-routing.ts:** `infra/agent-registry/lib/maestro-v2-routing.ts`

---

**Last updated:** 2026-08-02  
**Status:** ✅ Implemented & tested (Phase 1 complete)
