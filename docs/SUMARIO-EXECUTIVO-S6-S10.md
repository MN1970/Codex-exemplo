# SUMÁRIO EXECUTIVO — Maestro S6–S10
## Consolidação de SharePoint em 4 fases, 3 semanas

**Data**: 2026-07-24 | **Responsável**: mneves@mantaassociados.com | **Status**: Ready to Execute

---

## SITUAÇÃO ATUAL

✅ **Completo**:
- CLAUDE.md v4.2 — Mapa de 20 agentes (11 horizontais + 5 verticais S1-S4 + 5 novos S6-S10)
- 5 arquivos `.md` dos agentes criados em `.claude/agents/`
- Routing rules documentadas no CLAUDE.md

❌ **Pendente** (ESTE PLANO RESOLVE):
- SharePoint: 5 pastas `03_Projetos/{Saneamento|Energia|Portos|Aeroportos|Barragens}` estruturadas?
- Normas + projetos sincronizados localmente?
- Validação de gaps (documentos faltantes)?
- RAG collections em Supabase carregadas
- Agentes testados end-to-end

---

## OBJETIVO

Consolidar **conteúdo SharePoint** para S6–S10, preparar para **RAG ingestion** (Supabase), e validar **routing do Maestro**.

**Resultado**: Agentes S6–S10 operacionais, com base de conhecimento fundamentada em normas + projetos reais.

---

## ESTRATÉGIA: 4 FASES EM 21 DIAS

### FASE 1: SINCRONIZAR TIER 1 + TIER 2 (24–28 JUL)
**Duração**: 5 dias | **Esforço**: ~8 horas | **Bloqueia**: Outras fases

| Dia | Tarefa | Duração | Output |
|-----|--------|---------|--------|
| 24-Jul | Setup local + sync TIER 1 (normas) | 2h | `~/Manta-S6-S10-Sync/03_Projetos/**/00-Normativos` |
| 25-Jul | Validação TIER 1 + análise gaps | 3h | `validate-tier1-report.txt` + gaps identificados |
| 26-Jul | Sync TIER 2 (projetos + editais) | 2h | `01-Projetos-Executados/` + `02-Estudos-Primarios/` |
| 27-Jul | Checklists por segmento (S6-S10) | 2h | 5 checklists validados |
| 28-Jul | Consolidation report + aprovação | 1h | Sinal verde para RAG |

**Comando rápido**:
```bash
export WORK_DIR=~/Manta-S6-S10-Sync
bash setup-sync-s6-s10.sh && bash sync-tier1.sh && bash validate-tier1.sh
```

---

### FASE 2: PREPARAR RAG (31 JUL – 04 AGO)
**Duração**: 5 dias | **Esforço**: ~6 horas | **Dependência**: Fase 1

**O que fazer**:
1. Criar collections em Supabase (`rag_chunks` table com 5 prefixos: `san:`, `ene:`, `por:`, `bar:`, `aer:`)
2. Chunking/embedding (PDFs → chunks 1024 tokens → embeddings via Claude)
3. Bulk insert em `rag_chunks` com metadata (segment, source, doc_type)

| Segmento | Prioridade | Arquivos-fonte | Chunks esperados |
|----------|-----------|-----------------|------------------|
| **S8 Saneamento** | P0 | Lei 14.026, NBR 12211-12218, 3 projetos ETA/ETE | 500–700 |
| **S9 Energia** | P0 | ANEEL REN, NBR 5422, R1-R5 ANEEL, 3 LTs | 600–800 |
| **S6 Portos** | P1 | Lei 12.815, PIANC, 3 terminais | 400–500 |
| **S10 Barragens** | P1 | Lei 12.334, ICOLD, 3 barragens | 450–600 |
| **S7 Aeroportos** | P2 | RBAC 154, ICAO Annex 14, 3 TPS | 350–450 |

**Comando template**:
```bash
python3 /path/to/ingest-rag.py \
  --source ~/Manta-S6-S10-Sync/03_Projetos/Saneamento \
  --segment san \
  --model claude-3-5-sonnet \
  --batch-size 100
```

**Checkpoints**:
- [x] Supabase project preparado
- [x] Table `rag_chunks` criada com schema correto
- [x] Ingestion scripts testados com 10 documentos
- [x] Embeddings validados (similaridade semântica)
- [x] Todos os 5 segmentos ingestionados

---

### FASE 3: VALIDAR AGENTES (07–11 AGO)
**Duração**: 5 dias | **Esforço**: ~4 horas | **Dependência**: Fase 2

**Testes por segmento** (todos devem passar):

