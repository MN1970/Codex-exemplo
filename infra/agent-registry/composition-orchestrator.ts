/**
 * composition-orchestrator.ts
 * =====================================================================
 * Manta Maestro — Multi-Agent Composition System
 * ---------------------------------------------------------------------
 * Implements Fase 2.2 "Multi-agent composition" from
 * docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md (§2.2, owner: Manta 16 —
 * arquiteto-ia), and formalizes the `CompositionPlan` sketch already
 * drafted there (§4.2, `maestro-v2.ts`) into a working implementation.
 *
 * Three entry points, matching the ticket exactly:
 *
 *   detectComposition(query)      → identifica se 2+ agentes são
 *                                    necessários (ex: UHE = barragens
 *                                    + energia)
 *   analyzeScheduling(agents)     → serial vs paralelo (grafo de
 *                                    dependências → estágios)
 *   orchestrateComposition(plan)  → dispatch & merge de resultados
 *                                    (com fallback e timeout)
 *
 * Design goals / how this fits the rest of the repo:
 *
 *   - Reuses the SAME agent metadata shape produced by
 *     `infra/agent-registry/lib/parse-agent-md.js` (id, description,
 *     expertise_primary/secondary, keywords, model, handoffs_to) —
 *     see AgentDefinition below. The 5 vertical agents that live in
 *     THIS repo (.claude/agents/*.md — S6-S10, per README.md) are
 *     loaded from disk; the horizontais (Manta 00-16) and S1-S4
 *     verticais that live in the OPERATIONAL Maestro repo are
 *     represented as documented stubs (EXTERNAL_AGENT_STUBS) sourced
 *     straight from CLAUDE.md, so composition detection still works
 *     end-to-end without vendoring agents this repo doesn't own.
 *
 *   - Keyword scoring mirrors `maestro_routing_keywords` (see
 *     supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql) —
 *     weighted keyword hits, not naive counting — so a future
 *     migration to reading that table from Supabase is a drop-in
 *     swap of `loadRoutingKeywords()`.
 *
 *   - `orchestrateComposition` accepts an injected `isRoutable?`
 *     predicate with the exact contract of
 *     `services/heartbeat/heartbeat-service.js`'s
 *     `HealthRegistry.isRoutable(agentId)`, so a caller can wire in
 *     live health data without this module importing an HTTP service.
 *
 *   - `AgentInvoker` is a small injected interface (same pattern as
 *     `registerAgentFromFile({ agentInvoker })` in
 *     auto-registration-service.js) — this module never assumes HOW
 *     an agent actually runs. A reference `AnthropicAgentInvoker` is
 *     provided (uses `@anthropic-ai/sdk`, maps each agent's `model`
 *     tier to a concrete Claude model ID, and loads the agent's
 *     system prompt straight from its `.claude/agents/*.md` body) for
 *     when agents are dispatched as direct Claude API calls rather
 *     than as Claude Code subagent tasks.
 *
 * ---------------------------------------------------------------------
 * DIAGRAM 1 — End-to-end pipeline
 * ---------------------------------------------------------------------
 *
 *   ```mermaid
 *   flowchart LR
 *     Q[query] --> DC[detectComposition]
 *     DC -->|isComposite=false| SINGLE[Maestro roteia\npara 1 agente]
 *     DC -->|isComposite=true| AS[analyzeScheduling]
 *     AS --> SP[SchedulingPlan\n(stages = DAG topo-levels)]
 *     SP --> OC[orchestrateComposition]
 *     OC --> INV{{AgentInvoker}}
 *     INV --> R1[agente A]
 *     INV --> R2[agente B]
 *     R1 --> MERGE[merge / defaultMerge]
 *     R2 --> MERGE
 *     MERGE --> OUT[OrchestrationResult]
 *   ```
 *
 * ---------------------------------------------------------------------
 * DIAGRAM 2 — Dependency graph examples (the 3 canonical cases)
 * ---------------------------------------------------------------------
 *
 *   ```mermaid
 *   graph TD
 *     subgraph UHE [UHE — serial: energia depende dos dados da barragem]
 *       B1[agente-barragens\nprimary] -->|queda liquida, vazao,\nNA maximo maximorum| E1[agente-energia\nsecondary]
 *     end
 *     subgraph ETE_SE [ETE + Subestacao — parallel: escopos independentes]
 *       S2[agente-saneamento\nprimary]
 *       E2[agente-energia\nsecondary]
 *     end
 *     subgraph PORTO_PISTA [Porto + pista de carga — parallel: handoff apenas no merge]
 *       P3[agente-portos\nprimary]
 *       A3[agente-aeroportos\nsecondary]
 *     end
 *   ```
 *
 * ---------------------------------------------------------------------
 * DIAGRAM 3 — Kahn's-algorithm staging (generic N-agent case)
 * ---------------------------------------------------------------------
 *
 *   ```mermaid
 *   graph LR
 *     A((A: no deps)) --> C((C: depende de A e B))
 *     B((B: no deps)) --> C
 *     C --> D((D: depende de C))
 *     %% stage 0 = [A, B]  (parallel — indegree 0)
 *     %% stage 1 = [C]     (serial after A,B settle)
 *     %% stage 2 = [D]     (serial after C settles)
 *   ```
 *
 * ---------------------------------------------------------------------
 * DIAGRAM 4 — orchestrateComposition sequence (fallback + timeout)
 * ---------------------------------------------------------------------
 *
 *   ```mermaid
 *   sequenceDiagram
 *     participant O as orchestrateComposition
 *     participant CB as CircuitBreaker
 *     participant I as AgentInvoker
 *     O->>CB: isOpen()?
 *     CB-->>O: closed
 *     O->>I: invoke(agentId, task, timeout=Tms)
 *     alt sucesso dentro do timeout
 *       I-->>O: { output, modelUsed }
 *       O->>CB: recordSuccess()
 *     else timeout / erro
 *       I-->>O: throw / AbortError
 *       O->>O: retry (backoff) até maxRetries
 *       O->>O: escalateTier (sonnet -> opus) se configurado
 *       O->>CB: recordFailure()
 *       CB-->>O: open? (>= failureThreshold)
 *       O->>O: se agente primary falhar de forma irrecuperavel,\n aborta estagios dependentes (status='partial')
 *     end
 *   ```
 * =====================================================================
 */

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { join, basename } from 'node:path';

// =====================================================================
// 1. TYPES
// =====================================================================

/** Model tier as used throughout Manta's agent frontmatter (`model:`). */
export type ModelTier = 'haiku' | 'sonnet' | 'opus';

/**
 * Normalized agent metadata. Field names intentionally mirror
 * `infra/agent-registry/lib/parse-agent-md.js`'s return shape (and the
 * `agents` Supabase table it upserts into) so the two can be unified
 * later without a remapping layer.
 */
export interface AgentDefinition {
  /** e.g. "agente-barragens" — matches `.claude/agents/<id>.md`. */
  id: string;
  name: string;
  description: string;
  expertisePrimary: string[];
  expertiseSecondary: string[];
  /** Alias of expertisePrimary, kept for parity with parse-agent-md.js's `keywords`. */
  keywords: string[];
  model: ModelTier;
  handoffsTo: string[];
  /** Segment code, e.g. "S10" — used for CLAUDE.md cross-referencing. */
  segment: string;
  /** Human-readable Manta code, e.g. "Manta 03-S10" or "Manta 05". */
  mantaCode: string;
  /** Whether this definition was loaded from a real `.claude/agents/*.md`
   *  file in this repo, or is a documented stub for an agent that lives
   *  in the operational Maestro repo (see README.md § "Arquivos deste
   *  repositório"). Composition detection treats both identically;
   *  this only matters for diagnostics/logging. */
  source: 'local-md' | 'external-stub';
  /** Absolute path to the source `.md` file, when `source === 'local-md'`. */
  sourcePath?: string;
  /** Raw body (after frontmatter) — used as the system prompt by
   *  AnthropicAgentInvoker when dispatching real Claude API calls. */
  body?: string;
  /** false for Manta 00 (maestro) — it is the router, never a
   *  composable worker, so it is excluded from detectComposition's
   *  candidate pool but kept in the registry for completeness. */
  composable: boolean;
}

/** A single (agentSlug, keyword, priority) entry — mirrors the
 *  `maestro_routing_keywords` table shape 1:1. Priority is an
 *  arbitrary weight (roughly 60-120 in the existing migration), not a
 *  probability — higher means a stronger, less ambiguous signal. */
export interface RoutingKeyword {
  agentId: string;
  keyword: string;
  priority: number;
}

export type AgentRole = 'primary' | 'secondary' | 'consult';

/** One agent's participation in a (possible) composition. */
export interface AgentInvolvement {
  agentId: string;
  role: AgentRole;
  /** Raw weighted keyword score (sum of matched keyword priorities). */
  score: number;
  /** Saturating 0..1 confidence derived from `score`. */
  confidence: number;
  matchedKeywords: string[];
  rationale: string;
}

/** `from` must complete before `to` starts. Mirrors the
 *  `dependencies: { [key: string]: string[] }` sketch in
 *  docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md, expressed as an edge
 *  list (easier to validate/topo-sort than an adjacency map). */
export interface DependencyEdge {
  from: string;
  to: string;
  reason: string;
}

export type SchedulingHint = 'serial' | 'parallel' | 'auto';

/** A known, named composition rule (UHE, ETE+subestação, ...). Checked
 *  in priority order before falling back to generic ad-hoc detection. */
