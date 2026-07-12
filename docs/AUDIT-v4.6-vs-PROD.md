# Auditoria — v4.6 (repo) vs Produção Supabase

**Data:** 2026-07-12
**Projeto Supabase:** `manta-maestro` (`ogxxgvgtulrbbppshjie`)
**Executado por:** Claude Opus 4.7 via MCP Supabase
**Contexto:** verificação **antes** de aplicar as 9 migrações candidatas do repo `Codex-exemplo/supabase/migrations/`. Objetivo: identificar conflitos com o schema já em produção e propor caminho seguro de convergência.

---

## TL;DR

- Produção tem **17 agentes** registrados (nomenclatura M02, M07, M12…, distinta dos meus S1-S13).
- **WF-AKP-001 já executou stages 1-4**: 36 teses, 52 KEs, embeddings **bge-m3 1024d** (não OpenAI 1536d como assumi).
- **8 das 9 migrações candidatas colidem** com tabelas/tipos já em produção. Aplicar tudo QUEBRA o banco.
- Existem **6 tabelas** de suporte que meu backlog não conhecia (`manta_rag_feedback/errors/decisions/ml_models/ml_predictions/ml_training_runs`) — 80% do que propus em v4.5/v4.6 **já existe**, em versão mais madura.
- Peças ORIGINAIS que valem manter: v4.4 (4 verticais novos como SKILL.md), v4.5 governance (cross-refs, curation backlog, approval workflow) e v4.7 handoffs playbook.
- **Recomendação:** Opção 1 do plano — refactorar as 9 migrações para o schema real e aplicar seletivamente.

---

## 1. O que existe em produção

### 1.1 Schema — 19 tabelas em `public`

| Tabela | Rows | Domínio |
|---|---:|---|
| `manta_rag_documents` | 71 | L0.5 documentos indexados, sanitização R1 aplicada |
| `manta_rag_chunks` | 71 | Chunks com **embedding vector(1024)** bge-m3 + HNSW cosine |
| `manta_rag_cases` | 0 | Feedback loop — casos exemplares do learner agent |
| `manta_rag_queries` | 0 | Log de queries (trace_id linkado) |
| `manta_rag_feedback` | 0 | Feedback do usuário sobre chunks (util, correção) |
| `manta_rag_errors` | 0 | Erros pegos por guard-rails (aluci/consist/context) |
| `manta_rag_decisions` | 2 | **Precedentes** MN — `paradigmatico` flag para replicação |
| `manta_rag_ml_predictions` | 0 | Snapshots risk-scorer/nc-classifier |
| `manta_rag_ml_models` | 0 | Versionamento (model_id, versao) |
| `manta_rag_ml_training_runs` | 0 | Re-treino noturno via Cowork |
| `manta_trace` | 9 | Trace observability (parent_trace_id, evento, skill, tokens…) |
| `teses_academicas` | **36** | WF-AKP-001 fonte — status: catalogado→extraido→graded→approved→ingested |
| `knowledge_extractions` | **52** | KEs — tipos: metodo/parametro/formula/benchmark/case_study/norma |
| `ke_embeddings` | **52** | pgvector 1024d bge-m3 (embedding **separado** dos KEs — FK ke_codigo) |
| `manta_agent_messages` | 4 | A2A Nível 1 — mensageria inter-agente (correlation_id) |
| `manta_agent_capabilities` | **17** | A2A Nível 2 — capability registry (routing dinâmico) |
| `manta_api_clients` | 0 | Whitelist A2A externos (api_key_hash SHA256) |
| `manta_api_calls` | 0 | Log A2A com rate_limit |
| `manta_projeto_status_snapshots` | 0 | Snapshots status com gate `aprovado=true + publicado=true` |

### 1.2 Extensões — `vector 0.8.0` instalada em `public`

Advisor WARN: extensão está em `public`, deveria estar em `extensions`. Legado — herdado do template Supabase.

### 1.3 Funções descobertas

| Função | Assinatura | Propósito |
|---|---|---|
| `manta_rag_search(...)` | 8 args (embedding + 7 filtros: projeto, tipos[], perfil, datas, apenas_aprovados) | Busca RAG geral |
| `manta_rag_agent_search(embedding, agente, limit)` | 3 args | Busca RAG por agente |
| `manta_agent_rag(agente, embedding, limit)` | 3 args | Alias/orquestração |
| `rag_search(embedding, count, collection, agent, project, min_quality)` | 6 args com **enums `rag_collection` + `rag_agent`** | Versão tipada |
| `wf_akp_touch_updated_at()` | trigger | Auto-update updated_at |

