# Plano de Auditoria — Sistema Manta Maestro (repo + SharePoint + Supabase)

**Versão:** v1.1 · **Data:** 2026-09-22 · **Solicitante:** MN
**Status:** 📋 PLANO — decisões D1–D4 tomadas por MN em 2026-09-22
(seção 7). **D1 aguarda reconfirmação** à luz do achado P-16 (seção 7).
Nenhuma correção executada; a próxima etapa é a Fase 0.

Este plano foi montado a partir de um **reconhecimento somente-leitura**
feito em 2026-09-22:

- inventário das 6 bibliotecas do site SharePoint `Engenharia`;
- leitura de `README.md`, `PENDENTE-SHAREPOINT.md` e da auditoria de
  duplicações de 2026-07-11 no canonical SP;
- listagem dos projetos Supabase;
- leitura da `main` deste repositório (v5.4.7, 1.616 arquivos),
  incluindo as auditorias anteriores `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`
  e `docs/SUPABASE-PROJECT-AUDIT.md`.

Os achados preliminares da seção 3 vieram desses dados, cada um com a
evidência que o originou (R2: nada inventado).

> **v1.1:** a v1.0 foi escrita sobre um clone local desatualizado
> (38 arquivos, `CLAUDE.md` v4.2.3). Esta versão refaz os achados sobre
> o repo contra a `main` real e incorpora as auditorias anteriores.

---

## 1. Objetivo e escopo

Auditar o sistema de agentes IA da Manta em quatro superfícies, gerar um
relatório de achados priorizado e, após aprovação, aplicar correções:

| # | Superfície | O que entra |
| --- | --- | --- |
| S-A | **Repositório** `mn1970/codex-exemplo` (`main`, v5.4.7) | 1.616 arquivos: `CLAUDE.md`, `.claude/agents/` (25), `infra/agent-registry/` (1.198), `docs/`, `sharepoint/` (mirror), `supabase/migrations/`, `migrations/`, `db/`, `src/`, `tests/`, `.github/workflows/` (3), arquivos avulsos na raiz |
| S-B | **SharePoint** `sites/Engenharia` | 6 bibliotecas: `Documentos` (canonical Drive A), `04_IA` (Drive B), `01_BIBLIOTECA`, `02_CLIENTE`, `03_APOIO`, `ABDIB` |
| S-C | **Supabase** | 4 projetos (`manta-maestro` ativo; `manta-tocantins`, `manta-rodovias`, `manta-portal-piloto` inativos) |
| S-D | **Integrações** | Routine de sync GitHub↔SharePoint `trig_01KPNtXg2TJJaNYhHoetrB3D`, `Sync-MantaMaestro.ps1`, OneDrive sync, MCP `sharepoint-write`, mirror local do Drive B, backups em `13_BACKUPS` |

**Fora do escopo:** mérito técnico dos entregáveis de cliente em
`02_CLIENTE/*` (lá só entram estrutura, nomes e duplicações) e o
repositório operacional do Maestro, que não está nesta sessão.

**Trabalho anterior que esta auditoria continua, sem refazer:**

| Documento | Onde | O que já resolveu | O que deixou aberto |
| --- | --- | --- | --- |
| Auditoria de duplicações v2×v3 (2026-07-11) | SP `_correcoes/` | Fases 1–2 (placas `_DEPRECATED.md`) | Fase 3 (`03-exemplares` → `06-exemplares`) |
| `GAP-RECONCILIACAO-SHAREPOINT-REAL.md` (2026-09-07/10) | repo `docs/` | Numeração S (no `CLAUDE.md`), embedder | Modelo "20 agentes Manta NN" × estrutura real; alegações sem lastro; risco de edição concorrente |
| `SUPABASE-PROJECT-AUDIT.md` (G012, 2026-07-31) | repo `docs/` | Diagnóstico do projeto `xgluoaa…` inacessível | Action items da seção 7 dele |
| `PENDENTE-SHAREPOINT.md` (2026-07-11) | SP `00-arquitetura/` | — | 10 pendências v3.2 |

---

## 2. Regras de execução (valem para todas as fases)

