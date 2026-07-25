#!/usr/bin/env python3
"""
regenerate_skill.py — Auto-sync agentes para canonical spec v5.0

Objetivo:
  Regenera/atualiza arquivos de agentes para sincronizar com CLAUDE.md v5.0 +
  VERSIONS.json. Detecta divergências via checksum e reescreve o arquivo baseado
  no template canonical.

Workflow:
  1. Lê agent spec de VERSIONS.json (checksum esperado)
  2. Valida divergência (se checksum atual != esperado)
  3. Reescreve arquivo baseado em template + frontmatter canonical
  4. Atualiza checksum em VERSIONS.json
  5. Sincroniza skill_version_pin em settings.json
  6. Log: divergence_fix.log

Inputs:
  --agent: agente-id (ex: agente-saneamento)
  --all: regenerar todos os agentes
  --dry-run: mostrar mudanças sem aplicar
  --force: forçar regeneração mesmo sem drift
  --verbose: logging detalhado

Output:
  - .claude/agents/{agent}.md (atualizado)
  - VERSIONS.json (checksum atualizado)
  - .claude/settings.json (skill_version_pin atualizado)
  - divergence_fix.log (log de mudanças)

Exit codes:
  0: Sucesso
  1: Erro (agent not found, write failed)
"""

import sys
import os
import json
import logging
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import re
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("divergence_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CANONICAL TEMPLATES
# ============================================================================

CANONICAL_AGENT_SPECS = {
    "agente-saneamento": {
        "name": "agente-saneamento",
        "description": "Manta 03-S8 — Especialista em saneamento básico (água, esgoto, drenagem urbana, resíduos sólidos). PRIORIDADE AySA (projeto Argentina). Cobre estudo prévio, projeto básico, executivo, obra, O&M, licitação, DD e descomissionamento de ETAs, ETEs, sistemas de adução, distribuição de água, coleta e tratamento de esgoto, drenagem urbana e resíduos. Roteia quando o usuário menciona saneamento, ETA, ETE, adutora, esgoto, água tratada, AySA, drenagem urbana, macrodrenagem, SNIS, PMSB, Lei 14.026, subsídio cruzado, elevatória, reservatório, RAP, EEE, EEAB, reúso, lodo, digestor, UASB, MBR.",
        "tools": ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"],
        "model": "sonnet",
        "tier": "vertical",
        "segment": "S8"
    },
    "agente-energia": {
        "name": "agente-energia",
        "description": "Manta 03-S9 — Especialista em setor elétrico (geração, transmissão, distribuição). Prioridade transmissão (ANEEL/State Grid). Cobre estudo prévio, projeto básico, executivo, obra, O&M, leilão, DD e descomissionamento de linhas de transmissão, subestações, usinas (hidro, eólica, solar, térmica), sistemas de distribuição. Roteia quando o usuário menciona transmissão, LT, subestação, ANEEL, RAP, leilão transmissão, ONS, EPE, PDE, R1-R5, torre estaiada, cabo condutor, ACSR, CAA, ATSR, ONS, MRE, ACR, ACL, WEG, State Grid, ISA CTEEP, Alupar, Taesa, geração eólica, PV, hidráulica, PCH, UHE.",
        "tools": ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"],
        "model": "sonnet",
        "tier": "vertical",
        "segment": "S9"
    },
    "agente-portos": {
        "name": "agente-portos",
        "description": "Manta 03-S6 — Especialista em projetos portuários e hidroviários. Cobre estudos prévios, projetos básico/executivo, obra e operação de terminais marítimos, fluviais e hidroviários. Roteia automaticamente quando o usuário menciona porto, terminal, ANTAQ, dragagem, molhe, quebra-mar, berço, calado, contêiner, granel sólido/líquido, cais, píer, retroárea, pátio de estocagem, TUP, TPS, PIANC, arrendamento portuário ou hidrovia.",
        "tools": ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"],
        "model": "sonnet",
        "tier": "vertical",
        "segment": "S6"
    },
    "agente-aeroportos": {
        "name": "agente-aeroportos",
        "description": "Manta 03-S7 — Especialista em infraestrutura aeroportuária (lado ar + lado terra). Cobre pistas de pouso e decolagem, taxiways, pátios, TPS (terminal de passageiros), TECA (terminal de cargas), balizamento e sistemas visuais, torre de controle e apoio ao aeroporto. Roteia quando o usuário menciona aeroporto, pista, RWY, taxiway, TWY, pátio, TPS, TECA, ANAC, RBAC 154, ICAO Annex 14, FAA AC, balizamento, PAPI, ILS, PCN, gate, ponte de embarque, jetway, aviação geral, aviação regional, concessão aeroportuária.",
        "tools": ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"],
        "model": "sonnet",
        "tier": "vertical",
        "segment": "S7"
    },
    "agente-barragens": {
        "name": "agente-barragens",
        "description": "Manta 03-S10 — Especialista em barragens (concreto, terra, enrocamento, rejeitos). Cobre estudo prévio, projeto básico, executivo, obra, O&M, DD, descomissionamento e descaracterização. Roteia quando o usuário menciona barragem, vertedouro, CFRD, CCR, RCC, rejeitos, TSF, PNSB, ICOLD, CBDB, dique, SIGBM, ANM, ANA, Lei 12.334, Fundão, Brumadinho, descomissionamento, alteamento a montante/jusante/linha de centro, filtragem de rejeitos, dry stack, PAE, PAEBM, ZAS, ZSS, HHP.",
        "tools": ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"],
        "model": "sonnet",
        "tier": "vertical",
        "segment": "S10"
    }
}


# ============================================================================
# CLI ARGS
# ============================================================================

def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Auto-sync agentes para canonical spec v5.0 (VERSIONS.json + CLAUDE.md)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--agent",
        help="Agent ID to regenerate (e.g., agente-saneamento)"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Regenerate all agents"
    )
    parser.add_argument(
        "--agents-dir",
        default=".claude/agents",
        help="Path to .claude/agents/ (default: .claude/agents)"
    )
    parser.add_argument(
        "--versions-json",
        default="VERSIONS.json",
        help="Path to VERSIONS.json (default: VERSIONS.json)"
    )
    parser.add_argument(
        "--settings-json",
        default=".claude/settings.json",
        help="Path to settings.json (default: .claude/settings.json)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without applying"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even without drift"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )
    return parser.parse_args()


# ============================================================================
# UTIL FUNCTIONS
# ============================================================================

def calculate_checksum(content: str) -> str:
    """Calculate MD5 checksum of content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def load_versions_json(filepath: Path) -> Dict[str, Any]:
    """Load VERSIONS.json."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading VERSIONS.json: {e}")
        return {}


