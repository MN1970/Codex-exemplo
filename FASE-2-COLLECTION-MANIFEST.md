# FASE 2 — Collection Manifest
## Especificação Completa de 950+ Documentos a Coletar

**Data:** 2026-07-22  
**Status:** Ready for Collection  
**Total Estimado:** 950 documentos

---

## 📋 Como Usar Este Manifest

1. **Estrutura de Diretórios:**
   ```
   data/rag-docs/
   ├── san:/          # Saneamento (200 docs)
   ├── ene:/          # Energia (300 docs)
   ├── por:/          # Portos (150 docs)
   ├── aer:/          # Aeroportos (120 docs)
   └── bar:/          # Barragens (180 docs)
   ```

2. **Fazer Download:**
   - Seguir URLs e instruções de coleta para cada coleção
   - Salvar em diretório correspondente
   - Nomes de arquivo: `{sigla}-{ano}-{tema}-{número}.{ext}`
     - Ex: `SNIS-2025-Diagnostico-001.pdf`

3. **Validar:**
   ```bash
   # Verificar documentos coletados
   ls -lh data/rag-docs/san:/
   ls -lh data/rag-docs/ene:/
   # etc...
   ```

4. **Processar:**
   ```bash
   SUPABASE_URL=<url> SUPABASE_KEY=<key> ./scripts/extract-and-populate-rag.sh
   ```

---

## 🔴 Coleção `san:` — SANEAMENTO (200 documentos) — PRIORIDADE ALTA (AYSÁ)

### Fonte 1: SNIS — Sistema Nacional de Informações sobre Saneamento

**URL:** https://www.gov.br/snirh/pt-br/centrais-de-conteudo/publicacoes/snis

| # | Documento | Ano | Tipo | Estimado |
|---|-----------|-----|------|----------|
| 1 | Diagnóstico dos Serviços de Água e Esgoto | 2023 | PDF | 40 pages |
| 2 | Diagnóstico dos Serviços de Água e Esgoto | 2024 | PDF | 45 pages |
| 3 | Diagnóstico dos Serviços de Água e Esgoto | 2025 | PDF | 50 pages |
| 4 | Série Histórica — Água | 2020-2025 | XLSX | 100 rows |
| 5 | Série Histórica — Esgoto | 2020-2025 | XLSX | 100 rows |

**Próximos Passos:**
- [ ] Download SNIS-2023-Diagnostico.pdf
- [ ] Download SNIS-2024-Diagnostico.pdf
- [ ] Download SNIS-2025-Diagnostico.pdf
- [ ] Download SNIS-SerieHistorica-Agua.xlsx
- [ ] Download SNIS-SerieHistorica-Esgoto.xlsx
- [ ] Copiar para `data/rag-docs/san:/`

---

### Fonte 2: BNDES — Banco Nacional de Desenvolvimento

**URL:** https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/saneamento

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Manual de Saneamento Básico | PDF | 150 pages |
| 2 | Normas Técnicas de ETA | PDF | 80 pages |
| 3 | Normas Técnicas de ETE | PDF | 120 pages |
| 4 | Guia de Adutoras | PDF | 90 pages |
| 5 | Diretrizes de Financiamento | PDF | 40 pages |

---

### Fonte 3: Legislação e Normas

**URLs:**
- Lei 14.026/2020: https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14026.htm
- NBR 12211: Norma de Engenharia de Saneamento
- NBR 12212: Abastecimento de Água
- NBR 12213: Sistemas de Tratamento de Água
- NBR 12215: Tubulações para Água
- NBR 12216: ETA
- NBR 12217: Reservatórios
- NBR 12218: Rede de Distribuição

**Próximos Passos:**
- [ ] Download Lei 14.026 (PDF)
- [ ] Obter NBR 12211-12218 (contato com ABNT)
- [ ] Copiar para `data/rag-docs/san:/`

---

### Fonte 4: IWA — International Water Association

**URL:** https://www.iwahq.org/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Water Supply Systems | PDF | 60 pages |
| 2 | Wastewater Treatment | PDF | 85 pages |
| 3 | Water Quality Standards | PDF | 40 pages |

---

### Fonte 5: ANA — Agência Nacional de Águas

**URL:** https://www.ana.gov.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Plano de Segurança da Água | PDF | 50 pages |
| 2 | Gestão de Recursos Hídricos | PDF | 100 pages |
| 3 | Relatório de Situação | Anual | PDF | 80 pages |

---

### Fonte 6: Ministério das Cidades / MCIDADES

**URL:** https://www.gov.br/mcidades/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Editais de Financiamento (últimos 5 anos) | PDF | 50 × 5 = 250 pages |
| 2 | Diretrizes Técnicas | PDF | 80 pages |

