#!/usr/bin/env python3
"""
background_agent_framework.py — Framework para background agents (S5 + horizontais)

Objetivo:
  Framework de workers para disparar tasks long-running (> 30s) sem bloquear.
  Cada agente pode spawnar subagents em background via background_spawn().

Componentes:
  1. BackgroundAgentFramework — Core class para gerenciar jobs
  2. Job states: pending → running → completed/error
  3. Persistence: Supabase agent_jobs table
  4. Timeout: 5 min para long-running, retry 2x se falha
  5. Integration: hooks via settings.json

Fluxo:
  agent_skill.md:
    from scripts.background_agent_framework import background_spawn
    job_id = background_spawn(
      agent_id="manta-03-s5",
      prompt="Analise projeto de túnel + viabilidade geotécnica",
      timeout=300
    )

  Hook SubagentStop:
    background_store_result(job_id, result, status)

Classes:
  - BackgroundAgentFramework
  - BackgroundJobManager
  - BackgroundJobResult

Exit codes:
  0: Sucesso
  1: Erro crítico (conexão Supabase)
  2: Job timeout/retry limit exceeded
"""

import sys
import os
import logging
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Try to import Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase client not installed. Install: pip install supabase")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


# =====================================================================
# ENUMS & DATA CLASSES
# =====================================================================

class JobStatus(str, Enum):
    """Job state machine."""
    PENDING = "pending"           # Created, awaiting execution
    RUNNING = "running"           # Agent is processing
    COMPLETED = "completed"       # Success
    FAILED = "failed"             # Error, exhausted retries
    TIMEOUT = "timeout"           # Hit 5-min timeout
    CANCELLED = "cancelled"       # User cancelled


@dataclass
class BackgroundJobResult:
    """Result of a background job."""
    job_id: str
    agent_id: str
    status: JobStatus
    prompt: str
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 2
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


# =====================================================================
# BACKGROUND AGENT FRAMEWORK
# =====================================================================

