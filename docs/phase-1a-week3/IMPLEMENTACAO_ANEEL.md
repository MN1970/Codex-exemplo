# Implementação: Integração ANEEL Editais no Manta Hub

## Contexto
Backend `agente-energia` (Manta 03-S9) precisa acessar editais de transmissão da ANEEL para consultas de usuários.

## Problema Atual
- Portal ANEEL bloqueado para requisições automatizadas (HTTP 403)
- CKAN API estruturada mas inacessível via proxy

## Soluções Recomendadas (por ordem de viabilidade)

---

## SOLUÇÃO 1: Scraper HTML + Cache (RECOMENDADO - Imediato)

### Arquivo: `backends/mcp/app/aneel_scraper.py`

```python
"""
Scraper robusto para editais ANEEL com cache local.
Fallback para Internet Archive se portal principal não responder.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ANEELEditalScraper:
    """Scraper para editais de transmissão ANEEL."""
    
    PORTAL_URL = "https://www.aneel.gov.br/aplicacoes/editais-transmissao"
    ARCHIVE_URL = "https://web.archive.org/web/20240101000000/dadosabertos.aneel.gov.br"
    CACHE_DIR = Path("/tmp/manta/aneel_cache")
    CACHE_TTL = timedelta(days=1)
    
    def __init__(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        self._load_cache()
    
    async def buscar_editais(
        self,
        ano: Optional[int] = None,
        tipo: Optional[str] = None  # "LT", "SE", "Ampliação"
    ) -> list:
        """
        Busca editais de transmissão.
        
        Fluxo:
        1. Verificar cache local
        2. Fazer scrape do portal ANEEL
        3. Fallback para Internet Archive
        4. Salvar em cache
        """
        
        cache_key = f"editais_{ano or 'all'}_{tipo or 'all'}"
        
        # 1. Verificar cache
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if datetime.now() - cached["timestamp"] < self.CACHE_TTL:
                logger.info(f"Cache hit: {cache_key}")
                return cached["data"]
        
        # 2. Tentar scrape do portal ANEEL
        try:
            editais = await self._scrape_aneel_portal(ano, tipo)
            if editais:
                self._save_cache(cache_key, editais)
                return editais
        except Exception as e:
            logger.warning(f"Erro no scrape ANEEL: {e}")
        
        # 3. Fallback para Internet Archive
        try:
            logger.info("Tentando Internet Archive...")
            editais = await self._scrape_internet_archive(ano, tipo)
            if editais:
                self._save_cache(cache_key, editais)
                return editais
        except Exception as e:
            logger.warning(f"Erro no Internet Archive: {e}")
        
        # 4. Retornar cache antigo (se existir)
        if cache_key in self._cache:
            logger.warning(f"Usando cache expirado para {cache_key}")
            return self._cache[cache_key]["data"]
        
        return []
    
    async def _scrape_aneel_portal(
        self,
        ano: Optional[int],
        tipo: Optional[str]
    ) -> list:
        """Faz scrape da página de editais do portal ANEEL."""
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                self.PORTAL_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        editais = []
        
        # Procurar por tabelas ou divs com editais
        # Estrutura esperada: <table> com linhas por edital
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                edital = self._parse_edital_row(cells, ano, tipo)
                if edital:
                    editais.append(edital)
        
        return editais
    
    def _parse_edital_row(self, cells, ano, tipo) -> Optional[dict]:
        """Extrai dados de uma linha de tabela de edital."""
        
        try:
            # Padrão esperado:
            # [0] Número | [1] Tipo | [2] Descrição | [3] Link PDF
            
            numero = cells[0].get_text().strip()
            titulo = cells[1].get_text().strip() if len(cells) > 1 else ""
            descricao = cells[2].get_text().strip() if len(cells) > 2 else ""
            
            # Procurar por link PDF
            pdf_url = None
            for link in cells[-1].find_all("a"):
                href = link.get("href", "")
                if href.endswith(".pdf"):
                    pdf_url = href if href.startswith("http") else f"https://www.aneel.gov.br{href}"
            
            # Extrair ano e tipo da descrição/título
            edital_ano = ano or self._extract_ano(titulo + " " + descricao)
            edital_tipo = tipo or self._extract_tipo(titulo + " " + descricao)
            
            if not edital_ano:
                return None
            
            return {
                "numero": numero,
                "titulo": titulo,
                "descricao": descricao,
                "ano": edital_ano,
                "tipo": edital_tipo,
                "pdf_url": pdf_url,
                "fonte": "ANEEL Portal",
                "data_coleta": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.warning(f"Erro ao parsear linha de edital: {e}")
            return None
    
    async def _scrape_internet_archive(
        self,
        ano: Optional[int],
        tipo: Optional[str]
    ) -> list:
        """Fallback para Internet Archive (Wayback Machine)."""
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                self.ARCHIVE_URL,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        editais = []
        
        for link in soup.find_all("a", href=lambda x: x and "edital" in x.lower()):
            href = link.get("href", "")
            text = link.get_text()
            
            edital = {
                "titulo": text,
                "pdf_url": href if href.startswith("http") else f"https://web.archive.org{href}",
                "fonte": "Internet Archive",
                "data_coleta": datetime.now().isoformat()
            }
            
            # Tentar extrair ano e tipo
            edital["ano"] = self._extract_ano(text)
            edital["tipo"] = self._extract_tipo(text)
            
            editais.append(edital)
        
        return editais
    
    @staticmethod
    def _extract_ano(texto: str) -> Optional[int]:
        """Extrai ano do texto."""
        import re
        match = re.search(r"(20\d{2})", texto)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def _extract_tipo(texto: str) -> Optional[str]:
        """Extrai tipo (LT/SE/Ampliação) do texto."""
        texto_upper = texto.upper()
        if "LINHA" in texto_upper or "LT" in texto_upper:
            return "LT"
        elif "SUBESTAÇÃO" in texto_upper or "SE" in texto_upper:
            return "SE"
        elif "AMPLIAÇÃO" in texto_upper:
            return "Ampliação"
        return None
    
    def _load_cache(self):
        """Carrega cache do disco."""
        cache_file = self.CACHE_DIR / "editais_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    self._cache = {
                        k: {
                            **v,
                            "timestamp": datetime.fromisoformat(v["timestamp"])
                        }
                        for k, v in data.items()
                    }
                logger.info(f"Cache carregado: {len(self._cache)} entradas")
            except Exception as e:
                logger.warning(f"Erro ao carregar cache: {e}")
    
    def _save_cache(self, key: str, data: list):
        """Salva cache no disco."""
        self._cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
        
        cache_file = self.CACHE_DIR / "editais_cache.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(
                    {
                        k: {
                            **v,
                            "timestamp": v["timestamp"].isoformat()
                        }
                        for k, v in self._cache.items()
                    },
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
```

