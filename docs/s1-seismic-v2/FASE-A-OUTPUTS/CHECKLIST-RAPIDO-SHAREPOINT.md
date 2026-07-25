# CHECKLIST RÁPIDO — SharePoint Manta v4.2

**Uso:** Imprima ou abra em tablet durante implementação. Marque conforme conclui cada item.

---

## ✅ FASE 1: CRIAR ESTRUTURA DE PASTAS (Dia 1-2)

### Raiz `Projetos` (site-level)

- [ ] `01-agentes-fundamentais/`
- [ ] `02-padrao-manta/`
- [ ] `03-Projetos/`
- [ ] `04-admin/`

### Dentro de `01-agentes-fundamentais/`
- [ ] CLAUDE.md (upload)
- [ ] SKILL.md (upload)
- [ ] ARQUITETURA-AGENTES-IA.md (upload)

### Dentro de `02-padrao-manta/`
- [ ] `templates-documento/`
- [ ] `brand-guidelines/`
- [ ] `processos-comuns/`

### Dentro de `03-Projetos/` — Criar 9 pastas de segmento

- [ ] `Rodovias/` (S1)
- [ ] `OAE/` (S2)
- [ ] `Ferrovia/` (S3)
- [ ] `Metrô/` (S4)
- [ ] `Portos/` (S6)
- [ ] `Aeroportos/` (S7)
- [ ] `Saneamento/` (S8) ⭐ PRIORIDADE
- [ ] `Energia/` (S9)
- [ ] `Barragens/` (S10)

### Dentro de CADA segmento — Criar 8 pastas de fase

**Template (repetir para todos os 9 segmentos):**

```
[SEGMENTO]/
├─ 01-Estudos-Previos/
│  ├─ EVTE/
│  ├─ Viabilidade-tecnica/
│  └─ Estudos-base/
├─ 02-Projeto-Basico/
│  ├─ Levantamento-dados/
│  ├─ Anteprojeto/
│  ├─ Orcamento-preliminar/
│  └─ Cronograma-preliminar/
├─ 03-Projeto-Executivo/
│  ├─ Memoriais/
│  ├─ Desenhos-tecnicos/
│  ├─ Orcamento-executivo/
│  ├─ Cronograma-executivo/
│  └─ Especificacoes-tecnicas/
├─ 04-Obra-em-Execucao/
│  ├─ Diarios-de-obra/
│  ├─ Aditivos-e-certificacoes/
│  └─ Medicoes-e-pagamentos/
├─ 05-Operacao-Manutencao/
├─ 06-Processo-Competitivo/
│  ├─ Editais-e-bases/
│  ├─ Respostas-esclarecimentos/
│  └─ Resultado-licitacao/
├─ 07-Due-diligence-M&A/
├─ 08-Encerramento/
└─ _Arquivos-auxil/
   ├─ Referências-tecnicas/
   ├─ Templates-padrao/
   └─ Logs-sync-RAG/
```

**Contador:**
- Segmentos: [9 ✓]
- Fases por segmento: [8 ✓]
- **TOTAL esperado:** 9 × ~20 pastas = ~180 pastas criadas ✅

### Dentro de `04-admin/`
- [ ] `RAG-chunks/`
- [ ] `Routing-rules/`
- [ ] `Audit-logs/`

**Status Fase 1:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 2: CRIAR METADATA COLUMNS (Dia 3)

**Local:** Site Settings → Site Columns → Create

### Criar 11 Site Columns

- [ ] **Segmento** (Type: Choice)
  - Choices: Rodovias | OAE | Ferrovia | Metrô | Portos | Aeroportos | Saneamento | Energia | Barragens
  - Required: YES

- [ ] **Fase-ciclo** (Type: Choice)
  - Choices: 01-Estudo | 02-Basico | 03-Executivo | 04-Obra | 05-Operacao | 06-Processo | 07-DueDilience | 08-Encerramento
  - Required: YES

- [ ] **Tipo-documento** (Type: Choice)
  - Choices: PDF | DWG | XLSX | DOCX | MPP | Outro
  - Required: YES

- [ ] **Numero-projeto** (Type: Single line of text)
  - Description: "Ex: MANT-2026-ROD-001"
  - Required: YES

