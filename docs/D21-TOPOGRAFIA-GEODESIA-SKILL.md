---
name: disciplina-D21-topografia-geodesia
codigo: D21
camada: L1.8
tipo: disciplina
version: 0.1.0-draft
status: DRAFT — a confirmar (gate humano MN pendente; pasta SharePoint estava vazia)
updated: 2026-09-11
---

# D21 Topografia e Geodésia — Biblioteca técnica

> **Nota de origem**: esta disciplina existe como pasta vazia no
> SharePoint (`01-agentes-fundamentais/.../D21`), sem conteúdo prévio.
> Este documento é um primeiro rascunho, estruturado no mesmo padrão de
> D03-Geotecnia, para revisão e gate humano MN antes de publicação.
> Normas citadas foram verificadas por busca externa nesta sessão
> (ver rodapé de cada item); onde não foi possível confirmar número,
> edição ou vigência com segurança, o item está marcado
> **"a confirmar"** em vez de um valor estimado.

Georreferenciamento, sistemas de referência geodésica, levantamento
planialtimétrico, aerolevantamento (drone/LiDAR) e cadastro técnico
para obras de infraestrutura. Alimenta primariamente o traçado e a
faixa de domínio de rodovias (S1) e ferrovias (S3), e dá suporte a
implantação de eixo/gabarito de OAE (S2), rede de apoio superficial
para metrô (S4), due diligence fundiária (S5 Imobiliário) e transporte
de coordenadas para portais de túnel (interface com D22).

## Cobertura

### Sistemas de referência geodésica
- SIRGAS2000 (Sistema de Referência Geocêntrico para as Américas,
  realização 2000) — referencial oficial do Sistema Geodésico
  Brasileiro (SGB) e do Sistema Cartográfico Nacional (SCN) desde a
  Resolução do Presidente do IBGE nº 1/2005; único referencial
  planimétrico do país desde o fim do período de transição em 2015
  (Resolução IBGE PR nº 1/2015).
- Sistemas anteriores ainda encontrados em acervos legados: SAD69,
  Córrego Alegre — exigem transformação de coordenadas antes de
  integração a projeto novo.
- Projeção UTM (fusos), altitude ortométrica vs. altitude elipsoidal
  (GNSS), modelo geoidal do IBGE (MAPGEO) para conversão H = h − N.

### Posicionamento GNSS
- Métodos: estático, estático-rápido, RTK (tempo real, base própria ou
  via rede), PPP (Precise Point Positioning).
- RBMC — Rede Brasileira de Monitoramento Contínuo dos Sistemas GNSS
  (IBGE): rede de estações de referência ativas usada para
  pós-processamento e correção RTK/DGPS; dados em RINEX2 disponíveis
  no portal IBGE.
- Transporte de coordenadas de RN/vértice geodésico oficial para a
  poligonal de apoio do projeto.

### Levantamento planialtimétrico
- Poligonação topográfica: classes de precisão IP a VP conforme
  NBR 13133 — da densificação de rede geodésica (IP) a estudos
  expeditos (VP), cada classe com especificação de equipamento
  (teodolito/estação total, MED), método de leitura e distância
  mínima entre vértices.
- Nivelamento geométrico e trigonométrico, caderneta de campo,
  cálculo e ajuste de poligonal e de rede de nivelamento.
- Levantamento de detalhes (planimétrico e altimétrico) para projeto
  básico/executivo, as built e cadastro de faixa de domínio.

### Aerolevantamento e sensoriamento remoto
- Aerofotogrametria com RPA (drone): regulada pela ANAC — RBAC 100
  (Resolução ANAC nº 805) substituiu integralmente o RBAC-E nº 94/2017
  a partir de 16/06/2026, com regras complementares de DECEA
  (espaço aéreo) e ANATEL (radiofrequência); mudança de enfoque de
  "peso do equipamento" para "risco da operação".
- LiDAR aerotransportado e terrestre (veículo/mochila — mobile
  mapping), nuvem de pontos (LAS/LAZ), classificação de pontos
  (solo/vegetação/edificação), geração de MDT/MDS.
- Restituição fotogramétrica, ortofoto, mosaico — insumo para plano
  altimétrico de projeto conceitual/EVTE.

### Georreferenciamento de imóveis rurais
- Base legal: Lei nº 10.267/2001 (cria o Cadastro Nacional de Imóveis
  Rurais e torna obrigatório o georreferenciamento de limites) e
  Decreto nº 4.449/2002 (regulamenta prazos e procedimento).
- Norma Técnica para Georreferenciamento de Imóveis Rurais (NTGIR),
  INCRA — 3ª edição (2013): precisão posicional exigida por tipo de
  vértice definidor de limite (ver seção de cálculos).
- SIGEF (Sistema de Gestão Fundiária, INCRA) — submissão do memorial
  descritivo georreferenciado para certificação; certificação é
  pré-requisito para qualquer alteração de matrícula de imóvel rural
  (compra e venda, desmembramento, partilha).

### Cadastro técnico e cartografia
- Cadastro Técnico Multifinalitário (CTM) urbano — integração de
  levantamento topográfico a base cadastral municipal.
