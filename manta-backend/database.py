"""
database.py — Camada de persistência canônica SQLAlchemy (async, 2.0
style) do Manta Backend: engine, sessão, os 8 modelos ORM pedidos
(Organization, Agent, RagChunk, Session, Feedback, MLModel, User, Role)
e o helper de contexto multi-organização usado pelas RLS policies.

Desenho (multi-tenant simples, sem tabela de associação):

    Organization ──< User >── Role
         │  │  │  │  │
         │  │  │  │  └──< Feedback
         │  │  │  └─────< Session
         │  │  └────────< RagChunk
         │  └───────────< Agent
         └──────────────< MLModel (org_id opcional — catálogo global)

Toda tabela "operacional" (agents, rag_chunks, sessions, feedback,
ml_models) carrega `org_id` — é a coluna que a migration
`0003_rls_policies` usa para isolar organizações via Row-Level
Security no Postgres. `users`/`roles` ficam FORA da RLS de propósito:
login precisa localizar o usuário pelo e-mail antes de saber qual é a
"organização ativa" da conexão — ver docstring da migration 0003.

Este módulo convive com `pg_pool.py` (pool asyncpg cru, usado pelos
routers legados `rag.py`/`feedback.py` contra as tabelas do
`scripts/init.sql`) e com `db.py`/`models.py` (SQLAlchemy ORM só de
auth, usado por `auth.py`/`routers/auth.py`/a suíte de testes contra
SQLite em memória). `database.py` é a base para qualquer serviço novo
e para o schema gerenciado por Alembic (`alembic/versions/`).

Uso típico (FastAPI):

    from database import get_session, get_org_scoped_session

    @router.get("/agents")
    async def list_agents(session: AsyncSession = Depends(get_session)):
        ...

    @router.get("/agents/scoped")
    async def list_my_agents(
        session: AsyncSession = Depends(lambda: get_org_scoped_session(org_id)),
    ):
        # dentro deste bloco, a RLS do Postgres já filtra por org_id
        ...

Uso fora do FastAPI (scripts, testes — ver test_connection.py):

    async with SessionLocal() as session:
        await set_org_context(session, org_id)
        ...
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import get_settings

settings = get_settings()

# Dimensão do vetor de embedding — mantida em sincronia com
# `settings.embedding_dimensions` (config.py, default 1536 para
# text-embedding-3-small). As migrations Alembic fixam o valor
# numericamente (schema não pode depender de env var em runtime), então
# ao mudar de modelo de embedding é preciso uma migration nova.
EMBEDDING_DIM: int = settings.embedding_dimensions


def to_async_dsn(dsn: str) -> str:
    """Normaliza um DSN síncrono (`postgresql://`, `postgres://`) para o
    driver assíncrono `asyncpg` usado pelo SQLAlchemy. DSNs que já
    especificam driver (`postgresql+asyncpg://` etc.) passam intactos."""
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    if dsn.startswith("postgres://"):
        return dsn.replace("postgres://", "postgresql+asyncpg://", 1)
    return dsn


engine: AsyncEngine = create_async_engine(
    to_async_dsn(settings.database_url),
    pool_pre_ping=True,
    pool_size=settings.db_pool_min_size,
    max_overflow=max(settings.db_pool_max_size - settings.db_pool_min_size, 0),
    future=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


def _new_uuid() -> str:
    return str(uuid.uuid4())


# Papéis padrão seedados em toda organização nova — ver Manta CLAUDE.md
# (RBAC não é por aqui; é apenas o catálogo global de nomes de papel).
DEFAULT_ROLE_NAMES: tuple[str, ...] = ("owner", "admin", "member", "viewer")

# Tabelas por-organização que a migration 0003 protege com RLS.
ORG_SCOPED_TABLES: tuple[str, ...] = (
    "organizations",
    "agents",
    "rag_chunks",
    "sessions",
    "feedback",
    "ml_models",
)


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------
class Organization(Base):
    """Tenant raiz — toda linha "operacional" (Agent, RagChunk, Session,
    Feedback, MLModel) pertence a exatamente uma Organization."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    users: Mapped[list[User]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    agents: Mapped[list[Agent]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    rag_chunks: Mapped[list[RagChunk]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    sessions: Mapped[list[Session]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    feedback_entries: Mapped[list[Feedback]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    ml_models: Mapped[list[MLModel]] = relationship(back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Organization id={self.id!r} slug={self.slug!r}>"


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------
class Role(Base):
    """Catálogo global de papéis (owner/admin/member/viewer) — não é
    por-organização; `User.role_id` aponta para cá."""

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list[User]] = relationship(back_populates="role")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Role name={self.name!r}>"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(Base):
    """Usuário pertence a exatamente UMA organização (`org_id`) com
    exatamente UM papel (`role_id`) — desenho simples e explícito de
    propósito. Um mesmo e-mail pode se repetir em organizações
    diferentes (linhas distintas); a unicidade é (org_id, email), não
    email global."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("org_id", "email", name="uq_users_org_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped[Organization] = relationship(back_populates="users")
    role: Mapped[Role] = relationship(back_populates="users")
    sessions: Mapped[list[Session]] = relationship(back_populates="user")
    feedback_entries: Mapped[list[Feedback]] = relationship(back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User id={self.id!r} email={self.email!r} org_id={self.org_id!r}>"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class Agent(Base):
    """Instância, por organização, de um agente do Maestro (Eixo 1
    horizontal ou Eixo 2 vertical por segmento) — ver CLAUDE.md "MAPA
    COMPLETO DE AGENTES". `code` é o código Manta (ex.: "Manta 03-S8"),
    `segment` é S1..S10 quando o agente for vertical."""

    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("org_id", "code", name="uq_agents_org_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # "Manta 03-S8"
    slug: Mapped[str] = mapped_column(String(100), nullable=False)  # "agente-saneamento"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    axis: Mapped[str] = mapped_column(String(20), nullable=False, default="horizontal")  # horizontal|vertical
    segment: Mapped[str | None] = mapped_column(String(10), nullable=True)  # S1..S10
    tier_default: Mapped[str] = mapped_column(String(50), nullable=False, default="Sonnet")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="operational")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped[Organization] = relationship(back_populates="agents")
    rag_chunks: Mapped[list[RagChunk]] = relationship(back_populates="agent")
    sessions: Mapped[list[Session]] = relationship(back_populates="agent")
    feedback_entries: Mapped[list[Feedback]] = relationship(back_populates="agent")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Agent code={self.code!r} org_id={self.org_id!r}>"


# ---------------------------------------------------------------------------
# RagChunk
# ---------------------------------------------------------------------------
class RagChunk(Base):
    """Chunk vetorizado de uma coleção RAG (Supabase/pgvector) — ver
    tabela "RAG — Coleções em Supabase" do CLAUDE.md (saneamento,
    energia, portos, aeroportos, barragens). `embedding` usa pgvector;
    o índice IVFFlat (cosine) é criado na migration 0002."""

    __tablename__ = "rag_chunks"
    __table_args__ = (
        Index("ix_rag_chunks_org_collection", "org_id", "collection"),
        Index(
            "ix_rag_chunks_embedding_ivfflat",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    collection: Mapped[str] = mapped_column(String(50), nullable=False)  # saneamento|energia|portos|...
    prefix: Mapped[str] = mapped_column(String(10), nullable=False)  # san:|ene:|por:|aer:|bar:
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Organization] = relationship(back_populates="rag_chunks")
    agent: Mapped[Agent | None] = relationship(back_populates="rag_chunks")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RagChunk id={self.id!r} collection={self.collection!r}>"


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------
class Session(Base):
    """Uma execução/atendimento de um Agent para um User — cronologia
    de input→output, tokens e status. O nome é o pedido explicitamente
    ("Session" do desenho de dados); não colide com
    `sqlalchemy.orm.Session` porque este módulo não importa esse nome."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")  # active|completed|error
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(back_populates="sessions")
    agent: Mapped[Agent | None] = relationship(back_populates="sessions")
    user: Mapped[User | None] = relationship(back_populates="sessions")
    feedback_entries: Mapped[list[Feedback]] = relationship(back_populates="session")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Session id={self.id!r} status={self.status!r}>"


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
class Feedback(Base):
    """Feedback de uso de um agente (thumbs up/down + comentário),
    opcionalmente ligado à Session que o originou."""

    __tablename__ = "feedback"
    __table_args__ = (CheckConstraint("rating BETWEEN -1 AND 1", name="ck_feedback_rating_range"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # -1 ruim | 0 neutro | 1 bom
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Organization] = relationship(back_populates="feedback_entries")
    session: Mapped[Session | None] = relationship(back_populates="feedback_entries")
    agent: Mapped[Agent | None] = relationship(back_populates="feedback_entries")
    user: Mapped[User | None] = relationship(back_populates="feedback_entries")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Feedback id={self.id!r} rating={self.rating!r}>"


# ---------------------------------------------------------------------------
# MLModel
# ---------------------------------------------------------------------------
class MLModel(Base):
    """Catálogo de modelos de LLM/embedding disponíveis para os
    agentes. `org_id` nulo = modelo global de plataforma (visível a
    todas as organizações); preenchido = override específico de uma
    organização (ex.: fine-tune, tier customizado)."""

    __tablename__ = "ml_models"
    __table_args__ = (UniqueConstraint("org_id", "model_id", name="uq_ml_models_org_model_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    org_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="anthropic")
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)  # "claude-sonnet-5"
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="Sonnet")  # Haiku|Sonnet|Opus
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="generation")  # routing|generation|embedding
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped[Organization | None] = relationship(back_populates="ml_models")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<MLModel model_id={self.model_id!r} org_id={self.org_id!r}>"


