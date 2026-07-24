# CAG — Custom Agent Group (v5.0 Prototipagem)

Orquestração inteligente com ML para o Manta Maestro.

**Status**: 🚧 Prototipagem (branch `claude/manta-maestro-cag-ml-8wdrg4`)  
**Ticket**: MNT-2026-CAG-ML  
**Data**: 2026-07-22

---

## Estrutura

```
cag/
├── schemas/
│   └── cag_schema.sql              # Schema Supabase
├── ml/
│   ├── __init__.py
│   ├── intent_classifier.py        # Intent Classification + Agent Selection
│   └── (futura: embedding_service.py, feedback_processor.py)
├── orchestrator/
│   ├── __init__.py
│   ├── response_ranker.py          # Response Ranking + Synthesis
│   └── cag_orchestrator.py         # Orquestrador principal (TODO)
├── tests/
│   └── test_cag_e2e.py             # Testes end-to-end
├── README.md                        # Este arquivo
└── requirements.txt                 # Dependências Python
```

---

## Setup Rápido

### 1. Instalar dependências

```bash
pip install -r cag/requirements.txt
```

### 2. Aplicar schema Supabase

```bash
# Via CLI Supabase
cd supabase/migrations/
cp ../../cag/schemas/cag_schema.sql .
supabase db push

# OU via psql direto
psql "$SUPABASE_DB_URL" -f cag/schemas/cag_schema.sql
```

### 3. Verificar schema

```sql
-- No Supabase console
SELECT COUNT(*) FROM cag_intent_classes;  -- Esperado: 7 linhas
SELECT COUNT(*) FROM cag_agent_pool;      -- Esperado: 8 linhas
```

---

## Como Usar

### Intent Classification

```python
from cag.ml.intent_classifier import IntentClassifier, AgentSelector

# 1. Setup
intent_classes = {
    'saneamento': {
        'display_name': 'Saneamento',
        'description': 'Água, esgoto, drenagem',
        'keywords': ['saneamento', 'ETA', 'ETE', 'adutora'],
        'primary_agents': ['agente-saneamento'],
        'secondary_agents': ['agente-energia']
    },
    # ... mais intents
}

# 2. Classificar query
classifier = IntentClassifier(intent_classes, threshold=0.6)
query = "Qual é a norma para ETA?"
prediction = classifier.classify(query)

print(f"Primary: {prediction.primary_intent} ({prediction.confidence:.2f})")
# Output: Primary: saneamento (0.92)

# 3. Selecionar agentes
agent_pool = {
    'agente-saneamento': {},
    'agente-energia': {},
    # ...
}
selector = AgentSelector(agent_pool, intent_classes)
agents = selector.select_agents(prediction)

for agent in agents:
    print(f"  {agent.agent_slug}: {agent.score:.2f}")
# Output:
#   agente-saneamento: 0.92
#   agente-energia: 0.58
```

### Response Ranking & Synthesis

```python
from cag.orchestrator.response_ranker import (
    ResponseRanker, 
    ResponseSynthesizer, 
    AgentResponse
)

# 1. Simular respostas de agentes
responses = [
    AgentResponse(
        agent_slug="agente-saneamento",
        agent_name="Saneamento",
        response_text="ETA conforme NBR 12.211...",
        confidence=0.92,
        sources=["NBR 12.211", "Lei 14.026"],
        latency_ms=2500
    ),
    AgentResponse(
        agent_slug="agente-energia",
        agent_name="Energia",
        response_text="Subestação conforme ANEEL...",
        confidence=0.85,
        sources=["ANEEL", "NBR 5422"],
        latency_ms=3100
    )
]

# 2. Rankear
ranker = ResponseRanker()
query = "Qual é a norma para ETA e subestação?"
rankings = ranker.rank_responses(query, responses)

for rank in rankings:
    print(f"Rank {rank.rank}: {rank.agent_slug} (score: {rank.score:.2f})")
# Output:
# Rank 1: agente-saneamento (score: 0.92)
# Rank 2: agente-energia (score: 0.85)

# 3. Sintetizar
synthesizer = ResponseSynthesizer()
agent_responses_dict = {
    "agente-saneamento": responses[0],
    "agente-energia": responses[1]
}
final_response = synthesizer.synthesize(query, rankings, agent_responses_dict)

print(final_response)
# Output: resposta integrada com ambos agentes
```

### Orquestrador End-to-End

```python
from cag.ml.intent_classifier import IntentClassifier, AgentSelector
from cag.orchestrator.cag_orchestrator import CAGOrchestrator

# Setup (ver exemplos acima)
classifier = IntentClassifier(intent_classes)
selector = AgentSelector(agent_pool, intent_classes)
orchestrator = CAGOrchestrator()

# Execute
query = "Projeto saneamento com subestação"
prediction = classifier.classify(query)
agents = selector.select_agents(prediction)

# Simular respostas dos agentes (em produção: chamar agentes reais)
agent_responses_dict = {
    agent.agent_slug: AgentResponse(...)
    for agent in agents
}

# Orquestrar: rank + síntese
result = await orchestrator.orchestrate(
    query=query,
    selected_agents=[agent.agent_slug for agent in agents],
    agent_responses_dict=agent_responses_dict
)

print(result['final_response'])
print(f"Sources: {result['sources']}")
```

