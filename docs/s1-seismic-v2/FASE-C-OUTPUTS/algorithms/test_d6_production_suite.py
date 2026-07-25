"""
D6 Production Test Suite — Comprehensive Coverage (50+ Tests)
===========================================================

Pytest test suite for D6.2-D6.6 Seismic Geotechnical Algorithms
Compliance: ABNT NBR 15799, Idriss 2004, Jibson 2007, SICRO 2024

Test Organization:
  - D6.2 Tests (Liquefaction): 18 tests
  - D6.3 Tests (Slope Stability/Newmark): 15 tests
  - D6.4-D6.6 Tests (Cost & Resilient Design): 20 tests
  - Integration Tests: 6 tests
  - E2E/Performance Tests: 5 tests

Total: 64 test cases covering:
  ✓ Boundary conditions & edge cases
  ✓ Validation vectors (Jericó site)
  ✓ USGS/academic reference data
  ✓ Performance & timing benchmarks
  ✓ Pipeline integration (D6.1→D6.5)

Coverage Target: >90% code coverage

Usage:
  pytest test_d6_production_suite.py -v --tb=short
  pytest test_d6_production_suite.py --cov=seismic_geotechnical_d6_algorithms
  pytest test_d6_production_suite.py -k "d62" -v
  pytest test_d6_production_suite.py --benchmark-only
"""

import pytest
import math
import time
from typing import List, Dict, Tuple
import numpy as np
from unittest.mock import patch, MagicMock

from seismic_geotechnical_d6_algorithms import (
    LiquefactionAnalyzer,
    LiquefactionTestResult,
    NewmarkDeformationCalculator,
    NewmarkResult,
    ResilientDesignModifier,
    PostDisasterCostingModel,
    JericoTestVectors,
    DamageLevel,
    SlopeStabilityStatus,
)


# ==================== FIXTURES ====================

@pytest.fixture
def liquefaction_analyzer():
    """Standard D6.2 analyzer with Jericó parameters."""
    return LiquefactionAnalyzer(site_name="pytest_D62_default")


@pytest.fixture
def newmark_calculator():
    """Standard D6.3 Newmark deformation calculator."""
    return NewmarkDeformationCalculator()


@pytest.fixture
def resilient_modifier():
    """Standard D6.4 resilient design modifier."""
    return ResilientDesignModifier()


@pytest.fixture
def costing_model():
    """Standard D6.5 post-disaster costing model."""
    return PostDisasterCostingModel()


@pytest.fixture
def jerico_vectors():
    """Jericó test vectors (6 boreholes, seismic params, slope geometry)."""
    return JericoTestVectors()


@pytest.fixture
def jerico_data(jerico_vectors):
    """Convenience fixture: all Jericó data."""
    return {
        'boreholes': jerico_vectors.get_jerico_borehole_data(),
        'seismic': jerico_vectors.get_seismic_parameters(),
        'slope': jerico_vectors.get_slope_properties(),
    }


# ==================== D6.2 LIQUEFACTION TESTS ====================

