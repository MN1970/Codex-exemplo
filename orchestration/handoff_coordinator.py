"""
Coordenador de Handoff — Manta Maestro v4.3
Otimiza transições entre agentes (ex: S8 → Manta-05 orçamento → Manta-07 cronograma)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class HandoffType(Enum):
    """Tipos de handoff entre agentes"""
    S8_TO_ORCAMENTO = "saneamento_to_budget"  # ETA/ETE → quantitativos
    S8_TO_CRONOGRAMA = "saneamento_to_schedule"  # Projeto → cronograma
    S9_TO_ORCAMENTO = "energia_to_budget"  # LT → quantitativos
    S6_TO_ORCAMENTO = "portos_to_budget"  # Terminal → quantitativos
    QUALQUER_TO_ADVISORY = "any_to_advisory"  # Qualquer coisa → modelo financeiro


@dataclass
class HandoffData:
    """Dados transferidos no handoff"""
    source_agent: str  # S8, S9, etc
    target_agent: str  # Manta-05, Manta-07, etc
    analysis_result: str  # Resultado da análise
    inherited_cache: Optional[Dict[str, Any]] = None  # Cache do agente anterior
    context_tokens: int = 0  # Tokens já no cache

    def get_tokens_saved(self) -> int:
        """Tokens economizados por reutilizar contexto"""
        return self.context_tokens


class HandoffCoordinator:
    """
    Coordena handoffs entre agentes otimizando:
    1. Transferência de contexto cachado
    2. Reutilização de análises prévias
    3. Padrão de handoff (qual agente chama qual)
    """

    def __init__(self):
        self.handoff_rules = self._init_rules()
        self.handoff_history: List[HandoffData] = []
        self.total_tokens_saved = 0

    def _init_rules(self) -> Dict[str, List[str]]:
        """Definir regras de handoff automático"""
        return {
            # Após análise S8 (saneamento)
            "S8": [
                "Manta-05",  # Orçamento de ETA/ETE/redes
                "Manta-07",  # Cronograma de obra
                "Manta-15",  # Modelo financeiro de concessão
            ],
            # Após análise S9 (energia)
            "S9": [
                "Manta-05",  # Orçamento de LT/subestação
                "Manta-07",  # Cronograma de construção
                "Manta-15",  # Modelo financeiro (RAP, VPL, TIR)
            ],
            # Após análise S6 (portos)
            "S6": [
                "Manta-05",  # Orçamento de dragagem/cais
                "Manta-07",  # Cronograma de faseamento
                "Manta-15",  # Modelo financeiro de concessão
            ],
            # Após análise S7 (aeroportos)
            "S7": [
                "Manta-05",  # Orçamento de pista/terminal
                "Manta-07",  # Cronograma respeitando operação
                "Manta-15",  # Modelo financeiro de concessão
            ],
            # Após análise S10 (barragens)
            "S10": [
                "Manta-05",  # Orçamento de obra
                "Manta-07",  # Cronograma com janela seca
                "Manta-15",  # Modelo financeiro (UHE, PPP)
            ],
        }

    def suggest_next_agents(self, current_agent: str) -> List[str]:
        """
        Sugerir próximos agentes após análise.

        Args:
            current_agent: Agente atual (S8, S9, etc)

        Returns:
            Lista de agentes recomendados para handoff
        """
        return self.handoff_rules.get(current_agent, [])

    def prepare_handoff(
        self,
        source_agent: str,
        target_agent: str,
        analysis_result: str,
        inherited_cache: Optional[Dict[str, Any]] = None,
        context_tokens: int = 0
    ) -> HandoffData:
        """
        Preparar dados para handoff otimizado.

        Args:
            source_agent: Agente que fez análise
            target_agent: Agente que vai receber
            analysis_result: Resultado da análise
            inherited_cache: Contexto/cache do agente anterior
            context_tokens: Tokens no contexto compartilhado

        Returns:
            HandoffData pronto para o próximo agente
        """
        handoff = HandoffData(
            source_agent=source_agent,
            target_agent=target_agent,
            analysis_result=analysis_result,
            inherited_cache=inherited_cache,
            context_tokens=context_tokens
        )

        self.handoff_history.append(handoff)
        self.total_tokens_saved += context_tokens

        return handoff

    def get_handoff_summary(self) -> Dict[str, Any]:
        """Resumo de handoffs realizados"""
        if not self.handoff_history:
            return {
                "total_handoffs": 0,
                "total_tokens_saved": 0,
                "average_context_transfer": 0
            }

        contexts = [h.context_tokens for h in self.handoff_history]
        return {
            "total_handoffs": len(self.handoff_history),
            "total_tokens_saved": self.total_tokens_saved,
            "average_context_transfer": sum(contexts) / len(contexts) if contexts else 0,
            "handoff_chain": " → ".join([
                h.source_agent for h in self.handoff_history
            ] + [self.handoff_history[-1].target_agent] if self.handoff_history else [])
        }

    def print_handoff_graph(self) -> None:
        """Visualizar grafo de handoffs"""
        print("\n🔄 GRAFO DE HANDOFFS")
        print("="*60)

        for agent, next_agents in self.handoff_rules.items():
            print(f"\n{agent}")
            for next_agent in next_agents:
                print(f"  └─ → {next_agent}")

        print("\n" + "="*60)

    def print_history(self) -> None:
        """Imprimir histórico de handoffs"""
        if not self.handoff_history:
            print("Nenhum handoff realizado ainda.")
            return

        print("\n📊 HISTÓRICO DE HANDOFFS")
        print("="*60)

        for i, h in enumerate(self.handoff_history, 1):
            print(f"\n{i}. {h.source_agent} → {h.target_agent}")
            print(f"   Contexto herdado: {h.context_tokens:,} tokens")
            print(f"   Resultado: {h.analysis_result[:100]}...")

        summary = self.get_handoff_summary()
        print(f"\n📈 RESUMO")
        print(f"  Total de handoffs: {summary['total_handoffs']}")
        print(f"  Tokens economizados: {summary['total_tokens_saved']:,}")
        print(f"  Contexto médio: {summary['average_context_transfer']:.0f} tokens")
        print(f"  Cadeia: {summary['handoff_chain']}")
        print("="*60 + "\n")


# Exemplo de padrão de handoff típico
HANDOFF_PATTERNS = {
    "saneamento_completo": [
        ("S8", "Análise de ETA/ETE"),
        ("Manta-05", "Orçamento de construção"),
        ("Manta-07", "Cronograma de obra"),
        ("Manta-15", "Modelo financeiro"),
    ],
    "energia_completa": [
        ("S9", "Análise de LT/subestação"),
        ("Manta-05", "Orçamento"),
        ("Manta-07", "Cronograma de energização"),
        ("Manta-15", "Modelo financeiro (RAP)"),
    ],
    "porto_completo": [
        ("S6", "Análise de terminal/dragagem"),
        ("Manta-05", "Orçamento"),
        ("Manta-07", "Cronograma de faseamento"),
        ("Manta-15", "Modelo de concessão"),
    ]
}


if __name__ == "__main__":
    coordinator = HandoffCoordinator()

    # Sugerir próximos agentes
    print("Próximos agentes após S8:")
    print(coordinator.suggest_next_agents("S8"))

    # Preparar handoff
    handoff = coordinator.prepare_handoff(
        source_agent="S8",
        target_agent="Manta-05",
        analysis_result="ETA Riachuelo: 150 m³/s, CVC, orçamento ~R$ 250M",
        inherited_cache={"lei_14026": "..."},
        context_tokens=5000
    )

    # Visualizar
    coordinator.print_handoff_graph()
