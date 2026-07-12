# Drenagem — Checklist SAP padrao (A2 Levantamento de Quantidades)

Referencia: DNIT IPR-724 + NBR 15645 + PMSP IE-SO. Aplicado ao intake
A2 de projetos com componente de drenagem (rodovia + sistema viario
urbano). Consumido por `BriefingGenerator._load_checklist_items("drenagem")`.

Backend de extracao: `backends/drenagem/` (novo, Agente B da sprint).

## Lista base (25 itens)

| SAP           | Descricao                                       | Unidade | Faixa tipica              | Flag se ausente | Norma          |
|---------------|-------------------------------------------------|---------|---------------------------|-----------------|----------------|
| SICRO5013010  | BSTC 2x1.00 x 1.00 m (bueiro simples)          | m       | trecho x qtd celulas      | esperado        | DNIT ES-034/17 |
| SICRO5013012  | BSTC 3x1.20 x 1.20 m (bueiro triplo)           | m       | trecho x qtd celulas      | condicional     | DNIT ES-034/17 |
| SICRO5013020  | BSCC circular Ø 1000 mm                         | m       | comp linear               | esperado        | NBR 15645      |
| SICRO5013022  | BSCC circular Ø 1200 mm                         | m       | comp linear               | opcional        | NBR 15645      |
| SICRO5013024  | BSCC circular Ø 1500 mm                         | m       | comp linear               | condicional     | NBR 15645      |
| SICRO5013030  | Sarjeta SBC (baldrame simples concreto)         | m       | ext borda pista           | esperado        | DNIT IPR-724   |
| SICRO5013032  | Sarjeta SBV (bordao vazado)                     | m       | ext borda pista urbano    | condicional     | PMSP IE-SO     |
| SICRO5013034  | Sarjeta STC (trapezoidal concreto)              | m       | ext borda pista           | esperado        | DNIT IPR-724   |
| SICRO5013040  | Meio-fio MFC-01 (chapeu de bispo)               | m       | borda pista urbana        | esperado        | DER-SP IP-DE-D00 |
| SICRO5013042  | Meio-fio MFC-02 (rampa acessivel)               | m       | borda em travessias       | condicional     | NBR 9050       |
| SICRO5013050  | Valeta VT-01 escavada em solo                   | m       | ext borda faixa           | condicional     | DNIT IPR-724   |
| SICRO5013052  | Valeta VT-02 revestida concreto                 | m       | trecho declividade > 5%   | esperado        | DNIT IPR-724   |
| SICRO5013054  | Valeta VT-03 pedra argamassada                  | m       | opcao para VT-02          | opcional        | DNIT IPR-724   |
| SICRO5013056  | Valeta VT-04 grama                              | m       | trecho canteiro central   | opcional        | DNIT IPR-724   |
| SICRO5013058  | Valeta VT-05 pre-moldada concreto               | m       | canteiro central urbano   | opcional        | PMSP IE-SO     |
| SICRO5013060  | Boca-de-lobo simples grelha ferro fundido       | un      | 1 a cada 40-60m sarjeta   | esperado        | PMSP IE-SO     |
| SICRO5013062  | Boca-de-lobo dupla                              | un      | 1 a cada 30m em urbano    | condicional     | PMSP IE-SO     |
| SICRO5013064  | Boca-de-lobo tripla                             | un      | so em confluencias        | opcional        | PMSP IE-SO     |
| SICRO5013070  | Poco de visita PV-01 (Ø 0.60 m ate 1.5 m prof)  | un      | 1 a cada 60-80m           | esperado        | NBR 12266      |
| SICRO5013072  | Poco de visita PV-02 (Ø 1.20 m ate 3 m prof)    | un      | PV profundo               | condicional     | NBR 12266      |
| SICRO5013080  | Descida d'agua DA-01 rampa concreto             | un      | 1 por talude/aterro       | esperado        | DNIT IPR-724   |
| SICRO5013082  | Canaleta CAN longitudinal                       | m       | topo aterro/talude        | esperado        | DNIT IPR-724   |
| SICRO5013090  | Dreno cego (subterraneo)                        | m       | trecho de nascente        | opcional        | DNIT IPR-724   |
| SICRO5013092  | Tubo dreno PVC Ø 100 mm perfurado               | m       | subdrenagem pavimento     | esperado        | NBR 15645      |
| SICRO5013094  | Filtro geotextil OP-90 (bidim 200 g/m2)         | m2      | envolope tubo dreno       | esperado        | NBR 15229      |

## Regras de consistencia (consist-guard)

- vazao_PV_jusante >= vazao_PV_montante (error se contrario — inversao de fluxo)
- diametro_BSTC coerente com area de contribuicao (metodo racional Q=CIA)
- espacamento_BocaDeLobo: 40-60 m em sarjeta rural, 30 m em urbano (warn fora)
- espacamento_PV: 60-80 m em coletor tronco (warn fora)
- comprimento_sarjeta ~ 2 x comprimento_pista (2 bordas — warn se ratio < 1.8 ou > 2.2)
- Boca-de-lobo sem PV a montante em 100m: error (sistema sem convergencia)
- Filtro geotextil area >= 2 x (comp x Ø) do tubo dreno (envolope minimo)
- Meio-fio MFC-01 e sarjeta SBC devem ter comp coerente (par arquitetonico)

## Discovery hints

- Layers convencao DNIT/DER-SP:
  - `DRE-*` — linhas de drenagem
  - `PV-*` — pocos de visita
  - `BSTC-*`/`BSCC-*` — bueiros
  - `SBC|SBV|STC` — sarjetas por tipo
  - `VT-01..VT-05` — valetas por tipo
  - `MFC-01|MFC-02` — meio-fios
- MTEXT patterns:
  - `BSTC\s+(\d+)x(\d+)\.?(\d+)?\s*x\s*(\d+)\.?(\d+)?\s*m` (celulas)
  - `Ø\s*(\d+)\s*mm` (diametro nominal)
  - `L\s*=\s*(\d+)(?:\.|,)?(\d+)?\s*m` (comprimento)
- Cotas de fundo em textos ancoradas nas linhas de drenagem
- Sondagem geotecnica (`backends/sondagem`) — dado de entrada para
  verificar viabilidade de PVs profundos e drenos.

## Ver tambem

- `drenagem-checklist-sap.md` alimenta `BriefingGenerator._load_checklist_items("drenagem")`
- Backend novo do Agente B (drenagem) — implementacao paralela
- SKILL.md master §14.2.1
