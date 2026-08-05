# MAESTRO v4.2 — Plano de Implementação
**Status:** BLUEPRINT PARA EXECUÇÃO  
**Alvo:** Completar expansão S6–S10 até 2026-08-11  
**Proprietário:** Tech Lead IA (Manta Associados)

---

## 🎯 OBJETIVO

Ativar 5 novos agentes verticais (Portos, Aeroportos, Saneamento, Energia, Barragens) com infraestrutura completa (RAG + SharePoint + Skills + Tests).

**Valor entregue:** 
- ✅ Routing automático de 5 novos domínios
- ✅ 50+ documentos de referência por domínio indexados
- ✅ Latência <2s por query
- ✅ SLA de 99.5% uptime (após go-live)

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### FASE 1A: Supabase RAG Collections (Dia 1–2)

**Responsável:** DBA / Data Engineer  
**Dependências:** Acesso Supabase projeto Manta

#### 1A.1 — Criar Tabela rag_chunks
```sql
-- [Supabase Console] → SQL Editor

BEGIN;

CREATE TABLE rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identificação
  prefix TEXT NOT NULL COMMENT 'Prefixo de coleção (san:, ene:, por:, aer:, bar:)',
  title TEXT NOT NULL COMMENT 'Título do documento/seção',
  source_url TEXT COMMENT 'URL original ou identificação do arquivo',
  
  -- Conteúdo
  content TEXT NOT NULL COMMENT 'Texto integral (até 10k chars)',
  metadata JSONB DEFAULT '{}' COMMENT 'Tags, autor, data, versão, etc',
  
  -- Embeddings (para busca vetorial futura)
  embedding VECTOR(1536) COMMENT 'OpenAI/Claude embeddings',
  
  -- Auditoria
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by TEXT DEFAULT 'system',
  
  -- Índices
  INDEX idx_prefix (prefix),
  INDEX idx_title (title),
  INDEX idx_source (source_url),
  INDEX idx_embedding (embedding)
);

-- RLS Policy (agentes podem ler, humans podem CRUD)
ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "agents_read_all" ON rag_chunks
  FOR SELECT USING (TRUE);

CREATE POLICY "humans_full_access" ON rag_chunks
  USING (auth.role() = 'authenticated');

COMMIT;
```

**Ação:** Executar no Supabase SQL Editor  
**Tempo estimado:** 5 minutos  
**Validação:** `SELECT COUNT(*) FROM rag_chunks;` → 0

---

