"""
MantaBase MCP v2 — FastMCP server com 3 meta-tools.

Tools:
1. execute — roda Python assinado contra Supabase (schema validado)
2. query — somente leitura Supabase + SharePoint (sem mutations)
3. skills — lista templates pré-aprovados
"""

import os
from typing import Any, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from auth import get_token_manager, TokenPayload
from cors_config import CORSConfig, create_cors_headers
from logging_config import get_logger
from middleware import check_permission, RequestWithAuth
from permissions import PermissionChecker, Scope
from rate_limiting import get_rate_limiter, RateLimitExceeded
from sandbox import execute_python
from supabase_client import SupabaseQueryClient
import hashlib
import time


# --- Server setup ---

mcp = FastMCP("mantabase-mcp-v2")
token_manager = get_token_manager()
rate_limiter = get_rate_limiter()
cors_config = CORSConfig()


class ExecuteRequest(BaseModel):
    """Requisição de execução de código Python."""

    code: str
    context: dict[str, Any] = {}  # variáveis injetadas (ex: {"df": pandas.DataFrame})
    token: Optional[str] = None  # JWT token para autenticação


class QueryRequest(BaseModel):
    """Requisição de query (read-only)."""

    sql: str
    params: dict[str, Any] = {}
    token: Optional[str] = None  # JWT token para autenticação


class SkillsListRequest(BaseModel):
    """Requisição de listagem de skills."""

    category: str = "all"  # "all", "data-processing", "schema-audit", etc


# --- Tool 1: execute ---


@mcp.tool()
def execute(request: ExecuteRequest) -> dict[str, Any]:
    """
    Executa código Python assinado em sandbox isolado.

    Requer: Scope EXECUTE_SANDBOXED (USER+) ou EXECUTE_PYTHON (ADMIN).
    Bloqueia: I/O de rede, filesystem, subprocess.
    Acessa: Supabase (via contexto), pandas, numpy, etc.

    Args:
        code: código Python (máx 10KB).
        context: variáveis injetadas no escopo (ex: {"client": supabase_client}).
        token: JWT token para autenticação.

    Returns:
        {
            "result": qualquer coisa,
            "output": stdout capturado,
            "error": None ou mensagem,
            "execution_time": float
        }
    """
    # Helper para respostas com CORS
    def respond_execute_error(error: str, payload=None) -> dict[str, Any]:
        resp = {"error": error, "result": None, "_cors_headers": create_cors_headers("*", cors_config)}
        if payload:
            resp["user"] = payload.sub
        return resp

    # Validar token e extrair permissões
    if not request.token:
        return respond_execute_error("Authorization required (no token provided)")

    payload = token_manager.validate_token(request.token)
    if not payload:
        return respond_execute_error("Invalid or expired token")

    # Verificar rate limit
    try:
        rate_limiter.check_rate_limit(payload.sub)
    except RateLimitExceeded as e:
        get_logger().warning(
            "Rate limit exceeded for execute",
            user_email=payload.sub,
            error=str(e),
        )
        return respond_execute_error(f"Rate limit exceeded: {str(e)}", payload)

    # Verificar permissão (ADMIN pode usar execute.python, USER usa execute.sandboxed)
    required_scopes = [Scope.EXECUTE_SANDBOXED, Scope.EXECUTE_PYTHON]
    error_msg = check_permission(payload, required_scopes)
    if error_msg:
        return respond_execute_error(error_msg, payload)

    # Validar tamanho do código
    if len(request.code) > 10 * 1024:
        return respond_execute_error("Code too large (max 10KB)", payload)

    # Executar em sandbox
    start_time = time.time()
    result = execute_python(request.code, locals_dict=request.context)
    duration_ms = int((time.time() - start_time) * 1000)

    # Adicionar metadata de auditoria
    result["user"] = payload.sub
    result["role"] = PermissionChecker.get_role_from_scopes(payload.scope).value if PermissionChecker.get_role_from_scopes(payload.scope) else "unknown"

    # Adicionar CORS headers para HTTP wrapper (origin = any)
    result["_cors_headers"] = create_cors_headers("*", cors_config)

    # Logar execução
    code_hash = hashlib.md5(request.code.encode()).hexdigest()[:8]
    error_msg = result.get("error")
    get_logger().log_execute(
        user_email=payload.sub,
        code_hash=code_hash,
        duration_ms=duration_ms,
        error=error_msg,
    )

    return result


# --- Tool 2: query ---


