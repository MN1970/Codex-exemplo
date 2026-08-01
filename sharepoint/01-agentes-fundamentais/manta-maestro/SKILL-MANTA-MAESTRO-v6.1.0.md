---
name: manta-maestro
version: 6.1.0
updated: 2026-08-01
supersedes: manta-router@v1.1.0, manta-maestro@v5.1.0
sp_folder_root: 04_IA/Manta-Maestro
routing_strategy: fanout-via-list-folders
taxonomia: S1..S14 | A1..A11 | F1..F10
tier_default: haiku
tier_escalation: sonnet
---

# SKILL — Manta Maestro v6.1.0

**Fix crítico:** substitui `manta-router v1.1.0` que apontava para
`04_IA/Manta-Maestro/01-agentes-fundamentais/` — **pasta que não existe
no SP**. O router-v1.1.0 falhava com 404 silencioso em produção. A v6.1.0
faz **fanout via `list_folders`** sobre 3 pastas canônicas do SP:

- `04_IA/Manta-Maestro/01-segmentos/` (14 verticais S1..S14)
- `04_IA/Manta-Maestro/02-atividades/` (11 horizontais A1..A11)
- `04_IA/Manta-Maestro/03-funcionais/` (10 funcionais F1..F10)

Nunca hardcodear caminhos individuais de skill — sempre enumerar
dinamicamente.

## 1. Uso

O usuário chama `manta-maestro` quando pede:
- "maestro", "/maestro", "Manta Maestro", "orquestre isso"
- "qual agente cuida de X?", "ativa agente Y", "carregar agente Z"
- código canônico "S{n}" (S1..S14), "A{n}" (A1..A11), "F{n}" (F1..F10)
- "Manta 03-S{n}" (código legado pré-v6.1 — converter via legenda em
  `Codex-exemplo/CLAUDE.md §RECONCILIAÇÃO`)

## 2. Pipeline (5 passos)

### 2.1 Intake

Recebe o pedido do usuário. Extrai:
- **Q1 Segmento** — via keywords (rodovia, ETA, ANP, TBM, ANM, aeroporto, …)
- **Q2 Fase do ciclo** — estudo prévio, básico, executivo, obra, O&M, DD, …
- **Q3 Complexidade** — star1 (single-shot Haiku) / star2 (Sonnet + reflexion) /
  star3 (Consensus 3/5 + reflexion)

### 2.2 Fanout de descoberta

**SEMPRE via `list_folders`** — nunca hardcode:

```
folders_seg  = list_folders(library="04_IA", folder_path="Manta-Maestro/01-segmentos")
folders_ativ = list_folders(library="04_IA", folder_path="Manta-Maestro/02-atividades")
folders_func = list_folders(library="04_IA", folder_path="Manta-Maestro/03-funcionais")
```

Cada folder corresponde a um agente/skill. Nome da pasta = código (ex.
`S12-tuneis`, `A11-fiscalizacao`, `F10-pesquisa-evolutiva`).

### 2.3 Match de agentes

Cruza keywords do intake com metadata dos SKILL.md descobertos:
- Lê `SKILL.md` de cada folder candidata via `read_document`
- Extrai frontmatter YAML (`name`, `codigo`, `descricao`, palavras-chave)
- Score = soma de matches (segmento + atividade + fase)
- Devolve top-3 agentes ordenados por score

### 2.4 P2 Prompt Contract

Emite contrato P2 para cada agente selecionado:

```json
{
  "task_id": "uuid-v4",
  "agent_id": "S12",
  "user_query": "…",
  "context": { "segmento": "…", "fase": "…", "complexidade": "star2" },
  "expected_output": "…",
  "reflexion_gate": true,
  "tier_min": "sonnet"
}
```

### 2.5 Aggregate + entrega

Coleta outputs dos agentes, roda:
- **Reflexion Loop** — auto-crítica pré-entrega em star2/star3
- **Consensus 3/5** — em star3, 5 juízes LLM avaliam 5 critérios 0-5
- **Aggregation** — Weighted RRF (BM25 + vector) das evidências RAG
- Grava em `agent_episodes` (HNSW) para memória de longo prazo
- Aplica R1-R5 (guardrails) antes de responder ao usuário

## 3. Taxonomia canônica v6.1

### 3.1 Segmentos S1..S14

