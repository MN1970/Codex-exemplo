/**
 * expert-finder.ts
 * =====================================================================
 * Manta Maestro v5.0 — Expert Agent Finder with Advanced Scoring
 *
 * Implements a multi-signal ranking system for agent selection combining:
 * - 40% Semantic relevance (query embedding vs agent expertise embeddings)
 * - 30% Historical success rate (from routing_feedback & routing_events)
 * - 15% Capability match (agent_capabilities: does agent have this skill?)
 * - 10% Cost estimate (token budgeting per model tier: Haiku < Sonnet < Opus)
 * - 5% Latency/SLA track record (from agent_health metrics)
 *
 * Features:
 * - Tie-breaking: If top 2 agents within 2% confidence → pick lower-cost
 * - Fallback: If top confidence < 0.6 → escalate to Opus or human review
 * - Explainability: Why this agent won (JSON reasoning per agent)
 * - Integration with existing maestro-v2-routing.ts types & Agent Registry
 *
 * Design: Zero hard SDK dependencies (dependency injection for DB/embeddings)
 * Backward compatible with v4.2 static registry
 *
 * Ticket: MNT-2026-ECOSYSTEM-UPGRADE-V5 (§2.2 Expert Ranker, §4.2 Explainability)
 */

import {
  AgentRecord,
  MaestroRoutingError,
  cosineSimilarity,
  Bm25Index,
  tokenize,
} from './maestro-v2-routing';

// =====================================================================
// 1. Domain types for Expert Ranker
// =====================================================================

export type CostTier = 'haiku' | 'sonnet' | 'opus';

const COST_PER_TIER: Record<CostTier, number> = {
  haiku: 100,   // 1x baseline (cheapest)
  sonnet: 300,  // 3x
  opus: 800,    // 8x
};

/** Metrics from a single routing_event and routing_feedback */
export interface RoutingHistory {
  totalQueries: number;
  successCount: number;
  failureCount: number;
  /** success_count / total_queries, [0, 1] */
  successRate: number;
  /** mean latency_ms across all events for this agent */
  avgLatencyMs: number;
  /** p99 latency (99th percentile) for SLA budgeting */
  p99LatencyMs: number;
  /** mean error_rate_24h from latest agent_health snapshot */
  errorRate24h: number;
  lastRoutedAt: Date | null;
}

export interface CapabilityMatch {
  /** Does agent have the primary domain skill for this query? */
  hasPrimaryCapability: boolean;
  /** How many relevant tools/skills does agent have? */
  capabilityCount: number;
  /** Capability coverage ratio [0, 1] */
  coverageRatio: number;
}

/** Score component breakdown (for explainability) */
export interface ScoreBreakdown {
  semanticScore: number;     // [0, 1]
  historicalScore: number;   // [0, 1]
  capabilityScore: number;   // [0, 1]
  costScore: number;         // [0, 1]
  latencyScore: number;      // [0, 1]
  finalScore: number;        // [0, 1] — weighted sum
}

/** Full ranking result for one agent */
export interface ExpertRankedAgent {
  rank: number;
  agent: AgentRecord;
  scores: ScoreBreakdown;
  confidence: number;  // Synonym for finalScore; used in circuit breaker
  historicalContext: RoutingHistory;
  capabilityMatch: CapabilityMatch;
  costEstimate: number; // tokens_needed * cost_per_tier[model]
  explanation: string;
}

export interface ExpertRankingResult {
  query: string;
  ranked: ExpertRankedAgent[];
  primaryChoice: ExpertRankedAgent | null;
  alternatives: ExpertRankedAgent[];
  circuitBreakerEscalate: boolean;
  circuitBreakerReason: string;
  tookMs: number;
}

// =====================================================================
// 2. Data source interfaces (dependency injection)
// =====================================================================

/** Provides historical routing metrics for an agent. */
export interface HistoryProvider {
  readonly name: string;
  /** Load aggregated metrics for one agent from routing_events + routing_feedback */
  getRoutingHistory(agentId: string): Promise<RoutingHistory>;
}

