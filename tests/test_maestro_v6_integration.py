"""
Maestro OS v6.0 — Full-Stack Integration Tests (Phase A + B + C)
Tests orchestration (A) + ML inference (B) + engineering analysis (C) working together.
"""

import unittest
from datetime import datetime

from src.maestro.detector import ComplexityDetector
from src.maestro.parser import WorkflowParser
from src.maestro.consensus import ConsensusEngine, Candidate, Vote
from src.maestro.orchestrator import MaestroOrchestrator, WorkflowExecution
from src.maestro.queue_executor import QueueExecutor, Task
from src.maestro.ml_features import ProjectFeatures, FeatureEngineer
from src.maestro.ml_inference import MLInferenceEngine, InferenceService
from src.maestro.mcp_tools import CADToolAdapter, RAGRetriever, SupabaseStateManager
from src.maestro.code_executor import SafePythonSandbox, StructuralCalculator
from src.maestro.norm_parser import Lei12334Parser, ComplianceChecker
from src.maestro.simulator import WhatIfSimulator, Scenario, ScenarioType
from src.maestro.metrics import MetricsCollector


class TestMaestroV6Integration(unittest.TestCase):
    """Integration tests for Maestro OS v6.0 full stack."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = ComplexityDetector()
        self.parser = WorkflowParser()
        self.orchestrator = MaestroOrchestrator()
        self.metrics_simple = MetricsCollector("wf-001", "proj-rodovia", num_agents=8, complexity_level="simple")
        self.metrics_medium = MetricsCollector("wf-002", "proj-porto", num_agents=12, complexity_level="medium")
        self.metrics_complex = MetricsCollector("wf-003", "proj-multimodal", num_agents=16, complexity_level="complex")

    def test_simple_workflow_8_agents(self):
        """Test simple project: Rodovia (1 segment, 8 agents)."""
        # Phase A: Detect complexity
        description = "Rodovia federal BR-101, pavimentação 200 km, DNIT compliance"
        detection = self.detector.detect(description)

        self.assertEqual(detection.num_segments, 1)
        self.assertEqual(detection.complexity_level.value, "simple")
        self.assertGreaterEqual(len(detection.agents_pool), 8)

        # Phase B: ML inference
        features = ProjectFeatures(
            project_id="proj-rodovia",
            project_type="infraestrutura_linear",
            title="BR-101 Pavimentação",
            num_segments=1,
            segments=["S1"],
            complexity_level="simple",
            budget_range="50M+",
            budget_numeric=75_000_000,
            is_urban=False,
            is_coastal=False,
            latitude=-23.5505,
            longitude=-46.6333,
            has_geotechnical_risk=True,
            has_environmental_constraints=False,
            has_indigenous_land=False,
            is_regulated_sector=True,
            timeline_months=18,
            has_seasonal_constraints=True,
            is_follow_up_project=False,
            previous_phase="estudo_previo"
        )

        feature_vector = features.to_feature_vector()
        self.assertEqual(len(feature_vector), 16)  # 16 features
        self.assertTrue(all(0 <= v <= 1 for v in feature_vector))  # All normalized

        # Phase C: Engineering analysis
        sandbox = SafePythonSandbox()
        calculator = StructuralCalculator()

        slope_result = calculator.calculate_slope_stability(
            height=10.0,
            angle_deg=25.0,
            gamma_soil=18.0,
            phi_deg=35.0,
            cohesion=20.0
        )
        self.assertIn("factor_of_safety", slope_result)
        self.assertGreater(slope_result["factor_of_safety"], 0)

        # Compliance checking
        checker = ComplianceChecker()
        compliant, warnings, violations = checker.check_compliance("rodovia", {"dnit": True})
        self.assertIsInstance(compliant, list)
        self.assertIsInstance(warnings, list)
        self.assertIsInstance(violations, list)

        # Record metrics
        self.metrics_simple.set_phase_duration("fan_out", 2.5)
        self.metrics_simple.set_phase_duration("consensus", 1.0)
        self.metrics_simple.set_phase_duration("aggregate", 0.5)
        self.metrics_simple.add_agent_metric("agente-infraestrutura-S1", 2.5, 45000, "completed", 5000)
        self.metrics_simple.add_consensus_metric("cronograma", 5, 3, True, False, 1.0)
        self.metrics_simple.finalize(success=True)

        report = self.metrics_simple.get_report()
        self.assertTrue(report.execution_time_met)  # <8 min for simple
        self.assertTrue(report.consensus_rate_met)
        self.assertTrue(report.token_budget_met)

    def test_medium_workflow_12_agents(self):
        """Test medium project: Porto + Energia + Saneamento (3 segments, 12 agents)."""
        # Phase A: Detect complexity
        description = """
        Terminal portuário Paranaguá (dragagem, molhe, berço contêiner) +
        Subestação ANEEL 230kV +
        ETA São Vicente (Lei 14.026, AySA)
        """
        detection = self.detector.detect(description)

        self.assertEqual(detection.num_segments, 3)
        self.assertEqual(detection.complexity_level.value, "medium")
        self.assertGreaterEqual(len(detection.agents_pool), 10)

        # Phase A: Workflow parsing
        workflow_yaml = """
        project:
          id: "proj-porto-energia-saneamento"
          type: "multi_segment"
          segments: ["S7", "S10", "S9"]

        agents:
          - name: "agente-portos"
            tier: "sonnet"
          - name: "agente-energia"
            tier: "sonnet"
          - name: "agente-saneamento"
            tier: "sonnet"
          - name: "manta-05"
            tier: "sonnet"
          - name: "manta-07"
            tier: "sonnet"

        phases:
          - name: "fan_out"
            agents: ["agente-portos", "agente-energia", "agente-saneamento", "manta-05", "manta-07"]

          - name: "consensus"
            aspects:
              - aspect: "orçamento"
                voters: ["agente-portos", "agente-energia", "agente-saneamento", "manta-05"]
                threshold: 3
              - aspect: "cronograma"
                voters: ["manta-07", "agente-portos", "agente-energia"]
                threshold: 3
        """

        parsed_workflow = self.parser.parse(workflow_yaml)
        self.assertIsNotNone(parsed_workflow)

        # Phase B: ML predictions
        features = ProjectFeatures(
            project_id="proj-porto-energia-saneamento",
            project_type="multi_segment",
            title="Porto + Energia + Saneamento",
            num_segments=3,
            segments=["S7", "S10", "S9"],
            complexity_level="medium",
            budget_range="1B+",
            budget_numeric=1_150_000_000,
            is_urban=True,
            is_coastal=True,
            latitude=-25.5169,
            longitude=-49.2566,
            has_geotechnical_risk=True,
            has_environmental_constraints=True,
            has_indigenous_land=False,
            is_regulated_sector=True,
            timeline_months=42,
            has_seasonal_constraints=True,
            is_follow_up_project=False,
            previous_phase="projeto_basico"
        )

        # Phase C: What-if analysis
        simulator = WhatIfSimulator()
        scenarios = [
            Scenario("sc-001", ScenarioType.DELAY, "3-month delay", "Dragagem takes 3 months extra", delay_days=90, affected_agent="S7"),
            Scenario("sc-002", ScenarioType.BUDGET_OVERRUN, "Budget +15%", "Labor cost inflation", budget_increase_pct=15.0),
            Scenario("sc-003", ScenarioType.RISK_ESCALATION, "Risk +10%", "Environmental license delay", risk_increase_pct=10.0),
        ]

        results = simulator.compare_scenarios(
            base_duration_min=6300,  # 105 min × 60
            base_cost=1_150_000_000,
            base_risk=0.35,
            scenarios=scenarios,
            segments_involved=["S7", "S10", "S9"],
            risk_level="medium"
        )

        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsNotNone(result.critical_path_impact)
            self.assertIsNotNone(result.recommendation)

        # Record metrics
        self.metrics_medium.set_phase_duration("fan_out", 4.0)
        self.metrics_medium.set_phase_duration("consensus", 1.5)
        self.metrics_medium.set_phase_duration("aggregate", 0.8)
        self.metrics_medium.add_agent_metric("agente-portos", 3.5, 60000, "completed", 8000)
        self.metrics_medium.add_agent_metric("agente-energia", 3.8, 65000, "completed", 7500)
        self.metrics_medium.add_agent_metric("agente-saneamento", 3.2, 58000, "completed", 7000)
        self.metrics_medium.add_agent_metric("manta-05", 2.0, 45000, "completed", 5000)
        self.metrics_medium.add_agent_metric("manta-07", 1.8, 40000, "completed", 4500)
        self.metrics_medium.add_consensus_metric("orçamento", 5, 5, True, False, 1.5)
        self.metrics_medium.add_consensus_metric("cronograma", 3, 3, True, False, 0.8)
        self.metrics_medium.finalize(success=True)

        report = self.metrics_medium.get_report()
        self.assertTrue(report.execution_time_met)  # <10 min for medium
        self.assertTrue(report.token_budget_met)

    def test_complex_workflow_16_agents(self):
        """Test complex project: 4+ segments (16 agents)."""
        # Phase A: Detect complexity
        description = """
        Complexo multimodal:
        - Rodovia SP-100 (200 km, pavimentação)
        - OAE (15 pontes, viadutos)
        - Ferrovia Carga São Paulo-Santos
        - Metrô Linha Amarela Expansão
        - Ambos com barragem, energia, saneamento
        """
        detection = self.detector.detect(description)

        self.assertGreaterEqual(detection.num_segments, 4)
        self.assertEqual(detection.complexity_level.value, "complex")
        self.assertGreaterEqual(len(detection.agents_pool), 14)

        # Phase C: Compliance analysis
        lei_parser = Lei12334Parser()
        rules = lei_parser.parse_lei_12334()
        self.assertGreater(len(rules), 0)

        # Phase C: Code execution
        sandbox = SafePythonSandbox()
        code = """
