# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3** (2026-08-22) — base de consumos por receita setorial
(programa de pesquisa + schema + catálogo de 171 fontes BR/internacionais/EUA).
Base anterior:
v4.2 (2026-07-05) — expansão S6–S10 (Portos, Aeroportos, Saneamento,
Energia, Barragens).

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

## BASE DE CONSUMOS POR RECEITA SETORIAL (v4.3)

Quanto de insumo físico é consumido por unidade de receita/investimento em cada
segmento de construção pesada. Abordagem **top-down**: intensidade macro, não
composição serviço por serviço.

- Programa, método e fontes: `docs/pesquisa-consumos/`
- Dados, schema e validador: `data/consumos/`, `tools/validate_consumos.py`

**Oito famílias de insumo** (vocabulário fechado): `mao_de_obra`,
`equipamentos`, `aco`, `concreto`, `cimento`, `agregados`, `combustivel`,
`outros_materiais`.

**Catálogo de fontes** — 171 fontes em 7 camadas: estatística oficial (PAIC e
matriz de insumo-produto do IBGE são a espinha dorsal), governo e planejamento
setorial, associações setoriais, índices econômicos, academia, multilaterais, e
proprietária cite-only. Inclui 35 fontes do mercado americano
(`docs/pesquisa-consumos/06-FONTES-EUA.md`), com o par **CNAE 42 ↔ NAICS 237**
para comparação internacional.

**Armadilha registrada** — a cesta do **ENR Construction Cost Index** (200 h de
mão de obra + 25 cwt de aço + 1,128 t de cimento + 1.088 bf de madeira) *parece*
coeficiente de consumo e **não é**: a ENR mantém as quantidades constantes para
rastrear preço. Serve como deflator, nunca como consumo.

**Estado (2026-08-22)** — 8 linhas de intensidade no recorte agregado CNAE
41/42/43; os segmentos S1–S10 ainda vazios. Nenhuma linha verificada contra a
fonte primária: o egress da sessão de coleta bloqueou `ibge.gov.br`, `snic.org.br`
e demais. Detalhe em `data/consumos/validacao/relatorio.md`.

**Regras duras, cobradas pelo validador:**

1. Fonte com `entrega = custo_unitario_agregado` (ministérios, PPI, Novo PAC,
   Banco Mundial, INFRALATAM) **não** origina linha de intensidade — publica
   CAPEX de projeto, não coeficiente. É denominador, não numerador.
2. `licenca = cite_only` **nunca** carrega valor numérico.
3. `metodo = indireto` exige `memoria_calculo` reproduzível.
4. `denominador`, `ano_base` e `deflator` obrigatórios em toda linha — receita da
   PAIC ≠ CAPEX de projeto ≠ valor de obra contratada.
5. `verificacao = fonte_primaria_lida` só quando o documento foi aberto. Valor
   `snippet_busca` não vai para entregável de cliente.

```bash
python3 tools/validate_consumos.py --stats     # valida + matriz de cobertura
python3 tools/validate_consumos.py --selftest  # prova que as regras reprovam
```

**Coleção RAG `consumos` (prefixo `cns:`) — PLANEJADA, NÃO CRIADA.** Decisão de
MN: o repositório é a fonte da verdade nesta rodada. Migração Supabase, agente
horizontal Manta 17 e artefato React estão em `docs/pesquisa-consumos/05-BACKLOG.md`.

---

## Arquivos deste repositório

```
Codex-exemplo/
├── CLAUDE.md                         # este arquivo (master registry)
├── docs/
│   └── pesquisa-consumos/            # 🆕 v4.3 programa de pesquisa de consumos
├── data/
│   └── consumos/                     # 🆕 v4.3 schema + CSVs + registro de fontes
├── tools/
│   └── validate_consumos.py          # 🆕 v4.3 validador da base
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

- **v4.3** (2026-08-22) — base de consumos por receita setorial. Programa de
  pesquisa (método direto × indireto, disciplinas de denominador/deflator/moeda),
  JSON Schema de intensidade e de fonte, validador com autoteste, crosswalk
  CNAE 2.0 ↔ S1–S10 ↔ NAICS, catálogo de 171 fontes BR, internacionais e dos
  EUA (ENR incluso) em 7 camadas,
  e 8 linhas de intensidade no recorte agregado CNAE. Coleta limitada por
  bloqueio de egress — nenhuma linha verificada na fonte primária. Ticket
  MNT-2026-CONSUMOS-SETORIAIS.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
