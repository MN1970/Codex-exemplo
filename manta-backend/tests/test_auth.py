"""
tests/test_auth.py — Suíte pytest do módulo de autenticação:

  * hashing de senha
  * emissão/validação de JWT RS256 (incluindo rejeição de assinatura
    adulterada e de tipo de token trocado — access vs. refresh)
  * endpoints /auth/register, /auth/login, /auth/refresh, /auth/me,
    /auth/orgs
  * RBAC multi-organização (`require_roles`) ponta a ponta, incluindo
    troca de organização ativa via header `X-Org-Id` e bypass de
    superusuário

Roda com: `pytest` (a partir de `manta-backend/`), sem depender de
Postgres — ver tests/conftest.py.
"""
from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy import select

import auth
import models

# Nota: `asyncio_mode = "auto"` está configurado em pyproject.toml
# ([tool.pytest.ini_options]) — funções `async def test_*` rodam como
# testes assíncronos automaticamente, sem precisar de
# `@pytest.mark.asyncio` em cada uma (e sem marcar por engano as
# funções síncronas, como os testes de hashing/JWT abaixo).


# --------------------------------------------------------------------------
# Helpers de fixture (dados diretamente no banco, fora dos endpoints
# públicos — usados para montar cenários que /auth/register não cobre,
# como um usuário pertencendo a duas organizações).
# --------------------------------------------------------------------------

async def _create_org(session, name: str, slug: str) -> models.Organization:
    org = models.Organization(name=name, slug=slug)
    session.add(org)
    await session.flush()
    return org


async def _create_user(session, email: str, password: str = "senha-super-secreta") -> models.User:
    user = models.User(email=email, hashed_password=auth.hash_password(password), full_name="Fulano de Tal")
    session.add(user)
    await session.flush()
    return user


async def _get_or_create_role(session, name: str) -> models.Role:
    role = await session.scalar(select(models.Role).where(models.Role.name == name))
    if role is None:
        role = models.Role(name=name)
        session.add(role)
        await session.flush()
    return role


async def _grant(session, user: models.User, org: models.Organization, role_name: str) -> None:
    role = await _get_or_create_role(session, role_name)
    session.add(models.UserRole(user_id=user.id, org_id=org.id, role_id=role.id))
    await session.flush()


# --------------------------------------------------------------------------
# Password hashing
# --------------------------------------------------------------------------

def test_hash_password_roundtrip():
    hashed = auth.hash_password("uma-senha-forte")
    assert hashed != "uma-senha-forte"
    assert auth.verify_password("uma-senha-forte", hashed)
    assert not auth.verify_password("senha-errada", hashed)


# --------------------------------------------------------------------------
# JWT RS256 — emissão e validação
# --------------------------------------------------------------------------

def test_access_token_is_signed_rs256_and_decodes():
    token = auth.create_access_token(subject="user-1", email="a@b.com", roles=["owner"], org_id="org-1")
    header = jwt.get_unverified_header(token)
    assert header["alg"] == "RS256"

    payload = auth.decode_token(token, expected_type=auth.ACCESS_TOKEN_TYPE)
    assert payload["sub"] == "user-1"
    assert payload["roles"] == ["owner"]
    assert payload["org_id"] == "org-1"
    assert payload["type"] == "access"
    assert payload["iss"] == auth.settings.jwt_issuer


def test_decode_token_rejects_tampered_signature():
    token = auth.create_access_token(subject="user-1", roles=["owner"])
    tampered = token[:-4] + ("aaaa" if not token.endswith("aaaa") else "bbbb")
    with pytest.raises(HTTPException) as exc_info:
        auth.decode_token(tampered, expected_type=auth.ACCESS_TOKEN_TYPE)
    assert exc_info.value.status_code == 401


def test_decode_token_rejects_expired_token():
    token = auth.create_access_token(subject="user-1", expires_delta=timedelta(seconds=-10))
    with pytest.raises(HTTPException) as exc_info:
        auth.decode_token(token, expected_type=auth.ACCESS_TOKEN_TYPE)
    assert exc_info.value.status_code == 401


def test_decode_token_rejects_wrong_type():
    access_token = auth.create_access_token(subject="user-1")
    # um access token não deve ser aceito onde um refresh é esperado
    with pytest.raises(HTTPException) as exc_info:
        auth.decode_token(access_token, expected_type=auth.REFRESH_TOKEN_TYPE)
    assert exc_info.value.status_code == 401


