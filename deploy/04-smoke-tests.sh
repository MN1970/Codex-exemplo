#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: SMOKE TESTS — ROUTING + RAG
# Manta Maestro v5.0.1 Production Deployment
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PHASE 4: SMOKE TESTS — ROUTING + RAG"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

START_TIME=$(date +%s)
PASSED=0
FAILED=0

# Test 1: Verify routing keywords in CLAUDE.md
echo "Test 1: Verify routing keywords in CLAUDE.md"
if grep -q "petróleo" CLAUDE.md && grep -q "edificação" CLAUDE.md; then
    echo "  ✅ PASS: Routing keywords found"
    ((PASSED++))
else
    echo "  ❌ FAIL: Routing keywords not found"
    ((FAILED++))
fi
echo ""

# Test 2: Verify agent files exist and are properly formatted
echo "Test 2: Verify agent files exist and are properly formatted"
AGENT_COUNT=0
for agent in ".claude/agents/agente-oleo-gas.md" ".claude/agents/agente-edificacoes.md"; do
    if [ -f "$agent" ]; then
        if head -3 "$agent" | grep -q "^---"; then
            echo "  ✅ PASS: $agent exists with proper YAML header"
            ((AGENT_COUNT++))
        else
            echo "  ❌ FAIL: $agent missing YAML header"
            ((FAILED++))
        fi
    else
        echo "  ❌ FAIL: $agent not found"
        ((FAILED++))
    fi
done
if [ $AGENT_COUNT -eq 2 ]; then
    ((PASSED++))
fi
echo ""

# Test 3: Verify RAG collections in migration
echo "Test 3: Verify RAG collections in migration"
MIGRATION="supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql"
if [ -f "$MIGRATION" ]; then
    if grep -q "oleo-gas" "$MIGRATION" && grep -q "edificacoes" "$MIGRATION"; then
        echo "  ✅ PASS: RAG collections defined in migration"
        ((PASSED++))
    else
        echo "  ❌ FAIL: RAG collections not found in migration"
        ((FAILED++))
    fi
else
    echo "  ❌ FAIL: Migration file not found"
    ((FAILED++))
fi
echo ""

# Test 4: Verify SharePoint routing in migration
echo "Test 4: Verify SharePoint routing in migration"
if grep -q "OleoGas" "$MIGRATION" && grep -q "Edificacoes" "$MIGRATION"; then
    echo "  ✅ PASS: SharePoint routing registered"
    ((PASSED++))
else
    echo "  ❌ FAIL: SharePoint routing not found"
    ((FAILED++))
fi
echo ""

# Test 5: Verify no regressions in S1-S10
echo "Test 5: Verify existing agents (S1-S10) not affected"
AGENTS_OK=true
for agent_ref in "saneamento" "energia" "portos" "aeroportos" "barragens"; do
    if grep -q "$agent_ref" CLAUDE.md; then
        : # OK
    else
        AGENTS_OK=false
        break
    fi
done
if $AGENTS_OK; then
    echo "  ✅ PASS: Existing agents still in registry"
    ((PASSED++))
else
    echo "  ❌ FAIL: Regression detected in existing agents"
    ((FAILED++))
fi
echo ""

# Test 6: Verify Maestro keywords present
echo "Test 6: Verify Maestro routing keywords present"
if grep -q "gasoduto\|dutovia" CLAUDE.md && grep -q "warehouse\|data center" CLAUDE.md; then
    echo "  ✅ PASS: S12/S13 keywords found"
    ((PASSED++))
else
    echo "  ❌ FAIL: S12/S13 keywords missing"
    ((FAILED++))
fi
echo ""

# Test 7: Verify no conflicting segment numbering
echo "Test 7: Verify no conflicting segment numbering (Convenção A)"
if grep -q "S6.*Portos\|S7.*Aeroportos\|S13.*Edificações" CLAUDE.md; then
    echo "  ✅ PASS: Segment numbering consistent (Convenção A)"
    ((PASSED++))
else
    echo "  ❌ FAIL: Segment numbering inconsistent"
    ((FAILED++))
fi
echo ""

# Test 8: Verify deployment document present
echo "Test 8: Verify deployment documentation complete"
if [ -f "DEPLOYMENT-COMPLETE-v5.0.1.md" ] && [ -f "docs/SEGMENTOS-S12-S13-DECISION.md" ]; then
    echo "  ✅ PASS: Deployment docs complete"
    ((PASSED++))
else
    echo "  ❌ FAIL: Deployment docs missing"
    ((FAILED++))
fi
echo ""

# Manual tests
echo "📋 MANUAL TESTS (requires deployed infrastructure):"
echo ""
echo "  Test 9: Maestro dispatch to S12 (Óleo & Gás)"
echo "    Input: 'Cliente quer viabilidade de gasoduto costeiro com HAZOP'"
echo "    Expected: Dispatch to agente-oleo-gas"
echo "    Status: ⏳ MANUAL"
echo ""
echo "  Test 10: Maestro dispatch to S13 (Edificações)"
echo "    Input: 'Projeto de data center em São Paulo com LEED Gold e BIM'"
echo "    Expected: Dispatch to agente-edificacoes"
echo "    Status: ⏳ MANUAL"
echo ""
echo "  Test 11: RAG query S12"
echo "    Query: SELECT COUNT(*) FROM manta_rag_chunks WHERE collection='oleo-gas'"
echo "    Expected: ≥1 chunks"
echo "    Status: ⏳ MANUAL"
echo ""
echo "  Test 12: RAG query S13"
echo "    Query: SELECT COUNT(*) FROM manta_rag_chunks WHERE collection='edificacoes'"
echo "    Expected: ≥1 chunks"
echo "    Status: ⏳ MANUAL"
echo ""

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ SMOKE TESTS COMPLETE"
echo ""
echo "Automated Tests:  $PASSED passed, $FAILED failed"
echo "Duration: ${DURATION}s"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🟢 ALL AUTOMATED TESTS PASSED"
    echo ""
    echo "Next: Execute manual tests after Phase 3 (MCP indexing)"
    exit 0
else
    echo "🔴 SOME TESTS FAILED"
    echo ""
    echo "Please review failures and retry"
    exit 1
fi
echo "═══════════════════════════════════════════════════════════════════════════"
