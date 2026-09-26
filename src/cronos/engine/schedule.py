"""Cálculo CPM por datas e calendários (equivalente ao F9 do P6, modo lógica retida).

Regras implementadas (F1):
- Data de status: nada remanescente começa antes dela.
- Concluída: datas reais fixas, fora do cálculo de folga.
- Em andamento: início real fixo; o remanescente começa na data de status e, com
  lógica retida, espera as predecessoras FS/FF ainda não concluídas.
- Ligações FS/SS/FF/SF com lag medido no calendário da predecessora.
- Restrições: SNET, FNET, MSO, MFO (ida); SNLT, FNLT, MSO, MFO (volta).
- Volta a partir do maior término cedo ou do "término exigido" do projeto.
- Folga total = menor entre folga de início e de término, em horas do calendário
  da atividade; crítica quando folga ≤ 0 (padrão do P6).
Não implementado ainda: nivelamento, LOE/resumo de EAP no cálculo, caminho mais longo.
"""
from __future__ import annotations

import random
from collections import defaultdict, deque
from dataclasses import replace
from datetime import datetime

from .model import Atividade, Ligacao, Projeto

EPS = 1e-6


def _ordem(p: Projeto, ids: list[str], preds: dict, succs: dict) -> list[str]:
    grau = {u: len(preds[u]) for u in ids}
    fila = deque(u for u in ids if grau[u] == 0)
    ordem = []
    while fila:
        u = fila.popleft()
        ordem.append(u)
        for l in succs[u]:
            grau[l.succ] -= 1
            if grau[l.succ] == 0:
                fila.append(l.succ)
    if len(ordem) != len(ids):
        presas = [p.atividades[u].codigo for u in ids if grau[u] > 0][:10]
        raise ValueError(f"Laço lógico (loop) no cronograma, envolvendo: {', '.join(presas)}")
    return ordem


def _lag(cal, t: datetime, lag_h: float, como_inicio: bool) -> datetime:
    return t if abs(lag_h) < EPS else cal.soma(t, lag_h, como_inicio=como_inicio)


