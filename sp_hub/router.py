"""
Aplica `sp_routing_rules` a um `ChangeEntry` e devolve `RoutingDecision`.

Matching:
- `path_pattern`: glob simples com `*` (não recursivo, `**` opcional).
- `file_ext_pattern`: lista CSV de extensões (`.xer,.mpp`) ou `*` para qualquer.
- `name_pattern`: regex Python (compilada com re.IGNORECASE).

Uma rule casa quando TODOS os padrões definidos (não-nulos) casarem. Rules
com `active=FALSE` são ignoradas antes de chegarem aqui.

Ordem determinística: as rules chegam de `db.fetch_active_routing_rules` já
ordenadas por id crescente. A `RoutingDecision.priority` é a maior entre as
rules que casaram; `target_agents` é a união deduplicada; `doc_type` vem da
rule de MAIOR prioridade (empate → primeira). Fallback quando nenhuma rule
casa: usa `classifier.classify` com prioridade média e sem agente destino.
"""

from __future__ import annotations

import re
from typing import Any

from sp_hub.classifier import classify
from sp_hub.models import ChangeEntry, Priority, RoutingDecision, RoutingRule


def parse_rules(rows: list[dict[str, Any]]) -> list[RoutingRule]:
    """Converte rows crus de `sp_routing_rules` em `RoutingRule`."""
    out: list[RoutingRule] = []
    for row in rows:
        priority_raw = str(row.get("priority", "media")).lower()
        try:
            priority = Priority(priority_raw)
        except ValueError:
            priority = Priority.MEDIA
        out.append(
            RoutingRule(
                id=int(row["id"]),
                rule_name=str(row["rule_name"]),
                path_pattern=row.get("path_pattern"),
                file_ext_pattern=row.get("file_ext_pattern"),
                name_pattern=row.get("name_pattern"),
                target_agents=list(row.get("target_agents") or []),
                doc_type=str(row.get("doc_type") or "outros"),
                priority=priority,
                active=bool(row.get("active", True)),
            )
        )
    return out


def route(entry: ChangeEntry, rules: list[RoutingRule]) -> RoutingDecision:
    """Aplica todas as rules ativas ao entry e sintetiza a decisão."""
    matched: list[RoutingRule] = [r for r in rules if r.active and _matches(entry, r)]

    if not matched:
        return RoutingDecision(
            doc=entry,
            target_agents=[],
            doc_type=classify(entry.doc_path, entry.doc_name, entry.file_ext),
            priority=Priority.MEDIA,
            matched_rules=[],
        )

    priority = Priority.coalesce([r.priority for r in matched])
    agents = _dedupe([a for r in matched for a in r.target_agents])

    # doc_type da rule com maior prioridade (empate → primeira/id menor).
    priority_order = {Priority.ALTA: 3, Priority.MEDIA: 2, Priority.BAIXA: 1}
    doc_type_source = min(
        (r for r in matched if r.priority == priority),
        key=lambda r: r.id,
    )

    return RoutingDecision(
        doc=entry,
        target_agents=agents,
        doc_type=doc_type_source.doc_type,
        priority=priority,
        matched_rules=[r.rule_name for r in matched],
    )


def _matches(entry: ChangeEntry, rule: RoutingRule) -> bool:
    if rule.path_pattern and not _glob_match(rule.path_pattern, entry.doc_path):
        return False
    if rule.file_ext_pattern and not _ext_match(rule.file_ext_pattern, entry.normalized_ext):
        return False
    if rule.name_pattern and not re.search(rule.name_pattern, entry.doc_name, re.IGNORECASE):
        return False
    return True


def _glob_match(pattern: str, text: str) -> bool:
    """Glob simples: `*` = qualquer caractere exceto `/`; `**` = qualquer coisa."""
    regex = _compile_glob(pattern)
    return regex.search(text) is not None


_GLOB_CACHE: dict[str, re.Pattern[str]] = {}


def _compile_glob(pattern: str) -> re.Pattern[str]:
    cached = _GLOB_CACHE.get(pattern)
    if cached is not None:
        return cached
    parts: list[str] = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                parts.append(".*")
                i += 2
            else:
                parts.append("[^/]*")
                i += 1
        elif c in ".+()[]{}|^$?\\":
            parts.append(re.escape(c))
            i += 1
        else:
            parts.append(c)
            i += 1
    compiled = re.compile("".join(parts), re.IGNORECASE)
    _GLOB_CACHE[pattern] = compiled
    return compiled


def _ext_match(pattern: str, ext: str) -> bool:
    if pattern == "*":
        return True
    exts = {p.strip().lstrip(".").lower() for p in pattern.split(",") if p.strip()}
    return ext in exts if exts else True


def _dedupe(items: list[str]) -> list[str]:
    """Preserva ordem de primeira aparição."""
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
