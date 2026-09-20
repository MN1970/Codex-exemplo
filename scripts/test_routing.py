#!/usr/bin/env python3
"""
test_routing.py — smoke test for the Manta Maestro (Manta 00) keyword router.

Parses tests/routing/prompts.md, extracts prompt -> expected-agent pairs that
follow the exact format:

    - [ ] `<prompt text>` → **<expected-agent>**

runs each prompt through a deterministic, case-insensitive keyword router
implementing the "ROUTING — Maestro (Manta 00)" rules from CLAUDE.md (in the
exact priority order written there), and reports pass/fail/skip counts.

Lines that don't match the exact format above (non-regression entries with
trailing annotations like "(Rodovias) + handoff **manta-05**", or ambiguous
cases whose expected agent is described in a follow-up "- Esperado: ..."
line rather than inline) are counted separately as skipped/unparsed rather
than causing a crash.

Usage:
    python3 scripts/test_routing.py [path/to/prompts.md]
"""

import re
import sys
from pathlib import Path

DEFAULT_PROMPTS_PATH = Path(__file__).resolve().parent.parent / "tests" / "routing" / "prompts.md"

# ---------------------------------------------------------------------------
# Routing rules, transcribed from CLAUDE.md's "ROUTING — Maestro (Manta 00)"
# section, in the exact top-to-bottom priority order written there.
# Each rule is (target_agent, [keywords...]); a rule matches a prompt if ANY
# of its keywords appears as a case-insensitive substring of the prompt.
# ---------------------------------------------------------------------------
ROUTING_RULES = [
    ("agente-saneamento", [
        "saneamento", "eta", "ete", "adutora", "esgoto", "aysa",
        "drenagem urbana", "snis",
    ]),
    ("agente-energia", [
        "transmissão", "lt", "subestação", "aneel", "rap",
        "leilão transmissão", "ons", "epe",
    ]),
    ("agente-portos", [
        "porto", "terminal", "antaq", "dragagem", "molhe", "berço",
        "calado", "contêiner", "granel",
    ]),
    ("agente-aeroportos", [
        "aeroporto", "pista pouso", "anac", "icao", "tps", "teca",
        "balizamento",
    ]),
    ("agente-barragens", [
        "barragem", "vertedouro", "cfrd", "ccr", "rejeitos", "pnsb",
        "icold", "cbdb", "tsf",
    ]),
    # Regras existentes S1-S4 mantidas sem alteração
    ("agente-infraestrutura S1", [
        "rodovia", "pavimento", "cbuq", "bgs", "terraplenagem", "sicro",
        "dnit",
    ]),
    ("agente-infraestrutura S2", [
        "ponte", "viaduto", "oae", "nbr 7187", "túnel rodoviário",
    ]),
    ("agente-infraestrutura S3", [
        "ferrovia", "trilho", "amv", "dormente", "via permanente",
    ]),
    ("agente-infraestrutura S4", [
        "metrô", "estação", "natm", "psd", "linha 4", "linha 5", "vlt",
    ]),
]

NO_MATCH = "(nenhum agente — sem keyword correspondente)"

# Only lines shaped like "- [ ] `<prompt>` → **<agent>**" (nothing trailing
# after the closing **) are treated as parseable regression test cases.
LINE_RE = re.compile(r"^-\s*\[\s*\]\s*`(?P<prompt>.+?)`\s*→\s*\*\*(?P<agent>[^*]+)\*\*\s*$")

# Any checkbox bullet line at all (used to detect "candidate" lines that
# looked like a test case but didn't match the strict format above).
BULLET_RE = re.compile(r"^-\s*\[\s*\]\s*")


def route(prompt: str) -> str:
    """Deterministic keyword router implementing CLAUDE.md's routing rules."""
    lowered = prompt.lower()
    for agent, keywords in ROUTING_RULES:
        for kw in keywords:
            if kw.lower() in lowered:
                return agent
    return NO_MATCH


def parse_prompts_file(path: Path):
    """Returns (cases, skipped_lines) where cases is a list of
    (prompt, expected_agent, raw_line) and skipped_lines is a list of raw
    bullet lines that could not be parsed into a test case."""
    cases = []
    skipped_lines = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not BULLET_RE.match(line):
            continue  # not a checkbox bullet at all — not a candidate

        match = LINE_RE.match(line)
        if match:
            prompt = match.group("prompt").strip()
            expected_agent = match.group("agent").strip()
            cases.append((prompt, expected_agent, line))
        else:
            skipped_lines.append(line)

    return cases, skipped_lines


def main():
    prompts_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PROMPTS_PATH

    if not prompts_path.exists():
        print(f"ERROR: prompts file not found: {prompts_path}")
        sys.exit(1)

    cases, skipped_lines = parse_prompts_file(prompts_path)

    passed = []
    failed = []

    for prompt, expected_agent, raw_line in cases:
        actual_agent = route(prompt)
        if actual_agent == expected_agent:
            passed.append((prompt, expected_agent, actual_agent))
        else:
            failed.append((prompt, expected_agent, actual_agent))

    total_bullets = len(cases) + len(skipped_lines)

    print("=" * 72)
    print("Manta Maestro — routing smoke test")
    print(f"Source: {prompts_path}")
    print("=" * 72)
    print()
    print(f"Total checkbox bullet lines found : {total_bullets}")
    print(f"Parsed as test cases               : {len(cases)}")
    print(f"Skipped / unparsed (no exact arrow format): {len(skipped_lines)}")
    print()
    print(f"PASSED: {len(passed)}")
    print(f"FAILED: {len(failed)}")
    print()

    if failed:
        print("-" * 72)
        print("FAILURES")
        print("-" * 72)
        for prompt, expected_agent, actual_agent in failed:
            print(f"  Prompt   : {prompt}")
            print(f"  Expected : {expected_agent}")
            print(f"  Actual   : {actual_agent}")
            print()

    if skipped_lines:
        print("-" * 72)
        print("SKIPPED / UNPARSED LINES")
        print("-" * 72)
        for line in skipped_lines:
            print(f"  {line}")
        print()

    print("=" * 72)
    print(
        f"SUMMARY: total={total_bullets} parsed={len(cases)} "
        f"passed={len(passed)} failed={len(failed)} skipped={len(skipped_lines)}"
    )
    print("=" * 72)

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
