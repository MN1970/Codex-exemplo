# LangGraph 0.2+ vs CrewAI 2.0 — Análise para Manta Maestro

**Data**: 2026-08-02
**Autor**: Manta Arquiteto de IA (Manta 15/16)
**Escopo**: escolha de framework de orquestração multi-agente para a camada
de produção do Manta Maestro (20 agentes — Eixo 1 horizontais + Eixo 2
verticais S1-S10 — ver `CLAUDE.md` v4.2).
**Relacionado**: `docs/RESEARCH-MODERN-AGENT-ORCHESTRATION.md` (deixou a
decisão em aberto, "decidir via PoC"). Este documento fecha a decisão.

---

## 1. Contexto — por que essa escolha importa agora

O Maestro hoje roteia por regex simples no Q1 do intake (seção ROUTING do
`CLAUDE.md`) e os 20 agentes existem como subagents/skills nativos do
Claude Code (`.claude/agents/*.md`). Isso funciona bem dentro do Claude
Code, mas não serve como motor de orquestração para o backend de produção
(FastAPI, camada "Skills/Agentes" do PK_07) quando o roteamento precisa de
estado persistente, retomada após falha, paralelismo controlado e trilha
de auditoria fora do terminal.

LangGraph e CrewAI são as duas opções mais maduras hoje para essa camada.
A pergunta não é "qual framework é melhor" em abstrato — é qual se encaixa
nos 5 pilares obrigatórios da Manta: modular, auditável, evolutivo,
econômico, anti-vazamento.

---

## 2. Tabela comparativa

| Dimensão | LangGraph 0.2+ | CrewAI 2.0 | Vencedor |
|---|---|---|---|
| **Modelo de execução** | Grafo de estado explícito (nós + arestas + schema compartilhado); roteamento por código (`if/else`, `match`) | Times de agentes com papel/objetivo/história (Crews) + camada determinística por evento (Flows, `@start`/`@listen`) | — |
| **Observabilidade nativa** | LangSmith: tracing automático, contagem de tokens, latência por nó, replay, versionamento de prompt, eval pipelines — só variáveis de ambiente | CrewAI AMP/Enterprise (pago) traz trace por passo e uso de token por agente; OSS depende de OpenTelemetry/Langfuse/Arize plugado à mão | **LangGraph** |
| **Supervisor pattern** | Primitivo `interrupt()` para HITL com preservação total de estado; lib `langgraph-supervisor` (`create_supervisor` + handoff tools) — mas o próprio time recomenda hoje implementar supervisor via tool-calling direto para mais controle | `Process.hierarchical`: um agente-gerente (LLM) decide delegação a cada task; Flows cobrem o roteamento determinístico, Crews cobrem a colaboração autônoma | **LangGraph** (mais granular e auditável) |
| **Escalabilidade (nº de agentes)** | Sem limite documentado; grafos com 50-500+ nós em produção (Rakuten, GitLab, Elastic); LangGraph Cloud/Platform com checkpointer Postgres para usuários concorrentes | Sem limite documentado; adoção agregada alta (~450M execuções/mês, 60% da Fortune 500 US), mas escala por fila de jobs (SQS/RabbitMQ/Redis Streams) com 1 crew completo por worker — menos natural para 20+ agentes roteados dinamicamente num único fluxo | **LangGraph** para registry grande e único; CrewAI escala bem por *volume* de execuções paralelas, não por *tamanho* do grafo |
| **Custo de tokens** | Roteamento decidido em código, não em chamada LLM; benchmarks independentes (2026) medem 30-40% menos tokens que CrewAI em tarefas de complexidade média, chegando a 3x menos em alguns fluxos comparáveis | Cada agente injeta role+goal+backstory em toda chamada; `hierarchical process` soma 1 chamada LLM extra por decisão de delegação (3 tasks paralelas = 3 chamadas de gerente antes do trabalho começar); overhead medido ~18-300% acima do LangGraph equivalente | **LangGraph**, com folga |
| **Latência de orquestração** | ~120ms de overhead por nó (transição via código) | picos de ~450ms por transição de task (delegação via LLM) | **LangGraph** |
| **Community & docs** | Ecossistema LangChain (maior no agregado), LangChain Academy, LangGraph Studio, `awesome-LangGraph`, forte tração enterprise em 2026 (ultrapassou CrewAI em estrelas GitHub em alguns levantamentos de 2026); docs de referência mais densas, curva de aprendizado mais alta | Maior popularidade "de largada": 100k+ devs certificados via learn.crewai.com, Discord ativo, docs voltadas a iniciante, curva de aprendizado mais baixa | **CrewAI** (facilidade/onboarding) / **LangGraph** (profundidade técnica e produção) |
| **Maturidade para produção** | Checkpointer Postgres, time-travel, recovery, HITL granular — desenhado para sistemas de longa duração com auditoria | Flows (determinístico) reduz a lacuna, mas sem checkpointing nativo para workflows longos na versão OSS; observabilidade fina é feature paga (AMP) | **LangGraph** |

