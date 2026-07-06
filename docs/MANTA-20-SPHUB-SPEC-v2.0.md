# MANTA 20 — SP Hub (SharePoint Hub Agent)
## Spec Consolidada: Estado Atual + Proposta de Evolução v2.0

**ID:** MANTA-SPHUB-20260706-001
**Versão:** 2.0 (evolução do agente-sp-indexer v1.0.0 de 05/07/2026)
**Autor:** Manta Associados
**Classificação:** Interno

---

## PARTE A — ESTADO ATUAL (Manta 20 v1.0)

### A1. Identidade

| Campo | Valor |
|-------|-------|
| Nome | agente-sp-indexer |
| Manta Code | Manta 20 |
| Aliases | manta-20, sp-indexer, sharepoint-indexer, indexador, mapear-sharepoint |
| Criado em | 05/07/2026 (sessão Maestro v4.2) |
| Origem | Evolução do tocantins-engine:sp-indexer (escopo único) para multi-projeto |

### A2. Arquitetura Atual

```
SharePoint Manta (7 drives, ~190k docs)
       │
       ▼
┌─────────────────┐
│  SP CRAWLER     │  Microsoft 365 MCP
│  (percorre drives)│  list_folder + read_resource
└──────┬──────────┘
       ▼
┌─────────────────┐
│  CATALOGADOR    │  classifica tipo, extrai metadata
└──────┬──────────┘
       ▼
┌─────────────────┐     ┌───────────────────┐
│  sharepoint-map │────▶│  sp_agent_routing  │
│  .json (índice) │     │  (Supabase)        │
└──────┬──────────┘     └───────────────────┘
       ▼
┌─────────────────┐
│  RAG TRIGGER    │  docs novos → agente-rag-manager
└─────────────────┘
```

### A3. Infraestrutura Já Construída (sessões anteriores)

| Componente | Status | Onde |
|------------|--------|------|
| Tabela `sp_index` (Supabase) | ✅ Criada | kwuubcnedqtapvykmyye |
| Tabela `sp_sync_log` | ✅ Criada | Supabase |
| Function `search_sp_index()` | ✅ Criada | PostgreSQL full-text (pt) |
| `sp_indexer.py` | ✅ Criado | Claude Code repo |
| `onedrive_mn_indexer.py` | ✅ Criado | Claude Code repo (separado) |
| `daily_index.sh` | ✅ Criado | Cron script |
| Tool `search_files` no MantaBase MCP | ✅ Criado | Netlify (site bbbe19a4) |
| Deploy Railway (MantaBase MCP) | ⏳ Pendente | — |
| `sp_agent_routing` (24+ regras) | 📋 Planejado | Supabase |
| RAG Trigger automático | 📋 Planejado | — |

### A4. Drives Mapeados

| # | Drive | DriveId | Conteúdo |
|---|-------|---------|----------|
| 1 | SP Engenharia | `b!7wlZlI7tWU2o09im0xX4dSggtXaRRJ5LktNsMxjSZr8OGwV61sTwTqLCB0pYNM1D` | Docs Compartilhados — projetos, propostas, skills |
| 2 | SP Biblioteca | — | Backup Daniel Picchi / Projetos históricos |
| 3 | SP 02_CLIENTE | — | Projetos por cliente (CCR, EGTC, Vale, OEC...) |
| 4 | OneDrive MN | `b!MnOHM4PjNEGbl5CxF-7Ji2v8fx-LrRhEhNBEliwJm2UNPSR1tzQSSKn3VXZjftjb` | Arquivos pessoais MN |
| 5–7 | Outros drives | — | Mapeados mas não indexados em detalhe |

### A5. Limitações Atuais

1. **Só indexa, não alimenta** — o mapa existe mas nenhum agente é notificado proativamente
2. **Sem delta detection real** — não há comparação "antes vs depois" entre syncs
3. **Sem gateway de escrita** — SharePoint MCP é read-only, escrita não está integrada
4. **Deploy pendente** — MantaBase MCP no Railway nunca foi ativado
5. **Routing rules vazias** — `sp_agent_routing` com 24+ regras planejadas mas não implementadas
6. **Busca live vs cached** — hoje cada skill faz `sharepoint_search` ad hoc, gastando tokens

---

## PARTE B — PROPOSTA DE EVOLUÇÃO (SP Hub v2.0)

### B1. Nova Missão

> **Manta 20 deixa de ser um indexador passivo e se torna o Hub Central SharePoint**:
> o único ponto de entrada e saída de documentos do SharePoint para todos os 19
> agentes restantes do Maestro, com alimentação proativa baseada em conhecimento
> específico de cada agente.

### B2. Arquitetura Proposta

