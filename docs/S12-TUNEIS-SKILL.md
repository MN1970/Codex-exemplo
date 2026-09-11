---
name: segmento-S12-tuneis
codigo: S12
camada: L1.5
tipo: segmento
version: 1.0.0-draft
status: DRAFT — a confirmar (gate humano MN pendente; pasta SharePoint 01-segmentos/S12-tuneis/ existe mas está vazia)
updated: 2026-09-11
---

# S12 Túneis — Segmento vertical

O segmento S12 cobre a engenharia de obras subterrâneas de qualquer
finalidade — túneis rodoviários, ferroviários, metroviários, hidráulicos
(adução, desvio, restituição) e galerias técnicas urbanas — do ponto de
vista de projeto geológico-geotécnico, método construtivo, suporte,
revestimento, ventilação e segurança contra incêndio, tratados de forma
unificada independentemente do segmento hospedeiro. Isso o distingue de
S1 (rodovias) e S4 (metrô), que tratam túneis como um componente dentro
do corredor viário ou da linha metroviária, e de S2 (OAE), que cobre a
interface estrutural em galerias curtas e transições túnel-ponte. S12
também se relaciona com S11 (barragens), quando o túnel é de desvio,
adução ou restituição associado a um empreendimento hidráulico, e com as
disciplinas transversais D03-Geotecnia (investigação e parâmetros de
maciço) e D22-Túneis (métodos construtivos e dimensionamento de suporte),
das quais este segmento consome insumos técnicos sem duplicá-los.

## Cobertura

**Técnicas construtivas**
- NATM / NMT (Novo Método Austríaco) — escavação sequencial com suporte
  ativo (concreto projetado, cambotas, tirantes) e monitoramento por
  convergência
- TBM (Tunnel Boring Machine) — EPB (Earth Pressure Balance), slurry
  shield, gripper (hard rock, single/double shield)
- Cut-and-cover (vala a céu aberto coberta) — típico em trechos urbanos
  rasos
- Pipe jacking / microtunelamento — travessias de pequeno diâmetro sem
  abertura de vala
- Tratamento especial de solo — jet grouting, congelamento do solo,
  rebaixamento de lençol, para condições geotécnicas adversas

**Tipologias**
- Túneis rodoviários e ferroviários (interurbanos e de montanha)
- Túneis metroviários e estações subterrâneas (urbanos rasos)
- Túneis hidráulicos — adução, desvio de rio, restituição (associados a
  barragens/PCH/UHE)
- Túneis submersos/imersos (tunnel-boring ou elementos pré-moldados
  afundados)
- Galerias técnicas urbanas (infraestrutura compartilhada)

**Fases de projeto**
1. Investigação geológico-geotécnica (sondagens, ensaios de campo e
   laboratório, classificação geomecânica)
2. Projeto conceitual/básico — traçado, seção geométrica, classes de
   suporte previstas
3. Projeto executivo — dimensionamento de suporte primário e
   revestimento definitivo, ventilação, sistemas de segurança
4. Execução e monitoramento — instrumentação, auscultação, gestão de
   frente de escavação
5. Operação e manutenção — inspeção de revestimento, sistemas de
   ventilação/incêndio
6. Gestão de risco e contingência — planos de emergência, geologia
   imprevista

## Normas-chave

| Norma/referência | Escopo | Status |
|---|---|---|
| DNIT — Publicação IPR-753, "Manual de Projeto de Túneis Rodoviários e Ferroviários" | Referência técnica nacional principal: elementos geométricos, aspectos geológico-geotécnicos, diretrizes de projeto e gestão de risco | Vigente (1ª edição) — confirmar edição/data exatos no portal DNIT antes de citar formalmente em documento contratual |
| ABNT NBR 15661 | Proteção contra incêndio em túneis rodoviários e urbanos | Vigente |
| ABNT NBR 14026 | Concreto projetado — Especificação | Status a confirmar — há indícios de cancelamento/substituição da edição de 2012; confirmar edição vigente na ABNT antes de citar formalmente |
| ISRM — Suggested Methods | Ensaios e classificação geomecânica de maciços rochosos (base de RQD, RMR, sistema Q) | Referência internacional consolidada, sem número ABNT correspondente |
| ITA-AITES — Guidelines for the Design of Tunnels (WG "General Approaches to the Design of Tunnels") | Diretrizes internacionais de investigação, modelos estruturais e método observacional | Referência internacional consolidada |
| NFPA 502 | Standard for Road Tunnels, Bridges, and Other Limited Access Highways — ventilação e segurança contra incêndio | Referência internacional, uso complementar à NBR 15661 |
| PIARC — Road Tunnels Manual | Boas práticas internacionais de operação, ventilação e segurança em túneis rodoviários | Referência internacional consolidada |
| DNIT — especificações de serviço (ES) para concreto projetado/suporte em túneis | Execução de suporte NATM | Número(s) específico(s) a confirmar — não identificados com segurança na pesquisa desta versão; não citar número sem verificação direta na coletânea DNIT |

