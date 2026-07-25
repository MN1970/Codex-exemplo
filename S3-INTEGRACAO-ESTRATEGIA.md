# S3 Integração Estratégica — Ferrovia (Q1 2027 → Q2 2027)

**Documento**: Estratégia de Integração Técnica para Manta 03-S3 (agente-infraestrutura).  
**Data**: 2026-07-24  
**Versão**: 1.0 (DRAFT)  
**Proprietário**: Manta Associados — Arquiteto IA (Manta 16)  
**Status**: Pronto para aprovação de gate humano (MN)

---

## 1. VISÃO GERAL

A estratégia S3 visa integrar o agente-infraestrutura (Ferrovias) com uma pilha técnica de processamento de design assistida por IA, focada em linhas férreas, transporte sobre trilhos (metrô, VLT) e infraestruturas de via permanente:

1. **LandXML Input** — parsear alinhamentos, superfícies e corredores (origem Civil 3D ou Bentley)
2. **Bentley OpenRail vs Civil 3D Decision Matrix** — selecionar ferramenta ótima por tipo de projeto
3. **Via Permanente Validation** — verificar ballast, dormentes, geometria de trilho conforme NBR 8932-8934
4. **Bentley Copilot MCP Integration** — especialistas de domínio via IA Bentley (Q1 2027)
5. **Corridor Design Automation** — gerar seções transversais, perfis verticais, tables de projeto
6. **Output Delivery** — DXF normalizado + relatórios de verificação + playbooks operacionais

**Resultado esperado**: Redução de 35-50% do tempo de projeto básico e executivo de ferrovias via automação inteligente de fluxos LandXML → geometria trilho → validação via permanente → análise → output normalizado.

---

## 2. ARQUITETURA TÉCNICA

### 2.1 Pilha de Integração

```
┌─────────────────────────────────────────────────────────────┐
│  ENTRADA — Usuário (Engenheiro de Ferrovias / S3)          │
│  Formato: LandXML (Civil 3D ou Bentley), PDF, CSV (pontos) │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  PARSER LAYER (lxml)    │
        │  ├─ LandXML parsing      │
        │  ├─ Alignment extraction │
        │  ├─ Surface TIN gen      │
        │  └─ Coordinate validation│
        └────────────┬───────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  NORMALIZATION LAYER                │
        │  ├─ Rail geometry alignment         │
        │  ├─ Curve & tangent validation      │
        │  ├─ Profile grade consistency       │
        │  └─ Via permanente standards        │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  TOOL SELECTION LAYER               │
        │  ├─ Bentley OpenRail vs Civil 3D    │
        │  ├─ Project type matching           │
        │  └─ Feature availability check      │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  ANALYSIS & GENERATION LAYER        │
        │  ├─ Bentley Copilot (Q1 2027)       │
        │  ├─ Via permanente design (ballast) │
        │  ├─ AMV (Aparelhos de Via)          │
        │  ├─ Grade/cant calculation          │
        │  └─ Geotechnical integration        │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │  VALIDATION LAYER                   │
        │  ├─ NBR 8932-8934 compliance        │
        │  ├─ Curve super-elevation check     │
        │  ├─ Ballast & sleeper spec match    │
        │  └─ Geometric constraints verify    │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  SAÍDA — Deliverables  │
        │  ├─ DXF (normatizado)  │
        │  ├─ Relatórios PDF     │
        │  ├─ Playbooks          │
        │  └─ Tabelas de projeto │
        └────────────────────────┘
```

### 2.2 Componentes

| Componente | Tech Stack | Responsabilidade | Tempo Estimado |
|------------|------------|------------------|-----------------|
| **LandXML Parser** | lxml + XSD validator | Alinhamentos, superfícies, pontos de estaca | Q1 2027 |
| **Rail Geometry Engine** | Python GIS libs | Cálculo de superelevação, bitola, raios mín. | Q1 2027 |
| **Bentley OpenRail Bridge** | OpenAPI / MCP (Q1 2027) | Connecção com Bentley (quando disponível) | Q1 2027 |
| **Civil 3D Rail Fallback** | Autodesk Automation API | Suporte via Civil 3D para projetos menores | Q1 2027 |
| **Bentley Copilot MCP** | Bentley AI embeddings | Especialistas domínio (cantaria, via perm., AMV) | Q1 2027 |
| **Via Permanente Validator** | NBR 8932-8934 rules engine | Verificação ballast, dormentes, trilho, gauge | Q1 2027 |
| **DXF Output Rail** | ezdxf writer + rail rules | Layer normalization específica ferrovias | Q1 2027 |
| **Report Generator** | Jinja2 + ReportLab | Relatórios PDF, planilhas técnicas, compliance | Q1 2027 |

---

## 3. FLUXOS DE INTEGRAÇÃO

### 3.1 Fluxo LandXML → Validação Via Permanente → Análise

#### Fluxo-1: Parse & Validate LandXML (Railway)

**Input**: arquivo `ferrovia-km0-km50.xml` (LandXML 1.2, exportado de Civil 3D ou Bentley)

