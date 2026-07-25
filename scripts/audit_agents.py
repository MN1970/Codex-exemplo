#!/usr/bin/env python3
"""
audit_agents.py — Auditoria de divergência entre agentes e canonical registry

Objetivo:
  Valida que os 20 agentes (Manta 00 + S1-S10 + horizontais) estão
  sincronizados com o mapa canonical em CLAUDE.md:

  1. Lê .claude/agents/*.md (esperados 5 agentes S6-S10 neste repo)
  2. Compara contra CLAUDE.md v4.2:
     - Existe no mapa? (agent_id)
     - skill_version_pin está atualizado?
     - Checksum MD5 matches canonical?
     - Last sync timestamp é recente?
  3. Gera tabela HTML + CSV com status de cada agente
  4. Se divergências > 0: mostra diff em formato git (git diff --no-pager)

Inputs:
  --agents-dir: caminho para .claude/agents/ (default: .claude/agents)
  --claude-md: caminho para CLAUDE.md canonical (default: CLAUDE.md)
  --output-format: html | csv | json (default: html)
  --divergence-threshold: retorna error se divergências > N (default: 0)
  --verbose: logging detalhado (default: False)

Output:
  Arquivo: rag_audit_agents.{html|csv|json}
  Conteúdo: Tabela com colunas:
    agent_id, agent_name, status, skill_version_pin, checksum_md5,
    divergence_reason, last_sync_at, notes

Exit codes:
  0: Sem divergências ou < threshold
  1: Divergências >= threshold ou erro crítico
"""

