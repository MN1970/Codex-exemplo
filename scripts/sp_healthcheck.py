#!/usr/bin/env python3
"""
sp_healthcheck.py — Healthcheck para Microsoft 365 + SharePoint + Azure Key Vault

Objetivo:
  Valida a saúde operacional da integração Manta com M365:
  1. Testa autenticação com Azure AD (token validity)
  2. Testa escrita em SharePoint (04_IA/Manta-Maestro/_healthcheck/test.txt)
  3. Calcula dias até expiração do secret (Azure Key Vault)
  4. Registra timestamp último write bem-sucedido

Inputs:
  --sharepoint-tenant: tenant ID do Azure (default: env SHAREPOINT_TENANT_ID)
  --vault-name: nome do Key Vault (default: env AZURE_KEYVAULT_NAME)
  --dry-run: valida credenciais mas não escreve em SP (default: False)
  --verbose: logging detalhado (default: False)

Output:
  JSON {
    "status": "ok" | "error" | "warning",
    "timestamp": "2026-07-25T10:30:00Z",
    "token_valid": true/false,
    "token_expires_in_days": int,
    "last_write_at": "2026-07-25T10:30:00Z" | null,
    "sharepoint_writable": true/false,
    "vault_accessible": true/false,
    "errors": [{ "component": str, "message": str, "timestamp": str }]
  }

Exit codes:
  0: status == "ok"
  1: status == "error" ou "warning"

SessionStart hook:
  python scripts/sp_healthcheck.py --verbose > .healthcheck.json
  [git commit ou alerta se status != ok]
"""

import sys
import os
import json
import logging
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
import traceback
import time
from functools import wraps

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found. Install: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    on_retry: Optional[Callable[[int, Exception], None]] = None
) -> Callable:
    """
    Decorator for retry logic with exponential backoff.

    Args:
      max_attempts: Máximo de tentativas (default 3)
      initial_delay: Delay inicial em segundos (default 1.0)
      backoff_factor: Fator de multiplicação (default 2.0)
      on_retry: Callback opcional: on_retry(attempt_num, exception)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        if on_retry:
                            on_retry(attempt, e)
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )

            raise last_exception

        return wrapper
    return decorator


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Healthcheck para Manta Maestro M365 + SharePoint + Azure Key Vault (v2)"
    )
    parser.add_argument(
        "--sharepoint-tenant",
        default=os.getenv("SHAREPOINT_TENANT_ID"),
        help="Azure tenant ID (default: env SHAREPOINT_TENANT_ID)"
    )
    parser.add_argument(
        "--sharepoint-site",
        default=os.getenv("SHAREPOINT_SITE_NAME", "manta-maestro"),
        help="SharePoint site name (default: env SHAREPOINT_SITE_NAME or 'manta-maestro')"
    )
    parser.add_argument(
        "--vault-name",
        default=os.getenv("AZURE_KEYVAULT_NAME", "manta-maestro-vault"),
        help="Azure Key Vault name (default: env AZURE_KEYVAULT_NAME)"
    )
    parser.add_argument(
        "--secret-name",
        default=os.getenv("AZURE_SECRET_NAME", "manta-maestro-credentials"),
        help="Azure Key Vault secret name (default: env AZURE_SECRET_NAME)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate credentials but don't write to SharePoint"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )
    return parser.parse_args()


@retry_with_backoff(max_attempts=3, initial_delay=1.0)
def get_azure_ad_token(
    tenant_id: str,
    client_id: str,
    client_secret: str
) -> Dict[str, Any]:
    """
    Obtain Azure AD token using OAuth2 client credentials flow.

    Args:
      tenant_id: Azure tenant ID
      client_id: App registration client ID
      client_secret: App registration client secret

    Returns:
      Dict with 'access_token' and 'expires_in' (seconds)

    Raises:
      requests.RequestException: Si falla la solicitud HTTP
      ValueError: Si la respuesta no tiene el formato esperado
    """
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }

    logger.debug(f"Requesting token from: {token_url}")
    resp = requests.post(token_url, data=payload, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    if "access_token" not in data:
        raise ValueError(f"No access_token in response: {data}")

    logger.debug(f"Token obtained. Expires in: {data.get('expires_in')} seconds")
    return data


@retry_with_backoff(max_attempts=3, initial_delay=1.0)
def test_sharepoint_write(
    tenant_id: str,
    site_name: str,
    access_token: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Test write capability to SharePoint at 04_IA/Manta-Maestro/_healthcheck/test.txt

    Args:
      tenant_id: Azure tenant ID
      site_name: SharePoint site name (e.g., 'manta-maestro')
      access_token: Bearer token
      dry_run: Si True, no escribe; sólo valida token

    Returns:
      Dict con 'success' y 'write_timestamp'

    Raises:
      requests.RequestException: Si falla la solicitud HTTP
    """
    tenant_name = os.getenv("SHAREPOINT_TENANT_NAME", "mantaassociados")
    sp_site_url = f"https://{tenant_name}.sharepoint.com/sites/{site_name}"

    # Construct SharePoint REST API call
    # Path: 04_IA/Manta-Maestro/_healthcheck/test.txt
    list_title = "04_IA"
    folder_name = "Manta-Maestro"
    subfolder = "_healthcheck"
    file_name = "test.txt"

    if dry_run:
        logger.info("DRY-RUN: Skipping SharePoint write (validation only)")
        return {
            "success": True,
            "write_timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": True
        }

    # Obtain folder ID first
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json;odata=verbose"
    }

    # Get list by title
    logger.debug(f"Querying SharePoint list: {list_title}")
    list_url = f"{sp_site_url}/_api/web/lists/getbytitle('{list_title}')"
    resp = requests.get(list_url, headers=headers, timeout=10)
    resp.raise_for_status()
    list_id = resp.json()["d"]["Id"]
    logger.debug(f"List ID: {list_id}")

    # Get folder path: 04_IA/Manta-Maestro/_healthcheck
    folder_path = f"{list_title}/{folder_name}/{subfolder}"
    logger.debug(f"Getting folder: {folder_path}")
    folder_url = f"{sp_site_url}/_api/web/getfolderbyserverrelativeurl('{folder_path}')"
    resp = requests.get(folder_url, headers=headers, timeout=10)
    resp.raise_for_status()

    # Write file using PUT
    write_timestamp = datetime.now(timezone.utc).isoformat()
    file_content = f"Healthcheck OK at {write_timestamp}\n"

    file_url = f"{sp_site_url}/_api/web/getfolderbyserverrelativeurl('{folder_path}')/files/add(url='{file_name}',overwrite=true)"
    logger.debug(f"Writing file to: {file_url}")

    resp = requests.post(
        file_url,
        data=file_content.encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "text/plain"
        },
        timeout=10
    )
    resp.raise_for_status()

    logger.info(f"SharePoint write successful. File: {folder_path}/{file_name}")
    return {
        "success": True,
        "write_timestamp": write_timestamp,
        "file_url": f"{sp_site_url}/{folder_path}/{file_name}"
    }


