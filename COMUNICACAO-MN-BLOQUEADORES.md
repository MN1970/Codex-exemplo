# 📞 COMUNICAÇÃO: Bloqueadores Fase 1 — Decisões Urgentes

**Para:** Mauricio Neves (mneves@mantaassociados.com)  
**De:** Claude Code (Fase 1 Diagnostic Workflow)  
**Data:** 2026-08-03  
**Assunto:** 4 Bloqueadores críticos — Fase 1 Aguardando Aprovação e Decisões Arquiteturais  
**Urgência:** 🔴 CRÍTICA — Semana 1 (RAG) bloqueada aguardando resposta  

---

## 📋 Executivo

Fase 1 foi iniciada conforme aprovado em 2026-08-02. Workflow diagnóstico completou ontem identificando **4 bloqueadores reais** que impedem o carregamento de dados em produção:

1. **Schema Supabase**: tabela `rag_chunks` sem coluna `embedding`
2. **Embeddings Service**: sem ferramenta de geração disponível
3. **Network Access**: bloqueio HTTP 403 em gov.br
4. **Approval Gate**: exigida aprovação MN antes de carga em produção

**Semana 2 (SharePoint)** e **Semana 3 (Validação)** prosseguem em paralelo.  
**Semana 1 (RAG)** aguarda resolução destes blockers + sua aprovação.

---

## 🚨 Bloqueadores Detalhados

### BLOCKER 1: Schema Supabase — Coluna `embedding` Faltando

**Status**: 🔴 CRÍTICO  
**Descoberto por**: Infrastructure Diagnostic Agent  
**Data de descoberta**: 2026-08-03

#### Problema
A tabela `public.rag_chunks` (alvo do runbook CLAUDE.md v4.2 para carregar S6-S10) tem schema:
```sql
id(int4), collection(varchar), prefix(varchar), title(varchar), 
content(text), source(varchar), segment(varchar), created_at(timestamp)
```

**Falta**: Coluna `embedding` (vector) necessária para busca semântica.

#### Situação Atual
- `rag_chunks` hoje tem apenas **15 linhas** (3 por coleção nova, stubs sem conteúdo real)
- Função `public.rag_search()` referencia `public.rag_documents` que **NÃO EXISTE** (quebrada)
- Tabela alternativa `public.manta_rag_chunks` **existe** com colunas `embedding`(384d) e `embedding_m3`(1024d) **mas está vazia** (0/204 rows têm embedding_m3)

#### Decisão Necessária
Escolher UMA das opções:

**Opção A**: Usar `manta_rag_chunks` como tabela canonical
- ✅ Já tem coluna embedding funcional
- ✅ Pipeline manta_rag_search já implementado
- ⚠️ Precisa migrar 5 coleções S6-S10 para esse pipeline
- ⏱️ Esforço: 2-3 dias

**Opção B**: Migrar `rag_chunks` com coluna embedding
- ✅ Mantém arquitetura planejada no CLAUDE.md
- ✅ Compatibilidade com runbook existente
- ⚠️ Requer migração DDL em produção
- ⚠️ Precisa criar função rag_search funcional
- ⏱️ Esforço: 2-3 dias

**Recomendação**: Opção A (usar `manta_rag_chunks`) — menos risco, pipeline já testado.

**Owner proposto**: DevOps  
**Prazo**: Comunicar decisão hoje, implementar amanhã-dia seguinte  
**ETA resolução**: 2026-08-05

---

### BLOCKER 2: Embeddings Service — Não Disponível

**Status**: 🔴 CRÍTICO  
**Descoberto por**: Infrastructure Diagnostic Agent  
**Data de descoberta**: 2026-08-03

#### Problema
Nenhuma ferramenta de geração de embeddings está disponível nesta sessão:

- ❌ Claude Embeddings API: não integrada
- ❌ Supabase Edge Function: nenhuma implantada (lista vazia)
- ❌ Modelo local: sem acesso
- ❌ Serviço externo: não configurado

**Impacto**: PASSO 3 do runbook (EMBED: "Gerar embeddings vetoriais") é **estruturalmente impossível**.

#### Situação Atual
- `manta_rag_chunks` tem coluna `embedding_m3` vector(1024) — 100% vazio
- Nenhum embedding foi gerado para nenhum dos 5 segmentos (S6-S10)
- Embeddings existentes são apenas para pipeline legado (S1-S4), desatualizado

