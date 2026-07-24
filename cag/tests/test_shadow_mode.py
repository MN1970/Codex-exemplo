"""
Tests for Shadow Mode Orchestrator
Version: 1.0
"""

import asyncio
import pytest
from datetime import datetime

from cag.shadow_mode import ShadowModeOrchestrator, ShadowModeAnalyzer, ShadowResult


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_rag_handler():
    """Mock v4.2 RAG handler"""
    def handler(query, session_id, context=None):
        return {
            'selected_agent': 'agente-saneamento',
            'agent': 'agente-saneamento',
            'confidence': 0.85,
            'response_text': f'RAG response for: {query[:50]}...',
            'sources': ['NBR 12.211', 'Lei 14.026']
        }
    return handler


@pytest.fixture
def mock_cag_orchestrator():
    """Mock CAG orchestrator"""
    class MockCAG:
        async def orchestrate(self, query, selected_agents, agent_responses_dict, session_id):
            await asyncio.sleep(0.01)  # simulate processing
            return {
                'selected_agents': ['agente-saneamento', 'agente-energia'],
                'final_response': f'CAG response for: {query[:50]}...',
                'metadata': {
                    'avg_confidence': 0.88,
                    'execution_time_ms': 1500
                }
            }
    return MockCAG()


@pytest.fixture
def shadow_orchestrator(mock_rag_handler, mock_cag_orchestrator):
    """Shadow orchestrator instance"""
    return ShadowModeOrchestrator(
        rag_handler=mock_rag_handler,
        cag_orchestrator=mock_cag_orchestrator,
        debug=False
    )


# =============================================================================
# TESTS: ShadowModeOrchestrator
# =============================================================================

@pytest.mark.asyncio
async def test_shadow_run_success(shadow_orchestrator):
    """Test successful shadow mode run"""
    rag_result, shadow_result = await shadow_orchestrator.shadow_run(
        query="Qual é a norma para ETA?",
        session_id="test-001"
    )

    # Verify RAG result returned
    assert rag_result['agent'] == 'agente-saneamento'
    assert rag_result['confidence'] == 0.85

    # Verify shadow result captured
    assert shadow_result.session_id == "test-001"
    assert shadow_result.rag_agent == 'agente-saneamento'
    assert shadow_result.cag_selected_agents == ['agente-saneamento', 'agente-energia']
    assert shadow_result.rag_latency_ms > 0
    assert shadow_result.cag_latency_ms > 0


@pytest.mark.asyncio
async def test_agent_match_detection(shadow_orchestrator):
    """Test detection of matching primary agents"""
    rag_result, shadow_result = await shadow_orchestrator.shadow_run(
        query="Qual é a norma para ETA?",
        session_id="test-002"
    )

    # CAG selects [agente-saneamento, agente-energia]
    # RAG selects agente-saneamento
    # First element matches → agent_match = True
    assert shadow_result.agent_match is True


@pytest.mark.asyncio
async def test_agent_mismatch_detection(shadow_orchestrator, mock_rag_handler, mock_cag_orchestrator):
    """Test detection of mismatched primary agents"""
    class MismatchCAG:
        async def orchestrate(self, query, selected_agents, agent_responses_dict, session_id):
            return {
                'selected_agents': ['agente-energia', 'agente-saneamento'],  # Different order
                'final_response': 'CAG response',
                'metadata': {'avg_confidence': 0.80}
            }

    shadow = ShadowModeOrchestrator(
        rag_handler=mock_rag_handler,
        cag_orchestrator=MismatchCAG(),
        debug=False
    )

    rag_result, shadow_result = await shadow.shadow_run(
        query="Query",
        session_id="test-003"
    )

    # Primary agents differ
    assert shadow_result.agent_match is False


@pytest.mark.asyncio
async def test_latency_comparison(shadow_orchestrator):
    """Test latency delta calculation"""
    rag_result, shadow_result = await shadow_orchestrator.shadow_run(
        query="Query",
        session_id="test-004"
    )

    # Verify latency metrics
    assert shadow_result.rag_latency_ms > 0
    assert shadow_result.cag_latency_ms > 0
    assert shadow_result.latency_delta_ms == shadow_result.cag_latency_ms - shadow_result.rag_latency_ms
    assert isinstance(shadow_result.latency_delta_pct, float)


@pytest.mark.asyncio
async def test_confidence_delta(shadow_orchestrator):
    """Test confidence delta calculation"""
    rag_result, shadow_result = await shadow_orchestrator.shadow_run(
        query="Query",
        session_id="test-005"
    )

    # RAG confidence: 0.85, CAG avg_confidence: 0.88
    assert shadow_result.rag_confidence == 0.85
    assert shadow_result.cag_avg_confidence == 0.88
    assert abs(shadow_result.confidence_delta - 0.03) < 0.01


@pytest.mark.asyncio
async def test_buffer_accumulation(shadow_orchestrator):
    """Test that shadow results accumulate in buffer"""
    # Clear buffer first
    shadow_orchestrator.results_buffer.clear()

    # Run 5 queries
    for i in range(5):
        await shadow_orchestrator.shadow_run(
            query=f"Query {i}",
            session_id=f"test-{i}"
        )

    # Verify buffer has 5 results
    assert len(shadow_orchestrator.results_buffer) == 5


