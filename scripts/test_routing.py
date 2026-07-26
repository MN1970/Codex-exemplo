#!/usr/bin/env python3
"""
Test runner for Maestro (Manta 00) routing validation.
Reads prompts from tests/routing/prompts.md and validates routing accuracy + latency.
"""

import json
import re
import sys
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Dict, Any
import os

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ anthropic package required: pip install anthropic")
    sys.exit(1)


class RoutingTest:
    def __init__(self, prompt: str, expected_agent: str):
        self.prompt = prompt
        self.expected_agent = expected_agent
        self.routed_agent = None
        self.latency_ms = 0
        self.score = 0
        self.status = "pending"
        self.confidence = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "expected_agent": self.expected_agent,
            "routed_agent": self.routed_agent,
            "latency_ms": self.latency_ms,
            "score": self.score,
            "confidence": self.confidence,
            "status": self.status,
        }


def parse_prompts_md(file_path: Path) -> List[RoutingTest]:
    """Parse tests/routing/prompts.md and extract test cases."""
    tests = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match pattern: `prompt text` → **agent-name**
    pattern = r"- \[ \] `([^`]+)` → \*\*([^*]+)\*\*"
    matches = re.findall(pattern, content)

    for prompt, agent in matches:
        tests.append(RoutingTest(prompt, agent))

    return tests


def route_prompt(client: Anthropic, prompt: str) -> tuple[str, float]:
    """
    Route a prompt through Maestro (Manta 00) and measure latency.
    Returns: (routed_agent_slug, latency_ms)
    """
    # Maestro system prompt (simplified routing logic)
    system = """Você é o Maestro (Manta 00), o orquestrador central de agentes IA da Manta Associados.
Sua função é analisar uma consulta do usuário e rotear para o agente especializado mais apropriado.

Responda APENAS com o slug do agente no formato: `agente-<segmento>` ou `manta-<codigo>`

Regras de roteamento:
- Se menciona saneamento, ETA, ETE, adutora, esgoto, AySA, drenagem urbana, SNIS → agente-saneamento
- Se menciona transmissão, LT, subestação, ANEEL, RAP, leilão, ONS, EPE, torre, ACSR → agente-energia
- Se menciona porto, terminal, ANTAQ, dragagem, molhe, berço, calado, contêiner, granel → agente-portos
- Se menciona aeroporto, pista, ANAC, ICAO, TPS, TECA, balizamento, PAPI, RWY → agente-aeroportos
- Se menciona barragem, vertedouro, CFRD, CCR, rejeitos, PNSB, ICOLD, CBDB, TSF → agente-barragens
- Se menciona rodovia, pavimento, CBUQ, DNIT, SICRO, terraplenagem → agente-infraestrutura S1
- Se menciona ponte, viaduto, OAE, NBR 7187 → agente-infraestrutura S2
- Se menciona ferrovia, trilho, AMV, via permanente → agente-infraestrutura S3
- Se menciona metrô, estação, NATM, VLT → agente-infraestrutura S4

Casos ambíguos: prefira o agente mais específico, não o primeiro match."""

    start_time = time.perf_counter()
    message = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=50,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000
    response_text = message.content[0].text.strip()

    # Extract agent slug from response
    agent_match = re.search(r"(agente-\w+|manta-\w+)", response_text)
    routed_agent = agent_match.group(1) if agent_match else "unknown"

    return routed_agent, latency_ms


def score_match(expected: str, actual: str) -> tuple[int, float]:
    """
    Score a routing match.
    Returns: (score 0-100, confidence 0-1)
    """
    if expected == actual:
        return 100, 1.0
    elif expected.startswith("agente-") and actual.startswith("agente-"):
        # Both are agents, check segment match
        exp_seg = expected.split("-")[1]
        act_seg = actual.split("-")[1]
        if exp_seg == act_seg:
            return 100, 1.0
        # Same agent type but different segment
        return 25, 0.3
    elif expected.startswith("manta-") or actual.startswith("manta-"):
        # Horizontal agent
        if expected == actual:
            return 100, 1.0
        return 10, 0.1
    else:
        return 0, 0.0


def run_tests(
    tests: List[RoutingTest],
    client: Anthropic,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Run all routing tests and collect results."""
    latencies = []
    passed = 0

    print(f"🧪 Running {len(tests)} routing tests...\n")

    for i, test in enumerate(tests, 1):
        if verbose:
            print(f"[{i}/{len(tests)}] Testing: {test.prompt[:60]}...", end="", flush=True)

        try:
            test.routed_agent, test.latency_ms = route_prompt(client, test.prompt)
            test.score, test.confidence = score_match(
                test.expected_agent, test.routed_agent
            )
            test.status = "passed" if test.score == 100 else "failed"

            if test.status == "passed":
                passed += 1

            latencies.append(test.latency_ms)

            if verbose:
                status_icon = "✅" if test.status == "passed" else "❌"
                print(
                    f" {status_icon} {test.routed_agent} ({test.latency_ms:.0f}ms)"
                )
        except Exception as e:
            test.status = "error"
            test.routed_agent = f"error: {str(e)}"
            if verbose:
                print(f" ❌ ERROR: {e}")

        # Rate limit: space out API calls
        if i < len(tests):
            time.sleep(0.5)

    # Calculate metrics
    latencies.sort()
    median_latency = latencies[len(latencies) // 2] if latencies else 0
    p95_latency = latencies[int(len(latencies) * 0.95)] if latencies else 0

    accuracy = (passed / len(tests) * 100) if tests else 0

    return {
        "tests": [t.to_dict() for t in tests],
        "metrics": {
            "total": len(tests),
            "passed": passed,
            "failed": len(tests) - passed,
            "accuracy_percent": accuracy,
            "latency_median_ms": median_latency,
            "latency_p95_ms": p95_latency,
            "latency_max_ms": max(latencies) if latencies else 0,
        },
    }


def main():
    parser = ArgumentParser(
        description="Run Maestro routing tests from prompts.md"
    )
    parser.add_argument(
        "prompts_file",
        type=Path,
        help="Path to tests/routing/prompts.md",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    args = parser.parse_args()

    # Initialize Anthropic client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    # Parse test cases
    if not args.prompts_file.exists():
        print(f"❌ File not found: {args.prompts_file}")
        sys.exit(1)

    tests = parse_prompts_md(args.prompts_file)
    print(f"📖 Loaded {len(tests)} test cases from {args.prompts_file}\n")

    # Run tests
    results = run_tests(tests, client, verbose=args.verbose)

    # Format output
    if args.format == "json":
        output = json.dumps(results, indent=2)
    else:
        # Text format
        output = f"""
Maestro Routing Test Results
============================

Accuracy: {results['metrics']['accuracy_percent']:.1f}% ({results['metrics']['passed']}/{results['metrics']['total']})
Median Latency: {results['metrics']['latency_median_ms']:.0f}ms
P95 Latency: {results['metrics']['latency_p95_ms']:.0f}ms
Max Latency: {results['metrics']['latency_max_ms']:.0f}ms

Failed Tests:
"""
        for test_result in results["tests"]:
            if test_result["status"] == "failed":
                output += f"\n  ❌ {test_result['prompt'][:70]}\n"
                output += f"     Expected: {test_result['expected_agent']}\n"
                output += f"     Got: {test_result['routed_agent']}\n"

    # Output
    if args.output:
        args.output.write_text(output)
        print(f"✅ Results written to {args.output}")
    else:
        print(output)

    # Exit with failure if tests failed
    if results["metrics"]["accuracy_percent"] < 90:
        sys.exit(1)


if __name__ == "__main__":
    main()