**Descoberta importante:** existem tipos customizados `rag_collection` e `rag_agent` (enums SQL). Minhas migrações não sabem disso e criariam duplicatas.

### 1.4 17 agentes registrados em `manta_agent_capabilities`

| agent_id | capability | modelo | tags |
|---|---|---|---|
| aluci-guard | validar-alucinacao | haiku | guard, R2 |
| consist-guard | validar-consistencia | haiku | guard, consistencia |
| context-guardian | preservar-contexto | haiku | guard, contexto |
| M02 | analise-juridica, peca-juridica | sonnet | juridico, claim, output |
| M07 | sicro-lookup | haiku | sicro, custos |
| **M12** | **orquestrar** | **sonnet** | **orquestrador** ← este é o Maestro |
| M13 | business-development | sonnet | bd, prospeccao |
| M16 | revisar-entregavel | sonnet | qa, revisor |
| M17 | testar-consistencia | haiku | qa, testador |
| M18 | arquiteto-ia | opus | arquitetura, decisao |
| M19 | orcamento-executivo | sonnet | orcamento, custos |
| M20 | qa-transversal | sonnet | qa, gate |
| M21 | sharepoint-indexar | haiku | sharepoint, indice |
| **M22** | **extrator-sondagem** | **haiku** | **geotecnia** ← integração com backend Sondagem do manta-hub |
| M23 | rag-consultar, rag-indexar | haiku | rag, query, ingest |

### 1.5 Distribuição dos 52 KEs

Por tipo:
| Tipo | N | % |
|---|---:|---:|
| metodo | 23 | 44% |
| benchmark | 12 | 23% |
| case_study | 8 | 15% |
| parametro | 5 | 10% |
| norma | 3 | 6% |
| formula | 1 | 2% |

Por agente destino (top 10):
| Agente | N KEs |
|---|---:|
| 07 (cronograma) | 18 |
| 05 (orcamento) | 12 |
| 15 (advisory) | 12 |
| 01 (claims) | 10 |
| **03-S1 (rodovias)** | 9 |
| 02-C (contratual claims) | 8 |
| **03-S8 (saneamento)** | 7 |
| **03-S4 (metrô)** | 5 |
| **03-S2 (OAE)** | 5 |
| 06 (modelagem) | 2 |
| 16 (arquiteto-ia) | 1 |

**Observação crítica:** os KEs cobrem S1, S2, S4, S8 mas **NÃO** cobrem S3 (ferrovia), S5 (túneis), S6 (portos), S7 (aeroportos), S9 (energia), S10 (barragens), S11 (mineração), S12 (óleo & gás), S13 (edificações). Meus 4 verticais novos (v4.4) + coleções v4.2 tentavam cobrir isso — permanecem como valor incremental real.

### 1.6 Advisors — riscos ativos

**ERROR (2 — precisam ação):**
- `v_manta_l05_overview` e `v_ke_por_agente` são **SECURITY DEFINER** → risco de bypass de RLS.
  Fix: `ALTER VIEW ... SET (security_invoker = on);`

**WARN (6):**
- 5 funções com `search_path` mutável → risco de function injection. Fix: `ALTER FUNCTION ... SET search_path = public, extensions;`
- 1 extensão `vector` em `public` — mover para `extensions`.

**INFO (10 tabelas RLS enabled sem policy, 10 FKs sem índice, 30+ índices unused):**
- Baixo risco. RLS sem policy = 0 acessos. FKs sem índice = perf marginal em BD vazio. Unused = normal em BD novo.

### 1.7 15 migrações já aplicadas