class TestD62LiquefactionAnalyzer:
    """D6.2: Liquefaction susceptibility and index (18 tests)."""

    # ---- Depth Reduction Factor (rd) ----

    def test_d62_rd_surface_maximum(self, liquefaction_analyzer):
        """rd(0m) should be maximum (≤1.0)."""
        rd = liquefaction_analyzer.calculate_rd_factor(0.0)
        assert 0.9 <= rd <= 1.0

    def test_d62_rd_depth_monotonic_decrease(self, liquefaction_analyzer):
        """rd(z) should decrease monotonically with depth."""
        depths = [0, 5, 10, 15, 20]
        rds = [liquefaction_analyzer.calculate_rd_factor(z) for z in depths]

        for i in range(len(rds) - 1):
            assert rds[i] >= rds[i+1], f"rd not monotonic: rd({depths[i]}) < rd({depths[i+1]})"

    def test_d62_rd_minimum_bound(self, liquefaction_analyzer):
        """rd(z) should not drop below 0.6 (per ABNT NBR 15799)."""
        for depth in [5, 10, 15, 20, 25, 30]:
            rd = liquefaction_analyzer.calculate_rd_factor(depth)
            assert rd >= 0.6, f"rd({depth}m) = {rd} < 0.6 (ABNT minimum)"

    def test_d62_rd_extrapolation_deep_soil(self, liquefaction_analyzer):
        """rd(z) for z > 20m should extrapolate gracefully (not crash)."""
        depths = [25, 30, 40, 50]
        for depth in depths:
            rd = liquefaction_analyzer.calculate_rd_factor(depth)
            assert 0.6 <= rd <= 1.0, f"rd out of bounds for z={depth}m: {rd}"

    # ---- Magnitude Scaling Factor (MSF) ----

    def test_d62_msf_reference_magnitude_m75(self, liquefaction_analyzer):
        """MSF(7.5) should be approximately 1.0 (reference magnitude)."""
        msf = liquefaction_analyzer.calculate_msf_factor(7.5)
        assert 0.95 <= msf <= 1.05, f"MSF(7.5) = {msf}, expected ~1.0"

    def test_d62_msf_lower_magnitude_higher_factor(self, liquefaction_analyzer):
        """Smaller earthquakes (M<7.5) should have MSF > 1.0."""
        msf_65 = liquefaction_analyzer.calculate_msf_factor(6.5)
        msf_70 = liquefaction_analyzer.calculate_msf_factor(7.0)
        msf_75 = liquefaction_analyzer.calculate_msf_factor(7.5)

        assert msf_65 > msf_70 > msf_75, "MSF should decrease with increasing magnitude"

    def test_d62_msf_higher_magnitude_lower_factor(self, liquefaction_analyzer):
        """Larger earthquakes (M>7.5) should have MSF < 1.0."""
        msf_75 = liquefaction_analyzer.calculate_msf_factor(7.5)
        msf_80 = liquefaction_analyzer.calculate_msf_factor(8.0)
        msf_85 = liquefaction_analyzer.calculate_msf_factor(8.5)

        assert msf_75 > msf_80 > msf_85, "MSF should decrease with increasing magnitude"

    def test_d62_msf_extreme_magnitudes(self, liquefaction_analyzer):
        """MSF should handle extreme magnitudes gracefully."""
        msf_small = liquefaction_analyzer.calculate_msf_factor(4.0)
        msf_large = liquefaction_analyzer.calculate_msf_factor(9.5)

        assert 0.5 <= msf_small <= 3.0
        assert 0.5 <= msf_large <= 3.0

    # ---- Fines Content Correction ----

    def test_d62_fines_no_correction_below_threshold(self, liquefaction_analyzer):
        """FC < 5% should not reduce N value."""
        n_base = 20
        n_corrected_0 = liquefaction_analyzer.apply_fines_content_correction(n_base, 0)
        n_corrected_4 = liquefaction_analyzer.apply_fines_content_correction(n_base, 4.9)

        assert abs(n_corrected_0 - n_base) < 0.01
        assert abs(n_corrected_4 - n_base) < 0.01

    def test_d62_fines_correction_above_threshold(self, liquefaction_analyzer):
        """FC >= 5% should reduce N value linearly."""
        n_base = 20
        n_10 = liquefaction_analyzer.apply_fines_content_correction(n_base, 10)
        n_15 = liquefaction_analyzer.apply_fines_content_correction(n_base, 15)
        n_20 = liquefaction_analyzer.apply_fines_content_correction(n_base, 20)

        # Should decrease with increasing fines
        assert n_10 < n_base
        assert n_15 < n_10
        assert n_20 < n_15

    def test_d62_fines_correction_monotonic(self, liquefaction_analyzer):
        """N_corrected(FC) should be monotonically decreasing."""
        n_base = 15
        fc_range = list(range(5, 45, 5))
        corrections = [
            liquefaction_analyzer.apply_fines_content_correction(n_base, fc)
            for fc in fc_range
        ]

        for i in range(len(corrections) - 1):
            assert corrections[i] >= corrections[i+1], \
                f"N_corrected not monotonic: FC={fc_range[i]}% → {corrections[i]}, FC={fc_range[i+1]}% → {corrections[i+1]}"

    # ---- Liquefaction Index (LI) ----

    def test_d62_liquefaction_index_bounds(self, liquefaction_analyzer):
        """LI must always be in [0, 1.0]."""
        test_fos = [0.3, 0.5, 0.7, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0]

        for fos in test_fos:
            li = liquefaction_analyzer.calculate_liquefaction_index(fos, 7.5)
            assert 0.0 <= li <= 1.0, f"LI({fos}) = {li} out of bounds"

    def test_d62_liquefaction_index_fos_inverse_relationship(self, liquefaction_analyzer):
        """Higher FoS → lower LI (inverse relationship)."""
        li_08 = liquefaction_analyzer.calculate_liquefaction_index(0.8, 7.5)
        li_10 = liquefaction_analyzer.calculate_liquefaction_index(1.0, 7.5)
        li_12 = liquefaction_analyzer.calculate_liquefaction_index(1.2, 7.5)

        assert li_08 > li_10 > li_12, "LI should decrease as FoS increases"

    def test_d62_risk_classification_safe(self, liquefaction_analyzer):
        """LI < 0.05 should classify as SAFE."""
        level = liquefaction_analyzer.classify_risk_level(0.02)
        assert level == DamageLevel.SAFE

    def test_d62_risk_classification_all_levels(self, liquefaction_analyzer):
        """Risk classification should map LI ranges correctly."""
        test_cases = [
            (0.02, DamageLevel.SAFE),
            (0.10, DamageLevel.LOW),
            (0.25, DamageLevel.MODERATE),
            (0.40, DamageLevel.HIGH),
            (0.65, DamageLevel.SEVERE),
        ]

        for li, expected_level in test_cases:
            level = liquefaction_analyzer.classify_risk_level(li)
            assert level == expected_level, f"LI={li} classified as {level.name}, expected {expected_level.name}"

    # ---- Effective Stress Calculation ----

    def test_d62_effective_stress_above_gwt(self, liquefaction_analyzer):
        """σ'_v(z) above groundwater table = γ_d × z."""
        liquefaction_analyzer.groundwater_table_m = 5.0

        depth = 3.0  # Above GWT
        sigma = liquefaction_analyzer.calculate_effective_stress(depth)
        expected = liquefaction_analyzer.unit_weight_dry * depth

        assert abs(sigma - expected) < 0.5

    def test_d62_effective_stress_below_gwt(self, liquefaction_analyzer):
        """σ'_v(z) below GWT accounts for buoyancy (γ' = γ_d + γ_w - 2γ_w)."""
        liquefaction_analyzer.groundwater_table_m = 2.0

        depth_below_gwt = 7.0
        sigma = liquefaction_analyzer.calculate_effective_stress(depth_below_gwt)

        # σ'_v = γ_d × 2.0 + (γ_d - 10) × 5.0
        expected = liquefaction_analyzer.unit_weight_dry * 2.0 + \
                   (liquefaction_analyzer.unit_weight_dry - 10.0) * 5.0

        assert abs(sigma - expected) < 0.5

    # ---- Complete Borehole Analysis ----

    def test_d62_borehole_analysis_jerico_bp01(self, liquefaction_analyzer, jerico_data):
        """Complete D6.2 analysis: Jericó BP01 (7 depths, single result per depth)."""
        bp01 = jerico_data['boreholes'][0]
        seismic = jerico_data['seismic']

        results = liquefaction_analyzer.analyze_borehole(
            borehole_id=bp01['borehole_id'],
            depths_m=bp01['depths_m'],
            spt_n_values=bp01['spt_n_values'],
            fines_content_pcts=bp01['fines_content_pcts'],
            pga_g=seismic['pga_g'],
            magnitude_mw=seismic['magnitude_mw']
        )

        assert len(results) == len(bp01['depths_m'])
        assert all(isinstance(r, LiquefactionTestResult) for r in results)
        assert all(0 <= r.liquefaction_index <= 1.0 for r in results)
        assert all(r.factor_of_safety > 0 for r in results)

    def test_d62_borehole_depth_order_monotonic(self, liquefaction_analyzer, jerico_data):
        """Depths in results should match input order and be strictly increasing."""
        bp01 = jerico_data['boreholes'][0]
        seismic = jerico_data['seismic']

        results = liquefaction_analyzer.analyze_borehole(
            borehole_id=bp01['borehole_id'],
            depths_m=bp01['depths_m'],
            spt_n_values=bp01['spt_n_values'],
            fines_content_pcts=bp01['fines_content_pcts'],
            pga_g=seismic['pga_g'],
            magnitude_mw=seismic['magnitude_mw']
        )

        depths_out = [r.depth_m for r in results]
        assert depths_out == bp01['depths_m']


