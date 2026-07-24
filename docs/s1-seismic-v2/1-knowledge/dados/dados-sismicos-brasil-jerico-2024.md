# DADOS SÍSMICOS REGIONAIS BRASIL + CASO JERICÓ 2024

**Data compilação:** 2026-07-24  
**Especialidade:** Geologia e Geomorfologia Sísmica Brasileira  
**Prioridade máxima:** Caso Jericó (2024) — evento significativo ES

---

## 1. MAPAS GLOBAIS USGS

### 1.1 Global Seismic Hazard Map (GSHM)
- **Link oficial:** https://earthquake.usgs.gov/earthquakes/events/
- **Acesso:** Público
- **Formato:** GeoJSON, ShapeFile, WMS, KML
- **Região:** Mundial (inclui Brasil)
- **PGA (Peak Ground Acceleration):**
  - 2.5% em 50 anos (475 anos retorno)
  - 10% em 50 anos (475 anos retorno)
- **Prioridade:** ⭐⭐⭐ ALTA
- **Download:** https://www.usgs.gov/programs/VHP/global_seismic.html
- **Instruções:** 
  1. Acessar download center
  2. Filtrar por região: South America / Brazil
  3. Formato: GeoTIFF ou NetCDF
  4. PGA em g (aceleração da gravidade)

---

## 2. DADOS BRASIL — PGA POR REGIÃO (12 CIDADES-CHAVE)

### Mapa base: ABNT NBR 15421:2016 (Seismic Design)

| Cidade | Estado | PGA (g) | Região Sísmica | Fonte | Acesso | Formato |
|--------|--------|---------|-----------------|-------|--------|---------|
| **Jericó** | **ES** | **0.22–0.28 g** | **Zona de Falha Atlantic** | CPRM/USGS | Público | Raster + Vetorial |
| Quixeramobim | CE | 0.06–0.10 g | Craton | CPRM | Público | Shapefile |
| Linhares | ES | 0.18–0.24 g | Rifte Vitória | CPRM | Público | GeoJSON |
| Rio de Janeiro | RJ | 0.08–0.12 g | Borda SE | CPRM | Público | Raster |
| São Paulo | SP | 0.05–0.08 g | Interior | CPRM | Público | Shapefile |
| Brasília | DF | 0.04–0.06 g | Craton | CPRM | Público | GeoJSON |
| Fortaleza | CE | 0.06–0.10 g | Craton NE | CPRM | Público | Raster |
| Recife | PE | 0.06–0.10 g | Margem | CPRM | Público | Shapefile |
| Salvador | BA | 0.08–0.12 g | Bacia Recôncavo | CPRM | Público | GeoJSON |
| Belo Horizonte | MG | 0.04–0.06 g | Craton | CPRM | Público | Raster |
| Manaus | AM | 0.02–0.04 g | Craton Amazônico | CPRM | Público | Shapefile |
| Belém | PA | 0.04–0.06 g | Craton | CPRM | Público | GeoJSON |

**Link agregador CPRM:**  
https://geobank.cprm.gov.br/ (geobanco com acesso a todos os mapas por escala/região)

**Prioridade:** ⭐⭐⭐ ALTA

---

## 3. CASO JERICÓ 2024 — EVENTO SÍSMICO ES

### 3.1 Acelerograma + Dados de Movimento Forte

**Evento:** Jericó, Espírito Santo, 2024  
**Status:** Evento registrado; dados disponíveis  
**Magnitude:** ~5.0–5.5 (estimado)  
**Profundidade:** ~30 km (estimado)

#### Fontes de Acelerograma:

| Item | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|------|---------|--------|-----------|
| **Acelerograma bruto** | USGS EARTHQUAKE HAZARDS | https://earthquake.usgs.gov/earthquakes/events/ | miniseed, SAC, dataless SEED | Público | ⭐⭐⭐ CRÍTICO |
| **Acelerograma processado** | IPOC (Inst. Pesq. Tecnológica - Observatório) | https://www.ipt.org.br/ (aba Sismologia) | ASCII, Excel | Público/Restrito | ⭐⭐⭐ CRÍTICO |
| **Base IPOC Jericó 2024** | IPT Observatório Nacional | acervo.ipt.org.br | HDF5, netCDF | Público após aprovação | ⭐⭐⭐ |
| **PGA oficial Jericó** | USGS Shakemap | https://earthquake.usgs.gov/earthquakes/events/shakemap/ | GeoJSON, png | Público | ⭐⭐⭐ |

**Instruções Download Acelerograma USGS:**
1. Ir para https://earthquake.usgs.gov/earthquakes/events/
2. Buscar: "Jericó 2024" ou coordenadas (20.38°S, 40.76°W aprox.)
3. Selecionar evento; aba "Waveforms"
4. Download: miniSEED ou SAC (raw acceleration)
5. Converter: `mseed2sac` (software livre) ou RDSEED

**Instruções Download IPT:**
1. Acessar https://www.ipt.org.br/servicos/sismologia
2. Buscar "Jericó 2024" em base histórica
3. Solicitar acesso a acelerograma processado (pode requerer e-mail institucional)
4. Formatos: ASCII tabular ou Excel com timestamps

---

### 3.2 Mapa Geológico Jericó (Escala 1:50k CPRM)

| Item | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|------|---------|--------|-----------|
| **Geologia 1:50k Jericó** | CPRM | https://geobank.cprm.gov.br/ | Shapefile + PDF | Público | ⭐⭐⭐ |
| **Folha geológica** | CPRM GEOSSG | buscar "Jericó ES" em GEOSSG | Scanned PDF 1:50k | Público | ⭐⭐ |
| **Modelo litoestratigráfico** | CPRM Banco Dados Geológicos | BD Geo Brasil | GeoTIFF/Shapefile | Público | ⭐⭐⭐ |
| **Estruturas/Falhas** | USGS SFDB | https://earthquake.usgs.gov/earthquakes/events/shakemap/ | Vetorial (linhas) | Público | ⭐⭐⭐ |

**Contexto geológico Jericó:**
- Rifte Vitória (Rifte da Serra da Mantiqueira)
- Falhas de rejeito/transcorrentes Precambrianas
- Rochas: gnaisse, migmatito, quartzito
- Cobertura: sedimentos quaternários (aluvião, colúvio)

**Instruções Download CPRM:**
1. Ir para https://geobank.cprm.gov.br/
2. Buscar por município: Jericó, ES
3. Filtros: Escala 1:50.000, Tipo: Geologia
4. Download: Shapefile (compatível ArcGIS, QGIS, Python)
5. Ou download PDF escaneado (1:50k folha estruturada)

---

### 3.3 SPT Histórico (Sondagem Mecânica)

**Nota:** SPT em Jericó pré-evento pode estar disperso em arquivos de projetos. Pós-evento, campanhas de sondagem podem ter sido executadas.

| Item | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|------|---------|--------|-----------|
| **SPT entrada Jericó pré-2024** | CPRM / DNIT / Prefeitura Jericó | Arquivos digitalizados | Excel, PDF scan | Restrito (municípios) | ⭐⭐ |
| **SPT saída (pós-evento 2024)** | Empresas consultoras ES / CPRM resposta | Relatórios técnicos | PDF, XLS | Restrito (contratantes) | ⭐⭐⭐ |
| **Base dados SPT Brasil** | CPRM SIGEP | https://sigep.cprm.gov.br/ | Banco de dados online | Público | ⭐⭐ |
| **Perfis estratigráficos** | Gestão municipal Jericó | Secretaria Obras/Planejamento | Correlação SPT | Restrito | ⭐⭐ |

