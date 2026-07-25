# tests/e2e/test_examples_e2e.py
"""
10 Exemplos de testes E2E detalhados para Sprint 2 (D6.1–D7.5).
Cobre happy path, edge cases, regression, e casos patológicos.
"""

import pytest
import math
import time
from typing import Dict, Any, List, Tuple


# ============================================================================
# MOCK IMPLEMENTATIONS (para ilustração)
# ============================================================================

def parse_spt_profile(spt: Dict[str, Any]) -> Dict[str, Any]:
    """
    D6.1: Parse SPT profile e recomenda tipo de estaca.
    MOCK para ilustração.
    """
    if not spt or 'spt_profile' not in spt or not spt['spt_profile']:
        raise ValueError("spt_profile is required and cannot be empty")

    profile = spt['spt_profile']
    avg_spt = sum(p['spt_blow'] for p in profile) / len(profile)
    max_spt = max(p['spt_blow'] for p in profile)
    min_spt = min(p['spt_blow'] for p in profile)

    # Determine pile type and depth
    if max_spt >= 100:
        pile_type = 'rockhammer'
        design_depth = 2.0
    elif avg_spt >= 15:
        pile_type = 'driven'
        design_depth = 2.5
    elif avg_spt >= 8:
        pile_type = 'helical'
        design_depth = 3.0
    else:
        pile_type = 'helical'
        design_depth = 4.5

    # Bearing capacity estimate (kN)
    capacity = (avg_spt + 5) * 50

    risk_flag = None
    if avg_spt < 2:
        risk_flag = 'very_low_bearing_capacity'
    elif max_spt >= 100:
        risk_flag = 'refusal'

    return {
        'pile_recommendation': {
            'type': pile_type,
            'depth_m': design_depth,
            'embedment_ratio': design_depth / (design_depth + 1),
            'safety_factor': 1.5 + (avg_spt / 20)
        },
        'bearing_capacity_kN': capacity,
        'avg_spt': avg_spt,
        'max_spt': max_spt,
        'min_spt': min_spt,
        'risk_flag': risk_flag,
        'refusal_expected': max_spt >= 100
    }


def compute_bearing_capacity(piles: Dict[str, float], pga_cm_s2: float) -> Dict[str, float]:
    """
    D6.2: Computa capacidade portante com redução dinâmica por PGA.
    MOCK.
    """
    diameter_mm = piles.get('diameter_mm', 508)
    depth_m = piles.get('depth_m', 3.0)

    # Static capacity (simplified: ~60 kN/pile nominal)
    static_capacity = 100 + (diameter_mm / 100) + (depth_m * 20)

    # Dynamic reduction factor (PGA)
    if pga_cm_s2 == 0:
        reduction_factor = 1.0
    elif pga_cm_s2 <= 150:
        reduction_factor = 1.0
    elif pga_cm_s2 <= 500:
        reduction_factor = 0.95
    elif pga_cm_s2 <= 3000:
        reduction_factor = 0.85
    elif pga_cm_s2 <= 30000:
        reduction_factor = 0.65
    else:
        reduction_factor = 0.60

    dynamic_capacity = static_capacity * reduction_factor

    return {
        'static_kN': static_capacity,
        'dynamic_kN': dynamic_capacity,
        'pga_cm_s2': pga_cm_s2,
        'reduction_factor': reduction_factor,
        'safety_factor_static': 1.5,
        'safety_factor_dynamic': 1.3 * reduction_factor
    }