export interface CompositionPattern {
  id: string;
  name: string;
  description: string;
  /** Returns true if this pattern applies to the query. Receives the
   *  normalized (lowercased, diacritics-stripped) query plus the
   *  per-agent scores already computed by detectComposition, so a
   *  pattern can combine explicit regexes with keyword-score signals. */
  match(normalizedQuery: string, scores: Map<string, AgentInvolvement>): boolean;
  agents: Array<{ agentId: string; role: AgentRole; rationale: string }>;
  dependencies: DependencyEdge[];
  schedulingHint: SchedulingHint;
  /** Per tests/routing.md "Casos ambíguos": several composite patterns
   *  are policy calls pending Manta N approval, not purely mechanical
   *  routing — flag them so the caller can gate on human confirmation. */
  requiresHumanConfirmation: boolean;
}

export interface DetectCompositionOptions {
  /** Confidence a single agent must reach to be considered "matched"
   *  at all. Default 0.28 (≈ one strong keyword hit). */
  matchThreshold?: number;
  /** For the generic (non-pattern) fallback: minimum number of
   *  distinct agents above matchThreshold to call it a composition.
   *  Default 2. */
  minAgentsForComposite?: number;
  /** Override/extend the registry used for scoring. Defaults to
   *  `buildAgentRegistry()`. */
  registry?: Map<string, AgentDefinition>;
  /** Override/extend the routing keyword index. Defaults to
   *  `DEFAULT_ROUTING_KEYWORDS`. */
  routingKeywords?: RoutingKeyword[];
  /** Extra composition patterns checked before the built-in ones. */
  extraPatterns?: CompositionPattern[];
}

/** Output of detectComposition. Deliberately shaped so it can be
 *  passed straight into analyzeScheduling — `agents`, `dependencies`,
 *  and `schedulingHint` are the exact fields analyzeScheduling reads. */
export interface CompositionDetectionResult {
  query: string;
  isComposite: boolean;
  /** Set only when a named CompositionPattern matched. */
  patternId?: string;
  patternName?: string;
  agents: AgentInvolvement[];
  dependencies: DependencyEdge[];
  schedulingHint: SchedulingHint;
  /** Overall confidence in the composition call itself (not any one
   *  agent) — min of the participating agents' confidences for named
   *  patterns, or the mean for ad-hoc detections. */
  confidence: number;
  requiresHumanConfirmation: boolean;
  rationale: string;
  /** Every candidate agent's score, matched or not — useful for
   *  debugging/explainability ("why didn't X get picked up?"). */
  allScores: AgentInvolvement[];
}

// --- Scheduling -------------------------------------------------------

export interface FallbackPolicy {
  maxRetries: number;
  backoffMs: number;
  /** On final failure, retry once more at the next-higher model tier
   *  (haiku -> sonnet -> opus). No-op once already at 'opus'. */
  escalateTierOnFinalFailure: boolean;
  timeoutMs: number;
}

/** A resolved node inside a SchedulingPlan — an AgentInvolvement plus
 *  everything orchestrateComposition needs to actually dispatch it. */
export interface ScheduledAgent extends AgentInvolvement {
  model: ModelTier;
  fallbackPolicy: FallbackPolicy;
  /** Direct predecessors (must have completed before this agent runs). */
  dependsOn: string[];
}

export interface SchedulingStage {
  index: number;
  agents: ScheduledAgent[];
  /** max timeout across this stage's agents (this stage runs them in
   *  parallel, so wall-clock is bounded by the slowest one). */
  estimatedMs: number;
}

export interface CompositionGraph {
  nodes: string[];
  edges: DependencyEdge[];
}

export interface SchedulingPlan {
  stages: SchedulingStage[];
  graph: CompositionGraph;
  /** 'parallel' (single stage, no deps), 'serial' (one agent per
   *  stage), or 'hybrid' (some stages have >1 agent, some don't). */
  strategy: 'parallel' | 'serial' | 'hybrid';
  /** Sum of each stage's estimatedMs — a conservative wall-clock
   *  upper bound assuming every stage runs at its slowest agent. */
  totalEstimatedMs: number;
  source: CompositionDetectionResult | CompositionPlanInput;
}

export interface AnalyzeSchedulingOptions {
  /** Per-agent-id timeout overrides (ms). Falls back to per-tier
   *  defaults (DEFAULT_TIMEOUTS_MS) when absent. */
  timeoutOverridesMs?: Record<string, number>;
  /** Per-agent-id fallback policy overrides (merged over defaults). */
  fallbackOverrides?: Record<string, Partial<FallbackPolicy>>;
  registry?: Map<string, AgentDefinition>;
}

/** Minimal shape analyzeScheduling actually needs — satisfied by
 *  CompositionDetectionResult, or constructible by hand for ad-hoc /
 *  test scenarios ("monte uma task force de N agentes"). */
export interface CompositionPlanInput {
  agents: AgentInvolvement[];
  dependencies?: DependencyEdge[];
  schedulingHint?: SchedulingHint;
}

export class CompositionCycleError extends Error {
  constructor(public readonly cycle: string[]) {
    super(`Ciclo de dependência detectado entre agentes: ${cycle.join(' -> ')}`);
    this.name = 'CompositionCycleError';
  }
}

// --- Orchestration ------------------------------------------------------

export interface OrchestrationTask {
  query: string;
  /** Arbitrary caller-supplied context (project id, GR, locale, ...). */
  metadata?: Record<string, unknown>;
}

export type AgentInvocationStatus = 'success' | 'error' | 'timeout' | 'skipped';

export interface AgentInvocationResult {
  agentId: string;
  status: AgentInvocationStatus;
  output?: string;
  structuredOutput?: unknown;
  error?: string;
  attempts: number;
  tookMs: number;
  modelUsed: string;
  escalated: boolean;
}

/** What an AgentInvoker receives for a single call. `upstreamContext`
 *  carries the results of every agent this one depends on (per the
 *  SchedulingPlan's dependency edges), so e.g. agente-energia's
 *  request for a UHE composition includes agente-barragens' output. */
export interface AgentInvokerRequest {
  agentId: string;
  agentDefinition: AgentDefinition;
  task: OrchestrationTask;
  role: AgentRole;
  upstreamContext: Record<string, AgentInvocationResult>;
  /** Set on a fallback-tier retry (e.g. 'opus' after 'sonnet' failed). */
  modelOverride?: ModelTier;
  signal: AbortSignal;
}

export interface AgentInvokerResponse {
  output: string;
  structuredOutput?: unknown;
  modelUsed: string;
}

/** The one thing this module doesn't decide: HOW an agent actually
 *  runs (Claude API call, Claude Code Task-tool subagent, HTTP
 *  microservice, ...). Same injection pattern as
 *  `registerAgentFromFile({ agentInvoker })` in
 *  auto-registration-service.js. */
export interface AgentInvoker {
  invoke(request: AgentInvokerRequest): Promise<AgentInvokerResponse>;
}

export interface CircuitBreakerOptions {
  /** Consecutive failures before the breaker opens. Default 3. */
  failureThreshold?: number;
  /** How long the breaker stays open before allowing a half-open
   *  probe. Default 30s. */
  resetTimeoutMs?: number;
}

export type OrchestrationStatus = 'success' | 'partial' | 'failed' | 'aborted';

export interface OrchestrationResult {
  status: OrchestrationStatus;
  plan: SchedulingPlan;
  agentResults: Record<string, AgentInvocationResult>;
  stagesExecuted: number;
  mergedOutput: string;
  errors: string[];
  totalMs: number;
}

export interface OrchestrateOptions {
  /** If a `primary` agent in a stage fails irrecoverably, abort
   *  remaining stages by default. Set true to keep going in a
   *  degraded ("partial") mode instead. Default false. */
  continueOnPrimaryFailure?: boolean;
  circuitBreaker?: CircuitBreakerOptions;
  /** Injected health check — see services/heartbeat/heartbeat-service.js
   *  `HealthRegistry.isRoutable(agentId)`. Agents reported as
   *  not-routable are skipped (status: 'skipped') before ever being
   *  dispatched, and treated as a failure for circuit-breaker/primary
   *  purposes. Optional — when absent every agent is assumed routable. */
  isRoutable?(agentId: string): boolean;
  /** Custom merge strategy. Defaults to `defaultMerge`. */
  merge?(results: Record<string, AgentInvocationResult>, plan: SchedulingPlan): string;
}

// =====================================================================
// 2. CONSTANTS — model mapping, timeouts, registry data
// =====================================================================

/** Claude API model IDs per tier. Per the current model catalog:
 *  claude-opus-5 / claude-sonnet-5 / claude-haiku-4-5. Kept as a single
 *  map so a model migration (see shared/model-migration.md in the
 *  claude-api skill) only touches one place. */
export const MODEL_TIER_TO_ID: Record<ModelTier, string> = {
  haiku: 'claude-haiku-4-5',
  sonnet: 'claude-sonnet-5',
  opus: 'claude-opus-5',
};

/** Conservative per-tier wall-clock budgets. Opus/Sonnet agents in
 *  Manta typically read/search/grep before answering (tools: [Read,
 *  Grep, Glob, Bash, WebSearch, WebFetch] per .claude/agents/*.md), so
 *  these are generous relative to a bare chat completion. */
export const DEFAULT_TIMEOUTS_MS: Record<ModelTier, number> = {
  haiku: 45_000,
  sonnet: 120_000,
  opus: 240_000,
};

const TIER_ORDER: ModelTier[] = ['haiku', 'sonnet', 'opus'];

