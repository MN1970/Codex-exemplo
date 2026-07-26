"""
test_connection.py — Smoke test de conectividade e schema do Postgres
(SQLAlchemy async + pgvector + RLS multi-org, ver `database.py` e
`alembic/versions/`).

Uso:

    python test_connection.py        # roda como script, imprime relatório
    pytest test_connection.py -v     # roda como suíte (pytest-asyncio)

Pré-requisito: `alembic upgrade head` já rodado contra `DATABASE_URL`
(ver config.py/.env) — este script SÓ verifica, não cria schema.

Não depende de fixtures externas: os dados de teste (2 organizações +
2 agentes) são criados e sempre desfeitos com ROLLBACK dentro da mesma
sessão — seguro para rodar contra um banco com dados reais, nada fica
persistido.
"""
from __future__ import annotations

import asyncio
import sys
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select, text

from database import (
    Agent,
    SessionLocal,
    create_organization,
    engine,
    set_org_context,
)

EXPECTED_TABLES = {
    "organizations",
    "roles",
    "users",
    "agents",
    "rag_chunks",
    "sessions",
    "feedback",
    "ml_models",
}

# Tabelas que a migration 0003 deve ter deixado com RLS habilitada e
# forçada (inclusive para o dono da tabela).
EXPECTED_RLS_TABLES = {"organizations", "agents", "rag_chunks", "sessions", "feedback", "ml_models"}


async def _connect_ok() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


async def _pgvector_extension_installed() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
        assert result.first() is not None, (
            "extensão 'vector' não encontrada — rode `alembic upgrade head` "
            "(migration 0001_pgvector_extension)"
        )


async def _expected_tables_exist() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        found = {row[0] for row in result}
        missing = EXPECTED_TABLES - found
        assert not missing, f"tabelas ausentes: {missing} — rode `alembic upgrade head`"


async def _ivfflat_index_exists() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE tablename = 'rag_chunks' AND indexname = 'ix_rag_chunks_embedding_ivfflat'"
            )
        )
        row = result.first()
        assert row is not None, "índice IVFFlat de rag_chunks.embedding não encontrado"
        assert "ivfflat" in row[0].lower(), f"índice encontrado mas não é IVFFlat: {row[0]!r}"


async def _rls_enabled_and_forced() -> None:
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = ANY(:names)"
            ),
            {"names": list(EXPECTED_RLS_TABLES)},
        )
        rows = {r[0]: (r[1], r[2]) for r in result}
        missing = EXPECTED_RLS_TABLES - rows.keys()
        assert not missing, f"tabelas não encontradas para checar RLS: {missing}"
        not_enabled = {t for t, (enabled, _forced) in rows.items() if not enabled}
        not_forced = {t for t, (_enabled, forced) in rows.items() if not forced}
        assert not not_enabled, f"RLS não habilitada em: {not_enabled} — rode a migration 0003_rls_policies"
        assert not not_forced, f"RLS não forçada (dono ainda bypassa) em: {not_forced}"


async def _rls_isolation_roundtrip() -> None:
    """Cria 2 orgs + 1 agent cada, confirma que a RLS (com o contexto
    certo) só devolve o agent da própria org — e desfaz tudo com
    ROLLBACK ao final, mesmo se as asserções falharem.

    Usa `create_organization()` (não `Organization(...)` direto) para
    cada uma das 2 orgs — ver a docstring dessa função em database.py
    sobre por que a criação da organização precisa setar o contexto
    RLS *antes* do insert, ao contrário das demais tabelas.

    A policy de `agents` é `FOR ALL` (mesma condição para
    SELECT/INSERT/UPDATE/DELETE) — diferente de `organizations`, aqui
    o contexto já precisa bater com `org_id` NO MOMENTO DO INSERT, não
    só na leitura. Por isso cada Agent é inserido logo após o
    `set_org_context`/`create_organization` da sua própria org, um de
    cada vez — inserir os dois no mesmo `flush()` com um único
    contexto ativo derrubaria o que estivesse com `org_id` diferente."""
    async with SessionLocal() as session:
        suffix = uuid.uuid4().hex[:8]

        org_a = await create_organization(session, name="Org A (smoke test)", slug=f"smoke-test-org-a-{suffix}")
        agent_a = Agent(org_id=org_a.id, code="Manta 00", slug="maestro", name="Maestro (smoke A)")
        session.add(agent_a)
        await session.flush()

        org_b = await create_organization(session, name="Org B (smoke test)", slug=f"smoke-test-org-b-{suffix}")
        agent_b = Agent(org_id=org_b.id, code="Manta 00", slug="maestro", name="Maestro (smoke B)")
        session.add(agent_b)
        await session.flush()

        try:
            await set_org_context(session, org_a.id)
            visible = (await session.execute(select(Agent).where(Agent.slug == "maestro"))).scalars().all()
            visible_ids = {a.id for a in visible}

            assert agent_a.id in visible_ids, "RLS bloqueou a própria organização (falso negativo)"
            assert agent_b.id not in visible_ids, "RLS vazou dado de outra organização (falha de isolamento!)"
        finally:
            await session.rollback()


CHECKS = [
    ("Conexão básica (SELECT 1)", _connect_ok),
    ("Extensão pgvector instalada", _pgvector_extension_installed),
    ("Tabelas do schema (8 modelos ORM)", _expected_tables_exist),
    ("Índice IVFFlat em rag_chunks.embedding", _ivfflat_index_exists),
    ("RLS habilitada + forçada nas tabelas multi-org", _rls_enabled_and_forced),
    ("Isolamento RLS multi-org (round-trip, com rollback)", _rls_isolation_roundtrip),
]


@pytest_asyncio.fixture(autouse=True)
async def _dispose_engine_pool_after_test():
    """`engine` (database.py) é criado uma vez, no import do módulo, e
    suas conexões pooladas ficam presas ao event loop em que foram
    abertas. Sob pytest-asyncio (uma nova event loop por teste, no
    modo default), reusar o mesmo pool no teste seguinte estoura
    `RuntimeError: ... attached to a different loop`. Descartar o pool
    ao final de cada teste força o próximo a abrir conexões novas, já
    na loop certa — sem isso, só o primeiro teste do arquivo passaria."""
    yield
    await engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("label,check", CHECKS)
async def test_database_health(label: str, check) -> None:
    await check()


async def _run_report() -> int:
    print(f"Testando conexão: {engine.url.render_as_string(hide_password=True)}\n")
    failures = 0
    for label, check in CHECKS:
        try:
            await check()
        except Exception as exc:  # noqa: BLE001 - queremos reportar, não propagar
            failures += 1
            print(f"[FALHOU] {label}: {exc}")
        else:
            print(f"[OK]     {label}")

    print()
    if failures:
        print(f"{failures} verificação(ões) falharam.")
    else:
        print("Todas as verificações passaram.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_run_report()))
