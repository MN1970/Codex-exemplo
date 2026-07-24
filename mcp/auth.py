"""
SSA-equivalente authentication: JWT de curta duração + renovação automática.

Modelo: emissão de token sem intervenção humana, renovação automática.
Resolve: bloqueador compartilhado (MantaBase + SharePoint write).
"""

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from pydantic import BaseModel


class TokenPayload(BaseModel):
    """Payload de um token JWT."""

    sub: str  # subject (user email)
    iss: str  # issuer (sempre "mantabase-mcp-v2")
    aud: str  # audience (scope, ex: "execute", "query", "sharepoint")
    exp: int  # expiration (unix timestamp)
    iat: int  # issued at
    nbf: int  # not before
    scope: list[str]  # permissões (["execute.python", "query.supabase", "sharepoint.write"])


class TokenManager:
    """Gerencia emissão, validação e renovação de tokens SSA-equivalentes."""

    def __init__(self, secret_key: Optional[str] = None, ttl_seconds: int = 3600):
        """
        Args:
            secret_key: chave privada para assinar tokens. Padrão: env MANTABASE_SECRET_KEY.
            ttl_seconds: tempo de vida do token em segundos. Padrão: 1 hora.
        """
        self.secret_key = secret_key or os.getenv("MANTABASE_SECRET_KEY", "default-dev-key")
        self.ttl_seconds = ttl_seconds
        self.algorithm = "HS256"

    def issue_token(
        self,
        user_email: str,
        scopes: list[str],
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """
        Emite um novo token JWT.

        Args:
            user_email: email do usuário (ex: mneves@mantaassociados.com)
            scopes: lista de permissões (ex: ["execute.python", "query.supabase"])
            ttl_seconds: override do TTL. Padrão: self.ttl_seconds.

        Returns:
            Token JWT assinado.
        """
        now = datetime.now(timezone.utc)
        ttl = ttl_seconds or self.ttl_seconds

        payload = TokenPayload(
            sub=user_email,
            iss="mantabase-mcp-v2",
            aud="mcp-core",
            iat=int(now.timestamp()),
            nbf=int(now.timestamp()),
            exp=int((now + timedelta(seconds=ttl)).timestamp()),
            scope=scopes,
        )

        token = jwt.encode(
            payload.model_dump(),
            self.secret_key,
            algorithm=self.algorithm,
        )

        return token

    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """
        Valida e decodifica um token JWT.

        Args:
            token: token JWT a validar.

        Returns:
            TokenPayload se válido, None se expirado/inválido.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True},
            )
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def is_token_expiring_soon(self, token: str, threshold_seconds: int = 300) -> bool:
        """
        Verifica se um token está próximo de expirar.

        Args:
            token: token JWT.
            threshold_seconds: margem (padrão: 5 minutos).

        Returns:
            True se o token expira em menos de `threshold_seconds`.
        """
        payload = self.validate_token(token)
        if not payload:
            return True

        time_until_exp = payload.exp - int(time.time())
        return time_until_exp < threshold_seconds

    def refresh_token(self, old_token: str, new_scopes: Optional[list[str]] = None) -> Optional[str]:
        """
        Renova um token válido (mas possivelmente próximo de expirar).

        Args:
            old_token: token anterior.
            new_scopes: scopes para o novo token (padrão: mantém os antigos).

        Returns:
            Novo token se o anterior era válido, None caso contrário.
        """
        payload = self.validate_token(old_token)
        if not payload:
            return None

        scopes = new_scopes or payload.scope
        return self.issue_token(payload.sub, scopes)


# Instância global (singleton).
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """Retorna a instância global do TokenManager."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager
