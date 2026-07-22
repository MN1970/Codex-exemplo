"""
CAG Shadow Mode — Parallel Log Processor & Analysis Workers
Version: 1.0
Purpose: Distributed processing of shadow mode results for scalable analysis
"""

import asyncio
import json
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# =============================================================================
# PARALLEL WORKER TYPES
# =============================================================================

@dataclass
class ParallelTask:
    """Unit of work for parallel processing"""
    task_id: str
    task_type: str  # 'log_flush', 'analysis', 'metrics_compute', 'alert_check'
    payload: Dict
    created_at: str
    status: str = 'pending'  # pending, running, completed, failed
    result: Optional[Dict] = None
    error: Optional[str] = None


class ShadowModeLogProcessor:
    """
    Parallel processor for shadow mode logs.

    Distributes batch log processing across worker threads/processes:
    - Thread pool for I/O-bound tasks (Supabase writes)
    - Process pool for CPU-bound tasks (analysis, aggregation)
    """

    def __init__(
        self,
        num_thread_workers: int = 4,
        num_process_workers: int = 2,
        batch_size: int = 100,
        debug: bool = False
    ):
        """
        Args:
            num_thread_workers: I/O workers (Supabase writes)
            num_process_workers: CPU workers (analysis)
            batch_size: logs per batch
            debug: verbose logging
        """
        self.num_thread_workers = num_thread_workers
        self.num_process_workers = num_process_workers
        self.batch_size = batch_size
        self.debug = debug

        self.thread_pool = ThreadPoolExecutor(max_workers=num_thread_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=num_process_workers)

        self.task_queue = asyncio.Queue()
        self.results = {}

    async def process_batch_async(
        self,
        shadow_results: List[Dict],
        operation: str = 'flush'
    ) -> Dict:
        """
        Process batch of shadow results in parallel.

        Args:
            shadow_results: list of ShadowResult dicts
            operation: 'flush' (Supabase), 'analyze', 'aggregate'

        Returns:
            {
                'operation': operation,
                'total_items': count,
                'processed': count,
                'duration_ms': time,
                'results': [per-batch results]
            }
        """
        import time
        start_time = time.time()

        # Split into batches
        batches = [
            shadow_results[i:i + self.batch_size]
            for i in range(0, len(shadow_results), self.batch_size)
        ]

        if self.debug:
            print(f"[SHADOW] Processing {len(shadow_results)} results in {len(batches)} batches ({operation})")

        # Dispatch batches to workers
        tasks = []
        for batch_idx, batch in enumerate(batches):
            task = ParallelTask(
                task_id=f"{operation}-batch-{batch_idx}",
                task_type=operation,
                payload={'batch': batch, 'batch_idx': batch_idx},
                created_at=datetime.utcnow().isoformat()
            )
            tasks.append(task)

        # Execute in parallel based on operation type
        if operation == 'flush':
            results = await self._parallel_flush_batches(tasks)
        elif operation == 'analyze':
            results = await self._parallel_analyze_batches(tasks)
        elif operation == 'aggregate':
            results = await self._parallel_aggregate_batches(tasks)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        duration_ms = (time.time() - start_time) * 1000

        return {
            'operation': operation,
            'total_items': len(shadow_results),
            'batches': len(batches),
            'processed': sum(r.get('count', 0) for r in results if r),
            'duration_ms': duration_ms,
            'results': results
        }

    async def _parallel_flush_batches(self, tasks: List[ParallelTask]) -> List[Dict]:
        """Flush batches to Supabase in parallel (I/O-bound, thread pool)"""
        loop = asyncio.get_event_loop()

        async def flush_task(task: ParallelTask):
            try:
                # Simulate Supabase write (2-5ms per 100 items)
                result = await loop.run_in_executor(
                    self.thread_pool,
                    self._supabase_flush_batch,
                    task.payload['batch'],
                    task.task_id
                )
                return result
            except Exception as e:
                if self.debug:
                    print(f"[SHADOW] Flush error in {task.task_id}: {e}")
                return {'error': str(e), 'count': 0}

        results = await asyncio.gather(*[flush_task(t) for t in tasks])
        return results

    async def _parallel_analyze_batches(self, tasks: List[ParallelTask]) -> List[Dict]:
        """Analyze batches in parallel (CPU-bound, process pool)"""
        loop = asyncio.get_event_loop()

        async def analyze_task(task: ParallelTask):
            try:
                result = await loop.run_in_executor(
                    self.process_pool,
                    self._compute_batch_metrics,
                    task.payload['batch'],
                    task.task_id
                )
                return result
            except Exception as e:
                if self.debug:
                    print(f"[SHADOW] Analysis error in {task.task_id}: {e}")
                return {'error': str(e), 'metrics': {}}

        results = await asyncio.gather(*[analyze_task(t) for t in tasks])
        return results

    async def _parallel_aggregate_batches(self, tasks: List[ParallelTask]) -> List[Dict]:
        """Aggregate batch results in parallel"""
        loop = asyncio.get_event_loop()

        async def aggregate_task(task: ParallelTask):
            try:
                result = await loop.run_in_executor(
                    self.process_pool,
                    self._aggregate_batch,
                    task.payload['batch'],
                    task.task_id
                )
                return result
            except Exception as e:
                if self.debug:
                    print(f"[SHADOW] Aggregation error in {task.task_id}: {e}")
                return {'error': str(e), 'aggregates': {}}

        results = await asyncio.gather(*[aggregate_task(t) for t in tasks])
        return results

    # =========================================================================
    # EXECUTOR FUNCTIONS (run in thread/process pools)
    # =========================================================================

    @staticmethod
    def _supabase_flush_batch(batch: List[Dict], batch_id: str) -> Dict:
        """Flush batch to Supabase (thread pool)"""
        # TODO: Replace with actual Supabase insert
        # For now: simulate I/O
        import time
        time.sleep(0.005)  # 5ms per 100 items

        return {
            'batch_id': batch_id,
            'count': len(batch),
            'status': 'flushed'
        }

    @staticmethod
    def _compute_batch_metrics(batch: List[Dict], batch_id: str) -> Dict:
        """Compute metrics for batch (process pool, CPU-intensive)"""
        if not batch:
            return {'batch_id': batch_id, 'metrics': {}}

        # Extract metrics from shadow results
        agent_matches = sum(1 for r in batch if r.get('agent_match'))
        latencies_rag = [r.get('rag_latency_ms', 0) for r in batch if r.get('rag_latency_ms')]
        latencies_cag = [r.get('cag_latency_ms', 0) for r in batch if r.get('cag_latency_ms')]
        errors = sum(1 for r in batch if 'error' in str(r.get('rag_response_text', '')).lower())

        return {
            'batch_id': batch_id,
            'count': len(batch),
            'metrics': {
                'agent_match_rate': agent_matches / len(batch) if batch else 0,
                'rag_latency_p50': sorted(latencies_rag)[len(latencies_rag)//2] if latencies_rag else 0,
                'cag_latency_p50': sorted(latencies_cag)[len(latencies_cag)//2] if latencies_cag else 0,
                'error_count': errors,
                'error_rate': errors / len(batch) if batch else 0
            }
        }

    @staticmethod
    def _aggregate_batch(batch: List[Dict], batch_id: str) -> Dict:
        """Aggregate batch into daily stats entry"""
        if not batch:
            return {'batch_id': batch_id, 'aggregates': {}}

        dates = set()
        total_queries = len(batch)
        agent_matches = sum(1 for r in batch if r.get('agent_match'))
        errors = sum(1 for r in batch if 'error' in str(r.get('rag_response_text', '')).lower())

        return {
            'batch_id': batch_id,
            'aggregates': {
                'total_queries': total_queries,
                'agent_match_rate': agent_matches / total_queries if total_queries else 0,
                'error_rate': errors / total_queries if total_queries else 0,
                'dates': list(dates)
            }
        }

    def shutdown(self):
        """Gracefully shutdown thread and process pools"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


# =============================================================================
# PARALLEL ANALYSIS ENGINE
# =============================================================================

class ParallelAnalysisEngine:
    """
    Distributes analysis tasks across multiple workers.
    Computes metrics in parallel: accuracy, latency, errors, trends.
    """

    def __init__(self, num_workers: int = 4, debug: bool = False):
        self.num_workers = num_workers
        self.debug = debug
        self.executor = ProcessPoolExecutor(max_workers=num_workers)

    async def analyze_parallel(
        self,
        shadow_results: List[Dict],
        analysis_dimensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze shadow results across multiple dimensions in parallel.

        Args:
            shadow_results: list of ShadowResult dicts
            analysis_dimensions: list of dimensions to analyze
                Default: ['accuracy', 'latency', 'errors', 'trends', 'agents']

        Returns:
            {
                'accuracy': {...},
                'latency': {...},
                'errors': {...},
                'trends': {...},
                'agents': {...},
                'summary': {...}
            }
        """
        import time
        start_time = time.time()

        if not analysis_dimensions:
            analysis_dimensions = ['accuracy', 'latency', 'errors', 'trends', 'agents']

        loop = asyncio.get_event_loop()

        # Dispatch analysis tasks in parallel
        analysis_tasks = []
        for dimension in analysis_dimensions:
            task = loop.run_in_executor(
                self.executor,
                self._analyze_dimension,
                shadow_results,
                dimension
            )
            analysis_tasks.append(task)

        # Gather results
        results = await asyncio.gather(*analysis_tasks)

        duration_ms = (time.time() - start_time) * 1000

        # Combine results
        combined = {}
        for dimension, result in zip(analysis_dimensions, results):
            combined[dimension] = result

        # Summary
        combined['summary'] = {
            'total_results': len(shadow_results),
            'dimensions_analyzed': len(analysis_dimensions),
            'duration_ms': duration_ms,
            'timestamp': datetime.utcnow().isoformat()
        }

        return combined

    @staticmethod
    def _analyze_dimension(shadow_results: List[Dict], dimension: str) -> Dict:
        """Analyze single dimension (process pool, CPU-intensive)"""
        if dimension == 'accuracy':
            agent_matches = sum(1 for r in shadow_results if r.get('agent_match'))
            return {
                'agent_match_rate': agent_matches / len(shadow_results) if shadow_results else 0,
                'total_queries': len(shadow_results)
            }

        elif dimension == 'latency':
            rag_latencies = [r.get('rag_latency_ms', 0) for r in shadow_results if r.get('rag_latency_ms')]
            cag_latencies = [r.get('cag_latency_ms', 0) for r in shadow_results if r.get('cag_latency_ms')]

            return {
                'rag_p50_ms': sorted(rag_latencies)[len(rag_latencies)//2] if rag_latencies else 0,
                'rag_p95_ms': sorted(rag_latencies)[int(len(rag_latencies)*0.95)] if rag_latencies else 0,
                'cag_p50_ms': sorted(cag_latencies)[len(cag_latencies)//2] if cag_latencies else 0,
                'cag_p95_ms': sorted(cag_latencies)[int(len(cag_latencies)*0.95)] if cag_latencies else 0
            }

        elif dimension == 'errors':
            errors = sum(1 for r in shadow_results if 'error' in str(r.get('rag_response_text', '')).lower())
            return {
                'error_count': errors,
                'error_rate': errors / len(shadow_results) if shadow_results else 0
            }

        elif dimension == 'trends':
            # Group by date, compute trend
            by_date = {}
            for r in shadow_results:
                date = r.get('timestamp', '').split('T')[0]
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(r)

            trend = {}
            for date in sorted(by_date.keys()):
                daily = by_date[date]
                matches = sum(1 for d in daily if d.get('agent_match'))
                trend[date] = {
                    'queries': len(daily),
                    'match_rate': matches / len(daily) if daily else 0
                }

            return {'daily_trend': trend}

        elif dimension == 'agents':
            agent_hits = {}
            for r in shadow_results:
                rag_agent = r.get('rag_agent', 'unknown')
                if rag_agent not in agent_hits:
                    agent_hits[rag_agent] = {'total': 0, 'matches': 0}
                agent_hits[rag_agent]['total'] += 1
                if r.get('agent_match'):
                    agent_hits[rag_agent]['matches'] += 1

            return {
                'agents': {
                    agent: {
                        'total_queries': hits['total'],
                        'match_rate': hits['matches'] / hits['total'] if hits['total'] else 0
                    }
                    for agent, hits in agent_hits.items()
                }
            }

        else:
            return {'error': f'Unknown dimension: {dimension}'}

    def shutdown(self):
        """Shutdown executor"""
        self.executor.shutdown(wait=True)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("Parallel Shadow Mode Processor ready.")
    print("Usage: ShadowModeLogProcessor, ParallelAnalysisEngine")
