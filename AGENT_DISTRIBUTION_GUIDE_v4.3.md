# AGENT DISTRIBUTION GUIDE — ANTT KB v4.3

**Data:** 2026-08-08  
**Versão:** 4.3  
**Status:** Ready for Agent Integration  
**RAG Collection:** transportes_terrestres:antt-v4.3-2026-08

---

## 📋 SUMÁRIO EXECUTIVO

Conhecimento consolidado do ANTT KB v4.3 está pronto para distribuição aos 9 agentes verticais Manta (S1-S10). Estrutura:
- **RAG Collection:** 13 chunks em `manta_rag_documents` + `manta_rag_chunks`
- **Metadata Routing:** Cada chunk contém `agentes_verticais` array para filtragem automática
- **QA Status:** `VALIDACAO_PENDENTE_PROBLEMS_ABC` (validações A/B/C bloqueiam high-confidence ingestion)

---

## 🚀 AGENTES LIBERADOS PARA USO IMEDIATO

### ✅ S1 — Rodovias

**Marcos Legais Aplicáveis:**
- Lei 10.233/2001 (ANTT competências)
- Lei 8.987/1995 (concessões + reequilíbrio)
- CL 214/2025 art. 376 (NOVO: reforma tributária como vetor reequilíbrio)

**Resoluções Vigentes:**
- RCR1-4 (5.950/2021 → 6.053/2024)
- Free Flow (ANTT 6.079/2026)

**Casos Emblemáticos:**
- Via Bahia (BR-116/324/BA) — rescisão consensual R$ 9 bi
- BR-101/RJ — reequilíbrio R$ 136,9 mi
- BR-381/MG-SP (Fernão Dias) — relicitação R$ 15 bi

**Descobertas v4.3:**
- Consensualismo TCU: paradigma shift 2025-2026 (mediação → soluções consensuais + ESG)
- CL 214/2025: novo fundamento reequilíbrio (R$ 15-25 bi/ano potencial 2027-2030)
- Limite 2 reequilíbrios/10 anos + buffer 8-12% receita obrigatório
- Modelagem 3-cenários agora requerida por TCU (2025+)

**Instrução:** Usar Via Bahia como precedente para rescisões consensuais. Preparar dossiês 2027-28 com CL 214/2025 art. 376 como fundamento adicional. Flag ESG compliance desde brief do cliente.

**RAG Query Tags:** `['s1', 'rodovia', 'reequilibrio', 'tcu', 'cl-214-2025']`

---

### ✅ S2 — OAE (Pontes/Viadutos)

**Marcos Legais Aplicáveis:**
- Lei 10.233/2001
- NBR 7187:2022 (Projetos de pontes)
- NBR 9452:2023 (Inspeção estrutural) — NOVO em v4.3

**Casos Emblemáticos:**
- Ecoponte (13km, 2015-2045) — benchmark gestão reversão concessão

**Descobertas v4.3:**
- NBR 9452:2023 entrada vigor — afeta inspeção técnica em laudo concessão

**Instrução:** Atualizar protocolos inspeção com NBR 9452:2023. Usar Ecoponte como precedente em discussões reversão ativos.

**RAG Query Tags:** `['s2', 'oae', 'ponte', 'viaduto', 'nbr-9452']`

---

### ✅ S3 — Ferrovias

**Marcos Legais Aplicáveis:**
- Lei 10.233/2001 (ANTT competências)
- Lei 14.273/2021 (Marco Legal Ferrovias) — ⚠️ IMPLEMENTAÇÃO LENTA
- Lei 8.987/1995 (concessões)

**Resoluções Vigentes:**
- ANTT 5.987/2022 (Autorizações Lei 14.273)
- ANTT 6.050/2024 (Atualização processos)
- ANTT 5.902/2020 (Acidentes)
- ANTT 6.031/2023 (Operações auxiliares)

**Casos Emblemáticos:**
- FCA (Ferrovia Centro-Atlântica) — Renovação antecipada R$ 24 bi (2026)
- MRS Logística — Renovação com reequilíbrio R$ 2,8 bi
- Rumo Malha Sul — Relicitação R$ 14+ bi (4.250 km)
- Rumo Malha Oeste — Edital aprovado R$ 89 bi potencial

**ALERTAS CRÍTICOS:**
- 🔴 Lei 14.273/21 IMPLEMENTAÇÃO FRACASSADA: ZERO operadores independentes (OFI) operando
- Casos aprovados (FTL, Temape, Minas-Rio 2026) — nenhum operacional
- **Ação:** Revisar TODA projeção baseada em interoperabilidade multioperador. Retirar OFI das premissas de receita.

**Descobertas v4.3:**
- Consensualismo TCU: MRS/Rumo/FCA como precedentes solução integrada
- Onda regulatória 2026-2027: 8 leilões R$ 140 bilhões (ALTAMENTE TRIANGULADO)
- 5 renovações/aditivos pipeline: Malha Sul, Centro-Atlântica, Transnordestina, Malha Oeste, Tereza Cristina
- CL 214/2025 art. 376: aplicável ferrovias (R$ 15-25 bi/ano)

