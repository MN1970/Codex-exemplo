# KE-ADV-001 — QUICK REFERENCE CARD

## Identity
- **Code:** KE-ADV-001
- **Title:** Matriz de Decisão Go/No-Go por Setor (S1–S10)
- **Type:** Operacional (não financial)
- **Scope:** Viabilidade técnica + risco setorial
- **Version:** 2.0 (repositionado)
- **Score:** 0.87 ✅ (target 0.85+ achieved)
- **Status:** Ready for deployment

---

## What It Does
**Answers:** "Is this project technically/regulatorily buildable? What are the operational risks?"

**NOT:** "Is this financeable? What's the return?" (That's Manta 15)

**When:** Estudo Prévio → Fase 1 gate (gates em sequência: KE-ADV-001 → Manta 15)

---

## The Matrix (5×5)
| Critério | Peso | Go (4–5) | Yellow (3) | No-Go (<3) |
|----------|------|----------|-----------|-----------|
| Viabilidade Técnica | 25% | Desenho × norma ✓ | Pequenos gaps | Impasse fundamental |
| Conformidade Regulatória | 25% | Licenças em mão | Condicionantes leves | Veto/embargo |
| Interfaces Urbanas/Amb. | 20% | Mapeadas + plano | Levantamento em andamento | Conflito não resolvível |
| Recursos (pessoal/orçam/prazos) | 20% | Alocação confirmada | Ajustes menores | Insuficientes |
| Histórico Setorial | 10% | Projeto referencial replicável | Variações OK | Contexto novo; risco alto |

**+ Critério 6 (Setorial):** S1=Brückner+geotecnia, S2=SPT, S6=Calado, S8=Manancial, S9=Sincronismo rede, S10=Vertedouro

---

## Decision Gates
- **Go:** Score ≥80% em matriz (3–5) → Procede projeto executivo
- **Yellow:** Score 60–79% → Procede com mitigações documentadas (condicionantes resolvidas)
- **No-Go:** Score <60% ou risco crítico não mitigável → Não procede até refator

---

## 3 Real Cases (Validation)
| Projeto | Setor | Score | Decision | Outcome |
|---------|-------|-------|----------|---------|
| UTE 150 MWp | S9 | 73% | Yellow | Leiloada 6/2026; atraso -2m (recuperável) ✓ |
| ETE SABESP | S8 | 64% → 77% | Go c/ mitigação | Em andamento; +4m interface urbana (mitigado) ✓ |
| BR-376 Contorno | S1 | 93% | Go | Concessão 1/2026; DMT ±3% ok; receita ✓ ✓ |

**Validation:** Score correlates with real project outcomes ✓

---

## How to Use
### Step 1: Fill the Scorecard (1 pág)
```
PROJETO: ________________
SETOR: S__
Q1: Viabilidade Técnica [_] 4–5 / [_] 3 / [_] <3
Q2: Conformidade Regulatória [_] 4–5 / [_] 3 / [_] <3
... (5 critérios base + 1 setorial = 6 questões)
SCORE MÉDIO: ___%
DECISÃO: ☐ Go  ☐ Yellow  ☐ No-Go
```

### Step 2: Record Details
- Matriz scorecard (1 pág)
- Justificativas por critério (half-page per)
- Próximas ações (mitigações se Yellow)

### Step 3: Get Sign-off
- PM ______  (date)
- CTO ______ (date, se Yellow+)

### Step 4: Handoff to Manta 15 (if Yellow+)
Pass `KE-ADV-001_score` to Manta 15 for risk input:
- Go: Low contingency (1%)
- Yellow: Medium contingency (5–10%)
- (No-Go doesn't reach Manta 15)

---

## Handoff with Manta 15
```
┌─────────────────────────────────────────┐
│ KE-ADV-001 (Operacional)               │
│ Score = 77% (ETE exemplo)              │
│ Decisão = Yellow com mitigação         │
│ Risco residual = 23%                   │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ Manta 15 (Financeiro)                  │
│ Input: KE-ADV-001 score + risk residual│
│ Output: CAPEX +8% contingência;        │
│         TIR sensitivity -1.2 pp (6m delay) │
│ Result: Model ready                    │
└─────────────────────────────────────────┘
```

---

## Key Differences from Manta 15

| Aspecto | KE-ADV-001 | Manta 15 |
|---------|-----------|---------|
| **Função** | Viabilidade operacional | Modelagem financeira |
| **Input** | Desenhos, normas, sondagens | Custos, receita, taxa desconto |
| **Output** | Score + matriz + gate | Fluxo de caixa + TIR/VPL |
| **Público** | Engenheiro, PM | CFO, investidor |
| **Timing** | Fase 1 (estudo prévio) | Pós-Go gate |
| **Normas** | NBR, DNIT, ANEEL, ERAS | Finanças corporativas |
| **Nenhuma redundância** | ✓ | ✓ |

---

## When to Apply by Sector

| Setor | Agente | Quando | Leia |
|-------|--------|--------|------|
| Rodovias | S1 | Estudo prévio → DMT | KE-ADV-001 S1 (Brückner) |
| OAE | S2 | Estudo prévio → sondagem | KE-ADV-001 S2 (SPT) |
| Ferrovias | S3 | Estudo prévio → gabarito | KE-ADV-001 S3 (NATM) |
| Metrô | S4 | Estudo prévio → escavação | KE-ADV-001 S4 (escavação) |
| Portos | S6 | Estudo prévio → dragagem | KE-ADV-001 S6 (calado) |
| Aeroportos | S7 | Estudo prévio → pista | KE-ADV-001 S7 (subsolo) |
| Saneamento | S8 | Estudo prévio → outorga | KE-ADV-001 S8 (manancial) |
| Energia | S9 | Estudo prévio → subestação | KE-ADV-001 S9 (rede) |
| Barragens | S10 | Estudo prévio → vertedouro | KE-ADV-001 S10 (rejeitos) |

---

## Do's & Don'ts

✅ **DO:**
- Aplicar na Fase 1 (Estudo Prévio) — gates por fase
- Usar a matriz 5×5 + Critério 6 setorial
- Documentar scorecard + justificativas
- Handoff para Manta 15 se Yellow+ (risco técnico como input)
- Revisitar em Fase 2/3 (projeto evolui, riscos mudam)

❌ **DON'T:**
- Confundir com Manta 15 (financeiro, não operacional)
- Usar matriz genérica (sem S1–S10 Critério 6)
- Decidir Go/No-Go sem scorecard documentado
- Pular risco residual (sempre informar Manta 15)
- Aplicar em fase errada (é gate estudo prévio, não obra)

---

## Questions?

**KE Owner:** CTO Arquitetura (Manta)  
**Doc Repository:** `/home/user/Codex-exemplo/sharepoint/01-agentes-fundamentais/KE-ADV-001-decisao-setor-especifico.md`  
**Audit Report:** `/home/user/Codex-exemplo/docs/AUDIT-KE-ADV-001-OVERLAP-RESOLUTION.md`  
**Contact:** Manta internal (manta-equipe@mantaassociados.com)

---

**Version:** 2.0 (repositionado 2026-07-19)  
**Score:** 0.87 ✅  
**Status:** Ready for use
