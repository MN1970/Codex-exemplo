# 🔐 Setup Supabase — Credenciais para Seed DER-SP + SICRO

Guia visual passo-a-passo para completar as credenciais e executar seed.

---

## ✅ Já Preenchido (via MCP Supabase)

```env
SUPABASE_URL=https://ogxxgvgtulrbbppshjie.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Projeto:** manta-maestro | **Status:** ACTIVE_HEALTHY | **Região:** sa-east-1

---

## ❌ Falta Completar — SUPABASE_SERVICE_KEY

### **Passo 1: Abra Supabase Dashboard**
```
https://app.supabase.com
```

### **Passo 2: Selecione Projeto "manta-maestro"**
Ou acesse direto:
```
https://app.supabase.com/project/ogxxgvgtulrbbppshjie
```

### **Passo 3: Vá para Settings → API**
```
Lado esquerdo → Settings → API
```

### **Passo 4: Copie "service_role secret"**
Encontre a seção:
```
┌─────────────────────────────────────┐
│ Keys & tokens                       │
├─────────────────────────────────────┤
│ service_role (secret)               │
│ [Copiar] ← CLIQUE AQUI              │
│ eyJhbGciOiJIUzI1NiIsInR5cCI...      │
└─────────────────────────────────────┘
```

⚠️ **Atenção:** Essa é uma chave SECRETA — não compartilhe!

### **Passo 5: Cole em .env**
Edite `/home/user/Codex-exemplo/.env`:
```env
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
```

---

## 🧪 Testar Conexão

```bash
cd /home/user/Codex-exemplo

# Teste se .env está correto
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

if url and key:
    print(f'✅ SUPABASE_URL: {url}')
    print(f'✅ SUPABASE_SERVICE_KEY: {key[:20]}...')
else:
    print(f'❌ SUPABASE_URL: {url}')
    print(f'❌ SUPABASE_SERVICE_KEY: {key}')
EOF
```

**Esperado:**
```
✅ SUPABASE_URL: https://ogxxgvgtulrbbppshjie.supabase.co
✅ SUPABASE_SERVICE_KEY: eyJhbGciOiJIUzI1NiIsIn...
```

---

## 🚀 Executar Seed

Após completar `.env`:

```bash
# Seed DER-SP (TPU_2026_01.xlsx) — sem embeddings
python scripts/seed_supabase_der_sicro.py \
  --der /root/.claude/uploads/dde16663-d743-51f3-a652-93e05204725a/0ce13ad8-TPU_2026_01.xlsx \
  --sem-embedding

# Esperado:
# ✅ Supabase conectado: https://ogxxgvgtulrbbppshjie.supabase.co
# 📂 DER-SP: TPU_2026_01.xlsx
# 📄 Processando: TPU JAN 2026-O (1756 linhas)
# 📄 Processando: TPU JAN 2026-D (1729 linhas)
# ✓ 3485 registros lidos
# 📤 Enviando 3485 registros para rag_chunks...
# ✓ Upsert concluído. Importados: 3485 | Erros: 0
# ✅ Seed concluído!
```

---

## 📊 Validar no Supabase

Após seed completado:

1. **Supabase Dashboard** → seu projeto → Table Editor
2. **Tabela:** `rag_chunks`
3. **Verificar:**
   - Rows count: ~3485 (DER-SP)
   - Colunas: `codigo`, `descricao`, `preco`, `tipo_preco`, etc.
   - Dados: ex. codigo `21.01.01`, descricao "Sondagem...", preco 220.68

---

## 🎯 Próximas Fases

Após DER-SP seed:

1. **Seed SICRO** (igual, com arquivo SICRO CSV)
2. **Embeddings** (geração vetorial OpenAI)
3. **Operação P1+P2** (Banco+Data automático + Paralelo 16x)

---

## ❓ Dúvidas

- **Onde está minha service_role key?**  
  → Supabase Dashboard → Settings → API → "service_role (secret)"

- **Posso usar ANON_KEY para seed?**  
  → Não. Seed precisa de `service_role` (super permissões).

- **E se perder a chave?**  
  → Supabase permite regenerar em Settings → API.

---

**Próximo passo:** Cole a `service_role` em `.env` e execute seed! 🚀
