from terraplenagem_auditor.comparador import comparar
from terraplenagem_auditor.models import AlocacaoOtima, EstudoTerraplenagem, ResultadoAuditoria, TrechoVolume


def test_comparar_calcula_gap_percentual():
    estudo = EstudoTerraplenagem(trechos=[TrechoVolume(0, 100, 100, 100)], custo_total_proposto=1000.0)
    resultado = ResultadoAuditoria(
        custo_estudo=None,
        custo_otimo=800.0,
        gap_percentual=None,
        alocacoes_otimas=[AlocacaoOtima("corte@0-100", "bota_fora@X", 100.0, 500.0, 800.0)],
        alertas=[],
        volume_total_m3=100.0,
    )

    resultado_final = comparar(estudo, resultado)

    assert resultado_final.custo_estudo == 1000.0
    assert round(resultado_final.gap_percentual, 2) == 20.0
    assert len(resultado_final.alertas) >= 1
