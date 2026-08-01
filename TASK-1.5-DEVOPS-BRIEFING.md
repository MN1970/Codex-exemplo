# 🚨 TASK 1.5 — S12/S13 OPERATIONALIZATION

**CRITICIDADE**: 🔴 **BLOQUEADOR CRÍTICO DO CAMINHO CRÍTICO**

**Despachado**: 2026-08-01  
**Owner**: DevOps  
**Deadline**: 2026-08-05 18:00 UTC (3 dias)  
**Blocked by**: Ninguém — INICIA HOJE  
**Blocks**: Task 1.6 (Smoke Tests), Task 1.7 (Slack Announcement), CHECKPOINT 1

---

## 📋 O QUÊ FAZER

Operacionalizar 2 segmentos na Maestro Supabase:
- **S12 — Óleo & Gás** (downstream + midstream CIVIL engineering; NOT E&P)
- **S13 — Edificações** (residencial, comercial, galpão, hospitalar, data center; NOT imobiliário/Manta 04)

Hoje eles existem como:
- ✅ Agentes `.md` criados (`agente-oleo-gas.md`, `agente-edificacoes.md`)
- ✅ Registrados em Supabase `manta_agent_capabilities` (ativo=true desde 2026-07-12)
- ❌ SEM RAG collections
- ❌ SEM routing keywords
- ❌ SEM SharePoint folders
- ❌ NÃO despachável pelo Maestro (Manta 00 router não consegue rotear para S12/S13 ainda)

**Objetivo**: Fazer S12/S13 100% despachável (igual a S6-S10 hoje).

---

## ✅ CHECKLIST — 3 PARTES

### Parte 1: RAG Collections (Supabase)

**Criar 2 coleções em `manta_rag_chunks`**:

1. **og: (Óleo & Gás)**
   - Prefixo: `og:`
   - Documentos inclusos: ANP editais, API 650/653, ASME B31.3/4/8, NFPA 30, HAZOP
   - Chunks: ~20-30 (padrão = mesma quantidade que S6-S10, ex: por: 18, aer: 12)
   - Embedding: 1024-dimensional bge-m3 (confirmado em v5.0.1)
   - Status: `active`
   - Comando SQL template:
     ```sql
     INSERT INTO manta_rag_chunks (collection_id, chunk_text, embedding, metadata, created_at)
     SELECT 'og_collection_id', chunk, embedding_1024d, '{"source":"ANP Edital XYZ", ...}', NOW()
     FROM staging_og_chunks;
     ```

2. **edi: (Edificações)**
   - Prefixo: `edi:`
   - Documentos inclusos: NBR 15575, LEED, BIM, ABNT edificação
   - Chunks: ~20-30 (mesma escala)
   - Embedding: 1024-dimensional bge-m3
   - Status: `active`
   - Comando SQL template (análogo ao og:)

**Referência de volume**: S6-S10 têm entre 12-30 chunks cada. Manter 20±5 por coleção.

**Verificação**: Rodar `SELECT COUNT(*) FROM manta_rag_chunks WHERE collection LIKE 'og:%' OR 'edi:%';` — esperar ≥20 per collection.

---

### Parte 2: Routing Keywords (Supabase)

**Registrar em `maestro_routing_keywords`**:

1. **Para agente-oleo-gas (S12)**
   - Keywords: `petróleo`, `óleo`, `gás`, `gasoduto`, `oleoduto`, `dutovia`, `refinaria`, `ANP`, `tancagem`, `API 650`, `ASME B31`, `NFPA 30`, `HAZOP`, `terminal combustíveis`, `GLP`, `distribuidora`
   - Peso: 0.8-0.9 (alto, para garantir match rápido)
   - Agent ID: `03-S12` (verificar em `manta_agent_capabilities`)
   - Comando SQL template:
     ```sql
     INSERT INTO maestro_routing_keywords (keyword, agent_id, weight, language, active)
     VALUES 
       ('petróleo', '03-S12', 0.85, 'pt', true),
       ('gasoduto', '03-S12', 0.85, 'pt', true),
       ...
     ```

2. **Para agente-edificacoes (S13)**
   - Keywords: `edificação`, `torre residencial`, `comercial`, `galpão`, `warehouse`, `data center`, `hospital`, `universidade`, `MCMV`, `NBR 15575`, `LEED`, `BIM`, `estrutura predial`
   - Peso: 0.8-0.9
   - Agent ID: `03-S13`

**Verificação**: Rodar `SELECT COUNT(*) FROM maestro_routing_keywords WHERE agent_id IN ('03-S12', '03-S13');` — esperar ≥10 per agent.

---

### Parte 3: SharePoint Folders (Manta Associados site)

**Criar 2 pastas em `/03_Projetos/`**:

