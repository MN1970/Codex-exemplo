# prompts/starters.md — agente-oleo-gas

## 1. Downstream — DD de terminal de derivados

- "Rodando DD de um terminal de derivados no litoral norte-SP (150
  mil m³ tancagem, oleoduto de 12" para retaguarda). Preciso de um
  diagnóstico civil + integridade em 15 dias — parte marítima está
  com agente-portos, e a ETE de água oleosa com agente-saneamento.
  Como estruturamos o pacote?"

## 2. Tancagem — dimensionamento API 650 teto flutuante

- "Tanque de gasolina 30.000 m³, Ø 45m, altura 20m. Pode revisar meu
  dimensionamento API 650 (chapa, ligação, fundação anelar), com
  verificação sísmica (Anexo E) para zona sísmica NBR 15421-2 e
  vento NBR 6123 (V0 = 45 m/s)? Bacia de contenção precisa cobrir
  110% do maior tanque + chuva 10 anos + foam NFPA 30."

## 3. Refino — review de HAZOP de FCC

- "Recebi as worksheets de HAZOP da unidade de FCC (Craqueamento
  Catalítico Fluidizado) da Refinaria X — 42 nós, 380 recomendações.
  Preciso de gap analysis SIL (IEC 61511) das SIFs críticas e LOPA
  das top-10 consequências (fogo/explosão/tóxico). Manta não facilita
  o HAZOP, só apoia leitura + gap — confirme os limites e me diga
  quais nós carecem de facilitador certificado."

## 4. Midstream — gasoduto com travessia HDD

- "Gasoduto 20" MOP 100 bar, 85 km, atravessando 3 rios (150, 380 e
  520m) e a BR-101. Preciso do estudo de traçado + faixa de
  servidão ANP 858 + matriz travessia (HDD × bridge × trenching)
  por obstáculo. Base API 5L X70, ANSI B31.8. Espessura por
  t=P·D/(2·S·E·F·T) — pode conferir?"

## 5. City gate — para termoelétrica

- "City gate para termoelétrica 500 MW a gás natural: chega em 50
  bar do troncal, precisa reduzir para 25 bar + odorização (só se
  for para consumo residencial, aqui não é) + medição fiscal ANP.
  Layout do skid, áreas classificadas Zone 1/2 (IEC 60079-10-1),
  distanciamento à turbina — pode montar o plot plan mínimo?"

## 6. Downstream — fundação de coluna 65m destilação a vácuo

- "Coluna de destilação a vácuo Ø 8m, altura 65m, peso operante
  1.200 ton, sismo NBR 15421 zona 2, vento NBR 6123 V0=40 m/s.
  Fundação em sapata + 24 estacas raiz Ø 400mm. Sondagem indica
  areia média + fragmento de rocha alterada a partir de 12m.
  Verificação NBR 6122 + API 4F — pode conferir dimensionamento
  e me dizer se o bloco maciço passa em vibração da coluna?"

## 7. Tancagem — bacia de contenção + foam NFPA 30

- "Ilha de 6 tanques teto flutuante gasolina + nafta (Ø 30m, altura
  18m cada, ~11.500 m³ nominal). Preciso dimensionar bacia de
  contenção (110% do maior + chuva projeto 25 anos), espaçamento
  API 2610, distância a limite de propriedade, câmara de espuma
  NFPA 30 (top pourer + subsurface), sistema deluge de resfriamento
  em tanque adjacente pegando fogo. Portaria ANP 32."

## 8. Integridade — RBI API 580 de tancagem envelhecida

- "Terminal de 25 tanques com 30+ anos de operação. Diligência de
  M&A pediu inspeção RBI API 580/581 + inspeção interna API 653 do
  bottom (magnetic flux leakage) das 8 unidades priorizadas.
  Preciso de: (i) matriz risco = PoF × CoF por tanque, (ii)
  intervalo ótimo de inspeção, (iii) budget de reparo estimado.
  Base histórica UT thickness disponível."

## 9. Descomissionamento — refinaria pequena

- "Refinaria regional de 30 mil bpd em desativação: 42 tanques, 3
  fornos, 8 km de tubulação intraplanta, 2 UPGN pequenas. Plano de
  descomissionamento: (i) inertização/purga N2, (ii) limpeza
  química, (iii) desativação e desmobilização, (iv) plano de
  remediação de área contaminada (TPH, BTEX). Estimar CAPEX de
  desmobilização + prazo + escopo do handoff para agente-advisory
  (valor residual do ativo)."

## 10. Pipe-rack — expansão de UPGN

- "UPGN existente com pipe-rack de 3 níveis (utilities, processo,
  E&I) precisa de expansão para nova linha de C3+. Alturas 6/9/12m,
  vão 8m entre columns, 42 novas linhas Ø 2-24". Cargas: térmica
  (dilatação por CAESAR II), vento NBR 6123, sismo. Fundação
  existente comporta carga adicional? Áreas classificadas Zone 1
  na cota de operação — como recompor a grade IEC 60079?"

## Handoffs comuns nesses starters

- Starter 1 → **agente-portos** (parte marítima do TA),
  **agente-saneamento** (ETE óleo), **agente-advisory** (DD financeiro).
- Starter 3 → HAZOP facilitação **NÃO** é escopo Manta (consultor
  certificado); gap analysis SIL/LOPA é escopo aqui.
- Starter 4 → **agente-contratual** para servidão administrativa,
  **agente-tuneis (S5)** se optar por microtúnel numa travessia grande.
- Starter 5 → **agente-energia (S9)** para LT/SE da termoelétrica.
- Starter 8 → **agente-advisory** para valuation pós-RBI.
- Starter 9 → **agente-advisory** para valor residual,
  **agente-saneamento** para remediação ambiental.
