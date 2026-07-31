/**
 * Maestro Router — Motor de roteamento determinístico para Manta Agentes
 * Versão: 4.2
 * Algoritmo: Keyword Matching + Scoring Ponderado
 * Fórmula: base_weight + context_bonus + category_bonus
 */

/**
 * Tipos e interfaces do roteador
 */
export interface AgentRoute {
  code: string;
  name: string;
  segment?: string;
  tier: string;
  aliases: string[];
}

export interface KeywordConfig {
  keyword: string;
  weight: number;
  category: "primary" | "secondary" | "context" | "regulatory";
}

export interface SegmentConfig {
  segment: string;
  agent: AgentRoute;
  keywords: KeywordConfig[];
  contextBonus: number;
}

export interface RoutingResult {
  agent: AgentRoute;
  matchedKeywords: string[];
  score: number;
  confidence: "high" | "medium" | "low";
}

export interface RouterStats {
  inputLength: number;
  matchCount: number;
  topScores: Map<string, number>;
  executionTimeMs: number;
}

/**
 * Configuração mestre de agentes e keywords
 */
const AGENT_ROUTES: Record<string, AgentRoute> = {
  "agente-saneamento": {
    code: "Manta 03-S8",
    name: "agente-saneamento",
    segment: "Saneamento",
    tier: "Sonnet",
    aliases: ["s8", "saneamento", "ete", "eta"],
  },
  "agente-energia": {
    code: "Manta 03-S9",
    name: "agente-energia",
    segment: "Energia",
    tier: "Sonnet",
    aliases: ["s9", "energia", "aneel"],
  },
  "agente-portos": {
    code: "Manta 03-S6",
    name: "agente-portos",
    segment: "Portos",
    tier: "Sonnet",
    aliases: ["s6", "portos", "antaq"],
  },
  "agente-aeroportos": {
    code: "Manta 03-S7",
    name: "agente-aeroportos",
    segment: "Aeroportos",
    tier: "Sonnet",
    aliases: ["s7", "aeroportos", "anac"],
  },
  "agente-barragens": {
    code: "Manta 03-S10",
    name: "agente-barragens",
    segment: "Barragens",
    tier: "Sonnet",
    aliases: ["s10", "barragens", "icold"],
  },
  "agente-infraestrutura-s1": {
    code: "Manta 03-S1",
    name: "agente-infraestrutura",
    segment: "Rodovias",
    tier: "Sonnet",
    aliases: ["s1", "rodovia", "dnit"],
  },
  "agente-infraestrutura-s2": {
    code: "Manta 03-S2",
    name: "agente-infraestrutura",
    segment: "OAE (Pontes/Viadutos)",
    tier: "Sonnet",
    aliases: ["s2", "ponte", "viaduto"],
  },
  "agente-infraestrutura-s3": {
    code: "Manta 03-S3",
    name: "agente-infraestrutura",
    segment: "Ferrovia",
    tier: "Sonnet",
    aliases: ["s3", "ferrovia"],
  },
  "agente-infraestrutura-s4": {
    code: "Manta 03-S4",
    name: "agente-infraestrutura",
    segment: "Metrô",
    tier: "Sonnet",
    aliases: ["s4", "metrô", "metro"],
  },
};

/**
 * Configuração de segmentos com keywords ponderadas
 */
