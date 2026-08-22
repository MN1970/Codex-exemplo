#!/usr/bin/env python3
"""Gera data/consumos/intensidades-setor.csv a partir dos agregados coletados.

Toda conta fica aqui, explicita, para poder ser reauditada. Rodar de qualquer
diretorio; o caminho de saida e resolvido a partir da raiz do repositorio.

Os agregados de entrada abaixo vieram de RESULTADO DE BUSCA, nao da leitura dos
documentos primarios - ver data/consumos/validacao/relatorio.md. Ao substituir
por dado lido na fonte, trocar tambem verificacao='fonte_primaria_lida' e o tier.
"""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "consumos" / "intensidades-setor.csv"

# ---------------------------------------------------------------- PAIC 2022 (F-001)
# valor das obras e/ou servicos, R$ milhoes
VO_2022 = {"C41": 186_100.0, "C42": 147_800.0, "C43": 105_100.0}
VO_2022["CF"] = sum(VO_2022.values())            # 439.000 -> confere com "R$ 439 bi"
# pessoal ocupado, pessoas
PO_2022 = {"C41": 862_800.0, "C42": 684_700.0, "C43": 770_300.0}
PO_2022["CF"] = sum(PO_2022.values())            # 2.317.800 -> confere com "2,3 milhoes"

# ---------------------------------------------------------------- 2024
VO_2024_CF = 522_500.0        # R$ mi, valor gerado pela industria da construcao (F-001)
CIMENTO_2024_T = 64_750_000.0 # t, consumo aparente; fontes divergem 64,7/64,8 Mt (F-063)
ACO_APARENTE_2024_T = 26_100_000.0
ACO_SHARE_CONSTRUCAO = 0.373  # participacao da construcao civil no consumo aparente (F-064)
ACO_CONSTRUCAO_T = ACO_APARENTE_2024_T * ACO_SHARE_CONSTRUCAO

HORAS_ANO = 1800.0  # PREMISSA MANTA: ~220 dias uteis x 8,2 h. Nao e dado do IBGE.

FONTE_PAIC = "https://www.ibge.gov.br/estatisticas/economicas/industria/9018-pesquisa-anual-da-industria-da-construcao.html"

rows = []
def add(**kw):
    rows.append(kw)

NOTA_SNIPPET = ("Valor NAO verificado contra a fonte primaria: o egress desta sessao bloqueou "
                "ibge.gov.br, biblioteca.ibge.gov.br, sidra.ibge.gov.br e agenciadenoticias.ibge.gov.br. "
                "Promover para fonte_primaria_lida antes de qualquer uso em orcamento de cliente.")

# --- mao de obra: pessoas-ano por R$ mi, 2022, por recorte agregado ---------
seq = 0
for setor, cnae, rot in [("C42","42","Obras de infraestrutura"),
                         ("C41","41","Construcao de edificios"),
                         ("C43","43","Servicos especializados"),
                         ("CF","F","Total da industria da construcao")]:
    seq += 1
    v = PO_2022[setor] / VO_2022[setor]
    add(id=f"INT-{setor}-MAO_DE_OBRA-001", setor=setor, cnae=cnae,
        familia_insumo="mao_de_obra", valor=round(v, 3),
        unidade_fisica="pessoas-ano/R$ mi", denominador="valor_obras_paic",
        ano_base=2022, deflator="nominal_corrente", moeda="BRL", pais="BR",
        metodo="direto",
        memoria_calculo=(f"{PO_2022[setor]:,.0f} pessoas ocupadas / R$ {VO_2022[setor]:,.0f} mi "
                         f"de valor das obras = {v:.3f} pessoas-ano por R$ mi ({rot})."
                         ).replace(",", "."),
        premissas="",
        fonte_id="F-001", fonte_localizacao="PAIC 2022 - valor das obras e pessoal ocupado por segmento",
        tier="D", licenca="publico", verificacao="snippet_busca", url=FONTE_PAIC,
        notas=NOTA_SNIPPET)

# --- mao de obra convertida em homem-hora ----------------------------------
for setor, cnae in [("C42","42"), ("CF","F")]:
    v = PO_2022[setor] / VO_2022[setor] * HORAS_ANO
    add(id=f"INT-{setor}-MAO_DE_OBRA-002", setor=setor, cnae=cnae,
        familia_insumo="mao_de_obra", valor=round(v, 0),
        unidade_fisica="hh/R$ mi", denominador="valor_obras_paic",
        ano_base=2022, deflator="nominal_corrente", moeda="BRL", pais="BR",
        metodo="indireto",
        memoria_calculo=(f"({PO_2022[setor]:,.0f} pessoas / R$ {VO_2022[setor]:,.0f} mi) x {HORAS_ANO:,.0f} h/ano "
                         f"= {v:,.0f} hh por R$ mi.").replace(",", "."),
        premissas=f"Horas trabalhadas por pessoa-ano = {HORAS_ANO:.0f} h (~220 dias uteis). PREMISSA MANTA, nao e dado do IBGE. Trocar a premissa reescala a linha inteira.",
        fonte_id="F-001", fonte_localizacao="PAIC 2022 - valor das obras e pessoal ocupado por segmento",
        tier="D", licenca="publico", verificacao="snippet_busca", url=FONTE_PAIC,
        notas=NOTA_SNIPPET)

