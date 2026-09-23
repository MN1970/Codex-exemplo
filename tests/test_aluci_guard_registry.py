"""Regressão do aluci-guard (camada T3 de docs/PLANO-TESTES-MAESTRO-v1.md)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "guardrails" / "aluci-guard"))

from auditor import auditar_texto  # noqa: E402

REAIS = [
    "Estrutura conforme NBR 6118:2023.",
    "Fundações segundo NBR 6122:2019.",
    "Metas da Lei 14.026/2020.",
    "Desempenho de edificações pela NBR 15575.",
    "Armazenamento de inflamáveis pela NBR 17505.",
    "Transformador conforme NBR 5356-1.",
    "Série NBR 12211-12218 de abastecimento.",
    "Arrendamento pela Lei 12.815/2013.",
]
FALSAS = [
    "Dimensionar pela NBR 19999.",
    "Composição SICRO 9999999.",
    "Conforme a Lei 99.999/2031.",
    "Transformador conforme NBR 60076.",
    "Ver doi: abc/123 da norma.",
]


def _falhou(texto):
    return any(a["verdict"] != "OK" for a in auditar_texto(texto)["achados"])


@pytest.mark.unit
@pytest.mark.parametrize("texto", REAIS)
def test_referencia_real_passa(texto):
    assert not _falhou(texto)


@pytest.mark.unit
@pytest.mark.parametrize("texto", FALSAS)
def test_referencia_inventada_e_marcada(texto):
    assert _falhou(texto)