const SEGMENT_CONFIGS: SegmentConfig[] = [
  {
    segment: "Saneamento",
    agent: AGENT_ROUTES["agente-saneamento"],
    contextBonus: 2.0,
    keywords: [
      // Primary keywords (base_weight = 3.0)
      { keyword: "saneamento", weight: 3.0, category: "primary" },
      { keyword: "saneamento ambiental", weight: 3.2, category: "primary" },
      { keyword: "etação", weight: 3.0, category: "primary" }, // ETA (tratamento água)
      { keyword: "eta", weight: 3.0, category: "primary" },
      { keyword: "estaçãotatória", weight: 3.0, category: "primary" }, // ETE (tratamento esgoto)
      { keyword: "ete", weight: 3.0, category: "primary" },
      { keyword: "adutora", weight: 3.0, category: "primary" },
      { keyword: "esgoto", weight: 3.0, category: "primary" },
      { keyword: "esgotos", weight: 3.0, category: "primary" },
      { keyword: "drenagem urbana", weight: 3.0, category: "primary" },
      { keyword: "drenagem", weight: 2.8, category: "primary" },
      // Secondary keywords
      { keyword: "aysa", weight: 2.9, category: "secondary" }, // Operadora argentina
      { keyword: "ayvsa", weight: 2.9, category: "secondary" },
      { keyword: "agua potable", weight: 2.8, category: "secondary" },
      { keyword: "água", weight: 2.5, category: "secondary" },
      { keyword: "rcd", weight: 2.7, category: "secondary" }, // Rede de coleta
      { keyword: "rede distribuição", weight: 2.7, category: "secondary" },
      { keyword: "reservatorio", weight: 2.6, category: "secondary" },
      { keyword: "reservatório", weight: 2.6, category: "secondary" },
      // Regulatory/standards
      { keyword: "snis", weight: 2.8, category: "regulatory" },
      { keyword: "nbr 12211", weight: 2.9, category: "regulatory" },
      { keyword: "nbr 12212", weight: 2.9, category: "regulatory" },
      { keyword: "nbr 12213", weight: 2.9, category: "regulatory" },
      { keyword: "lei 14.026", weight: 2.8, category: "regulatory" },
      { keyword: "abnt", weight: 2.0, category: "regulatory" },
      // Context keywords
      { keyword: "operação", weight: 1.5, category: "context" },
      { keyword: "manutenção", weight: 1.5, category: "context" },
    ],
  },
  {
    segment: "Energia",
    agent: AGENT_ROUTES["agente-energia"],
    contextBonus: 2.0,
    keywords: [
      // Primary
      { keyword: "energia", weight: 3.0, category: "primary" },
      { keyword: "transmissão", weight: 3.1, category: "primary" },
      { keyword: "transmision", weight: 3.1, category: "primary" },
      { keyword: "lt", weight: 3.0, category: "primary" }, // Linha transmissão
      { keyword: "linhadetrasmissão", weight: 3.1, category: "primary" },
      { keyword: "subestação", weight: 3.0, category: "primary" },
      { keyword: "subestacion", weight: 3.0, category: "primary" },
      { keyword: "rap", weight: 2.9, category: "primary" }, // Receita acesso ponto
      { keyword: "leilão transmissão", weight: 3.1, category: "primary" },
      { keyword: "ons", weight: 2.9, category: "primary" }, // Operador nacional
      { keyword: "epe", weight: 2.8, category: "primary" }, // Empresa planejamento
      { keyword: "aneel", weight: 2.9, category: "regulatory" },
      // Secondary
      { keyword: "distribuição", weight: 2.7, category: "secondary" },
      { keyword: "geração", weight: 2.6, category: "secondary" },
      { keyword: "usina", weight: 2.5, category: "secondary" },
      { keyword: "hidrelétrica", weight: 2.6, category: "secondary" },
      { keyword: "termélétrica", weight: 2.6, category: "secondary" },
      { keyword: "solar", weight: 2.4, category: "secondary" },
      { keyword: "eólica", weight: 2.4, category: "secondary" },
      { keyword: "transformador", weight: 2.4, category: "secondary" },
      // Regulatory
      { keyword: "ieee", weight: 2.5, category: "regulatory" },
      { keyword: "iec", weight: 2.5, category: "regulatory" },
      { keyword: "nbr iec", weight: 2.6, category: "regulatory" },
      { keyword: "resolução aneel", weight: 2.8, category: "regulatory" },
      // Context
      { keyword: "projeto", weight: 1.2, category: "context" },
    ],
  },
  {
    segment: "Portos",
    agent: AGENT_ROUTES["agente-portos"],
    contextBonus: 2.0,
    keywords: [
      // Primary
      { keyword: "porto", weight: 3.0, category: "primary" },
      { keyword: "portos", weight: 3.0, category: "primary" },
      { keyword: "terminal", weight: 2.8, category: "primary" },
      { keyword: "antaq", weight: 2.9, category: "primary" },
      { keyword: "dragagem", weight: 3.0, category: "primary" },
      { keyword: "molhe", weight: 3.0, category: "primary" },
      { keyword: "berço", weight: 3.0, category: "primary" },
      { keyword: "calado", weight: 3.0, category: "primary" },
      { keyword: "contêiner", weight: 2.9, category: "primary" },
      { keyword: "contenedor", weight: 2.9, category: "primary" },
      { keyword: "granel", weight: 2.9, category: "primary" },
      { keyword: "cais", weight: 2.8, category: "primary" },
      { keyword: "pier", weight: 2.7, category: "primary" },
      // Secondary
      { keyword: "navio", weight: 2.5, category: "secondary" },
      { keyword: "embarcação", weight: 2.4, category: "secondary" },
      { keyword: "carga", weight: 2.2, category: "secondary" },
      { keyword: "desembarque", weight: 2.3, category: "secondary" },
      { keyword: "embarque", weight: 2.3, category: "secondary" },
      { keyword: "estuário", weight: 2.2, category: "secondary" },
      // Regulatory
      { keyword: "pianc", weight: 2.8, category: "regulatory" },
      { keyword: "iala", weight: 2.7, category: "regulatory" },
      { keyword: "imca", weight: 2.7, category: "regulatory" },
      { keyword: "solas", weight: 2.6, category: "regulatory" },
    ],
  },
  {
    segment: "Aeroportos",
    agent: AGENT_ROUTES["agente-aeroportos"],
    contextBonus: 2.0,
    keywords: [
      // Primary
      { keyword: "aeroporto", weight: 3.0, category: "primary" },
      { keyword: "aeropuerto", weight: 3.0, category: "primary" },
      { keyword: "pista", weight: 2.9, category: "primary" },
      { keyword: "pista pouso", weight: 3.1, category: "primary" },
      { keyword: "anac", weight: 2.9, category: "primary" },
      { keyword: "icao", weight: 2.9, category: "primary" },
      { keyword: "tps", weight: 2.9, category: "primary" }, // Terminal passageiros
      { keyword: "teca", weight: 2.9, category: "primary" }, // Terminal carga
      { keyword: "balizamento", weight: 3.0, category: "primary" },
      { keyword: "navegação aérea", weight: 2.9, category: "primary" },
      { keyword: "iluminação pista", weight: 2.8, category: "primary" },
      // Secondary
      { keyword: "avião", weight: 2.5, category: "secondary" },
      { keyword: "aeronave", weight: 2.5, category: "secondary" },
      { keyword: "decolagem", weight: 2.4, category: "secondary" },
      { keyword: "pouso", weight: 2.4, category: "secondary" },
      { keyword: "taxiway", weight: 2.6, category: "secondary" },
      { keyword: "apron", weight: 2.6, category: "secondary" },
      { keyword: "pátio", weight: 2.3, category: "secondary" },
      // Regulatory
      { keyword: "faa", weight: 2.7, category: "regulatory" },
      { keyword: "rbac", weight: 2.8, category: "regulatory" },
      { keyword: "annex 14", weight: 2.8, category: "regulatory" },
      { keyword: "ac", weight: 1.5, category: "regulatory" }, // Advisory circular
    ],
  },
  {
    segment: "Barragens",
    agent: AGENT_ROUTES["agente-barragens"],
    contextBonus: 2.0,
    keywords: [
      // Primary
      { keyword: "barragem", weight: 3.0, category: "primary" },
      { keyword: "presa", weight: 3.0, category: "primary" },
      { keyword: "dique", weight: 2.9, category: "primary" },
      { keyword: "vertedouro", weight: 3.0, category: "primary" },
      { keyword: "spillway", weight: 2.8, category: "primary" },
      { keyword: "cfrd", weight: 3.0, category: "primary" }, // Concreto face rockfill
      { keyword: "ccr", weight: 3.0, category: "primary" }, // Concreto compactado
      { keyword: "rejeitos", weight: 2.9, category: "primary" },
      { keyword: "relaves", weight: 2.9, category: "primary" },
      { keyword: "fundação", weight: 2.5, category: "primary" },
      // Secondary
      { keyword: "hidrelétrica", weight: 2.5, category: "secondary" },
      { keyword: "açude", weight: 2.7, category: "secondary" },
      { keyword: "reservatório", weight: 2.6, category: "secondary" },
      { keyword: "ensecadeira", weight: 2.8, category: "secondary" },
      { keyword: "escavação", weight: 2.0, category: "secondary" },
      // Regulatory
      { keyword: "icold", weight: 2.9, category: "regulatory" },
      { keyword: "cbdb", weight: 2.9, category: "regulatory" },
      { keyword: "sigbm", weight: 2.8, category: "regulatory" },
      { keyword: "lei 12.334", weight: 2.8, category: "regulatory" },
      { keyword: "pnsb", weight: 2.8, category: "regulatory" },
      { keyword: "tsf", weight: 2.8, category: "regulatory" },
    ],
  },
  {
    segment: "Rodovias",
    agent: AGENT_ROUTES["agente-infraestrutura-s1"],
    contextBonus: 1.8,
    keywords: [
      // Primary
      { keyword: "rodovia", weight: 3.0, category: "primary" },
      { keyword: "via", weight: 2.3, category: "primary" },
      { keyword: "estrada", weight: 2.7, category: "primary" },
      { keyword: "pavimento", weight: 3.0, category: "primary" },
      { keyword: "pavimentação", weight: 3.0, category: "primary" },
      { keyword: "cbuq", weight: 3.0, category: "primary" },
      { keyword: "bgs", weight: 3.0, category: "primary" },
      { keyword: "terraplenagem", weight: 3.0, category: "primary" },
      { keyword: "sicro", weight: 2.9, category: "primary" },
      { keyword: "dnit", weight: 2.9, category: "primary" },
      // Secondary
      { keyword: "asfalto", weight: 2.6, category: "secondary" },
      { keyword: "concreto", weight: 2.1, category: "secondary" },
      { keyword: "base", weight: 1.8, category: "secondary" },
      { keyword: "sub-base", weight: 2.4, category: "secondary" },
      { keyword: "subleito", weight: 2.6, category: "secondary" },
      { keyword: "drenagem", weight: 2.0, category: "secondary" },
      // Regulatory
      { keyword: "nbr", weight: 2.0, category: "regulatory" },
      { keyword: "manual dnit", weight: 2.8, category: "regulatory" },
      { keyword: "especificação técnica", weight: 2.2, category: "regulatory" },
    ],
  },
  {
    segment: "OAE (Pontes/Viadutos)",
    agent: AGENT_ROUTES["agente-infraestrutura-s2"],
    contextBonus: 1.8,
    keywords: [
      // Primary
      { keyword: "ponte", weight: 3.0, category: "primary" },
      { keyword: "viaduto", weight: 3.0, category: "primary" },
      { keyword: "oae", weight: 3.0, category: "primary" },
      { keyword: "obra de arte", weight: 2.9, category: "primary" },
      { keyword: "túnel rodoviário", weight: 3.0, category: "primary" },
      { keyword: "túnel", weight: 2.9, category: "primary" },
      { keyword: "passarela", weight: 2.8, category: "primary" },
      // Secondary
      { keyword: "vão", weight: 2.5, category: "secondary" },
      { keyword: "tabuleiro", weight: 2.8, category: "secondary" },
      { keyword: "pilar", weight: 2.6, category: "secondary" },
      { keyword: "encontro", weight: 2.5, category: "secondary" },
      { keyword: "estrutura", weight: 2.0, category: "secondary" },
      // Regulatory
      { keyword: "nbr 7187", weight: 2.9, category: "regulatory" },
      { keyword: "nbr 7188", weight: 2.9, category: "regulatory" },
      { keyword: "nbr 8681", weight: 2.8, category: "regulatory" },
    ],
  },
  {
    segment: "Ferrovia",
    agent: AGENT_ROUTES["agente-infraestrutura-s3"],
    contextBonus: 1.8,
    keywords: [
      // Primary
      { keyword: "ferrovia", weight: 3.0, category: "primary" },
      { keyword: "trilho", weight: 3.0, category: "primary" },
      { keyword: "via permanente", weight: 3.0, category: "primary" },
      { keyword: "amv", weight: 2.9, category: "primary" },
      { keyword: "dormente", weight: 3.0, category: "primary" },
      { keyword: "lastro", weight: 2.8, category: "primary" },
      // Secondary
      { keyword: "vagão", weight: 2.5, category: "secondary" },
      { keyword: "locomotiva", weight: 2.5, category: "secondary" },
      { keyword: "material rodante", weight: 2.7, category: "secondary" },
      { keyword: "estação", weight: 2.2, category: "secondary" },
      { keyword: "pátio ferroviário", weight: 2.6, category: "secondary" },
    ],
  },
  {
    segment: "Metrô",
    agent: AGENT_ROUTES["agente-infraestrutura-s4"],
    contextBonus: 1.8,
    keywords: [
      // Primary
      { keyword: "metrô", weight: 3.0, category: "primary" },
      { keyword: "metro", weight: 3.0, category: "primary" },
      { keyword: "vlt", weight: 2.9, category: "primary" },
      { keyword: "estação", weight: 2.8, category: "primary" },
      { keyword: "natm", weight: 2.9, category: "primary" },
      { keyword: "psd", weight: 2.9, category: "primary" },
      { keyword: "linha 4", weight: 2.9, category: "primary" },
      { keyword: "linha 5", weight: 2.9, category: "primary" },
      { keyword: "linha 6", weight: 2.9, category: "primary" },
      // Secondary
      { keyword: "trilho", weight: 2.4, category: "secondary" },
      { keyword: "via", weight: 2.0, category: "secondary" },
      { keyword: "túnel", weight: 2.3, category: "secondary" },
      { keyword: "escavação subterrânea", weight: 2.8, category: "secondary" },
      { keyword: "escudo", weight: 2.7, category: "secondary" },
    ],
  },
];

