# Competitive Intelligence com Obscura

**Como usar Obscura para rastrear concorrentes e monitorar mercado.**

---

## 1. Quickstart — Rastrear Verum

```bash
# Script prático
python examples/competitive-intel-verum.py

# Resultado: relatório JSON em /tmp/verum-intel.json
```

---

## 2. O que o script extrai

| Dado | Método | Uso |
|------|--------|-----|
| **Serviços** | Regex em keywords | Que áreas de negócio? |
| **Projetos** | Pattern matching | Qual é o portfólio? |
| **Tecnologias** | Keyword search | Que stack usam? |
| **Contatos** | Email regex | Como alcançar? |
| **Equipe** | Heurística de tamanho | Qual é a escala? |

---

## 3. Extensões possíveis

### 3.1 Monitoramento contínuo (Routine)

```python
# Rodar diariamente via send_later + Routine
# Comparar relatórios de semana em semana
# Alertar sobre mudanças significativas

async def monitor_competitor_changes():
    """Comparar intel de hoje vs semana passada."""
    today = await analyze_competitor("https://verum.com.br")
    last_week = load_json("/backups/verum-intel-2026-07-16.json")
    
    changes = {
        "novos_servicos": set(today.services) - set(last_week.services),
        "projetos_removidos": set(last_week.projects) - set(today.projects),
        "tech_stack_mudou": today.technologies != last_week.technologies
    }
    
    if any(changes.values()):
        alert(f"⚠️ Verum mudou: {changes}")
```

### 3.2 Análise de múltiplos concorrentes

```python
competitors = [
    "https://verum.com.br",
    "https://otro.com.br",
    "https://tercero.com.br"
]

for url in competitors:
    intel = analyze_competitor(url)
    # Comparar side-by-side
```

### 3.3 Scraping avançado com eval()

```bash
# Extrair tabela de preços dinâmica
obscura fetch https://verum.com.br/precos \
  --eval 'document.querySelectorAll("tr").map(r => ({
    servico: r.querySelector("td:1").textContent,
    preco: r.querySelector("td:2").textContent,
    data_atualizacao: r.querySelector("td:3").textContent
  }))' \
  --dump json > precos-verum.json
```

### 3.4 Índice de preços Manta

```python
# Skill `mk-manta` integrada
# Atualizar base de dados em Supabase com:
# - URL concorrente
# - Preço/escopo extraído
# - Data de coleta
# - Trend (subindo/descendo)

await supabase.table("competitive_pricing").insert({
    "competitor": "Verum",
    "servico": "Consultoria BIM",
    "preco_estimado": "R$ 50k-100k",
    "coleta_data": datetime.now(),
    "fonte": "https://verum.com.br/servicos"
})
```

---

## 4. Casos reais de uso

### Advisory (Manta 15)
- Monitorar sites de concorrentes em tempo real
- Alertar sobre novas parcerias, contratações
- Acompanhar estratégia de preços

### BD (Manta 13) + mk-manta
- Coletar dados de mercado para business case
- Benchmarking de projetos similares
- Estimar ticket size de propostas

### Manta 01 (Claims)
- Extrair termos de serviço de concorrentes
- Monitorar mudanças em condições comerciais
- Documentar para análise de disputes

---

## 5. Limitações & Compliance

⚠️ **Respeitar robots.txt e termos de serviço**

```bash
# Verificar permissão antes
curl -s https://verum.com.br/robots.txt

# Se permitido:
obscura fetch https://verum.com.br --dump text

# Se NOT permitido (User-agent: *), respeitar
```

**Recomendações:**
- ✅ Usar stealth (fingerprint consistente)
- ✅ Respeitar rate limits (1-2 req/min por site)
- ✅ Documentar data/hora da coleta
- ✅ Usar dados apenas para análise interna
- ❌ NÃO republish conteúdo sem permissão

---

## 6. Integração com MCP Obscura

Quando registrado em `.mcp.json`, qualquer skill pode chamar:

```python
# skill mk-manta.py
obscura_server = get_mcp_server("obscura")

# Fetch com render
html = await obscura_server.fetch({
    "url": "https://verum.com.br",
    "dump": "html"
})

# Eval customizado
data = await obscura_server.fetch({
    "url": "https://verum.com.br/equipe",
    "eval": "document.querySelectorAll('.team-member').map(m => m.textContent)"
})
```

---

## 7. Próximos passos

- [ ] Testar em ambiente local com internet aberto
- [ ] Criar Routine de monitoramento diário
- [ ] Integrar resultado com Manta 01 (claims analysis)
- [ ] Adicionar alertas no Slack via MCP
- [ ] Indexar dados em Supabase (rag_chunks) para RAG

---

**Exemplo:** `examples/competitive-intel-verum.py`  
**Documentação:** `OBSCURA-INTEGRATION.md`  
**Conector MCP:** `.mcp.json`

Criado: 2026-07-23  
Atualizado: 2026-07-23
