"""
Maestro OS v6.0 — Cliente Supabase real (aprendizado/telemetria)

Primeira implementação real de persistência para o Maestro OS. Até esta
mudança, `mcp_tools.py::SupabaseStateManager` era um stub — nenhum código
em `src/maestro/` gravava em nenhuma tabela Supabase (confirmado por
auditoria de código em 2026-08-13).

Este módulo é deliberadamente best-effort e silencioso por padrão:
- Sem `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` configurados, todas as
  funções de gravação são no-op (retornam sem erro) — o orquestrador
  continua funcionando normalmente em dev/teste sem Supabase.
- Falhas de rede/API na gravação são logadas, nunca propagadas — captura
  de telemetria não deve derrubar um workflow real do usuário.

Usa SERVICE_ROLE_KEY (nunca ANON_KEY): este é código server-side, nunca
exposto a cliente/navegador — mesma convenção já adotada no restante do
repositório (ver `infra/agent-registry/.env.example`).
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger("maestro.supabase_client")

_client_cache: Optional[Any] = None
_client_checked: bool = False


def get_supabase_client() -> Optional[Any]:
    """
    Retorna um cliente Supabase configurado com a service role key, ou
    None se as variáveis de ambiente não estiverem presentes ou a lib
    `supabase` não estiver instalada. Nunca lança exceção.
    """
    global _client_cache, _client_checked

    if _client_checked:
        return _client_cache

    _client_checked = True

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        logger.info(
            "SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY não configurados — "
            "telemetria de agent_episodes desabilitada (no-op)."
        )
        return None

    try:
        from supabase import create_client
    except ImportError:
        logger.warning(
            "Pacote 'supabase' não instalado — telemetria de agent_episodes "
            "desabilitada (no-op). Ver requirements.txt (supabase>=2.0.0)."
        )
        return None

    try:
        _client_cache = create_client(url, key)
    except Exception as exc:  # noqa: BLE001 — best-effort, nunca propagar
        logger.warning("Falha ao criar cliente Supabase: %s", exc)
        _client_cache = None

    return _client_cache


def reset_client_cache_for_tests() -> None:
    """Usado apenas por testes — força reavaliação das env vars."""
    global _client_cache, _client_checked
    _client_cache = None
    _client_checked = False


def insert_rows(table: str, rows: list) -> bool:
    """
    Insere `rows` em `table` via o cliente Supabase, best-effort.

    Retorna True se a gravação foi tentada e não lançou erro, False se
    não há cliente configurado ou se a gravação falhou. Nunca lança.
    """
    if not rows:
        return True

    client = get_supabase_client()
    if client is None:
        return False

    try:
        client.table(table).insert(rows).execute()
        return True
    except Exception as exc:  # noqa: BLE001 — best-effort, nunca propagar
        logger.warning("Falha ao gravar em '%s' (%d linha(s)): %s", table, len(rows), exc)
        return False
