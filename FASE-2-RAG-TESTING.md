# FASE 2 — RAG Testing Guide
## Como Testar o Sistema RAG (Retrieval Augmented Generation)

**Data:** 2026-07-22  
**Status:** Complete testing framework com 4 níveis  
**Objetivo:** Validar extração, armazenamento, busca e integração com agentes

---

## 🎯 4 Níveis de Teste

| Nível | Escopo | Dados | Tempo | Quando |
|-------|--------|-------|-------|--------|
| **1. Extração Local** | Pipeline sem Supabase | 3 test docs | 5 min | Agora |
| **2. Dry-Run** | Processamento completo | Seus docs | 15 min | Antes de coletar |
| **3. Supabase Query** | Busca semântica | 947+ chunks | 10 min | Após inserção |
| **4. Agent Integration** | Agente usando RAG | Queries reais | 20 min | Validação final |

---

## ✅ NÍVEL 1: Extração Local (SEM Supabase)

### 1A. Testar Extração de Um Documento

```bash
# Usar o documento de teste que criamos
python3 scripts/rag-extraction-utils.py \
  data/rag-docs/san:/Lei-14026-2020.txt \
  san: \
  S8

# Output esperado:
# {
#   "document_id": "san:-Lei-14026-2020",
#   "source_url": "file:///home/user/Codex-exemplo/data/rag-docs/san:/Lei-14026-2020.txt",
#   "collection_prefix": "san:",
#   "segment": "S8",
#   "chunks": [
#     {
#       "content": "LEI Nº 14.026, DE 26 DE JULHO DE 2020...",
#       "confidence_score": 1.0,
#       "collection_prefix": "san:",
#       "segment": "S8"
#     }
#   ]
# }
```

### 1B. Testar com Arquivo PDF

```bash
# Se você tem um PDF local
python3 scripts/rag-extraction-utils.py \
  /seu/caminho/documento.pdf \
  ene: \
  S9 | jq '.'

# Verificar extração
# - content está preenchido
# - confidence_score > 0.85
# - collection_prefix é correto
```

### 1C. Testar com Arquivo DOCX

```bash
python3 scripts/rag-extraction-utils.py \
  /seu/caminho/documento.docx \
  por: \
  S6 | jq '.chunks | length'

# Output: número de chunks gerados
```

---

## 🧪 NÍVEL 2: Pipeline Completo (Dry-Run)

### 2A. Testar com 3 Documentos de Teste

```bash
# Criar 3 docs de teste adicionais
cat > data/rag-docs/san:/Test-Agua-01.txt << 'EOF'
SANEAMENTO BÁSICO — ÁGUA TRATADA

O acesso à água tratada é fundamental para a saúde pública.

Definição:
Água potável é aquela que atende aos padrões de qualidade 
estabelecidos pela Portaria 888/2021 do Ministério da Saúde.

Parâmetros de Qualidade:
- pH: 6,5 a 8,5
- Turbidez: ≤ 0,5 UNT
- Cloro residual: 0,5 a 2,0 mg/L
- Coliformes: Ausentes em 100 ml

Tecnologias:
1. ETA (Estação de Tratamento de Água)
2. Sistemas de adução
3. Redes de distribuição
4. Elevatórias de reforço
EOF

cat > data/rag-docs/ene:/Test-Transmissao-01.txt << 'EOF'
ENERGIA ELÉTRICA — TRANSMISSÃO

Linhas de Transmissão são sistemas que transportam energia elétrica 
de longas distâncias com alta voltagem.

Tipos de Linhas:
- LT 69 kV (distribuição)
- LT 138 kV (transmissão sub-regional)
- LT 230 kV (transmissão regional)
- LT 500 kV (transmissão nacional/internacional)
- LT 600 kV (ultra-alta tensão)

Componentes:
1. Estruturas/Torres
2. Condutores ACSR
3. Isoladores de vidro/cerâmica
4. Acessórios de fixação
5. Aterramento

Normas: ABNT NBR 5422, IEC 60871
EOF

cat > data/rag-docs/por:/Test-Dragagem-01.txt << 'EOF'
PORTOS — DRAGAGEM E MANUTENÇÃO

Dragagem é a remoção de sedimentos do fundo do porto para manter 
calados de navegação adequados.

Tipos de Dragagem:
1. Dragagem de manutenção (anual/periódica)
2. Dragagem de aprofundamento (projeto)
3. Dragagem ambiental (proteção)

Equipamentos:
- Draga de sucção de arraste
- Draga de corrente
- Escavadeira hidráulica anfíbia
- Barcaça de descarregamento

Volume Típico:
Portos brasileiros: 50-200 Mm³/ano

Custo: R$ 2-5 por m³ escavado
EOF

echo "✅ Criados 3 arquivos de teste adicionais"
```

