# Agent Library — Manta 07 Cronograma (manta-07)

Referência canônica de trabalho do agente **Cronograma** (Sonnet, tier default).
Se o `.claude/agents/agente-cronograma.md` é o **como o agente pensa**, este
arquivo é o **com o que o agente trabalha**.

**Escopo:** planejamento (CPM, Monte Carlo, PERT, Lean Construction/Last
Planner), acompanhamento (EVM, TIA), integrações Primavera/MS Project. É o
agente com **maior cobertura de KEs (18 de 52)** — funciona como camada de
inteligência de prazo para todos os segmentos.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/08_Cronograma/Baseline/`             | Baseline aprovado — só leitura                 |
| `03_Projetos/{segmento}/{obra}/08_Cronograma/As-Built/`             | Fatos executados — leitura+escrita             |
| `03_Projetos/{segmento}/{obra}/08_Cronograma/Analises/`             | Monte Carlo, TIA, EVM — leitura+escrita        |
| `03_Projetos/{segmento}/{obra}/08_Cronograma/LPS/`                  | Last Planner (VMS, PPC) — leitura+escrita      |
| `04_IA/Manta-Maestro/Modelos/Cronograma/`                           | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B1/`, `B2/`, `B4/`                       | PDFs dos KEs — só leitura                      |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| CRN-M-001   | Cronograma baseline — obra linear (WBS + CPM)             | Modelo Manta                    |
| CRN-M-002   | Monte Carlo com distribuição Beta (algoritmo Python)      | Herzog 2024 + KE-032            |
| CRN-M-003   | Last Planner System — VMS + PPC + lookahead 6 semanas     | Ballard 2000 + KE-013           |
| CRN-M-004   | Curva S baseline + EVM (Framework Nature)                 | Nature 2025 + KE-048/049        |
| CRN-M-005   | TIA — memória retrospectiva MIP 3.3-3.7                   | PMWJ 2018 + KE-016              |
| CRN-M-006   | ICRA — Índice de Criticidade de Risco de Atraso           | Caderno Ped. 2024 + KE-031      |

## 3. Knowledge Elements (18 KEs no pgvector)

Do `INDICE-KEs.md`, seção Cronograma (18 KEs · B1 + B2 + B4):

| KE     | Tipo         | Uso operacional                                         |
|--------|--------------|---------------------------------------------------------|
| KE-001 | metodo       | MILP terraplenagem — planeja seq. corte/aterro          |
| KE-002 | benchmark    | Mapping 72 papers earthwork (LP domina allocation)      |
| KE-005 | metodo       | Monte Carlo adaptativo (contra flecha OAE)              |
| KE-006 | formula      | Fluência estocástica CEB-FIP — cronograma OAE           |
| KE-011 | benchmark    | 5 técnicas Lean PT (VSM, TVD, BIM…)                     |
| KE-012 | metodo       | Framework Lean Construction — ineficiências por fase    |
| KE-013 | metodo       | Last Planner System — PPC, lookahead, constraints        |
| KE-014 | metodo       | Teoria TFV (Transformation-Flow-Value)                   |
| KE-016 | metodo       | TIA prospectiva vs retrospectiva (MIP 3.3-3.7)          |
| KE-017 | benchmark    | Tabela 5 técnicas delay — quando usar cada              |
| KE-030 | metodo       | Monte Carlo com distribuição Beta (descomissionamento)   |
| KE-031 | metodo       | ICRA + Monte Carlo @RISK                                 |
| KE-032 | metodo       | Algoritmo Python Monte Carlo — open source               |
| KE-033 | benchmark    | CPM determinístico vs Monte Carlo — assertividade        |
| KE-048 | benchmark    | 3 técnicas EVM em 30 projetos                            |
| KE-049 | metodo       | Framework seleção EVM por estágio                        |
| KE-050 | case_study   | EVM em obras reais Equador                               |
| KE-051 | metodo       | ML + 19 EAC — integrável com 16 pesquisador              |

Retrieval: `select ke_codigo, descricao from knowledge_extractions where '07' = any(agentes_destino) order by grader_score desc;`

## 4. Skills disponíveis

- `cronograma.build_baseline` — gera WBS + CPM a partir de escopo (CRN-M-001)
- `cronograma.monte_carlo_beta` — roda Monte Carlo com KE-032 Python
- `cronograma.tia_analyze` — TIA retrospectiva entre dois cronogramas
- `cronograma.lps_ppc` — cálculo PPC + lookahead + restrições (KE-013)
- `cronograma.evm_snapshot` — PV/EV/AC/CPI/SPI/EAC (compartilhado com 05)
- `cronograma.icra_score` — pontua atividades por criticidade (KE-031)

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Novo projeto — precisa de baseline (Q2=1/2/3)        | 08_Cronograma/Baseline            | CRN-M-001 preenchido + Monte Carlo (CRN-M-002)    |
| Análise de risco de prazo pré-obra                   | 08_Cronograma/Analises            | CRN-M-006 (ICRA) + histograma de duração          |
| Reunião semanal de obra (Q2=4)                       | 08_Cronograma/LPS                 | CRN-M-003 atualizado (PPC + lookahead)            |
| Medição + EVM mensal                                 | 08_Cronograma/Analises            | CRN-M-004 preenchido + interpretação SPI/CPI      |
| Ocorreu atraso — precisa provar responsabilidade      | 08_Cronograma/Analises            | CRN-M-005 (TIA) + laudo temporal                  |
| Cliente pergunta "vai atrasar?" (mid-obra)           | 08_Cronograma/Analises            | Monte Carlo atualizado + P50/P80/P95              |

Handoff frequente: **01 Claims** (TIA vira anexo de pleito), **05 Orçamento**
(EVM cruza tempo × custo), **16 Arquiteto-IA** (ML+EVM via KE-051).
