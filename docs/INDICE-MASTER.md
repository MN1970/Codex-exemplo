# ÍNDICE MASTER — Plano de Ação S6-S10
## Consolidação de SharePoint + Preparação RAG

**Gerado**: 2026-07-24  
**Status**: Ready to Execute  
**Owner**: mneves@mantaassociados.com (Maestro)

---

## VISÃO GERAL

Este plano estrutura a consolidação de conteúdo SharePoint para os **5 novos agentes Manta S6-S10** (Portos, Aeroportos, Saneamento, Energia, Barragens).

**Objetivo Final**: Agentes operacionais com base de conhecimento RAG fundamentada em normas + projetos reais.

**Timeline**: 21 dias (24-Jul até 14-Ago)  
**Fases**: 4 (Sincronização → RAG Prep → Validação → Go-live)  
**Esforço**: ~20 horas engenharia

---

## ARQUIVOS DESTE PLANO

Todos os arquivos estão em scratchpad e prontos para uso:

### 1. **QUICKSTART-24JUL.md** ⭐ COMECE AQUI
**Tipo**: Guia de início rápido  
**Duração**: ~2 horas  
**Para**: Colocar o plano em ação AGORA (hoje)

**Conteúdo**:
- Pré-requisitos (5 min)
- Passo-a-passo: Setup → Sync TIER 1 → Validação
- Problemas comuns + soluções
- 3 comandos para começar

**Ação**: Ler e executar hoje (24-Jul)

---

### 2. **SUMARIO-EXECUTIVO-S6-S10.md** (1 página)
**Tipo**: Sumário executivo  
**Para**: Entender a estratégia em 5 minutos

**Conteúdo**:
- Situação atual (✅/❌)
- Objetivo + resultado esperado
- 4 Fases em 3 semanas (timeline)
- Matriz de prioridade (TIER 1-4)
- Checklists por segmento (resumido)
- Riscos + mitigações
- Custos aproximados

**Ação**: Ler para entender contexto executivo

---

### 3. **PLANO-SINCRONIZACAO-S6-S10.md** (COMPLETO)
**Tipo**: Plano detalhado, referência  
**Para**: Implementação profunda, documentação

**Conteúdo** (5 seções):
1. **Matriz de Prioridade** — TIER 1-4 por segmento
   - Quais documentos sincronizar PRIMEIRO (ranking)
   - O que bloqueia (TIER 1) vs. o que enriquece (TIER 2-4)
2. **Scripts de Sincronização** — Prontos para executar
   - Setup local
   - Sync TIER 1 (normativos)
   - Validação pós-sync
   - Sync TIER 2 (projetos)
   - Análise de gaps
3. **Checklists por Segmento** — Validação local
   - S8 Saneamento (AySA priority)
   - S9 Energia (ANEEL)
   - S6 Portos (ANTAQ)
   - S10 Barragens (Lei 12.334)
   - S7 Aeroportos (RBAC/ANAC)
4. **Roadmap — 4 Fases, 21 dias**
   - Fase 1: Sync local (24-28 Jul)
   - Fase 2: RAG prep (31-Jul–04-Ago)
   - Fase 3: Validação agentes (07-11 Ago)
   - Fase 4: Go-live (14-Ago)
5. **Anexo** — Estrutura esperada local, tamanhos, timeline

**Ação**: Referência de implementação; revisar quando em dúvida

---

### 4. **SCRIPTS-PRONTOS-S6-S10.sh** (Gerador)
**Tipo**: Bash script que cria todos os outros scripts  
**Para**: Executar UMA VEZ para popular ~/

**Conteúdo** — Cria scripts em `~/`:
- `setup-sync-s6-s10.sh` — Setup local
- `sync-tier1.sh` — Sincronização TIER 1
- `validate-tier1.sh` — Validação TIER 1
- `sync-tier2.sh` — Sincronização TIER 2
- `generate-gaps-report.sh` — Análise de gaps
- `checklist-s8.sh`, `checklist-s9.sh`, ... (S6-S10) — Validação por segmento
- `generate-consolidation-report.sh` — Relatório final

**Ação executar**:
```bash
bash SCRIPTS-PRONTOS-S6-S10.sh
```

**Resultado**: Todos os scripts em `~/` prontos para executar

---

