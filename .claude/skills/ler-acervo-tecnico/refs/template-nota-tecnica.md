# refs/template-nota-tecnica.md — ler-acervo-tecnico

Estrutura de saída para a Nota Técnica de briefing de acervo, extraída
e generalizada a partir de "Acervo Técnico do Ferroanel Norte — Projeto
Básico DERSA" (v1.0, 27/08/2026). Usar como esqueleto de seções — o
conteúdo de cada seção vem do inventário efetivamente levantado pelo
pipeline do `SKILL.md`; nunca preencher uma seção com dado não
confirmado no acervo.

## Capa

- Nome da consultoria / cabeçalho `padrao-manta`.
- Título: "Acervo Técnico de [Empreendimento] — [Origem do material]".
- Subtítulo: propósito do documento (ex. "Briefing de nivelamento da
  equipe para a reunião inicial com o Cliente").
- Metadados de capa: Cliente, Projeto, Fonte do material.
- KPIs de destaque (adaptar aos achados do acervo — ex. nº de pastas,
  volume total, nº de estruturas/obras, nº de disciplinas).

## 1. Objetivo desta nota

Uma a duas frases: nivelar a equipe sobre o que foi recebido, antes de
qual evento (reunião, entrega, decisão). Deixar explícito que **não** é
uma análise crítica de projeto — é um mapa do território; a avaliação
de suficiência técnica/normativa é etapa posterior de escopo a
acordar.

## 2. Procedência e natureza do material

- Contratante / Cliente original do material.
- Projetista / emitente.
- Instrumento contratual (edital, contrato, termo de cessão).
- Responsável técnico e verificação de conformidade, se identificáveis.
- Janela de emissão (datas mín./máx. observadas nos documentos).
- Documento índice-mestre, se existir (código/nome).
- **Ponto contratual relevante**: qualquer ressalva de propriedade/
  confidencialidade impressa nos documentos — sempre reportar, sempre
  como pendência para confirmar com o Cliente a base de cessão.

## 3. O empreendimento em síntese

- Descrição objetiva do empreendimento (o que é, onde, extensão/porte
  se identificável nos desenhos/relatórios).
- Camadas do objeto contratual (ex.: estudos → projeto básico →
  elementos por disciplina → plano de execução), se aplicável.
- Qualquer número de porte (extensão, capacidade) deve vir com a
  ressalva "a confirmar no documento X" quando inferido indiretamente
  (ex. por estaqueamento), nunca apresentado como dado firme sem fonte
  direta.

## 4. Chave de leitura: a codificação do acervo

- O template de codificação identificado (ver
  `refs/padrao-codificacao.md`), com a legenda de cada campo.
- Tabela de disciplinas identificadas → onde aparecem com mais peso.
- Um exemplo prático de "tradução" de um pedido comum da equipe em
  código + pasta.
- Se nenhum padrão foi identificável: dizer isso explicitamente e
  descrever como o acervo foi inventariado (por pasta/nome literal).

## 5. Conteúdo por disciplina

Tabela pasta → conteúdo essencial → volume, uma linha por
pasta/disciplina, replicando o inventário do Passo 3 do pipeline. Se o
acervo tiver uma pasta transversal de arquivos nativos (CAD/BIM/
planilhas), destacar separadamente por concentrar volume desproporcional.

## 6. Escopo físico que o acervo revela

Síntese cruzando desenhos/estruturas com memórias de quantidade/
orçamento, quando existirem — quantidade de obras, tipologias
padronizadas, soluções especiais identificadas, campanha de
investigação (geotécnica, ambiental, operacional) conforme o que o
acervo efetivamente contém. Omitir qualquer subseção para a qual não
haja material no acervo, em vez de preenchê-la com genérico.

## 7. Maturidade e histórico de revisões

- Linha do tempo do que foi emitido em cada janela de datas observada.
- Documentos com maior número de revisões — sinalizar como possível
  indicador de instabilidade de escopo/quantidade, sem afirmar
  causalidade.
- Notas de revisão do índice, se existirem e trouxerem informação sobre
  o que mudou.

## 8. Lacunas e pontos de atenção

Tabela `Achado` → `Implicação`, resultado do Passo 5 do pipeline.
Classificar cada achado com uma legenda consistente (ex.: Lacuna
crítica / Requer esclarecimento / Observação / Ponto favorável) e
manter isso visível no rodapé da seção.

## 9. Pauta proposta para a reunião

Tabela `Bloco` → `Pergunta a levar ao Cliente`, cobrindo no mínimo:
finalidade do uso do acervo, completude (existe revisão mais nova? há
documento faltante referenciado?), base de cessão/confidencialidade,
atualização de custos/data-base (se houver orçamento no acervo),
escopo pendente de definição, interfaces externas não incluídas no
acervo.

## Encaminhamentos internos sugeridos

- Lista curta de próximos passos operacionais da própria equipe (ex.:
  consolidar inventário rastreável em planilha — este skill já entrega
  isso automaticamente via `xlsx`; priorizar leitura de N documentos
  antes da reunião; confirmar integridade de arquivos nativos por
  amostragem).

## Ficha técnica do documento

Cliente · Projeto · Documento · Código Manta (a atribuir) · Versão ·
Data de criação · Elaboração · Classificação · Origem dos dados
(caminho SharePoint/OneDrive/local) · Documento-base · Última
modificação da fonte.
