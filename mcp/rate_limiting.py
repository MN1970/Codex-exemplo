"""
Rate limiting por user/IP para MantaBase MCP v2.

Suporta: in-memory (dev), Redis (prod).
"""

import hashlib
import os
import time
from typing import Optional

from logging_config import get_logger


class RateLimitExceeded(Exception):
    """Exceção quando rate limit é excedido."""

    pass


class RateLimiter:
    """Rate limiter base (interface)."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: máximo de requisições por janela.
            window_seconds: duração da janela em segundos.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, key: str) -> bool:
        """
        Verifica se requisição é permitida.

        Args:
            key: identificador único (ex: user_email, IP).

        Returns:
            True se permitido, False se excedido.

        Raises:
            RateLimitExceeded se o limite foi excedido.
        """
        raise NotImplementedError


class InMemoryRateLimiter(RateLimiter):
    """Rate limiter em memória (para desenvolvimento)."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(max_requests, window_seconds)
        self.buckets: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Verifica se requisição é permitida usando token bucket."""
        now = time.time()
        window_start = now - self.window_seconds

        # Inicializar bucket se não existir
        if key not in self.buckets:
            self.buckets[key] = []

        # Remover timestamps fora da janela
        self.buckets[key] = [ts for ts in self.buckets[key] if ts > window_start]

        # Verificar limite
        if len(self.buckets[key]) >= self.max_requests:
            get_logger().warning(
                "Rate limit exceeded",
                key=key,
                requests=len(self.buckets[key]),
                limit=self.max_requests,
            )
            raise RateLimitExceeded(
                f"Rate limit exceeded: {len(self.buckets[key])}/{self.max_requests}"
            )

        # Adicionar nova requisição
        self.buckets[key].append(now)
        return True

    def cleanup(self):
        """Remove buckets vazios (para economizar memória)."""
        now = time.time()
        window_start = now - self.window_seconds

        expired_keys = [
            k for k, v in self.buckets.items()
            if not any(ts > window_start for ts in v)
        ]
        for k in expired_keys:
            del self.buckets[k]


class RedisRateLimiter(RateLimiter):
    """Rate limiter com Redis (para produção)."""

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        redis_url: Optional[str] = None,
    ):
        super().__init__(max_requests, window_seconds)

        try:
            import redis
        except ImportError:
            raise ImportError("redis-py is required for RedisRateLimiter")

        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        self.prefix = "rate_limit:"

    def is_allowed(self, key: str) -> bool:
        """Verifica se requisição é permitida usando Redis."""
        redis_key = f"{self.prefix}{key}"

        try:
            current = self.client.incr(redis_key)

            # Set expiration na primeira requisição da janela
            if current == 1:
                self.client.expire(redis_key, self.window_seconds)

            if current > self.max_requests:
                get_logger().warning(
                    "Rate limit exceeded (Redis)",
                    key=key,
                    requests=current,
                    limit=self.max_requests,
                )
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {current}/{self.max_requests}"
                )

            return True
        except Exception as e:
            # Se Redis falhar, permitir requisição (fail-open)
            get_logger().error("Rate limiter error (failing open)", error=str(e))
            return True


class RateLimitMiddleware:
    """Middleware de rate limiting para tools."""

    def __init__(self, limiter: Optional[RateLimiter] = None):
        """
        Args:
            limiter: instância de RateLimiter. Padrão: InMemoryRateLimiter.
        """
        if limiter is None:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                try:
                    limiter = RedisRateLimiter(redis_url=redis_url)
                except ImportError:
                    limiter = InMemoryRateLimiter()
            else:
                limiter = InMemoryRateLimiter()

        self.limiter = limiter

    def check_rate_limit(self, user_email: str) -> bool:
        """
        Verifica se o usuário está dentro do rate limit.

        Args:
            user_email: email do usuário.

        Returns:
            True se permitido.

        Raises:
            RateLimitExceeded se excedido.
        """
        # Hash do email para key redis (privacidade)
        key_hash = hashlib.sha256(user_email.encode()).hexdigest()[:16]
        return self.limiter.is_allowed(key_hash)


# Singleton global
_rate_limiter: Optional[RateLimitMiddleware] = None


def get_rate_limiter() -> RateLimitMiddleware:
    """Retorna a instância global de rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimitMiddleware()
    return _rate_limiter
