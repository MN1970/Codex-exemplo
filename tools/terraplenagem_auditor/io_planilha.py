from typing import Optional

import pandas as pd

from .models import ComposicaoSicro, EstudoTerraplenagem, JazidaBotaFora, ParametrosTransporte, TrechoVolume


def carregar_estudo_csv(
    caminho_trechos: str,
    caminho_jazidas: Optional[str] = None,
    caminho_composicoes: Optional[str] = None,
    custo_total_proposto: Optional[float] = None,
) -> EstudoTerraplenagem:
    df_trechos = pd.read_csv(caminho_trechos)
    trechos = [
        TrechoVolume(
            estaca_inicial=float(row["estaca_inicial"]),
            estaca_final=float(row["estaca_final"]),
            volume_corte_m3=float(row["volume_corte_m3"]),
            volume_aterro_m3=float(row["volume_aterro_m3"]),
            tipo_material=str(row.get("tipo_material", "solo") or "solo"),
        )
        for _, row in df_trechos.iterrows()
    ]

    jazidas_bota_foras = []
    if caminho_jazidas:
        df_jazidas = pd.read_csv(caminho_jazidas)
        for _, row in df_jazidas.iterrows():
            capacidade = row.get("capacidade_m3")
            jazidas_bota_foras.append(
                JazidaBotaFora(
                    nome=str(row["nome"]),
                    tipo=str(row["tipo"]),
                    estaca=float(row["estaca"]),
                    capacidade_m3=float(capacidade) if pd.notna(capacidade) else None,
                    custo_unitario_extra=float(row.get("custo_unitario_extra", 0.0) or 0.0),
                )
            )

    composicoes = []
    if caminho_composicoes:
        df_composicoes = pd.read_csv(caminho_composicoes)
        for _, row in df_composicoes.iterrows():
            composicoes.append(
                ComposicaoSicro(
                    codigo=str(row["codigo"]),
                    descricao=str(row["descricao"]),
                    custo_unitario=float(row["custo_unitario"]),
                    data_base=str(row["data_base"]),
                )
            )

    return EstudoTerraplenagem(
        trechos=trechos,
        jazidas_bota_foras=jazidas_bota_foras,
        composicoes=composicoes,
        parametros_transporte=ParametrosTransporte(),
        custo_total_proposto=custo_total_proposto,
    )
