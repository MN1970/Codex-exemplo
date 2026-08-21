# Phase 2 Composition Orchestrator — Integration Guide

**Version:** Phase 2.0  
**Status:** Production-ready  
**Last updated:** 2026-08-02

This guide explains how to integrate the enhanced `CrossSegmentComposer` (Phase 2) with your Manta Maestro deployment, covering resource pooling, cost optimization, parallel execution with shared context, and observability.

---

## Overview

The Phase 2 composition orchestrator adds four key capabilities to Phase 1:

| Feature | Phase 1 | Phase 2 | Benefit |
|---------|---------|---------|---------|
| **Composition detection** | ✅ | ✅ | Identify multi-agent scenarios |
| **Scheduling (serial/parallel)** | ✅ | ✅ | DAG-based orchestration |
| **Cross-segment handoffs** | ✅ | ✅ | Automatic routing (5 patterns) |
| **Resource pooling (RAG)** | ❌ | ✅ | Cache edital, normativas, avoid redundant queries |
| **Cost tracking & optimization** | ❌ | ✅ | Token budgets, per-agent breakdown, Haiku-first tier selection |
| **Observability events** | ❌ | ✅ | Emit to `routing_events` table for SLA/debugging |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CrossSegmentComposer (orchestrator)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │ Resource     │  │ Cost         │  │ Event          │   │
│  │ Pool         │  │ Tracker      │  │ Emitter        │   │
│  │ (shared RAG) │  │ (tokens)     │  │ (observability)│   │
│  └──────────────┘  └──────────────┘  └────────────────┘   │
│         │                 │                   │             │
│  ┌──────┴─────────────────┴───────────────────┴──────┐     │
│  │  composeAndOrchestrate(query)                     │     │
│  │    → detect() → schedule() → budget_check()       │     │
│  │    → orchestrate() → merge() → emit_events()      │     │
│  └───────────────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key classes:

- **ResourcePool**: Caches shared RAG chunks (edital, normativa, Lei 14.026) across agents to avoid redundant queries.
- **CostTracker**: Estimates and tracks token consumption per-agent and globally; enforces budget limits.
- **EventEmitter**: Interface for emitting observability events (ConsoleEventEmitter for dev, SupabaseEventEmitter for prod).
- **CompositionEvent**: Structured event schema for `routing_events` table (SQL schema below).
- **CrossSegmentComposer**: Facade orchestrating the full pipeline with resource pooling, cost optimization, and event emission.

---

## Usage

### Basic integration (Phase 1 compatible)

```typescript
import { detectComposition, analyzeScheduling, orchestrateComposition, MockAgentInvoker } from './composition-orchestrator';

const query = 'Preciso de uma UHE com barragem CFRD e LT de 500kV.';
const invoker = new MockAgentInvoker();

const detection = detectComposition(query);
if (!detection.isComposite) {
  console.log('Single-agent routing: ' + detection.agents[0].agentId);
  return;
}

const plan = analyzeScheduling(detection);
const result = await orchestrateComposition(plan, invoker, { query });

console.log(`Status: ${result.status}`);
console.log(`Merged output:\n${result.mergedOutput}`);
```

### Phase 2 integration (with cost tracking + resource pooling + observability)

```typescript
import { 
  CrossSegmentComposer, 
  ConsoleEventEmitter,
  MockAgentInvoker 
} from './composition-orchestrator';

const composer = new CrossSegmentComposer({
  globalBudgetTokens: 150_000,        // max 150k tokens per composition
  eventEmitter: new ConsoleEventEmitter(),
  compositionId: `comp_${Date.now()}`,
});

const result = await composer.composeAndOrchestrate(
  'Projeto de ETE + subestação no mesmo canteiro',
  new MockAgentInvoker(),
  {
    metadata: { projectId: 'GR-2026-001', phase: 'basic' },
  }
);

console.log(`Status: ${result.status}`);
console.log(`Composition ID: ${result.compositionId}`);
console.log(result.costSummary);  // Token breakdown
```

### Production: Supabase event emission

```typescript
import { 
  CrossSegmentComposer, 
  SupabaseEventEmitter,
  AnthropicAgentInvoker 
} from './composition-orchestrator';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
const eventEmitter = new SupabaseEventEmitter(supabase);

const composer = new CrossSegmentComposer({
  globalBudgetTokens: 250_000,
  eventEmitter,
});

const invoker = new AnthropicAgentInvoker({ apiKey: process.env.ANTHROPIC_API_KEY });

const result = await composer.composeAndOrchestrate(query, invoker, {
  metadata: { userId: 'mneves@mantaassociados.com', source: 'sharepoint' },
});

// Events automatically emitted to `routing_events` table
```

---

## Resource Pooling (RAG Cache)

The `ResourcePool` shares frequently-accessed documents (edital, normativa) across agents in a composition, avoiding redundant RAG queries.

### Example: Pre-load a shared edital

