# Deploy runbook — Manta Maestro v4.2

Ticket: **MNT-2026-UPGRADE-AGENTS-S6S10**
Data: 2026-07-05
Autor: bootstrap via PR `claude/manta-agents-s6-s10-7qklcw`

Este runbook cobre o que precisa ser feito **fora dos repos git** para
concluir a v4.2 (Portos, Aeroportos, Saneamento, Energia, Barragens).

Cada item indica se pode ser executado por automação disponível hoje
ou se exige ação humana.

---

## 1. Merge dos PRs (gate humano MN)

- [ ] Revisar `MN1970/Codex-exemplo#1` — registro mestre.
- [ ] Revisar `viniciusmagnos/manta-hub#3` — mirror dos agentes verticais.
- [ ] Approve + merge (draft → ready → merged).

Não seguir para os próximos passos até ambos merges estarem no `main`.

---

## 2. Supabase — coleções RAG + routing rules

**Arquivo pronto:** `supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql`
(neste PR).

### 2.1. Pré-checagem

Antes de rodar, confirmar que o schema tem:
- Tabela `rag_collections` (ou equivalente) com colunas `slug`, `name`,
  `storage_prefix`, `initial_sources JSONB`.
- Tabela `sp_agent_routing` com colunas `agent_slug`, `sp_folder`,
  `file_patterns TEXT[]`, `priority`.
- Tabela `maestro_routing_keywords` (opcional — só se o Maestro
  carregar keywords do DB e não parseando o CLAUDE.md).

Se o schema real diverge, ajustar o `.sql` antes de rodar. Todo o
arquivo é envolvido em `BEGIN…COMMIT`, então divergências fazem tudo
reverter.

### 2.2. Execução

Duas opções:

**A) Via CLI Supabase** (recomendado):
```bash
cd <repo-operacional-manta-maestro>
cp .../supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql \
   supabase/migrations/
supabase db push --dry-run     # ver o que vai mudar
supabase db push                # aplicar
```

**B) Direto via psql**:
```bash
psql "$SUPABASE_DB_URL" \
  -f supabase/migrations/2026_07_05_v4_2_agents_s6_s10.sql
```

**C) Via MCP Supabase (automação futura)**: as chamadas
`apply_migration` do Supabase MCP podem executar o mesmo SQL após
`list_organizations` + `list_projects` para escolher o projeto certo.
Não fiz automaticamente porque acessar produção sem confirmação
explícita não é apropriado.

### 2.3. Verificação pós-deploy

```sql
SELECT slug, storage_prefix, jsonb_array_length(initial_sources) AS sources
FROM rag_collections
WHERE slug IN ('saneamento','energia','portos','aeroportos','barragens')
ORDER BY slug;

SELECT agent_slug, sp_folder, priority
FROM sp_agent_routing
WHERE agent_slug LIKE 'agente-%'
  AND agent_slug NOT IN (
    'agente-infraestrutura','agente-claims','agente-contratual',
    'agente-imobiliario','agente-orcamento','agente-modelagem',
    'agente-cronograma','agente-bd','agente-apresentacoes',
    'agente-advisory','agente-arquiteto-ia','maestro'
  );
```

Esperado: 5 linhas em cada consulta.

---

## 3. SharePoint — pastas dos agentes + pastas de projeto

**Site canônico**: `https://mnassociados.sharepoint.com/sites/Engenharia`
**Library**: `Documentos Compartilhados`

O MCP Microsoft 365 disponível hoje é **read-only** — não expõe tool
de criação de pasta / upload. As duas séries abaixo precisam ser
criadas manualmente (ou via Graph API por script dedicado).

### 3.1. Pastas dos agentes (para SKILL.md, guias, refs)

Criar em `Documentos Compartilhados/04_IA/Manta-Maestro/01-agentes-fundamentais/`:

- [ ] `agente-portos/`
- [ ] `agente-aeroportos/`
- [ ] `agente-saneamento/`
- [ ] `agente-energia/`
- [ ] `agente-barragens/`