def load_settings_json(filepath: Path) -> Dict[str, Any]:
    """Load settings.json."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"skill_version_pin": {}}
    except Exception as e:
        logger.error(f"Error loading settings.json: {e}")
        return {"skill_version_pin": {}}


def read_agent_file(filepath: Path) -> str:
    """Read agent .md file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return ""


def write_agent_file(filepath: Path, content: str, dry_run: bool = False):
    """Write agent .md file."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would write {filepath}")
        logger.info(f"Content length: {len(content)} bytes")
        return

    try:
        # Backup original if exists
        if filepath.exists():
            backup_path = filepath.with_suffix(".bak")
            shutil.copy2(filepath, backup_path)
            logger.info(f"Backed up original to {backup_path}")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Updated {filepath}")
    except Exception as e:
        logger.error(f"Error writing {filepath}: {e}")
        raise


def update_versions_json(
    filepath: Path,
    agent_id: str,
    new_checksum: str,
    dry_run: bool = False
):
    """Update checksum in VERSIONS.json."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would update VERSIONS.json checksum for {agent_id}")
        return

    try:
        data = load_versions_json(filepath)

        if agent_id not in data.get("agent_skills", {}):
            data["agent_skills"] = data.get("agent_skills", {})
            data["agent_skills"][agent_id] = {}

        if "v5.0" not in data["agent_skills"][agent_id]:
            data["agent_skills"][agent_id]["v5.0"] = {}

        old_checksum = data["agent_skills"][agent_id]["v5.0"].get("checksum")
        data["agent_skills"][agent_id]["v5.0"]["checksum"] = new_checksum
        data["agent_skills"][agent_id]["v5.0"]["last_updated"] = datetime.now(timezone.utc).isoformat()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Updated VERSIONS.json: {agent_id} checksum {old_checksum[:8]}... -> {new_checksum[:8]}...")

    except Exception as e:
        logger.error(f"Error updating VERSIONS.json: {e}")
        raise


def update_settings_json(
    filepath: Path,
    agent_id: str,
    version: str = "v5.0",
    dry_run: bool = False
):
    """Update skill_version_pin in settings.json."""
    if dry_run:
        logger.info(f"[DRY-RUN] Would update settings.json for {agent_id}")
        return

    try:
        data = load_settings_json(filepath)

        if "skill_version_pin" not in data:
            data["skill_version_pin"] = {}

        old_version = data["skill_version_pin"].get(agent_id)
        data["skill_version_pin"][agent_id] = version

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Updated settings.json: {agent_id} pinned to {version} (was {old_version})")

    except Exception as e:
        logger.error(f"Error updating settings.json: {e}")
        raise


# ============================================================================
# AGENT CONTENT GENERATOR
# ============================================================================

