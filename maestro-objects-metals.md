# Manta Maestro — Objects & Metals v5.0

**Documento de Clarificação Estratégica**

Versão: **5.0-draft** (2026-08-02)  
Autor: Mauricio Neves  
Status: **Em Planejamento**  
Branch: `claude/manta-maestro-objects-metals-vhfirl`

---

## Executive Summary

Este documento formaliza a **estrutura de objetos (agentes)** e **metadados operacionais (modelos, tiers, custos)** do Manta Maestro, alinhando-os aos objetivos estratégicos da Manta Associados.

O Manta Maestro é um sistema de **20 agentes IA especializados** que amplifica a capacidade de análise técnica, financeira e contratual da Manta em 10 segmentos de infraestrutura (Rodovias, OAE, Ferrovia, Metrô, Portos, Aeroportos, Saneamento, Energia, Barragens + transversal). 

**Objetivo da intervenção**: deixar explícito, em forma consumível por sistemas, quais agentes existem (objects), como eles são configurados (metals), e como isso se traduz em valor de negócio.

---

## 1. Papel Estratégico da Manta Associados

**Missão**: consultoria integrada em infraestrutura (Brasil + Argentina), cobrindo estudo prévio até operação & manutenção.

**Diferencial competitivo**:
- Cobertura multi-segmento (9 verticais operacionais).
- Expertise técnica integrada (engenharia + direito + finanças).
- Velocidade de análise aumentada por IA.

**Ambição do Maestro**: reduzir **time-to-insight** em 60-70% (vs. análise manual) mantendo qualidade de parecer técnico.

---

## 2. Papel Operacional do Manta Maestro

O Maestro é **middleware IA** que:

1. **Roteia consultas** para o agente certo (Maestro 00 — router).
2. **Especializa análise** por segmento/disciplina (20 agentes).
3. **Escala modelos** conforme complexidade (Haiku → Sonnet → Opus).
4. **Integra conhecimento** via RAG (Supabase) de 100+ fontes normativas.
5. **Entrega artefatos** (memoriais DOCX, artefatos React, orçamentos XLSX).

**Não substitui** o consultor; **amplia** sua capacidade de síntese e verificação.

---

## 3. Objetivos Principais

### Nível de Negócio
- [ ] Reduzir custo por análise em 40% (automação de síntese).
- [ ] Aumentar número de projectos analisados por consultor em 2-3x.
- [ ] Melhorar cobertura de pequenos projetos (antes não economicamente viáveis).
- [ ] Abrir novo mercado de "diagnóstico rápido" (24h turnaround).

### Nível de IA/Operacional
- [ ] 20 agentes operacionais, cada um especializado em 1 segmento + 8 fases.
- [ ] 90%+ de routing correto (teste de prompts).
- [ ] RAG completo com 500+ documentos de referência normativa.
- [ ] Integração com SP, Supabase, Claude API.

### Nível Técnico (Objects & Metals)
- [ ] Definição canônica de cada agente: nome, código, tier padrão, handoffs, RAG collection.
- [ ] Matriz de modelo x carga: quando usar Haiku vs. Sonnet vs. Opus.
- [ ] Custos operacionais por segmento (tokens/mês, custo estimado).
- [ ] SLA de resposta por tier (Haiku: <5s, Sonnet: <30s, Opus: <2min).

---

## 4. Objects — Registro Canônico dos 20 Agentes

### 4.1 Estrutura de Dados (JSON Schema)

