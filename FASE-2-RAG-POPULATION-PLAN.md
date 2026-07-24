# FASE 2 — População RAG com 950+ Documentos
## Plano de Execução e Validação v5.0.0

**Status:** ✅ Planejado — 2026-07-22  
**Timeline:** 1 semana (Sprint 1 de 3)  
**Escopo:** População de 5 coleções RAG em Supabase com 950+ documentos validados

---

## 📋 Resumo Executivo

A Fase 2 popula as 5 coleções RAG definidas na Fase 1 com documentação técnica, regulatória e comercial de fontes autorizadas.

| Coleção | Docs | Fontes | Prioridade | Status |
|---------|------|--------|-----------|--------|
| `san:` (Saneamento) | 200 | SNIS, IWA, NBR, Lei 14.026, BNDES | 🔴 ALTA (AYSÁ) | ⏳ Planejado |
| `ene:` (Energia) | 300 | ANEEL, EPE R1-R5, ONS, IEEE | 🔴 ALTA (ANEEL) | ⏳ Planejado |
| `por:` (Portos) | 150 | ANTAQ, PIANC, BNDES, TUP editais | 🟡 Média | ⏳ Planejado |
| `aer:` (Aeroportos) | 120 | ANAC/RBAC, ICAO Annex 14, FAA | 🟡 Média | ⏳ Planejado |
| `bar:` (Barragens) | 180 | ICOLD, CBDB, SIGBM, Lei 12.334 | 🟡 Média | ⏳ Planejado |
| **TOTAL** | **950** | — | — | ⏳ Planejado |

---

## 🎯 Objetivos da Fase 2

1. **Coleta de Documentos:** Agregar 950+ docs de fontes autorizadas
2. **Extração de Conteúdo:** Converter PDFs, DOCXs, excels em texto estruturado
3. **Chunkarização:** Dividir documentos em chunks de 1000 caracteres com metadados
4. **Validação:** Aplicar aluci-guard para garantir qualidade (confidence ≥ 0.85)
5. **Inserção:** Carregar chunks para Supabase com rastreamento de origem
6. **Verificação:** Validar 950+ chunks inseridos e acessíveis via RAG

---

## 📂 Estrutura de Dados e Metadados

### Chunk Structure (rag_chunks)

```json
{
  "id": "uuid",
  "collection_prefix": "san:",
  "segment": "S8",
  "document_id": "doc-2026-07-snis-001",
  "chunk_index": 0,
  "content": "Texto do chunk (max 1000 caracteres)...",
  "source_url": "https://snis.gov.br/...",
  "source_type": "snis|bndes|lei|norma|editorial",
  "metadata": {
    "document_title": "SNIS 2025 - Diagnóstico de Saneamento",
    "publication_date": "2025-06-15",
    "author": "ANA/SNIS",
    "document_version": "2025.1"
  },
  "confidence_score": 0.92,
  "validation_status": "validated",
  "validated_by": "aluci-guard",
  "validated_at": "2026-07-22T10:30:00Z",
  "tags": ["saneamento", "snis", "agua-tratada", "diagnostico"],
  "created_at": "2026-07-22T10:30:00Z",
  "updated_at": "2026-07-22T10:30:00Z"
}
```

### Metadados de Documento

```json
{
  "document_id": "doc-2026-07-snis-001",
  "title": "SNIS 2025 - Diagnóstico de Saneamento",
  "collection": "san:",
  "segment": "S8",
  "source": "https://snis.gov.br/dados-2025",
  "source_type": "snis",
  "publication_date": "2025-06-15",
  "language": "pt-BR",
  "domain": "saneamento básico",
  "file_format": "pdf",
  "file_size_kb": 2450,
  "total_pages": 145,
  "total_chunks": 145,
  "confidence_baseline": 0.92,
  "quality_score": "A",
  "tags": ["saneamento", "snis", "agua-tratada", "diagnostico"],
  "extracted_at": "2026-07-22T10:30:00Z"
}
```

---

## 📚 Fontes de Dados por Coleção

### Coleção `san:` (Saneamento) — 200 docs

**Prioridade:** 🔴 ALTA (AYSÁ)  
**Update Freq:** Mensal

#### Fontes Primárias

1. **SNIS — Sistema Nacional de Informações sobre Saneamento**
   - Banco de dados de prestadores de água/esgoto
   - Relatórios anuais: 2023, 2024, 2025
   - Diagnósticos por estado e região
   - Estimado: 40 documentos

2. **BNDES — Editoriais e Normas Técnicas**
   - Manuais de saneamento
   - Estudos de viabilidade
   - Normas de contratação
   - Estimado: 35 documentos

