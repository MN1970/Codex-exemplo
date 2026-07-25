#!/usr/bin/env python3
"""
test_rag_reranker.py — Testes unitários para R6 Reranker

Testa:
1. Cache operations (get/set, TTL, hit rate)
2. Reranker output format
3. Score distribution validation
4. Batch processing
5. Error handling
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from rag_reranker import RerankerCache, SonnetCrossEncoder, RAGReranker


def test_cache_basic():
    """Test basic cache operations."""
    print("Test 1: Cache basic operations...")
    cache = RerankerCache(ttl_days=7)

    query = "Como dimensionar ETA?"
    chunks = [
        {"chunk_id": "san_001", "text": "..."},
        {"chunk_id": "san_002", "text": "..."}
    ]
    result = {"rankings": [{"chunk_id": "san_001", "score": 0.95}]}

    # Set
    cache.set(query, chunks, result)
    assert cache.cache, "Cache should not be empty after set"

    # Get
    cached = cache.get(query, chunks)
    assert cached is not None, "Cache get should return result"
    assert cached["rankings"][0]["score"] == 0.95

    print("  ✓ Cache basic operations OK")


def test_cache_miss():
    """Test cache miss."""
    print("Test 2: Cache miss...")
    cache = RerankerCache()

    query = "Query 1"
    chunks = [{"chunk_id": "c1"}]
    result = {"rankings": []}

    cache.set(query, chunks, result)

    # Different query should miss
    different_query = "Query 2"
    cached = cache.get(different_query, chunks)
    assert cached is None, "Cache miss should return None"
    assert cache.misses == 1

    print("  ✓ Cache miss OK")


def test_cache_stats():
    """Test cache statistics."""
    print("Test 3: Cache stats...")
    cache = RerankerCache()

    query = "Test"
    chunks = [{"chunk_id": "c1"}]
    result = {}

    cache.set(query, chunks, result)
    cache.get(query, chunks)  # Hit
    cache.get(query + "2", chunks)  # Miss

    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["total"] == 2
    assert stats["hit_rate"] == 0.5

    print(f"  ✓ Cache stats OK: {stats}")


def test_sonnet_encoder_prompt():
    """Test prompt building."""
    print("Test 4: Sonnet encoder prompt...")
    encoder = SonnetCrossEncoder()

    query = "How to design ETA?"
    chunks = [
        {
            "chunk_id": "c1",
            "text": "ETA includes coagulation...",
            "source": "NBR 12211",
            "bm25_score": 0.95
        }
    ]

    prompt = encoder.build_prompt(query, chunks)

    assert "Como dimensionar" in prompt or "design" in prompt or "ETA" in prompt
    assert "chunk_id" in prompt or "c1" in prompt or "NBR" in prompt
    assert "0.0-1.0" in prompt or "score" in prompt
    assert "JSON" in prompt

    print(f"  ✓ Prompt generation OK ({len(prompt)} chars)")


def test_reranker_output_format():
    """Test reranker output format."""
    print("Test 5: Reranker output format...")
    reranker = RAGReranker(top_k=5, cache_enabled=False)

    query = "Dimensionar ETA?"
    chunks = [
        {
            "chunk_id": f"c{i}",
            "text": f"Content {i}",
            "source": f"Source {i}",
            "bm25_score": 0.8 + (i * 0.01)
        }
        for i in range(10)
    ]

    result = reranker.rerank(query, chunks)

    # Validate structure
    assert "query" in result
    assert "reranked_chunks" in result
    assert "metrics" in result

    # Validate reranked chunks
    assert len(result["reranked_chunks"]) <= 5
    for chunk in result["reranked_chunks"]:
        assert "chunk_id" in chunk
        assert "score" in chunk
        assert "rank" in chunk
        assert "text" in chunk
        assert "source" in chunk
        assert 0.0 <= chunk["score"] <= 1.0

    # Validate metrics
    assert "latency_ms" in result["metrics"]
    assert "cache_hit" in result["metrics"]
    assert "score_distribution" in result["metrics"]
    dist = result["metrics"]["score_distribution"]
    assert "min" in dist and "max" in dist and "mean" in dist and "stdev" in dist

    print(f"  ✓ Output format OK")
    print(f"    Reranked {len(result['reranked_chunks'])} chunks")
    print(f"    Score range: {dist['min']:.2f}-{dist['max']:.2f}")


def test_score_distribution():
    """Test score distribution calculation."""
    print("Test 6: Score distribution...")
    reranker = RAGReranker(top_k=3)

    query = "Test"
    chunks = [
        {"chunk_id": f"c{i}", "text": f"Text {i}", "source": "Src", "bm25_score": 0.5 + i*0.1}
        for i in range(5)
    ]

    result = reranker.rerank(query, chunks)
    dist = result["metrics"]["score_distribution"]

    # Validate stats
    assert dist["min"] <= dist["mean"] <= dist["max"]
    assert dist["stdev"] >= 0
    if dist["max"] - dist["min"] > 0.01:
        assert dist["stdev"] > 0, "Non-zero spread should have non-zero stdev"

    print(f"  ✓ Score distribution OK: min={dist['min']:.2f}, max={dist['max']:.2f}, mean={dist['mean']:.2f}")


def test_batch_rerank():
    """Test batch reranking."""
    print("Test 7: Batch reranking...")
    reranker = RAGReranker(top_k=5, cache_enabled=True)

    batch = [
        {
            "query": f"ETA dimensioning {i}",
            "chunks": [
                {"chunk_id": f"c{j}", "text": f"Text {j}", "source": f"Src", "bm25_score": 0.8 + j*0.01}
                for j in range(5)
            ]
        }
        for i in range(3)
    ]

    results = reranker.batch_rerank(batch)

    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    for result in results:
        assert "query" in result
        assert "reranked_chunks" in result
        assert len(result["reranked_chunks"]) > 0

    # Check cache hit rate after batch
    stats = reranker.stats()
    assert stats["total_reranks"] == 3, f"Expected 3 total reranks, got {stats['total_reranks']}"

    print(f"  ✓ Batch reranking OK: {len(results)} queries processed")


def test_reranker_stats():
    """Test reranker statistics."""
    print("Test 8: Reranker statistics...")
    reranker = RAGReranker()

    query = "Test"
    chunks = [{"chunk_id": "c1", "text": "Text", "source": "Src", "bm25_score": 0.9}]

    reranker.rerank(query, chunks)
    reranker.rerank(query, chunks)  # Cache hit

    stats = reranker.stats()

    assert stats["total_reranks"] == 2
    assert stats["cache_hits"] == 1
    assert "latency_stats" in stats
    assert stats["latency_stats"]["count"] >= 1

    print(f"  ✓ Stats OK: {stats['total_reranks']} reranks, {stats['cache_hits']} hits")


def test_empty_chunks():
    """Test handling of empty chunks."""
    print("Test 9: Empty chunks handling...")
    reranker = RAGReranker()

    query = "Test"
    chunks = []

    result = reranker.rerank(query, chunks)

    assert len(result["reranked_chunks"]) == 0
    assert result["metrics"]["score_distribution"]["min"] == 0.0

    print("  ✓ Empty chunks handling OK")


def test_large_batch():
    """Test large batch processing."""
    print("Test 10: Large batch...")
    reranker = RAGReranker(top_k=5, cache_enabled=False)

    batch = [
        {
            "query": f"Query {i}",
            "chunks": [
                {"chunk_id": f"c{j}", "text": f"Text", "source": "Src", "bm25_score": 0.8}
                for j in range(20)
            ]
        }
        for i in range(10)
    ]

    results = reranker.batch_rerank(batch)
    assert len(results) == 10

    print(f"  ✓ Large batch OK: {len(results)} queries")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("RAG Reranker (R6) Unit Tests")
    print("="*60 + "\n")

    tests = [
        test_cache_basic,
        test_cache_miss,
        test_cache_stats,
        test_sonnet_encoder_prompt,
        test_reranker_output_format,
        test_score_distribution,
        test_batch_rerank,
        test_reranker_stats,
        test_empty_chunks,
        test_large_batch,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