def test_create_access_token_accepts_legacy_single_role_kwarg():
    """Compat: routers/admin.py chama create_access_token(subject=..., role=...)."""
    token = auth.create_access_token(subject="admin", role="admin")
    payload = auth.decode_token(token)
    assert payload["roles"] == ["admin"]


# --------------------------------------------------------------------------
# POST /auth/register
# --------------------------------------------------------------------------

async def test_register_creates_user_and_owner_org(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "ana@manta.com", "password": "senha-1234", "full_name": "Ana", "org_name": "Manta Associados"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["user"]["email"] == "ana@manta.com"
    assert body["user"]["is_active"] is True
    assert body["organization"]["name"] == "Manta Associados"
    assert body["organization"]["roles"] == ["owner"]
    assert body["organization"]["slug"]  # slugificado, não vazio


async def test_register_duplicate_email_is_conflict(client):
    payload = {"email": "dup@manta.com", "password": "senha-1234", "org_name": "Org A"}
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json={**payload, "org_name": "Org B"})
    assert second.status_code == 409


async def test_register_rejects_short_password(client):
    resp = await client.post(
        "/auth/register",
        json={"email": "x@manta.com", "password": "123", "org_name": "Org C"},
    )
    assert resp.status_code == 422


# --------------------------------------------------------------------------
# POST /auth/login
# --------------------------------------------------------------------------

