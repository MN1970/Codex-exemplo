# Bloco E — Validação de Routing (Testes Manta Maestro v4.2)

**Status**: ⏳ AGUARDANDO Blocos B+D  
**Owner**: Claude Code (QA)  
**Duração estimada**: 30 min  
**Critério de sucesso**: ≥90% acurácia de dispatch

---

## Setup

### Pré-requisitos (executar quando B+D terminarem)
1. ✅ Bloco B (DevOps) — Migração SQL completa (5 coleções RAG inseridas)
2. ✅ Bloco D (Admin SP + Claude) — SKILL.md uploaded e routing rules no DB
3. ✅ Manta Maestro v4.2 recarregado em ambiente QA/staging

### Artefatos disponíveis
- `tests/routing/prompts.md` — 30+ prompts estruturados por segmento (S6-S10) + regressão (S1-S4) + casos ambíguos

---

## Plano de Execução

### Fase 1: Testes Funcionais (15 min)

Invocar Manta Maestro com cada prompt e registrar:
- **Prompt**
- **Agente esperado** (conforme prompts.md)
- **Agente despachado** (resposta real)
- **Match?** (✅ Pass / ❌ Fail)

**Categorias**:
- S6 Portos: 5 prompts
- S7 Aeroportos: 5 prompts
- S8 Saneamento: 6 prompts
- S9 Energia: 6 prompts
- S10 Barragens: 6 prompts
- **Subtotal S6-S10**: 28 prompts
- Regressão S1-S4: 4 prompts
- **Total**: 32 prompts

### Fase 2: Casos Ambíguos (10 min)

4 prompts com overlap de keywords — validar que Maestro escolhe o **mais específico**:
1. UHE + CFRD + LT (barragem vs. energia?)
2. ETE + subestação (saneamento vs. energia?)
3. Porto + pátio + pista aérea (portos vs. aeroportos?)
4. Adutora sobre barragem (saneamento com consulta barragens?)

Documentar decisão de roteamento + avaliar se faz sentido.

### Fase 3: Consolidação (5 min)

- Calcular taxa de acurácia: `(Pass / Total) * 100`
- Documentar falhas em matriz de rastreabilidade
- Anotar necessidade de ajuste nas routing rules (se houver padrão de falha)

---

## Matriz de Testes

### S6 — Portos (5 testes)

| # | Prompt | Esperado | Despachado | ✓ |
|----|--------|----------|-----------|---|
| 1 | Dragagem terminal Itaqui | agente-portos | — | ⏳ |
| 2 | Dimensionar defensa Panamax | agente-portos | — | ⏳ |
| 3 | ANTAQ cronograma TUP | agente-portos | — | ⏳ |
| 4 | PIANC quebra-mar enrocamento | agente-portos | — | ⏳ |
| 5 | Calado insuficiente dragagem | agente-portos | — | ⏳ |

### S7 — Aeroportos (5 testes)

| # | Prompt | Esperado | Despachado | ✓ |
|----|--------|----------|-----------|---|
| 6 | Dimensionar pista código 3C | agente-aeroportos | — | ⏳ |
| 7 | RBAC pátio aeronaves | agente-aeroportos | — | ⏳ |
| 8 | PCN pista A320neo | agente-aeroportos | — | ⏳ |
| 9 | Balizamento CAT II noturno | agente-aeroportos | — | ⏳ |
| 10 | ICAO Annex 14 offset RWY | agente-aeroportos | — | ⏳ |

### S8 — Saneamento (6 testes)

| # | Prompt | Esperado | Despachado | ✓ |
|----|--------|----------|-----------|---|
| 11 | ETA ciclo completo 200k hab | agente-saneamento | — | ⏳ |
| 12 | Golpe de aríete 800mm | agente-saneamento | — | ⏳ |
| 13 | AySA reabilitação Planta Norte | agente-saneamento | — | ⏳ |
| 14 | Dimensionamento rede esgoto NBR 9649 | agente-saneamento | — | ⏳ |
| 15 | PMSB município | agente-saneamento | — | ⏳ |
| 16 | Lei 14.026 SNIS universalização | agente-saneamento | — | ⏳ |

