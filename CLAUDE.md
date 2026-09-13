# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3-candidata** (2026-09-13) — v4.2 expansão S6–S10 (Portos,
Aeroportos, Saneamento, Energia, Barragens) + análise de modelo mestre de
proposta técnico-comercial + proposta de evolução do RAG (busca híbrida
+ metadado de versão/vigência).

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

## RAG — Evolução v4.3 (proposta, não aplicada)

Análise feita a partir de discussão sobre RAG vs. CAG e sobre uso
simultâneo dos agentes por múltiplas pessoas. Ver
`docs/RAG-EMBEDDING-HIBRIDO.md` para a análise completa e
`supabase/migrations/2026_09_13_rag_busca_hibrida.sql` para a migração
candidata.

**Diagnóstico**: o RAG atual usa embedding `BAAI/bge-small-en-v1.5`
(modelo em inglês, para conteúdo majoritariamente em português/espanhol),
busca puramente vetorial (sem componente textual para códigos de norma,
leis e siglas exatas), e nenhum metadado de versão/vigência por chunk —
esta última lacuna é a mesma causa raiz do caso já registrado nesta
seção do arquivo, em "MODELO MESTRE DE PROPOSTA" (fonte `_D` citada sem
confirmação, só `_C` localizada).

**Recomendação (3 frentes, não CAG)**:
1. Busca híbrida (vetorial + full-text `tsvector`, fusão por RRF) —
   sem dependência de re-embedding, ganho imediato.
2. Metadado `documento_revisao` / `documento_data` / `status_vigencia`
   por chunk, com `superado` excluído da busca por padrão.
3. Troca do modelo de embedding para multilíngue (`BAAI/bge-m3` ou
   `intfloat/multilingual-e5-large`) — projeto separado, pois muda a
   dimensão do vetor (384→1024) e exige re-embedding completo das 5
   coleções (janela de manutenção, custo de API; decisão de negócio,
   não só técnica).

**Gate humano: pendente.** Nenhuma parte desta proposta foi aplicada em
produção — esta sessão não tem acesso ao Supabase de produção nem
confirmação do schema real de `rag_chunks` (a migração candidata assume
um schema aproximado e precisa ser conferida antes de rodar). Filtro de
permissão por usuário/cliente (RLS) antes da busca fica registrado como
pendência separada, fora desta migração — depende de como o Maestro
operacional modela usuário/cliente hoje.

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

## DEPLOY CHECKLIST v4.3 (RAG — busca híbrida)

- [x] Documento de análise (`docs/RAG-EMBEDDING-HIBRIDO.md`)
- [x] Migração SQL candidata (`supabase/migrations/2026_09_13_rag_busca_hibrida.sql`)
- [ ] Confirmar schema real de `rag_chunks` em produção
- [ ] Ajustar migração ao schema real, se divergir
- [ ] Gate humano: aprovação MN antes de aplicar
- [ ] Aplicar migração (busca híbrida + metadado de versão)
- [ ] Retestar `tests/routing/prompts.md` pós-deploy
- [ ] (Projeto separado) Planejar janela de re-embedding para modelo multilíngue

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

- **v4.3-candidata** (2026-09-13) — proposta de evolução do RAG: busca
  híbrida (vetorial + textual), metadado de versão/vigência por chunk, e
  recomendação de troca futura do modelo de embedding para multilíngue
  (bge-small-en-v1.5 → bge-m3/multilingual-e5-large). Migração SQL
  candidata escrita; nenhuma parte aplicada em produção — gate humano
  MN pendente, assim como confirmação do schema real de `rag_chunks`.
  Ver `docs/RAG-EMBEDDING-HIBRIDO.md`.
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
