# NOTAS TÉCNICAS DETALHADAS — Saneamento Tier 1 Ingestion
## Code Patterns, Blockers & Mitigations

---

## 1. SNIS 2024 — Transição SNIS → SINISA

### Blocker Principal: Inconsistência de Dados em 2023–2024

A Lei 14.026/2020 introduziu novos indicadores em 2024 via **SINISA** (Sistema Nacional de Informações sobre Segurança de Abastecimento), substituindo o SNIS. Possíveis problemas:

```
2023 SNIS: 5.565 municípios, 42 indicadores
         ↓ (transição)
2024 SINISA: 5.565 municípios, 48 indicadores (novos: "segurança_agua_dias_falta", etc.)

Risco: Mesmo município pode ter 2023 com "cobertura_agua = 85%" e dados não-comparáveis
```

### Mitigação: Validação de Overlaps

```python
# snis_validator.py
import pandas as pd
import hashlib

class SNISTransitionValidator:
    def __init__(self):
        self.snis_2023 = None
        self.sinisa_2024 = None
    
    def load_data(self):
        # Baixar série histórica SNIS até 2023
        self.snis_2023 = pd.read_csv("snis_1995_2023.csv")
        # Baixar SINISA 2024
        self.sinisa_2024 = pd.read_csv("sinisa_2024.csv")
    
    def validate_overlap(self):
        """Validar 2023 em ambos os sistemas"""
        snis_2023_only = self.snis_2023[self.snis_2023['ano'] == 2023]
        sinisa_2023 = self.sinisa_2024[self.sinisa_2024['ano'] == 2023]
        
        if snis_2023_only.empty or sinisa_2023.empty:
            print("⚠️ Nenhum overlap encontrado — possível gap em 2023")
            return False
        
        # Validação de checksum
        snis_sum = snis_2023_only['cobertura_agua'].sum()
        sinisa_sum = sinisa_2023['cobertura_agua'].sum()
        
        delta = abs(snis_sum - sinisa_sum) / max(snis_sum, sinisa_sum)
        if delta > 0.05:  # >5% de desvio
            print(f"🔴 INCONSISTÊNCIA: {delta*100:.2f}% de desvio em cobertura_agua 2023")
            return False
        
        print("✅ Transição validada")
        return True
    
    def mark_metadata(self, df):
        """Adicionar coluna de provenance"""
        df['fonte_sistema'] = df['ano'].apply(
            lambda x: 'SINISA' if x >= 2024 else ('SNIS_2023_compat' if x == 2023 else 'SNIS')
        )
        return df
```

### Impacto em Chunking

Ao criar chunks para RAG, flaggar com metadada `sistema: "SNIS" | "SINISA" | "SNIS_2023_compat"`.
Queries que cruzam 2023–2024 devem alertar ao usuário sobre possível inconsistência.

---

## 2. Lei 14.026/2020 — Estruturação de Texto Jurídico

### Parsing de Artigos com Regex

```python
# lei_parser.py
import requests
from bs4 import BeautifulSoup
import re

def parse_lei_14026():
    """Fetch Lei 14.026 do Planalto e estruturar por artigos"""
    
    url = "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2020/lei/l14026.htm"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Planalto estrutura em <p> tags
    artigos = []
    article_text = ""
    current_article = None
    
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        
        # Regex: "Art. 1" ou "Art. 1º"
        match = re.match(r"^Art\.\s*(\d+)", text)
        if match:
            if current_article:  # Salvar artigo anterior
                artigos.append({
                    'numero': current_article,
                    'texto': article_text.strip()
                })
            current_article = match.group(1)
            article_text = text
        else:
            article_text += " " + text
    
    # Salvar último artigo
    if current_article:
        artigos.append({
            'numero': current_article,
            'texto': article_text.strip()
        })
    
    return artigos

# Teste
for art in parse_lei_14026():
    print(f"Art. {art['numero']}: {art['texto'][:100]}...")
    
    # Detectar menções a RAP, subsídios, ANA
    if "RAP" in art['texto'] or "Regime de Ações Planejadas" in art['texto']:
        print("  → Menciona RAP")
    if "subsídio" in art['texto'].lower():
        print("  → Menciona subsídios cruzados")
    if "ANA" in art['texto']:
        print("  → Menciona ANA (Agência Nacional de Águas)")
```

