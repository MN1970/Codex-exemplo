"""
Wrapper minimalista sobre um cliente Supabase — Protocol para permitir fake
in-memory em teste sem depender do supabase-py real.

Em produção, `supabase_client()` retorna o `supabase.Client` construído a partir
de `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`. Em teste, o `conftest.py` injeta um
fake que expõe a mesma superfície.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Protocol


class SupabaseTable(Protocol):
    """Superfície mínima do query builder do supabase-py que usamos."""

    def select(self, cols: str) -> "SupabaseTable": ...
    def eq(self, col: str, value: Any) -> "SupabaseTable": ...
    def gt(self, col: str, value: Any) -> "SupabaseTable": ...
    def order(self, col: str, desc: bool = False) -> "SupabaseTable": ...
    def limit(self, n: int) -> "SupabaseTable": ...
    def insert(self, rows: list[dict] | dict) -> "SupabaseTable": ...
    def upsert(
        self, rows: list[dict] | dict, on_conflict: str | None = None
    ) -> "SupabaseTable": ...
    def execute(self) -> Any: ...


class SupabaseClient(Protocol):
    def table(self, name: str) -> SupabaseTable: ...


def supabase_client() -> SupabaseClient:
    """Constrói o cliente real. Levanta se as env vars não estiverem setadas."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError(
            "SP Hub: SUPABASE_URL e SUPABASE_SERVICE_KEY precisam estar setados"
        )
    # Import tardio para não exigir supabase-py em testes.
    from supabase import create_client  # type: ignore

    return create_client(url, key)


def last_successful_sync_at(client: SupabaseClient) -> datetime:
    """
    Timestamp do último `sp_sync_log` com status='success'. Se nunca rodou,
    devolve epoch (1970-01-01Z) — força um full sweep na primeira execução.
    """
    result = (
        client.table("sp_sync_log")
        .select("completed_at")
        .eq("status", "success")
        .order("completed_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = getattr(result, "data", None) or []
    if not rows or not rows[0].get("completed_at"):
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    return _parse_ts(rows[0]["completed_at"])


def fetch_changes_since(
    client: SupabaseClient, since: datetime, limit: int = 1000
) -> list[dict[str, Any]]:
    """
    Docs em `sp_index` com `updated_at > since`, ordenados asc por updated_at.
    Retorna dicts crus — o caller mapeia para `ChangeEntry`.
    """
    result = (
        client.table("sp_index")
        .select("doc_id, doc_path, doc_name, file_ext, drive_id, updated_at, metadata")
        .gt("updated_at", since.isoformat())
        .order("updated_at", desc=False)
        .limit(limit)
        .execute()
    )
    return list(getattr(result, "data", None) or [])


def fetch_active_routing_rules(client: SupabaseClient) -> list[dict[str, Any]]:
    """Todas as rules com `active=TRUE`, ordenadas por id para replay determinístico."""
    result = (
        client.table("sp_routing_rules")
        .select(
            "id, rule_name, path_pattern, file_ext_pattern, name_pattern, "
            "target_agents, doc_type, priority, active"
        )
        .eq("active", True)
        .order("id", desc=False)
        .execute()
    )
    return list(getattr(result, "data", None) or [])


def insert_feed_entries(
    client: SupabaseClient, rows: list[dict[str, Any]]
) -> int:
    """
    Upsert em `sp_agent_feed`. O índice único parcial `uniq_agent_feed_pending`
    (agent_code, doc_id) WHERE status='pending' impede duplicatas para o
    mesmo agente enquanto a entrada anterior ainda estiver pending.
    Retorna quantas linhas foram efetivamente inseridas/atualizadas.
    """
    if not rows:
        return 0
    result = (
        client.table("sp_agent_feed")
        .upsert(rows, on_conflict="agent_code,doc_id")
        .execute()
    )
    inserted = getattr(result, "data", None) or []
    return len(inserted)


def write_sync_log(client: SupabaseClient, row: dict[str, Any]) -> None:
    """Registra o resultado de um run em `sp_sync_log`."""
    client.table("sp_sync_log").insert(row).execute()


def _parse_ts(value: Any) -> datetime:
    """Aceita ISO string ou datetime; sempre devolve datetime tz-aware."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
