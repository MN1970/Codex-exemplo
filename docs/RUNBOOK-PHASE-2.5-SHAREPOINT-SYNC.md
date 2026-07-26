# Runbook: Phase 2.5 SharePoint Sync Automation

**Status**: 🟢 PRODUCTION READY  
**Owner**: DevOps + SharePoint Admin  
**Audience**: Engineers + administrators  
**Duration**: 1-2 hours (initial setup + testing)

---

## Pre-Deployment Checklist

- [ ] Microsoft 365 tenant admin access
- [ ] Azure AD App registration completed
- [ ] SharePoint site URL confirmed (`/sites/manta`)
- [ ] 04_IA document library identified and accessible
- [ ] GitHub repository write access
- [ ] Python 3.9+ available locally
- [ ] Microsoft Graph Postman collection (optional, for testing)

---

## STEP 1: Configure Azure App Registration (20 min)

### 1.1 Create App Registration

```bash
# Navigate to Azure Portal
# https://portal.azure.com → App registrations → New registration

# App details:
# Name: Maestro-SharePoint-Sync
# Supported account types: Single tenant (your organization only)
# Redirect URI: (leave blank for service account)

# After creation, note these values:
APP_CLIENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"      # Application ID
APP_TENANT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"      # Directory ID
```

### 1.2 Create Client Secret

```bash
# In Azure Portal → App registration → Certificates & secrets
# Click: New client secret
# Description: Maestro SharePoint Sync
# Expires: 24 months

APP_CLIENT_SECRET="your-secret-here"  # Copy the VALUE (not the Secret ID)

# ⚠️ Save this immediately! Can't be retrieved later!
```

### 1.3 Configure API Permissions

```bash
# In Azure Portal → API permissions
# Click: Add a permission → Microsoft Graph

# Required permissions:
# - Sites.ReadWrite.All (read/write SharePoint sites)
# - Files.ReadWrite.All (read/write files)
# - Directory.ReadWrite.All (optional, for admin purposes)

# Grant admin consent (button at bottom)
```

### 1.4 Test App Registration

```bash
# Get access token
TOKEN_RESPONSE=$(curl -s -X POST \
  "https://login.microsoftonline.com/$APP_TENANT_ID/oauth2/v2.0/token" \
  -d "client_id=$APP_CLIENT_ID" \
  -d "client_secret=$APP_CLIENT_SECRET" \
  -d "scope=https://graph.microsoft.com/.default" \
  -d "grant_type=client_credentials")

GRAPH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

# Verify token works
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  https://graph.microsoft.com/v1.0/me | jq '.error'

# Expected: null (no error) or actual response
```

---

## STEP 2: Get SharePoint IDs (10 min)

### 2.1 Find SharePoint Site ID

```bash
# List all sites in tenant
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/sites?search=manta" | jq '.'

# Look for: /sites/manta
# Copy the "id" field (format: tenant.sharepoint.com,site-id,web-id)

SHAREPOINT_SITE_ID="xxxxx,xxxxx,xxxxx"
```

### 2.2 Find Drive ID (04_IA Library)

```bash
# Get drives in the site
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/$SHAREPOINT_SITE_ID/drives" | jq '.value[] | {name, id}'

# Find: "04_IA" (or "04_IA - Documentos IA")
# Copy the "id" field

SHAREPOINT_DRIVE_ID="b!xxxxx"
```

### 2.3 Find Agents Folder ID

```bash
# Get folder structure
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drives/$SHAREPOINT_DRIVE_ID/root/children" | \
  jq '.value[] | select(.name | contains("01-agentes")) | {name, id, webUrl}'

# Should see: 01-agentes-fundamentais
AGENTS_FOLDER_ID="01XXX"
```

---

## STEP 3: Configure GitHub Secrets (5 min)

### 3.1 Gather All Credentials

```bash
# Compile all secrets
cat > /tmp/sp_secrets.env << EOF
SHAREPOINT_SITE_ID=$SHAREPOINT_SITE_ID
SHAREPOINT_DRIVE_ID=$SHAREPOINT_DRIVE_ID
SHAREPOINT_AGENTS_FOLDER_ID=$AGENTS_FOLDER_ID
MICROSOFT_GRAPH_CLIENT_ID=$APP_CLIENT_ID
MICROSOFT_GRAPH_CLIENT_SECRET=$APP_CLIENT_SECRET
MICROSOFT_GRAPH_TENANT_ID=$APP_TENANT_ID
EOF
```

### 3.2 Add to GitHub Secrets

