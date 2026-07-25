"""
Test suite for autodesk-dxf-parser skill
Tests entity extraction, layer queries, CRS validation, anomaly detection
"""

import pytest
import tempfile
from pathlib import Path
import json

try:
    from dxf_parser import (
        DXFParser, Entity, LayerInfo, BBox, Anomaly, AnomalySummary,
        ValidationReport, ParseReport, batch_parse_dxf
    )
except ImportError:
    pytest.skip("dxf_parser module not found", allow_module_level=True)

try:
    import ezdxf
except ImportError:
    pytest.skip("ezdxf not installed", allow_module_level=True)


# ============================================================================
# FIXTURES — Create Sample DXF Files
# ============================================================================

@pytest.fixture
def rodovia_dxf(tmp_path):
    """Create sample roadway project DXF."""
    dxf_path = tmp_path / "rodovia_br116_km0_50.dxf"

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Create layers (DNIT/SICRO aligned)
    for layer_name, color in [
        ('rodovia-eixo', 1),  # RED
        ('rodovia-acostamento', 2),  # YELLOW
        ('marcacao', 5),  # CYAN
        ('drenagem', 3)  # GREEN
    ]:
        doc.layers.new(name=layer_name, dxfattribs={'color': color})

    # Draw centerline (eixo)
    centerline_points = [
        (0, 0), (100, 50), (200, 100), (300, 150), (400, 200),
        (500, 250), (600, 300), (700, 350), (800, 400), (900, 450)
    ]
    msp.add_lwpolyline(centerline_points, dxfattribs={'layer': 'rodovia-eixo', 'color': 1})

    # Draw shoulders (acostamento)
    shoulder_points = [(x, y + 3.5) for x, y in centerline_points]
    msp.add_lwpolyline(shoulder_points, dxfattribs={'layer': 'rodovia-acostamento', 'color': 2})

    # Add cross-section markers
    for i in range(0, 10):
        x = i * 100
        y = (i * 50) if i > 0 else 0
        # Transverse line
        msp.add_line((x - 10, y - 5), (x + 10, y + 5),
                    dxfattribs={'layer': 'marcacao', 'color': 5})
        # Station text
        msp.add_text(f'PK {i * 50}', dxfattribs={'layer': 'marcacao', 'insert': (x, y - 10)})

    # Add drainage
    for i in range(2, 8):
        msp.add_circle((i * 120, 100), radius=2.0, dxfattribs={'layer': 'drenagem', 'color': 3})

    doc.saveas(str(dxf_path))
    return dxf_path


@pytest.fixture
def ponte_dxf(tmp_path):
    """Create sample bridge structure DXF."""
    dxf_path = tmp_path / "ponte_viaduto_01.dxf"

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Create layers
    for layer_name, color in [
        ('estrutura', 1),
        ('pilares', 2),
        ('tabuleiro', 5),
        ('barras-reforco', 3)
    ]:
        doc.layers.new(name=layer_name, dxfattribs={'color': color})

    # Draw deck (tabuleiro)
    deck = [(0, 0), (120, 0), (120, 12), (0, 12)]
    msp.add_lwpolyline(deck, dxfattribs={'layer': 'tabuleiro', 'color': 5})

    # Draw pillars (pilares)
    pillar_x_positions = [30, 60, 90]
    for x in pillar_x_positions:
        msp.add_line((x, 0), (x, -15), dxfattribs={'layer': 'pilares', 'color': 2})
        msp.add_circle((x, 0), radius=1.5, dxfattribs={'layer': 'pilares', 'color': 2})

    # Draw reinforcement (barras-reforco)
    for i in range(0, 10):
        msp.add_line((i * 12, 2), (i * 12, 10), dxfattribs={'layer': 'barras-reforco', 'color': 3})

    # Add some attributes via blocks
    block = doc.blocks.new(name='PILLAR_ATTR')
    block.add_text('PHC 1.5m', dxfattribs={'height': 2})

    msp.add_blockref('PILLAR_ATTR', (30, -15))
    msp.add_blockref('PILLAR_ATTR', (60, -15))
    msp.add_blockref('PILLAR_ATTR', (90, -15))

    doc.saveas(str(dxf_path))
    return dxf_path


