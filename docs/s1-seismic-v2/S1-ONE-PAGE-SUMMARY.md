# S1-V6 SÍSMICA — UMA PÁGINA RESUMO (VISUAL)

---

## 🎯 O QUE, POR QUÊ, QUANDO, COMO

| Dimensão | Resposta |
|----------|----------|
| **O QUE** | Evoluir Manta 03-S1 de 5 para 6 vertentes, adicionando V6 — Sísmica & Resiliência |
| **POR QUÊ** | Jericó 2024 + zonas sísmicas Brasil (Ceará, ES); market LATAM; diferencial competitivo |
| **QUANDO** | Q3 2026 (agora) → Q2 2027 (go-live) = 12 meses, 8 sprints |
| **COMO** | 6 disciplinas (D6.1–D6.6), 23 módulos, 3 calculadoras, handoffs integrados |

---

## 🏗️ ARQUITETURA — 6 VERTENTES S1

```
V1: Análise Técnica & Risco ✅ Existente
V2: Inteligência DNIT ✅ Existente
V3: Gestão de Obra ✅ Existente
V4: Document Intelligence ✅ Existente
V5: Pavimento & Terraplenagem ✅ Existente
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V6: SÍSMICA & RESILIÊNCIA 🆕 NOVO ← 6 disciplinas (D6.1–D6.6)

D6.1 Zoneamento Sísmico (PGA, Sa, amplificação)
D6.2 Liquefação (Tokimatsu, índice LI)
D6.3 Estabilidade Taludes (Newmark, deformação)
D6.4 Design Resiliente (materiais, componentes)
D6.5 Custeamento (pós-desastre, SICRO adaptado)
D6.6 Casos Sísmicos (Jericó, Ceará, ES, LATAM)
```

---

## 💡 3 CALCULADORAS CRÍTICAS

| Calculadora | Input | Output | Acurácia |
|------------|-------|--------|----------|
| **PGA** | lat/lon ou região | Aceleração pico (g) | ≥95% vs USGS |
| **LI (Liquefação)** | SPT, profundidade, PGA | Índice 0–1 + risco | ≥90% vs literatura |
| **Newmark** | FS, φ, β, acelerograma | Deformação permanente (m) | ≥85% vs benchmarks |

---

## 🔄 INTAKE ESTENDIDO (Q1–Q5)

```
Q1: Obra?      → Pavimento / Talude / Drenagem / Barreira / Múltiplo
Q2: Fase?      → Estudo / Projeto / Obra / O&M / Pós-desastre
Q3: Sísmico?   → Baixo / Moderado / Alto / Incerto ← AUTO-CLASSIFICA via USGS
Q4: Objetivo?  → Diagnóstico / Design / Análise / Custo
Q5: [Rotas]    → D6.1 / D6.2 / D6.3 / D6.4 / D6.5 (automático)
```

**Resultado**: Usuario entra com contexto sísmico → Sistema auto-route para módulos corretos.

---

## 🌍 GEOTECNIA & GEOLOGIA (D6.2 ESTENDIDO)

| Aspecto | Módulo | Cobertura |
|--------|--------|-----------|
| **Geologia** | D6.2.1 | Idade depósito, origem, estratificação |
| **Dinâmica** | D6.2.2 | Vs30, G_max, amortecimento, CRR |
| **Liquefação** | D6.2.3 | Índice Tokimatsu + correções SPT |
| **Amplificação** | D6.2.4 | Vs30 → Classe NEHRP → Fa/Fv |
| **Deformação** | D6.2.5 | Newmark, Younes, monitoramento |
| **Remediação** | D6.2.6 | Dreno, densificação, substituição, custo |
| **Casos** | D6.2.7 | Jericó, Ceará, ES, LATAM |

---

## 📚 CONHECIMENTO A INGERIR

```
NORMAS (5):
  ✅ ISO 14383-1:2016
  ✅ ASCE 7-22
  ✅ Eurocode 8 EN1998-1
  ✅ NBR 8681, 15421
  ✅ DNIT ES-Sísmica (propor)

PAPERS (8):
  ✅ Tokimatsu & Yoshida (1983)
  ✅ Youd et al. (2001)
  ✅ Newmark (1965)
  ✅ Imai & Tonouchi, Kramer, Boore, Okada, Younes

DADOS REGIONAIS:
  ✅ USGS Global Seismic Hazard Map
  ✅ Jericó 2024 (CPRM, Defesa Civil)
  ✅ Ceará, ES (sismicidade histórica)
  ✅ IPOC acelerogramas (Andes)

RAG Collections (8):
  ✅ rod:seism:norm:
  ✅ rod:seism:pga:
  ✅ rod:seism:liq:
  ✅ rod:seism:ana:
  ✅ rod:seism:des:
  ✅ rod:seism:cost:
  ✅ rod:seism:case:
  ✅ rod:seism:geo:
```

