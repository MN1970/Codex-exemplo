# Observability Scripts — Manta Maestro v4.2

Conjunto de 4 scripts Python para observabilidade e validação do Maestro (Manta 00) e agentes verticais (S1-S10).

**Versão**: 1.0.0  
**Data**: 2026-07-25  
**Status**: Production Ready  

---

## Visão Geral

| Script | Função | Entrada | Saída | Exit Code |
|--------|--------|---------|-------|-----------|
| `sp_healthcheck.py` | Valida M365 + SharePoint + Key Vault | CLI args | JSON | 0/1 |
| `audit_agents.py` | Auditoria de divergência vs CLAUDE.md | `.claude/agents/*.md` | HTML/CSV/JSON | 0/1 |
| `eval_routing.py` | Avalia acurácia de roteamento | `tests/routing/prompts.md` | JSON/CSV | 0/1 |
| `init_rag_golden_set.py` | Cria 50 QA pairs para baseline RAG | Templates (hardcoded) | CSV + JSON | 0/1 |

---

## Instalação

```bash
# Clone repo e entre no diretório
cd /home/user/Codex-exemplo

# Instale dependências (Python 3.8+)
pip install -r scripts/requirements.txt

# (Optional) Para deployment em Azure (sp_healthcheck.py)
pip install azure-identity azure-keyvault-secrets requests
```

---

## Scripts em Detalhe

### 1. `sp_healthcheck.py` — Healthcheck M365 + SharePoint + Azure

**Objetivo**: Validar saúde operacional da integração Microsoft 365.

**Execução**:
```bash
python scripts/sp_healthcheck.py [--verbose] [--dry-run]
```

**Saída**:
```json
{
  "status": "ok" | "error" | "warning",
  "timestamp": "2026-07-25T10:30:00Z",
  "token_valid": true,
  "token_expires_in_days": 27,
  "last_write_at": "2026-07-25T10:30:00Z",
  "sharepoint_writable": true,
  "vault_accessible": true,
  "errors": []
}
```

**Casos de uso**:
- SessionStart hook (valida credenciais ao abrir session)
- Pré-deploy (assegura que M365 está operacional)
- Monitoramento em background (alertar se token expira em < 7 dias)

**Vars de ambiente**:
```bash
SHAREPOINT_TENANT_ID=<uuid>
AZURE_CLIENT_ID=<uuid>
AZURE_CLIENT_SECRET=<secret>
AZURE_KEYVAULT_NAME=manta-maestro-vault
SHAREPOINT_SITE_URL=https://tenant.sharepoint.com/sites/manta-maestro
```

---

### 2. `audit_agents.py` — Auditoria de Divergência

**Objetivo**: Validar que agentes em `.claude/agents/*.md` estão sincronizados com canonical registry (`CLAUDE.md` v4.2).

**Execução**:
```bash
# HTML report (padrão)
python scripts/audit_agents.py --verbose

# CSV report
python scripts/audit_agents.py --output-format csv

# JSON report com threshold
python scripts/audit_agents.py --output-format json --divergence-threshold 1
```

**Outputs**:
- `rag_evals/audit_agents.html` — Tabela formatada para review
- `rag_evals/audit_agents.csv` — Exportável para Excel
- `rag_evals/audit_agents.json` — Estruturado para CI/CD

**Colunas do report**:
| Campo | Descrição |
|-------|-----------|
| `agent_id` | Nome arquivo (agente-saneamento) |
| `agent_name` | Campo `name:` do frontmatter |
| `status` | synced / new / missing_from_canonical |
| `skill_version_pin` | Version em CLAUDE.md (v4.2) |
| `checksum_md5` | Hash do arquivo agent .md |
| `divergence_reason` | Causa divergência (se houver) |
| `last_sync_at` | Timestamp da auditoria |

**Casos de uso**:
- Pre-commit hook (falha se divergências > 0)
- Deploy validation (assegura agents estão alinhados)
- Compliance audit (rastrear mudanças em agent definitions)

---

### 3. `eval_routing.py` — Avaliação de Acurácia de Roteamento

**Objetivo**: Validar que Maestro roteia corretamente 30+ prompts-teste para agentes verticais (S1-S10).

