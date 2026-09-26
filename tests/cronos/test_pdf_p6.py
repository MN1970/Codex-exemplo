"""Leitor de relatório do P6 impresso em PDF (motor do navegador).

Os itens de texto imitam o que o pdf.js extrai de um layout do P6: cabeçalho em
duas linhas, faixas de EAP sem ID, nome quebrado em duas linhas, datas reais com
"A", marco sem término e a régua do Gantt à direita (que deve ser ignorada).
Dados fictícios.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
JS = Path(__file__).resolve().parents[2] / "src" / "cronos" / "web" / "cronos-engine.js"

RUNNER = r"""
const E = require(process.argv[2]);
const pags = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));
const p = E.lerRelatorioPDF(pags, 'impactado.pdf')[0];
const r = E.resultadoDasDatas(p);
const f = E.fmtXER;
const at = Object.values(p.at).map(a => [a.cod, a.nome, a.wbs, a.tipo, a.status, a.durH, a.restH, f(a.iniPDF), f(a.fimPDF), a.folgaPDF]);
const cs = E.curvaS(p, r);
const lt = E.linhaDoTempo([p]);
process.stdout.write(JSON.stringify({nome: p.nome, status: f(p.dataStatus), at, eap: p.eap.map(w => w.nome), termino: f(r.termino),
  criticas: r.criticas.map(u => p.at[u].cod), alertas: p.alertas, meses: cs.meses.length, versoes: lt.versoes.length,
  xml: E.gravarMSPDI(p, r).length > 0,
  arvore: E.arvoreEAP(p, r).map(l => [l.k, l.k === 'eap' ? l.nome : p.at[l.u].cod, l.nivel])}));
"""


def it(x, y, s):
    return {"x": x, "y": y, "s": s}


def pagina(y0, linhas):
    """linhas: lista de listas de (x, texto); y decresce 14 por linha."""
    out = []
    for n, cel in enumerate(linhas):
        out += [it(x, y0 - 14 * n, s) for x, s in cel]
    return out


CAB = [it(20, 700, "Activity ID"), it(80, 700, "Activity Name"), it(330, 703, "Remaining"), it(331, 695, "Duration"),
       it(395, 699, "Start"), it(455, 699, "Finish"), it(515, 699, "Total Float"), it(700, 705, "2023"), it(760, 705, "2024")]


def paginas():
    p1 = CAB + [it(20, 740, "Data Date: 30/06/25")] + pagina(680, [
        [(20, "PROJETO PONTE EXEMPLO - ESTUDO"), (330, "1541"), (395, "17/03/23 A"), (455, "17/06/27"), (515, "0")],
        [(80, "COMUM"), (330, "1541"), (395, "17/03/23 A"), (455, "17/06/27")],
        [(20, "A0004"), (80, "Emitir O.S Pacote 02"), (330, "0"), (395, "17/03/23 A"), (515, "0"), (700, "Emitir O.S")],
        [(20, "A10002"), (80, "Mobilizar Pessoal e Equipamentos"), (330, "0"), (395, "17/03/23 A"), (455, "20/06/23 A")],
        [(80, "Pacote 02 | OAEs")],
        [(20, "A0095"), (80, "Desmobilizar Pessoal"), (330, "31"), (395, "18/05/27"), (455, "17/06/27"), (515, "0")],
    ])
    p2 = CAB + pagina(680, [
        [(20, "A2000"), (80, "Estacas apoio 5"), (330, "40"), (395, "02/06/25 A"), (455, "15/09/25"), (515, "12")],
        [(20, "M900"), (80, "Liberação do tráfego"), (330, "0"), (455, "17/06/27"), (515, "0")],
    ])
    return [p1, p2]


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js não disponível")
def test_le_layout_p6_em_pdf(tmp_path):
    arq = tmp_path / "pags.json"
    arq.write_text(json.dumps(paginas()))
    runner = tmp_path / "run.js"
    runner.write_text(RUNNER)
    js = json.loads(subprocess.run(["node", str(runner), str(JS), str(arq)], capture_output=True, text=True,
                                   check=True, timeout=60).stdout)
    at = {a[0]: a for a in js["at"]}
    assert js["nome"] == "PROJETO PONTE EXEMPLO - ESTUDO"
    assert js["status"] == "2025-06-30 08:00"
    assert js["eap"] == ["PROJETO PONTE EXEMPLO - ESTUDO", "COMUM"]
    assert set(at) == {"A0004", "A10002", "A0095", "A2000", "M900"}
    assert at["A0004"][3] == "marco_inicio" and at["A0004"][4] == "concluida"
    assert at["A10002"][1] == "Mobilizar Pessoal e Equipamentos Pacote 02 | OAEs"   # nome em 2 linhas
    assert at["A10002"][4] == "concluida" and at["A10002"][2] == "COMUM"
    assert at["A0095"][5:9] == [248, 248, "2027-05-18 08:00", "2027-06-17 17:00"]
    assert at["A2000"][4] == "em_andamento" and at["A2000"][6] == 320 and at["A2000"][9] == 12
    assert at["M900"][3] == "marco_fim"
    assert js["termino"] == "2027-06-17 17:00"
    assert js["criticas"] == ["A0095", "M900"]           # folga ≤ 0 e não concluídas (o marco A0004 já ocorreu)
    assert any("sem lógica" in a for a in js["alertas"])
    assert js["meses"] > 0 and js["versoes"] == 1 and js["xml"]
    assert js["arvore"] == [["eap", "PROJETO PONTE EXEMPLO - ESTUDO", 0], ["eap", "COMUM", 1], ["atv", "A0004", 2],
                            ["atv", "A10002", 2], ["atv", "A0095", 2], ["atv", "A2000", 2], ["atv", "M900", 2]]


RUNNER_XER = r"""
const E = require(process.argv[2]);
const p = E.lerXER(require('fs').readFileSync(process.argv[3], 'latin1'), 'x.xer')[0];
const r = E.calcular(p);
process.stdout.write(JSON.stringify(E.arvoreEAP(p, r).map(l => [l.k, l.k === 'eap' ? l.nome : p.at[l.u].cod, l.nivel])));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js não disponível")
def test_arvore_eap_do_xer_segue_a_hierarquia(tmp_path):
    from cronos_xer_sintetico import montar_xer, t
    eap = [("W0", "", "0", "Y", "Projeto"), ("W1", "W0", "2", "N", "Obras de arte"),
           ("W2", "W0", "1", "N", "Mobilização"), ("W3", "W1", "1", "N", "Ponte 1")]
    txt = montar_xer([t("1", "A1", 8), t("2", "A2", 8), t("3", "A3", 8)], [("1", "2", "PR_FS", "1", 0)],
                     eap=eap, eap_de={"1": "W2", "2": "W3", "3": "W1"})
    arq = tmp_path / "x.xer"
    arq.write_bytes(txt.encode("latin-1"))
    runner = tmp_path / "run.js"
    runner.write_text(RUNNER_XER)
    arvore = json.loads(subprocess.run(["node", str(runner), str(JS), str(arq)], capture_output=True, text=True,
                                       check=True, timeout=60).stdout)
    assert arvore == [["eap", "Mobilização", 0], ["atv", "A1", 1], ["eap", "Obras de arte", 0], ["atv", "A3", 1],
                      ["eap", "Ponte 1", 1], ["atv", "A2", 2]]
