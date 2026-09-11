# Planejamento Manta Maestro — Conhecimentos por Agente/Segmento/Disciplina

**Status:** plano de conhecimento, pendente de revisão e gate humano
(MN) antes de qualquer escrita na fonte real de produção (SharePoint).
**Data:** 2026-09-11. **Método:** 5 agentes de pesquisa em paralelo,
grounded em (a) leitura ao vivo do `INDICE-CANONICAL.md` real via MCP
`SharePoint_Manta`, (b) leitura ao vivo do `SKILL.md` real de
D03-Geotecnia como template de qualidade, e (c) pesquisa web para
verificar normas/órgãos citados antes de qualquer citação (nenhum
número de norma foi inventado — onde não verificável, o texto diz
"a confirmar" em vez de uma citação fabricada).

Este documento existe porque a pergunta "que conhecimentos os agentes
da Manta precisam ter para os projetos da Manta?" não tinha uma
resposta única — precisa ser respondida em 3 camadas: (1) o estado real
atual do sistema, (2) o que falta formalizar nas lacunas já conhecidas,
e (3) o que cada agente operacional precisa saber para ser útil de
verdade. As 3 camadas estão aqui.

---

## 1. Estado real atual (ground truth, verificado ao vivo em 2026-09-11)

O Manta Maestro real (SharePoint, `09-base-conhecimento/
INDICE-CANONICAL.md`, v1.1, 2026-09-07) organiza conhecimento em **4
eixos ortogonais**, não 3:

| Eixo | Códigos | Total | Confirmados | "A confirmar" |
|---|---|---|---|---|
| **S — Segmentos** | S1–S14 | 14 | 11 (S1–S11) | 3 (S12-Túneis, S13-Mineração, S14-Óleo e Gás) |
| **A — Atividades** | A1–A11 | 11 | 10 (A1–A10) | 1 (A11-Fiscalização) |
| **F — Funcionais** | F1–F10 | 10 | 8 (F1–F8) | 2 (F9-Meta, F10-Pesquisa Evolutiva) |
| **D — Disciplinas** | D01–D22 | 22 | 20 (D01–D20) | 2 (D21-Topografia/Geodésia, D22-Túneis) |

"A confirmar" significa: a pasta existe fisicamente na árvore
SharePoint, mas o conteúdo/keywords não foram auditados/escritos ainda
— não significa "não existe". Isso já corrige uma leitura anterior
deste repositório (`CLAUDE.md`, seção "Eixo S", nota de 2026-09-07), que
tratava Óleo & Gás e Mineração como "sem correspondência confirmada,
índice canônico vai só até S11" — **o índice real (v1.1) já vai até
S14 e nomeia os três segmentos explicitamente** (S12-Túneis,
S13-Mineração, S14-Óleo e Gás). Ver detalhe em `CLAUDE.md` → "GAPS
ABERTOS", entrada atualizada nesta mesma leva de mudanças.

**21 agentes operacionais** consomem esses eixos hoje (12 horizontais +
9 verticais operacionais, incl. Manta 20-ESG) — ver `CLAUDE.md` →
"Mapa completo de agentes" para a lista exata e status de cada um.

---

## 2. O que foi produzido nesta leva — fechando as lacunas "a confirmar"

Para cada item marcado "a confirmar" no eixo real, foi produzido um
brief de conhecimento no mesmo formato e nível de precisão técnica do
`SKILL.md` real de D03-Geotecnia (v2.0.0) — normas verificadas por
pesquisa web antes de citar, métodos/fórmulas padrão, mapa de
segmentos/disciplinas relacionados, handoffs, e o que o item
explicitamente NÃO faz. Todos marcados `status: DRAFT` — nenhum foi
escrito na fonte real (SharePoint) nesta sessão.

| Item | Arquivo | Resumo em 1 linha |
|---|---|---|
| **S12 — Túneis** | `docs/S12-TUNEIS-SKILL.md` | Segmento próprio para obras subterrâneas (NATM/TBM/cut-and-cover), consumindo D03 (geotecnia) e D22 (método construtivo); relacionado a S1/S2/S4/S11. |
| **S13 — Mineração** | `docs/S13-MINERACAO-SKILL.md` | Lavra, beneficiamento e logística de minério — deliberadamente **não duplica** barragem de rejeitos (isso fica com S11). Normas ANM, NR-22, Código de Mineração. |
| **S14 — Óleo e Gás** | `docs/S14-OLEOGAS-SKILL.md` | Dutos, terminais, midstream/downstream — ANP (RTDT, SGSO), NR-37, API 5L/1104/6D, ASME B31.4/B31.8. |
| **D21 — Topografia e Geodésia** | `docs/D21-TOPOGRAFIA-GEODESIA-SKILL.md` | Georreferenciamento, SIRGAS2000, NBR 13133:2021, NTGIR/SIGEF — alimenta principalmente S1 e S3. |
| **D22 — Túneis (disciplina)** | `docs/D22-TUNEIS-SKILL.md` | Método construtivo e dimensionamento de suporte (RMR/Q/GSI, convergência-confinamento) — consome D03, alimenta S12/S1/S2/S4. |
| **A11 — Fiscalização** | `docs/A11-F9-F10-ESCOPO-PROPOSTO.md` | Verificação de campo (diário de obra, medições, FVS) → conformidade; alimenta A6 (contratual) e A7 (claims). |
| **F9 — Meta** | (mesmo arquivo acima) | Proposta: governança interna do próprio Maestro (registro de agentes/skills, versionamento) — hipótese, não confirmada contra `99-meta/agente-projeto-claude/` real. |
| **F10 — Pesquisa Evolutiva** | (mesmo arquivo acima) | Proposta: watch contínuo de normas/mercado, alimentando A9 e os verticais — não confirma a existência de um "Daily Evolution Engine" real, só documenta a hipótese. |

