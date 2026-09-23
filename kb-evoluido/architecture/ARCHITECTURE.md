# ARCHITECTURE.md — KB Evoluído do Manta Maestro

**Versão**: 1.0.0 (2026-07-30)  
**Status**: Especificação de design  
**Responsável**: Manta Associados — Maestro Knowledge Systems  
**Público**: Arquitetos IA, Engenheiros de ML, Product Owners

---

## Sumário Executivo

O **KB Evoluído** é um sistema de aprendizado contínuo que transforma projetos finalizados (rodovias, saneamento, energia, portos, aeroportos, barragens) em conhecimento estruturado e operacional para os agentes do Manta Maestro.

Diferentemente de um KB estático, o sistema **coleta**, **processa**, **valida** e **realimenta** constantes, templates, padrões de custo, cronogramas e regras de negócio diretamente dos projetos reais, mantendo histórico completo e permitindo rollback.

**Pilares**:
1. **Ingestion em Tempo Real**: dados de projetos finalizados entram na Ingestion Layer
2. **Processamento Inteligente**: análise + clustering + outlier detection
3. **Feedback Loop**: aprendizado → atualização do RAG em Supabase → versioning
4. **Auditoria Total**: quem mudou quê, quando, e por quê

---

## 1. Visão Geral Arquitetural — 3 Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE LAYER                              │
│  (Supabase RAG + Templates + Constantes + Regras de Negócio)    │
│  - kb_chunks (versionado: v1.0, v1.1, v2.0, ...)               │
│  - kb_metadata (trilha de auditoria)                             │
│  - kb_snapshots (rollback)                                       │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ commit + versioning
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                              │
│  (Análise + ML + Validação por Especialistas)                   │
│  - Feature extraction (custo/metro, duração/fase, taxa falha)   │
│  - Clustering (agrupamento por tipologia)                       │
│  - Outlier detection (anomalias)                                │
│  - Pattern matching (regras recorrentes)                         │
│  - Expert validation (agentes S1-S10 certificam)                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ dados brutos + metadados
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   INGESTION LAYER                               │
│  (Coleta de Dados de Projetos Finalizados)                      │
│  - SharePoint (projeto finalizado → .pdf, .xlsx, .dwg)          │
│  - Projetos do ERP (custo real, duração real, incidências)      │
│  - Banco de Dados Operacional (evento finalizado = trigger)     │
│  - Upstream APIs (DNIT, ANEEL, ANTAQ, AySA, ICOLD)             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.1 Ingestion Layer — Fontes de Dados

