# S1-V7 — PLANO FINAL INTEGRADO
**MNT-2026-S1-SEISMIC-RESILIENCE | Agente Completo Rodovias Resilientes**

---

## 🎯 VISÃO FINAL (MN APROVADO)

```
MANTA 03-S1 v3.0 (Q2 2027)
┌─────────────────────────────────────────────────────────┐
│  AGENTE ESPECIALISTA RODOVIAS RESILIENTES SÍSMICAS     │
│                                                         │
│  7 VERTENTES:                                           │
│  ✅ V1: Análise Técnica & Risco                        │
│  ✅ V2: Inteligência DNIT                              │
│  ✅ V3: Gestão de Obra                                 │
│  ✅ V4: Document Intelligence                          │
│  ✅ V5: Pavimento & Terraplenagem                      │
│  🆕 V6: SÍSMICA & RESILIÊNCIA (6 disciplinas)         │
│  🆕 V7: GEOMETRIA SÍSMICA (5 disciplinas)             │
│                                                         │
│  13 DISCIPLINAS TOTAIS (D1–D7):                        │
│  - D6.1–D6.6: Sísmica + geotecnia + custeamento       │
│  - D7.1–D7.5: Geometria horizontal/vertical resiliente│
│                                                         │
│  HANDOFFS INTEGRADOS:                                  │
│  → Agente-05 (Orçamento)                              │
│  → Agente-07 (Cronograma)                             │
│  → Agente-advisory (Financeiro)                       │
│  → Agente-contratual (Jurídico)                       │
│  → Futuros agentes (Geotecnia, Hidráulica)           │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 MATRIZ COMPLETA — V6 + V7

### V6 — SÍSMICA & RESILIÊNCIA (6 Disciplinas)

```
D6.1: Zoneamento Sísmico
      ├─ PGA maps (USGS)
      ├─ Espectro resposta (Sa, Sd, Sv)
      ├─ Amplificação sítio (Vs30, Fa, Fv)
      └─ Classificação risco (baixo/moderado/alto/muito alto)

D6.2: Liquefação & Geotecnia Sísmica
      ├─ Caracteriação geológica
      ├─ Propriedades dinâmicas (G_max, ξ, CRR)
      ├─ Índice liquefação (Tokimatsu v2)
      ├─ Amplificação sítio (NEHRP)
      ├─ Deformação permanente (Newmark, Younes)
      ├─ Remediação geotécnica (5+ técnicas)
      └─ Casos Jericó, Ceará, ES

D6.3: Estabilidade Sísmica Taludes
      ├─ Método Newmark (sliding block)
      ├─ Coeficiente sísmico dinâmico
      ├─ Deslocamento permanente (m)
      ├─ Monitoramento pós-evento
      └─ Integração com taludes existentes (V1)

D6.4: Design Resiliente
      ├─ Pavimento resiliente (CBUQ elástico, BGS reforçado)
      ├─ Reforço taludes (geotêxtil, geocomposto, PVD)
      ├─ Muros dinâmicos (gabiões, MSR, juntas sísmicas)
      ├─ Barreiras com amortecedor
      ├─ Drenagem resiliente
      └─ Tabelas dimensionamento por zona sísmica

D6.5: Custeamento Pós-Desastre
      ├─ SICRO adaptado (items sísmicos)
      ├─ Matriz custos (emergencial vs redesign)
      ├─ TRS (Tempo Retorno Serviço)
      ├─ Financiamento (FUNDO, BNDES, seguros)
      └─ Handoff agente-05 integrado

D6.6: Casos Sísmicos
      ├─ Jericó 2024 (análise completa)
      ├─ Ceará (solos arenosos)
      ├─ ES (argilas moles)
      ├─ SP (solos residuais)
      └─ LATAM (Colômbia, Peru, Argentina)
