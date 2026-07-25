# CLAUDE.md — Manta Maestro (Agent Registry & Orchestration)

Registro mestre e especificação operacional dos agentes IA da Manta Associados.
Este arquivo é o "CLAUDE.md master" referenciado pelos SKILL.md, runbooks do
SharePoint, e pelas chamadas ao Maestro (Manta 00).

**Versão: v5.0** (2026-07-25) — Arquitetura escalável com 8 pilares, orquestração
em background, RAG híbrido (BM25 + vetor + reranker), tiering de modelo automático,
observabilidade completa, e ciclo de vida de skills com versionamento.

**Status de adoção:**
- Produção: Manta 00–02, 04–07, 13–16, 03-S1..S4 (15 agentes)
- Staging (v5.0): Manta 03-S6..S10 (5 novos, integrados v4.2)
- Roadmap: Replicação de S5 em S6..S10; feedback loops com LLM-as-judge

---

## OS 8 PILARES DE ARQUITETURA v5.0

### P1 — Routing Determinístico (Maestro)

O Maestro (Manta 00) é o router canônico: recebe prompt do usuário, aplica
regras de roteamento (R1), e injeta config (model override, skill_version_pin,
context window allocation) no agente alvo.

**Entrada:** `(prompt, user_id, session_id, context_hints)`
**Saída:** `(agent_id, skill_id[], config_override, context_injection)`

Regras de roteamento: keyword matching → embedding similarity → fallback
(maestro resolve ambigüidades).

---

### P2 — Qualidade Vertical com Pinagem de Skill

Cada agente vertical (S1–S10) pineia skills específicos via `skill_version_pin`
em settings.json local. Checksums MD5 impedem drift involuntário.

**Garantias:**
- S8 (saneamento) sempre usa `saneamento.v5.0.md` (não a v4.9)
- RAG collections versionadas: `san:v5.0:chunks` (separado do `san:v4.9:chunks`)
- Rollback automático se checksum falhar (deprecation log)

---

### P3 — Ciclo de Vida (8 fases)

Todos os agentes verticais (Manta 03-*) suportam intake declarativo com 8 fases:

1. **Estudo prévio / EVTE** — Diagnóstico, benchmarking, análise preliminar
2. **Projeto básico** — Conceitos, layouts, orçamento order-of-magnitude
3. **Projeto executivo** — Detalhamento, especificações, cronograma vinculante
4. **Obra em execução** — Acompanhamento, desvios, revisões de escopo
5. **Operação & manutenção** — Gestão de ativo, indicadores, OPEX
6. **Processo competitivo / licitação** — Edital, termo de referência, avaliação
7. **Due diligence / M&A** — Auditoria financeira, ambiental, legal, riscos
8. **Encerramento / descomissionamento** — Final de vida útil, passivos, reabilitação

Usuário declara fase via: `{phase: "projeto-executivo"}` ou contexto é inferido
via embedding + BM25 no RAG.

---

### P4 — RAG Híbrido (BM25 + Vetor + Reranker)

**Componentes:**
1. **BM25 (Elasticsearch)** → Keyword matching rápido (1–2ms)
2. **Embedding (Qdrant/Pinecone)** → Semantic search (5–10ms)
3. **Reranker (R6)** → Cross-encoder fine-tuned para queries de eng. (10–20ms)
4. **Cache de embedding** → Resultados frequentes (10ms → 1ms)

**Fluxo:**
```
query → [BM25 top-10] + [embedding top-10] → union/dedup
      → [reranker top-5] → agent recebe resultado filtrado
```

Coleções em Supabase: `rag_chunks` (versioned), `rag_metadata` (lineage),
`rag_cache` (TTL 7 dias).

---

### P5 — Tiering de Modelo Automático (R7)

Baseado em `input_tokens` + `complexity_score`, router escolhe tier:

```
IF input_tokens < 2000 AND complexity < 3
   → Haiku 4.5 (custo: ~$0.08 / 1M)
ELSE IF input_tokens < 10000 AND complexity < 5
   → Sonnet 5 (custo: ~$3 / 1M)
ELSE
   → Opus 5 (custo: ~$15 / 1M)
```

**Complexity score:** sum([keywords_matched, rag_reranker_score > 0.7,
cross_agent_ref, file_processing_token_ratio])

Fallback inteligente (R8): se Sonnet timeout após 60s, cascade para Opus
(mantém estado).

---

### P6 — Observabilidade (Run Tracking + Custos)

**Logs estruturados em Supabase (`agent_runs`):**
- `run_id` (UUID)
- `agent_id`, `skill_id`, `model_tier`
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

**Dashboard (Grafana):**
- Custo/agente/dia
- Latência p50/p95/p99
- Taxa de erro por segmento (S6..S10)
- Feedback trend (3 meses)

