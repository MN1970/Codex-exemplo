# agente-portos (Manta 03-S6)

Agente vertical de projetos portuários e hidroviários. Cobre terminais
marítimos (contêineres, granéis, ro-ro, offshore), fluviais/hidroviários
e infraestrutura associada (canal, bacia de evolução, cais, quebra-mar,
dolfins, retroárea).

## Estrutura desta pasta

```
agente-portos/
├── SKILL.md         # definição canônica (frontmatter, intake, arquitetura V1-V5)
├── README.md        # este arquivo — visão geral e onboarding
├── refs/            # documentos técnicos de referência
│   └── README.md    # bibliografia comentada
└── prompts/         # prompts amostrais + conversation starters
    └── starters.md  # 10 starters por caso de uso
```

## Quando usar

Roteia automaticamente quando aparecem palavras-chave: **porto,
terminal, ANTAQ, PIANC, dragagem, molhe, quebra-mar, dolfin, berço,
calado, contêiner, granel sólido/líquido, cais, píer, retroárea, TUP,
hidrovia, arrendamento portuário, defensa**.

## Casos de uso típicos

- Diagnóstico técnico / DD de terminal existente ou em arrendamento.
- Quantificação de dragagem (aprofundamento × manutenção).
- Dimensionamento de cais, píer e dolfins.
- Estudo de defensas (energia de atracação) e amarração (spring/breast/head).
- Avaliação de retroárea e equipamento portuário (portêiner, MHC, esteira).
- Cronograma físico-financeiro de obra marítima (janelas operacionais).
- Pleito técnico / claim por atraso de dragagem, mudança de escopo.

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Cláusula de arrendamento ANTAQ | `agente-contratual` |
| Modelagem financeira de TUP/arrendamento | `agente-advisory` |
| Rodovia de acesso ao terminal | `agente-infraestrutura S1` |
| Ponte de acesso ao píer | `agente-infraestrutura S2` |
| ETE do canteiro / drenagem oleosa | `agente-saneamento` |
| Subestação + LT para o terminal | `agente-energia` |

## Onboarding para novos usuários

1. Ler o `SKILL.md` completo (intake Q1-Q4).
2. Consultar `refs/README.md` para a bibliografia mínima que o agente assume.
3. Testar com um dos `prompts/starters.md` no ambiente Maestro.
4. Salvar o caso no RAG (`por:cases:CASE-POR-NNN`) ao final.
