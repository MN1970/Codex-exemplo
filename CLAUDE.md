# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
Saneamento, Energia, Barragens).

---

## MAPA COMPLETO DE AGENTES — 20 agentes, 3 eixos

### Eixo 1 — Horizontais (transversais a todos os segmentos)

| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro (router) | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
| Manta 01 | claims | 02-C, manta-claims | Opus | ✅ Operacional |
| Manta 02 | contratual | manta-02, contratual | Sonnet | ✅ Operacional |
| Manta 04 | imobiliario | manta-04 | Sonnet | ✅ Operacional |
| Manta 05 | orcamento | manta-05 | Sonnet | ✅ Operacional |
| Manta 06 | modelagem | manta-06 | Sonnet/Opus | ✅ Operacional |
| Manta 07 | cronograma | manta-07 | Sonnet | ✅ Operacional |
| Manta 13 | bd | manta-13, business-dev | Sonnet | ✅ Operacional |
| Manta 14 | apresentacoes | manta-14-pptx | Sonnet | ✅ Operacional |
| Manta 15 | advisory | manta-15, advisory | Sonnet/Opus | ✅ Operacional |
| Manta 16 | arquiteto-ia | manta-15-arq | Opus | ✅ Operacional |

### Eixo 2 — Verticais por segmento (C3)

| Código | Segmento | Agente | Status |
|--------|----------|--------|--------|
| Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional |
| Manta 03-S2 | OAE (pontes, viadutos) | agente-infraestrutura (S2) | ✅ Operacional |
| Manta 03-S3 | Ferrovia | agente-infraestrutura (S3) | ✅ Operacional |
| Manta 03-S4 | Metrô | agente-infraestrutura (S4) | ✅ Operacional |
| Manta 03-S5 | Túneis | agente-infraestrutura (S2+S4) | ⚡ Parcial (coberto por S2/S4) |
| Manta 03-S6 | Portos | agente-portos | 🆕 Criado 2026-07-05 |
| Manta 03-S7 | Aeroportos | agente-aeroportos | 🆕 Criado 2026-07-05 |
| Manta 03-S8 | Saneamento | agente-saneamento | 🆕 Criado 2026-07-05 — PRIORIDADE AySA |
| Manta 03-S9 | Energia | agente-energia | 🆕 Criado 2026-07-05 — ANEEL/State Grid |
| Manta 03-S10 | Barragens | agente-barragens | 🆕 Criado 2026-07-05 |

### Eixo 3 — Ciclo de vida (8 fases)

Todos os agentes verticais suportam as 8 fases via intake Q2:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

---

## ROUTING — Maestro (Manta 00)

Regra de roteamento atualizada para Q1 do intake:

```
IF menção a saneamento|ETA|ETE|adutora|esgoto|AySA|drenagem urbana|SNIS
   → agente-saneamento (S8)

IF menção a transmissão|LT|subestação|ANEEL|RAP|leilão transmissão|ONS|EPE
   → agente-energia (S9)

IF menção a porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner|granel
   → agente-portos (S6)

IF menção a aeroporto|pista pouso|ANAC|ICAO|TPS|TECA|balizamento
   → agente-aeroportos (S7)

IF menção a barragem|vertedouro|CFRD|CCR|rejeitos|PNSB|ICOLD|CBDB|TSF
   → agente-barragens (S10)

# Regras existentes S1-S4 mantidas sem alteração
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1

IF menção a ponte|viaduto|OAE|NBR 7187|túnel rodoviário
   → agente-infraestrutura S2

IF menção a ferrovia|trilho|AMV|dormente|via permanente
   → agente-infraestrutura S3

IF menção a metrô|estação|NATM|PSD|linha 4|linha 5|VLT
   → agente-infraestrutura S4
```

### Smart Model Selection (Maestro logic)

O Maestro automaticamente escolhe o modelo baseado na **tarefa detectada**:

```
FUNÇÃO: smart_model_selection(task_type, context, cost_priority=false)

IF task_type IN [extração_dados, quantidades, engenharia]:
   model = "sonnet-5"  # Precisão crítica
   confidence = 0.95

ELIF task_type IN [visão_multimodal, pdf_raster]:
   model = "opus-4-8"  # Fallback: Sonnet 4.6
   confidence = 0.90

ELIF task_type IN [roteamento, decisão_inicial]:
   model = "haiku-4-5"  # Rápido primeiro, depois escala se needed
   confidence = 0.85

ELIF task_type IN [análise_jurídica, contratual, claims]:
   model = "opus-4-8"  # Máximo raciocínio
   confidence = 0.95

ELIF task_type IN [agentic_qa, iteração]:
   model = "sonnet-4-6"  # Custo-benefício agentes
   confidence = 0.90

ELSE:
   model = "sonnet-5"  # Default seguro

# Override por custo_priority
IF cost_priority AND task_type IN [síntese, relatórios]:
   model = "haiku-4-5"  # Fallback barato

RETURN { model, confidence, reasoning }
```