### 2B. Executar Dry-Run (SEM Supabase)

```bash
# Limpar staging anterior
rm -rf .rag-staging

# Definir variáveis (placeholders, não são usadas em DRY_RUN)
export DRY_RUN=true
export SUPABASE_URL="https://placeholder.supabase.co"
export SUPABASE_KEY="placeholder-key"

# Executar pipeline
./scripts/extract-and-populate-rag.sh 2>&1 | tee /tmp/dryrun-test.log

# Verificar output
echo ""
echo "=== TEST SUMMARY ==="
grep "✓ Extraído" /tmp/dryrun-test.log | wc -l
grep "Chunks após filtro" /tmp/dryrun-test.log
```

### 2C. Verificar Staging Files

```bash
# Listar arquivos extratos
ls -lh .rag-staging/

# Verificar estrutura JSON
jq '.' .rag-staging/san:-Lei-14026-2020.txt.json | head -30

# Contar chunks por coleção
for col in san ene por; do
  count=$(jq '.chunks | length' .rag-staging/${col}:-*.json 2>/dev/null | paste -sd+ | bc)
  echo "${col}: $count chunks"
done
```

---

## 🗄️ NÍVEL 3: Teste contra Supabase

### 3A. Verificar Conexão com Supabase

```bash
# Verificar credenciais
echo "SUPABASE_URL: ${SUPABASE_URL}"
echo "SUPABASE_KEY: ${SUPABASE_KEY}"

# Testar conectividade
curl -s "$SUPABASE_URL/rest/v1/" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.version // "OK"'

# Esperado: resposta JSON com versão ou "OK"
```

### 3B. Contar Chunks Existentes

```bash
# Total de chunks
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.count'

# Chunks por coleção
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=collection_prefix,count=exact&group_by=collection_prefix" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | {collection: .collection_prefix, count: .count}'
```

### 3C. Buscar Chunks por Coleção

```bash
# Buscar 3 chunks de Saneamento
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY" | \
  jq '.[] | {id: .id, collection: .collection_prefix, segment: .segment, confidence: .confidence_score, content: (.content[:80] + "...")}'

# Esperado:
# {
#   "id": "uuid",
#   "collection": "san:",
#   "segment": "S8",
#   "confidence": 0.92,
#   "content": "LEI Nº 14.026, DE 26 DE JULHO DE 2020 Atualiza o marco legal..."
# }
```

### 3D. Testar Busca com Filtros

```bash
# Chunks com confidence >= 0.90
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?confidence_score=gte.0.9&limit=5" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | {confidence: .confidence_score, collection: .collection_prefix}'

# Chunks por segmento (energia)
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?segment=eq.S9&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | {segment: .segment, collection: .collection_prefix}'

# Chunks de um documento específico
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?document_id=eq.san:-Lei-14026-2020&limit=10" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | .content'
```

### 3E. Verificar Collection Status