/**
 * Classe principal do roteador
 */
export class MaestroRouter {
  private segmentConfigs: SegmentConfig[];
  private allKeywordsLower: Map<string, SegmentConfig[]> = new Map();

  constructor() {
    this.segmentConfigs = SEGMENT_CONFIGS;
    this.buildKeywordIndex();
  }

  /**
   * Constrói índice invertido de keywords para busca rápida
   */
  private buildKeywordIndex(): void {
    this.allKeywordsLower.clear();

    for (const config of this.segmentConfigs) {
      for (const kw of config.keywords) {
        const keyLower = kw.keyword.toLowerCase();
        if (!this.allKeywordsLower.has(keyLower)) {
          this.allKeywordsLower.set(keyLower, []);
        }
        this.allKeywordsLower.get(keyLower)!.push(config);
      }
    }
  }

  /**
   * Calcula score final com fórmula: base_weight + context_bonus + category_bonus
   */
  private calculateScore(
    keywordConfig: KeywordConfig,
    segmentConfig: SegmentConfig,
    inputLength: number
  ): number {
    const baseWeight = keywordConfig.weight;

    // Category bonus (ajusta importância por tipo)
    const categoryBonus = this.getCategoryBonus(keywordConfig.category);

    // Context bonus baseado no tamanho do input
    // Inputs mais longos e específicos recebem bonus
    const contextBonus =
      inputLength > 50 ? segmentConfig.contextBonus * 1.2 : segmentConfig.contextBonus * 0.9;

    return baseWeight + contextBonus + categoryBonus;
  }

