# Integração Manta 20 (manta-20-esg) — Design Agent ESG/Impact

**Documento de integração técnica e operacional**  
**Versão**: v1.0 (2026-08-02)  
**Responsável**: ESG & Compliance Lead + Maestro (routing)  

---

## Sumário

1. [Visão geral](#visão-geral)
2. [Arquitetura de roteamento](#arquitetura-de-roteamento)
3. [Integrações funcionais](#integrações-funcionais)
4. [Fluxos de dados](#fluxos-de-dados)
5. [RAG e fontes de dados](#rag-e-fontes-de-dados)
6. [Model tiering e capacidades](#model-tiering-e-capacidades)
7. [Checklist de deployment](#checklist-de-deployment)
8. [Runbook operacional](#runbook-operacional)

---

## Visão geral

**Manta 20 (manta-20-esg)** é um agente horizontal transversal que fornece
**Design Agent P3-04** — avaliação ESG (Environmental, Social, Governance) e
mitigação de impacto ambiental e social para projetos de infraestrutura.

**Características**:
- **Tipo**: Horizontal (não é vertical de segmento)
- **Modelo**: Claude Sonnet (análise multi-dimensional)
- **Ativação**: Co-agente disparado pelo Maestro quando termos ESG detectados
- **Responsabilidade primária**: ESG scorecard, roadmap de compliance, carbon accounting
- **Segmentos suportados**: S6 (Portos), S7 (Aeroportos), S8 (Saneamento), S9 (Energia), S10 (Barragens) — com extensão possível a S1-S4
- **Status operacional**: v1.0 (2026-08-02)

---

## Arquitetura de roteamento

### Ativadores de Maestro → Manta 20

```python
# Em manta-00-maestro.py (intake Q1)
keywords_esg = [
    # Dimensão Ambiental
    'biodiversidade', 'ambiental', 'carbono', 'carbon', 'offset', 'florestal',
    'mata atlântica', 'cerrado', 'amazônia', 'mangue', 'app', 'rl',
    'ibama', 'icmbio', 'unidade conservação', 'snuc',
    
    # Dimensão Social
    'social license', 'stakeholder', 'impacto comunitário', 'comunidade',
    'consulta prévia', 'funai', 'indígena', 'quilombola', 'tradicional',
    
    # Dimensão Governança & Compliance
    'esg', 'compliance esg', 'tcfd', 'sasb', 'gri', 'governance',
    
    # Accounting
    'carbon accounting', 'net zero', 'escopo 1', 'escopo 2', 'escopo 3', 'ghg',
]

IF any(kw in prompt.lower() for kw in keywords_esg):
    detected_segment = detect_segment(prompt)  # S6, S7, S8, S9, S10, etc
    
    if detected_segment in ['S6', 'S7', 'S8', 'S9', 'S10']:
        # Co-agente: Maestro orquestra { vertical_agent, manta_20_esg }
        return dispatch_to_coagents([
            agent=vertical_agents[detected_segment],
            coagent=manta_20_esg,
            context=['footprint', 'timeline', 'orçamento']
        ])
    else:
        # Outros segmentos: ESG direto (menos comum)
        return manta_20_esg
```

### Diagrama de fluxo

```
┌─────────────────┐
│   User Input    │
│   (intake)      │
└────────┬────────┘
         │
         v
    ┌─────────────────────────────┐
    │ Maestro (Manta 00)          │
    │ Q1: Detecção de keywords    │
    │ Q2: Phase (1-8)             │
    │ Q3: Activity (A1-A10)       │
    └────────┬────────────────────┘
             │
    ┌────────┴─────────────────────────────────────────┐
    │ Detecta ESG? (biodiversidade, carbono, etc.)     │
    └────────┬─────────────────────────────────────────┘
             │
         YES │
             v
    ┌──────────────────────────────────────────────┐
    │ Segmento em [S6,S7,S8,S9,S10]?               │
    └──┬────────────────────────────────────────┬──┘
  SIM │                                         │ NÃO
      │                                         │
      v                                         v
  ┌─────────────────────────────────────┐  ┌──────────────────────┐
  │ Dispatch CO-AGENTES:                │  │ Direct to Manta 20   │
  │ • Vertical (S6-S10)                 │  │ (menos comum)        │
  │ • + Manta 20 (ESG)                  │  │                      │
  │ Context: footprint,                 │  └──────────────────────┘
  │           timeline, orçamento       │
  └──┬────────────────────────────────┬─┘
     │                                │
     v                                v
  ┌──────────────────────────────┐  ┌────────────────────────────────┐
  │ Manta 20 (manta-20-esg)      │  │ Vertical Agent (S{N})          │
  │ ESG Assessment               │  │ Domain-specific design         │
  │ • ISA (Sensibilidade)        │  │ • Layout, specs               │
  │ • Carbon footprint           │  │ • Cost, timeline              │
  │ • Social License Score       │  │ • Technical compliance         │
  │ • Compliance checklist       │  │                                │
  └──┬───────────────────────────┘  └────────┬─────────────────────┘
     │                                       │
     │ ESG scorecard                        │ Footprint
     │ Roadmap mitigation                  │ Schedule
     │                                      │ Budget impact
     v                                      v
  ┌─────────────────────────────────────────────────────┐
  │ DECISION MATRIX (Maestro orchestrates)              │
  │ ESG x Technical x Financial Trade-offs              │
  │ → Scenario A: High ESG score, +40% cost             │
  │ → Scenario B: Moderate ESG, baseline cost           │
  │ → Scenario C: Low ESG, -20% cost, high risk         │
  └─────────┬───────────────────────────────────────────┘
            │
            v
  ┌──────────────────────────────────┐
  │ User (Decision maker)             │
  │ Approves scenario + triggers      │
  │ downstream agents (Manta 05, 07)  │
  └──────────────────────────────────┘
```

---

## Integrações funcionais

### 1. Maestro (Manta 00) — Routing e Orquestração

**Interface**: Maestro inicia Manta 20 como co-agente quando ESG detectado.

```json
{
  "request_id": "req_2026_08_001",
  "prompt": "...transmissão LT 250 kV, Cerrado, carbono...",
  "segment": "S9",
  "phase": 2,
  "coagents": {
    "primary": "agente-energia",
    "secondary": ["manta-20-esg"],
    "context": {
      "footprint": "geometry.geojson",
      "timeline_months": 24,
      "budget_usd": 150000000
    }
  }
}
```

**Saída Maestro** (após orquestração): matriz de cenários agregados.

---

### 2. Agentes Verticais (S6–S10) — Co-execução

Cada vertical (portos, energia, saneamento, barragens, aeroportos) passa para
Manta 20:

- **Entrada**: Footprint do projeto (área, geometria, fase, timeline)
- **Saída Esperada**: ESG scorecard, impacto ambiental/social quantificado
- **Handoff**: Manta 20 retorna ao vertical com recomendações de ajuste

**Exemplo (S9 - Energia)**:

```
Agente-energia → "LT atravessa 20 km de Cerrado nativo, fase de viabilidade"
                  ↓
                  Manta 20 calcula:
                  • ISA = 72 (alto)
                  • Offset obrigatório = 3.600 ha
                  • Carbon footprint = 2.300 tCO₂e (construção)
                  • Social license score = 65/100 (comunidades quilombola x)
                  ↓
                  Retorna ao Agente-energia:
                  "Rota alternativa +8 km desvio, ISA -12%, offset -40%, social +10"
Agente-energia → Ajusta capex (+R$ 12M), CAPEX recalculado → Manta 05 (orçamento)
```

---

### 3. Manta 05 (Orçamento) — Impacto CAPEX/OPEX

**Entrada**: ESG scorecard com custos de mitigação e offset.

```json
{
  "mitigacao": [
    { "risco": "offset_florestal", "custo_r": 3600000, "timeline_mes": 36 },
    { "risco": "social_engagement", "custo_r": 1500000, "timeline_mes": 18 },
    { "risco": "carbon_offset", "custo_r": 200000, "timeline_mes": 60 }
  ]
}
```

**Saída esperada**: Orçamento revisado com linha "ESG & Compliance".

---

### 4. Manta 07 (Cronograma) — Timeline de Licenciamento

**Entrada**: Compliance roadmap (LP IBAMA 24 meses, RAP ANEEL 4 meses, etc).

**Saída**: Atividades paralelas adicionadas:
- T_ESG_01: EIA/RIMA (meses 1–9)
- T_ESG_02: Diálogo stakeholder (meses 1–18)
- T_ESG_03: Offset site preparation (meses 3–36)
- T_LIC_01: Licença Prévia IBAMA (meses 6–24)

---

### 5. Manta 02 (Contratual) — Governança e Cláusulas ESG

**Entrada**: ESG scorecard + compliance gaps.

**Saída**: Templates contratuais com:
- Cláusulas ambientais (offset, biodiversidade)
- SLA de carbon reduction
- Aprovação FUNAI (se aplicável)
- Penalidades por non-compliance ESG

---

### 6. Manta 15 (Advisory) — Social License & Stakeholder Management

**Integração crítica**: Manta 20 fornece mapa de stakeholders + scoring;
Manta 15 desenha estratégia de engagement detalhada.

**Fluxo**:
```
Manta 20 → { comunidades: 12, ongs: 3, indigenas: 1, órgãos: 4 }
          + { social_license_score: 65/100, conflict_risk: ALTO }
           ↓
Manta 15 → Plano de engajamento 18-mês, co-design workshops,
           benefício comunitário 5%, diálogo contínuo
```

---

### 7. Dados Transversais (F-Funcionais)

**F2 (SharePoint)**: Rota automática → `03_Projetos/ESG_Assessments/*`

**F4 (Extração)**: PDF de EIA/RIMA → extração automática de dados ambientais

**F5 (Notificação)**: Alertas ESG → email a compliance lead se score < 60

**F6 (Trace)**: Audit log de todas as decisões ESG (who, when, what scoring)

---

## Fluxos de dados

### Fluxo 1: Assessment Inicial (fase Viabilidade)

```
User → Maestro: "Quero fazer uma transmissão em Goiás (Cerrado)"
                │
                ├─→ Manta 20 (ESG)
                │   • INPE MapBiomas: cobertura + ISA
                │   • IBAMA: áreas protegidas
                │   • Stakeholder map: comunidades locais
                │   ↓
                │   ESG Scorecard (inicial): 68/100
                │   • Ambiental: 72 (alto risco - Cerrado)
                │   • Social: 65 (comunidades quilombola)
                │   • Governança: 75 (compliance claro)
                │   Recomendação: VIÁVEL com condicionantes
                │
                └─→ Agente-energia (S9)
                    • Rota otimizada (ISA -12%)
                    • Timeline: +6 meses (licenciamento)
                    • Capex: +12 M (offset, diálogo)
                    ↓
                    Viabilidade Técnica revisada
                    ↓
                    Manta 05 (Orçamento): orçamento revisado
                    Manta 07 (Cronograma): timeline revisado
                    ↓
                    DECISÃO: aprovar com ESG roadmap
```

### Fluxo 2: Monitoramento Contínuo (Obra em Execução)

```
Fase 4 (Obra) → Manta 20 (monitoramento mensal):
              • Desflorestamento real vs. baseline
              • Certificação offset (pagamentos)
              • Social license score (surveys)
              • Carbon actual vs. roadmap
              ↓
              Se off-track: alert → Maestro → decisão de ação corretiva
              ↓
              Compliance gate: aprovação para próxima fase apenas se ESG OK
```

---

## RAG e fontes de dados

### Coleção ESG em Supabase

**Tabela**: `manta_rag_chunks` (prefixo `esg:`)

| Subcoleção | Chunks | Atualização | Fonte |
|-----------|--------|------------|--------|
| `esg:inpe-mapbiomas` | 40 | Anual | INPE MapBiomas 1985–2023 |
| `esg:ibama-uc` | 25 | Mensal | IBAMA Geoportal |
| `esg:lei-florestal` | 15 | Pontual | Lei 12.651, resoluções CONAMA |
| `esg:stakeholder-mapping` | 30 | Por projeto | Manta 15 + IPAM |
| `esg:carbon-factors` | 20 | Anual | EPA/GHG Protocol |
| `esg:aneel-compliance` | 12 | Trimestral | ANEEL, ONS editais |
| `esg:antaq-compliance` | 10 | Trimestral | ANTAQ, ROM (portos) |
| `esg:saneamento-compliance` | 8 | Semestral | SNIS, Lei 14.026, ERAS |

**Total**: ~160 chunks em ESG (sugestão: criar como v1.0 do Manta 20)

### APIs Externas (via MCP)

- **INPE**: MapBiomas, PRODES (desflorestamento tempo-real)
- **IBAMA**: Geoportal (UC, TI, APP, RL, licenças)
- **ANA**: Sistema Outorgas (água)
- **EPA/GHG Protocol**: Fatores de emissão setoriais

---

## Model tiering e capacidades

### Tier Sonnet (padrão para Manta 20)

**Capacidades**:
- Análise multi-dimensional (4D ESG)
- Leitura de GeoJSON (spatial footprint)
- Cálculo de scoring (ISA, social license, carbon)
- Geração de roadmaps estruturados
- Integração com 7+ fontes de dados RAG

**Latência típica**: 45–90 segundos (primeira rodada + cálculos)

**Fallback**: Haiku para triagem rápida (scoring simples, não-crítico); Opus para disputes legais complexos (raro).

### Contexto de prompt

```
Entrada típica: 32–64K tokens
├─ ESG framework (4D, normas): 8K
├─ GeoJSON footprint: 4K
├─ RAG chunks INPE/IBAMA: 12K
├─ Compliance checklist templates: 6K
├─ Histórico social (se projeto existente): 6K
└─ Stakeholder mapping (se conhecido): 4K
```

---

## Checklist de deployment

### Fase 1: Criação da Coleção RAG (Week 1–2)

- [ ] Criar tabela `esg_collections` em Supabase
- [ ] Carregar 160 chunks (8 subcoleções × ~20 chunks/col)
- [ ] Testar busca semântica (query: "biodiversidade Cerrado")
- [ ] Validar embeddings (dimensionalidade: bge-m3 ou bge-small?)
- [ ] Documento de auditoria: `docs/ESG-RAG-AUDIT.md`

### Fase 2: Integração Maestro (Week 2–3)

- [ ] Adicionar keywords ESG ao routing (Maestro v5.1.1)
- [ ] Testar co-agente dispatch com scenario fake (LT + Cerrado)
- [ ] Verificar contexto passado (footprint, timeline, budget)
- [ ] Smoke test: 5 prompts ESG-ativadores

### Fase 3: Testes com Verticais (Week 3)

- [ ] S9 (Energia): LT em Mata Atlântica
- [ ] S6 (Portos): expansão em mangue
- [ ] S8 (Saneamento): ETA em zona indígena
- [ ] S10 (Barragens): reservatório com assentamento
- [ ] S7 (Aeroportos): pista em Cerrado (extensão)

### Fase 4: Gate Humano (Week 4)

- [ ] Revisão ESG Lead: 3 casos uso escolhidos
- [ ] Revisão Legal (Manta 02): cláusulas contratuais
- [ ] Revisão Compliance: checklist legislativo (IBAMA, ANEEL, ANTAQ)
- [ ] Aprovação MN (VP)
- [ ] Documento de aprovação: `docs/ESG-GATE-HUMANO-MN-APROVADO.md`

### Fase 5: Go-Live (Week 5+)

- [ ] Deploy em produção (Supabase + Maestro)
- [ ] Monitoria inicial (5 sessões, 2 semanas)
- [ ] Feedback loop → ajuste de keywords/RAG
- [ ] Handover para operação (ESG team)

---

## Runbook operacional

### Cenário 1: Novo Projeto Chega ao Maestro

```bash
# User → Claude Code
prompt: "Vou fazer um porto em Laguna (SC), dragagem de 2M m³"

# Maestro detects: "porto" + "dragagem" = S6
# Q1: Ativa agente-portos
# Detect ESG keywords: nenhum → normal (sem ESG automático)
# BUT: Se user depois menciona "mangue" ou "comunidade pesqueira"
#      → Maestro re-roteia: agente-portos + manta-20-esg

# Manta 20 → 
#  • INPE/IBAMA: mangue nesta área? 60 ha confirmado
#  • Stakeholder: 80 famílias pescadores
#  • Normas: Lei 11.428 (Mata Atlântica + mangue)
#  • ISA = 87 (muito alto)
#  ↓
#  ESG Scorecard: 42/100 (risco CRÍTICO)
#  → "Viabilidade comprometida. Recomenda-se:"
#     1. Co-design com comunidade (pode levantar score para 68)
#     2. Offset obrigatório: 150 ha preservação
#     3. Timeline: +18 meses (diálogo)
#  ↓
#  Manta 15 (Advisory) → desenha estratégia co-design
#  Manta 02 (Contratual) → cláusulas ambientais/sociais
#  Manta 05 (Orçamento) → adiciona R$ 4M (offset + diálogo)
#  Manta 07 (Cronograma) → adiciona 18 meses
#  ↓
#  Maestro compõe cenários e submete a decisão
```

### Cenário 2: Auditoria de Projeto em Andamento

```bash
# Fase 4 (Obra em execução) — Manta 20 monitoramento mensal

# Entrada: relatório de progresso da obra
#  • Desflorestamento real (INPE PRODES): 15 ha vs. baseline 10 ha
#  • Social license surveys: score 62 → 58 (queda)
#  • Carbon acumulado: 1.200 tCO₂e vs. roadmap 1.100 (ligeira queda)

# Manta 20 análise:
#  ✗ Desflorestamento over baseline → RED FLAG
#  ✗ Social license declining → community unrest risk
#  ✓ Carbon tracking OK

# Output: ALERTA
#  "Desflorestamento +50% vs. planejado. Recomendações:"
#  1. Imediato: auditoria de campo (impacto real)
#  2. Social: reunião comunitária de realinhamento
#  3. Offset: acelerar 5 ha preservação para compensar

# Escalação → Maestro → Manta 15 (diálogo urgente) + responsável obra
```

### Cenário 3: Consulta de Compliance (Audit/Due Diligence)

```bash
# Scenario: M&A — fund de infra estuda aquisição de ativo (fase 7)
# Input: "Qual é a exposição ESG desta hidrelétrica (UHE)?"

# Maestro detects: "hidrelétrica" + "compliance" → S10 + manta-20-esg

# Manta 20 Assessment:
#  • Reservatório: 2.500 famílias assentadas (social risk ALTO)
#  • Habitat perdido: 80 km² (biodiversidade risco ALTO)
#  • Carbon offset: geração -80 tCO₂e/ano (positivo)
#  • Compliance: Lei 12.334 (segurança), Lei 9.985 (UC), ANEEL (concessão)
#  ↓
#  ESG Scorecard: 55/100 (moderado, passível de melhoria)
#  ↓
#  Cenários:
#  A) Manter status quo: compliance OK, social risk contém-se
#  B) Investir em social: +R$ 3M (community programs) → score +15
#  C) Melhorar amostragem ambiental: +R$ 500K (monitoramento) → score +8
#  ↓
#  Output: Relatório ESG DD com cenários, usado no valuation

# Usado por: Manta 13 (BD), Manta 06 (financeiro), advisory fund
```

### Scenario 4: Consulta de Rota / Otimização

```bash
# User → Maestro: "Tenho 3 traçados para LT. Qual o melhor ESG?"

# Manta 20 co-executa com Agente-energia:

# Traçado A: 250 km direto, Cerrado 100%, ISA=85
# Traçado B: 258 km (8 km desvio), Cerrado 80%, ISA=72
# Traçado C: 270 km (desvio maior), Cerrado 45%, Mata Atl. 10%, ISA=58

# Manta 20 scoring:
#  A: ESG = 45/100 (risco alto) | offset = 5.000 ha | carbon = 2.300 tCO₂e
#  B: ESG = 72/100 (aceitável) | offset = 3.600 ha | carbon = 2.300 tCO₂e
#  C: ESG = 82/100 (bom)       | offset = 2.100 ha | carbon = 2.350 tCO₂e

# Agente-energia análise técnica:
#  A: capex = R$ 150M, timeline = 24 meses
#  B: capex = R$ 162M, timeline = 30 meses (offset delay)
#  C: capex = R$ 175M, timeline = 36 meses

# Maestro matriz de decisão (agregada):
#  A: High risk (ESG) + low cost + short timeline
#  B: Moderate ESG + moderate cost + moderate timeline → RECOMENDADO
#  C: Good ESG + high cost + long timeline

# Output: "Traçado B é Pareto-ótimo. ESG aceitável (72/100) com
#          adicional de capex moderado (R$ 12M) e 6-mês extra."
```

---

## Contatos & Escalação

| Role | Contato | Disponibilidade | Expertise |
|------|---------|-----------------|-----------|
| **Proprietário Manta 20** | ESG & Compliance Lead (TBD) | Business hours | Overall ESG framework, gate humano |
| **Biodiversity** | IPAM partnership | 24h (research) | Offset, habitat, mapas INPE/IBAMA |
| **Social license** | Manta 15 (Advisory) | Business hours | Stakeholder mapping, community strategy |
| **Carbon accounting** | Sustainability consultant | 24h (análise) | GHG protocol, net zero roadmap |
| **Compliance legal** | Manta 02 (Contratual) | Business hours | Regulatory mapping, cláusulas |
| **Escalação crítica** | Maestro (Manta 00) + MN (VP) | On-demand | Deal-breaker ESG decisions |

---

## Aprova e Próximos Passos

**Assinado por**: (MN — gate humano)  
**Data**: 2026-08-02  
**Status**: ✅ Pronto para implementação  

**Próximos passos**:
1. Provisão de RAG collections (Supabase, week 1–2)
2. Integração Maestro routing (week 2–3)
3. Testes com S6–S10 (week 3)
4. Go-live (week 4–5, sujeito a gate MN)
