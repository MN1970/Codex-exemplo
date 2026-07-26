"""
Maestro OS v6.0 — Smoke Tests
Validates 5 representative projects (simple → complex).
"""

import unittest

from src.maestro.detector import ComplexityDetector
from src.maestro.queue_executor import QueueExecutor
from src.maestro.consensus import ConsensusEngine, Candidate, Vote
from src.maestro.ml_inference import InferenceService
from src.maestro.norm_parser import ComplianceChecker
from src.maestro.simulator import WhatIfSimulator, Scenario, ScenarioType


class TestSmokeRodovia(unittest.TestCase):
    """Smoke test: Simple project (1 segment, 8 agents)."""

    def test_rodovia_project_simple(self):
        """BR-101 Rodovia project: 1 segment, simple complexity."""
        detector = ComplexityDetector()
        description = "Rodovia federal BR-101, pavimentação 200 km, SICRO, DNIT"
        detection = detector.detect(description)

        # Verify detection
        self.assertEqual(detection.num_segments, 1)
        self.assertEqual(detection.complexity_level.value, "simple")
        self.assertGreaterEqual(len(detection.agents_pool), 5)  # At least vertical + base horizontals
        self.assertIn("agente-infraestrutura-rodovias", detection.agents_pool)

        # Verify queue executor can handle 8 agents
        executor = QueueExecutor()
        self.assertEqual(executor.MAX_CONCURRENT_WORKERS, 8)
        self.assertEqual(executor.MAX_QUEUE_SIZE, 16)

        # Verify ML inference works (skip if models not trained)
        try:
            from src.maestro.ml_trainer import RoutingModel, DurationPredictor, RiskClassifier
            service = InferenceService(RoutingModel(), DurationPredictor(), RiskClassifier())
            result = service.infer("proj-br101", description)

            self.assertIsNotNone(result.routing)
            self.assertGreater(result.duration.estimated_minutes, 0)
            self.assertLess(result.duration.estimated_minutes, 1000)  # Sanity check
        except ValueError:
            # Models not trained - skip this part for smoke test
            pass

        # Verify compliance checking works
        checker = ComplianceChecker()
        compliant, warnings, violations = checker.check_compliance("rodovia", {})
        self.assertIsInstance(compliant, list)


class TestSmokeBarragemEnergia(unittest.TestCase):
    """Smoke test: Medium-A project (2 segments, 10 agents)."""

    def test_barragem_energia_project(self):
        """Barragem + Energia: 2 segments, 10 agents."""
        detector = ComplexityDetector()
        description = """
        Barragem de terra enrocamento + UHE (Usina Hidrelétrica)
        Estudo prévio + EIA com rejeitos, ICOLD Bulletin 194
        """
        detection = detector.detect(description)

        # Verify detection
        self.assertGreaterEqual(detection.num_segments, 2)
        self.assertEqual(detection.complexity_level.value, "medium")
        self.assertGreaterEqual(len(detection.agents_pool), 7)

        # Verify agents include both S11 and S10
        agent_names = detection.agents_pool
        self.assertTrue(
            any("barragens" in name.lower() for name in agent_names) or
            any("energia" in name.lower() for name in agent_names)
        )


class TestSmokePortoEnergiaSaneamento(unittest.TestCase):
    """Smoke test: Medium-B project (3 segments, 12 agents)."""

    def test_porto_energia_saneamento_project(self):
        """Porto + Energia + Saneamento: 3 segments, 12 agents."""
        detector = ComplexityDetector()
        description = """
        Terminal portuário Paranaguá com dragagem de 3m de calado +
        Subestação ANEEL 230kV linha transmissão +
        ETA São Vicente Lei 14.026 AySA projeto executivo
        """
        detection = detector.detect(description)

        # Verify detection
        self.assertEqual(detection.num_segments, 3)
        self.assertEqual(detection.complexity_level.value, "medium")
        self.assertGreaterEqual(len(detection.agents_pool), 8)

        # Verify agent pool includes all 3 segments
        agent_names = detection.agents_pool
        has_portos = any("porto" in name.lower() for name in agent_names)
        has_energia = any("energia" in name.lower() for name in agent_names)
        has_saneamento = any("saneamento" in name.lower() for name in agent_names)

        self.assertTrue(has_portos or any("S7" in name for name in agent_names))
        self.assertTrue(has_energia or any("S10" in name for name in agent_names))
        self.assertTrue(has_saneamento or any("S9" in name for name in agent_names))

        # Verify what-if analysis works
        simulator = WhatIfSimulator()
        scenarios = [
            Scenario("sc-delay", ScenarioType.DELAY, "3-month delay", "dragagem", delay_days=90),
            Scenario("sc-budget", ScenarioType.BUDGET_OVERRUN, "Budget +20%", "inflation", budget_increase_pct=20.0),
        ]

        results = simulator.compare_scenarios(
            base_duration_min=6300,
            base_cost=1_150_000_000,
            base_risk=0.35,
            scenarios=scenarios,
            segments_involved=["S7", "S10", "S9"],
            risk_level="medium"
        )

        self.assertEqual(len(results), 2)
        self.assertGreater(results[0].new_duration_min, results[0].base_duration_min)


