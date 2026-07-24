# EVOLUÇÃO S1 — RODOVIAS COM SÍSMICA & RESILIÊNCIA
**Executive Summary | MNT-2026-S1-SEISMIC-RESILIENCE**

---

## 🎯 VISÃO GERAL

Transformar o **Manta 03-S1 (Rodovias)** de agente com 5 vertentes para **6 vertentes**, adicionando capacidade completa de:

1. **Análise sísmica** (zoneamento, PGA, espectros)
2. **Avaliação de liquefação** (índices, mitigação)
3. **Estabilidade de taludes sísmicos** (deformação Newmark)
4. **Design resiliente** (componentes, materiais, técnicas)
5. **Custeamento integrado pós-desastre** (SICRO adaptado)
6. **Banco de casos sísmicos** (Jericó, zonas Brasil/LATAM)

**Contexto**: Jericó/MG (2024), zonas sísmicas emergentes (Ceará, ES), mercados LATAM (Colômbia, Peru).

---

## 📊 ESTADO ATUAL vs. ALVO

### O que S1 já faz (V1–V5)
✅ Pavimento (CBUQ, BGS)  
✅ Terraplenagem & drenagem convencional  
✅ Estabilidade estática (Bishop, Spencer)  
✅ Barreira & segurança viária  
✅ SICRO + DNIT  

### O que falta (NOVO)
❌ Zoneamento sísmico (PGA, Sa)  
❌ Índices de liquefação (SPT → LI)  
❌ Análise sísmica de taludes (Newmark)  
❌ Componentes resilientes (pavimento elástico, barreira com amortecedor, drenagem sísmica)  
❌ Custeamento pós-desastre  
❌ Normas sísmicas (ISO 14383, ASCE 7, EC8)  

**Resultado**: S1 V6 será **agente de referência brasileira em rodovias sísmicas**.

---

## 🏗️ ARQUITETURA — 6 VERTENTES

```
AGENTE-INFRAESTRUTURA S1
├─ V1: Análise Técnica & Risco (EXISTENTE)
├─ V2: Inteligência DNIT (EXISTENTE)
├─ V3: Gestão de Obra (EXISTENTE)
├─ V4: Document Intelligence (EXISTENTE)
├─ V5: Pavimento & Terraplenagem (EXISTENTE)
└─ V6: SÍSMICA & RESILIÊNCIA ⭐ (NOVO)
   ├─ D6.1: Zoneamento sísmico regional (USGS PGA maps)
   ├─ D6.2: Análise de liquefação (Tokimatsu, Youd)
   ├─ D6.3: Estabilidade sísmica taludes (Newmark)
   ├─ D6.4: Design resiliente (materiais, componentes, técnicas)
   ├─ D6.5: Custeamento pós-desastre (SICRO adaptado + financiamento)
   └─ D6.6: Banco de casos (Jericó, zonas BR/LATAM)
```

---

## 🔄 NOVO FLUXO DE INTAKE (Q1–Q5)

Estender as 4 perguntas existentes com **Q5 — Contexto Sísmico**:

```
Q1: Que obra?          → Pavimento / Talude / Drenagem / Barreira / Múltiplo
Q2: Qual fase?         → Estudo / Projeto / Obra / O&M / ⭐ Pós-desastre
Q3: Contexto sísmico?  → Baixo / Moderado / Alto / Incerto ⭐ NOVO
    ↓ Se Incerto → ATIVA D6.1 (Zoneamento automático via lat/lon)
    ↓ Se Moderado+ → ATIVA V6 completo
    ↓ Se Alto + Talude → ATIVA D6.2 (Liquefação) + D6.3 (Newmark)
    ↓ Se Pós-desastre → ATIVA D6.5 (Custos) + Handoff agente-05/07

Q4: Objetivo?          → Diagnóstico / Design resiliente / Análise LI / Custo
```

**Resultado**: Usuário entra com contexto sísmico → Agente auto-route para módulos corretos.

---

## 📚 CONHECIMENTO A ADICIONAR (V6)

### Normas & Padrões Sísmicos

| Norma | Escopo | Prioridade |
|-------|--------|-----------|
| **ISO 14383-1:2016** | Design sísmico genérico | ⭐⭐⭐ |
| **ASCE 7-22** | EUA (referência ampla) | ⭐⭐ |
| **Eurocode 8** | Europa (referência) | ⭐⭐ |
| **USGS Seismic Hazard Maps** | Mapas PGA globais | ⭐⭐⭐ |
| **Tokimatsu & Yoshida (1983)** | Índice liquefação | ⭐⭐⭐ |
| **Youd et al. (2001)** | Liquefação (curvas risco) | ⭐⭐⭐ |
| **Newmark (1965)** | Deformação taludes | ⭐⭐⭐ |
| **DNIT ES-Sísmica** | Brasil (a propor) | ⭐⭐ |
| **INVIAS (Colômbia)** | LATAM | ⭐⭐ |
| **MTC Perú** | LATAM | ⭐⭐ |