  /**
   * Retorna bonus por categoria de keyword
   */
  private getCategoryBonus(category: KeywordConfig["category"]): number {
    const bonusMap: Record<KeywordConfig["category"], number> = {
      primary: 0.5,
      secondary: 0.2,
      context: 0.1,
      regulatory: 0.3,
    };
    return bonusMap[category];
  }

  /**
   * Extrai tokens do input e remove stopwords
   */
  private tokenize(input: string): string[] {
    const stopwords = new Set([
      "o",
      "a",
      "os",
      "as",
      "um",
      "uma",
      "uns",
      "umas",
      "de",
      "do",
      "da",
      "dos",
      "das",
      "para",
      "por",
      "em",
      "no",
      "na",
      "nos",
      "nas",
      "é",
      "são",
      "e",
      "ou",
      "que",
      "com",
      "se",
      "seu",
      "sua",
      "este",
      "esse",
      "the",
      "a",
      "an",
      "and",
      "or",
      "is",
      "are",
      "be",
      "been",
      "being",
      "have",
      "has",
      "had",
      "do",
      "does",
      "did",
      "will",
      "would",
      "could",
      "should",
      "may",
      "might",
      "must",
      "can",
      "this",
      "that",
      "these",
      "those",
      "i",
      "you",
      "he",
      "she",
      "it",
      "we",
      "they",
      "what",
      "which",
      "who",
      "when",
      "where",
      "why",
      "how",
    ]);

    return input
      .toLowerCase()
      .split(/[\s\-,;:.!?()\/\[\]{}]+/)
      .filter((token) => token.length > 0 && !stopwords.has(token));
  }

