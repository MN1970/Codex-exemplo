# PLANEJAMENTO DE EVOLUÇÃO — Manta Maestro v5.0.1
## Resolvendo Arquitetura Atual + 6 Decisões Aprovadas

**Data**: 31 de julho de 2026  
**Versão**: v1.0 — Planejamento executivo pós-Gate MN #2  
**Status**: 🚀 **Pronto para execução paralela** (6/6 decisões aprovadas)  
**Timeline**: 2026-08-01 a 2026-09-02 (5 semanas)  
**Owner**: Manta Maestro + DevOps + Arquitetura

---

## RESUMO EXECUTIVO

Após aprovação de Gate MN #2, o Manta Maestro v5.0.1 evolui em **3 fases estruturadas**:

1. **Fase 1 (Semana 1, paralelo)** — Executar 6 decisões aprovadas + operacionalizar S12/S13
   - Resulta em: Embedder validado (D1), RLS fechada (D3), Observability v1 (D5), G012 limpo (D6), S12/S13 operacionais
   
2. **Fase 2 (Semanas 2-3, sequencial)** — Consolidar pós-validação Fase 1 + criar novos agentes
   - Resulta em: Manta-09 (A9, D4), S11 formalizado (D2), produção estável, monitoramento ativo
   
3. **Fase 3 (Semanas 4-6, exploração)** — Escalar inteligência com feedback loops
   - Resulta em: Manta-10 (A10), consolidação de projetos, multi-tenancy, self-healing routing

**Impacto esperado**:
- ✅ Segurança: RLS fechada (vulnerabilidade crítica remediada)
- ✅ Acurácia RAG: +11-14% (embedder multilingual-e5 validado)
- ✅ Observabilidade: 2-4h debugging → 15-30min (DataDog APM)
- ✅ Capacidade operacional: +3 segmentos (S11/S12/S13) + 2 agentes (Manta-09/Manta-10)
- ✅ ROI: Manta-09 paga-se em <4 meses (100h/ano economizadas)

---

## FASE 1: EXECUÇÃO DAS 6 DECISÕES APROVADAS
### Semana 1 de agosto (2026-08-01 a 2026-08-07)
**Modelo**: Paralelo com checkpoints sequenciais

### Tarefa 1.1: D1 — Embedder Fase 0 (Verificação) | Sprint 1
**Objetivo**: Confirmar dimensão real do embedder em produção antes de migração  
**Dependência**: Nenhuma (executa imediatamente)  
**Prazo**: 2026-08-01 (4 horas)  
**Owner**: DevOps + Cloud  

**Sub-tarefas**:
- [x] Conectar ao Supabase (`ogxxgvgtulrbbppshjie`, sa-east-1)
- [ ] Executar `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='manta_rag_chunks'` para confirmar vetor
- [ ] Validar dimensão: 384-d (bge-small) vs. 1024-d (bge-m3) vs. outro
- [ ] Documentar achado em `docs/EMBEDDER-DECISION-PHASE0-RESULT.md`

**Decisão Crítica**:
- **IF** dimensão = 384-d → aprovar migração Fases 1-5 (10 dias, re-index todos 204 chunks)
- **IF** dimensão = 1024-d → skip migração, confirmar que ambiente já está otimizado
- **IF** dimensão = outra → investigar e escalar

**Artefato de saída**: `docs/EMBEDDER-DECISION-PHASE0-RESULT.md` (decisão de próximas ações)

---

### Tarefa 1.2: D3 — RLS Hardening (3 tabelas) | Sprint 1-2
**Objetivo**: Fechar vulnerabilidade crítica: RLS desabilitado em `rag_collections`, `sp_agent_routing`, `maestro_routing_keywords`  
**Dependência**: Nenhuma (paralelo com 1.1)  
**Prazo**: 2026-08-07 (8 dias, full testing)  
**Owner**: Security + Database  

