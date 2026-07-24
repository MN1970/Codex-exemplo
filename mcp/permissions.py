"""
Modelo de permissões granulares para execute() e query().

Suporta 3 roles: admin, user, viewer.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Role(str, Enum):
    """Roles de acesso."""

    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class Scope(str, Enum):
    """Scopes de permissão."""

    EXECUTE_PYTHON = "execute.python"
    EXECUTE_SANDBOXED = "execute.sandboxed"
    QUERY_SUPABASE = "query.supabase"
    QUERY_SHAREPOINT = "query.sharepoint"
    SHAREPOINT_WRITE = "sharepoint.write"
    SKILLS_READ = "skills.read"
    SKILLS_WRITE = "skills.write"


class RolePermissions(BaseModel):
    """Mapeamento de role → scopes."""

    role: Role
    scopes: list[Scope]

    @staticmethod
    def for_admin() -> "RolePermissions":
        """Admin: acesso total."""
        return RolePermissions(
            role=Role.ADMIN,
            scopes=[
                Scope.EXECUTE_PYTHON,
                Scope.EXECUTE_SANDBOXED,
                Scope.QUERY_SUPABASE,
                Scope.QUERY_SHAREPOINT,
                Scope.SHAREPOINT_WRITE,
                Scope.SKILLS_READ,
                Scope.SKILLS_WRITE,
            ],
        )

    @staticmethod
    def for_user() -> "RolePermissions":
        """User: execução + leitura."""
        return RolePermissions(
            role=Role.USER,
            scopes=[
                Scope.EXECUTE_SANDBOXED,
                Scope.QUERY_SUPABASE,
                Scope.QUERY_SHAREPOINT,
                Scope.SKILLS_READ,
            ],
        )

    @staticmethod
    def for_viewer() -> "RolePermissions":
        """Viewer: somente leitura."""
        return RolePermissions(
            role=Role.VIEWER,
            scopes=[
                Scope.QUERY_SUPABASE,
                Scope.SKILLS_READ,
            ],
        )


class PermissionChecker:
    """Verifica permissões contra um token/role."""

    @staticmethod
    def check_scope(scopes: list[str], required_scope: Scope) -> bool:
        """
        Verifica se um dos scopes fornecidos contém a permissão.

        Args:
            scopes: lista de scopes do token.
            required_scope: escopo necessário.

        Returns:
            True se autorizado.
        """
        return required_scope.value in scopes

    @staticmethod
    def check_scopes(scopes: list[str], required_scopes: list[Scope]) -> bool:
        """
        Verifica se todos os scopes necessários estão presentes.

        Args:
            scopes: lista de scopes do token.
            required_scopes: lista de escopos necessários.

        Returns:
            True se todos os escopos estão presentes.
        """
        return all(PermissionChecker.check_scope(scopes, s) for s in required_scopes)

    @staticmethod
    def get_role_from_scopes(scopes: list[str]) -> Optional[Role]:
        """
        Tenta inferir role a partir dos scopes.

        Args:
            scopes: lista de scopes.

        Returns:
            Role inferido, ou None se ambíguo.
        """
        admin_perms = RolePermissions.for_admin()
        user_perms = RolePermissions.for_user()
        viewer_perms = RolePermissions.for_viewer()

        scopes_set = set(scopes)
        admin_set = {s.value for s in admin_perms.scopes}
        user_set = {s.value for s in user_perms.scopes}
        viewer_set = {s.value for s in viewer_perms.scopes}

        if scopes_set >= admin_set:
            return Role.ADMIN
        elif scopes_set >= user_set:
            return Role.USER
        elif scopes_set >= viewer_set:
            return Role.VIEWER

        return None
