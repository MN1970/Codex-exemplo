# Deploy runbook — Manta Maestro v4.3 (Leitor Documental)

Ticket: **MNT-2026-LEITOR-DOCUMENTAL**
Data: 2026-09-14
Autor: bootstrap via PR `claude/pdf-excel-dwg-reader-galg55`

Este runbook cobre o que precisa ser feito **fora dos repos git** para
concluir a v4.3 — introdução do **agente-leitor-documental (Manta 08)**,
a camada de ingestão multi-formato (PDF, Excel, DWG/DXF, Word, PPTX,
BIM, cronograma) que fica entre a origem do arquivo e os agentes
verticais S1-S10.

Segue o mesmo formato do runbook da v4.2
(`docs/DEPLOY-v4.2.md`) — cada item indica se pode ser feito por
automação disponível hoje ou exige ação humana.

---

## 0. Por que este agente antes de mais nada

Este PR é um **draft de arquitetura** (rascunho), não uma implementação
operacional. Ele:

- Formaliza um pipeline que hoje é implícito (cada vertical chama
  skills de formato por conta própria).
- Não cria nenhuma skill de leitura nova — reaproveita `pdf`, `xlsx`,
  `docx`, `pptx`, `autodesk-toolkit`, `cronograma-toolkit` e os
  extratores especializados já existentes no catálogo.
- Só adiciona a camada de **detecção + normalização + roteamento** que
  faltava entre a origem do arquivo e o agente vertical.

Antes de promover a **Operacional**, decidir com MN:
1. Se o dispatch por formato deve morar em banco (`doc_format_dispatch`,
   como candidatado aqui) ou só no `SKILL.md` (parsing pelo Maestro).
2. Se este agente roda como um passo automático do Maestro (sempre
   antes do vertical) ou só quando invocado explicitamente.

---

## 1. Merge do PR (gate humano MN)

- [ ] Revisar `MN1970/Codex-exemplo` — branch `claude/pdf-excel-dwg-reader-galg55`.
- [ ] Approve + merge (draft → ready → merged).

Não seguir para os próximos passos até o merge estar no branch
principal do repo.

---

## 2. Supabase — índice de controle + tabela de despacho

**Arquivo pronto:** `supabase/migrations/2026_09_14_v4_3_leitor_documental.sql`
(neste PR).

### 2.1. Pré-checagem

- Confirmar que `sp_agent_routing` já existe (criada na migração v4.2).
- As duas tabelas novas (`doc_processing_index`, `doc_format_dispatch`)
  são criadas do zero por este script — não dependem de schema prévio
  além de `sp_agent_routing`.

### 2.2. Execução

```bash
cd <repo-operacional-manta-maestro>
cp .../supabase/migrations/2026_09_14_v4_3_leitor_documental.sql \
   supabase/migrations/
supabase db push --dry-run     # ver o que vai mudar
supabase db push                # aplicar
```

Ou via MCP Supabase (`apply_migration`) após confirmar o projeto certo
com `list_organizations` + `list_projects` — não fiz automaticamente
porque alterar schema de produção sem confirmação explícita não é
apropriado.

### 2.3. Verificação pós-deploy

```sql
SELECT extensao, subtipo, skill_alvo, prioridade
FROM doc_format_dispatch
ORDER BY extensao, prioridade DESC;

SELECT agent_slug, sp_folder, priority
FROM sp_agent_routing
WHERE agent_slug = 'agente-leitor-documental';
```

Esperado: 18 linhas na primeira consulta, 1 linha na segunda.

---

## 3. SharePoint — pasta do agente

**Site canônico**: `https://mnassociados.sharepoint.com/sites/Engenharia`
**Library**: `Documentos Compartilhados`

- [ ] Criar `04_IA/Manta-Maestro/01-agentes-fundamentais/agente-leitor-documental/`.
- [ ] Upload de `SKILL.md`, `README.md`, `refs/`, `prompts/` (mirror
  já versionado em `sharepoint/01-agentes-fundamentais/agente-leitor-documental/`
  neste repo).

Este agente **não** ganha uma pasta em `03_Projetos/*` própria — ele
observa as pastas já existentes dos verticais S1-S10.

---

## 4. Atualizar `ARQUITETURA-AGENTES-IA.md` no SP

- [ ] Bump de versão v2.0.0 → **v2.1.0**.
- [ ] Adicionar o Manta 08 (leitor-documental) na tabela do Eixo 1 e
  no diagrama de fluxo (passo 0, antes do agente vertical assumir).
- [ ] Referenciar a tabela de despacho por formato da seção 3 do
  `SKILL.md`.

---

## 5. Testes de dispatch (equivalente aos testes de routing da v4.2)

Não há arquivo de teste específico ainda (diferente de
`tests/routing/prompts.md`, que testa routing por **segmento**). Antes
de promover a Operacional:

- [ ] Rodar um arquivo de cada formato suportado (PDF genérico, edital,
  edital ANEEL, EVTEA, XLSX, DOCX, DWG, XER) e confirmar que:
  1. cai na skill certa (tabela `doc_format_dispatch`),
  2. produz o JSON canônico completo (seção 4 do `SKILL.md`),
  3. o `hash` evita reprocessamento em uma segunda chamada com o mesmo
     arquivo.
- [ ] Registrar os resultados como um novo arquivo
  `tests/dispatch/formatos.md` (a criar em PR futuro, seguindo o
  padrão de `tests/routing/prompts.md`).

---

## 6. Rollback

1. **Git**: reverter o merge (`git revert -m 1 <merge-sha>`).
2. **Supabase**: rodar o bloco `ROLLBACK` comentado no fim do
   `2026_09_14_v4_3_leitor_documental.sql`.
3. **SharePoint**: renomear a pasta criada para `*_DEPRECATED` (não
   deletar imediatamente).

---

## Estado atual (por seção)

- [x] Definição canônica do agente (`.claude/agents/agente-leitor-documental.md`).
- [x] SKILL.md + mirror SharePoint versionados neste repo.
- [x] Migração Supabase candidata escrita (`.sql` neste PR).
- [ ] Merge do PR pelo MN.
- [ ] Aplicação da migração Supabase.
- [ ] Criação manual da pasta SP do agente.
- [ ] Atualização do `ARQUITETURA-AGENTES-IA.md` (v2.0.0 → v2.1.0).
- [ ] Testes de dispatch por formato.
- [ ] Decisão MN: dispatch em banco vs. só Markdown; execução automática
  vs. invocação explícita.