```bash
gh secret set SHAREPOINT_SITE_ID --body "$SHAREPOINT_SITE_ID"
gh secret set SHAREPOINT_DRIVE_ID --body "$SHAREPOINT_DRIVE_ID"
gh secret set SHAREPOINT_AGENTS_FOLDER_ID --body "$SHAREPOINT_AGENTS_FOLDER_ID"
gh secret set MICROSOFT_GRAPH_CLIENT_ID --body "$APP_CLIENT_ID"
gh secret set MICROSOFT_GRAPH_CLIENT_SECRET --body "$APP_CLIENT_SECRET"
gh secret set MICROSOFT_GRAPH_TENANT_ID --body "$APP_TENANT_ID"

# Verify
gh secret list | grep SHAREPOINT

# Clean up
rm /tmp/sp_secrets.env
```

---

## STEP 4: Prepare SharePoint Folder Structure (15 min)

### 4.1 Create Agent Folders (if not exist)

Navigate in SharePoint to: `/sites/manta/04_IA/01-agentes-fundamentais/`

Create folders for 5 agents:
- `agente-saneamento`
- `agente-energia`
- `agente-portos`
- `agente-aeroportos`
- `agente-barragens`

### 4.2 Upload Initial Agent Files (Manual)

Option A: Upload via SharePoint UI
1. Go to each agent folder
2. Upload `SKILL.md` from `.claude/agents/*.md`
3. Rename to `SKILL.md` if needed

Option B: Via PowerShell (for admins)

```powershell
# (Windows/Mac PowerShell with Microsoft.SharePoint.Client module)
Connect-PnPOnline -Url "https://manta.sharepoint.com/sites/manta" -Interactive

$agents = @(
    "agente-saneamento",
    "agente-energia",
    "agente-portos",
    "agente-aeroportos",
    "agente-barragens"
)

foreach ($agent in $agents) {
    $folderName = "01-agentes-fundamentais/$agent"
    Add-PnPFolder -Name $agent -Folder "01-agentes-fundamentais"
}
```

---

## STEP 5: Test Locally (20 min)

### 5.1 Install Dependencies

```bash
pip install --upgrade pip
pip install requests python-dotenv

# Verify
python -c "import requests; print(requests.__version__)"
```

### 5.2 Create Local .env File

```bash
cat > .env << 'EOF'
SHAREPOINT_SITE_ID="your-site-id"
SHAREPOINT_DRIVE_ID="your-drive-id"
SHAREPOINT_AGENTS_FOLDER_ID="your-folder-id"
MICROSOFT_GRAPH_CLIENT_ID="your-client-id"
MICROSOFT_GRAPH_CLIENT_SECRET="your-secret"
MICROSOFT_GRAPH_TENANT_ID="your-tenant-id"
EOF

# Do NOT commit .env
echo ".env" >> .gitignore
```

### 5.3 Run Dry-Run Test

```bash
# Test without uploading
python scripts/sync_agents_to_sharepoint.py --all --dry-run

# Expected output:
# [DRY RUN] Would sync agente-portos → 04_IA/.../agente-portos/SKILL.md (1.2 KB)
# [DRY RUN] Would sync agente-aeroportos → 04_IA/.../agente-aeroportos/SKILL.md (0.9 KB)
# [DRY RUN] Would sync agente-saneamento → 04_IA/.../agente-saneamento/SKILL.md (1.5 KB)
# [DRY RUN] Would sync agente-energia → 04_IA/.../agente-energia/SKILL.md (1.3 KB)
# [DRY RUN] Would sync agente-barragens → 04_IA/.../agente-barragens/SKILL.md (1.1 KB)
#
# Total: 5 agents (6.0 KB)
# Dry-run completed. No changes made.
```

### 5.4 Sync One Agent (Real)

```bash
# Start with one agent
python scripts/sync_agents_to_sharepoint.py \
  --agent agente-saneamento

# Expected output:
# ✅ Uploaded agente-saneamento/SKILL.md
# Version history: Auto-sync from local — 2026-07-25T10:30:00Z
# Size: 1.5 KB
# Location: https://manta.sharepoint.com/.../agente-saneamento/SKILL.md
```

### 5.5 Verify in SharePoint

```bash
# Check the file was uploaded
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drives/$SHAREPOINT_DRIVE_ID/root/children" | \
  jq '.value[] | select(.name == "agente-saneamento")'

# Download the file to verify
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drives/$SHAREPOINT_DRIVE_ID/items/agente-saneamento/SKILL.md/content" \
  > /tmp/skill.md

# Check content
head -20 /tmp/skill.md
```

