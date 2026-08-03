# FASE 1 — Execução com 10 Agentes em Paralelo

**Status**: ✅ PRONTO PARA EXECUÇÃO  
**Data**: 2026-08-02  
**Aprovado por**: MN  

---

## 📊 MAPA DE AGENTES (10 paralelos)

```
FASE 1 — 3 SEMANAS

┌─────────────────────────────────────────────────────────┐
│ SEMANA 1: RAG LOADING (5 agentes)                       │
├─────────────────────────────────────────────────────────┤
│ 🤖 Agente 1: RAG Saneamento    (S8)                    │
│ 🤖 Agente 2: RAG Energia       (S9)                    │
│ 🤖 Agente 3: RAG Portos        (S6)                    │
│ 🤖 Agente 4: RAG Aeroportos    (S7)                    │
│ 🤖 Agente 5: RAG Barragens     (S10)                   │
│                                                         │
│ Paralelo: Todos 5 rodam simultânea mente               │
│ Duração: 6-8 dias                                       │
│ Saída: 5 coleções, ~2500-5000 chunks cada              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SEMANA 2: SHAREPOINT SETUP (5 agentes)                  │
├─────────────────────────────────────────────────────────┤
│ 🤖 Agente 6: SP Portos         (S6)                    │
│ 🤖 Agente 7: SP Aeroportos     (S7)                    │
│ 🤖 Agente 8: SP Saneamento     (S8)                    │
│ 🤖 Agente 9: SP Energia        (S9)                    │
│ 🤖 Agente 10: SP Barragens     (S10)                   │
│                                                         │
│ Paralelo: Todos 5 rodam simultaneamente                │
│ Duração: 5-6 dias                                       │
│ Saída: 10 pastas, 5 SKILL.md, docs                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SEMANA 3: VALIDAÇÃO (1 agente serial)                   │
├─────────────────────────────────────────────────────────┤
│ 🤖 Agente 11: QA + Routing Tests                       │
│                                                         │
│ Serial (após Semana 1-2)                               │
│ Duração: 3-4 dias                                       │
│ Saída: Relatório final, gate Fase 2                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 EXECUÇÃO PARALELA — SEMANA 1 (RAG LOADING)

### Agente 1: RAG Saneamento (S8)
```
Tarefa: Carregar coleção 'saneamento' com ~500-1000 chunks

FONTES PRIMÁRIAS:
├─ SNIS (Sistema Nacional de Informações de Saneamento)
├─ Lei 14.026/2020 (marco do saneamento)
├─ NBR 12211-12218 (normas de projeto)
├─ Editais BNDES saneamento
└─ ANA (Agência Nacional de Águas)

EXECUÇÃO:
1. Fetch: Buscar PDFs das fontes
2. Chunk: Dividir em 200-300 tokens, overlap 50
3. Embed: Gerar embeddings vetoriais
4. Upload: Inserir em Supabase rag_chunks
5. Validate: ≥500 chunks, avg_similarity >0.7

SAÍDA ESPERADA:
{
  collection_slug: 'saneamento',
  chunks_loaded: 750,
  sources_processed: ['SNIS', 'Lei 14.026', 'NBR 12211', ...],
  status: 'success'
}
```

### Agente 2: RAG Energia (S9)
```
Tarefa: Carregar coleção 'energia' com ~500-1000 chunks

FONTES PRIMÁRIAS:
├─ ANEEL (resoluções + editais)
├─ EPE (Empresa de Pesquisa Energética)
├─ ONS (Operador Nacional de Eletricidade)
├─ IEEE (normas internacionais)
└─ State Grid (procedimentos operacionais)

[Execução similar ao Agente 1]
```

### Agente 3: RAG Portos (S6)
```
Tarefa: Carregar coleção 'portos' com ~500-1000 chunks

FONTES PRIMÁRIAS:
├─ ANTAQ (Agência Nacional de Transportes Aquaviários)
├─ PIANC (Permanent International Association of Navigation Congresses)
├─ Editais BNDES/ANTAQ
└─ Lei 12.815/2013 (Lei dos Portos)

[Execução similar]
```

### Agente 4: RAG Aeroportos (S7)
```
Tarefa: Carregar coleção 'aeroportos' com ~500-1000 chunks

FONTES PRIMÁRIAS:
├─ ANAC (Agência Nacional de Aviação Civil)
├─ RBAC 154 (Regulamentação Brasileira da Aviação Civil)
├─ ICAO Annex 14 (Aerodrome Design and Operations)
└─ FAA Advisory Circulars

[Execução similar]
```

### Agente 5: RAG Barragens (S10)
```
Tarefa: Carregar coleção 'barragens' com ~500-1000 chunks

