# Agent Library — Manta 00 Maestro (router)

Referência canônica de trabalho do **Router principal**. Formato ligeiramente
diferente dos outros libraries: **o Maestro não consome KEs** (não gera
artefato técnico), então as seções 2 e 3 ficam substituídas por *routing
rules* e *escalation matrix*.

Complementa `sharepoint/01-agentes-fundamentais/agente-maestro/SKILL.md`
(o `SKILL.md` é *como* orquestrar; este é *quais rotas existem*).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `04_IA/Manta-Maestro/Traces/`                                       | Log estruturado de todas as chamadas — E       |
| `04_IA/Manta-Maestro/Traces/Escalations/`                            | Casos escalados para Opus (auditoria)          |
| `04_IA/Manta-Maestro/Traces/Parallel-Runs/`                          | Fan-outs multi-agente (auditoria)              |
| Todos os `03_Projetos/*/12_Advisory/` e demais                       | Leitura de contexto para roteamento            |

## 2. Regras de roteamento (Q1 → agente)

Sincronizado com `CLAUDE.md §ROUTING`. Sumário operacional:

| Q1 (segmento)       | Agente(s) primário(s)   | Blocos KE relevantes                  |
|---------------------|-------------------------|---------------------------------------|
| 1 Rodovia           | S1                      | B1                                    |
| 2 OAE               | S2                      | B8                                    |
| 3 Ferrovia          | S3                      | (backlog)                             |
| 4 Metrô             | S4                      | B6                                    |
| 5 Túneis            | S2 ou S4 (por contexto) | B6 + B8                               |
| 6 Portos            | S6                      | (backlog)                             |
| 7 Aeroportos        | S7                      | (backlog)                             |
| 8 Saneamento        | S8                      | B7                                    |
| 9 Energia           | S9                      | (backlog)                             |
| 10 Barragens        | S10                     | (backlog)                             |
| Q1 múltiplo         | **Fan-out obrigatório** | união dos blocos                      |

Cruzamento com Q2 (fase):

| Q2                  | Horizontais acionados em paralelo          |
|---------------------|--------------------------------------------|
| A/B Estudo/Básico   | 05 Orçamento + 07 Cronograma               |
| C Executivo         | 05 + 07 + 06 Modelagem                     |
| D Obra              | 07 + 05 + eventualmente 01 Claims          |
| E O&M                | 07 + 15 Advisory + 03-S* específico        |
| F Licitação         | 13 BD + 05 + 15                            |
| G DD/M&A            | 15 + 06 + 02 Contratual                    |
| H Descomissionamento | 15 + segmento + 06                         |

## 3. Escalation matrix (tier)

| Condição                                             | Ação                                             |
|-------------------------------------------------------|--------------------------------------------------|
| `intake.confidence < 0.7`                             | Haiku → Sonnet mesmo turno                       |
| `subagents.disagree == true` (2+ pareceres conflitam) | Sonnet → Opus para resolver                      |
| `user.marks_reroute == true` (feedback humano)         | Novo turno em tier superior                      |
| `budget.remaining < threshold`                        | Segue no tier atual, log warning                 |
| `pleito.value > R$ 5M`                                | Opus obrigatório em 01, 02, 15 (regra política)  |

Traces em `04_IA/Manta-Maestro/Traces/Escalations/{YYYY-MM-DD}/{trace_id}.json`.

## 4. Skills disponíveis (do router)

- `maestro.route` — classifica prompt e emite lista de agentes
- `maestro.fan_out` — despacha N agentes em paralelo, coleta N respostas
- `maestro.synthesize` — agrega respostas paralelas em uma síntese única
- `maestro.escalate` — sobe tier segundo escalation matrix
- `maestro.trace` — grava o `manta_trace` estruturado

## 5. Padrões de uso (quando o Maestro delega)

| Sinal no prompt do usuário                          | Rota decidida                                    |
|-----------------------------------------------------|--------------------------------------------------|
| Menciona 1 segmento + 1 fase                        | Serial: vertical → horizontal(is) por fase       |
| Menciona 2+ segmentos                                | **Fan-out**: verticais em paralelo → agrega       |
| Menciona "pleito", "reequilíbrio", "TIA"             | Fan-out: 01 + 02 + 15 (+ 06 se envolver TIR)     |
| Menciona "estudo prévio", "EVTE"                     | Fan-out: vertical + 05 + 07                      |
| Menciona "DD", "due diligence"                       | Fan-out amplo: 15 + 06 + 02 + vertical(is)       |
| Pergunta puramente conceitual (sem projeto)          | 16 Arquiteto-IA + retrieval livre                |

**Regra dourada** (do SKILL.md cláusula 1): se as tarefas geradas são
independentes, **paralelo por padrão**. Serial só com justificativa no trace.
