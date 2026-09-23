# Plano de testes funcionais — Manta Maestro (v1)

Data: 2026-09-23 · Autor: sessão Claude Code a pedido de MN · Status:
**rascunho para aprovação de MN** (nada foi executado ainda).

Complementa a auditoria de 2026-09-22 (`docs/PLANO-AUDITORIA-v1.md`,
`docs/auditoria/RELATORIO-AUDITORIA-2026-09-22.md`). A auditoria verificou
se o sistema está **consistente**; este plano verifica se ele **funciona**:
se uma pergunta de engenharia chega ao agente certo, se o agente acha a
base de conhecimento certa e se a resposta é tecnicamente correta.

---

## 1. O que é "o Maestro" que vamos testar

Só entram componentes com lastro real (matriz E9 do relatório). A camada
📐 "Maestro OS v6" (ML, consenso, orquestrador) fica fora — não está
implantada.

| Componente | Onde vive | O que faz |
|---|---|---|
| C1 Roteamento por palavra-chave | Supabase `maestro_routing_keywords` (61 linhas) + `src/maestro/keyword_router.py` (referência) | Decide qual agente atende a pergunta |
| C2 Base de conhecimento (RAG) | Supabase `manta_rag_documents` (126) / `manta_rag_chunks` (316); funções `manta_rag_search` (vetor), `manta_rag_fts` (texto), `match_kes_hybrid` | Entrega trechos de norma/conhecimento ao agente |
| C3 Guardrails | Função `manta_r1_check`/`manta_r1_sanitize` (R1); skills `aluci-guard` e `consist-guard` | Bloqueia nome de cliente/pessoa, norma inventada, inconsistência numérica |
| C4 Agentes especialistas | `.claude/agents/*.md` (repo) e `SKILL.md` em `01-segmentos/`, `02-atividades/`, `04-disciplinas/` (SharePoint) | Respondem a pergunta técnica |
| C5 Rubricas (auto-juiz) | SharePoint `08-rubricas/` (41 ativas) | Dão nota à resposta |
| C6 Skill `manta-maestro` | Skill da conta no Claude (canal que a equipe usa) | Orquestra C1–C5 numa conversa real |

## 2. Achados de pré-voo (já medidos em 2026-09-23)

Consultas somente-leitura ao Supabase antes de montar o plano. Vários
testes abaixo **vão falhar hoje** por causa disso — é esperado e é
exatamente o que o teste precisa mostrar.

1. **Metade da base de conhecimento está sem vetor**: 162 de 316 trechos
   têm embedding. Tipos inteiros sem nenhum: `knowledge_base` (0/63),
   `manual_tecnico` (0/11), `artefato_html` (0/12), `edital`, `regulatorio`,
   `norma` (singular), `parametro`. Esses trechos só são encontráveis por
   busca textual, nunca por busca semântica.
2. **O roteamento no banco só conhece 6 agentes**: as 61 palavras-chave
   apontam para saneamento, energia, portos, aeroportos, barragens e
   infraestrutura (S1–S4). Não há rota para **S6 Edificações, S12 Túneis,
   S13 Mineração, S14 Óleo e Gás** nem para nenhum horizontal (orçamento,
   cronograma, claims…).
3. **Campo legado `manta_code` em S12–S14** colide com o código de outro
   segmento (já registrado na auditoria) — se algo rotear por esse campo,
   óleo e gás cai em túneis.

## 3. Camadas de teste

Cada camada tem casos, critério de aprovação e quem executa. "Aqui" = esta
sessão Claude Code (acesso a repo, Supabase, SharePoint e aos agentes como
subagentes). "Chat" = MN numa conversa normal do Claude com a skill
`manta-maestro`, que é o caminho real da equipe.

### T1 — Roteamento (C1) · aqui · ~30 min · sem custo de API

- **Casos**: os 36 prompts de `tests/routing/prompts.md` (S7–S11, não
  regressão S1–S4, casos ambíguos) + **12 novos** cobrindo o que falta: 3 de
  S6 Edificações, 3 de S12–S14, 6 horizontais (orçamento SICRO, cronograma
  P6, claim de reequilíbrio, contrato/aditivo, proposta, ESG).
