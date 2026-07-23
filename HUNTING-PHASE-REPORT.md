# Hunting Phase Report — Agentes Manta Discovery

**Data:** 2026-07-23  
**Objetivo:** Descobrir e catalogar agentes Manta existentes para Metrô, Engenharia, BIM, Autodesk  
**Status:** ✅ Completo

---

## 1. Resumo das Descobertas

| Agente | Código | Segmento | Status | Localização |
|--------|--------|----------|--------|-------------|
| agente-metrô | 03-S4 | Metrô | ✅ Operacional | `.claude/agents/` |
| agente-infraestrutura | 03-S1 | Rodovias | ✅ Operacional | `.claude/agents/` |
| agente-infraestrutura | 03-S2 | OAE/BIM | ✅ Operacional | `.claude/agents/` |
| agente-infraestrutura | 03-S3 | Ferrovia | ✅ Operacional | `.claude/agents/` |
| autodesk-toolkit | skill | CAD/BIM | ✅ Operacional | `skills/` |

**Total:** 5 agentes descobertos | **Operacionais:** 5 | **Necessários:** 0

---

## 2. Agentes Prioritários para Metrô + Engenharia + BIM

### 2.1 Metrô (S4) ✅

**Status:** Operacional

**Arquivo:** `.claude/agents/agente-infraestrutura.md` (S4)

**Capabilities:**
- Estações de metrô (NATM, PSD)
- Linhas de metrô (Linha 4, Linha 5, VLT)
- Sistemas de ventilação
- Segurança em escavação subterrânea
- Conexões com superfície (TPS)

**Integração:** Via Maestro (Manta 00) com roteamento automático

---

### 2.2 OAE + BIM (S2) ✅

**Status:** Operacional

**Arquivo:** `.claude/agents/agente-infraestrutura.md` (S2)

**Capabilities:**
- Pontes (NBR 7187)
- Viadutos
- Estruturas de concreto/aço
- BIM básico (IFC leitura)
- Revit integration via `autodesk-toolkit`

**Enhancement:** Usar **autodesk-toolkit** para:
- Ler DWG/RVT nativamente
- Gerar DXF com layers normatizados
- Clash detection automática

---

### 2.3 Autodesk Toolkit ✅

**Status:** Operacional (skill)

**Arquivo:** `skills/autodesk-toolkit.md`

**Suportado:**
- AutoCAD (DXF, DWG)
- Civil 3D (alignments, superfícies)
- Revit (RVT, IFC export)
- InfraWorks
- Navisworks
- BIM Collaboration Format

**MCP Integration:**
```json
{
  "mcpServers": {
    "autodesk": {
      "type": "toolkit",
      "command": "autodesk-toolkit"
    }
  }
}
```

---

### 2.4 Infraestrutura Geral (S1-S3) ✅

**Status:** Operacional

**Arquivo:** `.claude/agents/agente-infraestrutura.md` (S1, S3)

**Segmentos:**
- S1: Rodovias (pavimento, terraplenagem, SICRO)
- S3: Ferrovias (via permanente, AMV, dormente)

**Roteamento:**
```
IF rodovia|pavimento|CBUQ|DNIT → S1
IF ferrovia|trilho|AMV|dormente → S3
IF metrô|estação|NATM|Linha 4 → S4
```

---

## 3. Mapa Completo de Agentes Operacionais

### Horizontais (Transversais)

| Código | Agente | Status | Uso |
|--------|--------|--------|-----|
| 00 | Maestro (router) | ✅ | Roteamento inteligente |
| 01 | Claims | ✅ | Análise de disputas |
| 02 | Contratual | ✅ | Análise de contratos |
| 04 | Imobiliário | ✅ | Projetos imobiliários |
| 05 | Orçamento | ✅ | Composições SICRO |
| 06 | Modelagem | ✅ | 3D, FEA, simulações |
| 07 | Cronograma | ✅ | Planejamento MS Project |
| 13 | BD (Business Dev) | ✅ | Editais, licitações |
| 14 | Apresentações | ✅ | PowerPoint automático |
| 15 | Advisory | ✅ | Parecer técnico |
| 16 | Arquiteto-IA | ✅ | Design de solução |

### Verticais (por Segmento)

