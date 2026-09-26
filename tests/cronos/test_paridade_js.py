"""Paridade entre o motor Python (src/cronos/engine) e o motor do navegador (src/cronos/web/cronos-engine.js).

O visualizador do Ask Manta usa o motor JS; este teste garante que ele calcula
exatamente o mesmo que o motor Python em cronogramas sintéticos variados.
"""
import json
import random
import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

from cronos.engine import calcular, dcma14, gravar_xer, ler_xer
from cronos_xer_sintetico import montar_xer, t

pytestmark = pytest.mark.unit
JS = Path(__file__).resolve().parents[2] / "src" / "cronos" / "web" / "cronos-engine.js"

RUNNER = r"""
const E = require(process.argv[2]);
const fs = require('fs');
const txt = fs.readFileSync(process.argv[3], 'latin1');
const p = E.lerXER(txt, 'x.xer')[0];
const r = E.calcular(p);
const f = t => E.fmtXER(t);
const out = {termino: f(r.termino), atividades: {}};
Object.keys(r.es).forEach(u => out.atividades[p.at[u].cod] =
  [f(r.es[u]), f(r.ef[u]), f(r.ls[u]), f(r.lf[u]), r.folgaH[u] === undefined ? null : Math.round(r.folgaH[u] * 1000) / 1000]);
const d = E.dcma14(p, r);
out.dcma = d.pontos.map(x => [x.ponto, x.passou, String(x.valor)]);
out.nota = d.nota;
out.xer_len = E.gravarXER(p, r).length;
process.stdout.write(JSON.stringify(out));
"""


def cenario(semente: int, n: int = 120) -> str:
    rnd = random.Random(semente)
    tarefas, ligs, recs = [], [], []
    for i in range(1, n + 1):
        status, ini, fim, rest = "TK_NotStart", "", "", None
        if i <= n // 6:
            status, ini, fim, rest = "TK_Complete", "2025-01-06 08:00", "2025-01-08 17:00", 0
        elif i <= n // 4:
            status, ini, rest = "TK_Active", "2025-01-09 08:00", rnd.choice([8, 16, 24])
        cstr, cd = "", ""
        if rnd.random() < 0.06:
            cstr = rnd.choice(["CS_MSOA", "CS_MEOB", "CS_MEOA", "CS_MSOB"])
            cd = f"2025-0{rnd.randint(2, 6)}-{rnd.randint(10, 27)} {rnd.choice(['08:00', '17:00'])}"
        tipo = "TT_FinMile" if rnd.random() < 0.05 else "TT_Task"
        dur = 0 if tipo == "TT_FinMile" else rnd.choice([4, 8, 16, 40, 80, 200, 400])
        tarefas.append(t(str(i), f"A{i:04d}", dur, tipo=tipo, status=status, ini=ini, fim=fim, rest=rest,
                         cstr=cstr, cdata=cd, tfim=rnd.choice(["", "2025-02-14 17:00", "2025-01-10 17:00"])))
        if rnd.random() < 0.7:
            recs.append((str(i), rnd.randint(1000, 90000)))
    for i in range(2, n + 1):
        for _ in range(rnd.choice([0, 1, 1, 2])):
            j = rnd.randint(max(1, i - 15), i - 1)
            ligs.append((str(j), str(i), rnd.choice(["PR_FS"] * 6 + ["PR_SS", "PR_FF", "PR_SF"]), "1",
                         rnd.choice([0, 0, 0, 8, 16, -8])))
    return montar_xer(tarefas, ligs, recursos=recs,
                      projetos=(("1", "PARIDADE", "2025-01-13 08:00", rnd.choice(["", "2025-06-30 17:00"]), ""),),
                      feriados=(date(2025, 1, 20), date(2025, 3, 4), date(2025, 4, 18)))


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js não disponível")
@pytest.mark.parametrize("semente", [1, 2, 3, 7, 11])
def test_motor_js_igual_ao_python(tmp_path, semente):
    txt = cenario(semente)
    arq = tmp_path / "x.xer"
    arq.write_bytes(txt.encode("latin-1"))
    runner = tmp_path / "run.js"
    runner.write_text(RUNNER)
    js = json.loads(subprocess.run(["node", str(runner), str(JS), str(arq)], capture_output=True, text=True,
                                   check=True, timeout=60).stdout)

    p = ler_xer(texto=txt, nome="x.xer")[0]
    r = calcular(p)
    fx = lambda d: d.strftime("%Y-%m-%d %H:%M")
    assert js["termino"] == fx(r["termino"])
    for u in r["es"]:
        cod = p.atividades[u].codigo
        fol = r["folga_h"].get(u)
        esperado = [fx(r["es"][u]), fx(r["ef"][u]), fx(r["ls"][u]), fx(r["lf"][u]),
                    None if fol is None else round(fol, 3)]
        assert js["atividades"][cod] == esperado, cod
    d = dcma14(p, r)
    assert [[x[0], x[1]] for x in js["dcma"]] == [[x["ponto"], x["passou"]] for x in d["pontos"]]
    assert js["nota"] == d["nota"]
    assert js["xer_len"] == len(gravar_xer(p, r))