- [ ] **Versao** (Type: Single line of text)
  - Description: "Ex: v1.0, v1.1, v2.0"
  - Required: NO

- [ ] **Agente-responsavel** (Type: Single line of text)
  - Description: "Ex: agente-infraestrutura-S1"
  - Required: NO

- [ ] **Data-ultima-atualizacao** (Type: Date and Time)
  - Required: NO

- [ ] **Status-documento** (Type: Choice)
  - Choices: Rascunho | Revisão | Aprovado | Arquivado
  - Default: Rascunho
  - Required: NO

- [ ] **Cliente-projeto** (Type: Single line of text)
  - Required: NO

- [ ] **Palavra-chave-RAG** (Type: Multiple lines of text)
  - Description: "Tags separadas por vírgula para busca RAG"
  - Required: NO

- [ ] **Link-Jerico** (Type: Hyperlink or Picture)
  - Description: "URL de sincronização com Jericó"
  - Required: NO

### Aplicar columns em libraries

**Para CADA pasta de fase (ex: `Rodovias/03-Projeto-Executivo/Memoriais/`):**

- [ ] Ir em Library Settings → Columns
- [ ] Add existing site column
- [ ] Selecionar: Segmento, Fase-ciclo, Tipo-documento, Numero-projeto, Status-documento (obrigatórios)
- [ ] Selecionar: Versao, Agente-responsavel, Cliente-projeto, Palavra-chave-RAG, Link-Jerico (opcionais)
- [ ] Save

**Contador:**
- Segmentos: 9
- Fases por segmento (com libraries de documentos): ~12
- **TOTAL esperado:** 9 × 12 = ~108 libraries configuradas ✅

**Status Fase 2:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 3: CRIAR GRUPOS AZURE AD E PERMISSÕES (Dia 4-5)

### Criar grupos Azure AD

**Local:** Azure Portal → Groups → New Group

**Template para CADA segmento (repetir 9×):**

- [ ] `Manta-Projetos-[SEG]-Leitura`
  - Tipo: Security
  - Owners: [coordenador TI] + [coordenador segmento]
  - Members: arquitetos, engenheiros segmento

- [ ] `Manta-Projetos-[SEG]-Edicao`
  - Tipo: Security
  - Owners: [coordenador segmento]
  - Members: lead técnico + gerentes projetos

- [ ] `Manta-Projetos-[SEG]-Aprovacao`
  - Tipo: Security
  - Owners: [diretor técnico]
  - Members: partner + sênior segmento

**Grupos globais:**

- [ ] `Manta-Maestro-Admins`
  - Members: TI, Manta 00 orchestrator

- [ ] `Manta-RAG-Sync`
  - Members: Supabase connector, Maestro

**Contador:**
- Grupos por segmento: 3
- Segmentos: 9
- **TOTAL esperado:** (3 × 9) + 2 = 29 grupos ✅

### Atribuir permissões

**Raiz site `Projetos`:**

- [ ] `Manta-Maestro-Admins` → Full Control
- [ ] `Todos (Manta)` → Read

**`01-agentes-fundamentais/`:**
- [ ] `Manta-Maestro-Admins` → Full Control
- [ ] `Todos (Manta)` → Read

**`02-padrao-manta/`:**
- [ ] `Manta-Maestro-Admins` → Edit
- [ ] `Todos (Manta)` → Read

**`03-Projetos/`:**
- [ ] `Manta-Maestro-Admins` → Full Control

**Para CADA segmento (ex: `Rodovias/`):**

- [ ] `Manta-Projetos-Rodovias-Leitura` → Read
- [ ] `Manta-Projetos-Rodovias-Edicao` → Edit
- [ ] `Manta-Projetos-Rodovias-Aprovacao` → Full Control

**Para pastas críticas (ex: `03-Projeto-Executivo/Orcamento-executivo/`):**

- [ ] Herdar permissões do segmento (padrão)
- [ ] OU configurar granular se necessário (ex: só orçamentistas editam XLSX)

**`04-admin/`:**

- [ ] `Manta-Maestro-Admins` → Full Control
- [ ] `Manta-RAG-Sync` → Edit (só subpasta `RAG-chunks/`)

**Contador:**
- Atribuições de permissão esperadas: ~50+ ✅

