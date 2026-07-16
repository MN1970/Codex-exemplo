"""
GitHub webhook handler service.

Processes inbound GitHub webhooks for repository events and manages:
- Agent metadata extraction from CLAUDE.md
- Knowledge base content indexing
- Sync event triggering to Portal Integration service
"""

import asyncio
import hmac
import hashlib
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class GitHubWebhookHandler:
    """Handle GitHub webhook events and extract metadata."""

    def __init__(self):
        """Initialize handler with Portal Integration service URL."""
        self.portal_integration_url = os.getenv(
            "PORTAL_INTEGRATION_URL",
            "http://localhost:8016"
        )
        self.http_timeout = 30.0
        self.max_retries = 3

    async def verify_signature(
        self,
        body: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify GitHub webhook signature using HMAC-SHA256.

        GitHub sends the X-Hub-Signature-256 header in format:
        sha256=<hex_digest>

        Args:
            body: Raw request body bytes
            signature: X-Hub-Signature-256 header value
            secret: GitHub webhook secret

        Returns:
            True if signature is valid, False otherwise
        """
        if not signature.startswith("sha256="):
            logger.warning("Invalid signature format")
            return False

        try:
            expected_sig = hmac.new(
                secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()

            provided_sig = signature[7:]  # Remove "sha256=" prefix

            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_sig, provided_sig)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

    def parse_claude_md(self, content: str) -> Dict[str, Any]:
        """
        Extract agent metadata from CLAUDE.md content.

        Extracts:
        - Agent registry (code, name, status, tier, eixo)
        - Routing rules
        - RAG collections metadata
        - SharePoint routing configuration

        Args:
            content: Raw CLAUDE.md file content

        Returns:
            Dictionary with extracted metadata
        """
        result = {
            "agents": [],
            "routing_rules": [],
            "rag_collections": [],
            "sharepoint_routing": [],
            "version": None,
            "extracted_at": datetime.utcnow().isoformat(),
        }

        try:
            # Extract version
            version_match = re.search(
                r"Versão:\s*\*\*v([\d.]+)\*\*",
                content,
                re.IGNORECASE
            )
            if version_match:
                result["version"] = version_match.group(1)

            # Extract agents from table sections
            # Pattern: | Código | Agente | ... | Status |
            agent_tables = re.finditer(
                r"\|\s*(?:Código|Code)\s*\|.*?\n((?:\|.*?\n)*)",
                content,
                re.IGNORECASE | re.MULTILINE
            )

            for table in agent_tables:
                rows = table.group(1).split("\n")
                for row in rows:
                    if not row.strip() or row.startswith("|--"):
                        continue

                    parts = [p.strip() for p in row.split("|")]
                    if len(parts) >= 5:
                        agent = {
                            "code": parts[1] if parts[1] else None,
                            "name": parts[2] if parts[2] else None,
                            "aliases": [a.strip() for a in parts[3].split(",")]
                            if parts[3] else [],
                            "tier": parts[4] if parts[4] else None,
                            "status": parts[5] if len(parts) > 5 else None,
                        }
                        if agent["code"]:
                            result["agents"].append(agent)

            # Extract routing rules from code block
            routing_pattern = r"```\s*\n(.*?)```"
            routing_blocks = re.finditer(routing_pattern, content, re.DOTALL)

            for block in routing_blocks:
                block_content = block.group(1)
                if "IF menção" in block_content or "IF " in block_content:
                    rules = self._parse_routing_rules(block_content)
                    result["routing_rules"].extend(rules)

            # Extract RAG collections table
            rag_tables = re.finditer(
                r"\|\s*(?:Coleção|Collection)\s*\|.*?\n((?:\|.*?\n)*)",
                content,
                re.IGNORECASE | re.MULTILINE
            )

            for table in rag_tables:
                rows = table.group(1).split("\n")
                for row in rows:
                    if not row.strip() or row.startswith("|--"):
                        continue

                    parts = [p.strip() for p in row.split("|")]
                    if len(parts) >= 4:
                        collection = {
                            "name": parts[1] if parts[1] else None,
                            "prefix": parts[2] if parts[2] else None,
                            "sources": [s.strip() for s in parts[3].split(",")]
                            if parts[3] else [],
                            "status": parts[4] if len(parts) > 4 else None,
                        }
                        if collection["name"]:
                            result["rag_collections"].append(collection)

            # Extract SharePoint routing rules
            sp_tables = re.finditer(
                r"## SHAREPOINT.*?\n(.*?)\n\n",
                content,
                re.IGNORECASE | re.DOTALL
            )

            for table in sp_tables:
                rows = table.group(1).split("\n")
                for row in rows:
                    if not row.strip() or row.startswith("|"):
                        if "Agente" in row:
                            continue
                        if "|" in row:
                            parts = [p.strip() for p in row.split("|")]
                            if len(parts) >= 3:
                                routing = {
                                    "agent": parts[1] if parts[1] else None,
                                    "folder": parts[2] if parts[2] else None,
                                    "pattern": parts[3] if len(parts) > 3 else None,
                                }
                                if routing["agent"]:
                                    result["sharepoint_routing"].append(routing)

            logger.info(
                f"Extracted {len(result['agents'])} agents, "
                f"{len(result['routing_rules'])} routing rules, "
                f"{len(result['rag_collections'])} RAG collections"
            )

        except Exception as e:
            logger.error(f"Error parsing CLAUDE.md: {e}")

        return result

    def _parse_routing_rules(self, block_content: str) -> List[Dict[str, Any]]:
        """
        Parse routing rules from code block.

        Format:
        IF menção a <keywords> → <agent>

        Args:
            block_content: Content of the routing rules code block

        Returns:
            List of parsed routing rules
        """
        rules = []

        # Pattern: IF menção a <keywords> → <agent>
        pattern = r"IF\s+menção\s+a\s+([^→]+?)→\s*(\w+(?:\s+\w+)*)"

        matches = re.finditer(pattern, block_content)
        for match in matches:
            keywords = [k.strip() for k in match.group(1).split("|")]
            agent = match.group(2).strip()

            rules.append({
                "keywords": keywords,
                "agent": agent,
                "type": "keyword_based",
            })

        return rules

    def extract_knowledge_urls(self, content: str) -> List[Dict[str, str]]:
        """
        Extract knowledge source URLs from README/documentation content.

        Finds:
        - Markdown links [text](url)
        - HTTP(S) URLs
        - References to external sources

        Args:
            content: File content to search

        Returns:
            List of extracted URLs with metadata
        """
        urls = []

        try:
            # Extract markdown links
            markdown_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            for match in re.finditer(markdown_pattern, content):
                text, url = match.groups()
                if url.startswith(("http://", "https://")):
                    urls.append({
                        "url": url,
                        "title": text.strip(),
                        "format": "markdown",
                    })

            # Extract bare URLs
            url_pattern = r"https?://[^\s\)]+[^\s\).,;:]"
            for match in re.finditer(url_pattern, content):
                url = match.group(0)
                # Avoid duplicates
                if not any(u["url"] == url for u in urls):
                    urls.append({
                        "url": url,
                        "title": None,
                        "format": "bare",
                    })

            # Extract common documentation sources
            doc_sources = [
                ("SNIS", "https://www.gov.br/cidades/pt-br/acesso-a-informacao/ações-e-programas/saneamento"),
                ("IWA", "https://www.iwanetwork.org"),
                ("ANTAQ", "https://www.gov.br/antaq"),
                ("ANAC", "https://www.gov.br/anac"),
                ("ANEEL", "https://www.aneel.gov.br"),
                ("ICOLD", "https://www.icold-cigb.org"),
                ("CBDB", "https://www.cbdb.org.br"),
            ]

            for source_name, source_url in doc_sources:
                if source_name in content:
                    if not any(u["url"] == source_url for u in urls):
                        urls.append({
                            "url": source_url,
                            "title": source_name,
                            "format": "source",
                        })

            logger.info(f"Extracted {len(urls)} knowledge URLs")

        except Exception as e:
            logger.error(f"Error extracting knowledge URLs: {e}")

        return urls

    async def trigger_sync_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        retries: int = 0
    ) -> bool:
        """
        Trigger a sync event to Portal Integration service.

        Sends a POST request to the integration service with event data.

        Args:
            event_type: Type of event (e.g., "agent_metadata_updated")
            payload: Event payload data
            retries: Current retry attempt number

        Returns:
            True if sync was triggered successfully, False otherwise
        """
        if retries >= self.max_retries:
            logger.error(
                f"Max retries reached for sync event: {event_type}"
            )
            return False

        try:
            url = f"{self.portal_integration_url}/api/sync/webhook"

            request_body = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": payload,
            }

            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                response = await client.post(
                    url,
                    json=request_body,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code in (200, 201, 202, 204):
                    logger.info(
                        f"Successfully triggered sync event: {event_type} "
                        f"(status: {response.status_code})"
                    )
                    return True
                else:
                    logger.warning(
                        f"Sync event failed with status {response.status_code}: "
                        f"{response.text[:200]}"
                    )
                    if response.status_code >= 500:
                        # Retry on server errors
                        await asyncio.sleep(2 ** retries)
                        return await self.trigger_sync_event(
                            event_type, payload, retries + 1
                        )
                    return False

        except httpx.TimeoutException as e:
            logger.warning(f"Timeout triggering sync event: {e}")
            if retries < self.max_retries:
                await asyncio.sleep(2 ** retries)
                return await self.trigger_sync_event(
                    event_type, payload, retries + 1
                )
            return False

        except Exception as e:
            logger.error(f"Error triggering sync event: {e}")
            return False

    async def handle_push_event(
        self,
        payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle GitHub push event.

        Extracts modified files and triggers sync if CLAUDE.md was changed.

        Args:
            payload: GitHub webhook push event payload

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            repo_name = payload.get("repository", {}).get("full_name", "")
            branch = payload.get("ref", "").split("/")[-1]
            commits = payload.get("commits", [])

            logger.info(
                f"Processing push event for {repo_name} on branch {branch} "
                f"with {len(commits)} commits"
            )

            modified_files = set()
            for commit in commits:
                modified_files.update(commit.get("modified", []))
                modified_files.update(commit.get("added", []))

            if "CLAUDE.md" in modified_files or "claude.md" in modified_files:
                logger.info("CLAUDE.md was modified, triggering metadata sync")

                sync_payload = {
                    "repository": repo_name,
                    "branch": branch,
                    "event": "claude_md_updated",
                    "modified_files": list(modified_files),
                }

                success = await self.trigger_sync_event(
                    "agent_metadata_updated",
                    sync_payload
                )

                if success:
                    return True, "CLAUDE.md sync triggered successfully"
                else:
                    return False, "Failed to trigger CLAUDE.md sync"

            return True, f"Push processed ({len(modified_files)} files modified)"

        except Exception as e:
            logger.error(f"Error handling push event: {e}")
            return False, f"Error processing push event: {str(e)}"

    async def handle_pull_request_event(
        self,
        payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle GitHub pull_request event.

        Validates agent metadata in PR changes.

        Args:
            payload: GitHub webhook pull_request event payload

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            repo_name = payload.get("repository", {}).get("full_name", "")

            pr_number = pr.get("number")
            pr_title = pr.get("title", "")

            logger.info(
                f"Processing PR #{pr_number} event (action: {action}) "
                f"for {repo_name}"
            )

            if action in ("opened", "synchronize"):
                sync_payload = {
                    "repository": repo_name,
                    "pull_request": pr_number,
                    "action": action,
                    "title": pr_title,
                }

                success = await self.trigger_sync_event(
                    "pull_request_validation",
                    sync_payload
                )

                if success:
                    return True, f"PR #{pr_number} validation triggered"
                else:
                    return False, f"Failed to validate PR #{pr_number}"

            return True, f"PR event processed (action: {action})"

        except Exception as e:
            logger.error(f"Error handling pull_request event: {e}")
            return False, f"Error processing PR event: {str(e)}"

    async def handle_issue_event(
        self,
        payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle GitHub issue event.

        Indexes issue content for knowledge base if relevant.

        Args:
            payload: GitHub webhook issue event payload

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            action = payload.get("action")
            issue = payload.get("issue", {})
            repo_name = payload.get("repository", {}).get("full_name", "")

            issue_number = issue.get("number")
            issue_title = issue.get("title", "")
            labels = [l.get("name") for l in issue.get("labels", [])]

            logger.info(
                f"Processing issue #{issue_number} event (action: {action}) "
                f"for {repo_name}"
            )

            if action in ("opened", "edited"):
                # Only index if labeled as documentation/knowledge
                if "documentation" in labels or "knowledge" in labels:
                    sync_payload = {
                        "repository": repo_name,
                        "issue_number": issue_number,
                        "title": issue_title,
                        "action": action,
                        "labels": labels,
                    }

                    success = await self.trigger_sync_event(
                        "knowledge_content_indexed",
                        sync_payload
                    )

                    if success:
                        return True, f"Issue #{issue_number} indexed for knowledge base"
                    else:
                        return False, f"Failed to index issue #{issue_number}"

            return True, f"Issue event processed (action: {action})"

        except Exception as e:
            logger.error(f"Error handling issue event: {e}")
            return False, f"Error processing issue event: {str(e)}"

    async def handle_release_event(
        self,
        payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Handle GitHub release event.

        Triggers agent version updates on release.

        Args:
            payload: GitHub webhook release event payload

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            action = payload.get("action")
            release = payload.get("release", {})
            repo_name = payload.get("repository", {}).get("full_name", "")

            release_name = release.get("name", "")
            tag = release.get("tag_name", "")

            logger.info(
                f"Processing release event (action: {action}) "
                f"{tag} for {repo_name}"
            )

            if action == "published":
                sync_payload = {
                    "repository": repo_name,
                    "tag": tag,
                    "name": release_name,
                    "action": action,
                }

                success = await self.trigger_sync_event(
                    "agent_version_released",
                    sync_payload
                )

                if success:
                    return True, f"Release {tag} sync triggered"
                else:
                    return False, f"Failed to sync release {tag}"

            return True, f"Release event processed (action: {action})"

        except Exception as e:
            logger.error(f"Error handling release event: {e}")
            return False, f"Error processing release event: {str(e)}"