| Fonte | Tipo | Frequência | Gatilho | Dados principais |
|-------|------|-----------|---------|------------------|
| SharePoint (03_Projetos/*) | Documentos | Contínua | Projeto finalizado marcado em SP | PDF técnicos, relatórios |
| ERP (SAP/Oracle) | Transacional | Diária | Fase finalizada | Custo real, duração, recursos |
| Banco Operacional | Eventos | Real-time | webhook | Status mudança, marcos, incidências |
| DNIT (S1) | API/Feed | Semanal | Release de dados | Índices de custos, composições SICRO |
| ANEEL (S9) | Edital/Resolução | Mensal | Publicação | Taxas, normas, requisitos novos |
| ANTAQ (S6) | Portaria | Trimestral | Publicação | Dragas, composições, regulamentações |
| AySA (S8) | Contrato | Ad-hoc | Entrega de projeto | Topologias de redes, custos unitários |
| CBDB/ICOLD (S10) | Publicação | Anual | Release | Barragens benchmark, classificação |

### 1.2 Processing Layer — 4 Sub-pipelines

#### a) **Feature Extraction**
Converte documentos brutos em features estruturadas:
- Custo por unidade ($/m de rodovia, $/km de LT, $/m³ de ETA)
- Duração por fase (meses de projeto básico, duração obra)
- Taxa de deflação/escalonamento (IPC, índice específico)
- Índices de risco (clima, geologia, social)
- Recursos alocados (engenheiros/dia, equipamentos)

**Tecnologia**: spaCy + regex + LLM extraction (para docs não-estruturados)

#### b) **Clustering & Categorização**
Agrupa projetos similares para derivar **constantes** do Maestro:
- Clustering por tipologia (rodovia urbana vs rural, ETA vs ETE)
- Subtipologia (ex: rodovia duplicada em solo mole)
- Geografia (bioma, clima, região de custo)
- Época de execução

**Output**: centróides que alimentam templates padrão dos agentes

#### c) **Outlier Detection**
Identifica anomalias que precisam revisão humana:
- Projeto com custo 3σ acima da média (possível erro ou novidade)
- Cronograma muito fora da curva (atraso significativo)
- Taxa de incidência acima do usual

**Output**: flags + notify Maestro S1-S10 relevante para investigação

#### d) **Pattern Matching & Rule Extraction**
Descobre padrões recorrentes em dados estruturados:
- Regra: "se solo mole + drenagem deficiente → atraso de X meses"
- Regra: "se deflação acumulada > Y% → revisar tarifa"
- Regra: "se classe de risco Z → executar monitoramento D"

**Output**: regras expressas em Prolog/JSON para Maestro

### 1.3 Knowledge Layer — 3 Dimensões

#### Dimensão A: **KB Chunks (RAG)**
Fragmentos de conhecimento versionados em `kb_chunks`:
```sql
table: kb_chunks
columns:
  id: uuid
  segment: varchar (S1-S10)
  kb_version: varchar (e.g., "S1-v2.3")
  chunk_text: text
  chunk_type: enum ('constant', 'template', 'rule', 'example', 'benchmark')
  confidence: float (0.0-1.0)
  source_project: varchar (id do projeto)
  created_at: timestamp
  updated_at: timestamp
  created_by: varchar (agente que validou)
  parent_version: varchar (anterior)
  tags: jsonb
```

#### Dimensão B: **Metadata & Auditoria**
Trilha de quem mudou o quê em `kb_metadata`:
```sql
table: kb_metadata
columns:
  id: uuid
  chunk_id: uuid (fk → kb_chunks)
  change_type: enum ('create', 'update', 'deprecate', 'rollback')
  changed_by: varchar (e.g., "agente-saneamento", "human-reviewer")
  reason: text (ex: "baseado em 5 projetos AySA 2025-2026")
  validation_status: enum ('pending', 'approved', 'rejected', 'superseded')
  approved_by: varchar (human ou agente de tier superior)
  created_at: timestamp
  superseded_by: uuid (fk para versão nova)
```

#### Dimensão C: **KB Snapshots & Rollback**
Histórico completo para rollback em `kb_snapshots`:
```sql
table: kb_snapshots
columns:
  id: uuid
  snapshot_id: varchar (e.g., "S8-saneamento-20260730-1400")
  segment: varchar
  kb_version_at_snapshot: varchar
  snapshot_data: jsonb (estado completo do KB naquele momento)
  triggered_by: varchar (quem iniciou)
  reason: text (ex: "rollback após outlier detection falso")
  created_at: timestamp
  can_restore_to: boolean
```

---

## 2. Fluxo de Dados — Feedback Loop

```
                    ┌──────────────────────────────┐
                    │   PROJETO FINALIZADO         │
                    │  (Saneamento ETA, Rodovia,   │
                    │   Energia LT, etc)           │
                    └──────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────────┐
                    │  1. INGESTION TRIGGER        │
                    │  (webhook ou batch diário)    │
                    │  Coleta: documentos, ERP,    │
                    │  marcadores de status         │
                    └──────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────────┐
                    │  2. FEATURE EXTRACTION       │
                    │  spaCy + regex + LLM         │
                    │  Output: vetor de features   │
                    └──────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────────┐
                    │  3. CLUSTERING & PATTERN     │
                    │  sklearn (KMeans, DBSCAN)    │
                    │  → centróides + regras       │
                    └──────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
         ┌─────────────────────┐  ┌─────────────────────┐
         │  4a. OUTLIERS       │  │  4b. PATTERNS OK    │
         │  (Anomalias)        │  │  (Dentro da curva)  │
         │  ↓ flag humano      │  │  ↓ auto-approve     │
         │  ↓ rever manual     │  │  ↓ pronto para KB   │
         └─────────────────────┘  └─────────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────────┐
              │  5. EXPERT VALIDATION                │
              │  (Agente S1-S10 especializado)       │
              │  ✓ Certifica novo conhecimento       │
              │  ✗ Rejeita (volta ao step 2)         │
              └──────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
         ┌─────────────────────┐  ┌─────────────────────┐
         │  APROVADO           │  │  REJEITADO          │
         │  ↓ insert em        │  │  ↓ log + notifica   │
         │    kb_chunks (v+1)  │  │    Maestro          │
         │  ↓ update metadata  │  │  ↓ volta ao source  │
         │  ↓ snapshot         │  │    para revisão     │
         └─────────────────────┘  └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────┐
         │  6. BROADCAST TO AGENTS         │
         │  S1-S10 recebem atualização     │
         │  (RAG refresh, templates novos) │
         └─────────────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────┐
         │  7. METRIC TRACKING             │
         │  Confidence score               │
         │  Adoption rate by agents        │
         │  Feedback loop closes           │
         └─────────────────────────────────┘
```

### 2.1 Gatilhos de Ingestion

| Cenário | Gatilho | Latência | Ação |
|---------|---------|----------|------|
| Projeto finalizado no ERP | Status = "Encerrado" | < 1h | Inicia pipeline |
| Documento novo no SharePoint | Upload em 03_Projetos/* | < 30min | OCR + extraction |
| DNIT publica SICRO novo | API feed | Diária | Atualiza constantes S1 |
| ANEEL lança edital | Email + web scrape | Semanal | Novo chunk S9 |
| Feedback humano | Agente rejeita chunk | Real-time | Volta ao step 3 |
| Rollback demand | Maestro ou human | Real-time | Restore de snapshot |

### 2.2 Estados de Validação

```
pending → approved → live (em kb_chunks)
  ↓
  └→ rejected → (log + voltar ao source)

live → superseded (quando nova versão entra)
  ↓
  └→ deprecated (versão antiga, ainda consultável)

live → rolled_back (se anomalia detectada pós-deploy)
  ↓
  └→ (volta a pending para revisão)
```

---

## 3. Componentes Principais

### 3.1 KB Versioned

**Responsabilidade**: Versionamento semântico do conhecimento base

**Estrutura de versões**: `{SEGMENT}-v{MAJOR}.{MINOR}.{PATCH}`

Exemplos:
- `S1-v2.3.1` (Rodovias: v2 com breaking change em índice de custo SICRO)
- `S8-v1.0.0` (Saneamento: versão inicial baseada em 5 projetos AySA)
- `S9-v1.1.0` (Energia: novo chunk sobre leilão de transmissão)

**Regras**:
1. **MAJOR** sobe quando breaking change (ex: novo índice de custo)
2. **MINOR** sobe quando novo feature (ex: novo tipo de ETA)
3. **PATCH** sobe quando bugfix ou refinamento

**Arquivo**: `kb_versions.json` no repositório
```json
{
  "S1": {
    "latest": "S1-v2.3.1",
    "stable": "S1-v2.3.0",
    "previous": ["S1-v2.2.5", "S1-v2.1.0"]
  },
  "S8": {
    "latest": "S8-v1.0.0",
    "stable": "S8-v1.0.0",
    "previous": []
  }
}
```

### 3.2 Feedback System

**Responsabilidade**: Capturar aprendizado contínuo de projetos reais

**Componentes**:

#### a) **Project-to-KB Extractor**
Aplicação (Python + FastAPI) que:
1. Lê projeto finalizado (SharePoint + ERP)
2. Extrai features via spaCy + regex + LLM
3. Classifica por segment (S1-S10)
4. Submete ao Processing Layer

#### b) **Confidence Scoring**
Cada novo chunk recebe score baseado em:
- Número de projetos que corroboram (n ≥ 3 para passar)
- Variância estatística (se σ < threshold)
- Agreement de agentes especialistas (≥ 2/3)

Fórmula:
```
confidence = (n_projects / 5) * 0.4 + 
             (1 - normalized_variance) * 0.4 +
             (expert_agreement / 1.0) * 0.2
```

#### c) **Human-in-the-Loop Gates**
1. **Outlier review**: human valida anomalias antes de entrar no KB
2. **Expert approval**: agente S1-S10 assina cada novo chunk
3. **Quarterly audit**: revisão de todas as entradas do trimestre

### 3.3 ML Pipeline

**Tecnologias**:
- **Feature extraction**: spaCy, Hugging Face NER, regex
- **Clustering**: scikit-learn (KMeans, DBSCAN, hierarchical)
- **Outlier detection**: Isolation Forest, Local Outlier Factor (LOF)
- **Pattern matching**: MLflow + custom Prolog engine

**Métricas trackadas**:
- Silhouette score (qualidade de clustering)
- Outlier percentage (anomalias por segment)
- Precision / Recall (validação de padrões extraídos)
- Adoption rate by agents (quantas vezes usaram novo chunk)

**Output**:
```
ml_results.json
├── clusters
│   ├── S1
│   │   ├── cluster_0: "rodovia duplicada em áreas urbanas"
│   │   ├── cluster_1: "rodovia rural dois-via"
│   │   └── centroid: {cost_km: 2.5M, duration_months: 18, ...}
│   └── S8: ...
├── outliers
│   ├── project_id_XYZ: {reason: "cost 5σ above", segment: "S1", status: "pending_review"}
│   └── ...
└── patterns
    ├── "soil_soft + drainage_poor → delay_6m": {confidence: 0.92, sources: [p1, p2, p3]}
    └── ...
```

### 3.4 Audit Trail

**Responsabilidade**: Registrar todas as mudanças no KB com contexto

**Tabela**: `kb_metadata` (vide seção 1.3)

**Eventos logados**:
1. Criação de novo chunk (origem: projeto + data)
2. Atualização de chunk (versão anterior, razão, aprovador)
3. Depreciação (quando supersedido por versão nova)
4. Rollback (motivo: anomalia detectada ou rejeição)

**Dashboard de auditoria** (future: Superset/Metabase):
```
Timeline de todas as mudanças:
2026-07-30 14:30 agente-saneamento criou "ETA custo médio AySA 2025" (confidence: 0.95)
2026-07-28 09:15 human-reviewer rejeitou "LT custo novo" (reason: "outlier não investigado")
2026-07-25 11:00 agente-energia aprovou "transmissão leilão 2026" (source: 3 editais ANEEL)
```

---

## 4. Segmentos Prioritários

### 4.1 S8 — Saneamento (AySA)

**Escopo**: Estações de Tratamento (ETA), Estações de Tratamento de Esgoto (ETE), adutoras, redes de drenagem

**Prioridade**: 🔴 **CRÍTICA** — parceria AySA 2026

**Fontes de dados**:
- AySA: arquivos de projetos finalizados (4 ETA já entregues em 2024-2025)
- SNIS: Banco de custos nacional
- Lei 14.026 (Marco Legal do Saneamento)
- Editais BNDES: histórico de investimentos

**Features-chave**:
- Volume tratado (m³/dia)
- Topografia + solo (impacto em adutoras)
- Taxa de tratamento (primário/secundário/terciário)
- Custo por m³ tratado
- Duração de projeto básico vs executivo

**Templates iniciais**:
- "ETA fluvial de 50 m³/dia em solo mole"
- "ETE compacta para município < 10k hab"
- "Adutora > 5 km com cruzamentos"

**KB versão inicial**: S8-v1.0.0 (a ser criada em step 5)

### 4.2 S9 — Energia (ANEEL/State Grid)

**Escopo**: Linhas de Transmissão (LT), subestações, ramais

**Prioridade**: 🟠 **ALTA** — demanda ANEEL crescente

**Fontes de dados**:
- ANEEL: Editais de leilão de transmissão
- EPE: Plano Decenal de Energia
- ONS: Operador Nacional do Sistema
- IEEE: Padrões de engenharia

**Features-chave**:
- Tensão (69 kV, 138 kV, 230 kV, 500 kV, 600 kV)
- Comprimento da LT
- Topografia (plana vs montanha)
- Tipo de torre (estaiada vs auto-portante)
- Custo por km
- Duração de autorização ambiental vs construção

**Templates iniciais**:
- "LT 230 kV em topografia plana, 50 km"
- "Subestação em área urbana, 138/69 kV"
- "RAP (Relatório Ambiental Prévio): 8-10 meses"

**KB versão inicial**: S9-v1.0.0

### 4.3 S6 — Portos (ANTAQ)

**Escopo**: Terminais, dragagem, molhes, cais, berços

**Prioridade**: 🟡 **MÉDIA** — mercado em retomada

**Fontes de dados**:
- ANTAQ: Concessões e editais
- PIANC (Permanent International Association of Navigation Congresses): Guidelines
- Editais BNDES: financiamentos históricos
- Relatórios de dragagem

**Features-chave**:
- Calado (profundidade de acesso)
- Capacidade de carga (toneladas/ano)
- Tipo de carga (contêiner, granel, carga geral)
- Dragagem necessária (m³)
- Custo por tonelada movimentada
- Duração de projeto + pré-operação

**Templates iniciais**:
- "Terminal contêinerista: 50k TEU/ano, calado 12m"
- "Dragaria de 2M m³ em baía protegida"
- "Molhe de proteção, 500m, em costa rochosa"

**KB versão inicial**: S6-v1.0.0

---

## 5. Timeline de Evolução

### 5.1 Ingestion Frequency (Cadência de Coleta)

| Frequência | Responsabilidade | Dados |
|-----------|---|---|
| **Diária** (00h/05h UTC) | Batch job ETL | ERP (custo real), SharePoint (novos docs) |
| **Horária** (a cada h) | Webhook | Novo evento de status, feedback humano |
| **Semanal** (seg 09h) | API externa | DNIT SICRO, ANEEL editais, ANTAQ portarias |
| **Mensal** (1º do mês) | Manual + API | Snapshot de kb_chunks, relatório de métricas |
| **Trimestral** (15/1, 15/4, 15/7, 15/10) | Humano | Audit completo, aprovação de quebras de versão |

### 5.2 Processing Latency

| Step | Latência | Frequência |
|------|----------|-----------|
| 1. Ingestion | < 30 min | Contínua |
| 2. Feature extraction | 1-2 horas | Dependente de tamanho |
| 3. Clustering | 2-4 horas | Diária (recomputa) |
| 4. Outlier detection | 1-2 horas | Junto com clustering |
| 5. Expert validation | 4-24 horas | Human-in-the-loop (SLA: 24h) |
| 6. KB commit | < 5 min | Pós-aprovação |
| 7. Broadcast to agents | < 5 min | Webhook RAG refresh |

**Exemplo timeline real**:
```
2026-07-30 08:00 — Projeto ETA finalizado no ERP
2026-07-30 08:45 — Extraction completa, features extraídas
2026-07-30 10:30 — Clustering + outlier detection (custo 4σ acima)
2026-07-30 10:35 — Flag para human review (outlier)
2026-07-30 11:00 — Human abre documento, valida (ok, projeto especial)
2026-07-30 11:05 — Expert validation requisição enviada a agente-saneamento
2026-07-30 14:30 — agente-saneamento aprova, kb_chunks insert
2026-07-30 14:31 — kb_metadata + snapshot criados
2026-07-30 14:32 — Broadcast: S8 refresh, novo template live
```

### 5.3 Knowledge Evolution Roadmap

#### Q3 2026 (agora)
- [ ] Deploy inicial: S8 (Saneamento), S9 (Energia), S6 (Portos)
- [ ] Create 3 RAG collections em Supabase
- [ ] Setup ML pipeline (KMeans, Isolation Forest)
- [ ] Create kb_chunks, kb_metadata, kb_snapshots tables
- [ ] Beta: 5 projetos piloto por segment
- [ ] Deploy de audit trail dashboard

#### Q4 2026
- [ ] Expand S8 com 10+ projetos AySA
- [ ] S9: integração de 5 leilões ANEEL 2026
- [ ] S6: 3 terminais de pesquisa
- [ ] Feature: rollback automático via anomaly score (threshold = 0.7)
- [ ] Métricas: adoção por agentes (quantas vezes consultaram novo chunk)

#### Q1 2027
- [ ] S7 (Aeroportos) beta launch
- [ ] S10 (Barragens) beta launch
- [ ] Expert validation automation (SVM classifier: agente ou humano?)
- [ ] KB consolidation: primeira quebra major (v2.0.0)
- [ ] Integration: Maestro routing usa KB versão live

#### Q2 2027+
- [ ] Todos os 10 segments em operação
- [ ] ML model serving (real-time outlier detection)
- [ ] Feedback loop: agentes sugerem padrões novos automaticamente
- [ ] "Knowledge marketplace": agentes podem "vender" chunks validados

---

## 6. Dados de Entrada — Schema de Ingestão

### 6.1 Project Finalization Event

Quando projeto chega ao estado "Encerrado" no ERP, gateway emite:

```json
{
  "event_type": "project.finalized",
  "project_id": "PRJ-2026-01234-AYS",
  "segment": "S8",
  "segment_label": "Saneamento",
  "project_name": "ETA Alto da Lapa (AySA)",
  "completed_at": "2026-07-28T15:30:00Z",
  "phases": [
    {
      "phase": "estudo_previo",
      "duration_months": 4,
      "cost_usd": 45000
    },
    {
      "phase": "projeto_basico",
      "duration_months": 6,
      "cost_usd": 120000
    },
    {
      "phase": "projeto_executivo",
      "duration_months": 8,
      "cost_usd": 180000
    },
    {
      "phase": "obra_execucao",
      "duration_months": 24,
      "cost_usd": 2500000
    }
  ],
  "key_metrics": {
    "volume_day_m3": 75,
    "treatment_type": "secondary",
    "soil_class": "soft_clay",
    "area_hectares": 8.5
  },
  "sp_links": [
    "https://sp.mantaassociados.com/03_Projetos/Saneamento/ETA_Alto_Lapa_2026/"
  ]
}
```

### 6.2 Document Ingestion

```
/03_Projetos/Saneamento/ETA_Alto_Lapa_2026/
├── 01-EVTE_Alto_Lapa.pdf
├── 02-Projeto_Basico_completo.dwg
├── 03-Projeto_Executivo.dwg
├── 04-AS_Built_final.dwg
├── 05-Relatorio_Final_Licitacao.xlsx
└── 06-Lessons_Learned.docx
```

Ingestion layer:
1. Detecta novo PDF → OCR + text extraction
2. Estruturado (.xlsx) → SQL insert direto
3. CAD (.dwg) → metadata extraction (área, volumes)
4. Docx → spaCy NER (pessoas, datas, números)

---

## 7. Integração com Maestro Agents

### 7.1 RAG Refresh Protocol

Quando novo chunk é aprovado:

```python
# Pseudocódigo
def commit_and_broadcast(chunk: KBChunk, version_bump: str):
    # 1. Versioning
    new_version = bump_version(chunk.segment, version_bump)
    chunk.kb_version = new_version
    
    # 2. DB commit
    db.insert(kb_chunks, chunk)
    db.insert(kb_metadata, {
        chunk_id: chunk.id,
        change_type: 'create',
        approval_status: 'approved',
        approved_by: current_user
    })
    
    # 3. Snapshot
    snapshot = create_snapshot(chunk.segment, new_version)
    db.insert(kb_snapshots, snapshot)
    
    # 4. Broadcast
    for agent in [agente_saneamento, agente_energia, ...]:
        if agent.segment == chunk.segment:
            send_webhook(agent.webhook_url, {
                event: 'kb_update',
                segment: chunk.segment,
                new_version: new_version,
                chunks_added: 1
            })
```

### 7.2 Agent Interface to KB

Cada agente S1-S10 implementa:

```python
class AgentKBInterface:
    
    def fetch_kb(self, segment: str, version: str = "latest"):
        """Busca chunks do KB para este segment"""
        chunks = supabase.query(
            table="kb_chunks",
            filters=[
                ("segment", "eq", segment),
                ("kb_version", "eq", version)
            ]
        )
        return chunks
    
    def report_outlier(self, project_id: str, reason: str):
        """Agente reporta anomalia detectada"""
        db.insert(outlier_reports, {
            project_id: project_id,
            reported_by: self.name,
            reason: reason,
            timestamp: now()
        })
    
    def suggest_pattern(self, pattern: Pattern, evidence: List[ProjectID]):
        """Agente sugere novo padrão para ML"""
        db.insert(pattern_suggestions, {
            pattern: pattern.to_json(),
            evidence: evidence,
            suggested_by: self.name,
            status: 'pending_ml_validation'
        })
```

---

## 8. Rollback & Recovery

### 8.1 Scenarios de Rollback

| Cenário | Gatilho | Ação | Tempo |
|---------|---------|------|-------|
| Outlier não investigado | Agente detecta anomalia pós-deploy | Restore snapshot anterior | < 30 min |
| Versão quebrada | Teste falha | Rollback para v-1 | < 10 min |
| Feedback humano | Human rejeita chunk após aprovação | Mark deprecated, voltar a pending | < 5 min |
| Update cascata | Chunk mudou, filhos inválidos | Revalidar children | < 2 horas |

### 8.2 Restore de Snapshot

```python
def restore_snapshot(segment: str, kb_version: str):
    """Volta KB para versão anterior"""
    snapshot = db.query(kb_snapshots).filter(
        segment=segment, 
        kb_version=kb_version
    ).order_by(created_at.desc()).first()
    
    if not snapshot:
        raise SnapshotNotFound
    
    # 1. Atualizar kb_chunks de volta
    db.bulk_update(snapshot.snapshot_data['chunks'])
    
    # 2. Log auditoria
    db.insert(kb_metadata, {
        change_type: 'rollback',
        restored_to: kb_version,
        reason: current_user.input(),
        timestamp: now()
    })
    
    # 3. Notificar agentes
    broadcast_rollback(segment, kb_version)
```

---

## 9. Monitoramento & Observabilidade

### 9.1 Key Metrics (Dashboard)

```
Saneamento (S8)
├── KB Version: S8-v1.0.0
├── Total Chunks: 42
├── Confidence (avg): 0.88
├── Projects Processed (lifetime): 7
├── Outliers Detected (30d): 1 (under review)
├── Chunks Added (30d): 5
├── Agent Adoption (last 30d): agente-saneamento 23 queries
└── Rollbacks (30d): 0

Energia (S9)
├── KB Version: S9-v1.0.0
├── Total Chunks: 28
├── Confidence (avg): 0.92
└── ...
```

### 9.2 Alertas

| Métrica | Threshold | Ação |
|---------|-----------|------|
| Outlier rate | > 5% | Pause ingestion + investigate |
| KB version drift | Agent < 3 versions behind latest | Notify PO |
| Processing latency | > 4 horas | Page on-call |
| Confidence score | Chunk < 0.6 | Require human validation |
| Adoption rate | New chunk never used in 30d | Flag for deprecation review |

---

## 10. Segurança & Compliance

### 10.1 Access Control

| Role | Permissões | Exemplos |
|------|-----------|----------|
| AgentS8 (agente-saneamento) | Read KB, suggest patterns, report outliers | Lê ETA templates, sugere "ETE compacta" |
| HumanReviewer | Approve/reject, initiate rollback | Valida outlier, aprova novo chunk |
| Admin | Manage versions, audit trail | Força rollback, força bump major version |
| PublicAPI | Read-only KB latest | Ferramentas externas consultam público |

### 10.2 Data Privacy

- Nomes de projetos + clientes: masked em exemplos públicos
- Custos reais: stored em kb_chunks com flag `is_sensitive`
- Proprietary methods: access restricted a Manta only
- GDPR: delete traces de pessoa se solicitado

---

## 11. Próximas Fases — Roadmap Técnico

### Phase 1 (agora): Foundation
- [x] ARCHITECTURE.md (este documento)
- [ ] Implement Ingestion Layer + ETL
- [ ] Setup Supabase tables (kb_chunks, kb_metadata, kb_snapshots)
- [ ] ML pipeline skeleton (feature extraction)
- [ ] Expert validation gate (manual)

### Phase 2 (Q4 2026): Scale
- [ ] Automation de outlier detection
- [ ] Feedback loop closure (agentes sugerem padrões)
- [ ] Dashboard de auditoria
- [ ] Integração S8, S9, S6 com 20+ projetos

### Phase 3 (Q1 2027): Intelligence
- [ ] SVM para predizer se chunk é "expert-approvable"
- [ ] Auto-generation de chunks via LLM
- [ ] Pattern discovery automática
- [ ] S7, S10 launch

### Phase 4 (Q2 2027+): Ecosystem
- [ ] Knowledge marketplace (agentes trocam chunks)
- [ ] Multi-tenant (Manta + partners)
- [ ] Real-time RAG serving (sub-ms latency)
- [ ] Monetização (vender insights a terceiros)

---

## 12. Referências & Repositórios

| Artefato | Localização | Responsável |
|----------|-------------|-------------|
| CLAUDE.md master | Codex-exemplo/CLAUDE.md | MN (master registry) |
| ARCHITECTURE.md | Codex-exemplo/ARCHITECTURE.md | Este arquivo |
| Ingestion code | `/src/ingestion/` (TBD) | TBD |
| ML pipeline | `/src/ml/` (TBD) | TBD |
| Supabase schema | Migrations em `db/migrations/` (TBD) | TBD |
| Agent integrations | `.claude/agents/agente-{segment}.md` | Cada agente |
| Audit dashboard | `/dashboards/kb-audit.json` (future) | TBD |

---

## 13. Glossário

| Termo | Definição |
|-------|-----------|
| **KB Chunk** | Fragmento de conhecimento (constante, template, regra) versionado |
| **Feature** | Atributo estruturado extraído de projeto (custo/m, duração/mes, etc) |
| **Confidence** | Pontuação 0-1 de confiança que chunk é acurado (baseado em n projetos) |
| **Outlier** | Datapoint fora da distribuição esperada (requer review humano) |
| **Pattern** | Regra recorrente descoberta em clustering (ex: "soft soil → 6m delay") |
| **Expert Validation** | Certificação por agente especializado (S1-S10) que chunk é correto |
| **Snapshot** | Estado imutável do KB em ponto no tempo (permite rollback) |
| **Segment** | Domínio vertical (S1 Rodovia, S8 Saneamento, S9 Energia, etc) |
| **Audit Trail** | Log completo de quem/quando/por quê mudou KB |

---

**Documento finalizado**: 2026-07-30  
**Próxima revisão**: 2026-10-30 (final de Q3)  
**Responsável**: Manta Maestro Knowledge Systems

