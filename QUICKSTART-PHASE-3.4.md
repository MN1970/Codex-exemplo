# Phase 3.4 — AskCAD Persona Sync
## Quick Start Guide

**Status:** ✅ Production-Ready | **Version:** 1.0 | **Date:** 2026-07-27

---

## 60-Second Setup

```bash
# 1. Install dependencies
pip install pyyaml requests pytest

# 2. Create AskCAD config directory
mkdir -p .askcad

# 3. Set API key (for local testing)
export ASKCAD_API_KEY="sk-your-api-key-here"

# 4. Extract agent metadata
python scripts/extract_agent_metadata.py --output /tmp/metadata.json

# 5. View extracted metadata
cat /tmp/metadata.json | python -m json.tool | head -50

# Done! Ready to sync
```

---

## Five Core Commands

### 1. Extract Metadata
```bash
python scripts/extract_agent_metadata.py \
  --output agents_metadata.json \
  --validate \
  --report
```
**Output:** `agents_metadata.json` with all agent definitions

### 2. Sync to AskCAD (Dry-Run First)
```bash
python scripts/askcad_sync_client.py sync \
  --agent-code manta-03-s1 \
  --metadata agents_metadata.json \
  --dry-run
```
**Output:** Validation report (no actual changes)

### 3. Sync to AskCAD (Production)
```bash
python scripts/askcad_sync_client.py sync \
  --agent-code manta-03-s1 \
  --metadata agents_metadata.json
```
**Output:** `SyncResult` JSON with success/failure status

### 4. Check Health & Alerts
```bash
python scripts/monitoring_askcad_sync.py health --hours 24
```
**Output:** Success rate, agent count, alerts, etc.

### 5. Rollback on Error
```bash
python scripts/askcad_sync_client.py rollback \
  --agent-code manta-03-s1 \
  --target-version 1.0.2
```
**Output:** Rollback confirmation

---

## Common Workflows

### Workflow A: Push Agent Update to Production

```bash
# 1. Update your agent file
nano .claude/agents/agente-portos.md
# Edit version, capabilities, keywords, etc.

# 2. Commit and push (triggers GitHub Actions)
git add .claude/agents/agente-portos.md
git commit -m "update: agente-portos v1.1.0 with new capabilities"
git push origin main

# 3. GitHub Actions runs automatically:
#    - Validates metadata
#    - Syncs to AskCAD
#    - Verifies success
#    - Sends PR comment

# 4. Check results in Actions tab (5 min)
```

### Workflow B: Test Sync Locally

```bash
# 1. Extract metadata
python scripts/extract_agent_metadata.py --output /tmp/meta.json

# 2. Dry-run sync
python scripts/askcad_sync_client.py sync \
  --agent-code manta-03-s1 \
  --metadata /tmp/meta.json \
  --dry-run

# 3. Check report for issues
# If OK, proceed to production

# 4. Full sync
python scripts/askcad_sync_client.py sync \
  --agent-code manta-03-s1 \
  --metadata /tmp/meta.json

# 5. Verify in AskCAD
python scripts/askcad_sync_client.py verify \
  --agent-code manta-03-s1
```

### Workflow C: Emergency Rollback

```bash
# 1. Check what went wrong
python scripts/monitoring_askcad_sync.py history \
  --agent-code manta-03-s1

# 2. See available versions
python scripts/askcad_sync_client.py history \
  --agent-code manta-03-s1

# 3. Rollback to previous
python scripts/askcad_sync_client.py rollback \
  --agent-code manta-03-s1 \
  --target-version 1.0.0

# 4. Verify
python scripts/askcad_sync_client.py verify \
  --agent-code manta-03-s1
```

---

## Agent File Format

Every agent file in `.claude/agents/` must have this structure:

```yaml
---
agent_code: manta-03-s6           # Required: manta-XX[-sYY]
agent_name: agente-portos         # Required: lowercase-with-hyphens
title: Agente de Portos           # Display title
tier: Sonnet                      # Haiku, Sonnet, or Opus
status: Operacional               # Operacional, Planejado, or Parcial
segment: S6                       # S1-S10 for vertical agents
version: 1.0.0                    # Bump on changes
last_updated: 2026-07-27T12:00Z  # ISO 8601 timestamp
aliases:                          # Alternative names
  - "agente-terminais"
capabilities:                     # List capabilities
  - "Análise de terminais"
keywords:                         # Routing keywords
  - "porto"
  - "ANTAQ"
rag_collections:                  # RAG prefixes
  - "por:"
input_formats: [".pdf", ".dwg"]  # Supported inputs
output_formats: [".pdf", ".json"] # Supported outputs
contact: "s6@mantaassociados.com" # Team email
sharepoint_folder: "03_Projetos/Portos"
dependencies: ["manta-01"]        # Other agents required
---

# Agente de Portos

Markdown content describing the agent...
```

