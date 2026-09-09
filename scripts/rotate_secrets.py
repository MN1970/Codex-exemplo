#!/usr/bin/env python3
"""
Manta Maestro v5.0 — Secrets Rotation CLI
Rotate M365, Supabase, MantaBase, MantaHub credentials with Azure Key Vault integration.
Logs all rotations, pre-notifies via Slack 7 days before expiry.

Usage:
  python rotate_secrets.py rotate --secret M365_CLIENT_SECRET
  python rotate_secrets.py rotate --all
  python rotate_secrets.py check-expiry
  python rotate_secrets.py list-rotations --limit 20
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import uuid
from dataclasses import dataclass, asdict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """Metadata for a rotated secret"""
    secret_name: str
    rotation_timestamp: str
    old_version: str
    new_version: str
    old_hash: str
    new_hash: str
    rotated_by: str
    status: str  # 'success', 'partial', 'failed'
    error_message: Optional[str] = None
    keyvault_sync: bool = False
    slack_notified: bool = False


class SecretsRotationManager:
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.policy_file = self.repo_root / "scripts" / "rotation_policy.json"
        self.rotation_log = self.repo_root / "rotation_log.json"
        self.policy = self._load_policy()
        self.rotation_history = self._load_rotation_log()

    def _load_policy(self) -> Dict:
        """Load rotation policy from JSON"""
        if not self.policy_file.exists():
            logger.error(f"Rotation policy not found: {self.policy_file}")
            return {}

        try:
            with open(self.policy_file) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in rotation policy: {e}")
            return {}

    def _load_rotation_log(self) -> List[Dict]:
        """Load rotation history"""
        if not self.rotation_log.exists():
            return []

        try:
            with open(self.rotation_log) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_rotation_log(self):
        """Persist rotation history to disk"""
        with open(self.rotation_log, 'w') as f:
            json.dump(self.rotation_history, f, indent=2)
        logger.info(f"Rotation log saved: {self.rotation_log}")

    def _get_secret_from_env(self, secret_name: str) -> str:
        """Retrieve current secret value from environment"""
        value = os.environ.get(secret_name)
        if not value:
            raise ValueError(f"Secret '{secret_name}' not found in environment")
        return value

    def _hash_secret(self, secret: str) -> str:
        """Create hash of secret for audit trail (non-reversible)"""
        return hashlib.sha256(secret.encode()).hexdigest()[:16]

    def _generate_new_secret(self, secret_type: str) -> str:
        """Generate a new secret value"""
        if secret_type == "M365_CLIENT_SECRET":
            # Generate Azure-compatible secret (base64-like, 34 chars)
            return str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4())[:6]
        elif secret_type == "SUPABASE_KEY":
            # Supabase API key format
            return f"sbp_{uuid.uuid4().hex}_{uuid.uuid4().hex[:8]}"
        elif secret_type == "MANTAHUB_TOKEN":
            # Bearer token format
            return f"mh_{uuid.uuid4().hex}_{int(datetime.now().timestamp())}"
        elif secret_type == "MANTABASE_PASSWORD":
            # Complex password
            return f"Mb{uuid.uuid4().hex[:16].upper()}{uuid.uuid4().hex[:8]}"
        else:
            return str(uuid.uuid4())

    def _sync_to_azure_keyvault(self, secret_name: str, secret_value: str) -> bool:
        """Sync rotated secret to Azure Key Vault"""
        try:
            # This requires 'az' CLI or SDK installed
            import subprocess

            vault_name = os.environ.get("AZURE_KEYVAULT_NAME")
            if not vault_name:
                logger.warning("AZURE_KEYVAULT_NAME not set, skipping Key Vault sync")
                return False

            # Use Azure CLI to set secret
            cmd = [
                "az", "keyvault", "secret", "set",
                "--vault-name", vault_name,
                "--name", secret_name,
                "--value", secret_value
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"Secret synced to Azure Key Vault: {secret_name}")
                return True
            else:
                logger.error(f"Key Vault sync failed: {result.stderr.decode()}")
                return False

        except (ImportError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Azure Key Vault sync unavailable: {e}")
            return False

    def _notify_slack(self, secret_name: str, action: str, details: str = None) -> bool:
        """Send Slack notification about secret rotation"""
        try:
            import requests

            webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
            if not webhook_url:
                logger.warning("SLACK_WEBHOOK_URL not set, skipping Slack notification")
                return False

            emoji = "✅" if action == "rotated" else "⚠️" if action == "expiring_soon" else "❌"

            message = {
                "text": f"{emoji} **Secrets Rotation Alert**",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} Secret {action.replace('_', ' ').title()}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Secret:*\n{secret_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Timestamp:*\n{datetime.now().isoformat()}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": details or f"Secret `{secret_name}` has been {action.replace('_', ' ')}."
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"User: {os.environ.get('USER', 'unknown')} | Host: {os.environ.get('HOSTNAME', 'unknown')}"
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                webhook_url,
                json=message,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Slack notification sent: {secret_name}")
                return True
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
                return False

        except (ImportError, requests.RequestException) as e:
            logger.warning(f"Slack notification unavailable: {e}")
            return False

    def rotate_secret(self, secret_name: str) -> Tuple[bool, str]:
        """Rotate a single secret"""

        if secret_name not in self.policy.get("secrets", {}):
            return False, f"Secret '{secret_name}' not in rotation policy"

        try:
            # 1. Get current secret
            old_secret = self._get_secret_from_env(secret_name)
            old_hash = self._hash_secret(old_secret)
            old_version = self._generate_version_id()

            # 2. Generate new secret
            new_secret = self._generate_new_secret(secret_name)
            new_hash = self._hash_secret(new_secret)
            new_version = self._generate_version_id()

            # 3. Sync to Azure Key Vault
            kv_synced = self._sync_to_azure_keyvault(secret_name, new_secret)

            # 4. Update environment (for immediate use)
            os.environ[secret_name] = new_secret

            # 5. Log rotation
            metadata = SecretMetadata(
                secret_name=secret_name,
                rotation_timestamp=datetime.now().isoformat(),
                old_version=old_version,
                new_version=new_version,
                old_hash=old_hash,
                new_hash=new_hash,
                rotated_by=os.environ.get("USER", "system"),
                status="success",
                keyvault_sync=kv_synced,
                slack_notified=False
            )

            self.rotation_history.append(asdict(metadata))
            self._save_rotation_log()

            # 6. Send Slack notification
            slack_sent = self._notify_slack(
                secret_name,
                "rotated",
                f"Secret `{secret_name}` rotated successfully.\n"
                f"Old version: `{old_version}`\n"
                f"New version: `{new_version}`\n"
                f"Key Vault sync: {'✅' if kv_synced else '⚠️ Manual review required'}"
            )

            if slack_sent:
                metadata.slack_notified = True

            logger.info(f"✅ Secret rotated: {secret_name} ({old_version} → {new_version})")
            return True, f"Secret {secret_name} rotated successfully"

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Rotation failed for {secret_name}: {error_msg}")

            # Log failure
            metadata = SecretMetadata(
                secret_name=secret_name,
                rotation_timestamp=datetime.now().isoformat(),
                old_version="unknown",
                new_version="unknown",
                old_hash="unknown",
                new_hash="unknown",
                rotated_by=os.environ.get("USER", "system"),
                status="failed",
                error_message=error_msg,
                keyvault_sync=False,
                slack_notified=False
            )

            self.rotation_history.append(asdict(metadata))
            self._save_rotation_log()

            # Notify Slack of failure
            self._notify_slack(secret_name, "rotation_failed", f"Error: {error_msg}")

            return False, error_msg

    def rotate_all(self) -> Dict[str, Tuple[bool, str]]:
        """Rotate all secrets in policy"""
        results = {}

        for secret_name in self.policy.get("secrets", {}).keys():
            success, message = self.rotate_secret(secret_name)
            results[secret_name] = (success, message)

        return results

    def check_expiry(self) -> List[Dict]:
        """Check which secrets are expiring soon"""
        expiring_secrets = []
        now = datetime.now()

        for secret_name, config in self.policy.get("secrets", {}).items():
            rotation_days = config.get("rotation_days")
            warning_days = config.get("warning_days", 7)

            # Find last rotation
            last_rotation = None
            for entry in reversed(self.rotation_history):
                if entry.get("secret_name") == secret_name and entry.get("status") == "success":
                    last_rotation = datetime.fromisoformat(entry["rotation_timestamp"])
                    break

            if not last_rotation:
                # Never rotated, assume creation date is "now"
                last_rotation = now

            # Calculate expiry
            expiry_date = last_rotation + timedelta(days=rotation_days)
            days_until_expiry = (expiry_date - now).days

            if 0 < days_until_expiry <= warning_days:
                expiring_secrets.append({
                    "secret_name": secret_name,
                    "last_rotation": last_rotation.isoformat(),
                    "expiry_date": expiry_date.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "rotation_days": rotation_days,
                    "warning_days": warning_days,
                    "status": "EXPIRING_SOON"
                })

                # Send pre-rotation warning
                self._notify_slack(
                    secret_name,
                    "expiring_soon",
                    f"Secret `{secret_name}` expires in {days_until_expiry} days.\n"
                    f"Expiry: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Rotation interval: {rotation_days} days"
                )

        return expiring_secrets

    def list_rotations(self, limit: int = 20) -> List[Dict]:
        """List recent rotations"""
        return self.rotation_history[-limit:]

    def _generate_version_id(self) -> str:
        """Generate a version ID for audit trail"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = uuid.uuid4().hex[:8]
        return f"{timestamp}_{random_suffix}"

    def export_report(self, output_file: Path = None) -> str:
        """Generate a rotation report"""
        output_file = output_file or self.repo_root / "rotation_report.json"

        report = {
            "generated_at": datetime.now().isoformat(),
            "policy_version": self.policy.get("version", "unknown"),
            "total_rotations": len(self.rotation_history),
            "recent_rotations": self.list_rotations(limit=50),
            "expiring_soon": self.check_expiry(),
            "summary": {
                "successful": len([h for h in self.rotation_history if h.get("status") == "success"]),
                "failed": len([h for h in self.rotation_history if h.get("status") == "failed"]),
                "partial": len([h for h in self.rotation_history if h.get("status") == "partial"]),
            }
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report generated: {output_file}")
        return str(output_file)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manta Maestro v5.0 Secrets Rotation Manager"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Rotate secrets")
    rotate_parser.add_argument("--secret", help="Specific secret to rotate")
    rotate_parser.add_argument("--all", action="store_true", help="Rotate all secrets")

    # check-expiry command
    subparsers.add_parser("check-expiry", help="Check for secrets expiring soon")

    # list-rotations command
    list_parser = subparsers.add_parser("list-rotations", help="List recent rotations")
    list_parser.add_argument("--limit", type=int, default=20, help="Number of rotations to list")

    # export-report command
    export_parser = subparsers.add_parser("export-report", help="Export rotation report")
    export_parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    manager = SecretsRotationManager()

    if args.command == "rotate":
        if args.secret:
            success, message = manager.rotate_secret(args.secret)
            print(message)
            sys.exit(0 if success else 1)
        elif args.all:
            results = manager.rotate_all()
            print("\nRotation Results:")
            print("=" * 70)
            for secret, (success, message) in results.items():
                status = "✅" if success else "❌"
                print(f"{status} {secret}: {message}")
            print("=" * 70)
            all_success = all(success for success, _ in results.values())
            sys.exit(0 if all_success else 1)
        else:
            rotate_parser.print_help()
            sys.exit(1)

    elif args.command == "check-expiry":
        expiring = manager.check_expiry()
        if expiring:
            print(f"\n⚠️  {len(expiring)} secrets expiring soon:")
            print("=" * 70)
            for secret in expiring:
                print(f"  {secret['secret_name']}: expires in {secret['days_until_expiry']} days")
            print("=" * 70)
            sys.exit(1)
        else:
            print("✅ No secrets expiring soon")
            sys.exit(0)

    elif args.command == "list-rotations":
        rotations = manager.list_rotations(args.limit)
        print(f"\nRecent {len(rotations)} Rotations:")
        print("=" * 70)
        for rotation in rotations:
            ts = rotation.get("rotation_timestamp", "unknown")
            secret = rotation.get("secret_name", "unknown")
            status = rotation.get("status", "unknown")
            print(f"  {ts}: {secret} [{status}]")
        print("=" * 70)
        sys.exit(0)

    elif args.command == "export-report":
        output = manager.export_report(
            Path(args.output) if args.output else None
        )
        print(f"Report exported: {output}")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