3. **Legislação e Normas**
   - Lei 14.026/2020 (Marco Legal)
   - NBR 12211-12218 (Engenharia de Saneamento)
   - Resoluções CONAMA
   - Estimado: 25 documentos

4. **IWA — International Water Association**
   - Relatórios internacionais
   - Best practices em tratamento
   - Estimado: 30 documentos

5. **ANA — Agência Nacional de Águas**
   - Relatórios de gestão de recursos hídricos
   - Planos de bacia
   - Estimado: 35 documentos

6. **Ministério das Cidades / MCIDADES**
   - Editais de financiamento
   - Diretrizes técnicas
   - Estimado: 15 documentos

**Total Estimado:** 180-200 documentos

### Coleção `ene:` (Energia) — 300 docs

**Prioridade:** 🔴 ALTA (ANEEL)  
**Update Freq:** Semanal

#### Fontes Primárias

1. **ANEEL — Agência Nacional de Energia Elétrica**
   - Resoluções e normas técnicas
   - RAP (Receita Anual Permitida)
   - Editais de transmissão e distribuição
   - Relatórios de leilões 2023-2025
   - Estimado: 80 documentos

2. **EPE — Empresa de Pesquisa Energética**
   - PDE (Plano Decenal de Expansão)
   - Relatórios R1-R5
   - Projeções de demanda
   - Estimado: 50 documentos

3. **ONS — Operador Nacional do Sistema**
   - Procedimentos de rede
   - Relatórios operacionais
   - Guias de acesso
   - Estimado: 35 documentos

4. **IEEE Standards**
   - Normas de transmissão (IEEE 738, 1243)
   - Cálculo de ampacidade
   - Estimado: 25 documentos

5. **State Grid / Concessionárias**
   - Relatórios técnicos de LT (Linhas de Transmissão)
   - Projetos executivos
   - Manuais operacionais
   - Estimado: 60 documentos

6. **BNDES Energia**
   - Análise de projetos
   - Diretrizes de financiamento
   - Estimado: 30 documentos

7. **Legislação**
   - Lei 9.074/1995 (Concessões)
   - Decretos regulatórios
   - Estimado: 20 documentos

**Total Estimado:** 300 documentos

### Coleção `por:` (Portos) — 150 docs

**Prioridade:** 🟡 Média  
**Update Freq:** Semestral

#### Fontes Primárias

1. **ANTAQ — Agência Nacional de Transportes Aquaviários**
   - Regulamentações portuárias
   - Editais TUP (Terminais de Uso Privativo)
   - Relatórios de movimentação
   - Estimado: 50 documentos

2. **PIANC — Permanent International Association of Navigation Congresses**
   - Diretrizes de projeto de terminais
   - Boas práticas internacionais
   - Estimado: 25 documentos

3. **BNDES Portos**
   - Estudos de viabilidade
   - Análise de projetos portuários
   - Estimado: 30 documentos

4. **Editais de Concessão e TUP**
   - Projetos de portos públicos
   - Edital TUP (últimos 5 anos)
   - Estimado: 25 documentos

5. **Normas Técnicas**
   - NBR sobre estruturas portuárias
   - Dragagem e derrocamento
   - Estimado: 20 documentos

**Total Estimado:** 150 documentos

### Coleção `aer:` (Aeroportos) — 120 docs

**Prioridade:** 🟡 Média  
**Update Freq:** Semestral

#### Fontes Primárias

1. **ANAC — Agência Nacional de Aviação Civil**
   - RBAC (Regulamento Brasileiro de Aviação Civil)
   - Normas de infraestrutura
   - Editais de concessão
   - Estimado: 40 documentos

2. **ICAO — International Civil Aviation Organization**
   - Annex 14 (Aerodromes)
   - Diretrizes internacionais
   - Estimado: 20 documentos

3. **FAA — Federal Aviation Administration**
   - Advisory Circulars (ACs)
   - Boas práticas norte-americanas
   - Estimado: 15 documentos

4. **BNDES Aeroportos**
   - Estudos de viabilidade
   - Análise de projetos
   - Estimado: 20 documentos

5. **Editais de Concessão**
   - Infraero / Concessões privadas (últimos 5 anos)
   - Especificações técnicas
   - Estimado: 25 documentos

**Total Estimado:** 120 documentos

### Coleção `bar:` (Barragens) — 180 docs

**Prioridade:** 🟡 Média  
**Update Freq:** Trimestral

#### Fontes Primárias