**Etapas**:
1. **lxml.parse()** → Document object
2. **Extract alignment** por AMV (Aparelhos de Via), raios de curva, superelevação
3. **Extract surface** (TIN topografia)
4. **Extract profile** (greide vertical + curves)
5. **Validate coordinate system** (UTM, local, lat/long)
6. **Calc stationing** (estaqueamento ferroviário)
7. **Output**: Python dict com estrutura normalizada

**Pseudocódigo**:
```python
import lxml.etree as etree

def parse_railway_landxml(filepath: str) -> Dict[str, Any]:
    """Parse LandXML para projeto ferroviário."""
    
    tree = etree.parse(filepath)
    root = tree.getroot()
    ns = {"landxml": "http://www.landxml.org/schema/LandXML-1.2"}
    
    # Extract alinhamento ferroviário
    alignment_elem = root.find(".//landxml:Alignment", ns)
    pis = []
    for cogo_point in alignment_elem.findall(".//landxml:CogoPoint", ns):
        coords_text = cogo_point.find("landxml:Coordinates", ns).text
        x, y, z = map(float, coords_text.split()[:3])
        pis.append({
            "name": cogo_point.get("name"),
            "x": x, "y": y, "z": z
        })
    
    # Extract curvas (curvatura ferroviária)
    curves = []
    for curve_elem in alignment_elem.findall(".//landxml:Curve", ns):
        curves.append({
            "radius": float(curve_elem.get("radius")),
            "length": float(curve_elem.get("length")),
            "start_station": curve_elem.find("landxml:Start", ns).text,
            "dir": curve_elem.get("dir"),  # L ou R
        })
    
    # Extract perfil vertical
    profile_elem = root.find(".//landxml:Profile", ns)
    profile_data = []
    for pvi in profile_elem.findall(".//landxml:PVI", ns):
        station = pvi.get("station")
        elevation = float(pvi.get("elevation"))
        profile_data.append({"station": station, "elevation": elevation})
    
    # Extract superfície (topografia)
    surface_elem = root.find(".//landxml:Surface", ns)
    points = []
    for point_elem in surface_elem.findall(".//landxml:Point", ns):
        coords_text = point_elem.find("landxml:Coordinates", ns).text
        x, y, z = map(float, coords_text.split()[:3])
        points.append({"x": x, "y": y, "z": z})
    
    return {
        "alignment_pis": pis,
        "curves": curves,
        "profile": profile_data,
        "surface_points": points,
        "metadata": extract_metadata(root, ns),
    }
```

**Tempo**: 5-15 min

---

#### Fluxo-2: Rail Geometry Engine — Superelevação & Bitola

**Input**:
- Alinhamento (curvas com raios, comprimentos)
- Superfície (TIN topografia)
- Tipo de via (Via singela, dupla, bitola métrica, larga)
- Velocidade projeto (km/h)

**Processo**:
1. **Calc superelevação** (cant) conforme NBR 8932:
   - Fórmula: e = V² / (127 × R)
   - máximo 10% (bitola métrica), 12% (bitola larga)
2. **Validate min/max raios** conforme tipo:
   - Via singela: R mín 200m (urbana), 500m (rural)
   - Via dupla: R mín 300m
3. **Check bitola consistency** (1000mm métrica vs 1600mm larga)
4. **Generate superelevation transitions** (curvas de transição)
5. **Output**: JSON com cant por estaca, transições

**Pseudocódigo**:
```python
import math

def calc_rail_superelevation(
    curves: List[Dict],
    gauge_type: str = "métrica",
    speed_kmh: float = 80.0,
) -> Dict[str, Any]:
    """
    Calcula superelevação (cant) de ferrovias conforme NBR 8932.
    
    gauge_type: 'métrica' (1000mm), 'larga' (1600mm), 'dupla' (1435mm)
    """
    
    max_cant = {
        "métrica": 0.10,
        "larga": 0.12,
        "dupla": 0.08,
    }.get(gauge_type, 0.10)
    
    min_radius = {
        "métrica": {"urbana": 200, "rural": 500},
        "larga": {"urbana": 250, "rural": 600},
        "dupla": {"urbana": 300, "rural": 800},
    }.get(gauge_type, {})
    
    results = []
    
    for curve in curves:
        radius = curve["radius"]
        length = curve["length"]
        start_sta = float(curve["start_station"].replace("+", ""))
        
        # Verificar raio mínimo
        context = "urbana" if radius < 500 else "rural"
        min_r = min_radius.get(context, 500)
        if radius < min_r:
            raise ValueError(f"Raio {radius}m < mínimo {min_r}m para {context}")
        
        # Calcular cant (superelevação)
        cant = (speed_kmh ** 2) / (127 * radius)
        cant = min(cant, max_cant)  # limitar ao máximo
        
        # Gerar transições (comprimento de transição = cant × comprimento curva)
        transition_length = int(length * cant / max_cant) if cant > 0 else 0
        
        results.append({
            "start_station": start_sta,
            "radius": radius,
            "length": length,
            "cant_percent": cant * 100,
            "transition_length": transition_length,
            "valid": radius >= min_r,
        })
    
    return {
        "curves_analysis": results,
        "gauge_type": gauge_type,
        "speed_kmh": speed_kmh,
    }
```

