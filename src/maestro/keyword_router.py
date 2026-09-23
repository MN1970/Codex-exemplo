"""
Router de referência do Maestro (Manta 00) — determinístico, por palavra-chave.

Implementa como código executável as regras da seção ROUTING do CLAUDE.md
master, para que os testes E2E validem uma implementação real (antes, cada
arquivo de teste trazia seu próprio mock inline).

Regras:
  - Casamento por PALAVRA INTEIRA (fronteira de palavra), sem acento e sem
    diferenciar maiúsculas; plural simples ("trilhos" casa "trilho").
    Isso elimina o misroteamento por substring ("porto" dentro de
    "aeroporto", "LT" dentro de "filtrados", "ETA" dentro de "projetar").
  - Pontuação: 1 ponto por palavra-chave distinta no prompt; dicas de
    contexto (context_hints) somam 1 ponto cada, ou 2 quando a dica é o
    termo de domínio do agente (ex.: "saneamento", "porto").
  - Empate: vertical vence horizontal (o segmento decide o dispatch
    primário — CLAUDE.md, "Modelo de composição S.A.D"); persistindo o
    empate, vence o agente citado primeiro no prompt.
  - Numeração de segmentos: a do SharePoint canônico (decisão D2 de MN,
    2026-09-22) — S6 Edificações, S7 Portos, S8 Aeroportos, S9 Saneamento,
    S10 Energia, S11 Barragens, S12 Túneis, S13 Mineração, S14 Óleo e Gás.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def normalize(text: str) -> str:
    """Minúsculas, sem acento, hífen/sublinhado viram espaço."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[-_]+", " ", text.lower())


def _pattern(keyword: str) -> re.Pattern:
    kw = re.escape(normalize(keyword)).replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![a-z0-9]){kw}(?:e?s)?(?![a-z0-9])")


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    slug: str
    domain: tuple
    keywords: tuple
    vertical: bool
    default_tier: str = "sonnet-5"
    rag_collection: Optional[str] = None


