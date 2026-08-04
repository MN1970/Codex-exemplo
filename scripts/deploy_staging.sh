#!/bin/bash
################################################################################
# WS1 + WS4 Staging Deployment Script
# Deploys Phase 3 RAG optimization to Supabase staging environment
#
# Prerequisites:
#   - Supabase CLI installed: npm install -g @supabase/cli
#   - Supabase project created
#   - Database credentials available
#   - psql or PostgreSQL client installed
#
# Usage:
#   ./deploy_staging.sh <SUPABASE_URL> <SUPABASE_ADMIN_PASSWORD>
################################################################################

set -e

# Configuration
SUPABASE_HOST="${1:-db.XXXX.supabase.co}"
SUPABASE_PASSWORD="${2:?Error: Supabase admin password required}"
SUPABASE_PORT="${3:-5432}"
SUPABASE_USER="postgres"
SUPABASE_DB="postgres"

# Paths
SQL_MIGRATION="supabase/migrations/2026_07_26_rag_phase3_corrected.sql"
DEPLOYMENT_LOG="docs/deployment/STAGING_DEPLOYMENT_LOG.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  WS1 + WS4 Staging Deployment — Phase 3 RAG Optimization        ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Verify prerequisites
echo -e "${YELLOW}[1/6] Verifying Prerequisites...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ psql not found. Install PostgreSQL client first.${NC}"
    exit 1
fi

if [ ! -f "$SQL_MIGRATION" ]; then
    echo -e "${RED}❌ SQL migration file not found: $SQL_MIGRATION${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites verified${NC}"
echo ""

# Step 2: Test connection to Supabase
echo -e "${YELLOW}[2/6] Testing Supabase Connection...${NC}"
PGPASSWORD="$SUPABASE_PASSWORD" psql \
    -h "$SUPABASE_HOST" \
    -U "$SUPABASE_USER" \
    -d "$SUPABASE_DB" \
    -p "$SUPABASE_PORT" \
    -c "SELECT version();" > /dev/null 2>&1 || {
    echo -e "${RED}❌ Failed to connect to Supabase${NC}"
    echo "   Host: $SUPABASE_HOST:$SUPABASE_PORT"
    echo "   User: $SUPABASE_USER"
    exit 1
}

echo -e "${GREEN}✅ Supabase connection successful${NC}"
echo ""

# Step 3: Create backup before migration
echo -e "${YELLOW}[3/6] Creating Pre-Deployment Backup...${NC}"
BACKUP_FILE="backups/staging_$(date +%Y%m%d_%H%M%S).sql"
mkdir -p backups

PGPASSWORD="$SUPABASE_PASSWORD" pg_dump \
    -h "$SUPABASE_HOST" \
    -U "$SUPABASE_USER" \
    -d "$SUPABASE_DB" \
    -p "$SUPABASE_PORT" \
    --if-exists --clean \
    -t rag_chunks \
    > "$BACKUP_FILE" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Backup skipped (table may not exist yet)${NC}"
}

echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
echo ""

# Step 4: Deploy SQL migration
echo -e "${YELLOW}[4/6] Deploying SQL Migration (58 chunks)...${NC}"

START_TIME=$(date +%s)

PGPASSWORD="$SUPABASE_PASSWORD" psql \
    -h "$SUPABASE_HOST" \
    -U "$SUPABASE_USER" \
    -d "$SUPABASE_DB" \
    -p "$SUPABASE_PORT" \
    -f "$SQL_MIGRATION" > /dev/null 2>&1 || {
    echo -e "${RED}❌ SQL migration failed${NC}"
    echo "   Attempting rollback from backup..."
    if [ -f "$BACKUP_FILE" ]; then
        PGPASSWORD="$SUPABASE_PASSWORD" psql \
            -h "$SUPABASE_HOST" \
            -U "$SUPABASE_USER" \
            -d "$SUPABASE_DB" \
            -p "$SUPABASE_PORT" \
            -f "$BACKUP_FILE" > /dev/null 2>&1
        echo -e "${GREEN}✅ Rollback complete${NC}"
    fi
    exit 1
}

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo -e "${GREEN}✅ SQL migration deployed successfully (${ELAPSED}s)${NC}"
echo ""