/** Escalates one tier (haiku -> sonnet -> opus). Returns null once
 *  already at the top — there's nowhere further to escalate to. */
export function escalateTier(tier: ModelTier): ModelTier | null {
  const idx = TIER_ORDER.indexOf(tier);
  return idx >= 0 && idx < TIER_ORDER.length - 1 ? TIER_ORDER[idx + 1] : null;
}

/**
 * Weighted routing keywords. The S6-S10 block below is a verbatim
 * transcription of `maestro_routing_keywords` in
 * supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql (priorities
 * included) — swap `loadRoutingKeywords()` for a Supabase query and
 * nothing else in this file needs to change. S1-S4 and the
 * horizontais are derived from CLAUDE.md's "ROUTING — Maestro" block
 * and its agent table, at a flat priority of 90 (no migration exists
 * for them yet since they live in the operational Maestro repo).
 */
export const DEFAULT_ROUTING_KEYWORDS: RoutingKeyword[] = [
  // --- Saneamento (S8) — supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql
  { agentId: 'agente-saneamento', keyword: 'saneamento', priority: 100 },
  { agentId: 'agente-saneamento', keyword: 'eta', priority: 100 },
  { agentId: 'agente-saneamento', keyword: 'ete', priority: 100 },
  { agentId: 'agente-saneamento', keyword: 'adutora', priority: 100 },
  { agentId: 'agente-saneamento', keyword: 'esgoto', priority: 100 },
  { agentId: 'agente-saneamento', keyword: 'aysa', priority: 120 },
  { agentId: 'agente-saneamento', keyword: 'drenagem urbana', priority: 95 },
  { agentId: 'agente-saneamento', keyword: 'snis', priority: 100 },
  { agentId: 'agente-saneamento', keyword: 'pmsb', priority: 90 },
  { agentId: 'agente-saneamento', keyword: 'lei 14.026', priority: 100 },
  // --- Energia (S9)
  { agentId: 'agente-energia', keyword: 'transmissão', priority: 100 },
  { agentId: 'agente-energia', keyword: 'lt', priority: 90 },
  { agentId: 'agente-energia', keyword: 'subestação', priority: 100 },
  { agentId: 'agente-energia', keyword: 'aneel', priority: 100 },
  { agentId: 'agente-energia', keyword: 'rap', priority: 90 },
  { agentId: 'agente-energia', keyword: 'leilão transmissão', priority: 95 },
  { agentId: 'agente-energia', keyword: 'ons', priority: 90 },
  { agentId: 'agente-energia', keyword: 'epe', priority: 90 },
  { agentId: 'agente-energia', keyword: 'kv', priority: 70 },
  { agentId: 'agente-energia', keyword: 'geração', priority: 65 },
  { agentId: 'agente-energia', keyword: 'uhe', priority: 60 }, // low weight alone — UHE is a composite trigger, see COMPOSITION_PATTERNS
  // --- Portos (S6)
  { agentId: 'agente-portos', keyword: 'porto', priority: 80 },
  { agentId: 'agente-portos', keyword: 'terminal', priority: 70 },
  { agentId: 'agente-portos', keyword: 'antaq', priority: 100 },
  { agentId: 'agente-portos', keyword: 'dragagem', priority: 100 },
  { agentId: 'agente-portos', keyword: 'molhe', priority: 100 },
  { agentId: 'agente-portos', keyword: 'berço', priority: 90 },
  { agentId: 'agente-portos', keyword: 'calado', priority: 90 },
  { agentId: 'agente-portos', keyword: 'contêiner', priority: 80 },
  { agentId: 'agente-portos', keyword: 'granel', priority: 80 },
  // --- Aeroportos (S7)
  { agentId: 'agente-aeroportos', keyword: 'aeroporto', priority: 100 },
  { agentId: 'agente-aeroportos', keyword: 'pista pouso', priority: 100 },
  { agentId: 'agente-aeroportos', keyword: 'anac', priority: 100 },
  { agentId: 'agente-aeroportos', keyword: 'icao', priority: 100 },
  { agentId: 'agente-aeroportos', keyword: 'tps', priority: 90 },
  { agentId: 'agente-aeroportos', keyword: 'teca', priority: 90 },
  { agentId: 'agente-aeroportos', keyword: 'balizamento', priority: 100 },
  { agentId: 'agente-aeroportos', keyword: 'pista de carga', priority: 90 },
  // --- Barragens (S10)
  { agentId: 'agente-barragens', keyword: 'barragem', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'vertedouro', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'cfrd', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'ccr', priority: 80 },
  { agentId: 'agente-barragens', keyword: 'rejeitos', priority: 110 },
  { agentId: 'agente-barragens', keyword: 'pnsb', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'icold', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'cbdb', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'tsf', priority: 100 },
  { agentId: 'agente-barragens', keyword: 'barragem de rejeitos', priority: 110 },
  // --- S1 Rodovias (external — CLAUDE.md routing rule)
  { agentId: 'agente-infraestrutura-s1', keyword: 'rodovia', priority: 90 },
  { agentId: 'agente-infraestrutura-s1', keyword: 'pavimento', priority: 90 },
  { agentId: 'agente-infraestrutura-s1', keyword: 'cbuq', priority: 90 },
  { agentId: 'agente-infraestrutura-s1', keyword: 'bgs', priority: 85 },
  { agentId: 'agente-infraestrutura-s1', keyword: 'terraplenagem', priority: 85 },
  { agentId: 'agente-infraestrutura-s1', keyword: 'sicro', priority: 90 },
  { agentId: 'agente-infraestrutura-s1', keyword: 'dnit', priority: 85 },
  // --- S2 OAE (external)
  { agentId: 'agente-infraestrutura-s2', keyword: 'ponte', priority: 90 },
  { agentId: 'agente-infraestrutura-s2', keyword: 'viaduto', priority: 90 },
  { agentId: 'agente-infraestrutura-s2', keyword: 'oae', priority: 90 },
  { agentId: 'agente-infraestrutura-s2', keyword: 'nbr 7187', priority: 90 },
  { agentId: 'agente-infraestrutura-s2', keyword: 'túnel rodoviário', priority: 85 },
  // --- S3 Ferrovia (external)
  { agentId: 'agente-infraestrutura-s3', keyword: 'ferrovia', priority: 90 },
  { agentId: 'agente-infraestrutura-s3', keyword: 'trilho', priority: 85 },
  { agentId: 'agente-infraestrutura-s3', keyword: 'amv', priority: 90 },
  { agentId: 'agente-infraestrutura-s3', keyword: 'dormente', priority: 85 },
  { agentId: 'agente-infraestrutura-s3', keyword: 'via permanente', priority: 85 },
  // --- S4 Metrô (external)
  { agentId: 'agente-infraestrutura-s4', keyword: 'metrô', priority: 90 },
  { agentId: 'agente-infraestrutura-s4', keyword: 'natm', priority: 90 },
  { agentId: 'agente-infraestrutura-s4', keyword: 'psd', priority: 85 },
  { agentId: 'agente-infraestrutura-s4', keyword: 'vlt', priority: 85 },
  // --- Horizontais (external — approximate; refine when the
  // operational Maestro registry is wired in, per manta-maestro skill)
  { agentId: 'manta-01-claims', keyword: 'claim', priority: 85 },
  { agentId: 'manta-01-claims', keyword: 'reequilíbrio', priority: 90 },
  { agentId: 'manta-01-claims', keyword: 'reequilibrio econômico-financeiro', priority: 90 },
  { agentId: 'manta-01-claims', keyword: 'quantum', priority: 75 },
  { agentId: 'manta-05-orcamento', keyword: 'orçamento', priority: 90 },
  { agentId: 'manta-05-orcamento', keyword: 'sinapi', priority: 85 },
  { agentId: 'manta-05-orcamento', keyword: 'bdi', priority: 80 },
  { agentId: 'manta-05-orcamento', keyword: 'planilha orçamentária', priority: 85 },
  { agentId: 'manta-06-modelagem', keyword: 'modelagem financeira', priority: 90 },
  { agentId: 'manta-06-modelagem', keyword: 'fluxo de caixa', priority: 80 },
  { agentId: 'manta-06-modelagem', keyword: 'tir', priority: 75 },
  { agentId: 'manta-06-modelagem', keyword: 'vpl', priority: 75 },
];

/** Groups DEFAULT_ROUTING_KEYWORDS by agentId for O(1) lookup during
 *  scoring. Rebuilt once per detectComposition call (cheap — this list
 *  is small; a Supabase-backed loader would cache this instead). */
function indexRoutingKeywords(keywords: RoutingKeyword[]): Map<string, RoutingKeyword[]> {
  const index = new Map<string, RoutingKeyword[]>();
  for (const kw of keywords) {
    const bucket = index.get(kw.agentId);
    if (bucket) bucket.push(kw);
    else index.set(kw.agentId, [kw]);
  }
  return index;
}

/**
 * Agents documented in CLAUDE.md that live in the operational Maestro
 * repo and therefore have no `.claude/agents/*.md` file here (see
 * README.md § "Arquivos deste repositório"). Kept minimal — just
 * enough metadata for composition detection and scheduling to work —
 * and clearly marked `source: 'external-stub'` so nothing pretends
 * these are authoritative definitions.
 */
