#!/usr/bin/env python3
"""
Audit dos templates declarados nos agent-libraries versus o que existe no SharePoint.

Cada arquivo agent-libraries/*.md declara templates (ex: CLM-M-001..005). Este
script varre `04_IA/Manta-Maestro/Modelos/<Agente>/` e reporta:
    - templates existentes que casam com os IDs declarados
    - templates declarados que não existem (a criar)
    - arquivos existentes que ninguém referencia (candidatos a documentar ou remover)

Uso:
    export SP_TENANT_ID="..."
    export SP_CLIENT_ID="..."
    export SP_CLIENT_SECRET="..."
    export SP_SITE_ID="mantaassociados.sharepoint.com,{site},{web}"
    export SP_DRIVE_NAME="Documentos"
    pip install --break-system-packages msal httpx pyyaml
    python sp_audit.py --libraries ../../agent-libraries/ --report sp-audit.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

TEMPLATE_LINE = re.compile(r"\|\s*([A-Z]{2,4}-M-\d{3})\s*\|", re.M)
MODEL_ROOT = "04_IA/Manta-Maestro/Modelos"

# Mapeamento arquivo → subpasta esperada no SP.
# (Extraído dos cabeçalhos "Modelos/<Agente>/" nos próprios .md.)
AGENT_TO_FOLDER = {
    "01-claims":        "Claims",
    "02-contratual":    "Contratual",
    "05-orcamento":     "Orcamento",
    "07-cronograma":    "Cronograma",
    "04-imobiliario":   "Imobiliario",
    "06-modelagem":     "Modelagem",
    "13-bd":            "BusinessDev",
    "14-apresentacoes": "Apresentacoes",
    "15-advisory":      "Advisory",
    "16-arquiteto-ia":  "Arquiteto-IA",
}


def _env(k: str) -> str:
    v = os.environ.get(k)
    if not v:
        sys.exit(f"[sp_audit] {k} obrigatória — abortando.")
    return v


def acquire_token() -> str:
    import msal
    app = msal.ConfidentialClientApplication(
        client_id=_env("SP_CLIENT_ID"),
        client_credential=_env("SP_CLIENT_SECRET"),
        authority=f"https://login.microsoftonline.com/{_env('SP_TENANT_ID')}",
    )
    r = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in r:
        raise RuntimeError(f"[sp_audit] falha OAuth: {r.get('error_description', r)}")
    return r["access_token"]


def parse_declared(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8")
    return sorted(set(TEMPLATE_LINE.findall(text)))


def list_sp_folder(client, drive_id: str, path: str) -> list[dict]:
    try:
        r = client.get(f"/drives/{drive_id}/root:/{path}:/children")
        r.raise_for_status()
        return r.json()["value"]
    except Exception as e:
        return [{"_error": str(e)}]


def resolve_drive(client, site_id: str, drive_name: str) -> str:
    r = client.get(f"/sites/{site_id}/drives")
    r.raise_for_status()
    for d in r.json()["value"]:
        if d["name"] == drive_name:
            return d["id"]
    raise RuntimeError(f"[sp_audit] drive '{drive_name}' não encontrado")


def main() -> int:
    import httpx
    ap = argparse.ArgumentParser()
    ap.add_argument("--libraries", required=True, help="Diretório agent-libraries/")
    ap.add_argument("--report", default="sp-audit.json")
    args = ap.parse_args()

    lib_dir = Path(args.libraries)
    token = acquire_token()
    client = httpx.Client(
        base_url="https://graph.microsoft.com/v1.0",
        headers={"Authorization": f"Bearer {token}"},
        timeout=60.0,
    )
    drive_id = resolve_drive(client, _env("SP_SITE_ID"), os.environ.get("SP_DRIVE_NAME", "Documentos"))
    report: dict = {}

    for md in sorted(lib_dir.glob("*.md")):
        if md.name in ("README.md",):
            continue
        agent_slug = md.stem
        subfolder = AGENT_TO_FOLDER.get(agent_slug)
        if not subfolder:
            continue
        declared = set(parse_declared(md))
        sp_items = list_sp_folder(client, drive_id, f"{MODEL_ROOT}/{subfolder}")
        sp_names = {i.get("name", "") for i in sp_items if "_error" not in i}
        # Match: um item SP cujo nome contenha o ID declarado
        matched = {d: [n for n in sp_names if d in n] for d in declared}
        missing = [d for d, hits in matched.items() if not hits]
        orphan  = [n for n in sp_names if not any(d in n for d in declared)]
        report[agent_slug] = {
            "declared":   sorted(declared),
            "sp_folder":  f"{MODEL_ROOT}/{subfolder}",
            "sp_items":   sorted(sp_names),
            "matched":    matched,
            "missing":    missing,
            "orphan":     orphan,
        }
        status = "OK" if not missing else f"MISSING {len(missing)}"
        print(f"[sp_audit] {agent_slug:22} declared={len(declared)} sp={len(sp_names)} {status}")

    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[sp_audit] relatório em {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
