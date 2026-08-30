# Padrão de output — cliente Motiva

Referência canônica de como a Manta estrutura entregáveis para a
**Motiva Infraestrutura de Mobilidade** (ex-CCR Rodovias), levantada a
partir do SharePoint da Manta (site `Engenharia`) — projeto **SP-258**
(Duplicação Capão Bonito–Itararé/Itapeva, contrato 4600087479) e
projetos correlatos (SP-330, Rota Mogiana, PR-Vias Contorno Apucarana,
Lote 3/PR, Morro dos Cavalos BR-101/SC, Consultoria Geotecnia/Túneis).

Todo agente vertical (Manta 03-S1..S10) que produzir output para a
Motiva **deve seguir este padrão** nos formatos Excel, PowerPoint e
relatório, e usar a norma de codificação de documentos do cliente.

Última varredura: 2026-08-30. Ver seção "Fontes" para os caminhos
exatos consultados.

**Templates implementados** (aprovado por MN, 2026-08-30) — reproduzem
a estrutura documentada abaixo e ficam disponíveis para uso direto pelos
agentes verticais:

- [`templates/EAP-PADRAO-MOTIVA.xlsx`](templates/EAP-PADRAO-MOTIVA.xlsx) — capa
  com bloco de cabeçalho/legenda + aba EAP com cabeçalho, hierarquia de
  4 níveis e fórmulas de custo/preço (ver seção 1).
- [`templates/PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx`](templates/PLANEJAMENTO-GERENCIAL-PADRAO-MOTIVA.pptx) —
  capa, sumário de seções e slide-modelo de conteúdo com o rodapé
  padrão (ver seção 2).

Cores institucionais da Motiva continuam **não confirmadas** (seção 5)
— os dois templates usam uma paleta neutra em escala de cinza (padrão
Manta) até a marca oficial ser confirmada pelo cliente; a nota está
registrada no gerador de cada arquivo e nas notas do orador da capa do
PPTX.

---

## 1. EAP — formato Excel

Todos os arquivos de EAP do lote SP-258 seguem o mesmo template
controlado: **EAP PADRÃO NEGÓCIOS EXISTENTES — OBRAS DE AMPLIAÇÃO
(EDIFICAÇÕES) v8**, reaproveitado entre disciplinas e entre contratos
Motiva/CCR.

Versões por disciplina encontradas em
`01.44.04 - SP_VIAS (Quantidades SP_258)/02 - Material Recebido/SP_258 - Lote 01 - 090126/`:

- `EAP - GERAL.xlsx`
- `EAP - TERRAPLENAGEM.xlsx` (`03.TE/`)
- `EAP - DRENAGEM.xlsx` (`04.DR/`, também em `25_SP-258_FEL 03/.../04.DR`)
- `EAP - ILUMINAÇÃO.xlsx` (`09.EL/`)
- `EAP - INTERFERÊNCIAS.xlsx` (`11.IN/`)

### Bloco de cabeçalho (linhas 1–24)

Campos fixos: Projeto · PEP · Modal · UF · Município · Código do
empreendimento (`SP0-258`) · Fase de orçamentação · Revisão ·
Data-base.

Legenda (linhas 18–19, idêntica nos 4 arquivos lidos):

```text
LEGENDA:    CÉLULAS COM PREENCHIMENTO AUTOMÁTICO
            CÉLULAS PARA PREENCHIMENTO MANUAL
```

**A legenda não cita cor nenhuma** — distingue as duas categorias só
por texto. No Excel original elas certamente são diferenciadas por cor
de fundo, mas essa cor **não é recuperável via SharePoint/Graph**: a
leitura via MCP extrai apenas valores de célula e fórmulas (texto
puro), não o XML de estilo (`styles.xml`/`theme1.xml`) onde o Excel
guarda fill, fonte e formatação condicional. Para obter a cor real:
baixar o `.xlsx` (OneDrive/SharePoint → "Baixar uma cópia") e ler com
algo que exponha OOXML de estilo — ex. `openpyxl`
(`cell.fill.fgColor.rgb`) — ou abrir no Excel/LibreOffice.

