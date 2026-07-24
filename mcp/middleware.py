"""
Middleware de autenticação e permissões para tools.

Extrai token do contexto e verifica scopes antes de executar.
"""

from functools import wraps
from typing import Any, Callable, Optional

from auth import get_token_manager, TokenPayload
from permissions import PermissionChecker, Scope


class AuthorizationError(Exception):
    """Erro de autorização."""

    pass


def require_scope(*required_scopes: Scope) -> Callable:
    """
    Decorator para verificar scopes antes de executar um tool.

    Args:
        required_scopes: lista de scopes necessários.

    Returns:
        Função decorada que valida scopes.

    Exemplo:
        @require_scope(Scope.EXECUTE_PYTHON, Scope.QUERY_SUPABASE)
        def my_tool(request, token_payload):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: Any, token: Optional[str] = None) -> Any:
            # Se não houver token, assume viewer (mais restritivo)
            if not token:
                return {
                    "error": "Authorization required (no token provided)",
                    "result": None,
                }

            # Validar token
            token_manager = get_token_manager()
            payload = token_manager.validate_token(token)
            if not payload:
                return {
                    "error": "Invalid or expired token",
                    "result": None,
                }

            # Verificar scopes
            if not PermissionChecker.check_scopes(
                payload.scope, list(required_scopes)
            ):
                missing = [
                    s.value
                    for s in required_scopes
                    if not PermissionChecker.check_scope(payload.scope, s)
                ]
                return {
                    "error": f"Insufficient permissions. Required: {missing}",
                    "result": None,
                }

            # Executar função com payload para auditoria
            return func(request, payload=payload)

        return wrapper

    return decorator


class RequestWithAuth:
    """Wrapper para adicionar autenticação a uma requisição."""

    def __init__(self, base_request: Any, token: Optional[str] = None):
        self.base_request = base_request
        self.token = token
        self._payload: Optional[TokenPayload] = None

    @property
    def payload(self) -> Optional[TokenPayload]:
        """Retorna o payload do token (validado)."""
        if self._payload is None and self.token:
            token_manager = get_token_manager()
            self._payload = token_manager.validate_token(self.token)
        return self._payload

    def has_scope(self, scope: Scope) -> bool:
        """Verifica se o token tem um escopo específico."""
        if not self.payload:
            return False
        return PermissionChecker.check_scope(self.payload.scope, scope)

    def __getattr__(self, name):
        """Delega atributos para base_request."""
        return getattr(self.base_request, name)


def check_permission(
    payload: TokenPayload, required_scopes: list[Scope]
) -> Optional[str]:
    """
    Verifica permissão e retorna mensagem de erro se falhada.

    Args:
        payload: TokenPayload do usuário.
        required_scopes: lista de scopes necessários.

    Returns:
        None se autorizado, ou mensagem de erro.
    """
    if not PermissionChecker.check_scopes(payload.scope, required_scopes):
        missing = [
            s.value
            for s in required_scopes
            if not PermissionChecker.check_scope(payload.scope, s)
        ]
        return f"Insufficient permissions. Required: {missing}"
    return None
