"""
Smoke tests — para cada agente vertical, envia 5 perguntas de exemplo
reais à API da Anthropic usando o corpo do agente (.claude/agents/*.md)
como system prompt, e valida:

  1. a resposta chega em menos de SMOKE_TIMEOUT_SECONDS (default 30s);
  2. a resposta não é vazia;
  3. a resposta contém pelo menos um termo de relevância mínima
     (`expect_any` no YAML de perguntas) — checagem de sanidade, não
     de corretude técnica (isso continua sendo QA humano / aluci-guard).

Requer o secret ANTHROPIC_API_KEY. Se ausente (ex: PR de fork sem
acesso a secrets), os testes são SKIPADOS, não falham — a skill
lint/unit continuam sendo o gate obrigatório nesse caso. Ver
docs/TESTING-AGENTS.md para a política de branch protection.

Para adicionar um novo agente: crie
`tests/smoke/queries/<slug-do-agente>.yaml` com 5 entradas
`{prompt, expect_any}` — o teste é descoberto automaticamente via
parametrização, nenhuma outra mudança de código é necessária.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.agent_loader import load_agent, load_all_agents  # noqa: E402

pytestmark = pytest.mark.smoke

SMOKE_DIR = Path(__file__).resolve().parent
QUERIES_DIR = SMOKE_DIR / "queries"
MODEL_MAP = yaml.safe_load((SMOKE_DIR / "model_map.yaml").read_text(encoding="utf-8"))

SMOKE_TIMEOUT_SECONDS = float(os.environ.get("SMOKE_TIMEOUT_SECONDS", "30"))
SMOKE_MAX_TOKENS = int(os.environ.get("SMOKE_MAX_TOKENS", "500"))
API_KEY = os.environ.get("ANTHROPIC_API_KEY")

REQUIRE_SMOKE = os.environ.get("REQUIRE_SMOKE_TESTS", "").lower() in {"1", "true", "yes"}


def _resolve_model(model_tier: str) -> str:
    first_tier = model_tier.split("/")[0].strip()
    try:
        return MODEL_MAP[first_tier]
    except KeyError as exc:
        raise KeyError(
            f"Tier de modelo '{first_tier}' não mapeado em "
            f"tests/smoke/model_map.yaml"
        ) from exc


def _load_cases():
    """Descobre (agente, caso) para todo YAML em tests/smoke/queries/."""
    cases = []
    known_slugs = {a.slug for a in load_all_agents()}
    for yaml_path in sorted(QUERIES_DIR.glob("*.yaml")):
        slug = yaml_path.stem
        if slug not in known_slugs:
            # Arquivo de queries órfão (agente removido) — falha alto e
            # explícito em vez de silenciosamente nunca rodar.
            cases.append(
                pytest.param(
                    slug,
                    None,
                    marks=pytest.mark.xfail(
                        reason=f"tests/smoke/queries/{slug}.yaml não tem "
                        "agente correspondente em .claude/agents/",
                        strict=True,
                    ),
                    id=f"{slug}-orphan-query-file",
                )
            )
            continue
        entries = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or []
        assert len(entries) >= 5, (
            f"tests/smoke/queries/{slug}.yaml precisa ter >= 5 perguntas "
            f"de exemplo (tem {len(entries)})."
        )
        for i, entry in enumerate(entries):
            cases.append(
                pytest.param(slug, entry, id=f"{slug}-q{i + 1}")
            )
    return cases


CASES = _load_cases()


def _skip_or_fail_missing_key():
    if API_KEY:
        return
    if REQUIRE_SMOKE:
        pytest.fail(
            "ANTHROPIC_API_KEY ausente e REQUIRE_SMOKE_TESTS=1 — smoke "
            "tests são obrigatórios neste job/branch."
        )
    pytest.skip(
        "ANTHROPIC_API_KEY não configurado neste contexto (ex: PR de fork "
        "sem acesso a secrets) — smoke tests pulados. O merge continua "
        "bloqueado por lint/unit/rag."
    )


@pytest.mark.timeout(SMOKE_TIMEOUT_SECONDS + 5)
@pytest.mark.parametrize("slug,case", CASES)
def test_agent_answers_example_query_within_timeout(slug, case):
    _skip_or_fail_missing_key()

    import anthropic  # import tardio: só exigido quando o teste roda de fato

    agent = load_agent(slug)
    model = _resolve_model(agent.model_tier)
    client = anthropic.Anthropic(api_key=API_KEY, timeout=SMOKE_TIMEOUT_SECONDS)

    start = time.monotonic()
    response = client.messages.create(
        model=model,
        max_tokens=SMOKE_MAX_TOKENS,
        system=agent.body,
        messages=[{"role": "user", "content": case["prompt"]}],
    )
    elapsed = time.monotonic() - start

    assert elapsed < SMOKE_TIMEOUT_SECONDS, (
        f"{slug}: resposta demorou {elapsed:.1f}s (limite "
        f"{SMOKE_TIMEOUT_SECONDS:.0f}s) para o prompt: {case['prompt']!r}"
    )

    text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()
    assert text, f"{slug}: resposta vazia para o prompt: {case['prompt']!r}"

    expect_any = [term.lower() for term in case.get("expect_any", [])]
    if expect_any:
        text_lower = text.lower()
        assert any(term in text_lower for term in expect_any), (
            f"{slug}: resposta não contém nenhum termo esperado "
            f"{expect_any} para o prompt {case['prompt']!r}.\n"
            f"Resposta (primeiros 500 chars): {text[:500]!r}"
        )
