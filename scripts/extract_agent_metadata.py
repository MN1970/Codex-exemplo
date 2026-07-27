#!/usr/bin/env python3
"""
Extract agent metadata from CLAUDE.md agent files and normalize to AskCAD schema.

Phase 3.4 - AskCAD Persona Sync
Part 1: Agent Metadata Extractor

Parses .claude/agents/*.md files, extracts YAML frontmatter and content,
normalizes to AskCAD persona schema for synchronization.

Usage:
    python scripts/extract_agent_metadata.py --output agents_metadata.json
    python scripts/extract_agent_metadata.py --validate --strict
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """AskCAD normalized agent persona schema"""
    agent_code: str              # e.g., "manta-03-s1"
    agent_name: str              # e.g., "agente-infraestrutura"
    title: str                   # Display title
    tier: str                    # Haiku, Sonnet, Opus
    status: str                  # Operacional, Planejado, Parcial
    segment: Optional[str]       # S1, S2, ... S10 for vertical agents
    aliases: List[str]           # Alternative names
    description: str             # Short description (< 200 chars)
    capabilities: List[str]      # List of capabilities
    rag_collections: List[str]   # RAG collection prefixes (e.g., "rod:", "pon:")
    input_formats: List[str]     # Supported input formats (.pdf, .dwg, etc.)
    output_formats: List[str]    # Supported output formats
    keywords: List[str]          # Routing keywords
    version: str                 # Semantic version
    last_updated: str            # ISO 8601 timestamp
    contact: Optional[str]       # Email or team contact
    sharepoint_folder: Optional[str]  # Suggested SP folder
    dependencies: List[str]      # Other agents this depends on
    metadata_source: str         # Path to source .md file


class AgentMetadataExtractor:
    """Extract and validate agent metadata from markdown files"""

    def __init__(self, agents_dir: str = ".claude/agents"):
        self.agents_dir = Path(agents_dir)
        self.agents: Dict[str, AgentMetadata] = {}
        self.errors: List[Tuple[str, str]] = []
        self.warnings: List[Tuple[str, str]] = []

    def extract_all(self, strict: bool = False) -> Dict[str, AgentMetadata]:
        """Extract metadata from all agent markdown files"""
        if not self.agents_dir.exists():
            raise FileNotFoundError(f"Agents directory not found: {self.agents_dir}")

        agent_files = sorted(self.agents_dir.glob("*.md"))
        if not agent_files:
            logger.warning(f"No agent files found in {self.agents_dir}")
            return {}

        for agent_file in agent_files:
            try:
                metadata = self._extract_from_file(agent_file)
                if metadata:
                    self.agents[metadata.agent_code] = metadata
                    logger.info(f"✓ Extracted: {metadata.agent_code} ({metadata.agent_name})")
            except Exception as e:
                error_msg = f"Failed to extract {agent_file.name}: {str(e)}"
                self.errors.append((str(agent_file), error_msg))
                logger.error(error_msg)
                if strict:
                    raise

        return self.agents

    def _extract_from_file(self, file_path: Path) -> Optional[AgentMetadata]:
        """Extract metadata from a single agent markdown file"""
        content = file_path.read_text(encoding='utf-8')

        # Parse YAML frontmatter (if exists)
        frontmatter = self._parse_frontmatter(content)
        body = self._extract_body(content)

        # Validate required fields
        required_fields = ['agent_code', 'agent_name', 'tier', 'status']
        for field in required_fields:
            if field not in frontmatter:
                raise ValueError(f"Missing required field: {field}")

        # Extract from body if not in frontmatter
        if not frontmatter.get('description'):
            frontmatter['description'] = self._extract_description(body)

        if not frontmatter.get('keywords'):
            frontmatter['keywords'] = self._extract_keywords(body)

        if not frontmatter.get('capabilities'):
            frontmatter['capabilities'] = self._extract_capabilities(body)

        # Build metadata object
        metadata = AgentMetadata(
            agent_code=frontmatter['agent_code'],
            agent_name=frontmatter['agent_name'],
            title=frontmatter.get('title', frontmatter['agent_name']),
            tier=frontmatter['tier'],
            status=frontmatter['status'],
            segment=frontmatter.get('segment'),
            aliases=frontmatter.get('aliases', []),
            description=frontmatter.get('description', '')[:200],
            capabilities=frontmatter.get('capabilities', []),
            rag_collections=frontmatter.get('rag_collections', []),
            input_formats=frontmatter.get('input_formats', ['.pdf', '.dwg', '.xlsx']),
            output_formats=frontmatter.get('output_formats', ['.pdf', '.json', '.csv']),
            keywords=frontmatter.get('keywords', []),
            version=frontmatter.get('version', '1.0.0'),
            last_updated=frontmatter.get('last_updated', datetime.now().isoformat()),
            contact=frontmatter.get('contact'),
            sharepoint_folder=frontmatter.get('sharepoint_folder'),
            dependencies=frontmatter.get('dependencies', []),
            metadata_source=str(file_path)
        )

        # Validate extracted metadata
        self._validate_metadata(metadata)
        return metadata

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown"""
        # Pattern: --- YAML content --- on separate lines
        pattern = r'^---\n(.*?)\n---\n'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError as e:
                self.warnings.append(("frontmatter", f"YAML parse error: {e}"))
                return {}
        return {}

    def _extract_body(self, content: str) -> str:
        """Extract markdown body without frontmatter"""
        pattern = r'^---\n(.*?)\n---\n(.*)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(2) if match else content

    def _extract_description(self, body: str) -> str:
        """Extract first paragraph as description"""
        # First non-empty paragraph
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        for line in lines:
            if not line.startswith('#') and len(line) > 20:
                return line[:200]
        return ""

    def _extract_keywords(self, body: str) -> List[str]:
        """Extract routing keywords from body"""
        keywords = []
        # Look for "keywords:", "routing:", "triggers:" sections
        patterns = [
            r'[Kk]eywords?:?\s+([^\n]+)',
            r'[Rr]outing?:?\s+([^\n]+)',
            r'[Tt]riggers?:?\s+([^\n]+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, body)
            for match in matches:
                # Split on comma, pipe, or space
                words = re.split(r'[,|]\s*', match)
                keywords.extend([w.strip() for w in words if w.strip()])
        return list(set(keywords))[:20]  # Limit to 20 unique keywords

    def _extract_capabilities(self, body: str) -> List[str]:
        """Extract capabilities from body"""
        capabilities = []
        # Look for capability lists
        pattern = r'(?:Capabilit|Funcion|Recurso).*?:?\s*\n((?:[-*]\s+.*\n)+)'
        matches = re.findall(pattern, body, re.IGNORECASE)
        for match in matches:
            lines = [line.strip('- *').strip() for line in match.split('\n') if line.strip()]
            capabilities.extend(lines)
        return capabilities[:15]  # Limit to 15

    def _validate_metadata(self, metadata: AgentMetadata) -> None:
        """Validate extracted metadata"""
        # Agent code format: should match pattern
        if not re.match(r'^manta-\d+(-s\d+)?$', metadata.agent_code, re.IGNORECASE):
            self.warnings.append((
                metadata.agent_code,
                f"Non-standard agent code format: {metadata.agent_code}"
            ))

        # Tier validation
        valid_tiers = ['Haiku', 'Sonnet', 'Opus', 'Haiku→Sonnet', 'Sonnet/Opus']
        if metadata.tier not in valid_tiers:
            self.warnings.append((
                metadata.agent_code,
                f"Unknown tier: {metadata.tier}"
            ))

        # Status validation
        valid_statuses = ['Operacional', 'Planejado', 'Parcial', '✅', '⚡', '🆕', '🔴']
        if metadata.status not in valid_statuses:
            self.warnings.append((
                metadata.agent_code,
                f"Unknown status: {metadata.status}"
            ))

        # Description length
        if len(metadata.description) < 10:
            self.warnings.append((
                metadata.agent_code,
                "Description is very short (< 10 chars)"
            ))

    def to_json(self, output_file: Optional[str] = None) -> str:
        """Convert agents to JSON format"""
        agents_dict = {
            code: asdict(metadata)
            for code, metadata in self.agents.items()
        }
        json_str = json.dumps(agents_dict, indent=2, ensure_ascii=False)

        if output_file:
            Path(output_file).write_text(json_str, encoding='utf-8')
            logger.info(f"Metadata saved to {output_file}")

        return json_str

    def validate(self, strict: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """Validate all extracted metadata"""
        validation_result = {
            'valid': True,
            'agents_count': len(self.agents),
            'errors': self.errors,
            'warnings': self.warnings,
            'missing_fields': {}
        }

        # Check for missing required fields per agent
        required_fields = {'agent_code', 'agent_name', 'tier', 'status'}
        for code, metadata in self.agents.items():
            meta_dict = asdict(metadata)
            missing = [f for f in required_fields if not meta_dict.get(f)]
            if missing:
                validation_result['missing_fields'][code] = missing
                validation_result['valid'] = False

        if self.errors:
            validation_result['valid'] = False

        if strict and self.warnings:
            validation_result['valid'] = False

        return validation_result['valid'], validation_result

    def report(self) -> str:
        """Generate extraction report"""
        valid, report = self.validate()
        lines = [
            "=" * 60,
            "AGENT METADATA EXTRACTION REPORT",
            "=" * 60,
            f"Timestamp: {datetime.now().isoformat()}",
            f"Agents extracted: {len(self.agents)}",
            f"Errors: {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
            f"Overall status: {'✓ VALID' if valid else '✗ INVALID'}",
            "",
        ]

        if self.agents:
            lines.extend(["AGENTS:", ""])
            for code, meta in sorted(self.agents.items()):
                lines.append(f"  {code:20} | {meta.agent_name:25} | {meta.tier:12} | {meta.status}")
            lines.append("")

        if self.errors:
            lines.extend(["ERRORS:", ""])
            for file, error in self.errors:
                lines.append(f"  {file}: {error}")
            lines.append("")

        if self.warnings:
            lines.extend(["WARNINGS:", ""])
            for file, warning in self.warnings:
                lines.append(f"  {file}: {warning}")
            lines.append("")

        return "\n".join(lines)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract and validate agent metadata for AskCAD sync'
    )
    parser.add_argument(
        '--agents-dir',
        default='.claude/agents',
        help='Directory containing agent markdown files'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate extracted metadata'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print extraction report'
    )

    args = parser.parse_args()

    # Extract metadata
    extractor = AgentMetadataExtractor(args.agents_dir)
    agents = extractor.extract_all(strict=args.strict)

    if args.output:
        extractor.to_json(args.output)

    if args.validate:
        valid, report = extractor.validate(strict=args.strict)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0 if valid else 1)

    if args.report:
        print(extractor.report())
        sys.exit(0)

    # Default: print JSON to stdout
    print(extractor.to_json())


if __name__ == '__main__':
    main()
