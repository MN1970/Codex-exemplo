# Agent Audit Suite v2 — CLAUDE.md v5.0 Compliance

**Comprehensive drift detection & auto-remediation for Manta Maestro agents**

---

## Quick Summary

Three tools work together to maintain agent synchronization with the canonical v5.0 specification:

1. **`audit_agents.py`** — Detects divergences (checksums, specs, pinning)
2. **`regenerate_skill.py`** — Auto-fixes divergent agents
3. **Reports** — JSON (CI), HTML (humans), CSV (data)

---

## Files Overview

### Core Scripts

| File | Purpose | When to run |
|------|---------|-----------|
| `audit_agents.py` | Detect drift between agents and canonical spec | Every commit, daily scheduled |
| `regenerate_skill.py` | Auto-sync agents to canonical v5.0 | When drift detected, or manual maintenance |
| `audit_report_schema.json` | JSON Schema for audit reports (validation) | Reference only |
| `CI_INTEGRATION_GUIDE.md` | GitHub Actions, GitLab CI, Jenkins examples | Setup guide |
| `AUDIT_README.md` | This file | Reference |

### Generated Output

| File | Format | Audience | Refresh |
|------|--------|----------|---------|
| `rag_evals/audit_agents.json` | Structured JSON | CI/CD pipelines, APIs | On-demand |
| `rag_evals/divergence_report.json` | JSON (remediation) | Automation, alerts | On-demand |
| `rag_evals/audit_agents.html` | HTML | Team (browser) | On-demand |
| `rag_evals/audit_agents.csv` | CSV | Excel, BI tools | On-demand |
| `audit.log` | Text log | Debugging | On-demand |
| `divergence_fix.log` | Text log | Regeneration history | On-demand |

---

## Usage Guide

### 1. Basic Audit

```bash
# Run audit, output to JSON (default)
python scripts/audit_agents.py --verbose

# Check exit code
echo $?  # 0 = pass, 1 = fail
```

**Output:**
- `rag_evals/audit_agents.json` — Full results
- `rag_evals/divergence_report.json` — Drift details
- `audit.log` — Execution log

### 2. Generate HTML Report

```bash
python scripts/audit_agents.py \
  --output-format html \
  --verbose

# Open in browser
open rag_evals/audit_agents.html
```

### 3. Export to CSV

```bash
python scripts/audit_agents.py \
  --output-format csv \
  --output-dir rag_evals

# Import into Excel/BI tool
open rag_evals/audit_agents.csv
```

### 4. Check for Drift

```bash
python scripts/audit_agents.py --divergence-threshold 0

# If exit code = 1, drift detected
# Review: cat rag_evals/divergence_report.json
```

### 5. Auto-Remediate (Dry-Run First)

```bash
# Preview changes
python scripts/regenerate_skill.py --all --dry-run

# Apply changes
python scripts/regenerate_skill.py --all --verbose

# Re-run audit to verify
python scripts/audit_agents.py --verbose
```

### 6. Fix Single Agent

```bash
# Dry-run
python scripts/regenerate_skill.py --agent agente-saneamento --dry-run

# Apply
python scripts/regenerate_skill.py --agent agente-saneamento --verbose
```

### 7. Send Slack Alert

```bash
python scripts/audit_agents.py \
  --slack-webhook https://hooks.slack.com/services/YOUR/WEBHOOK \
  --verbose
```

---

## Understanding Divergence Types

### CHECKSUM_MISMATCH (HIGH severity)

**What:** File content differs from canonical spec in VERSIONS.json

**Why:** Agent file was manually edited after canonical was updated

**Fix:** `regenerate_skill.py --agent <id>`

```
Audit Output:
  "divergences": ["CHECKSUM_MISMATCH (expected=f1a3d2..., actual=3435f9...)"]
```

### SKILL_PIN_MISMATCH (MEDIUM severity)

**What:** settings.json pins wrong version (e.g., v4.9 instead of v5.0)

**Why:** settings.json not updated during upgrade

**Fix:** `regenerate_skill.py --agent <id>` updates pin automatically

### MODEL_MISMATCH (MEDIUM severity)

**What:** Agent frontmatter specifies wrong model (e.g., "haiku" vs "sonnet")

**Why:** Inconsistent tier assignment

**Fix:** Manual edit or `regenerate_skill.py`

### NOT_IN_CANONICAL_20 (CRITICAL)

**What:** Agent not in the 20-agent master registry

**Why:** Agent doesn't exist in v5.0 spec

**Fix:** Add to `CANONICAL_20_AGENTS` dict in `audit_agents.py`

### NO_V5_SPEC_IN_VERSIONS_JSON (HIGH severity)

**What:** VERSIONS.json missing v5.0 entry for agent

**Why:** Version file not initialized

**Fix:** Add v5.0 entry with correct checksum

### MISSING_RAG_COLLECTION_SPEC (LOW severity)

**What:** Vertical agent missing RAG collection reference (for S1–S10)

**Why:** Optional metadata missing

**Fix:** Add `rag_collection` field to VERSIONS.json

---

## CI/CD Integration Examples

### GitHub Actions (Quick Start)

```yaml
- name: Run Agent Audit
  run: |
    python scripts/audit_agents.py \
      --divergence-threshold 0 \
      --output-dir rag_evals
    
    # Check exit code
    EXIT=$?
    [ $EXIT -eq 0 ] && echo "PASS" || echo "FAIL"
    exit $EXIT
```