1. **ICOLD — International Commission on Large Dams**
   - Diretrizes de projeto
   - Boas práticas internacionais
   - Estimado: 30 documentos

2. **CBDB — Comitê Brasileiro de Barragens**
   - Normas técnicas brasileiras
   - Estudos de casos
   - Estimado: 25 documentos

3. **SIGBM — Sistema de Informações sobre Segurança de Barragens**
   - Banco de dados de barragens
   - Inspeções e monitoramento
   - Estimado: 35 documentos

4. **Legislação**
   - Lei 12.334/2010 (Política de Segurança de Barragens)
   - Resoluções ANEEL/ANA
   - Estimado: 20 documentos

5. **BNDES Infraestrutura Hídrica**
   - Estudos de viabilidade
   - Análise de projetos
   - Estimado: 30 documentos

6. **Agências Reguladoras (ANEEL, ANA)**
   - Diretrizes técnicas
   - Procedimentos de fiscalização
   - Estimado: 25 documentos

7. **Casos de Estudo**
   - Projetos executivos de barragens brasileiras
   - Estimado: 15 documentos

**Total Estimado:** 180 documentos

---

## 🔄 Processo de Extração e Validação

### Pipeline de Processamento

```
Documento Fonte (PDF/DOCX/etc)
    ↓
[1. Extração de Conteúdo]
    ├─ PDF → pdftotext / pdfplumber
    ├─ DOCX → python-docx
    ├─ XLSX → openpyxl
    └─ TXT → read direto
    ↓
[2. Limpeza e Normalização]
    ├─ Remover headers/footers
    ├─ Normalizar whitespace
    ├─ Remove linhas vazias
    └─ Detectar idioma (pt-BR/en)
    ↓
[3. Estruturação de Metadados]
    ├─ Extrair título
    ├─ Detectar data de publicação
    ├─ Classificar por domínio
    └─ Gerar lista de tags
    ↓
[4. Chunkarização]
    ├─ Dividir em chunks de ~1000 chars
    ├─ Manter quebra de parágrafo
    ├─ Numerar chunks (chunk_index)
    └─ Preservar contexto (títulos de seção)
    ↓
[5. Validação com aluci-guard]
    ├─ Verificar factualidade (confidence_score)
    ├─ Detectar alucinações
    ├─ Validar referências
    └─ Confidence ≥ 0.85 → ✓ PASS
    ↓
[6. Inserção em Supabase]
    ├─ INSERT INTO rag_chunks (...)
    ├─ Registrar em sharepoint_sync_log
    ├─ Atualizar rag_collection_status
    └─ Validar constraint checks
    ↓
[7. Verificação Final]
    ├─ Verificar row count por coleção
    ├─ Validar avg confidence_score
    └─ Testar busca semântica
```

### Validação com aluci-guard

Todos os chunks devem passar por validação:

```bash
# Pseudo-código da validação

for chunk in extracted_chunks:
  validation_result = aluci_guard.validate(
    content=chunk.text,
    context="domain: saneamento, section: ETA design",
    confidence_threshold=0.85
  )
  
  if validation_result.confidence >= 0.85:
    chunk.validation_status = "validated"
    chunk.confidence_score = validation_result.score
  else:
    chunk.validation_status = "pending"
    chunk.confidence_score = validation_result.score
    log_warning(f"Low confidence for chunk: {chunk.id}")
```

---

## 📊 Timeline e Milestones

### Semana 1 (Sprint 1)

| Dia | Tarefa | Responsável | Status |
|-----|--------|-------------|--------|
| Seg 22/07 | Setup de pipeline de extração | DevOps | ⏳ |
| Ter 23/07 | Coletar 200 docs saneamento (san:) | Pesquisa | ⏳ |
| Qua 24/07 | Coletar 300 docs energia (ene:) | Pesquisa | ⏳ |
| Qui 25/07 | Coletar 150 docs portos (por:) | Pesquisa | ⏳ |
| Sex 26/07 | Coletar 120 docs aeroportos (aer:) | Pesquisa | ⏳ |
| Sab 27/07 | Coletar 180 docs barragens (bar:) | Pesquisa | ⏳ |
| Dom 28/07 | Processamento e validação de todos (950 docs) | DevOps | ⏳ |

### Validações Finais

- [ ] 950+ chunks validados com aluci-guard
- [ ] Avg confidence_score ≥ 0.88 por coleção
- [ ] Todos os chunks com metadados completos
- [ ] Busca semântica funcional para cada coleção

---

## 🗂️ Script de Extração e Inserção

### `scripts/extract-and-populate-rag.sh`

