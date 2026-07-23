# Padrões de Otimização — Manta Maestro (v1.0)

Guia de implementação dos padrões de velocidade, paralelismo e otimização de tokens para agentes Manta (Maestro + S6-S10).

**Última atualização:** 2026-07-23  
**Versão:** 1.0.0  
**Referência:** Baseado em `docs/MODEL-SPEEDS-PARALLEL-TOKENS.md`

---

## 1. Otimizações por Agente Vertical (S6-S10)

### Saneamento (S8)

| Tarefa | Modelo | Workers | Caching | Batch? |
|--------|--------|---------|---------|--------|
| Análise 5 ETAs/ETEs | Sonnet | 5 | Lei 14.026 | Não |
| DD 20+ concessionárias | Opus | N/A | SNIS refs | **Sim** (50% off) |
| Roteamento inicial | Haiku | N/A | N/A | Não |

**Contextos cacheaváveis:**
- Lei 14.026/2020 + ANA NRs (100KB)
- NBR 12211-12218 (normas ETA/ETE)
- Metodologia SNIS/PMSB

**Ganho esperado:** 4-5x mais rápido em análise paralela; 85-90% redução em input_tokens com caching

---

### Portos (S6)

| Tarefa | Modelo | Workers | Caching | Batch? |
|--------|--------|---------|---------|--------|
| Análise 5 layouts de terminal | Sonnet | 5 | ANTAQ/PIANC | Não |
| DD 15+ concessões portuárias | Opus | N/A | Normas dragagem | **Sim** |
| Classificação (TUP/arrendado) | Haiku | N/A | N/A | Não |

**Contextos cacheaváveis:**
- Lei 12.815/2013 + ANTAQ (50KB)
- PIANC reports (dragagem, amarração)
- Batimetria/sondagem templates

**Ganho esperado:** 4-5x paralelismo; 85% redução input_tokens

---

### Aeroportos (S7)

| Tarefa | Modelo | Workers | Caching | Batch? |
|--------|--------|---------|---------|--------|
| Análise 5 pistas + TPS | Sonnet | 5 | RBAC 154 / ICAO | Não |
| DD 20+ concessões aeroportuárias | Opus | N/A | FAA ACs | **Sim** |
| Roteamento categoria | Haiku | N/A | N/A | Não |

**Contextos cacheaváveis:**
- RBAC 154 + ICAO Annex 14 (75KB)
- FAA AC 150/5300-13 (pavimentos FAA FAARFIELD)
- Normas DECEA/ICA 100-12

**Ganho esperado:** 4-5x paralelismo; 85% economia com cache

---

### Energia (S9)

| Tarefa | Modelo | Workers | Caching | Batch? |
|--------|--------|---------|---------|--------|
| Análise 5 LTs + subestações | Sonnet | 5 | ANEEL REN | Não |
| DD 20+ leilões transmissão ANEEL | Opus | N/A | IEEE 738, NBR 5422 | **Sim** |
| Roteamento (LT vs SE vs geração) | Haiku | N/A | N/A | Não |

**Contextos cacheaváveis:**
- ANEEL REN + procedimentos ONS (100KB)
- NBR 5422 + IEEE Std 738 (cálculos)
- EPE R1-R5 methodology (75KB)

**Ganho esperado:** 4-5x paralelismo; 90% economia com cache

---

### Barragens (S10)

| Tarefa | Modelo | Workers | Caching | Batch? |
|--------|--------|---------|---------|--------|
| Análise 5 barragens (hidro + rejeitos) | Sonnet | 5 | ICOLD/Lei 12.334 | Não |
| DD 15+ TSFs / portfólio mineradora | Opus | N/A | PNSB/CBDB | **Sim** |
| Classificação DPA/risco | Haiku | N/A | N/A | Não |

**Contextos cacheaváveis:**
- Lei 12.334 + Lei 14.066/2020 (75KB)
- ICOLD Bulletins (194, 164)
- CBDB + NBR 13028 (50KB)

**Ganho esperado:** 4-5x paralelismo; 90% economia com cache

---

## 2. Implementação: Exemplo Python (ThreadPoolExecutor)

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import anthropic

client = anthropic.Anthropic()

# ✅ Análise paralela de 5 ETAs (Saneamento S8)
def analyze_eta(doc: str, index: int):
    """Analisar 1 ETA com Sonnet"""
    return client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": "Lei 14.026 + NBR 12211-12218...",
                "cache_control": {"type": "ephemeral"}  # ✅ Cache 1h
            }
        ],
        messages=[
            {"role": "user", "content": f"Analise ETA {index}:\n{doc}"}
        ]
    )

# Correr 5 ETAs em paralelo (vs ~30s sequencial → ~6s paralelo)
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(analyze_eta, doc, i)
        for i, doc in enumerate(eta_documents)
    ]
    results = [f.result() for f in as_completed(futures)]
```

---

## 3. Implementação: Batch API (50% desconto)

```python
# ✅ DD de 20+ concessionárias (Saneamento)
batch_requests = [
    {
        "custom_id": f"dd-conc-{company}",
        "params": {
            "model": "claude-opus-4-8",
            "max_tokens": 3000,
            "system": [
                {
                    "type": "text",
                    "text": "Lei 14.026 + SNIS metodologia",
                    "cache_control": {"type": "ephemeral"}  # Cache base de leis
                }
            ],
            "messages": [
                {"role": "user", "content": f"DD: {company} — analise SNIS KPIs, tarifa, subsidio cruzado"}
            ]
        }
    }
    for company in companies  # 20+ concessionárias
]

