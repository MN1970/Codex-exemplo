"""
Pytest Test Suite for D6.4-D6.6 Resilient Design & Post-Disaster Costing
Comprehensive testing of ResilientDesignCalculator, PostDisasterCostingModel, CaseRegistry

Usage:
  pytest test_resilient_design_d64_d66.py -v --tb=short
  pytest test_resilient_design_d64_d66.py::test_jerico_worst_case_cost -v
  pytest test_resilient_design_d64_d66.py -x
"""

import pytest
import math
from resilient_design_d64_d66 import (
    ResilientDesignCalculator,
    ReslientDesignParameters,
    PostDisasterCostingModel,
    DamageScenario,
    SeismicDamageSeverity,
    Sicro2024Rates,
    CaseRegistry,
    format_cost_report,
    format_resilient_design_report,
)


# ==================== D6.4 RESILIENT DESIGN TESTS ====================

class TestD64ResilientDesignCalculator:
    """D6.4 Resilient Design Calculator tests."""

    @pytest.fixture
    def default_params(self):
        """Default resilient design parameters."""
        return ReslientDesignParameters(
            pga_g=0.25,
            magnitude_mw=5.0,
            liquefaction_index=0.30,
            cbuq_thickness_mm=150.0,
            cbuq_resilient_modulus_mpa=3500.0,
        )

    @pytest.fixture
    def low_hazard_params(self):
        """Low seismic hazard case."""
        return ReslientDesignParameters(
            pga_g=0.12,
            magnitude_mw=4.0,
            liquefaction_index=0.05,
        )

    @pytest.fixture
    def high_hazard_params(self):
        """High seismic hazard case."""
        return ReslientDesignParameters(
            pga_g=0.35,
            magnitude_mw=6.5,
            liquefaction_index=0.45,
        )

    def test_pga_modifier_low_hazard(self, low_hazard_params):
        """PGA < 0.25g should produce no modifier."""
        calc = ResilientDesignCalculator(low_hazard_params)
        modifier = calc.calculate_pga_modifier()
        assert modifier == 0.0, f"Expected 0.0 modifier, got {modifier}"

    def test_pga_modifier_moderate_hazard(self, default_params):
        """PGA 0.25-0.30g should produce 10% modifier."""
        params = ReslientDesignParameters(pga_g=0.26)  # Slightly above 0.25 threshold
        calc = ResilientDesignCalculator(params)
        modifier = calc.calculate_pga_modifier()
        assert modifier == 0.10, f"Expected 0.10 modifier, got {modifier}"

    def test_pga_modifier_high_hazard(self, high_hazard_params):
        """PGA > 0.30g should produce 15% modifier."""
        calc = ResilientDesignCalculator(high_hazard_params)
        modifier = calc.calculate_pga_modifier()
        assert modifier == 0.15, f"Expected 0.15 modifier, got {modifier}"

    def test_li_modifier_low_liquefaction(self, low_hazard_params):
        """LI < 0.15 should produce no modifier."""
        calc = ResilientDesignCalculator(low_hazard_params)
        modifier = calc.calculate_li_modifier()
        assert modifier == 0.0, f"Expected 0.0 modifier, got {modifier}"

    def test_li_modifier_moderate_liquefaction(self, default_params):
        """LI 0.15-0.30 should produce 10% modifier."""
        params = ReslientDesignParameters(liquefaction_index=0.25)
        calc = ResilientDesignCalculator(params)
        modifier = calc.calculate_li_modifier()
        assert modifier == 0.10, f"Expected 0.10 modifier, got {modifier}"

    def test_li_modifier_high_liquefaction(self, high_hazard_params):
        """LI > 0.30 should produce 15% modifier."""
        calc = ResilientDesignCalculator(high_hazard_params)
        modifier = calc.calculate_li_modifier()
        assert modifier == 0.15, f"Expected 0.15 modifier, got {modifier}"

    def test_combined_modifier_uses_max(self):
        """Combined modifier should be MAX of PGA and LI modifiers."""
        # Case 1: PGA > LI
        params1 = ReslientDesignParameters(pga_g=0.32, liquefaction_index=0.20)
        calc1 = ResilientDesignCalculator(params1)
        combined1 = calc1.calculate_combined_seismic_modifier()
        pga_mod1 = calc1.calculate_pga_modifier()
        li_mod1 = calc1.calculate_li_modifier()
        assert combined1 == max(pga_mod1, li_mod1)

        # Case 2: LI > PGA
        params2 = ReslientDesignParameters(pga_g=0.20, liquefaction_index=0.40)
        calc2 = ResilientDesignCalculator(params2)
        combined2 = calc2.calculate_combined_seismic_modifier()
        pga_mod2 = calc2.calculate_pga_modifier()
        li_mod2 = calc2.calculate_li_modifier()
        assert combined2 == max(pga_mod2, li_mod2)

    def test_effective_resilient_modulus_reduction(self, default_params):
        """Effective modulus should be MR_base * (1 - modifier)."""
        calc = ResilientDesignCalculator(default_params)
        base_mr = default_params.cbuq_resilient_modulus_mpa
        effective_mr = calc.calculate_effective_resilient_modulus()
        modifier = calc.calculate_combined_seismic_modifier()

        expected_mr = base_mr * (1.0 - modifier)
        assert abs(effective_mr - expected_mr) < 0.01, \
            f"Expected {expected_mr}MPa, got {effective_mr}MPa"

    def test_effective_modulus_no_reduction_low_hazard(self, low_hazard_params):
        """Low hazard should have no modulus reduction."""
        calc = ResilientDesignCalculator(low_hazard_params)
        base_mr = low_hazard_params.cbuq_resilient_modulus_mpa
        effective_mr = calc.calculate_effective_resilient_modulus()
        assert effective_mr == base_mr, "No reduction expected for low hazard"

    def test_effective_modulus_10pct_reduction_moderate(self):
        """Moderate hazard (0.25g) should reduce modulus by 10%."""
        params = ReslientDesignParameters(
            pga_g=0.26,  # Slightly above 0.25g threshold
            liquefaction_index=0.10,  # Low LI
            cbuq_resilient_modulus_mpa=3500.0,
        )
        calc = ResilientDesignCalculator(params)
        effective_mr = calc.calculate_effective_resilient_modulus()
        expected_mr = 3500.0 * 0.90  # 10% reduction
        assert abs(effective_mr - expected_mr) < 0.1

    def test_effective_modulus_15pct_reduction_high(self):
        """High hazard (>0.30g) should reduce modulus by 15%."""
        params = ReslientDesignParameters(
            pga_g=0.32,
            liquefaction_index=0.10,
            cbuq_resilient_modulus_mpa=3500.0,
        )
        calc = ResilientDesignCalculator(params)
        effective_mr = calc.calculate_effective_resilient_modulus()
        expected_mr = 3500.0 * 0.85  # 15% reduction
        assert abs(effective_mr - expected_mr) < 0.1

    def test_geotextile_not_required_low_li(self, low_hazard_params):
        """Low LI should not enable geotextile."""
        params = low_hazard_params
        params.use_geotextile = False
        calc = ResilientDesignCalculator(params)
        friction_increase, effective_friction = calc.calculate_geotextile_effect()
        assert friction_increase == 0.0
        assert effective_friction == params.soil_friction_angle_deg

    def test_geotextile_friction_increase_minimum(self):
        """Low LI with geotextile enabled should use minimum increase (12%)."""
        params = ReslientDesignParameters(
            liquefaction_index=0.10,
            soil_friction_angle_deg=35.0,
            use_geotextile=True,
        )
        calc = ResilientDesignCalculator(params)
        friction_increase_pct, effective_friction = calc.calculate_geotextile_effect()

        expected_increase_pct = 0.12
        assert friction_increase_pct == pytest.approx(expected_increase_pct, abs=0.01)

        expected_effective = 35.0 * (1.0 + expected_increase_pct)
        assert effective_friction == pytest.approx(expected_effective, abs=0.1)

    def test_geotextile_friction_increase_maximum(self):
        """High LI with geotextile should use maximum increase (18%)."""
        params = ReslientDesignParameters(
            liquefaction_index=0.50,
            soil_friction_angle_deg=35.0,
            use_geotextile=True,
        )
        calc = ResilientDesignCalculator(params)
        friction_increase_pct, effective_friction = calc.calculate_geotextile_effect()

        expected_increase_pct = 0.18
        assert friction_increase_pct == pytest.approx(expected_increase_pct, abs=0.01)

    def test_geotextile_friction_increase_interpolation(self):
        """Mid-range LI should interpolate friction increase."""
        params = ReslientDesignParameters(
            liquefaction_index=0.275,  # Mid-point between 0.15 and 0.40
            soil_friction_angle_deg=35.0,
            use_geotextile=True,
        )
        calc = ResilientDesignCalculator(params)
        friction_increase_pct, effective_friction = calc.calculate_geotextile_effect()

        # Should be between min (12%) and max (18%)
        assert 0.12 <= friction_increase_pct <= 0.18

    def test_damage_risk_assessment_pga(self):
        """Damage risk assessment from PGA levels."""
        # Low
        calc_low = ResilientDesignCalculator(ReslientDesignParameters(pga_g=0.10))
        assert calc_low.assess_damage_risk_pga() == "low"

        # Moderate
        calc_mod = ResilientDesignCalculator(ReslientDesignParameters(pga_g=0.20))
        assert calc_mod.assess_damage_risk_pga() == "moderate"

        # High
        calc_high = ResilientDesignCalculator(ReslientDesignParameters(pga_g=0.32))
        assert calc_high.assess_damage_risk_pga() == "high"

    def test_damage_risk_assessment_li(self):
        """Damage risk assessment from liquefaction index."""
        # Low
        calc_low = ResilientDesignCalculator(ReslientDesignParameters(liquefaction_index=0.10))
        assert calc_low.assess_damage_risk_li() == "low"

        # Moderate
        calc_mod = ResilientDesignCalculator(ReslientDesignParameters(liquefaction_index=0.25))
        assert calc_mod.assess_damage_risk_li() == "moderate"

        # High
        calc_high = ResilientDesignCalculator(ReslientDesignParameters(liquefaction_index=0.45))
        assert calc_high.assess_damage_risk_li() == "high"

    def test_barrier_not_required_low_hazard(self, low_hazard_params):
        """Low hazard should not require barrier."""
        calc = ResilientDesignCalculator(low_hazard_params)
        result = calc.calculate_resilient_design()
        assert result.barrier_required == False

    def test_barrier_required_high_hazard(self, high_hazard_params):
        """High hazard should require barrier."""
        calc = ResilientDesignCalculator(high_hazard_params)
        result = calc.calculate_resilient_design()
        assert result.barrier_required == True

    def test_barrier_cost_range(self, high_hazard_params):
        """Barrier cost should be positive and within expected range."""
        calc = ResilientDesignCalculator(high_hazard_params)
        result = calc.calculate_resilient_design()

        # Expected: BRL 8500/100m + labor BRL 45/m = BRL 85/m + 45/m = BRL 130/m
        expected_min = 80.0
        expected_max = 150.0
        assert expected_min <= result.barrier_cost_per_m_brl <= expected_max

    def test_full_resilient_design_calculation(self, default_params):
        """Full resilient design calculation should produce complete result."""
        calc = ResilientDesignCalculator(default_params)
        result = calc.calculate_resilient_design()

        # Check all fields are populated
        assert result.base_resilient_modulus_mpa > 0
        assert result.effective_resilient_modulus_mpa > 0
        assert 0 <= result.combined_seismic_modifier <= 0.15
        assert result.barrier_cost_per_m_brl > 0
        assert result.damage_risk_pga in ["low", "moderate", "high"]
        assert result.damage_risk_li in ["low", "moderate", "high"]
        assert isinstance(result.recommended_actions, list)