AGENTS: List[AgentSpec] = [
    # ---- Verticais (Manta 03-Sx) ----------------------------------------
    AgentSpec("manta-03-s1", "agente-infraestrutura", ("rodovia",),
              ("rodovia", "pavimento", "pavimentacao", "CBUQ", "BGS", "terraplenagem",
               "SICRO", "DNIT", "DER", "asfalto", "asfaltica", "acostamento"),
              True, rag_collection="rod:v5.0:*"),
    AgentSpec("manta-03-s2", "agente-infraestrutura", ("ponte", "OAE", "viaduto"),
              ("ponte", "viaduto", "OAE", "NBR 7187", "fundacao", "pilares", "longarina",
               "aparelho de apoio", "junta de dilatacao", "estaca", "protendido"),
              True, rag_collection="oae:v5.0:*"),
    AgentSpec("manta-03-s3", "agente-infraestrutura", ("ferrovia",),
              ("ferrovia", "ferroviario", "trilho", "AMV", "dormente", "via permanente",
               "bitola", "lastro", "pantografo", "catenaria"),
              True, rag_collection="fer:v5.0:*"),
    AgentSpec("manta-03-s4", "agente-infraestrutura", ("metro",),
              ("metro", "metroviario", "estacao de metro", "NATM", "PSD", "VLT",
               "linha 4", "linha 5", "linha 6", "trem urbano", "elevado"),
              True, rag_collection="mtr:v5.0:*"),
    AgentSpec("manta-03-s6", "agente-edificacoes", ("edificacao",),
              ("edificacao", "edificio", "torre residencial", "galpao", "warehouse",
               "data center", "MCMV", "NBR 15575", "LEED"),
              True, rag_collection="edi:v5.0:*"),
    AgentSpec("manta-03-s7", "agente-portos", ("porto",),
              ("porto", "portuario", "terminal", "ANTAQ", "dragagem", "molhe",
               "quebra mar", "berco", "calado", "conteiner", "TEU", "granel", "cais",
               "pier", "retroarea", "TUP", "PIANC", "hidrovia"),
              True, rag_collection="por:v5.0:*"),
    AgentSpec("manta-03-s8", "agente-aeroportos", ("aeroporto",),
              ("aeroporto", "aeroportuario", "pista de pouso", "pista", "RWY", "taxiway",
               "TWY", "TPS", "TECA", "ANAC", "RBAC", "ICAO", "balizamento", "PAPI",
               "ILS", "PCN", "ponte de embarque", "passageiros"),
              True, rag_collection="aer:v5.0:*"),
    AgentSpec("manta-03-s9", "agente-saneamento", ("saneamento",),
              ("saneamento", "ETA", "ETE", "adutora", "esgoto", "agua", "AySA",
               "drenagem urbana", "SNIS", "PMSB", "Lei 14.026", "elevatoria", "UASB",
               "MBR", "reuso", "Sabesp"),
              True, rag_collection="san:v5.0:*"),
    AgentSpec("manta-03-s10", "agente-energia", ("energia",),
              ("energia", "transmissao", "LT", "linha de transmissao", "subestacao",
               "ANEEL", "RAP", "leilao de transmissao", "ONS", "EPE", "usina", "UHE",
               "PCH", "eolica", "solar", "fotovoltaica", "ACSR", "ampacidade",
               "hidreletrica", "MW", "MVA", "kV"),
              True, rag_collection="ene:v5.0:*"),
    AgentSpec("manta-03-s11", "agente-barragens", ("barragem",),
              ("barragem", "vertedouro", "CFRD", "CCR", "RCC", "rejeitos", "TSF",
               "PNSB", "ICOLD", "CBDB", "dique", "SIGBM", "Lei 12.334", "dry stack",
               "dam break", "dam breach", "Brumadinho", "PAEBM", "alteamento"),
              True, rag_collection="bar:v5.0:*"),
    AgentSpec("manta-03-s12", "agente-tuneis", ("tunel",),
              ("tunel", "TBM", "EPB", "cut and cover", "dovela", "emboque"),
              True, rag_collection="tun:v5.0:*"),
    AgentSpec("manta-03-s13", "agente-mineracao", ("mineracao",),
              ("mineracao", "mina", "minerio", "ANM", "NR 22", "JORC", "lavra"),
              True, rag_collection="min:v5.0:*"),
    AgentSpec("manta-03-s14", "agente-oleo-gas", ("oleo e gas",),
              ("oleo e gas", "petroleo", "gasoduto", "oleoduto", "dutovia", "duto", "refinaria",
               "ANP", "API 650", "HAZOP", "tancagem"),
              True, rag_collection="og:v5.0:*"),
    # ---- Horizontais -----------------------------------------------------
    AgentSpec("manta-01", "agente-claims", ("claims",),
              ("claims", "claim", "indenizacao", "sinistro", "pleito", "prejuizo",
               "reequilibrio"), False, default_tier="opus"),
    AgentSpec("manta-02", "agente-contratual", ("contrato",),
              ("contrato", "contratual", "contratacao", "legal", "clausula", "forca maior",
               "aditivo", "rescisao", "jurisdicao"), False),
    AgentSpec("manta-04", "agente-imobiliario", ("imobiliario",),
              ("imobiliario", "imobiliaria", "terreno", "avaliacao", "zoneamento",
               "desapropriacao", "faixa de dominio"), False),
    AgentSpec("manta-05", "agente-orcamento", ("orcamento",),
              ("orcamento", "custo", "estimativa", "BDI", "SINAPI", "preco",
               "composicao de custo"), False),
    AgentSpec("manta-06", "agente-modelagem", ("modelagem",),
              ("modelagem", "modelo financeiro", "modelo", "financeiro", "PPP",
               "viabilidade", "VPL", "TIR", "fluxo de caixa"), False, default_tier="opus"),
    AgentSpec("manta-07", "agente-cronograma", ("cronograma",),
              ("cronograma", "planejamento", "gantt", "caminho critico", "recursos",
               "frentes", "marcos"), False),
    AgentSpec("manta-13", "agente-bd", ("bd",),
              ("bd", "negocio", "oportunidade", "mercado", "comercial", "pipeline",
               "parceria"), False),
    AgentSpec("manta-14", "agente-apresentacoes", ("apresentacao",),
              ("apresentacao", "pptx", "slides", "deck", "executiva", "pitch"), False),
    AgentSpec("manta-15", "agente-advisory", ("advisory",),
              ("advisory", "parecer", "tecnico", "segunda opiniao", "go no go"), False),
    AgentSpec("manta-16", "agente-arquiteto-ia", ("arquitetura",),
              ("arquitetura", "IA", "design", "agente", "workflow", "MCP", "RAG"),
              False, default_tier="opus"),
    # Co-agente ESG (CLAUDE.md, ROUTING): só vira primário quando nenhum
    # vertical pontua mais — nos demais casos entra como handoff.
    AgentSpec("manta-20", "manta-20-esg", ("esg",),
              ("ESG", "carbono", "GHG", "escopo 1", "escopo 2", "escopo 3", "TCFD",
               "SASB", "GRI", "net zero", "biodiversidade", "licenca social",
               "social license", "consulta previa", "inventario de emissoes"), False),
]

