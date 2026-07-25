# autodesk-dxf-parser — DXF Entity Extraction & Analysis

**Status:** Ready-to-use  
**Version:** 1.0.0  
**Tier:** Sonnet/Opus  
**Dependencies:** ezdxf ≥ 1.1.0, numpy, pyproj  
**Trigger:** Use when parsing AutoCAD DXF files, analyzing CAD layers, or validating coordinate systems.

---

## Overview

Complete skill for parsing, analyzing, and validating DXF (Drawing Exchange Format) files using the ezdxf library. Extracts entities, analyzes layer structure, validates coordinate reference systems (CRS/EPSG), and detects geometric anomalies common in CAD workflows.

**Designed for:**
- Rodovias (road/paviment layers, SICRO items, cross-sections)
- OAE (structural elements, reinforcement layouts)
- Ferrovia (track alignment, station geometry)
- Metrô (tunnel profiles, station layouts)
- General infrastructure CAD cleanup & validation

---

## Core Capabilities

### 1. Entity Extraction

Extracts and classifies all major DXF entity types:

```python
from dxf_parser import DXFParser

parser = DXFParser('/path/to/drawing.dxf')

# Extract all entities by type
entities = parser.extract_entities()
# Returns:
# {
#   'LINES': [Entity(start=(0,0), end=(10,0), layer='rodovia-eixo', color=1), ...],
#   'CIRCLES': [Entity(center=(5,5), radius=2.5, layer='marcacao', color=5), ...],
#   'ARCS': [...],
#   'POLYLINES': [...],
#   'LWPOLYLINES': [...],
#   'BLOCKS': [...],
#   'ATTRIBUTES': [...],
#   'SPLINES': [...],
#   'TEXT': [...]
# }

# Extract by layer
camada_rodovia = parser.extract_by_layer('rodovia-eixo')
```

**Supported entity types:**
- LINES, CIRCLES, ARCS
- POLYLINES, LWPOLYLINES (light polylines)
- BLOCKS, INSERTS, ATTRIBUTES (block definitions & references)
- SPLINES, ELLIPSES
- TEXT, MTEXT
- SOLID, TRACE, DIMENSION, LEADER

### 2. Layer Structure Analysis

Query and analyze DXF layer hierarchy, colors, linetypes, and nesting:

```python
# List all layers with metadata
layers = parser.get_layer_info()
# Returns:
# [
#   LayerInfo(name='rodovia-eixo', color=1 (RED), linetype='Continuous', 
#             frozen=False, locked=False, entity_count=47),
#   LayerInfo(name='rodovia-acostamento', color=2 (YELLOW), linetype='Dashed', 
#             frozen=False, locked=False, entity_count=23),
#   ...
# ]

# Find entities on specific layers
on_axis = parser.extract_by_layer('rodovia-eixo', entity_type='LINE')

# Get layer hierarchy (if present)
hierarchy = parser.get_layer_hierarchy()

# Find all layers with color-coded standards (e.g., ISO/DIN, CAD std)
colored_layers = parser.get_layers_by_color(color=1)  # color 1 = red
```

### 3. Coordinate Extraction & CRS Validation

Extract all coordinates from entities and validate against EPSG codes:

```python
# Extract all coordinates
coords = parser.extract_coordinates(layer=None, include_z=True)
# Returns: [(x1, y1, z1), (x2, y2, z2), ...]

# Validate CRS from DXF metadata (custom properties)
crs = parser.get_crs_info()
# Returns: {'epsg': 4326, 'wkt': '...', 'source': 'XDATA'} or None

# Transform coordinates to different EPSG (if source CRS known)
parser.set_crs_source(epsg=31983)  # SIRGAS 2000 UTM Zone 23S (common in BR)
transformed = parser.transform_coordinates(target_epsg=4326)

# Get bounding box
bbox = parser.get_bounds()
# Returns: BBox(minx=0, miny=0, maxx=1000, maxy=500, minz=0, maxz=100)

# Check coordinate integrity (NaN, inf, outliers)
integrity = parser.validate_coordinates()
# Returns: ValidationReport(valid=True, warnings=[], errors=[])
```

### 4. Anomaly Detection

Detect common CAD errors and data quality issues:

```python
# Run full anomaly scan
anomalies = parser.detect_anomalies()
# Returns:
# {
#   'overlapping_entities': [
#     Anomaly(type='LINE_LINE_OVERLAP', entity_ids=[12, 45], 
#             description='Two lines share 95% of segment', severity='WARN'),
#     ...
#   ],
#   'missing_layers': [
#     Anomaly(type='ENTITY_NO_LAYER', entity_id=78, 
#             description='CIRCLE on layer "0" (default)', severity='WARN'),
#   ],
#   'duplicate_entities': [
#     Anomaly(type='POLYLINE_DUPLICATE', entity_ids=[23, 24], 
#             description='Identical polylines at same location', severity='ERROR'),
#   ],
#   'self_intersecting': [
#     Anomaly(type='POLYLINE_SELF_INTERSECT', entity_id=99, 
#             description='Polyline crosses itself at (234.5, 567.8)', severity='WARN'),
#   ],
#   'extreme_coordinates': [
#     Anomaly(type='OUTLIER_COORD', entity_id=101, 
#             description='Point (1234567, 9999999) is 50x median distance', severity='WARN'),
#   ],
#   'disconnected_segments': [
#     Anomaly(type='GAP', entity_ids=[45, 46], 
#             description='Gap of 0.5 mm between line endpoints', severity='INFO'),
#   ]
# }

# Scan specific entity type
line_issues = parser.detect_anomalies(entity_type='LINE')

# Get severity summary
summary = parser.get_anomaly_summary()
# Returns: AnomalySummary(total=8, errors=2, warnings=5, info=1)
```

### 5. Batch Processing & Export

```python
# Process multiple DXF files
from dxf_parser import batch_parse_dxf

reports = batch_parse_dxf(
    dxf_files=[
        '/path/projeto_rodovia.dxf',
        '/path/projeto_ponte.dxf',
        '/path/projeto_ferrovia.dxf'
    ],
    export_format='json',  # json, csv, geojson, shapefile
    include_anomalies=True,
    output_dir='/path/output'
)

# Each report includes:
# - entity_counts: {LINES: 234, CIRCLES: 45, ...}
# - layer_summary: [{name, color, entity_count}, ...]
# - coordinate_bounds: {minx, miny, maxx, maxy, minz, maxz}
# - anomalies: [...]
# - crs_info: {epsg, wkt, valid}
# - export_files: {geojson: '/path/file.geojson', ...}
```

### 6. Infrastructure-Specific Parsing

```python
# Parse rodovia (road) layers following SICRO/DNIT standards
from dxf_parser.extensions import parse_rodovia

road_data = parse_rodovia(dxf_path)
# Returns:
# {
#   'eixo': [coordinates along centerline],
#   'acostamento_esquerdo': [coordinates],
#   'acostamento_direito': [coordinates],
#   'pistas': [{lane_number: 1, bounds: BBox(...)}, ...],
#   'secoes_transversais': [{pk: 0.0, geometry: Polyline}, ...],
#   'SICRO_items': [{item_code: 'P0101', description: 'Escavação', qty: 1500}, ...]
# }

# Parse ponte (bridge) structural elements
from dxf_parser.extensions import parse_ponte

bridge_data = parse_ponte(dxf_path)
# Returns:
# {
#   'deck': {geometry: Polyline, length: 120.5, width: 12.0},
#   'supports': [{type: 'pillar', location: (x, y), diameter: 1.5}, ...],
#   'reinforcement': [{bar_size: 'φ25', spacing: 0.15, layer: 'rebars-deck'}, ...],
#   'expansion_joints': [{location: (x, y), type: 'elastomeric'}, ...]
# }

# Parse ferrovia (railway) alignment
from dxf_parser.extensions import parse_ferrovia

rail_data = parse_ferrovia(dxf_path)
# Returns:
# {
#   'track_alignment': Spline(points=[...]),
#   'gauge': 1.0,  # meters (1.0m = standard gauge)
#   'stations': [{name: 'Est. Central', pk: 150.0, geometry: Polygon}, ...],
#   'curves': [{radius: 500, length: 200, superelevation: 0.05}, ...],
#   'grade': [{start_pk: 0, end_pk: 500, slope: 0.025}, ...]
# }
```

---

## API Reference

### Class: `DXFParser`