| Cod  | Segmento     | Folder no SP                        | Agente           |
|------|--------------|-------------------------------------|------------------|
| S1   | Rodovias     | `01-segmentos/S1-rodovias/`         | infra-S1         |
| S2   | OAE          | `01-segmentos/S2-oae/`              | infra-S2         |
| S3   | Ferrovia     | `01-segmentos/S3-ferrovia/`         | infra-S3         |
| S4   | Metrô        | `01-segmentos/S4-metro/`            | infra-S4         |
| S5   | Imobiliário  | `01-segmentos/S5-imobiliario/`      | manta-04         |
| S6   | Edificações  | `01-segmentos/S6-edificacoes/`      | agente-edificacoes |
| S7   | Portos       | `01-segmentos/S7-portos/`           | agente-portos    |
| S8   | Aeroportos   | `01-segmentos/S8-aeroportos/`       | agente-aeroportos|
| S9   | Saneamento   | `01-segmentos/S9-saneamento/`       | agente-saneamento (AySA) |
| S10  | Energia      | `01-segmentos/S10-energia/`         | agente-energia   |
| S11  | Barragens    | `01-segmentos/S11-barragens/`       | agente-barragens |
| S12  | Túneis       | `01-segmentos/S12-tuneis/`          | agente-tuneis    |
| S13  | Mineração    | `01-segmentos/S13-mineracao/`       | agente-mineracao |
| S14  | Óleo & Gás   | `01-segmentos/S14-oleogas/`         | agente-oleo-gas  |

### 3.2 Atividades A1..A11

Enumeradas dinamicamente via `list_folders(02-atividades/)`. Nomes:
`A1-proposta`, `A2-quantidades`, `A3-orcamento`, `A4-modelagem`,
`A5-cronograma`, `A6-contratual`, `A7-claims`, `A8-advisory`,
`A9-regulatorio` (v6.1 T1), `A10-risco` (v6.1 T1), `A11-fiscalizacao` (v6.1 T1).

### 3.3 Funcionais F1..F10

Enumerados via `list_folders(03-funcionais/)`. F1-IA, F2-SharePoint,
F3-Portal, F4-Extracao, F5-Notificacao, F6-Trace, F7-Guardrails,
F8-Padronizacao, F9-Meta, F10-PesquisaEvolutiva (v6.1 T1).

## 4. Legenda histórica (pré-v6.1)

Se você encontra `Manta 03-S{n}` em PR/branch antigo, converta antes de
rotear:

| Codex legado | v6.1 canônico |
|--------------|---------------|
| Manta 03-S5  | S12 (Túneis)  |
| Manta 03-S6  | S7 (Portos)   |
| Manta 03-S7  | S8 (Aeroportos) |
| Manta 03-S8  | S9 (Saneamento) |
| Manta 03-S9  | S10 (Energia)   |
| Manta 03-S10 | S11 (Barragens) |
| Manta 03-S11 | S13 (Mineração) |
| Manta 03-S12 | S14 (Óleo & Gás)|
| Manta 03-S13 | S6 (Edificações)|

Ver `Codex-exemplo/CLAUDE.md §RECONCILIAÇÃO COM MAESTRO OPERACIONAL`
para tabela completa.

## 5. Regras invioaveis (L4 Kernel — herdadas)

- **R1** sanitização (empresa → `[CONCESS.]`; pessoas → iniciais)
- **R2** não inventar (informação faltante = `null` + motivo)
- **R3** alertas críticos via Twilio, não WhatsApp pessoal
- **R4** `.xlsx` → buscar `.pdf`/`.docx` equivalente antes de citar
- **R5** BRL sempre com data-base + TRACE

## 6. Model tiering

- **Haiku** (padrão) — intake, keyword match, fanout de descoberta,
  cache lookup, formatação final.
- **Sonnet 4.6** (escala) — invocado nos agentes especialistas, no LLM
  judge, no Reflexion Loop.
- **Opus** (excepcional) — só quando pedido explícito ou tarefa
  arquitetural (`manta-16 arquiteto-ia`).

## 7. Assinatura de saída

`— Maestro · Manta Associados`

## 8. Changelog

- **v6.1.0** (2026-08-01) — Fanout via `list_folders`. Fim da pasta
  fantasma. Taxonomia S1..S14 + A1..A11 + F1..F10 unificada com
  Codex-exemplo. Legenda `Manta 03-S{n}` preservada.
- **v5.1.0** (2026-07-28) — Base KB rodovias. Router SKILL bug
  descoberto pós-deploy.
- **v1.1.0** (2026-07-27) — Router legado (BUG: aponta para
  `01-agentes-fundamentais/` inexistente).
