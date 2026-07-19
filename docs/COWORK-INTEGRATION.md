# Manta Maestro em Cowork — Runbook de integração

**Fase B** do roadmap de acesso: depois que o **MCP tools do Maestro**
(Fase A) já expõem o registro dos 20 agentes + routing + catálogo RAG,
Cowork pode consumir o mesmo endpoint sem código novo — só configuração
por usuário/workspace.

Este documento cobre:
1. O que já está implementado (Fase A).
2. Como configurar Cowork para acessar.
3. Cobertura resultante e gaps.
4. Se e quando fazer um MCP dedicado ao Cowork.

---

## 1. Fase A já entregou

**Repositório**: `viniciusmagnos/manta-hub` (branch
`claude/manta-agents-s6-s10-7qklcw`).

**Arquivos**:
- `backends/mcp/app/maestro.py` — módulo com registro estático (20
  agentes v4.2), routing engine (keyword match ponderado) e 4 tools.
- `backends/mcp/app/server.py` — chama `register_maestro_tools(mcp)` no
  bootstrap.
- `tests/mcp/test_maestro.py` — 21 testes cobrindo registry, routing
  determinístico, RAG catalog.

**4 tools novas** disponíveis via `https://hub.mantaassociados.com/mcp`:

| Tool | Uso |
|---|---|
| `list_maestro_agents(axis?, status?)` | Inventário completo dos 20 agentes |
| `route_maestro_prompt(prompt, top_k=3)` | Simula o Manta 00 — retorna dispatch primário + alternativas com scores |
| `get_maestro_rag_collections()` | 9 coleções RAG (prefixos rod:/oae:/fer:/mtr:/por:/aer:/san:/ene:/bar:) |
| `get_maestro_agent_details(agent_slug)` | Metadados canônicos de 1 agente |

**Características**:
- Read-only, estáticas (não chamam backend, não requerem Bearer).
- Deterministas (routing é keyword match puro).
- Testadas (21 unit tests passando).
- Zero dependência nova (só bibliotecas do MCP existente).

## 2. Configurar Cowork

Cowork consome MCPs por dois caminhos:

### Caminho A — Custom Connector no Cowork (recomendado)

1. Cowork admin acessa `Settings → Connectors → Add Custom Connector`.
2. Preenche:
   - **Name**: `Manta Hub`
   - **URL**: `https://hub.mantaassociados.com/mcp`
   - **Auth**: OAuth 2.1 (fluxo automático — Cowork abre navegador para o
     usuário logar no `hub.mantaassociados.com`; refresh token rotation
     já implementado no auth backend).
3. Após consentimento, o Cowork guarda o access token no vault do
   workspace. As 4 tools do Maestro + 16 tools AskCAD/Balanço/Paisagismo
   ficam disponíveis para qualquer sessão do time.

### Caminho B — Via arquivo `.mcp.json` do repo

Para ambientes Cowork que suportam `.mcp.json` per-repo:

```json
{
  "mcpServers": {
    "manta-hub": {
      "url": "https://hub.mantaassociados.com/mcp",
      "transport": "http"
    }
  }
}
```

Commit isso no `manta-hub` ou em `Codex-exemplo`; ao clonar em Cowork, o
MCP é auto-configurado (o fluxo OAuth ainda roda uma vez por usuário).

### Verificação

Depois de logar, testar no chat do Cowork:

```
Use route_maestro_prompt with "AySA reabilitação da Planta Norte"
```

Esperado: retorno primário = `agente-saneamento` com score ≥ 220
(saneamento 100 + AySA 120).

## 3. Cobertura resultante

Após ativar, Cowork ganha em cobertura do Maestro:

| Camada | Antes (só `.claude/agents/`) | Depois (com MCP) |
|---|---|---|
| Definições dos 20 agentes | ✅ .claude/agents/*.md (5 verticais novos) | ✅ + `list_maestro_agents` (todos os 20) |
| Routing rules | ❌ | ✅ `route_maestro_prompt` (keyword match) |
| Catálogo RAG (prefixos) | ❌ | ✅ `get_maestro_rag_collections` |
| Metadados canônicos + SP path | ❌ | ✅ `get_maestro_agent_details` |
| Consulta vetorial ao RAG | ❌ | ⚠️ requer MCP Supabase separado |
| Full-text nos SKILL.md | ❌ | ⚠️ ainda em SP — precisa MCP M365 write |
| Iniciar conversa com agente vertical | ❌ | ✅ via `start_askcad_chat(persona_id=...)` — se a persona `agente-<slug>` estiver criada no AskCAD |

**Cobertura efetiva: ~70%** (subiu de 30% para 70% com só a Fase A).

Gaps remanescentes para chegar em 100%:
- Vetor semântico no RAG (precisa MCP do Supabase configurado com
  credencial).
- Sync automático `.claude/agents/*.md` ↔ SharePoint SKILL.md (hoje
  manual, MCP M365 disponível é read-only).
- Personas do AskCAD alinhadas aos 20 agentes (hoje AskCAD tem 5 seed
  personas — precisa clonar/adaptar para cobrir S6-S10).

## 4. MCP dedicado ao Cowork — quando fazer?

**Recomendação**: **não fazer agora**. Fase A + configuração descrita
acima cobre ~70% do uso real.

Um MCP dedicado ao Cowork (`cowork.mantaassociados.com/mcp`) só justifica
esforço se:

- **Diferenciação de tenant**: workspaces Cowork precisam ver dados
  restritos (por área, por cliente) — hoje o hub compartilha o mesmo
  `user_id` para todos. Só vale se houver política de RBAC do Cowork
  que ainda não existe.
- **Tools que só fazem sentido colaborativas**: ex.: `broadcast_to_team`,
  `assign_to_member`, `create_shared_notebook`. Nada disso é core do
  Maestro.
- **Latência regional**: hospedar o MCP mais próximo dos usuários
  Cowork. Só justifica se o time crescer >50 usuários em regiões
  distantes de São Paulo.

Enquanto nenhum desses três for real, **Cowork consome o MCP do hub**
via custom connector — é a arquitetura de menor manutenção.

## 5. Roadmap de evolução (opcional)

Se depois de rodar a Fase A em produção surgir demanda por Fase B
dedicada:

**Fase B.1** — Extensões operacionais no mesmo MCP:
- `start_agent_conversation(agent_slug, message)` — cria persona no
  AskCAD com system prompt = SKILL.md do agente + inicia chat.
- `search_agent_rag(agent_slug, query, top_k)` — proxy ao Supabase
  filtrado pelo prefixo do agente.
- `list_agent_projects(agent_slug)` — lista projetos SP na pasta do
  agente.

**Fase B.2** — MCP separado só se justificado:
- Novo backend `backends/cowork-mcp/` com tools específicas de
  colaboração + auth próprio.
- Deploy separado (`cowork.mantaassociados.com/mcp`).

**Fase B.3** — Sync automático `.claude/agents/` ↔ SharePoint:
- CI/CD que quando um PR no `Codex-exemplo` é mergeado, dispara Graph
  API para atualizar `SKILL.md` no SP.
- Requer Graph API write scope (M365 admin approval).

---

## Checklist Fase A → produção

- [x] `backends/mcp/app/maestro.py` escrito e commitado.
- [x] `backends/mcp/app/server.py` chama `register_maestro_tools`.
- [x] `tests/mcp/test_maestro.py` (21 testes) passando.
- [x] Update do `CLAUDE.md` do `manta-hub` com o catálogo de tools.
- [ ] Merge do PR `viniciusmagnos/manta-hub#3` (gate MN).
- [ ] Deploy do MCP na VPS (`deploy/deploy.sh` restart do
  `mcp-api.service`).
- [ ] Teste E2E: `curl` no `/mcp` do hub após deploy — verificar que
  `list_maestro_agents` responde 20 itens.
- [ ] Config custom connector no Cowork (Caminho A ou B da seção 2).
- [ ] Documentar no ARQUITETURA-AGENTES-IA.md v2.0.0 (seção nova
  "Acesso via MCP").
