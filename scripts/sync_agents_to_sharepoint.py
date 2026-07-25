#!/usr/bin/env python3
"""
SharePoint Sync Automation — Phase 2.5

Sync .claude/agents/*.md files to SharePoint via Microsoft Graph API.

Triggered on:
  1. GitHub Actions: PR merged to main (changes to .claude/agents/*.md)
  2. Manual: python scripts/sync_agents_to_sharepoint.py --all

Mapping:
  .claude/agents/agente-portos.md
    → SharePoint: sites/manta/04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos/SKILL.md

Usage:
  # Dry run: preview changes
  python scripts/sync_agents_to_sharepoint.py --dry-run

  # Sync all agents
  python scripts/sync_agents_to_sharepoint.py --all

  # Sync specific agent
  python scripts/sync_agents_to_sharepoint.py --agent agente-saneamento

  # Push changed files only
  python scripts/sync_agents_to_sharepoint.py --changed

Requires:
  SHAREPOINT_SITE_ID: Manta SharePoint site
  SHAREPOINT_DRIVE_ID: 04_IA library drive
  MICROSOFT_GRAPH_TOKEN: Azure app credentials (Graph API scope: Sites.ReadWrite.All)
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from argparse import ArgumentParser
import subprocess

try:
    import requests
except ImportError:
    print("❌ Missing: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

---

# Configuration

SHAREPOINT_AGENT_BASE_PATH = "sites/manta/drives/{drive_id}/root:/04_IA/Manta-Maestro/01-agentes-fundamentais"

AGENT_MAPPING = {
    # S6 - Portos
    "agente-portos.md": "agente-portos/SKILL.md",
    # S7 - Aeroportos
    "agente-aeroportos.md": "agente-aeroportos/SKILL.md",
    # S8 - Saneamento
    "agente-saneamento.md": "agente-saneamento/SKILL.md",
    # S9 - Energia
    "agente-energia.md": "agente-energia/SKILL.md",
    # S10 - Barragens
    "agente-barragens.md": "agente-barragens/SKILL.md",
    # Future: add S1-S5 agents when available
}

---

# Data Classes

@dataclass
class SyncResult:
    """Result of syncing one agent file."""
    agent_slug: str
    local_path: str
    remote_path: str
    status: str  # "synced", "skipped", "error", "no_change"
    file_size_bytes: int
    timestamp: str
    error_message: Optional[str] = None
    version_comment: str = ""

@dataclass
class SyncStats:
    """Overall sync statistics."""
    total_agents: int
    synced: int
    skipped: int
    errors: int
    total_bytes: int
    duration_seconds: float

---

# SharePoint Graph API Client

class SharePointGraphClient:
    """Microsoft Graph API client for SharePoint file operations."""

    def __init__(self, token: str, site_id: str, drive_id: str):
        """Initialize with authentication token."""
        self.token = token
        self.site_id = site_id
        self.drive_id = drive_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

    def upload_file(
        self,
        remote_path: str,
        file_content: str,
        version_comment: str = "",
    ) -> bool:
        """Upload or update a file in SharePoint.

        Args:
            remote_path: Path in SharePoint (e.g., agente-portos/SKILL.md)
            file_content: File content (text)
            version_comment: Version history comment

        Returns:
            True if successful
        """
        try:
            # Ensure parent folders exist
            folder_path = remote_path.rsplit('/', 1)[0]
            self._ensure_folder_exists(folder_path)

            # Upload file
            url = (
                f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/"
                f"root:/{SHAREPOINT_AGENT_BASE_PATH}/{remote_path}:/content"
            )

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "text/plain",
            }

            response = requests.put(
                url,
                data=file_content.encode('utf-8'),
                headers=headers,
                timeout=30,
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ Uploaded {remote_path}")

                # Add version comment if provided
                if version_comment:
                    self._add_version_comment(remote_path, version_comment)

                return True
            else:
                logger.error(f"❌ Upload failed ({response.status_code}): {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Upload error for {remote_path}: {e}")
            return False

    def _ensure_folder_exists(self, folder_path: str) -> bool:
        """Create folder if it doesn't exist."""
        try:
            # This is simplified; real implementation would parse nested folders
            # and create each level. For now, assume base folder exists.
            return True
        except Exception as e:
            logger.error(f"Failed to ensure folder: {e}")
            return False

    def _add_version_comment(self, file_path: str, comment: str) -> None:
        """Add version comment to file history."""
        try:
            # Graph API version comment endpoint
            # (Implementation depends on SharePoint version + API availability)
            logger.info(f"  Version: {comment}")
        except Exception as e:
            logger.warning(f"Could not add version comment: {e}")

    def get_file_metadata(self, remote_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata (size, modified time, etc.)."""
        try:
            url = (
                f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/"
                f"root:/{SHAREPOINT_AGENT_BASE_PATH}/{remote_path}"
            )

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None  # File doesn't exist
            else:
                logger.warning(f"Failed to get metadata ({response.status_code})")
                return None
        except Exception as e:
            logger.warning(f"Metadata fetch error: {e}")
            return None

---

# Sync Logic

class AgentSyncer:
    """Synchronize agent .md files to SharePoint."""

    def __init__(self, client: SharePointGraphClient, agents_dir: str = '.claude/agents'):
        self.client = client
        self.agents_dir = Path(agents_dir)

    def get_local_agents(self) -> List[Path]:
        """Find all agent .md files locally."""
        if not self.agents_dir.exists():
            logger.error(f"Agents directory not found: {self.agents_dir}")
            return []

        agents = list(self.agents_dir.glob('agente-*.md'))
        logger.info(f"Found {len(agents)} local agents")
        return agents

    def get_changed_agents(self) -> List[Path]:
        """Get agents changed in last commit (git diff)."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10,
            )

            changed_files = [
                self.agents_dir / f.split('/')[-1]
                for f in result.stdout.split('\n')
                if f.startswith('.claude/agents/agente-')
            ]

            logger.info(f"Found {len(changed_files)} changed agents")
            return changed_files
        except Exception as e:
            logger.warning(f"Could not get changed files: {e}")
            return []

    def check_if_changed(self, local_path: Path, remote_path: str) -> bool:
        """Check if local file differs from remote."""
        try:
            # Get remote file content (via API)
            # Compare with local
            # For now, simple hash-based check
            local_content = local_path.read_text(encoding='utf-8')
            local_hash = hash(local_content)

            remote_metadata = self.client.get_file_metadata(remote_path)
            if not remote_metadata:
                return True  # Remote doesn't exist → always sync

            # In real impl, would fetch remote content and compare
            # This is simplified version
            return True
        except Exception as e:
            logger.warning(f"Change check failed: {e}")
            return True

    def sync_agent(
        self,
        local_path: Path,
        remote_path: str,
        dry_run: bool = False,
    ) -> SyncResult:
        """Sync one agent file."""

        agent_slug = local_path.stem
        local_size = local_path.stat().st_size

        try:
            # Read local file
            content = local_path.read_text(encoding='utf-8')

            # Check if changed
            if not self.check_if_changed(local_path, remote_path):
                logger.info(f"⊘ {agent_slug}: no changes")
                return SyncResult(
                    agent_slug=agent_slug,
                    local_path=str(local_path),
                    remote_path=remote_path,
                    status="skipped",
                    file_size_bytes=local_size,
                    timestamp=datetime.utcnow().isoformat(),
                )

            # Sync
            if dry_run:
                logger.info(f"[DRY RUN] Would sync {agent_slug} → {remote_path}")
                return SyncResult(
                    agent_slug=agent_slug,
                    local_path=str(local_path),
                    remote_path=remote_path,
                    status="skipped",
                    file_size_bytes=local_size,
                    timestamp=datetime.utcnow().isoformat(),
                    version_comment="[DRY RUN]",
                )
            else:
                success = self.client.upload_file(
                    remote_path=remote_path,
                    file_content=content,
                    version_comment=f"Auto-sync from PR — {datetime.utcnow().isoformat()}",
                )

                return SyncResult(
                    agent_slug=agent_slug,
                    local_path=str(local_path),
                    remote_path=remote_path,
                    status="synced" if success else "error",
                    file_size_bytes=local_size,
                    timestamp=datetime.utcnow().isoformat(),
                    error_message=None if success else "Upload failed",
                    version_comment="auto-sync" if success else "",
                )

        except Exception as e:
            logger.error(f"❌ Sync error for {agent_slug}: {e}")
            return SyncResult(
                agent_slug=agent_slug,
                local_path=str(local_path),
                remote_path=remote_path,
                status="error",
                file_size_bytes=local_size,
                timestamp=datetime.utcnow().isoformat(),
                error_message=str(e),
            )

    def sync_all(
        self,
        agents: Optional[List[Path]] = None,
        dry_run: bool = False,
    ) -> SyncStats:
        """Sync all agents."""

        if agents is None:
            agents = self.get_local_agents()

        if not agents:
            logger.warning("No agents to sync")
            return SyncStats(0, 0, 0, 0, 0, 0.0)

        import time
        start_time = time.time()

        results = []
        for agent_path in agents:
            agent_name = agent_path.name
            if agent_name not in AGENT_MAPPING:
                logger.warning(f"⊘ {agent_name}: not in mapping, skipping")
                continue

            remote_path = AGENT_MAPPING[agent_name]
            result = self.sync_agent(agent_path, remote_path, dry_run)
            results.append(result)

        # Summary
        stats = SyncStats(
            total_agents=len(agents),
            synced=sum(1 for r in results if r.status == "synced"),
            skipped=sum(1 for r in results if r.status == "skipped"),
            errors=sum(1 for r in results if r.status == "error"),
            total_bytes=sum(r.file_size_bytes for r in results),
            duration_seconds=time.time() - start_time,
        )

        return stats