```
                    ┌─────────────────────────────┐
                    │   MANTA 20 — SP HUB v2.0    │
                    │   (orquestrador SharePoint)  │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                     ▼
   ┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐
   │  MODO REATIVO │  │  MODO PROATIVO  │  │  MODO ESCRITA    │
   │  (sob demanda)│  │  (delta + push) │  │  (gateway write) │
   └──────┬───────┘  └──────┬──────────┘  └──────┬───────────┘
          │                  │                     │
          ▼                  ▼                     ▼
   sharepoint_search   delta_sync.py         Zapier Graph API
   + search_sp_index   (compara snapshots)   PUT drives/{id}/
   + read_resource     gera change_log       root:/path:/content
          │                  │
          │      ┌───────────┴──────────────┐
          │      ▼                          ▼
          │  ┌───────────────┐   ┌────────────────────┐
          │  │ ROUTER        │   │ RAG INGEST          │
          │  │ (classifica + │   │ (novo doc → chunk   │
          │  │  roteia para  │   │  → pgvector via     │
          │  │  agente certo)│   │  Manta 18)          │
          │  └───────┬───────┘   └────────────────────┘
          │          │
          ▼          ▼
   ┌─────────────────────────────────────────────┐
   │          AGENTES CONSUMIDORES               │
   │                                             │
   │  M1 Claims ◄── contratos, TACs, CRs        │
   │  M2 Contratual ◄── aditivos, atas          │
   │  M3 Rodovias ◄── projetos, DWG, orçamentos │
   │  M4 OAE ◄── laudos, sondagens, DXF         │
   │  M5 Metrô ◄── PEG, FIDIC, GED             │
   │  M6 Ferrovia ◄── projetos ferroviários      │
   │  M7 Orçamento ◄── planilhas, SICRO, BDIs   │
   │  M8 BD ◄── propostas, editais, PERs        │
   │  M9 Advisory ◄── laudos, pareceres          │
   │  M16 Pesquisador ◄── papers, relatórios     │
   │  M17 Grader ◄── outputs para validação      │
   │  M18 RAG Manager ◄── chunks para ingestão   │
   │  M19 Skill Lifecycle ◄── skills .md          │
   └─────────────────────────────────────────────┘
```

### B3. Mapa de Alimentação: Drive/Pasta → Agente

| Pasta SharePoint (padrão) | Agente(s) Destino | Tipo de Doc | Prioridade |
|---------------------------|-------------------|-------------|------------|
| `02_CLIENTE/*/01_CONTRATO` | M1 Claims, M2 Contratual | Contratos, TACs, aditivos | Alta |
| `02_CLIENTE/*/02_REC` | M8 BD | Editais, PERs, anexos técnicos | Alta |
| `02_CLIENTE/*/03_PROPOSTA` | M8 BD, M7 Orçamento | Propostas, planilhas | Alta |
| `02_CLIENTE/*/04_PROJETO` | M3 Rodovias, M4 OAE | DWG, DXF, memoriais | Alta |
| `02_CLIENTE/*/05_MEDICAO` | M7 Orçamento, M1 Claims | BMs, RDOs, medições | Média |
| `02_CLIENTE/*/06_CORRESPONDENCIA` | M2 Contratual | Cartas, ofícios | Média |
| `02_CLIENTE/*/07_CRONOGRAMA` | M1 Claims (forense) | XER, MPP, baselines | Alta |
| `04_IA/Manta-Maestro/` | M19 Skill Lifecycle | Skills, agents, configs | Baixa |
| `04_IA/RAG/` | M18 RAG Manager | Chunks, embeddings | Baixa |
| `03_BIBLIOTECA/` | M16 Pesquisador | Normas, papers, teses | Média |
| Qualquer pasta com `.xer` | M1 Claims + M3 Rodovias | Cronogramas P6 | Alta |
| Qualquer pasta com `.dxf/.dwg` | M3 Rodovias + M4 OAE | Projetos CAD | Alta |
| Qualquer pasta com `SICRO` no nome | M7 Orçamento | Composições, custos | Alta |

### B4. Protocolo de Alimentação Proativa

```
TRIGGER: delta_sync detecta documento novo ou modificado
    │
    ▼
STEP 1 — Classificar
    Extensão + pasta + nome → tipo (contrato/projeto/medição/proposta/norma/...)
    │
    ▼
STEP 2 — Rotear (sp_agent_routing rules)
    tipo + pasta → lista de agentes destino
    │
    ▼
STEP 3 — Notificar
    Para cada agente destino:
      a) Inserir em sp_agent_feed (Supabase):
         {agent_code, doc_id, doc_path, doc_type, priority, status: 'pending'}
      b) Se priority == 'Alta':
         Trigger RAG ingest via M18 (extrair texto → chunk → pgvector)
    │
    ▼
STEP 4 — Log
    Registrar em sp_sync_log: timestamp, docs_new, docs_modified, docs_routed
```

### B5. Novas Tabelas Supabase

