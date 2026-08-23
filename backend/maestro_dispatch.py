#!/usr/bin/env python3
"""
Manta 00 (Maestro) como endpoint FastAPI via Claude Agent SDK.

Contexto (Etapa 3 do review de arquitetura manta-arquiteto-ia, Proposta 1):
  A Etapa 1 (Diagnóstico) encontrou uma lacuna real, mas mais estreita
  do que parecia à primeira vista: já existe um backend de produção
  real (deploy/Dockerfile, APScheduler — ver scripts/apscheduler_setup.py,
  scripts/background_agent_framework.py), mas ele cobre jobs agendados
  (rotação de secrets, reindexação de RAG, purge de memória) — não o
  caminho "usuário manda um prompt, o Maestro roteia para o agente
  vertical certo e devolve resposta". Esse caminho hoje só existe como
  sessão manual do Claude Code. Este módulo fecha especificamente essa
  lacuna, sem duplicar a infraestrutura de jobs já existente.

Reaproveita os MESMOS agentes já versionados em `.claude/agents/*.md`
via `backend/agent_registry.py` (o mesmo parser usado pelos testes de
schema) — a definição do agente não muda, só onde ela roda. Aplica
tiering por agente a partir de `.claude/settings.json`
(`model_defaults.tier_horizontal`/`tier_vertical`), e o guardrail
determinístico aluci-guard (`.claude/hooks/pretooluse_aluci_guard.py`)
como PreToolUse hook do Claude Agent SDK.

Limitações conhecidas, documentadas em vez de escondidas:
  - `maestro.v5.0.md` (o próprio router) não tem frontmatter YAML — não
    dá para montar um `AgentDefinition` a partir dele com o parser
    padrão. Este módulo usa o corpo bruto do arquivo como system prompt
    do orquestrador (sem tools/model do frontmatter, que não existem
    aqui) em vez de fingir que o arquivo segue o padrão dos verticais.
  - Vários arquivos em `.claude/agents/` são documentos de design ainda
    não promovidos a agente (sem frontmatter) — `agent_registry.load_all_agents()`
    já os ignora (com aviso), então eles simplesmente não aparecem como
    subagentes despacháveis, sem quebrar o serviço.
  - `agente-oleo-gas` (S12) e `agente-edificacoes` (S13) TÊM frontmatter
    válido e por isso aparecem em `/maestro/agents` mesmo estando
    marcados "🟠 Proposto — pendente gate MN" no CLAUDE.md. Isto não é
    um bug novo introduzido aqui: é o mesmo estado de hoje (o arquivo
    já existe e já seria carregável numa sessão manual do Claude Code)
    — o "gate" real de fato é a ausência de keyword de roteamento em
    `maestro.v5.0.md` para S12/S13 (confirmado no próprio CLAUDE.md),
    não a inexistência do arquivo. Este módulo preserva esse gate
    como está, em vez de tentar reforçá-lo com um filtro heurístico
    "está operacional?" que seria frágil (ver `skill_version_pin` em
    `.claude/settings.json` — não cobre S1-S4/horizontais, que são
    operacionais sem estar pinados). Se o gate humano MN aprovar
    S12/S13, o passo natural é adicionar as keywords em
    `maestro.v5.0.md` — não mexer neste loader.
  - Requer `pip install claude-agent-sdk fastapi uvicorn` (ver
    requirements.txt) e `ANTHROPIC_API_KEY` no ambiente — não faz parte
    deste módulo simular isso.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.agent_registry import AgentDef, REPO_ROOT, load_all_agents

logger = logging.getLogger("maestro_dispatch")

SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
MAESTRO_ROUTER_PATH = REPO_ROOT / ".claude" / "agents" / "maestro.v5.0.md"

# .claude/settings.json::model_defaults.tier_vertical usa chaves tipo
# "agente_saneamento_s8" (underscore); os arquivos/slugs usam
# "agente-saneamento" (hífen, sem sufixo de segmento). Mapear os dois
# formatos aqui em vez de exigir que um dos dois lados mude.
_TIER_KEY_OVERRIDES = {
    "agente-saneamento": "agente_saneamento_s8",
    "agente-energia": "agente_energia_s9",
    "agente-portos": "agente_portos_s6",
    "agente-aeroportos": "agente_aeroportos_s7",
    "agente-barragens": "agente_barragens_s10",
    "agente-arquiteto-ia": "manta_16_arquiteto_ia",
    "agente-bd": "manta_13_bd",
    "agente-apresentacoes": "manta_14_apresentacoes",
    "agente-advisory": "manta_15_advisory",
    "agente-claims": "manta_01_claims",
    "agente-contratual": "manta_02_contratual",
    "agente-imobiliario": "manta_04_imobiliario",
    "agente-orcamento": "manta_05_orcamento",
    "agente-modelagem": "manta_06_modelagem",
    "agente-cronograma": "manta_07_cronograma",
}


def load_settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        return {}
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def resolve_model_for_agent(slug: str, settings: dict[str, Any]) -> str:
    """Aplica o tiering de `.claude/settings.json::model_defaults`.

    Cai para o `model:` do frontmatter do agente se não achar entrada
    de tiering, e para `default_model` se nem isso existir — nunca
    inventa um model ID novo.
    """
    tier_key = _TIER_KEY_OVERRIDES.get(slug, slug.replace("-", "_"))
    model_defaults = settings.get("model_defaults", {})
    for bucket in ("tier_horizontal", "tier_vertical"):
        model_id = model_defaults.get(bucket, {}).get(tier_key)
        if model_id:
            return model_id
    return model_defaults.get("default_model", "claude-sonnet-5-20250701")


def build_agent_definitions(
    agents: list[AgentDef], settings: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Monta o dict `agents=` esperado por `ClaudeAgentOptions`.

    Retorna dicts simples (não `AgentDefinition` do SDK) para manter
    este módulo testável sem o pacote `claude_agent_sdk` instalado —
    `_to_sdk_agent_definitions()` faz a conversão final.
    """
    definitions = {}
    for agent in agents:
        if not agent.description or not agent.tools:
            logger.warning(
                "Pulando %s no dispatch: frontmatter incompleto (description/tools)",
                agent.slug,
            )
            continue
        definitions[agent.slug] = {
            "description": agent.description,
            "prompt": agent.body,
            "tools": agent.tools,
            "model": resolve_model_for_agent(agent.slug, settings),
        }
    return definitions


