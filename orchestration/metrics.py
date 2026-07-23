"""
Coletor de Métricas — Manta Maestro v4.3
Rastreia performance, custo e eficiência de cada agente.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class TaskMetrics:
    """Métricas de uma tarefa individual"""
    agent: str
    timestamp: datetime
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    cache_hit: bool = False
    model: str = "sonnet"
    error: bool = False
    cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.tokens_input + self.tokens_output

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "timestamp": self.timestamp.isoformat(),
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "cache_hit": self.cache_hit,
            "model": self.model,
            "cost_usd": self.cost_usd,
            "error": self.error
        }


class MetricsCollector:
    """
    Coleta e analisa métricas de execução.

    Rastreia:
    - Latência por agente (p50, p95, p99)
    - Tokens por agente
    - Taxa de cache hit
    - Custo por agente
    - Gargalos de performance
    """

    def __init__(self):
        self.tasks: List[TaskMetrics] = []
        self.session_start = datetime.now()

    def record_task(
        self,
        agent: str,
        tokens: int = 0,
        latency: float = 0.0,
        cache_hit: bool = False,
        model: str = "sonnet",
        error: bool = False
    ) -> None:
        """Registrar métrica de uma tarefa"""
        # Estimar custo (Sonnet: $3/1M input, $15/1M output)
        input_tokens = tokens // 2
        output_tokens = tokens // 2
        input_cost = (input_tokens / 1_000_000) * 3
        output_cost = (output_tokens / 1_000_000) * 15
        total_cost = input_cost + output_cost

        metric = TaskMetrics(
            agent=agent,
            timestamp=datetime.now(),
            tokens_input=input_tokens,
            tokens_output=output_tokens,
            latency_ms=latency * 1000,
            cache_hit=cache_hit,
            model=model,
            error=error,
            cost_usd=total_cost
        )
        self.tasks.append(metric)

    def get_summary(self) -> Dict[str, Any]:
        """Obter resumo de métricas da sessão"""
        if not self.tasks:
            return {
                "total_tasks": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "cache_hit_rate": 0.0,
                "avg_latency_ms": 0.0
            }

        total_tokens = sum(t.total_tokens for t in self.tasks)
        total_cost = sum(t.cost_usd for t in self.tasks)
        cache_hits = sum(1 for t in self.tasks if t.cache_hit)
        avg_latency = sum(t.latency_ms for t in self.tasks) / len(self.tasks)

        return {
            "total_tasks": len(self.tasks),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "cache_hit_rate": (cache_hits / len(self.tasks)) * 100,
            "cache_savings_pct": (cache_hits / len(self.tasks)) * 85,  # 85% economia por hit
            "avg_latency_ms": avg_latency,
            "session_duration_s": (datetime.now() - self.session_start).total_seconds()
        }

    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Estatísticas por agente"""
        agents: Dict[str, List[TaskMetrics]] = {}

        for task in self.tasks:
            if task.agent not in agents:
                agents[task.agent] = []
            agents[task.agent].append(task)

        stats = {}
        for agent, tasks in agents.items():
            latencies = [t.latency_ms for t in tasks]
            tokens = [t.total_tokens for t in tasks]
            costs = [t.cost_usd for t in tasks]

            stats[agent] = {
                "count": len(tasks),
                "total_tokens": sum(tokens),
                "avg_tokens": sum(tokens) / len(tokens),
                "total_cost": sum(costs),
                "avg_cost": sum(costs) / len(costs),
                "latency_p50": sorted(latencies)[len(latencies) // 2],
                "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)],
                "latency_p99": sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else sorted(latencies)[-1],
                "cache_hit_rate": (sum(1 for t in tasks if t.cache_hit) / len(tasks)) * 100,
                "error_rate": (sum(1 for t in tasks if t.error) / len(tasks)) * 100
            }

        return stats

    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identificar gargalos de performance"""
        agent_stats = self.get_agent_stats()
        bottlenecks = []

        for agent, stats in agent_stats.items():
            # Critério 1: Latência alta (p99 > 10s)
            if stats["latency_p99"] > 10_000:
                bottlenecks.append({
                    "agent": agent,
                    "issue": "latency_high",
                    "value": f"{stats['latency_p99']:.0f}ms",
                    "recommendation": "Considerar usar modelo mais rápido (Haiku em vez de Sonnet)"
                })

            # Critério 2: Custo alto (> $10/execução)
            if stats["avg_cost"] > 10:
                bottlenecks.append({
                    "agent": agent,
                    "issue": "cost_high",
                    "value": f"${stats['avg_cost']:.2f}",
                    "recommendation": "Ativar Batch API ou compressão de documentos"
                })

            # Critério 3: Taxa de erro alta (> 5%)
            if stats["error_rate"] > 5:
                bottlenecks.append({
                    "agent": agent,
                    "issue": "error_rate_high",
                    "value": f"{stats['error_rate']:.1f}%",
                    "recommendation": "Investigar causa de falhas; adicionar retry logic"
                })

            # Critério 4: Cache hit rate baixo (< 50%)
            if stats["cache_hit_rate"] < 50:
                bottlenecks.append({
                    "agent": agent,
                    "issue": "cache_underutilized",
                    "value": f"{stats['cache_hit_rate']:.1f}%",
                    "recommendation": "Reutilizar mais contextos; ativar cache para mais padrões"
                })

        return sorted(bottlenecks, key=lambda x: x["value"], reverse=True)

    def export_json(self, filepath: str) -> None:
        """Exportar métricas para JSON"""
        data = {
            "session": {
                "start": self.session_start.isoformat(),
                "duration_s": (datetime.now() - self.session_start).total_seconds()
            },
            "summary": self.get_summary(),
            "agent_stats": self.get_agent_stats(),
            "bottlenecks": self.get_bottlenecks(),
            "tasks": [t.to_dict() for t in self.tasks]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def print_report(self) -> None:
        """Imprimir relatório completo de métricas"""
        summary = self.get_summary()
        agent_stats = self.get_agent_stats()
        bottlenecks = self.get_bottlenecks()

        print("\n" + "="*70)
        print("📊 RELATÓRIO DE MÉTRICAS — Manta Maestro v4.3")
        print("="*70)

        print("\n📈 RESUMO GERAL")
        print(f"  Tarefas executadas:  {summary['total_tasks']}")
        print(f"  Tempo total:         {summary['session_duration_s']:.1f}s")
        print(f"  Tokens processados:  {summary['total_tokens']:,}")
        print(f"  Custo total:         ${summary['total_cost']:.4f}")
        print(f"  Taxa de cache hit:   {summary['cache_hit_rate']:.1f}%")
        print(f"  Economia com cache:  ~{summary['cache_savings_pct']:.1f}%")
        print(f"  Latência média:      {summary['avg_latency_ms']:.1f}ms")

        print("\n🎯 PERFORMANCE POR AGENTE")
        for agent, stats in sorted(agent_stats.items()):
            print(f"\n  {agent}")
            print(f"    Tarefas:         {stats['count']}")
            print(f"    Tokens total:    {stats['total_tokens']:,}")
            print(f"    Custo:           ${stats['total_cost']:.4f}")
            print(f"    Latência P50:    {stats['latency_p50']:.1f}ms")
            print(f"    Latência P95:    {stats['latency_p95']:.1f}ms")
            print(f"    Cache hit rate:  {stats['cache_hit_rate']:.1f}%")
            print(f"    Taxa de erro:    {stats['error_rate']:.1f}%")

        if bottlenecks:
            print("\n⚠️  GARGALOS IDENTIFICADOS")
            for i, bn in enumerate(bottlenecks, 1):
                print(f"  {i}. {bn['agent']:12s} — {bn['issue']:25s} ({bn['value']})")
                print(f"     → {bn['recommendation']}")

        print("\n" + "="*70 + "\n")


# Exemplo de uso
if __name__ == "__main__":
    collector = MetricsCollector()

    # Simular algumas tarefas
    collector.record_task("S8", tokens=5000, latency=2.5, cache_hit=True)
    collector.record_task("S8", tokens=4800, latency=2.3, cache_hit=True)
    collector.record_task("S9", tokens=6000, latency=3.1, cache_hit=False)
    collector.record_task("S6", tokens=4500, latency=2.2, cache_hit=True)

    # Imprimir relatório
    # collector.print_report()
