"""
Fase 3 — Gateway de escrita `M20.write(drive, path, content, metadata)`.

Modelo: nenhum agente Manta chama Graph API direto. Todos passam pelo hub, que:

1. Aceita `WriteRequest` (drive_id, path, content_b64, metadata).
2. Envia payload para o Zapier webhook (`SP_HUB_ZAPIER_WRITE_WEBHOOK`) — Zapier
   faz o PUT `https://graph.microsoft.com/v1.0/drives/{driveId}/root:/{path}:/content`
   com o token OAuth de app-service.
3. Registra a operação em `sp_sync_log` (sync_type='write') e atualiza
   `sp_index` na próxima iteração do indexer.

Não bloqueia o hub: em caso de falha do webhook, o request é rejeitado com
`WriteResult.status='error'` — cabe ao agente chamador decidir se refaz.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sp_hub.db import SupabaseClient, write_sync_log
from sp_hub.models import WriteRequest

log = logging.getLogger("sp_hub.write_gateway")

_DEFAULT_TIMEOUT_S = 30.0


@dataclass
class WriteResult:
    status: str  # 'success' | 'error'
    drive_id: str
    path: str
    detail: str | None = None
    zapier_response: dict[str, Any] | None = None


class WriteGateway:
    """
    Encapsula o webhook Zapier + o audit log. Instância única por processo
    (o webhook URL fica no construtor).
    """

    def __init__(
        self,
        client: SupabaseClient,
        *,
        webhook_url: str | None = None,
        timeout_seconds: float = _DEFAULT_TIMEOUT_S,
    ):
        self.client = client
        self.webhook_url = webhook_url or os.environ.get(
            "SP_HUB_ZAPIER_WRITE_WEBHOOK"
        )
        self.timeout_seconds = timeout_seconds

    def write(self, request: WriteRequest) -> WriteResult:
        if not self.webhook_url:
            detail = "SP_HUB_ZAPIER_WRITE_WEBHOOK não configurado"
            log.error(detail)
            self._audit(request, status="error", detail=detail)
            return WriteResult(
                status="error",
                drive_id=request.drive_id,
                path=request.path,
                detail=detail,
            )

        payload = {
            "drive_id": request.drive_id,
            "path": request.path,
            "content_type": request.content_type,
            "content_b64": request.content_b64,
            "metadata": request.metadata,
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                if resp.status >= 300:
                    raise RuntimeError(f"zapier status={resp.status} body={raw[:200]}")
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = {"raw": raw}
                self._audit(request, status="success")
                return WriteResult(
                    status="success",
                    drive_id=request.drive_id,
                    path=request.path,
                    zapier_response=parsed,
                )
        except (urllib.error.URLError, RuntimeError, TimeoutError) as err:
            detail = f"zapier error: {err}"
            log.error(detail)
            self._audit(request, status="error", detail=detail)
            return WriteResult(
                status="error",
                drive_id=request.drive_id,
                path=request.path,
                detail=detail,
            )

    def _audit(self, request: WriteRequest, *, status: str, detail: str | None = None) -> None:
        """Registra a operação em sp_sync_log. Erros aqui não abortam o retorno."""
        row: dict[str, Any] = {
            "sync_type": "write",
            "status": status,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "docs_detected": 0,
            "docs_routed": 0,
            "docs_ingested_rag": 0,
            "errors": [detail] if detail else [],
            "metadata": {
                "drive_id": request.drive_id,
                "path": request.path,
                "content_type": request.content_type,
                "user_metadata": request.metadata,
            },
        }
        try:
            write_sync_log(self.client, row)
        except Exception as err:  # noqa: BLE001
            log.warning("audit log failed: %s", err)
