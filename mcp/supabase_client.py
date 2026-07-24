"""
Cliente Supabase para MantaBase MCP v2.

Suporta: SELECT, JOINs, agregações.
Bloqueia: INSERT, UPDATE, DELETE, DROP, TRUNCATE.
"""

import os
import re
from typing import Any, Optional

try:
    from supabase import create_client
except ImportError:
    create_client = None  # Optional dependency


class SupabaseQueryValidator:
    """Valida queries SQL antes de executar."""

    # Palavras-chave bloqueadas (mutations, DDL)
    BLOCKED_KEYWORDS = {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "REPLACE",
        "UPSERT",
    }

    # Funções bloqueadas (I/O, system)
    BLOCKED_FUNCTIONS = {
        "COPY",
        "EXECUTE",
        "EVAL",
        "SYSTEM",
        "SHELL",
        "PYTHON",
        "R",
    }

    @staticmethod
    def is_safe(sql: str) -> tuple[bool, Optional[str]]:
        """
        Valida se a query é segura (read-only).

        Args:
            sql: SQL a validar.

        Returns:
            (is_safe: bool, error_message: Optional[str])
        """
        sql_upper = sql.strip().upper()

        # Check blocked keywords
        for keyword in SupabaseQueryValidator.BLOCKED_KEYWORDS:
            if re.search(rf"\b{keyword}\b", sql_upper):
                return False, f"Keyword '{keyword}' not allowed (read-only only)"

        # Check blocked functions
        for func in SupabaseQueryValidator.BLOCKED_FUNCTIONS:
            if re.search(rf"\b{func}\s*\(", sql_upper):
                return False, f"Function '{func}' not allowed"

        # Check for SQL injection patterns
        if "--" in sql or "/*" in sql:
            return False, "Comments not allowed (potential injection)"

        # Query must start with SELECT
        if not sql_upper.startswith("SELECT"):
            return False, "Only SELECT queries allowed"

        return True, None


class SupabaseQueryClient:
    """Cliente para executar queries read-only no Supabase."""

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
    ):
        """
        Inicializa cliente Supabase.

        Args:
            url: URL do Supabase (padrão: env SUPABASE_URL).
            key: API key do Supabase (padrão: env SUPABASE_KEY).
        """
        if create_client is None:
            raise ImportError("supabase package is required but not installed")

        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client = create_client(self.url, self.key)

    def execute_query(
        self,
        sql: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Executa uma query read-only no Supabase via RPC.

        Args:
            sql: SQL a executar (SELECT only).
            params: parâmetros nomeados (ex: {"id": 123}).

        Returns:
            {
                "rows": lista de dicts,
                "count": int,
                "error": None ou mensagem
            }
        """
        # Validar query localmente primeiro
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        if not is_safe:
            return {"rows": [], "count": 0, "error": error}

        try:
            # Chamar RPC function no Supabase
            # RPC: execute_select_query(p_sql TEXT, p_params JSONB)
            result = self.client.rpc(
                "execute_select_query",
                {
                    "p_sql": sql,
                    "p_params": params,
                },
            ).execute()

            # Result estrutura: {"rows": [...], "count": N, "error": null}
            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                return {
                    "rows": [],
                    "count": 0,
                    "error": "No data returned from RPC",
                }

        except Exception as e:
            return {
                "rows": [],
                "count": 0,
                "error": f"RPC execution error: {str(e)}",
            }

    def test_connection(self) -> bool:
        """Testa conexão com Supabase."""
        try:
            # Try a simple auth test
            self.client.auth.get_session()
            return True
        except Exception:
            return False


def get_supabase_client() -> SupabaseQueryClient:
    """Factory para criar cliente Supabase."""
    return SupabaseQueryClient()
