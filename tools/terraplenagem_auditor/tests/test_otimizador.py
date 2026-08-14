from terraplenagem_auditor.models import ComposicaoSicro, EstudoTerraplenagem, ParametrosTransporte, TrechoVolume
from terraplenagem_auditor.otimizador_lp import resolver_alocacao_otima
from terraplenagem_auditor.sicro_custos import custo_transporte


def test_resolver_alocacao_otima_minimiza_custo_transporte():
    trechos = [
        TrechoVolume(0, 100, 1000, 0),
        TrechoVolume(100, 200, 0, 500),
        TrechoVolume(1000, 1100, 0, 500),
    ]
    composicoes = [ComposicaoSicro("EXEMPLO", "Escavação ilustrativa", 10.0, "2026")]
    parametros = ParametrosTransporte(distancia_livre_m=50.0, custo_por_m3_por_km_excedente=5.0)
    estudo = EstudoTerraplenagem(trechos=trechos, composicoes=composicoes, parametros_transporte=parametros)

    resultado = resolver_alocacao_otima(estudo)

    distancia_aterro_longe = abs(50 - 1050)
    custo_ingenuo_tudo_no_aterro_longe = 1000 * (10.0 + custo_transporte(distancia_aterro_longe, parametros))

    assert resultado.custo_otimo > 0
    assert resultado.custo_otimo <= custo_ingenuo_tudo_no_aterro_longe
    assert sum(a.volume_m3 for a in resultado.alocacoes_otimas) == 1000
