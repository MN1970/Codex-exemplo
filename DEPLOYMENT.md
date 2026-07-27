# 🚀 Deployment — Manta Maestro v4.3

Guia completo de deployment dos Protocolos P1 + P2 com Seed Supabase DER-SP + SICRO.

---

## ✅ Checklist de Deployment

### **FASE 1: Protocolos P1 + P2 (COMPLETO)**

- [x] CLAUDE.md atualizado (v4.3)
- [x] .claude/settings.json com hooks automáticos
- [x] .claude/skills/maestro-protocolos.md (Skill executor)
- [x] .claude/workflows/maestro-16-agentes-paralelo.js (Workflow 16 agentes)
- [x] PR #39 criado e sob monitoração
- [x] Commits pushed para `claude/maestro-leia-descreva-awlnhu`

**Status:** ✅ **ATIVO** — P1 + P2 prontos para operação

---

### **FASE 2: Supabase Seed (EM PROGRESSO)**

#### 2.1 Infraestrutura
- [x] Script seed criado: `scripts/seed_supabase_der_sicro.py`
- [x] Parser DER-SP (TPU_2026_01.xlsx) — ✅ Pronto
- [x] Parser SICRO (CSV) — ✅ Template pronto
- [x] Embeddings OpenAI — ✅ Integrado
- [x] Upsert Supabase pgvector — ✅ Integrado
- [ ] **Credenciais Supabase** — ⏳ Aguardando

#### 2.2 Dados
- [x] TPU_2026_01.xlsx recebido (DER-SP JAN/2026)
- [ ] SICRO CSV — ⏳ Aguardando (ou obter de fonte pública DNIT)

#### 2.3 Execution
```bash
# Passo 1: Criar .env local
cp .env.template .env
# Editar com suas credenciais

# Passo 2: Executar seed
python scripts/seed_supabase_der_sicro.py \
  --der TPU_2026_01.xlsx \
  --sicro sicro.csv \
  # (sem --sem-embedding para embeddings)

# Passo 3: Verificar
# Supabase → rag_chunks → verificar contagem + embeddings
```

**Status:** ⏳ **BLOQUEADO** — Aguardando credenciais Supabase

---

## 🎯 Operação — Uso de P1 + P2

### **P1: Confirmação Banco + Data**

**Trigger automático:**
```
Usuário: "Orçamento SICRO para rodovia"
↓
Maestro: "❓ Banco: SICRO ✓ Data: qual? (JAN/2026?)"
Usuário: "jan 2026"
↓
Maestro: "✅ Usando SICRO JAN/2026. Roteando → agente-infraestrutura S1"
```

**Ativa automaticamente em:**
- Menção SICRO|DER-SP|ORSE|SINAPI
- Orçamento, preço unitário, TPU
- Composição de BDI

### **P2: Paralelo 16x Sonnet**

**Trigger automático:**
```
Usuário: "Execute com 16 agentes: analise 16 segmentos"
↓
Maestro: "🚀 Disparando 16x Sonnet paralelo..."
[16 agentes simultâneos]
↓
Maestro: "✅ 16 análises concluídas em 8-12 min"
```

**Ativa automaticamente em:**
- "Execute com 16 agentes"
- "Paralelo 16x Sonnet"
- "/maestro-parallel 16"

---

## 📂 Estrutura de Arquivos

```
Codex-exemplo/
├── CLAUDE.md                                 # Master registry (v4.3)
├── DEPLOYMENT.md                             # Este arquivo
├── .env.template                             # Template credenciais
├── .claude/
│   ├── settings.json                         # Hooks P1+P2
│   ├── skills/
│   │   └── maestro-protocolos.md            # Skill executor
│   ├── workflows/
│   │   └── maestro-16-agentes-paralelo.js   # Workflow 16 agentes
│   └── agents/
│       ├── agente-portos.md
│       ├── agente-aeroportos.md
│       ├── agente-saneamento.md
│       ├── agente-energia.md
│       └── agente-barragens.md
├── scripts/
│   └── seed_supabase_der_sicro.py           # Seed DER-SP+SICRO
└── README.md
```

---

## 🔐 Credenciais Supabase

### **Como obter:**

1. **Supabase Dashboard:** https://app.supabase.com
2. **Seu Projeto** → Settings → API
3. **Copiar:**
   - `URL` → `SUPABASE_URL`
   - `service_role` (secret) → `SUPABASE_SERVICE_KEY`

### **Criar .env local:**
```bash
cp .env.template .env
# Editar com suas chaves
```

---

## 🧪 Testes

### **P1: Confirmação Banco + Data**
```bash
# Teste no Claude Code:
# "Orçamento DER-SP jan 2026"
# Esperado: Deve pedir Banco + Data, depois confirmar
```

### **P2: Paralelo 16x Sonnet**
```bash
# Teste no Claude Code:
# "Execute com 16 agentes: [16 tarefas]"
# Esperado: Dispara workflow maestro-16-agentes-paralelo
```

### **Seed Supabase**
```bash
python scripts/seed_supabase_der_sicro.py --der TPU_2026_01.xlsx --sem-embedding
# Esperado: ✅ Seed concluído! (sem embeddings)
```

---

## 📊 Status Geral

| Componente | Status | Ticket |
|-----------|--------|--------|
| **P1: Confirmação Banco+Data** | ✅ Ativo | MNT-2026-PROTOCOLOS-P1P2 |
| **P2: Paralelo 16x Sonnet** | ✅ Ativo | MNT-2026-PROTOCOLOS-P1P2 |
| **Seed DER-SP (TPU)** | ⏳ Aguardando creds | MNT-2026-SEED-SUPABASE |
| **Seed SICRO (CSV)** | ⏳ Aguardando arquivo | MNT-2026-SEED-SUPABASE |
| **PR #39** | 🔄 Em monitoração | - |

---

## 📞 Próximos Passos

**Para liberar FASE 2 (Seed completo):**

1. **Forneça credenciais Supabase** (ou configure projeto novo)
2. **Envie arquivo SICRO CSV** (ou use fonte pública DNIT)
3. **Execute seed script** com credenciais
4. **Valide dados** em Supabase → rag_chunks

**Então:**
- Protocolos P1+P2 estarão 100% operacionais
- Busca semântica SICRO+DER-SP ativa
- Roteamento automático → agentes S1-S10

---

**Versão:** 4.3 (2026-07-27)  
**Ticket:** MNT-2026-PROTOCOLOS-P1P2 + MNT-2026-SEED-SUPABASE  
**Maestro Status:** 🟢 **OPERACIONAL**