### S9 — Energia (6 testes)

| # | Prompt | Esperado | Despachado | ✓ |
|----|--------|----------|-----------|---|
| 17 | Leilão ANEEL transmissão 2027 | agente-energia | — | ⏳ |
| 18 | RAP LT 500kV 250km | agente-energia | — | ⏳ |
| 19 | Ampacidade ACSR 636 MCM | agente-energia | — | ⏳ |
| 20 | Arranjo subestação 230kV | agente-energia | — | ⏳ |
| 21 | ONS fluxo de potência | agente-energia | — | ⏳ |
| 22 | EPE R3 vs. edital | agente-energia | — | ⏳ |

### S10 — Barragens (6 testes)

| # | Prompt | Esperado | Despachado | ✓ |
|----|--------|----------|-----------|---|
| 23 | CFRD 80m altura | agente-barragens | — | ⏳ |
| 24 | Dam breach analysis | agente-barragens | — | ⏳ |
| 25 | ICOLD dry stack rejeitos filtrados | agente-barragens | — | ⏳ |
| 26 | PNSB revisão periódica | agente-barragens | — | ⏳ |
| 27 | TSF descaracterização | agente-barragens | — | ⏳ |
| 28 | SIGBM categoria risco | agente-barragens | — | ⏳ |

### Regressão S1-S4 (4 testes)

| # | Prompt | Esperado | Despachado | ✓ |
|----|--------|----------|-----------|---|
| 29 | SICRO CBUQ | S1 + manta-05 | — | ⏳ |
| 30 | Viga PRP viaduto | S2 | — | ⏳ |
| 31 | AMV pátio ferroviário | S3 | — | ⏳ |
| 32 | Estação NATM metrô | S4 | — | ⏳ |

### Casos Ambíguos (4 testes)

| # | Prompt | Esperado | Decisão | Justificativa |
|----|--------|----------|---------|---------------|
| 33 | UHE + CFRD + LT | barragens ou energia? | — | ⏳ |
| 34 | ETE + subestação | saneamento + energia? | — | ⏳ |
| 35 | Porto + pista aérea | portos + aeroportos? | — | ⏳ |
| 36 | Adutora sobre barragem | saneamento + barragens? | — | ⏳ |

---

## Critérios de Aprovação

✅ **Pass**: ≥90% dos 32 testes funcionais acertam agente esperado  
⚠️ **Parcial**: 85-89% — ajustar routing rules, re-testar  
❌ **Fail**: <85% — bloqueador para Trilha 4, escalação MN

Casos ambíguos: documentar e solicitar aprovação MN sobre política de dispatch.

---

## Output Esperado

Arquivo: `tests/routing/RESULTADO-BLOCO-E-VALIDACAO.md`

```markdown
# Resultado Final — Bloco E

Data: [TIMESTAMP]
Total de testes: 32
Passes: [N]
Fails: [N]
Taxa de acurácia: [%]
Status: ✅ PASS / ⚠️ PARTIAL / ❌ FAIL

## Sumário por segmento
- S6 Portos: [N/5]
- S7 Aeroportos: [N/5]
- S8 Saneamento: [N/6]
- S9 Energia: [N/6]
- S10 Barragens: [N/6]
- Regressão S1-S4: [N/4]

## Casos ambíguos
[Anotações de decisão]

## Falhas documentadas
[Matriz de rastreabilidade]

## Recomendações
[Próximas ações se houver fails]
```

---

## Timeline

- **Aguardando**: Conclusão Blocos B+D (DevOps + Admin SP) — ~60 min
- **Início Bloco E**: t+60 (quando B+D concluídos)
- **Duração**: 30 min
- **Conclusão esperada**: t+90
- **Liberação Trilha 4 (Gate MN)**: Após Bloco E (se ✅ PASS)

---

## Status Atual

🔄 **PRONTO PARA INICIAR** — aguardando sinal de conclusão de B+D

Quando recebermos notificação de conclusão dos Blocos B+D, Claude Code executará Bloco E imediatamente.