### Chunking Strategy

Para Lei 14.026, cada artigo é um natural boundary. Chunking recomendado:

```python
# lei_chunking.py
def chunk_lei_14026(artigos, chunk_size=400):
    """
    Chunking por artigo, com fallback para multi-artigo se artigo muito pequeno.
    Alvo: 400 tokens ≈ 1600 chars.
    """
    chunks = []
    buffer = ""
    
    for art in artigos:
        art_text = f"Art. {art['numero']}\n{art['texto']}"
        
        if len(art_text) <= 1600:
            # Artigo pequeno, tentar mergear com próximo
            buffer += "\n\n" + art_text
        else:
            # Artigo grande, chunkar internamente
            if buffer:
                chunks.append({
                    'texto': buffer.strip(),
                    'tipo': 'multi-artigo',
                    'tokens_estimado': len(buffer) // 4  # rough estimate
                })
                buffer = ""
            
            # Chunkar artigo grande
            sub_chunks = chunk_text(art_text, target_tokens=400)
            for i, sub in enumerate(sub_chunks):
                chunks.append({
                    'texto': sub,
                    'tipo': 'intra-artigo',
                    'artigo': art['numero'],
                    'sub_chunk': i,
                    'tokens_estimado': len(sub) // 4
                })
    
    return chunks

def chunk_text(text, target_tokens=400):
    """Chunkar por sentenças até atingir target_tokens"""
    import nltk
    nltk.download('punkt')
    sentences = nltk.sent_tokenize(text, language='portuguese')
    
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) <= target_tokens * 4:  # rough estimate
            current += " " + sent
        else:
            if current:
                chunks.append(current.strip())
            current = sent
    
    if current:
        chunks.append(current.strip())
    
    return chunks
```

---

## 3. ANA PMSB — WFS + Crawler Distribuído

### WFS Discovery Pattern

```python
# pmsb_wfs.py
import requests
import json
from xml.etree import ElementTree as ET

class PMSBWFSClient:
    def __init__(self):
        self.base_url = "https://geoinfo.dados.embrapa.br/geoserver/ows"
        self.crs = "EPSG:4326"
    
    def get_capabilities(self):
        """WFS GetCapabilities para descobrir layers"""
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetCapabilities'
        }
        r = requests.get(self.base_url, params=params, timeout=30)
        root = ET.fromstring(r.content)
        
        layers = []
        # Namespace WFS
        ns = {'wfs': 'http://www.opengis.net/wfs/2.0.0'}
        for ft in root.findall('.//wfs:FeatureType', ns):
            name = ft.find('wfs:Name', ns).text
            title = ft.find('wfs:Title', ns).text if ft.find('wfs:Title', ns) else name
            
            layers.append({
                'name': name,
                'title': title,
                'type': 'Feature'
            })
        
        return layers
    
    def get_features(self, layer_name, start_index=0, page_size=500):
        """Fetch features com paginação"""
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': layer_name,
            'outputFormat': 'application/json',
            'startIndex': start_index,
            'count': page_size,
            'srsname': self.crs
        }
        
        try:
            r = requests.get(self.base_url, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()
            
            features = data.get('features', [])
            num_returned = len(features)
            num_matched = data.get('numberMatched', 'unknown')
            
            print(f"📍 {layer_name}: {num_returned}/{num_matched} features (start={start_index})")
            
            return features, num_matched
        
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT {layer_name} @ start_index={start_index}")
            return [], 0
        except requests.exceptions.HTTPError as e:
            print(f"🔴 HTTP {e.response.status_code} {layer_name}")
            return [], 0
    
    def fetch_all_pages(self, layer_name, page_size=500, max_retries=3):
        """Fetch todas as pages com retry"""
        all_features = []
        start_index = 0
        
        while True:
            retries = 0
            while retries < max_retries:
                try:
                    features, num_matched = self.get_features(layer_name, start_index, page_size)
                    break
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"❌ Max retries reached for {layer_name} @ {start_index}")
                        return all_features
                    print(f"  Retry {retries}/{max_retries}...")
            
            if not features:
                break
            
            all_features.extend(features)
            start_index += page_size
            
            # Estimado
            if num_matched != 'unknown' and start_index >= int(num_matched):
                break
        
        return all_features

# Uso
wfs = PMSBWFSClient()
layers = wfs.get_capabilities()
print(f"Descobertos {len(layers)} layers WFS")

# Harvest ETA (estações de tratamento de água)
eta_features = wfs.fetch_all_pages('ANA_Metadados:ETA_Localizacao', page_size=500)
print(f"✅ {len(eta_features)} ETAs baixadas")
```

