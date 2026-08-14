from typing import List

from .models import TrechoVolume


def construir_curva_massas(trechos: List[TrechoVolume]) -> List[tuple]:
    """Reconstrói o diagrama de massas (curva de Brückner) por acumulação: corte soma, aterro subtrai."""
    if not trechos:
        return []

    trechos_ordenados = sorted(trechos, key=lambda t: t.estaca_inicial)
    curva = [(trechos_ordenados[0].estaca_inicial, 0.0)]
    massa_acumulada = 0.0
    for trecho in trechos_ordenados:
        massa_acumulada += trecho.volume_corte_m3 - trecho.volume_aterro_m3
        curva.append((trecho.estaca_final, massa_acumulada))
    return curva


def identificar_compensacoes(curva: List[tuple], tolerancia_m3: float = 1e-6) -> List[dict]:
    """Segmentos onde a curva retorna à mesma ordenada: corte e aterro se compensam sem jazida/bota-fora."""
    compensacoes = []
    for i in range(len(curva)):
        estaca_i, massa_i = curva[i]
        for j in range(i + 1, len(curva)):
            estaca_j, massa_j = curva[j]
            if abs(massa_j - massa_i) <= tolerancia_m3:
                compensacoes.append(
                    {
                        "estaca_inicial": estaca_i,
                        "estaca_final": estaca_j,
                        "distancia_m": estaca_j - estaca_i,
                        "massa_m3": massa_i,
                    }
                )
    return compensacoes
