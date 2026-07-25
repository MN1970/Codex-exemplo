# Manta Maestro 60 — Sistema de Agentes IA v5.0.0

**Versão:** 5.0.0  
**Data:** 2026-07-22  
**Status:** Phase 1 Complete — 60 Agents Defined  
**Mantido por:** mneves@mantaassociados.com

---

## 📋 Visão Geral

Manta Maestro é um sistema distribuído de **60 agentes IA especializados** para otimizar projetos de infraestrutura em 9 segmentos setoriais (rodovia, OAE, ferrovia, metrô, portos, aeroportos, saneamento, energia, barragens).

### Três Eixos de Organização

```
EIXO 1: 11 Agentes Horizontais (Transversais)
├─ maestro (router)           — Intake + roteamento semântico
├─ claims                     — Reclamações / sinistros / garantias
├─ contratual                 — Contratos, RDC, concorrências
├─ imobiliário                — Propriedades, zoneamento, ocupação
├─ orçamento                  — Custos, composições, licitação
├─ modelagem                  — BIM, análise estrutural, simulação
├─ cronograma                 — Planejamento, sequência, recursos
├─ bd                         — Oportunidades, pipeline, negociação
├─ apresentações              — Decks, relatórios executivos, pitch
├─ advisory                   — Estratégia, direcionamento, valor
└─ arquiteto-ia               — Design de workflows, orquestração

EIXO 2: 9 Agentes Verticais por Segmento
├─ agente-infraestrutura-s1   — Rodovias (pavimento, drenagem, DNIT)
├─ agente-infraestrutura-s2   — OAE (estruturas, fundações)
├─ agente-infraestrutura-s3   — Ferrovia (via permanente, sinalização)
├─ agente-infraestrutura-s4   — Metrô (estações, túneis, sistemas)
├─ agente-portos              — Portos (terminais, berços, dragagem) 🆕
├─ agente-aeroportos          — Aeroportos (pistas, TPS, TECA) 🆕
├─ agente-saneamento          — Saneamento (ETA, ETE, adutoras) 🆕 AYSÁ
├─ agente-energia             — Energia (LT, subestações, geração) 🆕 ANEEL
└─ agente-barragens           — Barragens (vertedouro, rejeitos) 🆕

EIXO 3: 40 Sub-agentes Especializados por Fase
├─ Portos (S6) — 8 sub-agentes (1 por fase)
├─ Aeroportos (S7) — 8 sub-agentes (1 por fase)
├─ Saneamento (S8) — 8 sub-agentes (1 por fase)
├─ Energia (S9) — 8 sub-agentes (1 por fase)
└─ Barragens (S10) — 8 sub-agentes (1 por fase)
```

---

## 🏗️ Arquitetura

### Camadas Técnicas

| Camada | Responsabilidade | Componentes |
|--------|-----------------|------------|
| **Intake** | Recebimento de requisições | Maestro router, parsing semântico |
| **Routing** | Despacho para agente correto | Pattern-matching, heurísticas inteligentes |
| **Agentes** | Execução especializada | 60 agentes (horizontais + verticais + especializados) |
| **RAG** | Contexto temático e documental | 5 coleções Supabase (950+ docs) |
| **Orchestration** | Execução paralela (max 20) | maestro-parallel.sh com load balancing |
| **Sync** | SharePoint ↔ Supabase | webhook-sp-to-supabase.sh com validação |
| **Storage** | Persistência | Supabase + GitHub + SharePoint |
| **Output** | Formatação de resultados | Docs, relatórios, parecer técnico |

### RAG Collections (Retrieval Augmented Generation)

```json
{
  "saneamento": {
    "prefix": "san:",
    "documents": 200,
    "sources": ["SNIS", "IWA", "NBR 12211-12218", "Lei 14.026"],
    "priority": "🔴 ALTA (AYSÁ)",
    "update_frequency": "Mensal"
  },
  "energia": {
    "prefix": "ene:",
    "documents": 300,
    "sources": ["ANEEL", "EPE R1-R5", "ONS", "IEEE"],
    "priority": "🔴 ALTA (ANEEL)",
    "update_frequency": "Semanal"
  },
  "portos": {
    "prefix": "por:",
    "documents": 150,
    "sources": ["ANTAQ", "PIANC", "BNDES"],
    "priority": "🟡 Média",
    "update_frequency": "Semestral"
  },
  "aeroportos": {
    "prefix": "aer:",
    "documents": 120,
    "sources": ["ANAC/RBAC", "ICAO Annex 14"],
    "priority": "🟡 Média",
    "update_frequency": "Semestral"
  },
  "barragens": {
    "prefix": "bar:",
    "documents": 180,
    "sources": ["ICOLD", "CBDB", "SIGBM"],
    "priority": "🟡 Média",
    "update_frequency": "Trimestral"
  }
}
```