**Status Fase 3:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 4: PREPARAR TEMPLATES DE DOCUMENTO (Dia 6-7)

### Identificar modelos de sucesso

**Para CADA segmento, localizar ou criar:**

- [ ] **[SEG]-Mem-Descritivo-TEMPLATE.docx**
  - Fazer upload em: `[SEG]/_Arquivos-auxil/Templates-padrao/`

- [ ] **[SEG]-Orcamento-TEMPLATE.xlsx**
  - Linhas: item | descrição | un | qtd | vr-unitário | subtotal
  - Fazer upload em: `[SEG]/_Arquivos-auxil/Templates-padrao/`

- [ ] **[SEG]-Cronograma-TEMPLATE.xlsx** (ou .mpp)
  - Fases principais do segmento
  - Fazer upload em: `[SEG]/_Arquivos-auxil/Templates-padrao/`

- [ ] **[SEG]-Especificacoes-TEMPLATE.docx**
  - NBR + normas segmento
  - Fazer upload em: `[SEG]/_Arquivos-auxil/Templates-padrao/`

### Checklist por segmento

**S1 Rodovias:**
- [ ] Mem-Descritivo (CBUQ, BGS, terraplenagem)
- [ ] Orcamento (SICRO integrado)
- [ ] Cronograma (MS Project ou XLSX)
- [ ] Especificacoes (DNIT + NBR)

**S2 OAE:**
- [ ] Mem-Descritivo (estrutura, fundações)
- [ ] Mem-Calculista (NBR 7187)
- [ ] Orcamento
- [ ] Cronograma

**S3 Ferrovia:**
- [ ] Mem-Descritivo (AMV, dormente)
- [ ] Orcamento
- [ ] Cronograma

**S4 Metrô:**
- [ ] Mem-Descritivo (NATM, PSD)
- [ ] Orcamento
- [ ] Cronograma

**S6 Portos:**
- [ ] Mem-Descritivo (berço, molhe, dragagem)
- [ ] Orcamento (PIANC)
- [ ] Cronograma

**S7 Aeroportos:**
- [ ] Mem-Descritivo (pista, TPS, TECA)
- [ ] Orcamento (RBAC ANAC)
- [ ] Cronograma

**S8 Saneamento ⭐:**
- [ ] Mem-Descritivo (ETA, ETE, adutora)
- [ ] Orcamento (tubulação, bombeamento)
- [ ] Cronograma (SNIS)
- [ ] Desenho-ETE-TEMPLATE.dwg

**S9 Energia:**
- [ ] Mem-Descritivo (LT, subestação)
- [ ] Orcamento (estrutura ANEEL)
- [ ] Cronograma (fases licitação)

**S10 Barragens:**
- [ ] Mem-Descritivo (vertedouro, CFRD)
- [ ] Orcamento (ICOLD)
- [ ] Cronograma

**Contador:**
- Templates por segmento: ~4-5
- Segmentos: 9
- **TOTAL esperado:** ~40 templates ✅

**Status Fase 4:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 5: INTEGRAÇÃO JERICÓ (Dia 8)

### Validar integração

- [ ] **Testar API Jericó:**
  ```bash
  curl -H "Authorization: Bearer $JERICO_TOKEN" \
    https://api.jerico.mantaassociados.com/v1/health
  ```
  → Esperado: `{"status": "ok"}`

- [ ] **Configurar credenciais Maestro:**
  - SharePoint → 04-admin → Credenciais-Maestro.xlsx
  - Linha "Jerico API Key": [inserir token]
  - Linha "Jerico URL": https://jerico.mantaassociados.com/
  - Criptografar arquivo

- [ ] **Testar sync em pasta piloto (Rodovias):**
  - Upload 1 arquivo para: `Rodovias/03-Projeto-Executivo/Memoriais/`
  - Preencher metadados
  - Mudar status para "Aprovado"
  - Aguardar 2-3 min
  - Verificar: arquivo aparece em Jericó?

### Validar Supabase RAG

- [ ] **Criar coleções RAG (Supabase):**
  - `rag_chunks` table deve ter columns:
    - `id` (uuid, pk)
    - `segmento` (text): rod | oae | fer | met | por | aer | san | ene | bar
    - `numero_projeto` (text)
    - `tipo_documento` (text)
    - `conteudo` (text): chunk extraído
    - `metadata` (jsonb): {fase, versao, link_jerico, checksum}
    - `sincronizado_em` (timestamp)

