"""
Testes unitários — scripts/manta_maestro_agent_sdk.py

Não fazem nenhuma chamada de rede/API: só validam que o entrypoint do
Claude Agent SDK monta corretamente as `ClaudeAgentOptions` a partir dos
mesmos artefatos reais (.claude/agents/*.md, CLAUDE.md) que os demais
testes do repo já validam.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

# claude-agent-sdk é pesado (mcp, starlette, uvicorn, cryptography...) e
# não faz parte de requirements-test.txt de propósito (lane "unit" fica
# leve/sem rede) - se não estiver instalado, pula este arquivo inteiro em
# vez de quebrar a suíte.
pytest.importorskip("claude_agent_sdk")

import manta_maestro_agent_sdk as sdk_entrypoint  # noqa: E402
from tests.lib.agent_loader import load_agent, load_all_agents  # noqa: E402

pytestmark = pytest.mark.unit


def test_build_agent_definitions_matches_registry():
    agents = sdk_entrypoint.build_agent_definitions()
    registry = {a.name for a in load_all_agents() if a.name}
    assert agents, "build_agent_definitions() não deveria retornar um dict vazio"
    assert set(agents) == registry, (
        "O conjunto de subagentes registrado no Agent SDK divergiu do "
        "registro real (.claude/agents/*.md via tests/lib/agent_loader) - "
        "os dois devem ficar sempre em sincronia."
    )


def test_build_agent_definitions_single_agent():
    forced = load_agent("agente-saneamento")
    agents = sdk_entrypoint.build_agent_definitions(forced)
    assert set(agents) == {"agente-saneamento"}


def test_build_options_default_routing_excludes_bash_by_default():
    options = sdk_entrypoint.build_options(
        allow_bash=False,
        permission_mode="bypassPermissions",
        model=None,
        forced_agent=None,
        mcp_config_path=None,
    )
    assert "Bash" not in options.allowed_tools
    assert set(sdk_entrypoint.DEFAULT_READ_ONLY_TOOLS) <= set(options.allowed_tools)
    assert options.setting_sources == []
    assert options.mcp_servers == {}
    assert options.system_prompt["type"] == "preset"
    assert options.system_prompt["preset"] == "claude_code"
    # CLAUDE.md real precisa estar de fato embutido, não um placeholder
    assert "Manta Maestro" in options.system_prompt["append"]
    assert len(options.agents) == len(load_all_agents())


def test_build_options_allow_bash_adds_bash_tool():
    options = sdk_entrypoint.build_options(
        allow_bash=True,
        permission_mode="bypassPermissions",
        model=None,
        forced_agent=None,
        mcp_config_path=None,
    )
    assert "Bash" in options.allowed_tools


def test_build_options_forced_agent_uses_agent_prompt_and_tools():
    forced = load_agent("agente-saneamento")
    options = sdk_entrypoint.build_options(
        allow_bash=False,
        permission_mode="bypassPermissions",
        model=None,
        forced_agent=forced,
        mcp_config_path=None,
    )
    assert options.system_prompt == {"type": "custom", "prompt": forced.body}
    assert options.allowed_tools == forced.tools
    assert options.model == forced.model_tier
    # mesmo forçando um agente, o registro completo continua disponível
    # para handoff (ex.: agente-saneamento -> agente-barragens)
    assert len(options.agents) == len(load_all_agents())


def test_build_options_model_override_wins_over_forced_agent_model():
    forced = load_agent("agente-saneamento")
    options = sdk_entrypoint.build_options(
        allow_bash=False,
        permission_mode="bypassPermissions",
        model="claude-opus-5",
        forced_agent=forced,
        mcp_config_path=None,
    )
    assert options.model == "claude-opus-5"


def test_load_mcp_config_without_path_is_empty():
    assert sdk_entrypoint.load_mcp_config(None) == {}