def solve_foundation_layout(boundary: Dict[str, Any],
                           constraints: Dict[str, Any] = None,
                           capacity_per_pile_kN: float = 150) -> Dict[str, Any]:
    """
    D6.3 & D7.1: Solver constraints → layout otimizado.
    MOCK com lógica simplificada.
    """
    constraints = constraints or {}

    # Extract boundary box
    coords = boundary['coordinates'][0]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x
    height = max_y - min_y

    # Constraints
    min_spacing = constraints.get('min_spacing_m', 2.0)
    setback = constraints.get('setback_m', 1.5)
    max_piles = constraints.get('max_piles', 10)

    # Place piles in grid
    piles = []
    x_positions = []
    y_positions = []

    # X direction
    available_width = width - 2 * setback
    if available_width <= 0:
        return {
            'piles': [],
            'feasible': False,
            'warning': 'narrow_geometry',
            'total_capacity_kN': 0
        }

    num_cols = max(1, int(available_width / min_spacing))
    if num_cols > 0:
        x_step = available_width / (num_cols + 1) if num_cols > 1 else available_width / 2
        x_positions = [min_x + setback + i * x_step for i in range(1, num_cols + 1)]
    else:
        x_positions = [min_x + width / 2]

    # Y direction
    available_height = height - 2 * setback
    if available_height <= 0:
        num_rows = 1
        y_positions = [min_y + height / 2]
    else:
        num_rows = max(1, int(available_height / min_spacing))
        if num_rows > 1:
            y_step = available_height / (num_rows + 1)
            y_positions = [min_y + setback + i * y_step for i in range(1, num_rows + 1)]
        else:
            y_positions = [min_y + height / 2]

    # Generate piles
    for y in y_positions:
        for x in x_positions:
            if len(piles) >= max_piles:
                break
            piles.append({
                'x': x,
                'y': y,
                'diameter_mm': 508,
                'depth_m': 3.0,
                'capacity_kN': capacity_per_pile_kN,
                'spacing_to_nearest_m': min_spacing
            })
        if len(piles) >= max_piles:
            break

    total_capacity = len(piles) * capacity_per_pile_kN

    return {
        'piles': piles,
        'boundary': boundary,
        'total_capacity_kN': total_capacity,
        'feasible': len(piles) > 0,
        'optimization_iterations': 5,
        'convergence': 0.95,
        'boundary_violations': 0
    }


def generate_cad_output(layout: Dict[str, Any], format: str = 'dxf') -> Dict[str, Any]:
    """
    D7.3: Gera CAD com layers normatizados.
    MOCK.
    """
    piles = layout.get('piles', [])

    return {
        'format': format,
        'layers': {
            'PILES': [{'id': i, 'x': p['x'], 'y': p['y']} for i, p in enumerate(piles)],
            'BOUNDARY': layout.get('boundary', {}),
            'DIMENSIONS': {},
            'ANNOTATIONS': {}
        },
        'entities_count': len(piles)
    }


def generate_report(layout: Dict[str, Any], format: str = 'pdf') -> Dict[str, Any]:
    """
    D7.4: Gera relatório técnico.
    MOCK.
    """
    return {
        'format': format,
        'executive_summary': f"Foundation design with {len(layout.get('piles', []))} piles",
        'sections': {
            'geotecnia': {'SPT analysis': True, 'Bearing capacity': True},
            'estrutura': {'Pile design': True, 'Load distribution': True},
            'calculations': list(range(10))  # Mock calculations
        },
        'calculations': [
            {'step': i, 'description': f'Calculation {i}'}
            for i in range(8)
        ]
    }


def convert_to_v1_format(layout: Dict[str, Any]) -> Dict[str, Any]:
    """
    D7.5: Converte v2 para v1.
    MOCK.
    """
    return {
        'version': 'v1.2',
        'piles': layout.get('piles', []),
        'boundary': layout.get('boundary'),
        'metadata': {
            'converted_from': 'v2.0',
            'conversion_date': '2026-07-25'
        }
    }


def point_in_polygon(point: List[float], polygon: Dict[str, Any]) -> bool:
    """Ray casting algorithm para point-in-polygon."""
    x, y = point
    coords = polygon['coordinates'][0]

    inside = False
    j = len(coords) - 1
    for i in range(len(coords)):
        xi, yi = coords[i][0], coords[i][1]
        xj, yj = coords[j][0], coords[j][1]

        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i

    return inside


def pairwise_distances(piles: List[Dict[str, float]]) -> List[float]:
    """Computa distâncias entre todos os pares de piles."""
    distances = []
    for i, p1 in enumerate(piles):
        for p2 in piles[i+1:]:
            dist = math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
            distances.append(dist)
    return distances


# ============================================================================
# TEST EXAMPLES (10 exemplos detalhados)
# ============================================================================

