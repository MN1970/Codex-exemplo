# agente-leitor-documental (Manta 08)

Camada horizontal de ingestão e normalização multi-formato. Recebe PDF,
Excel/XLSX, DWG/DXF, Word/DOCX, PPTX, BIM (IFC/RVT) e cronograma
(XER/MPP), detecta formato e subtipo, despacha para a skill de leitura
correta e entrega um JSON canônico normalizado ao agente vertical dono
do segmento (S1-S10).

**Status: 🆕 Proposto** — draft de arquitetura, aguardando gate humano
(MN) e wiring de Supabase/SharePoint antes de virar Operacional. Ver
`docs/DEPLOY-v4.3.md` no repo mestre.

## Estrutura desta pasta

```
agente-leitor-documental/
├── SKILL.md         # definição canônica (frontmatter, intake, pipeline)
├── README.md        # este arquivo — visão geral e onboarding
├── refs/            # referências de formato/skill
│   └── README.md
└── prompts/         # prompts amostrais + conversation starters
    └── starters.md
```

## Quando usar

Roteia automaticamente quando o usuário pede para **ler, extrair,
organizar ou processar** um PDF, Excel, DWG/DXF, Word, PPTX, BIM ou
cronograma — ou quando pede para "montar um pipeline de leitura de
documentos" / "ingestão documental" / "leitor de PDF/Excel/DWG".

## Por que este agente existe

Cada agente vertical (portos, saneamento, energia, etc.) já podia
chamar skills de formato (`pdf`, `xlsx`, `docx`, `autodesk-toolkit`)
por conta própria, mas sem um ponto único de:
- detecção de formato/subtipo,
- normalização da saída em um schema comum,
- controle de idempotência (não reprocessar o mesmo arquivo),
- log de proveniência para auditoria (`aluci-guard`, `consist-guard`).

O Manta 08 centraliza isso como uma camada fina entre a origem do
arquivo (SharePoint, upload, lote) e o agente vertical que vai
interpretar o conteúdo tecnicamente.

## Casos de uso típicos

- "Tenho uma pasta cheia de PDF, DWG e Excel de um projeto — organiza
  a leitura disso."
- "Chegou um edital em PDF — identifica se é edital comum ou ANEEL e
  extrai os dados."
- "Esse lote tem DWG de planta e XLSX de quantitativo — quero os dois
  cruzados."
- "Recebi um .xer de cronograma — converte pro formato que o
  manta-07 usa."

## Handoffs frequentes

| Contexto | Agente destino |
|---|---|
| Documento identificado como de um segmento (S1-S10) | agente vertical dono |
| Planilha de quantitativo/orçamento | `manta-05` (orcamento) |
| Cronograma XER/MPP | `manta-07` (cronograma) |
| Formato sem skill de leitura definida | `manta-16` (arquiteto-ia) |
| Cláusula contratual dentro do documento | `manta-02` (contratual) |

## Onboarding para novos usuários

1. Ler o `SKILL.md` completo (intake Q1-Q4 e tabela de despacho por
   formato).
2. Consultar `refs/README.md` para a lista de skills de formato que
   este agente orquestra (não reimplementa).
3. Testar com um dos `prompts/starters.md` no ambiente Maestro.
4. Confirmar que o JSON canônico produzido bate com o schema da
   seção 4 do `SKILL.md` antes de considerar o pipeline pronto.
