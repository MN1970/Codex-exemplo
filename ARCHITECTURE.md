# sp_healthcheck.py v2 — Architecture & Data Flow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                   Claude Code SessionStart Hook                 │
│                                                                 │
│  python scripts/sp_healthcheck.py --verbose > .healthcheck.json│
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   sp_healthcheck.py (main)     │
        │                                │
        │  1. Parse CLI arguments        │
        │  2. Validate environment       │
        │  3. Call get_healthcheck_status│
        │  4. Output JSON + exit code    │
        └────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────────┐
    │   get_healthcheck_status() [3 steps]   │
    └─────────────┬────────────────────────┬─┘
                  │                        │
       ┌──────────▼──────────┐  ┌──────────▼──────────┐
       │ STEP 1/3: Azure AD  │  │ STEP 2/3: SP Write │
       │  Token Acquisition  │  │  Test              │
       └──────────┬──────────┘  └──────────┬──────────┘
                  │                        │
    ┌─────────────▼──────────┐  ┌──────────▼──────────┐
    │ get_azure_ad_token()   │  │test_sharepoint_write│
    │ @retry_with_backoff    │  │ @retry_with_backoff │
    │ [max_attempts=3]       │  │ [max_attempts=3]    │
    └─────────────┬──────────┘  └──────────┬──────────┘
                  │                        │
    ┌─────────────▼──────────┐  ┌──────────▼──────────┐
    │ POST to Azure AD       │  │ SharePoint REST API │
    │ Endpoint:              │  │ /_api/web/lists/    │
    │ login.microsoftonline  │  │ getbytitle()        │
    │ .com/{tenant_id}/      │  │                     │
    │ oauth2/v2.0/token      │  │ /_api/.../          │
    │                        │  │ files/add()         │
    │ Returns:               │  │                     │
    │ - access_token         │  │ Writes to:          │
    │ - expires_in (seconds) │  │ 04_IA/Manta-Maestro/│
    │                        │  │ _healthcheck/       │
    │                        │  │ test.txt            │
    │                        │  │                     │
    │ Retry: 1s → 2s → 4s    │  │ Retry: 1s → 2s → 4s │
    └─────────────┬──────────┘  └──────────┬──────────┘
                  │                        │
                  └────────────┬───────────┘
                               │
                       ┌───────▼────────┐
                       │ STEP 3/3:      │
                       │ Key Vault      │
                       │ Secret Check   │
                       └───────┬────────┘
                               │
            ┌──────────────────▼──────────────────┐
            │get_vault_secret_expiry()            │
            │ @retry_with_backoff                 │
            │ [max_attempts=3]                    │
            └──────────────────┬──────────────────┘
                               │
            ┌──────────────────▼──────────────────┐
            │ GET to Azure Key Vault               │
            │ Endpoint:                            │
            │ https://{vault_name}.vault.azure.net │
            │ /secrets/{secret_name}               │
            │ ?api-version=7.4                     │
            │                                      │
            │ Returns:                             │
            │ - attributes.expires (Unix timestamp)│
            │ - Calculate days until expiration    │
            │ - Warn if < 30 days                  │
            │                                      │
            │ Retry: 1s → 2s → 4s                 │
            └──────────────────┬──────────────────┘
                               │
                       ┌───────▼────────┐
                       │ Aggregate      │
                       │ results        │
                       └───────┬────────┘
                               │
                       ┌───────▼────────┐
                       │ Determine      │
                       │ final status:  │
                       │ ok|warning|err │
                       └───────┬────────┘
                               │
                       ┌───────▼────────┐
                       │ Output JSON    │
                       │ + logger info  │
                       └───────┬────────┘
                               │
                       ┌───────▼────────┐
                       │ Exit code:     │
                       │ 0 or 1         │
                       └────────────────┘
```

---

## Retry Logic with Exponential Backoff

```
Attempt 1                  Attempt 2                  Attempt 3
┌────────────┐  [FAIL]     ┌────────────┐  [FAIL]     ┌────────────┐
│ HTTP POST  │ ─────────►  │ HTTP POST  │ ─────────►  │ HTTP POST  │
│ Timeout    │   sleep 1s  │ Timeout    │   sleep 2s  │ Timeout    │
└────────────┘             └────────────┘             └────────────┘
                           [LOG WARN]                 [LOG ERROR]
                    "Retrying in 1.0s..."       "Failed after 3 attempts"

