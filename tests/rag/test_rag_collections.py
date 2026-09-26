"""
Testes de RAG — em duas camadas:

1. Consistência estática (sempre roda, sem rede/secrets):
   `tests/rag/collections.yaml` <-> tabela "RAG — Coleções em Supabase"
   do CLAUDE.md <-> `supabase/migrations/*.sql`. Pega o caso comum de
   alguém adicionar uma coleção num lugar e esquecer os outros dois.

2. Verificação live contra o Supabase (só roda se
   SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY estiverem configurados):
   confirma que a coleção existe em `rag_collections` com o
   `storage_prefix` esperado e, se `min_chunks > 0`, que há pelo menos
   essa quantidade de chunks indexados.

   Se as tabelas ainda não existirem (migração candidata em
   supabase/migrations/ ainda não aplicada — ver "DEPLOY CHECKLIST
   v4.2" no CLAUDE.md), o teste é SKIPADO com um aviso claro em vez de
   falhar: isso é lacuna de infraestrutura, não regressão de código.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest
import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.agent_loader import CLAUDE_MD, REPO_ROOT  # noqa: E402

pytestmark = pytest.mark.rag

RAG_DIR = Path(__file__).resolve().parent
COLLECTIONS_YAML = RAG_DIR / "collections.yaml"
MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
REQUIRE_RAG_LIVE = os.environ.get("REQUIRE_RAG_LIVE_TESTS", "").lower() in {"1", "true", "yes"}

# Casa linhas da tabela "RAG — Coleções em Supabase" no CLAUDE.md, ex:
# | saneamento | san: | SNIS, IWA, ... | 🆕 v4.2 |
CLAUDE_MD_RAG_ROW_RE = re.compile(
    r"^\|\s*([\w-]+)\s*\|\s*([\w:]+:)\s*\|", re.MULTILINE
)


def _load_collections() -> list[dict]:
    data = yaml.safe_load(COLLECTIONS_YAML.read_text(encoding="utf-8"))
    return data["collections"]


COLLECTIONS = _load_collections()
COLLECTION_IDS = [c["name"] for c in COLLECTIONS]


def _claude_md_rag_table_section() -> str:
    text = CLAUDE_MD.read_text(encoding="utf-8")
    marker = "## RAG — Coleções em Supabase"
    start = text.find(marker)
    assert start != -1, "Seção '## RAG — Coleções em Supabase' não encontrada no CLAUDE.md"
    end = text.find("\n## ", start + len(marker))
    return text[start: end if end != -1 else None]


def _migrations_text() -> str:
    if not MIGRATIONS_DIR.exists():
        return ""
    return "\n".join(p.read_text(encoding="utf-8") for p in MIGRATIONS_DIR.glob("*.sql"))


# ---------------------------------------------------------------------
# Camada 1 — consistência estática
# ---------------------------------------------------------------------


@pytest.mark.parametrize("collection", COLLECTIONS, ids=COLLECTION_IDS)
def test_collection_documented_in_claude_md(collection):
    section = _claude_md_rag_table_section()
    assert collection["name"] in section, (
        f"Coleção '{collection['name']}' está em tests/rag/collections.yaml "
        "mas não aparece na tabela 'RAG — Coleções em Supabase' do CLAUDE.md."
    )
    assert collection["storage_prefix"] in section, (
        f"Prefixo de storage '{collection['storage_prefix']}' da coleção "
        f"'{collection['name']}' não aparece na tabela do CLAUDE.md — "
        "prefixos divergentes entre registro e código quebram a busca "
        "vetorial por coleção."
    )


@pytest.mark.parametrize("collection", COLLECTIONS, ids=COLLECTION_IDS)
def test_collection_present_in_a_migration_file(collection):
    migrations = _migrations_text()
    assert collection["name"] in migrations and collection["storage_prefix"] in migrations, (
        f"Coleção '{collection['name']}' (prefixo "
        f"'{collection['storage_prefix']}') não é criada por nenhum arquivo "
        f"em {MIGRATIONS_DIR.relative_to(REPO_ROOT)}/*.sql. Toda coleção "
        "declarada precisa de uma migração correspondente (mesmo que ainda "
        "não aplicada em produção)."
    )


def test_no_orphan_collections_in_claude_md():
    """Toda coleção listada no CLAUDE.md também precisa estar em collections.yaml."""
    section = _claude_md_rag_table_section()
    documented = set(CLAUDE_MD_RAG_ROW_RE.findall(section))
    documented_names = {name for name, _prefix in documented if name != "Coleção"}
    known_names = {c["name"] for c in COLLECTIONS}
    dangling = documented_names - known_names
    assert not dangling, (
        f"CLAUDE.md documenta a(s) coleção(ões) {sorted(dangling)} que não "
        "estão em tests/rag/collections.yaml — adicione lá para que o RAG "
        "test cubra a nova coleção."
    )


# ---------------------------------------------------------------------
# Camada 2 — verificação live (opcional, requer secrets)
# ---------------------------------------------------------------------


def _supabase_get(path: str, params: dict) -> requests.Response:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    return requests.get(
        f"{SUPABASE_URL.rstrip('/')}/rest/v1/{path}",
        headers=headers,
        params=params,
        timeout=15,
    )


def _skip_or_fail_missing_creds():
    if SUPABASE_URL and SUPABASE_KEY:
        return
    if REQUIRE_RAG_LIVE:
        pytest.fail(
            "SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY ausentes e "
            "REQUIRE_RAG_LIVE_TESTS=1 — verificação live é obrigatória "
            "neste job/branch."
        )
    pytest.skip(
        "SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configurados — "
        "verificação live do Supabase pulada, mantendo apenas a "
        "consistência estática (registro/CLAUDE.md/migrações)."
    )


@pytest.mark.parametrize("collection", COLLECTIONS, ids=COLLECTION_IDS)
def test_collection_exists_in_supabase(collection):
    _skip_or_fail_missing_creds()

    try:
        resp = _supabase_get(
            "rag_collections",
            {"slug": f"eq.{collection['name']}", "select": "slug,storage_prefix"},
        )
    except requests.RequestException as exc:
        pytest.fail(f"Falha de rede consultando Supabase: {exc}")

    if resp.status_code == 404 or (
        resp.status_code >= 400 and "rag_collections" in resp.text and "does not exist" in resp.text.lower()
    ):
        pytest.skip(
            "Tabela 'rag_collections' ainda não existe no Supabase — "
            "migração candidata em supabase/migrations/ ainda não foi "
            "aplicada (ver DEPLOY CHECKLIST v4.2 no CLAUDE.md)."
        )

    assert resp.status_code == 200, (
        f"Supabase retornou {resp.status_code} consultando rag_collections: "
        f"{resp.text[:300]}"
    )
    rows = resp.json()
    assert rows, (
        f"Coleção '{collection['name']}' não encontrada na tabela "
        "rag_collections do Supabase (migração ainda não aplicada?)."
    )
    assert rows[0]["storage_prefix"] == collection["storage_prefix"], (
        f"storage_prefix em produção ('{rows[0]['storage_prefix']}') "
        f"diverge do registro local ('{collection['storage_prefix']}')."
    )

    if collection["min_chunks"] > 0:
        count_resp = _supabase_get(
            "rag_chunks",
            {
                "collection": f"eq.{collection['name']}",
                "select": "id",
            },
        )
        assert count_resp.status_code == 200, (
            f"Supabase retornou {count_resp.status_code} consultando "
            f"rag_chunks: {count_resp.text[:300]}"
        )
        n = len(count_resp.json())
        assert n >= collection["min_chunks"], (
            f"Coleção '{collection['name']}' tem {n} chunks indexados, "
            f"mínimo esperado {collection['min_chunks']}."
        )
