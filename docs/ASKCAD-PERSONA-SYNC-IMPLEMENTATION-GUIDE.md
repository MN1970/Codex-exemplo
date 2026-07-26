# AskCAD Persona Sync — Phase 3.4 Implementation Guide

**Target**: `maestro-sync/sync_askcad_personas.py`  
**Pattern**: Event-driven on PR merge + nightly scheduled sync  
**Deployment**: GitHub Actions + Cloud Function  
**Timeline**: Phase 3.4 (Jan 01 - Jan 31, 2027)

This guide implements automatic synchronization of Maestro agent definitions to AskCAD personas.

---

## Overview

```
Maestro Agent Repository
  ├── .claude/agents/*.md (source of truth)
  │   ├── agente-saneamento.md
  │   ├── agente-energia.md
  │   ├── agente-portos.md
  │   ├── agente-aeroportos.md
  │   └── agente-barragens.md
  │
  └── CLAUDE.md (master registry)
      └── Agent versions + status
      ↓
AskCAD Persona Sync Service
  ├── Extract agent metadata
  ├── Parse CLAUDE.md for routing rules
  ├── Build persona definitions
  ├── Call AskCAD API: PATCH /personas/{agent_slug}
  └── Record sync event
      ↓
AskCAD Platform
  ├── personas/maestro-saneamento
  ├── personas/maestro-energia
  ├── personas/maestro-portos
  ├── personas/maestro-aeroportos
  └── personas/maestro-barragens
      (auto-updated, always in sync)
```

---

## Part 1: Agent Metadata Extraction

```python
# maestro-sync/agent_metadata.py

from pathlib import Path
from typing import Dict, List, Optional
import re
import yaml

class AgentMetadataExtractor:
    """Extract metadata from agent .md files."""

    def __init__(self, agents_dir: str = ".claude/agents"):
        self.agents_dir = Path(agents_dir)

    def extract_all_agents(self) -> Dict[str, Dict]:
        """Extract metadata from all agent files."""
        agents = {}

        for agent_file in self.agents_dir.glob("*.md"):
            agent_slug = agent_file.stem
            metadata = self.extract_agent(agent_file)

            if metadata:
                agents[agent_slug] = metadata

        return agents

    def extract_agent(self, file_path: Path) -> Optional[Dict]:
        """Extract metadata from single agent file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter
            frontmatter = self._extract_frontmatter(content)
            body = self._extract_body(content)

            # Parse sections
            description = self._extract_section(body, "Descrição") or \
                         self._extract_section(body, "Description") or \
                         self._extract_first_paragraph(body)

            routing_rules = self._extract_routing_rules(body)
            capabilities = self._extract_capabilities(body)
            model_tier = self._extract_model_tier(frontmatter, body)

            return {
                "slug": file_path.stem,
                "title": frontmatter.get("title", file_path.stem),
                "version": frontmatter.get("version", "1.0.0"),
                "description": description,
                "routing_keywords": routing_rules.get("keywords", []),
                "routing_priority": routing_rules.get("priority", 5),
                "capabilities": capabilities,
                "model_tier": model_tier,
                "tags": frontmatter.get("tags", []),
                "segment": self._infer_segment(file_path.stem),
            }

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return None

    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter."""
        match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)

        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except:
                return {}

        return {}

    def _extract_body(self, content: str) -> str:
        """Extract body after frontmatter."""
        match = re.match(r"^---\n.*?\n---\n(.*)", content, re.DOTALL)
        return match.group(1) if match else content

    def _extract_section(self, body: str, section_name: str) -> Optional[str]:
        """Extract content of a markdown section."""
        pattern = f"#{1,3}\\s+{re.escape(section_name)}\\s*\n(.*?)(?=\\n#{1,3}\\s|$)"
        match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)

        if match:
            return match.group(1).strip()

        return None

    def _extract_first_paragraph(self, body: str) -> str:
        """Extract first paragraph as fallback description."""
        lines = body.split("\n")

        for line in lines:
            if line.strip() and not line.startswith("#"):
                return line.strip()[:200]

        return ""

    def _extract_routing_rules(self, body: str) -> Dict:
        """Extract routing keywords and priority."""
        keywords = []
        priority = 5

        # Look for "Roteia quando" or "Keywords" section
        keywords_section = self._extract_section(body, "Roteia quando") or \
                          self._extract_section(body, "Keywords")

        if keywords_section:
            # Parse comma/pipe-separated keywords
            for line in keywords_section.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle pipe-separated: "termo1|termo2|termo3"
                    kws = re.split(r"[,|]", line)
                    keywords.extend([kw.strip() for kw in kws if kw.strip()])

        return {
            "keywords": keywords[:20],  # Limit to 20 keywords
            "priority": priority,
        }

    def _extract_capabilities(self, body: str) -> List[str]:
        """Extract agent capabilities."""
        capabilities = []

        # Look for "Cobre" or "Capabilities" section
        capabilities_section = self._extract_section(body, "Cobre") or \
                              self._extract_section(body, "Capabilities")

        if capabilities_section:
            # Parse list items
            for line in capabilities_section.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("•"):
                    cap = line.lstrip("-• ").strip()
                    if cap:
                        capabilities.append(cap)

        return capabilities[:15]  # Limit to 15 capabilities

    def _extract_model_tier(self, frontmatter: Dict, body: str) -> str:
        """Extract default model tier."""
        # Check frontmatter first
        if "model" in frontmatter:
            return frontmatter["model"].lower()

        # Look for "Tier" or "Model" mentions
        if "opus" in body.lower():
            return "opus"
        elif "sonnet" in body.lower():
            return "sonnet"
        else:
            return "haiku"

    def _infer_segment(self, agent_slug: str) -> Optional[str]:
        """Infer segment from agent slug."""
        mapping = {
            "saneamento": "S8",
            "energia": "S9",
            "portos": "S6",
            "aeroportos": "S7",
            "barragens": "S10",
        }

        for key, segment in mapping.items():
            if key in agent_slug:
                return segment

        return None
```

