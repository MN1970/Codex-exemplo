#!/usr/bin/env python3
"""
Maestro v4.3 Parallel Routing Tests
Run all 4 test cases against the 8-agent pool and validate results.

Usage:
    python scripts/run-parallel-tests.py [--verbose] [--output results.json]
"""

import asyncio
import json
import time
import sys
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Import executor (mock for demo)
sys.path.insert(0, "src")
from maestro_parallel_executor import MaestroParallelExecutor


@dataclass
class TestCase:
    name: str
    prompt: str
    expected_agents: List[str]
    expected_priorities: List[int]
    expect_discipline_coverage: int  # min number of disciplines


class MaestroParallelTester:
    """Run test suite for 8-agent parallel pool"""

    TESTS = [
        TestCase(
            name="TESTE 1: Saneamento + Energia (PRIORITY)",
            prompt="""
Projeto de ETA (Estação de Tratamento de Água) com areia quartzosa
e carvão ativado, servindo 150 mil habitantes na região metropolitana
de São Paulo. A água captada vem de rio próximo à subestação de 345 kV.
Preciso de:
- Estimativa de custo
- Cronograma executivo
- Análise de viabilidade (potencial de negócio)
- Parecer legal sobre concessão AySA vs. privado
            """,
            expected_agents=[
                "agente-saneamento",  # S8 PRIORITY
                "agente-energia",     # S9 PRIORITY
                "orcamento",          # Manta-05
                "cronograma",         # Manta-07
                "contratual"          # Manta-02
            ],
            expected_priorities=[200, 200, 100, 100, 90],
            expect_discipline_coverage=3
        ),

        TestCase(
            name="TESTE 2: Energia + Imobiliário",
            prompt="""
Projeto de subestação 138/13,8 kV em área urbana, com
possibilidade de desenvolvimento imobiliário no terreno vizinho.
Necessário:
- Projeto de transmissão (LT 138 kV)
- Estimativa orçamentária (capex SE)
- Análise de viabilidade da PPP
- Apresentação executiva para stakeholders
- Cronograma (SAE + obras civis)
            """,
            expected_agents=[
                "agente-energia",     # S9 PRIORITY
                "imobiliario",        # Manta-04
                "orcamento",          # Manta-05
                "cronograma",         # Manta-07
                "apresentacoes"       # Manta-14
            ],
            expected_priorities=[200, 50, 100, 100, 50],
            expect_discipline_coverage=3
        ),

        TestCase(
            name="TESTE 3: Saneamento (ETE + Reutilização)",
            prompt="""
Estação de Tratamento de Esgoto (ETE) no interior de São Paulo,
com tratamento avançado (MBR + RO) para reuso industrial.
Preciso de:
- Projeto técnico (NBR 12.209, 9.651)
- Orçamento com análise de OPEX/CAPEX
- Cronograma de 36 meses
- Viabilidade comercial (venda de água reciclada)
- Documentação contratual (concessão municipal)
            """,
            expected_agents=[
                "agente-saneamento",  # S8 PRIORITY
                "orcamento",          # Manta-05
                "cronograma",         # Manta-07
                "bd",                 # Manta-13 (viabilidade)
                "contratual"          # Manta-02
            ],
            expected_priorities=[200, 100, 100, 70, 90],
            expect_discipline_coverage=2
        ),

        TestCase(
            name="TESTE 4: Multi-Disciplina (Rodovia + OAE + Drenagem)",
            prompt="""
Licitação de concessão de rodovia BR-116 trecho São Paulo-RJ,
inclui construção de OAE (ponte) e drenagem urbana.
Necessário:
- Orçamento detalhado (SICRO + BDI)
- Cronograma macro (54 meses)
- Parecer legal (Lei 8.987 + licitação 14.133)
- Análise de viabilidade (receita de pedágios)
- Apresentação técnica para leilão
            """,
            expected_agents=[
                "orcamento",          # Manta-05
                "cronograma",         # Manta-07
                "contratual",         # Manta-02
                "bd",                 # Manta-13
                "apresentacoes"       # Manta-14
            ],
            expected_priorities=[100, 100, 90, 70, 50],
            expect_discipline_coverage=1  # Infrastructure (not S8/S9)
        ),
    ]

    PASS_CRITERIA = {
        "agents_triggered": 5,      # Min agents
        "latency_p50_ms": 6000,     # Max 6s
        "success_rate": 0.95,       # 95%+ agents succeed
        "priority_ordering": True,  # S8/S9 first if applicable
        "discipline_coverage": True # All mentioned disciplines covered
    }

    def __init__(self):
        self.executor = MaestroParallelExecutor()
        self.results = []

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all 4 test cases"""
        print("=" * 80)
        print("MAESTRO v4.3 — PARALLEL ROUTING TESTS")
        print("=" * 80)
        print()

        summary = {
            "total_tests": len(self.TESTS),
            "passed": 0,
            "failed": 0,
            "tests": []
        }

        for i, test in enumerate(self.TESTS, 1):
            print(f"[{i}/4] {test.name}")
            print("-" * 80)

            result = await self._run_test(test)
            summary["tests"].append(result)

            if result["status"] == "PASS":
                summary["passed"] += 1
                print("✓ PASS")
            else:
                summary["failed"] += 1
                print(f"✗ FAIL: {result['failures']}")

            print()

        # Overall summary
        print("=" * 80)
        print(f"SUMMARY: {summary['passed']}/{summary['total_tests']} PASSED")
        print("=" * 80)

        return summary

    async def _run_test(self, test: TestCase) -> Dict[str, Any]:
        """Run a single test case"""
        start = time.time()

        # Execute
        executor_result = await self.executor.execute_parallel(test.prompt)

        duration_ms = (time.time() - start) * 1000

        # Validate
        agents = executor_result["results"]
        successes = sum(1 for a in agents if a["status"] == "success")
        success_rate = successes / len(agents) if agents else 0

        failures = []

        # Check 1: Agent count
        if len(agents) < self.PASS_CRITERIA["agents_triggered"]:
            failures.append(
                f"Too few agents: {len(agents)} < {self.PASS_CRITERIA['agents_triggered']}"
            )

        # Check 2: Latency
        if duration_ms > self.PASS_CRITERIA["latency_p50_ms"]:
            failures.append(
                f"Too slow: {duration_ms:.0f}ms > {self.PASS_CRITERIA['latency_p50_ms']}ms"
            )

        # Check 3: Success rate
        if success_rate < self.PASS_CRITERIA["success_rate"]:
            failures.append(
                f"Low success rate: {success_rate:.1%} < {self.PASS_CRITERIA['success_rate']:.1%}"
            )

        # Check 4: Priority ordering (if S8/S9 expected)
        ranked = executor_result["ranked_by_relevance"]
        if ranked:
            first_agent = ranked[0]["agent_name"]
            if test.expected_agents and first_agent != test.expected_agents[0]:
                failures.append(
                    f"Wrong priority order: expected {test.expected_agents[0]}, got {first_agent}"
                )

        # Check 5: Expected agents present
        agent_names = {a["agent_name"] for a in agents}
        missing = set(test.expected_agents) - agent_names
        if missing:
            failures.append(f"Missing agents: {', '.join(missing)}")

        status = "PASS" if not failures else "FAIL"

        return {
            "test_name": test.name,
            "status": status,
            "duration_ms": duration_ms,
            "agents_triggered": len(agents),
            "success_count": successes,
            "success_rate": f"{success_rate:.1%}",
            "agents": [a["agent_name"] for a in agents],
            "failures": failures or None
        }


async def main():
    """Run full test suite"""
    tester = MaestroParallelTester()
    summary = await tester.run_all_tests()

    # Output summary
    print("\n📊 DETAILED RESULTS")
    print(json.dumps(summary, indent=2))

    # Exit code
    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
