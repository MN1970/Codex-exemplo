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
        # Import existing RAG reindexer. O arquivo é `rag-reindex.py`
        # (hífen) — não importável via `import rag_reindex`/`from
        # rag_reindex import ...` (esse módulo nunca existiu), então
        # carregamos pelo caminho do arquivo em vez de renomeá-lo (o
        # nome com hífen está referenciado em dezenas de docs/configs).
        import importlib.util

        module_path = repo_root / "scripts" / "rag-reindex.py"
        spec = importlib.util.spec_from_file_location("rag_reindex", module_path)
        rag_reindex = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rag_reindex)
        RAGReindexer = rag_reindex.RAGReindexer

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
