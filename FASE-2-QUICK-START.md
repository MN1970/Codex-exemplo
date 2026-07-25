# FASE 2 — Quick Start Guide
## Como Executar População RAG em 5 Minutos

**Data:** 2026-07-22  
**Tempo Estimado:** 5-10 minutos (setup) + tempo de processamento (depende do volume)

---

## 📋 Pré-requisitos

```bash
# 1. Python 3.8+
python3 --version  # Mínimo 3.8

# 2. Pip
pip3 --version

# 3. Ferramentas CLI
which jq curl  # Devem estar instaladas

# 4. Credenciais Supabase (se ainda não tiver)
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

---

## 🚀 Setup Inicial (5 minutos)

### Passo 1: Instalar dependências Python

```bash
# Instalar módulos de extração de documentos
pip3 install PyPDF2 python-docx openpyxl

# Verificar instalação
python3 -c "import PyPDF2, docx, openpyxl; print('OK')"
```

### Passo 2: Criar estrutura de diretórios

```bash
# Criar diretórios para cada coleção
mkdir -p data/rag-docs/{san,ene,por,aer,bar}

# Verificar
ls -la data/rag-docs/
```

### Passo 3: Download de documentos de teste

```bash
# Fazer download de alguns documentos públicos para testar

# Exemplo 1: Lei 14.026 (Saneamento) — Documento público
curl -L "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14026.htm" \
  -o data/rag-docs/san:/Lei-14026-2020.html

# Exemplo 2: Usar PDF local (se tiver)
# cp ~/Documents/saneamento.pdf data/rag-docs/san:/

# Listar documentos carregados
ls -lh data/rag-docs/san:/
```

### Passo 4: Tornar scripts executáveis

```bash
chmod +x scripts/rag-extraction-utils.py
chmod +x scripts/extract-and-populate-rag.sh
```

---

## 🧪 Teste Rápido (Dry Run)

### Rodar em modo "dry run" (sem inserir em Supabase)

```bash
# Modo dry-run: processa arquivos mas não insere em Supabase
export DRY_RUN=true
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

./scripts/extract-and-populate-rag.sh

# Output esperado:
# ✓ Python dependencies found
# ℹ Discovering documents...
# ✓ 1 document found in san:
# ✓ Processing: Lei-14026-2020.html
# ...
```

---

## 🎯 Processamento Real

### Rodar em modo "live" (inserir em Supabase)

```bash
# 1. Verificar credenciais
echo "SUPABASE_URL: $SUPABASE_URL"
echo "SUPABASE_KEY: $SUPABASE_KEY"

# 2. Verificar conexão com Supabase
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?limit=1" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | .id'

# Se receber um UUID, conexão está OK!

# 3. Executar população RAG (MODO REAL)
export DRY_RUN=false
./scripts/extract-and-populate-rag.sh 2>&1 | tee logs/fase2-run.log

# Isso vai:
# - Descobrir todos os documentos em data/rag-docs/
# - Extrair conteúdo (PDF/DOCX/XLSX/TXT)
# - Limpar e normalizar
# - Chunkarizar em segmentos de 1000 chars
# - Validar cada chunk com confidence_score
# - Inserir em Supabase rag_chunks
# - Atualizar rag_collection_status
```

---

## 📊 Verificar Resultados

### 1. Contar chunks inseridos

```bash
# Chunks por coleção
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=collection_prefix,count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq -r '.count'

# Exemplo output: 947 (se inseridos 947 chunks)
```

### 2. Verificar status de cada coleção

```bash
# Status consolidado
curl -s "$SUPABASE_URL/rest/v1/rag_collection_status" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.'

# Exemplo output:
# [
#   {
#     "collection_prefix": "san:",
#     "total_chunks": 150,
#     "validated_chunks": 149,
#     "avg_confidence_score": 0.89
#   },
#   ...
# ]
```

### 3. Validar busca semântica

```bash
# Testar query em um chunk (exemplo)
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=1&select=content" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | .content'

# Esperado: Texto de um documento sobre saneamento
```

### 4. Ver logs de execução

```bash
# Último log
tail -50 logs/rag-population/rag-population-*.log

# Ou abrir relatório JSON
jq . logs/rag-population/rag-population-report-*.json
```

---

## 🎓 Exemplo Passo-a-Passo Completo

### Cenário: Processar 1 documento de teste

```bash
# 1. Criar documento de teste
cat > /tmp/test-saneamento.txt << 'EOF'
SANEAMENTO BÁSICO — CONCEITOS FUNDAMENTAIS

A Lei 14.026/2020 estabelece a universalização do saneamento básico.

Tipos de Sistemas:
- ETA (Estação de Tratamento de Água)
- ETE (Estação de Tratamento de Esgoto)
- Adutoras (tubulações de água)
- Redes de distribuição

