"""
models.py — Modelos SQLAlchemy (async, 2.0 style) para autenticação e
autorização multi-organização do Manta Backend.

Desenho:

    User ──< UserRole >── Role
             │
             v
        Organization

`UserRole` é a tabela de associação que dá suporte a multi-org: o MESMO
usuário pode ter papéis diferentes em organizações diferentes (ex.:
"owner" na Manta, "viewer" num tenant de cliente). RBAC nunca pergunta
"qual o papel do usuário?" sozinho — sempre "qual o papel do usuário
NESTA organização?".

`RefreshToken` persiste apenas o `jti` (JWT ID) de cada refresh token
emitido, nunca o token em si — permite revogar/rotacionar sem guardar
segredos no banco.

Em produção, criação/alteração de schema deve passar por migrations
(Alembic). O helper `init_models()` em `db.py` usa `create_all` e serve
para dev local e para a suíte de testes (SQLite em memória).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _new_uuid() -> str:
    return str(uuid.uuid4())


# Papéis padrão seedados em toda organização nova. "owner" é atribuído
# automaticamente a quem registra a organização (ver routers/auth.py).
DEFAULT_ROLE_NAMES: tuple[str, ...] = ("owner", "admin", "member", "viewer")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_roles: Mapped[list[UserRole]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Organization id={self.id!r} slug={self.slug!r}>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_roles: Mapped[list[UserRole]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User id={self.id!r} email={self.email!r}>"


class Role(Base):
    """Catálogo global de papéis (não é por-organização — a associação
    org↔papel↔usuário vive em `UserRole`)."""

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")

    user_roles: Mapped[list[UserRole]] = relationship(back_populates="role")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Role name={self.name!r}>"


class UserRole(Base):
    """Tabela de associação N:N:N — concede a `role` a `user` dentro de
    `organization`. É esta a "context de multi-org": consultar
    `UserRole` filtrando por (user_id, org_id) responde "quais papéis o
    usuário tem NESTA organização"."""

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "org_id", "role_id", name="uq_user_org_role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="user_roles")
    organization: Mapped[Organization] = relationship(back_populates="user_roles")
    role: Mapped[Role] = relationship(back_populates="user_roles")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<UserRole user_id={self.user_id!r} org_id={self.org_id!r} role_id={self.role_id!r}>"


class RefreshToken(Base):
    """Registro de refresh tokens emitidos, para permitir revogação e
    rotação (o token em si — o JWT assinado — nunca é guardado, só o
    `jti` que ele carrega no payload)."""

    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    org_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    # Naive UTC de propósito (não `timezone=True`): comparações de
    # expiração/revogação são feitas em Python contra
    # `datetime.utcnow()` e precisam se comportar identicamente em
    # Postgres (prod) e SQLite (testes) — misturar aware/naive entre
    # dialetos é uma fonte clássica de "can't compare offset-naive and
    # offset-aware datetimes".
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<RefreshToken jti={self.jti!r} revoked={self.revoked!r}>"
