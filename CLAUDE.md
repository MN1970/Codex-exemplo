# CLAUDE.md — Manta Maestro (Agent Registry)

Registro mestre dos agentes IA da Manta Associados. Este arquivo é o
"CLAUDE.md master" referenciado pelos SKILL.md e pelos runbooks
operacionais no SharePoint.

Versão: **v4.3** (2026-08-30) — registro da skill transversal
`manta-visual-dinamico` (padrão visual dinâmico para artefatos HTML).

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

## SKILLS TRANSVERSAIS (C1) — Padrão Visual

Skills reutilizáveis (camada C1 da arquitetura) que qualquer agente
horizontal ou vertical invoca para garantir consistência visual e de
conteúdo nos artefatos entregues ao cliente.

| Skill | Cobre | Usar com |
|-------|-------|----------|
| `padrao-manta` | Esqueleto obrigatório (logo, abas, rastreabilidade) | Todo artefato para cliente |
| `manta-visual-dinamico` | Refinamento dinâmico (degradê de cor, tabelas, texto, Excel, grade×abas) | **v4.3** — junto com `padrao-manta` em artefatos institucionais/cliente |

### `manta-visual-dinamico` — regras-chave

1. **Degradê de cor por bloco** — 5 tons interpolando terracota→vinho
   (`#E0793D → #BF4D19 → #8F3D22 → #7A3B22 → #5F2C2B`), aplicado por
   seção/bloco (band do cabeçalho, borda superior de cards, sidenav e
   sub-abas ativas). Transições suaves (`background .3s ease`; troca de
   aba com `fadeIn .28s ease`). Nunca usar cores fora da família
   terracota/vinho na casca Manta — verde/azul/vermelho só em mockups
   que representem a paleta de OUTRA metodologia sendo comparada
   (ex.: navy do BCG, vermelho do Bain).
2. **Retigráfico ≠ Tempo × Caminho** — retigráfico é inventário linear
   georreferenciado por km (régua horizontal, sem eixo de tempo);
   Tempo×Caminho é avanço de obra por frente de serviço (eixo X = km,
   eixo Y = tempo; linhas diagonais = velocidade de avanço). Rotular
   explicitamente qual é qual; nunca representar retigráfico com linhas
   diagonais nem Tempo×Caminho com régua estática.
3. **Tabelas** — zebra em tom Manta (terracota ~4,5% / vinho ~4%),
   nunca cinza neutro. Mantém a regra "quadros e tabelas, nunca cards"
   do `padrao-manta`.
4. **Texto** — bullets curtos em vez de parágrafo corrido (relatórios
   SCL/AACE/MBB/FIDIC e elementos técnicos); `<b>` apenas no dado que
   carrega a conclusão (número, prazo, metodologia, responsável);
   quebrar frases com mais de ~15 palavras.
5. **Apresentações** — cards que simulam slide (McKinsey/BCG/Bain/
   Deloitte) usam tópicos curtos, não blocos de texto.
6. **Excel mock** — ribbon/nome do `.xlsx`, barra de fórmulas (célula
   ativa + `fx`), cabeçalho congelado (`border-bottom: 2px solid
   var(--maroon)`), abas de etapa (`xltabs`) quando o modelo é passo a
   passo (aba ativa na cor de acento do bloco).
7. **Grade × Abas** — quando o artefato compara mais de 6 exemplos,
   oferecer as duas visões (grade agrupada por seção com banda colorida
   / abas verticais + sub-abas horizontais + painel ampliado) a partir
   de uma ÚNICA fonte de dados JS (`const S = [...]`), nunca duplicando
   conteúdo. Botão de alternância `Grade`/`Abas` no topo; nunca remover
   uma visão sem confirmação explícita do usuário.
8. **Versionamento** — ajuste de estilo/cor pode substituir a versão
   atual quando o usuário pedir "mude"/"altere"/"corrija"; nova visão,
   novo bloco de conteúdo ou reestruturação de navegação gera nova
   versão do arquivo (`-v2`, `-v3`...), preservando a anterior.

Aplicar `manta-visual-dinamico` SEMPRE junto com `padrao-manta` em
artefatos para cliente ou uso institucional — `padrao-manta` define o
esqueleto obrigatório, `manta-visual-dinamico` refina cor, tabela,
texto e navegação por cima.

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

- **v4.3** (2026-08-30) — registro da skill transversal C1
  `manta-visual-dinamico` no mapa de skills do Maestro: degradê de cor
  por bloco (terracota→vinho), distinção Retigráfico × Tempo×Caminho,
  zebra de tabela em tom Manta, texto resumido com negrito nos
  destaques, mock de Excel realista e alternância grade/abas. Usar
  sempre em conjunto com `padrao-manta` em artefatos institucionais.
- **v4.2** (2026-07-05) — expansão S6–S10 (Portos, Aeroportos,
  Saneamento, Energia, Barragens). 5 novos agentes verticais + 5
  coleções RAG + 5 pastas SP. Ticket MNT-2026-UPGRADE-AGENTS-S6S10.
- **v4.1** (anterior) — 15 agentes: horizontais + S1–S4.