def load_router_system_prompt() -> str:
    """Corpo de `maestro.v5.0.md`, sem esperar frontmatter (ver docstring
    do módulo — o router não segue o padrão de frontmatter dos verticais)."""
    if not MAESTRO_ROUTER_PATH.exists():
        raise FileNotFoundError(
            f"Router do Maestro não encontrado em {MAESTRO_ROUTER_PATH}"
        )
    return MAESTRO_ROUTER_PATH.read_text(encoding="utf-8").strip()


def _to_sdk_agent_definitions(definitions: dict[str, dict[str, Any]]):
    from claude_agent_sdk import AgentDefinition

    return {
        slug: AgentDefinition(
            description=spec["description"],
            prompt=spec["prompt"],
            tools=spec["tools"],
            model=spec["model"],
        )
        for slug, spec in definitions.items()
    }


async def aluci_guard_pre_tool_use_hook(input_data, tool_use_id, context):
    """Adapta `.claude/hooks/pretooluse_aluci_guard.py::on_pre_tool_use`
    para o formato de hook do Claude Agent SDK (decision block/allow)."""
    import sys

    sys.path.insert(0, str(REPO_ROOT / ".claude" / "hooks"))
    from pretooluse_aluci_guard import on_pre_tool_use

    result = on_pre_tool_use(input_data)
    if result["decision"] == "block":
        return {"decision": "block", "reason": result["reason"]}
    return {}


def build_claude_agent_options(*, strict_agents: bool = False):
    """Monta `ClaudeAgentOptions` prontas para `query()`.

    Import de `claude_agent_sdk` fica dentro da função (não no topo do
    módulo) para que `build_agent_definitions`/`resolve_model_for_agent`
    continuem testáveis sem o pacote instalado.
    """
    from claude_agent_sdk import ClaudeAgentOptions

    settings = load_settings()
    agents = load_all_agents(strict=strict_agents)
    definitions = build_agent_definitions(agents, settings)

    return ClaudeAgentOptions(
        system_prompt=load_router_system_prompt(),
        agents=_to_sdk_agent_definitions(definitions),
        allowed_tools=["Read", "Grep", "Glob", "WebSearch"],
        hooks={"PreToolUse": [aluci_guard_pre_tool_use_hook]},
        permission_mode="acceptEdits",
        model=resolve_model_for_agent("manta_00_maestro", settings),
    )


app = FastAPI(title="Manta Maestro — Dispatch")


class MaestroRequest(BaseModel):
    prompt: str


@app.get("/maestro/agents")
def list_agents() -> dict[str, list[str]]:
    """Lista os slugs de agente atualmente despacháveis (frontmatter
    válido + description/tools presentes) — útil para depurar routing
    sem precisar de ANTHROPIC_API_KEY."""
    settings = load_settings()
    agents = load_all_agents()
    return {"agents": sorted(build_agent_definitions(agents, settings).keys())}


@app.post("/maestro/dispatch")
async def dispatch(req: MaestroRequest) -> dict[str, Any]:
    try:
        from claude_agent_sdk import query
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "claude_agent_sdk não instalado neste ambiente. "
                "pip install claude-agent-sdk (ver requirements.txt)."
            ),
        ) from exc

    options = build_claude_agent_options()
    messages = []
    async for message in query(prompt=req.prompt, options=options):
        messages.append(message)
    return {"messages": messages}
