"""
Testes unitarios do graph_api_wrapper.py — 100% mocked, nenhuma chamada de
rede real e nenhum secret necessario. Simula o cenario de "PR fake" mergeado
(.claude/agents/** alterado) exercitando o pipeline completo em dry-run e
depois com um client fake para o caminho "live".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import graph_api_wrapper as gw  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "sharepoint_deploy.json"


# ---------------------------------------------------------------------------
# resolve_dry_run — o gate de seguranca
# ---------------------------------------------------------------------------

def test_resolve_dry_run_defaults_to_dry_when_no_secrets(monkeypatch):
    for var in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    assert gw.resolve_dry_run(cli_live=True) is True


def test_resolve_dry_run_stays_dry_without_live_flag(monkeypatch):
    monkeypatch.setenv("AZURE_TENANT_ID", "t")
    monkeypatch.setenv("AZURE_CLIENT_ID", "c")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "s")
    assert gw.resolve_dry_run(cli_live=False) is True


def test_resolve_dry_run_goes_live_only_with_flag_and_secrets(monkeypatch):
    monkeypatch.setenv("AZURE_TENANT_ID", "t")
    monkeypatch.setenv("AZURE_CLIENT_ID", "c")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "s")
    assert gw.resolve_dry_run(cli_live=True) is False


# ---------------------------------------------------------------------------
# DeployPlan / config
# ---------------------------------------------------------------------------

def test_plan_loads_10_folders_and_5_uploads():
    plan = gw.DeployPlan.from_file(CONFIG_PATH)
    assert len(plan.all_folder_paths()) == 10
    assert len(plan.agent_folders) == 5
    assert len(plan.project_folders) == 5
    assert len(plan.uploads()) == 5
    # cada upload aponta para um SKILL.md que realmente existe no repo
    for upload in plan.uploads():
        local = REPO_ROOT / upload["upload"]["local_path"]
        assert local.exists(), f"SKILL.md ausente: {local}"


# ---------------------------------------------------------------------------
# GraphAPIClient — folder / upload logic com sessao HTTP falsa
# ---------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, status_code, json_data=None, text="", headers=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._json


class FakeSession:
    """Registra chamadas e devolve respostas programadas em sequencia."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self._responses:
            raise AssertionError(f"Chamada inesperada sem resposta programada: {method} {url}")
        return self._responses.pop(0)


@pytest.fixture
def client_factory(monkeypatch):
    def _make(responses):
        session = FakeSession(responses)
        client = gw.GraphAPIClient("tenant", "client", "secret", session=session)
        monkeypatch.setattr(client, "_acquire_token", lambda: "fake-token")
        return client, session

    return _make


def test_get_site_id_success(client_factory):
    client, session = client_factory([FakeResponse(200, {"id": "site-123"})])
    site_id = client.get_site_id("mnassociados.sharepoint.com", "/sites/Engenharia")
    assert site_id == "site-123"
    assert session.calls[0]["method"] == "GET"
    assert "mnassociados.sharepoint.com:/sites/Engenharia" in session.calls[0]["url"]


def test_get_site_id_failure_raises(client_factory):
    client, _ = client_factory([FakeResponse(404, text="not found")])
    with pytest.raises(gw.GraphAPIError):
        client.get_site_id("bad.host", "/sites/Nope")


def test_ensure_folder_creates_missing_single_segment(client_factory):
    # GET root:/agente-portos -> 404 (nao existe) ; POST children -> 201
    client, session = client_factory([
        FakeResponse(404),
        FakeResponse(201, {"id": "folder-1"}),
    ])
    status = client.ensure_folder("site-1", "agente-portos")
    assert status == "created"
    assert session.calls[0]["method"] == "GET"
    assert session.calls[1]["method"] == "POST"
    assert session.calls[1]["json"]["name"] == "agente-portos"


def test_ensure_folder_idempotent_when_already_exists(client_factory):
    client, session = client_factory([FakeResponse(200, {"id": "folder-1"})])
    status = client.ensure_folder("site-1", "agente-portos")
    assert status == "unchanged"
    assert len(session.calls) == 1  # so o GET, nenhum POST


def test_ensure_folder_nested_path_checks_each_segment(client_factory):
    # "04_IA/Manta-Maestro/agente-portos": 3 segmentos, todos ja existem
    client, session = client_factory([
        FakeResponse(200), FakeResponse(200), FakeResponse(200),
    ])
    status = client.ensure_folder("site-1", "04_IA/Manta-Maestro/agente-portos")
    assert status == "unchanged"
    gets = [c for c in session.calls if c["method"] == "GET"]
    assert len(gets) == 3


def test_ensure_folder_treats_409_as_ok(client_factory):
    client, session = client_factory([FakeResponse(404), FakeResponse(409, text="exists")])
    status = client.ensure_folder("site-1", "agente-portos")
    assert status == "unchanged"


def test_upload_file_puts_content(client_factory, tmp_path):
    local = tmp_path / "SKILL.md"
    local.write_text("# hello", encoding="utf-8")
    client, session = client_factory([FakeResponse(201, {"id": "item-1"})])
    status = client.upload_file("site-1", "agente-portos", local, "SKILL.md")
    assert status == "uploaded"
    call = session.calls[0]
    assert call["method"] == "PUT"
    assert call["url"].endswith("agente-portos/SKILL.md:/content")
    assert call["data"] == b"# hello"