**Audit:** todos os runs imutáveis (log append-only).

---

### P7 — Orquestração em Background (APScheduler)

Maestro pode disparar tasks assíncronos (não-blocking):

```python
# Exemplo: reindex RAG diariamente às 02:00 UTC
trigger = create_trigger(
    name="rag-reindex-daily",
    cron="0 2 * * *",
    prompt="Reindex RAG collections (S6–S10) e valide checksums"
)

# Feedback loop: retraining a cada 7 dias
trigger = create_trigger(
    name="embedding-retraining",
    cron="0 3 * * 0",  # Sunday 3am
    prompt="Fetch user_ratings > 4, retrain embedding model"
)
```

Triggers persisted em `agent_triggers` (Supabase), execução via Temporal/Celery.

---

### P8 — Versionamento de Skills (PK v5.0 + Checksums)

**Estrutura:**
```
.claude/agents/
  ├── agente-saneamento.md          # live
  ├── agente-saneamento.v4.9.md     # archived
  └── VERSIONS.json
     {
       "agente-saneamento": {
         "v5.0": {
           "checksum": "a3f1c8e2d4b5...",
           "pinned_by": ["S8-prod"],
           "rag_collection": "san:v5.0:chunks",
           "created_at": "2026-07-25T14:32:00Z"
         },
         "v4.9": {
           "checksum": "b2e4d7c3a1f6...",
           "deprecated_at": "2026-07-25"
         }
       }
     }
```

**Garantias:**
- Rollback = carregar skill v4.9 via checksum
- Deprecation = marca v4.9, notifica owners, 30d grace period
- Pin = settings.json local: `skill_version_pin.agente-saneamento = v5.0`

---

## R1 — MAESTRO (ROTEADOR CANÔNICO)

### Entrada

```json
{
  "prompt": "Preciso de ajuda com uma ETA em São Paulo",
  "user_id": "usr_12345",
  "session_id": "sess_abc123",
  "context_hints": ["saneamento", "ETA", "projeto-executivo"],
  "file_context": [
    {"name": "projeto.dwg", "mime": "image/vnd.dwg", "size_mb": 2.1}
  ]
}
```

### Processamento (3 estágios)

**Estágio 1: Keyword matching + embedding**

```
Keywords: ["ETA", "São Paulo", "saneamento"]
  ↓
BM25 lookup: "san:*" collections → relevance ≈ 0.92
Embedding: embed(prompt) → similarity(agente-saneamento) ≈ 0.88
  ↓
Candidatos: {agente-saneamento: 0.90 (média)}
```

**Estágio 2: Contexto + ciclo de vida**

```
IF contexto contém {projeto.dwg, "projeto-executivo"}
   → injetar context: phase="projeto-executivo", file_processing=true
   → allocate window_tokens=8000 (vs default 4000)
```

**Estágio 3: Tiering + config**

```
input_tokens = 1200 (prompt + context)
complexity = 2.5 (1 arquivo DWG, keywords_matched=2)

model_tier = Haiku 4.5  (custo-benefício)
fallback_tier = Sonnet 5 (se Haiku timeout)

skill_id = agente-saneamento.v5.0
rag_pin = san:v5.0:chunks
```

### Saída

```json
{
  "agent_id": "manta-03-s8",
  "skill_ids": ["agente-saneamento.v5.0", "autodesk-toolkit"],
  "config": {
    "model_tier": "haiku-4-5",
    "fallback_tier": "sonnet-5",
    "max_tokens": 2048,
    "temperature": 0.7,
    "context_window_tokens": 8000
  },
  "context_injection": {
    "phase": "projeto-executivo",
    "file_processing": true,
    "rag_collection": "san:v5.0:chunks",
    "skill_version_pin": "v5.0"
  },
  "routing_confidence": 0.90,
  "fallback_agent": "manta-00-maestro"
}
```

---

## R2–R5 (Existentes — sem alteração)

Mantidas do v4.2:
- R2: Skill loader (carregar .md do agente)
- R3: Context window manager (alocar tokens)
- R4: Tool dispatcher (chamar Bash/Read/Grep/etc.)
- R5: Output formatter (serializar resposta)

---

## R6 — RERANKING (NOVO)

**Entrada:** lista de 20 chunks do RAG (BM25 + embedding)

**Processamento:**
- Cross-encoder (modelo fine-tuned em queries + eng. context)
- Score: relevância relativa ao prompt original
- Threshold: score > 0.5 ou top-5 (o que for maior)

**Saída:** top-5 chunks ordenados por score

**Implementação:** Infinity (Hugging Face), latência ~15ms/batch.

---

## R7 — TIERING AUTOMÁTICO (NOVO)

**Entrada:**
```json
{
  "input_tokens": 2400,
  "keywords_matched": 3,
  "rag_reranker_score_max": 0.92,
  "files_to_process": 1,
  "cross_agent_references": 0
}
```

