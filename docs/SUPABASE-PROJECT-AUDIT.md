# Auditoria de Projetos Supabase — Gap G012

**Ticket**: G012 — projeto Supabase inacessível
**Data**: 2026-07-31
**Autor**: Sonnet 13 (auditoria via MCP Supabase, execução direta — sem
dados fabricados; toda tabela abaixo vem de chamada real às APIs de
`list_organizations`, `list_projects`, `get_project`, `list_tables` e
`get_advisors`)
**Status**: Investigação concluída — aguarda decisão MN sobre
recomendações (seção 6) e execução dos action items (seção 7)

---

## 0. Resumo executivo

O `SKILL.md` do Maestro no SharePoint referencia o projeto Supabase
`xgluoaaymbdzbbudnwrh` (região `us-east-2`, ~221 registros). Esse
projeto **não aparece** na lista de projetos acessíveis pela conta
`mneves@mantaassociados.com`, e uma chamada direta
`get_project(xgluoaaymbdzbbudnwrh)` retorna:

```
MCP error -32600: You do not have permission to perform this action
```

Isso é exatamente o sintoma relatado no gap. A auditoria abaixo
confirma, com evidência de API (não inferência), que:

1. A organização Supabase associada a `mneves@mantaassociados.com`
   (`umlmzpmdgffaiwpxyflb`, plano free) tem **exatamente 4 projetos**,
   todos na região `sa-east-1`. Nenhum deles é o `xgluoaa...`.
2. `list_organizations` retorna **apenas 1 organização** para esta
   conta — se `xgluoaa...` fosse um projeto legado dentro de uma
   segunda org à qual o usuário ainda pertencesse, a org apareceria
   nessa lista. Ela não aparece.
3. A região do projeto morto (`us-east-2`) diverge da região-padrão
   de todos os 4 projetos ativos (`sa-east-1`) — indício adicional de
   proveniência distinta (conta/org diferente, provavelmente criada
   por outra pessoa ou em outro momento/tooling, antes da
   padronização em `sa-east-1`).
4. O volume citado no SKILL.md (~221 registros) não bate com nenhuma
   tabela isolada do `manta-maestro` atual, mas é da mesma ordem de
   grandeza da maior tabela RAG hoje existente
   (`manta_rag_chunks` = 204 linhas) — compatível com a hipótese de
   que `xgluoaa...` era uma versão anterior/experimental do RAG do
   Maestro, descontinuada quando o projeto atual foi provisionado em
   `sa-east-1`.

**Conclusão preliminar**: referência morta, não migração pendente de
dados vivos. Ver seção 4.3 para o racional completo e seção 6 para
recomendação de ação.

---

## 1. Metodologia

Toda a evidência de projeto/organização usada neste documento veio de
chamadas ao vivo, feitas nesta sessão, ao MCP Supabase configurado
para a conta `mneves@mantaassociados.com`:

| Chamada | Objetivo |
|---|---|
| `list_organizations()` | Descobrir todas as orgs visíveis à conta |
| `list_projects()` | Listar todos os projetos visíveis (as 4 orgs ativos) |
| `get_project(id)` | Confirmar status/região de cada projeto, e testar acesso ao `xgluoaa...` |
| `list_tables(project_id="ogxxgvgtulrbbppshjie")` | Levantar schema e contagem de linhas do `manta-maestro` ativo |
| `get_advisors(project_id, type="security")` | Checar postura de segurança do projeto ativo (achado correlato, seção 5) |

Não foi feita nenhuma tentativa de acessar `xgluoaa...` por fora do
MCP (sem tentativa de força-bruta de credenciais, sem scraping do
dashboard Supabase). O objetivo era confirmar o estado relatado no
gap, não contornar a permissão.

Repositório local (`Codex-exemplo`) também foi varrido
(`grep -ri "xgluoaa|ogxxgvg"`) — **nenhuma referência** ao ID morto
existe no código versionado; a única referência conhecida está no
`SKILL.md` do SharePoint citado no ticket do gap, fora do escopo de
leitura direta desta auditoria (MCP SharePoint não foi acionado pois
o objetivo era o lado Supabase; ver action item AI-5 para fechar essa
ponta).

---

## 2. Auditoria dos 4 projetos Supabase da organização

