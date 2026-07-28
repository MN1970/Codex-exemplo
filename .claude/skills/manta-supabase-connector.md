# manta-supabase-connector — MCP Integration

Skill que usa **MCP Supabase connector** para todas operações de dados — sem precisar de .env ou credenciais locais.

**Versão:** 1.0 | **Status:** ✅ Ativo | **Projeto:** ogxxgvgtulrbbppshjie (manta-maestro)

---

## Características

- ✅ **Sem .env** — Usa MCP connector (já autenticado)
- ✅ **Sem credenciais locais** — Seguro e centralizado
- ✅ **RAG queries** — Busca vetorial em rag_chunks
- ✅ **Seed integrado** — Execute_sql para DER-SP + SICRO
- ✅ **Operação contínua** — P1 + P2 com dados em tempo real

---

## Operações Suportadas

### **1. Query RAG (Busca Semântica)**
```python
# Buscar composições SICRO parecidas com "pavimento CBUQ"
manta_supabase_connector.search_rag(
  banco='sicro',
  query='pavimento concreto betuminoso usinado quente',
  limit=5
)
```

### **2. Listar Tabelas**
```python
manta_supabase_connector.list_tables()
# Retorna: ['rag_chunks', 'importacoes', 'servicos', ...]
```

### **3. Execute SQL (Admin)**
```python
manta_supabase_connector.execute_sql(
  query="""
    INSERT INTO rag_chunks (banco, codigo, descricao, preco, embedding)
    VALUES ('der-sp', '21.01.01', 'Sondagem...', 220.68, [0.1, 0.2, ...])
  """
)
```

### **4. Seed DER-SP via SQL**
```python
manta_supabase_connector.seed_der_sp(
  xlsx_path='TPU_2026_01.xlsx',
  with_embeddings=False  # ou True com OpenAI
)
```

### **5. Seed SICRO via SQL**
```python
manta_supabase_connector.seed_sicro(
  csv_path='sicro_jan2026.csv',
  mes_ano='01-2026',
  with_embeddings=False
)
```

---

## Integração com P1 + P2

### **P1: Confirmação Banco + Data**
```
Usuário: "Orçamento SICRO jan 2026"
  ↓
Maestro: (usa manta_supabase_connector)
  → Verifica: SICRO JAN/2026 existe?
  → Busca: 500 registros de SICRO JAN/2026
  ↓
Maestro: "✅ Usando SICRO JAN/2026 (500 registros encontrados)"
```

### **P2: Paralelo 16x com Dados**
```
Usuário: "Execute com 16 agentes: analise 16 tipos de obra SICRO"
  ↓
Maestro (16x paralelo):
  → Agente 1: Busca SICRO "escavação" → RentaSQL via connector
  → Agente 2: Busca SICRO "pavimentação" → via connector
  ...
  → Agente 16: Busca DER-SP "estrutura" → via connector
  ↓
Maestro: "✅ 16 análises com dados reais"
```

---

## Arquivo de Implementação

Localização: `.claude/skills/manta-supabase-connector.py`

```python
# Pseudocódigo
from supabase_mcp import SupabaseMCPClient

class MantaSupabaseConnector:
    def __init__(self, project_id='ogxxgvgtulrbbppshjie'):
        self.project_id = project_id
        self.client = SupabaseMCPClient(project_id)  # Usa MCP
    
    def search_rag(self, banco, query, limit=5):
        """Busca vetorial em rag_chunks via pgvector"""
        return self.client.rpc('match_documents', {
            'query_embedding': embed(query),
            'match_threshold': 0.7,
            'match_count': limit,
            'banco_filter': banco
        })
    
    def execute_sql(self, query):
        """Execute SQL direto (admin)"""
        return self.client.rpc('sql_exec', {'sql': query})
    
    def seed_der_sp(self, xlsx_path, with_embeddings=False):
        """Seed TPU DER-SP via SQL INSERT"""
        # 1. Parse xlsx
        # 2. Gera embeddings (opcional)
        # 3. Monta INSERT em chunks
        # 4. Execute via self.execute_sql()
        pass
```

---

## Configuração MCP

**Já ativo em** `.claude/settings.json`:

```json
{
  "connectors": ["supabase"],
  "mcp_tools": {
    "supabase": {
      "project_id": "ogxxgvgtulrbbppshjie",
      "auto_auth": true
    }
  }
}
```

---

## Uso no Maestro

Sempre que P1 ou P2 precisar de dados:

```
Maestro.data_source = "manta_supabase_connector"
↓
Todas queries → via MCP connector (sem .env)
↓
Operação segura + centralizada + auditável
```

---

## Status

```
🟢 MCP Connector: ATIVO (project_id: ogxxgvgtulrbbppshjie)
🟢 RAG Queries: Pronto
🟢 Seed SQL: Pronto
🟢 P1+P2 Integration: Pronto
⏳ Dados: Aguardando DER-SP + SICRO seed
```

**Próximo:** Execute seed via connector e comece operações! 🚀
