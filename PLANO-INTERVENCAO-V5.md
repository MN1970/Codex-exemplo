# Plano de Intervenção — Manta Maestro Objects & Metals v5.0

**Data**: 2026-08-02  
**Branch**: `claude/manta-maestro-objects-metals-vhfirl`  
**Status**: 🔵 Em planejamento (pré-aprovação MN)  

---

## Síntese Executiva

O **Manta Maestro Objects & Metals** é uma redesign arquitetural que transforma 20 agentes IA (soltos em SKILL.md) em **entidades de primeira classe** com:

- **Objects** — Agentes com identidade, metadados, relacionamentos, histórico de sucesso
- **Metals** — Tiers de modelo (Haiku/Sonnet/Opus) com SLAs, custos, alocação dinâmica
- **Escalação automática** — Complexidade dispara modelo superior em tempo real
- **Auditoria total** — Cada decisão registrada (quem, quando, agente, modelo, por quê, custo)

**Impacto**: 
- ↓ 35-40% custo de IA (downgrading inteligente)
- ↑ 3x capacidade de análise por consultor
- ✓ Conformidade + auditoria (trail completo para claims/arbitragem)
- 🚀 Abertura de novos segmentos em 5 dias (não 5 meses)

**Timeline**: 15 semanas até go-live (6 fases, com entrega incremental)

---

## 1. Contexto Estratégico

### Papel da Manta Associados
- **Missão**: Consultoria integrada em infraestrutura (Brasil + Argentina, 9 segmentos)
- **Diferencial**: Cobertura multi-segmento + expertise técnica + velocidade IA
- **Ambição**: Reduzir time-to-insight em 60-70% mantendo rigor técnico

### Papel do Manta Maestro
- **Hub-and-spoke** orquestrador de 20 agentes IA
- **Roteia** consultas ao especialista certo
- **Pré-processa** documentos antes do humano
- **Oferece segunda opinião** técnica instantânea
- **Documenta** decisões (auditoria)

### Gap Atual (v4.2)
```
Existe:      20 agentes operacionais
Falta:       Definição explícita de "agente como objeto"
Problema:    Tier de modelo ESTÁTICO (sempre Sonnet por padrão)
Resultado:   Desperdício de dinheiro (Opus quando Haiku bastava)
              Falta de escalação automática (complexo fica preso em Sonnet)
              Sem auditoria de decisões (qual modelo foi usado, por quê)
```

---

## 2. Definições Operacionais

### Object (Agente)
```python
Agent(Object):
    id: str                      # "Manta 03-S8"
    slug: str                    # "agente-saneamento"
    default_model_tier: str      # "Sonnet"
    specializations: List[str]   # ["ETA", "ETE", "adutora", ...]
    rag_collections: List[str]   # ["san:br:", "san:ar:", ...]
    handoff_targets: List[...]   # handoffs explícitos para outros agentes
    status: str                  # "Operational"
    success_rate: float          # histórico (0-100%)
    avg_cost_per_call: float     # $ ou tokens
```

**Exemplos**:
- **Maestro (Manta 00)**: Router, default Haiku, nenhum RAG, handoff para todos
- **Saneamento (S8)**: Técnico, default Sonnet, RAG san:br:+san:ar:, escalação ao Opus se risco > 0.8
- **Claims (Manta 01)**: Jurídico, **sempre Opus**, nenhum RAG (sobe complexidade), segundo parecer

### Metal (Tier de Modelo)
```python
Metal(Tier):
    name: str                    # "Haiku" | "Sonnet" | "Opus"
    model_id: str                # "claude-haiku-4-5-20251001"
    context_window: int          # 200k tokens
    cost_per_1k_tokens: float    # $0.80 (Haiku input) até $4 (Opus output)
    latency_p99_ms: int          # 2000ms (Haiku) até 15000ms (Opus)
    reasoning_depth: str         # "Shallow" | "Medium" | "Deep"
    suitable_for: List[str]      # ["Routing", "Summarization"] vs ["Complex Reasoning"]
```

**Matriz de Custo (baseline: 8K tokens/query)**
| Tier | Input | Output | 100 queries/mês | Notes |
|------|-------|--------|-----------------|-------|
| Haiku | $0.80/1k | $4/1k | ~$4 | Triagem, extração |
| Sonnet | $3/1k | $15/1k | ~$20 | Trabalho geral, análise |
| Opus | $15/1k | $60/1k | ~$60 | Claims complexos, decision |

