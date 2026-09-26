"""Testes do motor Manta Cronos (F1): calendários, CPM por datas, DCMA-14, XER e MSPDI."""
from datetime import date, datetime

import pytest

from cronos.engine import (calcular, comparar, curva_s, dcma14, e_historico, folga_dias, gravar_mspdi, gravar_xer,
                           ler_arquivo, ler_clndr_data, ler_mspdi, ler_xer, linha_do_tempo, monte_carlo,
                           valor_agregado)
from cronos.engine.calendar import Calendario

from cronos_xer_sintetico import clndr_5x8, montar_xer, t

pytestmark = pytest.mark.unit
D = datetime


def projeto(txt):
    return ler_xer(texto=txt, nome="teste.xer")[0]


def por_codigo(p, r, campo):
    return {a.codigo: r[campo][u] for u, a in p.atividades.items() if u in r[campo]}


# ---------------------------------------------------------------- calendário
def test_clndr_data_semana_e_feriado():
    semana, exc = ler_clndr_data(clndr_5x8([date(2025, 1, 20)]))
    assert semana[0] == [(8.0, 12.0), (13.0, 17.0)]          # segunda
    assert semana[5] == [] and semana[6] == []                # sábado, domingo
    assert exc == {date(2025, 1, 20): []}


def test_clndr_data_invalido():
    with pytest.raises(ValueError):
        ler_clndr_data("(0||CalendarData()(")


def test_soma_de_trabalho_pula_fim_de_semana_e_feriado():
    semana, exc = ler_clndr_data(clndr_5x8([date(2025, 1, 20)]))
    cal = Calendario("C1", "5x8", semana, exc, base=date(2024, 1, 1))
    assert cal.soma(D(2025, 1, 10, 8), 8) == D(2025, 1, 10, 17)            # sexta inteira
    assert cal.soma(D(2025, 1, 10, 8), 16) == D(2025, 1, 13, 17)           # atravessa o fim de semana
    assert cal.soma(D(2025, 1, 17, 17), 0, como_inicio=True) == D(2025, 1, 21, 8)  # feriado 20/01
    assert cal.soma(D(2025, 1, 13, 17), -8, como_inicio=True) == D(2025, 1, 13, 8)
    assert cal.entre(D(2025, 1, 10, 17), D(2025, 1, 21, 17)) == 48         # 6 dias úteis
    assert cal.proximo_inicio(D(2025, 1, 11, 10)) == D(2025, 1, 13, 8)     # sábado → segunda
    assert cal.ultimo_fim(D(2025, 1, 13, 8)) == D(2025, 1, 10, 17)


# ---------------------------------------------------------------- CPM por datas
def test_cpm_fs_ss_lag_feriado(xer_basico):
    p = projeto(xer_basico)
    r = calcular(p)
    es, ef = por_codigo(p, r, "es"), por_codigo(p, r, "ef")
    assert (es["A100"], ef["A100"]) == (D(2025, 1, 6, 8), D(2025, 1, 10, 17))
    assert (es["A110"], ef["A110"]) == (D(2025, 1, 13, 8), D(2025, 1, 15, 17))
    assert es["A120"] == D(2025, 1, 15, 8)                                  # SS + 2 dias
    assert ef["A120"] == D(2025, 1, 21, 17)                                 # pula feriado 20/01
    assert ef["M900"] == r["termino"] == D(2025, 1, 21, 17)
    criticas = {p.atividades[u].codigo for u in r["criticas"]}
    assert criticas == {"A100", "A110", "A120", "M900"}
    d_uid = next(u for u, a in p.atividades.items() if a.codigo == "A130")
    assert folga_dias(p, r, d_uid) == 9


def test_ff_e_sf():
    txt = montar_xer([t("1", "A", 40), t("2", "B", 16), t("3", "C", 8)],
                     [("1", "2", "PR_FF"), ("1", "3", "PR_SF", "1", 8)])
    p = projeto(txt)
    r = calcular(p)
    ef = por_codigo(p, r, "ef")
    assert ef["B"] == ef["A"] == D(2025, 1, 10, 17)                        # FF: termina junto
    assert ef["C"] == D(2025, 1, 6, 17)                                     # SF+1d: fim ≥ início(A)+1d


def test_data_de_status_real_e_logica_retida():
    """A concluída; B em andamento (remanescente 2d) espera nada; C não iniciada."""
    txt = montar_xer(
        [t("1", "A", 40, status="TK_Complete", ini="2025-01-06 08:00", fim="2025-01-10 17:00", rest=0),
         t("2", "B", 40, status="TK_Active", ini="2025-01-13 08:00", rest=16),
         t("3", "C", 8)],
        [("1", "2", "PR_FS"), ("2", "3", "PR_FS")],
        projetos=(("1", "TESTE", "2025-01-16 08:00", "", ""),))
    p = projeto(txt)
    r = calcular(p)
    es, ef = por_codigo(p, r, "es"), por_codigo(p, r, "ef")
    assert (es["A"], ef["A"]) == (D(2025, 1, 6, 8), D(2025, 1, 10, 17))    # real fixo
    assert es["B"] == D(2025, 1, 13, 8)                                     # início real
    assert ef["B"] == D(2025, 1, 17, 17)                                    # data status + 2d
    assert es["C"] == D(2025, 1, 21, 8)                                     # pula fim de semana e feriado
    assert "A" not in {p.atividades[u].codigo for u in r["folga_h"]}        # concluída fora da folga


