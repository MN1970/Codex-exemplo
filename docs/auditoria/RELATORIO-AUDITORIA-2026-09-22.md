# Relatório da auditoria do Manta Maestro — 2026-09-22

Plano: `docs/PLANO-AUDITORIA-v1.md` (v1.1). Decisões de MN: D1 repositório
como fonte, D2 numeração do SharePoint, D3 Maestro primeiro, D4 autonomia por
risco (§7 do plano). PR: <https://github.com/MN1970/Codex-exemplo/pull/123>.

Escopo corrigido nesta rodada: repositório, SharePoint `Documentos/04_IA/Manta-Maestro`
(Drive A), biblioteca `04_IA` (Drive B) e o projeto Supabase `manta-maestro`.
As bibliotecas `01_BIBLIOTECA`, `02_CLIENTE`, `03_APOIO` e `ABDIB` foram só
auditadas — a correção delas é a 2ª rodada.

Toda exclusão no SharePoint foi para a **lixeira** (recuperável). Nenhuma
operação irreversível foi feita no Supabase (a migração tem bloco de reversão).

---

## 1. Resumo

| Onda | Resultado |
|---|---|
| W0 Segurança | ✅ O `.env` guardado no SP só tinha placeholders (nada para rotacionar) e foi para a lixeira. Varredura de segredos no repo: limpa. **Mas ver achado P-21** (dado comercial em branches públicas — não é "segredo" para o scanner). |
| W1 Lastro (E9) | ✅ 18 documentos receberam aviso de lastro no topo (ver §3). Nenhum conteúdo apagado. |
| W2 Fonte de verdade | ⏸️ **Suspensa.** O repositório é **público**; importar a árvore canônica publicaria tabela de preços, dados bancários, contatos e nomes de clientes. Precisa de decisão de MN (ver §6). Feito só o que não expõe conteúdo: avisos `_DEPRECATED.md` no Drive B, `sharepoint/README.md` reescrito, espelho parcial de 3 arquivos sanitizados. |
| W3 Numeração + CI | ✅ Numeração D2 aplicada em ~76 arquivos do repo (agentes, espelho, scripts, registry, testes). Router de referência determinístico (`src/maestro/keyword_router.py`) no lugar dos mocks dos testes E2E. Lint de Markdown e `pytest` corrigidos. |
| W4 03-exemplares | ✅ Conteúdo movido para `06-exemplares/`; 9 subpastas vazias para a lixeira; `_DEPRECATED.md`; A1-proposta v3.3.10, template PRT v1.0.1 e `INDICE-CANONICAL.md` v1.2 atualizados. |
| W5 Duplicatas (Drive B) | ✅ 5 cadernos SICRO duplicados (hash idêntico, ~7,8 MB) removidos de `MANUAL DE CUSTO/`; a cópia organizada em `CADERNO DE APLICAÇÃO/` ficou. `tt_sk/xer-msp-toolkit` × `09_TESTE_SKILLS/cronograma-toolkit` **não são duplicatas** (ver §4). |
| W6 Duplicatas (repo) | ✅ Os "checklists/summaries duplicados" de P-19 são documentos de assuntos diferentes com nomes parecidos — mantidos. Logs versionados (`audit.log`, `divergence_fix.log`) saíram do git e foram para o `.gitignore`. |
| W7 Espelhos | ✅ `_DEPRECATED.md` em `04_IA/Manta-Maestro/` e `04_IA/01-agentes-fundamentais/`; `04_IA/02-agentes-horizontais/` (9 pastas vazias) para a lixeira. |
| W8 Supabase | ✅ RLS em `manta_artefatos`; 13 views passaram a `security_invoker`; `search_path` fixo em `r2j_un_norm`; `manta_agent_capabilities` renumerada para D2 (com tabela de auditoria); change requests pendentes fechados. Migração: `supabase/migrations/2026_09_22_auditoria_w8_seguranca_renumeracao.sql`. |

---

## 2. Achado novo — P-21 🔴 dado comercial em repositório público

O repositório `MN1970/Codex-exemplo` é **público**. Duas branches criadas por
sessões anteriores já publicam dados que não deveriam estar fora do SharePoint:
dados bancários da empresa, telefone de um profissional nomeado e a tabela
tarifária completa. As branches e commits foram informados a MN diretamente,
fora do repositório, para não servirem de indicação aqui.