---

## Part 2: AskCAD API Client

```python
# maestro-sync/askcad_client.py

import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AskCADClient:
    """Client for AskCAD persona API."""

    def __init__(self, api_key: str, api_url: str = "https://api.askcad.com"):
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def get_persona(self, persona_slug: str) -> Optional[Dict]:
        """Get existing persona."""
        try:
            response = self.session.get(
                f"{self.api_url}/personas/{persona_slug}",
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error fetching persona: {e}")
            return None

    def create_persona(self, payload: Dict) -> Optional[Dict]:
        """Create new persona."""
        try:
            response = self.session.post(
                f"{self.api_url}/personas",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f"Created persona: {payload.get('slug')}")
            return response.json()
        except Exception as e:
            logger.error(f"Error creating persona: {e}")
            return None

    def update_persona(self, persona_slug: str, payload: Dict) -> Optional[Dict]:
        """Update existing persona."""
        try:
            response = self.session.patch(
                f"{self.api_url}/personas/{persona_slug}",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f"Updated persona: {persona_slug}")
            return response.json()
        except Exception as e:
            logger.error(f"Error updating persona: {e}")
            return None

    def delete_persona(self, persona_slug: str) -> bool:
        """Delete persona."""
        try:
            response = self.session.delete(
                f"{self.api_url}/personas/{persona_slug}",
                timeout=30,
            )
            response.raise_for_status()
            logger.info(f"Deleted persona: {persona_slug}")
            return True
        except Exception as e:
            logger.error(f"Error deleting persona: {e}")
            return False
```

---

## Part 3: Sync Orchestration

