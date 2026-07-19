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

## SLA & Tier por Agente

| Agente | Tier padrão | RTT esperado | SLA resposta | Notas |
|--------|-------------|--------------|--------------|-------|
| Manta 00 (maestro) | Haiku→Sonnet | < 1s | RTT | Router crítico; escalada automática |
| Manta 01 (claims) | Opus | < 3s | 2h | Análise jurídica complexa |
| Manta 02 (contratual) | Sonnet | < 2s | 4h | Minutas e termos legais |
| Manta 04 (imobiliário) | Sonnet | < 2s | 4h | Análise de propriedades |
| Manta 05 (orçamento) | Sonnet | < 2s | 6h | Levantamentos e BOQs |
| Manta 06 (modelagem) | Sonnet/Opus | < 3s | 8h | Modelos econômicos complexos |
| Manta 07 (cronograma) | Sonnet | < 2s | 6h | Planejamento de prazos |
| Manta 13 (business-dev) | Sonnet | < 2s | 4h | Prospecção e análise de mercado |
| Manta 14 (apresentações) | Sonnet | < 2s | 4h | Geração de decks |
| Manta 15 (advisory) | Sonnet/Opus | < 3s | 8h | Consultoria estratégica |
| Manta 16 (arquiteto-IA) | Opus | < 3s | 6h | Desenho de arquiteturas |
| Manta 03-S1 (Rodovias) | Sonnet | < 2s | 24h | Segmento maduro |
| Manta 03-S2 (OAE) | Sonnet | < 2s | 24h | Segmento maduro |
| Manta 03-S3 (Ferrovia) | Sonnet | < 2s | 24h | Segmento maduro |
| Manta 03-S4 (Metrô) | Sonnet | < 2s | 24h | Segmento maduro |
| Manta 03-S6 (Portos) | Sonnet | < 2s | 24h | Novo v4.2 |
| Manta 03-S7 (Aeroportos) | Sonnet | < 2s | 24h | Novo v4.2 |
| Manta 03-S8 (Saneamento) | Sonnet | < 2s | 24h | Novo v4.2 — **PRIORITY AySA** |
| Manta 03-S9 (Energia) | Sonnet | < 2s | 24h | Novo v4.2 — ANEEL/State Grid |
| Manta 03-S10 (Barragens) | Sonnet | < 2s | 24h | Novo v4.2 |

---

## Exemplos de Roteamento

### Exemplo 1: Análise de terminal portuário

**Prompt do usuário:**
```
Preciso analisar a viabilidade técnica de um terminal de contêineres 
em Rio Grande. Quais serão os calados mínimos, e qual é a capacidade 
anual estimada?
```

**Roteamento esperado:** → **agente-portos (Manta 03-S6)**
- Keywords detectadas: "terminal", "contêineres", "calados"
- RAG acionada: `por:*` (ANTAQ, PIANC)
- Contexto geográfico (Rio Grande) enriquecido

### Exemplo 2: Projeto de subestação elétrica

**Prompt do usuário:**
```
Qual é o procedimento para licenciar uma LT de 345 kV no estado de São Paulo? 
Preciso da documentação ANEEL e do prazo esperado.
```

**Roteamento esperado:** → **agente-energia (Manta 03-S9)**
- Keywords detectadas: "LT", "345 kV", "ANEEL", "licenciar"
- RAG acionada: `ene:*` (ANEEL editais, R1-R5 EPE, ONS)
- Sugestão de integração com Manta 02 (contratual) para minutas

### Exemplo 3: Drenagem urbana em área de expansão

**Prompt do usuário:**
```
Estou desenvolvendo um projeto de drenagem para um bairro novo em Brasília. 
Qual é a vazão de projeto, segundo a NBR 12211? Qual é o volume de retenção 
necessário para 25 anos de retorno?
```

**Roteamento esperado:** → **agente-saneamento (Manta 03-S8)**
- Keywords detectadas: "drenagem", "NBR 12211", "vazão projeto", "retenção"
- RAG acionada: `san:*` (SNIS, IWA, NBR 12211-12218, Lei 14.026)
- Integração potencial com Manta 05 (orçamento) para estudo preliminar

### Exemplo 4: Reavaliação econômica de rodovia com sondagens

**Prompt do usuário:**
```
Tenho um levantamento de sondagens SPT em uma rodovia federal. Como devo 
reclassificar o material escavado (1ª, 2ª ou 3ª categoria) e qual é o 
impacto no orçamento de terraplenagem?
```

**Roteamento esperado:** → **agente-infraestrutura S1 (Manta 03-S1)**
- Keywords detectadas: "sondagens", "SPT", "categoria DNIT", "terraplenagem"
- RAG acionada: `s1:*` (DNIT, NBR 6484, manuais de terraplenagem)
- Integração com Manta 05 (orçamento) para reestimativa pós-classificação

### Exemplo 5: Segurança de barragem após inspeção visual

**Prompt do usuário:**
```
Uma barragem de CCR apresenta fissuras em padrão de mapa. Qual é o protocolo 
de inspeção segundo o CBDB? O quanto devo aprofundar para atestar a segurança 
estrutural?
```

**Roteamento esperado:** → **agente-barragens (Manta 03-S10)**
- Keywords detectadas: "barragem", "CCR", "fissuras", "CBDB", "inspeção"
- RAG acionada: `bar:*` (ICOLD, CBDB, SIGBM, Lei 12.334)
- Sugestão de escalada para Manta 15 (advisory) se risco > nível de confiança

---

## DEPLOY CHECKLIST v4.2

**PRIORITY: Completar 7 itens [ ] antes de merge para v4.2 GA**

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