- [ ] **Testar inserção manual:**
  ```sql
  INSERT INTO rag_chunks (segmento, numero_projeto, tipo_documento, conteudo, metadata)
  VALUES ('rod', 'MANT-2026-ROD-001', 'pdf', 'test content chunk', '{"fase": "03"}');
  ```

- [ ] **Configurar job Maestro:**
  - Arquivo: `04-admin/Maestro-config.json`
  - Linha "rag_sync_interval": "0 */6 * * *" (a cada 6h)
  - Salvar

**Status Fase 5:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 6: CRIAR VIEWS (Dia 9-10)

### Para CADA pasta de documentos (ex: `Rodovias/03-Projeto-Executivo/Memoriais/`)

**View 1: "Todos-documentos" (padrão)**
- [ ] Name: `Todos-documentos`
- [ ] Type: List (ou Gallery)
- [ ] Columns: Nome | Numero-projeto | Tipo-documento | Versao | Status-documento | Modified | Modified By
- [ ] Filtro: `Status-documento ≠ "Arquivado"`
- [ ] Ordenação: Modified (desc)
- [ ] Agrupar por: (nenhum)

**View 2: "Em-Revisao"**
- [ ] Name: `Em-Revisao`
- [ ] Columns: Nome | Numero-projeto | Modified By | Created
- [ ] Filtro: `Status-documento = "Revisão"`
- [ ] Ordenação: Created (desc)

**View 3: "Historico-Versoes"**
- [ ] Name: `Historico-Versoes`
- [ ] Columns: Nome | Numero-projeto | Versao | Status-documento | Modified | Modified By
- [ ] Filtro: (sem filtro, mostra tudo)
- [ ] Ordenação: Numero-projeto (asc), Versao (desc)

**View 4: "Vista-Rapida" (mobile)**
- [ ] Name: `Vista-Rapida`
- [ ] Columns: Nome | Numero-projeto | Tipo-documento
- [ ] Filtro: `Status-documento = "Aprovado"`
- [ ] Ordenação: Modified (desc)

**Contador:**
- Views por biblioteca: 4
- Bibliotecas (fases): ~108
- **TOTAL esperado:** 108 × 4 = 432 views ✅

> **Dica:** Criar script PowerShell para automatizar? Consulte TI.

**Status Fase 6:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 7: TESTES E VALIDAÇÃO (Dia 11-12)

### Teste de acesso (por segmento)

**Para Rodovias (S1):**
- [ ] Usuário "Rodovias-Leitura" consegue acessar? (ler, mas não editar)
- [ ] Usuário "Rodovias-Edicao" consegue fazer upload + editar metadados?
- [ ] Usuário "Rodovias-Aprovacao" consegue mudar status para "Aprovado"?
- [ ] Usuário fora do grupo é bloqueado (error 403)?

**Para Saneamento (S8) ⭐:**
- [ ] Mesmo teste acima
- [ ] Verificar prioridade: upload deve ser rápido

**Para Energia (S9):**
- [ ] Mesmo teste

### Teste de upload + aprovação

- [ ] Upload arquivo PDF: `MANT-2026-ROD-001-Mem-Descritivo-03-v1.0.pdf`
- [ ] Preencher metadados: ✓ Segmento | ✓ Fase | ✓ Numero-projeto | ✓ Tipo | ✓ Status=Rascunho
- [ ] Mudar status para "Revisão"
- [ ] Revisor clica, muda para "Aprovado"
- [ ] Aguardar 5 min
- [ ] Verificar: arquivo sincronizou com Jericó? (URL aparece em Link-Jerico)

### Teste RAG + Busca

- [ ] Aprovados 5 documentos em diferentes segmentos
- [ ] Aguardar job sync (até 6h conforme cron)
- [ ] Testar busca Maestro: "encontre memoriais de saneamento"
- [ ] Resultado deve trazer chunks de `san:*` do Supabase

### Teste de permissões granulares

