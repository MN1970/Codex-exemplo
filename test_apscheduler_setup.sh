#!/bin/bash
# Quick test script for APScheduler implementation

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "=========================================="
echo "APScheduler Implementation Test"
echo "=========================================="
echo ""

# Test 1: Check files exist
echo "[TEST 1] Checking files..."
files=(
    "scripts/apscheduler_setup.py"
    "scripts/feedback_loop_job.py"
    "scripts/health_check_job.py"
    "scripts/rag_reindex_job.py"
    "scripts/agent_memory_purge_job.py"
    ".claude/apscheduler_config.json"
    ".claude/hooks/session_start_apscheduler_check.py"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ MISSING: $file"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo "ERROR: Some files missing"
    exit 1
fi

echo ""
echo "[TEST 2] Checking Python syntax..."
python3 -m py_compile scripts/apscheduler_setup.py
echo "  ✓ apscheduler_setup.py"
python3 -m py_compile scripts/feedback_loop_job.py
echo "  ✓ feedback_loop_job.py"
python3 -m py_compile scripts/health_check_job.py
echo "  ✓ health_check_job.py"

echo ""
echo "[TEST 3] Checking JSON config..."
python3 -m json.tool .claude/apscheduler_config.json > /dev/null
echo "  ✓ apscheduler_config.json is valid JSON"

echo ""
echo "[TEST 4] Listing registered jobs..."
python3 scripts/apscheduler_setup.py --list-jobs 2>&1 | head -20

echo ""
echo "=========================================="
echo "✓ All tests passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set environment variables: export SUPABASE_URL=... SUPABASE_KEY=..."
echo "  2. Test a job: python3 scripts/apscheduler_setup.py --test-job rag-reindex"
echo "  3. Run scheduler: python3 scripts/apscheduler_setup.py --run-scheduler"
echo ""