**Instrução:** Priorizar cobertura dos 8 leilões 2026 (R$ 140 bi — driver principal). AVISAR clientes sobre Lei 14.273/21 fracasso. Preparar modeling para 5 renovações com dados tráfego REAL (não projeções otimistas). Usar FCA como benchmark: renovação com devolução seções inviáveis.

**RAG Query Tags:** `['s3', 'ferrovia', 'leiloes', 'lei-14273', 'ofi-alerta', 'malha-sul', 'malha-oeste']`

---

### ✅ S4 — Metrô

**Marcos Legais Aplicáveis:**
- Lei 10.233/2001 (ANTT competência limitada)
- Legislação estadual SP/RJ

**Casos Emblemáticos:**
- Linha 4 SP (Motiva) — Aditivo 11, R$ 676 M (jun 2026)
- Rio Linha 5 — Subsídio -15% (contexto: potencial contágio ferrovias)

**Descobertas v4.3:**
- Consensualismo TCU: modelo aplicável metrô (precedentes Via Bahia, MRS)
- CL 214/2025: potencial aplicação (reequilíbrio por reforma tributária)

**Instrução:** Monitorar Rio Linha 5: -15% subsídio pode indicar stress setorial. Usar consensualismo modelo para saídas.

**RAG Query Tags:** `['s4', 'metro', 'subsidio', 'consensual']`

---

### ✅ S6 — Portos

**Marcos Legais Aplicáveis:**
- Lei 12.815/2013 (Lei dos Portos)
- Lei 10.233/2001 (ANTAQ criação)
- Res. ANTAQ 124/2025, 127/2025, 131/2025

**Casos Emblemáticos:**
- Porto de Santos — Movimentação -20%, dragagem emergencial R$ 45 M

**Descobertas v4.3:**
- ANTAQ agenda 2025: Modernização portuária (Res. 127), sandbox regulatório (Res. 131)
- Consensualismo: aplicável concessões portuárias (precedente Via Bahia)
- CL 214/2025: potencial aplicação (reequilíbrio)

**Instrução:** Monitorar seca: Porto Santos -20% pode propagar rodovia (BR-116 carga pesada). Usar consensualismo para negociações reequilíbrio.

**RAG Query Tags:** `['s6', 'porto', 'antaq', 'dragagem', 'consensual']`

---

### ✅ S8 — Saneamento

**Marcos Legais Aplicáveis:**
- Lei 14.026/2020 (Lei do Saneamento)
- SNIS (Sistema Nacional Informações Saneamento)

**Casos Emblemáticos:**
- CEDAE Rio — Faturamento -18% por seca Guanabara (2026)

**Descobertas v4.3:**
- Seca estrutural: risco setorial concentrado (potencial onda pleitos 2027-28)
- Consensualismo TCU aplicável
- CL 214/2025: novo fundamento reequilíbrio (reforma tributária)

**Instrução:** Monitorar CEDAE: -18% pode ser primeira de múltiplas reivindicações reequilíbrio por seca. Preparar estrutura reequilíbrio baseado CL 214/2025 + seca extraordinária.

**RAG Query Tags:** `['s8', 'saneamento', 'cedae', 'seca', 'reequilibrio']`

---

## ⏳ AGENTES COM GAPS — PESQUISA DEDICADA NECESSÁRIA

### 🔴 S7 — Aeroportos (GAP CRÍTICO)

**Status:** Cobertura genérica insuficiente

**Marcos Legais:**
- Lei 11.182/2005 (ANAC criação)
- RBAC (Regulamento Brasileiro Aviação Civil)
- ICAO Annex 14

**Casos Disponíveis:**
- GRU/Galeão — Revisões extraordinárias (genérico, sem detalhe)

**LACUNA CRÍTICA:**
- Nenhum caso concreto de reequilíbrio/risco identificado 2024-2026
- Cobertura de GRU/Galeão insuficiente para ação

**Instrução — Pesquisa Dedicada:**
🔍 Identificar casos de stress aeroportuário 2024-2026:
- Reequilíbrios em andamento/solicitados
- Impacto de eventos climáticos (secas, enchentes)
- Concessões em dificuldade operacional
- Potencial aplicação CL 214/2025

**RAG Query Tags:** `['s7', 'aeroporto', 'anac', 'gap-critico']`

---

### 🔴 S9 — Energia (GAP CRÍTICO + PRIORIDADE DECLARED)

**Status:** PRIORIDADE DECLARADA do CLAUDE.md v4.2 (ANEEL/State Grid) — gap inaceitável

**Marcos Legais:**
- Lei 10.848/2004 (Políticas setor elétrico)
- Lei 9.427/1996 (ANEEL criação)
- RN 1.137/2025 (Resiliência climática)
- RN 1.095/2024, RN 1.110/2024

