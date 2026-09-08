#!/usr/bin/env python3
"""
eval_embeddings_ab.py — A/B test para escolher embedding model (P4 RAG)

Objetivo:
  Comparar dois embedding models em 50 QA pairs do golden set:

  1. Embedding v1: bge-small-en-v1.5 (384d, rápido, English)
  2. Embedding v2: intfloat/multilingual-e5-large-instruct (1024d, multilíngue)

  Dataset: 50 QA pairs (rag_evals/golden_set_v1.csv)

  Métricas:
    - Recall@5: fração de QAs onde melhor chunk está em top-5
    - MRR: Mean Reciprocal Rank (1 / posição média do melhor chunk)
    - Latência: tempo médio de embedding (ms)
    - NDCG@5: Normalized Discounted Cumulative Gain

  Decisão: winner = modelo com ganho > 10% em recall

Inputs:
  --golden-set: path para CSV (default: rag_evals/golden_set_v1.csv)
  --model-v1: embedding model v1 (default: bge-small-en-v1.5)
  --model-v2: embedding model v2 (default: intfloat/multilingual-e5-large-instruct)
  --num-chunks-per-qa: chunks simulados por QA (default: 10)
  --batch-size: batch size para embedding (default: 32)
  --device: cuda/cpu (default: auto-detect)
  --output-dir: saída de resultados (default: rag_evals)
  --verbose: logging detalhado

Output:
  rag_evals/eval_embeddings_ab_results.json — Resultados completos:
    {
      "evaluation_metadata": {...},
      "models": {
        "bge-small": {recall@5, mrr, ndcg@5, latency_ms, n_runs},
        "multilingual-e5": {...}
      },
      "comparison": {
        "winner": "multilingual-e5-large-instruct",
        "improvement_recall_pct": 15.3,
        "improvement_mrr_pct": 12.1,
        "confidence_score": 0.92
      },
      "qa_details": [
        {
          "qa_id": "qa_001",
          "question": "...",
          "bge_small": {rank: 1, score: 0.92},
          "e5_large": {rank: 1, score: 0.94}
        }
      ],
      "recommendations": [...]
    }

Exit codes:
  0: Sucesso
  1: Erro crítico
  2: Dados insuficientes
"""

import sys
import os
import json
import csv
import logging
import argparse
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import hashlib

import numpy as np
from scipy.spatial.distance import cosine