# Submeter batch
batch = client.beta.messages.batches.create(requests=batch_requests)

# Coletar resultados (processamento noturno)
while batch.processing_status == "in_progress":
    batch = client.beta.messages.batches.retrieve(batch.id)
    time.sleep(30)  # Esperar

for result in client.beta.messages.batches.results(batch.id):
    print(result.result.message.content)
```

---

## 4. Token Counting (estimar antes de enviar)

```python
# ✅ Contar tokens ANTES de enviar DD de 50+ documentos
cost_estimate = client.messages.count_tokens(
    model="claude-sonnet-5",
    system="Lei 14.026...",
    messages=[{"role": "user", "content": large_dd_document}]
)

print(f"Input tokens: {cost_estimate.input_tokens}")
print(f"Custo estimado: ${cost_estimate.input_tokens / 1_000_000 * 3:.2f}")

if cost_estimate.input_tokens > 50_000:
    # ⚠️ Muito grande! Comprimir com Haiku
    print("Documento > 50K tokens — ativando compressão...")
    compressed = compress_document(large_dd_document)
    # Depois usar compressed para análise Sonnet
```

---

## 5. Decisão: Quando usar cada padrão

### Paralelismo (ThreadPoolExecutor)
✅ **Use quando:**
- Múltiplos documentos **independentes** (5-10 docs)
- Análise simultânea é possível (sem dependências)
- Latência total importa (vs. apenas throughput)

❌ **Não use quando:**
- 1 documento único (não há paralelismo a explorar)
- Documentos têm dependências (doc B depende de análise de doc A)

### Batch API
✅ **Use quando:**
- 1K+ requisições ou documentos
- Custo importa (50% desconto)
- Latência não importa (processamento noturno/background OK)

❌ **Não use quando:**
- < 100 requisições (overhead não compensa)
- Resultado precisa **imediato** (batches levam 30min-24h)

### Prompt Caching
✅ **Use quando:**
- Contexto base (lei, norma, padrão) é reutilizado N vezes
- N ≥ 5 requisições (ROI do cache)
- Contexto é > 10K tokens (economia fica relevante)

❌ **Não use quando:**
- Contexto muda a cada requisição
- N < 3 (cache overhead não compensa)

### Compressão (Haiku → Sonnet)
✅ **Use quando:**
- Documento > 50K tokens
- Parte substancial é "ruído" (preâmbulos, anexos)

❌ **Não use quando:**
- Documento < 30K tokens (economia marginal)
- Todo conteúdo é relevante (não há compressão)

---

## 6. Checklist de Implementação

Para cada agente S6-S10:

- [ ] Identificar tarefas parallelizáveis (análise de múltiplos docs)
- [ ] Implementar ThreadPoolExecutor (5-10 workers)
- [ ] Identificar contextos reutilizáveis (leis, normas > 5 usos)
- [ ] Ativar `cache_control: {"type": "ephemeral"}` em system prompts
- [ ] Para 100+ reqs: implementar Batch API
- [ ] Usar `count_tokens()` antes de enviar docs > 50K
- [ ] Testar latência paralela vs. sequencial
- [ ] Documentar economia (% tokens economizados com cache)

---

## 7. Benchmarks Esperados (Manta Maestro)

### Roteamento Maestro (100 mensagens)
| Abordagem | Tempo | Custo |
|-----------|-------|-------|
| Sequencial Haiku | ~30s | $0.10 |
| **Paralelo Haiku (20 workers)** | **~2s** | **$0.10** |

**Ganho:** 15x mais rápido, mesmo custo ✅

### Análise de 10 documentos (S8 Saneamento)
| Abordagem | Tempo | Custo |
|-----------|-------|-------|
| Sequencial Sonnet | ~50s | $1.50 |
| Paralelo Sonnet (5 workers) | ~12s | $1.50 |
| Paralelo + cache Lei 14.026 | ~12s | **$0.80** | 

**Ganho:** 4x mais rápido + 45% economia com cache ✅

### DD de 50 empresas (S8 Saneamento)
| Abordagem | Tempo | Custo |
|-----------|-------|-------|
| Opus sequencial | ~5min | $7.50 |
| Opus + Batch API | ~30min (noturno) | **$3.75** |

**Ganho:** 50% desconto; latência aceitável se noturno ✅

---

## 8. Referências

- **claude-api skill:** https://code.claude.com/ (Tool Runner, Batch API)
- **MODEL-SPEEDS-PARALLEL-TOKENS.md:** Guia detalhado de modelos, velocidades e tokens
- **Anthropic SDK:** https://github.com/anthropic-ai/anthropic-sdk-python
- **CLAUDE.md:** Master registry de agentes Manta

---

**Status de implementação:** Capacidades adicionadas aos agentes S6-S10 (2026-07-23)  
**Próximo passo:** Criar exemplos de código working end-to-end (Python + TypeScript)
