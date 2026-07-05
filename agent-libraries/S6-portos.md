# Agent Library — Manta 03-S6 Portos (agente-portos)

Agente vertical **Portos e Hidrovias**. Cobre terminais marítimos (contêiner,
granel, ro-ro, offshore), terminais fluviais/hidroviários e apoio (dragagem,
molhe, cais, dolfins).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG hoje**. Backlog: WF-AKP-002
  focado em ANTAQ, PIANC, Marinha, autoridades portuárias.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Portos/{obra}/02_Projeto/{Cais,Dragagem,Retroarea}/`   | Projeto — L+E                                  |
| `03_Projetos/Portos/{obra}/06_Operacao/`                            | O&M — L+E                                      |
| `04_IA/Manta-Maestro/Modelos/Portos/`                               | Documentos-modelo — só leitura                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| PRT-M-001   | Batimetria + dragagem — memorial                          | PIANC + Marinha                 |
| PRT-M-002   | Cais / píer — estrutura marítima                          | PIANC WG                        |
| PRT-M-003   | Defensa e amarração                                       | PIANC MarCom                    |
| PRT-M-004   | Arrendamento portuário — análise ANTAQ                    | ANTAQ Resolução                 |

## 3. Knowledge Elements

**0 KEs próprios.** Backlog documentado.

## 4. Skills disponíveis

- `portos.batimetria_parse` — leitura de batimetria digitalizada
- `portos.dragagem_calc` — volumes de dragagem por profundidade projeto
- `portos.antaq_check` — checagem regulatória de arrendamento

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Projeto de terminal / expansão                       | 02_Projeto/*                      | PRT-M-001..003 + fan-out 05 + 07                  |
| Arrendamento portuário                               | 12_Advisory                       | PRT-M-004 + fan-out S6 + 15 + 06                  |

Handoff frequente: **15 Advisory** (regulação ANTAQ), **05 Orçamento**, **07
Cronograma**, **04 Imobiliário** (retroárea).
