"""Curva S (física e financeira) e valor agregado — sempre cost-loaded.

- Planejado (linha de base): datas planejadas do XER (target_*); sem elas, usa as
  datas calculadas e marca `linha_de_base_proxy`.
- Previsto: datas calculadas pelo motor (realizado + remanescente).
- Custo e peso físico distribuídos uniformemente nas horas de trabalho de cada
  atividade (calendário da atividade). Peso físico = duração original.
- Valor agregado na data de status: PV, EV, AC, SPI, CPI, EAC, TCPI (ANSI/EIA-748).
"""
from __future__ import annotations

from datetime import datetime

from .model import Projeto
from .schedule import EPS, calcular


def _fracao(cal, ini: datetime, fim: datetime, t: datetime) -> float:
    """Fração do trabalho da atividade concluída até t (0–1)."""
    if t <= ini:
        return 0.0
    if t >= fim:
        return 1.0
    total = cal.entre(ini, fim)
    return 1.0 if total <= EPS else max(0.0, min(1.0, cal.entre(ini, t) / total))


def pct_concluido(a) -> float:
    if a.status == "concluida":
        return 1.0
    if a.status == "nao_iniciada":
        return 0.0
    if a.pct_fisico is not None and a.pct_fisico > 0:
        return max(0.0, min(1.0, a.pct_fisico / 100.0))
    return 0.0 if a.dur_h <= EPS else max(0.0, min(1.0, 1.0 - a.rest_h / a.dur_h))


def _fins_de_mes(t0: datetime, t1: datetime) -> list[datetime]:
    marcos, ano, mes = [], t0.year, t0.month
    while True:
        ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
        m = datetime(ano, mes, 1)
        marcos.append(m)
        if m > t1:
            return marcos


def curva_s(p: Projeto, r: dict | None = None) -> dict:
    r = r or calcular(p)
    ids = r["ordem"]
    base_proxy = any(p.atividades[u].inicio_plan is None or p.atividades[u].fim_plan is None for u in ids)
    plan, prev = {}, {}
    for u in ids:
        a = p.atividades[u]
        plan[u] = ((a.inicio_plan, a.fim_plan) if (a.inicio_plan and a.fim_plan) else (r["es"][u], r["ef"][u]))
        prev[u] = (r["es"][u], r["ef"][u])
    datas = [d for u in ids for d in (*plan[u], *prev[u])]
    if not datas:
        return {"meses": [], "bac": 0.0, "linha_de_base_proxy": base_proxy}
    t0, t1 = min(datas), max(datas)
    bac = sum(p.atividades[u].custo for u in ids)
    peso_total = sum(p.atividades[u].dur_h for u in ids) or 1.0
    meses = []
    for fim in _fins_de_mes(t0, t1):
        cp = cf = fp = ff = 0.0
        for u in ids:
            a, cal = p.atividades[u], p.cal(p.atividades[u])
            fr_p = _fracao(cal, plan[u][0], plan[u][1], fim)
            fr_f = _fracao(cal, prev[u][0], prev[u][1], fim)
            cp += a.custo * fr_p
            cf += a.custo * fr_f
            fp += a.dur_h * fr_p
            ff += a.dur_h * fr_f
        meses.append({"mes": f"{(fim.year if fim.month > 1 else fim.year - 1):04d}-{(fim.month - 1 or 12):02d}",
                      "planejado_custo": round(cp, 2), "previsto_custo": round(cf, 2),
                      "planejado_fisico_pct": round(100 * fp / peso_total, 2),
                      "previsto_fisico_pct": round(100 * ff / peso_total, 2)})
    return {"meses": meses, "bac": round(bac, 2), "linha_de_base_proxy": base_proxy}


def valor_agregado(p: Projeto, r: dict | None = None) -> dict:
    r = r or calcular(p)
    dd = r["data_status"]
    ids = r["ordem"]
    bac = sum(p.atividades[u].custo for u in ids)
    pv = ev = ac = 0.0
    tem_real = False
    for u in ids:
        a, cal = p.atividades[u], p.cal(p.atividades[u])
        ini, fim = ((a.inicio_plan, a.fim_plan) if (a.inicio_plan and a.fim_plan) else (r["es"][u], r["ef"][u]))
        pv += a.custo * _fracao(cal, ini, fim, dd)
        ev += a.custo * pct_concluido(a)
        ac += a.custo_real
        tem_real = tem_real or a.custo_real > EPS
    spi = ev / pv if pv > EPS else None
    cpi = ev / ac if tem_real and ac > EPS else None
    eac = bac / cpi if cpi else None
    tcpi = (bac - ev) / (bac - ac) if tem_real and abs(bac - ac) > EPS else None
    r2 = lambda x: None if x is None else round(x, 2)
    r3 = lambda x: None if x is None else round(x, 3)
    return {"data_status": dd, "BAC": r2(bac), "PV": r2(pv), "EV": r2(ev), "AC": r2(ac) if tem_real else None,
            "SPI": r3(spi), "CPI": r3(cpi), "EAC": r2(eac), "TCPI": r3(tcpi),
            "SV": r2(ev - pv), "CV": r2(ev - ac) if tem_real else None,
            "avisos": [] if tem_real else ["Sem custos reais (act_reg_cost/act_ot_cost) no cronograma: AC, CPI, EAC e TCPI não calculados"]}
