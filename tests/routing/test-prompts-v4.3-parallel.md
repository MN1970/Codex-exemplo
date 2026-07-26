# Prompts de Teste — Maestro v4.3 (8-Agent Parallel Routing)

**Objetivo**: Validar que Maestro roteia corretamente para a pool de 8 agentes Sonnet em paralelo.

**Metodologia**: Para cada prompt, verificar:
1. ✓ Quais agentes foram acionados (devem ser ≥2 para justificar paralelização)
2. ✓ Prioridade: S8/S9 (saneamento/energia) aparecem primeiro?
3. ✓ Latência: resposta em 3-5s (vs. 30-45s sequencial)
4. ✓ Cobertura: todas as disciplinas mencionadas foram cobertas?

---

## Prompts de Teste (4 casos multi-disciplina)

### TESTE 1: Saneamento + Energia (PRIORITY)
**Input**:
```
Projeto de ETA (Estação de Tratamento de Água) com areia quartzosa
e carvão ativado, servindo 150 mil habitantes na região metropolitana
de São Paulo. A água captada vem de rio próximo à subestação de 345 kV.
Preciso de:
- Estimativa de custo
- Cronograma executivo
- Análise de viabilidade (potencial de negócio)
- Parecer legal sobre concessão AySA vs. privado
```

**Esperado**:
- ✓ **Manta-03-S8** (agente-saneamento) — PRIORITY (200)
- ✓ **Manta-03-S9** (agente-energia) — PRIORITY (200)
- ✓ **Manta-05** (orcamento)
- ✓ **Manta-07** (cronograma)
- ✓ **Manta-02** (contratual)
- ✓ **Manta-13** (bd — viabilidade)
- ⏱ Tempo esperado: 3-5s

**Veredito**: PASS se S8/S9 aparecem primeiro + ≥5 agentes + latência < 6s

---

### TESTE 2: Energia + Imobiliário (Subestação + Condomínio)
**Input**:
```
Projeto de subestação 138/13,8 kV em área urbana, com
possibilidade de desenvolvimento imobiliário no terreno vizinho
(aproveitando acesso, infraestrutura).
Necessário:
- Projeto de transmissão (LT 138 kV de acesso)
- Estimativa orçamentária (capex SE)
- Análise de viabilidade da parceria público-privada
- Apresentação executiva para stakeholders
- Cronograma (SAE + obras civis)
```

**Esperado**:
- ✓ **Manta-03-S9** (agente-energia) — PRIORITY (200)
- ✓ **Manta-04** (imobiliario)
- ✓ **Manta-05** (orcamento)
- ✓ **Manta-07** (cronograma)
- ✓ **Manta-14** (apresentacoes)
- ✓ **Manta-02** (contratual — PPP)
- ⏱ Tempo esperado: 3-5s

**Veredito**: PASS se S9 primeiro + cobertura de energia E imob + latência OK

---

### TESTE 3: Saneamento (ETE + Reutilização)
**Input**:
```
Estação de Tratamento de Esgoto (ETE) no interior de São Paulo,
com tratamento avançado (MBR + RO) para reuso industrial.
Preciso de:
- Projeto técnico (NBR 12.209, 9.651)
- Orçamento com análise de OPEX/CAPEX
- Cronograma de 36 meses (planning + exec + startup)
- Viabilidade comercial (venda de água reciclada)
- Documentação contratual (concessão municipal)
```

**Esperado**:
- ✓ **Manta-03-S8** (agente-saneamento) — PRIORITY (200)
- ✓ **Manta-05** (orcamento)
- ✓ **Manta-07** (cronograma)
- ✓ **Manta-13** (bd — viabilidade comercial)
- ✓ **Manta-02** (contratual)
- ⏱ Tempo esperado: 3-5s

**Veredito**: PASS se S8 primeiro + todas 5 disciplinas cobertas

---

### TESTE 4: Licitação Multi-Disciplina (Rodovia + Ponte + Drenagem)
**Input**:
```
Licitação de concessão de rodovia BR-116 trecho São Paulo-RJ,
inclui construção de OAE (ponte sobre rio de 150m) e
sistema de drenagem urbana na região metropolitana.
Necessário:
- Orçamento detalhado (SICRO + BDI)
- Cronograma macro e crítico (54 meses)
- Parecer legal (Lei 8.987 + licitação 14.133)
- Análise de viabilidade (receita de pedágios vs. investimento)
- Apresentação técnica para lance no leilão
```

**Esperado**:
- ✗ **NÃO dispara S8/S9** (não é prioridade)
- ✓ **Manta-05** (orcamento) — 100 (alta)
- ✓ **Manta-07** (cronograma) — 100 (alta)
- ✓ **Manta-02** (contratual) — 90
- ✓ **Manta-13** (bd) — 70
- ✓ **Manta-14** (apresentacoes) — 50
- ⏱ Tempo esperado: 3-5s

**Veredito**: PASS se cobertura OK + S8/S9 NÃO aparecem (não aplicável)

---

## Critérios de Aceitação

### ✓ PASS Geral
- [ ] Teste 1: S8/S9 aparecem primeiro, latência < 6s, ≥5 agentes
- [ ] Teste 2: S9 priorizado, imob cobertura, latência < 6s
- [ ] Teste 3: S8 priorizado, todas 5 disciplinas, latência < 6s
- [ ] Teste 4: S8/S9 ausentes (correto), 5+ agentes, latência < 6s

### Métricas Esperadas
| Métrica | Target | Limite |
|---------|--------|--------|
| Latência (p50) | 3s | < 6s |
| Latência (p95) | 4.5s | < 7s |
| Taxa sucesso agentes | ≥95% | < 80% = FAIL |
| Cobertura disciplinas | 100% | < 90% = FAIL |

---

## Como Executar

### Via CLI
```bash
# Teste 1
maestro-test --prompt "TESTE 1: Saneamento + Energia..." --pool-size 8 --mode parallel

# Todos os testes
maestro-test --suite parallel-routing-v4.3 --output-json results.json
```

### Via Code (Python)
```python
from maestro_parallel_executor import MaestroParallelExecutor

executor = MaestroParallelExecutor()
result = await executor.execute_parallel(TESTE_1_INPUT)

print(f"Agents triggered: {len(result['results'])}")
print(f"Duration: {result['total_duration_ms']:.1f}ms")
print(f"Priority agents: {[r['agent_name'] for r in result['ranked_by_relevance'][:2]]}")
```

---

## Observações

1. **Paralelização não é obrigatória** para queries de disciplina única
2. **S8/S9 sempre prioritários** quando mencionam saneamento/energia
3. **Timeout por agente**: 120s — se exceder, retorna "timeout" status
4. **Síntese**: top-3 agentes ranqueados por priority + sucesso
5. **Logging**: todos os resultados em `maestro_execution_logs` (Supabase)

---

**Última atualização**: 2026-07-26  
**Versão**: v4.3 (Maestro Parallel Pool)  
**Ticket**: MNT-2026-MAESTRO-PARALELO-8-SONNET