1. **Leitura antes de escrita.** As fases 1–3 são 100% somente-leitura.
2. **Reler antes de editar.** O SP é editado por várias sessões e
   processos ao mesmo tempo, e isso já causou perda de trabalho real
   (ver `GAP-RECONCILIACAO-SHAREPOINT-REAL.md`, "Risco de edição
   concorrente"). Toda escrita é precedida de releitura do alvo, e toda
   escrita é verificada por leitura depois.
3. **Nada é apagado sem aprovação explícita de MN**, item a item ou por
   lote aprovado. Exclusões vão para a lixeira do SP (recuperável).
4. **Mover > apagar.** A duplicata vai para `99-backup/` ou recebe uma
   placa `_DEPRECATED.md` apontando para o canonical, antes de qualquer
   exclusão.
5. **Snapshot antes de cada onda de correção** (Fase 0).
6. **Rastreabilidade (R5).** Todo achado cita caminho e evidência; toda
   correção é registrada em log (`_correcoes/AAAA-MM-DD-*.md` no SP e
   histórico do `CLAUDE.md` no repo).
7. **Citação de "documento real" só vale após confirmação no SP.** É a
   lição das citações fabricadas corrigidas em A1-proposta v3.3.7/v3.3.9.
8. **Sanitização R1.** Nenhum nome de empresa ou profissional em arquivo
   canonical; segredos nunca copiados para relatórios.

---

## 3. Achados preliminares do reconhecimento (a confirmar na Fase 2)

Severidade: 🔴 crítico · 🟠 alto · 🟡 médio · ⚪ baixo

| ID | Sev. | Achado | Evidência |
| --- | --- | --- | --- |
| P-01 | 🔴 | **Três "fontes de verdade" concorrentes** para o Maestro: o repo (`CLAUDE.md` v5.4.7), o SP Drive A `Documentos/04_IA/Manta-Maestro/` (cujo README se declara "único canonical", v5.0) e o SP Drive B, biblioteca `04_IA/Manta-Maestro/` (declarado deprecated, mas ainda com conteúdo). | README do canonical SP; árvore da biblioteca `04_IA` |
| P-16 | 🔴 | **Parte do repo pode não ter lastro real.** A auditoria anterior (`GAP-RECONCILIACAO-SHAREPOINT-REAL.md`) concluiu, como hipótese mais provável, "núcleo real + camada de embelezamento fictício": ML routing/XGBoost, consensus voting, DR RTO/RPO, Docker/K8s e "Maestro OS v6.0" sem evidência no SP. Recomendou marcar tudo isso como "proposta futura, não implementada". Documentos na raiz como `DEPLOYMENT-REPORT-v5-0-PRODUCTION.md` ("✅ Live") continuam afirmando produção. | `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` §"O que isso pode significar" e §"Recomendação" |
| P-02 | 🟠 | **Numeração antiga ainda espalhada.** O `CLAUDE.md` já adota S6 Edificações · S7 Portos · S8 Aeroportos · S9 Saneamento · S10 Energia · S11 Barragens (igual ao SP), mas mais de 20 ocorrências de "S6 = Portos" / "S10 = Barragens" sobrevivem em agentes (`agente-esg`, `agente-oleo-gas`, `agente-procurement-p3-08`, `manta-25-kg`), em `.claude/procurement/`, em `MAESTRO-OPERACIONAL-v5.0.md`, `DEPLOYMENT-REPORT-v5-0-PRODUCTION.md`, `AGENT_MEMORY_DELIVERY_SUMMARY.txt`, `EMBEDDING_AB_TEST_README.md`, `S6-GO-LIVE-*` e `.github/DEPLOYMENT-APPROVALS.md`. Também há o campo legado `manta_code` que colide entre segmentos (já registrado no `CLAUDE.md` v5.4.7). | `git grep` na `main` |
| P-03 | 🟠 | **Versões de arquitetura convivendo sem vigente clara.** No SP, `00-arquitetura/` tem 43 arquivos: `ARQUITETURA-AGENTES-IA` v5.0.0, v5.1.0 e v6.1.0; `CLAUDE.md-v5.0/v5.1/v6.1-CONSOLIDATED`; `manta-maestro-arquitetura` v2 a v5.0; `SKILL-MANTA-MAESTRO` v1.1.0 a v6.1.0. No repo, `docs/ARQUITETURA-v5.0.md`, `ARCHITECTURE.md`, `sharepoint/ARQUITETURA-AGENTES-IA-v5.0.0.md` e `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`. | árvores SP e repo |
| P-20 | 🟠 | **CI vermelho na `main`.** No commit `3753de6` falham `Router E2E` (16 de 40; acurácia 79,4% < 81%), `Cross-Agent Flows`, `Test Summary`, `Build Docker Image` e `Notify Slack`, o que já estava registrado no #117. Os casos de routing esperam `manta-03-s8` / `san:` para Saneamento, ou seja, fixtures e código de routing ainda seguem a numeração antiga (liga com P-02). Sem CI verde, nenhuma correção das ondas pode ser validada. | runs `35095731584` (main) e `35782102636` (PR #123) |
| P-04 | 🟠 | **O mirror do repo aponta para um path que não existe no canonical.** `sharepoint/README.md` manda publicar em `Documentos/04_IA/Manta-Maestro/01-agentes-fundamentais/`, mas o canonical usa `01-segmentos/S7-portos/…`. Os SKILL.md foram parar no **Drive B** (`04_IA/01-agentes-fundamentais/`) como stubs de 0,6–1,5 KB, com cópias `SKILL-<seg>.md` duplicadas na pasta pai. | `sharepoint/README.md`; árvore `04_IA` |
| P-05 | 🟠 | **A auditoria de duplicações de 2026-07-11 ficou pela metade.** `03-exemplares/bd/manta_propostas_index.json` e `03-exemplares/imobiliario/` continuam no slot v2; `06-exemplares/_indices/` só tem README; três skills ativas ainda apontam para o path v2. | `_correcoes/2026-07-11-auditoria-duplicacoes.md`; árvore canonical |
| P-06 | 🟠 | **Arquivo `.env` guardado no SharePoint**, em `06-infraestrutura/mcp-servers/sharepoint-write/`. Tem o mesmo tamanho do `.env.example` (296 B), então provavelmente é uma cópia sem segredo, mas **precisa ser verificado** (sem copiar valores). Se houver credencial: rotacionar e remover. | árvore canonical |
| P-17 | 🟠 | **Vários processos escrevem no SP ao mesmo tempo**: a Routine diária GitHub↔SP (`trig_01KPNtXg2TJJaNYhHoetrB3D`), `Sync-MantaMaestro.ps1` na máquina local, o OneDrive sync e as sessões de agente. Qualquer limpeza pode ser desfeita no ciclo seguinte se esses escritores não forem mapeados e alinhados antes. | `GAP-RECONCILIACAO-SHAREPOINT-REAL.md`; `06-infraestrutura/scripts/` |
| P-07 | 🟠 | **O Drive B (biblioteca `04_IA`) acumula resíduo do Maestro:** `Manta-Maestro/` (16 arquivos de arquitetura duplicados do canonical), `MANTA_MAESTRO_v4.3/` (arquivo de 21 B, que também existe como `MANTA_MAESTRO_v4.3.md` na raiz do repo), `Manta-Maestro-v4.2-KB-Evoluido/`, `02-agentes-horizontais/` (9 pastas vazias) e `Fase 4 - Git Evolution Suite/`. | árvore `04_IA` |
| P-19 | 🟡 | **Duplicação e resíduo dentro do próprio repo:** `DEPLOY-CHECKLIST.md`, `DEPLOYMENT-CHECKLIST.md`, `PRE-DEPLOYMENT-CHECKLIST.md` e `docs/DEPLOY-CHECKLIST-v5.0.md`; `IMPLEMENTATION-SUMMARY.md` e `IMPLEMENTATION_SUMMARY.md`; migrações em `migrations/`, `supabase/migrations/` e `db/`; logs versionados (`audit.log`, `divergence_fix.log`); cerca de 45 arquivos avulsos na raiz. | `git ls-tree` da `main` |
| P-08 | 🟡 | **Duplicatas exatas (mesmo nome e tamanho) no Drive B:** 5 cadernos SICRO repetidos entre `SICRO/CADERNO DE APLICAÇÃO` e `SICRO/MANUAL DE CUSTO` (~7,8 MB); o toolkit XER/MSP repetido entre `09_TESTE_SKILLS/cronograma-toolkit` e `tt_sk/xer-msp-toolkit`; `12_03_2026_TA_Regulamento` em 3 cópias (FINEP). | análise nome+tamanho, 751 arquivos |
| P-09 | 🟡 | **Pastas espelhadas entre bibliotecas:** `03_Projetos` (`Documentos` e `03_APOIO`); `04_IA` (biblioteca, pasta em `Documentos`, `01_BIBLIOTECA/03_IA` e `03_APOIO/04_IA_PROPOSTA` vazia); SICRO (`Documentos/Sicro`, `02_CLIENTE/00_SICRO`, `04_IA/07_ORÇAMENTO - BASES/SICRO`); ABDIB (biblioteca e `02_CLIENTE/46_ABDIB` vazia); `03_Metodologias Construtivas` (`03_APOIO` e `04_IA/02_IMAGENS`); `EGTC` × `EGTC2`. | listagem das bibliotecas |
| P-10 | 🟡 | **Checklists de deploy divergentes do estado real:** há itens pendentes que podem já estar feitos (por exemplo, `04-routing-migration-v4.2/` com `sp_agent_routing_config.json` existe no SP) e itens que ficaram obsoletos (upload para `01-agentes-fundamentais/`). | checklists do repo × SP |
| P-11 | 🟡 | **Conteúdo pessoal e de teste em bibliotecas de trabalho:** `05_STHEPHANY/` (fotos de aniversário, backup), `Teste_Vinicius/`, `09_TESTE_SKILLS/`, `tt_sk/`, `02_CLIENTE/TESTE_LIVE ARTIFACTS`. | árvores `04_IA`, `02_CLIENTE` |
| P-12 | 🟡 | **Conflito com a regra R1 no repo:** o `CLAUDE.md` cita cliente/projeto pelo nome ("AySA", "State Grid"). O item 10 do `PENDENTE-SHAREPOINT.md` pede que isso vá para o CLAUDE.md do projeto. | `CLAUDE.md`; `PENDENTE-SHAREPOINT.md` |
| P-13 | ⚪ | **Nomenclatura inconsistente em `02_CLIENTE`:** `35 - ECORODOVIAS` foge do padrão `NN_NOME`; há lacunas de numeração (05, 36, 42) e pastas de cliente vazias (04, 07, 09, 13, 14, 46, 47). | listagem `02_CLIENTE` |
| P-14 | ⚪ | **Backups em `13_BACKUPS`:** dumps diários `.age` (21 por app) sem política de retenção visível. Falta verificar se a retenção e a restauração estão testadas. | árvore `04_IA` |
| P-15 | ⚪ | **Supabase:** há 3 projetos inativos e os action items de G012 estão em aberto. Falta confirmar quais migrações (`supabase/migrations/`, 15 arquivos) foram realmente aplicadas no `manta-maestro` e com qual numeração de segmento. | `list_projects`; `SUPABASE-PROJECT-AUDIT.md` |

**Números do reconhecimento:**

- biblioteca `04_IA`: 240 pastas, 751 arquivos, 1,31 GB;
- `Documentos/04_IA`: 420 pastas, 645 arquivos, 3,9 MB;
- busca por "SKILL": 320 itens em 3 bibliotecas;
- repo `main`: 1.616 arquivos.

---

## 4. Fases da auditoria

### Fase 0 — Preparação e preservação (≈30 min · sem escrita em produção)

- [x] Gate MN: plano e decisões D1–D4 (seção 7), em 2026-09-22.
- [ ] Reconfirmação de D1 à luz de P-16 (seção 7).
- [ ] Congelar as escritas no Maestro durante a auditoria: avisar a
      equipe e **pausar a Routine `trig_01KPNtXg2TJJaNYhHoetrB3D`**.
- [ ] Snapshot: exportar a árvore completa das 6 bibliotecas (JSON) para
      `99-backup/snapshot-2026-09-XX-pre-auditoria/` e criar uma tag git
      no repo.
- [ ] Confirmar os conectores ativos: `SharePoint_Manta` (leitura e
      escrita) e `Supabase` (`manta-maestro`).

### Fase 1 — Inventário completo (≈1–2 h · somente leitura)

- [ ] Árvore completa das 6 bibliotecas, com tamanho e data de modificação.
- [ ] Índice de todos os `SKILL*.md`, `CLAUDE*.md` e `ARQUITETURA*.md`
      (SP e repo), com a versão declarada no cabeçalho.
- [ ] Inventário Supabase do `manta-maestro`: tabelas, contagem de
      `rag_chunks` por coleção, conteúdo de `sp_agent_routing`,
      migrações aplicadas, advisors de segurança e performance.
- [ ] Inventário do repo: classificar os 1.616 arquivos por área e por
      tipo (spec, código, teste, relatório, log).
- [ ] Rodar localmente os testes do repo (`pytest -m unit`, lint) para
      saber o estado de partida.

### Fase 2 — Auditoria por eixo (≈4–6 h · somente leitura)

| Eixo | Pergunta que responde | Método |
| --- | --- | --- |
| **E1 Fonte de verdade** | Onde mora o canonical de cada artefato? | Matriz artefato × {repo, Drive A, Drive B}; confirmar P-01, P-04 e P-07 |
| **E2 Versionamento** | Qual versão está vigente e quais são histórico? | Ler os cabeçalhos de versão; montar a linha do tempo v2 → v6.1 no SP e no repo; confirmar P-02 e P-03 |
| **E3 Duplicações** | O que está duplicado, onde, e qual cópia fica? | (a) nome+tamanho; (b) hash de conteúdo nos candidatos; (c) nome normalizado (acentos, "(1)", "v2", "copia"); (d) pastas espelhadas entre bibliotecas; (e) duplicatas internas do repo (P-19). Excluir falsos positivos: variações de imagem gerada por IA e dumps de backup |
| **E4 Skills & routing** | Cada agente ou skill tem SKILL.md íntegro, routing correto e nome sem conflito? | Cruzar o registry do `CLAUDE.md` × `.claude/agents/` × `01-segmentos/`, `02-atividades/` × skills instaladas; checar stubs, `_DEPRECATED`, referências quebradas (grep por paths v2) e colisões de `manta_code` |
| **E5 Supabase** | O RAG e o routing refletem a arquitetura vigente? | Comparar coleções e routing com a numeração canonical; migrações aplicadas × arquivos do repo; projetos inativos; action items de G012 |
| **E6 Segurança & conformidade** | Há segredo exposto, dado pessoal ou violação da R1? | `.env` (P-06); `.env.example` e `.mcp.json` do repo; secret scanning no repo; pastas pessoais (P-11); nomes de cliente em arquivos canonical (P-12); permissões de compartilhamento das bibliotecas |
| **E7 Higiene estrutural** | A organização é navegável e consistente? | Nomenclatura, pastas vazias, pastas de teste, zips de portais, retenção de backups (P-13, P-14), arquivos avulsos na raiz do repo (P-19) |
| **E8 Integrações** | Alguma sincronização pode reintroduzir o que for limpo? | Mapear **todos os escritores** do SP (P-17): Routine `trig_01KPNtXg2TJJaNYhHoetrB3D`, `Sync-MantaMaestro.ps1`, OneDrive, MCP `sharepoint-write`, mirror local do Drive B |
| **E9 Lastro real** | Cada alegação de "operacional/produção" do repo tem evidência? | Para cada componente que o repo declara em produção (agentes Manta NN, ML routing, APScheduler, Docker/K8s, Maestro OS v6, deploy reports), buscar evidência no SP, no Supabase ou em execução real. Classificar como ✅ real · 🟡 real mas descrito errado · 📐 proposta não implementada · ❌ sem lastro. Continua a recomendação §2(e) do `GAP-RECONCILIACAO-SHAREPOINT-REAL.md` |

### Fase 3 — Relatório de achados (≈1 h)

Entregável: `_correcoes/2026-09-XX-auditoria-sistema-v1.md` no SP, com
cópia em `docs/` no repo, contendo:

- a tabela de achados (ID, severidade, evidência, correção proposta,
  risco, esforço, se é reversível);
- a **matriz de duplicatas**, com decisão por item: MANTER · MOVER para o
  canonical · DEPRECATE (placa) · ARQUIVAR em `99-backup` · EXCLUIR
  (lixeira);
- a **matriz de lastro (E9)**, com a classificação de cada componente;
- a lista de referências cruzadas que bloqueiam cada movimentação.

### Fase 4 — Gate humano MN

MN revisa o relatório e aprova por **onda** (abaixo). Itens de risco
alto ou crítico exigem aprovação individual (D4).

### Fase 5 — Correções em ondas

| Onda | Conteúdo | Risco | Autonomia (D4) |
| --- | --- | --- | --- |
| **W0** Segurança | Verificar e remover o `.env` do SP; rotacionar a credencial, se houver | 🔴 | Item a item |
| **W1** Lastro | Aplicar a matriz E9 no repo: marcar como "📐 proposta, não implementada" o que não tem lastro; corrigir o que é real mas está descrito errado. **Pré-requisito de W2**: só vira canonical o que passar pelo E9 | 🔴 | Item a item; PRs por área |
| **W2** Fonte de verdade (D1 = repo) | (a) importar para o repo o que existe só no canonical SP `Documentos/04_IA/Manta-Maestro/` (≈645 arquivos, ≈3,9 MB), exceto `99-backup/` e segredos, reconciliando com o que o repo já tem; (b) trocar o README do SP ("único canonical") por "espelho publicado a partir do GitHub — não editar aqui"; (c) placa `_DEPRECATED.md` no Drive B `Manta-Maestro/`; (d) redirecionar os escritores de P-17 para o sentido único repo → SP; (e) reescrever `sharepoint/README.md` do repo com o path real | 🟠 | Item a item |
| **W3** Numeração & versões (D2) | Eliminar os resíduos de numeração antiga (P-02) no repo, incluindo o código de routing e as fixtures de teste (P-20), até o CI ficar verde; resolver `manta_code`; marcar a versão vigente de cada documento de arquitetura e mover as antigas para histórico, no repo e no SP | 🟠 | Item a item; PR no repo |
| **W4** Conclusão da auditoria 07-11 | Fase 3 dela: migrar `03-exemplares/` → `06-exemplares/` e atualizar as 3 referências ativas (A1-proposta `SKILL.md`, `template-prt-rodovias-v1.md`, `INDICE-CANONICAL.md`) | 🟠 | Item a item, com o mapa S.A.D aprovado |
| **W5** Duplicatas | P-08 (Drive B) e P-19 (repo): manter uma cópia; as demais vão para a lixeira ou para histórico | 🟡 | Por lote |
| **W6** Espelhos entre bibliotecas | P-09: somente as pastas ligadas ao Maestro nesta rodada (D3). As demais vão para a 2ª rodada | 🟡 | Por lote |
| **W7** Higiene | Mover pastas pessoais e de teste para área própria; corrigir nomenclatura e pastas vazias; definir a política de retenção de backups | ⚪ | Por lote |
| **W8** Supabase | Alinhar routing e coleções RAG à numeração canonical; fechar os action items de G012; decidir o destino dos projetos inativos | 🟠 | Item a item (as migrações vão direto para produção) |

### Fase 6 — Verificação e fechamento (≈30 min)

- [ ] Rodar de novo os detectores da Fase 2: só as placas
      `_DEPRECATED.md` podem aparecer como "duplicatas".
- [ ] Grep por paths v2 e pela numeração antiga fora do histórico.
- [ ] Testes do repo verdes (`agent-test.yml`) e routing do Maestro
      testado com os prompts atualizados.
- [ ] Atualizar `PENDENTE-SHAREPOINT.md`, `INDEX.md` e `README.md` no SP,
      e o `CLAUDE.md` (com histórico de versões) no repo.
- [ ] Reativar a Routine de sync já alinhada ao sentido repo → SP.
- [ ] Registrar em TRACE (R5).

---

## 5. Estimativa

| Bloco | Esforço |
| --- | --- |
| Fases 0–3 (auditoria, somente leitura) | ≈ 6–9 h de agente, em 1–2 sessões |
| Fase 4 (gate MN) | tempo humano |
| Fase 5 (W0–W8) | ≈ 6–12 h, dependendo do resultado do E9 e das decisões |
| Fase 6 | ≈ 30 min |

---

## 6. Entregáveis

1. Este plano (`docs/PLANO-AUDITORIA-v1.md`).
2. O relatório de achados, com a matriz de duplicatas e a matriz de
   lastro (Fase 3).
3. Log de correções por onda (`_correcoes/` no SP).
4. PRs no repo: lastro (W1), fonte de verdade/mirror (W2) e
   numeração/versões (W3).
5. `CLAUDE.md` atualizado com o histórico da auditoria.

---

## 7. Decisões de MN (tomadas em 2026-09-22)

| # | Decisão | Escolha de MN |
| --- | --- | --- |
| D1 | Qual é o canonical? | **Repositório GitHub `mn1970/codex-exemplo`.** O SharePoint passa a ser espelho publicado a partir do repo; o Drive B é drenado. ⚠️ Aguarda reconfirmação (ver abaixo) |
| D2 | Numeração de segmentos | **S7–S11 do SP** (S5 Imobiliário, S6 Edificações, S7 Portos, S8 Aeroportos, S9 Saneamento, S10 Energia, S11 Barragens). O `CLAUDE.md` já segue essa numeração; os resíduos são corrigidos (W3) |
| D3 | Escopo das correções | **Maestro primeiro:** repo, Drive A, Drive B e Supabase nesta 1ª rodada. `01_BIBLIOTECA`, `02_CLIENTE`, `03_APOIO` e `ABDIB` são auditadas agora e corrigidas numa 2ª rodada |
| D4 | Nível de autonomia | **Por risco:** ondas ⚪/🟡 aprovadas por lote; ondas 🟠/🔴 aprovadas item a item |

### Por que D1 precisa ser reconfirmada

D1 foi escolhida com base na v1.0 deste plano, que dizia que o repo
tinha 38 arquivos. A `main` real tem 1.616, e a auditoria anterior do
próprio repo recomenda o **oposto** de D1: tratar o SharePoint como o
sistema real e reduzir o repo a ele (P-16). Se o repo virar canonical
sem passar pelo E9, o conteúdo sem lastro seria **publicado no SP como
oficial**.

Duas saídas compatíveis com a escolha de MN:

- **D1-a (mantém a decisão, com salvaguarda):** o repo vira canonical,
  mas somente depois de W1 (lastro). Tudo o que for classificado como
  📐 ou ❌ fica marcado no repo e não é espelhado no SP como vigente.
  *Este é o plano como está escrito.*
- **D1-b (canonical por tipo de artefato):** skills, índices e runbooks
  operacionais continuam canonical no SP (que é onde as sessões e os
  processos os consomem hoje); o repo é canonical para código, testes,
  migrações e documentação de arquitetura.

### Implicações de D1-a (repo como canonical)

1. **Sentido único de sincronização: repo → SP.** Enquanto houver
   escrita direta no SP (P-17), o drift volta. W2 depende do mapa de
   escritores do E8.
2. **Congelamento do SP durante a importação**, entre o snapshot
   (Fase 0) e o merge do PR de importação.
3. **Ficam fora do repo:** segredos, binários grandes e `99-backup/`,
   que permanecem só no SP como arquivo. O `.gitignore` e o README do
   repo passam a dizer isso.
4. **Textos que dizem o contrário precisam ser atualizados:** o README
   do SP ("único canonical"), o `CLAUDE.md` do repo ("referência
   canônica versionada dos agentes verticais") e a recomendação do
   `GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.

---

*Plano elaborado a partir de reconhecimento somente-leitura em
2026-09-22. Nenhum arquivo foi movido, renomeado ou excluído.*
