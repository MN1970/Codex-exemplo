"""
agents/mcp_tools.py — Executor de ferramentas MCP para uso por agentes.

Dado um schema de ferramenta MCP e uma entrada, executa via cliente MCP,
trata erros e retorna resultados estruturados. Suporta execução sequencial
de múltiplas ferramentas com passagem de estado.
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("manta.agents.mcp_tools")


class MCPToolError(Exception):
    """Erro na execução de ferramenta MCP."""
    pass


class MCPTool:
    """Descritor de uma ferramenta MCP com schema."""

    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        required: Optional[List[str]] = None,
    ):
        """
        Inicializa uma ferramenta MCP.

        Args:
            name: Nome da ferramenta (ex: 'get_file_contents')
            description: Descrição legível
            input_schema: Schema JSON (properties + type)
            required: Lista de propriedades obrigatórias
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.required = required or []

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Valida entrada contra o schema da ferramenta.

        Raises:
            MCPToolError: Se a entrada for inválida
        """
        for req_field in self.required:
            if req_field not in input_data:
                raise MCPToolError(
                    f"Ferramenta '{self.name}' requer campo obrigatório: {req_field}"
                )

        props = self.input_schema.get("properties", {})
        for key, value in input_data.items():
            if key in props:
                expected_type = props[key].get("type")
                if expected_type and not self._check_type(value, expected_type):
                    raise MCPToolError(
                        f"Campo '{key}' deve ser {expected_type}, recebeu {type(value).__name__}"
                    )

    @staticmethod
    def _check_type(value: Any, expected: str) -> bool:
        """Verifica se valor corresponde ao tipo esperado."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected_type = type_map.get(expected)
        if expected_type is None:
            return True  # tipo desconhecido, permite
        return isinstance(value, expected_type)


class MCPToolExecutor:
    """Executor de ferramentas MCP via cliente MCP do backend."""

    def __init__(self, mcp_client: Any):
        """
        Inicializa o executor com um cliente MCP.

        Args:
            mcp_client: Instância de MCPClient (do mcp/client.py)
        """
        self.mcp_client = mcp_client
        self._tool_cache: Dict[str, MCPTool] = {}

    async def list_tools(self) -> List[MCPTool]:
        """
        Lista todas as ferramentas disponíveis no gateway MCP.

        Returns:
            Lista de MCPTool com schemas

        Raises:
            MCPToolError: Se o gateway não responder
        """
        try:
            # Chama o endpoint de listagem do gateway
            response = await self.mcp_client.call("tools/list", {})
            tools = []

            for tool_data in response.get("tools", []):
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                    required=tool_data.get("inputSchema", {}).get("required", []),
                )
                tools.append(tool)
                self._tool_cache[tool.name] = tool

            return tools
        except Exception as e:
            raise MCPToolError(f"Falha ao listar ferramentas MCP: {e}") from e

    async def execute(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executa uma ferramenta MCP.

        Args:
            tool_name: Nome da ferramenta
            tool_input: Dicionário com parâmetros de entrada

        Returns:
            Resultado da execução (content list de results da spec MCP)

        Raises:
            MCPToolError: Se a ferramenta falhar
        """
        logger.info("Executando ferramenta MCP: %s com entrada: %s", tool_name, tool_input)

        try:
            # Valida input contra schema se disponível
            if tool_name in self._tool_cache:
                self._tool_cache[tool_name].validate_input(tool_input)

            # Chama o gateway
            response = await self.mcp_client.call(
                f"tools/execute",
                {
                    "name": tool_name,
                    "arguments": tool_input,
                }
            )

            logger.info("Ferramenta %s executada com sucesso", tool_name)
            return {
                "success": True,
                "tool": tool_name,
                "result": response,
            }
        except MCPToolError:
            raise
        except Exception as e:
            logger.error("Erro ao executar ferramenta %s: %s", tool_name, e)
            raise MCPToolError(f"Erro ao executar '{tool_name}': {e}") from e

    async def execute_sequence(
        self,
        tools: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Executa uma sequência de ferramentas, passando saída para entrada seguinte.

        Cada elemento de tools deve ter:
        - name: str (nome da ferramenta)
        - input: dict (parâmetros, pode usar {{resultado_anterior}} para substituição)

        Args:
            tools: Lista de ferramentas a executar

        Returns:
            Lista de resultados na mesma ordem

        Raises:
            MCPToolError: Se qualquer ferramenta falhar
        """
        results = []
        context = {}

        for i, tool_spec in enumerate(tools):
            tool_name = tool_spec.get("name")
            tool_input = tool_spec.get("input", {})

            if not tool_name:
                raise MCPToolError(f"Ferramenta {i}: 'name' é obrigatório")

            # Substitui placeholders {{resultado_N}} com resultados anteriores
            tool_input = self._substitute_context(tool_input, context)

            result = await self.execute(tool_name, tool_input)
            results.append(result)
            context[f"resultado_{i}"] = result.get("result")

        return results

    @staticmethod
    def _substitute_context(obj: Any, context: Dict[str, Any]) -> Any:
        """
        Substitui placeholders {{chave}} recursivamente em um objeto.

        Args:
            obj: Objeto (dict, list, str, etc)
            context: Mapa de substituições

        Returns:
            Objeto com placeholders substituídos
        """
        if isinstance(obj, str):
            # Substitui {{resultado_N}} por valor do contexto
            import re
            def replace_placeholder(match):
                key = match.group(1)
                return json.dumps(context.get(key, f"{{{{resultado}}}}"))
            return re.sub(r"\{\{([^}]+)\}\}", replace_placeholder, obj)
        elif isinstance(obj, dict):
            return {k: MCPToolExecutor._substitute_context(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [MCPToolExecutor._substitute_context(item, context) for item in obj]
        else:
            return obj
