---
name: ler-acervo-tecnico
manta_code: "a confirmar (skill transversal, sem código Manta dedicado)"
aliases: ["acervo-tecnico", "leitor-acervo", "briefing-acervo", "inventario-acervo"]
version: 1.0.0
updated: 2026-08-27
author: Manta Associados
origem: generalização do briefing "Acervo Técnico do Ferroanel Norte — EPL/DERSA" (v1.0, 27/08/2026)
description: >
  Skill transversal (Eixo 1, horizontal) para ler e inventariar qualquer
  acervo técnico recebido de um Cliente ou terceiro (estudos, projeto
  básico/executivo, memoriais, plantas, orçamento, cronograma), a partir
  de SharePoint, OneDrive ou diretório local — inclusive volumes
  combinados nas três fontes. Detecta o padrão de codificação de
  documentos do emissor (ex.: esquema DERSA
  TIPO-EMPREENDIMENTO.SUBTRECHO.OBRA-DISCIPLINA/SEQ_REV), monta um
  inventário rastreável por pasta/disciplina (código, tipo documental,
  disciplina, revisão, data, contagem de arquivos, volume), cruza com o
  índice-mestre quando existir, identifica lacunas (índices ausentes,
  saltos de numeração, revisões não recebidas, pastas vazias, prefixos
  duplicados, disciplinas sem amarração ao índice, volume incompatível
  com o esperado) e gera uma Nota Técnica de briefing no padrão Manta,
  mais uma planilha de inventário com uma aba por disciplina. Use SEMPRE
  que o usuário mencionar: acervo técnico, acervo recebido, material
  recebido do Cliente, ler estrutura de pastas de projeto, inventariar
  projeto recebido, briefing de acervo, nota técnica de acervo, chave de
  leitura de codificação, índice-mestre, ID de documentos, nivelamento
  de equipe sobre material recebido, "o que veio no material", "mapear o
  que recebemos", "descrever o acervo", ou similar — em qualquer
  segmento (rodovia, OAE, ferrovia, metrô, porto, aeroporto, saneamento,
  energia, barragem, imobiliário).
---

# LER-ACERVO-TECNICO — Skill Transversal (Eixo 1)

Generaliza, como skill reutilizável, o trabalho manual que originou a
Nota Técnica "Acervo Técnico do Ferroanel Norte — Projeto Básico DERSA"
(MRS, 27/08/2026): ler um volume de documentos entregue por um Cliente,
decifrar a lógica de organização/codificação do emissor, montar um mapa
do território (não uma crítica técnica) e levar à equipe — antes de
qualquer reunião ou proposta — o que existe, o que não existe e o que
precisa ser esclarecido.

## 1. PERGUNTA OBRIGATÓRIA INICIAL

```
┌──────────────────────────────────────────────────────────┐
│  LER-ACERVO-TECNICO — INTAKE                              │
│                                                            │
│  Q1: Onde estão os dados?                                 │
│      (a) SharePoint (Manta ou do Cliente)                 │
│      (b) OneDrive                                         │
│      (c) Diretório local (disco / pasta montada)           │
│      (d) Combinação de fontes (a+b+c)                      │
│                                                            │
│  Q2: Cliente / Projeto / Segmento?                          │
│      (nome do Cliente, nome do empreendimento, segmento    │
│      S1-S10 se aplicável — usa roteamento do CLAUDE.md)    │
│                                                            │
│  Q3: Finalidade do inventário?                              │
│      (A) Briefing de nivelamento interno (pré-reunião)     │
│      (B) Due diligence técnica                              │
│      (C) Base para orçamento de referência                  │
│      (D) Subsídio a modelagem de concessão                  │
│      (E) Simples localização de documento específico        │
│                                                            │
│  Q4: Profundidade da varredura?                              │
│      (a) Só estrutura de pastas + índice-mestre (rápido)   │
│      (b) Estrutura + amostragem de arquivos nativos          │
│          (DWG/XLSX/DOC) para checar integridade              │
│      (c) Varredura completa com leitura de conteúdo de       │
│          cada PDF/memorial (lento — só sob pedido explícito) │
└──────────────────────────────────────────────────────────┘
```

Sem Q1–Q4 respondidas (mesmo que por inferência clara do pedido do
usuário), não iniciar a varredura — o custo de tempo e de leitura de
material sob confidencialidade do Cliente é alto demais para adivinhar.

## 2. PIPELINE

### Passo 1 — Conectar e listar

