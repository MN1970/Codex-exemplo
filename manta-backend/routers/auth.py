"""
routers/auth.py — Endpoints de autenticação e identidade multi-org.

    POST /auth/register  — cria usuário + organização (usuário vira "owner")
    POST /auth/login     — troca email/senha (+ org_id opcional) por tokens
    POST /auth/refresh   — rotaciona refresh token, emite novo access token
    GET  /auth/me        — perfil do usuário autenticado + org ativa
    GET  /auth/orgs      — todas as organizações do usuário e seus papéis

Nenhuma rota aqui assume que o usuário pertence a uma única organização
— `login`/`refresh` resolvem a organização ativa (via `org_id` explícito
ou, se só houver uma, por default) e embutem `org_id`+`roles` no access
token; `me`/`orgs` expõem a visão completa (todas as orgs) além da
organização "ativa" do request atual.
"""
from __future__ import annotations

import re
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from config import get_settings
from db import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = ""
    org_name: str = Field(min_length=2, max_length=255, description="Nome da organização criada para o usuário (vira 'owner' nela).")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    org_id: str | None = Field(
        default=None,
        description="Organização a ativar no token. Obrigatório se o usuário pertencer a mais de uma.",
    )


class RefreshRequest(BaseModel):
    refresh_token: str


class OrgMembership(BaseModel):
    org_id: str
    slug: str
    name: str
    roles: list[str] = Field(default_factory=list)


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool


class RegisterResponse(BaseModel):
    user: UserPublic
    organization: OrgMembership


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    org_id: str | None = None
    roles: list[str] = Field(default_factory=list)


class MeResponse(UserPublic):
    active_org: OrgMembership | None = None
    organizations: list[OrgMembership] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Helpers internos
# --------------------------------------------------------------------------

def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "org"


async def _unique_slug(session: AsyncSession, base: str) -> str:
    slug = base
    suffix = 1
    while await session.scalar(select(models.Organization.id).where(models.Organization.slug == slug)):
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


async def _get_or_create_role(session: AsyncSession, name: str) -> models.Role:
    role = await session.scalar(select(models.Role).where(models.Role.name == name))
    if role is None:
        role = models.Role(name=name)
        session.add(role)
        await session.flush()
    return role


async def _load_memberships(session: AsyncSession, user_id: str) -> list[OrgMembership]:
    """Todas as organizações do usuário, com os papéis que ele tem em
    cada uma (um usuário pode ter mais de um papel por organização)."""
    result = await session.execute(
        select(models.Organization.id, models.Organization.slug, models.Organization.name, models.Role.name)
        .join(models.UserRole, models.UserRole.org_id == models.Organization.id)
        .join(models.Role, models.Role.id == models.UserRole.role_id)
        .where(models.UserRole.user_id == user_id)
        .order_by(models.Organization.name)
    )
    grouped: dict[str, OrgMembership] = {}
    for org_id, slug, name, role_name in result.all():
        membership = grouped.setdefault(org_id, OrgMembership(org_id=org_id, slug=slug, name=name, roles=[]))
        membership.roles.append(role_name)
    for membership in grouped.values():
        membership.roles = sorted(membership.roles)
    return list(grouped.values())


async def _issue_tokens(
    session: AsyncSession,
    user: models.User,
    org_id: str | None,
    roles: list[str],
) -> TokenResponse:
    access_token = create_access_token(subject=user.id, email=user.email, roles=roles, org_id=org_id)
    refresh_token, jti, expires_at = create_refresh_token(subject=user.id, org_id=org_id)
    session.add(models.RefreshToken(jti=jti, user_id=user.id, org_id=org_id, expires_at=expires_at))
    await session.commit()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expires_minutes * 60,
        org_id=org_id,
        roles=roles,
    )


