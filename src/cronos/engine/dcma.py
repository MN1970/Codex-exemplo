"""Checagem DCMA-14 (qualidade do cronograma), com as regras do Maestro A5.

Regra A5 (02-atividades/A5-cronograma): nota mínima de 90% dos pontos aplicáveis e
nenhuma reprovação nos pontos bloqueantes 1, 3, 6, 7 e 11.

Universo padrão: atividades não concluídas que entram na rede (exclui LOE e resumo).
Os pontos 11 e 14 usam as datas planejadas do XER (target_*) como aproximação da
linha de base; o resultado indica isso.
"""
from __future__ import annotations

from .model import Projeto
from .schedule import EPS, calcular, com_atraso

BLOQUEANTES = {1, 3, 6, 7, 11}
NOTA_MINIMA = 0.90
DIAS_LIMITE = 44


def _ponto(n, nome, valor, limite, passou, detalhe, aplicavel=True, exemplos=None):
    return {"ponto": n, "nome": nome, "valor": valor, "limite": limite, "passou": passou if aplicavel else None,
            "aplicavel": aplicavel, "detalhe": detalhe, "exemplos": (exemplos or [])[:10]}


def _pct(n: int, total: int) -> float:
    return round(100.0 * n / total, 1) if total else 0.0


def dcma14(p: Projeto, r: dict | None = None) -> dict:
    r = r or calcular(p)
    dd = r["data_status"]
    ativs = [a for a in p.atividades.values() if a.no_calculo]
    abertas = [a for a in ativs if a.status != "concluida"]
    tarefas = [a for a in abertas if not a.marco]
    ligs = r["ligacoes"]
    n_ab = len(abertas)
    cod = lambda lst: [a.codigo for a in lst]
    tem_pred = {l.succ for l in ligs}
    tem_succ = {l.pred for l in ligs}
    pts = []

    # 1 Lógica
    sem = [a for a in abertas if (a.uid not in tem_pred and a.tipo != "marco_inicio")
           or (a.uid not in tem_succ and a.tipo != "marco_fim")]
    pts.append(_ponto(1, "Lógica (sem predecessora ou sucessora)", f"{_pct(len(sem), n_ab)}%", "≤ 5%",
                      _pct(len(sem), n_ab) <= 5, f"{len(sem)} de {n_ab} abertas", exemplos=cod(sem)))
    # 2 Leads
    leads = [l for l in ligs if l.lag_h < -EPS]
    pts.append(_ponto(2, "Leads (lag negativo)", len(leads), "0", not leads, f"{len(leads)} ligações"))
    # 3 Lags
    lags = [l for l in ligs if l.lag_h > EPS]
    pts.append(_ponto(3, "Lags", f"{_pct(len(lags), len(ligs))}%", "≤ 5%", _pct(len(lags), len(ligs)) <= 5,
                      f"{len(lags)} de {len(ligs)} ligações"))
    # 4 Tipos de ligação
    fs = [l for l in ligs if l.tipo == "FS"]
    pts.append(_ponto(4, "Ligações término-início (FS)", f"{_pct(len(fs), len(ligs))}%", "≥ 90%",
                      _pct(len(fs), len(ligs)) >= 90 if ligs else True, f"{len(fs)} de {len(ligs)} ligações"))
    # 5 Restrições rígidas
    rig = [a for a in abertas if any(x.tipo in ("MSO", "MFO", "SNLT", "FNLT") for x in a.restricoes)]
    pts.append(_ponto(5, "Restrições rígidas", f"{_pct(len(rig), n_ab)}%", "≤ 5%", _pct(len(rig), n_ab) <= 5,
                      f"{len(rig)} de {n_ab} abertas", exemplos=cod(rig)))
    # 6 Folga alta
    fd = lambda a: r["folga_h"].get(a.uid, 0.0) / p.cal(a).horas_dia
    alta = [a for a in abertas if fd(a) > DIAS_LIMITE]
    pts.append(_ponto(6, f"Folga alta (> {DIAS_LIMITE} dias úteis)", f"{_pct(len(alta), n_ab)}%", "≤ 5%",
                      _pct(len(alta), n_ab) <= 5, f"{len(alta)} de {n_ab} abertas", exemplos=cod(alta)))
    # 7 Folga negativa
    neg = [a for a in abertas if r["folga_h"].get(a.uid, 0.0) < -EPS]
    pts.append(_ponto(7, "Folga negativa", len(neg), "0", not neg, f"{len(neg)} atividades", exemplos=cod(neg)))
    # 8 Duração alta
    longas = [a for a in tarefas if a.rest_h / p.cal(a).horas_dia > DIAS_LIMITE]
    pts.append(_ponto(8, f"Duração alta (> {DIAS_LIMITE} dias úteis)", f"{_pct(len(longas), len(tarefas))}%",
                      "≤ 5%", _pct(len(longas), len(tarefas)) <= 5, f"{len(longas)} de {len(tarefas)} tarefas",
                      exemplos=cod(longas)))
    # 9 Datas inválidas
    inval = [a for a in ativs if (a.inicio_real and a.inicio_real > dd) or (a.fim_real and a.fim_real > dd)]
    inval += [a for a in abertas if a.status == "nao_iniciada" and r["es"][a.uid] < dd]
    pts.append(_ponto(9, "Datas inválidas (real após a data de status ou previsão antes dela)", len(inval), "0",
                      not inval, f"{len(inval)} atividades", exemplos=cod(inval)))
    # 10 Recursos
    sem_rec = [a for a in tarefas if a.rest_h > EPS and not a.tem_recurso]
    pts.append(_ponto(10, "Tarefas sem recurso/custo", f"{_pct(len(sem_rec), len(tarefas))}%", "0%",
                      not sem_rec, f"{len(sem_rec)} de {len(tarefas)} tarefas", exemplos=cod(sem_rec)))
    # 11 Tarefas perdidas (proxy: datas planejadas do XER)
    devidas = [a for a in ativs if a.fim_plan and a.fim_plan <= dd]
    perdidas = [a for a in devidas if not (a.status == "concluida" and a.fim_real and a.fim_real <= a.fim_plan)]
    pts.append(_ponto(11, "Tarefas perdidas (proxy: datas planejadas)", f"{_pct(len(perdidas), len(devidas))}%",
                      "≤ 5%", _pct(len(perdidas), len(devidas)) <= 5, f"{len(perdidas)} de {len(devidas)} devidas",
                      aplicavel=bool(devidas), exemplos=cod(perdidas)))
    # 12 Teste do caminho crítico
    crit_abertas = [u for u in r["criticas"] if p.atividades[u].status != "concluida"]
    if crit_abertas:
        u = crit_abertas[0]
        atraso_h = 100 * p.cal(p.atividades[u]).horas_dia
        r2 = calcular(com_atraso(p, u, atraso_h))
        cal = p.cal(p.atividades[u])
        desliz = cal.entre(r["termino"], r2["termino"])
        ok = desliz >= atraso_h - 1.0
        pts.append(_ponto(12, "Teste do caminho crítico (+100 dias numa crítica)", f"{desliz / cal.horas_dia:.0f} d",
                          "= 100 d", ok, f"atividade testada {p.atividades[u].codigo}"))
    else:
        pts.append(_ponto(12, "Teste do caminho crítico", "—", "= 100 d", None, "sem atividade crítica aberta",
                          aplicavel=False))
    # 13 CPLI
    if p.termino_exigido:
        cal = p.calendarios.get(p.calendario_padrao) or p.calendarios["_padrao"]
        cpl = cal.entre(dd, r["termino"])
        folga_proj = cal.entre(r["termino"], p.termino_exigido)
        cpli = (cpl + folga_proj) / cpl if cpl > EPS else 1.0
        pts.append(_ponto(13, "CPLI", f"{cpli:.2f}", "≥ 0,95", cpli >= 0.95, "término exigido do projeto"))
    else:
        pts.append(_ponto(13, "CPLI", "—", "≥ 0,95", None, "projeto sem término exigido", aplicavel=False))
    # 14 BEI (proxy)
    concluidas_devidas = [a for a in ativs if a.status == "concluida"]
    bei = len(concluidas_devidas) / len(devidas) if devidas else None
    pts.append(_ponto(14, "BEI (proxy: datas planejadas)", f"{bei:.2f}" if bei is not None else "—", "≥ 0,95",
                      bei is not None and bei >= 0.95, f"{len(concluidas_devidas)} concluídas / {len(devidas)} devidas",
                      aplicavel=bei is not None))

    aplic = [x for x in pts if x["aplicavel"]]
    nota = sum(1 for x in aplic if x["passou"]) / len(aplic) if aplic else 0.0
    bloqueios = [x["ponto"] for x in aplic if x["ponto"] in BLOQUEANTES and not x["passou"]]
    return {"pontos": pts, "nota": round(nota, 3), "aplicaveis": len(aplic),
            "aprovado": nota >= NOTA_MINIMA and not bloqueios, "bloqueios": bloqueios,
            "regra": "A5: nota ≥ 90% e nenhum bloqueio nos pontos 1, 3, 6, 7, 11"}