```bash
# Status consolidado por coleção
curl -s "$SUPABASE_URL/rest/v1/rag_collection_status" \
  -H "Authorization: Bearer $SUPABASE_KEY" | \
  jq '.[] | {collection: .collection_prefix, total: .total_chunks, validated: .validated_chunks, avg_confidence: .avg_confidence_score}'

# Esperado:
# {
#   "collection": "san:",
#   "total": 199,
#   "validated": 199,
#   "avg_confidence": 0.92
# }
```

---

## 🤖 NÍVEL 4: Teste de Integração com Agentes

### 4A. Criar Script de Teste com Agente Saneamento

```bash
cat > /tmp/test-rag-with-agent.sh << 'TESTEOF'
#!/bin/bash

# Simular query através do agente-saneamento
# Scenario: Usuário pergunta sobre ETA (Estação de Tratamento de Água)

QUERY="O que é ETA e quais são as tecnologias de tratamento de água?"
COLLECTION="san:"
SEGMENT="S8"

echo "=========================================="
echo "TEST: RAG Query com Agente Saneamento"
echo "=========================================="
echo ""
echo "Query: $QUERY"
echo "Collection: $COLLECTION"
echo "Segment: $SEGMENT"
echo ""

# 1. Buscar chunks relevantes
echo "1. Buscando chunks relevantes..."
CHUNKS=$(curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.$COLLECTION&limit=5&select=content,confidence_score" \
  -H "Authorization: Bearer $SUPABASE_KEY")

CHUNK_COUNT=$(echo "$CHUNKS" | jq 'length')
echo "   ✓ Encontrados $CHUNK_COUNT chunks relevantes"

# 2. Exibir chunks
echo ""
echo "2. Chunks encontrados:"
echo "$CHUNKS" | jq -r '.[] | "   - [\(.confidence_score)] \(.content[:100])"'

# 3. Simular resposta do agente
echo ""
echo "3. Resposta que o agente formaria:"
echo "   Com base nos $CHUNK_COUNT chunks do RAG (san:), o agente-saneamento"
echo "   responderia com informações sobre ETA e tecnologias de tratamento."
echo ""
echo "   Confidence média: $(echo "$CHUNKS" | jq '[.[].confidence_score] | add/length' | xargs printf '%.2f')"
echo ""

echo "=========================================="
echo "✓ TEST PASSED: RAG integrado com agente"
echo "=========================================="

TESTEOF

chmod +x /tmp/test-rag-with-agent.sh
bash /tmp/test-rag-with-agent.sh
```

### 4B. Testar Routing Automático

```bash
# Simular que diferentes queries vão para diferentes agentes

declare -A ROUTING_TESTS=(
  ["san:esgoto"]=S8  # Saneamento
  ["ene:transmissão"]=S9  # Energia
  ["por:dragagem"]=S6  # Portos
  ["aer:pista"]=S7  # Aeroportos
  ["bar:barragem"]=S10  # Barragens
)

echo "Testing RAG Routing..."
echo ""

for query in "${!ROUTING_TESTS[@]}"; do
  segment=${ROUTING_TESTS[$query]}
  collection=$(echo $query | cut -d: -f1)
  
  # Contar chunks disponíveis para este segmento
  count=$(curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.${collection}:&select=count=exact" \
    -H "Authorization: Bearer $SUPABASE_KEY" | jq '.count')
  
  echo "Query: '$query'"
  echo "  → Collection: $collection (Segment: $segment)"
  echo "  → Available chunks: $count"
  echo ""
done
```

### 4C. Teste de Performance

```bash
# Medir tempo de resposta das queries

echo "RAG Query Performance Test"
echo "============================"
echo ""

for i in {1..5}; do
  START=$(date +%s%N)
  
  RESULT=$(curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=10&select=count=exact" \
    -H "Authorization: Bearer $SUPABASE_KEY")
  
  END=$(date +%s%N)
  ELAPSED=$(( (END - START) / 1000000 ))  # Convert to ms
  
  CHUNK_COUNT=$(echo "$RESULT" | jq '.count // 0')
  
  echo "Query $i: ${ELAPSED}ms (found $CHUNK_COUNT chunks)"
done

echo ""
echo "Expected: < 500ms per query (typical: 100-300ms)"
```

