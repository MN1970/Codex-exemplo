"""
Maestro OS v6.0 — What-If Scenario Simulator
Impact analysis: delay, budget overrun, risk changes.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ScenarioType(Enum):
    """Tipo de cenário simulado."""
    DELAY = "delay"               # Atrasos na execução
    BUDGET_OVERRUN = "budget_overrun"  # Aumento de custo
    RISK_ESCALATION = "risk_escalation"  # Aumento de risco
    RESOURCE_LOSS = "resource_loss"  # Perda de recurso (agente, especialista)
    COMBINED = "combined"         # Múltiplos cenários


@dataclass
class Scenario:
    """Um cenário para simulação."""
    scenario_id: str
    type: ScenarioType
    name: str
    description: str

    # Parâmetros do cenário
    delay_days: Optional[int] = None
    budget_increase_pct: Optional[float] = None
    risk_increase_pct: Optional[float] = None
    affected_agent: Optional[str] = None  # Ex: 'agente-portos'


@dataclass
class ScenarioResult:
    """Resultado de um cenário simulado."""
    scenario: Scenario
    base_duration_min: int
    new_duration_min: int
    duration_increase_pct: float

    base_cost: float
    new_cost: float
    cost_increase_pct: float

    base_risk: float
    new_risk: float
    risk_increase_pct: float

    critical_path_impact: str  # Qual atividade crítica afetada
    recommendation: str


class DelayAnalyzer:
    """
    Analisador de atrasos em cascata.

    Modela como atraso em uma atividade/agente afeta o projeto todo.

    Exemplo:
    - Dragagem (S7) atrasada 3 meses
    - Fundação SE (S10) depende de conclusão dragagem
    - Total delay: 3 meses (paralelo permite overlap parcial)
    """

    # Mapeamento de dependências entre segmentos
    SEGMENT_DEPENDENCIES = {
        "S7": ["S10"],  # Portos → precisa estar pronto para energia
        "S10": ["S9"],  # Energia → precisa cais/obra para ligar
        "S9": ["S7"],   # Saneamento → usa captação próxima ao porto
    }

    def analyze_delay(
        self,
        base_duration_min: int,
        delayed_segment: str,
        delay_days: int,
        segments_involved: List[str]
    ) -> Tuple[int, str]:
        """
        Simula impacto de atraso em cascata.

        Args:
            base_duration_min: Duração base em minutos
            delayed_segment: Segmento atrasado (ex: 'S7')
            delay_days: Dias de atraso
            segments_involved: Todos segmentos do projeto

        Returns:
            (new_duration_min, impact_description)
        """
        delay_mins = delay_days * 24 * 60  # Converter para minutos

        # Identificar segmentos dependentes
        dependent = self.SEGMENT_DEPENDENCIES.get(delayed_segment, [])
        affected_segments = [s for s in dependent if s in segments_involved]

        # Em paralelismo: atraso não é 100% transmitido (pode haver overlap)
        # Regra empírica: 70% do atraso transmite em cascata
        cascading_delay = delay_mins * 0.7 if affected_segments else delay_mins

        new_duration = base_duration_min + cascading_delay

        impact = (
            f"Atraso de {delay_days}d no {delayed_segment} "
            f"impacta {len(affected_segments)} segmento(s) "
            f"(+{cascading_delay:.0f} min de atraso em cascata)"
        )

        return int(new_duration), impact


class BudgetAnalyzer:
    """
    Analisador de impacto orçamentário.

    Modela:
    - Overrun por atraso (overhead de mobilização)
    - Aumento de custo por risco (contingência)
    - Economia por paralelismo
    """

    # Overhead por atraso (%)
    DELAY_OVERHEAD_PCT = 0.05  # 5% por mês de atraso

    # Multiplicador de contingência por risco
    RISK_CONTINGENCY = {
        "low": 0.10,      # 10% para baixo risco
        "medium": 0.20,   # 20% para médio risco
        "high": 0.35,     # 35% para alto risco
    }

    def analyze_budget_impact(
        self,
        base_cost: float,
        delay_days: int,
        risk_level: str,
        is_parallel: bool = True
    ) -> Tuple[float, str]:
        """
        Simula impacto de atraso e risco no orçamento.

        Args:
            base_cost: Custo base
            delay_days: Dias de atraso
            risk_level: 'low', 'medium', 'high'
            is_parallel: Se execução é paralela (reduz overhead)

        Returns:
            (new_cost, impact_description)
        """
        new_cost = base_cost

        # Overhead por atraso
        months_delayed = delay_days / 30
        delay_overhead = months_delayed * self.DELAY_OVERHEAD_PCT
        if not is_parallel:
            delay_overhead *= 1.5  # Serial sofre mais com atraso

        new_cost *= (1 + delay_overhead)

        # Contingência por risco
        contingency = self.RISK_CONTINGENCY.get(risk_level, 0.15)
        new_cost *= (1 + contingency)

        pct_increase = ((new_cost - base_cost) / base_cost) * 100

        impact = (
            f"Atraso {delay_days}d: +{delay_overhead*100:.1f}% | "
            f"Risco {risk_level}: +{contingency*100:.0f}% contingência | "
            f"Total: +{pct_increase:.1f}%"
        )

        return new_cost, impact


class RiskSimulator:
    """
    Simulador de risco.

    Modela como mudanças em projeto aumentam risco total.
    """

    # Fatores que aumentam risco
    RISK_FACTORS = {
        "delay": 0.02,                # 2% por dia de atraso
        "budget_overrun": 0.03,       # 3% por 10% de overrun
        "geotechnical": 0.25,         # +25% se risco geotécnico
        "environmental": 0.15,        # +15% se restrição ambiental
    }

    def simulate_risk_change(
        self,
        base_risk: float,
        delay_days: int = 0,
        budget_increase_pct: float = 0.0,
        has_geotechnical_risk: bool = False
    ) -> Tuple[float, str]:
        """
        Simula mudança de risco total.

        Args:
            base_risk: Risco base (0–1)
            delay_days: Dias de atraso
            budget_increase_pct: % de aumento orçamentário
            has_geotechnical_risk: Se tem risco geotécnico

        Returns:
            (new_risk, factors_applied)
        """
        risk_delta = 0.0
        factors_applied = []

        # Atraso
        if delay_days > 0:
            delay_factor = min(delay_days * self.RISK_FACTORS["delay"], 0.2)
            risk_delta += delay_factor
            factors_applied.append(f"Atraso {delay_days}d: +{delay_factor*100:.1f}%")

        # Budget overrun
        if budget_increase_pct > 0:
            budget_factor = (budget_increase_pct / 10.0) * self.RISK_FACTORS["budget_overrun"]
            risk_delta += budget_factor
            factors_applied.append(f"Budget +{budget_increase_pct:.0f}%: +{budget_factor*100:.1f}%")

        # Geotechnical
        if has_geotechnical_risk:
            geo_factor = self.RISK_FACTORS["geotechnical"]
            risk_delta += geo_factor
            factors_applied.append(f"Risco geotécnico: +{geo_factor*100:.1f}%")

        new_risk = min(base_risk + risk_delta, 1.0)  # Cap at 100%
        pct_change = ((new_risk - base_risk) / max(base_risk, 0.01)) * 100

        return new_risk, " | ".join(factors_applied)


class WhatIfSimulator:
    """
    Simulador de cenários "e se...?".

    Coordena:
    - DelayAnalyzer (atrasos em cascata)
    - BudgetAnalyzer (impacto orçamentário)
    - RiskSimulator (mudança de risco)

    Exemplo:
    "E se o atraso da dragagem for 2 meses?"
    → Calcula impacto em cronograma, orçamento, risco
    """

    def __init__(self):
        self.delay_analyzer = DelayAnalyzer()
        self.budget_analyzer = BudgetAnalyzer()
        self.risk_simulator = RiskSimulator()

    def simulate_scenario(
        self,
        base_duration_min: int,
        base_cost: float,
        base_risk: float,
        scenario: Scenario,
        segments_involved: List[str],
        risk_level: str = "medium"
    ) -> ScenarioResult:
        """
        Simula um cenário e retorna impactos.

        Args:
            base_duration_min: Duração base em minutos
            base_cost: Custo base em reais
            base_risk: Risco base (0–1)
            scenario: Cenário para simular
            segments_involved: Segmentos envolvidos
            risk_level: Nível de risco ('low', 'medium', 'high')

        Returns:
            ScenarioResult com comparações base vs novo
        """
        new_duration = base_duration_min
        new_cost = base_cost
        new_risk = base_risk
        impacts = []

        # Aplicar mudanças conforme tipo de cenário
        if scenario.type == ScenarioType.DELAY:
            if scenario.delay_days:
                new_duration, impact = self.delay_analyzer.analyze_delay(
                    base_duration_min,
                    scenario.affected_agent or "unknown",
                    scenario.delay_days,
                    segments_involved
                )
                impacts.append(impact)

                new_cost, cost_impact = self.budget_analyzer.analyze_budget_impact(
                    base_cost,
                    scenario.delay_days,
                    risk_level
                )
                impacts.append(cost_impact)

                new_risk, risk_impact = self.risk_simulator.simulate_risk_change(
                    base_risk,
                    delay_days=scenario.delay_days
                )
                impacts.append(risk_impact)

        elif scenario.type == ScenarioType.BUDGET_OVERRUN:
            if scenario.budget_increase_pct:
                new_cost = base_cost * (1 + scenario.budget_increase_pct / 100.0)
                impacts.append(f"Budget +{scenario.budget_increase_pct:.0f}% aplicado")

                new_risk, risk_impact = self.risk_simulator.simulate_risk_change(
                    base_risk,
                    budget_increase_pct=scenario.budget_increase_pct
                )
                impacts.append(risk_impact)

        elif scenario.type == ScenarioType.RISK_ESCALATION:
            if scenario.risk_increase_pct:
                new_risk = min(
                    base_risk * (1 + scenario.risk_increase_pct / 100.0),
                    1.0
                )
                impacts.append(f"Risco +{scenario.risk_increase_pct:.0f}% aplicado")

        # Calcular porcentagens
        duration_increase_pct = ((new_duration - base_duration_min) / base_duration_min) * 100
        cost_increase_pct = ((new_cost - base_cost) / base_cost) * 100
        risk_increase_pct = ((new_risk - base_risk) / max(base_risk, 0.01)) * 100

        # Gerar recomendação
        recommendation = self._generate_recommendation(
            scenario,
            duration_increase_pct,
            cost_increase_pct,
            risk_increase_pct
        )

        # Identificar critical path
        critical = "Cronograma" if duration_increase_pct > 10 else "Orçamento" if cost_increase_pct > 20 else "Risco"

        return ScenarioResult(
            scenario=scenario,
            base_duration_min=base_duration_min,
            new_duration_min=int(new_duration),
            duration_increase_pct=duration_increase_pct,
            base_cost=base_cost,
            new_cost=new_cost,
            cost_increase_pct=cost_increase_pct,
            base_risk=base_risk,
            new_risk=new_risk,
            risk_increase_pct=risk_increase_pct,
            critical_path_impact=critical,
            recommendation=recommendation
        )

    def _generate_recommendation(
        self,
        scenario: Scenario,
        duration_delta_pct: float,
        cost_delta_pct: float,
        risk_delta_pct: float
    ) -> str:
        """Gera recomendação baseada em impactos."""
        if duration_delta_pct > 20 or cost_delta_pct > 30:
            return "❌ Cenário crítico: buscar mitigação ou replanejar"
        elif duration_delta_pct > 10 or cost_delta_pct > 15:
            return "⚠️ Cenário preocupante: implementar plano de contingência"
        else:
            return "✓ Cenário aceitável: monitorar próximos marcos"

    def compare_scenarios(
        self,
        base_duration_min: int,
        base_cost: float,
        base_risk: float,
        scenarios: List[Scenario],
        segments_involved: List[str],
        risk_level: str = "medium"
    ) -> List[ScenarioResult]:
        """
        Simula múltiplos cenários e retorna comparação.

        Args:
            scenarios: Lista de cenários para simular

        Returns:
            Lista de ScenarioResult ordenada por impacto (maior impacto primeiro)
        """
        results = []

        for scenario in scenarios:
            result = self.simulate_scenario(
                base_duration_min,
                base_cost,
                base_risk,
                scenario,
                segments_involved,
                risk_level
            )
            results.append(result)

        # Ordenar por impacto total
        results.sort(
            key=lambda r: abs(r.duration_increase_pct) + abs(r.cost_increase_pct) + abs(r.risk_increase_pct),
            reverse=True
        )

        return results

    def format_comparison_report(
        self,
        base_duration_min: int,
        base_cost: float,
        base_risk: float,
        results: List[ScenarioResult]
    ) -> str:
        """Formata relatório de comparação de cenários."""
        lines = [
            "=== ANÁLISE DE CENÁRIOS (What-If) ===",
            "",
            f"Base:",
            f"  Duração: {base_duration_min} min ({base_duration_min/60:.1f}h)",
            f"  Custo: R$ {base_cost/1e6:.1f}M",
            f"  Risco: {base_risk*100:.0f}%",
            "",
        ]

        for i, result in enumerate(results, 1):
            lines.extend([
                f"{i}. {result.scenario.name}",
                f"   Duração: {result.new_duration_min}min ({result.duration_increase_pct:+.1f}%)",
                f"   Custo: R$ {result.new_cost/1e6:.1f}M ({result.cost_increase_pct:+.1f}%)",
                f"   Risco: {result.new_risk*100:.0f}% ({result.risk_increase_pct:+.1f}%)",
                f"   Crítico: {result.critical_path_impact}",
                f"   Recomendação: {result.recommendation}",
                "",
            ])

        return "\n".join(lines)
