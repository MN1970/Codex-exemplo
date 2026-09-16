# Onde guardar apresentações e ativos binários do Manta Maestro

Pergunta recorrente: ao gerar/receber uma apresentação institucional (ex.:
`ABR_APR_INST_MANTA_Nova.pdf`, deck PptxGenJS de 24 slides, 4,3 MB, com a
logo da Manta Associados no cabeçalho de cada slide), onde ela deve viver
para ser reaproveitada pelo Manta Maestro e seu ecossistema — base64,
Supabase ou GitHub?

## Resposta curta

| Tipo de ativo | Onde | Por quê |
|---|---|---|
| Documento-fonte grande (apresentação completa, PDF de projeto, EVTEA) | **SharePoint** — `04_IA/01_APRESENTAÇÕES/` (já existe e já é usada) | É o sistema de arquivos oficial da Manta (`CLAUDE.md` já roteia documentos de projeto para lá); versiona nativamente, tem controle de acesso por usuário Microsoft 365, e não precisa de codificação alguma — upload direto do arquivo |
| Texto/conteúdo da apresentação, para busca semântica pelos agentes (RAG) | **Supabase** — tabelas `manta_rag_documents` / `manta_rag_chunks` do projeto `manta-maestro` (`ogxxgvgtulrbbppshjie`) | Essas tabelas existem exatamente pra isso: texto extraído + chunks + embeddings (bge-m3, 1024d), não os bytes do arquivo. O `storage.buckets` do Supabase está vazio — não há hoje um bucket de arquivos configurado no projeto |
| Ativo pequeno e reutilizado por código (logo, ícone) | **Este repositório GitHub**, versionado normalmente (`assets/branding/`) | É pequeno (dezenas de KB), muda raramente, e agentes/skills que geram artefatos (propostas, decks, dashboards) precisam referenciá-lo por caminho de arquivo, não por linha em banco |
| — | ~~Base64 em texto/CLAUDE.md/coluna de banco~~ | **Não usar como forma de guardar arquivo.** Base64 infla ~33% o tamanho, quebra diff binário, e — na prática desta sessão — só para subir a logo de 22 KB via chat foi preciso ~90 mil tokens de contexto. Para o PDF de 4,3 MB isso passaria de 1 milhão de tokens só na chamada da ferramenta. Base64 só faz sentido como *encoding de transporte* pontual (ex.: payload de uma API), nunca como local de armazenamento |

## O que foi feito nesta sessão

1. `Manta_Associados_Apresentacao_Institucional.pdf` (o arquivo enviado)
   foi enviado para o SharePoint em
   `Engenharia/04_IA/01_APRESENTAÇÕES/Manta_Associados_Apresentacao_Institucional.pdf`.
2. A logo da Manta foi extraída do PDF (imagem de cabeçalho presente em
   quase todos os slides, com máscara de transparência) e commitada neste
   repositório em `assets/branding/manta-logo.png`, para reuso direto por
   código/skills.
3. Uma cópia da logo também pode ser enviada para
   `Engenharia/04_IA/02_IMAGENS/` no SharePoint (pasta já existente para
   imagens) — ver observação abaixo sobre o método de upload.

## Observação técnica sobre o conector SharePoint

A ferramenta de upload do SharePoint (`SharePoint_Manta`) só aceita o
conteúdo do arquivo de duas formas: `local_path` (um caminho no *servidor*
do conector — não no ambiente desta sessão de agente) ou `content_b64`
(o arquivo inteiro codificado em base64, embutido na chamada). Como as
duas sessões não compartilham disco, qualquer upload feito por um agente
de chat precisa necessariamente passar por base64 — o que é aceitável para
um logo de ~22 KB, mas inviável em custo/confiabilidade para um PDF de
alguns MB. Para arquivos grandes, o caminho mais rápido e confiável é
upload direto pela interface web do SharePoint (arrastar e soltar).

## Se no futuro for necessário indexar o conteúdo da apresentação no RAG

O caminho correto **não** é subir o PDF em si para o Supabase, e sim rodar
o pipeline de ingestão já usado pela skill `manta-supabase-update` (ou
equivalente) para: extrair o texto/slides → chunkar → gerar embeddings
bge-m3 1024d → inserir em `manta_rag_documents` + `manta_rag_chunks`,
mantendo `source_url` apontando para o arquivo real no SharePoint. Isso
mantém uma única fonte de verdade binária (SharePoint) e um índice de
busca separado (Supabase), em vez de duplicar o binário em dois lugares.
