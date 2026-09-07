# Decisão de Embedder — bge-m3 vs. bge-small-en-v1.5

**Gap:** G010
**Autor:** Sonnet 11
**Data:** 2026-07-31
**Status:** 🟡 Aguardando aprovação MN (gate humano obrigatório)
**Ticket relacionado:** MNT-2026-UPGRADE-AGENTS-S6S10 (RAG das 5 novas coleções S6–S10 depende desta decisão)

---

## 1. Resumo executivo

Existe uma divergência entre o que foi **decidido** e o que está **em
produção**:

| | Valor |
|---|---|
| Decisão registrada em 22/07/2026 | `bge-m3` (1024-d), classificado como "canônico" |
| Embedder rodando em produção hoje | `bge-small-en-v1.5` (384-d) |
| Chunks migrados para bge-m3 | **0 de 204** (0%) |
| Impacto direto | As 9 coleções RAG do Manta Maestro (`rod:`, `oae:`, `fer:`, `mtr:`, `por:`, `aer:`, `san:`, `ene:`, `bar:`) — incluindo as 5 novas de S6–S10 — dependem de um embedder único e consistente para a busca vetorial funcionar. |

Este documento analisa as duas opções, recomenda um caminho e propõe
um roadmap de execução. **A decisão final exige aprovação de MN antes
de qualquer alteração em produção**, conforme o padrão de gate humano
já usado neste repositório (ver `docs/DEPLOY-v4.2.md`, seção "Merge dos
PRs (gate humano MN)").

**Recomendação desta análise: Opção B — migrar para bge-m3**, mantendo
a decisão de 22/07, por três motivos que pesam mais que o custo de
migração:
1. o corpus é multilíngue (PT/ES/EN) e `bge-small-en-v1.5` é
   monolíngue-inglês;
2. o volume a migrar é pequeno (204 chunks — trivial em custo de
   compute);
3. não há decisão técnica formal revertendo o que foi decidido em
   22/07 — hoje existe apenas inércia de execução, não um novo
   argumento técnico contra bge-m3.

---

## 2. Contexto

O Manta Maestro (skill `manta-maestro`, v5.0.1) usa RAG via Supabase
pgvector no projeto `ogxxgvgtulrbbppshjie`, hoje descrito como rodando
com **BAAI/bge-small-en-v1.5, 384 dimensões**. A migração v4.2
(`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) criou 5 novas
coleções RAG (`saneamento`, `energia`, `portos`, `aeroportos`,
`barragens`) que ainda não têm chunks vetorizados — o gap G010 bloqueia
a decisão de **com qual embedder** essas e as coleções já existentes
devem ser (re)indexadas.

Em 22/07/2026 foi tomada a decisão de adotar `bge-m3` como o embedder
canônico do sistema. Essa decisão nunca chegou a ser executada: o
pipeline de produção continua gerando embeddings com
`bge-small-en-v1.5`, e os 204 chunks existentes na base (distribuídos
entre as coleções `rod:`, `oae:`, `fer:`, `mtr:` e as novas S6–S10)
estão **0% migrados** para o espaço vetorial de 1024-d do bge-m3.

Isso deixa o sistema em um estado ambíguo e potencialmente perigoso:
qualquer código ou skill que assuma "canônico = bge-m3" (por exemplo,
se o `CLAUDE.md` ou uma skill nova documentar 1024-d) vai gerar
embeddings de query incompatíveis com os embeddings de documento
armazenados (384-d), quebrando silenciosamente a busca vetorial ou
lançando erro de dimensão no `<=>`/`<->` do pgvector.

---

## 3. Análise comparativa

### 3.1. bge-m3 (BAAI/bge-m3)

| Critério | Avaliação |
|---|---|
| Dimensão do vetor | 1024-d |
| Cobertura de idioma | **Multilíngue** — treinado e validado para 100+ idiomas, incluindo português e espanhol nativamente |
| Qualidade de recuperação (relatada) | Superior ao bge-small em benchmarks multilíngues e em textos longos (MIRACL, MKQA); suporta busca densa + esparsa + multi-vetor (ColBERT-like) no mesmo modelo |
| Comprimento de contexto | Até 8192 tokens (adequado para chunks técnicos longos — memoriais, cláusulas de edital) |
| Tamanho do modelo / custo de inferência | ~2.27 GB, mais pesado para servir; maior latência e uso de memória por embedding gerado |
| Custo de armazenamento por vetor | ~2.7× o espaço de bge-small (1024 vs. 384 floats) — para 204 chunks isso é irrelevante em termos absolutos (kilobytes), mas relevante se o corpus crescer para dezenas de milhares de chunks |
| Maturidade operacional no nosso stack | **Não validado em produção** — nunca foi de fato usado para gerar um embedding real no pipeline |
| Alinhamento com o corpus real da Manta | **Alto** — as fontes documentadas no `CLAUDE.md` e na migração v4.2 incluem NBR (PT), SNIS (PT), Lei 14.026 (PT), fontes AySA (ES/Argentina), ANEEL/EPE/ONS (PT), e só uma fração é inglês (ICOLD, PIANC, ICAO, IEEE, FAA) |

**Pros:**
- Único embedder do stack capaz de tratar corretamente PT + ES + EN no
  mesmo espaço vetorial sem gambiarra de "traduzir antes de indexar".
- Já foi objeto de uma decisão formal (22/07) — adotá-lo não é uma
  mudança de rumo, é terminar o que já foi decidido.
- Suporta chunks mais longos sem truncamento (8192 vs. 512 tokens
  tipicamente em modelos small), reduzindo a necessidade de
  chunking agressivo em memoriais e editais extensos.

**Contras:**
- Maior custo computacional por embedding (latência de indexação e de
  query) — relevante se o volume crescer rápido (edital novo com
  centenas de páginas).
- Reindexação obrigatória de tudo que já existe (mas ver §4 — é
  barato no volume atual).
- Nenhum embedding real gerado até hoje — zero validação empírica de
  qualidade *neste* corpus específico da Manta.

### 3.2. bge-small-en-v1.5 (BAAI/bge-small-en-v1.5)

| Critério | Avaliação |
|---|---|
| Dimensão do vetor | 384-d |
| Cobertura de idioma | **Monolíngue, inglês** — não foi treinado para português ou espanhol; embeddings de texto em PT/ES tendem a ficar mal calibrados no espaço vetorial |
| Qualidade de recuperação (relatada) | Boa para textos em inglês curtos; degrada em textos técnicos em PT/ES, que são a maioria do corpus Manta |
| Tamanho do modelo / custo de inferência | ~133 MB — leve, rápido, barato de servir |
| Maturidade operacional no nosso stack | **Em produção hoje**, com 204 chunks já indexados e funcionando |
| Alinhamento com o corpus real da Manta | **Baixo** — a maior parte das fontes documentadas (NBR, SNIS, Lei 14.026, ANEEL, AySA/Argentina) não é inglês |

**Pros:**
- Já está rodando — zero esforço de migração, zero risco de quebra.
- Mais barato e mais rápido por embedding gerado.
- "Funciona" no sentido de que o Maestro responde e a busca retorna
  resultados hoje.

**Contras:**
- É um modelo **inglês** aplicado a um corpus majoritariamente em
  **português e espanhol**. Isso não é um detalhe — é uma
  incompatibilidade estrutural entre a ferramenta e o dado.
  Recuperação semântica em PT/ES com um encoder treinado só em inglês
  tende a funcionar "por acaso" (sobreposição lexical, cognatos,
  termos técnicos em inglês dentro do texto em PT) e não por real
  compreensão semântica multilíngue.
- Contradiz a decisão já tomada em 22/07 sem que exista um documento
  formal explicando por que ela teria sido revertida.
- Qualquer expansão futura do RAG para os novos segmentos S6–S10
  (Portos, Aeroportos, Saneamento, Energia, Barragens) vai herdar o
  mesmo problema em escala maior, já que as fontes desses segmentos
  (SNIS, ANEEL, ANTAQ, ICOLD/CBDB em português) são majoritariamente
  em português.

### 3.3. Tabela-resumo

| Dimensão | bge-m3 | bge-small-en-v1.5 |
|---|---|---|
| Dimensões do vetor | 1024 | 384 |
| Multilíngue (PT/ES) | ✅ Sim, nativo | ❌ Não — apenas inglês |
| Custo de inferência | Mais alto | Mais baixo |
| Custo de armazenamento (204 chunks) | Irrelevante (~800 KB total) | Irrelevante (~300 KB total) |
| Em produção hoje | ❌ Não | ✅ Sim |
| Decisão formal anterior | ✅ 22/07/2026 | — |
| Adequação ao corpus real da Manta | ✅ Alta | ❌ Baixa |
| Esforço de migração | 204 chunks (baixo) | N/A |

---

## 4. Recomendação

**Migrar para bge-m3 (Opção B), concluindo a decisão de 22/07.**

Motivos, em ordem de peso:

1. **Adequação ao corpus é o critério dominante.** Um RAG existe para
   recuperar o chunk certo dado uma pergunta. Se o encoder não entende
   bem o idioma do corpus, a qualidade de recuperação está comprometida
   na raiz — nenhuma otimização de chunking, prompt ou reranking
   compensa isso de forma confiável. Como a maioria das fontes documentadas
   (NBR, SNIS, Lei 14.026, ANEEL/EPE/ONS, fontes AySA em espanhol) está em
   PT/ES, `bge-small-en-v1.5` é a ferramenta errada para o dado que
   temos.
2. **O custo de migração é pequeno no estado atual.** 204 chunks é um
   volume trivial para reindexar — o esforço de execução é medido em
   horas de engenharia, não em orçamento de compute relevante. Quanto
   mais tempo se espera para migrar, maior o volume acumulado (as 5
   coleções novas de S6–S10 ainda não têm nenhum chunk indexado) e
   maior o custo de uma migração futura.
3. **Não há uma decisão técnica nova que justifique reverter 22/07.**
   O estado atual (bge-small em produção) é resultado de a migração
   nunca ter sido executada, não de uma reavaliação que tenha
   encontrado bge-m3 inadequado. Manter bge-small por inércia,
   sem um argumento técnico documentado, não é uma decisão — é um
   gap não fechado (este próprio G010).
4. **Custo de latência/infra do bge-m3 é administrável.** O modelo é
   mais pesado, mas o volume de indexação (chunks novos por semana,
   estimado a partir do ritmo de ingestão de editais/projetos) não
   parece justificar otimizar para o encoder mais leve às custas de
   qualidade multilíngue.

Se, **após esta análise**, a decisão de MN for manter bge-small
mesmo assim, o Roadmap A abaixo cobre o que precisa ser documentado
para isso ser uma decisão explícita e não um gap silencioso.

---

## 5. Roadmap

### 5.1. Se a decisão for A — manter bge-small-en-v1.5

Isso reverteria formalmente a decisão de 22/07. Para isso ser
rastreável (e não um segundo gap "por que a decisão mudou de novo"),
é necessário:

- [ ] Registrar no `CLAUDE.md` master um ADR (Architecture Decision
  Record) curto explicando **por que** a decisão de 22/07 foi
  revertida — ex.: restrição de custo/infra identificada, latência
  inaceitável em teste real, benchmark interno que mostrou bge-m3 sem
  ganho relevante para o corpus da Manta. Sem esse motivo documentado,
  o gap G010 simplesmente reaparece na próxima auditoria.
- [ ] Atualizar toda menção a "bge-m3 canônico" nos docs do Maestro
  (`manta-maestro` skill description, runbooks) para refletir
  bge-small como o embedder real e definitivo.
- [ ] Mitigar o problema de idioma sem trocar de embedder — opções
  paliativas a avaliar (nenhuma resolve completamente):
  - Pré-processar/traduzir chunks PT/ES para inglês antes de indexar
    (custo de qualidade e de manutenção de um pipeline de tradução).
  - Avaliar um modelo *small* multilíngue alternativo (ex.:
    `bge-small` não tem variante multilíngue oficial da BAAI — a
    alternativa nessa faixa de tamanho seria outro fornecedor, o que
    reabre a decisão de embedder do zero).
- [ ] Formalizar o encerramento do G010 com a assinatura de MN sobre
  o ADR acima.

### 5.2. Se a decisão for B — migrar para bge-m3 (recomendado)

**Escopo:** 204 chunks existentes + pipeline de ingestão futuro
(inclusive as 5 coleções S6–S10 ainda vazias).

| Etapa | Ação | Esforço estimado |
|---|---|---|
| 1. Provisionamento | Disponibilizar `BAAI/bge-m3` no ambiente de inferência usado hoje para gerar embeddings (self-hosted via `sentence-transformers`/sistema equivalente, ou endpoint gerenciado) | 0,5 dia |
| 2. Schema | No Supabase (projeto `ogxxgvgtulrbbppshjie`), adicionar coluna nova de vetor 1024-d em `rag_chunks` (ex.: `embedding_bge_m3 vector(1024)`) **sem remover** a coluna 384-d existente, para permitir rollback e validação lado a lado | 0,5 dia |
| 3. Reindexação em lote | Rodar os 204 chunks existentes pelo bge-m3 e popular a nova coluna. Volume trivial — minutos de processamento puro; a maior parte do tempo é escrever/testar o script de migração | 1 dia (inclui testes) |
| 4. Índice vetorial | Recriar índice (`hnsw` ou `ivfflat`) do pgvector sobre a nova coluna de 1024-d (pgvector suporta até 2000 dimensões em `hnsw`, então não há bloqueio técnico) | 0,5 dia |
| 5. Validação de qualidade | Rodar as queries de teste já existentes em `tests/routing/prompts.md` (adaptando de teste de routing para teste de recuperação) comparando resultados bge-small vs. bge-m3 para o mesmo conjunto de perguntas, com foco em queries em português e espanhol | 1 dia |
| 6. Corte (cutover) | Trocar a coluna usada pelo pipeline de query para a de 1024-d; manter a coluna antiga por um período de observação (ex.: 1–2 semanas) antes de removê-la | 0,5 dia + janela de observação |
| 7. Ingestão futura (S6–S10) | Todo chunk novo das coleções recém-criadas (`saneamento`, `energia`, `portos`, `aeroportos`, `barragens`) já nasce indexado direto em bge-m3 — não há dívida adicional para esses segmentos | contínuo, sem esforço extra além do já planejado no `docs/DEPLOY-v4.2.md` |
| 8. Descomissionamento | Remover a coluna 384-d e qualquer referência a bge-small no código/documentação após a janela de observação sem incidentes | 0,5 dia |

**Custo estimado:** desprezível em termos de compute/armazenamento
para o volume atual (204 chunks); o custo real é o esforço de
engenharia acima, aproximadamente **4–5 dias-pessoa** distribuídos em
uma janela de calendário de **1–2 semanas** (incluindo tempo de
aprovação MN e a janela de observação pós-corte antes de descomissionar
bge-small).

**Riscos e mitigação:**
- *Regressão de qualidade não detectada* → mitigado pela etapa 5
  (validação lado a lado antes do corte) e pela manutenção da coluna
  antiga durante a janela de observação.
- *Migração em produção sem aprovação* → bloqueado pelo gate humano
  MN (ver §6).
- *Divergência de schema real vs. assumido* (mesmo padrão de risco já
  visto na migração v4.2 — ver comentários em
  `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`) → mitigar
  rodando `list_tables`/`list_extensions` no Supabase antes de aplicar
  qualquer DDL, e testando em branch/staging do Supabase antes do
  `main`.

---

## 6. Decisão final

**Este documento é uma recomendação técnica, não uma decisão
executória.** Conforme o padrão de governança já em vigor neste
repositório (gate humano MN em merges e em migrações de produção — ver
`docs/DEPLOY-v4.2.md`), a escolha entre Opção A e Opção B, e a
autorização para executar o roadmap correspondente, requer:

- [ ] **Aprovação explícita de MN** sobre qual opção seguir (A ou B).
- [ ] Se B: aprovação para rodar a migração de schema no Supabase
  produção (`ogxxgvgtulrbbppshjie`), seguindo o mesmo processo de
  pré-checagem + `db push --dry-run` já documentado em
  `docs/DEPLOY-v4.2.md` §2.
- [ ] Se A: aprovação do ADR de reversão a ser registrado no
  `CLAUDE.md` master.

Até essa aprovação, **nenhuma alteração em produção deve ser
executada** a partir deste documento — ele serve para embasar a
decisão, não para autorizá-la.

---

## 7. Referências internas

- `CLAUDE.md` (raiz deste repo) — registro mestre dos agentes e das
  coleções RAG (`saneamento`, `energia`, `portos`, `aeroportos`,
  `barragens`), todas ainda sem embeddings.
- `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql` — migração
  candidata que criou as 5 coleções RAG novas, ainda pendente de
  aplicação em produção.
- `docs/DEPLOY-v4.2.md` — runbook de deploy v4.2, com o padrão de gate
  humano MN e pré-checagem de schema usado como referência de processo
  neste documento.
- `docs/COWORK-INTEGRATION.md` — descreve `get_maestro_rag_collections()`
  expondo as 9 coleções RAG (prefixos `rod:`/`oae:`/`fer:`/`mtr:`/
  `por:`/`aer:`/`san:`/`ene:`/`bar:`) cuja consulta vetorial depende
  diretamente da decisão deste documento.
- Skill `manta-maestro` — descreve o estado atual em produção como
  "RAG Supabase pgvector (BAAI/bge-small-en-v1.5 384d, projeto
  ogxxgvgtulrbbppshjie)", a referência usada nesta análise para o
  estado "como está" (Opção A).
