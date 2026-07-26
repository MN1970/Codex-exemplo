"""
tests/conftest.py — Fixtures pytest para a suíte de autenticação.

Estratégia: cada teste roda contra um banco SQLite *em memória*
(via `aiosqlite`), criado do zero a partir de `models.Base.metadata` —
não depende de Postgres nem de rede. O schema é o mesmo (SQLAlchemy
ORM) usado em produção; a única coisa trocada é o driver do engine.

`db.get_session` (a dependency real usada por `auth.py` e
`routers/auth.py`) é sobrescrita via `app.dependency_overrides` para
apontar para esse engine de teste — o código de produção sob teste é
exatamente o mesmo, só o banco por trás é outro.
"""
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import models
from auth import OrgContext, require_roles
from db import get_session
from routers.auth import router as auth_router


@pytest_asyncio.fixture
async def engine():
    """Engine SQLite in-memory único por teste. `StaticPool` garante que
    todas as conexões (mesmo em código async) enxerguem o MESMO banco em
    memória — sem isso, cada nova conexão sqlite `:memory:` seria um
    banco vazio independente."""
    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    async with eng.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncIterator[AsyncSession]:
    """Sessão direta para os testes montarem fixtures (ex.: usuário já
    pertencendo a duas organizações) que não são alcançáveis só pelos
    endpoints públicos de /auth."""
    async with session_factory() as session:
        yield session


@pytest.fixture
def test_app(session_factory) -> FastAPI:
    """App FastAPI mínimo com o router real de auth + uma rota
    protegida só-de-teste, usada para exercitar `require_roles` (RBAC)
    ponta a ponta via HTTP (não apenas chamando a função Python)."""
    app = FastAPI()
    app.include_router(auth_router)

    @app.get("/protegido/somente-owner")
    async def owner_only(ctx: OrgContext = Depends(require_roles("owner"))):
        return {"org_id": ctx.org_id, "org_name": ctx.org_name, "roles": ctx.roles}

    @app.get("/protegido/admin-ou-owner")
    async def admin_or_owner(ctx: OrgContext = Depends(require_roles("owner", "admin"))):
        return {"org_id": ctx.org_id, "roles": ctx.roles}

    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    return app


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
