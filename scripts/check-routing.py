#!/usr/bin/env python3
"""check-routing.py — Manta Maestro Agent Registry.

Dois checks do workflow agent-validation vivem neste script,
selecionados pelo subcomando:

  check-routing.py routing-integrity   (check 2/5)
  check-routing.py rag-collision       (check 4/5)

`routing-integrity`
--------------------
Valida a integridade referencial do CLAUDE.md master:
  - Toda linha vertical da tabela "Eixo 2" tem uma regra correspondente
    no bloco ROUTING (exceto S5, marcado como parcial/coberto).
  - Toda regra do bloco ROUTING aponta para um agente que existe na
    tabela Eixo 2 (nenhuma regra órfã).
  - Todo agente vertical "novo" (S6-S10) tem um arquivo
    `.claude/agents/agente-*.md` correspondente, com front-matter
    `name:` batendo com o slug e `description:` citando o código
    Manta 03-S<n> da tabela.
  - As tabelas RAG e SHAREPOINT citam exatamente os mesmos agentes
    novos (nenhum esquecido, nenhum extra).

`rag-collision`
----------------
Valida que não há colisão de identificadores entre a tabela RAG do
CLAUDE.md e as migrations SQL (`supabase/migrations/*.sql`):
  - slugs de coleção duplicados;
  - prefixos de storage duplicados ou um prefixo-de-outro (ex.:
    "por:" vs "porto:" colidiriam na hora de fazer strip do prefixo);
  - drift entre o que o CLAUDE.md documenta e o que a migration
    realmente insere;
  - `agent_slug` duplicado em `sp_agent_routing`;
  - par (agent_slug, keyword) duplicado em `maestro_routing_keywords`;
  - a mesma keyword atribuída a dois agent_slugs diferentes em
    `maestro_routing_keywords` (colisão de routing na origem dos dados
    usados pelo RAG/Maestro).

Uso:
  python3 scripts/check-routing.py routing-integrity [--root .]
  python3 scripts/check-routing.py rag-collision [--root .]

Exit code 0 = passou, 1 = achou problema(s). Sempre imprime a lista
completa de achados antes de sair (não para no primeiro erro).
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


# ---------------------------------------------------------------------
# Parsing helpers — CLAUDE.md
# ---------------------------------------------------------------------

VERTICAL_ROW_RE = re.compile(
    r"^\|\s*Manta 03-S(\d+)\s*\|\s*(?P<segmento>[^|]+?)\s*\|\s*(?P<agente>[^|]+?)\s*\|\s*(?P<status>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)

ROUTING_BLOCK_RE = re.compile(r"## ROUTING.*?```\n(?P<body>.*?)```", re.DOTALL)

ROUTING_RULE_RE = re.compile(
    r"IF menção a (?P<keywords>[^\n]+)\n\s*→\s*(?P<target>[^\n]+)", re.MULTILINE
)

RAG_ROW_RE = re.compile(
    r"^\|\s*(?P<slug>[a-z]+)\s*\|\s*(?P<prefix>[a-z]+:)\s*\|\s*(?P<sources>[^|]+?)\s*\|\s*(?P<status>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)

SP_ROW_RE = re.compile(
    r"^\|\s*(?P<agent>agente-[a-z]+)\s*\|\s*(?P<folder>[^|]+?)\s*\|\s*(?P<pattern>[^|]+?)\s*\|\s*$",
    re.MULTILINE,
)


@dataclass
class VerticalRow:
    segment_num: int
    segmento: str
    agente_raw: str
    status: str


@dataclass
class RoutingRule:
    keywords: list
    target_raw: str
    target_norm: str


def strip_suffix_paren(target: str) -> str:
    """'agente-portos (S6)' -> 'agente-portos'; 'agente-infraestrutura S1' unchanged."""
    return re.sub(r"\s*\(S\d+\)\s*$", "", target).strip()


def parse_verticals(text: str) -> list:
    rows = []
    for m in VERTICAL_ROW_RE.finditer(text):
        rows.append(
            VerticalRow(
                segment_num=int(m.group(1)),
                segmento=m.group("segmento"),
                agente_raw=m.group("agente"),
                status=m.group("status"),
            )
        )
    return rows


def agente_slug_from_table(agente_raw: str) -> str:
    """'agente-portos' -> 'agente-portos'; 'agente-infraestrutura (S1)' -> 'agente-infraestrutura'."""
    return re.sub(r"\s*\(.*\)\s*$", "", agente_raw).strip()


def parse_routing_rules(text: str) -> list:
    m = ROUTING_BLOCK_RE.search(text)
    if not m:
        return []
    body = m.group("body")
    rules = []
    for rm in ROUTING_RULE_RE.finditer(body):
        keywords = [k.strip() for k in rm.group("keywords").split("|") if k.strip()]
        target_raw = rm.group("target").strip()
        rules.append(
            RoutingRule(
                keywords=keywords,
                target_raw=target_raw,
                target_norm=strip_suffix_paren(target_raw),
            )
        )
    return rules


def parse_rag_table(text: str) -> dict:
    out = {}
    for m in RAG_ROW_RE.finditer(text):
        out[m.group("slug")] = m.group("prefix")
    return out


def parse_sp_table(text: str) -> set:
    return {m.group("agent") for m in SP_ROW_RE.finditer(text)}


# ---------------------------------------------------------------------
# Parsing helpers — Supabase migrations
# ---------------------------------------------------------------------

RAG_INSERT_TUPLE_RE = re.compile(
    r"\(\s*'(?P<slug>[a-z][a-z0-9_]*)'\s*,\s*'(?P<name>[^']+)'\s*,\s*'(?P<prefix>[a-z]+:)'\s*,",
)

SP_ROUTING_TUPLE_RE = re.compile(
    r"\(\s*'(?P<agent_slug>agente-[a-z]+)'\s*,\s*'(?P<folder>[^']+)'\s*,",
)

KEYWORD_TUPLE_RE = re.compile(
    r"\(\s*'(?P<agent_slug>agente-[a-z]+)'\s*,\s*'(?P<keyword>[^']+)'\s*,\s*\d+\s*\)",
)


def extract_section(sql: str, table: str) -> str:
    """Return the text between 'INSERT INTO <table>' and the following ';'."""
    m = re.search(rf"INSERT INTO {re.escape(table)}\b.*?VALUES(?P<body>.*?);", sql, re.DOTALL)
    return m.group("body") if m else ""


def load_migrations(root: str) -> list:
    pattern = os.path.join(root, "supabase", "migrations", "*.sql")
    return sorted(glob.glob(pattern))


# ---------------------------------------------------------------------
# routing-integrity
# ---------------------------------------------------------------------

def cmd_routing_integrity(root: str) -> int:
    claude_md_path = os.path.join(root, "CLAUDE.md")
    if not os.path.isfile(claude_md_path):
        print(f"ERRO: {claude_md_path} não encontrado")
        return 1

    with open(claude_md_path, encoding="utf-8") as f:
        text = f.read()

    errors = []
    warnings = []

    verticals = parse_verticals(text)
    if not verticals:
        errors.append("nenhuma linha 'Manta 03-S<n>' encontrada na tabela Eixo 2")

    rules = parse_routing_rules(text)
    if not rules:
        errors.append("bloco ROUTING não encontrado ou vazio (## ROUTING seguido de ```...```)")

    rule_targets = {r.target_norm for r in rules}

    rag_table = parse_rag_table(text)
    sp_agents = parse_sp_table(text)

    # 1. cada vertical (exceto parcial/coberta) tem regra de routing
    for v in verticals:
        if "parcial" in v.status.lower() or "coberto" in v.status.lower():
            continue
        slug = agente_slug_from_table(v.agente_raw)
        # infra S1-S4 tem alvo "agente-infraestrutura S<n>"
        if slug == "agente-infraestrutura":
            expected_target = f"agente-infraestrutura S{v.segment_num}"
        else:
            expected_target = slug
        if expected_target not in rule_targets:
            errors.append(
                f"Manta 03-S{v.segment_num} ({v.segmento}): nenhuma regra ROUTING aponta "
                f"para '{expected_target}'"
            )

    # 2. cada regra de routing aponta para uma vertical existente
    known_targets = set()
    for v in verticals:
        slug = agente_slug_from_table(v.agente_raw)
        if slug == "agente-infraestrutura":
            known_targets.add(f"agente-infraestrutura S{v.segment_num}")
        else:
            known_targets.add(slug)
    for r in rules:
        if r.target_norm not in known_targets:
            errors.append(
                f"regra ROUTING órfã: 'IF menção a {'|'.join(r.keywords)}' aponta para "
                f"'{r.target_norm}', que não existe na tabela Eixo 2"
            )

    # 3. agentes verticais "novos" (com arquivo local esperado) — front-matter
    new_agent_slugs = []
    for v in verticals:
        slug = agente_slug_from_table(v.agente_raw)
        if slug != "agente-infraestrutura":
            new_agent_slugs.append((slug, v.segment_num))

    agents_dir = os.path.join(root, ".claude", "agents")
    for slug, seg_num in new_agent_slugs:
        agent_file = os.path.join(agents_dir, f"{slug}.md")
        if not os.path.isfile(agent_file):
            errors.append(f"{slug}: arquivo {agent_file} não encontrado (referenciado na tabela Eixo 2)")
            continue
        with open(agent_file, encoding="utf-8") as f:
            content = f.read()
        fm = extract_frontmatter(content)
        if fm is None:
            errors.append(f"{slug}.md: front-matter YAML ilegível")
            continue
        if fm.get("name") != slug:
            errors.append(f"{slug}.md: front-matter name='{fm.get('name')}', esperado '{slug}'")
        code_tag = f"Manta 03-S{seg_num}"
        if code_tag not in content:
            errors.append(f"{slug}.md: não menciona '{code_tag}' (código da tabela Eixo 2)")

        # 4. tabelas RAG e SHAREPOINT devem citar o mesmo agente
        if slug not in {f"agente-{s}" for s in rag_table}:
            errors.append(f"{slug}: sem linha correspondente na tabela '## RAG — Coleções em Supabase'")
        if slug not in sp_agents:
            errors.append(f"{slug}: sem linha correspondente na tabela '## SHAREPOINT — Routing rules'")

    # 5. RAG/SHAREPOINT não devem citar agentes que não existem na Eixo 2
    known_new_slugs = {slug for slug, _ in new_agent_slugs}
    for rag_slug in rag_table:
        full = f"agente-{rag_slug}"
        if full not in known_new_slugs:
            warnings.append(f"tabela RAG cita '{rag_slug}' sem linha correspondente na Eixo 2")
    for sp_agent in sp_agents:
        if sp_agent not in known_new_slugs:
            warnings.append(f"tabela SHAREPOINT cita '{sp_agent}' sem linha correspondente na Eixo 2")

    return report("routing-integrity", errors, warnings)


def extract_frontmatter(content: str):
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None
    fm_text = "\n".join(lines[1:end])
    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text)
            return data if isinstance(data, dict) else None
        except yaml.YAMLError:
            return None
    # fallback sem PyYAML: parsing ingênuo "key: value"
    data = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip()
    return data


# ---------------------------------------------------------------------
# rag-collision
# ---------------------------------------------------------------------

def cmd_rag_collision(root: str) -> int:
    claude_md_path = os.path.join(root, "CLAUDE.md")
    errors = []
    warnings = []

    doc_rag = {}
    if os.path.isfile(claude_md_path):
        with open(claude_md_path, encoding="utf-8") as f:
            doc_text = f.read()
        doc_rag = parse_rag_table(doc_text)
    else:
        errors.append(f"{claude_md_path} não encontrado")

    # 1. duplicidade dentro do próprio CLAUDE.md (mesmo prefixo em 2 slugs)
    prefix_to_slugs = {}
    for slug, prefix in doc_rag.items():
        prefix_to_slugs.setdefault(prefix, []).append(slug)
    for prefix, slugs in prefix_to_slugs.items():
        if len(slugs) > 1:
            errors.append(f"CLAUDE.md: prefixo '{prefix}' usado por múltiplas coleções: {slugs}")

    # 2. um prefixo é prefixo-de-outro (colisão de strip/parsing)
    prefixes = list(doc_rag.values())
    for i, p1 in enumerate(prefixes):
        for p2 in prefixes[i + 1:]:
            if p1 != p2 and (p1.startswith(p2) or p2.startswith(p1)):
                errors.append(f"CLAUDE.md: prefixos colidem por prefixo-de-prefixo: '{p1}' vs '{p2}'")

    # 3. migrations SQL
    migrations = load_migrations(root)
    if not migrations:
        warnings.append("nenhuma migration encontrada em supabase/migrations/*.sql")

    sql_rag = {}  # slug -> prefix
    sql_sp_agents = []  # list of agent_slug
    sql_keywords = []  # list of (agent_slug, keyword)

    for path in migrations:
        with open(path, encoding="utf-8") as f:
            sql = f.read()

        rag_body = extract_section(sql, "rag_collections")
        for m in RAG_INSERT_TUPLE_RE.finditer(rag_body):
            slug = m.group("slug")
            prefix = m.group("prefix")
            if slug in sql_rag and sql_rag[slug] != prefix:
                errors.append(
                    f"{os.path.basename(path)}: coleção '{slug}' com prefixos divergentes: "
                    f"'{sql_rag[slug]}' vs '{prefix}'"
                )
            sql_rag[slug] = prefix

        sp_body = extract_section(sql, "sp_agent_routing")
        for m in SP_ROUTING_TUPLE_RE.finditer(sp_body):
            sql_sp_agents.append(m.group("agent_slug"))

        kw_body = extract_section(sql, "maestro_routing_keywords")
        for m in KEYWORD_TUPLE_RE.finditer(kw_body):
            sql_keywords.append((m.group("agent_slug"), m.group("keyword")))

    # 3a. slug/prefix duplicado dentro da(s) migration(s)
    sql_prefix_to_slugs = {}
    for slug, prefix in sql_rag.items():
        sql_prefix_to_slugs.setdefault(prefix, []).append(slug)
    for prefix, slugs in sql_prefix_to_slugs.items():
        if len(slugs) > 1:
            errors.append(f"migrations: prefixo '{prefix}' usado por múltiplas coleções: {slugs}")

    sql_prefixes = list(sql_rag.values())
    for i, p1 in enumerate(sql_prefixes):
        for p2 in sql_prefixes[i + 1:]:
            if p1 != p2 and (p1.startswith(p2) or p2.startswith(p1)):
                errors.append(f"migrations: prefixos colidem por prefixo-de-prefixo: '{p1}' vs '{p2}'")

    # 3b. drift entre CLAUDE.md e migration
    for slug, prefix in doc_rag.items():
        if slug not in sql_rag:
            errors.append(f"CLAUDE.md documenta coleção '{slug}' que não existe em nenhuma migration")
        elif sql_rag[slug] != prefix:
            errors.append(
                f"drift: CLAUDE.md diz '{slug}' -> '{prefix}', migration diz '{slug}' -> '{sql_rag[slug]}'"
            )
    for slug in sql_rag:
        if slug not in doc_rag:
            warnings.append(f"migration insere coleção '{slug}' não documentada no CLAUDE.md")

    # 3c. agent_slug duplicado em sp_agent_routing
    seen = set()
    for agent_slug in sql_sp_agents:
        if agent_slug in seen:
            errors.append(f"sp_agent_routing: agent_slug duplicado '{agent_slug}'")
        seen.add(agent_slug)

    # 3d. par (agent_slug, keyword) duplicado
    seen_pairs = set()
    for pair in sql_keywords:
        if pair in seen_pairs:
            errors.append(f"maestro_routing_keywords: par duplicado {pair}")
        seen_pairs.add(pair)

    # 3e. mesma keyword em agentes diferentes (colisão de routing)
    keyword_to_agents = {}
    for agent_slug, keyword in sql_keywords:
        keyword_to_agents.setdefault(keyword.lower(), set()).add(agent_slug)
    for keyword, agents in keyword_to_agents.items():
        if len(agents) > 1:
            errors.append(f"keyword '{keyword}' atribuída a múltiplos agentes: {sorted(agents)}")

    return report("rag-collision", errors, warnings)


# ---------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------

def report(check_name: str, errors: list, warnings: list) -> int:
    print(f"check-routing.py {check_name}")
    if warnings:
        print(f"\n{len(warnings)} aviso(s):")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print(f"\nFALHOU — {len(errors)} erro(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nOK — nenhum erro encontrado.")
    return 0


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "command",
        choices=["routing-integrity", "rag-collision"],
        help="qual check rodar",
    )
    parser.add_argument("--root", default=".", help="raiz do repositório (default: .)")
    args = parser.parse_args()

    if args.command == "routing-integrity":
        return cmd_routing_integrity(args.root)
    return cmd_rag_collision(args.root)


if __name__ == "__main__":
    sys.exit(main())