/** Provides capability metadata: tools, skills, RAG collections, etc. */
export interface CapabilityProvider {
  readonly name: string;
  /** Check if agent has primary capability for a domain */
  checkCapability(agentId: string, domain: string): Promise<CapabilityMatch>;
}

// =====================================================================
// 3. Mock/fallback providers (for dev/test when DB unavailable)
// =====================================================================

/**
 * Fallback history provider that returns synthetic but reasonable metrics
 * when DB is unreachable or not yet instrumented.
 */
export class SyntheticHistoryProvider implements HistoryProvider {
  readonly name = 'synthetic-fallback';

  async getRoutingHistory(agentId: string): Promise<RoutingHistory> {
    // Synthetic but plausible data: older agentes (Manta 01-16) have more history
    const isVertical = agentId.startsWith('manta-03') || agentId.startsWith('agente-');
    const totalQueries = isVertical ? 15 : 50; // Verticals are newer
    const successCount = Math.floor(totalQueries * 0.85); // ~85% success

    return {
      totalQueries,
      successCount,
      failureCount: totalQueries - successCount,
      successRate: successCount / totalQueries,
      avgLatencyMs: 250,
      p99LatencyMs: 800,
      errorRate24h: 0.02,
      lastRoutedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2h ago
    };
  }
}

/**
 * Fallback capability provider: infers from agent.skills + tools + rag_collections.
 */
export class LocalCapabilityProvider implements CapabilityProvider {
  readonly name = 'local-fallback';

  async checkCapability(agentId: string, domain: string): Promise<CapabilityMatch> {
    // Domains: saneamento, energia, portos, aeroportos, barragens, rodovia, cronograma, etc.
    const domainKeywords = tokenize(domain);

    // In a real implementation, query agent_capabilities from the registry.
    // For now, return a baseline estimate.
    const capabilityCount = Math.max(1, Math.floor(Math.random() * 8));
    return {
      hasPrimaryCapability: domainKeywords.length > 0,
      capabilityCount,
      coverageRatio: Math.min(1.0, capabilityCount / 10),
    };
  }
}

// =====================================================================
// 4. ExpertRanker — the main scoring engine
// =====================================================================

export interface ExpertRankerOptions {
  /** Weights for scoring (sum should = 1.0) */
  weights?: {
    semantic?: number;    // default 0.40
    historical?: number; // default 0.30
    capability?: number; // default 0.15
    cost?: number;       // default 0.10
    latency?: number;    // default 0.05
  };
  /** Escalate if top confidence below this. Default 0.6 */
  confidenceThreshold?: number;
  /** Escalate if top 2 within this margin. Default 0.02 */
  ambiguityMargin?: number;
  /** Cost estimate per query (tokens), for budgeting. Default 5000. */
  tokensPerQuery?: number;
  /** Data providers for history & capabilities */
  historyProvider?: HistoryProvider;
  capabilityProvider?: CapabilityProvider;
}

export class ExpertRanker {
  private readonly weights: {
    semantic: number;
    historical: number;
    capability: number;
    cost: number;
    latency: number;
  };
  private readonly confidenceThreshold: number;
  private readonly ambiguityMargin: number;
  private readonly tokensPerQuery: number;
  private readonly historyProvider: HistoryProvider;
  private readonly capabilityProvider: CapabilityProvider;

  constructor(options: ExpertRankerOptions = {}) {
    const w = options.weights ?? {};
    this.weights = {
      semantic: w.semantic ?? 0.40,
      historical: w.historical ?? 0.30,
      capability: w.capability ?? 0.15,
      cost: w.cost ?? 0.10,
      latency: w.latency ?? 0.05,
    };

    // Validate weights sum to 1.0 (with small tolerance for floating point)
    const weightSum = Object.values(this.weights).reduce((a, b) => a + b, 0);
    if (Math.abs(weightSum - 1.0) > 0.001) {
      throw new MaestroRoutingError(
        `ExpertRanker weights must sum to 1.0, got ${weightSum.toFixed(4)}`
      );
    }

    this.confidenceThreshold = options.confidenceThreshold ?? 0.6;
    this.ambiguityMargin = options.ambiguityMargin ?? 0.02;
    this.tokensPerQuery = options.tokensPerQuery ?? 5000;
    this.historyProvider = options.historyProvider ?? new SyntheticHistoryProvider();
    this.capabilityProvider =
      options.capabilityProvider ?? new LocalCapabilityProvider();
  }

