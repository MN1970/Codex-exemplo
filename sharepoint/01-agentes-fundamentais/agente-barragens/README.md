# agente-barragens (Manta 03-S10)

Agente vertical de barragens — todas as tipologias (concreto CVC/CCR/RCC,
terra, enrocamento CFRD/ECRD, rejeitos, diques) e propósitos (UHE,
abastecimento, irrigação, contenção rejeitos, controle de cheias).

## Estrutura desta pasta

```
agente-barragens/
├── SKILL.md         # definição canônica (intake por tipologia + propósito)
├── README.md        # este arquivo
├── refs/
│   └── README.md    # bibliografia (ICOLD, CBDB, ANM, ANA, Lei 12.334)
└── prompts/
    └── starters.md  # 20 starters + regras de descaracterização
```

## Quando usar

Palavras-chave: **barragem, vertedouro, CFRD, CCR, RCC, rejeitos,
TSF, PNSB, ICOLD, CBDB, dique, SIGBM, ANM, ANA, Lei 12.334,
Fundão, Brumadinho, descomissionamento, alteamento montante/jusante/
linha de centro, filtragem de rejeitos, dry stack, PAE, PAEBM, ZAS,
ZSS, HHP**.

## Casos de uso típicos

- Barragens de concreto: gravidade, gravidade aliviada, arco,
  contrafortes.
- Barragens de terra: homogênea, zonada, com filtro vertical.
- Barragens de enrocamento: CFRD (face de concreto), ECRD (núcleo
  argiloso), com núcleo asfáltico.
- **Barragens de rejeitos (mineração)**: alteamento a montante
  (proibido no BR desde 2019), jusante, linha de centro, dry stack.
  **Descaracterização obrigatória** de barragens a montante existentes
  (ANM Res. 95/2022).
- Estudo de estabilidade estática (Bishop, Morgenstern-Price, Spencer,
  Janbu) + sísmica (OBE/MDE, Newmark, dinâmica).
- Percolação (Darcy, redes de fluxo, EF) + liquefação (rejeitos
  saturados fofos).
- **Dam breach analysis** + PAE (Plano de Ação Emergencial) + PAEBM
  (para mineração) com ZAS (< 30 min) e ZSS.
- Instrumentação e monitoramento (piezômetro, extensômetro, vazão em
  drenos, célula de carga).

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Contrato EPC UHE / empreitada | `agente-contratual` |
| Modelo financeiro UHE (VPL, TIR) | `agente-advisory` |
| Pleito imprevisto geológico | `agente-contratual` (V6 Claims) |
| UHE completa (barragem + LT + SE) | `agente-energia` |
| Barragem de abastecimento (qualidade água) | `agente-saneamento` |
| Acesso ao canteiro em região remota | `agente-infraestrutura S1` |
| BIM 3D + análise FEM (PLAXIS, GeoStudio, FLAC) | `agente-modelagem` |

## Onboarding

1. Ler o `SKILL.md` completo — atenção à **regra especial de
   descaracterização** (ANM Res. 95/2022) para barragens a montante.
2. Consultar `refs/README.md` para ICOLD/CBDB/ANM/PNSB.
3. Testar com um dos `prompts/starters.md`.
4. Salvar como caso em `bar:cases:CASE-BAR-NNN` (sub `bar:c:` concreto,
   `bar:t:` terra, `bar:e:` enrocamento, `bar:r:` rejeitos).
