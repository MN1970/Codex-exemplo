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

Este módulo é importado tanto pelos testes unitários (schema/lint)
quanto pelos smoke tests (que usam `body` como system prompt real
enviado à API da Anthropic). Manter um único parser evita divergência
entre o que é validado e o que é de fato executado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)

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
# de forçar frontmatter/seções fabricadas neles:
#
# - Specs "Design Phase" (P3-04/P3-07/P3-08/P3-09, Manta 20/21/25):
#   documentos de proposta em formato de spec longa (seções numeradas,
#   em inglês/EXECUTIVE SUMMARY), ainda não convertidos para o formato
#   operacional conciso (frontmatter + "## Contexto de domínio" +
#   "## Handoff com outros agentes") usado pelos agentes já aprovados —
#   inclusive os "propostos, pendente gate MN" como agente-oleo-gas.md/
#   agente-edificacoes.md, que já seguem esse formato apesar de também
#   aguardarem aprovação. Promover estes 5 exige reescrever a spec no
#   formato operacional + passar pelo gate MN, não apenas frontmatter.
# - example_background_agent_skill.md: documentação de referência/how-to
#   sobre background agents, não a definição de um agente.
# - sicro-similaridade-skill.md: documentação de uma skill (não de um
#   agente) — o próprio título já diz "SKILL:".
# - maestro.v5.0.md: spec do router Manta 00 em formato de documento de
#   arquitetura, não um subagente Claude Code — não segue o formato de
#   frontmatter usado pelos spokes S1-S13.
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
    slug: str  # nome do arquivo sem extensão, ex: "agente-portos"
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
        slug=path.stem,
        path=path,
        frontmatter=frontmatter,
        body=body.strip(),
        raw=raw,
    )


def load_all_agents() -> list[AgentDef]:
    if not AGENTS_DIR.exists():
        return []
    return [
        parse_agent_file(p)
        for p in sorted(AGENTS_DIR.glob("*.md"))
        if p.name not in EXCLUDED_FROM_REGISTRY
    ]


def load_agent(slug: str) -> AgentDef:
    path = AGENTS_DIR / f"{slug}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agente '{slug}' não encontrado em {AGENTS_DIR}")
    return parse_agent_file(path)
