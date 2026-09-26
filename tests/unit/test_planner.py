"""
Testes unitários — planejador do Maestro (N0), src/maestro/planner.py.

Garantem as regras de contenção descritas em docs/maestro/PLANEJADOR.md:
plano mínimo, casos ambíguos documentados, aprovação para Opus ou
muitos agentes, guardiões só com entregável externo. Sem rede.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.maestro.planner import (  # noqa: E402
    MAX_AGENTES,
    MAX_AGENTES_SEM_APROVACAO,
    PADRAO_MOTIVA,
    planejar,
    prompt_planejador_llm,
)

pytestmark = pytest.mark.unit


def test_um_segmento_gera_um_agente():
    plano = planejar("dimensionar a adutora de água bruta")
    assert plano.agentes == ["agente-saneamento"]
    assert plano.metodo == "palavras-chave"
    assert not plano.requer_aprovacao


@pytest.mark.parametrize(
    "pedido, esperado",
    [
        ("UHE com barragem e LT 500 kV", ["agente-barragens", "agente-energia"]),
        ("ETE com subestação dedicada", ["agente-saneamento", "agente-energia"]),
        ("porto com pista de carga", ["agente-portos", "agente-aeroportos"]),
        ("ponte na rodovia BR-153", ["agente-infraestrutura-s2", "agente-infraestrutura-s1"]),
    ],
)
def test_casos_ambiguos_documentados(pedido, esperado):
    plano = planejar(pedido)
    assert plano.agentes == esperado
    assert plano.passos[0].papel == "primario"
    assert all(p.papel == "handoff" for p in plano.passos[1:])


def test_atividade_vira_handoff_do_segmento():
    plano = planejar("revisar orçamento da ETE Lote 3")
    assert plano.agentes == ["agente-saneamento", "agente-orcamento"]


def test_sem_segmento_atividade_vira_primario():
    plano = planejar("montar o cronograma do contrato")
    assert plano.passos[0].agente == "agente-cronograma"
    assert plano.passos[0].papel == "primario"


def test_siglas_so_casam_em_maiusculas():
    # "eta", "rap" e "lt" em minúsculas são palavras comuns, não siglas.
    assert planejar("a meta é boa, eta nóis; rap e lt").metodo == "llm"
    assert planejar("ETA de Guandu").agentes == ["agente-saneamento"]


def test_ccr_rodovias_nao_aciona_barragens():
    plano = planejar("pavimento CBUQ da CCR Rodovias")
    assert "agente-barragens" not in plano.agentes
    assert PADRAO_MOTIVA[0] in plano.padroes_output


def test_opus_exige_aprovacao():
    plano = planejar("pleito de reequilíbrio na rodovia")
    assert "agente-claims" in plano.agentes
    assert plano.requer_aprovacao
    assert any("Opus" in m for m in plano.motivos_aprovacao)


def test_muitos_agentes_exige_aprovacao_e_respeita_teto():
    pedido = ("ETE, barragem, porto, LT, aeroporto, ponte, metrô, ferrovia e "
              "rodovia com orçamento e cronograma")
    plano = planejar(pedido)
    assert len(plano.passos) == MAX_AGENTES
    assert plano.requer_aprovacao
    assert [p.ordem for p in plano.passos] == list(range(1, MAX_AGENTES + 1))


def test_ate_limite_sem_aprovacao_nao_pede_aprovacao():
    plano = planejar("orçamento e cronograma da ETE")
    assert len(plano.passos) <= MAX_AGENTES_SEM_APROVACAO
    assert not plano.requer_aprovacao


def test_guardioes_so_com_entregavel_externo():
    assert planejar("ETE nova").guardioes == []
    assert planejar("ETE nova", entregavel_externo=True).guardioes == [
        "aluci-guard", "consist-guard"]


def test_teto_de_tokens_soma_os_niveis():
    plano = planejar("ETE nova", entregavel_externo=True)
    # N0 + 1×N1 + 2 guardiões N3
    assert plano.teto_tokens == 20_000 + 120_000 + 2 * 10_000


def test_sem_palavra_chave_cai_no_planejador_llm():
    plano = planejar("qual a capital da França")
    assert plano.metodo == "llm"
    assert plano.passos == []
    prompt = prompt_planejador_llm(plano.pedido)
    assert "agente-saneamento" in prompt
    # o planejador LLM só vê o catálogo compacto, não as definições
    assert len(prompt) < 3_000
