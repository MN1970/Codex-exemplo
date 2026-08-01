---
name: funcional-F10-pesquisa-evolutiva
codigo: F10
camada: L1.6
tipo: funcional
version: 1.0.0
updated: 2026-07-28
origem: "Formalizado a partir de KE-076, KE-077, KE-078 (tese REF-2026-PESQ-ML), previamente referenciado como 'agente Pesquisador Evolutivo (M16)' em esquema legado nao-canonico. Portado do SP-native 2026-07-31 para v6.1 taxonomia reconciliada."
---

# F10 Pesquisa Evolutiva — Scout de conhecimento e RAG incremental

Servico transversal de descoberta e priorizacao continua de conhecimento novo para
alimentar o pipeline RAG do Manta Maestro. Diferente de F9-meta (que audita e
mantem a arquitetura ja existente), F10 olha para fora: novas normas, novos
metodos, novos recursos que ainda nao viraram KE.

## Cobertura

- Active learning para triagem de documentos tecnicos (classificador + incerteza
  de predicao) para priorizar quais documentos merecem extracao de KE (KE-076)
- RAG incremental: reindexacao apenas de chunks novos/alterados, com
  versionamento de modelo de embedding por chunk, evitando reprocessar toda a
  `ke_embeddings` a cada atualizacao (KE-077)
- Benchmarking de modelos de embedding para texto tecnico em portugues —
  trade-off dimensionalidade x qualidade semantica (KE-078)

## Palavras-chave de roteamento

pesquisa evolutiva, scout, active learning, RAG incremental, benchmark embedding,
triagem de documentos, novo recurso, novo conhecimento, priorizar KE, pipeline AKP.

## Cruzamentos S.A.D tipicos

- F10 alimenta o pipeline AKP (aquisicao de conhecimento) que gera novos KEs
- Handoff para F1-ia (rag-retriever) quando decide migrar/atualizar modelo de embedding
- Handoff para F7-guardrails (aluci-guard) antes de qualquer KE novo ser aprovado
- Nao decide arquitetura (isso e F9-meta / arquiteto-ia) — apenas descobre e prioriza

## O que F10 NAO faz

- Nao aprova KEs sozinho (aluci-guard e grader continuam obrigatorios)
- Nao decide mudanca de modelo de embedding sem aprovacao humana (MN) — apenas
  recomenda com base em benchmark
- Nao substitui F9-meta (auditoria/consolidacao da arquitetura ja existente)

## Pendencia conhecida

Este agente foi referenciado em producao como "M16" / "Pesquisador Evolutivo"
antes de existir um codigo canonico. KE-076, KE-077 e KE-078 foram corrigidos em
2026-07-28 para apontar a `agentes_destino = ['F10']`. Mesma correcao aplicada a
KE-073/074/075, que apontavam para codigos legados ["06","01"] → agora
`['A8','A7']`, `['A8','A6']`, `['A8']` respectivamente.