---

## STEP 6: Deploy CI/CD Workflow (10 min)

### 6.1 Verify Workflow File

```bash
# Check workflow exists
cat .github/workflows/sync-agents-to-sharepoint.yml | head -40

# Should show:
# on:
#   push:
#     branches: [main]
#     paths: ['.claude/agents/*.md', 'CLAUDE.md']
```

### 6.2 Enable & Test Workflow

```bash
# List workflows
gh workflow list | grep sync-agents

# Enable if disabled
gh workflow enable sync-agents-to-sharepoint.yml

# Manual trigger
gh workflow run sync-agents-to-sharepoint.yml \
  -f mode=all \
  -f dry_run=false

# Monitor
gh run list --workflow=sync-agents-to-sharepoint.yml --limit=1
gh run view <run-id> --log | tail -50
```

---

## STEP 7: Test PR Auto-Sync (15 min)

### 7.1 Create Test PR with Agent Change

```bash
# Create test branch
git checkout -b test/update-agent-saneamento

# Modify an agent file
echo "# Updated $(date)" >> .claude/agents/agente-saneamento.md

# Commit and push
git add .claude/agents/agente-saneamento.md
git commit -m "test: update agent definition for sync testing"
git push -u origin test/update-agent-saneamento

# Create PR
gh pr create \
  --base main \
  --head test/update-agent-saneamento \
  --title "test: verify SharePoint sync on PR" \
  --body "Testing auto-sync workflow"
```

### 7.2 Monitor Workflow on PR

```bash
# Get PR number
PR_NUM=$(gh pr list --head test/update-agent-saneamento --json number -q .[0].number)

# Check workflow status
gh run list --workflow=sync-agents-to-sharepoint.yml --limit=3

# View PR checks
gh pr checks $PR_NUM

# Expected: Green checkmark on "sync-agents-to-sharepoint"
```

### 7.3 Verify SharePoint Update

```bash
# Check version history in SharePoint
# Navigate to: agente-saneamento/SKILL.md → Version history
# Should see: "Auto-sync from PR — 2026-07-25T..."

# Or via API:
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drives/$SHAREPOINT_DRIVE_ID/items/agente-saneamento/versions" | \
  jq '.value[0] | {id, created: .createdDateTime, lastModifiedBy: .lastModifiedBy.user.displayName}'
```

### 7.4 Clean Up Test PR

```bash
# Close test PR (don't merge)
gh pr close $PR_NUM --delete-branch

# Clean local
git checkout main
git branch -D test/update-agent-saneamento
```

---

## STEP 8: Full Sync All Agents (10 min)

### 8.1 Sync All Remaining Agents

```bash
# After dry-run passed, sync all
python scripts/sync_agents_to_sharepoint.py --all

# Expected output:
# ✅ Uploaded agente-saneamento/SKILL.md (1.5 KB)
# ✅ Uploaded agente-energia/SKILL.md (1.3 KB)
# ✅ Uploaded agente-portos/SKILL.md (1.2 KB)
# ✅ Uploaded agente-aeroportos/SKILL.md (0.9 KB)
# ✅ Uploaded agente-barragens/SKILL.md (1.1 KB)
#
# Total: 5 agents synced (6.0 KB)
# Version comment: Auto-sync from local — 2026-07-25T10:45:00Z
```

### 8.2 Verify All Files in SharePoint

```bash
# List all agent files in SharePoint
curl -s -H "Authorization: Bearer $GRAPH_TOKEN" \
  "https://graph.microsoft.com/v1.0/drives/$SHAREPOINT_DRIVE_ID/items/$AGENTS_FOLDER_ID/children" | \
  jq '.value[] | {name, size: .size, lastModified: .lastModifiedDateTime}'

# Expected:
# 5 folders (agente-*) with SKILL.md files inside
```

---

## STEP 9: Enable Production Auto-Sync (5 min)

### 9.1 Push Changes to Main

```bash
# Once everything is working, merge the branch
git checkout main
git pull origin main

# Ensure secrets are set (already done in Step 3)
gh secret list | grep SHAREPOINT
```

### 9.2 Create Production Change

```bash
# Make a real change to an agent
nano .claude/agents/agente-saneamento.md
# (Add a meaningful update)

# Commit and push
git add .claude/agents/agente-saneamento.md
git commit -m "docs: update agente-saneamento capabilities"
git push origin main

# ✅ Workflow will auto-run and sync to SharePoint!
```

### 9.3 Verify Auto-Sync

