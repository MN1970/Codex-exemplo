"""
pg_pool.py — Pool de conexões async Postgres cru (asyncpg), usado pelos
endpoints legados que ainda fazem SQL direto (routers/rag.py,
routers/feedback.py) contra as tabelas bootstrapadas por
`scripts/init.sql` (`rag_chunks`, `agent_feedback`, `sp_agent_routing`).

Este módulo já se chamou `database.py`. Foi renomeado para abrir espaço
para o novo `database.py` — a camada canônica SQLAlchemy (ORM + Alembic
+ RLS multi-org) com os modelos Organization/Agent/RagChunk/Session/
Feedback/MLModel/User/Role. Os dois convivem de propósito enquanto os
routers legados não migram para o ORM:

    pg_pool.py   → pool asyncpg cru, SQL literal, tabelas do init.sql
    database.py  → SQLAlchemy async, modelos ORM, migrations Alembic

O pool é criado no lifespan do FastAPI (ver app.py) e guardado em
app.state.db_pool. Endpoints acessam via a dependency `get_db`, que
devolve uma conexão emprestada do pool para a duração do request.

Se o banco não estiver disponível (ex.: rodando o skeleton sem docker
compose), o pool falha ao conectar e a app ainda sobe — os endpoints
que precisam de DB retornam 503 em vez de derrubar o processo inteiro.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

import asyncpg
from fastapi import Request, HTTPException, status

from config import get_settings

logger = logging.getLogger("manta.pg_pool")

_settings = get_settings()


async def create_pool() -> Optional[asyncpg.Pool]:
    """Cria o pool de conexões. Retorna None se a conexão falhar,
    permitindo que a aplicação suba mesmo sem banco disponível
    (útil em dev/preview do skeleton)."""
    try:
        pool = await asyncpg.create_pool(
            dsn=_settings.database_url,
            min_size=_settings.db_pool_min_size,
            max_size=_settings.db_pool_max_size,
            command_timeout=30,
        )
        logger.info("pg_pool: pool criado com sucesso")
        return pool
    except Exception as exc:  # noqa: BLE001 - queremos degradar, não derrubar
        logger.warning("pg_pool: não foi possível conectar (%s). "
                        "Endpoints dependentes de DB responderão 503.", exc)
        return None


async def close_pool(pool: Optional[asyncpg.Pool]) -> None:
    if pool is not None:
        await pool.close()
        logger.info("pg_pool: pool encerrado")


async def get_db(request: Request) -> AsyncIterator[asyncpg.Connection]:
    """Dependency: empresta uma conexão do pool para o request atual."""
    pool: Optional[asyncpg.Pool] = getattr(request.app.state, "db_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados indisponível no momento.",
        )
    async with pool.acquire() as connection:
        yield connection


@asynccontextmanager
async def acquire_optional(request: Request) -> AsyncIterator[Optional[asyncpg.Connection]]:
    """Variante que não lança 503 — devolve None se o pool não existir.
    Útil em endpoints que têm um caminho de fallback (ex.: rag.py)."""
    pool: Optional[asyncpg.Pool] = getattr(request.app.state, "db_pool", None)
    if pool is None:
        yield None
        return
    async with pool.acquire() as connection:
        yield connection
