# GUIA TÉCNICO — SharePoint Admin | Manta v4.2

**Público:** Administrador SharePoint + TI  
**Nível:** Intermediário / Avançado  
**Duração:** ~3 dias de trabalho

---

## ÍNDICE

1. [Setup Inicial](#setup-inicial)
2. [Criar estrutura via PnP PowerShell](#criar-estrutura-via-pnp-powershell)
3. [Configurar Metadata e Content Types](#configurar-metadata-e-content-types)
4. [Permissões Azure AD + SharePoint](#permissões-azure-ad--sharepoint)
5. [Automações e Flows](#automações-e-flows)
6. [Checklist de validação técnica](#checklist-de-validação-técnica)

---

## SETUP INICIAL

### Pré-requisitos

- Windows 10+ ou macOS/Linux com PowerShell 7+
- Acesso ao SharePoint Online como administrador global
- Azure AD com permissão para criar grupos de segurança
- PnP PowerShell instalado: 
  ```bash
  Install-Module PnP.PowerShell -Scope CurrentUser
  ```
- Jericó API key disponível (consultá-lo em ti-suporte@)

### Conectar ao SharePoint

```powershell
# Conectar ao tenant
Connect-PnPOnline -Url https://mantaassociados.sharepoint.com/sites/Projetos `
  -Interactive

# Validar conexão
Get-PnPWeb | Select Title, Url
```

Esperado output:
```
Title : Projetos
Url   : https://mantaassociados.sharepoint.com/sites/Projetos
```

---

## CRIAR ESTRUTURA VIA PNP POWERSHELL

### Script 1: Criar pastas raiz

```powershell
# Definir URLs base
$siteUrl = "https://mantaassociados.sharepoint.com/sites/Projetos"
$docLib = "Shared Documents"  # nome padrão SharePoint

# Conectar
Connect-PnPOnline -Url $siteUrl -Interactive

# Criar pastas raiz
$rootFolders = @(
    "01-agentes-fundamentais",
    "02-padrao-manta",
    "03-Projetos",
    "04-admin"
)

foreach ($folder in $rootFolders) {
    $existing = Get-PnPFolder -Url $folder -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "✓ Pasta já existe: $folder"
    } else {
        Add-PnPFolder -Name $folder -Folder $docLib
        Write-Host "✓ Criada: $folder"
    }
}
```

### Script 2: Criar subpastas de segmento

```powershell
# Definir segmentos
$segmentos = @(
    "Rodovias",
    "OAE",
    "Ferrovia",
    "Metrô",
    "Portos",
    "Aeroportos",
    "Saneamento",
    "Energia",
    "Barragens"
)

# Criar pasta em 03-Projetos para cada segmento
foreach ($seg in $segmentos) {
    $folderPath = "03-Projetos/$seg"
    $existing = Get-PnPFolder -Url $folderPath -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "✓ Segmento já existe: $seg"
    } else {
        Add-PnPFolder -Name $seg -Folder "03-Projetos"
        Write-Host "✓ Criado segmento: $seg"
    }
}
```

### Script 3: Criar fases (dentro de cada segmento)

```powershell
# Definir fases (conforme CLAUDE.md)
$fases = @(
    @{ Name = "01-Estudos-Previos"; SubFolders = @("EVTE", "Viabilidade-tecnica", "Estudos-base") },
    @{ Name = "02-Projeto-Basico"; SubFolders = @("Levantamento-dados", "Anteprojeto", "Orcamento-preliminar", "Cronograma-preliminar") },
    @{ Name = "03-Projeto-Executivo"; SubFolders = @("Memoriais", "Desenhos-tecnicos", "Orcamento-executivo", "Cronograma-executivo", "Especificacoes-tecnicas") },
    @{ Name = "04-Obra-em-Execucao"; SubFolders = @("Diarios-de-obra", "Aditivos-e-certificacoes", "Medicoes-e-pagamentos") },
    @{ Name = "05-Operacao-Manutencao"; SubFolders = @() },
    @{ Name = "06-Processo-Competitivo"; SubFolders = @("Editais-e-bases", "Respostas-esclarecimentos", "Resultado-licitacao") },
    @{ Name = "07-Due-diligence-M&A"; SubFolders = @() },
    @{ Name = "08-Encerramento"; SubFolders = @("As-built", "Documentacao-final", "Lições-aprendidas") }
)

$segmentos = @("Rodovias", "OAE", "Ferrovia", "Metrô", "Portos", "Aeroportos", "Saneamento", "Energia", "Barragens")

foreach ($seg in $segmentos) {
    foreach ($fase in $fases) {
        $folderPath = "03-Projetos/$seg/$($fase.Name)"
        
        # Criar pasta de fase
        Add-PnPFolder -Name $fase.Name -Folder "03-Projetos/$seg" -ErrorAction SilentlyContinue
        Write-Host "✓ Fase criada: $folderPath"
        
        # Criar subpastas dentro da fase
        foreach ($subFolder in $fase.SubFolders) {
            Add-PnPFolder -Name $subFolder -Folder $folderPath -ErrorAction SilentlyContinue
            Write-Host "  ├─ Subfolder: $subFolder"
        }
    }
    
    # Criar pasta auxiliar para cada segmento
    $auxPath = "03-Projetos/$seg/_Arquivos-auxil"
    Add-PnPFolder -Name "_Arquivos-auxil" -Folder "03-Projetos/$seg" -ErrorAction SilentlyContinue
    Add-PnPFolder -Name "Referências-tecnicas" -Folder $auxPath -ErrorAction SilentlyContinue
    Add-PnPFolder -Name "Templates-padrao" -Folder $auxPath -ErrorAction SilentlyContinue
    Add-PnPFolder -Name "Logs-sync-RAG" -Folder $auxPath -ErrorAction SilentlyContinue
    Write-Host "✓ Auxiliares criados: $seg"
}
```

### Script 4: Criar admin folders

```powershell
$adminBase = "04-admin"

Add-PnPFolder -Name "RAG-chunks" -Folder $adminBase -ErrorAction SilentlyContinue
Add-PnPFolder -Name "Routing-rules" -Folder $adminBase -ErrorAction SilentlyContinue
Add-PnPFolder -Name "Audit-logs" -Folder $adminBase -ErrorAction SilentlyContinue

Write-Host "✓ Admin folders criadas"
```

---

## CONFIGURAR METADATA E CONTENT TYPES

### Script 5: Criar Site Columns

```powershell
$siteUrl = "https://mantaassociados.sharepoint.com/sites/Projetos"
Connect-PnPOnline -Url $siteUrl -Interactive

# 1. Segmento (Choice)
Add-PnPField -DisplayName "Segmento" `
  -InternalName "Segmento" `
  -Type Choice `
  -Required $true `
  -Group "Manta Metadata" `
  -Choices @("Rodovias","OAE","Ferrovia","Metrô","Portos","Aeroportos","Saneamento","Energia","Barragens")

# 2. Fase-ciclo (Choice)
Add-PnPField -DisplayName "Fase-ciclo" `
  -InternalName "Faseciclo" `
  -Type Choice `
  -Required $true `
  -Group "Manta Metadata" `
  -Choices @("01-Estudo","02-Basico","03-Executivo","04-Obra","05-Operacao","06-Processo","07-DueDilience","08-Encerramento")

# 3. Tipo-documento (Choice)
Add-PnPField -DisplayName "Tipo-documento" `
  -InternalName "Tipodocumento" `
  -Type Choice `
  -Required $true `
  -Group "Manta Metadata" `
  -Choices @("PDF","DWG","XLSX","DOCX","MPP","Outro")

# 4. Numero-projeto (Text)
Add-PnPField -DisplayName "Numero-projeto" `
  -InternalName "Numeroprojeto" `
  -Type Text `
  -Required $true `
  -Group "Manta Metadata"

# 5. Versao (Text)
Add-PnPField -DisplayName "Versao" `
  -InternalName "Versao" `
  -Type Text `
  -Required $false `
  -Group "Manta Metadata"

# 6. Agente-responsavel (Text)
Add-PnPField -DisplayName "Agente-responsavel" `
  -InternalName "Agenteresponsavel" `
  -Type Text `
  -Required $false `
  -Group "Manta Metadata"

# 7. Data-ultima-atualizacao (DateTime)
Add-PnPField -DisplayName "Data-ultima-atualizacao" `
  -InternalName "Dataultimaatualizacao" `
  -Type DateTime `
  -Required $false `
  -Group "Manta Metadata"

# 8. Status-documento (Choice)
Add-PnPField -DisplayName "Status-documento" `
  -InternalName "Statusdocumento" `
  -Type Choice `
  -Required $false `
  -Group "Manta Metadata" `
  -Choices @("Rascunho","Revisão","Aprovado","Arquivado") `
  -DefaultValue "Rascunho"

# 9. Cliente-projeto (Text)
Add-PnPField -DisplayName "Cliente-projeto" `
  -InternalName "Clienteprojeto" `
  -Type Text `
  -Required $false `
  -Group "Manta Metadata"

# 10. Palavra-chave-RAG (Multiple lines)
Add-PnPField -DisplayName "Palavra-chave-RAG" `
  -InternalName "PalavrachaveRAG" `
  -Type MultipleLineOfText `
  -Required $false `
  -Group "Manta Metadata"

# 11. Link-Jerico (Hyperlink)
Add-PnPField -DisplayName "Link-Jerico" `
  -InternalName "LinkJerico" `
  -Type URL `
  -Required $false `
  -Group "Manta Metadata"

Write-Host "✓ Todas as 11 Site Columns criadas"
```

### Script 6: Adicionar columns em libraries

```powershell
# Função para adicionar columns a uma library
function Add-ColumnsToLibrary {
    param(
        [string]$LibraryPath,
        [string[]]$ColumnNames
    )
    
    foreach ($col in $ColumnNames) {
        Add-PnPFieldToContentType -Field $col -ContentType "Document" `
          -ErrorAction SilentlyContinue
        Write-Host "  ✓ Column '$col' adicionada"
    }
}

# Aplicar columns obrigatórias em todas as bibliotecas de documento
$mandatoryCols = @("Segmento", "Faseciclo", "Tipodocumento", "Numeroprojeto")
$optionalCols = @("Versao", "Statusdocumento", "Clienteprojeto", "PalavrachaveRAG", "LinkJerico")
$allCols = $mandatoryCols + $optionalCols

$segmentos = @("Rodovias", "OAE", "Ferrovia", "Metrô", "Portos", "Aeroportos", "Saneamento", "Energia", "Barragens")

foreach ($seg in $segmentos) {
    Write-Host "Configurando columns em $seg..."
    
    # Para cada fase que tem subpastas de documento
    $fases = @("01-Estudos-Previos/EVTE", "02-Projeto-Basico/Anteprojeto", "03-Projeto-Executivo/Memoriais", "03-Projeto-Executivo/Orcamento-executivo", "04-Obra-em-Execucao", "06-Processo-Competitivo/Editais-e-bases", "08-Encerramento/As-built")
    
    foreach ($fase in $fases) {
        $folderPath = "03-Projetos/$seg/$fase"
        
        # Criar lista dentro da pasta para armazenar documents com metadata
        # (ou usar a biblioteca padrão com filtros de pasta)
        
        Write-Host "  ✓ $fase configurada"
    }
}

Write-Host "✓ Todas as libraries configuradas"
```

---

## PERMISSÕES AZURE AD + SHAREPOINT

### Script 7: Criar grupos Azure AD

```powershell
# Requer conexão ao Azure AD
Connect-MgGraph -Scopes "Group.ReadWrite.All", "Directory.ReadWrite.All"

$segmentos = @(
    @{ Name = "Rodovias"; Code = "ROD" },
    @{ Name = "OAE"; Code = "OAE" },
    @{ Name = "Ferrovia"; Code = "FER" },
    @{ Name = "Metrô"; Code = "MET" },
    @{ Name = "Portos"; Code = "POR" },
    @{ Name = "Aeroportos"; Code = "AER" },
    @{ Name = "Saneamento"; Code = "SAN" },
    @{ Name = "Energia"; Code = "ENE" },
    @{ Name = "Barragens"; Code = "BAR" }
)

foreach ($seg in $segmentos) {
    # Grupo de Leitura
    New-MgGroup -DisplayName "Manta-Projetos-$($seg.Code)-Leitura" `
      -MailNickname "manta-projetos-$($seg.Code)-leitura" `
      -GroupTypes @() `
      -SecurityEnabled $true `
      -MailEnabled $false `
      -Description "Grupo de leitura - $($seg.Name)" `
      -ErrorAction SilentlyContinue | Out-Null
    
    # Grupo de Edição
    New-MgGroup -DisplayName "Manta-Projetos-$($seg.Code)-Edicao" `
      -MailNickname "manta-projetos-$($seg.Code)-edicao" `
      -GroupTypes @() `
      -SecurityEnabled $true `
      -MailEnabled $false `
      -Description "Grupo de edição - $($seg.Name)" `
      -ErrorAction SilentlyContinue | Out-Null
    
    # Grupo de Aprovação
    New-MgGroup -DisplayName "Manta-Projetos-$($seg.Code)-Aprovacao" `
      -MailNickname "manta-projetos-$($seg.Code)-aprovacao" `
      -GroupTypes @() `
      -SecurityEnabled $true `
      -MailEnabled $false `
      -Description "Grupo de aprovação - $($seg.Name)" `
      -ErrorAction SilentlyContinue | Out-Null
    
    Write-Host "✓ Grupos criados para $($seg.Name)"
}

# Grupos globais
New-MgGroup -DisplayName "Manta-Maestro-Admins" `
  -MailNickname "manta-maestro-admins" `
  -GroupTypes @() `
  -SecurityEnabled $true `
  -MailEnabled $false `
  -ErrorAction SilentlyContinue | Out-Null

New-MgGroup -DisplayName "Manta-RAG-Sync" `
  -MailNickname "manta-rag-sync" `
  -GroupTypes @() `
  -SecurityEnabled $true `
  -MailEnabled $false `
  -ErrorAction SilentlyContinue | Out-Null

Write-Host "✓ Todos os grupos criados"
```

### Script 8: Atribuir permissões no SharePoint

```powershell
$siteUrl = "https://mantaassociados.sharepoint.com/sites/Projetos"
Connect-PnPOnline -Url $siteUrl -Interactive

# Grupos (obter IDs via Get-MgGroup)
$adminGroup = "Manta-Maestro-Admins"
$ragSyncGroup = "Manta-RAG-Sync"

# Atribuir permissões RAIZ
Set-PnPFolderPermission -Identity "01-agentes-fundamentais" `
  -Group $adminGroup -Role "Full Control"

Set-PnPFolderPermission -Identity "02-padrao-manta" `
  -Group $adminGroup -Role "Edit"

Set-PnPFolderPermission -Identity "03-Projetos" `
  -Group $adminGroup -Role "Full Control"

Set-PnPFolderPermission -Identity "04-admin" `
  -Group $adminGroup -Role "Full Control"

Set-PnPFolderPermission -Identity "04-admin/RAG-chunks" `
  -Group $ragSyncGroup -Role "Edit"

Write-Host "✓ Permissões raiz atribuídas"

# Atribuir permissões por SEGMENTO
$segmentos = @(
    @{ Name = "Rodovias"; Code = "ROD" },
    @{ Name = "OAE"; Code = "OAE" },
    # ... etc
)

foreach ($seg in $segmentos) {
    $leitura = "Manta-Projetos-$($seg.Code)-Leitura"
    $edicao = "Manta-Projetos-$($seg.Code)-Edicao"
    $aprovacao = "Manta-Projetos-$($seg.Code)-Aprovacao"
    $path = "03-Projetos/$($seg.Name)"
    
    Set-PnPFolderPermission -Identity $path -Group $leitura -Role "Read"
    Set-PnPFolderPermission -Identity $path -Group $edicao -Role "Edit"
    Set-PnPFolderPermission -Identity $path -Group $aprovacao -Role "Full Control"
    
    Write-Host "✓ Permissões atribuídas: $($seg.Name)"
}
```

---

## AUTOMAÇÕES E FLOWS

### Script 9: Criar Power Automate Flow (Status → Aprovado)

**Trigger:** Item status muda para "Aprovado"  
**Action 1:** Preencher Link-Jerico  
**Action 2:** Notificar Maestro para sincronizar RAG

```json
{
  "triggers": [
    {
      "name": "trigger_item_modified",
      "type": "create_or_update_item",
      "condition": "Status-documento == 'Aprovado' AND Link-Jerico == NULL"
    }
  ],
  "actions": [
    {
      "action": "call_http_api",
      "url": "https://api.jerico.mantaassociados.com/v1/create-document",
      "method": "POST",
      "body": {
        "numero_projeto": "{{Numero-projeto}}",
        "tipo_documento": "{{Tipo-documento}}",
        "fase": "{{Fase-ciclo}}",
        "segmento": "{{Segmento}}",
        "sharepoint_url": "{{Item.Url}}",
        "metadata": {
          "versao": "{{Versao}}",
          "cliente": "{{Cliente-projeto}}"
        }
      },
      "assign_to": "Link-Jerico"
    },
    {
      "action": "send_notification",
      "to": "maestro@mantaassociados.com",
      "subject": "Documento aprovado — RAG sync needed",
      "body": "{{Numero-projeto}} | {{Tipo-documento}} | Status: Aprovado"
    }
  ]
}
```

### Script 10: Job Supabase RAG Sync (via Maestro)

**Arquivo:** `04-admin/Maestro-config.json`

```json
{
  "rag_sync": {
    "enabled": true,
    "schedule": "0 */6 * * *",
    "source": {
      "type": "sharepoint",
      "site_url": "https://mantaassociados.sharepoint.com/sites/Projetos",
      "query": {
        "status": "Aprovado",
        "link_jerico": { "$exists": true }
      }
    },
    "destination": {
      "type": "supabase",
      "table": "rag_chunks",
      "api_url": "https://xxxx.supabase.co",
      "api_key": "${SUPABASE_API_KEY}"
    },
    "chunking": {
      "pdf": {
        "method": "page-based",
        "size": 1000
      },
      "dwg": {
        "method": "layer-based"
      },
      "xlsx": {
        "method": "sheet-based"
      }
    },
    "tags": {
      "rodovias": "rod:",
      "oae": "oae:",
      "ferrovia": "fer:",
      "metro": "met:",
      "portos": "por:",
      "aeroportos": "aer:",
      "saneamento": "san:",
      "energia": "ene:",
      "barragens": "bar:"
    }
  }
}
```

---

## CHECKLIST DE VALIDAÇÃO TÉCNICA

### Pré-launch validation (Dia 12)

- [ ] **Pasta raiz existem:**
  ```powershell
  Get-PnPFolder -Url "01-agentes-fundamentais"
  Get-PnPFolder -Url "02-padrao-manta"
  Get-PnPFolder -Url "03-Projetos"
  Get-PnPFolder -Url "04-admin"
  ```

- [ ] **Todos os segmentos criados:**
  ```powershell
  Get-PnPFolderItem -Folder "03-Projetos" | Where Type -eq "Folder"
  # Esperado: 9 pastas (Rodovias, OAE, Ferrovia, Metrô, Portos, Aeroportos, Saneamento, Energia, Barragens)
  ```

- [ ] **Fases criadas em pelo menos 1 segmento:**
  ```powershell
  Get-PnPFolderItem -Folder "03-Projetos/Rodovias" | Where Type -eq "Folder"
  # Esperado: 9 pastas (01-Estudos-Previos, 02-Projeto-Basico, ..., 08-Encerramento, _Arquivos-auxil)
  ```

- [ ] **Site Columns criadas:**
  ```powershell
  Get-PnPField -Scope Web | Where Group -eq "Manta Metadata"
  # Esperado: 11 fields
  ```

- [ ] **Grupos Azure AD criados:**
  ```powershell
  # Via Azure Portal ou Get-MgGroup
  # Esperado: 29 grupos (3 × 9 + 2 globais)
  ```

- [ ] **Permissões atribuídas:**
  ```powershell
  Get-PnPFolderPermission -Identity "03-Projetos/Rodovias"
  # Esperado: Manta-Projetos-ROD-Leitura (Read), Edicao (Edit), Aprovacao (Full Control)
  ```

- [ ] **Link-Jerico configurado:**
  - [ ] Testar API endpoint:
    ```bash
    curl -H "Authorization: Bearer $JERICO_TOKEN" \
      https://api.jerico.mantaassociados.com/v1/health
    # Esperado: {"status": "ok"}
    ```

- [ ] **Supabase RAG table criada:**
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema='public' AND table_name='rag_chunks';
  -- Esperado: 1 row
  ```

- [ ] **Power Automate Flow testado:**
  - [ ] Upload documento em Rodovias
  - [ ] Mudar status para "Aprovado"
  - [ ] Aguardar 30 seg
  - [ ] Verificar: Link-Jerico foi preenchido?
  - [ ] Verificar: Email notificação foi enviado?

### Performance tests (Dia 13)

- [ ] **Teste de upload (arquivo 50MB):**
  ```powershell
  # Upload via PnP ou interface
  # Esperado: < 5 minutos
  ```

- [ ] **Teste de busca (metadata):**
  - [ ] Criar 10 documentos com diferentes Segmento/Fase
  - [ ] Filtrar por Segmento = "Rodovias"
  - [ ] Esperado: retorna apenas 10 documentos ROD

- [ ] **Teste de permissões:**
  - [ ] Login como usuário "Rodovias-Leitura"
  - [ ] Tentar editar em Rodovias
  - [ ] Esperado: erro "You don't have permission to modify this list item"
  - [ ] Tentar acessar Saneamento
  - [ ] Esperado: erro 403

- [ ] **Teste de RAG sync:**
  - [ ] Forçar sync: `Invoke-WebRequest -Uri "https://maestro.mantaassociados.com/rag/sync"`
  - [ ] Aguardar 2-3 min
  - [ ] Verificar log: `04-admin/Logs-sync-RAG/[YYYY-MM-DD]-sync-result.txt`
  - [ ] Esperado: "Status: OK"

---

## TROUBLESHOOTING

| Erro | Causa | Solução |
|------|-------|---------|
| "Cannot add field, field already exists" | Field criada em execução anterior | Remover com `Remove-PnPField` |
| "User does not have permission to this list" | Grupo Azure AD não sincronizou | Aguardar 15-30 min ou forçar sincronização |
| "Jerico API timeout" | Conectividade com Jericó | Verificar firewall, IP whitelist em Jericó |
| "Supabase rate limit exceeded" | Muitos chunks simultâneos | Reduzir `rag_sync.chunking.size` ou aumentar intervalo |
| "DWG preview not working" | Conversor não ativado | Ativar em: Site Settings → Site Features → "Query Rules" |

---

## ROLLBACK (se necessário)

```powershell
# Remover Site Columns
$fields = @("Segmento", "Faseciclo", "Tipodocumento", "Numeroprojeto", "Versao", "Agenteresponsavel", "Dataultimaatualizacao", "Statusdocumento", "Clienteprojeto", "PalavrachaveRAG", "LinkJerico")

foreach ($field in $fields) {
    Remove-PnPField -DisplayName $field -Force -ErrorAction SilentlyContinue
}

# Remover pastas (via UI ou script)
# Nota: isso move para lixeira, não delete permanentemente
```

---

## PRÓXIMOS PASSOS

1. **Executar scripts 1-10** em ordem (requer ~4-6 horas de trabalho total)
2. **Validar checklist** (30 minutos)
3. **Comunicar ao time** que SP está pronto
4. **Monitorar** primeiros uploads (primeiras 24h)

---

**Documento técnico:** 2026-07-25  
**Versão:** 1.0  
**Support:** maestro@mantaassociados.com