**Fórmula:**
```
complexity = (
  keywords_matched * 1.0 +
  (rag_reranker_score_max > 0.7 ? 1.5 : 0) +
  files_to_process * 2.0 +
  cross_agent_references * 0.5
)
```

**Decisão:**
```
IF input_tokens < 2000 AND complexity < 3.0
   → Haiku 4.5
ELIF input_tokens < 10000 AND complexity < 6.0
   → Sonnet 5
ELSE
   → Opus 5
```

**Custo esperado por tier:**
- Haiku: ~$0.08 / 1M
- Sonnet: ~$3 / 1M
- Opus: ~$15 / 1M

---

## R8 — FALLBACK INTELIGENTE (NOVO)

Se agente timeout após 60s em modelo inicial:

```
1. Log: {run_id, agent_id, model_tier, latency_ms, timeout=true}
2. Resubmit com fallback_tier (próximo nível)
3. Manter estado: reinjetar {context, rag_results, partial_output}
4. Set max_tokens = 1500 (reduzir scope, não quebrar timeout novamente)
5. Alert: Slack #agent-ops se > 3 timeouts/hora em um agente
```

---

## R9 — FEEDBACK LOOP (NOVO)

Após cada run:
1. Coletar `feedback_score` (0–5 estrellas, opcional)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding "user_intent_vector" de prompts com score ≥ 4
4. Treinar/fine-tune reranker cross-encoder com high-scoring queries
5. Redeploy checksum atualizado em `VERSIONS.json`

---

## R10 — PURGA DE AGENT_MEMORY (NOVO)

Política de limpeza:

```
IF agent_memory_size_mb > 100
   OR last_purge > 30 days ago
   THEN:
     - Manter últimas 1000 completions
     - Descartar chunks com age > 7 dias e user_rating < 2
     - Manter embeddings de queries frequentes
     - Log: {agent_id, size_before, size_after, deleted_count}
```

Executado via trigger APScheduler (R7 dispara daily às 03:00 UTC).

---

## MAPA COMPLETO DE AGENTES — 20 agentes, 5 tiers

### Tier 1 — Horizontais (transversais)

| Código | Agente | Aliases | Tier default | Skill v5.0 | Checksum | Status |
|--------|--------|---------|--------------|-----------|----------|--------|
| Manta 00 | maestro | router, manta-router | Haiku→Sonnet | maestro.v5.0.md | `d3a2f1c8e4b7` | ✅ Prod |
| Manta 01 | claims | manta-claims, claim-mgmt | Opus | claims.v5.0.md | `c1f4b7d3a2e6` | ✅ Prod |
| Manta 02 | contratual | manta-02, legal | Sonnet | contratual.v5.0.md | `b2e5c3a1f7d4` | ✅ Prod |
| Manta 04 | imobiliario | real-estate, manta-04 | Sonnet | imobiliario.v5.0.md | `a4d7f2c1b3e8` | ✅ Prod |
| Manta 05 | orcamento | budget, manta-05 | Sonnet | orcamento.v5.0.md | `f3c8e1a4d2b6` | ✅ Prod |
| Manta 06 | modelagem | modeling, manta-06 | Sonnet/Opus | modelagem.v5.0.md | `e2b5d3a1c4f7` | ✅ Prod |
| Manta 07 | cronograma | schedule, manta-07 | Sonnet | cronograma.v5.0.md | `d1a6f4c2b3e5` | ✅ Prod |
| Manta 13 | bd | business-dev, manta-13 | Sonnet | bd.v5.0.md | `c3f2a1d5e4b6` | ✅ Prod |
| Manta 14 | apresentacoes | pptx, slides, manta-14 | Sonnet | apresentacoes.v5.0.md | `b4e3c1a2f6d5` | ✅ Prod |
| Manta 15 | advisory | advisory-board, manta-15 | Sonnet/Opus | advisory.v5.0.md | `a5d2f3c1b4e7` | ✅ Prod |
| Manta 16 | arquiteto-ia | ai-arch, manta-16-arq | Opus | arquiteto-ia.v5.0.md | `f6b1e3d5a2c4` | ✅ Prod |

### Tier 2–3 — Verticais por segmento (C3 + Ciclo de vida 8 fases)