**Execução**:
```bash
# Avalia roteamento (baseline BM25)
python scripts/eval_routing.py --verbose

# Com timeout customizado
python scripts/eval_routing.py --timeout 10

# CSV para análise manual
python scripts/eval_routing.py --output-format csv
```

**Teste Prompts** (extraídos de `tests/routing/prompts.md`):

| Segmento | Exemplo | Agente Esperado |
|----------|---------|-----------------|
| S6 Portos | "Dragagem para terminal de contêineres" | agente-portos |
| S7 Aeroportos | "Dimensionar pista para A320neo" | agente-aeroportos |
| S8 Saneamento | "Projetar ETA para 200k hab" | agente-saneamento |
| S9 Energia | "RAP para leilão de transmissão" | agente-energia |
| S10 Barragens | "CFRD de 80m altura" | agente-barragens |

**Métricas de Output**:
```json
{
  "accuracy_top1": 0.867,      // % prompts roteados corretamente (rank 1)
  "accuracy_top3": 0.933,      // % prompts nos top-3
  "total_tests": 30,
  "passed": 26,
  "failed": 4,
  "confusion_matrix": {
    "agente-saneamento": {
      "agente-saneamento": 8,
      "agente-energia": 1,
      "other": 0
    }
  },
  "slow_routes": [             // Latência > 2s
    {
      "prompt": "...",
      "latency_ms": 2345.67,
      "expected": "agente-energia",
      "actual": "agente-energia"
    }
  ]
}
```

**Exit code**:
- 0: Accuracy >= 80%
- 1: Accuracy < 80% ou erro crítico

**Casos de uso**:
- Validação pós-deploy (assegura routing está funcionando)
- A/B testing (comparar embeddings v1 vs v2)
- Performance monitoring (alertar se latência cresce)

---

### 4. `init_rag_golden_set.py` — Inicializar Golden Set

**Objetivo**: Criar baseline de 50 QA pairs para avaliação de qualidade RAG (retrieval-augmented generation).

**Execução**:
```bash
# Gera 50 QA pairs com seed=42 (reproduzível)
python scripts/init_rag_golden_set.py

# Customizar quantidade ou segmentos
python scripts/init_rag_golden_set.py --num-pairs 100 --segments saneamento,energia,portos

# Seed diferente (nova distribuição)
python scripts/init_rag_golden_set.py --seed 999
```

**Outputs**:
- `rag_evals/golden_set_v1.csv` — 50 linhas com QA pairs
- `rag_evals/golden_set_schema.json` — Schema de validação + metadados

**Formato CSV** (`golden_set_v1.csv`):
```
qa_id,question,golden_answer,agent_id,expected_chunks,difficulty_level,source_domain,created_at
qa_001,"Como dimensionar ETA ciclo completo...","ETA inclui coagulação...",agente-saneamento,"chunk_saneamento_1;chunk_saneamento_2;chunk_saneamento_3",medium,water_treatment,2026-07-25T...
qa_002,"Qual método calcular golpe de aríete...","Usar fórmula Joukowsky...",agente-saneamento,"chunk_saneamento_1;chunk_saneamento_4",hard,hydraulics,2026-07-25T...
...
```

**Distribuição de QA Pairs** (por padrão, 10 por segmento):
| Segmento | Questões | Domínios |
|----------|----------|----------|
| Saneamento (S8) | 10 | water_treatment, wastewater, regulation, hydraulics, etc. |
| Energia (S9) | 10 | transmission, substation, renewable_energy, standards, etc. |
| Portos (S6) | 10 | terminal_design, dredging, port_operation, standards, etc. |
| Aeroportos (S7) | 10 | airfield_design, navigation_aids, pavement_design, etc. |
| Barragens (S10) | 10 | dam_engineering, tailings_management, hazard_assessment, etc. |

**Métricas de Validação RAG** (schema JSON):
```json
{
  "evaluation_metrics": {
    "recall_at_5": "fração de QAs onde chunk esperado está em top-5",
    "mrr": "Mean Reciprocal Rank (posição média do melhor chunk)",
    "ndcg_5": "Normalized Discounted Cumulative Gain@5"
  }
}
```