**Tempo**: 3-8 min

---

#### Fluxo-3: Via Permanente Design — Ballast & Dormentes

**Input**:
- Alinhamento (pis, curvas)
- Tipo de via (singela, dupla)
- Tipo solo (subgrade material)
- Velocidade projeto
- Traffic load (tonnadas por ano)

**Processo**:
1. **Spec ballast** (material de lastro):
   - Granulometria: 40-60mm (standard ferroviário)
   - Profundidade: 250-350mm (conforme carga)
   - Material: rocha britada (basalto/granito)
2. **Spec dormentes** (sleepers):
   - Tipo: madeira tratada ou concreto protendido
   - Espaçamento: 0.6m (linha de passageiros), 0.5m (mercadorias)
   - Dimensões: 250×250×2500mm (madeira)
3. **Calc geotechnical** (capacidade subgrade):
   - CBR mínimo 5% para via permanente
   - Drainage adequado
4. **Generate ballast section** (perfil transversal de lastro)
5. **Output**: JSON com specs, quantities, profile

**Pseudocódigo**:
```python
def design_ballast_and_sleepers(
    alignment: Dict,
    via_type: str = "singela",
    soil_type: str = "areia",
    speed_kmh: float = 80.0,
    traffic_tonnage_annual: float = 5e6,
) -> Dict[str, Any]:
    """
    Dimensiona lastro e dormentes conforme padrões ferroviários.
    """
    
    # Definir specs conforme tipo via
    ballast_depth = 0.350 if traffic_tonnage_annual > 1e7 else 0.250
    sleeper_spacing = 0.50 if via_type == "dupla" else 0.60
    
    # Specs de ballast
    ballast_spec = {
        "material": "rocha britada (basalto/granito)",
        "granulometry_min_mm": 40,
        "granulometry_max_mm": 60,
        "depth_m": ballast_depth,
        "density_ton_per_m3": 1.5,
        "friction_coeff": 0.45,
    }
    
    # Specs de dormentes
    sleeper_type = "madeira tratada" if traffic_tonnage_annual < 1e7 else "concreto protendido"
    sleeper_spec = {
        "type": sleeper_type,
        "length_mm": 2500,
        "cross_section_mm": (250, 250),
        "spacing_m": sleeper_spacing,
        "sleepers_per_km": int(1000 / sleeper_spacing),
    }
    
    # Calc quantidade total por km
    total_sleepers_km = sleeper_spec["sleepers_per_km"]
    total_ballast_m3_km = (
        1000 * 2.0 * ballast_depth  # 2.0m de largura
    )
    
    # Validação geotécnica (CBR)
    min_cbr = 0.05
    if soil_type in ["lama", "turfa"]:
        recommendations = ["Executar melhoria de subgrade", "Aumentar drenagem"]
    else:
        recommendations = []
    
    return {
        "ballast_spec": ballast_spec,
        "sleeper_spec": sleeper_spec,
        "quantities_per_km": {
            "sleepers": total_sleepers_km,
            "ballast_m3": total_ballast_m3_km,
            "ballast_tons": total_ballast_m3_km * ballast_spec["density_ton_per_m3"],
        },
        "recommendations": recommendations,
    }
```

**Tempo**: 5-12 min

---

#### Fluxo-4: Bentley Copilot MCP Integration (Q1 2027)

**Input**:
- Geometria ferroviária (alignment, profile, curves)
- Via permanente design (ballast, sleepers)
- Contexto de projeto (velocidade, tipo carga)

**Processo**:
1. **Connect to Bentley Copilot MCP** (via OpenAPI, Q1 2027):
   ```
   POST /bentley-copilot/rail-design
   {
     "project_type": "ferrovia",
     "alignment": {...},
     "via_permanente": {...},
     "constraints": {...}
   }
   ```
2. **Call specialized models**:
   - **RailCant AI** — otimizar superelevação
   - **TrackGeometry AI** — validar geometria de trilho
   - **CantileAmortissement AI** — modelar sistemas de amortecimento
3. **Receive recommendations**:
   - Ajustes de curva
   - Alternativas de via permanente
   - Análise de custos vs. performance
4. **Output**: JSON com recomendações

**Pseudocódigo** (Q1 2027):
```python
import aiohttp

async def call_bentley_copilot_rail(
    alignment: Dict,
    via_permanente: Dict,
    constraints: Dict,
) -> Dict[str, Any]:
    """Call Bentley Copilot MCP para design ferroviário (Q1 2027)."""
    
    payload = {
        "project_type": "ferrovia",
        "project_phase": "projeto_basico",
        "alignment": alignment,
        "via_permanente": via_permanente,
        "constraints": constraints,
        "optimization_targets": [
            "minimize_ballast_volume",
            "optimize_superelevation",
            "validate_amv_spacing",
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.bentley.com/copilot/rail-design",
            json=payload,
            headers={"Authorization": f"Bearer {BENTLEY_API_KEY}"},
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            return await resp.json()
```

**Tempo**: 20-40 min (Q1 2027)

---