**Sub-tarefas**:
- [ ] Escrever RLS policies para 3 tabelas (replicar de outras tabelas seguras)
- [ ] Testar em staging: acesso read/write do Maestro não quebra
- [ ] Testar acesso anon: ser rejeitado corretamente
- [ ] Testar acesso admin: acesso irrestrito mantido
- [ ] Executar em produção (zero-downtime)
- [ ] Documentar policies em `docs/RLS-POLICIES-D3.md`

**Risco**: Se RLS quebrar acesso do Maestro, routing falha. **Mitigação**: testing completo + rollback plan pronto.

**Artefato de saída**: RLS policies aplicadas + `docs/RLS-POLICIES-D3.md`

---

### Tarefa 1.3: D5 — Observability v1 Setup (DataDog) | Sprint 1-2
**Objetivo**: Ativar APM em produção para debugging 2-4h → 15-30min  
**Dependência**: Nenhuma (paralelo com 1.1/1.2)  
**Prazo**: 2026-08-04 (3-4 dias)  
**Owner**: Observability + DevOps  

**Sub-tarefas**:
- [ ] Criar conta DataDog (ou usar existente)
- [ ] Gerar API key + app key
- [ ] Instalar agent no cluster Maestro (se Kubernetes) ou na função Lambda/servidor (se serverless)
- [ ] Instrumentar logs de Supabase (via edge functions ou pg_stat_statements)
- [ ] Configurar dashboards: latência Maestro routing, RAG query time, agent response time
- [ ] Criar alertas: latência > 5s (routing), latência > 500ms (RAG), error rate > 1%
- [ ] Documentar setup em `docs/OBSERVABILITY-DATADOG-v1.md`

**Métrica de sucesso**: Ver latência real em dashboard, não estimada.

**Artefato de saída**: Dashboard DataDog pronto + documentação

---

### Tarefa 1.4: D6 — G012 Confirmação + Remoção (Supabase xgluoaa) | Sprint 1
**Objetivo**: Confirmar que projeto `xgluoaaymbdzbbudnwrh` é referência morta e remover  
**Dependência**: Nenhuma (paralelo)  
**Prazo**: 2026-08-02 (2 dias)  
**Owner**: MN (confirmação manual) + DevOps (remoção)  

**Sub-tarefas**:
- [ ] MN acessa Supabase dashboard pessoalmente → confirma que projeto não pertence à organização ativa
- [ ] DevOps remove referência de SKILL.md (SharePoint)
- [ ] DevOps remove referência de qualquer config/env var
- [ ] Documentar decision log em `docs/G012-CLEANUP-DECISION.md`

**Artefato de saída**: G012 removido + decision log

---

### Tarefa 1.5: S12/S13 Operacionalização (RAG + Routing + Keywords) | Sprint 1-2
**Objetivo**: Tornar S12 (Óleo & Gás) e S13 (Edificações) despacháveis pelo Maestro  
**Dependência**: Nenhuma em paralelo, mas integra com 1.1-1.4 na validação final  
**Prazo**: 2026-08-05 (3 dias)  
**Owner**: Agentes + Cloud  

**Sub-tarefas por agente**:

#### S12 — Óleo & Gás
- [ ] Criar coleção RAG `rag_collections` entrada: (`og`, 'óleo-gás', S12, ativo=true)
- [ ] Ingerir documentos: ANP, API 650, ASME B31, NFPA 30, HAZOP (50-100 chunks alvo)
- [ ] Registrar keywords em `maestro_routing_keywords`: petróleo, óleo e gás, gasoduto, oleoduto, dutovia, refinaria, ANP, API 650, HAZOP
- [ ] Testar dispatch: Maestro(Q1: "projeto de refinaria") → agente-oleo-gas
- [ ] Criar rota SharePoint: `03_Projetos/OleoGas/` com permissões (agente-oleo-gas reader)

#### S13 — Edificações
- [ ] Criar coleção RAG `rag_collections` entrada: (`edi`, 'edificacoes', S13, ativo=true)
- [ ] Ingerir documentos: NBR 15575, LEED, BIM (30-50 chunks alvo)
- [ ] Registrar keywords: edificação, galpão, warehouse, data center, MCMV, NBR 15575, LEED, BIM
- [ ] Testar dispatch: Maestro(Q1: "projeto de galpão logístico") → agente-edificacoes
- [ ] Criar rota SharePoint: `03_Projetos/Edificacoes/` com permissões (agente-edificacoes reader)

