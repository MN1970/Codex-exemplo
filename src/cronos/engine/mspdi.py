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
from .model import Atividade, Ligacao, Projeto, Restricao

NS = "http://schemas.microsoft.com/project"
TIPO_DE = {"0": "FF", "1": "FS", "2": "SF", "3": "SS"}
TIPO_PARA = {v: k for k, v in TIPO_DE.items()}
# ConstraintType do MSPDI (0 = ASAP). O MS Project aceita uma restrição por tarefa.
RESTRICAO_DE = {"1": "ALAP", "2": "MSO", "3": "MFO", "4": "SNET", "5": "SNLT", "6": "FNET", "7": "FNLT"}
RESTRICAO_PARA = {v: k for k, v in RESTRICAO_DE.items()}


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


def _hhmm(v: str) -> float:
    partes = (v or "0:0").split(":")
    return int(partes[0]) + int(partes[1]) / 60.0


def _faixas(el, ns, q) -> list[tuple[float, float]]:
    out = []
    for wt in el.findall(f"{q('WorkingTimes')}/{q('WorkingTime')}", ns):
        s = _hhmm(wt.findtext(q("FromTime"), default="", namespaces=ns))
        e = _hhmm(wt.findtext(q("ToTime"), default="", namespaces=ns))
        if e <= s:
            e = 24.0 if e == 0 else e + 24.0
        out.append((s, min(e, 24.0)))
    return sorted(out)


def _dias(el, ns, q, g) -> list[date]:
    ini = _data(g(el, "FromDate")) if el is not None else None
    fim = _data(g(el, "ToDate")) if el is not None else None
    if not ini:
        return []
    fim = fim or ini
    return [date.fromordinal(o) for o in range(ini.date().toordinal(), fim.date().toordinal() + 1)][:3660]


