#!/usr/bin/env python3
"""
audit_agents.py v2 — Auditoria de drift entre agentes e canonical registry v5.0

Objetivo:
  Valida que os agentes em .claude/agents/ estão sincronizados com o mapa
  canonical em CLAUDE.md v5.0 + VERSIONS.json:

  1. Lê .claude/agents/*.md (5 agentes S6-S10 esperados neste repo)
  2. Compara contra CLAUDE.md v5.0 + VERSIONS.json:
     - Existe no mapa de 20 agentes?
     - Checksum MD5 matches canonical?
     - Frontmatter (model, tools) está atualizado?
     - skill_version_pin está correto em settings.json?
  3. Detecta DRIFT: divergências entre arquivo e spec
  4. Gera relatórios: JSON (CI), HTML (humans), CSV (dados)
  5. Output divergence_report.json com remediação sugerida

Inputs (CLI):
  --agents-dir: .claude/agents/ (default: .claude/agents)
  --claude-md: CLAUDE.md canonical (default: CLAUDE.md)
  --versions-json: VERSIONS.json (default: VERSIONS.json)
  --settings-json: settings.json com skill pins (default: .claude/settings.json)
  --output-format: html | csv | json (default: json)
  --output-dir: diretório de saída (default: rag_evals)
  --divergence-threshold: fail se divergências >= N (default: 0)
  --slack-webhook: URL Slack para alertas (optional)
  --verbose: logging detalhado (default: False)

Output:
  - audit_agents.{json,html,csv}: Relatório estruturado
  - divergence_report.json: Detalhes de drift + remediação
  - audit.log: Log detalhado

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
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
import traceback
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("audit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS
# ============================================================================

CANONICAL_20_AGENTS = {
    # Tier 1 — Horizontais (11)
    "maestro": {"codigo": "Manta 00", "tier": "horizontal", "version": "v5.0"},
    "agente-claims": {"codigo": "Manta 01", "tier": "horizontal", "version": "v5.0"},
    "agente-contratual": {"codigo": "Manta 02", "tier": "horizontal", "version": "v5.0"},
    "agente-imobiliario": {"codigo": "Manta 04", "tier": "horizontal", "version": "v5.0"},
    "agente-orcamento": {"codigo": "Manta 05", "tier": "horizontal", "version": "v5.0"},
    "agente-modelagem": {"codigo": "Manta 06", "tier": "horizontal", "version": "v5.0"},
    "agente-cronograma": {"codigo": "Manta 07", "tier": "horizontal", "version": "v5.0"},
    "agente-bd": {"codigo": "Manta 13", "tier": "horizontal", "version": "v5.0"},
    "agente-apresentacoes": {"codigo": "Manta 14", "tier": "horizontal", "version": "v5.0"},
    "agente-advisory": {"codigo": "Manta 15", "tier": "horizontal", "version": "v5.0"},
    "agente-arquiteto-ia": {"codigo": "Manta 16", "tier": "horizontal", "version": "v5.0"},
    # Tier 2–3 — Verticais (9: S1-S4, S6-S10)
    "agente-rodovias": {"codigo": "Manta 03-S1", "tier": "vertical", "segment": "S1", "version": "v5.0"},
    "agente-oae": {"codigo": "Manta 03-S2", "tier": "vertical", "segment": "S2", "version": "v5.0"},
    "agente-ferrovia": {"codigo": "Manta 03-S3", "tier": "vertical", "segment": "S3", "version": "v5.0"},
    "agente-metro": {"codigo": "Manta 03-S4", "tier": "vertical", "segment": "S4", "version": "v5.0"},
    "agente-portos": {"codigo": "Manta 03-S6", "tier": "vertical", "segment": "S6", "version": "v5.0"},
    "agente-aeroportos": {"codigo": "Manta 03-S7", "tier": "vertical", "segment": "S7", "version": "v5.0"},
    "agente-saneamento": {"codigo": "Manta 03-S8", "tier": "vertical", "segment": "S8", "version": "v5.0"},
    "agente-energia": {"codigo": "Manta 03-S9", "tier": "vertical", "segment": "S9", "version": "v5.0"},
    "agente-barragens": {"codigo": "Manta 03-S10", "tier": "vertical", "segment": "S10", "version": "v5.0"},
}


# ============================================================================
# CLI ARGS
# ============================================================================

def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Auditoria v2: Detecta drift entre agentes e canonical registry (CLAUDE.md + VERSIONS.json)"
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
        "--versions-json",
        default="VERSIONS.json",
        help="Path to VERSIONS.json (default: VERSIONS.json)"
    )
    parser.add_argument(
        "--settings-json",
        default=".claude/settings.json",
        help="Path to settings.json with skill pins (default: .claude/settings.json)"
    )
    parser.add_argument(
        "--output-format",
        choices=["html", "csv", "json"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--output-dir",
        default="rag_evals",
        help="Output directory for audit reports (default: rag_evals)"
    )
    parser.add_argument(
        "--divergence-threshold",
        type=int,
        default=0,
        help="Fail if divergences >= N (default: 0)"
    )
    parser.add_argument(
        "--slack-webhook",
        help="Slack webhook URL for alerts (optional)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )
    return parser.parse_args()


# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

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
            logger.warning(f"No frontmatter found in {filepath}")
            return result

        fm = match.group(1)

        # Parse YAML fields
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
        return "ERROR"


def load_versions_json(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Load and parse VERSIONS.json."""
    try:
        if not filepath.exists():
            logger.warning(f"VERSIONS.json not found at {filepath}")
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading VERSIONS.json: {e}")
        return {}


