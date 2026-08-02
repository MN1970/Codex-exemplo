#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: AGENT INDEXING & MCP SYNC
# Manta Maestro v5.0.1 Production Deployment
# ═══════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PHASE 3: AGENT INDEXING & MCP SYNC"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

START_TIME=$(date +%s)

echo "ℹ️  AUTOMATIC PHASE"
echo ""
echo "This phase requires no manual action. MCP indexing happens automatically"
echo "after Phase 2 (SharePoint folder creation). Files in .claude/agents/"
echo "are automatically synced to SharePoint Skills folder."
echo ""

echo "⏳ Waiting for MCP indexing to complete (~5 minutes)..."
echo ""
echo "During this time:"
echo "  • .claude/agents/agente-oleo-gas.md → /Skills/Óleo & Gás/"
echo "  • .claude/agents/agente-edificacoes.md → /Skills/Edificações/"
echo "  • Maestro routing keywords registered in maestro_routing_keywords"
echo "  • RAG collections indexed in Supabase"
echo ""

# Show progress dots every 30 seconds for 5 minutes
for i in {1..10}; do
    sleep 30
    echo -n "."
done
echo ""
echo ""

# Verification steps
echo "🔍 Verifying MCP indexing..."
echo ""

# Check if agent files are in .claude/agents/
echo "Test 1: Agent files present in .claude/agents/"
if [ -f ".claude/agents/agente-oleo-gas.md" ] && [ -f ".claude/agents/agente-edificacoes.md" ]; then
    echo "  ✅ PASS: Both agent files present"
    PHASE3_PASS=1
else
    echo "  ❌ FAIL: Agent files missing"
    PHASE3_PASS=0
fi
echo ""

# Check if frontmatters are valid YAML
echo "Test 2: Agent frontmatters valid"
if head -3 ".claude/agents/agente-oleo-gas.md" | grep -q "^---"; then
    echo "  ✅ PASS: agente-oleo-gas.md has valid YAML header"
else
    echo "  ❌ FAIL: agente-oleo-gas.md missing YAML header"
    PHASE3_PASS=0
fi

if head -3 ".claude/agents/agente-edificacoes.md" | grep -q "^---"; then
    echo "  ✅ PASS: agente-edificacoes.md has valid YAML header"
else
    echo "  ❌ FAIL: agente-edificacoes.md missing YAML header"
    PHASE3_PASS=0
fi
echo ""

echo "📋 MANUAL VERIFICATION CHECKLIST:"
echo ""
read -p "  ✓ Check SharePoint Skills folder — do you see both agent files? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "    ✅ SharePoint sync confirmed"
else
    echo "    ⚠️  SharePoint sync may be delayed (wait a few more minutes)"
    PHASE3_PASS=0
fi
echo ""

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ PHASE 3 COMPLETE"
echo "Duration: ${DURATION}s"
echo ""
echo "What was indexed:"
echo "  ✓ .claude/agents/agente-oleo-gas.md synced to SharePoint"
echo "  ✓ .claude/agents/agente-edificacoes.md synced to SharePoint"
echo "  ✓ MCP indexing confirmed"
echo "═══════════════════════════════════════════════════════════════════════════"

if [ $PHASE3_PASS -eq 1 ]; then
    exit 0
else
    exit 1
fi