```

### V7 — GEOMETRIA SÍSMICA (5 Disciplinas)

```
D7.1: Geometria Horizontal Resiliente
      ├─ Raios mínimos ajustados (tabela por PGA)
      ├─ Superelevação otimizada (dinâmica)
      ├─ Rampa de transição sísmica
      ├─ Distância de visibilidade sísmica
      └─ Fatores de segurança 1.1–1.3x vs convencional

D7.2: Geometria Vertical Resiliente
      ├─ Rampas máximas reduzidas (zona sísmica)
      ├─ Raios verticais (PIV) aumentados
      ├─ Curvas verticais resilientes
      └─ Consideração inércia vertical em sísmo

D7.3: Interação Geometria × Taludes Sísmicos
      ├─ Feedback D6.3 (Newmark) → Geometria
      ├─ Mapa vulnerabilidades geométricas
      ├─ Geometria preventiva (pré-evento)
      ├─ Curvas críticas + taludes críticos
      └─ Árvore decisão (reforçar vs redesenhar)

D7.4: Segurança Viária em Contextos Sísmicos
      ├─ Visibilidade pós-evento
      ├─ Superelevação × tombamento (novo limite)
      ├─ Comprimento de parada em sísmo (+18%)
      ├─ Sinalização específica
      └─ Conformidade operacional

D7.5: Casos Geométricos — Jericó + Redesign
      ├─ Análise geometria Jericó (vulnerabilidades)
      ├─ Redesign proposto (3 opções)
      ├─ Matriz decisão (Δ > 0.15m → ações)
      ├─ Custos adaptação (2–3% extra)
      └─ Validação contra dados reais
```

---

## 🔄 FLUXO DE INTEGRAÇÃO (V6 ↔ V7)

```
                    USUÁRIO INPUT
                         │
                         ↓
        ┌─────────────────────────────────┐
        │ Q1–Q5: Caracterização Projeto   │
        │  - Obra?  - Fase?               │
        │  - Sísmico? - Objetivo?         │
        └─────────────────────────────────┘
                         │
             ┌───────────┴───────────┐
             ↓                       ↓
         D6.1 (Zoneamento)       D7 (Geom)
         PGA maps               Geom convencional
         Classificação          Raios, rampas, etc.
             │                       │
             ↓                       ↓
         D6.2/D6.3              D7.1/D7.2
         Liquefação+            Raios sísmico
         Newmark (Δ)            Superelevação sísmico
             │                       │
             │       D7.3 FEEDBACK   │
             ├──────────────────────→┤
             │    (Δ > 0.15m?)       │
             ↓                       ↓
         D6.4 (Design)          D7.5 (Redesign)
         Reforço talude         Elevar raio?
         Dreno sísmico          Aumentar e%?
         Barreira                Mover PIV?
             │                       │
             └───────────┬───────────┘
                         ↓
             ┌─────────────────────────────┐
             │ D6.5/D7.5: CUSTEAMENTO     │
             │  - SICRO adaptado (geo+sís)│
             │  - Custo extra (+3–5%)     │
             │  - Handoff agente-05       │
             └─────────────────────────────┘
                         │
                         ↓
             ┌─────────────────────────────┐
             │ ARTEFATO REACT (20+ abas)   │
             │  - Zoneamento sísmico       │
             │  - Liquefação               │
             │  - Estabilidade sísmica     │
             │  - Design resiliente        │
             │  - Geometria sísmica        │
             │  - Vulnerabilidades        │
             │  - Custos                  │
             │  - Casos                   │
             └─────────────────────────────┘
```

---

## 📈 INTAKE ESTENDIDO (Q1–Q5)

```
┌────────────────────────────────────────────────────┐
│ NOVO INTAKE S1-V7 (integrado V6+V7)               │
└────────────────────────────────────────────────────┘

Q1: Que obra?
    [ ] Pavimento
    [ ] Talude / Aterro
    [ ] Drenagem
    [ ] Barreira / Segurança Viária
    [ ] Geometria (NOVO em V7)
    [ ] Múltiplo

