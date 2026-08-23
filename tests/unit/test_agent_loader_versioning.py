"""
Testes de regressão — resolução de slug para agentes "pinados" em
produção (sufixo `.vN.N.md`, ver docs/DEPLOYMENT-GUIDE.md Fase 3).

Cobre o bug encontrado durante a Etapa 3 do review de arquitetura
(manta-arquiteto-ia): `Path.stem` só remove o `.md` final, então
`agente-saneamento.v5.0.md` virava slug `"agente-saneamento.v5.0"` em
vez de `"agente-saneamento"` — quebrando `load_agent()` para todo
agente pinado e (antes do fix em `agent_loader.load_all_agents`)
derrubando a coleta inteira dos testes ao encontrar qualquer `.md` sem
frontmatter válido (ex: documentos de design como
`agente-analytics-p3-07.md`).
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.agent_loader import (  # noqa: E402
    AGENTS_DIR,
    _slug_from_stem,
    load_agent,
    load_all_agents,
)

pytestmark = pytest.mark.unit

# Os 6 agentes que passaram pela Fase 3 (Skill Versioning) do go-live
# v5.0 e por isso têm arquivo pinado `{slug}.v5.0.md` em vez de
# `{slug}.md` (ver VERSIONS.json e .claude/settings.json::skill_version_pin).
#
# "maestro" fica de fora desta lista: `maestro.v5.0.md` — diferente dos
# outros 5 — não usa frontmatter YAML (é markdown puro desde a origem),
# então `parse_agent_file()` legitimamente não consegue montá-lo em
# AgentDef. Isso é uma lacuna real e pré-existente (não fabricamos
# frontmatter para "consertar" o teste) — ver
# `test_maestro_pin_still_lacks_frontmatter_known_gap` abaixo e o Registro
# da Etapa 4 do review de arquitetura em CLAUDE.md.
PINNED_SLUGS = [
    "agente-saneamento",
    "agente-energia",
    "agente-portos",
    "agente-aeroportos",
    "agente-barragens",
]


@pytest.mark.parametrize(
    "stem,expected_slug",
    [
        ("agente-saneamento.v5.0", "agente-saneamento"),
        ("maestro.v5.0", "maestro"),
        ("agente-claims", "agente-claims"),  # sem sufixo: inalterado
        ("agente-portos.v5.0", "agente-portos"),
    ],
)
def test_slug_from_stem_strips_version_suffix(stem, expected_slug):
    assert _slug_from_stem(stem) == expected_slug


@pytest.mark.parametrize("slug", PINNED_SLUGS)
def test_load_agent_resolves_pinned_files(slug):
    """`load_agent(slug)` deve achar o arquivo pinado `{slug}.v5.0.md`
    mesmo sem `{slug}.md` existir — sem exigir renomear o arquivo
    pinado (a versão é intencional, não um erro a corrigir)."""
    agent = load_agent(slug)
    assert agent.name == slug
    assert agent.slug == slug


def test_load_agent_raises_for_unknown_slug():
    with pytest.raises(FileNotFoundError):
        load_agent("agente-que-nao-existe")


def test_load_all_agents_skips_malformed_files_with_warning():
    """Um `.md` sem frontmatter (ex: doc de design ainda não promovido
    a agente) não deve derrubar a coleta inteira — só é ignorado, com
    aviso."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        agents = load_all_agents()

    assert agents, "load_all_agents() não deveria retornar lista vazia"
    assert any("Ignorando" in str(w.message) for w in caught)

    loaded_paths = {a.path for a in agents}
    malformed = AGENTS_DIR / "agente-analytics-p3-07.md"
    assert malformed not in loaded_paths


def test_maestro_pin_still_lacks_frontmatter_known_gap():
    """Guarda de regressão para uma lacuna conhecida, não um requisito:
    `maestro.v5.0.md` (Manta 00, router canônico) não tem frontmatter
    YAML, diferente dos 5 verticais pinados junto com ele no mesmo
    go-live v5.0. Isso o deixa fora de `load_agent()`/`load_all_agents()`
    e fora da montagem dinâmica de `AgentDefinition` (backend SDK).

    Se este teste começar a falhar porque `maestro.v5.0.md` passou a ter
    frontmatter válido, é uma boa notícia — ajuste o teste e mova
    "maestro" de volta para `PINNED_SLUGS`."""
    from lib.agent_loader import AgentParseError

    with pytest.raises(AgentParseError):
        load_agent("maestro")


def test_load_all_agents_strict_mode_raises():
    from lib.agent_loader import AgentParseError

    with pytest.raises(AgentParseError):
        load_all_agents(strict=True)


def test_no_duplicate_agent_slugs():
    """Nenhum slug deve aparecer 2x entre os agentes válidos (ex: não
    pode existir `{slug}.md` E `{slug}.v5.0.md` simultaneamente — isso
    tornaria load_agent() ambíguo)."""
    agents = load_all_agents()
    slugs = [a.slug for a in agents]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    assert not dupes, f"Slugs duplicados encontrados: {sorted(dupes)}"