**Exemplos de decisão automática:**
- Usuário: "Extraia dados do DXF da barragem" → **Sonnet 5** (extração_dados)
- Usuário: "Calcule volumes de corte/aterro" → **Sonnet 5** (quantidades)
- Usuário: "Qual agente chamar?" → **Haiku** (roteamento, depois escala)
- Usuário: "Analise o contrato" → **Opus 4.8** (análise_jurídica)
- Usuário: "Chat AskCAD" → **Sonnet 4.6** (agentic iterativo)

---

## MODELOS — Smart Model Selection por Tarefa

Estratégia inteligente de seleção de modelos baseada na tarefa. O **Maestro (Manta 00)** escolhe automaticamente o melhor modelo considerando **precisão**, **custo** e **velocidade**.

### Matriz de Modelos por Tarefa

| Tarefa | Segmento | Melhor Modelo | Razão | Fallback |
|--------|----------|---------------|-------|----------|
| **Extração de dados** (DXF/DWG/PDF) | Todos | **Sonnet 5** | Visão + OCR preciso | Opus 4.8 |
| **Quantidades/volumes** (balanço, pavimentação, iluminação) | S1, S8-S10 | **Sonnet 5** | Matemática + geometria | Sonnet 4.6 |
| **Análise estrutural** (OAE, estrutural) | S2, S1 | **Sonnet 5** | Engenharia complexa | Opus 4.8 |
| **Matching semântico** (orçamento SICRO/TPU) | Todos | **Sonnet 5** | Embeddings + numéricos | Haiku |
| **Roteamento/decisão** (maestro, primeira pass) | Todos | **Haiku** | Rápido + barato | Sonnet 5 |
| **Fallback vision** (sondagem PDF raster) | S1, S8 | **Opus 4.8** | Visão multimodal | Sonnet 4.6 |
| **Agentic Q&A** (AskCAD co-pilot) | Todos | **Sonnet 4.6** | Agente iterativo | Opus 4.8 |
| **Síntese/relatórios** (advisory, apresentações) | Todos | **Sonnet 5** | Qualidade redação | Haiku |
| **Análise contratual** (claims, contratual) | Todos | **Opus 4.8** | Raciocínio jurídico | Sonnet 5 |
| **Modelagem 3D/cenários** (landxml, terraplenagem) | S1, S8-S10 | **Sonnet 5** | Cálculos de momento | Haiku |

### Critérios de Decisão (ordem de precedência)

```
1. PRECISÃO CRÍTICA (dados/quantidades/engenharia)
   → Sonnet 5 (sempre)

2. ANÁLISE JURÍDICA/CONTRATUAL
   → Opus 4.8 (máximo raciocínio)

3. VISÃO MULTIMODAL (PDF raster, imagens)
   → Opus 4.8 > Sonnet 4.6

4. ITERAÇÃO/AGENTIC (múltiplas voltas)
   → Sonnet 4.6 (custo-benefício) > Opus 4.8

5. ROTEAMENTO/DECISÃO (primeira pass)
   → Haiku (rápido + barato)

6. SÍNTESE/RELATÓRIOS
   → Sonnet 5 (qualidade)
```

### Tabela de Custos Relativos (benchmark)

| Modelo | Custo | Velocidade | Qualidade | Uso ideal |
|--------|-------|-----------|-----------|-----------|
| Haiku 4.5 | 🟢 Mínimo | 🟢 Máxima | 🟡 Boa | Roteamento, iteração rápida |
| Sonnet 5 | 🟡 Moderado | 🟡 Alta | 🟢 Excelente | Tarefas críticas (default) |
| Sonnet 4.6 | 🟡 Moderado | 🟡 Alta | 🟢 Excelente | Agentes (AskCAD) |
| Opus 4.8 | 🔴 Alto | 🔴 Mais lento | 🟢 Máxima | Jurídico, visão, fallback |

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES | 🆕 v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE | 🆕 v4.2 |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |

---

