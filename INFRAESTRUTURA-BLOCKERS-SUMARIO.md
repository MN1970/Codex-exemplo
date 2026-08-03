# Infraestrutura Blockers — Sumário Executivo

**Data**: 2026-08-03  
**Status**: Diagnóstico concluído, 4 blockers identificados  
**Impacto**: Semana 1 (RAG) aguardando infraestrutura. Semana 2 (SharePoint) em execução paralela.  

---

## 📊 Visão Geral

Fase 1 foi iniciada com 10 agentes em paralelo conforme aprovado. Os agentes S6-S10 executaram e descobriram **4 bloqueadores reais na infraestrutura de produção** que impedem o carregamento de RAG (Semana 1). Em vez de fabricar dados fictícios, os agentes documentaram os problemas e pivotaram para tarefas executáveis (Semana 2 SharePoint).

**Resultado**: Fase 1 continua, mas com sequência revisada:
- ⏳ **Semana 1 (RAG)**: Bloqueada, aguardando infraestrutura
- 🟡 **Semana 2 (SharePoint)**: Em execução (5 agentes gerando SKILL.md)
- 🟡 **Semana 3 (Validação)**: Preparada, aguarda Semana 1-2

---

## 🚨 Bloqueadores Críticos (Semana 1)

### 1️⃣ **BLOCKER: Schema Supabase — Coluna `embedding` faltando**

**Problema**:
- Tabela `public.rag_chunks` (alvo do runbook) tem schema: `id, collection, prefix, title, content, source, segment, created_at`
- **Falta**: coluna `embedding` ou `collection_slug` necessária para vector search
- Tabela alternativa `public.manta_rag_chunks` **existe** com colunas `embedding` e `embedding_m3` (384d, modelo bge-small-en-v1.5)

**Decisão Necessária**:
- ❓ Qual é a tabela CANONICAL para Manta Maestro RAG? `rag_chunks` ou `manta_rag_chunks`?
- ❓ Se `rag_chunks`, executar: `ALTER TABLE public.rag_chunks ADD COLUMN embedding vector(384)`?
- ❓ Se `manta_rag_chunks`, remapear o runbook para usar essa tabela como target?

**Owner**: DevOps + Manta 16 (arquiteto-ia)  
**Esforço**: 1-2 dias após decisão  
**Urgência**: 🔴 CRÍTICO (bloqueia RAG load)

---

### 2️⃣ **BLOCKER: Ferramenta de Embeddings — Não disponível**

**Problema**:
- Nenhuma ferramenta de geração de embeddings está disponível nesta sessão
- Supabase project `manta-maestro` tem extensão `pgvector` (v0.8.0) instalada mas **sem Edge Function**
- Nenhuma integração com Claude Embeddings API ou similar
- **PASSO 3 do runbook** (EMBED: "Gerar embeddings vetoriais") é estruturalmente inexequível

**Decisão Necessária**:
- ❓ Integrar Claude Embeddings API (via MCP Supabase MCP server)?
- ❓ Criar Edge Function Supabase com modelo bge-small-en-v1.5?
- ❓ Usar serviço externo de embeddings?

**Owner**: Manta 16 (arquiteto-ia) + DevOps  
**Esforço**: 3-5 dias após decisão + testes  
**Urgência**: 🔴 CRÍTICO (sem embeddings, sem RAG)

---

### 3️⃣ **BLOCKER: Network — HTTP 403 bloqueando gov.br**

**Problema**:
- Fetch de fontes públicas legítimas retorna HTTP 403:
  - Lei 12.334/2010 (planalto.gov.br) ❌
  - Lei 14.026/2020 (planalto.gov.br) ❌
  - RBAC 154 (camara.leg.br) ❌
  - Outras resoluções em domínios .gov.br ❌
- Retry em múltiplos mirrors: sem sucesso
- Bloqueio não é transitório (mesmo domínio, consistente)

**Solução Possível**:
- ✅ Upload manual de PDFs via SharePoint (Semana 2 já tem estrutura)
- ✅ Acesso autenticado a gov.br (se disponível em Manta)
- ✅ Usar mirrors internos ou cached Manta de regulamentações

**Owner**: Manta 06 (modelagem/dados) ou DevOps  
**Esforço**: 1-2 dias para coletar PDFs manualmente  
**Urgência**: ⚠️  MEDIUM (workaround: upload manual)

---

### 4️⃣ **REQUERIDO: Aprovação MN — Não obtida**

**Problema**:
- `CLAUDE.md` v4.2 **deploy checklist** lista: `[ ] Gate humano: aprovação MN antes de merge`
- Carregar dados em `manta-maestro` (DB de produção) sem aprovação viola processo documentado
- Agentes recusaram intencionalmente fabricar dados para não poluir DB de produção com conteúdo fictício

**Decisão Necessária**:
- ❓ Obter aprovação MN (mneves@mantaassociados.com) explícita para prosseguir com Semana 1 RAG?
- ❓ Incluir feedback de blockers 1-3 na comunicação a MN?

**Owner**: MN (mneves@mantaassociados.com)  
**Esforço**: Comunicação hoje, decisão dentro de 24-48h  
**Urgência**: 🔐 REQUERIDO (gate antes de carga em produção)

---

## ✅ Em Execução (Bloqueadores Resolvidos)

### Semana 2: SharePoint Setup (5 agentes S6-S10)

**Status**: 🟡 EM PROGRESSO (workflow wwbblh70y)

