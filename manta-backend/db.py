"""
db.py — Engine e sessão async SQLAlchemy para autenticação (models.py).

Este módulo é independente do pool asyncpg "cru" usado pelos demais
routers (database.py) — os modelos de auth (User/Role/Organization/...)
são ORM porque precisam de relacionamentos, constraints e migrations
de forma mais ergonômica do que o pool asyncpg oferece.

`DATABASE_URL` continua sendo a mesma fonte de verdade (config.py);
aqui apenas normalizamos o DSN para o driver async do SQLAlchemy
(`postgresql+asyncpg://`). Em testes, os módulos de teste sobrescrevem
`get_session` via `app.dependency_overrides` apontando para SQLite
in-memory (`aiosqlite`), então nenhuma conexão real de Postgres é
necessária para rodar a suíte.
"""
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import get_settings
from models import Base

settings = get_settings()


def to_async_dsn(dsn: str) -> str:
    """Normaliza um DSN síncrono (`postgresql://`, `postgres://`) para o
    driver assíncrono `asyncpg` usado pelo SQLAlchemy. DSNs que já
    especificam driver (`postgresql+asyncpg://`, `sqlite+aiosqlite://`
    etc.) passam intactos."""
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    if dsn.startswith("postgres://"):
        return dsn.replace("postgres://", "postgresql+asyncpg://", 1)
    return dsn


engine: AsyncEngine = create_async_engine(to_async_dsn(settings.database_url), pool_pre_ping=True, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_models() -> None:
    """Cria as tabelas se não existirem. Uso: dev local e testes.
    Produção deve usar migrations (Alembic) contra o DSN real."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependency FastAPI: uma `AsyncSession` por request, fechada ao final."""
    async with SessionLocal() as session:
        yield session