### Algoritmos & Cálculos Novos

- **Calculadora PGA** (lat/lon → USGS)
- **Índice de Liquefação** (SPT → LI via Tokimatsu)
- **Deformação Newmark** (talude sísmico → deslocamento permanente)
- **Amplificação de sítio** (Vs30 → Sa ajustado)

### Componentes de Design Resiliente

| Componente | Aplicação | Benefício |
|------------|-----------|-----------|
| **CBUQ elástico (EBA)** | Pavimento | Absorve ciclos sísmicos |
| **BGS reforçado** | Base/subbase | Maior estabilidade dinâmica |
| **Geotêxtil + reforço** | Taludes/aterros | Inércia lateral; dissipa poropressão |
| **Drenagem sísmica** | Pós-evento | Recuperação rápida |
| **Barreira com amortecedor** | Segurança viária | Absorção energia dinâmica |
| **Junta de dilatação sísmica** | Estruturas | Permite movimento horizontal |

---

## ⏱️ TIMELINE — 12 MESES (Q3 2026 → Q2 2027)

### Sprints (8 total, 4 semanas cada)

```
Q3 2026 (JUL–SET)
  Sprint 1–2: Scaffold V6 + Knowledge intake (USGS, ISO 14383, papers)
             ↳ Saída: D6.1–D6.2 prontos; calculadoras PGA & LI funcionando

Q4 2026 (OUT–DEZ)
  Sprint 3–4: Análise sísmica + Design resiliente + Custeamento
             ↳ Saída: D6.3–D6.5 prontos; artefato com 5 novas abas; handoff mock

Q1 2027 (JAN–MAR)
  Sprint 5–6: Banco de casos + Integração sistêmica + Testes
             ↳ Saída: ≥10 casos; handoffs reais; UAT ≥90% pass

Q2 2027 (ABR–JUN)
  Sprint 7–8: Deploy produção + Go-live
             ↳ Saída: 🎯 Manta 03-S1 v2.0 operacional
```

### Marcos Críticos

| Marco | Quando | Deliverable |
|-------|--------|------------|
| **Knowledge Intake** | Q3 end (SET 2026) | Todos docs sísmicos em RAG |
| **Validação Jericó** | Q4 end (DEZ 2026) | Caso validado vs. dados reais |
| **UAT Piloto** | Q1 end (MAR 2027) | 3 usuários; NPS ≥ 40 |
| **Go-live** | Q2 end (JUN 2027) | Production routing + live handoff |

---

## 🔗 INTEGRAÇÕES COM OUTROS AGENTES

V6 ativa automaticamente handoffs:

```
S1 (V6 sísmica)
├─ → agente-05 (Orçamento)
│    Solicita: SICRO adaptado (CBUQ elástico, geotêxtil sísmico, etc.)
│    Recebe: Matriz custos (emergencial vs redesign)
│
├─ → agente-07 (Cronograma)
│    Solicita: Timeline restauração pós-desastre
│    Recebe: Milestone schedule crítico
│
├─ → agente-advisory
│    Solicita (pós-desastre): VPL/TIR design resiliente
│    Recebe: Modelo financeiro
│
├─ → agente-contratual
│    Solicita: Cláusulas responsabilidade sísmica
│    Recebe: Template contratual
│
├─ → agente-infraestrutura S2 (OAE)
│    Se travessia estrutural → Design sísmico ponte
│
└─ → agente-saneamento S8
     Se drenagem urbana crítica → Integração agua + resiliência
```

---

## 📊 MÉTRICAS DE SUCESSO

### Técnicas (Q2 2027)

| Métrica | Baseline | Target | Method |
|---------|----------|--------|--------|
| **Cobertura normas sísmicas** | 0 | ≥5 | Contagem D6.1–D6.6 |
| **Acurácia PGA (vs USGS)** | — | ≥95% | 100 pontos teste |
| **Acurácia LI (vs literatura)** | — | ≥90% | 50 casos SPT |
| **Tempo análise sísmica** | — | <5 min | Cronômetro UAT |
| **Taxa acerto routing Q3** | — | ≥90% | 30 test cases |
| **Handoff agente-05 success** | — | ≥95% | 20 casos E2E |

### Negócio (Q2 2027)

| KPI | Target |
|-----|--------|
| **# Casos sísmicos documentados** | ≥10 |
| **Cobertura geográfica** | 8 regiões BR + 3 LATAM |
| **NPS usuário piloto** | ≥40 |
| **Tempo uptake V6** | <15 min |
| **Cross-sell (handoff agente-05/07)** | +40% conversão |

---

## 🚨 RISCOS CRÍTICOS & MITIGAÇÕES