### Blocker: PDF Scraper com OCR Fallback

```python
# pmsb_crawler.py
import os
import requests
import concurrent.futures
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
import hashlib

class PMSBCrawler:
    def __init__(self, output_dir="/tmp/pmsb", n_workers=100):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.n_workers = n_workers
        self.processed_urls = set()
        self.load_cache()
    
    def load_cache(self):
        """Carregar URLs já processadas"""
        cache_file = self.output_dir / ".processed_urls"
        if cache_file.exists():
            with open(cache_file) as f:
                self.processed_urls = set(line.strip() for line in f)
    
    def save_cache(self):
        """Salvar URLs processadas"""
        cache_file = self.output_dir / ".processed_urls"
        with open(cache_file, 'w') as f:
            for url in self.processed_urls:
                f.write(url + "\n")
    
    def download_pdf(self, municipio, url):
        """Baixar PDF com retry"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        if url_hash in self.processed_urls:
            print(f"⏭️  Skipped (cached): {municipio}")
            return None
        
        try:
            r = requests.get(url, timeout=30, allow_redirects=True)
            r.raise_for_status()
            
            pdf_path = self.output_dir / f"{municipio}_{url_hash}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(r.content)
            
            self.processed_urls.add(url_hash)
            return str(pdf_path)
        
        except requests.exceptions.Timeout:
            print(f"⏱️ TIMEOUT: {municipio}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"🔴 HTTP {e.response.status_code}: {municipio}")
            return None
    
    def extract_text_ocr(self, pdf_path):
        """
        Extrair texto do PDF com fallback OCR.
        CRÍTICO: 30% dos PMSB são scans.
        """
        try:
            # Tentar PyPDF primeiro (rápido)
            import pypdf
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            
            if len(text.strip()) > 100:
                return text, "pypdf"
        
        except Exception as e:
            print(f"  PyPDF falhou: {e}")
        
        # Fallback OCR
        print(f"  🔎 OCR fallback para {Path(pdf_path).name}")
        try:
            images = convert_from_path(pdf_path, dpi=150)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img, lang='por')
            
            if len(text.strip()) > 100:
                return text, "ocr_tesseract"
        
        except Exception as e:
            print(f"  ❌ OCR também falhou: {e}")
        
        return "", "none"
    
    def crawl_municipios(self, url_list):
        """
        Crawl distribuído com 100 workers paralelos.
        
        url_list: [
            {'municipio': 'São Paulo', 'url': 'http://...PMSB_SP.pdf'},
            ...
        ]
        """
        def process_municipio(item):
            municipio = item['municipio']
            url = item['url']
            
            pdf_path = self.download_pdf(municipio, url)
            if not pdf_path:
                return {'municipio': municipio, 'status': 'download_failed'}
            
            text, method = self.extract_text_ocr(pdf_path)
            
            return {
                'municipio': municipio,
                'pdf_path': pdf_path,
                'text_length': len(text),
                'extraction_method': method,
                'status': 'success' if len(text) > 100 else 'extraction_failed'
            }
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            futures = [executor.submit(process_municipio, item) for item in url_list]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                
                if (i + 1) % 100 == 0:
                    print(f"  ✅ {i+1} municípios processados")
        
        self.save_cache()
        return results

# Teste com amostra
crawler = PMSBCrawler()
sample_urls = [
    {'municipio': 'São Paulo', 'url': 'http://example.com/PMSB_SP.pdf'},
    {'municipio': 'Rio de Janeiro', 'url': 'http://example.com/PMSB_RJ.pdf'},
]
results = crawler.crawl_municipios(sample_urls)

success = sum(1 for r in results if r['status'] == 'success')
print(f"\n📊 Resultados: {success}/{len(results)} sucesso")
```