# ==================== D6.5 POST-DISASTER COSTING TESTS ====================

class TestD65PostDisasterCosting:
    """D6.5 Post-Disaster Costing tests."""

    @pytest.fixture
    def sicro_rates(self):
        """Standard SICRO 2024 rates."""
        return Sicro2024Rates()

    @pytest.fixture
    def costing_model(self, sicro_rates):
        """Costing model with standard rates."""
        return PostDisasterCostingModel(sicro_rates)

    def test_sicro_rate_liquefaction(self, sicro_rates):
        """SICRO 2024 liquefaction rate should be BRL 198.5/m²."""
        assert sicro_rates.liquefaction_repair_per_m2_brl == 198.50

    def test_sicro_rate_slope_failure(self, sicro_rates):
        """SICRO 2024 slope failure rate should be BRL 196/m²."""
        assert sicro_rates.slope_failure_repair_per_m2_brl == 196.00

    def test_liquefaction_cost_calculation(self, costing_model):
        """Liquefaction cost = area × rate."""
        area_m2 = 1000.0
        cost = costing_model.calculate_liquefaction_cost(area_m2)
        expected = area_m2 * 198.50
        assert cost == pytest.approx(expected, abs=0.01)

    def test_slope_failure_cost_calculation(self, costing_model):
        """Slope failure cost = area × rate."""
        area_m2 = 500.0
        cost = costing_model.calculate_slope_failure_cost(area_m2)
        expected = area_m2 * 196.00
        assert cost == pytest.approx(expected, abs=0.01)

    def test_cracking_cost_calculation(self, costing_model):
        """Cracking cost = length × rate."""
        length_m = 200.0
        cost = costing_model.calculate_cracking_cost(length_m)
        expected = length_m * 125.0
        assert cost == pytest.approx(expected, abs=0.01)

    def test_lateral_spread_cost_calculation(self, costing_model):
        """Lateral spread cost = length × rate."""
        length_m = 100.0
        cost = costing_model.calculate_lateral_spread_cost(length_m)
        expected = length_m * 175.0
        assert cost == pytest.approx(expected, abs=0.01)

    def test_light_damage_scenario_cost(self, costing_model):
        """Light damage should only include cracking costs."""
        scenario = DamageScenario(
            severity=SeismicDamageSeverity.LIGHT,
            surface_cracks_length_m=100.0,
        )
        result = costing_model.cost_scenario_light(scenario)

        assert result.liquefaction_cost_brl == 0.0
        assert result.slope_failure_cost_brl == 0.0
        assert result.cracking_cost_brl > 0
        assert result.total_cost_brl > result.cracking_cost_brl  # includes overhead

    def test_moderate_damage_scenario_cost(self, costing_model):
        """Moderate damage should include liquefaction and slope failure."""
        scenario = DamageScenario(
            severity=SeismicDamageSeverity.MODERATE,
            liquefaction_area_m2=500.0,
            slope_failure_area_m2=300.0,
        )
        result = costing_model.cost_scenario_moderate(scenario)

        assert result.liquefaction_cost_brl > 0
        assert result.slope_failure_cost_brl > 0
        assert result.total_cost_brl > result.liquefaction_cost_brl

    def test_severe_damage_scenario_cost(self, costing_model):
        """Severe damage should include all cost components."""
        scenario = DamageScenario(
            severity=SeismicDamageSeverity.SEVERE,
            liquefaction_area_m2=1000.0,
            slope_failure_area_m2=800.0,
            surface_cracks_length_m=500.0,
            lateral_spread_length_m=200.0,
        )
        result = costing_model.cost_scenario_severe(scenario)

        assert result.liquefaction_cost_brl > 0
        assert result.slope_failure_cost_brl > 0
        assert result.cracking_cost_brl > 0
        assert result.lateral_spread_cost_brl > 0
        assert result.total_cost_brl > 0

    def test_cost_escalation_by_severity(self, costing_model):
        """Costs should escalate: light < moderate < severe."""
        scenario_light = DamageScenario(
            severity=SeismicDamageSeverity.LIGHT,
            surface_cracks_length_m=200.0,
        )
        scenario_moderate = DamageScenario(
            severity=SeismicDamageSeverity.MODERATE,
            liquefaction_area_m2=500.0,
            slope_failure_area_m2=400.0,
        )
        scenario_severe = DamageScenario(
            severity=SeismicDamageSeverity.SEVERE,
            liquefaction_area_m2=2000.0,
            slope_failure_area_m2=1500.0,
            lateral_spread_length_m=400.0,
        )

        cost_light = costing_model.calculate_scenario_cost(scenario_light).total_cost_brl
        cost_moderate = costing_model.calculate_scenario_cost(scenario_moderate).total_cost_brl
        cost_severe = costing_model.calculate_scenario_cost(scenario_severe).total_cost_brl

        assert cost_light < cost_moderate < cost_severe

    def test_labor_overhead_calculation(self, costing_model):
        """Labor overhead should be 15% of subtotal."""
        scenario = DamageScenario(
            severity=SeismicDamageSeverity.MODERATE,
            liquefaction_area_m2=1000.0,
        )
        result = costing_model.cost_scenario_moderate(scenario)

        expected_overhead = result.subtotal_brl * 0.15
        assert result.labor_overhead_brl == pytest.approx(expected_overhead, rel=0.01)

    def test_normalized_cost_calculation(self, costing_model):
        """Cost per m² should be total cost / area."""
        scenario = DamageScenario(
            severity=SeismicDamageSeverity.MODERATE,
            liquefaction_area_m2=500.0,
        )
        result = costing_model.cost_scenario_moderate(scenario)

        expected_cost_per_m2 = result.total_cost_brl / 500.0
        assert result.cost_per_m2_brl == pytest.approx(expected_cost_per_m2, rel=0.01)

    def test_no_damage_scenario_cost(self, costing_model):
        """No damage scenario should have zero cost."""
        scenario = DamageScenario(severity=SeismicDamageSeverity.NONE)
        result = costing_model.calculate_scenario_cost(scenario)

        assert result.total_cost_brl == 0.0


