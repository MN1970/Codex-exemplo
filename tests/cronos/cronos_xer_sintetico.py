"""XER sintéticos para os testes do Manta Cronos (nenhum dado de cliente)."""
from datetime import date


def serial(d: date) -> int:
    return (d - date(1899, 12, 30)).days


def clndr_5x8(feriados=()):
    dia = "(0||{n}()({h}))"
    util = "(0||0(s|08:00|f|12:00)())(0||1(s|13:00|f|17:00)())"
    semana = "".join(dia.format(n=n, h=(util if 2 <= n <= 6 else "")) for n in range(1, 8))
    exc = "".join(f"(0||{i}(d|{serial(f)})())" for i, f in enumerate(feriados))
    return ("(0||CalendarData()(\x7f(0||DaysOfWeek()(" + semana + "))"
            "(0||VIEW(ShowTotal|Y)())(0||Exceptions()(" + exc + "))))")


def tabela(nome, campos, linhas):
    return ("%T\t" + nome + "\r\n%F\t" + "\t".join(campos) + "\r\n"
            + "".join("%R\t" + "\t".join(str(v) for v in l) + "\r\n" for l in linhas))


def montar_xer(tarefas, ligacoes, recursos=(), projetos=(("1", "TESTE", "2025-01-06 08:00", "", ""),),
               feriados=(date(2025, 1, 20),), eap=None, eap_de=None):
    """tarefas: (task_id, proj_id, código, nome, dur_h, tipo, status, ini_real, fim_real, rest_h,
                 cstr_type, cstr_date, target_start, target_end)
    eap: linhas (wbs_id, parent_wbs_id, seq_num, proj_node_flag, wbs_name) em vez da EAP de um nó;
    eap_de: {task_id: wbs_id}."""
    txt = "ERMHDR\t19.12\t2025-01-01\tProject\tadmin\tadmin\tdbx\tProject Management\tBRL\r\n"
    txt += tabela("CALENDAR", ["clndr_id", "clndr_name", "day_hr_cnt", "clndr_data"],
                  [["C1", "Padrao 5x8", "8", clndr_5x8(feriados)]])
    txt += tabela("PROJECT", ["proj_id", "proj_short_name", "last_recalc_date", "plan_start_date",
                              "plan_end_date", "clndr_id"],
                  [[p[0], p[1], p[2], p[2], p[3], "C1"] for p in projetos])
    if eap:
        txt += tabela("PROJWBS", ["wbs_id", "proj_id", "parent_wbs_id", "seq_num", "proj_node_flag", "wbs_name"],
                      [[w[0], projetos[0][0], w[1], w[2], w[3], w[4]] for w in eap])
    else:
        txt += tabela("PROJWBS", ["wbs_id", "proj_id", "wbs_name"], [["W1", p[0], "Obra"] for p in projetos])
    txt += tabela("TASK", ["task_id", "proj_id", "wbs_id", "clndr_id", "task_code", "task_name",
                           "target_drtn_hr_cnt", "remain_drtn_hr_cnt", "task_type", "status_code",
                           "act_start_date", "act_end_date", "cstr_type", "cstr_date",
                           "target_start_date", "target_end_date"],
                  [[t[0], t[1], (eap_de or {}).get(t[0], "W1"), "C1", t[2], t[3], t[4], t[9] if t[9] is not None else t[4], t[5], t[6],
                    t[7], t[8], t[10], t[11], t[12], t[13]] for t in tarefas])
    txt += tabela("TASKPRED", ["task_pred_id", "task_id", "pred_task_id", "proj_id", "pred_type", "lag_hr_cnt"],
                  [[i, l[1], l[0], l[3] if len(l) > 3 else "1", l[2], l[4] if len(l) > 4 else 0]
                   for i, l in enumerate(ligacoes, start=1)])
    txt += tabela("TASKRSRC", ["taskrsrc_id", "task_id", "proj_id", "target_cost", "act_reg_cost"],
                  [[i, r[0], "1", r[1], r[2] if len(r) > 2 else 0] for i, r in enumerate(recursos, start=1)])
    return txt + "%E\r\n"


def t(uid, cod, dur_h, tipo="TT_Task", status="TK_NotStart", ini="", fim="", rest=None,
      cstr="", cdata="", tini="", tfim="", proj="1"):
    return (uid, proj, cod, f"Atividade {cod}", dur_h, tipo, status, ini, fim, rest, cstr, cdata, tini, tfim)
