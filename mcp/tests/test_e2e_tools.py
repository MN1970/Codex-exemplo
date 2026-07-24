"""Testes E2E: simulação de requests aos tools com permissões."""

import pytest

from auth import get_token_manager
from permissions import RolePermissions, Scope


class TestExecuteWithPermissions:
    """Testes de execute() com validação de permissões."""

    @pytest.fixture
    def token_mgr(self):
        return get_token_manager()

    @pytest.fixture
    def admin_token(self, token_mgr):
        return token_mgr.issue_token(
            user_email="admin@test.com",
            scopes=[s.value for s in RolePermissions.for_admin().scopes],
        )

    @pytest.fixture
    def user_token(self, token_mgr):
        return token_mgr.issue_token(
            user_email="user@test.com",
            scopes=[s.value for s in RolePermissions.for_user().scopes],
        )

    @pytest.fixture
    def viewer_token(self, token_mgr):
        return token_mgr.issue_token(
            user_email="viewer@test.com",
            scopes=[s.value for s in RolePermissions.for_viewer().scopes],
        )

    def test_execute_admin_with_python_code(self, admin_token):
        """Admin pode executar código Python."""
        # Simulação: request to execute() com token admin
        code = "result = 1 + 1"

        # Verifica que admin tem permissão
        from middleware import check_permission
        from permissions import Scope

        payload = get_token_manager().validate_token(admin_token)
        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is None  # Autorizado

    def test_execute_user_with_sandboxed_only(self, user_token):
        """User pode usar execute.sandboxed, não execute.python."""
        from middleware import check_permission
        from permissions import Scope

        payload = get_token_manager().validate_token(user_token)

        # Não pode usar execute.python
        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is not None

        # Pode usar execute.sandboxed
        error = check_permission(payload, [Scope.EXECUTE_SANDBOXED])
        assert error is None

    def test_execute_viewer_denied(self, viewer_token):
        """Viewer não pode executar código."""
        from middleware import check_permission
        from permissions import Scope

        payload = get_token_manager().validate_token(viewer_token)

        # Não pode usar nenhum execute
        error = check_permission(payload, [Scope.EXECUTE_SANDBOXED])
        assert error is not None

        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is not None


class TestQueryWithPermissions:
    """Testes de query() com validação de permissões."""

    @pytest.fixture
    def token_mgr(self):
        return get_token_manager()

    @pytest.fixture
    def admin_token(self, token_mgr):
        return token_mgr.issue_token(
            user_email="admin@test.com",
            scopes=[s.value for s in RolePermissions.for_admin().scopes],
        )

    @pytest.fixture
    def user_token(self, token_mgr):
        return token_mgr.issue_token(
            user_email="user@test.com",
            scopes=[s.value for s in RolePermissions.for_user().scopes],
        )

    @pytest.fixture
    def viewer_token(self, token_mgr):
        return token_mgr.issue_token(
            user_email="viewer@test.com",
            scopes=[s.value for s in RolePermissions.for_viewer().scopes],
        )

    def test_query_admin_allowed(self, admin_token):
        """Admin pode fazer query."""
        from middleware import check_permission
        from permissions import Scope

        payload = get_token_manager().validate_token(admin_token)
        error = check_permission(payload, [Scope.QUERY_SUPABASE])
        assert error is None

    def test_query_user_allowed(self, user_token):
        """User pode fazer query."""
        from middleware import check_permission
        from permissions import Scope

        payload = get_token_manager().validate_token(user_token)
        error = check_permission(payload, [Scope.QUERY_SUPABASE])
        assert error is None

    def test_query_viewer_allowed(self, viewer_token):
        """Viewer pode fazer query (read-only)."""
        from middleware import check_permission
        from permissions import Scope

        payload = get_token_manager().validate_token(viewer_token)
        error = check_permission(payload, [Scope.QUERY_SUPABASE])
        assert error is None

    def test_sharepoint_write_only_admin(self, user_token, admin_token):
        """Somente admin pode escrever no SharePoint."""
        from middleware import check_permission
        from permissions import Scope

        # User não pode
        payload = get_token_manager().validate_token(user_token)
        error = check_permission(payload, [Scope.SHAREPOINT_WRITE])
        assert error is not None

        # Admin pode
        payload = get_token_manager().validate_token(admin_token)
        error = check_permission(payload, [Scope.SHAREPOINT_WRITE])
        assert error is None


class TestTokenExpiration:
    """Testes de comportamento com tokens expirados."""

    def test_execute_with_expired_token(self):
        """Execute com token expirado é rejeitado."""
        from middleware import check_permission
        from permissions import Scope

        token_mgr = get_token_manager(ttl_seconds=1)
        token = token_mgr.issue_token(
            user_email="test@test.com",
            scopes=[s.value for s in RolePermissions.for_admin().scopes],
        )

        import time
        time.sleep(2)

        # Token expirado não valida
        payload = token_mgr.validate_token(token)
        assert payload is None

    def test_query_with_expired_token(self):
        """Query com token expirado é rejeitado."""
        token_mgr = get_token_manager(ttl_seconds=1)
        token = token_mgr.issue_token(
            user_email="test@test.com",
            scopes=[s.value for s in RolePermissions.for_admin().scopes],
        )

        import time
        time.sleep(2)

        payload = token_mgr.validate_token(token)
        assert payload is None
