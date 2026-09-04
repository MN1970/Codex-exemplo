/**
 * maestro-v2-routing.ts
 * ---------------------------------------------------------------------
 * Manta Maestro v2.0 — Search & Ranking Engine
 *
 * Implements the "Dynamic ranking" + "Explainability" + "Circuit
 * breaker" capabilities described in
 * `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` (§2.2, §4.2) and
 * `docs/EXECUTIVE-SUMMARY-v5-UPGRADE.md`:
 *
 *   - searchAgents(query, top_k)    → hybrid BM25 + semantic retrieval
 *   - rankAgents(candidates, query) → weighted re-rank (0.6 BM25 + 0.4 semantic)
 *   - explainRanking(ranked, query) → JSON reasoning per agent
 *   - circuit breaker                → confidence < 0.6 escalates to Opus
 *
 * Design goals:
 *   - Zero hard dependencies (no @supabase/supabase-js, no embedding
 *     SDK import) so this module compiles and runs standalone. Real
 *     integrations (Supabase pgvector, Claude embeddings) are wired in
 *     via dependency injection — see `AgentRegistrySource` and
 *     `EmbeddingProvider` below.
 *   - Backward compatible with the v4.2 static registry: the default
 *     `AgentRegistrySource` is `StaticAgentRegistrySource`, seeded from
 *     the 20-agent table in `CLAUDE.md`. `SupabaseAgentRegistrySource`
 *     falls back to it automatically if the DB is unreachable (per
 *     "Fallback: manter CLAUDE.md como source of truth se DB fora").
 *   - Never routes to an agent whose health status is "down".
 *
 * See `maestro-v2-routing.test.ts` for a runnable test skeleton
 * (Node's built-in `node:test` runner — no extra dependency to add).
 */

// =====================================================================
// 1. Domain types
// =====================================================================

/** Model tier a given agent runs on by default. */
export type ModelTier = 'haiku' | 'sonnet' | 'opus';

export type AgentLifecycle = 'alpha' | 'beta' | 'prod';

export type AgentHealthStatus = 'healthy' | 'degraded' | 'down';

/**
 * Normalized agent shape. Field names intentionally mirror the
 * `agents` table schema from `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`
 * (§4.1) and the auto-registration parser output
 * (`infra/agent-registry/lib/parse-agent-md.js`) so records loaded
 * from either source are interchangeable.
 */
export interface AgentRecord {
  /** Stable slug, e.g. "agente-saneamento" or "manta-03-s8". */
  id: string;
  name: string;
  description: string;
  expertise_primary: string[];
  expertise_secondary: string[];
  /** Flat keyword list used for BM25 (usually primary ∪ secondary). */
  keywords: string[];
  model: ModelTier;
  skills: string[];
  tools: string[];
  rag_collections: string[];
  handoffs_to: string[];
  lifecycle: AgentLifecycle;
  version: string | null;
  source_path?: string | null;

  // --- Optional Fase 1+ telemetry (populated once agent_health /
  // routing_events exist in Supabase; absent when reading raw CLAUDE.md). ---
  /** Priority tier, lower = more critical/expensive (Opus-only ≈ 1). */
  tier?: number;
  cost_per_call?: number;
  success_rate?: number;
  status?: AgentHealthStatus;
  /** Precomputed description embedding, if the registry supplies one. */
  embedding?: number[] | null;
}

// =====================================================================
// 2. Errors
// =====================================================================

/** Base class for every error this module raises. Never thrown directly. */
export class MaestroRoutingError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = new.target.name;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class InvalidQueryError extends MaestroRoutingError {}
export class InvalidTopKError extends MaestroRoutingError {}
export class EmptyRegistryError extends MaestroRoutingError {}
export class EmbeddingProviderError extends MaestroRoutingError {}
export class RegistrySourceError extends MaestroRoutingError {}

const MAX_QUERY_LENGTH = 4000;
const MAX_TOP_K = 50;

function assertValidQuery(query: unknown): asserts query is string {
  if (typeof query !== 'string') {
    throw new InvalidQueryError('query must be a string.');
  }
  if (query.trim().length === 0) {
    throw new InvalidQueryError('query must not be empty.');
  }
  if (query.length > MAX_QUERY_LENGTH) {
    throw new InvalidQueryError(
      `query exceeds max length of ${MAX_QUERY_LENGTH} characters.`
    );
  }
}

function assertValidTopK(top_k: unknown): asserts top_k is number {
  if (typeof top_k !== 'number' || !Number.isInteger(top_k) || top_k <= 0) {
    throw new InvalidTopKError('top_k must be a positive integer.');
  }
  if (top_k > MAX_TOP_K) {
    throw new InvalidTopKError(`top_k must not exceed ${MAX_TOP_K}.`);
  }
}

// =====================================================================
// 3. Tokenization & BM25
// =====================================================================

const STOPWORDS = new Set([
  // PT-BR
  'a', 'o', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'e', 'em', 'um',
  'uma', 'para', 'com', 'no', 'na', 'nos', 'nas', 'que', 'ao', 'aos', 'à',
  'às', 'é', 'ou', 'se', 'por', 'como', 'qual', 'quais', 'meu', 'minha',
  // EN
  'the', 'a', 'an', 'of', 'for', 'to', 'and', 'or', 'in', 'on', 'is', 'are',
]);