#### Fluxo-5: Bentley OpenRail vs Civil 3D Decision Matrix

**Matriz de decisão**:

| Aspecto | Bentley OpenRail | Civil 3D Rail Tools | Recomendação |
|--------|---|---|---|
| **Metros/VLT (LRT)** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐ Bom | Bentley OpenRail |
| **Ferrovias longos (>100km)** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐ Bom | Bentley OpenRail |
| **Via permanente design** | ⭐⭐⭐⭐⭐ Nativo | ⭐⭐ Limitado | Bentley OpenRail |
| **Integração IFC (BIM)** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Bom | Bentley OpenRail |
| **Estações (arquitetura)** | ⭐⭐⭐ Bom | ⭐⭐⭐⭐⭐ Excelente | Civil 3D |
| **Custo inicial** | $ $ $ $ (alto) | $ $ (médio) | Civil 3D |
| **Curva de aprendizado** | Difícil (especializado) | Média | Civil 3D |
| **Projetos pequenos (<20km)** | Possível (over-spec) | ⭐⭐⭐⭐ Recomendado | Civil 3D |

**Lógica de seleção**:
```python
def select_optimal_tool(
    project_type: str,
    length_km: float,
    project_phase: str,
    budget_usd: float,
) -> str:
    """Seleciona Bentley OpenRail ou Civil 3D Rail Tools."""
    
    if project_type in ["metro", "vlt", "lrt"]:
        return "bentley_openrail"
    
    if length_km > 100 and project_type == "ferrovia":
        return "bentley_openrail"
    
    if "estacao" in project_type and project_phase == "projeto_executivo":
        return "civil_3d"
    
    if length_km < 20 and budget_usd < 50000:
        return "civil_3d"
    
    if length_km > 50:
        return "bentley_openrail"
    
    # Default fallback
    return "civil_3d"
```

**Tempo**: 2 min (decisão automática)

---

#### Fluxo-6: Corridor Generation — Seções Transversais

**Input**:
- Alinhamento (3D coordinates, curves)
- Perfil vertical (elevações, grades)
- Via permanente design (ballast, sleepers)
- Tipo seção (aterro, corte, misto)

**Processo**:
1. **Generate template seção transversal** (cross-section):
   ```
   ┌─────────────────────────────┐  Terreno natural (superficie)
   │     Talude Esquerdo         │
   │                             │
   │    ┌──────────┐             │
   │    │  Ballast │ (250-350mm) │
   │ ───┤──────────├───┬─────────┤
   │    │Sleepers  │   │         │
   │    └──────────┘   │         │
   │       Trilhos     │ Drenagem│
   │                   │         │
   └───────────────────┴─────────┘
   ```
2. **Apply at each station** (a cada 20m ou conforme curva)
3. **Calc volumes** (terra, ballast, concreto)
4. **Export seções** (DXF, PDF, 3D mesh)

**Pseudocódigo**:
```python
def generate_rail_sections(
    alignment: Dict,
    profile: Dict,
    via_perm: Dict,
    output_dir: str = "./sections/",
) -> List[Dict]:
    """Gera seções transversais para ferrovia."""
    
    sections = []
    station_interval = 20  # metros
    
    for station in range(0, int(alignment["total_length"]), station_interval):
        # Get elevation na estaca
        elevation = interpolate_profile(profile, station)
        
        # Get curvatura na estaca
        radius = get_curve_radius(alignment, station)
        cant = calc_cant(radius, speed=80)
        
        # Build seção template
        section = {
            "station": station,
            "elevation": elevation,
            "cant_percent": cant * 100,
            "ballast_depth": via_perm["ballast_spec"]["depth_m"],
            "sleeper_spacing": via_perm["sleeper_spec"]["spacing_m"],
        }
        
        # Export para DXF (simplificado)
        export_section_to_dxf(section, f"{output_dir}/SEC_{station:05d}.dxf")
        sections.append(section)
    
    return sections
```

**Tempo**: 10-20 min

---

### 3.2 Fluxo Validação & Output

#### Fluxo-7: NBR 8932-8934 Compliance Check

**Validações automáticas**:
1. **NBR 8932** — Bitola de via (tolerâncias 1435mm ±3mm)
2. **NBR 8933** — Documentação (apresentação de projeto)
3. **NBR 8934** — Aparelhos de via (AMV, junções, travessias)
4. **Raios mínimos** conforme tipo (200m singela, 300m dupla)
5. **Superelevação máxima** (10% métrica, 12% larga)
6. **Drenagem adequada** (CBR >5% subgrade)

**Output**: Relatório PDF com:
- Sumário executivo
- Checklist conformidade NBR
- Gráficos de superelevação, profile
- Via permanente specs
- Lista de sinalizadores
- Recomendações

**Tempo**: 5 min (template)

---

#### Fluxo-8: DXF Normalization & Delivery (Railway)

**Normalização ferroviária**:
- Layers: ALINHAMENTO_TRILHO, PERFIL, SECOES, BALLAST, DORMENTES, AMV, DRENAGEM, COTAS
- Linha types: CONTINUOUS (trilhos), DASHED (centerline), DOTTED (ballast)
- Colors: 1 (vermelho, trilho), 5 (cyan, perfil), 3 (verde, lastro)
- Text heights: 2.5mm (cotas de estaca), 3.5mm (títulos)