| Código | Segmento | Agente | Tier default | Skill v5.0 | Checksum | RAG coleção | Status |
|--------|----------|--------|--------------|-----------|----------|-------------|--------|
| Manta 03-S1 | Rodovias | agente-rodovias | Sonnet | rodovias.v5.0.md | `f7a3b2c1d4e6` | rod:v5.0:* | ✅ Prod |
| Manta 03-S2 | OAE | agente-oae | Sonnet | oae.v5.0.md | `e4c2b3a1f5d7` | oae:v5.0:* | ✅ Prod |
| Manta 03-S3 | Ferrovia | agente-ferrovia | Sonnet | ferrovia.v5.0.md | `d5b1a3f2c4e6` | fer:v5.0:* | ✅ Prod |
| Manta 03-S4 | Metrô | agente-metro | Sonnet | metro.v5.0.md | `c6a2f4b1d3e5` | met:v5.0:* | ✅ Prod |
| Manta 03-S5 | Túneis | (S2+S4) | — | — | — | — | ⚡ Parcial |
| Manta 03-S6 | Portos | agente-portos | Sonnet | portos.v5.0.md | `b7d3e5a2f1c4` | por:v5.0:* | 🆕 v5.0 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | Sonnet | aeroportos.v5.0.md | `a8e1f3c2d4b6` | aer:v5.0:* | 🆕 v5.0 |
| Manta 03-S8 | Saneamento | agente-saneamento | Sonnet | saneamento.v5.0.md | `f1a3d2b4c5e7` | san:v5.0:* | 🆕 v5.0 ⭐ AySA |
| Manta 03-S9 | Energia | agente-energia | Sonnet | energia.v5.0.md | `e2b5c3a1d6f4` | ene:v5.0:* | 🆕 v5.0 ⭐ ANEEL |
| Manta 03-S10 | Barragens | agente-barragens | Sonnet | barragens.v5.0.md | `d3c4a2f5b1e6` | bar:v5.0:* | 🆕 v5.0 |

---

## CICLO DE VIDA — 8 FASES (Manta 03-*)

Todos os agentes verticais suportam intake via `phase` declarer:

```json
{
  "phase": "projeto-executivo",
  "segment": "s8",
  "deliverables": [
    "memorial-descritivo.pdf",
    "projeto-estrutural.dwg",
    "cronograma-macro.xlsx"
  ]
}
```

**Fases:**

| # | Fase | Artifacts típicos | RAG focus | Agente skill |
|---|------|-------------------|-----------|--------------|
| 1 | Estudo prévio / EVTE | relatório-diagnóstico.pdf, benchmarks | Legislação, casos de sucesso | baseline |
| 2 | Projeto básico | estudo-de-viabilidade.pdf, layouts conceituais | Normativas, orçamento order-of-magnitude | design |
| 3 | Projeto executivo | memorial-descritivo.pdf, CAD, especificações técnicas | Normas (ABNT), detalhes técnicos | exec |
| 4 | Obra em execução | relatório-mensal.pdf, fotos, desvios | Cronograma, riscos, SICRO/SESI | site-mgmt |
| 5 | Operação & manutenção | OPEX report, indicadores, manual de operação | O&M best practices, legislação | operations |
| 6 | Processo competitivo / licitação | edital.pdf, termo-referência.pdf, avaliação de propostas | Editais (BNDES, ANEEL, ANTAQ), jurisprudência | bid-mgmt |
| 7 | Due diligence / M&A | relatório-DD.pdf, auditoria, riscos, passivos | Financeiro, ambiental, legal | dd |
| 8 | Encerramento / descomissionamento | plano-desativação.pdf, remediação | Legislação de encerramento, reabilitação | closeout |

---

## ROUTING — REGRAS ATUALIZADAS (R1)

### Entrada ao Maestro

```
prompt = "Estudamos uma ETA para AySA em Buenos Aires, precisamos do básico"
user_id = mneves@mantaassociados.com
context_hints = []  # vazio, maestro infere
files = [{"name": "estudo-site.pdf", "size": 1.2MB}]
```

### Processamento

**Passo 1: Keyword extraction + embedding**

Keywords: ["ETA", "AySA", "Buenos Aires", "estudo"]

**Passo 2: BM25 × collections**

```
san:v5.0:chunks   → relevance 0.95 (ETA, AySA, estudo prévio)
aer:v5.0:chunks   → relevance 0.10 (sem match)
ene:v5.0:chunks   → relevance 0.05
```

**Passo 3: Embedding similarity**

```
embed(prompt) → similarity(agente-saneamento) = 0.92
                similarity(agente-energia) = 0.15
                similarity(agente-portos) = 0.08
```

**Passo 4: Routing decision**

```
agent = agente-saneamento  (score 0.90 = avg(0.95, 0.92, 0.88 complex))
phase = "estudo-previo"   (inferred from "básico")
model_tier = Haiku 4.5    (input < 2000, complexity < 3)
```

### Regras Keyword (R1 — especificação completa)

