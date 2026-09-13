# sp_healthcheck.py — Setup e Integração

## Overview

`scripts/sp_healthcheck.py` (v2) é um script robusto de healthcheck para validação de:

1. **Azure AD Token** — OAuth2 client credentials flow
2. **SharePoint Write** — Teste de escrita em `04_IA/Manta-Maestro/_healthcheck/test.txt`
3. **Azure Key Vault** — Dias até expiração do secret
4. **Retry Logic** — 3 tentativas com backoff exponencial
5. **Exit Codes** — 0 (ok) / 1 (error ou warning)

Output: JSON estruturado com status, timestamps, e detalhes de erro.

---

## Instalação de Dependências

```bash
pip install requests
```

---

## Variáveis de Ambiente Necessárias

Configure as seguintes variáveis antes de executar:

```bash
# Azure AD (obrigatório)
export AZURE_CLIENT_ID="<app-registration-client-id>"
export AZURE_CLIENT_SECRET="<app-registration-client-secret>"
export SHAREPOINT_TENANT_ID="<tenant-uuid>"

# SharePoint (opcional, valores padrão mostrados)
export SHAREPOINT_TENANT_NAME="mantaassociados"  # Nome curto do tenant (URL)
export SHAREPOINT_SITE_NAME="manta-maestro"       # Nome do site SP

# Azure Key Vault (opcional, valores padrão mostrados)
export AZURE_KEYVAULT_NAME="manta-maestro-vault"
export AZURE_SECRET_NAME="manta-maestro-credentials"
```

---

## Uso

### Modo Normal (com escrita em SharePoint)

```bash
python scripts/sp_healthcheck.py --verbose > /tmp/healthcheck.json
echo $?  # Exit code: 0 (ok) ou 1 (error/warning)
```

### Modo Dry-Run (validação apenas, sem escrita)

```bash
python scripts/sp_healthcheck.py --dry-run --verbose
```

### Com argumentos customizados

```bash
python scripts/sp_healthcheck.py \
  --sharepoint-tenant "your-tenant-id" \
  --sharepoint-site "your-site-name" \
  --vault-name "your-vault" \
  --secret-name "your-secret" \
  --verbose
```

---

## Output JSON

Exemplo de resposta bem-sucedida:

```json
{
  "status": "ok",
  "timestamp": "2026-07-25T10:30:00+00:00",
  "token_valid": true,
  "token_expires_in_days": 27,
  "last_write_at": "2026-07-25T10:30:15+00:00",
  "sharepoint_writable": true,
  "vault_accessible": true,
  "vault_secret_expires_in_days": 150,
  "errors": []
}
```

Exemplo com warnings (secret expirando em < 30 dias):

```json
{
  "status": "warning",
  "timestamp": "2026-07-25T10:30:00+00:00",
  "token_valid": true,
  "token_expires_in_days": 27,
  "last_write_at": "2026-07-25T10:30:15+00:00",
  "sharepoint_writable": true,
  "vault_accessible": true,
  "vault_secret_expires_in_days": 20,
  "errors": [
    {
      "component": "keyvault",
      "message": "Secret expiring soon: 20 days",
      "timestamp": "2026-07-25T10:30:00+00:00"
    }
  ]
}
```

Exemplo com erro crítico:

```json
{
  "status": "error",
  "timestamp": "2026-07-25T10:30:00+00:00",
  "token_valid": false,
  "token_expires_in_days": -1,
  "last_write_at": null,
  "sharepoint_writable": false,
  "vault_accessible": false,
  "vault_secret_expires_in_days": null,
  "errors": [
    {
      "component": "azure_ad",
      "message": "Invalid client credentials",
      "timestamp": "2026-07-25T10:30:00+00:00"
    }
  ]
}
```

---

## Integração com SessionStart Hook

Para rodar este script automaticamente a cada sessão, configure `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": {
      "description": "Run M365 healthcheck on session start",
      "command": "python scripts/sp_healthcheck.py --verbose > .healthcheck.json",
      "on_exit_code": {
        "0": "silent",
        "1": "warn"
      }
    }
  }
}
```

Ou, com verificação mais rigorosa:

```json
{
  "hooks": {
    "SessionStart": {
      "command": "bash -c 'python scripts/sp_healthcheck.py --verbose > .healthcheck.json && exit 0 || (cat .healthcheck.json && exit 1)'",
      "on_exit_code": {
        "1": "error"
      }
    }
  }
}
```

---

## Características Implementadas

### 1. Retry Logic com Backoff Exponencial

- **3 tentativas** por componente (Azure AD, SharePoint, Key Vault)
- **Delay inicial**: 1 segundo
- **Backoff factor**: 2x (1s → 2s → 4s)
- **Timeout**: 10 segundos por requisição HTTP

```python
@retry_with_backoff(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
def get_azure_ad_token(...):
    ...
```

### 2. Azure AD OAuth2 Client Credentials Flow

- Solicita token via `POST https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`
- Scope: `https://graph.microsoft.com/.default`
- Retorna `expires_in` (segundos) → convertido para dias
- Decorado com `@retry_with_backoff`