# Try to import transformers and sentence-transformers
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
except ImportError:
    print("ERROR: Please install 'transformers' and 'torch'")
    print("  pip install transformers torch")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for embedding model with caching and metrics."""

    def __init__(self, model_name: str, device: str = "cpu"):
        """Initialize embedding model."""
        self.model_name = model_name
        self.device = device
        logger.info(f"Loading model: {model_name} on {device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()

        # Get embedding dimension
        with torch.no_grad():
            sample = self.tokenizer(["test"], return_tensors="pt", padding=True).to(device)
            outputs = self.model(**sample)
            self.embedding_dim = outputs.last_hidden_state.shape[-1]

        self.embedding_cache = {}
        self.timing_stats = {"n_embeds": 0, "total_ms": 0.0}

    def embed(self, texts: List[str], normalize: bool = True) -> np.ndarray:
        """Embed texts with caching and timing."""
        embeddings = []

        for text in texts:
            # Cache lookup
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self.embedding_cache:
                embeddings.append(self.embedding_cache[cache_key])
                continue

            # Embed single text
            start_ms = time.time() * 1000
            with torch.no_grad():
                encoded = self.tokenizer(
                    [text],
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)

                outputs = self.model(**encoded)
                # Use mean pooling of last hidden state
                embedding = outputs.last_hidden_state.mean(dim=1)[0].cpu().numpy()

                if normalize:
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm

            elapsed_ms = (time.time() * 1000) - start_ms
            self.timing_stats["n_embeds"] += 1
            self.timing_stats["total_ms"] += elapsed_ms

            # Cache result
            self.embedding_cache[cache_key] = embedding
            embeddings.append(embedding)

        return np.array(embeddings)

    def get_avg_latency_ms(self) -> float:
        """Get average embedding latency in ms."""
        if self.timing_stats["n_embeds"] == 0:
            return 0.0
        return self.timing_stats["total_ms"] / self.timing_stats["n_embeds"]


class RAGEvaluator:
    """Evaluator for RAG retrieval with both embedding models."""

    def __init__(self, model_v1: EmbeddingModel, model_v2: EmbeddingModel,
                 num_chunks_per_qa: int = 10):
        """Initialize evaluator."""
        self.model_v1 = model_v1
        self.model_v2 = model_v2
        self.num_chunks_per_qa = num_chunks_per_qa
        self.results = []

    def generate_mock_chunks(self, qa_pair: Dict[str, Any], seed: int = 42) -> Dict[str, List[str]]:
        """Generate mock chunks for evaluation (simulates RAG retrieval)."""
        np.random.seed(seed)

        question = qa_pair["question"]
        golden_answer = qa_pair["golden_answer"]

        # Golden chunk (should have high similarity)
        golden_chunk = golden_answer

        # Generate 9 distractor chunks (low similarity)
        distractors = [
            "Normas ABNT para projeto de estruturas de concreto armado.",
            "Procedimentos de licitação pública conforme Lei 8.666/93.",
            "Critérios de estabilidade de encostas em solos residuais.",
            "Metodologia de análise de risco financeiro em projetos de infraestrutura.",
            "Especificações técnicas para pavimentação de rodovias federais.",
            "Guia de dimensionamento de fundações em solos moles.",
            "Normas de segurança para trabalho em altura.",
            "Procedimentos de gestão ambiental em canteiros de obra.",
            "Critérios de seleção de fornecedores em compras públicas."
        ]

        chunks = [golden_chunk] + distractors[:self.num_chunks_per_qa - 1]
        np.random.shuffle(chunks)

        return {
            "chunks": chunks,
            "golden_chunk": golden_chunk,
            "golden_idx": chunks.index(golden_chunk)
        }

    def evaluate_qa(self, qa_pair: Dict[str, Any], seed: int = 42) -> Dict[str, Any]:
        """Evaluate single QA pair with both models."""
        qa_id = qa_pair["qa_id"]
        question = qa_pair["question"]

        # Generate mock chunks
        chunks_data = self.generate_mock_chunks(qa_pair, seed=hash(qa_id) % (2**31))
        chunks = chunks_data["chunks"]
        golden_idx = chunks_data["golden_idx"]

        # Embed question with both models
        q_emb_v1 = self.model_v1.embed([question])[0]
        q_emb_v2 = self.model_v2.embed([question])[0]

        # Embed chunks with both models
        chunk_emb_v1 = self.model_v1.embed(chunks)
        chunk_emb_v2 = self.model_v2.embed(chunks)

        # Calculate similarity scores (cosine)
        scores_v1 = 1 - np.array([cosine(q_emb_v1, c) for c in chunk_emb_v1])
        scores_v2 = 1 - np.array([cosine(q_emb_v2, c) for c in chunk_emb_v2])

        # Get rankings
        rank_v1 = np.argsort(scores_v1)[::-1]  # descending
        rank_v2 = np.argsort(scores_v2)[::-1]

        # Find position of golden chunk
        pos_v1 = np.where(rank_v1 == golden_idx)[0][0] + 1  # 1-indexed
        pos_v2 = np.where(rank_v2 == golden_idx)[0][0] + 1

        # Top-5 ranking
        top5_v1 = rank_v1[:5]
        top5_v2 = rank_v2[:5]

        in_top5_v1 = golden_idx in top5_v1
        in_top5_v2 = golden_idx in top5_v2

        # RRR (Reciprocal Rank)
        rrr_v1 = 1.0 / pos_v1 if in_top5_v1 else 0.0
        rrr_v2 = 1.0 / pos_v2 if in_top5_v2 else 0.0

        # NDCG@5 (simplified)
        dcg_v1 = sum([1.0 / np.log2(i + 2) for i in range(5) if rank_v1[i] == golden_idx])
        dcg_v2 = sum([1.0 / np.log2(i + 2) for i in range(5) if rank_v2[i] == golden_idx])
        idcg = 1.0 / np.log2(2)  # ideal: golden at position 1

        ndcg_v1 = dcg_v1 / idcg
        ndcg_v2 = dcg_v2 / idcg

        result = {
            "qa_id": qa_id,
            "question": question,
            "golden_chunk": chunks_data["golden_chunk"][:100] + "...",  # Truncate for readability
            "bge_small": {
                "rank": int(pos_v1),
                "in_top5": bool(in_top5_v1),
                "score": float(scores_v1[golden_idx]),
                "rrr": float(rrr_v1),
                "ndcg_at_5": float(ndcg_v1)
            },
            "e5_large": {
                "rank": int(pos_v2),
                "in_top5": bool(in_top5_v2),
                "score": float(scores_v2[golden_idx]),
                "rrr": float(rrr_v2),
                "ndcg_at_5": float(ndcg_v2)
            }
        }

        return result

    def run_evaluation(self, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run evaluation on all QA pairs."""
        logger.info(f"Running evaluation on {len(qa_pairs)} QA pairs...")

        for i, qa in enumerate(qa_pairs, 1):
            if i % 10 == 0:
                logger.info(f"  Progress: {i}/{len(qa_pairs)}")

            try:
                result = self.evaluate_qa(qa)
                self.results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating {qa['qa_id']}: {e}")
                logger.debug(traceback.format_exc())

        return self.results


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
                "agent_id": row["agent_id"],
                "expected_chunks": row["expected_chunks"].split(";") if row["expected_chunks"] else [],
                "difficulty_level": row["difficulty_level"],
                "source_domain": row["source_domain"]
            })

    logger.info(f"Loaded {len(qa_pairs)} QA pairs from {csv_path}")
    return qa_pairs


