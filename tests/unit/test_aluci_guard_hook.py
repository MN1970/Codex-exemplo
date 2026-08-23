"""
Testes unitários — hook PreToolUse `pretooluse_aluci_guard.py`.

Sem rede, sem secrets: cobre só a heurística de formato (dígitos/ano
plausíveis), não a auditoria de conteúdo completa (essa é a skill
`aluci-guard` / `scripts/ke_aluci_guard_audit.py`).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude" / "hooks"))
from pretooluse_aluci_guard import (  # noqa: E402
    find_implausible_citations,
    on_pre_tool_use,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "text",
    [
        "Conforme a NBR 6118 e a NBR 15575, o projeto atende...",
        "A Lei 14.026/2020 (marco do saneamento) estabelece metas.",
        "O código SICRO 74001-1 cobre escavação em solo comum.",
        "Texto sem nenhuma citação técnica.",
    ],
)
def test_plausible_citations_pass(text):
    assert find_implausible_citations(text) == []


@pytest.mark.parametrize(
    "text,expected_substring",
    [
        ("Conforme a NBR 999999...", "NBR"),
        ("A Lei 12.345/2099 estabelece...", "ano futuro"),
        ("A Lei 12.345/1500 estabelece...", "implausível"),
        ("O código SICRO 12 cobre...", "SICRO"),
    ],
)
def test_implausible_citations_are_flagged(text, expected_substring):
    findings = find_implausible_citations(text)
    assert findings, f"esperava pelo menos 1 finding para: {text!r}"
    assert any(expected_substring.lower() in f.reason.lower() for f in findings)


def test_on_pre_tool_use_allows_non_write_edit_tools():
    event = {"tool_name": "Bash", "tool_input": {"command": "NBR 999999"}}
    result = on_pre_tool_use(event)
    assert result["decision"] == "allow"


def test_on_pre_tool_use_allows_clean_write():
    event = {
        "tool_name": "Write",
        "tool_input": {"file_path": "x.md", "content": "Conforme a NBR 6118..."},
    }
    result = on_pre_tool_use(event)
    assert result["decision"] == "allow"
    assert result["reason"] is None


def test_on_pre_tool_use_blocks_implausible_write():
    event = {
        "tool_name": "Write",
        "tool_input": {"file_path": "x.md", "content": "Conforme a NBR 999999..."},
    }
    result = on_pre_tool_use(event)
    assert result["decision"] == "block"
    assert "NBR 999999" in result["reason"]


def test_on_pre_tool_use_checks_edit_new_string_not_old_string():
    event = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "x.md",
            "old_string": "Conforme a NBR 999999...",
            "new_string": "Conforme a NBR 6118...",
        },
    }
    result = on_pre_tool_use(event)
    assert result["decision"] == "allow"
