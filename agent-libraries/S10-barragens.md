# Agent Library — Manta 03-S10 Barragens (agente-barragens)

Agente vertical **Barragens** — concreto (CFRD/CCR/RCC), terra, enrocamento,
rejeitos. Cobre estudo → obra → O&M → DD → descaracterização (Lei 12.334/2010,
ANM/ANA, PNSB, ICOLD/CBDB).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG hoje**. Backlog: WF-AKP-002
  focado em ICOLD, CBDB, SIGBM, alteamento, dry stack pós-Fundão/Brumadinho.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Barragens/{obra}/02_Projeto/{Concreto,Terra,Rejeitos}/` | Projeto — L+E                                 |
| `03_Projetos/Barragens/{obra}/06_Seguranca/`                        | PAE, PAEBM, ZAS, ZSS — L+E                     |
| `03_Projetos/Barragens/{obra}/08_Descaracterizacao/`                | Alteamentos a montante — L+E                   |
| `04_IA/Manta-Maestro/Modelos/Barragens/`                            | Documentos-modelo — só leitura                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| BAR-M-001   | Barragem de concreto CCR — memorial                       | ICOLD Bulletin 165              |
| BAR-M-002   | Barragem de rejeitos — dry stack + filtragem              | Pós-Brumadinho                  |
| BAR-M-003   | PAE / PAEBM — plano de ação emergencial                   | Lei 12.334/2010                 |
| BAR-M-004   | Descaracterização de alteamento a montante                | ANM Resolução 32/2020           |
| BAR-M-005   | Análise HHP (High Hazard Potential)                       | ICOLD                           |

## 3. Knowledge Elements

**0 KEs próprios.** Backlog documentado.

## 4. Skills disponíveis

- `barragens.ccr_project` — projeto de CCR
- `barragens.rejeitos_drystack` — dimensionamento dry stack
- `barragens.pae_gen` — geração de PAE/PAEBM
- `barragens.descarac_plan` — plano de descaracterização

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Projeto de nova barragem                             | 02_Projeto/*                      | BAR-M-001 ou 002 + fan-out 05 + 07                |
| Barragem existente — PAE/PAEBM                       | 06_Seguranca                      | BAR-M-003 + BAR-M-005                             |
| Descaracterização (alteamento montante pós-Fundão)   | 08_Descaracterizacao              | BAR-M-004                                          |
| DD/M&A de barragem                                   | 12_Advisory                       | Fan-out S10 + 15 + 06                             |

Handoff frequente: **S4 Metrô** (túneis de adução — retroanálise geotécnica),
**S9 Energia** (barragens em UHE/PCH), **15 Advisory** (regulação ANM/ANA),
**05 Orçamento**, **07 Cronograma**.