---

## 3. Fluxo de Execução (com Objects & Metals)

```
ENTRADA: "AySA pediu reabilitação da Planta Norte"
    ↓
MAESTRO (Haiku, triagem)
  ├─ Detecta: saneamento (score 100), Argentina (score 80) = roteie S8
  ├─ Chama MSE: "reabilitação ETE + impacto ambiental" → complexidade 0.7
  └─ Decide: Sonnet (default S8), mas não escale Opus já (0.7 < 0.8)
    ↓
AGENTE-SANEAMENTO (Sonnet)
  ├─ Carrega RAG: san:br:, san:ar:
  ├─ Mid-analysis: "Tem interface com LT" → handoff energia (S9)
  │   └─ S9 (Sonnet): "LT fora escopo, não crítica"
  └─ Final check: Risco ambiental = 0.85 → escalação auto para Opus
    ↓
RE-ANALYSIS (Opus)
  ├─ Deep-dive técnico + ambiental + financeiro
  ├─ Produz artefato React + memorial DOCX
  └─ Log: { agent: "S8", metal: "Opus", escalation_reason: "risk > 0.8", cost: $4.20 }
    ↓
AUDITORIA: aluci-guard ✓, consist-guard ✓
    ↓
SAÍDA: Artefato + trail completo (qual modelo, quando, por quê)
```

---

## 4. Arquitetura de Dados v5.0

### Tabelas Supabase Novas

**`agents`** (20 linhas — os 20 agentes)
```sql
id | manta_code | slug | axis_1 | axis_2 | default_tier | specializations | rag_collections | status
```

**`metals`** (3 linhas — Haiku, Sonnet, Opus)
```sql
id | name | model_id | context_window | cost_per_1k_tokens_in | cost_per_1k_tokens_out | latency_p99_ms
```

**`agent_metal_mapping`** (20 linhas)
```sql
agent_id | default_metal_id | escalation_triggers | escalation_target_metal_id | reason
```
Exemplo: Saneamento → Sonnet padrão, mas {"risk > 0.8"} → Opus

**`agent_relationships`** (~30 linhas — handoffs explícitos)
```sql
source_agent_id | target_agent_id | trigger_keywords | trigger_condition | relationship_type
```
Exemplo: Saneamento → Energia, ["subestação", "LT"], "IF mention AND critical", "Handoff"

**`maestro_execution_log`** (~100k+ linhas — auditoria)
```sql
id | session_id | timestamp | input_prompt | routing_agent_id | selected_metal_id | 
complexity_score | escalation_occurred | execution_time_ms | input_tokens | output_tokens | 
cost_usd | quality_score | success | error_message | handoff_chain (JSONB)
```

### Metal Selection Engine (MSE)

Pseudocódigo:
```python
def select_metal(prompt, agent_object) -> Metal:
    # 1. Detecta sinais: multi_domain, high_stakes, ambiguous, novel
    complexity_score = compute_complexity(prompt)
    
    # 2. Escalação heurística
    if complexity_score > 0.75:
        return agent_object.escalation_target_metal or "Opus"
    elif complexity_score > 0.50:
        return "Sonnet"
    else:
        return agent_object.default_metal
    
    # 3. Consulta histórico (qual tier funcionou melhor para problema similar?)
    similar_cases = query_execution_log(agent_id, similarity_to_prompt)
    success_rates = {metal: avg(success) for metal in ["Haiku", "Sonnet", "Opus"]}
    
    # 4. Custo-benefício (trade-off entre sucesso e dinheiro)
    selected = max_score(
        [("Haiku", 0.9 * success["Haiku"] - 0.1 * cost["Haiku"]),
         ("Sonnet", 0.9 * success["Sonnet"] - 0.1 * cost["Sonnet"]),
         ("Opus", 0.9 * success["Opus"] - 0.1 * cost["Opus"])]
    )
    return selected

def execute_with_escalation(agent, metal, prompt):
    result = call_model(metal.model_id, prompt)
    
    if detect_low_confidence(result):  # "I'm not sure", "escalate"
        next_metal = metal.fallback_to
        log_escalation(agent.id, metal.name, next_metal)
        result = call_model(next_metal.model_id, prompt)
    
    return result
```

