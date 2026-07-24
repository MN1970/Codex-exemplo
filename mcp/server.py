"""
MantaBase MCP v2 — FastMCP server com 3 meta-tools.

Tools:
1. execute — roda Python assinado contra Supabase (schema validado)
2. query — somente leitura Supabase + SharePoint (sem mutations)
3. skills — lista templates pré-aprovados
"""

import os
from typing import Any

from fastmcp import FastMCP
from pydantic import BaseModel

from auth import get_token_manager
from sandbox import execute_python


# --- Server setup ---

mcp = FastMCP("mantabase-mcp-v2")
token_manager = get_token_manager()


class ExecuteRequest(BaseModel):
    """Requisição de execução de código Python."""

    code: str
    context: dict[str, Any] = {}  # variáveis injetadas (ex: {"df": pandas.DataFrame})


class QueryRequest(BaseModel):
    """Requisição de query (read-only)."""

    sql: str
    params: dict[str, Any] = {}


class SkillsListRequest(BaseModel):
    """Requisição de listagem de skills."""

    category: str = "all"  # "all", "data-processing", "schema-audit", etc


# --- Tool 1: execute ---


@mcp.tool()
def execute(request: ExecuteRequest) -> dict[str, Any]:
    """
    Executa código Python assinado em sandbox isolado.

    Bloqueia: I/O de rede, filesystem, subprocess.
    Acessa: Supabase (via contexto), pandas, numpy, etc.

    Args:
        code: código Python (máx 10KB).
        context: variáveis injetadas no escopo (ex: {"client": supabase_client}).

    Returns:
        {
            "result": qualquer coisa,
            "output": stdout capturado,
            "error": None ou mensagem,
            "execution_time": float
        }
    """
    if len(request.code) > 10 * 1024:
        return {"error": "Code too large (max 10KB)", "result": None}

    result = execute_python(request.code, locals_dict=request.context)
    return result


# --- Tool 2: query ---


@mcp.tool()
def query(request: QueryRequest) -> dict[str, Any]:
    """
    Query somente-leitura contra Supabase e SharePoint.

    Suporta: SELECT, agregações, JOINs.
    Bloqueia: INSERT, UPDATE, DELETE, DROP.

    Args:
        sql: SQL a executar.
        params: parâmetros nomeados (ex: {"id": 123}).

    Returns:
        {
            "rows": lista de dicts,
            "count": int,
            "error": None ou mensagem
        }
    """
    # TODO: implementar validação SQL + execução via Supabase client.
    # Por enquanto, stubbed.

    if any(
        keyword in request.sql.upper()
        for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE"]
    ):
        return {"error": "Mutation queries are not allowed (read-only)", "rows": []}

    return {"rows": [], "count": 0, "error": "Not implemented yet"}


# --- Tool 3: skills ---


@mcp.tool()
def skills(request: SkillsListRequest) -> dict[str, Any]:
    """
    Lista templates de skills pré-aprovados.

    Cada skill é um snippet Python testado que pode ser usado em `execute()`.

    Args:
        category: filtro por categoria (padrão: "all").

    Returns:
        {
            "skills": [
                {
                    "id": "skill-001",
                    "name": "Bulk insert into table",
                    "category": "data-processing",
                    "code": "...",
                    "description": "..."
                }
            ]
        }
    """
    # TODO: carregar do database ou arquivo skills.json.
    mock_skills = [
        {
            "id": "skill-001",
            "name": "Bulk insert rows",
            "category": "data-processing",
            "code": "# Insert rows into Supabase table\n# Usage: exec(skill_code, {'table': 'my_table', 'rows': [...]}}",
            "description": "Template para inserção em lote com validação de schema.",
        },
    ]

    if request.category != "all":
        mock_skills = [s for s in mock_skills if s["category"] == request.category]

    return {"skills": mock_skills}


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