```python
# maestro-sync/sync_askcad_personas.py

import os
import logging
from datetime import datetime
from typing import Dict, List
from agent_metadata import AgentMetadataExtractor
from askcad_client import AskCADClient
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AskCADPersonaSync:
    """Synchronize Maestro agents to AskCAD personas."""

    def __init__(self):
        self.extractor = AgentMetadataExtractor()
        self.askcad = AskCADClient(api_key=os.getenv("ASKCAD_API_KEY"))
        self.db = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )

    def sync_all_personas(self, dry_run: bool = False) -> Dict:
        """Sync all agent personas to AskCAD."""
        logger.info("Starting persona sync...")

        # Extract metadata
        agents = self.extractor.extract_all_agents()
        logger.info(f"Extracted {len(agents)} agents")

        results = {
            "created": [],
            "updated": [],
            "deleted": [],
            "errors": [],
        }

        # Sync each agent
        for agent_slug, metadata in agents.items():
            try:
                persona_slug = f"maestro-{agent_slug}"
                payload = self._build_persona_payload(metadata)

                # Check if exists
                existing = self.askcad.get_persona(persona_slug)

                if dry_run:
                    if existing:
                        logger.info(f"[DRY RUN] Would update: {persona_slug}")
                        results["updated"].append(persona_slug)
                    else:
                        logger.info(f"[DRY RUN] Would create: {persona_slug}")
                        results["created"].append(persona_slug)
                else:
                    if existing:
                        # Update
                        self.askcad.update_persona(persona_slug, payload)
                        results["updated"].append(persona_slug)
                    else:
                        # Create
                        payload["slug"] = persona_slug
                        self.askcad.create_persona(payload)
                        results["created"].append(persona_slug)

            except Exception as e:
                logger.error(f"Error syncing {agent_slug}: {e}")
                results["errors"].append({
                    "agent": agent_slug,
                    "error": str(e),
                })

        # Record sync event
        self._record_sync_event(results, dry_run=dry_run)

        logger.info(f"Sync complete: {len(results['created'])} created, "
                   f"{len(results['updated'])} updated, "
                   f"{len(results['errors'])} errors")

        return results

    def _build_persona_payload(self, metadata: Dict) -> Dict:
        """Build persona definition from agent metadata."""
        return {
            "name": metadata["title"],
            "description": metadata["description"],
            "segment": metadata.get("segment"),
            "version": metadata["version"],
            "keywords": metadata["routing_keywords"],
            "capabilities": metadata["capabilities"],
            "model_tier": metadata["model_tier"],
            "tags": metadata["tags"],
            "metadata": {
                "synchronized_at": datetime.utcnow().isoformat(),
                "sync_version": "1.0",
            }
        }

    def _record_sync_event(self, results: Dict, dry_run: bool = False):
        """Record sync event in database."""
        self.db.table("maestro_askcad_sync_log").insert({
            "timestamp": datetime.utcnow().isoformat(),
            "created_count": len(results["created"]),
            "updated_count": len(results["updated"]),
            "error_count": len(results["errors"]),
            "dry_run": dry_run,
            "status": "success" if len(results["errors"]) == 0 else "partial",
        }).execute()
```

---

## Part 4: CI/CD Integration

```yaml
# .github/workflows/sync-askcad-personas.yml

name: Sync Maestro Personas to AskCAD

on:
  push:
    branches:
      - main
    paths:
      - '.claude/agents/*.md'
      - 'CLAUDE.md'
  schedule:
    # Nightly sync at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  sync-personas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install requests supabase python-dotenv pyyaml

      - name: Sync personas (dry-run)
        env:
          ASKCAD_API_KEY: ${{ secrets.ASKCAD_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: |
          python maestro-sync/sync_askcad_personas.py --dry-run

      - name: Sync personas (live)
        if: github.event_name == 'push'
        env:
          ASKCAD_API_KEY: ${{ secrets.ASKCAD_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: |
          python maestro-sync/sync_askcad_personas.py

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Persona sync dry-run passed. Will auto-sync to AskCAD on merge.'
            })
```

---

## Part 5: Database Schema

```sql
-- maestro_askcad_sync_log table
CREATE TABLE maestro_askcad_sync_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT now(),
    created_count INT DEFAULT 0,
    updated_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    dry_run BOOLEAN DEFAULT false,
    status VARCHAR(20),  -- success, partial, failed
    sync_version VARCHAR(10),
    details JSONB
);

CREATE INDEX idx_askcad_sync_timestamp ON maestro_askcad_sync_log(timestamp);
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|------------|
| **Sync Success Rate** | 100% | maestro_askcad_sync_log.status = success |
| **Sync Latency** | <2 min | Workflow execution time |
| **Persona Currency** | 100% | All 5 personas within 24h of source |
| **API Availability** | 99.9% | Uptime monitoring |

---

## Deployment Checklist

- [ ] Implement AgentMetadataExtractor
- [ ] Implement AskCADClient
- [ ] Implement AskCADPersonaSync orchestration
- [ ] Create GitHub Actions workflow
- [ ] Create Supabase sync log table
- [ ] Configure ASKCAD_API_KEY secret
- [ ] Test dry-run mode
- [ ] Deploy to production
- [ ] Monitor first 7 days
- [ ] Verify all 5 personas synced

---

**Status**: Ready for implementation  
**Owner**: DevOps + AskCAD team  
**Timeline**: Phase 3.4 (Jan 01 - Jan 31, 2027)