Q2: Qual fase?
    [ ] Estudo prévio / EVTE
    [ ] Projeto básico
    [ ] Projeto executivo
    [ ] Obra em execução
    [ ] O&M
    [ ] Pós-desastre (NOVO)

Q3: Contexto sísmico? (DETECTA PGA AUTOMATICAMENTE)
    [ ] Baixo (PGA < 0.06g)       → V1–V5 convencional
    [ ] Moderado (0.06–0.12g)     → D6.1 + D6.2 + D7 básico
    [ ] Alto (0.12–0.20g)          → D6.1–D6.3 + D7 completo
    [ ] Muito Alto (>0.20g)        → V6 + V7 completo + flag
    [ ] Incerto                    → Auto-detecção USGS (lat/lon)

Q4: Objetivo específico?
    [ ] Diagnóstico técnico
    [ ] Design resiliente (NOVO em V6–V7)
    [ ] Análise liquefação (NOVO)
    [ ] Geometria sísmica (NOVO em V7)
    [ ] Custeamento pós-desastre (NOVO)
    [ ] Pleito técnico / claim

Q5 (NOVO): Dados disponíveis?
    [ ] Tenho SPT (geotecnia)
    [ ] Tenho DWG (geometria)
    [ ] Tenho acelerograma
    [ ] Tenho projeto as-built
    [ ] Nenhum (agentar recomenda investigação)
```

---

## 🎁 COMPONENTES NOVOS (IMPLEMENTAR V6–V7)

### Hardware Geotécnico Resiliente (D6.4)

```
PAVIMENTO:
  ✅ CBUQ Elástico (EBA) — absorve ciclos sísmicos
  ✅ BGS reforçado — estabilidade dinâmica

DRENAGEM:
  ✅ Dreno francês sísmico — dissipa poropressão
  ✅ PVD (Prefab Drains) — para argilas moles
  ✅ Sistema dissipação poro-pressão

REFORÇO:
  ✅ Geotêxtil + reforço sísmico
  ✅ Geocomposto (drenante + reforço)
  ✅ Geogrelha (para taludes)

MUROS:
  ✅ Gabiões c/ junta de dilatação sísmica
  ✅ MSR (Mechanically Stabilized Earth)
  ✅ Parede de solo reforçado

BARREIRA:
  ✅ Defensa metálica com amortecedor viscoso
  ✅ Guarda corpo flexível (steel rope)
  ✅ Junta de dilatação em barreiras rígidas
```

### Hardware Geométrico Resiliente (D7.1–D7.5)

```
CURVAS:
  ✅ Raios aumentados 1.1–1.3x (vs convencional)
  ✅ Superelevação dinâmica (+0.5–1.5%)
  ✅ Transição de superelevação sísmica

RAMPAS:
  ✅ Limites reduzidos (6–7.5% vs 8% DNIT)
  ✅ Compensação inércia sísmica vertical

VISIBILIDADE:
  ✅ Ajuste distância (curvas pós-deformação)
  ✅ Sinalização pós-sísmo (parada +18%)

PIVs:
  ✅ Raios aumentados
  ✅ Realocação se perto de taludes críticos