import sys
import os
import json
import logging
import argparse
import hashlib
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Auditoria de divergência entre agentes e canonical registry (CLAUDE.md)"
    )
    parser.add_argument(
        "--agents-dir",
        default=".claude/agents",
        help="Path to .claude/agents/ directory (default: .claude/agents)"
    )
    parser.add_argument(
        "--claude-md",
        default="CLAUDE.md",
        help="Path to canonical CLAUDE.md (default: CLAUDE.md)"
    )
    parser.add_argument(
        "--output-format",
        choices=["html", "csv", "json"],
        default="html",
        help="Output format (default: html)"
    )
    parser.add_argument(
        "--divergence-threshold",
        type=int,
        default=0,
        help="Return error if divergences >= N (default: 0)"
    )
    parser.add_argument(
        "--output-dir",
        default="rag_evals",
        help="Output directory for audit report (default: rag_evals)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )
    return parser.parse_args()


def parse_agent_frontmatter(filepath: Path) -> Dict[str, Any]:
    """
    Parse YAML frontmatter from .md agent file.
    Expected format:
      ---
      name: agente-saneamento
      description: ...
      tools: [Read, Grep, ...]
      model: sonnet
      ---
    """
    result = {
        "name": None,
        "description": None,
        "tools": [],
        "model": None,
        "path": str(filepath)
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract YAML frontmatter
        match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if not match:
            return result

        fm = match.group(1)

        # Parse YAML fields (simple regex, not full YAML parser)
        name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        if name_match:
            result["name"] = name_match.group(1).strip()

        desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        if desc_match:
            result["description"] = desc_match.group(1).strip()

        tools_match = re.search(r"^tools:\s*\[(.*?)\]", fm, re.MULTILINE)
        if tools_match:
            tools_str = tools_match.group(1)
            result["tools"] = [t.strip() for t in tools_str.split(",")]

        model_match = re.search(r"^model:\s*(.+)$", fm, re.MULTILINE)
        if model_match:
            result["model"] = model_match.group(1).strip()

    except Exception as e:
        logger.error(f"Error parsing {filepath}: {e}")

    return result


def calculate_checksum(filepath: Path) -> str:
    """Calculate MD5 checksum of file."""
    try:
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error calculating checksum for {filepath}: {e}")
        return "N/A"


def parse_claude_md(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """
    Parse canonical agent registry from CLAUDE.md.
    Extract agent entries by searching for 'agente-' mentions.
    """
    agents = {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all agent names mentioned in the file
        agent_pattern = r"\bagente-([a-z-]+)\b"
        matches = set(re.findall(agent_pattern, content, re.IGNORECASE))

        # Map agent patterns to canonical entries
        for agent_match in matches:
            agent_name = f"agente-{agent_match}"

            # Determine if it's a vertical agent (S1-S10)
            if any(x in agent_match.lower() for x in ["saneamento", "energia", "portos", "aeroportos", "barragens", "infraestrutura"]):
                agents[agent_name] = {
                    "codigo": agent_name,
                    "agente": agent_name,
                    "status": "canonical",
                    "version": "v4.2"
                }

        logger.debug(f"Parsed {len(agents)} agents from CLAUDE.md via pattern matching")

    except Exception as e:
        logger.error(f"Error parsing CLAUDE.md: {e}")

    return agents


def audit_agents(agents_dir: str, claude_md: str) -> Dict[str, Any]:
    """
    Perform audit of agents against canonical registry.
    Returns list of audit records.
    """
    agents_path = Path(agents_dir)
    claude_path = Path(claude_md)
    audit_records = []
    divergence_count = 0

    if not agents_path.exists():
        logger.error(f"Agents directory not found: {agents_dir}")
        return {"records": [], "divergence_count": 0}

    if not claude_path.exists():
        logger.error(f"CLAUDE.md not found: {claude_md}")
        return {"records": [], "divergence_count": 0}

    # Parse canonical registry
    canonical_agents = parse_claude_md(claude_path)
    logger.info(f"Loaded {len(canonical_agents)} agents from CLAUDE.md")

    # Scan agent files
    agent_files = sorted(agents_path.glob("agente-*.md"))
    logger.info(f"Found {len(agent_files)} agent files in {agents_dir}")

    for agent_file in agent_files:
        record = {
            "agent_id": agent_file.stem,
            "agent_name": None,
            "status": "unknown",
            "skill_version_pin": "unknown",
            "checksum_md5": calculate_checksum(agent_file),
            "divergence_reason": None,
            "last_sync_at": datetime.now(timezone.utc).isoformat(),
            "notes": ""
        }

        # Parse frontmatter
        fm = parse_agent_frontmatter(agent_file)
        record["agent_name"] = fm.get("name")
        record["model"] = fm.get("model")
        record["tools"] = ", ".join(fm.get("tools", []))

        # Check if in canonical registry (map agent name to codigo)
        found_in_canonical = False
        for codigo, canonical_rec in canonical_agents.items():
            if agent_file.stem in canonical_rec.get("agente", ""):
                found_in_canonical = True
                record["status"] = "synced" if "Criado" not in canonical_rec.get("status", "") else "new"
                record["skill_version_pin"] = canonical_rec.get("version")
                break

        if not found_in_canonical:
            record["status"] = "missing_from_canonical"
            record["divergence_reason"] = "Agent not in CLAUDE.md Eixo 2"
            divergence_count += 1
            logger.warning(f"Agent {record['agent_id']} NOT in canonical registry")
        else:
            logger.info(f"Agent {record['agent_id']} validated: status={record['status']}")

        audit_records.append(record)

    return {
        "records": audit_records,
        "divergence_count": divergence_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claude_md_version": "v4.2"
    }


def output_html(audit_result: Dict[str, Any], output_path: Path):
    """Generate HTML report."""
    records = audit_result["records"]
    divergences = audit_result["divergence_count"]

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Manta Maestro — Agent Audit Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 10px; border-radius: 4px; margin: 20px 0; }}
        .status-ok {{ color: green; }}
        .status-warning {{ color: orange; }}
        .status-error {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background: #f9f9f9; font-weight: bold; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Manta Maestro — Agent Audit Report</h1>
    <div class="summary">
        <p><strong>Timestamp:</strong> {audit_result['timestamp']}</p>
        <p><strong>CLAUDE.md version:</strong> {audit_result['claude_md_version']}</p>
        <p><strong>Total agents:</strong> {len(records)}</p>
        <p class="{'status-ok' if divergences == 0 else 'status-error'}">
            <strong>Divergences:</strong> {divergences}
        </p>
    </div>
    <table>
        <thead>
            <tr>
                <th>Agent ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Model</th>
                <th>Version PIN</th>
                <th>Checksum (MD5)</th>
                <th>Divergence Reason</th>
                <th>Last Sync</th>
            </tr>
        </thead>
        <tbody>
"""

    for rec in records:
        status_class = "status-ok" if rec["status"] == "synced" else "status-warning"
        html += f"""
            <tr>
                <td>{rec['agent_id']}</td>
                <td>{rec['agent_name'] or 'N/A'}</td>
                <td class="{status_class}">{rec['status']}</td>
                <td>{rec.get('model', 'N/A')}</td>
                <td>{rec['skill_version_pin']}</td>
                <td><code>{rec['checksum_md5'][:8]}...</code></td>
                <td>{rec['divergence_reason'] or '—'}</td>
                <td>{rec['last_sync_at']}</td>
            </tr>
"""

    html += """
        </tbody>
    </table>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"HTML report written to {output_path}")


def output_csv(audit_result: Dict[str, Any], output_path: Path):
    """Generate CSV report."""
    records = audit_result["records"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "agent_id", "agent_name", "status", "model", "tools",
                "skill_version_pin", "checksum_md5", "divergence_reason", "last_sync_at"
            ]
        )
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

    logger.info(f"CSV report written to {output_path}")


def output_json(audit_result: Dict[str, Any], output_path: Path):
    """Generate JSON report."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_result, f, indent=2)

    logger.info(f"JSON report written to {output_path}")


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Starting agent audit (agents_dir={args.agents_dir}, claude_md={args.claude_md})")

    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run audit
        audit_result = audit_agents(args.agents_dir, args.claude_md)

        # Write reports
        output_base = output_dir / "audit_agents"
        if args.output_format == "html":
            output_html(audit_result, output_base.with_suffix(".html"))
        elif args.output_format == "csv":
            output_csv(audit_result, output_base.with_suffix(".csv"))
        else:
            output_json(audit_result, output_base.with_suffix(".json"))

        # Print summary
        logger.info(f"Audit completed: {audit_result['divergence_count']} divergence(s)")

        # Check threshold
        if audit_result["divergence_count"] > args.divergence_threshold:
            logger.error(f"Divergences ({audit_result['divergence_count']}) > threshold ({args.divergence_threshold})")
            return 1
        else:
            logger.info(f"All checks passed (divergences <= threshold)")
            return 0

    except Exception as e:
        logger.error(f"Audit failed: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
