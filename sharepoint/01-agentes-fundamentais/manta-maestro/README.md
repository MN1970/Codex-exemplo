# manta-maestro (Manta 00 / Manta 12) — v4.6

Roteador e regente do agentic OS da Manta Associados. É o ponto de
entrada canônico: recebe o pedido, lê fontes (F4), sintetiza objetivo,
compõe um DAG **S × A × D × F** de sub-agentes, apresenta plano em
handshake, aprova com o usuário e só então executa em paralelo. Aplica
as 5 regras invioláveis R1-R5 desde o PLAN.

## Quando invocar

Sempre que o usuário disser "maestro", "/maestro", "orquestre",
"qual agente cuida", "ativa agente", "carregar agente", ou citar
um código `Manta NN` / `S{n}.A{m}.D{k}`. Também quando o pedido for
multi-agente (multi-segmento, multi-disciplina, com handoff cross-agent).

## Quando NÃO invocar

- Tarefa trivial coberta por 1 sub-skill L1 direto (ex.: "leia este PDF").
- Já dentro de um agente vertical (S1..S14) rodando uma sub-tarefa.
- Usuário chamou nominalmente outra skill.

## 4 eixos (v4.6)

- **S1..S14** — 14 segmentos verticais (Rodovias, OAE, Ferrovia, Metrô,
  Imobiliário, Edificações, Portos, Aeroportos, Saneamento, Energia,
  Barragens, Túneis, Mineração, Óleo & Gás).
- **A1..A10** — 10 atividades (Proposta, Quantidades, Orçamento,
  Modelagem, Cronograma, Contratual, Claims, Advisory, Risco).
- **D01..D20** — 20 disciplinas técnicas (Geotecnia, Fundações,
  Hidrologia, Contenção, Estrutural, BIM, HVAC etc).
- **F1..F9** — 9 funcionais transversais (IA cognitiva, SharePoint,
  Portal, Extração, Notificação, TRACE, Guardrails, Padronização, Meta).

## Novidades v4.6

- **F1.b RAG hybrid** — bge-m3 1024d + BM25 pt via RRF k=60.
- **F1.c Learned Router** — MLP 384→128 com threshold de confidence 0.85.
- **F4.d Manta Cases** — coleção `mcs:` priority 120 (> academic 100).
- **F6.b LLM-as-a-judge** — Sonnet 4.6 amostra 10% em 5 critérios.

## Estrutura desta pasta

```
manta-maestro/
├── SKILL.md                        # definição canônica (v4.6)
├── README.md                       # este arquivo
├── refs/
│   ├── routing-table-v4.6.md       # tabela keyword→segmento (S1-S14)
│   └── handoffs-cross-agent.md     # 8 cenários canônicos v4.5
└── prompts/
    ├── intake-ambiguo.md           # 5 exemplos de resolução Q1
    └── handoff-tsf-barragem-mina.md # 1 exemplo detalhado S10↔S11
```

## Reconciliação Codex ↔ Maestro operacional

A numeração `Manta 03-S{n}` do Codex-exemplo NÃO bate 1:1 com o
`S{n}` operacional do Maestro (ex.: Codex `03-S5 Túneis` = operacional
`S12`; Codex `03-S13 Edificações` = operacional `S6`). Tabela completa
em §3.1 do `SKILL.md`.

## Distribuição multi-canal (V7)

Este agente é publicado em 4 formatos pelo script
`manta-hub/scripts/publish_agents.py` a partir deste SKILL.md:
Claude Code (`.claude/agents/manta-maestro.md`), claude.ai Projects
(`manta-maestro.zip` com README + refs + starters), Claude Skills v2
(zip com manifest.json) e Cowork workspace (`manta-maestro.json`).
GH Action `.github/workflows/publish-agents.yml` empacota em push de
tag `v*`.

## Onboarding

1. Ler o `SKILL.md` completo (7 fases + R1-R5 + 4 eixos).
2. Consultar `refs/routing-table-v4.6.md` para as regras keyword→S.
3. Ler `refs/handoffs-cross-agent.md` para entender os 8 cenários
   canônicos de coordenação multi-agente.
4. Testar com um dos exemplos em `prompts/intake-ambiguo.md`.
