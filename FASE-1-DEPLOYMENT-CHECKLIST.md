# FASE 1 — Expansão para 60 Agentes
## Deployment Checklist v5.0.0

**Status:** ✅ Inicial Criado — 2026-07-22

---

## 📋 Sumário Executivo

A Fase 1 expande a arquitetura de Manta Maestro de **20 para 60 agentes**:
- **11 Agentes Horizontais** (transversais) — maestro, claims, contratual, imobiliário, orçamento, modelagem, cronograma, BD, apresentações, advisory, arquiteto-IA
- **9 Agentes Verticais** por Segmento (S1-S4, S6-S10) — especialistas em rodovia, OAE, ferrovia, metrô, portos, aeroportos, saneamento, energia, barragens
- **40 Agentes Especializados por Fase** — 8 sub-agentes por segmento vertical (5 segmentos × 8 fases)

**Total:** 11 + 9 + 40 = **60 agentes operacionais**

---

## 🎯 Objetivos da Fase 1

- [x] Definir arquitetura completa de 60 agentes em `agents-config-60.json`
- [x] Criar schema Supabase com RAG e agent knowledge mapping
- [x] Implementar executor paralelo com suporte a 20 agentes simultâneos
- [x] Criar script de webhook SharePoint → Supabase com validação
- [ ] Deploy do schema Supabase em produção
- [ ] Inicializar dados de configuração de agentes
- [ ] Testar routing do maestro com 60 agentes
- [ ] Validar limites de concorrência
- [ ] Documentar playbook operacional

---

## 📂 Arquivos Criados na Fase 1

### Configuração
```
agents-config-60.json
  └─ Definição de 60 agentes com tiers, especialidades, RAG access, pesos de concorrência
```

### Supabase Schema
```
supabase/migrations/001_create_rag_and_agents_schema.sql
  ├─ rag_chunks — Armazenamento de chunks de conhecimento
  ├─ agent_knowledge_mapping — Mapeamento de acesso RAG por agente
  ├─ agent_execution_log — Rastreamento de execução paralela
  ├─ sharepoint_sync_log — Log de sincronização SP → Supabase
  ├─ rag_collection_status — Status agregado das coleções
  └─ Triggers, índices, e dados iniciais
```

### Scripts de Orchestração
```
scripts/maestro-parallel.sh
  └─ Executor de 60 agentes em paralelo (max 20 simultâneos)
  
scripts/webhook-sp-to-supabase.sh
  └─ Sincronização automatizada SharePoint → Supabase com validação
```

---

## 🔧 Checklist Técnico

### Pré-requisitos de Ambiente

- [ ] Variáveis de ambiente definidas:
  - `SUPABASE_URL` — URL do projeto Supabase
  - `SUPABASE_KEY` — Chave de API do Supabase
  - `SHAREPOINT_SITE` — URL do site SharePoint
  - `SHAREPOINT_TOKEN` — Token de autenticação SharePoint

- [ ] Ferramentas instaladas:
  - [ ] `jq` para processamento JSON
  - [ ] `curl` para requisições HTTP
  - [ ] `pdftotext` para extração de PDFs
  - [ ] `unzip` para processamento de DOCX/XLSX (opcional)

### Supabase

- [ ] Projeto Supabase criado e acessível
- [ ] Executar migração SQL:
  ```bash
  supabase db push --project-id <project-id>
  ```
- [ ] Verificar tabelas criadas:
  - `rag_chunks`
  - `agent_knowledge_mapping`
  - `agent_execution_log`
  - `sharepoint_sync_log`
  - `rag_collection_status`
- [ ] Verificar índices e triggers
- [ ] Validar dados iniciais (11 agentes horizontais + 5 agentes verticais)

### Configuração de Agentes

- [ ] Validar `agents-config-60.json`:
  ```bash
  jq . agents-config-60.json > /dev/null
  ```
- [ ] Verificar contagens:
  - Agentes Horizontais: 11 ✓
  - Agentes Verticais: 9 ✓
  - Agentes Especializados: 40 ✓
  - Total: 60 ✓

### Scripts de Orchestração

- [ ] Tornar scripts executáveis:
  ```bash
  chmod +x scripts/maestro-parallel.sh
  chmod +x scripts/webhook-sp-to-supabase.sh
  ```
- [ ] Validar syntax:
  ```bash
  bash -n scripts/maestro-parallel.sh
  bash -n scripts/webhook-sp-to-supabase.sh
  ```
