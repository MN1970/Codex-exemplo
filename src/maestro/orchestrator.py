"""
Maestro OS v6.0 — Maestro Orchestrator
Orquestrador end-to-end: Detector → Fan-out → Consensus → Aggregate
"""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

from .detector import ComplexityDetector, DetectionResult
from .queue_executor import QueueExecutor, Task, TaskResult
from .consensus import ConsensusEngine, Candidate, Vote, ConsensusResult
from .parser import WorkflowDSL, Phase
from .episode_recorder import record_fan_out_episodes


@dataclass
class WorkflowExecution:
    """Execução de um workflow Maestro OS."""
    project_id: str
    workflow_id: str
    status: str                    # 'running', 'completed', 'failed'

    # Fases
    phase_1_detection: Optional[DetectionResult] = None
    phase_1_fan_out_results: Dict[str, TaskResult] = None

    phase_2_consensus_results: Dict[str, ConsensusResult] = None

    phase_3_aggregate_output: Optional[Dict[str, Any]] = None

    # Timing
    started_at: str = None
    completed_at: Optional[str] = None
    total_duration_secs: float = 0.0

    # Auditoria
    errors: List[str] = None

    def __post_init__(self):
        if self.phase_1_fan_out_results is None:
            self.phase_1_fan_out_results = {}
        if self.phase_2_consensus_results is None:
            self.phase_2_consensus_results = {}
        if self.errors is None:
            self.errors = []
        if self.started_at is None:
            self.started_at = datetime.utcnow().isoformat()


