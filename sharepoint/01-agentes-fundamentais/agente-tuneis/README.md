# agente-tuneis (Manta 03-S5)

Agente vertical de túneis e obras subterrâneas. Cobre túneis
rodoviários (montanha, urbanos, imersos — ITT), ferroviários,
metroviários, hidráulicos (adução, desvio, conduto forçado),
galerias urbanas de utilidades e poços de acesso e ventilação.
Trata todos os métodos construtivos: NATM / escavação sequencial,
TBM (EPB, slurry, hard rock), cut & cover, imersão de módulos
pré-fabricados e microtúneis (pipe jacking).

Substitui a cobertura anterior que era compartilhada entre S2
(OAE) e S4 (metrô), consolidando "tunneling" como um vertical
próprio na arquitetura Manta.

## Estrutura desta pasta

```
agente-tuneis/
├── SKILL.md         # definição canônica (frontmatter, intake, arquitetura V1-V5)
├── README.md        # este arquivo — visão geral e onboarding
├── refs/            # documentos técnicos de referência
│   └── README.md    # bibliografia comentada
└── prompts/         # prompts amostrais + conversation starters
    └── starters.md  # 10 starters por caso de uso
```

## Quando usar

Roteia automaticamente quando aparecem palavras-chave: **túnel,
tunel, NATM, TBM, EPB, slurry, hard rock, cut and cover, cut &
cover, imerso, ITT, dovela, shotcrete, cambota, tirante,
enfilagem, jet grouting, jet fan, PIARC, ITA, AITES, NFPA 502,
convergência, curva de Fenner-Pacher, método observacional Peck,
escudo, tuneladora, pipe jacking, microtúnel, portal, poço de
acesso, Linha 4, Linha 6, Rodoanel túnel, Marcello Alencar,
Gotthard**.

## Casos de uso típicos

- Dimensionamento NATM em rocha (classe RMR, curva de
  Fenner-Pacher, suporte primário).
- Seleção de TBM (EPB × slurry × hard rock) por granulometria +
  permeabilidade + carga hidráulica.
- Análise de assentamento superficial em túneis urbanos rasos
  (método observacional de Peck, volume perdido Vl).
- Ventilação longitudinal com jet fans e cálculo PIARC (poluentes,
  visibilidade, incêndio).
- Análise de risco de incêndio (NFPA 502) — sistema hidráulico,
  detecção, escape, compartimentação.
- Estudo de portal em encosta (cortina ancorada, tirantes
  protendidos, drenagem).
- Revestimento com dovelas pré-fabricadas (juntas EPDM, TBM
  backfill).
- Microtúneis em travessias sob rodovia, ferrovia ou rio.
- DD / EVTE de concessão com trechos em túnel (Rodoanel, PPPs).
- Pleito técnico / claim por classe de rocha divergente, TBM
  parada, fluxo d'água inesperado.

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Cláusula de risco geotécnico contratual | `agente-contratual` |
| Pleito por classe de rocha divergente / TBM parada | `agente-claims` |
| Modelagem financeira de concessão com túnel | `agente-advisory` |
| Rodovia de acesso ao portal | `agente-infraestrutura S1` |
| Portal apoiado em ponte / viaduto | `agente-infraestrutura S2` |
| Túnel como parte de linha metroviária | `agente-infraestrutura S4` |
| Túnel de adução ou emissário submarino | `agente-saneamento (S8)` |
| Túnel para conduto forçado de PCH/UHE | `agente-energia (S9)` |
| Túnel de desvio / extravasor de barragem | `agente-barragens (S10)` |

## Onboarding para novos usuários

1. Ler o `SKILL.md` completo (intake Q1-Q4 e as 5 vertentes V1-V5).
2. Consultar `refs/README.md` para a bibliografia mínima que o
   agente assume (DNIT IPR-742, NBR 15220, ITA/AITES, PIARC C4,
   NFPA 502, FHWA Tunnel Manual).
3. Testar com um dos `prompts/starters.md` no ambiente Maestro.
4. Salvar o caso no RAG (`tun:cases:CASE-TUN-NNN`) ao final e
   propor upgrade da bibliografia se o caso trouxe fonte nova.