---

## 3. Observabilidade — detalhe

**LangGraph**: com `LANGCHAIN_TRACING_V2=true` e uma API key do LangSmith,
todo `graph.invoke()` já aparece traçado — sem instrumentação manual.
Cobre chamada LLM, tool call e passo intermediário, com replay de estado
via checkpoint. Isso atende diretamente o pilar **auditável** do PK_07
(log + gate humano em decisão irreversível) sem código adicional.

**CrewAI**: a versão gratuita não tem equivalente nativo — a trilha
completa (custo por passo, latência por crew) só chega no AMP/Enterprise,
que é pago e ainda considerado "menos maduro" que a oferta da LangSmith
nos comparativos de 2026. Na prática, times CrewAI plugam OpenTelemetry,
Langfuse ou Arize por conta própria.

**Veredito**: para os 20 agentes do Maestro rodando 8 fases de ciclo de
vida × 5 segmentos verticais, observabilidade *out-of-the-box* poupa
trabalho de instrumentação que teria de ser refeito para cada agente
vertical (S6-S10 e além).

---

## 4. Supervisor pattern — detalhe

O Maestro já é, conceitualmente, um supervisor pattern: Manta 00
(maestro/router) decide qual dos 19 agentes especializados chama, com
Q1 do intake fazendo o roteamento (hoje por regex, seção ROUTING do
`CLAUDE.md`).

**LangGraph** mapeia isso quase 1:1: o nó "maestro" vira o nó supervisor,
cada agente vertical vira um nó (ou subgrafo) worker, e a aresta
condicional decide o roteamento. O `interrupt()` dá o "gate humano" (item
do DEPLOY CHECKLIST v4.2 — "Gate humano: aprovação MN antes de merge") como
primitivo de framework, não como convenção manual. A recomendação atual do
próprio time LangChain — usar tool-calling direto em vez da lib
`langgraph-supervisor` — ainda é compatível com o padrão hub-and-spoke que
a Manta já usa (Seção 9 da skill `manta-arquiteto-ia`).

**CrewAI** cobre o mesmo caso com `Process.hierarchical`, mas a decisão de
delegação é ela própria uma chamada LLM — o que é exatamente o anti-padrão
que a Manta já evita ("LLM como orquestrador de cron" → usar scheduler
determinístico). Aqui o equivalente seria "LLM como orquestrador de
roteamento", que custa tokens e reduz a determinicidade do rastreamento
que a Manta exige para claims e laudos.

**Veredito**: LangGraph encaixa melhor no padrão hub-and-spoke que a Manta
já adotou como padrão dominante (Seção 9, skill do arquiteto).

---

## 5. Escalabilidade — detalhe

Nenhum dos dois frameworks documenta um teto rígido de agentes. A
diferença é estrutural:

