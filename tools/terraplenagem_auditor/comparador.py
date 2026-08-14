from .models import EstudoTerraplenagem, ResultadoAuditoria


def comparar(estudo: EstudoTerraplenagem, resultado: ResultadoAuditoria) -> ResultadoAuditoria:
    custo_estudo = estudo.custo_total_proposto
    gap_percentual = None
    alertas = list(resultado.alertas)

    if custo_estudo is not None and custo_estudo > 0:
        gap_percentual = (custo_estudo - resultado.custo_otimo) / custo_estudo * 100
        if gap_percentual > 1.0:
            alertas.append(
                f"O estudo proposto custa {gap_percentual:.2f}% acima da alocação ótima calculada "
                f"(R$ {custo_estudo:,.2f} vs. R$ {resultado.custo_otimo:,.2f}); há espaço para otimização."
            )
        elif gap_percentual < -1.0:
            alertas.append(
                "O custo do estudo está abaixo do custo ótimo calculado pelo modelo — revisar parâmetros de "
                "transporte, capacidades de jazida/bota-fora ou custos SICRO informados, pois o modelo pode "
                "estar ignorando alguma restrição real do projeto."
            )
        else:
            alertas.append("O estudo proposto está próximo (dentro de 1%) da alocação ótima calculada.")

    for alocacao in resultado.alocacoes_otimas:
        if alocacao.destino.startswith("bota_fora@") and alocacao.distancia_m > 0:
            alertas.append(
                f"Alocação ótima envia {alocacao.volume_m3:,.0f} m³ de {alocacao.origem} para "
                f"{alocacao.destino} a {alocacao.distancia_m:,.0f} m — confirmar se o estudo já usa este "
                f"destino/distância ou se está descartando material que poderia compensar aterro mais próximo."
            )

    resultado.custo_estudo = custo_estudo
    resultado.gap_percentual = gap_percentual
    resultado.alertas = alertas
    return resultado
