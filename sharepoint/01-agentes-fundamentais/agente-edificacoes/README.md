# agente-edificacoes (Manta 03-S13)

Agente vertical de edificações verticais residenciais, comerciais,
mistas, galpões industriais leves (warehouse Class A, cross-dock, dark
store, data center shell) e institucionais (hospital, escola,
universidade, hotel). Também cobre retrofit e mudança de uso.

## Estrutura desta pasta

```
agente-edificacoes/
├── SKILL.md         # definição canônica (frontmatter, intake, arquitetura V1-V5)
├── README.md        # este arquivo — visão geral e onboarding
├── refs/            # documentos técnicos de referência
│   └── README.md    # bibliografia comentada
└── prompts/         # prompts amostrais + conversation starters
    └── starters.md  # 10 starters por caso de uso
```

## Quando usar

Roteia automaticamente quando aparecem palavras-chave: **edificação,
edificações, predial, vertical, torre, galpão, warehouse, cross-dock,
dark store, data center, hospital, universidade, escola, hotel, MRV,
Cyrela, Even, MCMV, NBR 15575, NBR 6118, NBR 8800, NBR 6122, NBR 6120,
LEED, AQUA, Selo Casa Azul, curtain wall, alvenaria estrutural, laje
protendida, hélice contínua, BIM, Revit, IFC, BMS, sprinkler, CBMESP**.

## Escopo e fora do escopo

**Cobertura**: consultoria técnica e de gestão em edificações verticais
residenciais/comerciais/mistas + galpões industriais leves + institucional
(hospital, escola, universidade, hotel) + retrofit. A Manta apoia
projetos executivos, orçamento, obra e DD — não substitui arquitetura
criativa nem ART/RRT.

**Fora do escopo**: obra industrial pesada de processo (refino, planta
química, mineração beneficiamento — encaminhar para S11/S12); barragens
(→ S10); OAE de grande porte (→ S2); TPS aeroportuário (→ S7).

## Casos de uso típicos

- DD técnica de portfolio de incorporadora (múltiplas torres MCMV ou
  médio padrão).
- Review de projeto executivo de torre AAA (30-50 pavimentos), com
  atenção a lajes protendidas e curtain wall silicone estrutural.
- Dimensionamento de galpão Class A (30k m² tipo WT) com pé-direito 12m
  e piso industrial high-performance.
- Retrofit de edifício histórico centro SP (mudança de uso comercial→
  residencial), com reforço estrutural e atualização normativa.
- Certificação LEED Platinum ou AQUA Excelente de sede corporativa.
- Hospital 300 leitos: coordenação disciplinar entre estrutura,
  fundação, MEP crítico (gases medicinais, UPS, HVAC filtrado) e SCI.
- Data center TIER III shell 5 MW crítica: coordenar carga elétrica,
  redundância N+1 no HVAC, PSE.
- Orçamento SINAPI vs SICRO para condomínio popular MCMV faixa 2.
- BIM coordination em edifício de uso misto (residencial + comercial +
  garagem subsolo).
- Análise de desempenho NBR 15575 nível intermediário para faixa 3 MCMV.

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Obra industrial pesada — refino, planta química | `Manta 03-S12 (óleo & gás)` |
| Obra industrial — mineração beneficiamento | `Manta 03-S11 (mineração)` |
| Terminal de passageiros aeroportuário (TPS) | `agente-aeroportos (S7)` |
| Passarela / ponte / viaduto de acesso à torre | `agente-infraestrutura S2 (OAE)` |
| Data center com LT + SE + no-break UPS crítico | `agente-energia (S9)` |
| Drenagem macro urbana do empreendimento + ETE local | `agente-saneamento (S8)` |
| Terraplenagem grande do sítio (transversal) | `agente-infraestrutura S1` |
| Contratos EPC / empreitada global / performance | `agente-contratual` (Manta 02) |
| DD de portfolio de incorporadora / VGV / valuation | `agente-advisory` (Manta 15) |
| LPUOS / incorporação / matérias fundiárias | `agente-imobiliario` (Manta 04) |
| Orçamento SINAPI/TCPO detalhado | `agente-05 (orcamento)` |
| Cronograma + linha de balanço em torres repetitivas | `agente-07 (cronograma)` |
| Coordenação BIM Revit/IFC / clash detection | `agente-06 (modelagem)` |
| Barragem / bacia grande porte | `agente-barragens (S10)` |

## Onboarding para novos usuários

1. Ler o `SKILL.md` completo (intake Q1-Q4).
2. Consultar `refs/README.md` para a bibliografia mínima que o agente
   assume (NBRs, IT-CBMESP, Casa Azul, LEED/AQUA).
3. Testar com um dos `prompts/starters.md` no ambiente Maestro.
4. Salvar o caso no RAG (`edi:cases:CASE-EDI-NNN`) ao final.
