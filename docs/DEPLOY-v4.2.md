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

### 2.4. Verificação real (2026-08-29 — projeto `manta-maestro`, `ogxxgvgtulrbbppshjie`)

**A migração já estava aplicada em produção.** Projeto Supabase estava
`INACTIVE` (pausado por inatividade); após `restore_project`, as
consultas de 2.3 rodaram direto contra o banco real:

- `rag_collections`: 10 no total (as 5 legado + as 5 novas + `orcamento`),
  todas com `storage_prefix`/contagem de fontes batendo com o `.sql`.
- `sp_agent_routing`: as 5 linhas esperadas, `priority=100`.
- `maestro_routing_keywords`: contagens batendo com o `.sql` (aeroportos 7,
  barragens 9, energia 8, portos 9, saneamento 8).

**Não é preciso reaplicar** — o `INSERT ... ON CONFLICT DO NOTHING` já
rodou (idempotente, mas redundante rodar de novo).

**Gap real encontrado, fora do escopo original deste runbook**: a
tabela `manta_rag_chunks` (292 chunks no total) tem quase nenhum
conteúdo indexado para os 5 segmentos novos — **aeroportos: 7 chunks,
saneamento: 5 chunks, portos/energia/barragens: 0 chunks**. Também tem
duas colunas de embedding — `embedding` (BAAI/bge-small-en-v1.5, 384d;
162/292 populado) e `embedding_m3` (BGE-M3 multilíngue; 0/292, coluna
ainda não usada — provável upgrade planejado para cobrir espanhol/AySA).
`manta_rag_ml_training_runs` existe mas tem 0 linhas (nenhum
treino/fine-tuning real já rodou) e `ultima_recuperacao` está nula em
todos os chunks (o RAG nunca serviu uma busca real em produção).

**Novo item de trabalho**: ingestão de conteúdo real (normas, editais,
casos) para popular `por:`, `ene:`, `bar:` — sem isso, os agentes
verticais desses 3 segmentos não têm nenhuma base RAG para consultar,
mesmo com toda a configuração (coleção, routing, keywords) já correta.

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

## 6. Extensão do registry `aluci-guard` (S6-S10)

**Arquivos prontos:** `docs/aluci-guard/registry-extension-{portos,
aeroportos,saneamento,energia,barragens}.md` + consolidação em
`docs/aluci-guard/README.md` (neste PR).

- [x] Extrair das 5 SKILL.md as referências normativas/legais citadas
  (57 no total: 15 compatíveis com o schema atual `normas_abnt.py`/
  `leis_federais.py`, 42 exigindo categoria nova — setorial/
  internacional).
- [ ] Gate MN: decidir nome/formato das categorias novas de registry
  (`normas_setoriais.py`, `normas_internacionais.py`, possível fatia
  argentina para saneamento/AySA).
- [ ] Confirmar onde vive o código-fonte real da skill `aluci-guard`
  (o ambiente atual só tem o `SKILL.md`, sem `auditor.py`/`registry/`)
  para abrir PR lá com as 57 entradas.
- [ ] Validar vigência real das 57 entradas antes de marcá-las
  `vigente` no registry de produção.

## 7. Rollback

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
- [x] Extração das referências normativas das 5 SKILL.md p/ aluci-guard
  (`docs/aluci-guard/`, neste PR) — 57 entradas aguardando gate MN.
- [x] Aplicação da migração Supabase — **confirmado direto no banco em
  2026-08-29** (ver §2.4); o runbook estava desatualizado, não é
  preciso rodar de novo.
- [x] Atualização do `ARQUITETURA-AGENTES-IA.md` (v1.0.0 → v2.0.0) —
  já está em v2.0.0 na cópia deste repo (`sharepoint/00-arquitetura/`);
  falta só o re-upload no SP real (bloqueado, ver abaixo).
- [ ] Merge dos PRs pelo MN.
- [ ] Ingestão de conteúdo real no RAG para portos/energia/barragens
  (hoje 0 chunks cada — ver §2.4). Prioridade sobre qualquer outro
  item de Supabase.
- [ ] Criação manual das 10 pastas SP (5 agentes + 5 projetos) —
  bloqueado: MCP M365 disponível é somente leitura.
- [ ] Upload dos 5 SKILL.md no SP — mesmo bloqueio de acesso.
- [ ] Execução dos testes de routing — bloqueado: endpoint real
  (`hub.mantaassociados.com/askcad`) não acessível neste ambiente.