- **SharePoint**: `mcp__Microsoft_365__sharepoint_folder_search` /
  `sharepoint_search` para localizar a pasta-raiz do acervo e listar
  subpastas e arquivos (nome, tamanho, data de modificação).
- **OneDrive**: mesma família de ferramentas Microsoft 365 (Graph API
  cobre SharePoint e OneDrive) — se o Cliente compartilhou por OneDrive
  pessoal/empresarial, localizar via busca por nome de arquivo/pasta.
- **Diretório local**: `Bash` (`find`, `du -sh`, `ls -la`) e `Glob` para
  levantar a árvore de pastas, contagem de arquivos e volume por pasta.
- **Google Drive** (se aplicável): `mcp__Google_Drive__search_files` /
  `list_recent_files`.
- Combinação de fontes (Q1=d): listar cada fonte separadamente e
  **deduplicar** por nome de arquivo + código de documento antes de
  montar o inventário único — não somar volume de cópias.

### Passo 2 — Detectar o padrão de codificação do emissor

Ver `refs/padrao-codificacao.md` para o método de detecção e para o
caso de referência (esquema DERSA). Resumo do método:

1. Amostrar ~30 nomes de arquivo/pasta espalhados pelo acervo.
2. Testar contra um template genérico:
   `TIPO – EMPREENDIMENTO . SUBTRECHO . OBRA – DISCIPLINA / SEQUENCIAL _ REVISÃO`
3. Se não casar, procurar um índice-mestre (arquivo tipo "ID-", "índice",
   "index", "relação de documentos") que costuma trazer a legenda da
   codificação — ler esse documento primeiro sempre que existir.
4. Se nenhum padrão for identificável, **não inventar um esquema** —
   registrar no relatório que a codificação não pôde ser decifrada e
   inventariar por pasta/nome literal.
5. Montar a tabela de disciplinas identificadas (código → disciplina →
   onde aparece com mais peso), no mesmo formato da seção 4 do template.

### Passo 3 — Montar o inventário estruturado