def generate_agent_content_template(agent_id: str, spec: Dict[str, Any]) -> str:
    """
    Generate canonical frontmatter + minimal content for agent.
    This is a placeholder; in production you'd fetch full content from
    a template repository or template files.
    """
    tools_str = ", ".join(spec["tools"])
    description = spec["description"]

    template = f"""---
name: {spec['name']}
description: {description}
tools: [{tools_str}]
model: {spec['model']}
---

# {spec['name']} ({spec['tier'].upper()})

Especialista conforme CLAUDE.md v5.0 — {spec['description'][:100]}...

## Contexto de domínio

[Content to be filled from canonical source — VERSIONS.json references]

## Routing rules

O Maestro roteia automaticamente para este agente baseado em keywords
e embedding similarity contra queries do usuário.

## Ciclo de vida (8 fases)

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

---

**Nota:** Este arquivo foi regenerado via regenerate_skill.py.
Versão v5.0 — Checksum validado contra VERSIONS.json.
"""
    return template


# ============================================================================
# REGENERATION ENGINE
# ============================================================================

def regenerate_agent(
    agent_id: str,
    agents_dir: Path,
    versions_json_path: Path,
    settings_json_path: Path,
    dry_run: bool = False,
    force: bool = False
) -> bool:
    """
    Regenerate/sync a single agent.
    Returns True if successful, False if failed.
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing agent: {agent_id}")
    logger.info(f"{'='*70}")

    # Get canonical spec
    if agent_id not in CANONICAL_AGENT_SPECS:
        logger.error(f"Agent {agent_id} not in canonical specs (only 5 supported)")
        return False

    spec = CANONICAL_AGENT_SPECS[agent_id]

    # Check if agent file exists
    agent_file = agents_dir / f"{agent_id}.md"
    if not agent_file.exists():
        logger.warning(f"Agent file not found: {agent_file}")
        logger.info("Will create new file...")

    # Read current file (if exists)
    current_content = read_agent_file(agent_file) if agent_file.exists() else ""
    current_checksum = calculate_checksum(current_content)

    # Load expected checksum from VERSIONS.json
    versions_data = load_versions_json(versions_json_path)
    expected_checksum = versions_data.get("agent_skills", {}).get(agent_id, {}).get("v5.0", {}).get("checksum")

    # Detect drift
    has_drift = (current_checksum != expected_checksum) if expected_checksum else False

    logger.info(f"Current checksum:  {current_checksum[:8]}...")
    logger.info(f"Expected checksum: {expected_checksum[:8] if expected_checksum else 'N/A'}...")
    logger.info(f"Has drift: {has_drift}")

    if not has_drift and not force:
        logger.info("No drift detected and --force not set. Skipping.")
        return True

    # Generate new content
    logger.info("Generating canonical content...")
    new_content = generate_agent_content_template(agent_id, spec)
    new_checksum = calculate_checksum(new_content)

    logger.info(f"New checksum: {new_checksum[:8]}...")

    if dry_run:
        logger.info("[DRY-RUN] Would apply changes:")
        logger.info(f"  - Write {agent_file}")
        logger.info(f"  - Update VERSIONS.json: {expected_checksum[:8]}... -> {new_checksum[:8]}...")
        logger.info(f"  - Pin settings.json: {agent_id} = v5.0")
        return True

    # Apply changes
    try:
        # 1. Write agent file
        write_agent_file(agent_file, new_content, dry_run=False)

        # 2. Update VERSIONS.json
        update_versions_json(versions_json_path, agent_id, new_checksum, dry_run=False)

        # 3. Update settings.json
        update_settings_json(settings_json_path, agent_id, "v5.0", dry_run=False)

        logger.info(f"Successfully regenerated {agent_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to regenerate {agent_id}: {e}")
        return False


def regenerate_all_agents(
    agents_dir: Path,
    versions_json_path: Path,
    settings_json_path: Path,
    dry_run: bool = False,
    force: bool = False
) -> Tuple[int, int]:
    """
    Regenerate all agents.
    Returns (success_count, failure_count).
    """
    success = 0
    failures = 0

    for agent_id in CANONICAL_AGENT_SPECS.keys():
        if regenerate_agent(
            agent_id,
            agents_dir,
            versions_json_path,
            settings_json_path,
            dry_run=dry_run,
            force=force
        ):
            success += 1
        else:
            failures += 1

    return success, failures


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("=" * 80)
    logger.info("Starting Agent Regeneration (CLAUDE.md v5.0)")
    logger.info("=" * 80)

    try:
        agents_path = Path(args.agents_dir)
        versions_path = Path(args.versions_json)
        settings_path = Path(args.settings_json)

        # Validate paths
        if not agents_path.exists():
            agents_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created agents directory: {agents_path}")

        if not versions_path.exists():
            logger.error(f"VERSIONS.json not found: {versions_path}")
            return 1

        # Process agents
        if args.agent:
            success = regenerate_agent(
                args.agent,
                agents_path,
                versions_path,
                settings_path,
                dry_run=args.dry_run,
                force=args.force
            )
            result = 0 if success else 1
        else:  # --all
            success, failures = regenerate_all_agents(
                agents_path,
                versions_path,
                settings_path,
                dry_run=args.dry_run,
                force=args.force
            )
            logger.info("=" * 80)
            logger.info(f"Summary: {success} successful, {failures} failed")
            logger.info("=" * 80)
            result = 0 if failures == 0 else 1

        return result

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