import math
import numpy as np

# Stress distribution calculation
load = 5000  # kN
width = 5.0   # m
depth = 3.0   # m
area = width * depth
stress = load / area
result = {
    'stress_kpa': round(stress, 1),
    'status': 'safe' if stress < 2000 else 'critical'
}
"""

        from src.maestro.code_executor import ExecutionRequest
        request = ExecutionRequest(code, {})
        exec_result = sandbox.execute(request)
        self.assertTrue(exec_result.success)
        self.assertIsNotNone(exec_result.output)

        # Record metrics
        self.metrics_complex.set_phase_duration("fan_out", 6.0)
        self.metrics_complex.set_phase_duration("consensus", 2.0)
        self.metrics_complex.set_phase_duration("aggregate", 1.0)

        # Simulate 16 agents
        for i in range(16):
            self.metrics_complex.add_agent_metric(f"agent-{i}", 3.0, 50000, "completed", 6000)

        self.metrics_complex.add_consensus_metric("orçamento", 5, 4, True, False, 1.5)
        self.metrics_complex.add_consensus_metric("cronograma", 4, 4, True, False, 1.0)
        self.metrics_complex.add_consensus_metric("risco", 3, 3, False, True, 0.8)  # Escalated
        self.metrics_complex.set_ml_metrics(85.0, 92.0, 78.0)
        self.metrics_complex.set_engineering_metrics(5, 20, 8)
        self.metrics_complex.finalize(success=True)

        report = self.metrics_complex.get_report()
        self.assertTrue(report.token_budget_met)
        self.assertGreater(report.execution_time_min, 0)

    def test_consensus_voting_integration(self):
        """Test consensus voting with multiple candidates."""
        engine = ConsensusEngine()

        candidates = [
            Candidate("agente-portos", "R$ 500M", 0.85),
            Candidate("agente-energia", "R$ 450M", 0.78),
            Candidate("agente-saneamento", "R$ 200M", 0.92),
            Candidate("manta-05", "R$ 1.15B", 0.88),
            Candidate("manta-15", "R$ 1.10B-1.20B", 0.80),
        ]

        votes = [
            Vote("agente-portos", "R$ 500M", 0.85),
            Vote("agente-energia", "R$ 450M", 0.78),
            Vote("agente-saneamento", "R$ 200M", 0.92),
            Vote("manta-05", "R$ 1.15B", 0.88),
            Vote("manta-15", "R$ 1.10B-1.20B", 0.80),
        ]

        result = engine.execute_vote("orçamento", candidates, votes)
        self.assertIsNotNone(result)
        self.assertTrue(result.status.value in ["decided", "escalated"])

    def test_ml_inference_integration(self):
        """Test ML inference (routing, duration, risk) integration."""
        from src.maestro.ml_trainer import RoutingModel, DurationPredictor, RiskClassifier

        # Create simple mock models
        routing_model = RoutingModel()
        duration_model = DurationPredictor()
        risk_model = RiskClassifier()

        service = InferenceService(routing_model, duration_model, risk_model)

        result = service.infer(
            "proj-teste",
            "Porto terminal Paranaguá com energia"
        )

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.routing)
        self.assertIsNotNone(result.duration)
        self.assertIsNotNone(result.risk)
        self.assertGreater(len(result.routing.suggested_agents), 0)
        self.assertGreater(result.duration.estimated_minutes, 0)
        self.assertGreaterEqual(result.risk.risk_score, 0)
        self.assertLessEqual(result.risk.risk_score, 100)

    def test_metrics_summary_formatting(self):
        """Test metrics collection and summary formatting."""
        self.metrics_simple.finalize(success=True)
        summary = self.metrics_simple.format_summary()

        self.assertIn("MAESTRO OS v6.0", summary)
        self.assertIn("proj-rodovia", summary)
        self.assertIn("SUCCESS", summary)

        json_str = self.metrics_simple.to_json()
        self.assertIn("proj-rodovia", json_str)


class TestPerformanceTargets(unittest.TestCase):
    """Test performance targets for different complexity levels."""

    def test_simple_project_targets(self):
        """Simple project (8 agents) should complete <8 min."""
        metrics = MetricsCollector("wf-001", "proj-simple", num_agents=8, complexity_level="simple")
        metrics.set_phase_duration("fan_out", 2.0)
        metrics.set_phase_duration("consensus", 0.8)
        metrics.set_phase_duration("aggregate", 0.3)
        metrics.finalize(success=True)

        report = metrics.get_report()
        self.assertLess(report.execution_time_min, 8.0)

    def test_medium_project_targets(self):
        """Medium project (12 agents) should complete <10 min."""
        metrics = MetricsCollector("wf-002", "proj-medium", num_agents=12, complexity_level="medium")
        metrics.set_phase_duration("fan_out", 4.0)
        metrics.set_phase_duration("consensus", 1.5)
        metrics.set_phase_duration("aggregate", 0.8)
        metrics.finalize(success=True)

        report = metrics.get_report()
        self.assertLess(report.execution_time_min, 10.0)

    def test_complex_project_targets(self):
        """Complex project (16 agents) should complete <15 min."""
        metrics = MetricsCollector("wf-003", "proj-complex", num_agents=16, complexity_level="complex")
        metrics.set_phase_duration("fan_out", 6.0)
        metrics.set_phase_duration("consensus", 2.0)
        metrics.set_phase_duration("aggregate", 1.0)
        metrics.finalize(success=True)

        report = metrics.get_report()
        self.assertLess(report.execution_time_min, 15.0)


if __name__ == "__main__":
    unittest.main()
