"""Regressão de roteamento: cada prompt de tests/routing/prompts.md vai ao agente esperado."""

from pathlib import Path

import pytest

from scripts.test_routing import parse_prompts
from src.maestro import keyword_router as kr

PROMPTS = Path(__file__).with_name("prompts.md")
CASES = parse_prompts(PROMPTS)


def test_prompts_parseados():
    assert len(CASES) >= 48


@pytest.mark.unit
@pytest.mark.parametrize("case", CASES, ids=[c["prompt"][:40] for c in CASES])
def test_agente_primario(case):
    r = kr.route(case["prompt"])
    assert r.slug == case["expected_slug"], r.scores
    if case["expected_agent_id"]:
        assert r.agent_id == case["expected_agent_id"]
