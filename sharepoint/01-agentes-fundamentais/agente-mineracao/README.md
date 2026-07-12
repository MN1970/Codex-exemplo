# agente-mineracao (Manta 03-S11)

Agente vertical de mineração — todas as tipologias de mina (open pit,
subterrânea, aluvionar, dragagem) e commodities (ferro, cobre, ouro,
bauxita, níquel, manganês, fosfato, potássio, calcário, zinco/chumbo,
nióbio). Cobre exploração, modelagem geológica, recursos & reservas,
planejamento de lavra, geotecnia de cava, desmonte, frota,
beneficiamento, hidrometalurgia, infraestrutura de suporte, fechamento
e mine-to-port.

## Fronteira crítica com S10 (barragens)

**Este agente NÃO cobre barragens de rejeitos.** Qualquer pergunta
sobre TSF, alteamento (montante/jusante/linha de centro), dry stack /
filtragem de rejeitos, dam breach, PAE/PAEBM, ZAS/ZSS,
descaracterização de barragem, ANM Res. 95/2022, ICOLD Bulletin 194,
CBDB → **encaminhar imediatamente para `agente-barragens` (Manta
03-S10)**.

O que este agente cobre em rejeitos: apenas o **planejamento upstream**
(volume anual gerado, granulometria, densidade in-situ, water balance
de processo, teor residual). A partir do momento em que o rejeito chega
à estrutura de disposição, é S10.

## Estrutura desta pasta

```
agente-mineracao/
├── SKILL.md         # definição canônica (intake por tipologia + commodity + fase)
├── README.md        # este arquivo
├── refs/
│   └── README.md    # bibliografia (ANM, NRM, NR-22, CBRR, CIM, JORC, SEC K-1300)
└── prompts/
    └── starters.md  # 10 starters cobrindo cava, planta, hidromet, DD e fechamento
```

## Quando usar

Palavras-chave: **mineração, mineracao, mina, minério, minerio, ANM,
DNPM, NI 43-101, JORC, PERC, SEC K-1300, CBRR, cava, open pit,
subterrânea, block caving, sub-level stoping, room-and-pillar,
cut-and-fill, moagem SAG, ball mill, HPGR, flotação, gravimetria,
pellet plant, ANFO, emulsão, heap leach, CIL, CIP, HPAL, SX-EW, LOM,
LHD, SMU, cut-off, push-back, minério de ferro, cobre, ouro, bauxita,
níquel laterítico, manganês, fosfato, potássio, calcário, zinco,
chumbo, nióbio, Vale, Anglo American, CSN Mineração, Kinross, Yamana,
Nexa, CBMM, MRN, Carajás, Salobo, Sossego, Minas Rio, Paracatu,
Chapada, Trombetas, Vazante, Cajati, Whittle, Datamine, Micromine,
Vulcan, Leapfrog, Deswik, MineSight, JKSimMet, NRM, NR-22, CFEM,
SIGMINE**.

## Casos de uso típicos

- **Open pit / céu aberto**: cava econômica Whittle, push-back,
  sequenciamento LOM 10–30 anos, ângulo de talude por setor
  geotécnico, monitoramento SSR/InSAR, blending de teor.
- **Subterrânea**: sub-level stoping (Nexa Vazante, Vale Voisey),
  block caving / sub-level caving (baixo teor grande volume),
  room-and-pillar (calcário, potássio), cut-and-fill (veios estreitos
  ouro).
- **Beneficiamento**: britagem primária/secundária/terciária, moagem
  SAG + ball / HPGR, flotação (rougher/scavenger/cleaner, coluna),
  gravimetria (jigues, espirais, Knelson), separação magnética
  (LIMS/WHIMS), separação eletrostática.
- **Hidrometalurgia**: heap leaching (ouro CN⁻, cobre H₂SO₄), CIL/CIP
  (ouro), HPAL (níquel laterítico Vale Onça Puma), SX-EW (cobre
  catódico), Merrill-Crowe.