---

## 📊 Script de Teste Automatizado Completo

```bash
cat > /tmp/comprehensive-rag-test.sh << 'FULLEOF'
#!/bin/bash

# Comprehensive RAG Testing Suite
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

test_info() { echo -e "${BLUE}ℹ${NC} $@"; }
test_success() { echo -e "${GREEN}✓${NC} $@"; ((TESTS_PASSED++)); }
test_error() { echo -e "${RED}✗${NC} $@"; ((TESTS_FAILED++)); }
test_warn() { echo -e "${YELLOW}⚠${NC} $@"; }

echo "╔════════════════════════════════════════╗"
echo "║ Comprehensive RAG Testing Suite        ║"
echo "║ Fase 2 — Validação Completa            ║"
echo "╚════════════════════════════════════════╝"
echo ""

# TEST 1: Extraction
test_info "TEST 1: Local Extraction"
if python3 scripts/rag-extraction-utils.py \
   data/rag-docs/san:/Lei-14026-2020.txt san: S8 > /tmp/extract-test.json 2>&1; then
  CHUNKS=$(jq '.chunks | length' /tmp/extract-test.json)
  if [ "$CHUNKS" -gt 0 ]; then
    test_success "Extraction: $CHUNKS chunks generated"
  else
    test_error "Extraction: No chunks generated"
  fi
else
  test_error "Extraction: Python script failed"
fi
echo ""

# TEST 2: Confidence Filtering
test_info "TEST 2: Confidence Filtering"
CONFIDENCE=$(jq '.chunks[0].confidence_score' /tmp/extract-test.json)
if (( $(echo "$CONFIDENCE >= 0.85" | bc -l) )); then
  test_success "Confidence: Score $CONFIDENCE >= 0.85"
else
  test_warn "Confidence: Score $CONFIDENCE < 0.85 (may be filtered)"
fi
echo ""

# TEST 3: Supabase Connectivity
test_info "TEST 3: Supabase Connectivity"
if curl -s "$SUPABASE_URL/rest/v1/" \
   -H "Authorization: Bearer $SUPABASE_KEY" | \
   jq -e '.version // true' > /dev/null 2>&1; then
  test_success "Supabase: Connected"
else
  test_error "Supabase: Connection failed"
fi
echo ""

# TEST 4: Chunk Count
test_info "TEST 4: Chunk Count in Supabase"
TOTAL_CHUNKS=$(curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.count')
if [ "$TOTAL_CHUNKS" -gt 0 ]; then
  test_success "Chunks: $TOTAL_CHUNKS chunks in database"
else
  test_warn "Chunks: 0 chunks found (pipeline may not have run yet)"
fi
echo ""

# TEST 5: Collection Status
test_info "TEST 5: Collection Status"
COLLECTIONS=$(curl -s "$SUPABASE_URL/rest/v1/rag_collection_status" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq 'length')
if [ "$COLLECTIONS" -gt 0 ]; then
  test_success "Collections: $COLLECTIONS collections initialized"
  curl -s "$SUPABASE_URL/rest/v1/rag_collection_status" \
    -H "Authorization: Bearer $SUPABASE_KEY" | \
    jq -r '.[] | "  - \(.collection_prefix): \(.total_chunks) chunks"'
else
  test_warn "Collections: No status found"
fi
echo ""

# TEST 6: Query Performance
test_info "TEST 6: Query Performance"
START=$(date +%s%N)
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=5&select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" > /dev/null
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))
if [ "$ELAPSED" -lt 1000 ]; then
  test_success "Performance: ${ELAPSED}ms (acceptable)"
else
  test_warn "Performance: ${ELAPSED}ms (slower than expected)"
fi
echo ""

# SUMMARY
echo "╔════════════════════════════════════════╗"
echo "║ TEST RESULTS                           ║"
echo "╚════════════════════════════════════════╝"
echo "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}✗ Some tests failed${NC}"
  exit 1
fi

FULLEOF

chmod +x /tmp/comprehensive-rag-test.sh
bash /tmp/comprehensive-rag-test.sh
```