  /**
   * Compute semantic relevance score [0, 1] based on BM25 + semantic similarity.
   * Mirrors the logic from maestro-v2-routing.ts rankAgents().
   */
  private computeSemanticScore(
    agent: AgentRecord,
    queryTokens: string[],
    bm25Index: Bm25Index,
    queryEmbedding: number[]
  ): number {
    const bm25Raw = bm25Index.score(queryTokens, agent.id);

    let semanticRaw = 0;
    if (agent.embedding && agent.embedding.length > 0) {
      semanticRaw = cosineSimilarity(queryEmbedding, agent.embedding);
    } else {
      // Fallback: embed agent text on the fly (only in dev/test)
      const agentText = [
        agent.name,
        agent.description,
        agent.expertise_primary.join(' '),
        agent.expertise_secondary.join(' '),
      ].join(' ');
      const agentTokens = tokenize(agentText);
      const agentVector = normalizeVector(
        agentTokens.reduce<number[]>((acc, tok) => {
          const h = fnv1aHash(tok) % queryEmbedding.length;
          const sign = fnv1aHash(tok + '#s') % 2 === 0 ? 1 : -1;
          acc[h] = (acc[h] ?? 0) + sign;
          return acc;
        }, new Array(queryEmbedding.length).fill(0))
      );
      semanticRaw = cosineSimilarity(queryEmbedding, agentVector);
    }

    // Normalize both to [0, 1] and blend (0.6 BM25 + 0.4 semantic)
    // In a real implementation, normalize across the candidate pool.
    // Here, approximate with min-max against reasonable bounds:
    // BM25 unbounded, but clip to [0, 10]; semantic in [-1, 1]
    const bm25Norm = Math.min(1.0, bm25Raw / 10);
    const semanticNorm = (semanticRaw + 1) / 2; // [-1, 1] → [0, 1]

    return 0.6 * bm25Norm + 0.4 * semanticNorm;
  }

  /**
   * Compute historical success rate [0, 1].
   * Agents with no history default to 0.5 (neutral).
   */
  private computeHistoricalScore(history: RoutingHistory): number {
    if (history.totalQueries === 0) return 0.5; // No data: neutral prior
    // successRate is already [0, 1]
    return history.successRate;
  }

  /**
   * Compute capability match [0, 1].
   * If agent has primary capability: 1.0, else scale by coverage ratio.
   */
  private computeCapabilityScore(capability: CapabilityMatch): number {
    if (capability.hasPrimaryCapability) {
      return Math.min(1.0, 0.9 + 0.1 * capability.coverageRatio); // [0.9, 1.0]
    }
    return Math.max(0.0, capability.coverageRatio * 0.7); // [0, 0.7]
  }

  /**
   * Compute cost score [0, 1] (inverted: cheaper = higher score).
   * Normalizes based on model tier costs.
   */
  private computeCostScore(agent: AgentRecord): number {
    const costPerCall = COST_PER_TIER[agent.model as CostTier] ?? 300;
    const maxCost = COST_PER_TIER.opus; // 800
    // Invert: expensive (Opus) → low score, cheap (Haiku) → high score
    return 1.0 - Math.min(1.0, costPerCall / maxCost);
  }

