#!/usr/bin/env python3
"""
WF-AKP-001 — M18 embedding pipeline (pgvector 768d)

Lê os 52 KEs de `knowledge_extractions` no Supabase manta-maestro,
gera embeddings 768d com `paraphrase-multilingual-mpnet-base-v2`
(mesmo modelo usado em manta_rag_chunks para consistência de retrieval),
e faz upsert em `ke_embeddings`.

Uso:
    export SUPABASE_URL="https://ogxxgvgtulrbbppshjie.supabase.co"
    export SUPABASE_SERVICE_KEY="eyJhbGciOi..."   # service_role
    pip install --break-system-packages sentence-transformers supabase pgvector numpy
    python m18_embeddings.py                       # todos os KEs faltantes
    python m18_embeddings.py --force               # regera todos, mesmo os já embutidos
    python m18_embeddings.py --ke KE-018           # só um KE

Idempotente: pula KEs que já têm embedding a menos que --force.
Modelo (~470MB) é baixado do HuggingFace no primeiro run e cacheado.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIM = 768
BATCH = 16


def _require(env: str) -> str:
    v = os.environ.get(env)
    if not v:
        sys.exit(f"[m18] variável de ambiente {env} obrigatória — abortando.")
    return v


def _client():
    from supabase import create_client
    return create_client(_require("SUPABASE_URL"), _require("SUPABASE_SERVICE_KEY"))


def _pending_kes(sb, force: bool, only: str | None) -> list[dict]:
    """Retorna KEs que ainda precisam de embedding (ou todos se force)."""
    if only:
        rs = sb.table("knowledge_extractions").select(
            "ke_codigo, descricao, tipo, agentes_destino, tese_codigo"
        ).eq("ke_codigo", only).execute()
        return rs.data or []

    if force:
        rs = sb.table("knowledge_extractions").select(
            "ke_codigo, descricao, tipo, agentes_destino, tese_codigo"
        ).execute()
        return rs.data or []

    # KEs sem embedding: LEFT JOIN não é direto no PostgREST; fazemos 2 queries.
    all_kes = sb.table("knowledge_extractions").select("ke_codigo, descricao, tipo, agentes_destino, tese_codigo").execute().data or []
    embedded = {r["ke_codigo"] for r in (sb.table("ke_embeddings").select("ke_codigo").execute().data or [])}
    return [k for k in all_kes if k["ke_codigo"] not in embedded]


def _build_chunk_text(ke: dict) -> str:
    """Texto que vai ser embedado.
    Enriquecemos com tipo/agentes para melhorar o retrieval por lente."""
    agents = " ".join(ke.get("agentes_destino") or [])
    return f"[{ke.get('tipo','?')}] [{agents}] {ke.get('descricao','')}"


def embed(kes: Iterable[dict]) -> list[tuple[str, list[float], str]]:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)
    kes = list(kes)
    texts = [_build_chunk_text(k) for k in kes]
    vectors = model.encode(texts, batch_size=BATCH, normalize_embeddings=True, show_progress_bar=True)
    out = []
    for ke, v, t in zip(kes, vectors, texts):
        assert len(v) == EMBEDDING_DIM, f"dimensão inesperada: {len(v)}"
        out.append((ke["ke_codigo"], v.tolist(), t))
    return out


def upsert(sb, rows: list[tuple[str, list[float], str]]) -> int:
    payload = [
        {"ke_codigo": ke, "embedding": vec, "model": MODEL_NAME, "chunk_text": txt}
        for ke, vec, txt in rows
    ]
    if not payload:
        return 0
    sb.table("ke_embeddings").upsert(payload, on_conflict="ke_codigo").execute()
    return len(payload)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Regera todos os embeddings")
    ap.add_argument("--ke", help="Só processa este ke_codigo")
    args = ap.parse_args()

    sb = _client()
    pending = _pending_kes(sb, args.force, args.ke)
    if not pending:
        print("[m18] nada a fazer — todos os KEs já têm embedding.")
        return 0

    print(f"[m18] {len(pending)} KEs pendentes. Gerando embeddings com {MODEL_NAME}...")
    rows = embed(pending)
    n = upsert(sb, rows)
    print(f"[m18] {n} embeddings upserted em ke_embeddings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
