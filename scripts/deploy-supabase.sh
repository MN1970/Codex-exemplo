#!/bin/bash
# Deploy Maestro v4.3 schema to Supabase
# Usage: ./scripts/deploy-supabase.sh [--dry-run] [--project-id PROJECT_ID]

set -e

PROJECT_ID="${2:-ogxxgvgtulrbbppshjie}"
DRY_RUN="${1}"
MIGRATION_FILE="supabase/migrations/2026_07_26_maestro_agent_pool.sql"

echo "=========================================="
echo "SUPABASE DEPLOYMENT — Maestro v4.3"
echo "=========================================="
echo ""
echo "Project ID: $PROJECT_ID"
echo "Migration: $MIGRATION_FILE"
echo ""

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Error: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

# Option 1: Using Supabase CLI (recommended)
if command -v supabase &> /dev/null; then
    echo "[1/3] Using Supabase CLI..."

    if [ "$DRY_RUN" == "--dry-run" ]; then
        echo "🔍 DRY RUN: Checking migration validity..."
        supabase db push --dry-run
    else
        echo "✓ Applying migration..."
        supabase db push
    fi

    echo "✓ Migration applied successfully"
else
    echo "⚠️  Supabase CLI not found. Using psql instead..."

    # Option 2: Direct psql (if CLI not available)
    if [ -z "$SUPABASE_DB_URL" ]; then
        echo "❌ Error: SUPABASE_DB_URL not set"
        echo "   Set via: export SUPABASE_DB_URL=postgresql://..."
        exit 1
    fi

    if [ "$DRY_RUN" == "--dry-run" ]; then
        echo "🔍 DRY RUN: Would apply migration..."
        psql "$SUPABASE_DB_URL" --dry-run -f "$MIGRATION_FILE"
    else
        echo "✓ Applying migration via psql..."
        psql "$SUPABASE_DB_URL" -f "$MIGRATION_FILE"
    fi
fi

echo ""
echo "=========================================="
echo "✓ DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Verification queries:"
echo ""
echo "1. Check agent pool:"
echo "   SELECT agent_code, agent_name, priority FROM maestro_agent_pool ORDER BY priority DESC;"
echo ""
echo "2. Check logs table:"
echo "   SELECT COUNT(*) FROM maestro_execution_logs;"
echo ""
echo "3. Check indexes:"
echo "   SELECT indexname FROM pg_indexes WHERE tablename='maestro_execution_logs';"
echo ""
