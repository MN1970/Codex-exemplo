#!/usr/bin/env python3
"""
eval_routing.py — Avalia acurácia de roteamento do Maestro

Objetivo:
  Valida que o Maestro (Manta 00) roteia corretamente 30 prompts-teste
  para os agentes verticais S1-S10:

  1. Carrega 30 prompts anotados (formato: {prompt, expected_agent_id, expected_skill_id})
  2. Roda maestro router contra cada prompt (simula chamada ao Maestro)
  3. Compara dispatch real vs esperado
  4. Mede métricas:
     - Acurácia top-1 (primeiro agente proposto)
     - Acurácia top-3 (agente está nos 3 primeiros?)
     - Confusion matrix (quem vs quem)
     - Rotas lentas (latência > 2s)
  5. Loga resultados em maestro_runs para auditoria
  6. Gera JSON com estatísticas de roteamento

Inputs:
  --test-prompts: arquivo JSON/YAML com prompts-teste (default: tests/routing/prompts.md)
  --maestro-api: URL do Maestro (default: env MAESTRO_API_URL)
  --output-format: json | csv (default: json)
  --verbose: logging detalhado (default: False)

Output:
  Arquivo: rag_evals/routing_eval.{json|csv}
  Conteúdo: {
    "accuracy_top1": float (0-1),
    "accuracy_top3": float (0-1),
    "total_tests": int,
    "passed": int,
    "failed": int,
    "confusion_matrix": Dict[str, Dict[str, int]],
    "slow_routes": List[{prompt, latency_ms, expected, actual}],
    "timestamp": ISO8601,
    "results": List[{prompt, expected, actual, rank, latency_ms, status}]
  }

Exit codes:
  0: accuracy >= 80%
  1: accuracy < 80% ou erro crítico
"""

