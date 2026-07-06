"""
Classificação de doc_type a partir de (path, name, ext).

Fallback estático quando o `sp_routing_rules` retorna múltiplos tipos ou nenhum
— serve como default sensato. As decisões finais de `doc_type` no feed são
tomadas pelo `router.py`, que consulta as rules ativas.
"""

from __future__ import annotations

import re

# Ordem importa: primeira regra que casar vence.
# `\b` não separa em `_` (underscore é word char em Python re). Como os nomes
# de arquivo tipicamente usam `_`/`-` como separadores, definimos boundaries
# alfa-numéricos explícitos.
_LB = r"(?<![A-Za-z0-9])"  # left boundary
_RB = r"(?![A-Za-z0-9])"   # right boundary

_NAME_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(rf"{_LB}SICRO{_RB}", re.IGNORECASE), "composicao_custo"),
    (re.compile(rf"{_LB}(BM|Boletim.?Medi\w*){_RB}", re.IGNORECASE), "boletim_medicao"),
    (re.compile(rf"{_LB}RDO{_RB}", re.IGNORECASE), "diario_obra"),
    (re.compile(rf"{_LB}(TAC|Termo.?Aditivo){_RB}", re.IGNORECASE), "aditivo_contrato"),
    (re.compile(rf"{_LB}(PER|Projeto.?Executivo.?Refer\w*){_RB}", re.IGNORECASE), "per"),
    (re.compile(rf"{_LB}(sondagem|SPT|CPT){_RB}", re.IGNORECASE), "sondagem"),
    (re.compile(rf"{_LB}batimetri\w*{_RB}", re.IGNORECASE), "batimetria"),
    (re.compile(rf"{_LB}(barragem|dam|vertedouro){_RB}", re.IGNORECASE), "barragem"),
    (re.compile(rf"{_LB}(edital|licitacao|preg[aã]o){_RB}", re.IGNORECASE), "edital"),
]

_EXT_RULES: dict[str, str] = {
    "xer": "cronograma_p6",
    "mpp": "cronograma_p6",
    "dwg": "projeto_cad",
    "dxf": "projeto_cad",
    "ifc": "modelo_bim",
    "ifczip": "modelo_bim",
    "ifcxml": "modelo_bim",
    "landxml": "landxml",
}

_FOLDER_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"02_CLIENTE/[^/]+/01_CONTRATO", re.IGNORECASE), "contrato"),
    (re.compile(r"02_CLIENTE/[^/]+/02_REC", re.IGNORECASE), "edital"),
    (re.compile(r"02_CLIENTE/[^/]+/03_PROPOSTA", re.IGNORECASE), "proposta"),
    (re.compile(r"02_CLIENTE/[^/]+/04_PROJETO", re.IGNORECASE), "projeto"),
    (re.compile(r"02_CLIENTE/[^/]+/05_MEDICAO", re.IGNORECASE), "medicao"),
    (
        re.compile(r"02_CLIENTE/[^/]+/06_CORRESPONDENCIA", re.IGNORECASE),
        "correspondencia",
    ),
    (re.compile(r"02_CLIENTE/[^/]+/07_CRONOGRAMA", re.IGNORECASE), "cronograma"),
    (re.compile(r"04_IA/Manta-Maestro", re.IGNORECASE), "skill"),
    (re.compile(r"04_IA/RAG", re.IGNORECASE), "rag_chunk"),
    (re.compile(r"03_BIBLIOTECA", re.IGNORECASE), "norma_paper"),
]


def classify(path: str, name: str, ext: str | None) -> str:
    """
    Devolve o `doc_type` mais específico para (path, name, ext).

    Ordem de precedência: name > ext > folder > fallback.
    """
    for pattern, doc_type in _NAME_RULES:
        if pattern.search(name):
            return doc_type

    if ext:
        normalized = ext.lstrip(".").lower()
        if normalized in _EXT_RULES:
            return _EXT_RULES[normalized]

    for pattern, doc_type in _FOLDER_RULES:
        if pattern.search(path):
            return doc_type

    return "outros"
