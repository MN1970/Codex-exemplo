"""Testes de logging estruturado."""

import json
import logging
from io import StringIO

import pytest

from logging_config import JSONFormatter, MantaBaseLogger, get_logger


class TestJSONFormatter:
    """Testes do formatter JSON."""

    def test_format_basic_log(self):
        """Formata log básico como JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_format_log_with_extra(self):
        """Adiciona campos extras no JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Query executed",
            args=(),
            exc_info=None,
        )
        record.user_email = "user@example.com"
        record.duration_ms = 125

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["user_email"] == "user@example.com"
        assert data["duration_ms"] == 125


class TestMantaBaseLogger:
    """Testes do logger centralizado."""

    def test_singleton_pattern(self):
        """Logger é singleton."""
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2

    def test_log_info(self):
        """Loga mensagem info."""
        logger = get_logger()
        logger.info("Test message", key="value")
        # Sem exception se não houver erro

    def test_log_error(self):
        """Loga mensagem error."""
        logger = get_logger()
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.error("Error occurred", error_code="ERR_TEST")
        # Sem exception se não houver erro

    def test_log_query(self):
        """Loga execução de query."""
        logger = get_logger()
        logger.log_query(
            user_email="user@example.com",
            query_hash="abc12345",
            duration_ms=150,
            row_count=42,
        )
        # Sem exception se não houver erro

    def test_log_execute(self):
        """Loga execução de código."""
        logger = get_logger()
        logger.log_execute(
            user_email="user@example.com",
            code_hash="xyz98765",
            duration_ms=300,
        )
        # Sem exception se não houver erro

    def test_log_auth_failure(self):
        """Loga falha de autenticação."""
        logger = get_logger()
        logger.log_auth_failure("INVALID_TOKEN", token="abc...")
        # Sem exception se não houver erro

    def test_log_permission_denied(self):
        """Loga negação de permissão."""
        logger = get_logger()
        logger.log_permission_denied(
            user_email="user@example.com",
            scope="execute.python",
            action="execute_code",
        )
        # Sem exception se não houver erro


class TestLoggingIntegration:
    """Testes de integração com tools."""

    def test_logging_available_in_tools(self):
        """Logger está disponível para tools."""
        from logging_config import get_logger

        logger = get_logger()
        assert logger is not None
        assert hasattr(logger, "log_query")
        assert hasattr(logger, "log_execute")