export const EXTERNAL_AGENT_STUBS: AgentDefinition[] = [
  {
    id: 'manta-00-maestro',
    name: 'maestro (router)',
    description: 'Manta 00 — roteador master. Nunca é um agente composable; escolhe/orquestra os demais.',
    expertisePrimary: [],
    expertiseSecondary: [],
    keywords: [],
    model: 'sonnet',
    handoffsTo: [],
    segment: 'A1',
    mantaCode: 'Manta 00',
    source: 'external-stub',
    composable: false,
  },
  {
    id: 'agente-infraestrutura-s1',
    name: 'agente-infraestrutura (Rodovias)',
    description: 'Manta 03-S1 — rodovias, pavimento, terraplenagem, SICRO/DNIT.',
    expertisePrimary: ['rodovia', 'pavimento', 'CBUQ', 'BGS', 'terraplenagem', 'SICRO', 'DNIT'],
    expertiseSecondary: [],
    keywords: ['rodovia', 'pavimento', 'CBUQ', 'BGS', 'terraplenagem', 'SICRO', 'DNIT'],
    model: 'sonnet',
    handoffsTo: ['manta-05-orcamento'],
    segment: 'S1',
    mantaCode: 'Manta 03-S1',
    source: 'external-stub',
    composable: true,
  },
  {
    id: 'agente-infraestrutura-s2',
    name: 'agente-infraestrutura (OAE)',
    description: 'Manta 03-S2 — pontes, viadutos, OAE, túneis rodoviários.',
    expertisePrimary: ['ponte', 'viaduto', 'OAE', 'NBR 7187', 'túnel rodoviário'],
    expertiseSecondary: [],
    keywords: ['ponte', 'viaduto', 'OAE', 'NBR 7187', 'túnel rodoviário'],
    model: 'sonnet',
    handoffsTo: [],
    segment: 'S2',
    mantaCode: 'Manta 03-S2',
    source: 'external-stub',
    composable: true,
  },
  {
    id: 'agente-infraestrutura-s3',
    name: 'agente-infraestrutura (Ferrovia)',
    description: 'Manta 03-S3 — ferrovia, via permanente, AMV, dormentes.',
    expertisePrimary: ['ferrovia', 'trilho', 'AMV', 'dormente', 'via permanente'],
    expertiseSecondary: [],
    keywords: ['ferrovia', 'trilho', 'AMV', 'dormente', 'via permanente'],
    model: 'sonnet',
    handoffsTo: [],
    segment: 'S3',
    mantaCode: 'Manta 03-S3',
    source: 'external-stub',
    composable: true,
  },
  {
    id: 'agente-infraestrutura-s4',
    name: 'agente-infraestrutura (Metrô)',
    description: 'Manta 03-S4 — metrô, NATM, PSD, VLT.',
    expertisePrimary: ['metrô', 'estação', 'NATM', 'PSD', 'linha 4', 'linha 5', 'VLT'],
    expertiseSecondary: [],
    keywords: ['metrô', 'estação', 'NATM', 'PSD', 'linha 4', 'linha 5', 'VLT'],
    model: 'sonnet',
    handoffsTo: [],
    segment: 'S4',
    mantaCode: 'Manta 03-S4',
    source: 'external-stub',
    composable: true,
  },
  {
    id: 'manta-01-claims',
    name: 'claims',
    description: 'Manta 01 — claims, reequilíbrio econômico-financeiro, quantum.',
    expertisePrimary: ['claim', 'reequilíbrio', 'quantum'],
    expertiseSecondary: [],
    keywords: ['claim', 'reequilíbrio', 'quantum'],
    model: 'opus',
    handoffsTo: ['manta-05-orcamento'],
    segment: 'A1',
    mantaCode: 'Manta 01',
    source: 'external-stub',
    composable: true,
  },
  {
    id: 'manta-05-orcamento',
    name: 'orcamento',
    description: 'Manta 05 — orçamento, SICRO/SINAPI, BDI.',
    expertisePrimary: ['orçamento', 'SICRO', 'SINAPI', 'BDI'],
    expertiseSecondary: [],
    keywords: ['orçamento', 'SICRO', 'SINAPI', 'BDI'],
    model: 'sonnet',
    handoffsTo: [],
    segment: 'A1',
    mantaCode: 'Manta 05',
    source: 'external-stub',
    composable: true,
  },
  {
    id: 'manta-06-modelagem',
    name: 'modelagem',
    description: 'Manta 06 — modelagem financeira (TIR, VPL, fluxo de caixa).',
    expertisePrimary: ['modelagem financeira', 'fluxo de caixa', 'TIR', 'VPL'],
    expertiseSecondary: [],
    keywords: ['modelagem financeira', 'fluxo de caixa', 'TIR', 'VPL'],
    model: 'sonnet',
    handoffsTo: [],
    segment: 'A1',
    mantaCode: 'Manta 06',
    source: 'external-stub',
    composable: true,
  },
];

// =====================================================================
// 3. REGISTRY LOADING — parses .claude/agents/*.md (local, real S6-S10)
// =====================================================================

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/;

/** Small YAML-subset parser mirroring
 *  `infra/agent-registry/lib/parse-agent-md.js`'s `parseFrontmatterYaml`
 *  (native TS port, no runtime dependency on the CommonJS module, so
 *  this file works standalone regardless of the caller's module
 *  system/tsconfig). Supports scalars and `key: [a, b, c]` arrays —
 *  exactly what `.claude/agents/*.md` frontmatter uses today. */
function parseFrontmatterYaml(raw: string): Record<string, string | string[]> {
  const root: Record<string, string | string[]> = {};
  for (const rawLine of raw.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    const kv = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!kv) continue;
    const [, key, valueRaw] = kv;
    root[key] = parseScalarOrArray(valueRaw);
  }
  return root;
}

function parseScalarOrArray(value: string): string | string[] {
  const v = value.trim();
  if (v.startsWith('[') && v.endsWith(']')) {
    const inner = v.slice(1, -1).trim();
    if (!inner) return [];
    return inner.split(',').map((s) => stripQuotes(s.trim())).filter(Boolean);
  }
  return stripQuotes(v);
}

function stripQuotes(s: string): string {
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  return s;
}

/** Same heuristic as parse-agent-md.js's `deriveExpertiseFromDescription`:
 *  Manta descriptions end with "Roteia quando o usuário menciona X, Y,
 *  Z." — reuse that comma list as the keyword set. */
function deriveExpertiseFromDescription(description: string): string[] {
  if (!description) return [];
  const match = description.match(/menciona\s+(.+?)\.?$/i);
  if (!match) return [];
  return match[1].split(',').map((s) => s.trim()).filter(Boolean).slice(0, 20);
}

function extractSegment(description: string): { segment: string; mantaCode: string } {
  const m = description.match(/Manta\s+([\w-]+)/i);
  const mantaCode = m ? `Manta ${m[1]}` : 'Manta ?';
  const segMatch = m ? m[1].match(/S\d+/i) : null;
  return { segment: segMatch ? segMatch[0].toUpperCase() : (m ? m[1] : '?'), mantaCode };
}

/** Parses one `.claude/agents/<id>.md` file into an AgentDefinition. */
export function parseAgentFile(filePath: string): AgentDefinition {
  const raw = readFileSync(filePath, 'utf8');
  const match = raw.match(FRONTMATTER_RE);
  if (!match) {
    throw new Error(`Sem frontmatter YAML em ${filePath}`);
  }
  const [, frontmatterRaw, body] = match;
  const fm = parseFrontmatterYaml(frontmatterRaw);

  const id = typeof fm.name === 'string' ? fm.name : basename(filePath, '.md');
  const description = typeof fm.description === 'string' ? fm.description : '';
  const keywords = deriveExpertiseFromDescription(description);
  const model = (typeof fm.model === 'string' ? fm.model : 'sonnet') as ModelTier;
  const { segment, mantaCode } = extractSegment(description);

  return {
    id,
    name: id,
    description,
    expertisePrimary: keywords,
    expertiseSecondary: [],
    keywords,
    model: TIER_ORDER.includes(model) ? model : 'sonnet',
    handoffsTo: [],
    segment,
    mantaCode,
    source: 'local-md',
    sourcePath: filePath,
    body: body.trim(),
    composable: true,
  };
}

/** Scans `.claude/agents/*.md` (defaults to the repo-relative path) and
 *  parses every file found. Returns [] (never throws) if the directory
 *  doesn't exist, so this module degrades gracefully outside this repo. */
export function loadLocalAgentDefinitions(agentsDir = join(__dirname, '..', '..', '.claude', 'agents')): AgentDefinition[] {
  if (!existsSync(agentsDir)) return [];
  return readdirSync(agentsDir)
    .filter((f) => f.endsWith('.md'))
    .map((f) => parseAgentFile(join(agentsDir, f)));
}

/** Builds the full registry: real local agents (.claude/agents/*.md)
 *  plus the documented external stubs, keyed by agent id. Local
 *  definitions always win on id collision (they're authoritative). */
export function buildAgentRegistry(agentsDir?: string): Map<string, AgentDefinition> {
  const registry = new Map<string, AgentDefinition>();
  for (const stub of EXTERNAL_AGENT_STUBS) registry.set(stub.id, stub);
  for (const local of loadLocalAgentDefinitions(agentsDir)) registry.set(local.id, local);
  return registry;
}

// =====================================================================
// 4. SCORING — weighted keyword matching (mirrors maestro_routing_keywords)
// =====================================================================

/** Lowercases and strips diacritics so "saneamento" matches "saneaménto"
 *  and PT-BR queries without accents still hit e.g. "energia"/"reequilibrio". */
export function normalizeText(text: string): string {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
}

