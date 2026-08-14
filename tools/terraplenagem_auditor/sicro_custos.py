from typing import List

from .models import ComposicaoSicro, ParametrosTransporte


def custo_unitario_execucao(composicoes: List[ComposicaoSicro], codigo: str) -> float:
    for composicao in composicoes:
        if composicao.codigo == codigo:
            return composicao.custo_unitario
    raise ValueError(f"Composição SICRO não encontrada: {codigo}")


def custo_transporte(distancia_m: float, parametros: ParametrosTransporte) -> float:
    """Aplica free-haul (distancia_livre_m) e cobra sobretransporte (overhaul) por m³ acima disso."""
    if distancia_m <= parametros.distancia_livre_m:
        return 0.0
    distancia_excedente_km = (distancia_m - parametros.distancia_livre_m) / 1000.0
    return distancia_excedente_km * parametros.custo_por_m3_por_km_excedente