Nesta auditoria o mesmo conteúdo chegou a ser espelhado na branch do PR #123
(skill A1-proposta completa) e, junto, um snapshot da árvore do SP com a lista
de pastas de clientes. **Os dois arquivos foram retirados do histórico dessa
branch** (reescrita + force-push na própria branch da auditoria) antes de
qualquer merge; o snapshot foi preservado em `_correcoes/` no SharePoint.
Commits órfãos continuam acessíveis por SHA no GitHub até coleta de lixo.

**Ação recomendada (MN):** tornar o repositório privado, ou apagar as duas
branches acima (ou reescrevê-las sem os arquivos). Remoção definitiva de commits
já publicados exige pedido ao suporte do GitHub.

---

## 3. Matriz de lastro real (E9)

Legenda: ✅ real · 🟡 real mas descrito errado · 📐 proposta, não implementada · ❌ sem lastro.

Evidência consultada no Supabase `manta-maestro` em 2026-09-22: nenhuma edge
function publicada; `manta_rag_ml_models`, `manta_rag_ml_predictions`,
`manta_rag_ml_training_runs`, `maestro_cost_log`, `manta_api_calls` e
`manta_rag_feedback` com **0 linhas**; `manta_trace` 20 linhas,
`manta_agent_messages` 4, `agent_episodes` 5, `manta_rag_queries` 1.

| Componente | Classe | Evidência |
|---|---|---|
| Base RAG no Supabase (`rag_collections`, `manta_rag_documents`/`_chunks`, `maestro_routing_keywords`, `sp_agent_routing`) | ✅ | Tabelas com dados: coleções 11, docs 126, chunks 316, keywords 61, routing 9 (contagem exata) |
| Bases de custo e projeto rodoviário (`pk_*`, `r2j_*`) | ✅ | Dezenas de milhares de linhas |
| Estrutura de agentes em `SKILL.md` no SP (S1–S14, A1–A11, F1–F10, D01–D22) | ✅ | `INDICE-CANONICAL.md` v1.2 |
| Router de routing por palavra-chave | 🟡 → ✅ | Os testes E2E exercitavam um mock dentro do próprio teste; agora usam `src/maestro/keyword_router.py` |
| "20/21 agentes Manta NN em produção" | ❌ | Sem evidência de execução; `DEPLOYMENT-REPORT-v5-0-PRODUCTION.md`, `MAESTRO-OPERACIONAL-v5.0.md` |
| Maestro OS v6.0 (orquestrador, consensus, ML inference) | 📐 | Código em `src/maestro/`, sem implantação; tabelas de ML vazias |
| APScheduler / background agents | 📐 | Código em `scripts/`; agendamento real registrado é `cron` Linux (`docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`) |
| Docker/K8s, DR com RTO/RPO | 📐 | A imagem Docker compila no CI; não há evidência de implantação |
| Go-live S6 Portos (2026-07-25) | 📐 | Sem evidência de ter ocorrido; numeração anterior à D2 |
| Custo por usuário (`v_top_users`, `maestro_cost_log`) | 📐 | View existe, tabela vazia |

Documentos marcados com aviso no topo: `DEPLOYMENT-REPORT-v5-0-PRODUCTION.md`,
`MAESTRO-OPERACIONAL-v5.0.md`, `PRODUCTION-DEPLOYMENT.md`, `QUICKSTART-v6.md`,
`docs/MAESTRO-OS-v6-API.md`, `docs/MAESTRO-OS-v6-DEVELOPER.md`,
`docs/MAESTRO-OS-v6.0-WORKFLOW-DSL.md`, `APSCHEDULER_IMPLEMENTATION.md`,
`APSCHEDULER_DEPLOYMENT_GUIDE.md`, `DEPLOYMENT_BACKGROUND_TASKS.md`,
`BACKGROUND_AGENTS_INTEGRATION.md`, `S6-GO-LIVE-CHECKLIST.md`,
`S6-GO-LIVE-RUNBOOK.md`, `S6-LAUNCH-INDEX.md`, `S6-ROLLBACK-PLAN.md`,
`IMPLEMENTATION_SUMMARY_E2E_v5.0.md`, `docs/EXECUTIVE-SUMMARY-v5-UPGRADE.md`,
`docs/MANTA-MAESTRO-ECOSYSTEM-v5-UPGRADE.md`.