Padrão inicial de cada pasta (copiar de qualquer agente existente,
p. ex. `agente-modelagem/`):
- `SKILL.md`
- `README.md`
- `refs/` (documentos técnicos de referência)
- `prompts/` (prompts de exemplo)

### 3.2. Pastas de projeto (para os arquivos DWG/PDF/XLSX)

O routing rule `sp_agent_routing` aponta para
`03_Projetos/<Segmento>/*`. Confirmar em qual site esse root vive —
provavelmente também `sites/Engenharia/Documentos Compartilhados/`:

- [ ] `03_Projetos/Saneamento/`
- [ ] `03_Projetos/Energia/`
- [ ] `03_Projetos/Portos/`
- [ ] `03_Projetos/Aeroportos/`
- [ ] `03_Projetos/Barragens/`

Se o naming convention `03_Projetos` for outra coisa (o folder search
não encontrou nada com esse nome exato), atualizar
`sp_agent_routing.sp_folder` na migração Supabase antes de rodar.

### 3.3. Upload dos SKILL.md

- [ ] Escrever os 5 `SKILL.md` seguindo o template dos agentes
  existentes. Basear no conteúdo do `.claude/agents/*.md` deste repo
  como esqueleto (contexto, ordem canônica, handoffs, delimitação).
- [ ] Fazer upload para as pastas criadas no 3.1.

---

## 4. Atualizar `ARQUITETURA-AGENTES-IA.md` no SP

**Localização**: procurar no site `sites/Engenharia` — o folder
`04_IA/Manta-Maestro/` provavelmente contém a versão atual (v1.0.0).

- [ ] Bump de versão v1.0.0 → **v2.0.0**.
- [ ] Adicionar seções para S6–S10 (Portos, Aeroportos, Saneamento,
  Energia, Barragens) — pode reaproveitar diretamente o material do
  `CLAUDE.md` deste PR + os agent `.md`.
- [ ] Atualizar o diagrama de routing do Maestro para incluir as 5
  novas branches.

---

## 5. Testes de routing

**Arquivo pronto:** `tests/routing/prompts.md` (neste PR).

- [ ] Rodar cada prompt do arquivo no ambiente do Maestro
  (`https://hub.mantaassociados.com/askcad` ou o entrypoint que o time
  usa para o router).
- [ ] Anotar em qual agente cada prompt caiu.
- [ ] Considerar aprovado se ≥ 90% dos prompts primários caírem no
  agente esperado.
- [ ] Registrar decisões sobre os "casos ambíguos" (UHE = barragem OU
  energia, ETE + subestação, etc.) diretamente no `CLAUDE.md` ou num
  ADR separado.

Casos que falharem: iterar nas keywords do
`maestro_routing_keywords` (ajustar prioridades).

---

## 6. Rollback

Se algo der errado após o deploy dos PRs + Supabase migration:

1. **Git**: reverter os merges (`git revert -m 1 <merge-sha>`) nos dois
   repos.
2. **Supabase**: rodar o bloco `ROLLBACK` comentado no fim do
   `2026_07_05_v4_2_agents_s6_s10.sql` — ele remove exatamente as
   linhas inseridas.
3. **SharePoint**: renomear as pastas criadas para `*_DEPRECATED` (não
   deletar imediatamente — pode haver conteúdo já colocado por
   usuários).

---

## Estado atual (por seção)

- [x] Registro mestre versionado (`Codex-exemplo` PR #1).
- [x] `.claude/agents/*.md` versionados (mirror em `manta-hub` PR #3).
- [x] Migração Supabase candidata escrita (`.sql` neste PR).
- [x] Prompts de teste de routing escritos (`.md` neste PR).
- [x] SP site canônico identificado.
- [ ] Merge dos PRs pelo MN.
- [ ] Aplicação da migração Supabase.
- [ ] Criação manual das 10 pastas SP (5 agentes + 5 projetos).
- [ ] Escrita e upload dos 5 SKILL.md.
- [ ] Atualização do `ARQUITETURA-AGENTES-IA.md` (v1.0.0 → v2.0.0).
- [ ] Execução dos testes de routing.