- **LangGraph** representa o roteamento como grafo — natural para
  20 nós hoje, crescendo para roteamento hierárquico (L1 maestro → L2
  supervisores por eixo → L3 workers por fase de ciclo de vida) sem
  redesenho, conforme já mapeado em
  `docs/RESEARCH-MODERN-AGENT-ORCHESTRATION.md` seção 7
  (20 → 50 → 100+ agentes).
- **CrewAI** escala bem em *throughput* (fila de jobs, um worker por
  crew), mas cada crew tende a ser um time pequeno e coeso de agentes.
  Para um *registry* de 20 especialistas verticais roteados
  dinamicamente por consulta, CrewAI exigiria ou (a) um Flow por segmento
  para simular o grafo, ou (b) uma Crew gigante com custo de contexto por
  agente (role+goal+backstory) multiplicado por todos os membros.

**Veredito**: para o formato específico do Maestro (registry grande,
roteamento dinâmico, 1 especialista ativo por request), LangGraph escala
com menos redesenho.

---

## 6. Custo de tokens — detalhe

Achados de benchmarks independentes de 2026:

- LangGraph usa **30–40% menos tokens** que CrewAI em tarefas de
  complexidade média.
- Um benchmark de março/2026 mediu CrewAI consumindo **até 3x** os tokens
  do LangGraph em fluxos comparáveis.
- Overhead de orquestração pura: CrewAI gastou ~US$ 4,10 em tokens de
  orquestração num teste de 100 loops de um fluxo research-and-summarize,
  contra custo próximo de zero no LangGraph (roteamento por código).
- CrewAI adiciona ~18% de overhead de token vs. LangGraph escrito à mão
  em fluxos equivalentes; em processo hierárquico, cada delegação paralela
  soma uma chamada de "gerente" extra.

Aplicado ao Maestro: com 20 agentes verticais × 8 fases de ciclo de vida,
qualquer overhead percentual por chamada se multiplica pelo volume de
roteamento. O pilar **econômico** do PK_07 (tiering Haiku/Sonnet/Opus,
meta de ~80% de economia) é mais fácil de sustentar com roteamento por
código do que com uma camada extra de decisão via LLM.

---

## 7. Community & docs — detalhe

- **CrewAI** vence em popularidade de entrada: mais estrelas históricas
  em parte dos levantamentos, 100k+ devs certificados, documentação
  voltada a quem está começando, Discord ativo. Curva de aprendizado
  mais baixa favorece prototipagem rápida.
- **LangGraph** vence em profundidade e em tração enterprise: parte do
  guarda-chuva LangChain (o maior ecossistema do espaço), LangGraph
  Studio para debug visual, LangChain Academy, e — em levantamentos de
  2026 — ultrapassou o CrewAI em estrelas GitHub puxado por adoção
  corporativa (Rakuten, GitLab, Elastic citados como referência).

Os números de estrelas GitHub variam entre fontes de 2026 (alguns dão
CrewAI na frente, outros dão LangGraph ultrapassando) — não há consenso
de número absoluto, mas há consenso de que **CrewAI onboarda mais rápido**
e **LangGraph documenta melhor os casos de produção** (checkpointing,
HITL, deploy).

**Veredito**: para equipe que já opera FastAPI + Postgres + Celery (stack
de referência Manta, seção 12 da skill do arquiteto), a documentação de
produção do LangGraph é mais aplicável que os guias de onboarding do
CrewAI.

---

## 8. Trade-offs — resumo direto

| Se a prioridade é... | Escolha |
|---|---|
| Auditoria completa, HITL granular, custo de token controlado, grafo de 20+ agentes | **LangGraph** |
| Prototipar rápido um time pequeno de 2-4 agentes colaborativos, sem preocupação imediata com produção | **CrewAI** |
| Ambos ao mesmo tempo (padrão relatado por times que usam os dois) | CrewAI para a fase exploratória (pesquisa/síntese, onde flexibilidade importa) entregando para LangGraph na fase de execução determinística — mas isso é complexidade extra que a Manta não precisa hoje |