/** Lowercases, strips diacritics, splits on non-alphanumerics, drops stopwords. */
export function tokenize(text: string): string[] {
  const normalized = text
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // strip accents
    .toLowerCase();

  return normalized
    .split(/[^a-z0-9]+/)
    .map((t) => t.trim())
    .filter((t) => t.length > 1 && !STOPWORDS.has(t));
}

interface Bm25Doc {
  id: string;
  tokens: string[];
  termFreq: Map<string, number>;
  length: number;
}

export interface Bm25Options {
  k1?: number;
  b?: number;
}

/**
 * Minimal, dependency-free BM25 index. Each `AgentRecord` becomes one
 * "document" built from its name + description + expertise + keywords,
 * so BM25 approximates "how well does this agent's expertise vocabulary
 * match the query" — the `expertise (keywords)` component described in
 * §4.2 of the upgrade spec.
 */
export class Bm25Index {
  private readonly docs: Map<string, Bm25Doc> = new Map();
  private readonly docFreq: Map<string, number> = new Map();
  private readonly avgDocLength: number;
  private readonly k1: number;
  private readonly b: number;

  constructor(agents: AgentRecord[], options: Bm25Options = {}) {
    this.k1 = options.k1 ?? 1.5;
    this.b = options.b ?? 0.75;

    let totalLength = 0;
    for (const agent of agents) {
      const tokens = tokenize(agentToBm25Text(agent));
      const termFreq = new Map<string, number>();
      for (const tok of tokens) {
        termFreq.set(tok, (termFreq.get(tok) ?? 0) + 1);
      }
      for (const tok of termFreq.keys()) {
        this.docFreq.set(tok, (this.docFreq.get(tok) ?? 0) + 1);
      }
      this.docs.set(agent.id, {
        id: agent.id,
        tokens,
        termFreq,
        length: tokens.length,
      });
      totalLength += tokens.length;
    }

    this.avgDocLength = this.docs.size > 0 ? totalLength / this.docs.size : 0;
  }

  private idf(term: string): number {
    const n = this.docs.size;
    const df = this.docFreq.get(term) ?? 0;
    // BM25+ style idf; floors at a small positive value so unseen terms
    // never produce a negative contribution.
    return Math.log(1 + (n - df + 0.5) / (df + 0.5));
  }

  /** Raw (unbounded, >= 0) BM25 score of `queryTokens` against one agent. */
  score(queryTokens: string[], agentId: string): number {
    const doc = this.docs.get(agentId);
    if (!doc || doc.length === 0 || this.avgDocLength === 0) return 0;

    let score = 0;
    for (const term of new Set(queryTokens)) {
      const freq = doc.termFreq.get(term);
      if (!freq) continue;
      const idf = this.idf(term);
      const numerator = freq * (this.k1 + 1);
      const denominator =
        freq + this.k1 * (1 - this.b + (this.b * doc.length) / this.avgDocLength);
      score += idf * (numerator / denominator);
    }
    return score;
  }

  /** Query terms that literally matched this agent's corpus (for explainability). */
  matchedTerms(queryTokens: string[], agentId: string): string[] {
    const doc = this.docs.get(agentId);
    if (!doc) return [];
    return [...new Set(queryTokens)].filter((t) => doc.termFreq.has(t));
  }
}

function agentToBm25Text(agent: AgentRecord): string {
  return [
    agent.name,
    agent.description,
    agent.expertise_primary.join(' '),
    agent.expertise_secondary.join(' '),
    agent.keywords.join(' '),
  ].join(' ');
}

// =====================================================================
// 4. Embeddings & semantic similarity
// =====================================================================

export interface EmbeddingProvider {
  readonly name: string;
  readonly dimensions: number;
  embed(text: string): Promise<number[]>;
}

/**
 * Deterministic, dependency-free embedding via the hashing trick.
 * Not a real semantic model — it approximates token-overlap similarity
 * offline, which is enough for local dev, unit tests, and as the
 * degraded-mode fallback if the real embedding provider is unavailable.
 * Swap in `ClaudeEmbeddingProvider` (or any `EmbeddingProvider`) for
 * production semantic search, per "Claude embeddings = semantic search
 * pronto" (docs/EXECUTIVE-SUMMARY-v5-UPGRADE.md §"THE OPPORTUNITY").
 */
export class LocalHashingEmbeddingProvider implements EmbeddingProvider {
  readonly name = 'local-hashing-fallback';
  readonly dimensions: number;

  constructor(dimensions = 1536) {
    this.dimensions = dimensions;
  }

  async embed(text: string): Promise<number[]> {
    const vector = new Array<number>(this.dimensions).fill(0);
    const tokens = tokenize(text);
    for (const token of tokens) {
      const bucket = fnv1aHash(token) % this.dimensions;
      const sign = fnv1aHash(token + '#sign') % 2 === 0 ? 1 : -1;
      vector[bucket] += sign;
    }
    return normalizeVector(vector);
  }
}

/**
 * Production adapter: wraps an injected embedding function so this
 * module never hard-imports an SDK. Wire `embedFn` to whichever
 * embedding backend Manta standardizes on (Claude API, Voyage, or a
 * Supabase edge function proxying either).
 */
export class DelegatingEmbeddingProvider implements EmbeddingProvider {
  readonly name: string;
  readonly dimensions: number;

  constructor(
    private readonly embedFn: (text: string) => Promise<number[]>,
    options: { name?: string; dimensions?: number } = {}
  ) {
    this.name = options.name ?? 'delegating-provider';
    this.dimensions = options.dimensions ?? 1536;
  }