## FLUXO DE EXECUÇÃO

### Hoje (24-JUL) — RÁPIDO
1. Ler: **QUICKSTART-24JUL.md** (10 min)
2. Executar:
   ```bash
   bash SCRIPTS-PRONTOS-S6-S10.sh        # 2 min
   bash ~/setup-sync-s6-s10.sh           # 2 min
   time bash ~/sync-tier1.sh             # ~1 hora (deixa rodando)
   ```
3. Parar aqui

### Amanhã (25-JUL) — VALIDAÇÃO
1. Executar:
   ```bash
   bash ~/validate-tier1.sh              # ~5 min
   bash ~/generate-gaps-report.sh        # ~3 min
   time bash ~/sync-tier2.sh             # ~1 hora (deixa rodando)
   ```
2. Revisar relatórios; corrigir gaps se houver

### Dia 26-27-JUL — CHECKLISTS
1. Executar checklists por segmento:
   ```bash
   bash ~/checklist-s8.sh   # Saneamento
   bash ~/checklist-s9.sh   # Energia
   bash ~/checklist-s6.sh   # Portos
   bash ~/checklist-s10.sh  # Barragens
   bash ~/checklist-s7.sh   # Aeroportos
   ```
2. Revisar resultados
3. Correções finais (se necessário)

### Dia 28-JUL — CONSOLIDAÇÃO
1. Executar:
   ```bash
   bash ~/generate-consolidation-report.sh
   ```
2. Revisar relatório
3. **SINAL VERDE para FASE 2** (RAG)

### FASE 2 (31-Jul a 04-Ago) — RAG INGESTION
1. Preparar Supabase: criar tabela `rag_chunks`, prefixos storage
2. Executar ingestion: chunks + embeddings + bulk insert
3. Validar: busca semântica em RAG

### FASE 3 (07-11 Ago) — VALIDAÇÃO AGENTES
1. Testar routing Maestro → agentes corretos
2. Testar respostas fundadas em RAG
3. Gating: se ≥4/5 agentes passam, liberar staging

### FASE 4 (14-Ago) — GO-LIVE
1. Merge CLAUDE.md v4.2
2. Deploy routing rules
3. Publicar SKILL.md
4. Slack announcement

---

## MATRIZ DE DECISÃO

**Qual arquivo ler?**

| Você quer... | Leia... | Duração |
|---|---|---|
| Começar AGORA sem ler tudo | **QUICKSTART-24JUL.md** | 5 min leitura + 2h execução |
| Entender a estratégia em alto nível | **SUMARIO-EXECUTIVO-S6-S10.md** | 5 min |
| Implementar profundamente / resolver issues | **PLANO-SINCRONIZACAO-S6-S10.md** | 20 min leitura + 4h implementação |
| Executar scripts prontos | **SCRIPTS-PRONTOS-S6-S10.sh** | 30 sec setup |
| Visão consolidada (este arquivo) | **INDICE-MASTER.md** | 10 min |

---

## ESTRUTURA ESPERADA AO FINAL (DIA 28-JUL)

```
~/Manta-S6-S10-Sync/
├── 03_Projetos/
│   ├── Saneamento/           (800–1100 MB, 150–200 arquivos)
│   │   ├── 00-Normativos/    (300–400 MB) — Lei 14.026, NBR 12211-12218, SNIS
│   │   ├── 01-Projetos-Executados/  (500–700 MB) — >3 ETAs/ETEs, AySA
│   │   └── 02-Estudos-Primarios/    — PMSB, hidrológicos
│   │
│   ├── Energia/              (850–1150 MB, 180–220 arquivos)
│   │   ├── 00-Normativos/    (250–350 MB) — ANEEL REN, NBR 5422, IEEE 738
│   │   ├── 01-Projetos-Executados/  (600–800 MB) — >3 LTs, >2 SEs
│   │   └── 02-Estudos-Primarios/    — R1-R5 ANEEL
│   │
│   ├── Portos/               (600–800 MB, 120–150 arquivos)
│   │   ├── 00-Normativos/    (200–300 MB) — Lei 12.815, PIANC, NBR
│   │   ├── 01-Projetos-Executados/  (400–500 MB) — >2 contêiner, >2 granel
│   │   └── 02-Estudos-Primarios/    — hidrográficos, geotécnicos
│   │
│   ├── Barragens/            (700–1000 MB, 140–180 arquivos)
│   │   ├── 00-Normativos/    (200–300 MB) — Lei 12.334, ICOLD, CBDB
│   │   ├── 01-Projetos-Executados/  (500–700 MB) — >2 UHE, >2 abastecimento
│   │   └── 02-Casos-Referencia/     — Fundão, Brumadinho
│   │
│   └── Aeroportos/           (480–650 MB, 100–130 arquivos)
│       ├── 00-Normativos/    (180–250 MB) — RBAC 154, ICAO, FAA
│       ├── 01-Projetos-Executados/  (300–400 MB) — >2 TPS, >2 pistas
│       └── 02-Estudos-Primarios/    — mix aeronaves, TPHP
│
├── logs/
│   ├── sync-tier1-*.log      (stdout do sync TIER 1)
│   ├── sync-tier2-*.log      (stdout do sync TIER 2)
│   └── ...
│
└── *.txt (relatórios)
    ├── validate-tier1-*.txt
    ├── gaps-report-*.txt
    ├── checklist-s*.txt
    └── consolidation-report-*.txt

TOTAL: 3.5–4.7 GB, 650–880 arquivos
```

