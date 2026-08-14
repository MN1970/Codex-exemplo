from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrechoVolume:
    estaca_inicial: float
    estaca_final: float
    volume_corte_m3: float
    volume_aterro_m3: float
    tipo_material: str = "solo"


@dataclass
class JazidaBotaFora:
    nome: str
    tipo: str  # "jazida" | "bota_fora"
    estaca: float
    capacidade_m3: Optional[float] = None
    custo_unitario_extra: float = 0.0


@dataclass
class ComposicaoSicro:
    codigo: str
    descricao: str
    custo_unitario: float
    data_base: str


@dataclass
class ParametrosTransporte:
    distancia_livre_m: float = 200.0
    custo_por_m3_por_km_excedente: float = 0.0


@dataclass
class EstudoTerraplenagem:
    trechos: List[TrechoVolume]
    jazidas_bota_foras: List[JazidaBotaFora] = field(default_factory=list)
    composicoes: List[ComposicaoSicro] = field(default_factory=list)
    parametros_transporte: ParametrosTransporte = field(default_factory=ParametrosTransporte)
    custo_total_proposto: Optional[float] = None


@dataclass
class AlocacaoOtima:
    origem: str
    destino: str
    volume_m3: float
    distancia_m: float
    custo_total: float


@dataclass
class ResultadoAuditoria:
    custo_estudo: Optional[float]
    custo_otimo: float
    gap_percentual: Optional[float]
    alocacoes_otimas: List[AlocacaoOtima]
    alertas: List[str]
    volume_total_m3: float
