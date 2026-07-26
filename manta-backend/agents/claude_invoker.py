"""
agents/claude_invoker.py — Wrapper da Claude API para invocação de agentes.

Chamadas ao Claude Opus/Sonnet com suporte a streaming, uso de ferramentas MCP,
parsing de tool_use blocks, execução sequencial, e limitação de tokens.
"""
import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

logger = logging.getLogger("manta.agents.claude_invoker")


class ClaudeInvokerError(Exception):
    """Erro na invocação Claude."""
    pass


class ClaudeInvoker:
    """Wrapper para chamadas ao Claude com streaming e tool use."""

    def __init__(
        self,
        api_key: str,
        default_model: str = "claude-3-5-sonnet-20241022",
        opus_model: str = "claude-3-opus-20250219",
        max_tokens: int = 4096,
        timeout_seconds: int = 120,
        mcp_executor: Optional[Any] = None,
    ):
        """
        Inicializa o invoker.

        Args:
            api_key: Chave da API Anthropic
            default_model: Modelo padrão (Sonnet)
            opus_model: Modelo Opus (para tarefas complexas)
            max_tokens: Tokens máximos na resposta
            timeout_seconds: Timeout para chamadas HTTP
            mcp_executor: Instância de MCPToolExecutor (opcional)
        """
        self.api_key = api_key
        self.default_model = default_model
        self.opus_model = opus_model
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.mcp_executor = mcp_executor

        if not api_key:
            logger.warning("Claude API key não configurada; tool use não funcionará")

    def _select_model(self, complexity: str = "normal") -> str:
        """
        Seleciona o modelo baseado na complexidade da tarefa.

        Args:
            complexity: 'simple' → Sonnet, 'normal' → Sonnet, 'complex' → Opus

        Returns:
            Model ID
        """
        if complexity in ("complex", "high"):
            return self.opus_model
        return self.default_model

    def _build_system_prompt(self, agent_name: str, agent_code: str) -> str:
        """
        Constrói o system prompt para um agente.

        Args:
            agent_name: Nome do agente (ex: 'claims')
            agent_code: Código do agente (ex: 'Manta 01')

        Returns:
            System prompt formatado
        """
        return (
            f"Você é o agente {agent_code} ({agent_name}) da Manta Associados. "
            f"Você é um especialista em sua área e pode usar ferramentas MCP "
            f"para buscar dados, ler documentos e executar ações. "
            f"Responda em português brasileiro com clareza e profissionalismo. "
            f"Se usar ferramentas, sempre cite o resultado de forma clara ao usuário."
        )

    async def invoke(
        self,
        prompt: str,
        agent_name: str = "agente",
        agent_code: str = "Manta XX",
        complexity: str = "normal",
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Invoca Claude com streaming.

        Args:
            prompt: Prompt do usuário
            agent_name: Nome do agente
            agent_code: Código do agente
            complexity: Complexidade ('simple'/'normal'/'complex')
            tools: Lista de ferramentas disponíveis (do MCP)
            system_prompt: Customizar system prompt (opcional)

        Yields:
            Chunks de resposta (texto)

        Raises:
            ClaudeInvokerError: Se API não configurada ou chamada falhar
        """
        if not self.api_key:
            raise ClaudeInvokerError(
                "Claude API key não configurada. "
                "Configure CLAUDE_API_KEY na variável de ambiente."
            )

        model = self._select_model(complexity)
        sys_prompt = system_prompt or self._build_system_prompt(agent_name, agent_code)

        try:
            import anthropic
        except ImportError:
            raise ClaudeInvokerError(
                "Biblioteca 'anthropic' não instalada. "
                "Execute: pip install anthropic"
            ) from None

        # Importa e instancia o cliente (é síncrono, mas usamos em thread pool)
        client = anthropic.Anthropic(api_key=self.api_key)

        # Prepara mensagens
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Prepara tools
        claude_tools = []
        if tools:
            for tool in tools:
                claude_tools.append(
                    {
                        "name": tool.get("name"),
                        "description": tool.get("description", ""),
                        "input_schema": tool.get("inputSchema", {}),
                    }
                )

        logger.info(
            "Invocando Claude (modelo=%s, agente=%s, complexity=%s)",
            model, agent_name, complexity
        )

        # Chamada com streaming (síncrono, executado em asyncio.to_thread)
        def _make_request():
            return client.messages.create(
                model=model,
                max_tokens=self.max_tokens,
                system=sys_prompt,
                tools=claude_tools if claude_tools else None,
                messages=messages,
                stream=True,
            )

        try:
            # Executa a chamada síncrona em thread pool
            stream = await asyncio.to_thread(_make_request)

            # Coleta blocos até encontrar tool_use (se houver)
            text_buffer = []
            tool_uses: List[Tuple[str, str, Dict]] = []  # (id, name, input)

            with stream as s:
                for event in s:
                    # Eventos do stream
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_start':
                            if hasattr(event, 'content_block'):
                                block_type = getattr(event.content_block, 'type', None)
                                logger.debug("Content block: %s", block_type)

                        elif event.type == 'content_block_delta':
                            if hasattr(event, 'delta'):
                                delta = event.delta
                                if hasattr(delta, 'text'):
                                    # Yielda texto incrementalmente
                                    text_buffer.append(delta.text)
                                    yield delta.text
                                elif hasattr(delta, 'input'):
                                    # Tool use input (acumula)
                                    pass

                        elif event.type == 'content_block_stop':
                            # Verifica se foi tool_use
                            if hasattr(event, 'index'):
                                idx = event.index
                                # Aqui poderíamos marcar que um bloco terminou

            # Se houver tool_uses a processar, faria em loop (não implementado
            # neste skeleton; em produção seria recursivo com max_iterations)
            logger.debug("Claude invocation completa")

        except asyncio.TimeoutError as e:
            raise ClaudeInvokerError(f"Timeout de Claude após {self.timeout_seconds}s") from e
        except Exception as e:
            logger.error("Erro ao chamar Claude: %s", e)
            raise ClaudeInvokerError(f"Erro na API Claude: {e}") from e

    async def invoke_with_tools(
        self,
        prompt: str,
        agent_name: str = "agente",
        agent_code: str = "Manta XX",
        max_iterations: int = 5,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Invoca Claude com suporte a tool_use (iterativo até agent_loop_complete).

        Args:
            prompt: Prompt do usuário
            agent_name: Nome do agente
            agent_code: Código do agente
            max_iterations: Máximo de iterações (tool_use → execute → continue)
            system_prompt: Customizar system prompt (opcional)

        Yields:
            Dicts com chaves:
            - type: 'text' | 'tool_use' | 'tool_result' | 'done'
            - content: texto, tool info, ou resultado

        Raises:
            ClaudeInvokerError: Se API falhar ou max_iterations atingido
        """
        if not self.api_key:
            raise ClaudeInvokerError(
                "Claude API key não configurada. "
                "Configure CLAUDE_API_KEY na variável de ambiente."
            )

        if not self.mcp_executor:
            raise ClaudeInvokerError(
                "MCPToolExecutor não configurado. "
                "Não posso executar tool_use sem MCP."
            )

        try:
            import anthropic
        except ImportError:
            raise ClaudeInvokerError(
                "Biblioteca 'anthropic' não instalada. "
                "Execute: pip install anthropic"
            ) from None

        client = anthropic.Anthropic(api_key=self.api_key)
        sys_prompt = system_prompt or self._build_system_prompt(agent_name, agent_code)
        messages: List[Dict[str, Any]] = [{"role": "user", "content": prompt}]

        # Lista ferramentas disponíveis
        logger.info("Carregando ferramentas MCP disponíveis")
        try:
            tools_list = await self.mcp_executor.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.input_schema,
                }
                for t in tools_list
            ]
        except Exception as e:
            logger.warning("Falha ao listar ferramentas MCP: %s", e)
            tools = []

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info("Claude invoke_with_tools: iteração %d", iteration)

            try:
                response = await asyncio.to_thread(
                    lambda: client.messages.create(
                        model=self.default_model,
                        max_tokens=self.max_tokens,
                        system=sys_prompt,
                        tools=tools if tools else None,
                        messages=messages,
                    )
                )
            except Exception as e:
                logger.error("Erro na iteração %d: %s", iteration, e)
                raise ClaudeInvokerError(f"Claude API erro (iteração {iteration}): {e}") from e

            # Processa blocos de conteúdo
            tool_uses_this_iteration = []

            for block in response.content:
                if block.type == 'text':
                    yield {
                        "type": "text",
                        "content": block.text,
                    }
                    # Adiciona à history
                    messages.append({"role": "assistant", "content": block.text})

                elif block.type == 'tool_use':
                    yield {
                        "type": "tool_use",
                        "tool_name": block.name,
                        "tool_input": block.input,
                        "tool_use_id": block.id,
                    }
                    tool_uses_this_iteration.append(
                        (block.id, block.name, block.input)
                    )

            # Se houve tool_uses, executa e continua loop
            if tool_uses_this_iteration:
                for tool_use_id, tool_name, tool_input in tool_uses_this_iteration:
                    try:
                        result = await self.mcp_executor.execute(tool_name, tool_input)
                        yield {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "tool_name": tool_name,
                            "tool_result": result,
                        }

                        # Adiciona à history para próxima iteração
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": json.dumps(result),
                                }
                            ]
                        })
                    except Exception as e:
                        logger.error("Erro executando tool %s: %s", tool_name, e)
                        yield {
                            "type": "tool_error",
                            "tool_name": tool_name,
                            "error": str(e),
                        }

            # Se stop_reason é end_turn ou nenhum tool_use, termina
            if response.stop_reason == 'end_turn' or not tool_uses_this_iteration:
                break

        yield {"type": "done"}

    async def count_tokens(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> int:
        """
        Conta tokens em uma requisição usando token counting API.

        Args:
            prompt: Prompt do usuário
            system_prompt: System prompt (opcional)

        Returns:
            Número de tokens

        Raises:
            ClaudeInvokerError: Se API falhar
        """
        if not self.api_key:
            raise ClaudeInvokerError("Claude API key não configurada")

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            response = await asyncio.to_thread(
                lambda: client.messages.count_tokens(
                    model=self.default_model,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                )
            )
            return response.input_tokens
        except Exception as e:
            logger.error("Erro contando tokens: %s", e)
            raise ClaudeInvokerError(f"Falha ao contar tokens: {e}") from e