**Geotecnia (D03)** não entrou nesta lista porque **já existe e já é
madura** em produção — ver `docs/D03-GEOTECNIA-APLICACAO-PROJETOS-MANTA.md`
para o guia prático de aplicação e o único gap real encontrado (S12
ainda não listado como segmento-cliente de D03).

---

## 3. Matriz de conhecimento por agente operacional

Documento completo: `docs/MATRIZ-CONHECIMENTO-POR-AGENTE.md` — cobre os
21+1 agentes (12 horizontais + 10 verticais, incl. Manta 20-ESG e
agente-edificacoes/agente-oleo-gas hoje sem segmento real confirmado),
cada um com: missão no contexto Manta, conhecimento técnico essencial,
fontes de atualização contínua, e gap de maturidade atual.

**Síntese dos 3 maiores gaps de maturidade identificados** (detalhe no
documento):

1. **S9-Saneamento (prioridade AySA)** — dupla exposição regulatória:
   o marco brasileiro mudou recentemente (Lei 14.026/2020) e seu
   próprio sistema de indicadores foi descontinuado no meio do caminho
   (SNIS encerrado em 2023, substituído por SINISA em 2024), enquanto a
   prioridade AySA/Argentina exige um corpo regulatório totalmente
   separado, ainda não segregado do arcabouço brasileiro na descrição
   do agente.
2. **S11-Barragens** — normas de barragem de rejeitos da ANM estão em
   revisão ativa e recorrente (resoluções pós-eventos de ruptura) —
   maior risco reputacional: uma citação desatualizada aqui é
   perigosa.
3. **S8-Aeroportos** — precisa acompanhar duas camadas normativas em
   paralelo com defasagem natural entre elas: emendas ao ICAO Annex 14
   e sua tradução/atualização correspondente na série RBAC da ANAC.

---

## 4. Prioridades recomendadas (o que fazer primeiro, se aprovado por MN)

1. **Confirmar ou descartar S12/S13/S14 e D21/D22 contra a fonte real**
   — os briefs desta leva são propostas informadas por pesquisa
   externa, não uma leitura do que já existe no SharePoint (as pastas
   estão vazias). Antes de publicar, um humano com contexto de negócio
   deve confirmar se a Manta realmente atua/pretende atuar em
   Mineração e Óleo & Gás como segmentos formais — isso é uma decisão
   de negócio, não técnica.
2. **D03 → adicionar S12 como segmento-cliente**, assim que S12 for
   formalizado — edição pequena e de baixo risco na fonte real (ver
   seção 4 de `docs/D03-GEOTECNIA-APLICACAO-PROJETOS-MANTA.md`).
3. **A11-Fiscalização** — parece o item de maior valor prático imediato
   entre os "a confirmar": Manta já participa de contratos de obra
   pública onde fiscalização/medição é rotina; formalizar essa
   atividade tem retorno direto, ao contrário de F9/F10 que são
   internos ao próprio sistema Maestro.
4. **F9/F10** — menor urgência; são propostas especulativas (o
   documento é explícito sobre isso) até que alguém com acesso à pasta
   `99-meta/agente-projeto-claude/` real confirme ou refute a hipótese
   de sobreposição.
5. **Matriz de conhecimento por agente** — usar como checklist de
   revisão contínua (ex.: quando a Lei 14.026 ou uma resolução ANM
   mudar, o gap já está sinalizado em qual agente precisa de
   atualização).

---

## 5. O que este plano explicitamente não faz

- Não escreve nada na fonte real do SharePoint — todo conteúdo novo
  vive só neste repositório, como proposta.
- Não corrige a renumeração de segmento pendente em
  `.claude/agents/*.md` (frontmatter ainda em S6-S10 onde o real é
  S7-S11) — esse é um trabalho mecânico à parte, já rastreado em
  `CLAUDE.md` → "GAPS ABERTOS" como pendência de uma fase futura, e
  fora do escopo deste plano de conhecimento.
- Não decide se Mineração e Óleo & Gás devem virar segmentos reais da
  Manta — isso é decisão de negócio (MN), não uma conclusão técnica
  deste documento.

---

*Construído com 5 agentes de pesquisa em paralelo nesta sessão. Cada
arquivo citado acima documenta suas próprias fontes verificadas e o que
ficou marcado "a confirmar" — ver cada arquivo individualmente antes de
qualquer uso formal (proposta, laudo, claim).*
