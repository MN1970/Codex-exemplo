"""
mcp/integration.py — Camada de integração MCP (Model Context Protocol)
completa do Manta Backend.

Este módulo faz o Manta Backend atuar nos dois papéis do protocolo MCP
ao mesmo tempo:

  1. MCP SERVER — expõe as capacidades do próprio Manta Backend
     (registro de agentes, motor de roteamento do Maestro, fases do
     ciclo de vida) como *tools* MCP, para que qualquer cliente MCP
     (Claude Desktop, outro agente Manta, um IDE) descubra e chame essas
     tools via `POST /mcp` (JSON-RPC 2.0 — `initialize`, `tools/list`,
     `tools/call`) ou via os atalhos REST `GET /mcp/tools` e
     `POST /mcp/invoke/{tool_name}`.

  2. MCP CLIENT — consome MCP servers remotos já usados pelo ecossistema
     Manta (GitHub, Supabase, Microsoft 365 / SharePoint), registra as
     tools deles sob namespace (`github.*`, `supabase.*`, `ms365.*`) e
     as expõe pelo MESMO tool registry — um agente Claude conversando
     com o Manta Backend enxerga tools locais e remotas de forma
     unificada.

Toda invocação (local ou remota) recebe um `MCPContext` injetado
automaticamente — quem chamou (JWT), qual agente Manta está atuando,
trace id e timestamp — propagado como metadado JSON-RPC (`_meta`) e
como headers HTTP, para auditoria/rastreabilidade (ver CLAUDE.md master
→ "Gate humano" / "DEPLOY CHECKLIST").

Relação com `mcp/client.py`: aquele módulo é um cliente fino para UM
gateway HTTP custom (`POST {base_url}/tools/{tool}`), usado desde o
início do skeleton. Este módulo (`mcp/integration.py`) é a evolução:
fala o protocolo MCP real (JSON-RPC 2.0) com N servers remotos e
adiciona o papel de *servidor* MCP. Os dois coexistem sem conflito
(namespaces de módulo distintos); `app.py` decide o que usar.

Uso rápido:
    - Endpoints reais: ver `router` incluído em `app.py`.
    - Exemplo de invoke funcionando de ponta a ponta, sem precisar de
      credenciais nem rede: `python -m mcp.integration`.
    - Integração com um agente Claude: `run_claude_agent(...)`.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from itertools import count
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

logger = logging.getLogger("manta.mcp.integration")

MCP_PROTOCOL_VERSION = "2025-06-18"


# ---------------------------------------------------------------------------
# MCP context — injetado em toda invocação, local ou remota
# ---------------------------------------------------------------------------

@dataclass
class MCPContext:
    """Metadado propagado com toda chamada de tool (local ou remota).

    Serve tanto para auditoria (quem/quando/qual agente Manta) quanto
    para os MCP servers remotos poderem aplicar suas próprias regras de
    autorização por ator.
    """

    trace_id: str
    actor: str
    actor_role: str = "user"
    agent_code: Optional[str] = None
    requested_at: float = field(default_factory=time.time)

    @classmethod
    def new(cls, actor: str = "anonymous", actor_role: str = "user",
            agent_code: Optional[str] = None) -> "MCPContext":
        return cls(trace_id=str(uuid4()), actor=actor, actor_role=actor_role, agent_code=agent_code)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "traceId": self.trace_id,
            "actor": self.actor,
            "actorRole": self.actor_role,
            "agentCode": self.agent_code,
            "requestedAt": self.requested_at,
        }

    def to_headers(self) -> Dict[str, str]:
        """Formato alternativo de propagação, para MCP servers remotos
        que preferem ler contexto de headers HTTP a de `_meta` JSON-RPC."""
        headers = {
            "X-MCP-Trace-Id": self.trace_id,
            "X-MCP-Actor": self.actor,
            "X-MCP-Actor-Role": self.actor_role,
        }
        if self.agent_code:
            headers["X-MCP-Agent-Code"] = self.agent_code
        return headers


# ---------------------------------------------------------------------------
# Tool registry — descrição unificada de tools locais e remotas
# ---------------------------------------------------------------------------

class MCPTool(BaseModel):
    """Descrição de uma tool MCP, no formato usado tanto pelo `tools/list`
    JSON-RPC quanto pelo parâmetro `tools=` da Claude Messages API
    (`input_schema` é JSON Schema em ambos os casos)."""

    name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})
    server: str = "local"            # "local" | "github" | "supabase" | "ms365" | ...
    read_only: bool = True


LocalToolHandler = Callable[[Dict[str, Any], MCPContext], Awaitable[Dict[str, Any]]]


class ToolNotFoundError(LookupError):
    def __init__(self, tool_name: str):
        super().__init__(f"Tool '{tool_name}' não registrada.")
        self.tool_name = tool_name


class MCPUpstreamError(RuntimeError):
    """Erro ao chamar um MCP server remoto (rede, JSON-RPC error, etc.)."""

    def __init__(self, server: str, tool_name: str, detail: str):
        super().__init__(f"MCP remoto '{server}' falhou em '{tool_name}': {detail}")
        self.server = server
        self.tool_name = tool_name
        self.detail = detail


class ToolRegistry:
    """Registro das tools LOCAIS do Manta Backend (as que este processo
    sabe executar diretamente, sem sair pela rede)."""

    def __init__(self) -> None:
        self._entries: Dict[str, tuple[MCPTool, LocalToolHandler]] = {}

    def register(self, tool: MCPTool, handler: LocalToolHandler) -> None:
        self._entries[tool.name] = (tool, handler)
        logger.debug("mcp.registry: tool local registrada: %s", tool.name)

    def get(self, name: str) -> Optional[tuple[MCPTool, LocalToolHandler]]:
        return self._entries.get(name)

    def list_tools(self) -> List[MCPTool]:
        return [tool for tool, _ in self._entries.values()]


# ---------------------------------------------------------------------------
# MCPClient — cliente para UM MCP server remoto (JSON-RPC 2.0 real)
# ---------------------------------------------------------------------------

@dataclass
class RemoteMCPServerConfig:
    """Config de um MCP server remoto consumido pelo Manta Backend."""

    name: str                      # namespace: "github" | "supabase" | "ms365"
    base_url: str
    api_key_env: Optional[str] = None   # nome da env var com o bearer token
    enabled: bool = True


class MCPClient:
    """Cliente MCP para UM servidor remoto, falando o protocolo real
    (JSON-RPC 2.0 sobre HTTP — transporte "Streamable HTTP" do MCP):
    `initialize`, `tools/list`, `tools/call`.

    Reaproveita a `aiohttp.ClientSession` compartilhada da app (injetada
    pelo lifespan em `app.py`) em vez de abrir uma conexão por request.
    """

    def __init__(self, config: RemoteMCPServerConfig, session: aiohttp.ClientSession):
        self.config = config
        self._session = session
        self._id_counter = count(1)
        self._initialized = False

    def _headers(self, context: Optional[MCPContext] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_key_env:
            token = os.environ.get(self.config.api_key_env)
            if token:
                headers["Authorization"] = f"Bearer {token}"
        if context is not None:
            headers.update(context.to_headers())
        return headers

    async def _rpc(self, method: str, params: Dict[str, Any],
                    context: Optional[MCPContext] = None) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": next(self._id_counter),
            "method": method,
            "params": params,
        }
        try:
            async with self._session.post(
                self.config.base_url, json=payload, headers=self._headers(context)
            ) as resp:
                resp.raise_for_status()
                body = await resp.json()
        except aiohttp.ClientError as exc:
            raise MCPUpstreamError(self.config.name, method, str(exc)) from exc

        if "error" in body:
            err = body["error"]
            raise MCPUpstreamError(self.config.name, method, f"{err.get('code')}: {err.get('message')}")
        return body.get("result", {})

    async def initialize(self) -> Dict[str, Any]:
        result = await self._rpc("initialize", {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "manta-backend", "version": "0.1.0"},
        })
        self._initialized = True
        return result

    async def list_tools(self) -> List[MCPTool]:
        if not self._initialized:
            await self.initialize()
        result = await self._rpc("tools/list", {})
        tools = []
        for raw in result.get("tools", []):
            tools.append(MCPTool(
                name=raw["name"],
                description=raw.get("description", ""),
                input_schema=raw.get("inputSchema", {"type": "object", "properties": {}}),
                server=self.config.name,
            ))
        return tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any],
                         context: MCPContext) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        result = await self._rpc("tools/call", {
            "name": tool_name,
            "arguments": arguments,
            "_meta": {"mcpContext": context.to_dict()},
        }, context=context)
        if result.get("isError"):
            detail = json.dumps(result.get("content", []), ensure_ascii=False)
            raise MCPUpstreamError(self.config.name, tool_name, detail)
        return result


def default_remote_configs() -> List[RemoteMCPServerConfig]:
    """Lê a config dos 3 MCP servers remotos do CLAUDE.md/env. Um server
    sem `base_url` configurada fica `enabled=False` e é ignorado — assim
    o backend sobe mesmo sem as 3 integrações prontas."""
    def _cfg(name: str, url_env: str, key_env: str) -> RemoteMCPServerConfig:
        base_url = os.environ.get(url_env, "")
        return RemoteMCPServerConfig(name=name, base_url=base_url, api_key_env=key_env, enabled=bool(base_url))

    return [
        _cfg("github", "GITHUB_MCP_URL", "GITHUB_MCP_TOKEN"),
        _cfg("supabase", "SUPABASE_MCP_URL", "SUPABASE_MCP_TOKEN"),
        _cfg("ms365", "MICROSOFT_365_MCP_URL", "MICROSOFT_365_MCP_TOKEN"),
    ]


def build_remote_clients(session: aiohttp.ClientSession,
                          configs: Optional[List[RemoteMCPServerConfig]] = None) -> Dict[str, MCPClient]:
    configs = configs if configs is not None else default_remote_configs()
    clients: Dict[str, MCPClient] = {}
    for cfg in configs:
        if not cfg.enabled:
            logger.info("mcp.remote: '%s' desabilitado (sem base_url configurada)", cfg.name)
            continue
        clients[cfg.name] = MCPClient(cfg, session)
    return clients


# ---------------------------------------------------------------------------
# MCPServer — o Manta Backend NO PAPEL de MCP server
# ---------------------------------------------------------------------------

class MCPServer:
    """Representa o Manta Backend como um MCP server: agrega o
    `ToolRegistry` local com as tools espelhadas dos MCP servers
    remotos (GitHub, Supabase, MS365) sob namespace, e sabe:

      - listar todas as tools (`list_all_tools`)
      - invocar qualquer uma delas por nome (`invoke`) — despachando
        para o handler local ou para o `MCPClient` remoto certo
      - responder ao protocolo JSON-RPC 2.0 (`handle_jsonrpc`) para que
        clientes MCP externos (Claude Desktop, outro Manta Backend)
        conversem com este processo como um MCP server de verdade.
    """

    def __init__(self, registry: ToolRegistry, remote_clients: Optional[Dict[str, MCPClient]] = None):
        self.registry = registry
        self.remote_clients: Dict[str, MCPClient] = remote_clients or {}
        self._remote_cache: Dict[str, MCPTool] = {}
        self._cache_loaded = False

    async def refresh_remote_tools(self) -> None:
        """Consulta `tools/list` em cada MCP server remoto e guarda os
        resultados namespaceados (`github.search_repositories`, etc.).
        Falhas em um server remoto não derrubam os demais nem as tools
        locais — apenas ficam de fora do registry até a próxima refresh."""
        for name, client in self.remote_clients.items():
            try:
                tools = await client.list_tools()
            except MCPUpstreamError as exc:
                logger.warning("mcp.remote: falha ao listar tools de '%s': %s", name, exc)
                continue
            for tool in tools:
                namespaced = tool.model_copy(update={"name": f"{name}.{tool.name}"})
                self._remote_cache[namespaced.name] = namespaced
        self._cache_loaded = True

    async def list_all_tools(self, force_refresh: bool = False) -> List[MCPTool]:
        if force_refresh or not self._cache_loaded:
            await self.refresh_remote_tools()
        return self.registry.list_tools() + list(self._remote_cache.values())

    async def invoke(self, tool_name: str, arguments: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        """Ponto único de invocação: tools locais primeiro (namespace
        implícito `manta.*` registrado diretamente pelo nome), depois
        tools remotas via `<server>.<tool>` (ex.: `github.search_repositories`)."""
        local_entry = self.registry.get(tool_name)
        if local_entry is not None:
            tool, handler = local_entry
            logger.info("mcp.invoke local: %s (trace=%s actor=%s)", tool_name, context.trace_id, context.actor)
            return await handler(arguments, context)

        if "." in tool_name:
            server_name, remote_name = tool_name.split(".", 1)
            client = self.remote_clients.get(server_name)
            if client is not None:
                logger.info("mcp.invoke remoto: %s->%s (trace=%s actor=%s)",
                            server_name, remote_name, context.trace_id, context.actor)
                return await client.call_tool(remote_name, arguments, context)

        raise ToolNotFoundError(tool_name)

    # -- protocolo JSON-RPC 2.0, para clientes MCP externos batendo em POST /mcp --

    async def handle_jsonrpc(self, payload: Dict[str, Any], context: MCPContext) -> Optional[Dict[str, Any]]:
        method = payload.get("method")
        req_id = payload.get("id")
        params = payload.get("params") or {}
        is_notification = "id" not in payload

        def _ok(result: Any) -> Dict[str, Any]:
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        def _err(code: int, message: str) -> Dict[str, Any]:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

        if method == "initialize":
            return _ok({
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "serverInfo": {"name": "manta-backend", "version": "0.1.0"},
                "capabilities": {"tools": {"listChanged": False}},
            })

        if method == "notifications/initialized":
            return None  # notificação: sem resposta

        if method == "tools/list":
            tools = await self.list_all_tools()
            return _ok({"tools": [
                {"name": t.name, "description": t.description, "inputSchema": t.input_schema}
                for t in tools
            ]})

        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not name:
                return None if is_notification else _err(-32602, "Parâmetro 'name' obrigatório em tools/call")
            try:
                result = await self.invoke(name, arguments, context)
                return None if is_notification else _ok({
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                    "isError": False,
                })
            except ToolNotFoundError as exc:
                return None if is_notification else _err(-32601, str(exc))
            except MCPUpstreamError as exc:
                return None if is_notification else _ok({
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                })

        return None if is_notification else _err(-32601, f"Método '{method}' não suportado")


# ---------------------------------------------------------------------------
# Tools locais do Manta Backend (agentes, routing, ciclo de vida)
# ---------------------------------------------------------------------------

def build_default_registry() -> ToolRegistry:
    """Registra as tools locais do Manta Backend — espelham o CLAUDE.md
    master (registro de agentes + motor de roteamento Q1 + ciclo de
    vida) como capacidades MCP invocáveis por qualquer agente Claude."""
    from routers.agents import AGENT_REGISTRY, LIFECYCLE_PHASES

    registry = ToolRegistry()

    async def _list_agents(arguments: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        axis = arguments.get("axis")
        agents = AGENT_REGISTRY if not axis else [a for a in AGENT_REGISTRY if a.axis == axis]
        return {"count": len(agents), "agents": [a.model_dump() for a in agents]}

    registry.register(
        MCPTool(
            name="manta.list_agents",
            description=(
                "Lista os agentes IA da Manta Associados (registro mestre do CLAUDE.md), "
                "opcionalmente filtrando por eixo (horizontal|vertical)."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "axis": {"type": "string", "enum": ["horizontal", "vertical"],
                              "description": "Filtra por eixo do agente."},
                },
            },
        ),
        _list_agents,
    )

    async def _classify_routing(arguments: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        from routers.routing import classify, ClassifyRequest

        text = arguments.get("text", "")
        result = await classify(ClassifyRequest(text=text))
        return result.model_dump()

    registry.register(
        MCPTool(
            name="manta.classify_routing",
            description=(
                "Classifica um texto livre (Q1 do intake) e devolve o agente vertical do "
                "Maestro (Manta 00) responsável — regras de routing por segmento (S1-S10)."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto livre descrevendo o projeto/pedido."},
                },
                "required": ["text"],
            },
        ),
        _classify_routing,
    )

    async def _list_lifecycle_phases(arguments: Dict[str, Any], context: MCPContext) -> Dict[str, Any]:
        return {"phases": LIFECYCLE_PHASES}

    registry.register(
        MCPTool(
            name="manta.list_lifecycle_phases",
            description="Lista as 8 fases do ciclo de vida (Eixo 3) suportadas por todo agente vertical.",
            input_schema={"type": "object", "properties": {}},
        ),
        _list_lifecycle_phases,
    )

    return registry


# ---------------------------------------------------------------------------
# FastAPI router — GET /mcp/tools, POST /mcp/invoke/{tool_name}, POST /mcp
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/mcp", tags=["mcp"])


async def get_optional_actor(request: Request) -> Dict[str, str]:
    """Autenticação best-effort: usa o JWT (RS256, `auth.decode_token`)
    se presente/válido para identificar o `actor` no MCPContext; degrada
    para "anonymous" em vez de bloquear — GET /mcp/tools e o invoke
    continuam usáveis por clientes MCP externos sem login (ex.: Claude
    Desktop local). Lê o Bearer token direto do header em vez de puxar
    `auth.oauth2_scheme` como Depends para não acoplar este módulo ao
    formato exato da dependency de auth (que evolui em `auth.py`)."""
    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            from auth import decode_token

            payload = decode_token(token)
            roles = payload.get("roles") or []
            actor = payload.get("email") or payload.get("sub") or "unknown"
            return {"actor": actor, "role": roles[0] if roles else "user"}
        except HTTPException:
            pass
        except Exception as exc:  # noqa: BLE001 - auth em evolução; nunca derruba /mcp
            logger.warning("mcp.auth: token presente mas não decodificável (%s)", exc)
    return {"actor": "anonymous", "role": "anonymous"}


def get_mcp_server(request: Request) -> MCPServer:
    server = getattr(request.app.state, "mcp_server", None)
    if server is None:
        # Fallback: em testes/scripts sem lifespan, monta um server
        # local-only sob demanda (sem tools remotas — sem sessão HTTP viva).
        server = MCPServer(build_default_registry(), remote_clients={})
        request.app.state.mcp_server = server
    return server


class InvokeRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)
    agent_code: Optional[str] = Field(default=None, description="Código do agente Manta em nome de quem a tool é chamada.")


@router.get("/tools", summary="Lista tools MCP disponíveis (locais + remotas: GitHub/Supabase/MS365)")
async def list_tools(request: Request, refresh: bool = False,
                      actor: Dict[str, str] = Depends(get_optional_actor)) -> Dict[str, Any]:
    server = get_mcp_server(request)
    tools = await server.list_all_tools(force_refresh=refresh)
    return {"tools": [t.model_dump() for t in tools], "count": len(tools)}


@router.post("/invoke/{tool_name}", summary="Invoca uma tool MCP (local ou remota) por nome")
async def invoke_tool(tool_name: str, payload: InvokeRequest, request: Request,
                       actor: Dict[str, str] = Depends(get_optional_actor)) -> Dict[str, Any]:
    server = get_mcp_server(request)
    context = MCPContext.new(actor=actor["actor"], actor_role=actor["role"], agent_code=payload.agent_code)
    try:
        result = await server.invoke(tool_name, payload.arguments, context)
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MCPUpstreamError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return {"tool": tool_name, "context": context.to_dict(), "result": result}


@router.post("", summary="Endpoint JSON-RPC 2.0 — permite plugar este backend como MCP server em qualquer cliente MCP")
async def mcp_jsonrpc(request: Request, actor: Dict[str, str] = Depends(get_optional_actor)) -> Any:
    body = await request.json()
    server = get_mcp_server(request)
    context = MCPContext.new(actor=actor["actor"], actor_role=actor["role"])
    response = await server.handle_jsonrpc(body, context)
    return response if response is not None else {}


# ---------------------------------------------------------------------------
# Integração com agentes Claude (Anthropic Messages API + tool use)
# ---------------------------------------------------------------------------

def tools_for_claude(tools: List[MCPTool]) -> List[Dict[str, Any]]:
    """Converte MCPTool -> formato `tools=[...]` da Claude Messages API.
    `input_schema` já é JSON Schema em ambos os mundos (MCP e Claude),
    então a conversão é direta."""
    return [{"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in tools]


async def run_claude_agent(
    server: MCPServer,
    context: MCPContext,
    user_message: str,
    model: str = "claude-sonnet-4-5",
    system: Optional[str] = None,
    max_tool_turns: int = 5,
) -> Dict[str, Any]:
    """Loop de agente Claude com acesso às tools MCP do `server`
    (locais + remotas). A cada `tool_use` do Claude, despacha via
    `server.invoke()` — que já injeta o `MCPContext` — e devolve o
    `tool_result`; repete até o Claude parar de chamar tools ou até
    `max_tool_turns`.

    Requer `pip install anthropic` e `ANTHROPIC_API_KEY` no ambiente;
    o import é lazy para que o resto do módulo funcione sem a lib.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError(
            "run_claude_agent precisa do pacote 'anthropic' (pip install anthropic)."
        ) from exc

    client = anthropic.AsyncAnthropic()
    tools = tools_for_claude(await server.list_all_tools())
    messages: List[Dict[str, Any]] = [{"role": "user", "content": user_message}]

    for _ in range(max_tool_turns):
        response = await client.messages.create(
            model=model,
            max_tokens=2048,
            system=system or (
                "Você é um agente do Manta Maestro. Use as tools MCP disponíveis "
                "(prefixo manta.*, github.*, supabase.*, ms365.*) para responder com precisão."
            ),
            tools=tools,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if not tool_uses:
            final_text = "".join(block.text for block in response.content if block.type == "text")
            return {"final_text": final_text, "messages": messages, "stop_reason": response.stop_reason}

        tool_results = []
        for call in tool_uses:
            try:
                result = await server.invoke(call.name, call.input, context)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
            except (ToolNotFoundError, MCPUpstreamError) as exc:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": str(exc),
                    "is_error": True,
                })
        messages.append({"role": "user", "content": tool_results})

    return {"final_text": None, "messages": messages, "truncated": True}


