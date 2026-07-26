#!/usr/bin/env python3
"""
Disaster Recovery — backup verification.

Checks that Supabase Point-in-Time-Recovery (WAL) is enabled and that the
most recent daily snapshot is within the RPO window. Intended to run as a
scheduled job (see docs/TRAINING-GUIDE-DEVOPS-DATA-TEAMS.md Part A §3) and
fail loudly (non-zero exit) if backups are stale or missing.

Usage:
    python scripts/db_backup_verify.py --project-ref abc123 --rpo-minutes 60
    python scripts/db_backup_verify.py --project-ref abc123 --rpo-minutes 60 --alert-webhook $SLACK_WEBHOOK_URL
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("Missing dependency. Install with: pip install requests")
    sys.exit(1)

SUPABASE_MGMT_API = "https://api.supabase.com/v1"


def get_headers():
    token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    if not token:
        print("SUPABASE_ACCESS_TOKEN not set (Management API personal access token)")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}


def check_pitr_enabled(project_ref: str) -> bool:
    resp = requests.get(
        f"{SUPABASE_MGMT_API}/projects/{project_ref}/database/backups",
        headers=get_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return bool(data.get("pitr_enabled", False)), data


def latest_backup_age_minutes(backups_data: dict) -> float:
    backups = backups_data.get("backups", [])
    if not backups:
        return float("inf")
    latest = max(backups, key=lambda b: b["inserted_at"])
    ts = datetime.fromisoformat(latest["inserted_at"].replace("Z", "+00:00"))
    age = datetime.now(timezone.utc) - ts
    return age.total_seconds() / 60.0


def alert(webhook: str, message: str):
    if not webhook:
        return
    try:
        requests.post(webhook, json={"text": message}, timeout=10)
    except Exception as e:
        print(f"Failed to send alert: {e}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-ref", required=True)
    parser.add_argument("--rpo-minutes", type=int, default=60,
                        help="Max acceptable backup age before this is a failure (RPO)")
    parser.add_argument("--alert-webhook", default=os.environ.get("SLACK_WEBHOOK_URL"))
    args = parser.parse_args()

    pitr_enabled, data = check_pitr_enabled(args.project_ref)
    age_minutes = latest_backup_age_minutes(data)

    print(f"Project: {args.project_ref}")
    print(f"PITR enabled: {pitr_enabled}")
    print(f"Latest backup age: {age_minutes:.1f} minutes (RPO target: {args.rpo_minutes} min)")

    failures = []
    if not pitr_enabled:
        failures.append("PITR / WAL archiving is DISABLED — no point-in-time recovery possible.")
    if age_minutes > args.rpo_minutes:
        failures.append(
            f"Latest backup is {age_minutes:.0f} min old, exceeding RPO of {args.rpo_minutes} min."
        )

    if failures:
        msg = "DR BACKUP CHECK FAILED for " + args.project_ref + ":\n- " + "\n- ".join(failures)
        print(f"\n{msg}")
        alert(args.alert_webhook, msg)
        sys.exit(1)

    print("\nBackup check passed.")


if __name__ == "__main__":
    main()