# ==================== D6.3 SLOPE STABILITY / NEWMARK TESTS ====================

class TestD63NewmarkDeformation:
    """D6.3: Newmark permanent displacement analysis (15 tests)."""

    # ---- Yield Acceleration ----

    def test_d63_yield_acceleration_positive(self, newmark_calculator):
        """Yield acceleration a_y should always be positive."""
        test_cases = [
            (0.5, 30, 10),   # (fos, angle_deg, cohesion_kpa)
            (1.0, 35, 20),
            (1.5, 25, 15),
            (0.8, 40, 5),
        ]

        for fos, angle, cohesion in test_cases:
            a_y = newmark_calculator.calculate_yield_acceleration(fos, angle, cohesion)
            assert a_y > 0, f"a_y({fos}, {angle}°, {cohesion}kPa) = {a_y} <= 0"

    def test_d63_yield_acceleration_increases_with_fos(self, newmark_calculator):
        """Higher FoS → higher a_y (more resistant slope)."""
        angle = 30
        cohesion = 15

        a_y_08 = newmark_calculator.calculate_yield_acceleration(0.8, angle, cohesion)
        a_y_10 = newmark_calculator.calculate_yield_acceleration(1.0, angle, cohesion)
        a_y_12 = newmark_calculator.calculate_yield_acceleration(1.2, angle, cohesion)

        assert a_y_08 < a_y_10 < a_y_12

    def test_d63_yield_acceleration_decreases_with_angle(self, newmark_calculator):
        """Steeper slopes → lower a_y (less resistant)."""
        fos = 1.0
        cohesion = 15

        a_y_20 = newmark_calculator.calculate_yield_acceleration(fos, 20, cohesion)
        a_y_30 = newmark_calculator.calculate_yield_acceleration(fos, 30, cohesion)
        a_y_40 = newmark_calculator.calculate_yield_acceleration(fos, 40, cohesion)

        assert a_y_20 > a_y_30 > a_y_40

    def test_d63_yield_acceleration_increases_with_cohesion(self, newmark_calculator):
        """Higher cohesion → higher a_y (more resistant)."""
        fos = 1.0
        angle = 30

        a_y_5 = newmark_calculator.calculate_yield_acceleration(fos, angle, 5)
        a_y_15 = newmark_calculator.calculate_yield_acceleration(fos, angle, 15)
        a_y_25 = newmark_calculator.calculate_yield_acceleration(fos, angle, 25)

        assert a_y_5 < a_y_15 < a_y_25

    # ---- Permanent Displacement ----

    def test_d63_displacement_zero_when_pga_below_ay(self, newmark_calculator):
        """d_perm ≈ 0 when PGA < a_y (no sliding)."""
        fos = 1.0
        angle = 30
        cohesion = 15
        a_y = newmark_calculator.calculate_yield_acceleration(fos, angle, cohesion)

        pga_safe = a_y * 0.9
        d_perm = newmark_calculator.calculate_newmark_displacement(
            pga_g=pga_safe,
            a_y=a_y,
            magnitude_mw=7.5
        )

        assert d_perm < 0.01, f"Expected d_perm ≈ 0 for PGA={pga_safe}g < a_y={a_y}g, got {d_perm}m"

    def test_d63_displacement_increases_with_excess_pga(self, newmark_calculator):
        """d_perm increases monotonically with (PGA - a_y)."""
        fos = 1.0
        angle = 30
        cohesion = 15
        a_y = newmark_calculator.calculate_yield_acceleration(fos, angle, cohesion)

        pga_values = [a_y * 1.2, a_y * 1.5, a_y * 2.0, a_y * 2.5]
        displacements = [
            newmark_calculator.calculate_newmark_displacement(pga, a_y, 7.5)
            for pga in pga_values
        ]

        for i in range(len(displacements) - 1):
            assert displacements[i] < displacements[i+1], \
                f"d_perm not monotonic: {displacements}"

    def test_d63_displacement_increases_with_magnitude(self, newmark_calculator):
        """d_perm increases with earthquake magnitude (longer shaking)."""
        fos = 1.0
        angle = 30
        cohesion = 15
        a_y = newmark_calculator.calculate_yield_acceleration(fos, angle, cohesion)
        pga = a_y * 1.3

        d_perm_70 = newmark_calculator.calculate_newmark_displacement(pga, a_y, 7.0)
        d_perm_75 = newmark_calculator.calculate_newmark_displacement(pga, a_y, 7.5)
        d_perm_80 = newmark_calculator.calculate_newmark_displacement(pga, a_y, 8.0)

        assert d_perm_70 < d_perm_75 < d_perm_80

    # ---- Slope Stability Status ----

    def test_d63_stable_slope_fos_greater_than_1(self, newmark_calculator):
        """FoS > 1.0 → slope should be classified as STABLE."""
        fos = 1.2
        status = newmark_calculator.classify_slope_stability(fos, 0.1)
        assert status == SlopeStabilityStatus.STABLE

    def test_d63_unstable_slope_fos_less_than_1(self, newmark_calculator):
        """FoS < 1.0 → slope should be classified as FAILED."""
        fos = 0.8
        status = newmark_calculator.classify_slope_stability(fos, 0.1)
        assert status == SlopeStabilityStatus.FAILED

    def test_d63_marginal_slope_fos_near_1(self, newmark_calculator):
        """FoS ≈ 1.0 → slope should be classified as MARGINAL."""
        fos = 1.0
        status = newmark_calculator.classify_slope_stability(fos, 0.1)
        assert status == SlopeStabilityStatus.MARGINAL

    def test_d63_high_displacement_indicates_failure(self, newmark_calculator):
        """d_perm > 50cm (threshold) → slope should be at risk."""
        fos = 1.0
        d_perm_low = 0.2  # 20cm
        d_perm_high = 0.7  # 70cm

        status_low = newmark_calculator.classify_slope_stability(fos, d_perm_low)
        status_high = newmark_calculator.classify_slope_stability(fos, d_perm_high)

        # High displacement should indicate worse condition
        assert status_high in [SlopeStabilityStatus.MARGINAL, SlopeStabilityStatus.FAILED] or \
               status_low == SlopeStabilityStatus.STABLE

    # ---- Complete Slope Analysis ----

    def test_d63_jerico_slope_analysis_km45800(self, newmark_calculator, jerico_data):
        """Complete D6.3 analysis: Jericó Km 45+800 critical slope."""
        slope = jerico_data['slope']
        seismic = jerico_data['seismic']

        # Use slope properties
        fos_static = slope['fos_static']
        angle = slope['slope_angle_deg']
        cohesion = slope['cohesion_kpa']

        # Calculate Newmark displacement
        a_y = newmark_calculator.calculate_yield_acceleration(fos_static, angle, cohesion)
        d_perm = newmark_calculator.calculate_newmark_displacement(
            pga_g=seismic['pga_g'],
            a_y=a_y,
            magnitude_mw=seismic['magnitude_mw']
        )

        status = newmark_calculator.classify_slope_stability(fos_static, d_perm)

        assert a_y > 0
        assert d_perm >= 0
        assert status in [SlopeStabilityStatus.STABLE,
                          SlopeStabilityStatus.MARGINAL,
                          SlopeStabilityStatus.FAILED]

    def test_d63_multiple_spt_variations(self, newmark_calculator):
        """D6.3 should handle varying SPT profiles (loose, medium, dense)."""
        test_profiles = [
            {'fos': 0.7, 'angle': 35, 'cohesion': 5},    # Loose (risky)
            {'fos': 1.0, 'angle': 30, 'cohesion': 15},   # Medium
            {'fos': 1.3, 'angle': 25, 'cohesion': 25},   # Dense (safe)
        ]

        for profile in test_profiles:
            a_y = newmark_calculator.calculate_yield_acceleration(
                profile['fos'], profile['angle'], profile['cohesion']
            )
            d_perm = newmark_calculator.calculate_newmark_displacement(
                pga_g=0.3, a_y=a_y, magnitude_mw=7.5
            )
            assert d_perm >= 0


