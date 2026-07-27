#!/usr/bin/env python3
"""
graph_api_wrapper.py — Manta Maestro / Codex-exemplo

Cria pastas e faz upload de arquivos no SharePoint via Microsoft Graph API,
usando client-credentials (app-only) auth. Desenhado para ser chamado pelo
workflow `.github/workflows/deploy-skillmd.yml` no merge de PRs que tocam
`.claude/agents/**`.

Referencia do plano de pastas/uploads: docs/DEPLOY-v4.2.md secao 3 e
config/sharepoint_deploy.json.

SEGURANCA / GATE HUMANO
------------------------
Este script roda em modo --dry-run por padrao. Ele só faz chamadas de rede
reais quando TODAS as condicoes abaixo forem verdadeiras:
  1. as 4 variaveis de ambiente AZURE_TENANT_ID, AZURE_CLIENT_ID,
     AZURE_CLIENT_SECRET e SP_SITE_HOSTNAME (ou config) estao presentes; e
  2. a flag --live é passada explicitamente.
Sem isso, o script sempre cai em dry-run e apenas imprime o plano —
nunca falha silenciosamente para "esquecer" e acabar rodando ao vivo.
Isso reflete o item do CLAUDE.md/DEPLOY-v4.2.md: "Gate humano: aprovacao
MN antes de [ir para producao]".

Uso:
    python scripts/graph_api_wrapper.py --config config/sharepoint_deploy.json --dry-run
    python scripts/graph_api_wrapper.py --config config/sharepoint_deploy.json --live
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - exercised only when dependency missing
    requests = None  # type: ignore[assignment]

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("graph_api_wrapper")


class GraphAPIError(RuntimeError):
    pass


@dataclass
class DeployPlan:
    site_hostname: str
    site_path: str
    drive_name: str
    agent_folders: list[dict[str, Any]] = field(default_factory=list)
    project_folders: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "DeployPlan":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            site_hostname=data["site_hostname"],
            site_path=data["site_path"],
            drive_name=data.get("drive_name", "Documentos Compartilhados"),
            agent_folders=data.get("agent_folders", []),
            project_folders=data.get("project_folders", []),
        )

    def all_folder_paths(self) -> list[str]:
        paths = [f["sp_path"] for f in self.agent_folders]
        paths += [f["sp_path"] for f in self.project_folders]
        return paths

    def uploads(self) -> list[dict[str, Any]]:
        return [f for f in self.agent_folders if "upload" in f]


def retry(times: int = 4, base_delay: float = 1.0):
    """Retry decorator with exponential backoff, honouring Retry-After on 429."""

    def decorator(fn):
        def wrapped(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except GraphThrottled as exc:
                    attempt += 1
                    if attempt > times:
                        raise GraphAPIError(
                            f"Esgotadas {times} tentativas apos throttling"
                        ) from exc
                    delay = exc.retry_after or (base_delay * (2 ** (attempt - 1)))
                    log.warning(
                        "429 throttled, retry %s/%s em %.1fs", attempt, times, delay
                    )
                    time.sleep(delay)
                except GraphTransientError as exc:
                    attempt += 1
                    if attempt > times:
                        raise GraphAPIError(
                            f"Esgotadas {times} tentativas apos erro transiente"
                        ) from exc
                    delay = base_delay * (2 ** (attempt - 1))
                    log.warning(
                        "Erro transiente (%s), retry %s/%s em %.1fs",
                        exc, attempt, times, delay,
                    )
                    time.sleep(delay)

        return wrapped

    return decorator


class GraphThrottled(RuntimeError):
    def __init__(self, retry_after: float | None):
        super().__init__("throttled")
        self.retry_after = retry_after


class GraphTransientError(RuntimeError):
    pass


class GraphAPIClient:
    """Thin wrapper around the subset of Microsoft Graph used by this deploy."""

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        session: "requests.Session | None" = None,
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._session = session or (requests.Session() if requests else None)
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    # -- auth -----------------------------------------------------------
    def _acquire_token(self) -> str:
        """Client-credentials token acquisition via MSAL.

        Imported lazily so unit tests can run without msal installed by
        monkeypatching this method directly.
        """
        import msal  # local import: optional dependency, only needed live

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority,
        )
        result = app.acquire_token_for_client(scopes=[GRAPH_SCOPE])
        if "access_token" not in result:
            raise GraphAPIError(
                f"Falha ao obter token: {result.get('error')} "
                f"{result.get('error_description')}"
            )
        return result["access_token"]

    def _headers(self) -> dict[str, str]:
        now = time.time()
        if not self._token or now >= self._token_expires_at:
            self._token = self._acquire_token()
            self._token_expires_at = now + 55 * 60  # tokens last ~60min, refresh early
        return {"Authorization": f"Bearer {self._token}"}

    # -- low level request helper ----------------------------------------
    @retry(times=4)
    def _request(self, method: str, url: str, **kwargs) -> "requests.Response":
        headers = kwargs.pop("headers", {})
        headers.update(self._headers())
        resp = self._session.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            raise GraphThrottled(float(retry_after) if retry_after else None)
        if resp.status_code >= 500:
            raise GraphTransientError(f"{resp.status_code} {resp.text[:200]}")
        return resp

    # -- site / drive resolution ------------------------------------------
    def get_site_id(self, hostname: str, site_path: str) -> str:
        url = f"{GRAPH_ROOT}/sites/{hostname}:{site_path}"
        resp = self._request("GET", url)
        if resp.status_code != 200:
            raise GraphAPIError(f"Nao encontrou site {hostname}{site_path}: {resp.status_code} {resp.text}")
        return resp.json()["id"]

    # -- folders -----------------------------------------------------------
    def folder_exists(self, site_id: str, path: str) -> bool:
        url = f"{GRAPH_ROOT}/sites/{site_id}/drive/root:/{path}"
        resp = self._request("GET", url)
        return resp.status_code == 200

    def ensure_folder(self, site_id: str, path: str) -> str:
        """Idempotently ensure every segment of `path` exists, return status."""
        segments = [s for s in path.split("/") if s]
        built = ""
        last_status = "unchanged"
        for segment in segments:
            parent = built
            built = f"{built}/{segment}" if built else segment
            if self.folder_exists(site_id, built):
                continue
            create_url = (
                f"{GRAPH_ROOT}/sites/{site_id}/drive/root:/{parent}:/children"
                if parent
                else f"{GRAPH_ROOT}/sites/{site_id}/drive/root/children"
            )
            body = {
                "name": segment,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail",
            }
            resp = self._request("POST", create_url, json=body)
            if resp.status_code not in (200, 201):
                # 409 = someone else created it concurrently -> treat as ok
                if resp.status_code == 409:
                    continue
                raise GraphAPIError(
                    f"Falha ao criar pasta '{built}': {resp.status_code} {resp.text}"
                )
            last_status = "created"
        return last_status

    # -- files -----------------------------------------------------------
    def upload_file(self, site_id: str, remote_folder: str, local_path: Path, remote_name: str | None = None) -> str:
        remote_name = remote_name or local_path.name
        content = local_path.read_bytes()
        url = f"{GRAPH_ROOT}/sites/{site_id}/drive/root:/{remote_folder}/{remote_name}:/content"
        resp = self._request(
            "PUT", url, data=content, headers={"Content-Type": "text/markdown"}
        )
        if resp.status_code not in (200, 201):
            raise GraphAPIError(
                f"Falha ao subir '{remote_name}' para '{remote_folder}': "
                f"{resp.status_code} {resp.text}"
            )
        return "uploaded"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def build_report(plan: DeployPlan, dry_run: bool) -> dict[str, Any]:
    """Compute the full set of actions this run would take (or did take)."""
    return {
        "dry_run": dry_run,
        "site": f"{plan.site_hostname}{plan.site_path}",
        "folders_planned": plan.all_folder_paths(),
        "uploads_planned": [
            {"local": u["upload"]["local_path"], "remote_folder": u["sp_path"],
             "remote_name": u["upload"]["remote_name"]}
            for u in plan.uploads()
        ],
    }


def run(plan: DeployPlan, client: "GraphAPIClient | None", dry_run: bool, repo_root: Path) -> dict[str, Any]:
    report = build_report(plan, dry_run)
    results: list[dict[str, Any]] = []

    if dry_run:
        for path in plan.all_folder_paths():
            results.append({"action": "ensure_folder", "path": path, "status": "dry-run"})
        for u in plan.uploads():
            results.append({
                "action": "upload_file",
                "local": u["upload"]["local_path"],
                "remote_folder": u["sp_path"],
                "status": "dry-run",
            })
        report["results"] = results
        report["ok"] = True
        return report

    assert client is not None
    site_id = client.get_site_id(plan.site_hostname, plan.site_path)
    for path in plan.all_folder_paths():
        status = client.ensure_folder(site_id, path)
        results.append({"action": "ensure_folder", "path": path, "status": status})

    for u in plan.agent_folders:
        if "upload" not in u:
            continue
        local_path = repo_root / u["upload"]["local_path"]
        if not local_path.exists():
            raise GraphAPIError(f"Arquivo local nao encontrado: {local_path}")
        status = client.upload_file(
            site_id, u["sp_path"], local_path, u["upload"]["remote_name"]
        )
        results.append({
            "action": "upload_file",
            "local": str(local_path),
            "remote_folder": u["sp_path"],
            "status": status,
        })

    report["results"] = results
    report["ok"] = all(r["status"] in ("created", "unchanged", "uploaded") for r in results)
    return report


def resolve_dry_run(cli_live: bool) -> bool:
    """Live mode requires --live AND all 3 Azure secrets present. Otherwise dry-run."""
    required = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET"]
    have_all_secrets = all(os.environ.get(v) for v in required)
    return not (cli_live and have_all_secrets)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/sharepoint_deploy.json"))
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--live", action="store_true", help="Faz chamadas reais ao Graph API (requer secrets).")
    parser.add_argument("--dry-run", action="store_true", help="Forca dry-run mesmo com secrets presentes.")
    parser.add_argument("--report-out", type=Path, default=Path("deploy-report.json"))
    args = parser.parse_args(argv)

    plan = DeployPlan.from_file(args.config)

    dry_run = True if args.dry_run else resolve_dry_run(args.live)

    client = None
    if not dry_run:
        if requests is None:
            log.error("Modulo 'requests' nao instalado; nao e possivel rodar em modo live.")
            return 2
        client = GraphAPIClient(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )

    log.info("Modo: %s", "DRY-RUN" if dry_run else "LIVE")
    report = run(plan, client, dry_run, args.repo_root)

    args.report_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Relatorio escrito em %s", args.report_out)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