O padrão híbrido (CrewAI + LangGraph) aparece em parte da literatura de
2026, mas soma uma segunda dependência e um segundo formato de estado para
manter — contra o pilar **modular com contrato explícito** do PK_07. Só
vale a pena se a Manta precisar mesmo de uma fase de "crew autônoma" sem
determinismo (não é o caso do Maestro, cujo roteamento já é regrado por
Q1/Q2 do intake).

---

## 9. Recomendação final

**Adotar LangGraph 0.2+ como motor de orquestração da camada de produção
do Manta Maestro**, mantendo Claude Code (subagents/skills nativos) como
ambiente de desenvolvimento e operação assistida — os dois não competem,
resolvem camadas diferentes:

- **Claude Code** continua sendo onde os 20 agentes são *escritos,
  testados e operados interativamente* (skills `.md`, subagents,
  hooks) — nenhuma mudança aqui.
- **LangGraph** entra como motor de roteamento *quando* o Maestro precisar
  rodar como serviço de API (FastAPI, camada "Skills/Agentes" do PK_07),
  fora do terminal, com estado persistente entre chamadas, HITL formal e
  trilha de auditoria — o que hoje falta na regra de regex do Q1.

Motivos, em ordem de peso:

1. **Auditabilidade nativa** (LangSmith) resolve de graça o pilar
   *auditável* do PK_07 — sem essa dependência extra, qualquer skill
   precisaria reimplementar logging estruturado por conta própria.
2. **Custo de token 30-40% menor** (até 3x em alguns fluxos) é decisivo
   num sistema com 20 agentes × 8 fases de ciclo de vida — o volume
   multiplica qualquer overhead percentual.
3. **Roteamento por código, não por LLM**, evita reintroduzir o
   anti-padrão "LLM decidindo o quê já deveria ser regra determinística"
   que a skill `manta-arquiteto-ia` já lista para cron e deveria valer
   também para dispatch de agente.
4. **Grafo de estado escala para o formato exato do Maestro** — registry
   grande, 1 especialista ativo por request, caminho de crescimento já
   desenhado (L1→L2→L3, ver `RESEARCH-MODERN-AGENT-ORCHESTRATION.md`
   seção 7) sem exigir redesenho de arquitetura.
5. CrewAI não é descartado por ser ruim — é descartado porque resolve um
   problema (colaboração autônoma de um time pequeno de agentes) que o
   Maestro não tem. O Maestro já é regrado (Q1/Q2 do intake, 8 fases fixas
   de ciclo de vida); precisa de determinismo auditável, não de
   flexibilidade de crew.

### O que isso muda no roadmap (`DEPLOY CHECKLIST v4.2` / v5.0)