Total time: 1s + 2s = 3 seconds (+ HTTP request times)
Max wait before giving up: ~15 seconds (with timeouts)
```

---

## HTTP Request Flow

```
CLIENT (sp_healthcheck.py)
    │
    ├─ HTTP Request to Azure AD ───────────────────────────────────────┐
    │  POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
    │  Payload: grant_type, client_id, client_secret, scope
    │  Timeout: 10 seconds
    │                                                                   │
    │  ◄────────────────────────────────────────────────────────────────┤
    │  Response: {"access_token": "...", "expires_in": 3600, ...}      │
    │                                                                   │
    ├─ HTTP GET to SharePoint REST API (get list) ─────────────────────┐
    │  GET https://{tenant}.sharepoint.com/sites/{site}/_api/web/     │
    │      lists/getbytitle('{list}')                                  │
    │  Headers: Authorization: Bearer {access_token}                   │
    │                                                                   │
    │  ◄────────────────────────────────────────────────────────────────┤
    │  Response: {"d": {"Id": "...", ...}}                             │
    │                                                                   │
    ├─ HTTP GET to SharePoint REST API (get folder) ───────────────────┐
    │  GET https://{tenant}.sharepoint.com/sites/{site}/_api/web/     │
    │      getfolderbyserverrelativeurl('{folder_path}')              │
    │  Headers: Authorization: Bearer {access_token}                   │
    │                                                                   │
    │  ◄────────────────────────────────────────────────────────────────┤
    │  Response: {"d": {...folder metadata...}}                        │
    │                                                                   │
    ├─ HTTP POST to SharePoint REST API (add file) ─────────────────────┐
    │  POST https://{tenant}.sharepoint.com/sites/{site}/_api/web/    │
    │       getfolderbyserverrelativeurl('{folder}')/files/           │
    │       add(url='test.txt',overwrite=true)                         │
    │  Headers: Authorization: Bearer {access_token}                   │
    │           Content-Type: text/plain                               │
    │  Body: "Healthcheck OK at 2026-07-25T10:30:00+00:00\n"          │
    │                                                                   │
    │  ◄────────────────────────────────────────────────────────────────┤
    │  Response: {"d": {"UniqueId": "...", ...}}                       │
    │                                                                   │
    ├─ HTTP GET to Azure Key Vault ──────────────────────────────────────┐
    │  GET https://{vault_name}.vault.azure.net/secrets/{secret}      │
    │      ?api-version=7.4                                            │
    │  Headers: Authorization: Bearer {access_token}                   │
    │                                                                   │
    │  ◄────────────────────────────────────────────────────────────────┤
    │  Response: {"attributes": {"expires": 1788796800, ...}}          │
    │            (Unix timestamp = 2026-07-25)                         │
```

---

## Data Flow - JSON Output Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Input: Environment + CLI Args                               │
├─────────────────────────────────────────────────────────────┤
│ AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SHAREPOINT_TENANT_ID │
│ --verbose, --dry-run, etc.                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  get_healthcheck_status()      │
        │                                │
        │  Collects:                     │
        │  • token validity (Y/N)        │
        │  • token expires in X days     │
        │  • SP write timestamp or null  │
        │  • SP write success (Y/N)      │
        │  • KV accessible (Y/N)         │
        │  • KV secret expires in X days │
        │  • errors array                │
        │  • final status (ok/warn/err)  │
        └────────────────┬───────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │  JSON Output Structure                 │
    ├────────────────────────────────────────┤
    │ {                                      │
    │   "status": "ok",                      │
    │   "timestamp": "2026-07-25T...",       │
    │   "token_valid": true,                 │
    │   "token_expires_in_days": 27,         │
    │   "last_write_at": "2026-07-25T...",   │
    │   "sharepoint_writable": true,         │
    │   "vault_accessible": true,            │
    │   "vault_secret_expires_in_days": 150, │
    │   "errors": []                         │
    │ }                                      │
    └────────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────┐
    │  Exit Code (0=ok, 1=error/warning)     │
    │                                        │
    │  status == "ok" ──────► exit 0         │
    │  status != "ok" ──────► exit 1         │
    └────────────────────────────────────────┘
```

---

## Component Dependencies

```
sp_healthcheck.py
├── Python Standard Library
│   ├── sys
│   ├── os
│   ├── json
│   ├── logging
│   ├── argparse
│   ├── datetime
│   ├── typing
│   ├── traceback
│   ├── time
│   └── functools
│
└── External Dependencies
    └── requests (HTTP client)
        ├── for Azure AD token acquisition
        ├── for SharePoint REST API calls
        └── for Azure Key Vault API calls

Internal Functions:
├── retry_with_backoff()
│   └── Decorator for retry logic with exponential backoff
│
├── parse_args()
│   └── CLI argument parsing
│
├── get_azure_ad_token() [decorated]
│   └── OAuth2 client credentials flow
│
├── test_sharepoint_write() [decorated]
│   └── SharePoint REST API write test
│
├── get_vault_secret_expiry() [decorated]
│   └── Azure Key Vault secret metadata query
│
├── get_healthcheck_status()
│   └── Main orchestration function (3 steps)
│
└── main()
    └── Entry point, output JSON, exit code
```

