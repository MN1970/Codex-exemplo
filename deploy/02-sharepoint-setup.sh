#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: SHAREPOINT FOLDER SETUP
# Manta Maestro v5.0.1 Production Deployment
# ═══════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PHASE 2: SHAREPOINT FOLDER SETUP"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

START_TIME=$(date +%s)

echo "⚠️  MANUAL EXECUTION REQUIRED"
echo ""
echo "This phase requires direct access to Manta SharePoint site."
echo "Automated execution not available in this environment."
echo ""

echo "📋 INSTRUCTIONS:"
echo ""
echo "Step 1: Connect to SharePoint"
echo "  URL: Manta hub SharePoint site"
echo "  Navigate to: 03_Projetos/"
echo ""
echo "Step 2: Create folder structure"
echo ""
echo "  2a) Create: 03_Projetos/OleoGas/"
echo "      └─ Apply folder-level permissions (match S6-S10 pattern)"
echo "      └─ Subfolders (optional):"
echo "         ├─ Projetos Ativos/"
echo "         ├─ Referências/"
echo "         └─ Documentação/"
echo ""
echo "  2b) Create: 03_Projetos/Edificacoes/"
echo "      └─ Apply folder-level permissions (match S6-S10 pattern)"
echo "      └─ Subfolders (optional):"
echo "         ├─ Projetos Ativos/"
echo "         ├─ Referências/"
echo "         └─ Documentação/"
echo ""
echo "Step 3: Verify permissions"
echo "  ✓ OleoGas folder readable by agente-oleo-gas"
echo "  ✓ Edificacoes folder readable by agente-edificacoes"
echo "  ✓ Both visible to Maestro router"
echo ""
echo "Step 4: Wait for MCP indexing"
echo "  ⏳ After creation, wait ~5 minutes for automatic indexing"
echo "  ✓ New folders will appear in manta_sp_index"
echo ""

# Check if MCP tools are available
if command -v mcp &> /dev/null; then
    echo "🔧 MCP tools detected - checking current SharePoint structure:"
    echo ""
    mcp SharePoint list-folders --path "03_Projetos" 2>/dev/null || echo "  (MCP list failed - may require authentication)"
    echo ""
fi

echo "📋 VERIFICATION CHECKLIST:"
echo ""
read -p "  ✓ OleoGas folder created? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Folder creation incomplete"
    exit 1
fi

read -p "  ✓ Edificacoes folder created? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Folder creation incomplete"
    exit 1
fi

read -p "  ✓ Permissions verified? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Permissions not verified"
    exit 1
fi

read -p "  ✓ Waited for MCP indexing (~5 min)? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  MCP indexing not waited"
    exit 1
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ PHASE 2 COMPLETE"
echo "Duration: ${DURATION}s"
echo ""
echo "What was created:"
echo "  ✓ 03_Projetos/OleoGas/ (S12 Óleo & Gás)"
echo "  ✓ 03_Projetos/Edificacoes/ (S13 Edificações)"
echo "  ✓ MCP indexing complete"
echo "═══════════════════════════════════════════════════════════════════════════"
