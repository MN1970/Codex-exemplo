"""Testes de middleware de autenticação e permissões."""

import pytest

from auth import get_token_manager
from middleware import check_permission, RequestWithAuth
from permissions import PermissionChecker, Role, RolePermissions, Scope


class TestCheckPermission:
    """Testes da função check_permission."""

    def test_admin_has_all_permissions(self):
        """Admin tem todas as permissões."""
        token_mgr = get_token_manager()
        token = token_mgr.issue_token(
            user_email="admin@mantaassociados.com",
            scopes=[s.value for s in RolePermissions.for_admin().scopes],
        )
        payload = token_mgr.validate_token(token)

        # Verificar qualquer scope
        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is None

    def test_user_cannot_execute_python(self):
        """User não pode usar execute.python (apenas sandboxed)."""
        token_mgr = get_token_manager()
        token = token_mgr.issue_token(
            user_email="user@mantaassociados.com",
            scopes=[s.value for s in RolePermissions.for_user().scopes],
        )
        payload = token_mgr.validate_token(token)

        # Tentar acessar execute.python
        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is not None
        assert "Insufficient permissions" in error

    def test_viewer_cannot_execute(self):
        """Viewer não pode executar nada."""
        token_mgr = get_token_manager()
        token = token_mgr.issue_token(
            user_email="viewer@mantaassociados.com",
            scopes=[s.value for s in RolePermissions.for_viewer().scopes],
        )
        payload = token_mgr.validate_token(token)

        # Tentar acessar execute
        error = check_permission(payload, [Scope.EXECUTE_SANDBOXED])
        assert error is not None

    def test_multiple_required_scopes(self):
        """Verifica múltiplos scopes necessários."""
        token_mgr = get_token_manager()
        token = token_mgr.issue_token(
            user_email="user@mantaassociados.com",
            scopes=["execute.sandboxed", "query.supabase"],
        )
        payload = token_mgr.validate_token(token)

        # Ambos os scopes estão presentes
        error = check_permission(
            payload, [Scope.EXECUTE_SANDBOXED, Scope.QUERY_SUPABASE]
        )
        assert error is None

        # Um dos scopes falta
        error = check_permission(
            payload,
            [Scope.EXECUTE_SANDBOXED, Scope.SHAREPOINT_WRITE],
        )
        assert error is not None


class TestRequestWithAuth:
    """Testes do wrapper RequestWithAuth."""

    def test_has_scope_true(self):
        """Verifica se tem um scope específico."""
        token_mgr = get_token_manager()
        token = token_mgr.issue_token(
            user_email="user@mantaassociados.com",
            scopes=["execute.sandboxed", "query.supabase"],
        )

        class MockRequest:
            pass

        req = RequestWithAuth(MockRequest(), token=token)
        assert req.has_scope(Scope.QUERY_SUPABASE) is True
        assert req.has_scope(Scope.EXECUTE_PYTHON) is False

    def test_has_scope_no_token(self):
        """Sem token, retorna False."""
        class MockRequest:
            pass

        req = RequestWithAuth(MockRequest(), token=None)
        assert req.has_scope(Scope.QUERY_SUPABASE) is False

    def test_payload_property(self):
        """Propriedade payload retorna TokenPayload validado."""
        token_mgr = get_token_manager()
        token = token_mgr.issue_token(
            user_email="test@mantaassociados.com",
            scopes=["query.supabase"],
        )

        class MockRequest:
            pass

        req = RequestWithAuth(MockRequest(), token=token)
        assert req.payload is not None
        assert req.payload.sub == "test@mantaassociados.com"

    def test_getattr_delegation(self):
        """Atributos são delegados para base_request."""
        class MockRequest:
            def __init__(self):
                self.custom_attr = "custom_value"

        req = RequestWithAuth(MockRequest())
        assert req.custom_attr == "custom_value"


class TestPermissionFlowE2E:
    """Teste de fluxo ponta-a-ponta: token → payload → permissão."""

    def test_admin_execute_flow(self):
        """Admin: emite token, valida, verifica permissão para execute.python."""
        token_mgr = get_token_manager()

        # 1. Admin emite token
        token = token_mgr.issue_token(
            user_email="admin@mantaassociados.com",
            scopes=[s.value for s in RolePermissions.for_admin().scopes],
        )
        assert token is not None

        # 2. Token é validado
        payload = token_mgr.validate_token(token)
        assert payload is not None
        assert payload.sub == "admin@mantaassociados.com"

        # 3. Verifica permissão para execute.python
        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is None  # Autorizado

    def test_user_cannot_execute_python_flow(self):
        """User: token válido, mas sem permissão para execute.python."""
        token_mgr = get_token_manager()

        # 1. User emite token
        token = token_mgr.issue_token(
            user_email="user@mantaassociados.com",
            scopes=[s.value for s in RolePermissions.for_user().scopes],
        )

        # 2. Token é validado
        payload = token_mgr.validate_token(token)
        assert payload is not None

        # 3. Verifica permissão — falha
        error = check_permission(payload, [Scope.EXECUTE_PYTHON])
        assert error is not None  # Negado
        assert "Insufficient permissions" in error
