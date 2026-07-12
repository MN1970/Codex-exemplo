# Seed payload — validação end-to-end

Este diretório contém um **payload de validação** com 10 teses fictícias
e 15 Knowledge Elements exemplares (3 por segmento S6-S10). O propósito
é permitir que o pipeline seja validado end-to-end **antes** do payload
real das stages 1-3 aterrissar.

## O que este seed NÃO é

- **Não é** o resultado das stages 1-3.
- **Não é** para produção.
- **Não substitui** o `03_exports/akp-ke-payload.json` real.

Todos os KEs aqui têm `provenance.stage_1.curator == "SEED-VALIDATION"`
para serem trivialmente distinguíveis do payload real.

## Como usar

### 1. Ingerir em ambiente de staging

```bash
cd manta-hub
python scripts/akp_ingest.py \
  --input ../Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-payload.json \
  --theses-inventory ../Codex-exemplo/sharepoint/02-academic-knowledge/seed/akp-seed-theses.csv \
  --supabase-url $SUPABASE_STAGING_URL \
  --supabase-key $SUPABASE_STAGING_SERVICE_ROLE_KEY \
  --embedding-model text-embedding-3-small
```

### 2. Rodar smoke test

```bash
python scripts/akp_smoke_test.py \
  --supabase-url $SUPABASE_STAGING_URL \
  --supabase-key $SUPABASE_STAGING_SERVICE_ROLE_KEY \
  --embedding-model text-embedding-3-small
```

Esperado: 5/5 segmentos verdes (S6, S7, S8, S9, S10 cada um com ≥1 KE
relevante no top-3).

### 3. Purgar antes de ingerir o payload real

```sql
DELETE FROM academic_knowledge_elements
 WHERE provenance->'stage_1'->>'curator' = 'SEED-VALIDATION';
DELETE FROM academic_theses
 WHERE id IN (SELECT id FROM academic_theses
              WHERE id LIKE 'seed-%');
```

Ou simplesmente restaure o schema (é uma migração idempotente).

## Distribuição do seed

| Segmento | Teses | KEs | Tipos representados                     |
|----------|-------|-----|-----------------------------------------|
| S6 portos       | 2 | 3 | metodo, caso, critica                   |
| S7 aeroportos   | 2 | 3 | formula, critica, metodo                |
| S8 saneamento   | 2 | 3 | recomendacao, metodo, dado              |
| S9 energia      | 2 | 3 | formula, conceito, caso                 |
| S10 barragens   | 2 | 3 | metodo, critica, conceito               |
| **Total**       | **10** | **15** | Todos os 7 tipos cobertos         |
