# FASE 2 — START HERE
## Guia de Início para Coleta e Processamento RAG

**Status:** ✅ Pronto para começar  
**Data:** 2026-07-22  
**Tempo Estimado:** 1 semana para coleta + 2 horas para processamento

---

## 🚀 Opção 1: Quick Start (5 minutos)

Se você já tem documentos em `data/rag-docs/`:

```bash
# 1. Instalar dependências
pip3 install PyPDF2 python-docx openpyxl

# 2. Teste dry-run (sem inserir em Supabase)
export DRY_RUN=true
./scripts/extract-and-populate-rag.sh

# 3. Se OK, rodar processamento real
export DRY_RUN=false
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
./scripts/extract-and-populate-rag.sh
```

---

## 📥 Opção 2: Começar Coleta Agora (1 semana)

Se você precisa coletar os 950 documentos:

### PASSO 1: Entender o que precisa coletar (15 min)

```bash
# Abrir documento de coleta
cat FASE-2-COLLECTION-MANIFEST.md | head -100

# Ou abrir em editor
vim FASE-2-COLLECTION-MANIFEST.md
```

**Resumo Rápido:**
- **san:** 200 docs sobre Saneamento (AYSÁ prioridade)
- **ene:** 300 docs sobre Energia (ANEEL prioridade)
- **por:** 150 docs sobre Portos
- **aer:** 120 docs sobre Aeroportos
- **bar:** 180 docs sobre Barragens

### PASSO 2: Acompanhar progresso (Diário)

```bash
# Abrir tracker
vim FASE-2-COLLECTION-TRACKER.md

# Marcar documentos coletados
# Atualizar % de progresso
# Registrar contatos/requisições enviadas
```

### PASSO 3: Coletar documentos

#### 3A: Documentos Públicos (Fácil — 30 min)

```bash
# Executar coleta automática de fontes públicas
./scripts/collect-public-documents.sh

# Vai tentar baixar:
# - Lei 14.026/2020 (Saneamento)
# - Lei 9.074/1995 (Energia)
# - Lei 12.815/2013 (Portos)
# - Lei 13.182/2015 (Aeroportos)
# - Lei 12.334/2010 (Barragens)
# (E mais 320+ documentos de órgãos públicos)
```

#### 3B: Documentos de Agências (Médio — 2-3 dias)

Visitar sites e fazer download manual:

```bash
# ANEEL (Energia)
# URL: https://www.aneel.gov.br/
# Download: Resoluções, Leilões, RAP
# Salvar em: data/rag-docs/ene:/

# ANTAQ (Portos)
# URL: https://www.gov.br/antaq/
# Download: Regulamentações
# Salvar em: data/rag-docs/por:/

# ANAC (Aeroportos)
# URL: https://www.gov.br/anac/
# Download: RBAC, Normas
# Salvar em: data/rag-docs/aer:/

# ANA (Barragens)
# URL: https://www.ana.gov.br/
# Download: Resoluções, SIGBM
# Salvar em: data/rag-docs/bar:/
```

#### 3C: Documentos Restritos (Difícil — 3-5 dias)

Enviar requisições:

```bash
# ABNT (Normas)
# Email: abnt@abnt.org.br
# Assunto: "Requisição de acesso: NBR 12211-12218"
# Corpo: "Projeto de pesquisa em Saneamento, necessário acesso a normas"

# BNDES
# URL: https://www.bndes.gov.br/
# Menu: Financiamento → Saneamento
# Download: Manuais, Diretrizes
# Salvar em: data/rag-docs/san:/

# SNIS (Água e Esgoto)
# URL: https://www.gov.br/snirh/pt-br
# Dados: Série histórica, diagnósticos
# Salvar em: data/rag-docs/san:/

# EPE (Planejamento Energético)
# URL: https://www.epe.gov.br/
# Download: PDE, Relatórios R1-R5
# Salvar em: data/rag-docs/ene:/

# ONS (Operação Sistema)
# URL: https://www.ons.org.br/
# Download: Procedimentos, Relatórios
# Salvar em: data/rag-docs/ene:/
```

### PASSO 4: Validar coleta

```bash
# Contar documentos por coleção
for col in san ene por aer bar; do
  count=$(find data/rag-docs/${col} -type f | wc -l)
  echo "${col}: $count documentos"
done

# Esperado total: 950 documentos
# Se <900: Coletar mais fontes
# Se ≥950: Pronto para processar
```

### PASSO 5: Processar RAG

```bash
# 1. Instalar dependências
pip3 install PyPDF2 python-docx openpyxl

# 2. Teste (dry-run)
export DRY_RUN=true
./scripts/extract-and-populate-rag.sh 2>&1 | tee logs/test-run.log

# 3. Se passou, rodar real
export DRY_RUN=false
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

./scripts/extract-and-populate-rag.sh 2>&1 | tee logs/fase2-run.log

# Vai levar 1-2 horas para 950 documentos
# Monitor: tail -f logs/rag-population/*.log
```

### PASSO 6: Validar resultado

```bash
# Contar chunks inseridos
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?select=count=exact" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.count'

# Esperado: 947+ chunks (99.7% validados)

# Ver status por coleção
curl -s "$SUPABASE_URL/rest/v1/rag_collection_status" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.'

# Testar busca
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?collection_prefix=eq.san:&limit=1" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq '.[] | .content' | head -5
```

---

## 📂 Estrutura de Diretórios

