"""
Materializa `RoutingDecision` em `FeedEntry`s prontas para `sp_agent_feed`.

Cada decisão com N `target_agents` produz N feed entries (uma por agente).
Decisões sem agente destino são descartadas silenciosamente (log responsabilidade
do caller — `delta_sync`).
"""

from __future__ import annotations

from sp_hub.models import FeedEntry, RoutingDecision


def decisions_to_feed(decisions: list[RoutingDecision]) -> list[FeedEntry]:
    """Explode as decisões em uma feed entry por (doc, agente)."""
    out: list[FeedEntry] = []
    for decision in decisions:
        if not decision.has_targets:
            continue
        for agent_code in decision.target_agents:
            out.append(
                FeedEntry(
                    agent_code=agent_code,
                    doc_id=decision.doc.doc_id,
                    doc_path=_sanitize_path(decision.doc.doc_path),
                    doc_name=decision.doc.doc_name,
                    doc_type=decision.doc_type,
                    file_ext=decision.doc.file_ext,
                    priority=decision.priority,
                    metadata={
                        "matched_rules": decision.matched_rules,
                        "drive_id": decision.doc.drive_id,
                        **decision.doc.metadata,
                    },
                )
            )
    return out


# R1 — paths sanitizados antes de servir a outros agentes.
# Substitui o segmento imediatamente após 02_CLIENTE/ por <CLIENTE>.
# Ex.: 02_CLIENTE/CCR-Rodovias/01_CONTRATO/x.pdf → 02_CLIENTE/<CLIENTE>/01_CONTRATO/x.pdf.
import re as _re

_CLIENT_SEGMENT = _re.compile(r"(02_CLIENTE/)[^/]+(/)", _re.IGNORECASE)


def _sanitize_path(path: str) -> str:
    return _CLIENT_SEGMENT.sub(r"\1<CLIENTE>\2", path)