- NBR 14166 (Rede de Referência Cadastral Municipal — RRCM):
  estabelece rede básica de apoio planialtimétrico municipal,
  materializada em campo, referenciada ao SGB, com espaçamento típico
  ≤ 2 km em zona urbana e densificação ≤ 500 m em áreas consolidadas —
  ver **Red flag** sobre status de vigência.
- PEC — Padrão de Exatidão Cartográfica (Decreto nº 89.817/1984):
  classifica produto cartográfico por classe de exatidão planimétrica
  e altimétrica em função da escala.

## Normas-chave

| Norma / Referência | Escopo | Aquisição | Status verificação |
|---|---|---|---|
| NBR 13133:2021 | Execução de levantamento topográfico — métodos, instrumentos, classes de precisão (substitui a edição de 1994) | Paga (ABNT) | Vigente — edição 2021 confirmada por múltiplas fontes |
| Lei nº 10.267/2001 + Decreto nº 4.449/2002 | Cadastro Nacional de Imóveis Rurais; georreferenciamento obrigatório de limites | Gratuita (legislação federal) | Vigente |
| NTGIR — Norma Técnica para Georreferenciamento de Imóveis Rurais, INCRA, 3ª ed. (2013) | Procedimento e precisão posicional para georreferenciamento rural (base do SIGEF) | Gratuita (INCRA/SIGEF) | Vigente — 3ª edição confirmada; **a confirmar** se há edição/errata posterior a 2013 ainda não localizada nesta pesquisa |
| Resolução do Presidente do IBGE nº 1/2005 | Adota SIRGAS2000 como referencial do SGB/SCN | Gratuita (IBGE) | Vigente |
| Resolução do Presidente do IBGE nº 1/2015 | Encerra período de transição — SIRGAS2000 como único referencial planimétrico desde 2015 | Gratuita (IBGE) | Vigente |
| Decreto nº 89.817/1984 | PEC — Padrão de Exatidão Cartográfica (classes por escala) | Gratuita (legislação) | Vigente |
| NBR 14166 (1998; "versão corrigida" 2022) | Rede de Referência Cadastral Municipal — requisitos e procedimento | Paga (ABNT) | **Status conflitante entre fontes consultadas** — pelo menos um catálogo indica cancelamento da versão 01/2022; outro cita normalização vigente. Número/existência da norma confirmados; **vigência atual a confirmar diretamente na ABNT antes de citar em memorial** |
| RBAC 100 (ANAC, Resolução ANAC nº 805) | Operação de aeronaves não tripuladas (RPA/drone), inclui uso para aerolevantamento | Gratuita (ANAC) | Vigente desde 16/06/2026, substituiu RBAC-E nº 94/2017 — **a confirmar** eventuais disposições transitórias residuais |
| RBMC (rede de estações IBGE) | Infraestrutura de referência GNSS ativa para RTK/pós-processamento | Gratuita (IBGE) | Vigente — rede operacional, sem número de norma único (é infraestrutura, não norma) |

## Cálculos e métodos padrão

### Altitude ortométrica a partir de GNSS
- H = h − N, onde h é a altitude elipsoidal medida por GNSS e N é a
  ondulação geoidal do modelo oficial do IBGE (MAPGEO).
- Red flag: usar h bruto do receptor GNSS como cota de projeto sem
  aplicar N — gera erro sistemático que pode chegar à ordem de metros
  dependendo da região do país; sempre declarar o modelo geoidal e a
  versão usados no relatório.

### Precisão posicional de vértice em georreferenciamento rural (NTGIR)
- Limite artificial (cerca, marco, linha reta definida): precisão
  posicional ≤ 0,50 m.