#### 1A.2 — Inserir Dados Iniciais (5 coleções)
```sql
-- Saneamento (san:)
INSERT INTO rag_chunks (prefix, title, content, metadata) VALUES
('san:', 'SNIS 2024 — Indicadores Principais', 
 'Água: atendimento 93%, perda 38%, tarifa média R$ 8,50/m³
  Esgoto: atendimento 54%, coleta 83%, SNIS meta 90% até 2033
  Key metrics: perdas reais, volume faturado, despesa OPEX', 
 '{"source": "ANA SNIS", "year": 2024, "category": "water"}'),

('san:', 'Lei 14.026/2020 — Novo Marco do Saneamento',
 'Artigos-chave para concessões, subsídio cruzado, universalização.
  Regulação por ANA (agência), por estado (reguladora estadual).
  Prazos: 99% água até 2033, 90% esgoto até 2033.',
 '{"source": "Planalto.gov.br", "law_id": "14.026", "year": 2020}'),

('san:', 'NBR 12211 — Concepção Sistemas Abastecimento',
 'Norma técnica para projeto básico/executivo de sistemas de água.
  Vazão: per capita (150–250 L/hab.dia), coeficientes K1 (1.2–1.5) K2 (1.5–2.0).
  Adutora: Hazen-Williams, materiais (PVC, DEFOFO, aço).',
 '{"source": "ABNT", "norm_id": "NBR12211", "category": "technical"}'),

-- [Similar para energia, portos, aeroportos, barragens — 3 docs cada]

-- Energia (ene:)
INSERT INTO rag_chunks (prefix, title, content, metadata) VALUES
('ene:', 'ANEEL Edital 001/2024 — Leilão LT 230kV',
 'Edital completo de leilão de linha de transmissão. 
  Objeto: 450 km em região Nordeste, custo R$ 1,2B, cronograma 48 meses.
  Requisitos: modelo financeiro, garantias, aval...',
 '{"source": "ANEEL", "edital_id": "001/2024", "category": "tender"}'),

('ene:', 'EPE R1–R5 — Custos de Referência Transmissão',
 'Tabelas de custos R1–R5 por kV. 
  R1 (500kV): 2.5–3.2 M/km, R5 (138kV): 1.2–1.8 M/km.
  Inclui CAPEX (obra, material, projeto) + OPEX (O&M 25 anos).',
 '{"source": "EPE", "category": "cost_reference", "unit": "R$/km"}'),

-- Portos (por:)
INSERT INTO rag_chunks (prefix, title, content, metadata) VALUES
('por:', 'ANTAQ Normativa 2206 — Concessão de Berços',
 'Regulamentação para licitação de berços portuários.
  Prazos: até 25 anos, remuneração por metro linear/ano, tarifa de acesso...',
 '{"source": "ANTAQ", "norm_id": "2206", "category": "regulation"}'),

-- Aeroportos (aer:)
INSERT INTO rack_chunks (prefix, title, content, metadata) VALUES
('aer:', 'ANAC RBAC 154.405 — Pátio de Aeronaves',
 'Norma de distâncias de segurança entre stands: 60m mínimo fuselagem.
  Tipos de stand (A/B/C/D) com footprint diferente.
  Zona de movimento vs. zona de estacionamento.',
 '{"source": "ANAC", "rbac_id": "154.405", "category": "technical"}'),

-- Barragens (bar:)
INSERT INTO rag_chunks (prefix, title, content, metadata) VALUES
('bar:', 'ICOLD Dam Safety Guidelines — Inspeção Estrutural',
 'Protocolo de inspeção de segurança de barragens.
  Frequência: visual anual, instrumentação contínua, ensaios a cada 5 anos.
  Critérios de alerta (phreatic surface, seepage rate).',
 '{"source": "ICOLD", "publication_id": "GUIDELINES_2023", "category": "technical"}');
```

**Ação:** Executar INSERT statements  
**Tempo estimado:** 10 minutos  
**Validação:** `SELECT DISTINCT prefix FROM rag_chunks;` → san:, ene:, por:, aer:, bar:

---

#### 1A.3 — Criar Índices de Performance
```sql
-- Índice BRIN para atributos temporais
CREATE INDEX idx_rag_created_brin ON rag_chunks USING BRIN (created_at);

-- Índice GiST para busca full-text (opcional, v2.0)
CREATE INDEX idx_rag_content_fts ON rag_chunks USING GiST (to_tsvector('portuguese', content));

-- Índice HNSW para embeddings (para similaridade vetorial)
CREATE INDEX idx_rag_embedding_hnsw ON rag_chunks USING hnsw (embedding vector_cosine_ops);
```

**Ação:** Executar no Supabase  
**Tempo estimado:** 5 minutos  
**Validação:** `\d rag_chunks` (listar índices)

---

### FASE 1B: SharePoint Folder Structure (Dia 1–2)

**Responsável:** SharePoint Admin / Gestor de Projetos  
**Dependências:** Acesso ao SharePoint Manta

#### 1B.1 — Criar Pastas Base
```bash
# [Via SharePoint Manta MCP ou UI web]

03_Projetos/
│
├── 01_Rodovias/                    (já existe)
├── 02_OAE/                         (já existe)
├── 03_Ferrovia/                    (já existe)
├── 04_Metro/                       (já existe)
│
├── 05_Saneamento/                  (🆕 criar)
│   ├── Memoriais/
│   ├── Projetos Executivos/
│   ├── Editais/
│   ├── PMSB/
│   ├── Licitações/
│   └── Estudos de Viabilidade/
│
├── 06_Energia/                     (🆕 criar)
│   ├── Leilões ANEEL/
│   ├── Estudos de Inserção/
│   ├── Análises Técnicas/
│   ├── Cronogramas/
│   └── Custos R1-R5/
│
├── 07_Portos/                      (🆕 criar)
│   ├── Estudos de Viabilidade/
│   ├── Editais ANTAQ/
│   ├── Projetos Executivos/
│   ├── Normas e Regulamentação/
│   └── Benchmarking Internacional/
│
├── 08_Aeroportos/                  (🆕 criar)
│   ├── Estudos de Demanda/
│   ├── Projetos de Pista/
│   ├── Projeto de Pátio/
│   ├── RBAC e Normas ANAC/
│   └── Concessões Operacionais/
│
└── 09_Barragens/                   (🆕 criar)
    ├── Estudos Hidrológicos/
    ├── Projetos de Barragem/
    ├── Inspeção e Monitoramento/
    ├── Normas CBDB/ICOLD/
    └── Segurança de Barragens/
```

