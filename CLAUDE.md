# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2.3** (2026-09-20) — v4.2 expansão S6–S10 (Portos,
Aeroportos, Saneamento, Energia, Barragens) + análise de modelo mestre de
proposta técnico-comercial + verificação ao vivo (Supabase/SharePoint) e
correção do checklist de deploy + achados do `scripts/test_routing.py`.

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

> ⚠️ **Achado do `scripts/test_routing.py` (2026-09-20):** rodando os 28
> prompts testáveis de `tests/routing/prompts.md` contra estas regras
> literais (correspondência por substring), **10 de 28 falharam**. Causa
> raiz: keywords curtos casam por substring dentro de palavras não
> relacionadas — `ETA` casa com "proj**eta**r", `LT` casa com "fi**lt**rados",
> `porto` casa com "aero**porto**" — e isso desvia prompts de barragens/
> aeroportos para saneamento/energia/portos. Uma implementação real
> **precisa casar por palavra inteira**, não substring. Keywords também
> faltantes nas listas abaixo e já adicionadas: PIANC (portos), RBAC 154 e
> PCN (aeroportos), PMSB (saneamento), ampacidade/ACSR (energia), SIGBM e
> "dam breach" (barragens). Ver as 10 falhas completas no script.

Atualização das listas de keywords (mesmas regras acima, completadas):
- saneamento: ... `PMSB`
- energia: ... `ampacidade`, `ACSR`
- portos: ... `PIANC`
- aeroportos: ... `RBAC 154`, `PCN`
- barragens: ... `SIGBM`, `dam breach`

---

## RAG — Coleções em Supabase

| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218, Lei 14.026, editais BNDES | 🆕 v4.2 |
| energia | ene: | ANEEL editais, R1-R5 EPE, ONS, IEEE | 🆕 v4.2 |
| portos | por: | ANTAQ, PIANC, editais BNDES/ANTAQ | 🆕 v4.2 |
| aeroportos | aer: | ANAC/RBAC, ICAO Annex 14, FAA ACs | 🆕 v4.2 |
| barragens | bar: | ICOLD, CBDB, SIGBM, Lei 12.334 | 🆕 v4.2 |

> ✅ **Verificado ao vivo em 2026-09-20:** as 5 coleções acima existem de
> fato no Supabase (projeto `manta-maestro`, `ogxxgvgtulrbbppshjie`) desde
> 30/07/2026 — junto com **6 outras** não listadas aqui (rodovias, oae,
> ferrovia, metro, orcamento, institucional), total de 11. A tabela
> principal de produção do RAG é `ke_embeddings` (embeddings 384d
> bge-small-en-v1.5, 86 registros) + `manta_rag_chunks` (292 registros) —
> **não** `rag_chunks` (27 registros, tabela legada desta migração v4.2).

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

## MODELO MESTRE DE PROPOSTA

Análise de referência sobre uso da proposta MNT-2026-COM-1183_D (Concessão
Rota 2 de Julho) como modelo mestre de propostas técnico-comerciais do
Manta Maestro, validada contra a skill `proposta-comercial` (agente
A7-bd/Manta 13-bd — 18 seções canônicas). Ver `docs/MODELO-MESTRE-PROPOSTA.md`.

Recomendação: adotar como variante especializada "PTC-Infraestrutura/
Concessão de grande porte" (modo **M6**), incorporando ao padrão os blocos
de dados oficiais rastreáveis, cenários com success fee opcional, método
do paramétrico em etapas, infraestrutura incluída e ficha técnica de
fechamento — sem substituir o modo genérico M1 da skill. O texto pronto
para colar na skill de produção está em
`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`.

**Gate humano: ✅ aprovado por MN em 2026-09-10.** Falta só a aplicação
técnica: colar o bloco da Seção A do addendum em
`skill-proposta-comercial-SKILL.md` no SharePoint. Essa etapa está
bloqueada nesta sessão porque o conector `SharePoint_Manta` caiu
(MCP server disconnected) — precisa ser feita numa sessão com esse
conector ativo, ou manualmente por quem tem acesso ao SharePoint.

**Pendência a resolver antes de publicar:** a fonte de validação citada
(MNT-2026-COM-1183_**D**, 27 páginas) não foi localizada no SharePoint em
levantamento de 2026-09-10 — só existe a revisão **_C** (21 páginas,
24/08/2026), cujo controle de revisão interno não menciona uma `_D`.
Confirmar se a `_D` existe em outro local antes de publicar o addendum
citando-a como fonte, ou atualizar a referência para `_C`.

