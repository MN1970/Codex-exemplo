# Integração Cowork ↔ Manta Maestro v6.1.0

**Versão:** 1.0.0 (2026-08-03)  
**Status:** Operacional  
**Arquitetura:** Cowork Web + Maestro API + SharePoint Storage  

---

## Sumário Executivo

Manta Maestro v6.1.0 integra-se com Cowork para permitir:
- **Entrada de projetos** via formulário Cowork (web ou desktop)
- **Roteamento automático** para agentes especializados (S1–S14)
- **Colaboração em tempo real** com comentários + entregáveis
- **Armazenamento compartilhado** no SharePoint (fonte de verdade)
- **Rastreabilidade completa** (audit trail R1–R5)

---

## 1. Fluxo de Integração

### Fase 1: Intake do Projeto (usuário → Cowork)

1. **Usuário submete projeto** via Cowork Web Form:
   - Nome do projeto (ex: "BR-101 Duplicação 200km")
   - Descrição (texto livre)
   - Segmento(s) envolvido(s) — select box: S1–S14
   - Atividade(ies) — multi-select: A1–A11
   - Data-base orçamentária (texto)
   - Documentos anexados (PDF/DWG/XLSX)

2. **Dados salvos em Cowork DataBase:**
   - Tabela `projects` com ID único
   - Referência ao usuário (mneves@mantaassociados.com)
   - Status inicial: `pending_routing`

### Fase 2: Detecção & Roteamento (Cowork → Maestro API)

1. **Webhook Cowork → Maestro:**
   ```json
   POST /maestro/v6/intake
   {
     "project_id": "proj-br101-2026",
     "description": "BR-101 Duplicação 200km pavimentação DNIT",
     "user_email": "mneves@mantaassociados.com",
     "segments": ["S1"],
     "activities": ["A3", "A5"],
     "documents": [
       {"url": "cowork://docs/projeto.pdf", "type": "PDF"}
     ]
   }
   ```

2. **Maestro Detector (Manta 00):**
   - Analisa descrição + segmentos indicados
   - Detecta complexity: star1/star2/star3
   - Seleciona pool de agentes (8–16)
   - Gera contrato P2 com escopo esperado

3. **Callback para Cowork:**
   ```json
   {
     "project_id": "proj-br101-2026",
     "status": "routing_done",
     "agents_selected": [
       {"name": "agente-infraestrutura-S1", "tier": "sonnet"},
       {"name": "manta-05", "tier": "sonnet"},
       {"name": "manta-07", "tier": "sonnet"}
     ],
     "estimated_duration_min": 480,
     "token_budget": 450000,
     "maestro_workflow_id": "wf-br101-001"
   }
   ```

### Fase 3: Execução (Maestro Agentes em Paralelo)

1. **Cada agente recebe P2 com:**
   - Projeto ID
   - Descrição
   - Documentos (via SharePoint link)
   - Escopo esperado (quantidades, orçamento, cronograma)
   - Referências técnicas (RAG → Supabase)

2. **Execução paralela com QueueExecutor:**
   - Max 8 agentes simultâneos
   - Timeout 30s por agente
   - Rate limit recovery automático (2s, 4s, 8s, 16s)

3. **Consensus voting (3/5) em aspectos críticos:**
   - **Orçamento:** S1 + A3 + A4 devem concordar ±10%
   - **Cronograma:** S1 + A5 devem concordar ±5%
   - **Risco:** A10 + Maestro devem concordar em nível

### Fase 4: Entregáveis (Maestro → SharePoint → Cowork)

1. **Armazenamento em SharePoint:**
   - **Projeto executivo:** `04_IA/Manta-Maestro/01-segmentos/S1-rodovias/proj-br101-2026/PE.docx`
   - **Orcamento:** `...02-atividades/A3-orcamento/proj-br101-2026/ORC.xlsx`
   - **Cronograma:** `...02-atividades/A5-cronograma/proj-br101-2026/CRONOGRAMA.mpp`
   - **Audit log:** `...07-execucoes/proj-br101-2026/AUDIT.json` (R1–R5)