  /**
   * Realiza matching de keywords com suporte a variações
   */
  private findMatches(
    input: string
  ): Map<SegmentConfig, { keywords: string[]; scores: number[] }> {
    const matches = new Map<SegmentConfig, { keywords: string[]; scores: number[] }>();
    const inputLower = input.toLowerCase();
    const tokens = this.tokenize(input);

    // Match exato de keywords compostas
    for (const [keywordLower, segments] of this.allKeywordsLower) {
      if (inputLower.includes(keywordLower)) {
        for (const segment of segments) {
          const keywordConfig = segment.keywords.find((k) => k.keyword.toLowerCase() === keywordLower);
          if (!keywordConfig) continue;

          const score = this.calculateScore(keywordConfig, segment, input.length);

          if (!matches.has(segment)) {
            matches.set(segment, { keywords: [], scores: [] });
          }
          matches.get(segment)!.keywords.push(keywordLower);
          matches.get(segment)!.scores.push(score);
        }
      }
    }

    // Match por tokens individuais
    for (const token of tokens) {
      if (this.allKeywordsLower.has(token)) {
        const segments = this.allKeywordsLower.get(token)!;
        for (const segment of segments) {
          const keywordConfig = segment.keywords.find((k) => k.keyword.toLowerCase() === token);
          if (!keywordConfig) continue;

          // Reduz score para matches de token único
          const score = this.calculateScore(keywordConfig, segment, input.length) * 0.85;

          if (!matches.has(segment)) {
            matches.set(segment, { keywords: [], scores: [] });
          }
          matches.get(segment)!.keywords.push(token);
          matches.get(segment)!.scores.push(score);
        }
      }
    }

    return matches;
  }