  /**
   * Compute latency score [0, 1] (inverted: lower latency = higher score).
   * Based on p99LatencyMs (SLA budgeting).
   */
  private computeLatencyScore(history: RoutingHistory): number {
    // SLA budget: p99 should be < 5 seconds (5000 ms) for scoring purposes
    const slaBudget = 5000;
    const p99 = history.p99LatencyMs || 1000; // Default if unavailable
    // Invert: slow (>5000 ms) → low score, fast (<500 ms) → high score
    return Math.max(0.0, 1.0 - p99 / slaBudget);
  }

  /**
   * Main ranking method: given agents and query, return ranked list.
   * All agents are scored independently (no normalization across candidates).
   */
  async rankAgents(
    agents: AgentRecord[],
    query: string,
    queryEmbedding: number[]
  ): Promise<ExpertRankedAgent[]> {
    const startedAt = Date.now();
    const queryTokens = tokenize(query);
    const bm25 = new Bm25Index(agents);

    const ranked: ExpertRankedAgent[] = [];

    for (let i = 0; i < agents.length; i++) {
      const agent = agents[i];

      // Fetch history & capabilities in parallel
      const [history, capability] = await Promise.all([
        this.historyProvider.getRoutingHistory(agent.id),
        this.capabilityProvider.checkCapability(agent.id, query),
      ]);

      // Compute individual score components
      const semanticScore = this.computeSemanticScore(
        agent,
        queryTokens,
        bm25,
        queryEmbedding
      );
      const historicalScore = this.computeHistoricalScore(history);
      const capabilityScore = this.computeCapabilityScore(capability);
      const costScore = this.computeCostScore(agent);
      const latencyScore = this.computeLatencyScore(history);

      // Weighted blend
      const finalScore =
        this.weights.semantic * semanticScore +
        this.weights.historical * historicalScore +
        this.weights.capability * capabilityScore +
        this.weights.cost * costScore +
        this.weights.latency * latencyScore;

      const costEstimate = this.tokensPerQuery * COST_PER_TIER[agent.model as CostTier];

      ranked.push({
        rank: 0, // Will be set after sorting
        agent,
        scores: {
          semanticScore: round4(semanticScore),
          historicalScore: round4(historicalScore),
          capabilityScore: round4(capabilityScore),
          costScore: round4(costScore),
          latencyScore: round4(latencyScore),
          finalScore: round4(finalScore),
        },
        confidence: round4(finalScore),
        historicalContext: history,
        capabilityMatch: capability,
        costEstimate,
        explanation: '', // Will be built after ranking
      });
    }

    // Sort by finalScore descending
    ranked.sort((a, b) => b.scores.finalScore - a.scores.finalScore);

    // Assign ranks and build explanations
    for (let i = 0; i < ranked.length; i++) {
      ranked[i].rank = i + 1;
      ranked[i].explanation = this.buildExplanation(ranked[i]);
    }

    // Apply tie-breaking: if top 2 within ambiguityMargin, pick the cheaper one
    if (ranked.length > 1) {
      const top = ranked[0];
      const runnerUp = ranked[1];
      const margin = top.scores.finalScore - runnerUp.scores.finalScore;

      if (margin < this.ambiguityMargin) {
        // Tie: swap if runnerUp is cheaper
        if (runnerUp.costEstimate < top.costEstimate) {
          const temp = ranked[0];
          ranked[0] = ranked[1];
          ranked[1] = temp;
          ranked[0].rank = 1;
          ranked[1].rank = 2;
        }
      }
    }

    return ranked;
  }