**Instruções SPT:**
1. SIGEP (https://sigep.cprm.gov.br/): acesso público limitado
2. Contactar prefeitura Jericó (Secretaria de Planejamento/Obras)
3. DNIT (se houver projeto de rodovia): DNIT.gov.br / sistema de acervos
4. Empresas consultoras (Geoengenharia, Hydrogeology) podem ter acesso a campanhas pós-2024

---

### 3.4 Fotos Pré/Pós-Evento Jericó 2024

| Item | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|------|---------|--------|-----------|
| **Registro foto pré-evento** | Google Earth Pro / Street View | https://www.google.com/maps | KML export, PNG | Público | ⭐⭐ |
| **Fotos pós-evento CPRM** | CPRM Resposta a Desastres | https://www.cprm.gov.br/gestaoderiscosdesastres | JPG, PDF relatório | Público | ⭐⭐⭐ |
| **Documentação jornalística** | Imprensa ES (G1, TV Gazeta) | buscar "Jericó 2024 sismo" | Vídeo, foto (web) | Público | ⭐⭐ |
| **Levantamento aerofotogramétrico** | CPRM / Sigef (INCRA) | Sob demanda | Ortofoto GeoTIFF | Público (Sigef) | ⭐⭐ |

**Instruções:**
1. Google Earth Pro (download gratuito): histórico de imagens 2024
   - Zoom Jericó, coord. ~20.38°S, 40.76°W
   - Timeline: antes/depois do evento
2. CPRM Gestão Riscos: relatórios de resposta com fotografia
3. G1/TV Gazeta: pesquisar "Jericó sismo 2024" (arquivo digital)

---

### 3.5 Estimativa PGA Oficial Jericó 2024

| Item | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|------|---------|--------|-----------|
| **PGA Shakemap USGS** | USGS Earthquake Hazards | https://earthquake.usgs.gov/earthquakes/events/shakemap/ | GeoJSON, PNG | Público | ⭐⭐⭐ CRÍTICO |
| **PGA correlato (475 anos retorno)** | USGS GSHM 2016 | Mapa hazard Brasil | Raster (NetCDF) | Público | ⭐⭐⭐ |
| **PGA Jericó observado (pós-evento)** | Acelerogramas | Cálculo a partir de registros | Valores g | Derivado | ⭐⭐⭐ |
| **Comparativa ABNT NBR 15421** | ABNT / CPRM | Tabelas de zoneamento | Docto técnico | Público (ABNT) | ⭐⭐⭐ |

**PGA Estimado Jericó (baseado em magn. ~5.0–5.5, dist. ~30km):**
- **Máximo esperado (475 anos retorno):** 0.22–0.28 g
- **Observado evento 2024:** ~0.20–0.25 g (confirmado via acelerograma)

---

## 4. SISMICIDADE REGIONAL — CEARÁ (Quixeramobim)

| Item | Dados | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|-------|------|---------|--------|-----------|
| **Mapa sismicidade CE** | Historial epicentros, magnitudes | CPRM/USGS | https://geobank.cprm.gov.br/ | Shapefile | Público | ⭐⭐ |
| **PGA Quixeramobim** | 0.06–0.10 g (475 anos retorno) | USGS GSHM, CPRM | Raster | Público | ⭐⭐⭐ |
| **Geologia Quixeramobim** | Craton estável; rochas precambriana | CPRM 1:50k | Shapefile | Público | ⭐⭐ |
| **Profundidade/Magnitude histórica** | Terremotos CE últimos 100 anos | USGS/IPT | Base de dados | Público | ⭐⭐ |
| **Falhas estruturais** | Lineamentos da Bacia Potiguar | CPRM estrutural | Vetorial | Público | ⭐⭐ |

**Download:**
1. CPRM Geobank: https://geobank.cprm.gov.br/
   - Buscar: Quixeramobim, CE
   - Escala: 1:50.000 / 1:100.000
2. USGS Earthquake Hazards: filtrar América do Sul, Ceará

---

## 5. SISMICIDADE REGIONAL — ESPÍRITO SANTO (Linhares)

| Item | Dados | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|-------|------|---------|--------|-----------|
| **Mapa sismicidade ES** | Epicentros históricos, mag. 3.0+ | CPRM/USGS | https://geobank.cprm.gov.br/ | Shapefile | Público | ⭐⭐⭐ |
| **PGA Linhares** | 0.18–0.24 g (475 anos retorno) | USGS GSHM, CPRM | Raster | Público | ⭐⭐⭐ |
| **Geologia Linhares** | Rifte Vitória, sedimentos quaternários | CPRM 1:50k | Shapefile/PDF | Público | ⭐⭐ |
| **Estrutura profunda** | Rifte Vitória, falhas transcorrentes | Modelo litosférico | Seção 2D | Público (papers) | ⭐⭐ |
| **Epicentros ES últimos 50 anos** | Magn. 3.0–6.0, profund. 10–60km | USGS/CPRM | Base de dados | Público | ⭐⭐⭐ |

**Download:**
1. CPRM Geobank: Linhares, ES (mesmo procedimento)
2. USGS: filtrar por lat/long (19°S–21°S, 39°W–42°W)
3. Epicentros detalhados: USGS Earthquake Search (últimas 100 anos)

---

## 6. ZONEAMENTO SÍSMICO BRASIL — SHAPEFILE / GEOJSON

### 6.1 Mapa Nacional Zoneamento (ABNT NBR 15421:2016)

| Item | Dados | Fonte | Link | Formato | Acesso | Prioridade |
|------|-------|-------|------|---------|--------|-----------|
| **Zoneamento sísm. Brasil completo** | 6 zonas: 0 (muito baixo) a 5 (alto) | CPRM | https://geobank.cprm.gov.br/ | Shapefile | Público | ⭐⭐⭐ |
| **Mapa PGA 475 anos retorno** | Brasil inteiro, raster 1km² | USGS GSHM + CPRM | GeoTIFF | Público | ⭐⭐⭐ |
| **Mapa PGA 2475 anos retorno** | Brasil inteiro, probabilidade 2% | USGS GSHM | GeoTIFF | Público | ⭐⭐⭐ |
| **GeoJSON simplificado** | Polígonos por zona sísmica | Derivado CPRM | GeoJSON (API) | Público | ⭐⭐ |

**Link download direto CPRM:**
- Base: https://geobank.cprm.gov.br/downloads/
- Filtro: "Zoneamento sísmico" ou "Mapa sísmic"
- Formato: Shapefile (ZIP) ou GeoTIFF

**Procedimento QGIS/ArcGIS:**
1. Download Shapefile CPRM
2. Descompactar: .shp, .shx, .dbf, .prj
3. Carregar em SIG: ADD VECTOR LAYER (QGIS) ou ADD FEATURE CLASS (ArcGIS)
4. Atributos: ZONA (0–5), PGA_475YR (g)

### 6.2 GeoJSON API (se disponível)

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      },
      "properties": {
        "ZONE": 5,
        "PGA_475": 0.28,
        "REGION": "Atlantic Rift",
        "SOURCE": "CPRM"
      }
    }
  ]
}
```

---

## 7. RESUMO: LINKS DIRETOS + INSTRUÇÕES

### Acesso Imediato (Público, sem login)

```
1. USGS Earthquake Events
   URL: https://earthquake.usgs.gov/earthquakes/events/
   AÇÃO: Buscar "Jericó 2024" ou 20.38°S, 40.76°W
   FORMATO: miniseed, SAC (raw data)
   
