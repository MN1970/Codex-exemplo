# FASE 1 — STATUS EM TEMPO REAL

**Iniciado em**: 2026-08-02  
**Status**: 🟢 EM EXECUÇÃO  
**Timeline**: Semanas 1-3 (8 jul - 26 jul)  

---

## 📊 PROGRESSO

### SEMANA 1: RAG LOADING (5 agentes em paralelo) — ⏳ BLOQUEADO

| # | Agente | Coleção | Status | Chunks | Blocker |
|---|--------|---------|--------|--------|---------|
| 1 | RAG Saneamento | saneamento | 🔴 BLOQUEADO | 0/750 | Infraestrutura (veja abaixo) |
| 2 | RAG Energia | energia | 🔴 BLOQUEADO | 0/750 | Infraestrutura (veja abaixo) |
| 3 | RAG Portos | portos | 🔴 BLOQUEADO | 0/750 | Infraestrutura (veja abaixo) |
| 4 | RAG Aeroportos | aeroportos | 🔴 BLOQUEADO | 0/750 | Infraestrutura (veja abaixo) |
| 5 | RAG Barragens | barragens | 🔴 BLOQUEADO | 0/750 | Infraestrutura (veja abaixo) |

**META**: 5 coleções × ~750 chunks cada = ~3750 total  
**STATUS**: Agentes executados, diagnosticaram blockers reais, recusaram fabricar dados  
**AÇÕES NECESSÁRIAS**:
- [ ] **Blocker 1**: Schema Supabase — public.rag_chunks sem coluna `embedding`. Decisão: usar `manta_rag_chunks` (tem embedding) ou migrar DDL?
- [ ] **Blocker 2**: Embeddings — sem ferramenta de geração. Decisão: integrar Claude Embeddings API ou criar Edge Function?
- [ ] **Blocker 3**: Network — HTTP 403 em gov.br. Solução: upload manual de PDFs ou acesso autenticado
- [ ] **Blocker 4**: Approval — CLAUDE.md exige "Gate humano: aprovação MN". Status: PENDENTE
- [ ] Obter aprovação MN (mneves@mantaassociados.com) + arquitetura definida
- [ ] Semana 1 inicia APÓS infraestrutura estar pronta

---

### SEMANA 2: SHAREPOINT SETUP (5 agentes em paralelo) — 🟡 EM EXECUÇÃO

| # | Agente | Alvo | Status | Pastas | Documentos |
|---|--------|------|--------|--------|------------|
| 6 | SP Portos | S6 | 🟡 EM PROGRESSO | 2 | SKILL.md preparado |
| 7 | SP Aeroportos | S7 | 🟡 EM PROGRESSO | 2 | SKILL.md preparado |
| 8 | SP Saneamento | S8 | 🟡 EM PROGRESSO | 2 | SKILL.md preparado |
| 9 | SP Energia | S9 | 🟡 EM PROGRESSO | 2 | SKILL.md preparado |
| 10 | SP Barragens | S10 | 🟡 EM PROGRESSO | 2 | SKILL.md preparado |

**META**: 10 pastas criadas + 5 SKILL.md content generated + MCP config  
**STATUS**: Agentes S6-S10 gerando conteúdo SKILL.md em paralelo  
**DURAÇÃO**: ~1-2 dias (content generation) + upload quando ready  
**NÃO DEPENDE DE**: Semana 1 concluída (execução paralela)

---

### SEMANA 3: VALIDAÇÃO (1 agente serial)

| # | Agente | Tarefa | Status | Resultado |
|---|--------|--------|--------|-----------|
| 11 | QA Validation | Testes + Gate | 🔴 AGUARDANDO | — |

**META**: ≥90% routing tests + gate Fase 2  
**DURAÇÃO**: 3-4 dias  
**INICIA**: Após Semana 2 concluída

---

## 🎯 MÉTRICAS ESPERADAS

### RAG Collections
- **Total chunks**: ~3750-5000
- **Chunks por coleção**: 500-1000
- **Avg similarity**: >0.7
- **Meta**: 100% de sucesso

### SharePoint
- **Pastas criadas**: 10/10
- **SKILL.md carregados**: 5/5
- **Documentos de referência**: 25+

### Routing Tests
- **Prompts**: 30
- **Taxa de sucesso**: ≥90%
- **Confiança média**: ≥75%
- **Ambigüidades resolvidas**: 100%

---

## 📝 NOTAS TÉCNICAS

### Semana 1 - RAG Loading
```
Cada agente:
1. Fetch documentos das fontes
2. Chunk: 200-300 tokens, overlap 50
3. Embed: vetorial
4. Upload: Supabase rag_chunks
5. Validate: ≥500 chunks, similarity >0.7

Sucesso = status 'success' em todos 5
```

