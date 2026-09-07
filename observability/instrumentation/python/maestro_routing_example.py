"""
maestro_routing_example.py — Exemplo de instrumentação do Maestro (Python)
===========================================================================

Demonstra o fluxo completo de tracing/metrics do Manta Maestro (Manta 00)
roteando uma query para um agente vertical (aqui: agente-saneamento,
Manta 03-S8), com:

  1. `maestro.route`  — routing span (L4, ver docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md)
  2. `registry.search` / `ranking.score` — sub-spans internos do routing
  3. `agent.dispatch`  — agent span (L2), com propagação de contexto W3C
     via headers HTTP para o processo do agente (pode ser um serviço
     Python OU Node.js — ver instrumentation/nodejs/agent_service_example.js)
  4. `skill.<nome>`    — skill span (L1), executado dentro do agente
  5. Métricas: manta.routing.latency_ms, manta.routing.success_rate,
     manta.agent.latency_ms, manta.agent.error_rate, manta.agent.queue_depth

Rodar (com o docker-compose deste diretório no ar):

    export OTEL_EXPORTER_TARGET=otlp_collector
    pip install -r ../requirements.txt
    python maestro_routing_example.py

Ou em modo 100% local, sem docker (spans só no console):

    OTEL_EXPORTER_TARGET=console python maestro_routing_example.py
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # observability/
from opentelemetry_setup import configure_telemetry, get_telemetry  # noqa: E402

try:
    import requests

    _REQUESTS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _REQUESTS_AVAILABLE = False


# ---------------------------------------------------------------------------
# Mocks simplificados do Agent Registry / Ranking (ver seção 2.2/2.3 do
# docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md) — o objetivo aqui é ilustrar
# ONDE os spans entram no pipeline de roteamento real, não implementar o
# registry de fato.
# ---------------------------------------------------------------------------
class Candidate(NamedTuple):
    agent_id: str
    segment: str
    score: float


_MOCK_REGISTRY = [
    Candidate("manta-03-s8", "saneamento", 0.0),
    Candidate("manta-03-s9", "energia", 0.0),
    Candidate("manta-13", "business-dev", 0.0),
]

# Fila simulada de tarefas pendentes por agente, usada para alimentar o
# gauge observável manta.agent.queue_depth (ver register_queue_depth_provider).
_MOCK_QUEUES = {"manta-03-s8": 2, "manta-03-s9": 0, "manta-13": 5}


def registry_search(telemetry, query: str, top_k: int = 3):
    with telemetry.tracer.start_as_current_span("registry.search") as span:
        time.sleep(0.01)  # simula I/O no Supabase (pgvector + BM25)
        candidates = [
            c._replace(score=round(random.uniform(0.4, 0.95), 3)) for c in _MOCK_REGISTRY[:top_k]
        ]
        span.set_attribute("manta.registry.candidates_count", len(candidates))
        span.add_event("candidates_found", {"count": len(candidates)})
        return candidates


def ranking_score(telemetry, candidates, query: str):
    with telemetry.tracer.start_as_current_span("ranking.score") as span:
        time.sleep(0.005)
        ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
        span.set_attribute("manta.ranking.top_agent", ranked[0].agent_id)
        span.set_attribute("manta.ranking.top_score", ranked[0].score)
        return ranked


# ---------------------------------------------------------------------------
# Dispatch: chama o agente. Duas variantes são mostradas —
#   (a) in-process (mesmo runtime Python, ex.: subagentes do Claude Code)
#   (b) HTTP remoto, propagando o trace via headers (para um serviço
#       separado, inclusive um agente escrito em Node.js).
# ---------------------------------------------------------------------------
def dispatch_in_process(telemetry, agent_id: str, segment: str, query: str) -> str:
    with telemetry.agent_span(agent_id, segment=segment) as _span:
        telemetry.register_queue_depth_provider(agent_id, lambda: _MOCK_QUEUES[agent_id])

        with telemetry.skill_span("ler-edital", agent_id):
            time.sleep(0.06)  # simula extração de PDF

        with telemetry.skill_span("aluci-guard", agent_id):
            time.sleep(0.015)  # simula auditoria de referências

        return f"[{agent_id}] parecer técnico gerado para: {query[:60]!r}"


def dispatch_remote_http(telemetry, agent_id: str, segment: str, query: str, base_url: str) -> str:
    """Handoff via HTTP para um agente rodando como serviço separado
    (ex.: agent_service_example.js em Node.js). O traceparent é injetado
    nos headers para que o span `agent.dispatch` do lado remoto seja
    filho do mesmo trace do routing span do Maestro."""
    if not _REQUESTS_AVAILABLE:
        raise RuntimeError("pip install requests` para usar dispatch_remote_http")

    with telemetry.agent_span(agent_id, phase="dispatch_remote", segment=segment):
        headers = telemetry.inject({"content-type": "application/json"})
        resp = requests.post(
            f"{base_url}/agents/{agent_id}/invoke",
            json={"query": query},
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["result"]


# ---------------------------------------------------------------------------
# Fluxo completo do Maestro
# ---------------------------------------------------------------------------
def route(telemetry, query: str, request_id: str) -> str:
    with telemetry.routing_span(query, request_id=request_id) as rspan:
        candidates = registry_search(telemetry, query)
        ranked = ranking_score(telemetry, candidates, query)
        chosen = ranked[0]

        rspan.set_attribute("manta.agent.chosen", chosen.agent_id)
        rspan.set_attribute("manta.agent.chosen_score", chosen.score)

        result = dispatch_in_process(telemetry, chosen.agent_id, chosen.segment, query)
        return result


def main() -> None:
    telemetry = configure_telemetry("manta-maestro", agent_id="manta-00", environment="local")

    queries = [
        "Preciso de parecer técnico sobre a ETE Riachuelo (AySA) para o EVTEA",
        "Qual o RAP teto do lote de transmissão ANEEL 5/2026?",
        "Analisar contrato de dragagem do porto de Santos",
    ]

    for i, q in enumerate(queries, start=1):
        result = route(telemetry, q, request_id=f"req-{i:03d}")
        print(result)

    from opentelemetry_setup import shutdown_telemetry

    shutdown_telemetry()


if __name__ == "__main__":
    main()