- **Como**: rodar cada prompt contra (a) as palavras-chave do banco,
  reproduzindo a regra de match, e (b) `keyword_router.py`; comparar os dois.
  Vira o `scripts/test_routing.py` que o próprio `prompts.md` pede.
- **Aprovação**: ≥ 90% de acerto do agente primário nos 36 originais; nos
  12 novos, medir e **registrar a lacuna** (hoje devem falhar — achado 2).
  Divergência entre banco e referência = defeito.

### T2 — Base de conhecimento (C2) · aqui · ~1 h

- **Casos**: 33 perguntas-ouro, 3 por coleção (11 coleções), cada uma com o
  trecho que **deve** aparecer. Exemplos:
  - Barragens: "altura de alteamento e método a montante em barragem de
    rejeitos" → trecho da Lei 12.334/2010 alterada pela Lei 14.066/2020.
  - Saneamento: "vazão de dimensionamento de ETE e coeficientes K1/K2" →
    NBR 12209.
  - Rodovias: "dimensionamento de pavimento flexível pelo número N" →
    método DNIT/DNER.
- **Como**: busca textual (`manta_rag_fts`) para todas; busca vetorial
  (`manta_rag_search`) gerando o vetor da pergunta com o embedder canônico
  `bge-small-en-v1.5` (384 d). Se o modelo não puder ser baixado nesta
  sessão, a vetorial fica para a Routine/servidor e só a textual roda aqui.
- **Métricas**: cobertura de embedding por coleção (meta 100%); acerto@5
  (o trecho certo entre os 5 primeiros) ≥ 70%; coleção certa no 1º
  resultado ≥ 80%.

### T3 — Guardrails (C3) · aqui · ~30 min

- **R1 (sanitização)**: 10 textos com nome de cliente, de profissional,
  CNPJ e telefone fictícios + 10 textos limpos → `manta_r1_check`.
  Aprovação: 100% dos sujos detectados, ≤ 1 falso positivo nos limpos.
- **aluci-guard (norma inventada)**: 10 trechos técnicos, 5 com referência
  real (ex.: NBR 6118:2023, NBR 6122:2019, Lei 14.026/2020) e 5 com
  referência plantada inexistente (ex.: "NBR 19999", "SICRO 9999999",
  URL de norma falsa). Aprovação: 5/5 inventadas marcadas, 0 reais marcadas.
- **consist-guard**: 2 pareceres HTML curtos, um com subtotal que não fecha
  e data fora de ordem. Aprovação: os dois defeitos apontados.

### T4 — Agentes especialistas (C4 + C5) · aqui · ~2 h · custo moderado

- **Casos**: as 30 perguntas de `tests/smoke/queries/` (5 por agente:
  portos, aeroportos, saneamento, energia, barragens, óleo e gás) + 1
  **armadilha técnica** por agente — pergunta com uma premissa errada que o
  especialista precisa corrigir:

  | Agente | Armadilha | Resposta correta esperada |
  |---|---|---|
  | barragens | "Vamos alteamento a montante na barragem de rejeitos nova." | Recusar: vedado pela Lei 14.066/2020 (altera a PNSB); indicar jusante/linha de centro ou disposição a seco |
  | saneamento | "ETE para 50 mil hab. com 150 L/hab·dia, sem coeficiente de pico." | Apontar que a vazão máxima exige K1·K2 (NBR 12209/9649) |
  | portos | "Calado de projeto = profundidade do canal." | Separar calado do navio, folga sob a quilha (UKC) e cota de dragagem (PIANC) |
  | aeroportos | "PCN 40 atende A320neo em qualquer pavimento." | Explicar ACR/PCR (ICAO, desde 2024) e que depende do tipo de pavimento e do subleito |
  | energia | "LT 500 kV com a mesma faixa de servidão de uma 138 kV." | Faixa depende de tensão, cabo e flecha (NBR 5422) — não é a mesma |
  | óleo e gás | "Tanque atmosférico de 20 m sem bacia de contenção." | Exigir contenção secundária (NFPA 30 / NBR 17505) |

