#!/usr/bin/env python3
"""
APScheduler Setup — Orquestração em Background (P7)

Configura e executa 4 jobs críticos:
  1. RAG reindex — Daily @ 02:00 UTC
  2. Agent memory purge — Daily @ 03:00 UTC
  3. Feedback loop (retraining) — Weekly @ 03:00 Sunday UTC
  4. Health check — Every 6 hours

Uso:
  python scripts/apscheduler_setup.py --list-jobs
  python scripts/apscheduler_setup.py --run-scheduler
  python scripts/apscheduler_setup.py --test-job rag-reindex
  python scripts/apscheduler_setup.py --pause-job feedback-loop

Dependências:
  pip install APScheduler pytz supabase-py python-dotenv
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s — %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/apscheduler.log', mode='a')
    ]
)
logger = logging.getLogger('apscheduler_setup')

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from pytz import utc
except ImportError:
    logger.error("APScheduler não instalado. Execute: pip install APScheduler pytz")
    sys.exit(1)

# Load environment
from dotenv import load_dotenv
load_dotenv()


class APSchedulerManager:
    """
    Gerenciador central de jobs APScheduler para Manta v5.0 (P7).
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.config_file = self.repo_root / ".claude" / "apscheduler_config.json"
        self.scheduler = BackgroundScheduler(timezone=utc)
        self.jobs_registered = {}
        self.load_config()

    def load_config(self) -> Dict:
        """Load APScheduler config from .claude/apscheduler_config.json"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self.config = json.load(f)
                logger.info(f"Loaded config from {self.config_file}")
                return self.config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")

        # Defaults
        self.config = {
            "enabled": True,
            "timezone": "UTC",
            "jobs": [
                {
                    "id": "rag-reindex",
                    "name": "RAG Reindex (R6)",
                    "enabled": True,
                    "trigger": "cron",
                    "cron": "0 2 * * *",
                    "description": "Reindex all RAG collections, validate embeddings"
                },
                {
                    "id": "agent-memory-purge",
                    "name": "Agent Memory Purge (R10)",
                    "enabled": True,
                    "trigger": "cron",
                    "cron": "0 3 * * *",
                    "description": "Purge expired chunks and low-rating entries"
                },
                {
                    "id": "feedback-loop",
                    "name": "Feedback Loop & Retraining (R9)",
                    "enabled": True,
                    "trigger": "cron",
                    "cron": "0 3 * * 0",
                    "description": "Extract feedback, retrain reranker"
                },
                {
                    "id": "health-check",
                    "name": "Health Check",
                    "enabled": True,
                    "trigger": "cron",
                    "cron": "0 */6 * * *",
                    "description": "Validate maestro_runs schema, indexes, RLS, agent memory"
                }
            ]
        }
        return self.config

    def save_config(self) -> None:
        """Save current config to .claude/apscheduler_config.json"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Saved config to {self.config_file}")

    def register_job(
        self,
        job_id: str,
        job_func: Callable,
        trigger: str,
        cron: str,
        description: str = ""
    ) -> bool:
        """Register a job with APScheduler."""
        try:
            if trigger == "cron":
                parts = cron.split()
                if len(parts) >= 5:
                    minute, hour = int(parts[0]), parts[1]
                    self.scheduler.add_job(
                        job_func,
                        trigger="cron",
                        hour=hour,
                        minute=minute,
                        id=job_id,
                        name=description,
                        coalesce=True,
                        max_instances=1
                    )
                else:
                    logger.error(f"Invalid cron format: {cron}")
                    return False
            else:
                logger.warning(f"Unsupported trigger type: {trigger}")
                return False

            self.jobs_registered[job_id] = {
                "func": job_func,
                "trigger": trigger,
                "cron": cron,
                "description": description,
                "registered_at": datetime.now(utc).isoformat()
            }
            logger.info(f"✓ Job registered: {job_id} ({cron}) — {description}")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to register job {job_id}: {e}")
            return False

    def register_all_jobs(self) -> int:
        """Register all jobs from config."""
        logger.info("=" * 70)
        logger.info("REGISTERING APScheduler JOBS")
        logger.info("=" * 70)

        count = 0
        for job_config in self.config.get("jobs", []):
            if not job_config.get("enabled", True):
                logger.info(f"⊘ Skipping disabled job: {job_config['id']}")
                continue

            job_id = job_config["id"]
            job_func = self._get_job_function(job_id)

            if job_func:
                if self.register_job(
                    job_id=job_id,
                    job_func=job_func,
                    trigger=job_config.get("trigger", "cron"),
                    cron=job_config.get("cron", ""),
                    description=job_config.get("description", "")
                ):
                    count += 1

        logger.info("=" * 70)
        logger.info(f"Registered {count} jobs")
        logger.info("=" * 70)
        return count

    def _get_job_function(self, job_id: str) -> Optional[Callable]:
        """Get job function by ID"""
        job_functions = {
            "rag-reindex": self._job_rag_reindex,
            "agent-memory-purge": self._job_agent_memory_purge,
            "feedback-loop": self._job_feedback_loop,
            "health-check": self._job_health_check
        }
        return job_functions.get(job_id)

    # ===== JOB IMPLEMENTATIONS =====

    def _job_rag_reindex(self) -> None:
        """Job: RAG Reindex (R6) — Daily @ 02:00 UTC"""
        logger.info("[JOB] Starting RAG Reindex...")
        try:
            # Arquivo é `rag-reindex.py` (hífen) — não importável via
            # `from rag_reindex import ...`; carregar pelo caminho.
            import importlib.util

            module_path = self.repo_root / "scripts" / "rag-reindex.py"
            spec = importlib.util.spec_from_file_location("rag_reindex", module_path)
            rag_reindex = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rag_reindex)
            RAGReindexer = rag_reindex.RAGReindexer
            reindexer = RAGReindexer(self.repo_root)
            result = reindexer.run()
            logger.info(f"[JOB] ✓ RAG Reindex completed: {json.dumps(result, indent=2)}")
        except Exception as e:
            logger.error(f"[JOB] ✗ RAG Reindex failed: {e}", exc_info=True)

    def _job_agent_memory_purge(self) -> None:
        """Job: Agent Memory Purge (R10) — Daily @ 03:00 UTC"""
        logger.info("[JOB] Starting Agent Memory Purge...")
        try:
            from agent_memory_purge import AgentMemoryPurger
            purger = AgentMemoryPurger(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_KEY'),
                dry_run=False,
                slack_webhook=os.getenv('SLACK_WEBHOOK_URL')
            )
            success, message = purger.run()
            logger.info(f"[JOB] ✓ Agent Memory Purge: {message}")
        except Exception as e:
            logger.error(f"[JOB] ✗ Agent Memory Purge failed: {e}", exc_info=True)

    def _job_feedback_loop(self) -> None:
        """Job: Feedback Loop & Retraining (R9) — Weekly @ 03:00 Sunday UTC"""
        logger.info("[JOB] Starting Feedback Loop (R9)...")
        try:
            from feedback_loop_job import FeedbackLoopExecutor
            executor = FeedbackLoopExecutor(
                supabase_url=os.getenv('SUPABASE_URL'),
                supabase_key=os.getenv('SUPABASE_KEY'),
                repo_root=self.repo_root
            )
            result = executor.run()
            logger.info(f"[JOB] ✓ Feedback Loop completed: {json.dumps(result, indent=2)}")
        except Exception as e:
            logger.error(f"[JOB] ✗ Feedback Loop failed: {e}", exc_info=True)

    def _job_health_check(self) -> None:
        """Job: Health Check — Every 6 hours"""
        logger.info("[JOB] Starting Health Check...")
        try:
            from healthcheck import HealthChecker
            checker = HealthChecker(self.repo_root)
            result = checker.health_check()
            logger.info(f"[JOB] ✓ Health Check: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"[JOB] ✗ Health Check failed: {e}", exc_info=True)

    def start(self) -> bool:
        """Start the scheduler"""
        if not self.config.get("enabled", True):
            logger.warning("APScheduler is disabled in config")
            return False

        try:
            logger.info("=" * 70)
            logger.info("STARTING APScheduler (P7 — Background Orchestration)")
            logger.info(f"Timezone: {self.config.get('timezone', 'UTC')}")
            logger.info("=" * 70)

            self.register_all_jobs()

            if self.scheduler.running:
                logger.warning("Scheduler already running")
                return True

            self.scheduler.start()
            logger.info("✓ APScheduler started successfully")
            logger.info("")
            logger.info("Scheduled jobs:")
            for job in self.scheduler.get_jobs():
                logger.info(f"  - {job.id}: {job.name} (next run: {job.next_run_time})")
            logger.info("")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to start scheduler: {e}", exc_info=True)
            return False

    def stop(self) -> None:
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("✓ APScheduler stopped")
        except Exception as e:
            logger.error(f"✗ Failed to stop scheduler: {e}")

    def pause_job(self, job_id: str) -> bool:
        """Pause a job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.pause_job(job_id)
                logger.info(f"✓ Job paused: {job_id}")
                return True
            else:
                logger.error(f"✗ Job not found: {job_id}")
                return False
        except Exception as e:
            logger.error(f"✗ Failed to pause job {job_id}: {e}")
            return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.resume_job(job_id)
                logger.info(f"✓ Job resumed: {job_id}")
                return True
            else:
                logger.error(f"✗ Job not found: {job_id}")
                return False
        except Exception as e:
            logger.error(f"✗ Failed to resume job {job_id}: {e}")
            return False

    def list_jobs(self) -> None:
        """List all registered jobs"""
        logger.info("=" * 70)
        logger.info("REGISTERED JOBS")
        logger.info("=" * 70)

        if not self.scheduler.get_jobs():
            logger.info("No jobs registered")
        else:
            for job in self.scheduler.get_jobs():
                logger.info(f"ID: {job.id}")
                logger.info(f"  Name: {job.name}")
                logger.info(f"  Next run: {job.next_run_time}")
                logger.info(f"  Trigger: {job.trigger}")
                logger.info("")

    def test_job(self, job_id: str) -> None:
        """Execute a job immediately (for testing)"""
        logger.info(f"Testing job: {job_id}")
        job_func = self._get_job_function(job_id)
        if job_func:
            try:
                logger.info(f"Executing {job_id}...")
                job_func()
                logger.info(f"✓ Job {job_id} completed successfully")
            except Exception as e:
                logger.error(f"✗ Job {job_id} failed: {e}", exc_info=True)
        else:
            logger.error(f"Job not found: {job_id}")

    def get_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            "running": self.scheduler.running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None,
                    "trigger": str(job.trigger)
                }
                for job in self.scheduler.get_jobs()
            ],
            "timestamp": datetime.now(utc).isoformat()
        }


def main():
    parser = argparse.ArgumentParser(
        description="APScheduler Setup — P7 Background Orchestration"
    )
    parser.add_argument(
        '--run-scheduler',
        action='store_true',
        help='Start APScheduler daemon (foreground)'
    )
    parser.add_argument(
        '--list-jobs',
        action='store_true',
        help='List all registered jobs'
    )
    parser.add_argument(
        '--test-job',
        type=str,
        help='Execute a job immediately (for testing)'
    )
    parser.add_argument(
        '--pause-job',
        type=str,
        help='Pause a scheduled job'
    )
    parser.add_argument(
        '--resume-job',
        type=str,
        help='Resume a paused job'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current scheduler status'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Repository root directory'
    )

    args = parser.parse_args()

    manager = APSchedulerManager(repo_root=args.repo_root)

    if args.run_scheduler:
        logger.info("Mode: RUN_SCHEDULER (foreground)")
        if manager.start():
            try:
                logger.info("Scheduler running. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping scheduler...")
                manager.stop()
        sys.exit(0)

    elif args.list_jobs:
        logger.info("Mode: LIST_JOBS")
        manager.register_all_jobs()
        manager.list_jobs()
        sys.exit(0)

    elif args.test_job:
        logger.info(f"Mode: TEST_JOB ({args.test_job})")
        manager.test_job(args.test_job)
        sys.exit(0)

    elif args.pause_job:
        logger.info(f"Mode: PAUSE_JOB ({args.pause_job})")
        manager.register_all_jobs()
        manager.pause_job(args.pause_job)
        sys.exit(0)

    elif args.resume_job:
        logger.info(f"Mode: RESUME_JOB ({args.resume_job})")
        manager.register_all_jobs()
        manager.resume_job(args.resume_job)
        sys.exit(0)

    elif args.status:
        logger.info("Mode: STATUS")
        manager.register_all_jobs()
        status = manager.get_status()
        logger.info(json.dumps(status, indent=2))
        sys.exit(0)

    else:
        logger.info("No option specified. Running scheduler...")
        if manager.start():
            try:
                logger.info("Scheduler running. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping scheduler...")
                manager.stop()
        sys.exit(0)


if __name__ == '__main__':
    main()