```
# S8 — SANEAMENTO
IF {saneamento|ETA|ETE|adutora|esgoto|água tratada|AySA|drenagem urbana|macrodrenagem|SNIS|PMSB|Lei 14.026|subsídio cruzado|elevatória|reservatório|RAP|EEE|EEAB|reúso|lodo|digestor|UASB|MBR|bombeamento|tratamento}
   → agente-saneamento (S8)

# S9 — ENERGIA
IF {transmissão|LT|subestação|ANEEL|RAP|leilão|ONS|EPE|PDE|R1-R5|torre|cabo|ACSR|CAA|ATSR|MRE|ACR|ACL|WEG|State Grid|ISA CTEEP|Alupar|Taesa|geração|eólica|PV|hidráulica|PCH|UHE|usina|térmica|nuclear|CCGT}
   → agente-energia (S9)

# S6 — PORTOS
IF {porto|terminal|ANTAQ|dragagem|molhe|quebra-mar|berço|calado|contêiner|granel|cais|píer|retroárea|pátio|TUP|TPS|PIANC|arrendamento|hidrovia|navios|cabotagem|longo-curso|fluvial|marítimo|acostagem|bóia}
   → agente-portos (S6)

# S7 — AEROPORTOS
IF {aeroporto|pista|RWY|taxiway|TWY|pátio|TPS|TECA|ANAC|RBAC|ICAO|Annex 14|FAA|balizamento|PAPI|ILS|PCN|gate|jetway|ponte|embarque|desembarque|TPS|TECA|aviação|regional|geral|concessão|pista-pouso|corredor|aproximação}
   → agente-aeroportos (S7)

# S10 — BARRAGENS
IF {barragem|vertedouro|CFRD|CCR|RCC|rejeitos|TSF|PNSB|ICOLD|CBDB|dique|SIGBM|ANM|ANA|Lei 12.334|Fundão|Brumadinho|descomissionamento|alteamento|montante|jusante|linha-centro|filtragem|dry-stack|PAE|PAEBM|ZAS|ZSS|HHP|piping|galgamento|liquefação}
   → agente-barragens (S10)

# S1 — RODOVIAS
IF {rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT|asfalto|concreto|base|sub-base|terraplenagem|corte|aterro|drenagem-rodoviária|tráfego|capacidade|PSV|VDM}
   → agente-rodovias (S1)

# S2 — OAE (Pontes, Viadutos, Túneis)
IF {ponte|viaduto|OAE|NBR 7187|túnel|rodoviário|ferroviário|fundação|pilares|aparelhos-apoio|junta|elastômero|expansão|vão|laje|estrutura-metálica|concreto-protendido}
   → agente-oae (S2)

# S3 — FERROVIA
IF {ferrovia|trilho|AMV|dormente|via-permanente|bitola|pantógrafo|catenária|tráfego-ferroviário|estação|ptv|ramal|desvio|junção|manutenção-trilho|lastro}
   → agente-ferrovia (S3)

# S4 — METRÔ / VLT
IF {metrô|estação|NATM|PSD|linha|VLT|veículo-leve|subterrâneo|elevado|superficial|portal|túnel-metrô|trem|automático|ATO|sinalização-metrô|estação-intermediária}
   → agente-metro (S4)

# HORIZONTAIS (fallback)
IF {claims|indenização|sinistro|seguro}
   → agente-claims (01)
IF {contrato|legal|cláusula|jurisdição|litigância}
   → agente-contratual (02)
...
```

### Confidence Score (quando múltiplos matches)

```
score = 0.4 × keyword_relevance
      + 0.4 × embedding_similarity
      + 0.15 × rag_max_score
      + 0.05 × user_history_affinity

IF score_top1 - score_top2 < 0.1
   → maestro retorna ambiguidade, solicita clarification
```

---

## RAG — COLEÇÕES VERSIONADAS EM SUPABASE

### Estrutura

Cada coleção: `{prefix}:v5.0:chunks` (namespace versionado)

**Tabelas:**
- `rag_chunks` — chunks (document_id, coleção, embedding, text, metadata)
- `rag_metadata` — lineage (fonte, data, versão, checksum)
- `rag_cache` — cache de queries recentes (TTL 7 dias)

### Especificação por coleção

