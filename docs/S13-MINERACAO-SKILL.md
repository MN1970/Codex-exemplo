---
name: segmento-S13-mineracao
codigo: S13
camada: L1.5
tipo: segmento
version: 1.0.0-draft
status: DRAFT — a confirmar (gate humano MN pendente; pasta SharePoint 01-segmentos/S13-mineracao/ existe mas está vazia)
updated: 2026-09-11
---

# S13 Mineração — Segmento vertical

O segmento S13 cobre a engenharia da operação de mineração propriamente
dita: lavra a céu aberto e subterrânea, beneficiamento/processamento
mineral e logística de escoamento de minério (correias de longa
distância, mineroduto, ferrovia e porto dedicados). O ponto de atenção
central deste segmento é a fronteira com S11-Barragens: barragens de
rejeitos, de contenção de sedimentos e as pilhas/estruturas de disposição
associadas a elas (TSF — *Tailings Storage Facility*) são tratadas
integralmente por S11, que responde pelo projeto geotécnico-estrutural e
pela segurança da barragem em si; S13 fornece a S11 apenas os dados de
origem (volume, caracterização e cronograma de geração de rejeitos), sem
duplicar o projeto da estrutura de contenção. S13 também se relaciona
com S12-Túneis (métodos construtivos compartilhados em acessos
subterrâneos — rampas, poços, galerias), com D03-Geotecnia (estabilidade
de taludes de cava e de escavações subterrâneas) e, na ponta de
escoamento, com S3-Ferrovia e S6-Portos.

## Cobertura

**Métodos de lavra**
- Lavra a céu aberto — sequenciamento de bancadas, projeto de cava,
  blend de minério, taludes inter-rampa e globais
- Lavra subterrânea — câmaras e pilares, sublevel stoping, corte e
  enchimento (cut and fill), block/sublevel caving
- Lavra aluvionar/dragagem — extração em depósitos fluviais e de
  planície aluvial

**Beneficiamento (processamento mineral)**
- Britagem e moagem (cominuição)
- Classificação granulométrica
- Concentração — flotação, separação magnética, separação gravimétrica
- Espessamento e filtragem de polpa
- Manejo de pilhas de ROM (run-of-mine) e de produto

**Logística de minério**
- Correias transportadoras de longa distância
- Mineroduto
- Interface com ferrovia dedicada/captive (S3) e terminal portuário de
  granéis sólidos (S6)

**Fases de projeto (ciclo de vida)**
1. Pesquisa mineral / estudo de viabilidade (EVTE)
2. Plano de lavra e Plano de Aproveitamento Econômico (PAE)
3. Projeto básico e executivo de mina e planta de beneficiamento
4. Implantação/obra
5. Operação
6. Due diligence / M&A de ativo minerário
7. Fechamento de mina e reabilitação de áreas degradadas

## Normas-chave

| Norma/referência | Escopo | Status |
|---|---|---|
| ANM — Normas Reguladoras da Mineração (NRM-01 a NRM-22) | Conjunto de normas obrigatórias da Agência Nacional de Mineração, da pesquisa ao fechamento; destaque para NRM-17 (Topografia de Minas), NRM-18 (Beneficiamento), NRM-19 (Disposição de estéril, rejeitos e produtos), NRM-20 (Suspensão/fechamento de mina) e NRM-21 (Reabilitação de áreas pesquisadas/mineradas/impactadas) | Vigente |
| Decreto-Lei nº 227/1967 (Código de Mineração) e regulamento | Base legal da atividade minerária — exigência do PAE (Plano de Aproveitamento Econômico) e do Plano de Lavra | Vigente, com alterações posteriores |
| NR-22 | Segurança e Saúde Ocupacional na Mineração (Ministério do Trabalho) | Vigente — revisão relevante publicada em 2024 |
| ABNT NBR 13029 | Mineração — Elaboração e apresentação de projeto de disposição de estéril em pilha | Vigente (edição mais recente identificada: 2024) |
| ABNT NBR 13030 | Elaboração e apresentação de projeto de reabilitação de áreas degradadas pela mineração | Vigente (edição original de 1999; confirmar se há revisão mais recente antes de citar em documento formal) |
| CBRR — Código Brasileiro de Recursos e Reservas Minerais | Diretrizes voluntárias (não vinculantes) para declaração pública de recursos e reservas minerais, alinhadas ao template CRIRSCO | Vigente — adesão voluntária, não obrigatória |
| Guidelines for Open Pit Slope Design (Read & Stacey, projeto LOP/CSIRO) | Referência internacional consolidada para investigação, projeto geotécnico e monitoramento de taludes de cava | Referência técnica internacional, não é norma regulatória |
| ISRM — Suggested Methods | Classificação geomecânica de maciços (RMR, sistema Q) aplicada a taludes de cava e escavações subterrâneas | Referência internacional consolidada |