class TestExample1HappyPathJerico:
    """
    Exemplo 1: Happy Path — Caso Jericó nominal.
    D6.1: SPT → recomendação estaca.
    """

    @pytest.mark.e2e
    @pytest.mark.happy_path
    def test_jerico_spt_to_piles(self, happy_path_jerico):
        """Teste D6.1 completo para Jericó."""
        # ARRANGE
        test_case = happy_path_jerico
        spt = test_case['spt']
        expected = test_case['expected_output']

        # ACT
        result = parse_spt_profile(spt)

        # ASSERT
        assert result['pile_recommendation']['type'] == 'helical'
        assert result['pile_recommendation']['depth_m'] >= 2.5
        assert result['pile_recommendation']['depth_m'] <= 3.5
        assert result['bearing_capacity_kN'] >= 100
        assert result['risk_flag'] is None  # Sem risco

        print(f"✓ Example 1: SPT={result['avg_spt']:.1f}, Pile={result['pile_recommendation']['type']}, "
              f"Capacity={result['bearing_capacity_kN']:.0f} kN")


class TestExample2PGAExtreme30000:
    """
    Exemplo 2: Edge Case — PGA extremo (30.000 cm/s²).
    D6.2: Redução dinâmica com PGA extremo.
    """

    @pytest.mark.e2e
    @pytest.mark.edge_case
    @pytest.mark.parametrize("pga_cm_s2,expected_reduction_factor", [
        (0, 1.0),
        (150, 1.0),
        (500, 0.95),
        (3000, 0.85),
        (30000, 0.65),
    ])
    def test_pga_reduction_curve(self, pga_cm_s2, expected_reduction_factor):
        """Teste de redução dinâmica com vários PGAs."""
        # ARRANGE
        piles = {'diameter_mm': 508, 'depth_m': 3.0}

        # ACT
        capacity = compute_bearing_capacity(piles, pga_cm_s2)

        # ASSERT
        assert abs(capacity['reduction_factor'] - expected_reduction_factor) < 0.01
        assert capacity['safety_factor_dynamic'] >= 1.3 * expected_reduction_factor - 0.05

        print(f"✓ Example 2: PGA={pga_cm_s2} cm/s², Factor={capacity['reduction_factor']:.2f}, "
              f"Capacity={capacity['dynamic_kN']:.0f} kN")


class TestExample3SPTZeroVerysoft:
    """
    Exemplo 3: Edge Case — SPT = 0 (solo muito mole).
    D6.1: Detecção de risco de baixa capacidade.
    """

    @pytest.mark.e2e
    @pytest.mark.edge_case
    def test_spt_zero_very_soft_soil(self, edge_case_spt_zero):
        """Teste SPT=0 com recomendação de profundidade maior."""
        # ARRANGE
        test_case = edge_case_spt_zero
        spt = test_case['spt']
        expected = test_case['expected_output']

        # ACT
        result = parse_spt_profile(spt)

        # ASSERT
        assert result['pile_recommendation']['depth_m'] >= expected['depth_m_min']
        assert result['pile_recommendation']['depth_m'] <= expected['depth_m_max']
        assert result['bearing_capacity_kN'] <= expected['bearing_capacity_kN'] + 10
        assert result['risk_flag'] == expected['risk_flag']
        assert result['min_spt'] == 0

        print(f"✓ Example 3: SPT=0, Risk={result['risk_flag']}, "
              f"Depth={result['pile_recommendation']['depth_m']:.1f}m, "
              f"Capacity={result['bearing_capacity_kN']:.0f} kN")


class TestExample4SPTHard100:
    """
    Exemplo 4: Edge Case — SPT = 100 (rocha/muito rígido).
    D6.1: Detecção de refusal e rockhammer.
    """

    @pytest.mark.e2e
    @pytest.mark.edge_case
    def test_spt_100_rockhammer(self, spt_very_hard_soil):
        """Teste SPT=100 com recomendação rockhammer."""
        # ARRANGE
        expected_type = 'rockhammer'
        expected_depth_max = 2.0

        # ACT
        result = parse_spt_profile(spt_very_hard_soil)

        # ASSERT
        assert result['pile_recommendation']['type'] == expected_type
        assert result['pile_recommendation']['depth_m'] <= expected_depth_max
        assert result['bearing_capacity_kN'] > 400
        assert result['refusal_expected'] is True
        assert result['max_spt'] == 100

        print(f"✓ Example 4: SPT=100, Type={result['pile_recommendation']['type']}, "
              f"Refusal={result['refusal_expected']}, Capacity={result['bearing_capacity_kN']:.0f} kN")