**Ação:** Criar pastas via UI SharePoint ou MCP `mcp__SharePoint_Manta__create_folder`  
**Tempo estimado:** 20 minutos  
**Validação:** Verificar que todas as 5 pastas base + subpastas existem

---

#### 1B.2 — Upload de Documentos de Referência
**Por segmento:** Fazer upload de ~10 documentos iniciais (PDFs, Word, Excel)

```bash
# Exemplo — Saneamento
05_Saneamento/
├── SNIS_2024_Indicadores.xlsx          (ANA, público)
├── Lei_14026_2020_FullText.pdf         (Planalto, público)
├── NBR_12211_ConcepsaoSistemas.pdf     (ABNT, comprado)
├── AySA_ProjetoRiachuelo_2023.pdf      (AySA, publicado)
├── Template_Memorial_ETA.docx          (Manta, interno)
├── Composicoes_SINAPI_Saneamento.xlsx  (SINAPI, público)
├── PMSB_SP_2023_Resumo.pdf             (Municípios, público)
├── Lei_Saneamento_Estadual_SP.pdf      (Estado, público)
├── Edital_BNDES_2024_Saneamento.pdf    (BNDES, público)
└── Analise_Subsidio_Cruzado.xlsx       (Manta, interno)

# Totalizando: 5 agentes × 10 docs = 50 documentos
# Tempo: ~2–3 horas (upload batch)
```

**Ação:** Upload via SharePoint MCP `mcp__SharePoint_Manta__upload_file`  
**Tempo estimado:** 2–3 horas  
**Validação:** `SELECT COUNT(*) FROM SharePoint folder` → 50 items mín.

---

### FASE 2A: Skills Registry Creation (Dia 3)

**Responsável:** Tech Lead IA  
**Dependências:** Acesso a `.claude/skills/`

#### 2A.1 — Criar Skills específicos

Exemplo: `agente-saneamento-snis-integration.md`

```yaml
---
name: saneamento-snis-integration
description: Integração com SNIS (Sistema Nacional de Informações de Saneamento) — leitura de KPIs, indicadores, análise de performance de sistemas de água/esgoto brasileiros.
model: sonnet
trigger: "SNIS|sistema nacional saneamento|indicador água|perda água|tarifa média|atendimento esgoto"
---

# Skill: SNIS Integration para Agente Saneamento

Permite que `agente-saneamento` consulte dados públicos do SNIS (ANA) 
em tempo real e realize análises comparativas.

## Métodos

### 1. Fetch KPI by Municipality
```python
def fetch_snis_kpi(city_code: int, indicator: str, year: int):
    """
    Busca KPI SNIS por município.
    
    Args:
        city_code: Código IBGE (ex: 3550308 para São Paulo)
        indicator: 'water_loss', 'sewage_treatment', 'tariff_avg', etc.
        year: 2024 (ou anterior)
    
    Returns:
        {"city": "São Paulo", "indicator": "water_loss", "value": 38.2, "unit": "%"}
    """
    # Chamar API SNIS (público): https://www.snirh.gov.br/
```

### 2. Comparative Analysis
```python
def compare_snis_region(state: str, indicator: str):
    """Compara 27 municípios de estado X"""
```

## Referências
- SNIS Portal: https://www.snirh.gov.br/
- ANA: Agência Nacional de Águas
- Atualização: anual (junho)
```

**Similar para:**
- `agente-energia-aneel-integration.md` (fetch editais ANEEL)
- `agente-portos-antaq-integration.md` (fetch normas ANTAQ)
- `agente-aeroportos-anac-integration.md` (fetch RBAC ANAC)
- `agente-barragens-icold-integration.md` (fetch guidelines ICOLD)