def _multi_org_error(memberships: list[OrgMembership]) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Usuário pertence a múltiplas organizações — informe org_id.",
            "organizations": [m.model_dump() for m in memberships],
        },
    )


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria usuário + organização (usuário vira 'owner' da organização)",
)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> RegisterResponse:
    email = payload.email.lower()
    existing = await session.scalar(select(models.User).where(models.User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado.")

    user = models.User(email=email, hashed_password=hash_password(payload.password), full_name=payload.full_name)
    session.add(user)
    await session.flush()  # popula user.id (uuid client-side) para as FKs abaixo

    slug = await _unique_slug(session, _slugify(payload.org_name))
    organization = models.Organization(name=payload.org_name, slug=slug)
    session.add(organization)
    await session.flush()

    owner_role = await _get_or_create_role(session, "owner")
    session.add(models.UserRole(user_id=user.id, org_id=organization.id, role_id=owner_role.id))

    await session.commit()

    return RegisterResponse(
        user=UserPublic(
            id=user.id, email=user.email, full_name=user.full_name,
            is_active=user.is_active, is_superuser=user.is_superuser,
        ),
        organization=OrgMembership(org_id=organization.id, slug=organization.slug, name=organization.name, roles=["owner"]),
    )


@router.post("/login", response_model=TokenResponse, summary="Login: e-mail/senha (+ org_id opcional) → access+refresh token")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    user = await session.scalar(select(models.User).where(models.User.email == payload.email.lower()))
    # Mensagem genérica de propósito: não revelar se o e-mail existe ou
    # se foi a senha que errou (evita enumeração de contas).
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário desativado.")

    memberships = await _load_memberships(session, user.id)

    if payload.org_id is not None:
        membership = next((m for m in memberships if m.org_id == payload.org_id), None)
        if membership is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não pertence a esta organização.")
        org_id, roles = membership.org_id, membership.roles
    elif len(memberships) == 1:
        org_id, roles = memberships[0].org_id, memberships[0].roles
    elif len(memberships) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não pertence a nenhuma organização.")
    else:
        raise _multi_org_error(memberships)

    return await _issue_tokens(session, user, org_id, roles)


@router.post("/refresh", response_model=TokenResponse, summary="Rotaciona refresh token e emite novo access token")
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    token_payload = decode_token(payload.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    jti = token_payload.get("jti")

    stored = await session.scalar(select(models.RefreshToken).where(models.RefreshToken.jti == jti))
    # `datetime.utcnow()` (naive) de propósito, não `datetime.now(UTC)`:
    # `RefreshToken.expires_at` é uma coluna naive-UTC (ver models.py) —
    # comparar com um datetime aware aqui levantaria TypeError.
    if stored is None or stored.revoked or stored.expires_at < datetime.utcnow():  # noqa: DTZ003
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido, expirado ou revogado.")

    user = await session.get(models.User, token_payload.get("sub"))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido ou inativo.")

    # Rotação: um refresh token só vale para uma única troca — usá-lo
    # revoga-o imediatamente, mesmo que o novo refresh nunca seja usado
    # (mitiga replay de um refresh token vazado/interceptado).
    stored.revoked = True

    org_id = token_payload.get("org_id")
    roles: list[str] = []
    if org_id is not None:
        memberships = await _load_memberships(session, user.id)
        membership = next((m for m in memberships if m.org_id == org_id), None)
        if membership is not None:
            roles = membership.roles
        else:
            org_id = None  # acesso à org foi removido entre o login e este refresh

    return await _issue_tokens(session, user, org_id, roles)


@router.get("/me", response_model=MeResponse, summary="Perfil do usuário autenticado + organização ativa")
async def me(
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    x_org_id: str | None = Header(default=None, alias=settings.org_header_name),
) -> MeResponse:
    memberships = await _load_memberships(session, current_user.id)

    org_id = x_org_id or getattr(current_user, "token_org_id", None)
    active: OrgMembership | None = None
    if org_id is not None:
        active = next((m for m in memberships if m.org_id == org_id), None)
    elif len(memberships) == 1:
        active = memberships[0]

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        active_org=active,
        organizations=memberships,
    )


@router.get("/orgs", response_model=list[OrgMembership], summary="Todas as organizações do usuário e seus papéis em cada uma")
async def list_orgs(
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[OrgMembership]:
    return await _load_memberships(session, current_user.id)
