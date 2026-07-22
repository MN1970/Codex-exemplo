"""
Tests for Parallel Shadow Mode Processing
Version: 1.0
"""

import asyncio
import pytest
from datetime import datetime

from cag.shadow_mode.parallel_processor import (
    ShadowModeLogProcessor,
    ParallelAnalysisEngine,
    ParallelTask
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def log_processor():
    """Parallel log processor instance"""
    processor = ShadowModeLogProcessor(
        num_thread_workers=2,
        num_process_workers=1,
        batch_size=10,
        debug=False
    )
    yield processor
    processor.shutdown()


@pytest.fixture
def analysis_engine():
    """Parallel analysis engine instance"""
    engine = ParallelAnalysisEngine(num_workers=2, debug=False)
    yield engine
    engine.shutdown()


def create_mock_shadow_results(count: int = 100) -> list:
    """Create mock shadow results for testing"""
    results = []
    for i in range(count):
        results.append({
            'session_id': f'test-{i}',
            'query': f'Query {i}',
            'timestamp': datetime.utcnow().isoformat(),
            'rag_agent': 'agente-saneamento' if i % 2 == 0 else 'agente-energia',
            'rag_latency_ms': 1000.0 + (i % 100),
            'rag_confidence': 0.85,
            'rag_response_text': f'RAG response {i}',
            'cag_selected_agents': ['agente-saneamento'],
            'cag_latency_ms': 1050.0 + (i % 100),
            'cag_avg_confidence': 0.88,
            'cag_final_response': f'CAG response {i}',
            'agent_match': i % 10 != 0,  # 90% match rate
            'confidence_delta': 0.03,
            'latency_delta_ms': 50.0,
            'latency_delta_pct': 5.0,
            'cag_metadata': {}
        })
    return results


# =============================================================================
# TESTS: ShadowModeLogProcessor
# =============================================================================

@pytest.mark.asyncio
async def test_processor_flush_batch(log_processor):
    """Test parallel batch flushing"""
    results = create_mock_shadow_results(50)

    output = await log_processor.process_batch_async(results, operation='flush')

    assert output['operation'] == 'flush'
    assert output['total_items'] == 50
    assert output['batches'] == 5  # 50 items / 10 batch size
    assert output['processed'] == 50
    assert output['duration_ms'] > 0


@pytest.mark.asyncio
async def test_processor_analyze_batch(log_processor):
    """Test parallel batch analysis"""
    results = create_mock_shadow_results(50)

    output = await log_processor.process_batch_async(results, operation='analyze')

    assert output['operation'] == 'analyze'
    assert output['total_items'] == 50
    assert 'results' in output
    # Each batch should have metrics
    assert len(output['results']) > 0


@pytest.mark.asyncio
async def test_processor_aggregate_batch(log_processor):
    """Test parallel batch aggregation"""
    results = create_mock_shadow_results(100)

    output = await log_processor.process_batch_async(results, operation='aggregate')

    assert output['operation'] == 'aggregate'
    assert output['total_items'] == 100
    assert 'results' in output


@pytest.mark.asyncio
async def test_processor_large_batch(log_processor):
    """Test processing large batch (1000+ items)"""
    results = create_mock_shadow_results(1000)

    output = await log_processor.process_batch_async(results, operation='flush')

    assert output['total_items'] == 1000
    assert output['batches'] == 100  # 1000 / 10
    assert output['processed'] == 1000


@pytest.mark.asyncio
async def test_processor_empty_batch(log_processor):
    """Test handling of empty batch"""
    results = []

    output = await log_processor.process_batch_async(results, operation='flush')

    assert output['total_items'] == 0
    assert output['batches'] == 0


@pytest.mark.asyncio
async def test_processor_invalid_operation(log_processor):
    """Test error handling for invalid operation"""
    results = create_mock_shadow_results(10)

    with pytest.raises(ValueError):
        await log_processor.process_batch_async(results, operation='invalid_op')


# =============================================================================
# TESTS: ParallelAnalysisEngine
# =============================================================================

@pytest.mark.asyncio
async def test_analysis_single_dimension(analysis_engine):
    """Test analyzing single dimension"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results, ['accuracy'])

    assert 'accuracy' in output
    assert 'summary' in output
    assert output['accuracy']['agent_match_rate'] == 0.9  # 90% match rate


@pytest.mark.asyncio
async def test_analysis_multiple_dimensions(analysis_engine):
    """Test analyzing multiple dimensions in parallel"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(
        results,
        ['accuracy', 'latency', 'errors']
    )

    assert 'accuracy' in output
    assert 'latency' in output
    assert 'errors' in output
    assert 'summary' in output


