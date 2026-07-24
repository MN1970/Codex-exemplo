"""Testes de modelo de permissões granulares."""

import pytest

from permissions import PermissionChecker, Role, RolePermissions, Scope


class TestRolePermissions:
    """Testes de mapeamento role → scopes."""

    def test_admin_permissions(self):
        """Admin tem acesso total."""
        perms = RolePermissions.for_admin()
        assert perms.role == Role.ADMIN
        assert len(perms.scopes) == 7  # todos os scopes

    def test_user_permissions(self):
        """User tem execução + leitura (sem write)."""
        perms = RolePermissions.for_user()
        assert perms.role == Role.USER
        assert Scope.EXECUTE_SANDBOXED in perms.scopes
        assert Scope.QUERY_SUPABASE in perms.scopes
        assert Scope.SHAREPOINT_WRITE not in perms.scopes

    def test_viewer_permissions(self):
        """Viewer tem somente leitura."""
        perms = RolePermissions.for_viewer()
        assert perms.role == Role.VIEWER
        assert Scope.QUERY_SUPABASE in perms.scopes
        assert Scope.EXECUTE_SANDBOXED not in perms.scopes
        assert Scope.SHAREPOINT_WRITE not in perms.scopes


class TestPermissionChecker:
    """Testes de verificação de permissões."""

    def test_check_single_scope(self):
        """Verifica se um scope está presente."""
        scopes = ["execute.python", "query.supabase", "sharepoint.write"]
        assert PermissionChecker.check_scope(scopes, Scope.EXECUTE_PYTHON) is True
        assert PermissionChecker.check_scope(scopes, Scope.SKILLS_WRITE) is False

    def test_check_multiple_scopes(self):
        """Verifica se todos os scopes requeridos estão presentes."""
        scopes = ["execute.sandboxed", "query.supabase", "skills.read"]
        required = [Scope.EXECUTE_SANDBOXED, Scope.QUERY_SUPABASE]
        assert PermissionChecker.check_scopes(scopes, required) is True

        required = [Scope.EXECUTE_SANDBOXED, Scope.SHAREPOINT_WRITE]
        assert PermissionChecker.check_scopes(scopes, required) is False

    def test_infer_admin_role(self):
        """Infere role ADMIN a partir dos scopes."""
        admin_scopes = [s.value for s in RolePermissions.for_admin().scopes]
        inferred = PermissionChecker.get_role_from_scopes(admin_scopes)
        assert inferred == Role.ADMIN

    def test_infer_user_role(self):
        """Infere role USER a partir dos scopes."""
        user_scopes = [s.value for s in RolePermissions.for_user().scopes]
        inferred = PermissionChecker.get_role_from_scopes(user_scopes)
        assert inferred == Role.USER

    def test_infer_viewer_role(self):
        """Infere role VIEWER a partir dos scopes."""
        viewer_scopes = [s.value for s in RolePermissions.for_viewer().scopes]
        inferred = PermissionChecker.get_role_from_scopes(viewer_scopes)
        assert inferred == Role.VIEWER

    def test_ambiguous_scopes_return_none(self):
        """Scopes ambíguous retornam None."""
        scopes = ["skills.read", "unknown.scope"]
        inferred = PermissionChecker.get_role_from_scopes(scopes)
        assert inferred is None


class TestExecuteWithPermissions:
    """Testes de execute() com validação de permissões."""

    def test_admin_can_execute_python(self):
        """Admin pode executar execute.python."""
        admin_scopes = [s.value for s in RolePermissions.for_admin().scopes]
        can_execute = PermissionChecker.check_scope(admin_scopes, Scope.EXECUTE_PYTHON)
        assert can_execute is True

    def test_user_cannot_execute_python(self):
        """User não pode executar execute.python (apenas sandboxed)."""
        user_scopes = [s.value for s in RolePermissions.for_user().scopes]
        can_execute = PermissionChecker.check_scope(user_scopes, Scope.EXECUTE_PYTHON)
        assert can_execute is False

    def test_viewer_cannot_execute(self):
        """Viewer não pode executar nada."""
        viewer_scopes = [s.value for s in RolePermissions.for_viewer().scopes]
        can_execute = PermissionChecker.check_scope(viewer_scopes, Scope.EXECUTE_SANDBOXED)
        assert can_execute is False


class TestQueryWithPermissions:
    """Testes de query() com validação de permissões."""

    def test_user_can_query_supabase(self):
        """User pode fazer query no Supabase."""
        user_scopes = [s.value for s in RolePermissions.for_user().scopes]
        can_query = PermissionChecker.check_scope(user_scopes, Scope.QUERY_SUPABASE)
        assert can_query is True

    def test_viewer_can_query_supabase(self):
        """Viewer pode fazer query no Supabase."""
        viewer_scopes = [s.value for s in RolePermissions.for_viewer().scopes]
        can_query = PermissionChecker.check_scope(viewer_scopes, Scope.QUERY_SUPABASE)
        assert can_query is True

    def test_viewer_cannot_query_sharepoint(self):
        """Viewer não pode fazer query no SharePoint."""
        viewer_scopes = [s.value for s in RolePermissions.for_viewer().scopes]
        can_query = PermissionChecker.check_scope(viewer_scopes, Scope.QUERY_SHAREPOINT)
        assert can_query is False