# ---------------------------------------------------------------------------
# Engine / sessão / contexto RLS
# ---------------------------------------------------------------------------
async def init_models() -> None:
    """Cria a extensão `vector` e as tabelas se não existirem. Uso: dev
    local e smoke tests. Produção deve usar as migrations Alembic
    (`alembic upgrade head`) — é lá que a RLS é habilitada; `create_all`
    NÃO aplica RLS nem policies."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependency FastAPI: uma `AsyncSession` por request, sem contexto
    de organização setado (uso administrativo/global, ou quando o
    endpoint filtra por org_id manualmente nas queries)."""
    async with SessionLocal() as session:
        yield session


async def set_org_context(session: AsyncSession, org_id: str) -> None:
    """Define `app.current_org_id` para a transação atual — é o que as
    RLS policies leem via `current_setting('app.current_org_id', true)`
    (migration 0003_rls_policies).

    Usa `set_config(...)` (função SQL comum) em vez de `SET LOCAL ...`
    cru: o comando `SET` não aceita bind parameters no protocolo
    "extended query" usado por asyncpg/SQLAlchemy, então concatenar
    `org_id` numa string `SET LOCAL app.current_org_id = '{org_id}'`
    seria necessário — e abriria espaço para injeção de SQL.
    `set_config('app.current_org_id', $1, true)` é uma chamada de
    função normal, parametrizável com segurança; o terceiro argumento
    `true` (`is_local`) dá o mesmo escopo de `SET LOCAL` — o valor só
    vale até o fim da transação atual da sessão."""
    await session.execute(
        text("SELECT set_config('app.current_org_id', :org_id, true)"),
        {"org_id": org_id},
    )