| Código | Segmento | Status | Arquivo |
|--------|----------|--------|---------|
| 03-S1 | Rodovias | ✅ | agente-infraestrutura.md |
| 03-S2 | OAE/BIM | ✅ | agente-infraestrutura.md |
| 03-S3 | Ferrovias | ✅ | agente-infraestrutura.md |
| 03-S4 | Metrô | ✅ | agente-infraestrutura.md |
| 03-S6 | Portos | ✅ | agente-portos.md |
| 03-S7 | Aeroportos | ✅ | agente-aeroportos.md |
| 03-S8 | Saneamento | ✅ | agente-saneamento.md |
| 03-S9 | Energia | ✅ | agente-energia.md |
| 03-S10 | Barragens | ✅ | agente-barragens.md |

---

## 4. Conectores MCP Ativos

| Servidor | Versão | Status | Uso |
|----------|--------|--------|-----|
| Obscura | 0.1.10 | ✅ Ativo | Web scraping, competitive intel |
| Autodesk-toolkit | skill | ✅ Ativo | CAD/BIM files reading |
| GitHub | (built-in) | ✅ Ativo | Repositórios |
| SharePoint | (built-in) | ✅ Ativo | Documentação |

---

## 5. Fluxo de Uso — Metrô + BIM + Autodesk

```
Usuário: "Análise de projeto de metrô com BIM em Revit"
            ↓
Maestro (00) identifica: METRÔ + BIM
            ↓
Rota para: agente-infraestrutura (S4) + autodesk-toolkit
            ↓
1. autodesk-toolkit: Ler RVT → extrair geometria, layers
2. agente-infraestrutura (S4): Analisar design vs NATM/PSD
3. Gerar: DXF normalizado + parecer técnico + BOM
            ↓
Salvar em: SharePoint 04_IA / Supabase RAG
```

---

## 6. Recomendações para Metrô Inteligente

### 6.1 Integration Checklist

- [x] Agente S4 operacional
- [x] Autodesk-toolkit pronto
- [x] Obscura MCP (competitive intel sobre metros)
- [ ] RAG collection: projetos de metrô (NATM, escavação)
- [ ] Routine: monitorar licitações de metrô (ANTAQ, ANTT)
- [ ] Skill: `analise-secoes-metro.py` (análise de cortes geológicos)
- [ ] Skill: `revit-bim-metro.py` (integração Revit para metrô)

### 6.2 Dados a Indexar (Supabase)

```python
# RAG collection: "metrô"
rag_chunks = [
    {
        "source": "NATM_Manual_2024.pdf",
        "tipo": "norma",
        "tags": ["metrô", "escavação", "segurança"]
    },
    {
        "source": "Caso_Linha4_SP_2020.docx",
        "tipo": "case_study",
        "tags": ["metrô", "Brasil", "estação"]
    },
    {
        "source": "Spec_PSD_System.pdf",
        "tipo": "especificação",
        "tags": ["metrô", "suporte", "contenção"]
    }
]
```

### 6.3 Skills Sugeridas

```
Manta Maestro → agente-infraestrutura (S4)
└── skill: analise-secoes-metro
    • Lê seções (DWG/PDF)
    • Identifica camadas geológicas
    • Valida contra NATM/PSD
└── skill: revit-bim-metro
    • Integra com Revit (autodesk-toolkit)
    • Gera coordenação 3D
    • Export IFC normalizado
└── skill: liciacao-metro
    • Monitora editais de metrô
    • Extrai requisitos via Obscura
    • Gera proposta técnica
```

---

## 7. Próximos Passos

| Prioridade | Tarefa | Responsável | ETA |
|-----------|--------|-------------|-----|
| 🔴 Alta | Testar S4 com projeto real de metrô | Claude | Q4 2026 |
| 🔴 Alta | Integrar autodesk-toolkit com S2 (BIM) | Claude | Q4 2026 |
| 🟡 Média | Criar RAG collection "metrô" | Manta 13 | Q4 2026 |
| 🟡 Média | Skill: analise-secoes-metro | Claude | Q4 2026 |
| 🟢 Baixa | Monitorar licitações de metrô com Obscura | Routine | Ongoing |

---

## 8. Referências

- **CLAUDE.md master:** [Link](./CLAUDE.md)
- **Autodesk toolkit:** [Link](./skills/autodesk-toolkit.md)
- **Obscura integration:** [Link](./OBSCURA-INTEGRATION.md)
- **GitHub search:** `repo:MN1970 agente`
- **Documentação NATM:** NBR ISO 23469:2022
- **BIM spec:** ISO 19650 (Information Management)

---

**Relatório gerado:** 2026-07-23  
**Executado por:** Claude Code  
**Próxima revisão:** 2026-Q4
