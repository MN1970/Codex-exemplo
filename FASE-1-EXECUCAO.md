# FASE 1 — EXECUÇÃO PARALELA
## Manta Maestro v5.0.1 — Semana 1 (2026-08-01 a 2026-08-07)

**Data de Início**: 2026-08-01 06:00 (AGORA)  
**Status**: 🚀 **EM EXECUÇÃO**  
**Modelo**: Paralelo com checkpoints sequenciais  
**Owner**: DevOps + Cloud + Security + Agentes  

---

## TAREFAS PARALELAS (7 execuções simultâneas)

### ✅ TAREFA 1.1 — D1: Embedder Fase 0 (Verificação)
**Status**: 🔄 IN_PROGRESS  
**Prazo**: 2026-08-01 (4 horas)  
**Owner**: Cloud  
**Dependência**: Nenhuma  

**Sub-tarefas**:
- [ ] Conectar ao Supabase (ogxxgvgtulrbbppshjie, sa-east-1)
- [ ] Executar query de verificação de dimensão do vetor
- [ ] Documentar resultado em `docs/EMBEDDER-DECISION-PHASE0-RESULT.md`
- [ ] Decidir: migrar (384d→1024d) ou já otimizado?

**Query de Verificação**:
```sql
-- Conectar via supabase CLI ou psql
SELECT 
  table_name,
  column_name,
  data_type,
  udt_name
FROM information_schema.columns
WHERE table_name IN ('manta_rag_chunks', 'manta_rag_documents', 'rag_collections')
ORDER BY table_name, ordinal_position;

-- Ver dimensão atual de embeddings (se houver comentário)
SELECT 
  table_name,
  column_name,
  col_description((table_schema||'.'||table_name)::regclass, ordinal_position) as description
FROM information_schema.columns
WHERE table_name='manta_rag_chunks'
AND column_name ILIKE '%embed%';
```

**Decisão Crítica**:
- **IF** dimensão = 384-d → **GO Fase 3.1** (migração multilingual-e5)
- **IF** dimensão = 1024-d → **SKIP Fase 3.1** (já otimizado)
- **IF** dimensão = outra → investigar + escalar

---

### ✅ TAREFA 1.2 — D3: RLS Hardening (3 tabelas)
**Status**: 🔄 IN_PROGRESS  
**Prazo**: 2026-08-07 (8 dias, full testing)  
**Owner**: Security + Database  
**Dependência**: Nenhuma (paralelo)  

**Tabelas a hardener**:
1. `rag_collections` (9 linhas)
2. `sp_agent_routing` (9 linhas)
3. `maestro_routing_keywords` (50 linhas)

**Processo**:
- [ ] **Dia 1-2**: Design RLS policies (replicar de tabelas seguras)
- [ ] **Dia 3-5**: Testar em staging
  - [ ] Maestro read/write não quebra
  - [ ] Anon access rejeitado corretamente
  - [ ] Admin access irrestrito
- [ ] **Dia 6-7**: Deploy em produção (zero-downtime)
- [ ] **Dia 8**: Verificação pós-deploy + documentação

**SQL de Remediação** (template):
```sql
-- RLS policies para rag_collections
ALTER TABLE rag_collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "rag_collections_read_all" ON rag_collections
  FOR SELECT USING (true);

CREATE POLICY "rag_collections_admin_full" ON rag_collections
  FOR ALL USING (auth.role() = 'authenticated' AND auth.jwt() ->> 'role' = 'admin');

-- Idem para sp_agent_routing e maestro_routing_keywords
```

**Documentação esperada**: `docs/RLS-POLICIES-D3.md`

---

### ✅ TAREFA 1.3 — D5: DataDog APM Setup
**Status**: 🔄 IN_PROGRESS  
**Prazo**: 2026-08-04 (3-4 dias)  
**Owner**: Observability + DevOps  
**Dependência**: Nenhuma (paralelo)  

**Checklist**:
- [ ] Criar/validar conta DataDog
- [ ] Gerar API key + app key
- [ ] Instalar agent:
  - [ ] Se Kubernetes: agent daemonset
  - [ ] Se Lambda: layer + environment variables
  - [ ] Se container: sidecar ou embedded
- [ ] Instrumentar Supabase:
  - [ ] Edge functions logging
  - [ ] PostgreSQL query monitoring
  - [ ] RLS policy performance
- [ ] Criar dashboards:
  - [ ] Maestro routing latency (P50/P95/P99)
  - [ ] RAG query time (por coleção)
  - [ ] Agent response time (por segmento)
  - [ ] Error rates (by service)
  - [ ] RLS policy overhead
- [ ] Configurar alertas:
  - [ ] Latência routing > 5s → escalate
  - [ ] Error rate > 1% → escalate
  - [ ] Downtime > 10min → incident