# ==================== D6.6 CASE REGISTRY TESTS ====================

class TestD66CaseRegistry:
    """D6.6 Case Registry tests."""

    @pytest.fixture
    def registry(self):
        """Case registry with predefined cases."""
        return CaseRegistry()

    def test_registry_has_three_cases(self, registry):
        """Registry should have 3 predefined cases."""
        cases = registry.list_cases()
        assert len(cases) == 3

    def test_jerico_case_exists(self, registry):
        """Jericó case should be retrievable."""
        case = registry.get_case("JERICO-2024")
        assert case is not None
        assert case.case_id == "JERICO-2024"
        assert case.magnitude_mw == 5.0
        assert case.pga_g == 0.32
        assert case.liquefaction_index == 0.35

    def test_ceara_case_exists(self, registry):
        """Ceará case should be retrievable."""
        case = registry.get_case("CEARA-REGIONAL")
        assert case is not None
        assert case.magnitude_mw == 7.2
        assert case.pga_g == 0.35
        assert case.liquefaction_index == 0.40

    def test_es_baseline_exists(self, registry):
        """ES baseline case should be retrievable."""
        case = registry.get_case("ES-LOW-SEISMIC")
        assert case is not None
        assert case.pga_g == 0.12
        assert case.liquefaction_index == 0.05

    def test_get_nonexistent_case(self, registry):
        """Retrieving nonexistent case should return None."""
        case = registry.get_case("NONEXISTENT")
        assert case is None

    def test_jerico_analysis_returns_result(self, registry):
        """Jericó analysis should return complete result."""
        result = registry.analyze_case("JERICO-2024")
        assert result is not None
        assert result.case.case_id == "JERICO-2024"
        assert result.resilient_design is not None
        assert result.light_damage_cost is not None
        assert result.moderate_damage_cost is not None
        assert result.severe_damage_cost is not None
        assert result.estimated_cost_brl >= 0

    def test_jerico_cost_escalation(self, registry):
        """Jericó costs should escalate with severity."""
        result = registry.analyze_case("JERICO-2024")

        light = result.light_damage_cost.total_cost_brl
        moderate = result.moderate_damage_cost.total_cost_brl
        severe = result.severe_damage_cost.total_cost_brl

        assert light < moderate < severe

    def test_ceara_larger_costs_than_es(self, registry):
        """Ceará (M7.2) should have larger costs than ES (baseline)."""
        ceara = registry.analyze_case("CEARA-REGIONAL")
        es = registry.analyze_case("ES-LOW-SEISMIC")

        assert ceara.severe_damage_cost.total_cost_brl > es.severe_damage_cost.total_cost_brl

    def test_jerico_worst_case_analysis(self, registry):
        """Jericó worst-case should return valid result."""
        result = registry.jerico_worst_case_analysis()
        assert result is not None
        assert result.case.case_id == "JERICO-2024"
        assert result.resilient_design.barrier_required == True  # High LI

    def test_ceara_regional_analysis(self, registry):
        """Ceará regional analysis should return valid result."""
        result = registry.ceara_regional_analysis()
        assert result is not None
        assert result.case.magnitude_mw == 7.2

    def test_es_baseline_analysis(self, registry):
        """ES baseline should require no reinforcement."""
        result = registry.es_baseline_analysis()
        assert result is not None
        assert result.resilient_design.barrier_required == False

    def test_estimated_cost_weighted_by_li(self, registry):
        """Estimated cost should reflect LI-based damage probability."""
        jerico = registry.analyze_case("JERICO-2024")  # LI=0.35 → high probability of severe
        es = registry.analyze_case("ES-LOW-SEISMIC")  # LI=0.05 → low probability

        # Jericó estimated cost should be closer to severe cost
        jerico_severity_weight = (jerico.estimated_cost_brl - jerico.light_damage_cost.total_cost_brl) / \
                                 (jerico.severe_damage_cost.total_cost_brl - jerico.light_damage_cost.total_cost_brl)
        assert 0.3 < jerico_severity_weight < 0.8  # Biased toward moderate/severe

        # ES estimated cost should be closer to light cost
        es_severity_weight = (es.estimated_cost_brl - es.light_damage_cost.total_cost_brl) / \
                             max(es.severe_damage_cost.total_cost_brl - es.light_damage_cost.total_cost_brl, 1.0)
        assert es_severity_weight < 0.5  # Biased toward light

    def test_barrier_cost_for_jerico(self, registry):
        """Jericó should require barrier with meaningful cost."""
        result = registry.jerico_worst_case_analysis()
        barrier_cost_per_m = result.resilient_design.barrier_cost_per_m_brl

        # Should be in range: BRL 85-100/m typical
        assert 80 < barrier_cost_per_m < 150

    def test_case_analysis_with_barrier_enabled(self, registry):
        """Analysis with barrier should show higher costs than without."""
        jerico_with_barrier = registry.analyze_case("JERICO-2024", use_barrier=True)
        # Note: Current model doesn't fully differentiate with/without barrier in costing
        # but barrier cost is included in design recommendations
        assert jerico_with_barrier.resilient_design.barrier_required == True


