#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: SUPABASE SCHEMA MIGRATION
# Manta Maestro v5.0.1 Production Deployment
# ═══════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PHASE 1: SUPABASE SCHEMA MIGRATION"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

MIGRATION_FILE="supabase/migrations/2026_07_31_v4_3_agents_s12_s13.sql"
START_TIME=$(date +%s)

# Validate migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ ERROR: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "✓ Migration file found: $MIGRATION_FILE"
wc -l "$MIGRATION_FILE" | awk '{print "  Lines: " $1}'
echo ""

# Check for Supabase CLI
if command -v supabase &> /dev/null; then
    echo "🚀 Supabase CLI detected. Executing migration..."
    echo ""

    # Show dry-run first
    echo "📋 Dry-run preview:"
    supabase db push --remote --dry-run 2>&1 | head -20 || true
    echo ""

    # Ask for confirmation
    read -p "❓ Execute migration? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⏳ Executing migration..."
        supabase db push --remote
        echo "✅ Migration executed successfully"
    else
        echo "⚠️  Migration skipped by user"
        exit 0
    fi

elif [ -n "$SUPABASE_DB_URL" ]; then
    echo "🚀 Using SUPABASE_DB_URL environment variable..."
    echo ""

    # Show preview
    echo "📋 Preview (first 30 lines of migration):"
    head -30 "$MIGRATION_FILE"
    echo "..."
    echo ""

    # Ask for confirmation
    read -p "❓ Execute migration? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "⏳ Executing migration via psql..."
        psql "$SUPABASE_DB_URL" -f "$MIGRATION_FILE"
        echo "✅ Migration executed successfully"
    else
        echo "⚠️  Migration skipped by user"
        exit 0
    fi

else
    echo "⚠️  Neither Supabase CLI nor SUPABASE_DB_URL found"
    echo ""
    echo "📋 To execute this migration manually:"
    echo ""
    echo "Option A: Via Supabase CLI"
    echo "  supabase db push --remote"
    echo ""
    echo "Option B: Via psql"
    echo "  psql \"\$SUPABASE_DB_URL\" -f $MIGRATION_FILE"
    echo ""
    echo "Option C: Via Supabase dashboard"
    echo "  1. Open Supabase dashboard"
    echo "  2. Go to SQL Editor"
    echo "  3. Copy content from $MIGRATION_FILE"
    echo "  4. Execute in new query"
    echo ""
    exit 1
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ PHASE 1 COMPLETE"
echo "Duration: ${DURATION}s"
echo ""
echo "What was deployed:"
echo "  ✓ 2 RAG collections: oleo-gas (S12) + edificacoes (S13)"
echo "  ✓ 2 SharePoint routing rules"
echo "  ✓ 17 Maestro routing keywords"
echo "═══════════════════════════════════════════════════════════════════════════"