## Cálculos e métodos padrão

- Classificação geomecânica: RMR (Bieniawski) e sistema Q (Barton) para
  definição de classe de suporte e método construtivo.
- Método convergência-confinamento: cruzamento da curva característica
  do terreno com a curva de rigidez do suporte para dimensionar o
  suporte primário NATM.
- FS de estabilidade de frente/talude de escavação: FS = τ_resistente /
  τ_atuante. Meta: definida pela classe geomecânica e pela criticidade
  da obra (túneis urbanos rasos exigem margem mais conservadora que
  túneis profundos em rocha competente).
- Razão de cobertura (C/D — cover-to-diameter ratio): indicador de risco
  de colapso superficial em túneis rasos (TBM urbano); valores baixos
  exigem tratamento de solo ou reforço adicional.
- Estimativa de recalque superficial (settlement trough) em túneis
  urbanos rasos — método de Peck, a partir da perda de volume (Vl%)
  estimada para o método construtivo adotado.
- Red flags: RQD baixo combinado com presença de água subterrânea não
  drenada; cobertura inferior a 1–2 diâmetros em solo urbano sem
  tratamento; convergência medida em instrumentação acima do previsto
  em projeto; ausência de plano de contingência para geologia
  imprevista.

## Segmentos/disciplinas relacionados

| Relacionado | Tipo de interação |
|---|---|
| S1 — Rodovias | Túneis rodoviários inseridos em corredor viário; compartilha geometria de portal e drenagem de acesso |
| S2 — OAE | Interfaces estruturais em galerias curtas, transições túnel-ponte/viaduto, boca de túnel |
| S4 — Metrô | Túneis urbanos NATM/TBM e estações subterrâneas — principal interface operacional deste segmento |
| S11 — Barragens | Túneis de desvio, adução e restituição associados a barragens, PCHs e UHEs |
| D03 — Geotecnia | Investigação geológico-geotécnica, sondagens (SPT/rotativa), parâmetros de maciço, RQD/RMR |
| D22 — Túneis | Disciplina técnica de métodos construtivos e dimensionamento de suporte — camada de conhecimento compartilhada com este segmento |

## Handoffs

| Para | Quando | Formato de entrega |
|---|---|---|
| D03-Geotecnia | Antes do dimensionamento do suporte | Relatório de investigação geotécnica, boletins de sondagem, classificação geomecânica por trecho |
| S1/S4 (segmento hospedeiro) | Ao integrar o túnel ao projeto viário/metroviário | Projeto geométrico do túnel compatibilizado, quantitativos, cronograma de interface |
| S11-Barragens | Quando o túnel for de desvio/adução/restituição em barragem | Dados hidráulicos, geometria de tomada d'água e descarga, cotas de projeto |
| Manta 05 — orçamento | Após definição do método construtivo e classes de suporte | Memorial descritivo, quantitativos por classe de suporte, composições de custo |
| Manta 01 — claims | Em disputas de classificação geomecânica ou condição geológica imprevista | Instrumentação, relatórios de frente de escavação, comparação projetado x encontrado |

## NÃO faz

- Não substitui o dimensionamento estrutural de pontes e viadutos (OAE) do S2.
- Não projeta a barragem em si (maciço, vertedouro) — apenas os túneis
  associados, cujo projeto hidráulico/estrutural principal segue com S11.
- Não define sinalização e operação viária fora do túnel — permanece
  com S1.
- Não emite ART; os produtos deste segmento são insumos técnicos para o
  agente/segmento responsável pelo entregável contratual final.
- Não substitui a investigação e a instrumentação de campo executadas
  sob D03-Geotecnia.

## Palavras-chave de roteamento

túnel, tunel, NATM, NMT, TBM, escudo, tuneladora, cut-and-cover, jet grouting, congelamento do solo, concreto projetado, shotcrete, boca de túnel, portal de túnel, galeria subterrânea, RMR, RQD, sistema Q, classificação geomecânica, convergência-confinamento, suporte primário, revestimento definitivo, túnel de adução, túnel de desvio, poço de ventilação, PIARC, NFPA 502, túnel submerso, microtunelamento