| Coleção | Prefixo | Versão | Fontes iniciais | N_chunks target | Status | Owner |
|---------|---------|--------|-----------------|-----------------|--------|-------|
| Saneamento | san: | v5.0 | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES, AySA | 2500 | 🆕 v5.0 | AySA team |
| Energia | ene: | v5.0 | ANEEL editais, R1-R5 EPE, ONS, IEEE, ABNT, PDE | 3000 | 🆕 v5.0 | State Grid liaison |
| Portos | por: | v5.0 | ANTAQ, PIANC, editais BNDES/ANTAQ, ICS, portos-br | 2000 | 🆕 v5.0 | ANTAQ expert |
| Aeroportos | aer: | v5.0 | ANAC/RBAC, ICAO Annex 14, FAA ACs, INAC, concessões | 1800 | 🆕 v5.0 | ANAC liaison |
| Barragens | bar: | v5.0 | ICOLD, CBDB, SIGBM, Lei 12.334, COBRAMSEG, barragens-br | 2200 | 🆕 v5.0 | CBDB expert |
| Rodovias | rod: | v5.0 | DNIT, SICRO, ABNT, normas DNIT, cases históricos | 4000 | ✅ v5.0 | DNIT team |
| OAE | oae: | v5.0 | NBR 7187, DNIT, casos-OAE, estruturas metálicas | 2000 | ✅ v5.0 | Struct team |
| Ferrovia | fer: | v5.0 | SuperVia, ABNT, via-permanente, normas Inmetro | 1500 | ✅ v5.0 | Rail team |
| Metrô | met: | v5.0 | NATM, PSD, normas metrô, cases linha 4/5 | 2000 | ✅ v5.0 | Metro team |

### Ingestão

**Processo:**
1. Upload fontes para `rag_staging/{prefixo}/`
2. OCR (PDF → txt) + chunk (512 tokens, overlap 50)
3. Embed via Infinity (Hugging Face, modelo: `intfloat/multilingual-e5-large-instruct`)
4. Persistir em `rag_chunks` com versão + checksum MD5
5. Validar: reranker score > 0.5 em test queries

**SLA:** Coleção nova disponível em ≤ 24h da aprovação.

---

## SHAREPOINT — ROUTING RULES ESTRUTURADO

Cada agente roteado automaticamente para pasta SP sugerida (via `sp_agent_routing`):

| Agente | Site | Drive | Pasta | Pattern | Tier acesso |
|--------|------|-------|-------|---------|------------|
| agente-saneamento | Manta.net | Projetos | 03_Projetos/Saneamento/2026-AySA | *.pdf, *.dwg, *.xlsx, *.docx | Editor |
| agente-energia | Manta.net | Projetos | 03_Projetos/Energia/ANEEL-2026 | *.pdf, *.dwg, *.xlsx, RAP-* | Editor |
| agente-portos | Manta.net | Projetos | 03_Projetos/Portos/ANTAQ | *.pdf, *.dwg, PIANC-* | Editor |
| agente-aeroportos | Manta.net | Projetos | 03_Projetos/Aeroportos/ANAC-2026 | *.pdf, RBAC-*, *.xlsx | Editor |
| agente-barragens | Manta.net | Projetos | 03_Projetos/Barragens/ICOLD-Registry | *.pdf, *.dwg, SIGBM-* | Editor |
| agente-rodovias | Manta.net | Projetos | 03_Projetos/Rodovias/SICRO-2026 | *.pdf, *.dwg, DNIT-* | Editor |
| agente-oae | Manta.net | Projetos | 03_Projetos/OAE/Estruturas | *.pdf, *.dwg, NBR-7187 | Editor |
| agente-ferrovia | Manta.net | Projetos | 03_Projetos/Ferrovia/Via-Permanente | *.pdf, *.dwg, AMV-* | Editor |
| agente-metro | Manta.net | Projetos | 03_Projetos/Metro/Linha4-L5 | *.pdf, *.dwg, PSD-* | Editor |
| agente-claims | Manta.net | Projetos | 05_Claims/2026-Portfolio | *.pdf, *.docx, claim-* | Viewer |
| agente-contratual | Manta.net | Projetos | 05_Legal/Contratos | *.pdf, *.docx, contrato-* | Viewer |

---

## DEPLOY CHECKLIST v5.0

### Phase 1 — Preparação (Sem alterações em produção)

- [ ] Validar 8 pilares (arquitetura doc)
- [ ] Revisar R1 routing (20 agentes)
- [ ] Testar R6 reranker (cross-encoder) em 100 queries
- [ ] Validar R7 tiering em histórico de 1000 runs
- [ ] Implementar R8 fallback (mock timeout)
- [ ] Criar R9 feedback loop skeleton (Supabase schema)
- [ ] Implementar R10 memory purge policy (APScheduler test)

### Phase 2 — RAG (24–48h antes go-live)

- [ ] Criar 5 coleções S6–S10 em Supabase (san:v5.0:*, ene:v5.0:*, etc.)
- [ ] Ingerir fontes iniciais (2000–4000 chunks/coleção)
- [ ] Testar BM25 × embedding em 50 queries/coleção
- [ ] Validar reranker score > 0.5 em queries críticas
- [ ] Criar `rag_cache` (TTL 7 dias)
- [ ] Build VERSIONS.json com checksums (MD5)
- [ ] Backup RAG v4.9 → `rag_archive`

### Phase 3 — Skill versionamento (T-24h)