---

## 4. BNDES Editais — CKAN API + Tabula

### CKAN Package Search

```python
# bndes_editais.py
import requests
import json

class BNDESEditaisClient:
    def __init__(self):
        self.base_url = "https://dadosabertos.bndes.gov.br/api/3/action"
        self.session = requests.Session()
    
    def package_search(self, query="saneamento", rows=100, start=0):
        """CKAN package_search para listar editais"""
        url = f"{self.base_url}/package_search"
        params = {
            'q': f'org:bndes tags:{query}',
            'rows': rows,
            'start': start
        }
        
        r = self.session.get(url, params=params, timeout=30)
        data = r.json()
        
        if not data['success']:
            raise Exception(f"CKAN error: {data.get('error')}")
        
        return data['result']
    
    def harvest_all_editais(self):
        """Harvest iterativo com paginação"""
        all_editais = []
        start = 0
        rows = 50
        
        while True:
            result = self.package_search(start=start, rows=rows)
            editais = result.get('results', [])
            
            if not editais:
                break
            
            all_editais.extend(editais)
            print(f"📦 {len(all_editais)} editais descobertos")
            
            start += rows
            
            # Validação de totalização
            if start >= result.get('count', 0):
                break
        
        return all_editais
    
    def extract_resources(self, package):
        """Extrair URLs de recursos (PDFs, CSVs) de um pacote"""
        resources = []
        for res in package.get('resources', []):
            resources.append({
                'name': res.get('name'),
                'url': res.get('url'),
                'format': res.get('format'),
                'size': res.get('size'),
                'last_modified': res.get('last_modified')
            })
        return resources

# Uso
client = BNDESEditaisClient()
editais = client.harvest_all_editais()

print(f"\n✅ Total de {len(editais)} editais saneamento")

for edital in editais[:3]:
    print(f"\n📋 {edital['title']}")
    resources = client.extract_resources(edital)
    for res in resources[:3]:
        print(f"  - {res['name']}: {res['format']} ({res['size']} bytes)")
```

### Tabula: Extrair Tabelas de PDFs

```python
# bndes_tabula.py
import tabula
import os

def extract_tables_from_bndes_pdfs(pdf_dir="/tmp/bndes_pdfs", output_dir="/tmp/bndes_tables"):
    """Extrair tabelas de PDFs com Tabula"""
    os.makedirs(output_dir, exist_ok=True)
    
    for pdf_file in os.listdir(pdf_dir):
        if not pdf_file.endswith('.pdf'):
            continue
        
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"📄 Processando {pdf_file}...")
        
        try:
            # Tabula: detect todas as tabelas em todas as páginas
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                stream=True  # Mode stream para PDFs com layout complexo
            )
            
            print(f"  📊 {len(tables)} tabelas encontradas")
            
            # Salvar cada tabela como CSV
            for i, table in enumerate(tables):
                csv_path = os.path.join(output_dir, f"{pdf_file[:-4]}_table_{i}.csv")
                table.to_csv(csv_path, index=False)
        
        except Exception as e:
            print(f"  ⚠️ Erro ao processar {pdf_file}: {e}")
```

