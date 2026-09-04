#!/usr/bin/env python3
"""
Pytest configuration for Maestro E2E Tests (v5.0)
================================================
Centraliza fixtures, plugins, e configurações globais.

Uso:
  pytest --co -q  # List all fixtures
"""

import pytest
import json
import logging
from pathlib import Path
from datetime import datetime

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tests/test_run.log', mode='a'),
    ]
)


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configuração de inicialização do pytest."""
    config.addinivalue_line(
        "markers", "ci: CI/CD gate tests (regression suite only)"
    )
    config.addinivalue_line(
        "markers", "perf: performance baseline tests"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
    config.addinivalue_line(
        "markers", "smoke: smoke tests (quick validation)"
    )

    print("\n" + "=" * 70)
    print("Maestro Router E2E Tests (v5.0)")
    print("=" * 70)
    print(f"Start time: {datetime.utcnow().isoformat()}")
    print(f"Python: {config.option.verbose and 'Verbose' or 'Normal'} mode")
    print("=" * 70 + "\n")


def pytest_collection_modifyitems(config, items):
    """Modifica items coletados (ex: adicionar markers automáticamente)."""
    for item in items:
        # Auto-marker based on filename
        if "regression" in item.nodeid:
            item.add_marker(pytest.mark.ci)
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.perf)
        elif "cross_agent" in item.nodeid:
            item.add_marker(pytest.mark.integration)


def pytest_sessionfinish(session, exitstatus):
    """Finalização da sessão."""
    print("\n" + "=" * 70)
    print(f"Test run completed at {datetime.utcnow().isoformat()}")
    print(f"Exit status: {exitstatus}")
    print("=" * 70 + "\n")


# ============================================================================
# GLOBAL FIXTURES
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def log_test_environment():
    """Log informações do ambiente de teste."""
    import sys
    import platform

    logger = logging.getLogger(__name__)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Test suite: Maestro Router E2E v5.0")
    logger.info(f"Fixtures path: {Path(__file__).parent / 'fixtures'}")

    yield

    logger.info("Test environment cleanup completed")


@pytest.fixture(scope="session")
def test_config() -> dict:
    """Configurações globais de teste."""
    return {
        "version": "v5.0",
        "timeout_seconds": 300,
        "max_agents": 20,
        "expected_accuracy": 0.81,
        "max_latency_ms": 5000,
        "max_throughput_rps": 10,
        "fixtures_path": Path(__file__).parent / "fixtures",
    }


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    """Temporary directory para test artifacts."""
    return tmp_path_factory.mktemp("maestro-e2e")


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def load_golden_cases() -> dict:
    """Carrega golden test cases do JSON."""
    fixtures_path = Path(__file__).parent / "fixtures" / "prompts_golden_40.json"

    if not fixtures_path.exists():
        pytest.skip(f"Fixtures not found: {fixtures_path}")

    with open(fixtures_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


@pytest.fixture(scope="session")
def golden_case_ids(load_golden_cases) -> list:
    """Lista de IDs de golden cases."""
    return [tc['id'] for tc in load_golden_cases['test_cases']]


@pytest.fixture(scope="session")
def baseline_metrics() -> dict:
    """Baseline metrics para regression testing."""
    return {
        "routing_accuracy": 0.85,
        "latency_p95_ms": 3200,
        "latency_p99_ms": 4500,
        "throughput_rps": 8.0,
        "cross_agent_success_rate": 0.95,
        "memory_per_agent_mb": 45.0,
    }


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_prompts() -> list:
    """Amostra de 10 prompts diversificados."""
    return [
        "ETA para 500 mil habitantes com tecnologia MBR",
        "Qual o custo de uma rodovia de 100 km?",
        "Terminal portuário em dragagem de -15m",
        "Barragem de concreto compactado 80m",
        "Linha de transmissão 765 kV ANEEL",
        "Estação de metrô em NATM",
        "Indenização por sinistro",
        "Modelo financeiro PPP",
        "Orçamento de infraestrutura",
        "Parecer técnico",
    ]


@pytest.fixture
def agent_list() -> list:
    """Lista de 20 agentes esperados."""
    return [
        "manta-00", "manta-01", "manta-02", "manta-03-s1", "manta-03-s2",
        "manta-03-s3", "manta-03-s4", "manta-03-s6", "manta-03-s7", "manta-03-s8",
        "manta-03-s9", "manta-03-s10", "manta-04", "manta-05", "manta-06",
        "manta-07", "manta-13", "manta-14", "manta-15", "manta-16",
    ]


@pytest.fixture
def rag_collections() -> dict:
    """Definição de RAG collections."""
    return {
        "san:v5.0:*": {"chunks": 2500, "status": "active"},
        "ene:v5.0:*": {"chunks": 3000, "status": "active"},
        "por:v5.0:*": {"chunks": 2000, "status": "active"},
        "aer:v5.0:*": {"chunks": 1800, "status": "active"},
        "bar:v5.0:*": {"chunks": 2200, "status": "active"},
        "rod:v5.0:*": {"chunks": 4000, "status": "active"},
        "oae:v5.0:*": {"chunks": 2000, "status": "active"},
        "fer:v5.0:*": {"chunks": 1500, "status": "active"},
        "met:v5.0:*": {"chunks": 2000, "status": "active"},
    }


# ============================================================================
# PYTEST PLUGINS / HOOKS
# ============================================================================

def pytest_runtest_makereport(item, call):
    """Hook para criar custom report items."""
    if call.excinfo is None:
        return

    # Log failures detalhadamente
    logger = logging.getLogger(__name__)
    if call.excinfo:
        logger.error(f"Test failed: {item.nodeid}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Hook para interceptar testes."""
    logger = logging.getLogger(__name__)
    logger.debug(f"Running test: {item.nodeid}")

    outcome = yield

    if outcome.excinfo:
        logger.error(f"Test {item.nodeid} failed")
    else:
        logger.debug(f"Test {item.nodeid} passed")


# ============================================================================
# HELPER FUNCTIONS (accessible via fixtures)
# ============================================================================

# ============================================================================
# COMMAND LINE OPTIONS
# ============================================================================

def pytest_addoption(parser):
    """Adiciona opções de linha de comando customizadas."""
    parser.addoption(
        "--include-slow",
        action="store_true",
        default=False,
        help="Include slow tests (performance baseline)"
    )
    parser.addoption(
        "--ci",
        action="store_true",
        default=False,
        help="Run only CI gate tests"
    )


def pytest_configure(config):
    """Aplicar filtros baseado em opções."""
    if config.getoption("--ci"):
        config.option.markexpr = "ci"
