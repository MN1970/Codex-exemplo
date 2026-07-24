# FASE 2 — EXECUÇÃO IMEDIATA
**Data:** 2026-07-23  
**Status:** 🚀 COMEÇANDO AGORA  
**Timeline:** 5 dias (coleta) + 2 horas (processamento)  
**Resultado Final:** 947+ chunks em Supabase, pronto para Fase 3

---

## ✅ Checklist Rápido (Antes de Começar)

- [ ] Criar diretório `data/rag-docs/` com 5 subpastas (san, ene, por, aer, bar)
- [ ] Instalar Python dependencies: `pip3 install PyPDF2 python-docx openpyxl`
- [ ] Ter SUPABASE_URL e SUPABASE_KEY prontos
- [ ] Ler este documento por completo (10 minutos)
- [ ] Abrir FASE-2-COLLECTION-MANIFEST.md em paralelo

---

## 📁 PASSO 1: Setup de Diretórios (2 minutos)

```bash
cd /home/user/Codex-exemplo

# Criar estrutura
mkdir -p data/rag-docs/{san,ene,por,aer,bar}
mkdir -p logs/rag-population

# Verificar
ls -la data/rag-docs/
# Deve mostrar: san  ene  por  aer  bar
```

---

## 🔧 PASSO 2: Preparar Ambiente (3 minutos)

```bash
# Instalar dependências Python
pip3 install PyPDF2 python-docx openpyxl

# Verificar scripts existem
ls -la scripts/extract-and-populate-rag.sh
ls -la scripts/rag-extraction-utils.py

# Definir variáveis de ambiente
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Testar conexão Supabase
curl -s "$SUPABASE_URL/rest/v1/" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "apikey: $SUPABASE_KEY" | head -20
```

---

## 📥 PASSO 3: Coletar Documentos (5 dias, 10-12 horas)

### DIA 1 (Hoje — 23 Jul) — Documentos Públicos (2-3 horas)

**Objective:** Baixar ~320 documentos de fontes públicas

#### 3.1.1 Leis Federais (30 min)

Baixar de planalto.gov.br:
```bash
# Lei 14.026/2020 (Saneamento)
wget "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14026.htm" \
  -O data/rag-docs/san/lei-14026-2020.pdf

# Lei 9.074/1995 (Energia)
wget "https://www.planalto.gov.br/ccivil_03/leis/l9074.htm" \
  -O data/rag-docs/ene/lei-9074-1995.pdf

# Lei 12.815/2013 (Portos)
wget "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12815.htm" \
  -O data/rag-docs/por/lei-12815-2013.pdf

# Lei 13.182/2015 (Aeroportos)
wget "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13182.htm" \
  -O data/rag-docs/aer/lei-13182-2015.pdf

# Lei 12.334/2010 (Barragens)
wget "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12334.htm" \
  -O data/rag-docs/bar/lei-12334-2010.pdf
```

#### 3.1.2 Documentos BNDES (1 hora)

Visitar https://www.bndes.gov.br/ → Financiamento → Saneamento/Energia/Infraestrutura

Download manual:
- Manuais de projeto (5+ documentos)
- Diretrizes de viabilidade (3+ documentos)
- Guias de execução (3+ documentos)
- Salvar em: `data/rag-docs/san/` ou `data/rag-docs/ene/`

**Target:** 50+ documentos BNDES

#### 3.1.3 SNIS & Estatísticas (30 min)

Visitar https://www.snirh.gov.br/ 

Download:
- Série histórica água/esgoto (Excel)
- Diagnósticos (PDF)
- Indicadores (CSV/Excel)
- Salvar em: `data/rag-docs/san/`

**Target:** 30+ documentos SNIS

#### 3.1.4 Verificação Dia 1
```bash
count_san=$(find data/rag-docs/san -type f | wc -l)
count_ene=$(find data/rag-docs/ene -type f | wc -l)
count_por=$(find data/rag-docs/por -type f | wc -l)
count_aer=$(find data/rag-docs/aer -type f | wc -l)
count_bar=$(find data/rag-docs/bar -type f | wc -l)
total=$((count_san + count_ene + count_por + count_aer + count_bar))

echo "Dia 1 Progress:"
echo "  san: $count_san"
echo "  ene: $count_ene"
echo "  por: $count_por"
echo "  aer: $count_aer"
echo "  bar: $count_bar"
echo "  TOTAL: $total / 950 (Target: 100+)"
```

**Expected:** 80-120 documentos após Dia 1

---

### DIAS 2-3 (24-25 Jul) — Agências Regulatórias (4 horas)

Visitar sites das agências e fazer download manual

#### 3.2.1 ANEEL (Energia) — 1 hora
- Website: https://www.aneel.gov.br/
- Buscar: Resoluções normativas, Leilões, RAP (Relatório Anual)
- Download: 80+ documentos
- Salvar em: `data/rag-docs/ene/`

#### 3.2.2 ANTAQ (Portos) — 1 hora
- Website: https://www.gov.br/antaq/
- Buscar: Resoluções, Regulamentações, Guias
- Download: 60+ documentos
- Salvar em: `data/rag-docs/por/`

#### 3.2.3 ANAC (Aeroportos) — 1 hora
- Website: https://www.gov.br/anac/
- Buscar: RBAC (regulamentos), Normas, Circulares
- Download: 50+ documentos
- Salvar em: `data/rag-docs/aer/`

#### 3.2.4 ANA (Barragens & Água) — 1 hora
- Website: https://www.ana.gov.br/
- Buscar: Resoluções, SIGBM (Sistema de Informações de Barragens)
- Download: 60+ documentos
- Salvar em: `data/rag-docs/bar/`