### 3. SharePoint REST API Write Test

- Lista API: `/_api/web/lists/getbytitle('{list_title}')`
- Folder API: `/_api/web/getfolderbyserverrelativeurl('{folder_path}')`
- File Add: `/_api/.../files/add(url='{file_name}',overwrite=true)`
- Cria arquivo `test.txt` com timestamp UTC
- Modo dry-run salta escrita (valida token apenas)

### 4. Azure Key Vault REST API

- REST endpoint: `https://{vault_name}.vault.azure.net/secrets/{secret_name}?api-version=7.4`
- Extrai `attributes.expires` (Unix timestamp)
- Calcula `expires_in_days` = (expires_at - now).days
- **Warning** se < 30 dias até expiração

### 5. Logging Estruturado

- **INFO**: steps principais, sucesso
- **WARNING**: tentativas, secret expirando, componentes não-críticos
- **ERROR**: falhas críticas, stack trace em DEBUG mode
- Formatado: `timestamp [LEVEL] logger: message`

### 6. JSON Output Estruturado

Campo | Tipo | Descrição
------|------|----------
`status` | str | "ok" \| "error" \| "warning"
`timestamp` | ISO8601 | UTC ISO string
`token_valid` | bool | Azure AD token válido?
`token_expires_in_days` | int | Dias até expiração (ou -1 se erro)
`last_write_at` | ISO8601 \| null | Timestamp da escrita no SP
`sharepoint_writable` | bool | SP escreve corretamente?
`vault_accessible` | bool | Key Vault acessível?
`vault_secret_expires_in_days` | int \| null | Dias até expiração do secret
`errors` | array | List of {component, message, timestamp}

### 7. Exit Codes

- **0**: `status == "ok"`
- **1**: `status == "error"` ou `status == "warning"`

---

## Troubleshooting

### "requests module not found"

```bash
pip install requests
```

### "Missing AZURE_CLIENT_ID or AZURE_CLIENT_SECRET"

```bash
export AZURE_CLIENT_ID="..."
export AZURE_CLIENT_SECRET="..."
export SHAREPOINT_TENANT_ID="..."
```

### "No access_token in response"

Verifique:
- `AZURE_CLIENT_ID` e `AZURE_CLIENT_SECRET` estão corretos
- App registration tem permissões Graph API
- Tenant ID está correto

### "SharePoint write test: HTTP 401 Unauthorized"

- Token expirou (retry logic vai tentar 3x)
- Permissões insuficientes (app registration precisa de SharePoint Contributor)
- Site ou pasta não existe

### "Azure Key Vault: Secret has no expiration date set"

Configure expiração do secret no Key Vault:

```bash
az keyvault secret set --vault-name "manta-maestro-vault" \
  --name "manta-maestro-credentials" \
  --value "..." \
  --expires $(date -d "+1 year" +%s)
```

---

## Exemplo de Uso em CI/CD

### GitHub Actions

```yaml
name: M365 Healthcheck

on: [schedule: ["0 * * * *"]]  # Hourly

jobs:
  healthcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install requests
      - run: python scripts/sp_healthcheck.py --verbose
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          SHAREPOINT_TENANT_ID: ${{ secrets.SHAREPOINT_TENANT_ID }}
      - name: Alert on failure
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const result = JSON.parse(fs.readFileSync('.healthcheck.json', 'utf8'));
            core.setFailed(`Healthcheck failed: ${result.status}\n${JSON.stringify(result.errors)}`);
```

### SystemD Timer (Linux)

`/etc/systemd/system/manta-healthcheck.service`:
```ini
[Unit]
Description=Manta M365 Healthcheck
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/home/user/Codex-exemplo
ExecStart=/usr/bin/python3 scripts/sp_healthcheck.py --verbose
Environment="AZURE_CLIENT_ID=..."
Environment="AZURE_CLIENT_SECRET=..."
Environment="SHAREPOINT_TENANT_ID=..."
StandardOutput=journal
StandardError=journal
```

`/etc/systemd/system/manta-healthcheck.timer`:
```ini
[Unit]
Description=Run Manta M365 Healthcheck hourly

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
```

```bash
sudo systemctl enable manta-healthcheck.timer
sudo systemctl start manta-healthcheck.timer
journalctl -u manta-healthcheck.service -f
```

---

## Performance

- **Azure AD token**: ~50-100ms (com cache possível)
- **SharePoint write**: ~200-500ms (depende do tenant)
- **Key Vault query**: ~100-200ms
- **Total (sucesso)**: ~400-800ms + retries se necessário
- **Timeout total**: 30s (10s × 3 componentes)

---

## Roadmap

- [ ] Implementar caching de token em arquivo local (~/.manta_token)
- [ ] Suporte a MSI (Managed Identity) no Azure
- [ ] Integração com Slack para alertas
- [ ] Dashboard Prometheus metrics export
- [ ] Suporte a proxy HTTPS customizado

---

**Versão**: v2 (2026-07-25)  
**Status**: Pronto para produção  
**Autor**: Manta Maestro (M365 Integration Team)