#### Decisão Necessária
Escolher COMO gerar embeddings:

**Opção A**: Integrar Claude Embeddings API (via MCP)
- ✅ Sem setup adicional em Supabase
- ✅ Modelo atualizado (Claude embeddings)
- ✅ Escalável dinamicamente
- ⚠️ Custo por API call
- ⏱️ Esforço: 2-3 dias (integração + testes)

**Opção B**: Criar Supabase Edge Function com modelo local (bge-small-en-v1.5)
- ✅ Sem custo de API externo
- ✅ Fica em produção indefinidamente
- ✅ Fast local inference
- ⚠️ Precisa setup em Supabase
- ⚠️ Deploy e mantenibilidade
- ⏱️ Esforço: 3-5 dias

**Opção C**: Usar OpenAI/Cohere API (alternativa comercial)
- ✅ Solução pronta
- ⚠️ Custo permanente
- ⚠️ Dependência externa

**Recomendação**: Opção A (Claude Embeddings API) — integração simples, modelo de ponta, custa pouco.

**Owner proposto**: Manta 16 (arquiteto-ia)  
**Prazo**: Comunicar decisão hoje, implementar + testar 2-3 dias  
**ETA resolução**: 2026-08-05

---

### BLOCKER 3: Network Access — HTTP 403 em gov.br

**Status**: ⚠️ MEDIUM (tem workaround)  
**Descoberto por**: RAG Loading Agents (tentativas de fetch)  
**Data de descoberta**: 2026-08-03

#### Problema
Fetch de fontes públicas legítimas retorna HTTP 403 (bloqueio de proxy):

- Lei 12.334/2010 (planalto.gov.br) ❌
- Lei 14.026/2020 (planalto.gov.br) ❌
- RBAC 154 (camara.leg.br) ❌
- Outras resoluções .gov.br ❌

**Bloqueio ocorre no nível do proxy** de saída da sessão, antes de chegar ao site (não é erro transitório).

#### Impacto
Impossível fazer scraping automático de documentação oficial para as 5 coleções.

#### Solução Possível

**Opção A**: Upload manual de PDFs (via SharePoint)
- ✅ Simples implementação
- ✅ Agentes podem processar uploads
- ⚠️ Requer esforço manual de coleção
- ⏱️ Esforço: 1-2 dias de coleta + validação

**Opção B**: Acesso autenticado a gov.br
- ✅ Automatizado
- ⚠️ Requer credenciais + configuração VPN/proxy
- ⏱️ Esforço: 1 dia (se credenciais disponíveis)

**Opção C**: Usar mirrors internos Manta (se existe)
- ✅ Rápido, já centralizado
- ⚠️ Requer validação de atualização

**Recomendação**: Opção A (upload manual) — rápido, confiável, não depende de infraestrutura.

**Owner proposto**: Manta 06 (modelagem/dados)  
**Prazo**: Identificar PDFs necessários hoje, coletar + validar 2-3 dias  
**ETA resolução**: 2026-08-05

---

### BLOCKER 4: MN Approval — Gate de Produção

**Status**: 🔐 REQUERIDO (gate)  
**Achado**: CLAUDE.md v4.2 deploy checklist, item: `[ ] Gate humano: aprovação MN antes de merge`

#### Contexto
O próprio documento master do repositório exige aprovação MN explícita antes de:
- Carregar dados em `manta-maestro` (DB de produção)
- Fazer merge de Fase 1 para main
- Aprovar Fase 2

#### Decisão Necessária
Você, como MN (mneves@mantaassociados.com), precisa:

1. ✅ Revisar este documento
2. ✅ Decidir blocker #1 (schema)
3. ✅ Decidir blocker #2 (embeddings)
4. ✅ Aprovar blocker #3 (network — upload manual)
5. ✅ Assinar aprovação para carga em produção

---

## 📅 Timeline Revisado