### GitLab CI (Quick Start)

```yaml
audit_agents:
  script:
    - python scripts/audit_agents.py --divergence-threshold 0
  artifacts:
    paths:
      - rag_evals/
```

### Jenkins (Quick Start)

```groovy
stage('Audit') {
  steps {
    sh 'python scripts/audit_agents.py --divergence-threshold 0'
  }
}
```

See **[CI_INTEGRATION_GUIDE.md](./CI_INTEGRATION_GUIDE.md)** for complete examples.

---

## Canonical Agent Registry (20 Agents)

### Tier 1: Horizontals (11)

```
maestro                (Manta 00)
agente-claims          (Manta 01)
agente-contratual      (Manta 02)
agente-imobiliario     (Manta 04)
agente-orcamento       (Manta 05)
agente-modelagem       (Manta 06)
agente-cronograma      (Manta 07)
agente-bd              (Manta 13)
agente-apresentacoes   (Manta 14)
agente-advisory        (Manta 15)
agente-arquiteto-ia    (Manta 16)
```

### Tier 2–3: Verticals (9)

```
agente-rodovias        (Manta 03-S1) — Roads
agente-oae             (Manta 03-S2) — Bridges/Viaducts
agente-ferrovia        (Manta 03-S3) — Railways
agente-metro           (Manta 03-S4) — Metros
agente-portos          (Manta 03-S6) — Ports
agente-aeroportos      (Manta 03-S7) — Airports
agente-saneamento      (Manta 03-S8) — Water/Sanitation ⭐ PRIORITY
agente-energia         (Manta 03-S9) — Power
agente-barragens       (Manta 03-S10) — Dams
```

---

## Spec Files

### CLAUDE.md v5.0

Master registry with 20 agents, 8 pillars, routing rules.

**Location:** `/CLAUDE.md`  
**Updated:** 2026-07-25  
**Contains:** Agent map, tier definitions, RAG collections, routing rules

### VERSIONS.json

Tracks checksums and versions for every agent + deprecated versions.

**Location:** `/VERSIONS.json`  
**Updated:** After each audit fix  
**Contains:** MD5 checksums (v5.0, v4.9), RAG collections, pinning metadata

### settings.json

Skill version pins and agent routing config.

**Location:** `.claude/settings.json`  
**Updated:** By regenerate_skill.py  
**Contains:** skill_version_pin (e.g., `agente-saneamento: v5.0`)

---

## Troubleshooting

### Q: Audit passes but git diff shows changes?

**A:** Drift was already present. Run `regenerate_skill.py` and commit:

```bash
python scripts/regenerate_skill.py --all
git add .claude/agents/* VERSIONS.json .claude/settings.json
git commit -m "chore: sync agents to v5.0 canonical spec"
```

### Q: `divergence_report.json` shows agents_to_fix but I didn't change anything?

**A:** Checksums in VERSIONS.json may be outdated. Use force flag:

```bash
python scripts/regenerate_skill.py --all --force
```

### Q: How to update agent content in bulk?

**A:** Extend `CANONICAL_AGENT_SPECS` dict in `regenerate_skill.py` with full templates, then regenerate:

```bash
python scripts/regenerate_skill.py --all
```

### Q: Can I exclude certain agents from audit?

**A:** Not directly. Instead, update their checksum in VERSIONS.json to match current file:

```bash
# Calculate actual checksum
md5sum .claude/agents/agente-saneamento.md

# Update VERSIONS.json with actual value
jq '.agent_skills."agente-saneamento".v5.0.checksum = "new_value"' VERSIONS.json > tmp.json
mv tmp.json VERSIONS.json
```

### Q: What happens if I manually edit an agent file?

**A:** Checksum changes, drift is detected on next audit:

```bash
# Before edit
Checksum: f1a3d2b4...

# After manual edit
Checksum: 3435f9cb...

# Audit detects mismatch
CHECKSUM_MISMATCH (expected=f1a3d2b4..., actual=3435f9cb...)
```

---

## Performance Notes

- **Audit execution:** < 1 second for 5 agents
- **Report generation:** < 500ms per format
- **Checksum calculation:** ~10ms per file
- **JSON schema validation:** < 100ms

No external dependencies (pure Python standard library).

---

## Version History

### v2.0 (Current — 2026-07-25)

- Full drift detection (checksum, version pins, specs)
- Auto-remediation with dry-run mode
- Structured JSON output + divergence_report.json
- HTML/CSV reporting
- Slack alerts
- CI/CD integration guide

### v1.0 (2026-07-05)

- Basic audit (pattern matching only)
- HTML report only
- No auto-fix capability

---

## Related Documentation

- [CLAUDE.md v5.0](../CLAUDE.md) — Master agent registry
- [VERSIONS.json](../VERSIONS.json) — Version tracking
- [CI_INTEGRATION_GUIDE.md](./CI_INTEGRATION_GUIDE.md) — CI/CD examples
- [audit_report_schema.json](./audit_report_schema.json) — Output schema (JSON Schema)

---

## Support & Contact

**Author:** mneves@mantaassociados.com  
**Version:** v2.0  
**Updated:** 2026-07-25  
**Status:** Production

For issues or feature requests, create an issue with label `agent-audit`.

---

## License & Attribution

Part of **Manta Maestro v5.0** — Agent Registry & Orchestration system.

Generated by: Agent audit_agents.py v2.0
