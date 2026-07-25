#!/usr/bin/env python3
"""
Maestro APScheduler Orchestrator — v5.0
Coordinates all background tasks with Prometheus metrics export.
Runs: RAG reindex (daily 02:00 UTC), embedding retrain (weekly Sun 03:00 UTC),
agent memory purge (daily 03:00 UTC), feedback loop (weekly Mon 04:00 UTC).
"""

import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, field

import schedule
import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server, CollectorRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("/var/log/maestro-apscheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REGISTRY = CollectorRegistry()
JOB_COUNT = Gauge("maestro_job_count", "Total background jobs scheduled", registry=REGISTRY)
JOB_SUCCESS = Counter("maestro_job_success_total", "Successful job executions", ["job_name"], registry=REGISTRY)
JOB_FAILURE = Counter("maestro_job_failure_total", "Failed job executions", ["job_name"], registry=REGISTRY)
JOB_DURATION = Histogram(
    "maestro_job_duration_ms",
    "Job execution time in milliseconds",
    ["job_name"],
    registry=REGISTRY
)
LAST_JOB_DURATION = Gauge(
    "maestro_last_job_duration_ms",
    "Last job execution duration in ms",
    ["job_name"],
    registry=REGISTRY
)
RAG_COLLECTIONS = Gauge("maestro_rag_collections", "RAG collections count", registry=REGISTRY)
AGENT_MEMORY_MB = Gauge("maestro_agent_memory_mb", "Agent memory usage in MB", registry=REGISTRY)


@dataclass
class JobConfig:
    """Configuration for a background job."""
    name: str
    schedule_cron: str  # "02:00" format or "weekly:0:03:00" (Mon 03:00)
    script_path: str
    timeout_seconds: int = 300
    retry_count: int = 1
    enabled: bool = True
    error_log_path: str = "/var/log/maestro-jobs-error.log"
    last_run: Optional[datetime] = None
    last_status: str = "pending"  # pending, success, failure


class JobRunner:
    """Executes a job and tracks metrics."""

    def __init__(self, config: JobConfig, repo_root: Path = Path.cwd()):
        self.config = config
        self.repo_root = repo_root
        self.script_full_path = repo_root / config.script_path

    def run(self) -> bool:
        """Execute job and return success status."""
        start_time = time.time()
        logger.info(f"Starting job: {self.config.name}")

        if not self.script_full_path.exists():
            logger.error(f"Script not found: {self.script_full_path}")
            JOB_FAILURE.labels(job_name=self.config.name).inc()
            self.config.last_status = "failure"
            return False

        try:
            # Execute script
            result = self._execute_script()

            duration_ms = (time.time() - start_time) * 1000
            self.config.last_duration = duration_ms
            LAST_JOB_DURATION.labels(job_name=self.config.name).set(duration_ms)
            JOB_DURATION.labels(job_name=self.config.name).observe(duration_ms)

            if result:
                logger.info(f"Job completed successfully: {self.config.name} ({duration_ms:.0f}ms)")
                JOB_SUCCESS.labels(job_name=self.config.name).inc()
                self.config.last_status = "success"
                self.config.last_run = datetime.now()
                return True
            else:
                logger.error(f"Job failed: {self.config.name}")
                JOB_FAILURE.labels(job_name=self.config.name).inc()
                self.config.last_status = "failure"
                return False

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Job exception: {self.config.name}: {e}")
            self._log_error(str(e))
            JOB_FAILURE.labels(job_name=self.config.name).inc()
            LAST_JOB_DURATION.labels(job_name=self.config.name).set(duration_ms)
            self.config.last_status = "failure"
            return False

    def _execute_script(self) -> bool:
        """Execute Python script in subprocess."""
        import subprocess

        try:
            result = subprocess.run(
                ["python3", str(self.script_full_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )

            if result.returncode == 0:
                logger.info(f"Script output:\n{result.stdout[:500]}")  # First 500 chars
                return True
            else:
                logger.error(f"Script error (rc={result.returncode}):\n{result.stderr[:500]}")
                self._log_error(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Job timeout: {self.config.name} (>{self.config.timeout_seconds}s)")
            self._log_error(f"Timeout after {self.config.timeout_seconds}s")
            return False

    def _log_error(self, error_msg: str) -> None:
        """Log error to dedicated error log."""
        try:
            with open(self.config.error_log_path, "a") as f:
                f.write(
                    f"{datetime.now().isoformat()} [{self.config.name}] {error_msg}\n"
                )
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")


class MaestroScheduler:
    """Coordinates all background jobs with Prometheus metrics."""

    def __init__(self, repo_root: Path = Path.cwd(), config_path: Optional[Path] = None):
        self.repo_root = repo_root
        self.config_path = config_path or (repo_root / ".claude" / "scheduler-config.json")
        self.jobs: Dict[str, JobRunner] = {}
        self.running = False
        self._load_jobs()

    def _load_jobs(self) -> None:
        """Load job configuration from file or use defaults."""
        default_jobs = [
            JobConfig(
                name="rag-reindex",
                schedule_cron="02:00",
                script_path="scripts/rag-reindex.py",
                timeout_seconds=600,
                enabled=True
            ),
            JobConfig(
                name="embedding-retrain",
                schedule_cron="weekly:0:03:00",  # Sunday 03:00
                script_path="scripts/eval_embeddings_ab.py",
                timeout_seconds=1800,
                enabled=True
            ),
            JobConfig(
                name="agent-memory-purge",
                schedule_cron="03:00",
                script_path="scripts/agent_memory_purge.py",
                timeout_seconds=300,
                enabled=True
            ),
            JobConfig(
                name="tiering-audit",
                schedule_cron="04:00",
                script_path="scripts/tiering-audit.py",
                timeout_seconds=300,
                enabled=True
            )
        ]

        # Try to load from config file
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config_data = json.load(f)
                logger.info(f"Loaded scheduler config from {self.config_path}")
                # Merge with defaults (config overrides defaults)
                for job_dict in config_data.get("jobs", []):
                    default_jobs = [
                        j for j in default_jobs if j.name != job_dict.get("name")
                    ]
                    default_jobs.append(JobConfig(**job_dict))
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}, using defaults")

        # Create JobRunner instances
        for job_config in default_jobs:
            self.jobs[job_config.name] = JobRunner(job_config, self.repo_root)

        JOB_COUNT.set(len(self.jobs))
        logger.info(f"Loaded {len(self.jobs)} background jobs")

    def schedule_jobs(self) -> None:
        """Schedule all jobs based on cron expressions."""
        for job_name, runner in self.jobs.items():
            if not runner.config.enabled:
                logger.info(f"Job disabled (skipping): {job_name}")
                continue

            cron = runner.config.schedule_cron

            if cron.startswith("weekly:"):
                # Parse "weekly:0:03:00" (Monday 03:00)
                parts = cron.split(":")
                day_of_week = int(parts[1])  # 0=Monday
                hour = int(parts[2])
                minute = int(parts[3])
                schedule.every().monday.at(f"{hour:02d}:{minute:02d}").do(runner.run)
                logger.info(f"Job scheduled (weekly Mon {hour:02d}:{minute:02d}): {job_name}")
            else:
                # Parse "02:00" format
                parts = cron.split(":")
                hour = int(parts[0])
                minute = int(parts[1])
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(runner.run)
                logger.info(f"Job scheduled (daily {hour:02d}:{minute:02d}): {job_name}")

    def update_metrics(self) -> None:
        """Update Prometheus metrics from job state."""
        for runner in self.jobs.values():
            if hasattr(runner.config, "last_duration"):
                LAST_JOB_DURATION.labels(job_name=runner.config.name).set(
                    runner.config.last_duration
                )

    def health_check(self) -> Dict:
        """Return health status for health endpoint."""
        return {
            "status": "healthy" if self.running else "stopped",
            "timestamp": datetime.now().isoformat(),
            "jobs": {
                name: {
                    "status": runner.config.last_status,
                    "last_run": runner.config.last_run.isoformat() if runner.config.last_run else None,
                    "enabled": runner.config.enabled
                }
                for name, runner in self.jobs.items()
            }
        }

    def run(self) -> None:
        """Main scheduler loop."""
        logger.info("=" * 70)
        logger.info("Maestro APScheduler v5.0 starting")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        self.running = True
        self.schedule_jobs()

        try:
            while True:
                schedule.run_pending()
                self.update_metrics()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted")
            self.running = False
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.running = False
            raise


def create_health_endpoint():
    """Create a simple HTTP health endpoint (Flask optional)."""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json

    scheduler_instance = None

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                health = scheduler_instance.health_check()
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(health).encode())
            elif self.path == "/metrics":
                from prometheus_client import generate_latest
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(generate_latest(REGISTRY))
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Suppress default HTTP logging
            pass

    return HealthHandler, scheduler_instance


if __name__ == "__main__":
    # Start Prometheus metrics server on port 8080
    start_http_server(8080, registry=REGISTRY)
    logger.info("Prometheus metrics server started on port 8080")

    # Create and run scheduler
    repo_root = Path(__file__).parent.parent
    scheduler = MaestroScheduler(repo_root)

    try:
        scheduler.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