---

**TOTAL `san:`:** ~1,500 páginas = ~200 documentos após chunkarização

---

## 🔴 Coleção `ene:` — ENERGIA (300 documentos) — PRIORIDADE ALTA (ANEEL)

### Fonte 1: ANEEL — Agência Nacional de Energia Elétrica

**URL:** https://www.aneel.gov.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Resoluções Técnicas (2020-2026) | PDF | 80 |
| 2 | Editais de Leilão (últimos 5 anos) | PDF | 50 |
| 3 | Relatórios de Leilão | PDF | 40 |
| 4 | RAP (Receita Anual Permitida) — Exemplo | PDF | 30 |

---

### Fonte 2: EPE — Empresa de Pesquisa Energética

**URL:** https://www.epe.gov.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | PDE 2025 (Plano Decenal) | PDF | 200 pages |
| 2 | Relatório R1 — Demanda | PDF | 80 pages |
| 3 | Relatório R2 — Oferta Hidro | PDF | 60 pages |
| 4 | Relatório R3 — Oferta Térmico | PDF | 60 pages |
| 5 | Relatório R4 — Oferta Eólico/Solar | PDF | 50 pages |
| 6 | Relatório R5 — Transmissão | PDF | 70 pages |

---

### Fonte 3: ONS — Operador Nacional do Sistema

**URL:** https://www.ons.org.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Procedimentos de Rede (Revisão Anual) | PDF | 500 pages |
| 2 | Relatórios Operacionais (últimos 12 meses) | PDF | 100 pages |
| 3 | Guia de Acesso | PDF | 150 pages |

---

### Fonte 4: IEEE Standards

**URL:** https://www.ieee.org/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | IEEE 738 — Ampacity Calculation | PDF | 40 pages |
| 2 | IEEE 1243 — Design Guide for Power Distribution | PDF | 60 pages |
| 3 | IEEE 1100 — Recommended Practice for Grounding | PDF | 50 pages |

---

### Fonte 5: State Grid / Concessionárias

**Exemplo URLs:**
- ISA CTEEP: https://www.isaenergia.com.br/
- Alupar: https://www.alupar.com.br/
- Taesa: https://www.taesa.com.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Relatórios Técnicos (por concessionária) | PDF | 30 × 5 = 150 |
| 2 | Manuais Operacionais | PDF | 20 × 5 = 100 |
| 3 | Projetos Executivos (exemplos) | PDF | 15 × 3 = 45 |

---

### Fonte 6: BNDES Energia

**URL:** https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/energia

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Análise de Projetos de Energia | PDF | 50 |
| 2 | Diretrizes de Financiamento | PDF | 30 |

---

### Fonte 7: Legislação

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Lei 9.074/1995 (Concessões) | TXT | 20 |
| 2 | Decretos Regulatórios (últimas 5 edições) | PDF | 5 × 10 = 50 |

---

**TOTAL `ene:`:** ~2,500 páginas = ~300 documentos após chunkarização

---

## 🟡 Coleção `por:` — PORTOS (150 documentos) — Média Prioridade

### Fonte 1: ANTAQ — Agência Nacional de Transportes Aquaviários

**URL:** https://www.gov.br/antaq/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Regulamentações Portuárias | PDF | 80 |
| 2 | Editais TUP (últimos 5 anos) | PDF | 50 |
| 3 | Relatórios de Movimentação (anuais) | PDF | 20 |

---

### Fonte 2: PIANC — Permanent International Association

**URL:** https://www.pianc.org/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Port Design & Construction | PDF | 40 |
| 2 | Dredging & Maintenance | PDF | 25 |

---

### Fonte 3: BNDES Portos

**URL:** https://www.bndes.gov.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Estudos de Viabilidade Portuária | PDF | 30 |

---

**TOTAL `por:`:** ~1,200 páginas = ~150 documentos

---

## 🟡 Coleção `aer:` — AEROPORTOS (120 documentos) — Média Prioridade

### Fonte 1: ANAC — Agência Nacional de Aviação Civil

**URL:** https://www.gov.br/anac/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | RBAC (Regulamento Brasileiro de Aviação) | PDF | 100 pages |
| 2 | Normas de Infraestrutura | PDF | 80 pages |
| 3 | Editais de Concessão | PDF | 40 pages |

---

### Fonte 2: ICAO — International Civil Aviation

**URL:** https://www.icao.int/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Annex 14 — Aerodromes | PDF | 120 pages |
| 2 | Diretrizes Internacionais | PDF | 60 pages |

---

### Fonte 3: FAA — Federal Aviation Administration

