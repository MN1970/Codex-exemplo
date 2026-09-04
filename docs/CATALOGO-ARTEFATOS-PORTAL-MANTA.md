# Catálogo de Artefatos-Modelo — Portais Manta

Registro dos artefatos reais (React/HTML) de portais já produzidos pela
Manta, encontrados no OneDrive/SharePoint pessoal de Maurício Neves
(`Documents/Claude/Artifacts/`), e o protocolo a seguir **antes de criar um
novo portal**: consultar este catálogo, escolher o padrão mais aplicável e
levantar as perguntas de triagem da Seção 3 com o usuário.

**Limitação de acesso:** os arquivos `.jsx` são servidos pelo SharePoint como
`application/octet-stream` e a ferramenta de leitura disponível nesta sessão
não lê esse tipo MIME — não foi possível abrir o código-fonte. Este catálogo
foi montado a partir de nomes de arquivo, datas de modificação, 2 capturas de
tela reais anexadas às pastas de versão, e cruzamento com a arquitetura
documentada na skill `manta-maestro`. Ele deve ser tratado como **v1 —
inventário por metadado**, não como leitura de código. Um próximo passo
natural é reexportar os `.jsx` como `.txt`/`.md` (ou liberar um conector com
download bruto) para produzir um catálogo v2 com estrutura de componentes
real.

---

## 1. Artefatos encontrados

### Família A — "Portal Manta" (orçamentação/dashboard geral)

| Arquivo | Modificado em |
|---|---|
| Portal_Manta_v8.jsx | 2026-04-01 |
| portal_manta_v19.jsx | 2026-05-09 |
| portal_manta_v22.jsx | 2026-05-09 |
| portal_manta_v22.1.jsx | 2026-05-10 |
| portal_manta_v25.jsx | 2026-05-10 |
| portal_manta_v28_7_1.jsx | 2026-05-10 |
| **portal_manta_v28_9.jsx** (mais recente) | 2026-05-11 |

**Evidência visual** (captura de tela anexada à v22.1): navbar escura com
logo "M", título "MANTA · Portal Orçamentação", seletor de contexto
("Lote 3 / Lote 4 / Lote 5"), ações "Imprimir/PDF", "Tela cheia", "Dados
(JSON)"; abaixo, navegação horizontal por abas (0 Capa, 1 Orçamento Manta,
2 Indiretos & Canteiro, 3 Insumos·Curva ABC, 4 Transporte...); capa com
logo, título, KPIs (versão, data de geração, data-base do MEF, valor total
agregado) e cards comparativos por lote (ampliação, CAPEX total,
extensão/OAEs).

Iteração muito ativa: 7 revisões catalogadas em ~40 dias — é o produto mais
maduro da família.

### Família B — "Portal Manta Lotes" (comparação multi-lote/EPC)

`portal_manta_lotes_pr_v2.jsx` até `_v9.jsx` (9 revisões, 2026-04-24 a
2026-05-04) + pasta de projeto `portal-manta-lotes-pr-v9/` (com subpasta
`versions/` e thumbnail).

**Evidência visual** (thumbnail da pasta v9): sidebar vertical escura —
"PORTAL MANTA · Índice geral" — com grupos numerados: **Introdução**
(1 Sumário, 2 Guia, 3 Glossário), **Análise por Lote** (4 Lote 3 · BR-376,
5 Lote 4 · PR-323, 6 Lote 5 · BR-369), **Ferramentas** (7 KB Curada,
8 Novo Orçamento, 9 KPIs Globais).

Aparenta ser a mesma linhagem de produto da Família A aplicada ao caso real
"Lotes 3/4/5 — Concessões Rodoviárias do Paraná/ANTT" — possivelmente A e B
convergiram (nomenclatura `lotes_pr` antecede `portal_manta_v19+` em parte
do período, mas há sobreposição de datas que não permite confirmar sem ler
o código).

### Família C — "Portal Manta Unificado"

`Portal_Manta_Unificado.jsx` (2026-03-22 — o mais antigo do inventário).

Corresponde à skill `manta-portal-unificado:portal-unificado` já registrada
na arquitetura do Manta Maestro: back-end MySQL de 27 tabelas, API REST
Node.js + React, integrando 4 domínios (SICRO+, Rodovias, Metrô L5,
Tocantins).

### Pastas de projeto multi-arquivo

`portal-manta-pr-v22-2/` e `portal-manta-lotes-pr-v9/` — indicam que, a
partir de certa versão, o artefato deixou de ser um único `.jsx` e passou a
ser entregue como projeto (múltiplos arquivos + `versions/` + thumbnail) —
padrão a preservar em novos portais que cresçam além de um único arquivo.

---