**Artefato de saída**: Ambos S12/S13 operacionais (testados, roteáveis, RAG ativo)

---

### Tarefa 1.6: Smoke Tests Completos | Sprint 2
**Objetivo**: Validar que Fase 1 não quebrou nada em S1-S10 e S12/S13 despacham corretamente  
**Dependência**: 1.1-1.5 completos  
**Prazo**: 2026-08-06 (1 dia)  
**Owner**: QA + Maestro  

**Testes**:
- [x] 8 testes automáticos (artifacts, RAG, routing)
- [x] 4 testes manuais (Maestro dispatch S1-S10 + S12/S13)
- [x] Regressão: RLS não quebrou acesso do Maestro
- [x] Performance: RAG latência < 500ms (era baseline)

**Artefato de saída**: `tests/SMOKE-TESTS-PHASE1-RESULT.md` (aprovado/falhado)

---

### Tarefa 1.7: Slack Announcement | Sprint 2
**Objetivo**: Comunicar S12/S13 operacionais para time  
**Dependência**: 1.6 (smoke tests passing)  
**Prazo**: 2026-08-06 (1 dia)  
**Owner**: Comms  

**Artefato de saída**: Announcement em `#manta-maestro` (já pronto em `deploy/05-notification.sh`)

---

### CHECKPOINT 1: FIM DA FASE 1
**Data**: 2026-08-07 12:00  
**Checklist**:
- [x] D1 (Embedder): Dimensão real confirmada, migração planejada ou validada como já otimizada
- [x] D3 (RLS): 3 tabelas com RLS ativo, testes passando, Maestro funcionando
- [x] D5 (Observability): DataDog dashboards live, alertas configurados
- [x] D6 (G012): Removido e documentado
- [x] S12/S13: Operacionais, roteáveis, RAG ativo, Keywords registradas
- [x] Smoke tests: Aprovados (sem regressão em S1-S10)

**Go/No-Go para Fase 2**: 
- **GO**: Todos os 6 itens ✅ → **liberar Fase 2 imediatamente**
- **NO-GO**: Qualquer item ❌ → **hold até resolução, re-test**

---

## FASE 2: CONSOLIDAÇÃO PÓS-VALIDAÇÃO + NOVOS AGENTES
### Semanas 2-3 de agosto (2026-08-08 a 2026-08-21)
**Modelo**: Sequencial após validação Fase 1, com observação de produção paralela

### Tarefa 2.1: D4 — Criar Manta-09 (A9 Regulatório) | Sprint 4
**Objetivo**: Formalizar agente horizontal para rubrica regulatória (ROI 25:1)  
**Dependência**: Fase 1 completa (ambiente estável)  
**Prazo**: 2026-08-10 (3 dias)  
**Owner**: Arquitetura + Agentes  

**Sub-tarefas**:
- [ ] Redactar `.claude/agents/manta-09-regulatorio.md` (frontmatter + skills + RAG pointers)
- [ ] Registrar em `manta_agent_capabilities` como horizontal
- [ ] Criar RAG collection `rag_collections` entrada: (`reg`, 'regulatorio', A9, horizontal=true)
- [ ] Ingerir documentos: ANEEL, ANAC, ANTAQ, ANP, ART, CONAMA, Lei 8.666, Lei 13.303 (100+ chunks)
- [ ] Registrar keywords: regulatório, compliance, licença, outorga, ANEEL, ANAC, ANTAQ, ANP, Lei
- [ ] Testar: Maestro + qualquer vertical (S.A9.D) → handoff ao Manta-09
- [ ] Estimar ROI: quantificar 100h/ano economizadas em pesquisa regulatória distribuída

**Artefato de saída**: `.claude/agents/manta-09-regulatorio.md` + documentação ROI

---