BY_ID: Dict[str, AgentSpec] = {a.agent_id: a for a in AGENTS}
FALLBACK_AGENT = "manta-00"

_KW_PATTERNS = {a.agent_id: [(k, _pattern(k)) for k in a.keywords] for a in AGENTS}
_DOMAIN = {a.agent_id: {normalize(d) for d in a.domain} for a in AGENTS}
_KW_NORM = {a.agent_id: {normalize(k) for k in a.keywords} for a in AGENTS}

# Handoffs permitidos (primário → secundários), na ordem de prioridade.
CROSS_AGENT_RULES: Dict[str, List[str]] = {
    "manta-03-s9": ["manta-05", "manta-02", "manta-15"],   # Saneamento
    "manta-03-s7": ["manta-05", "manta-07"],               # Portos
    "manta-03-s10": ["manta-06", "manta-05"],              # Energia
    "manta-03-s11": ["manta-02", "manta-01",               # Barragens
                     "manta-03-s10", "manta-03-s14"],      # UHE → energia; duto → O&G
    "manta-03-s4": ["manta-03-s2", "manta-07", "manta-03-s9", "manta-03-s1"],  # Metrô
    "manta-03-s1": ["manta-03-s3", "manta-03-s10"],        # Rodovias
    "manta-03-s2": ["manta-07"],                           # OAE
    "manta-03-s8": ["manta-03-s1", "manta-05"],            # Aeroportos
}

# Casos ambíguos com política definida no CLAUDE.md ("ROUTING", casos
# ambíguos): quando os dois agentes pontuam e a palavra-gatilho aparece, o
# primário é fixo — independente de quem somou mais palavras-chave.
AMBIGUITY_RULES = [
    # UHE (barragem + LT + SE) → barragens primário, handoff energia
    ({"manta-03-s11", "manta-03-s10"}, ("UHE", "hidreletrica"), "manta-03-s11"),
    # Adutora atravessa barragem → saneamento, consulta técnica a barragens
    ({"manta-03-s9", "manta-03-s11"}, ("adutora",), "manta-03-s9"),
]
_AMBIGUITY_PATTERNS = [(agents, [_pattern(t) for t in triggers], primary)
                       for agents, triggers, primary in AMBIGUITY_RULES]


def _apply_ambiguity_rules(scores: Dict[str, float], prompt: str) -> Optional[str]:
    norm = normalize(prompt)
    for agents, patterns, primary in _AMBIGUITY_PATTERNS:
        if agents <= scores.keys() and any(p.search(norm) for p in patterns):
            return primary
    return None


# Palavras que acionam um handoff (além das palavras-chave do agente).
_HANDOFF_EXTRA = {
    "manta-03-s2": ("estrutural", "estrutura"),
    "manta-03-s1": ("via de acesso", "vias de acesso"),
}

_PHASES = [
    ("licitacao", ("licitacao", "edital", "concorrencia", "processo competitivo", "leilao")),
    ("due-diligence", ("due diligence", "M&A")),
    ("encerramento", ("encerramento", "descomissionamento", "descaracterizacao")),
    ("operacao", ("operacao", "manutencao", "O&M", "OPEX")),
    ("obra", ("obra em execucao", "execucao da obra", "construcao", "implantacao")),
    ("projeto-executivo", ("projeto executivo", "detalhamento")),
    ("projeto-basico", ("projeto basico", "anteprojeto")),
    ("estudo-previo", ("estudo previo", "EVTE", "EVTEA", "diagnostico")),
]
_PHASE_PATTERNS = [(ph, [_pattern(k) for k in kws]) for ph, kws in _PHASES]


@dataclass
class RoutingResult:
    agent_id: str
    skill_id: str
    model_tier: str
    complexity_score: float
    routing_confidence: float
    phase: Optional[str] = None
    rag_collection: Optional[str] = None
    rag_reranker_score: Optional[float] = None
    fallback_agent: Optional[str] = FALLBACK_AGENT
    context_injection: Optional[Dict] = None
    scores: Dict[str, float] = field(default_factory=dict)
    slug: Optional[str] = None


