# PLANO DE IMPLEMENTAÇÃO SharePoint — Manta Associados v4.2

**Versão:** 1.0 | **Data:** 2026-07-25 | **Responsável:** Maestro (Manta 00)  
**Ticket:** MNT-2026-UPGRADE-SP-INFRASTRUCTURE  
**Status:** ✅ Pronto para execução

---

## ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Fase 1: Estrutura de Pastas](#fase-1-estrutura-de-pastas)
3. [Fase 2: Metadata Columns](#fase-2-metadata-columns)
4. [Fase 3: Permissões e Grupos](#fase-3-permissões-e-grupos)
5. [Fase 4: Document Templates](#fase-4-document-templates)
6. [Fase 5: Links Jericó](#fase-5-links-jericó)
7. [Fase 6: Checklist de Upload](#fase-6-checklist-de-upload)
8. [Fase 7: Configurações de View](#fase-7-configurações-de-view)

---

## VISÃO GERAL

Esta infraestrutura suporta:
- **8 agentes verticais** (Rodovias S1, OAE S2, Ferrovia S3, Metrô S4, Portos S6, Aeroportos S7, Saneamento S8, Energia S9, Barragens S10)
- **8 fases de ciclo de vida** (EVTE → Encerramento)
- **3 tipos principais de arquivo** (PDF projetos, DWG CAD, XLSX planilhas/orçamentos)
- **RAG + routing automático** (Supabase → agentes)
- **Permissões granulares** (por segmento + por fase)

**Localização raiz:** `https://mantaassociados.sharepoint.com/sites/Projetos/`

---

## FASE 1: ESTRUTURA DE PASTAS

### 1.1 Estrutura de nível 0-2 (CRIAR PRIMEIRO)

```
Projetos (site raiz)
│
├─ 01-agentes-fundamentais/
│  ├─ CLAUDE.md (master registry)
│  ├─ SKILL.md (catálogo de skills)
│  └─ ARQUITETURA-AGENTES-IA.md (v2.0.0)
│
├─ 02-padrao-manta/
│  ├─ templates-documento/
│  ├─ brand-guidelines/
│  └─ processos-comuns/
│
├─ 03-Projetos/
│  ├─ Rodovias/
│  ├─ OAE/
│  ├─ Ferrovia/
│  ├─ Metrô/
│  ├─ Portos/
│  ├─ Aeroportos/
│  ├─ Saneamento/
│  ├─ Energia/
│  └─ Barragens/
│
└─ 04-admin/
   ├─ RAG-chunks/ (Supabase mirror)
   ├─ Routing-rules/ (sp_agent_routing)
   └─ Audit-logs/
```

### 1.2 Estrutura de nível 3-5 POR SEGMENTO (Rodovias S1 como modelo)

**Caminho base:** `03-Projetos/[SEGMENTO]/`

```
Rodovias/
│
├─ 01-Estudos-Previos/
│  ├─ EVTE/
│  │  ├─ [PROJETO-001]-EVTE-vX.pdf
│  │  ├─ [PROJETO-001]-EVTE-CAD-vX.dwg
│  │  └─ [PROJETO-001]-EVTE-Orcamento.xlsx
│  │
│  ├─ Viabilidade-tecnica/
│  │  └─ [PROJETO-001]-Viabilidade-vX.pdf
│  │
│  └─ Estudos-base/
│     ├─ Topografia/
│     ├─ Geotecnia/
│     └─ Ambiental/
│
├─ 02-Projeto-Basico/
│  ├─ Levantamento-dados/
│  ├─ Anteprojeto/
│  │  ├─ [PROJETO-001]-APE-vX.pdf
│  │  └─ [PROJETO-001]-APE-CAD-vX.dwg
│  │
│  ├─ Orcamento-preliminar/
│  │  └─ [PROJETO-001]-ORC-BASICO-vX.xlsx
│  │
│  └─ Cronograma-preliminar/
│     └─ [PROJETO-001]-CRON-BASICO-vX.xlsx
│
├─ 03-Projeto-Executivo/
│  ├─ Memoriais/
│  │  ├─ [PROJETO-001]-Mem-Descritivo-vX.pdf
│  │  ├─ [PROJETO-001]-Mem-Calculista-vX.pdf
│  │  └─ [PROJETO-001]-Mem-Especialidades-vX.pdf
│  │
│  ├─ Desenhos-tecnicos/
│  │  ├─ [PROJETO-001]-PE-Planta-Geral-vX.dwg
│  │  ├─ [PROJETO-001]-PE-Perfil-vX.dwg
│  │  └─ [PROJETO-001]-PE-Detalhe-Especiais-vX.dwg
│  │
│  ├─ Orcamento-executivo/
│  │  ├─ [PROJETO-001]-ORC-EXEC-vX.xlsx
│  │  ├─ [PROJETO-001]-Composicoes-SICRO-vX.xlsx
│  │  └─ [PROJETO-001]-BDI-Analise.xlsx
│  │
│  ├─ Cronograma-executivo/
│  │  ├─ [PROJETO-001]-CRON-EXEC-vX.xlsx
│  │  └─ [PROJETO-001]-CRON-EXEC-vX.mpp
│  │
│  └─ Especificacoes-tecnicas/
│     ├─ [PROJETO-001]-Espec-Materiais-vX.pdf
│     └─ [PROJETO-001]-ESpec-Execucao-vX.pdf
│
├─ 04-Obra-em-Execucao/
│  ├─ Diarios-de-obra/
│  │  └─ [PROJETO-001]-Diario-YYYY-MM-DD-vX.pdf
│  │
│  ├─ Aditivos-e-certificacoes/
│  │  ├─ [PROJETO-001]-Aditivo-001-vX.pdf
│  │  └─ [PROJETO-001]-Certificacao-Medio-vX.pdf
│  │
│  └─ Medições-e-pagamentos/
│     └─ [PROJETO-001]-Medicao-202X-MM-vX.xlsx
│
├─ 05-Operacao-Manutencao/
│  ├─ Manuais/
│  ├─ Registros-manutencao/
│  └─ KPI-desempenho/
│
├─ 06-Processo-Competitivo/
│  ├─ Editais-e-bases/
│  │  ├─ [PROJETO-001]-Edital-vX.pdf
│  │  └─ [PROJETO-001]-Base-Licitacao-vX.xlsx
│  │
│  ├─ Respostas-esclarecimentos/
│  │  └─ [PROJETO-001]-Esclarec-xxx-vX.pdf
│  │
│  └─ Resultado-licitacao/
│     └─ [PROJETO-001]-Resultado-vX.pdf
│
├─ 07-Due-diligence-M&A/
│  ├─ Documentacao-legal/
│  ├─ Documentacao-tecnica/
│  └─ Relatorios-due-diligence/
│
├─ 08-Encerramento/
│  ├─ As-built/
│  │  ├─ [PROJETO-001]-AsBuilt-vX.pdf
│  │  └─ [PROJETO-001]-AsBuilt-CAD-vX.dwg
│  │
│  ├─ Documentacao-final/
│  └─ Lições-aprendidas/
│     └─ [PROJETO-001]-LicoesAprendidas-vX.pdf
│
└─ _Arquivos-auxil/
   ├─ Referências-tecnicas/
   │  └─ Normas DNIT, ABNT, etc
   │
   ├─ Templates-padrao/
   │  ├─ Rodovias-Mem-Descritivo-TEMPLATE.docx
   │  ├─ Rodovias-Orcamento-TEMPLATE.xlsx
   │  └─ Rodovias-Cronograma-TEMPLATE.mpp
   │
   └─ Logs-sync-RAG/
      └─ [AUTO] Auditoria de sincronização com Supabase
```

### 1.3 Estrutura POR SEGMENTO (resumida)

Aplicar mesmo padrão acima para:
- `03-Projetos/OAE/` (Pontes, viadutos, túneis)
- `03-Projetos/Ferrovia/`
- `03-Projetos/Metrô/`
- `03-Projetos/Portos/`
- `03-Projetos/Aeroportos/`
- `03-Projetos/Saneamento/` ← PRIORIDADE AySA
- `03-Projetos/Energia/` ← ANEEL/State Grid
- `03-Projetos/Barragens/`

---

## FASE 2: METADATA COLUMNS

### 2.1 Criar Site Columns (escopo global)

**Local:** Site Settings → Site Columns → Create

| Nome coluna | Tipo | Obrigatório | Descrição |
|------------|------|-------------|-----------|
| **Segmento** | Choice | ✅ | Rodovias, OAE, Ferrovia, Metrô, Portos, Aeroportos, Saneamento, Energia, Barragens |
| **Fase-ciclo** | Choice | ✅ | 01-Estudo, 02-Basico, 03-Executivo, 04-Obra, 05-Operacao, 06-Processo, 07-DueDilience, 08-Encerramento |
| **Tipo-documento** | Choice | ✅ | PDF, DWG, XLSX, DOCX, MPP, Outro |
| **Numero-projeto** | Text | ✅ | Ex: MANT-2026-ROD-001 |
| **Versao** | Text | Não | Ex: v1.0, v1.1, etc |
| **Agente-responsavel** | Text | Não | Ex: agente-infraestrutura-S1 |
| **Data-ultima-atualizacao** | DateTime | Não | Auto-populate |
| **Status-documento** | Choice | Não | Rascunho, Revisão, Aprovado, Arquivado |
| **Cliente-projeto** | Text | Não | Nome do cliente |
| **Palavra-chave-RAG** | Text | Não | Tags para busca RAG |
| **Link-Jerico** | Hyperlink | Não | URL para Jericó |

### 2.2 Aplicar columns em cada library

**Para cada pasta:** `03-Projetos/[SEGMENTO]/[FASE]/`

**View padrão:** Adicionar filtro por Segmento + Fase

```
Configuração por library:
├─ 01-Estudos-Previos/
│  └─ Columns obrigatórias: Segmento, Fase-ciclo, Numero-projeto, Tipo-documento
│
├─ 02-Projeto-Basico/
│  └─ Columns obrigatórias: Segmento, Fase-ciclo, Numero-projeto, Tipo-documento, Versao
│
├─ 03-Projeto-Executivo/
│  └─ Columns obrigatórias: Segmento, Fase-ciclo, Numero-projeto, Tipo-documento, Versao, Status-documento
│
└─ [etc para outras fases...]
```

---

## FASE 3: PERMISSÕES E GRUPOS

### 3.1 Criar Grupos de Segurança (Azure AD)

**Local:** Azure Portal → Groups → Create new group

```
Grupo: Manta-Projetos-Rodovias-Leitura
├─ Tipo: Security
├─ Owners: [TI + coordenador S1]
└─ Members: arquitetos, engenheiros S1

Grupo: Manta-Projetos-Rodovias-Edicao
├─ Tipo: Security
├─ Owners: [coordenador S1]
└─ Members: lead técnico + gerente projeto S1

Grupo: Manta-Projetos-Rodovias-Aprovacao
├─ Tipo: Security
├─ Owners: [diretor técnico]
└─ Members: partner + sênior S1

[REPETIR PARA: OAE, Ferrovia, Metrô, Portos, Aeroportos, Saneamento, Energia, Barragens]

Grupo: Manta-Maestro-Admins
├─ Tipo: Security
└─ Members: [TI, Manta 00 orchestrator]

Grupo: Manta-RAG-Sync
├─ Tipo: Security
└─ Members: [Supabase connector, Maestro]
```

### 3.2 Atribuir permissões na estrutura

**Site raiz:** `https://mantaassociados.sharepoint.com/sites/Projetos/`

```
Permissão padrão:
├─ 01-agentes-fundamentais/
│  └─ Manta-Maestro-Admins: Full Control
│  └─ Todos (Manta): Read
│
├─ 02-padrao-manta/
│  └─ Manta-Maestro-Admins: Edit
│  └─ Todos (Manta): Read
│
├─ 03-Projetos/
│  │
│  ├─ Rodovias/
│  │  └─ Manta-Projetos-Rodovias-Leitura: Read
│  │  └─ Manta-Projetos-Rodovias-Edicao: Edit
│  │  └─ Manta-Projetos-Rodovias-Aprovacao: Full Control
│  │
│  ├─ OAE/
│  │  └─ [idem para S2]
│  │
│  └─ [estrutura similar para Ferrovia, Metrô, Portos, Aeroportos, Saneamento, Energia, Barragens]
│
└─ 04-admin/
   └─ Manta-Maestro-Admins: Full Control
   └─ Manta-RAG-Sync: Edit (só RAG-chunks/)
```

### 3.3 Configurar permissões por fase (controle fino)

Para pasta crítica como `03-Projeto-Executivo/`:

```
├─ 03-Projeto-Executivo/
│  ├─ Memoriais/
│  │  └─ Rodovias-Edicao: Edit
│  │  └─ Rodovias-Aprovacao: Full Control
│  │
│  ├─ Desenhos-tecnicos/ (CAD)
│  │  └─ Rodovias-Edicao (projetistas): Edit
│  │  └─ Rodovias-Leitura: Read (visualizar apenas)
│  │
│  ├─ Orcamento-executivo/
│  │  └─ Rodovias-Edicao (orçamentistas): Edit
│  │  └─ Rodovias-Leitura: Read
│  │
│  └─ Especificacoes-tecnicas/
│     └─ Rodovias-Edicao: Edit
│     └─ Rodovias-Aprovacao: Full Control
```

---

## FASE 4: DOCUMENT TEMPLATES

### 4.1 Localização padrão

Toda pasta deve ter estrutura:

```
_Arquivos-auxil/Templates-padrao/
├─ [SEGMENTO]-Mem-Descritivo-TEMPLATE.docx
├─ [SEGMENTO]-Mem-Calculista-TEMPLATE.docx
├─ [SEGMENTO]-Orcamento-TEMPLATE.xlsx
├─ [SEGMENTO]-Cronograma-TEMPLATE.mpp
├─ [SEGMENTO]-Cronograma-TEMPLATE.xlsx (versão simplificada)
├─ [SEGMENTO]-Especificacoes-TEMPLATE.docx
├─ [SEGMENTO]-Diario-Obra-TEMPLATE.docx
└─ [SEGMENTO]-Edital-TEMPLATE.docx
```

### 4.2 Templates por segmento (exemplos)

#### **Rodovias (S1)**
- `Rodovias-Mem-Descritivo-TEMPLATE.docx` (header: "Manta Associados | Rodovia [--PROJETO--]")
- `Rodovias-Mem-Calculista-TEMPLATE.docx` (pavimentação, terraplenagem, drenagem)
- `Rodovias-Orcamento-TEMPLATE.xlsx` (SICRO integrado, estrutura: item, descrição, un, qtd, vr-un, subtotal)
- `Rodovias-Cronograma-TEMPLATE.mpp` (MS Project com fases de obra)
- `Rodovias-Especificacoes-TEMPLATE.docx` (DNIT + NBR padrão)

#### **OAE (S2) — Pontes/Viadutos**
- `OAE-Mem-Descritivo-TEMPLATE.docx` (estrutura, fundações, encontros)
- `OAE-Mem-Calculista-TEMPLATE.docx` (cálculos estruturais, NBR 7187)
- `OAE-Orcamento-TEMPLATE.xlsx` (armação, concretagem, forma)
- `OAE-Cronograma-TEMPLATE.mpp` (fases críticas: escavação, concretagem, desforma)

#### **Saneamento (S8) — PRIORIDADE AySA**
- `Saneamento-Mem-Descritivo-TEMPLATE.docx` (ETA, ETE, adutora, coletora)
- `Saneamento-Orcamento-TEMPLATE.xlsx` (tubulação, bombeamento, tratamento)
- `Saneamento-Cronograma-TEMPLATE.xlsx` (referência SNIS)
- `Saneamento-ETE-Projeto-TEMPLATE.dwg` (croqui padrão ETE)

#### **Energia (S9) — ANEEL**
- `Energia-Mem-Descritivo-TEMPLATE.docx` (LT, subestação, RAP)
- `Energia-Orcamento-TEMPLATE.xlsx` (estrutura ANEEL)
- `Energia-Cronograma-TEMPLATE.xlsx` (fases licitação ANEEL)

#### **Portos (S6)**
- `Portos-Mem-Descritivo-TEMPLATE.docx` (berço, molhe, dragagem)
- `Portos-Orcamento-TEMPLATE.xlsx` (estruturas portuárias, PIANC)

#### **Aeroportos (S7)**
- `Aeroportos-Mem-Descritivo-TEMPLATE.docx` (pista, TPS, TECA, balizamento)
- `Aeroportos-Orcamento-TEMPLATE.xlsx` (RBAC ANAC)

#### **Barragens (S10)**
- `Barragens-Mem-Descritivo-TEMPLATE.docx` (vertedouro, CFRD, rejeitos)
- `Barragens-Orcamento-TEMPLATE.xlsx` (ICOLD, CCR)

#### **Ferrovia (S3) + Metrô (S4)**
- Templates similares, com referências a AMV, NATM, PSD, etc.

### 4.3 Instruções para criar template

**Passo 1:** Copiar arquivo com sucesso em projeto piloto  
**Passo 2:** Salvar como template (.dotx para Word, modelo para Excel)  
**Passo 3:** Fazer upload em `_Arquivos-auxil/Templates-padrao/`  
**Passo 4:** Documentar placeholders:

```
Template Word:
[--PROJETO--]     → Número projeto (ex: MANT-2026-ROD-001)
[--CLIENTE--]     → Nome cliente
[--DATA--]        → Preenchimento automático
[--ENGENHEIRO--]  → Responsável técnico

Template Excel:
{PROJETO}         → Número projeto
{VERSAO}          → v1.0
{DATA}            → Data de emissão
```

---

## FASE 5: LINKS JERICÓ

### 5.1 O que é Jericó?

**Jericó** = Sistema de gestão de conteúdo + BI + DAM interno Manta  
**URL base:** `https://jerico.mantaassociados.com/`  
**API endpoint:** `https://api.jerico.mantaassociados.com/v1/`

### 5.2 Integração SharePoint ↔ Jericó

Cada documento importante deve ter link bidirecional:

**Estrutura de URL Jericó:**

```
https://jerico.mantaassociados.com/projetos/[SEGMENTO]/[NUMERO-PROJETO]/[FASE]/[TIPO-DOC]

Exemplos:
├─ https://jerico.mantaassociados.com/projetos/rodovias/MANT-2026-ROD-001/03-executivo/memoriais
├─ https://jerico.mantaassociados.com/projetos/saneamento/MANT-2026-SAN-001/02-basico/orcamento
└─ https://jerico.mantaassociados.com/projetos/energia/MANT-2026-ENE-001/06-licitacao/edital
```

### 5.3 Metadado "Link-Jerico" — Preenchimento

**Local:** Coluna "Link-Jerico" em cada biblioteca

**Quando preencher:**
- ✅ Após upload de documento **aprovado** (status = "Aprovado")
- ✅ Documentos principais: Memoriais, Orçamentos, Cronogramas, Desenhos CAD, Editais
- ❌ Rascunhos, referências, auxiliares

**Formato:**

```
{
  "tipo": "PDF|DWG|XLSX",
  "jerico_id": "uuid-gerado-jerico",
  "jerico_url": "https://jerico.mantaassociados.com/projetos/...",
  "sincronizado_em": "2026-07-25T14:30:00Z",
  "checksum": "sha256:abc123..."
}
```

### 5.4 Sincronização automática RAG

**Localização:** `04-admin/RAG-chunks/`

Maestro roda job `sync-to-rag`:

```
1. Procura documentos com status="Aprovado" + Link-Jerico preenchido
2. Baixa arquivo do SharePoint
3. Extrai chunks (PDF parser, DWG layers, XLSX sheets)
4. Envia para Supabase (rag_chunks table)
5. Tag com prefixo: rod:, oae:, fer:, met:, por:, aer:, san:, ene:, bar:
6. Marca "Logs-sync-RAG/[YYYY-MM-DD]-sync-result.txt"
```

**Arquivo de log exemplo:**

```
[2026-07-25 14:30:15] SYNC START: Rodovias
├─ Documentos encontrados: 42
├─ Com Link-Jerico: 38
├─ Novos chunks gerados: 156
├─ Chunks sincronizados com Supabase: 156 (100%)
├─ Tempo: 2m 14s
└─ Status: OK ✅

[2026-07-25 14:35:20] SYNC START: Saneamento (AySA priority)
├─ Documentos encontrados: 18
├─ Com Link-Jerico: 16
├─ Novos chunks gerados: 94
├─ Chunks sincronizados com Supabase: 94 (100%)
└─ Status: OK ✅
```

---

## FASE 6: CHECKLIST DE UPLOAD

### 6.1 Pré-requisitos (antes de subir arquivo)

- [ ] **Nome do arquivo** segue padrão: `[PROJETO-XXX]-[Tipo-doc]-[Fase]-vX.Y.[ext]`
  - ✅ Exemplo: `MANT-2026-ROD-001-Mem-Descritivo-03-v1.0.pdf`
  - ✅ Exemplo: `MANT-2026-SAN-001-Orcamento-02-v2.1.xlsx`
  - ❌ Evitar: `projeto_novo.pdf`, `documento (1).docx`

- [ ] **Arquivo foi validado** para erros:
  - PDF: abrir, verificar OCR se necessário
  - DWG: verificar layers, escalas, referências externas
  - XLSX: validar fórmulas, referências circulares

- [ ] **Arquivo está em versão final de análise** (não é rascunho)

- [ ] **Arquivo tem metadados preenchidos** (exif/properties):
  - Title: [PROJETO-XXX] [Tipo-doc]
  - Author: Nome engenheiro responsável
  - Subject: [SEGMENTO] - [FASE]
  - Keywords: [tags relevantes]

### 6.2 Passos de upload (executável)

#### **Passo 1: Selecionar pasta correta**

```
Navegar até: Projetos → 03-Projetos → [SEGMENTO] → [FASE] → [SUBFASE]

Exemplo para Rodovia executiva:
  Projetos / 03-Projetos / Rodovias / 03-Projeto-Executivo / Memoriais/
```

#### **Passo 2: Upload do arquivo**

```
Click "Upload" → Selecionar arquivo → OK
→ SharePoint inicia upload
→ Após conclusão, arquivo aparece na lista
```

#### **Passo 3: Preencher metadados obrigatórios**

Clicar no arquivo → "Edit details" (ou ⋮ → Detalhe)

| Campo | Valor | Exemplo |
|-------|-------|---------|
| **Segmento** | Choice dropdown | Rodovias |
| **Fase-ciclo** | Choice dropdown | 03-Executivo |
| **Numero-projeto** | Text | MANT-2026-ROD-001 |
| **Tipo-documento** | Choice dropdown | PDF |
| **Versao** | Text | 1.0 |
| **Status-documento** | Choice dropdown | Rascunho (inicialmente) |
| **Cliente-projeto** | Text (auto-complete) | [Nome cliente] |
| **Palavra-chave-RAG** | Text (tags) | rodovia, pavimentação, terraplenagem, CBUQ |
| **Link-Jerico** | Hyperlink | [Deixar em branco por enquanto] |

**Salvar.**

#### **Passo 4: Submeter para aprovação**

Quando documento pronto para revisão:

```
1. Editar arquivo
2. Mudar "Status-documento" para "Revisão"
3. Adicionar comentário: "@[Nome revisor] favor revisar"
4. Salvar
```

Revisor recebe notificação.

#### **Passo 5: Aprovar documento**

Se revisor aprova:

```
1. Editar arquivo
2. Mudar "Status-documento" para "Aprovado"
3. Preencher "Link-Jerico" com URL Jericó
4. Adicionar comentário: "Aprovado em [DATA]"
5. Salvar
```

Maestro (RAG sync job) detecta status "Aprovado" → sincroniza com Jericó + Supabase.

#### **Passo 6: Documentar versões**

Se arquivo já existe (v1.0) e precisa atualizar:

```
❌ NÃO sobrescrever arquivo anterior
✅ FAZER:
   1. Renomear antigo: [PROJETO-001]-Mem-v1.0.pdf → [PROJETO-001]-Mem-v1.0_ARCHIVED.pdf
   2. Upload novo: [PROJETO-001]-Mem-v1.1.pdf
   3. Atualizar "Versao" no metadata novo arquivo: 1.1
   4. Voltar versão antiga para "Status-documento" = "Arquivado"
```

SharePoint preserva histórico automático via "Version History".

### 6.3 Checklist pós-upload (validação)

- [ ] Arquivo aparece na pasta correta
- [ ] Todos os metadados foram preenchidos (5 obrigatórios: Segmento, Fase, Número-projeto, Tipo-documento, Status)
- [ ] Arquivo é visualizável (clique no nome → preview abre)
- [ ] Se PDF: OCR está pronto (pode levar 1-2 min)
- [ ] Se DWG: layers estão visíveis no preview
- [ ] Se XLSX: gráficos renderizam corretamente
- [ ] Versão anterior (se existia) está marcada como "Arquivado"
- [ ] Nenhum erro de permissão ou checagem de malware

### 6.4 Erros comuns e soluções

| Erro | Causa | Solução |
|------|-------|---------|
| "Você não tem permissão para fazer upload aqui" | Grupo Azure AD fora da permissão da pasta | Contactar Manta-Maestro-Admins para adicionar ao grupo de segurança do segmento |
| "Arquivo muito grande (>500MB)" | Limite SharePoint | Compactar CAD ou dividir XLSX em múltiplas abas |
| "Extensão .dwg não permitida" | Filtro de segurança | Configurar no site settings: Allowed file types: .pdf, .dwg, .xlsx, .docx, .mpp |
| "Metadados obrigatórios faltando" | Coluna required está vazia | Preencher todos os 5 campos obrigatórios antes de salvar |
| "Preview não funciona para DWG" | Conversor não disponível | Usar Autodesk viewer: https://viewer.autodesk.com/ (alternativa) |

---

## FASE 7: CONFIGURAÇÕES DE VIEW

### 7.1 View padrão por pasta

**Para cada pasta de fase (ex: `03-Executivo/Memoriais/`)**

Nome: `Todos-documentos`  
Tipo: List (ou Gallery para preview)

| Coluna | Ordem | Filtro | Agrupado | Observação |
|--------|-------|--------|----------|------------|
| Nome (Title) | 1 | — | — | Clicável para abrir |
| Numero-projeto | 2 | — | — | Agrupação opcional |
| Tipo-documento | 3 | — | ✅ | Agrupar por Tipo |
| Versao | 4 | — | — | Último à esquerda |
| Status-documento | 5 | ✅ | — | Filtro: "Aprovado" by default |
| Modified | 6 | — | — | Ordenar desc (mais novo primeiro) |
| Modified By | 7 | — | — | Quem alterou |

**Filtro padrão:**
```
Status-documento equals "Aprovado"
AND Tipo-documento NOT equals "Arquivado"
```

### 7.2 View especializada: "Em Revisão"

Nome: `Em-Revisao`  
Filtro:
```
Status-documento equals "Revisão"
```

Colunas: Nome, Numero-projeto, Modified By, Created (data submissão)

### 7.3 View especializada: "Histórico de versões"

Nome: `Historico-Versoes`  
Filtro: (sem filtro, mostra tudo)

Colunas: Nome, Numero-projeto, Versao, Status-documento, Modified, Modified By

Ordenar: Numero-projeto (asc), Versao (desc)

### 7.4 View móvel / simplificada

Nome: `Vista-Rapida` (para mobile)

Colunas: Nome, Numero-projeto, Tipo-documento  
Filtro: Status-documento equals "Aprovado"  
Ordenar: Modified (desc)

---

## RESUMO EXECUTÁVEL (Roadmap)

### Semana 1: Infraestrutura base

- [ ] **Dia 1-2:** Criar estrutura de pastas (Fase 1)
  - Criar raiz `03-Projetos/`
  - Criar 9 pastas de segmento
  - Criar subpastas de fase (01-08) em cada segmento
  
- [ ] **Dia 3:** Criar Site Columns (Fase 2)
  - 11 columns conforme tabela 2.1
  - Aplicar em todas as libraries de documento
  
- [ ] **Dia 4-5:** Configurar permissões (Fase 3)
  - Criar 27 grupos de segurança Azure AD (3 por segmento × 9)
  - Atribuir permissões em cada pasta
  - Testar acesso com 1-2 usuários piloto

### Semana 2: Templates e configuração final

- [ ] **Dia 6-7:** Preparar templates (Fase 4)
  - Criar templates para segmentos prioritários: Rodovias, Saneamento, Energia
  - Upload em `_Arquivos-auxil/Templates-padrao/`
  - Documentar placeholders em WIKI interno
  
- [ ] **Dia 8:** Configurar integração Jericó (Fase 5)
  - Validar API endpoint Jericó
  - Configurar credenciais Maestro ↔ Jericó
  - Testar sync em pasta piloto
  
- [ ] **Dia 9-10:** Configurar Views (Fase 7)
  - Criar 4 views por pasta (Todos, Em Revisão, Histórico, Rápida)
  - Testar filtros e ordenação
  - Publicar documentação para usuários

### Semana 3: Validação e go-live

- [ ] **Dia 11-12:** Testes de acesso
  - Grupo S1 (Rodovias): upload, edição, aprovação
  - Grupo S8 (Saneamento): upload, edição, aprovação
  - Verificar permissões granulares por fase
  
- [ ] **Dia 13:** Treinamento
  - Sessão com líderes técnicos de cada segmento
  - Walkthrough: upload, metadados, aprovação, Jericó
  - Entrega de checklist de upload (Fase 6)
  
- [ ] **Dia 14-15:** Go-live + suporte
  - Liberação para todos os usuários
  - Suporte a dúvidas (primeira semana)
  - Documentar lições aprendidas

---

## DOCUMENTAÇÃO PARA USUÁRIOS

### Template de instruções (copiar para cada segmento)

```markdown
# Como fazer upload de documentos — Rodovias (S1)

## 1. Acessar a biblioteca

Navegue até:
Projetos → 03-Projetos → Rodovias → [FASE desejada] → [SUBFASE]

Exemplo: 03-Projeto-Executivo → Memoriais

## 2. Fazer upload

Click "Upload" (canto superior direito) → Selecione arquivo → "Upload"

## 3. Preencher metadados

Após upload, clique no arquivo → "Edit details" → Preencha:

- **Segmento:** Rodovias
- **Fase-ciclo:** 03-Executivo (ou fase apropriada)
- **Numero-projeto:** Ex: MANT-2026-ROD-001
- **Tipo-documento:** PDF (ou DWG, XLSX)
- **Status-documento:** Rascunho (por default)

Click "Save"

## 4. Submeter para revisão

Quando pronto:
- Edit details → Status-documento = "Revisão"
- Adicione comentário: @[Nome revisor] favor revisar
- Save

## 5. Revisor aprova

Revisor:
- Edit details → Status-documento = "Aprovado"
- Link-Jerico = [URL do Jericó, se disponível]
- Save

→ Documento sincroniza automaticamente com RAG (Supabase) para buscas

## Dúvidas?

Contacte: [email TI] ou Manta-Maestro-Admins
```

---

## APÊNDICE A: Naming Convention (resumo)

```
[PROJETO-XXX]-[TipoDoc]-[Fase]-v[Maior].[Menor].[ext]

Exemplos:
├─ MANT-2026-ROD-001-Mem-Descritivo-03-v1.0.pdf
├─ MANT-2026-ROD-001-Orcamento-03-v2.1.xlsx
├─ MANT-2026-SAN-001-ETE-Projeto-02-v1.0.dwg
├─ MANT-2026-ENE-001-Edital-06-v1.2.pdf
└─ MANT-2026-BAR-001-Mem-Calculista-03-v3.0.pdf

Legenda:
├─ MANT-[YYYY]-[SEG]-[NNN]
│  ├─ YYYY: ano projeto
│  ├─ SEG: segmento (ROD, OAE, FER, MET, POR, AER, SAN, ENE, BAR)
│  └─ NNN: número sequencial (001, 002, ...)
│
├─ TipoDoc: Mem (memorial), Orcamento, Cronograma, Desenho, Edital, etc
│
├─ Fase:
│  ├─ 01: Estudo
│  ├─ 02: Básico
│  ├─ 03: Executivo
│  ├─ 04: Obra
│  ├─ 05: Operação
│  ├─ 06: Processo
│  ├─ 07: Due-diligence
│  └─ 08: Encerramento
│
└─ v[Maior].[Menor]: 1.0, 1.1, 2.0, etc
```

---

## APÊNDICE B: Segredos e credenciais (não incluído neste documento)

Localizar em: **SharePoint → 04-admin → Credenciais-Maestro.xlsx** (encrypted)

- Credenciais API Jericó
- Credenciais Supabase (RAG)
- Tokens Azure AD para sync automático
- Chaves de assinatura

→ **Acessível apenas a Manta-Maestro-Admins**

---

## ASSINATURAS E APROVAÇÃO

| Papel | Nome | Data | Assinatura |
|-------|------|------|-----------|
| Coordenador TI | [--] | 2026-07-25 | — |
| Diretor Técnico | [--] | 2026-07-25 | — |
| Maestro (Manta 00) | IA Orchestrator | 2026-07-25 | ✅ |

---

**FIM DO PLANO**

Versão: 1.0 | Data: 2026-07-25 | Ticket: MNT-2026-UPGRADE-SP-INFRASTRUCTURE