  /**
   * Rota input para o melhor agente
   * Retorna resultado com score e confiança
   */
  public route(input: string): RoutingResult {
    const startTime = performance.now();

    if (!input || input.trim().length === 0) {
      throw new Error("Input vazio para roteamento");
    }

    const matches = this.findMatches(input);

    if (matches.size === 0) {
      const endTime = performance.now();
      return {
        agent: AGENT_ROUTES["agente-infraestrutura-s1"], // fallback padrão
        matchedKeywords: [],
        score: 0,
        confidence: "low",
      };
    }

    // Calcula score agregado por segmento
    let bestSegment: SegmentConfig | null = null;
    let bestScore = -Infinity;
    let bestKeywords: string[] = [];

    for (const [segment, data] of matches) {
      const aggregatedScore = data.scores.reduce((a, b) => a + b, 0);

      if (aggregatedScore > bestScore) {
        bestScore = aggregatedScore;
        bestSegment = segment;
        bestKeywords = [...new Set(data.keywords)]; // Remove duplicatas
      }
    }

    if (!bestSegment) {
      throw new Error("Nenhum segmento encontrado após matching");
    }

    // Determina nível de confiança baseado no score
    let confidence: "high" | "medium" | "low" = "low";
    if (bestScore >= 8.0) {
      confidence = "high";
    } else if (bestScore >= 4.0) {
      confidence = "medium";
    }

    const endTime = performance.now();

    return {
      agent: bestSegment.agent,
      matchedKeywords: bestKeywords,
      score: parseFloat(bestScore.toFixed(2)),
      confidence,
    };
  }

