#!/usr/bin/env python3
"""
fallback_strategy.py — Manta Maestro v4.2/v5 · Markov-chain agent fallback
============================================================================

Quando um agente vertical do Maestro (S1-S10) falha em responder uma
consulta (timeout, baixa confiança do RAG, fora de escopo, erro etc.),
este módulo decide **para qual agente tentar o fallback em seguida**,
usando uma cadeia de Markov de primeira ordem treinada sobre o
histórico de falhas/recuperações do roteador.

    P(agente_j | agente_i falhou)

Estados da cadeia
-----------------
- Os 10 agentes verticais (S1..S10) definidos em CLAUDE.md §Eixo 2.
- Dois estados absorventes "de escape":
    * "MAESTRO_REVIEW"   — devolve ao Manta 00 (maestro) para nova
                            triagem/roteamento manual;
    * "OPUS_ESCALATION"  — escala a mesma vertical, porém rodando em
                            tier Opus (mais caro, mais capaz), em vez
                            de trocar de segmento.

Sobre os dados de treino
------------------------
Este repositório (`Codex-exemplo`) é a referência canônica versionada
dos agentes — os logs operacionais de produção (6 meses de v4.2) vivem
no repositório operacional do Maestro, fora deste repo (ver CLAUDE.md,
seção "Arquivos deste repositório"). Como não há logs reais aqui, o
módulo:

  1. Sabe carregar logs reais assim que existirem, via `--logs arquivo
     .jsonl` (um `FallbackEvent` por linha — ver `FallbackEvent`
     abaixo), ou uma lista de dicts equivalente passada em código; e
  2. Inclui um gerador de logs sintéticos (`generate_synthetic_logs`)
     que reproduz um padrão de handoff plausível, alinhado com os
     pares de handoff documentados em `tests/routing/prompts.md`
     ("Casos ambíguos/desafiadores": S8↔S9, S8↔S10, S6↔S7), incluindo
     o cenário citado na especificação: S8 (saneamento) falhando numa
     consulta de ETA cai ~60% das vezes em S6 (portos), com o resto
     distribuído entre S10 (barragens, também "água/infra pesada") e
     escalonamento Opus.

Uso rápido
----------
    # treina (sintético, já que não há logs reais no repo) e persiste
    python scripts/fallback_strategy.py train --synthetic --save

    # inferência
    python scripts/fallback_strategy.py infer --failed-agent S8 \\
        --query "ETA da AySA com vazão baixa, preciso de fallback"

    # demo completa (treina + salva + roda os exemplos da spec)
    python scripts/fallback_strategy.py demo

Uso programático
----------------
    from fallback_strategy import findFallback, load_default_chain

    chain = load_default_chain()          # carrega estado persistido
                                           # (ou treina sintético se
                                           # não existir ainda)
    result = findFallback("S8", "vazão baixa na ETA, código SNIS?", chain)
    print(result.best_agent, result.best_probability)
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# 1. Registro de agentes e palavras-chave de routing
#    (espelha CLAUDE.md §ROUTING e o INSERT INTO maestro_routing_keywords
#    em supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql)
# ---------------------------------------------------------------------------

# Estados absorventes / "de escape" da cadeia — não são segmentos verticais,
# representam decisões de roteamento em vez de troca de segmento.
MAESTRO_REVIEW = "MAESTRO_REVIEW"
OPUS_ESCALATION = "OPUS_ESCALATION"
ABSORBING_STATES = (MAESTRO_REVIEW, OPUS_ESCALATION)

VERTICAL_AGENTS: List[str] = [
    "S1", "S2", "S3", "S4",  # túnel (S5) é coberto por S2/S4, sem estado próprio
    "S6", "S7", "S8", "S9", "S10",
]

AGENT_LABELS: Dict[str, str] = {
    "S1": "agente-infraestrutura (Rodovias)",
    "S2": "agente-infraestrutura (OAE)",
    "S3": "agente-infraestrutura (Ferrovia)",
    "S4": "agente-infraestrutura (Metrô)",
    "S6": "agente-portos",
    "S7": "agente-aeroportos",
    "S8": "agente-saneamento",
    "S9": "agente-energia",
    "S10": "agente-barragens",
    MAESTRO_REVIEW: "Manta 00 — devolve p/ triagem manual",
    OPUS_ESCALATION: "mesma vertical, tier Opus",
}

DEFAULT_TIER: Dict[str, str] = {
    "S1": "Sonnet", "S2": "Sonnet", "S3": "Sonnet", "S4": "Sonnet",
    "S6": "Sonnet", "S7": "Sonnet", "S8": "Sonnet", "S9": "Sonnet",
    "S10": "Sonnet",
}

# keyword -> priority (mesma escala 0-120 usada no INSERT da migração SQL).
# S1-S4 derivadas das regras do CLAUDE.md §ROUTING (sem prioridade explícita
# lá, então usamos 90 como default "documentado, mas não ranqueado").
AGENT_KEYWORDS: Dict[str, Dict[str, int]] = {
    "S1": {"rodovia": 90, "pavimento": 90, "cbuq": 90, "bgs": 90,
           "terraplenagem": 90, "sicro": 90, "dnit": 90},
    "S2": {"ponte": 90, "viaduto": 90, "oae": 90, "nbr 7187": 90,
           "túnel rodoviário": 90, "tunel rodoviario": 90},
    "S3": {"ferrovia": 90, "trilho": 90, "amv": 90, "dormente": 90,
           "via permanente": 90},
    "S4": {"metrô": 90, "metro": 90, "estação": 85, "estacao": 85,
           "natm": 90, "psd": 90, "linha 4": 90, "linha 5": 90, "vlt": 90},
    "S6": {"porto": 80, "terminal": 70, "antaq": 100, "dragagem": 100,
           "molhe": 100, "berço": 90, "berco": 90, "calado": 90,
           "contêiner": 80, "conteiner": 80, "granel": 80},
    "S7": {"aeroporto": 100, "pista pouso": 100, "anac": 100, "icao": 100,
           "tps": 90, "teca": 90, "balizamento": 100, "rbac": 95, "pcn": 90},
    "S8": {"saneamento": 100, "eta": 100, "ete": 100, "adutora": 100,
           "esgoto": 100, "aysa": 120, "drenagem urbana": 95, "snis": 100,
           "pmsb": 90, "golpe de ariete": 95, "golpe de aríete": 95,
           "lei 14.026": 95},
    "S9": {"transmissão": 100, "transmissao": 100, "lt": 90,
           "subestação": 100, "subestacao": 100, "aneel": 100, "rap": 90,
           "leilão transmissão": 95, "leilao transmissao": 95, "ons": 90,
           "epe": 90, "ampacidade": 90},
    "S10": {"barragem": 100, "vertedouro": 100, "cfrd": 100, "ccr": 80,
            "rejeitos": 110, "pnsb": 100, "icold": 100, "cbdb": 100,
            "tsf": 100, "dam breach": 95, "sigbm": 95},
}

_WORD_RE = re.compile(r"\w+(?:[- ]\w+)*", re.UNICODE)


def _normalize_text(text: str) -> str:
    return text.strip().lower()


def keyword_score(query: str, agent: str) -> float:
    """Score 0..1 de quão fortemente `query` casa com as keywords do `agent`.

    Soma as prioridades das keywords do agente que aparecem na query
    (substring match, case-insensitive), normalizada pela soma total de
    prioridades daquele agente — evita que agentes com listas de
    keywords maiores dominem artificialmente o score.
    """
    kws = AGENT_KEYWORDS.get(agent)
    if not kws:
        return 0.0
    text = _normalize_text(query)
    total = sum(kws.values())
    if total == 0:
        return 0.0
    hit = sum(weight for kw, weight in kws.items() if kw in text)
    return min(hit / total, 1.0)


def best_keyword_agent(query: str, candidates: Optional[Sequence[str]] = None) -> Optional[Tuple[str, float]]:
    """Retorna (agente, score) com melhor casamento de keywords para a query."""
    pool = candidates if candidates is not None else VERTICAL_AGENTS
    scored = [(a, keyword_score(query, a)) for a in pool]
    scored = [s for s in scored if s[1] > 0]
    if not scored:
        return None
    return max(scored, key=lambda s: s[1])


# ---------------------------------------------------------------------------
# 2. Estrutura de log (evento de falha + fallback)
# ---------------------------------------------------------------------------

FAILURE_REASONS = (
    "timeout",          # agente não respondeu a tempo
    "error",            # exceção / erro de execução
    "low_confidence",   # RAG retornou match fraco
    "no_rag_match",     # nenhuma coleção retornou chunk relevante
    "ambiguous_segment",  # query cruza >1 segmento (ver casos ambíguos)
    "out_of_scope",     # query fora do domínio do agente
)

# Razões "de conteúdo" — o contexto semântico da query importa para decidir
# o fallback. Razões de infraestrutura (timeout/error) não dizem nada sobre
# o assunto da query, então o histórico puro pesa mais nesses casos.
_CONTENT_REASONS = {"low_confidence", "no_rag_match", "ambiguous_segment", "out_of_scope"}


@dataclass
class FallbackEvent:
    """Um evento de falha+resolução extraído dos logs operacionais do Maestro."""

    timestamp: str            # ISO-8601
    query: str
    failed_agent: str         # estado de origem (S1..S10)
    failure_reason: str       # ver FAILURE_REASONS
    fallback_agent: str       # estado de destino (S1..S10, MAESTRO_REVIEW, OPUS_ESCALATION)
    resolved: bool            # o fallback resolveu a consulta?

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "FallbackEvent":
        return cls(
            timestamp=d["timestamp"],
            query=d["query"],
            failed_agent=d["failed_agent"],
            failure_reason=d.get("failure_reason", "no_rag_match"),
            fallback_agent=d["fallback_agent"],
            resolved=bool(d.get("resolved", True)),
        )


def load_logs_jsonl(path: str | Path) -> List[FallbackEvent]:
    """Carrega eventos de um arquivo JSONL real (um FallbackEvent por linha)."""
    events: List[FallbackEvent] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(FallbackEvent.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError) as exc:
                raise ValueError(f"{path}:{line_no}: log malformado — {exc}") from exc
    return events


# ---------------------------------------------------------------------------
# 3. Gerador de logs sintéticos (stand-in para os 6 meses de logs v4.2
#    reais, que vivem no repo operacional do Maestro e não estão
#    disponíveis aqui — ver docstring do módulo).
# ---------------------------------------------------------------------------

# Distribuição "verdadeira" oculta usada só para GERAR o dataset sintético.
# Não é lida pelo treino — o treino sempre reaprende isso a partir dos
# eventos amostrados, exatamente como faria sobre logs reais.
#
# Alinhada com os pares de handoff em tests/routing/prompts.md ("Casos
# ambíguos"): S8<->S9 (ETE+subestação), S6<->S7 (porto+pista de carga
# aérea), S8<->S10 (adutora atravessando barragem de rejeitos). O caso
# S8 -> S6 60% é o exemplo citado na especificação deste módulo.
_SYNTHETIC_GROUND_TRUTH: Dict[str, Dict[str, float]] = {
    "S1": {"S2": 0.30, MAESTRO_REVIEW: 0.45, OPUS_ESCALATION: 0.25},
    "S2": {"S1": 0.25, "S4": 0.10, MAESTRO_REVIEW: 0.40, OPUS_ESCALATION: 0.25},
    "S3": {"S1": 0.20, MAESTRO_REVIEW: 0.50, OPUS_ESCALATION: 0.30},
    "S4": {"S2": 0.20, MAESTRO_REVIEW: 0.45, OPUS_ESCALATION: 0.35},
    "S6": {"S7": 0.55, MAESTRO_REVIEW: 0.25, OPUS_ESCALATION: 0.20},
    "S7": {"S6": 0.50, MAESTRO_REVIEW: 0.30, OPUS_ESCALATION: 0.20},
    "S8": {"S6": 0.60, "S10": 0.25, OPUS_ESCALATION: 0.15},
    "S9": {"S8": 0.45, "S10": 0.20, MAESTRO_REVIEW: 0.20, OPUS_ESCALATION: 0.15},
    "S10": {"S8": 0.40, MAESTRO_REVIEW: 0.30, OPUS_ESCALATION: 0.30},
}

# Bag de queries de exemplo por segmento, extraídas/inspiradas em
# tests/routing/prompts.md, usadas para dar às queries sintéticas
# vocabulário realista.
_SAMPLE_QUERIES: Dict[str, List[str]] = {
    "S1": ["Preciso do orçamento SICRO para pavimento CBUQ 5cm.",
           "Terraplenagem com BGS, qual espessura recomenda?"],
    "S2": ["Como projeto uma viga PRP para viaduto sobre a rodovia?",
           "OAE com fundação em estaca hélice contínua, NBR 7187."],
    "S3": ["Qual AMV recomenda para pátio ferroviário?",
           "Dormente de concreto protendido, via permanente."],
    "S4": ["Vou escavar uma estação de metrô pelo método NATM.",
           "PSD da linha 5 precisa de qual gabarito?"],
    "S6": ["Preciso de um preliminar de dragagem para o terminal de contêineres.",
           "ANTAQ pede cronograma de arrendamento para o TUP."],
    "S7": ["Quero dimensionar a pista de pouso do aeroporto regional (código 3C).",
           "Como projeto o balizamento CAT II para operação noturna?"],
    "S8": ["Preciso projetar uma ETA de ciclo completo para 200 mil hab.",
           "AySA pediu estudo de reabilitação da Planta Norte, vazão baixa.",
           "Golpe de aríete na adutora de 800mm, código SNIS?"],
    "S9": ["Estamos avaliando um leilão de transmissão da ANEEL em 2027.",
           "Preciso da RAP referencial para uma LT de 500kV, 250km."],
    "S10": ["Preciso projetar uma barragem CFRD de 80m de altura.",
            "Qual bulletin ICOLD cobre rejeitos filtrados (dry stack)?"],
}


def generate_synthetic_logs(
    n_events: int = 1200,
    months: int = 6,
    seed: int = 42,
) -> List[FallbackEvent]:
    """Gera um dataset sintético de eventos de falha/fallback.

    Serve como stand-in para os logs reais de produção (que não estão
    neste repositório) para permitir treinar e demonstrar a cadeia de
    Markov ponta-a-ponta. A distribuição usada para amostrar (`_SYNTHETIC_
    GROUND_TRUTH`) é intencionalmente próxima do exemplo da especificação
    (S8 -> S6 ~60%), mas o treino em si (`MarkovFallbackChain.fit`) nunca
    lê essa distribuição diretamente — ele reaprende tudo a partir dos
    eventos amostrados, exatamente como faria com logs reais.
    """
    rng = random.Random(seed)
    end = datetime(2026, 7, 5, tzinfo=timezone.utc)  # data do release v4.2
    start = end - timedelta(days=30 * months)
    span_seconds = int((end - start).total_seconds())

    events: List[FallbackEvent] = []
    failed_agents = list(_SYNTHETIC_GROUND_TRUTH.keys())

    for _ in range(n_events):
        failed_agent = rng.choice(failed_agents)
        dist = _SYNTHETIC_GROUND_TRUTH[failed_agent]
        targets, weights = zip(*dist.items())
        fallback_agent = rng.choices(targets, weights=weights, k=1)[0]

        reason = rng.choice(FAILURE_REASONS)
        query = rng.choice(_SAMPLE_QUERIES.get(failed_agent, ["consulta genérica"]))

        # taxa de sucesso do fallback: um pouco maior quando o fallback é
        # para um segmento historicamente mais provável (proxy de "faz
        # sentido"), e menor para escalonamentos genéricos.
        base_success = 0.85 if fallback_agent not in ABSORBING_STATES else 0.7
        resolved = rng.random() < base_success

        ts = start + timedelta(seconds=rng.randint(0, span_seconds))
        events.append(FallbackEvent(
            timestamp=ts.isoformat(),
            query=query,
            failed_agent=failed_agent,
            failure_reason=reason,
            fallback_agent=fallback_agent,
            resolved=resolved,
        ))

    events.sort(key=lambda e: e.timestamp)
    return events


# ---------------------------------------------------------------------------
# 4. Cadeia de Markov de fallback
# ---------------------------------------------------------------------------

@dataclass
class FallbackCandidate:
    agent: str
    label: str
    probability: float          # P(agente | falha), pura frequência histórica
    keyword_score: float        # casamento léxico da query com o agente
    blended_score: float        # combinação usada para ranquear


@dataclass
class FallbackResult:
    failed_agent: str
    query: str
    candidates: List[FallbackCandidate]
    escalate: bool
    best_agent: Optional[str]
    best_probability: float
    rationale: str

    def as_dict(self) -> dict:
        d = asdict(self)
        return d


class MarkovFallbackChain:
    """Cadeia de Markov de 1ª ordem: P(agente_j | agente_i falhou).

    Os "estados" são os agentes verticais (S1..S10) mais dois estados
    absorventes (MAESTRO_REVIEW, OPUS_ESCALATION). As transições são
    aprendidas contando, para cada agente que falhou, para qual agente
    o Maestro tentou (e teve sucesso ou não) o fallback.
    """

    def __init__(self, smoothing: float = 0.5):
        # Laplace/add-k smoothing: evita prob. zero para pares nunca
        # observados e garante que a cadeia sempre tenha uma resposta,
        # mesmo com pouco histórico para um dado agente.
        self.smoothing = smoothing
        self.transition_counts: Dict[str, Counter] = defaultdict(Counter)
        self.event_counts: Dict[str, int] = defaultdict(int)   # p/ métricas
        self.resolved_counts: Dict[str, int] = defaultdict(int)
        self.states: set[str] = set(VERTICAL_AGENTS) | set(ABSORBING_STATES)
        self.trained_on: int = 0
        self.trained_at: Optional[str] = None

    # -- treino -----------------------------------------------------------

    def fit(self, events: Iterable[FallbackEvent]) -> "MarkovFallbackChain":
        """Constrói/atualiza a matriz de transição a partir de eventos de log.

        Eventos resolvidos (`resolved=True`) pesam 1.0; eventos não
        resolvidos pesam 0.3 — ainda contam como evidência de que o
        Maestro *tentou* aquele fallback, mas com menos confiança do
        que uma recuperação bem-sucedida.
        """
        n = 0
        for ev in events:
            self.states.add(ev.failed_agent)
            self.states.add(ev.fallback_agent)
            weight = 1.0 if ev.resolved else 0.3
            self.transition_counts[ev.failed_agent][ev.fallback_agent] += weight
            self.event_counts[ev.failed_agent] += 1
            if ev.resolved:
                self.resolved_counts[ev.failed_agent] += 1
            n += 1
        self.trained_on += n
        self.trained_at = datetime.now(timezone.utc).isoformat()
        return self

    # -- inspeção da matriz -------------------------------------------------

    def transition_probs(self, failed_agent: str) -> Dict[str, float]:
        """P(agente_j | failed_agent) com add-k smoothing sobre todos os estados."""
        counts = self.transition_counts.get(failed_agent, Counter())
        k = self.smoothing
        all_states = sorted(self.states - {failed_agent}) or sorted(ABSORBING_STATES)
        total = sum(counts.values()) + k * len(all_states)
        if total == 0:
            return {s: 1.0 / len(all_states) for s in all_states}
        return {s: (counts.get(s, 0.0) + k) / total for s in all_states}

    def success_rate(self, failed_agent: str) -> Optional[float]:
        n = self.event_counts.get(failed_agent, 0)
        if n == 0:
            return None
        return self.resolved_counts.get(failed_agent, 0) / n

    def top_fallbacks(self, failed_agent: str, k: int = 5) -> List[Tuple[str, float]]:
        probs = self.transition_probs(failed_agent)
        return sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[:k]

    # -- inferência ---------------------------------------------------------

    def find_fallback(
        self,
        failed_agent: str,
        query: str,
        top_k: int = 3,
        escalate_threshold: float = 0.20,
        failure_reason: Optional[str] = None,
    ) -> FallbackResult:
        """Decide o próximo agente a tentar, dado que `failed_agent` falhou.

        Combina a probabilidade histórica (Markov) com o casamento de
        keywords da query. Quando `failure_reason` é uma razão "de
        infraestrutura" (timeout/error), o histórico pesa quase
        totalmente (alpha alto) — o conteúdo da query não é o problema.
        Quando é uma razão "de conteúdo" (baixa confiança, sem match no
        RAG, segmento ambíguo, fora de escopo), o casamento léxico pesa
        mais, porque é justamente aí que o texto da query ajuda a
        decidir o destino certo.
        """
        alpha = 0.85 if failure_reason not in _CONTENT_REASONS else 0.6

        probs = self.transition_probs(failed_agent)
        candidates: List[FallbackCandidate] = []
        for agent, p in probs.items():
            kscore = keyword_score(query, agent) if agent in AGENT_KEYWORDS else 0.0
            blended = alpha * p + (1 - alpha) * kscore
            candidates.append(FallbackCandidate(
                agent=agent,
                label=AGENT_LABELS.get(agent, agent),
                probability=round(p, 4),
                keyword_score=round(kscore, 4),
                blended_score=round(blended, 4),
            ))

        candidates.sort(key=lambda c: c.blended_score, reverse=True)
        top = candidates[:top_k]

        best = top[0] if top else None
        escalate = best is None or best.blended_score < escalate_threshold or best.agent == OPUS_ESCALATION

        if best is None:
            rationale = ("Nenhum histórico disponível para este agente — "
                          "escalar para Opus e acionar revisão do Maestro.")
            best_agent, best_prob = OPUS_ESCALATION, 0.0
        elif escalate:
            best_agent, best_prob = OPUS_ESCALATION, best.blended_score
            rationale = (
                f"Melhor candidato ({best.agent}) tem score {best.blended_score:.2f} "
                f"abaixo do limiar de confiança ({escalate_threshold:.2f}) — "
                f"escalar para tier Opus em vez de trocar de segmento às cegas."
            )
        else:
            best_agent, best_prob = best.agent, best.blended_score
            rationale = (
                f"P(historico)={best.probability:.2f}, "
                f"match_keywords={best.keyword_score:.2f} -> "
                f"fallback recomendado: {best.agent} ({best.label})."
            )

        return FallbackResult(
            failed_agent=failed_agent,
            query=query,
            candidates=top,
            escalate=escalate,
            best_agent=best_agent,
            best_probability=round(best_prob, 4),
            rationale=rationale,
        )

    # -- persistência ---------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "version": 1,
            "smoothing": self.smoothing,
            "states": sorted(self.states),
            "trained_on": self.trained_on,
            "trained_at": self.trained_at,
            "transition_counts": {
                src: dict(counter) for src, counter in self.transition_counts.items()
            },
            "event_counts": dict(self.event_counts),
            "resolved_counts": dict(self.resolved_counts),
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "MarkovFallbackChain":
        chain = cls(smoothing=data.get("smoothing", 0.5))
        chain.states = set(data.get("states", [])) | set(VERTICAL_AGENTS) | set(ABSORBING_STATES)
        chain.trained_on = data.get("trained_on", 0)
        chain.trained_at = data.get("trained_at")
        for src, counts in data.get("transition_counts", {}).items():
            chain.transition_counts[src] = Counter(counts)
        chain.event_counts = defaultdict(int, data.get("event_counts", {}))
        chain.resolved_counts = defaultdict(int, data.get("resolved_counts", {}))
        return chain

    @classmethod
    def load(cls, path: str | Path) -> "MarkovFallbackChain":
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# 5. API pública em nível de módulo
# ---------------------------------------------------------------------------

DEFAULT_STATE_PATH = Path(__file__).parent / "data" / "fallback_markov_state.json"

_default_chain: Optional[MarkovFallbackChain] = None


def train_default_chain(save: bool = True, n_events: int = 1200) -> MarkovFallbackChain:
    """Treina a cadeia padrão sobre logs sintéticos e opcionalmente persiste."""
    chain = MarkovFallbackChain()
    chain.fit(generate_synthetic_logs(n_events=n_events))
    if save:
        chain.save(DEFAULT_STATE_PATH)
    global _default_chain
    _default_chain = chain
    return chain


def load_default_chain() -> MarkovFallbackChain:
    """Carrega o estado persistido; treina sobre dados sintéticos se ausente."""
    global _default_chain
    if _default_chain is not None:
        return _default_chain
    if DEFAULT_STATE_PATH.exists():
        _default_chain = MarkovFallbackChain.load(DEFAULT_STATE_PATH)
    else:
        _default_chain = train_default_chain(save=True)
    return _default_chain


def findFallback(
    failed_agent: str,
    query: str,
    chain: Optional[MarkovFallbackChain] = None,
    top_k: int = 3,
    escalate_threshold: float = 0.20,
    failure_reason: Optional[str] = None,
) -> FallbackResult:
    """findFallback(failed_agent, query) -> next agent by probability.

    Assinatura pedida pela especificação. Usa `chain` se fornecida, senão
    carrega/treina a cadeia padrão persistida em `DEFAULT_STATE_PATH`.
    """
    active_chain = chain or load_default_chain()
    return active_chain.find_fallback(
        failed_agent=failed_agent,
        query=query,
        top_k=top_k,
        escalate_threshold=escalate_threshold,
        failure_reason=failure_reason,
    )


# alias snake_case para quem preferir a convenção Python
find_fallback = findFallback


# ---------------------------------------------------------------------------
# 6. CLI
# ---------------------------------------------------------------------------

def _print_result(result: FallbackResult) -> None:
    print(f"\nAgente que falhou : {result.failed_agent} ({AGENT_LABELS.get(result.failed_agent, '?')})")
    print(f"Query              : {result.query!r}")
    print("-" * 78)
    print(f"{'agente':<16}{'P(histórico)':<14}{'match kw':<10}{'score final':<12}")
    for c in result.candidates:
        print(f"{c.agent:<16}{c.probability:<14.3f}{c.keyword_score:<10.3f}{c.blended_score:<12.3f}")
    print("-" * 78)
    if result.escalate:
        print(f"DECISÃO: escalar -> {OPUS_ESCALATION} (tier Opus, mesma vertical)")
    else:
        print(f"DECISÃO: fallback -> {result.best_agent} ({AGENT_LABELS.get(result.best_agent, '?')})"
              f"  [score={result.best_probability:.3f}]")
    print(f"Racional: {result.rationale}\n")


def _cmd_train(args: argparse.Namespace) -> None:
    if args.logs:
        events = load_logs_jsonl(args.logs)
        print(f"Carregados {len(events)} eventos reais de {args.logs}")
    else:
        events = generate_synthetic_logs(n_events=args.n_events)
        print(f"Gerados {len(events)} eventos sintéticos "
              f"(stand-in para {args.n_events} eventos / ~6 meses de logs v4.2 "
              f"— ver docstring do módulo).")

    chain = MarkovFallbackChain(smoothing=args.smoothing)
    chain.fit(events)

    print("\nMatriz de transição aprendida P(agente_j | agente_i falhou):\n")
    header = "de \\ para".ljust(16) + "".join(s.ljust(16) for s in sorted(chain.states))
    print(header)
    for src in sorted(chain.states):
        row = chain.transition_probs(src)
        line = src.ljust(16) + "".join(f"{row.get(s, 0):.2f}".ljust(16) for s in sorted(chain.states))
        print(line)

    if args.save:
        chain.save(args.state_path)
        print(f"\nEstado salvo em: {args.state_path}")


def _cmd_infer(args: argparse.Namespace) -> None:
    if Path(args.state_path).exists():
        chain = MarkovFallbackChain.load(args.state_path)
    else:
        print(f"[!] Nenhum estado em {args.state_path} — treinando sobre dados sintéticos.")
        chain = train_default_chain(save=True)

    result = chain.find_fallback(
        failed_agent=args.failed_agent,
        query=args.query,
        top_k=args.top_k,
        escalate_threshold=args.escalate_threshold,
        failure_reason=args.failure_reason,
    )
    _print_result(result)


def _cmd_demo(args: argparse.Namespace) -> None:
    print("=" * 78)
    print("DEMO — fallback_strategy.py (Manta Maestro v4.2)")
    print("=" * 78)

    chain = train_default_chain(save=True, n_events=args.n_events)
    print(f"\nTreinado sobre {chain.trained_on} eventos sintéticos. "
          f"Estado persistido em: {DEFAULT_STATE_PATH}\n")

    print("Top fallbacks por agente (ordenado por probabilidade histórica):")
    for agent in VERTICAL_AGENTS:
        top = chain.top_fallbacks(agent, k=3)
        sr = chain.success_rate(agent)
        sr_txt = f"{sr:.0%}" if sr is not None else "n/d"
        top_txt = ", ".join(f"{a}={p:.0%}" for a, p in top)
        print(f"  {agent:<4} (taxa sucesso fallback={sr_txt:<5}) -> {top_txt}")

    # Cenário exato citado na especificação: S8 falha numa query de ETA.
    print("\n--- Cenário da especificação: S8 falha numa consulta de ETA ---")
    result = chain.find_fallback(
        "S8",
        "A ETA está com vazão baixa e o SNIS pede indicador atualizado.",
        failure_reason="low_confidence",
    )
    _print_result(result)

    # Cenário de baixa confiança geral -> deve escalar para Opus.
    print("--- Cenário de baixo sinal (query fora de qualquer domínio conhecido) ---")
    result2 = chain.find_fallback(
        "S8",
        "Preciso de ajuda com uma planilha de RH, não é sobre engenharia.",
        escalate_threshold=0.35,
        failure_reason="out_of_scope",
    )
    _print_result(result2)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Fallback de agentes do Manta Maestro via cadeia de Markov.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    p_train = sub.add_parser("train", help="Treina a cadeia (sintético ou logs reais).")
    p_train.add_argument("--logs", type=str, default=None,
                          help="Arquivo JSONL com FallbackEvent reais.")
    p_train.add_argument("--synthetic", action="store_true",
                          help="Força uso de dados sintéticos mesmo se --logs for omitido (default).")
    p_train.add_argument("--n-events", type=int, default=1200, dest="n_events")
    p_train.add_argument("--smoothing", type=float, default=0.5)
    p_train.add_argument("--save", action="store_true")
    p_train.add_argument("--state-path", type=str, default=str(DEFAULT_STATE_PATH), dest="state_path")
    p_train.set_defaults(func=_cmd_train)

    p_infer = sub.add_parser("infer", help="Roda findFallback(failed_agent, query).")
    p_infer.add_argument("--failed-agent", required=True, dest="failed_agent",
                          choices=VERTICAL_AGENTS)
    p_infer.add_argument("--query", required=True)
    p_infer.add_argument("--top-k", type=int, default=3, dest="top_k")
    p_infer.add_argument("--escalate-threshold", type=float, default=0.20, dest="escalate_threshold")
    p_infer.add_argument("--failure-reason", type=str, default=None, dest="failure_reason",
                          choices=FAILURE_REASONS)
    p_infer.add_argument("--state-path", type=str, default=str(DEFAULT_STATE_PATH), dest="state_path")
    p_infer.set_defaults(func=_cmd_infer)

    p_demo = sub.add_parser("demo", help="Treina + salva + roda os exemplos da especificação.")
    p_demo.add_argument("--n-events", type=int, default=1200, dest="n_events")
    p_demo.set_defaults(func=_cmd_demo)

    return p


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