**Casos de uso**:
- Baseline para RAG evaluation (BM25 vs embedding v1 vs v2)
- A/B testing em Supabase retrieval
- Documentação de domínio (golden answers como referência técnica)

---

## Ordem de Execução Recomendada

### Startup (quando novo agente é deployado):
```bash
# 1. Healthcheck M365
python scripts/sp_healthcheck.py > /tmp/health.json

# 2. Auditoria de agentes
python scripts/audit_agents.py --divergence-threshold 0
if [ $? -ne 0 ]; then echo "Agents not synced!"; exit 1; fi

# 3. Avalia roteamento
python scripts/eval_routing.py
if [ $? -ne 0 ]; then echo "Routing accuracy < 80%"; exit 1; fi

# 4. Inicializa golden set (uma única vez ou update periódico)
python scripts/init_rag_golden_set.py
```

### CI/CD Integration:
```yaml
# .github/workflows/observability.yml (exemplo)
name: Observability Checks
on: [push, pull_request]
jobs:
  healthcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Healthcheck
        run: python scripts/sp_healthcheck.py --verbose
        env:
          SHAREPOINT_TENANT_ID: ${{ secrets.SHAREPOINT_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      - name: Audit agents
        run: python scripts/audit_agents.py --divergence-threshold 1
      - name: Eval routing
        run: python scripts/eval_routing.py --timeout 10
```

### SessionStart hook (`.claude/settings.json`):
```json
{
  "hooks": {
    "sessionStart": {
      "command": "python scripts/sp_healthcheck.py --verbose",
      "timeout": 10,
      "onFailure": "warn"  // ou "error" para parar session
    }
  }
}
```

---

## Help e Troubleshooting

### Cada script tem `--help`:
```bash
python scripts/sp_healthcheck.py --help
python scripts/audit_agents.py --help
python scripts/eval_routing.py --help
python scripts/init_rag_golden_set.py --help
```

### Logging:
```bash
# Verbose mode (DEBUG level)
python scripts/audit_agents.py --verbose 2>&1 | tee audit.log

# Filter por componente
python scripts/sp_healthcheck.py 2>&1 | grep "azure_ad"
```

### Comuns Issues:

**`sp_healthcheck.py` falha com "Missing AZURE_CLIENT_ID"**
```bash
# Setup vars de ambiente
export AZURE_CLIENT_ID=<uuid>
export AZURE_CLIENT_SECRET=<secret>
export SHAREPOINT_TENANT_ID=<uuid>
python scripts/sp_healthcheck.py
```

**`audit_agents.py` relata divergências**
```bash
# Review HTML report
open rag_evals/audit_agents.html

# Check agent diff
git diff --no-pager .claude/agents/agente-saneamento.md
```

**`eval_routing.py` com accuracy < 80%**
```bash
# Debug confusão matrix
python scripts/eval_routing.py --output-format csv
# Analisar confusão_matrix em rag_evals/routing_eval.csv
# Considerar retraining de router (Maestro)
```

**`init_rag_golden_set.py` com seed diferente**
```bash
# Reproduzir exatamente mesmos 50 QAs
python scripts/init_rag_golden_set.py --seed 42

# Gerar novo dataset
python scripts/init_rag_golden_set.py --seed 999 --num-pairs 100
```

---

## Performance Notes

| Script | Tempo típico | Dependências | Notas |
|--------|-------------|--------------|-------|
| `sp_healthcheck.py` | 0.5-1s | Azure SDK (mock: 50ms) | Callout a Azure AD + SP + KV |
| `audit_agents.py` | 0.1-0.2s | I/O local | Lê 5 arquivos .md + CLAUDE.md |
| `eval_routing.py` | 2-5s | I/O + mock router | 30 prompts × ~100ms cada |
| `init_rag_golden_set.py` | 0.5s | I/O | Gera CSV + JSON, sem I/O remoto |

---

## Versionamento

**Versão dos scripts**: 1.0.0  
**Compatível com CLAUDE.md**: v4.2 (2026-07-05)  
**Python**: 3.8+  
**Última atualização**: 2026-07-25  

---

## Contato e Contribuições

Maintained by Manta Associados — IA & Observability Team.

Para reports ou sugestões:
- Email: ia-team@mantaassociados.com
- SharePoint: `/01-agentes-fundamentais/observability/`