  /**
   * Rota e retorna estatísticas detalhadas (para debug/testes)
   */
  public routeWithStats(input: string): RoutingResult & RouterStats {
    const startTime = performance.now();

    const result = this.route(input);

    const matches = this.findMatches(input);
    const topScores = new Map<string, number>();

    for (const [segment, data] of matches) {
      const aggregatedScore = data.scores.reduce((a, b) => a + b, 0);
      topScores.set(segment.agent.name, aggregatedScore);
    }

    const endTime = performance.now();

    return {
      ...result,
      inputLength: input.length,
      matchCount: matches.size,
      topScores,
      executionTimeMs: parseFloat((endTime - startTime).toFixed(2)),
    };
  }

  /**
   * Retorna todos os agentes disponíveis
   */
  public getAvailableAgents(): AgentRoute[] {
    return Array.from(Object.values(AGENT_ROUTES));
  }

  /**
   * Retorna configuração de keywords para um segmento específico
   */
  public getSegmentConfig(segmentName: string): SegmentConfig | undefined {
    return this.segmentConfigs.find((s) => s.segment.toLowerCase() === segmentName.toLowerCase());
  }
}

/**
 * Factory para criação de instância singleton
 */
let routerInstance: MaestroRouter | null = null;

export function getMaestroRouter(): MaestroRouter {
  if (!routerInstance) {
    routerInstance = new MaestroRouter();
  }
  return routerInstance;
}

/**
 * Testes e exemplos de uso
 */
export async function runExamples(): Promise<void> {
  const router = getMaestroRouter();

  const testCases = [
    // Saneamento
    "Projeto de ETA e ETE para AySA na região metropolitana",
    "Adutora de saneamento seguindo SNIS",
    "ETE com drenagem urbana integrada",
    // Energia
    "Leilão de transmissão ANEEL com LT de 500kV",
    "Subestação RAP conforme ONS",
    "Geração eólica com transmissão",
    // Portos
    "Terminal de contêiner no porto com dragagem",
    "Berço para navio de grande calado conforme ANTAQ",
    // Aeroportos
    "Pista de pouso com balizamento ICAO",
    "Terminal de passageiros TPS",
    // Barragens
    "Barragem CFRD com vertedouro",
    "Rejeitos em TSF conforme ICOLD",
    // Rodovias
    "Pavimentação CBUQ e terraplenagem via SICRO",
    "Base BGS conforme DNIT",
    // OAE
    "Ponte com 200m de vão seguindo NBR 7187",
    "Viaduto em estrutura de concreto",
    // Ferrovia
    "Projeto de ferrovia com via permanente e trilho",
    "Dormente e AMV",
    // Metrô
    "Estação de metrô na Linha 4 com NATM",
    "Construção de túnel para VLT",
  ];

  console.log("=== MAESTRO ROUTER EXAMPLES ===\n");

  for (const testCase of testCases) {
    const result = router.routeWithStats(testCase);

    console.log(`📝 Input: "${testCase}"`);
    console.log(`✅ Agent: ${result.agent.name} (${result.agent.code})`);
    console.log(`📊 Score: ${result.score} | Confidence: ${result.confidence}`);
    console.log(`🔑 Keywords: ${result.matchedKeywords.join(", ")}`);
    console.log(`⏱️  Execution: ${result.executionTimeMs}ms`);
    console.log("---\n");
  }
}

/**
 * Teste determinístico específico: AySA → agente-saneamento
 */
export function testAySARouting(): void {
  const router = getMaestroRouter();

  const testInput = "AySA solicitou projeto de ETA e ETE com adutora";
  const result = router.routeWithStats(testInput);

  console.log("🧪 TESTE: AySA → agente-saneamento");
  console.log(`Input: "${testInput}"`);
  console.log(`Agente: ${result.agent.name}`);
  console.log(`Score: ${result.score}`);
  console.log(`Confiança: ${result.confidence}`);
  console.log(`Keywords: ${result.matchedKeywords.join(", ")}`);

  if (result.agent.name === "agente-saneamento" && result.confidence === "high") {
    console.log("✅ TESTE PASSOU");
  } else {
    console.log("❌ TESTE FALHOU");
  }
}
