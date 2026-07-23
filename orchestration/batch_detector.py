"""
Detector Automático de Batch API — Manta Maestro v4.3
Detecta quando usar Batch API para ganhar 50% de desconto.
"""

from typing import Dict, Any
from enum import Enum

from orchestrator import AgentTask


class BatchCriteria(Enum):
    """Critérios para usar Batch API"""
    VOLUME_ALTO = "high_volume"  # 100+ requisições
    DD_PATTERN = "due_diligence"  # Múltiplos docs para análise
    LATENCIA_OK = "latency_ok"  # Resultado não precisa imediato
    CUSTO_IMPORTA = "cost_matters"  # Tarefa repetitiva


class BatchDetector:
    """
    Detecta automaticamente quando usar Batch API.
    Batch API oferece 50% desconto mas latência é 30min-24h.

    Critérios para ativar:
    1. 100+ requisições independentes
    2. Padrão DD: múltiplos documentos, análise Opus
    3. Resultado não precisa imediato (noturno OK)
    """

    def __init__(self):
        self.batch_threshold_docs = 50  # Ativar se > 50 docs
        self.batch_threshold_tokens = 500_000  # Ativar se > 500K tokens
        self.dd_min_docs = 10  # DD pattern: 10+ docs

    def should_use_batch(self, task: AgentTask) -> bool:
        """
        Determinar se tarefa deve usar Batch API.

        Returns:
            True se vale a pena usar Batch API (50% desconto)
        """
        # Critério 1: Volume alto (100+ docs)
        if len(task.documents) >= self.batch_threshold_docs:
            return True

        # Critério 2: Padrão DD (Opus + múltiplos docs + grande volume)
        if self._is_dd_pattern(task):
            return True

        # Critério 3: Economia significativa em tokens
        estimated_tokens = self._estimate_tokens(task)
        if estimated_tokens > self.batch_threshold_tokens:
            return True

        return False

    def _is_dd_pattern(self, task: AgentTask) -> bool:
        """Detectar padrão DD (due diligence)"""
        # DD típico: 10+ documentos, modelo Opus, análise profunda
        is_opus = task.model == "opus"
        has_many_docs = len(task.documents) >= self.dd_min_docs
        high_max_tokens = task.max_tokens >= 3000

        return is_opus and has_many_docs and high_max_tokens

    def _estimate_tokens(self, task: AgentTask) -> int:
        """Estimar tokens da tarefa (heurística: 1 token ≈ 4 chars)"""
        total_chars = sum(len(doc) for doc in task.documents)
        return total_chars // 4

    def estimate_savings(self, task: AgentTask) -> Dict[str, Any]:
        """
        Estimar economia com Batch API para uma tarefa.

        Returns:
            Dict com estimativas de custo, tempo, desconto
        """
        estimated_tokens = self._estimate_tokens(task)
        use_batch = self.should_use_batch(task)

        # Preços (Opus): $5/1M input, $25/1M output
        input_cost = (estimated_tokens * 0.5) / 1_000_000
        output_tokens = estimated_tokens // 5  # Estimativa: output = 20% input
        output_cost = (output_tokens * 25) / 1_000_000

        total_cost = input_cost + output_cost
        batch_cost = total_cost * 0.5  # 50% desconto

        return {
            "should_use_batch": use_batch,
            "estimated_tokens": estimated_tokens,
            "sequential_cost": f"${total_cost:.4f}",
            "batch_cost": f"${batch_cost:.4f}",
            "savings": f"${total_cost - batch_cost:.4f}",
            "savings_pct": 50.0,
            "latency_sequential": "30-60s",
            "latency_batch": "30min-24h (noturno recomendado)"
        }

    def print_analysis(self, task: AgentTask) -> None:
        """Imprimir análise de Batch API para tarefa"""
        savings = self.estimate_savings(task)
        use_batch = savings["should_use_batch"]

        print("\n💰 ANÁLISE DE BATCH API")
        print("="*60)
        print(f"Tarefa:            {task.agent_type.value}")
        print(f"Documentos:        {len(task.documents)}")
        print(f"Tokens estimados:  {savings['estimated_tokens']:,}")
        print(f"\nCusto:")
        print(f"  Sequencial:      {savings['sequential_cost']}")
        print(f"  Batch API:       {savings['batch_cost']} (50% desconto)")
        print(f"  Economia:        {savings['savings']}")
        print(f"\nLatência:")
        print(f"  Sequencial:      {savings['latency_sequential']}")
        print(f"  Batch API:       {savings['latency_batch']}")
        print(f"\nRecomendação:      {'✅ USAR BATCH API' if use_batch else '❌ Usar sequencial'}")
        print("="*60 + "\n")


# Critérios por tipo de agente
BATCH_RECOMMENDATIONS = {
    "S8": {
        "min_docs": 15,  # DD de 15+ concessionárias
        "typical_model": "opus",
        "use_case": "DD de portfólio, análise SNIS em lote"
    },
    "S9": {
        "min_docs": 20,  # DD de leilões ANEEL
        "typical_model": "opus",
        "use_case": "Análise de 20+ leilões de transmissão"
    },
    "S6": {
        "min_docs": 10,  # DD de concessões portuárias
        "typical_model": "opus",
        "use_case": "Análise de viabilidade econômica"
    },
    "S7": {
        "min_docs": 20,  # DD de concessões aeroportuárias
        "typical_model": "opus",
        "use_case": "Análise de 20+ concessões regionais"
    },
    "S10": {
        "min_docs": 15,  # DD de portfólio de TSF
        "typical_model": "opus",
        "use_case": "DD integrada de 15+ barragens/TSF"
    }
}


# Exemplo de uso
if __name__ == "__main__":
    detector = BatchDetector()

    task = AgentTask(
        agent_type=AgentType.SANEAMENTO,
        documents=["Doc 1"] * 50,  # 50 docs
        model="opus",
        max_tokens=3000
    )

    # Analisar
    # detector.print_analysis(task)
