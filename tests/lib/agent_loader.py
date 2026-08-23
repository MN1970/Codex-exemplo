"""
Shim de compatibilidade — a implementação real mora em
`backend/agent_registry.py` (promovida de `tests/lib/` para código de
produção na Etapa 3 do review de arquitetura, Proposta 1: backend real
via Claude Agent SDK, que também precisa carregar `.claude/agents/*.md`
em runtime, não só nos testes). Mantido para não quebrar os `import`s
já existentes em `tests/unit/*.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.agent_registry import (  # noqa: E402,F401
    AGENTS_DIR,
    ALLOWED_MODEL_TIERS,
    ALLOWED_TOOLS,
    CLAUDE_MD,
    REPO_ROOT,
    VERSION_SUFFIX_RE,
    AgentDef,
    AgentParseError,
    _slug_from_stem,
    load_agent,
    load_all_agents,
    parse_agent_file,
)