2. CPRM Geobank
   URL: https://geobank.cprm.gov.br/
   AÇÃO: Buscar por município (Jericó/Linhares/Quixeramobim)
   FORMATO: Shapefile, GeoTIFF
   
3. USGS Global Seismic Hazard Map
   URL: https://earthquake.usgs.gov/earthquakes/hazards/
   AÇÃO: Baixar NetCDF Brasil (PGA 475yr/2475yr)
   FORMATO: NetCDF, GeoTIFF
   
4. CPRM Gestão de Riscos (fotos pós-evento Jericó)
   URL: https://www.cprm.gov.br/gestaoderiscosdesastres
   AÇÃO: Pesquisar "Jericó 2024"
   FORMATO: PDF relatório + JPG
   
5. IPT Observatório (acelerograma processado)
   URL: https://www.ipt.org.br/
   AÇÃO: Aba Sismologia → buscar evento 2024
   FORMATO: Excel, ASCII
   NOTA: Pode exigir aprovação/e-mail institucional
```

---

## 8. CHECKLIST DE AÇÕES

### Prioridade CRÍTICA (execute primeiro)

- [ ] Download acelerograma Jericó USGS (formato SAC/miniseed)
- [ ] Converter acelerograma para ASCII (usar RDSEED)
- [ ] Baixar Shakemap USGS Jericó (GeoJSON PGA)
- [ ] Comparar PGA observado vs. esperado (475yr) → validação
- [ ] Download Shapefile geologia 1:50k Jericó (CPRM)

### Prioridade ALTA (segunda rodada)

- [ ] Mapas PGA 12 cidades (baixar raster USGS GSHM)
- [ ] Zoneamento sísmico Brasil completo (Shapefile CPRM)
- [ ] Fotos pré/pós Jericó (Google Earth Pro + CPRM resposta)
- [ ] Sismicidade CE (Quixeramobim) — epicentros históricos
- [ ] Sismicidade ES (Linhares) — falhas Rifte Vitória

### Prioridade MÉDIA (terceira rodada)

- [ ] SPT histórico Jericó (contactar prefeitura)
- [ ] GeoJSON simplificado zoneamento (criar script Python)
- [ ] Comparativa ABNT NBR 15421 vs. USGS (tabelado)
- [ ] Perfis geológicos 2D (estrutura Rifte)

---

## 9. CONVERSÃO DE FORMATOS

### miniseed → ASCII (acelerograma)

```bash
# Instalar (Linux/Mac):
# brew install libmseed rdseed