/** How much weighted-score maps to confidence=1.0. Two strong
 *  (priority ~100) keyword hits already saturate — deliberately
 *  generous, since Manta's routing keywords are already high-precision
 *  domain terms (ANEEL, CFRD, ICOLD, ...), not generic words. */
const CONFIDENCE_SATURATION = 180;

function scoreAgent(
  agentId: string,
  normalizedQuery: string,
  keywordsByAgent: Map<string, RoutingKeyword[]>,
): AgentInvolvement {
  const keywords = keywordsByAgent.get(agentId) ?? [];
  let score = 0;
  const matched: string[] = [];
  for (const kw of keywords) {
    if (normalizedQuery.includes(normalizeText(kw.keyword))) {
      score += kw.priority;
      matched.push(kw.keyword);
    }
  }
  const confidence = Math.max(0, Math.min(1, score / CONFIDENCE_SATURATION));
  const rationale = matched.length
    ? `Match em ${matched.length} keyword(s): ${matched.join(', ')} (score=${score}).`
    : 'Nenhuma keyword de routing correspondeu.';
  return { agentId, role: 'secondary', score, confidence, matchedKeywords: matched, rationale };
}

/** Scores every composable agent in the registry against the query.
 *  Non-composable agents (the maestro router itself) are excluded —
 *  they're never a *participant* in a composition. */
export function computeAllScores(
  query: string,
  registry: Map<string, AgentDefinition>,
  routingKeywords: RoutingKeyword[] = DEFAULT_ROUTING_KEYWORDS,
): Map<string, AgentInvolvement> {
  const normalizedQuery = normalizeText(query);
  const keywordsByAgent = indexRoutingKeywords(routingKeywords);
  const scores = new Map<string, AgentInvolvement>();
  for (const [agentId, def] of registry) {
    if (!def.composable) continue;
    scores.set(agentId, scoreAgent(agentId, normalizedQuery, keywordsByAgent));
  }
  return scores;
}

// =====================================================================
// 5. KNOWN COMPOSITION PATTERNS
// =====================================================================
// Explicit, named multi-agent patterns — checked in order before the
// generic ad-hoc fallback. Each mirrors a case from
// tests/routing/prompts.md § "Casos ambíguos / desafiadores" and/or
// docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §2.2's pseudocode:
//
//   IF (barragem AND transmissão) THEN compose(barragens, energia)
//   IF (ETE AND subestação) THEN compose(saneamento, energia)
//
// `requiresHumanConfirmation: true` on the ambiguous ones is
// deliberate — tests/routing.md explicitly flags "Definir política MN"
// for the UHE case (barragens vs. energia as primary is a product
// decision, not something to silently hardcode).
// =====================================================================

function hasAny(text: string, needles: string[]): boolean {
  return needles.some((n) => text.includes(normalizeText(n)));
}

export const UHE_PATTERN: CompositionPattern = {
  id: 'uhe',
  name: 'UHE — Usina Hidrelétrica (barragem + geração)',
  description:
    'Projeto de usina hidrelétrica: a barragem (vertedouro, NA máximo maximorum, volume de reservatório) ' +
    'precisa estar definida antes do estudo de geração (queda líquida, vazão de projeto, potência instalada).',
  match(q, scores) {
    const mentionsUhe = /\buhe\b|usina hidrel[e]trica/.test(q);
    const damSignal = (scores.get('agente-barragens')?.score ?? 0) > 0 || hasAny(q, ['barragem', 'cfrd', 'vertedouro']);
    const powerSignal =
      (scores.get('agente-energia')?.score ?? 0) > 0 ||
      hasAny(q, ['geração', 'turbina', 'casa de força', 'kv', 'subestação']);
    return mentionsUhe || (damSignal && powerSignal);
  },
  agents: [
    {
      agentId: 'agente-barragens',
      role: 'primary',
      rationale: 'Define a estrutura de contenção e o reservatório — pré-requisito hidráulico da geração.',
    },
    {
      agentId: 'agente-energia',
      role: 'secondary',
      rationale: 'Dimensiona a casa de força / geração a partir dos dados de queda líquida e vazão fornecidos pela barragem.',
    },
  ],
  dependencies: [
    {
      from: 'agente-barragens',
      to: 'agente-energia',
      reason: 'Estudo de geração depende de NA máximo maximorum, volume útil e vazão de projeto do reservatório.',
    },
  ],
  schedulingHint: 'serial',
  requiresHumanConfirmation: true, // tests/routing.md: "Definir política MN" (barragens vs energia como primário)
};

export const ETE_SUBESTACAO_PATTERN: CompositionPattern = {
  id: 'ete-subestacao',
  name: 'ETE + Subestação (saneamento + energia)',
  description: 'ETE nova e subestação de energia no mesmo canteiro — escopos tecnicamente independentes.',
  match(q) {
    const hasEte = hasAny(q, ['ete', 'estação de tratamento de esgoto']);
    const hasSe = hasAny(q, ['subestação', ' se ', 'kv']);
    return hasEte && hasSe;
  },
  agents: [
    { agentId: 'agente-saneamento', role: 'primary', rationale: 'Escopo principal do pedido (ETE nova).' },
    { agentId: 'agente-energia', role: 'secondary', rationale: 'Subestação é um escopo elétrico independente, no mesmo canteiro.' },
  ],
  dependencies: [], // no data dependency between the two — independent scopes
  schedulingHint: 'parallel',
  requiresHumanConfirmation: false,
};

export const PORTO_PISTA_PATTERN: CompositionPattern = {
  id: 'porto-pista-carga',
  name: 'Porto + Pista de carga aérea (portos + aeroportos)',
  description: 'Porto com pátio auxiliar de carga aérea — escopos independentes com handoff no merge final.',
  match(q) {
    const hasPorto = hasAny(q, ['porto', 'terminal portuário', 'arrendado']);
    const hasPista = hasAny(q, ['pista', 'aeroporto', 'carga aérea', 'pista de carga']);
    return hasPorto && hasPista;
  },
  agents: [
    { agentId: 'agente-portos', role: 'primary', rationale: 'Escopo principal do pedido (porto arrendado).' },
    { agentId: 'agente-aeroportos', role: 'secondary', rationale: 'Pátio + pista para carga aérea auxiliar é um escopo aeroportuário independente.' },
  ],
  dependencies: [],
  schedulingHint: 'parallel',
  requiresHumanConfirmation: false,
};

export const ADUTORA_BARRAGEM_PATTERN: CompositionPattern = {
  id: 'adutora-barragem-rejeitos',
  name: 'Adutora atravessando barragem de rejeitos (saneamento + barragens, consulta)',
  description:
    'O traçado da adutora precisa respeitar as restrições de segurança da barragem de rejeitos ' +
    '(zona de autossalvamento, servidão de faixa de segurança) antes de ser finalizado.',
  match(q) {
    const hasAdutora = q.includes('adutora');
    const hasTailingsDam = hasAny(q, ['barragem de rejeitos', 'tsf', 'pilha de rejeito']);
    return hasAdutora && hasTailingsDam;
  },
  agents: [
    {
      agentId: 'agente-barragens',
      role: 'consult',
      rationale: 'Consulta técnica curta: restrições de segurança/servidão antes do traçado final da adutora.',
    },
    { agentId: 'agente-saneamento', role: 'primary', rationale: 'Escopo principal — traçado e dimensionamento da adutora.' },
  ],
  dependencies: [
    {
      from: 'agente-barragens',
      to: 'agente-saneamento',
      reason: 'Traçado da adutora deve respeitar a zona de autossalvamento / servidão de segurança da barragem.',
    },
  ],
  schedulingHint: 'serial',
  requiresHumanConfirmation: false,
};

export const CLAIM_ORCAMENTO_PATTERN: CompositionPattern = {
  id: 'claim-orcamento',
  name: 'Claim + Orçamento (reequilíbrio econômico-financeiro)',
  description: 'Pleito de reequilíbrio precisa do quantitativo/orçamento subjacente para sustentar o quantum.',
  match(q) {
    const hasClaim = hasAny(q, ['claim', 'reequilíbrio', 'reequilibrio']);
    const hasBudget = hasAny(q, ['orçamento', 'quantitativo', 'planilha orçamentária']);
    return hasClaim && hasBudget;
  },
  agents: [
    { agentId: 'manta-01-claims', role: 'primary', rationale: 'Estrutura o pleito e o quantum do reequilíbrio.' },
    { agentId: 'manta-05-orcamento', role: 'secondary', rationale: 'Fornece o quantitativo/orçamento que sustenta o quantum.' },
  ],
  dependencies: [],
  schedulingHint: 'parallel',
  requiresHumanConfirmation: false,
};

/** Checked in this exact order — first match wins. Order matters when
 *  a query could plausibly satisfy more than one (e.g. a query
 *  mentioning both UHE and an ETE would match UHE first). */
export const COMPOSITION_PATTERNS: CompositionPattern[] = [
  UHE_PATTERN,
  ETE_SUBESTACAO_PATTERN,
  PORTO_PISTA_PATTERN,
  ADUTORA_BARRAGEM_PATTERN,
  CLAIM_ORCAMENTO_PATTERN,
];

// =====================================================================
// 6. detectComposition
// =====================================================================