# --- cimento --------------------------------------------------------------
v = CIMENTO_2024_T / VO_2024_CF
add(id="INT-CF-CIMENTO-001", setor="CF", cnae="F",
    familia_insumo="cimento", valor=round(v, 1),
    unidade_fisica="t/R$ mi", denominador="valor_obras_paic",
    ano_base=2024, deflator="nominal_corrente", moeda="BRL", pais="BR",
    metodo="indireto",
    memoria_calculo=(f"{CIMENTO_2024_T/1e6:.2f} Mt de consumo aparente de cimento / R$ {VO_2024_CF:,.1f} mi "
                     f"gerados pela industria da construcao = {v:.1f} t/R$ mi.").replace(",", "."),
    premissas=("Assume que TODO o cimento consumido no pais e absorvido pela construcao formal medida pela PAIC. "
               "FALSO: a autoconstrucao consome parcela relevante e nao entra na receita da PAIC. "
               "Logo esta linha SUPERESTIMA a intensidade da construcao formal. Limite superior, nao valor central."),
    fonte_id="F-063", fonte_localizacao="SNIC - Numeros do setor, consumo aparente 2024 (64,7-64,8 Mt conforme a fonte)",
    tier="D", licenca="publico", verificacao="snippet_busca", url="http://snic.org.br/numeros-do-setor.php",
    notas="Denominador vem de F-001 (PAIC 2024) e numerador de F-063. Fontes distintas - risco de recorte incompativel. " + NOTA_SNIPPET)

# --- aco ------------------------------------------------------------------
v = ACO_CONSTRUCAO_T / VO_2024_CF
add(id="INT-CF-ACO-001", setor="CF", cnae="F",
    familia_insumo="aco", valor=round(v, 2),
    unidade_fisica="t/R$ mi", denominador="valor_obras_paic",
    ano_base=2024, deflator="nominal_corrente", moeda="BRL", pais="BR",
    metodo="indireto",
    memoria_calculo=(f"{ACO_APARENTE_2024_T/1e6:.1f} Mt de consumo aparente de aco x {ACO_SHARE_CONSTRUCAO:.3f} "
                     f"(participacao da construcao civil) = {ACO_CONSTRUCAO_T/1e6:.3f} Mt; "
                     f"/ R$ {VO_2024_CF:,.1f} mi = {v:.2f} t/R$ mi.").replace(",", "."),
    premissas=("Mesma ressalva do cimento: parte do aco vai para autoconstrucao e para obra nao coberta pela PAIC. "
               "Limite superior."),
    fonte_id="F-064", fonte_localizacao="Instituto Aco Brasil - Mercado Brasileiro do Aco, consumo aparente 2024 e participacao setorial",
    tier="D", licenca="publico", verificacao="snippet_busca", url="https://www.acobrasil.org.br/",
    notas="Denominador vem de F-001 (PAIC 2024) e numerador de F-064. " + NOTA_SNIPPET)

campos = ["id","setor","cnae","familia_insumo","valor","unidade_fisica","denominador","ano_base",
          "deflator","moeda","pais","metodo","memoria_calculo","premissas","fonte_id",
          "fonte_localizacao","tier","licenca","verificacao","url","notas"]
with open(SAIDA, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k,"") for k in campos})

print(f"{len(rows)} linhas escritas")
for r in rows:
    print(f"  {r['id']:32s} {r['valor']:>10} {r['unidade_fisica']:22s} {r['ano_base']}")
print()
print("--- checagens de consistencia interna ---")
print(f"soma dos segmentos 2022 = R$ {VO_2022['CF']:,.0f} mi (esperado 439.000)")
print(f"soma do pessoal 2022    = {PO_2022['CF']:,.0f} (esperado ~2,3 mi)")
sal = 79_600.0
print(f"salarios/valor obras    = {sal/VO_2022['CF']*100:.1f}%")
print(f"salario medio anual     = R$ {sal*1e6/PO_2022['CF']:,.0f} por pessoa-ano -> R$ {sal*1e6/PO_2022['CF']/13.3:,.0f}/mes equivalente")
