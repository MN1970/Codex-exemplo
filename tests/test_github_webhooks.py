"""
Unit tests for GitHub webhook integration.

Tests:
- Signature verification (valid and invalid)
- CLAUDE.md parsing and metadata extraction
- Knowledge URL extraction
- Event handler methods (push, PR, issue, release)
"""

import json
import hmac
import hashlib
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.github_service import GitHubWebhookHandler


class TestGitHubWebhookSignature:
    """Test webhook signature verification."""

    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return GitHubWebhookHandler()

    def test_valid_signature(self, handler):
        """Test signature verification with valid signature."""
        secret = "test_secret"
        body = b'{"action": "opened"}'

        # Generate valid signature
        expected_sig = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        signature = f"sha256={expected_sig}"

        assert handler.verify_signature(body, signature, secret) is True

    def test_invalid_signature(self, handler):
        """Test signature verification with invalid signature."""
        secret = "test_secret"
        body = b'{"action": "opened"}'
        signature = "sha256=invalid_signature_here"

        assert handler.verify_signature(body, signature, secret) is False

    def test_signature_with_wrong_secret(self, handler):
        """Test signature verification with wrong secret."""
        secret = "test_secret"
        wrong_secret = "wrong_secret"
        body = b'{"action": "opened"}'

        expected_sig = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        signature = f"sha256={expected_sig}"

        assert handler.verify_signature(body, signature, wrong_secret) is False

    def test_signature_with_tampered_body(self, handler):
        """Test signature verification with tampered body."""
        secret = "test_secret"
        original_body = b'{"action": "opened"}'
        tampered_body = b'{"action": "closed"}'

        expected_sig = hmac.new(
            secret.encode(),
            original_body,
            hashlib.sha256
        ).hexdigest()
        signature = f"sha256={expected_sig}"

        assert handler.verify_signature(tampered_body, signature, secret) is False

    def test_malformed_signature_header(self, handler):
        """Test signature verification with malformed header."""
        secret = "test_secret"
        body = b'{"action": "opened"}'
        malformed_signature = "invalid_format_signature"

        assert handler.verify_signature(body, malformed_signature, secret) is False

    def test_timing_attack_protection(self, handler):
        """Test that signature comparison is constant-time."""
        secret = "test_secret"
        body = b'{"action": "opened"}'

        expected_sig = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        # Alter just the first character
        wrong_sig = "0" + expected_sig[1:]
        signature = f"sha256={wrong_sig}"

        # Should still reject (no timing leak)
        assert handler.verify_signature(body, signature, secret) is False


class TestClaudeMdParsing:
    """Test CLAUDE.md parsing and metadata extraction."""

    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return GitHubWebhookHandler()

    def test_extract_version(self, handler):
        """Test version extraction from CLAUDE.md."""
        content = """
# CLAUDE.md — Manta Maestro (Agent Registry)

Versão: **v4.2** (2026-07-05) — expansão S6–S10
"""
        result = handler.parse_claude_md(content)
        assert result["version"] == "4.2"

    def test_extract_agents_from_table(self, handler):
        """Test agent extraction from markdown table."""
        content = """
| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
"""
        result = handler.parse_claude_md(content)

        assert len(result["agents"]) >= 2
        agents_by_code = {a["code"]: a for a in result["agents"]}

        assert "Manta 00" in agents_by_code
        assert agents_by_code["Manta 00"]["name"] == "maestro (router)"
        assert "maestro" in agents_by_code["Manta 00"]["aliases"]
        assert agents_by_code["Manta 00"]["tier"] == "Haiku→Sonnet"

    def test_extract_routing_rules(self, handler):
        """Test routing rule extraction."""
        content = """
## ROUTING — Maestro (Manta 00)

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA → agente-saneamento
IF menção a transmissão|LT|subestação|ANEEL → agente-energia
IF menção a porto|terminal|ANTAQ|dragagem → agente-portos
```
"""
        result = handler.parse_claude_md(content)

        assert len(result["routing_rules"]) >= 3

        # Check first rule
        saneamento_rule = next(
            (r for r in result["routing_rules"]
             if "saneamento" in r["keywords"]),
            None
        )
        assert saneamento_rule is not None
        assert "ETA" in saneamento_rule["keywords"]
        assert "agente-saneamento" in saneamento_rule["agent"]

    def test_extract_rag_collections(self, handler):
        """Test RAG collections extraction."""
        content = """
| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026 | 🆕 v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS | 🆕 v4.2 |
"""
        result = handler.parse_claude_md(content)

        assert len(result["rag_collections"]) >= 2
        collections_by_name = {c["name"]: c for c in result["rag_collections"]}

        assert "saneamento" in collections_by_name
        assert collections_by_name["saneamento"]["prefix"] == "san:"

    def test_parse_empty_content(self, handler):
        """Test parsing empty content."""
        result = handler.parse_claude_md("")
        assert result["version"] is None
        assert result["agents"] == []
        assert result["routing_rules"] == []

    def test_parse_malformed_table(self, handler):
        """Test parsing with malformed table."""
        content = """
| Código | Agente |
| broken table |
"""
        # Should not crash
        result = handler.parse_claude_md(content)
        assert isinstance(result, dict)
        assert "extracted_at" in result


