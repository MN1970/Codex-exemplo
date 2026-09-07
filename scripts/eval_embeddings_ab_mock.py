#!/usr/bin/env python3
"""
eval_embeddings_ab_mock.py — Mock evaluation for quick testing/demo

Purpose:
  Run A/B test WITHOUT loading actual embedding models (useful for CI/CD, quick validation)
  Uses simulated metrics based on golden set characteristics.

Simulated results:
  - bge-small-en-v1.5: Recall@5 ~85%, latency ~5ms
  - multilingual-e5-large-instruct: Recall@5 ~94%, latency ~25ms (winner)

This allows pipeline testing before doing expensive model downloads.
"""

import sys
import json
import csv
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_golden_set(csv_path: Path) -> List[Dict[str, Any]]:
    """Load golden set from CSV."""
    qa_pairs = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qa_pairs.append({
                "qa_id": row["qa_id"],
                "question": row["question"],
                "golden_answer": row["golden_answer"],
                "difficulty_level": row["difficulty_level"]
            })
    return qa_pairs


def generate_mock_results(qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate mock evaluation results."""
    results = []
    random.seed(42)  # Reproducible

    for qa in qa_pairs:
        qa_id = qa["qa_id"]
        difficulty = qa["difficulty_level"]

        # Difficulty affects scores
        difficulty_factor = {
            "easy": 0.95,
            "medium": 0.85,
            "hard": 0.70
        }.get(difficulty, 0.85)

        # bge-small: lower recall but fast
        bge_recall_base = 0.82
        bge_rank = random.randint(1, 8) if random.random() < bge_recall_base * difficulty_factor else random.randint(6, 10)
        bge_in_top5 = bge_rank <= 5

        # e5-large: higher recall but slower
        e5_recall_base = 0.91
        e5_rank = random.randint(1, 5) if random.random() < e5_recall_base * difficulty_factor else random.randint(5, 10)
        e5_in_top5 = e5_rank <= 5

        result = {
            "qa_id": qa_id,
            "question": qa["question"][:50] + "...",
            "difficulty": difficulty,
            "bge_small": {
                "rank": bge_rank,
                "in_top5": bge_in_top5,
                "score": round(random.uniform(0.65, 0.95), 3) if bge_in_top5 else round(random.uniform(0.45, 0.65), 3),
                "rrr": 1.0 / bge_rank if bge_in_top5 else 0.0,
                "ndcg_at_5": round(1.0 / (bge_rank ** 0.5) if bge_in_top5 else 0, 3)
            },
            "e5_large": {
                "rank": e5_rank,
                "in_top5": e5_in_top5,
                "score": round(random.uniform(0.72, 0.98), 3) if e5_in_top5 else round(random.uniform(0.50, 0.70), 3),
                "rrr": 1.0 / e5_rank if e5_in_top5 else 0.0,
                "ndcg_at_5": round(1.0 / (e5_rank ** 0.5) if e5_in_top5 else 0, 3)
            }
        }
        results.append(result)

    return results


def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregated metrics from results."""
    if not results:
        return {}

    n = len(results)

    # Recall@5
    recall5_v1 = sum(1 for r in results if r["bge_small"]["in_top5"]) / n
    recall5_v2 = sum(1 for r in results if r["e5_large"]["in_top5"]) / n

    # MRR
    mrr_v1 = sum(r["bge_small"]["rrr"] for r in results) / n
    mrr_v2 = sum(r["e5_large"]["rrr"] for r in results) / n

    # NDCG@5
    ndcg_v1 = sum(r["bge_small"]["ndcg_at_5"] for r in results) / n
    ndcg_v2 = sum(r["e5_large"]["ndcg_at_5"] for r in results) / n

    improvement_recall = ((recall5_v2 - recall5_v1) / recall5_v1 * 100) if recall5_v1 > 0 else 0
    improvement_mrr = ((mrr_v2 - mrr_v1) / mrr_v1 * 100) if mrr_v1 > 0 else 0
    improvement_ndcg = ((ndcg_v2 - ndcg_v1) / ndcg_v1 * 100) if ndcg_v1 > 0 else 0

    # Determine winner
    winner = "intfloat/multilingual-e5-large-instruct" if improvement_recall > 8 else "bge-small-en-v1.5"
    confidence = min(0.95, 0.5 + abs(improvement_recall) / 100)

    return {
        "bge_small": {
            "recall_at_5": float(recall5_v1),
            "mrr": float(mrr_v1),
            "ndcg_at_5": float(ndcg_v1),
            "latency_ms": 5.2  # Simulated
        },
        "e5_large": {
            "recall_at_5": float(recall5_v2),
            "mrr": float(mrr_v2),
            "ndcg_at_5": float(ndcg_v2),
            "latency_ms": 24.8  # Simulated
        },
        "comparison": {
            "winner": winner,
            "improvement_recall_pct": float(improvement_recall),
            "improvement_mrr_pct": float(improvement_mrr),
            "improvement_ndcg_pct": float(improvement_ndcg),
            "confidence_score": float(min(1.0, confidence))
        }
    }


def save_results(metrics: Dict[str, Any], results_detail: List[Dict[str, Any]], output_path: Path):
    """Save evaluation results."""
    output = {
        "evaluation_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "golden_set_size": len(results_detail),
            "evaluation_type": "A/B test (P4 RAG embedding models) — MOCK",
            "methodology": "Simulated metrics (for CI/CD validation)"
        },
        "models": {
            "bge_small": {
                "name": "bge-small-en-v1.5",
                "dimension": 384,
                "language": "English",
                "characteristics": "Small, fast, efficient",
                **metrics["bge_small"]
            },
            "e5_large": {
                "name": "intfloat/multilingual-e5-large-instruct",
                "dimension": 1024,
                "language": "Multilingual (Portuguese native)",
                "characteristics": "Large, accurate, multilingual",
                **metrics["e5_large"]
            }
        },
        "comparison": metrics["comparison"],
        "qa_details_sample": results_detail[:10],  # Sample only
        "recommendations": [
            f"WINNER: {metrics['comparison']['winner']}",
            f"Recall@5 improvement: {metrics['comparison']['improvement_recall_pct']:+.1f}%",
            f"Confidence: {metrics['comparison']['confidence_score']:.0%}",
            "Run actual eval_embeddings_ab.py with real models for production decisions"
        ],
        "note": "This is a MOCK evaluation. Run eval_embeddings_ab.py with actual models for production."
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Results saved to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Mock A/B test for RAG embedding models")
    parser.add_argument("--golden-set", type=Path, default=Path("rag_evals/golden_set_v1.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("rag_evals"))

    args = parser.parse_args()

    try:
        if not args.golden_set.exists():
            logger.error(f"Golden set not found: {args.golden_set}")
            return 2

        qa_pairs = load_golden_set(args.golden_set)
        logger.info(f"Loaded {len(qa_pairs)} QA pairs")

        args.output_dir.mkdir(parents=True, exist_ok=True)

        results = generate_mock_results(qa_pairs)
        metrics = compute_metrics(results)

        output_path = args.output_dir / "eval_embeddings_ab_results_mock.json"
        save_results(metrics, results, output_path)

        logger.info("\n" + "=" * 70)
        logger.info("MOCK EVALUATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"\nWINNER: {metrics['comparison']['winner']}")
        logger.info(f"  Recall@5 improvement: {metrics['comparison']['improvement_recall_pct']:+.1f}%")
        logger.info(f"  MRR improvement:      {metrics['comparison']['improvement_mrr_pct']:+.1f}%")
        logger.info(f"  Confidence:           {metrics['comparison']['confidence_score']:.0%}")

        return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
