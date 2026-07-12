# Seed payload — bibliografia de arquitetura de agentes IA

Extensão do seed principal (`akp-seed-payload.json`) com 6 KEs +
6 fontes cobrindo **literatura sobre arquitetura de agentes IA**.

Segmento (novo): `transversal_arq`.
Alvo: `agente-arquiteto-ia` (Manta 16) e `agente-maestro` (Manta 00).

## Por que agentes de arquitetura estão na coleção acadêmica

O `academic-knowledge` foi desenhado (v4.3) como coleção **transversal
horizontal** — teses de engenharia civil que servem a vários agentes
verticais (S6-S13). A mesma infraestrutura serve para outra transversal:
**os próprios papers que informam como o Maestro é construído e como
ele deve evoluir.**

A tese central deste pacote é operacional:

> Quando o MN debate com o Maestro (ou o Manta 16/arquiteto-ia) uma
> decisão de evolução do ecossistema — "devo criar um agente novo?",
> "o router precisa virar orquestrador?", "por que k=60 no RRF?", "como
> validar o agente-portos vs agente-oleo-gas em disputa?" — o Maestro
> **deveria conseguir citar os papers que fundamentam a resposta**, no
> mesmo formato acadêmico canônico com que já cita Silva 2019 sobre
> dragagem. A separação entre "conhecimento do domínio" e "conhecimento
> de como o próprio agente é feito" é artificial: para o Maestro é tudo
> RAG.

Portanto, a mesma coleção `academic-knowledge` (prefixo `ake:`) recebe
esses 6 KEs; o RPC `match_academic_knowledge_hybrid` já resolve por
`segmento` e `agentes_alvo`, então não há mudança de infra — só payload
adicional.

## Como ingerir junto ao payload principal

Duas opções:

### (A) Ingestão em bloco — merge lógico

Faça um payload consolidado que soma `elements` e teses:

```bash
cd manta-hub

jq -s '{
  "$schema": .[0]."$schema",
  version: "1.0.0-seed-consolidado",
  pipeline: .[0].pipeline,
  generated_at: .[0].generated_at,
  stages_completed: .[0].stages_completed,
  theses_count: 16,
  knowledge_elements_count: 21,
  elements: (.[0].elements + .[1].elements)
}' \
  ../Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-payload.json \
  ../Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-arquitetura-agentes.json \
  > /tmp/akp-seed-merged.json

cat \
  ../Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-theses.csv \
  <(tail -n +2 ../Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-arquitetura-agentes-theses.csv) \
  > /tmp/akp-seed-merged-theses.csv

python scripts/akp_ingest.py \
  --input /tmp/akp-seed-merged.json \
  --theses-inventory /tmp/akp-seed-merged-theses.csv \
  --supabase-url $SUPABASE_STAGING_URL \
  --supabase-key $SUPABASE_STAGING_SERVICE_ROLE_KEY \
  --embedding-model text-embedding-3-small
```

### (B) Duas ingestões independentes

Se preferir isolar o rollback (ex.: sair o pacote de arquitetura sem
tocar no de engenharia), rode `akp_ingest.py` duas vezes — os dois
payloads são idempotentes por `id` do KE e por `id` da tese.

## Como purgar antes do payload real

O filtro por `curator = 'SEED-VALIDATION'` continua funcionando (vide
README.md do seed original), mas também dá para restringir por
segmento se você quiser preservar os KEs de arquitetura em produção:

```sql
-- purga só a engenharia civil (S6-S10 fictícios)
DELETE FROM academic_knowledge_elements
 WHERE provenance->'stage_1'->>'curator' = 'SEED-VALIDATION'
   AND segmento IN ('portos','aeroportos','saneamento','energia','barragens');

-- mantém `transversal_arq` (papers reais, úteis mesmo em prod)
```

Os 6 KEs de arquitetura são **papers reais e citáveis** (não fictícios
como Silva 2019 / Costa 2022 do seed original), então em muitos casos
o cliente vai querer promovê-los diretamente à ingestão de produção,
apenas re-avaliando `provenance.stage_1.curator` de `SEED-VALIDATION`
para o nome da MN.

## Os 6 papers e sua relevância prática para a Manta

| # | KE | Paper | Relevância para o ecossistema Manta |
|---|-----|-------|-------------------------------------|
| 1 | KE-ARQ-01 | Chen et al. 2024 — AgentBench (ICLR) | Justifica criar sub-benchmarks por agente vertical (S1-S13) medindo tool-chains, não só acurácia final. |
| 2 | KE-ARQ-02 | Wu et al. 2023 — AutoGen (Microsoft) | Fundamenta a evolução do Manta 00 de router regex para GroupChatManager e o padrão critic (Manta 15b futuro). |
| 3 | KE-ARQ-03 | Park et al. 2023 — Generative Agents (Stanford / UIST) | Base teórica da Reflexive Memory já implementada no AskCAD; motiva a camada 2 (reflection) que ainda falta. |
| 4 | KE-ARQ-04 | Shen et al. 2023 — HuggingGPT (NeurIPS) | Crítica ao routing LLM-puro — reforça o fallback regex do Maestro e o budget cap por handoff. |
| 5 | KE-ARQ-05 | Anthropic 2024 — Building Effective Agents | Taxonomia dos 5 padrões (chaining/routing/parallelization/orchestrator/evaluator). Guia para próximas decisões de topologia. |
| 6 | KE-ARQ-06 | Cormack, Clarke, Büttcher 2009 — RRF (SIGIR) | Justifica o `k=60` no RPC `match_academic_knowledge_hybrid` da v4.3. Ancora escolha de constante. |

## Uso previsto pelo Maestro

Após ingestão, uma pergunta do MN como:

> "Manta, o `agente-portos` está fazendo trabalho demais. Faz sentido
> quebrar em `agente-portos-mar` e `agente-portos-hidrovia`?"

deveria trigar recuperação híbrida (BM25 + pgvector) na coleção
`academic-knowledge` filtrada por `segmento = 'transversal_arq'` e
retornar como top-3 provavelmente:

1. KE-ARQ-05 (Anthropic 2024) — "não escale complexidade antes de o
   comportamento simples se mostrar insuficiente"
2. KE-ARQ-02 (AutoGen) — quando decompor em conversantes ganha
3. KE-ARQ-04 (HuggingGPT) — riscos de routing entre muitos experts

...e o Maestro responde citando os três no mesmo formato canônico
`[Autor Ano, KE-XX]` que já usa para engenharia civil, com link para
os PDFs no SharePoint `07_Conhecimento_Academico/`.
