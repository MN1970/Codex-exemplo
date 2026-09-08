"""
Testes unitários — validação estrutural (schema) dos agentes.

Não fazem nenhuma chamada de rede: rodam em segundos e não exigem
nenhum secret. Garantem que todo arquivo em `.claude/agents/*.md`
está bem formado ANTES de ser publicado como subagente do Claude Code
ou de ser exercitado pelos smoke tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.agent_loader import (  # noqa: E402
    ALLOWED_MODEL_TIERS,
    ALLOWED_TOOLS,
    AGENTS_DIR,
    load_all_agents,
)

pytestmark = pytest.mark.unit

AGENTS = load_all_agents()
AGENT_IDS = [a.slug for a in AGENTS]

REQUIRED_FRONTMATTER_KEYS = {"name", "description", "tools", "model"}
MIN_DESCRIPTION_LEN = 80
REQUIRED_BODY_SECTIONS = (
    "## Contexto de domínio",
    "## Handoff",
)


def test_agents_dir_exists_and_is_not_empty():
    assert AGENTS_DIR.exists(), f"Diretório de agentes não existe: {AGENTS_DIR}"
    assert AGENTS, f"Nenhum agente encontrado em {AGENTS_DIR}/*.md"


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_frontmatter_has_required_keys(agent):
    missing = REQUIRED_FRONTMATTER_KEYS - agent.frontmatter.keys()
    assert not missing, (
        f"{agent.path.name}: frontmatter faltando chave(s) obrigatória(s): "
        f"{sorted(missing)}"
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_name_matches_filename(agent):
    assert agent.name == agent.slug, (
        f"{agent.path.name}: `name:` no frontmatter ('{agent.name}') deve "
        f"ser igual ao nome do arquivo ('{agent.slug}')."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_description_present_and_substantial(agent):
    desc = agent.description or ""
    assert len(desc) >= MIN_DESCRIPTION_LEN, (
        f"{agent.path.name}: `description:` muito curta ({len(desc)} chars, "
        f"mínimo {MIN_DESCRIPTION_LEN}). O Maestro roteia com base nesta "
        "descrição — precisa listar palavras-chave/gatilhos suficientes."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_description_documents_routing_trigger(agent):
    desc = agent.description or ""
    assert "Roteia" in desc or "roteia" in desc, (
        f"{agent.path.name}: description deve declarar explicitamente a "
        "condição de roteamento (ex: 'Roteia quando o usuário menciona...') "
        "para que o Maestro (Manta 00) saiba quando despachar para este agente."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_tools_are_known_and_nonempty(agent):
    assert agent.tools, f"{agent.path.name}: `tools:` não pode ser vazio."
    unknown = set(agent.tools) - ALLOWED_TOOLS
    assert not unknown, (
        f"{agent.path.name}: tool(s) desconhecida(s) {sorted(unknown)}. "
        f"Permitidas: {sorted(ALLOWED_TOOLS)}. Se é uma tool nova e "
        "legítima, adicione em tests/lib/agent_loader.py::ALLOWED_TOOLS."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_model_tier_is_valid(agent):
    tier = agent.model_tier
    # aceita tier único ("sonnet") ou combinações documentadas tipo "sonnet/opus"
    tiers = {t.strip() for t in str(tier).split("/")} if tier else set()
    assert tiers and tiers <= ALLOWED_MODEL_TIERS, (
        f"{agent.path.name}: `model:` inválido ('{tier}'). "
        f"Esperado um de {sorted(ALLOWED_MODEL_TIERS)} (ou combinação com '/')."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_body_has_required_sections(agent):
    missing = [s for s in REQUIRED_BODY_SECTIONS if s not in agent.body]
    assert not missing, (
        f"{agent.path.name}: corpo do agente não contém a(s) seção(ões) "
        f"obrigatória(s) {missing}. Todo agente vertical deve documentar "
        "domínio e handoffs para ser auditável/mantível."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=AGENT_IDS)
def test_body_is_not_a_stub(agent):
    assert len(agent.body) >= 500, (
        f"{agent.path.name}: corpo do system prompt parece um stub "
        f"({len(agent.body)} chars). Agentes verticais da Manta devem "
        "documentar contexto de domínio, ordem de raciocínio e handoffs."
    )