```bash
#!/bin/bash

# Extração de documentos, validação e inserção em Supabase

for collection_prefix in "san:" "ene:" "por:" "aer:" "bar:"; do
  echo "Processando coleção: $collection_prefix"
  
  # 1. Listar documentos da pasta
  for doc in /mnt/docs/$collection_prefix/*.pdf; do
    # 2. Extrair conteúdo
    pdftotext "$doc" - | convert_to_utf8 > content.txt
    
    # 3. Chunkarizar
    create_chunks "$content.txt" 1000 > chunks.json
    
    # 4. Validar com aluci-guard
    validate_with_aluci_guard chunks.json > validated_chunks.json
    
    # 5. Inserir em Supabase
    for chunk in validated_chunks.json; do
      curl -X POST "$SUPABASE_URL/rest/v1/rag_chunks" \
        -H "Authorization: Bearer $SUPABASE_KEY" \
        -d "$chunk"
    done
  done
  
  # 6. Atualizar status de coleção
  update_collection_status "$collection_prefix"
done
```

---

## 🧪 Testes de Validação

### Test 1: Contagem de Chunks

```sql
-- Verificar 950+ chunks total
SELECT collection_prefix, COUNT(*) as chunk_count
FROM rag_chunks
GROUP BY collection_prefix
ORDER BY collection_prefix;

-- Expected:
-- san: | 200 chunks
-- ene: | 300 chunks
-- por: | 150 chunks
-- aer: | 120 chunks
-- bar: | 180 chunks
-- Total: 950+ chunks
```

### Test 2: Validação Quality

```sql
-- Verificar confidence scores
SELECT 
  collection_prefix,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE confidence_score >= 0.85) as validated,
  AVG(confidence_score)::NUMERIC(3,2) as avg_confidence
FROM rag_chunks
GROUP BY collection_prefix;

-- Expected:
-- Todas as coleções: avg_confidence >= 0.85
-- Validated >= 95% do total
```

### Test 3: Busca Semântica

```bash
# Testar busca por coleção
curl -X POST "$SUPABASE_URL/rest/v1/rpc/rag_search" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -d '{
    "collection": "san:",
    "query": "ETA tratamento agua",
    "limit": 5
  }' | jq .

# Expected: 5 chunks mais relevantes com confidence > 0.85
```

### Test 4: Integração com Agentes

```bash
# Testar acesso do agente-saneamento à coleção san:
curl -X POST "$CLAUDE_API/messages" \
  -H "Authorization: Bearer $CLAUDE_KEY" \
  -d '{
    "model": "claude-opus-4.1",
    "system": "Você é agente-saneamento. Acesse RAG san: para responder.",
    "messages": [{
      "role": "user",
      "content": "Qual é a taxa média de cobertura de água tratada no Brasil?"
    }]
  }'

# Expected: Resposta fundamentada em documentos do RAG (SNIS, ANA, etc)
```

---

## 📋 Checklist da Fase 2

### Pré-requisitos
- [ ] Acesso a SNIS, ANEEL, ANTAQ, ANAC, ICOLD, etc
- [ ] Documentos salvos em `/mnt/docs/{collection}/`
- [ ] Python 3.8+ com pdftotext, python-docx, openpyxl
- [ ] aluci-guard disponível para validação
- [ ] Supabase com schema da Fase 1 já aplicado

### Extração e Inserção
- [ ] 200 docs saneamento extraídos e validados
- [ ] 300 docs energia extraídos e validados
- [ ] 150 docs portos extraídos e validados
- [ ] 120 docs aeroportos extraídos e validados
- [ ] 180 docs barragens extraídos e validados
- [ ] Total: 950+ chunks em Supabase

### Qualidade
- [ ] Avg confidence_score ≥ 0.88 por coleção
- [ ] ≥ 95% dos chunks com validation_status = "validated"
- [ ] Todos os chunks com metadados completos (tags, source_url, etc)
- [ ] Sem chunks duplicados

### Testes de Integração
- [ ] Busca semântica funciona para cada coleção
- [ ] Agentes conseguem acessar RAG via conhecimento_mapping
- [ ] Queries retornam chunks relevantes (confidence > 0.85)
- [ ] Performance aceitável (<500ms por query)

---

## 🚀 Próximo Passo: Fase 3

Após conclusão da Fase 2:
- Implementar advanced orchestration com load balancing
- Adicionar fila de prioridades (ALTA > Média)
- Implementar caching e índices semânticos
- Monitoramento em tempo real de execução

---

**Mantido por:** mneves@mantaassociados.com  
**Versão:** 5.0.0 | **Data:** 2026-07-22 | **Timeline:** 1 semana