FONTES PRIMÁRIAS:
├─ ICOLD (International Commission on Large Dams)
├─ CBDB (Comitê Brasileiro de Barragens)
├─ SIGBM (Sistema de Informação de Barragens)
├─ Lei 12.334/2010 (Segurança de Barragens)
└─ ANM (Agência Nacional de Mineração)

[Execução similar]
```

**Resultado esperado Semana 1**: 
- ✅ 5 coleções carregadas
- ✅ ~3750-5000 chunks total
- ✅ Todos com status 'success'

---

## 🔄 EXECUÇÃO PARALELA — SEMANA 2 (SHAREPOINT SETUP)

### Agente 6: SP Portos (S6)
```
Tarefa: Criar estrutura SharePoint para agente-portos

PASTAS A CRIAR:
├─ 04_IA/Manta-Maestro/01-agentes-fundamentais/agente-portos/
│  ├─ SKILL.md
│  ├─ README.md
│  ├─ refs/
│  └─ prompts/
└─ 03_Projetos/Portos/
   └─ (vazia para receber projetos)

DOCUMENTOS A CARREGAR:
├─ SKILL.md (~5 KB) — descrição do agente
├─ README.md (~2 KB) — guia de uso
├─ refs/PIANC-guidelines.pdf
├─ refs/ANTAQ-edital-2025.pdf
└─ prompts/starter-prompts.md

SAÍDA ESPERADA:
{
  agent_name: 'agente-portos',
  folders_created: 2,
  skill_md_uploaded: true,
  documents_uploaded: 5,
  status: 'success'
}
```

### Agente 7: SP Aeroportos (S7)
```
Tarefa: Criar estrutura SharePoint para agente-aeroportos
[similar ao Agente 6]
```

### Agente 8: SP Saneamento (S8)
```
Tarefa: Criar estrutura SharePoint para agente-saneamento
[similar ao Agente 6]
```

### Agente 9: SP Energia (S9)
```
Tarefa: Criar estrutura SharePoint para agente-energia
[similar ao Agente 6]
```

### Agente 10: SP Barragens (S10)
```
Tarefa: Criar estrutura SharePoint para agente-barragens
[similar ao Agente 6]
```

**Resultado esperado Semana 2**:
- ✅ 10 pastas criadas (5 agentes + 5 projetos)
- ✅ 5 SKILL.md carregados
- ✅ ~25 documentos de referência carregados
- ✅ Todos com status 'success'

---

## 🧪 EXECUÇÃO SERIAL — SEMANA 3 (VALIDAÇÃO)

### Agente 11: QA + Routing Tests
```
Tarefa: Validar Fase 1 completa + testes de routing

VALIDAÇÃO CHECKLIST:

1. RAG Collections (5 coleções)
   ├─ SELECT COUNT(*) FROM rag_chunks WHERE collection_slug='saneamento' → ≥500
   ├─ SELECT COUNT(*) FROM rag_chunks WHERE collection_slug='energia' → ≥500
   ├─ [repetir para portos, aeroportos, barragens]
   └─ Total esperado: ≥2500 chunks

2. SharePoint (10 pastas)
   ├─ Folder agente-portos: existe? ✅
   ├─ Folder agente-aeroportos: existe? ✅
   ├─ [repetir para saneamento, energia, barragens]
   ├─ Folder 03_Projetos/Saneamento: existe? ✅
   ├─ [repetir para energia, portos, aeroportos, barragens]
   └─ Total esperado: 10 pastas

3. MCP Configuration
   ├─ .mcp.json criado? ✅
   ├─ .claude/settings.json criado? ✅
   ├─ .claude/hooks/validate-claude-md.sh criado? ✅
   └─ Todos commitados no git? ✅

4. Routing Tests (30 prompts)
   ├─ "Vou fazer uma ETA de 50 mil hab/dia" → agente-saneamento (S8)?
   ├─ "Projeto de linha de transmissão 345 kV" → agente-energia (S9)?
   ├─ "Terminal de contêineres no Rio" → agente-portos (S6)?
   ├─ "Ampliação de pista no Galeão" → agente-aeroportos (S7)?
   ├─ "Barragem de 100 MW no Tejo" → agente-barragens (S10)?
   └─ Meta: ≥90% sucesso, confiança média ≥75%

5. Ambigüidades Documentadas
   ├─ "UHE = barragem (PRIMARY) OU energia (SECONDARY)?"
   ├─ "Porto fluvial = portos OU energia (PCH)?"
   └─ Todas as decisões em CLAUDE.md