@pytest.mark.asyncio
async def test_analysis_all_dimensions(analysis_engine):
    """Test analyzing all standard dimensions"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results)

    assert 'accuracy' in output
    assert 'latency' in output
    assert 'errors' in output
    assert 'trends' in output
    assert 'agents' in output


@pytest.mark.asyncio
async def test_analysis_accuracy_metrics(analysis_engine):
    """Test accuracy metrics computation"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results, ['accuracy'])

    accuracy = output['accuracy']
    assert 'agent_match_rate' in accuracy
    assert 'total_queries' in accuracy
    assert accuracy['agent_match_rate'] == 0.9
    assert accuracy['total_queries'] == 100


@pytest.mark.asyncio
async def test_analysis_latency_metrics(analysis_engine):
    """Test latency metrics computation"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results, ['latency'])

    latency = output['latency']
    assert 'rag_p50_ms' in latency
    assert 'rag_p95_ms' in latency
    assert 'cag_p50_ms' in latency
    assert 'cag_p95_ms' in latency
    assert latency['rag_p50_ms'] > 0
    assert latency['cag_p50_ms'] > 0


@pytest.mark.asyncio
async def test_analysis_error_metrics(analysis_engine):
    """Test error metrics computation"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results, ['errors'])

    errors = output['errors']
    assert 'error_count' in errors
    assert 'error_rate' in errors


@pytest.mark.asyncio
async def test_analysis_trends(analysis_engine):
    """Test trend analysis across dates"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results, ['trends'])

    trends = output['trends']
    assert 'daily_trend' in trends
    # All results have same timestamp, so should be 1 day
    assert len(trends['daily_trend']) >= 1


@pytest.mark.asyncio
async def test_analysis_agents(analysis_engine):
    """Test agent-level analysis"""
    results = create_mock_shadow_results(100)

    output = await analysis_engine.analyze_parallel(results, ['agents'])

    agents = output['agents']
    assert 'agents' in agents
    # Should have metrics for both agents
    assert len(agents['agents']) >= 1


@pytest.mark.asyncio
async def test_analysis_performance(analysis_engine):
    """Test performance of parallel analysis"""
    import time
    results = create_mock_shadow_results(1000)

    start_time = time.time()
    output = await analysis_engine.analyze_parallel(results)
    duration_ms = (time.time() - start_time) * 1000

    # Should complete in reasonable time (parallel > sequential)
    assert duration_ms < 5000  # 5 seconds max
    assert output['summary']['total_results'] == 1000


# =============================================================================
# TESTS: ParallelTask
# =============================================================================

def test_parallel_task_creation():
    """Test creation of parallel task"""
    task = ParallelTask(
        task_id='test-001',
        task_type='flush',
        payload={'items': 100},
        created_at=datetime.utcnow().isoformat()
    )

    assert task.task_id == 'test-001'
    assert task.task_type == 'flush'
    assert task.status == 'pending'
    assert task.result is None


def test_parallel_task_update():
    """Test updating parallel task status"""
    task = ParallelTask(
        task_id='test-001',
        task_type='flush',
        payload={'items': 100},
        created_at=datetime.utcnow().isoformat()
    )

    task.status = 'running'
    assert task.status == 'running'

    task.status = 'completed'
    task.result = {'flushed': 100}
    assert task.status == 'completed'
    assert task.result['flushed'] == 100


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_end_to_end_parallel_pipeline(log_processor, analysis_engine):
    """Test complete parallel pipeline: flush → analyze → report"""
    results = create_mock_shadow_results(500)

    # Step 1: Flush in parallel
    flush_output = await log_processor.process_batch_async(results, 'flush')
    assert flush_output['processed'] == 500

    # Step 2: Analyze in parallel
    analysis_output = await analysis_engine.analyze_parallel(results)
    assert analysis_output['accuracy']['agent_match_rate'] == 0.9

    # Step 3: Verify summary
    summary = analysis_output['summary']
    assert summary['total_results'] == 500
    assert summary['dimensions_analyzed'] == 5


@pytest.mark.asyncio
async def test_parallel_robustness(log_processor, analysis_engine):
    """Test robustness under various conditions"""
    # Mixed batch sizes
    results_small = create_mock_shadow_results(10)
    results_large = create_mock_shadow_results(1000)

    # Process all in parallel
    tasks = [
        log_processor.process_batch_async(results_small, 'flush'),
        log_processor.process_batch_async(results_large, 'flush'),
        analysis_engine.analyze_parallel(results_small),
    ]

    results = await asyncio.gather(*tasks)

    assert all(r is not None for r in results)
    assert results[0]['processed'] == 10
    assert results[1]['processed'] == 1000