```

---

## 💾 ARQUIVOS & ESTRUTURA FINAL

```
Codex-exemplo/
│
├── .claude/agents/
│   └── agente-infraestrutura-S1-v3.md ← agent definition (V1–V7)
│
├── docs/s1-seismic-v2/
│   ├── 1-knowledge/
│   │   ├── normas/ (ISO, ASCE, NBR, DNIT, EC8)
│   │   ├── papers/ (Tokimatsu, Youd, Newmark, et al)
│   │   ├── dados/ (Jericó 2024, Ceará, ES)
│   │   ├── mapas/ (USGS PGA, zoneamento Brasil)
│   │   └── RAG-index/RAG-INDEX-MASTER.xlsx
│   │
│   ├── 2-algorithms/
│   │   ├── D6.1-Zoneamento-Sismico.md
│   │   ├── D6.2-Liquefacao-Geotecnia.md
│   │   ├── D6.3-Estabilidade-Sismica.md
│   │   ├── D6.4-Design-Resiliente.md
│   │   ├── D6.5-Custeamento-Pos-Desastre.md
│   │   ├── D6.6-Casos-Sismicos.md
│   │   ├── D7.1-Geometria-Horizontal.md
│   │   ├── D7.2-Geometria-Vertical.md
│   │   ├── D7.3-Interacao-Geom-Talude.md
│   │   ├── D7.4-Seguranca-Viaria.md
│   │   ├── D7.5-Casos-Jerico-Redesign.md
│   │   ├── calculator-pga.py
│   │   ├── calculator-li.py
│   │   ├── calculator-newmark.py
│   │   ├── calculator-geom-seismic.py ← NOVO
│   │   └── routing-v7.py ← NOVO (Q1–Q5 + handoffs)
│   │
│   ├── 3-tests/
│   │   ├── case-jerico-2024.md
│   │   ├── case-ceara.md
│   │   ├── case-es.md
│   │   ├── case-sp.md
│   │   ├── prompts-s1-v6-v7.yaml
│   │   ├── test-routing.py (30+ cenários)
│   │   ├── test-e2e.py (20+ E2E)
│   │   └── test-geom-resilience.py ← NOVO
│   │
│   └── 4-deploy/
│       ├── supabase-migration-s1-v6-v7.sql
│       ├── RAG-collections-definition.md
│       └── rollback-plan.md
│
├── sharepoint/01-agentes-fundamentais/agente-infraestrutura-S1/
│   ├── SKILL.md (v3.0 — V1–V7 completo)
│   ├── README.md (atualizado)
│   ├── ARQUITETURA-S1-V7.md ← NOVO
│   ├── refs/ (docs sísmicos compilados + refs geom)
│   └── prompts/ (exemplos intake Q1–Q5)
│
├── supabase/migrations/
│   └── 2027_01_15_s1_seismic_geom_v3.0.sql
│       (RAG collections: rod:seism:*, rod:seism:geom:*)
│
└── CLAUDE.md
    └── Atualizado: V7 adicionada, D6.1–D7.5 listadas
```

---

## 🎯 ROADMAP SPRINT CONSOLIDADO

```
SPRINT | DATA       | FOCO                           | SAÍDA
───────┼────────────┼────────────────────────────────┼─────────────────
S1     | AGO 2026   | Knowledge intake (V6–V7)       | 100+ docs, RAG 50%
S2     | SET 2026   | Scaffold V6–V7, D6.1, D7.1    | Calcs PGA, geometria
S3     | OUT 2026   | D6.2–D7.3, Newmark, interação | Liquefação, feedback
S4     | NOV 2026   | D6.3–D7.5, custeamento        | Design + geom redesign
S5     | DEZ 2026   | Casos (D6.6 + D7.5), validação| 10+ casos, Jericó
S6     | JAN 2027   | UAT + integração sistêmica    | Piloto NPS ≥40
S7     | FEV 2027   | Documentação final (SKILL v3)  | Docs, prompts, casos
S8     | MAR–JUN    | Deploy + go-live (canário)     | 🎯 LIVE produção
       | 2027       | (3 phases: 10% → 50% → 100%)   |