5 agentes rodando em paralelo, cada um:
1. Gerando conteúdo SKILL.md (~3-5 KB) com:
   - Título: Manta 03-Sx — agente-X
   - Especialidade e fases suportadas
   - Ferramentas MCP acessadas
   - Aliases de roteamento
2. Documentando estrutura de pastas esperada:
   - `04_IA/Manta-Maestro/01-agentes-fundamentais/agente-X/`
   - `03_Projetos/X/` (para projetos)
3. Listando fontes de referência que deveriam estar em `refs/`

**Saída Esperada**:
- 5 arquivos SKILL.md (pronto para upload a SharePoint)
- Estrutura de pastas documentada
- Lista de referências por segmento
- Status: ready for SharePoint upload

**Não Depende De**: Semana 1 (RAG) — execução paralela ✅

---

### MCP Config Generation

**Status**: 🟡 EM PROGRESSO (mesmo workflow)

Gerando:
- `.mcp.json` com agentes S6-S10 + integrações (Supabase, SharePoint, GitHub, WebSearch)
- `.claude/settings.json` com discovery, artifact caching, prompt caching
- `.claude/hooks/validate-claude-md.sh` (pre-commit hook)

**Saída Esperada**:
- 3 arquivos config prontos para committar
- Estrutura MCP documentada

---

### RAG Planning

**Status**: 🟡 EM PROGRESSO (mesmo workflow)

Agente mapeando:
- 4 blockers confirmados
- Ações corretivas ordenadas por dependência
- Esforço e timeline estimada
- Documentação para README: "SEMANA 1 ROADMAP"

---

## 📅 Timeline Revisado

```
2026-08-03 (Hoje):
├─ ✅ Diagnóstico: infraestrutura validada
├─ ✅ Semana 2: SharePoint setup iniciado (5 agentes)
├─ ✅ MCP Config: templates gerados
├─ 📝 RAG Plan: documentar blockers + ações
└─ 📞 Comunicação: enviar sumário a MN

2026-08-04 — 2026-08-05 (D+1 a D+2):
├─ ⏳ Aguardando: MN approval + decisões arquiteturais
├─ 🔧 DevOps: Implementar fixes (schema, embeddings)
├─ 📦 Manta 06: Coletar PDFs / resolver network
└─ 🟡 Semana 2: Continuar (independente)

2026-08-06 — 2026-08-10 (D+3 a D+7):
├─ ✅ Infraestrutura: schema + embeddings prontos
├─ ✅ Network: PDFs coletados / acesso autenticado resolvido
├─ 🟡 Semana 1 (RAG): Inicia carregamento real (5 agentes)
└─ 🟡 Semana 2: Finaliza uploads SharePoint + validação

2026-08-11 — 2026-08-14 (D+8 a D+11):
├─ 🟡 Semana 3 (Validação): Routing tests + gate Fase 2
└─ 📊 Relatório Final: sucesso vs. falta

**GATE Fase 2**: Approx. 2026-08-14 (se tudo resolver rápido) ou 2026-08-21 (timeline conservadora)
```

---

## 🎯 Próximos Passos

### Hoje (D+0):
1. ✅ **Concluir workflow wwbblh70y** → extrair SKILL.md, MCP config, RAG plan
2. 📝 **Criar .mcp.json e settings.json** nos arquivos de config
3. 📞 **Comunicar a MN**:
   - Sumário de 4 blockers
   - Ações corretivas + owners
   - Timeline revisado
   - Solicitar: aprovação + decisões arquiteturais (schema, embeddings)

### D+1 a D+2 (após MN approval):
4. 🔧 **DevOps**: Executar fixes infraestrutura
   - Decidir e implementar schema (rag_chunks ou manta_rag_chunks)
   - Integrar ou criar embeddings service
5. 📦 **Manta 06**: Coletar/disponibilizar PDFs dos documentos

### D+3+ (infraestrutura pronta):
6. 🚀 **Iniciar Semana 1**: 5 agentes RAG loading com infraestrutura corrigida
7. 🟡 **Continuação Semana 2-3**: Validações + gate Fase 2

---

## 📊 Métricas & Ganhos Fase 1 (Revisado)

| Métrica | Baseline | Esperado | Status |
|---------|----------|----------|--------|
| Semana 1 (RAG) — Timeline | 6-8 dias | +2-3 semanas (bloqueadores) | ⏳ Remapped |
| Semana 2 (SharePoint) — Timeline | 5-6 dias | 2-3 dias (content ready) | 🟡 Em track |
| Semana 3 (Validação) — Timeline | 3-4 dias | 3-4 dias (aguarda 1-2) | 🟡 Pronta |
| **Fase 1 Total** | 14-18 dias | ~21-28 dias (infraestrutura) | ⏳ Revisado |
| MCP Config | 0% | 100% (em progresso) | 🟡 Adiantado |
| Bloqueadores Identificados | 0 | 4 (documentados) | ✅ Resolvido |

---

## 📞 Contatos

- **MN (Aprovação, decisões)**: mneves@mantaassociados.com
- **Manta 16 (Arquiteto-IA, schema/embeddings)**: [Slack @manta-16]
- **DevOps (Infraestrutura, Supabase)**: [Slack @devops]
- **Manta 06 (Dados, PDFs)**: [Slack @manta-06]

---

**Relatório preparado por**: Claude Code (Fase 1 Diagnosis Workflow)  
**Data**: 2026-08-03  
**Status**: ✅ Diagnóstico concluído, aguardando ação de MN

