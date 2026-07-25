# S1 Integração Estratégica — Rodovias (Q4 2026 → Q2 2027)

**Documento**: Estratégia de Integração Técnica para Manta 03-S1 (agente-infraestrutura).  
**Data**: 2026-07-24  
**Versão**: 1.0 (DRAFT)  
**Proprietário**: Manta Associados — Arquiteto IA (Manta 16)  
**Status**: Pronto para aprovação de gate humano (MN)

---

## 1. VISÃO GERAL

A estratégia S1 visa integrar o agente-infraestrutura (Rodovias) com uma pilha técnica de processamento de design assistida por IA:

1. **DXF Input** — parsear arquivos nativos AutoCAD (ezdxf)
2. **Civil 3D Automation** — acesso a superfícies, alinhamentos, corredores via API
3. **LandXML Import** — carregar topografia e alinhamentos de levantamentos
4. **Allsite.ai Integration** — especialistas de domínio:
   - **Level AI** (rasante/greide de rodovia)
   - **Service AI** (sistemas de drenagem e obras-de-arte especiais)
5. **Output Delivery** — DXF normalizado + relatórios de verificação + playbooks operacionais

**Resultado esperado**: Redução de 40-60% do tempo de projeto básico e executivo de rodovias via automação inteligente de fluxos DXF → Civil 3D → análise → validação.

---

## 2. ARQUITETURA TÉCNICA

### 2.1 Pilha de Integração

```
┌─────────────────────────────────────────────────────────────┐
│  ENTRADA — Usuário (Engenheiro de Rodovias / S1)            │
│  Formato: DXF, PDF (projeto), LandXML (levantamento)        │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  PARSER LAYER (ezdxf)  │
        │  ├─ DXF parsing        │
        │  ├─ Entity extraction  │
        │  └─ Layer audit        │
        └────────────┬───────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  NORMALIZATION LAYER                │
        │  ├─ Layer normalization (CBR)       │
        │  ├─ Coordinate validation           │
        │  ├─ LandXML alignment merge         │
        │  └─ Surface SRT processing          │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  ANALYSIS LAYER                     │
        │  ├─ Level AI (rasante/greide)       │
        │  ├─ Service AI (drenagem/OAE)       │
        │  ├─ SICRO costing                   │
        │  └─ CBR geometry check              │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  GENERATION LAYER                   │
        │  ├─ Civil 3D Automation API         │
        │  ├─ Corridor assembly               │
        │  ├─ DXF sections generation         │
        │  └─ Report templates                │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  SAÍDA — Deliverables  │
        │  ├─ DXF (normatizado)  │
        │  ├─ Relatórios PDF     │
        │  ├─ Playbooks          │
        │  └─ Sinalizadores      │
        └────────────────────────┘
```

### 2.2 Componentes

| Componente | Tech Stack | Responsabilidade | Tempo Estimado |
|------------|------------|------------------|-----------------|
| **DXF Parser** | Python + ezdxf 1.2+ | Carregar, validar, extrair entities de DXF | Q4 2026 |
| **LandXML Importer** | lxml + XSD validator | Topografia (SRT), alinhamentos, pontos | Q4 2026 |
| **Level AI Bridge** | Allsite.ai API (async) | Rasante inteligente, validação CBR | Q1 2027 |
| **Service AI Bridge** | Allsite.ai API (async) | Drenagem, bueiros, obras-de-arte | Q1 2027 |
| **Civil 3D Automation** | Autodesk Automation API | Corridor, seções, superfícies VIK | Q2 2027 |
| **SICRO Connector** | Manta-SICRO (Redis cache) | Precificação de composições | Q4 2026 |
| **DXF Output** | ezdxf writer + CBR rules | Layer normalization (ABNT NBR 13142) | Q1 2027 |
| **Report Generator** | Jinja2 + ReportLab | Relatórios PDF, validação, compliance | Q1 2027 |

---

## 3. FLUXOS DE INTEGRAÇÃO

### 3.1 Fluxo DXF → Civil 3D → Análise

#### Fluxo-1: Parse & Validate DXF

**Input**: arquivo `rodovia-km0-km10.dxf`

**Etapas**:
1. **ezdxf.readfile()** → Document object
2. **Extract entities** por layer (ALINHAMENTO, PERFIL, SEÇÕES, DRENAGEM, OAE)
3. **Validate layer naming** contra CBR normalization (ABNT NBR 13142)
4. **Coordinate system detection** (UTM zona 23S vs. local vs. lat/long)
5. **Output**: Python dict com estrutura normalizada