**Ação:** Criar 5 `.md` files em `.claude/skills/`  
**Tempo estimado:** 3–4 horas  
**Validação:** Listar arquivos: `ls -la .claude/skills/ | grep agente-`

---

### FASE 2B: Routing Tests (Dia 4–5)

**Responsável:** QA IA / Test Engineer  
**Dependências:** Maestro operacional

#### 2B.1 — Test Framework
```python
# test_maestro_routing_v42.py

import pytest
from manta_maestro import MaestroRouter

router = MaestroRouter()

class TestSaneamentoRouting:
    def test_saneamento_eta_design(self):
        """Test que prompt sobre ETA roteia para agente-saneamento"""
        prompt = """
        Preciso dimensionar uma ETA para 50.000 habitantes 
        com demanda de 150 L/hab.dia, manancial superficial.
        Qual é a norma ABNT?
        """
        result = router.route(prompt)
        
        assert result['agent'] == 'agente-saneamento'
        assert result['confidence'] > 0.9
        assert 'saneamento|ETA|água tratada|ABNT' in result['matched_rules']

    def test_saneamento_licitacao(self):
        """Test licitação BNDES saneamento"""
        prompt = "Lançamos edital BNDES para ampliação de ETE com lodo ativado..."
        result = router.route(prompt)
        assert result['agent'] == 'agente-saneamento'

class TestEnergiaRouting:
    def test_energia_leilao_aneel(self):
        prompt = "Analisando leilão ANEEL para LT 230 kV com cronograma R1-R5..."
        result = router.route(prompt)
        assert result['agent'] == 'agente-energia'
        assert result['confidence'] > 0.9

class TestPortosRouting:
    def test_portos_berco(self):
        prompt = "Ampliação de berço para 40k TEU/ano com calado e moldura PIANC..."
        result = router.route(prompt)
        assert result['agent'] == 'agente-portos'

class TestAeroportosRouting:
    def test_aeroportos_patio(self):
        prompt = "Expansão de pátio em aeroporto regional, estações RBAC 154..."
        result = router.route(prompt)
        assert result['agent'] == 'agente-aeroportos'

class TestBarragensRouting:
    def test_barragens_inspeção(self):
        prompt = "Barragem de terra em zona sísmica, protocolo ICOLD de segurança..."
        result = router.route(prompt)
        assert result['agent'] == 'agente-barragens'

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
```

**Ação:** Executar testes  
**Tempo estimado:** 2–3 horas  
**Validação:** `pytest -v` → 5/5 PASSED

---

### FASE 3: Documentation & Gate (Dia 5–7)

#### 3.1 — Atualizar ARQUITETURA-AGENTES-IA.md
**Localização SharePoint:** `00-Documentacao/ARQUITETURA-AGENTES-IA.md`  
**Versão anterior:** v1.0.0 (2026-07-04)  
**Versão nova:** v2.0.0 (2026-08-11)

```markdown
# Arquitetura de Agentes IA — Manta Associados

## v2.0.0 (2026-08-11) — Expansão S6–S10

### Mudanças Principais

- ✅ 5 novos agentes verticais (Portos, Aeroportos, Saneamento, Energia, Barragens)
- ✅ Routing automático Maestro (Manta 00) com 10 regras
- ✅ RAG Supabase para 5 coleções de domínio
- ✅ SharePoint integration com 5 pastas base
- ✅ Skills registry para integração com APIs (ANTAQ, ANEEL, ANAC, SNIS, ICOLD)

### Diagrama de Routing

```
User Prompt
    ↓
Maestro (Manta 00)
    ├─ IF saneamento|ETA|... → agente-saneamento (S8)
    ├─ IF energia|ANEEL|... → agente-energia (S9)
    ├─ IF porto|berço|... → agente-portos (S6)
    ├─ IF aeroporto|RBAC|... → agente-aeroportos (S7)
    ├─ IF barragem|ICOLD|... → agente-barragens (S10)
    └─ IF rodovia|... → agente-infraestrutura (S1–S4)
