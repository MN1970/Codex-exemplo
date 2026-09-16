"""
Integration test for Maestro OS v6.0 Phase A (Core)
Tests: consensus, queue_executor, parser, orchestrator
"""

import asyncio
import pytest
from src.maestro.parser import WorkflowParser
from src.maestro.consensus import ConsensusEngine, Candidate, Vote, ConsensusStatus
from src.maestro.queue_executor import QueueExecutor, Task, TaskStatus
from src.maestro.orchestrator import MaestroOrchestrator


# Sample YAML workflow for testing
SAMPLE_WORKFLOW_YAML = """
project:
  id: test-porto-energia
  type: multi_segment
  title: Porto Terminal + Subestação
  location: Paranaguá, PR
  budget_range: 250M+
  segments: [S7, S10]

agents:
  - name: agente-portos
    tier: sonnet
    rag_prefix: por:
  - name: agente-energia
    tier: sonnet
    rag_prefix: ene:
  - name: manta-05-orcamento
    tier: sonnet
  - name: manta-07-cronograma
    tier: sonnet
  - name: manta-15-advisory
    tier: sonnet

phase_1_fan_out:
  agents: [agente-portos, agente-energia, manta-05-orcamento]
  shared_context:
    project_id: test-porto-energia
    deadline: 2026-08-15
  prompts:
    agente-portos: Analisar terminal portuário em Paranaguá
    agente-energia: Analisar subestação 230kV
    manta-05-orcamento: Consolidar orçamento

phase_2_consensus:
  decision_1:
    aspect: orçamento
    candidates:
      - agent: agente-portos
        value: 500_000_000
        confidence: 0.85
        reasoning: Cais novo 1.2km, dragagem
      - agent: agente-energia
        value: 450_000_000
        confidence: 0.78
        reasoning: SE 230kV, equipamentos caros
      - agent: manta-05-orcamento
        value: 1_000_000_000
        confidence: 0.88
        reasoning: Consolidado total

phase_3_aggregate:
  format: docx
  output_path: /tmp/maestro-test-output
  sections:
    - title: Escopo Integrado
      content: Porto + Energia em Paranaguá
    - title: Orçamento Consolidado
      content: R$ 1.0B consolidado
"""


class TestWorkflowParser:
    """Testa parser YAML."""

    def test_parse_sample_workflow(self):
        """Parse workflow YAML válido."""
        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)

        assert workflow.project.id == "test-porto-energia"
        assert workflow.project.type == "multi_segment"
        assert len(workflow.agents) == 5
        assert workflow.phase_1_fan_out is not None
        assert workflow.phase_2_consensus is not None
        assert workflow.phase_3_aggregate is not None

    def test_validate_workflow(self):
        """Valida workflow."""
        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)
        errors = parser.validate(workflow)

        assert errors == {} or not any(errors.values()), f"Erros: {errors}"

    def test_workflow_summary(self):
        """Formata sumário do workflow."""
        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)
        summary = parser.format_workflow_summary(workflow)

        assert "Porto Terminal" in summary
        assert "5" in summary  # 5 agents


class TestConsensusEngine:
    """Testa motor de consenso."""

    def test_consensus_super_majority(self):
        """Testa votação 3/5 com maioria."""
        engine = ConsensusEngine()

        # 3 candidatos
        candidates = [
            Candidate("agente-portos", 500_000_000, 0.85),
            Candidate("agente-energia", 450_000_000, 0.78),
            Candidate("manta-05", 1_000_000_000, 0.88),
        ]

        # 5 votos (3 para agente-portos)
        votes = [
            Vote("agente-portos", 500_000_000, 0.85, "Realistic"),
            Vote("agente-energia", 500_000_000, 0.78, "Agree with portos"),
            Vote("manta-05", 1_000_000_000, 0.88, "Own estimate"),
            Vote("manta-07", 500_000_000, 0.80, "Aligns with portos"),
            Vote("manta-15", 900_000_000, 0.75, "Middle estimate"),
        ]

        result = engine.execute_vote("orçamento", candidates, votes)

        assert result.status == ConsensusStatus.DECIDED
        assert result.consensus_value == 500_000_000
        assert result.votes_for_winner == 3

    def test_consensus_escalation(self):
        """Testa escalação quando sem maioria."""
        engine = ConsensusEngine()

        candidates = [
            Candidate("agente-portos", 500_000_000, 0.85),
            Candidate("agente-energia", 450_000_000, 0.78),
        ]

        # 5 votos (2 para portos, 3 dispersos - sem maioria)
        votes = [
            Vote("agente-portos", 500_000_000, 0.85),
            Vote("agente-energia", 450_000_000, 0.78),
            Vote("manta-05", 550_000_000, 0.80),
            Vote("manta-07", 480_000_000, 0.75),
            Vote("manta-15", 520_000_000, 0.70),
        ]

        result = engine.execute_vote("orçamento", candidates, votes)

        assert result.status == ConsensusStatus.ESCALATED
        assert result.escalation_to is not None

    def test_subset_relevant_voters(self):
        """Testa seleção de votantes subset-relevantes."""
        engine = ConsensusEngine()

        available = [
            "agente-portos", "agente-energia", "manta-05-orcamento",
            "manta-07-cronograma", "manta-15-advisory"
        ]

        candidates = [
            Candidate("agente-portos", 500_000_000, 0.85),
            Candidate("agente-energia", 450_000_000, 0.78),
        ]

        voters = engine.determine_relevant_voters("orçamento", available, candidates)

        # Deve incluir candidatos + especialistas de orçamento
        assert "agente-portos" in voters
        assert "agente-energia" in voters
        assert "manta-05-orcamento" in voters