2. **Link de compartilhamento retorna a Cowork:**
   ```json
   {
     "project_id": "proj-br101-2026",
     "status": "completed",
     "deliverables": [
       {
         "type": "projeto_executivo",
         "format": "docx",
         "sp_link": "https://mnassociados.sharepoint.com/.../PE.docx",
         "size_bytes": 2458624
       },
       {
         "type": "orcamento",
         "format": "xlsx",
         "sp_link": "https://mnassociados.sharepoint.com/.../ORC.xlsx",
         "size_bytes": 1024576
       }
     ],
     "execution_time_sec": 583,
     "tokens_used": 437842,
     "metrics": {
       "consensus_auto_resolved": 2,
       "consensus_escalated": 0,
       "agent_count": 8
     }
   }
   ```

### Fase 5: Colaboração (Cowork → SharePoint → Slack)

1. **Comentários em Cowork** são sincronizados para SP:
   - Usuário comenta em "ajustar orçamento de fundação"
   - Webhook: `POST /maestro/v6/comment`
   - Armazenado em `proj-br101-2026/FEEDBACK.md` (R1 sanitizado)
   - Notificação via Slack: `@agente-infraestrutura-S1`

2. **Revisão de entregáveis:**
   - Usuário marca como "Aprovado" ou "Solicitado ajuste"
   - Status em `projects.status = approved | revision_requested`
   - Se revisão: roteamento automático para agentes + consensus novamente

---

## 2. Configuração Técnica

### Cowork Connector Settings

```json
// .claude/settings.json — seção Cowork
{
  "cowork": {
    "enabled": true,
    "workspace_id": "cowork-manta-associados",
    "base_url": "https://cowork.manta.internal",
    "api_key_env": "COWORK_API_KEY",
    "webhook_secret_env": "COWORK_WEBHOOK_SECRET",
    "sync_interval_sec": 60,
    "retry_policy": {
      "max_attempts": 3,
      "backoff_base_sec": 2
    }
  }
}
```

### SharePoint Connector Settings

```json
{
  "sharepoint": {
    "tenant_id": "env:SHAREPOINT_TENANT_ID",
    "site_url": "https://mnassociados.sharepoint.com/sites/Engenharia",
    "library": "04_IA",
    "root_folder": "Manta-Maestro",
    "auth_method": "oauth",
    "mcp_server": "mcp__SharePoint_Manta__*"
  }
}
```

### Supabase (RAG + Execuções)

```
Projeto: ogxxgvgtulrbbppshjie (sa-east-1)
Tabelas:
  - rag_collections (coleções por S/A/D)
  - agent_episodes (histórico de execuções)
  - maestro_routing_keywords (pattern matching)
  - cowork_projects (sync com Cowork)
  - cowork_feedback (comentários)
```

---

## 3. Segurança & Conformidade (R1–R5)

### R1 — Sanitização
- Nomes de empresas → `[CONCESS.]`
- Nomes de pessoas → iniciais (ex: "J.N.")
- BRL preserva data-base: `BRL 1.150.000.000 (data-base: 2026-07-01)`

### R2 — Não inventar
- Informação faltante = `null` + motivo
- Exemplo: "Sondagem não fornecida para km 15–20 → usar CBR conservador"

### R3 — Alertas críticos
- Via **Twilio** (não WhatsApp pessoal)
- Caso: orçamento >R$500M, cronograma >48 meses, risco crítico

### R4 — Buscar equivalente
- Se usuário fornece `.xlsx` isolado → buscar `.pdf`/`.docx` antes de citar
- Exemplo: "Orcamento.xlsx fornecido, mas SICRO-referencia nao declarado"

### R5 — Rastreabilidade BRL
- Toda citação financeira = data-base + fonte + TRACE
- Exemplo: `"R$ 125M (SICRO 2026-07-30, via agente-infraestrutura-S1, uuid: abc123)"`

### RLS Supabase
Habilitado para tabelas:
- `rag_collections` — read-only público + write service_role
- `maestro_routing_keywords` — read-only público + write service_role
- `cowork_projects` — read-only usuário (RLS por user_email) + write service_role