---

## 5. Teses — OAI-PMH Harvest

### OAI-PMH Client com ResumptionToken

```python
# oai_harvest.py
import requests
from xml.etree import ElementTree as ET
from datetime import datetime

class OAIHarvester:
    def __init__(self, oai_base_url, resumption_file=None):
        self.oai_url = oai_base_url
        self.resumption_file = resumption_file or ".oai_resumption"
        self.session = requests.Session()
    
    def list_records(self, metadata_prefix='oai_dc', from_date=None, until_date=None, 
                     set_spec=None, resumption_token=None):
        """
        OAI ListRecords com suporte a ResumptionToken.
        
        OAI-PMH v2.0 padrão: pagination via resumption tokens (not offset).
        """
        params = {
            'verb': 'ListRecords',
            'metadataPrefix': metadata_prefix
        }
        
        if resumption_token:
            params['resumptionToken'] = resumption_token
        else:
            if from_date:
                params['from'] = from_date
            if until_date:
                params['until'] = until_date
            if set_spec:
                params['set'] = set_spec
        
        r = self.session.get(self.oai_url, params=params, timeout=60)
        root = ET.fromstring(r.content)
        
        # Parse records
        records = []
        ns = {'oai': 'http://www.openarchives.org/OAI/2.0/'}
        
        for record in root.findall('.//oai:record', ns):
            header = record.find('oai:header', ns)
            if header is None or header.get('status') == 'deleted':
                continue  # Skip deleted records
            
            metadata = record.find('oai:metadata', ns)
            if metadata is None:
                continue
            
            dc = metadata.find('oai_dc:dc', {'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'})
            
            record_data = {
                'identifier': header.find('oai:identifier', ns).text,
                'datestamp': header.find('oai:datestamp', ns).text,
                'title': None,
                'author': None,
                'description': None,
                'url': None
            }
            
            if dc is not None:
                dc_ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
                title_elem = dc.find('dc:title', dc_ns)
                if title_elem is not None:
                    record_data['title'] = title_elem.text
                
                author_elem = dc.find('dc:creator', dc_ns)
                if author_elem is not None:
                    record_data['author'] = author_elem.text
                
                desc_elem = dc.find('dc:description', dc_ns)
                if desc_elem is not None:
                    record_data['description'] = desc_elem.text
                
                url_elem = dc.find('dc:identifier', dc_ns)
                if url_elem is not None:
                    record_data['url'] = url_elem.text
            
            records.append(record_data)
        
        # Extract next resumption token
        resumption = root.find('.//oai:resumptionToken', ns)
        next_token = resumption.text if resumption is not None else None
        
        return records, next_token
    
    def harvest_all(self, metadata_prefix='oai_dc', from_date='1980-01-01'):
        """Harvest iterativo com todos os records"""
        all_records = []
        resumption_token = None
        
        while True:
            print(f"📥 Harvest batch (token: {resumption_token[:20] if resumption_token else 'initial'}...)")
            
            try:
                records, next_token = self.list_records(
                    metadata_prefix=metadata_prefix,
                    from_date=from_date,
                    resumption_token=resumption_token
                )
            except requests.exceptions.Timeout:
                print("⏱️ TIMEOUT — salvando resumption token")
                if resumption_token:
                    with open(self.resumption_file, 'w') as f:
                        f.write(resumption_token)
                raise
            
            all_records.extend(records)
            print(f"  ✅ +{len(records)} records (total: {len(all_records)})")
            
            if not next_token:
                break
            
            resumption_token = next_token
            
            # Rate limit: respectar Retry-After se presente
            # time.sleep(1)  # Ser respeitoso com servidores OAI
        
        return all_records

# Uso: COPPE-UFRJ
harvester = OAIHarvester("https://pantheon.ufrj.br/oai/request")
records = harvester.harvest_all(from_date='2010-01-01')

print(f"\n✅ Total de {len(records)} teses harvested")

# Deduplicação por MD5 + DOI
import hashlib

def deduplicate(records):
    """Remover duplicatas entre repositórios"""
    seen = {}
    deduped = []
    
    for rec in records:
        # Tentarkey por DOI, ou URL, ou título
        doi = rec.get('identifier', '').split('/')[-1]
        url = rec.get('url', '')
        title = rec.get('title', '')
        
        key = doi or url or title
        key_hash = hashlib.md5(key.encode()).hexdigest()
        
        if key_hash not in seen:
            seen[key_hash] = rec
            deduped.append(rec)
    
    print(f"  Deduplication: {len(records)} → {len(deduped)} (removidas {len(records) - len(deduped)})")
    return deduped
```