```json
{
  "object": {
    "code": "Manta 03-S8",
    "name": "agente-saneamento",
    "aliases": ["agente-08", "saneamento"],
    "tier_default": "Sonnet",
    "tier_escalation": {
      "intake_simple": "Haiku",
      "project_phase": "Sonnet",
      "financial_risk": "Opus",
      "multi_layer_claim": "Opus"
    },
    "domain": "Saneamento",
    "coverage": {
      "segments": ["ETA", "ETE", "adução", "drenagem urbana", "resíduos"],
      "phases": 8,
      "jurisdictions": ["Brasil", "Argentina (prioridade AySA)"]
    },
    "rag_collection": {
      "slug": "san",
      "storage_prefix": "san:",
      "sub_prefixes": ["san:br:", "san:ar:"],
      "source_count": 120,
      "update_frequency": "quarterly"
    },
    "handoffs": [
      { "trigger": "menção a cost", "to": "Manta 05 (orçamento)" },
      { "trigger": "timeline/cronograma", "to": "Manta 07 (cronograma)" },
      { "trigger": "claim jurídico", "to": "Manta 01 (claims)" }
    ],
    "skills_available": [
      "aluci-guard",
      "consist-guard",
      "cad-quantifier",
      "sicro-composicoes"
    ],
    "status": "✅ Operacional",
    "created_date": "2026-07-05",
    "last_tested_routing": "2026-08-01"
  }
}
```

### 4.2 Mapa Completo — 20 Agentes

#### **Eixo 1 — Horizontais (11 agentes transversais)**

| Código | Agente | Tier | Função | Handoffs |
|--------|--------|------|--------|----------|
| Manta 00 | maestro | Haiku→Sonnet | **Router central** | → C2/C3 |
| Manta 01 | claims | Opus | Parecer jurídico/técnico | ← C2/C3 |
| Manta 02 | contratual | Sonnet | Análise contratual/risco | ← C2/C3 |
| Manta 04 | imobiliario | Sonnet | Questões fundiárias/desaprop | ← C2/C3 |
| Manta 05 | orcamento | Sonnet | Orçamento / SINAPI / SICRO | ← C2/C3 |
| Manta 06 | modelagem | Sonnet/Opus | Modelagem financeira/sensibilidade | ← C2/C3 |
| Manta 07 | cronograma | Sonnet | Planejamento / cronograma / CPM | ← C2/C3 |
| Manta 13 | bd | Sonnet | Business dev / licitações | ← C2/C3 |
| Manta 14 | apresentacoes | Sonnet | Geração de apresentações/PPTX | ← C2/C3 |
| Manta 15 | advisory | Sonnet/Opus | Consultoria estratégica | ← C2/C3 |
| Manta 16 | arquiteto-ia | Opus | Second opinion / arbitragem | ← C2/C3 |

#### **Eixo 2 — Verticais por Segmento (9 agentes)**

| Código | Segmento | Agente | Tier | RAG | Status |
|--------|----------|--------|------|-----|--------|
| 03-S1 | Rodovias | agente-infraestrutura | Sonnet | rod: | ✅ |
| 03-S2 | OAE | agente-infraestrutura | Sonnet | oae: | ✅ |
| 03-S3 | Ferrovia | agente-infraestrutura | Sonnet | fer: | ✅ |
| 03-S4 | Metrô | agente-infraestrutura | Sonnet | mtr: | ✅ |
| 03-S6 | Portos | agente-portos | Sonnet | por: | 🆕 v4.2 |
| 03-S7 | Aeroportos | agente-aeroportos | Sonnet | aer: | 🆕 v4.2 |
| 03-S8 | Saneamento | agente-saneamento | Sonnet | san: | 🆕 v4.2 — AySA |
| 03-S9 | Energia | agente-energia | Sonnet | ene: | 🆕 v4.2 — ANEEL |
| 03-S10 | Barragens | agente-barragens | Sonnet | bar: | 🆕 v4.2 |

---

## 5. Metals — Matriz de Modelos, Tiers e Configuração

### 5.1 Model Tiering Strategy

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1 (Triagem)       → Claude Haiku 4.5                  │
│  Uso: routing, intake Q1-Q4, extração de metadados           │
│  Custo: ~$0.001 / 1K tokens                                  │
│  Latência: <5s                                              │
│  % de chamadas: ~20%                                         │
├─────────────────────────────────────────────────────────────┤
│  TIER 2 (Execução)      → Claude Sonnet 4.6                 │
│  Uso: análise técnica, redação, orçamento, cronograma        │
│  Custo: ~$0.015 / 1K tokens                                  │
│  Latência: <30s                                             │
│  % de chamadas: ~70%                                         │
├─────────────────────────────────────────────────────────────┤
│  TIER 3 (Complexo)      → Claude Opus 4.7/4.8               │
│  Uso: claims multi-layer, arquitetura, second opinion        │
│  Custo: ~$0.050 / 1K tokens                                  │
│  Latência: <2min                                            │
│  % de chamadas: ~10%                                         │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Matriz de Escalação Dinâmica

