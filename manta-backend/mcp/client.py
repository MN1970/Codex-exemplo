"""
mcp/client.py — Cliente async para o gateway MCP (Model Context
Protocol) usado pelos agentes Manta (SharePoint, Supabase, GitHub,
etc.). Implementado sobre aiohttp com uma única ClientSession
reaproveitada (criada no lifespan da app — ver app.py).
"""
import logging
from functools import lru_cache
from typing import Any, Dict, Optional

import aiohttp

from config import get_settings

logger = logging.getLogger("manta.mcp")


class MCPClient:
    """Wrapper fino sobre aiohttp para chamar tools de um servidor MCP
    exposto via HTTP (gateway). `session` é injetada e gerenciada pelo
    lifespan da aplicação para evitar recriar conexões TCP por request.
    """

    def __init__(self, base_url: str, timeout_seconds: int, session: Optional[aiohttp.ClientSession] = None):
        self.base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._session = session
        self._owns_session = session is None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
            self._owns_session = True
        return self._session

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Chama uma tool MCP via o gateway HTTP.
        Espera um contrato `POST {base_url}/tools/{tool_name}` -> JSON.
        """
        session = await self._ensure_session()
        url = f"{self.base_url}/tools/{tool_name}"
        try:
            async with session.post(url, json={"arguments": arguments}) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as exc:
            logger.error("mcp.call_tool(%s) falhou: %s", tool_name, exc)
            raise

    async def list_tools(self) -> Dict[str, Any]:
        session = await self._ensure_session()
        url = f"{self.base_url}/tools"
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def close(self) -> None:
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()


@lru_cache
def get_mcp_client() -> MCPClient:
    """Singleton leve para uso fora do lifespan (ex.: scripts, testes).
    Dentro da app, prefira `request.app.state.mcp_client`."""
    settings = get_settings()
    return MCPClient(
        base_url=settings.mcp_gateway_url,
        timeout_seconds=settings.mcp_request_timeout_seconds,
    )