## SHAREPOINT — Routing rules (sp_agent_routing)

| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
| agente-energia | 03_Projetos/Energia/* | *.pdf, *.dwg, *.xlsx |
| agente-portos | 03_Projetos/Portos/* | *.pdf, *.dwg, *.xlsx |
| agente-aeroportos | 03_Projetos/Aeroportos/* | *.pdf, *.dwg, *.xlsx |
| agente-barragens | 03_Projetos/Barragens/* | *.pdf, *.dwg, *.xlsx |

---

## WORKFLOW PRONTO — Maestro Smart Routing

Implementação concreta do roteamento inteligente com seleção automática de modelo.

**Arquivo:** `.claude/workflows/maestro-smart-router.js`

```javascript
export const meta = {
  name: 'maestro-smart-router',
  description: 'Intelligent agent routing with automatic model selection (Haiku→Sonnet→Opus)',
  phases: [
    { title: 'Detect', detail: 'Identify task type and segment' },
    { title: 'Route', detail: 'Call agent with optimal model' },
    { title: 'Synthesize', detail: 'Consolidate results' },
  ]
}

// Task type detection
const TASK_KEYWORDS = {
  'extração_dados': ['extrair', 'dados', 'dxf', 'dwg', 'pdf', 'informações'],
  'quantidades': ['volume', 'área', 'quantidade', 'balanço', 'corte', 'aterro', 'pavimentação'],
  'engenharia': ['projeto', 'análise', 'estrutura', 'oae', 'ponte', 'viaduto', 'barragem'],
  'jurídica': ['contrato', 'cláusula', 'análise legal', 'claims', 'risco'],
  'agentic': ['chat', 'pergunta', 'ajuda', 'analise isso'],
}

const SEGMENT_MAP = {
  'saneamento|eta|ete|esgoto': 'agente-saneamento',
  'energia|transmissão|lt|subestação': 'agente-energia',
  'porto|terminal|dragagem': 'agente-portos',
  'aeroporto|pista|icao|anac': 'agente-aeroportos',
  'barragem|rejeitos|cfrd': 'agente-barragens',
  'rodovia|pavimento|dnit': 'agente-infraestrutura-s1',
  'oae|ponte|viaduto|nbre|7187': 'agente-infraestrutura-s2',
  'ferrovia|trilho|via permanente': 'agente-infraestrutura-s3',
  'metrô|estação|natm|psd': 'agente-infraestrutura-s4',
}

function detect_task_and_segment(input) {
  const lower = input.toLowerCase()
  
  let task_type = 'síntese'
  for (const [ttype, keywords] of Object.entries(TASK_KEYWORDS)) {
    if (keywords.some(k => lower.includes(k))) {
      task_type = ttype
      break
    }
  }
  
  let segment = null
  for (const [pattern, agent] of Object.entries(SEGMENT_MAP)) {
    if (new RegExp(pattern).test(lower)) {
      segment = agent
      break
    }
  }
  
  return { task_type, segment }
}

function select_optimal_model(task_type, segment) {
  const model_by_task = {
    'extração_dados': 'sonnet-5',
    'quantidades': 'sonnet-5',
    'engenharia': 'sonnet-5',
    'jurídica': 'opus-4-8',
    'agentic': 'sonnet-4-6',
    'roteamento': 'haiku',
    'síntese': 'sonnet-5',
  }
  return model_by_task[task_type] || 'sonnet-5'
}

phase('Detect')
const detection = detect_task_and_segment(args)
log(`📊 Detectado: task=${detection.task_type}, segment=${detection.segment}`)

phase('Route')
const optimal_model = select_optimal_model(detection.task_type, detection.segment)
log(`🎯 Modelo selecionado: ${optimal_model}`)

const result = await agent(args, {
  subagent_type: detection.segment || 'claude',
  model: optimal_model,
  label: `${detection.segment}@${optimal_model}`,
})

phase('Synthesize')
const synthesis = await agent(
  `Resume o resultado: ${result}`,
  { model: 'haiku', schema: { summary: 'string', confidence: 'number' } }
)

return {
  original_result: result,
  synthesis: synthesis.summary,
  task_type: detection.task_type,
  segment: detection.segment,
  model_used: optimal_model,
  confidence: synthesis.confidence,
}
```

**Como usar:**
```bash
# Chamar via CLI do Claude Code
/workflow maestro-smart-router "Extraia dados de quantidades do projeto de barragem em Brumadinho"

# Resultado esperado:
# ✅ Detectado: task=quantidades, segment=agente-barragens
# ✅ Modelo: sonnet-5
# ✅ Resultado: [dados extraídos com alta precisão]
```

---

## DEPLOY CHECKLIST v4.3 (Smart Model Selection)

**v4.2 (7 jul):**
- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [ ] Criar 5 coleções RAG em Supabase (`rag_chunks`)
- [ ] Inserir 5 routing rules em `sp_agent_routing`
- [ ] Criar pastas SP para novos segmentos
- [ ] Registrar skills no catálogo (skill registry)
- [ ] Testar routing do Maestro com prompts de cada segmento
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge

**v4.3 (16 jul) — Smart Model Selection:**
- [x] Matriz de modelos por tarefa (MODELOS section)
- [x] Critérios de decisão (roteamento automático)
- [x] Workflow maestro-smart-router.js pronto
- [x] Quick start guide + exemplos
- [ ] Testar maestro-smart-router com 10 prompts reais
- [ ] Documentar no SharePoint: `ARQUITETURA-MODELOS-IA.md` (v1.0.0)
- [ ] Treinar equipe no criterio "Sonnet 5 para dados críticos"
- [ ] Gate humano: aprovação MN antes de merge

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
└── .claude/
    └── agents/
        ├── agente-portos.md          # 🆕 S6
        ├── agente-aeroportos.md      # 🆕 S7
        ├── agente-saneamento.md      # 🆕 S8 — prioridade AySA
        ├── agente-energia.md         # 🆕 S9 — ANEEL/State Grid
        └── agente-barragens.md       # 🆕 S10
```

Os agentes existentes (Manta 00, 01, 02, 04-07, 13-16, 03-S1..S4) vivem
no repositório operacional do Maestro. Este repositório (`Codex-exemplo`)
serve como referência canônica versionada dos agentes verticais e do
mapa de routing.

---

## QUICK START — Smart Model Routing

**Resumo executivo para usar o Maestro inteligente:**

### Passo 1: Invoque uma tarefa (qualquer uma)
```
"Extraia quantidades de corte/aterro do projeto de barragem em Brumadinho"
```

### Passo 2: Maestro detecta automaticamente
```
✅ Tarefa: quantidades (dado numérico crítico)
✅ Segmento: agente-barragens (S10)
✅ Modelo: sonnet-5 (precisão máxima)
```

### Passo 3: Resultado com confiança
```
{
  quantidades: {
    corte_m3: 12450,
    aterro_m3: 8900,
    deficit_m3: 3550
  },
  confidence: 0.98,
  model_used: "sonnet-5",
  segment: "agente-barragens"
}
```

### Exemplos por tipo de tarefa:

| Input | Detecção | Modelo | Tempo est. |
|-------|----------|--------|-----------|
| "Extraia dados da sondagem em PDF" | extração_dados → S8 | Sonnet 5 | 45s |
| "Calcule DMT e Brückner" | quantidades → S1 | Sonnet 5 | 60s |
| "Analise o contrato de concessão" | jurídica | Opus 4.8 | 90s |
| "Qual segmento?" | roteamento | Haiku | 5s |
| "Chat: como extrair??" | agentic → AskCAD | Sonnet 4.6 | 30s |

### Critério de decisão automática:

```
📊 Dados críticos (extração, quantidades, engenharia)
   → Sonnet 5 SEMPRE (precisão > custo)

⚖️ Análise jurídica (contratos, claims)
   → Opus 4.8 (máximo raciocínio)

🤖 Chat/iterativo (AskCAD, Q&A)
   → Sonnet 4.6 (custo-benefício agente)

⚡ Roteamento/decisão (primeira pass)
   → Haiku (rápido, depois escala)

📝 Síntese/relatórios
   → Sonnet 5 (qualidade)
```

### Usar Haiku se prioridade é CUSTO/SPEED:
```javascript
// Override automático (ativar apenas se custo é constraint crítico)
smart_model_selection(task_type, context, cost_priority=true)
// → seleciona Haiku mesmo para tarefas críticas
```

---

## Histórico de versões

- **v4.3** (2026-07-16) — Smart model selection. Matriz de modelos por
  tarefa (Haiku/Sonnet 5/Opus 4.8). Workflow `maestro-smart-router.js`
  com detecção automática de tarefa + roteamento inteligente. Prioriza
  **Sonnet 5 para dados críticos**, Haiku para roteamento/iteração.
  Ticket MNT-2026-SMART-MODELS-ROUTING.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
