# Manta Maestro v5.0 — Secrets Rotation Policy

**Version:** v5.0  
**Last Updated:** 2026-07-25  
**Owner:** DevOps Team  
**Criticality:** P0 (Production)

---

## Overview

This document describes the **automated secrets rotation policy** for Manta Maestro v5.0, covering all critical credentials used by horizontal and vertical agents:

| Secret | Service | Rotation | Warning | Criticality |
|--------|---------|----------|---------|-------------|
| `M365_CLIENT_SECRET` | Microsoft Entra ID | 30 days | 7 days | P1 |
| `MANTAHUB_TOKEN` | MantaHub API | 30 days | 7 days | P1 |
| `SUPABASE_KEY` | Supabase Database | 60 days | 14 days | P1 |
| `MANTABASE_PASSWORD` | MantaBase PostgreSQL | 90 days | 21 days | P0 |

---

## Architecture

### Files & Components

```
Codex-exemplo/
├── scripts/
│   ├── rotate_secrets.py           ✨ Main rotation CLI
│   ├── rotation_policy.json        📋 Policy definition
│   ├── validate_secret.py          🔍 Pre-rotation validation
│   └── verify_secret.py            ✅ Post-rotation verification
├── .claude/
│   └── settings.json               ⚙️ APScheduler hooks
├── rotation_log.json               📝 Immutable audit log
├── rotation_report.json            📊 Generated reports
└── SECRETS_ROTATION_README.md      📖 This file
```

