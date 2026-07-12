# refs/routing-table-v4.6.md — manta-maestro

Tabela expandida de roteamento **palavra-chave → segmento** (S1..S14),
extraída do §6.1 do `SKILL.md` v4.6. Determinística — casa o termo
literal no pedido do usuário. Se nada casar, cai no fallback §6.4
(F1.c Learned Router → F1.b RAG hybrid → Q1 humano).

Convenções:
- Match é case-insensitive; acentos são tolerados.
- Match parcial em palavra composta (ex.: "geradorETE" bate "ETE").
- Prioridade cai para o segmento com MAIS termos casados; em empate,
  o segmento de menor índice ganha.

---

## S1 — Rodovias

rodovia, asfalto, concessão rodoviária, BR-XXX, DNIT, DER, CBUQ,
BGS, SICRO

## S2 — OAE (pontes, viadutos)

ponte, viaduto, obra de arte, OAE, NBR 7187, longarina, bloco
coroamento

## S3 — Ferrovia

trem, trilho, AMV, ferroviário, FEC, Ferrograo, Vale, MRS

## S4 — Metrô

metrô, estação, PSD, Linha 4, Linha 5, NATM metroviário

## S5 — Imobiliário

incorporação, imóvel, lançamento, VGV, SCP, permuta, landbank

## S6 — Edificações

hospital, industrial, edifício corporativo, comercial, MCMV,
NBR 15575, LEED

## S7 — Portos

porto, terminal marítimo, TUP, ANTAQ, dragagem, molhe, quebra-mar,
dolfin, berço, cais, calado, contêiner, granel, PIANC, hidrovia,
retroárea, defensa

## S8 — Aeroportos

aeroporto, pista pouso, ANAC, ICAO, Annex 14, RBAC 154, TPS, TECA,
balizamento, PAPI, ILS, PCN, FAARFIELD, jetway, concessão
aeroportuária

## S9 — Saneamento (PRIORIDADE AySA)

saneamento, ETA, ETE, adutora, esgoto, AySA, drenagem urbana,
macrodrenagem, SNIS, PMSB, Lei 14.026, subsídio cruzado, elevatória,
UASB, MBR

## S10 — Energia (ANEEL/State Grid)

transmissão, LT, subestação, ANEEL, RAP, leilão transmissão, ONS,
EPE, PDE, ACSR, torre estaiada, HVDC, R1-R5 EPE, geração eólica, PV,
PCH, UHE

## S11 — Barragens

barragem, vertedouro, CFRD, CCR, RCC, rejeitos, TSF, PNSB, ICOLD,
CBDB, Lei 12.334, Lei 14.066, Fundão, Brumadinho, PAEBM, ZAS, ZSS,
HHP, alteamento a montante, alteamento a jusante, alteamento por
linha de centro

## S12 — Túneis

túnel, NATM, TBM, EPB, slurry, hard rock, cut and cover, imerso,
ITT, dovela, shotcrete, cambota, jet fan, ventilação longitudinal,
PIARC, ITA, NFPA 502, convergência, Peck

## S13 — Mineração

mineração, mina, minério, ANM, DNPM, NRM, NR-22, cava, open pit,
subterrânea, block caving, SME, CIM, JORC, NI 43-101, PERC, LOM,
moagem SAG, ball mill, flotação, ANFO, heap leach, CIL, CIP,
Vale Carajás, Salobo, pellet plant, mine-to-port

## S14 — Óleo & Gás

petróleo, óleo e gás, ANP, Petrobras, refinaria, Comperj, Rnest,
Replan, Reduc, Rlam, gasoduto, oleoduto, GASBOL, Rota 3, Rota 4,
API 650, API 5L, API 653, ANSI B31, NFPA 30, NFPA 59A, IEC 61511,
HAZOP, SIL, LOPA, RBI, HDD, land-fall, city gate, LNG, GNL, FCC,
HDT, DCU, UPGN, tanque teto flutuante, pipe-rack, área classificada,
PSM

---

## Reconciliação com Codex-exemplo (numeração dupla)

| Codex `03-Sn` | Segmento | Maestro operacional `Sn` |
|---|---|---|
| 03-S1  | Rodovias    | S1  |
| 03-S2  | OAE         | S2  |
| 03-S3  | Ferrovia    | S3  |
| 03-S4  | Metrô       | S4  |
| 03-S5  | **Túneis**  | **S12** |
| 03-S6  | Portos      | S7  |
| 03-S7  | Aeroportos  | S8  |
| 03-S8  | Saneamento  | S9  |
| 03-S9  | Energia     | S10 |
| 03-S10 | Barragens   | S11 |
| 03-S11 | Mineração   | S13 |
| 03-S12 | Óleo & Gás  | S14 |
| 03-S13 | Edificações | S6 (não renumera — reusa S6 existente) |

---

## Ver também

- `SKILL.md` §6 — regras completas de roteamento + fallback
- `SKILL.md` §3.1 — mapa completo dos 14 segmentos
- `handoffs-cross-agent.md` — como o Maestro coordena múltiplos S
