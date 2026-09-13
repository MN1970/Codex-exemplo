# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.2.3** (2026-09-13) — v4.2 expansão S6–S10 (Portos,
Aeroportos, Saneamento, Energia, Barragens) + variante de proposta
técnico-comercial para concessões de grande porte, confirmada como já
implementada na skill de produção (ver "MODELO MESTRE DE PROPOSTA").

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

## MODELO MESTRE DE PROPOSTA

**✅ Status: já implementado na skill de produção — nenhuma publicação
pendente.**

Análise original (2026-09-01) sobre usar a proposta MNT-2026-COM-1183_D
(Concessão Rota 2 de Julho) como modelo mestre de propostas
técnico-comerciais, validada contra a skill então chamada
`proposta-comercial` (agente A7-bd/Manta 13-bd — 18 seções canônicas). Ver
`docs/MODELO-MESTRE-PROPOSTA.md` e o addendum de deploy em
`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md` (histórico — conteúdo já
superado pela skill em produção, mantidos apenas como registro).

**O que mudou (confirmado em 2026-09-13):** a skill de produção foi
reorganizada. `skill-proposta-comercial-SKILL.md` é hoje um stub
"DEPRECATED"; a fonte de verdade passou a ser
`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (atividade A1,
camada L1.7). Essa skill **já contém** a variante equivalente ao "M6"
proposto aqui — lá chamada **"Tipo A / Concessão de Infraestrutura de
Grande Porte"** — com os mesmos 5 blocos recomendados (Dados Oficiais do
Empreendimento, Cenários de Contratação, Método do Paramétrico em Etapas,
Infraestrutura e Ferramentas Incluídas, Ficha Técnica), como perfil do
"Tipo A" genérico (a numeração de modos mudou de M1–M6 para
Tipo A / Tipo B / PRC).

**A pendência _C/_D já foi resolvida na fonte, de forma independente
desta análise:** o changelog da skill (v3.3.7, 2026-09-10) registra que a
alegação de validação contra "MNT-2026-COM-1183_D" foi removida por não
corresponder a nenhum documento real no SharePoint (só existe
`MNT-2026-COM-1183_C_3.pdf`) — a mesma divergência identificada no
levantamento do acervo desta sessão. A skill hoje é mais conservadora que
a proposta original deste repositório: marca a variante como **"pendente
de validação contra uma proposta real específica antes de uso em
cliente"**, em vez de alegar uma validação que não existe.

**Achado adicional (v3.3.9, 2026-09-11):** o mesmo padrão de fabricação
se repetiu — uma citação a "MNT-2026-COM-1301 (Rota da Liberdade, Lote
07)" como fonte de validação do template `template-ptc-tipo-a-v1.html`
também não correspondia a documento real; foi encontrada e corrigida do
mesmo jeito. Vale atenção redobrada a citações de "proposta real X"
como fonte de validação em qualquer skill — confirmar contra o SharePoint
antes de aceitar.

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

- **v4.2.3** (2026-09-13) — confirmado que a variante de proposta para
  concessões de grande porte (antigo "M6") já está implementada na skill
  de produção, sob nova estrutura/local (`02-atividades/A1-proposta/
  SKILL.md`, "Tipo A / Concessão de Infraestrutura de Grande Porte",
  v3.3.9). A divergência _C/_D já havia sido corrigida na fonte de forma
  independente (changelog v3.3.7), com achado adicional de uma segunda
  citação fabricada (v3.3.9, MNT-2026-COM-1301) também corrigida. Nenhuma
  ação de publicação restante — ver "MODELO MESTRE DE PROPOSTA" acima.
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