/**
 * Detects whether a query needs 2+ agents composed together.
 *
 * Resolution order:
 *   1. Named COMPOSITION_PATTERNS (+ any `options.extraPatterns`,
 *      checked first so callers can override/prepend) — deterministic,
 *      documented, reviewed rules (UHE, ETE+subestação, ...).
 *   2. Generic ad-hoc detection: if 2+ agents independently score
 *      above `matchThreshold` and no named pattern fired, treat it as
 *      an undocumented composite — flagged `requiresHumanConfirmation`
 *      since there's no reviewed dependency/scheduling policy for it
 *      yet (mirrors docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §2.2's
 *      "Fallback: se falha composição, pergunte ao usuário").
 *   3. Otherwise: a single agent (or none) — not a composition.
 */
export function detectComposition(query: string, options: DetectCompositionOptions = {}): CompositionDetectionResult {
  const {
    matchThreshold = 0.28,
    minAgentsForComposite = 2,
    registry = buildAgentRegistry(),
    routingKeywords = DEFAULT_ROUTING_KEYWORDS,
    extraPatterns = [],
  } = options;

  const normalizedQuery = normalizeText(query);
  const scores = computeAllScores(query, registry, routingKeywords);
  const allScores = [...scores.values()].sort((a, b) => b.score - a.score);

  for (const pattern of [...extraPatterns, ...COMPOSITION_PATTERNS]) {
    if (!pattern.match(normalizedQuery, scores)) continue;

    const agents: AgentInvolvement[] = pattern.agents.map(({ agentId, role, rationale }) => {
      const live = scores.get(agentId);
      return {
        agentId,
        role,
        score: live?.score ?? 0,
        confidence: live && live.confidence > 0 ? live.confidence : 0.6, // pattern itself is the signal even if keyword score is thin
        matchedKeywords: live?.matchedKeywords ?? [],
        rationale,
      };
    });

    return {
      query,
      isComposite: true,
      patternId: pattern.id,
      patternName: pattern.name,
      agents,
      dependencies: pattern.dependencies,
      schedulingHint: pattern.schedulingHint,
      confidence: Math.min(...agents.map((a) => a.confidence)),
      requiresHumanConfirmation: pattern.requiresHumanConfirmation,
      rationale: `Padrão "${pattern.name}" identificado — ${pattern.description}`,
      allScores,
    };
  }

  const matched = allScores.filter((a) => a.confidence >= matchThreshold);

  if (matched.length >= minAgentsForComposite) {
    const agents = matched.map((a, i) => ({ ...a, role: (i === 0 ? 'primary' : 'secondary') as AgentRole }));
    return {
      query,
      isComposite: true,
      agents,
      dependencies: [],
      schedulingHint: 'parallel', // safe default: no known data dependency between ad-hoc matches
      confidence: agents.reduce((sum, a) => sum + a.confidence, 0) / agents.length,
      requiresHumanConfirmation: true, // ad-hoc — no reviewed policy, per §2.2 fallback ("pergunte ao usuário")
      rationale:
        `${agents.length} agentes ultrapassaram o limiar de confiança (${matchThreshold}) sem corresponder a ` +
        `nenhum padrão nomeado (${agents.map((a) => `${a.agentId}=${a.confidence.toFixed(2)}`).join(', ')}). ` +
        'Composição ad-hoc — confirmar prioridade com o usuário antes de despachar.',
      allScores,
    };
  }

  if (matched.length === 1) {
    return {
      query,
      isComposite: false,
      agents: matched,
      dependencies: [],
      schedulingHint: 'parallel',
      confidence: matched[0].confidence,
      requiresHumanConfirmation: false,
      rationale: `Apenas 1 agente correspondeu (${matched[0].agentId}) — roteamento simples, não composição.`,
      allScores,
    };
  }

  return {
    query,
    isComposite: false,
    agents: [],
    dependencies: [],
    schedulingHint: 'parallel',
    confidence: 0,
    requiresHumanConfirmation: true,
    rationale: 'Nenhum agente correspondeu com confiança suficiente — encaminhar ao Maestro para triagem manual.',
    allScores,
  };
}

// =====================================================================
// 7. analyzeScheduling — dependency graph → serial/parallel stages
// =====================================================================

function detectCycle(nodeIds: string[], edges: DependencyEdge[]): string[] | null {
  const adjacency = new Map<string, string[]>();
  for (const id of nodeIds) adjacency.set(id, []);
  for (const e of edges) adjacency.get(e.from)?.push(e.to);

  const WHITE = 0;
  const GRAY = 1;
  const BLACK = 2;
  const color = new Map<string, number>(nodeIds.map((id) => [id, WHITE]));
  const path: string[] = [];

  function visit(id: string): string[] | null {
    color.set(id, GRAY);
    path.push(id);
    for (const next of adjacency.get(id) ?? []) {
      if (color.get(next) === GRAY) {
        const cycleStart = path.indexOf(next);
        return [...path.slice(cycleStart), next];
      }
      if (color.get(next) === WHITE) {
        const found = visit(next);
        if (found) return found;
      }
    }
    path.pop();
    color.set(id, BLACK);
    return null;
  }

  for (const id of nodeIds) {
    if (color.get(id) === WHITE) {
      const found = visit(id);
      if (found) return found;
    }
  }
  return null;
}

/** When `schedulingHint === 'serial'` but the caller supplied no
 *  explicit dependency edges (typical for the generic ad-hoc detection
 *  path in detectComposition), synthesize a deterministic chain:
 *  primary -> secondary[0] -> secondary[1] -> ... so "serial" still
 *  means something concrete rather than silently behaving like
 *  "parallel". */
function synthesizeSerialChain(agents: AgentInvolvement[]): DependencyEdge[] {
  const ordered = [...agents].sort((a, b) => {
    const rank = (r: AgentRole) => (r === 'primary' ? 0 : r === 'consult' ? 1 : 2);
    return rank(a.role) - rank(b.role);
  });
  const edges: DependencyEdge[] = [];
  for (let i = 0; i < ordered.length - 1; i += 1) {
    edges.push({
      from: ordered[i].agentId,
      to: ordered[i + 1].agentId,
      reason: 'Cadeia serial sintetizada (schedulingHint="serial" sem dependências explícitas).',
    });
  }
  return edges;
}

function resolveFallbackPolicy(
  agentId: string,
  tier: ModelTier,
  options: AnalyzeSchedulingOptions,
): FallbackPolicy {
  const base: FallbackPolicy = {
    maxRetries: 1,
    backoffMs: 1500,
    escalateTierOnFinalFailure: true,
    timeoutMs: options.timeoutOverridesMs?.[agentId] ?? DEFAULT_TIMEOUTS_MS[tier],
  };
  return { ...base, ...(options.fallbackOverrides?.[agentId] ?? {}) };
}

/**
 * Builds a serial-vs-parallel execution plan from a composition (or a
 * hand-built `{ agents, dependencies, schedulingHint }`). Uses Kahn's
 * algorithm to turn the dependency graph into topological levels
 * ("stages") — every stage runs its agents in parallel; stages run one
 * after another. This is the general mechanism that naturally
 * produces:
 *
 *   - 'parallel' strategy  → one stage, no edges (ETE+subestação, Porto+pista)
 *   - 'serial' strategy    → one agent per stage (UHE: barragens -> energia)
 *   - 'hybrid' strategy    → mixed (e.g. [A, B] parallel, then C depends on both)
 *
 * Throws CompositionCycleError if the dependency graph isn't a DAG.
 */
export function analyzeScheduling(
  input: CompositionPlanInput,
  options: AnalyzeSchedulingOptions = {},
): SchedulingPlan {
  const { registry = buildAgentRegistry() } = options;
  if (input.agents.length === 0) {
    throw new Error('analyzeScheduling: nenhum agente para agendar.');
  }

  const nodeIds = input.agents.map((a) => a.agentId);
  let edges = input.dependencies ? [...input.dependencies] : [];

  if (edges.length === 0 && input.schedulingHint === 'serial' && input.agents.length > 1) {
    edges = synthesizeSerialChain(input.agents);
  }

  // Guard against edges referencing agents outside this composition —
  // easy to introduce by hand-building a CompositionPlanInput.
  const nodeSet = new Set(nodeIds);
  for (const e of edges) {
    if (!nodeSet.has(e.from) || !nodeSet.has(e.to)) {
      throw new Error(
        `analyzeScheduling: aresta de dependência referencia agente fora da composição (${e.from} -> ${e.to}).`,
      );
    }
  }

  const cycle = detectCycle(nodeIds, edges);
  if (cycle) throw new CompositionCycleError(cycle);

  // Kahn's algorithm: repeatedly peel off nodes with indegree 0.
  const indegree = new Map<string, number>(nodeIds.map((id) => [id, 0]));
  const successors = new Map<string, string[]>(nodeIds.map((id) => [id, []]));
  for (const e of edges) {
    indegree.set(e.to, (indegree.get(e.to) ?? 0) + 1);
    successors.get(e.from)?.push(e.to);
  }

  const byId = new Map(input.agents.map((a) => [a.agentId, a]));
  const remaining = new Set(nodeIds);
  const stages: SchedulingStage[] = [];

  let stageIndex = 0;
  while (remaining.size > 0) {
    const ready = [...remaining].filter((id) => (indegree.get(id) ?? 0) === 0);
    // detectCycle already ran, so `ready` can only be empty here due to
    // a logic error — guard anyway rather than looping forever.
    if (ready.length === 0) throw new CompositionCycleError([...remaining]);

    const scheduledAgents: ScheduledAgent[] = ready.map((id) => {
      const involvement = byId.get(id)!;
      const def = registry.get(id);
      const model = def?.model ?? 'sonnet';
      const dependsOn = edges.filter((e) => e.to === id).map((e) => e.from);
      return {
        ...involvement,
        model,
        fallbackPolicy: resolveFallbackPolicy(id, model, options),
        dependsOn,
      };
    });

    stages.push({
      index: stageIndex,
      agents: scheduledAgents,
      estimatedMs: Math.max(...scheduledAgents.map((a) => a.fallbackPolicy.timeoutMs)),
    });

    for (const id of ready) {
      remaining.delete(id);
      for (const next of successors.get(id) ?? []) {
        indegree.set(next, (indegree.get(next) ?? 0) - 1);
      }
    }
    stageIndex += 1;
  }

  const totalEstimatedMs = stages.reduce((sum, s) => sum + s.estimatedMs, 0);
  const strategy: SchedulingPlan['strategy'] =
    edges.length === 0 ? 'parallel' : stages.every((s) => s.agents.length === 1) ? 'serial' : 'hybrid';

  return {
    stages,
    graph: { nodes: nodeIds, edges },
    strategy,
    totalEstimatedMs,
    source: input,
  };
}

