# refs/p2-contract-template.md — manta-maestro

Referência canônica do **Prompt Composition Contract (P2)** — Upgrade B
do roadmap v4.7 (MNT-IA-20260712-001, §3). O P2 é o pacote formal que o
Maestro entrega a cada subagente que ele ativa. Substitui o "system
prompt herdado" e o "brief free-form" por um contrato de 4 elementos
obrigatórios que garante isolamento de contexto, previsibilidade e
auditabilidade.

Fonte: Wang et al. 2026 "AgentFactory" (NeurIPS) §4.2 + Anthropic 2025
"Building Effective Agents" §context-isolation. Ver `SKILL.md` §14.B do
Maestro para gating e política de handoff.

---

## 1. Definição — os 4 elementos obrigatórios

Todo P2 emitido pelo Maestro DEVE conter:

1. **`objective`** — 1 sentença clara do que se pede ao subagente,
   incluindo o output esperado (formato + destino).
2. **`context_compressed`** — resumo denso da tarefa em ≤400 tokens,
   citando apenas o essencial (não passa a conversa inteira). O
   Maestro pré-processa via Haiku 4.5 quando o intake for longo.
3. **`skills_preloaded`** — lista de slugs (SP) das skills que o
   subagente DEVE consultar antes de responder. Progressive
   disclosure: só carrega o que é relevante.
4. **`success_criteria`** — 2-5 checks binários que definem
   "entregue vs não entregue". O Reflexion Loop (Upgrade A) usa
   estes critérios para decidir se re-executa.

Opcional (permitido, mas não obrigatório):
- `deadline_hint` — se a tarefa é star3 ou tem SLA humano
- `handoff_targets` — outros agentes que este pode chamar
- `budget_usd` — orçamento máximo antes de escalar (padrão 0.30)

---

## 2. Template YAML pronto para cópia

```yaml
# P2 Contract — emitido por Manta 00 (Maestro) para <agente>
p2_contract:
  version: "1.0"
  emitted_by: "manta-maestro"
  emitted_at: "2026-07-13T14:22:00Z"
  target_agent: "<slug>"      # ex: agente-portos, manta-15-advisory
  task_id: "<uuid>"           # rastreável no agent_episodes

  objective: >
    <1 sentença: o que fazer + output esperado + destino>

  context_compressed: |
    <resumo em ≤400 tokens; incluir apenas fatos, restrições,
    entregável esperado. NÃO incluir chit-chat, nem contexto de
    outros agentes irrelevantes.>

  skills_preloaded:
    - "<slug-skill-1>"
    - "<slug-skill-2>"

  success_criteria:
    - "<critério binário 1>"
    - "<critério binário 2>"
    - "<critério binário 3>"

  # opcionais
  handoff_targets: ["<agente-x>", "<agente-y>"]
  budget_usd: 0.30
  deadline_hint: "star2"      # star1/star2/star3
```

---

## 3. Exemplos concretos preenchidos

### 3.1 agente-portos — A2 quantitativos de dragagem

```yaml
p2_contract:
  target_agent: "agente-portos"
  objective: >
    Estimar volume de dragagem inicial + manutenção anual para
    aprofundamento do canal de acesso do TUP Porto Central de -14m
    para -17m CD, entregando tabela m³ por trecho em Markdown.
  context_compressed: |
    Cliente: Porto Central (Presidente Kennedy/ES). Canal atual 12km,
    largura 220m, cota -14m CD. Meta -17m CD para Capesize. Sedimento:
    silte marinho leve (batimetria 2024). PIANC 158 aplicável. Não
    considerar bota-fora offshore (assumir aterro hidráulico interno).
  skills_preloaded:
    - "portos-quantitativos-dragagem-pianc-158"
    - "portos-batimetria-2024-porto-central"
  success_criteria:
    - "Tabela m³ tem colunas: trecho, área, prof_atual, prof_meta, volume"
    - "Cita PIANC 158 explicitamente na justificativa da folga de dragagem"
    - "Volume total ± 15% da baseline histórica de projetos similares"
  budget_usd: 0.20
```

### 3.2 agente-tuneis — A3 orçamento preliminar NATM

```yaml
p2_contract:
  target_agent: "agente-tuneis"
  objective: >
    Produzir orçamento paramétrico (R$/m de túnel) para trecho NATM de
    850m em solo mole/rocha alterada, entregando planilha SICRO-like em
    Markdown com discriminação de escavação, revestimento primário,
    impermeabilização e drenagem.
  context_compressed: |
    Trecho urbano SP, Ø escavado 12m, cobertura 8-25m, NA em -6m.
    Método observacional Peck OBRIGATÓRIO (portaria CBH). SICRO SP
    2024/06. Não incluir emboque/desemboque (já orçado em OAE).
  skills_preloaded:
    - "tuneis-parametrico-natm-solo-mole"
    - "tuneis-sicro-sp-2024-06-referencias"
  success_criteria:
    - "R$/m está em faixa 55k-95k (baseline NATM SP urbano)"
    - "Discrimina os 4 grupos (escavação/revest/imperm/drenagem)"
    - "Cita método observacional Peck e monitoramento SIN-M"
  budget_usd: 0.25
```

### 3.3 agente-barragens — A8 advisory de descaracterização