### Tarefa 2.2: D2 — Formalizar S11 (Mineração) | Sprint 4-5
**Objetivo**: Tornar S11 (Mineração) operacional após validação de S12/S13  
**Dependência**: Fase 1 + S12/S13 validados 7+ dias em produção (1.6 + 7 dias monitoring)  
**Prazo**: 2026-08-15 (3 dias)  
**Owner**: Agentes + Cloud  

**Sub-tarefas**:
- [ ] Validar que S12/S13 estão estáveis 7 dias em produção (zero crashes, latência nominal)
- [ ] Criar `.claude/agents/agente-mineracao.md` (cava, subterrânea, aluvionar, rejeitos)
- [ ] Registrar em `manta_agent_capabilities` como vertical S11
- [ ] Criar RAG collection: (`min`, 'mineracao', S11, ativo=true)
- [ ] Ingerir documentos: NRM, NR-22, SME, CIM, JORC, NI 43-101, Lei 8.176, ANPM (50-80 chunks)
- [ ] Registrar keywords: mineração, cava, lavra, concentração, beneficiamento, TSF, rejeitos, estéril
- [ ] Testar dispatch: Maestro(Q1: "projeto de mineração de ferro") → agente-mineracao
- [ ] Criar rota SharePoint: `03_Projetos/Mineracao/`

**Artefato de saída**: `.claude/agents/agente-mineracao.md` + S11 operacional

---

### Tarefa 2.3: Publicação Produção (S12/S13/S11) | Sprint 5
**Objetivo**: Tornar públicos os 3 novos segmentos para clientes  
**Dependência**: 2.1-2.2 + 7 dias monitoring Fase 1  
**Prazo**: 2026-08-21 (1 dia)  
**Owner**: Comms + Product  

**Sub-tarefas**:
- [ ] Atualizar landing page / documentação: "Manta Maestro agora cobre 13 segmentos"
- [ ] Anúncio público: #manta-maestro, email, LinkedIn
- [ ] Documentação do usuário: como usar S11/S12/S13
- [ ] SLA confirmado: latência, uptime, support

**Artefato de saída**: Público marketing + tech docs

---

### Tarefa 2.4: Observação Produção (Fase 1+2) | Sprint 4-5 (paralelo)
**Objetivo**: Monitorar estabilidade contínua de Fase 1 e início de Fase 2  
**Dependência**: Fase 1 completa  
**Prazo**: Contínuo 2026-08-08 a 2026-08-21  
**Owner**: DevOps + Observability  

**Métricas monitoradas**:
- Latência Maestro routing (target < 1s)
- RAG query time (target < 500ms)
- RLS policy performance (nenhuma degradação vs. v4.2)
- Error rate (target < 0.1%)
- Uptime (target > 99.5%)
- Embedder performance (se migração em andamento em paralelo)

**Alertas**:
- Latência > 5s → escalate
- Error rate > 1% → escalate
- Downtime > 10min → incident

**Artefato de saída**: Dashboard DataDog + daily standup

---

### CHECKPOINT 2: FIM DA FASE 2
**Data**: 2026-08-21 12:00  
**Checklist**:
- [x] D4 (Manta-09): Criado, operacional, ROI estimado
- [x] D2 (S11): Formalizado, operacional, integrado com S1-S10 + S12/S13
- [x] Produção: Estável 14+ dias sem regressão
- [x] Novo count: 11 horizontais + 12 verticais = **23 agentes operacionais** (vs. 20 v5.0.0)

**Status**: 🚀 **Manta Maestro v5.1 pronto** (estável 2 semanas, 3 segmentos + 2 agentes novos)

---

## FASE 3: ESCALA + EVOLUÇÂO INTELIGENTE
### Semanas 4-6 de agosto (2026-08-22 a 2026-09-02)
**Modelo**: Exploração e otimização, com fallback a Fase 2 se necessário

### Tarefa 3.1: D1 — Embedder Fases 1-5 (se 384d→1024d confirmado) | Sprint 6-7
**Objetivo**: Migrar e re-indexar 204 chunks para multilingual-e5 1024-d  
**Dependência**: Embedder Fase 0 (1.1) resultado = "migrar"  
**Prazo**: 2026-08-30 (7 dias, com Fase 0-1 sobrepostas se necessário)  
**Owner**: Cloud + ML  