**Pseudocódigo**:
```python
import ezdxf

dxf = ezdxf.readfile("rodovia-km0-km10.dxf")
roadway_data = {
    "alignment": extract_lwpolylines(dxf, "ALINHAMENTO"),
    "profile": extract_entities(dxf, "PERFIL"),
    "sections": extract_text_blocks(dxf, "SEÇÕES"),
    "drainage": extract_drainage_entities(dxf, "DRENAGEM"),
    "oae": extract_oae(dxf, "OAE"),
    "metadata": extract_metadata(dxf),
}
return roadway_data
```

**Tempo**: 5-15 min (consoante tamanho DXF)

---

#### Fluxo-2: LandXML Merge (Topografia + Alinhamento)

**Input**: 
- `levantamento.xml` (LandXML 1.2, origem GNSS/RTK ou voo drone)
- `alinhamento-civil3d.xml` (exported from Civil 3D)

**Etapas**:
1. **Parse LandXML** → Surface (SRT) + Alignment (horizontal + vertical PI)
2. **Merge SRT** com topografia existente em DXF (se houver)
3. **Validate alignment consistency** (horizontal vs. vertical curve PI)
4. **Calc stationing** (estaqueamento) desde km 0+0.00
5. **Output**: SRT unified + alignment in control format

**Pseudocódigo**:
```python
import xml.etree.ElementTree as ET
from lxml import etree

# Parse LandXML surface
srt_tree = etree.parse("levantamento.xml")
surface = extract_surface_from_landxml(srt_tree)  # → TIN grid

# Parse alignment
alignment = extract_alignment_from_landxml(srt_tree)  # → [PI coords + elevations]

# Validate alignment vertical curve consistency
validate_vertical_curves(alignment)

# Merge with existing DXF topography
merged_srt = merge_surfaces(surface, dxf_topography)

return {
    "surface": merged_srt,
    "alignment": alignment,
    "stationing": calc_stationing(alignment),
}
```

**Tempo**: 3-10 min

---

#### Fluxo-3: Level AI — Rasante Inteligente

**Input**: 
- Alinhamento (horizontal + SRT)
- Tipo de rodovia (classe DNIT: federal, estadual, municipal; pista dupla/simples)
- Restrições (obras existentes, áreas de proteção)

**Processo**:
1. **Call Allsite.ai/Level AI** com prompt estruturado:
   ```
   DADOS:
   - Alinhamento horizontal: [list de PI com coords + elevações]
   - Superfície (SRT): [arquivo ou pontos]
   - Tipo: Rodovia Federal, Classe IIA, pista dupla, 100 km/h
   - Restricoes: viaduto em km 3.5, preservação APA km 7-8
   
   TAREFA:
   Gerar rasante otimizada segundo:
   - Greide máximo 8%, mínimo 0.3%
   - Conforto (mudança greide máx. 2% por 100m)
   - Minimização de corte/aterro
   - Conformidade com DNIT-ES-PRO-01/79
   
   OUTPUT: JSON com {estaca, cota_rasante, greide_local, mudanca_greide}
   ```
2. **Async call** (webhook + pooling)
3. **Validate output** contra critérios DNIT
4. **Apply to DXF profile** (layer PERFIL, greide_proposted)

**Tempo**: 15-30 min (consoante complexidade)

---

#### Fluxo-4: Service AI — Drenagem & OAE

**Input**:
- Alignment + rasante
- SRT (superfícies naturais adjacentes)
- Tipo de seção transversal (aterro, corte, misto)
- Dados hidrológicos (bacia, Q10, velocidade)

**Processo**:
1. **Call Allsite.ai/Service AI** com contexto:
   ```
   PROJETO: Rodovia km0-km10
   SEÇÕES: [list com {estaca, tipo, altura, taludes}]
   HIDROLOGIA: Q10=150 m³/s, TR=10 anos, precipitação=2600 mm/ano
   
   TAREFA:
   Dimensionar:
   - Bueiros (seções e espaçamento)
   - Canaletas laterais
   - Dissipadores de energia
   - Obras-de-arte especiais (tubulões, drenagem)
   
   OUTPUT: JSON {estaca, tipo_bueiro, dimensões, material, observações}
   ```
2. **Async call**
3. **Cross-reference SICRO** para custos de bueiro (código 73.xx)
4. **Generate DXF insertion points** (layer DRENAGEM)

**Tempo**: 20-40 min

---

#### Fluxo-5: Civil 3D Automation — Corridor Assembly

