"""initial schema — organizations, roles, users, agents, rag_chunks, sessions, feedback, ml_models

Cria as 8 tabelas mapeadas em `database.py` (Organization, Role, User,
Agent, RagChunk, Session, Feedback, MLModel), suas foreign keys,
constraints e índices — incluindo o índice IVFFlat (cosine) sobre
`rag_chunks.embedding`.

Ordem de criação respeita as dependências de FK:

    organizations, roles            (sem dependências)
    users                           (-> organizations, roles)
    agents                          (-> organizations)
    rag_chunks                      (-> organizations, agents)
    sessions                        (-> organizations, agents, users)
    feedback                        (-> organizations, sessions, agents, users)
    ml_models                       (-> organizations, nullable)

Revision ID: 0002_initial_schema
Revises: 0001_pgvector_extension
Create Date: 2026-07-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_initial_schema"
down_revision: Union[str, None] = "0001_pgvector_extension"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Dimensão do vetor de embedding — mantenha em sincronia com
# `database.EMBEDDING_DIM` / `config.Settings.embedding_dimensions`
# (1536 = text-embedding-3-small). Trocar de modelo de embedding com
# dimensão diferente exige uma migration nova (ALTER COLUMN + reindex),
# não editar este valor retroativamente.
EMBEDDING_DIM = 1536


def upgrade() -> None:
    # -- organizations ------------------------------------------------
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("plan", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    # -- roles ----------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # -- users ------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.String(36), sa.ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("org_id", "email", name="uq_users_org_email"),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])
    op.create_index("ix_users_role_id", "users", ["role_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # -- agents -----------------------------------------------------------
    op.create_table(
        "agents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("axis", sa.String(20), nullable=False, server_default="horizontal"),
        sa.Column("segment", sa.String(10), nullable=True),
        sa.Column("tier_default", sa.String(50), nullable=False, server_default="Sonnet"),
        sa.Column("status", sa.String(30), nullable=False, server_default="operational"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("org_id", "code", name="uq_agents_org_code"),
    )
    op.create_index("ix_agents_org_id", "agents", ["org_id"])

    # -- rag_chunks ---------------------------------------------------
    op.create_table(
        "rag_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("collection", sa.String(50), nullable=False),
        sa.Column("prefix", sa.String(10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        sa.Column(
            "meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_rag_chunks_org_id", "rag_chunks", ["org_id"])
    op.create_index("ix_rag_chunks_agent_id", "rag_chunks", ["agent_id"])
    op.create_index("ix_rag_chunks_org_collection", "rag_chunks", ["org_id", "collection"])
    # Índice IVFFlat (aproximado, cosine) para busca por similaridade.
    # `lists = 100` é um ponto de partida razoável para até ~1M linhas
    # (regra prática do pgvector: lists ≈ sqrt(N) para N grande, ou
    # N/1000 para N muito grande); revise e REINDEX conforme o volume
    # real de cada coleção crescer — IVFFlat também se beneficia de ser
    # criado DEPOIS de a tabela já ter dados (senão as listas ficam mal
    # distribuídas). Se a coleção crescer muito, considere migrar para
    # HNSW (`postgresql_using="hnsw"`), disponível a partir do
    # pgvector 0.5.
    op.create_index(
        "ix_rag_chunks_embedding_ivfflat",
        "rag_chunks",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )

    # -- sessions -----------------------------------------------------
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sessions_org_id", "sessions", ["org_id"])
    op.create_index("ix_sessions_agent_id", "sessions", ["agent_id"])
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    # -- feedback -------------------------------------------------------
    op.create_table(
        "feedback",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rating BETWEEN -1 AND 1", name="ck_feedback_rating_range"),
    )
    op.create_index("ix_feedback_org_id", "feedback", ["org_id"])
    op.create_index("ix_feedback_session_id", "feedback", ["session_id"])
    op.create_index("ix_feedback_agent_id", "feedback", ["agent_id"])
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])

    # -- ml_models --------------------------------------------------
    op.create_table(
        "ml_models",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, server_default="anthropic"),
        sa.Column("model_id", sa.String(100), nullable=False),
        sa.Column("tier", sa.String(20), nullable=False, server_default="Sonnet"),
        sa.Column("purpose", sa.String(50), nullable=False, server_default="generation"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("org_id", "model_id", name="uq_ml_models_org_model_id"),
    )
    op.create_index("ix_ml_models_org_id", "ml_models", ["org_id"])


def downgrade() -> None:
    op.drop_table("ml_models")

    op.drop_index("ix_feedback_user_id", table_name="feedback")
    op.drop_index("ix_feedback_agent_id", table_name="feedback")
    op.drop_index("ix_feedback_session_id", table_name="feedback")
    op.drop_index("ix_feedback_org_id", table_name="feedback")
    op.drop_table("feedback")

    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_index("ix_sessions_agent_id", table_name="sessions")
    op.drop_index("ix_sessions_org_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_rag_chunks_embedding_ivfflat", table_name="rag_chunks")
    op.drop_index("ix_rag_chunks_org_collection", table_name="rag_chunks")
    op.drop_index("ix_rag_chunks_agent_id", table_name="rag_chunks")
    op.drop_index("ix_rag_chunks_org_id", table_name="rag_chunks")
    op.drop_table("rag_chunks")

    op.drop_index("ix_agents_org_id", table_name="agents")
    op.drop_table("agents")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_index("ix_users_org_id", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")

    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")
