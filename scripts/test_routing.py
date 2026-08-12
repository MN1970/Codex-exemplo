#!/usr/bin/env python3
"""Simula o roteamento do Maestro (Manta 00) contra tests/routing/prompts.md.

Compara duas fontes de verdade que hoje divergem no repositorio:

  1. As regras IF da secao ROUTING do CLAUDE.md (o "master rule" que o
     Maestro deveria seguir).
  2. As listas de palavras-chave do campo `description` de cada
     `.claude/agents/*.md` (usadas pelo Claude Code para auto-selecionar
     o subagente).

Para cada prompt do arquivo de teste, aplica as regras na ordem em que
aparecem (semantica IF / ELSE IF) e reporta o primeiro agente cujo
padrao bate. Uso:

    python3 scripts/test_routing.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = ROOT / "CLAUDE.md"
AGENTS_DIR = ROOT / ".claude" / "agents"
PROMPTS_MD = ROOT / "tests" / "routing" / "prompts.md"

# .claude/agents/*.md tem cobertura so para S6-S10; S1-S4 (agente-infraestrutura)
# so existem como regras no CLAUDE.md, entao usamos sempre essa fonte para elas.
NO_AGENT_MD = {"agente-infraestrutura S1", "agente-infraestrutura S2", "agente-infraestrutura S3", "agente-infraestrutura S4"}


def parse_claude_md_rules(text):
    rules = []
    for m in re.finditer(
        r"IF menç[ãa]o a (?P<kw>[^\n]+)\n\s*→\s*(?P<agent>[^\n(]+)(?:\((?P<seg>S\d+)\))?",
        text,
    ):
        kws = [k.strip() for k in m.group("kw").split("|")]
        agent = m.group("agent").strip()
        seg = m.group("seg")
        label = f"{agent} {seg}" if seg else agent
        rules.append((label, kws))
    return rules


def parse_agent_md_rules():
    rules = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        text = path.read_text()
        name_m = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
        if not name_m or not desc_m:
            continue
        name = name_m.group(1)
        desc = desc_m.group(1)
        trig_m = re.search(r"[Rr]oteia (?:automaticamente )?quando o usuário menciona (.+)$", desc)
        if not trig_m:
            continue
        raw = trig_m.group(1).rstrip(".").rstrip()
        # separa por virgula e trata o ultimo item ligado por " ou "
        raw = raw.replace(" ou ", ", ")
        kws = [k.strip() for k in raw.split(",") if k.strip()]
        rules.append((name, kws))
    return rules


def build_ruleset(claude_rules, agent_rules):
    """Substitui, na ordem do CLAUDE.md, as entradas S6-S10 pelas keywords
    mais ricas do .claude/agents/*.md correspondente; mantem S1-S4 como estao."""
    agent_by_slug = {name: kws for name, kws in agent_rules}
    slug_by_segment = {
        "S6": "agente-portos",
        "S7": "agente-aeroportos",
        "S8": "agente-saneamento",
        "S9": "agente-energia",
        "S10": "agente-barragens",
    }
    merged = []
    for label, kws in claude_rules:
        seg_m = re.search(r"\bS(\d+)\b", label)
        seg = f"S{seg_m.group(1)}" if seg_m else None
        slug = slug_by_segment.get(seg)
        if slug and slug in agent_by_slug:
            merged.append((label, agent_by_slug[slug]))
        else:
            merged.append((label, kws))
    return merged


def parse_prompts_md(text):
    cases = []
    section = None
    for line in text.splitlines():
        h = re.match(r"^##\s+(.+)$", line)
        if h:
            section = h.group(1).strip()
            continue
        m = re.match(r"^- \[[ x]\]\s*`(?P<prompt>.+?)`\s*→\s*\*\*(?P<agent>[^*]+)\*\*", line)
        if m and section and "ambíguos" not in section.lower():
            cases.append((section, m.group("prompt"), m.group("agent").strip()))
    return cases


def match(rules, prompt, word_boundary=True):
    low = prompt.lower()
    for label, kws in rules:
        for kw in kws:
            kwl = kw.lower().strip()
            if not kwl:
                continue
            if word_boundary:
                if re.search(r"(?<!\w)" + re.escape(kwl) + r"(?!\w)", low):
                    return label
            elif kwl in low:
                return label
    return None


def normalize(label):
    # normaliza "agente-portos (S6)" vs "agente-portos" vs "agente-infraestrutura S1 (Rodovias)"
    label = re.sub(r"\s*\([^)]*\)\s*", " ", label).strip()
    return label


def run(rules, cases, name, word_boundary=True):
    print(f"\n=== {name} ===")
    passed = 0
    fails = []
    for section, prompt, expected in cases:
        got = match(rules, prompt, word_boundary=word_boundary)
        exp_norm = normalize(expected)
        got_norm = normalize(got) if got else None
        ok = got_norm is not None and (got_norm in exp_norm or exp_norm in got_norm)
        if ok:
            passed += 1
        else:
            fails.append((section, prompt, expected, got))
    total = len(cases)
    print(f"{passed}/{total} passou ({100*passed/total:.1f}%)")
    for section, prompt, expected, got in fails:
        print(f"  FALHA [{section}] '{prompt}'")
        print(f"         esperado={expected!r}  obtido={got!r}")
    return passed, total


def main():
    claude_text = CLAUDE_MD.read_text()
    claude_rules = parse_claude_md_rules(claude_text)
    agent_rules = parse_agent_md_rules()
    merged_rules = build_ruleset(claude_rules, agent_rules)
    cases = parse_prompts_md(PROMPTS_MD.read_text())

    print(f"Regras extraidas do CLAUDE.md: {len(claude_rules)}")
    for label, kws in claude_rules:
        print(f"  - {label}: {kws}")
    print(f"\nCasos de teste (excl. ambiguos): {len(cases)}")

    run(claude_rules, cases, "CLAUDE.md ROUTING, substring cru (ex.: SQL ILIKE '%kw%')", word_boundary=False)
    run(claude_rules, cases, "CLAUDE.md ROUTING, match com borda de palavra (regex \\b)", word_boundary=True)
    run(merged_rules, cases, "CLAUDE.md ROUTING + keywords .claude/agents/*.md, borda de palavra", word_boundary=True)


if __name__ == "__main__":
    sys.exit(main())