async def test_login_success_single_org(client):
    await client.post(
        "/auth/register",
        json={"email": "beto@manta.com", "password": "senha-1234", "org_name": "Org Beto"},
    )
    resp = await client.post("/auth/login", json={"email": "beto@manta.com", "password": "senha-1234"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["roles"] == ["owner"]
    assert body["org_id"]
    assert body["access_token"] and body["refresh_token"]


async def test_login_wrong_password_is_unauthorized(client):
    await client.post(
        "/auth/register",
        json={"email": "carla@manta.com", "password": "senha-1234", "org_name": "Org Carla"},
    )
    resp = await client.post("/auth/login", json={"email": "carla@manta.com", "password": "errada"})
    assert resp.status_code == 401


async def test_login_unknown_email_is_unauthorized(client):
    resp = await client.post("/auth/login", json={"email": "ninguem@manta.com", "password": "qualquer"})
    assert resp.status_code == 401


async def test_login_multi_org_without_org_id_requires_selection(client, db_session):
    user = await _create_user(db_session, "multi@manta.com")
    org_a = await _create_org(db_session, "Org A", "org-a")
    org_b = await _create_org(db_session, "Org B", "org-b")
    await _grant(db_session, user, org_a, "member")
    await _grant(db_session, user, org_b, "owner")
    await db_session.commit()

    resp = await client.post("/auth/login", json={"email": "multi@manta.com", "password": "senha-super-secreta"})
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    org_ids = {o["org_id"] for o in detail["organizations"]}
    assert org_ids == {org_a.id, org_b.id}


async def test_login_multi_org_with_org_id_picks_that_org(client, db_session):
    user = await _create_user(db_session, "multi2@manta.com")
    org_a = await _create_org(db_session, "Org A2", "org-a2")
    org_b = await _create_org(db_session, "Org B2", "org-b2")
    await _grant(db_session, user, org_a, "member")
    await _grant(db_session, user, org_b, "owner")
    await db_session.commit()

    resp = await client.post(
        "/auth/login",
        json={"email": "multi2@manta.com", "password": "senha-super-secreta", "org_id": org_b.id},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["org_id"] == org_b.id
    assert body["roles"] == ["owner"]


async def test_login_org_id_not_a_member_is_forbidden(client, db_session):
    await _create_user(db_session, "naomembro@manta.com")
    org = await _create_org(db_session, "Org Alheia", "org-alheia")
    await db_session.commit()

    resp = await client.post(
        "/auth/login",
        json={"email": "naomembro@manta.com", "password": "senha-super-secreta", "org_id": org.id},
    )
    assert resp.status_code == 403


# --------------------------------------------------------------------------
# POST /auth/refresh
# --------------------------------------------------------------------------

async def test_refresh_issues_new_tokens_and_revokes_old(client):
    await client.post(
        "/auth/register",
        json={"email": "diana@manta.com", "password": "senha-1234", "org_name": "Org Diana"},
    )
    login = (await client.post("/auth/login", json={"email": "diana@manta.com", "password": "senha-1234"})).json()

    refreshed = await client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert refreshed.status_code == 200, refreshed.text
    new_tokens = refreshed.json()
    assert new_tokens["access_token"] != login["access_token"]
    assert new_tokens["refresh_token"] != login["refresh_token"]
    assert new_tokens["org_id"] == login["org_id"]
    assert new_tokens["roles"] == login["roles"]

    # Reuso do refresh token antigo (já rotacionado) deve falhar — mitiga
    # replay de um token vazado.
    reused = await client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert reused.status_code == 401


async def test_refresh_with_garbage_token_is_unauthorized(client):
    resp = await client.post("/auth/refresh", json={"refresh_token": "isto-nao-e-um-jwt"})
    assert resp.status_code == 401


async def test_refresh_rejects_an_access_token(client):
    """Um access token não pode ser usado no lugar de um refresh token
    (o claim `type` precisa bater)."""
    await client.post(
        "/auth/register",
        json={"email": "erico@manta.com", "password": "senha-1234", "org_name": "Org Erico"},
    )
    login = (await client.post("/auth/login", json={"email": "erico@manta.com", "password": "senha-1234"})).json()

    resp = await client.post("/auth/refresh", json={"refresh_token": login["access_token"]})
    assert resp.status_code == 401


# --------------------------------------------------------------------------
# GET /auth/me e GET /auth/orgs
# --------------------------------------------------------------------------

async def test_me_returns_profile_and_active_org(client):
    await client.post(
        "/auth/register",
        json={"email": "fabio@manta.com", "password": "senha-1234", "full_name": "Fábio", "org_name": "Org Fabio"},
    )
    login = (await client.post("/auth/login", json={"email": "fabio@manta.com", "password": "senha-1234"})).json()

    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {login['access_token']}"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["email"] == "fabio@manta.com"
    assert body["full_name"] == "Fábio"
    assert body["active_org"]["org_id"] == login["org_id"]
    assert body["organizations"][0]["roles"] == ["owner"]


async def test_me_without_token_is_unauthorized(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_orgs_lists_every_membership(client, db_session):
    user = await _create_user(db_session, "gil@manta.com")
    org_a = await _create_org(db_session, "Org Gil A", "org-gil-a")
    org_b = await _create_org(db_session, "Org Gil B", "org-gil-b")
    await _grant(db_session, user, org_a, "admin")
    await _grant(db_session, user, org_b, "viewer")
    await db_session.commit()

    login = (await client.post("/auth/login", json={
        "email": "gil@manta.com", "password": "senha-super-secreta", "org_id": org_a.id,
    })).json()

    resp = await client.get("/auth/orgs", headers={"Authorization": f"Bearer {login['access_token']}"})
    assert resp.status_code == 200
    orgs = {o["org_id"]: o["roles"] for o in resp.json()}
    assert orgs == {org_a.id: ["admin"], org_b.id: ["viewer"]}


# --------------------------------------------------------------------------
# RBAC multi-org (`require_roles`) ponta a ponta
# --------------------------------------------------------------------------

async def test_require_roles_allows_matching_role(client):
    await client.post(
        "/auth/register",
        json={"email": "helo@manta.com", "password": "senha-1234", "org_name": "Org Helo"},
    )
    login_owner = (await client.post("/auth/login", json={"email": "helo@manta.com", "password": "senha-1234"})).json()
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {login_owner['access_token']}"})
    org_id = me.json()["active_org"]["org_id"]

    # `register` concede "owner" automaticamente — a rota que exige
    # "owner" deve aceitar sem qualquer configuração extra.
    ok = await client.get("/protegido/somente-owner", headers={"Authorization": f"Bearer {login_owner['access_token']}"})
    assert ok.status_code == 200
    assert ok.json()["org_id"] == org_id


async def test_require_roles_end_to_end_blocks_and_allows(client, db_session):
    user = await _create_user(db_session, "irene@manta.com")
    org = await _create_org(db_session, "Org Irene", "org-irene")
    await _grant(db_session, user, org, "viewer")
    await db_session.commit()

    login = (await client.post("/auth/login", json={
        "email": "irene@manta.com", "password": "senha-super-secreta", "org_id": org.id,
    })).json()

    blocked = await client.get(
        "/protegido/somente-owner", headers={"Authorization": f"Bearer {login['access_token']}"}
    )
    assert blocked.status_code == 403

    # "admin-ou-owner" também bloqueia um "viewer" puro:
    blocked2 = await client.get(
        "/protegido/admin-ou-owner", headers={"Authorization": f"Bearer {login['access_token']}"}
    )
    assert blocked2.status_code == 403

    await _grant(db_session, user, org, "admin")
    await db_session.commit()

    # Access token antigo não tem "admin" no claim `roles`, mas
    # `require_roles` REVALIDA contra o banco via `get_current_org` — a
    # promoção tem efeito imediato mesmo sem novo login.
    allowed = await client.get(
        "/protegido/admin-ou-owner", headers={"Authorization": f"Bearer {login['access_token']}"}
    )
    assert allowed.status_code == 200
    assert set(allowed.json()["roles"]) == {"viewer", "admin"}


async def test_require_roles_org_switch_via_header(client, db_session):
    """Mesmo usuário, dois papéis diferentes em duas organizações
    diferentes — o header X-Org-Id decide qual organização (e qual
    conjunto de papéis) vale para aquele request específico."""
    user = await _create_user(db_session, "joao@manta.com")
    org_owner = await _create_org(db_session, "Org Joao Owner", "org-joao-owner")
    org_viewer = await _create_org(db_session, "Org Joao Viewer", "org-joao-viewer")
    await _grant(db_session, user, org_owner, "owner")
    await _grant(db_session, user, org_viewer, "viewer")
    await db_session.commit()

    login = (await client.post("/auth/login", json={
        "email": "joao@manta.com", "password": "senha-super-secreta", "org_id": org_viewer.id,
    })).json()
    token = login["access_token"]

    # Sem header: usa org_id do token (org_viewer) -> bloqueado.
    default_ctx = await client.get("/protegido/somente-owner", headers={"Authorization": f"Bearer {token}"})
    assert default_ctx.status_code == 403

    # Com header apontando para a org onde o usuário é owner -> permitido,
    # mesmo com o MESMO access token (a organização ativa é resolvida
    # por request, não fixada para sempre no token).
    switched = await client.get(
        "/protegido/somente-owner",
        headers={"Authorization": f"Bearer {token}", auth.settings.org_header_name: org_owner.id},
    )
    assert switched.status_code == 200
    assert switched.json()["org_id"] == org_owner.id


async def test_require_roles_rejects_non_member_org_in_header(client, db_session):
    user = await _create_user(db_session, "karen@manta.com")
    org_mine = await _create_org(db_session, "Org Karen", "org-karen")
    org_other = await _create_org(db_session, "Org Alheia Karen", "org-alheia-karen")
    await _grant(db_session, user, org_mine, "owner")
    await db_session.commit()

    login = (await client.post("/auth/login", json={
        "email": "karen@manta.com", "password": "senha-super-secreta", "org_id": org_mine.id,
    })).json()

    resp = await client.get(
        "/protegido/somente-owner",
        headers={"Authorization": f"Bearer {login['access_token']}", auth.settings.org_header_name: org_other.id},
    )
    assert resp.status_code == 403


async def test_require_roles_superuser_bypasses_role_check(client, db_session):
    user = await _create_user(db_session, "livia@manta.com")
    user.is_superuser = True
    org = await _create_org(db_session, "Org Livia", "org-livia")
    await _grant(db_session, user, org, "viewer")  # papel insuficiente de propósito
    await db_session.commit()

    login = (await client.post("/auth/login", json={
        "email": "livia@manta.com", "password": "senha-super-secreta", "org_id": org.id,
    })).json()

    resp = await client.get(
        "/protegido/somente-owner", headers={"Authorization": f"Bearer {login['access_token']}"}
    )
    assert resp.status_code == 200


async def test_require_roles_inactive_user_is_rejected(client, db_session):
    user = await _create_user(db_session, "mario@manta.com")
    org = await _create_org(db_session, "Org Mario", "org-mario")
    await _grant(db_session, user, org, "owner")
    await db_session.commit()

    login = (await client.post("/auth/login", json={
        "email": "mario@manta.com", "password": "senha-super-secreta", "org_id": org.id,
    })).json()

    user.is_active = False
    await db_session.commit()

    resp = await client.get(
        "/protegido/somente-owner", headers={"Authorization": f"Bearer {login['access_token']}"}
    )
    assert resp.status_code == 401