  async embed(text: string): Promise<number[]> {
    try {
      const vector = await this.embedFn(text);
      if (!Array.isArray(vector) || vector.length === 0) {
        throw new Error('embedding function returned an empty/invalid vector.');
      }
      return vector;
    } catch (err) {
      throw new EmbeddingProviderError(
        `Embedding provider "${this.name}" failed to embed text.`,
        err
      );
    }
  }
}

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

/** Cosine similarity in [-1, 1]; returns 0 for degenerate (zero-length) vectors. */
export function cosineSimilarity(a: number[], b: number[]): number {
  const len = Math.min(a.length, b.length);
  if (len === 0) return 0;
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < len; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

// =====================================================================
// 5. Score normalization
// =====================================================================

/** Min-max normalizes a list of scores to [0, 1]. Flat inputs map to 0.5. */
function normalizeMinMax(values: number[]): number[] {
  if (values.length === 0) return [];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min;
  if (range === 0) return values.map(() => 0.5);
  return values.map((v) => (v - min) / range);
}

// =====================================================================
// 6. Agent registry — static seed + pluggable sources
// =====================================================================

/**
 * Static fallback registry seeded from `CLAUDE.md` v4.2 (20 agentes, 3
 * eixos). This is the "source of truth if DB is down" referenced in
 * the v5.0 upgrade spec §9.1.
 */
export const AGENT_REGISTRY_SEED: AgentRecord[] = [
  // ---- Eixo 1 — Horizontais ----
  {
    id: 'manta-00', name: 'maestro (router)',
    description: 'Roteador central do ecossistema Manta — direciona cada consulta ao agente horizontal ou vertical correto com base em expertise, segmento e fase do ciclo de vida.',
    expertise_primary: ['roteamento', 'orquestração', 'triagem de consulta'],
    expertise_secondary: ['intake', 'handoff entre agentes'],
    keywords: ['maestro', 'router', 'roteamento', 'triagem'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 0,
  },
  {
    id: 'manta-01', name: 'claims',
    description: 'Claims e reequilíbrio econômico-financeiro de contratos de infraestrutura — improdutividade, disrupção, quebra de premissas de proposta.',
    expertise_primary: ['claims', 'reequilíbrio econômico-financeiro', 'disrupção', 'quebra de premissas'],
    expertise_secondary: ['improdutividade', 'janelas de impacto', 'cascata cronológica'],
    keywords: ['claim', 'reequilíbrio', 'disrupção', 'improdutividade', 'premissas de proposta'],
    model: 'opus', skills: ['conclusao-janelas'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: [], handoffs_to: ['manta-02', 'manta-07'], lifecycle: 'prod', version: 'v4.2', tier: 1,
  },
  {
    id: 'manta-02', name: 'contratual',
    description: 'Análise contratual — FIDIC, aditivos, cláusulas de reequilíbrio, matriz de risco contratual.',
    expertise_primary: ['contratual', 'FIDIC', 'aditivo contratual', 'cláusulas'],
    expertise_secondary: ['matriz de risco', 'concessão'],
    keywords: ['contrato', 'FIDIC', 'aditivo', 'cláusula', 'concessão'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob'],
    rag_collections: [], handoffs_to: ['manta-01'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-04', name: 'imobiliario',
    description: 'Assuntos imobiliários — desapropriação, avaliação de imóveis, servidões para obras de infraestrutura.',
    expertise_primary: ['imobiliário', 'desapropriação', 'avaliação de imóveis'],
    expertise_secondary: ['servidão', 'laudo de avaliação'],
    keywords: ['imóvel', 'desapropriação', 'servidão', 'avaliação'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-05', name: 'orcamento',
    description: 'Orçamento de obras — SICRO, SINAPI, composições de custo, memórias de cálculo.',
    expertise_primary: ['orçamento', 'SICRO', 'SINAPI', 'custo unitário'],
    expertise_secondary: ['composição de serviço', 'BDI'],
    keywords: ['orçamento', 'sicro', 'sinape', 'sinapi', 'custo', 'bdi'],
    model: 'sonnet', skills: ['sicro-completo', 'sicro-composicoes', 'sicro-similaridade'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-06', name: 'modelagem',
    description: 'Modelagem financeira e BIM — fluxo de caixa de concessões, viabilidade econômica, integração com projetos BIM/CAD.',
    expertise_primary: ['modelagem financeira', 'BIM', 'fluxo de caixa', 'viabilidade econômica'],
    expertise_secondary: ['TIR', 'VPL', 'clash detection'],
    keywords: ['modelagem', 'bim', 'fluxo de caixa', 'viabilidade', 'tir', 'vpl'],
    model: 'sonnet', skills: ['autodesk-toolkit'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-07', name: 'cronograma',
    description: 'Cronogramas de obra — Primavera P6 (XER), Microsoft Project, caminho crítico, curva S.',
    expertise_primary: ['cronograma', 'Primavera P6', 'Microsoft Project', 'caminho crítico'],
    expertise_secondary: ['curva S', 'WBS', 'baseline'],
    keywords: ['cronograma', 'xer', 'p6', 'mpp', 'caminho critico', 'wbs'],
    model: 'sonnet', skills: ['cronograma-toolkit', 'xer-msp-toolkit', 'xer-p6-analytics'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: [], handoffs_to: ['manta-01'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-13', name: 'bd',
    description: 'Business development — prospecção de oportunidades, pipeline comercial, radar de licitações.',
    expertise_primary: ['business development', 'prospecção', 'pipeline comercial'],
    expertise_secondary: ['radar de licitação', 'oportunidades'],
    keywords: ['bd', 'business development', 'prospeccao', 'pipeline', 'oportunidade'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob', 'WebSearch'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-14', name: 'apresentacoes',
    description: 'Apresentações comerciais e técnicas — geração de PPTX no padrão visual Manta.',
    expertise_primary: ['apresentações', 'pptx', 'slides comerciais'],
    expertise_secondary: ['storytelling executivo'],
    keywords: ['apresentacao', 'pptx', 'slides', 'deck'],
    model: 'sonnet', skills: ['pptx'], tools: ['Read', 'Write', 'Grep', 'Glob'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-15', name: 'advisory',
    description: 'Advisory estratégico — due diligence, M&A, estruturação de negócios de infraestrutura.',
    expertise_primary: ['advisory', 'due diligence', 'M&A'],
    expertise_secondary: ['estruturação de negócio', 'valuation'],
    keywords: ['advisory', 'due diligence', 'm&a', 'valuation'],
    model: 'opus', skills: ['mk-manta'], tools: ['Read', 'Grep', 'Glob', 'WebSearch'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 1,
  },
  {
    id: 'manta-16', name: 'arquiteto-ia',
    description: 'Arquitetura de sistemas de IA — desenho e revisão de agentes, skills, pipelines e integrações MCP do ecossistema Manta.',
    expertise_primary: ['arquitetura de agentes IA', 'Claude Code', 'MCP', 'skills'],
    expertise_secondary: ['model tiering', 'anti-padrão IA'],
    keywords: ['arquitetura ia', 'claude code', 'mcp', 'skill', 'agente'],
    model: 'opus', skills: ['manta-arquiteto-ia'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: [], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 1,
  },

  // ---- Eixo 2 — Verticais por segmento (S1-S4 + S6-S10) ----
  {
    id: 'manta-03-s1', name: 'agente-infraestrutura (Rodovias)',
    description: 'Engenharia rodoviária — pavimento, terraplenagem, orçamento SICRO/DNIT.',
    expertise_primary: ['rodovia', 'pavimento', 'CBUQ', 'BGS', 'terraplenagem'],
    expertise_secondary: ['SICRO', 'DNIT'],
    keywords: ['rodovia', 'pavimento', 'cbuq', 'bgs', 'terraplenagem', 'sicro', 'dnit'],
    model: 'sonnet', skills: ['rodovias', 'rodovias-geotecnia', 'projeto-rodovias-cad'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: ['rod:'], handoffs_to: ['manta-05', 'manta-07'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s2', name: 'agente-infraestrutura (OAE)',
    description: 'Obras de arte especiais — pontes, viadutos, túneis rodoviários, NBR 7187.',
    expertise_primary: ['ponte', 'viaduto', 'OAE', 'NBR 7187', 'túnel rodoviário'],
    expertise_secondary: ['fundações', 'infraestrutura de pontes'],
    keywords: ['ponte', 'viaduto', 'oae', 'nbr 7187', 'tunel rodoviario'],
    model: 'sonnet', skills: ['gr04-infraestrutura-pontes'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: ['oae:'], handoffs_to: ['manta-05'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s3', name: 'agente-infraestrutura (Ferrovia)',
    description: 'Engenharia ferroviária — via permanente, AMV, dormentes.',
    expertise_primary: ['ferrovia', 'trilho', 'AMV', 'dormente', 'via permanente'],
    expertise_secondary: [],
    keywords: ['ferrovia', 'trilho', 'amv', 'dormente', 'via permanente'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: ['fer:'], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s4', name: 'agente-infraestrutura (Metrô)',
    description: 'Metrô e VLT — estações, escavação NATM, PSD.',
    expertise_primary: ['metrô', 'estação', 'NATM', 'PSD', 'VLT'],
    expertise_secondary: ['linha 4', 'linha 5', 'túnel metroviário'],
    keywords: ['metro', 'estacao', 'natm', 'psd', 'vlt', 'linha 4', 'linha 5'],
    model: 'sonnet', skills: ['portal-metro-l4'], tools: ['Read', 'Grep', 'Glob', 'Bash'],
    rag_collections: ['met:'], handoffs_to: [], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s6', name: 'agente-portos',
    description: 'Portos e terminais — dragagem, molhes, berços, ANTAQ, PIANC.',
    expertise_primary: ['porto', 'terminal', 'ANTAQ', 'dragagem', 'molhe'],
    expertise_secondary: ['berço', 'calado', 'contêiner', 'granel'],
    keywords: ['porto', 'terminal', 'antaq', 'dragagem', 'molhe', 'berco', 'calado', 'conteiner', 'granel'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob', 'WebSearch', 'WebFetch'],
    rag_collections: ['por:'], handoffs_to: ['manta-03-s7'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s7', name: 'agente-aeroportos',
    description: 'Aeroportos — dimensionamento de pista, ANAC/RBAC, ICAO, balizamento.',
    expertise_primary: ['aeroporto', 'pista pouso', 'ANAC', 'ICAO'],
    expertise_secondary: ['TPS', 'TECA', 'balizamento'],
    keywords: ['aeroporto', 'pista pouso', 'anac', 'icao', 'tps', 'teca', 'balizamento'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob', 'WebSearch', 'WebFetch'],
    rag_collections: ['aer:'], handoffs_to: ['manta-03-s6'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s8', name: 'agente-saneamento',
    description: 'Saneamento — ETA/ETE, adutoras, esgoto, SNIS, prioridade AySA. Lei 14.026/2020.',
    expertise_primary: ['saneamento', 'ETA', 'ETE', 'adutora', 'esgoto'],
    expertise_secondary: ['AySA', 'drenagem urbana', 'SNIS'],
    keywords: ['saneamento', 'eta', 'ete', 'adutora', 'esgoto', 'aysa', 'drenagem urbana', 'snis'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob', 'WebSearch', 'WebFetch'],
    rag_collections: ['san:'], handoffs_to: ['manta-03-s9', 'manta-03-s10'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s9', name: 'agente-energia',
    description: 'Energia — transmissão, subestações, ANEEL/ONS/EPE, leilões de transmissão.',
    expertise_primary: ['transmissão', 'LT', 'subestação', 'ANEEL'],
    expertise_secondary: ['RAP', 'leilão transmissão', 'ONS', 'EPE'],
    keywords: ['transmissao', 'lt', 'subestacao', 'aneel', 'rap', 'leilao transmissao', 'ons', 'epe'],
    model: 'sonnet', skills: ['ler-edital-aneel'], tools: ['Read', 'Grep', 'Glob', 'WebSearch', 'WebFetch'],
    rag_collections: ['ene:'], handoffs_to: ['manta-03-s8', 'manta-03-s10'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
  {
    id: 'manta-03-s10', name: 'agente-barragens',
    description: 'Barragens — CFRD/CCR, rejeitos, PNSB, ICOLD/CBDB, descaracterização de TSF.',
    expertise_primary: ['barragem', 'vertedouro', 'CFRD', 'CCR'],
    expertise_secondary: ['rejeitos', 'PNSB', 'ICOLD', 'CBDB', 'TSF'],
    keywords: ['barragem', 'vertedouro', 'cfrd', 'ccr', 'rejeitos', 'pnsb', 'icold', 'cbdb', 'tsf'],
    model: 'sonnet', skills: [], tools: ['Read', 'Grep', 'Glob', 'WebSearch', 'WebFetch'],
    rag_collections: ['bar:'], handoffs_to: ['manta-03-s9'], lifecycle: 'prod', version: 'v4.2', tier: 2,
  },
];

/** Pluggable source of agent records — DB-backed or static. */
export interface AgentRegistrySource {
  readonly name: string;
  loadAgents(): Promise<AgentRecord[]>;
}

/** Default source: the static CLAUDE.md-derived seed above. */
export class StaticAgentRegistrySource implements AgentRegistrySource {
  readonly name = 'claude-md-static';
  constructor(private readonly agents: AgentRecord[] = AGENT_REGISTRY_SEED) {}
  async loadAgents(): Promise<AgentRecord[]> {
    return this.agents;
  }
}

/**
 * Structural type for a Supabase-js-like client, kept minimal so this
 * file never imports `@supabase/supabase-js` directly. Pass the real
 * client from `infra/agent-registry/lib/supabase-client.js` at the
 * call site.
 */
export interface SupabaseLikeClient {
  from(table: string): {
    select(columns: string): Promise<{ data: unknown[] | null; error: unknown | null }>;
  };
}

/**
 * Reads from the live `agents` table (schema in
 * docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.1) and transparently
 * falls back to a `StaticAgentRegistrySource` if the DB call fails —
 * implements "Fallback: manter CLAUDE.md como source of truth se DB
 * fora" (§1.2 / §9.1 of the upgrade spec).
 */
export class SupabaseAgentRegistrySource implements AgentRegistrySource {
  readonly name = 'supabase';

  constructor(
    private readonly client: SupabaseLikeClient,
    private readonly fallback: AgentRegistrySource = new StaticAgentRegistrySource()
  ) {}

  async loadAgents(): Promise<AgentRecord[]> {
    try {
      const { data, error } = await this.client.from('agents').select('*');
      if (error) {
        throw new RegistrySourceError('Supabase returned an error reading `agents`.', error);
      }
      if (!data || data.length === 0) {
        throw new RegistrySourceError('Supabase `agents` table returned no rows.');
      }
      return data.map(normalizeSupabaseRow);
    } catch (err) {
      // Degrade gracefully instead of taking the whole Maestro down.
      return this.fallback.loadAgents();
    }
  }
}

function normalizeSupabaseRow(row: unknown): AgentRecord {
  const r = row as Record<string, unknown>;
  return {
    id: String(r.id),
    name: String(r.name ?? r.id),
    description: String(r.description ?? ''),
    expertise_primary: asStringArray(r.expertise_primary),
    expertise_secondary: asStringArray(r.expertise_secondary),
    keywords: asStringArray(r.keywords ?? r.expertise_primary),
    model: (r.model as ModelTier) ?? 'sonnet',
    skills: asStringArray(r.skills),
    tools: asStringArray(r.tools),
    rag_collections: asStringArray(r.rag_collections),
    handoffs_to: asStringArray(r.handoffs_to),
    lifecycle: (r.lifecycle as AgentLifecycle) ?? 'prod',
    version: (r.version as string | null) ?? null,
    source_path: null,
    tier: typeof r.tier === 'number' ? r.tier : undefined,
    cost_per_call: typeof r.cost_per_call === 'number' ? r.cost_per_call : undefined,
    success_rate: typeof r.success_rate === 'number' ? r.success_rate : undefined,
    status: (r.status as AgentHealthStatus) ?? undefined,
    embedding: Array.isArray(r.description_embedding)
      ? (r.description_embedding as number[])
      : null,
  };
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String) : [];
}

// =====================================================================
// 7. searchAgents — hybrid BM25 + semantic retrieval
// =====================================================================

export interface SearchCandidate {
  agent: AgentRecord;
  /** Raw (unbounded) BM25 score. */
  bm25Raw: number;
  /** Raw cosine similarity in [-1, 1] against the query embedding. */
  semanticRaw: number;
}

export interface SearchAgentsOptions {
  registrySource?: AgentRegistrySource;
  embeddingProvider?: EmbeddingProvider;
  bm25Options?: Bm25Options;
  /** Retrieval pool = top_k * multiplier, re-ranked later by rankAgents. */
  candidatePoolMultiplier?: number;
  /** Exclude agents currently reporting these health statuses. Default: ['down']. */
  excludeStatuses?: AgentHealthStatus[];
}

export interface SearchAgentsResult {
  query: string;
  candidates: SearchCandidate[];
  registrySource: string;
  embeddingProvider: string;
  tookMs: number;
}

/**
 * Retrieval phase: pulls a candidate pool (BM25 ∪ semantic top matches)
 * from the agent registry. Does NOT compute the final weighted score —
 * that is `rankAgents`'s job — so callers can swap re-ranking logic
 * without re-querying the registry/embeddings.
 */
export async function searchAgents(
  query: string,
  top_k: number,
  options: SearchAgentsOptions = {}
): Promise<SearchAgentsResult> {
  const startedAt = Date.now();
  assertValidQuery(query);
  assertValidTopK(top_k);

  const registrySource = options.registrySource ?? new StaticAgentRegistrySource();
  const embeddingProvider = options.embeddingProvider ?? new LocalHashingEmbeddingProvider();
  const excludeStatuses = options.excludeStatuses ?? ['down'];
  const poolMultiplier = options.candidatePoolMultiplier ?? 3;

  let agents: AgentRecord[];
  try {
    agents = await registrySource.loadAgents();
  } catch (err) {
    throw new RegistrySourceError(
      `Failed to load agents from registry source "${registrySource.name}".`,
      err
    );
  }

  agents = agents.filter((a) => !excludeStatuses.includes(a.status as AgentHealthStatus));
  if (agents.length === 0) {
    throw new EmptyRegistryError('Agent registry has no eligible (non-down) agents.');
  }

  const bm25 = new Bm25Index(agents, options.bm25Options);
  const queryTokens = tokenize(query);

  let queryEmbedding: number[];
  try {
    queryEmbedding = await embeddingProvider.embed(query);
  } catch (err) {
    if (err instanceof EmbeddingProviderError) throw err;
    throw new EmbeddingProviderError('Failed to embed query.', err);
  }

  const candidates: SearchCandidate[] = [];
  for (const agent of agents) {
    const bm25Raw = bm25.score(queryTokens, agent.id);
    let semanticRaw = 0;
    if (agent.embedding && agent.embedding.length > 0) {
      semanticRaw = cosineSimilarity(queryEmbedding, agent.embedding);
    } else {
      // No precomputed embedding on the record (e.g. static seed) —
      // embed the agent's own text on the fly. Fine for small
      // registries (~20-100 agents); production should precompute and
      // cache `embedding` on the agent row instead.
      const agentVector = await embeddingProvider.embed(agentToBm25Text(agent));
      semanticRaw = cosineSimilarity(queryEmbedding, agentVector);
    }
    candidates.push({ agent, bm25Raw, semanticRaw });
  }

  // Union of top-N by BM25 and top-N by semantic similarity, N = top_k * multiplier.
  const poolSize = Math.min(agents.length, Math.max(top_k * poolMultiplier, top_k));
  const byBm25 = [...candidates].sort((a, b) => b.bm25Raw - a.bm25Raw).slice(0, poolSize);
  const bySemantic = [...candidates].sort((a, b) => b.semanticRaw - a.semanticRaw).slice(0, poolSize);

  const pool = new Map<string, SearchCandidate>();
  for (const c of [...byBm25, ...bySemantic]) pool.set(c.agent.id, c);

  return {
    query,
    candidates: [...pool.values()],
    registrySource: registrySource.name,
    embeddingProvider: embeddingProvider.name,
    tookMs: Date.now() - startedAt,
  };
}

// =====================================================================
// 8. rankAgents — weighted hybrid scoring (0.6 BM25 + 0.4 semantic)
// =====================================================================

export const DEFAULT_BM25_WEIGHT = 0.6;
export const DEFAULT_SEMANTIC_WEIGHT = 0.4;

export interface RankAgentsOptions {
  bm25Weight?: number;
  semanticWeight?: number;
}

export interface RankedAgent {
  agent: AgentRecord;
  /** Min-max normalized BM25 score within this candidate set, [0, 1]. */
  bm25Score: number;
  /** Min-max normalized semantic score within this candidate set, [0, 1]. */
  semanticScore: number;
  /** bm25Weight * bm25Score + semanticWeight * semanticScore, [0, 1]. */
  finalScore: number;
  /** Confidence Maestro should report to the user / circuit breaker. */
  confidence: number;
  /** Query tokens that literally matched this agent's keyword corpus. */
  matchedTerms: string[];
  /** 1-based rank after sorting by finalScore desc. */
  rank: number;
}

/**
 * Re-ranks a candidate pool by the blended score described in
 * `docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md` §2.2 / §4.2.1:
 * `0.6 * BM25 + 0.4 * semantic`, both normalized to [0, 1] across the
 * candidate set before blending (raw BM25 is unbounded, raw cosine
 * similarity is in [-1, 1] — neither is directly comparable to the
 * other without normalization).
 */
export function rankAgents(
  candidates: SearchCandidate[],
  query: string,
  options: RankAgentsOptions = {}
): RankedAgent[] {
  assertValidQuery(query);

  const bm25Weight = options.bm25Weight ?? DEFAULT_BM25_WEIGHT;
  const semanticWeight = options.semanticWeight ?? DEFAULT_SEMANTIC_WEIGHT;
  const weightSum = bm25Weight + semanticWeight;
  if (weightSum <= 0) {
    throw new MaestroRoutingError('bm25Weight + semanticWeight must be > 0.');
  }

  if (candidates.length === 0) return [];

  const bm25Normalized = normalizeMinMax(candidates.map((c) => c.bm25Raw));
  const semanticNormalized = normalizeMinMax(candidates.map((c) => c.semanticRaw));
  const queryTokens = tokenize(query);
  const bm25 = new Bm25Index(candidates.map((c) => c.agent));

  const ranked: Omit<RankedAgent, 'rank'>[] = candidates.map((c, i) => {
    const bm25Score = bm25Normalized[i];
    const semanticScore = semanticNormalized[i];
    const finalScore = (bm25Weight * bm25Score + semanticWeight * semanticScore) / weightSum;
    return {
      agent: c.agent,
      bm25Score,
      semanticScore,
      finalScore,
      confidence: finalScore,
      matchedTerms: bm25.matchedTerms(queryTokens, c.agent.id),
    };
  });

  ranked.sort((a, b) => b.finalScore - a.finalScore);
  return ranked.map((r, i) => ({ ...r, rank: i + 1 }));
}

// =====================================================================
// 9. Circuit breaker — escalate to Opus below confidence threshold
// =====================================================================

export const DEFAULT_CONFIDENCE_THRESHOLD = 0.6;
export const DEFAULT_AMBIGUITY_MARGIN = 0.05;

export type CircuitBreakerReason =
  | 'ok'
  | 'no_candidates'
  | 'low_confidence'
  | 'ambiguous_top_two';

export interface CircuitBreakerOptions {
  /** Escalate to Opus if top confidence is below this. Default 0.6. */
  confidenceThreshold?: number;
  /** Escalate (for disambiguation) if top-two finalScore gap is below this. Default 0.05. */
  ambiguityMargin?: number;
}

export interface CircuitBreakerResult {
  escalate: boolean;
  reason: CircuitBreakerReason;
  recommendedTier: ModelTier;
  topConfidence: number;
  marginToRunnerUp: number | null;
}

/**
 * Implements the circuit breaker described in
 * docs/EXECUTIVE-SUMMARY-v5-UPGRADE.md ("Agent timeout cascade —
 * Circuit breakers, fallback strategy") and the CLAUDE.md "Casos
 * ambíguos" section: if confidence < 0.6, or the top two candidates
 * are too close to call, escalate to Opus for disambiguation /
 * higher-reasoning routing instead of committing to a shaky pick.
 */
export function evaluateCircuitBreaker(
  ranked_agents: RankedAgent[],
  options: CircuitBreakerOptions = {}
): CircuitBreakerResult {
  const confidenceThreshold = options.confidenceThreshold ?? DEFAULT_CONFIDENCE_THRESHOLD;
  const ambiguityMargin = options.ambiguityMargin ?? DEFAULT_AMBIGUITY_MARGIN;

  if (ranked_agents.length === 0) {
    return {
      escalate: true,
      reason: 'no_candidates',
      recommendedTier: 'opus',
      topConfidence: 0,
      marginToRunnerUp: null,
    };
  }

  const top = ranked_agents[0];
  const runnerUp = ranked_agents[1];
  const margin = runnerUp ? top.finalScore - runnerUp.finalScore : null;

  if (top.confidence < confidenceThreshold) {
    return {
      escalate: true,
      reason: 'low_confidence',
      recommendedTier: 'opus',
      topConfidence: top.confidence,
      marginToRunnerUp: margin,
    };
  }

  if (margin !== null && margin < ambiguityMargin) {
    return {
      escalate: true,
      reason: 'ambiguous_top_two',
      recommendedTier: 'opus',
      topConfidence: top.confidence,
      marginToRunnerUp: margin,
    };
  }

  return {
    escalate: false,
    reason: 'ok',
    recommendedTier: top.agent.model,
    topConfidence: top.confidence,
    marginToRunnerUp: margin,
  };
}

// =====================================================================
// 10. explainRanking — human/audit-facing reasoning JSON
// =====================================================================

export interface AgentExplanation {
  rank: number;
  agent_id: string;
  agent_name: string;
  model: ModelTier;
  score: number;
  confidence: number;
  bm25_score: number;
  semantic_score: number;
  matched_terms: string[];
  explanation: string;
}

export interface ExplainRankingResult {
  query: string;
  generated_at: string;
  weights: { bm25: number; semantic: number };
  /** Top-N candidates, per docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.2.1 example shape. */
  top_candidates: AgentExplanation[];
  chosen: string | null;
  reasoning_summary: string;
  circuit_breaker: CircuitBreakerResult;
}

export interface ExplainRankingOptions {
  topN?: number;
  bm25Weight?: number;
  semanticWeight?: number;
  circuitBreakerOptions?: CircuitBreakerOptions;
}

/**
 * Produces the explainability JSON described in
 * docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §"1.3 Explainability
 * module" — one entry per ranked agent with a human-readable
 * `explanation`, plus the overall `reasoning_summary` and the circuit
 * breaker verdict for this query.
 */
export function explainRanking(
  ranked_agents: RankedAgent[],
  query: string,
  options: ExplainRankingOptions = {}
): ExplainRankingResult {
  assertValidQuery(query);

  const topN = options.topN ?? 3;
  const bm25Weight = options.bm25Weight ?? DEFAULT_BM25_WEIGHT;
  const semanticWeight = options.semanticWeight ?? DEFAULT_SEMANTIC_WEIGHT;
  const circuitBreaker = evaluateCircuitBreaker(ranked_agents, options.circuitBreakerOptions);

  const top_candidates = ranked_agents.slice(0, topN).map((r) => ({
    rank: r.rank,
    agent_id: r.agent.id,
    agent_name: r.agent.name,
    model: r.agent.model,
    score: round4(r.finalScore),
    confidence: round4(r.confidence),
    bm25_score: round4(r.bm25Score),
    semantic_score: round4(r.semanticScore),
    matched_terms: r.matchedTerms,
    explanation: buildAgentExplanation(r),
  }));

  const chosen = circuitBreaker.escalate ? null : ranked_agents[0]?.agent.id ?? null;
  const reasoning_summary = buildReasoningSummary(ranked_agents, circuitBreaker);

  return {
    query,
    generated_at: new Date().toISOString(),
    weights: { bm25: bm25Weight, semantic: semanticWeight },
    top_candidates,
    chosen,
    reasoning_summary,
    circuit_breaker: circuitBreaker,
  };
}

function buildAgentExplanation(r: RankedAgent): string {
  const parts: string[] = [];
  if (r.matchedTerms.length > 0) {
    parts.push(`Matched keywords: ${r.matchedTerms.slice(0, 8).join(', ')}`);
  } else {
    parts.push('No literal keyword match — ranked on semantic similarity alone');
  }
  parts.push(`BM25=${round4(r.bm25Score)}`);
  parts.push(`semantic=${round4(r.semanticScore)}`);
  parts.push(`model=${r.agent.model}`);
  return parts.join('. ') + '.';
}

function buildReasoningSummary(
  ranked_agents: RankedAgent[],
  circuitBreaker: CircuitBreakerResult
): string {
  if (ranked_agents.length === 0) {
    return 'No candidates were found in the agent registry for this query.';
  }
  const top = ranked_agents[0];
  if (circuitBreaker.escalate) {
    return (
      `Escalated to Opus (reason: ${circuitBreaker.reason}, ` +
      `top confidence ${round4(circuitBreaker.topConfidence)} ` +
      `< threshold). Top candidate was "${top.agent.name}" but confidence ` +
      `was insufficient to auto-commit routing.`
    );
  }
  return (
    `Routed to "${top.agent.name}" (${top.agent.id}) with ` +
    `${Math.round(top.confidence * 100)}% confidence, primary match on ` +
    `domain expertise (${top.matchedTerms.slice(0, 3).join(', ') || 'semantic similarity'}).`
  );
}

function round4(n: number): number {
  return Math.round(n * 10000) / 10000;
}

// =====================================================================
// 11. routeQuery — end-to-end orchestrator (search → rank → explain → breaker)
// =====================================================================

export interface RouteQueryOptions
  extends SearchAgentsOptions,
    RankAgentsOptions,
    Pick<ExplainRankingOptions, 'topN' | 'circuitBreakerOptions'> {}

export interface RoutingDecision {
  primary: RankedAgent | null;
  alternatives: RankedAgent[];
  explanation: ExplainRankingResult;
  circuitBreaker: CircuitBreakerResult;
  tookMs: number;
}

/**
 * Full Maestro v2.0 routing pipeline, mirroring `MaestroV2.route()`
 * from docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md §4.2:
 * search → rank → circuit-breaker → explain.
 *
 * Wraps every step so a failure anywhere degrades to a
 * `MaestroRoutingError` with the original cause attached rather than
 * an opaque stack trace — callers (e.g. an HTTP handler) can catch
 * `MaestroRoutingError` uniformly and decide whether to retry, fall
 * back to a human, or escalate.
 */
export async function routeQuery(
  query: string,
  top_k = 5,
  options: RouteQueryOptions = {}
): Promise<RoutingDecision> {
  const startedAt = Date.now();
  try {
    assertValidQuery(query);
    assertValidTopK(top_k);

    const searchResult = await searchAgents(query, top_k, options);
    const ranked = rankAgents(searchResult.candidates, query, options).slice(0, top_k);
    const explanation = explainRanking(ranked, query, {
      topN: options.topN,
      bm25Weight: options.bm25Weight,
      semanticWeight: options.semanticWeight,
      circuitBreakerOptions: options.circuitBreakerOptions,
    });

    return {
      primary: explanation.circuit_breaker.escalate ? null : ranked[0] ?? null,
      alternatives: explanation.circuit_breaker.escalate ? ranked : ranked.slice(1),
      explanation,
      circuitBreaker: explanation.circuit_breaker,
      tookMs: Date.now() - startedAt,
    };
  } catch (err) {
    if (err instanceof MaestroRoutingError) throw err;
    throw new MaestroRoutingError(
      `routeQuery failed unexpectedly for query "${query.slice(0, 80)}".`,
      err
    );
  }
}