Cada agente começa em **Sonnet** (padrão). Escala conforme:

| Sinal de Complexidade | Escala para |
|----------------------|-------------|
| Entrada > 5K tokens | Opus |
| Multi-segmento (ex: barragem + LT) | Opus |
| Claim jurídico + técnico + financeiro | Opus |
| Requer second opinion | Manta 16 (Opus) |
| Valor do projeto > R$ 500M | Opus |

### 5.3 Custos Operacionais Estimados

**Por segmento/mês** (baseline: 100 consultas/mês × 8K tokens/consulta):

| Segmento | Haiku | Sonnet | Opus | Mix (20:70:10) |
|----------|-------|--------|------|----------------|
| Rodovias | $1.60 | $24 | $4 | **$20.40** |
| Saneamento | $1.60 | $24 | $4 | **$20.40** |
| Energia | $1.60 | $24 | $4 | **$20.40** |
| **Total (9 × S)** | **$14.40** | **$216** | **$36** | **~$183.60/mês** |
| **Anual (9 segments)** | - | - | - | **~$2,204** |

**ROI assumido**: redução de 10 horas de análise/projeto × R$ 500/hora = R$ 5K poupado. Break-even em ~1 projeto.

---

## 6. Arquitetura de Conexão — Integração Objects → Metals → Valor

### 6.1 Fluxo Canônico

```
Usuário (Portal/Slack/Email)
    ↓
Maestro (Manta 00) — TRIAGEM
    • Haiku: identifica segmento (Q1)
    • Haiku: identifica fase (Q2)
    • Haiku: identifica objetivo (Q3)
    • Haiku: identifica formato de dados (Q4)
    ↓ [decide tier + agente]
    ↓
Agente Vertical (ex: agente-saneamento S8)
    • Sonnet: ativa SKILL.md (V1-V5)
    • Sonnet: consulta RAG (san:*, san:br:*, san:ar:*)
    • Sonnet: invoca skills (C1)
    • Decide handoff → C2 (claims, orçamento, cronograma, etc.)
    ↓ [se handoff]
    ↓
Agente Horizontal (ex: Manta 05 — orçamento)
    • Sonnet/Opus: calcula SINAPI/SICRO
    • Opus (se financeiro > R$500M): escalação
    ↓
Artefato (C5)
    • React app (dashboard)
    • Memorial DOCX (parecer)
    • Spreadsheet (orçamento/cronograma)
    ↓
Usuário ← resposta com fontes, quantitativos, risco
```

### 6.2 Estrutura de Dados — Database Schema

```sql
-- objects (agentes)
CREATE TABLE maestro_objects (
  id UUID PRIMARY KEY,
  code VARCHAR (20),           -- "Manta 03-S8"
  name VARCHAR (255),          -- "agente-saneamento"
  aliases TEXT[],
  domain VARCHAR (255),        -- "Saneamento"
  tier_default VARCHAR (50),   -- "Sonnet"
  tier_escalation JSONB,       -- { "intake_simple": "Haiku", ... }
  rag_collection_slug VARCHAR (50),
  handoffs JSONB,
  skills TEXT[],
  status VARCHAR (50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- metals (configurações operacionais)
CREATE TABLE maestro_metals (
  id UUID PRIMARY KEY,
  object_code VARCHAR (20) REFERENCES maestro_objects(code),
  tier VARCHAR (50),           -- "Haiku", "Sonnet", "Opus"
  model_id VARCHAR (255),      -- "claude-haiku-4-5-20251001"
  cost_per_1k_tokens NUMERIC,
  max_latency_seconds INT,
  % _of_calls NUMERIC,
  context_window INT,
  updated_at TIMESTAMP
);

-- routing rules
CREATE TABLE maestro_routing_keywords (
  id UUID PRIMARY KEY,
  object_code VARCHAR (20) REFERENCES maestro_objects(code),
  keyword VARCHAR (255),       -- "saneamento", "ETA", "AySA"
  priority INT,
  updated_at TIMESTAMP
);
```

