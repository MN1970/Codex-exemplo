#!/usr/bin/env python3
"""
AskCAD sync client for persona synchronization.

Phase 3.4 - AskCAD Persona Sync
Part 2: AskCAD Sync Client

REST API integration with AskCAD platform for creating, updating, and
managing agent personas. Includes version history and rollback capabilities.

Usage:
    client = AskCADSyncClient(api_key="sk-...", api_url="https://api.askcad.com")
    result = client.sync_persona(metadata)
    client.verify_sync(agent_code)
"""

import os
import json
import logging
import hashlib
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Sync operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class SyncResult:
    """Result of a sync operation"""
    agent_code: str
    status: SyncStatus
    persona_id: Optional[str]
    timestamp: str
    version: str
    message: str
    changes_summary: Dict[str, Any]
    previous_version: Optional[str] = None
    rollback_available: bool = False


@dataclass
class PersonaVersion:
    """Track persona version history"""
    version: str
    timestamp: str
    agent_code: str
    content_hash: str
    sync_status: str
    created_by: str
    changes: Dict[str, Any]


class AskCADSyncClient:
    """Client for synchronizing agent personas with AskCAD platform"""

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.askcad.com",
        timeout: int = 30,
        max_retries: int = 3,
        version_history_file: Optional[str] = None
    ):
        """
        Initialize AskCAD sync client.

        Args:
            api_key: AskCAD API key (sk-...)
            api_url: AskCAD API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            version_history_file: Path to store version history (default: .askcad/version_history.json)
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.version_history_file = Path(
            version_history_file or '.askcad/version_history.json'
        )
        self.session = self._create_session()
        self.version_history: Dict[str, List[PersonaVersion]] = self._load_version_history()

        logger.info(f"Initialized AskCAD client: {self.api_url}")

    def _create_session(self) -> requests.Session:
        """Create authenticated requests session"""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Manta-Maestro-AskCAD-Sync/3.4'
        })
        return session

    def _load_version_history(self) -> Dict[str, List[PersonaVersion]]:
        """Load version history from local storage"""
        if not self.version_history_file.exists():
            return {}

        try:
            data = json.loads(self.version_history_file.read_text())
            # Parse PersonaVersion objects
            history = {}
            for agent_code, versions in data.items():
                history[agent_code] = [
                    PersonaVersion(**v) if isinstance(v, dict) else v
                    for v in versions
                ]
            return history
        except Exception as e:
            logger.warning(f"Could not load version history: {e}")
            return {}

    def _save_version_history(self) -> None:
        """Save version history to local storage"""
        self.version_history_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            agent_code: [asdict(v) for v in versions]
            for agent_code, versions in self.version_history.items()
        }
        self.version_history_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False)
        )

    def sync_persona(
        self,
        metadata: Dict[str, Any],
        dry_run: bool = False,
        change_log: Optional[str] = None
    ) -> SyncResult:
        """
        Sync agent metadata to AskCAD as persona.

        Args:
            metadata: Agent metadata dictionary (from extract_agent_metadata.py)
            dry_run: Validate without actually syncing
            change_log: Description of changes being made

        Returns:
            SyncResult with status and details
        """
        agent_code = metadata.get('agent_code')
        if not agent_code:
            return SyncResult(
                agent_code="unknown",
                status=SyncStatus.FAILED,
                persona_id=None,
                timestamp=datetime.now().isoformat(),
                version=metadata.get('version', '0.0.0'),
                message="Missing agent_code in metadata",
                changes_summary={}
            )

        logger.info(f"Starting sync for {agent_code}")

        try:
            # Normalize metadata to AskCAD schema
            persona_payload = self._normalize_to_persona(metadata)

            # Calculate content hash
            content_hash = self._calculate_hash(persona_payload)

            # Check for changes
            changes, previous_version = self._detect_changes(
                agent_code, content_hash, persona_payload
            )

            if dry_run:
                logger.info(f"[DRY RUN] Would sync {agent_code}")
                return SyncResult(
                    agent_code=agent_code,
                    status=SyncStatus.PENDING,
                    persona_id=None,
                    timestamp=datetime.now().isoformat(),
                    version=metadata.get('version', '1.0.0'),
                    message="Dry run - no changes made",
                    changes_summary=changes
                )

            # Perform actual sync
            if not changes:
                logger.info(f"No changes detected for {agent_code}")
                return SyncResult(
                    agent_code=agent_code,
                    status=SyncStatus.SUCCESS,
                    persona_id=metadata.get('agent_code'),
                    timestamp=datetime.now().isoformat(),
                    version=metadata.get('version', '1.0.0'),
                    message="No changes detected",
                    changes_summary={}
                )

            # Sync to AskCAD
            persona_id = self._get_or_create_persona(agent_code, persona_payload)
            success = self._update_persona(persona_id, persona_payload)

            if success:
                # Record in version history
                self._add_to_version_history(
                    agent_code=agent_code,
                    version=metadata.get('version', '1.0.0'),
                    content_hash=content_hash,
                    changes=changes,
                    previous_version=previous_version,
                    change_log=change_log
                )

                logger.info(f"✓ Successfully synced {agent_code} (ID: {persona_id})")
                return SyncResult(
                    agent_code=agent_code,
                    status=SyncStatus.SUCCESS,
                    persona_id=persona_id,
                    timestamp=datetime.now().isoformat(),
                    version=metadata.get('version', '1.0.0'),
                    message=f"Persona updated successfully",
                    changes_summary=changes,
                    previous_version=previous_version,
                    rollback_available=bool(previous_version)
                )
            else:
                return SyncResult(
                    agent_code=agent_code,
                    status=SyncStatus.FAILED,
                    persona_id=persona_id,
                    timestamp=datetime.now().isoformat(),
                    version=metadata.get('version', '1.0.0'),
                    message="Failed to update persona in AskCAD",
                    changes_summary=changes
                )

        except Exception as e:
            logger.error(f"Sync failed for {agent_code}: {str(e)}", exc_info=True)
            return SyncResult(
                agent_code=agent_code,
                status=SyncStatus.FAILED,
                persona_id=None,
                timestamp=datetime.now().isoformat(),
                version=metadata.get('version', '0.0.0'),
                message=f"Error: {str(e)}",
                changes_summary={}
            )

    def _normalize_to_persona(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert agent metadata to AskCAD persona schema"""
        return {
            "id": metadata.get('agent_code'),
            "name": metadata.get('agent_name'),
            "title": metadata.get('title', metadata.get('agent_name')),
            "description": metadata.get('description', ''),
            "tier": metadata.get('tier', 'Sonnet'),
            "status": metadata.get('status', 'Operacional'),
            "segment": metadata.get('segment'),
            "aliases": metadata.get('aliases', []),
            "capabilities": metadata.get('capabilities', []),
            "rag_collections": metadata.get('rag_collections', []),
            "input_formats": metadata.get('input_formats', []),
            "output_formats": metadata.get('output_formats', []),
            "keywords": metadata.get('keywords', []),
            "contact": metadata.get('contact'),
            "sharepoint_folder": metadata.get('sharepoint_folder'),
            "dependencies": metadata.get('dependencies', []),
            "metadata": {
                "version": metadata.get('version', '1.0.0'),
                "last_updated": metadata.get('last_updated', datetime.now().isoformat()),
                "source_file": metadata.get('metadata_source', '')
            }
        }

    def _calculate_hash(self, payload: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of payload"""
        content = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()

    def _detect_changes(
        self,
        agent_code: str,
        new_hash: str,
        new_payload: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """Detect what has changed from previous version"""
        history = self.version_history.get(agent_code, [])
        if not history:
            return {"type": "new_persona"}, None

        latest = history[-1]
        previous_version = latest.version

        if latest.content_hash == new_hash:
            return {}, previous_version  # No changes

        # Calculate field-level differences
        changes = self._calculate_field_diffs(latest, new_payload, agent_code)
        return changes, previous_version

    def _calculate_field_diffs(
        self,
        old_version: PersonaVersion,
        new_payload: Dict[str, Any],
        agent_code: str
    ) -> Dict[str, Any]:
        """Calculate field-level differences"""
        changes = {}
        # This is a simplified version; full implementation would do deeper comparison
        changes['modified_at'] = datetime.now().isoformat()
        changes['fields_changed'] = list(new_payload.keys())
        return changes

    def _get_or_create_persona(self, agent_code: str, payload: Dict[str, Any]) -> str:
        """Get existing persona or create new one"""
        # Try to get existing
        try:
            response = self._request(
                'GET',
                f'/personas/{agent_code}',
                expect_404=True
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('id', agent_code)
        except Exception as e:
            logger.debug(f"Could not fetch existing persona: {e}")

        # Create new
        try:
            response = self._request(
                'POST',
                '/personas',
                json=payload
            )
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get('id', agent_code)
        except Exception as e:
            logger.error(f"Failed to create persona: {e}")
            raise

        return agent_code

    def _update_persona(self, persona_id: str, payload: Dict[str, Any]) -> bool:
        """Update persona in AskCAD"""
        try:
            response = self._request(
                'PUT',
                f'/personas/{persona_id}',
                json=payload
            )
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Failed to update persona {persona_id}: {e}")
            return False

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        expect_404: bool = False,
        **kwargs
    ) -> requests.Response:
        """Make authenticated API request with retries"""
        url = f"{self.api_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method,
                    url,
                    json=json,
                    timeout=self.timeout,
                    **kwargs
                )

                if response.status_code == 404 and expect_404:
                    return response

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries}), "
                        f"retrying in {wait_time}s: {str(e)}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {str(e)}")
                    raise

    def _add_to_version_history(
        self,
        agent_code: str,
        version: str,
        content_hash: str,
        changes: Dict[str, Any],
        previous_version: Optional[str],
        change_log: Optional[str]
    ) -> None:
        """Record sync in version history"""
        if agent_code not in self.version_history:
            self.version_history[agent_code] = []

        persona_version = PersonaVersion(
            version=version,
            timestamp=datetime.now().isoformat(),
            agent_code=agent_code,
            content_hash=content_hash,
            sync_status='success',
            created_by='github-action',
            changes={
                **changes,
                'change_log': change_log,
                'previous_version': previous_version
            }
        )

        self.version_history[agent_code].append(persona_version)
        self._save_version_history()

    def rollback(self, agent_code: str, target_version: Optional[str] = None) -> SyncResult:
        """
        Rollback persona to previous version.

        Args:
            agent_code: Code of agent to rollback
            target_version: Specific version to rollback to (default: previous)

        Returns:
            SyncResult indicating success/failure
        """
        history = self.version_history.get(agent_code, [])
        if not history:
            return SyncResult(
                agent_code=agent_code,
                status=SyncStatus.FAILED,
                persona_id=None,
                timestamp=datetime.now().isoformat(),
                version="unknown",
                message="No version history found",
                changes_summary={}
            )

        # Find target version
        target = None
        if target_version:
            target = next((v for v in history if v.version == target_version), None)
        else:
            target = history[-2] if len(history) > 1 else None

        if not target:
            return SyncResult(
                agent_code=agent_code,
                status=SyncStatus.FAILED,
                persona_id=None,
                timestamp=datetime.now().isoformat(),
                version=history[-1].version if history else "unknown",
                message="Target version not found",
                changes_summary={}
            )

        # Perform rollback
        try:
            success = self._request(
                'POST',
                f'/personas/{agent_code}/rollback',
                json={'target_version': target.version}
            ).status_code == 200

            if success:
                logger.info(f"Rolled back {agent_code} to version {target.version}")
                return SyncResult(
                    agent_code=agent_code,
                    status=SyncStatus.ROLLED_BACK,
                    persona_id=agent_code,
                    timestamp=datetime.now().isoformat(),
                    version=target.version,
                    message=f"Rolled back to {target.version}",
                    changes_summary={'action': 'rollback'}
                )
        except Exception as e:
            logger.error(f"Rollback failed: {e}")

        return SyncResult(
            agent_code=agent_code,
            status=SyncStatus.FAILED,
            persona_id=None,
            timestamp=datetime.now().isoformat(),
            version=target.version if target else "unknown",
            message="Rollback failed",
            changes_summary={}
        )

    def verify_sync(self, agent_code: str) -> Dict[str, Any]:
        """
        Verify that persona is correctly synced in AskCAD.

        Returns:
            Dict with verification status and mismatches (if any)
        """
        try:
            response = self._request(
                'GET',
                f'/personas/{agent_code}/verify',
                expect_404=True
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'verified': data.get('verified', False),
                    'agent_code': agent_code,
                    'last_sync': data.get('last_sync'),
                    'mismatches': data.get('mismatches', [])
                }
            elif response.status_code == 404:
                return {
                    'verified': False,
                    'agent_code': agent_code,
                    'error': 'Persona not found in AskCAD'
                }
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {
                'verified': False,
                'agent_code': agent_code,
                'error': str(e)
            }

    def get_version_history(self, agent_code: str) -> List[Dict[str, Any]]:
        """Get version history for an agent"""
        if agent_code not in self.version_history:
            return []

        return [
            asdict(v) for v in self.version_history[agent_code]
        ]


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='AskCAD sync client for agent personas'
    )
    parser.add_argument(
        'command',
        choices=['sync', 'verify', 'rollback', 'history'],
        help='Operation to perform'
    )
    parser.add_argument(
        '--agent-code',
        required=True,
        help='Agent code (e.g., manta-03-s1)'
    )
    parser.add_argument(
        '--metadata',
        help='Path to metadata JSON file (for sync command)'
    )
    parser.add_argument(
        '--api-key',
        default=os.getenv('ASKCAD_API_KEY'),
        help='AskCAD API key'
    )
    parser.add_argument(
        '--api-url',
        default=os.getenv('ASKCAD_API_URL', 'https://api.askcad.com'),
        help='AskCAD API URL'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate without syncing'
    )
    parser.add_argument(
        '--target-version',
        help='Target version for rollback'
    )

    args = parser.parse_args()

    if not args.api_key:
        print("Error: ASKCAD_API_KEY environment variable not set")
        sys.exit(1)

    client = AskCADSyncClient(
        api_key=args.api_key,
        api_url=args.api_url
    )

    if args.command == 'sync':
        if not args.metadata:
            print("Error: --metadata required for sync command")
            sys.exit(1)
        metadata = json.loads(Path(args.metadata).read_text())
        result = client.sync_persona(metadata, dry_run=args.dry_run)
        print(json.dumps(asdict(result), indent=2, default=str))

    elif args.command == 'verify':
        result = client.verify_sync(args.agent_code)
        print(json.dumps(result, indent=2))

    elif args.command == 'rollback':
        result = client.rollback(args.agent_code, target_version=args.target_version)
        print(json.dumps(asdict(result), indent=2, default=str))

    elif args.command == 'history':
        history = client.get_version_history(args.agent_code)
        print(json.dumps(history, indent=2))


if __name__ == '__main__':
    import sys
    main()
