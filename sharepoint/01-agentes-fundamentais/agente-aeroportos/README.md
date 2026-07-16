# agente-aeroportos (Manta 03-S7)

Agente vertical de projetos aeroportuários. Cobre lado ar (pista de
pouso, taxiway, pátio, RESA), lado terra (TPS, TECA, estacionamento) e
sistemas (balizamento CAT I/II/III, ILS, torre, SCI).

## Estrutura desta pasta

```
agente-aeroportos/
├── SKILL.md         # definição canônica
├── README.md        # este arquivo
├── refs/
│   └── README.md    # bibliografia comentada (RBAC, ICAO, FAA)
└── prompts/
    └── starters.md  # 15 starters por caso de uso
```

## Quando usar

Palavras-chave de routing: **aeroporto, pista, RWY, taxiway, TWY,
pátio, TPS, TECA, ANAC, RBAC 154, ICAO Annex 14, FAA AC, balizamento,
PAPI, ILS, PCN, ACN, gate, jetway, código aeródromo, aviação geral,
concessão aeroportuária**.

## Casos de uso típicos

- Dimensionamento geométrico airside (pista, taxiway, RESA) por
  código aeródromo + aeronave crítica.
- Pavimento aeroportuário (FAA FAARFIELD, verificação PCN/ACN).
- TPS: dimensionamento por LOS IATA, análise de fluxo, hora-pico TPHP.
- Balizamento (CAT I/II/III), sistemas de navegação (ILS, VOR, DME).
- Plano de fases + NOTAM para obra em aeroporto operante.
- DD de concessão aeroportuária (obra + operação).

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Contrato de concessão / PPP aeroportuária | `agente-contratual` |
| Modelo financeiro de concessão (VPL, TIR) | `agente-advisory` |
| Rodovia de acesso | `agente-infraestrutura S1` |
| Passarela/viaduto TPS ↔ estacionamento | `agente-infraestrutura S2` |
| ETE do TPS, drenagem oleosa de pátio (SOS) | `agente-saneamento` |
| Subestação + alimentação de balizamento | `agente-energia` |

## Onboarding

1. Ler o `SKILL.md` completo (intake Q1-Q4).
2. Consultar `refs/README.md` para RBAC 154, ICAO Annex 14, FAA ACs.
3. Testar com um dos `prompts/starters.md`.
4. Salvar como caso em `aer:cases:CASE-AER-NNN`.
