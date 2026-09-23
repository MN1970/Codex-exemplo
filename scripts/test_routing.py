#!/usr/bin/env python3
"""
Teste de roteamento do Maestro (camada T1 de docs/PLANO-TESTES-MAESTRO-v1.md).

Lê os prompts de tests/routing/prompts.md e confere o agente primário
escolhido por:
  (a) o router de referência (src/maestro/keyword_router.py) — sempre;
  (b) as palavras-chave do banco (tabela maestro_routing_keywords), quando
      um export JSON for passado em --db-json (lista de objetos com
      agent_slug, keyword, priority). O export não é versionado: o banco
      traz nomes de cliente e o repositório é público (achado P-21).

Regra de match do banco (não documentada no Supabase; reproduzida aqui):
soma das prioridades das palavras-chave presentes no prompt, vence a maior.
Dois modos: "palavra" (fronteira de palavra, sem acento — igual ao router
de referência) e "substring" (ILIKE ingênuo, o que um consumidor SQL
simples faria). A diferença entre os dois mostra o risco de misroteamento
por substring ("ETA" em "projetar", "LT" em "filtrados").

Uso:
  python scripts/test_routing.py [tests/routing/prompts.md] [--db-json F] [--json]
Saída não-zero se o router de referência errar algum caso não marcado
como lacuna conhecida.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.maestro import keyword_router as kr  # noqa: E402

LINE_RE = re.compile(r"^- \[[ x]\] `(?P<prompt>[^`]+)`(?:\s*→\s*\*\*(?P<exp>[^*]+)\*\*)?")
EXPECT_RE = re.compile(r"Esperado:[^*]*\*\*(?P<exp>[^*]+)\*\*")
SECTION_RE = re.compile(r"^##\s+(?P<name>.+)$")
KNOWN_GAP = "(lacuna)"


def parse_prompts(path: Path):
    cases, section, pending = [], "", None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = SECTION_RE.match(line)
        if m:
            section = m.group("name")
            continue
        m = LINE_RE.match(line)
        if m:
            if m.group("exp"):
                cases.append(_case(section, m.group("prompt"), m.group("exp"), raw))
                pending = None
            else:
                pending = m.group("prompt")
            continue
        m = EXPECT_RE.search(line)
        if m and pending:
            cases.append(_case(section, pending, m.group("exp"), raw))
            pending = None
    return cases


def _case(section, prompt, expected, raw):
    exp = expected.strip()
    seg = re.search(r"\bS(\d+)\b", exp)
    slug = exp.split()[0]
    agent_id = None
    if slug == "agente-infraestrutura" and seg:
        agent_id = f"manta-03-s{seg.group(1)}"
    return {
        "section": section,
        "prompt": prompt,
        "expected_slug": slug,
        "expected_agent_id": agent_id,
        "known_gap": KNOWN_GAP in raw,
    }


def db_route(prompt: str, rows, mode: str):
    scores = defaultdict(int)
    norm = kr.normalize(prompt)
    for r in rows:
        kw = r["keyword"]
        if mode == "substring":
            hit = kw.lower() in prompt.lower()
        else:
            hit = bool(kr._pattern(kw).search(norm))
        if hit:
            scores[r["agent_slug"]] += int(r.get("priority") or 0)
    if not scores:
        return None, {}
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return best, dict(scores)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("prompts", nargs="?", default=str(ROOT / "tests/routing/prompts.md"))
    ap.add_argument("--db-json")
    ap.add_argument("--json", action="store_true", help="saída detalhada em JSON")
    args = ap.parse_args(argv)

    cases = parse_prompts(Path(args.prompts))
    rows = json.loads(Path(args.db_json).read_text(encoding="utf-8")) if args.db_json else None

    results, fails = [], 0
    for c in cases:
        r = kr.route(c["prompt"])
        ok_ref = (r.slug == c["expected_slug"]) and (
            c["expected_agent_id"] is None or r.agent_id == c["expected_agent_id"])
        res = dict(c, ref_agent=r.agent_id, ref_slug=r.slug, ref_ok=ok_ref)
        if rows is not None:
            for mode in ("palavra", "substring"):
                best, _ = db_route(c["prompt"], rows, mode)
                res[f"db_{mode}"] = best
                res[f"db_{mode}_ok"] = best == c["expected_slug"]
        if not ok_ref and not c["known_gap"]:
            fails += 1
        results.append(res)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    else:
        for res in results:
            mark = "OK " if res["ref_ok"] else ("GAP" if res["known_gap"] else "ERR")
            line = f"[{mark}] {res['expected_slug']:<22} ref={res['ref_slug'] or res['ref_agent']:<22}"
            if rows is not None:
                line += (f" db(pal)={res['db_palavra'] or '-':<22}"
                         f" db(sub)={res['db_substring'] or '-':<22}")
            print(line + " | " + res["prompt"][:60])
        n = len(results)
        print(f"\nReferência: {sum(r['ref_ok'] for r in results)}/{n} corretos")
        if rows is not None:
            for mode in ("palavra", "substring"):
                print(f"Banco ({mode}): {sum(r[f'db_{mode}_ok'] for r in results)}/{n} corretos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