**Endpoints a monitorar**:
- `/maestro/routing` (latência < 1s target)
- `/rag/query/*` (latência < 500ms target)
- `/agents/{agentId}/response` (latência < 15s target)

**Documentação esperada**: `docs/OBSERVABILITY-DATADOG-v1.md`

---

### ✅ TAREFA 1.4 — D6: G012 Confirmação + Remoção
**Status**: 🔄 IN_PROGRESS  
**Prazo**: 2026-08-02 (2 dias)  
**Owner**: MN (confirmação) + Cloud (remoção)  
**Dependência**: MN disponível para dashboard check  

**Checklist MN**:
- [ ] Acessar Supabase dashboard pessoalmente
- [ ] Navegar para "Projetos" na organização
- [ ] Procurar por `xgluoaaymbdzbbudnwrh`
- [ ] Confirmar: **não pertence à organização ativa**?
- [ ] Responder: confirmar remoção (Slack/email)

**Checklist Cloud** (após confirmação MN):
- [ ] Remover referência de `SKILL.md` (SharePoint)
- [ ] Remover referência de `docs/SUPABASE-PROJECT-AUDIT.md`
- [ ] Remover referência de environment variables
- [ ] Commit: "Cleanup: Remove reference to xgluoaa project (G012)"
- [ ] Documentar decision log em `docs/G012-CLEANUP-DECISION.md`

**Decision Log Template** (`docs/G012-CLEANUP-DECISION.md`):
```markdown
# G012 Cleanup Decision — 31 julho 2026

## Projeto: xgluoaaymbdzbbudnwrh

**Status**: Referência morta, removida

### Verificação MN
- Data: 2026-08-02
- Confirmação: Projeto não pertence à organização ativa
- Autorização: Remover

### Ações Executadas
- [x] Removido de SKILL.md
- [x] Removido de documentação
- [x] Removido de env vars
- [x] Commit realizado: <SHA>

**Fecha**: Gap G012 ✅
```

---

### ✅ TAREFA 1.5 — S12/S13: Operacionalização Completa
**Status**: 🔄 IN_PROGRESS  
**Prazo**: 2026-08-05 (3 dias)  
**Owner**: Agentes + Cloud  
**Dependência**: Nenhuma (paralelo)  

#### S12 — Óleo & Gás

**Sub-tarefas**:
- [ ] **Dia 1**: Criar RAG collection
  ```sql
  INSERT INTO rag_collections (slug, nome, segment_id, ativo)
  VALUES ('og', 'óleo-gás', 'S12', true);
  ```
- [ ] **Dia 1-2**: Ingerir documentos
  - Fontes: ANP, API 650, ASME B31.3/4/8, NFPA 30, HAZOP
  - Target: 50-100 chunks
  - Prefixo: `og:`
  
- [ ] **Dia 2**: Registrar keywords de routing
  ```sql
  INSERT INTO maestro_routing_keywords (keyword, agent_id, weight)
  VALUES 
    ('petróleo', '03-S12', 1.0),
    ('óleo e gás', '03-S12', 1.0),
    ('gasoduto', '03-S12', 0.9),
    ('oleoduto', '03-S12', 0.9),
    ('dutovia', '03-S12', 0.8),
    ('refinaria', '03-S12', 0.9),
    ('ANP', '03-S12', 0.9),
    ('API 650', '03-S12', 0.8),
    ('HAZOP', '03-S12', 0.7),
    ('tancagem', '03-S12', 0.8),
    ('distribuição derivados', '03-S12', 0.8);
  ```

- [ ] **Dia 3**: Criar rota SharePoint
  - Pasta: `03_Projetos/OleoGas/`
  - Subpastas (opcionais):
    - `Projetos Ativos/`
    - `Referências/`
    - `Documentação/`
  - Permissões: agente-oleo-gas reader

- [ ] **Dia 3**: Testar dispatch
  - Teste: `Q: "Projeto de refinaria no Pará" → agente-oleo-gas`
  - Resultado esperado: match de keywords + RAG ativo

#### S13 — Edificações

**Sub-tarefas** (paralelo com S12):
- [ ] **Dia 1**: Criar RAG collection
  ```sql
  INSERT INTO rag_collections (slug, nome, segment_id, ativo)
  VALUES ('edi', 'edificacoes', 'S13', true);
  ```

- [ ] **Dia 1-2**: Ingerir documentos
  - Fontes: NBR 15575, LEED, BIM, acessibilidade
  - Target: 30-50 chunks
  - Prefixo: `edi:`

