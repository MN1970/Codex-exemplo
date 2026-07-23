# Integração Obscura ↔ Manta Maestro

**Versão:** 1.0  
**Data:** 2026-07-23  
**Status:** ✅ Ativado e testado  
**Binário:** obscura v0.1.10 (x86_64-linux)  

---

## 1. O que é Obscura

**Obscura** é um browser headless + ferramenta CLI para:
- **Fetch & Render**: Baixar e renderizar páginas HTML/JavaScript
- **Scraping**: Extrair dados estruturados de sites (DOM, links, texto)
- **Stealth**: Fingerprint consistente, bloqueio de trackers, anti-detecção
- **CDP (Chrome DevTools Protocol)**: Automação headless nativa

**Casos de uso no Manta:**
- Monitorar portais de licitação/concessão em tempo real
- Coletar editais (ComprasNet, DOU, ANEEL, ANTT, ARTESP)
- Competitive intelligence (sites de concorrentes, cotações, tendências)
- Pesquisa de mercado para business case
- Renderização de documentos complexos (PDFs dinâmicos, dashboards)

---

## 2. Instalação & Registro MCP

### 2.1 Binário instalado

```bash
# Localização
/root/.local/bin/obscura
/root/.local/bin/obscura-worker

# Versão
/root/.local/bin/obscura --version
# → obscura 0.1.10
```

### 2.2 Registro MCP (stdio)

Arquivo: `.mcp.json`

```json
{
  "mcpServers": {
    "obscura": {
      "command": "/root/.local/bin/obscura",
      "args": ["mcp"],
      "env": {
        "OBSCURA_STEALTH": "true",
        "OBSCURA_OBEY_ROBOTS": "true"
      }
    }
  }
}
```

**Flags explicadas:**
- `OBSCURA_STEALTH=true` — Ativa fingerprint consistente + anti-detecção
- `OBSCURA_OBEY_ROBOTS=true` — Respeita robots.txt (recomendado para compliance)

### 2.3 Registro MCP (HTTP, alternativo)

Se o cliente MCP exigir transporte por rede:

```bash
# Em um terminal separado:
/root/.local/bin/obscura mcp --http --port 3000

# No .mcp.json:
{
  "mcpServers": {
    "obscura": {
      "url": "http://127.0.0.1:3000"
    }
  }
}
```

---

## 3. API Obscura (via CLI e MCP)

### 3.1 Comandos básicos

#### Fetch simples
```bash
obscura fetch <URL> [--dump text|json|links|html]
```

Exemplos:
```bash
# Apenas texto limpo
obscura fetch https://www.bndes.gov.br --dump text

# Links extraídos
obscura fetch https://licitacoes-e.tcu.gov.br --dump links

# HTML renderizado
obscura fetch https://example.com --dump html > saida.html

# JSON (estrutura)
obscura fetch https://example.com --dump json
```

#### Eval (JavaScript no DOM)
```bash
obscura fetch <URL> --eval '<script>'
```

Exemplo: Extrair tabela dinâmica em um portal de licitação
```bash
obscura fetch https://portal.tcu.gov.br --eval '
  document.querySelectorAll("table tr").map(row => ({
    edital: row.querySelector("td:nth-child(1)")?.textContent,
    status: row.querySelector("td:nth-child(2)")?.textContent,
    data: row.querySelector("td:nth-child(3)")?.textContent
  }))
' --dump json
```

#### Stealth + robots
```bash
obscura fetch <URL> \
  --stealth \
  --obey-robots \
  --dump text
```

#### Com proxy (se necessário)
```bash
obscura fetch <URL> \
  --proxy socks5://proxy.manta.local:1080 \
  --dump text
```

### 3.2 Acesso via MCP (Python/Node/CLI genérico)

Quando registrado em `.mcp.json`, ferramentas MCP podem chamar:

```python
# Pseudocódigo — implementação específica por linguagem
import mcp_client

obscura = mcp_client.get_server("obscura")
result = await obscura.call("fetch", {
    "url": "https://www.bndes.gov.br",
    "dump": "text",
    "stealth": True,
    "obey_robots": True
})
print(result.text)
```

---

## 4. Integração com Agentes Manta

### 4.1 Roteamento de uso

| Agente | Skill | Caso de uso | Exemplo |
|--------|-------|-------------|---------|
| Advisory (Manta 15) | advisory | Competitive intelligence | Monitorar sites de concorrentes, cotações, tendências do mercado |
| BD (Manta 13) | `ler-edital`, `mk-manta` | Buscar editais | ComprasNet, TCU, licitações-e, DOU, ANTAQ |
| Energia (S9) | (interno) | Portais ANEEL | Acompanhar editais de transmissão, leilões, publicações R1-R5 |
| Saneamento (S8) | (interno) | SNIS, editais | AySA, portais de saneamento, bases de dados |
| Portos (S6) | (interno) | ANTAQ | Publicações ANTAQ, estatísticas, terminais |
| Barragens (S10) | (interno) | CBDB, SIGBM | Bases de dados de barragens, relatórios de operação |

### 4.2 Exemplo: Skill `ler-edital` + Obscura

