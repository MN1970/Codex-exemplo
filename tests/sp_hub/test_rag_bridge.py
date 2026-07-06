"""Testes de rag_bridge — Noop, HttpRagBridge, QueueRagBridge, factory."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from sp_hub.models import ChangeEntry, Priority, RoutingDecision
from sp_hub.rag_bridge import (
    HttpRagBridge,
    NoopRagBridge,
    QueueRagBridge,
    build_default_rag_bridge,
)


def _decision():
    entry = ChangeEntry(
        doc_id="doc-1",
        doc_path="02_CLIENTE/CCR/04_PROJETO/x.dwg",
        doc_name="x.dwg",
        file_ext="dwg",
        updated_at=datetime.now(timezone.utc),
    )
    return RoutingDecision(
        doc=entry,
        target_agents=["M3"],
        doc_type="projeto",
        priority=Priority.ALTA,
        matched_rules=["cliente_projeto"],
    )


def test_noop_never_raises():
    NoopRagBridge().trigger_ingest(_decision())


def test_queue_bridge_inserts_row(fake_client):
    bridge = QueueRagBridge(fake_client)
    bridge.trigger_ingest(_decision())
    rows = fake_client.tables.get("rag_ingest_queue", [])
    assert len(rows) == 1
    assert rows[0]["doc_id"] == "doc-1"
    assert rows[0]["priority"] == "alta"
    assert rows[0]["metadata"]["target_agents"] == ["M3"]


def test_http_bridge_posts_to_endpoint():
    captured = {}

    class _FakeResp:
        status = 200

        def read(self):
            return b'{"ok":true}'

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["body"] = req.data
        captured["method"] = req.get_method()
        return _FakeResp()

    with patch("sp_hub.rag_bridge.urllib.request.urlopen", _fake_urlopen):
        bridge = HttpRagBridge("https://m18.internal")
        bridge.trigger_ingest(_decision())

    assert captured["url"] == "https://m18.internal/api/ingest"
    assert captured["method"] == "POST"
    assert b'"doc_id": "doc-1"' in captured["body"]


def test_http_bridge_raises_on_non_2xx():
    class _FakeResp:
        status = 500

        def read(self):
            return b"boom"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    with patch("sp_hub.rag_bridge.urllib.request.urlopen", lambda *a, **kw: _FakeResp()):
        bridge = HttpRagBridge("https://m18.internal")
        with pytest.raises(RuntimeError):
            bridge.trigger_ingest(_decision())


def test_factory_returns_noop_when_env_unset(monkeypatch):
    monkeypatch.delenv("SP_HUB_RAG_ENDPOINT", raising=False)
    assert isinstance(build_default_rag_bridge(), NoopRagBridge)


def test_factory_returns_http_when_env_set(monkeypatch):
    monkeypatch.setenv("SP_HUB_RAG_ENDPOINT", "https://m18.internal")
    assert isinstance(build_default_rag_bridge(), HttpRagBridge)