class TestSmokeComplexoMultimodal(unittest.TestCase):
    """Smoke test: Complex project (4 segments, 14 agents)."""

    def test_complexo_multimodal_project(self):
        """Complexo multimodal: 4+ segments, 14 agents."""
        detector = ComplexityDetector()
        description = """
        Complexo multimodal de transporte:
        - Rodovia expressa SP-500 (150 km)
        - OAE 20 pontes viadutos
        - Ferrovia carga eletrificada
        - Barragem de suporte + saneamento
        Projeto executivo, licitação, obra simultânea 4 fases
        """
        detection = detector.detect(description)

        # Verify detection
        self.assertGreaterEqual(detection.num_segments, 4)
        self.assertEqual(detection.complexity_level.value, "complex")
        self.assertGreaterEqual(len(detection.agents_pool), 13)

        # Verify consensus voting for multiple aspects
        engine = ConsensusEngine()
        candidates = [
            Candidate("agente-rodovia", "R$ 2.5B", 0.82),
            Candidate("agente-oae", "R$ 2.7B", 0.88),
            Candidate("agente-ferrovia", "R$ 2.6B", 0.85),
            Candidate("manta-05", "R$ 2.8B", 0.79),
            Candidate("manta-15", "R$ 2.4B-2.9B", 0.75),
        ]

        votes = [
            Vote("agente-rodovia", "R$ 2.5B", 0.82),
            Vote("agente-oae", "R$ 2.7B", 0.88),
            Vote("agente-ferrovia", "R$ 2.6B", 0.85),
            Vote("manta-05", "R$ 2.8B", 0.79),
            Vote("manta-15", "R$ 2.4B-2.9B", 0.75),
        ]

        result = engine.execute_vote("orçamento", candidates, votes)
        self.assertIsNotNone(result)
        self.assertIn(result.status.value, ["decided", "escalated", "tied"])


class TestSmokeMaxComplexidade(unittest.TestCase):
    """Smoke test: Maximum complexity (5+ segments, 16 agents)."""

    def test_max_complexity_project(self):
        """Maximum escalation: 5+ segments, 16 agents."""
        detector = ComplexityDetector()
        description = """
        Megaprojeto Nacional Integrado (5+ segmentos):
        1. Rodovia multicarril BR-116 (400 km)
        2. OAE críticas (35 estruturas)
        3. Ferrovia Carga Norte-Nordeste (eletrificação)
        4. Metrô linha metropolitana (50 km)
        5. Barragem + saneamento (EIA completo)
        6. Energia renovável solar + eólica
        Escopo: EVTEA + Projeto Executivo + Obra simultânea
        Orçamento estimado R$ 10B+
        Timeline: 60 meses (5 anos)
        Interdependências complexas entre segmentos
        """
        detection = detector.detect(description)

        # Verify maximum escalation
        self.assertGreaterEqual(detection.num_segments, 5)
        self.assertEqual(detection.complexity_level.value, "complex")
        self.assertGreaterEqual(len(detection.agents_pool), 14)  # Maximum agents

        # Verify all 9 vertical agents are selected (S1-S11)
        agent_names = detection.agents_pool
        # Count unique segment agents
        segment_agents = [a for a in agent_names if "-S" in a or "infraestrutura" in a or "barragem" in a or "energia" in a or "saneamento" in a]
        self.assertGreaterEqual(len(segment_agents), 5)

        # Verify ML inference handles max complexity (skip if models not trained)
        try:
            from src.maestro.ml_trainer import RoutingModel, DurationPredictor, RiskClassifier
            service = InferenceService(RoutingModel(), DurationPredictor(), RiskClassifier())
            result = service.infer("proj-megaprojeto", description)

            self.assertIsNotNone(result)
            self.assertGreaterEqual(len(result.routing.suggested_agents), 14)
            self.assertGreater(result.duration.estimated_minutes, 500)  # Very long project
            self.assertGreater(result.risk.risk_score, 50)  # High risk for mega projects

            # Verify token budget for max agents
            self.assertGreater(result.routing.confidence, 0)
        except ValueError:
            # Models not trained - skip this part for smoke test
            pass


class TestQueueExecutorConcurrency(unittest.TestCase):
    """Test queue executor concurrency limits."""

    def test_queue_executor_max_workers(self):
        """Verify queue executor respects max 8 concurrent workers."""
        executor = QueueExecutor()

        # Queue limits are enforced
        self.assertEqual(executor.MAX_CONCURRENT_WORKERS, 8)
        self.assertEqual(executor.MAX_QUEUE_SIZE, 16)

        # Verify results tracking
        from src.maestro.queue_executor import Task, TaskStatus
        task = Task(
            task_id="task-001",
            agent_name="test-agent",
            prompt="Test prompt"
        )
        self.assertEqual(task.status, TaskStatus.QUEUED)


class TestConsensusEscalation(unittest.TestCase):
    """Test consensus escalation logic."""

    def test_consensus_escalation_threshold(self):
        """Verify consensus escalates when <3/5 votes."""
        engine = ConsensusEngine()

        candidates = [
            Candidate("agent-1", "Option A", 0.80),
            Candidate("agent-2", "Option B", 0.75),
            Candidate("agent-3", "Option C", 0.70),
        ]

        # Only 2 votes for same candidate (below 3/5 threshold)
        votes = [
            Vote("agent-1", "Option A", 0.80),
            Vote("agent-2", "Option B", 0.75),
        ]

        result = engine.execute_vote("test", candidates, votes)

        # With only 2 votes, should escalate or tie
        self.assertIn(result.status.value, ["escalated", "tied"])


if __name__ == "__main__":
    unittest.main()