**Entregáveis**:
1. `ferrovia-km0-km50-PROJETO-BASICO.dxf` (alinhamento, perfil, seções)
2. `ferrovia-km0-km50-PROJETO-EXECUTIVO.dxf` (+ via permanente, drenagem, AMV)
3. `RELATORIO-VALIDACAO-NBR8932.pdf` (compliance + recomendações)
4. `TABELAS-PROJETO.xlsx` (estacas, cotas, ballast volumes)
5. `PLAYBOOK-S3.md` (instruções próximos passos)

**Tempo**: 3 min

---

## 4. INTEGRAÇÃO BENTLEY & MCP

### 4.1 Bentley Copilot MCP (Q1 2027)

**Disponibilidade**: Q1 2027 (sujeito a contrato Bentley)

**Capacidades iniciais**:
- Rail design optimization (geometry, cant, grades)
- Track geometry validation
- Via permanente recommendations

**API Endpoint**: `https://api.bentley.com/copilot/` (TBD)

**Latência esperada**: 15-30s

---

### 4.2 OpenRail Integration Path

**Fase 1 (Q1 2027)**: Validação de viabilidade com Bentley
- Teste de MCP integration
- Prototipagem de workflows

**Fase 2 (Q2 2027)**: Integração full
- Connecção com OpenRail projects
- Export/import LandXML bidirecional

---

## 5. LANDXML IMPORT SPECIFICATION (Railway)

### 5.1 Estrutura LandXML Esperada para Ferrovias

```xml
<?xml version="1.0" encoding="utf-8"?>
<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.landxml.org/schema/LandXML-1.2
                             http://www.landxml.org/schema/LandXML-1.2/LandXML-1.2.xsd"
         date="2026-07-01" version="1.2">
    
    <Project name="Ferrovia Regional - km0 a km50">
        <Application name="Civil 3D" version="2024" manufacturer="Autodesk"/>
        
        <!-- Superfície (topografia) -->
        <Surfaces>
            <Surface name="Levantamento_Topografico" dateTime="2026-06-15">
                <SourceData>
                    <Cogo>
                        <Point id="P1" name="TM-001">
                            <Coordinates>300000.00 7000000.00 45.23</Coordinates>
                        </Point>
                        <Point id="P2" name="TM-002">
                            <Coordinates>300050.00 7000000.00 45.45</Coordinates>
                        </Point>
                        <!-- mais pontos -->
                    </Cogo>
                </SourceData>
                <Triangles>
                    <Triangle id="TR1" p1="P1" p2="P2" p3="P3"/>
                    <!-- mais triângulos -->
                </Triangles>
            </Surface>
        </Surfaces>
        
        <!-- Alinhamento (eixo de trilho) -->
        <Alignments>
            <Alignment name="Eixo_Ferrovia_Regional" staStart="0+0.00" length="50000.00">
                <CogoPoints>
                    <CogoPoint id="PI1" name="Km0">
                        <Coordinates>300000.00 7000000.00</Coordinates>
                    </CogoPoint>
                    <CogoPoint id="PI2" name="Km10">
                        <Coordinates>310000.00 7001200.00</Coordinates>
                    </CogoPoint>
                    <CogoPoint id="PI3" name="Km20">
                        <Coordinates>320000.00 7000800.00</Coordinates>
                    </CogoPoint>
                    <CogoPoint id="PI4" name="Km50">
                        <Coordinates>350000.00 7005000.00</Coordinates>
                    </CogoPoint>
                </CogoPoints>
                
                <!-- Tangentes -->
                <Line name="Tangent1" length="10000.00">
                    <Start>0+0.00</Start>
                    <End>0+10000.00</End>
                    <Bearing>45.0</Bearing>
                </Line>
                
                <!-- Curvas ferroviárias -->
                <Curve name="Curva1" radius="2000.00" length="500.00" dir="L">
                    <Start>0+10000.00</Start>
                    <End>0+10500.00</End>
                </Curve>
                
                <!-- mais geometria -->
            </Alignment>
        </Alignments>
        
        <!-- Perfil vertical (greide ferroviário) -->
        <Profiles>
            <Profile name="Greide_Ferrovia" alignmentRef="Eixo_Ferrovia_Regional">
                <ProfileGeometry>
                    <PVI name="VI1" station="0+0.00" elevation="45.00"/>
                    <PVI name="VI2" station="0+10000.00" elevation="50.00"/>
                    <PVI name="VI3" station="0+20000.00" elevation="52.50"/>
                    <PVI name="VI4" station="0+50000.00" elevation="48.00"/>
                </ProfileGeometry>
            </Profile>
        </Profiles>
        
    </Project>
</LandXML>
```

### 5.2 Parsing LandXML (Python)

