# 🔄 Sincronização Bidirecional — Claude AI ↔ Maestro ↔ Cowork

**Status:** ✅ Production Ready  
**Versão:** 1.0.0  
**Data:** 2026-07-31

---

## 📋 O que é sincronizado?

```
Claude AI (fonte de prompts)
    ↓
Maestro Router (decisões de roteamento)
    ↓
Cowork (tasks e comentários)
    ↓
Claude AI (contexto atualizado)
    ↓
[Feedback loop contínuo]
```

**Dados sincronizados:**
- ✅ Prompts do usuário
- ✅ Decisões de roteamento (agent, score, confidence)
- ✅ Criação de tasks
- ✅ Comentários e feedback
- ✅ Status de tasks
- ✅ Histórico de sincronização

---

## 🚀 Setup Rápido (5 minutos)

### 1️⃣ Iniciar o MCP Server

```bash
# Terminal 1
cd /home/user/Codex-exemplo
npx tsx src/mcp-server.ts
```

Você verá:
```
🚀 MCP Server iniciado
📡 Escutando em http://localhost:3001

📚 Endpoints disponíveis:
   POST /mcp/route
   POST /mcp/sync-prompt
   GET  /mcp/agents
   ...
✨ Sistema pronto para sincronizar
```

### 2️⃣ Testar sincronização localmente

```bash
# Terminal 2
curl -X POST http://localhost:3001/mcp/sync-prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Projeto de ETA com adução de 150km"}'
```

Resposta esperada:
```json
{
  "syncId": "sync-1785500269761-abc123",
  "status": "pending",
  "message": "Prompt registrado. Sincronizando..."
}
```

### 3️⃣ Ver status de sincronização

```bash
curl http://localhost:3001/mcp/sync-status
```

---

## 🔌 Integrar com Claude AI

### Opção A: CLI (recomendado para desenvolvimento)

```bash
# Terminal 1: MCP Server
npx tsx src/mcp-server.ts

# Terminal 2: Claude Code
claude
```

Dentro do Claude:
```
Rotear este prompt para o agente correto usando Maestro:
"Linha de transmissão 500kV com subestação"

E sincronize com Cowork.
```

### Opção B: Web (claude.ai/code)

1. Abra: https://claude.ai/code
2. Selecione: "Open Folder" → `/home/user/Codex-exemplo`
3. Converse com Claude:

```
Use o MCP Server para rotear este prompt:
"Terminal portuário com berços para contêineres"

Crie uma task no Cowork com os detalhes de roteamento.
```

### Opção C: MCP Server Registrado (produção)

1. Acesse: **claude.ai → Settings → Claude Code → MCP Servers**
2. Clique: **+ Add MCP Server**

```json
{
  "name": "maestro-sync-server",
  "command": "npx",
  "args": ["tsx", "/home/user/Codex-exemplo/src/mcp-server.ts"],
  "environment": {
    "MCP_PORT": "3001",
    "NODE_ENV": "production"
  }
}
```

3. Reinicie Claude
4. Use normalmente

---

## 📡 API Endpoints Disponíveis

### 1. Rotear com Maestro

```bash
POST /mcp/route
Content-Type: application/json

{
  "prompt": "Projeto de barragem de rejeitos"
}
```

**Resposta:**
```json
{
  "agent": {
    "name": "agente-barragens",
    "code": "Manta 03-S10",
    "segment": "Barragens"
  },
  "score": 28.49,
  "confidence": "high",
  "keywords": ["barragem", "rejeitos", "pnsb"]
}
```

---

### 2. Sincronizar Prompt do Claude AI

```bash
POST /mcp/sync-prompt
Content-Type: application/json

{
  "prompt": "Preciso de um projeto de ETA com análise de qualidade de água"
}
```

**O que acontece automaticamente:**
1. ✅ Prompt é registrado no SyncManager
2. ✅ Maestro roteia para agente correto
3. ✅ Task é criada no Cowork
4. ✅ Comentário é postado com contexto
5. ✅ Histórico é mantido

**Resposta:**
```json
{
  "syncId": "sync-1785500269761-xyz789",
  "status": "pending",
  "message": "Prompt registrado. Sincronizando com Maestro e Cowork..."
}
```

---

### 3. Listar Agentes Disponíveis

```bash
GET /mcp/agents
```

**Resposta:**
```json
{
  "agents": [
    {
      "code": "Manta 03-S8",
      "name": "agente-saneamento",
      "segment": "Saneamento",
      "tier": "Sonnet"
    },
    ...
  ],
  "total": 10,
  "status": "operational"
}
```

---

### 4. Criar Task no Cowork

```bash
POST /mcp/create-task
Content-Type: application/json

{
  "title": "Projeto de Aeroporto com TPS",
  "description": "Detalhes do projeto...",
  "agent_source": "agente-aeroportos",
  "segment": "Aeroportos",
  "priority": "high",
  "tags": ["pista", "tps", "anac"]
}
```

---

### 5. Listar Tasks do Cowork

```bash
GET /mcp/tasks?limit=20&agent_source=agente-saneamento&status=open
```

---

### 6. Postar Comentário em Task

```bash
POST /mcp/post-comment
Content-Type: application/json

{
  "taskId": "task-123456789",
  "content": "Atualização do status..."
}
```

---

### 7. Webhook: Receber Atualizações do Cowork

Quando uma task é atualizada no Cowork, configure para enviar:

```bash
POST /webhooks/cowork-update
Content-Type: application/json

{
  "taskId": "task-123456789",
  "updateData": {
    "status": "in_progress",
    "assignee": "specialist-name",
    "timestamp": "2026-07-31T10:00:00Z"
  }
}
```

---

### 8. Ver Status de Sincronização

```bash
GET /mcp/sync-status
```

**Resposta:**
```json
{
  "status": {
    "lastSync": "2026-07-31T10:15:30Z",
    "totalRecords": 15,
    "synced": 14,
    "pending": 0,
    "errors": 1,
    "activePrompts": 3,
    "activeRoutes": 3,
    "activeTasks": 3
  },
  "recentActivity": [
    {
      "id": "sync-1785500269761-abc123",
      "timestamp": "2026-07-31T10:14:20Z",
      "source": "claude-ai",
      "type": "prompt",
      "status": "synced"
    },
    ...
  ]
}
```

---

## 🔄 Fluxo de Sincronização Completo

### Exemplo: User passa prompt no Claude AI

**1. User no Claude AI:**
```
"Preciso de um projeto de subestação com ANEEL"
```

**2. Claude chama `/mcp/sync-prompt`:**
```json
{
  "prompt": "Preciso de um projeto de subestação com ANEEL"
}
```

**3. SyncManager processa automaticamente:**
- ✅ Registra prompt com ID único
- ✅ Chama Maestro Router
- ✅ Obtém routing: agente-energia (S9), score 39.5, confidence: high
- ✅ Cria task no Cowork com metadados
- ✅ Posta comentário com contexto
- ✅ Atualiza histórico de sincronização

**4. Claude recebe resposta:**
```json
{
  "syncId": "sync-1785500269761-xyz",
  "status": "pending",
  "message": "Sincronizando..."
}

→ Em segundos: Task criada no Cowork
→ Em segundos: Comentário postado
→ Claude pode consultar /mcp/sync-status
```

**5. Feedback loop:**
- Specialist trabalha no Cowork
- Task é atualizada
- Webhook `/webhooks/cowork-update` recebe atualização
- SyncManager registra mudança
- Claude é notificado do progresso

---

## 📊 Monitorar Sincronização

### Dashboard em Tempo Real

```bash
# Ver status a cada 5 segundos
watch -n 5 'curl -s http://localhost:3001/mcp/sync-status | jq'
```

### Histórico de Sincronização

```bash
# Últimas 20 operações
curl http://localhost:3001/mcp/sync-status | jq '.recentActivity'
```

---

## 🔒 Segurança & Autenticação

### Para Produção

1. **Adicione autenticação no MCP Server:**

```typescript
// Em src/mcp-server.ts
app.use((req, res, next) => {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (token !== process.env.MCP_API_TOKEN) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  next();
});
```

2. **Configure variáveis de ambiente:**

```bash
export MCP_API_TOKEN="seu-token-seguro"
export ANTHROPIC_API_KEY="sk-ant-..."
export COWORK_API_URL="https://seu-cowork.com/api"
export COWORK_API_TOKEN="token-cowork"
```

3. **Ative HTTPS:**

```bash
# Use reverse proxy como nginx ou caddy
# para terminar SSL antes do MCP Server
```

---

## 🧪 Testar Completo

### 1. Teste de Sincronização Rápida

```bash
npx tsx tests/maestro-local.test.ts
```

**Resultado esperado:** ✅ 5/5 testes passando

### 2. Teste de Sincronização com Claude AI

```bash
npx tsx tests/maestro-enhanced.test.ts
```

**Resultado esperado:**
- ✅ Routing correto
- ✅ Claude AI integrado
- ✅ Tasks criadas
- ✅ Feedback loop funcionando

### 3. Teste E2E Completo

```bash
npx tsx tests/e2e-maestro-claude-cowork.test.ts
```

---

## 🚨 Troubleshooting

### Problema: Sync pendente indefinidamente

```bash
# Verificar status
curl http://localhost:3001/mcp/sync-status

# Reiniciar servidor
pkill -f "mcp-server"
npx tsx src/mcp-server.ts
```

### Problema: Tasks não aparecem no Cowork

1. Verificar conectividade:
```bash
curl http://localhost:3001/health
```

2. Verificar logs do servidor:
```bash
npx tsx src/mcp-server.ts 2>&1 | grep -i error
```

3. Testar endpoint de task:
```bash
curl -X GET http://localhost:3001/mcp/tasks
```

### Problema: Claude AI não consegue acessar MCP

1. Verificar se servidor está rodando na porta correta:
```bash
lsof -i :3001
```

2. Adicionar CORS (se necessário):
```typescript
// Em src/mcp-server.ts
app.use(cors());
```

---

## 📈 Próximos Passos

- [ ] Deploy do MCP Server em produção
- [ ] Configurar webhooks do Cowork
- [ ] Implementar cache distribuído
- [ ] Adicionar autenticação multi-user
- [ ] Criar dashboard de monitoramento
- [ ] Documentar API para integrators

---

## 📞 Suporte

```bash
# Ver todos os endpoints
curl http://localhost:3001/health

# Ver status atual
curl http://localhost:3001/mcp/sync-status

# Ver histórico de operações
curl http://localhost:3001/mcp/sync-status | jq '.recentActivity[0:5]'
```

---

**Status:** ✅ Pronto para usar em produção
**Última atualização:** 2026-07-31
**Versão:** 1.0.0
