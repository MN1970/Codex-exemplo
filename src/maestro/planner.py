"""
Planejador do Maestro (nível N0) — decide o conjunto mínimo de agentes
ANTES de carregar qualquer um.

Objetivo: economizar tokens e janela de contexto. O Maestro não abre o
ecossistema inteiro "por garantia"; ele gera um plano curto (quais
agentes, em que ordem, com que modelo, com que teto de tokens e se
precisa de aprovação humana) e só então executa.

Primeiro passo é determinístico (palavras-chave, custo LLM zero). Só
quando nada casa o plano sai com `metodo="llm"`, sinalizando que o
planejador Haiku deve decidir a partir do catálogo compacto
(`prompt_planejador_llm`).

Especificação completa: docs/maestro/PLANEJADOR.md.
Sem rede, sem secrets, sem dependências fora da biblioteca padrão.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"

# ── Regras de contenção (ver docs/maestro/PLANEJADOR.md) ────────────────
MAX_AGENTES_SEM_APROVACAO = 3
MAX_AGENTES = 5

# Teto de tokens por passo, por nível da hierarquia N0–N3.
TETO_TOKENS_POR_NIVEL = {"N0": 20_000, "N1": 120_000, "N2": 60_000, "N3": 10_000}

GUARDIOES_ENTREGAVEL_EXTERNO = ("aluci-guard", "consist-guard")

# ── Segmentos (eixo S) ──────────────────────────────────────────────────
# Espelho da seção ROUTING de docs/maestro/REGISTRO-AGENTES.md e da tabela
# `maestro_routing_keywords` (Supabase). A ORDEM define o primário quando
# mais de um segmento casa — segue os casos ambíguos documentados:
# UHE → barragens antes de energia; ETE + subestação → saneamento antes
# de energia; porto + pista de carga → portos antes de aeroportos;
# ponte rodoviária → OAE antes de rodovias.
SEGMENTOS: list[tuple[str, str, tuple[str, ...]]] = [
    ("agente-saneamento", "S9", (
        "saneamento", "ETA", "ETE", "adutora", "esgoto", "AySA",
        "drenagem urbana", "SNIS")),
    ("agente-barragens", "S11", (
        "barragem", "barragens", "vertedouro", "CFRD", "CCR", "rejeitos",
        "PNSB", "ICOLD", "CBDB", "TSF", "UHE")),
    ("agente-portos", "S7", (
        "porto", "portos", "portuario", "terminal portuario", "ANTAQ",
        "dragagem", "molhe", "berco", "calado", "conteiner", "granel")),
    ("agente-energia", "S10", (
        "transmissao", "LT", "subestacao", "ANEEL", "RAP",
        "leilao de transmissao", "ONS", "EPE")),
    ("agente-aeroportos", "S8", (
        "aeroporto", "aeroportos", "pista de pouso", "pista de carga",
        "ANAC", "ICAO", "TPS", "TECA", "balizamento")),
    ("agente-infraestrutura-s2", "S2", (
        "ponte", "viaduto", "OAE", "NBR 7187", "tunel rodoviario")),
    ("agente-infraestrutura-s4", "S4", (
        "metro", "NATM", "PSD", "linha 4", "linha 5", "VLT")),
    ("agente-infraestrutura-s3", "S3", (
        "ferrovia", "ferroviario", "trilho", "AMV", "dormente",
        "via permanente")),
    ("agente-infraestrutura-s1", "S1", (
        "rodovia", "rodovias", "pavimento", "pavimentacao", "CBUQ", "BGS",
        "terraplenagem", "SICRO", "DNIT")),
]

# ── Atividades (eixo A) → handoff horizontal ────────────────────────────
ATIVIDADES: list[tuple[str, str, tuple[str, ...]]] = [
    ("agente-claims", "A7", (
        "claim", "claims", "pleito", "reequilibrio", "desequilibrio")),
    ("agente-orcamento", "A3", ("orcamento", "orcar", "custo unitario", "BDI")),
    ("agente-cronograma", "A5", (
        "cronograma", "XER", "Primavera", "curva S", "caminho critico")),
    ("agente-contratual", "A6", ("contrato", "contratual", "aditivo", "clausula")),
    ("agente-modelagem", "A4", (
        "modelagem financeira", "fluxo de caixa", "TIR", "VPL", "project finance")),
    ("agente-bd", "A1", ("proposta", "licitacao", "edital")),
    ("agente-apresentacoes", "A1", ("apresentacao", "slides", "PPT", "PPTX")),
    ("agente-advisory", "A8", ("advisory", "second opinion", "due diligence")),
]

# ── Co-agentes que não substituem o primário ───────────────────────────
CO_AGENTE_ESG = ("manta-20-esg", (
    "ESG", "biodiversidade", "carbono", "offset", "IBAMA", "FUNAI",
    "Net Zero", "GHG", "TCFD", "SASB", "GRI", "licenca social"))

PADRAO_MOTIVA = ("docs/PADRAO-OUTPUT-MOTIVA.md", (
    "Motiva", "CCR Rodovias", "SP-258", "SP-330", "Contorno Apucarana"))

# Modelo padrão quando o agente não tem arquivo local com `model:`.
MODELO_PADRAO = "sonnet"


# ── Estruturas ──────────────────────────────────────────────────────────
@dataclass
class Passo:
    ordem: int
    agente: str
    papel: str  # primario | handoff | co-agente
    nivel: str
    modelo: str
    motivo: str


@dataclass
class Plano:
    pedido: str
    metodo: str  # palavras-chave | llm
    passos: list[Passo] = field(default_factory=list)
    guardioes: list[str] = field(default_factory=list)
    padroes_output: list[str] = field(default_factory=list)
    teto_tokens: int = 0
    requer_aprovacao: bool = False
    motivos_aprovacao: list[str] = field(default_factory=list)

    @property
    def agentes(self) -> list[str]:
        return [p.agente for p in self.passos]

    def to_dict(self) -> dict:
        return asdict(self)

    def resumo(self) -> str:
        if not self.passos:
            return (f"Plano ({self.metodo}): nenhuma palavra-chave casou — "
                    "planejador LLM (Haiku) decide a partir do catálogo.")
        linhas = [f"Plano ({self.metodo}) — teto {self.teto_tokens:,} tokens".replace(",", ".")]
        for p in self.passos:
            linhas.append(f"  {p.ordem}. {p.agente} [{p.papel}, {p.nivel}, {p.modelo}] — {p.motivo}")
        if self.guardioes:
            linhas.append(f"  guardiões no fim: {', '.join(self.guardioes)}")
        if self.padroes_output:
            linhas.append(f"  padrão de output: {', '.join(self.padroes_output)}")
        if self.requer_aprovacao:
            linhas.append(f"  ⚠ requer aprovação: {'; '.join(self.motivos_aprovacao)}")
        return "\n".join(linhas)


# ── Casamento de palavras-chave ─────────────────────────────────────────
def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto)
                   if not unicodedata.combining(c))


def _eh_sigla(chave: str) -> bool:
    """Siglas curtas (LT, RAP, ETA, TPS...) casam só em maiúsculas, para
    não confundir com palavras comuns ("eta", "rap", "lt")."""
    return chave.isupper() and len(chave.replace(" ", "")) <= 5


def _casa(texto_orig: str, texto_norm: str, chave: str) -> bool:
    alvo, base = (chave, texto_orig) if _eh_sigla(chave) else (
        _sem_acento(chave).lower(), texto_norm)
    padrao = r"(?<![\w-])" + re.escape(alvo) + r"(?![\w-])"
    return re.search(padrao, base) is not None


def _achados(texto_orig: str, texto_norm: str, chaves: tuple[str, ...]) -> list[str]:
    return [c for c in chaves if _casa(texto_orig, texto_norm, c)]


def _modelo_do_agente(slug: str) -> str:
    path = AGENTS_DIR / f"{slug}.md"
    if path.exists():
        m = re.search(r"^model:\s*(\w+)", path.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            return m.group(1)
    return MODELO_PADRAO


# ── Planejamento ────────────────────────────────────────────────────────
def planejar(pedido: str, entregavel_externo: bool = False) -> Plano:
    """Gera o plano mínimo para `pedido`. Determinístico e sem rede."""
    texto = pedido
    # "CCR Rodovias" é cliente (Motiva), não CCR de barragem (concreto
    # compactado a rolo): tira a expressão antes de casar segmentos.
    motiva = _achados(texto, _sem_acento(texto).lower(), PADRAO_MOTIVA[1])
    texto_seg = re.sub(r"CCR\s+Rodovias", " ", texto, flags=re.IGNORECASE)
    norm = _sem_acento(texto_seg).lower()

    passos: list[Passo] = []

    for slug, codigo, chaves in SEGMENTOS:
        hits = _achados(texto_seg, norm, chaves)
        if hits:
            papel = "primario" if not passos else "handoff"
            passos.append(Passo(0, slug, papel, "N1", _modelo_do_agente(slug),
                                f"{codigo}: {', '.join(hits)}"))

    for slug, codigo, chaves in ATIVIDADES:
        hits = _achados(texto_seg, norm, chaves)
        if hits and slug not in [p.agente for p in passos]:
            papel = "primario" if not passos else "handoff"
            passos.append(Passo(0, slug, papel, "N1", _modelo_do_agente(slug),
                                f"{codigo}: {', '.join(hits)}"))

    esg_hits = _achados(texto_seg, norm, CO_AGENTE_ESG[1])
    if esg_hits:
        passos.append(Passo(0, CO_AGENTE_ESG[0], "co-agente", "N1", "sonnet",
                            f"ESG: {', '.join(esg_hits)}"))

    plano = Plano(pedido=pedido, metodo="palavras-chave" if passos else "llm")
    if motiva:
        plano.padroes_output.append(PADRAO_MOTIVA[0])

    if len(passos) > MAX_AGENTES:
        plano.motivos_aprovacao.append(
            f"{len(passos)} agentes casaram; plano cortado nos {MAX_AGENTES} primeiros")
        passos = passos[:MAX_AGENTES]
    for i, p in enumerate(passos, start=1):
        p.ordem = i
    plano.passos = passos

    if entregavel_externo and passos:
        plano.guardioes = list(GUARDIOES_ENTREGAVEL_EXTERNO)

    plano.teto_tokens = (
        TETO_TOKENS_POR_NIVEL["N0"]
        + sum(TETO_TOKENS_POR_NIVEL[p.nivel] for p in passos)
        + TETO_TOKENS_POR_NIVEL["N3"] * len(plano.guardioes)
    )

    if len(passos) > MAX_AGENTES_SEM_APROVACAO:
        plano.motivos_aprovacao.append(
            f"{len(passos)} agentes (limite sem aprovação: {MAX_AGENTES_SEM_APROVACAO})")
    opus = [p.agente for p in passos if p.modelo == "opus"]
    if opus:
        plano.motivos_aprovacao.append(f"usa Opus: {', '.join(opus)}")
    plano.requer_aprovacao = bool(plano.motivos_aprovacao)
    return plano


def catalogo_compacto() -> str:
    """Uma linha por agente — é tudo que o planejador LLM precisa ver.
    Nunca inclui o corpo das definições."""
    linhas = [f"- {slug} ({cod}): {', '.join(ch[:4])}" for slug, cod, ch in SEGMENTOS]
    linhas += [f"- {slug} ({cod}): {', '.join(ch[:4])}" for slug, cod, ch in ATIVIDADES]
    linhas.append(f"- {CO_AGENTE_ESG[0]} (co-agente): {', '.join(CO_AGENTE_ESG[1][:4])}")
    return "\n".join(linhas)


def prompt_planejador_llm(pedido: str) -> str:
    """Prompt curto para o planejador Haiku quando `metodo == "llm"`."""
    return (
        "Você é o planejador do Manta Maestro. Escolha o MENOR conjunto de "
        f"agentes (1 por padrão, no máximo {MAX_AGENTES_SEM_APROVACAO} sem aprovação) "
        "para atender o pedido. Responda só JSON no formato "
        '{"passos":[{"agente":"...","papel":"primario|handoff","motivo":"..."}],'
        '"requer_aprovacao":false}. Se nenhum agente servir, devolva passos vazios.\n\n'
        f"Catálogo:\n{catalogo_compacto()}\n\nPedido: {pedido}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Planejador do Manta Maestro (N0).")
    ap.add_argument("pedido", help="texto do pedido do usuário")
    ap.add_argument("--externo", action="store_true",
                    help="entregável vai para cliente (inclui guardiões no fim)")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    args = ap.parse_args(argv)

    plano = planejar(args.pedido, entregavel_externo=args.externo)
    if args.json:
        print(json.dumps(plano.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(plano.resumo())
    return 0


if __name__ == "__main__":
    sys.exit(main())