```python
import lxml.etree as etree
from dataclasses import dataclass
from typing import List

@dataclass
class RailPoint:
    x: float
    y: float
    z: float
    name: str = ""

@dataclass
class RailCurve:
    name: str
    radius: float
    length: float
    direction: str  # L ou R

def parse_railway_landxml(filepath: str) -> Dict[str, Any]:
    """Parse LandXML 1.2 para projeto ferroviário."""
    
    tree = etree.parse(filepath)
    root = tree.getroot()
    ns = {"landxml": "http://www.landxml.org/schema/LandXML-1.2"}
    
    # Extract topografia
    surface_elem = root.find(".//landxml:Surface", ns)
    surface_points = []
    for point_elem in surface_elem.findall(".//landxml:Point", ns):
        coords_text = point_elem.find("landxml:Coordinates", ns).text
        x, y, z = map(float, coords_text.split())
        surface_points.append(RailPoint(x=x, y=y, z=z, name=point_elem.get("name")))
    
    # Extract alinhamento (eixo trilho)
    alignment_elem = root.find(".//landxml:Alignment", ns)
    rail_pis = []
    for cogo_point in alignment_elem.findall(".//landxml:CogoPoint", ns):
        coords_text = cogo_point.find("landxml:Coordinates", ns).text
        x, y = map(float, coords_text.split()[:2])
        rail_pis.append(RailPoint(x=x, y=y, z=0, name=cogo_point.get("name")))
    
    # Extract curvas
    rail_curves = []
    for curve_elem in alignment_elem.findall(".//landxml:Curve", ns):
        rail_curves.append(RailCurve(
            name=curve_elem.get("name"),
            radius=float(curve_elem.get("radius")),
            length=float(curve_elem.get("length")),
            direction=curve_elem.get("dir"),
        ))
    
    # Extract perfil (greide ferroviário)
    profile_elem = root.find(".//landxml:Profile", ns)
    profile_points = []
    for pvi in profile_elem.findall(".//landxml:PVI", ns):
        station_str = pvi.get("station").replace("+", "")
        station = float(station_str) if station_str else 0
        elevation = float(pvi.get("elevation"))
        profile_points.append({"station": station, "elevation": elevation})
    
    return {
        "surface_points": surface_points,
        "rail_alignment_pis": rail_pis,
        "rail_curves": rail_curves,
        "profile": profile_points,
        "metadata": extract_metadata(root, ns),
    }
```

---

## 6. EZDXF PARSER & DXF OUTPUT (Railway)

### 6.1 DXF Input Parsing (Railway-specific)

```python
import ezdxf

def extract_rail_alignment_from_dxf(dxf_doc: ezdxf.Drawing) -> List[tuple]:
    """Extrai eixo de trilho de DXF (camada ALINHAMENTO_TRILHO)."""
    
    alignment = []
    mspace = dxf_doc.modelspace()
    
    for entity in mspace.query('LWPOLYLINE[layer=="ALINHAMENTO_TRILHO"]'):
        for point in entity.get_points():
            alignment.append(point[:3])  # (x, y, z)
    
    return alignment

def extract_ballast_blocks_from_dxf(dxf_doc: ezdxf.Drawing) -> Dict[str, Any]:
    """Extrai layout de lastro de camada BALLAST."""
    
    ballast = {"regions": [], "dimensions": {}}
    mspace = dxf_doc.modelspace()
    
    for entity in mspace.query('POLYLINE[layer=="BALLAST"]'):
        points = [p[:2] for p in entity.get_points()]
        ballast["regions"].append({"points": points})
    
    return ballast

def validate_rail_layer_structure(dxf_doc: ezdxf.Drawing) -> List[str]:
    """Valida estrutura de layers conforme padrão ferroviário."""
    
    expected_layers = [
        "ALINHAMENTO_TRILHO", "PERFIL", "SECOES", "BALLAST",
        "DORMENTES", "AMV", "DRENAGEM", "COTAS", "HATCH", "TEXT",
    ]
    
    errors = []
    for layer in expected_layers:
        if layer not in dxf_doc.layers:
            errors.append(f"Missing layer: {layer}")
    
    return errors
```

### 6.2 DXF Output Generation (Railway)

```python
import ezdxf

def generate_railway_dxf(
    alignment: List[tuple],
    profile: Dict[float, float],
    ballast_sections: List[Dict],
    sleepers: List[Dict],
    output_file: str,
) -> str:
    """Gera DXF normalizado para projeto ferroviário."""
    
    # Criar novo desenho
    dwg = ezdxf.new(dxfversion="R2024")
    mspace = dwg.modelspace()
    
    # Adicionar layers com cores apropriadas
    dwg.layers.new(name="ALINHAMENTO_TRILHO", dxfattribs={"color": 1})  # Vermelho
    dwg.layers.new(name="PERFIL", dxfattribs={"color": 5})              # Cyan
    dwg.layers.new(name="BALLAST", dxfattribs={"color": 3})             # Verde
    dwg.layers.new(name="DORMENTES", dxfattribs={"color": 4})           # Magenta
    dwg.layers.new(name="DRENAGEM", dxfattribs={"color": 6})            # Magenta
    
    # Adicionar alinhamento (trilho)
    alignment_2d = [(p[0], p[1]) for p in alignment]
    rail_polyline = mspace.add_lwpolyline(alignment_2d)
    rail_polyline.dxf.layer = "ALINHAMENTO_TRILHO"
    rail_polyline.dxf.lineweight = 35
    
    # Adicionar perfil (greide)
    profile_points = []
    for station, elevation in sorted(profile.items()):
        profile_points.append((station, elevation))
    
    profile_polyline = mspace.add_lwpolyline(profile_points)
    profile_polyline.dxf.layer = "PERFIL"
    profile_polyline.dxf.lineweight = 35
    
    # Adicionar anotações (estacas, cotas)
    for station, elevation in sorted(profile.items())[:20]:
        text = mspace.add_text(
            f"Est {station:.0f}m\n{elevation:.2f}m",
            dxfattribs={"insert": (station, elevation + 5), "height": 2.5}
        )
        text.dxf.layer = "COTAS"
    
    # Salvar
    dwg.saveas(output_file)
    return output_file
```

