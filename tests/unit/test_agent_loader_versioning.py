"""
Testes de regressão — resolução de slug e exclusão de não-agentes em
`backend/agent_registry.py` (via o shim `lib.agent_loader`).

Cobre dois bugs encontrados durante a Etapa 3 do review de arquitetura
(manta-arquiteto-ia), ambos hoje mitigados por camadas complementares:

1. `Path.stem` só remove o `.md` final, então um agente pinado com
   sufixo de versão (`agente-saneamento.v5.0.md`) virava slug
   `"agente-saneamento.v5.0"` em vez de `"agente-saneamento"` —
   quebrando `load_agent()`. PR #88 (branch Motiva, mesclado em `main`
   em 2026-09-01) resolveu isso na raiz renomeando os 5 arquivos
   verticais pinados (removendo o sufixo do nome do arquivo); a
   normalização de slug em `_slug_from_stem`/`load_agent()` continua
   como defesa para qualquer arquivo futuro que volte a usar sufixo de
   versão (ex: `maestro.v5.0.md`, que nunca teve frontmatter e por isso
   nunca dependeu desse caminho).
2. `load_all_agents()` derrubava a coleta inteira ao encontrar qualquer
   `.md` sem frontmatter válido (ex: documentos de design como
   `agente-analytics-p3-07.md`). Mitigado em duas camadas: os 8
   arquivos conhecidos ficam em `EXCLUDED_FROM_REGISTRY` (ignorados
   silenciosamente, com a razão documentada) e qualquer OUTRO arquivo
   malformado ainda não catalogado cai no fallback `try/except` (avisa
   em vez de derrubar a coleta, a menos que `strict=True`).
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.agent_loader import (  # noqa: E402
    AGENTS_DIR,
    EXCLUDED_FROM_REGISTRY,
    _slug_from_stem,
    load_agent,
    load_all_agents,
    parse_agent_file,
)

pytestmark = pytest.mark.unit

# Os 5 agentes verticais que passaram pela Fase 3 (Skill Versioning) do
# go-live v5.0 com arquivo pinado `{slug}.v5.0.md` — desde PR #88
# (2026-09-01) renomeados para `{slug}.md` (sem sufixo). Mantidos aqui
# como regressão: `load_agent(slug)` deve resolvê-los normalmente pelo
# caminho "exact" (não mais pelo caminho "pinned", que só entra em jogo
# se um arquivo `{slug}.vN.N.md` voltar a existir no futuro).
#
# "maestro" fica de fora desta lista: `maestro.v5.0.md` não usa
# frontmatter YAML (é markdown puro desde a origem), então
# `parse_agent_file()` legitimamente não consegue montá-lo em AgentDef.
# Isso é uma lacuna real e pré-existente (não fabricamos frontmatter
# para "consertar" o teste) — ver
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


def test_load_all_agents_skips_excluded_files_silently():
    """Os 8 documentos conhecidos em `EXCLUDED_FROM_REGISTRY` (specs de
    design, docs de skill, o router) são ignorados sem aviso — a razão
    de cada exclusão já está documentada no próprio conjunto, não
    precisa de warning em tempo de execução."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        agents = load_all_agents()

    assert agents, "load_all_agents() não deveria retornar lista vazia"
    assert not any(
        "agente-analytics-p3-07.md" in str(w.message) for w in caught
    )

    loaded_paths = {a.path for a in agents}
    for excluded_name in EXCLUDED_FROM_REGISTRY:
        assert AGENTS_DIR / excluded_name not in loaded_paths


def test_load_all_agents_warns_on_uncatalogued_malformed_file(tmp_path, monkeypatch):
    """Um `.md` malformado que NÃO está em `EXCLUDED_FROM_REGISTRY`
    (ex: um arquivo novo, ainda não catalogado) não deve derrubar a
    coleta — cai no fallback `try/except`, que avisa em vez de
    propagar o erro."""
    (tmp_path / "agente-valido.md").write_text(
        "---\nname: agente-valido\ndescription: x\ntools: [Read]\nmodel: sonnet\n---\ncorpo",
        encoding="utf-8",
    )
    (tmp_path / "documento-novo-sem-frontmatter.md").write_text(
        "# Só um título, sem frontmatter\n", encoding="utf-8"
    )
    monkeypatch.setattr("backend.agent_registry.AGENTS_DIR", tmp_path)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        agents = load_all_agents()

    assert [a.slug for a in agents] == ["agente-valido"]
    assert any(
        "documento-novo-sem-frontmatter.md" in str(w.message) for w in caught
    )


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


def test_load_all_agents_strict_mode_raises(tmp_path, monkeypatch):
    from lib.agent_loader import AgentParseError

    (tmp_path / "documento-novo-sem-frontmatter.md").write_text(
        "# Só um título, sem frontmatter\n", encoding="utf-8"
    )
    monkeypatch.setattr("backend.agent_registry.AGENTS_DIR", tmp_path)

    with pytest.raises(AgentParseError):
        load_all_agents(strict=True)


def test_parse_agent_file_raises_for_missing_frontmatter(tmp_path):
    from lib.agent_loader import AgentParseError

    bad = tmp_path / "sem-frontmatter.md"
    bad.write_text("# Só um título, sem frontmatter\n", encoding="utf-8")

    with pytest.raises(AgentParseError):
        parse_agent_file(bad)


def test_no_duplicate_agent_slugs():
    """Nenhum slug deve aparecer 2x entre os agentes válidos (ex: não
    pode existir `{slug}.md` E `{slug}.v5.0.md` simultaneamente — isso
    tornaria load_agent() ambíguo)."""
    agents = load_all_agents()
    slugs = [a.slug for a in agents]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    assert not dupes, f"Slugs duplicados encontrados: {sorted(dupes)}"