---

### Integração em `backends/mcp/app/server.py`

```python
from aneel_scraper import ANEELEditalScraper

# No lifespan startup:
aneel_scraper = ANEELEditalScraper()

# Tools adicionadas:
@mcp.tool()
async def list_editais_transmissao(
    ano: Optional[int] = None,
    tipo: Optional[str] = None,
    limit: int = 50
) -> dict:
    """
    Lista editais de transmissão da ANEEL.
    
    Args:
        ano: Filtrar por ano (ex: 2024)
        tipo: Filtrar por tipo ("LT", "SE", "Ampliação")
        limit: Limite de resultados
    
    Returns:
        dict com "editais": list[{numero, titulo, ano, tipo, pdf_url}]
    """
    editais = await aneel_scraper.buscar_editais(ano=ano, tipo=tipo)
    return {
        "editais": editais[:limit],
        "total": len(editais),
        "anos_disponiveis": sorted(set(e.get("ano") for e in editais if e.get("ano"))),
        "tipos_disponiveis": sorted(set(e.get("tipo") for e in editais if e.get("tipo")))
    }
```

---

## SOLUÇÃO 2: CKAN API (Quando bloqueio for levantado)

### Arquivo: `backends/mcp/app/aneel_ckan.py`

```python
"""
Cliente CKAN para ANEEL Open Data.
Implementar quando proxy permitir acesso a dadosabertos.aneel.gov.br
"""

import httpx
from typing import Optional, List

class ANEELCKANClient:
    """Cliente CKAN para portal ANEEL Open Data."""
    
    BASE_URL = "https://dadosabertos.aneel.gov.br/api/3/action"
    
    async def package_search(
        self,
        q: str,
        rows: int = 50,
        sort: str = "metadata_created desc"
    ) -> dict:
        """Busca pacotes (datasets) por palavra-chave."""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/package_search",
                params={
                    "q": q,
                    "rows": rows,
                    "sort": sort,
                    "fq": "organization:aneel"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def resource_search(
        self,
        query: str,
        limit: int = 100
    ) -> dict:
        """Busca recursos (arquivos) por palavra-chave."""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/resource_search",
                params={
                    "query": query,
                    "limit": limit
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def package_show(self, package_id: str) -> dict:
        """Obtém detalhes de um pacote específico."""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/package_show",
                params={"id": package_id}
            )
            response.raise_for_status()
            return response.json()
```

