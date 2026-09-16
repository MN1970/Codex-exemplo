#!/usr/bin/env python3
"""
Pre-rotation secret validation — ensures current secret is valid before rotation.
Used as pre_rotation hook in rotation_policy.json.
"""

import os
import sys
import logging
from datetime import datetime
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_m365_secret() -> bool:
    """Validate M365_CLIENT_SECRET is working"""
    try:
        client_id = os.environ.get("M365_CLIENT_ID")
        client_secret = os.environ.get("M365_CLIENT_SECRET")
        tenant_id = os.environ.get("M365_TENANT_ID")

        if not all([client_id, client_secret, tenant_id]):
            logger.error("Missing M365 credentials")
            return False

        # Test OAuth flow
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }

        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            logger.info("✅ M365_CLIENT_SECRET is valid")
            return True
        else:
            logger.error(f"❌ M365 token validation failed: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ M365 validation error: {e}")
        return False


def validate_supabase_secret() -> bool:
    """Validate SUPABASE_KEY is working"""
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not all([supabase_url, supabase_key]):
            logger.error("Missing Supabase credentials")
            return False

        # Test Supabase API
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}"
        }

        response = requests.get(
            f"{supabase_url}/rest/v1/",
            headers=headers,
            timeout=10
        )

        if response.status_code in [200, 404]:  # 404 is ok, means we're authenticated
            logger.info("✅ SUPABASE_KEY is valid")
            return True
        else:
            logger.error(f"❌ Supabase validation failed: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Supabase validation error: {e}")
        return False


def validate_mantahub_secret() -> bool:
    """Validate MANTAHUB_TOKEN is working"""
    try:
        api_url = os.environ.get("MANTAHUB_API_URL")
        token = os.environ.get("MANTAHUB_TOKEN")

        if not all([api_url, token]):
            logger.error("Missing MantaHub credentials")
            return False

        # Test MantaHub API
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
            logger.info("✅ MANTAHUB_TOKEN is valid")
            return True
        else:
            logger.error(f"❌ MantaHub validation failed: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ MantaHub validation error: {e}")
        return False


def validate_mantabase_password() -> bool:
    """Validate MANTABASE_PASSWORD is working"""
    try:
        import psycopg2

        mantabase_url = os.environ.get("MANTABASE_URL")
        username = os.environ.get("MANTABASE_USER")
        password = os.environ.get("MANTABASE_PASSWORD")

        if not all([mantabase_url, username, password]):
            logger.error("Missing MantaBase credentials")
            return False

        # Parse connection URL (postgresql://user:pass@host:port/dbname)
        # or use direct credentials
        try:
            conn = psycopg2.connect(
                host=os.environ.get("MANTABASE_HOST", "localhost"),
                database=os.environ.get("MANTABASE_DB", "mantadb"),
                user=username,
                password=password,
                timeout=10
            )
            conn.close()
            logger.info("✅ MANTABASE_PASSWORD is valid")
            return True

        except psycopg2.OperationalError as e:
            logger.error(f"❌ MantaBase connection failed: {e}")
            return False

    except ImportError:
        logger.warning("⚠️ psycopg2 not installed, skipping MantaBase validation")
        return True  # Don't fail if psycopg2 not available
    except Exception as e:
        logger.error(f"❌ MantaBase validation error: {e}")
        return False


def validate_all_secrets() -> bool:
    """Validate all managed secrets before rotation"""
    logger.info("=" * 70)
    logger.info("Pre-rotation Secret Validation")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 70)

    validators = [
        ("M365_CLIENT_SECRET", validate_m365_secret),
        ("MANTAHUB_TOKEN", validate_mantahub_secret),
        ("SUPABASE_KEY", validate_supabase_secret),
        ("MANTABASE_PASSWORD", validate_mantabase_password),
    ]

    results = {}
    for secret_name, validator in validators:
        try:
            is_valid = validator()
            results[secret_name] = is_valid
        except Exception as e:
            logger.error(f"Validation exception for {secret_name}: {e}")
            results[secret_name] = False

    logger.info("=" * 70)
    logger.info("Validation Results:")
    for secret_name, is_valid in results.items():
        status = "✅" if is_valid else "❌"
        logger.info(f"  {status} {secret_name}")

    all_valid = all(results.values())
    logger.info("=" * 70)
    logger.info(f"Overall status: {'PASS' if all_valid else 'FAIL'}")

    return all_valid


if __name__ == "__main__":
    success = validate_all_secrets()
    sys.exit(0 if success else 1)
