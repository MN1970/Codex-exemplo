# 🚀 Codex Hub — Instruções Completas para Executar no Claude AI

**Data:** 2026-07-31  
**Versão:** 1.0.0 Production Ready  
**Status:** ✅ Totalmente Testado e Operacional

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Setup Rápido (5 minutos)](#setup-rápido-5-minutos)
3. [Setup Completo (Claude AI Integrado)](#setup-completo-claude-ai-integrado)
4. [Teste de Conexão](#teste-de-conexão)
5. [Usar Maestro Router no Claude](#usar-maestro-router-no-claude)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Solução de Problemas](#solução-de-problemas)

---

## 🔧 Pré-requisitos

- **Node.js:** v22+ (verificar: `node --version`)
- **npm:** v9+ (verificar: `npm --version`)
- **Git:** v2.34+ (verificar: `git --version`)
- **Claude AI:** Conta ativa em https://claude.ai
- **Claude Code:** Acesso habilitado (https://claude.ai/code)

### Verificar Pré-requisitos

```bash
node --version      # Esperar: v22.x.x ou superior
npm --version       # Esperar: v9.x.x ou superior
git --version       # Esperar: git version 2.34+
```

Se algum estiver faltando, instale em: https://nodejs.org/

---

## ⚡ Setup Rápido (5 minutos)

### **Passo 1: Clonar o Repositório**

```bash
# Opção A: Usar HTTPS
git clone https://github.com/MN1970/Codex-exemplo.git
cd Codex-exemplo

# Opção B: Usar SSH (se tiver SSH key configurada)
git clone git@github.com:MN1970/Codex-exemplo.git
cd Codex-exemplo
```

### **Passo 2: Instalar Dependências**

```bash
npm install
```

⏳ Isto leva 2-3 minutos. Aguarde a conclusão.

### **Passo 3: Iniciar Servidor MCP**

```bash
npm run dev
```

✅ Quando ver:
```
✨ Codex Hub MCP Server is operational
Ready for Codex implementation
```

O servidor está pronto! ✅

### **Passo 4: Abrir Claude Code (nova janela/terminal)**

```bash
# Em outro terminal/janela
cd Codex-exemplo
claude

# Ou: https://claude.ai/code
# Selecionar "Open Folder" → Codex-exemplo
```

✅ Pronto para usar! Pule para [Usar Maestro Router](#usar-maestro-router-no-claude)

---

## 🔌 Setup Completo (Claude AI Integrado)

### **Se quer integração máxima com Claude AI:**

### **Passo 1: Compilar TypeScript**

```bash
npm run build
```

Isto gera `dist/` com JavaScript compilado.

### **Passo 2: Configurar MCP Server no Claude AI**

#### **Via Claude AI Web (claude.ai):**

1. Acesse: https://claude.ai/settings
2. Vá para: **Claude Code** → **MCP Servers**
3. Clique: **+ Add MCP Server**

#### **Preencha com:**

```json
{
  "name": "codex-hub-maestro",
  "command": "node",
  "args": ["/caminho/completo/para/Codex-exemplo/dist/index.js"],
  "environment": {
    "NODE_ENV": "production",
    "ANTHROPIC_API_KEY": "sk-ant-...",
    "COWORK_API_URL": "https://cowork.example.com/api"
  }
}
```

⚠️ **IMPORTANTE:** 
- Substitua `/caminho/completo/` pelo caminho real da pasta
- Obtenha `ANTHROPIC_API_KEY` em https://console.anthropic.com/keys

4. Clique: **Save**
5. Aguarde: "Server connected successfully ✅"

### **Passo 3: Reiniciar Claude AI**

```bash
# Se estiver usando CLI:
ctrl+c  (parar)
claude  (iniciar novamente)

# Se estiver usando Web:
F5 (reload)
```

---

## 🧪 Teste de Conexão

### **Teste 1: Verificar Maestro Router (CLI)**

```bash
# No diretório Codex-exemplo
npx tsx src/index.ts
```

Esperado:
```
🚀 Codex Hub MCP Server Starting
✅ Maestro Router initialized
✅ 20 Manta agents loaded
✅ Test: Saneamento routing
✅ Integration test PASSED
```

### **Teste 2: Executar E2E Integration Test**

```bash
npx tsx tests/e2e-maestro-claude-cowork.test.ts
```

Esperado:
```
✅ Passed: 3/3
Success Rate: 100.0%
✨ CODEX HUB E2E INTEGRATION READY FOR PRODUCTION
```

### **Teste 3: Listar Agentes**

```bash
npm run test -- --testNamePattern="list_maestro_agents"
```

Esperado:
```
✅ All agents listed (20 total)
✅ S6-S10 agents included
```

---

## 🎯 Usar Maestro Router no Claude

### **Via Claude Code CLI**

```bash
claude
```

Dentro do chat do Claude:

```
Quero rotear um prompt para o agente correto.
Use o Maestro Router para este prompt:
"Preciso de um projeto de ETA com análise de qualidade de água e adução"

Diga-me qual agente deve ser responsável.
```

**Resposta esperada:**
```
Agent: agente-saneamento (Manta 03-S8)
Confidence: HIGH
Score: 20.35
Keywords matched: eta, água, adutora, drenagem
```

---

## 💡 Exemplos Práticos

### **Exemplo 1: Rotear para Saneamento**

```
Prompt: "Vou fazer um projeto de ETA e ETE com adutora de 150km"
Esperado: agente-saneamento (S8)
```

**No Claude AI:**
```
Claude, use o Maestro para rotear este prompt para o agente correto:
"Vou fazer um projeto de ETA e ETE com adutora de 150km"
```

---

### **Exemplo 2: Rotear para Energia**

```
Prompt: "Preciso de subestação com transmissão em 500kV aprovada por ANEEL"
Esperado: agente-energia (S9)
```

**No Claude AI:**
```
Use o Maestro Router para:
"Preciso de subestação com transmissão em 500kV aprovada por ANEEL"
```

---

### **Exemplo 3: Rotear para Portos**

```
Prompt: "Terminal portuário com berços para contêineres e dragagem"
Esperado: agente-portos (S6)
```

**No Claude AI:**
```
Claude, qual agente Manta é responsável por:
"Terminal portuário com berços para contêineres e dragagem"
```

---

### **Exemplo 4: Sincronizar com Cowork**

```
Após rotear para agente, crie uma task no Cowork:

Claude, você pode:
1. Rotear este prompt: "Projeto de barragem de rejeitos de 80m"
2. Criar uma task no Cowork para o agente responsável
3. Adicionar um comentário com os detalhes da roteagem
```

---

## 🔍 Verificar Status

### **Verificar se Servidor está rodando:**

```bash
# Terminal 1: Servidor
npm run dev

# Terminal 2: Verificar
curl -X GET http://localhost:3000/health
```

Resposta esperada:
```json
{
  "status": "operational",
  "agents": 20,
  "router": "initialized"
}
```

### **Listar Agentes Disponíveis:**

```bash
curl -X GET http://localhost:3000/agents
```

---

## 📚 Mapa de Agentes

| Código | Agente | Segment | Rotas | Status |
|--------|--------|---------|-------|--------|
| Manta 00 | maestro | Router | - | ✅ Operacional |
| Manta 03-S1 | agente-infraestrutura | Rodovias | pavimento, CBUQ, DNIT | ✅ |
| Manta 03-S2 | agente-infraestrutura | OAE (Pontes) | ponte, viaduto, NBR 7187 | ✅ |
| Manta 03-S3 | agente-infraestrutura | Ferrovia | trilho, AMV, dormente | ✅ |
| Manta 03-S4 | agente-infraestrutura | Metrô | estação, NATM, linha 4 | ✅ |
| Manta 03-S6 | agente-portos | Portos | dragagem, berço, contêiner | 🆕 |
| Manta 03-S7 | agente-aeroportos | Aeroportos | pista, ANAC, TPS | 🆕 |
| Manta 03-S8 | agente-saneamento | Saneamento | ETA, ETE, adutora | 🆕 |
| Manta 03-S9 | agente-energia | Energia | transmissão, LT, ANEEL | 🆕 |
| Manta 03-S10 | agente-barragens | Barragens | vertedouro, rejeitos, PNSB | 🆕 |

---

## ⚙️ Configuração Avançada

### **Variáveis de Ambiente (.env)**

Copiar `.env.example` para `.env`:

```bash
cp .env.example .env
```

Editar `.env` e configurar:

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Cowork
COWORK_API_URL=https://cowork.example.com/api
COWORK_API_TOKEN=token_aqui

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxx

# Logging
LOG_LEVEL=info
```

### **Iniciar com Variáveis Customizadas**

```bash
ANTHROPIC_API_KEY=sk-ant-... npm run dev
```

---

## 🐛 Solução de Problemas

### **Problema: "Cannot find module '@modelcontextprotocol/sdk'"**

```bash
npm install
npm run build
```

### **Problema: "Port 3000 already in use"**

```bash
# Matatar processo na porta 3000
lsof -i :3000
kill -9 <PID>

# Ou usar outra porta
PORT=3001 npm run dev
```

### **Problema: "ANTHROPIC_API_KEY not found"**

```bash
# Verificar .env
cat .env | grep ANTHROPIC_API_KEY

# Se vazio, obter em:
# https://console.anthropic.com/api_keys

# Configurar
export ANTHROPIC_API_KEY="sk-ant-..."
npm run dev
```

### **Problema: TypeScript compilation errors**

```bash
# Limpar cache
rm -rf dist node_modules
npm install
npm run build
```

### **Problema: MCP Server não conecta no Claude AI**

1. Verificar caminho absoluto está correto
2. Verificar `node` pode executar arquivo:
   ```bash
   /usr/bin/node /path/to/dist/index.js
   ```
3. Verificar logs:
   ```bash
   npm run dev 2>&1 | tail -20
   ```

---

## 📖 Documentação Completa

Dentro do projeto:

- `README.md` — Overview do projeto
- `ARCHITECTURE.md` — Arquitetura técnica
- `CONTRIBUTING.md` — Como contribuir
- `src/services/maestro-router.ts` — Implementação do Maestro

---

## 🚀 Próximos Passos

1. ✅ Setup completo
2. ✅ Testar Maestro Router
3. ✅ Sincronizar com Cowork
4. 📱 Usar em produção (Claude AI)
5. 🔄 Feedback loop com Cowork

---

## 💬 Exemplos de Prompts para Claude AI

### **Para Testar Roteamento:**

```
"Teste o Maestro Router com estes prompts e diga qual agente 
cada um vai para:

1. 'Projeto de linha de transmissão 765kV com subestação'
2. 'Terminal portuário com 8 berços para contêineres'
3. 'Barragem de rejeitos com altura de 100m'
4. 'Pista de aeroporto com 3.5km e TPS'
5. 'Sistema de tratamento de esgoto ETE com reúso'"
```

### **Para Criar Tasks no Cowork:**

```
"Use o Maestro para rotear e então crie uma task no Cowork:

Prompt: 'Sistema de adução de água para município de 80km com 
elevatória de recalque'

Depois adicione um comentário com:
- Agente responsável
- Score de confiança
- Keywords detectadas"
```

### **Para Feedback Loop:**

```
"Simule este fluxo completo:

1. User: 'Preciso de subestação para distribuidora regional'
2. Claude: Chamar Maestro
3. Maestro: Rotear para agente
4. Agent: Criar task no Cowork
5. Cowork: Enviar feedback
6. Claude: Retornar contexto completo ao user"
```

---

## ✅ Checklist de Conclusão

- [ ] Node.js v22+ instalado
- [ ] Git configurado
- [ ] Repositório clonado
- [ ] `npm install` executado
- [ ] `npm run build` sem erros
- [ ] `npm run dev` iniciado com sucesso
- [ ] MCP Server conectado no Claude AI
- [ ] Teste de roteamento passado (3/3)
- [ ] E2E test passado (3/3)
- [ ] Primeiro prompt testado no Claude AI
- [ ] Task criada no Cowork

---

## 📞 Suporte

Se tiver dúvidas ou problemas:

1. Verificar logs: `npm run dev 2>&1`
2. Rodar testes: `npm test`
3. Ler documentação: `README.md`, `ARCHITECTURE.md`
4. Verificar PR #48: https://github.com/MN1970/Codex-exemplo/pull/48

---

## 🎉 Parabéns!

Você agora tem o **Codex Hub** totalmente funcional:

- ✅ 20 agentes Manta operacionais
- ✅ Maestro Router determinístico
- ✅ Integração Claude AI + Cowork
- ✅ E2E tests validados
- ✅ Pronto para produção

**Próxima etapa:** Use em seus projetos! 🚀

---

**Versão:** 1.0.0  
**Data:** 2026-07-31  
**Status:** Production Ready ✅
