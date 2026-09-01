/**
 * Manta Maestro — Roteador v2 (auto-classification + seleção de agentes + orquestração)
 * ---------------------------------------------------------------------------------------
 * Referência canônica: CLAUDE.md (raiz do repo) — seções:
 *   - "MAPA COMPLETO DE AGENTES — 20 agentes, 3 eixos"
 *   - "ROUTING — Maestro (Manta 00)"
 *   - "RAG — Coleções em Supabase"
 *   - "SHAREPOINT — Routing rules (sp_agent_routing)"
 * Casos ambíguos documentados em tests/routing/prompts.md ("Casos ambíguos / desafiadores").
 *
 * Este módulo é autocontido (zero dependências externas) e cobre o pipeline completo:
 *
 *   texto do usuário
 *        │
 *        ▼
 *   1) Classifier.classify()      → pontuação por segmento (keywords normalizadas)
 *        │
 *        ▼
 *   2) AgentSelector.select()     → agente primário + handoffs/consultas + tier de modelo
 *        │
 *        ▼
 *   3) Orchestrator.buildPlan()   → plano de execução (grupos sequenciais/paralelos)
 *        │
 *        ▼
 *   4) Orchestrator.execute()     → dispatch real via AgentExecutor injetado (Claude API,
 *                                    subagentes, etc.) + síntese final pelo Maestro
 *
 * A integração com a API da Anthropic (ou com Claude Code subagents) é feita injetando um
 * `AgentExecutor` em `MaestroRouterV2.run(...)`. Sem executor customizado, um executor mock
 * determinístico é usado (útil para testes/demonstração — ver `runSelfTest()` no fim do
 * arquivo, que valida o roteador contra os prompts de tests/routing/prompts.md).
 *
 * ATENÇÃO — COLISÃO DE NOME: este arquivo é um protótipo isolado e independente,
 * escrito sem visibilidade do módulo real de produção. Existe hoje em `main`, em
 * `infra/agent-registry/lib/maestro-v2-routing.ts`, um módulo também chamado
 * "Maestro v2", já integrado a Supabase/pgvector (BM25 + busca semântica, ranking,
 * circuit breaker) — não confundir os dois. Este arquivo (`src/router/maestro-router-v2.ts`)
 * não deve ser portado/integrado à produção sem antes reconciliar com aquele módulo real.
 */

// ============================================================================================
// 1. TIPOS BASE
// ============================================================================================

/** Tiers de modelo disponíveis para execução de um agente/etapa. */
export enum ModelTier {
  HAIKU = "haiku",
  SONNET = "sonnet",
  OPUS = "opus",
}

/** As 8 fases do ciclo de vida (Eixo 3 do CLAUDE.md), usadas no intake Q2. */
export enum LifecyclePhase {
  ESTUDO_PREVIO_EVTE = "estudo_previo_evte",
  PROJETO_BASICO = "projeto_basico",
  PROJETO_EXECUTIVO = "projeto_executivo",
  OBRA_EM_EXECUCAO = "obra_em_execucao",
  OPERACAO_MANUTENCAO = "operacao_manutencao",
  PROCESSO_COMPETITIVO_LICITACAO = "processo_competitivo_licitacao",
  DUE_DILIGENCE_MA = "due_diligence_ma",
  ENCERRAMENTO_DESCOMISSIONAMENTO = "encerramento_descomissionamento",
}

export type AgentAxis = "horizontal" | "vertical";

export interface RagCollection {
  slug: string;
  storagePrefix: string; // ex: "san:", "ene:", "por:", "aer:", "bar:"
}

export interface SharePointRouting {
  folder: string; // ex: "03_Projetos/Saneamento/*"
  filePatterns: string[]; // ex: ["*.pdf", "*.dwg", "*.xlsx"]
}

export interface AgentDefinition {
  /** id canônico usado internamente pelo router, ex: "agente-saneamento" */
  id: string;
  /** código do registro mestre, ex: "Manta 03-S8" */
  code: string;
  name: string;
  aliases: string[];
  axis: AgentAxis;
  /** segmento vertical (S1..S10), undefined para horizontais */
  segment?: string;
  /**
   * Tiers de modelo suportados, em ordem de preferência (o primeiro é o default).
   * Agentes com tier único (ex: Opus fixo) têm array de 1 elemento.
   * Agentes "Sonnet/Opus" têm 2 elementos — o segundo é usado em escalonamento.
   */
  tiers: ModelTier[];
  status: string;
  ragCollection?: RagCollection;
  spRouting?: SharePointRouting;
}

// ============================================================================================
// 2. REGISTRO DE AGENTES (fonte: CLAUDE.md — Eixo 1 e Eixo 2)
// ============================================================================================

export const MAESTRO_AGENT: AgentDefinition = {
  id: "maestro",
  code: "Manta 00",
  name: "maestro (router)",
  aliases: ["maestro", "manta-router"],
  axis: "horizontal",
  tiers: [ModelTier.HAIKU, ModelTier.SONNET],
  status: "✅ Operacional",
};