**Input**:
- Alignment (estacas, PI, elevações)
- Rasante (greide por estaca)
- Seções transversais (template com larguras, taludes)

**Processo**:
1. **Connect to Civil 3D instance** via COM Automation (Windows)
2. **Create/update Alignment** object
3. **Create/update Profile** (greide)
4. **Apply Assembly** (seção transversal padrão + variações)
5. **Generate Corridor** (malha 3D)
6. **Extract sections** (perfis transversais em cada estaca)
7. **Export to DXF** (layers normatizados)

**Pseudocódigo** (C# .NET for Civil 3D):
```csharp
public static void CreateCorridorFromRoadwayData(
    Database db, 
    Alignment alignment, 
    Profile profile, 
    Assembly assembly) {
    
    // Create corridor
    var corridor = new Corridor(db);
    corridor.SetAlignment(alignment);
    corridor.SetProfile(profile);
    corridor.SetAssembly(assembly);
    corridor.SetCodeSetStyle("Standard");
    
    // Generate sections every 20m
    for (double station = 0; station <= alignment.Length; station += 20) {
        var section = corridor.GetSectionAtStation(station);
        ExportSectionToDXF(section, $"SEC_{station:F0}");
    }
    
    // Export corridor to DXF layer
    ExportCorridorToDXF(corridor, "PLATAFORMA");
}
```

**Tempo**: 10-20 min (com Civil 3D já aberto)

---

### 3.2 Fluxo Validação & Output

#### Fluxo-6: Compliance Check & Report

**Validações automáticas**:
1. **DNIT-ES-PRO-01/79** — greide, raios, superelevação
2. **NBR 6118** — fundações, concreto
3. **NBR 6123** — cargas de vento em OAE
4. **SICRO 2024** — composições existentes vs. proposto
5. **APA/Preservação** — verificação de polígonos de restrição
6. **Topografia** — consistência SRT vs. DXF

**Output**: Relatório PDF com:
- Sumário executivo
- Checklist conformidade
- Gráficos de rasante, seções
- Lista de sinalizadores (warnings/errors)
- Recomendações

**Tempo**: 5 min (template)

---

#### Fluxo-7: DXF Normalization & Delivery

**Normalização ABNT NBR 13142**:
- Layers padrão: ALINHAMENTO, PERFIL, SEÇÕES, PLATAFORMA, DRENAGEM, OAE, COTAS
- Linha types: CONTINUOUS, DASHED, DOTTED (conforme projeto)
- Colors: 1 (red, alinhamento), 5 (cyan, rasante), 3 (green, plataforma)
- Text heights: 2.5mm (cotas), 3.5mm (títulos)

**Entregáveis**:
1. `rodovia-km0-km10-PROJETO-BASICO.dxf` (layers: alinhamento, perfil, seções)
2. `rodovia-km0-km10-PROJETO-EXECUTIVO.dxf` (layers: +plataforma, +drenagem, +detalhes OAE)
3. `RELATORIO-VALIDACAO.pdf` (compliance + recomendações)
4. `PLAYBOOK-S1.md` (instruções próximos passos)

**Tempo**: 3 min

---

## 4. INTEGRAÇÃO ALLSITE.AI

### 4.1 Modelos Especializados

#### Level AI — Rasante Inteligente

**Especialidade**: Greide otimizado para rodovias, ferrovias, metrô.

**Inputs**:
- Topografia (SRT em pontos ou raster)
- Alinhamento horizontal (polyline 3D)
- Restrições (viadutos, pontes, áreas de preservação)
- Normas (DNIT-ES-PRO-01, NBR, ABNT)
- KPIs (minimizar corte/aterro, conforto, velocidade projeto)

**Outputs**:
- Greide (cota por estaca)
- Análise de movimentação de terra (volumes)
- Conformidade com normas (relatório)

**API Endpoint**: `https://api.allsite.ai/level-ai/rasante`

**Latência**: 10-20s (timeout 60s)

---

#### Service AI — Drenagem & Obras Especiais

**Especialidade**: Dimensionamento de drenagem, bueiros, dissipadores, dispositivos hidráulicos.

**Inputs**:
- Seções transversais (altura, taludes, declividade)
- Dados hidrológicos (Q10, tempo concentração)
- Tipo de solo (granulometria, permeabilidade)
- Alinhamento (traçado em planta)

**Outputs**:
- Espaçamento de bueiros (estacas)
- Dimensões de bueiro (diâmetro, tipo)
- Canaleta lateral (altura, declividade)
- Dispositivos especiais (dissipadores, drenagem subsuperficial)
- Estimativas de volume (tubo, concreto)

**API Endpoint**: `https://api.allsite.ai/service-ai/drenagem`

**Latência**: 15-30s (timeout 60s)

---

### 4.2 Fluxo de Integração Async

```python
import aiohttp
import asyncio
from typing import Dict, Any

async def call_level_ai(
    alignment: Dict[str, Any],
    srt: Dict[str, Any],
    constraints: Dict[str, Any],
) -> Dict[str, Any]:
    """Call Allsite.ai/Level AI asynchronously."""
    
    payload = {
        "alignment": alignment,
        "surface": srt,
        "constraints": constraints,
        "norms": ["DNIT-ES-PRO-01", "NBR 6118"],
        "optimization": {
            "minimize_earthwork": True,
            "max_grade": 0.08,
            "min_grade": 0.003,
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.allsite.ai/level-ai/rasante",
            json=payload,
            headers={"Authorization": f"Bearer {ALLSITE_API_KEY}"},
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            return await resp.json()

async def call_service_ai(
    sections: List[Dict],
    hydrology: Dict[str, Any],
) -> Dict[str, Any]:
    """Call Allsite.ai/Service AI for drainage design."""
    
    payload = {
        "sections": sections,
        "hydrology": hydrology,
        "soil_type": "areia fina",
        "standards": ["DNIT-IPR-726", "NBR 12566"],
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.allsite.ai/service-ai/drenagem",
            json=payload,
            headers={"Authorization": f"Bearer {ALLSITE_API_KEY}"},
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            return await resp.json()

# Usage
async def process_s1_project(dxf_path: str):
    roadway_data = parse_dxf(dxf_path)
    
    level_ai_result = await call_level_ai(
        alignment=roadway_data["alignment"],
        srt=roadway_data["surface"],
        constraints=roadway_data.get("constraints", {}),
    )
    
    service_ai_result = await call_service_ai(
        sections=roadway_data["sections"],
        hydrology=roadway_data.get("hydrology", {}),
    )
    
    return {
        "rasante": level_ai_result,
        "drenagem": service_ai_result,
    }
```

---

## 5. CIVIL 3D AUTOMATION API

### 5.1 Diagrama de Contexto

```
Manta S1 Agent (Python/Node)
    ↓
    └─→ Civil 3D Automation API (C# / .NET COM)
            ├─ Alignment object
            ├─ Profile (greide) object
            ├─ Assembly (seção transversal) object
            ├─ Corridor (3D mesh)
            └─ Section output (DXF exports)
```

### 5.2 Fluxo Técnico

**Setup**:
1. Civil 3D (2024+) instalado no servidor ou workstation
2. Autodesk .NET SDK (acsbr24.dll, acadm24.dll)
3. Python bridge: `pyautoclient` ou `win32com` (Windows only)

**Integração Python → Civil 3D**:

```python
import win32com.client

def create_corridor_via_automation(
    dwg_path: str,
    alignment_coords: List[Tuple[float, float, float]],
    profile_data: Dict[float, float],  # {station: elevation}
    assembly_name: str = "Standard",
) -> str:
    """Create Corridor in Civil 3D and export sections."""
    
    # Connect to Civil 3D
    acad = win32com.client.GetObject(class_name="AcadApplication")
    doc = acad.ActiveDocument
    db = doc.Database
    
    # Create/get alignment
    alignment = create_alignment(db, alignment_coords)
    
    # Create/get profile
    profile = create_profile(db, alignment, profile_data)
    
    # Apply assembly
    assembly = get_assembly(db, assembly_name)
    
    # Create corridor
    corridor = create_corridor(db, alignment, profile, assembly)
    
    # Generate sections
    export_corridor_sections(corridor, output_dir="./sections/")
    
    # Save DXF
    doc.SaveAs(dwg_path)
    
    return f"Corridor created in {dwg_path}"
```

---

## 6. LANDXML IMPORT SPECIFICATION

### 6.1 Estrutura LandXML Esperada

```xml
<?xml version="1.0" encoding="utf-8"?>
<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.landxml.org/schema/LandXML-1.2
                             http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd"
         date="2026-07-01" version="1.2">
    
    <Project name="Rodovia BR-101 km0-km10">
        <Application name="Civil 3D" version="2024" manufacturer="Autodesk"/>
        
        <!-- Surface (topografia) -->
        <Surfaces>
            <Surface name="Levantamento_GNSS" dateTime="2026-06-15">
                <SourceData>
                    <Cogo>
                        <Point id="P1" name="TM-001">
                            <Coordinates>300000.00 7000000.00 45.23</Coordinates>
                        </Point>
                        <Point id="P2" name="TM-002">
                            <Coordinates>300050.00 7000000.00 45.45</Coordinates>
                        </Point>
                        <!-- more points -->
                    </Cogo>
                </SourceData>
                <Triangles>
                    <Triangle id="TR1" p1="P1" p2="P2" p3="P3"/>
                    <!-- more triangles -->
                </Triangles>
            </Surface>
        </Surfaces>
        
        <!-- Alignment (alinhamento horizontal) -->
        <Alignments>
            <Alignment name="Eixo BR-101" staStart="0+0.00" length="10000.00">
                <CogoPoints>
                    <CogoPoint id="PI1" name="PI-KM0">
                        <Coordinates>300000.00 7000000.00</Coordinates>
                    </CogoPoint>
                    <CogoPoint id="PI2" name="PI-KM3.5">
                        <Coordinates>303500.00 7001200.00</Coordinates>
                    </CogoPoint>
                    <CogoPoint id="PI3" name="PI-KM10">
                        <Coordinates>310000.00 7000800.00</Coordinates>
                    </CogoPoint>
                </CogoPoints>
                
                <Line name="Tangent1" length="3500.00">
                    <Start>0+0.00</Start>
                    <End>0+3500.00</End>
                    <Bearing>45.0</Bearing>
                </Line>
                
                <Curve name="Curva1" radius="2000.00" length="500.00" dir="L">
                    <Start>0+3500.00</Start>
                    <End>0+4000.00</End>
                </Curve>
                
                <!-- more geometry -->
            </Alignment>
        </Alignments>
        
        <!-- Profile (alinhamento vertical) -->
        <Profiles>
            <Profile name="Greide_Atual" alignmentRef="Eixo BR-101">
                <ProfileGeometry>
                    <PVI name="VI1" station="0+0.00" elevation="45.00"/>
                    <PVI name="VI2" station="0+2000.00" elevation="48.50"/>
                    <PVI name="VI3" station="0+5000.00" elevation="52.00"/>
                    <PVI name="VI4" station="1+0000.00" elevation="50.00"/>
                </ProfileGeometry>
            </Profile>
        </Profiles>
        
    </Project>
</LandXML>
```

### 6.2 Parsing LandXML (Python)

```python
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

@dataclass
class Point3D:
    x: float
    y: float
    z: float
    name: str = ""

@dataclass
class Surface:
    name: str
    points: List[Point3D]
    triangles: List[tuple]  # [(p1_id, p2_id, p3_id), ...]

def parse_landxml(filepath: str) -> Dict[str, Any]:
    """Parse LandXML 1.2 file and extract surface + alignment."""
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"landxml": "http://www.landxml.org/schema/LandXML-1.2"}
    
    # Extract surface
    surface_elem = root.find(".//landxml:Surface", ns)
    points = []
    for point_elem in surface_elem.findall(".//landxml:Point", ns):
        coords_text = point_elem.find("landxml:Coordinates", ns).text
        x, y, z = map(float, coords_text.split())
        points.append(Point3D(x=x, y=y, z=z, name=point_elem.get("name")))
    
    # Extract alignment
    alignment_elem = root.find(".//landxml:Alignment", ns)
    pis = []
    for cogo_point in alignment_elem.findall(".//landxml:CogoPoint", ns):
        coords_text = cogo_point.find("landxml:Coordinates", ns).text
        x, y = map(float, coords_text.split()[:2])
        pis.append(Point3D(x=x, y=y, z=0, name=cogo_point.get("name")))
    
    # Extract profile (greide)
    profile_elem = root.find(".//landxml:Profile", ns)
    profile_points = []
    for pvi in profile_elem.findall(".//landxml:PVI", ns):
        station = float(pvi.get("station").replace("+", ""))
        elevation = float(pvi.get("elevation"))
        profile_points.append({"station": station, "elevation": elevation})
    
    return {
        "surface": Surface(name="imported", points=points, triangles=[]),
        "alignment_pis": pis,
        "profile": profile_points,
    }
```

---

## 7. EZDXF PARSER & DXF OUTPUT

### 7.1 DXF Input Parsing

```python
import ezdxf
from ezdxf.layouts import Modelspace

def extract_alignment_from_dxf(dxf_doc: ezdxf.Drawing) -> List[Tuple[float, float, float]]:
    """Extract 3D alignment polyline from DXF ALINHAMENTO layer."""
    
    alignment = []
    mspace = dxf_doc.modelspace()
    
    for entity in mspace.query('LWPOLYLINE[layer=="ALINHAMENTO"]'):
        for point in entity.get_points():
            alignment.append(point[:3])  # (x, y, z)
    
    return alignment

def extract_drainage_blocks_from_dxf(dxf_doc: ezdxf.Drawing) -> Dict[str, Any]:
    """Extract drainage layout from DRENAGEM layer."""
    
    drainage = {"bueiros": [], "canaletas": []}
    mspace = dxf_doc.modelspace()
    
    for entity in mspace.query('INSERT[layer=="DRENAGEM"]'):
        block_name = entity.name
        if "BUEIRO" in block_name:
            drainage["bueiros"].append({
                "position": entity.dxf.insert,
                "name": block_name,
                "rotation": entity.dxf.rotation,
            })
    
    return drainage

def validate_layer_structure(dxf_doc: ezdxf.Drawing) -> List[str]:
    """Validate CBR-compliant layer naming (ABNT NBR 13142)."""
    
    expected_layers = [
        "ALINHAMENTO", "PERFIL", "SEÇÕES", "PLATAFORMA",
        "DRENAGEM", "OAE", "COTAS", "HATCH", "TEXT",
    ]
    
    errors = []
    for layer in expected_layers:
        if layer not in dxf_doc.layers:
            errors.append(f"Missing layer: {layer}")
    
    return errors
```

### 7.2 DXF Output Generation

```python
import ezdxf

def generate_normalized_dxf(
    alignment: List[Tuple[float, float, float]],
    rasante: Dict[float, float],  # {station: elevation}
    sections: List[Dict],
    drenagem: Dict,
    output_file: str,
) -> str:
    """Generate ABNT NBR 13142-compliant DXF output."""
    
    # Create new drawing
    dwg = ezdxf.new(dxfversion="R2024")
    mspace = dwg.modelspace()
    
    # Add layers with proper color & linetype
    dwg.layers.new(name="ALINHAMENTO", dxfattribs={"color": 1})  # Red
    dwg.layers.new(name="PERFIL", dxfattribs={"color": 5})       # Cyan
    dwg.layers.new(name="PLATAFORMA", dxfattribs={"color": 3})   # Green
    dwg.layers.new(name="DRENAGEM", dxfattribs={"color": 4})     # Magenta
    dwg.layers.new(name="OAE", dxfattribs={"color": 6})          # Magenta
    
    # Add alignment polyline
    alignment_points = [(p[0], p[1]) for p in alignment]
    alignment_polyline = mspace.add_lwpolyline(alignment_points)
    alignment_polyline.dxf.layer = "ALINHAMENTO"
    alignment_polyline.dxf.lineweight = 35  # 0.5mm
    
    # Add profile (rasante)
    profile_points = []
    for station, elevation in sorted(rasante.items()):
        # Convert station to x-axis (e.g., station 0+0 → x=0)
        x = station
        y = elevation
        profile_points.append((x, y))
    
    profile_polyline = mspace.add_lwpolyline(profile_points)
    profile_polyline.dxf.layer = "PERFIL"
    profile_polyline.dxf.lineweight = 35
    
    # Add drainage blocks
    for bueiro in drenagem.get("bueiros", []):
        insert = mspace.add_insert(
            "BUEIRO_400x400",
            dxfattribs={"insert": bueiro["position"]}
        )
        insert.dxf.layer = "DRENAGEM"
    
    # Add text annotations (cotas, estacas)
    for station, elevation in sorted(rasante.items())[:10]:  # Sample
        x = station
        y = elevation
        text = mspace.add_text(
            f"Est {station:.0f}\nCota {elevation:.2f}",
            dxfattribs={"insert": (x, y + 5), "height": 2.5}
        )
        text.dxf.layer = "COTAS"
    
    # Save
    dwg.saveas(output_file)
    return output_file
```

---

## 8. PLAYBOOK OPERACIONAL S1

### 8.1 Intake Estruturado

**Checklist de entrada (usuário S1 preenchido no chat)**:

1. **Dados básicos**:
   - [ ] Nome do projeto (ex: "Rodovia BR-101 km0-km10")
   - [ ] Segmento (Classe DNIT: I, II, III, IV)
   - [ ] Tipo via (pista dupla/simples, com/sem canteiro)

2. **Arquivos**:
   - [ ] DXF com alinhamento horizontal (camada ALINHAMENTO)
   - [ ] Levantamento topográfico (LandXML ou pontos ASCII)
   - [ ] PDF do projeto anterior (se houver)

3. **Restrições**:
   - [ ] Áreas de proteção (APAs, terras indígenas)
   - [ ] Pontos críticos (viadutos, pontes existentes)
   - [ ] Dados hidrológicos (bacia, Q10)

4. **Normas**:
   - [ ] DNIT-ES-PRO-01/79 (sim/não)
   - [ ] Velocidade projeto (km/h)
   - [ ] Outras normas específicas

---

### 8.2 Processos Automáticos (Orchestration)

#### Process-1: DXF Parse & Validate
```yaml
trigger: file_received(*.dxf)
steps:
  - parse_dxf_with_ezdxf()
  - validate_layer_structure()
  - extract_alignment()
  - extract_sections()
  - output: roadway_data (JSON)
timeout: 5m
```

#### Process-2: LandXML Merge
```yaml
trigger: landxml_received
depends: Process-1
steps:
  - parse_landxml()
  - merge_surfaces()
  - validate_alignment_consistency()
  - output: merged_roadway_data (JSON)
timeout: 10m
```

#### Process-3: Level AI Rasante
```yaml
trigger: roadway_data ready
depends: Process-2
parallel_calls: 3  # can run 3 in parallel
steps:
  - call_allsite_level_ai_async()
  - validate_rasante_against_dnit()
  - output: greide (JSON)
timeout: 30m
retry: 3
```

#### Process-4: Service AI Drenagem
```yaml
trigger: roadway_data ready
depends: Process-2
parallel_calls: 3
steps:
  - call_allsite_service_ai_async()
  - validate_drainage_design()
  - lookup_sicro_codes()
  - output: drenagem (JSON)
timeout: 40m
retry: 3
```

#### Process-5: Civil 3D Automation (Windows only)
```yaml
trigger: greide + drenagem ready
depends: [Process-3, Process-4]
environment: Windows server with Civil 3D 2024+
steps:
  - connect_civil3d_com()
  - create_alignment()
  - create_profile()
  - create_corridor()
  - export_sections()
  - output: dwg file + sections
timeout: 20m
retry: 2
```

#### Process-6: DXF Output Normalization
```yaml
trigger: all components ready
steps:
  - generate_normalized_dxf()
  - apply_cbrules()
  - validate_layers()
  - output: rodovia-PROJETO-BASICO.dxf
timeout: 5m
```

#### Process-7: Report & Compliance
```yaml
trigger: all processes complete
steps:
  - generate_compliance_report()
  - create_playbook_next_steps()
  - output: RELATORIO-VALIDACAO.pdf + PLAYBOOK-S1.md
timeout: 10m
```

---

### 8.3 Saída (Deliverables)

Após sucesso em todos os processos, usuário recebe:

**Arquivos**:
1. `[projeto]-PROJETO-BASICO.dxf` (alinhamento + perfil + seções)
2. `[projeto]-PROJETO-EXECUTIVO.dxf` (+ plataforma + drenagem + OAE)
3. `RELATORIO-VALIDACAO-[data].pdf` (checklist + warnings)
4. `PLAYBOOK-S1-[projeto].md` (próximos passos, detalhes design)

**Documentação no chat**:
- Resumo de mudanças (greide vs. topografia)
- Volumes corte/aterro estimados
- Recomendações (seções críticas, drenagem)
- Sinalizadores (risk flags, normas pendentes)

---

## 9. TIMELINE & DEPENDÊNCIAS (Q4 2026 → Q2 2027)

### 9.1 Fases de Entrega

| Fase | Período | Entregáveis | Dependências |
|------|---------|-------------|--------------|
| **Alpha** | Q4 2026 (Nov-Dez) | DXF parser + LandXML importer + SICRO connector | ezdxf 1.2+, lxml |
| **Beta** | Q1 2027 (Jan-Mar) | Level AI bridge + Service AI bridge + DXF normalizer | Allsite.ai API keys + docs |
| **Gamma** | Q2 2027 (Apr-Jun) | Civil 3D Automation API + corridor generation + playbook | Civil 3D 2024+ SDK, C# bridge |
| **GA** | Q2 2027 (Jun) | Full integration + training + documentation | All above + user feedback |

### 9.2 Dependências Técnicas

```
ezdxf 1.2+
├─ DXF parser (✅ available)
└─ DXF writer (✅ available)

lxml + XSD validators
├─ LandXML parsing (✅ available)
└─ schema validation (✅ available)

Allsite.ai Partnership
├─ Level AI API (🔄 Q4 2026 contract)
├─ Service AI API (🔄 Q4 2026 contract)
└─ Rate limits, auth (TBD)

Autodesk Automation API
├─ Civil 3D 2024+ (✅ available)
├─ .NET SDK (✅ available)
└─ COM/Win32 bridge (🔄 Q1 2027 dev)

Manta SICRO Connector
├─ Redis cache (✅ available)
├─ Composição codes (✅ synced Q4 2026)
└─ Price updates (monthly automated)
```

### 9.3 Gráfico de Gantt (Simplificado)

```
Q4 2026 ━━━━━━━ | Q1 2027 ━━━━━━━ | Q2 2027 ━━━━━━━
 N  D  │  J  F  M  │  A  M  J  │
 
[DXF Parser ▓▓▓▓▓▓]
 [LandXML Importer ▓▓▓▓▓▓]
  [SICRO Connector ▓▓▓▓▓▓]
       [Level AI Bridge ▓▓▓▓▓▓▓▓▓]
        [Service AI Bridge ▓▓▓▓▓▓▓▓▓]
         [DXF Normalizer ▓▓▓▓▓▓▓▓▓]
              [Civil 3D Automation ▓▓▓▓▓▓▓▓▓▓▓]
               [Corridor Gen ▓▓▓▓▓▓▓▓▓▓▓]
                [Integration Testing ▓▓▓▓▓▓▓▓]
                 [User Training ▓▓▓▓▓▓]
                  [GA Release ▓]
```

---

## 10. RISCOS & MITIGAÇÃO

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Allsite.ai API instabilidade | Médio | Alto | Implementar retry + fallback manual |
| Civil 3D Automation COM crashes | Médio | Alto | Isolar em serviço Windows separado + health check |
| LandXML formato variável | Alto | Médio | Suportar múltiplos dialetos, validação lenient |
| Drenagem otimização inadequada | Médio | Médio | Validação por especialista SICRO, flag de revisão |
| Performance DXF >500MB | Baixo | Alto | Chunking automático, processamento em partes |

---

## 11. SUCESSO & KPIs

### 11.1 Métricas de Qualidade

1. **Conformidade DNIT**: 100% dos projetos passam em checklist DNIT-ES-PRO-01
2. **Tempo médio processamento**: <2 horas (ponta-a-ponta)
3. **Taxa de erro drenagem**: <2% necessidade de ajustes pós-design
4. **Reuso de playbook**: >80% dos usuários utilizam output do S1 direto em fase executiva

### 11.2 Adoção

- **Q1 2027**: 5 projetos piloto (internos)
- **Q2 2027**: 15 projetos (clientes beta)
- **Q3 2027**: 50+ projetos (produção)

---

## 12. PRÓXIMOS PASSOS

1. **Gate Humano** (MN approval) — este documento + plano risco (1 semana)
2. **Contract Allsite.ai** — assinatura SLA + API keys (2 semanas)
3. **Dev Alpha Sprint** — DXF parser + LandXML importer (4 semanas, Q4 2026)
4. **Dev Beta Sprint** — Level AI/Service AI bridges (6 semanas, Q1 2027)
5. **Dev Gamma Sprint** — Civil 3D Automation (8 semanas, Q1-Q2 2027)
6. **Testing & Validation** — 5 projetos piloto (4 semanas, Q2 2027)
7. **GA Release** — documentação + training (2 semanas, Q2 2027)

---

## REFERÊNCIAS

- **Autodesk Civil 3D Automation API**: [Link to official docs, TBD]
- **ezdxf Documentation**: https://ezdxf.readthedocs.io/
- **LandXML Specification 1.2**: https://www.landxml.org/
- **DNIT-ES-PRO-01/79**: Manual de projeto geométrico de rodovias rurais
- **ABNT NBR 13142**: Desenho técnico - Dobra e esquadria de papel
- **Manta SICRO Integration**: [Internal wiki, access via SharePoint]
- **Allsite.ai API Docs**: [To be provided on partnership signing]

---

**Aprovações Pendentes**:
- [ ] MN (Arquiteto IA) — estratégia geral
- [ ] CTO Infraestrutura — arquitetura técnica
- [ ] Allsite.ai — viabilidade técnica dos modelos
- [ ] CFO — orçamento Q4 2026 → Q2 2027