---

## 7. PLAYBOOK OPERACIONAL S3

### 7.1 Intake Estruturado

**Checklist de entrada (usuário S3 preenchido no chat)**:

1. **Dados básicos**:
   - [ ] Nome do projeto (ex: "Ferrovia Regional Km0-Km50")
   - [ ] Tipo via (via singela, dupla)
   - [ ] Bitola (métrica 1000mm, larga 1600mm, dupla 1435mm)
   - [ ] Velocidade projeto (km/h)

2. **Arquivos**:
   - [ ] LandXML com alinhamento e superfície
   - [ ] Levantamento topográfico (pontos, DEM)
   - [ ] PDF do projeto anterior (se houver)

3. **Restrições**:
   - [ ] Raios mínimos obrigatórios
   - [ ] Áreas urbanas vs. rurais
   - [ ] Drenagem adequada (CBR mínimo)

4. **Normas**:
   - [ ] NBR 8932 (bitola)
   - [ ] NBR 8933 (documentação)
   - [ ] NBR 8934 (aparelhos de via)

---

### 7.2 Processos Automáticos (Orchestration)

#### Process-1: LandXML Parse & Validate
```yaml
trigger: landxml_received
steps:
  - parse_railway_landxml()
  - validate_coordinate_system()
  - extract_alignment_pis()
  - extract_curves()
  - output: railway_data (JSON)
timeout: 5m
```

#### Process-2: Rail Geometry & Superelevation
```yaml
trigger: railway_data ready
steps:
  - calc_rail_superelevation()
  - validate_min_radius()
  - generate_transition_curves()
  - output: geometry_data (JSON)
timeout: 8m
```

#### Process-3: Via Permanente Design
```yaml
trigger: geometry_data ready
steps:
  - design_ballast_and_sleepers()
  - spec_amv_apparatus()
  - calc_geotechnical_requirements()
  - output: via_perm_spec (JSON)
timeout: 12m
```

#### Process-4: Bentley Copilot (Q1 2027)
```yaml
trigger: geometry + via_perm ready
steps:
  - call_bentley_copilot_rail_design()
  - validate_recommendations()
  - output: copilot_recommendations (JSON)
timeout: 40m
retry: 2
enabled_q1_2027: true
```

#### Process-5: Seção Transversais & 3D
```yaml
trigger: all geometry ready
steps:
  - generate_cross_sections()
  - create_3d_mesh()
  - calc_earthwork_volumes()
  - output: sections_dir + 3d_model
timeout: 20m
```

#### Process-6: DXF Output Normalization
```yaml
trigger: all components ready
steps:
  - generate_railway_dxf()
  - apply_layer_rules()
  - validate_layer_structure()
  - output: ferrovia-PROJETO-BASICO.dxf
timeout: 5m
```

#### Process-7: Report & Compliance
```yaml
trigger: all processes complete
steps:
  - generate_nbr_compliance_report()
  - create_project_tables()
  - generate_playbook_next_steps()
  - output: RELATORIO-NBR8932.pdf + TABELAS.xlsx + PLAYBOOK-S3.md
timeout: 10m
```

---

### 7.3 Saída (Deliverables)

Após sucesso em todos os processos, usuário recebe:

**Arquivos**:
1. `[projeto]-PROJETO-BASICO.dxf` (alinhamento + perfil + seções)
2. `[projeto]-PROJETO-EXECUTIVO.dxf` (+ via permanente, AMV, drenagem)
3. `RELATORIO-VALIDACAO-NBR8932.pdf` (checklist + recomendações)
4. `TABELAS-PROJETO.xlsx` (estacas, cotas, cant, ballast volumes, dormentes)
5. `PLAYBOOK-S3-[projeto].md` (próximos passos, detalhes design)
6. `SECOES/` (pasta com seções transversais DXF)
7. `3D_MODEL_[projeto].dxf` ou `.obj` (modelo 3D da via)

**Documentação no chat**:
- Resumo de mudanças (perfil vs. topografia)
- Volumes de terra (corte/aterro)
- Specs via permanente (ballast, dormentes, AMV)
- Recomendações críticas
- Sinalizadores de risco

---

## 8. TIMELINE & DEPENDÊNCIAS (Q1 2027 → Q2 2027)

