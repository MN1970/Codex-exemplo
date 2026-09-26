"""Leitura e gravação de XER (Primavera P6).

Formato: texto tabulado, encoding latin-1.
  ERMHDR ...  |  %T <tabela>  |  %F <campos>  |  %R <valores>  |  %E fim
Um XER pode conter vários projetos: a leitura devolve um Projeto por linha de PROJECT.
A gravação preserva todas as tabelas originais e só atualiza os campos calculados.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from .calendar import Calendario, calendario_padrao, ler_clndr_data
from .model import Atividade, Ligacao, Projeto, Restricao

TIPOS_LIGACAO = {"PR_FS": "FS", "PR_SS": "SS", "PR_FF": "FF", "PR_SF": "SF"}
TIPOS_ATIVIDADE = {"TT_Task": "tarefa", "TT_Rsrc": "tarefa", "TT_Mile": "marco_inicio",
                   "TT_FinMile": "marco_fim", "TT_LOE": "loe", "TT_WBS": "resumo"}
STATUS = {"TK_NotStart": "nao_iniciada", "TK_Active": "em_andamento", "TK_Complete": "concluida"}
RESTRICOES = {"CS_MSOA": "SNET", "CS_MEOA": "FNET", "CS_MSOB": "SNLT", "CS_MEOB": "FNLT",
              "CS_MSO": "MSO", "CS_MEO": "MFO", "CS_MANDSTART": "MSO", "CS_MANDFIN": "MFO",
              "CS_ALAP": "ALAP"}
HISTORICO = ("obsoleto", "_deprecated", "deprecated", "99-backup")


@dataclass
class TabelasXER:
    cabecalho: str
    ordem: list[str] = field(default_factory=list)
    campos: dict[str, list[str]] = field(default_factory=dict)
    linhas: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    fim_linha: str = "\r\n"


def e_historico(caminho: str) -> bool:
    """Arquivo em pasta/nome de versão obsoleta (OBSOLETO, DEPRECATED, 99-backup)."""
    return any(h in str(caminho).lower() for h in HISTORICO)


def data_xer(v: str | None) -> datetime | None:
    if not v:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(v.strip(), fmt)
        except ValueError:
            continue
    return None


def fmt_xer(t: datetime | None) -> str:
    return t.strftime("%Y-%m-%d %H:%M") if t else ""


def _num(v: str | None) -> float:
    try:
        return float(v) if v not in (None, "") else 0.0
    except ValueError:
        return 0.0


def ler_tabelas(texto: str) -> TabelasXER:
    fim = "\r\n" if "\r\n" in texto[:5000] else "\n"
    linhas = texto.split(fim)
    tb = TabelasXER(cabecalho=linhas[0] if linhas and linhas[0].startswith("ERMHDR") else "ERMHDR\t19.12",
                    fim_linha=fim)
    atual = None
    for n, linha in enumerate(linhas, start=1):
        partes = linha.split("\t")
        marca = partes[0]
        if marca == "%T":
            atual = partes[1].strip()
            tb.ordem.append(atual)
            tb.linhas[atual] = []
        elif marca == "%F" and atual:
            tb.campos[atual] = partes[1:]
        elif marca == "%R" and atual:
            reg = dict(zip(tb.campos.get(atual, []), partes[1:]))
            reg["_linha"] = str(n)
            tb.linhas[atual].append(reg)
    return tb


def _calendarios(tb: TabelasXER, base: date, alertas: list[str]) -> dict[str, Calendario]:
    cals = {"_padrao": calendario_padrao(base)}
    for c in tb.linhas.get("CALENDAR", []):
        cid = c.get("clndr_id", "")
        try:
            semana, exc = ler_clndr_data(c.get("clndr_data", ""))
            cals[cid] = Calendario(cid, c.get("clndr_name", cid), semana, exc,
                                   _num(c.get("day_hr_cnt")) or 8.0, base=base)
        except ValueError as e:
            alertas.append(f"Calendário {cid} ({c.get('clndr_name', '')}) ilegível, usado o padrão 5×8: {e}")
    return cals


def ler_xer(caminho: str | Path | None = None, texto: str | None = None, nome: str | None = None) -> list[Projeto]:
    if texto is None:
        texto = Path(caminho).read_bytes().decode("latin-1")
    arq = nome or (Path(caminho).name if caminho else "cronograma.xer")
    tb = ler_tabelas(texto)

    datas = [data_xer(p.get("plan_start_date")) or data_xer(p.get("last_recalc_date"))
             for p in tb.linhas.get("PROJECT", [])]
    datas += [data_xer(a.get("act_start_date")) or data_xer(a.get("target_start_date"))
              for a in tb.linhas.get("TASK", [])[:5000]]
    datas = [d for d in datas if d]
    base = date(min(datas).year - 2, 1, 1) if datas else date(1990, 1, 1)

    alertas_gerais: list[str] = []
    cals = _calendarios(tb, base, alertas_gerais)
    wbs = {w["wbs_id"]: w.get("wbs_name", "") for w in tb.linhas.get("PROJWBS", [])}
    custo: dict[str, float] = {}
    real: dict[str, float] = {}
    com_recurso: set[str] = set()
    for r in tb.linhas.get("TASKRSRC", []):
        custo[r["task_id"]] = custo.get(r["task_id"], 0.0) + _num(r.get("target_cost"))
        real[r["task_id"]] = real.get(r["task_id"], 0.0) + _num(r.get("act_reg_cost")) + _num(r.get("act_ot_cost"))
        com_recurso.add(r["task_id"])

    projetos: dict[str, Projeto] = {}
    for p in tb.linhas.get("PROJECT", []):
        projetos[p["proj_id"]] = Projeto(
            id=p["proj_id"], nome=p.get("proj_short_name", p["proj_id"]), arquivo=arq,
            data_status=data_xer(p.get("last_recalc_date")) or data_xer(p.get("plan_start_date")),
            inicio_plan=data_xer(p.get("plan_start_date")),
            termino_exigido=data_xer(p.get("plan_end_date")),
            calendario_padrao=p.get("clndr_id", ""), calendarios=cals,
            alertas=list(alertas_gerais), origem=tb)

    for a in tb.linhas.get("TASK", []):
        pr = projetos.get(a.get("proj_id"))
        if not pr:
            continue
        restr = []
        for campo_t, campo_d in (("cstr_type", "cstr_date"), ("cstr_type2", "cstr_date2")):
            t = RESTRICOES.get(a.get(campo_t, ""))
            if t:
                restr.append(Restricao(t, data_xer(a.get(campo_d))))
        pr.atividades[a["task_id"]] = Atividade(
            uid=a["task_id"], codigo=a.get("task_code", ""), nome=a.get("task_name", ""),
            wbs=wbs.get(a.get("wbs_id", ""), ""),
            tipo=TIPOS_ATIVIDADE.get(a.get("task_type", "TT_Task"), "tarefa"),
            status=STATUS.get(a.get("status_code", ""), "nao_iniciada"),
            dur_h=_num(a.get("target_drtn_hr_cnt")),
            rest_h=_num(a.get("remain_drtn_hr_cnt")) if a.get("remain_drtn_hr_cnt") not in (None, "")
            else _num(a.get("target_drtn_hr_cnt")),
            calendario=a.get("clndr_id", ""),
            inicio_real=data_xer(a.get("act_start_date")), fim_real=data_xer(a.get("act_end_date")),
            inicio_plan=data_xer(a.get("target_start_date")), fim_plan=data_xer(a.get("target_end_date")),
            restricoes=restr, custo=custo.get(a["task_id"], 0.0), custo_real=real.get(a["task_id"], 0.0),
            pct_fisico=_num(a.get("phys_complete_pct")) if a.get("phys_complete_pct") not in (None, "") else None,
            tem_recurso=a["task_id"] in com_recurso,
            fonte=f"{arq} › TASK › linha {a['_linha']}")

    for r in tb.linhas.get("TASKPRED", []):
        pr = projetos.get(r.get("proj_id")) or projetos.get(r.get("pred_proj_id"))
        if pr and r.get("task_id") in pr.atividades and r.get("pred_task_id") in pr.atividades:
            pr.ligacoes.append(Ligacao(r["pred_task_id"], r["task_id"],
                                       TIPOS_LIGACAO.get(r.get("pred_type", "PR_FS"), "FS"),
                                       _num(r.get("lag_hr_cnt"))))
    return list(projetos.values())


# ---------------------------------------------------------------------------
# Gravação
# ---------------------------------------------------------------------------
CAMPOS_CALCULADOS = ("early_start_date", "early_end_date", "late_start_date", "late_end_date",
                     "total_float_hr_cnt")


def gravar_xer(projeto: Projeto, resultado: dict | None = None) -> str:
    """XER do projeto com as tabelas originais e as datas calculadas pelo motor.

    Tabelas com proj_id são filtradas para este projeto; as globais (moeda,
    calendários, recursos…) são mantidas integralmente.
    """
    tb: TabelasXER | None = projeto.origem if isinstance(projeto.origem, TabelasXER) else None
    if tb is None:
        raise ValueError("Projeto sem tabelas XER de origem (importado de outro formato)")
    fl = tb.fim_linha
    out = [tb.cabecalho]
    for nome in tb.ordem:
        campos = list(tb.campos.get(nome, []))
        linhas = [r for r in tb.linhas.get(nome, [])
                  if "proj_id" not in r or r.get("proj_id") == projeto.id]
        if nome == "TASK" and resultado:
            for c in CAMPOS_CALCULADOS:
                if c not in campos:
                    campos.append(c)
        out.append("%T\t" + nome)
        out.append("%F\t" + "\t".join(campos))
        for r in linhas:
            valores = dict(r)
            if nome == "TASK" and resultado and r.get("task_id") in resultado["es"]:
                u = r["task_id"]
                valores["early_start_date"] = fmt_xer(resultado["es"][u])
                valores["early_end_date"] = fmt_xer(resultado["ef"][u])
                valores["late_start_date"] = fmt_xer(resultado["ls"].get(u))
                valores["late_end_date"] = fmt_xer(resultado["lf"].get(u))
                if u in resultado["folga_h"]:
                    valores["total_float_hr_cnt"] = f"{resultado['folga_h'][u]:.1f}"
            out.append("%R\t" + "\t".join(valores.get(c, "") for c in campos))
    out.append("%E")
    return fl.join(out) + fl
