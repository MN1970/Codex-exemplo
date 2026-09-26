"""Várias versões ao mesmo tempo: linha do tempo de versões e tendência de marcos."""
from __future__ import annotations

from datetime import datetime

from .model import Projeto
from .schedule import calcular


def linha_do_tempo(projetos: list[Projeto]) -> dict:
    """Versões em ordem de data de status, com término, custo e variação contra a anterior.

    Tendência de marcos: data de término de cada marco (casado pelo código) em cada versão.
    """
    calc = []
    for p in projetos:
        try:
            calc.append((p, calcular(p), None))
        except ValueError as e:
            calc.append((p, None, str(e)))
    calc.sort(key=lambda x: x[0].data_status or datetime.max)
    versoes, anterior = [], None
    for p, r, erro in calc:
        linha = {"chave": p.chave, "projeto": p.nome, "data_status": p.data_status,
                 "atividades": len(p.atividades), "custo_total": round(p.custo_total, 2), "erro": erro}
        if r:
            linha.update({"termino": r["termino"], "criticas": len(r["criticas"])})
            if anterior:
                linha["delta_termino_dias_corridos"] = round(
                    (r["termino"] - anterior["termino"]).total_seconds() / 86400, 1)
                linha["delta_custo"] = round(p.custo_total - anterior["custo_total"], 2)
            anterior = linha
        versoes.append(linha)

    marcos: dict[str, dict] = {}
    for p, r, _ in calc:
        if not r:
            continue
        for u in r["ordem"]:
            a = p.atividades[u]
            if a.marco:
                m = marcos.setdefault(a.codigo, {"codigo": a.codigo, "nome": a.nome, "datas": {}})
                m["datas"][p.chave] = r["ef"][u]
    tendencia = []
    for m in marcos.values():
        if len(m["datas"]) < 2:
            continue
        ordem = [v["chave"] for v in versoes if v["chave"] in m["datas"]]
        primeira, ultima = m["datas"][ordem[0]], m["datas"][ordem[-1]]
        m["deslizamento_dias_corridos"] = round((ultima - primeira).total_seconds() / 86400, 1)
        tendencia.append(m)
    tendencia.sort(key=lambda m: -abs(m["deslizamento_dias_corridos"]))
    return {"versoes": versoes, "tendencia_marcos": tendencia}
