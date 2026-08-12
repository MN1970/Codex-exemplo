# SharePoint Upload Manual — Manta Maestro v5.0.1

**Data:** 2026-08-03  
**Status:** 5 SKILL.md prontos + 4 docs de arquitetura prontos para upload  
**Responsável:** User/Admin SharePoint

---

## 📤 Arquivos Prontos para Upload

### **A) 5 SKILL.md (Agentes Verticais S6-S10)**

Localização em repo: `/sharepoint/01-agentes-fundamentais/agente-{x}/SKILL.md`

| Agente | Prioridade | Destino SharePoint | Status |
|--------|---|---|---|
| **agente-saneamento** | ⭐ **1** | `04_IA/01-agentes-fundamentais/agente-saneamento/` | ✅ Pronto |
| **agente-energia** | 2 | `04_IA/01-agentes-fundamentais/agente-energia/` | ✅ Pronto |
| **agente-portos** | 3 | `04_IA/01-agentes-fundamentais/agente-portos/` | ✅ Pronto |
| **agente-barragens** | 4 | `04_IA/01-agentes-fundamentais/agente-barragens/` | ✅ Pronto |
| **agente-aeroportos** | 5 | `04_IA/01-agentes-fundamentais/agente-aeroportos/` | ✅ Pronto |

**Ação:** Fazer upload via SharePoint UI ou `sp.web.folders` API (via Microsoft Graph):
```
PUT /sites/Engenharia/04_IA/01-agentes-fundamentais/agente-saneamento/SKILL.md
Content: <file content>
```

---

### **B) 4 Documentos de Arquitetura (Novo)**

Localização em repo: `/sharepoint/00-arquitetura/` e `/sharepoint/`

| Documento | Prioridade | Destino SharePoint | Ação |
|-----------|---|---|---|
| **CONSOLIDACAO-SHAREPOINT-v5.0.1.md** | 1 | `04_IA/Manta-Maestro/` | 📤 Upload |
| **ROUTING-DECISION-TREE-v5.0.1.md** | 2 | `04_IA/Manta-Maestro/00-arquitetura/` | 📤 Upload |
| **MANTA-v5.0.1-DEPLOYMENT-STATUS.md** | 3 | `04_IA/Manta-Maestro/00-arquitetura/` | 📤 Upload |
| **INDICE-CANONICAL-v5.0.md** | 4 (update) | `04_IA/Manta-Maestro/00-arquitetura/` | 🔄 Atualizar (adicionar v5.0.1 status) |

**Ação:** Upload similar, pasta destino é `Manta-Maestro/00-arquitetura/`

---

## 🔧 Instruções de Upload

### **Opção 1: SharePoint UI (Manual)**

1. Abra: `https://mnassociados.sharepoint.com/sites/Engenharia`
2. Navegue a: `04_IA → 01-agentes-fundamentais → agente-saneamento/`
3. Clique **+ Add file** ou **Upload**
4. Selecione `/sharepoint/01-agentes-fundamentais/agente-saneamento/SKILL.md` do seu computador
5. Confirme upload (sobrescrever se já existe)
6. Repita para os outros 4 agentes e 4 docs

**Tempo estimado:** 10 minutos (5 files + 4 docs)

### **Opção 2: Microsoft Graph API (Automatizado)**

```powershell
# PowerShell script para upload batch
$siteURL = "https://mnassociados.sharepoint.com/sites/Engenharia"
$accessToken = "<seu_token_Graph>"

$files = @(
    @{file="/sharepoint/01-agentes-fundamentais/agente-saneamento/SKILL.md"; folder="04_IA/01-agentes-fundamentais/agente-saneamento"},
    @{file="/sharepoint/01-agentes-fundamentais/agente-energia/SKILL.md"; folder="04_IA/01-agentes-fundamentais/agente-energia"},
    # ... mais 3 agentes + 4 docs
)

foreach ($item in $files) {
    $fileContent = [System.IO.File]::ReadAllBytes($item.file)
    $fileName = Split-Path $item.file -Leaf
    
    $uri = "$siteURL/Documentos/$($ item.folder)/:/$fileName"
    
    Invoke-WebRequest -Uri $uri -Method PUT -Headers @{"Authorization" = "Bearer $accessToken"} -InFile $item.file
}
```

### **Opção 3: MCP SharePoint (Código)**

```python
# Python com requests + MCP
import requests
import base64

files = {...}  # dict com path + destino
graph_token = "<seu_token>"

for file_info in files:
    with open(file_info['path'], 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    
    # Use MCP upload_file com content_b64
    # mcp_upload(library="04_IA", folder_path=file_info['folder'], 
    #           file_name="SKILL.md", content_b64=content)
```

---

## 📋 Checklist de Upload

### Fase 1: Upload 5 SKILL.md (S6-S10)

- [ ] agente-saneamento/SKILL.md → `04_IA/01-agentes-fundamentais/agente-saneamento/`
- [ ] agente-energia/SKILL.md → `04_IA/01-agentes-fundamentais/agente-energia/`
- [ ] agente-portos/SKILL.md → `04_IA/01-agentes-fundamentais/agente-portos/`
- [ ] agente-barragens/SKILL.md → `04_IA/01-agentes-fundamentais/agente-barragens/`
- [ ] agente-aeroportos/SKILL.md → `04_IA/01-agentes-fundamentais/agente-aeroportos/`

### Fase 2: Upload 4 Docs de Arquitetura

- [ ] CONSOLIDACAO-SHAREPOINT-v5.0.1.md → `04_IA/Manta-Maestro/`
- [ ] ROUTING-DECISION-TREE-v5.0.1.md → `04_IA/Manta-Maestro/00-arquitetura/`
- [ ] MANTA-v5.0.1-DEPLOYMENT-STATUS.md → `04_IA/Manta-Maestro/00-arquitetura/`
- [ ] INDICE-CANONICAL-v5.0.md (atualizar com v5.0.1 status) → `04_IA/Manta-Maestro/00-arquitetura/`

### Fase 3: Criar Pasta 02-agentes-horizontais (depois de SKILL.md horizontais prontos)

- [ ] Criar pasta `02-agentes-horizontais` em `04_IA/`
- [ ] Criar 11 subpastas (agente-claims, agente-contratual, ..., agente-arquiteto-ia)
- [ ] Upload 11 SKILL.md horizontais quando prontos

---

## 🔗 Referências & Documentação

- **CONSOLIDACAO-SHAREPOINT-v5.0.1.md** — Mapa completo de consolidação
- **ROUTING-DECISION-TREE-v5.0.1.md** — Decisões de roteamento por agente
- **MANTA-v5.0.1-DEPLOYMENT-STATUS.md** — Status operacional e SLA
- **INDICE-CANONICAL-v5.0.md** — Canonical reference (4 eixos, 11 segmentos)

---

## ✅ Próximas Ações Após Upload

1. **Validar** que todos os 5 SKILL.md aparecem em `01-agentes-fundamentais` no SP
2. **Aguardar** conclusão dos 11 SKILL.md horizontais (Agent B rodando)
3. **Criar** pasta `02-agentes-horizontais` e upload dos 11 agentes
4. **Publicar** 4 novos docs de arquitetura em `Manta-Maestro/00-arquitetura/`
5. **Atualizar** INDICE-CANONICAL com status v5.0.1 (17 agentes live)
6. **Decisões MN:** S12/S13 gate, embedder confirmação, RLS security

---

**Status:** Prontos para upload imediato  
**Data limite recomendada:** 2026-08-05 (dentro de 2 dias)