### Semana 2 - SharePoint Setup
```
Cada agente:
1. Criar 2 pastas (agente + projetos)
2. Upload SKILL.md (~5 KB)
3. Upload README.md (~2 KB)
4. Upload 3+ documentos refs/
5. Criar prompts/ com exemplos

Sucesso = 10 pastas + 5+ SKILL.md
```

### Semana 3 - Validação
```
Agente QA:
1. Validar 5 coleções RAG (count chunks)
2. Validar 10 pastas SharePoint
3. Validar MCP config (.mcp.json)
4. Executar 30 routing tests
5. Documentar ambigüidades
6. Gate: Fase 2 aprovada?

Sucesso = overall_status 'success' + gate_phase2 true
```

---

## 🚨 BLOCKERS (4 IDENTIFICADOS — SEMANA 1 RAG LOADING)

### BLOCKER 1: Schema Supabase — Coluna `embedding` faltando
```
Status:  ❌ CRÍTICO
Achado:  public.rag_chunks NÃO tem coluna 'embedding' ou 'collection_slug'
Real:    Schema atual = id, collection, prefix, title, content, source, segment, created_at
Alt:     Existe public.manta_rag_chunks com colunas embedding/embedding_m3 (384d, bge-small-en-v1.5)
Decisão: Qual é a tabela CANONICAL para RAG? rag_chunks ou manta_rag_chunks?
Ação:    Definir e comunicar. Se rag_chunks, executar ALTER TABLE ADD COLUMN embedding vector(384).
Owner:   DevOps/Manta 16
ETA:     1-2 dias após decisão
```

### BLOCKER 2: Ferramenta de Embeddings — Não disponível
```
Status:  ❌ CRÍTICO
Achado:  Nenhuma função de geração de embeddings está disponível nesta sessão
         Supabase pgvector (0.8.0) está instalado mas sem Edge Function
         Nenhuma ferramenta Claude Embeddings API acessível
Decisão: (a) Integrar Claude Embeddings API via MCP? (b) Criar Edge Function Supabase? (c) Outro?
Ação:    Escolher abordagem + implementar
Owner:   Manta 16 (arquitetor-ia)
ETA:     3-5 dias após decisão + implementação
```

### BLOCKER 3: Network — HTTP 403 em gov.br
```
Status:  ⚠️  MEDIUM
Achado:  Tentativas de fetch em planalto.gov.br, camara.leg.br retornam HTTP 403
         Bloqueia acesso a: Lei 12.334/2010, Lei 14.026/2020, RBAC 154, etc
Solução: (a) Upload manual de PDFs (ex: via SharePoint) (b) Acesso autenticado ao gov.br (c) Usar mirrors internos Manta
Ação:    Fornecer PDFs manualmente ou resolver acesso autenticado
Owner:   Manta 06 (modelagem/dados) ou DevOps
ETA:     1-2 dias
```

### BLOCKER 4: Aprovação MN — Não obtida
```
Status:  🔐 REQUERIDO
Achado:  CLAUDE.md v4.2 deploy checklist exige "Gate humano: aprovação MN antes de merge"
         Necessário para: carga de dados em DB de produção (manta-maestro)
Ação:    Comunicar blockers 1-3 a MN + aguardar aprovação para proceder com Semana 1
Owner:   MN (mneves@mantaassociados.com)
ETA:     Comunicação hoje; aprovação dentro de 24-48h
```

### Resumo de bloqueadores
- ❌ CRÍTICO (Semana 1 não pode iniciar):
  1. Schema Supabase definir
  2. Embeddings service implementar
- ⚠️  MEDIUM (Semana 1 pode proceder com workaround):
  3. Network - usar PDFs manuais
- 🔐 REQUERIDO (antes de qualquer carga em produção):
  4. MN approval obter

**Impacto**: Semana 1 (RAG) desliza para 2-3 semanas após resolução de blockers.
**Mitigation**: Semana 2 (SharePoint) e Semana 3 (Validação) prosseguem em paralelo (não dependem de RAG).
**Gate**: Fase 2 só inicia após Semana 1-3 TODAS completas.

---

## 📞 CONTACTS

- **Lead Fase 1**: [Designado]
- **MN (Aprovador)**: mneves@mantaassociados.com
- **On-call**: [Designado]

---

**Última atualização**: 2026-08-03 (diagnóstico + blockers identificados)
**Status Atual**: Semana 1 (RAG) ⏳ bloqueada aguardando infraestrutura. Semana 2 (SharePoint) 🟡 em execução. Semana 3 (Validação) ⏳ pronta para iniciar.
**Próxima atualização**: Quando workflow Fase 1 revisado (wwbblh70y) completar (~1h)

