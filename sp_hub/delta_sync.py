"""
Entrypoint da Fase 2 — orquestra:

    sp_index (últimas mudanças)
       ↓
    classify + route (via sp_routing_rules)
       ↓
    upsert em sp_agent_feed
       ↓
    (opcional) rag_bridge.trigger_ingest para priority='alta'
       ↓
    write_sync_log

Rodável direto: `python -m sp_hub.delta_sync`.

Env vars obrigatórias em produção:
    SUPABASE_URL
    SUPABASE_SERVICE_KEY

Env vars opcionais:
    SP_HUB_RAG_ENDPOINT     — URL do Manta 18 (se ausente, RAG bridge é no-op).
    SP_HUB_DELTA_LIMIT      — máximo de docs processados por run (default: 1000).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from sp_hub.db import (
    SupabaseClient,
    fetch_active_routing_rules,
    fetch_changes_since,
    insert_feed_entries,
    last_successful_sync_at,
    supabase_client,
    write_sync_log,
)
from sp_hub.feed import decisions_to_feed
from sp_hub.models import ChangeEntry, Priority, RoutingDecision, SyncResult
from sp_hub.rag_bridge import RagBridge, build_default_rag_bridge
from sp_hub.router import parse_rules, route

log = logging.getLogger("sp_hub.delta_sync")


def run_delta_sync(
    client: SupabaseClient,
    *,
    rag_bridge: RagBridge | None = None,
    delta_limit: int | None = None,
) -> SyncResult:
    """
    Uma iteração completa do delta sync. Idempotente: rodar duas vezes seguidas
    sem novas mudanças deve produzir zero inserts na segunda (upsert é no-op).
    """
    started = datetime.now(timezone.utc)
    result = SyncResult(started_at=started)

    limit = delta_limit or int(os.environ.get("SP_HUB_DELTA_LIMIT", "1000"))
    if rag_bridge is None:
        rag_bridge = build_default_rag_bridge()

    try:
        since = last_successful_sync_at(client)
        log.info("delta_sync starting; since=%s limit=%d", since.isoformat(), limit)

        rule_rows = fetch_active_routing_rules(client)
        rules = parse_rules(rule_rows)
        log.info("loaded %d active routing rules", len(rules))

        change_rows = fetch_changes_since(client, since, limit=limit)
        result.changes_detected = len(change_rows)
        log.info("detected %d changes in sp_index", result.changes_detected)

        decisions: list[RoutingDecision] = []
        for row in change_rows:
            try:
                entry = _row_to_entry(row)
            except (KeyError, ValueError) as err:
                result.errors.append(f"parse_entry:{err}")
                continue
            decisions.append(route(entry, rules))

        feed_entries = decisions_to_feed(decisions)
        feed_rows = [f.to_row() for f in feed_entries]

        if feed_rows:
            inserted = insert_feed_entries(client, feed_rows)
            result.feed_entries_inserted = inserted
            log.info("upserted %d feed entries", inserted)

        high_priority = [d for d in decisions if d.priority == Priority.ALTA and d.has_targets]
        for decision in high_priority:
            try:
                rag_bridge.trigger_ingest(decision)
                result.rag_ingests_triggered += 1
            except Exception as err:  # noqa: BLE001 — best-effort
                result.errors.append(f"rag_ingest:{decision.doc.doc_id}:{err}")

    except Exception as err:  # noqa: BLE001 — captura pra registrar no log
        result.errors.append(f"fatal:{err}")
        log.exception("delta_sync failed")
    finally:
        result.completed_at = datetime.now(timezone.utc)
        try:
            write_sync_log(client, result.to_log_row())
        except Exception as err:  # noqa: BLE001
            log.warning("failed to write sp_sync_log: %s", err)

    log.info("delta_sync done: %s", result.summary())
    return result


def _row_to_entry(row: dict) -> ChangeEntry:
    updated = row.get("updated_at")
    if isinstance(updated, str):
        parsed = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    elif isinstance(updated, datetime):
        parsed = updated if updated.tzinfo else updated.replace(tzinfo=timezone.utc)
    else:
        parsed = datetime.now(timezone.utc)

    return ChangeEntry(
        doc_id=str(row["doc_id"]),
        doc_path=str(row["doc_path"]),
        doc_name=str(row["doc_name"]),
        file_ext=(row.get("file_ext") or None),
        drive_id=row.get("drive_id"),
        updated_at=parsed,
        metadata=dict(row.get("metadata") or {}),
    )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    client = supabase_client()
    result = run_delta_sync(client)
    print(result.summary())
    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