### Colunas da tabela de itens

`NÍVEL | ITEM | FONTE (Tab. pública) | CÓD. (Tab. pública) | GRUPO | SUB-GRUPO | CÓD. INTERNO | DESCRIÇÃO | UND | QUANT. TOTAL | CUSTO UNITÁRIO | CUSTO TOTAL | BDI | PREÇO UNITÁRIO | PREÇO TOTAL | %`
— bloco repetido para um segundo cenário — seguido de
`LOTES CONTRATAÇÃO | REIDI | FATURAM. DIRETO | GRUPO MERCADORIAS | CLASSE CUSTO | FUNCIONAL | ANTEPROJETO | EXECUTIVO`.

### Hierarquia — 4 níveis

| Nível | Papel | Exemplo |
|---|---|---|
| N1 | Macro-disciplina | VIÁRIO, OAE, DRENAGEM |
| N2 | Grupo | `DE` (Demolições), `RE` (Reformas), `IM` (Implantação)… |
| N3 | Sub-grupo | recorte funcional dentro do grupo |
| N4 | Item / composição | código de tabela pública, ex. `E1005`, `D3246` |

Código interno = `[empreendimento]-[disciplina]-[grupo]-[sub-grupo]`,
ex. `SP0-258-VIÁRIO-DE-DEDF`.

---

## 2. EAP — formato PowerPoint

**Não existe** um slide de EAP isolado em formato de organograma
hierárquico nas pastas varridas. A EAP alimenta o PPT de planejamento
gerencial mas não vira um slide próprio (confirmado em apresentação
Motiva BR-101/SC — Morro dos Cavalos, gerada via pptxgenjs, que cita
explicitamente a distribuição dos "quantitativos da EAP" entre
trechos).

Padrão visual identificado nesse deck:

- Capa: título em versalete espaçado (`P L A N E J A M E N T O
  G E R E N C I A L`), campos **Cliente / Elaboração / Status**.
- Rodapé fixo em todos os slides:
  `[Rodovia] · [Segmento] · MOTIVA · [Título da seção] · nº/total`
- Sequência de seções: 01 Visão geral · 02 Frentes de trabalho ·
  03 Diagrama tempo-caminho · 04 Matriz de fatores · 05 Curva S.

---

## 3. Relatório — Caderno de Premissas (FEL-1)

Template usado em múltiplos dispositivos Motiva (ex.: SP-330
Anhanguera km 78/82). Estrutura fixa de 8 capítulos:

1. Introdução e finalidade do documento
2. Descrição sumária do projeto (2.1 localização; 2.2 tipologia
   conceitual do dispositivo)
3. Nível de contingências — custos diretos/indiretos/BDI, normas
   SICRO, metodologia FEL
4. Identificação de ramos e OAEs
5. Premissas de planejamento e cronograma — **5.3 Gantt, EAP e
   calendário** (5.3.1 Estrutura Analítica do Projeto)
6. Metodologia de orçamento — paramétrico FEL-1, base de
   quantificação, CAPEX preliminar
7. Análise por tipologia — preliminares, terraplenagem, pavimentação,
   OAE, drenagem, iluminação, sinalização, paisagismo, desvios de
   tráfego
8. Anexos — planilha orçamentária, composições unitárias, Gantt,
   documentação recebida

---

## 4. Codificação de documentos (norma do cliente)

Norma **"Normas de Codificações de Documentos CCR Rodovias"** — código
`EN-SP000_00-0000.00-GER-A1-GR_PO.C-201-R43`, vigência 09/2022,
revisão 43 (pasta `01.58 - MOTIVA (Consultoria Geotecnia e Anteprojeto
Túneis)/01.58.01/Anexo 05`). Rege todo documento técnico gerado para a
Motiva, em 3 níveis:

| Nível | Conteúdo |
|---|---|
| N1 | Concessionária — sigla de 2 letras |
| N2 | Rodovia + UF · km · tipo de obra · intervenção · classe do projeto |
| N3 | Tipo de documento · fase · sequencial · revisão |