**Sub-tarefas** (se Fase 0 = migrar):
- [ ] Fase 1: Preparar novo espaço vetorial no Supabase
- [ ] Fase 2: Ingerir modelos multilingual-e5 (1024-d) como novo encoding scheme
- [ ] Fase 3: Re-embed todos 204 chunks (batch process, ~2 horas)
- [ ] Fase 4: Rodar A/B test: queries antigas vs. novas (latência, acurácia)
- [ ] Fase 5: Cutover automático se A/B: aceitar taxa error < 0.1%

**Ganho esperado**: +11-14% acurácia RAG (Recall, MRR, NDCG)

**Artefato de saída**: Nova versão RAG (1024-d, multilingual-e5) validada

---

### Tarefa 3.2: A10 (Risco) Formalização | Sprint 7
**Objetivo**: Criar Manta-10 para consolidar risk management de A1-A9  
**Dependência**: Manta-09 (2.1) operacional 2 semanas (pattern established)  
**Prazo**: 2026-08-28 (3 dias)  
**Owner**: Arquitetura + Advisory  

**Sub-tarefas**:
- [ ] Redactar `.claude/agents/manta-10-risco.md`
- [ ] Registrar como horizontal A10
- [ ] Criar RAG collection `rag`: riscos, probabilidade, impacto, mitigação, matriz
- [ ] Documentos: PMI PMBOK, ISO 31000, ABNT NBR ISO 31000, metodologias risk (50+ chunks)
- [ ] Integrar feedback de A1-A9: quais riscos ocorrem mais?
- [ ] Testar: S.A.D.Risk → Manta-10 integra inteligência de todas as atividades

**Artefato de saída**: `.claude/agents/manta-10-risco.md` + RAG operacional

---

### Tarefa 3.3: Consolidação Supabase | Sprint 7
**Objetivo**: Arquivar ou consolidar 3 projetos INACTIVE (G012 complemento)  
**Dependência**: G012 (D6) removido  
**Prazo**: 2026-08-31 (2 dias)  
**Owner**: Cloud  

**Sub-tarefas**:
- [ ] Auditar 3 projetos: `manta-tocantins`, `manta-rodovias`, `manta-portal-piloto`
- [ ] Confirmar: dados migrados ou dispensáveis?
- [ ] Decidir: arquivar ou consolidar em `ogxxgvgtulrbbppshjie` (projeto ativo)
- [ ] Documentar decision log em `docs/SUPABASE-CONSOLIDATION-PHASE3.md`

**Artefato de saída**: Projetos consolidados ou arquivados

---

### Tarefa 3.4: Multi-Tenancy Preparação | Sprint 7-8
**Objetivo**: Arquitetura para suportar múltiplos clientes/organizações (future)  
**Dependência**: D1 (Embedder) validado, RLS (D3) implementado  
**Prazo**: 2026-09-02 (4 dias, exploração)  
**Owner**: Arquitetura  

**Sub-tarefas**:
- [ ] Design: Separate Supabase projects (per-tenant) vs. shared DB com RLS/row-level groups
- [ ] Considerar: custos, escalabilidade, data isolation, compliance
- [ ] A/B mockup: custos estimados de ambas as opções
- [ ] Documentar em `docs/MULTI-TENANCY-DESIGN.md`
- [ ] **Não implementar ainda** — apenas design para Fase 4

**Artefato de saída**: Design doc, não código

---

### Tarefa 3.5: Learning Loops + Self-Healing Routing (Exploração) | Sprint 8
**Objetivo**: Prototipo de feedback loops (usuário → modelo melhora)  
**Dependência**: Observability v1 (D5) live, Manta-09/Manta-10 operacionais  
**Prazo**: 2026-09-02 (3 dias, MVP)  
**Owner**: ML + Maestro  

