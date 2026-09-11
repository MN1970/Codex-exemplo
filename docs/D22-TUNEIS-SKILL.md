---
name: disciplina-D22-tuneis
codigo: D22
camada: L1.8
tipo: disciplina
version: 0.1.0-draft
status: DRAFT — a confirmar (gate humano MN pendente; pasta SharePoint estava vazia)
updated: 2026-09-11
---

# D22 Túneis — Biblioteca técnica

> **Nota de origem**: esta disciplina existe como pasta vazia no
> SharePoint (`01-agentes-fundamentais/.../D22`), sem conteúdo prévio.
> Este documento é um primeiro rascunho, estruturado no mesmo padrão de
> D03-Geotecnia, para revisão e gate humano MN antes de publicação.
> Normas citadas foram verificadas por busca externa nesta sessão; onde
> não foi possível confirmar número, edição, vigência ou escopo exato
> com segurança, o item está marcado **"a confirmar"** em vez de um
> valor estimado.

**D22 é a disciplina técnica de engenharia de túneis** (método
construtivo, revestimento, impermeabilização, ventilação,
monitoramento) — distinta do **S12 Túneis**, que é o segmento de
mercado (o ativo/contrato). D22 é o know-how consumido por S12 como
ativo principal, e também por S1 (túnel rodoviário em traçado), S2 OAE
(quando o túnel é tratado como estrutura especial) e S4 Metrô (túneis
de linha). Depende fortemente de D03 Geotecnia para caracterização do
maciço e de D21 Topografia e Geodésia para transporte de coordenadas a
portais e eixo de escavação.

## Cobertura

### Métodos construtivos
- NATM / Método Sequencial de Escavação (SEM — Sequential Excavation
  Method): escavação por fases, sustentação inicial imediata,
  observação contínua do comportamento do maciço (método
  observacional), revestimento definitivo posterior.
- TBM (tuneladora): EPB (Earth Pressure Balance), slurry shield, TBM
  aberta/hard rock — escavação mecanizada contínua com revestimento
  primário em anéis pré-moldados (dovelas).
- Cut-and-cover (vala a céu aberto coberta) — alternativa para trechos
  rasos ou de baixo recobrimento.
- Microtunelamento / jacking — cravação de tubos para redes de
  pequeno/médio diâmetro (interface com S9 Saneamento).

### Classificação geomecânica do maciço (compartilhado com D03)
- RMR — Rock Mass Rating (Bieniawski): soma de 5 parâmetros
  (resistência à compressão uniaxial da rocha intacta, RQD,
  espaçamento de descontinuidades, condição das descontinuidades,
  água subterrânea) mais ajuste pela orientação das descontinuidades
  em relação ao eixo do túnel; escala 0–100 define 5 classes de
  maciço (I a V).
- Q-system (Barton, Lien e Lunde): índice de qualidade do maciço
  derivado de seis parâmetros agrupados em três razões, usado para
  estimar suporte necessário.
- GSI — Geological Strength Index (Hoek): estima parâmetros de
  resistência/deformabilidade do maciço a partir de observação de
  campo (estrutura da rocha e condição das superfícies de
  descontinuidade), correlacionável ao RMR.
- Critério de ruptura de Hoek-Brown para o maciço rochoso (usa
  parâmetros derivados de GSI/RMR); Mohr-Coulomb para descontinuidades
  isoladas.
- Conjunto de referência: ISRM Suggested Methods (boletins da
  International Society for Rock Mechanics) — não é uma norma única,
  é uma coletânea de métodos sugeridos para ensaio e classificação de
  rocha, referenciada internacionalmente e usada como base de boa
  prática no Brasil na ausência de NBR específica equivalente.

### Suporte e revestimento
- Concreto projetado (shotcrete) como sustentação inicial —
  especificação técnica conforme NBR 14026.
- Cambotas metálicas, tela metálica/fibra, tirantes e chumbadores como
  elementos complementares de suporte inicial.
- Revestimento definitivo: concreto moldado in loco (NATM) ou
  segmentos pré-moldados/dovelas (TBM); dupla camada com
  impermeabilização intermediária quando há exigência de estanqueidade
  (túneis rodoviários/metroviários urbanos, adução).

### Impermeabilização e drenagem
- Sistema de impermeabilização por manta/geomembrana entre
  revestimento primário e secundário.