**Casos Disponíveis:**
- Leilão 1/2026 transmissão (RAP) — sem caso concreto reequilíbrio identificado

**LACUNA CRÍTICA:**
- NENHUM caso de risco reequilíbrio em energia identificado
- Status: ZERO reequilíbrios transmissão/distribuição em stress 2024-2026
- Resiliência climática (RN 1.137/2025) não mapeada em concessões

**Instrução — Pesquisa URGENTE Dedicada:**
🔍 PRIORIDADE: Identificar concessões transmissão em stress 2024-2026:
- Concessionárias com dificuldades financeiras
- Impacto resiliência climática (RN 1.137/2025) em receitas
- State Grid concessões — status operacional/risco
- Potencial reequilíbrios por CL 214/2025
- Precedentes TCU/ANEEL

**RAG Query Tags:** `['s9', 'energia', 'aneel', 'transmissao', 'gap-critico']`

---

### 🔴 S10 — Barragens (GAP CRÍTICO)

**Status:** Cobertura insuficiente para 2026

**Marcos Legais:**
- Lei 12.334/2010 (Lei Segurança Barragens — PNSB)
- Lei 14.066/2020 (Atualizações PNSB)

**Casos Disponíveis:**
- Histórico: Brumadinho (2019), Mariana (2015) — referências, não eventos 2026

**LACUNA CRÍTICA:**
- NENHUM evento de barragem ou risco reequilíbrio em 2026 identificado
- Cobertura histórica desatualizada

**Instrução — Pesquisa Dedicada:**
🔍 Monitorar:
- ANM (Agência Nacional Mineração)
- ANA (Agência Nacional Águas)
- Identificar barragens em concessão com risco ESG/climático
- Potencial reequilíbrios por seca (como S8 saneamento)

**RAG Query Tags:** `['s10', 'barragem', 'pnsb', 'gap-critico']`

---

## 📊 INTEGRATION CHECKLIST

### Para Agentes Liberados (S1-S6, S8)

- [ ] **S1 (Rodovias):** Integrar chunks RAG com tags `['s1', 'rodovia', 'reequilibrio']`
- [ ] **S2 (OAE):** Integrar chunks RAG; atualizar NBR 9452:2023
- [ ] **S3 (Ferrovias):** Integrar chunks RAG; FLAG Lei 14.273/21 OFI ZERO
- [ ] **S4 (Metrô):** Integrar chunks RAG; monitorar subsídios
- [ ] **S6 (Portos):** Integrar chunks RAG; monitorar seca
- [ ] **S8 (Saneamento):** Integrar chunks RAG; preparar reequilíbrio framework

### Para Agentes com Gaps (S7, S9, S10)

- [ ] **S7 (Aeroportos):** Solicitar pesquisa dedicada — identificar casos stress 2024-2026
- [ ] **S9 (Energia):** URGENTE — pesquisa PRIORIZADA (CLAUDE.md v4.2)
- [ ] **S10 (Barragens):** Solicitar pesquisa dedicada — monitorar ANM/ANA

---

## 🔐 RAG ACCESS

**Project:** manta-maestro (ogxxgvgtulrbbppshjie)  
**Database:** Supabase PostgreSQL  
**Tables:**
- `manta_rag_documents` — doc_id: `antt-kb-v4.3-2026-08`
- `manta_rag_chunks` — 13 chunks com metadata routing

**Query Pattern (para agente S1, exemplo):**
```sql
SELECT chunk_id, texto, metadados_chunk 
FROM manta_rag_chunks 
WHERE doc_id = 'antt-kb-v4.3-2026-08'
  AND metadados_chunk->>'tipo' != 'routing'
  AND metadados_chunk->'agentes_verticais' @> '"S1"'
ORDER BY posicao;
```

---

## ⚠️ QA VALIDATION BLOCKERS

**3 Problemas identificados na síntese multi-agente v4.3:**

| Problema | Tipo | Status | Blocker |
|----------|------|--------|---------|
| A — Régis Bittencourt | Conflito caracterização | ⏳ Pendente | SIM (S1 rodovias) |
| B — Citations (Análise 1) | Alucinação LLM | ⏳ Pendente | SIM (credibilidade geral) |
| C — Unidades (Análise 2) | R$ 945 bi → R$ 945 mi | ✅ Validável | Não (corrigível) |

**Status:** Descobertas v4.3 marcadas como `VALIDACAO_PENDENTE_PROBLEMS_ABC`. Usar com cautela até validações A/B/C.

---

## 📌 PRÓXIMAS AÇÕES

1. **Agentes S1-S6, S8:** Integrar RAG chunks (query de metadata routing)
2. **Agentes S7, S9, S10:** Solicitar pesquisa dedicada (tickets separados)
3. **QA Validação:** Resolver Problems A/B/C antes high-confidence ingestion
4. **FASE 5:** Commit final + Push para merge

---

**Document:** Agent Distribution Guide v4.3  
**Gerado:** 2026-08-08  
**Status:** Ready for Integration

