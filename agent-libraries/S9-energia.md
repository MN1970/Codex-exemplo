# Agent Library — Manta 03-S9 Energia (agente-energia) — ANEEL/State Grid

Agente vertical **Energia** — prioridade **transmissão** (ANEEL / State Grid).
Cobre também distribuição, geração (hidro, eólica, solar, térmica).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG hoje**. Backlog: WF-AKP-002
  focado em leilões ANEEL de transmissão, R1-R5 EPE, RAP, ONS, IEEE.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Energia/{obra}/02_Projeto/{LT,SE,Geracao}/`            | Projeto — L+E                                  |
| `03_Projetos/Energia/{obra}/06_Leilao/`                             | Documentos de leilão — L+E                     |
| `04_IA/Manta-Maestro/Modelos/Energia/`                              | Documentos-modelo — só leitura                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| ENR-M-001   | Linha de transmissão — memorial (torres, condutor)        | ABNT NBR 5422                   |
| ENR-M-002   | Subestação — arranjo físico + memorial                    | ABNT NBR 5460                   |
| ENR-M-003   | Análise RAP para leilão de transmissão                    | Edital ANEEL                    |
| ENR-M-004   | Geração eólica/solar — layout do parque                   | Modelo Manta                    |

## 3. Knowledge Elements

**0 KEs próprios.** Backlog documentado.

## 4. Skills disponíveis

- `energia.lt_project` — dimensiona LT (torre, condutor)
- `energia.rap_estimate` — estimativa de RAP para leilão
- `energia.se_arrange` — projeto de arranjo de SE
- `energia.wind_solar_layout` — layout de parque eólico/solar

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Estudo prévio de LT (Q2=A)                           | 02_Projeto/LT                     | ENR-M-001 + fan-out 05 + 07                       |
| Leilão de transmissão (Q2=F)                         | 06_Leilao                         | ENR-M-003 + fan-out 13 + 06 + 15                  |
| Projeto executivo SE                                 | 02_Projeto/SE                     | ENR-M-002                                          |

Handoff frequente: **13 BD** (leilões), **06 Modelagem** (RAP → TIR), **15
Advisory** (regulação ANEEL/ONS), **05 Orçamento**, **07 Cronograma**.
