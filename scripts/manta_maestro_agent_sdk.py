#!/usr/bin/env python3
"""
Manta Maestro — entrypoint via Claude Agent SDK.

Roda o ecossistema Manta Maestro (regras de routing do CLAUDE.md + subagentes
de .claude/agents/ + guardiões de .claude/skills/) através do Claude Agent SDK
oficial (`claude-agent-sdk`), para poder ser chamado fora do Claude Code CLI —
de um serviço interno, um cron job, um bot de Slack etc.

Escopo deste script:
  - Carrega o CLAUDE.md e o injeta como `append` do preset de system prompt
    "claude_code" (`{"type": "preset", "preset": "claude_code", "append": ...}`),
    para que as regras de routing do Maestro (códigos S/A/F, tabela de
    keywords, model tiering) valham igual a uma sessão interativa do
    Claude Code.
  - Registra cada subagente REAL de .claude/agents/*.md como subagente do SDK,
    reaproveitando tests/lib/agent_loader.py — o mesmo parser que os testes
    do próprio repo usam — para que o conjunto de agentes aqui nunca
    diverja do que já é validado/lint-checado em outro lugar do repo.
  - Carrega .claude/skills/* (dedup-guard, consist-guard) via `skills="all"`
    do SDK.
  - NÃO carrega `.mcp.json` automaticamente: hoje esse arquivo não é JSON
    válido (tem chaves "comment" penduradas dentro de arrays, quebrando a
    sintaxe) e seu schema não bate com o formato real de `.mcp.json` do
    Claude Code / Agent SDK (campos extras como "tier", "capabilities",
    "rate_limiting" em vez do formato real command/args/env ou
    type/url/headers). Ver `_MCP_JSON_NOTE` abaixo. Para plugar um MCP real
    (ex.: SharePoint_Manta, Supabase), passe um config próprio via
    --mcp-config apontando para um JSON no formato real.

Uso:
    python3 scripts/manta_maestro_agent_sdk.py "Qual o RAP teto do leilão de transmissão X?"
    python3 scripts/manta_maestro_agent_sdk.py --agent agente-saneamento "Resuma o SNIS 2025"
    python3 scripts/manta_maestro_agent_sdk.py --allow-bash --agent agente-arquiteto-ia "rode o dedup-guard em teste.html"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tests.lib.agent_loader import AgentDef, AgentParseError, load_agent, load_all_agents  # noqa: E402

try:
    from claude_agent_sdk import (
        AgentDefinition,
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )
except ImportError as exc:
    # Reaproveitado por tests/unit/test_manta_maestro_agent_sdk.py (via
    # `pytest.importorskip`), que roda até na suíte "unit" leve (sem
    # claude-agent-sdk instalado - não faz parte de requirements-test.txt
    # de propósito, é pesado e tem rede/dependências próprias). Por isso
    # aqui é uma Exception normal, não SystemExit: SystemExit é uma
    # BaseException e escapa do collection error handling do pytest,
    # derrubando a sessão inteira (INTERNALERROR) em vez de só este módulo.
    raise ImportError(
        "claude-agent-sdk não instalado. Rode: pip install claude-agent-sdk"
    ) from exc

# Tools seguras por padrão para o orquestrador de topo (routing completo do
# CLAUDE.md, sem --agent). Bash fica de fora até --allow-bash ser passado,
# porque os guardiões (dedup-guard/consist-guard) o exigem para rodar seus
# scripts .py, mas o orquestrador de topo não precisa dele para só rotear.
DEFAULT_READ_ONLY_TOOLS = ["Read", "Grep", "Glob", "WebSearch", "WebFetch"]

_MCP_JSON_NOTE = """
NOTA — .mcp.json deste repositório:
  1. Não é JSON válido hoje: tem chaves "comment" dentro de arrays
     (ex.: dentro de "deny": [...]), o que quebra a sintaxe JSON.
  2. Mesmo corrigido, o schema usado (enabled/tier/capabilities/
     authentication/rate_limiting por servidor) não é o formato real de
     `.mcp.json` esperado pelo Claude Code / Agent SDK — que é
     {"mcpServers": {"nome": {"command", "args", "env"}}} (stdio) ou
     {"nome": {"type": "http"|"sse", "url", "headers"}}.
  Por isso este script não tenta carregá-lo automaticamente. Use
  --mcp-config apontando para um JSON já no formato real, com os
  servidores (ex. SharePoint_Manta, Supabase) resolvidos via variáveis de
  ambiente reais.