```yaml
p2_contract:
  target_agent: "agente-barragens"
  objective: >
    Emitir parecer técnico curto (≤600 palavras) sobre viabilidade da
    descaracterização de barragem alteada a montante em Nova Lima até
    2027, com riscos residuais e vetores de aceleração.
  context_compressed: |
    Barragem X, DAM 2, HHP baixo, alteamento a montante desde 1998.
    Rejeitos siltosos NP. Cliente é proprietária da mina. Lei 14.066
    prazo 2027. Já existe estudo de estabilidade IPT 2023 (r_max 1.2).
  skills_preloaded:
    - "barragens-descaracterizacao-lei-14066"
    - "barragens-kes-fernandes-2020-mendes-2022"
  success_criteria:
    - "Cita Lei 14.066 e Res ANM 95 explicitamente"
    - "Identifica ao menos 3 riscos residuais + 2 mitigantes"
    - "Recomendação FINAL é acionável (executar / adiar / abortar)"
  handoff_targets: ["agente-mineracao", "manta-02-contratual"]
  deadline_hint: "star3"
  budget_usd: 0.40
```

### 3.4 manta-15-advisory — A10 análise de risco de investimento

```yaml
p2_contract:
  target_agent: "manta-15-advisory"
  objective: >
    Analisar risco-retorno de aquisição de concessão rodoviária
    federal Fase 5, entregando memo executivo em Markdown com TIR
    real, principais riscos e comparativo com 2 benchmarks públicos.
  context_compressed: |
    Ativo: lote 5.700 km SC/PR/SP, TIR referencial 8.5% real, prazo
    30 anos. Cliente é fundo brasileiro. R1 do EPE aplicável. Comparar
    com CCR Nova Dutra (2021) e Motiva EcoRodovias (2023).
  skills_preloaded:
    - "advisory-concessao-rodoviaria-fase5"
    - "advisory-benchmarks-motiva-ccr"
    - "academic-kes-modelagem-concessoes"
  success_criteria:
    - "TIR real reportada em cenários base/pessimista/otimista"
    - "Cita ao menos 5 riscos com probabilidade × impacto"
    - "Comparativo tem 2 benchmarks nomeados"
  handoff_targets: ["manta-05-orcamento"]
  budget_usd: 0.50
```

### 3.5 manta-16-arquiteto-ia — A1 proposta de novo agente

```yaml
p2_contract:
  target_agent: "manta-16-arquiteto-ia"
  objective: >
    Redigir proposta técnica (SKILL.md draft) para novo agente
    "agente-siderurgia" (S15), incluindo escopo, adjacências,
    palavras-chave de routing e coleção RAG inicial.
  context_compressed: |
    Motivação: 2 clientes com plantas siderúrgicas (CSN Volta Redonda,
    Usiminas Ipatinga) pediram advisory em 2026Q2. Adjacências: S13
    mineração (upstream), S6 edificações (galpão), S14 óleo & gás
    (utilities). NÃO cobrir processo metalúrgico — só o civil/infra.
  skills_preloaded:
    - "arquiteto-ia-template-skill-md"
    - "arquiteto-ia-processo-de-criacao-agente"
    - "academic-kes-arquitetura-multi-agent"
  success_criteria:
    - "SKILL.md draft tem os 12 blocos canônicos"
    - "Palavras-chave de routing NÃO colidem com S13/S14"
    - "Justificativa de escopo referencia os 2 clientes reais"
  deadline_hint: "star2"
  budget_usd: 0.60
```

---

## 4. Anti-patterns (o que NÃO fazer)

### ❌ Anti-pattern 1: system prompt herdado

O Maestro NÃO deve simplesmente encaminhar o system prompt dele para o
subagente. Cada subagente tem seu próprio `SKILL.md` que já define
identidade. P2 é um *contrato de tarefa*, não uma injeção de persona.

### ❌ Anti-pattern 2: brief free-form

Errado: `"olha, dá uma olhada nesse porto aí e me diz o custo da
dragagem"`. Certo: objective + context_compressed + success_criteria
explícitos. Free-form quebra o Reflexion Loop (não há critério para
avaliar) e a memória episódica (não indexável).

### ❌ Anti-pattern 3: contexto não comprimido

Passar a conversa inteira como `context_compressed`. O ponto do P2 é
justamente o *isolamento de contexto*: o subagente recebe só o que
importa. Se o intake do usuário tem 8k tokens, o Maestro comprime para
≤400 antes de emitir o P2. Use Haiku 4.5 (skill `maestro-compressor`).

### ❌ Anti-pattern 4: subagente sem skill pré-carregada

Errado: `skills_preloaded: []`. Certo: sempre listar ≥1 skill relevante.
Progressive disclosure só funciona se o Maestro fizer o trabalho de
seleção — deixar o subagente descobrir sozinho gasta contexto e turnos.

### ❌ Anti-pattern 5: success_criteria vago

Errado: `"resposta boa"`. Certo: `"cita PIANC 158"`, `"tabela tem N
linhas"`, `"TIR está entre 6% e 12%"`. Critério tem que ser *binário*
(passou/não passou) para o Reflexion Loop funcionar.

---

## 5. Rastreabilidade

- **Emissão**: cada P2 emitido é logado em `agent_episodes` (v4.7
  Upgrade C, coluna `p2_contract JSONB`).
- **Auditoria**: LLM-as-a-judge (v4.6 V5) avalia se o subagente
  cumpriu os `success_criteria` — score < 3 aciona flag.
- **CI**: `.github/workflows/skill-sync-check.yml` (v4.5) valida que
  todo agente ativado teve P2 emitido; ausente ⇒ warning.

---

## Ver também

- `SKILL.md` §14.B — política operacional do P2
- `reflexion-loop-guide.md` — como o Reflexion consome `success_criteria`
- `episodic-memory-schema.md` — como o P2 é indexado em `agent_episodes`
- Roadmap MNT-IA-20260712-001 §3 — motivação e prior art
