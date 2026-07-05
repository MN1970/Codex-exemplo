# Agent Library — Manta 14 Apresentações (manta-14-pptx)

Agente **Apresentações** (Sonnet). Escopo: geração de PPTX corporativo,
executive summaries, decks de proposta, painéis de status, artefatos visuais.
Consome outputs de outros agentes e formata para audiência humana.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG** (não faz sentido — este
  agente formata, não gera conhecimento). Templates de PPTX são o "starter kit" real.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/13_Apresentacoes/`                   | Decks do projeto — L+E                         |
| `01_Comercial/Propostas/Decks/`                                     | Decks comerciais — L+E                         |
| `04_IA/Manta-Maestro/Modelos/Apresentacoes/`                        | Templates PPTX + palette + fonts               |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| APR-M-001   | Deck padrão Manta (16:9, dark + light)                    | Design system Manta             |
| APR-M-002   | Status report mensal — obra em execução                   | Modelo Manta                    |
| APR-M-003   | Executive summary — parecer/pleito de 10 slides           | Modelo Manta                    |
| APR-M-004   | Proposta comercial — deck de 20-30 slides                  | Modelo Manta                    |
| APR-M-005   | Kick-off de projeto — deck de abertura                    | Modelo Manta                    |

## 3. Knowledge Elements

**0 KEs próprios.** Este agente **consome** outputs de outros — não gera
conhecimento primário. Retrieval é sobre templates de layout, não sobre KEs.

## 4. Skills disponíveis

- `pptx.build_deck` — monta PPTX a partir de estrutura + template
- `pptx.executive_summary` — condensa parecer/relatório em 10 slides
- `pptx.status_report` — monta APR-M-002 a partir de KPIs de 05, 07
- `pptx.chart_render` — gera gráfico (Curva S, Monte Carlo hist, FCM) em PNG

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Encerramento de análise técnica de 01, 07 ou 15      | 13_Apresentacoes                  | APR-M-003 (executive summary)                     |
| Reunião mensal de acompanhamento                     | 13_Apresentacoes                  | APR-M-002 preenchida com dados de 05 + 07         |
| Handoff de 13 BD (proposta comercial)                | Propostas/Decks                   | APR-M-004 + APR-M-005 no kickoff                  |

Handoff frequente: **todos os agentes** (formata output de todos). Handoff
inverso raro — quase sempre é o último elo antes do usuário humano.