def _calendarios_mspdi(raiz, ns, q, g, horas_dia, base):
    """Semana (DayType 1 = domingo … 7 = sábado) e exceções nos dois formatos do MSPDI."""
    cals: dict[str, Calendario] = {"_padrao": Calendario("_padrao", "Padrão 5×8", horas_dia=horas_dia, base=base)}
    alertas: list[str] = []
    brutos = {}
    for c in raiz.findall(f"{q('Calendars')}/{q('Calendar')}", ns):
        uid = g(c, "UID")
        semana: dict[int, list] = {}
        excecoes: dict[date, list] = {}
        for wd in c.findall(f"{q('WeekDays')}/{q('WeekDay')}", ns):
            tipo = g(wd, "DayType")
            faixas = _faixas(wd, ns, q) if g(wd, "DayWorking") == "1" else []
            if tipo == "0":
                for d in _dias(wd.find(q("TimePeriod"), ns), ns, q, g):
                    excecoes[d] = faixas
            elif tipo.isdigit() and 1 <= int(tipo) <= 7:
                semana[(int(tipo) + 5) % 7] = faixas
        for ex in c.findall(f"{q('Exceptions')}/{q('Exception')}", ns):
            faixas = _faixas(ex, ns, q) if g(ex, "DayWorking") == "1" else []
            for d in _dias(ex.find(q("TimePeriod"), ns), ns, q, g):
                excecoes[d] = faixas
        brutos[uid] = (g(c, "Name") or uid, g(c, "BaseCalendarUID"), semana, excecoes)
    for uid, (nome, base_uid, semana, excecoes) in brutos.items():
        herdada = brutos.get(base_uid)
        sem = {d: semana.get(d, herdada[2].get(d) if herdada else None) for d in range(7)}
        if any(v is None for v in sem.values()):
            padrao = cals["_padrao"].semana
            sem = {d: (v if v is not None else padrao[d]) for d, v in sem.items()}
        exc = dict(herdada[3]) if herdada else {}
        exc.update(excecoes)
        try:
            cals[uid] = Calendario(uid, nome, sem, exc, horas_dia=horas_dia, base=base)
        except ValueError as e:
            alertas.append(f"Calendário {uid} ({nome}) ignorado: {e}")
    return cals, alertas


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
    cals, alertas = _calendarios_mspdi(raiz, ns, q, g, horas_dia, base)
    padrao = g(raiz, "CalendarUID")
    pr = Projeto(id="1", nome=g(raiz, "Name") or g(raiz, "Title") or arq, arquivo=arq,
                 data_status=_data(g(raiz, "StatusDate")) or inicio, inicio_plan=inicio,
                 termino_exigido=None, calendarios=cals,
                 calendario_padrao=padrao if padrao in cals else "_padrao", alertas=alertas)

    tarefas = raiz.find(q("Tasks"), ns)
    for n, t in enumerate(tarefas.findall(q("Task"), ns), start=1):
        if g(t, "Summary") == "1" or g(t, "IsNull") == "1" or not g(t, "Name"):
            continue
        uid = g(t, "UID")
        pc = float(g(t, "PercentComplete") or 0)
        dur = _horas_iso(g(t, "Duration"))
        rest = _horas_iso(g(t, "RemainingDuration")) if g(t, "RemainingDuration") else dur
        fim_real, ini_real = _data(g(t, "ActualFinish")), _data(g(t, "ActualStart"))
        status = ("concluida" if pc >= 100 or fim_real else
                  "em_andamento" if pc > 0 or ini_real else "nao_iniciada")
        ct = RESTRICAO_DE.get(g(t, "ConstraintType"))
        restr = [Restricao(ct, _data(g(t, "ConstraintDate")))] if ct else []
        pr.atividades[uid] = Atividade(
            uid=uid, codigo=g(t, "WBS") or g(t, "ID") or uid, nome=g(t, "Name"), wbs=g(t, "OutlineNumber"),
            tipo="marco_fim" if g(t, "Milestone") == "1" else "tarefa",
            status=status, dur_h=dur, rest_h=0.0 if status == "concluida" else rest,
            inicio_real=ini_real, fim_real=fim_real, restricoes=restr,
            inicio_plan=_data(g(t, "Start")), fim_plan=_data(g(t, "Finish")),
            custo=float(g(t, "Cost") or 0), custo_real=float(g(t, "ActualCost") or 0),
            pct_fisico=float(g(t, "PhysicalPercentComplete")) if g(t, "PhysicalPercentComplete") else None,
            tem_recurso=float(g(t, "Cost") or 0) > 0,
            calendario=g(t, "CalendarUID") if g(t, "CalendarUID") in cals else "",
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


def _excecoes_xml(cal) -> str:
    if not cal.excecoes:
        return ""
    itens = []
    for d, faixas in sorted(cal.excecoes.items()):
        tempos = "".join(
            f"<WorkingTime><FromTime>{int(s):02d}:{int(round((s % 1) * 60)):02d}:00</FromTime>"
            f"<ToTime>{int(e) % 24:02d}:{int(round((e % 1) * 60)):02d}:00</ToTime></WorkingTime>" for s, e in faixas)
        itens.append(f"<Exception><EnteredByOccurrences>0</EnteredByOccurrences><TimePeriod>"
                     f"<FromDate>{d.isoformat()}T00:00:00</FromDate><ToDate>{d.isoformat()}T23:59:00</ToDate>"
                     f"</TimePeriod><Occurrences>1</Occurrences><Type>1</Type>"
                     f"<DayWorking>{1 if faixas else 0}</DayWorking>"
                     + (f"<WorkingTimes>{tempos}</WorkingTimes>" if faixas else "") + "</Exception>")
    return "<Exceptions>" + "".join(itens) + "</Exceptions>"


def _semana_xml(cal) -> str:
    return "".join(
        f"<WeekDay><DayType>{(d + 1) % 7 + 1}</DayType><DayWorking>{1 if cal.semana[d] else 0}</DayWorking>"
        + ("<WorkingTimes>" + "".join(
            f"<WorkingTime><FromTime>{int(s):02d}:{int(round((s % 1) * 60)):02d}:00</FromTime>"
            f"<ToTime>{int(e) % 24:02d}:{int(round((e % 1) * 60)):02d}:00</ToTime></WorkingTime>"
            for s, e in cal.semana[d]) + "</WorkingTimes>" if cal.semana[d] else "")
        + "</WeekDay>" for d in range(7))


def gravar_mspdi(p: Projeto, r: dict) -> str:
    """MSPDI com datas calculadas e todos os calendários usados (semana + exceções)."""
    padrao = p.calendarios.get(p.calendario_padrao) or p.calendarios.get("_padrao") or calendario_padrao()
    ids = [u for u in r["ordem"]]
    uid_num = {u: i for i, u in enumerate(ids, start=1)}
    preds: dict[str, list[Ligacao]] = {}
    for l in r["ligacoes"]:
        preds.setdefault(l.succ, []).append(l)
    usados = [padrao]
    for u in ids:
        c = p.cal(p.atividades[u])
        if all(c is not x for x in usados):
            usados.append(c)
    cal_uid = {id(c): i for i, c in enumerate(usados, start=1)}
    calendarios = "".join(
        f"<Calendar><UID>{cal_uid[id(c)]}</UID><Name>{escape(c.nome)}</Name><IsBaseCalendar>1</IsBaseCalendar>"
        f"<WeekDays>{_semana_xml(c)}</WeekDays>{_excecoes_xml(c)}</Calendar>" for c in usados)
    x = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
         f'<Project xmlns="{NS}">',
         f"<Name>{escape(p.nome)}</Name><Title>{escape(p.nome)}</Title>",
         f"<StartDate>{_iso(min(r['es'].values(), default=r['data_status']))}</StartDate>",
         f"<StatusDate>{_iso(r['data_status'])}</StatusDate>",
         f"<MinutesPerDay>{int(padrao.horas_dia * 60)}</MinutesPerDay><CalendarUID>1</CalendarUID>",
         f"<Calendars>{calendarios}</Calendars>",
         "<Tasks>"]
    for u in ids:
        a = p.atividades[u]
        cstr = next((c for c in a.restricoes if c.tipo in RESTRICAO_PARA), None)
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
                 f"<Cost>{a.custo:.2f}</Cost><ActualCost>{a.custo_real:.2f}</ActualCost>"
                 f"<CalendarUID>{cal_uid[id(p.cal(a))]}</CalendarUID>"
                 + (f"<ConstraintType>{RESTRICAO_PARA[cstr.tipo]}</ConstraintType>"
                    + (f"<ConstraintDate>{_iso(cstr.data)}</ConstraintDate>" if cstr.data else "") if cstr else "")
                 + (f"<ActualStart>{_iso(a.inicio_real)}</ActualStart>" if a.inicio_real else "")
                 + (f"<ActualFinish>{_iso(a.fim_real)}</ActualFinish>" if a.fim_real else "")
                 + "".join(f"<PredecessorLink><PredecessorUID>{uid_num[l.pred]}</PredecessorUID>"
                           f"<Type>{TIPO_PARA[l.tipo]}</Type><LinkLag>{int(round(l.lag_h * 600))}</LinkLag>"
                           "<LagFormat>7</LagFormat></PredecessorLink>" for l in preds.get(u, []))
                 + "</Task>")
    x += ["</Tasks>", "</Project>"]
    return "\n".join(x) + "\n"
