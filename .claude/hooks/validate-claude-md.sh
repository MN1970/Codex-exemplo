#!/bin/bash
# Pre-commit hook: Validate CLAUDE.md consistency
# Run this hook before committing changes that affect CLAUDE.md or agent files

set -e

echo "🔍 Validating CLAUDE.md integrity..."

# Check if CLAUDE.md exists
if [ ! -f "CLAUDE.md" ]; then
  echo "❌ CLAUDE.md not found"
  exit 1
fi

# Check consistency between CLAUDE.md and .claude/agents/
echo "   • Checking agent file consistency..."

# Extract agent list from CLAUDE.md
AGENTS_IN_MD=$(grep -oP "agente-\w+" CLAUDE.md | sort -u)

# List agent files
AGENTS_ON_DISK=$(ls -1 .claude/agents/agente-*.md 2>/dev/null | xargs -n1 basename | sed 's/.md$//' | sort -u)

# Verify all agents in CLAUDE.md have corresponding files
for agent in $AGENTS_IN_MD; do
  if ! echo "$AGENTS_ON_DISK" | grep -q "^$agent$"; then
    echo "⚠️  Warning: $agent mentioned in CLAUDE.md but .claude/agents/$agent.md not found"
  fi
done

# Verify all .claude/agents files are mentioned in CLAUDE.md
for agent in $AGENTS_ON_DISK; do
  if ! echo "$AGENTS_IN_MD" | grep -q "^$agent$"; then
    echo "⚠️  Warning: .claude/agents/$agent.md exists but not mentioned in CLAUDE.md"
  fi
done

# Check for duplicate agent codes
echo "   • Checking for duplicate agent codes..."
DUPLICATES=$(grep -o "Manta 03-S[0-9]" CLAUDE.md | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
  echo "❌ Duplicate agent codes found: $DUPLICATES"
  exit 1
fi

# Validate routing rules reference existing agents
echo "   • Validating routing rules..."
ROUTING_AGENTS=$(grep -oP "→ agente-\w+" CLAUDE.md | cut -d- -f2- | sort -u)
for agent in $ROUTING_AGENTS; do
  if ! echo "$AGENTS_ON_DISK" | grep -q "^agente-$agent$"; then
    echo "❌ Routing rule references non-existent agent: agente-$agent"
    exit 1
  fi
done

# Check version consistency
echo "   • Checking version consistency..."
VERSION=$(grep -m1 "Versão: " CLAUDE.md | grep -oP "v\d+\.\d+\.\d+" || echo "unknown")
echo "   CLAUDE.md version: $VERSION"

echo "✅ CLAUDE.md validation passed"
echo ""
exit 0
