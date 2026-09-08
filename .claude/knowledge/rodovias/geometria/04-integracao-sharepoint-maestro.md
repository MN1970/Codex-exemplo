# Integração SharePoint & Manta Maestro — Geometria de Rodovias

**Data**: 2026-08-03  
**Repositório**: `MN1970/Codex-exemplo`  
**Branch**: `claude/agente-rodovias-conhecimento-6jhqhc`  
**Prefixo RAG**: `rod:geom:*`  
**Status**: 🔄 Mapeamento com Manta Maestro

---

## 1. Estrutura SharePoint Atual

### 📁 Pasta Canônica Manta

```
SharePoint > Documentos Compartilhados > 04_IA > Manta-Maestro
├── 00-arquitetura/
│   └── ARQUITETURA-AGENTES-IA.md (v2.0.0)
│
├── 01-agentes-fundamentais/
│   ├── agente-infraestrutura/          ⬅ Aqui está S1-S4
│   │   ├── agente-infraestrutura-s1/   # RODOVIAS
│   │   │   ├── README.md
│   │   │   ├── SKILL.md
│   │   │   ├── prompts/
│   │   │   │   └── starters.md
│   │   │   ├── refs/
│   │   │   │   ├── DNIT-ES-101-97.pdf
│   │   │   │   ├── DNIT-ES-131-86.pdf
│   │   │   │   ├── DNIT-IPR-726.pdf
│   │   │   │   └── tabelas-normalizadas.xlsx
│   │   │   └── exemplos/                 🆕 EXPANDIR AQUI
│   │   │       ├── br-116-sp-mg.dwg
│   │   │       ├── br-101-rj-sp.dwg
│   │   │       └── casos-reais.md
│   │   │
│   │   ├── agente-infraestrutura-s2/   # OAE (Pontes)
│   │   ├── agente-infraestrutura-s3/   # Ferrovia
│   │   └── agente-infraestrutura-s4/   # Metrô
│   │
│   ├── agente-portos/ (S6 — novo)
│   ├── agente-aeroportos/ (S7 — novo)
│   ├── agente-saneamento/ (S8 — novo)
│   ├── agente-energia/ (S9 — novo)
│   └── agente-barragens/ (S10 — novo)
│
├── 02-horizontais/                      # Agentes transversais
│   ├── agente-claims/
│   ├── agente-contratual/
│   ├── agente-orcamento/
│   ├── agente-cronograma/
│   └── ... (manta-01 a manta-16)
│
└── 03_Projetos/
    ├── Rodovias/
    │   ├── BR-116-SP-MG/
    │   ├── BR-101-RJ/
    │   ├── BR-163-SC/
    │   └── templates/
    │       ├── projeto-geometria-template.dwg
    │       ├── memorial-descritivo-template.docx
    │       └── checklist-validacao.xlsx
    │
    ├── Saneamento/ (novo S8)
    ├── Energia/ (novo S9)
    ├── Portos/ (novo S6)
    ├── Aeroportos/ (novo S7)
    └── Barragens/ (novo S10)
```

---

## 2. Mapeamento Documentação Criada → SharePoint

### Arquivo 01: Elementos Geométricos

**Criado em**: `.claude/knowledge/rodovias/geometria/01-elementos-geometricos.md`

**Espelhamento em SharePoint**:
```
01-agentes-fundamentais/agente-infraestrutura-s1/refs/
├── 01-elementos-geometricos.md  (este arquivo)
├── tabelas-raios-minimos.xlsx
├── formulas-calculo.pdf
└── diagramas-alinhamento-h-v.dwg
```

**Conteúdo a integrar**:
1. Normas DNIT ES 101/97 ✅
2. Tabelas de raio mínimo ✅
3. Fórmulas de clotóide ✅
4. Gráficos de visibilidade ✅

---

### Arquivo 02: Cálculos Práticos

**Criado em**: `.claude/knowledge/rodovias/geometria/02-calculos-praticos.md`

**Espelhamento em SharePoint**:
```
01-agentes-fundamentais/agente-infraestrutura-s1/exemplos/
├── caso-1-br-vd100.md          # Rodovia Federal
├── caso-2-estadual-vd80.md     # Rodovia Estadual
├── br-116-sp-mg-real.md        # Caso histórico
├── orçamento-sicro-exemplo.xlsx
└── parametros-projeto.csv
```

**Conteúdo a integrar**:
1. Caso BR (Vd=100) ✅
2. Caso Estadual (Vd=80) ✅
3. BR-116 real ✅
4. Orçamento SICRO ✅

---

### Arquivo 03: Softwares & Referências