"""


def build_agent_definitions(only: AgentDef | None = None) -> dict[str, AgentDefinition]:
    """Monta o `agents=` do Agent SDK a partir de .claude/agents/*.md.

    Reaproveita tests/lib/agent_loader.py (o mesmo parser usado pelos
    testes do repo) para que o conjunto de agentes aqui nunca divirja do
    que já é validado/lint-checado em outro lugar.
    """
    agent_defs = [only] if only else load_all_agents()
    agents: dict[str, AgentDefinition] = {}
    for agent in agent_defs:
        if not agent.name or not agent.description:
            continue  # frontmatter incompleto - não é um subagente registrável
        kwargs: dict = {"description": agent.description, "prompt": agent.body}
        if agent.tools:
            kwargs["tools"] = agent.tools
        if agent.model_tier:
            kwargs["model"] = agent.model_tier
        agents[agent.name] = AgentDefinition(**kwargs)
    return agents


def load_claude_md() -> str:
    claude_md = REPO_ROOT / "CLAUDE.md"
    return claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""


# Mesma sintaxe ${VAR} / ${VAR:default} já usada (embora quebrada) no
# .mcp.json deste repositório - aqui expandida de verdade pelo próprio
# script, para que um --mcp-config possa ser versionado/compartilhado
# sem segredos reais dentro dele (só os nomes das env vars).
_ENV_VAR_RE = re.compile(r"\$\{([A-Za-z0-9_]+)(?::([^}]*))?\}")


def _expand_env(value):
    if isinstance(value, str):
        def repl(m: re.Match) -> str:
            name, default = m.group(1), m.group(2)
            return os.environ.get(name, default if default is not None else "")

        return _ENV_VAR_RE.sub(repl, value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def load_mcp_config(path: str | None) -> dict:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _expand_env(data.get("mcpServers", data))


def build_options(
    *,
    allow_bash: bool,
    permission_mode: str,
    model: str | None,
    forced_agent: AgentDef | None,
    mcp_config_path: str | None,
) -> ClaudeAgentOptions:
    agents = build_agent_definitions()  # sempre registra todos - permite handoff mesmo com --agent

    if forced_agent is not None:
        # Roda diretamente como o subagente escolhido, pulando o routing
        # do Maestro (equivalente a chamar a Task tool já mirando esse
        # subagent_type).
        system_prompt = {"type": "custom", "prompt": forced_agent.body}
        allowed_tools = list(forced_agent.tools) if forced_agent.tools else list(DEFAULT_READ_ONLY_TOOLS)
        if allow_bash and "Bash" not in allowed_tools:
            allowed_tools.append("Bash")
        effective_model = model or forced_agent.model_tier
    else:
        system_prompt = {
            "type": "preset",
            "preset": "claude_code",
            "append": load_claude_md(),
        }
        allowed_tools = list(DEFAULT_READ_ONLY_TOOLS)
        if allow_bash:
            allowed_tools.append("Bash")
        effective_model = model

    return ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        setting_sources=[],  # ver _MCP_JSON_NOTE - não confiar no .mcp.json quebrado do repo
        system_prompt=system_prompt,
        agents=agents,
        skills="all",
        allowed_tools=allowed_tools,
        permission_mode=permission_mode,
        model=effective_model,
        mcp_servers=load_mcp_config(mcp_config_path),
    )


async def run(prompt: str, options: ClaudeAgentOptions) -> int:
    exit_code = 0
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[tool_use] {block.name}({block.input})", file=sys.stderr)
        elif isinstance(message, ResultMessage):
            print()
            if message.subtype != "success":
                print(f"[result] {message.subtype}: {message.result}", file=sys.stderr)
                exit_code = 1
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("prompt", help="Prompt/pergunta a enviar ao Maestro")
    parser.add_argument(
        "--agent",
        metavar="SLUG",
        help="Roda direto um subagente (ex: agente-saneamento), pulando o routing do CLAUDE.md",
    )
    parser.add_argument("--model", default=None, help="Override de modelo (ex: claude-sonnet-5)")
    parser.add_argument(
        "--permission-mode",
        default="bypassPermissions",
        choices=["default", "acceptEdits", "plan", "bypassPermissions", "dontAsk", "auto"],
        help="Default bypassPermissions - seguro aqui porque o conjunto de tools já é "
        "restrito via allowed_tools/--allow-bash, não por aprovação interativa "
        "(este script roda sem humano no loop).",
    )
    parser.add_argument(
        "--allow-bash",
        action="store_true",
        help="Permite a tool Bash (necessária para os guardiões dedup-guard/consist-guard). "
        "Desligado por padrão.",
    )
    parser.add_argument(
        "--mcp-config",
        metavar="PATH",
        help="JSON no formato real de mcpServers (ver _MCP_JSON_NOTE) - NÃO é .mcp.json deste repo",
    )
    args = parser.parse_args()

    forced_agent: AgentDef | None = None
    if args.agent:
        try:
            forced_agent = load_agent(args.agent)
        except (FileNotFoundError, AgentParseError) as exc:
            parser.error(str(exc))

    options = build_options(
        allow_bash=args.allow_bash,
        permission_mode=args.permission_mode,
        model=args.model,
        forced_agent=forced_agent,
        mcp_config_path=args.mcp_config,
    )
    return asyncio.run(run(args.prompt, options))


if __name__ == "__main__":
    raise SystemExit(main())