- **Como**: rodar cada pergunta no agente correspondente (subagentes desta
  sessão, que são os `.claude/agents/*.md`); dar nota 1–5 com a rubrica do
  segmento em `08-rubricas/` (lida do SharePoint, somente leitura); checar
  também os termos `expect_any` de cada YAML.
- **Aprovação**: nota ≥ 4 em ≥ 80% das perguntas; **6/6 armadilhas
  corrigidas** (uma armadilha aceita sem correção é falha grave); zero
  norma inventada (aluci-guard sobre cada resposta).

### T5 — Ponta a ponta (C6) · chat de MN + aqui · ~1 h de MN

Cinco casos compostos S.A.D, digitados por MN na skill `manta-maestro` (é o
teste que mais importa: é o caminho real da equipe). Eu preparo o texto de
cada caso, MN cola a resposta num arquivo e eu avalio.

| # | Célula | Caso | O que precisa acontecer |
|---|---|---|---|
| E1 | S9.A3.D07 | Orçamento paramétrico de ETE de lodos ativados, 500 L/s | Rota saneamento → orçamento; SINAPI/SICRO com data-base; BDI dentro das faixas do Acórdão TCU 2622/2013 |
| E2 | S7.A2.D01 | Volume de dragagem de aprofundamento de canal para calado 14 m | Rota portos; memória de cálculo com UKC e taludes; pede batimetria se faltar dado (R2: não inventa) |
| E3 | S11.A10.D03 | Matriz de risco de barragem de rejeitos com alteamento a montante | Rota barragens → risco; aponta a vedação legal antes da matriz |
| E4 | S1.A1 | Proposta técnica PRT para duplicação rodoviária | Usa o template PRT; saída sem nome de cliente real (R1) |
| E5 | S14 + S11 | Duto de óleo cruzando barragem de UHE | Hoje deve falhar (sem rota para S14) — confirma o achado 2 |

- **Aprovação**: E1–E4 com rota certa, sem norma inventada, sem violação
  R1/R2 e nota ≥ 4 na rubrica; E5 registra a lacuna.

### T6 — Integração SharePoint · aqui · ~20 min

- A skill encontra o `SKILL.md` certo pelo `INDICE-CANONICAL.md` para 5
  pedidos (um por eixo).
- Execução manual (dry-run) da nova Routine de publicação repo → SP:
  nenhum arquivo diferente deve ser detectado.

## 4. Ordem de execução

1. T1 e T3 (baratos, sem API) → 2. T2 (mede a base) → 3. T4 (agentes) →
4. T5 (MN no chat) → 5. T6 → 6. relatório.

Estimativa total: ~5 h de execução aqui + ~1 h de MN. Custo de API:
moderado, concentrado em T4 (~36 respostas de agente + ~36 avaliações).

## 5. Entregáveis

- `docs/testes/RELATORIO-TESTES-MAESTRO-<data>.md`: resultado por camada,
  métricas, lista de defeitos com gravidade e proposta de correção.
- `scripts/test_routing.py` e os casos novos em `tests/routing/`,
  `tests/rag/` e `tests/smoke/queries/`, para os testes virarem regressão
  no CI (T1–T3 rodam sem segredo; T4 fica para quando houver
  `ANTHROPIC_API_KEY` no CI).
- Nenhuma correção em produção durante a rodada: defeito vira item do
  relatório. Corrigir é decisão de MN depois (mesmo modelo da auditoria).

## 6. Decisões pedidas a MN

1. **Escopo**: rodar as 6 camadas, ou começar só por T1–T3 (baratos) e
   decidir T4/T5 depois?
2. **T4 com custo de API** (~70 chamadas de modelo nesta sessão): pode?
3. **T5**: MN topa rodar os 5 casos no chat, ou prefere que eu simule o
   Maestro aqui com os subagentes (menos fiel ao uso real)?
4. **Defeitos**: só relatar, ou já corrigir os de baixo risco que
   aparecerem (ex.: gerar os embeddings faltantes, incluir palavras-chave
   de S6/S12–S14 no banco)?
