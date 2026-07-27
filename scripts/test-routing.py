#!/usr/bin/env python3
"""test-routing.py — Manta Maestro Agent Registry.

Check 3/5 do workflow agent-validation: roda um conjunto fixo de 24
prompts (extraídos de `tests/routing/prompts.md`) contra um router de
referência derivado do próprio CLAUDE.md, e confirma que cada um cai
no agente esperado.

Este repositório não contém o runtime do Maestro (ele vive no repo
operacional) — então este script implementa um router de referência
determinístico que qualquer PR pode auditar:

  1. Extrai as regras `IF menção a kw1|kw2|... → agente-X` do bloco
     ROUTING do CLAUDE.md.
  2. Para os agentes verticais que TÊM arquivo neste repo (S6-S10),
     soma as palavras-chave citadas na própria frase "Roteia quando o
     usuário menciona ..." do front-matter `description:` do agente —
     é a mesma fonte que o Claude Code usa para despacho automático de
     subagents, então é a leitura mais fiel disponível aqui.
  3. Para cada prompt, cada regra ganha 1 ponto por palavra-chave sua
     encontrada (substring, case-insensitive) no prompt. A regra com
     maior pontuação vence; empate é resolvido por uma ordem de
     prioridade explícita (ver PRIORITY abaixo) — a única temos no
     conjunto de 24 é o par S1×S2 (Rodovias é o "guarda-chuva"
     genérico do C3 rodoviário; verticals mais específicas como OAE
     (S2) devem vencer o empate).

Fonte dos 24 prompts (`tests/routing/prompts.md`): os 4 primeiros
itens de cada uma das 6 seções determinísticas — S6, S7, S8, S9, S10 e
"Verificações de não-regressão (S1-S4)". A seção "Casos ambíguos /
desafiadores" é propositalmente excluída: o próprio arquivo documenta
que esses exigem decisão humana (política MN), não asserção
automática.

Uso:
  python3 scripts/test-routing.py [--root .] [--prompts tests/routing/prompts.md] [-v]

Exit code 0 = 24/24 passaram; 1 = pelo menos 1 falhou (lista todos os
casos, passando e falhando, em modo -v).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

N_PROMPTS_PER_SECTION = 4
SECTIONS_IN_ORDER = [
    "S6 — Portos",
    "S7 — Aeroportos",
    "S8 — Saneamento (prioridade AySA)",
    "S9 — Energia (prioridade transmissão)",
    "S10 — Barragens",
    "Verificações de não-regressão (S1-S4 mantidos)",
]

# Empate: dentro do cluster S1-S4, a vertical genérica (S1 Rodovias)
# perde para qualquer uma das mais específicas (S2 OAE, S3 Ferrovia,
# S4 Metrô). Fora desse cluster nenhum empate é esperado nos 24
# prompts fixos; se aparecer um empate novo, ele é reportado como
# ambíguo (nem PASS nem FAIL silencioso).
TIE_BREAK_PRIORITY = [
    "agente-infraestrutura S2",
    "agente-infraestrutura S3",
    "agente-infraestrutura S4",
    "agente-infraestrutura S1",
]


@dataclass
class Rule:
    target: str
    keywords: list


def strip_suffix_paren(target: str) -> str:
    return re.sub(r"\s*\(S\d+\)\s*$", "", target).strip()


def load_routing_rules(claude_md_text: str) -> list:
    m = re.search(r"## ROUTING.*?```\n(?P<body>.*?)```", claude_md_text, re.DOTALL)
    if not m:
        raise RuntimeError("bloco ROUTING não encontrado em CLAUDE.md")
    body = m.group("body")
    rules = []
    for rm in re.finditer(r"IF menção a (?P<keywords>[^\n]+)\n\s*→\s*(?P<target>[^\n]+)", body):
        keywords = [k.strip() for k in rm.group("keywords").split("|") if k.strip()]
        target = strip_suffix_paren(rm.group("target").strip())
        rules.append(Rule(target=target, keywords=keywords))
    return rules


def load_agent_description_keywords(agents_dir: str) -> dict:
    """slug -> extra keywords citados em 'Roteia ... menciona X, Y, Z.'"""
    out = {}
    if not os.path.isdir(agents_dir):
        return out
    for fname in sorted(os.listdir(agents_dir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(agents_dir, fname)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        fm = extract_frontmatter(content)
        if not fm:
            continue
        slug = fm.get("name", fname[:-3])
        description = fm.get("description", "")
        # note: usa lookahead negativo para não parar em pontos decimais
        # dentro de números de lei/norma (ex.: "Lei 12.334").
        dm = re.search(r"[Rr]oteia[^.]*?menciona\s+(?P<list>.+?)\.(?!\d)", description)
        if not dm:
            continue
        keywords = [k.strip() for k in dm.group("list").split(",") if k.strip()]
        out[slug] = keywords
    return out


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
    data = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip()
    return data


def build_rules(root: str) -> list:
    claude_md_path = os.path.join(root, "CLAUDE.md")
    with open(claude_md_path, encoding="utf-8") as f:
        claude_text = f.read()
    rules = load_routing_rules(claude_text)

    extra_by_slug = load_agent_description_keywords(os.path.join(root, ".claude", "agents"))
    for rule in rules:
        extra = extra_by_slug.get(rule.target)
        if extra:
            merged = list(dict.fromkeys(rule.keywords + extra))  # dedupe, preserva ordem
            rule.keywords = merged
    return rules


def contains_keyword(text_lower: str, keyword_lower: str) -> bool:
    """Substring match com fronteira de palavra "manual" (unicode-safe).

    Evita falsos positivos como a keyword 'ANA' (barragens) batendo
    dentro de 'panamax', ou 'estação' (metrô) batendo dentro de
    'subestação' (energia) — ambos são substrings literais mas não
    ocorrências reais da palavra/termo.
    """
    start = 0
    while True:
        idx = text_lower.find(keyword_lower, start)
        if idx == -1:
            return False
        before = text_lower[idx - 1] if idx > 0 else ""
        after_idx = idx + len(keyword_lower)
        after = text_lower[after_idx] if after_idx < len(text_lower) else ""
        if not before.isalpha() and not after.isalpha():
            return True
        start = idx + 1


def route(prompt: str, rules: list) -> tuple:
    """Retorna (target_vencedor_ou_None, scores_dict, ambíguo_bool)."""
    prompt_lower = prompt.lower()
    scores = {}
    for rule in rules:
        hits = [kw for kw in rule.keywords if contains_keyword(prompt_lower, kw.lower())]
        if hits:
            scores[rule.target] = max(scores.get(rule.target, 0), len(hits))
    if not scores:
        return None, scores, False

    best_score = max(scores.values())
    winners = [t for t, s in scores.items() if s == best_score]
    if len(winners) == 1:
        return winners[0], scores, False

    for candidate in TIE_BREAK_PRIORITY:
        if candidate in winners:
            return candidate, scores, False

    # empate não coberto pela tabela de prioridade — reporta como ambíguo
    return None, scores, True


# ---------------------------------------------------------------------
# parsing de tests/routing/prompts.md
# ---------------------------------------------------------------------

CHECKLIST_RE = re.compile(r"^- \[ \] `(?P<prompt>.+?)` → \*\*(?P<agent>[^*]+)\*\*")


def load_test_cases(prompts_md_path: str) -> list:
    with open(prompts_md_path, encoding="utf-8") as f:
        lines = f.readlines()

    sections = {}
    current = None
    for line in lines:
        h = re.match(r"^## (?P<title>.+)$", line.strip())
        if h:
            current = h.group("title").strip()
            sections.setdefault(current, [])
            continue
        m = CHECKLIST_RE.match(line.strip())
        if m and current is not None:
            sections[current].append((m.group("prompt"), m.group("agent").strip()))

    cases = []
    for section in SECTIONS_IN_ORDER:
        entries = sections.get(section, [])
        if len(entries) < N_PROMPTS_PER_SECTION:
            raise RuntimeError(
                f"seção '{section}' tem só {len(entries)} prompt(s), esperado >= {N_PROMPTS_PER_SECTION}"
            )
        for prompt, expected in entries[:N_PROMPTS_PER_SECTION]:
            cases.append((section, prompt, expected))
    return cases


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="raiz do repositório (default: .)")
    parser.add_argument(
        "--prompts",
        default=None,
        help="path do prompts.md (default: <root>/tests/routing/prompts.md)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="lista também os PASS, não só os FAIL")
    args = parser.parse_args()

    prompts_path = args.prompts or os.path.join(args.root, "tests", "routing", "prompts.md")

    try:
        rules = build_rules(args.root)
        cases = load_test_cases(prompts_path)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"ERRO ao preparar o teste: {e}")
        return 1

    results = []
    for section, prompt, expected in cases:
        predicted, scores, ambiguous = route(prompt, rules)
        ok = (predicted == expected) and not ambiguous
        results.append((section, prompt, expected, predicted, scores, ambiguous, ok))

    passed = sum(1 for r in results if r[-1])
    total = len(results)

    print(f"test-routing.py — {total} prompts testados\n")
    for section, prompt, expected, predicted, scores, ambiguous, ok in results:
        if ok and not args.verbose:
            continue
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] ({section}) \"{prompt}\"")
        print(f"       esperado: {expected}   obtido: {predicted!r}{'  [AMBÍGUO]' if ambiguous else ''}")
        if not ok:
            print(f"       scores: {scores}")

    print(f"\n{passed}/{total} passaram.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
