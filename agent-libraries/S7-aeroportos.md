# Agent Library — Manta 03-S7 Aeroportos (agente-aeroportos)

Agente vertical **Aeroportos**. Cobre lado ar (RWY, TWY, pátio, balizamento)
e lado terra (TPS, TECA, torre, apoio). Segue RBAC 154 (ANAC) + ICAO Annex 14
+ FAA ACs.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG hoje**. Backlog: WF-AKP-002
  focado em RBAC 154, Annex 14, PCN/ACN, concessões ANAC/Infraero.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Aeroportos/{obra}/02_Projeto/{LadoAr,LadoTerra,Balizamento}/` | Projeto — L+E                        |
| `04_IA/Manta-Maestro/Modelos/Aeroportos/`                           | Documentos-modelo — só leitura                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| AER-M-001   | Pista de pouso — projeto geométrico ANAC/ICAO             | RBAC 154 + Annex 14             |
| AER-M-002   | Pátio de aeronaves — dimensionamento                      | ICAO 9157                       |
| AER-M-003   | PCN/ACN — capacidade estrutural pavimento                 | ICAO 9157 vol. 3                |
| AER-M-004   | TPS — programa arquitetônico                              | Modelo Manta                    |

## 3. Knowledge Elements

**0 KEs próprios.** Backlog documentado.

## 4. Skills disponíveis

- `aeroportos.rwy_project` — dimensionamento RWY por classe RBAC/ICAO
- `aeroportos.pcn_check` — verificação PCN vs mix de aeronaves
- `aeroportos.tps_flow` — cálculo de vazão de passageiros

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Projeto de expansão de RWY/pátio                     | 02_Projeto/LadoAr                 | AER-M-001..003 + fan-out 05 + 07                  |
| DD de concessão aeroportuária                        | 12_Advisory                       | Fan-out S7 + 15 + 06 + 02                         |

Handoff frequente: **15 Advisory** (regulação ANAC), **06 Modelagem** (FCM de
concessão), **05 Orçamento**, **07 Cronograma**.
