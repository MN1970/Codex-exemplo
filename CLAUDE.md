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

---

## AUTOSCALING — Política de Escalagem Automática (v1.0, 2026-08-08)

**Princípio Fundamental:** "Sempre comece com múltiplos agentes em paralelo. Diminua apenas se volume < 500 tokens."

Maestro (Manta 00) decide **automaticamente**:
- Número de agentes a disparar (1, 3, 8, ou 16)
- Modelo primário (Haiku, Sonnet, Opus)
- Padrão de orquestração (direto, pipeline, parallel, fan-out)

Baseado em: **volume de input** + **complexidade da tarefa**

### Volume Bands

| Band | Tokens | Agentes | Modelo | Wall-Clock | Padrão |
|------|--------|---------|--------|-----------|--------|
| **Pequeno** | 0–500 | 1 | Haiku | <30s | Conversa direta |
| **Médio** | 500–2000 | 3–4 | Sonnet + Haiku | 5–10 min | Pipeline 2 etapas |
| **Grande** | 2000–5000 | 8 | Sonnet + Haiku | 20–30 min | Pipeline 3 etapas |
| **Extra-Grande** | 5000+ | 16 | Sonnet + Haiku (paralelo) | 30 min–2h | Lotes 16 + consolidação |

### Matriz de Seleção de Modelo

| Volume | Complexidade | Modelo Primário | Modelo Secundário | Motivo |
|--------|---|---|---|---|
| Pequeno | Baixa | **Haiku** | — | Velocidade máxima |
| Pequeno | Alta | **Sonnet** | — | Complexidade demanda Sonnet |
| Médio | Baixa | **Haiku** | Haiku | Paralelizar Haikus é eficiente |
| Médio | Média | **Sonnet** | Haiku | Sonnet crítico, Haiku suporte |
| Médio | Alta | **Sonnet** | Sonnet | Ambos Sonnet para robustez |
| Grande | Qualquer | **Sonnet** | Haiku | **PADRÃO MANTA**: Sonnet análise, Haiku paralelo |
| Extra-Grande | Qualquer | **Sonnet** | Haiku | Maximize throughput |
| Qualquer | Crítica* | **Opus** | Sonnet | *Rare: claims reequilíbrio, M&A. Opus + votação Sonnet |

### Algoritmo Simplificado

```
1. Contar tokens(input + context)
2. Classificar volume (Pequeno/Médio/Grande/Extra-Grande)
3. Detectar complexidade (keywords: claim, edital, concessão, etc.)
4. Selecionar modelo primário + secundário da Matriz acima
5. Escolher padrão: direto (1 agente) | pipeline (8 agentes) | lotes (16 agentes)
6. Selecionar agentes relevantes (routing + contexto do projeto)
7. Executar e registrar em rag_learning_log: tokens, wall-clock real, status
8. Retornar resultado ao usuário
```

### Exemplos de Decisão

**Cenário 1:** "Qual a SELIC hoje?"
- Volume: 15 tokens → **Pequeno**
- Modelo: **Haiku**, conversa direta, <30s
- Agentes: 1 (nenhum workflow)

**Cenário 2:** "Analise este edital de concessão rodoviária (10 páginas)"
- Volume: 1200 tokens → **Médio**
- Modelo: **Sonnet + Sonnet + Haiku** (3 agentes)
- Agentes: A9 (regulatório) + S1 (técnico) + A7 (mercado)
- Pattern: Pipeline 2 etapas (análise paralela → síntese) — 5–10 min

**Cenário 3:** "Proposta comercial completa para concessão até amanhã"
- Volume: 3500 tokens → **Grande**
- Modelo: **4 Sonnet + 4 Haiku** (8 agentes)
- Agentes: Etapa 1 (A9, S1, A7, A10) → Etapa 2 (A6, A5, A4, A3) → Etapa 3 (A8, A1)
- Pattern: Pipeline 3 etapas (análise → síntese → entrega) — 25 min wall-clock

### Regras Invioláveis

1. **Sempre múltiplos agentes por padrão** — serial é exceção, não regra
2. **Haiku é padrão para paralelo massivo** — não use Sonnet para tasks menores em fan-out
3. **Sonnet para análise única crítica** — qualidade > velocidade
4. **Opus apenas para reequilíbrio/M&A** — raro, alto risco, alto impacto
5. **Pipeline sem barrier é padrão** — evite parallel() com barrier desnecessário

### Monitoramento Semanal

Toda segunda-feira: analisar `rag_learning_log` da semana
- Quais combinações volume/modelo/agentes tiveram melhor SLA?
- Quais tiveram pior taxa de sucesso?
- Qual foi o custo médio por tipo de tarefa?
- Atualizar esta política se patterns mudam

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

## DEPLOY CHECKLIST v4.2

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

## Histórico de versões

- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
