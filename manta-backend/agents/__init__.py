"""
agents — Pacote com módulos para execução de agentes IA.

- mcp_tools: Executor de ferramentas MCP (schema, validação, execução)
- claude_invoker: Wrapper da Claude API (streaming, tool_use, token counting)
"""

from agents.claude_invoker import ClaudeInvoker, ClaudeInvokerError
from agents.mcp_tools import MCPToolError, MCPToolExecutor, MCPTool

__all__ = [
    "ClaudeInvoker",
    "ClaudeInvokerError",
    "MCPToolExecutor",
    "MCPTool",
    "MCPToolError",
]