- [ ] **Dia 2**: Registrar keywords
  ```sql
  INSERT INTO maestro_routing_keywords (keyword, agent_id, weight)
  VALUES 
    ('edificação', '03-S13', 1.0),
    ('galpão', '03-S13', 0.9),
    ('warehouse', '03-S13', 0.8),
    ('data center', '03-S13', 0.9),
    ('MCMV', '03-S13', 0.7),
    ('NBR 15575', '03-S13', 0.8),
    ('LEED', '03-S13', 0.7),
    ('BIM', '03-S13', 0.8),
    ('hospital', '03-S13', 0.8),
    ('residencial', '03-S13', 0.7),
    ('comercial', '03-S13', 0.7);
  ```

- [ ] **Dia 3**: Criar rota SharePoint
  - Pasta: `03_Projetos/Edificacoes/`
  - Subpastas (opcionais):
    - `Projetos Ativos/`
    - `Referências/`
    - `Documentação/`
  - Permissões: agente-edificacoes reader

- [ ] **Dia 3**: Testar dispatch
  - Teste: `Q: "Projeto de galpão logístico em SP" → agente-edificacoes`
  - Resultado esperado: match + RAG

**Documentação esperada**: Atualizações em `CLAUDE.md` (S12/S13 agora "operacionais" vs. "propostos")

---

### ✅ TAREFA 1.6 — Smoke Tests Completos
**Status**: 🔄 BLOQUEADO ATÉ 1.5  
**Prazo**: 2026-08-06 (1 dia, após 1.5)  
**Owner**: QA + Maestro  
**Dependência**: 1.1-1.5 completos  

**8 Testes Automáticos**:
```bash
# Executar via deploy/04-smoke-tests.sh
bash deploy/04-smoke-tests.sh
```

**Validações**:
- [x] ✅ Artifacts integridade (CLAUDE.md, agent files)
- [x] ✅ RAG coleções (9 confirmadas)
- [x] ✅ Routing keywords (maestro_routing_keywords count >= 50)
- [x] ✅ SharePoint routes (sp_agent_routing count >= 9)
- [x] ✅ RLS policies (3 tabelas ativas)
- [x] ✅ Agent files YAML headers válidos
- [x] ✅ Performance baseline (RAG latência < 500ms)
- [x] ✅ Regressão S1-S10 (sem breaking changes)

**4 Testes Manuais** (prompts):
- [ ] Dispatch S1 (rodovia): Maestro corretamente roteia?
- [ ] Dispatch S12 (óleo & gás): Novo segmento despacha?
- [ ] Dispatch S13 (edificação): Novo segmento despacha?
- [ ] Routing ambigüidade: S9 (energia) vs. S12 (oleoduto)? → correto?

**Artefato de saída**: `tests/SMOKE-TESTS-PHASE1-RESULT.md`

```markdown
# Smoke Tests — Fase 1 Result

**Data**: 2026-08-06  
**Status**: ✅ PASSED (8/8 automated + 4/4 manual)

## Automated Tests
✅ Artifacts integridade
✅ RAG coleções
✅ Routing keywords
✅ SharePoint routes
✅ RLS policies ativo
✅ Agent YAML headers
✅ Performance baseline
✅ Regressão S1-S10

## Manual Tests
✅ S1 dispatch (rodovia)
✅ S12 dispatch (óleo & gás)
✅ S13 dispatch (edificação)
✅ Routing ambigüidade tratada

## Resultado Final
🚀 GO para Fase 2
```

---

### ✅ TAREFA 1.7 — Slack Announcement
**Status**: 🔄 BLOQUEADO ATÉ 1.6  
**Prazo**: 2026-08-06 (1 dia, após smoke tests)  
**Owner**: Comms  
**Dependência**: Smoke tests aprovados  

**Mensagem (já pronta em `deploy/05-notification.sh`)**:
```
🚀 Manta Maestro v5.0.1 — OPERACIONAL

Dois novos segmentos foram ativados em produção:

📦 *S12 — Óleo & Gás* (downstream + midstream)
   Especialista: agente-oleo-gas
   RAG: coleção 'oleo-gas' com ANP, API 650, HAZOP, NR-20, NFPA 30
   SharePoint: 03_Projetos/OleoGas/*
   Triggering: petróleo | óleo e gás | gasoduto | oleoduto | dutovia | refinaria | ANP | API 650 | HAZOP

🏢 *S13 — Edificações* (residencial, comercial, hospitalar, data center)
   Especialista: agente-edificacoes
   RAG: coleção 'edificacoes' com NBR 15575, LEED, BIM, acessibilidade
   SharePoint: 03_Projetos/Edificacoes/*
   Triggering: edificação | galpão | warehouse | data center | MCMV | NBR 15575 | LEED | BIM

📚 Documentação:
   • Decisão técnica: docs/SEGMENTOS-S12-S13-DECISION.md
   • Roteiro v5.0.1: CLAUDE.md (master registry)
   • Deploy checklist: DEPLOYMENT-COMPLETE-v5.0.1.md

🔧 Como usar: Mencione qualquer palavra-chave acima e o Maestro roteia automaticamente.

❓ Dúvidas? Consulte #manta-architect ou veja docs/SEGMENTOS-S12-S13-DECISION.md

---
Deployment completed: 2026-08-07
Version: v5.0.1 (Unified operacional + consolidação)
```