def test_em_andamento_nao_sofre_restricao_de_ss_na_volta():
    """B já começou; a sucessora C (SS+5d) não pode tornar negativa a folga de B."""
    txt = montar_xer(
        [t("1", "B", 80, status="TK_Active", ini="2025-02-03 08:00", rest=40), t("2", "C", 120), t("3", "M", 0, tipo="TT_FinMile")],
        [("1", "2", "PR_SS", "1", 40), ("2", "3", "PR_FS"), ("1", "3", "PR_FS")],
        projetos=(("1", "TESTE", "2025-02-10 08:00", "", ""),))
    p = projeto(txt)
    r = calcular(p)
    b = next(u for u, a in p.atividades.items() if a.codigo == "B")
    assert folga_dias(p, r, b) >= 0


def test_restricoes_snet_e_fnlt_folga_negativa():
    txt = montar_xer([t("1", "A", 40, cstr="CS_MSOA", cdata="2025-01-13 08:00"),
                      t("2", "B", 16, cstr="CS_MEOB", cdata="2025-01-17 17:00")],
                     [("1", "2", "PR_FS")])
    p = projeto(txt)
    r = calcular(p)
    es, ef = por_codigo(p, r, "es"), por_codigo(p, r, "ef")
    assert es["A"] == D(2025, 1, 13, 8)                                     # não antes de 13/01
    assert ef["B"] == D(2025, 1, 22, 17)                                    # A até 17/01; B 21–22/01 (feriado 20/01)
    b = next(u for u, a in p.atividades.items() if a.codigo == "B")
    assert folga_dias(p, r, b) == -2                                        # FNLT 17/01 → folga −2d


def test_termino_exigido_gera_folga_negativa(xer_basico):
    txt = xer_basico.replace("2025-01-06 08:00\t\tC1", "2025-01-06 08:00\t2025-01-17 17:00\tC1")
    p = projeto(txt)
    assert p.termino_exigido == D(2025, 1, 17, 17)
    r = calcular(p)
    assert r["avisos"] and min(r["folga_h"].values()) < 0


def test_laco_logico_e_detectado():
    txt = montar_xer([t("1", "A", 8), t("2", "B", 8)], [("1", "2", "PR_FS"), ("2", "1", "PR_FS")])
    with pytest.raises(ValueError, match="Laço lógico"):
        calcular(projeto(txt))


# ---------------------------------------------------------------- DCMA-14
def test_dcma14_regras_a5(xer_basico):
    p = projeto(xer_basico)
    res = dcma14(p)
    pts = {x["ponto"]: x for x in res["pontos"]}
    assert len(res["pontos"]) == 14
    assert pts[1]["passou"] is False                     # A100 e A130 sem predecessora
    assert pts[3]["passou"] is False                     # 1 de 4 ligações com lag (25%)
    assert pts[7]["passou"] is True
    assert pts[10]["passou"] is False                    # A130 sem recurso
    assert pts[12]["passou"] is True                     # teste do caminho crítico
    assert pts[13]["aplicavel"] is False                 # sem término exigido
    assert res["aprovado"] is False and {1, 3} <= set(res["bloqueios"])


# ---------------------------------------------------------------- formatos
def test_xer_multiprojeto_e_custo():
    txt = montar_xer([t("1", "A", 8), t("2", "B", 8, proj="2")], [],
                     projetos=(("1", "P1", "2025-01-06 08:00", "", ""), ("2", "P2", "2025-01-06 08:00", "", "")),
                     recursos=[("1", 1234.5)])
    ps = ler_xer(texto=txt, nome="multi.xer")
    assert [x.nome for x in ps] == ["P1", "P2"]
    assert ps[0].custo_total == 1234.5 and ps[1].custo_total == 0


def test_xer_ida_e_volta_preserva_calculo(xer_basico):
    p = projeto(xer_basico)
    r = calcular(p)
    saida = gravar_xer(p, r)
    assert saida.startswith("ERMHDR") and "early_start_date" in saida and saida.rstrip().endswith("%E")
    p2 = ler_xer(texto=saida, nome="saida.xer")[0]
    r2 = calcular(p2)
    assert r2["termino"] == r["termino"]
    assert len(p2.ligacoes) == len(p.ligacoes) and p2.custo_total == p.custo_total


def test_mspdi_exporta_e_reimporta(xer_basico):
    p = projeto(xer_basico)
    r = calcular(p)
    xml = gravar_mspdi(p, r)
    q = ler_mspdi(texto=xml, nome="saida.xml")[0]
    assert len(q.atividades) == 5 and len(q.ligacoes) == 4
    tipos = sorted(l.tipo for l in q.ligacoes)
    assert tipos == ["FS", "FS", "FS", "SS"]
    assert any(abs(l.lag_h - 16) < 1e-6 for l in q.ligacoes)
    assert calcular(q)["termino"] == r["termino"]                # calendário e feriado preservados
    cal = q.cal(next(iter(q.atividades.values())))
    assert cal.excecoes == {date(2025, 1, 20): []} and cal.semana[5] == []