@pytest.mark.asyncio
async def test_rag_error_handling(shadow_orchestrator):
    """Test graceful handling of RAG errors"""
    def failing_rag(query, session_id, context=None):
        raise Exception("RAG service unavailable")

    shadow = ShadowModeOrchestrator(
        rag_handler=failing_rag,
        cag_orchestrator=shadow_orchestrator.cag_orchestrator,
        debug=False
    )

    rag_result, shadow_result = await shadow.shadow_run(
        query="Query",
        session_id="test-error"
    )

    # RAG error should be captured
    assert 'error' in rag_result
    assert shadow_result.rag_latency_ms > 0


# =============================================================================
# TESTS: ShadowModeAnalyzer
# =============================================================================

@pytest.fixture
def analyzer():
    """Shadow mode analyzer instance"""
    return ShadowModeAnalyzer(debug=False)


def create_shadow_result(
    agent_match=True,
    rag_latency_ms=1000.0,
    cag_latency_ms=1050.0,
    rag_confidence=0.85,
    cag_confidence=0.88,
    has_error=False
):
    """Helper to create shadow results"""
    return ShadowResult(
        session_id="test",
        query="test query",
        timestamp=datetime.utcnow().isoformat(),
        rag_agent="agente-saneamento",
        rag_latency_ms=rag_latency_ms,
        rag_confidence=rag_confidence,
        rag_response_text="RAG" + (" error" if has_error else " response"),
        cag_selected_agents=['agente-saneamento'] if agent_match else ['agente-energia'],
        cag_latency_ms=cag_latency_ms,
        cag_avg_confidence=cag_confidence,
        cag_final_response="CAG" + (" error" if has_error else " response"),
        agent_match=agent_match,
        confidence_delta=cag_confidence - rag_confidence,
        latency_delta_ms=cag_latency_ms - rag_latency_ms,
        latency_delta_pct=((cag_latency_ms / rag_latency_ms) - 1) * 100,
        cag_metadata={}
    )


def test_analyze_all_pass(analyzer):
    """Test analysis when all criteria pass"""
    results = [
        create_shadow_result(agent_match=True, rag_latency_ms=1000, cag_latency_ms=1050)
        for _ in range(100)
    ]

    analysis = analyzer.analyze_results(results)

    assert analysis['go_decision'] is True
    assert analysis['accuracy_metrics']['agent_match_rate'] == 1.0
    assert len(analysis['blockers']) == 0
    assert analysis['next_phase'] == 'PILOT'


def test_analyze_low_agent_match(analyzer):
    """Test analysis with low agent match rate"""
    results = [
        create_shadow_result(agent_match=False)
        for _ in range(100)
    ]

    analysis = analyzer.analyze_results(results)

    assert analysis['go_decision'] is False
    assert any('Agent match rate' in b for b in analysis['blockers'])
    assert analysis['next_phase'] == 'TUNING_REQUIRED'


def test_analyze_high_latency(analyzer):
    """Test analysis with CAG latency exceeding threshold"""
    results = [
        create_shadow_result(
            agent_match=True,
            rag_latency_ms=1000.0,
            cag_latency_ms=1200.0  # 20% slower (exceeds 10% threshold)
        )
        for _ in range(100)
    ]

    analysis = analyzer.analyze_results(results)

    assert analysis['go_decision'] is False
    assert any('Latency' in b for b in analysis['blockers'])


def test_analyze_high_error_rate(analyzer):
    """Test analysis with high error rate"""
    results = [
        create_shadow_result(has_error=i < 2)  # 2% errors
        for i in range(100)
    ]

    analysis = analyzer.analyze_results(results)

    # 2% > 0.1% threshold
    assert analysis['error_rate'] > 0.001


def test_analyze_metrics_calculation(analyzer):
    """Test correct calculation of latency percentiles"""
    results = [
        create_shadow_result(
            agent_match=True,
            rag_latency_ms=float(i * 10),
            cag_latency_ms=float(i * 10 + 50)
        )
        for i in range(1, 101)
    ]

    analysis = analyzer.analyze_results(results)

    # Verify percentile calculations exist
    assert 'latency_metrics' in analysis
    assert analysis['latency_metrics']['rag_p50_ms'] > 0
    assert analysis['latency_metrics']['cag_p95_ms'] > 0


def test_analyze_empty_results(analyzer):
    """Test handling of empty results"""
    analysis = analyzer.analyze_results([])

    assert 'error' in analysis


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_end_to_end_shadow_flow(shadow_orchestrator, analyzer):
    """Test complete shadow mode flow: run → collect → analyze"""
    # Run 50 simulated queries
    results = []
    for i in range(50):
        rag_result, shadow_result = await shadow_orchestrator.shadow_run(
            query=f"Query {i}",
            session_id=f"e2e-{i}"
        )
        results.append(shadow_result)

    # Analyze accumulated results
    analysis = analyzer.analyze_results(results)

    # Should have metrics
    assert analysis['total_queries'] == 50
    assert 'accuracy_metrics' in analysis
    assert 'latency_metrics' in analysis
    assert 'go_decision' in analysis