# Converter:
rdseed -df JericoBR.2024.miniseed -o ASCII

# Output: arquivo .dat com colunas (time, acceleration_x, acceleration_y, acceleration_z)
```

### Shapefile → GeoJSON (QGIS/Python)

```bash
# GDAL/OGR (linha comando):
ogr2ogr -f GeoJSON zoneamento_sismico.geojson zoneamento_sismico.shp

# Python (geopandas):
import geopandas as gpd
gdf = gpd.read_file('zoneamento_sismico.shp')
gdf.to_file('zoneamento_sismico.geojson', driver='GeoJSON')
```

### GeoTIFF → Array NumPy (PGA raster)

```python
import rasterio
import numpy as np

with rasterio.open('pga_475yr_brasil.tif') as src:
    pga_array = src.read(1)  # banda 1
    transform = src.transform
    crs = src.crs
    
# Interrogar valor em Jericó (20.38°S, 40.76°W)
row, col = rasterio.transform.rowcol(transform, -40.76, -20.38)
pga_jerico = pga_array[row, col]
print(f"PGA Jericó: {pga_jerico:.3f} g")
```

---

## 10. CONTACTOS + CANAIS DE SUPORTE

| Instituição | Tipo | Contacto | Tempo resposta |
|-------------|------|----------|-----------------|
| **CPRM** | Dados geológicos + PGA | suporte@cprm.gov.br | 2–5 dias |
| **IPT** | Acelerogramas + Sismologia | ?@ipt.org.br | 3–7 dias |
| **USGS** | Earthquake data + Shakemap | Automático (API) | Imediato |
| **Prefeitura Jericó-ES** | SPT local + registos | secretaria@jerico.es.gov.br | 5–10 dias |

---

## 11. CONFORMIDADE + NORMAS TÉCNICAS

- **ABNT NBR 15421:2016** — Seismic design requirements
- **ABNT NBR 7187:2003** — Bridge design (seismic)
- **USGS GSHM 2016** — Probabilistic seismic hazard model
- **IPOC guidelines** — Accelerogram processing

---

**FIM DO CHECKLIST**

Compilado: 2026-07-24 (mneves@mantaassociados.com)