- [ ] Usuário de Rodovias não consegue acessar Saneamento (403)?
- [ ] Usuário "Leitura" não consegue editar em `Orcamento-executivo/` (read-only)?

**Status Fase 7:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 8: TREINAMENTO (Dia 13)

### Preparar materiais

- [ ] Imprimir/enviar: PLANO-SHAREPOINT-MANTA-v4.2.md
- [ ] Imprimir/enviar: CHECKLIST-RAPIDO-SHAREPOINT.md (este arquivo)
- [ ] Criar 1-min video: "Como fazer upload"
- [ ] Criar 1-min video: "Como submeter para aprovação"
- [ ] Preparar FAQ (dúvidas comuns)

### Sessões de treinamento (por segmento)

**Rodovias (S1):**
- [ ] Data: [--/--/2026]
- [ ] Participantes: [listar coordenadores]
- [ ] Tópicos: navegação, upload, metadados, aprovação, Jericó
- [ ] Q&A: registrar dúvidas

**OAE (S2):**
- [ ] Data: [--/--/2026]
- [ ] [idem]

**[continuar para S3, S4, S6, S7, S8, S9, S10]**

### Documentação para usuários

- [ ] Criar arquivo WIKI: "Como fazer upload — Rodovias"
- [ ] Criar arquivo WIKI: "Como fazer upload — Saneamento"
- [ ] [idem para outros segmentos]
- [ ] Salvar em: `02-padrao-manta/processos-comuns/` com link em cada segmento

**Status Fase 8:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## ✅ FASE 9: GO-LIVE (Dia 14-15)

### Dia 14: Liberação para todos

- [ ] Enviar email aos líderes técnicos de cada segmento
- [ ] Assunto: "SharePoint Manta pronto para uso"
- [ ] Incluir: link plano, link FAQ, email de suporte TI
- [ ] Liberar acesso: remover restrições piloto

### Dia 15: Suporte e ajustes

- [ ] Monitorar: erros, dúvidas nos primeiros dias
- [ ] Criar log de issues: "SharePoint-Issues-Log.xlsx"
- [ ] Resolver em < 24h se possível
- [ ] Documentar soluções para FAQ

### Após 1 semana: Lições aprendidas

- [ ] [ ] Reunião retrospectiva com TI + leads
- [ ] [ ] Registrar em: `04-admin/Audit-logs/Jericoes-Aprendidas-v4.2.md`
- [ ] [ ] Atualizar plano para v4.3 (se necessário)

**Status Fase 9:** [ ] NÃO INICIADA [ ] EM ANDAMENTO [ ] COMPLETA ✅

---

## 📋 SUMÁRIO DE PROGRESSO

```
Fase 1 (Estrutura):       [████████░░░░░░░░░░░░] 40%
Fase 2 (Metadata):        [██░░░░░░░░░░░░░░░░░░] 10%
Fase 3 (Permissões):      [░░░░░░░░░░░░░░░░░░░░]  0%
Fase 4 (Templates):       [░░░░░░░░░░░░░░░░░░░░]  0%
Fase 5 (Jericó):          [░░░░░░░░░░░░░░░░░░░░]  0%
Fase 6 (Views):           [░░░░░░░░░░░░░░░░░░░░]  0%
Fase 7 (Testes):          [░░░░░░░░░░░░░░░░░░░░]  0%
Fase 8 (Treinamento):     [░░░░░░░░░░░░░░░░░░░░]  0%
Fase 9 (Go-live):         [░░░░░░░░░░░░░░░░░░░░]  0%

TOTAL GERAL:              [████░░░░░░░░░░░░░░░░]  7%
```

---

## 📞 SUPORTE

**Problemas de acesso?**
- Contactar: IT Help Desk (`it-suporte@mantaassociados.com`)
- Incluir: nome, segmento, erro exato

**Problemas técnicos (DWG, PDF, Excel)?**
- Contactar: Maestro Admin (`maestro@mantaassociados.com`)

**Dúvidas sobre processo?**
- Consultar: PLANO-SHAREPOINT-MANTA-v4.2.md (seção correspondente)
- Ou: líder técnico do seu segmento

---

**Documento gerado:** 2026-07-25  
**Versão:** 1.0  
**Ticket:** MNT-2026-UPGRADE-SP-INFRASTRUCTURE