Normas Aplicáveis:
- NBR 12211: Engenharia de saneamento
- NBR 12216: ETA (Estação de Tratamento de Água)
- SNIS: Sistema Nacional de Informações sobre Saneamento

Tratamento convencional de água:
1. Coagulação/Floculação
2. Decantação
3. Filtração
4. Desinfecção (cloro ou ozônio)

O Brasil tem aproximadamente 40 milhões de pessoas sem acesso a água tratada.
EOF

# 2. Copiar para data/rag-docs/
cp /tmp/test-saneamento.txt data/rag-docs/san:/

# 3. Rodar extração com Python direto
python3 scripts/rag-extraction-utils.py \
  data/rag-docs/san:/test-saneamento.txt \
  san: \
  S8

# Output esperado: JSON com metadata + chunks

# 4. Ou rodar pipeline completo
./scripts/extract-and-populate-rag.sh

# 5. Verificar resultado
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[].content'
```

---

## 🔧 Troubleshooting

### Problema 1: "ModuleNotFoundError: No module named 'PyPDF2'"

```bash
# Solução
pip3 install PyPDF2 python-docx openpyxl

# Verificar
python3 -c "import PyPDF2; print(PyPDF2.__version__)"
```

### Problema 2: "SUPABASE_URL ou SUPABASE_KEY não definidos"

```bash
# Verificar se estão definidas
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Se vazios, definir
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Ou adicionar a ~/.bash_profile ou ~/.bashrc
echo 'export SUPABASE_URL="..."' >> ~/.bash_profile
```

### Problema 3: "Failed to insert chunks into Supabase"

```bash
# Verificar conexão
curl -s "$SUPABASE_URL/rest/v1/" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.error // "OK"'

# Verificar se schema foi criado
supabase db push --project-id <project-id>

# Verificar se tabela rag_chunks existe
curl -s "$SUPABASE_URL/rest/v1/information_schema.tables?table_name=eq.rag_chunks" \
  -H "Authorization: Bearer $SUPABASE_KEY"
```

### Problema 4: "Connection timeout"

```bash
# Verificar proxy/firewall
curl -v https://your-project.supabase.co/rest/v1/

# Se usar proxy, adicionar
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"
```

---

## 📈 Progresso Esperado

### Estimativa de Tempo por Fase

| Fase | Documentos | Tempo | Chunks Esperado |
|------|-----------|--------|---|
| Descoberta | 950 | 1 min | — |
| Extração | 950 | 10-30 min | 950 |
| Limpeza | 950 | 2-5 min | 950 |
| Chunkarização | 950 | 5 min | 950 |
| Validação | 950 | 5 min | 947 |
| Inserção Supabase | 947 | 10-20 min | 947 |
| **TOTAL** | **950** | **35-70 min** | **947** |

### Resumo Esperado ao Final

```json
{
  "timestamp": "2026-07-22T15:30:00Z",
  "total_chunks": 950,
  "validated_chunks": 947,
  "validation_percentage": 99.7,
  "collections": [
    { "collection": "san:", "total": 200, "validated": 199 },
    { "collection": "ene:", "total": 300, "validated": 298 },
    { "collection": "por:", "total": 150, "validated": 149 },
    { "collection": "aer:", "total": 120, "validated": 120 },
    { "collection": "bar:", "total": 180, "validated": 181 }
  ]
}
```

---

## ✅ Checklist Final

- [ ] Python 3.8+ instalado
- [ ] Dependências (PyPDF2, docx, openpyxl) instaladas
- [ ] Diretório `data/rag-docs/` criado com 5 subdiretórios
- [ ] Scripts em `scripts/` são executáveis
- [ ] Variáveis SUPABASE_URL e SUPABASE_KEY definidas
- [ ] Conexão com Supabase validada
- [ ] Schema Supabase foi criado (rag_chunks table existe)
- [ ] Teste de extração passou (dry-run)
- [ ] Documentos coletados em data/rag-docs/
- [ ] Pipeline executado com sucesso
- [ ] 947+ chunks inseridos em Supabase
- [ ] Validação: 99.7%+ chunks com validation_status = "validated"

---

## 🚀 Próximos Passos

Após conclusão da Fase 2:

1. **Validar Resultados:**
   - 950+ chunks em Supabase
   - Avg confidence_score ≥ 0.88 por coleção
   - Busca semântica funcional

2. **Fase 3 — Orchestração Avançada:**
   - Load balancing por segmento
   - Caching distribuído (Redis)
   - Métricas em tempo real

3. **Fase 4 — Sincronização Automática:**
   - Webhooks SharePoint change events
   - Cron jobs periódicos
   - Sincronização bidirecional

4. **Fase 5 — Dashboard:**
   - Visualização em tempo real
   - Alertas automáticos
   - Go-live operacional

---

**Status:** Ready to execute  
**Tempo Estimado:** 1-2 horas para coleta + processamento  
**Próximo Marco:** 950+ chunks em Supabase com 99.7% validação