- Drenagem periférica (dreno de calota/parede) para alívio de
  subpressão de água antes do revestimento definitivo.

### Ventilação
- Ventilação natural (efeito chaminé/pistão de tráfego), longitudinal
  (jato/jet fan) e transversal/semitransversal, dimensionada em função
  do comprimento do túnel, tráfego previsto e cenário de emergência
  (incêndio, fumaça).
- Referências internacionais habitualmente usadas no setor: NFPA 502
  e diretrizes ITA-AITES/PIARC para túneis rodoviários — **a
  confirmar** se há adoção formal por norma brasileira específica
  (não localizada nesta pesquisa uma NBR/portaria brasileira dedicada
  a ventilação de túnel rodoviário; tratar como referência de boa
  prática internacional até confirmação).

### Monitoramento e instrumentação
- Convergência de seção transversal, extensômetros, inclinômetros,
  marcos superficiais, piezômetros.
- Método observacional (núcleo do NATM): comparação contínua entre
  leitura de campo e comportamento previsto em projeto, com limites de
  alerta e de alarme por seção/classe de suporte.
- Interface direta com D21 para monitoramento topográfico de
  recalque em superfície acima do túnel (áreas urbanas/S4 Metrô).

### Segurança do trabalho em obra subterrânea
- NR-18 (Segurança e Saúde no Trabalho na Indústria da Construção) —
  disposições sobre escavação, fundação e desmonte de rochas,
  exigência de projeto por profissional habilitado e sinalização de
  risco.
- NR-33 (Segurança e Saúde em Espaços Confinados) — aplicável a
  atividades específicas dentro do túnel conforme classificação do
  espaço.
- NR-22 (Segurança e Saúde Ocupacional na Mineração) trata de
  escavação subterrânea no contexto de mineração — referência
  análoga, **não diretamente aplicável** a túneis civis; usar com
  cautela e não citar como norma cogente para obra de infraestrutura
  de transporte.

### Aspectos geométricos
- Seção transversal conforme gabarito do modal (rodoviário, ferroviário,
  metroviário), raio mínimo de curvatura, greide, geometria e proteção
  de portais.

## Normas-chave

| Norma / Referência | Escopo | Aquisição | Status verificação |
|---|---|---|---|
| NBR 14026:2012 | Concreto projetado (shotcrete) — especificação; 2ª edição, substitui a de 1997 | Paga (ABNT) | Vigente — 2ª edição confirmada |
| DNIT/IPR-753 — Manual de Projeto de Túneis (1ª edição) | Diretrizes de projeto geométrico, aspectos geológico-geotécnicos e gestão de risco para túneis convencionais (escavação sequencial) rodoviários e ferroviários | Gratuita (DNIT/IPR) | Documento localizado com título, número de publicação (IPR-753) e ano (2026) confirmados por busca; **conteúdo integral e status final (versão definitiva vs. ainda sujeita a errata/consulta pública) não confirmados nesta sessão** — o PDF oficial em gov.br não pôde ser acessado pelo proxy de rede desta sessão. Confirmar diretamente com DNIT/IPR antes de citar cláusula específica |
| ISRM Suggested Methods (diversos boletins) | Classificação e ensaio de maciço rochoso (RMR, Q, GSI, ensaios de resistência) | Gratuita/parcial conforme boletim (ISRM) | Vigente como conjunto de referências consolidado internacionalmente — não é uma norma única; citar o boletim específico usado, não "ISRM" genericamente |
| ITA-AITES — Guidelines for the Design of Tunnels (WG "General Approaches to the Design of Tunnels") | Diretrizes internacionais de projeto: investigação, análise de tensão/deformação, modelos estruturais (inclui método observacional), detalhamento de revestimento | Gratuita/parcial (ITA-AITES) | Referência internacional consolidada — não é norma cogente no Brasil; usar como boa prática, não como exigência normativa |
| NR-18 | Segurança e saúde na indústria da construção — inclui escavação/desmonte de rocha | Gratuita (Ministério do Trabalho e Emprego) | Vigente |
| NR-33 | Segurança e saúde em espaços confinados | Gratuita (MTE) | Vigente |
| NBR 16939 | Ensaio de duplo puncionamento ("Barcelona") em concreto — usado para controle de concreto projetado/reforçado com fibras | Paga (ABNT) | Existência confirmada; **ano de publicação e escopo exato de aplicação a túneis a confirmar** antes de citar em memorial |
| NBR 13070 | Concreto reforçado com fibras de aço — procedimento de ensaio | Paga (ABNT) | Existência confirmada; **escopo exato e ano a confirmar** — não verificado com segurança suficiente nesta pesquisa |