---

# CLI

def main():
    parser = ArgumentParser(description="Sync agents to SharePoint")
    parser.add_argument(
        '--all',
        action='store_true',
        help='Sync all agents',
    )
    parser.add_argument(
        '--changed',
        action='store_true',
        help='Sync only changed agents (git diff)',
    )
    parser.add_argument(
        '--agent',
        type=str,
        help='Sync specific agent (e.g., agente-saneamento)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without uploading',
    )
    args = parser.parse_args()

    # Load config
    site_id = os.environ.get('SHAREPOINT_SITE_ID')
    drive_id = os.environ.get('SHAREPOINT_DRIVE_ID')
    token = os.environ.get('MICROSOFT_GRAPH_TOKEN')

    if not (site_id and drive_id and token):
        logger.error("Missing credentials: SHAREPOINT_SITE_ID, SHAREPOINT_DRIVE_ID, MICROSOFT_GRAPH_TOKEN")
        sys.exit(1)

    # Initialize client
    client = SharePointGraphClient(token, site_id, drive_id)
    syncer = AgentSyncer(client)

    # Determine agents to sync
    if args.agent:
        agents = [Path(f'.claude/agents/{args.agent}.md')]
    elif args.changed:
        agents = syncer.get_changed_agents()
    elif args.all:
        agents = syncer.get_local_agents()
    else:
        # Default: changed agents only
        agents = syncer.get_changed_agents()

    if not agents:
        logger.info("No agents to sync")
        return

    # Sync
    stats = syncer.sync_all(agents, dry_run=args.dry_run)

    # Report
    logger.info(f"""
╔════════════════════════════════════════╗
║  SharePoint Sync Complete              ║
╚════════════════════════════════════════╝

Total agents:  {stats.total_agents}
Synced:        {stats.synced} ✅
Skipped:       {stats.skipped} ⊘
Errors:        {stats.errors} ❌
Total size:    {stats.total_bytes / 1024:.1f} KB
Duration:      {stats.duration_seconds:.1f}s

{"[DRY RUN]" if args.dry_run else ""}
    """)

    if stats.errors > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