class BackgroundAgentFramework:
    """
    Core framework para background agents.

    Responsabilidades:
      1. Spawn jobs (background_spawn)
      2. Persist state to Supabase
      3. Manage timeouts (5 min)
      4. Retry logic (2x on failure)
      5. Result storage (agent_jobs table)
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize framework.

        Args:
          supabase_url: Supabase project URL (env: SUPABASE_URL)
          supabase_key: Supabase API key (env: SUPABASE_KEY)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None

        if SUPABASE_AVAILABLE and self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")
                self.client = None
        else:
            logger.warning("Supabase credentials not available. Jobs will be stored in-memory only.")

    def spawn_job(
        self,
        agent_id: str,
        prompt: str,
        timeout_seconds: int = 300,
        metadata: Optional[Dict] = None,
        callback_url: Optional[str] = None
    ) -> str:
        """
        Spawn a background job.

        Args:
          agent_id: Agent ID (e.g., "manta-03-s5")
          prompt: Task prompt for the agent
          timeout_seconds: Job timeout (default: 300s = 5 min)
          metadata: Additional metadata (dict)
          callback_url: Optional webhook URL for completion

        Returns:
          job_id: UUID of created job

        Raises:
          RuntimeError: If Supabase unavailable
        """
        job_id = str(uuid4())

        job_record = {
            "id": job_id,
            "agent_id": agent_id,
            "status": JobStatus.PENDING.value,
            "prompt": prompt,
            "timeout_seconds": timeout_seconds,
            "metadata": metadata or {},
            "callback_url": callback_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0,
            "max_retries": 2,
            "result": None,
            "error": None,
            "started_at": None,
            "completed_at": None,
        }

        # Persist to Supabase
        if self.client:
            try:
                response = self.client.table("agent_jobs").insert(job_record).execute()
                logger.info(f"Job spawned: {job_id} for agent {agent_id}")
                return job_id
            except Exception as e:
                logger.error(f"Failed to insert job to Supabase: {e}")
                raise RuntimeError(f"Failed to persist job: {e}")
        else:
            logger.warning(f"Job {job_id} created in-memory only (Supabase unavailable)")
            return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """
        Get job status and result.

        Args:
          job_id: Job UUID

        Returns:
          Dict with job details or None if not found
        """
        if not self.client:
            logger.warning("Cannot fetch job without Supabase connection")
            return None

        try:
            response = self.client.table("agent_jobs") \
                .select("*") \
                .eq("id", job_id) \
                .single() \
                .execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Failed to fetch job {job_id}: {e}")
            return None

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[str] = None,
        error: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> bool:
        """
        Update job status in database.

        Args:
          job_id: Job UUID
          status: New JobStatus
          result: Job result (if completed)
          error: Error message (if failed)
          started_at: When job started processing
          completed_at: When job finished

        Returns:
          True if successful, False otherwise
        """
        if not self.client:
            logger.warning(f"Cannot update job {job_id} without Supabase")
            return False

        update_data = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        if result:
            update_data["result"] = result
        if error:
            update_data["error"] = error
        if started_at:
            update_data["started_at"] = started_at
        if completed_at:
            update_data["completed_at"] = completed_at

        try:
            self.client.table("agent_jobs") \
                .update(update_data) \
                .eq("id", job_id) \
                .execute()
            logger.info(f"Job {job_id} updated: {status.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False

    def increment_retry(self, job_id: str) -> bool:
        """
        Increment retry counter for a job.

        Args:
          job_id: Job UUID

        Returns:
          True if successful
        """
        if not self.client:
            return False

        try:
            # Fetch current retry count
            response = self.client.table("agent_jobs") \
                .select("retry_count") \
                .eq("id", job_id) \
                .single() \
                .execute()

            current_retry = response.data.get("retry_count", 0) if response.data else 0
            new_retry = current_retry + 1

            self.client.table("agent_jobs") \
                .update({"retry_count": new_retry}) \
                .eq("id", job_id) \
                .execute()

            logger.info(f"Job {job_id} retry count incremented to {new_retry}")
            return True
        except Exception as e:
            logger.error(f"Failed to increment retry for {job_id}: {e}")
            return False

    def list_jobs(
        self,
        agent_id: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        List background jobs with optional filtering.

        Args:
          agent_id: Filter by agent (optional)
          status: Filter by status (optional)
          limit: Max results (default: 100)

        Returns:
          List of job records
        """
        if not self.client:
            logger.warning("Cannot list jobs without Supabase")
            return []

        try:
            query = self.client.table("agent_jobs").select("*")

            if agent_id:
                query = query.eq("agent_id", agent_id)
            if status:
                query = query.eq("status", status.value)

            response = query.order("created_at", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []

    def cleanup_expired_jobs(self, days_old: int = 7) -> int:
        """
        Delete completed/failed jobs older than N days.

        Args:
          days_old: Only delete jobs older than this (default: 7)

        Returns:
          Number of jobs deleted
        """
        if not self.client:
            return 0

        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()

            # Only delete COMPLETED or FAILED jobs
            response = self.client.table("agent_jobs") \
                .delete() \
                .gte("completed_at", cutoff_date) \
                .in_("status", [JobStatus.COMPLETED.value, JobStatus.FAILED.value]) \
                .execute()

            logger.info(f"Cleaned up {len(response.data) if response.data else 0} expired jobs")
            return len(response.data) if response.data else 0
        except Exception as e:
            logger.error(f"Failed to cleanup jobs: {e}")
            return 0


# =====================================================================
# PUBLIC API — Convenience functions
# =====================================================================

# Global framework instance
_framework: Optional[BackgroundAgentFramework] = None


def get_framework() -> BackgroundAgentFramework:
    """
    Get or create global framework instance.

    Returns:
      BackgroundAgentFramework singleton
    """
    global _framework
    if _framework is None:
        _framework = BackgroundAgentFramework()
    return _framework


def background_spawn(
    agent_id: str,
    prompt: str,
    timeout_seconds: int = 300,
    metadata: Optional[Dict] = None,
    callback_url: Optional[str] = None
) -> str:
    """
    Spawn a background job (public API).

    Usage in agent skill:
      from scripts.background_agent_framework import background_spawn

      job_id = background_spawn(
        agent_id="manta-03-s5",
        prompt="Analise geotécnica de túnel",
        timeout_seconds=300
      )

      print(f"Job started: {job_id}")
      # Don't wait — return immediately to user
      # Status via background_status(job_id)

    Args:
      agent_id: Agent ID (e.g., "manta-03-s5")
      prompt: Task prompt
      timeout_seconds: Timeout in seconds (default: 300)
      metadata: Optional metadata dict
      callback_url: Optional webhook for completion

    Returns:
      job_id: Job UUID
    """
    framework = get_framework()
    return framework.spawn_job(agent_id, prompt, timeout_seconds, metadata, callback_url)


def background_status(job_id: str) -> Optional[Dict]:
    """
    Check job status (public API).

    Usage:
      result = background_status(job_id)
      if result['status'] == 'completed':
        print(result['result'])
      elif result['status'] == 'running':
        print("Still processing...")

    Args:
      job_id: Job UUID

    Returns:
      Dict with job details or None
    """
    framework = get_framework()
    return framework.get_job_status(job_id)


def background_list(agent_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
    """
    List background jobs (public API).

    Usage:
      jobs = background_list(agent_id="manta-03-s5", status="pending")

    Args:
      agent_id: Filter by agent
      status: Filter by status ("pending", "running", "completed", etc)

    Returns:
      List of job records
    """
    framework = get_framework()
    status_enum = JobStatus(status) if status else None
    return framework.list_jobs(agent_id, status_enum)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Background agent framework CLI")
    subparsers = parser.add_subparsers(dest="command")

    # spawn command
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a background job")
    spawn_parser.add_argument("--agent-id", required=True, help="Agent ID")
    spawn_parser.add_argument("--prompt", required=True, help="Task prompt")
    spawn_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    spawn_parser.add_argument("--metadata", help="JSON metadata")

    # status command
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("job_id", help="Job UUID")

    # list command
    list_parser = subparsers.add_parser("list", help="List jobs")
    list_parser.add_argument("--agent-id", help="Filter by agent")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=100, help="Max results")

    # cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup expired jobs")
    cleanup_parser.add_argument("--days", type=int, default=7, help="Delete jobs older than N days")

    args = parser.parse_args()

    framework = get_framework()

    if args.command == "spawn":
        metadata = json.loads(args.metadata) if args.metadata else None
        job_id = framework.spawn_job(
            args.agent_id,
            args.prompt,
            args.timeout,
            metadata
        )
        print(f"Job spawned: {job_id}")

    elif args.command == "status":
        result = framework.get_job_status(args.job_id)
        if result:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Job not found: {args.job_id}")
            sys.exit(1)

    elif args.command == "list":
        status_enum = JobStatus(args.status) if args.status else None
        jobs = framework.list_jobs(args.agent_id, status_enum, args.limit)
        print(json.dumps(jobs, indent=2, default=str))

    elif args.command == "cleanup":
        deleted = framework.cleanup_expired_jobs(args.days)
        print(f"Deleted {deleted} expired jobs")

    else:
        parser.print_help()