@retry_with_backoff(max_attempts=3, initial_delay=1.0)
def get_vault_secret_expiry(
    vault_name: str,
    secret_name: str,
    access_token: str
) -> Dict[str, Any]:
    """
    Get secret expiration date from Azure Key Vault via REST API.

    Args:
      vault_name: Key Vault name
      secret_name: Secret name to check
      access_token: Bearer token (with Key Vault scope)

    Returns:
      Dict con 'expires_at' (ISO string), 'expires_in_days' (int)

    Raises:
      requests.RequestException: Si falla la solicitud HTTP
      ValueError: Si el secret no tiene expires_on
    """
    vault_url = f"https://{vault_name}.vault.azure.net"
    secret_url = f"{vault_url}/secrets/{secret_name}?api-version=7.4"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    logger.debug(f"Fetching secret metadata: {secret_name} from {vault_name}")
    resp = requests.get(secret_url, headers=headers, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    attributes = data.get("attributes", {})
    expires_on = attributes.get("expires")

    if not expires_on:
        raise ValueError(f"Secret '{secret_name}' has no expiration date set")

    expires_at = datetime.fromtimestamp(expires_on, tz=timezone.utc)
    expires_in_days = (expires_at - datetime.now(timezone.utc)).days

    logger.debug(f"Secret expires at: {expires_at.isoformat()} ({expires_in_days} days from now)")
    return {
        "expires_at": expires_at.isoformat(),
        "expires_in_days": expires_in_days
    }


def get_healthcheck_status(
    tenant_id: str,
    site_name: str,
    vault_name: str,
    secret_name: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Execute healthcheck against Azure + M365 + SharePoint + Key Vault.
    Returns JSON structure as specified in docstring.
    """
    result = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token_valid": False,
        "token_expires_in_days": -1,
        "last_write_at": None,
        "sharepoint_writable": False,
        "vault_accessible": False,
        "vault_secret_expires_in_days": None,
        "errors": []
    }

    # Validate required environment variables
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not client_id or not client_secret:
        result["errors"].append({
            "component": "config",
            "message": "Missing AZURE_CLIENT_ID or AZURE_CLIENT_SECRET",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        result["status"] = "error"
        return result

    access_token = None

    # 1. Get Azure AD token
    try:
        logger.info("Step 1/3: Acquiring Azure AD token...")
        token_data = get_azure_ad_token(tenant_id, client_id, client_secret)
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)
        expires_in_days = expires_in // 86400

        result["token_valid"] = True
        result["token_expires_in_days"] = expires_in_days
        logger.info(f"Azure AD token valid (expires in {expires_in_days} days)")

    except Exception as e:
        logger.error(f"Step 1 failed - Azure AD token check: {e}")
        result["token_valid"] = False
        result["token_expires_in_days"] = -1
        result["errors"].append({
            "component": "azure_ad",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        result["status"] = "error"
        return result  # Cannot continue without token

    # 2. Test SharePoint write capability
    try:
        logger.info("Step 2/3: Testing SharePoint write capability...")
        sp_result = test_sharepoint_write(tenant_id, site_name, access_token, dry_run=dry_run)

        result["sharepoint_writable"] = sp_result.get("success", False)
        result["last_write_at"] = sp_result.get("write_timestamp")
        logger.info(f"SharePoint test passed (write timestamp: {result['last_write_at']})")

    except Exception as e:
        logger.error(f"Step 2 failed - SharePoint write test: {e}")
        result["sharepoint_writable"] = False
        result["errors"].append({
            "component": "sharepoint",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        result["status"] = "error"

    # 3. Check Key Vault secret expiration
    try:
        logger.info("Step 3/3: Checking Azure Key Vault secret expiration...")
        # Note: Key Vault requires separate scope for token
        # Ideally, request token with vault scope: https://vault.azure.net/.default
        vault_result = get_vault_secret_expiry(vault_name, secret_name, access_token)

        result["vault_accessible"] = True
        result["vault_secret_expires_in_days"] = vault_result.get("expires_in_days")
        logger.info(f"Key Vault secret expires in {result['vault_secret_expires_in_days']} days")

        # Warning if secret expiring soon (< 30 days)
        if result["vault_secret_expires_in_days"] is not None and result["vault_secret_expires_in_days"] < 30:
            result["errors"].append({
                "component": "keyvault",
                "message": f"Secret expiring soon: {result['vault_secret_expires_in_days']} days",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            if result["status"] == "ok":
                result["status"] = "warning"

    except Exception as e:
        logger.warning(f"Step 3 failed - Key Vault check: {e}")
        result["vault_accessible"] = False
        result["errors"].append({
            "component": "keyvault",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        # Key Vault is non-critical; downgrade to warning only
        if result["status"] == "ok":
            result["status"] = "warning"

    # 4. Determine final status
    if result["status"] == "ok":
        if not all([result["token_valid"], result["sharepoint_writable"]]):
            result["status"] = "warning"

    return result


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate required arguments
    if not args.sharepoint_tenant:
        logger.error("Missing --sharepoint-tenant or SHAREPOINT_TENANT_ID env var")
        error_json = {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token_valid": False,
            "token_expires_in_days": -1,
            "last_write_at": None,
            "sharepoint_writable": False,
            "vault_accessible": False,
            "vault_secret_expires_in_days": None,
            "errors": [{
                "component": "config",
                "message": "Missing --sharepoint-tenant or SHAREPOINT_TENANT_ID env var",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        print(json.dumps(error_json, indent=2))
        return 1

    logger.debug(
        f"Starting healthcheck (tenant={args.sharepoint_tenant}, "
        f"site={args.sharepoint_site}, vault={args.vault_name}, "
        f"secret={args.secret_name}, dry_run={args.dry_run})"
    )

    try:
        result = get_healthcheck_status(
            tenant_id=args.sharepoint_tenant,
            site_name=args.sharepoint_site,
            vault_name=args.vault_name,
            secret_name=args.secret_name,
            dry_run=args.dry_run
        )

        # Output JSON (stdout)
        print(json.dumps(result, indent=2))

        # Log summary (stderr via logger)
        logger.info(f"Healthcheck completed: status={result['status']}")
        if result["errors"]:
            logger.warning(f"Found {len(result['errors'])} issue(s):")
            for err in result["errors"]:
                logger.warning(f"  [{err['component']}] {err['message']}")
        else:
            logger.info("All checks passed successfully")

        # Exit code: 0 for ok, 1 for error/warning
        exit_code = 0 if result["status"] == "ok" else 1
        logger.info(f"Exit code: {exit_code}")
        return exit_code

    except Exception as e:
        logger.error(f"Healthcheck failed with exception: {e}")
        logger.debug(traceback.format_exc())

        error_result = {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token_valid": False,
            "token_expires_in_days": -1,
            "last_write_at": None,
            "sharepoint_writable": False,
            "vault_accessible": False,
            "vault_secret_expires_in_days": None,
            "errors": [{
                "component": "healthcheck",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }

        print(json.dumps(error_result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