@pytest.fixture
def ferrovia_dxf(tmp_path):
    """Create sample railway alignment DXF."""
    dxf_path = tmp_path / "ferrovia_linha4_alinhamento.dxf"

    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Create layers
    for layer_name, color in [
        ('alignmento', 1),
        ('estaçoes', 2),
        ('curvas', 5),
        ('plataformas', 3)
    ]:
        doc.layers.new(name=layer_name, dxfattribs={'color': color})

    # Draw track alignment
    alignment_points = [
        (0, 0), (50, 10), (100, 30), (150, 60), (200, 100),
        (250, 140), (300, 170), (350, 180), (400, 175), (450, 160)
    ]
    msp.add_lwpolyline(alignment_points, dxfattribs={'layer': 'alignmento', 'color': 1})

    # Add parallel track (gauge = 1.0m)
    offset_alignment = [(x, y - 1.0) for x, y in alignment_points]
    msp.add_lwpolyline(offset_alignment, dxfattribs={'layer': 'alignmento', 'color': 1})

    # Add stations
    stations = [
        ('Estação Central', 100, 30),
        ('Estação Santa Cruz', 200, 100),
        ('Estação Oeste', 350, 180)
    ]
    for name, x, y in stations:
        # Station platform
        platform_box = [(x - 5, y - 10), (x + 5, y - 10), (x + 5, y + 10), (x - 5, y + 10)]
        msp.add_lwpolyline(platform_box, dxfattribs={'layer': 'plataformas', 'color': 3})
        msp.add_text(name, dxfattribs={'layer': 'estaçoes', 'insert': (x - 3, y)})

    # Add curve markers
    for x, y in alignment_points[1:-1]:
        msp.add_circle((x, y), radius=5, dxfattribs={'layer': 'curvas', 'color': 5})

    doc.saveas(str(dxf_path))
    return dxf_path


# ============================================================================
# TESTS — Entity Extraction
# ============================================================================

class TestEntityExtraction:
    """Test entity extraction and conversion."""

    def test_load_rodovia_dxf(self, rodovia_dxf):
        """Test loading a roadway DXF file."""
        parser = DXFParser(str(rodovia_dxf))
        assert parser._doc is not None

    def test_extract_all_entities(self, rodovia_dxf):
        """Test extracting all entities."""
        parser = DXFParser(str(rodovia_dxf))
        entities = parser.extract_entities()

        assert isinstance(entities, dict)
        assert 'LWPOLYLINE' in entities or 'POLYLINE' in entities
        assert 'TEXT' in entities or len(entities) > 0

    def test_extract_by_type(self, rodovia_dxf):
        """Test extracting specific entity type."""
        parser = DXFParser(str(rodovia_dxf))
        lines = parser.extract_entities(entity_type='LINE')

        assert isinstance(lines, dict)
        assert 'LINE' in lines

    def test_extract_by_layer(self, rodovia_dxf):
        """Test extracting from specific layer."""
        parser = DXFParser(str(rodovia_dxf))
        eixo_entities = parser.extract_by_layer('rodovia-eixo')

        assert isinstance(eixo_entities, list)
        assert len(eixo_entities) > 0
        assert all(e.layer == 'rodovia-eixo' for e in eixo_entities)

    def test_entity_properties(self, rodovia_dxf):
        """Test entity properties extraction."""
        parser = DXFParser(str(rodovia_dxf))
        entities = parser.extract_entities()

        # Check that entities have required properties
        for ent_list in entities.values():
            for entity in ent_list:
                assert hasattr(entity, 'entity_type')
                assert hasattr(entity, 'layer')
                assert hasattr(entity, 'color')
                assert hasattr(entity, 'coordinates')


# ============================================================================
# TESTS — Layer Analysis
# ============================================================================

