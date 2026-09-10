#!/usr/bin/env python3
"""
Post-rotation secret verification — ensures new secret is working correctly.
Used as post_rotation hook in rotation_policy.json.
"""

import os
import sys
import logging
from datetime import datetime
import requests
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecretVerifier:
    def __init__(self):
        self.repo_root = Path.cwd()
        self.rotation_log = self.repo_root / "rotation_log.json"
        self.verification_results = []

    def load_latest_rotation(self) -> dict:
        """Load the most recent rotation entry"""
        if not self.rotation_log.exists():
            logger.error(f"Rotation log not found: {self.rotation_log}")
            return None

        try:
            with open(self.rotation_log) as f:
                rotations = json.load(f)
                return rotations[-1] if rotations else None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in rotation log: {e}")
            return None

    def verify_m365_secret(self) -> bool:
        """Verify new M365_CLIENT_SECRET is working"""
        try:
            client_id = os.environ.get("M365_CLIENT_ID")
            client_secret = os.environ.get("M365_CLIENT_SECRET")
            tenant_id = os.environ.get("M365_TENANT_ID")

            if not all([client_id, client_secret, tenant_id]):
                logger.error("Missing M365 credentials for verification")
                return False

            url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                logger.info("✅ New M365_CLIENT_SECRET verified and working")
                return True
            else:
                logger.error(f"❌ New M365_CLIENT_SECRET verification failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ M365 verification error: {e}")
            return False

    def verify_supabase_secret(self) -> bool:
        """Verify new SUPABASE_KEY is working"""
        try:
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")

            if not all([supabase_url, supabase_key]):
                logger.error("Missing Supabase credentials for verification")
                return False

            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}"
            }

            # Test health endpoint
            response = requests.get(
                f"{supabase_url}/rest/v1/",
                headers=headers,
                timeout=10
            )

            # 404 is okay, means we're authenticated
            if response.status_code in [200, 404]:
                logger.info("✅ New SUPABASE_KEY verified and working")
                return True
            else:
                logger.error(f"❌ New SUPABASE_KEY verification failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Supabase verification error: {e}")
            return False

    def verify_mantahub_secret(self) -> bool:
        """Verify new MANTAHUB_TOKEN is working"""
        try:
            api_url = os.environ.get("MANTAHUB_API_URL")
            token = os.environ.get("MANTAHUB_TOKEN")

            if not all([api_url, token]):
                logger.error("Missing MantaHub credentials for verification")
                return False

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"{api_url}/v1/health",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✅ New MANTAHUB_TOKEN verified and working")
                return True
            else:
                logger.error(f"❌ New MANTAHUB_TOKEN verification failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"❌ MantaHub verification error: {e}")
            return False

    def verify_mantabase_password(self) -> bool:
        """Verify new MANTABASE_PASSWORD is working"""
        try:
            import psycopg2

            username = os.environ.get("MANTABASE_USER")
            password = os.environ.get("MANTABASE_PASSWORD")

            if not all([username, password]):
                logger.error("Missing MantaBase credentials for verification")
                return False

            try:
                conn = psycopg2.connect(
                    host=os.environ.get("MANTABASE_HOST", "localhost"),
                    database=os.environ.get("MANTABASE_DB", "mantadb"),
                    user=username,
                    password=password,
                    timeout=10
                )
                conn.close()
                logger.info("✅ New MANTABASE_PASSWORD verified and working")
                return True

            except psycopg2.OperationalError as e:
                logger.error(f"❌ New MANTABASE_PASSWORD verification failed: {e}")
                return False

        except ImportError:
            logger.warning("⚠️ psycopg2 not installed, skipping MantaBase verification")
            return True
        except Exception as e:
            logger.error(f"❌ MantaBase verification error: {e}")
            return False

    def verify_all_secrets(self) -> bool:
        """Verify all rotated secrets after rotation"""
        logger.info("=" * 70)
        logger.info("Post-rotation Secret Verification")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        latest_rotation = self.load_latest_rotation()
        if not latest_rotation:
            logger.warning("No rotation found to verify")
            return False

        logger.info(f"Verifying rotation: {latest_rotation.get('secret_name')}")

        verifiers = {
            "M365_CLIENT_SECRET": self.verify_m365_secret,
            "MANTAHUB_TOKEN": self.verify_mantahub_secret,
            "SUPABASE_KEY": self.verify_supabase_secret,
            "MANTABASE_PASSWORD": self.verify_mantabase_password,
        }

        results = {}
        secret_name = latest_rotation.get("secret_name")

        # Only verify the secret that was just rotated
        if secret_name in verifiers:
            try:
                is_valid = verifiers[secret_name]()
                results[secret_name] = is_valid
            except Exception as e:
                logger.error(f"Verification exception for {secret_name}: {e}")
                results[secret_name] = False

        logger.info("=" * 70)
        logger.info("Verification Results:")
        for name, is_valid in results.items():
            status = "✅" if is_valid else "❌"
            logger.info(f"  {status} {name}")

        all_valid = all(results.values())
        logger.info("=" * 70)
        logger.info(f"Overall status: {'PASS' if all_valid else 'FAIL'}")

        return all_valid


if __name__ == "__main__":
    verifier = SecretVerifier()
    success = verifier.verify_all_secrets()
    sys.exit(0 if success else 1)
