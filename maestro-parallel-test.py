#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MANTA MAESTRO - Parallel Routing Test (S2-b)
---------------------------------------------
Testa o routing do Maestro com 15 prompts em paralelo (pool de workers Sonnet).
Valida distribuição correta entre S01–S10 e mede latência/throughput.

Uso:
  python3 maestro-parallel-test.py --dry-run          # simula, nao chama API
  python3 maestro-parallel-test.py --workers 15       # roda com 15 workers
  python3 maestro-parallel-test.py --report report.md # salva relatorio

Esperado:
  - 15 prompts distribuídos em paralelo
  - Routing correto para cada setor (S01–S10)
  - Latência < 5s por prompt (com cache/batch)
  - Throughput: 15 prompts em <30s
"""
import argparse
import json
import time
import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Test prompts mapeados para setores esperados
TEST_PROMPTS = [
    # S01 — Rodovias
    {
        "id": "T01",
        "prompt": "Qual é a norma DNIT para projeto de rodovia de pista dupla com CBUQ?",
        "expected_sector": "S01",
        "keywords": ["rodovia", "DNIT", "CBUQ", "pavimento"]
    },
    {
        "id": "T02",
        "prompt": "Como dimensionar a base e sub-base em pavimento flexível (BGS)?",
        "expected_sector": "S01",
        "keywords": ["pavimento", "BGS", "terraplenagem", "SICRO"]
    },
    # S02 — OAE (Pontes/Viadutos)
    {
        "id": "T03",
        "prompt": "NBR 7187: quais são os estados limites de uma ponte?",
        "expected_sector": "S02",
        "keywords": ["ponte", "viaduto", "OAE", "NBR 7187"]
    },
    {
        "id": "T04",
        "prompt": "Como verificar a segurança de um túnel rodoviário contra colapso?",
        "expected_sector": "S02",
        "keywords": ["túnel", "rodoviário", "estabilidade"]
    },
    # S03 — Ferrovia
    {
        "id": "T05",
        "prompt": "Qual é o padrão de dormente em ferrovias brasileiras?",
        "expected_sector": "S03",
        "keywords": ["ferrovia", "dormente", "trilho", "via permanente", "AMV"]
    },
    {
        "id": "T06",
        "prompt": "Como dimensionar uma curva de ferrovia com raio mínimo?",
        "expected_sector": "S03",
        "keywords": ["ferrovia", "trilho", "curva", "via"]
    },
    # S04 — Metrô
    {
        "id": "T07",
        "prompt": "NATM: qual é o método de New Austrian Tunneling em metrô?",
        "expected_sector": "S04",
        "keywords": ["metrô", "estação", "NATM", "PSD", "linha"]
    },
    {
        "id": "T08",
        "prompt": "VLT: diferenças entre VLT e metrô leve (LRT)?",
        "expected_sector": "S04",
        "keywords": ["metrô", "VLT", "estação", "transporte"]
    },
    # S06 — Portos
    {
        "id": "T09",
        "prompt": "ANTAQ: qual é a regulação para concessão portuária?",
        "expected_sector": "S06",
        "keywords": ["porto", "terminal", "ANTAQ", "dragagem", "berço"]
    },
    {
        "id": "T10",
        "prompt": "Como dimensionar o calado de um terminal de contêiner?",
        "expected_sector": "S06",
        "keywords": ["porto", "calado", "contêiner", "granel"]
    },
    # S07 — Aeroportos
    {
        "id": "T11",
        "prompt": "RBAC 154: qual é a categoria de pista de pouso?",
        "expected_sector": "S07",
        "keywords": ["aeroporto", "pista", "ANAC", "ICAO", "balizamento"]
    },
    {
        "id": "T12",
        "prompt": "TPS: dimensões mínimas de terminal de passageiros?",
        "expected_sector": "S07",
        "keywords": ["aeroporto", "TPS", "TECA", "ponte de embarque"]
    },
    # S08 — Saneamento
    {
        "id": "T13",
        "prompt": "Lei 14.026: como financiar ETA em município pequeno?",
        "expected_sector": "S08",
        "keywords": ["saneamento", "ETA", "esgoto", "AySA", "SNIS"]
    },
    {
        "id": "T14",
        "prompt": "NBR 12.211: qual é o dimensionamento de adutora de água?",
        "expected_sector": "S08",
        "keywords": ["saneamento", "adutora", "água", "drenagem urbana"]
    },
    # S09 — Energia (Transmissão)
    {
        "id": "T15",
        "prompt": "ANEEL: qual é o regra R1-R5 para leilão de transmissão?",
        "expected_sector": "S09",
        "keywords": ["transmissão", "LT", "subestação", "ANEEL", "RAP"]
    },
]

@dataclass
class TestResult:
    test_id: str
    prompt: str
    expected_sector: str
    routed_sector: str
    latency_ms: float
    success: bool
    error: str = None

class MaestroRouter:
    """Simula o Maestro routing (substituir por API real)."""

    ROUTING_RULES = {
        "S01": ["rodovia", "pavimento", "cbuq", "bgs", "terraplenagem", "sicro", "dnit"],
        "S02": ["ponte", "viaduto", "oae", "nbr 7187", "túnel rodoviário"],
        "S03": ["ferrovia", "trilho", "amv", "dormente", "via permanente"],
        "S04": ["metrô", "estação", "natm", "psd", "linha", "vlt"],
        "S06": ["porto", "terminal portuário", "antaq", "dragagem", "molhe", "berço", "calado", "contêiner", "granel", "tup"],
        "S07": ["aeroporto", "pista", "anac", "icao", "rbac 154", "terminal de passageiros", "teca", "balizamento", "ponte de embarque"],
        "S08": ["saneamento", "eta", "ete", "adutora", "esgoto", "aysa", "drenagem urbana", "snis"],
        "S09": ["transmissão", "lt", "subestação", "aneel", "rap", "leilão transmissão", "ons", "epe"],
        "S10": ["barragem", "vertedouro", "cfrd", "ccr", "rejeitos", "pnsb", "icold", "cbdb", "tsf"],
    }

    @staticmethod
    def route(prompt: str) -> str:
        """Determina setor com base em keywords."""
        prompt_lower = prompt.lower()
        for sector, keywords in MaestroRouter.ROUTING_RULES.items():
            if any(kw in prompt_lower for kw in keywords):
                return sector
        return "UNKNOWN"

    @staticmethod
    async def query(prompt: str, timeout: float = 5.0) -> str:
        """Simula query ao Maestro (latência sintética)."""
        start = time.time()
        # Simula latência (substituir por API real)
        await asyncio.sleep(0.2)
        routed = MaestroRouter.route(prompt)
        latency = (time.time() - start) * 1000
        return routed, latency

class WorkerPool:
    """Pool de 15 workers processando prompts em paralelo."""

    def __init__(self, num_workers: int = 15):
        self.num_workers = num_workers
        self.results: List[TestResult] = []

    async def process_test(self, test: Dict) -> TestResult:
        """Processa um teste através do Maestro."""
        start = time.time()
        try:
            routed_sector, latency = await MaestroRouter.query(test["prompt"])
            success = routed_sector == test["expected_sector"]
            latency_ms = latency
        except Exception as e:
            success = False
            routed_sector = "ERROR"
            latency_ms = (time.time() - start) * 1000
            error_msg = str(e)
            return TestResult(
                test_id=test["id"],
                prompt=test["prompt"],
                expected_sector=test["expected_sector"],
                routed_sector=routed_sector,
                latency_ms=latency_ms,
                success=success,
                error=error_msg
            )

        return TestResult(
            test_id=test["id"],
            prompt=test["prompt"],
            expected_sector=test["expected_sector"],
            routed_sector=routed_sector,
            latency_ms=latency_ms,
            success=success
        )

    async def run_parallel(self, tests: List[Dict]) -> List[TestResult]:
        """Executa testes em paralelo usando worker pool."""
        # Cria semáforo para limitar a concorrência a num_workers
        semaphore = asyncio.Semaphore(self.num_workers)

        async def bounded_process(test):
            async with semaphore:
                return await self.process_test(test)

        tasks = [bounded_process(test) for test in tests]
        self.results = await asyncio.gather(*tasks)
        return self.results

def generate_report(results: List[TestResult]) -> str:
    """Gera relatório de testes."""
    lines = []
    lines.append("# Maestro Parallel Routing Test — Relatório\n")
    lines.append(f"**Data:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Total de testes:** {len(results)}")
    lines.append(f"**Sucesso:** {sum(1 for r in results if r.success)} / {len(results)}")
    lines.append(f"**Taxa de acerto:** {100 * sum(1 for r in results if r.success) // len(results)}%\n")

    # Latência
    latencies = [r.latency_ms for r in results if r.success]
    if latencies:
        lines.append(f"## Latência\n")
        lines.append(f"- **Mínima:** {min(latencies):.1f}ms")
        lines.append(f"- **Máxima:** {max(latencies):.1f}ms")
        lines.append(f"- **Média:** {sum(latencies) / len(latencies):.1f}ms\n")

    # Distribuição por setor
    lines.append("## Distribuição por Setor\n")
    distribution = defaultdict(lambda: {"correto": 0, "total": 0})
    for r in results:
        dist = distribution[r.expected_sector]
        dist["total"] += 1
        if r.success:
            dist["correto"] += 1

    lines.append("| Setor | Corretos | Total | Taxa |\n")
    lines.append("|-------|----------|-------|------|\n")
    for sector in sorted(distribution.keys()):
        d = distribution[sector]
        taxa = 100 * d["correto"] // d["total"] if d["total"] > 0 else 0
        lines.append(f"| {sector} | {d['correto']} | {d['total']} | {taxa}% |\n")

    # Detalhes de falhas
    failures = [r for r in results if not r.success]
    if failures:
        lines.append("\n## Falhas de Routing\n")
        lines.append("| ID | Esperado | Roteado | Prompt |\n")
        lines.append("|-------|----------|---------|--------|\n")
        for f in failures:
            lines.append(f"| {f.test_id} | {f.expected_sector} | {f.routed_sector} | {f.prompt[:40]}... |\n")

    # Detalhes completos
    lines.append("\n## Detalhes Completos\n")
    lines.append("| ID | Esperado | Roteado | Latência | Status |\n")
    lines.append("|-------|----------|---------|----------|--------|\n")
    for r in sorted(results, key=lambda x: x.test_id):
        status = "✅" if r.success else "❌"
        lines.append(f"| {r.test_id} | {r.expected_sector} | {r.routed_sector} | {r.latency_ms:.1f}ms | {status} |\n")

    return "\n".join(lines)

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=15, help="Número de workers paralelos")
    ap.add_argument("--dry-run", action="store_true", help="Apenas simula, não executa")
    ap.add_argument("--report", help="Salvar relatório em arquivo")
    a = ap.parse_args()

    if a.dry_run:
        print(f"[dry-run] Processaria {len(TEST_PROMPTS)} testes com {a.workers} workers")
        print(f"\nPrompts de teste:")
        for t in TEST_PROMPTS:
            print(f"  {t['id']}: {t['prompt'][:60]}... → {t['expected_sector']}")
        return

    print(f"Iniciando teste de routing paralelo...")
    print(f"- {len(TEST_PROMPTS)} prompts")
    print(f"- {a.workers} workers concorrentes")
    print(f"- Setores: S01–S10\n")

    pool = WorkerPool(num_workers=a.workers)
    start = time.time()
    results = await pool.run_parallel(TEST_PROMPTS)
    elapsed = time.time() - start

    print(f"✅ Testes completados em {elapsed:.2f}s")
    print(f"Throughput: {len(TEST_PROMPTS) / elapsed:.1f} prompts/seg\n")

    report = generate_report(results)
    print(report)

    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\nRelatório salvo: {a.report}")

if __name__ == "__main__":
    asyncio.run(main())