- [ ] Copiar 5 agent skills para v5.0 (portos, aeroportos, saneamento, energia, barragens)
- [ ] Copiar 4 existentes (rodovias, oae, ferrovia, metrô) → v5.0
- [ ] Calcular checksums MD5 (todos 20 skills)
- [ ] Criar VERSIONS.json (prefab na `.claude/agents/`)
- [ ] Pin skills em settings.json local (skill_version_pin.agente-saneamento = v5.0)
- [ ] Deprecate v4.9 skills (mark `deprecated_at`, 30d grace period)

### Phase 4 — Observabilidade (T-12h)

- [ ] Criar tabelas Supabase: `agent_runs`, `agent_feedback`, `agent_triggers`
- [ ] Setup Grafana dashboards (custo, latência, erro rate)
- [ ] Configurar Slack alerts (#agent-ops) para falhas
- [ ] Habilitar audit logging (imutável)
- [ ] Setup APScheduler para triggers (reindex, feedback, purge)

### Phase 5 — Tiering & Fallback (T-6h)

- [ ] Validar R7 complexity score em 100 queries
- [ ] Testar R8 fallback (simular timeout, verify cascade)
- [ ] Deploy hook PreToolUse (Haiku→Sonnet→Opus transition)
- [ ] Criar fallback config per-agent (maestro.json)

### Phase 6 — Testes (T-2h)

- [ ] Teste E2E: prompt em português → agente-saneamento (S8) com phase="projeto-executivo"
- [ ] Teste cross-agent: "Qual o custo de tratamento de esgoto para 500k hab?" (deve usar S8 + S5 orcamento)
- [ ] Teste timeout recovery (R8): força timeout em Sonnet, verifica cascade para Opus
- [ ] Teste feedback loop (R9): rate 5 queries, verifica persistência em Supabase
- [ ] Teste memory purge (R10): agent_memory > 100MB, verifica limpeza

### Phase 7 — Go-live (T+0)

- [ ] Merge CLAUDE.md v5.0
- [ ] Deploy skills v5.0 para `.claude/agents/`
- [ ] Ativar RAG collections (san:v5.0:*, ene:v5.0:*, etc.)
- [ ] Ativar R1 maestro routing rules (Manta 00)
- [ ] Ativar R6–R10 loops (reranker, tiering, fallback, feedback, purge)
- [ ] Monitorar Grafana por 1h (custo, latência, erro rate)
- [ ] Anunciar time (Slack, email) com runbook de rollback

### Phase 8 — Pós-launch (24–72h)

- [ ] Coletar feedback de usuários (Slack thread)
- [ ] Validar custo vs. baseline (tiering savings)
- [ ] Monitorar taxa de erro por segmento (S6–S10)
- [ ] Ajustar complexity score weights se necessário
- [ ] Agendar gate humano (aprovação final by MN)

### Rollback

Se issues críticas:
1. Revert CLAUDE.md → v4.2
2. Desativar R6–R10 (manter R1–R5)
3. Restaurar RAG de v4.9 (backup)
4. Revert skills → v4.9 (via VERSIONS.json checksum)
5. Log post-mortem em `ROLLBACK_LOG.md`

---

## ARQUIVOS DESTE REPOSITÓRIO

```
Codex-exemplo/
├── CLAUDE.md                              # este arquivo (v5.0, master registry)
├── VERSIONS.json                          # checksums de todos 20 skills + RAG
├── ROLLBACK_LOG.md                        # log de rollbacks (append-only)
│
├── .claude/
│   ├── agents/
│   │   ├── maestro.v5.0.md                # Router canônico (R1)
│   │   ├── agente-saneamento.v5.0.md      # Novo S8 — PRIORIDADE AySA
│   │   ├── agente-energia.v5.0.md         # Novo S9 — ANEEL
│   │   ├── agente-portos.v5.0.md          # Novo S6
│   │   ├── agente-aeroportos.v5.0.md      # Novo S7
│   │   ├── agente-barragens.v5.0.md       # Novo S10
│   │   ├── agente-rodovias.v5.0.md        # Atualizado para v5.0
│   │   ├── agente-oae.v5.0.md             # Atualizado para v5.0
│   │   ├── agente-ferrovia.v5.0.md        # Atualizado para v5.0
│   │   ├── agente-metro.v5.0.md           # Atualizado para v5.0
│   │   ├── agente-claims.v5.0.md          # Atualizado para v5.0
│   │   ├── agente-contratual.v5.0.md      # Atualizado para v5.0
│   │   └── ... (8 mais: imobiliario, orcamento, modelagem, cronograma, bd, apresentacoes, advisory, arquiteto-ia)
│   │
│   ├── rag/
│   │   ├── san_v5.0/                      # Saneamento chunks (2500+)
│   │   │   ├── chunks.jsonl               # BM25 + embedding + metadata
│   │   │   └── metadata.json              # lineage, checksum, ingestão timestamp
│   │   ├── ene_v5.0/                      # Energia
│   │   ├── por_v5.0/                      # Portos
│   │   ├── aer_v5.0/                      # Aeroportos
│   │   ├── bar_v5.0/                      # Barragens
│   │   └── [rod|oae|fer|met]_v5.0/        # Verticais existentes (upgraded)
│   │
│   └── settings.json
│       {
│         "skill_version_pin": {
│           "agente-saneamento": "v5.0",
│           "agente-energia": "v5.0",
│           ... (20 agentes total)
│         },
│         "maestro_routing_rules": "R1",
│         "tiering_strategy": "R7",
│         "fallback_policy": "R8",
│         "feedback_loop": "R9",
│         "memory_purge_policy": "R10"
│       }
│
├── scripts/
│   ├── healthcheck.py                     # Valida checksums, RAG collections
│   ├── rag-reindex.py                     # Dispara reindex diário (APScheduler)
│   ├── embedding-retrain.py               # Fine-tune embedding semanal (R9)
│   ├── tiering-audit.py                   # Valida R7 complexity score
│   ├── eval-A-B.py                        # Teste A/B embedding models
│   └── rollback.py                        # Script de rollback (semi-automático)
│
└── docs/
    ├── ARQUITETURA-v5.0.md                # Detalhe dos 8 pilares
    ├── DEPLOYMENT-GUIDE.md                # Guia step-by-step deploy
    ├── ROUTING-REFERENCE.md               # Especificação R1 completa
    ├── RAG-INGESTAO.md                    # Procedure ingestão RAG
    └── TROUBLESHOOTING.md                 # Debugging runbook
```

---

## HISTÓRICO DE VERSÕES

### v5.0 (2026-07-25) — VERSÃO ATUAL

**Major features:**
- 8 pilares arquiteturais (routing determinístico, qualidade vertical, ciclo de vida, RAG híbrido, tiering automático, observabilidade, orquestração async, versionamento)
- R1 maestro expandido (3 estágios: keyword + embedding + context)
- R6–R10 novos loops (reranking, tiering, fallback, feedback, memory)
- 20 agentes (11 horizontais + 9 verticais S1..S10)
- 5 coleções RAG novas (S6–S10) + upgrade S1–S4
- Skill versionamento com checksums MD5
- Observabilidade completa (run tracking, custos, latência)
- APScheduler para background tasks (reindex, feedback, purge)

**Foco:** Escalabilidade (suporta até 50 agentes), confiabilidade (fallback inteligente), custo-efetividade (tiering automático), auditoria (run tracking imutável).

**Migrando de v4.2?** Veja `DEPLOYMENT-GUIDE.md` (Phase 1–8).

### v4.2 (2026-07-05)

- Expansão S6–S10 (Portos, Aeroportos, Saneamento, Energia, Barragens)
- 5 novos agentes verticais
- RAG básico (sem versionamento)
- Sem observabilidade estruturada

### v4.1 (anterior)

- 15 agentes (Horizontais + S1–S4)
- Routing simples (keyword matching)
- RAG inicial

---

## CONTATO & GOVERNANÇA

**Proprietário:** mneves@mantaassociados.com  
**Versão:** v5.0 (2026-07-25)  
**Aprovação:** Gate humano (MN) antes de merge  
**SLA de updates:** Patches minor < 48h; major > 2 semanas notice  
**Ticket MNT:** MNT-2026-UPGRADE-AGENTS-V5

---

## APÊNDICE — Fórmula de Complexity Score (R7)

```python
def compute_complexity(
    input_tokens: int,
    keywords_matched: int,
    rag_reranker_score_max: float,
    files_to_process: int,
    cross_agent_references: int,
    phase: str = None
) -> float:
    """
    Compute complexity score for tiering decision (R7).
    Range: [0, 10]
    """
    score = 0.0
    
    # Baseline: keywords (0–3 points)
    score += min(keywords_matched * 1.0, 3.0)
    
    # RAG reranker signal (0–2 points)
    if rag_reranker_score_max > 0.7:
        score += 2.0
    elif rag_reranker_score_max > 0.5:
        score += 1.0
    
    # File processing (0–3 points)
    score += min(files_to_process * 1.5, 3.0)
    
    # Cross-agent dependencies (0–1 point)
    if cross_agent_references > 0:
        score += 1.0
    
    # Phase multiplier (0–1 point)
    phase_multipliers = {
        "estudo-previo": 0.5,
        "projeto-basico": 0.8,
        "projeto-executivo": 1.2,
        "obra": 1.0,
        "operacao": 0.7,
        "licitacao": 1.1,
        "due-diligence": 1.3,
        "encerramento": 0.9
    }
    if phase in phase_multipliers:
        score *= phase_multipliers[phase]
    
    return min(score, 10.0)
```

---

**Fim do CLAUDE.md v5.0**