```
2026-08-03 (Hoje):
├─ ✅ Diagnóstico concluído
├─ ✅ 5 SKILL.md gerados
├─ 📝 Comunicação a MN (ESTE DOCUMENTO)
└─ 📞 Aguardando aprovação

2026-08-04 (D+1):
├─ MN: Rever + decidir blockers
├─ DevOps: Começar implementação (após decisão)
└─ Manta 06: Coletar PDFs

2026-08-05 (D+2):
├─ Schema + Embeddings: ~50% implementados
├─ PDFs: ~80% coletados
└─ Semana 2 (SharePoint): Continua em paralelo

2026-08-06 — 2026-08-10 (D+3 a D+7):
├─ Infraestrutura: 100% pronta
├─ PDFs: 100% carregados em SharePoint
├─ Semana 1 (RAG): INICIA (5 agentes, ~2-3 dias)
└─ Semana 2: Finaliza (SharePoint + validação)

2026-08-11 — 2026-08-14 (D+8 a D+11):
├─ Semana 3: Routing tests + gate Fase 2
└─ MN: Aprovação Fase 2

GATE Fase 2: ~2026-08-14
```

---

## ✅ O que está PRONTO (Não bloqueado)

- ✅ **SKILL.md para 5 agentes** (S6-S10) — 44.6 KB de documentação pronta
- ✅ **MCP config** (.mcp.json + settings.json) — integração especificada
- ✅ **SharePoint structure** — definida, pronta para upload
- ✅ **Validation hooks** — pre-commit hook criado e testado
- ✅ **Semana 2 & 3** — podem prosseguir independente de Semana 1

---

## 🎯 Ações Necessárias de Você (MN)

**HOJE (2026-08-03):**

1. **Rever esta comunicação** (20 min)
2. **Decidir Blocker #1** — Qual schema usar?
   - [ ] Opção A: `manta_rag_chunks` (recomendado)
   - [ ] Opção B: Migrar `rag_chunks` com DDL
   - [ ] Outra (especifique)

3. **Decidir Blocker #2** — Como gerar embeddings?
   - [ ] Opção A: Claude Embeddings API (recomendado)
   - [ ] Opção B: Supabase Edge Function
   - [ ] Opção C: OpenAI/Cohere API
   - [ ] Outra (especifique)

4. **Aprovar Blocker #3** — Network access via upload manual
   - [ ] Aprovado — Manta 06 começa coleta PDFs
   - [ ] Alternativa — Especifique (VPN/proxy/mirrors)

5. **Assinar Gate de Produção**
   - [ ] Aprovado para carregar dados em `manta-maestro`
   - [ ] Aprovado para merge Fase 1 em main
   - [ ] Aprovado para gate Fase 2 (quando chegar lá)

6. **Responder** (email ou comentário no PR #53)

**PRAZO**: Hoje ou amanhã (2026-08-04 09:00) para não atrasar timeline.

---

## 📊 Impacto de Decisões

| Decisão | Timeline | Custo | Risco |
|---------|----------|-------|-------|
| Schema + Embeddings hoje | -2-3 dias | Médio | Baixo |
| Schema + Embeddings amanhã | -1 dia | Médio | Baixo |
| Schema + Embeddings segunda | +1-2 dias | Médio | Médio |
| Sem decisão (inércia) | +5+ dias | Alto | Alto |

**Recomendação**: Decidir HOJE para não atrasar Fase 1.

---

## 📎 Referências

| Documento | Localização | Status |
|-----------|-------------|--------|
| FASE1-STATUS.md | Repo (root) | ✅ Atualizado |
| INFRAESTRUTURA-BLOCKERS-SUMARIO.md | Repo (root) | ✅ Detalhado |
| CLAUDE.md (v4.2) | Repo (root) | ✅ Aprovado antes |
| PR #53 | GitHub | 🟡 Aguardando aprovação |
| Workflow results | Transcript | ✅ Completo |

---

## 🔗 Links Úteis

- **PR #53**: https://github.com/MN1970/Codex-exemplo/pull/53
- **Status Tracker**: FASE1-STATUS.md (este repo)
- **Blocker Summary**: INFRAESTRUTURA-BLOCKERS-SUMARIO.md (este repo)

---

## 📞 Próximos Passos (Após Sua Resposta)

**Se aprovação recebida hoje:**
1. DevOps/Manta 16 começam implementação (amanhã)
2. Manta 06 coleta PDFs (amanhã)
3. Semana 1 RAG inicia 2026-08-06
4. Fase 1 gate ~2026-08-14

**Se sem resposta até 2026-08-04 18:00:**
1. Execução pausa (em risco)
2. Timeline estende +3-5 dias
3. Fase 2 gate muda para ~2026-08-21

---

**Aguardando sua decisão.**

---

**Preparado por:** Claude Code Automation  
**Data**: 2026-08-03  
**Session**: https://claude.ai/code/session_0148au6EaXyhEPTCG4XzNueb

---
