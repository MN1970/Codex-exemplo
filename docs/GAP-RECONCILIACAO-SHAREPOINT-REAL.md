# Gap — Reconciliação entre este repositório e o Manta Maestro real (SharePoint)

**Status:** 🟡 parcialmente investigado e parcialmente resolvido em
2026-09-07 (numeração de segmento corrigida; gap do embedder G010
resolvido com decisão real; Supabase confirmado real). **Reconciliação
completa não terminada** — escopo grande demais para uma sessão só.
Documentado aqui conforme combinado com o usuário em 2026-09-07.

> ⚠️ **Atualização 2026-09-07 (mesma sessão, investigação mais
> profunda)**: a primeira versão deste documento concluía que a
> infraestrutura Supabase/RAG era "nunca confirmada como real". Isso
> era **impreciso** — ao investigar mais (ver "O que é confirmado como
> real" abaixo), achamos evidência forte de que o projeto Supabase
> `ogxxgvgtulrbbppshjie` existe de verdade (mesma conta
> `mneves@mantaassociados.com`, confirmado por chamadas reais de API
> em `docs/SUPABASE-PROJECT-AUDIT.md`) e que há um pipeline real de RAG
> documentado em `07-execucoes/` e `03-funcionais/F1-ia/rag-retriever/`
> no SharePoint, com decisões de arquitetura versionadas (v3.0 → v3.1 →
> v3.2). A conclusão certa não é "tudo é fictício" — é "o núcleo
> (Supabase, RAG, algumas coleções, model tiering em 3 papéis) é real,
> mas com especificações diferentes das assumidas aqui, e a camada
> mais elaborada (APScheduler, ML routing com XGBoost, consensus
> voting, disaster recovery, 'Maestro OS v6.0') não tem nenhuma
> evidência real encontrada até agora."

## Como foi descoberto

Até 2026-09-07 esta sessão (e, aparentemente, todas as sessões que
escreveram este repositório antes dela) não tinha acesso real de
leitura/escrita ao SharePoint da Manta (`SharePoint_Manta` MCP). Toda a
arquitetura "Manta Maestro" documentada aqui — segmentos, agentes, RAG,
infraestrutura — foi escrita sem nunca ser checada contra a fonte real.
Ao ganhar acesso real nesta sessão (para corrigir a skill
`proposta-comercial`, ver `docs/MODELO-MESTRE-PROPOSTA.md`), a leitura
de `Documentos Compartilhados/04_IA/Manta-Maestro/09-base-conhecimento/
INDICE-CANONICAL.md` (índice canônico real, gerado 2026-07-11) revelou
divergências estruturais, não só pontuais.

## Divergências confirmadas

| Dimensão | Este repositório (`Codex-exemplo`) | SharePoint real (`INDICE-CANONICAL.md`) |
|---|---|---|
| Segmentos | S1–S13 (+ S11 "Mineração" identificado, S12 Óleo&Gás, S13 Edificações, todos "propostos") | **S1–S11**, sendo S1=Rodovias, S2=OAE, S3=Ferrovia, S4=Metrô, **S5=Imobiliário**, **S6=Edificações**, **S7=Portos**, **S8=Aeroportos**, **S9=Saneamento**, **S10=Energia**, **S11=Barragens** |
| Numeração S6–S11 | "Convenção A" (S6=Portos...S10=Barragens), com "Convenção B" explicitamente descartada nos Gaps abertos | É **exatamente** a "Convenção B" que este repositório descartou — Edificações=S6, Barragens=S11 |
| Atividades | A1–A10 (Proposta, Quantidades, Orçamento, Modelagem, Cronograma, Contratual, Claims, Advisory, Regulatório, Risco) | **Mesma lista e mesma ordem** — este eixo bate |
| Estrutura de skill | "20+ agentes" nomeados "Manta 00–25", cada um um `.claude/agents/*.md` extenso | `SKILL.md` por segmento/atividade/disciplina/funcional/sub-skill, em pastas numeradas (`01-segmentos/`, `02-atividades/`, `03-funcionais/`, `04-disciplinas/`, `05-sub-skills/`) — sem "Manta NN" como identidade central |
| RAG / infraestrutura | Supabase pgvector (projeto `ogxxgvgtulrbbppshjie`), 9 coleções, embedder bge-small/bge-m3 (contradição não resolvida), APScheduler, ML routing (XGBoost/NN), consensus voting, disaster recovery (RTO/RPO), Docker/K8s deploy | **Parcialmente confirmado real** (ver seção dedicada abaixo): projeto Supabase `ogxxgvgtulrbbppshjie` existe de fato (mesma conta, API real), com tabelas RAG populadas; embedder canônico real é bge-small-en-v1.5 (bge-m3 rejeitado 24/07). **Sem evidência real encontrada**: APScheduler (real usa `cron` de Linux — ver `07-execucoes/pipeline/cron.txt`), ML routing/XGBoost, consensus voting, disaster recovery RTO/RPO, deploy Docker/K8s — nada disso aparece nos documentos reais de arquitetura (`00-arquitetura/manta-maestro-arquitetura-v3.0.md`/`v3.2.md`) lidos até agora |
| Skill `proposta-comercial` | 18 seções, modos M1–M6, tabela de 13 perfis, ref. MNT-2026-COM-1183_D | 14 seções, modos M1–M5, tabela de 12 níveis, ref. Hope PPP MNT-2025-COM-1104 — corrigido em `docs/MODELO-MESTRE-PROPOSTA.md` ⚠️ **ver nota abaixo — esta linha ficou desatualizada em 2026-09-09** |

> ⚠️ **Nota (2026-09-09)**: a coluna "SharePoint real" da linha acima
> reflete a investigação de 2026-09-07 **antes** de uma fusão que
> aconteceu no mesmo dia. Releitura direta em 2026-09-09
> (`SharePoint_Manta` MCP) mostra que a skill de proposta agora vive em
> `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (versão
> 3.3.1, "supersedes: 3.3.0 (2026-09-07)"), cujo próprio changelog diz
> que a v3.3.0 "funde o corpo operacional da antiga skill
> `05-sub-skills/skill-proposta-comercial-SKILL.md`" de volta para
> dentro do arquivo de atividade. O arquivo real hoje tem **18 seções +
> Anexo**, **tabela de 13 perfis** (idêntica à conhecida antes da
> "correção") e a variante "Tipo A / Concessão de Infraestrutura de
> Grande Porte" (equivalente ao antigo modo "M6") **já aplicada**. O
> antigo `05-sub-skills/skill-proposta-comercial-SKILL.md` hoje é um
> stub de 667 bytes redirecionando para `_DEPRECATED.md`. Ver
> `docs/ATUALIZACAO-TARIFAS-2026.md` para o detalhe e para uma nova
> análise de atualização de valores da tabela tarifária, a partir de
> planilha real de fechamento de orçamento.

## O que é confirmado como real (investigação de 2026-09-07)

Achados concretos, cada um com fonte real citada, que **não** eram
conhecidos na primeira versão deste documento:

- **Supabase `ogxxgvgtulrbbppshjie` é real** — `docs/SUPABASE-PROJECT-AUDIT.md`
  chamou de verdade `list_organizations`/`list_projects`/`get_project`/
  `list_tables`/`get_advisors` (MCP Supabase) contra a conta
  `mneves@mantaassociados.com` e confirmou o projeto `manta-maestro`
  (`ogxxgvgtulrbbppshjie`, `sa-east-1`, `ACTIVE_HEALTHY`) com 34 tabelas
  reais, incluindo `rag_collections` (9 linhas), `sp_agent_routing` (9
  linhas), `maestro_routing_keywords` (50 linhas), `manta_rag_chunks`
  (204 linhas). Essa parte do repositório **não é fabricação** — é uma
  auditoria real bem conduzida.
- **Pipeline de RAG real existe, com histórico de decisões**:
  `07-execucoes/pipeline/` (código Python real: `chunker.py`,
  `embedder.py`, `supabase_client.py`, `sync_delta.py`, `ingestion.py`)
  e `03-funcionais/F1-ia/rag-retriever/pack-vps/` (pacote canônico
  atual). Evoluiu por versões documentadas:
  `00-arquitetura/manta-maestro-arquitetura-v3.0.md` (2026-07-09) →
  `v3.1` (2026-07-11) → `v3.2` patch (2026-07-22) →
  `09-base-conhecimento/RAG_ARQUITETURA_CANONICA.md` (2026-07-26,
  documento de verdade atual).
- **Embedder resolvido** (ver `docs/EMBEDDER-DECISION.md`): canônico
  real é `bge-small-en-v1.5` (384-d), confirmado 26/07/2026; `bge-m3`
  foi avaliado 24/07/2026 e **rejeitado**.
- **Agendamento real é `cron` de Linux, não APScheduler**:
  `07-execucoes/pipeline/cron.txt` documenta um cron job
  (`0 2 * * * .../run-sync-delta.sh`) rodando `sync_delta.py` num host
  Linux (`/opt/manta-maestro/`), não um scheduler Python (APScheduler)
  nem Windows Task Scheduler.
- **Model tiering real existe, com papéis diferentes dos deste
  repositório**: `03-funcionais/F1-ia/` tem subpastas
  `haiku-triager/`, `opus-orchestrator/`, `sonnet-worker/`,
  `prompt-lib/`, `rag-retriever/`. A v3.0 real define: Haiku
  classifica/sanitiza/recupera, **Opus planeja** (fase PLAN do ciclo
  INTAKE→DELIVER) e decide estrategicamente, Sonnet produz e verifica.
  Isso é mais específico e diferente do "Opus para claims complexos e
  arquitetura" descrito neste repositório — o real amarra o tier à
  **fase do ciclo de vida do pedido**, não à complexidade do domínio.
- **Ciclo de fases real** (v3.0): `INTAKE → READ → UNDERSTAND → PLAN →
  CONFIRM → EXECUTE → DELIVER → RE-PLAN`, com handshakes em 3 níveis
  (Maestro/Segmento/Atividade×Disciplina) e paralelismo default no
  EXECUTE (teto 8 sub-agentes). Não existe nada parecido descrito neste
  repositório — é uma camada de processo real sem contrapartida aqui.

## Sem evidência real encontrada (até agora)

Itens descritos neste repositório como operacionais que **não
apareceram em nenhum documento real lido até agora** — o que não prova
que não existam em algum outro lugar do SharePoint ainda não
explorado, mas não há confirmação:

- APScheduler, orquestração assíncrona Python-scheduler-based
- ML routing (XGBoost para roteamento, NN para duração/risco)
- Consensus voting (3/5 super-maioria) entre sub-agentes
- "Maestro OS v6.0", disaster recovery (RTO 4h/RPO 1h), pipeline
  Docker/K8s de deploy, monitoramento Prometheus/Grafana/PagerDuty
- Os project IDs/nomes de tabela específicos citados em
  `docs/COWORK-INTEGRATION.md` e em partes do `CLAUDE.md` que não batem
  com os nomes reais confirmados (`manta_execucoes.embeddings`,
  `rag_chunks` via RPC `match_rag_chunks` — não uma tabela chamada
  exatamente como este repositório assume em todo lugar)

## O que isso pode significar

Três hipóteses, em ordem decrescente de probabilidade — **atualizadas**
à luz do achado de que o núcleo Supabase/RAG é real:

1. **Núcleo real + camada de embelezamento fictício**: alguém (ou uma
   sessão) partiu de infraestrutura real (Supabase `ogxxgvgtulrbbppshjie`,
   pipeline RAG, model tiering em 3 papéis) e **extrapolou** para uma
   arquitetura muito mais elaborada e "enterprise" (ML routing,
   consensus voting, disaster recovery, Docker/K8s) sem que essa
   extrapolação tivesse qualquer decisão real por trás — nem no
   SharePoint, nem aprovação MN registrada. O núcleo real emprestou
   credibilidade a alegações fictícias em cima dele.
2. **Protótipo/exercício paralelo intencional**: este repositório pode
   ter sido criado como exercício de design ("Codex-exemplo" sugere
   isso pelo nome) para explorar uma arquitetura mais ambiciosa a
   partir do núcleo real — mas, se for esse o caso, isso nunca foi
   declarado explicitamente em nenhum README ou CLAUDE.md deste
   repositório; o texto sempre trata a arquitetura elaborada como se
   fosse a real ("Operacional", "produção", "gate humano MN").
3. **SharePoint real está incompleto na área explorada até agora**:
   possível — a investigação desta sessão cobriu `00-arquitetura`,
   `07-execucoes`, `03-funcionais/F1-ia`, `09-base-conhecimento`, mas
   não os outros F2-F9, nem os 06-exemplares, 08-rubricas, cada
   segmento individual. Pode haver mais infraestrutura real em pastas
   ainda não lidas — mas não há indício disso até agora, e o padrão
   dos documentos lidos (decisões versionadas, deprecação explícita,
   pendências registradas) sugere um sistema real bem mais modesto que
   o descrito neste repositório, não um sistema real igualmente
   elaborado só que "em outra pasta".

## Recomendação

Não decidir isso via consolidação automática de CLAUDE.md, como as
versões anteriores fizeram com outras divergências (numeração de
segmento, embedder). Esta é uma decisão de produto/arquitetura que
precisa do MN:

1. **Confirmar qual é o sistema real** — se é o SharePoint
   (`INDICE-CANONICAL.md` + `05-sub-skills/` etc.), então este
   repositório deveria ser reduzido/revisado para refletir isso, não o
   contrário.
2. Se confirmado que o SharePoint é a fonte real, planejar a
   reconciliação em fases (não em um único PR): (a) numeração de
   segmento — **feito** em 2026-09-07; (b) embedder — **feito** em
   2026-09-07; (c) trocar o modelo de "20 agentes Manta NN" pela
   estrutura real de pastas/SKILL.md; (d) corrigir as especificações
   do RAG/Supabase que são reais só que descritas errado aqui (nomes de
   tabela, agendamento via cron não APScheduler); (e) remover ou marcar
   claramente como "proposta de arquitetura futura, não implementada"
   tudo que não tem lastro real encontrado (ML routing, consensus
   voting, disaster recovery, Docker/K8s, "Maestro OS v6.0").
3. Enquanto isso não for decidido, tratar qualquer alegação deste
   repositório sobre "produção"/"operacional" com ceticismo e, quando
   uma mudança real for necessária (como a da skill
   `proposta-comercial`), **sempre verificar contra o SharePoint real
   primeiro**, não confiar no que já está escrito aqui.

## Feito nesta sessão (2026-09-07)

- Numeração de segmento corrigida no `CLAUDE.md` (S1–S11 real).
- Gap do embedder (G010) resolvido com decisão real (`docs/EMBEDDER-DECISION.md`,
  `docs/SUPABASE-PROJECT-AUDIT.md`, `CLAUDE.md` atualizados).
- Confirmado que o núcleo Supabase/RAG é real (não fictício) — ver
  seção "O que é confirmado como real" acima.

## Não resolvido nesta sessão

- Renumerar o frontmatter interno dos agentes `.md` afetados.
- Trocar o modelo de "20 agentes Manta NN" pela estrutura real de
  pastas/SKILL.md (mudança grande, toca praticamente todo o repositório).
- Corrigir nomes de tabela/agendamento (cron vs. APScheduler) nas
  demais menções espalhadas pelo repositório (`docs/COWORK-INTEGRATION.md`,
  `.github/workflows/`, `scripts/`, etc. — não auditado nesta sessão).
- Decidir o destino do que não tem lastro real (ML routing, consensus
  voting, disaster recovery, Docker/K8s, "Maestro OS v6.0") — remover,
  marcar como proposta futura, ou investigar mais (F2–F9, exemplares,
  rubricas, segmentos individuais ainda não lidos).
- Aguarda decisão do MN sobre a recomendação item 1 (confirmar
  explicitamente que o SharePoint é a fonte real e que este
  repositório deve convergir para ela).
