"""
config.py — Configuração central do Manta Backend.

Usa pydantic-settings para carregar variáveis de ambiente (.env em dev,
env vars reais em produção/Docker). Nenhum segredo tem default de
produção: tudo cai para valores de desenvolvimento local óbvios, para
que rodar `uvicorn app:app` funcione fora da caixa em localhost:8000.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Manta Maestro Backend"
    app_version: str = "0.1.0"
    environment: str = Field(default="development")  # development|staging|production
    debug: bool = True

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- CORS ---
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
        ]
    )

    # --- Database (Postgres / Supabase) ---
    database_url: str = Field(
        default="postgresql://manta:manta@db:5432/manta",
        description="DSN async (usado via asyncpg).",
    )
    db_pool_min_size: int = 1
    db_pool_max_size: int = 10

    # --- Supabase (RAG pgvector) ---
    supabase_url: str = ""
    supabase_service_key: str = ""

    # --- Auth / JWT ---
    # RS256 (assinatura assimétrica) é o padrão: o serviço que emite tokens
    # guarda a chave privada; qualquer serviço com a chave pública pode
    # validar sem poder forjar tokens. Em produção, defina JWT_PRIVATE_KEY
    # e JWT_PUBLIC_KEY (PEM) via secret manager — nunca commitar as chaves.
    # Se ficarem vazias, auth.py gera um par RSA efêmero em memória (útil
    # para dev/testes, mas não sobrevive a restart nem escala horizontalmente).
    jwt_algorithm: str = "RS256"
    jwt_private_key: str = ""  # PEM (PKCS8), multi-linha
    jwt_public_key: str = ""  # PEM (SubjectPublicKeyInfo)
    jwt_issuer: str = "manta-maestro-auth"
    jwt_secret: str = "change-me-in-production"  # usado apenas se jwt_algorithm cair para HS256
    jwt_expires_minutes: int = 60 * 8  # 8h — legado (admin.py /admin/token)
    access_token_expires_minutes: int = 15
    refresh_token_expires_days: int = 30
    org_header_name: str = "X-Org-Id"

    # --- MCP ---
    mcp_gateway_url: str = "http://localhost:8765"
    mcp_request_timeout_seconds: int = 30

    # --- MCP remoto (mcp/integration.py) — servers consumidos como MCP client ---
    # Vazio = integração desabilitada (server sobe sem essa tool remota).
    github_mcp_url: str = ""
    github_mcp_token: str = ""
    supabase_mcp_url: str = ""
    supabase_mcp_token: str = ""
    microsoft_365_mcp_url: str = ""
    microsoft_365_mcp_token: str = ""

    # --- Claude API (agent executor) ---
    claude_api_key: str = ""
    claude_default_model: str = "claude-3-5-sonnet-20241022"
    claude_opus_model: str = "claude-3-opus-20250219"
    claude_max_tokens: int = 4096
    claude_streaming_timeout: int = 120

    # --- ML ---
    # all-MiniLM-L6-v2 (Sentence Transformers, local, sem API externa) —
    # ver ml/embeddings.py::EMBEDDING_MODEL_NAME/EMBEDDING_DIMENSIONS.
    # dimensions=384 precisa bater com a coluna `vector(N)` das
    # migrations Alembic (0002 + 0004_embedding_dim_384) e com
    # scripts/init.sql — trocar de modelo exige atualizar todos esses
    # pontos + uma migration nova.
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimensions: int = 384


@lru_cache
def get_settings() -> Settings:
    """Settings são carregadas uma única vez e cacheadas (singleton)."""
    return Settings()