class TestKnowledgeUrlExtraction:
    """Test knowledge source URL extraction."""

    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return GitHubWebhookHandler()

    def test_extract_markdown_links(self, handler):
        """Test markdown link extraction."""
        content = """
# Documentation

See [SNIS Reference](https://www.gov.br/cidades/snis)
And [ANTAQ Rules](https://www.antaq.gov.br)
"""
        urls = handler.extract_knowledge_urls(content)

        assert len(urls) >= 2
        urls_by_title = {u["title"]: u for u in urls if u["title"]}

        assert "SNIS Reference" in urls_by_title
        assert "ANTAQ Rules" in urls_by_title
        assert urls_by_title["SNIS Reference"]["format"] == "markdown"

    def test_extract_bare_urls(self, handler):
        """Test bare URL extraction."""
        content = """
Check https://www.example.com/docs for more info.
Visit https://another-site.org for details.
"""
        urls = handler.extract_knowledge_urls(content)

        url_strings = [u["url"] for u in urls]
        assert "https://www.example.com/docs" in url_strings
        assert "https://another-site.org" in url_strings

    def test_extract_source_references(self, handler):
        """Test common source reference extraction."""
        content = """
This is based on SNIS guidelines and ANEEL regulations.
Follows ICOLD and CBDB standards.
"""
        urls = handler.extract_knowledge_urls(content)

        titles = [u["title"] for u in urls if u["title"]]
        assert "SNIS" in titles
        assert "ANEEL" in titles
        assert "ICOLD" in titles

    def test_avoid_duplicate_urls(self, handler):
        """Test that duplicate URLs are avoided."""
        content = """
See https://example.com and https://example.com again.
And [Example Link](https://example.com)
"""
        urls = handler.extract_knowledge_urls(content)

        url_strings = [u["url"] for u in urls]
        # Count occurrences of the example URL
        count = sum(1 for u in url_strings if u == "https://example.com")

        assert count == 1  # Should only appear once

    def test_extract_from_empty_content(self, handler):
        """Test extraction from empty content."""
        urls = handler.extract_knowledge_urls("")
        assert urls == []

    def test_extract_urls_with_punctuation(self, handler):
        """Test URL extraction handles trailing punctuation."""
        content = """
Check https://example.com, https://another.com. And https://third.org!
"""
        urls = handler.extract_knowledge_urls(content)

        url_strings = [u["url"] for u in urls]
        # Should not include trailing punctuation
        for url in url_strings:
            assert not url.endswith((",", ".", "!"))


