# Reconciliação Arquitetura v6 (SharePoint) vs CLAUDE.md Master (v4.2.2)

Este documento registra a comparação solicitada entre a arquitetura "v6"
descrita em 5 arquivos na pasta SharePoint
`Documentos/04_IA/Manta-Maestro/00-arquitetura/` e o **CLAUDE.md master**
deste repositório (`Codex-exemplo/CLAUDE.md`, hoje **v4.2.2**, 2026-09-04,
20 agentes em 3 eixos: Horizontais, Verticais S1–S10, Ciclo de vida 8
fases).

É um documento de **comparação**, não de decisão. Não altera o
`CLAUDE.md` deste repositório. Qualquer fusão/adoção de conteúdo do
SharePoint no registro mestre requer **aprovação humana (gate MN)**,
conforme já é prática registrada neste repositório (ver
`docs/MODELO-MESTRE-PROPOSTA.md`, seção 6, e o item "Gate humano: aprovação
MN antes de merge" no checklist de deploy do `CLAUDE.md`).

---

## 1. Arquivos lidos

Do SharePoint (biblioteca "Documentos",
`04_IA/Manta-Maestro/00-arquitetura/`), via `read_document`:

| Arquivo | Versão declarada | Data | Observação de leitura |
|---|---|---|---|
| `ARQUITETURA-AGENTES-IA-v6.1.0.md` | 6.1.0 | 2026-08-01 | Legível integralmente, UTF-8 limpo |
| `CLAUDE.md-v6.1.0-CONSOLIDATED.md` | 6.1.0 | 2026-08-01 | Legível integralmente, UTF-8 limpo |
| `SKILL-MANTA-MAESTRO-v6.1.0.md` | 6.1.0 | 2026-08-01 | Legível integralmente, UTF-8 limpo |
| `MAESTRO-OS-v6-API.md` | 6.0.0 | 2026-07-26 | **Encoding corrompido (mojibake)** — ver §5 |
| `MAESTRO-OS-v6-DEVELOPER.md` | 6.0.0 | 2026-07-26 | Legível integralmente, UTF-8 limpo |

Deste repositório: `CLAUDE.md` (raiz), `docs/MODELO-MESTRE-PROPOSTA.md`
(apenas para tom/formato), e inspeção do próprio repositório git (log de
commits, árvore de arquivos, `supabase/migrations/`,
`sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`) para verificar
afirmações feitas pelos documentos v6 sobre o estado deste repositório.

**Nota sobre encoding — `MAESTRO-OS-v6-API.md`:** o documento retornou com
`extraction_method: "text-latin-1"` e contém mojibake visível nos
diagramas de caixa (box-drawing) e em toda palavra acentuada em português
(ex.: `Votação` aparece como `VotaÃ§Ã£o`, `orçamento` como `orÃ§amento`,
`terminal portuário` como `terminal portuÃ¡rio`). O conteúdo técnico em
inglês (nomes de classes, assinaturas de função, YAML) permanece legível
porque não usa acentuação. Não tentei reconstruir os trechos corrompidos
por inferência — o que segue abaixo usa apenas o que era literalmente
legível no documento. `MAESTRO-OS-v6-DEVELOPER.md`, por contraste, veio
como `text-utf-8` sem mojibake aparente.

---

## 2. O que é consistente entre v6 (SharePoint) e o CLAUDE.md v4.2.2 (repo)

- **Origem comum dos 5 agentes S6–S10**: os 3 documentos v6.1.0 (Arquitetura,
  CLAUDE.md-CONSOLIDATED, SKILL) preservam explicitamente a proveniência
  dos agentes `agente-portos`, `agente-aeroportos`, `agente-saneamento`,
  `agente-energia`, `agente-barragens` — os mesmos 5 arquivos que existem
  hoje em `.claude/agents/` neste repositório — apenas renumerando os
  códigos de segmento (ver §3).
- **Prioridade AySA em Saneamento** é mantida em todos os documentos v6
  (`agente-saneamento (AySA)`), igual ao CLAUDE.md v4.2.2 local.
- **Model tiering** (Haiku default → Sonnet escalação → Opus excepcional)
  é o mesmo conceito em ambos os lados, incluindo a regra de que Opus só
  entra por pedido explícito ou tarefa arquitetural.
- **Regras de guardrail R1–R5** (sanitização, não inventar, alertas
  críticos, `.xlsx`→buscar `.pdf`/`.docx`, BRL com data-base) aparecem
  em `CLAUDE.md-v6.1.0-CONSOLIDATED.md` e `SKILL-MANTA-MAESTRO-v6.1.0.md`
  sem contradição com nada que exista no CLAUDE.md v4.2.2 local (este
  último não lista R1–R5 explicitamente, mas não há conflito — apenas
  ausência local).
- **Gate humano MN** para migrações de schema é reconhecido nos dois
  lados: o CLAUDE.md v4.2.2 local marca "Gate humano: aprovação MN antes
  de merge" como pendente no checklist v4.2; os documentos v6.1.0 marcam
  a migração `2026_08_01_v6_1_taxonomy_reconciliation.sql` como
  "gate MN duro" e "não aplicada em produção".
- **`ARQUITETURA-AGENTES-IA.md` local** (`sharepoint/00-arquitetura/` neste
  repo) está em v2.0.0 (2026-07-05), o que bate com o item do checklist
  do CLAUDE.md v4.2.2 que pede "Atualizar `ARQUITETURA-AGENTES-IA.md` no
  SP (v1.0.0 → v2.0.0)" — ou seja, esse item específico do checklist já
  está de fato refletido neste repositório, embora o arquivo v6.1.0 do
  SharePoint já fale em substituir uma v5.2.0 anterior a ele, que não
  existe neste repositório (ver §4).

---

## 3. O que diverge — taxonomia e contagem de agentes

| Dimensão | CLAUDE.md v4.2.2 (repo, este) | v6.1.0 (SharePoint, 3 docs) |
|---|---|---|
| Segmentos verticais | **S1–S10** (10 códigos, prefixo `Manta 03-S{n}`) | **S1–S14** (14 códigos, prefixo `Manta 03-S{n}` "aposentado") |
| Horizontais | 11 agentes nomeados (Manta 00,01,02,04-07,13-16), sem código `A{n}` | **A1–A11** (11 códigos, com A9-regulatório/A10-risco/A11-fiscalização "portados do SP") |
| Funcionais | Não existe esse eixo no CLAUDE.md local | **F1–F10** (10 códigos: IA, SharePoint, Portal, Extração, Notificação, Trace, Guardrails, Padronização, Meta, Pesquisa Evolutiva) |
| Disciplinas | Não existe esse eixo no CLAUDE.md local | **D01–D23** (citado, mas com a própria fonte v6.1 dizendo "referência ... pendente de expansão") |
| Total de agentes | 20 (enunciado explicitamente no título do repo) | Não há uma contagem total explícita nos 3 docs v6.1.0; a soma dos códigos citados (14+11+10) é 35, sem D01–D23 |
| Renumeração de S6–S10 | S6=Portos, S7=Aeroportos, S8=Saneamento, S9=Energia, S10=Barragens | Os mesmos 5 agentes agora são **S7=Portos, S8=Aeroportos, S9=Saneamento, S10=Energia, S11=Barragens** — cada um deslocado +1 |
| Novo S6 | Não existe | S6 = **Edificações** (`agente-edificacoes`), agente que não existe neste repositório |
| Novos S12–S14 | Não existem | S12=Túneis, S13=Mineração, S14=Óleo&Gás — nenhum desses 3 agentes existe neste repositório (nem em `.claude/agents/`, nem em pastas equivalentes) |
| S5 | Não codificado como S5 no CLAUDE.md local (Túneis aparece como `Manta 03-S5`, "coberto por S2/S4", sem agente próprio) | v6.1.0 usa S5 para **Imobiliário** (`manta-04`, "SP-native") e desloca Túneis para S12 |

**Consequência prática**: a tabela de conversão "legenda histórica"
presente nos 3 documentos v6.1.0 (`Manta 03-S6→S7`, `S7→S8`, `S8→S9`,
`S9→S10`, `S10→S11`, além de S5→S12, S11→S13, S12→S14, S13→S6) é
incompatível ponto a ponto com a tabela de routing atualmente publicada
no CLAUDE.md v4.2.2 deste repositório (seção "ROUTING — Maestro (Manta
00)"), que mantém os códigos S6–S10 originais. Se essa renumeração for
adotada, todo o bloco de routing regex do CLAUDE.md local precisaria ser
reescrito — o que este memo **não faz**, apenas sinaliza.

---

## 4. Afirmações dos documentos v6.1.0 sobre este repositório que não se confirmam

Os 3 documentos v6.1.0 (Arquitetura, CLAUDE.md-CONSOLIDATED, SKILL)
descrevem um trabalho de reconciliação já **concluído** ("v6.1.0 T1+T2+T3
(repo) publicado") com referências verificáveis. Conferi cada uma contra
o estado real deste repositório e nenhuma se confirma:

- **Commits citados** `ad98925` (T1 — portar A9/A10/A11/F10 do SP) e
  `48412d1` (T3 — renumerar 9 agent files) — **não existem** no histórico
  deste repositório (`git log --all`, 13 commits no total, nenhum com
  esses hashes).
- **Pastas `S12-tuneis`, `S13-mineracao`, `S14-oleogas`** — o doc de
  arquitetura afirma "Criar pastas SP" para esses segmentos em T2; não há
  como verificar o lado SharePoint a partir deste memo (não foi pedido
  navegar o restante do SP), mas do lado do repositório não existe
  nenhum arquivo `agente-tuneis.md`, `agente-mineracao.md` ou
  `agente-oleo-gas.md`.
- **Migração `Codex-exemplo/supabase/migrations/2026_08_01_v6_1_taxonomy_reconciliation.sql`**
  — citada nos 3 documentos como arquivo já referenciável neste
  repositório — **não existe**. O único arquivo em
  `supabase/migrations/` é `2026_07_05_v4_2_agents_s6_s10.sql` (a
  migração candidata da v4.2, consistente com o CLAUDE.md v4.2.2 local).
- **`.claude/agents/manta-maestro.md` §3.1`** — citado como uma das
  localizações da "tabela canônica" de conversão — este arquivo não
  existe em `.claude/agents/` neste repositório (a pasta contém apenas os
  5 arquivos `agente-{aeroportos,barragens,energia,portos,saneamento}.md`
  da v4.2).
- **`Codex-exemplo/CLAUDE.md §RECONCILIAÇÃO` / `§RECONCILIAÇÃO COM MAESTRO OPERACIONAL`**
  — citada por 2 dos documentos v6.1.0 como seção já existente neste
  arquivo — **não existe** essa seção no `CLAUDE.md` v4.2.2 atual deste
  repositório.
- **v5.2.0 (2026-07-29)** — o doc de arquitetura v6.1.0 diz "substitui
  v5.2.0" e o CLAUDE.md-CONSOLIDATED diz que v6.1.0 "substitui
  `CLAUDE.md-v5.1.0-CONSOLIDATED.md`" — nenhuma v5.x deste registro (nem
  do CLAUDE.md master, nem do consolidado do SP) foi lida nesta sessão;
  não tenho como confirmar ou negar o conteúdo dessas versões
  intermediárias — apenas registro que o CLAUDE.md deste repositório
  pulou diretamente de v4.1 (implícito) para v4.2 → v4.2.1 → v4.2.2, sem
  nunca ter tido uma v5.x.

**Não estou afirmando que o trabalho descrito nos documentos v6.1.0 é
falso ou inválido** — é possível que ele exista de fato só do lado
SharePoint/Supabase (fora do que foi lido nesta sessão) e que as
referências a "Codex-exemplo" nos documentos estejam simplesmente
desatualizadas ou antecipando um merge que ainda não aconteceu. O ponto
factual verificável é: **neste repositório git, no estado atual, nada
disso está presente.**

---

## 5. Conceito novo: "Maestro OS" — camada de API/software

`MAESTRO-OS-v6-API.md` e `MAESTRO-OS-v6-DEVELOPER.md` descrevem um
sistema chamado **Maestro OS v6.0.0** (2026-07-26 — note-se: **anterior**
aos 3 documentos v6.1.0 de 2026-08-01, e não referenciado por nenhum
deles) que é qualitativamente diferente do que existe hoje: não é um
conjunto de arquivos `.md` de agente/skill, é um **runtime Python**
(`src/maestro/*.py`) com:

- 5 camadas: Complexity Detection → Orchestration → Consensus Engine →
  Aggregation → ML Intelligence.
- Classes concretas: `ComplexityDetector`, `WorkflowParser`,
  `MaestroOrchestrator`, `ConsensusEngine`, `QueueExecutor`,
  `MLInferenceService` (com `RoutingModel`, `DurationPredictor`,
  `RiskClassifier`), `ComplianceChecker` (normas Lei 12.334/ICOLD/CBDB),
  `WhatIfSimulator`.
- DSL de workflow em YAML com fan-out paralelo (máx. 8 agentes
  concorrentes, buffer de fila até 16), votação de consenso 3/5 com
  escalação, e emissão de saída em DOCX+JSON.
- Escalonamento dinâmico de 8 a 16 agentes por projeto conforme
  complexidade, com orçamento de tokens de 300k–600k.

**Este código não existe neste repositório** — não há diretório `src/`
nem qualquer arquivo Python; o repositório é inteiramente Markdown +
front-matter YAML de agentes + 1 template HTML + 1 migração SQL
candidata. Não há como saber, a partir do que foi lido, se
`Maestro OS` roda em algum outro repositório real (fora do escopo desta
sessão) ou se é uma especificação/protótipo ainda não implementado — os
documentos não dizem isso, então não devo supor.

**Inconsistência interna nos próprios documentos "Maestro OS"**: a seção
"Configuration → Agent Pool (20 total)" do `MAESTRO-OS-v6-API.md` lista
verticais como **S1–S11** (não S1–S14) e horizontais numerados até
**A15** (cita A1, A2, A4, A5, A6, A7, A13, A14, A15 — pulando A3 e
A8–A12), e os exemplos YAML do mesmo documento também usam `segments:
["S1"..."S11"]`. Isso **não bate** com a taxonomia S1–S14 / A1–A11 dos 3
documentos v6.1.0 nem com o S1–S10 do CLAUDE.md v4.2.2 local. Ou seja,
mesmo dentro do material lido no SharePoint desta pasta, há pelo menos
**três numerações de segmento diferentes coexistindo** (S1–S10 local,
S1–S11 no Maestro OS, S1–S14 no v6.1.0), sem que nenhum dos documentos
reconheça ou reconcilie essa diferença entre si.

---

## 6. Resumo da comparação

| Aspecto | Repo `CLAUDE.md` v4.2.2 | SharePoint v6.1.0 (3 docs) | SharePoint "Maestro OS" v6.0.0 (2 docs) |
|---|---|---|---|
| Estrutura de registro | Tabelas Markdown de agentes + routing regex | Igual (tabelas Markdown), + tabela de conversão de códigos legados | N/A — API/runtime, não é registro de agentes |
| Eixos | 3 (Horizontais, Verticais S1-S10, Ciclo de vida) | Efetivamente 4 (Segmentos, Atividades, Funcionais, Disciplinas) | 5 camadas de execução (Detection→Orchestration→Consensus→Aggregation→ML) |
| Nº segmentos verticais | 10 (S1–S10) | 14 (S1–S14) | 11 citados (S1–S11) |
| Nº total de agentes | 20 (declarado) | Não declarado explicitamente (soma dos códigos ≈ 35 sem D01-D23) | "20 total" declarado, mas lista incompleta/inconsistente com A1-A15 |
| Presente no repo git hoje | Sim (é a fonte) | Não (nenhum arquivo/commit correspondente encontrado) | Não (nenhum código-fonte correspondente encontrado) |
| Data mais recente | 2026-09-04 | 2026-08-01 | 2026-07-26 |

---

## 7. Recomendação e próximos passos

Este memo **não recomenda merge automático** de nenhuma parte da
taxonomia v6.1.0 ou do conceito Maestro OS para o CLAUDE.md v4.2.2 deste
repositório. Antes de qualquer decisão de fusão/adoção:

1. **Confirmar com MN/SharePoint** se os commits `ad98925`/`48412d1` e a
   migração `2026_08_01_v6_1_taxonomy_reconciliation.sql` citados pelos
   documentos v6.1.0 existem em algum outro repositório ou branch fora do
   escopo desta sessão — ou se os documentos descrevem trabalho planejado
   e não trabalho concluído.
2. **Esclarecer a relação entre v6.1.0 (taxonomia S1-S14) e Maestro OS
   v6.0.0 (runtime S1-S11)** — são a mesma iniciativa em estágios
   diferentes, iniciativas paralelas independentes, ou um dos dois está
   desatualizado em relação ao outro? Nenhum dos 5 documentos lidos
   responde a isso.
3. **Corrigir o encoding de `MAESTRO-OS-v6-API.md`** no SharePoint antes
   de tratá-lo como fonte de decisão — no estado atual, os diagramas e
   todo texto acentuado em português estão corrompidos.
4. Qualquer decisão de renumerar S6–S10 → S7–S11 (ou adotar S1–S14/A1–A11/F1–F10)
   no CLAUDE.md master **requer aprovação humana explícita (gate MN)**,
   dado o impacto em cascata sobre routing regex, nomes de pasta
   SharePoint, coleções RAG e os 5 arquivos de agente já publicados em
   `.claude/agents/` neste repositório.
5. Até essa aprovação, o CLAUDE.md v4.2.2 deste repositório **permanece a
   fonte canônica vigente** tal como está — este memo não o altera.

---

*Análise feita a partir da leitura integral dos 5 arquivos v6 na pasta
`04_IA/Manta-Maestro/00-arquitetura/` do SharePoint (biblioteca
"Documentos") via `read_document`, comparada ao `CLAUDE.md` e ao estado
git deste repositório em 2026-09-08. Este arquivo é apenas registro de
comparação — não altera o `CLAUDE.md` em produção.*