def test_so_dados_vigentes(tmp_path, xer_basico):
    obsoleto = tmp_path / "OBSOLETO" / "v0.xer"
    obsoleto.parent.mkdir()
    obsoleto.write_bytes(xer_basico.encode("latin-1"))
    assert e_historico(str(obsoleto)) and not e_historico("L2040.LB2-30.06.2025.xer")
    with pytest.raises(PermissionError):
        ler_arquivo(str(obsoleto))
    assert ler_arquivo(str(obsoleto), incluir_historico=True)[0].nome == "TESTE"
    with pytest.raises(ValueError, match="mpp"):
        ler_arquivo(str(tmp_path / "x.mpp"))


# ---------------------------------------------------------------- análises
def test_comparar_versoes(xer_basico):
    a = projeto(xer_basico)
    b = projeto(xer_basico.replace("\tA100\tAtividade A100\t40\t40", "\tA100\tAtividade A100\t56\t56"))
    c = comparar(a, b)
    assert c["delta_termino_dias_corridos"] == pytest.approx(2.0)          # +2 dias úteis = 21→23/01
    alt = {x["codigo"]: x for x in c["alteradas"]}
    assert alt["A100"]["delta_duracao_dias_uteis"] == 2


def test_monte_carlo_reprodutivel(xer_basico):
    p = projeto(xer_basico)
    m1, m2 = monte_carlo(p, n=60), monte_carlo(p, n=60)
    assert m1 == m2
    assert m1["P10"] <= m1["P50"] <= m1["P80"] <= m1["P90"]


# ---------------------------------------------------------------- F2: curva S, valor agregado, versões
def test_curva_s_e_valor_agregado():
    """A (40h, R$100k) concluída; B (40h, R$50k) com 50% físico; C (40h, R$30k) não iniciada."""
    txt = montar_xer(
        [t("1", "A", 40, status="TK_Complete", ini="2025-01-06 08:00", fim="2025-01-10 17:00", rest=0,
           tini="2025-01-06 08:00", tfim="2025-01-10 17:00"),
         t("2", "B", 40, status="TK_Active", ini="2025-01-13 08:00", rest=24,
           tini="2025-01-13 08:00", tfim="2025-01-17 17:00"),
         t("3", "C", 40, tini="2025-01-21 08:00", tfim="2025-01-27 17:00")],
        [("1", "2", "PR_FS"), ("2", "3", "PR_FS")],
        recursos=[("1", 100000), ("2", 50000), ("3", 30000)],
        projetos=(("1", "TESTE", "2025-01-15 08:00", "", ""),))
    txt = txt.replace("taskrsrc_id\ttask_id\tproj_id\ttarget_cost",
                      "taskrsrc_id\ttask_id\tproj_id\ttarget_cost\tact_reg_cost")
    linhas = txt.split("\r\n")
    ini = linhas.index("%T\tTASKRSRC")
    for i, real in zip(range(ini + 2, ini + 5), (110000, 20000, 0)):
        linhas[i] += f"\t{real}"
    p = projeto("\r\n".join(linhas))
    ev = valor_agregado(p)
    assert ev["BAC"] == 180000
    assert ev["PV"] == 120000                               # A inteira + 2 de 5 dias de B até 15/01 08h
    assert ev["EV"] == pytest.approx(100000 + 50000 * 16 / 40)
    assert ev["AC"] == 130000
    assert ev["SPI"] == pytest.approx(round(120000 / 120000, 3))
    assert ev["CPI"] == pytest.approx(round(120000 / 130000, 3))
    cs = curva_s(p)
    assert cs["meses"][-1]["planejado_custo"] == 180000 and cs["meses"][-1]["previsto_fisico_pct"] == 100
    assert cs["meses"][0]["mes"] == "2025-01" and not cs["linha_de_base_proxy"]


def test_valor_agregado_sem_custo_real(xer_basico):
    ev = valor_agregado(projeto(xer_basico))
    assert ev["AC"] is None and ev["CPI"] is None and ev["avisos"]


def test_linha_do_tempo_e_tendencia_de_marcos(xer_basico):
    v1 = ler_xer(texto=xer_basico, nome="v1.xer")[0]
    v2 = ler_xer(texto=xer_basico.replace("\tA100\tAtividade A100\t40\t40", "\tA100\tAtividade A100\t56\t56")
                 .replace("2025-01-06 08:00\t2025-01-06 08:00", "2025-02-03 08:00\t2025-01-06 08:00", 1), nome="v2.xer")[0]
    lt = linha_do_tempo([v2, v1])
    assert [v["chave"] for v in lt["versoes"]] == ["v1.xer#1", "v2.xer#1"]     # ordem por data de status
    assert lt["versoes"][1]["delta_termino_dias_corridos"] > 0
    m = lt["tendencia_marcos"][0]
    assert m["codigo"] == "M900" and m["deslizamento_dias_corridos"] > 0
