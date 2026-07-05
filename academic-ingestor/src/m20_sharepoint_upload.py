#!/usr/bin/env python3
"""
WF-AKP-001 — M20 SharePoint uploader

Faz mirror dos PDFs originais das 36 teses para:
    <SITE>/Documentos/04_IA/Manta-Maestro/Teses/{bloco}/{codigo}.pdf

E copia o INDICE-KEs.md como referência dentro da pasta 04_IA/Manta-Maestro/Teses/.

Uso:
    export SP_TENANT_ID="..."
    export SP_CLIENT_ID="..."
    export SP_CLIENT_SECRET="..."
    export SP_SITE_ID="mantaassociados.sharepoint.com,{site-guid},{web-guid}"
    export SP_DRIVE_NAME="Documentos"       # default do site
    pip install --break-system-packages msal httpx
    python m20_sharepoint_upload.py --catalog ../MASTER-CATALOG.json --pdfs ../pdfs/

Fluxo:
1. OAuth client_credentials → Graph token (App-only, precisa de Sites.ReadWrite.All).
2. Resolve drive_id do SP_DRIVE_NAME dentro do SP_SITE_ID.
3. Cria pastas 04_IA/Manta-Maestro/Teses/{bloco} se não existirem.
4. Para cada tese com PDF local em pdfs/{codigo}.pdf:
    - upload via /drives/{drive-id}/items/{parent-id}:/{codigo}.pdf:/content
    - PDF <4MB = single request; >4MB = upload session (chunked 5MB, retentativa exponencial).
5. Upload do INDICE-KEs.md.
6. Emite relatório JSON com dict[codigo] = {status, url, size_kb, error?}.

Este é o scaffold documentado; a execução real depende de credenciais SP que
não estão nesta sessão. O código foi validado sintaticamente e segue o padrão
do Graph API (msgraph.microsoft.com/v1.0).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

TARGET_ROOT = "04_IA/Manta-Maestro/Teses"
CHUNK_BYTES = 5 * 1024 * 1024  # 5MB — mínimo recomendado pelo Graph
SINGLE_MAX_BYTES = 4 * 1024 * 1024


def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"[m20] {name} obrigatória — abortando.")
    return v


def _acquire_token() -> str:
    """OAuth 2.0 client_credentials via MSAL — App-only, sem UI."""
    import msal
    app = msal.ConfidentialClientApplication(
        client_id=_env("SP_CLIENT_ID"),
        client_credential=_env("SP_CLIENT_SECRET"),
        authority=f"https://login.microsoftonline.com/{_env('SP_TENANT_ID')}",
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"[m20] falha OAuth: {result.get('error_description', result)}")
    return result["access_token"]


class Graph:
    def __init__(self, token: str) -> None:
        import httpx
        self.h = httpx.Client(
            base_url="https://graph.microsoft.com/v1.0",
            headers={"Authorization": f"Bearer {token}"},
            timeout=60.0,
        )

    def get(self, path: str, **kw: Any):
        r = self.h.get(path, **kw)
        r.raise_for_status()
        return r.json()

    def put_raw(self, url: str, content: bytes, headers: dict[str, str]):
        import httpx
        r = httpx.put(url, content=content, headers=headers, timeout=120.0)
        r.raise_for_status()
        return r.json() if r.content else {}


def resolve_drive_id(g: Graph, site_id: str, drive_name: str) -> str:
    drives = g.get(f"/sites/{site_id}/drives")["value"]
    for d in drives:
        if d["name"] == drive_name:
            return d["id"]
    raise RuntimeError(f"[m20] drive '{drive_name}' não encontrado em {site_id}")


def ensure_folder(g: Graph, drive_id: str, path: str) -> str:
    """Cria a pasta se não existe. Retorna o id do item final."""
    parts = [p for p in path.split("/") if p]
    parent = "root"
    for name in parts:
        try:
            child = g.get(f"/drives/{drive_id}/items/{parent}:/{name}")
        except Exception:
            body = {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "replace"}
            r = g.h.post(f"/drives/{drive_id}/items/{parent}/children", json=body)
            r.raise_for_status()
            child = r.json()
        parent = child["id"]
    return parent


def upload_file(g: Graph, drive_id: str, parent_id: str, name: str, path: Path) -> dict:
    size = path.stat().st_size
    if size <= SINGLE_MAX_BYTES:
        with path.open("rb") as f:
            return g.put_raw(
                f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_id}:/{name}:/content",
                f.read(),
                {"Content-Type": "application/octet-stream"},
            )
    # Upload session (chunked)
    r = g.h.post(
        f"/drives/{drive_id}/items/{parent_id}:/{name}:/createUploadSession",
        json={"item": {"@microsoft.graph.conflictBehavior": "replace", "name": name}},
    )
    r.raise_for_status()
    url = r.json()["uploadUrl"]
    with path.open("rb") as f:
        pos = 0
        while pos < size:
            chunk = f.read(CHUNK_BYTES)
            end = pos + len(chunk) - 1
            headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {pos}-{end}/{size}",
            }
            backoff = 1.0
            for attempt in range(4):
                try:
                    g.put_raw(url, chunk, headers)
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    time.sleep(backoff)
                    backoff *= 2
            pos = end + 1
    return {"name": name, "size": size}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True, help="MASTER-CATALOG.json")
    ap.add_argument("--pdfs", required=True, help="Diretório com {codigo}.pdf")
    ap.add_argument("--report", default="m20-upload-report.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    pdf_dir = Path(args.pdfs)

    if args.dry_run:
        print(f"[m20] DRY RUN — {len(catalog['teses'])} teses no catálogo.")
        for t in catalog["teses"]:
            local = pdf_dir / f"{t['id']}.pdf"
            status = "ok" if local.exists() else "MISSING"
            print(f"  {status:8} {t['bloco']}/{t['id']}  <- {local}")
        return 0

    token = _acquire_token()
    g = Graph(token)
    drive_id = resolve_drive_id(g, _env("SP_SITE_ID"), os.environ.get("SP_DRIVE_NAME", "Documentos"))
    report: dict[str, dict] = {}

    for t in catalog["teses"]:
        cod = t["id"]
        bloco = t["bloco"]
        local = pdf_dir / f"{cod}.pdf"
        entry: dict = {"bloco": bloco}
        if not local.exists():
            entry["status"] = "MISSING"
            report[cod] = entry
            continue
        try:
            parent = ensure_folder(g, drive_id, f"{TARGET_ROOT}/{bloco}")
            info = upload_file(g, drive_id, parent, f"{cod}.pdf", local)
            entry.update({"status": "ok", "size_bytes": info.get("size", local.stat().st_size)})
            print(f"[m20] {cod} → {TARGET_ROOT}/{bloco}/{cod}.pdf")
        except Exception as e:
            entry.update({"status": "FAIL", "error": str(e)})
            print(f"[m20] {cod} FAIL: {e}", file=sys.stderr)
        report[cod] = entry

    # INDICE-KEs.md
    indice = Path(args.catalog).parent / "INDICE-KEs.md"
    if indice.exists():
        parent = ensure_folder(g, drive_id, TARGET_ROOT)
        upload_file(g, drive_id, parent, "INDICE-KEs.md", indice)
        report["_INDICE"] = {"status": "ok"}

    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[m20] relatório em {args.report}")
    ok = sum(1 for v in report.values() if v.get("status") == "ok")
    print(f"[m20] {ok}/{len(report)} uploads ok.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
