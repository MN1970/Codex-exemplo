#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MANTA MAESTRO - S2-a  Reconciliacao de taxonomia de agentes
-----------------------------------------------------------
Compara as fontes de verdade que hoje divergem:
  A) BANCO      manta_agent_capabilities.agent_id            (producao)
  B) SKILLS     .claude/skills/*/SKILL.md  (manta_code / tabela do Maestro)
  C) PK         lista canonica v5.0 (arquivo pk_agentes.json)
Saida: tabela de divergencia + exit code 1 se houver conflito (uso em hook/CI).

Uso:
  python3 reconciliacao-agentes.py --db-json banco.json --skills-dir .claude/skills \
      --pk pk_agentes.json [--md relatorio.md]

banco.json = saida de:
  select agent_id, modelo_default, ativo from manta_agent_capabilities;
"""
import argparse, json, os, re, sys
from collections import defaultdict

# Mapa declarado na SKILL.md manta-maestro v4.0.0 (secao 2)
SKILL_MAP_V4 = {
    "02-C": "claims", "02": "contratual", "03-S1": "rodovias", "03-S2": "oae",
    "03-S3": "ferrovia", "03-S4": "metro", "04": "imobiliario", "05": "orcamento",
    "06": "modelagem", "07": "cronograma", "13": "bd", "14": "apresentacoes",
    "15": "advisory",
}

def ler_skills(d):
    """Coleta manta_code declarado no frontmatter de cada SKILL.md."""
    achados = defaultdict(list)
    if not d or not os.path.isdir(d):
        return achados
    for raiz, _, arqs in os.walk(d):
        for a in arqs:
            if a != "SKILL.md":
                continue
            p = os.path.join(raiz, a)
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read(4000)
            except OSError:
                continue
            m = re.search(r'^manta_code:\s*"?([^"\n]+)"?', txt, re.M)
            if m:
                achados[m.group(1).strip()].append(os.path.basename(raiz))
    return achados

def classificar(aid):
    if re.fullmatch(r"03-S\d+", aid):   return "setorial"
    if re.fullmatch(r"M\d+", aid):      return "M-scheme"
    if aid.endswith("-guard") or aid == "context-guardian": return "guard(skill)"
    return "legado"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-json", required=True)
    ap.add_argument("--skills-dir")
    ap.add_argument("--pk")
    ap.add_argument("--md")
    a = ap.parse_args()

    banco = json.load(open(a.db_json, encoding="utf-8"))
    ids_banco = {r["agent_id"] for r in banco}
    pk = set(json.load(open(a.pk, encoding="utf-8"))) if a.pk and os.path.exists(a.pk) else set()
    skills = ler_skills(a.skills_dir)

    fam = defaultdict(list)
    for i in sorted(ids_banco):
        fam[classificar(i)].append(i)

    L = []
    add = L.append
    add("# Reconciliacao de agentes - Manta Maestro\n")
    add(f"- Banco (manta_agent_capabilities): **{len(ids_banco)}** agent_id")
    add(f"- Skills (mapa v4.0.0 da SKILL.md): **{len(SKILL_MAP_V4)}** codigos")
    add(f"- PK v5.0 (pk_agentes.json): **{len(pk) if pk else 'NAO FORNECIDO'}**\n")

    add("## 1. Familias de nomenclatura no banco\n")
    add("| Familia | Qtd | agent_id |")
    add("|---|---|---|")
    for k in ("setorial", "M-scheme", "guard(skill)", "legado"):
        if fam[k]:
            add(f"| {k} | {len(fam[k])} | {', '.join(fam[k])} |")

    add("\n## 2. Divergencias\n")
    so_banco = sorted(ids_banco - set(SKILL_MAP_V4) - pk)
    so_skill = sorted(set(SKILL_MAP_V4) - ids_banco)
    add(f"**No banco, ausentes no mapa das skills ({len(so_banco)}):** {', '.join(so_banco) or '-'}\n")
    add(f"**No mapa das skills, ausentes no banco ({len(so_skill)}):** {', '.join(so_skill) or '-'}\n")
    if pk:
        add(f"**No PK, ausentes no banco:** {', '.join(sorted(pk - ids_banco)) or '-'}\n")
        add(f"**No banco, ausentes no PK:** {', '.join(sorted(ids_banco - pk)) or '-'}\n")

    add("## 3. Colisao de manta_code nas skills\n")
    col = {c: v for c, v in skills.items() if len(set(v)) > 1}
    if col:
        add("| manta_code | reclamado por |")
        add("|---|---|")
        for c, v in sorted(col.items()):
            add(f"| {c} | {', '.join(sorted(set(v)))} |")
    else:
        add("Nenhuma colisao entre skills. Conferir manualmente contra o mapa do Maestro.")
    for c, v in sorted(skills.items()):
        if c in SKILL_MAP_V4 or c.replace("Manta ", "") in SKILL_MAP_V4:
            add(f"\n- ATENCAO: `{c}` usado por skill(s) {sorted(set(v))} e tambem no mapa do Maestro.")

    saida = "\n".join(L)
    if a.md:
        open(a.md, "w", encoding="utf-8").write(saida)
    print(saida)

    conflitos = len(so_banco) + len(so_skill) + len(col)
    print(f"\n[reconciliacao] conflitos={conflitos}")
    sys.exit(1 if conflitos else 0)

if __name__ == "__main__":
    main()