def calcular(p: Projeto, rest_h: dict[str, float] | None = None) -> dict:
    """Ida e volta. `rest_h` permite trocar durações remanescentes (Monte Carlo)."""
    ids = [u for u, a in p.atividades.items() if a.no_calculo]
    conj = set(ids)
    ligs = [l for l in p.ligacoes if l.pred in conj and l.succ in conj]
    preds, succs = defaultdict(list), defaultdict(list)
    for l in ligs:
        preds[l.succ].append(l)
        succs[l.pred].append(l)
    ordem = _ordem(p, ids, preds, succs)
    dur = {u: (rest_h[u] if rest_h and u in rest_h else p.atividades[u].rest_h) for u in ids}
    dd = p.data_status or p.inicio_plan
    if dd is None:
        datas = [a.inicio_plan for a in p.atividades.values() if a.inicio_plan]
        dd = min(datas) if datas else datetime(2000, 1, 3, 8)

    es: dict[str, datetime] = {}
    ef: dict[str, datetime] = {}
    avisos: list[str] = []

    # ---------------- ida ----------------
    for u in ordem:
        a, cal = p.atividades[u], p.cal(p.atividades[u])
        if a.status == "concluida":
            ini = a.inicio_real or a.fim_real or dd
            es[u], ef[u] = ini, a.fim_real or ini
            continue
        d = dur[u]
        cedo_ini = cal.proximo_inicio(dd)                 # nunca antes da data de status
        cedo_fim = None
        for l in preds[u]:
            pa, pcal = p.atividades[l.pred], p.cal(p.atividades[l.pred])
            if a.status == "em_andamento" and l.tipo in ("SS", "SF"):
                continue                                   # já começou: SS/SF satisfeitas
            if l.tipo == "FS":
                cedo_ini = max(cedo_ini, cal.proximo_inicio(_lag(pcal, ef[l.pred], l.lag_h, True)))
            elif l.tipo == "SS":
                cedo_ini = max(cedo_ini, cal.proximo_inicio(_lag(pcal, es[l.pred], l.lag_h, True)))
            elif l.tipo == "FF":
                alvo = cal.ultimo_fim(_lag(pcal, ef[l.pred], l.lag_h, False))
                cedo_fim = alvo if cedo_fim is None else max(cedo_fim, alvo)
            else:  # SF
                alvo = cal.ultimo_fim(_lag(pcal, es[l.pred], l.lag_h, False))
                cedo_fim = alvo if cedo_fim is None else max(cedo_fim, alvo)
        for r in a.restricoes:
            if not r.data or a.status == "em_andamento":
                continue
            if r.tipo in ("SNET", "MSO"):
                cedo_ini = cal.proximo_inicio(r.data) if r.tipo == "MSO" else max(cedo_ini, cal.proximo_inicio(r.data))
            elif r.tipo in ("FNET", "MFO"):
                alvo = cal.ultimo_fim(r.data)
                cedo_fim = alvo if (r.tipo == "MFO" or cedo_fim is None) else max(cedo_fim, alvo)
        if cedo_fim is not None:
            ini_por_fim = cal.soma(cedo_fim, -d, como_inicio=True) if d > EPS else cedo_fim
            cedo_ini = max(cedo_ini, ini_por_fim)
        if a.tipo == "marco_fim" and d <= EPS:
            fim = cal.ultimo_fim(cedo_ini) if cedo_fim is None else max(cal.ultimo_fim(cedo_ini), cedo_fim)
            es[u] = ef[u] = fim
            continue
        fim = cal.soma(cedo_ini, d) if d > EPS else cedo_ini
        if a.status == "em_andamento":
            es[u] = a.inicio_real or cedo_ini
            ef[u] = fim
        else:
            es[u], ef[u] = cedo_ini, fim

    fim_cedo = max((ef[u] for u in ordem), default=dd)
    fim_proj = p.termino_exigido or fim_cedo

    # ---------------- volta ----------------
    ls: dict[str, datetime] = {}
    lf: dict[str, datetime] = {}
    for u in reversed(ordem):
        a, cal = p.atividades[u], p.cal(p.atividades[u])
        if a.status == "concluida":
            ls[u], lf[u] = es[u], ef[u]
            continue
        d = dur[u]
        tarde_fim = cal.ultimo_fim(fim_proj)
        tarde_ini = None
        for l in succs[u]:
            sa, scal = p.atividades[l.succ], p.cal(p.atividades[l.succ])
            if sa.status == "concluida":
                continue
            pcal = cal
            if l.tipo == "FS":
                tarde_fim = min(tarde_fim, cal.ultimo_fim(_lag(pcal, ls[l.succ], -l.lag_h, False)))
            elif l.tipo == "FF":
                tarde_fim = min(tarde_fim, cal.ultimo_fim(_lag(pcal, lf[l.succ], -l.lag_h, False)))
            elif l.tipo == "SS":
                if sa.status == "em_andamento" or a.status == "em_andamento":
                    continue                               # início já ocorreu: SS não restringe
                alvo = cal.proximo_inicio(_lag(pcal, ls[l.succ], -l.lag_h, True))
                tarde_ini = alvo if tarde_ini is None else min(tarde_ini, alvo)
            else:  # SF
                if a.status == "em_andamento":
                    continue
                alvo = cal.proximo_inicio(_lag(pcal, lf[l.succ], -l.lag_h, True))
                tarde_ini = alvo if tarde_ini is None else min(tarde_ini, alvo)
        for r in a.restricoes:
            if not r.data:
                continue
            if r.tipo in ("FNLT", "MFO"):
                tarde_fim = min(tarde_fim, cal.ultimo_fim(r.data))
            elif r.tipo in ("SNLT", "MSO") and a.status != "em_andamento":
                alvo = cal.proximo_inicio(r.data)
                tarde_ini = alvo if tarde_ini is None else min(tarde_ini, alvo)
        if tarde_ini is not None:
            fim_por_ini = cal.soma(tarde_ini, d) if d > EPS else tarde_ini
            tarde_fim = min(tarde_fim, fim_por_ini)
        lf[u] = tarde_fim
        ls[u] = cal.soma(tarde_fim, -d, como_inicio=True) if d > EPS else tarde_fim
        if a.status == "em_andamento":
            ls[u] = es[u]                                  # início real; vale a folga de término

    folga_h: dict[str, float] = {}
    for u in ordem:
        a = p.atividades[u]
        if a.status == "concluida":
            continue
        cal = p.cal(a)
        f_fim = cal.entre(ef[u], lf[u])
        if a.status == "em_andamento":
            folga_h[u] = f_fim
        else:
            folga_h[u] = min(cal.entre(es[u], ls[u]), f_fim)
    criticas = [u for u in ordem if u in folga_h and folga_h[u] <= EPS]
    if p.termino_exigido and fim_cedo > p.termino_exigido:
        avisos.append(f"Término cedo {fim_cedo:%d/%m/%Y} após o término exigido {p.termino_exigido:%d/%m/%Y}")
    return {"ordem": ordem, "es": es, "ef": ef, "ls": ls, "lf": lf, "folga_h": folga_h,
            "criticas": criticas, "data_status": dd, "termino": fim_cedo, "avisos": avisos,
            "ligacoes": ligs}