---

## 5. Plano de Implementação (6 Fases, 15 semanas)

| Fase | Objetivo | Semanas | Entrega |
|------|----------|---------|---------|
| 1 | Design schema v5.0 | 2 | schema.sql, agents.json, agent_metal_mapping.json |
| 2 | Implementar DB | 2 | Tabelas criadas, dados seedados, índices otimizados |
| 3 | Metal Selection Engine | 2 | MSE code, heurísticas v1, 50+ testes |
| 4 | Integrar Maestro | 2 | Maestro sem hardcodes, logging, shadow mode |
| 5 | Auditoria & Dashboard | 2 | Execution log views, dashboard, relatório de ROI |
| 6 | Feedback & Otimização | 2 | Feedback loop fechado, MSE v1.1, go-live |

**Caminho crítico**: 1 → 2 → 3 → 4 → 5 → 6 (sequencial)  
**Parallelização possível**: Fases 1 e 3 podem rodar em paralelo  
**Go-live**: Semana 15, após aprovação MN em Fase 5

---

## 6. ROI Estimado

### Custos
- **Desenvolvimento**: ~450 horas (3 engenheiros × 15 semanas)
- **Infraestrutura**: Supabase + cloud (novo dashboard) = ~$2K/ano
- **Manutenção**: ~10 horas/mês (tuning MSE, gestão de feedback)

### Benefícios (ano 1)
- **Economia de IA**: 35-40% redução em LLM spend
  - Baseline: 9 segmentos × 100 queries/mês × $20 (Sonnet) = $21.6K/ano
  - Com tiering: ~$13K/ano (downgrade agressivo a Haiku/Sonnet, pouca escalação Opus)
  - **Economia**: ~$8.6K/ano
  
- **Aumento de produtividade**: 3x análises por consultor
  - 5 consultores × 3x = 15 projetos adicionais/ano
  - Se margem por projeto = R$ 5K, ganho = R$ 75K/ano
  
- **Redução de risco**: Auditoria + escalação auto
  - Menos claims por "alucinação IA" = reduz indenização em ~10-20K/ano

**Total Year 1**: ~$8.6K + $75K + $15K = **~$98.6K benefício** vs ~$50K desenvolvimento  
**Payback**: ~6 meses

---

## 7. Próximos Passos (próximas 2 semanas)

### SEMANA 1
- [ ] Apresentar este plano ao time (arquiteto, backend, product, MN)
- [ ] Validar schema com DBA
- [ ] Listar 20 agentes com metadados (do CLAUDE.md + SKILL.md)
- [ ] Prototipar MSE em notebook (20 casos de teste)

### SEMANA 2
- [ ] Refinar schema após feedback
- [ ] Desenhar agent_relationships (~30 linhas, extrair de SKILL.md)
- [ ] Especificar cost model por metal (validar com Anthropic pricing)
- [ ] **Apresentar v2 ao MN** ← **GATE DE APROVAÇÃO**

---

## 8. Documentos Criados Nesta Branch

```
.
├── CLAUDE.md (existente, sem alteração)
├── PLANO-INTERVENCAO-V5.md (este arquivo)
├── maestro-objects-metals.md (especificação técnica detalhada)
├── maestro-objects-metals.json (schema estruturado, 20 agents + 3 metals)
├── sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md
│   └─ (será atualizado a v3.0 após aprovação)
└── docs/
    ├── DEPLOY-v4.2.md (existente)
    └── DEPLOY-v5.0.md (novo, após Phase 1)
```

---

## Aprovação & Próximas Ações

```
[ ] Revisão por MN (este documento)
    ↓
[ ] Feedback incorporado
    ↓
[ ] Aprovação para iniciar Fase 1
    ↓
[ ] Criação de épica no Jira: MNT-2026-OBJECTS-METALS
    ↓
[ ] Início Semana 1: Design + validação schema
```

**Responsáveis**:
- **Arquitetura**: Mauricio Neves (MN) — aprovação + roadmap
- **Backend**: Engenheiro Supabase — implementação DB
- **IA/MSE**: Engenheiro IA — Metal Selection Engine
- **Ops**: DevOps — CI/CD, monitoring, alertas

---

**Documento Final**. Pronto para discussão com time e aprovação MN.

Data: 2026-08-02  
Versão: 1.0