/** Renders a SchedulingPlan as readable ASCII — handy for logs and for
 *  eyeballing that a composition scheduled the way you expected
 *  (complements the mermaid diagrams in the file header). */
export function describeSchedulingPlan(plan: SchedulingPlan): string {
  const lines = [`Estratégia: ${plan.strategy} (total estimado: ${plan.totalEstimatedMs}ms)`];
  plan.stages.forEach((stage) => {
    const agentDescriptions = stage.agents
      .map((a) => `${a.agentId}[${a.role}, ${a.model}, timeout=${a.fallbackPolicy.timeoutMs}ms]`)
      .join(' | ');
    const deps = stage.agents
      .filter((a) => a.dependsOn.length > 0)
      .map((a) => `${a.agentId} <- ${a.dependsOn.join(',')}`);
    lines.push(`  Stage ${stage.index}: ${agentDescriptions}`);
    if (deps.length) lines.push(`    depende de: ${deps.join('; ')}`);
  });
  return lines.join('\n');
}

// =====================================================================
// 8. ORCHESTRATION PRIMITIVES — timeout, retry/escalation, circuit breaker
// =====================================================================

/** Classic 3-state circuit breaker (CLOSED -> OPEN -> HALF_OPEN ->
 *  CLOSED). Shared across an entire orchestrateComposition run so a
 *  cascade of agent failures aborts remaining stages instead of
 *  burning the full plan's timeout budget on calls likely to fail. */
export class CircuitBreaker {
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  private consecutiveFailures = 0;
  private openedAt = 0;
  private readonly failureThreshold: number;
  private readonly resetTimeoutMs: number;

  constructor(options: CircuitBreakerOptions = {}) {
    this.failureThreshold = options.failureThreshold ?? 3;
    this.resetTimeoutMs = options.resetTimeoutMs ?? 30_000;
  }

  /** Whether a new call should be allowed right now. Also flips
   *  OPEN -> HALF_OPEN once resetTimeoutMs has elapsed, allowing a
   *  single probe call through. */
  canProceed(): boolean {
    if (this.state === 'closed') return true;
    if (this.state === 'open' && Date.now() - this.openedAt >= this.resetTimeoutMs) {
      this.state = 'half-open';
      return true;
    }
    return this.state === 'half-open';
  }

  isOpen(): boolean {
    return this.state === 'open' && Date.now() - this.openedAt < this.resetTimeoutMs;
  }

  recordSuccess(): void {
    this.consecutiveFailures = 0;
    this.state = 'closed';
  }

  recordFailure(): void {
    this.consecutiveFailures += 1;
    if (this.state === 'half-open' || this.consecutiveFailures >= this.failureThreshold) {
      this.state = 'open';
      this.openedAt = Date.now();
    }
  }

  getState(): 'closed' | 'open' | 'half-open' {
    return this.state;
  }
}

/** Runs `fn` under an AbortController-based timeout. Rejects with a
 *  descriptive error (not a bare AbortError) so callers can log
 *  something actionable. */