**Required fields:** `agent_code`, `agent_name`, `tier`, `status`
**All others:** Optional but recommended for completeness

---

## Testing

```bash
# Run all tests
pytest tests/test_askcad_sync.py -v

# Run specific test
pytest tests/test_askcad_sync.py::TestMetadataExtraction -v

# Run with coverage
pytest tests/test_askcad_sync.py --cov=scripts --cov-report=html

# Quick integration test
python -m pytest tests/test_askcad_sync.py::TestIntegration -v -s
```

---

## Troubleshooting

### "API Authentication Failed (401)"
```bash
# Check if API key is set
echo $ASKCAD_API_KEY

# Should show: sk-...
# If empty, set it:
export ASKCAD_API_KEY="sk-your-key-here"

# For GitHub Actions, add to Secrets:
gh secret set ASKCAD_API_KEY --body "sk-..."
```

### "Missing required field: agent_code"
```yaml
# Make sure your YAML frontmatter has:
---
agent_code: manta-03-s6    # <-- This line
agent_name: agente-portos
tier: Sonnet
status: Operacional
---
```

### "Version hash mismatch"
```bash
# Bump version in YAML when content changes:
version: 1.0.1  # Was 1.0.0

# Then sync again
python scripts/askcad_sync_client.py sync ...
```

### "Sync timed out (>30s)"
```bash
# Network issue or large payload
# Try again in a few seconds
# Or increase timeout in code:
timeout=60  # default is 30
```

---

## File Structure

```
Codex-exemplo/
├── .claude/agents/
│   ├── agente-portos.md              # ✅ New (S6)
│   ├── agente-saneamento.md          # ✅ New (S8)
│   └── agente-energia.md             # ✅ New (S9)
│
├── scripts/
│   ├── extract_agent_metadata.py     # Part 1: Parser (~200 lines)
│   ├── askcad_sync_client.py         # Part 2: Client (~200 lines)
│   └── monitoring_askcad_sync.py     # Part 4: Monitor (~100 lines)
│
├── .github/workflows/
│   └── askcad-sync.yml               # Part 3: CI/CD (~100 lines)
│
├── tests/
│   └── test_askcad_sync.py           # Part 5: Tests (~200 lines)
│
├── docs/
│   └── PHASE-3.4-ASKCAD-SYNC-IMPLEMENTATION.md  # Full guide
│
├── .askcad/                          # Git-ignored (local config)
│   ├── version_history.json          # Version tracking
│   ├── sync_monitor.db               # SQLite metrics
│   ├── audit_trail.jsonl             # Audit log
│   └── sync.log                      # Detailed logs
│
└── QUICKSTART-PHASE-3.4.md           # This file
```

---

## Key Files to Know

| File | Purpose | Lines |
|------|---------|-------|
| `extract_agent_metadata.py` | Parse agent YAML files | 200 |
| `askcad_sync_client.py` | Sync to AskCAD API | 200 |
| `monitoring_askcad_sync.py` | Track health & alerts | 100 |
| `askcad-sync.yml` | GitHub Actions workflow | 100 |
| `test_askcad_sync.py` | Test suite | 200 |
| `PHASE-3.4-ASKCAD-SYNC-IMPLEMENTATION.md` | Full documentation | — |

---

## Environment Variables

```bash
# Required for API calls
ASKCAD_API_KEY=sk-...           # Your API key

# Optional overrides
ASKCAD_API_URL=https://...      # Default: https://api.askcad.com
LOGLEVEL=DEBUG                  # Default: INFO
```

---

## GitHub Secrets Setup

```bash
# Add to your repository
gh secret set ASKCAD_API_KEY --body "sk-your-key"
gh secret set ASKCAD_API_URL --body "https://api.askcad.com"

# Verify
gh secret list | grep ASKCAD
```

---

## Next Steps

1. **Edit agent files** in `.claude/agents/`
2. **Test locally** with `extract_agent_metadata.py`
3. **Push to main** (GitHub Actions runs automatically)
4. **Monitor** with `monitoring_askcad_sync.py`
5. **Rollback** if needed with `askcad_sync_client.py rollback`

---

## Getting Help

- **Full guide:** `docs/PHASE-3.4-ASKCAD-SYNC-IMPLEMENTATION.md`
- **Issues:** Open GitHub issue with `phase-3.4-askcad` label
- **Slack:** `#manta-maestro-phase3`
- **Email:** maestro@mantaassociados.com

---

**Ready to sync? Start with:**
```bash
python scripts/extract_agent_metadata.py --report
```