6. Documentação
   ├─ ARQUITETURA-AGENTES-IA.md v2.0.0 em SharePoint? ✅
   ├─ Runbooks básicos criados? ✅
   └─ README Fase 1 finalizado? ✅

SAÍDA ESPERADA:
{
  rag_collections: { total: 5, chunks: 3750 },
  sharepoint_folders: { total: 10, verified: 10 },
  mcp_config: { files: 3, validated: true },
  routing_tests: { total: 30, passed: 28, confidence_avg: 82 },
  overall_status: 'success',
  gate_phase2: true  ← APROVADO PARA FASE 2!
}
```

**Resultado esperado Semana 3**:
- ✅ Todas as validações passando
- ✅ Routing tests com ≥90% sucesso
- ✅ Gate Fase 2 APROVADO

---

## 📋 CHECKLIST DE EXECUÇÃO

### PRÉ-REQUISITOS (Semana 0)
- [ ] Supabase credenciais prontas
- [ ] SharePoint Graph API credenciais prontas
- [ ] GitHub PAT token pronto
- [ ] Staging environments criados
- [ ] Equipe designada (Leads de semana)

### SEMANA 1 (RAG LOADING)
- [ ] Agente 1: RAG Saneamento ✅
- [ ] Agente 2: RAG Energia ✅
- [ ] Agente 3: RAG Portos ✅
- [ ] Agente 4: RAG Aeroportos ✅
- [ ] Agente 5: RAG Barragens ✅
- [ ] QA: Validar 5 coleções carregadas
- [ ] Semana 1 COMPLETA? → Sim ✅

### SEMANA 2 (SHAREPOINT SETUP)
- [ ] Agente 6: SP Portos ✅
- [ ] Agente 7: SP Aeroportos ✅
- [ ] Agente 8: SP Saneamento ✅
- [ ] Agente 9: SP Energia ✅
- [ ] Agente 10: SP Barragens ✅
- [ ] QA: Validar 10 pastas criadas
- [ ] Semana 2 COMPLETA? → Sim ✅

### SEMANA 3 (VALIDAÇÃO)
- [ ] Agente 11: QA Validation ✅
- [ ] RAG collections validadas ✅
- [ ] SharePoint folders validadas ✅
- [ ] MCP config validada ✅
- [ ] Routing tests ≥90% ✅
- [ ] Gate Fase 2? → SIM ✅ APROVADO

---

## 📊 TIMELINE

```
Seg 8 jul   ├─ Kick-off meeting (30 min)
            └─ Semana 1 INICIA

Ter-Qua-Qui ├─ Agentes 1-5 em paralelo
            ├─ Daily standup 10:00
            └─ RAG collections carregando

Sex 12 jul  └─ Semana 1 TERMINA ✅

Seg 15 jul  ├─ Validação RAG
            └─ Semana 2 INICIA

Ter-Qua-Qui ├─ Agentes 6-10 em paralelo
            ├─ Daily standup 10:00
            └─ SharePoint folders criando

Sex 19 jul  └─ Semana 2 TERMINA ✅

Seg 22 jul  ├─ Agente 11: Validação total
            └─ Semana 3 INICIA

Ter-Qua-Qui ├─ Routing tests (30 prompts)
            ├─ Documentação ambigüidades
            ├─ Daily standup 10:00
            └─ Relatório final

Qui 25 jul  └─ Semana 3 TERMINA ✅

Sex 26 jul  ├─ GATE FASE 1 → MN APROVA FASE 2?
            └─ ✅ APROVADO PARA FASE 2
```

---

## 📈 GANHOS ESPERADOS (FIM FASE 1)

| Métrica | Antes | Depois |
|---------|-------|--------|
| Agentes S6-S10 operacionais | 0 | 5 |
| RAG collections | 0 | 5 |
| Chunks de contexto | 0 | ~3750-5000 |
| Pastas SharePoint | 0 | 10 |
| Documentação | Incompleta | Completa |
| Sistema operacional | Declarativo | ✅ Operacional |

---

## 🎯 PRÓXIMO PASSO

Quando Fase 1 estiver **100% COMPLETA** (Fri 26 jul):

→ **Iniciar Fase 2** (Seg 29 jul):
- Semana 4: Workflows multi-agente (2 workflows em paralelo)
- Semana 5: Integrações MCP (3 integrations em paralelo)
- Semana 6: Automação CI/CD (3 systems em paralelo)
- Semanas 7-8: Load testing + Otimizações

---

**Status**: 🟢 PRONTO PARA COMEÇAR  
**Data de conclusão esperada**: 26 de julho (Semana 3)  
**Investimento**: 60 horas de desenvolvimento

Boa sorte! 🚀