@mcp.tool()
def query(request: QueryRequest) -> dict[str, Any]:
    """
    Query somente-leitura contra Supabase e SharePoint.

    Suporta: SELECT, agregações, JOINs.
    Bloqueia: INSERT, UPDATE, DELETE, DROP.
    Requer: Scope QUERY_SUPABASE (USER+) ou QUERY_SHAREPOINT (ADMIN).

    Args:
        sql: SQL a executar.
        params: parâmetros nomeados (ex: {"id": 123}).
        token: JWT token para autenticação.

    Returns:
        {
            "rows": lista de dicts,
            "count": int,
            "error": None ou mensagem
        }
    """
    # Helper para respostas com CORS
    def respond_query_error(error: str, payload=None) -> dict[str, Any]:
        resp = {"rows": [], "count": 0, "error": error, "_cors_headers": create_cors_headers("*", cors_config)}
        if payload:
            resp["user"] = payload.sub
        return resp

    # Validar token
    if not request.token:
        return respond_query_error("Authorization required (no token provided)")

    payload = token_manager.validate_token(request.token)
    if not payload:
        return respond_query_error("Invalid or expired token")

    # Verificar rate limit
    try:
        rate_limiter.check_rate_limit(payload.sub)
    except RateLimitExceeded as e:
        get_logger().warning(
            "Rate limit exceeded for query",
            user_email=payload.sub,
            error=str(e),
        )
        return respond_query_error(f"Rate limit exceeded: {str(e)}", payload)

    # Verificar permissão
    required_scopes = [Scope.QUERY_SUPABASE]
    error_msg = check_permission(payload, required_scopes)
    if error_msg:
        return respond_query_error(error_msg, payload)

    try:
        start_time = time.time()
        client = SupabaseQueryClient()
        result = client.execute_query(request.sql, request.params)
        duration_ms = int((time.time() - start_time) * 1000)

        result["user"] = payload.sub
        result["_cors_headers"] = create_cors_headers("*", cors_config)

        # Logar query
        query_hash = hashlib.md5(request.sql.encode()).hexdigest()[:8]
        row_count = result.get("count", 0)
        error_msg = result.get("error")
        get_logger().log_query(
            user_email=payload.sub,
            query_hash=query_hash,
            duration_ms=duration_ms,
            row_count=row_count,
            error=error_msg,
        )

        return result
    except ValueError as e:
        error_str = f"Configuration error: {str(e)}"
        get_logger().error("Query config error", user_email=payload.sub, error=error_str)
        return respond_query_error(error_str, payload)
    except Exception as e:
        error_str = f"Query error: {str(e)}"
        get_logger().error("Query execution error", user_email=payload.sub, error=error_str)
        return respond_query_error(error_str, payload)


# --- Tool 3: skills ---


@mcp.tool()
def skills(request: SkillsListRequest) -> dict[str, Any]:
    """
    Lista templates de skills pré-aprovados.

    Cada skill é um snippet Python testado que pode ser usado em `execute()`.
    Carrega da biblioteca skills.json.

    Args:
        category: filtro por categoria (padrão: "all").

    Returns:
        {
            "skills": [
                {
                    "id": "skill-001",
                    "name": "Bulk insert rows",
                    "category": "data-processing",
                    "code": "...",
                    "description": "..."
                }
            ]
        }
    """
    import json
    import os

    # Carregar skills.json
    skills_path = os.path.join(os.path.dirname(__file__), "skills.json")
    try:
        with open(skills_path, "r") as f:
            data = json.load(f)
        all_skills = data.get("skills", [])
    except FileNotFoundError:
        return {"skills": [], "error": "Skills library not found"}
    except json.JSONDecodeError:
        return {"skills": [], "error": "Skills library malformed"}

    # Filtrar por categoria
    if request.category != "all":
        filtered_skills = [s for s in all_skills if s.get("category") == request.category]
    else:
        filtered_skills = all_skills

    return {"skills": filtered_skills, "count": len(filtered_skills)}


# --- Startup hook: token renewal ---


@mcp.after_server_init
async def on_startup():
    """Hook executado após init do servidor."""
    print("[MantaBase MCP v2] Server started")
    print(f"[Auth] Secret key loaded: {bool(os.getenv('MANTABASE_SECRET_KEY'))}")


# --- Main ---

if __name__ == "__main__":
    import asyncio

    # Para testes locais: emite um token e printa.
    token = token_manager.issue_token(
        user_email="test@mantaassociados.com",
        scopes=["execute.python", "query.supabase", "sharepoint.write"],
    )
    print(f"[Auth] Sample token: {token[:50]}...")

    # Inicia servidor.
    asyncio.run(mcp.run())