- PoC citado em `RESEARCH-MODERN-AGENT-ORCHESTRATION.md` ("Escolher
  LangGraph OU CrewAI via PoC rápido, teste S8") pode ser fechado direto
  em LangGraph — os benchmarks públicos de 2026 já respondem a pergunta
  que o PoC ia responder.
- Adicionar `langgraph`, `langgraph-checkpoint-postgres` e `langsmith` ao
  stack técnico (seção 12, skill `manta-arquiteto-ia`), mantendo
  APScheduler para o pipeline diário determinístico (o LangGraph não
  substitui o scheduler — ele orquestra o *grafo de agentes*, não o
  *cron*).
- Sem gate humano adicional necessário para essa escolha de biblioteca —
  não é uma decisão irreversível de dado ou conteúdo, é escolha de
  ferramenta de infraestrutura. Gate humano continua obrigatório antes de
  qualquer merge de agente novo no registry, como já previsto no
  checklist v4.2.

---

## 10. Fontes

- [LangGraph vs CrewAI: Let's Learn About the Differences — ZenML Blog](https://www.zenml.io/blog/langgraph-vs-crewai)
- [Observability for AI Agents: LangGraph, OpenAI Agents, and Crew AI — GetMaxim](https://www.getmaxim.ai/articles/observability-for-ai-agents-langgraph-openai-agents-and-crew-ai/)
- [LangGraph vs CrewAI vs AutoGen: Which Framework for Enterprise 2026 — Towards AI](https://pub.towardsai.net/langgraph-vs-crewai-vs-autogen-which-ai-agent-framework-should-your-enterprise-use-in-2026-3a9ebb407b09)
- [AI Agent Frameworks Compared: LangGraph vs CrewAI vs AutoGen (2026) — PE Collective](https://pecollective.com/blog/ai-agent-frameworks-compared/)
- [In-depth comparison: workflow control with LangGraph and CrewAI — DEV Community](https://dev.to/rosidotidev/in-depth-comparison-workflow-control-with-langgraph-and-crewai-ae3)
- [LangSmith for Agent Observability: Tracing LangGraph + Tool-Calling — Medium](https://ravjot03.medium.com/langsmith-for-agent-observability-tracing-langgraph-tool-calling-end-to-end-2a97d0024dfb)
- [What is LangSmith? 2026 Guide to LLM Observability — MetaCTO](https://www.metacto.com/blogs/what-is-langsmith-a-comprehensive-guide-to-llm-observability)
- [CrewAI Explained: Architecture, Limits, Context Gap — Atlan](https://atlan.com/know/ai-agent/what-is-crewai/)
- [CrewAI Flows: Production Multi-Agent Guide 2026 — Jahanzaib](https://www.jahanzaib.ai/blog/crewai-flows-production-multi-agent-guide)
- [CrewAI in Production: Deployment, Monitoring & Scaling (2026) — TechJack Solutions](https://techjacksolutions.com/ai-tools/crewai/crewai-production-guide/)
- [LangGraph Multi-Agent Supervisor — LangChain Reference](https://reference.langchain.com/python/langgraph-supervisor)
- [GitHub - langchain-ai/langgraph-supervisor-py](https://github.com/langchain-ai/langgraph-supervisor-py)
- [How to Orchestrate Multi-Agent Systems in LangGraph (Supervisor vs Swarm) — Focused](https://focused.io/lab/multi-agent-orchestration-in-langgraph-supervisor-vs-swarm-tradeoffs-and-architecture)
- [Best AI Agent SDKs Compared (2026) — Requesty](https://www.requesty.ai/blog/best-ai-agent-sdks-compared-2026-langchain-crewai-openai-anthropic-google)
- [Claude Agent SDK vs LangGraph vs CrewAI: Complete 2026 Benchmark](https://pasqualepillitteri.it/en/news/3095/claude-agent-sdk-vs-langgraph-vs-crewai-benchmark-2026-en)
- [CrewAI vs LangGraph vs AutoGen 2026: Benchmarks, Pricing — Pooya Golchian](https://pooya.blog/blog/crewai-vs-langgraph-autogen-comparison-2026/)
- [LangGraph vs CrewAI: Multi-Agent Performance and Cost in Production 2026 — Markaicode](https://markaicode.com/vs/langgraph-vs-crewai-multi-agent-production/)
- [CrewAI to LangGraph Migration Guide: Save 18% Tokens (2026) — TokenMix](https://tokenmix.ai/blog/crewai-to-langgraph-migration-guide-2026)
- [LangGraph vs CrewAI: Honest Comparison for 2026 — Fastio](https://fast.io/resources/langgraph-vs-crewai/)
- [LangGraph v0.2: Increased customization with new checkpointer libraries — LangChain Blog](https://www.langchain.com/blog/langgraph-v0-2)
- [LangGraph State Management: Checkpointing & Recovery — ActiveWizards](https://activewizards.com/blog/langgraph-state-management-checkpointing-recovery-and-the-persistence-layer-decision/)

---

_Documento gerado sob demanda. Complementa
`docs/RESEARCH-MODERN-AGENT-ORCHESTRATION.md` e
`docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`. Fecha o item em aberto
"Escolher LangGraph OU CrewAI via PoC" com recomendação: **LangGraph**._