**Expected:** 250+ documentos adicionais (Total: 350-400)

---

### DIAS 4-5 (26-27 Jul) — Fontes Especializadas (4 horas)

#### 3.3.1 EPE (Planejamento Energético)
- Website: https://www.epe.gov.br/
- Buscar: PDE (Plano Decenal), Relatórios R1-R5
- Download: 40+ documentos
- Salvar em: `data/rag-docs/ene/`

#### 3.3.2 ONS (Operação Sistema Elétrico)
- Website: https://www.ons.org.br/
- Buscar: Procedimentos de Rede, Relatórios Anuais
- Download: 40+ documentos
- Salvar em: `data/rag-docs/ene/`

#### 3.3.3 Normas ABNT (Se Acessível)
- Website: https://www.abnt.org.br/
- Relevantes:
  - NBR 12211 — Projeto de adutora
  - NBR 12212 — Projeto de sistema de tratamento
  - NBR 12213 — Coleta de água
  - NBR 7187 — Projeto de obras de arte
- **Nota:** Podem ser pagas. Se não conseguir, documentos técnicos alternativos disponíveis

#### 3.3.4 ICOLD (International Commission on Large Dams)
- Website: https://www.icold-cigb.org/
- Buscar: Design guidelines, Safety documentation
- Download: 20+ documentos (se disponível)
- Salvar em: `data/rag-docs/bar/`

#### 3.3.5 Relatórios Técnicos
- Buscar em Google Scholar, ResearchGate
- Termos: "saneamento brasil", "transmissão energia", "operação porto"
- Download: 100+ artigos acadêmicos
- Salvar por coleção

**Expected:** 200+ documentos adicionais (Total: 550-600)

---

### DIAS 5-7 (27-28 Jul) — Consolidação (3 horas)

#### 3.4.1 Requisições e Follow-ups
```bash
# Se não conseguiu 950 documentos:
# Enviar emails a:
# - BNDES: projetos@bndes.gov.br
# - ANEEL: ouvidoria@aneel.gov.br
# - SNIS: snis@snirh.gov.br
# Assunto: "Requisição de documentos para pesquisa"
```

#### 3.4.2 Verificação Final
```bash
# Contar total
find data/rag-docs -type f | wc -l

# Verificar distribuição
echo "san: $(find data/rag-docs/san -type f | wc -l) / 200"
echo "ene: $(find data/rag-docs/ene -type f | wc -l) / 300"
echo "por: $(find data/rag-docs/por -type f | wc -l) / 150"
echo "aer: $(find data/rag-docs/aer -type f | wc -l) / 120"
echo "bar: $(find data/rag-docs/bar -type f | wc -l) / 180"

# Se < 900: Procurar mais fontes
# Se ≥ 900: Prosseguir para Passo 4
```

---

## 🔄 PASSO 4: Processar RAG (2 horas — Jul 28)

### 4.1 Teste Seco (Dry Run) — 30 min

```bash
# Definir modo teste
export DRY_RUN=true

# Rodar extraction sem inserir em Supabase
bash scripts/extract-and-populate-rag.sh 2>&1 | tee logs/test-run.log

# Verificar output
tail -50 logs/test-run.log

# Se tudo OK, passou no teste!
```

### 4.2 Processamento Real — 1.5 horas

```bash
# Definir credenciais
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export DRY_RUN=false

# Rodar extraction COM inserção em Supabase
bash scripts/extract-and-populate-rag.sh 2>&1 | tee logs/fase2-production.log

# Monitorar progresso em outro terminal
tail -f logs/fase2-production.log
```

### 4.3 Validação — 30 min

```bash
# Contar chunks inseridos
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.count'
# Expected: 947+ chunks

# Ver por coleção
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=collection_prefix&distinct=true" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | .collection_prefix' | sort | uniq -c

# Testar busca simples
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=5" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | {id, collection_prefix, content}' | head -20
```

---

## ✅ CONCLUSÃO FASE 2

Quando chegar aqui, você terá:

```
✅ 950+ documentos coletados (data/rag-docs/)
✅ 947+ chunks extraídos e validados
✅ Dados populados em Supabase (rag_chunks table)
✅ Pronto para Fase 3 (Orchestração)
```

---

## 🚀 PRÓXIMO: Fase 3

Assim que validar 947+ chunks:

```bash
# Deploy SQL indexes
supabase db push < sql/rag-phase3-migrate-indexes.sql

# Escolher tier e rodar orchestrador
# Opção 1: Production (30 agents)
DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-30agents.sh "Como funciona uma ETA?"

# Opção 2: Scale (60 agents)
DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-60agents.sh "Como funciona uma ETA?"

# Opção 3: Enterprise (100 agents)
DRY_RUN=false bash scripts/rag-phase3-query-orchestrator-100agents.sh "Como funciona uma ETA?"
```

---

## 📊 Status de Progresso

| Fase | Status | Deadline |
|------|--------|----------|
| **Fase 2.1** Documentos Públicos | ⏳ | Jul 23 |
| **Fase 2.2** Agências Regulatórias | ⏳ | Jul 24-25 |
| **Fase 2.3** Fontes Especializadas | ⏳ | Jul 26-27 |
| **Fase 2.4** Consolidação | ⏳ | Jul 27 |
| **Fase 2.5** Processamento RAG | ⏳ | Jul 28 |
| **Fase 3** Production Deployment | ⏳ | Jul 29-31 |

---

**Comece agora!** Crie os diretórios e baixe os primeiros documentos:

```bash
mkdir -p data/rag-docs/{san,ene,por,aer,bar}
mkdir -p logs/rag-population
echo "✅ Estrutura criada. Prossiga com PASSO 3."
```