async def create_organization(
    session: AsyncSession, *, name: str, slug: str, plan: str = "standard"
) -> Organization:
    """Cria uma Organization respeitando a RLS da migration 0003.

    Pegadinha que esta função existe para evitar: a policy de SELECT de
    `organizations` (que a inserção via SQLAlchemy também precisa
    satisfazer, por causa do `RETURNING` implícito que o dialeto
    postgresql usa para ler de volta `created_at`/`updated_at`) só
    libera a linha cujo `id` bate com `app.current_org_id`. Como esse
    id normalmente só existiria DEPOIS do insert (default gerado no
    flush), setar o contexto "depois" é tarde demais — o servidor já
    rejeitou a linha antes de você conseguir lê-la de volta.

    Por isso, aqui o id é gerado ANTES, em Python, e o contexto é
    setado para esse valor antes do `flush()` — ao contrário do padrão
    usual (criar a linha e só depois entrar no contexto dela), que
    funciona bem para Agent/RagChunk/Session/Feedback (cujo `org_id`
    referencia uma organização que já existe)."""
    org_id = _new_uuid()
    await set_org_context(session, org_id)
    organization = Organization(id=org_id, name=name, slug=slug, plan=plan)
    session.add(organization)
    await session.flush()
    return organization


@asynccontextmanager
async def get_org_scoped_session(org_id: str) -> AsyncIterator[AsyncSession]:
    """Dependency/context manager: abre uma sessão, seta o contexto RLS
    da organização informada e devolve a sessão — os SELECTs/INSERTs
    feitos com ela já respeitam o isolamento multi-org no Postgres
    (além de qualquer filtro `WHERE org_id = ...` feito na aplicação).

    Uso em FastAPI:

        async def dep(org_id: str = Depends(get_current_org_id)):
            async with get_org_scoped_session(org_id) as session:
                yield session

        @router.get("/agents")
        async def list_agents(session: AsyncSession = Depends(dep)):
            ...
    """
    async with SessionLocal() as session:
        await set_org_context(session, org_id)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