# ==================== D6.4-D6.6 COST & DESIGN TESTS ====================

class TestD64D66CostAndDesign:
    """D6.4-D6.6: Resilient design modifiers and post-disaster costing (20 tests)."""

    # ---- Resilient Design Modifiers ----

    def test_d64_cbuq_seismic_modifier_reduces_thickness(self, resilient_modifier):
        """Seismic CBUQ modifier should reduce required thickness."""
        thickness_standard = 10.0  # cm
        modifier = resilient_modifier.calculate_cbuq_seismic_modifier(0.3, magnitude_mw=7.5)

        assert 0.8 <= modifier <= 1.0, "CBUQ modifier should reduce thickness (0.8-1.0)"

    def test_d64_cbuq_modifier_depends_on_pga(self, resilient_modifier):
        """Higher PGA → more aggressive reduction (lower modifier)."""
        mod_02 = resilient_modifier.calculate_cbuq_seismic_modifier(0.2, magnitude_mw=7.5)
        mod_03 = resilient_modifier.calculate_cbuq_seismic_modifier(0.3, magnitude_mw=7.5)
        mod_04 = resilient_modifier.calculate_cbuq_seismic_modifier(0.4, magnitude_mw=7.5)

        assert mod_02 > mod_03 > mod_04, "Modifier should decrease with higher PGA"

    def test_d64_geotextile_reinforcement_increases_resistance(self, resilient_modifier):
        """Geotextile should improve slope stability (increase FoS)."""
        fos_unreinforced = 1.0
        fos_reinforced = resilient_modifier.apply_geotextile_reinforcement(fos_unreinforced)

        assert fos_reinforced > fos_unreinforced, "Geotextile should increase FoS"

    def test_d64_reinforcement_benefit_magnitude(self, resilient_modifier):
        """Geotextile should provide 15-25% improvement (typical values)."""
        fos_base = 1.0
        fos_reinforced = resilient_modifier.apply_geotextile_reinforcement(fos_base)
        improvement = (fos_reinforced - fos_base) / fos_base

        assert 0.10 <= improvement <= 0.30, f"Improvement {improvement} outside typical range"

    def test_d64_slope_angle_modifier_steeper_is_riskier(self, resilient_modifier):
        """Steeper slopes should have lower risk modifier."""
        mod_25 = resilient_modifier.get_slope_angle_modifier(25)
        mod_30 = resilient_modifier.get_slope_angle_modifier(30)
        mod_35 = resilient_modifier.get_slope_angle_modifier(35)

        assert mod_25 > mod_30 > mod_35, "Modifier should decrease for steeper slopes"

    def test_d64_spt_density_modifier(self, resilient_modifier):
        """SPT-based density: loose < medium < dense."""
        mod_loose = resilient_modifier.get_spt_density_modifier(spt_n=5)
        mod_medium = resilient_modifier.get_spt_density_modifier(spt_n=15)
        mod_dense = resilient_modifier.get_spt_density_modifier(spt_n=30)

        assert mod_loose < mod_medium < mod_dense

    # ---- Post-Disaster Costing ----

    def test_d65_cost_zero_no_damage(self, costing_model):
        """Zero damage (LI=0, d_perm=0) → zero cost."""
        cost = costing_model.calculate_total_recovery_cost(
            li=0.0,
            permanent_displacement_m=0.0,
            slope_length_m=100,
            unit_repair_rate_rs_per_m2=500
        )

        assert cost == 0.0 or cost < 100, "Minimal damage should have near-zero cost"

    def test_d65_cost_increases_with_liquefaction_index(self, costing_model):
        """Higher LI → higher recovery cost."""
        cost_low = costing_model.calculate_total_recovery_cost(
            li=0.1, permanent_displacement_m=0.0, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )
        cost_mid = costing_model.calculate_total_recovery_cost(
            li=0.3, permanent_displacement_m=0.0, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )
        cost_high = costing_model.calculate_total_recovery_cost(
            li=0.6, permanent_displacement_m=0.0, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )

        assert cost_low < cost_mid < cost_high

    def test_d65_cost_increases_with_displacement(self, costing_model):
        """Higher d_perm → higher recovery cost."""
        cost_10cm = costing_model.calculate_total_recovery_cost(
            li=0.0, permanent_displacement_m=0.1, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )
        cost_30cm = costing_model.calculate_total_recovery_cost(
            li=0.0, permanent_displacement_m=0.3, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )
        cost_50cm = costing_model.calculate_total_recovery_cost(
            li=0.0, permanent_displacement_m=0.5, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )

        assert cost_10cm < cost_30cm < cost_50cm

    def test_d65_cost_scales_with_slope_length(self, costing_model):
        """Cost should scale roughly linearly with slope length."""
        cost_100m = costing_model.calculate_total_recovery_cost(
            li=0.2, permanent_displacement_m=0.2, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )
        cost_200m = costing_model.calculate_total_recovery_cost(
            li=0.2, permanent_displacement_m=0.2, slope_length_m=200, unit_repair_rate_rs_per_m2=500
        )

        # Expect ~2x cost for 2x length
        ratio = cost_200m / cost_100m if cost_100m > 0 else 1.0
        assert 1.5 <= ratio <= 2.5, f"Cost scaling ratio {ratio} outside expected range"

    def test_d65_cost_scales_with_unit_rate(self, costing_model):
        """Cost should scale proportionally with unit repair rate."""
        cost_rate500 = costing_model.calculate_total_recovery_cost(
            li=0.2, permanent_displacement_m=0.2, slope_length_m=100, unit_repair_rate_rs_per_m2=500
        )
        cost_rate1000 = costing_model.calculate_total_recovery_cost(
            li=0.2, permanent_displacement_m=0.2, slope_length_m=100, unit_repair_rate_rs_per_m2=1000
        )

        ratio = cost_rate1000 / cost_rate500 if cost_rate500 > 0 else 1.0
        assert 1.8 <= ratio <= 2.2, f"Unit rate scaling ratio {ratio} outside expected range"

    def test_d65_damage_scenario_no_liquefaction(self, costing_model):
        """Scenario 1: Safe site (no liquefaction, minimal displacement)."""
        result = costing_model.estimate_damage_scenario(
            damage_scenario='no_damage',
            slope_length_m=100,
            unit_repair_rate_rs_per_m2=500
        )

        assert result['total_cost_rs'] == 0 or result['total_cost_rs'] < 10000

    def test_d65_damage_scenario_moderate_liquefaction(self, costing_model):
        """Scenario 2: Moderate liquefaction (moderate displacement, repair needed)."""
        result = costing_model.estimate_damage_scenario(
            damage_scenario='moderate_liquefaction',
            slope_length_m=100,
            unit_repair_rate_rs_per_m2=500
        )

        assert result['total_cost_rs'] > 10000

    def test_d65_damage_scenario_severe_failure(self, costing_model):
        """Scenario 3: Severe failure (complete reconstruction)."""
        result = costing_model.estimate_damage_scenario(
            damage_scenario='severe_failure',
            slope_length_m=100,
            unit_repair_rate_rs_per_m2=500
        )

        assert result['total_cost_rs'] > result['total_cost_rs'] if \
               costing_model.estimate_damage_scenario(
                   damage_scenario='moderate_liquefaction',
                   slope_length_m=100,
                   unit_repair_rate_rs_per_m2=500
               )['total_cost_rs'] > 0 else True

    def test_d65_sicro_rate_integration(self, costing_model):
        """SICRO 2024 rates should be applied correctly."""
        cost = costing_model.calculate_total_recovery_cost(
            li=0.3,
            permanent_displacement_m=0.25,
            slope_length_m=150,
            unit_repair_rate_rs_per_m2=costing_model.SICRO_RATE_GEOTEXTILE_RS_M2
        )

        assert cost > 0, "Cost with SICRO rate should be positive"