def test_upload_file_failure_raises(client_factory, tmp_path, monkeypatch):
    local = tmp_path / "SKILL.md"
    local.write_text("x", encoding="utf-8")
    monkeypatch.setattr(gw.time, "sleep", lambda _: None)
    # times=4 -> 1 tentativa inicial + 4 retries = 5 respostas 500 antes de desistir
    client, _ = client_factory([FakeResponse(500, text="boom") for _ in range(5)])
    with pytest.raises(gw.GraphAPIError):
        client.upload_file("site-1", "agente-portos", local, "SKILL.md")


def test_retry_recovers_from_throttling(monkeypatch, client_factory):
    client, session = client_factory([
        FakeResponse(429, headers={"Retry-After": "0"}),
        FakeResponse(200, {"id": "site-123"}),
    ])
    monkeypatch.setattr(gw.time, "sleep", lambda _: None)
    site_id = client.get_site_id("host", "/sites/X")
    assert site_id == "site-123"
    assert len(session.calls) == 2


# ---------------------------------------------------------------------------
# run() — orchestration: dry-run path (o que o workflow_dispatch de teste usa)
# ---------------------------------------------------------------------------

def test_run_dry_run_plans_all_10_folders_and_5_uploads():
    plan = gw.DeployPlan.from_file(CONFIG_PATH)
    report = gw.run(plan, client=None, dry_run=True, repo_root=REPO_ROOT)

    assert report["ok"] is True
    assert report["dry_run"] is True
    folder_actions = [r for r in report["results"] if r["action"] == "ensure_folder"]
    upload_actions = [r for r in report["results"] if r["action"] == "upload_file"]
    assert len(folder_actions) == 10
    assert len(upload_actions) == 5
    assert all(r["status"] == "dry-run" for r in report["results"])


class FakeGraphClient:
    """Stub do client real — usado para testar run() no caminho 'live' sem rede."""

    def __init__(self):
        self.ensured = []
        self.uploaded = []

    def get_site_id(self, hostname, path):
        return "site-xyz"

    def ensure_folder(self, site_id, path):
        assert site_id == "site-xyz"
        self.ensured.append(path)
        return "created"

    def upload_file(self, site_id, remote_folder, local_path, remote_name):
        assert site_id == "site-xyz"
        assert local_path.exists()
        self.uploaded.append((remote_folder, remote_name))
        return "uploaded"


def test_run_live_path_with_fake_client_creates_everything():
    plan = gw.DeployPlan.from_file(CONFIG_PATH)
    fake_client = FakeGraphClient()
    report = gw.run(plan, client=fake_client, dry_run=False, repo_root=REPO_ROOT)

    assert report["ok"] is True
    assert len(fake_client.ensured) == 10
    assert len(fake_client.uploaded) == 5
    assert ("04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos", "SKILL.md") in fake_client.uploaded


def test_run_live_path_raises_if_local_skill_md_missing(tmp_path):
    bad_config = {
        "site_hostname": "h", "site_path": "/sites/x", "drive_name": "d",
        "agent_folders": [{
            "slug": "x", "sp_path": "x",
            "upload": {"local_path": "does/not/exist/SKILL.md", "remote_name": "SKILL.md"},
        }],
        "project_folders": [],
    }
    cfg_path = tmp_path / "plan.json"
    cfg_path.write_text(json.dumps(bad_config), encoding="utf-8")
    plan = gw.DeployPlan.from_file(cfg_path)
    with pytest.raises(gw.GraphAPIError):
        gw.run(plan, client=FakeGraphClient(), dry_run=False, repo_root=REPO_ROOT)


# ---------------------------------------------------------------------------
# main() — CLI end-to-end em dry-run (simula a chamada feita pelo workflow)
# ---------------------------------------------------------------------------

def test_main_cli_dry_run_end_to_end(tmp_path, monkeypatch, capsys):
    report_out = tmp_path / "deploy-report.json"
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)

    exit_code = gw.main([
        "--config", str(CONFIG_PATH),
        "--repo-root", str(REPO_ROOT),
        "--report-out", str(report_out),
        "--dry-run",
    ])

    assert exit_code == 0
    report = json.loads(report_out.read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["dry_run"] is True
    assert len(report["folders_planned"]) == 10
    assert len(report["uploads_planned"]) == 5


def test_main_cli_live_flag_without_secrets_falls_back_to_dry_run(tmp_path, monkeypatch):
    """Mesmo pedindo --live, sem secrets no ambiente o script tem que
    recusar ir 'ao vivo' — este é o comportamento que torna seguro rodar
    o workflow num PR fake / repo sem credenciais configuradas."""
    report_out = tmp_path / "deploy-report.json"
    monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
    monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)

    exit_code = gw.main([
        "--config", str(CONFIG_PATH),
        "--repo-root", str(REPO_ROOT),
        "--report-out", str(report_out),
        "--live",
    ])

    assert exit_code == 0
    report = json.loads(report_out.read_text(encoding="utf-8"))
    assert report["dry_run"] is True
