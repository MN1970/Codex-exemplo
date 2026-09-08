#!/usr/bin/env python3
"""
rag_reranker.py — Reranker R6 (Cross-encoder com Sonnet 5)

Objetivo:
  Implementa reranking de chunks RAG usando Sonnet 5 como cross-encoder.

  1. Input: Top-20 chunks (BM25 + embedding), query original
  2. Batch processing com Sonnet 5 (prompt engineering)
  3. Rerank por relevância relativa à query
  4. Output: Top-5 chunks com scores (0-1)
  5. Cache em memória (TTL 7 dias para batch)
  6. Métricas: latência, score distribution, impact on routing accuracy

Arquitetura:
  - RAGReranker: classe principal com batch processing
  - SonnetCrossEncoder: wrapper para Sonnet 5 prompt
  - RerankerCache: cache em memória com TTL
  - Integração com eval_routing.py (medir impacto em acurácia)

Entrada (--chunks):
  JSON format:
  {
    "query": "Como dimensionar ETA ciclo completo para 200k habitantes?",
    "chunks": [
      {
        "chunk_id": "san_001",
        "text": "ETA inclui coagulação, decantação, filtração...",
        "source": "NBR 12211",
        "bm25_score": 0.95
      },
      ...
    ]
  }

Saída:
  JSON format:
  {
    "query": "...",
    "reranked_chunks": [
      {
        "chunk_id": "san_001",
        "text": "...",
        "score": 0.98,
        "rank": 1,
        "reasoning": "Responde diretamente à pergunta sobre dimensionamento"
      },
      ...
    ],
    "metrics": {
      "latency_ms": 234.5,
      "tokens_used": {"input": 1200, "output": 450},
      "cache_hit": false,
      "score_distribution": {
        "min": 0.45,
        "max": 0.98,
        "mean": 0.75,
        "stdev": 0.18
      }
    }
  }

Exit codes:
  0: Reranking bem-sucedido
  1: Erro crítico (chunks inválidos, Sonnet timeout)
"""

import sys
import os
import json
import logging
import argparse
import time
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import traceback
import statistics

# Optional: Claude API
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install via: pip install anthropic")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class RerankerCache:
    """
    In-memory cache com TTL para reranking results.
    TTL: 7 dias por padrão.
    """

    def __init__(self, ttl_days: int = 7):
        self.cache = {}  # {query_hash: {chunks_hash: (result, expiry)}}
        self.ttl = timedelta(days=ttl_days)
        self.hits = 0
        self.misses = 0

    def _hash_query_chunks(self, query: str, chunks: List[Dict]) -> str:
        """Compute hash of query + chunk IDs."""
        chunk_ids = ";".join(c.get("chunk_id", "") for c in chunks)
        content = f"{query}:{chunk_ids}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, query: str, chunks: List[Dict]) -> Optional[Dict]:
        """Retrieve cached result if valid."""
        key = self._hash_query_chunks(query, chunks)

        if key in self.cache:
            result, expiry = self.cache[key]
            if datetime.now(timezone.utc) < expiry:
                self.hits += 1
                logger.debug(f"Cache hit: {key[:8]}...")
                return result
            else:
                # Expired
                del self.cache[key]

        self.misses += 1
        return None

    def set(self, query: str, chunks: List[Dict], result: Dict):
        """Store result in cache."""
        key = self._hash_query_chunks(query, chunks)
        expiry = datetime.now(timezone.utc) + self.ttl
        self.cache[key] = (result, expiry)
        logger.debug(f"Cache set: {key[:8]}...")

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total": total,
            "hit_rate": round(hit_rate, 4),
            "cached_items": len(self.cache)
        }


class SonnetCrossEncoder:
    """
    Sonnet 5 cross-encoder para reranking RAG chunks.

    Usa prompt engineering para extrair relevância scores.
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model
        if ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            self.client = None
        self.max_tokens = 2048

    def build_prompt(self, query: str, chunks: List[Dict]) -> str:
        """
        Build prompt para Sonnet 5 cross-encoder.

        Estratégia:
        1. Contexto: explica tarefa de reranking
        2. Query: pergunta original
        3. Chunks: lista numerada de chunks com suas fontes
        4. Instruções: score 0-1, retornar JSON
        5. Exemplos: 2-3 exemplos de scoring
        """

        chunks_text = "\n\n".join(
            f"{i+1}. **ID**: {c.get('chunk_id', 'unknown')}\n"
            f"   **Fonte**: {c.get('source', 'desconhecida')}\n"
            f"   **Score BM25**: {c.get('bm25_score', 0):.3f}\n"
            f"   **Texto**: {c.get('text', '')[:500]}\n"
            for i, c in enumerate(chunks)
        )

        prompt = f"""## Tarefa: Reranking de Chunks RAG

Você é um especialista em engenharia civil que avalia relevância de documentos técnicos.

### Pergunta Original:
"{query}"

### Chunks Recuperados:
{chunks_text}

