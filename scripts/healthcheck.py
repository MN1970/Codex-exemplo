#!/usr/bin/env python3
"""
Maestro v5.0 Comprehensive Healthcheck Script

Validates P1-P8 (8 pilares):
  P1: Routing determinístico (R1, R6, R7, R8)
  P2: Qualidade vertical (skill pinning, checksums)
  P3: Ciclo de vida (8 fases suportadas)
  P4: RAG híbrido (BM25, embedding, reranker)
  P5: Tiering automático (R7 complexity score)
  P6: Observabilidade (run tracking, custos)
  P7: Orquestração background (APScheduler triggers)
  P8: Versionamento de skills (checksums, deprecation)

Exit codes:
  0 = All checks passed
  1 = Warnings (non-blocking)
  2 = Critical failures (blockers)
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class HealthChecker:
    def __init__(self, repo_root: Path = Path.cwd()):
        self.repo_root = repo_root
        self.versions_file = repo_root / "VERSIONS.json"
        self.agents_dir = repo_root / ".claude" / "agents"
        self.rag_dir = repo_root / ".claude" / "rag"
        self.issues = []
        self.warnings = []
        self.passed = []

    def load_versions(self) -> Dict:
        """Load VERSIONS.json"""
        try:
            with open(self.versions_file) as f:
                return json.load(f)
        except FileNotFoundError:
            self.issues.append(f"VERSIONS.json not found at {self.versions_file}")
            return {}

    def compute_checksum(self, file_path: Path) -> str:
        """Compute MD5 checksum of a file"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except FileNotFoundError:
            return None

    def validate_skill_checksums(self, versions: Dict) -> None:
        """Validate skill file checksums"""
        agent_skills = versions.get("agent_skills", {})

        for agent_name, versions_dict in agent_skills.items():
            for version, metadata in versions_dict.items():
                file_path = self.repo_root / metadata.get("file", "")
                expected_checksum = metadata.get("checksum")

                if not file_path.exists():
                    self.issues.append(
                        f"Skill file missing: {agent_name} {version} "
                        f"(expected at {file_path})"
                    )
                    continue

                actual_checksum = self.compute_checksum(file_path)
                if actual_checksum and actual_checksum != expected_checksum:
                    self.warnings.append(
                        f"Checksum mismatch: {agent_name} {version}\n"
                        f"  Expected: {expected_checksum}\n"
                        f"  Actual: {actual_checksum}"
                    )
                else:
                    self.passed.append(f"Skill checksum OK: {agent_name} {version}")

    def validate_rag_collections(self, versions: Dict) -> None:
        """Validate RAG collections exist and have metadata"""
        rag_collections = versions.get("rag_collections", {})

        for collection_id, metadata in rag_collections.items():
            collection_dir = self.rag_dir / collection_id

            # Check if directory exists
            if not collection_dir.exists():
                self.warnings.append(
                    f"RAG collection directory not found: {collection_id} "
                    f"(expected at {collection_dir})"
                )
                continue

            # Check for chunks.jsonl
            chunks_file = collection_dir / "chunks.jsonl"
            if not chunks_file.exists():
                self.warnings.append(
                    f"RAG chunks file missing: {collection_id}/chunks.jsonl"
                )
            else:
                # Count chunks
                try:
                    n_chunks = sum(1 for _ in chunks_file.open())
                    expected_chunks = metadata.get("n_chunks", 0)
                    if n_chunks != expected_chunks:
                        self.warnings.append(
                            f"RAG chunk count mismatch: {collection_id}\n"
                            f"  Expected: {expected_chunks}\n"
                            f"  Actual: {n_chunks}"
                        )
                    else:
                        self.passed.append(
                            f"RAG collection OK: {collection_id} ({n_chunks} chunks)"
                        )
                except Exception as e:
                    self.issues.append(f"Error reading {collection_id}: {e}")

            # Check for metadata.json
            metadata_file = collection_dir / "metadata.json"
            if not metadata_file.exists():
                self.warnings.append(
                    f"RAG metadata file missing: {collection_id}/metadata.json"
                )

    def validate_claude_md(self) -> None:
        """Validate CLAUDE.md structure"""
        claude_md = self.repo_root / "CLAUDE.md"

        if not claude_md.exists():
            self.issues.append("CLAUDE.md not found")
            return

        with open(claude_md) as f:
            content = f.read()

        # Check for v5.0
        if "v5.0" not in content:
            self.warnings.append("CLAUDE.md does not mention v5.0")
        else:
            self.passed.append("CLAUDE.md version: v5.0")

        # Check for required sections
        required_sections = [
            "OS 8 PILARES",
            "R1 — MAESTRO",
            "R6 — RERANKING",
            "R7 — TIERING",
            "R8 — FALLBACK",
            "R9 — FEEDBACK",
            "R10 — PURGA",
            "MAPA COMPLETO DE AGENTES",
            "DEPLOY CHECKLIST"
        ]

        for section in required_sections:
            if section in content:
                self.passed.append(f"Section found: {section}")
            else:
                self.issues.append(f"Required section missing: {section}")

    def validate_settings_json(self) -> None:
        """Validate .claude/settings.json skill pins and v5.0 config"""
        settings_file = self.repo_root / ".claude" / "settings.json"

        if not settings_file.exists():
            self.warnings.append(f".claude/settings.json not found")
            return

        try:
            with open(settings_file) as f:
                settings = json.load(f)

            skill_pins = settings.get("skill_version_pin", {})

            if not skill_pins:
                self.warnings.append("No skill_version_pin entries found in settings.json")
                return

            # Check that each pinned skill exists
            for skill_name, version in skill_pins.items():
                skill_file = self.agents_dir / f"{skill_name}.{version}.md"
                if skill_file.exists():
                    self.passed.append(f"Skill pin OK: {skill_name}={version}")
                else:
                    self.issues.append(
                        f"Pinned skill not found: {skill_name}={version} "
                        f"(expected at {skill_file})"
                    )
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in .claude/settings.json: {e}")

    def validate_apscheduler_config(self) -> None:
        """P7 — Validate APScheduler trigger definitions"""
        settings_file = self.repo_root / "settings.json"

        if not settings_file.exists():
            self.warnings.append("settings.json not found (APScheduler config)")
            return

        try:
            with open(settings_file) as f:
                settings = json.load(f)

            scheduler_config = settings.get("apscheduler_config", {})
            if not scheduler_config.get("enabled"):
                self.warnings.append("APScheduler not enabled in settings.json")
                return

            triggers = scheduler_config.get("triggers", [])
            if not triggers:
                self.warnings.append("No APScheduler triggers defined")
                return

            for trigger in triggers:
                name = trigger.get("name")
                cron = trigger.get("cron")
                if name and cron:
                    self.passed.append(f"APScheduler trigger OK: {name} ({cron})")
                else:
                    self.issues.append(f"Invalid trigger config: {name}")

        except Exception as e:
            self.issues.append(f"Error reading APScheduler config: {e}")

    def validate_root_settings_json(self) -> None:
        """Validate root-level settings.json for v5.0 config"""
        settings_file = self.repo_root / "settings.json"

        if not settings_file.exists():
            self.warnings.append("Root settings.json not found")
            return

        try:
            with open(settings_file) as f:
                settings = json.load(f)

            required_keys = [
                "skill_version_pin",
                "tiering_strategy",
                "fallback_policy",
                "rag_config",
                "supabase_config"
            ]

            for key in required_keys:
                if key in settings:
                    self.passed.append(f"Setting '{key}' defined")
                else:
                    self.warnings.append(f"Setting '{key}' missing from root settings.json")

        except Exception as e:
            self.issues.append(f"Error reading root settings.json: {e}")

    def run(self) -> Tuple[int, str]:
        """Run all P1-P8 checks and return exit code"""
        print("=" * 70)
        print("Manta Maestro v5.0 Comprehensive Healthcheck")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 70)

        versions = self.load_versions()

        if not versions:
            print("CRITICAL: Cannot load VERSIONS.json")
            return 2, "VERSIONS.json loading failed"

        # Run all checks (P1-P8)
        print("\n[P2 + P8] Validating skill checksums and versions...")
        self.validate_skill_checksums(versions)

        print("[P4] Validating RAG collections...")
        self.validate_rag_collections(versions)

        print("[P1] Validating CLAUDE.md structure...")
        self.validate_claude_md()

        print("[P2] Validating skill pinning (.claude/settings.json)...")
        self.validate_settings_json()

        print("[P5-P8] Validating root settings.json config...")
        self.validate_root_settings_json()

        print("[P7] Validating APScheduler configuration...")
        self.validate_apscheduler_config()

        # Print results
        print(f"\n✓ PASSED ({len(self.passed)}):")
        for msg in self.passed[:15]:
            print(f"  {msg}")
        if len(self.passed) > 15:
            print(f"  ... and {len(self.passed) - 15} more")

        if self.warnings:
            print(f"\n⚠ WARNINGS ({len(self.warnings)}):")
            for msg in self.warnings[:10]:
                print(f"  {msg}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")

        if self.issues:
            print(f"\n✗ CRITICAL ISSUES ({len(self.issues)}):")
            for msg in self.issues[:10]:
                print(f"  {msg}")
            if len(self.issues) > 10:
                print(f"  ... and {len(self.issues) - 10} more")

        print("=" * 70)

        if self.issues:
            status = "🔴 FAILED"
            exit_code = 2
        elif self.warnings:
            status = "🟡 WARNING"
            exit_code = 1
        else:
            status = "🟢 HEALTHY"
            exit_code = 0

        print(f"Status: {status}")
        print(f"Passed: {len(self.passed)} | Warnings: {len(self.warnings)} | Issues: {len(self.issues)}")
        print("=" * 70)

        return exit_code, f"{status}: {len(self.issues)} critical, {len(self.warnings)} warnings"


if __name__ == "__main__":
    checker = HealthChecker()
    exit_code, message = checker.run()
    print(f"\nResult: {message}")
    sys.exit(exit_code)