class TestQueueExecutor:
    """Testa executor de fila."""

    @pytest.mark.asyncio
    async def test_queue_executor_basic(self):
        """Executa tarefas simples com queue executor."""
        executor = QueueExecutor()

        tasks = [
            Task(f"task-{i}", f"agente-{i}", f"Prompt {i}")
            for i in range(1, 4)
        ]

        results = await executor.execute_all(tasks)

        assert len(results) == 3
        summary = executor.get_results_summary()
        assert summary["total"] == 3
        assert summary["completed"] > 0

    @pytest.mark.asyncio
    async def test_max_concurrent_workers(self):
        """Testa limite de 8 workers simultâneos."""
        executor = QueueExecutor()

        # Criar 16 tarefas
        tasks = [
            Task(f"task-{i}", f"agente-{i % 5}", f"Prompt {i}")
            for i in range(1, 17)
        ]

        results = await executor.execute_all(tasks)

        # Todas devem executar (mesmo com max 8 simultâneos)
        assert len(results) == 16


class TestMaestroOrchestrator:
    """Testa orquestrador end-to-end."""

    @pytest.mark.asyncio
    async def test_orchestrator_full_workflow(self):
        """Executa workflow completo Maestro OS."""
        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)

        orchestrator = MaestroOrchestrator()

        execution = await orchestrator.execute_workflow(
            workflow,
            "Projeto Porto Terminal Paranaguá + Subestação Energia"
        )

        assert execution.status == "completed"
        assert execution.phase_1_detection is not None
        assert len(execution.phase_1_fan_out_results) > 0
        assert len(execution.phase_2_consensus_results) > 0

    @pytest.mark.asyncio
    async def test_orchestrator_summary(self):
        """Testa formatação de sumário da execução."""
        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)

        orchestrator = MaestroOrchestrator()
        execution = await orchestrator.execute_workflow(
            workflow,
            "Test project"
        )

        summary = orchestrator.format_execution_summary(execution)

        assert "WORKFLOW EXECUTION SUMMARY" in summary
        assert "completed" in summary.lower() or "failed" in summary.lower()
        assert "PHASE 1:" in summary
        assert "PHASE 2:" in summary
        assert "PHASE 3:" in summary


class TestPhaseAIntegration:
    """Testes de integração Phase A (Core)."""

    def test_parser_to_detector_integration(self):
        """Valida fluxo: parse YAML → detectar agentes."""
        from src.maestro.detector import ComplexityDetector

        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)

        detector = ComplexityDetector()
        project_desc = f"{workflow.project.title} - segmentos: {', '.join(workflow.project.segments)}"
        detection = detector.detect(project_desc)

        # Deve detectar S7 (portos) e S10 (energia)
        assert len(detection.segments_detected) >= 2

    @pytest.mark.asyncio
    async def test_full_phase_a_flow(self):
        """Testa fluxo completo de Phase A."""
        # 1. Parse
        parser = WorkflowParser()
        workflow = parser.parse(SAMPLE_WORKFLOW_YAML)
        assert workflow is not None

        # 2. Validate
        errors = parser.validate(workflow)
        assert not any(errors.values())

        # 3. Detect
        from src.maestro.detector import ComplexityDetector
        detector = ComplexityDetector()
        detection = detector.detect(workflow.project.title)
        assert detection.total_agents >= 8

        # 4. Queue & Execute
        executor = QueueExecutor()
        tasks = [
            Task(f"t{i}", agent, f"Prompt for {agent}")
            for i, agent in enumerate(workflow.phase_1_fan_out.agents)
        ]
        results = await executor.execute_all(tasks)
        assert len(results) > 0

        # 5. Consensus
        engine = ConsensusEngine()
        if workflow.phase_2_consensus:
            decision = workflow.phase_2_consensus.decisions[0]
            candidates = [
                Candidate(c["agent"], c["value"], c["confidence"])
                for c in decision.candidates
            ]
            votes = [
                Vote(c.agent_name, c.value, c.confidence)
                for c in candidates
            ]
            consensus = engine.execute_vote(decision.aspect, candidates, votes)
            assert consensus.status is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