### 8.1 Fases de Entrega

| Fase | Período | Entregáveis | Dependências |
|------|---------|-------------|--------------|
| **Alpha** | Q1 2027 (Jan-Mar) | LandXML parser + Rail geometry engine + Via perm. validator | lxml, ezdxf |
| **Beta** | Q1 2027 (Mar-Apr) | Bentley decision matrix + DXF output + NBR compliance | Bentley docs |
| **Gamma** | Q2 2027 (Apr-Jun) | Bentley Copilot MCP (se disponível) + seções 3D | Bentley API (Q1 2027) |
| **GA** | Q2 2027 (Jun) | Full integration + training + documentation | All above + user feedback |

### 8.2 Dependências Técnicas

```
lxml + XSD validators
├─ LandXML parsing (✅ available)
└─ schema validation (✅ available)

ezdxf 1.2+
├─ DXF parser (✅ available)
└─ DXF writer (✅ available)

NBR 8932-8934 Rules Engine
├─ Superelevação logic (✅ available)
├─ Gauge validation (✅ available)
└─ Via permanente specs (✅ available)

Bentley Partnership
├─ OpenRail API docs (🔄 Q1 2027)
├─ Copilot MCP endpoint (🔄 Q1 2027)
└─ Rate limits, auth (TBD)

Civil 3D Rail Tools (Fallback)
├─ Rail design module (✅ available)
└─ Export/import LandXML (✅ available)
```

### 8.3 Gráfico de Gantt

```
Q1 2027 ━━━━━━━ | Q2 2027 ━━━━━━━
 J  F  M  │  A  M  J  │

[LandXML Parser ▓▓▓▓▓]
 [Rail Geometry Engine ▓▓▓▓▓]
  [Via Perm Validator ▓▓▓▓▓]
   [Bentley Decision Matrix ▓▓▓]
    [DXF Output Rail ▓▓▓▓▓▓]
      [NBR Compliance Check ▓▓▓]
       [Bentley Copilot (if avail) ▓▓▓▓▓▓▓]
        [Section Generation ▓▓▓▓▓▓]
         [Integration Testing ▓▓▓▓▓]
          [User Training ▓▓▓▓]
           [GA Release ▓]
```

---

## 9. RISCOS & MITIGAÇÃO

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Bentley API delays (Q1 2027) | Médio | Alto | Manter fallback Civil 3D, decision matrix sem MCP |
| LandXML formato variável | Alto | Médio | Suportar múltiplos dialetos, lenient validation |
| Via permanente specs inadequados | Médio | Médio | Validação por especialista, flag de revisão |
| Superelevação otimização (curvas complexas) | Baixo | Médio | Especialista review em curvas >2000m |
| Performance seções >100km | Baixo | Médio | Chunking automático, processamento paralelo |

---

## 10. SUCESSO & KPIs

### 10.1 Métricas de Qualidade

1. **Conformidade NBR 8932-8934**: 100% dos projetos passam checklist
2. **Tempo médio processamento**: <90 min (ponta-a-ponta)
3. **Taxa de erro via permanente**: <1% necessidade de ajustes
4. **Reuso de playbook**: >85% dos usuários utilizam output S3 direto em fase executiva

### 10.2 Adoção

- **Q1 2027**: 3 projetos piloto (internos)
- **Q2 2027**: 10 projetos (clientes beta)
- **Q3 2027**: 30+ projetos (produção)

---

## 11. PRÓXIMOS PASSOS

1. **Gate Humano** (MN approval) — este documento + plano risco (1 semana)
2. **Contract Bentley** — assinatura SLA + API keys / MCP access (4 semanas)
3. **Dev Alpha Sprint** — LandXML parser + Rail geometry engine (6 semanas, Q1 2027)
4. **Dev Beta Sprint** — Decision matrix + DXF output + NBR compliance (4 semanas, Q1 2027)
5. **Dev Gamma Sprint** — Bentley Copilot integration (se disponível) + seções 3D (6 semanas, Q1-Q2 2027)
6. **Testing & Validation** — 3 projetos piloto (4 semanas, Q2 2027)
7. **GA Release** — documentação + training (2 semanas, Q2 2027)

---

## REFERÊNCIAS

- **NBR 8932** — Bitola de via férrea
- **NBR 8933** — Documentação de projeto de ferrovia
- **NBR 8934** — Aparelhos de via (AMV)
- **Bentley OpenRail Documentation**: [Link TBD, Q1 2027]
- **Civil 3D Rail Tools**: https://www.autodesk.com/products/civil-3d/
- **LandXML Specification 1.2**: https://www.landxml.org/
- **ABNT NBR 13142** — Desenho técnico (aplicável)
- **Manta SICRO Integration**: [Internal wiki, access via SharePoint]
- **AMV Standards (ABNT/DNIT)**: [Internal reference library]

---

**Aprovações Pendentes**:
- [ ] MN (Arquiteto IA) — estratégia geral
- [ ] CTO Infraestrutura — arquitetura técnica
- [ ] Bentley Partnership Manager — viabilidade técnica
- [ ] CFO — orçamento Q1 2027 → Q2 2027