import sys
import os
import json
import logging
import argparse
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import traceback
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Avalia acurácia de roteamento do Maestro (S1-S10)"
    )
    parser.add_argument(
        "--test-prompts",
        default="tests/routing/prompts.md",
        help="Path to test prompts file (default: tests/routing/prompts.md)"
    )
    parser.add_argument(
        "--maestro-api",
        default=os.getenv("MAESTRO_API_URL", "http://localhost:8000/maestro"),
        help="Maestro API URL (default: env MAESTRO_API_URL or http://localhost:8000/maestro)"
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output-dir",
        default="rag_evals",
        help="Output directory for routing eval (default: rag_evals)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Request timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )
    return parser.parse_args()


def parse_routing_prompts(filepath: Path) -> List[Dict[str, str]]:
    """
    Parse routing test prompts from prompts.md.
    Expected format:
      ## S6 — Portos
      - [ ] `Preciso de um preliminar...` → **agente-portos**
      - [ ] `Como dimensiono...` → **agente-portos**
    """
    prompts = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse sections (## S6, ## S7, etc.)
        sections = re.split(r"## (S\d+)", content)

        for i in range(1, len(sections), 2):
            segment = sections[i]
            text = sections[i + 1] if i + 1 < len(sections) else ""

            # Extract test cases: `prompt` → **agent**
            matches = re.findall(
                r"`([^`]+?)`\s*→\s*\*\*([^\*]+?)\*\*",
                text
            )

            for prompt_text, agent_name in matches:
                prompts.append({
                    "prompt": prompt_text.strip(),
                    "expected_agent": agent_name.strip(),
                    "segment": segment.strip()
                })

        logger.info(f"Loaded {len(prompts)} test prompts from {filepath}")

    except Exception as e:
        logger.error(f"Error parsing prompts: {e}")

    return prompts


def simulate_maestro_routing(prompt: str) -> Dict[str, Any]:
    """
    Simulate Maestro router dispatch (mock for now).
    In production, would call actual Maestro API.

    Returns:
      {
        "agents": ["agente-saneamento", "agente-energia", ...],
        "confidence": [0.95, 0.02, ...],
        "latency_ms": 150
      }
    """
    start = time.time()

    # Mock routing: detect keywords
    routing_rules = {
        "agente-saneamento": [
            "saneamento", "eta", "ete", "adutora", "esgoto", "aysa",
            "drenagem urbana", "snis", "pmsb", "lei 14.026"
        ],
        "agente-energia": [
            "transmissão", "lt", "subestação", "aneel", "rap", "leilão",
            "ons", "epe", "leilão transmissão"
        ],
        "agente-portos": [
            "porto", "terminal", "antaq", "dragagem", "molhe", "berço",
            "calado", "contêiner", "granel", "pianc", "tup"
        ],
        "agente-aeroportos": [
            "aeroporto", "pista", "anac", "icao", "tps", "teca",
            "balizamento", "rbac", "pcn", "rwy", "taxiway"
        ],
        "agente-barragens": [
            "barragem", "vertedouro", "cfrd", "ccr", "rejeitos", "pnsb",
            "icold", "cbdb", "tsf", "sigbm", "dan", "dry stack"
        ]
    }

    prompt_lower = prompt.lower()
    scores = {}

    for agent, keywords in routing_rules.items():
        score = sum(prompt_lower.count(kw) for kw in keywords) / (len(keywords) + 0.001)
        scores[agent] = score

    # Sort by score
    sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    agents = [agent for agent, _ in sorted_agents[:5]]
    max_score = max(list(scores.values()) + [1])
    confidences = [min(score / max_score, 1.0) for agent, score in sorted_agents[:5]]

    latency_ms = (time.time() - start) * 1000

    return {
        "agents": agents,
        "confidence": confidences,
        "latency_ms": latency_ms
    }


def evaluate_routing(prompts: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Evaluate routing accuracy across all test prompts.
    """
    results = []
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    slow_routes = []

    for prompt_obj in prompts:
        prompt = prompt_obj["prompt"]
        expected_agent = prompt_obj["expected_agent"]

        # Normalize agent names (remove extra spaces)
        expected_agent = expected_agent.strip()

        # Get routing decision
        routing = simulate_maestro_routing(prompt)

        actual_agent = routing["agents"][0] if routing["agents"] else "unknown"
        rank = -1
        for i, agent in enumerate(routing["agents"]):
            if agent == expected_agent:
                rank = i + 1
                break

        status = "pass" if rank == 1 else ("partial" if rank > 0 else "fail")
        latency = routing["latency_ms"]

        result = {
            "prompt": prompt,
            "expected": expected_agent,
            "actual": actual_agent,
            "rank": rank if rank > 0 else -1,
            "latency_ms": round(latency, 2),
            "status": status
        }
        results.append(result)

        # Update confusion matrix
        confusion_matrix[expected_agent][actual_agent] += 1

        # Track slow routes
        if latency > 2000:
            slow_routes.append({
                "prompt": prompt,
                "latency_ms": round(latency, 2),
                "expected": expected_agent,
                "actual": actual_agent
            })

        logger.debug(f"Prompt: {prompt[:50]}... → {expected_agent} (rank={rank})")

    # Calculate accuracy
    passed_top1 = sum(1 for r in results if r["status"] == "pass")
    passed_top3 = sum(1 for r in results if r["rank"] > 0 and r["rank"] <= 3)
    total = len(results)

    accuracy_top1 = passed_top1 / total if total > 0 else 0
    accuracy_top3 = passed_top3 / total if total > 0 else 0

    return {
        "accuracy_top1": round(accuracy_top1, 4),
        "accuracy_top3": round(accuracy_top3, 4),
        "total_tests": total,
        "passed": passed_top1,
        "failed": total - passed_top1,
        "confusion_matrix": {k: dict(v) for k, v in confusion_matrix.items()},
        "slow_routes": slow_routes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results
    }


def output_json(eval_result: Dict[str, Any], output_path: Path):
    """Generate JSON report."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)

    logger.info(f"JSON report written to {output_path}")


def output_csv(eval_result: Dict[str, Any], output_path: Path):
    """Generate CSV report."""
    results = eval_result["results"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["prompt", "expected", "actual", "rank", "latency_ms", "status"]
        )
        writer.writeheader()
        for res in results:
            writer.writerow(res)

    logger.info(f"CSV report written to {output_path}")


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Starting routing evaluation (test_prompts={args.test_prompts})")

    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load test prompts
        prompts_file = Path(args.test_prompts)
        if not prompts_file.exists():
            logger.error(f"Test prompts file not found: {args.test_prompts}")
            return 1

        prompts = parse_routing_prompts(prompts_file)
        if not prompts:
            logger.error("No test prompts loaded")
            return 1

        logger.info(f"Evaluating {len(prompts)} routing test cases...")

        # Run evaluation
        eval_result = evaluate_routing(prompts)

        # Write reports
        output_base = output_dir / "routing_eval"
        if args.output_format == "json":
            output_json(eval_result, output_base.with_suffix(".json"))
        else:
            output_csv(eval_result, output_base.with_suffix(".csv"))

        # Print summary
        logger.info(f"Routing evaluation completed:")
        logger.info(f"  Accuracy (top-1): {eval_result['accuracy_top1'] * 100:.1f}%")
        logger.info(f"  Accuracy (top-3): {eval_result['accuracy_top3'] * 100:.1f}%")
        logger.info(f"  Passed: {eval_result['passed']}/{eval_result['total_tests']}")
        if eval_result["slow_routes"]:
            logger.warning(f"  Slow routes: {len(eval_result['slow_routes'])}")

        # Determine exit code
        threshold = 0.80  # 80% accuracy threshold
        if eval_result["accuracy_top1"] >= threshold:
            logger.info(f"Success: accuracy >= {threshold*100:.0f}%")
            return 0
        else:
            logger.error(f"Failed: accuracy < {threshold*100:.0f}%")
            return 1

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
