# agente-saneamento (Manta 03-S8)

Agente vertical de saneamento básico — água, esgoto, drenagem urbana,
resíduos sólidos. **PRIORIDADE AySA (Argentina)** com cobertura do
marco brasileiro pós-Lei 14.026/2020.

## Estrutura desta pasta

```
agente-saneamento/
├── SKILL.md         # definição canônica (intake com Q3 país BR/AR)
├── README.md        # este arquivo
├── refs/
│   └── README.md    # bibliografia comentada (ANA, ERAS, IWA, NBR)
└── prompts/
    └── starters.md  # 18 starters + casos AySA específicos
```

## Quando usar

Palavras-chave: **saneamento, ETA, ETE, adutora, esgoto, AySA, água
tratada, drenagem urbana, macrodrenagem, SNIS, PMSB, Lei 14.026,
subsídio cruzado, elevatória, reservatório, RAP, EEE, EEAB, reúso,
lodo, UASB, MBR, digestor**.

## Casos de uso típicos

- **AySA (AR)**: reabilitação/ampliação Planta Norte + Sistema
  Riachuelo + Sistema Sur.
- **BR**: universalização Lei 14.026 (99% água + 90% esgoto até 2033).
- Concepção de ETA (ciclo completo × em linha) por vazão + qualidade
  bruta.
- Dimensionamento hidráulico (Hazen-Williams, golpe de aríete Joukowsky).
- ETE com escolha de tecnologia (UASB, lodo ativado, MBR, filtro bio.)
  por eficiência × custo × área × operação.
- Drenagem urbana (micro + macro + SbN — soluções baseadas em natureza).
- Plano de outorga, licença ambiental, EIA/RIMA.

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Concessão / PPP saneamento | `agente-contratual` |
| VPL/TIR/EBITDA de concessão | `agente-advisory` |
| Travessia sob rodovia / drenagem viária | `agente-infraestrutura S1` |
| Emissário sob ponte / OAE | `agente-infraestrutura S2` |
| Alimentação EEE, tarifa industrial/rural | `agente-energia` |
| Barragem de abastecimento (manancial) | `agente-barragens` |
| BIM MEP + modelagem hidráulica (EPANET) | `agente-modelagem` (Manta 06) |

## Onboarding

1. Ler o `SKILL.md` completo — **especial atenção à Q3 país (BR/AR)**.
2. Consultar `refs/README.md` para AySA/ERAS/PIRHA (AR) e ANA/SNIS (BR).
3. Testar com um dos `prompts/starters.md`.
4. Salvar como caso em `san:cases:CASE-SAN-NNN` (com sub-prefixo
   `san:br:` ou `san:ar:`).