```
S8 Saneamento
├─ Prompt: "Projeto ETA com 100k m³/dia para AySA, qual abordagem?"
└─ Esperado: Agente cita Lei 14.026, NBR 12211, sugere ETA com coagulação+floculação+filtração

S9 Energia
├─ Prompt: "Qual ampacidade de cabo ACSR 480 mm² a 50°C?"
└─ Esperado: Agente consulta IEEE 738, cita tabelas de referência, refere-se a ANEEL REN

S6 Portos
├─ Prompt: "Dragagem de aprofundamento para terminal contêiner, volume esperado?"
└─ Esperado: Agente consulta projeto similar do RAG, recomenda volume + método

S10 Barragens
├─ Prompt: "Qual a Lei que proíbe alteamento a montante?"
└─ Esperado: Lei 12.334/2010 + Lei 14.066/2020, ZAS/ZSS, PAE obrigatório

S7 Aeroportos
├─ Prompt: "RBAC 154 para pista de 3.000 m servindo ATR72?"
└─ Esperado: Agente calcula categoria de código, cita comprimento mínimo, pavimento
```

**Gating**: Se ≥4/5 agentes passam, liberar para staging. Se <4/5, revisar RAG + routing.

---

### FASE 4: GO-LIVE (14 AGO)
**Duração**: 1 dia | **Esforço**: ~2 horas | **Dependência**: Fase 3

| Tarefa | Owner | Checklist |
|--------|-------|-----------|
| Merge CLAUDE.md v4.2 ao repo principal | Maestro | [ ] |
| Criar 5 routing rules em `sp_agent_routing` | Usuário (DBA) | [ ] |
| Deploy SKILL.md ao SharePoint | Usuário | [ ] |
| Slack announcement | Maestro | [ ] |
| Atualizar `ARQUITETURA-AGENTES-IA.md` | Maestro | [ ] |

**Resultado**: 5 novos agentes ao vivo, roteáveis pelo Maestro, com base de conhecimento RAG.

---

## MATRIZ DE PRIORIDADE (TIER 1-4)

### TIER 1 — Crítico (SINCRONIZE PRIMEIRO)
Bloqueadores: sem isso, agentes não têm base legal/técnica.

**Exemplo S8**: Lei 14.026, NBR 12211-12218 (projeto ETA), SNIS
**Exemplo S9**: ANEEL REN, NBR 5422, IEEE 738
**Exemplo S6**: Lei 12.815, PIANC, NBR 9782

**Ação**: Sincronizar TODAS as pastas `00-Normativos/` (TIER 1 = "Normativos")

---

### TIER 2 — Alto (PARALELO COM TIER 1)
Projetos executados + editais: fornecem contexto real.

**Exemplo S8**: 3 projetos ETA (>10k m³/dia), 3 projetos ETE (>10k PE), PMSB
**Exemplo S9**: 3 LTs leiloadas, R1-R5 ANEEL completos
**Exemplo S6**: 3 terminais (contêiner, granel sólido, granel líquido)

**Ação**: Sincronizar `01-Projetos-Executados/` + `02-Estudos-Primarios/`

---

### TIER 3 — Médio (PRÓXIMA SEMANA)
Estudos técnicos, procedimentos internos Manta.

**Ação**: Agendar para 31-Jul. Não bloqueia função dos agentes.

---

### TIER 4 — Referência (CONFORME DISPONÍVEL)
Editais históricos, casos internacionais, publicações de mercado.

**Ação**: Background. Aumenta valor mas não é crítico.

---

## CHECKLIST POR SEGMENTO

Cada segmento deve ter ao final da FASE 1:

```
S8 Saneamento (AySA PRIORIDADE):
  ✓ 00-Normativos: Lei 14.026, Lei 11.445, NBR 12211-12218, SNIS, ANA NR, ERAS/AySA
  ✓ 01-Projetos: >3 ETAs, >3 ETEs, >2 AySA
  ✓ 02-Estudos: PMSB, hidrológicos, geotécnicos

S9 Energia (ANEEL):
  ✓ 00-Normativos: ANEEL REN, ONS PdR, NBR 5422, IEEE 738, IEC 60826
  ✓ 01-Projetos: >3 LTs, >2 subestações
  ✓ 02-Estudos: R1-R5 ANEEL, estudos de sistema

S6 Portos (ANTAQ):
  ✓ 00-Normativos: Lei 12.815, Lei 14.301, PIANC, ROM, NBR 9782/6122
  ✓ 01-Projetos: >2 contêiner, >2 granel, dragagem
  ✓ 02-Estudos: hidrográficos, geotécnicos, econômicos

S10 Barragens (ICOLD + Lei 12.334):
  ✓ 00-Normativos: Lei 12.334, Lei 14.066, ANM, ICOLD, CBDB
  ✓ 01-Projetos: >2 UHE, >2 abastecimento, >2 rejeitos
  ✓ 02-Casos: Fundão, Brumadinho (post-mortem)

S7 Aeroportos (RBAC/ANAC):
  ✓ 00-Normativos: RBAC 154, ICAO Annex 14, FAA ACs, DECEA ICA 100-12
  ✓ 01-Projetos: >2 TPS, >2 pistas/taxiways
  ✓ 02-Estudos: mix de aeronaves, TPHP (movimentos)
```