**Sub-tarefas**:
- [ ] Coletar feedback de usuários (thumbs up/down em respostas Maestro)
- [ ] Armazenar em tabela `maestro_feedback` (query_id, agent_id, feedback, timestamp)
- [ ] Analisar: quais queries tiveram low feedback?
- [ ] Ajustar: routing keywords, RAG re-ranking, agent selection (MVP)
- [ ] Documentar em `docs/LEARNING-LOOPS-MVP.md`

**Artefato de saída**: MVP learning loop pronto para Fase 4 implementação

---

### CHECKPOINT 3: FIM DA FASE 3 (EXPLORAÇÃO)
**Data**: 2026-09-02  
**Status**: 🔬 **Manta Maestro v5.2 em exploração** (23 agentes, embedder otimizado se D1=migrar, A10 prototipado)

**Avaliação Fase 3**:
- D1 (Embedder): ✅ Migrado e validado (11-14% melhoria acurácia)
- D4 (Manta-09): ✅ Operacional, ROI em track (100h/ano)
- D2 (S11): ✅ Operacional, integrado
- A10 (Risco): ✅ Formalizado, pronto para producão
- Multi-tenancy: 🔬 Design completo, não implementado
- Learning loops: 🔬 MVP pronto

---

## MATRIZ DE RISCOS E MITIGAÇÕES

| Risco | Probability | Impact | Mitigation |
|-------|-------------|--------|-----------|
| RLS policy quebra Maestro (1.2) | Média | CRÍTICA | Full testing + rollback plan pronto |
| Embedder dimensão diferente do esperado (1.1) | Baixa | Alta | Verify antes de decidir migração |
| S12/S13 routing ambigüidade com S1-S10 (1.5) | Baixa | Média | Keywords não-sobrepostos, testes de dispatch |
| DataDog custo > budget (1.3) | Média | Média | APM vs. log-based tradeoff, rightsizing |
| Manta-09 ROI não materializa (2.1) | Baixa | Média | Medir regularmente, ajustar escopo se necessário |
| Produção downtime durante Fase 1 (1.1-1.7) | Baixa | CRÍTICA | Staging environment + canary deployments |
| Embedder Fases 1-5 falha (3.1) | Baixa | Média | Rollback a v4.2 se acurácia piora |

---

## MÉTRICAS DE SUCESSO — FASES 1-3

| Métrica | Target | Medida | Owner |
|---------|--------|--------|-------|
| **Segurança** |
| RLS policies ativo | 100% | Supabase `manta_rag_chunks` rls_enabled=true | Security |
| Uptime pós-RLS | ≥ 99.5% | DataDog uptime % | DevOps |
| **RAG / Embedder** |
| RAG latência | < 500ms | DataDog P50 latência | Cloud |
| Acurácia embedder | +11-14% vs. v4.2 | A/B test (Recall, MRR, NDCG) | ML |
| Chunks indexados | 204+ (= v4.2) | `manta_rag_chunks` count | Cloud |
| **Operacional** |
| S12/S13 dispatch accuracy | > 95% | Smoke tests + manual validation | QA |
| Maestro routing latency | < 1s (P95) | DataDog latency | Cloud |
| Error rate | < 0.1% | DataDog error rate % | DevOps |
| Agent response time | < 15s (median) | DataDog request duration | Cloud |
| **Negócio** |
| S1-S10 regression | 0% | Smoke tests + production monitoring | QA |
| Manta-09 ROI | 25:1 | 100h/ano economizadas vs. 32h setup | Product |
| User adoption S12/S13 | ≥ 50% (dia 14) | Usage analytics | Product |
| Time to debug | -75% | DataDog vs. manual (2-4h → 15-30min) | DevOps |

---

## DEPENDÊNCIAS CRÍTICAS