## Cálculos e métodos padrão

### Classificação RMR (Bieniawski)
- RMR = soma de 5 parâmetros de campo/laboratório (resistência da
  rocha intacta, RQD, espaçamento de descontinuidades, condição das
  descontinuidades, água subterrânea), ajustada pela orientação das
  descontinuidades em relação ao eixo do túnel; RMR de 0 a 100 define
  5 classes de maciço (I muito bom a V muito ruim), usadas para
  orientar tempo de auto-sustentação e tipo de suporte.
- Red flag: RMR calculado sem aplicar o ajuste de orientação das
  descontinuidades em relação ao eixo do túnel — pode superestimar a
  qualidade efetiva do maciço na frente de escavação.

### Q-system (Barton, Lien e Lunde, 1974)
- Q = (RQD/Jn) × (Jr/Ja) × (Jw/SRF), onde Jn = número de famílias de
  juntas, Jr = rugosidade das juntas, Ja = alteração das juntas,
  Jw = fator de redução por água, SRF = fator de redução por tensão.
- Red flag: uso de Q sem atualizar o SRF para condições de "squeezing"
  (fluência) ou de alta tensão in situ — subestima a necessidade real
  de suporte em maciços sob tensão elevada.

### GSI (Hoek, 1994) e critério de Hoek-Brown
- GSI classifica o maciço por estrutura (grau de blocagem) e condição
  da superfície das descontinuidades; usado quando RMR/Q não se
  aplicam bem (maciços muito fraturados/heterogêneos, ex. rocha
  brandas/alteradas).
- GSI e RMR alimentam o critério de Hoek-Brown para estimar
  resistência e módulo de deformabilidade equivalentes do maciço.
- Red flag: GSI estimado apenas por fotografia de face de escavação,
  sem mapeamento estrutural sistemático em campo — parâmetro
  fortemente subjetivo nessas condições; sempre validar com geólogo/
  geotécnico responsável antes de usar em dimensionamento.

### Método convergência-confinamento
- Ferramenta de projeto preliminar: cruza a curva característica do
  maciço (GRC — Ground Reaction Curve, relação entre pressão interna e
  convergência da escavação) com a curva de reação do suporte (SCC —
  Support Characteristic Curve); o ponto de interseção estima a
  pressão de equilíbrio suporte-maciço.
- Red flag: aplicação em condições fortemente anisotrópicas, com
  tensões principais muito distintas no plano da seção, ou próximo a
  portais/interseções — o método (formulação axissimétrica) perde
  validade; nesses casos migrar para modelo numérico 2D/3D
  (elementos finitos/diferenças finitas).

### Monitoramento — método observacional (NATM)
- Cada seção e classe de suporte tem limites de alerta e de alarme de
  convergência definidos em projeto, comparados às leituras de
  instrumentação (fita de convergência, extensômetros) durante o
  avanço.
- Red flag: leitura de convergência acima do limite de alarme sem
  paralisação imediata da frente de escavação e reavaliação do
  suporte pela equipe de projeto/geotecnia — risco direto de colapso
  de seção.

## Segmentos onde D22 aparece

| Segmento | Peso | Exemplo típico |
|---|---|---|
| S12 Túneis | Alto | Ciclo completo de projeto/execução de túnel como ativo principal do contrato |
| S4 Metrô | Alto | Túneis de linha (NATM/TBM) e estações subterrâneas |
| S1 Rodovias | Médio | Túnel rodoviário como estrutura especial em traçado (interface com S2 quando tratado como OAE) |
| S2 OAE | Médio | Túneis curtos/passagens inferiores tratados como estrutura especial |
| S3 Ferrovia | Baixo/Médio | Túneis ferroviários em traçado de longo curso |
| S11 Barragens | Baixo | Túneis de desvio, adução e vertedouro associados à barragem |
| S9 Saneamento | Baixo | Microtunelamento/jacking para adutoras e interceptores |

