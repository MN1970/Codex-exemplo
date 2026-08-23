"""
Testes unitários — `backend/maestro_dispatch.py`.

Cobrem só as partes puras (montagem de AgentDefinition-like dicts,
resolução de tiering, leitura do system prompt do router) — sem
`claude_agent_sdk` instalado, sem ANTHROPIC_API_KEY, sem rede. O
endpoint FastAPI em si (`/maestro/dispatch`) não é exercitado aqui.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.maestro_dispatch import (  # noqa: E402
    build_agent_definitions,
    load_router_system_prompt,
    load_settings,
    resolve_model_for_agent,
)
from backend.agent_registry import load_all_agents  # noqa: E402

pytestmark = pytest.mark.unit


def test_load_settings_returns_dict_with_model_defaults():
    settings = load_settings()
    assert "model_defaults" in settings
    assert "tier_vertical" in settings["model_defaults"]


@pytest.mark.parametrize(
    "slug,expected_model",
    [
        ("agente-saneamento", "claude-opus-5-20250701"),
        ("agente-energia", "claude-opus-5-20250701"),
        ("agente-portos", "claude-sonnet-5-20250701"),
    ],
)
def test_resolve_model_for_agent_uses_settings_tiering(slug, expected_model):
    settings = load_settings()
    assert resolve_model_for_agent(slug, settings) == expected_model


def test_resolve_model_for_agent_falls_back_to_default_model():
    settings = load_settings()
    model = resolve_model_for_agent("agente-que-nao-existe-no-tiering", settings)
    assert model == settings["model_defaults"]["default_model"]


def test_build_agent_definitions_covers_all_five_pinned_verticals():
    settings = load_settings()
    agents = load_all_agents()
    definitions = build_agent_definitions(agents, settings)

    for slug in (
        "agente-saneamento",
        "agente-energia",
        "agente-portos",
        "agente-aeroportos",
        "agente-barragens",
    ):
        assert slug in definitions, f"{slug} deveria estar despachável"
        assert definitions[slug]["prompt"], f"{slug}: prompt (body) vazio"
        assert definitions[slug]["tools"], f"{slug}: tools vazio"
        assert definitions[slug]["model"]


def test_build_agent_definitions_skips_incomplete_frontmatter(monkeypatch):
    from backend.agent_registry import AgentDef

    incomplete = AgentDef(
        slug="agente-incompleto",
        path=Path("/dev/null"),
        frontmatter={"name": "agente-incompleto"},  # sem description/tools
        body="corpo qualquer",
        raw="",
    )
    settings = load_settings()
    definitions = build_agent_definitions([incomplete], settings)
    assert "agente-incompleto" not in definitions


def test_load_router_system_prompt_reads_maestro_body():
    prompt = load_router_system_prompt()
    assert "MAESTRO" in prompt.upper()
    assert len(prompt) > 200