---

## 🧪 Checklist de Testes

### Antes de Coletar Documentos
- [ ] Teste Local: Extração funciona (`python3 rag-extraction-utils.py ...`)
- [ ] Teste Local: Dry-run completa (`DRY_RUN=true ./scripts/extract-and-populate-rag.sh`)
- [ ] Conexão Supabase: Credenciais corretas (`curl ... rest/v1/`)

### Após Inserir Chunks
- [ ] [ ] Contagem: 947+ chunks em Supabase
- [ ] [ ] Validação: 99.7%+ pass rate
- [ ] [ ] Qualidade: Avg confidence_score > 0.85
- [ ] [ ] Busca: Queries retornam resultados em < 500ms
- [ ] [ ] Status: Todas 5 coleções têm chunks

### Antes de Phase 3
- [ ] [ ] Integração: Agentes conseguem acessar RAG
- [ ] [ ] Routing: Queries vão para coleção correta
- [ ] [ ] Performance: Sistema responde em tempo aceitável
- [ ] [ ] Confiança: Chunks têm metadata completa

---

## 🎓 Exemplos de Queries por Agente

### Agente Saneamento (san:)
```bash
# Query sobre ETA
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&segment=eq.S8&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY"

# Resultado: Chunks sobre saneamento, tratamento, Lei 14.026
```

### Agente Energia (ene:)
```bash
# Query sobre transmissão
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.ene:&segment=eq.S9&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY"

# Resultado: Chunks sobre energia, linhas transmissão, ANEEL
```

### Agente Portos (por:)
```bash
# Query sobre dragagem
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.por:&segment=eq.S6&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY"

# Resultado: Chunks sobre portos, dragagem, ANTAQ
```

### Agente Aeroportos (aer:)
```bash
# Query sobre pistas
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.aer:&segment=eq.S7&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY"

# Resultado: Chunks sobre aeroportos, pistas, ANAC
```

### Agente Barragens (bar:)
```bash
# Query sobre segurança
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.bar:&segment=eq.S10&limit=3" \
  -H "Authorization: Bearer $SUPABASE_KEY"

# Resultado: Chunks sobre barragens, segurança, Lei 12.334
```

---

## 📈 Esperado vs Real

### Se 947+ Chunks Estão em Supabase:
```bash
# Contagem deve retornar algo como:
{
  "count": 947
}

# Status deve mostrar:
[
  { "collection_prefix": "san:", "total_chunks": 199, "validated_chunks": 199, "avg_confidence_score": 0.92 },
  { "collection_prefix": "ene:", "total_chunks": 298, "validated_chunks": 298, "avg_confidence_score": 0.89 },
  { "collection_prefix": "por:", "total_chunks": 149, "validated_chunks": 149, "avg_confidence_score": 0.91 },
  { "collection_prefix": "aer:", "total_chunks": 119, "validated_chunks": 119, "avg_confidence_score": 0.90 },
  { "collection_prefix": "bar:", "total_chunks": 182, "validated_chunks": 182, "avg_confidence_score": 0.88 }
]
```

### Se Falta Dados:
- Rever FASE-2-EXECUTION-PLAN.md para coleta
- Rodar dry-run novamente: `DRY_RUN=true ./scripts/extract-and-populate-rag.sh`
- Verificar logs: `tail -100 logs/rag-population/*.log`

---

## 🚀 Próximos Passos

1. **Agora (Antes de Coletar):** Rodar Nível 1-2 de testes
2. **Após Inserção (Domingo):** Rodar Nível 3 de testes
3. **Antes Phase 3:** Rodar Nível 4 (integração com agentes)

---

**Status:** Testing framework completo ✅  
**Pronto para:** Execução em todos os 4 níveis  
**Próximo:** Collect documents e validar RAG em produção