---

## CHECKPOINTS CRÍTICOS

Estes pontos DEVEM passar antes de avançar:

### Checkpoint 1 (25-Jul): TIER 1 Validado
```
Teste: bash ~/validate-tier1.sh
Esperado:
  [✓] Saneamento: >40 arquivos, >250 MB
  [✓] Energia: >40 arquivos, >200 MB
  [✓] Portos: >30 arquivos, >150 MB
  [✓] Barragens: >30 arquivos, >150 MB
  [✓] Aeroportos: >25 arquivos, >120 MB
```

**Se falhar**: Revisar logs em `~/Manta-S6-S10-Sync/logs/sync-tier1-*.log`

---

### Checkpoint 2 (28-Jul): Checklists Passando
```
Teste: bash ~/checklist-s*.sh (todos 5)
Esperado: Mínimo [✓] nas seções críticas de cada segmento
```

**Se falhar**: Gaps = documentos faltantes no SharePoint. Fazer upload manual.

---

### Checkpoint 3 (04-Ago): RAG Ingestion Completa
```
Teste: SELECT COUNT(*) FROM rag_chunks WHERE segment IN ('san:', 'ene:', 'por:', 'bar:', 'aer:');
Esperado: ~2500–3000 chunks total
```

**Se falhar**: Revisar logs de embedding/chunking

---

### Checkpoint 4 (11-Ago): Agentes Validados
```
Teste: 5 prompts de teste (um por segmento)
Esperado: ≥4/5 agentes respondem com RAG + normas corretas
```

**Se falhar**: Revisar routing + RAG queries

---

## RISCOS PRINCIPAIS

| Risco | Probab. | Impacto | Mitigation |
|-------|---------|---------|-----------|
| SharePoint lento/offline | Média | Alto | Sync fora do horário pico; usar `--max-retries 5` |
| Documentos corrompidos | Baixa | Alto | Checksum validation; retentativa automática |
| Espaço disco insuficiente | Baixa | Alto | Pré-verificar `df -h ~`; usar HD externo se necessário |
| Normas desatualizadas em SP | Média | Médio | Validar datas; marcar versão YYYY-MM-DD |
| RAG ingestion falha | Baixa | Alto | Testar com 10 documentos antes de batch grande |
| Routing não funciona | Média | Alto | Validar em staging; rodar testes FASE 3 antes go-live |

**Mais detalhes**: Ver PLANO-SINCRONIZACAO-S6-S10.md seção "Riscos e Mitigações"

---

## FÓRMULA DO SUCESSO

1. **Hoje (24-Jul)**: Ler QUICKSTART + executar setup + iniciar sync TIER 1
2. **Amanhã (25-Jul)**: Validar TIER 1 + iniciar sync TIER 2
3. **26-27-Jul**: Rodar checklists por segmento
4. **28-Jul**: Consolidation report → SINAL VERDE
5. **31-Jul–04-Ago**: Preparar RAG Supabase (em paralelo se possível)
6. **07-11-Ago**: Validar agentes
7. **14-Ago**: Go-live 🎉

---