def load_settings_json(filepath: Path) -> Dict[str, Any]:
    """Load settings.json with skill pins."""
    try:
        if not filepath.exists():
            logger.warning(f"settings.json not found at {filepath}")
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading settings.json: {e}")
        return {}


def parse_claude_md_agents(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """
    Extract agent specs from CLAUDE.md v5.0 mapa de agentes.
    Looks for the agent mapping table.
    """
    agents = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract mapa table (between table headers)
        # Format: | Código | Agente | Aliases | Tier default | Skill v5.0 | Checksum | Status |
        pattern = r"\| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \| ([^\|]+) \|"

        for match in re.finditer(pattern, content):
            codigo = match.group(1).strip()
            agente = match.group(2).strip()
            aliases = match.group(3).strip()
            tier = match.group(4).strip()
            skill = match.group(5).strip()
            checksum = match.group(6).strip()
            status = match.group(7).strip()

            if agente.startswith("agente-") or agente.startswith("maestro"):
                agents[agente] = {
                    "codigo": codigo,
                    "aliases": aliases,
                    "tier": tier,
                    "skill_v5": skill,
                    "checksum": checksum,
                    "status": status
                }

        logger.info(f"Extracted {len(agents)} agents from CLAUDE.md mapa")

    except Exception as e:
        logger.error(f"Error parsing CLAUDE.md agents: {e}")

    return agents


# ============================================================================
# DRIFT DETECTION
# ============================================================================

def detect_drift(
    agent_id: str,
    agent_file: Path,
    frontmatter: Dict[str, Any],
    checksum_actual: str,
    versions_json: Dict[str, Any],
    settings_json: Dict[str, Any],
    claude_agents: Dict[str, Dict[str, Any]]
) -> Tuple[List[str], str]:
    """
    Detect divergences between agent file and canonical specs.
    Returns (list of divergence reasons, overall status).
    """
    divergences = []
    status = "synced"

    # Check 1: Is agent in canonical 20?
    if agent_id not in CANONICAL_20_AGENTS:
        divergences.append("NOT_IN_CANONICAL_20")
        status = "not_in_registry"
        return divergences, status

    # Check 2: Checksum validation against VERSIONS.json
    agent_versions = versions_json.get("agent_skills", {}).get(agent_id, {})
    v5_spec = agent_versions.get("v5.0", {})

    if v5_spec:
        expected_checksum = v5_spec.get("checksum", "")
        if expected_checksum and expected_checksum != checksum_actual:
            divergences.append(f"CHECKSUM_MISMATCH (expected={expected_checksum[:8]}, actual={checksum_actual[:8]})")
            status = "drift"
    else:
        divergences.append("NO_V5_SPEC_IN_VERSIONS_JSON")
        status = "missing_version"

    # Check 3: Frontmatter validation
    canonical_agent = CANONICAL_20_AGENTS.get(agent_id)
    if canonical_agent:
        tier = canonical_agent.get("tier")

        # Model should be "sonnet" for verticals, "haiku" or "sonnet" for horizontals
        if frontmatter.get("model"):
            expected_model = "sonnet"  # Default for most
            if frontmatter.get("model") != expected_model and tier == "vertical":
                divergences.append(f"MODEL_MISMATCH (expected={expected_model}, actual={frontmatter.get('model')})")
                status = "drift"

    # Check 4: Skill version pin in settings.json
    skill_pins = settings_json.get("skill_version_pin", {})
    if skill_pins:
        pinned_version = skill_pins.get(agent_id)
        if pinned_version and pinned_version != "v5.0":
            divergences.append(f"SKILL_PIN_MISMATCH (pinned={pinned_version}, expected=v5.0)")
            status = "drift"

    # Check 5: RAG collection (for verticals)
    if CANONICAL_20_AGENTS.get(agent_id, {}).get("tier") == "vertical":
        rag_expected = v5_spec.get("rag_collection")
        if not rag_expected:
            divergences.append("MISSING_RAG_COLLECTION_SPEC")
            status = "incomplete"

    return divergences, status


# ============================================================================
# AUDIT ENGINE
# ============================================================================

def audit_agents(
    agents_dir: str,
    claude_md: str,
    versions_json_path: str,
    settings_json_path: str
) -> Dict[str, Any]:
    """
    Perform comprehensive audit of agents against canonical specs.
    """
    agents_path = Path(agents_dir)
    claude_path = Path(claude_md)
    versions_path = Path(versions_json_path)
    settings_path = Path(settings_json_path)

    audit_records = []
    divergence_summary = {
        "total": 0,
        "synced": 0,
        "drift": 0,
        "not_in_registry": 0,
        "missing_version": 0,
        "incomplete": 0
    }

    # Load specs
    versions_data = load_versions_json(versions_path)
    settings_data = load_settings_json(settings_path)
    claude_agents = parse_claude_md_agents(claude_path)

    if not agents_path.exists():
        logger.error(f"Agents directory not found: {agents_dir}")
        return {
            "records": [],
            "divergence_summary": divergence_summary,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": f"Directory not found: {agents_dir}"
        }

    # Scan agent files
    agent_files = sorted(agents_path.glob("agente-*.md"))
    logger.info(f"Found {len(agent_files)} agent files in {agents_dir}")

    for agent_file in agent_files:
        agent_id = agent_file.stem
        checksum_actual = calculate_checksum(agent_file)
        frontmatter = parse_agent_frontmatter(agent_file)

        divergences, status = detect_drift(
            agent_id,
            agent_file,
            frontmatter,
            checksum_actual,
            versions_data,
            settings_data,
            claude_agents
        )

        record = {
            "agent_id": agent_id,
            "agent_name": frontmatter.get("name"),
            "status": status,
            "model": frontmatter.get("model"),
            "tools": ", ".join(frontmatter.get("tools", [])),
            "checksum_md5": checksum_actual,
            "canonical_checksum": versions_data.get("agent_skills", {}).get(agent_id, {}).get("v5.0", {}).get("checksum", "N/A"),
            "divergences": divergences,
            "num_divergences": len(divergences),
            "last_validated_at": datetime.now(timezone.utc).isoformat(),
            "remediation_suggest": f"Run: python scripts/regenerate_skill.py --agent {agent_id}" if divergences else None
        }

        audit_records.append(record)

        # Update summary
        divergence_summary["total"] += 1
        divergence_summary[status] = divergence_summary.get(status, 0) + 1
        if divergences:
            logger.warning(f"Agent {agent_id}: {len(divergences)} divergence(s) — {', '.join(divergences)}")
        else:
            logger.info(f"Agent {agent_id}: synced")

    return {
        "records": audit_records,
        "divergence_summary": divergence_summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "claude_md_version": "v5.0",
        "expected_agents": list(CANONICAL_20_AGENTS.keys()),
        "expected_count": 20
    }


# ============================================================================
# OUTPUT FORMATTERS
# ============================================================================

def output_json(audit_result: Dict[str, Any], output_path: Path):
    """Generate JSON report."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_result, f, indent=2)
    logger.info(f"JSON report written to {output_path}")


def output_html(audit_result: Dict[str, Any], output_path: Path):
    """Generate HTML report."""
    records = audit_result["records"]
    summary = audit_result["divergence_summary"]

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Manta Maestro — Agent Audit Report v5.0</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background: #1a1a1a; color: white; padding: 30px 20px; margin-bottom: 30px; border-radius: 8px; }}
        h1 {{ margin-bottom: 10px; }}
        .metadata {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .metadata-item {{ background: rgba(255,255,255,0.1); padding: 10px; border-radius: 4px; }}
        .metadata-item strong {{ display: block; font-size: 0.9em; color: #aaa; }}
        .metadata-item span {{ display: block; font-size: 1.1em; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 30px 0; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 8px; border-left: 4px solid; text-align: center; }}
        .summary-card.synced {{ border-left-color: #27ae60; }}
        .summary-card.drift {{ border-left-color: #e74c3c; }}
        .summary-card.warning {{ border-left-color: #f39c12; }}
        .summary-card .number {{ font-size: 2em; font-weight: bold; }}
        .summary-card .label {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
        .table-wrapper {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 30px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f9f9f9; padding: 15px; text-align: left; font-weight: 600; border-bottom: 2px solid #eee; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #eee; }}
        tr:last-child td {{ border-bottom: none; }}
        .status-synced {{ color: #27ae60; font-weight: 600; }}
        .status-drift {{ color: #e74c3c; font-weight: 600; }}
        .status-warning {{ color: #f39c12; font-weight: 600; }}
        .checksum {{ font-family: monospace; font-size: 0.85em; color: #666; }}
        .divergences {{ background: #fff3cd; padding: 8px 12px; border-radius: 4px; font-size: 0.9em; }}
        .divergence-item {{ margin: 4px 0; padding: 4px 0; }}
        .remediation {{ background: #d4edda; padding: 8px 12px; border-radius: 4px; font-size: 0.85em; font-family: monospace; color: #155724; }}
        footer {{ text-align: center; padding: 20px; color: #888; font-size: 0.9em; }}
    </style>
</head>
<body>
    <header>
        <h1>Manta Maestro — Agent Audit Report v5.0</h1>
        <div class="metadata">
            <div class="metadata-item">
                <strong>Report Generated</strong>
                <span>{audit_result['timestamp']}</span>
            </div>
            <div class="metadata-item">
                <strong>CLAUDE.md Version</strong>
                <span>{audit_result['claude_md_version']}</span>
            </div>
            <div class="metadata-item">
                <strong>Agents Scanned</strong>
                <span>{len(records)}/{audit_result['expected_count']}</span>
            </div>
        </div>
    </header>

    <div class="container">
        <h2>Audit Summary</h2>
        <div class="summary-grid">
            <div class="summary-card synced">
                <div class="number">{summary.get('synced', 0)}</div>
                <div class="label">Synced</div>
            </div>
            <div class="summary-card drift">
                <div class="number">{summary.get('drift', 0)}</div>
                <div class="label">Drift Detected</div>
            </div>
            <div class="summary-card warning">
                <div class="number">{summary.get('not_in_registry', 0)}</div>
                <div class="label">Not in Registry</div>
            </div>
            <div class="summary-card warning">
                <div class="number">{summary.get('missing_version', 0)}</div>
                <div class="label">Missing v5.0 Spec</div>
            </div>
        </div>

        <h2>Agent Details</h2>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Agent ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Model</th>
                        <th>Divergences</th>
                        <th>Checksum (MD5)</th>
                        <th>Remediation</th>
                    </tr>
                </thead>
                <tbody>
"""

    for rec in records:
        status_class = f"status-{rec['status']}"
        divergences_html = ""
        if rec["divergences"]:
            divergences_html = f"""<div class="divergences">
                {''.join(f'<div class="divergence-item">• {d}</div>' for d in rec['divergences'])}
            </div>"""

        remediation_html = ""
        if rec["remediation_suggest"]:
            remediation_html = f'<div class="remediation">{rec["remediation_suggest"]}</div>'

        html += f"""
                    <tr>
                        <td><code>{rec['agent_id']}</code></td>
                        <td>{rec['agent_name'] or 'N/A'}</td>
                        <td><span class="{status_class}">{rec['status']}</span></td>
                        <td>{rec.get('model', 'N/A')}</td>
                        <td>
                            {divergences_html}
                        </td>
                        <td><span class="checksum">{rec['checksum_md5'][:8]}...</span></td>
                        <td>{remediation_html}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
    </div>

    <footer>
        <p>Generated by audit_agents.py v2 — Manta Maestro Agent Registry v5.0</p>
    </footer>
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
                "checksum_md5", "canonical_checksum", "num_divergences",
                "divergences", "last_validated_at"
            ]
        )
        writer.writeheader()
        for rec in records:
            writer.writerow({
                "agent_id": rec["agent_id"],
                "agent_name": rec["agent_name"],
                "status": rec["status"],
                "model": rec["model"],
                "tools": rec["tools"],
                "checksum_md5": rec["checksum_md5"],
                "canonical_checksum": rec["canonical_checksum"],
                "num_divergences": rec["num_divergences"],
                "divergences": " | ".join(rec["divergences"]),
                "last_validated_at": rec["last_validated_at"]
            })

    logger.info(f"CSV report written to {output_path}")


# ============================================================================
# DIVERGENCE REPORT
# ============================================================================

def generate_divergence_report(audit_result: Dict[str, Any], output_path: Path):
    """
    Generate detailed divergence_report.json for CI consumption.
    Includes remediation suggestions and automated fix commands.
    """
    divergence_report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_agents_scanned": audit_result["divergence_summary"]["total"],
            "agents_with_drift": sum(1 for r in audit_result["records"] if r["divergences"]),
            "total_divergences": sum(r["num_divergences"] for r in audit_result["records"])
        },
        "divergences": [],
        "remediation": {
            "auto_sync_command": "python scripts/regenerate_skill.py --all --dry-run",
            "agents_to_fix": []
        }
    }

    for rec in audit_result["records"]:
        if rec["divergences"]:
            divergence_report["divergences"].append({
                "agent_id": rec["agent_id"],
                "status": rec["status"],
                "divergence_reasons": rec["divergences"],
                "checksum_actual": rec["checksum_md5"],
                "checksum_expected": rec["canonical_checksum"],
                "remediation_command": f"python scripts/regenerate_skill.py --agent {rec['agent_id']}"
            })
            divergence_report["remediation"]["agents_to_fix"].append({
                "agent_id": rec["agent_id"],
                "command": f"python scripts/regenerate_skill.py --agent {rec['agent_id']}"
            })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(divergence_report, f, indent=2)
    logger.info(f"Divergence report written to {output_path}")


# ============================================================================
# SLACK ALERTS
# ============================================================================

def send_slack_alert(webhook_url: str, audit_result: Dict[str, Any]):
    """Send audit summary to Slack webhook."""
    summary = audit_result["divergence_summary"]
    divergence_count = summary.get("drift", 0) + summary.get("not_in_registry", 0)

    if divergence_count == 0:
        color = "#27ae60"
        status = "PASS"
    else:
        color = "#e74c3c"
        status = "FAIL"

    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"Manta Maestro Agent Audit — {status}",
                "text": f"Audit Results v5.0 — {datetime.now(timezone.utc).isoformat()}",
                "fields": [
                    {"title": "Total Agents", "value": str(summary["total"]), "short": True},
                    {"title": "Synced", "value": str(summary["synced"]), "short": True},
                    {"title": "Drift Detected", "value": str(summary["drift"]), "short": True},
                    {"title": "Not in Registry", "value": str(summary["not_in_registry"]), "short": True},
                ]
            }
        ]
    }

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                logger.info("Slack alert sent successfully")
            else:
                logger.warning(f"Slack alert returned status {response.status}")
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("=" * 80)
    logger.info("Starting Agent Audit v2 (CLAUDE.md v5.0 + VERSIONS.json)")
    logger.info("=" * 80)

    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run audit
        audit_result = audit_agents(
            args.agents_dir,
            args.claude_md,
            args.versions_json,
            args.settings_json
        )

        # Generate reports
        output_base = output_dir / "audit_agents"
        output_json(audit_result, output_base.with_suffix(".json"))

        if args.output_format == "html":
            output_html(audit_result, output_base.with_suffix(".html"))
        elif args.output_format == "csv":
            output_csv(audit_result, output_base.with_suffix(".csv"))

        # Generate divergence report
        divergence_path = output_dir / "divergence_report.json"
        generate_divergence_report(audit_result, divergence_path)

        # Send Slack alert if configured
        if args.slack_webhook:
            send_slack_alert(args.slack_webhook, audit_result)

        # Print summary
        summary = audit_result["divergence_summary"]
        logger.info("=" * 80)
        logger.info(f"Audit completed at {audit_result['timestamp']}")
        logger.info(f"  Total agents: {summary['total']}")
        logger.info(f"  Synced: {summary['synced']}")
        logger.info(f"  Drift detected: {summary['drift']}")
        logger.info(f"  Not in registry: {summary['not_in_registry']}")
        logger.info(f"  Missing v5.0 spec: {summary['missing_version']}")
        logger.info(f"  Incomplete: {summary['incomplete']}")
        logger.info("=" * 80)

        # Check threshold
        total_divergences = (
            summary.get("drift", 0) +
            summary.get("not_in_registry", 0) +
            summary.get("missing_version", 0)
        )

        if total_divergences > args.divergence_threshold:
            logger.error(f"AUDIT FAILED: {total_divergences} divergence(s) > threshold {args.divergence_threshold}")
            logger.error(f"Review {divergence_path} for remediation steps")
            return 1
        else:
            logger.info(f"AUDIT PASSED: {total_divergences} divergence(s) <= threshold {args.divergence_threshold}")
            return 0

    except Exception as e:
        logger.error(f"Audit failed with exception: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
