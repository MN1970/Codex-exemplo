"""
Logging estruturado para MantaBase MCP v2.

Integra python logging + Sentry para monitoramento.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """Formatter que serializa logs em JSON estruturado."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Formata log como JSON.

        Fields:
        - timestamp: ISO 8601
        - level: DEBUG, INFO, WARNING, ERROR, CRITICAL
        - logger: nome do módulo
        - message: mensagem
        - exc_info: stack trace (se houver)
        - extra: dados customizados
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        # Adicionar campos extras
        if hasattr(record, "user_email"):
            log_data["user_email"] = record.user_email
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code

        return json.dumps(log_data)


class MantaBaseLogger:
    """Logger centralizado para MCP v2."""

    _instance: Optional["MantaBaseLogger"] = None

    def __new__(cls) -> "MantaBaseLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.logger = logging.getLogger("mantabase-mcp-v2")
        self.logger.setLevel(logging.DEBUG)

        # Remove handlers padrão
        self.logger.handlers.clear()

        # Handler para stdout (JSON estruturado)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(stdout_handler)

        # Inicializar Sentry se disponível
        self.setup_sentry()

    @staticmethod
    def setup_sentry():
        """Inicializa Sentry para erro tracking."""
        if not SENTRY_AVAILABLE:
            return

        sentry_dsn = os.getenv("SENTRY_DSN")
        if not sentry_dsn:
            return

        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR,
                )
            ],
            traces_sample_rate=0.1,  # 10% sampling
            environment=os.getenv("ENVIRONMENT", "development"),
        )

    def debug(self, message: str, **kwargs):
        """Log debug com dados estruturados."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info com dados estruturados."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning com dados estruturados."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error com dados estruturados."""
        self.logger.error(message, extra=kwargs, exc_info=True)

    def critical(self, message: str, **kwargs):
        """Log critical com dados estruturados."""
        self.logger.critical(message, extra=kwargs, exc_info=True)

    def log_query(
        self,
        user_email: str,
        query_hash: str,
        duration_ms: int,
        row_count: int,
        error: Optional[str] = None,
    ):
        """Loga execução de query."""
        self.info(
            "Query executed",
            user_email=user_email,
            query_hash=query_hash,
            duration_ms=duration_ms,
            row_count=row_count,
            error_code=error,
        )

    def log_execute(
        self,
        user_email: str,
        code_hash: str,
        duration_ms: int,
        error: Optional[str] = None,
    ):
        """Loga execução de código."""
        self.info(
            "Code executed",
            user_email=user_email,
            code_hash=code_hash,
            duration_ms=duration_ms,
            error_code=error,
        )

    def log_auth_failure(self, reason: str, **kwargs):
        """Loga falha de autenticação."""
        self.warning("Auth failure", error_code=reason, **kwargs)

    def log_permission_denied(self, user_email: str, scope: str, action: str):
        """Loga negação de permissão."""
        self.warning(
            "Permission denied",
            user_email=user_email,
            scope=scope,
            action=action,
        )


# Singleton global
_logger: Optional[MantaBaseLogger] = None


def get_logger() -> MantaBaseLogger:
    """Retorna a instância global do logger."""
    global _logger
    if _logger is None:
        _logger = MantaBaseLogger()
    return _logger


# Função conveniente
def log_info(message: str, **kwargs):
    """Log info global."""
    get_logger().info(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error global."""
    get_logger().error(message, **kwargs)
