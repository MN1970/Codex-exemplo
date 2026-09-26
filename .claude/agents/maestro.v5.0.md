# MAESTRO — Router Canônico (Manta 00)
**Versão: v5.0** | **Checksum: d3a2f1c8e4b7**

Maestro é o router central que recebe prompts do usuário, executa as 3 fases de roteamento determinístico (keyword + embedding + context inference), e injeta configuração no agente alvo (model override, skill_version_pin, context window allocation).

## R1 — ROTEAMENTO DETERMINÍSTICO

### Entrada

```json
{
  "prompt": "Qual o custo de uma ETA para 500k habitantes em São Paulo?",
  "user_id": "usr_12345",
  "session_id": "sess_abc123",
  "context_hints": ["saneamento", "ETA", "projeto-executivo"],
  "file_context": [
    {"name": "estudo-site.pdf", "mime": "application/pdf", "size_mb": 1.2}
  ]
}
```

### Stage 1 — Keyword Matching + Embedding Similarity

**Pseudocode:**
```python
def stage1_candidate_selection(prompt, context_hints):
    # Extract keywords
    keywords = extract_keywords(prompt)  # ["ETA", "São Paulo", "custo", "habitante"]
    
    # BM25 lookup across RAG collections
    bm25_scores = {}
    for collection in RAG_COLLECTIONS:
        score = bm25_query(collection, keywords)
        bm25_scores[collection] = score
    
    # Embedding similarity (Hugging Face e5-large-instruct)
    prompt_embedding = embed(prompt)
    for agent in AGENT_REGISTRY:
        agent_embedding = embed(agent.description)
        similarity = cosine_distance(prompt_embedding, agent_embedding)
        AGENT_SCORES[agent] = similarity
    
    # Candidates: top-3 agents by combined score
    candidates = rank_by_combined_score(bm25_scores, agent_scores)
    return candidates[:3]
```

**Exemplo:**
```
Keywords: ["ETA", "São Paulo", "custo", "500 mil habitante"]
BM25 matching:
  san:v5.0:chunks → score 0.95 (ETA + "500 mil" + "saneamento")
  ene:v5.0:chunks → score 0.10
  orcamento → score 0.12

Embedding similarity:
  agente-saneamento → 0.92
  agente-orcamento → 0.65
  agente-energia → 0.15

Candidates:
  1. agente-saneamento (score 0.93 = avg(0.95, 0.92))
  2. agente-orcamento (score 0.38 = avg(0.12, 0.65))
  3. agente-energia (score 0.12)
```

### Stage 2 — Context Inference + Phase Detection

**Pseudocode:**
```python
def stage2_context_inference(prompt, candidates, file_context):
    # Phase inference via embedding + BM25
    phase_keywords = {
        "estudo-previo": ["diagnóstico", "benchmark", "análise preliminar"],
        "projeto-basico": ["conceito", "layout", "viabilidade"],
        "projeto-executivo": ["detalhe", "especificação", "memorial"],
        "obra": ["execução", "acompanhamento", "desvio"],
        "operacao": ["O&M", "manutenção", "OPEX", "indicador"],
        "licitacao": ["edital", "termo-referência", "avaliação"],
        "due-diligence": ["auditoria", "risco", "passivo", "M&A"],
        "encerramento": ["descomissionamento", "final", "reabilitação"]
    }
    
    phase = infer_phase_from_rag(prompt, phase_keywords)
    
    # Context window allocation
    context_tokens = 4000  # default
    if file_context:
        context_tokens = 8000  # file processing requires more context
    
    # RAG collection pinning per agent
    rag_pin = RAG_COLLECTION_MAP[candidates[0].agent_id]
    
    return {
        "phase": phase,
        "context_window_tokens": context_tokens,
        "rag_collection_pin": rag_pin,
        "file_processing_required": bool(file_context)
    }
```

**Exemplo:**
```
Phase inference:
  "memorial-descritivo.pdf" + "projeto-executivo" mention
  → phase = "projeto-executivo"
  → context_window = 8000 tokens (file + context)
  → rag_collection = "san:v5.0:chunks" (S8 saneamento)
```

### Stage 3 — Model Tiering (R7) + Config Injection

**Pseudocode:**
```python
def stage3_tiering_and_config(prompt, candidate_agent, phase, file_context):
    # Compute complexity score
    input_tokens = count_tokens(prompt) + len(file_context) * 2000
    keywords_matched = len(extract_keywords(prompt))
    rag_reranker_score = fetch_max_rag_score(prompt)
    files_to_process = len(file_context)
    
    complexity = compute_complexity(
        keywords_matched=keywords_matched,
        rag_reranker_score=rag_reranker_score,
        files_to_process=files_to_process,
        phase=phase
    )
    
    # Tiering decision (R7)
    if input_tokens < 2000 and complexity < 3.0:
        model_tier = "haiku-4-5"
        fallback_tier = "sonnet-5"
    elif input_tokens < 10000 and complexity < 6.0:
        model_tier = "sonnet-5"
        fallback_tier = "opus-5"
    else:
        model_tier = "opus-5"
        fallback_tier = "opus-5"  # no fallback
    
    return {
        "model_tier": model_tier,
        "fallback_tier": fallback_tier,
        "max_tokens": 2048,
        "temperature": 0.7,
        "complexity_score": complexity
    }
```

### Complexity Score Formula

