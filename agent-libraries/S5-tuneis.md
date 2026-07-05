# Agent Library — Manta 03-S5 Túneis (coberto por S2/S4)

Agente vertical **Túneis** — status oficial no CLAUDE.md v4.2: **coberto por
S2 (túneis rodoviários) + S4 (túneis metroferroviários)**. Este library serve
como *cross-reference*, não como pacote autônomo.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** cross-reference. **Não tem KEs próprios** — usa os de S2 e S4.

---

## Roteamento

| Contexto                                             | Agente a usar                                    |
|------------------------------------------------------|--------------------------------------------------|
| Túnel rodoviário (BR-116, BR-101…)                    | **S2 OAE** — mesma norma NBR 7187 + inspeção     |
| Túnel metroferroviário urbano                         | **S4 Metrô** — TBM/EPB, NATM, PSD                |
| Túnel de adução hidráulica (barragem/PCH)             | **S10 Barragens** (leading) + S4 (retroanálise)  |
| Túnel imerso (subaquático, ex.: interligação)         | **S6 Portos** + S2 (estrutural)                  |

## KEs relevantes (via S2 + S4)

- **De S2:** KE-005/006 (Monte Carlo + fluência aplicáveis a estrutura de
  revestimento), KE-040/041/042 (inspeção — se túnel exige monitoramento
  patológico como OAE).
- **De S4:** KE-003/004 (Plaxis TBM), KE-009/010 (NATM Plaxis), KE-023
  (recalques L2-Verde).

## Documentos-modelo

Não há templates próprios. Usar OAE-M-001 (memorial estrutural) ou MTR-M-001/002
(FEM/NATM) conforme contexto.

## Padrões de uso

Sempre despachar em **paralelo** para S2 + S4 no fan-out inicial se o contexto
for ambíguo. O agente melhor posicionado responde primeiro; o outro contribui
com dados adjacentes.

Handoff frequente: **S2 OAE**, **S4 Metrô**, **S10 Barragens** (túneis de
adução), **S6 Portos** (túneis imersos).
