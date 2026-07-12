# agente-oleo-gas (Manta 03-S12)

Agente vertical de engenharia CIVIL e de INFRAESTRUTURA do setor de
óleo & gás — upstream de superfície, midstream de dutovias, downstream
de refino e terminais/armazenagem.

**Fora do escopo Manta**: engenharia de reservatório, perfuração,
completação e geologia de subsuperfície — encaminhar. Este agente foca
no que a Manta entrega: obras civis, tancagem, pipe-rack, dutovias,
terminais, city gates.

## Estrutura desta pasta

```
agente-oleo-gas/
├── SKILL.md         # definição canônica (5 segmentos: U/Md/R/T/M)
├── README.md        # este arquivo
├── refs/
│   └── README.md    # bibliografia (ANP, API, ANSI B31, NFPA, IEC, OSHA)
└── prompts/
    └── starters.md  # 10 starters por segmento e fase
```

## Quando usar

Palavras-chave: **petróleo, óleo e gás, o&g, ANP, Petrobras, Braskem,
GASBOL, Rota 3, Rota 4, GASENE, gasoduto, oleoduto, poliduto, refino,
refinaria, Comperj, Rnest, Replan, Reduc, Rlam, Regap, UPGN, FCC, HDT,
UCR, coqueamento, tancagem, tanque teto flutuante, esfera GLP, API 650,
API 653, API 5L, ANSI B31.3/4/8, monoboia, PLEM, PLET, HAZOP, SIL, LOPA,
RBI, NFPA 30, NFPA 59A, IEC 60079, IEC 61511, PSM, city gate, terminal
aquaviário, LNG, GNL**.

## Casos de uso típicos

- **Downstream**: DD de refinaria em desinvestimento ANP (Refap, Regap,
  Repar); review de FCC/HDT/UCR; fundação de coluna de destilação a
  vácuo 65m; pipe-rack para expansão de UPGN.
- **Tancagem**: dimensionamento de tanque teto flutuante API 650 para
  gasolina, esfera GLP, teto fixo para óleo combustível; bacia de
  contenção 110% + chuva projeto + foam NFPA 30.
- **Midstream — dutos**: traçado de gasoduto com faixa de servidão
  (ANP 858), travessia HDD sob rio/rodovia, city gate para
  termoelétrica, estação de compressão booster.
- **Terminais**: TA (parte civil das ilhas de tancagem + utilities),
  TERCA, ilhas de carregamento top/bottom loading, sistema de blending.
- **Segurança de processo**: leitura de HAZOP worksheets, gap analysis
  SIL/LOPA (IEC 61511), grade de áreas classificadas (IEC 60079 Zone
  0/1/2 × API RP 500 Class I Div 1/2), NFPA 30/59A.
- **Integridade**: RBI (API 580/581) de tancagem envelhecida,
  inspeção de tanque API 653, ILI de duto (smart pigging).
- **Descomissionamento**: refinaria pequena, terminal desmobilizado,
  remediação de área contaminada.

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Contrato EPC/EPCM turnkey | `agente-contratual` |
| Modelo financeiro CAPEX × EBITDA / DD de refinaria | `agente-advisory` |
| Edital ANP de desinvestimento / RFP EPC | `agente-bd` |
| Terminal aquaviário — parte marítima (cais, dolfin, monoboia, quebra-mar) | `agente-portos` (S6) |
| LT + subestação dedicada, cogeração a gás | `agente-energia` (S9) |
| ETE de água produzida oleosa (SAO/DAF) | `agente-saneamento` (S8) |
| Rodovia de acesso à refinaria / via interna | `agente-infraestrutura S1` |
| Torre de destilação como OAE especial / viaduto sobre duto | `agente-infraestrutura S2` |
| Ramal ferroviário de derivados | `agente-infraestrutura S3` |
| Travessia de duto por microtúnel / túnel dedicado | `agente-tuneis` (S5) |
| Bacia de contenção grande porte / barragem de rejeitos petroquímicos | `agente-barragens` (S10) |
| **Reservatório, poço, perfuração, completação, geologia** | **FORA DE ESCOPO — não atendemos** |
| **Simulação de processo (HYSYS/PIPESIM/PHAST)** | **FORA DE ESCOPO — consultor externo** |

## Onboarding

1. Ler o `SKILL.md` completo — atentar ao intake com **5 segmentos**
   U/Md/R/T/M e ao gate de escopo (reservatório/poço = fora).
2. Consultar `refs/README.md` para ANP + API + ANSI B31 + NFPA + IEC
   + OSHA + bibliografia.
3. Testar com um dos `prompts/starters.md`.
4. Salvar como caso em `ogs:cases:CASE-OGS-NNN` (sub `ogs:u:`
   upstream, `ogs:m:` midstream, `ogs:r:` refino, `ogs:t:` terminal).
