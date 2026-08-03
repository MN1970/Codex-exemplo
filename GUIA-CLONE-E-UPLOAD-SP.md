# 📋 GUIA PRÁTICO: Clone + Upload SharePoint

**Data**: 2026-08-02  
**Duração**: ~10 minutos  
**Pré-requisito**: Acesso a GitHub + SharePoint

---

## PASSO 1️⃣: Clone a Branch Localmente

Abra terminal/PowerShell e execute:

```bash
# Clone o repositório
git clone https://github.com/mn1970/codex-exemplo.git
cd codex-exemplo

# Checkout na branch
git checkout claude/manta-maestro-objects-metals-vhfirl

# Verifique que está na branch correta
git branch
# Deve mostrar: * claude/manta-maestro-objects-metals-vhfirl
```

**Arquivos disponíveis após clone:**

```
codex-exemplo/
├── maestro-objects-metals.md
├── maestro-objects-metals.json
├── PLANO-INTERVENCAO-V5.md
├── ENTENDIMENTO-MANTA-MAESTRO.md
├── EVOLUCAO-CONHECIMENTO-MAESTRO.md
├── SUMARIO-EXECUTIVO-MAESTRO.md
├── KICKOFF-PHASE1-OBJECTS-METALS.md
├── DIAGNOSTICO-INTEGRACAO-CLAUDE-COWORK.md
└── STATUS-FINAL-COMPLETO.md
```

---

## PASSO 2️⃣: Upload para SharePoint

### A. Acesse o SharePoint

1. Abra: **SharePoint → Documentos Compartilhados**
2. Navegue para: **04_IA → Manta-Maestro**
3. Crie nova pasta: **MAESTRO-OBJECTS-METALS**

### B. Selecione os 8 arquivos

Na pasta local clonada, selecione:

```
✓ maestro-objects-metals.md
✓ maestro-objects-metals.json
✓ PLANO-INTERVENCAO-V5.md
✓ ENTENDIMENTO-MANTA-MAESTRO.md
✓ EVOLUCAO-CONHECIMENTO-MAESTRO.md
✓ SUMARIO-EXECUTIVO-MAESTRO.md
✓ KICKOFF-PHASE1-OBJECTS-METALS.md
✓ DIAGNOSTICO-INTEGRACAO-CLAUDE-COWORK.md
```

### C. Faça Upload em Lote

**Opção 1: Drag-and-drop (recomendado)**
1. Abra SharePoint em navegador
2. Abra pasta `MAESTRO-OBJECTS-METALS`
3. Selecione 8 arquivos no Explorer/Finder local
4. Arraste para a página SharePoint
5. Aguarde conclusão

**Opção 2: Upload pela interface**
1. Na pasta SharePoint, clique **+ Upload**
2. Selecione os 8 arquivos de uma vez
3. Clique **Upload**

**Opção 3: PowerShell (automático)**

```powershell
# Instale PnP.PowerShell se necessário
Install-Module PnP.PowerShell -Force

# Conecte ao SharePoint
$siteUrl = "https://mnassociados.sharepoint.com/sites/Engenharia"
Connect-PnPOnline -Url $siteUrl -Interactive

# Faça upload dos arquivos
$files = @(
  "maestro-objects-metals.md",
  "maestro-objects-metals.json",
  "PLANO-INTERVENCAO-V5.md",
  "ENTENDIMENTO-MANTA-MAESTRO.md",
  "EVOLUCAO-CONHECIMENTO-MAESTRO.md",
  "SUMARIO-EXECUTIVO-MAESTRO.md",
  "KICKOFF-PHASE1-OBJECTS-METALS.md",
  "DIAGNOSTICO-INTEGRACAO-CLAUDE-COWORK.md"
)

$localPath = "C:\Users\<seu-usuario>\caminho\para\codex-exemplo"
$spFolder = "/sites/Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/MAESTRO-OBJECTS-METALS"

foreach ($file in $files) {
  Add-PnPFile -Path "$localPath\$file" -Folder $spFolder -Overwrite
  Write-Host "✓ $file uploaded"
}
```

---

## ✅ Verificação Final

Após upload, verifique no SharePoint:

```
04_IA/Manta-Maestro/MAESTRO-OBJECTS-METALS/
├── ✓ maestro-objects-metals.md (14 KB)
├── ✓ maestro-objects-metals.json (26 KB)
├── ✓ PLANO-INTERVENCAO-V5.md (11 KB)
├── ✓ ENTENDIMENTO-MANTA-MAESTRO.md (33 KB)
├── ✓ EVOLUCAO-CONHECIMENTO-MAESTRO.md (31 KB)
├── ✓ SUMARIO-EXECUTIVO-MAESTRO.md (15 KB)
├── ✓ KICKOFF-PHASE1-OBJECTS-METALS.md (5.7 KB)
└── ✓ DIAGNOSTICO-INTEGRACAO-CLAUDE-COWORK.md (7.0 KB)
```

Tamanho total: ~142 KB

---

## 📞 Próximo: Reunião Kickoff

Após upload, avise para que eu faça:
1. ✅ Verificação de conclusão
2. ✅ Notificação para MN apresentar PR #51
3. ✅ Convite reunião kickoff Fase 1

---

**Tempo estimado**: 10 minutos  
**Dificuldade**: ⭐ Fácil  
**Suporte**: Se tiver dúvida, avisa