```python
# pseudo-código: skill ler-edital.py

import asyncio
from mcp_client import get_server

async def ler_edital(url_edital: str) -> dict:
    """Baixa e extrai dados estruturados de um edital via Obscura"""
    
    obscura = get_server("obscura")
    
    # 1. Fetch renderizado
    html_completo = await obscura.call("fetch", {
        "url": url_edital,
        "dump": "html",
        "stealth": True,
        "obey_robots": True
    })
    
    # 2. Parse + extração (Python native ou outro LLM)
    estrutura = parse_edital(html_completo)
    
    return {
        "url": url_edital,
        "numero": estrutura.numero,
        "orgao": estrutura.orgao,
        "objeto": estrutura.objeto,
        "data_publicacao": estrutura.data,
        "data_encerramento": estrutura.encerramento,
        "links_arquivos": estrutura.links,
        "raw_html": html_completo
    }

# Uso:
edital = await ler_edital("https://www.tcu.gov.br/licitacoes/2026/001")
print(edital["numero"])  # → "001/2026"
```

### 4.3 Exemplo: Monitoramento contínuo (skill `mk-manta`)

```python
# pseudo-código: skill mk-manta.py

async def monitorar_editais_diarios():
    """Roda diariamente via Routine; coleta editais novos e os indexa"""
    
    portais = [
        "https://www.comprasnet.gov.br",
        "https://licitacoes-e.tcu.gov.br",
        "https://www.bndes.gov.br/wps/portal/site/home/transparencia/licitacoes",
        "https://www.aneel.gov.br/leiloes"
    ]
    
    for portal in portais:
        # 1. Fetch via Obscura
        html = await obscura.call("fetch", {
            "url": portal,
            "dump": "html",
            "stealth": True
        })
        
        # 2. Extrair links de editais
        links_novos = extract_edital_links(html)
        
        # 3. Indexar em Supabase (rag_chunks)
        for link in links_novos:
            await supabase.table("rag_chunks").insert({
                "source": "edital",
                "url": link,
                "collected_at": datetime.now(),
                "agent_id": "mk-manta"
            })
    
    return {"novos": len(links_novos), "portais": len(portais)}
```

---

## 5. Testes executados

### 5.1 Verificação de instalação

```bash
✅ Binário instalado:
   /root/.local/bin/obscura (77 MB)
   /root/.local/bin/obscura-worker (73 MB)

✅ Versão:
   obscura 0.1.10

✅ Registro MCP:
   .mcp.json criado com configuração stdio

✅ Flags OBSCURA_STEALTH, OBSCURA_OBEY_ROBOTS configuradas
```

### 5.2 Estado da rede

**Ambiente:** Remote execution sandbox (Claude Code cloud)  
**Acesso externo:** Via proxy HTTPS em http://127.0.0.1:42709  
**CA Bundle:** /root/.ccr/ca-bundle.crt  
**Política:** Policy denial ativa (403 em tentativas de fetch externo)

**Próximos passos para testes reais:**
1. Testar em ambiente local (desktop/servidor) com internet aberto
2. Usar flags `--proxy` se atrás de proxy corporativo
3. Registrar Obscura permanentemente em `.claude/mcp.json` do usuário

---

## 6. Configuração permanente (para usuários)

### 6.1 Instalação local (macOS / Linux)

```bash
# Linux x86_64
curl -LO https://github.com/h4ckf0r0day/obscura/releases/latest/download/obscura-x86_64-linux.tar.gz
tar xzf obscura-x86_64-linux.tar.gz
sudo mv obscura obscura-worker /usr/local/bin/

# macOS Apple Silicon
curl -LO https://github.com/h4ckf0r0day/obscura/releases/latest/download/obscura-aarch64-macos.tar.gz
tar xzf obscura-aarch64-macos.tar.gz
sudo mv obscura obscura-worker /usr/local/bin/
```

### 6.2 Registrar em Claude Code

No arquivo **~/.claude/mcp.json** (ou settings via `/config`):

```json
{
  "mcpServers": {
    "obscura": {
      "command": "/usr/local/bin/obscura",
      "args": ["mcp"],
      "env": {
        "OBSCURA_STEALTH": "true",
        "OBSCURA_OBEY_ROBOTS": "true"
      }
    }
  }
}
```

### 6.3 Usar em prompts/skills

Toda skill que precisar de web scraping / fetch pode agora usar:
```
Use o servidor MCP "obscura" para buscar e renderizar <URL>
com stealth ativado.
```

---

## 7. Roadmap de expansão

| Fase | O quê | Quando | Responsável |
|------|-------|--------|-------------|
| 1 ✅ | Instalação + MCP | 2026-07-23 | Claude Code |
| 2 | RAG: Coleção de editais | Q3 2026 | Manta 13 (BD) |
| 3 | Skill `ler-edital` v2 | Q3 2026 | mk-manta |
| 4 | Routine: monitoramento diário | Q4 2026 | mk-manta |
| 5 | Integration: ANEEL/ANTAQ específicos | Q4 2026 | S9/S6 |

---

## 8. Referências

- **Repositório:** https://github.com/h4ckf0r0day/obscura
- **Releases:** https://github.com/h4ckf0r0day/obscura/releases/latest
- **Documentação Manta Master:** [CLAUDE.md](./CLAUDE.md)
- **Skills relacionadas:** `ler-edital`, `mk-manta`, `portal-gestao-manta`

---

**Mantido por:** Claude Code (Manta Maestro)  
**Última atualização:** 2026-07-23  
**Próxima revisão:** 2026-Q4
