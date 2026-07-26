"""
app.py — Ponto de entrada do Manta Backend (FastAPI, async).

Roda em: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
Docs em: http://localhost:8000/docs (Swagger) e /redoc (ReDoc)
"""
import logging
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db import init_models
from pg_pool import close_pool, create_pool
from mcp.client import MCPClient
from mcp.integration import MCPServer, build_default_registry, build_remote_clients
from mcp.integration import router as mcp_router
from routers import admin, agents, executor, feedback, rag, routing
from routers import auth as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manta.app")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia recursos de longa duração: pool async Postgres e
    ClientSession aiohttp compartilhada (reuso de conexões TCP para
    chamadas ao gateway MCP e a serviços externos)."""
    logger.info("startup: %s v%s (%s)", settings.app_name, settings.app_version, settings.environment)

    app.state.db_pool = await create_pool()

    # Garante o schema de documentos do Knowledge Hub (rag_documents +
    # colunas novas em rag_chunks). Best-effort — não derruba o startup
    # se o Postgres ainda não estiver acessível (ver rag.ensure_schema).
    await rag.ensure_schema(app.state.db_pool)

    try:
        # Cria as tabelas de auth (users/roles/organizations/...) se não
        # existirem. Best-effort: em produção prefira migrations
        # (Alembic); se o Postgres não estiver acessível ainda, não
        # derruba a app — os endpoints de /auth responderão com erro no
        # primeiro uso, igual ao pool asyncpg em database.py.
        await init_models()
    except Exception:  # noqa: BLE001 - queremos degradar, não derrubar
        logger.warning("auth: não foi possível criar/verificar as tabelas de autenticação no startup.")

    http_session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.mcp_request_timeout_seconds)
    )
    app.state.http_session = http_session
    app.state.mcp_client = MCPClient(
        base_url=settings.mcp_gateway_url,
        timeout_seconds=settings.mcp_request_timeout_seconds,
        session=http_session,
    )

    # MCP server + client multi-remoto (GitHub/Supabase/MS365) — ver
    # mcp/integration.py. Reaproveita a mesma http_session (sem abrir
    # novas conexões TCP por request).
    mcp_registry = build_default_registry()
    mcp_remote_clients = build_remote_clients(http_session)
    app.state.mcp_server = MCPServer(mcp_registry, mcp_remote_clients)

    yield

    logger.info("shutdown: encerrando pool e sessões HTTP")
    await close_pool(app.state.db_pool)
    await app.state.mcp_client.close()
    if not http_session.closed:
        await http_session.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API do Manta Maestro — orquestração dos 20 agentes IA da Manta "
        "Associados (horizontais, verticais por segmento e ciclo de vida), "
        "RAG semântico via Supabase pgvector e roteamento por intake Q1."
    ),
    lifespan=lifespan,
    openapi_tags=[
        {"name": "agents", "description": "Registro dos agentes (Eixos 1, 2 e 3)."},
        {"name": "rag", "description": "Coleções RAG e busca semântica (pgvector)."},
        {"name": "routing", "description": "Motor de roteamento do Maestro (Q1 do intake)."},
        {"name": "feedback", "description": "Feedback de uso dos agentes."},
        {"name": "admin", "description": "Health check, checklist de deploy e auth de dev."},
        {"name": "mcp", "description": "MCP server (tools do Manta) + MCP client (GitHub/Supabase/MS365)."},
        {"name": "auth", "description": "Registro, login, refresh, perfil e organizações (JWT RS256 + RBAC multi-org)."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(executor.router)
app.include_router(rag.router)
app.include_router(routing.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(mcp_router)
app.include_router(auth_router.router)


@app.get("/", tags=["admin"], summary="Root — status básico da API")
async def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=settings.debug)