```typescript
const composer = new CrossSegmentComposer();
const pool = composer.getResourcePool();

// Simulate fetching from Supabase RAG
const sharedEdital = {
  id: 'edital_2026_01_bndes',
  sourceAgentId: 'agente-saneamento',
  collectionPrefix: 'san:',
  content: 'Edital BNDES 2026 Saneamento...',
  estimatedTokens: 2_500,
  createdAt: new Date(),
  consumedBy: new Set(),
};

pool.addChunk(sharedEdital);
composer.getCostTracker().recordRagReuse(2_500);  // Document the benefit
```

When an agent completes, it can add findings to the pool:

```typescript
// Inside agente-energia's upstream context
const upstreamContext = {
  'agente-barragens': {
    output: 'Barragem CFRD 100m, NA máximo maximorum 500m...',
    // Agent merges relevant chunks into ResourcePool
  }
};

// Subsequent agents access via pool.findByKeyword('NA máximo')
```

---

## Cost Optimization

### Token estimation heuristics

Per Manta's typical usage, costs are estimated as:

| Tier | Model | Input est. | Output est. | Use case |
|------|-------|------------|------------|----------|
| **Haiku** | claude-haiku-4-5 | 1–2k | 0.5–2k | Simple classifications, lookups |
| **Sonnet** | claude-sonnet-5 | 2–5k | 1–4k | Technical reasoning, document analysis |
| **Opus** | claude-opus-5 | 3–8k | 2–8k | Complex composition, synthesis |

The `selectOptimalTier()` method chooses the minimum tier meeting a confidence threshold:

```typescript
// Confidence >= 85% → haiku (cheap, confident)
// Confidence >= 50% → sonnet (balanced)
// Confidence < 50% → agent's default tier (or opus if no default)

const tier = composer.selectOptimalTier(detection.confidence, agentDef);
```

### Budget enforcement

```typescript
const composer = new CrossSegmentComposer({ globalBudgetTokens: 250_000 });
const result = await composer.composeAndOrchestrate(query, invoker);

if (result.status === 'failed' && result.errors.some(e => e.includes('Budget'))) {
  console.error('Composition exceeded token budget — escalate to manual review.');
}
```

---

## Observability & Metrics

### CompositionEvent schema

Every significant action in a composition emits a `CompositionEvent` to the `routing_events` table:

```sql
create table if not exists routing_events (
  event_id text primary key,
  composition_id text not null,
  query_id text not null,
  agent_id text not null,
  stage text not null,  -- 'detect', 'schedule', 'invoke_start', 'invoke_complete', 'invoke_error', 'merge', 'complete'
  pattern_matched text,
  status text not null,
  duration_ms int,
  token_count int,
  confidence float,
  fallback_triggered boolean,
  fallback_reason text,
  rag_reuse_count int,
  metadata jsonb,
  created_at timestamptz default now(),
  
  constraint fk_composition foreign key (composition_id) references compositions(id),
  constraint fk_agent foreign key (agent_id) references agents(id)
);

create index on routing_events(composition_id);
create index on routing_events(agent_id);
create index on routing_events(created_at);
create index on routing_events(stage);
```

### Querying metrics

```sql
-- Total token spend per composition
select composition_id, sum(token_count) as total_tokens, count(*) as events
from routing_events
where created_at > now() - interval '7 days'
group by composition_id
order by total_tokens desc;

-- Fallback rate per agent
select agent_id, 
       count(*) as invocations,
       sum(case when fallback_triggered then 1 else 0 end) as fallbacks,
       round(100.0 * sum(case when fallback_triggered then 1 else 0 end) / count(*), 2) as fallback_pct
from routing_events
where stage = 'invoke_complete'
group by agent_id;

-- Pattern usage
select pattern_matched, count(*) as compositions
from routing_events
where stage = 'detect'
group by pattern_matched
order by compositions desc;
```

---

## 5 Canonical Handoff Patterns

The `CrossSegmentComposer` natively supports 5 known composition patterns:

### 1. UHE (Usina Hidrelétrica)