### 8 Fases do Ciclo de Vida

Todos os agentes verticais (S1–S10) suportam trabalho em todas as 8 fases:

1. **Estudo Prévio** — Pré-viabilidade, EVTE, conceitual
2. **Projeto Básico** — Definição de soluções, custos estimados
3. **Projeto Executivo** — Detalhamento completo, especificações
4. **Obra em Execução** — Supervisão, fiscalização
5. **Operação & Manutenção** — Gestão de ativo operacional
6. **Licitação/Competição** — Edital, concorrência, RDC
7. **Due Diligence / M&A** — Avaliação para transação
8. **Encerramento** — Descomissionamento, desativação

---

## 📂 Estrutura de Arquivos

```
Codex-exemplo/
├── agents-config-60.json                    # Definição de 60 agentes
├── CLAUDE.md                                # Master registry (v4.2)
├── FASE-1-DEPLOYMENT-CHECKLIST.md           # Checklist de deployment
├── README-60-AGENTS.md                      # Este arquivo
│
├── supabase/
│   └── migrations/
│       └── 001_create_rag_and_agents_schema.sql
│
├── scripts/
│   ├── maestro-parallel.sh                  # Executor paralelo (max 20 agentes)
│   └── webhook-sp-to-supabase.sh            # Sincronizador SP → Supabase
│
└── logs/
    ├── maestro/                             # Logs de execução do maestro
    └── sync/                                # Logs de sincronização SP
```

---

## 🚀 Quick Start

### 1. Setup Inicial

```bash
# Clone o repositório e acesse a branch de trabalho
git checkout claude/sharepoint-manta-maestro-5-tahryk

# Validar configuração de agentes
jq . agents-config-60.json | head -20

# Tornar scripts executáveis
chmod +x scripts/maestro-parallel.sh
chmod +x scripts/webhook-sp-to-supabase.sh
```

### 2. Deploy Supabase

```bash
# Definir credenciais de ambiente
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Executar migração
supabase db push --project-id your-project

# Verificar tabelas criadas
curl -s "$SUPABASE_URL/rest/v1/rag_chunks?limit=1" \
  -H "Authorization: Bearer $SUPABASE_KEY" | jq .
```

### 3. Testar Maestro Paralelo

```bash
# Executar com logging
./scripts/maestro-parallel.sh

# Ver logs
tail -f logs/maestro/maestro-*.log
```

### 4. Testar Sincronização SharePoint

```bash
# Definir credenciais SharePoint
export SHAREPOINT_SITE="https://yourtenant.sharepoint.com/sites/..."
export SHAREPOINT_TOKEN="your-access-token"

# Executar sincronização
./scripts/webhook-sp-to-supabase.sh

# Ver logs
tail -f logs/sync/webhook-sync-*.log
```

---

## 🔄 Fluxo de Execução

### Intake → Routing → Agente Especializado

```
Usuário submete requisição
    ↓
Maestro (Manta 00) — Parser Semântico
    ↓
Análise de Padrões de Menção
    ├─ Contém "saneamento|ETA|ETE|AYSÁ" → agente-saneamento (S8)
    ├─ Contém "transmissão|LT|ANEEL|ONS" → agente-energia (S9)
    ├─ Contém "porto|terminal|ANTAQ|dragagem" → agente-portos (S6)
    ├─ Contém "aeroporto|pista|ANAC|RBAC" → agente-aeroportos (S7)
    ├─ Contém "barragem|vertedouro|ICOLD" → agente-barragens (S10)
    └─ Padrões S1-S4 mantidos...
    ↓
Agente Vertical Especializado
    ↓
Verificação de Fase (1-8)
    ├─ Estudo Prévio → agente-x-estudo-previo
    ├─ Projeto Básico → agente-x-projeto-basico
    ├─ Projeto Executivo → agente-x-projeto-executivo
    ├─ Obra em Execução → agente-x-obra
    ├─ Operação & Manutenção → agente-x-operacao
    ├─ Licitação/Competição → agente-x-licitacao
    ├─ Due Diligence → agente-x-due-diligence
    └─ Encerramento → agente-x-encerramento
    ↓
Recuperação RAG (san:, ene:, por:, aer:, bar:)
    ↓
Processamento Especializado
    ↓
Output Formatado (Parecer Técnico / Relatório)
```

---

## ⚙️ Paralelização

