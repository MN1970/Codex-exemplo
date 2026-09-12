# ADR D1–D4 — Decisões arquiteturais pendentes do Manta Maestro

- **Status**: **aprovado por MN (2026-09-13)** — implementação em
  andamento, corrigida contra o código real do repositório (ver
  "Correção de diagnóstico 2026-09-13" abaixo)
- **Data**: 2026-09-08 (diagnóstico original) / 2026-09-13 (correção)
- **Autor**: Manta 16 (arquiteto-ia), via sessão Claude Code
- **Referências**: `CLAUDE.md` (registro mestre v5.4.7),
  `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md` (v2.0.0),
  `docs/COWORK-INTEGRATION.md`, `docs/DEPLOY-v4.2.md`

Este documento resolve as 4 pendências arquiteturais citadas no status do
Portal (`portal-manta-maestro`): **D1 multi-tenancy**, **D2 versionamento
de agentes**, **D3 fallback de modelo**, **D4 retenção de logs**. Segue o
workflow de revisão de 4 etapas da skill `manta-arquiteto-ia`: diagnóstico
→ propostas → implementação (patch de referência) → registro (gate
humano).

## ⚠️ Correção de diagnóstico — 2026-09-13

O diagnóstico original (2026-09-08, seções abaixo) foi escrito **sem
checar o código real** de `src/maestro/`, `infra/agent-registry/`,
`scripts/` e `supabase/migrations/` — um repositório muito maior do que
o `CLAUDE.md` documentava até então. Uma reconciliação com 4 sessões
paralelas (read-only) encontrou que boa parte das premissas de "nada
disso existe" estava **desatualizada ou errada**. Resumo (ver PR de
implementação para o detalhe completo por arquivo):

- **D1**: falso que "nenhuma política RLS está documentada" — já
  existem 13 policies reais, isolando por `agent_id`/`user_id` (nunca
  por tenant). Achado novo e mais urgente: `rag_chunks` tem **duas
  definições de schema conflitantes** no repo
  (`2026_07_27_barragens_rag_chunks.sql` vs.
  `2026_08_02_rag_hierarchy_v5.sql`), e a produção real audita para
  `manta_rag_chunks`/`manta_rag_documents`, nomes diferentes dos usados
  nas migrações deste repo. A migração de tenant precisa resolver isso
  antes de assumir um schema único. `aysa`/`regis-dd` seguem como
  tenants **propostos**, sem lastro em código — não tratar como já
  confirmados.
- **D2**: falso que nenhum agente tem campo de versão — 7 dos 17
  agentes registrados já têm `version:` (semver) no frontmatter, e o
  schema Supabase já tem `agents.version` + `agent_registry_history`
  (audit genérico). O gap real é **inconsistência** (10/17 sem o
  campo, uma ordem de frontmatter divergente em
  `agente-saneamento.md`) e a ausência de `source_of_truth`/
  `last_sync_sp` (esses sim não existem em lugar nenhum) — não criar
  tabela `agent_versions` nova, reaproveitar o que já existe.
- **D3**: existe um protótipo `scripts/fallback_strategy.py` com
  auto-escalonamento para Opus (cadeia de Markov, estado
  `OPUS_ESCALATION`) — mas ele (a) atua sobre segmento vertical, não
  sobre os 4 agentes horizontais alvo do D3; (b) é treinado só com
  dados sintéticos; (c) está desconectado do `orchestrator.py`; (d) faz
  o **oposto** do D3 (escala para Opus automaticamente, sem gate
  humano). Não reaproveitar sem revisão. Também: `agente-modelagem.md`
  usa `model: sonnet` no frontmatter real, não `opus` como a v0 deste
  ADR assumia — a lista de agentes "sem fallback automático para Opus"
  precisa ser conferida contra o frontmatter real de cada agente, não
  assumida.
- **D4**: existe sistema real de retenção para `agent_memory`
  (`scripts/agent_memory_cleanup.py`, SQL real via `psycopg2`,
  migrações de tiering com `purge_cold_tier()`), mas o job
  "agendado" oficial (`scripts/agent_memory_purge.py` +
  `agent_memory_purge_job.py`, chamado por `apscheduler_setup.py`) é
  **mockado** — nunca executa DELETE real contra o Supabase
  (`# Real execution would go here`). Routing/RAG/claims/advisory/
  artefato/Cowork **não têm nenhuma tabela de retenção hoje** — esses
  sim precisam ser desenhados do zero, estendendo o padrão já real de
  `agent_memory_cleanup.py` em vez de duplicá-lo.

**Gate humano**: aprovado por MN para prosseguir com a implementação
corrigida acima (não com o diagnóstico original de "nada existe").
Pontos que ainda dependem de confirmação humana específica ficam
marcados como TODO/comentário no código, não bloqueiam a implementação
do que é seguro e não-destrutivo (novas colunas com default, novo
módulo isolado, nova tabela) — mudanças que alterariam dado existente
(ex.: escolher entre as 2 definições conflitantes de `rag_chunks`,
incluir `agente-modelagem` na lista de no-fallback-Opus) permanecem
sinalizadas para decisão MN antes de aplicar em produção real.