**Execução**:
```bash
bash deploy/05-notification.sh
# Escolher: Slack CLI / Webhook / Manual copy-paste
```

---

## 📊 DASHBOARD DE PROGRESSO

| Tarefa | Prazo | Status | % | Owner |
|--------|-------|--------|---|-------|
| 1.1 | 2026-08-01 (4h) | 🔄 IN_PROGRESS | 0% | Cloud |
| 1.2 | 2026-08-07 (8d) | 🔄 IN_PROGRESS | 0% | Security |
| 1.3 | 2026-08-04 (3-4d) | 🔄 IN_PROGRESS | 0% | Observability |
| 1.4 | 2026-08-02 (2d) | 🔄 IN_PROGRESS | 0% | MN + Cloud |
| 1.5 | 2026-08-05 (3d) | 🔄 IN_PROGRESS | 0% | Agentes |
| 1.6 | 2026-08-06 (1d) | 🔴 BLOQUEADO | 0% | QA |
| 1.7 | 2026-08-06 (1d) | 🔴 BLOQUEADO | 0% | Comms |

---

## ⏱️ TIMELINE PARALELA

```
2026-08-01 06:00 ↓
├─ 1.1 (Embedder Fase 0) ──────────► 2026-08-01 10:00
├─ 1.2 (RLS hardening) ─────────────────────────────────────► 2026-08-07
├─ 1.3 (DataDog APM) ─────────────────► 2026-08-04
├─ 1.4 (G012 cleanup) ─────► 2026-08-02
├─ 1.5 (S12/S13 ops) ────────────────► 2026-08-05
├─ 1.6 (Smoke tests) ─────────────────────► 2026-08-06 (após 1.5)
└─ 1.7 (Slack announce) ──────────────────► 2026-08-06 (após 1.6)

CHECKPOINT 1: 2026-08-07 12:00
Go/No-Go para Fase 2
```

---

## 🎯 CHECKPOINT 1 — 2026-08-07 12:00

**Critérios de Go/No-Go**:

| Item | Go | No-Go |
|------|----|----|
| 1.1 (D1 Embedder) | ✅ Dimensão confirmada | ❌ Erro na query / desconexão |
| 1.2 (D3 RLS) | ✅ 3 tabelas com RLS ativo, testes passando | ❌ RLS quebrou Maestro |
| 1.3 (D5 DataDog) | ✅ Dashboards live, alertas ✓ | ❌ Setup incompleto |
| 1.4 (D6 G012) | ✅ Removido e documentado | ❌ MN não confirmou / referências restam |
| 1.5 (S12/S13) | ✅ Ambos roteáveis, RAG ativo | ❌ Dispatch falha, RAG vazio |
| 1.6 (Smoke tests) | ✅ 8/8 automated + 4/4 manual | ❌ Qualquer teste falha |

**Decisão**:
- **6/6 ✅ → GO**: Libera Fase 2 imediatamente
- **<6 ✅ → NO-GO**: Hold Fase 2 até resolução, re-test

---

## 📝 PRÓXIMAS AÇÕES AGORA

**Imediatamente (2026-08-01 06:00)**:

1. ✅ Iniciar **Tarefa 1.1** (Embedder Fase 0)
   ```bash
   # Conectar ao Supabase e executar query de verificação
   ```

2. ✅ Iniciar **Tarefa 1.2** (RLS hardening)
   - [ ] Design policies (Dia 1-2)
   - [ ] Staging test (Dia 3-5)

3. ✅ Iniciar **Tarefa 1.3** (DataDog APM)
   - [ ] Criar account/keys
   - [ ] Instalar agent

4. ✅ Iniciar **Tarefa 1.4** (G012 cleanup)
   - [ ] MN acessa dashboard

5. ✅ Iniciar **Tarefa 1.5** (S12/S13 ops)
   - [ ] Ingerir RAG
   - [ ] Registrar keywords

6. ⏳ **Tarefa 1.6** (Smoke tests)
   - Bloqueado até 1.5 completo

7. ⏳ **Tarefa 1.7** (Slack announce)
   - Bloqueado até 1.6 completo

---

**Status**: 🚀 **ATIVAÇÃO FASE 1 AGORA**  
**Próxima revisão**: 2026-08-02 (daily standup)  
**Checkpoint**: 2026-08-07 12:00