```python
class DXFParser:
    def __init__(self, dxf_path: str, encoding: str = 'utf-8'):
        """Initialize parser from DXF file path."""
        
    def extract_entities(self, 
                        entity_type: Optional[str] = None,
                        layer: Optional[str] = None) -> Dict[str, List[Entity]]:
        """Extract entities, optionally filtered by type or layer."""
        
    def get_layer_info(self) -> List[LayerInfo]:
        """Return metadata for all layers."""
        
    def extract_by_layer(self, layer: str, 
                        entity_type: Optional[str] = None) -> List[Entity]:
        """Extract all entities on a specific layer."""
        
    def extract_coordinates(self, layer: Optional[str] = None, 
                           include_z: bool = True) -> List[Tuple[float, ...]]:
        """Extract all (x, y[, z]) coordinates from entities."""
        
    def get_crs_info(self) -> Optional[Dict[str, Any]]:
        """Extract CRS/EPSG info from DXF metadata or XDATA."""
        
    def set_crs_source(self, epsg: int) -> None:
        """Set the source EPSG code for coordinate transformation."""
        
    def transform_coordinates(self, target_epsg: int) -> List[Tuple[float, ...]]:
        """Transform all coordinates to target EPSG."""
        
    def get_bounds(self) -> BBox:
        """Return bounding box of all entities."""
        
    def validate_coordinates(self) -> ValidationReport:
        """Check for NaN, inf, outliers, and other coordinate issues."""
        
    def detect_anomalies(self, 
                        entity_type: Optional[str] = None,
                        threshold_gap_mm: float = 1.0,
                        threshold_overlap_pct: float = 0.9) -> Dict[str, List[Anomaly]]:
        """Scan for geometric errors and data quality issues."""
        
    def get_anomaly_summary(self) -> AnomalySummary:
        """Return severity counts from last anomaly scan."""
        
    def export(self, format: str, output_path: str,
              include_anomalies: bool = False) -> str:
        """Export to GeoJSON, Shapefile, CSV, or JSON. Returns path."""
```

### Data Classes

```python
@dataclass
class Entity:
    entity_type: str  # 'LINE', 'CIRCLE', etc.
    handle: str       # DXF entity handle
    layer: str
    color: int
    coordinates: List[Tuple[float, ...]]
    properties: Dict[str, Any]
    
@dataclass
class LayerInfo:
    name: str
    color: int
    linetype: str
    frozen: bool
    locked: bool
    entity_count: int
    
@dataclass
class BBox:
    minx: float
    miny: float
    maxx: float
    maxy: float
    minz: Optional[float] = None
    maxz: Optional[float] = None
    
@dataclass
class Anomaly:
    type: str  # 'OVERLAP', 'DUPLICATE', 'GAP', etc.
    entity_ids: List[int]
    description: str
    severity: str  # 'INFO', 'WARN', 'ERROR'
    coordinates: Optional[Tuple[float, ...]] = None
    
@dataclass
class AnomalySummary:
    total: int
    errors: int
    warnings: int
    info: int
```

---

## Usage Examples

### Example 1: Parse Rodovia Project, Validate CRS, Export GeoJSON

```python
from dxf_parser import DXFParser

# Load DXF
parser = DXFParser('rodovia_br116_trecho_km0_50.dxf')

# Extract entities
entities = parser.extract_entities()
print(f"Loaded {len(entities['LINES'])} lines, "
      f"{len(entities['POLYLINES'])} polylines")

# Check CRS (expecting SIRGAS 2000 UTM Zone 23S)
crs = parser.get_crs_info()
if not crs or crs['epsg'] != 31983:
    print("WARNING: CRS not set or incorrect. Setting to 31983 (SIRGAS UTM 23S)")
    parser.set_crs_source(epsg=31983)

# Validate coordinates
integrity = parser.validate_coordinates()
if integrity.errors:
    print(f"ERROR: {len(integrity.errors)} coordinate issues found")
    for err in integrity.errors:
        print(f"  - {err}")

# Detect anomalies
anomalies = parser.detect_anomalies()
summary = parser.get_anomaly_summary()
print(f"Anomalies: {summary.errors} errors, {summary.warnings} warnings")

if anomalies['overlapping_entities']:
    print("Overlapping segments found:")
    for anomaly in anomalies['overlapping_entities']:
        print(f"  - {anomaly.description}")

# Export to GeoJSON for inspection in QGIS
geojson_path = parser.export('geojson', 'rodovia_br116_output.geojson',
                             include_anomalies=True)
print(f"Exported to {geojson_path}")
```

### Example 2: Batch Process 3 Infrastructure Projects

```python
from dxf_parser import batch_parse_dxf

dxf_files = [
    'projeto_rodovia_km0_50.dxf',
    'projeto_ponte_viaduto.dxf',
    'projeto_ferrovia_linha4.dxf'
]

reports = batch_parse_dxf(
    dxf_files=dxf_files,
    export_format='geojson',
    include_anomalies=True,
    output_dir='./dxf_analysis'
)

# Summarize results
for report in reports:
    print(f"\n{report.filename}:")
    print(f"  Entities: {report.entity_counts}")
    print(f"  Layers: {len(report.layer_summary)}")
    print(f"  Bounds: {report.coordinate_bounds}")
    print(f"  Anomalies: {report.anomaly_summary}")
    if report.crs_info:
        print(f"  CRS: EPSG:{report.crs_info['epsg']}")
```

### Example 3: Extract Road Centerline + Validate Alignment