**Fronteira explícita com S11:** ABNT NBR 13028 (projeto de barragens de
mineração) e a Resolução ANM nº 95/2022 (segurança de barragens de
mineração, PNSB) pertencem ao escopo de S11-Barragens, não a S13 — citadas
aqui apenas para deixar clara a fronteira de responsabilidade.

## Cálculos e métodos padrão

- FS de talude de cava (equilíbrio limite — Bishop, Spencer ou
  Morgenstern-Price, conforme geometria): FS = τ_resistente / τ_atuante.
  Meta: da ordem de 1,2 para taludes de bancada/inter-rampa operacionais
  a 1,3–1,5 para taludes globais de longo prazo, com o valor exato
  definido pela análise de consequência do projeto (ver Read & Stacey) —
  não adotar um valor único sem essa análise.
- Razão estéril/minério (stripping ratio) para sequenciamento de lavra e
  definição de teor de corte (cutoff grade) econômico.
- Diluição planejada e recuperação de lavra — indicadores de controle de
  aderência entre modelo de blocos e resultado realizado.
- Beneficiamento: recuperação metalúrgica (%) e balanço de massa e água
  (moagem, flotação, espessamento).
- Red flags: FS de talude abaixo da meta definida para a classe de
  consequência; presença de água subterrânea não drenada em bancada;
  PAE desatualizado frente à cava realizada; disposição de estéril em
  pilha sem projeto conforme NBR 13029; ausência de plano de fechamento
  atualizado (NRM-20/21).

## Segmentos/disciplinas relacionados

| Relacionado | Tipo de interação |
|---|---|
| S11 — Barragens | Barragens de rejeitos e de contenção de sedimentos — S11 é responsável pelo projeto e segurança da estrutura; S13 fornece os dados de origem dos rejeitos |
| S12 — Túneis | Métodos construtivos compartilhados para acessos subterrâneos de mina (rampas, poços, galerias) |
| S1 — Rodovias | Vias de acesso e de serviço (haul roads) fora da cava, quando aplicável |
| S3 — Ferrovia | Ferrovias dedicadas/captive de escoamento de minério |
| S6 — Portos | Terminais portuários de granéis sólidos para exportação de minério |
| D03 — Geotecnia | Investigação geotécnica, ensaios de resistência ao cisalhamento, parâmetros de água subterrânea para estabilidade de taludes e escavações |

## Handoffs

| Para | Quando | Formato de entrega |
|---|---|---|
| S11-Barragens | Quando o projeto envolve barragem de rejeitos/sedimentos | Volume e caracterização de rejeitos, curva de alteamento prevista, cronograma de disposição |
| D03-Geotecnia | Antes do dimensionamento de taludes de cava ou de escavações subterrâneas | Investigação geotécnica, ensaios de cisalhamento/triaxial, dados piezométricos |
| S3-Ferrovia / S6-Portos | Quando há logística dedicada de minério | Especificação do produto (granulometria, umidade), volumes e sazonalidade de escoamento |
| Manta 05 — orçamento | Após definição do plano de lavra | Quantitativos de movimentação de estéril/minério, plano de lavra, PAE |
| Manta 01 — claims | Disputas de condição geológica/geotécnica imprevista na cava | Modelo de blocos, dados de sondagem, comparação entre projetado e realizado |

## NÃO faz

- Não projeta nem avalia a segurança de barragens de rejeitos ou de
  sedimentos — escopo integral de S11-Barragens (NBR 13028, Resolução
  ANM 95/2022).
- Não substitui a certificação formal de recursos e reservas por
  competent person (CBRR/CRIRSCO) — apenas organiza e referencia os
  dados técnicos de suporte.
- Não conduz o licenciamento ambiental em si (EIA/RIMA) — fornece
  insumos técnicos de lavra e beneficiamento que alimentam esse processo.
- Não emite laudos de segurança e saúde ocupacional sob NR-22 — apoia
  com dados técnicos quando solicitado pelo responsável técnico da área.

## Palavras-chave de roteamento

mineração, mina, lavra, lavra a céu aberto, lavra subterrânea, cava, bancada, pit, stripping ratio, ROM, beneficiamento mineral, britagem, moagem, flotação, minério, estéril, pilha de estéril, mineroduto, PAE, plano de aproveitamento econômico, ANM, NRM, teor de corte, cutoff grade, block caving, sublevel stoping, câmaras e pilares, modelo de blocos, fechamento de mina