**Agents:** agente-barragens (primary) → agente-energia (secondary)  
**Dependencies:** Serial (energia depends on barragem's NA, volume, vazão)  
**Cost:** ~4–5 agents' worth of tokens

```
Query: "Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV."
Pattern match: ✅ UHE_PATTERN
Detected agents: [barragens (primary), energia (secondary)]
Schedule: serial (barragem → energia)
```

### 2. ETE + Subestação

**Agents:** agente-saneamento (primary) ∥ agente-energia (secondary)  
**Dependencies:** None (parallel, independent scopes)  
**Cost:** ~2–3 agents' worth of tokens

```
Query: "ETE nova + subestação 138kV no mesmo canteiro."
Pattern match: ✅ ETE_SUBESTACAO_PATTERN
Detected agents: [saneamento (primary), energia (secondary)]
Schedule: parallel (no data dependency)
```

### 3. Porto + Pista de Carga

**Agents:** agente-portos (primary) ∥ agente-aeroportos (secondary)  
**Dependencies:** None (parallel, independent)  
**Cost:** ~2–3 agents' worth

```
Query: "Porto arrendado no Amazonas com pátio + pista para carga aérea."
Pattern match: ✅ PORTO_PISTA_PATTERN
Detected agents: [portos (primary), aeroportos (secondary)]
Schedule: parallel
```

### 4. Adutora × Barragem de Rejeitos

**Agents:** agente-barragens (consult) → agente-saneamento (primary)  
**Dependencies:** Serial (traçado respeta zona de autossalvamento)  
**Cost:** ~2–3 agents' worth

```
Query: "Adutora atravessando barragem de rejeitos TSF."
Pattern match: ✅ ADUTORA_BARRAGEM_PATTERN
Detected agents: [barragens (consult), saneamento (primary)]
Schedule: serial (barragens consult before saneamento finalizes traçado)
```

### 5. Claim + Orçamento

**Agents:** manta-01-claims (primary) ∥ manta-05-orcamento (secondary)  
**Dependencies:** None (parallel, often cross-checked in merge)  
**Cost:** ~1–2 agents' worth

```
Query: "Pleito de reequilíbrio econômico-financeiro precisa de quantitativo."
Pattern match: ✅ CLAIM_ORCAMENTO_PATTERN
Detected agents: [manta-01-claims (primary), manta-05-orcamento (secondary)]
Schedule: parallel
```

---

## Testing

### Unit tests (composition detection)

```typescript
import { detectComposition } from './composition-orchestrator';

describe('CrossSegmentComposer', () => {
  it('detects UHE pattern', () => {
    const result = detectComposition('UHE com barragem CFRD 100m e LT 500kV');
    expect(result.isComposite).toBe(true);
    expect(result.patternId).toBe('uhe');
  });

  it('costs under budget', () => {
    const composer = new CrossSegmentComposer({ globalBudgetTokens: 150_000 });
    // ... simulate composition
    expect(composer.getCostTracker().isWithinBudget()).toBe(true);
  });
});
```

### Integration test (full pipeline)

```typescript
import { runPhase2Demo, runPhase2AdvancedDemo } from './composition-orchestrator';

// Run built-in demos with mock invoker
await runPhase2Demo();
await runPhase2AdvancedDemo();
```

---

## Migration from Phase 1

No breaking changes. Phase 1 code continues to work:

```typescript
// Old Phase 1 code still works
const plan = analyzeScheduling(detection);
const result = await orchestrateComposition(plan, invoker, task);
```

To adopt Phase 2 features, wrap with `CrossSegmentComposer`:

```typescript
// New Phase 2 code
const composer = new CrossSegmentComposer();
const result = await composer.composeAndOrchestrate(query, invoker);
```

Or mix: use `detectComposition` + `analyzeScheduling` directly, then feed to `orchestrateComposition` with custom handlers.

---

## Known Limitations & Future work

- **Resource pool**: Currently in-memory; persisting to Supabase requires a background job to checkpoint chunks.
- **Cost estimation**: Uses fixed heuristics; real costs vary by query complexity. Future: call `tokenizer.estimate()` on actual requests.
- **Tier escalation**: `selectOptimalTier()` uses hard-coded confidence thresholds; future: learn from historical SLA/cost trade-offs.
- **Ad-hoc composition**: Compositions not matching named patterns are flagged `requiresHumanConfirmation: true`; policy pending Manta N approval.

---

## Troubleshooting

### Composition not detected

- Check if query matches any of the 5 named patterns (UHE, ETE+subestação, Porto+pista, adutora×barragem, claim+orçamento).
- If not, check if 2+ agents score above `matchThreshold` (default 0.28) via keyword matching.
- Use `allScores` in the detection result to debug why an agent wasn't picked up.

```typescript
const result = detectComposition(query, { matchThreshold: 0.2 });  // Lower threshold
console.log(result.allScores);  // Debug all scores
```

### Budget exceeded

- The composition's estimated token count exceeds `globalBudgetTokens`.
- Lower the budget or reduce the number of agents (e.g., more selective `matchThreshold`).
- Check if RAG chunks can be pre-loaded in `ResourcePool` to reduce queries.

### Fallback triggered (tier escalation)

- An agent failed at its assigned tier (haiku or sonnet) and escalated to the next (sonnet or opus).
- Check the agent's `fallback_reason` in the event log; may indicate a timeout or transient error.
- Increase the per-agent `timeoutMs` in `AnalyzeSchedulingOptions.timeoutOverridesMs`.

### Circuit breaker opened

- Too many failures in rapid succession (`failureThreshold` consecutive failures).
- Wait `resetTimeoutMs` (default 30s) before retrying, or reset manually via `new CircuitBreaker()`.

---

## References

- **Composition orchestrator source:** `/infra/agent-registry/composition-orchestrator.ts`
- **Schemas:** CompositionEvent (this doc), AgentDefinition, SchedulingPlan
- **Routing keywords:** `DEFAULT_ROUTING_KEYWORDS` (sync with `maestro_routing_keywords` Supabase table)
- **Agent frontmatter:** `.claude/agents/*.md` (parsed by `parseAgentFile()`)
- **Phase 1 docs:** `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` §2.2

---

**Questions?** Reach out to manta-16-arquiteto-ia or file an issue in the Manta Maestro registry.