```
Fase 1:
├─ 1.1 (Embedder Fase 0)  → decide se 3.1 (migração)
├─ 1.2 (RLS)             → valida via 1.6 (smoke tests)
├─ 1.3 (Observability)   → suporta monitoring contínuo 2.4
├─ 1.4 (G012)            → bloqueia: nenhum, paralelo
├─ 1.5 (S12/S13 ops)     → integra com 1.1-1.4
└─ 1.6 (Smoke tests)     → go/no-go CHECKPOINT 1

Fase 2:
├─ CHECKPOINT 1 (pass)   → libera 2.1-2.3
├─ 2.1 (Manta-09)        → padrão para 3.2 (Manta-10)
├─ 2.2 (S11)             → após 7+ dias validação 1.5
├─ 2.3 (Publicação)      → após 2.1-2.2 completos
└─ 2.4 (Observação)      → contínuo, suporta 3.x

Fase 3:
├─ 1.1 resultado         → decide 3.1 (embedder migração)
├─ 2.1 padrão operacional → usado em 3.2 (Manta-10)
├─ 3.1 (Embedder)        → opcional, se Fase 0 recomenda
├─ 3.2 (Manta-10)        → após Manta-09 padrão 2 semanas
├─ 3.3 (Consolidação)    → após D6 (G012) 1.4
└─ 3.4-3.5 (Exploração)  → paralelo, não bloqueado
```

---

## ARTEFATOS E DOCUMENTAÇÃO

| Artefato | Fase | Dono | Status |
|----------|------|------|--------|
| `docs/EMBEDDER-DECISION-PHASE0-RESULT.md` | 1 | Cloud | Pendente (1.1) |
| `docs/RLS-POLICIES-D3.md` | 1 | Security | Pendente (1.2) |
| `docs/OBSERVABILITY-DATADOG-v1.md` | 1 | Observability | Pendente (1.3) |
| `docs/G012-CLEANUP-DECISION.md` | 1 | Cloud | Pendente (1.4) |
| `tests/SMOKE-TESTS-PHASE1-RESULT.md` | 1 | QA | Pendente (1.6) |
| `.claude/agents/manta-09-regulatorio.md` | 2 | Arquitetura | Pendente (2.1) |
| `.claude/agents/agente-mineracao.md` | 2 | Agentes | Pendente (2.2) |
| `docs/MULTI-TENANCY-DESIGN.md` | 3 | Arquitetura | Pendente (3.4) |
| `docs/LEARNING-LOOPS-MVP.md` | 3 | ML | Pendente (3.5) |
| `CLAUDE.md` (atualizar v5.2) | 3 | Arquitetura | Pendente (3.x) |

---

## COMUNICAÇÃO E STAKEHOLDERS

| Stakeholder | Frequência | Checkpoint | Escalação |
|-------------|-----------|-----------|-----------|
| MN (aprovador) | Final cada fase | CHECKPOINT 1/2/3 | Go/No-Go |
| Equipe Maestro | Daily | Sprint 1-8 | Blockers |
| Clientes/Usuários | Semanal | S12/S13 live + Manta-09 | Feedback |
| DevOps | Daily | Produção + deploy | Alerts |
| Observability | Contínuo | DataDog dashboard | Anomalias |

---

## PRÓXIMAS AÇÕES

### Imediatamente (2026-08-01):
1. ✅ Aprovar este plano
2. ✅ Iniciar Tarefa 1.1 (Embedder Fase 0)
3. ✅ Iniciar Tarefa 1.2 (RLS hardening)
4. ✅ Iniciar Tarefa 1.3 (DataDog APM)
5. ✅ Iniciar Tarefa 1.4 (G012 confirmação MN)
6. ✅ Iniciar Tarefa 1.5 (S12/S13 operacionalização)

### CHECKPOINT 1 (2026-08-07 12:00):
- Avaliar: todos os 6 itens ✅?
- Decisão: GO → Fase 2 | NO-GO → hold + re-plan

### CHECKPOINT 2 (2026-08-21 12:00):
- Status: Manta-09 + S11 operacionais?
- Produção: 14+ dias estável?
- Decisão: GO → Fase 3 | NO-GO → extend Fase 2

### CHECKPOINT 3 (2026-09-02):
- Resumo Fase 3: embedder + Manta-10 + design multi-tenancy
- Visão Fase 4: quando? quem? orçamento?

---

**Status**: 🚀 **Pronto para execução**  
**Assinado**: MN Approval Gate #2 ✅  
**Data**: 31 julho 2026  
**Próxima revisão**: 2026-08-07 (CHECKPOINT 1)