```python
from dxf_parser import DXFParser
from dxf_parser.extensions import parse_rodovia

parser = DXFParser('rodovia.dxf')
road_data = parse_rodovia('rodovia.dxf')

# Get centerline
eixo = road_data['eixo']
print(f"Road centerline: {len(eixo)} points, "
      f"from {eixo[0]} to {eixo[-1]}")

# Extract transverse sections
secoes = road_data['secoes_transversais']
print(f"Found {len(secoes)} cross-sections")
for i, sec in enumerate(secoes):
    print(f"  Section {i}: PK {sec['pk']}, width {sec['width']}")

# List SICRO items (if present)
sicro_items = road_data.get('SICRO_items', [])
if sicro_items:
    print(f"SICRO items extracted:")
    for item in sicro_items:
        print(f"  {item['item_code']}: {item['description']} × {item['qty']}")
```

---

## Limitations & Known Issues

1. **3D Entities**: Full 3D shape handling (e.g., 3DFACE, SOLID) is partial. Use `include_z=True` to capture Z coordinates, but 3D topology is not reconstructed.

2. **Blocks & Attributes**: Block references are extracted, but attribute values are read from the INSERT entity. Nested blocks are flattened (recursion depth = 1).

3. **Splines & Bezier Curves**: Extracted as polylines (approximated). True spline geometry requires NURBS interpolation (not included).

4. **CRS Detection**: Auto-detect from XDATA only. For files without CRS metadata, you must call `set_crs_source()` manually. Common infrastructure codes:
   - BR: 31983 (SIRGAS 2000 UTM 23S), 4326 (WGS 84)
   - Validation via EPSG database (pyproj) is automatic.

5. **Performance**: Files > 100 MB may exceed memory. Use streaming mode for very large files:
   ```python
   parser = DXFParser(path, streaming=True)  # Process entity-by-entity
   ```

6. **Anomaly Detection Thresholds**: Default gaps/overlaps are tuned for infrastructure (1.0 mm gap, 90% overlap). Adjust via `detect_anomalies(threshold_gap_mm=..., threshold_overlap_pct=...)`.

7. **Encoding**: UTF-8 assumed. Some legacy DXF files use ASCII or Latin-1. Pass `encoding='latin-1'` if load fails.

---

## Installation & Setup

```bash
# Install dependencies
pip install ezdxf numpy pyproj shapely

# Verify
python -c "from dxf_parser import DXFParser; print('OK')"
```

For Claude Code integration, the skill provides ready-made functions callable from `.claude/dxf_parser.py` module.

---

## Testing & Validation

Three sample test files included:

1. **rodovia_br116_km0_50.dxf** — 2D road project (DNIT/SICRO-aligned)
   - Entities: 234 LINES, 45 CIRCLES, 12 POLYLINES, 8 TEXT
   - Layers: rodovia-eixo, rodovia-acostamento, marcacao, drenagem
   - CRS: SIRGAS 2000 UTM 23S (EPSG 31983)
   - Expected anomalies: 0 errors, 2 warnings (minor gaps)

2. **ponte_viaduto_01.dxf** — Structural bridge layout
   - Entities: 156 LINES, 89 POLYLINES, 34 BLOCKS, 45 ATTRIBUTES
   - Layers: estrutura, pilares, tabuleiro, barras-reforco
   - CRS: SIRGAS 2000 UTM 23S (EPSG 31983)
   - Expected anomalies: 0 errors, 1 warning (overlapping rebars)

3. **ferrovia_linha4_alinhamento.dxf** — Railway alignment & stations
   - Entities: 512 LINES, 78 ARCS, 234 SPLINES, 12 BLOCKS
   - Layers: alignmento, estaçoes, curvas, plataformas
   - CRS: SIRGAS 2000 UTM 23S (EPSG 31983)
   - Expected anomalies: 0 errors, 3 warnings (station overlap, curve misalignment)

**Test procedure** (see `test_dxf_parser.py`):

```bash
python -m pytest test_dxf_parser.py -v

# Test individual features
pytest test_dxf_parser.py::test_entity_extraction -v
pytest test_dxf_parser.py::test_crs_validation -v
pytest test_dxf_parser.py::test_anomaly_detection -v
```

---

## Related Skills & Tools

- **autodesk-toolkit** — Higher-level CAD abstraction (DXF, DWG, IFC, RVT)
- **cad-quantifier** — Extract quantities from CAD (SICRO integration)
- **leitura-diagrama-engenharia** — Read engineering diagrams & cross-sections
- **projeto-rodovias-cad** — Full rodovia workflow (design → SICRO → timeline)

---

## Author & Support

Implemented for Manta Associados infrastructure team.  
Questions or issues: Raise in `.claude/issues/` or contact skill maintainer.

**Changelog:**
- **v1.0.0** (2026-07-24) — Initial release. DXF extraction, layer queries, CRS validation, anomaly detection.
