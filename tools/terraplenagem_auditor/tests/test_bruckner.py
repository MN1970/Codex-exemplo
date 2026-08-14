from terraplenagem_auditor.bruckner import construir_curva_massas, identificar_compensacoes
from terraplenagem_auditor.models import TrechoVolume


def test_construir_curva_massas_acumula_corretamente():
    trechos = [
        TrechoVolume(0, 100, 100, 0),
        TrechoVolume(100, 200, 0, 100),
    ]

    curva = construir_curva_massas(trechos)

    assert curva[0] == (0, 0.0)
    assert curva[1] == (100, 100.0)
    assert curva[2] == (200, 0.0)


def test_identificar_compensacoes_detecta_retorno_a_mesma_massa():
    trechos = [
        TrechoVolume(0, 100, 100, 0),
        TrechoVolume(100, 200, 0, 100),
    ]
    curva = construir_curva_massas(trechos)

    compensacoes = identificar_compensacoes(curva)

    assert any(c["massa_m3"] == 0.0 and c["distancia_m"] == 200 for c in compensacoes)