## PRÓXIMAS AÇÕES PARA O USUÁRIO

### ✅ Imediato (próximas 2 horas)
- [ ] Ler QUICKSTART-24JUL.md
- [ ] Verificar rclone + acesso SharePoint
- [ ] Executar `bash SCRIPTS-PRONTOS-S6-S10.sh`
- [ ] Executar `bash ~/setup-sync-s6-s10.sh && bash ~/sync-tier1.sh`

### ✅ Amanhã (25-Jul)
- [ ] Executar `bash ~/validate-tier1.sh`
- [ ] Revisar relatórios + corrigir gaps
- [ ] Executar `bash ~/sync-tier2.sh`

### ✅ Semana (26-28 Jul)
- [ ] Rodar todos os checklists (S6-S10)
- [ ] Consolidation report
- [ ] Sinal verde para FASE 2

### 📋 Próximas semanas (31-Jul+)
- Preparar RAG em Supabase
- Validar agentes
- Deploy go-live

---

## DOCUMENTAÇÃO DE REFERÊNCIA

**Mantidos aqui (scratchpad)**:
- PLANO-SINCRONIZACAO-S6-S10.md
- SUMARIO-EXECUTIVO-S6-S10.md
- SCRIPTS-PRONTOS-S6-S10.sh
- QUICKSTART-24JUL.md
- INDICE-MASTER.md (este arquivo)

**Mantidos no repositório (`Codex-exemplo`)**:
- CLAUDE.md v4.2 (mapa de agentes)
- `.claude/agents/agente-*.md` (5 novos agentes)

**Referências externas**:
- PLANO-SINCRONIZACAO-S6-S10.md: Seção 2 (Scripts completos)
- PLANO-SINCRONIZACAO-S6-S10.md: Seção 3 (Checklists por segmento)
- PLANO-SINCRONIZACAO-S6-S10.md: Seção 4 (Roadmap detalhado)

---

## FAQ

**P: Por onde começo?**  
R: QUICKSTART-24JUL.md. Leia hoje, execute hoje.

**P: Quanto tempo leva tudo?**  
R: Setup = 2h. Sync TIER 1 = 1h. Validação = 30min. Sync TIER 2 = 1.5h. Total ~5h spread em 4 dias.

**P: Posso fazer TIER 2 antes de TIER 1 estar 100% validado?**  
R: Não é recomendado. TIER 1 (normas) é o bloqueador. Espere validação antes de TIER 2.

**P: E se um segmento tiver muitos gaps?**  
R: Verificar SharePoint manualmente. Se documentos não existem, criar/fazer upload. Rodar sync novamente.

**P: Posso deixar scripts rodando em background?**  
R: Sim! Use `nohup bash ~/sync-tier1.sh > ~/Manta-S6-S10-Sync/logs/sync.out 2>&1 &`

**P: Qual o tamanho final esperado?**  
R: 3.5–4.7 GB (com projetos reais pode chegar a 6–8 GB).

**P: Depois de sincronizar, o que fazer com os documentos?**  
R: FASE 2 = Preparar RAG ingestion em Supabase (chunking + embedding).

**P: Quem faz FASE 2 (RAG)?**  
R: Idealmente um engenheiro IA/ML. Scripts preparados em PLANO-SINCRONIZACAO-S6-S10.md seção 4.

**P: Posso cancelar sincronização no meio?**  
R: Sim, Ctrl+C. Rclone vai retomar de onde parou na próxima execução (se usar `--checksum`).

---

## SUPORTE

Se tiver dúvidas:
1. Revisar seção apropriada do arquivo (veja Matriz de Decisão acima)
2. Procurar em "PROBLEMAS COMUNS" (QUICKSTART-24JUL.md)
3. Revisar logs em `~/Manta-S6-S10-Sync/logs/`
4. Contactar: mneves@mantaassociados.com (Maestro)

---

## RESULTADO FINAL

**24 Ago (depois de tudo)**:

✅ 5 novos agentes operacionais (S6-S10)  
✅ Base de conhecimento RAG consolidada (3000+ chunks)  
✅ Routing Maestro funcional  
✅ Documentação pronta para uso  
✅ Time treinado no novo intake Q2 (8 fases)

---

**Maestro | Manta 00 | 2026-07-24 | v1.0**