---

## DEPLOY CHECKLIST v4.2

- [x] Copiar 5 agent .md para `.claude/agents/`
- [x] Aplicar patch no CLAUDE.md master (seção Agentes)
- [x] Criar 5 coleções RAG em Supabase (`rag_chunks`) — ✅ confirmado ao vivo 2026-09-20, feito em 30/07/2026 (11 coleções reais, ver seção RAG)
- [x] Inserir 5 routing rules em `sp_agent_routing` — ✅ confirmado ao vivo 2026-09-20 (9 linhas reais)
- [x] Criar pastas SP para novos segmentos — ✅ confirmado ao vivo 2026-09-20 (5 pastas em `03_Projetos/`)
- [ ] Registrar skills no catálogo (skill registry)
- [x] Testar routing do Maestro com prompts de cada segmento — ✅ `scripts/test_routing.py` criado e rodado em 2026-09-20: 28/28 prompts testáveis executados, 18 passaram, 10 falharam (ver nota na seção ROUTING)
- [ ] Upload dos SKILL.md para SP em `01-agentes-fundamentais/`
- [ ] Atualizar `ARQUITETURA-AGENTES-IA.md` no SP (v1.0.0 → v2.0.0)
- [ ] Gate humano: aprovação MN antes de merge

---

## PROPOSTAS DA IA — aguardando confirmação MN

Geradas automaticamente pela rotina noturna do Manta Maestro Control Room
em 2026-09-20 e registradas em `agent_change_requests` (Supabase, projeto
`manta-maestro`, status `pending`) — **nenhuma numeração ou dado de
produção foi alterado**, apenas propostas para revisão humana.

- **`CR-2026-09-20-TAXONOMY-01`** — recomenda manter a numeração S6–S10
  já usada tanto por este repo quanto pelo registry ao vivo
  `manta_agent_capabilities` (registrado em 12/07, antes do SKILL.md
  v5.0.1) como canônica, e corrigir/depreciar a numeração deslocada do
  SKILL.md v5.0.1 (que insere Edificações em S6 e empurra Portos–Barragens
  para S7–S11) em vez do inverso.
- **`CR-2026-09-20-SEGMENTS-01`** — recomenda uma decisão formal sobre
  Mineração (`03-S11`) e Óleo & Gás (`03-S12`), ativos no registry ao vivo
  desde 12/07 mas não documentados em nenhum lugar (oficializar ou
  descontinuar); e recomenda atualizar a referência de
  MNT-2026-COM-1183_**D** para a revisão **_C**, já que a _D não foi
  localizada no SharePoint.

**KE-068 (barragens):** verificado ao vivo em 2026-09-20 — o erro factual
de prazo legal (fusão de dois regimes) **já foi corrigido** em
2026-07-28 (`aluci_status: pass` em `knowledge_extractions`), mas o campo
`approved_by` segue nulo — falta só a aprovação humana formal do
conteúdo já corrigido.

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

- **v4.2.3** (2026-09-20) — rotina noturna automatizada (catch-up de 3
  execuções pendentes, 18–20/09): checklist de deploy corrigido a partir
  de verificação ao vivo do Supabase/SharePoint (RAG, routing e pastas SP
  já existiam, só não estavam documentados); `scripts/test_routing.py`
  criado, 10/28 falhas encontradas nas regras de routing por substring
  (ver seção ROUTING); KE-068 confirmado corrigido desde 28/07 (aprovação
  humana ainda pendente); duas propostas de reconciliação registradas em
  `agent_change_requests` (`CR-2026-09-20-TAXONOMY-01`,
  `CR-2026-09-20-SEGMENTS-01`), aguardando confirmação MN.
- **v4.2.2** (2026-09-10) — gate humano MN aprovado para a variante M6
  (addendum de proposta técnico-comercial). Aplicação no SharePoint
  pendente (conector `SharePoint_Manta` indisponível na sessão de
  aprovação). Levantamento completo do acervo de propostas/CVs/
  apresentações no SharePoint identificou que a fonte de validação
  citada (MNT-2026-COM-1183_D) não foi localizada — só a revisão _C
  existe; ver nota em "MODELO MESTRE DE PROPOSTA" acima.
- **v4.2.1** (2026-09-01) — análise e recomendação de modelo mestre de
  proposta técnico-comercial, validada contra a proposta MNT-2026-COM-1183_D
  e a skill `proposta-comercial` (A7-bd). Ver `docs/MODELO-MESTRE-PROPOSTA.md`.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