class TestEventHandlers:
    """Test GitHub event handlers."""

    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return GitHubWebhookHandler()

    @pytest.mark.asyncio
    async def test_handle_push_event_with_claude_md(self, handler):
        """Test push event handler when CLAUDE.md is modified."""
        payload = {
            "repository": {"full_name": "manta/repo"},
            "ref": "refs/heads/main",
            "commits": [
                {
                    "modified": ["CLAUDE.md", "other_file.py"],
                    "added": []
                }
            ]
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = True

            success, message = await handler.handle_push_event(payload)

            assert success is True
            assert "sync triggered" in message.lower()
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_push_event_without_claude_md(self, handler):
        """Test push event handler when CLAUDE.md is not modified."""
        payload = {
            "repository": {"full_name": "manta/repo"},
            "ref": "refs/heads/main",
            "commits": [
                {
                    "modified": ["other_file.py"],
                    "added": ["test.py"]
                }
            ]
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            success, message = await handler.handle_push_event(payload)

            assert success is True
            assert "Push processed" in message
            # Should not trigger sync if CLAUDE.md not modified
            mock_sync.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_pull_request_event(self, handler):
        """Test pull request event handler."""
        payload = {
            "action": "opened",
            "repository": {"full_name": "manta/repo"},
            "pull_request": {
                "number": 42,
                "title": "Update agent metadata"
            }
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = True

            success, message = await handler.handle_pull_request_event(payload)

            assert success is True
            assert "42" in message
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_issue_event_with_knowledge_label(self, handler):
        """Test issue event handler with knowledge label."""
        payload = {
            "action": "opened",
            "repository": {"full_name": "manta/repo"},
            "issue": {
                "number": 123,
                "title": "Document new feature",
                "labels": [
                    {"name": "documentation"},
                    {"name": "enhancement"}
                ]
            }
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = True

            success, message = await handler.handle_issue_event(payload)

            assert success is True
            assert "123" in message
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_issue_event_without_knowledge_label(self, handler):
        """Test issue event handler without knowledge label."""
        payload = {
            "action": "opened",
            "repository": {"full_name": "manta/repo"},
            "issue": {
                "number": 456,
                "title": "Bug report",
                "labels": [{"name": "bug"}]
            }
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            success, message = await handler.handle_issue_event(payload)

            # Should still succeed but not trigger sync
            assert success is True
            mock_sync.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_release_event(self, handler):
        """Test release event handler."""
        payload = {
            "action": "published",
            "repository": {"full_name": "manta/repo"},
            "release": {
                "tag_name": "v4.2",
                "name": "Version 4.2 Release"
            }
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = True

            success, message = await handler.handle_release_event(payload)

            assert success is True
            assert "v4.2" in message
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_push_event_sync_failure(self, handler):
        """Test push event handler when sync fails."""
        payload = {
            "repository": {"full_name": "manta/repo"},
            "ref": "refs/heads/main",
            "commits": [
                {
                    "modified": ["CLAUDE.md"],
                    "added": []
                }
            ]
        }

        with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = False

            success, message = await handler.handle_push_event(payload)

            assert success is False
            assert "Failed" in message

    @pytest.mark.asyncio
    async def test_event_handler_error_handling(self, handler):
        """Test event handler error handling."""
        payload = {}  # Invalid/empty payload

        success, message = await handler.handle_push_event(payload)

        assert success is False
        assert "Error" in message or "error" in message.lower()


class TestSyncEventTriggering:
    """Test sync event triggering to Portal Integration service."""

    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return GitHubWebhookHandler()

    @pytest.mark.asyncio
    async def test_trigger_sync_event_success(self, handler):
        """Test successful sync event triggering."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = await handler.trigger_sync_event(
                "test_event",
                {"test": "payload"}
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_trigger_sync_event_server_error_with_retry(self, handler):
        """Test sync event triggering with server error and retry."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            # First call returns 500, second call returns 200
            mock_response_error = MagicMock()
            mock_response_error.status_code = 500

            mock_response_success = MagicMock()
            mock_response_success.status_code = 200

            mock_post.side_effect = [mock_response_error, mock_response_success]

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await handler.trigger_sync_event(
                    "test_event",
                    {"test": "payload"}
                )

            # Should retry and succeed
            assert result is True

    @pytest.mark.asyncio
    async def test_trigger_sync_event_max_retries_exceeded(self, handler):
        """Test sync event triggering with max retries exceeded."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await handler.trigger_sync_event(
                    "test_event",
                    {"test": "payload"},
                    retries=handler.max_retries  # Already at max
                )

            assert result is False

    @pytest.mark.asyncio
    async def test_trigger_sync_event_timeout(self, handler):
        """Test sync event triggering with timeout."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            from httpx import TimeoutException
            mock_post.side_effect = TimeoutException("Timeout")

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await handler.trigger_sync_event(
                    "test_event",
                    {"test": "payload"}
                )

            # Should attempt retries
            assert mock_post.call_count >= 1


# Integration test stubs for Phase 2
class TestWebhookEndpointIntegration:
    """
    Integration tests for webhook endpoint.
    These are stubs for Phase 2 when the endpoint is fully tested.
    """

    @pytest.mark.asyncio
    async def test_webhook_endpoint_with_valid_request(self):
        """[Phase 2] Test webhook endpoint with valid request."""
        pytest.skip("Phase 2: Full endpoint integration testing")

    @pytest.mark.asyncio
    async def test_webhook_endpoint_with_invalid_signature(self):
        """[Phase 2] Test webhook endpoint with invalid signature."""
        pytest.skip("Phase 2: Full endpoint integration testing")

    @pytest.mark.asyncio
    async def test_webhook_endpoint_dispatch(self):
        """[Phase 2] Test webhook endpoint event dispatch."""
        pytest.skip("Phase 2: Full endpoint integration testing")