---

## 7. Plano de Implementação (Fases)

### Fase 1: Documentação (CURRENT — 2026-08-02)
- [ ] Finalizar este doc (objects-metals v5.0).
- [ ] Estruturar JSON schema de objects.
- [ ] Tabular metals (custos, latências, SLAs).

### Fase 2: Codificação (2026-08-05 → 2026-08-12)
- [ ] Implementar tabelas `maestro_objects` + `maestro_metals` em Supabase.
- [ ] Popular com dados dos 20 agentes.
- [ ] Criar API GET `/maestro/objects` e `/maestro/metals`.
- [ ] Testes unitários (routing correto, escalação correta).

### Fase 3: Integração (2026-08-15 → 2026-08-25)
- [ ] Integrar Maestro (Manta 00) com novo schema.
- [ ] Implementar escalação dinâmica de tier baseada em signals.
- [ ] Testar com 50+ prompts de cada segmento.
- [ ] Validar SLAs (latência, custo, qualidade).

### Fase 4: Operação & Monitoring (2026-08-25+)
- [ ] Dashboard de consumo (por agent, por tier, por segmento).
- [ ] Alertas se custo/latência sair de SLA.
- [ ] Quarterly review de matriz de escalação.
- [ ] Feedback loop: melhorias em RAG baseadas em feedback.

---

## 8. Riscos & Mitigações

| Risco | Severidade | Mitigação |
|-------|-----------|----------|
| Routing incorreto (ex: porto routed para energia) | **ALTA** | Teste com 500+ prompts. Deploy a 10% de usuários. Monitoramento em tempo real. |
| Escalação errada (desperdício em Opus) | **MÉDIA** | Matriz de escalação conservadora inicialmente. Ajustar conforme aprendizado. |
| Custo acima do orçado | **MÉDIA** | Cap de tokens/mês por agente. Alerta se > 120% do baseline. |
| RAG incompleteto ou desatualizado | **ALTA** | Processo de atualização trimestral. Versionamento de coleções. |
| Dependência crítica do Claude API (outage) | **ALTA** | Fallback a Sonnet se timeout em Opus. Circuit breaker. Cache de respostas recentes. |

---

## 9. Próximos Passos Concretos

### Imediato (próximos 3 dias)
1. [ ] Review deste doc com MN.
2. [ ] Fechar estrutura de JSON schema (objects).
3. [ ] Fechar matriz de metals (tiers, custos, SLAs).

### Curto prazo (próximas 2 semanas)
4. [ ] Implementar tabelas em Supabase.
5. [ ] Migração de dados (20 agentes, 3 tiers).
6. [ ] API endpoints de read.

### Médio prazo (próximas 4 semanas)
7. [ ] Integração no Maestro.
8. [ ] Testes de routing + escalação.
9. [ ] Deploy a 10% de usuários.
10. [ ] Dashboard de monitoramento.

---

## 10. Apêndice — Glossário

- **Object** = agente IA (identificado por código Manta XX, domain, tier default).
- **Metal** = configuração operacional de um agente (modelo, custo, latência, SLA).
- **Tier** = classe de modelo Claude (Haiku, Sonnet, Opus).
- **RAG** = coleção de documentos de referência (por segment + sub-região).
- **Handoff** = delegação automática de subtarefa para agente horizontal.
- **Escalação** = mudança de tier conforme sinal de complexidade.
- **Routing** = decisão do Maestro sobre qual agente invocar.

---

**Documento vivo.** Alterações via PR neste repo, aprovação MN, e re-publicação no SP.

Data de próxima revisão: **2026-09-02**