- [ ] Testar maestro-parallel.sh com log:
  ```bash
  SUPABASE_URL=<url> SUPABASE_KEY=<key> ./scripts/maestro-parallel.sh
  ```
- [ ] Verificar saída de logs em `logs/maestro/`

### SharePoint Sync

- [ ] Testar webhook-sp-to-supabase.sh:
  ```bash
  SUPABASE_URL=<url> SUPABASE_KEY=<key> \
  SHAREPOINT_SITE=<site> SHAREPOINT_TOKEN=<token> \
  ./scripts/webhook-sp-to-supabase.sh
  ```
- [ ] Verificar saída de logs em `logs/sync/`
- [ ] Validar registros criados em `sharepoint_sync_log`

### Testes de Integração

- [ ] Test 1: Maestro carrega configuração corretamente
  - [ ] Todos os 60 agentes listados
  - [ ] Pesos de concorrência corretos
  - [ ] RAG access correto por agente

- [ ] Test 2: Paralelização respeitando limites
  - [ ] Max 20 agentes simultâneos
  - [ ] Pesos de concorrência balanceados
  - [ ] Logs de execução registrados

- [ ] Test 3: Sincronização SharePoint → Supabase
  - [ ] Detecta novos documentos
  - [ ] Extrai conteúdo corretamente
  - [ ] Valida com aluci-guard
  - [ ] Insere chunks em Supabase
  - [ ] Atualiza status de coleção

### Dados Iniciais

- [ ] RAG Collection Status inicializado para 5 coleções:
  - [ ] `san:` (Saneamento) — ALTA prioridade, Mensal
  - [ ] `ene:` (Energia) — ALTA prioridade, Semanal
  - [ ] `por:` (Portos) — Média prioridade, Semestral
  - [ ] `aer:` (Aeroportos) — Média prioridade, Semestral
  - [ ] `bar:` (Barragens) — Média prioridade, Trimestral

- [ ] Agent Knowledge Mapping inicializado:
  - [ ] 11 Agentes Horizontais com acesso a todas as 5 coleções
  - [ ] 9 Agentes Verticais com acesso a sua coleção respectiva
  - [ ] Weights de concorrência definidos

---

## 🚀 Próximos Passos (Fase 2)

Após conclusão da Fase 1:

1. **Fase 2 — População RAG:**
   - Populacional 950+ documentos nas 5 coleções
   - Validação automática com aluci-guard
   - Testes de busca semântica

2. **Fase 3 — Orchestração Avançada:**
   - Implementar load balancing por segmento
   - Fila de prioridades (ALTA > Média)
   - Monitoramento em tempo real

3. **Fase 4 — Sincronização Automática:**
   - Webhook de change events do SharePoint
   - Cron jobs para updates periódicos
   - Dashboard de status de sincronização

4. **Fase 5 — Dashboard de Monitoramento:**
   - Visualização de status de agentes
   - Métricas de execução
   - Alertas de falha

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Total de Agentes | 60 |
| Agentes Horizontais | 11 |
| Agentes Verticais (principais) | 9 |
| Sub-agentes Especializados | 40 |
| Max Concorrência | 20 |
| RAG Collections | 5 |
| Docs Estimados no RAG | 950+ |
| Fases do Ciclo de Vida | 8 |

---

## 📝 Notas Importantes

1. **Concorrência:** Máximo de 20 agentes simultâneos respeitando os pesos de concorrência definidos. Agentes mais pesados (peso 3) ocupam 3 slots.

2. **RAG Access:** Agentes horizontais têm acesso a todas as 5 coleções. Agentes verticais têm acesso apenas à sua coleção específica.

3. **Validação:** Todos os chunks inseridos via SharePoint passam por aluci-guard antes de serem armazenados em Supabase.

4. **Prioridades de Atualização:**
   - 🔴 ALTA: Saneamento (AYSÁ) — Mensal, Energia (ANEEL) — Semanal
   - 🟡 Média: Portos, Aeroportos, Barragens — Semestral/Trimestral

---

## 🔗 Referências

- Arquivo de configuração: `agents-config-60.json`
- Schema Supabase: `supabase/migrations/001_create_rag_and_agents_schema.sql`
- Executor paralelo: `scripts/maestro-parallel.sh`
- Webhook de sync: `scripts/webhook-sp-to-supabase.sh`
- Arquitetura v5.0.0: `sharepoint/ARQUITETURA-AGENTES-IA-v5.0.0.md`

---

**Mantido por:** mneves@mantaassociados.com  
**Data de criação:** 2026-07-22  
**Versão:** 5.0.0
