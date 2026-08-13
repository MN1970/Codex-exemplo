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
import warnings
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
    """
    Carrega todos os agentes válidos em `.claude/agents/`.

    Um único arquivo malformado (frontmatter YAML ausente/inválido) não
    deve derrubar a coleta de testes de TODOS os agentes — historicamente
    isso já aconteceu (ver `list_malformed_agent_files`): um arquivo em
    "Design Phase" sem frontmatter travava até os smoke tests de agentes
    operacionais não relacionados. Arquivos malformados são pulados aqui
    com um warning (visível no resumo do pytest, sem falhar a suíte);
    use `list_malformed_agent_files()` num teste dedicado para reportar
    isso explicitamente sem acoplar ao carregamento em si.
    """
    if not AGENTS_DIR.exists():
        return []
    agents = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        try:
            agents.append(parse_agent_file(path))
        except AgentParseError as exc:
            warnings.warn(f"Pulando agente malformado em load_all_agents(): {exc}", stacklevel=2)
    return agents


def list_malformed_agent_files() -> list[tuple[Path, str]]:
    """
    Retorna `(path, mensagem_de_erro)` para cada arquivo em `.claude/agents/`
    que falha ao parsear. Usado por testes que querem reportar o problema
    explicitamente (ex: "N arquivos sem frontmatter") sem que isso quebre
    a coleta de outros testes que dependem de `load_all_agents()`.
    """
    if not AGENTS_DIR.exists():
        return []
    problems: list[tuple[Path, str]] = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        try:
            parse_agent_file(path)
        except AgentParseError as exc:
            problems.append((path, str(exc)))
    return problems


def load_agent(slug: str) -> AgentDef:
    path = AGENTS_DIR / f"{slug}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agente '{slug}' não encontrado em {AGENTS_DIR}")
    return parse_agent_file(path)
