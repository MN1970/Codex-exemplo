"""
auth.py — JWT (RS256) + middleware de validação + RBAC + contexto
multi-organização.

Peças principais:

  * `create_access_token` / `create_refresh_token` / `decode_token` —
    emissão e validação de JWT assinados com RS256 (chave privada
    assina, chave pública valida — permite que outros serviços
    verifiquem tokens sem poder forjá-los).
  * `get_current_user` — dependency FastAPI que funciona como
    "middleware de validação de token": extrai o Bearer token, decodifica,
    carrega o usuário real do banco (via SQLAlchemy async) e garante que
    ele ainda existe e está ativo (revogação de conta tem efeito
    imediato mesmo com um access token não expirado).
  * `get_current_org` — resolve a organização "ativa" do request
    (header `X-Org-Id` ou claim do token) e as roles do usuário NESSA
    organização, sempre revalidando contra o banco — é o núcleo do
    suporte multi-org.
  * `require_roles(*roles)` — decorator/dependency factory de RBAC:
    bloqueia com 403 se o usuário não tiver nenhum dos papéis exigidos
    na organização ativa. `is_superuser` faz bypass (operador de
    plataforma, não papel de organização).
  * `require_role(*roles)` / `User` / `get_current_user` (variante
    simples) — mantidos por compatibilidade com `routers/admin.py`,
    que usa um modelo de papel único embutido no token, sem contexto de
    organização (o `/admin/token` é um atalho de desenvolvimento).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import get_settings
from db import get_session

logger = logging.getLogger("manta.auth")

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


# --------------------------------------------------------------------------
# Chaves RS256
# --------------------------------------------------------------------------

def _generate_ephemeral_rsa_keypair() -> tuple[str, str]:
    """Gera um par RSA-2048 em memória. Usado apenas quando
    JWT_PRIVATE_KEY/JWT_PUBLIC_KEY não estão configurados — cobre dev e
    testes, mas NÃO deve ser usado em produção: as chaves não
    sobrevivem a um restart nem são compartilhadas entre réplicas, o
    que invalida todos os tokens emitidos a cada deploy/restart."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


def _load_signing_keys() -> tuple[str, str]:
    algorithm = settings.jwt_algorithm.upper()
    if algorithm.startswith(("RS", "ES", "PS")):
        if settings.jwt_private_key and settings.jwt_public_key:
            return settings.jwt_private_key, settings.jwt_public_key
        logger.warning(
            "auth: JWT_PRIVATE_KEY/JWT_PUBLIC_KEY não configurados — "
            "gerando par RSA efêmero (NÃO usar em produção multi-instância)."
        )
        return _generate_ephemeral_rsa_keypair()
    # Algoritmo simétrico (HS*): a mesma chave assina e valida.
    return settings.jwt_secret, settings.jwt_secret


_PRIVATE_KEY, _PUBLIC_KEY = _load_signing_keys()


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou expiradas.",
    headers={"WWW-Authenticate": "Bearer"},
)


# --------------------------------------------------------------------------
# Password hashing
# --------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# --------------------------------------------------------------------------
# Emissão / validação de tokens
# --------------------------------------------------------------------------

def create_access_token(
    subject: str,
    email: str = "",
    roles: list[str] | None = None,
    org_id: str | None = None,
    role: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Emite um access token de curta duração.

    `role` (singular) é aceito por compatibilidade com chamadores
    legados que emitem um único papel embutido no token (ver
    `routers/admin.py`); é normalizado para `roles=[role]`.
    """
    if role and not roles:
        roles = [role]
    roles = roles or []

    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expires_minutes))
    claims = {
        "sub": subject,
        "email": email,
        "org_id": org_id,
        "roles": roles,
        "type": ACCESS_TOKEN_TYPE,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        # Timestamp int explícito (não um `datetime`): evita qualquer
        # ambiguidade aware/naive na serialização do claim `exp` — o
        # valor de epoch de um datetime aware já é UTC por definição.
        "exp": int(expire.timestamp()),
        "iss": settings.jwt_issuer,
    }
    return jwt.encode(claims, _PRIVATE_KEY, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    subject: str,
    org_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> tuple[str, str, datetime]:
    """Emite um refresh token de longa duração.

    Retorna `(token, jti, expires_at)` — o chamador é responsável por
    persistir `(jti, expires_at)` em `RefreshToken` (permite revogação e
    rotação) ANTES de devolver o token ao cliente. `expires_at` é
    devolvido como datetime **naive em UTC** (ver comentário em
    `models.RefreshToken.expires_at`).
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.refresh_token_expires_days))
    jti = str(uuid.uuid4())
    claims = {
        "sub": subject,
        "org_id": org_id,
        "type": REFRESH_TOKEN_TYPE,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": settings.jwt_issuer,
    }
    token = jwt.encode(claims, _PRIVATE_KEY, algorithm=settings.jwt_algorithm)
    return token, jti, expire.astimezone(timezone.utc).replace(tzinfo=None)