class MaestroOrchestrator:
    """
    Orquestrador central do Maestro OS v6.0.

    Fluxo end-to-end:
    1. Phase 1 Detection: Analisar projeto → identificar 8-16 agentes
    2. Phase 1 Fan-out: Invocar agentes em paralelo (max 8 simultâneos)
    3. Phase 2 Consensus: Coletar propostas, votar 3/5, resolver conflitos
    4. Phase 3 Aggregate: Consolidar outputs em DOCX/JSON/Matrix
    """

    def __init__(
        self,
        escalation_email: Optional[str] = None,
        token_budget: Optional[int] = None
    ):
        """
        Inicializa orquestrador.

        Args:
            escalation_email: Email para escalações (default: maestro@manta.local)
            token_budget: Budget de tokens total (calculado dinamicamente se None)
        """
        self.detector = ComplexityDetector()
        self.queue_executor = QueueExecutor(escalation_email)
        self.consensus_engine = ConsensusEngine(escalation_email)
        self.escalation_email = escalation_email or "maestro@manta.local"
        self.token_budget = token_budget

    async def execute_workflow(
        self,
        workflow: WorkflowDSL,
        project_description: str
    ) -> WorkflowExecution:
        """
        Executa workflow Maestro OS completo.

        Args:
            workflow: WorkflowDSL (AST parsed)
            project_description: Descrição do projeto (para detector)

        Returns:
            WorkflowExecution com resultados de todas fases
        """
        execution = WorkflowExecution(
            project_id=workflow.project.id,
            workflow_id=f"{workflow.project.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        try:
            # Phase 1: Detection
            print(f"\n[MAESTRO] Fase 1: Detecção para projeto '{workflow.project.title}'")
            detection = self.detector.detect(project_description)
            execution.phase_1_detection = detection
            print(f"[MAESTRO] Detectado: {detection.complexity_level.value} "
                  f"({detection.total_agents} agentes, {detection.token_budget}k tokens)")

            # Phase 1: Fan-out (paralelo)
            if workflow.phase_1_fan_out:
                print(f"\n[MAESTRO] Fase 1b: Fan-out ({len(workflow.phase_1_fan_out.agents)} agentes)")
                fan_out_results = await self._execute_fan_out(
                    workflow.phase_1_fan_out,
                    detection
                )
                execution.phase_1_fan_out_results = fan_out_results

            # Phase 2: Consensus
            if workflow.phase_2_consensus:
                print(f"\n[MAESTRO] Fase 2: Consenso ({len(workflow.phase_2_consensus.decisions)} decisões)")
                consensus_results = await self._execute_consensus(
                    workflow.phase_2_consensus,
                    workflow.agents,
                    execution.phase_1_fan_out_results
                )
                execution.phase_2_consensus_results = consensus_results

            # Phase 3: Aggregate
            if workflow.phase_3_aggregate:
                print(f"\n[MAESTRO] Fase 3: Agregação")
                aggregate_output = await self._execute_aggregate(
                    workflow.phase_3_aggregate,
                    execution
                )
                execution.phase_3_aggregate_output = aggregate_output

            execution.status = "completed"
            execution.completed_at = datetime.utcnow().isoformat()

        except Exception as e:
            execution.status = "failed"
            execution.errors.append(f"Workflow falhou: {str(e)}")
            print(f"[MAESTRO] ✗ Erro: {e}")

        return execution

    async def _execute_fan_out(
        self,
        fan_out_phase,
        detection: DetectionResult
    ) -> Dict[str, TaskResult]:
        """
        Executa Phase 1: Fan-out (invocar 8-16 agentes em paralelo).

        Args:
            fan_out_phase: FanOutPhase com agentes e prompts
            detection: Resultado da detecção

        Returns:
            Dict {agent_name: TaskResult}
        """
        # Selecionar agentes: usar detecção + fase declarada
        agents_to_invoke = list(set(
            detection.agents_selected +
            fan_out_phase.agents
        ))

        print(f"[FAN-OUT] Invocando {len(agents_to_invoke)} agentes:")
        for agent in agents_to_invoke:
            print(f"  - {agent}")

        # Criar tarefas
        tasks = []
        for i, agent_name in enumerate(agents_to_invoke):
            prompt = fan_out_phase.prompts.get(
                agent_name,
                f"Analisar projeto conforme especialidade: {agent_name}"
            )

            task = Task(
                task_id=f"task-{i+1}",
                agent_name=agent_name,
                prompt=prompt,
                context=fan_out_phase.shared_context
            )
            tasks.append(task)

        # Executar com queue executor
        results = await self.queue_executor.execute_all(tasks)

        # Log resumo
        summary = self.queue_executor.get_results_summary()
        print(f"[FAN-OUT] Resumo: {summary['completed']} completadas, "
              f"{summary['failed']} falhadas")

        # Telemetria/aprendizado: grava 1 episódio por tarefa em agent_episodes
        # (best-effort — no-op se Supabase não estiver configurado; ver
        # src/maestro/supabase_client.py e episode_recorder.py)
        record_fan_out_episodes(tasks, results, task_type="fan_out")

        return results

    async def _execute_consensus(
        self,
        consensus_phase,
        agents,
        fan_out_results: Dict[str, TaskResult]
    ) -> Dict[str, ConsensusResult]:
        """
        Executa Phase 2: Consenso (votação 3/5).

        Args:
            consensus_phase: ConsensusPhas com decisões
            agents: Lista de todos agentes declarados
            fan_out_results: Resultados da fan-out

        Returns:
            Dict {aspect: ConsensusResult}
        """
        results = {}

        for decision in consensus_phase.decisions:
            print(f"\n[CONSENSUS] Votando: {decision.aspect}")

            # Simular coleta de candidatos dos agentes
            candidates = [
                Candidate(
                    agent_name=c.get("agent", "unknown"),
                    value=c.get("value", "unknown"),
                    confidence=c.get("confidence", 0.5),
                    reasoning=c.get("reasoning", "")
                )
                for c in decision.candidates
            ]

            # Simular coleta de votos
            votes = [
                Vote(
                    agent_name=candidate.agent_name,
                    candidate_value=candidate.value,
                    confidence_in_vote=candidate.confidence,
                    reasoning=candidate.reasoning
                )
                for candidate in candidates
            ]

            # Determinar votantes relevantes
            voter_names = self.consensus_engine.determine_relevant_voters(
                aspect=decision.aspect,
                available_agents=[a.name for a in agents],
                candidates=candidates
            )

            print(f"  Votantes relevantes: {', '.join(voter_names)}")

            # Executar votação
            consensus_result = self.consensus_engine.execute_vote(
                aspect=decision.aspect,
                candidates=candidates,
                votes=votes
            )

            results[decision.aspect] = consensus_result

            # Log resultado
            print(f"  Status: {consensus_result.status.value}")
            if consensus_result.status.value == "decided":
                print(f"  Consenso: {consensus_result.consensus_value} "
                      f"(confiança {consensus_result.consensus_confidence:.1%})")
            elif consensus_result.status.value == "escalated":
                print(f"  Escalado para {consensus_result.escalation_to}")

        return results

    async def _execute_aggregate(
        self,
        aggregate_phase,
        execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """
        Executa Phase 3: Agregação (consolidar outputs).

        Args:
            aggregate_phase: AggregatePhase com formato e sections
            execution: Execução até agora

        Returns:
            Dict com outputs (DOCX path, JSON, etc)
        """
        outputs = {
            "format": aggregate_phase.format,
            "path": aggregate_phase.output_path,
        }

        if aggregate_phase.format == "docx":
            docx_path = f"{aggregate_phase.output_path}/consolidated.docx"
            print(f"[AGGREGATE] Gerando DOCX: {docx_path}")
            outputs["docx_path"] = docx_path

        if aggregate_phase.also_output == "json":
            json_path = f"{aggregate_phase.output_path}/consolidated.json"
            print(f"[AGGREGATE] Gerando JSON: {json_path}")
            outputs["json_path"] = json_path

        # Simular consolidação
        outputs["sections"] = len(aggregate_phase.sections)
        outputs["save_audit_trail"] = aggregate_phase.save_decision_trail

        return outputs

    def format_execution_summary(self, execution: WorkflowExecution) -> str:
        """Formata resumo legível da execução."""
        lines = [
            f"=== WORKFLOW EXECUTION SUMMARY ===",
            f"ID: {execution.workflow_id}",
            f"Status: {execution.status}",
            f"",
            "PHASE 1: Detection",
        ]

        if execution.phase_1_detection:
            d = execution.phase_1_detection
            lines.extend([
                f"  Complexity: {d.complexity_level.value}",
                f"  Agents detected: {d.total_agents}",
                f"  Token budget: {d.token_budget}k",
            ])

        lines.extend([
            "",
            "PHASE 1b: Fan-out",
            f"  Tasks executed: {len(execution.phase_1_fan_out_results)}",
        ])

        lines.extend([
            "",
            "PHASE 2: Consensus",
            f"  Decisions: {len(execution.phase_2_consensus_results)}",
        ])

        if execution.phase_2_consensus_results:
            decided = sum(1 for r in execution.phase_2_consensus_results.values()
                         if r.status.value == "decided")
            escalated = sum(1 for r in execution.phase_2_consensus_results.values()
                           if r.status.value == "escalated")
            lines.append(f"  - Decided: {decided}")
            lines.append(f"  - Escalated: {escalated}")

        lines.extend([
            "",
            "PHASE 3: Aggregate",
        ])

        if execution.phase_3_aggregate_output:
            lines.extend([
                f"  Format: {execution.phase_3_aggregate_output.get('format', 'N/A')}",
                f"  Sections: {execution.phase_3_aggregate_output.get('sections', 0)}",
                f"  Path: {execution.phase_3_aggregate_output.get('path', 'N/A')}",
            ])

        if execution.errors:
            lines.append(f"\nERRORS: {len(execution.errors)}")
            for error in execution.errors:
                lines.append(f"  - {error}")

        return "\n".join(lines)
