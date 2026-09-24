# RAG — Busca Híbrida + Metadado de Versão (proposta v5.4.7)

Este documento registra a análise e recomendação para evoluir o RAG do
Manta Maestro (9 coleções Supabase pgvector confirmadas por auditoria
real — ver `docs/SUPABASE-PROJECT-AUDIT.md` — nas tabelas
`manta_rag_chunks`/`manta_rag_documents`), a partir de uma discussão
sobre RAG vs. CAG e sobre uso simultâneo dos agentes por múltiplas
pessoas.

> ⚠️ **Nota de correção desta própria análise, antes de publicar**: a
> primeira versão deste documento recomendava trocar o embedder de
> produção (`bge-small-en-v1.5`) por um modelo multilíngue (`bge-m3`
> ou `intfloat/multilingual-e5-large`), com o argumento de que o corpus
> é majoritariamente em português/espanhol e o modelo em produção é
> monolíngue em inglês. Esse argumento é razoável em abstrato — mas,
> ao verificar a seção "RAG — Coleções em Supabase" deste mesmo
> `CLAUDE.md`, descobrimos que **essa exata troca (`bge-m3`) já foi
> avaliada em 24/07/2026 e formalmente rejeitada em 26/07/2026** (gap
> G010), com um motivo concreto: reprocessamento completo dos chunks
> existentes sem ganho comprovado de qualidade de retrieval. Ver
> `docs/EMBEDDER-DECISION.md` para a análise completa (que também
> chegou à recomendação de migrar, e também foi corrigida com a mesma
> nota, ao se confirmar a decisão real). Reabrir essa decisão de novo,
> aqui, sem nenhum argumento técnico novo além do que já foi pesado em
> julho, seria repetir uma análise já feita — por isso a recomendação
> de troca de embedder foi **removida** deste documento antes de
> publicá-lo. Se surgir evidência nova de qualidade de retrieval que
> justifique reabrir o G010, isso deveria ser um documento à parte que
> cite essa evidência, não uma reafirmação do argumento de cobertura
> de idioma já conhecido e já pesado contra o custo.

O que resta abaixo são as duas frentes que **não dependem do embedder**
e que, até onde este repositório consegue confirmar, não foram
propostas nem decididas antes.

---

## 1. Problemas identificados no desenho atual

### 1.1 Busca só vetorial, sem componente textual

Embeddings generalizam bem semântica, mas são fracos para casar termos
exatos e alfanuméricos — código de norma (`NBR 12211`), número de lei
(`Lei 14.026/2020`), código de resolução ANEEL, sigla (`RAP`, `TSF`,
`CFRD`). Sem um componente de full-text (BM25/`tsvector`) combinado ao
vetorial, esses termos competem em pé de igualdade com texto semântico
solto e podem perder no ranqueamento. Isso vale independente de qual
embedder está em uso — não é argumento para trocar o modelo, é
argumento para adicionar uma segunda via de busca em paralelo.

### 1.2 Ausência de metadado de versão/vigência por chunk

Este repositório tem um histórico real e documentado de **citação
fabricada** de revisão de documento: a seção "Modelo Mestre de
Proposta" registra que `MNT-2026-COM-1183_D` foi citada como fonte em
uma análise anterior deste mesmo repositório e **nunca existiu** — só
a revisão `_C` é real. Isso foi uma alucinação de conteúdo (território
do `aluci-guard`, não do RAG em si) — metadado de versão por chunk não
teria impedido a fabricação de acontecer. O que ele teria feito, se já
existisse: (a) dar ao RAG uma forma de nunca *retornar* uma citação de
revisão que não está de fato indexada — hoje, se um chunk cita uma
revisão desatualizada de um documento real, o RAG não tem como saber
disso e sinalizar; (b) permitir excluir da busca, por padrão, conteúdo
já marcado como `superado` quando uma revisão nova é indexada por
cima. É uma mitigação parcial e complementar ao `aluci-guard`, não um
substituto dele.

### 1.3 Sem isolamento por usuário/segmento na busca

Com múltiplas pessoas usando os agentes, a busca vetorial hoje não
filtra por permissão antes do cálculo de similaridade. Isto já é um
gap rastreado neste repositório, independente desta proposta: RLS está
desabilitado em `rag_collections`, `sp_agent_routing` e
`maestro_routing_keywords` (ver `CLAUDE.md`, seção "Gaps abertos",
achado de segurança da auditoria G012 — SQL de remediação já redigido
lá, ainda não aplicado). Este documento não duplica esse item; só
registra que, quando a remediação de RLS for aplicada, o filtro de
permissão deveria valer também para a nova função de busca híbrida
proposta abaixo (§2.1), não só para o acesso direto às tabelas.

---

## 2. Recomendação

Não trocar RAG por CAG (ver discussão registrada nesta sessão) — o CAG
não resolve nenhum dos problemas acima e piora o isolamento
multiusuário (todo mundo compartilharia o mesmo cache de contexto
pré-carregado). Evoluir o RAG existente em 2 frentes, sem tocar no
embedder:

### 2.1 Busca híbrida (vetorial + full-text)

Adicionar coluna `tsvector` (gerada, `GENERATED ALWAYS AS ... STORED`,
configuração `portuguese`) + índice GIN em `manta_rag_chunks`, e uma
função de busca que combina rank textual e similaridade vetorial via
Reciprocal Rank Fusion (RRF). Ver migração candidata em
`supabase/migrations/2026_09_13_rag_busca_hibrida.sql`. Não altera a
coluna de embedding nem sua dimensão — compatível com qualquer
resultado que a reconciliação de specs do gap G016/G010 confirmar.

### 2.2 Metadado de versão/status por chunk

Adicionar `documento_revisao`, `documento_data`, `status_vigencia`
(`vigente` / `superado` / `rascunho`) a cada chunk, e por padrão
excluir `superado` da busca (a menos que explicitamente solicitado).

---

## 3. O que este documento NÃO faz

Este documento é **registro e recomendação**, não aplicação — mesma
convenção usada para o addendum de proposta (v5.4.1 em diante) e para
o gap G010: a migração SQL anexa é candidata, assume um schema
aproximado de `manta_rag_chunks` (baseado no que
`docs/SUPABASE-PROJECT-AUDIT.md` e `docs/EMBEDDER-DECISION.md`
documentam sobre ela) que precisa ser conferido contra o schema real
antes de rodar — este repositório não tem acesso de escrita a esse
projeto Supabase.

**Gate humano necessário antes de qualquer aplicação em produção**,
pela mesma convenção já estabelecida neste repositório para qualquer
mudança de schema/produção.

---

## 4. Próximos passos sugeridos (ordem de execução)

1. Confirmar schema real de `manta_rag_chunks` no Supabase de produção
   (colunas exatas, se já existe algum campo de metadado de versão).
2. Ajustar a migração candidata a esse schema real.
3. Aplicar busca híbrida + metadado de versão, idealmente na mesma
   janela em que a remediação de RLS (gap já pendente) for aplicada,
   já que tocam as mesmas tabelas.
4. Rodar os prompts de `tests/routing/prompts.md` novamente após a
   mudança para confirmar que o routing do Maestro não regrediu.