def decode_token(token: str, expected_type: str = ACCESS_TOKEN_TYPE) -> dict:
    """Decodifica e valida assinatura, expiração, issuer e `type` do
    claim (access vs. refresh não são intercambiáveis)."""
    try:
        payload = jwt.decode(
            token,
            _PUBLIC_KEY,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise credentials_exception from exc

    if payload.get("type") != expected_type:
        raise credentials_exception
    return payload


# --------------------------------------------------------------------------
# Middleware de validação de token + carregamento do usuário (multi-org)
# --------------------------------------------------------------------------

class OrgContext(BaseModel):
    """Organização ativa do request + papéis do usuário NELA. Nunca é
    construído a partir apenas do JWT — sempre revalidado contra o
    banco em `get_current_org`, para que remoção de acesso a uma
    organização tenha efeito imediato mesmo com o access token ainda
    dentro da validade."""

    org_id: str
    org_name: str
    roles: list[str] = Field(default_factory=list)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> models.User:
    """Middleware de validação: extrai o Bearer token, decodifica (RS256),
    e carrega o `User` real do banco — garante que a conta ainda existe
    e está ativa. Anexa `token_org_id`/`token_roles` (claims do próprio
    token) como atributos de instância, usados como fallback por
    `get_current_org` quando o header de organização não é enviado."""
    if token is None:
        raise credentials_exception

    payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = await session.get(models.User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    user.token_org_id = payload.get("org_id")  # type: ignore[attr-defined]
    user.token_roles = payload.get("roles", [])  # type: ignore[attr-defined]
    return user


async def get_current_org(
    current_user: models.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    x_org_id: str | None = Header(default=None, alias=settings.org_header_name),
) -> OrgContext:
    """Resolve a organização ativa do request:

    1. Header `X-Org-Id` (nome configurável via `org_header_name`), se enviado.
    2. Caso contrário, o `org_id` embutido no access token.
    3. Caso ainda não haja organização, resolve sozinho SE o usuário
       pertencer a exatamente uma organização; senão, 400 pedindo para
       o cliente escolher.

    Em todos os casos a pertinência (e as roles) são revalidadas contra
    o banco — nunca confiamos cegamente nas roles do JWT.
    """
    org_id = x_org_id or getattr(current_user, "token_org_id", None)

    if org_id is None:
        result = await session.execute(
            select(models.UserRole.org_id)
            .where(models.UserRole.user_id == current_user.id)
            .distinct()
        )
        org_ids = [row[0] for row in result.all()]
        if len(org_ids) == 1:
            org_id = org_ids[0]
        elif len(org_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não pertence a nenhuma organização.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Usuário pertence a múltiplas organizações — "
                    f"informe o header {settings.org_header_name}."
                ),
            )

    result = await session.execute(
        select(models.Role.name, models.Organization.name)
        .join(models.UserRole, models.UserRole.role_id == models.Role.id)
        .join(models.Organization, models.Organization.id == models.UserRole.org_id)
        .where(models.UserRole.user_id == current_user.id, models.UserRole.org_id == org_id)
    )
    rows = result.all()
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não pertence a esta organização.",
        )

    roles = sorted({row[0] for row in rows})
    org_name = rows[0][1]
    return OrgContext(org_id=org_id, org_name=org_name, roles=roles)


def require_roles(*allowed_roles: str):
    """RBAC decorator (dependency factory) com contexto de organização:
    `Depends(require_roles("owner", "admin"))`.

    Bloqueia com 403 se nenhum papel do usuário NA ORGANIZAÇÃO ATIVA
    estiver em `allowed_roles`. `current_user.is_superuser` sempre
    passa — é bypass de operador de plataforma, não papel de
    organização.
    """

    async def _checker(
        org_context: OrgContext = Depends(get_current_org),
        current_user: models.User = Depends(get_current_user),
    ) -> OrgContext:
        if current_user.is_superuser:
            return org_context
        if not set(org_context.roles) & set(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Requer um dos papéis: {', '.join(allowed_roles)} "
                    f"(organização {org_context.org_id})."
                ),
            )
        return org_context

    return _checker


# --------------------------------------------------------------------------
# Compat legado — routers/admin.py (papel único, sem organização)
# --------------------------------------------------------------------------

class User(BaseModel):
    """Modelo "achatado" (sem organização) usado pelo fluxo legado de
    dev-token em `routers/admin.py`. Endpoints novos devem usar
    `models.User` (ORM) + `OrgContext` via `require_roles`."""

    username: str
    role: str = "user"
    disabled: bool = False


def require_role(*allowed_roles: str):
    """Compat: `Depends(require_role("admin"))` — RBAC "simples" que lê
    o(s) papel(is) direto do claim `roles` do access token, sem
    resolver organização nem tocar o banco. Mantido para não quebrar
    `routers/admin.py`; rotas que operam sobre dados de uma organização
    devem usar `require_roles`, que reforça contra o banco.
    """

    async def _checker(token: str | None = Depends(oauth2_scheme)) -> User:
        if token is None:
            raise credentials_exception
        payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
        roles = set(payload.get("roles", []))
        if not roles & set(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requer papel: {', '.join(allowed_roles)}.",
            )
        return User(
            username=payload.get("email") or payload.get("sub", ""),
            role=next(iter(roles), "user"),
        )

    return _checker
