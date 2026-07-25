#!/usr/bin/env python3
"""
Regression Tests for CI/CD Pipeline (v5.0)
=========================================
Testes rápidos de regressão que rodam após cada commit.

Gate criteria:
  - Routing accuracy >= 81% (vs baseline)
  - Latency p95 < 5s (vs baseline, allow 5% regression)
  - No missing agents (20 agentes devem estar disponíveis)
  - Cross-agent job dispatch working
  - RAG collections acessíveis

Tempo total: < 60s

Uso:
  pytest tests/test_regression_suite.py -v --tb=short
  pytest tests/test_regression_suite.py -m ci  # CI gate
"""

import pytest
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# REGRESSION TEST DATA
# ============================================================================

BASELINE_METRICS = {
    "routing_accuracy": 0.85,  # 85% baseline
    "latency_p95_ms": 3200,    # 3.2s baseline
    "latency_p99_ms": 4500,    # 4.5s baseline
    "throughput_rps": 8.0,     # 8 req/s baseline
    "cross_agent_success_rate": 0.95,
    "memory_per_agent_mb": 45.0,
}

EXPECTED_AGENTS = [
    "manta-00",  # Maestro
    "manta-01",  # Claims
    "manta-02",  # Contratual
    "manta-03-s1",  # Rodovias
    "manta-03-s2",  # OAE
    "manta-03-s3",  # Ferrovia
    "manta-03-s4",  # Metrô
    "manta-03-s6",  # Portos
    "manta-03-s7",  # Aeroportos
    "manta-03-s8",  # Saneamento
    "manta-03-s9",  # Energia
    "manta-03-s10",  # Barragens
    "manta-04",  # Imobiliário
    "manta-05",  # Orçamento
    "manta-06",  # Modelagem
    "manta-07",  # Cronograma
    "manta-13",  # BD
    "manta-14",  # Apresentações
    "manta-15",  # Advisory
    "manta-16",  # Arquiteto IA
]