Exemplos observados:

```text
MD-SP0000258-226.255-620-L09/101
RS-BR000/00-0000.00-PRT-A1-GR/IT.C-201
```

Único template de carimbo recebido do cliente: `Anexo 11 - Modelos
Carimbo-Relatórios` (01.58.01) — carimbo de prancha CAD (.dwg) e de
relatório (.docx), só com campos de metadado (código, revisão,
responsável técnico/CREA), sem cor especificada.

---

## 5. Cores oficiais da Motiva — LACUNA CONFIRMADA

Duas varreduras dedicadas não encontraram manual de marca, brandbook
ou código de cor (hex/RGB/CMYK/Pantone) da Motiva:

1. Busca geral por "manual de marca", "identidade visual",
   "brandbook", "logotipo", "paleta de cores", "cores oficiais" —
   nenhum resultado.
2. Busca dedicada às pastas **"Material Recebido"** de 10 projetos
   Motiva/CCR (01.20, 01.37, 01.44, 01.52, 01.53, 01.58, 01.59, 01.67
   e as pastas correspondentes em `02_CLIENTE/15_CCR`) — nenhuma
   continha brandbook ou código de cor.

O que o cliente de fato envia, repetido em quase todo processo de
concorrência, é um pacote-padrão de anexos de edital (Regras de Ouro,
Termo de Referência, Diretrizes de Qualidade, Instruções de Projeto
ENGELOG). Dois arquivos poderiam conter referência cromática mas não
foram lidos como texto (sem OCR nesta varredura):

- `Anexo — Padrão de Uniformes.pdf` (~1,75 MB, repetido em 4+
  projetos) — provável cor institucional em foto.
- `Manual de Sinalização Temporária CCR Rodovias 2024.pdf` (~120 MB) —
  cores normativas de placa de obra (padrão CONTRAN), **não** de
  identidade de marca.

**Recomendação:** (1) abrir visualmente o PDF de Padrão de Uniformes;
(2) solicitar o manual de marca diretamente à Motiva, ou perguntar a
Daniel Picchi Junior se guarda esse material fora do SharePoint. Até
lá, nenhum agente deve inventar ou assumir uma cor institucional da
Motiva — usar sempre o padrão visual neutro da Manta (`padrao-manta`)
em qualquer entregável até a cor oficial ser confirmada.

---

## Fontes (SharePoint · site Engenharia)

```text
Documentos Compartilhados/Projeto 01/01.37 - MOTIVA (SP Vias - Duplicação SP_258)
Documentos Compartilhados/Projeto 01/01.44 - MOTIVA (Concessionárias 11)/01.44.04
Documentos Compartilhados/Projeto 01/01.52 - CSA (Adequação OAE's - MOTIVA)
Documentos Compartilhados/Projeto 01/01.53 - MOTIVA (Rota Mogiana)
Documentos Compartilhados/Projeto 01/01.58 - MOTIVA (Consultoria Geotecnia e Anteprojeto Túneis)
Documentos Compartilhados/Projeto 01/01.59 - MOTIVA (Projeto IA)
Documentos Compartilhados/Projeto 01/01.67 - MOTIVA (Lote 3_PR)
01_BIBLIOTECA/04_BACKUP/Daniel Picchi Junior/01.20 - MOTIVA (PR Vias - Contorno Apucarana)
02_CLIENTE/15_CCR/15_SP330/03_MAT_ELAB/02_Caderno de Premissas
02_CLIENTE/15_CCR/17_LEVANTAMENTO_QUANTITATIVO_SP_258
02_CLIENTE/15_CCR/21_MDCavalos Planejamento/03_MAT_ELAB/05_APRESENTACAO
02_CLIENTE/15_CCR/25_SP-258_FEL 03
02_CLIENTE/15_CCR/02_PR_LOTE_3/02_MATERIAL_RECEBIDO
```

Relatório visual completo (dossiê HTML) publicado como Artifact durante
o levantamento — ver histórico da sessão que gerou este documento.