---

## ⏱️ TIMELINE — 8 SPRINTS (12 MESES)

```
SPRINT  | PERÍODO      | FOCO                          | SAÍDA
───────┼──────────────┼──────────────────────────────┼─────────────
S1     | AGO 2026     | Knowledge intake              | Docs sísmicos coletados
S2     | SET 2026     | Scaffold V6 + D6.1–D6.2       | Calculadoras PGA & LI
S3     | OUT 2026     | D6.3–D6.4 + integração        | Newmark + design resiliente
S4     | NOV 2026     | D6.5 + handoff agente-05      | Custeamento + integração
S5     | DEZ 2026     | Banco de casos + validação    | ≥10 casos documentados
S6     | JAN 2027     | UAT piloto + testes E2E       | Feedback piloto, NPS ≥40
S7     | FEV 2027     | Documentação final            | SKILL.md, README, prompts
S8     | MAR–JUN 2027 | Deploy + go-live (canário)    | 🎯 LIVE em produção
```

---

## 🔗 HANDOFFS INTEGRADOS

```
S1-V6 (Rodovias Sísmicas)
│
├─ → Agente-05 (Orçamento)
│    Solicita: SICRO sísmico (CBUQ elástico, dreno, reforço)
│    Recebe: Custo adaptado (1.2–3.0x vs convencional)
│
├─ → Agente-07 (Cronograma)
│    Solicita: Timeline restauração pós-desastre
│    Recebe: Milestone schedule (desobstrução → reparo)
│
├─ → Agente-Advisory
│    Solicita: VPL/TIR design resiliente vs emergencial
│    Recebe: Modelo financeiro (payback, risk)
│
├─ → Agente-Contratual
│    Solicita: Cláusulas responsabilidade sísmica
│    Recebe: Template contratual + alocação risco
│
├─ → Agente-Infraestrutura S2 (OAE)
│    Se ponte sísmico-crítica → Design colaborativo
│
└─ → Agente-Saneamento S8
     Se drenagem urbana crítica → Integração água + resiliência
```

---

## 📊 KPIs DE SUCESSO

### Técnicas (Q2 2027)

```
✅ Acurácia PGA ≥95% vs USGS
✅ Acurácia LI ≥90% vs literatura
✅ Taxa routing Q1–Q5 ≥90% acertos
✅ Tempo análise <5 min (interativo)
✅ Handoff agente-05 sucesso ≥95%
✅ Cobertura normas sísmicas ≥5 principais
✅ Casos documentados ≥10
```

### Negócio (Q2 2027)

```
✅ NPS usuário piloto ≥40
✅ Conversão casos sísmicos +25%
✅ Cross-sell handoff +40%
✅ Cobertura geográfica 8 BR + 3 LATAM
✅ Tempo uptake V6 <15 min
```

---

## 🎁 COMPONENTES RESILIENTES NOVO DESIGN

```
Pavimento:    CBUQ elástico (EBA) — absorve ciclos sísmicos
Base:         BGS reforçado c/ geotêxtil — estabilidade dinâmica
Talude:       Dreno francês + reforço sísmico — dissipa poropressão
Aterro:       Densificação / PVD — reduz LI
Muro:         Gabiões c/ junta sísmica — flexibilidade
Barreira:     Defensa com amortecedor — absorção energia
Drenagem:     Dreno resiliente — recupera pós-evento
```

---

## 🚨 TOP 5 RISCOS

| Risco | Mitigação |
|-------|-----------|
| Falta norma BR sísmico (DNIT) | Usar ISO 14383; propor ao DNIT |
| Dados USGS imprecisos Jericó | Obter dados IPOC/universidades; validar |
| SICRO não cobre sísmico | Criar composições Manta; agente-05 adapta |
| Scope creep (V7, V8 pedidas) | Fixar V6; roadmap v3.0 público |
| Handoff agente-05 falha | Teste integrado Q1 2027; dummy data |

---

## 📁 DELIVERABLES (ESTRUTURA)

```
Codex-exemplo/
├── .claude/agents/
│   └── agente-infraestrutura-S1-v2.md ← agent definition atualizada
│
├── docs/s1-seismic-v2/
│   ├── 1-knowledge/           ← Docs coletadas (normas, papers, dados)
│   ├── 2-algorithms/          ← D6.1–D6.6 modules + calculadoras
│   ├── 3-tests/               ← Casos + testes routing + E2E
│   └── 4-deploy/              ← Migration SQL, runbook, rollback plan
│
├── sharepoint/01-agentes-fundamentais/agente-infraestrutura-S1/
│   ├── SKILL.md (v2.0)        ← Skill estendido V1–V6
│   ├── README.md
│   ├── refs/                  ← Docs compilados
│   └── prompts/               ← Exemplos Q1–Q5
│
└── supabase/migrations/
    └── 2027_01_15_s1_seismic_v2.sql ← RAG collections rod:seism:*
```

