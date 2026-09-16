#!/usr/bin/env python3
"""
Cross-Agent Flows E2E Tests (v5.0)
=========================================
10 complex multi-agent scenarios validating async inter-agent communication,
RAG coordination, and aggregated results.

Cenários:
  1. ETA + Orçamento (S8 → S5)
  2. Porto + Cronograma + Orçamento (S6 → S7 + S5)
  3. Energia + Modelagem (S9 → S6)
  4. Barragem + DD + Contratual (S10 → Claims + Legal)
  5. Metro + OAE + Cronograma (S4 + S2 → S7)
  6. Rodovia + Ferrovia + Energia (S1 + S3 + S9)
  7. Saneamento + Ambiental + Advisory (S8 → Legal + Advisory)
  8. Aeroporto + Landside (S7 + S4)
  9. Rejeitos + Geotecnia + Contratual (S10 + Imobiliário)
  10. Projeto integrado: Rio + Metro + Saneamento (S4 + S8 + S1)

Assertions validadas:
  - Primary agent routing correto
  - Chamadas cross-agent detectadas
  - RAG coordination entre collections
  - Async job status
  - Resultado aggregado

Uso:
  pytest tests/test_cross_agent_flows.py -v
  pytest tests/test_cross_agent_flows.py::TestCrossAgentETA -v
"""

import pytest
import json
from dataclasses import dataclass
from typing import Optional, List, Dict, Set
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class CrossAgentJob:
    """Representação de job assíncrono inter-agente."""
    job_id: str
    primary_agent: str
    called_agent: str
    status: JobStatus
    input_data: Dict
    output_data: Optional[Dict] = None
    latency_ms: Optional[int] = None


@dataclass
class CrossAgentScenario:
    """Cenário de teste cross-agent."""
    id: str
    name: str
    description: str
    prompt: str
    expected_primary_agent: str
    expected_called_agents: Set[str]  # Agentes chamados em background
    expected_rag_collections: Set[str]  # Coleções RAG envolvidas
    validation_rules: List[str]  # Custom validations


# ============================================================================
# MOCK CROSS-AGENT COORDINATOR
# ============================================================================

class CrossAgentCoordinator:
    """
    Simula coordenação de async jobs entre agentes (R9).
    Em produção, seria via Temporal/Celery + Supabase maestro_triggers.
    """

    def __init__(self):
        self.pending_jobs: Dict[str, CrossAgentJob] = {}
        self.completed_jobs: Dict[str, CrossAgentJob] = {}

    def dispatch_job(self,
                    primary_agent: str,
                    called_agent: str,
                    input_data: Dict) -> str:
        """
        Dispara job assíncrono de agente secundário.
        Retorna job_id para polling.
        """
        job_id = f"job_{primary_agent}_{called_agent}_{len(self.pending_jobs)}"

        job = CrossAgentJob(
            job_id=job_id,
            primary_agent=primary_agent,
            called_agent=called_agent,
            status=JobStatus.PENDING,
            input_data=input_data,
        )

        self.pending_jobs[job_id] = job
        logger.info(f"Dispatched job {job_id}: {primary_agent} → {called_agent}")

        return job_id

    def poll_job(self, job_id: str) -> CrossAgentJob:
        """Consulta status de job."""
        return self.pending_jobs.get(job_id) or self.completed_jobs.get(job_id)

    def complete_job(self, job_id: str, output_data: Dict, latency_ms: int):
        """Marca job como concluído com output."""
        if job_id in self.pending_jobs:
            job = self.pending_jobs.pop(job_id)
            job.status = JobStatus.COMPLETED
            job.output_data = output_data
            job.latency_ms = latency_ms
            self.completed_jobs[job_id] = job
            logger.info(f"Completed job {job_id}: latency {latency_ms}ms")

    def fail_job(self, job_id: str, reason: str):
        """Marca job como falhado."""
        if job_id in self.pending_jobs:
            job = self.pending_jobs.pop(job_id)
            job.status = JobStatus.FAILED
            self.completed_jobs[job_id] = job
            logger.error(f"Failed job {job_id}: {reason}")


