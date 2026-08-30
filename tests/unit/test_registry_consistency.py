"""
Testes unitários — consistência entre o registro mestre (CLAUDE.md) e os
arquivos reais de agente em `.claude/agents/`.

Este repositório é a fonte canônica versionada dos agentes verticais
(ver README.md). Se alguém adiciona/remove um agente em
`.claude/agents/*.md` sem atualizar a tabela "Eixo 2 — Verticais por
segmento" do CLAUDE.md (ou vice-versa), o Maestro operacional e este
registro divergem silenciosamente — é exatamente o tipo de bug que só
aparece em produção. Estes testes existem para pegar isso no PR.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.agent_loader import CLAUDE_MD, load_all_agents  # noqa: E402

pytestmark = pytest.mark.unit

AGENTS = load_all_agents()

# Casa linhas de tabela markdown tipo:
# | Manta 03-S6 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
TABLE_ROW_RE = re.compile(r"^\|\s*Manta [\w-]+\s*\|.*?\|\s*(agente-[\w-]+)\s*\|", re.MULTILINE)


def _claude_md_text() -> str:
    assert CLAUDE_MD.exists(), f"CLAUDE.md master não encontrado em {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


def test_every_agent_file_is_registered_in_claude_md():
    text = _claude_md_text()
    missing = [a.slug for a in AGENTS if a.slug not in text]
    assert not missing, (
        f"Agente(s) {missing} existem em .claude/agents/ mas não são "
        "mencionados em CLAUDE.md. Atualize a tabela 'Eixo 2 — Verticais "
        "por segmento' (e a árvore de arquivos, se aplicável)."
    )


def test_every_registered_vertical_has_an_agent_file():
    text = _claude_md_text()
    registered_slugs = set(TABLE_ROW_RE.findall(text))
    file_slugs = {a.slug for a in AGENTS}

    # Segmentos cobertos por agentes fora deste repo (ex: S1-S4, S5 parcial
    # coberto por S2/S4) não têm arquivo .md aqui — só cobramos consistência
    # para os slugs "agente-*" que o CLAUDE.md efetivamente referencia.
    dangling = registered_slugs - file_slugs
    assert not dangling, (
        f"CLAUDE.md referencia o(s) agente(s) {sorted(dangling)} na tabela "
        "de verticais, mas não há arquivo correspondente em "
        ".claude/agents/*.md neste repositório."
    )


@pytest.mark.parametrize("agent", AGENTS, ids=[a.slug for a in AGENTS])
def test_agent_segment_code_appears_in_body(agent):
    """
    Cada corpo de agente se autodeclara com seu código de segmento
    (ex: 'Manta 03-S8') no título — checagem barata contra copy-paste
    errado entre agentes (ex: clonar agente-portos.md e esquecer de
    trocar o código do segmento no título).
    """
    title_match = re.search(r"^# .*\((Manta [\w-]+)\)", agent.body, re.MULTILINE)
    assert title_match, (
        f"{agent.path.name}: título do corpo não contém o padrão "
        "'# Agente X (Manta 03-SN)' esperado."
    )
    segment_code = title_match.group(1)
    assert segment_code in agent.description, (
        f"{agent.path.name}: código de segmento '{segment_code}' no título "
        "do corpo não aparece na `description:` do frontmatter — possível "
        "copy-paste entre agentes sem atualizar o segmento."
    )
