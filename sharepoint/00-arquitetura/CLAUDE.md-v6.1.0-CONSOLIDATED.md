# CLAUDE.md — Manta Maestro (Agent Registry) v6.1.0 CONSOLIDATED

**Versão:** 6.1.0 (2026-08-01)
**Escopo:** SharePoint mirror do `Codex-exemplo/CLAUDE.md` v6.1 + orientações
operacionais do SP-native. Substitui `CLAUDE.md-v5.1.0-CONSOLIDATED.md`.

---

## Sumário

- [1. Taxonomia unificada S1..S14 + A1..A11 + F1..F10](#1-taxonomia-unificada)
- [2. Router — Manta 00 (fanout via `list_folders`)](#2-router)
- [3. Pastas SP autoritativas](#3-pastas-sp-autoritativas)
- [4. Coleções RAG Supabase](#4-colecoes-rag-supabase)
- [5. Camadas do Maestro (v4.7 → v4.9 → v6.1)](#5-camadas)
- [6. Migração v6.1 pendente (gate MN duro)](#6-migracao-pendente)
- [7. Regras L4 Kernel (invioaveis)](#7-regras-l4)
- [8. Legenda histórica pré-v6.1](#8-legenda-historica)

---

## 1. Taxonomia unificada

### 1.1 Segmentos verticais S1..S14

| Cod  | Segmento     | Agente                   | Status v6.1                |
|------|--------------|--------------------------|----------------------------|
| S1   | Rodovias     | agente-infraestrutura S1 | operacional (ambos)        |
| S2   | OAE          | agente-infraestrutura S2 | operacional (ambos)        |
| S3   | Ferrovia     | agente-infraestrutura S3 | operacional (ambos)        |
| S4   | Metrô        | agente-infraestrutura S4 | operacional (ambos)        |
| S5   | Imobiliário  | manta-04 (SP-native)     | operacional (SP)           |
| S6   | Edificações  | agente-edificacoes       | v6.1 (era `Manta 03-S13`)  |
| S7   | Portos       | agente-portos            | v6.1 (era `Manta 03-S6`)   |
| S8   | Aeroportos   | agente-aeroportos        | v6.1 (era `Manta 03-S7`)   |
| S9   | Saneamento   | agente-saneamento (AySA) | v6.1 (era `Manta 03-S8`)   |
| S10  | Energia      | agente-energia           | v6.1 (era `Manta 03-S9`)   |
| S11  | Barragens    | agente-barragens         | v6.1 (era `Manta 03-S10`)  |
| S12  | Túneis       | agente-tuneis            | v6.1 T2 (era `Manta 03-S5`) |
| S13  | Mineração    | agente-mineracao         | v6.1 T2 (era `Manta 03-S11`) |
| S14  | Óleo & Gás   | agente-oleo-gas          | v6.1 T2 (era `Manta 03-S12`) |

### 1.2 Atividades horizontais A1..A11

`A1-proposta, A2-quantidades, A3-orcamento, A4-modelagem, A5-cronograma,
A6-contratual, A7-claims, A8-advisory, A9-regulatorio, A10-risco,
A11-fiscalizacao`. A9/A10/A11 portadas do SP para o repo em v6.1 T1.

### 1.3 Funcionais F1..F10

`F1-IA, F2-SharePoint, F3-Portal, F4-Extracao, F5-Notificacao, F6-Trace,
F7-Guardrails, F8-Padronizacao, F9-Meta, F10-PesquisaEvolutiva`. F10
portada do SP em v6.1 T1.

### 1.4 Disciplinas D01..D23

Adotada taxonomia SP integral. Referência em
`03-funcionais/F10-pesquisa-evolutiva/refs/disciplinas.md` (pendente
expansão).

---

## 2. Router

O `manta-maestro v6.1.0` substitui `manta-router v1.1.0` (broken, apontava
para pasta inexistente). Fanout via `list_folders`:

```
list_folders(library="04_IA", folder_path="Manta-Maestro/01-segmentos")
list_folders(library="04_IA", folder_path="Manta-Maestro/02-atividades")
list_folders(library="04_IA", folder_path="Manta-Maestro/03-funcionais")
```

Nunca hardcode caminhos individuais. Ver
`SKILL-MANTA-MAESTRO-v6.1.0.md` para pipeline completo (5 passos).

---

## 3. Pastas SP autoritativas

```
04_IA/Manta-Maestro/
├── 00-arquitetura/            # docs de arquitetura (este + ARQUITETURA-v6.1)
├── 01-segmentos/              # S1..S14 (fanout do router)
├── 02-atividades/             # A1..A11 (fanout do router)
├── 03-funcionais/             # F1..F10 (fanout do router)
├── 04-disciplinas/            # D01..D23 (subskills técnicas)
├── 04-routing-migration-v4.2/ # legado, congelado
├── 05-sub-skills/             # sub-skills do Maestro (refs, prompts)
├── 06-exemplares/             # exemplos e templates
├── 07-execucoes/              # log de execuções
├── 08-rubricas/               # rubricas de aval + juízes
├── 09-base-conhecimento/      # KB estruturada (rodovias etc.)
├── 99-backup/                 # versões arquivadas
└── 99-meta/                   # meta-config
```

---

## 4. Coleções RAG Supabase

Projeto `ogxxgvgtulrbbppshjie` (sa-east-1) — Maestro core:

| Coleção            | Prefixo | Escopo v6.1                          |
|--------------------|---------|--------------------------------------|
| saneamento         | san:    | S9 (Saneamento — AySA)                |
| energia            | ene:    | S10 (Energia)                         |
| portos             | por:    | S7 (Portos)                           |
| aeroportos         | aer:    | S8 (Aeroportos)                       |
| barragens          | bar:    | S11 (Barragens)                       |
| tuneis             | tun:    | S12 (Túneis)                          |
| mineracao          | min:    | S13 (Mineração)                       |
| oleo-gas           | ogs:    | S14 (Óleo & Gás)                      |
| edificacoes        | edi:    | S6 (Edificações)                      |
| academic-knowledge | ake:    | transversal (36 teses + 52 KEs)       |
| manta-cases        | mcs:    | transversal (23 KEs seed v4.9)        |

Projeto `xgluoaaymbdzbbudnwrh` (us-east-2) — KB rodovias S1 (acesso
pendente MN).

---

## 5. Camadas

1. **Complexity Detection** (Q0/Q3 intake) — star1/star2/star3
2. **Reflexion Loop** (Upgrade A, v4.7) — auto-crítica pré-entrega
3. **Consensus 3/5** (v4.6 V5, Sonnet 4.6) — 5 critérios 0-5
4. **Aggregation** — Weighted RRF (BM25 + vector)
5. **ML Intelligence** (v4.6 V1) — MLP 384→128 (learned router)
6. **Episodic Memory** (Upgrade C, v4.7) — HNSW + cron consolidate
7. **Learning Loop v4.9** — judge → akp_curation_backlog (prod 2026-07-19)

---

## 6. Migração pendente

`Codex-exemplo/supabase/migrations/2026_08_01_v6_1_taxonomy_reconciliation.sql`
— UPDATE `03-S{n}` → `S{n}` unificado + INSERT 3 A + 1 F. **Não aplicada
em prod** — gate MN duro. Bloco DOWN de rollback incluso.

---

## 7. Regras L4 Kernel

- **R1** sanitização (empresa → `[CONCESS.]`; pessoas → iniciais)
- **R2** não inventar (`null` + motivo quando informação falta)
- **R3** alertas críticos via Twilio, não WhatsApp pessoal
- **R4** `.xlsx` → buscar `.pdf`/`.docx` antes de citar
- **R5** BRL sempre com data-base + TRACE

---

## 8. Legenda histórica

`Manta 03-S{n}` = código Codex legado até v4.9. Aposentado em v6.1
(2026-08-01). Conversão:

| Codex legado | v6.1 canônico |
|--------------|---------------|
| Manta 03-S1..S4 | S1..S4 (idem) |
| Manta 03-S5  | S12 (Túneis)  |
| Manta 03-S6  | S7 (Portos)   |
| Manta 03-S7  | S8 (Aeroportos) |
| Manta 03-S8  | S9 (Saneamento) |
| Manta 03-S9  | S10 (Energia)   |
| Manta 03-S10 | S11 (Barragens) |
| Manta 03-S11 | S13 (Mineração) |
| Manta 03-S12 | S14 (Óleo & Gás)|
| Manta 03-S13 | S6 (Edificações)|

Tabela canônica também em `.claude/agents/manta-maestro.md` §3.1 e
`Codex-exemplo/CLAUDE.md §RECONCILIAÇÃO`.

---

**Autor:** Maestro · Manta Associados · 2026-08-01
**Substitui:** `CLAUDE.md-v5.1.0-CONSOLIDATED.md` (arquivar em `99-backup/`).
