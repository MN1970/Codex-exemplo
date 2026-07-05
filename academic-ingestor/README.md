# academic-ingestor — WF-AKP-001

Pacote versionado do **Academic Knowledge Pipeline** do Manta Maestro v4.2.
Origem dos dados: sessão Claude Chat com Maurício (2026-07-05), Stages 1-3
concluídos e gate humano aprovado. Esta sessão do Claude Code executou Stages
4-5 e preparou os módulos das Stages 6.

Para o que já foi executado contra o Supabase manta-maestro, veja
[`EXECUCAO-CLAUDECODE.md`](./EXECUCAO-CLAUDECODE.md).
Para o pipeline conceitual completo, veja [`HANDOFF.md`](./HANDOFF.md).

## Estrutura

```
academic-ingestor/
├── README.md
├── HANDOFF.md                   ← handoff canônico da sessão Chat
├── EXECUCAO-CLAUDECODE.md       ← log do que rodou em produção nesta sessão
├── MASTER-CATALOG.json          ← 36 teses + 52 KEs (fonte da verdade)
├── INDICE-KEs.md                ← mapa KEs → agentes
├── stage2-jsons/                ← batches originais que geraram o MASTER
├── supabase/
│   ├── migration_teses_academicas.sql   ← DDL consolidado (aplicado)
│   └── inserts_teses.sql                ← 36 INSERTs (aplicados em 6 lotes)
├── src/
│   ├── m18_embeddings.py        ← pgvector 768d (mpnet paraphrase-multilingual)
│   ├── m20_sharepoint_upload.py ← Graph API upload (04_IA/Manta-Maestro/Teses/)
│   └── requirements.txt
└── pdfs/                        ← PDFs originais (vazio; batch fetch pendente)
```

## Status por Stage

| Stage | O que é                                    | Status                                                     |
|-------|---------------------------------------------|------------------------------------------------------------|
| 1     | Busca (M15/M16) — 39 candidatas             | ✅ concluído no Chat                                       |
| 2     | Extração (M18) — 5 batches → 52 KEs         | ✅ concluído no Chat                                       |
| 3     | Validação (M17 + aluci-guard) + gate humano | ✅ concluído no Chat (36/36 pass, avg 8.9/10)              |
| 4     | M13 migration no Supabase                    | ✅ aplicada nesta sessão em `ogxxgvgtulrbbppshjie`         |
| 5     | Seed dos 36 registros + 52 KEs normalizados  | ✅ aplicado nesta sessão (36 teses + 52 KEs no banco)      |
| 6.1   | M18 embeddings 768d → `ke_embeddings`        | ⏸ código pronto, precisa de `SUPABASE_SERVICE_KEY`         |
| 6.2   | M20 mirror PDFs no SharePoint                | ⏸ código pronto, precisa das creds SP + fetch dos PDFs     |
| 7     | Atualizar `INDICE-MANTA.md` no SharePoint    | ⏸ próximo item para o Maestro                              |

## Como continuar de onde parei

```bash
# 6.1 — embeddings
cd academic-ingestor/src
pip install -r requirements.txt
export SUPABASE_URL="https://ogxxgvgtulrbbppshjie.supabase.co"
export SUPABASE_SERVICE_KEY="..."   # do dashboard Supabase
python m18_embeddings.py            # gera 52 embeddings (~2min em CPU)

# 6.2 — SharePoint (depois de baixar os PDFs em ./pdfs/{codigo}.pdf)
export SP_TENANT_ID="..."
export SP_CLIENT_ID="..."
export SP_CLIENT_SECRET="..."
export SP_SITE_ID="mantaassociados.sharepoint.com,<site>,<web>"
python m20_sharepoint_upload.py --catalog ../MASTER-CATALOG.json --pdfs ../pdfs/ --dry-run
python m20_sharepoint_upload.py --catalog ../MASTER-CATALOG.json --pdfs ../pdfs/
```