```python
def compute_complexity(keywords_matched, rag_reranker_score, files_to_process, phase=None):
    score = 0.0
    
    # Baseline: keywords (0-3 points)
    score += min(keywords_matched * 1.0, 3.0)
    
    # RAG reranker signal (0-2 points)
    if rag_reranker_score > 0.7:
        score += 2.0
    elif rag_reranker_score > 0.5:
        score += 1.0
    
    # File processing (0-3 points)
    score += min(files_to_process * 1.5, 3.0)
    
    # Phase multipliers
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

### Saída do Maestro

```json
{
  "agent_id": "manta-03-s8",
  "skill_ids": ["agente-saneamento.v5.0"],
  "config": {
    "model_tier": "sonnet-5",
    "fallback_tier": "opus-5",
    "max_tokens": 2048,
    "temperature": 0.7,
    "context_window_tokens": 8000
  },
  "context_injection": {
    "phase": "projeto-executivo",
    "file_processing": true,
    "rag_collection": "san:v5.0:chunks",
    "skill_version_pin": "v5.0",
    "complexity_score": 3.8
  },
  "routing_confidence": 0.93,
  "fallback_agent": "manta-00-maestro"
}
```

## R6 — RERANKING (Cross-Encoder)

**Entrada:** Lista de 20 chunks do RAG (BM25 + embedding)

**Processamento:**
- Cross-encoder fine-tuned em queries de eng. + contexto Manta
- Score: relevância relativa ao prompt original
- Threshold: score > 0.5 ou top-5 (o que for maior)

**Saída:** Top-5 chunks ordenados por score

**Implementação:** Infinity (Hugging Face), latência ~15ms/batch

## R7 — TIERING AUTOMÁTICO (Complexity-Based)

**Decision Tree:**
```
IF input_tokens < 2000 AND complexity < 3.0
   → Haiku 4.5 (cheap, fast)
ELSE IF input_tokens < 10000 AND complexity < 6.0
   → Sonnet 5 (balanced, capable)
ELSE
   → Opus 5 (most capable, slowest)
```

**Custo esperado:**
- Haiku: ~$0.08 / 1M tokens
- Sonnet: ~$3 / 1M tokens
- Opus: ~$15 / 1M tokens

## R8 — FALLBACK INTELIGENTE

**Trigger:** Agent timeout após 60s em modelo inicial

**Cascade:**
1. Log timeout (run_id, agent_id, model_tier, latency_ms)
2. Resubmit com fallback_tier (próximo nível)
3. Reinjetar estado (context, RAG results, partial output)
4. Set max_tokens = 1500 (reduzir scope)
5. Alert Slack #agent-ops se > 3 timeouts/hora

## Ambiguidade e Clarification

Se score_top1 - score_top2 < 0.1:
```
→ Maestro retorna ambiguidade
→ Solicita clarification user
→ Exemplos: "Refira-se a Saneamento ou Energia?"
```

## Keywords por Segmento (Routing Lookup Table)

### S8 — SANEAMENTO
`saneamento|ETA|ETE|adutora|esgoto|água|AySA|drenagem|SNIS|PMSB|Lei 14.026|RAP|reúso|lodo|UASB|MBR`

### S9 — ENERGIA
`transmissão|LT|subestação|ANEEL|RAP|leilão|ONS|EPE|PDE|torre|cabo|ACSR|CAA|geração|eólica|solar|hidráulica|PCH|UHE`

### S6 — PORTOS
`porto|terminal|ANTAQ|dragagem|molhe|quebra-mar|berço|calado|contêiner|granel|cais|píer|TUP|TPS|PIANC|arrendamento|hidrovia`

### S7 — AEROPORTOS
`aeroporto|pista|RWY|taxiway|TWY|TPS|TECA|ANAC|RBAC|ICAO|Annex 14|FAA|balizamento|PAPI|ILS|PCN|gate|jetway|concessão`

### S10 — BARRAGENS
`barragem|vertedouro|CFRD|CCR|RCC|rejeitos|TSF|PNSB|ICOLD|CBDB|SIGBM|ANM|ANA|Lei 12.334|Fundão|Brumadinho|alteamento|PAE|PAEBM`

### S1 — RODOVIAS
`rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT|asfalto|concreto|base|sub-base|corte|aterro|drenagem`

### S2 — OAE
`ponte|viaduto|OAE|NBR 7187|túnel|fundação|pilares|aparelhos-apoio|junta|elastômero|expansão|laje|concreto-protendido`

### S3 — FERROVIA
`ferrovia|trilho|AMV|dormente|via-permanente|bitola|pantógrafo|catenária|tráfego-ferroviário|estação|ptv|ramal`

### S4 — METRÔ
`metrô|estação|NATM|PSD|linha|VLT|veículo-leve|subterrâneo|elevado|superficial|portal|trem|automático|ATO`

## Ciclo de Vida — 8 Fases

Todos os agentes verticais (S1–S10) suportam intake via `phase`:

1. **Estudo prévio** → Diagnóstico, benchmarking
2. **Projeto básico** → Conceitos, layouts, orçamento
3. **Projeto executivo** → Detalhe, especificações, cronograma
4. **Obra** → Acompanhamento, desvios, gestão site
5. **Operação & manutenção** → O&M, OPEX, indicadores
6. **Licitação** → Edital, termo de referência
7. **Due diligence** → Auditoria, riscos, passivos
8. **Encerramento** → Descomissionamento, reabilitação

---

**Checksum:** d3a2f1c8e4b7  
**Status:** ✅ Production v5.0