### Estratégia de Load Balancing

```bash
# Máximo de 20 agentes simultâneos
# Weighted Round-Robin baseado em concurrency_weight

# Exemplo:
# Agente A (weight=2) — ocupa 2 slots
# Agente B (weight=3) — ocupa 3 slots
# Agente C (weight=1) — ocupa 1 slot

# Fila: [A, B, C, A, B, D, ...]
# Execução em lotes respeitando max=20 slots

for agent in ${all_agents[@]}; do
  weight=$(get_concurrency_weight "$agent")
  if (( current_weight + weight <= MAX_CONCURRENT_AGENTS )); then
    execute_agent_async "$agent" &
    current_weight=$((current_weight + weight))
  else
    wait  # Aguardar slot disponível
  fi
done
```

### Retry Policy

- **Max Attempts:** 4
- **Backoff:** 2s, 4s, 8s, 16s
- **Timeout:** 30s por agente

---

## 📊 Monitoramento

### agent_execution_log

```sql
SELECT 
  agent_id,
  status,
  COUNT(*) as executions,
  AVG(duration_ms) as avg_duration_ms
FROM agent_execution_log
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY agent_id, status
ORDER BY executions DESC;
```

### rag_collection_status

```sql
SELECT 
  collection_prefix,
  collection_name,
  total_documents,
  total_chunks,
  validated_chunks,
  ROUND(100.0 * validated_chunks / total_chunks, 2) as validation_percentage,
  last_update
FROM rag_collection_status
ORDER BY priority;
```

---

## 🔐 Segurança

### Validação Anti-Alucinação (aluci-guard)

Todos os chunks inseridos via SharePoint passam por validação antes de serem armazenados:

```bash
# Fluxo de validação
SharePoint Document
    ↓
Extract Content
    ↓
Validate with aluci-guard
    ├─ Confidence Score ≥ 0.85 → ✓ Insert
    └─ Confidence Score < 0.85 → ⚠ Mark as Pending
    ↓
Insert into Supabase (rag_chunks)
    ↓
Track in sharepoint_sync_log
```

### Controle de Acesso

```json
{
  "maestro": {
    "access_level": "admin",
    "collections": ["san:", "ene:", "por:", "aer:", "bar:"]
  },
  "agente-saneamento": {
    "access_level": "read_write",
    "collections": ["san:"]
  },
  "agente-energia": {
    "access_level": "read_write",
    "collections": ["ene:"]
  }
}
```

---

## 📅 Roadmap

### Fase 1: ✅ Arquitetura de 60 Agentes (Atual)
- [x] Definir especificações de 60 agentes
- [x] Criar schema Supabase para RAG + agents
- [x] Implementar executor paralelo (maestro-parallel.sh)
- [x] Implementar webhook de sincronização

### Fase 2: ⏳ População RAG (Próxima)
- [ ] Coletar 950+ documentos de fontes
- [ ] Extrair e chunkarizar conteúdo
- [ ] Validar com aluci-guard
- [ ] Inserir em 5 coleções Supabase

### Fase 3: ⏳ Orchestração Avançada
- [ ] Load balancing por segmento
- [ ] Fila de prioridades (ALTA > Média)
- [ ] Monitoramento em tempo real

### Fase 4: ⏳ Sincronização Automática
- [ ] Webhook change events SharePoint
- [ ] Cron jobs para updates periódicos
- [ ] Status dashboard

### Fase 5: ⏳ Dashboard de Monitoramento
- [ ] Visualização de status de agentes
- [ ] Métricas de execução
- [ ] Alertas de falha

---

## 📚 Referências

- **Arquitetura Completa:** [ARQUITETURA-AGENTES-IA-v5.0.0.md](sharepoint/ARQUITETURA-AGENTES-IA-v5.0.0.md)
- **Checklist de Deploy:** [FASE-1-DEPLOYMENT-CHECKLIST.md](FASE-1-DEPLOYMENT-CHECKLIST.md)
- **Configuração de Agentes:** [agents-config-60.json](agents-config-60.json)
- **Schema Supabase:** [supabase/migrations/001_create_rag_and_agents_schema.sql](supabase/migrations/001_create_rag_and_agents_schema.sql)
- **CLAUDE.md Master:** [CLAUDE.md](CLAUDE.md)

---

## 📞 Suporte

**Mantido por:** mneves@mantaassociados.com  
**Repositório:** mn1970/Codex-exemplo  
**Branch:** claude/sharepoint-manta-maestro-5-tahryk

---

**Versão:** 5.0.0 | **Data:** 2026-07-22 | **Status:** Phase 1 Complete