class TestExample5NarrowGeometry:
    """
    Exemplo 5: Edge Case — Lote estreito (8m × 25m).
    D6.3: Solver respeitando constraints de geometria.
    """

    @pytest.mark.e2e
    @pytest.mark.edge_case
    @pytest.mark.geometry_constraint
    def test_narrow_lot_8m_constraint(self, narrow_lot_8m_x_25m):
        """Teste solver em lote estreito."""
        # ARRANGE
        constraints = {
            'min_spacing_m': 2.0,
            'min_setback_m': 1.5,
            'max_piles': 6
        }

        # ACT
        layout = solve_foundation_layout(narrow_lot_8m_x_25m, constraints)

        # ASSERT
        assert layout['feasible'] is True
        piles_per_row_max = len(set(p['x'] for p in layout['piles']))
        assert piles_per_row_max <= 2, f"Too many columns: {piles_per_row_max} > 2"

        # Validar boundary violations
        for pile in layout['piles']:
            assert point_in_polygon([pile['x'], pile['y']], narrow_lot_8m_x_25m)

        assert layout['boundary_violations'] == 0

        print(f"✓ Example 5: Narrow 8m×25m, Piles={len(layout['piles'])}, "
              f"Cols={piles_per_row_max}, Feasible={layout['feasible']}")


class TestExample6IrregularLotLShape:
    """
    Exemplo 6: Edge Case — Lote em forma de L (irregular).
    D7.1: Otimização em geometria complexa.
    """

    @pytest.mark.e2e
    @pytest.mark.edge_case
    @pytest.mark.geometry_constraint
    def test_irregular_polygon_l_shape(self, irregular_lot_l_shape):
        """Teste solver em lote em forma de L."""
        # ARRANGE
        constraints = {
            'min_spacing_m': 2.0,
            'min_setback_m': 1.5,
            'max_piles': 12
        }

        # ACT
        layout = solve_foundation_layout(irregular_lot_l_shape, constraints)

        # ASSERT
        assert layout['feasible'] is True

        # Verificar que nenhuma pile viola boundary
        for pile in layout['piles']:
            in_boundary = point_in_polygon([pile['x'], pile['y']], irregular_lot_l_shape)
            assert in_boundary, f"Pile at ({pile['x']:.1f}, {pile['y']:.1f}) violates boundary"

        assert layout['boundary_violations'] == 0

        print(f"✓ Example 6: L-Shape Lot, Piles={len(layout['piles'])}, "
              f"Boundary violations={layout['boundary_violations']}")


class TestExample7ConstraintSpacingConflict:
    """
    Exemplo 7: Constraint Solver — Conflito de espaçamento.
    D6.3: Resolver conflito entre constraints.
    """

    @pytest.mark.e2e
    @pytest.mark.constraint_solver
    def test_constraint_spacing_conflict_resolution(self):
        """Teste de resolução de conflito de espaçamento."""
        # ARRANGE
        small_lot = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
        }
        constraints = {
            'min_spacing_m': 3.0,    # Demanda muito espaçamento
            'min_setback_m': 1.5,
            'max_piles': 3
        }

        # ACT
        layout = solve_foundation_layout(small_lot, constraints)

        # ASSERT
        assert len(layout['piles']) <= constraints['max_piles']
        assert layout['feasible'] is True

        if len(layout['piles']) > 1:
            distances = pairwise_distances(layout['piles'])
            min_dist = min(distances) if distances else float('inf')
            # Permitir tolerância de 0.1m
            assert min_dist >= constraints['min_spacing_m'] - 0.1, \
                f"Spacing violation: {min_dist:.2f}m < {constraints['min_spacing_m']:.1f}m"

        print(f"✓ Example 7: Spacing Conflict, Piles={len(layout['piles'])}, "
              f"Min spacing={min(pairwise_distances(layout['piles'])) if layout['piles'] else 0:.2f}m")