1. **`/03_Projetos/OleoGas/`**
   - Padrão: Mesmo layout que `/03_Projetos/Portos/`, `/03_Projetos/Energia/`, etc.
   - Estrutura sugerida:
     ```
     OleoGas/
     ├── README.md (link para agente-oleo-gas.md)
     ├── Templates/
     │   ├── Proposta-OG.docx
     │   ├── Orçamento-OG.xlsx
     │   └── Cronograma-OG.mpp
     ├── Referências/
     │   └── ANP-Editais/ (PDFs)
     ├── Projetos-Ativos/
     └── Arquivos/
     ```
   - Permissões: Admin RW, Agent Owner RW, User R (padrão RLS)

2. **`/03_Projetos/Edificacoes/`**
   - Padrão: Mesmo layout acima
   - Estrutura:
     ```
     Edificacoes/
     ├── README.md (link para agente-edificacoes.md)
     ├── Templates/
     ├── Referências/ (NBR, LEED, BIM specs)
     ├── Projetos-Ativos/
     └── Arquivos/
     ```
   - Permissões: Idem

**Verificação**: Acessar SharePoint → Manta Associados → 03_Projetos → confirmar 2 pastas criadas e populadas com README.

---

## 📊 DEFINIÇÃO DE PRONTO (Definition of Done)

Task 1.5 é ✅ completa quando:

- [ ] 2 RAG collections criadas em Supabase (`og:`, `edi:`)
- [ ] ≥10 routing keywords por agente registradas e testadas
- [ ] Maestro (Manta 00) consegue rotear pergunta mencionando "óleo e gás" → agente-oleo-gas
- [ ] Maestro consegue rotear pergunta mencionando "edificação" → agente-edificacoes
- [ ] 2 SharePoint folders criadas com conteúdo base (README + templates)
- [ ] Smoke tests iniciados (Task 1.6) — podem começar após este checklist ✅

---

## 🔗 DOCUMENTAÇÃO DE REFERÊNCIA

- **Agente spec**: `.claude/agents/agente-oleo-gas.md` (v1.0, criado 2026-07-31)
- **Agente spec**: `.claude/agents/agente-edificacoes.md` (v1.0, criado 2026-07-31)
- **Routing logic**: `CLAUDE.md` — seção "ROUTING — Maestro (Manta 00)"
- **RAG template**: `CLAUDE.md` — seção "RAG — Coleções em Supabase"
- **Comparação**: S6-S10 (Portos, Aeroportos, Saneamento, Energia, Barragens) — já operacional, use como template
- **SharePoint setup**: `docs/COWORK-INTEGRATION-GUIDE.md` — seção "SharePoint folders"

---

## ⏱️ TIMELINE — 3 DIAS

**2026-08-01 (T0)**: 
- Receber briefing ← VOCÊ ESTÁ AQUI
- Preparar SQL para RAG collections
- Preparar keyword list

**2026-08-02 (T+1)**:
- Aplicar SQL em staging (manta-staging project)
- Testar roteamento em staging
- Criar pastas SharePoint (pode ser paralelo)

**2026-08-03 (T+2)**:
- Validar completamente em staging (0 erros esperado)
- Aprovar deployment para produção

**2026-08-04 (T+3)**:
- Deploy em produção (ogxxgvgtulrbbppshjie)
- Verificação final: Maestro roteia S12/S13? ✅

**2026-08-05 18:00 (T+4, Deadline)**:
- Task 1.5 ✅ COMPLETA
- Task 1.6 (Smoke Tests) pode iniciar

---

## 🆘 BLOQUEADORES / RISCOS

**Sem bloqueadores conhecidos** — você tem:
- ✅ Agentes `.md` prontos
- ✅ Capacidades em produção (ativo=true)
- ✅ Routing logic documentada
- ✅ Templates de S6-S10 para copiar

**Risco**: Se houver erro na SQL de RAG, smoking tests falham. **Recomendação**: Testar em staging completamente antes de prod.

---

## 📞 CONTATO & ESCALAÇÃO

- **Questions**: Consulte `docs/SEGMENTOS-S12-S13-DECISION.md` (investigação que originou S12/S13)
- **Bloqueador**: Ping @MN (mneves@mantaassociados.com)
- **Teste em Staging**: Use `manta-staging` project (não prod diretamente)
- **Daily status**: Reportar em daily standup 17:00 UTC

---

## 🎯 IMPORTÂNCIA

**Este é o bloqueador crítico do Phase 1**. Se terminar hoje/amanhã, o projeto entra em buffer. Se atrasar, CHECKPOINT 1 (2026-08-07) fica em risco.

**Maestro recomenda**: Prioridade MÁXIMA hoje 2026-08-01.

---

**Despachado por**: Maestro (Manta 00)  
**Data**: 2026-08-01 (agora)  
**Status**: 🔴 CRÍTICO — Inicia HOJE