## Cruzamentos S.A.D típicos

- S12.A2.D22 — quantificação de escavação, suporte e revestimento por
  classe de maciço/trecho.
- S12.A10.D22 — análise de risco geológico-geotécnico (zonas de falha,
  entrada de água, condições de squeezing).
- S4.A4.D22 — modelagem BIM do túnel e interface com estações
  (handoff para manta-06).
- S1.A1.D22 — escopo de túnel rodoviário em proposta técnica,
  comparação com alternativa a céu aberto/viaduto.
- S12.A11.D22 — acompanhamento de obra e leitura de instrumentação
  (convergência, recalque de superfície).

## Handoffs

| Para | Quando | Formato de entrega |
|---|---|---|
| D03 Geotecnia | Classificação de maciço (RMR/Q/GSI) e parâmetros geomecânicos de entrada para dimensionamento de suporte | Relatório de caracterização + planilha de classificação por estaca/trecho |
| D21 Topografia e Geodésia | Transporte de coordenadas para portais/eixo de escavação; monitoramento topográfico de recalque em superfície | Poligonal de apoio + relatório de monitoramento |
| manta-05 (orçamento) | Quantitativos de escavação/suporte/revestimento por classe de maciço | Memória de cálculo por trecho/classe de suporte |
| manta-06 (modelagem) | Modelo BIM do túnel (seção, revestimento, interferências) | Modelo IFC/3D |
| manta-07 (cronograma) | Ritmo de avanço planejado por frente e por classe de suporte | Ritmo de avanço (m/dia) por classe, marcos de frentes |
| claims (Manta 01) | Pleito por condição geológica imprevista (differing site conditions) identificada durante a escavação | Relatório de divergência geológica + registro de instrumentação |
| agente-barragens (S11) | Túneis de desvio/adução/vertedouro associados a barragem | Memória de cálculo hidráulico-estrutural do túnel |

## Skills L1 consumidas

- `autodesk-toolkit` — leitura/geração de modelo BIM (IFC), seções e
  arquivos CAD do túnel, quando aplicável, sem depender de Revit/Civil
  3D instalado.
- Nenhuma skill dedicada especificamente a dimensionamento de suporte
  de túnel, cálculo de ventilação ou classificação geomecânica
  automatizada (RMR/Q/GSI) foi localizada no catálogo atual — item de
  backlog a avaliar junto ao arquiteto-ia (Manta 16), em conjunto com
  D03 Geotecnia, se houver demanda recorrente de projetos com túnel.

## Casos-âncora

Nenhum caso-âncora registrado ainda — a popular conforme os primeiros
projetos que consumirem esta disciplina.

## NÃO faz

- Não substitui projeto executivo assinado por engenheiro habilitado
  (ART/RRT) para estrutura de suporte e revestimento de túnel.
- Não define classificação de maciço isoladamente — depende de dados
  de campo/investigação fornecidos por D03 Geotecnia; não deve gerar
  RMR/Q/GSI "a partir do nada".
- Não substitui análise numérica (elementos finitos/diferenças
  finitas) em geometria complexa, túneis múltiplos próximos ou
  interação solo-estrutura relevante — convergência-confinamento é
  ferramenta de projeto preliminar, não de projeto executivo final.
- Não emite parecer de segurança operacional de túnel em uso — isso é
  atribuição do órgão gestor/concessionária responsável pela operação.
- Não substitui o plano de contingência/resgate de obra subterrânea
  elaborado pelo SESMT da obra (NR-18/NR-33).
- Não trata S12-Túneis (segmento de mercado/contrato) como sinônimo
  desta disciplina — D22 é o conhecimento técnico consumido por S12
  (e por S1, S2, S4), não o agente vertical do segmento.

## Palavras-chave de roteamento

túnel, túneis, NATM, método sequencial de escavação, SEM, TBM,
tuneladora, EPB, slurry shield, dovela, revestimento de túnel,
concreto projetado, shotcrete, cambota, tirante, impermeabilização de
túnel, ventilação de túnel, jet fan, RMR, Bieniawski, Q-system,
Barton, GSI, Hoek-Brown, convergência-confinamento, método
observacional, portal de túnel, escavação subterrânea, microtunelamento,
jacking, ITA-AITES, ISRM, DNIT IPR-753