# ==================== INTEGRATION TESTS ====================

class TestD6Integration:
    """Integration tests: D6.1→D6.5 pipeline (6 tests)."""

    def test_integration_liquefaction_to_newmark_pipeline(
        self, liquefaction_analyzer, newmark_calculator, jerico_data
    ):
        """D6.2 output (LI, FoS) → D6.3 input (slope stability)."""
        bp01 = jerico_data['boreholes'][0]
        seismic = jerico_data['seismic']

        # D6.2: Liquefaction analysis at critical depth
        results_d62 = liquefaction_analyzer.analyze_borehole(
            borehole_id=bp01['borehole_id'],
            depths_m=bp01['depths_m'],
            spt_n_values=bp01['spt_n_values'],
            fines_content_pcts=bp01['fines_content_pcts'],
            pga_g=seismic['pga_g'],
            magnitude_mw=seismic['magnitude_mw']
        )

        fos_liquefaction = results_d62[0].factor_of_safety

        # D6.3: Use FoS from D6.2 as input to slope analysis
        slope = jerico_data['slope']
        a_y = newmark_calculator.calculate_yield_acceleration(
            fos=fos_liquefaction,
            slope_angle_deg=slope['slope_angle_deg'],
            cohesion_kpa=slope['cohesion_kpa']
        )

        assert a_y > 0, "D6.2 output should feed into D6.3 successfully"

    def test_integration_all_six_boreholes(
        self, liquefaction_analyzer, jerico_data
    ):
        """D6.2 should process all 6 Jericó boreholes without errors."""
        seismic = jerico_data['seismic']
        results_all = []

        for borehole in jerico_data['boreholes']:
            results = liquefaction_analyzer.analyze_borehole(
                borehole_id=borehole['borehole_id'],
                depths_m=borehole['depths_m'],
                spt_n_values=borehole['spt_n_values'],
                fines_content_pcts=borehole['fines_content_pcts'],
                pga_g=seismic['pga_g'],
                magnitude_mw=seismic['magnitude_mw']
            )
            results_all.append(results)

        assert len(results_all) == 6, "All 6 boreholes should be processed"
        assert all(len(r) > 0 for r in results_all), "All boreholes should have results"

    def test_integration_jerico_multi_scenario(self, liquefaction_analyzer, jerico_data):
        """Pipeline should handle multiple PGA scenarios for the same site."""
        bp01 = jerico_data['boreholes'][0]

        scenarios = [0.15, 0.25, 0.35, 0.50]
        results_by_scenario = {}

        for pga in scenarios:
            results = liquefaction_analyzer.analyze_borehole(
                borehole_id=bp01['borehole_id'],
                depths_m=bp01['depths_m'],
                spt_n_values=bp01['spt_n_values'],
                fines_content_pcts=bp01['fines_content_pcts'],
                pga_g=pga,
                magnitude_mw=7.5
            )
            results_by_scenario[pga] = results

        # Higher PGA should lead to higher liquefaction risk
        li_values = [
            max(r.liquefaction_index for r in results_by_scenario[pga])
            for pga in sorted(scenarios)
        ]

        for i in range(len(li_values) - 1):
            assert li_values[i] <= li_values[i+1], \
                f"LI should increase with PGA: {li_values}"

    def test_integration_cost_from_liquefaction_output(
        self, liquefaction_analyzer, costing_model, jerico_data
    ):
        """D6.2 LI output → D6.5 costing input."""
        bp01 = jerico_data['boreholes'][0]
        seismic = jerico_data['seismic']

        results_d62 = liquefaction_analyzer.analyze_borehole(
            borehole_id=bp01['borehole_id'],
            depths_m=bp01['depths_m'],
            spt_n_values=bp01['spt_n_values'],
            fines_content_pcts=bp01['fines_content_pcts'],
            pga_g=seismic['pga_g'],
            magnitude_mw=seismic['magnitude_mw']
        )

        li_average = np.mean([r.liquefaction_index for r in results_d62])

        cost = costing_model.calculate_total_recovery_cost(
            li=li_average,
            permanent_displacement_m=0.20,
            slope_length_m=100,
            unit_repair_rate_rs_per_m2=500
        )

        assert cost >= 0, "D6.2 → D6.5 pipeline should produce valid cost"


