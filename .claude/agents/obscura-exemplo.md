# Obscura — Servidor MCP (Browser Headless + Scraping)

**Status:** ✅ Ativo  
**Versão:** 0.1.10  
**Registro:** `mcpServers.obscura` em `.mcp.json`

---

## Descrição

Servidor MCP que fornece acesso ao **Obscura** — ferramenta headless browser
para fetch, render, scraping e automação CDP de sites. Integra-se com qualquer
agente Manta que precise:

- Baixar/renderizar HTML dinâmico
- Extrair dados estruturados (DOM, links, texto)
- Monitorar portais em tempo real
- Stealth + anti-detecção

---

## Capabilities

| Capacidade | Descrição | Exemplo |
|------------|-----------|---------|
| `fetch` | Fetch + render de URL | `obscura fetch https://...` |
| `dump text\|html\|json\|links` | Extrair conteúdo em diferentes formatos | Links de edital, HTML completo, dados JSON |
| `--eval` | Executar JavaScript no DOM | Extrair tabelas dinâmicas, dados AJAX |
| `--stealth` | Fingerprint consistente, anti-detecção | Pesquisar sites de concorrentes |
| `--obey-robots` | Respeitar robots.txt | Compliance com diretrizes de scraping |
| `--proxy` | Suportar proxy SOCKS5/HTTP | Para redes corporativas |

---

## Roteamento (Maestro)

Não é uma vertical específica — todos os 20 agentes Manta podem usar Obscura
quando precisarem de web scraping/render. Exemplos:

```
IF usuário pede "buscar edital em..." OU "monitorar portal..." OU
   "extrair dados de..."
   → use MCP server "obscura" para fetch + parse
   → integre resultado com análise específica do agente
```

---

## Uso em Skills

Exemplo: `ler-edital-v2.py` (integrado com Obscura)

```python
import asyncio
from mcp_client import get_server

async def ler_edital_dinamico(url: str) -> dict:
    """Lê edital complexo que usa JavaScript dinâmico"""
    
    # 1. Obter servidor MCP Obscura
    obscura = get_server("obscura")
    
    # 2. Fetch com render
    page = await obscura.call("fetch", {
        "url": url,
        "dump": "html",
        "stealth": True,
        "obey_robots": True
    })
    
    # 3. Eval customizado (extrair campos específicos)
    dados = await obscura.call("fetch", {
        "url": url,
        "eval": """
            ({
                titulo: document.querySelector('h1')?.textContent.trim(),
                numero: document.querySelector('[data-edital-id]')?.textContent,
                datas: Array.from(document.querySelectorAll('.dates')).map(d => ({
                    label: d.querySelector('.label')?.textContent,
                    valor: d.querySelector('.value')?.textContent
                })),
                arquivos: Array.from(document.querySelectorAll('a.file-link')).map(a => ({
                    nome: a.textContent,
                    href: a.href
                }))
            })
        """,
        "dump": "json"
    })
    
    return dados

# Integração com Manta 13 (BD):
# await ler_edital_dinamico("https://portal.tcu.gov.br/licitacoes/...")
```

---

## Exemplos de Casos de Uso

### 1. Monitorar Portais (Advisory / BD)

```bash
# Coletar editais novos diariamente
obscura fetch https://www.comprasnet.gov.br \
  --dump links \
  --stealth \
  | grep -i "edital" > editais-novos.txt
```

### 2. Extrair Dados de Tabela Dinâmica (Energia / Saneamento)

```bash
obscura fetch https://www.aneel.gov.br/leiloes \
  --eval 'document.querySelectorAll("tr").map(r => ({
    id: r.querySelector("td:nth-child(1)").textContent,
    produto: r.querySelector("td:nth-child(2)").textContent,
    data: r.querySelector("td:nth-child(3)").textContent
  }))' \
  --dump json > leiloes.json
```

### 3. Buscar Arquivos em Portal (Qualquer agente)

```bash
obscura fetch https://portal.exemplo.com/documentos \
  --dump html | grep -oP 'href="\K[^"]*\.pdf' > lista-pdfs.txt
```

---

## Limitações conhecidas

1. **Acesso à rede:** Respeita política de proxy/firewall do ambiente
2. **JavaScript:** Suporta execução via `--eval`, mas não substitui browser full
3. **Autenticação:** Não mantém estado de login (sem suporte a cookies persistentes)
4. **Performance:** Cada fetch pode levar 3-5 segundos (render)

---

## Registrado em

- Arquivo: `.mcp.json` (nesta sessão)
- Registro permanente: `~/.claude/mcp.json` (do usuário)
- Documentação: `OBSCURA-INTEGRATION.md`

---

**Criado:** 2026-07-23  
**Próxima revisão:** 2026-Q4