```
20260615023353  manta_maestro_rag_schema_init         (base RAG)
20260615023416  manta_maestro_rag_rpcs_and_rls        (RPCs + RLS)
20260615023525  manta_maestro_rag_views               (views)
20260615023619  manta_maestro_trace_schema            (observability)
20260705144535  wf_akp_001_academic_ingestor          ← 36 teses ingeridas
20260705152607  wf_akp_001_align_with_handoff_schema  ← 52 KEs ingeridos
20260711172514  migrate_embedding_768_to_1024_bge_m3  ← migração de modelo
20260711172614  create_layer_c_operational_and_d_ml   ← ML pipeline
20260711173622  c_create_a2a_messages_and_capabilities ← A2A base
20260711173643  d_create_l05_overview_view_and_r1_functions
20260711173800  a_part1_migrate_legacy_rows_sanitized_no_drop
20260711173806  b_fix_views_security_invoker          (parcial — 2 views ainda ERROR)
20260711174125  drop_legacy_rag_documents_authorized_by_mn
20260711174144  create_a2a_helper_views
20260711184058  create_a2a_external_poc_schema_fixed
```

**Observação:** já há uma migração `b_fix_views_security_invoker` mas 2 views (`v_manta_l05_overview`, `v_ke_por_agente`) ainda estão em SECURITY DEFINER — fix incompleto.

---

## 2. Mapa de conflitos — v4.6 vs Prod

| Migração v4.6 | Conflito | Adaptação viável? |
|---|---|---|
| `2026_07_05_v4_2_agents_s6_s10.sql` — cria `rag_collections` + `sp_agent_routing` + `maestro_routing_keywords` | ❌ Prod não tem essas tabelas — usa `manta_agent_capabilities` + tags | **Sim** — abandonar tabelas, propor keywords via tags |
| `2026_07_12_akp_stages_4_6.sql` — cria `academic_theses` + `academic_knowledge_elements` + vector(1536) | ❌ Colide com `teses_academicas` + `knowledge_extractions` + vector(1024) | **Descartar** — schema já existe |
| `2026_07_12_akp_hybrid_search.sql` — cria `search_tsv` + função hybrid | ⚠️ Prod tem `manta_rag_search` mas sem hybrid explícito. Aditivo? | **Sim** — ADD COLUMN em `knowledge_extractions` + criar `match_kes_hybrid` novo |
| `2026_07_12_akp_telemetry.sql` — cria `agent_query_log` + views | ❌ Prod tem `manta_rag_queries` + `manta_trace` + views | **Substituir** — usar `manta_rag_queries` já existente |
| `2026_07_12_verticals_v4_4.sql` — 4 novas coleções + 4 sp_routing + 65 keywords | ❌ Não há `rag_collections`/`sp_agent_routing` | **Substituir** — registrar 4 novos agentes em `manta_agent_capabilities` |
| `2026_07_12_akp_governance_v4_5.sql` — cross-refs + versioning + curation_backlog + change_requests | ✅ Prod não tem cross-refs; tem parcial versioning via updated_at | **Aditivo** — ADD COLUMN `related_kes` em `knowledge_extractions`, criar novas tabelas |
| `2026_07_12_llm_judge_v4_6.sql` — judge_score + response_flags | ⚠️ Prod tem `manta_rag_errors` + guards. Overlap parcial. | **Adaptar** — usar `manta_rag_errors` para flags baixas OU tabela paralela |
| `2026_07_12_maestro_learned_router_v4_6.sql` — predictions + views | ✅ Prod tem `manta_rag_ml_predictions/models/training_runs` | **Reuso** — registrar como model_id="maestro_router" em `manta_rag_ml_models` |
| `2026_07_12_manta_cases_v4_6.sql` — WF-MCP-001, coleção `mcs:` | ✅ Prod tem `manta_rag_cases` mas conceito diferente (feedback learner ≠ curadoria memoriais) | **Aditivo** — pode coexistir com nome diferente |

### 2.1 Componentes NÃO SQL do v4.6 (todos ficam válidos)

| Componente | Aplicabilidade |
|---|---|
| 9 SKILL.md dos agentes verticais (S6-S13 + S5) | ✅ Valem — cobrem gaps de KEs prod |
| Playbook cross-agent (8 cenários) | ✅ Vale — nenhum conflito |
| CI parity check (.github/workflows) | ✅ Vale — aplicável |
| `apply_manta_migrations.py` | ⚠️ Precisa reordenar ordem canônica considerando prod |
| `akp_ingest.py` | ⚠️ Trocar OpenAI 1536d → bge-m3 1024d; adaptar schema `teses_academicas` + `knowledge_extractions` + `ke_embeddings` |
| `akp_smoke_test.py` | ⚠️ Trocar RPC de `match_academic_knowledge` → `manta_rag_agent_search` |
| `akp_report.py` | ⚠️ Trocar views por `manta_rag_queries` + `manta_trace` |
| `akp_judge.py` | ⚠️ Trocar UPDATE em `agent_query_log` → INSERT em `manta_rag_errors` |
| `manta_cases_extract.py` | ✅ Vale — só produz JSON, ingestor separado |
| `maestro_learned_router.py` | ⚠️ Persistir em `manta_rag_ml_models` (v="maestro_router_v1") |
| `publish_agents.py` | ✅ Vale — não depende de schema |