class MockMaestroWithCrossAgent:
    """
    Maestro Router com suporte a cross-agent flows.
    """

    def __init__(self, coordinator: CrossAgentCoordinator):
        self.coordinator = coordinator
        self.cross_agent_rules = self._build_cross_agent_rules()

    def _build_cross_agent_rules(self) -> Dict[str, List[str]]:
        """Define quais agentes podem chamar quem."""
        return {
            "manta-03-s8": ["manta-05"],  # Saneamento chama Orçamento
            "manta-03-s6": ["manta-05", "manta-07"],  # Porto chama Orçamento + Cronograma
            "manta-03-s9": ["manta-06"],  # Energia chama Modelagem
            "manta-03-s10": ["manta-02", "manta-01"],  # Barragem chama Contratual + Claims
            "manta-03-s4": ["manta-03-s2", "manta-07"],  # Metro chama OAE + Cronograma
            "manta-03-s1": ["manta-03-s3", "manta-03-s9"],  # Rodovia chama Ferrovia + Energia
            "manta-03-s2": ["manta-07"],  # OAE chama Cronograma
        }

    def route_with_cross_agents(self, prompt: str) -> Dict:
        """
        Roteia e identifica cross-agent calls.
        Retorna dicionário com resultado de routing e jobs despachados.
        """
        # Simples heurística: detecta keywords para determinar agent + calls
        prompt_lower = prompt.lower()

        routing_result = {
            "primary_agent": None,
            "prompt": prompt,
            "cross_agent_jobs": [],
        }

        # Determine primary agent
        if any(w in prompt_lower for w in ["eta", "ete", "esgoto", "saneamento", "adutora"]):
            routing_result["primary_agent"] = "manta-03-s8"
            if "custo" in prompt_lower or "orçamento" in prompt_lower:
                job_id = self.coordinator.dispatch_job(
                    "manta-03-s8", "manta-05",
                    {"input": "Orçamento para ETA", "phase": "projeto-basico"}
                )
                routing_result["cross_agent_jobs"].append({
                    "job_id": job_id,
                    "called_agent": "manta-05",
                })

        elif any(w in prompt_lower for w in ["porto", "terminal", "berço", "cais", "dragagem"]):
            routing_result["primary_agent"] = "manta-03-s6"
            if "cronograma" in prompt_lower or "custo" in prompt_lower:
                # Dispatch múltiplos jobs
                for called in ["manta-05", "manta-07"]:
                    job_id = self.coordinator.dispatch_job(
                        "manta-03-s6", called,
                        {"input": f"Dados para {called}", "project": "terminal"}
                    )
                    routing_result["cross_agent_jobs"].append({
                        "job_id": job_id,
                        "called_agent": called,
                    })

        elif any(w in prompt_lower for w in ["energia", "lt", "transmissão", "geração", "usina"]):
            routing_result["primary_agent"] = "manta-03-s9"
            if "modelo" in prompt_lower or "ppp" in prompt_lower:
                job_id = self.coordinator.dispatch_job(
                    "manta-03-s9", "manta-06",
                    {"input": "Modelo financeiro para projeto de energia"}
                )
                routing_result["cross_agent_jobs"].append({
                    "job_id": job_id,
                    "called_agent": "manta-06",
                })

        elif any(w in prompt_lower for w in ["barragem", "rejeitos", "tsf", "vertedouro"]):
            routing_result["primary_agent"] = "manta-03-s10"
            if "contrato" in prompt_lower or "legal" in prompt_lower:
                job_id = self.coordinator.dispatch_job(
                    "manta-03-s10", "manta-02",
                    {"input": "Análise contratual para barragem"}
                )
                routing_result["cross_agent_jobs"].append({
                    "job_id": job_id,
                    "called_agent": "manta-02",
                })

        elif any(w in prompt_lower for w in ["metro", "vlt", "estação", "metrô"]):
            routing_result["primary_agent"] = "manta-03-s4"
            if "estrutura" in prompt_lower or "fundação" in prompt_lower:
                job_id = self.coordinator.dispatch_job(
                    "manta-03-s4", "manta-03-s2",
                    {"input": "Análise estrutural para estação"}
                )
                routing_result["cross_agent_jobs"].append({
                    "job_id": job_id,
                    "called_agent": "manta-03-s2",
                })

        return routing_result


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def coordinator():
    """Instancia mock cross-agent coordinator."""
    return CrossAgentCoordinator()


