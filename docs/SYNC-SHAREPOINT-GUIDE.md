# Guide — Sincronizar SharePoint + Auditoria Automática

## Situação Atual

✅ **Script de auditoria criado**: `/scripts/audit_sharepoint_projects.py`
- Detecta estrutura `03_Projetos/{segmento}/`
- Cataloga arquivos por categoria
- Gera relatórios: CSV, JSON, Markdown
- Estima chunks RAG potenciais

❌ **Status**: Pasta `03_Projetos` vazia no local (0 arquivos encontrados)

---

## OPÇÃO 1: Sincronizar SharePoint Completo (Recomendado)

### Usando rclone (Síncrono):

```bash
# 1. Instalar rclone (se não tiver)
curl https://rclone.org/install.sh | sudo bash

# 2. Configurar acesso a SharePoint
rclone config

# Siga os prompts:
#   - Name: sharepoint
#   - Storage: Microsoft SharePoint
#   - Use interactive login: yes
#   - Tenant ID: [você terá que fornecer - está em Azure AD]
#   - Site URL: https://mnassociados.sharepoint.com/sites/Engenharia

# 3. Sincronizar pasta Documentos Compartilhados
rclone sync sharepoint:'/Documentos Compartilhados/03_Projetos' \
  /home/user/Codex-exemplo/sharepoint/03_Projetos \
  --progress

# 4. Rodar auditoria
python3 /home/user/Codex-exemplo/scripts/audit_sharepoint_projects.py
```

---

## OPÇÃO 2: Usar Microsoft Graph API (Alternativa)

```bash
# 1. Instalar bibliotecas Python
pip install msgraph-core azure-identity requests

# 2. Criar arquivo /home/user/Codex-exemplo/scripts/sync_sharepoint_graph.py
# (vou criar abaixo)

python3 /home/user/Codex-exemplo/scripts/sync_sharepoint_graph.py
```

---

## OPÇÃO 3: OneDrive Sync (Manual, Desktop App)

Se você tem OneDrive Desktop instalado:

1. Abrir OneDrive Desktop
2. Navegar para `Sites > Engenharia > Documentos Compartilhados`
3. Clicar "Sync"
4. Selecionar pasta local: `/home/user/Codex-exemplo/sharepoint`
5. Esperar sync completar (pode levar 5-10 min dependendo do volume)
6. Rodar script: `python3 /scripts/audit_sharepoint_projects.py`

---

## OPÇÃO 4: Export Manual (via SharePoint Web)

Se não conseguir via automação:

1. Ir para `https://mnassociados.sharepoint.com/sites/Engenharia`
2. Navegar para `Documentos Compartilhados > 03_Projetos`
3. Selecionar todas as pastas (S1-S10)
4. Clicar "Download"
5. Descompactar em `/home/user/Codex-exemplo/sharepoint/03_Projetos/`
6. Rodar script: `python3 /scripts/audit_sharepoint_projects.py`

---

## ⚡ Quick Start (Desktop Commander)

Se você usar **Desktop Commander** ou **Total Commander**:

```
1. Abrir Desktop Commander
2. Painel esquerdo: navegar para https://mnassociados.sharepoint.com/sites/Engenharia
3. Painel direito: /home/user/Codex-exemplo/sharepoint/03_Projetos
4. Drag-drop: 03_Projetos > Desktop Commander (sincroniza)
5. Terminal: python3 /scripts/audit_sharepoint_projects.py
```

---

## Após Sincronizar: Rodar Auditoria

```bash
cd /home/user/Codex-exemplo

# Executar script
python3 scripts/audit_sharepoint_projects.py

# Resultados:
# - docs/rag-sources/AUDIT-SHAREPOINT.csv
# - docs/rag-sources/AUDIT-SHAREPOINT.json
# - docs/rag-sources/AUDIT-CONSOLIDADO.md
```

---

## Interpretar Resultados

### CSV (`AUDIT-SHAREPOINT.csv`)

| Segmento | Nome | Status | Arquivos | RAG Chunks | Proj | Norm | Est | Tmpl |
|----------|------|--------|----------|------------|------|------|-----|------|
| S1 | Rodovias | OK | 32 | 420 | 5 | 8 | 12 | 3 |
| S2 | OAE | OK | 18 | 280 | 3 | 6 | 7 | 2 |
| ... | | | | | | | | |

**Colunas**:
- **Arquivos**: total de arquivos encontrados
- **RAG Chunks**: estimativa de chunks para ingestion
- **Proj/Norm/Est/Tmpl**: contagem por categoria

### JSON (`AUDIT-SHAREPOINT.json`)

Incluem:
- Detalhes completos por arquivo
- Path relativo no SP
- Tamanho individual
- Data de modificação
- Categorização automática

### Markdown (`AUDIT-CONSOLIDADO.md`)

Human-friendly:
- Resumo geral
- Tabela comparativa
- Detalhes por segmento
- Listas de arquivos principais

---

## Script de Sync Automático (Microsoft Graph API)

Se quiser automação contínua:

```python
# Criar arquivo: /home/user/Codex-exemplo/scripts/sync_sharepoint_graph.py

import requests
from azure.identity import DeviceFlowCredential
from pathlib import Path
import json

# Credenciais (você terá que configurar)
TENANT_ID = "seu-tenant-id"
CLIENT_ID = "seu-client-id"
SITE_ID = "seu-site-id"

credential = DeviceFlowCredential(client_id=CLIENT_ID, tenant_id=TENANT_ID)
token = credential.get_token("https://graph.microsoft.com/.default")

# Baixar arquivos recursivamente
headers = {"Authorization": f"Bearer {token.token}"}
url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drive/root/children"

response = requests.get(url, headers=headers)
print(json.dumps(response.json(), indent=2))
```

---

## Troubleshooting

### "Pasta 03_Projetos não existe"

**Solução**: O SP local ainda não foi sincronizado. Use uma das 4 opções acima.

### "Certificado SSL inválido"

**Solução**:
```bash
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt
python3 scripts/audit_sharepoint_projects.py
```

### "Permission denied"

**Solução**: Certificar que você tem permissão para ler SharePoint.
```bash
ls -la /home/user/Codex-exemplo/sharepoint/03_Projetos/
chmod -R 755 /home/user/Codex-exemplo/sharepoint/
```

---

## Próximos Passos (Após Auditoria)

1. **Revisar AUDIT-CONSOLIDADO.md** — ver quantos arquivos por segmento
2. **Identificar TIER 1 (normas)** — PDFs de DNIT, ABNT, ANEEL, etc
3. **Exportar normas** — copiar PDFs para `/docs/rag-sources/{segmento}/`
4. **Rodar ingestion** — `scripts/ingest_rag_batch.py` (Fase 1.1.3)
5. **Validar chunks** — conferir se foram processados corretamente

---

## Script para Automatizar Tudo (One-Liner)

```bash
# Sync + Audit + Gerar relatório (tudo de uma vez)
rclone sync sharepoint:'/Documentos Compartilhados/03_Projetos' \
  /home/user/Codex-exemplo/sharepoint/03_Projetos \
  --progress && \
python3 /home/user/Codex-exemplo/scripts/audit_sharepoint_projects.py && \
echo "✅ Done! Check docs/rag-sources/AUDIT-CONSOLIDADO.md"
```

---

## Contato / Suporte

Se tiver dúvidas durante a sync:
1. Rodar: `python3 scripts/audit_sharepoint_projects.py --debug`
2. Enviar: `docs/rag-sources/AUDIT-SHAREPOINT.json` para revisão
3. MN pode revisar estrutura em SP e confirmar se está tudo sincronizado