---

## 6. AySA — Selenium + Google Translate

### Scraper com Headless Chrome

```python
# aysa_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class AySAScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
    
    def scrape_transparency_reports(self):
        """Scrape relatórios do portal de transparencia"""
        self.driver.get("https://www.aysa.com.ar/Quienes-Somos/Transparencia")
        
        # Aguardar carregamento
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@href*='pdf']"))
        )
        
        # Listar todos os links PDF
        pdf_links = []
        for link in self.driver.find_elements(By.XPATH, "//a[@href*='pdf']"):
            href = link.get_attribute('href')
            text = link.text
            pdf_links.append({
                'texto': text,
                'url': href
            })
        
        print(f"📄 {len(pdf_links)} PDFs encontrados")
        return pdf_links
    
    def scrape_data_api(self):
        """Fetch dados da API JSON data.aysa.com.ar"""
        import requests
        
        endpoints = [
            "https://data.aysa.com.ar/api/cobertura",
            "https://data.aysa.com.ar/api/proyectos",
            "https://data.aysa.com.ar/api/tarifas"
        ]
        
        data = {}
        for endpoint in endpoints:
            try:
                r = requests.get(endpoint, timeout=30)
                r.raise_for_status()
                key = endpoint.split('/')[-1]
                data[key] = r.json()
            except Exception as e:
                print(f"❌ Erro ao buscar {endpoint}: {e}")
        
        return data
    
    def close(self):
        self.driver.quit()

# Uso
scraper = AySAScraper()
pdf_links = scraper.scrape_transparency_reports()
data = scraper.scrape_data_api()
scraper.close()

# Tradução de relatórios (ESP → PT-BR)
from google.cloud import translate_v2

def translate_spanish_reports(pdf_texts, target_language='pt'):
    """Traduzir relatórios espanhol → português"""
    client = translate_v2.Client()
    
    translated = {}
    for name, text in pdf_texts.items():
        result = client.translate_text(text, target_language=target_language)
        translated[name] = result['translatedText']
    
    return translated
```

---

## RESUMO DE BLOCKERS POR FONTE

| Fonte | Blocker | Gravidade | Dias Mitigação |
|-------|---------|-----------|-----------------|
| SNIS | Transição SNIS/SINISA | 🔴 CRÍTICA | 3 |
| Lei 14.026 | Nenhum significativo | ✅ | 0 |
| PMSB | 30% scans sem OCR | 🔴 CRÍTICA | 5 |
| PMSB | 15% links quebrados | ⚠️ MODERADO | 2 |
| BNDES | PDFs scaneados | ⚠️ MODERADO | 1 |
| Teses | ~15% duplicatas | ⚠️ MODERADO | 2 |
| Teses | 200 teses pré-2005 não digitalizadas | ⚠️ MODERADO | 1 (nice-to-have) |
| AySA | Portal JavaScript dinâmico | ⚠️ MODERADO | 1 |

**Total de dias de mitigação:** ~15 dias (já inclusos no cronograma Phase 1a)

---

**Última atualização:** 2026-07-15  
**Próxima revisão:** Week 4 (2026-07-28)
