#!/usr/bin/env python3
"""
Agent Memory Purge Job Wrapper — R10 trigger para APScheduler

Wraps agent_memory_purge.py para ser executado via APScheduler.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)


def agent_memory_purge_job(
    repo_root: Path = None,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    slack_webhook: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Execute agent memory purge job.
    
    Returns: (success: bool, message: str)
    """
    if repo_root is None:
        repo_root = Path.cwd()

    if supabase_url is None:
        supabase_url = os.getenv('SUPABASE_URL')
    if supabase_key is None:
        supabase_key = os.getenv('SUPABASE_KEY')
    if slack_webhook is None:
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')

    try:
        # Import existing purger
        import sys
        sys.path.insert(0, str(repo_root / "scripts"))
        from agent_memory_purge import AgentMemoryPurger

        purger = AgentMemoryPurger(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            dry_run=False,
            slack_webhook=slack_webhook
        )

        success, message = purger.run()
        return success, message

    except ImportError as e:
        logger.error(f"Failed to import AgentMemoryPurger: {e}")
        return False, f"Import error: {str(e)}"
    except Exception as e:
        logger.error(f"Agent memory purge failed: {e}", exc_info=True)
        return False, f"Purge failed: {str(e)}"


if __name__ == '__main__':
    success, message = agent_memory_purge_job()
    print(f"Success: {success}")
    print(f"Message: {message}")
