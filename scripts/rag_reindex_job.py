#!/usr/bin/env python3
"""
RAG Reindex Job Wrapper — R6 trigger para APScheduler

Wraps rag-reindex.py para ser executado via APScheduler.
"""

import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def rag_reindex_job(repo_root: Path = None) -> Dict:
    """
    Execute RAG reindex job.
    
    Returns: stats dict from RAGReindexer
    """
    if repo_root is None:
        repo_root = Path.cwd()

    try:
        # Import existing RAG reindexer
        import sys
        sys.path.insert(0, str(repo_root / "scripts"))
        from rag_reindex import RAGReindexer

        reindexer = RAGReindexer(repo_root)
        stats = reindexer.run()
        return stats

    except ImportError as e:
        logger.error(f"Failed to import RAGReindexer: {e}")
        return {"error": str(e), "status": "failed"}
    except Exception as e:
        logger.error(f"RAG reindex failed: {e}", exc_info=True)
        return {"error": str(e), "status": "failed"}


if __name__ == '__main__':
    import json
    result = rag_reindex_job()
    print(json.dumps(result, indent=2))
