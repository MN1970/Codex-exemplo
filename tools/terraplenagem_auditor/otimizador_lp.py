from typing import List

import pulp

from .models import AlocacaoOtima, ComposicaoSicro, EstudoTerraplenagem, ResultadoAuditoria
from .sicro_custos import custo_transporte

CUSTO_PENALIDADE_M3 = 1e6
CAPACIDADE_PADRAO_M3 = 1e9


def _custo_execucao_padrao(composicoes: List[ComposicaoSicro]) -> float:
    """Custo médio de escavação/carga/compactação das composições informadas.

    Simplificação assumida: o modelo de dados não amarra cada trecho a um código
    SICRO específico, então usa-se a média das composições fornecidas como custo
    de execução por m³, aplicado a toda alocação. Refinar por trecho/material é
    uma extensão natural quando o mapeamento trecho->código estiver disponível.
    """
    if not composicoes:
        return 0.0
    return sum(c.custo_unitario for c in composicoes) / len(composicoes)


def resolver_alocacao_otima(estudo: EstudoTerraplenagem) -> ResultadoAuditoria:
    """Resolve o problema de transporte corte/jazida -> aterro/bota-fora via PL.

    Corte e aterro são obrigatórios: todo corte tem que ir a algum destino, e
    todo aterro tem que ser preenchido (restrições de igualdade). Jazida e
    bota-fora são opcionais, limitados pela capacidade informada (restrições
    de limite superior) — o modelo só os usa se for necessário ou vantajoso.
    Uma válvula de escape com custo de penalidade alto garante que o problema
    sempre tenha solução, mesmo se as capacidades informadas forem insuficientes;
    seu uso gera um alerta em vez de tornar o modelo infactível.
    """
    custo_exec = _custo_execucao_padrao(estudo.composicoes)

    origens = []
    for trecho in estudo.trechos:
        if trecho.volume_corte_m3 > 0:
            origens.append(
                {
                    "id": f"corte@{trecho.estaca_inicial:.0f}-{trecho.estaca_final:.0f}",
                    "estaca": (trecho.estaca_inicial + trecho.estaca_final) / 2,
                    "quantidade": trecho.volume_corte_m3,
                    "custo_extra": 0.0,
                    "obrigatorio": True,
                }
            )
    for jazida in estudo.jazidas_bota_foras:
        if jazida.tipo == "jazida":
            origens.append(
                {
                    "id": f"jazida@{jazida.nome}",
                    "estaca": jazida.estaca,
                    "quantidade": jazida.capacidade_m3 if jazida.capacidade_m3 is not None else CAPACIDADE_PADRAO_M3,
                    "custo_extra": jazida.custo_unitario_extra,
                    "obrigatorio": False,
                }
            )
    origens.append(
        {
            "id": "_valvula_escape_origem",
            "estaca": None,
            "quantidade": CAPACIDADE_PADRAO_M3,
            "custo_extra": CUSTO_PENALIDADE_M3,
            "obrigatorio": False,
        }
    )

    destinos = []
    for trecho in estudo.trechos:
        if trecho.volume_aterro_m3 > 0:
            destinos.append(
                {
                    "id": f"aterro@{trecho.estaca_inicial:.0f}-{trecho.estaca_final:.0f}",
                    "estaca": (trecho.estaca_inicial + trecho.estaca_final) / 2,
                    "quantidade": trecho.volume_aterro_m3,
                    "custo_extra": 0.0,
                    "obrigatorio": True,
                }
            )
    for bota_fora in estudo.jazidas_bota_foras:
        if bota_fora.tipo == "bota_fora":
            destinos.append(
                {
                    "id": f"bota_fora@{bota_fora.nome}",
                    "estaca": bota_fora.estaca,
                    "quantidade": bota_fora.capacidade_m3
                    if bota_fora.capacidade_m3 is not None
                    else CAPACIDADE_PADRAO_M3,
                    "custo_extra": bota_fora.custo_unitario_extra,
                    "obrigatorio": False,
                }
            )
    destinos.append(
        {
            "id": "_valvula_escape_destino",
            "estaca": None,
            "quantidade": CAPACIDADE_PADRAO_M3,
            "custo_extra": CUSTO_PENALIDADE_M3,
            "obrigatorio": False,
        }
    )

    if not any(o["obrigatorio"] for o in origens) or not any(d["obrigatorio"] for d in destinos):
        return ResultadoAuditoria(
            custo_estudo=None,
            custo_otimo=0.0,
            gap_percentual=None,
            alocacoes_otimas=[],
            alertas=["Estudo sem trechos de corte ou sem trechos de aterro."],
            volume_total_m3=0.0,
        )

    problema = pulp.LpProblem("alocacao_terraplenagem", pulp.LpMinimize)
    variaveis = {}
    custos = {}
    for o in origens:
        for d in destinos:
            distancia = 0.0 if o["estaca"] is None or d["estaca"] is None else abs(o["estaca"] - d["estaca"])
            custo = (
                custo_exec
                + o["custo_extra"]
                + d["custo_extra"]
                + custo_transporte(distancia, estudo.parametros_transporte)
            )
            custos[(o["id"], d["id"])] = (custo, distancia)
            variaveis[(o["id"], d["id"])] = pulp.LpVariable(f"x_{o['id']}_{d['id']}", lowBound=0)

    problema += pulp.lpSum(
        variaveis[(o["id"], d["id"])] * custos[(o["id"], d["id"])][0] for o in origens for d in destinos
    )

    for o in origens:
        soma = pulp.lpSum(variaveis[(o["id"], d["id"])] for d in destinos)
        if o["obrigatorio"]:
            problema += soma == o["quantidade"]
        else:
            problema += soma <= o["quantidade"]

    for d in destinos:
        soma = pulp.lpSum(variaveis[(o["id"], d["id"])] for o in origens)
        if d["obrigatorio"]:
            problema += soma == d["quantidade"]
        else:
            problema += soma <= d["quantidade"]

    problema.solve(pulp.PULP_CBC_CMD(msg=False))

    alocacoes = []
    alertas = []
    custo_total = 0.0
    for o in origens:
        for d in destinos:
            valor = variaveis[(o["id"], d["id"])].value() or 0.0
            if valor <= 1e-6:
                continue
            if o["id"] == "_valvula_escape_origem" or d["id"] == "_valvula_escape_destino":
                alertas.append(
                    f"O modelo não encontrou capacidade suficiente de jazida/bota-fora para alocar "
                    f"{valor:,.0f} m³ (envolvendo {o['id']} -> {d['id']}) — revisar as capacidades "
                    f"informadas no estudo."
                )
                continue
            custo, distancia = custos[(o["id"], d["id"])]
            custo_alocacao = valor * custo
            custo_total += custo_alocacao
            alocacoes.append(
                AlocacaoOtima(
                    origem=o["id"],
                    destino=d["id"],
                    volume_m3=valor,
                    distancia_m=distancia,
                    custo_total=custo_alocacao,
                )
            )

    volume_total = sum(a.volume_m3 for a in alocacoes)

    return ResultadoAuditoria(
        custo_estudo=None,
        custo_otimo=custo_total,
        gap_percentual=None,
        alocacoes_otimas=alocacoes,
        alertas=alertas,
        volume_total_m3=volume_total,
    )
