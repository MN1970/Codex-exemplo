"""Modelo canônico do Manta Cronos (independente do formato de origem)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .calendar import Calendario

TIPOS_LIGACAO = ("FS", "SS", "FF", "SF")
RESTRICOES_CEDO = {"SNET", "FNET", "MSO", "MFO"}       # afetam a ida
RESTRICOES_TARDE = {"SNLT", "FNLT", "MSO", "MFO"}      # afetam a volta
RESTRICOES_RIGIDAS = {"MSO", "MFO", "SNLT", "FNLT"}    # DCMA ponto 5


@dataclass
class Restricao:
    tipo: str            # SNET, FNET, SNLT, FNLT, MSO, MFO, ALAP
    data: datetime | None


@dataclass
class Atividade:
    uid: str
    codigo: str
    nome: str
    wbs: str = ""
    tipo: str = "tarefa"              # tarefa | marco_inicio | marco_fim | loe | resumo
    status: str = "nao_iniciada"      # nao_iniciada | em_andamento | concluida
    dur_h: float = 0.0                # duração original (h de trabalho)
    rest_h: float = 0.0               # duração remanescente (h de trabalho)
    calendario: str = ""
    inicio_real: datetime | None = None
    fim_real: datetime | None = None
    inicio_plan: datetime | None = None   # target_start_date (planejado) — proxy de linha de base
    fim_plan: datetime | None = None      # target_end_date
    restricoes: list[Restricao] = field(default_factory=list)
    custo: float = 0.0                    # cost-loaded: soma de TASKRSRC.target_cost (orçado)
    custo_real: float = 0.0               # TASKRSRC.act_reg_cost + act_ot_cost
    pct_fisico: float | None = None       # TASK.phys_complete_pct (0–100), se informado
    tem_recurso: bool = False
    fonte: str = ""                       # rastreabilidade: arquivo › tabela › linha

    @property
    def marco(self) -> bool:
        return self.tipo in ("marco_inicio", "marco_fim")

    @property
    def no_calculo(self) -> bool:
        """LOE e resumo de EAP não entram na rede lógica (F1)."""
        return self.tipo not in ("loe", "resumo")


@dataclass
class Ligacao:
    pred: str
    succ: str
    tipo: str = "FS"
    lag_h: float = 0.0


@dataclass
class Projeto:
    id: str
    nome: str
    arquivo: str
    data_status: datetime | None = None
    inicio_plan: datetime | None = None
    termino_exigido: datetime | None = None      # "Must finish by"
    calendario_padrao: str = ""
    atividades: dict[str, Atividade] = field(default_factory=dict)
    ligacoes: list[Ligacao] = field(default_factory=list)
    calendarios: dict[str, Calendario] = field(default_factory=dict)
    alertas: list[str] = field(default_factory=list)
    origem: object | None = None                 # tabelas XER brutas, para exportar de volta

    @property
    def chave(self) -> str:
        return f"{self.arquivo}#{self.id}"

    @property
    def custo_total(self) -> float:
        return sum(a.custo for a in self.atividades.values())

    def cal(self, a: Atividade) -> Calendario:
        return (self.calendarios.get(a.calendario)
                or self.calendarios.get(self.calendario_padrao)
                or self.calendarios["_padrao"])