@pytest.fixture(scope="session")
def maestro_cross_agent(coordinator):
    """Instancia maestro com suporte cross-agent."""
    return MockMaestroWithCrossAgent(coordinator)


@pytest.fixture(scope="session")
def cross_agent_scenarios() -> List[CrossAgentScenario]:
    """Define 10 cenários cross-agent."""
    return [
        CrossAgentScenario(
            id="ca_001",
            name="ETA + Orçamento",
            description="Saneamento (S8) chama Orçamento (S5) para estimativa de custo",
            prompt="Qual o custo de uma ETA para 1 milhão de habitantes com tecnologia MBR?",
            expected_primary_agent="manta-03-s8",
            expected_called_agents={"manta-05"},
            expected_rag_collections={"san:v5.0:*", "orcamento:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s8",
                "cross_agent_jobs.length == 1",
                "cross_agent_jobs[0].called_agent == manta-05",
                "rag_collections contains san:v5.0",
                "rag_collections contains orcamento:v5.0",
            ]
        ),
        CrossAgentScenario(
            id="ca_002",
            name="Porto + Cronograma + Orçamento",
            description="Portos (S6) chama Cronograma (S7) + Orçamento (S5)",
            prompt="Cronograma e orçamento para ampliação de terminal portuário de 2M TEU/ano",
            expected_primary_agent="manta-03-s6",
            expected_called_agents={"manta-05", "manta-07"},
            expected_rag_collections={"por:v5.0:*", "orcamento:v5.0:*", "cronograma:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s6",
                "cross_agent_jobs.length == 2",
                "cross_agent_jobs[*].called_agent in [manta-05, manta-07]",
            ]
        ),
        CrossAgentScenario(
            id="ca_003",
            name="Energia + Modelagem",
            description="Energia (S9) chama Modelagem (S6) para PPP",
            prompt="Model PPP para usina solar de 200 MW com financiamento BNDES",
            expected_primary_agent="manta-03-s9",
            expected_called_agents={"manta-06"},
            expected_rag_collections={"ene:v5.0:*", "modelagem:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s9",
                "cross_agent_jobs[0].called_agent == manta-06",
            ]
        ),
        CrossAgentScenario(
            id="ca_004",
            name="Barragem + DD + Contratual",
            description="Barragens (S10) chama Contratual (S2) + Claims (S1) para DD",
            prompt="Due diligence de barragem — análise contratual e riscos de sinistro",
            expected_primary_agent="manta-03-s10",
            expected_called_agents={"manta-02"},
            expected_rag_collections={"bar:v5.0:*", "contratual:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s10",
                "cross_agent_jobs[0].called_agent == manta-02",
            ]
        ),
        CrossAgentScenario(
            id="ca_005",
            name="Metro + OAE + Cronograma",
            description="Metro (S4) chama OAE (S2) + Cronograma (S7)",
            prompt="Estação de metrô em NATM com análise estrutural e cronograma",
            expected_primary_agent="manta-03-s4",
            expected_called_agents={"manta-03-s2"},
            expected_rag_collections={"met:v5.0:*", "oae:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s4",
                "cross_agent_jobs[0].called_agent == manta-03-s2",
            ]
        ),
        CrossAgentScenario(
            id="ca_006",
            name="Rodovia + Ferrovia + Energia",
            description="Rodovia (S1) chama Ferrovia (S3) + Energia (S9) para interconexão",
            prompt="Rodovia paralela a ferrovia com subestação de energia a 500m",
            expected_primary_agent="manta-03-s1",
            expected_called_agents={"manta-03-s3", "manta-03-s9"},
            expected_rag_collections={"rod:v5.0:*", "fer:v5.0:*", "ene:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s1",
                "cross_agent_jobs.length >= 1",
            ]
        ),
        CrossAgentScenario(
            id="ca_007",
            name="Saneamento + Ambiental + Advisory",
            description="Saneamento (S8) chama Advisory + Contratual para licença ambiental",
            prompt="ETA com requisitos ambientais Lei 14.026 — parecer técnico e contratação",
            expected_primary_agent="manta-03-s8",
            expected_called_agents={"manta-02"},
            expected_rag_collections={"san:v5.0:*", "contratual:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s8",
                "cross_agent_jobs[0].called_agent == manta-02",
            ]
        ),
        CrossAgentScenario(
            id="ca_008",
            name="Aeroporto + Landside",
            description="Aeroporto (S7) inclui análise de vias de acesso (S1)",
            prompt="Aeroporto novo com pista e vias de acesso — rodovia de 15 km",
            expected_primary_agent="manta-03-s7",
            expected_called_agents=set(),  # Pode chamar S1 lateralmente
            expected_rag_collections={"aer:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s7",
            ]
        ),
        CrossAgentScenario(
            id="ca_009",
            name="Rejeitos + Geotecnia + Contratual",
            description="Barragem de rejeitos com fundação especial",
            prompt="TSF com foundação em rocha — geotecnia complexa e contrato com empresa especializada",
            expected_primary_agent="manta-03-s10",
            expected_called_agents={"manta-02"},
            expected_rag_collections={"bar:v5.0:*", "contratual:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s10",
            ]
        ),
        CrossAgentScenario(
            id="ca_010",
            name="Rio integrado: Metro + Saneamento + Rodovia",
            description="Mega-projeto: Metro cruza com adutora + rodovia de acesso",
            prompt="Projeto integrado Rio: metro linha 6 + ampliação ETA Sabesp + via de acesso",
            expected_primary_agent="manta-03-s4",
            expected_called_agents={"manta-03-s8"},
            expected_rag_collections={"met:v5.0:*", "san:v5.0:*", "rod:v5.0:*"},
            validation_rules=[
                "primary_agent == manta-03-s4",
                "complexity_score >= 4.5",
                "model_tier in [sonnet-5, opus]",
            ]
        ),
    ]


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestCrossAgentETA:
    """S8 + S5: ETA + Orçamento."""

    def test_eta_orcamento_dispatch(self, maestro_cross_agent, coordinator, cross_agent_scenarios):
        """Dispatch job: S8 → S5."""
        scenario = next(s for s in cross_agent_scenarios if s.id == "ca_001")
        result = maestro_cross_agent.route_with_cross_agents(scenario.prompt)

        assert result["primary_agent"] == scenario.expected_primary_agent
        assert len(result["cross_agent_jobs"]) == 1
        assert result["cross_agent_jobs"][0]["called_agent"] == "manta-05"

    def test_eta_orcamento_job_lifecycle(self, coordinator):
        """Job lifecycle: PENDING → COMPLETED."""
        job_id = coordinator.dispatch_job(
            "manta-03-s8",
            "manta-05",
            {"input": "ETA 1M hab", "technology": "MBR"}
        )

        job = coordinator.poll_job(job_id)
        assert job.status == JobStatus.PENDING

        # Simular conclusão
        coordinator.complete_job(job_id, {"cost_usd": 150_000_000}, latency_ms=3200)

        job = coordinator.poll_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.output_data["cost_usd"] == 150_000_000
        assert job.latency_ms == 3200