async function withTimeout<T>(
  fn: (signal: AbortSignal) => Promise<T>,
  timeoutMs: number,
  label: string,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await Promise.race([
      fn(controller.signal),
      new Promise<T>((_, reject) => {
        controller.signal.addEventListener('abort', () =>
          reject(new Error(`Timeout de ${timeoutMs}ms excedido em "${label}".`)),
        );
      }),
    ]);
  } finally {
    clearTimeout(timer);
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Dispatches a single agent with retries, timeout, and tier escalation
 * on final failure — the "fallback handling" half of the composition
 * system. Never throws: every outcome (including exhausting retries)
 * is reported back as an `AgentInvocationResult` so
 * `orchestrateComposition` can decide what to do next (abort vs.
 * degrade) rather than unwinding the stack.
 */
async function invokeWithFallback(
  node: ScheduledAgent,
  agentDefinition: AgentDefinition | undefined,
  invoker: AgentInvoker,
  task: OrchestrationTask,
  upstreamContext: Record<string, AgentInvocationResult>,
  breaker: CircuitBreaker,
  isRoutable?: (agentId: string) => boolean,
): Promise<AgentInvocationResult> {
  const start = Date.now();

  if (isRoutable && !isRoutable(node.agentId)) {
    return {
      agentId: node.agentId,
      status: 'skipped',
      error: 'Agente reportado como não-roteável pelo health registry (heartbeat-service).',
      attempts: 0,
      tookMs: 0,
      modelUsed: MODEL_TIER_TO_ID[node.model],
      escalated: false,
    };
  }

  if (!agentDefinition) {
    return {
      agentId: node.agentId,
      status: 'error',
      error: `Nenhuma AgentDefinition encontrada no registry para "${node.agentId}".`,
      attempts: 0,
      tookMs: Date.now() - start,
      modelUsed: MODEL_TIER_TO_ID[node.model],
      escalated: false,
    };
  }

  const { maxRetries, backoffMs, escalateTierOnFinalFailure, timeoutMs } = node.fallbackPolicy;
  let attempts = 0;
  let lastError = '';
  let currentTier: ModelTier | undefined;

  const totalAttempts = maxRetries + 1 + (escalateTierOnFinalFailure ? 1 : 0);

  while (attempts < totalAttempts) {
    attempts += 1;
    const isEscalationAttempt = escalateTierOnFinalFailure && attempts === totalAttempts;
    if (isEscalationAttempt) {
      currentTier = escalateTier(node.model) ?? node.model;
    }

    if (!breaker.canProceed()) {
      lastError = 'Circuit breaker aberto — chamada abortada antes do despacho.';
      break;
    }

    try {
      const response = await withTimeout(
        (signal) =>
          invoker.invoke({
            agentId: node.agentId,
            agentDefinition,
            task,
            role: node.role,
            upstreamContext,
            modelOverride: currentTier,
            signal,
          }),
        timeoutMs,
        node.agentId,
      );
      breaker.recordSuccess();
      return {
        agentId: node.agentId,
        status: 'success',
        output: response.output,
        structuredOutput: response.structuredOutput,
        attempts,
        tookMs: Date.now() - start,
        modelUsed: response.modelUsed,
        escalated: Boolean(currentTier),
      };
    } catch (err) {
      lastError = err instanceof Error ? err.message : String(err);
      breaker.recordFailure();
      const isTimeout = lastError.includes('Timeout de');
      const hasMoreAttempts = attempts < totalAttempts;
      if (hasMoreAttempts) {
        await sleep(backoffMs * attempts); // linear backoff
      } else {
        return {
          agentId: node.agentId,
          status: isTimeout ? 'timeout' : 'error',
          error: lastError,
          attempts,
          tookMs: Date.now() - start,
          modelUsed: MODEL_TIER_TO_ID[currentTier ?? node.model],
          escalated: Boolean(currentTier),
        };
      }
    }
  }

  return {
    agentId: node.agentId,
    status: 'error',
    error: lastError || 'Falha desconhecida antes do primeiro despacho (circuit breaker aberto).',
    attempts,
    tookMs: Date.now() - start,
    modelUsed: MODEL_TIER_TO_ID[currentTier ?? node.model],
    escalated: Boolean(currentTier),
  };
}

/** Merges every upstream agent's result (per the dependency graph)
 *  into the context passed to the next stage. */
function buildUpstreamContext(
  stage: SchedulingStage,
  resultsSoFar: Record<string, AgentInvocationResult>,
): Record<string, AgentInvocationResult> {
  const context: Record<string, AgentInvocationResult> = {};
  for (const agent of stage.agents) {
    for (const depId of agent.dependsOn) {
      if (resultsSoFar[depId]) context[depId] = resultsSoFar[depId];
    }
  }
  return context;
}

/** Default merge: a readable, labeled concatenation grouped by stage
 *  and role. Callers with a real synthesis need (e.g. dispatching to
 *  `manta-15-arq`/arquiteto-ia to combine sections into one narrative)
 *  should pass `options.merge` to `orchestrateComposition` instead. */
export function defaultMerge(results: Record<string, AgentInvocationResult>, plan: SchedulingPlan): string {
  const sections: string[] = [];
  for (const stage of plan.stages) {
    for (const agent of stage.agents) {
      const result = results[agent.agentId];
      if (!result) continue;
      const header = `## [${agent.role}] ${agent.agentId} (stage ${stage.index}, ${result.status})`;
      const body =
        result.status === 'success'
          ? result.output ?? '(sem saída)'
          : `_(indisponível: ${result.error ?? result.status})_`;
      sections.push(`${header}\n${body}`);
    }
  }
  return sections.join('\n\n');
}

// =====================================================================
// 9. orchestrateComposition — dispatch stage-by-stage & merge
// =====================================================================

/**
 * Executes a SchedulingPlan: runs each stage's agents in parallel,
 * feeds each stage's results forward as `upstreamContext` to whatever
 * depends on them, and merges everything into a final result.
 *
 * Failure handling:
 *   - Each agent gets its own retry/escalation/timeout policy (see
 *     `invokeWithFallback`).
 *   - A shared CircuitBreaker aborts remaining stages once repeated
 *     failures cross `failureThreshold` — no point burning the full
 *     plan timeout on a run that's already degrading.
 *   - If a `primary` agent fails irrecoverably, remaining stages are
 *     aborted by default (`status: 'partial'`) unless
 *     `options.continueOnPrimaryFailure` is set.
 */
export async function orchestrateComposition(
  plan: SchedulingPlan,
  invoker: AgentInvoker,
  task: OrchestrationTask,
  options: OrchestrateOptions = {},
): Promise<OrchestrationResult> {
  const { continueOnPrimaryFailure = false, isRoutable, merge = defaultMerge } = options;
  const registry = buildAgentRegistry();
  const breaker = new CircuitBreaker(options.circuitBreaker);

  const agentResults: Record<string, AgentInvocationResult> = {};
  const errors: string[] = [];
  let status: OrchestrationStatus = 'success';
  let stagesExecuted = 0;
  const startedAt = Date.now();

  for (const stage of plan.stages) {
    if (breaker.isOpen()) {
      status = 'aborted';
      errors.push(`Circuit breaker aberto antes do stage ${stage.index} — estágios restantes abortados.`);
      break;
    }

    const upstreamContext = buildUpstreamContext(stage, agentResults);

    const settled = await Promise.allSettled(
      stage.agents.map((node) =>
        invokeWithFallback(node, registry.get(node.agentId), invoker, task, upstreamContext, breaker, isRoutable),
      ),
    );

    settled.forEach((outcome, i) => {
      const node = stage.agents[i];
      const result: AgentInvocationResult =
        outcome.status === 'fulfilled'
          ? outcome.value
          : {
              agentId: node.agentId,
              status: 'error',
              error: outcome.reason instanceof Error ? outcome.reason.message : String(outcome.reason),
              attempts: 0,
              tookMs: 0,
              modelUsed: MODEL_TIER_TO_ID[node.model],
              escalated: false,
            };
      agentResults[node.agentId] = result;
      if (result.status !== 'success') {
        errors.push(`${node.agentId}: ${result.error ?? result.status}`);
      }
    });

    stagesExecuted += 1;

    const primaryFailed = stage.agents.some(
      (n) => n.role === 'primary' && agentResults[n.agentId]?.status !== 'success',
    );
    const anyFailed = stage.agents.some((n) => agentResults[n.agentId]?.status !== 'success');

    if (anyFailed && status === 'success') status = 'partial';

    if (primaryFailed && !continueOnPrimaryFailure) {
      errors.push(`Agente primário falhou no stage ${stage.index} — estágios dependentes abortados.`);
      status = 'partial';
      break;
    }
  }

  return {
    status,
    plan,
    agentResults,
    stagesExecuted,
    mergedOutput: merge(agentResults, plan),
    errors,
    totalMs: Date.now() - startedAt,
  };
}

// =====================================================================
// 10. AGENT INVOKERS — pluggable dispatch backends
// =====================================================================

/**
 * Reference AgentInvoker that dispatches each agent as a direct Claude
 * API call via `@anthropic-ai/sdk` (`npm install @anthropic-ai/sdk`),
 * using the agent's `.claude/agents/<id>.md` body as its system
 * prompt and its `model` frontmatter tier mapped through
 * MODEL_TIER_TO_ID. This is one valid way to run Manta agents
 * end-to-end from Node/TypeScript; a Claude Code deployment would
 * instead dispatch via the Task tool's subagent mechanism (in which
 * case implement `AgentInvoker` against that instead — the rest of
 * this module is unaffected either way).
 *
 * Per the claude-api skill defaults: adaptive thinking for
 * sonnet/opus (haiku 4.5 doesn't support it), `effort: "medium"` as a
 * balanced default for worker agents, non-streaming since these are
 * bounded technical answers, not long-form generation.
 */
export class AnthropicAgentInvoker implements AgentInvoker {
  private client: unknown;

  constructor(options: { apiKey?: string; effort?: 'low' | 'medium' | 'high' | 'xhigh' | 'max' } = {}) {
    // Lazy/dynamic require so this module has zero hard dependency on
    // `@anthropic-ai/sdk` for callers who only need detectComposition /
    // analyzeScheduling (pure logic, no network).
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const Anthropic = require('@anthropic-ai/sdk');
    this.client = new Anthropic(options.apiKey ? { apiKey: options.apiKey } : {});
    this.effort = options.effort ?? 'medium';
  }

  private effort: 'low' | 'medium' | 'high' | 'xhigh' | 'max';

  async invoke(request: AgentInvokerRequest): Promise<AgentInvokerResponse> {
    const tier = request.modelOverride ?? request.agentDefinition.model;
    const model = MODEL_TIER_TO_ID[tier];
    const systemPrompt =
      request.agentDefinition.body ??
      `Você é o ${request.agentDefinition.name} (${request.agentDefinition.mantaCode}). ${request.agentDefinition.description}`;

    const upstreamSummary = Object.entries(request.upstreamContext)
      .map(([id, res]) => `### Resultado de ${id}\n${res.output ?? '(sem saída)'}`)
      .join('\n\n');

    const userContent = upstreamSummary
      ? `${request.task.query}\n\n---\nContexto de agentes anteriores nesta composição:\n\n${upstreamSummary}`
      : request.task.query;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const client = this.client as any;
    const requestParams: Record<string, unknown> = {
      model,
      max_tokens: 16000,
      system: systemPrompt,
      messages: [{ role: 'user', content: userContent }],
    };
    if (tier !== 'haiku') {
      requestParams.thinking = { type: 'adaptive' };
      requestParams.output_config = { effort: this.effort };
    }

    const response = await client.messages.create(requestParams, { signal: request.signal });
    const textBlock = (response.content ?? []).find((b: { type: string }) => b.type === 'text');

    return {
      output: textBlock?.text ?? '',
      modelUsed: model,
      structuredOutput: response,
    };
  }
}

/**
 * Deterministic-ish mock invoker for tests, demos, and CI (no network,
 * no API key required) — mirrors the role `defaultAgentInvoker` /
 * injected `agentInvoker` play elsewhere in this repo (see
 * auto-registration-service.js). Simulates latency and an occasional
 * failure so fallback/timeout/circuit-breaker paths are exercisable.
 */
export class MockAgentInvoker implements AgentInvoker {
  constructor(
    private options: { latencyMs?: number; failureRate?: number; failFor?: Set<string> } = {},
  ) {}

  async invoke(request: AgentInvokerRequest): Promise<AgentInvokerResponse> {
    const latency = this.options.latencyMs ?? 200;
    await sleep(latency);

    if (request.signal.aborted) throw new Error('Chamada abortada (timeout).');

    const shouldFail =
      this.options.failFor?.has(request.agentId) ||
      (this.options.failureRate !== undefined && Math.random() < this.options.failureRate);
    if (shouldFail) {
      throw new Error(`[mock] falha simulada em ${request.agentId}`);
    }

    const model = MODEL_TIER_TO_ID[request.modelOverride ?? request.agentDefinition.model];
    return {
      output:
        `[MOCK ${request.agentId} / ${model} / role=${request.role}] Resposta simulada para: "${request.task.query}". ` +
        `Contexto upstream recebido: [${Object.keys(request.upstreamContext).join(', ') || 'nenhum'}].`,
      modelUsed: model,
    };
  }
}

// =====================================================================
// 11. DEMO — the 3 canonical examples (UHE, ETE+Subestação, Porto+pista)
// =====================================================================
// Not auto-executed. Run manually, e.g. with `tsx` or `ts-node`:
//
//   import { runCompositionDemo } from './composition-orchestrator';
//   runCompositionDemo();
//
// or add a small CLI wrapper. Uses MockAgentInvoker so it runs with no
// API key and no network access.
// =====================================================================

const DEMO_QUERIES = [
  'Preciso projetar uma UHE com barragem CFRD de 100m e LT de 500kV até a SE.',
  'A concessionária pediu uma ETE nova + subestação de 138kV no mesmo canteiro.',
  'Porto arrendado no Amazonas com pátio + pista para carga aérea auxiliar.',
];

export async function runCompositionDemo(): Promise<void> {
  const invoker = new MockAgentInvoker({ latencyMs: 50 });

  for (const query of DEMO_QUERIES) {
    console.log('='.repeat(78));
    console.log(`QUERY: ${query}`);

    const detection = detectComposition(query);
    console.log(`--> Padrão: ${detection.patternName ?? '(ad-hoc)'} | isComposite=${detection.isComposite}`);
    console.log(`--> Agentes: ${detection.agents.map((a) => `${a.agentId}(${a.role})`).join(', ')}`);

    if (!detection.isComposite) {
      console.log('--> Não é composição — roteamento simples ao Maestro.');
      continue;
    }

    const plan = analyzeScheduling(detection);
    console.log(describeSchedulingPlan(plan));

    const result = await orchestrateComposition(plan, invoker, { query });
    console.log(`--> Status final: ${result.status} (${result.totalMs}ms, ${result.stagesExecuted} estágio(s))`);
    console.log(result.mergedOutput);
  }
}