---

## 3. Recomendação de convergência

### Fase 1 — Fixes críticos de segurança (30 min, alto valor, baixo risco)

Antes de qualquer coisa, resolver os 2 ERRORS + 6 WARNS de advisors:

```sql
-- 1. SECURITY DEFINER → INVOKER
ALTER VIEW public.v_manta_l05_overview SET (security_invoker = on);
ALTER VIEW public.v_ke_por_agente SET (security_invoker = on);

-- 2. Fix search_path mutable em 6 funções
ALTER FUNCTION public.manta_rag_search SET search_path = public, extensions;
ALTER FUNCTION public.manta_rag_fts SET search_path = public, extensions;
ALTER FUNCTION public.rag_search SET search_path = public, extensions;
ALTER FUNCTION public.wf_akp_touch_updated_at() SET search_path = public, extensions;
ALTER FUNCTION public.manta_agent_rag SET search_path = public, extensions;
ALTER FUNCTION public.manta_rag_agent_search SET search_path = public, extensions;

-- 3. RLS policies em 10 tabelas — decidir política por tabela.
-- Exemplo mínimo: só service_role acessa.
CREATE POLICY svc_only ON manta_agent_capabilities FOR ALL TO service_role USING (true);
-- ... repetir para manta_agent_messages, manta_api_*, manta_projeto_status_snapshots,
-- manta_rag_decisions/errors/feedback/ml_models/ml_training_runs
```

### Fase 2 — Refactor das migrações v4.6 (2-3h)

Reescrever 4 migrações em cima do schema real:

**M-A** — `2026_07_13_verticals_bindings.sql`:
- INSERT 9 rows em `manta_agent_capabilities` para S1-S13 verticais + M12 orquestrar → S1..S13
- Cada linha: agent_id = `03-S1` até `03-S13`, capability = `especialista-<segmento>`, tags = keywords do CLAUDE.md v4.4
- Zero conflito porque tabela usa `(agent_id, capability)` como PK composto

**M-B** — `2026_07_13_akp_governance_adapted.sql`:
- `ALTER TABLE knowledge_extractions ADD COLUMN related_kes JSONB DEFAULT '{}'::jsonb;`
- `CREATE VIEW v_akp_contradictions ...` (adaptar para `knowledge_extractions.ke_codigo` + `related_kes`)
- Manter tabela `academic_theses_history` (adaptar FK para `teses_academicas.codigo`)
- Manter `akp_curation_backlog` (nova, sem conflito)
- Manter `agent_change_requests/reviews` (novas, sem conflito)

**M-C** — `2026_07_13_llm_judge_adapted.sql`:
- Estender `manta_rag_queries` com `ADD COLUMN judge_score SMALLINT`
- Reuso `manta_rag_errors` como flag store: `severidade='warn'` quando score < 3
- Nova view `v_akp_judge_health` sobre `manta_rag_queries` + `manta_rag_errors`
- Sample stratified via função nova

**M-D** — `2026_07_13_hybrid_search_adapted.sql`:
- Adicionar `search_tsv` em `knowledge_extractions` + `manta_rag_chunks`
- Nova função `match_kes_hybrid(query_text, query_embedding, ...)` sobre `ke_embeddings + knowledge_extractions` (não sobre `academic_knowledge_elements`)
- Reuso RRF k=60 com `ts_rank_cd`

**Descartar** (já existe em prod ou obsoleto):
- `2026_07_05_v4_2_agents_s6_s10.sql` inteiro (rag_collections/sp_agent_routing/keywords)
- `2026_07_12_akp_stages_4_6.sql` (schema base academic_theses)
- `2026_07_12_akp_telemetry.sql` (`agent_query_log` — usar `manta_rag_queries`)
- `2026_07_12_verticals_v4_4.sql` (rag_collections + sp_agent_routing versão S5/S11-S13 — vira M-A)
- `2026_07_12_maestro_learned_router_v4_6.sql` — usar `manta_rag_ml_models` existente com row `model_id='maestro_router_v1'`

