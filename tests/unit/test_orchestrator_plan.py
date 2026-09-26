"""
Testes unitários — o fan-out do MaestroOrchestrator invoca só os agentes
do plano (planejador N0) mais os declarados no workflow, nunca o pool
grande do detector legado. Sem rede: o QueueExecutor é substituído.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.maestro.orchestrator import MaestroOrchestrator  # noqa: E402
from src.maestro.parser import FanOutPhase  # noqa: E402
from src.maestro.planner import planejar  # noqa: E402

pytestmark = pytest.mark.unit


class _FakeQueue:
    def __init__(self):
        self.agents: list[str] = []

    async def execute_all(self, tasks):
        self.agents = [t.agent_name for t in tasks]
        return {t.agent_name: None for t in tasks}

    def get_results_summary(self):
        return {"completed": len(self.agents), "failed": 0}


def _fan_out(pedido: str, declarados: list[str]) -> list[str]:
    orq = MaestroOrchestrator()
    fila = _FakeQueue()
    orq.queue_executor = fila
    asyncio.run(orq._execute_fan_out(FanOutPhase(agents=declarados), planejar(pedido)))
    return fila.agents


def test_fan_out_so_invoca_agentes_do_plano():
    agentes = _fan_out("revisar orçamento da ETE Lote 3", [])
    assert agentes == ["agente-saneamento", "agente-orcamento"]


def test_fan_out_nao_usa_pool_do_detector():
    pedido = "revisar orçamento da ETE Lote 3"
    pool_legado = MaestroOrchestrator().detector.detect(pedido).agents_pool
    agentes = _fan_out(pedido, [])
    assert len(agentes) < len(pool_legado)
    assert "maestro-router" not in agentes


def test_fan_out_soma_declarados_sem_duplicar_e_mantem_ordem_do_plano():
    agentes = _fan_out("UHE com barragem e LT", ["agente-energia", "agente-cronograma"])
    assert agentes == ["agente-barragens", "agente-energia", "agente-cronograma"]
