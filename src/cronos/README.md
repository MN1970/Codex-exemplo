# Manta Cronos — motor de cronogramas do A5

Motor determinístico e camada de agentes (Claude Agent SDK) para o Maestro
**A5-cronograma** (L1.7). Plano completo: artefato "Manta Cronos" (v1.2).
Visualizador: aba **Cronogramas** do Ask Manta.

## Estrutura

```text
src/cronos/
├── engine/              # sem dependência do SDK — é o que os testes cobrem
│   ├── calendar.py      # clndr_data do P6, feriados, aritmética de horas de trabalho
│   ├── model.py         # modelo canônico (Projeto, Atividade, Ligacao, Restricao)
│   ├── xer.py           # leitura/gravação XER (latin-1, vários projetos, só vigentes)
│   ├── mspdi.py         # leitura/gravação MS Project XML (MSPDI)
│   ├── schedule.py      # CPM por datas, Monte Carlo, comparação de versões
│   └── dcma.py          # DCMA-14 com a regra A5
├── sdk/                 # requer claude-agent-sdk
│   ├── tools.py         # servidor MCP em processo "cronos" (7 ferramentas)
│   ├── agents.py        # subagentes A5.1, A5.2, A5.4, A5.5, A5.6, A7, guard
│   └── main.py          # agente-A5 pai (orquestrador)
└── web/
    ├── cronos-engine.js         # porta do motor para o navegador (paridade testada)
    └── askmanta-cronogramas.html # módulo da aba Cronogramas do Ask Manta
```

## Regras implementadas (F1)

| Tema | Comportamento |
|---|---|
| Calendários | Lê `clndr_data` do P6 (semana + exceções); fallback 5×8 com alerta |
| Data de status | Nada remanescente começa antes dela |
| Datas reais | Concluída fica fixa; em andamento usa o início real e o remanescente |
| Lógica retida | O remanescente espera predecessoras FS/FF abertas |
| Ligações | FS, SS, FF, SF com lag no calendário da predecessora |
| Restrições | SNET, FNET, MSO, MFO (ida); SNLT, FNLT, MSO, MFO (volta) |
| Folga | Menor entre folga de início e de término; crítica se ≤ 0 |
| Término exigido | Volta a partir dele quando o projeto define (gera folga negativa) |
| DCMA-14 | 14 pontos; aprovação A5: nota ≥ 90% e sem bloqueio em 1, 3, 6, 7, 11 |
| Só dados vigentes | Recusa OBSOLETO, DEPRECATED e 99-backup salvo pedido explícito |
| Cost-loaded | Custo por atividade (TASKRSRC); alerta quando não há custos |
| Exportação | XER com datas calculadas; MSPDI (o MS Project salva como .mpp) |

Ainda não implementado: nivelamento de recursos, LOE e resumo de EAP no
cálculo, caminho mais longo, calendários do MSPDI, leitura de Excel e PDF.

## Uso

```bash
# motor (sem SDK)
PYTHONPATH=src python -c "from cronos.engine import ler_arquivo, calcular; p = ler_arquivo('BL.xer')[0]; print(calcular(p)['termino'])"

# agentes (requer claude-agent-sdk e credencial Anthropic)
pip install claude-agent-sdk
PYTHONPATH=src python -m cronos.sdk.main "Compare as duas linhas de base" BL-01.xer BL-02.xer
```

## Testes

```bash
python -m pytest tests/cronos -m unit
```

Inclui paridade entre o motor Python e `web/cronos-engine.js` (precisa de
Node.js; o teste é pulado se não houver).

## Regra R1

Nenhum nome de contratante, consórcio ou subempreiteiro neste código, nos
testes ou nos exemplos. Cronogramas reais nunca entram no repositório.