### Top 5 Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Falta norma BR sísmico (DNIT)** | Alto | Alto | Usar ISO 14383 como proxy; propor ao DNIT |
| **Dados USGS imprecisos Jericó** | Médio | Médio | Obter dados IPOC/universidades; validar |
| **SICRO não cobre itens resilientes** | Médio | Médio | Criar composições Manta; agente-05 adapta |
| **Scope creep (V7, V8 solicitadas)** | Médio | Médio | Fixar escopo V6; roadmap público v3.0 |
| **Handoff agente-05 falha produção** | Baixo | Alto | Teste integrado Q1 2027; dummy data |

---

## 📁 ESTRUTURA DE ARQUIVOS (DELIVERABLES)

```
Codex-exemplo
├── .claude/agents/
│   └── agente-infraestrutura-S1-v2.md ⭐ (estendido com V6)
│
├── .claude/rag/
│   └── rod:seism:* (5 sub-coleções)
│       ├── rod:seism:norm: (normas ISO, ASCE, EC8, DNIT)
│       ├── rod:seism:pga:  (mapas USGS, zonas BR)
│       ├── rod:seism:liq:  (fórmulas Tokimatsu, Youd)
│       ├── rod:seism:ana:  (Newmark, coef. sísmico)
│       ├── rod:seism:des:  (materiais, componentes)
│       ├── rod:seism:cost: (SICRO sísmico, custeamento)
│       └── rod:seism:case: (Jericó, zonas BR/LATAM)
│
├── sharepoint/01-agentes-fundamentais/agente-infraestrutura-S1/
│   ├── SKILL.md (v2.0 estendido V1–V6)
│   ├── README.md
│   ├── refs/ (docs sísmicos compilados)
│   └── prompts/ (exemplos Q1–Q5)
│
└── docs/
    └── DEPLOY-S1-v2.0.md (runbook implementação)
```

---

## ✅ PRÓXIMOS PASSOS (IMEDIATOS)

### Semana 1 (24–30 JUL 2026)

- [ ] **Kickoff com team S1** (30 min): Apresentar visão, timeline, risks
- [ ] **Enviar RFC** a MN, arquiteto-ia, agente-05 lead
- [ ] **Pesquisa inicial**: Coletar Jericó report, USGS maps, papers-chave
- [ ] **Setup repo**: Branch `feat/s1-seismic-v2` em manta-hub

### Semana 2–3 (31 JUL – 13 AGO)

- [ ] **Sprint 1 kickoff**: Scaffold V6, estrutura conhecimento
- [ ] **Contato DNIT**: Propor ES-Sísmica (longo prazo)
- [ ] **Contato especialistas**: Universidades (Jericó, sísmica Brasil)
- [ ] **Reservar reunião agente-05**: Discutir SICRO adaptado

---

## 📈 VALOR AGREGADO

### Para Manta

1. **Diferencial competitivo**: Único agente IA brasileiro de rodovias sísmicas
2. **Novo mercado**: Jericó + zonas emergentes (Ceará, ES) = pipeline novo
3. **LATAM**: Colômbia, Peru, Argentina = expansão regional
4. **Reconhecimento setorial**: Publicar artigo DNIT/ABReg

### Para Cliente

1. **Resiliência**: Designs que resistem pós-sísmica → reduz custo reparos
2. **Conformidade**: Atende futuras normas sísmicas (quando aprovadas)
3. **Custeamento realista**: SICRO adaptado + financiamento pós-desastre
4. **Velocidade**: Intake Q3 → recomendação sísmica <5 min

---

## 📞 CONTATOS & SPONSORSHIP

| Papel | Responsável | Nota |
|-------|-------------|------|
| **Sponsor** | MN (aprovação) | Gate antes merge |
| **Tech Lead** | Arquiteto-ia | Design V6 |
| **Product Owner** | BD + Advisory | Market feedback |
| **Agente-05 liaison** | Orçamento lead | Integração SICRO |
| **QA/Validation** | 3 usuários piloto | Feedback UAT |

---

## 🎯 RESUMO FINAL

**Manta 03-S1 evoluirá para referência brasileira em rodovias resilientes a sismos**, adicionando:

✅ **6 disciplinas sísmicas** (D6.1–D6.6)  
✅ **23 módulos técnicos** (zoneamento, liquefação, Newmark, design, custos, casos)  
✅ **Integração sistêmica** (handoff agente-05/07/advisory)  
✅ **Timeline realista** (12 meses, 8 sprints, 4 marcos)  
✅ **Métricas claras** (KPI técnicas + negócio)  

**Resultado**: Q2 2027 → **Agente-infraestrutura S1 v2.0 operacional com V6 sísmica & resiliência** 🚀

---

**Documento**: MNT-2026-S1-SEISMIC-EVOLUTION  
**Data**: 2026-07-24  
**Versão**: 1.0 (Planning)  
**Status**: 📋 Pronto para kickoff