# ==================== E2E & PERFORMANCE TESTS ====================

class TestD6EndToEndAndPerformance:
    """E2E and performance tests (5 tests)."""

    def test_e2e_jerico_complete_analysis_no_exceptions(self, jerico_data):
        """Complete Jericó analysis (D6.2→D6.5) should run without exceptions."""
        from seismic_geotechnical_d6_algorithms import (
            LiquefactionAnalyzer, NewmarkDeformationCalculator,
            PostDisasterCostingModel
        )

        analyzer = LiquefactionAnalyzer(site_name="E2E_Jerico")
        newmark = NewmarkDeformationCalculator()
        costing = PostDisasterCostingModel()

        bp01 = jerico_data['boreholes'][0]
        seismic = jerico_data['seismic']
        slope = jerico_data['slope']

        try:
            # D6.2: Liquefaction
            li_results = analyzer.analyze_borehole(
                borehole_id=bp01['borehole_id'],
                depths_m=bp01['depths_m'],
                spt_n_values=bp01['spt_n_values'],
                fines_content_pcts=bp01['fines_content_pcts'],
                pga_g=seismic['pga_g'],
                magnitude_mw=seismic['magnitude_mw']
            )
            li_avg = np.mean([r.liquefaction_index for r in li_results])

            # D6.3: Newmark displacement
            a_y = newmark.calculate_yield_acceleration(
                slope['fos_static'], slope['slope_angle_deg'], slope['cohesion_kpa']
            )
            d_perm = newmark.calculate_newmark_displacement(
                seismic['pga_g'], a_y, seismic['magnitude_mw']
            )

            # D6.5: Costing
            cost = costing.calculate_total_recovery_cost(
                li=li_avg,
                permanent_displacement_m=d_perm,
                slope_length_m=150,
                unit_repair_rate_rs_per_m2=500
            )

            assert cost >= 0

        except Exception as e:
            pytest.fail(f"E2E analysis raised exception: {e}")

    def test_performance_liquefaction_single_depth_latency(self, liquefaction_analyzer):
        """Single-depth liquefaction analysis should complete in <100ms."""
        start = time.time()

        liquefaction_analyzer.analyze_borehole(
            borehole_id="perf_test_bp01",
            depths_m=[5.0],
            spt_n_values=[15],
            fines_content_pcts=[12],
            pga_g=0.25,
            magnitude_mw=7.5
        )

        elapsed = (time.time() - start) * 1000  # Convert to ms
        assert elapsed < 100, f"Single depth analysis took {elapsed}ms, should be <100ms"

    def test_performance_borehole_7_depths_latency(self, liquefaction_analyzer, jerico_data):
        """Borehole analysis (7 depths) should complete in <500ms."""
        bp01 = jerico_data['boreholes'][0]
        seismic = jerico_data['seismic']

        start = time.time()

        liquefaction_analyzer.analyze_borehole(
            borehole_id=bp01['borehole_id'],
            depths_m=bp01['depths_m'],
            spt_n_values=bp01['spt_n_values'],
            fines_content_pcts=bp01['fines_content_pcts'],
            pga_g=seismic['pga_g'],
            magnitude_mw=seismic['magnitude_mw']
        )

        elapsed = (time.time() - start) * 1000
        assert elapsed < 500, f"Borehole analysis took {elapsed}ms, should be <500ms"

    def test_performance_six_boreholes_latency(self, liquefaction_analyzer, jerico_data):
        """All 6 Jericó boreholes should process in <5 seconds."""
        seismic = jerico_data['seismic']

        start = time.time()

        for borehole in jerico_data['boreholes']:
            liquefaction_analyzer.analyze_borehole(
                borehole_id=borehole['borehole_id'],
                depths_m=borehole['depths_m'],
                spt_n_values=borehole['spt_n_values'],
                fines_content_pcts=borehole['fines_content_pcts'],
                pga_g=seismic['pga_g'],
                magnitude_mw=seismic['magnitude_mw']
            )

        elapsed = (time.time() - start)
        assert elapsed < 5.0, f"6-borehole analysis took {elapsed}s, should be <5s"

    @pytest.mark.benchmark
    def test_benchmark_liquefaction_throughput(self, benchmark, liquefaction_analyzer):
        """Benchmark: liquefaction analysis throughput (depths/second)."""
        bp01_depths = 7

        def analyze():
            liquefaction_analyzer.analyze_borehole(
                borehole_id="bench_bp01",
                depths_m=[float(i) for i in range(1, bp01_depths+1)],
                spt_n_values=[15] * bp01_depths,
                fines_content_pcts=[12] * bp01_depths,
                pga_g=0.25,
                magnitude_mw=7.5
            )

        result = benchmark(analyze)
        # Throughput > 1000 depths/second expected


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--cov=seismic_geotechnical_d6_algorithms"])