# ---------------------------------------------------------------------------
# Exemplo de invoke funcionando (sem precisar de rede/credenciais)
# ---------------------------------------------------------------------------

async def _demo() -> None:
    logging.basicConfig(level=logging.INFO)

    registry = build_default_registry()
    server = MCPServer(registry, remote_clients={})  # sem remotos: demo 100% offline
    context = MCPContext.new(actor="mneves@mantaassociados.com", actor_role="admin", agent_code="Manta 00")

    print("=== 1) GET /mcp/tools (via list_all_tools) ===")
    tools = await server.list_all_tools()
    for t in tools:
        print(f"  - {t.name} ({t.server}): {t.description}")

    print("\n=== 2) POST /mcp/invoke/manta.classify_routing ===")
    result = await server.invoke(
        "manta.classify_routing",
        {"text": "Precisamos avaliar uma dragagem no berço 3 do porto de Santos, ANTAQ já autorizou o EVTE."},
        context,
    )
    print(f"  contexto: trace_id={context.trace_id} actor={context.actor}")
    print(f"  resultado: {json.dumps(result, ensure_ascii=False, indent=2)}")

    print("\n=== 3) POST /mcp/invoke/manta.list_agents (axis=vertical) ===")
    result2 = await server.invoke("manta.list_agents", {"axis": "vertical"}, context)
    print(f"  {result2['count']} agentes verticais encontrados: "
          f"{[a['code'] for a in result2['agents']]}")

    print("\n=== 4) JSON-RPC (tools/call) — mesmo dispatcher usado por clientes MCP externos ===")
    rpc_response = await server.handle_jsonrpc({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "manta.list_lifecycle_phases", "arguments": {}},
    }, context)
    print(f"  {json.dumps(rpc_response, ensure_ascii=False, indent=2)}")

    print("\n=== 5) tools_for_claude() — formato pronto para `tools=` da Messages API ===")
    print(json.dumps(tools_for_claude(tools), ensure_ascii=False, indent=2))

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("\n=== 6) run_claude_agent() — loop real de tool-use com Claude ===")
        agent_result = await run_claude_agent(
            server, context,
            user_message="Qual agente Manta trata de dragagem em porto e quais são as fases de ciclo de vida suportadas?",
        )
        print(agent_result["final_text"])
    else:
        print("\n=== 6) run_claude_agent() ===")
        print("  ANTHROPIC_API_KEY não definida — pulando chamada real ao Claude "
              "(a integração acima, 1-5, já demonstra o invoke funcionando ponta a ponta).")


if __name__ == "__main__":
    asyncio.run(_demo())
