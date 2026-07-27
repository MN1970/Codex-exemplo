"""
routers/executor.py — Endpoint de execução de agentes com Claude + MCP tools.

POST /executor/{agent_slug} — Invoca um agente com um prompt, streamando resposta
via SSE (Server-Sent Events), executando tool_uses conforme necessário e
persistindo a sessão completa em Postgres.
"""
import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import get_settings
from pg_pool import acquire_optional
from agents.claude_invoker import ClaudeInvoker, ClaudeInvokerError
from agents.mcp_tools import MCPToolExecutor, MCPToolError

logger = logging.getLogger("manta.executor")
router = APIRouter(prefix="/executor", tags=["executor"])

settings = get_settings()

# Lazy-loaded instances (inicializados na primeira requisição)
_claude_invoker: Optional[ClaudeInvoker] = None
_mcp_executor: Optional[MCPToolExecutor] = None


class ExecutorRequest(BaseModel):
    """Requisição para execução de agente."""
    prompt: str = Field(..., min_length=1, max_length=8000)
    agent_code: str = Field("Manta XX", description="Código do agente")
    agent_name: str = Field("agente", description="Nome do agente")
    complexity: str = Field(
        "normal",
        description="Complexidade: 'simple'/'normal'/'complex'",
        pattern="^(simple|normal|complex)$",
    )
    user_email: Optional[str] = None
    system_prompt_override: Optional[str] = None


class ExecutorSession(BaseModel):
    """Sessão de execução com histórico completo."""
    id: str
    agent_code: str
    agent_slug: str
    prompt: str
    response: str
    tool_calls: List[dict] = []
    user_email: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = True
    error_message: Optional[str] = None


# Fallback em memória para quando Postgres não estiver disponível
_SESSION_STORE: List[ExecutorSession] = []


