"""
Roteador Inteligente — Maestro (Manta 00) v4.3
Classifica tarefas e detecta oportunidades de paralelismo automaticamente.
"""

import asyncio
from typing import List, Dict, Any
from enum import Enum

from orchestrator import AgentTask, AgentType


class TaskType(Enum):
    """Tipos de tarefas reconhecidas pelo Maestro"""
    CLASSIFICACAO = "classify"  # Haiku — rápido
    ANALISE = "analysis"  # Sonnet — equilibrado
    REASONING = "reasoning"  # Opus — preciso
    DD = "due_diligence"  # Opus + Batch API
    INTEGRACAO = "integration"  # Múltiplos agentes


class MaestroRouter:
    """
    Maestro inteligente que:
    1. Roteia para agente correto (S6-S10)
    2. Detecta paralelismo (múltiplas docs independentes)
    3. Detecta padrão DD (múltiplos documentos, Opus)
    4. Sugere modelo otimizado (Haiku/Sonnet/Opus)
    """

    def __init__(self, client):
        self.client = client
        self.routing_keywords = {
            "S8": ["saneamento", "eta", "ete", "esgoto", "água", "drenagem", "aySA"],
            "S9": ["energia", "transmissão", "lt", "subestação", "aneel", "ons", "upe"],
            "S6": ["porto", "terminal", "antaq", "dragagem", "molhe", "contêiner"],
            "S7": ["aeroporto", "pista", "tps", "anac", "rbac", "icao"],
            "S10": ["barragem", "rejeitos", "cfrd", "icold", "pnsb"]
        }

    async def route(self, tasks: List[AgentTask]) -> List[AgentTask]:
        """
        Analisar tarefas e retornar versão otimizada.

        Realiza:
        1. Detecção de paralelismo
        2. Seleção de modelo otimizado
        3. Sugestão de Batch API
        """
        optimized_tasks = []

        for task in tasks:
            # 1. Classificar tipo de tarefa
            task_type = self._classify_task(task)

            # 2. Selecionar modelo otimizado
            model = self._select_model(task_type, len(task.documents))

            # 3. Detectar paralelismo
            parallelizable = len(task.documents) > 1

            # 4. Retornar tarefa otimizada
            optimized_task = AgentTask(
                agent_type=task.agent_type,
                documents=task.documents,
                context=task.context,
                parallelizable=parallelizable,
                model=model,
                max_tokens=task.max_tokens
            )
            optimized_tasks.append(optimized_task)

        return optimized_tasks

    def _classify_task(self, task: AgentTask) -> TaskType:
        """Classificar tipo de tarefa (Haiku? Sonnet? Opus?)"""
        doc_count = len(task.documents)
        doc_size = sum(len(d) for d in task.documents)

        # Heurística: DD é muitos docs ou docs grandes
        if doc_count >= 10 or doc_size > 100_000:
            return TaskType.DD

        # Heurística: classificação é curta
        if doc_size < 5_000:
            return TaskType.CLASSIFICACAO

        # Heurística: múltiplos docs = análise
        if doc_count > 1:
            return TaskType.ANALISE

        # Default: análise
        return TaskType.ANALISE

    def _select_model(self, task_type: TaskType, doc_count: int) -> str:
        """Selecionar modelo otimizado para tipo de tarefa"""
        if task_type == TaskType.CLASSIFICACAO:
            return "haiku"  # ⚡ 15x mais rápido, ideal para roteamento

        elif task_type == TaskType.DD:
            return "opus"  # 🧠 Preciso para due diligence

        elif task_type == TaskType.ANALISE and doc_count > 3:
            return "sonnet"  # ⚖️ Bom balanço custo/qualidade

        else:
            return "sonnet"  # Default seguro

    def get_routing_rules(self) -> Dict[str, List[str]]:
        """Retornar regras de roteamento (para debug)"""
        return self.routing_keywords

    def print_analysis(self, tasks: List[AgentTask]) -> None:
        """Imprimir análise de roteamento"""
        print("\n🎯 ANÁLISE DE ROTEAMENTO — Maestro")
        print("="*60)
        for i, task in enumerate(tasks, 1):
            task_type = self._classify_task(task)
            model = self._select_model(task_type, len(task.documents))
            print(f"{i}. {task.agent_type.value}")
            print(f"   Docs:          {len(task.documents)}")
            print(f"   Tipo:          {task_type.value}")
            print(f"   Modelo:        {model}")
            print(f"   Paralelismo:   {'✅ Sim' if len(task.documents) > 1 else '❌ Não'}")
            print()
        print("="*60 + "\n")


# Exemplo de uso
if __name__ == "__main__":
    import anthropic

    client = anthropic.Anthropic()
    router = MaestroRouter(client)

    tasks = [
        AgentTask(
            agent_type=AgentType.SANEAMENTO,
            documents=["ETA 1", "ETA 2", "ETA 3"],  # 3 docs = paralelizável
            model="sonnet"
        ),
        AgentTask(
            agent_type=AgentType.ENERGIA,
            documents=["Pergunta curta?"],  # 1 doc curto = Haiku
            model="sonnet"
        ),
    ]

    # Analisar roteamento
    # optimized = asyncio.run(router.route(tasks))
    # router.print_analysis(optimized)
