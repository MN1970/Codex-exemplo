"""
CORS configuration para MantaBase MCP v2.

Controla acesso cross-origin de forma segura.
"""

import os
from enum import Enum
from typing import Optional


class Environment(str, Enum):
    """Ambientes suportados."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class CORSConfig:
    """Configuração de CORS por ambiente."""

    def __init__(self, environment: Optional[str] = None):
        """
        Args:
            environment: 'development', 'staging', ou 'production'.
                         Padrão: env ENVIRONMENT.
        """
        self.environment = environment or os.getenv("ENVIRONMENT", "development")

    @property
    def allowed_origins(self) -> list[str]:
        """Retorna lista de origins permitidos."""
        if self.environment == Environment.PRODUCTION:
            return [
                "https://hub.mantaassociados.com",
                "https://app.mantaassociados.com",
            ]
        elif self.environment == Environment.STAGING:
            return [
                "https://staging.mantaassociados.com",
                "https://dev.mantaassociados.com",
                "http://localhost:3000",
                "http://localhost:3001",
            ]
        else:  # development
            return [
                "http://localhost:*",
                "http://127.0.0.1:*",
                "*",  # allow all em dev
            ]

    @property
    def allowed_methods(self) -> list[str]:
        """Métodos HTTP permitidos."""
        return ["GET", "POST", "OPTIONS"]

    @property
    def allowed_headers(self) -> list[str]:
        """Headers HTTP permitidos."""
        return [
            "Content-Type",
            "Authorization",
            "Accept",
            "X-Request-ID",
        ]

    @property
    def expose_headers(self) -> list[str]:
        """Headers a expor ao cliente."""
        return [
            "Content-Type",
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]

    @property
    def max_age(self) -> int:
        """Cache de preflight em segundos."""
        if self.environment == Environment.PRODUCTION:
            return 86400  # 24 horas
        elif self.environment == Environment.STAGING:
            return 3600  # 1 hora
        else:  # development
            return 600  # 10 minutos

    @property
    def allow_credentials(self) -> bool:
        """Permitir credentials (cookies, auth)."""
        return True

    def get_middleware_config(self) -> dict:
        """Retorna configuração pronta para middleware CORS."""
        return {
            "allow_origins": self.allowed_origins,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
            "expose_headers": self.expose_headers,
            "max_age": self.max_age,
            "allow_credentials": self.allow_credentials,
        }


def create_cors_headers(origin: str, config: Optional[CORSConfig] = None) -> dict:
    """
    Cria headers CORS para uma requisição.

    Args:
        origin: origin da requisição (do header Origin).
        config: CORSConfig opcional.

    Returns:
        Dict de headers CORS.
    """
    if config is None:
        config = CORSConfig()

    # Verificar se origin é permitido
    allowed = config.allowed_origins
    origin_allowed = False

    for allowed_origin in allowed:
        if allowed_origin == "*":
            origin_allowed = True
            break
        elif allowed_origin.endswith(":*"):
            # Permitir localhost com qualquer porta
            prefix = allowed_origin[:-2]
            if origin.startswith(prefix):
                origin_allowed = True
                break
        elif origin == allowed_origin:
            origin_allowed = True
            break

    headers = {}

    if origin_allowed:
        headers["Access-Control-Allow-Origin"] = origin if origin in allowed else allowed[0]
        headers["Access-Control-Allow-Methods"] = ", ".join(config.allowed_methods)
        headers["Access-Control-Allow-Headers"] = ", ".join(config.allowed_headers)
        headers["Access-Control-Expose-Headers"] = ", ".join(config.expose_headers)
        headers["Access-Control-Max-Age"] = str(config.max_age)
        if config.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

    return headers