---

## Error Handling Strategy

```
Exception Type          │ Handler              │ Retry?  │ Exit Code
────────────────────────┼──────────────────────┼─────────┼──────────
HTTP Timeout            │ retry_with_backoff   │ Yes (3) │ 1
HTTP 401 Unauthorized   │ retry_with_backoff   │ Yes (3) │ 1
HTTP 404 Not Found      │ retry_with_backoff   │ Yes (3) │ 1
HTTP 500 Server Error   │ retry_with_backoff   │ Yes (3) │ 1
Invalid JSON Response   │ ValueError raised    │ Yes (3) │ 1
Missing Access Token    │ ValueError raised    │ Yes (3) │ 1
Missing Credentials     │ Early return, error  │ No      │ 1
Network Unreachable     │ ConnectionError      │ Yes (3) │ 1
SSL Certificate Error   │ SSLError (fail fast) │ No      │ 1
Timeout (10s/request)   │ requests timeout     │ Yes (3) │ 1
────────────────────────┴──────────────────────┴─────────┴──────────

Legend:
  Retry? = @retry_with_backoff decorator applies?
  Exit Code = Final process exit code (0 or 1)
```

---

## Logging Levels

```
DEBUG Level (-v flag)
├── Function entry/exit with parameters
├── HTTP request details (URL, method, headers)
├── Token expiration calculations
├── Retry delay calculations
└── Full stack traces on error

INFO Level (default)
├── Step 1/3, 2/3, 3/3 progress
├── Azure AD token acquired successfully
├── SharePoint write success + timestamp
├── Key Vault accessible + days to expiry
├── Healthcheck completed with final status

WARNING Level
├── Failed attempts (1/3, 2/3)
├── Non-critical component failures
├── Secret expiring soon (< 30 days)
└── Retry delays before next attempt

ERROR Level
├── Critical failures (Azure AD, SharePoint)
├── Permanent failures after 3 retries
├── Missing credentials
└── Unhandled exceptions
```

---

## Performance Timeline

```
Time    Component           Action                    Duration
────────────────────────────────────────────────────────────────
0ms     Client              Spawn process
5ms     Main                Parse args
10ms    Config              Validate credentials      ✓
20ms    Azure AD            HTTP POST request         50-100ms
120ms   SharePoint (list)   HTTP GET list             50-200ms
170ms   SharePoint (folder) HTTP GET folder           50-200ms
220ms   SharePoint (write)  HTTP POST file            100-300ms
320ms   Key Vault           HTTP GET secret           100-200ms
420ms   Aggregate           Build JSON + status       5-10ms
430ms   Output              Print JSON to stdout      1-2ms
432ms   Exit                Return exit code (0 or 1) 0ms
────────────────────────────────────────────────────────────────
Total: ~430ms (with optimal network)
Max: ~15s (with 3x retries + timeouts)
```

---

## Environment & Credentials

```
Required Environment Variables:
├── AZURE_CLIENT_ID              → Azure AD App Registration Client ID
├── AZURE_CLIENT_SECRET          → Azure AD App Registration Secret
└── SHAREPOINT_TENANT_ID         → Azure Tenant ID (UUID)

Optional Environment Variables:
├── SHAREPOINT_TENANT_NAME       → URL tenant name (default: mantaassociados)
├── SHAREPOINT_SITE_NAME         → SP site name (default: manta-maestro)
├── AZURE_KEYVAULT_NAME          → Key Vault name (default: manta-maestro-vault)
└── AZURE_SECRET_NAME            → Secret name to monitor (default: manta-maestro-credentials)

Scope Requirements (for Azure AD App Registration):
├── Microsoft Graph API
│   └── .default scope (grants all permissions)
├── SharePoint Online
│   └── Sites.ReadWrite.All (or similar)
└── Azure Key Vault
    └── Get on secrets (get secret attributes)
```

---

## Session Hook Integration

```
Claude Code Runner
    │
    ├─ SessionStart Event ─────────────────────────────┐
    │                                                   │
    │  Execute hook command:                           │
    │  python scripts/sp_healthcheck.py --verbose      │
    │                                                   │
    │  Capture output to:                              │
    │  .healthcheck.json                               │
    │                                                   │
    │  Check exit code:                                │
    │  0 → silent (all good)                           │
    │  1 → warn (issue detected)                       │
    │                                                   │
    └───► .healthcheck.json                            │
          {                                             │
            "status": "ok|error|warning",               │
            "timestamp": "...",                         │
            "errors": [...]                             │
          }                                             │
          └──► Available for logging/alerts            │
               in subsequent session operations
```

---

**Architecture Version**: v2 (2026-07-25)  
**Last Updated**: 2026-07-25