---

## 4. Matriz de duplicatas

| Item | Onde | Verificação | Ação |
|---|---|---|---|
| 5 cadernos de aplicação SICRO (V04–V08) | `04_IA/07_ORÇAMENTO - BASES/SICRO/CADERNO DE APLICAÇÃO/` × `…/MANUAL DE CUSTO/` | `quickXorHash` idêntico nos 5 pares; nenhuma referência no RAG nem no repo | Cópia de `MANUAL DE CUSTO/` → lixeira |
| Toolkit XER/MSP | `04_IA/tt_sk/xer-msp-toolkit/` × `04_IA/09_TESTE_SKILLS/cronograma-toolkit/` | `SKILL.md` com tamanhos diferentes (6.218 × 8.163 B); o segundo tem 1 referência a mais | **Não é duplicata** (P-08 corrigido); pastas de teste ficam para a 2ª rodada (P-11) |
| `03-exemplares/<domínio>/` × `06-exemplares/` | Drive A | Conteúdo movido; 9 pastas vazias | Pastas → lixeira + `_DEPRECATED.md` |
| `02-agentes-horizontais/` (9 pastas) | Drive B | Todas vazias | Pasta → lixeira |
| `Manta-Maestro/`, `01-agentes-fundamentais/` | Drive B | Cópias antigas; conteúdo exclusivo já migrado em 2026-09-07 | `_DEPRECATED.md`; conteúdo mantido até revisão humana |
| Checklists/summaries com nome parecido | raiz do repo | Assuntos diferentes (v5.0, Maestro OS v6, sp_healthcheck, expert finder) | Mantidos |
| `audit.log`, `divergence_fix.log` | raiz do repo | Saída de script versionada | Fora do git + `.gitignore` |
| `12_03_2026_TA_Regulamento` (3 cópias) | `04_IA/11_FINEP…` | Não verificado | 2ª rodada |
| Pastas espelhadas entre bibliotecas (P-09) | `03_APOIO`, `02_CLIENTE`, `Documentos` | Fora do escopo D3 | 2ª rodada |

---

## 5. O que ficou pendente

- **W2 completa** — depende da decisão sobre P-21 (§6).
- **Routines pausadas durante a auditoria — continuam pausadas.** O prompt de
  uma Routine só pode ser alterado a partir da conversa em que ela posta, então
  não foi possível atualizá-los daqui.
  - Rodada noturna (`trig_01CMJ41Dd1FmaMjL4ry2aXGq`): o prompt atual manda
    tratar a numeração S6–S13 e a fonte `_C`/`_D` como decisões em aberto —
    ambas já decididas (D2; `_C`) — e não conhece a regra de repositório
    público. Atualizar na conversa dela antes de reativar.
  - Sync GitHub ↔ SharePoint (`trig_01KPNtXg2TJJaNYhHoetrB3D`): o sentido
    SharePoint → GitHub pode copiar conteúdo confidencial para o repositório
    público (P-21). Reativar só depois da decisão §6.1.
- Campo legado `manta_code` nos `SKILL.md` de S12–S14 (colide com o código de
  outro segmento) — sinalizado no índice, não corrigido na fonte.
- Keywords/escopo dos itens "a confirmar" do índice (S12–S14, A11, D21–D22, F9–F10).
- Aposentadoria completa da biblioteca `04_IA` solta (revisão humana).
- 2ª rodada: `01_BIBLIOTECA`, `02_CLIENTE`, `03_APOIO`, `ABDIB`, conteúdo
  pessoal/de teste (P-11), nomenclatura de `02_CLIENTE` (P-13), retenção de
  backups (P-14).
- Suítes `tests/test_maestro_v6_*` com 12 falhas antigas, não cobertas por
  nenhum job de CI.

---

## 6. Decisões pedidas a MN

1. **P-21 / D1:** tornar o repositório privado? Se sim, a W2 segue como planejada
   (repo canônico, espelho completo). Se não, o modelo passa a ser "canônico
   dividido": arquivos sanitizados com edição no repo, arquivos com dado
   comercial ou de cliente com edição só no SP.
2. Apagar ou reescrever as duas branches do achado P-21.
3. Routine de sync: reativar só no sentido repo → SP (para os arquivos
   espelhados), reativar nos dois sentidos com filtro de conteúdo, ou desligar.