---

## SOLUÇÃO 3: Cache com Atualização Periódica

### Arquivo: `backends/mcp/app/aneel_background.py`

```python
"""
Tasks background para atualizar cache de editais.
Executa diariamente às 06:00 AM.
"""

import asyncio
from datetime import datetime, time
from aneel_scraper import ANEELEditalScraper

async def refresh_aneel_cache():
    """Refresh cache de editais ANEEL."""
    scraper = ANEELEditalScraper()
    
    logger.info("Iniciando refresh de cache ANEEL...")
    
    try:
        # Buscar editais de todos os anos recentes
        for ano in [2024, 2025, 2026]:
            editais = await scraper.buscar_editais(ano=ano)
            logger.info(f"Carregado {len(editais)} editais de {ano}")
        
        logger.info("Cache ANEEL atualizado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao atualizar cache ANEEL: {e}")

async def schedule_aneel_refresh():
    """Schedule daily refresh às 06:00 AM."""
    while True:
        now = datetime.now()
        target = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        if now > target:
            # Próximo dia
            target = target.replace(day=target.day + 1)
        
        wait_seconds = (target - now).total_seconds()
        
        await asyncio.sleep(wait_seconds)
        await refresh_aneel_cache()

# No FastMCP lifespan:
# asyncio.create_task(schedule_aneel_refresh())
```

---

## Instalação de Dependências

### Adicionar a `backends/mcp/requirements.txt`:

```
httpx>=0.24.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
```

---

## Testes

### Arquivo: `tests/mcp/test_aneel_scraper.py`

```python
"""Testes para scraper ANEEL."""

import pytest
from unittest.mock import patch, AsyncMock
from aneel_scraper import ANEELEditalScraper

@pytest.mark.asyncio
async def test_buscar_editais_cache():
    """Verifica se cache é utilizado corretamente."""
    scraper = ANEELEditalScraper()
    
    with patch.object(scraper, '_scrape_aneel_portal', new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = [
            {
                "numero": "001",
                "titulo": "Edital nº 001/2024/ANEEL/SRT",
                "ano": 2024,
                "tipo": "LT"
            }
        ]
        
        # Primeira chamada
        result1 = await scraper.buscar_editais(ano=2024)
        assert len(result1) == 1
        assert mock_scrape.call_count == 1
        
        # Segunda chamada (deve usar cache)
        result2 = await scraper.buscar_editais(ano=2024)
        assert result1 == result2
        assert mock_scrape.call_count == 1  # Não chamou novamente
```

---

## Configuração (env vars)

### Adicionar a `.env.example`:

```
# ANEEL Editais
ANEEL_SCRAPER_ENABLED=true
ANEEL_CACHE_TTL_HOURS=24
ANEEL_CACHE_DIR=/tmp/manta/aneel_cache
ANEEL_REFRESH_HOUR=6
ANEEL_TIMEOUT_SECONDS=30
```

---

## Próximos Passos

1. Implementar `SOLUÇÃO 1` (Scraper HTML) imediatamente
2. Adicionar ao agente-energia com prompts para
   - "Quais são os editais de transmissão de 2024?"
   - "Encontre a LT 500 kV no edital 001/2024"
   - "Baixe o Termo de Referência do edital..."
3. Integrar com extrator de PDFs (Claude vision) para parsing automático
4. Migrar para `SOLUÇÃO 2` (CKAN API) quando proxy permitir

---

## Monitoramento

```python
# Logging estruturado
logger.info("Scraper ANEEL iniciado", extra={
    "editais_count": len(editais),
    "anos": [e["ano"] for e in editais],
    "fonte": editais[0]["fonte"] if editais else None
})

# Métricas
metrics.increment("aneel.editais.scrape_count")
metrics.timing("aneel.editais.scrape_duration_ms", duration)
```