- **Pelotização**: Grate-Kiln, Traveling Grate; teor Fe > 66 %,
  15 % da produção mundial no BR (Vale, CSN, Samarco pós-retomada).
- **Fechamento e descomissionamento**: PRAD, PFM, capping de PDE
  (pilha de estéril), revegetação, monitoramento pós-fechamento (10–
  30 anos), passivo ambiental. **TSF → S10**.
- **DD técnico para M&A**: relatório NI 43-101 (TSX), SEC K-1300
  (Nasdaq/NYSE), JORC 2012 (ASX), CBRR (BR).
- **Mine-to-port**: correia overland (Carajás S11D, Minas Rio
  mineroduto), ferrovia dedicada (EFC, EFVM, malha norte), terminal
  mineiro (Ponta da Madeira, Tubarão, Guaíba, Açu).

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| **QUALQUER tema TSF / barragem de rejeitos / dry stack** | **`agente-barragens (S10)` — OBRIGATÓRIO** |
| LT dedicada + subestação principal + PPA | `agente-energia (S9)` |
| ETA/ETE canteiro + adução industrial + drenagem ácida (ARD) | `agente-saneamento (S8)` |
| Terminal portuário mineiro (Ponta da Madeira, Tubarão, Açu) | `agente-portos (S6)` |
| Ferrovia mine-to-port (EFC, EFVM, malha norte) | `agente-infraestrutura S3` |
| Rodovia de acesso e escoamento à mina | `agente-infraestrutura S1` |
| Ponte / viaduto / correia elevada sobre a cava | `agente-infraestrutura S2` |
| Contrato EPC/EPCM planta + contract mining + leasing frota | `agente-contratual (Manta 02)` |
| Modelo financeiro NPV/IRR, DD M&A, valuation | `agente-advisory (Manta 15)` |
| Pleito imprevisto geotécnico em desenvolvimento UG | `agente-contratual (V6 Claims / Manta 01)` |
| Edital ANM de outorga / leilão de área | `agente-bd (Manta 13)` |
| BIM 3D + FEM cava (PLAXIS 3D, FLAC 3D) | `agente-modelagem (Manta 06)` |
| Cronograma sequenciamento lavra + CAPEX faseado + ramp-up | `agente-cronograma (Manta 07)` |
| Quantitativos (US$/BCM movido, US$/t processada) | `agente-orcamento (Manta 05)` |

## Onboarding

1. Ler o `SKILL.md` completo — atenção à **regra Q0** (se for TSF,
   reencaminhar S10 antes de responder).
2. Consultar `refs/README.md` para NRM/CBRR/CIM/JORC/SEC K-1300 e
   softwares (Whittle, Datamine, Vulcan, Leapfrog, Deswik).
3. Testar com um dos `prompts/starters.md`.
4. Salvar como caso em `min:cases:CASE-MIN-NNN` (sub `min:o:` open
   pit, `min:u:` subterrânea, `min:b:` beneficiamento, `min:h:`
   hidrometalurgia, `min:f:` fechamento).

## Fronteira operacional entre S11 e S10

Regra de bolso: **se o material está sendo LAVRADO, é S11. Se está
sendo DISPOSTO em barragem, é S10.**

| Assunto | Agente |
|---|---|
| Balanço de água de processo (mina + planta) | S11 |
| Water balance de reservatório de rejeitos | S10 |
| Volume anual de rejeito gerado | S11 |
| Curva de alteamento da TSF | S10 |
| Filtragem de rejeitos (dewatering na planta) | S11 |
| Dry stack (pilha de rejeito filtrado) | S10 |
| Descomissionamento de PDE (pilha de estéril) | S11 |
| Descaracterização de barragem a montante | S10 |
| Drenagem ácida (DAM/ARD) na mina e planta | S11 (com apoio S8) |
| Dam breach analysis + PAE/PAEBM | S10 |