### Rotation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  APScheduler Trigger (cron: e.g., "0 2 * * 0")             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Pre-rotation hooks   │
        │ (validate_secret.py) │
        └────────┬─────────────┘
                 │ ✅ Valid?
                 ▼
        ┌──────────────────────────────────────────┐
        │ rotate_secrets.py rotate --secret <NAME> │
        │ 1. Generate new secret                   │
        │ 2. Sync to Azure Key Vault               │
        │ 3. Update environment vars               │
        │ 4. Log rotation to rotation_log.json     │
        └────────┬─────────────────────────────────┘
                 │
                 ▼
        ┌──────────────────────┐
        │ Post-rotation hooks  │
        │ (verify_secret.py)   │
        └────────┬─────────────┘
                 │ ✅ Working?
                 ▼
        ┌──────────────────────────────────────┐
        │ Slack notification                   │
        │ (#agent-ops with audit details)      │
        └──────────────────────────────────────┘
```

---

## Quick Start

### 1. Check Current Secret Status

```bash
# List recent rotations
python scripts/rotate_secrets.py list-rotations --limit 20

# Check which secrets expire soon
python scripts/rotate_secrets.py check-expiry
```

### 2. Manual Rotation (Emergency)

```bash
# Rotate a single secret
python scripts/rotate_secrets.py rotate --secret M365_CLIENT_SECRET

# Rotate all secrets
python scripts/rotate_secrets.py rotate --all
```

### 3. Generate Audit Report

```bash
# Export full rotation report
python scripts/rotate_secrets.py export-report --output rotation_report.json
```

---

## Rotation Schedule (APScheduler)

All times in **UTC**:

| Secret | Schedule | Next Run | Status |
|--------|----------|----------|--------|
| `M365_CLIENT_SECRET` | Every Sunday @ 02:00 UTC | Sun, 02:00 | ✅ Active |
| `MANTAHUB_TOKEN` | Every Monday @ 03:00 UTC | Mon, 03:00 | ✅ Active |
| `SUPABASE_KEY` | 1st & 15th @ 04:00 UTC | 1st, 04:00 | ✅ Active |
| `MANTABASE_PASSWORD` | 1st of every 3 months @ 05:00 UTC | 1st Q month, 05:00 | ✅ Active |
| **Daily expiry check** | Every day @ 07:00 UTC | Daily, 07:00 | ✅ Active |

### How to Modify Schedule

Edit `scripts/rotation_policy.json` → `scheduled_rotations`:

```json
{
  "scheduled_rotations": {
    "m365_monthly": {
      "secret_name": "M365_CLIENT_SECRET",
      "cron_expression": "0 2 * * 0",  // ← Change this
      "enabled": true
    }
  }
}
```

**Cron Format:** `minute hour day month day_of_week` (standard 5-field)

Examples:
- `0 2 * * 0` = Every Sunday at 02:00 UTC
- `0 3 * * 1` = Every Monday at 03:00 UTC
- `0 4 1,15 * *` = 1st & 15th of each month at 04:00 UTC
- `0 5 1 */3 *` = 1st of every 3rd month at 05:00 UTC

---

## Pre-rotation Validation

**Purpose:** Ensure current secret is valid before rotation.

**Runs:** Automatically before each scheduled rotation.

**What it checks:**
- M365: OAuth token exchange with Azure AD
- Supabase: API connectivity with existing key
- MantaHub: Bearer token auth with API health endpoint
- MantaBase: PostgreSQL connection

**Location:** `scripts/validate_secret.py`

**To run manually:**
```bash
python scripts/validate_secret.py
```

**Output:**
```
✓ M365_CLIENT_SECRET is valid
✓ SUPABASE_KEY is valid
✓ MANTAHUB_TOKEN is valid
✓ MANTABASE_PASSWORD is valid
```

If any validation **fails**, the rotation is **aborted** (see `pre_rotation.on_failure = "abort"` in settings.json).

---

## Post-rotation Verification

**Purpose:** Ensure new secret is working correctly after rotation.

**Runs:** Automatically after each successful rotation.

**What it checks:**
- M365: OAuth token with new secret
- Supabase: API call with new key
- MantaHub: Bearer auth with new token
- MantaBase: Database connection with new password

**Location:** `scripts/verify_secret.py`

**To run manually:**
```bash
python scripts/verify_secret.py
```

**Output:**
```
✅ New M365_CLIENT_SECRET verified and working
✅ New SUPABASE_KEY verified and working
✅ New MANTAHUB_TOKEN verified and working
✅ New MANTABASE_PASSWORD verified and working
```

If verification **fails**, a Slack alert is sent but the rotation is not rolled back (manual intervention needed).

---

## Audit Trail & Logging

### Rotation Log (`rotation_log.json`)

Every rotation is logged with:
- `secret_name` — Which secret was rotated
- `rotation_timestamp` — When (ISO 8601)
- `old_version` — Hash/ID of old secret
- `new_version` — Hash/ID of new secret
- `old_hash` — SHA256 hash of old value (non-reversible, for audit only)
- `new_hash` — SHA256 hash of new value
- `rotated_by` — User who triggered rotation
- `status` — `success`, `partial`, or `failed`
- `keyvault_sync` — Was Azure Key Vault updated?
- `slack_notified` — Were ops notified?

**Example entry:**
```json
{
  "secret_name": "M365_CLIENT_SECRET",
  "rotation_timestamp": "2026-07-25T02:15:03.123456Z",
  "old_version": "20260718010000_abc12345",
  "new_version": "20260725021503_def67890",
  "old_hash": "a3f1c8e2d4",
  "new_hash": "b2e4d7c3a1",
  "rotated_by": "maestro-v5.0",
  "status": "success",
  "keyvault_sync": true,
  "slack_notified": true
}
```

### Supabase Audit Table

Additionally, all rotations are logged to `secret_rotation_audit` table in Supabase (immutable, 365-day retention):

```sql
SELECT * FROM secret_rotation_audit
WHERE secret_name = 'M365_CLIENT_SECRET'
ORDER BY rotation_timestamp DESC
LIMIT 20;
```

---

## Notifications

### Slack Alerts

**Channel:** `#agent-ops`

**Triggered on:**
- ✅ `rotation_success` — Secret rotated, verified, synced
- ❌ `rotation_failed` — Rotation failed (action required)
- ⚠️ `expiring_soon` — Secret expiring in 7-21 days (pre-alert)

**Message format:**
```
✅ Secret rotated
Secret: M365_CLIENT_SECRET
Timestamp: 2026-07-25T02:15:03Z
Old version: 20260718010000_abc12345
New version: 20260725021503_def67890
Key Vault sync: ✅
```

### Email Alerts

**Recipients:** `devops@mantaassociados.com`, `security@mantaassociados.com`

**Triggered on:**
- ❌ `rotation_failed` — Immediate alert for manual action
- 🚨 `critical_secret_expired` — Secret is expired (past due)

---

## Azure Key Vault Integration

### Setup

1. **Prerequisites:**
   ```bash
   pip install azure-identity azure-keyvault-secrets
   az login
   ```

2. **Environment variables:**
   ```bash
   export AZURE_KEYVAULT_NAME="prod-maestro-v5"
   export AZURE_SUBSCRIPTION_ID="<your-sub-id>"
   ```

3. **Permissions:**
   Your service principal must have `Key Vault Secrets Officer` role:
   ```bash
   az role assignment create \
     --role "Key Vault Secrets Officer" \
     --assignee <principal-id> \
     --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<vault-name>
   ```

### How It Works

1. **Pre-rotation:** Current secret is read from Azure Key Vault
2. **Generation:** New secret is generated locally
3. **Sync:** New secret is uploaded to Key Vault (creates new version automatically)
4. **Environment:** New secret is loaded into process environment
5. **Audit:** Old version is archived in Key Vault (immutable history)

### Versioning

Azure Key Vault **automatically versions** secrets:
- Each `set_secret` creates a new version
- Old versions remain recoverable (kept indefinitely)
- Can rollback to any previous version via `restore_secret`

---

## Manual Rotation (Emergency)

### When to Rotate Manually

- 🚨 **Suspected compromise** — Rotate immediately
- 🚨 **Failed auto-rotation** — Manual intervention required
- 🚨 **Expiry imminent** — No automated rotation scheduled soon
- 📋 **Audit/compliance** — Forced rotation for policy compliance

### Emergency Rotation Steps

```bash
# 1. SSH to production server
ssh -i ~/.ssh/prod.pem deploy@maestro-prod.manta.local

# 2. Validate current secret works
python scripts/validate_secret.py

# 3. Rotate the secret (specify by name)
python scripts/rotate_secrets.py rotate --secret M365_CLIENT_SECRET

# 4. Verify new secret works
python scripts/verify_secret.py

# 5. Check Slack for confirmation
# (Watch #agent-ops for success/failure message)

# 6. If failed, check logs
cat rotation_log.json | tail -5 | jq '.'
```

### Rollback to Previous Secret

**If new secret doesn't work:**

```bash
# 1. List recent rotations
python scripts/rotate_secrets.py list-rotations --limit 5

# 2. Get the old version ID
# e.g., old_version: "20260718010000_abc12345"

# 3. Restore from Azure Key Vault
az keyvault secret show \
  --vault-name prod-maestro-v5 \
  --name M365_CLIENT_SECRET \
  --version <OLD_VERSION_ID>

# 4. Manually update environment variable
export M365_CLIENT_SECRET="<old-secret-value>"

# 5. Verify it works
python scripts/verify_secret.py
```

---

## Compliance & Security

### Compliance Frameworks

✅ **SOC2** — Immutable audit log, secret versioning, user attribution  
✅ **ISO 27001** — Access controls, change management, incident response  
✅ **GDPR** — Data retention policy, audit trail, consent logging

### Security Features

| Feature | Implementation |
|---------|-----------------|
| **Non-reversible hashing** | SHA256 hash of secrets (logged, not values) |
| **Immutable audit trail** | Append-only log in Supabase + Azure Key Vault |
| **User attribution** | Each rotation logged with `rotated_by` field |
| **Version control** | All secrets versioned in Key Vault (rollback possible) |
| **Pre/post validation** | Automated checks before & after rotation |
| **Slack notifications** | Real-time ops team alerts |
| **Expiry warnings** | Proactive alerts 7-21 days before expiry |
| **Tiered approval** | `MANTABASE_PASSWORD` requires human approval |

---

## Monitoring & Observability

### Metrics (Grafana Dashboard)

**Dashboard ID:** `secrets-rotation-v5`

| Metric | Alert Threshold |
|--------|-----------------|
| `rotation_duration_seconds` | > 300s = warning |
| `rotation_success_rate` | < 95% = critical |
| `keyvault_sync_latency_ms` | > 5000ms = warning |
| `slack_notification_latency_ms` | > 3000ms = warning |
| `secret_expiry_days` | < 7 days = critical |

### Logs

```bash
# View rotation log (pretty-printed)
cat rotation_log.json | jq '.'

# Filter by status
cat rotation_log.json | jq '.[] | select(.status == "failed")'

# Filter by secret
cat rotation_log.json | jq '.[] | select(.secret_name == "M365_CLIENT_SECRET")'

# Filter by date
cat rotation_log.json | jq '.[] | select(.rotation_timestamp > "2026-07-20")'
```

---

## Troubleshooting

### Rotation Failed — What To Do

1. **Check pre-rotation validation:**
   ```bash
   python scripts/validate_secret.py
   ```

2. **Check rotation log:**
   ```bash
   tail -20 rotation_log.json | jq '.'
   ```

3. **Check Slack notifications:**
   - Look in `#agent-ops` for error details

4. **Manual rollback (if needed):**
   ```bash
   # Restore previous secret from Key Vault
   az keyvault secret show --vault-name prod-maestro-v5 \
     --name M365_CLIENT_SECRET --version <OLD_VERSION>
   ```

### Azure Key Vault Sync Failed

**Symptom:** Rotation shows `success` but `keyvault_sync = false`

**Cause:** Missing `AZURE_KEYVAULT_NAME` or insufficient permissions

**Fix:**
```bash
# 1. Verify Key Vault name
echo $AZURE_KEYVAULT_NAME

# 2. Verify permissions
az keyvault secret list --vault-name prod-maestro-v5

# 3. If permission denied, request Azure admin to grant role
```

### Secret Validation Failed Before Rotation

**Symptom:** `validate_secret.py` shows ❌ for a secret

**Possible causes:**
- Current secret is corrupted/invalid
- Service (M365, Supabase, etc.) is down
- Network connectivity issue

**Fix:**
```bash
# 1. Test connectivity to service directly
curl -v https://login.microsoftonline.com/common/.well-known/openid-configuration

# 2. Verify credentials in environment
echo $M365_CLIENT_SECRET | head -c 10  # Print first 10 chars only

# 3. If service is down, wait and retry
# If credential is invalid, contact service admin
```

---

## FAQ

### Q: How long does a rotation take?

**A:** Typically 5-30 seconds depending on:
- Pre-validation (10-20s)
- Secret generation (< 1s)
- Key Vault sync (5-10s)
- Post-verification (10-20s)
- Slack notification (< 1s)

### Q: What happens if rotation fails?

**A:** 
1. Rotation is logged as `status = "failed"`
2. Slack alert sent to `#agent-ops` with error details
3. Email alert sent to DevOps + Security teams
4. **Old secret remains in use** (no breaking change)
5. Manual investigation required

### Q: Can I pause rotations?

**A:** Yes, in `.claude/settings.json` → `secrets_rotation.scheduled_tasks`:

```json
{
  "enabled": false  // ← Set to false to pause
}
```

### Q: What if I miss a rotation?

**A:** 
- Daily expiry check (`0 7 * * *`) alerts if secret is expiring
- If expiry passes, post-expiry alerts are sent
- Service will fail until secret is manually rotated

### Q: How do I rotate a compromised secret immediately?

**A:**
```bash
# Emergency rotation (bypasses validation)
python scripts/rotate_secrets.py rotate --secret <NAME> --force
```

### Q: Can I customize the rotation schedule?

**A:** Yes, edit `scripts/rotation_policy.json`:

```json
{
  "scheduled_rotations": {
    "m365_monthly": {
      "cron_expression": "0 3 * * 0"  // Change time/frequency
    }
  }
}
```

Then reload settings:
```bash
# APScheduler will pick up changes on next heartbeat
python scripts/rotate_secrets.py --reload-policy
```

---

## Support & Escalation

| Issue | Owner | Contact |
|-------|-------|---------|
| **Rotation failures** | DevOps Team | `#agent-ops` Slack |
| **Azure Key Vault issues** | Azure admin | `cloud-team@manta.local` |
| **Slack notification problems** | Platform team | `platform@manta.local` |
| **Policy changes** | Security team | `security@mantaassociados.com` |

---

## References

- **CLAUDE.md v5.0** — Master registry & architecture
- **rotation_policy.json** — Policy definition
- **settings.json** — APScheduler configuration
- **Azure Key Vault docs** — https://learn.microsoft.com/en-us/azure/key-vault/

---

**Version:** v5.0  
**Last Updated:** 2026-07-25  
**Next Review:** 2026-08-25