def keyword_hits(agent_id: str, text: str) -> List[str]:
    norm = normalize(text)
    return [k for k, p in _KW_PATTERNS[agent_id] if p.search(norm)]


def first_hit_position(agent_id: str, text: str) -> int:
    norm = normalize(text)
    positions = [m.start() for _, p in _KW_PATTERNS[agent_id] for m in [p.search(norm)] if m]
    return min(positions) if positions else len(norm)


def score_agents(prompt: str, context_hints: Optional[List[str]] = None) -> Dict[str, float]:
    hints = [normalize(h) for h in (context_hints or [])]
    scores: Dict[str, float] = {}
    for spec in AGENTS:
        s = float(len(keyword_hits(spec.agent_id, prompt)))
        for h in hints:
            if h in _DOMAIN[spec.agent_id]:
                s += 2.0
            elif h in _KW_NORM[spec.agent_id]:
                s += 1.0
        if s > 0:
            scores[spec.agent_id] = s
    return scores


def infer_phase(prompt: str, context_hints: Optional[List[str]] = None,
                complexity_score: Optional[float] = None) -> str:
    text = normalize(" ".join([prompt] + list(context_hints or [])))
    for phase, patterns in _PHASE_PATTERNS:
        if any(p.search(text) for p in patterns):
            return phase
    # Sem pista textual: trabalho de alta complexidade tende a ser executivo.
    if complexity_score is not None and complexity_score >= 4.0:
        return "projeto-executivo"
    return "projeto-basico"


def compute_tier(agent_id: str, complexity_score: float, prompt_len: int) -> str:
    spec = BY_ID.get(agent_id)
    if spec and spec.default_tier == "opus":
        return "opus"
    if complexity_score < 3.0 and prompt_len < 1500:
        return "haiku-4-5"
    if complexity_score > 4.5 or prompt_len > 3000:
        return "opus"
    return "sonnet-5"


def route(prompt: str, context_hints: Optional[List[str]] = None,
          complexity_score: Optional[float] = None) -> RoutingResult:
    scores = score_agents(prompt, context_hints)
    if scores:
        ranked = sorted(scores.items(),
                        key=lambda kv: (-kv[1], not BY_ID[kv[0]].vertical,
                                        first_hit_position(kv[0], prompt)))
        best, top = ranked[0]
        forced = _apply_ambiguity_rules(scores, prompt)
        if forced:
            best, top = forced, scores[forced]
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        confidence = min(0.95, 0.56 + 0.08 * top + 0.04 * (top - second))
    else:
        best, top, confidence = FALLBACK_AGENT, 0.0, 0.5

    if complexity_score is None:
        complexity_score = float(len(context_hints or []))
    phase = infer_phase(prompt, context_hints, complexity_score)
    spec = BY_ID.get(best)
    rag = spec.rag_collection if spec else None
    return RoutingResult(
        agent_id=best,
        skill_id=f"{best.replace('manta-', '').replace('-', '_')}.v5.0",
        model_tier=compute_tier(best, complexity_score, len(prompt)),
        complexity_score=complexity_score,
        routing_confidence=round(confidence, 4),
        phase=phase,
        rag_collection=rag,
        rag_reranker_score=None,
        context_injection={"phase": phase, "file_processing": False, "rag_collection": rag},
        scores=scores,
        slug=spec.slug if spec else None,
    )


def cross_agent_calls(primary: str, prompt: str) -> List[str]:
    """Secundários acionados a partir do primário, conforme CROSS_AGENT_RULES."""
    norm = normalize(prompt)
    calls = []
    for called in CROSS_AGENT_RULES.get(primary, []):
        extra = any(_pattern(w).search(norm) for w in _HANDOFF_EXTRA.get(called, ()))
        if keyword_hits(called, prompt) or extra:
            calls.append(called)
    # Primário horizontal (ex.: orçamento de uma ETE): o vertical citado entra
    # como handoff de contexto, para o segmento não se perder (teste E1, T5).
    spec = BY_ID.get(primary)
    if spec and not spec.vertical:
        for a in AGENTS:
            if a.vertical and a.agent_id not in calls and keyword_hits(a.agent_id, prompt):
                calls.append(a.agent_id)
    return calls