**URL:** https://www.faa.gov/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Advisory Circulars (ACs) | PDF | 50 pages |

---

**TOTAL `aer:`:** ~900 páginas = ~120 documentos

---

## 🟡 Coleção `bar:` — BARRAGENS (180 documentos) — Média Prioridade

### Fonte 1: ICOLD — International Commission on Large Dams

**URL:** https://www.icold-cigb.org/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Diretrizes de Projeto | PDF | 80 pages |
| 2 | Boas Práticas Internacionais | PDF | 60 pages |

---

### Fonte 2: CBDB — Comitê Brasileiro de Barragens

**URL:** https://www.cbdb.org.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Normas Técnicas Brasileiras | PDF | 100 pages |
| 2 | Estudos de Casos | PDF | 80 pages |

---

### Fonte 3: SIGBM — Sistema de Informações

**URL:** https://www.snisb.gov.br/

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Banco de Dados de Barragens | XLSX | 500 rows |
| 2 | Inspeções e Monitoramento | PDF | 100 pages |

---

### Fonte 4: Legislação

| # | Documento | Tipo | Estimado |
|---|-----------|------|----------|
| 1 | Lei 12.334/2010 (Segurança de Barragens) | TXT | 20 |
| 2 | Resoluções ANEEL/ANA | PDF | 30 |

---

**TOTAL `bar:`:** ~1,400 páginas = ~180 documentos

---

## 📊 Sumário de Coleta

| Coleção | Tipo | Documentos | Status | Responsável |
|---------|------|-----------|--------|-------------|
| san: (Saneamento) | 200 | 🟢 Ready | ⏳ A Coletar | AYSÁ Team |
| ene: (Energia) | 300 | 🟢 Ready | ⏳ A Coletar | ANEEL Team |
| por: (Portos) | 150 | 🟢 Ready | ⏳ A Coletar | Pesquisa |
| aer: (Aeroportos) | 120 | 🟢 Ready | ⏳ A Coletar | Pesquisa |
| bar: (Barragens) | 180 | 🟢 Ready | ⏳ A Coletar | Pesquisa |
| **TOTAL** | **950** | | | |

---

## 🚀 Quick Start

### 1. Criar estrutura de diretórios

```bash
mkdir -p data/rag-docs/{san,ene,por,aer,bar}
```

### 2. Download de documentos

```bash
# Exemplo: SNIS 2025
wget -O data/rag-docs/san:/SNIS-2025-Diagnostico.pdf \
  https://www.gov.br/snirh/snis-2025.pdf

# Exemplo: PDE 2025 (EPE)
wget -O data/rag-docs/ene:/EPE-PDE-2025.pdf \
  https://www.epe.gov.br/pde-2025.pdf
```

### 3. Validar coleta

```bash
# Contar documentos por coleção
for col in san ene por aer bar; do
  count=$(ls -1 data/rag-docs/${col}/ | wc -l)
  echo "${col}: $count documentos"
done
```

### 4. Processar RAG

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Modo dry-run (para testar)
DRY_RUN=true ./scripts/extract-and-populate-rag.sh

# Modo real
./scripts/extract-and-populate-rag.sh
```

### 5. Validar inserção

```bash
# Contar chunks por coleção
curl -s "${SUPABASE_URL}/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer ${SUPABASE_KEY}" | jq .

# Exemplo resultado: 950 chunks
```

---

## 📝 Notas Importantes

1. **Acesso a Documentos Protegidos:**
   - ABNT (NBR): Requerer acesso via dneves@mantaassociados.com
   - ICOLD: Acesso pago (~$500/ano para instituição)
   - Outros: Maioria é acesso público

2. **Licenças:**
   - Todos os documentos colhidos devem ter licença de uso apropriada
   - Documentos públicos (Lei, ABNT por Lei) ✅
   - Documentos de órgãos federais (ANEEL, ANA, EPE) ✅
   - Publicações acadêmicas: Verificar licença

3. **Nomeação de Arquivos:**
   ```
   {SIGLA}-{ANO}-{TEMA}-{NUMERO}.{EXT}
   
   Exemplos:
   SNIS-2025-Diagnostico-001.pdf
   EPE-2025-PDE-001.pdf
   ANAC-2024-RBAC-001.pdf
   ANTAQ-2023-TUP-Edital-001.pdf
   ```

4. **Tamanho Máximo:**
   - Documentos individuais: até 50MB
   - Chunks: até 5KB de texto limpo
   - Total RAG: até 100MB em Supabase

---

**Status:** Ready for collection phase  
**Próximo Passo:** Execução de coleta (ETA: 1 semana)

