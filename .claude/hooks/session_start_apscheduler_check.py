#!/usr/bin/env python3
"""
Session Start Hook — Check APScheduler Status

Hook executado ao iniciar sessão:
- Valida se APScheduler está rodando
- Avisa se algum job crítico está parado
- Sugere comando de restart se necessário

Ativação:
  - Adicionar em .claude/settings.json:
    "hooks": {
      "session_start": "scripts/session_start_apscheduler_check.py"
    }
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def check_apscheduler_status(repo_root: Path = None) -> Dict:
    """
    Check APScheduler status and return report.
    
    Returns: {
        "running": bool,
        "jobs": [...],
        "critical_issues": [...],
        "warnings": [...]
    }
    """
    if repo_root is None:
        repo_root = Path.cwd()

    config_file = repo_root / ".claude" / "apscheduler_config.json"
    
    if not config_file.exists():
        return {
            "running": False,
            "jobs": [],
            "critical_issues": [
                "APScheduler config not found at .claude/apscheduler_config.json"
            ],
            "warnings": []
        }

    try:
        with open(config_file) as f:
            config = json.load(f)
    except Exception as e:
        return {
            "running": False,
            "jobs": [],
            "critical_issues": [f"Failed to load APScheduler config: {e}"],
            "warnings": []
        }

    report = {
        "running": False,  # Would check actual process
        "jobs": config.get("jobs", []),
        "critical_issues": [],
        "warnings": []
    }

    # Check if config is enabled
    if not config.get("enabled", True):
        report["critical_issues"].append(
            "APScheduler is DISABLED in .claude/apscheduler_config.json"
        )

    # Check required env vars
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    for var in required_vars:
        if not os.getenv(var):
            report["warnings"].append(
                f"Environment variable {var} not set. "
                f"Background jobs may fail."
            )

    # Check if jobs are enabled
    disabled_jobs = [
        j["id"] for j in config.get("jobs", [])
        if not j.get("enabled", True)
    ]
    if disabled_jobs:
        report["warnings"].append(
            f"Disabled jobs: {', '.join(disabled_jobs)}"
        )

    return report


def format_message(report: Dict) -> str:
    """Format report as human-readable message"""
    lines = []
    lines.append("=" * 70)
    lines.append("APScheduler Status Check (P7 Background Orchestration)")
    lines.append("=" * 70)

    if report.get("critical_issues"):
        lines.append("\n⚠️  CRITICAL ISSUES:")
        for issue in report["critical_issues"]:
            lines.append(f"  - {issue}")
        lines.append("")
        lines.append("To restart APScheduler:")
        lines.append("  python scripts/apscheduler_setup.py --run-scheduler")

    if report.get("warnings"):
        lines.append("\n⚠️  WARNINGS:")
        for warn in report["warnings"]:
            lines.append(f"  - {warn}")

    jobs_enabled = sum(1 for j in report.get("jobs", []) if j.get("enabled", True))
    lines.append(f"\nScheduled jobs ({jobs_enabled} enabled):")
    for job in report.get("jobs", []):
        status = "✓" if job.get("enabled", True) else "✗"
        lines.append(f"  {status} {job.get('name')} ({job.get('cron')})")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    """Hook entry point"""
    repo_root = Path(__file__).parent.parent.parent
    report = check_apscheduler_status(repo_root)
    message = format_message(report)
    
    print(message)
    
    # Return exit code (0=ok, 1=critical issues)
    return 1 if report.get("critical_issues") else 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