```bash
# Check workflow ran automatically
gh run list --workflow=sync-agents-to-sharepoint.yml --limit=1

# View logs
gh run view <run-id> --log | tail -20
```

---

## STEP 10: Monitoring & Maintenance (Ongoing)

### 10.1 Set Up Slack Notifications (Optional)

```bash
# Add to .github/workflows/sync-agents-to-sharepoint.yml:
# Add step after job completes:
# - name: Notify Slack
#   if: always()
#   uses: slackapi/slack-github-action@v1
#   with:
#     payload: |
#       {
#         "text": "SharePoint Sync: ${{ job.status }}",
#         ...
#       }
```

### 10.2 Monitor Sync Log

```bash
# Query sync history (in Supabase)
supabase db query << 'SQL'
SELECT 
  timestamp,
  agent_slug,
  status,
  file_size_kb,
  sync_duration_ms
FROM maestro_sharepoint_sync_log
ORDER BY timestamp DESC
LIMIT 10;
SQL

# Expected:
# timestamp              | agent_slug         | status  | file_size_kb | sync_duration_ms
# 2026-07-25 10:45:00   | agente-saneamento  | synced  | 1.5          | 234
```

### 10.3 Handle Sync Failures

If a sync fails:

```bash
# Check error in workflow logs
gh run view <run-id> --log | grep -A 10 "ERROR"

# Common issues:
# 1. Credentials expired → Re-generate client secret in Azure
# 2. Rate limit → Add retry logic (already in script)
# 3. Network → Retry manually: gh workflow run sync-agents-to-sharepoint.yml

# Re-run workflow
gh workflow run sync-agents-to-sharepoint.yml -f mode=all
```

---

## STEP 11: Documentation & Handoff (10 min)

### 11.1 Create Team Runbook

```bash
cat > docs/SHAREPOINT-SYNC-RUNBOOK.md << 'EOF'
# SharePoint Sync Runbook (Team Copy)

## Automatic Sync Schedule
- **Trigger**: Push to `.claude/agents/*.md` on main branch
- **Destination**: `/sites/manta/04_IA/01-agentes-fundamentais/`
- **Response Time**: <2 minutes
- **Owner**: DevOps (automated)

## Manual Trigger
\`\`\`bash
gh workflow run sync-agents-to-sharepoint.yml -f mode=all
\`\`\`

## Monitoring
- Logs: GitHub Actions → sync-agents-to-sharepoint.yml
- SharePoint: Version history on each SKILL.md file
- Database: maestro_sharepoint_sync_log table

## Troubleshooting
See DEPLOYMENT-PHASE-2.md → Troubleshooting section
EOF

git add docs/SHAREPOINT-SYNC-RUNBOOK.md
git commit -m "docs: add SharePoint sync runbook"
```

### 11.2 Team Notification

```bash
# Announce to team
cat << 'EOF' | mail -s "SharePoint Sync Deployed" team@company.com
✅ SharePoint Auto-Sync (Phase 2.5) Deployed

Your changes to .claude/agents/*.md are now automatically synced to SharePoint:
- Location: /sites/manta/04_IA/01-agentes-fundamentais/
- Sync time: <2 minutes after push
- Version history: Tracked in SharePoint

No manual uploads needed!

Questions? See: docs/SHAREPOINT-SYNC-RUNBOOK.md
EOF
```

---

## Success Criteria

✅ **Deployment is successful when:**
- [ ] Azure app registration created with correct permissions
- [ ] GitHub secrets configured (6 secrets)
- [ ] SharePoint folder structure created (5 agent folders)
- [ ] Dry-run test passes with all 5 agents
- [ ] One agent synced successfully (real upload)
- [ ] Workflow runs on PR changes
- [ ] Auto-sync enabled on main branch
- [ ] Team notified and trained
- [ ] Runbook updated

**Estimated Total Time**: 1.5-2 hours

---

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| "Unauthorized" error | Client secret expired. Regenerate in Azure Portal → Certificates & secrets |
| "Not found" error | SHAREPOINT_DRIVE_ID or AGENTS_FOLDER_ID incorrect. Re-verify via Graph API |
| Workflow never triggers | Check `.github/workflows/sync-agents-to-sharepoint.yml` paths match `.claude/agents/*.md` |
| Version history missing | Ensure "Version history" is enabled in SharePoint library settings |
| Rate limit error | Wait 60 seconds, then retry. Script includes backoff logic |

---

**Status**: 🟢 READY TO EXECUTE  
**Last Updated**: 2026-07-25  
**Owner**: DevOps + SharePoint Admin
