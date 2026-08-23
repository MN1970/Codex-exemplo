#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Hook PreToolUse: aluci-guard determinístico
Bloqueia Write/Edit que citem norma/lei/SICRO com formato implausível
(P3-04 review de arquitetura, manta-arquiteto-ia, Etapa 3 — Proposta 2).

Contexto (por que este hook existe):
  A skill `aluci-guard` (anti-alucinação) e o script de auditoria em
  lote `scripts/ke_aluci_guard_audit.py` dependem do modelo "lembrar"
  de invocá-los antes de fechar um laudo/claim/parecer. Isso é uma
  instrução, não uma garantia. Este hook aplica uma camada
  determinística equivalente à de `.claude/hooks/block-sql-in-skill.sh`
  (que bloqueia SQL via Bash por script, não por instrução) — mas para
  citações de norma/lei/SICRO em conteúdo escrito via Write/Edit.

O que este hook NÃO faz (limitação honesta, documentada):
  Não é uma verificação contra um registro real da ABNT/Diário Oficial/
  DNIT — isso exigiria acesso de rede a uma base autoritativa, que este
  hook não tem (e não deveria ter: hooks de PreToolUse devem ser
  rápidos e determinísticos). É uma checagem heurística de *formato*
  (faixa de dígitos plausível, ano não-futuro, padrão de código
  conhecido) que pega o caso mais grosseiro de citação fabricada — não
  substitui a auditoria de conteúdo feita por `aluci-guard`/
  `ke_aluci_guard_audit.py`, nem revisão humana antes de uso oficial.

Integração esperada em .claude/settings.json:
  {
    "hooks": {
      "pre_tool_use": {
        "steps": [
          ...,
          {
            "step": 4,
            "name": "aluci_guard_check",
            "script": ".claude/hooks/pretooluse_aluci_guard.py",
            "on_violation": "block"
          }
        ]
      }
    }
  }
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Finding:
    citation: str
    reason: str


# NBR reais (ex: NBR 6118, NBR 15575, NBR 7187) usam de 1 a 5 dígitos.
# Mais que isso é format implausível — não existe registro ABNT nessa faixa.
NBR_RE = re.compile(r"\bNBR\s+(\d+)\b", re.IGNORECASE)
NBR_MAX_DIGITS = 5

# Lei BR: "Lei nº 14.026/2020", "Lei 12.334/2010" — ano de 4 dígitos.
LEI_RE = re.compile(
    r"\bLei\s+(?:n[ºo°.]*\s*)?[\d.]{1,7}[/-](\d{4})\b", re.IGNORECASE
)

# Código SICRO (DNIT) é numérico de 5 dígitos (ex: SICRO 74001-1, formato
# XXXXX-Y). Menos de 4 ou mais de 6 dígitos no bloco principal é suspeito.
SICRO_RE = re.compile(r"\bSICRO\s+(\d+)(?:-\d+)?\b", re.IGNORECASE)
SICRO_MIN_DIGITS = 4
SICRO_MAX_DIGITS = 6

CURRENT_YEAR = datetime.now(timezone.utc).year
MIN_PLAUSIBLE_YEAR = 1900


def _check_nbr(text: str) -> list[Finding]:
    findings = []
    for match in NBR_RE.finditer(text):
        digits = match.group(1)
        if len(digits) > NBR_MAX_DIGITS:
            findings.append(
                Finding(
                    citation=match.group(0),
                    reason=(
                        f"NBR com {len(digits)} dígitos (máx. plausível: "
                        f"{NBR_MAX_DIGITS}) — normas ABNT reais não chegam "
                        "nessa faixa numérica."
                    ),
                )
            )
    return findings


def _check_lei(text: str) -> list[Finding]:
    findings = []
    for match in LEI_RE.finditer(text):
        year = int(match.group(1))
        if year > CURRENT_YEAR:
            findings.append(
                Finding(
                    citation=match.group(0),
                    reason=f"Lei com ano futuro ({year} > {CURRENT_YEAR}).",
                )
            )
        elif year < MIN_PLAUSIBLE_YEAR:
            findings.append(
                Finding(
                    citation=match.group(0),
                    reason=f"Lei com ano implausível ({year}).",
                )
            )
    return findings


def _check_sicro(text: str) -> list[Finding]:
    findings = []
    for match in SICRO_RE.finditer(text):
        digits = match.group(1)
        if not (SICRO_MIN_DIGITS <= len(digits) <= SICRO_MAX_DIGITS):
            findings.append(
                Finding(
                    citation=match.group(0),
                    reason=(
                        f"Código SICRO com {len(digits)} dígitos (esperado "
                        f"{SICRO_MIN_DIGITS}-{SICRO_MAX_DIGITS}, formato DNIT)."
                    ),
                )
            )
    return findings


def find_implausible_citations(text: str) -> list[Finding]:
    """Ponto de entrada puro (sem I/O) — reusado pelos testes."""
    return [*_check_nbr(text), *_check_lei(text), *_check_sicro(text)]


def _extract_written_text(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "Write":
        return str(tool_input.get("content", ""))
    if tool_name == "Edit":
        return str(tool_input.get("new_string", ""))
    return ""


def on_pre_tool_use(event: dict[str, Any]) -> dict[str, Any]:
    """
    Hook principal: acionado antes de Write/Edit.

    Args:
        event: {'tool_name': 'Write'|'Edit', 'tool_input': {...}}

    Returns:
        {'decision': 'allow'|'block', 'reason': str | None}
    """
    tool_name = event.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return {"decision": "allow", "reason": None}

    text = _extract_written_text(tool_name, event.get("tool_input", {}) or {})
    findings = find_implausible_citations(text)

    if not findings:
        return {"decision": "allow", "reason": None}

    reasons = "; ".join(f"{f.citation} — {f.reason}" for f in findings)
    return {
        "decision": "block",
        "reason": (
            "aluci-guard (PreToolUse): citação com formato implausível "
            f"detectada — {reasons}. Verifique a fonte antes de gravar, ou "
            "corrija o número/ano se for erro de digitação. Isto é uma "
            "checagem heurística de formato, não substitui a auditoria "
            "completa de `aluci-guard`/`scripts/ke_aluci_guard_audit.py`."
        ),
    }


if __name__ == "__main__":
    mock_event = {
        "tool_name": "Write",
        "tool_input": {
            "file_path": "laudo.md",
            "content": "Conforme a NBR 999999 e a Lei 12.345/2099...",
        },
    }
    result = on_pre_tool_use(mock_event)
    print(result)