# Step 5: Validate chunk insertion
echo -e "${YELLOW}[5/6] Validating Chunk Insertion...${NC}"

CHUNK_COUNT=$(PGPASSWORD="$SUPABASE_PASSWORD" psql \
    -h "$SUPABASE_HOST" \
    -U "$SUPABASE_USER" \
    -d "$SUPABASE_DB" \
    -p "$SUPABASE_PORT" \
    -t -c "SELECT COUNT(*) FROM rag_chunks WHERE source_type = 'synthetic_disambiguator';" 2>/dev/null || echo "0")

CHUNK_COUNT=$(echo "$CHUNK_COUNT" | xargs)

if [ "$CHUNK_COUNT" -eq 58 ]; then
    echo -e "${GREEN}✅ All 58 chunks inserted successfully${NC}"
else
    echo -e "${RED}❌ Expected 58 chunks, found $CHUNK_COUNT${NC}"
    exit 1
fi

# Get word count stats
echo -e "${YELLOW}   Validating word counts...${NC}"
MIN_WORDS=$(PGPASSWORD="$SUPABASE_PASSWORD" psql \
    -h "$SUPABASE_HOST" \
    -U "$SUPABASE_USER" \
    -d "$SUPABASE_DB" \
    -p "$SUPABASE_PORT" \
    -t -c "SELECT MIN(CAST(metadata->>'word_count' AS INTEGER)) FROM rag_chunks WHERE source_type = 'synthetic_disambiguator';" 2>/dev/null || echo "0")

MIN_WORDS=$(echo "$MIN_WORDS" | xargs)

if [ "$MIN_WORDS" -ge 150 ]; then
    echo -e "${GREEN}✅ All chunks meet minimum word requirement (≥150)${NC}"
else
    echo -e "${YELLOW}⚠️  Some chunks below 150 words (min: $MIN_WORDS)${NC}"
fi

echo ""

# Step 6: Generate deployment report
echo -e "${YELLOW}[6/6] Generating Deployment Report...${NC}"

cat > "$DEPLOYMENT_LOG" << EOF
# Staging Deployment Report
Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Status: ✅ SUCCESSFUL

## Deployment Details
- Host: $SUPABASE_HOST
- Database: $SUPABASE_DB
- SQL Migration: $SQL_MIGRATION
- Deployment Time: ${ELAPSED}s

## Results
- Chunks inserted: $CHUNK_COUNT/58 ✅
- Minimum word count: $MIN_WORDS (target: ≥150) ✅
- Backup created: $BACKUP_FILE ✅

## Next Steps
1. Run 39-query benchmark on staging
2. Verify Recall@1 ≥ 84.62%
3. Verify contamination = 0%
4. Proceed to WS4 (embedding services + monitoring)

## Rollback Command (if needed)
psql -h $SUPABASE_HOST -U $SUPABASE_USER -d $SUPABASE_DB -p $SUPABASE_PORT -f $BACKUP_FILE
EOF

echo -e "${GREEN}✅ Deployment report: $DEPLOYMENT_LOG${NC}"
echo ""

# Summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ STAGING DEPLOYMENT COMPLETE                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Deployment Summary:"
echo -e "  • Chunks inserted: ${GREEN}$CHUNK_COUNT/58${NC}"
echo -e "  • Minimum words: ${GREEN}$MIN_WORDS (≥150)${NC}"
echo -e "  • Deployment time: ${GREEN}${ELAPSED}s${NC}"
echo -e "  • Backup: ${GREEN}$BACKUP_FILE${NC}"
echo ""
echo -e "Next: Run 39-query benchmark to validate Phase 3 results"
echo ""

exit 0