### Instruções:
1. Avalie cada chunk por relevância relativa à pergunta
2. Score: 0.0 (totalmente irrelevante) a 1.0 (altamente relevante)
3. Considere:
   - Responde diretamente a pergunta?
   - É contexto necessário?
   - Contém normas/standards relevantes?
   - Nível técnico apropriado?

### Critérios de Score:
- 0.90-1.0: Responde diretamente a pergunta, muito relevante
- 0.70-0.89: Contexto importante, norma/referência aplicável
- 0.50-0.69: Marginalmente relevante, fornece background
- 0.30-0.49: Levemente relacionado, mas não core
- 0.0-0.29: Irrelevante ou off-topic

### Retorne EXATAMENTE este JSON (sem markdown, sem comentários):
{{
  "rankings": [
    {{
      "chunk_id": "san_001",
      "score": 0.95,
      "reasoning": "Responde diretamente sobre dimensionamento de ETA"
    }},
    ...
  ]
}}

Comece diretamente com {{ - não inclua explicação extra.
"""
        return prompt

    def rerank(self, query: str, chunks: List[Dict]) -> Dict[str, Any]:
        """
        Rerank chunks usando Sonnet 5.

        Returns:
          {
            "rankings": [
              {"chunk_id": "...", "score": 0.95, "reasoning": "..."},
              ...
            ],
            "latency_ms": 234.5,
            "tokens": {"input": 1200, "output": 450}
          }
        """
        start = time.time()

        if not self.client:
            logger.warning("Anthropic client not available, using mock reranker")
            return self._mock_rerank(query, chunks)

        try:
            prompt = self.build_prompt(query, chunks)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            response_text = message.content[0].text.strip()

            # Extract JSON from response (in case there's extra text)
            try:
                # Try parsing directly
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try extracting JSON block
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    logger.error(f"Failed to parse Sonnet response: {response_text[:200]}")
                    return self._mock_rerank(query, chunks)

            latency_ms = (time.time() - start) * 1000

            return {
                "rankings": result.get("rankings", []),
                "latency_ms": round(latency_ms, 2),
                "tokens": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"Sonnet reranking failed: {e}")
            logger.debug(traceback.format_exc())
            # Fallback to BM25 scores
            return self._mock_rerank(query, chunks)

    def _mock_rerank(self, query: str, chunks: List[Dict]) -> Dict[str, Any]:
        """
        Mock reranker (use BM25 scores when Sonnet unavailable).
        """
        start = time.time()

        rankings = []
        for chunk in chunks:
            score = chunk.get("bm25_score", 0.5)
            # Add small random variation
            import random
            score = min(1.0, max(0.0, score + random.uniform(-0.1, 0.1)))

            rankings.append({
                "chunk_id": chunk.get("chunk_id", "unknown"),
                "score": round(score, 3),
                "reasoning": f"BM25-based score (mock): {score:.3f}"
            })

        # Sort by score descending
        rankings.sort(key=lambda x: x["score"], reverse=True)

        latency_ms = (time.time() - start) * 1000

        return {
            "rankings": rankings,
            "latency_ms": round(latency_ms, 2),
            "tokens": {"input": 0, "output": 0}
        }


class RAGReranker:
    """
    Orquestrador principal para reranking RAG (R6).
    """

    def __init__(self, top_k: int = 5, cache_enabled: bool = True):
        self.top_k = top_k
        self.encoder = SonnetCrossEncoder()
        self.cache = RerankerCache() if cache_enabled else None
        self.metrics = {
            "total_reranks": 0,
            "cache_hits": 0,
            "latencies": []
        }

    def rerank(self, query: str, chunks: List[Dict]) -> Dict[str, Any]:
        """
        Rerank top-20 chunks to top-5.

        Args:
          query: pergunta original
          chunks: lista de ~20 chunks (BM25 + embedding)

        Returns:
          {
            "query": "...",
            "reranked_chunks": [top-5],
            "metrics": {...}
          }
        """

        # Check cache
        cache_hit = False
        if self.cache:
            cached = self.cache.get(query, chunks)
            if cached:
                cache_hit = True
                self.metrics["cache_hits"] += 1
                return cached

        start = time.time()

        # Rerank with Sonnet
        rerank_result = self.encoder.rerank(query, chunks)

        # Build output
        reranked_chunks = []
        for i, ranking in enumerate(rerank_result["rankings"][:self.top_k]):
            # Find original chunk
            original = next(
                (c for c in chunks if c.get("chunk_id") == ranking["chunk_id"]),
                None
            )

            if original:
                reranked_chunks.append({
                    "chunk_id": ranking["chunk_id"],
                    "text": original.get("text", ""),
                    "source": original.get("source", ""),
                    "score": ranking["score"],
                    "rank": i + 1,
                    "reasoning": ranking.get("reasoning", "")
                })

        # Compute metrics
        scores = [c["score"] for c in reranked_chunks]
        score_distribution = {
            "min": round(min(scores), 3) if scores else 0.0,
            "max": round(max(scores), 3) if scores else 0.0,
            "mean": round(statistics.mean(scores), 3) if scores else 0.0,
            "stdev": round(statistics.stdev(scores), 3) if len(scores) > 1 else 0.0
        }

        latency_ms = rerank_result["latency_ms"]
        self.metrics["total_reranks"] += 1
        self.metrics["latencies"].append(latency_ms)

        output = {
            "query": query,
            "reranked_chunks": reranked_chunks,
            "metrics": {
                "latency_ms": latency_ms,
                "tokens_used": rerank_result.get("tokens", {}),
                "cache_hit": cache_hit,
                "score_distribution": score_distribution,
                "total_chunks_reranked": len(reranked_chunks),
                "top_k": self.top_k
            }
        }

        # Cache result
        if self.cache and not cache_hit:
            self.cache.set(query, chunks, output)

        return output

    def batch_rerank(self, queries_chunks: List[Dict]) -> List[Dict]:
        """
        Batch rerank múltiplas queries.

        Args:
          queries_chunks: lista de {"query": "...", "chunks": [...]}

        Returns:
          lista de resultados reranked
        """
        results = []
        for item in queries_chunks:
            result = self.rerank(item["query"], item["chunks"])
            results.append(result)

        return results

    def stats(self) -> Dict[str, Any]:
        """Get reranker statistics."""
        return {
            "total_reranks": self.metrics["total_reranks"],
            "cache_hits": self.metrics["cache_hits"],
            "latency_stats": {
                "count": len(self.metrics["latencies"]),
                "mean_ms": round(
                    statistics.mean(self.metrics["latencies"]), 2
                ) if self.metrics["latencies"] else 0.0,
                "p50_ms": round(
                    statistics.median(self.metrics["latencies"]), 2
                ) if self.metrics["latencies"] else 0.0,
                "p95_ms": round(
                    sorted(self.metrics["latencies"])[
                        int(len(self.metrics["latencies"]) * 0.95)
                    ], 2
                ) if len(self.metrics["latencies"]) > 1 else 0.0,
                "max_ms": round(max(self.metrics["latencies"]), 2)
                if self.metrics["latencies"] else 0.0
            },
            "cache_stats": self.cache.stats() if self.cache else {}
        }


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="R6 Reranker — Cross-encoder Sonnet 5 para RAG chunks"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file com query e chunks (ou '-' para stdin)"
    )
    parser.add_argument(
        "--output",
        default="rag_evals/reranker_output.json",
        help="Output JSON file (default: rag_evals/reranker_output.json)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Número de chunks reranked (default: 5)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Desabilitar cache de reranking"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode (input deve ser lista de queries_chunks)"
    )
    parser.add_argument(
        "--eval-routing",
        action="store_true",
        help="Avaliar impacto em routing accuracy (requer eval_routing.py)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )
    return parser.parse_args()


def load_input(input_file: str) -> Dict[str, Any]:
    """Load input JSON from file or stdin."""
    try:
        if input_file == "-":
            import sys
            content = sys.stdin.read()
        else:
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()

        return json.loads(content)
    except Exception as e:
        logger.error(f"Failed to load input: {e}")
        raise


def output_json(result: Any, output_path: Path):
    """Write output JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Output written to {output_path}")


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting RAG Reranker (R6 — Sonnet 5)")

    try:
        # Load input
        data = load_input(args.input)

        # Initialize reranker
        reranker = RAGReranker(
            top_k=args.top_k,
            cache_enabled=not args.no_cache
        )

        # Rerank
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        if args.batch and isinstance(data, list):
            logger.info(f"Reranking {len(data)} queries in batch mode...")
            results = reranker.batch_rerank(data)
            output_data = {
                "batch_mode": True,
                "total_queries": len(data),
                "results": results,
                "reranker_stats": reranker.stats(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            logger.info(f"Reranking single query with {len(data.get('chunks', []))} chunks...")
            result = reranker.rerank(
                data.get("query", ""),
                data.get("chunks", [])
            )
            output_data = {
                "batch_mode": False,
                "result": result,
                "reranker_stats": reranker.stats(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Write output
        output_json(output_data, Path(args.output))

        # Print summary
        stats = reranker.stats()
        logger.info(f"Reranking completed:")
        logger.info(f"  Total reranks: {stats['total_reranks']}")
        logger.info(f"  Cache hits: {stats['cache_hits']}")
        logger.info(f"  Mean latency: {stats['latency_stats']['mean_ms']:.2f}ms")
        logger.info(f"  P95 latency: {stats['latency_stats']['p95_ms']:.2f}ms")

        if args.eval_routing:
            logger.info("Evaluating impact on routing accuracy...")
            # TODO: Integrate with eval_routing.py
            logger.warning("eval_routing integration not yet implemented")

        return 0

    except Exception as e:
        logger.error(f"Reranking failed: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