class TestLayerAnalysis:
    """Test layer structure and metadata."""

    def test_get_layer_info(self, rodovia_dxf):
        """Test retrieving layer information."""
        parser = DXFParser(str(rodovia_dxf))
        layers = parser.get_layer_info()

        assert isinstance(layers, list)
        assert len(layers) > 0
        assert all(isinstance(l, LayerInfo) for l in layers)

    def test_layer_properties(self, rodovia_dxf):
        """Test layer metadata."""
        parser = DXFParser(str(rodovia_dxf))
        layers = parser.get_layer_info()

        for layer in layers:
            assert isinstance(layer.name, str)
            assert isinstance(layer.color, int)
            assert isinstance(layer.frozen, bool)

    def test_get_layers_by_color(self, rodovia_dxf):
        """Test filtering layers by color."""
        parser = DXFParser(str(rodovia_dxf))
        red_layers = parser.get_layers_by_color(1)

        assert isinstance(red_layers, list)
        assert all(l.color == 1 for l in red_layers)

    def test_get_layer_hierarchy(self, rodovia_dxf):
        """Test layer hierarchy detection."""
        parser = DXFParser(str(rodovia_dxf))
        hierarchy = parser.get_layer_hierarchy()

        assert isinstance(hierarchy, dict)
        # Layers starting with 'rodovia' should be grouped
        if 'rodovia' in hierarchy:
            assert len(hierarchy['rodovia']) > 0


# ============================================================================
# TESTS — Coordinate Extraction & Bounds
# ============================================================================

class TestCoordinateExtraction:
    """Test coordinate extraction and bounding boxes."""

    def test_extract_coordinates(self, rodovia_dxf):
        """Test extracting coordinates."""
        parser = DXFParser(str(rodovia_dxf))
        coords = parser.extract_coordinates()

        assert isinstance(coords, list)
        assert len(coords) > 0
        assert all(isinstance(c, tuple) for c in coords)

    def test_get_bounds(self, rodovia_dxf):
        """Test bounding box calculation."""
        parser = DXFParser(str(rodovia_dxf))
        bbox = parser.get_bounds()

        assert isinstance(bbox, BBox)
        assert bbox.minx < bbox.maxx
        assert bbox.miny < bbox.maxy

    def test_bounds_properties(self, rodovia_dxf):
        """Test bounding box width/height properties."""
        parser = DXFParser(str(rodovia_dxf))
        bbox = parser.get_bounds()

        width = bbox.width
        height = bbox.height

        assert width > 0
        assert height > 0

    def test_validate_coordinates(self, rodovia_dxf):
        """Test coordinate validation."""
        parser = DXFParser(str(rodovia_dxf))
        report = parser.validate_coordinates()

        assert isinstance(report, ValidationReport)
        assert isinstance(report.valid, bool)
        assert isinstance(report.errors, list)


# ============================================================================
# TESTS — CRS Handling
# ============================================================================

class TestCRSHandling:
    """Test coordinate reference system handling."""

    def test_set_crs_source(self, rodovia_dxf):
        """Test setting source CRS."""
        parser = DXFParser(str(rodovia_dxf))
        parser.set_crs_source(epsg=31983)  # SIRGAS 2000 UTM 23S

        assert parser._crs_source is not None

    def test_invalid_epsg(self, rodovia_dxf):
        """Test invalid EPSG code."""
        parser = DXFParser(str(rodovia_dxf))

        with pytest.raises(ValueError):
            parser.set_crs_source(epsg=999999)

    def test_get_crs_info(self, rodovia_dxf):
        """Test CRS info retrieval."""
        parser = DXFParser(str(rodovia_dxf))
        crs_info = parser.get_crs_info()

        # May return None if not in DXF metadata
        assert crs_info is None or isinstance(crs_info, dict)


# ============================================================================
# TESTS — Anomaly Detection
# ============================================================================

class TestAnomalyDetection:
    """Test anomaly detection and reporting."""

    def test_detect_anomalies(self, rodovia_dxf):
        """Test anomaly detection."""
        parser = DXFParser(str(rodovia_dxf))
        anomalies = parser.detect_anomalies()

        assert isinstance(anomalies, dict)
        assert 'overlapping_entities' in anomalies
        assert 'missing_layers' in anomalies
        assert 'duplicate_entities' in anomalies

    def test_anomaly_summary(self, rodovia_dxf):
        """Test anomaly summary."""
        parser = DXFParser(str(rodovia_dxf))
        summary = parser.get_anomaly_summary()

        assert isinstance(summary, AnomalySummary)
        assert summary.total >= 0
        assert summary.errors >= 0
        assert summary.warnings >= 0

    def test_anomaly_structure(self, rodovia_dxf):
        """Test anomaly data structure."""
        parser = DXFParser(str(rodovia_dxf))
        anomalies = parser.detect_anomalies()

        for anomaly_list in anomalies.values():
            for anomaly in anomaly_list:
                assert hasattr(anomaly, 'type')
                assert hasattr(anomaly, 'entity_ids')
                assert hasattr(anomaly, 'severity')


