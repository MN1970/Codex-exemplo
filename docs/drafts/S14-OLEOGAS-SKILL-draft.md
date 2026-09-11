---
name: segmento-S14-oleogas
codigo: S14
camada: L1.5
tipo: segmento
version: 1.0.0-draft
updated: 2026-09-11
---

# S14 Óleo e Gás — Segmento vertical

O segmento S14 cobre a infraestrutura física da cadeia de óleo e gás no
contexto regulatório brasileiro (ANP): upstream (exploração e produção,
onshore e offshore), midstream (dutos de transporte, estações de
bombeio/compressão, terminais de armazenamento e GNL) e downstream
(refino e distribuição), com foco na engenharia civil, geotécnica e de
integridade dutoviária dessas instalações. Relaciona-se com S9-Energia
nas interfaces de gás natural para geração termelétrica, com S6-Portos
nos terminais aquaviários de granéis líquidos e GNL, com S1-Rodovias e
S3-Ferrovia nas travessias de dutos sob faixas de domínio existentes, e
com D03-Geotecnia no projeto de valas, travessias especiais (perfuração
direcional horizontal) e cravações.

## Cobertura

**Segmentos da cadeia**
- Upstream — exploração e produção onshore/offshore, plataformas fixas
  e flutuantes (FPSO), poços (interface, não projeto de reservatório)
- Midstream — oleodutos, gasodutos e polidutos; estações de bombeio e
  compressão; terminais de armazenamento (tancagem); terminais de GNL
- Downstream — unidades de processamento (UPGN), refino, distribuição e
  revenda

**Infraestrutura física**
- Dutos terrestres e submarinos (projeto, construção, integridade)
- Estações de bombeio/compressão
- Terminais aquaviários e terrestres, parques de tancagem
- Faixas de servidão e cruzamentos com outras infraestruturas

**Fases do ciclo**
1. Estudo de viabilidade / prospecção
2. Projeto básico
3. Projeto executivo
4. Construção e montagem
5. Operação e gestão de integridade
6. Due diligence / M&A de ativos
7. Descomissionamento (plataformas, dutos, campos maduros)

## Normas-chave

| Norma/referência | Escopo | Status |
|---|---|---|
| ANP — Resolução ANP nº 6/2011 (RTDT — Regulamento Técnico de Dutos Terrestres) | Requisitos mínimos de segurança operacional para dutos terrestres (oleodutos e gasodutos), incluindo construção, operação e desativação | Vigente |
| ANP — Resolução ANP nº 43/2007 (SGSO) | Sistema de Gerenciamento de Segurança Operacional para instalações marítimas de perfuração e produção de petróleo e gás | Vigente |
| NR-37 | Segurança e saúde em plataformas de petróleo | Vigente |
| ABNT NBR 12712 | Projeto de sistemas de transmissão e distribuição de gás combustível (dutos), incluindo critérios de cruzamento e travessia | Vigente (edição de 2002 + Emenda 1/2002) |
| ABNT NBR 15280-1 | Dutos terrestres — Parte 1: Projeto | Vigente |
| ABNT NBR 15280-2 | Dutos terrestres — Parte 2: Construção e montagem | Vigente |
| API 5L | Line Pipe — especificação de tubos de aço para dutos | Referência internacional, uso consolidado no setor |
| API 1104 | Welding of Pipelines and Related Facilities | Referência internacional, uso consolidado no setor |
| API 6D | Pipeline and Piping Valves | Referência internacional, uso consolidado no setor |
| API RP 1160 | Managing System Integrity for Hazardous Liquid Pipelines | Referência internacional, uso consolidado no setor |
| ASME B31.4 / ASME B31.8 | Pipeline Transportation Systems for Liquids and Slurries / Gas Transmission and Distribution Piping Systems | Referência internacional, uso complementar às normas ABNT |

## Cálculos e métodos padrão