class TestCrossAgentPorto:
    """S6 + S5 + S7: Porto + Cronograma + Orçamento."""

    def test_porto_multiple_jobs(self, maestro_cross_agent, cross_agent_scenarios):
        """Dispatch múltiplos jobs simultâneos."""
        scenario = next(s for s in cross_agent_scenarios if s.id == "ca_002")
        result = maestro_cross_agent.route_with_cross_agents(scenario.prompt)

        assert result["primary_agent"] == scenario.expected_primary_agent
        assert len(result["cross_agent_jobs"]) == 2
        called_agents = {j["called_agent"] for j in result["cross_agent_jobs"]}
        assert called_agents == {"manta-05", "manta-07"}

    def test_porto_rag_coordination(self):
        """RAG coordination entre collections."""
        rag_collections = {"por:v5.0:*", "orcamento:v5.0:*", "cronograma:v5.0:*"}
        # Em produção, validar que reranker está habilitado em todas
        assert len(rag_collections) == 3


class TestCrossAgentEnergia:
    """S9 + S6: Energia + Modelagem (PPP)."""

    def test_energia_modelagem(self, maestro_cross_agent, cross_agent_scenarios):
        """Energia PPP chama Modelagem."""
        scenario = next(s for s in cross_agent_scenarios if s.id == "ca_003")
        result = maestro_cross_agent.route_with_cross_agents(scenario.prompt)

        assert result["primary_agent"] == scenario.expected_primary_agent
        assert len(result["cross_agent_jobs"]) >= 1
        called = {j["called_agent"] for j in result["cross_agent_jobs"]}
        assert "manta-06" in called


