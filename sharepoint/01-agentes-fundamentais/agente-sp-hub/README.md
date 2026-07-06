# agente-sp-hub — SharePoint mirror

Mirror versionado da pasta destino no SP:

```
Documentos Compartilhados/04_IA/Manta-Maestro/01-agentes-fundamentais/agente-sp-hub/
```

## Conteúdo

- `SKILL.md` — pronto para upload no SP (v2.0.0, Manta 20).

## Sobre o Manta 20 (SP Hub v2.0)

Evolução do `agente-sp-indexer` v1.0 (05/07/2026). Deixa de ser indexador
passivo e passa a ser o Hub Central SharePoint — ponto único de entrada
e saída de documentos SP para os outros 19 agentes do Maestro.

Três modos:

- **Reativo** — busca on-demand (`search_sp_index` + `sharepoint_search`).
- **Proativo** — `delta_sync.py` + push por routing rules → `sp_agent_feed`.
- **Escrita** — gateway via Zapier Graph API (auditoria centralizada).

Spec canônica: [`../../../docs/MANTA-20-SPHUB-SPEC-v2.0.md`](../../../docs/MANTA-20-SPHUB-SPEC-v2.0.md)
(ID `MANTA-SPHUB-20260706-001`).

Migração Supabase: [`../../../supabase/migrations/2026_07_06_v4_3_manta20_sphub.sql`](../../../supabase/migrations/2026_07_06_v4_3_manta20_sphub.sql)