- Dimensionamento de espessura de parede de duto — fórmula de Barlow:
  t = P·D / (2·S·F·E·T), conforme critérios de NBR 15280-1 / API 5L /
  ASME B31.4 ou B31.8, com fatores de projeto (F), de junta (E) e de
  temperatura (T) definidos pela classe de localização do traçado.
- Faixa de segurança/servidão e distâncias mínimas a terceiros conforme
  classe de localização definida na Resolução ANP 6/2011 (RTDT).
- Avaliação de integridade por perda de espessura (corrosão) a partir de
  inspeção interna instrumentada (ILI/"pig" instrumentado); cálculo de
  pressão de operação segura remanescente por métodos internacionalmente
  reconhecidos como ASME B31G e RSTRENG — citados aqui como métodos de
  engenharia consolidados, não como normas brasileiras específicas.
- Gestão de risco operacional: implementação das práticas do SGSO
  (Resolução ANP 43/2007) e estudos de análise de risco (HAZOP, QRA)
  conduzidos por especialistas de segurança de processo.
- Red flags: ausência de inspeção instrumentada dentro do prazo definido
  no plano de integridade; perda de espessura acima do limite crítico
  sem plano de reparo formalizado; cruzamento de duto com rodovia/
  ferrovia sem estudo específico conforme NBR 12712; instalação offshore
  operando sem SGSO implementado.

## Segmentos/disciplinas relacionados

| Relacionado | Tipo de interação |
|---|---|
| S9 — Energia | Interfaces em gás natural para geração termelétrica e plantas de processamento de gás |
| S6 — Portos | Terminais aquaviários de granéis líquidos e GNL |
| S1 — Rodovias / S3 — Ferrovia | Travessias de dutos sob rodovias/ferrovias existentes; faixas de servidão |
| D03 — Geotecnia | Geotecnia de valas, travessias especiais (perfuração direcional horizontal), cravações |
| S11 — Barragens | Interface pontual em reservatórios e captação de água industrial, quando aplicável |

## Handoffs

| Para | Quando | Formato de entrega |
|---|---|---|
| D03-Geotecnia | Antes do projeto de travessias especiais (HDD, cravação) | Investigação geotécnica ao longo do traçado, dados de perfuração |
| S1 / S3 | Quando o duto cruza rodovia ou ferrovia existente | Estudo de cruzamento conforme NBR 12712, ART, cronograma de interdição |
| S6-Portos | Quando há terminal aquaviário associado ao projeto | Especificação do produto, dados operacionais do terminal |
| Manta 05 — orçamento | Após definição de traçado e classe de duto | Memorial de quantidades, especificação de material (API 5L), cronograma |
| Manta 01 — claims | Disputas de integridade ou condição de campo imprevista | Relatórios de inspeção (ILI), histórico de manutenção, dados de corrosão |

## NÃO faz

- Não trata de geração ou transmissão de energia elétrica — permanece
  com S9-Energia, exceto nas interfaces pontuais de gás natural para
  geração.
- Não substitui a engenharia de segurança de processo (HAZOP/QRA) por
  especialistas certificados — apoia com dados técnicos de engenharia
  civil e de integridade dutoviária.
- Não conduz o licenciamento ambiental de exploração e produção em si —
  fornece apenas insumos técnicos de engenharia.
- Não faz projeto naval/estrutural de plataformas flutuantes (FPSO) —
  escopo de engenharia naval especializada, fora do núcleo de
  infraestrutura civil da Manta.
- Não projeta poço nem trata de engenharia de reservatório (upstream
  profundo) — fora do escopo de engenharia civil deste segmento.

## Palavras-chave de roteamento

óleo e gás, oil and gas, ANP, duto, oleoduto, gasoduto, poliduto, upstream, midstream, downstream, plataforma, FPSO, terminal aquaviário, GNL, refinaria, RTDT, SGSO, API 5L, pipeline, integridade de dutos, ILI, pig instrumentado, cruzamento de dutos, faixa de servidão, UPGN, E&P, pré-sal