---

## Testes

```bash
# Testes unitários
pytest cag/tests/test_cag_e2e.py -v

# Com coverage
pytest cag/tests/ --cov=cag --cov-report=html
```

---

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│ 1. QUERY USUÁRIO                                            │
│    "Saneamento + energia em 1 projeto"                      │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. INTENT CLASSIFIER (cag/ml/intent_classifier.py)          │
│    • Keyword match: "saneamento" ✓, "energia" ✓             │
│    • Semantic score: Claude embedding                       │
│    → IntentPrediction(primary="saneamento", conf=0.92, ...) │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. AGENT SELECTOR                                           │
│    • Primary agents: agente-saneamento (0.92)               │
│    • Secondary agents: agente-energia (0.85)                │
│    → [agente-saneamento, agente-energia]                    │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. EXECUTE AGENTS (PARALELO)                                │
│    • agente-saneamento ─→ busca RAG (san:*) ──→ resposta 1  │
│    • agente-energia     ─→ busca RAG (ene:*) ──→ resposta 2  │
│    (tempo: max(2.5s, 3.1s) = 3.1s)                          │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. RESPONSE RANKER (cag/orchestrator/response_ranker.py)    │
│    • Claude LLM-as-a-judge compara 2 respostas              │
│    • Scores: relevância, completude, acurácia               │
│    → [RankedResponse(rank=1, agent_sanitizacao, score=0.92)]│
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. RESPONSE SYNTHESIZER                                     │
│    • Claude integra top-2 respostas                         │
│    • Mantém citações de fontes                              │
│    → resposta final coerente                                │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. LOG & FEEDBACK (Supabase)                                │
│    • cag_feedback_logs: query, agentes, user_rating         │
│    • cag_agent_scores: atualiza matriz de hits/misses       │
│    • cag_routing_metrics: snapshot diário                   │
└─────────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ RESULTADO FINAL: resposta integrada + fontes + scores       │
└─────────────────────────────────────────────────────────────┘
```

---

## Métricas & Monitoramento

### Dashboards (Supabase)

Queries úteis para monitoramento:

```sql
-- Acurácia por agente (hoje)
SELECT agent_slug, 
       correct_selections, 
       incorrect_selections,
       ROUND(100.0 * correct_selections / NULLIF(correct_selections + incorrect_selections, 0), 2) AS accuracy_pct
FROM cag_routing_metrics
WHERE date_bucket = CURRENT_DATE
ORDER BY accuracy_pct DESC;

-- Intent distribution (últimos 7 dias)
SELECT query_intent, 
       COUNT(*) AS count,
       ROUND(AVG(CAST(user_rating AS NUMERIC)), 2) AS avg_rating
FROM cag_feedback_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY query_intent
ORDER BY count DESC;

-- Agentes mais usados
SELECT agent_slug, 
       COUNT(*) AS times_selected,
       ROUND(AVG(confidence_score), 2) AS avg_confidence
FROM cag_agent_scores
WHERE selected = TRUE
GROUP BY agent_slug
ORDER BY times_selected DESC;
```

---

## Próximos Passos (TODO)

- [ ] **Fine-tuning do Intent Classifier**
  - Treinar com histórico de queries reais (Manta)
  - Fine-tune distilbert ou equivalente

- [ ] **Integração com Maestro v4.2**
  - Shadow mode: CAG roda, mas v4.2 decide (logs de discordância)
  - Fallback: se CAG falhar, usar v4.2

- [ ] **Embedding Service**
  - Integração com Anthropic Embeddings (quando disponível)
  - Ou equivalente (OpenAI, HuggingFace)

- [ ] **Feedback Loop**
  - UI para usuário marcar "resposta foi útil?"
  - Retraining automático do classifier

- [ ] **Performance**
  - Caching de queries comuns
  - Latência target: <5s end-to-end

- [ ] **Testes com queries reais**
  - Pull histórico de 100+ queries do SharePoint
  - Comparar CAG vs v4.2 em casos ambíguos

---

## Referências

- **Arquitetura**: `/sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`
- **CLAUDE.md master**: `CLAUDE.md` neste repo
- **Agent definitions**: `.claude/agents/agente-*.md`
- **RAG v4.2**: `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`

---

## Contato

- **Ticket**: MNT-2026-CAG-ML
- **Branch**: `claude/manta-maestro-cag-ml-8wdrg4`
- **Autor**: Claude Code (2026-07-22)
