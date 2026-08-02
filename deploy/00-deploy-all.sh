#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# MANTA MAESTRO v5.0.1 — COMPLETE DEPLOYMENT ORCHESTRATOR
# Production deployment of S12 (Óleo & Gás) + S13 (Edificações)
# ═══════════════════════════════════════════════════════════════════════════

set +e  # Don't exit on individual phase failures — show all results

DEPLOY_START=$(date +%s)

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    MANTA MAESTRO v5.0.1 DEPLOYMENT                        ║"
echo "║                   Production Deployment Orchestrator                      ║"
echo "║                      S12 (Óleo & Gás) + S13 (Edificações)                 ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

PHASES_PASSED=0
PHASES_FAILED=0

# Phase 1: Supabase Migration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 1: SUPABASE SCHEMA MIGRATION (~ 2 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PHASE1_START=$(date +%s)
bash deploy/01-supabase-migration.sh
PHASE1_RESULT=$?
PHASE1_END=$(date +%s)
PHASE1_DURATION=$((PHASE1_END - PHASE1_START))

if [ $PHASE1_RESULT -eq 0 ]; then
    echo "✅ PHASE 1 PASSED"
    ((PHASES_PASSED++))
else
    echo "❌ PHASE 1 FAILED"
    ((PHASES_FAILED++))
fi
echo ""

# Phase 2: SharePoint Setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 2: SHAREPOINT FOLDER SETUP (~ 10 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PHASE2_START=$(date +%s)
bash deploy/02-sharepoint-setup.sh
PHASE2_RESULT=$?
PHASE2_END=$(date +%s)
PHASE2_DURATION=$((PHASE2_END - PHASE2_START))

if [ $PHASE2_RESULT -eq 0 ]; then
    echo "✅ PHASE 2 PASSED"
    ((PHASES_PASSED++))
else
    echo "❌ PHASE 2 FAILED"
    ((PHASES_FAILED++))
fi
echo ""

# Phase 3: Agent Indexing
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 3: AGENT INDEXING & MCP SYNC (~ 5 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PHASE3_START=$(date +%s)
bash deploy/03-agent-indexing.sh
PHASE3_RESULT=$?
PHASE3_END=$(date +%s)
PHASE3_DURATION=$((PHASE3_END - PHASE3_START))

if [ $PHASE3_RESULT -eq 0 ]; then
    echo "✅ PHASE 3 PASSED"
    ((PHASES_PASSED++))
else
    echo "⚠️  PHASE 3 INCOMPLETE (may be delayed MCP sync)"
    ((PHASES_FAILED++))
fi
echo ""

# Phase 4: Smoke Tests
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 4: SMOKE TESTS & VALIDATION (~ 15 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PHASE4_START=$(date +%s)
bash deploy/04-smoke-tests.sh
PHASE4_RESULT=$?
PHASE4_END=$(date +%s)
PHASE4_DURATION=$((PHASE4_END - PHASE4_START))

if [ $PHASE4_RESULT -eq 0 ]; then
    echo "✅ PHASE 4 PASSED"
    ((PHASES_PASSED++))
else
    echo "❌ PHASE 4 FAILED"
    ((PHASES_FAILED++))
fi
echo ""

# Phase 5: Notification
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 5: OPERATIONAL HUB COMMUNICATION (~ 2 min)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PHASE5_START=$(date +%s)
bash deploy/05-notification.sh
PHASE5_RESULT=$?
PHASE5_END=$(date +%s)
PHASE5_DURATION=$((PHASE5_END - PHASE5_START))

if [ $PHASE5_RESULT -eq 0 ]; then
    echo "✅ PHASE 5 PASSED"
    ((PHASES_PASSED++))
else
    echo "⚠️  PHASE 5 INCOMPLETE (announcement may need manual post)"
    ((PHASES_FAILED++))
fi
echo ""

# Summary
DEPLOY_END=$(date +%s)
DEPLOY_DURATION=$((DEPLOY_END - DEPLOY_START))

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                        DEPLOYMENT SUMMARY                                 ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Phases Passed:  $PHASES_PASSED / 5"
echo "Phases Failed:  $PHASES_FAILED / 5"
echo ""
echo "Phase Durations:"
echo "  Phase 1 (Supabase):    ${PHASE1_DURATION}s"
echo "  Phase 2 (SharePoint):  ${PHASE2_DURATION}s"
echo "  Phase 3 (MCP Sync):    ${PHASE3_DURATION}s"
echo "  Phase 4 (Tests):       ${PHASE4_DURATION}s"
echo "  Phase 5 (Notification):${PHASE5_DURATION}s"
echo "  ─────────────────────────────"
echo "  Total Duration:        ${DEPLOY_DURATION}s (~$(( (DEPLOY_DURATION + 59) / 60 )) min)"
echo ""

if [ $PHASES_FAILED -eq 0 ]; then
    echo "🟢 ALL PHASES COMPLETED SUCCESSFULLY"
    echo ""
    echo "✅ Deployment Status: READY FOR PRODUCTION"
    echo ""
    echo "Next Steps:"
    echo "  1. ✅ Verify Maestro dispatch logs for S12/S13 routing"
    echo "  2. ✅ Monitor RAG latency for new collections (<500ms target)"
    echo "  3. ✅ Watch SharePoint sync confirmation"
    echo "  4. ✅ Confirm no regressions in S1–S10 agents"
    echo "  5. ✅ 24-hour post-deployment monitoring"
    echo ""
    echo "Rollback (if needed):"
    echo "  See DEPLOYMENT-COMPLETE-v5.0.1.md for rollback procedures"
    echo ""
    exit 0
else
    echo "🔴 SOME PHASES INCOMPLETE"
    echo ""
    echo "⚠️  Manual intervention may be required:"
    if [ $PHASE1_RESULT -ne 0 ]; then
        echo "  • Phase 1: Check Supabase migration execution"
    fi
    if [ $PHASE2_RESULT -ne 0 ]; then
        echo "  • Phase 2: Verify SharePoint folder creation"
    fi
    if [ $PHASE3_RESULT -ne 0 ]; then
        echo "  • Phase 3: Wait for MCP indexing completion"
    fi
    if [ $PHASE4_RESULT -ne 0 ]; then
        echo "  • Phase 4: Review smoke test failures"
    fi
    if [ $PHASE5_RESULT -ne 0 ]; then
        echo "  • Phase 5: Post Slack announcement manually"
    fi
    echo ""
    echo "See DEPLOYMENT-COMPLETE-v5.0.1.md for troubleshooting"
    echo ""
    exit 1
fi
