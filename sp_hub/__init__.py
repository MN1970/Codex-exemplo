"""
Manta 20 — SP Hub v2.0

Ponto único de entrada e saída de documentos SharePoint para os 19 agentes do
Maestro. Ver `docs/MANTA-20-SPHUB-SPEC-v2.0.md` para a spec canônica.

Uso típico (cron):

    from sp_hub.db import supabase_client
    from sp_hub.delta_sync import run_delta_sync

    result = run_delta_sync(supabase_client())
    print(result.summary())

Fase 2 (delta + notificação): `delta_sync.run_delta_sync`.
Fase 3 (RAG ingest):          `rag_bridge.trigger_ingest`.
Fase 3 (escrita SP):          `write_gateway.write_document`.
"""

from sp_hub.models import (
    ChangeEntry,
    FeedEntry,
    Priority,
    RoutingDecision,
    RoutingRule,
    SyncResult,
    WriteRequest,
)

__all__ = [
    "ChangeEntry",
    "FeedEntry",
    "Priority",
    "RoutingDecision",
    "RoutingRule",
    "SyncResult",
    "WriteRequest",
]

__version__ = "2.0.0"