Organização: **`umlmzpmdgffaiwpxyflb`** ("mneves@mantaassociados.com's
Org"), plano **free**, canais de release permitidos: `ga`, `preview`.

| Projeto | ID (ref) | Região | Status | Criado em | Postgres |
|---|---|---|---|---|---|
| **manta-maestro** | `ogxxgvgtulrbbppshjie` | sa-east-1 | 🟢 `ACTIVE_HEALTHY` | 2026-06-14 | 17.6.1.127 (PG17, GA) |
| manta-tocantins | `vigfmejhdwuhlytloiyj` | sa-east-1 | ⚪ `INACTIVE` | 2026-05-29 | 17.6.1.127 (PG17, GA) |
| manta-rodovias | `runtluukrhjroxoikbpu` | sa-east-1 | ⚪ `INACTIVE` | 2026-06-04 | 17.6.1.127 (PG17, GA) |
| manta-portal-piloto | `kwuubcnedqtapvykmyye` | sa-east-1 | ⚪ `INACTIVE` | 2026-06-21 | 17.6.1.127 (PG17, GA) |

Observações:

- `manta-tocantins` é o projeto **mais antigo** do grupo
  (2026-05-29), condizente com o repositório operacional
  `CT5500097701 — Nova Ponte sobre o Rio Tocantins` já em produção
  documental (skills `conclusao-janelas`, `gr04-infraestrutura-pontes`
  referenciam esse contrato). Provavelmente o primeiro projeto Supabase
  criado pela Manta, hoje pausado por inatividade (free tier pausa
  projetos após 7 dias sem uso).
- `manta-rodovias` e `manta-portal-piloto` foram criados em sequência
  rápida (04/06 e 21/06), ambos já `INACTIVE` — sugerem projetos-piloto
  de curta duração, possivelmente testes de arquitetura antes de
  convergir para o `manta-maestro` único (criado 14/06, atualmente o
  único `ACTIVE_HEALTHY`).
- **Todos os 4 estão no plano free da mesma organização.** Isso é
  relevante para a recomendação de consolidação (seção 6.2): não há
  billing separado justificando múltiplos projetos — o padrão observado
  é mais "esqueci de desativar/apagar" do que "isolamento intencional
  por tenant".

### 2.1. Detalhe — `manta-maestro` (`ogxxgvgtulrbbppshjie`), o único ativo

`list_tables` no schema `public` retornou 34 tabelas. Resumo por
função:

| Grupo | Tabelas | Linhas (soma) |
|---|---|---|
| RAG core | `manta_rag_documents` (111), `manta_rag_chunks` (204), `manta_rag_cases` (0), `manta_rag_queries` (1), `manta_rag_feedback` (0), `manta_rag_errors` (1), `manta_rag_decisions` (2), `manta_rag_ml_predictions` (0), `manta_rag_ml_models` (0), `manta_rag_ml_training_runs` (0) | 319 |
| Knowledge pipeline (WF-AKP-001) | `teses_academicas` (44), `teses_academicas_history` (1), `knowledge_extractions` (88), `ke_embeddings` (86), `akp_curation_backlog` (0) | 219 |
| A2A / orquestração de agentes | `manta_agent_messages` (4), `manta_agent_capabilities` (30), `manta_api_clients` (0), `manta_api_calls` (0), `agent_episodes` (1), `agent_change_requests` (0), `agent_change_reviews` (0) | 35 |
| Governança de rotas/config | `rag_collections` (9), `sp_agent_routing` (9), `maestro_routing_keywords` (50) | 68 |
| Operacional / projetos | `manta_projects` (0), `manta_projeto_status_snapshots` (0), `manta_case_elements` (0), `mce_embeddings` (0), `manta_quantitativos_reconciliacao` (0), `quantitativo_overrides` (0), `field_measurements` (0), `maestro_cost_log` (0) | 0 |
| Traço/telemetria | `manta_trace` (10) | 10 |

Ponto de atenção para a hipótese de migração (seção 4): o comentário
da tabela `manta_rag_chunks` registra
`"Chunks com embeddings 1024d (bge-m3, canonical Maestro 2026-07-03)"`.
Isso significa que o schema vetorial **atual** usa `bge-m3` (1024
dimensões). Já a skill `manta-maestro` (catálogo de skills desta
sessão) descreve o RAG do Maestro como
`"BAAI/bge-small-en-v1.5 384d, projeto ogxxgvgtulrbbppshjie"` — **384
dimensões**, modelo diferente. Ou seja, o próprio projeto ativo já
passou por pelo menos uma migração de embedding (384d → 1024d,
datada de 2026-07-03) sem que a descrição da skill tenha sido
atualizada. Isso é evidência indireta de que o time já tem histórico
de trocar de schema/modelo de embedding e não voltar para atualizar a
documentação — o mesmo padrão que provavelmente explica a referência
morta ao `xgluoaa...`.

---

## 3. Investigação do `xgluoaaymbdzbbudnwrh`

### 3.1. O que sabemos com certeza (evidência direta)

| Fato | Fonte | Confiança |
|---|---|---|
| `get_project("xgluoaaymbdzbbudnwrh")` retorna `permission denied` (MCP -32600) | Chamada direta nesta sessão | Alta |
| A conta `mneves@mantaassociados.com` só enxerga 1 organização Supabase | `list_organizations()` | Alta |
| Essa 1 organização tem 4 projetos, nenhum com esse ID | `list_projects()` | Alta |
| Nenhum dos 4 projetos ativos está em `us-east-2` (todos `sa-east-1`) | `list_projects()` | Alta |
| SKILL.md do SharePoint cita `us-east-2`, ~221 registros, papel = "Maestro" | Ticket do gap G012 (não reverificado nesta sessão — MCP SharePoint fora do escopo desta auditoria) | Média (fonte secundária) |
| Nenhuma referência a `xgluoaa` existe no código versionado deste repo | `grep -ri` no repo local | Alta |

### 3.2. Hipóteses avaliadas

**H1 — Projeto de outra organização/conta Supabase (mais provável).**
Como `list_organizations()` só retorna 1 org para esta conta, e o erro
é "permission denied" (não "not found"), a interpretação mais direta é
que o projeto existe, mas pertence a uma organização Supabase à qual
`mneves@mantaassociados.com` **não tem mais** (ou nunca teve) acesso —
por exemplo, criado por outro membro da equipe (ou por um agente/CI
com conta própria) em conta pessoal ou em outra org corporativa, antes
da consolidação em `umlmzpmdgffaiwpxyflb`. A região `us-east-2`
reforça isso: nenhum projeto da org atual usa `us-east-2` — sugere
proveniência de um fluxo de criação diferente (ex.: `create_project`
rodado sem especificar região, caindo no default da conta/CLI de
quem criou, versus os 4 projetos atuais que foram todos criados
deliberadamente em `sa-east-1`).

**H2 — Legacy/arquivado da própria organização, removido/transferido.**
Também é possível que `xgluoaa...` tenha sido criado dentro da mesma
org e depois **transferido** para outra org ou **deletado**. Supabase
mantém o histórico de billing/transferência no dashboard da
organização, que não é exposto pelas tools de MCP disponíveis aqui —
não é possível confirmar ou descartar via API. Esta hipótese exigiria
confirmação manual no dashboard Supabase (ver AI-2).

**H3 — Erro de digitação/registro no SKILL.md.**
Um ID de projeto Supabase tem 20 caracteres alfanuméricos — improvável
(mas não impossível) que seja um typo de outro ID real. Comparando
caractere a caractere com os 4 IDs ativos
(`ogxxgvgtulrbbppshjie`, `vigfmejhdwuhlytloiyj`, `runtluukrhjroxoikbpu`,
`kwuubcnedqtapvykmyye`), `xgluoaaymbdzbbudnwrh` não tem similaridade
suficiente com nenhum para ser um typo plausível de um deles. **H3
descartada.**

**H4 — Dados vivos que precisam ser migrados.**
Não há como confirmar isso sem acesso ao próprio projeto morto (dados
não visitáveis via `permission denied`). Mas o argumento indireto da
seção 0/2.1 (o Maestro já migrou de embedding 384d→1024d dentro do
próprio projeto ativo, em 2026-07-03, sem atualizar a doc) torna mais
provável que `xgluoaa...` seja um **antecessor já superado** do RAG
atual — não uma fonte de dados exclusiva e não replicada. Ainda assim,
como não há certeza absoluta, a recomendação (seção 6) é confirmar
antes de simplesmente apagar a referência.

### 3.3. Conclusão

**Veredito: referência provavelmente morta, não migração ativa
pendente — mas com confirmação humana obrigatória antes de fechar o
gap**, porque:

- A API confirma que o projeto não é acessível pela conta/org
  corporativa atual (H1 é a explicação mais simples e consistente com
  todos os fatos: região diferente, org ausente da lista, erro de
  permissão e não de "recurso inexistente").
- O volume de dados citado (221 registros) é compatível com uma
  versão anterior e menor do RAG do Maestro, plausivelmente
  substituída pela migração de embedding já documentada em
  `manta_rag_chunks` (2026-07-03).
- Não existe, no repositório operacional (`Codex-exemplo`) nem nos
  4 projetos ativos, nenhuma dependência de código apontando para
  `xgluoaa...` — apenas a menção isolada no `SKILL.md` do SharePoint.

Isso não é uma prova definitiva de que os dados podem ser descartados
sem verificação — é uma auditoria de acessibilidade e plausibilidade,
não uma inspeção do conteúdo do projeto morto (que é impossível sem
acesso). Por isso o action item AI-1 (seção 7) exige que **alguém com
acesso ao dashboard Supabase da conta que criou `xgluoaa...`**
confirme se o projeto ainda existe, a quem pertence, e se tem dados
que não estão replicados em `manta-maestro`.

---

## 4. Achado correlato de segurança (bônus da auditoria)

Ao rodar `get_advisors(type="security")` no `manta-maestro` ativo
(`ogxxgvgtulrbbppshjie`) para levantar contexto de schema, apareceram
achados de segurança que não fazem parte do escopo original do G012,
mas são graves o suficiente para registrar aqui em vez de descartar:

| Nível | Achado | Tabelas afetadas |
|---|---|---|
| 🔴 ERROR | RLS desabilitado em tabela pública (exposta a `anon`/`authenticated` via PostgREST) | `rag_collections`, `sp_agent_routing`, `maestro_routing_keywords` |
| 🟡 WARN | Extensão `vector` instalada no schema `public` (deveria estar em schema dedicado) | extensão `vector` |
| 🔵 INFO | RLS habilitado mas sem nenhuma policy criada (bloqueia todo acesso, inclusive do dono, dependendo do role) | `agent_change_requests`, `agent_change_reviews`, `manta_agent_capabilities`, `manta_agent_messages`, `manta_api_calls`, `manta_api_clients`, `manta_case_elements`, `manta_projects`, `manta_projeto_status_snapshots`, `manta_rag_decisions`, `manta_rag_errors`, `manta_rag_feedback`, `manta_rag_ml_models`, `manta_rag_ml_training_runs`, `mce_embeddings`, `teses_academicas_history` |

O ERROR é o mais urgente: as 3 tabelas de roteamento/coleções RAG
estão **totalmente expostas** (leitura e escrita) a qualquer cliente
que tenha a chave `anon` do projeto. Não é escopo direto do G012, mas
como o SQL de remediação é trivial, está incluído como AI-6 (seção 7)
— **não aplicado automaticamente**, pois habilitar RLS sem políticas
corretas bloquearia acesso legítimo do próprio Maestro. SQL de
referência:

```sql
ALTER TABLE public.rag_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sp_agent_routing ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.maestro_routing_keywords ENABLE ROW LEVEL SECURITY;
-- ATENÇÃO: aplicar policies de leitura antes/junto, ou o Maestro
-- perde acesso de leitura a essas 3 tabelas em runtime.
```

---

## 5. Recomendações

### 5.1. Limpar referências mortas

- Atualizar o `SKILL.md` no SharePoint para **remover** a menção a
  `xgluoaaymbdzbbudnwrh` e apontar explicitamente para
  `ogxxgvgtulrbbppshjie` (`manta-maestro`, `sa-east-1`,
  `ACTIVE_HEALTHY`), que é o projeto real em uso hoje.
- Adicionar ao próprio `SKILL.md` uma nota de rodapé de proveniência
  ("projeto Y substitui X, migrado em <data>, ver AUDIT G012") para
  que a próxima pessoa que encontrar um ID de projeto desconhecido
  tenha contexto imediato em vez de repetir esta investigação.
- Rodar uma varredura mais ampla (não só neste repo, mas nos outros
  repositórios operacionais — `manta-hub`, runbooks no SharePoint,
  scripts locais de qualquer agente) por `xgluoaa` antes de considerar
  a limpeza completa. Esta auditoria só cobriu `Codex-exemplo`.

### 5.2. Consolidar dados em um único projeto?

**Recomendação: sim, com uma exceção.** Dos 4 projetos ativos na
organização, apenas `manta-maestro` está `ACTIVE_HEALTHY`; os outros 3
(`manta-tocantins`, `manta-rodovias`, `manta-portal-piloto`) estão
`INACTIVE` (pausados por inatividade no plano free) e nenhum
apresentou, nesta auditoria, justificativa de isolamento por
billing/tenant/compliance que impeça a consolidação.

- **`manta-rodovias`** e **`manta-portal-piloto`**: parecem pilotos
  de curta duração que não avançaram. Se não houver dado que não
  esteja também em `manta-maestro`, a recomendação é **exportar
  schema+dados relevantes (se houver) e desativar/deletar** — reduz
  superfície de gerenciamento e custo cognitivo de "qual projeto é o
  certo".
- **`manta-tocantins`**: merece checagem mais cuidadosa antes de
  qualquer decisão — é o projeto mais antigo do grupo e o nome sugere
  vínculo direto com o contrato ativo `CT5500097701` (Nova Ponte sobre
  o Rio Tocantins), que tem múltiplas skills operacionais no catálogo
  atual (`conclusao-janelas`, `gr04-infraestrutura-pontes`). Antes de
  consolidar ou desativar, confirmar se esse projeto guarda dados de
  claim/reequilíbrio que não têm outra cópia.
- Não recomendamos forçar tudo em um único projeto sem essa checagem
  prévia — mas o **padrão-alvo** deveria ser: 1 projeto Supabase
  "produção" (`manta-maestro`) + projetos separados **apenas** quando
  houver razão documentada (ver 5.3).

### 5.3. Documentar política de multi-project

Hoje não existe, em nenhum lugar do repositório, uma política
explícita de quando criar um novo projeto Supabase vs. reutilizar o
existente. Isso é provavelmente a causa raiz tanto do G012 quanto do
acúmulo de 3 projetos `INACTIVE`. Recomenda-se registrar, em um ADR
curto (`docs/ADR-supabase-multi-project.md` ou seção no
`CLAUDE.md` master), critérios objetivos, por exemplo:

1. **Isolamento por contrato/cliente sensível** (ex.: claim
   confidencial que não pode compartilhar RLS/schema com o resto) —
   justifica projeto dedicado.
2. **Ambiente de teste/protótipo de arquitetura** — permitido, mas com
   **prazo de vida** definido (ex.: 30 dias) após o qual o projeto é
   automaticamente candidato a arquivamento/deleção se não for
   promovido a produção.
3. **Todo o resto** (RAG do Maestro, routing, agentes, telemetria) —
   vive em `manta-maestro`.
4. Toda criação de projeto novo deve ser registrada em um log simples
   (mesmo que seja uma tabela `manta_projects` já existente no
   `manta-maestro`, hoje com 0 linhas — subutilizada) com
   `nome, motivo, owner, data_criacao, data_revisao_planejada`.

Isso resolve o problema de raiz: sem essa política, o próximo
`xgluoaa...` é questão de tempo.

---

## 6. Action items

| # | Ação | Owner | Deadline | Prioridade |
|---|---|---|---|---|
| AI-1 | Confirmar no dashboard Supabase (fora do MCP desta conta) se `xgluoaaymbdzbbudnwrh` ainda existe, a qual conta/org pertence, e se contém dados sem cópia em `manta-maestro` | MN (Mauricio Neves) — único com acesso corporativo amplo a contas Supabase da Manta | 2026-08-07 | Alta |
| AI-2 | Se AI-1 confirmar dados órfãos relevantes: exportar (`pg_dump` ou `execute_sql` via MCP se acesso for restabelecido) e reimportar em `manta-maestro` | MN + Sonnet (execução assistida) | 2026-08-14 (depende de AI-1) | Alta |
| AI-3 | Atualizar `SKILL.md` no SharePoint (`01-agentes-fundamentais/...`) removendo a referência a `xgluoaa...` e apontando para `ogxxgvgtulrbbppshjie` | MN (ou Sonnet via MCP M365 se write scope for liberado) | 2026-08-07 | Alta |
| AI-4 | Varrer outros repositórios operacionais (`manta-hub`, runbooks SharePoint) por referências a `xgluoaa` além deste repo | Time Maestro (dono do `manta-hub`) | 2026-08-14 | Média |
| AI-5 | Ler o `SKILL.md` original no SharePoint citado no gap (via MCP SharePoint) para confirmar o texto exato da referência antes de editar (AI-3 depende disso) | Sonnet (próxima sessão com MCP SharePoint habilitado) | 2026-08-04 | Alta |
| AI-6 | Aplicar RLS + policies nas 3 tabelas expostas (`rag_collections`, `sp_agent_routing`, `maestro_routing_keywords`) — achado correlato da seção 4 | MN (aprovação) + Sonnet (execução via `apply_migration`) | 2026-08-07 | Alta (segurança) |
| AI-7 | Decidir o destino de `manta-rodovias` e `manta-portal-piloto` (desativar/deletar vs. manter) | MN | 2026-08-21 | Média |
| AI-8 | Checar se `manta-tocantins` guarda dados exclusivos do contrato CT5500097701 antes de qualquer decisão de consolidação | MN + time do contrato Tocantins | 2026-08-21 | Média |
| AI-9 | Redigir e aprovar política de multi-project Supabase (seção 5.3) como ADR ou seção nova no `CLAUDE.md` master | MN (aprovação) + Sonnet (rascunho) | 2026-08-28 | Média |
| AI-10 | Popular `manta_projects` (hoje 0 linhas) como log de criação de projetos Supabase, conforme política do AI-9 | Time Maestro | 2026-09-04 (depende de AI-9) | Baixa |

---

## 7. Apêndice — evidência bruta das chamadas

Para reprodutibilidade, os resultados brutos (não editados) das
chamadas de auditoria:

```
list_organizations() →
  [{"id":"umlmzpmdgffaiwpxyflb","slug":"umlmzpmdgffaiwpxyflb",
    "name":"mneves@mantaassociados.com's Org"}]

list_projects() → 4 projetos, todos region=sa-east-1, org_id=umlmzpmdgffaiwpxyflb:
  manta-maestro         ogxxgvgtulrbbppshjie  ACTIVE_HEALTHY  criado 2026-06-14
  manta-tocantins       vigfmejhdwuhlytloiyj  INACTIVE        criado 2026-05-29
  manta-rodovias        runtluukrhjroxoikbpu  INACTIVE        criado 2026-06-04
  manta-portal-piloto   kwuubcnedqtapvykmyye  INACTIVE        criado 2026-06-21

get_project("xgluoaaymbdzbbudnwrh") →
  McpError -32600: "You do not have permission to perform this action"

get_project("ogxxgvgtulrbbppshjie") →
  confirma manta-maestro, sa-east-1, ACTIVE_HEALTHY, PG 17.6.1.127

list_tables("ogxxgvgtulrbbppshjie", schemas=["public"]) →
  34 tabelas, ver detalhamento seção 2.1

get_advisors("ogxxgvgtulrbbppshjie", type="security") →
  1 ERROR (RLS desabilitado em 3 tabelas públicas), 1 WARN (extensão
  vector em public), 16 INFO (RLS habilitado sem policy)
```

Nenhum dado de conteúdo (linhas reais das tabelas) foi extraído nesta
auditoria — apenas metadados de schema (nomes, contagem de linhas,
comentários de tabela) via `list_tables`, suficiente para o escopo do
gap sem expor dados sensíveis de projeto/cliente.

---

## Histórico

- **2026-07-31** — versão inicial. Auditoria executada por Sonnet 13
  em resposta ao gap G012. Aguarda AI-1 e AI-5 para fechar
  definitivamente a investigação do `xgluoaa...` e AI-6 para o achado
  de segurança correlato.