```

---

## 📊 KPIs FINAL (V6 + V7)

### Técnicas

```
✅ Acurácia PGA ≥95% vs USGS
✅ Acurácia LI ≥90% vs literatura
✅ Acurácia Newmark ≥85% vs benchmarks
✅ Taxa routing (Q1–Q5) ≥90% acertos ← NOVO: geom queries
✅ Geometria vulnerabilidades detectadas ≥95%
✅ Tempo análise sísmica <5 min
✅ Tempo análise geometria <2 min
✅ Handoff agente-05 sucesso ≥95%
```

### Negócio

```
✅ NPS piloto ≥40 (V6 + V7 combinado)
✅ Conversão casos sísmicos +25%
✅ Conversão casos geometria +15% (NOVO)
✅ Cross-sell handoff +40%
✅ Cobertura geográfica 8 BR + 3 LATAM
✅ Tempo uptake V6–V7 <20 min
```

---

## 🚀 PRÓXIMOS PASSOS (HOJE)

### ✅ Feito (Aprovado MN)

- [x] RFC aprovado
- [x] Planejamento estratégico (7 docs)
- [x] Sprint 1 iniciado
- [x] Estrutura repo criada
- [x] V6 + V7 arquitetura completa

### 🔄 Fazer Esta Semana

- [ ] Enviar emails especialistas (UFOP, CPRM, etc.)
- [ ] Agendar reunião agente-05 (SICRO)
- [ ] Criar SharePoint folder
- [ ] Começar coleta de documentos (normas, papers)
- [ ] Primeira daily standup (S1 team)

### 📅 Sprint 1 (AGO 2026)

- [ ] 100+ documentos coletados
- [ ] RAG INDEX 50% preenchido
- [ ] Dados Jericó compilados
- [ ] Sprint 2 detalhado
- [ ] Go para S2 (SET)

---

## 📞 STAKEHOLDERS FINAIS

| Papel | Responsável | Email | Função |
|-------|-------------|-------|--------|
| **Sponsor** | MN | mn@manta | Aprovação ✅ |
| **Tech Lead** | Arquiteto-IA | arq@manta | Design V6–V7 |
| **Product** | BD Lead | bd@manta | Market piloto |
| **Agente-05** | Orçamento | orcamento@manta | SICRO sísmico |
| **Agente-07** | Cronograma | cronograma@manta | TRS pós-desastre |
| **QA/Piloto 1** | Eng. Civil | [name] | Validação tech |
| **QA/Piloto 2** | PM | [name] | Usabilidade |
| **QA/Piloto 3** | Consultor Geotec | [name] | Lógica sísmica |

---

## 🏁 VISÃO FINAL — MN APROVADO

```
┌────────────────────────────────────────────────────┐
│                                                    │
│       MANTA 03-S1 v3.0 LIVE (Q2 2027)            │
│                                                    │
│  Agente Especialista Rodovias Resilientes        │
│  em Contextos Sísmicos + Design Geométrico       │
│                                                    │
│  ✅ 7 Vertentes (V1–V7)                          │
│  ✅ 13 Disciplinas (D1–D7)                       │
│  ✅ 50+ Módulos                                   │
│  ✅ 3 Calculadoras Críticas                      │
│  ✅ 10+ Casos Validados                          │
│  ✅ Integração 5+ Agentes                        │
│  ✅ 8 Sprints + 4 Marcos                         │
│  ✅ 12 Meses Implementação                       │
│                                                    │
│  RESULTADO: Agente de referência brasileira      │
│             em rodovias sismicamente resilientes │
│             → Pronto para mercado Jericó+        │
│                mercado LATAM                      │
│                                                    │
│  Status: 🟢 LIVE | Maestro Approved ✅           │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

**Documento**: MNT-2026-S1-SEISMIC-RESILIENCE — Plano Final Integrado  
**Versão**: 1.0 (V6 + V7 Completo)  
**Data**: 2026-07-24  
**Status**: ✅ APROVADO POR MN | IMPLEMENTAÇÃO INICIADA  
**Timeline**: Q3 2026 → Q2 2027 (12 meses)  
**Go-Live**: 30 JUN 2027 🚀

---

*Próximo milestone: Sprint 1 Knowledge Intake completion (30 AGO 2026)*