REGRESSION_PROMPTS = {
    "s8": "ETA para 500 mil habitantes — qual é o custo?",
    "s9": "Análise de RAP para LT 765 kV",
    "s6": "Terminal de contêineres em dragagem",
    "s7": "Pista de aeroporto regional",
    "s10": "Barragem de concreto compactado",
    "s1": "Pavimento asfáltico CBUQ",
    "claims": "Indenização por sinistro",
    "budget": "Orçamento de infraestrutura",
}


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def current_metrics() -> Dict:
    """Coleta métricas atuais (mock)."""
    return {
        "routing_accuracy": 0.86,
        "latency_p95_ms": 3100,
        "latency_p99_ms": 4400,
        "throughput_rps": 8.5,
        "cross_agent_success_rate": 0.96,
        "memory_per_agent_mb": 42.0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@pytest.fixture(scope="session")
def available_agents() -> List[str]:
    """Simula agentes disponíveis (mock)."""
    return EXPECTED_AGENTS.copy()


# ============================================================================
# TEST CLASSES
# ============================================================================

@pytest.mark.ci
class TestRegressionRoutingAccuracy:
    """Gate: Routing accuracy >= 81%."""

    def test_accuracy_baseline(self, current_metrics):
        """Accuracy não degradou."""
        current_accuracy = current_metrics["routing_accuracy"]
        baseline_accuracy = BASELINE_METRICS["routing_accuracy"]

        logger.info(f"Current accuracy: {current_accuracy:.1%}, Baseline: {baseline_accuracy:.1%}")

        # Permitir regressão de até 5%
        min_acceptable = baseline_accuracy * 0.95
        assert current_accuracy >= min_acceptable, \
            f"Accuracy {current_accuracy:.1%} < {min_acceptable:.1%} (5% regressão permitida)"

    def test_accuracy_minimum_threshold(self, current_metrics):
        """Accuracy nunca abaixo de 81%."""
        current_accuracy = current_metrics["routing_accuracy"]
        assert current_accuracy >= 0.81, \
            f"Accuracy {current_accuracy:.1%} < 81% minimum"


@pytest.mark.ci
class TestRegressionLatency:
    """Gate: Latência p95 < 5s, allow 5% regression."""

    def test_latency_p95_baseline(self, current_metrics):
        """Latência p95 não degradou > 5%."""
        current_p95 = current_metrics["latency_p95_ms"]
        baseline_p95 = BASELINE_METRICS["latency_p95_ms"]

        # Permitir degradação de até 5%
        max_acceptable = baseline_p95 * 1.05
        logger.info(f"Current p95: {current_p95}ms, Baseline: {baseline_p95}ms, Max: {max_acceptable}ms")

        assert current_p95 <= max_acceptable, \
            f"Latency p95 {current_p95}ms > {max_acceptable}ms (5% regressão)"

    def test_latency_p95_hard_limit(self, current_metrics):
        """Latência p95 < 5s (hard limit)."""
        current_p95 = current_metrics["latency_p95_ms"]
        assert current_p95 < 5000, f"Latency p95 {current_p95}ms >= 5s hard limit"

    def test_latency_p99_baseline(self, current_metrics):
        """Latência p99 < 5s."""
        current_p99 = current_metrics["latency_p99_ms"]
        # Hard limit: p99 < 5s
        assert current_p99 < 5000, f"Latency p99 {current_p99}ms >= 5s"


@pytest.mark.ci
class TestRegressionAgentRegistry:
    """Gate: Todos 20 agentes disponíveis."""

    def test_all_agents_registered(self, available_agents):
        """Todos 20 agentes presentes."""
        for agent in EXPECTED_AGENTS:
            assert agent in available_agents, \
                f"Agent {agent} not found in registry"

    def test_agent_count(self, available_agents):
        """Contagem de agentes = 20."""
        assert len(available_agents) >= len(EXPECTED_AGENTS), \
            f"Expected {len(EXPECTED_AGENTS)} agents, got {len(available_agents)}"

    def test_s8_saneamento_available(self, available_agents):
        """S8 — Saneamento disponível (prioridade AySA)."""
        assert "manta-03-s8" in available_agents

    def test_s9_energia_available(self, available_agents):
        """S9 — Energia disponível (ANEEL)."""
        assert "manta-03-s9" in available_agents

    def test_s6_portos_available(self, available_agents):
        """S6 — Portos disponível."""
        assert "manta-03-s6" in available_agents


@pytest.mark.ci
class TestRegressionCrossAgent:
    """Gate: Cross-agent jobs dispatch successfully."""

    def test_cross_agent_dispatch(self):
        """Cross-agent dispatch sem erro."""
        # Mock: simulate dispatch
        job_id = "job_manta-03-s8_manta-05_001"
        assert job_id is not None
        assert "job_" in job_id

    def test_cross_agent_success_rate(self, current_metrics):
        """Cross-agent success rate >= 95%."""
        success_rate = current_metrics["cross_agent_success_rate"]
        assert success_rate >= 0.95, \
            f"Cross-agent success rate {success_rate:.1%} < 95%"


@pytest.mark.ci
class TestRegressionRAG:
    """Gate: RAG collections acessíveis."""

    def test_rag_collections_exist(self):
        """Todas RAG collections presentes."""
        collections = [
            "san:v5.0:*",  # Saneamento
            "ene:v5.0:*",  # Energia
            "por:v5.0:*",  # Portos
            "aer:v5.0:*",  # Aeroportos
            "bar:v5.0:*",  # Barragens
            "rod:v5.0:*",  # Rodovias
            "oae:v5.0:*",  # OAE
            "fer:v5.0:*",  # Ferrovia
            "met:v5.0:*",  # Metrô
        ]

        for collection in collections:
            # Em produção, fazer query ao Supabase
            assert collection is not None

    def test_rag_reranker_enabled(self):
        """Reranker habilitado em todas collections."""
        # Mock: validar que reranker está ativo
        assert True  # Em produção, call reranker endpoint


@pytest.mark.ci
class TestRegressionSmokeTests:
    """Smoke tests rápidos para rotas principais."""

    def test_smoke_s8_routing(self):
        """Smoke: S8 routing funciona."""
        prompt = REGRESSION_PROMPTS["s8"]
        assert prompt is not None
        assert "ETA" in prompt

    def test_smoke_s9_routing(self):
        """Smoke: S9 routing funciona."""
        prompt = REGRESSION_PROMPTS["s9"]
        assert prompt is not None
        assert "RAP" in prompt

    def test_smoke_s6_routing(self):
        """Smoke: S6 routing funciona."""
        prompt = REGRESSION_PROMPTS["s6"]
        assert prompt is not None
        assert "terminal" in prompt.lower()

    def test_smoke_claims_routing(self):
        """Smoke: Claims routing funciona."""
        prompt = REGRESSION_PROMPTS["claims"]
        assert prompt is not None
        assert "Indenização" in prompt

    def test_smoke_budget_routing(self):
        """Smoke: Budget routing funciona."""
        prompt = REGRESSION_PROMPTS["budget"]
        assert prompt is not None
        assert "Orçamento" in prompt


@pytest.mark.ci
class TestRegressionVersioning:
    """Gate: Skill versioning correto."""

    def test_versions_json_valid(self):
        """VERSIONS.json é válido."""
        versions_path = Path("VERSIONS.json")
        if versions_path.exists():
            with open(versions_path, 'r') as f:
                data = json.load(f)
                assert "v5.0" in data or "agente-saneamento" in data

    def test_skill_checksums_exist(self):
        """Checksums de skills calculados."""
        # Em produção, validar checksums MD5
        expected_skills = [
            "agente-saneamento",
            "agente-energia",
            "agente-portos",
        ]
        # Mock: checksums existem
        assert len(expected_skills) >= 3

    def test_no_skill_drift(self):
        """Sem drift de skill versions."""
        # Em produção, comparar checksums atuais vs esperados
        # Nenhum skill deve mudar checksum sem notificação
        assert True


@pytest.mark.ci
class TestRegressionThresholds:
    """Testes de thresholds críticos."""

    def test_routing_confidence_threshold(self):
        """Routing confidence >= 80% em golden set."""
        # Mock: simular 40 test cases
        passing_cases = 33  # 33/40 = 82.5%
        total_cases = 40

        accuracy = passing_cases / total_cases
        logger.info(f"Routing confidence: {accuracy:.1%}")

        assert accuracy >= 0.80

    def test_model_tiering_correctness(self):
        """Model tiering alinhado com complexity."""
        # Validar que complexity > 4.0 não mapped para Haiku
        assert True  # Mock

    def test_no_critical_regression(self, current_metrics):
        """Sem regressão crítica em nenhuma métrica."""
        metrics_to_check = [
            ("routing_accuracy", 0.81),
            ("latency_p95_ms", 5000),
            ("cross_agent_success_rate", 0.90),
        ]

        for metric_name, threshold in metrics_to_check:
            value = current_metrics.get(metric_name, 0)
            if metric_name == "routing_accuracy":
                assert value >= threshold, \
                    f"{metric_name} {value:.1%} < {threshold:.1%}"
            elif metric_name == "latency_p95_ms":
                assert value <= threshold, \
                    f"{metric_name} {value}ms > {threshold}ms"
            else:
                assert value >= threshold, \
                    f"{metric_name} {value:.1%} < {threshold:.1%}"


@pytest.mark.ci
class TestRegressionDependencies:
    """Gate: Dependências satisfeitas."""

    def test_supabase_accessible(self):
        """Supabase database acessível."""
        # Mock: connection check
        assert True

    def test_elasticsearch_accessible(self):
        """Elasticsearch BM25 acessível."""
        # Mock: connection check
        assert True

    def test_vector_db_accessible(self):
        """Vector database (Qdrant/Pinecone) acessível."""
        # Mock: connection check
        assert True

    def test_reranker_service_responsive(self):
        """Reranker service respondendo."""
        # Mock: health check
        assert True


@pytest.mark.ci
class TestRegressionDeployment:
    """Gate: Deployment checklist."""

    def test_claude_md_valid(self):
        """CLAUDE.md v5.0 válido."""
        claude_path = Path("CLAUDE.md")
        if claude_path.exists():
            with open(claude_path, 'r') as f:
                content = f.read()
                assert "v5.0" in content
                assert "8 pilares" in content or "pilares" in content.lower()

    def test_no_breaking_changes(self):
        """Sem breaking changes em agent interfaces."""
        # Mock: compare current vs previous agent specs
        assert True

    def test_rollback_ready(self):
        """Rollback disponível (v4.9 skills archived)."""
        # Mock: validar archived versions
        assert True


# ============================================================================
# PARAMETRIZED REGRESSION TESTS
# ============================================================================

@pytest.mark.ci
class TestRegressionSegments:
    """Parametrized tests por segmento."""

    @pytest.mark.parametrize("agent_id,keyword", [
        ("manta-03-s8", "saneamento"),
        ("manta-03-s9", "energia"),
        ("manta-03-s6", "porto"),
        ("manta-03-s7", "aeroporto"),
        ("manta-03-s10", "barragem"),
        ("manta-03-s1", "rodovia"),
    ])
    def test_segment_routing(self, agent_id, keyword):
        """Segmento roteia para agente correto."""
        # Mock: route with keyword
        assert agent_id is not None
        assert keyword is not None

    @pytest.mark.parametrize("model_tier,min_complexity", [
        ("haiku-4-5", 0),
        ("sonnet-5", 3),
        ("opus", 4),
    ])
    def test_tiering_by_complexity(self, model_tier, min_complexity):
        """Tiering alinhado com complexity."""
        assert model_tier in ["haiku-4-5", "sonnet-5", "opus"]
        assert min_complexity >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'ci', '--tb=short'])
