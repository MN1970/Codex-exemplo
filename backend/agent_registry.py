"""
Utilitário compartilhado para carregar as definições de agente do
Manta Maestro a partir de `.claude/agents/*.md`.

Cada agente é um arquivo Markdown com frontmatter YAML:

    ---
    name: agente-portos
    description: ...
    tools: [Read, Grep, Glob, Bash, WebSearch, WebFetch]
    model: sonnet
    ---

    # corpo do system prompt do agente ...

Este módulo é a fonte única de verdade para o parser — importado tanto
pelo backend de dispatch (`backend/maestro_dispatch.py`, que usa `body`
como system prompt real enviado à API da Anthropic via Claude Agent
SDK) quanto pelos testes unitários (schema/lint) e smoke tests, via o
shim em `tests/lib/agent_loader.py`. Manter um único parser evita
divergência entre o que é validado e o que é de fato executado —
exatamente o motivo pelo qual este módulo foi promovido de
`tests/lib/` (só alcançável por testes) para `backend/` (código de
produção) durante a Etapa 3 do review de arquitetura (Proposta 1:
backend real via Claude Agent SDK).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)

# Alguns agentes promovidos a produção passaram por um período em que
# ganhavam um arquivo "pinado" com sufixo de versão (ex:
# `agente-saneamento.v5.0.md`, ver docs/DEPLOYMENT-GUIDE.md Fase 3 +
# VERSIONS.json) em vez de sobrescrever o arquivo de trabalho. PR #88
# (branch Motiva, mesclado em `main` em 2026-09-01) renomeou os 5
# arquivos verticais pinados para o nome sem sufixo
# (`agente-saneamento.v5.0.md` → `agente-saneamento.md` etc.) — decisão
# do repositório, adotada aqui. `maestro.v5.0.md` segue com o sufixo
# (nunca teve frontmatter, então nunca dependeu do parser abaixo).
# Mantido como defesa: `Path.stem` só remove o `.md` final, então um
# eventual arquivo futuro com sufixo de versão (`.vN.N`) ainda teria o
# slug computado corretamente em vez de vazar o sufixo para
# `load_agent(slug)`/AgentDefinition.
VERSION_SUFFIX_RE = re.compile(r"\.v\d+(?:\.\d+)*$")


def _slug_from_stem(stem: str) -> str:
    return VERSION_SUFFIX_RE.sub("", stem)


# Conjunto de tools reconhecidas pelo Claude Code para subagentes.
# Atualizar aqui se um novo agente precisar de uma tool ainda não usada.
ALLOWED_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob",
    "Bash",
    "WebSearch",
    "WebFetch",
    "NotebookEdit",
    "Task",
}

ALLOWED_MODEL_TIERS = {"haiku", "sonnet", "opus"}

# Arquivos em .claude/agents/*.md que NÃO são subagentes Claude Code
# prontos para validação de registro — excluídos explicitamente em vez
# de forçar frontmatter/seções fabricadas neles (mesma lista adotada em
# `main` PR #88, reconciliada aqui no merge de 2026-09-06):
#
# - Specs "Design Phase" (P3-04/P3-07/P3-08/P3-09, Manta 20/21/25):
#   documentos de proposta em formato de spec longa (seções numeradas,
#   em inglês/EXECUTIVE SUMMARY), ainda não convertidos para o formato
#   operacional conciso (frontmatter + "## Contexto de domínio" +
#   "## Handoff") usado pelos agentes já aprovados.
# - example_background_agent_skill.md: documentação de referência/how-to
#   sobre background agents, não a definição de um agente.
# - sicro-similaridade-skill.md: documentação de uma skill (não de um
#   agente) — o próprio título já diz "SKILL:".
# - maestro.v5.0.md: spec do router Manta 00 em formato de documento de
#   arquitetura, não um subagente Claude Code — não segue o formato de
#   frontmatter usado pelos verticais S1-S13.
#
# Qualquer arquivo NÃO nesta lista que ainda assim não tenha frontmatter
# válido é pego pelo fallback try/except em `load_all_agents()` (com
# aviso), então uma lacuna nesta lista nunca derruba a coleta/o dispatch
# — só deixa de ter a razão documentada acima.
EXCLUDED_FROM_REGISTRY = {
    "agente-analytics-p3-07.md",
    "agente-esg.md",
    "agente-procurement-p3-08.md",
    "manta-21-stakeholder.md",
    "manta-25-kg.md",
    "example_background_agent_skill.md",
    "sicro-similaridade-skill.md",
    "maestro.v5.0.md",
}


@dataclass(frozen=True)
class AgentDef:
    slug: str  # nome canônico sem extensão nem sufixo de versão, ex: "agente-portos"
    path: Path
    frontmatter: dict[str, Any]
    body: str  # system prompt (tudo após o segundo `---`)
    raw: str

    @property
    def name(self) -> str | None:
        return self.frontmatter.get("name")

    @property
    def description(self) -> str | None:
        return self.frontmatter.get("description")

    @property
    def tools(self) -> list[str]:
        return self.frontmatter.get("tools") or []

    @property
    def model_tier(self) -> str | None:
        return self.frontmatter.get("model")


class AgentParseError(ValueError):
    pass


def parse_agent_file(path: Path) -> AgentDef:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise AgentParseError(
            f"{path}: frontmatter YAML ausente ou malformado "
            "(esperado bloco `---\\n...\\n---` no topo do arquivo)."
        )
    fm_text, body = match.groups()
    try:
        frontmatter = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        raise AgentParseError(f"{path}: YAML inválido no frontmatter: {exc}") from exc

    if not isinstance(frontmatter, dict):
        raise AgentParseError(f"{path}: frontmatter deve ser um mapeamento YAML.")

    return AgentDef(
        slug=_slug_from_stem(path.stem),
        path=path,
        frontmatter=frontmatter,
        body=body.strip(),
        raw=raw,
    )


def load_all_agents(*, strict: bool = False) -> list[AgentDef]:
    """Carrega todo `.claude/agents/*.md`.

    Arquivos em `EXCLUDED_FROM_REGISTRY` são pulados silenciosamente
    (documentos conhecidos, não agentes — ver comentário acima do
    conjunto). Qualquer OUTRO arquivo sem frontmatter YAML válido é
    pulado também, mas com aviso (`strict=False`, padrão) — defesa
    contra um futuro arquivo malformado ainda não catalogado derrubar a
    coleta/o dispatch inteiro. Use `strict=True` para propagar o erro
    em vez de avisar (comportamento antigo).
    """
    if not AGENTS_DIR.exists():
        return []

    agents = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        if path.name in EXCLUDED_FROM_REGISTRY:
            continue
        try:
            agents.append(parse_agent_file(path))
        except AgentParseError as exc:
            if strict:
                raise
            import warnings

            warnings.warn(
                f"Ignorando {path.name} em load_all_agents(): {exc}",
                stacklevel=2,
            )
    return agents


def load_agent(slug: str) -> AgentDef:
    """Carrega um agente pelo slug canônico (sem sufixo de versão).

    Resolve tanto `{slug}.md` (arquivo de trabalho) quanto
    `{slug}.vN.N.md` (arquivo pinado de produção) — ver `_slug_from_stem`.
    Se ambos existirem, o arquivo pinado (produção) tem prioridade.
    """
    exact = AGENTS_DIR / f"{slug}.md"
    candidates = [
        p
        for p in AGENTS_DIR.glob(f"{slug}.v*.md")
        if _slug_from_stem(p.stem) == slug
    ]
    pinned = sorted(candidates, reverse=True)

    if pinned:
        return parse_agent_file(pinned[0])
    if exact.exists():
        return parse_agent_file(exact)
    raise FileNotFoundError(f"Agente '{slug}' não encontrado em {AGENTS_DIR}")
