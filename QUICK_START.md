# ⚡ Quick Start — Codex Hub em 5 Minutos

## 🚀 Começar AGORA

### **1. Clonar**
```bash
git clone https://github.com/MN1970/Codex-exemplo.git
cd Codex-exemplo
```

### **2. Instalar**
```bash
npm install
```

### **3. Iniciar Servidor**
```bash
npm run dev
```

✅ Servidor rodando em http://localhost:3000

---

## 💬 Usar no Claude AI

### **Via Web (claude.ai/code)**

1. Acesse: https://claude.ai/code
2. Clique: **"Open Folder"**
3. Selecione: `/Codex-exemplo`
4. Pergunte ao Claude:

```
"Use o Maestro Router para rotear este prompt:
'Projeto de ETA com adução de 150km'"
```

**Resposta:**
```
Agent: agente-saneamento (Manta 03-S8)
Confidence: HIGH
Score: 20.35
```

---

### **Via CLI (claude command)**

```bash
cd /Codex-exemplo
claude
```

Dentro do chat:
```
Rotear para mim: "Projeto de linha de transmissão 500kV com subestação"
```

---

## 🧪 Testar Tudo

```bash
# Teste integração
npx tsx tests/e2e-maestro-claude-cowork.test.ts

# Resultado esperado:
# ✅ Passed: 3/3
# Success Rate: 100.0%
```

---

## 📚 20 Agentes Disponíveis

| Tipo | Agente | Rotear com |
|------|--------|-----------|
| **Rodovias** | S1 | pavimento, CBUQ, DNIT |
| **Pontes** | S2 | ponte, viaduto, NBR 7187 |
| **Ferrovia** | S3 | trilho, AMV, dormente |
| **Metrô** | S4 | estação, NATM, linha 4 |
| **Portos** | S6 | dragagem, berço, contêiner |
| **Aeroportos** | S7 | pista, ANAC, TPS |
| **Saneamento** | S8 | ETA, ETE, adutora |
| **Energia** | S9 | transmissão, LT, ANEEL |
| **Barragens** | S10 | vertedouro, rejeitos, PNSB |

---

## 🎯 Exemplos Imediatos

```bash
# Terminal 1: Servidor
npm run dev

# Terminal 2: Teste com curl
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"prompt": "ETA com adução"}'

# Resposta:
# {"agent":"agente-saneamento","code":"Manta 03-S8","score":20.35,"confidence":"high"}
```

---

## 📖 Documentação Completa

- `CLAUDE_AI_SETUP.md` — Guia completo (30 minutos)
- `README.md` — Overview do projeto
- `ARCHITECTURE.md` — Arquitetura técnica

---

## ✅ Pronto!

Você está pronto para:
1. ✅ Rotear prompts para agentes
2. ✅ Criar tasks no Cowork
3. ✅ Sincronizar bidirecional
4. ✅ Usar em produção

**Próximo:** Leia `CLAUDE_AI_SETUP.md` para setup completo

---

**⏱️ Tempo total: ~5 minutos**  
**Status: ✅ Operational**  
**Agentes: 20/20 Ready**