---

## ⚡ KICKOFF ACTIONS (TODAY)

### 1️⃣ Email RFC a MN (15 min)
```
Assunto: RFC — S1 Evolução Sísmica & Resiliência
Anexar: S1-SEISMIC-EVOLUTION-EXECUTIVE-SUMMARY.md
Tone: Urgência (Jericó), oportunidade (LATAM), prazo realista
SLA: Decisão 5 dias
```

### 2️⃣ Criar Branch feat/s1-seismic-v2 (5 min)
```bash
git checkout -b feat/s1-seismic-v2
mkdir -p docs/s1-seismic-v2/{1-knowledge,2-algorithms,3-tests,4-deploy}
git add . && git commit -m "S1 V6 initial structure"
git push -u origin feat/s1-seismic-v2
```

### 3️⃣ Agendar Reunião Agente-05 (email 48h)
```
Assunto: Almoço — SICRO Sísmico
Pauta: CBUQ elástico, dreno resiliente, geotêxtil reforçado
Duração: 1h
Data: Próxima semana
```

### 4️⃣ Criar SharePoint Folder (10 min)
```
Caminho: Documentos Compartilhados/04_IA/Projetos-Ativos/S1-SEISMIC-2026/
Conteúdo: Roadmap, status semanal
Compartilhar: MN, arquiteto-ia, agente-05, BD
```

### 5️⃣ Contatar Especialistas (email hoje)
```
Destinatários:
  □ UFOP Ouro Preto (geotecnia/sísmica, dados Jericó)
  □ CPRM (Serviço Geológico, PGA maps)
  □ Defesa Civil MG (relatório Jericó damages)
  □ IPOC (acelerogramas)
  □ USP/COPPE (papers liquefação Brasil)

Prazo resposta: 1–2 semanas
```

---

## 📈 MÉTRICAS DE PROGRESSO (SEMANAL)

```
Semana | Sprint | % Completo | Milestone | Status
───────┼────────┼───────────┼──────────┼────────
1–2    | S1     | 30%       | RFC approved | 🟡 In Progress
3–4    | S1     | 70%       | Knowledge intake | 🟡 In Progress
5–6    | S2     | 20%       | Scaffold V6 | 🔴 Backlog
...
52     | S8     | 100%      | Go-live complete | 🟢 Done
```

→ Atualizar SharePoint semanalmente

---

## 🎓 CONHECIMENTO CRÍTICO (ORDEM DE LEITURA)

1. **Esta página** (1 min leitura)
2. **S1-SEISMIC-EVOLUTION-EXECUTIVE-SUMMARY.md** (15 min)
3. **S1-GEOTECNIA-GEOLOGIA-EXPANSION.md** (20 min, técnico)
4. **S1-ROADMAP-ACTIONABLE.md** (30 min, implementação)
5. **Papers-chave** (Tokimatsu, Youd, Newmark) — por demanda

---

## 🎯 VISÃO FINAL

```
┌─────────────────────────────────────────────────────┐
│  MANTA 03-S1 V2.0 — RODOVIAS RESILIENTES SÍSMICAS  │
│                                                     │
│  ✅ 6 vertentes (V1–V6)                            │
│  ✅ 6 disciplinas sísmicas (D6.1–D6.6)             │
│  ✅ 3 calculadoras críticas (PGA, LI, Newmark)    │
│  ✅ Integração sistêmica (handoffs 5+ agentes)    │
│  ✅ Validação realidade (casos Jericó+ Ceará+ES) │
│  ✅ Timeline 12 meses (Q3 2026 → Q2 2027)         │
│                                                     │
│  🎯 Q2 2027: Referência brasileira em rodovias    │
│             sísmicas → LIVE em produção            │
└─────────────────────────────────────────────────────┘
```

---

**Status Atual**: 📋 Aguardando aprovação RFC (MN)  
**Próximo Milestone**: S1 Kickoff (7 AGO 2026)  
**Ticket**: MNT-2026-S1-SEISMIC-RESILIENCE  

---

## 📞 CONTATOS IMEDIATOS

| Papel | Ação | Prazo |
|-------|------|-------|
| **MN** | Aprovar RFC | 5 dias |
| **Arquiteto-ia** | Design V6 | 7 AGO |
| **Agente-05 lead** | SICRO sísmico | 1 semana |
| **BD** | Market piloto | 2 semanas |
| **Especialistas** | Dados Jericó | 1–2 semanas |

---

*Documento pronto para print, apresentação, ou compartilhamento em reunião.*
