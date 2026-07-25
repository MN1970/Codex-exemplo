"""
Generate test reports and sample DXF files for autodesk-dxf-parser skill
Produces:
  1. Sample DXF files (rodovia, ponte, ferrovia)
  2. Test execution report
  3. Sample usage output
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import tempfile

try:
    import ezdxf
    from dxf_parser import DXFParser, batch_parse_dxf
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Install with: pip install ezdxf")
    sys.exit(1)


# ============================================================================
# SAMPLE DXF GENERATORS
# ============================================================================

def create_rodovia_sample():
    """Create sample roadway (rodovia) DXF file."""
    print("Creating rodovia_br116_km0_50.dxf...")
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Layers per DNIT standard
    for layer_name, color in [
        ('rodovia-eixo', 1),
        ('rodovia-acostamento', 2),
        ('marcacao', 5),
        ('drenagem', 3)
    ]:
        doc.layers.new(name=layer_name, dxfattribs={'color': color})

    # Centerline
    centerline_points = [
        (0, 0), (100, 50), (200, 100), (300, 150), (400, 200),
        (500, 250), (600, 300), (700, 350), (800, 400), (900, 450)
    ]
    msp.add_lwpolyline(centerline_points, dxfattribs={'layer': 'rodovia-eixo', 'color': 1})

    # Shoulders
    shoulder_points = [(x, y + 3.5) for x, y in centerline_points]
    msp.add_lwpolyline(shoulder_points, dxfattribs={'layer': 'rodovia-acostamento', 'color': 2})

    # Cross-section markers
    for i in range(0, 10):
        x = i * 100
        y = (i * 50) if i > 0 else 0
        msp.add_line((x - 10, y - 5), (x + 10, y + 5),
                    dxfattribs={'layer': 'marcacao', 'color': 5})
        msp.add_text(f'PK {i * 50}', dxfattribs={'layer': 'marcacao', 'insert': (x, y - 10)})

    # Drainage
    for i in range(2, 8):
        msp.add_circle((i * 120, 100), radius=2.0, dxfattribs={'layer': 'drenagem', 'color': 3})

    filepath = Path('./samples/rodovia_br116_km0_50.dxf')
    doc.saveas(str(filepath))
    return filepath


def create_ponte_sample():
    """Create sample bridge (ponte) DXF file."""
    print("Creating ponte_viaduto_01.dxf...")
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    for layer_name, color in [
        ('estrutura', 1),
        ('pilares', 2),
        ('tabuleiro', 5),
        ('barras-reforco', 3)
    ]:
        doc.layers.new(name=layer_name, dxfattribs={'color': color})

    # Deck
    deck = [(0, 0), (120, 0), (120, 12), (0, 12)]
    msp.add_lwpolyline(deck, dxfattribs={'layer': 'tabuleiro', 'color': 5})

    # Pillars
    for x in [30, 60, 90]:
        msp.add_line((x, 0), (x, -15), dxfattribs={'layer': 'pilares', 'color': 2})
        msp.add_circle((x, 0), radius=1.5, dxfattribs={'layer': 'pilares', 'color': 2})

    # Reinforcement
    for i in range(0, 10):
        msp.add_line((i * 12, 2), (i * 12, 10), dxfattribs={'layer': 'barras-reforco', 'color': 3})

    # Blocks with attributes
    block = doc.blocks.new(name='PILLAR_ATTR')
    block.add_text('PHC 1.5m', dxfattribs={'height': 2})

    for x in [30, 60, 90]:
        msp.add_blockref('PILLAR_ATTR', (x, -15))

    filepath = Path('./samples/ponte_viaduto_01.dxf')
    doc.saveas(str(filepath))
    return filepath


def create_ferrovia_sample():
    """Create sample railway (ferrovia) DXF file."""
    print("Creating ferrovia_linha4_alinhamento.dxf...")
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    for layer_name, color in [
        ('alignmento', 1),
        ('estaçoes', 2),
        ('curvas', 5),
        ('plataformas', 3)
    ]:
        doc.layers.new(name=layer_name, dxfattribs={'color': color})

    # Track alignment
    alignment_points = [
        (0, 0), (50, 10), (100, 30), (150, 60), (200, 100),
        (250, 140), (300, 170), (350, 180), (400, 175), (450, 160)
    ]
    msp.add_lwpolyline(alignment_points, dxfattribs={'layer': 'alignmento', 'color': 1})

    # Parallel track (gauge = 1.0m)
    offset_alignment = [(x, y - 1.0) for x, y in alignment_points]
    msp.add_lwpolyline(offset_alignment, dxfattribs={'layer': 'alignmento', 'color': 1})

    # Stations
    stations = [
        ('Estação Central', 100, 30),
        ('Estação Santa Cruz', 200, 100),
        ('Estação Oeste', 350, 180)
    ]
    for name, x, y in stations:
        platform_box = [(x - 5, y - 10), (x + 5, y - 10), (x + 5, y + 10), (x - 5, y + 10)]
        msp.add_lwpolyline(platform_box, dxfattribs={'layer': 'plataformas', 'color': 3})
        msp.add_text(name, dxfattribs={'layer': 'estaçoes', 'insert': (x - 3, y)})

    # Curve markers
    for x, y in alignment_points[1:-1]:
        msp.add_circle((x, y), radius=5, dxfattribs={'layer': 'curvas', 'color': 5})

    filepath = Path('./samples/ferrovia_linha4_alinhamento.dxf')
    doc.saveas(str(filepath))
    return filepath


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_tests():
    """Execute core functionality tests and generate report."""
    print("\n" + "="*80)
    print("AUTODESK-DXF-PARSER TEST EXECUTION REPORT")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Create sample directory
    Path('./samples').mkdir(exist_ok=True)

    # Generate sample files
    print("Step 1: Generating Sample DXF Files")
    print("-" * 80)
    rodovia_path = create_rodovia_sample()
    ponte_path = create_ponte_sample()
    ferrovia_path = create_ferrovia_sample()
    print(f"✓ Created 3 sample DXF files in ./samples/\n")

    # Initialize test results
    results = {
        'timestamp': datetime.now().isoformat(),
        'test_suites': [],
        'summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
    }

    # ========================================================================
    # TEST SUITE 1: Entity Extraction
    # ========================================================================
    print("Step 2: Testing Entity Extraction")
    print("-" * 80)

    test_results = []

    try:
        parser = DXFParser(str(rodovia_path))
        entities = parser.extract_entities()
        passed = len(entities) > 0
        test_results.append({
            'test': 'Extract All Entities',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Extracted {len(entities)} entity types"
        })
        print(f"✓ Extract All Entities: {len(entities)} types")
    except Exception as e:
        test_results.append({
            'test': 'Extract All Entities',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Extract All Entities: {e}")

    try:
        parser = DXFParser(str(rodovia_path))
        eixo = parser.extract_by_layer('rodovia-eixo')
        passed = len(eixo) > 0
        test_results.append({
            'test': 'Extract by Layer',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Extracted {len(eixo)} entities from 'rodovia-eixo'"
        })
        print(f"✓ Extract by Layer: {len(eixo)} entities on rodovia-eixo")
    except Exception as e:
        test_results.append({
            'test': 'Extract by Layer',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Extract by Layer: {e}")

    results['test_suites'].append({
        'name': 'Entity Extraction',
        'tests': test_results
    })
    results['summary']['total_tests'] += len(test_results)
    results['summary']['passed'] += sum(1 for t in test_results if t['status'] == 'PASS')
    results['summary']['failed'] += sum(1 for t in test_results if t['status'] == 'FAIL')
    print()

    # ========================================================================
    # TEST SUITE 2: Layer Analysis
    # ========================================================================
    print("Step 3: Testing Layer Analysis")
    print("-" * 80)

    test_results = []

    try:
        parser = DXFParser(str(ponte_path))
        layers = parser.get_layer_info()
        passed = len(layers) > 0
        test_results.append({
            'test': 'Get Layer Info',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Retrieved {len(layers)} layers"
        })
        print(f"✓ Get Layer Info: {len(layers)} layers")
        for layer in layers:
            print(f"  - {layer.name} (color={layer.color}, entities={layer.entity_count})")
    except Exception as e:
        test_results.append({
            'test': 'Get Layer Info',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Get Layer Info: {e}")

    try:
        parser = DXFParser(str(ponte_path))
        hierarchy = parser.get_layer_hierarchy()
        passed = len(hierarchy) > 0
        test_results.append({
            'test': 'Get Layer Hierarchy',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Found {len(hierarchy)} hierarchy groups"
        })
        print(f"✓ Get Layer Hierarchy: {len(hierarchy)} groups")
    except Exception as e:
        test_results.append({
            'test': 'Get Layer Hierarchy',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Get Layer Hierarchy: {e}")

    results['test_suites'].append({
        'name': 'Layer Analysis',
        'tests': test_results
    })
    results['summary']['total_tests'] += len(test_results)
    results['summary']['passed'] += sum(1 for t in test_results if t['status'] == 'PASS')
    results['summary']['failed'] += sum(1 for t in test_results if t['status'] == 'FAIL')
    print()

    # ========================================================================
    # TEST SUITE 3: Coordinate Extraction
    # ========================================================================
    print("Step 4: Testing Coordinate Extraction & Bounds")
    print("-" * 80)

    test_results = []

    try:
        parser = DXFParser(str(ferrovia_path))
        coords = parser.extract_coordinates()
        bbox = parser.get_bounds()
        passed = len(coords) > 0 and bbox.width > 0
        test_results.append({
            'test': 'Extract Coordinates & Bounds',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Extracted {len(coords)} coords, bbox={bbox.width:.1f}x{bbox.height:.1f}"
        })
        print(f"✓ Extract Coordinates: {len(coords)} points")
        print(f"✓ Bounds: X=[{bbox.minx:.1f}, {bbox.maxx:.1f}], Y=[{bbox.miny:.1f}, {bbox.maxy:.1f}]")
        print(f"  Width={bbox.width:.1f}, Height={bbox.height:.1f}")
    except Exception as e:
        test_results.append({
            'test': 'Extract Coordinates & Bounds',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Extract Coordinates & Bounds: {e}")

    try:
        parser = DXFParser(str(rodovia_path))
        validation = parser.validate_coordinates()
        passed = validation.valid
        test_results.append({
            'test': 'Validate Coordinates',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Valid={validation.valid}, Errors={len(validation.errors)}, Warnings={len(validation.warnings)}"
        })
        print(f"✓ Validate Coordinates: valid={validation.valid}")
    except Exception as e:
        test_results.append({
            'test': 'Validate Coordinates',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Validate Coordinates: {e}")

    results['test_suites'].append({
        'name': 'Coordinate Extraction',
        'tests': test_results
    })
    results['summary']['total_tests'] += len(test_results)
    results['summary']['passed'] += sum(1 for t in test_results if t['status'] == 'PASS')
    results['summary']['failed'] += sum(1 for t in test_results if t['status'] == 'FAIL')
    print()

    # ========================================================================
    # TEST SUITE 4: Anomaly Detection
    # ========================================================================
    print("Step 5: Testing Anomaly Detection")
    print("-" * 80)

    test_results = []

    try:
        parser = DXFParser(str(rodovia_path))
        anomalies = parser.detect_anomalies()
        summary = parser.get_anomaly_summary()
        test_results.append({
            'test': 'Detect Anomalies',
            'status': 'PASS',
            'details': f"Found {summary.total} anomalies (E:{summary.errors}, W:{summary.warnings}, I:{summary.info})"
        })
        print(f"✓ Detect Anomalies:")
        print(f"  Total: {summary.total}, Errors: {summary.errors}, Warnings: {summary.warnings}, Info: {summary.info}")
        for atype, alist in anomalies.items():
            if alist:
                print(f"  - {atype}: {len(alist)} items")
    except Exception as e:
        test_results.append({
            'test': 'Detect Anomalies',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Detect Anomalies: {e}")

    results['test_suites'].append({
        'name': 'Anomaly Detection',
        'tests': test_results
    })
    results['summary']['total_tests'] += len(test_results)
    results['summary']['passed'] += sum(1 for t in test_results if t['status'] == 'PASS')
    results['summary']['failed'] += sum(1 for t in test_results if t['status'] == 'FAIL')
    print()

    # ========================================================================
    # TEST SUITE 5: Export
    # ========================================================================
    print("Step 6: Testing Export Formats")
    print("-" * 80)

    test_results = []

    Path('./output').mkdir(exist_ok=True)

    try:
        parser = DXFParser(str(rodovia_path))
        result = parser.export('json', './output/rodovia_export.json', include_anomalies=True)
        passed = Path(result).exists()
        test_results.append({
            'test': 'Export JSON',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Exported to {result}"
        })
        print(f"✓ Export JSON: {result}")
    except Exception as e:
        test_results.append({
            'test': 'Export JSON',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Export JSON: {e}")

    try:
        parser = DXFParser(str(ponte_path))
        result = parser.export('csv', './output/ponte_export.csv')
        passed = Path(result).exists()
        test_results.append({
            'test': 'Export CSV',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Exported to {result}"
        })
        print(f"✓ Export CSV: {result}")
    except Exception as e:
        test_results.append({
            'test': 'Export CSV',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Export CSV: {e}")

    try:
        parser = DXFParser(str(ferrovia_path))
        result = parser.export('geojson', './output/ferrovia_export.geojson')
        passed = Path(result).exists()
        test_results.append({
            'test': 'Export GeoJSON',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Exported to {result}"
        })
        print(f"✓ Export GeoJSON: {result}")
    except Exception as e:
        test_results.append({
            'test': 'Export GeoJSON',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Export GeoJSON: {e}")

    results['test_suites'].append({
        'name': 'Export Formats',
        'tests': test_results
    })
    results['summary']['total_tests'] += len(test_results)
    results['summary']['passed'] += sum(1 for t in test_results if t['status'] == 'PASS')
    results['summary']['failed'] += sum(1 for t in test_results if t['status'] == 'FAIL')
    print()

    # ========================================================================
    # TEST SUITE 6: Batch Processing
    # ========================================================================
    print("Step 7: Testing Batch Processing")
    print("-" * 80)

    test_results = []

    try:
        dxf_files = [str(rodovia_path), str(ponte_path), str(ferrovia_path)]
        reports = batch_parse_dxf(
            dxf_files=dxf_files,
            export_format='json',
            include_anomalies=True,
            output_dir='./output/batch'
        )
        passed = len(reports) == 3
        test_results.append({
            'test': 'Batch Parse DXF',
            'status': 'PASS' if passed else 'FAIL',
            'details': f"Processed {len(reports)} files"
        })
        print(f"✓ Batch Parse: {len(reports)} files processed")
        for report in reports:
            print(f"  - {Path(report.filename).name}: {len(report.entity_counts)} entity types, "
                  f"{len(report.layer_summary)} layers")
    except Exception as e:
        test_results.append({
            'test': 'Batch Parse DXF',
            'status': 'FAIL',
            'details': str(e)
        })
        print(f"✗ Batch Parse: {e}")

    results['test_suites'].append({
        'name': 'Batch Processing',
        'tests': test_results
    })
    results['summary']['total_tests'] += len(test_results)
    results['summary']['passed'] += sum(1 for t in test_results if t['status'] == 'PASS')
    results['summary']['failed'] += sum(1 for t in test_results if t['status'] == 'FAIL')
    print()

    # ========================================================================
    # PRINT SUMMARY
    # ========================================================================
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Success Rate: {100 * results['summary']['passed'] // max(1, results['summary']['total_tests'])}%")
    print()

    # Save detailed report
    report_path = Path('./TEST_REPORT.json')
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Detailed report saved: {report_path}\n")

    return results


if __name__ == '__main__':
    try:
        run_tests()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