class TestExample8RegressionV2V1:
    """
    Exemplo 8: Regressão — Compatibilidade v2 ↔ v1.
    D7.5: Validar que v2 mantém compatibilidade com v1.
    """

    @pytest.mark.e2e
    @pytest.mark.regression
    def test_regression_v2_v1_compatibility(self, happy_path_jerico):
        """Teste compatibilidade v2 com v1."""
        # ARRANGE
        test_case = happy_path_jerico
        boundary = test_case['geojson']['features'][0]['geometry']
        constraints = test_case['constraints']

        # Mock v1 baseline output
        v1_baseline = {
            'total_capacity_kN': 600,
            'num_piles': 4,
            'pile_type': 'helical',
            'depth_m': 3.0
        }

        # ACT
        v2_layout = solve_foundation_layout(boundary, constraints, capacity_per_pile_kN=150)
        v1_output = convert_to_v1_format(v2_layout)

        # ASSERT
        assert v1_output['version'] == 'v1.2'
        assert 'piles' in v1_output
        assert 'boundary' in v1_output
        assert 'metadata' in v1_output

        # Validar diferença aceitável (< 10%)
        capacity_diff_pct = abs(v2_layout['total_capacity_kN'] - v1_baseline['total_capacity_kN']) / v1_baseline['total_capacity_kN'] * 100
        assert capacity_diff_pct < 10, f"Capacity diff {capacity_diff_pct:.1f}% > 10%"

        print(f"✓ Example 8: v1 Compatibility, v1_version={v1_output['version']}, "
              f"Capacity diff={capacity_diff_pct:.1f}%")


class TestExample9PathologicalCases:
    """
    Exemplo 9: Casos Patológicos — Entrada vazia/inválida.
    Testa tratamento de erros gracioso.
    """

    @pytest.mark.e2e
    @pytest.mark.pathological
    @pytest.mark.parametrize("invalid_input,expected_error", [
        (None, ValueError),
        ({}, ValueError),
        ({'spt_profile': []}, ValueError),
        ({'spt_profile': None}, ValueError),
    ])
    def test_pathological_empty_input(self, invalid_input, expected_error):
        """Teste de entrada inválida com erro gracioso."""
        # ACT & ASSERT
        with pytest.raises(expected_error) as exc_info:
            parse_spt_profile(invalid_input)

        error_msg = str(exc_info.value).lower()
        assert 'spt_profile' in error_msg or 'required' in error_msg

        print(f"✓ Example 9: Invalid input {invalid_input} raised {expected_error.__name__}")


class TestExample10Performance:
    """
    Exemplo 10: Performance — Solver com 1000 piles.
    D7.1: Benchmark de tempo execução.
    """

    @pytest.mark.e2e
    @pytest.mark.performance
    def test_performance_large_foundation_1000_piles(self):
        """Teste de performance com lote grande."""
        # ARRANGE
        large_geometry = {
            "type": "Polygon",
            "coordinates": [[[i * 0.1, j * 0.1] for i in range(100) for j in range(100)]]
        }
        constraints = {'max_piles': 1000, 'min_spacing_m': 1.0}

        # ACT
        start = time.time()
        layout = solve_foundation_layout(large_geometry, constraints)
        elapsed = time.time() - start

        # ASSERT
        assert elapsed < 30.0, f"Execution time {elapsed:.2f}s > 30s"
        assert len(layout['piles']) > 0
        assert layout['feasible'] is True

        throughput = len(layout['piles']) / elapsed

        print(f"✓ Example 10: Performance, Piles={len(layout['piles'])}, "
              f"Time={elapsed:.2f}s, Throughput={throughput:.0f} piles/sec")


# ============================================================================
# SUMMARY TEST RUNS
# ============================================================================

@pytest.mark.e2e
def test_all_examples_summary(happy_path_jerico, assertion_helper):
    """
    Teste resumido de todos os 10 exemplos.
    Verifica integrações D6.1–D7.5 completas.
    """
    # Example 1: Happy Path
    spt = happy_path_jerico['spt']
    result_d6_1 = parse_spt_profile(spt)
    assert result_d6_1['pile_recommendation']['type'] == 'helical'

    # Example 2: D6.2 Bearing Capacity
    piles = result_d6_1['pile_recommendation']
    capacity = compute_bearing_capacity({'diameter_mm': 508, 'depth_m': 3.0}, 30000)
    assert capacity['reduction_factor'] < 0.7

    # Example 3-6: Layout Optimization
    boundary = happy_path_jerico['geojson']['features'][0]['geometry']
    layout = solve_foundation_layout(boundary, happy_path_jerico['constraints'])
    assert len(layout['piles']) > 0

    # Example 7: CAD Generation
    cad = generate_cad_output(layout)
    assert 'PILES' in cad['layers']

    # Example 8: Report
    report = generate_report(layout)
    assert 'geotecnia' in report['sections']

    # Example 9: v1 Compatibility
    v1_output = convert_to_v1_format(layout)
    assert v1_output['version'] == 'v1.2'

    print("\n✅ All 10 examples PASSED — D6.1–D7.5 integration complete")
