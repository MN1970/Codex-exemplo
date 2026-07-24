"""Testes de integração rate limiting + CORS."""

import pytest
from unittest.mock import patch, MagicMock

from rate_limiting import RateLimitExceeded, InMemoryRateLimiter
from cors_config import CORSConfig, Environment


class TestCORSConfig:
    """Testes de configuração CORS."""

    def test_cors_config_by_environment(self):
        """CORSConfig ajusta headers por ambiente."""
        # Development
        dev_config = CORSConfig(environment="development")
        dev_headers = dev_config.allowed_origins
        assert "*" in dev_headers or any("*" in origin for origin in dev_headers)

        # Production
        prod_config = CORSConfig(environment="production")
        prod_headers = prod_config.allowed_origins
        assert "https://hub.mantaassociados.com" in prod_headers
        assert "https://app.mantaassociados.com" in prod_headers
        assert "*" not in prod_headers

        # Staging
        staging_config = CORSConfig(environment="staging")
        staging_headers = staging_config.allowed_origins
        assert "https://staging.mantaassociados.com" in staging_headers
        assert "http://localhost:3000" in staging_headers

    def test_cors_response_structure(self):
        """Respostas CORS têm estrutura correta."""
        config = CORSConfig(environment="development")
        headers = config.get_middleware_config()

        assert "allow_origins" in headers
        assert "allow_methods" in headers
        assert "allow_headers" in headers
        assert "expose_headers" in headers
        assert "max_age" in headers
        assert "allow_credentials" in headers

        assert isinstance(headers["allow_origins"], list)
        assert isinstance(headers["allow_methods"], list)
        assert isinstance(headers["allow_headers"], list)
        assert isinstance(headers["expose_headers"], list)
        assert isinstance(headers["max_age"], int)
        assert isinstance(headers["allow_credentials"], bool)

    def test_cors_headers_generation(self):
        """create_cors_headers gera headers corretamente."""
        from cors_config import create_cors_headers

        config = CORSConfig(environment="development")
        headers = create_cors_headers("http://localhost:3000", config)

        # Em dev, todo origin é permitido
        assert "Access-Control-Allow-Origin" in headers
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers

    def test_cors_headers_origin_whitelist(self):
        """CORS respeita whitelist de origins em production."""
        from cors_config import create_cors_headers

        config = CORSConfig(environment="production")

        # Origin permitido
        allowed_headers = create_cors_headers("https://hub.mantaassociados.com", config)
        assert len(allowed_headers) > 0

        # Origin não permitido
        denied_headers = create_cors_headers("https://evil.com", config)
        assert len(denied_headers) == 0


class TestRateLimiter:
    """Testes do rate limiter."""

    def test_rate_limiter_basic(self):
        """Rate limiter bloqueia requisições excessivas."""
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)

        # Primeira e segunda requisições
        assert limiter.is_allowed("user1") is True
        assert limiter.is_allowed("user1") is True

        # Terceira é bloqueada
        with pytest.raises(RateLimitExceeded):
            limiter.is_allowed("user1")

    def test_rate_limiter_by_key(self):
        """Rate limiter rastreia por chave separadamente."""
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)

        # User1: 2 requisições
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")

        # User2: pode fazer 2 também (chaves separadas)
        assert limiter.is_allowed("user2") is True
        assert limiter.is_allowed("user2") is True

        # Mas a terceira para user2 é bloqueada
        with pytest.raises(RateLimitExceeded):
            limiter.is_allowed("user2")

    def test_rate_limiter_cleanup(self):
        """Cleanup remove buckets vazios."""
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=1)

        limiter.is_allowed("user1")
        limiter.is_allowed("user2")

        assert "user1" in limiter.buckets
        assert "user2" in limiter.buckets

        # Simulate time passing (cheating by directly accessing)
        # In real scenario, would wait 1+ seconds
        limiter.buckets["user1"] = []
        limiter.cleanup()

        assert "user1" not in limiter.buckets
        assert "user2" in limiter.buckets
