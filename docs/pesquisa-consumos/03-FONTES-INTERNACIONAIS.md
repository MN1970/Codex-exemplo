# Fontes — Internacionais

Catálogo legível por máquina: `../../data/consumos/registro-fontes.csv`.
Ver `02-FONTES-BRASIL.md` para a regra do campo `entrega`.

## Camada 6 — Multilaterais e agências

### Insumo-produto e intensidade material (geram tier A)

As únicas fontes internacionais que dão intensidade física comparável entre
países no mesmo formato da nossa base:

- **OECD ICIO** `F-012` — tabelas de insumo-produto inter-país. Melhor rota para
  comparação internacional de coeficiente de insumo da construção.
- **EXIOBASE** `F-014` — insumo-produto ambientalmente estendido; dá aço e
  cimento por unidade de valor construído.
- **WIOD** `F-013` — descontinuada, útil para série histórica.
- **UN International Resource Panel** `F-015` — intensidade material por setor e
  país.
- **Eurostat** `F-011` — contas da construção por classe NACE.

### Bancos de desenvolvimento (denominadores de CAPEX)

- **INFRALATAM** `F-100` (BID + CAF + CEPAL) — investimento em infraestrutura na
  América Latina por setor e país. **O denominador latino-americano canônico.**
- **Banco Mundial**: ROCKS `F-094` (custo rodoviário por país), HDM-4 `F-095`,
  PPI Database `F-096`, **Contract Awards** `F-097` (valor real de contrato por
  país e setor), Port Reform Toolkit `F-098`, ESMAP `F-099`.
- **BID** `F-101`, **CAF/Informe IDEAL** `F-102`, **CEPAL** `F-103`,
  **EIB/JASPERS** `F-104`, **ADB** `F-106`.
- **Comissão Europeia / DG REGIO** `F-105` — o *Guide to Cost-Benefit Analysis*
  traz custo unitário de referência por setor.
- **OCDE / ITF** `F-107`.

### Mão de obra em contexto de baixa mecanização

- **OIT/ILO — programa ASIST** `F-108`. Coeficiente de mão de obra por m3 em obra
  rodoviária de baixa mecanização. É o tipo de dado que **não existe** nas fontes
  de países ricos e que importa em obra brasileira de interior e em África.

### Reguladores com avaliação de custo aberta

Subestimados e muito detalhados:

- **Ofwat** `F-113` — a revisão PR24 publica custo unitário de saneamento por
  unidade de serviço. Melhor referência internacional para S8.
- **Ofgem** `F-114` (RIIO) para S9.
- **National Highways** `F-115` (Cost Estimating Manual) e **IPA/UK** `F-116`.
- **Infrastructure Australia** `F-117`.

### Composições e normas técnicas por setor

- **USACE MII/MCACES** `F-118` — composições de obra hidráulica e dragagem com
  crew e produção. Tier A quando lido. Relevante para S6 e S10.
- **USBR** `F-119` — barragens.
- **FAA** `F-120` — Advisory Circulars e histórico do AIP: pavimento aeroportuário
  e custo de projeto financiado. Relevante para S7, que não tem classe CNAE.
- **BEDEC / ITeC** `F-124` — consulta online gratuita, excelente em obra
  hidráulica e marítima. **Embute perda de material** (como o SINAPI, ao
  contrário do SICRO).
- **PIANC** `F-121` e **Puertos del Estado / ROM** `F-123` para S6.
- **ICOLD** `F-122` para S10.

### Energia

**IEA** `F-110`, **IRENA** `F-111` (CAPEX por MW por tecnologia), **NREL ATB**
`F-112`.

### Marítimo

**UNCTAD — Review of Maritime Transport** `F-109`.

## Camada 5 internacional — academia

- **CII / UT Austin** `F-091` — benchmarking de produtividade de mão de obra.
- **Oxford Global Projects** `F-092` — base de desvio de custo e *reference class
  forecasting* (Flyvbjerg).
- **Transit Costs Project / NYU Marron** `F-093` — custo comparado de metrô e
  ferrovia entre países. Aberto e muito bem documentado.

## Camada 7 — Proprietária, cite-only

Ver `04-GOVERNANCA-LICENCAS.md`. Catalogadas com cobertura e forma de acesso;
**nenhum coeficiente copiado**.

RSMeans/Gordian `F-125`, Spon's `F-126`, Rawlinsons `F-127`, Caterpillar
Performance Handbook `F-128`, Komatsu Handbook `F-129`, EquipmentWatch Blue Book
`F-130`, ONDAC `F-131`, Construdata `F-132`, Revista Costos `F-133`, BIMSA/Opus
`F-134`, BKI `F-135`, Batiprix `F-136`.