# ============================================================================
# TESTS — Export
# ============================================================================

class TestExport:
    """Test data export in various formats."""

    def test_export_json(self, rodovia_dxf, tmp_path):
        """Test JSON export."""
        parser = DXFParser(str(rodovia_dxf))
        output = tmp_path / "export.json"

        result = parser.export('json', str(output))

        assert Path(result).exists()
        with open(result) as f:
            data = json.load(f)
            assert 'entities' in data
            assert 'layers' in data

    def test_export_csv(self, rodovia_dxf, tmp_path):
        """Test CSV export."""
        parser = DXFParser(str(rodovia_dxf))
        output = tmp_path / "export.csv"

        result = parser.export('csv', str(output))

        assert Path(result).exists()

    def test_export_geojson(self, rodovia_dxf, tmp_path):
        """Test GeoJSON export."""
        parser = DXFParser(str(rodovia_dxf))
        output = tmp_path / "export.geojson"

        try:
            result = parser.export('geojson', str(output))
            assert Path(result).exists()
        except ImportError:
            pytest.skip("shapely not installed")

    def test_export_with_anomalies(self, rodovia_dxf, tmp_path):
        """Test export with anomaly information."""
        parser = DXFParser(str(rodovia_dxf))
        output = tmp_path / "export_anomalies.json"

        result = parser.export('json', str(output), include_anomalies=True)

        assert Path(result).exists()
        with open(result) as f:
            data = json.load(f)
            assert 'anomalies' in data


# ============================================================================
# TESTS — Batch Processing
# ============================================================================

class TestBatchProcessing:
    """Test batch processing of multiple files."""

    def test_batch_parse(self, rodovia_dxf, ponte_dxf, ferrovia_dxf, tmp_path):
        """Test batch parsing of multiple DXF files."""
        dxf_files = [str(rodovia_dxf), str(ponte_dxf), str(ferrovia_dxf)]

        reports = batch_parse_dxf(
            dxf_files=dxf_files,
            output_dir=str(tmp_path),
            include_anomalies=True
        )

        assert len(reports) == 3
        assert all(isinstance(r, ParseReport) for r in reports)

    def test_batch_report_structure(self, rodovia_dxf, ponte_dxf, ferrovia_dxf, tmp_path):
        """Test batch report content."""
        dxf_files = [str(rodovia_dxf), str(ponte_dxf), str(ferrovia_dxf)]

        reports = batch_parse_dxf(
            dxf_files=dxf_files,
            export_format='json',
            output_dir=str(tmp_path)
        )

        for report in reports:
            assert isinstance(report.entity_counts, dict)
            assert isinstance(report.layer_summary, list)
            assert isinstance(report.coordinate_bounds, BBox)
            assert isinstance(report.anomaly_summary, AnomalySummary)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests across features."""

    def test_full_workflow_rodovia(self, rodovia_dxf, tmp_path):
        """Test full workflow on roadway project."""
        parser = DXFParser(str(rodovia_dxf))

        # Extract entities
        entities = parser.extract_entities()
        assert len(entities) > 0

        # Analyze layers
        layers = parser.get_layer_info()
        assert len(layers) > 0

        # Get bounds
        bounds = parser.get_bounds()
        assert bounds.width > 0

        # Detect anomalies
        anomalies = parser.detect_anomalies()
        summary = parser.get_anomaly_summary()
        assert summary.total >= 0

        # Export
        output = tmp_path / "full_workflow.json"
        parser.export('json', str(output), include_anomalies=True)
        assert Path(output).exists()

    def test_full_workflow_bridge(self, ponte_dxf, tmp_path):
        """Test full workflow on bridge project."""
        parser = DXFParser(str(ponte_dxf))

        # Extract structural elements
        entities = parser.extract_entities()
        assert 'LINE' in entities or len(entities) > 0

        # Check for pillars layer
        layers = parser.get_layer_info()
        layer_names = [l.name for l in layers]
        assert 'pilares' in layer_names

        # Export to GeoJSON for visualization
        output = tmp_path / "bridge.geojson"
        try:
            parser.export('geojson', str(output))
            assert Path(output).exists()
        except ImportError:
            pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