```
Codex-exemplo/
├── data/rag-docs/              ← Documentos originais (colecionar aqui)
│   ├── san/                    ← 200 docs Saneamento
│   ├── ene/                    ← 300 docs Energia
│   ├── por/                    ← 150 docs Portos
│   ├── aer/                    ← 120 docs Aeroportos
│   └── bar/                    ← 180 docs Barragens
│
├── scripts/
│   ├── rag-extraction-utils.py          ← Extração/validação
│   ├── extract-and-populate-rag.sh      ← Orquestrador
│   └── collect-public-documents.sh      ← Coleta automática
│
├── logs/
│   └── rag-population/                  ← Logs de execução
│
├── FASE-2-COLLECTION-MANIFEST.md        ← O quê coletar
├── FASE-2-COLLECTION-TRACKER.md         ← Progresso de coleta
└── FASE-2-QUICK-START.md                ← Guia executável
```

---

## ⏱️ Timeline Estimada

| Dia | Atividade | Tempo | Status |
|-----|-----------|-------|--------|
| **Seg 22** | Setup + Entender manifest | 1h | ⏳ |
| **Ter 23** | Coleta documentos públicos | 2h | ⏳ |
| **Qua 24** | Download ANEEL, ANTAQ, ANAC | 2h | ⏳ |
| **Qui 25** | Download EPE, ONS, ANA | 2h | ⏳ |
| **Sex 26** | Requisições ABNT, BNDES, etc | 1h | ⏳ |
| **Sab 27** | Validação e organização | 2h | ⏳ |
| **Dom 28** | Processamento RAG (1-2h) | 2h | ⏳ |
| **TOTAL** | | **12-15h** | |

---

## 🔧 Troubleshooting Rápido

### Problema: "ModuleNotFoundError: PyPDF2"

```bash
pip3 install PyPDF2 python-docx openpyxl
```

### Problema: Downloads não funcionam

```bash
# Tentar com wget
wget https://url-do-documento.pdf -O data/rag-docs/san:/documento.pdf

# Ou fazer download manual via navegador
# 1. Abrir URL no browser
# 2. Salvar como PDF
# 3. Mover para data/rag-docs/{col}/
```

### Problema: "SUPABASE_URL não definido"

```bash
# Definir em terminal
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Ou adicionar a ~/.bashrc
echo 'export SUPABASE_URL="..."' >> ~/.bashrc
source ~/.bashrc
```

### Problema: Inserção lenta em Supabase

```bash
# Normal: ~500-1000 chunks/hora
# Se mais lento, verificar:
# 1. Conexão de internet
# 2. Limite de rate da API (throttling)
# 3. Tamanho dos chunks (reduzir se muito grandes)

# Rodar apenas 1 coleção por vez (debug)
# (Editar extract-and-populate-rag.sh, comentar coleções)
```

---

## ✅ Checklist Final

### Antes de Coletar
- [ ] Ler FASE-2-COLLECTION-MANIFEST.md
- [ ] Abrir FASE-2-COLLECTION-TRACKER.md
- [ ] Criar data/rag-docs/ com 5 subdiretórios
- [ ] Entender fontes públicas vs restritas

### Durante Coleta
- [ ] Documentos públicos (320+) — script automático
- [ ] Documentos agências (400+) — download manual
- [ ] Documentos restritos (150+) — requisições
- [ ] Atualizar tracker com progresso

### Antes de Processar
- [ ] 950+ documentos em data/rag-docs/
- [ ] Verificar: `find data/rag-docs -type f | wc -l`
- [ ] Dependências Python instaladas
- [ ] SUPABASE_URL e SUPABASE_KEY definidas

### Processamento
- [ ] Executar dry-run: `DRY_RUN=true ./scripts/extract-and-populate-rag.sh`
- [ ] Se passou, executar real
- [ ] Monitorar logs: `tail -f logs/rag-population/*.log`
- [ ] Validar resultado: 947+ chunks em Supabase

### Próximo: Fase 3
- [ ] 950+ chunks em Supabase ✅
- [ ] Movimentar para Fase 3 (Orchestração Avançada)

---

## 📚 Documentos de Referência

| Documento | Propósito | Quando Ler |
|-----------|----------|-----------|
| FASE-2-COLLECTION-MANIFEST.md | Especificação de fontes | Antes de coletar |
| FASE-2-COLLECTION-TRACKER.md | Rastrear progresso | Durante coleta |
| FASE-2-QUICK-START.md | Passo-a-passo detalhado | Antes de processar |
| scripts/rag-extraction-utils.py | Código de extração | Para debug |
| scripts/extract-and-populate-rag.sh | Orquestrador | Para entender fluxo |

---

## 🎯 Objetivo Final

```
950 Documentos Coletados
        ↓
       [Extraction]
        ↓
    950 Documentos processados
        ↓
      [Validation]
        ↓
     ~1,000 chunks
        ↓
    [Supabase Insert]
        ↓
    947+ chunks ✅
    (99.7% validated)
        ↓
   Fase 3 Ready! 🚀
```

---

**Próximo Passo:** Abrir FASE-2-COLLECTION-MANIFEST.md e começar coleta!

```bash
cat FASE-2-COLLECTION-MANIFEST.md | less
```

ou

```bash
vim FASE-2-COLLECTION-MANIFEST.md
```

---

**Data:** 2026-07-22  
**Status:** Ready to execute  
**Timeline:** 1 semana (coleta) + 2h (processamento)