## 2. Padrões identificados (para reuso)

| Padrão | Quando usar | Modelo de referência |
|---|---|---|
| **Orçamentação Paramétrica** (capa + KPIs + comparação por frente/lote + curva ABC por módulo) | Comparar 2–4 frentes/lotes/cenários de CAPEX ou OPEX; suporte a decisão de lance ou divisão de lotes entre EPCistas | Família A/B — replicado no artefato-modelo funcional publicado nesta sessão: `templates/portal-manta-modelo-padrao/index.html` |
| **Dashboard Executivo multi-módulo** (assistente IA, Gantt multi-cenário, CAPEX/OPEX controller, consulta pública) | Gestão contínua de um empreendimento inteiro, não uma decisão pontual — 10+ módulos, uso ao longo de meses | Descrito na Parte III do MNT-2026-COM-1183_D (Portal Manta — Dashboard Executivo); ainda sem artefato-modelo funcional construído |
| **Unificado multi-domínio** (várias verticais na mesma base) | Cliente ou uso interno que precisa cruzar mais de um domínio de dados (ex.: rodovia + metrô + SICRO) na mesma tela | Família C — `Portal_Manta_Unificado.jsx` |

## 3. Protocolo — antes de criar um novo portal

**Passo 1.** Consultar este catálogo e classificar o pedido em um dos 3
padrões da Seção 2 (ou registrar um 4º padrão, se nenhum servir).

**Passo 2.** Fazer estas perguntas de triagem ao usuário antes de começar a
construir:

1. **Domínio do projeto** — rodovia/concessão, mineração, saneamento,
   energia, portos, barragens, aeroportos? (define o agente vertical S1–S11
   e o vocabulário técnico a usar nos módulos)
2. **Natureza do output** — é uma análise pontual para apoiar uma decisão
   (ex.: comparar lotes antes do lance) ou um painel de gestão contínua ao
   longo do contrato? → escolhe entre padrão "Orçamentação Paramétrica" e
   "Dashboard Executivo".
3. **Quantas frentes/lotes/cenários** precisam ser comparados lado a lado?
   (2–4 cabe em grade; mais que isso pede rolagem horizontal ou tabela)
4. **Múltiplos domínios na mesma tela?** Se sim, considerar o padrão
   "Unificado" em vez de duplicar o "Orçamentação Paramétrica" por domínio.
5. **Dados reais disponíveis** (MEF, edital, orçamento já fechado) ou é
   ainda placeholder para uma proposta comercial em construção?
6. **Quem usa o portal** — só a equipe Manta (uso interno) ou o portal é
   entregue ao cliente como produto? → define branding (logo do cliente
   aparece? onde?) e nível de confidencialidade dos dados de exemplo (regra
   R1 da skill `proposta-comercial`: nunca nome de outro cliente no código).
7. **Exportação necessária** — impressão/PDF, JSON, tela cheia para
   apresentação ao vivo? (os 3 já vêm prontos no modelo funcional
   publicado; confirmar se algum outro formato é necessário)

**Passo 3.** Duplicar o modelo funcional mais próximo — hoje,
`templates/portal-manta-modelo-padrao/index.html` para o padrão
"Orçamentação Paramétrica" — e seguir a aba "Como duplicar" embutida nele.
Se o padrão aplicável for "Dashboard Executivo" ou "Unificado" e ainda não
houver modelo funcional equivalente neste repositório, sinalizar isso
explicitamente ao usuário antes de construir do zero, em vez de presumir
que o padrão de Orçamentação Paramétrica serve para qualquer pedido de
portal.

## 4. Artefato-modelo publicado nesta sessão

`templates/portal-manta-modelo-padrao/index.html` — reproduz a estrutura,
os módulos e a complexidade observada na Família A/B (sidebar numerada,
capa com KPIs e comparação por frente, módulo de detalhe por frente com
tabela + gráfico de curva ABC, indicadores globais, ficha técnica), com
dados fictícios e placeholders no lugar dos dados de cada cliente. Contém
uma aba "Como duplicar" com o passo a passo e a tabela de tokens de cor.

## 5. Pendências para v2 deste catálogo

- [ ] Ler o código real de pelo menos um `.jsx` de cada família (via export
  `.txt`, conector com download bruto, ou colando o conteúdo diretamente
  na conversa) para confirmar componentes, dependências e se A/B de fato
  convergiram.
- [ ] Construir o modelo funcional do padrão "Dashboard Executivo
  multi-módulo" (Família ainda sem artefato de referência neste
  repositório).
- [ ] Confirmar com MN se `portal-manta-pr-v22-2/` e
  `portal-manta-lotes-pr-v9/` devem ser tratados como o mesmo produto ou
  como linhagens distintas.