---

Nenhuma mudança deste ADR é aplicada diretamente em produção Supabase —
o que segue é o diagnóstico original (2026-09-08) mantido como
histórico; a implementação real segue a correção acima.

---

## D1 — Multi-tenancy

### Diagnóstico

- Hoje o hub MCP compartilha o mesmo `user_id` para todos os workspaces
  Cowork (`docs/COWORK-INTEGRATION.md`, seção 4: "hoje o hub compartilha
  o mesmo `user_id` para todos"). Sem isolamento de tenant.
- O projeto Supabase de produção (`ogxxgvgtulrbbppshjie`) tem 1 schema
  único de `rag_chunks`/`rag_collections` para todos os segmentos —
  nenhuma coluna de tenant.
- Há pelo menos 2 casos que exigem separação de dados por cliente:
  AySA (Argentina, saneamento — dados sensíveis de outro país) e
  processos de M&A/DD (ex. Régis Bittencourt — dados de terceiros sob
  NDA).
- Nenhuma política RLS (Row Level Security) está documentada.

### Proposta

**Não criar projeto Supabase separado por cliente.** Custo operacional
alto (migração duplicada, sync de schema, sem ganho real hoje). Em vez
disso:

1. Adicionar coluna `tenant_id TEXT NOT NULL DEFAULT 'manta-interno'` em
   `rag_chunks`, `rag_collections` e `sp_agent_routing`.
2. Ativar RLS em todas as tabelas com política:
   ```sql
   CREATE POLICY tenant_isolation ON rag_chunks
     USING (tenant_id = current_setting('request.jwt.claims', true)::json->>'tenant_id');
   ```
3. Tenants previstos no lançamento: `manta-interno` (default, todos os
   20 agentes), `aysa` (saneamento Argentina, isolado), `regis-dd`
   (due diligence Régis Bittencourt, isolado e com expiração — ver D4).
4. Maestro (Manta 00) resolve `tenant_id` a partir do contexto de sessão
   (workspace Cowork ou claim do JWT via custom connector) e o propaga
   para toda consulta RAG e toda gravação de log.
5. SharePoint: manter site único `sites/Engenharia`, mas isolar por
   permissão de pasta nativa do M365 (já existe) em vez de multi-site —
   o MCP M365 é read-only hoje, então isolamento por ACL do SharePoint
   é suficiente e não exige mudança de infraestrutura.

**Critério para reabrir esta decisão**: se surgir um 3º cliente externo
com exigência contratual de isolamento físico de banco (ex. cláusula de
residência de dados), reavaliar projeto Supabase dedicado.

### Gate humano

- [ ] Aprovar `tenant_id` como padrão obrigatório em toda tabela nova.
- [ ] Aprovar lista inicial de tenants (`manta-interno`, `aysa`, `regis-dd`).
- [ ] Confirmar se AySA exige residência de dados fora do projeto
  Supabase atual (verificar contrato/DPA).

---

## D2 — Versionamento de agentes

### Diagnóstico

- `CLAUDE.md` tem versionamento global (v4.1 → v4.2 → v4.2.1), mas os
  arquivos individuais em `.claude/agents/*.md` e os `SKILL.md` em
  `sharepoint/01-agentes-fundamentais/` não têm campo de versão próprio.
- Não há como saber, olhando só `agente-saneamento.md`, se ele está
  sincronizado com a versão publicada no SharePoint (`docs/COWORK-
  INTEGRATION.md` já registra esse gap: "Sync automático `.claude/
  agents/*.md` ↔ SharePoint SKILL.md — hoje manual").
- Sem versão por agente, um handoff do Maestro pode invocar um agente
  desatualizado sem aviso.

### Proposta

1. Adicionar frontmatter YAML de versão em todo agente e SKILL.md:
   ```yaml
   ---
   name: agente-saneamento
   version: 1.0.0
   source_of_truth: MN1970/Codex-exemplo@.claude/agents/agente-saneamento.md
   last_sync_sp: 2026-07-05
   ---
   ```
2. Versionamento semântico por agente:
   - **MAJOR**: mudança de escopo/segmento ou remoção de handoff.
   - **MINOR**: nova disciplina, novo handoff, nova fonte RAG.
   - **PATCH**: correção de texto, ajuste de keyword de routing.
3. Tabela `agent_versions` (Supabase, tenant `manta-interno`) com
   `agent_slug, version, git_sha, sp_last_sync, status`. Populada por
   CI no merge de PR que altera `.claude/agents/*.md` (mesmo padrão de
   fila-pendente do PK_08: git é a fonte, SharePoint é publicação,
   nunca o inverso).
4. `docs/DEPLOY-v4.2.md` e futuros runbooks passam a exigir bump de
   versão no frontmatter como item do checklist antes do gate MN.
5. Não versionar por commit SHA como única fonte — SHA fica em
   `source_of_truth` para rastreabilidade, mas o número semântico é o
   que aparece para o time.

### Gate humano

- [ ] Aprovar convenção semver + campos de frontmatter.
- [ ] Autorizar criação da tabela `agent_versions` na próxima migração.
- [ ] Definir quem faz o bump (autor do PR vs. CI automático via hook).

---

## D3 — Fallback de modelo

### Diagnóstico

- Model tiering documentado (`ARQUITETURA-AGENTES-IA.md` §5): Haiku
  (triagem) → Sonnet (execução) → Opus (complexo). Nenhuma regra de
  fallback quando um tier está indisponível (rate limit, overload,
  modelo depreciado).
- Risco concreto: se Opus estiver indisponível durante análise de claim
  (Manta 01) ou arquitetura (Manta 16), um fallback silencioso para
  Sonnet pode produzir raciocínio raso apresentado com a mesma
  confiança — inaceitável em claim/contratual.

### Proposta

Fallback assimétrico por sensibilidade do agente, nunca silencioso:

| Tier solicitado | Fallback permitido | Ação obrigatória |
|---|---|---|
| Haiku (triagem/routing) | Sonnet | Log informativo, sem aviso ao usuário |
| Sonnet (execução geral) | Haiku (degradado) ou fila de retry | Banner na resposta: "modelo reduzido por indisponibilidade — revisar antes de usar" |
| Opus (Manta 01 claims, Manta 16 arquiteto, Manta 06 modelagem complexa, Manta 15 advisory crítico) | **Nenhum fallback automático** | Retry com backoff (3x); se persistir, resposta explícita "aguardando Opus — não gerar com tier inferior" + notificação humana. Usuário decide se aceita degradar. |

Regras adicionais:
1. Nunca fazer upgrade automático de tier (ex. Haiku falhando escalar
   sozinho para Opus) — custo sobe sem aprovação.
2. Todo evento de fallback é logado (ver D4) com `agent_slug,
   tier_requested, tier_used, reason, session_id`.
3. Maestro expõe o tier efetivamente usado na resposta (mesmo padrão de
   `last_served_model` já usado no monitoramento de sessões Claude Code
   Remote) para auditabilidade.

### Gate humano

- [ ] Confirmar lista de agentes "sem fallback automático" (proposta:
  Manta 01, 06, 15, 16 — os 4 que já usam Opus por padrão ou sob
  demanda).
- [ ] Aprovar número de retries e backoff (proposta: 3x, 2s/4s/8s).

---

## D4 — Retenção de logs

### Diagnóstico

- O workflow de revisão da skill `manta-arquiteto-ia` (Etapa 4) já
  assume "reversível em 30 dias" para logs de revisão de artefato, mas
  isso nunca foi generalizado para logs de routing, RAG e decisões de
  agente.
- Sem política de retenção, dois riscos: (a) custo de storage crescendo
  sem limite; (b) para clientes como AySA, ausência de retenção mínima
  pode violar exigência regulatória de rastreabilidade.

### Proposta

Retenção em camadas, por tipo de log — todas gravadas com `tenant_id`
(D1) para permitir purga seletiva por cliente:

| Tipo de log | Retenção | Justificativa |
|---|---|---|
| Routing (Maestro → agente, scores) | 90 dias | Suficiente para debug de routing; sem valor regulatório |
| Consulta RAG (query + chunks retornados) | 180 dias | Auditoria de qualidade de resposta técnica |
| Fallback de modelo (D3) | 180 dias | Auditoria de custo/degradação |
| Decisão de claim/contratual/advisory (Manta 01/02/15) | Indefinida (sem purga automática) | Rastreabilidade jurídica — mesma lógica de laudo técnico, nunca se apaga sozinho |
| Revisão de artefato (Etapa 4 do arquiteto) | 30 dias reversível, depois arquivado indefinidamente | Já é o padrão declarado na skill |
| Logs Cowork / task run | 30 dias | Operacional, sem valor de auditoria após execução confirmada |

Execução:
1. Purga via job agendado (APScheduler/cron determinístico — nunca LLM
   decidindo o que apagar, conforme anti-padrão da skill).
2. Purga é soft-delete (`deleted_at`) por 30 dias adicionais antes de
   hard-delete, para permitir recuperação em caso de erro do job.
3. Tenant `aysa`: antes de aplicar a tabela acima, confirmar com jurídico
   se há exigência de retenção mínima distinta (regulação argentina de
   saneamento/dados pessoais) — pode sobrepor os prazos gerais.

### Gate humano

- [ ] Aprovar tabela de retenção por tipo de log.
- [ ] Confirmar com jurídico a exigência específica do tenant `aysa`
  antes do primeiro job de purga rodar sobre esses dados.
- [ ] Autorizar criação do job de purga (owner: quem mantém o Supabase
  de produção).

---

## Resumo — próximos passos

1. MN revisa e aprova/ajusta as 4 propostas acima (gate humano).
2. Após aprovação, abrir migração Supabase incremental (`tenant_id` +
   `agent_versions` + colunas de retenção) como PR separado neste repo,
   seguindo o padrão de `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`.
3. Atualizar `ARQUITETURA-AGENTES-IA.md` com nova seção "Multi-tenancy,
   versionamento e retenção" após aprovação (bump v2.0.0 → v2.1.0).
4. Registrar decisão final no `CLAUDE.md` (seção de histórico de
   versões) apontando para este ADR.