- Limite natural (curso d'água, divisor de águas): precisão
  posicional ≤ 3,00 m.
- Limite inacessível: precisão posicional ≤ 7,50 m.
- Red flag: memorial descritivo com vértice fora da tolerância da sua
  categoria, sem justificativa técnica documentada — bloqueia a
  certificação no SIGEF/INCRA e invalida a matrícula pretendida.

### Padrão de Exatidão Cartográfica (PEC) — Decreto 89.817/1984
- Erro-padrão planimétrico: EP = 0,3 mm × escala do mapa.
- PEC (90% de probabilidade) = 1,6449 × EP.
- PEC altimétrico = metade da equidistância entre curvas de nível.
- Red flag: produto cartográfico entregue sem declaração de classe/
  escala de exatidão associada — não é auditável e não deve ser aceito
  como insumo de projeto sem essa informação.

### Erro de fechamento de poligonal topográfica (NBR 13133)
- Cada classe de poligonal (IP a VP) define equipamento mínimo,
  método de leitura angular e distância mínima entre vértices; a
  tolerância de fechamento angular e linear varia por classe e pela
  finalidade do levantamento.
- **A confirmar antes de uso em memorial**: os valores numéricos
  exatos de tolerância linear/angular por classe não foram extraídos
  do texto integral da NBR 13133:2021 nesta sessão (norma paga, não
  acessada na íntegra) — citar apenas após conferência do texto
  oficial adquirido junto à ABNT.
- Red flag: compensação de poligonal aplicada sem verificar
  previamente se o erro de fechamento está dentro da tolerância da
  classe declarada — mascara erro grosseiro de campo.

## Segmentos onde D21 aparece

| Segmento | Peso | Exemplo típico |
|---|---|---|
| S1 Rodovias | Alto | Levantamento planialtimétrico do eixo, cadastro de faixa de domínio, apoio a terraplenagem |
| S3 Ferrovia | Alto | Georreferenciamento de faixa de domínio ferroviária, perfil longitudinal de via permanente |
| S5 Imobiliário | Alto | Georreferenciamento de imóvel rural/urbano para due diligence fundiária e desapropriação |
| S2 OAE | Médio | Implantação de eixo e gabarito de pontes/viadutos, monitoramento topográfico de obra |
| S4 Metrô | Médio | Rede de apoio superficial para transporte de coordenadas a poços/estações, controle de recalque |
| S12 Túneis | Médio | Transporte de coordenadas de superfície para portais e eixo de escavação (interface com D22) |
| S9 Saneamento | Baixo | Cadastro georreferenciado de redes e adutoras |
| S10 Energia | Baixo | Levantamento de faixa de servidão de linha de transmissão |
| S11 Barragens | Baixo | Apoio topográfico para monitoramento geodésico de deslocamento de barragem |

## Cruzamentos S.A.D típicos

- S1.A2.D21 — levantamento planialtimétrico do eixo + cadastro de
  faixa de domínio para quantidades de desapropriação.
- S3.A2.D21 — georreferenciamento de faixa ferroviária para orçamento
  de desapropriação e via permanente.
- S1.A1.D21 — escopo e custo de levantamento de apoio geodésico em
  proposta técnica/EVTE.
- S2.A11.D21 — monitoramento topográfico de obra (fiscalização,
  controle de deslocamento de OAE em execução).
- S12.A2.D21 — implantação de portais e eixo de túnel (transporte de
  coordenadas, interface direta com D22).
- S5.A9.D21 — certificação de limites junto ao INCRA/SIGEF em
  regularização fundiária (componente regulatório).

## Handoffs

| Para | Quando | Formato de entrega |
|---|---|---|
| D03 Geotecnia | Pontos de sondagem/investigação precisam de coordenadas SIRGAS2000 certificadas | Planilha de coordenadas (E, N, h) + relatório de precisão |
| D22 Túneis | Transporte de coordenadas de superfície para portal/eixo de escavação subterrânea | Relatório de transporte de coordenadas + tolerância de fechamento atingida |
| manta-05 (orçamento) | Quantidades de levantamento/cadastro para composição de custo e desapropriação | Memória de cálculo + shapefile/DXF |
| manta-06 (modelagem) | Superfície de terreno (MDT/TIN) para modelo BIM/Civil 3D | LandXML, nuvem de pontos (LAS/LAZ) |
| agente-infraestrutura S1/S3 | Eixo geométrico definido, apoio para projeto geométrico de traçado | Caderneta de campo/RN, poligonal ajustada |
| imobiliario (Manta 04) | Certificação de limites em due diligence fundiária (S5) | Memorial descritivo + planta georreferenciada (SIGEF) |

## Skills L1 consumidas

- `autodesk-toolkit` — leitura/geração de superfícies de terreno
  (LandXML), coordenadas de projeto e arquivos DXF/DWG sem depender de
  Civil 3D instalado; camada compartilhada relevante para o insumo
  topográfico de rodovias, OAE, metrô e ferrovia.
- Nenhuma skill dedicada a processamento GNSS/fotogrametria/LiDAR foi
  localizada no catálogo atual — item de backlog a avaliar junto ao
  arquiteto-ia (Manta 16) se houver demanda recorrente.

## Casos-âncora

Nenhum caso-âncora registrado ainda — a popular conforme os primeiros
projetos que consumirem esta disciplina.

## NÃO faz

- Não substitui ART/RRT de profissional habilitado (engenheiro
  agrimensor/cartógrafo) responsável por levantamento e memorial
  assinado.
- Não executa a submissão/certificação de limites junto ao INCRA/SIGEF
  — isso é ato do profissional credenciado no sistema, não do agente.
- Não opera aeronave remotamente pilotada (RPA) — depende de piloto/
  operador habilitado conforme regulamento ANAC vigente (RBAC 100).
- Não substitui perícia judicial em disputa de limites — apoia com
  dado técnico, não emite laudo pericial.
- Não define o sistema de referência de um projeto por conta própria
  quando há exigência contratual de sistema local/legado — confirmar
  com o cliente antes de fixar SIRGAS2000 como único referencial de
  entrega.

## Palavras-chave de roteamento

georreferenciamento, geodésia, topografia, SIRGAS2000, SAD69, GNSS,
RTK, RBMC, poligonal, nivelamento, estação total, LiDAR, drone, RPA,
aerofotogrametria, ortofoto, MDT, cadastro, INCRA, SIGEF, NTGIR, PEC,
padrão de exatidão cartográfica, NBR 13133, NBR 14166, faixa de
domínio, levantamento planialtimétrico, rede de referência cadastral
municipal, transporte de coordenadas