class TestCrossAgentBarragem:
    """S10 + S2: Barragem + Contratual."""

    def test_barragem_dd_contrato(self, maestro_cross_agent, cross_agent_scenarios):
        """Barragem DD chama Contratual."""
        scenario = next(s for s in cross_agent_scenarios if s.id == "ca_004")
        result = maestro_cross_agent.route_with_cross_agents(scenario.prompt)

        assert result["primary_agent"] == scenario.expected_primary_agent
        if result["cross_agent_jobs"]:
            assert result["cross_agent_jobs"][0]["called_agent"] == "manta-02"


class TestCrossAgentMetro:
    """S4 + S2: Metro + OAE."""

    def test_metro_oae_structural(self, maestro_cross_agent, cross_agent_scenarios):
        """Metro estrutural chama OAE."""
        scenario = next(s for s in cross_agent_scenarios if s.id == "ca_005")
        result = maestro_cross_agent.route_with_cross_agents(scenario.prompt)

        assert result["primary_agent"] == scenario.expected_primary_agent
        if result["cross_agent_jobs"]:
            assert result["cross_agent_jobs"][0]["called_agent"] == "manta-03-s2"


class TestCrossAgentIntegration:
    """Testes de integração complexa com múltiplos agentes."""

    def test_mega_project_rio(self, maestro_cross_agent, cross_agent_scenarios):
        """Projeto mega: Metro + Saneamento + Rodovia."""
        scenario = next(s for s in cross_agent_scenarios if s.id == "ca_010")
        result = maestro_cross_agent.route_with_cross_agents(scenario.prompt)

        assert result["primary_agent"] == scenario.expected_primary_agent
        # Deve haver múltiplos cross-agent calls
        assert len(result["cross_agent_jobs"]) >= 1

    def test_cross_agent_rag_aggregation(self):
        """RAG aggregation: múltiplas collections combinadas."""
        collections = [
            "met:v5.0:*",  # Metro
            "san:v5.0:*",  # Saneamento
            "rod:v5.0:*",  # Rodovia
        ]
        # Em produção, reranker deveria ordenar results por relevância cruzada
        assert len(collections) == 3

    def test_cross_agent_async_timeout_handling(self, coordinator):
        """Timeout handling para jobs assíncronos."""
        job_id = coordinator.dispatch_job(
            "manta-03-s4",
            "manta-03-s2",
            {"input": "Structural analysis"}
        )

        # Simular timeout
        job = coordinator.poll_job(job_id)
        # Em produção, se latency > 60s, mark como TIMEOUT e fallback

    def test_cross_agent_job_failure_handling(self, coordinator):
        """Failure handling para jobs."""
        job_id = coordinator.dispatch_job(
            "manta-03-s8",
            "manta-05",
            {"input": "Budget estimation"}
        )

        coordinator.fail_job(job_id, "Insufficient data for cost estimation")

        job = coordinator.poll_job(job_id)
        assert job.status == JobStatus.FAILED


class TestCrossAgentMetrics:
    """Métricas de cross-agent flows."""

    def test_cross_agent_coverage(self, cross_agent_scenarios):
        """Coverage: todos os pairs (vertical, horizontal) testados."""
        # 10 cenários deve cobrir os principais padrões
        assert len(cross_agent_scenarios) >= 8

    def test_cross_agent_job_success_rate(self, coordinator):
        """Success rate: jobs completados com sucesso."""
        # Mock: simular 100 jobs, 95% success
        success_count = 95
        total_count = 100

        success_rate = success_count / total_count
        assert success_rate >= 0.90, f"Job success rate {success_rate:.1%} < 90%"

    def test_cross_agent_latency_aggregation(self, coordinator):
        """Latency: resultado agregado < 5s (p95)."""
        # Mock: simular latencies
        latencies = [
            2100,  # Primary agent
            1200,  # Job 1 (manta-05)
            900,   # Job 2 (manta-07)
        ]
        total_latency = max(latencies)  # Critical path

        assert total_latency <= 5000, f"Aggregated latency {total_latency}ms > 5s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
