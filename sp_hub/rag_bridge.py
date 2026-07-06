"""
Fase 3 — RAG bridge (Manta 18).

Quando `delta_sync` detecta um doc com `priority='alta'`, chama o Manta 18
para chunk + embed + insert em pgvector. Duas modalidades:

- HTTP direto: POST `{SP_HUB_RAG_ENDPOINT}/api/ingest` com o payload da decisão.
- Fila Supabase: insert em `rag_ingest_queue` (fallback quando endpoint ausente
  — o M18 puxa do próprio Supabase por cron).

Nenhuma das duas modalidades bloqueia o delta_sync: erros são registrados em
`SyncResult.errors` mas não interrompem o processamento das demais decisões.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Protocol

from sp_hub.models import RoutingDecision

log = logging.getLogger("sp_hub.rag_bridge")

_DEFAULT_TIMEOUT_S = 10.0


class RagBridge(Protocol):
    def trigger_ingest(self, decision: RoutingDecision) -> None: ...


class NoopRagBridge:
    """Bridge inerte: usado quando não há endpoint nem cliente configurado."""

    def trigger_ingest(self, decision: RoutingDecision) -> None:  # noqa: D401 — protocol
        log.debug("rag_bridge noop: %s", decision.doc.doc_id)


class HttpRagBridge:
    """POST síncrono para o endpoint do Manta 18."""

    def __init__(self, endpoint: str, timeout_seconds: float = _DEFAULT_TIMEOUT_S):
        self.endpoint = endpoint.rstrip("/") + "/api/ingest"
        self.timeout_seconds = timeout_seconds

    def trigger_ingest(self, decision: RoutingDecision) -> None:
        payload = {
            "doc_id": decision.doc.doc_id,
            "doc_path": decision.doc.doc_path,
            "doc_name": decision.doc.doc_name,
            "doc_type": decision.doc_type,
            "file_ext": decision.doc.file_ext,
            "drive_id": decision.doc.drive_id,
            "priority": decision.priority.value,
            "target_agents": decision.target_agents,
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                if resp.status >= 300:
                    raise RuntimeError(f"rag ingest status={resp.status}")
        except urllib.error.URLError as err:
            raise RuntimeError(f"rag ingest network error: {err}") from err


class QueueRagBridge:
    """Fallback: insere em `rag_ingest_queue`; o M18 puxa por cron."""

    def __init__(self, client):
        self.client = client

    def trigger_ingest(self, decision: RoutingDecision) -> None:
        row = {
            "doc_id": decision.doc.doc_id,
            "doc_path": decision.doc.doc_path,
            "doc_type": decision.doc_type,
            "priority": decision.priority.value,
            "status": "pending",
            "metadata": {
                "target_agents": decision.target_agents,
                "matched_rules": decision.matched_rules,
                "drive_id": decision.doc.drive_id,
            },
        }
        self.client.table("rag_ingest_queue").insert(row).execute()


def build_default_rag_bridge() -> RagBridge:
    """
    Escolhe a implementação a partir das env vars.

    - `SP_HUB_RAG_ENDPOINT` setado → HttpRagBridge.
    - Caso contrário → NoopRagBridge (registra debug, não falha).

    Para usar a fila Supabase, o caller injeta manualmente `QueueRagBridge`.
    """
    endpoint = os.environ.get("SP_HUB_RAG_ENDPOINT")
    if endpoint:
        return HttpRagBridge(endpoint)
    return NoopRagBridge()