---

## 4. Monitoramento & Observabilidade

### Metrics Coletadas

| Métrica | Definição | Alerta se |
|---------|-----------|-----------|
| `execution_time_sec` | Tempo total projeto | > 900s (15 min) |
| `tokens_used` | Tokens consumidos | > budget |
| `consensus_rate` | % de decisões auto-resolvidas | < 85% |
| `agent_latency_p99` | Latência do agente mais lento | > 30s |
| `queue_depth` | Tasks na fila | > 16 |

### Dashboard Cowork

Usuário vê em tempo real:
- Status: `pending` → `routing` → `executing` → `completed`
- Agents ativos: barra de progresso
- Consensus voting: "Orçamento votando... 2/5 concordam"
- ETA para conclusão

### Logs (Audit Trail)

Cada execução gera `AUDIT.json`:
```json
{
  "project_id": "proj-br101-2026",
  "execution_id": "exec-001",
  "start_time": "2026-08-03T10:30:00Z",
  "maestro_version": "6.1.0",
  "agents": [
    {
      "name": "agente-infraestrutura-S1",
      "status": "completed",
      "duration_sec": 245,
      "tokens": 125000,
      "output_summary": "Projeto executivo + 5 disciplinas"
    }
  ],
  "consensus": [
    {
      "aspect": "orcamento",
      "voters": ["S1", "A3", "A4"],
      "threshold": 3,
      "result": "decided",
      "winner": "R$ 1.150.000.000"
    }
  ],
  "compliance": {
    "r1_sanitized": true,
    "r2_no_invention": true,
    "r3_alerts_sent": 0,
    "r4_equivalents_checked": 2,
    "r5_trace_complete": true
  },
  "end_time": "2026-08-03T10:40:48Z"
}
```

---

## 5. Roadmap Integração

### v6.1.0 (Operacional agora)
- ✅ Intake form Cowork
- ✅ Roteamento automático S1–S14
- ✅ Execução paralela 8 agentes
- ✅ SharePoint storage
- ✅ Audit trail R1–R5

### v6.2.0 (T2 — Próximas semanas)
- [ ] Template library (S.A.D específicos)
- [ ] Exemplares L3 (few-shot learning)
- [ ] Revisão iterativa (feedback loop)
- [ ] Slack integration nativa

### v6.3.0 (T3 — Setembro)
- [ ] Supabase RAG search frontend
- [ ] ML judge automático (rubricas por atividade)
- [ ] Integração Primavera P6 (cronogramas)
- [ ] PDF geração direto em Cowork

### v7.0.0 (Futuro)
- [ ] Multi-tenant (múltiplos clientes)
- [ ] API pública com auth
- [ ] Marketplace de disciplinas (D01–D23)

---

## 6. Troubleshooting

### Problema: Roteamento não encontra agentes

**Causa:** Keywords na descrição não matcham padrões S1–S14  
**Solução:** 
1. Verificar keywords em `CLAUDE.md § ROUTING`
2. Adicionar termos faltantes em `maestro_routing_keywords` (Supabase)
3. Usar `/maestro detect "sua descrição"` no CLI para testar

### Problema: Consensus escalated (< 3/5)

**Causa:** Agentes divergem em orçamento/cronograma  
**Solução:**
1. Aumentar voter set (adicionar A4 para modelagem)
2. Revisar documento de entrada (inconsistências?)
3. Marcar em Cowork como "revisão manual" → human_review

### Problema: SharePoint upload falha

**Causa:** Path errado, permissões, ou MCP offline  
**Solução:**
1. Verificar `folder_path` (não incluir nome da biblioteca)
2. Verificar permissões M365 (Sites.Manage.All)
3. Usar `list_libraries()` para confirmar acesso

---

## Suporte

**Contato:** mneves@mantaassociados.com  
**Docs:** https://mnassociados.sharepoint.com/sites/Engenharia/04_IA/Manta-Maestro/  
**Issues:** Cowork #manta-maestro-support  

---

**Autor:** Manta Code Agent · Versão 6.1.0  
**Próxima revisão:** 2026-09-01