def _sse(event: str, data: dict) -> bytes:
    """Codifica um evento no formato Server-Sent Events."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


async def _get_claude_invoker() -> ClaudeInvoker:
    """Retorna instância singleton de ClaudeInvoker (lazy loading)."""
    global _claude_invoker
    if _claude_invoker is None:
        _claude_invoker = ClaudeInvoker(
            api_key=settings.claude_api_key,
            default_model=settings.claude_default_model,
            opus_model=settings.claude_opus_model,
            max_tokens=settings.claude_max_tokens,
            timeout_seconds=settings.claude_streaming_timeout,
            mcp_executor=None,  # Será inicializado junto com MCP
        )
    return _claude_invoker


async def _get_mcp_executor(request: Request) -> Optional[MCPToolExecutor]:
    """Retorna instância singleton de MCPToolExecutor (lazy loading)."""
    global _mcp_executor
    if _mcp_executor is None and hasattr(request.app.state, 'mcp_client'):
        try:
            _mcp_executor = MCPToolExecutor(request.app.state.mcp_client)
        except Exception as e:
            logger.warning("Não foi possível inicializar MCPToolExecutor: %s", e)
    return _mcp_executor


async def _persist_session(pool, record: ExecutorSession) -> None:
    """Persiste uma sessão em Postgres ou memória (fallback)."""
    if pool is None:
        logger.info("executor: DB indisponível, guardando sessão em memória (%s)", record.id)
        _SESSION_STORE.append(record)
        return

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO executor_sessions
                    (id, agent_code, agent_slug, prompt, response, tool_calls,
                     user_email, created_at, completed_at, success, error_message)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                record.id,
                record.agent_code,
                record.agent_slug,
                record.prompt,
                record.response,
                json.dumps(record.tool_calls),
                record.user_email,
                record.created_at,
                record.completed_at,
                record.success,
                record.error_message,
            )
    except Exception as e:
        logger.error("Erro persistindo sessão em DB: %s. Usando fallback em memória.", e)
        _SESSION_STORE.append(record)


@router.post(
    "/{agent_slug}",
    summary="Executa um agente com prompt (streaming SSE)",
    description=(
        "Invoca um agente com um prompt, streamando resposta via Server-Sent Events. "
        "Executa ferramentas MCP conforme necessário e persiste a sessão completa."
    ),
)
async def execute_agent(
    agent_slug: str,
    payload: ExecutorRequest,
    request: Request,
) -> StreamingResponse:
    """
    Endpoint de execução de agente.

    Args:
        agent_slug: Slug do agente (ex: 'claims', 'agente-saneamento')
        payload: Requisição com prompt e configurações
        request: Request FastAPI (para acesso ao app state)

    Returns:
        StreamingResponse com eventos SSE

    Raises:
        HTTPException: Se API Claude não configurada ou agente não encontrado
    """
    if not settings.claude_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "Claude API não configurada. "
                "Configure CLAUDE_API_KEY no .env"
            ),
        )

    # Captura pool antes de entrar no gerador
    pool = getattr(request.app.state, "db_pool", None)

    async def event_stream() -> AsyncIterator[bytes]:
        session_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        response_text = ""
        tool_calls_log: List[dict] = []
        session_error: Optional[str] = None
        session_success = True

        try:
            # Inicializa Claude invoker
            invoker = await _get_claude_invoker()
            mcp_executor = await _get_mcp_executor(request)

            # Se MCP está disponível, usa invoke_with_tools (iterativo)
            if mcp_executor and settings.claude_api_key:
                invoker.mcp_executor = mcp_executor
                use_tools = True
            else:
                use_tools = False

            # Notifica início
            yield _sse("meta", {
                "session_id": session_id,
                "agent_slug": agent_slug,
                "agent_code": payload.agent_code,
                "has_tools": use_tools,
            })

            # Invoca Claude
            if use_tools:
                logger.info(
                    "Executor: invocando %s com tools (complexidade=%s)",
                    agent_slug, payload.complexity
                )
                async for event in invoker.invoke_with_tools(
                    prompt=payload.prompt,
                    agent_name=payload.agent_name,
                    agent_code=payload.agent_code,
                    max_iterations=5,
                    system_prompt=payload.system_prompt_override,
                ):
                    if event["type"] == "text":
                        delta = event["content"]
                        response_text += delta
                        yield _sse("chunk", {"delta": delta})

                    elif event["type"] == "tool_use":
                        tool_info = {
                            "tool_name": event["tool_name"],
                            "tool_use_id": event["tool_use_id"],
                        }
                        yield _sse("tool_use", tool_info)
                        tool_calls_log.append(tool_info)

                    elif event["type"] == "tool_result":
                        yield _sse("tool_result", {
                            "tool_name": event["tool_name"],
                            "success": event["tool_result"].get("success", False),
                        })

                    elif event["type"] == "tool_error":
                        yield _sse("tool_error", {
                            "tool_name": event["tool_name"],
                            "error": event["error"],
                        })

                    elif event["type"] == "done":
                        break

            else:
                # Sem tools, usa invoke simples (streaming apenas)
                logger.info(
                    "Executor: invocando %s sem tools (complexidade=%s)",
                    agent_slug, payload.complexity
                )
                async for chunk in invoker.invoke(
                    prompt=payload.prompt,
                    agent_name=payload.agent_name,
                    agent_code=payload.agent_code,
                    complexity=payload.complexity,
                    system_prompt=payload.system_prompt_override,
                ):
                    response_text += chunk
                    yield _sse("chunk", {"delta": chunk})

        except ClaudeInvokerError as e:
            logger.error("Erro no Claude invoker: %s", e)
            session_error = str(e)
            session_success = False
            yield _sse("error", {
                "message": f"Erro ao invocar Claude: {e}",
                "type": "invoker_error",
            })

        except MCPToolError as e:
            logger.error("Erro no executor MCP: %s", e)
            session_error = str(e)
            session_success = False
            yield _sse("error", {
                "message": f"Erro ao executar ferramenta: {e}",
                "type": "tool_error",
            })

        except asyncio.TimeoutError as e:
            logger.error("Timeout na execução: %s", e)
            session_error = "Timeout ao executar agente"
            session_success = False
            yield _sse("error", {
                "message": "Timeout ao executar agente",
                "type": "timeout",
            })

        except Exception as e:
            logger.error("Erro inesperado na execução: %s", e)
            session_error = str(e)
            session_success = False
            yield _sse("error", {
                "message": f"Erro inesperado: {e}",
                "type": "unknown",
            })

        finally:
            # Persiste sessão
            completed_at = datetime.now(timezone.utc)
            record = ExecutorSession(
                id=session_id,
                agent_code=payload.agent_code,
                agent_slug=agent_slug,
                prompt=payload.prompt,
                response=response_text,
                tool_calls=tool_calls_log,
                user_email=payload.user_email,
                created_at=created_at,
                completed_at=completed_at,
                success=session_success,
                error_message=session_error,
            )
            await _persist_session(pool, record)

            # Notifica conclusão
            yield _sse("done", {
                "session_id": session_id,
                "success": session_success,
                "response_length": len(response_text),
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/sessions/{agent_slug}",
    response_model=List[ExecutorSession],
    summary="Histórico de sessões de execução de um agente",
)
async def list_executor_sessions(
    agent_slug: str,
    request: Request,
    limit: int = 20,
) -> List[ExecutorSession]:
    """Lista sessões recentes de execução de um agente."""
    async with acquire_optional(request) as conn:
        if conn is not None:
            try:
                rows = await conn.fetch(
                    """
                    SELECT id, agent_code, agent_slug, prompt, response, tool_calls,
                           user_email, created_at, completed_at, success, error_message
                    FROM executor_sessions
                    WHERE agent_slug = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    agent_slug,
                    limit,
                )
                return [
                    ExecutorSession(
                        **{
                            **dict(r),
                            "tool_calls": json.loads(r["tool_calls"] or "[]"),
                        }
                    )
                    for r in rows
                ]
            except Exception as e:
                logger.warning("Erro ao listar sessões de DB: %s", e)

    # Fallback em memória
    matching = [s for s in _SESSION_STORE if s.agent_slug == agent_slug]
    return list(reversed(matching))[:limit]


@router.post(
    "/token-count",
    summary="Conta tokens antes de executar (estimativa de custo)",
)
async def count_executor_tokens(
    agent_slug: str,
    prompt: str,
    system_prompt_override: Optional[str] = None,
) -> dict:
    """Conta tokens em uma requisição (para estimativa de custo)."""
    if not settings.claude_api_key:
        raise HTTPException(status_code=503, detail="Claude API não configurada")

    try:
        invoker = await _get_claude_invoker()
        token_count = await invoker.count_tokens(
            prompt=prompt,
            system_prompt=system_prompt_override,
        )
        return {
            "tokens": token_count,
            "estimated_cost": token_count * 0.000003,  # Preço aproximado por token
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao contar tokens: {e}",
        )
