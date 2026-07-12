# agente-energia (Manta 03-S9)

Agente vertical do setor elétrico brasileiro, com foco em **transmissão
(ANEEL/State Grid)** e cobertura de geração (hidro, eólica, solar,
térmica) e distribuição.

## Estrutura desta pasta

```
agente-energia/
├── SKILL.md         # definição canônica (7 segmentos: T/D/Gh/Ge/Gs/Gt/M)
├── README.md        # este arquivo
├── refs/
│   └── README.md    # bibliografia (ANEEL, EPE R1-R5, ONS, IEEE, IEC)
└── prompts/
    └── starters.md  # 20 starters por segmento e fase
```

## Quando usar

Palavras-chave: **transmissão, LT, subestação, ANEEL, RAP, leilão
transmissão, ONS, EPE, PDE, R1-R5, torre estaiada, cabo condutor,
ACSR, CAA, ATSR, MRE, ACR, ACL, WEG, State Grid, ISA CTEEP, Alupar,
Taesa, geração eólica, PV, hidráulica, PCH, UHE**.

## Casos de uso típicos

- **Transmissão** (prioridade): LT 138/230/345/440/500/750 kV +
  subestações associadas. Estudo de leilão ANEEL (menor RAP).
- **Distribuição**: MT/BT, transformadores, religadores, chaves
  telecomandadas.
- **Geração**: UHE (barragem + turbina + casa de força + LT),
  PCH, eólica (onshore/offshore), solar PV utility/DG, térmica.
- Estudos de sistema: fluxo de potência (ANATEM/ANAREDE),
  curto-circuito, estabilidade transitória.
- Ampacidade IEEE Std 738, malha de aterramento IEEE Std 80.
- Cronograma com **milestones RAP** (marcos ANEEL) e comissionamento
  (energização = data comercial).

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Contrato EPC ou PPA | `agente-contratual` |
| Modelo financeiro RAP × CAPEX | `agente-advisory` |
| Edital de leilão / RFP EPC | `agente-bd` |
| Acesso à torre em floresta / região remota | `agente-infraestrutura S1` |
| Travessia de rio com torre estaiada especial | `agente-infraestrutura S2` |
| UHE completa (barragem + LT) | `agente-barragens` + este |
| ETE de canteiro, drenagem oleosa da SE | `agente-saneamento` |

## Onboarding

1. Ler o `SKILL.md` completo (intake com **7 segmentos** T/D/Gh/Ge/Gs/Gt/M).
2. Consultar `refs/README.md` para ANEEL/EPE/ONS + IEEE + IEC.
3. Testar com um dos `prompts/starters.md`.
4. Salvar como caso em `ene:cases:CASE-ENE-NNN` (sub `ene:t:` transmissão,
   `ene:d:` distribuição, `ene:g:` geração).