Uma linha por documento (ou por lote homogêneo, quando o volume for
muito grande) com colunas: `pasta`, `código`, `tipo documental`,
`disciplina`, `descrição curta`, `revisão`, `data`, `nº de arquivos`,
`volume (MB)`, `fonte (SP/OneDrive/local)`. Agregar por pasta/disciplina
para a tabela-resumo (equivalente à seção 5 do template — "conteúdo
essencial" + "volume" por pasta).

### Passo 4 — Cruzar com o índice-mestre (quando existir)

Se houver um índice/relação de documentos, usá-lo como fonte de verdade
para o que **deveria** existir, e comparar item a item com o que foi
efetivamente encontrado nas pastas. Toda divergência vira um item da
seção de lacunas — nunca ficar só na leitura das pastas quando um índice
está disponível.

### Passo 5 — Detectar anomalias e lacunas

Checklist mínimo (replicável para qualquer acervo, generalizado a partir
do caso Ferroanel):

- Documento(s) referenciado(s) no índice mas ausente(s) do acervo.
- Revisão do índice mais antiga que a revisão citada dentro do próprio
  índice (ex.: índice está em Rev. B mas registra existência de Rev. C).
- Saltos na numeração de itens do índice ou de pastas (ex.: pula de 06
  para 08, ou de item 5 para item 7).
- Prefixos/números de pasta duplicados.
- Pastas vazias.
- Disciplinas com volume incompatível com o esperado para o porte do
  empreendimento (ex.: poucos MB para uma disciplina que tipicamente
  gera dezenas/centenas de MB nesse tipo de projeto).
- Disciplinas presentes nos arquivos nativos mas não amarradas a nenhum
  item do índice.
- Revisões mais altas concentradas em poucos documentos — sinal de
  instabilidade de escopo/quantidade nesse item (ver seção "Maturidade"
  do template) — vale destacar como possível indicador de risco de
  custo, sem afirmar causalidade.
- Ressalva de confidencialidade/propriedade impressa nos documentos —
  sempre reportar, nunca ignorar.

### Passo 6 — Gerar os entregáveis

1. **Nota Técnica de briefing** — usar `refs/template-nota-tecnica.md`
   como estrutura (capa, procedência/contrato, chave de leitura da
   codificação, conteúdo por disciplina, escopo físico revelado,
   maturidade e histórico de revisões, lacunas e pontos de atenção,
   pauta proposta de reunião, ficha técnica). Gerar via skill `docx` ou
   `pdf` conforme o formato pedido, aplicando `padrao-manta` para a
   identidade visual.
2. **Planilha de inventário** (melhoria em relação ao processo manual
   original) — via skill `xlsx`, uma aba por disciplina/pasta, com as
   colunas do Passo 3, mais uma aba "Lacunas" e uma aba "Resumo". Este
   entregável opera diretamente o encaminhamento que a própria Nota
   Técnica do Ferroanel recomendava como próximo passo: "consolidar um
   inventário rastreável em planilha — uma aba por disciplina".

## 3. REGRAS

1. Sempre perguntar Q1–Q4 antes de iniciar a varredura.
2. **Nunca inventar** código, disciplina, data ou volume que não pôde
   ser lido — marcar explicitamente como "a confirmar".
3. Reportar **sempre** qualquer ressalva de confidencialidade/
   propriedade impressa no material, e não presumir base de cessão —
   isso é pergunta para o Cliente, não dado a assumir.
4. Este skill produz um **mapa do território**, não uma avaliação de
   suficiência técnica ou de aderência normativa — isso é etapa
   posterior e deve ficar explícito no entregável.
5. `aluci-guard` antes de fechar a Nota Técnica — nenhuma norma, lei ou
   código citado pode ser inventado.
6. `consist-guard` — números de páginas/pastas/documentos citados no
   texto batem com o inventário efetivamente levantado.
7. Ao combinar múltiplas fontes (Q1=d), deduplicar antes de somar
   volumes — nunca reportar volume duplicado como se fosse conteúdo
   adicional.
8. Se o acervo for muito grande para varredura completa em uma sessão,
   dizer isso explicitamente e propor amostragem — nunca reportar
   cobertura total quando a varredura foi parcial.

## 4. INTEGRAÇÕES MANTA

- `padrao-manta` — identidade visual do entregável.
- `aluci-guard`, `consist-guard` — auditoria antes de fechar.
- `docx`, `pdf`, `xlsx` — geração dos entregáveis finais.
- `autodesk-toolkit` — quando Q4 incluir amostragem de nativos CAD/BIM
  (DWG, DXF, IFC, RVT) para checar integridade sem precisar do software
  original.
- `cad-quantifier` — se o objetivo (Q3) for orçamento de referência e o
  Cliente pedir quantitativos a partir do acervo recebido.
- `manta-context` — contexto institucional Manta ao redigir o
  documento (cabeçalho, ficha técnica, classificação).
- `manta-maestro` (roteamento) — usar as regras de routing do
  `CLAUDE.md` para sinalizar, ao final do briefing, para qual agente
  vertical (S1–S10) o conteúdo do acervo deveria ser encaminhado na
  sequência.

## 5. HANDOFF PARA AGENTES VERTICAIS

Ao final da varredura, aplicar as regras de routing do `CLAUDE.md`
(seção ROUTING — Maestro) sobre as disciplinas/palavras-chave
encontradas no acervo e sugerir o(s) agente(s) vertical(is)
correspondente(s) para a etapa seguinte (ex.: acervo ferroviário →
`agente-infraestrutura S3`; acervo portuário → `agente-portos`; acervo
de saneamento → `agente-saneamento`). O handoff é uma **sugestão** ao
final do briefing — este skill não aciona o agente vertical
automaticamente.

## 6. O QUE ESTE SKILL NÃO FAZ

- Não avalia suficiência técnica do projeto nem aderência a normas —
  isso é etapa posterior, com escopo a acordar com o Cliente.
- Não decide a base de cessão/circulação de material sob
  confidencialidade — isso é pergunta para o Cliente.
- Não abre, converte ou distribui arquivos protegidos sem confirmação
  prévia de autorização.
- Não substitui a leitura de conteúdo técnico por um especialista de
  disciplina quando a finalidade (Q3) exigir isso — nesse caso, faz o
  handoff para o agente vertical correspondente.

## 7. METADADOS

```
Skill: ler-acervo-tecnico
Versão: 1.0.0
Criada: 2026-08-27
Eixo: 1 — Horizontal / transversal (utilitário)
Origem: generalização da Nota Técnica "Acervo Ferroanel Norte — EPL/DERSA" v1.0
Fontes suportadas: SharePoint, OneDrive, diretório local, Google Drive
Entregáveis: Nota Técnica (docx/pdf) + planilha de inventário (xlsx, 1 aba/disciplina)
Classificação: Interno — Manta Associados
```
