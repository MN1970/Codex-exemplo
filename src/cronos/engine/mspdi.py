"""MS Project XML (MSPDI): leitura e gravação.

É o formato de troca com o MS Project: o .mpp binário não é gravável por
bibliotecas abertas, então o Cronos exporta MSPDI e o MS Project salva como .mpp.
Tipos de ligação no MSPDI: 0 = FF, 1 = FS, 2 = SF, 3 = SS. LinkLag em décimos de minuto.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from .calendar import Calendario, calendario_padrao
from .model import Atividade, Ligacao, Projeto

NS = "http://schemas.microsoft.com/project"
TIPO_DE = {"0": "FF", "1": "FS", "2": "SF", "3": "SS"}
TIPO_PARA = {v: k for k, v in TIPO_DE.items()}


def _horas_iso(v: str | None) -> float:
    m = re.match(r"PT(\d+(?:\.\d+)?)H(\d+(?:\.\d+)?)M(\d+(?:\.\d+)?)S", v or "")
    return float(m.group(1)) + float(m.group(2)) / 60 + float(m.group(3)) / 3600 if m else 0.0


def _data(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.strip()[:19])
    except ValueError:
        return None


def ler_mspdi(caminho: str | Path | None = None, texto: str | None = None, nome: str | None = None) -> list[Projeto]:
    if texto is None:
        texto = Path(caminho).read_text(encoding="utf-8-sig")
    arq = nome or (Path(caminho).name if caminho else "cronograma.xml")
    try:
        raiz = ET.fromstring(texto)
    except ET.ParseError as e:
        raise ValueError(f"XML inválido: {e}") from e
    ns = {"p": NS} if raiz.tag.startswith("{") else {}
    q = (lambda t: f"p:{t}") if ns else (lambda t: t)
    if raiz.find(q("Tasks"), ns) is None:
        raise ValueError("XML não reconhecido como MS Project (MSPDI): sem <Tasks>")
    g = lambda el, t: (el.findtext(q(t), default="", namespaces=ns) or "").strip()

    inicio = _data(g(raiz, "StartDate"))
    base = date((inicio.year if inicio else 2000) - 2, 1, 1)
    horas_dia = (float(g(raiz, "MinutesPerDay") or 480)) / 60
    cal = Calendario("_padrao", "Padrão do MS Project", horas_dia=horas_dia, base=base)
    pr = Projeto(id="1", nome=g(raiz, "Name") or g(raiz, "Title") or arq, arquivo=arq,
                 data_status=_data(g(raiz, "StatusDate")) or inicio, inicio_plan=inicio,
                 termino_exigido=None, calendarios={"_padrao": cal})
    pr.alertas.append("Calendários do MSPDI ainda não são lidos: usado o padrão 5×8 (F2)")

    tarefas = raiz.find(q("Tasks"), ns)
    for n, t in enumerate(tarefas.findall(q("Task"), ns), start=1):
        if g(t, "Summary") == "1" or g(t, "IsNull") == "1" or not g(t, "Name"):
            continue
        uid = g(t, "UID")
        pc = float(g(t, "PercentComplete") or 0)
        dur = _horas_iso(g(t, "Duration"))
        rest = _horas_iso(g(t, "RemainingDuration")) if g(t, "RemainingDuration") else dur
        pr.atividades[uid] = Atividade(
            uid=uid, codigo=g(t, "WBS") or g(t, "ID") or uid, nome=g(t, "Name"), wbs=g(t, "OutlineNumber"),
            tipo="marco_fim" if g(t, "Milestone") == "1" else "tarefa",
            status="concluida" if pc >= 100 else ("em_andamento" if pc > 0 else "nao_iniciada"),
            dur_h=dur, rest_h=0.0 if pc >= 100 else rest,
            inicio_real=_data(g(t, "ActualStart")), fim_real=_data(g(t, "ActualFinish")),
            inicio_plan=_data(g(t, "Start")), fim_plan=_data(g(t, "Finish")),
            custo=float(g(t, "Cost") or 0), tem_recurso=float(g(t, "Cost") or 0) > 0,
            fonte=f"{arq} › Task UID {uid} (item {n})")
    for t in tarefas.findall(q("Task"), ns):
        su = g(t, "UID")
        if su not in pr.atividades:
            continue
        for lk in t.findall(q("PredecessorLink"), ns):
            pu = g(lk, "PredecessorUID")
            if pu in pr.atividades:
                pr.ligacoes.append(Ligacao(pu, su, TIPO_DE.get(g(lk, "Type") or "1", "FS"),
                                           float(g(lk, "LinkLag") or 0) / 600.0))
    return [pr]


def _iso(t: datetime | None) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S") if t else ""


def _dur(h: float) -> str:
    h = max(h, 0.0)
    horas = int(h)
    minutos = round((h - horas) * 60)
    return f"PT{horas}H{minutos}M0S"


def gravar_mspdi(p: Projeto, r: dict) -> str:
    """MSPDI com datas calculadas. Uma única tabela de calendário padrão (F1)."""
    cal = p.calendarios.get(p.calendario_padrao) or p.calendarios.get("_padrao") or calendario_padrao()
    ids = [u for u in r["ordem"]]
    uid_num = {u: i for i, u in enumerate(ids, start=1)}
    preds: dict[str, list[Ligacao]] = {}
    for l in r["ligacoes"]:
        preds.setdefault(l.succ, []).append(l)
    semana = "".join(
        f"<WeekDay><DayType>{(d + 1) % 7 + 1}</DayType><DayWorking>{1 if cal.semana[d] else 0}</DayWorking>"
        + ("<WorkingTimes>" + "".join(
            f"<WorkingTime><FromTime>{int(s):02d}:{int(round((s % 1) * 60)):02d}:00</FromTime>"
            f"<ToTime>{int(e) % 24:02d}:{int(round((e % 1) * 60)):02d}:00</ToTime></WorkingTime>"
            for s, e in cal.semana[d]) + "</WorkingTimes>" if cal.semana[d] else "")
        + "</WeekDay>" for d in range(7))
    x = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
         f'<Project xmlns="{NS}">',
         f"<Name>{escape(p.nome)}</Name><Title>{escape(p.nome)}</Title>",
         f"<StartDate>{_iso(min(r['es'].values(), default=r['data_status']))}</StartDate>",
         f"<StatusDate>{_iso(r['data_status'])}</StatusDate>",
         f"<MinutesPerDay>{int(cal.horas_dia * 60)}</MinutesPerDay><CalendarUID>1</CalendarUID>",
         "<Calendars><Calendar><UID>1</UID><Name>" + escape(cal.nome) + "</Name><IsBaseCalendar>1</IsBaseCalendar>"
         f"<WeekDays>{semana}</WeekDays></Calendar></Calendars>",
         "<Tasks>"]
    for u in ids:
        a = p.atividades[u]
        pc = 100 if a.status == "concluida" else (
            0 if a.status == "nao_iniciada" or a.dur_h <= 0 else int(max(0.0, min(99.0, 100 * (1 - a.rest_h / a.dur_h)))))
        dur = a.dur_h if a.status != "concluida" else max(a.dur_h, 0.0)
        x.append("<Task>"
                 f"<UID>{uid_num[u]}</UID><ID>{uid_num[u]}</ID><Name>{escape(a.nome)}</Name>"
                 f"<WBS>{escape(a.codigo)}</WBS><OutlineLevel>1</OutlineLevel>"
                 f"<Start>{_iso(r['es'][u])}</Start><Finish>{_iso(r['ef'][u])}</Finish>"
                 f"<Duration>{_dur(dur)}</Duration><DurationFormat>7</DurationFormat>"
                 f"<RemainingDuration>{_dur(0 if a.status == 'concluida' else a.rest_h)}</RemainingDuration>"
                 f"<Milestone>{1 if a.marco else 0}</Milestone><PercentComplete>{pc}</PercentComplete>"
                 f"<Cost>{a.custo:.2f}</Cost>"
                 + (f"<ActualStart>{_iso(a.inicio_real)}</ActualStart>" if a.inicio_real else "")
                 + (f"<ActualFinish>{_iso(a.fim_real)}</ActualFinish>" if a.fim_real else "")
                 + "".join(f"<PredecessorLink><PredecessorUID>{uid_num[l.pred]}</PredecessorUID>"
                           f"<Type>{TIPO_PARA[l.tipo]}</Type><LinkLag>{int(round(l.lag_h * 600))}</LinkLag>"
                           "<LagFormat>7</LagFormat></PredecessorLink>" for l in preds.get(u, []))
                 + "</Task>")
    x += ["</Tasks>", "</Project>"]
    return "\n".join(x) + "\n"
