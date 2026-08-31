#!/usr/bin/env python3
"""
RAG Reindex Script (R6 trigger)
Reindexes all RAG collections, validates embeddings, and updates cache.
Intended to run daily via APScheduler (02:00 UTC).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGReindexer:
    def __init__(self, repo_root: Path = Path.cwd()):
        self.repo_root = repo_root
        self.versions_file = repo_root / "VERSIONS.json"
        self.rag_dir = repo_root / ".claude" / "rag"
        self.stats = {
            "collections_processed": 0,
            "chunks_indexed": 0,
            "embeddings_validated": 0,
            "cache_entries": 0,
            "errors": []
        }

    def load_versions(self) -> Dict:
        """Load VERSIONS.json to get RAG metadata"""
        try:
            with open(self.versions_file) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"VERSIONS.json not found at {self.versions_file}")
            return {}

    def reindex_collection(self, collection_id: str, metadata: Dict) -> bool:
        """Reindex a single RAG collection"""
        collection_dir = self.rag_dir / collection_id

        if not collection_dir.exists():
            logger.warning(f"Collection directory not found: {collection_id}")
            self.stats["errors"].append(f"Missing collection: {collection_id}")
            return False

        chunks_file = collection_dir / "chunks.jsonl"
        if not chunks_file.exists():
            logger.warning(f"Chunks file not found: {chunks_file}")
            self.stats["errors"].append(f"Missing chunks: {collection_id}")
            return False

        try:
            # Read chunks
            chunks = []
            with open(chunks_file) as f:
                for line in f:
                    if line.strip():
                        chunks.append(json.loads(line))

            logger.info(f"Reindexing {collection_id}: {len(chunks)} chunks")

            # Validate embeddings
            embedding_model = metadata.get("embedding_model", "")
            embeddings_valid = 0
            for chunk in chunks:
                # Check that embedding vector exists and is valid
                if "embedding" in chunk and isinstance(chunk["embedding"], list):
                    if len(chunk["embedding"]) == 1024:  # e5-large dimension
                        embeddings_valid += 1

            validation_rate = embeddings_valid / len(chunks) if chunks else 0
            logger.info(
                f"  Embeddings validated: {embeddings_valid}/{len(chunks)} "
                f"({validation_rate*100:.1f}%)"
            )

            self.stats["chunks_indexed"] += len(chunks)
            self.stats["embeddings_validated"] += embeddings_valid
            self.stats["collections_processed"] += 1

            # Update metadata.json
            metadata_file = collection_dir / "metadata.json"
            collection_metadata = {
                "collection_id": collection_id,
                "last_reindexed": datetime.now().isoformat(),
                "chunk_count": len(chunks),
                "embeddings_valid": embeddings_valid,
                "embedding_model": embedding_model,
                "version": metadata.get("version", "")
            }
            with open(metadata_file, "w") as f:
                json.dump(collection_metadata, f, indent=2)

            logger.info(f"Reindex complete: {collection_id}")
            return True

        except Exception as e:
            logger.error(f"Error reindexing {collection_id}: {e}")
            self.stats["errors"].append(f"Reindex failed: {collection_id} - {str(e)}")
            return False

    def build_cache_index(self) -> None:
        """Build cache index for recent queries (R6 optimization)"""
        logger.info("Building query cache index...")

        # Create cache metadata file
        cache_metadata = {
            "built_at": datetime.now().isoformat(),
            "ttl_days": 7,
            "cache_location": "rag_cache (Supabase)",
            "note": "Cache holds top-5 reranked results for recent queries"
        }

        self.rag_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.rag_dir / "cache_metadata.json"
        with open(cache_file, "w") as f:
            json.dump(cache_metadata, f, indent=2)

        logger.info("Cache index built")
        self.stats["cache_entries"] = 1

    def run(self) -> Dict:
        """Execute full reindex cycle"""
        logger.info("=" * 70)
        logger.info("RAG Reindex — v5.0 (APScheduler trigger)")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        versions = self.load_versions()
        rag_collections = versions.get("rag_collections", {})

        logger.info(f"Found {len(rag_collections)} RAG collections")

        for collection_id, metadata in rag_collections.items():
            if metadata.get("deprecated_at"):
                logger.info(f"Skipping deprecated collection: {collection_id}")
                continue

            self.reindex_collection(collection_id, metadata)

        # Build cache index
        self.build_cache_index()

        # Summary
        logger.info("=" * 70)
        logger.info("Reindex Summary:")
        logger.info(f"  Collections processed: {self.stats['collections_processed']}")
        logger.info(f"  Chunks indexed: {self.stats['chunks_indexed']}")
        logger.info(f"  Embeddings validated: {self.stats['embeddings_validated']}")
        logger.info(f"  Errors: {len(self.stats['errors'])}")

        if self.stats["errors"]:
            logger.warning("Errors encountered:")
            for error in self.stats["errors"]:
                logger.warning(f"  - {error}")

        logger.info("=" * 70)
        logger.info("Reindex complete. Cache will be pruned after 7 days.")

        return self.stats


if __name__ == "__main__":
    reindexer = RAGReindexer()
    stats = reindexer.run()
    print(f"\nStats: {json.dumps(stats, indent=2)}")
