"""Testes de autenticação SSA-equivalente (P3)."""

import time

import pytest

from auth import TokenManager, TokenPayload


@pytest.fixture
def token_manager():
    return TokenManager(secret_key="test-secret-key", ttl_seconds=3600)


class TestTokenIssue:
    """Testes de emissão de tokens."""

    def test_issue_token(self, token_manager):
        """Emissão básica."""
        token = token_manager.issue_token(
            user_email="test@mantaassociados.com",
            scopes=["execute.python", "query.supabase"],
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_issue_token_structure(self, token_manager):
        """Valida payload do token."""
        token = token_manager.issue_token(
            user_email="mneves@mantaassociados.com",
            scopes=["execute.python"],
        )
        payload = token_manager.validate_token(token)
        assert payload is not None
        assert payload.sub == "mneves@mantaassociados.com"
        assert payload.iss == "mantabase-mcp-v2"
        assert payload.scope == ["execute.python"]


class TestTokenValidation:
    """Testes de validação de tokens."""

    def test_validate_valid_token(self, token_manager):
        """Validação de token válido."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
        )
        payload = token_manager.validate_token(token)
        assert payload is not None
        assert payload.sub == "test@example.com"

    def test_validate_expired_token(self, token_manager):
        """Token expirado retorna None."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
            ttl_seconds=1,  # expira em 1 segundo
        )
        time.sleep(2)
        payload = token_manager.validate_token(token)
        assert payload is None

    def test_validate_malformed_token(self, token_manager):
        """Token malformado retorna None."""
        payload = token_manager.validate_token("not-a-valid-token")
        assert payload is None


class TestTokenExpiration:
    """Testes de verificação de expiração."""

    def test_is_token_expiring_soon_false(self, token_manager):
        """Token recém-emitido não está expirando."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
            ttl_seconds=3600,
        )
        assert token_manager.is_token_expiring_soon(token, threshold_seconds=300) is False

    def test_is_token_expiring_soon_true(self, token_manager):
        """Token próximo de expirar."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
            ttl_seconds=100,
        )
        assert token_manager.is_token_expiring_soon(token, threshold_seconds=200) is True


class TestTokenRefresh:
    """Testes de renovação de tokens."""

    def test_refresh_valid_token(self, token_manager):
        """Renova um token válido."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
        )
        refreshed = token_manager.refresh_token(token)
        assert refreshed is not None
        assert refreshed != token  # novo token

        payload = token_manager.validate_token(refreshed)
        assert payload is not None
        assert payload.sub == "test@example.com"

    def test_refresh_expired_token(self, token_manager):
        """Renovação de token expirado falha."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
            ttl_seconds=1,
        )
        time.sleep(2)
        refreshed = token_manager.refresh_token(token)
        assert refreshed is None

    def test_refresh_with_new_scopes(self, token_manager):
        """Renovação com novos scopes."""
        token = token_manager.issue_token(
            user_email="test@example.com",
            scopes=["execute.python"],
        )
        refreshed = token_manager.refresh_token(
            token,
            new_scopes=["execute.python", "query.supabase", "sharepoint.write"],
        )
        payload = token_manager.validate_token(refreshed)
        assert "sharepoint.write" in payload.scope


class TestSSAFlow:
    """Teste de fluxo completo SSA (sem intervenção humana)."""

    def test_ssa_issue_validate_refresh_cycle(self, token_manager):
        """Ciclo completo: emitir → validar → renovar."""
        # 1. Emitir token de curta duração
        token = token_manager.issue_token(
            user_email="mneves@mantaassociados.com",
            scopes=["execute.python", "query.supabase"],
            ttl_seconds=30,
        )

        # 2. Usar token
        payload = token_manager.validate_token(token)
        assert payload is not None

        # 3. Verificar se está próximo de expirar (threshold: 25s)
        should_refresh = token_manager.is_token_expiring_soon(token, threshold_seconds=25)
        # Não deve expirar em 5 segundos

        if should_refresh:
            # 4. Renovar automaticamente
            new_token = token_manager.refresh_token(token)
            assert new_token is not None

            # 5. Usar novo token
            new_payload = token_manager.validate_token(new_token)
            assert new_payload is not None
            assert new_payload.sub == "mneves@mantaassociados.com"