**Criado em**: `.claude/knowledge/rodovias/geometria/03-softwares-referencias.md`

**Espelhamento em SharePoint**:
```
01-agentes-fundamentais/agente-infraestrutura-s1/
├── SKILL.md                    (atualizar com referências)
├── tools/
│   ├── mx-road-workflow.pdf
│   ├── civil3d-configuracao.docx
│   └── sicro-guia-atualizacao.md
└── refs/
    ├── DNIT-ES-101-tabelas.xlsx
    ├── SICRO-2026-vigente.csv
    └── links-externos.md
```

**Conteúdo a integrar**:
1. MX Road workflow ✅
2. Civil 3D assembly ✅
3. SICRO integração ✅
4. Links normativos ✅

---

## 3. Integração com SKILL.md (Agente-infraestrutura S1)

### Estrutura Atual de SKILL.md

```yaml
---
agente: agente-infraestrutura-s1
versao: 1.0
disciplinas: [Geometria, Pavimentação, Terraplenagem, Drenagem]
normas: [ES 101/97, ES 131/86, IPR 702, IPR 726]
intake:
  Q1: Segmento (rodovia)
  Q2: Fase (estudo prévio, projeto básico, executivo, obra, O&M)
  Q3: Objetivo (novo projeto, reabilitação, análise risco)
  Q4: Dados disponíveis (topografia, alinhamento, etc)
---
```

### Vertentes (V1-V5) a Expandir

```markdown
## V1 — Análise Geométrica (EXPANDIR)

### Cobertura Atual
- Alinhamento horizontal básico
- Alinhamento vertical básico
- Seção transversal padrão

### Cobertura Futura (após consolidação)
- ✅ Clotóides avançadas
- ✅ Superelevação (todos métodos)
- ✅ Visibilidade 3D
- ✅ Análise de risco geométrico
- ✅ Interseções (rotatórias, T, cruz)
- ✅ Validação de checklist DNIT

## V2 — Inteligência Técnica (EXPANDIR)

### Cobertura Atual
- Consulta normas básicas
- Tabelas de referência

### Cobertura Futura
- ✅ Recomendação automática de Vd/classe
- ✅ Cálculo iterativo de geometria
- ✅ Análise de trade-offs (custo vs segurança)
- ✅ Machine learning: otimização de traçado

## V3 — Obra & Orçamento (EXPANDIR)

### Cobertura Atual
- Quantitativos básicos

### Cobertura Futura
- ✅ Integração SICRO automática
- ✅ Orçamento com margem e contingência
- ✅ Cronograma ligado a geometria
- ✅ Análise de viabilidade econômica

## V4 — Documentação & Inteligência (EXPANDIR)

### Cobertura Atual
- Memoriais descritivos básicos

### Cobertura Futura
- ✅ Memoriais técnicos DNIT ES 101/97 formatado
- ✅ Relatórios de visibilidade
- ✅ Análise de risco e mitigação
- ✅ Histórico de versões (markdown versionado)

## V5 — Disciplinas Transversais (MANTER)

- Claims (handoff agente-claims)
- Contratual (handoff agente-contratual)
- Orçamento (handoff agente-orcamento, manta-05)
- Cronograma (handoff agente-cronograma, manta-07)
- Modelagem (handoff agente-modelagem, manta-06)
```

---

## 4. Recursos do Manta Maestro a Referenciar

### Do CLAUDE.md (Registro Mestre)

```
Routing (Maestro — Manta 00):
────────────────────────────
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1 ✅ (ESTE AGENTE)

Tier Padrão:
────────────
Manta 03-S1: Sonnet (execução)
→ Handoffs para: manta-05 (orçamento), manta-07 (cronograma), 
  manta-02 (contratual), manta-01 (claims)

RAG Collection:
───────────────
rodovias (prefixo: rod:)
  - Status: ✅ Operacional
  - Fontes: DNIT, SICRO, NBR-DNIT
  - Versão: v4.1 (expandir para v4.2)
  - Sub-prefixos: rod:geom:*, rod:pavimento:*, etc.
```

### Do ARQUITETURA-AGENTES-IA.md (v2.0.0)

```
Agente Vertical (Eixo 2):
────────────────────────
Manta 03-S1 | Rodovias | agente-infraestrutura (S1) | ✅ Operacional

Ciclo de Vida (Eixo 3):
─────────────────────
Suporta 8 fases:
1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo ← MAIS CRITICO (geometria)
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

Conhecimento Engine (RAG):
─────────────────────────
rodovias | rod: | DNIT, SICRO, NBR-DNIT | ✅ Operacional

Storage Routing (SharePoint):
──────────────────────────────
agente-infraestrutura S1 | 03_Projetos/Rodovias/* | *.pdf, *.dwg, *.xlsx
```