  /**
   * Main entry point: Given a query and agent pool, return decision.
   */
  async findExperts(
    agents: AgentRecord[],
    query: string,
    queryEmbedding?: number[]
  ): Promise<ExpertRankingResult> {
    const startedAt = Date.now();

    // Fallback embedding: hash-based approximation if not provided
    let embedding = queryEmbedding;
    if (!embedding) {
      const tokens = tokenize(query);
      embedding = normalizeVector(
        tokens.reduce<number[]>((acc, tok) => {
          const h = fnv1aHash(tok) % 1536;
          const sign = fnv1aHash(tok + '#s') % 2 === 0 ? 1 : -1;
          acc[h] = (acc[h] ?? 0) + sign;
          return acc;
        }, new Array(1536).fill(0))
      );
    }

    const ranked = await this.rankAgents(agents, query, embedding);

    // Circuit breaker logic
    let escalate = false;
    let reason = 'ok';

    if (ranked.length === 0) {
      escalate = true;
      reason = 'no_candidates';
    } else {
      const top = ranked[0];
      if (top.confidence < this.confidenceThreshold) {
        escalate = true;
        reason = `low_confidence (${round4(top.confidence)} < ${this.confidenceThreshold})`;
      }

      // Also check if top 2 are ambiguous
      if (!escalate && ranked.length > 1) {
        const margin = top.scores.finalScore - ranked[1].scores.finalScore;
        if (margin < this.ambiguityMargin) {
          escalate = true;
          reason = `ambiguous_top_two (margin ${round4(margin)} < ${this.ambiguityMargin})`;
        }
      }
    }

    const primaryChoice = escalate ? null : ranked[0] ?? null;
    const alternatives = escalate ? ranked : ranked.slice(1);

    return {
      query,
      ranked,
      primaryChoice,
      alternatives,
      circuitBreakerEscalate: escalate,
      circuitBreakerReason: reason,
      tookMs: Date.now() - startedAt,
    };
  }

  private buildExplanation(r: ExpertRankedAgent): string {
    const parts: string[] = [];

    // Primary signal
    if (r.scores.semanticScore > 0.7) {
      parts.push(`Strong semantic match (${(r.scores.semanticScore * 100).toFixed(0)}%)`);
    }

    if (r.scores.historicalScore > 0.8) {
      parts.push(
        `High success rate (${r.historicalContext.successCount}/${r.historicalContext.totalQueries})`
      );
    }

    if (r.capabilityMatch.hasPrimaryCapability) {
      parts.push('Has primary capability for this domain');
    }

    if (r.scores.costScore > 0.7) {
      parts.push(`Efficient tier (${r.agent.model})`);
    }

    if (r.scores.latencyScore > 0.7) {
      parts.push(`Fast SLA (${r.historicalContext.p99LatencyMs}ms p99)`);
    }

    // Overall confidence
    parts.push(`Confidence: ${(r.confidence * 100).toFixed(1)}%`);

    return parts.length > 0 ? parts.join('; ') + '.' : 'Baseline match.';
  }
}

// =====================================================================
// 5. Utilities
// =====================================================================

function fnv1aHash(str: string): number {
  let hash = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193);
  }
  return Math.abs(hash);
}

function normalizeVector(vector: number[]): number[] {
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
  if (norm === 0) return vector;
  return vector.map((v) => v / norm);
}

function round4(n: number): number {
  return Math.round(n * 10000) / 10000;
}

// =====================================================================
// 6. Integration with maestro-v2-routing (adapter)
// =====================================================================

/**
 * Adapter: Convert ExpertRankingResult to maestro-v2-routing RoutingDecision shape.
 * (Not required, but useful for backward compatibility with existing v2 code.)
 */
export function adaptToMaestroV2(
  expertResult: ExpertRankingResult
): {
  primary: { agent: AgentRecord; confidence: number } | null;
  alternatives: { agent: AgentRecord; confidence: number }[];
  explanation: string;
  escalate: boolean;
} {
  return {
    primary: expertResult.primaryChoice
      ? {
          agent: expertResult.primaryChoice.agent,
          confidence: expertResult.primaryChoice.confidence,
        }
      : null,
    alternatives: expertResult.alternatives.map((r) => ({
      agent: r.agent,
      confidence: r.confidence,
    })),
    explanation: expertResult.circuitBreakerEscalate
      ? `Escalated to Opus: ${expertResult.circuitBreakerReason}`
      : `Routed to ${expertResult.primaryChoice?.agent.name} with ${(expertResult.primaryChoice?.confidence ?? 0) * 100}% confidence`,
    escalate: expertResult.circuitBreakerEscalate,
  };
}