```

### Responsabilidades por Agente

| Agente | Ciclo de Vida | RAG Collection | SharePoint Folder | Integration |
|---|---|---|---|---|
| S8 (Saneamento) | 8/8 fases | san: | 05_Saneamento/ | SNIS, ANA, AySA |
| S9 (Energia) | 8/8 fases | ene: | 06_Energia/ | ANEEL, ONS, EPE |
| S6 (Portos) | 8/8 fases | por: | 07_Portos/ | ANTAQ, PIANC |
| S7 (Aeroportos) | 8/8 fases | aer: | 08_Aeroportos/ | ANAC, RBAC, ICAO |
| S10 (Barragens) | 8/8 fases | bar: | 09_Barragens/ | CBDB, ICOLD, SIGBM |

### SLA de Resposta

- **Latência P95:** <2 segundos (RAG query + agent response)
- **Disponibilidade:** 99.5% (sujeito a SLA Supabase)
- **Timeout:** 30 segundos (máximo para resposta completa)

### Roadmap v2.1 (Q4 2026)

- [ ] Fine-tuning de embeddings por domínio
- [ ] Cache distribuído para RAG queries
- [ ] Integração com BIM/CAD (Revit, AutoCAD)
- [ ] Alertas de licitação em tempo real

```

**Ação:** Atualizar doc no SharePoint  
**Tempo estimado:** 2 horas  
**Validação:** Documentação revisada por MN + Technical Reviewer

---

#### 3.2 — Upload Skills para SharePoint
**Local:** `01-agentes-fundamentais/` no SharePoint

Fazer upload dos 5 skills `.md` criados em 2A.1  
**Tempo estimado:** 30 minutos

---

#### 3.3 — Gate Humano — Aprovação MN

**Checklist de Aprovação:**

```
[ ] Infrastructure Ready
    [ ] Supabase RAG collections 5/5 online
    [ ] SharePoint folders 5/5 created
    [ ] 50+ documentos uploaded
    
[ ] Testing Complete
    [ ] Routing tests 5/5 PASSED
    [ ] Performance P95 <2s
    [ ] Fallback/error handling tested
    
[ ] Documentation
    [ ] ARQUITETURA v2.0.0 updated
    [ ] Skills registered
    [ ] Deploy checklist marked complete
    
[ ] Security & Compliance
    [ ] RLS policies configured (Supabase)
    [ ] SharePoint access controls verified
    [ ] No sensitive data in RAG
    
[ ] Go/No-Go Decision
    [ ] MN approval: YES / NO / CONDITIONAL
    [ ] Technical Reviewer sign-off
    [ ] Deployment date confirmed
```

**Responsável:** MN (Maestro do Negócio) + Tech Lead  
**Tempo estimado:** 1 dia (revisão)

---

## 📊 TIMELINE CONSOLIDADO

```
Semana de 29/07 a 04/08 (Semana 1)
├─ Seg 29: Kickoff + Supabase setup (1A.1–1A.3)
├─ Ter 30: SharePoint folders + docs upload (1B.1–1B.2)
├─ Qua 31: Skills creation (2A.1)
├─ Qui 01: Initial validation + adjustments
└─ Sex 02: Contingency buffer

Semana de 05/08 a 11/08 (Semana 2)
├─ Seg 05: Routing tests (2B.1)
├─ Ter 06: Documentation update (3.1–3.2)
├─ Qua 07: Performance tuning + fixes
├─ Qui 08: Gate human review (3.3)
└─ Sex 09: Final deployment prep

DEPLOYMENT: Seg 12/08 (após aprovação MN)
```

---

## 💡 NOTAS & CONTINGÊNCIAS

### Se Atrasarmos
- **Dia 5 vs. Dia 3:** Estender Phase 1 por +1 dia (buffer segunda semana)
- **Testes falharem:** Debug regex + ajustar `DEPLOY CHECKLIST`
- **Performance lenta:** Escalate para Opus se Sonnet latência > 3s

### Próximas Fases (v2.1+)
- Machine learning embeddings customizados
- Cache distribuído (Redis)
- Integração BIM real-time
- Alertas de licitação

---

**Document Owner:** Tech Lead IA  
**Last Updated:** 2026-07-29 14:30 UTC  
**Next Review:** 2026-08-11 (após conclusão)