def folga_dias(p: Projeto, r: dict, u: str) -> float:
    return r["folga_h"].get(u, 0.0) / p.cal(p.atividades[u]).horas_dia


def monte_carlo(p: Projeto, n: int = 500, otimista: float = 0.9, pessimista: float = 1.3,
                semente: int = 42) -> dict:
    """PERT/MC triangular sobre as durações remanescentes (AACE 57R-09)."""
    rnd = random.Random(semente)
    base = calcular(p)
    ids = [u for u in base["ordem"] if p.atividades[u].status != "concluida"]
    fins, crit = [], defaultdict(int)
    for _ in range(n):
        d = {u: rnd.triangular(p.atividades[u].rest_h * otimista, p.atividades[u].rest_h * pessimista,
                               p.atividades[u].rest_h) for u in ids}
        r = calcular(p, d)
        fins.append(r["termino"])
        for u in r["criticas"]:
            crit[u] += 1
    fins.sort()
    q = lambda x: fins[min(int(x * n), n - 1)]
    top = sorted(((p.atividades[u].codigo, c / n) for u, c in crit.items()), key=lambda kv: -kv[1])[:15]
    return {"n": n, "deterministico": base["termino"], "P10": q(.1), "P50": q(.5), "P80": q(.8),
            "P90": q(.9), "indice_criticidade_top15": dict((k, round(v, 3)) for k, v in top)}


def comparar(a: Projeto, b: Projeto) -> dict:
    """Diferença entre versões, casando pelo código da atividade."""
    ra, rb = calcular(a), calcular(b)
    ca = {x.codigo: x for x in a.atividades.values() if x.no_calculo}
    cb = {x.codigo: x for x in b.atividades.values() if x.no_calculo}
    alteradas = []
    for cod in sorted(set(ca) & set(cb)):
        xa, xb = ca[cod], cb[cod]
        d_ini = (rb["es"][xb.uid] - ra["es"][xa.uid]).total_seconds() / 86400
        d_dur = (xb.rest_h - xa.rest_h) / p_horas(b, xb)
        d_custo = round(xb.custo - xa.custo, 2)
        crit_a, crit_b = xa.uid in ra["criticas"], xb.uid in rb["criticas"]
        if abs(d_ini) > EPS or abs(d_dur) > EPS or abs(d_custo) > 0.005 or crit_a != crit_b:
            alteradas.append({"codigo": cod, "nome": xb.nome, "delta_inicio_dias_corridos": round(d_ini, 1),
                              "delta_duracao_dias_uteis": round(d_dur, 1), "delta_custo": d_custo,
                              "critica_antes": crit_a, "critica_depois": crit_b})
    alteradas.sort(key=lambda r: -abs(r["delta_inicio_dias_corridos"]))
    return {"termino": [ra["termino"], rb["termino"]],
            "delta_termino_dias_corridos": round((rb["termino"] - ra["termino"]).total_seconds() / 86400, 1),
            "custo_total": [round(a.custo_total, 2), round(b.custo_total, 2)],
            "so_na_versao_a": sorted(set(ca) - set(cb)), "so_na_versao_b": sorted(set(cb) - set(ca)),
            "alteradas": alteradas}


def p_horas(p: Projeto, a: Atividade) -> float:
    return p.cal(a).horas_dia


def com_atraso(p: Projeto, uid: str, horas: float) -> Projeto:
    """Cópia rasa do projeto com a duração remanescente de uma atividade aumentada."""
    ativs = dict(p.atividades)
    ativs[uid] = replace(ativs[uid], rest_h=ativs[uid].rest_h + horas)
    return replace(p, atividades=ativs)


__all__ = ["calcular", "folga_dias", "monte_carlo", "comparar", "com_atraso", "Ligacao"]
