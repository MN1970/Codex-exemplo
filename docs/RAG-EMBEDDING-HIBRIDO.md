# RAG — Embedding Multilíngue + Busca Híbrida (proposta v4.3)

Este documento registra a análise e recomendação para evoluir o RAG do
Manta Maestro (5 coleções Supabase pgvector — `saneamento`, `energia`,
`portos`, `aeroportos`, `barragens`, criadas na v4.2), a partir de uma
discussão sobre RAG vs. CAG e sobre múltiplos usuários simultâneos
usando os agentes.

**Estado atual (conforme `manta-maestro` skill / `CLAUDE.md`)**:
embedding `BAAI/bge-small-en-v1.5` (384d), busca puramente vetorial,
sem coluna de versão/revisão por chunk.

---

## 1. Problemas identificados no desenho atual

### 1.1 Modelo de embedding é monolíngue em inglês

`bge-small-en-v1.5` é treinado majoritariamente em corpus em inglês. As
fontes das 5 coleções são quase 100% em português (NBR, SNIS, editais
BNDES/ANTAQ, Lei 14.026, resoluções ANEEL) ou espanhol (ERAS/AySA). Isso
degrada silenciosamente o recall — a busca retorna resultados, mas com
similaridade pior do que um modelo multilíngue entregaria para o mesmo
texto. Não há sintoma visível (não quebra), só perda de qualidade.

### 1.2 Busca só vetorial, sem componente textual

Embeddings generalizam bem semântica, mas são fracos para casar termos
exatos e alfanuméricos — código de norma (`NBR 12211`), número de lei
(`Lei 14.026/2020`), código de resolução ANEEL, sigla (`RAP`, `TSF`,
`CFRD`). Sem um componente de full-text (BM25/`tsvector`) combinado ao
vetorial, esses termos competem em pé de igualdade com texto semântico
solto e podem perder no ranqueamento.

### 1.3 Ausência de metadado de versão/revisão por chunk

Este é um problema que **já aconteceu neste próprio registro**: a seção
"MODELO MESTRE DE PROPOSTA" do `CLAUDE.md` documenta que a proposta
citada como fonte (`MNT-2026-COM-1183_D`) não foi localizada no
SharePoint — só a revisão `_C` existe. Um RAG sem metadado de
versão/data/status (vigente × superado) por chunk não teria como evitar
— nem detectar — que uma resposta cite uma revisão errada ou obsoleta de
um documento. Isso vale igualmente para revisões de normas, aditivos de
contrato e versões de edital.

### 1.4 Sem isolamento por usuário/segmento na busca

Com múltiplas pessoas usando os agentes, a busca vetorial hoje não filtra
por permissão antes do cálculo de similaridade — o roteamento por
palavra-chave do Maestro decide o agente, mas não há controle formal de
quem pode ver o quê dentro de uma coleção (ex.: dados sensíveis de um
cliente específico de saneamento vs. outro).

---

## 2. Recomendação

Não trocar RAG por CAG (ver discussão registrada nesta sessão) —
o CAG não resolve nenhum dos 4 problemas acima e piora o isolamento
multiusuário. Em vez disso, evoluir o RAG existente em 3 frentes:

### 2.1 Trocar o modelo de embedding para um multilíngue

Candidatos: `BAAI/bge-m3` (multilíngue, multi-granularidade, 1024d) ou
`intfloat/multilingual-e5-large` (1024d). Ambos superam `bge-small-en`
em benchmarks multilíngues (MIRACL/MTEB multilingual) para português.

**Custo real da troca**: não é só trocar o nome do modelo — a dimensão
do vetor muda de 384 para 1024, o que exige:
1. Alterar a coluna `embedding` (`vector(384)` → `vector(1024)`).
2. Recriar o índice `ivfflat` (não é possível fazer `ALTER` in-place).
3. **Re-embedar todo o conteúdo já indexado** nas 5 coleções — não é
   incremental, é reprocessamento completo.

Ou seja: é uma migração com janela de indisponibilidade parcial da busca
vetorial (a textual continua funcionando durante o reprocessamento, se a
busca híbrida do item 2.2 já estiver no ar).

### 2.2 Busca híbrida (vetorial + full-text)

Adicionar coluna `tsvector` (gerada, `GENERATED ALWAYS AS ... STORED`,
configuração `portuguese`) + índice GIN, e uma função de busca que
combina rank textual e similaridade vetorial (RRF — *Reciprocal Rank
Fusion* — ou soma ponderada simples). Ver migração candidata em
`supabase/migrations/2026_09_13_rag_busca_hibrida.sql`.

### 2.3 Metadado de versão/status por chunk

Adicionar `documento_revisao`, `documento_data`, `status_vigencia`
(`vigente` / `superado` / `rascunho`) a cada chunk, e por padrão excluir
`superado` da busca (a menos que explicitamente solicitado). Isso ataca
diretamente a causa raiz do caso `_C`/`_D` documentado no `CLAUDE.md`.

### 2.4 (Fora desta migração) Filtro de permissão pré-busca

Registrar como pendência separada — depende de como o Maestro
operacional modela usuário/cliente hoje, o que este repositório não
tem visibilidade (vive no repo operacional). Recomenda-se RLS
(*Row Level Security*) no Supabase por `cliente_id`/`segmento`, aplicado
**antes** do cálculo de similaridade, não depois.

---

## 3. O que este documento NÃO faz

Assim como a análise do modelo mestre de proposta (v4.2.1), este
documento é **registro e recomendação**, não aplicação. A migração
SQL anexa é candidata (mesma convenção de
`supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`): assume um
schema aproximado de `rag_chunks` que precisa ser conferido contra o
schema real do Supabase de produção antes de rodar — este repositório
não tem acesso de escrita a esse projeto Supabase nem confirmação do
schema exato da tabela `rag_chunks` (só sabemos, pelo `CLAUDE.md`
checklist v4.2, que ela existe e que as 5 coleções foram registradas
nela).

**Gate humano necessário antes de qualquer aplicação em produção**,
por dois motivos, não só um:
1. Convenção do repositório (toda mudança de schema/produção passa por
   aprovação MN).
2. Custo operacional real do re-embedding (item 2.1) — é uma decisão de
   negócio (janela de manutenção, custo de API de embedding), não só
   técnica.

---

## 4. Próximos passos sugeridos (ordem de execução)

1. Confirmar schema real de `rag_chunks` no Supabase de produção
   (colunas exatas, se já existe algum campo de metadado de versão).
2. Ajustar a migração candidata a esse schema real.
3. Aplicar busca híbrida + metadado de versão primeiro (não depende de
   re-embedding, ganho imediato de qualidade e de rastreabilidade).
4. Só depois, como projeto separado, planejar a janela de re-embedding
   para o modelo multilíngue (maior custo/risco).
5. Rodar os prompts de `tests/routing/prompts.md` novamente após cada
   etapa para confirmar que o routing do Maestro não regrediu.