def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregated metrics from evaluation results."""

    if not results:
        return {}

    metrics = {
        "bge_small": {},
        "e5_large": {}
    }

    # Recall@5
    recall5_v1 = sum([1 for r in results if r["bge_small"]["in_top5"]]) / len(results)
    recall5_v2 = sum([1 for r in results if r["e5_large"]["in_top5"]]) / len(results)

    metrics["bge_small"]["recall_at_5"] = float(recall5_v1)
    metrics["e5_large"]["recall_at_5"] = float(recall5_v2)

    # MRR (Mean Reciprocal Rank)
    mrr_v1 = np.mean([r["bge_small"]["rrr"] for r in results])
    mrr_v2 = np.mean([r["e5_large"]["rrr"] for r in results])

    metrics["bge_small"]["mrr"] = float(mrr_v1)
    metrics["e5_large"]["mrr"] = float(mrr_v2)

    # NDCG@5
    ndcg5_v1 = np.mean([r["bge_small"]["ndcg_at_5"] for r in results])
    ndcg5_v2 = np.mean([r["e5_large"]["ndcg_at_5"] for r in results])

    metrics["bge_small"]["ndcg_at_5"] = float(ndcg5_v1)
    metrics["e5_large"]["ndcg_at_5"] = float(ndcg5_v2)

    # Latency
    metrics["bge_small"]["latency_ms"] = 0.0  # Will set after models
    metrics["e5_large"]["latency_ms"] = 0.0

    # Improvement calculations
    improvement_recall = ((recall5_v2 - recall5_v1) / recall5_v1 * 100) if recall5_v1 > 0 else 0
    improvement_mrr = ((mrr_v2 - mrr_v1) / mrr_v1 * 100) if mrr_v1 > 0 else 0
    improvement_ndcg = ((ndcg5_v2 - ndcg5_v1) / ndcg5_v1 * 100) if ndcg5_v1 > 0 else 0

    # Determine winner
    # Winner if recall improvement > 10% OR (improvement > 5% AND ndcg > 5%)
    threshold_recall = 10.0
    threshold_minor = 5.0

    if improvement_recall > threshold_recall:
        winner = "intfloat/multilingual-e5-large-instruct" if recall5_v2 > recall5_v1 else "bge-small-en-v1.5"
        confidence = min(0.95, 0.5 + abs(improvement_recall) / 100)
    elif improvement_mrr > threshold_minor and improvement_ndcg > threshold_minor:
        winner = "intfloat/multilingual-e5-large-instruct" if mrr_v2 > mrr_v1 else "bge-small-en-v1.5"
        confidence = 0.65
    else:
        # No clear winner, choose by recall as tiebreaker
        winner = "intfloat/multilingual-e5-large-instruct" if recall5_v2 >= recall5_v1 else "bge-small-en-v1.5"
        confidence = 0.55

    metrics["comparison"] = {
        "winner": winner,
        "improvement_recall_pct": float(improvement_recall),
        "improvement_mrr_pct": float(improvement_mrr),
        "improvement_ndcg_pct": float(improvement_ndcg),
        "confidence_score": float(min(1.0, max(0.0, confidence)))
    }

    return metrics


def generate_recommendations(metrics: Dict[str, Any], model_v1_name: str,
                            model_v2_name: str) -> List[str]:
    """Generate recommendations based on metrics."""
    recommendations = []

    winner = metrics.get("comparison", {}).get("winner", "")
    improvement_recall = metrics.get("comparison", {}).get("improvement_recall_pct", 0)
    confidence = metrics.get("comparison", {}).get("confidence_score", 0)

    if winner == model_v2_name:
        if improvement_recall > 15:
            recommendations.append(
                f"STRONG RECOMMENDATION: Use {model_v2_name}. "
                f"Recall@5 improvement of {improvement_recall:.1f}% is significant."
            )
        elif improvement_recall > 10:
            recommendations.append(
                f"RECOMMENDED: Use {model_v2_name} for RAG collections. "
                f"Recall@5 improvement of {improvement_recall:.1f}% justifies the larger model size."
            )
        elif improvement_recall > 0:
            recommendations.append(
                f"CONSIDER: {model_v2_name} if latency allows. "
                f"Recall@5 improvement of {improvement_recall:.1f}% but larger model may impact speed."
            )
    elif winner == model_v1_name:
        if improvement_recall < -10:
            recommendations.append(
                f"STRONG RECOMMENDATION: Use {model_v1_name} (bge-small-en-v1.5). "
                f"Faster embeddings with competitive recall (only {abs(improvement_recall):.1f}% lower)."
            )
        else:
            recommendations.append(
                f"RECOMMENDED: Use {model_v1_name} for cost-efficiency. "
                f"Similar performance with lower latency."
            )
    else:
        recommendations.append(
            "NO CLEAR WINNER: Both models perform similarly. "
            "Choose based on infrastructure constraints (speed vs memory)."
        )

    # Confidence note
    if confidence < 0.7:
        recommendations.append(
            f"NOTE: Confidence score {confidence:.2f} is moderate. "
            "Consider expanding test set or adjusting evaluation methodology."
        )

    # Multilingual note
    recommendations.append(
        f"NOTE: {model_v2_name} supports multilingual queries. "
        "Important if RAG will serve Portuguese/Spanish queries."
    )

    return recommendations


def save_results(metrics: Dict[str, Any], results_detail: List[Dict[str, Any]],
                model_v1: EmbeddingModel, model_v2: EmbeddingModel,
                output_path: Path, args):
    """Save evaluation results to JSON."""

    # Add latency metrics
    metrics["bge_small"]["latency_ms"] = float(model_v1.get_avg_latency_ms())
    metrics["e5_large"]["latency_ms"] = float(model_v2.get_avg_latency_ms())

    recommendations = generate_recommendations(
        metrics, "bge-small-en-v1.5", "intfloat/multilingual-e5-large-instruct"
    )

    output = {
        "evaluation_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "golden_set_size": len(results_detail),
            "evaluation_type": "A/B test (P4 RAG embedding models)",
            "methodology": "cosine similarity ranking with mock chunks"
        },
        "models": {
            "bge_small": {
                "name": "bge-small-en-v1.5",
                "dimension": model_v1.embedding_dim,
                "language": "English (multilingual capable)",
                "source": "BAAI/bge-small-en-v1.5",
                "characteristics": "Small, fast, efficient",
                **metrics["bge_small"]
            },
            "e5_large": {
                "name": "intfloat/multilingual-e5-large-instruct",
                "dimension": model_v2.embedding_dim,
                "language": "Multilingual (Portuguese native)",
                "source": "intfloat/multilingual-e5-large-instruct",
                "characteristics": "Large, accurate, multilingual",
                **metrics["e5_large"]
            }
        },
        "comparison": metrics["comparison"],
        "qa_details": results_detail,
        "recommendations": recommendations,
        "next_steps": [
            f"Pin winner in VERSIONS.json: rag_collections.*.embedding_model = {metrics['comparison']['winner']}",
            f"Update .claude/settings.json with: embedding_strategy = '{metrics['comparison']['winner']}'",
            "Re-index RAG collections with chosen embedding model",
            "Monitor Grafana dashboard for query latency/cost after switch"
        ]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="A/B test for RAG embedding models (P4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full A/B test
  python scripts/eval_embeddings_ab.py

  # Test on CPU only
  python scripts/eval_embeddings_ab.py --device cpu

  # Custom models
  python scripts/eval_embeddings_ab.py \\
    --model-v1 BAAI/bge-small-en-v1.5 \\
    --model-v2 intfloat/multilingual-e5-large-instruct
        """
    )

    parser.add_argument(
        "--golden-set",
        type=Path,
        default=Path("rag_evals/golden_set_v1.csv"),
        help="Path to golden set CSV (default: rag_evals/golden_set_v1.csv)"
    )

    parser.add_argument(
        "--model-v1",
        default="BAAI/bge-small-en-v1.5",
        help="Embedding model v1 (default: BAAI/bge-small-en-v1.5)"
    )

    parser.add_argument(
        "--model-v2",
        default="intfloat/multilingual-e5-large-instruct",
        help="Embedding model v2 (default: intfloat/multilingual-e5-large-instruct)"
    )

    parser.add_argument(
        "--num-chunks-per-qa",
        type=int,
        default=10,
        help="Number of mock chunks per QA pair (default: 10)"
    )

    parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        default="auto",
        help="Device (default: auto-detect)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("rag_evals"),
        help="Output directory (default: rag_evals)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Check device
        if args.device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = args.device

        logger.info(f"Using device: {device}")

        # Load golden set
        if not args.golden_set.exists():
            logger.error(f"Golden set not found: {args.golden_set}")
            return 2

        qa_pairs = load_golden_set(args.golden_set)

        if not qa_pairs:
            logger.error("No QA pairs loaded from golden set")
            return 2

        # Create output directory
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize models
        logger.info("Initializing embedding models...")
        model_v1 = EmbeddingModel(args.model_v1, device=device)
        model_v2 = EmbeddingModel(args.model_v2, device=device)

        # Run evaluation
        logger.info("Running A/B test evaluation...")
        evaluator = RAGEvaluator(model_v1, model_v2,
                                num_chunks_per_qa=args.num_chunks_per_qa)
        results = evaluator.run_evaluation(qa_pairs)

        # Compute metrics
        logger.info("Computing metrics...")
        metrics = compute_metrics(results)

        # Save results
        output_path = args.output_dir / "eval_embeddings_ab_results.json"
        save_results(metrics, results, model_v1, model_v2, output_path, args)

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("EVALUATION SUMMARY")
        logger.info("=" * 70)

        for model_key, model_name in [("bge_small", "bge-small-en-v1.5"),
                                       ("e5_large", "intfloat/multilingual-e5-large-instruct")]:
            logger.info(f"\n{model_name}:")
            logger.info(f"  Recall@5:   {metrics[model_key]['recall_at_5']:.1%}")
            logger.info(f"  MRR:        {metrics[model_key]['mrr']:.3f}")
            logger.info(f"  NDCG@5:     {metrics[model_key]['ndcg_at_5']:.3f}")
            logger.info(f"  Latency:    {metrics[model_key]['latency_ms']:.2f} ms")

        logger.info(f"\nWINNER: {metrics['comparison']['winner']}")
        logger.info(f"  Recall improvement: {metrics['comparison']['improvement_recall_pct']:+.1f}%")
        logger.info(f"  MRR improvement:    {metrics['comparison']['improvement_mrr_pct']:+.1f}%")
        logger.info(f"  Confidence:         {metrics['comparison']['confidence_score']:.2%}")

        logger.info("\nRecommendations:")
        for i, rec in enumerate(metrics.get("recommendations", []), 1):
            logger.info(f"  {i}. {rec}")

        logger.info("\n" + "=" * 70)
        logger.info(f"Full results saved to: {output_path}")

        return 0

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
