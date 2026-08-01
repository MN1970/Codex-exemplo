---
name: atividade-A10-risco
codigo: A10
camada: L1.7
tipo: atividade
version: 3.0.0
updated: 2026-07-09
origem: portado do SP-native 2026-07-31 para v6.1 taxonomia reconciliada
---

# A10 Analise de risco — Metodo

Racional metodologico para analise de risco: matriz probabilidade x impacto, Monte Carlo de risco, cenarios, arvore de decisao. Absorve a antiga vertente-1-analise dos agentes v2.2.

## Pipeline
```
identificacao   -> catalogo de riscos por categoria (tecnico, contratual, financeiro, ambiental, geotecnico, hidrologico)
qualificacao    -> probabilidade (5 niveis) x impacto (5 niveis) = criticidade
quantificacao   -> valoracao economica-financeira dos riscos criticos
Monte Carlo     -> simulacao (5-10k iteracoes) para riscos combinados
resposta        -> mitigar / transferir / aceitar / evitar
contingencia    -> reserva orcamentaria e schedule float
publica         -> DOCX + XLSX matriz + portal F3 heat map
```

## Proposta de output canonica
- Tipo: matriz de riscos + relatorio
- Formato: XLSX (matriz + Monte Carlo) + DOCX (relatorio) + portal F3 com heat map interativo
- Estrutura XLSX: risco / categoria / P / I / criticidade / valoracao / owner / resposta / contingencia
- Funcionais: F1 (Opus), F8, F3 (heat map), F2, F6.

## Rubrica auto-juiz L2
- Recomenda: top 5 riscos e resposta prioritaria
- Compara: cenarios base/otimista/pessimista
- Antecipa: gatilhos e sinais de alerta
- Quantifica: BRL contingencia + dias schedule float
- Ponto cego: risco sistemico / correlacionado nao evidente

## Composicoes com atividades
A10 e transversal — pode ser autonomo (analise de risco de portfolio) ou integrado em A1 proposta, A4 modelagem, A5 cronograma, A6 contratual.

## Composicoes com disciplinas
A10.D03 risco geotecnico (variacao macico), A10.D07 risco hidrologico (evento extraordinario), A10.D13 risco ambiental.

## Sub-skills L1 chamadas
xlsx, artefato, matriz-riscos (a criar).

## Ver tambem
[[A4-modelagem]] (Monte Carlo compartilhado), [[A6-contratual]] (matriz pre-execucao), [[A7-claims]] (risco materializado).