```sql
-- Feed de documentos para agentes (notificação proativa)
CREATE TABLE sp_agent_feed (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  agent_code TEXT NOT NULL,          -- 'M1', 'M2', 'M3'...
  doc_id TEXT NOT NULL,              -- SP item ID
  doc_path TEXT NOT NULL,            -- caminho completo no SP
  doc_name TEXT NOT NULL,
  doc_type TEXT,                     -- 'contrato', 'projeto', 'medicao'...
  file_ext TEXT,                     -- 'pdf', 'dwg', 'xer'...
  priority TEXT DEFAULT 'media',     -- 'alta', 'media', 'baixa'
  status TEXT DEFAULT 'pending',     -- 'pending', 'delivered', 'ingested'
  detected_at TIMESTAMPTZ DEFAULT NOW(),
  delivered_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_agent_feed_agent ON sp_agent_feed(agent_code, status);
CREATE INDEX idx_agent_feed_priority ON sp_agent_feed(priority, status);

-- Regras de routing (configurável)
CREATE TABLE sp_routing_rules (
  id SERIAL PRIMARY KEY,
  rule_name TEXT NOT NULL,
  path_pattern TEXT,                 -- regex ou glob: '*/01_CONTRATO/*'
  file_ext_pattern TEXT,             -- '.xer,.mpp' ou '*'
  name_pattern TEXT,                 -- regex no nome do arquivo
  target_agents TEXT[] NOT NULL,     -- ARRAY['M1','M2']
  doc_type TEXT NOT NULL,            -- classificação resultante
  priority TEXT DEFAULT 'media',
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### B6. Gateway de Escrita

```
Agente qualquer precisa salvar arquivo no SharePoint
    │
    ▼
Chama M20.write(drive_id, path, content, metadata)
    │
    ▼
M20 executa via Zapier Graph API:
    PUT https://graph.microsoft.com/v1.0/drives/{driveId}/root:/{path}:/content
    │
    ▼
Registra no sp_sync_log + atualiza sp_index
```

### B7. Interface com Agentes (protocolo inter-agente)

Cada agente pode invocar o SP Hub com 4 comandos:

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `M20.search(query, filters)` | Busca semântica/full-text | `M20.search("sondagem SPT Tocantins", {ext: "pdf"})` |
| `M20.feed(agent_code)` | Consulta docs pendentes para o agente | `M20.feed("M3")` → lista de novos DWGs |
| `M20.read(doc_id)` | Lê conteúdo completo de um documento | `M20.read("01KJQ3YI...")` |
| `M20.write(drive, path, content)` | Salva arquivo no SP | `M20.write(eng_drive, "/outputs/relatorio.pdf", blob)` |

### B8. Regras R1/R7

- **R1** — Nenhum output do SP Hub expõe nomes de empresas/fornecedores. Paths são sanitizados antes de entregar a outros agentes.
- **R7** — Toda operação do SP Hub recebe selo de qualidade:
  - ★☆☆ Básico: busca simples retorna lista de docs
  - ★★☆ Padrão: busca + classificação + routing automático
  - ★★★ Avançado: busca + classificação + routing + ingestão RAG + validação cruzada

---

## PARTE C — ROADMAP DE IMPLEMENTAÇÃO

### C1. Fase 1 — Ativação Mínima (Claude Code, ~2h)

- [ ] Deploy MantaBase MCP no Railway
- [ ] Primeira indexação completa: `python sp_indexer.py` (7 drives)
- [ ] Criar tabelas `sp_agent_feed` e `sp_routing_rules` no Supabase
- [ ] Inserir 24 routing rules iniciais baseadas no mapa B3
- [ ] Testar `search_sp_index()` com 5 queries representativas

### C2. Fase 2 — Delta + Notificação (~4h)

- [ ] Implementar `delta_sync.py` (compara snapshots, gera change_log)
- [ ] Configurar cron: `daily_index.sh` + `delta_sync.py` em sequência
- [ ] Implementar protocolo de alimentação proativa (B4)
- [ ] Testar com 3 agentes: M1 (Claims), M3 (Rodovias), M8 (BD)

### C3. Fase 3 — RAG Integration + Escrita (~4h)

- [ ] Conectar delta → M18 RAG Manager para ingestão automática
- [ ] Implementar gateway de escrita via Zapier Graph API
- [ ] Testar ciclo completo: doc novo → classificação → routing → RAG → agente consulta

### C4. Fase 4 — Consolidação (~2h)

- [ ] Atualizar SKILL.md do Manta 20 no SharePoint
- [ ] Atualizar routing map do Maestro v4.2 → v4.3
- [ ] Documentar no CLAUDE.md do Claude Code
- [ ] Rodar R7 ★★★ validation no ciclo completo

---

## METADADOS

```
Documento:    MANTA 20 — SP Hub Spec Consolidada
Versão:       2.0
Data:         06/07/2026
Gerado por:   Claude AI — Manta Associados
Classificação: Interno
ID:           MANTA-SPHUB-20260706-001
```