---

## TAMANHOS ESPERADOS (após FASE 1)

| Segmento | TIER 1 | TIER 2 | Total | Arquivos |
|----------|--------|--------|-------|----------|
| **S8** | 300–400 MB | 500–700 MB | 800–1100 MB | 150–200 |
| **S9** | 250–350 MB | 600–800 MB | 850–1150 MB | 180–220 |
| **S6** | 200–300 MB | 400–500 MB | 600–800 MB | 120–150 |
| **S10** | 200–300 MB | 500–700 MB | 700–1000 MB | 140–180 |
| **S7** | 180–250 MB | 300–400 MB | 480–650 MB | 100–130 |
| **TOTAL** | 1.1–1.6 GB | 2.3–3.1 GB | **3.5–4.7 GB** | **650–880** |

*Nota: Com projetos reais grandes (.dwg, videos), pode chegar a 6–8 GB.*

---

## RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigation |
|-------|---------------|--------|-----------|
| SharePoint site offline/lento | **Média** | Alto | Usar `--max-retries 5` em rclone; sincronizar fora do horário pico (19h) |
| Arquivos corrompidos no transfer | **Baixa** | Alto | Validação checksum (rclone: `--checksum`) |
| Espaço em disco insuficiente | **Baixa** | Alto | Pré-verificar: `df -h ~`; excluir TIER 4 se necessário |
| Normas desatualizadas em SharePoint | **Média** | Médio | Validar datas de documentos; marcar com "versão conforme YYYY-MM-DD" |
| RAG ingestion falha | **Baixa** | Alto | Testar com 10 documentos primeiro; usar batch pequenos (100 chunks) |
| Routing não funciona | **Média** | Alto | Rodar testes em staging antes do go-live (FASE 3) |

**Prioridade**: Mitigar TIER 1 (normas) — sem isso, agentes não são legal/tech compliant.

---

## CUSTOS (APROXIMADOS)

| Item | Custo | Notas |
|------|-------|-------|
| **Armazenamento local** | R$ 0 | Pasta ~/Manta-S6-S10-Sync |
| **Supabase storage** | R$ 0–50 | 5 GB storage livre; >5 GB paga |
| **Embeddings Claude** | R$ 30–80 | ~3000 chunks × $0.02/1K embeddings |
| **Rclone (open-source)** | R$ 0 | Gratuito |
| **Tempo engenharia** | ~20 horas | Setup (2h) + sync (4h) + validate (4h) + RAG (6h) + test (4h) |
| **TOTAL** | R$ 30–130 | Ou ~R$ 2000–3000 em cust computacional/hora |

*Custo é baixo se usar Haiku (modelo de embedding mais barato) e batch processing.*

---

## PRÓXIMOS PASSOS (HOJE, 24-JUL)

1. **Verificar acesso SharePoint**:
   ```bash
   rclone lsd sharepoint:"Manta Associados/Documentos Compartilhados/03_Projetos"
   # Deve retornar: Saneamento, Energia, Portos, Aeroportos, Barragens
   ```

2. **Preparar local**:
   ```bash
   bash setup-sync-s6-s10.sh
   ```

3. **Iniciar sync TIER 1**:
   ```bash
   bash sync-tier1.sh  # Vai demorar 30–60 min, deixe rodando
   ```

4. **Enquanto aguarda**, revisar este plano + checklists por segmento.

5. **Amanhã (25-Jul)**, executar validações:
   ```bash
   bash validate-tier1.sh
   bash generate-gaps-report.sh
   ```

6. **Depois, paralelo com correção de gaps**:
   ```bash
   bash sync-tier2.sh
   ```

---

## RESULTADO FINAL (DIA 28-JUL)

✅ Conteúdo local consolidado (3–5 GB, 650–880 arquivos)
✅ Gaps identificados + documentados
✅ Checklists de validação passados (S6-S10)
✅ Pronto para RAG ingestion
✅ Sinal verde para FASE 2

**Após FASE 2 (04-AGO)**: Agentes têm base de conhecimento RAG fundada em normas + projetos reais.
**Após FASE 3 (11-AGO)**: Agentes validados end-to-end.
**FASE 4 (14-AGO)**: Go-live público.

---

**Maestro | Manta 00 | 2026-07-24**