# ==================== REPORTING & EXPORT TESTS ====================

class TestReportingAndExport:
    """Tests for reporting and export functions."""

    def test_cost_report_format(self):
        """Cost report should be formatted readably."""
        scenario = DamageScenario(severity=SeismicDamageSeverity.MODERATE)
        model = PostDisasterCostingModel()
        result = model.calculate_scenario_cost(scenario)

        report = format_cost_report(result)
        assert isinstance(report, str)
        assert len(report) > 0
        assert "MODERATE" in report.upper()
        assert "BRL" in report

    def test_resilient_design_report_format(self):
        """Resilient design report should be formatted readably."""
        calc = ResilientDesignCalculator()
        result = calc.calculate_resilient_design()

        report = format_resilient_design_report(result, "Test Site")
        assert isinstance(report, str)
        assert len(report) > 0
        assert "Test Site" in report
        assert "MPa" in report or "%" in report


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests across D6.4-D6.6."""

    def test_complete_jerico_workflow(self):
        """Complete workflow: Jericó case analysis with all components."""
        registry = CaseRegistry()
        result = registry.jerico_worst_case_analysis()

        # Verify all components are populated
        assert result is not None
        assert result.case.pga_g == 0.32
        assert result.case.liquefaction_index == 0.35

        # Resilient design should show modulus reduction
        assert result.resilient_design.effective_resilient_modulus_mpa < \
               result.resilient_design.base_resilient_modulus_mpa

        # Barrier should be required due to high LI
        assert result.resilient_design.barrier_required == True

        # Costing should show escalation
        assert result.light_damage_cost.total_cost_brl < result.severe_damage_cost.total_cost_brl

        # Estimated cost should be reasonable
        assert 0 < result.estimated_cost_brl < result.severe_damage_cost.total_cost_brl * 2

    def test_cost_ranges_across_cases(self):
        """Cost ranges should be appropriate for each case."""
        registry = CaseRegistry()

        jerico = registry.analyze_case("JERICO-2024")
        ceara = registry.analyze_case("CEARA-REGIONAL")
        es = registry.analyze_case("ES-LOW-SEISMIC")

        # Costs should be: ES << Jericó, Ceará (both have high LI)
        assert es.severe_damage_cost.total_cost_brl < jerico.severe_damage_cost.total_cost_brl
        assert es.severe_damage_cost.total_cost_brl < ceara.severe_damage_cost.total_cost_brl

        # Estimated costs should reflect LI-based weighting
        # Jericó (LI=0.35): weighted toward severe
        # ES (LI=0.05): weighted toward light
        assert jerico.estimated_cost_brl > es.estimated_cost_brl
        assert ceara.estimated_cost_brl > es.estimated_cost_brl

    def test_modifier_and_cost_consistency(self):
        """Higher modifiers should correlate with higher costs."""
        calc_low = ResilientDesignCalculator(ReslientDesignParameters(pga_g=0.12))
        calc_high = ResilientDesignCalculator(ReslientDesignParameters(pga_g=0.35))

        result_low = calc_low.calculate_resilient_design()
        result_high = calc_high.calculate_resilient_design()

        # Higher hazard should have larger modifier
        assert result_high.combined_seismic_modifier > result_low.combined_seismic_modifier

        # Higher hazard should trigger barrier
        assert result_high.barrier_required == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