const HORIZONTAL_AGENTS: AgentDefinition[] = [
  MAESTRO_AGENT,
  {
    id: "claims",
    code: "Manta 01",
    name: "claims",
    aliases: ["02-C", "manta-claims"],
    axis: "horizontal",
    tiers: [ModelTier.OPUS],
    status: "✅ Operacional",
  },
  {
    id: "contratual",
    code: "Manta 02",
    name: "contratual",
    aliases: ["manta-02", "contratual"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "imobiliario",
    code: "Manta 04",
    name: "imobiliario",
    aliases: ["manta-04"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "orcamento",
    code: "Manta 05",
    name: "orcamento",
    aliases: ["manta-05"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "modelagem",
    code: "Manta 06",
    name: "modelagem",
    aliases: ["manta-06"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET, ModelTier.OPUS],
    status: "✅ Operacional",
  },
  {
    id: "cronograma",
    code: "Manta 07",
    name: "cronograma",
    aliases: ["manta-07"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "bd",
    code: "Manta 13",
    name: "bd",
    aliases: ["manta-13", "business-dev"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "apresentacoes",
    code: "Manta 14",
    name: "apresentacoes",
    aliases: ["manta-14-pptx"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "advisory",
    code: "Manta 15",
    name: "advisory",
    aliases: ["manta-15", "advisory"],
    axis: "horizontal",
    tiers: [ModelTier.SONNET, ModelTier.OPUS],
    status: "✅ Operacional",
  },
  {
    id: "arquiteto-ia",
    code: "Manta 16",
    name: "arquiteto-ia",
    aliases: ["manta-15-arq"],
    axis: "horizontal",
    tiers: [ModelTier.OPUS],
    status: "✅ Operacional",
  },
];

const VERTICAL_AGENTS: AgentDefinition[] = [
  {
    id: "agente-infraestrutura-s1",
    code: "Manta 03-S1",
    name: "agente-infraestrutura (S1 — Rodovias)",
    aliases: ["agente-infraestrutura"],
    axis: "vertical",
    segment: "S1",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
    spRouting: undefined,
  },
  {
    id: "agente-infraestrutura-s2",
    code: "Manta 03-S2",
    name: "agente-infraestrutura (S2 — OAE)",
    aliases: ["agente-infraestrutura"],
    axis: "vertical",
    segment: "S2",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "agente-infraestrutura-s3",
    code: "Manta 03-S3",
    name: "agente-infraestrutura (S3 — Ferrovia)",
    aliases: ["agente-infraestrutura"],
    axis: "vertical",
    segment: "S3",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "agente-infraestrutura-s4",
    code: "Manta 03-S4",
    name: "agente-infraestrutura (S4 — Metrô)",
    aliases: ["agente-infraestrutura"],
    axis: "vertical",
    segment: "S4",
    tiers: [ModelTier.SONNET],
    status: "✅ Operacional",
  },
  {
    id: "agente-infraestrutura-s5",
    code: "Manta 03-S5",
    name: "agente-infraestrutura (S5 — Túneis, coberto por S2/S4)",
    aliases: ["agente-infraestrutura"],
    axis: "vertical",
    segment: "S5",
    tiers: [ModelTier.SONNET],
    status: "⚡ Parcial (coberto por S2/S4)",
  },
  {
    id: "agente-portos",
    code: "Manta 03-S6",
    name: "agente-portos",
    aliases: ["agente-portos"],
    axis: "vertical",
    segment: "S6",
    tiers: [ModelTier.SONNET],
    status: "🆕 Criado 2026-07-05",
    ragCollection: { slug: "portos", storagePrefix: "por:" },
    spRouting: { folder: "03_Projetos/Portos/*", filePatterns: ["*.pdf", "*.dwg", "*.xlsx"] },
  },
  {
    id: "agente-aeroportos",
    code: "Manta 03-S7",
    name: "agente-aeroportos",
    aliases: ["agente-aeroportos"],
    axis: "vertical",
    segment: "S7",
    tiers: [ModelTier.SONNET],
    status: "🆕 Criado 2026-07-05",
    ragCollection: { slug: "aeroportos", storagePrefix: "aer:" },
    spRouting: { folder: "03_Projetos/Aeroportos/*", filePatterns: ["*.pdf", "*.dwg", "*.xlsx"] },
  },
  {
    id: "agente-saneamento",
    code: "Manta 03-S8",
    name: "agente-saneamento",
    aliases: ["agente-saneamento"],
    axis: "vertical",
    segment: "S8",
    tiers: [ModelTier.SONNET],
    status: "🆕 Criado 2026-07-05 — PRIORIDADE AySA",
    ragCollection: { slug: "saneamento", storagePrefix: "san:" },
    spRouting: { folder: "03_Projetos/Saneamento/*", filePatterns: ["*.pdf", "*.dwg", "*.xlsx"] },
  },
  {
    id: "agente-energia",
    code: "Manta 03-S9",
    name: "agente-energia",
    aliases: ["agente-energia"],
    axis: "vertical",
    segment: "S9",
    tiers: [ModelTier.SONNET],
    status: "🆕 Criado 2026-07-05 — ANEEL/State Grid",
    ragCollection: { slug: "energia", storagePrefix: "ene:" },
    spRouting: { folder: "03_Projetos/Energia/*", filePatterns: ["*.pdf", "*.dwg", "*.xlsx"] },
  },
  {
    id: "agente-barragens",
    code: "Manta 03-S10",
    name: "agente-barragens",
    aliases: ["agente-barragens"],
    axis: "vertical",
    segment: "S10",
    tiers: [ModelTier.SONNET],
    status: "🆕 Criado 2026-07-05",
    ragCollection: { slug: "barragens", storagePrefix: "bar:" },
    spRouting: { folder: "03_Projetos/Barragens/*", filePatterns: ["*.pdf", "*.dwg", "*.xlsx"] },
  },
];

export const AGENT_REGISTRY: AgentDefinition[] = [...HORIZONTAL_AGENTS, ...VERTICAL_AGENTS];

const AGENT_BY_ID: Map<string, AgentDefinition> = new Map(
  AGENT_REGISTRY.map((a) => [a.id, a]),
);

export function getAgent(id: string): AgentDefinition {
  const agent = AGENT_BY_ID.get(id);
  if (!agent) {
    throw new Error(`[MaestroRouterV2] agente desconhecido: "${id}"`);
  }
  return agent;
}

// ============================================================================================
// 3. REGRAS DE CLASSIFICAÇÃO (fonte: CLAUDE.md — seção "ROUTING — Maestro (Manta 00)")
// ============================================================================================

/**
 * Uma keyword de rotina traz um `weight` opcional (default 1). Termos genéricos que
 * legitimamente co-ocorrem em textos de OUTROS segmentos (ex: "rodovia" aparece tanto
 * em prompts de S1 quanto descrevendo o contexto de uma OAE — "viaduto sobre a rodovia")
 * recebem peso reduzido, para que na hora do desempate por score o termo mais específico
 * do segmento "correto" prevaleça. Isso é ajuste de heurística do classificador, não
 * alteração da lista de keywords do CLAUDE.md (nenhum termo é adicionado/removido).
 */
interface WeightedKeyword {
  term: string;
  weight: number;
}

function kw(term: string, weight = 1): WeightedKeyword {
  return { term, weight };
}

interface RoutingRule {
  /** identificador do segmento/regra, ex: "saneamento", "S1" */
  segmentId: string;
  /** agente-alvo primário quando esta regra "ganha" */
  agentId: string;
  label: string;
  /**
   * Ordem de prioridade tal como declarada no CLAUDE.md (menor = avaliado primeiro).
   * Usada apenas como critério de desempate quando duas regras têm score E occurrences idênticos.
   */
  priority: number;
  keywords: WeightedKeyword[];
}

// Ordem replicada 1:1 do bloco `IF menção a ...` do CLAUDE.md v4.2.
const ROUTING_RULES: RoutingRule[] = [
  {
    segmentId: "saneamento",
    agentId: "agente-saneamento",
    label: "Saneamento (S8)",
    priority: 1,
    keywords: [kw("saneamento"), kw("ETA"), kw("ETE"), kw("adutora"), kw("esgoto"), kw("AySA"), kw("drenagem urbana"), kw("SNIS")],
  },
  {
    segmentId: "energia",
    agentId: "agente-energia",
    label: "Energia / Transmissão (S9)",
    priority: 2,
    keywords: [kw("transmissão"), kw("LT"), kw("subestação"), kw("ANEEL"), kw("RAP"), kw("leilão transmissão"), kw("ONS"), kw("EPE")],
  },
  {
    segmentId: "portos",
    agentId: "agente-portos",
    label: "Portos (S6)",
    priority: 3,
    keywords: [kw("porto"), kw("terminal"), kw("ANTAQ"), kw("dragagem"), kw("molhe"), kw("berço"), kw("calado"), kw("contêiner"), kw("granel")],
  },
  {
    segmentId: "aeroportos",
    agentId: "agente-aeroportos",
    label: "Aeroportos (S7)",
    priority: 4,
    keywords: [kw("aeroporto"), kw("pista pouso"), kw("ANAC"), kw("ICAO"), kw("TPS"), kw("TECA"), kw("balizamento")],
  },
  {
    segmentId: "barragens",
    agentId: "agente-barragens",
    label: "Barragens (S10)",
    priority: 5,
    keywords: [kw("barragem"), kw("vertedouro"), kw("CFRD"), kw("CCR"), kw("rejeitos"), kw("PNSB"), kw("ICOLD"), kw("CBDB"), kw("TSF")],
  },
  // Regras S1-S4 "mantidas sem alteração"
  {
    segmentId: "S1",
    agentId: "agente-infraestrutura-s1",
    label: "Rodovias (S1)",
    priority: 6,
    // "rodovia" é genérico (aparece também descrevendo o contexto de OAEs) → peso reduzido.
    keywords: [kw("rodovia", 0.6), kw("pavimento"), kw("CBUQ"), kw("BGS"), kw("terraplenagem"), kw("SICRO"), kw("DNIT")],
  },
  {
    segmentId: "S2",
    agentId: "agente-infraestrutura-s2",
    label: "OAE — pontes/viadutos (S2)",
    priority: 7,
    keywords: [kw("ponte"), kw("viaduto"), kw("OAE"), kw("NBR 7187"), kw("túnel rodoviário")],
  },
  {
    segmentId: "S3",
    agentId: "agente-infraestrutura-s3",
    label: "Ferrovia (S3)",
    priority: 8,
    keywords: [kw("ferrovia"), kw("trilho"), kw("AMV"), kw("dormente"), kw("via permanente")],
  },
  {
    segmentId: "S4",
    agentId: "agente-infraestrutura-s4",
    label: "Metrô (S4)",
    priority: 9,
    // "estação" é genérico (ferrovia, saneamento, etc.) → peso reduzido.
    keywords: [kw("metrô"), kw("estação", 0.6), kw("NATM"), kw("PSD"), kw("linha 4"), kw("linha 5"), kw("VLT")],
  },
];

/**
 * Política de resolução para pares ambíguos conhecidos, extraída de
 * tests/routing/prompts.md → "Casos ambíguos / desafiadores".
 * A chave é a combinação ordenada `"<segA>|<segB>"` das duas melhores pontuações.
 */
interface AmbiguityPolicy {
  primarySegment: string;
  handoffSegment: string;
  handoffRole: "handoff" | "consulta";
  note: string;
  requiresHumanReview: boolean;
}

function pairKey(a: string, b: string): string {
  return [a, b].sort().join("|");
}

const AMBIGUITY_POLICIES: Map<string, AmbiguityPolicy> = new Map([
  [
    pairKey("barragens", "energia"),
    {
      primarySegment: "barragens",
      handoffSegment: "energia",
      handoffRole: "handoff",
      note:
        "UHE com barragem CFRD + LT: política MN não definida em CLAUDE.md — " +
        "primário = barragens (maior massa técnica de risco), handoff explícito a energia. " +
        "Ver tests/routing/prompts.md. Requer confirmação humana.",
      requiresHumanReview: true,
    },
  ],
  [
    pairKey("saneamento", "energia"),
    {
      primarySegment: "saneamento",
      handoffSegment: "energia",
      handoffRole: "handoff",
      note: "ETE nova + subestação no mesmo canteiro: saneamento primário, handoff energia.",
      requiresHumanReview: false,
    },
  ],
  [
    pairKey("portos", "aeroportos"),
    {
      primarySegment: "portos",
      handoffSegment: "aeroportos",
      handoffRole: "handoff",
      note: "Porto com pátio + pista de carga aérea auxiliar: portos primário, handoff aeroportos.",
      requiresHumanReview: false,
    },
  ],
  [
    pairKey("saneamento", "barragens"),
    {
      primarySegment: "saneamento",
      handoffSegment: "barragens",
      handoffRole: "consulta",
      note: "Adutora atravessa barragem de rejeitos existente: saneamento primário, consulta técnica a barragens.",
      requiresHumanReview: false,
    },
  ],
]);

// ============================================================================================
// 4. NORMALIZAÇÃO E MATCHING DE KEYWORDS
// ============================================================================================

function normalize(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "") // remove acentos/diacriticos (marcas de combinacao NFD)
    .toLowerCase();
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

interface CompiledKeyword {
  original: string;
  weight: number;
  regex: RegExp;
}

function compileKeywords(keywords: WeightedKeyword[]): CompiledKeyword[] {
  return keywords.map(({ term, weight }) => ({
    original: term,
    weight,
    regex: new RegExp(`\\b${escapeRegExp(normalize(term))}\\b`, "g"),
  }));
}

const COMPILED_RULES: Array<RoutingRule & { compiled: CompiledKeyword[] }> = ROUTING_RULES.map(
  (rule) => ({ ...rule, compiled: compileKeywords(rule.keywords) }),
);

// ============================================================================================
// 5. CLASSIFICAÇÃO AUTOMÁTICA
// ============================================================================================

export interface SegmentScore {
  segmentId: string;
  agentId: string;
  label: string;
  priority: number;
  /** soma dos pesos das keywords distintas casadas — critério primário de ranking */
  score: number;
  matchedKeywords: string[];
  /** total de ocorrências (contando repetições) — usado como critério de desempate */
  occurrences: number;
}

export interface ClassificationResult {
  input: string;
  scores: SegmentScore[]; // ordenado desc: score, occurrences, priority asc
  top: SegmentScore | null;
  runnerUp: SegmentScore | null;
  isAmbiguous: boolean;
  /** heurística simples 0..1 — não é probabilidade calibrada, apenas sinal de confiança */
  confidence: number;
}

/** Diferença máxima de score entre 1º e 2º colocado para considerar a classificação ambígua. */
const AMBIGUITY_SCORE_GAP = 1;

export class Classifier {
  classify(rawInput: string): ClassificationResult {
    const normalized = normalize(rawInput);

    const scores: SegmentScore[] = COMPILED_RULES.map((rule) => {
      const matched: string[] = [];
      let occurrences = 0;
      let score = 0;
      for (const kw of rule.compiled) {
        const hits = normalized.match(kw.regex);
        if (hits && hits.length > 0) {
          matched.push(kw.original);
          occurrences += hits.length;
          score += kw.weight;
        }
      }
      return {
        segmentId: rule.segmentId,
        agentId: rule.agentId,
        label: rule.label,
        priority: rule.priority,
        score,
        matchedKeywords: matched,
        occurrences,
      };
    })
      .filter((s) => s.matchedKeywords.length > 0)
      .sort((a, b) => {
        if (b.score !== a.score) {
          return b.score - a.score;
        }
        if (b.occurrences !== a.occurrences) {
          return b.occurrences - a.occurrences;
        }
        return a.priority - b.priority; // menor priority = mais específico/prioritário no CLAUDE.md
      });

    const top = scores[0] ?? null;
    const runnerUp = scores[1] ?? null;

    const isAmbiguous = !!top && !!runnerUp && top.score - runnerUp.score <= AMBIGUITY_SCORE_GAP;

    let confidence = 0;
    if (top) {
      confidence = Math.min(1, top.score / 3);
      if (isAmbiguous) confidence = Math.min(confidence, 0.5);
    }

    return { input: rawInput, scores, top, runnerUp, isAmbiguous, confidence };
  }
}

// ============================================================================================
// 6. SELEÇÃO DE AGENTES
// ============================================================================================

export interface RouterContext {
  /** Q2 do intake — fase do ciclo de vida (Eixo 3) */
  lifecyclePhase?: LifecyclePhase;
  /** sinaliza contexto de alta complexidade/criticidade → favorece escalonamento a Opus */
  complexity?: "baixa" | "media" | "alta";
  /** força revisão humana mesmo quando a política não exigiria (ex: cliente sensível) */
  forceHumanReview?: boolean;
}

export type SelectionRole = "primary" | "handoff" | "consulta" | "clarify";

export interface AgentSelection {
  role: SelectionRole;
  agent: AgentDefinition;
  tier: ModelTier;
  reason: string;
}

export interface SelectionResult {
  selections: AgentSelection[];
  requiresHumanReview: boolean;
  classification: ClassificationResult;
}

/** Fases que, por padrão, empurram agentes de tier flexível para Opus. */
const HIGH_STAKES_PHASES = new Set<LifecyclePhase>([
  LifecyclePhase.DUE_DILIGENCE_MA,
  LifecyclePhase.ENCERRAMENTO_DESCOMISSIONAMENTO,
]);

export class AgentSelector {
  constructor(private readonly classifier: Classifier = new Classifier()) {}

  select(rawInput: string, context: RouterContext = {}): SelectionResult {
    const classification = this.classifier.classify(rawInput);

    if (!classification.top) {
      // Nenhum segmento identificado: Maestro pede esclarecimento (Q1 do intake) em vez de
      // adivinhar. Tier Haiku é suficiente para uma pergunta de clarificação.
      return {
        classification,
        requiresHumanReview: false,
        selections: [
          {
            role: "clarify",
            agent: MAESTRO_AGENT,
            tier: ModelTier.HAIKU,
            reason:
              "Nenhuma palavra-chave de segmento reconhecida — solicitar esclarecimento (Q1 do intake) antes de rotear.",
          },
        ],
      };
    }

    const { top, runnerUp, isAmbiguous } = classification;
    let requiresHumanReview = !!context.forceHumanReview;
    const selections: AgentSelection[] = [];

    let primarySegment = top.segmentId;
    let secondary: { segmentId: string; role: "handoff" | "consulta"; note: string } | null = null;

    if (isAmbiguous && runnerUp) {
      const policy = AMBIGUITY_POLICIES.get(pairKey(top.segmentId, runnerUp.segmentId));
      if (policy) {
        primarySegment = policy.primarySegment;
        secondary = {
          segmentId: policy.handoffSegment,
          role: policy.handoffRole,
          note: policy.note,
        };
        requiresHumanReview = requiresHumanReview || policy.requiresHumanReview;
      } else {
        // Ambiguidade sem política MN registrada: seguir o maior score, mas sinalizar
        // consulta ao 2º colocado e recomendar revisão humana (regra de cautela).
        secondary = {
          segmentId: runnerUp.segmentId,
          role: "consulta",
          note:
            `Ambiguidade entre "${top.label}" e "${runnerUp.label}" sem política MN registrada ` +
            `— seguindo maior score, mas recomenda-se validação humana.`,
        };
        requiresHumanReview = true;
      }
    }

    const primaryRule = ROUTING_RULES.find((r) => r.segmentId === primarySegment);
    if (!primaryRule) {
      throw new Error(`[MaestroRouterV2] regra de routing não encontrada para "${primarySegment}"`);
    }
    const primaryAgent = getAgent(primaryRule.agentId);
    selections.push({
      role: "primary",
      agent: primaryAgent,
      tier: this.resolveTier(primaryAgent, context, requiresHumanReview),
      reason: `Maior pontuação de classificação (${top.matchedKeywords.length} keyword(s): ${top.matchedKeywords.join(", ")}).`,
    });

    if (secondary) {
      const secondaryRule = ROUTING_RULES.find((r) => r.segmentId === secondary!.segmentId);
      if (secondaryRule) {
        const secondaryAgent = getAgent(secondaryRule.agentId);
        selections.push({
          role: secondary.role,
          agent: secondaryAgent,
          tier: this.resolveTier(secondaryAgent, context, requiresHumanReview),
          reason: secondary.note,
        });
      }
    }

    return { classification, selections, requiresHumanReview };
  }

  private resolveTier(
    agent: AgentDefinition,
    context: RouterContext,
    requiresHumanReview: boolean,
  ): ModelTier {
    if (agent.tiers.length === 1) return agent.tiers[0];
    const escalate =
      context.complexity === "alta" ||
      requiresHumanReview ||
      (context.lifecyclePhase !== undefined && HIGH_STAKES_PHASES.has(context.lifecyclePhase));
    return escalate ? agent.tiers[agent.tiers.length - 1] : agent.tiers[0];
  }
}

// ============================================================================================
// 7. ORQUESTRAÇÃO
// ============================================================================================

export type StepKind = "classify" | "escalate_review" | "dispatch" | "synthesize" | "human_gate";

export interface OrchestrationStep {
  id: string;
  kind: StepKind;
  agentId: string;
  tier: ModelTier;
  /** grupo de execução — steps do mesmo grupo correm em paralelo; grupos correm em sequência */
  group: number;
  role: SelectionRole | "maestro";
  promptExcerpt: string;
  dependsOn: string[];
}

export interface OrchestrationPlan {
  input: string;
  classification: ClassificationResult;
  selectionResult: SelectionResult;
  steps: OrchestrationStep[];
}

export interface StepResult {
  stepId: string;
  agentId: string;
  tier: ModelTier;
  output: string;
}

export interface OrchestrationResult {
  plan: OrchestrationPlan;
  transcript: StepResult[];
  finalOutput: string;
  requiresHumanReview: boolean;
}

/**
 * Callback de execução real de um step. Em produção, isto chama a API da Anthropic
 * (Claude) com o `tier` mapeado para um model id, ou dispara um subagente do Claude Code.
 * A assinatura é intencionalmente mínima para não acoplar este módulo a nenhum SDK.
 */
export type AgentExecutor = (step: OrchestrationStep, context: RouterContext) => Promise<string>;

/** Executor mock — determinístico, sem I/O. Útil para testes e demonstração. */
export const mockExecutor: AgentExecutor = async (step) => {
  return `[MOCK ${step.agentId}/${step.tier}] (${step.role}) resposta simulada para: "${step.promptExcerpt}"`;
};

export class Orchestrator {
  constructor(private readonly selector: AgentSelector = new AgentSelector()) {}

  buildPlan(rawInput: string, context: RouterContext = {}): OrchestrationPlan {
    const selectionResult = this.selector.select(rawInput, context);
    const { classification, selections, requiresHumanReview } = selectionResult;
    const excerpt = rawInput.length > 160 ? `${rawInput.slice(0, 160)}…` : rawInput;

    const steps: OrchestrationStep[] = [];
    let group = 0;

    // Step 0 — classificação (sempre roda; tier Haiku, conforme tiering do Manta 00).
    steps.push({
      id: "classify",
      kind: "classify",
      agentId: MAESTRO_AGENT.id,
      tier: ModelTier.HAIKU,
      group: group,
      role: "maestro",
      promptExcerpt: excerpt,
      dependsOn: [],
    });

    // Caso a classificação seja ambígua/sem match, o Maestro escala para Sonnet antes de
    // decidir (reflete o tiering "Haiku→Sonnet" declarado no CLAUDE.md para Manta 00).
    const needsEscalation = classification.isAmbiguous || !classification.top;
    if (needsEscalation) {
      group += 1;
      steps.push({
        id: "escalate_review",
        kind: "escalate_review",
        agentId: MAESTRO_AGENT.id,
        tier: ModelTier.SONNET,
        group,
        role: "maestro",
        promptExcerpt: classification.top
          ? `Desambiguar entre "${classification.top.label}" e "${classification.runnerUp?.label}".`
          : "Sem segmento identificado — preparar pergunta de esclarecimento (Q1).",
        dependsOn: ["classify"],
      });
    }

    // Dispatch — se houve "clarify", isto é a única ação (pergunta ao usuário).
    group += 1;
    const dispatchIds: string[] = [];
    for (const sel of selections) {
      const stepId = `dispatch:${sel.agent.id}:${sel.role}`;
      dispatchIds.push(stepId);
      steps.push({
        id: stepId,
        kind: sel.role === "clarify" ? "human_gate" : "dispatch",
        agentId: sel.agent.id,
        tier: sel.tier,
        group,
        role: sel.role,
        promptExcerpt: excerpt,
        dependsOn: needsEscalation ? ["escalate_review"] : ["classify"],
      });
    }

    // Síntese final — só faz sentido quando houve dispatch real (não em "clarify").
    const hadRealDispatch = selections.some((s) => s.role !== "clarify");
    if (hadRealDispatch) {
      group += 1;
      steps.push({
        id: "synthesize",
        kind: "synthesize",
        agentId: MAESTRO_AGENT.id,
        tier: ModelTier.SONNET,
        group,
        role: "maestro",
        promptExcerpt: "Consolidar respostas dos agentes despachados em uma única resposta ao usuário.",
        dependsOn: dispatchIds,
      });
    }

    // Gate humano explícito quando a política de ambiguidade (ou o contexto) exigir.
    if (requiresHumanReview && hadRealDispatch) {
      group += 1;
      steps.push({
        id: "human_gate",
        kind: "human_gate",
        agentId: MAESTRO_AGENT.id,
        tier: ModelTier.SONNET,
        group,
        role: "maestro",
        promptExcerpt: "Caso ambíguo/sensível — aguardar validação humana (MN) antes de finalizar.",
        dependsOn: ["synthesize"],
      });
    }

    return { input: rawInput, classification, selectionResult, steps };
  }

  async execute(
    plan: OrchestrationPlan,
    executor: AgentExecutor = mockExecutor,
    context: RouterContext = {},
  ): Promise<OrchestrationResult> {
    const byGroup = new Map<number, OrchestrationStep[]>();
    for (const step of plan.steps) {
      const bucket = byGroup.get(step.group) ?? [];
      bucket.push(step);
      byGroup.set(step.group, bucket);
    }

    const transcript: StepResult[] = [];
    const groups = [...byGroup.keys()].sort((a, b) => a - b);

    for (const g of groups) {
      const stepsInGroup = byGroup.get(g)!;
      const results = await Promise.all(
        stepsInGroup.map(async (step) => {
          const output = await executor(step, context);
          return { stepId: step.id, agentId: step.agentId, tier: step.tier, output };
        }),
      );
      transcript.push(...results);
    }

    const synthStep = transcript.find((r) => r.stepId === "synthesize");
    const clarifyStep = transcript.find((r) => r.stepId.startsWith("dispatch:") && r.stepId.endsWith(":clarify"));
    const finalOutput = synthStep?.output ?? clarifyStep?.output ?? transcript[transcript.length - 1]?.output ?? "";

    return {
      plan,
      transcript,
      finalOutput,
      requiresHumanReview: plan.selectionResult.requiresHumanReview,
    };
  }
}

// ============================================================================================
// 8. FAÇADE — MaestroRouterV2
// ============================================================================================

export class MaestroRouterV2 {
  private readonly classifier = new Classifier();
  private readonly selector = new AgentSelector(this.classifier);
  private readonly orchestrator = new Orchestrator(this.selector);

  /** Etapa 1 — apenas classificação automática. */
  classify(input: string): ClassificationResult {
    return this.classifier.classify(input);
  }

  /** Etapa 1+2 — classificação + seleção de agente(s). */
  select(input: string, context: RouterContext = {}): SelectionResult {
    return this.selector.select(input, context);
  }

  /** Etapa 1+2+3 — monta o plano de orquestração sem executar nada. */
  plan(input: string, context: RouterContext = {}): OrchestrationPlan {
    return this.orchestrator.buildPlan(input, context);
  }

  /**
   * Pipeline completo: classifica, seleciona, monta o plano e executa via `executor`
   * (por padrão, `mockExecutor` — injete um executor real ligado à API da Anthropic
   * ou a subagentes do Claude Code para uso em produção).
   */
  async run(
    input: string,
    context: RouterContext = {},
    executor: AgentExecutor = mockExecutor,
  ): Promise<OrchestrationResult> {
    const plan = this.orchestrator.buildPlan(input, context);
    return this.orchestrator.execute(plan, executor, context);
  }

  /** Trace legível em texto — útil para QA manual (ver DEPLOY-v4.2.md, item "Testes de routing"). */
  explain(input: string, context: RouterContext = {}): string {
    const selection = this.select(input, context);
    const lines: string[] = [];
    lines.push(`Input: "${input}"`);
    lines.push(
      `Classificação: ${
        selection.classification.scores
          .map((s) => `${s.label} (${s.matchedKeywords.length} kw: ${s.matchedKeywords.join("/")})`)
          .join(" | ") || "sem match"
      }`,
    );
    lines.push(`Ambíguo: ${selection.classification.isAmbiguous ? "sim" : "não"} | Confiança: ${selection.classification.confidence.toFixed(2)}`);
    for (const sel of selection.selections) {
      lines.push(`  → [${sel.role}] ${sel.agent.name} (${sel.agent.code}) tier=${sel.tier} — ${sel.reason}`);
    }
    lines.push(`Revisão humana necessária: ${selection.requiresHumanReview ? "sim" : "não"}`);
    return lines.join("\n");
  }
}

// ============================================================================================
// 9. AUTOTESTE — valida contra amostra de tests/routing/prompts.md
// ============================================================================================

interface SelfTestCase {
  prompt: string;
  expectedAgentId: string;
}

// Subconjunto representativo de tests/routing/prompts.md (S6-S10 + não-regressão S1-S4).
const SELF_TEST_CASES: SelfTestCase[] = [
  { prompt: "Preciso de um preliminar de dragagem para o terminal de contêineres do Porto do Itaqui.", expectedAgentId: "agente-portos" },
  { prompt: "Como dimensiono a defensa de um berço para navio Panamax?", expectedAgentId: "agente-portos" },
  { prompt: "Quero dimensionar a pista de pouso do aeroporto regional (código 3C).", expectedAgentId: "agente-aeroportos" },
  { prompt: "Como projeto o balizamento CAT II para operação noturna?", expectedAgentId: "agente-aeroportos" },
  { prompt: "Preciso projetar uma ETA de ciclo completo para 200 mil hab.", expectedAgentId: "agente-saneamento" },
  { prompt: "AySA me pediu um estudo de reabilitação da Planta Norte.", expectedAgentId: "agente-saneamento" },
  { prompt: "Preciso da RAP referencial para uma LT de 500kV, 250km.", expectedAgentId: "agente-energia" },
  { prompt: "ONS pede um estudo de fluxo — pode revisar minha modelagem?", expectedAgentId: "agente-energia" },
  { prompt: "Preciso projetar uma barragem CFRD de 80m de altura.", expectedAgentId: "agente-barragens" },
  { prompt: "Qual bulletin ICOLD cobre rejeitos filtrados (dry stack)?", expectedAgentId: "agente-barragens" },
  { prompt: "Preciso do orçamento SICRO para pavimento CBUQ 5cm.", expectedAgentId: "agente-infraestrutura-s1" },
  { prompt: "Como projeto uma viga PRP para viaduto sobre a rodovia?", expectedAgentId: "agente-infraestrutura-s2" },
  { prompt: "Qual AMV recomenda para pátio ferroviário?", expectedAgentId: "agente-infraestrutura-s3" },
  { prompt: "Vou escavar uma estação de metrô pelo método NATM.", expectedAgentId: "agente-infraestrutura-s4" },
];

export interface SelfTestSummary {
  total: number;
  passed: number;
  failed: number;
  details: Array<{ prompt: string; expected: string; got: string | null; pass: boolean }>;
}

/**
 * Roda o roteador contra a amostra de tests/routing/prompts.md e reporta divergências.
 * Não é um framework de teste (sem assert/exit code) — devolve um resumo estruturado
 * para uso em scripts de QA (ex: `scripts/test_routing.py` mencionado no runbook).
 */
export function runSelfTest(router: MaestroRouterV2 = new MaestroRouterV2()): SelfTestSummary {
  const details = SELF_TEST_CASES.map(({ prompt, expectedAgentId }) => {
    const { selections } = router.select(prompt);
    const primary = selections.find((s) => s.role === "primary");
    const got = primary?.agent.id ?? null;
    return { prompt, expected: expectedAgentId, got, pass: got === expectedAgentId };
  });
  const passed = details.filter((d) => d.pass).length;
  return { total: details.length, passed, failed: details.length - passed, details };
}

// ============================================================================================
// 10. DEMO — execução completa de ponta a ponta com o executor mock
// ============================================================================================

export async function demo(): Promise<void> {
  const router = new MaestroRouterV2();

  console.log("=== Manta Maestro v2 — autoteste de routing ===");
  const summary = runSelfTest(router);
  for (const d of summary.details) {
    const mark = d.pass ? "OK " : "FAIL";
    console.log(`[${mark}] esperado=${d.expected} obtido=${d.got ?? "(nenhum)"} :: "${d.prompt}"`);
  }
  console.log(`\nResultado: ${summary.passed}/${summary.total} aprovados.\n`);

  console.log("=== Exemplo de caso ambíguo (política MN aplicada) ===");
  const ambiguousPrompt = "A concessionária pediu uma ETE nova + subestação de 138kV no mesmo canteiro.";
  console.log(router.explain(ambiguousPrompt));

  console.log("\n=== Exemplo de orquestração completa (mock executor) ===");
  const result = await router.run(ambiguousPrompt, { lifecyclePhase: LifecyclePhase.PROJETO_BASICO });
  for (const step of result.transcript) {
    console.log(`  [${step.stepId}] (${step.agentId}/${step.tier}) → ${step.output}`);
  }
  console.log(`\nRevisão humana necessária: ${result.requiresHumanReview ? "sim" : "não"}`);
  console.log(`Resposta final consolidada: ${result.finalOutput}`);
}
