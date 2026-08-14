#!/usr/bin/env python3
"""
test_healthcheck.py — Unit tests para sp_healthcheck.py

Executa testes sem credenciais reais (mocks HTTP).
"""

import sys
import os
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the healthcheck module
import sp_healthcheck


class TestRetryWithBackoff(unittest.TestCase):
    """Test retry_with_backoff decorator."""

    def test_retry_succeeds_first_attempt(self):
        """Should return immediately if function succeeds."""
        call_count = [0]

        @sp_healthcheck.retry_with_backoff(max_attempts=3, initial_delay=0.01)
        def succeeds():
            call_count[0] += 1
            return "success"

        result = succeeds()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 1)

    def test_retry_succeeds_after_failures(self):
        """Should retry and eventually succeed."""
        call_count = [0]

        @sp_healthcheck.retry_with_backoff(max_attempts=3, initial_delay=0.01)
        def fails_twice():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Transient error")
            return "success"

        result = fails_twice()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)

    def test_retry_exhaustion(self):
        """Should raise exception after max_attempts."""
        @sp_healthcheck.retry_with_backoff(max_attempts=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("Permanent error")

        with self.assertRaises(ValueError) as ctx:
            always_fails()
        self.assertIn("Permanent error", str(ctx.exception))


class TestAzureADToken(unittest.TestCase):
    """Test Azure AD token acquisition."""

    @patch('sp_healthcheck.requests.post')
    def test_get_azure_ad_token_success(self, mock_post):
        """Should extract token from response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "eyJ0eXAi...",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_post.return_value = mock_response

        result = sp_healthcheck.get_azure_ad_token(
            tenant_id="12345678-1234-1234-1234-123456789012",
            client_id="test-client-id",
            client_secret="test-secret"
        )

        self.assertEqual(result["access_token"], "eyJ0eXAi...")
        self.assertEqual(result["expires_in"], 3600)

    @patch('sp_healthcheck.requests.post')
    def test_get_azure_ad_token_missing_token(self, mock_post):
        """Should raise ValueError if token missing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError) as ctx:
            sp_healthcheck.get_azure_ad_token(
                tenant_id="12345678-1234-1234-1234-123456789012",
                client_id="test-client-id",
                client_secret="test-secret"
            )
        self.assertIn("No access_token", str(ctx.exception))


class TestHealthcheckStatus(unittest.TestCase):
    """Test get_healthcheck_status function."""

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-id",
        "AZURE_CLIENT_SECRET": "test-secret"
    })
    def test_missing_credentials(self):
        """Should fail if credentials missing."""
        with patch.dict(os.environ, {"AZURE_CLIENT_ID": "", "AZURE_CLIENT_SECRET": ""}):
            result = sp_healthcheck.get_healthcheck_status(
                tenant_id="12345678-1234-1234-1234-123456789012",
                site_name="test-site",
                vault_name="test-vault",
                secret_name="test-secret",
                dry_run=True
            )

        self.assertEqual(result["status"], "error")
        self.assertFalse(result["token_valid"])
        self.assertTrue(any(e["component"] == "config" for e in result["errors"]))

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-id",
        "AZURE_CLIENT_SECRET": "test-secret"
    })
    @patch('sp_healthcheck.get_azure_ad_token')
    def test_healthcheck_with_dry_run(self, mock_get_token):
        """Should skip SharePoint write in dry-run mode."""
        mock_get_token.return_value = {
            "access_token": "test-token",
            "expires_in": 3600
        }

        result = sp_healthcheck.get_healthcheck_status(
            tenant_id="12345678-1234-1234-1234-123456789012",
            site_name="test-site",
            vault_name="test-vault",
            secret_name="test-secret",
            dry_run=True
        )

        self.assertTrue(result["token_valid"])
        self.assertTrue(result["sharepoint_writable"])  # dry-run passes
        self.assertEqual(result["token_expires_in_days"], 0)  # 3600 // 86400 = 0

    @patch.dict(os.environ, {
        "AZURE_CLIENT_ID": "test-id",
        "AZURE_CLIENT_SECRET": "test-secret"
    })
    @patch('sp_healthcheck.get_azure_ad_token')
    def test_healthcheck_token_failure(self, mock_get_token):
        """Should mark as error if token acquisition fails."""
        mock_get_token.side_effect = Exception("Token service unavailable")

        result = sp_healthcheck.get_healthcheck_status(
            tenant_id="12345678-1234-1234-1234-123456789012",
            site_name="test-site",
            vault_name="test-vault",
            secret_name="test-secret",
            dry_run=True
        )

        self.assertEqual(result["status"], "error")
        self.assertFalse(result["token_valid"])
        self.assertTrue(any(e["component"] == "azure_ad" for e in result["errors"]))


class TestOutputFormat(unittest.TestCase):
    """Test JSON output format."""

    def test_output_structure(self):
        """Should have required fields."""
        with patch.dict(os.environ, {
            "AZURE_CLIENT_ID": "",
            "AZURE_CLIENT_SECRET": ""
        }):
            result = sp_healthcheck.get_healthcheck_status(
                tenant_id="test",
                site_name="test",
                vault_name="test",
                secret_name="test"
            )

        required_fields = [
            "status", "timestamp", "token_valid", "token_expires_in_days",
            "last_write_at", "sharepoint_writable", "vault_accessible",
            "vault_secret_expires_in_days", "errors"
        ]

        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")

    def test_error_structure(self):
        """Errors should have component, message, timestamp."""
        with patch.dict(os.environ, {
            "AZURE_CLIENT_ID": "",
            "AZURE_CLIENT_SECRET": ""
        }):
            result = sp_healthcheck.get_healthcheck_status(
                tenant_id="test",
                site_name="test",
                vault_name="test",
                secret_name="test"
            )

        self.assertTrue(len(result["errors"]) > 0)
        for err in result["errors"]:
            self.assertIn("component", err)
            self.assertIn("message", err)
            self.assertIn("timestamp", err)

    def test_json_serializable(self):
        """Output should be JSON serializable."""
        with patch.dict(os.environ, {
            "AZURE_CLIENT_ID": "",
            "AZURE_CLIENT_SECRET": ""
        }):
            result = sp_healthcheck.get_healthcheck_status(
                tenant_id="test",
                site_name="test",
                vault_name="test",
                secret_name="test"
            )

        json_str = json.dumps(result)
        self.assertIsInstance(json_str, str)
        self.assertTrue(len(json_str) > 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRetryWithBackoff))
    suite.addTests(loader.loadTestsFromTestCase(TestAzureADToken))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthcheckStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormat))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
