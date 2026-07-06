"""Testes do write gateway — sucesso Zapier, falha, audit log."""

from unittest.mock import patch

from sp_hub.models import WriteRequest
from sp_hub.write_gateway import WriteGateway


def _request():
    return WriteRequest(
        drive_id="drv-eng",
        path="/04_IA/outputs/relatorio.pdf",
        content_b64="aGVsbG8=",
        content_type="application/pdf",
        metadata={"origem": "M1", "ticket": "ABC-123"},
    )


def test_write_success_posts_and_audits(fake_client):
    class _Resp:
        status = 200

        def read(self):
            return b'{"file_id":"01KJQ3YI"}'

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    captured = {}

    def _fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["body"] = req.data
        return _Resp()

    gw = WriteGateway(fake_client, webhook_url="https://hooks.zapier.com/write")
    with patch("sp_hub.write_gateway.urllib.request.urlopen", _fake_urlopen):
        result = gw.write(_request())

    assert result.status == "success"
    assert result.zapier_response == {"file_id": "01KJQ3YI"}
    assert captured["url"] == "https://hooks.zapier.com/write"
    assert b'"drive_id": "drv-eng"' in captured["body"]

    logs = [r for r in fake_client.tables.get("sp_sync_log", []) if r["sync_type"] == "write"]
    assert len(logs) == 1
    assert logs[0]["status"] == "success"
    assert logs[0]["metadata"]["drive_id"] == "drv-eng"


def test_write_without_webhook_returns_error(fake_client, monkeypatch):
    monkeypatch.delenv("SP_HUB_ZAPIER_WRITE_WEBHOOK", raising=False)
    gw = WriteGateway(fake_client)
    result = gw.write(_request())
    assert result.status == "error"
    assert "não configurado" in (result.detail or "")

    logs = [r for r in fake_client.tables.get("sp_sync_log", []) if r["sync_type"] == "write"]
    assert logs[0]["status"] == "error"


def test_write_network_error_returns_error_and_audits(fake_client):
    import urllib.error

    def _boom(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    gw = WriteGateway(fake_client, webhook_url="https://hooks.zapier.com/write")
    with patch("sp_hub.write_gateway.urllib.request.urlopen", _boom):
        result = gw.write(_request())

    assert result.status == "error"
    assert "connection refused" in (result.detail or "")


def test_write_non_2xx_returns_error(fake_client):
    class _Resp:
        status = 500

        def read(self):
            return b"internal"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    gw = WriteGateway(fake_client, webhook_url="https://hooks.zapier.com/write")
    with patch("sp_hub.write_gateway.urllib.request.urlopen", lambda *a, **kw: _Resp()):
        result = gw.write(_request())

    assert result.status == "error"
    assert "500" in (result.detail or "")