**M-E** — `2026_07_13_manta_cases_pipeline.sql`:
- Coleção conceitual `manta-cases` como enum value em `rag_agent` (se enum permitir extensão)
- Ou tabela dedicada `manta_case_elements` linkada a `manta_rag_cases` existente (case_id) mas com KEs formais
- Manter função `match_manta_cases_hybrid` adaptada

### Fase 3 — Ingerir 4 verticais faltantes (1h)

Os 4 novos SKILL.md (S5/S11/S12/S13) + 6 KEs de bibliografia de arq-agentes:

```bash
# Adaptar akp_ingest.py:
# - trocar model=text-embedding-3-small para model=bge-m3 (via sentence-transformers)
# - alvo: teses_academicas + knowledge_extractions + ke_embeddings
# - dim: 1024
python scripts/akp_ingest.py \
  --input Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-arquitetura-agentes.json \
  --theses-inventory Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-arquitetura-agentes-theses.csv \
  --embedding-model bge-m3 \
  --schema-target production  # nova flag
```

### Fase 4 — Update ONBOARDING.md (30min)

Reescrever o ONBOARDING para refletir a realidade: prod já rodou stages 1-4 do AKP, próximo passo é aplicar M-A a M-E (não 9 migrações genéricas).

---

## 4. Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Aplicar migrações do repo direto quebra prod | ALTA se rodar `apply_manta_migrations.py` como está | Bloqueia banco produção | **Nunca rodar sem refactor Fase 2** |
| Nome de agente divergente (S6 vs M22 vs "03-S6") | Média | Confusão de routing | Criar tabela de sinônimos em `manta_agent_capabilities.tags` |
| bge-m3 vs OpenAI compat | Alta se seed ingerido com modelo errado | Recall zero | Sempre bge-m3 em prod |
| 2 views SECURITY DEFINER | Alta | Bypass RLS | Fase 1 fix imediato |
| Registrar S5/S11-S13 sem KEs correspondentes | Média | Agente sem lastro | Priorizar curadoria acadêmica desses segmentos |

---

## 5. Próximos passos concretos

Ordem sugerida (esta janela ou próxima):

1. **Aplicar Fase 1** (fixes de segurança) — 30 min, alto valor imediato.
2. **Escrever as 5 migrações adaptadas M-A a M-E** — 2-3h.
3. **Refactorar 5 scripts em manta-hub** — 1-2h (akp_ingest, smoke_test, report, judge, learned_router).
4. **Ingerir os 6 KEs de bibliografia arq-agentes** + registrar 4 verticais em `manta_agent_capabilities` — 30 min.
5. **Curadoria manual das teses faltantes** (S3/S5/S6/S7/S9/S10/S11/S12/S13) — humano, semanas.
6. **Refazer ONBOARDING.md** com a realidade — 30 min.
7. **Retirar as 9 migrações antigas do repo** (para não confundir MN quem clonar) OU marcar como "DEPRECATED — see AUDIT-v4.6-vs-PROD.md" — 5 min.

Nenhum desses passos requer aprovação MN adicional além do que já tenho — todos os SQL propostos vão para migrações candidatas no repo primeiro, só depois `apply_migration` chamado.

---

## 6. Conclusão

O trabalho conceitual das 6 sprints v4.2 → v4.6 é **valioso mas foi construído sobre um schema imaginário**. A produção real é significativamente mais madura (17 agentes, guards, feedback loop, ML pipeline, A2A messaging já implementados) mas tem lacunas concretas que meu backlog preenche (verticais S5/S11-S13, cross-refs entre KEs, curation backlog formal, publish multi-channel, learned router explícito, LLM-as-a-judge com breakdown).

O caminho certo é **convergência**, não substituição: adaptar meus artefatos para o schema real via 5 migrações novas (M-A a M-E), descartar 4 migrações do repo antigo, refactorar 5 scripts.

Recomendo autorização para execução da Fase 1 (fixes de segurança) imediatamente e produção das migrações M-A a M-E na próxima janela.