---

## 5. Prompts de Teste — Validação com SharePoint

Após consolidação, validar contra documentos no SharePoint:

### Teste 1: Recuperar Norma DNIT

**Prompt**: 
```
"Qual é a fórmula de raio mínimo segundo DNIT ES 101/97? 
Cite a página específica da norma."
```

**Validação**:
- Agente recupera: `rod:geom:normas:dnit-es-101`
- Resposta: R_mín = V² / (127 × (e + f))
- Página: ES 101/97, Item 5.2.1

---

### Teste 2: Caso Histórico BR-116

**Prompt**:
```
"Qual foi o raio mínimo adotado no projeto da BR-116 SP-MG? 
Qual superelevação máxima foi usada?"
```

**Validação**:
- Agente recupera: `rod:geom:casos:br-116-sp-mg`
- Resposta baseada em `01-agentes-fundamentais/.../exemplos/br-116-sp-mg-real.md`
- R ≈ 350-500m, e_máx ≈ 7-8%

---

### Teste 3: SICRO Atual

**Prompt**:
```
"Qual é o custo unitário SICRO atual (2026) para CBUQ 5cm?"
```

**Validação**:
- Agente recupera: `rod:geom:sicro:composicoes`
- Resposta: ~R$ 95-100/m² (valor atualizado 2026)
- Fonte: SICRO oficial

---

## 6. Fluxo de Consolidação

```
┌─────────────────────────────────────────────────┐
│ 1. Workflow 20 agentes (em andamento)           │
│    └─ Gera 20 documentos especializados         │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 2. Consolidação Local (esta branch)             │
│    └─ Integra em `.claude/knowledge/rodovias/`  │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 3. Migração para Supabase (RAG)                 │
│    └─ Cria rod:geom:* chunks                    │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 4. Upload para SharePoint                       │
│    └─ `01-agentes-fundamentais/...`             │
│    └─ `03_Projetos/Rodovias/...`                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 5. Atualização SKILL.md + CLAUDE.md            │
│    └─ Registra novas vertentes e capacidades    │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 6. Testes de Validação (5 prompts)              │
│    └─ Verifica agente contra novas fontes       │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ 7. PR + Merge (gate humano: MN)                 │
│    └─ Versionamento v4.3                        │
└─────────────────────────────────────────────────┘
```

---

## 7. Checklist de Integração SharePoint

### Antes de Merge

- [ ] Documentação criada em `.claude/knowledge/`
- [ ] Workflow 20 agentes completado
- [ ] Consolidação em markdown finalizada
- [ ] Migração SQL Supabase criada
- [ ] Upload para SharePoint planejado

### Após Merge (Responsabilidade PM)

- [ ] Copiar arquivos para `01-agentes-fundamentais/agente-infraestrutura-s1/`
- [ ] Atualizar `SKILL.md` com novas vertentes
- [ ] Criar `exemplos/` com casos reais
- [ ] Atualizar `refs/` com normas/tabelas
- [ ] Aplicar migração Supabase v4.3
- [ ] Testar 5 prompts de validação
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` (v2.0 → v2.1)
- [ ] Documentar em changelog

---

## 8. Referências Cruzadas

| Documento | Link SharePoint | Função |
|-----------|-----------------|--------|
| SKILL.md | `01-agentes-fundamentais/agente-infraestrutura-s1/SKILL.md` | Definição canônica |
| CLAUDE.md | `/CLAUDE.md` (repo) | Registro mestre |
| ARQUITETURA | `00-arquitetura/ARQUITETURA-AGENTES-IA.md` | Visão geral sistema |
| Projetos | `03_Projetos/Rodovias/` | Casos históricos |
| DNIT ES 101 | `01-agentes-fundamentais/agente-infraestrutura-s1/refs/` | Normativo |
| SICRO | Supabase (rod:geom:sicro) | Orçamento dinâmico |

---

## 9. Contatos Escalação

| Responsabilidade | Contato | Email | Status |
|------------------|---------|-------|--------|
| PM (Agente S1) | Maurício Neves | mn@manta.br | Ativo |
| Revisor Técnico | [Eng. Rodovias] | tech@manta.br | Ativo |
| Arquiteto IA | [Manta 16] | manta-arq@manta.br | Ativo |
| QA / Testes | [QA Team] | qa@manta.br | Ativo |

---

**Status**: 🔄 Integração com Manta Maestro planejada  
**Próxima Review**: Após consolidação workflow (24-48h)  
**Versionamento**: v4.2 → v4.3 (ao merge)

